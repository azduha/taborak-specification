# Organization Structure

Units, their types, their nesting, and — the part that is usually skipped — how to keep
all of that true across four decades of reorganization.

---

## 1. Units are a configurable tree

You confirmed sub-units are core to the model. The design is a **single self-referencing
`org_unit` table** with configurable types, not one table per level.

```
org_unit(
    id,
    unit_type_id,             -- troop, pack, region, national, ...
    parent_unit_id,           -- nullable; null = top level
    code,                     -- short human code, e.g. "T12"
    name,                     -- current display name
    valid_from, valid_to,     -- when this unit existed
    status                    -- proposed | active | merged | closed
)
```

### Why one table, not `troop`/`pack`/`region` tables

- Depth is a data question, not a schema question. If the organization adds or removes a
  level, a data migration is unacceptable; a config row is not.
- "Who is in this unit and all its descendants?" (a district leader's question) becomes a
  single recursive query instead of a hand-written union across tables.
- Units get renamed and renumbered constantly. A `troop` table would need a rename history
  alongside; here the rename is one row in `org_unit_name`.

### Why types are rows, not an enum

Same reason. The unit vocabulary in a 40-year-old organization has changed — a type that
existed in 1995 may be gone, and a new one may be needed in 2027. An enum requires a
deployment to change; a `org_unit_type` row does not.

```
org_unit_type(
    id, code, name,
    allows_children,          -- may this unit contain child members?
    allows_adults,            -- may it contain adult members?
    max_depth,                -- nesting constraint
    sort_order
)
```

`allows_children` / `allows_adults` earn their place: they let the system validate that a
child member is not placed in a region-level administrative unit, without hardcoding
which types are which.

---

## 2. Nesting rules

*Assumption:* the organization has a hierarchy like:

```
national
  └── region
        └── district
              └── group
                    ├── troop      (children)
                    └── pack       (younger children)
```

If your real structure differs, only `org_unit_type` rows and this diagram change — the
schema does not.

### Enforcing valid nesting

```
org_unit_type_rule(
    id,
    parent_type_id,           -- may a unit of parent_type_id contain...
    child_type_id,            -- ...a unit of child_type_id?
    max_children,             -- optional cap
    is_required               -- must children of this type have a parent of this type?
)
```

This is a table rather than a check constraint because nesting rules change over decades
and because a constraint buried in code is invisible to the people configuring the
organization.

**Do not enforce nesting in the application layer only.** A `CHECK` cannot express it, so
enforce it with a database trigger or a deferred constraint, and expose the rules in an
admin UI. If it is only validated in the app, a data import will violate it.

---

## 3. Unit names and renumbering — the history problem

A unit called "4th Troop" in 1998 may be "Troop 12" today, or may have been split into
two, or merged into a group. The system must answer both:

- "What was this unit called in 2001?"
- "Is this the same unit as the one in the 1998 roster?"

### Names are temporal rows

```
org_unit_name(
    id, org_unit_id,
    name, code,
    valid_from, valid_to,
    change_reason             -- rename | renumber | reorganisation | correction
)
```

`org_unit.name` is a denormalised convenience holding the current name. The history lives
here. Queries about the past read this table; they must never read `org_unit.name`.

### Renumbering is a rename, not a new unit

When "4th Troop" becomes "Troop 12" and the members stay, that is **one unit with two
name rows**. Creating a new unit would orphan all the history and make "who was in Troop 12
in 1998?" answerable only by luck.

### Splits and mergers

These *do* create or close units:

```
org_unit_relationship(
    id,
    source_unit_id,
    target_unit_id,
    relationship,             -- split_from | merged_into | successor_of | renamed_to
    effective_date,
    note
)
```

A membership's history must survive a split: when Troop 12 splits into Troop 12 and
Troop 31, members who moved to 31 get a *new* `unit_membership` row starting at the split
date, and their old row closes at the same date. No rows are rewritten. The
`org_unit_relationship` row records that 31 came from 12, so a historical query can follow
the lineage if asked.

> Design rule: **never rewrite a `unit_membership` to point at a different unit.** Close it
> and open a new one. Rewriting destroys the answer to "where was this child in 2003?"

---

## 4. Positions

A **position** is a defined slot in a unit. A **position assignment** is a person
filling it for a period. This split is what lets the system say "Troop 12 has no
scoutmaster right now" and "this position has been vacant since March" — both operationally
important, and neither expressible if positions only exist when filled.

```
position(
    id, org_unit_id, unit_type_id,
    code,                     -- scoutmaster, assistant_leader, treasurer, quartermaster
    title,
    is_unique_per_unit,       -- only one scoutmaster per troop
    requires_adult_membership -- must the holder be a current adult member?
)

position_assignment(
    id, position_id, person_id,
    valid_from, valid_to,
    is_primary,               -- some people hold several positions
    appointment_reference,    -- link to the appointment letter/record
    ended_reason
)
```

### Positions are not permissions

Holding the `scoutmaster` position does **not** by itself grant any system capability.
The position is an organizational fact; authority comes from `role_assignment`. Keeping
them separate means:

- The organization's structure can be recorded completely, including for historical
  periods, without implying that a 1998 scoutmaster has system access today.
- A vacant position and an unfilled role are different reports.
- Changing what a scoutmaster can do in the system is a permission change, not a
  restructuring of the organization's records.

In practice a workflow will offer "appoint as scoutmaster" as one action that creates both
a `position_assignment` and the corresponding scoped `role_assignment`. That is
convenience; the schema stays separate.

### Eligibility

`requires_adult_membership` handles the common rule that a leader must be a current adult
member. Enforcing it as a **database constraint is not possible** (it depends on temporal
membership state), so it is an application rule plus a periodic consistency report. Do not
attempt to enforce it with a foreign key.

---

## 5. Historical units

Units that closed must remain queryable. `org_unit.status = 'closed'` with `valid_to` set.
They are excluded from pickers by default and included in historical reports always.

Two things to get right:

1. **A closed unit is not deleted.** Historical `unit_membership` rows reference it, and
   "who was in the 4th Troop?" must work forever.
2. **Reopening reuses the row** if it is genuinely the same unit, or creates a new one if
   the organization considers it a fresh start. This is an organizational judgement, not a
   technical one — record which was chosen and why on the unit, so the answer is not
   re-litigated every time someone asks about the 80s troop with the same number.

---

## 6. Units and permissions

Units are a **scope** for authority. The same role assignment mechanism handles both
organization-wide and unit-scoped authority:

```
role_assignment(
    id, person_id, role_id,
    scope_type,               -- 'organization' | 'org_unit'
    scope_id,                 -- null for organization, org_unit id otherwise
    valid_from, valid_to
)
```

So "treasurer of the organization" and "treasurer of Troop 12" are the same table and the
same role — differing only in `scope_type`/`scope_id`. This means:

- A permission check for a unit-scoped operation looks for role assignments at that unit
  **or any ancestor unit**. A district treasurer can act on a troop within the district.
- The ancestor walk uses the unit hierarchy, so it must be efficient (see
  [data-model/02-organization.md](../data-model/02-organization.md#6-hierarchy-traversal)).

*Assumption:* authority flows **downward** through the hierarchy (a regional role covers its
districts). If your organization instead requires explicit per-unit grants with no
inheritance, that is a one-line change in the resolver — but it is a policy decision you
should make deliberately. Tracked in [../open-questions.md](../open-questions.md).

### Unit-scoped access grants

Beyond roles, a unit can be the target of an item-scoped grant:

```
access_grant(..., scope_type = 'org_unit', scope_id = <unit>, level = 'manage')
```

This is how you grant someone authority over a unit's data without giving them an
organization-wide role — a temporary administrator for one troop, for instance.

---

## 7. Open issues

- The actual unit type vocabulary and nesting rules — needs your input; the schema is ready
  for them.
- Whether authority inherits downward (see §6) or must be granted per unit.
- Whether a person may hold memberships in units of different types simultaneously
  (e.g. a child in a troop whose adult leader is also in a district-level unit).
  Recommend: yes for adults, restricted for children.
- Whether units can be moved between parents retroactively (a troop reassigned to a
  different district in 2001). This affects historical reporting and needs a decision.

All tracked in [../open-questions.md](../open-questions.md).
