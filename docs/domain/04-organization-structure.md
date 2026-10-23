# Organization Structure

Units, their types, their nesting, and — the part that is usually skipped — how to keep
all of that true across four decades of reorganization.

---

## 1. One root, arbitrary sub-units

There is **exactly one top-level unit: the organization itself.** Everything else is a
sub-unit nested beneath it, **to arbitrary depth and in arbitrary combination** — weekly
meeting groups, smaller packs, sections, teams.

```
                    THE ORGANIZATION              ← the single root. depth 0.
                    ┌──────┴──────┬────────┐
                 Pack A        Pack B    Pack C      ← created by the organization
                ┌───┴───┐
          Thursday grp  Saturday grp                 ← created by the pack
              ┌───┴───┐
           Older  Younger                             ← arbitrary depth
```

**This is not a ladder of levels.** There is no fixed national → region → district → group
→ troop sequence, no required intermediate level, and no type that must appear at a
particular depth. A sub-unit may contain sub-units to any depth, and the arrangement is the
organization's business rather than the schema's.

### Membership lives at the root; participation lives in the sub-units

The distinction that makes this work:

| | Where it lives | What it means |
|---|---|---|
| **Membership** | **The root unit** | "This person is a member of the organization." Paid yearly. |
| **Participation** | Any sub-unit | "This person takes part in this weekly group." |

People **register and pay at the organization**, and their membership is theirs as a member
of the organization — not a membership of a pack. The packs they attend are recorded
separately, as participation ([§5](#5-participation-unit_participation)), because belonging
to a Thursday-evening group and being a paid-up member of the organization are different
facts with different lifetimes. See
[data-model/03-membership.md](../data-model/03-membership.md#5-unit_participation).

### Sub-units are self-governing

A pack has **its own events, its own local leadership, and its own roster**. It is not an
administrative subdivision of the root; it is a thing that runs itself and answers to the
root. That is why [authority originates at the unit](06-authorization-model.md#2-scope-authority--no-downward-inheritance)
and why the root cannot decide permissions inside a pack.

### Why one table, not `pack`/`group`/`troop` tables

- **Depth is a data question, not a schema question.** The organization invents and retires
  grouping arrangements; each one must be a row, not a migration.
- **"Who is in this pack and everything under it?"** becomes one recursive query rather than
  a hand-written union across tables.
- **Units get renamed and renumbered constantly.** A `pack` table would need rename history
  alongside; here a rename is one row in `org_unit_name`.

A unit row carries its `unit_type_id` — the organization type for the root, and otherwise
whatever type the organization has defined; a `parent_unit_id`, absent **only** for the single
root and immutable thereafter (§3); a short human `code` such as `T12`; the current display
`name`; the period the unit existed, as `valid_from` and `valid_to`; and a `status` of
`proposed`, `active`, `merged` or `closed`.

**The single root is enforced structurally**, not by convention: among all unit rows, at most
one may have no parent. The rule counts every row rather than only the open ones, so a root
that has closed does not make room for a second one.

### Why types are rows, not an enum

The unit vocabulary in a long-lived organization changes — a type that existed in 1995 may
be gone, and a new one may be needed in 2027. An enum requires a deployment to change; an
`org_unit_type` row does not.

> **This goes further than it used to: no sub-unit types are seeded at all**
> ([D-054](../decisions/decision-log.md#d-054--the-sub-unit-vocabulary-is-not-seeded-the-organization-defines-its-own-types)).
> `org_unit_type` is *runtime data*, like `role`
> ([D-052](../decisions/decision-log.md#d-052--roles-are-runtime-data-the-seed-set-is-not-a-specification)) —
> the seed carries the root type and nothing else, and the organization creates the types it
> uses. Earlier revisions seeded `pack`/`group`/`team`, and before that a
> `national`/`region`/`district` ladder; both were invented words that read as a
> specification. **The words below are still used throughout these docs as illustration** —
> "a pack may only sit directly under the root" is an example of a rule, not a type the
> system ships with.

A type row is a `code` and a name, plus `allows_minors`, `is_leaf` — may it contain sub-units —
an optional `max_depth` ceiling, and a `sort_order`.

`allows_minors` is a **safeguarding** flag, not a membership rule: it lets the system
validate that a unit which does not supervise minors never has any placed in it, without
hardcoding which type codes those are. Membership itself is ageless — see
[../decisions/decision-log.md](../decisions/decision-log.md#d-038--membership-is-ageless).

---

## 2. Nesting rules

Because sub-units nest arbitrarily, the rules are **permissive by default** and express only
the genuine constraints the organization wants to state. Most organizations need very few.

A rule pairs two types and answers one question about them: may a unit of `parent_type_id`
contain a unit of `child_type_id`. `max_children` is an optional cap on how many it may contain.
`is_required` asks the separate question — must a unit of the child type have a parent of the
parent type at all.

**A type with no rules at all is unconstrained.** That is the default and it is deliberate:
the organization is free to invent a new kind of group and nest it wherever it likes without
asking the schema's permission first. Rules exist to constrain where the organization has
decided it wants constraint — a `pack` may only sit directly under the root, say.

This is a table rather than a check constraint because nesting rules change over decades and
because a constraint buried in code is invisible to the people configuring the organization.

**Do not enforce nesting in the application layer only.** A check clause cannot express it — the
rule reads two tables and a history — and since
[D-072](../decisions/decision-log.md#d-072--the-documentation-carries-no-sql-the-schema-is-the-orms-job)
the trigger that used to carry it is gone from these documents too, so the obligation has to be
placed deliberately rather than assumed from a schema. **Put it in a constraint or a check inside
the writing transaction, at the migration layer, and expose the rules in an admin UI.** If it is
only validated by the form, a data import will violate it — which is not a hypothetical here: the
legacy corpus is precisely a data import, arriving before the admin UI exists. See
[../data-model/00-conventions.md §6a](../data-model/00-conventions.md#6a-who-enforces-an-invariant-now)
for which layer survives which kind of writer.

**"Before the admin UI exists" now costs more than it used to.** The same batch carries free-text
columns, and under [D-090](../decisions/decision-log.md#d-090--the-legacy-corpus-is-thousands-of-roster-rows-with-numbers-and-no-money)
the map from those columns to attribute codes has to be **authored and read before the batch applies**,
with the codes it names arriving `live` because a curator read them
([03-identity-and-legacy.md §7](03-identity-and-legacy.md#7-legacy-import-pipeline)). If the import
genuinely precedes the UI, that reading cannot happen in the UI — and `attribute.define` is held by no
seed role ([../appendix/permission-catalog.md §12](../appendix/permission-catalog.md#12-open-issues),
**AT-2**). So the organization's first act of vocabulary curation is currently scheduled and unstaffed.
That is a gap in the rollout plan rather than in the model, but it is the kind that gets discovered at
the import, not before it.

---

## 3. Unit names and renumbering — the history problem

A unit called "4th Pack" in 1998 may be "Pack 12" today, or may have been split into
two, or merged into another. The system must answer both:

- "What was this unit called in 2001?"
- "Is this the same unit as the one in the 1998 roster?"

### Names are temporal rows

One row per name a unit has gone by: the `name` and `code` it carried, the period it carried
them for, and a `change_reason` of `rename`, `renumber`, `reorganisation` or `correction`.

`org_unit.name` is a denormalised convenience holding the current name. The history lives
here. Queries about the past read this table; they must never read `org_unit.name`.

### Renumbering is a rename, not a new unit

When "4th Pack" becomes "Pack 12" and the participants stay, that is **one unit with two
name rows**. Creating a new unit would orphan all the history and make "who was in Pack 12
in 1998?" answerable only by luck.

### Splits and mergers

These *do* create or close units:

The record of one names the `source_unit_id` and the `target_unit_id`, the `relationship` from one to the
other — `split_from`, `merged_into`, `successor_of` or `renamed_to` — the `effective_date`, and
a `note`.

A participation history must survive a split: when Pack 12 splits into Pack 12 and
Pack 31, people who moved to 31 get a *new* `unit_participation` row starting at the split
date, and their old row closes at the same date. No rows are rewritten. The
`org_unit_relationship` row records that 31 came from 12, so a historical query can follow
the lineage if asked.

> Design rule: **never rewrite a `unit_participation` to point at a different unit.** Close
> it and open a new one. Rewriting destroys the answer to "where was this child in 2003?"

### A unit never changes parent

`parent_unit_id` is **immutable**. If a group genuinely transfers from one pack to another,
the **old unit closes and a new unit is created** under the new parent, the people are moved
across, and the lineage is recorded as an `org_unit_relationship`.

This is a significant simplification rather than a limitation:

- **The materialized `path` never needs a subtree cascade rewrite**, so the dangerous
  operation disappears along with its danger.
- **Historical reports cannot silently change.** "Who was in the 4th Pack in 2001?" keeps
  answering the same thing forever, because no unit's ancestry is ever edited.
- Retroactive reparenting — the hard case — becomes unrepresentable rather than difficult.
- **`scope_exposure` rows cannot shift meaning under their authors.** A reparent would move
  a unit in or out of a parent's reach, silently re-scoping rows nobody edited. It cannot
  happen, so it cannot be forgotten.

**No write may change `parent_unit_id` on a row that already has one.** Until D-072 this was a
trigger; nothing in the docs carries it now, and unlike most such rules **no report catches the
violation either**, because the damage is not a bad row, it is a set of previously-correct rows
whose meaning moved. So this one needs a positive guard in the write path — reject the update, do
not warn about it — and a test that attempts the update. See
[data-model/02-organization.md](../data-model/02-organization.md#a-unit-never-changes-parent).

---

## 4. Positions

A **position** is a defined slot in a unit. A **position assignment** is a person
filling it for a period. This split is what lets the system say "Pack 12 has no
scoutmaster right now" and "this position has been vacant since March" — both operationally
important, and neither expressible if positions only exist when filled.

A position is defined against a `unit_type_id` and carries a `code` — `scoutmaster`,
`assistant_leader`, `treasurer`, `quartermaster` are the ordinary ones — a `title`, a
`max_holders`, and `requires_membership`: must the holder be a current member.

An assignment joins three things and dates them: the `position`, the `org_unit` it is filled in,
the `person` filling it, and the period. It also carries `is_primary`, because some people hold
several positions; an `appointment_reference` to the appointment letter or record; and an
`ended_reason`.

### Multiple people share one position

**Several people may occupy the same position at the same time, and that is the default.**
A pack with three assistant leaders, two quartermasters, or a rotating team of instructors
is ordinary, not exceptional.

`position.max_holders` is how a single-holder position is expressed — `1` for a
scoutmaster, `NULL` (unlimited) for everything else. Two consequences worth being explicit
about:

- **Multiple occupancy is the default, not an exception.** `max_holders` is nullable, so a
  newly invented position accepts several holders without anyone declaring it. Single
  occupancy is the case that has to be stated.
- **The limit belongs to the position, not the hierarchy.** A parent unit cannot declare
  that a nested unit has one scoutmaster. What positions a unit defines, and how many
  holders each admits, is that unit's own business — the same principle as
  [authority over a unit originating at the unit](06-authorization-model.md#2-scope-authority--no-downward-inheritance).

**The limit is enforced below the application** — a constraint or a check inside the writing
transaction — rather than in the form, because the limit lives on a different table and because
`max_holders > 1` cannot be expressed as a unique index. **The reason this cannot wait for the ORM
to work it out is the second clause:** there is no declarative shape for "at most N open rows", so
a generated schema silently has no limit at all, and the failure is invisible until two people hold
the one chair. See [../data-model/02-organization.md](../data-model/02-organization.md#7-position-and-position_assignment).

**A person may hold the same position in the same unit across separate periods** — left in
2020, returned in 2024 — and both periods remain as distinct rows. Overlapping assignments
of the same person to the same position are prevented; sequential ones are the point.

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

`requires_membership` handles the common rule that a leader must be a current member.
Enforcing it as a **database constraint is not possible** (it depends on temporal membership
state), so it is an application rule plus a periodic consistency report. Do not attempt to
enforce it with a foreign key.

Note this is *reported* for positions but **enforced for roles**: the permission resolver
itself checks membership state for roles that require it — see
[D-039](../decisions/decision-log.md#d-039--member-permissions-require-a-current-paid-membership)
and [§6](#7-units-and-permissions).

---

## 5. Participation (`unit_participation`)

A **sub-unit's roster is participation, not membership.** These are different facts:

| | Membership | Participation |
|---|---|---|
| **Of what** | The organization (the root unit) | One sub-unit |
| **How many** | Exactly one at a time | Zero or more, simultaneously |
| **Costs money** | Yes — the yearly fee | No |
| **Ends when** | The fee is unpaid | The person stops attending |

A person may take part in a Thursday group, a weekend pack and a summer team at once, while
holding a single membership. Moving between groups is one row edit and costs no membership.

A participation row is a `person`, an `org_unit`, and a period, with a `join_reason_code` and a
`leave_reason_code`, an `is_primary` marking which group to show first, and a `role_in_unit`
that is a display convenience and **not an authorization fact** — nothing in the permission
model reads it.

**A participation row is created for the root unit when the membership is created**, so
"everyone in unit X" is one uniform query whether X is the organization or a Thursday-evening
pack. The schema detail is in
[data-model/03-membership.md](../data-model/03-membership.md#5-unit_participation).

---

## 6. Historical units

Units that closed must remain queryable. `org_unit.status = 'closed'` with `valid_to` set.
They are excluded from pickers by default and included in historical reports always.

Two things to get right:

1. **A closed unit is not deleted.** Historical `unit_participation` rows reference it, and
   "who was in the 4th Pack?" must work forever.
2. **Reopening reuses the row** if it is genuinely the same unit, or creates a new one if
   the organization considers it a fresh start. This is an organizational judgement, not a
   technical one — record which was chosen and why on the unit, so the answer is not
   re-litigated every time someone asks about the 80s unit with the same number.

**A unit that changes parent is a new unit** (§3), so `parent_unit_id` is immutable and the
historical answer to "where did this unit sit?" never changes retroactively.

---

## 7. Units and permissions

Units are a **scope** for authority. The same role assignment mechanism handles both
organization-wide and unit-scoped authority:

An assignment names a `person` and a `role`, the scope it applies in, and the period. The scope
is a `scope_type` of `organization` or `org_unit`, with `scope_id` absent for the former and a
unit for the latter — the two always agree, and there is no third shape.

So "treasurer of the organization" and "treasurer of Pack 12" are the same table and the
same role — differing only in `scope_type`/`scope_id`.

**Authority does not flow down the hierarchy.** This is the rule that most shapes the
permission system, and it is stated in full in
[06-authorization-model.md](06-authorization-model.md#2-scope-authority--no-downward-inheritance).
In brief:

- A role assignment at a unit covers **that unit only**.
- A parent unit — including the organization itself — **cannot** decide permissions inside a
  nested unit.
- **But not everything is a nested unit's business.** The person registry, the memberships
  and the fees belong to the **root** ([D-035](../decisions/decision-log.md#d-035--one-root-unit-all-sub-units-nest-arbitrarily-beneath-it)),
  so an organization-scoped role acting on them is working at its own scope. What a sub-unit
  owns is its own events, its own rosters, its own local leadership.
- Authority crosses a unit boundary downward **only** where the unit itself has written an
  explicit `scope_exposure` row granting a specific role assignment coverage over it.
- `system_admin` is the sole exception.

A permission check therefore matches the scope **exactly**, plus any explicit exposures.
**There is no ancestor walk in permission resolution.** `unit_ancestors()` exists in the
schema for reporting and for the exposure-direction check, but it must never appear in a
permission path — see
[data-model/02-organization.md](../data-model/02-organization.md#6-hierarchy-traversal).

### Unit-scoped access grants

Beyond roles, a unit can be the target of an item-scoped grant: an `access_grant` whose scope
type is `org_unit`, whose scope id is that unit, and whose level says how much.

This is how you grant someone authority over a unit's data without giving them an
organization-wide role — a temporary administrator for one pack, for instance. Note the
grant is written **against the unit**, and creating it requires `access_grant.create` held
at that unit. A parent unit cannot create it.

**The grantee may also be a set of people, rather than one person** ([D-042](../decisions/decision-log.md#d-042--grants-may-target-audiences-not-only-individuals)):
`access_grant.person_id` and `access_grant.audience_id` are mutually exclusive. "Expose this
event to everyone" or "to this pack's leaders" is **one row** with an audience — a rule the
resolver evaluates against current state — rather than one row per person. This is what
replaced the bulk scope-exposure tool ([D-045](../decisions/decision-log.md#d-045--the-bulk-scope-exposure-tool-is-removed)),
and it is why that tool had no remaining job.


---

## 8. Open issues

- The actual unit type vocabulary and nesting rules. Because nesting is permissive by
  default and one root is mandatory, this is now a much smaller question: which types exist,
  and which of the few genuine constraints does the organization want stated as rules.
- Whether the root unit may *see* what happens in its sub-units without those sub-units
  exposing their scope — a reporting/audit question, not a permission-inheritance one.
  [D-035](../decisions/decision-log.md#d-035--one-root-unit-all-sub-units-nest-arbitrarily-beneath-it)
  argues the root already owns the registry and the fees, so this is narrower than it first
  appears.
- Whether `is_leadership` should automatically create a `role_assignment`, or only suggest it.

Resolved and no longer open, kept here so the reasoning is visible: the organizational
structure itself (§1), retroactive reparenting (now prohibited — §3), unit types containing
children (§1), and whether a person may belong to several units at once (yes, by
participation — §5).

All tracked in [../open-questions.md](../open-questions.md).
