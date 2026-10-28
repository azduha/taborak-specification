# Data Model — Organization Structure

`org_unit`, unit types, name history, restructuring, positions, and assignments.

Domain rationale: [../domain/04-organization-structure.md](../domain/04-organization-structure.md).

---

## 1. `org_unit_type`

**Fields**

| Field | Kind | Notes |
|---|---|---|
| `code` | text, required | `'organization'`, then whatever the organization defines. |
| `name` | text, required | |
| `description` | text, optional | |
| `is_leaf` | boolean, required, defaults to false | A leaf may contain participants but not sub-units. A weekly meeting group is usually a leaf, but not necessarily — nesting is arbitrary (D-035). |
| `max_depth` | integer, optional | Maximum nesting depth for this type, relative to the root. Unset = unconstrained. |
| `sort_order` | integer rank, required, defaults to 0 | |
| `valid_from`, `valid_to` | period (from/to, open-ended allowed); both ends optional | Types are retired, not deleted: a 1995 `six` unit type must still resolve in historical queries. |
| `created_at` | timestamp, audit time | |

**Rules**

- `code` is unique over **all** rows, retired ones included — a type that has been withdrawn still holds its name against a newcomer.
- Where both ends of the period are set, `valid_to` is later than `valid_from`. Either end may be absent, and no comparison is attempted when one is.
- One row per `code` is the current one; the current row for a code is found among the rows with no `valid_to`.

**Types are rows, not an enum**, so the vocabulary can change across decades without a
deployment. See [../domain/04-organization-structure.md](../domain/04-organization-structure.md#1-one-root-arbitrary-sub-units).

**`allows_minors` was a column on this table; [D-095](../decisions/decision-log.md#d-095--units-carry-no-restrictions-joining-one-is-somebody-elses-act)
removed it, and the rule it named is now enforced by who may write the row.** The flag was introduced as a
safeguarding replacement for hardcoded type checks — *"a minor may not take part in the legal-and-filing
unit"* read the flag instead of listing type codes — and the argument that removed it is D-095's, not
repeated here. **Who enforces it now:** `unit_participation.manage` at that unit, held by the people who run
it, with no self-scoped variant; a person able to add a child to a unit is a person that unit's leadership
trusts with its roster, the write is audited, and the row names who made it. That is a stronger control
than a boolean on a type, because the boolean only ever refused a placement nobody had thought about while
the permission refuses every placement by the wrong person regardless of the child's age. **What is
genuinely lost is stated once, in D-095, and it is not small: the system no longer knows which units are
for children**, and nothing on this table replaces that. The sentence this note replaces also explained why
there is no `allows_adults` sibling; with no `allows_minors` there is nothing to be a sibling of, and
`position.min_age` remains a real eligibility constraint about the *position* rather than about the unit
(§7), which D-095 left untouched.

---

## 2. `org_unit_type_rule`

**Fields**

| Field | Kind | Notes |
|---|---|---|
| `parent_type_id` | reference to `org_unit_type`, optional | A `parent_type_id` that is absent means **"at the root"** — this type may be a top-level unit. |
| `child_type_id` | reference to `org_unit_type`, required | |
| `is_required` | boolean, required, defaults to false | True: a unit of `child_type` must have a parent of `parent_type`. False: permissive. |
| `max_children` | integer, optional | Optional cap on how many children of this type a parent may have. |
| `valid_from`, `valid_to` | period (from/to, open-ended allowed); both ends optional | |
| `created_at` | timestamp, audit time | |

**Rules**

- A rule may not name the same type as both its parent and its child. A rule with no parent type is exempt, because it has no parent to collide with.
- At most one **live** rule per (`parent_type_id`, `child_type_id`) pair — live rows only, so a superseded rule does not block its replacement. An absent `parent_type_id` counts as a value in that comparison; compared as plain nulls, duplicate root rules would slip through.

**Why a table rather than `CHECK` constraints or code.** Nesting rules in this
organization will change (a new level added, a type retired). A rule expressed in code is
invisible to the people configuring the organization and requires a deployment to change.
A rule in a table can be reviewed, exported, and audited.

**Enforcement note.** A `CHECK` cannot express "the parent's type must be permitted by a
rule", because it requires a lookup into another table — and nothing else declarative expresses
it either. The enforcement is therefore one ordered check, run once per row **inside the
transaction that writes the unit**, on insert and on any update that touches
`parent_unit_id` or `unit_type_id`. Inside the transaction is the part worth holding onto: a
nesting validated only in the model layer is walked straight past by the legacy import, by a row
someone corrects by hand, and by a second client, and all three exist here by design
([00-conventions.md §6a](00-conventions.md#6a-who-enforces-an-invariant-now)). Validating the
same steps in the application is still worth writing, because it produces the good error
message; it is not the enforcement. The steps and their order are the rule:

1. If the unit has no parent, look for a rule with no parent type whose child type is this
   unit's type and whose `valid_to` is absent or still in the future. (This branch reads
   `valid_to` only; `valid_from` is not part of it.)
2. If none was found **and** any rule at all names this type as its child — disregarding
   whether that rule is still live — refuse: this unit type may not exist at the root.
3. If none was found and no rule names this type as its child at all, accept. This is the
   permissive default.
4. If the unit does have a parent, read that parent unit's type.
5. Look for a rule pairing that parent type with this unit's type whose `valid_from` is
   absent or already reached and whose `valid_to` is absent or still in the future.
6. If none was found **and** the parent type has any rule at all — again disregarding
   validity — refuse: this unit type may not be nested under that one.
7. Otherwise accept.

The two refusals are each conditional on rules existing for the relevant side, and that
condition is evaluated *unconditionally*, against retired rules as well as live ones. A type
therefore has exactly two states: governed by rules, or untouched by them.

Note the permissive fallback: a type with **no** rules defined at all is unconstrained.
This matters during initial setup — the check must refuse nothing while the rule table is
still empty, or the first units could never be created. It also means the rules are opt-in, and
[§9](#9-integrity-checks) verifies them.

---

## 3. `org_unit`

**Fields**

| Field | Kind | Notes |
|---|---|---|
| `id` | surrogate id | Internal only; never exposed. |
| `public_id` | uuid, required, generated | The identifier used outside the system, and unique. |
| `unit_type_id` | reference to `org_unit_type`, required | |
| `parent_unit_id` | self-reference to `org_unit` (the parent), optional | Nullable **only** for the single root unit — the organization itself. See `uq_org_unit_single_root` below, and D-035. Immutable once set — see *A unit never changes parent*, and D-036. |
| `code` | text, optional | Short human code, e.g. `T12`. Not unique globally — two sub-units may both have a `T1`. |
| `name` | text, required | Current display name. **Denormalised convenience.** The history is in `org_unit_name` (§4). Queries about the past must read `org_unit_name`, never this column. |
| `status` | text, required, defaults to `active` | One of `proposed`, `active`, `merged`, `closed`. |
| `valid_from` | date, required | |
| `valid_to` | date, optional | NULL = still exists. |
| `closed_reason_code` | text, optional | |
| `closed_note` | text, optional | |
| `path` | text, required | Denormalised for fast ancestor queries. Maintained on write, see §6. |
| `depth` | integer, required | Number of segments in `path`; §6. |
| `data_confidence` | text, required, defaults to `high` | One of `high`, `medium`, `low`. |
| `created_at`, `created_by`, `updated_at`, `updated_by` | timestamp, audit time; reference to `person` | The standard audit columns. `created_by` is NULL for system and import jobs. |
| `import_batch_id` | reference to the import batch, optional | Set on imported rows. |

**Rules**

- Where both ends of the period are set, `valid_to` is later than `valid_from`.
- A unit may not be its own parent.
- `code` is unique **within a parent**, compared case-insensitively, among **live units only**
  — a closed unit's code is free again. Units with no code are outside the rule, and units at
  the root are compared with one another rather than exempted: an absent parent counts as a
  value.
- **Exactly one unit may exist at the root.** The organization itself. `uq_org_unit_single_root`
  is the name this rule carries here, and the layer that must carry it is a migration: it is
  uniqueness over the rows that have no parent, which is the conditional shape
  [00-conventions.md §6a](00-conventions.md#6a-who-enforces-an-invariant-now) says an ORM will not
  emit and a migration must.

**Indexes**

- On `path`, for prefix matching — this is what makes the set-based subtree question in §6.1
  cheap.
- On `parent_unit_id`, for walking one level of the tree.
- On `unit_type_id`, restricted to live units, and on live units generally: "what exists
  right now" is the question the partial indexes are for.

**The one-root rule is the whole of "there is one organization", and it is the load-bearing kind:
a constraint, not a convention.** At most one row with `parent_unit_id IS NULL` may exist, and the
rule deliberately ignores `valid_to` — even a closed root is still *the* root. A second root is not
an untidy state but a second organization, and only something running at the database can refuse
the insert that creates one. It is shape 2 of
[open question F-10](../open-questions.md#f-10--which-invariants-the-orm-cannot-express-and-who-writes-those)
— unique, but only among rows satisfying a condition — so the migration emits a partial unique
index and not the plain one, which would be a different rule: a plain unique constraint over
`parent_unit_id` would reject every sub-unit, since they all share a parent.
See [D-035](../decisions/decision-log.md#d-035--one-root-unit-all-sub-units-nest-arbitrarily-beneath-it).

**A unit cannot be closed without an end date** (`ck_org_unit_closed` is this rule's name).
Two columns of one row, so a migration can state it directly as a check on the row — the easy
shape, and worth stating as a requirement precisely because no object in this repository carries
it any more. Without it you get closed units with `valid_to IS NULL`, which then appear in
"currently active units" queries forever.

**Why `code` is not globally unique.** Unit numbering restarts and has been reused across
decades, and with arbitrary nesting two sub-units under different parents will legitimately
both be "1". A global unique constraint would reject real historical data during import.
Uniqueness is scoped to the parent and to live rows.

**And because it is scoped to live rows, a number coming back is legal — which raises the question
D-096 answers: is the new bearer the old unit?** A `code` is **a short human label somebody types**
(`T12`, `4. oddíl`). It is not the unit's identity, which is the row; it is not its name, which is a
temporal row of its own (§4). **A reused number is therefore a new `org_unit` row**, with its own period,
and the continuity between the two bearers is not a property of the label but an assertion somebody makes
and records as an `org_unit_relationship` with `successor_of` (§5). **The default matters precisely because
it is easy to leave unstated:** "match on code" reuses the row and lets a thirty-year gap show inside one
unit's life, which is what a system drifts into when nobody writes the rule down, and it makes "who was in
Pack 12 in 1984?" answerable by an overlapping name rather than by a record. D-096's cost is that someone
has to write a sentence down occasionally, when a troop really is refounded after a decade dormant; the
record then carries the direction the default goes in when nobody does.

### A unit never changes parent

`parent_unit_id` is **immutable**. This is not a convention — it is enforced inside the
transaction that writes the row, once per row, on any update that touches `parent_unit_id`,
in this order:

1. If `parent_unit_id` differs from its previous value in **any** way — including being set
   from nothing, or cleared to nothing — refuse, naming the unit, and say what to do instead:
   a unit that moves is a new unit; close this one and create its successor under the new
   parent, recording the lineage in `org_unit_relationship`.
2. Otherwise allow the write.

**Why a guard inside the database rather than a rule in the application.** Reparenting is the
one edit that would silently rewrite history: it changes what every historical report means,
moves a unit in and out of every ancestor's scope, and invalidates the materialized `path`
for the whole subtree. None of those failures are visible at the moment of the edit — which is
exactly why checking them in the application does not qualify, since the legacy import, the
hand-corrected row and a second client all change parents without ever passing the screen that
would refuse them. The comparison still costs something, and the migration must be able to pay
it: this is shape 4 of
[open question F-10](../open-questions.md#f-10--which-invariants-the-orm-cannot-express-and-who-writes-those)
— a column that may not change once it is set — and no declarative constraint in any database
states it, so this guard is one the migration writes by hand rather than one an ORM generates. See
[D-036](../decisions/decision-log.md#d-036--units-cannot-be-reparented-a-unit-that-moves-is-a-new-unit).

**The consequence is a simplification, not a loss.** Because the parent never changes, the
`path`/`depth` denormalisation never needs a subtree cascade rewrite, and "who was in this
unit in 2001?" keeps answering the same thing forever.

**A genuine move is recorded as a succession**, and the people are moved across explicitly —
see `org_unit_relationship` in [§5](#5-org_unit_relationship--splits-mergers-succession).

---

## 4. `org_unit_name` — rename and renumber history

**Fields**

| Field | Kind | Notes |
|---|---|---|
| `org_unit_id` | reference to `org_unit`, required | |
| `name` | text, required | The name the unit went by in this period. |
| `code` | text, optional | The code that went with it. |
| `valid_from` | date, required | |
| `valid_to` | date, optional | NULL = the current name. |
| `change_reason` | text, required | One of `established`, `rename`, `renumber`, `reorganisation`, `correction`, `import`. |
| `change_note` | text, optional | |
| `source` | text, optional | `staff` or `legacy_import`. |
| `import_batch_id` | reference to the import batch, optional | Set on imported rows. |
| `created_at`, `created_by` | timestamp, audit time; reference to `person` | |

**Rules**

- Where both ends of the period are set, `valid_to` is later than `valid_from`.

**One unit, one current name.** `uq_org_unit_name_open` is this rule's name; it is conditional
uniqueness over the open rows, the shape [00-conventions.md §6a](00-conventions.md#6a-who-enforces-an-invariant-now)
says a migration must emit by hand, and a uniqueness constraint over all rows would be a different
and wrong rule. The denormalised
`org_unit.name` must always equal that row, and nothing maintains the copy by itself any more:
**no write may change the current name row without setting `org_unit.name` in the same
transaction.** The failure mode is the one invariant 4 in [§9](#9-integrity-checks) counts — a
system that displays one name and reports under another — and it is reachable from any path that
writes `org_unit_name`, the legacy import included, so the pairing is a requirement on the write
rather than something a form handler remembers. Invariants 3 and 4 are the net beneath it, not
the guard.

**Renumbering is a rename, not a new unit.** "4th Pack" becoming "Pack 12" with the same
participants is one `org_unit` row and two `org_unit_name` rows — which is why `code` is a column
here as well as on `org_unit`: the number that changed *is* part of what a name period records.
Creating a new unit would orphan all historical `unit_participation` rows and make
"who was in Pack 12 in 1998?" unanswerable.

**Three changes look alike and are three different writes; keep them apart.**

| What happened | What it is | What gets written |
|---|---|---|
| The same unit is given a different number, while its people carry on | **A rename.** One unit | One new `org_unit_name` row with `change_reason = 'renumber'`, `org_unit.code` updated to match, one row and one identity (§3's uniqueness rule is what makes the old code free) |
| The unit's number is taken again later, by a body that was not the first one | **A different unit.** Two units | A **new** `org_unit` row with its own period; the continuity, if anyone claims it, is an `org_unit_relationship` with `successor_of` (§5) — never a shared row (D-096, §3) |
| The unit moves under another parent | **A different unit.** Two units | The move itself is refused outright (§*A unit never changes parent*, D-036); a genuine move closes this row, creates the successor, and records the lineage in `org_unit_relationship` |

**The middle row and the bottom row are the pair worth memorising, because both produce two units and
only the reason differs.** A renumber and a reuse are told apart by whether the participants and the
period are continuous, which is a fact about the world that only a human knows — so the schema offers
`successor_of` and refuses to guess, and a screen that matched on `code` would quietly collapse the middle
row into the top one, which is exactly the failure D-096 was written to prevent.

**`change_reason` distinguishes a correction from a rename.** A correction means the
record was wrong (a typo fixed in 2026 about a 1998 name); a rename means the world
changed. Only the latter is real history. Conflating them corrupts historical reporting.

---

## 5. `org_unit_relationship` — splits, mergers, succession

**Fields**

| Field | Kind | Notes |
|---|---|---|
| `source_unit_id` | reference to `org_unit`, required | |
| `target_unit_id` | reference to `org_unit`, required | |
| `relationship` | text, required | One of `split_from`, `merged_into`, `successor_of`, `renamed_to`. Direction is source → target. `split_from`: the target was created from the source. `merged_into`: the source was absorbed into the target. |
| `effective_date` | date, required | |
| `note` | text, optional | |
| `source` | text, optional | |
| `import_batch_id` | reference to the import batch, optional | Set on imported rows. |
| `created_at`, `created_by` | timestamp, audit time; reference to `person` | |

**Rules**

- A unit may not have a relationship to itself.
- Nothing else is unique: the same pair of units may carry several relationships, and the
  same kind of relationship more than once.

**Indexes**

- On `source_unit_id` and, separately, on `target_unit_id`. Lineage is asked in both
  directions — "what did this unit become?" and "what did this one come from?" — and neither
  question may have to scan the table.

**`successor_of` is where D-096's continuity assertion goes, and it is the only place it may go.**
When a unit number comes back after a decade dormant, the new bearer is a new row (§3) and any claim that
it is the same troop *carrying on* is an assertion about the world, recorded here as
`source = the new unit`, `target = the old one`, `relationship = successor_of`, with the `effective_date`
of the refounding and a `note` saying who decided. **A renumber does not produce a row here at all** — it
is one unit and two name rows (§4), and a `successor_of` edge between a unit and itself is refused by the
first rule above anyway. The value of putting the assertion here rather than in a `code` collision is that
"who was in Pack 12 in 1984?" then follows a recorded edge instead of guessing from an overlapping label,
and that the person who refuses to claim continuity has an equally cheap way to say so: write nothing.

**This table exists so that historical lineage is answerable.** When Troop 12 splits into
Troop 12 and Troop 31, the question "was this 2003 member in the unit that is now Troop 31?"
requires following the relationship. Without it, the answer is only guessable from
overlapping member sets.

**Note it is not a tree.** A unit may have been split from one parent and merged into
another; the same pair may even have multiple relationships over time (split in 1998,
merged back in 2005). Hence `effective_date` and no uniqueness constraint beyond the pair.

**Do not rewrite history on a split.** Participants who moved to the new unit get a *new*
`unit_participation` row starting at the split date; their old row closes at the same date.
Rewriting the old row destroys "where was this child in 2003?" — see
[§8](#8-unit_participation-lives-in-03-membershipmd).

---

## 6. Hierarchy traversal

Two mechanisms. One is stored and is only as correct as whatever wrote it; the other is
computed when it is asked and is correct by construction.

### 6.1 Materialized path (fast ancestor/descendant queries)

`org_unit.path` holds a slash-delimited id path: `/1/7/42/103/`. `depth` is the number of
segments. It is derived, never supplied: the rule runs inside the transaction that writes the
row, once per row, on insert and on any update that touches `parent_unit_id`, in this order.
A caller that wrote `path` itself would be writing a number nobody verified.

1. A unit with no parent gets a path of its own id between two slashes, and depth 0.
2. A unit with a parent reads that parent unit's `path` and `depth`.
3. If there is no such unit, refuse the write — a unit cannot be placed under a parent that
   does not exist.
4. Its path is the parent's path with its own id appended, and its depth is the parent's
   depth plus one.

The order is the rule: the parent's own path must already be correct, which is why a unit can
only be created after its parent.

**No subtree cascade is needed, ever.** Because `parent_unit_id` is immutable
([§3](#a-unit-never-changes-parent)), a unit's path is computed once at insert and never
rewritten. The repeat of this rule on an update to `parent_unit_id` is therefore defensive
only — the no-reparenting check rejects the change before it.

This is the payoff of [D-036](../decisions/decision-log.md#d-036--units-cannot-be-reparented-a-unit-that-moves-is-a-new-unit):
the materialized path is a pure insert-time denormalisation, which is the only kind that
stays trustworthy without versioning.

### 6.2 Recursive CTE (correct regardless of path integrity)

Two questions, each answered by following `parent_unit_id` one hop at a time from a starting
unit until there is nowhere further to go:

* **`unit_ancestors(unit)`** — which units are above this one? Every ancestor, **nearest
  first**, and the unit itself excluded. Distance from the starting unit is part of the
  answer, so "this unit's district" and "this unit's region" are the same question at
  different distances.
* **`unit_descendants(unit)`** — which units are below this one? Every descendant, the unit
  itself again excluded.

Both read nothing but `parent_unit_id`, so both stay correct whatever `path` currently says.

> **`unit_ancestors()` must NOT be used by the permission resolver.** Authority does not
> flow down the hierarchy. The resolver matches scopes exactly, plus explicit
> `scope_exposure` rows — see
> [../domain/06-authorization-model.md](../domain/06-authorization-model.md#2-scope-authority--no-downward-inheritance).
> `unit_ancestors()` is used for **reporting** ("everyone in this district"), for the
> path-consistency check below, and for the exposure-direction integrity check — never in a
> permission path. Integrity check 13 in
> [05-authorization.md](05-authorization.md#11-invariants-to-verify) asserts this in CI.

**Both mechanisms are kept.** The path is for set-based queries — one prefix test over the stored
path rather than a walk — which is dramatically faster for "everyone in this district". The recursive CTE is the
authority when the path might be stale, and is used by the nightly consistency check:

Nightly, for every unit that has a parent: take its ancestors with `unit_ancestors()`,
rebuild the path that chain implies — every ancestor's id nearest-first, then the unit's own
id last, each delimited by slashes — and report the units whose stored `path` is not that
string. Root units are excluded; their path is their own id by definition, and there is no
chain to check it against. This is invariant 1 in [§9](#9-integrity-checks).

---

## 7. `position` and `position_assignment`

**Fields — `position`**

| Field | Kind | Notes |
|---|---|---|
| `unit_type_id` | reference to `org_unit_type`, required | A position is defined per unit **type**, not per unit: every troop has a scoutmaster slot. The slot is instantiated implicitly by the unit existing. |
| `code` | text, required | |
| `title` | text, required | |
| `description` | text, optional | |
| `max_holders` | integer, optional | How many people may occupy this position in one unit at the same time. Unset = unlimited. `1` = a single holder (a scoutmaster). **The default is unset, i.e. unlimited**, because multiple occupancy is the normal case in this organization: a troop may have several assistant leaders, several quartermasters, several instructors. Single occupancy is the exception and must be declared by the position itself. Note this is a limit a position declares about *itself*. It is never imposed from outside the unit. See domain/06-authorization-model.md §2 for why authority over a unit's structure originates at the unit. |
| `is_leadership` | boolean, required, defaults to false | Flags positions that carry organizational authority. Used to drive the convenience workflow that also creates a `role_assignment`. |
| `requires_membership` | boolean, required, defaults to true | What it says here is **reported, not enforced**. The flag drives the "leaders whose membership has lapsed" worklist below. Whether holding the corresponding **role** survives a lapse is a separate switch, `role.requires_membership`, and that one *is* enforced by the permission resolver (D-039). The two are deliberately not the same column: an adult volunteer commonly holds a position for years while their membership lapses and is renewed, and the organization wants to see that on a report without losing the volunteer's access. |
| `min_age` | integer, optional | Position eligibility, a real constraint: a scoutmaster must be an adult. This is about the position, not about membership — membership is ageless (D-038). |
| `sort_order` | integer rank, required, defaults to 0 | |
| `valid_from`, `valid_to` | period (from/to, open-ended allowed); both ends optional | |
| `created_at` | timestamp, audit time | |

**Rules — `position`**

- Where both ends of the period are set, `valid_to` is later than `valid_from`. Either end may
  be absent, and no comparison is attempted when one is.
- `max_holders` is either unset or at least 1. There is no position that admits nobody.
- A position `code` is unique **within its unit type**, compared case-insensitively, among
  **live positions only**.

**Fields — `position_assignment`**

| Field | Kind | Notes |
|---|---|---|
| `position_id` | reference to `position`, required | |
| `org_unit_id` | reference to `org_unit`, required | The concrete unit. `position.unit_type_id` must match that unit's `org_unit.unit_type_id`; a reference between two rows cannot express this, so it is verified on write, and invariant 6 in §9 reports what slips through. |
| `person_id` | reference to `person`, required | |
| `valid_from` | date, required | |
| `valid_to` | date, optional | NULL = still in post. |
| `is_primary` | boolean, required, defaults to true | Some people hold several positions; one is primary for display and contact. |
| `appointment_reference` | text, optional | |
| `ended_reason_code` | text, optional | |
| `ended_note` | text, optional | |
| `created_at`, `created_by`, `updated_at`, `updated_by` | timestamp, audit time; reference to `person` | |
| `import_batch_id` | reference to the import batch, optional | Set on imported rows. |

**Rules — `position_assignment`**

- Where both ends of the period are set, `valid_to` is later than `valid_from`.
- A person may not hold the same position in the same unit over overlapping periods. The rule
  covers **every row, open and closed alike** — there is no status to scope it by.

**Indexes — `position_assignment`**

- On `person_id` with `valid_from` descending, for "what does this person hold, most recent
  first".
- On `org_unit_id`, and on `position_id`, each restricted to **open** assignments: "who runs
  this unit now" and "who holds this slot now" are the questions that run constantly, and both
  look only at rows that are still in post.

**The holder limit.** Where a position declares one, no write may leave the unit holding more
open assignments of it than the limit allows. It is enforced inside the transaction that writes
the assignment, once per row, on insert and on any update that touches `position_id`,
`org_unit_id` or `valid_to` — and the count is read *inside* that transaction, not before it,
because two inserts that each counted before either had landed are how a single-scoutmaster
unit ends up with two scoutmasters. The order is the rule:

1. Read the position's `max_holders`.
2. If it is unset, or the row being written is itself a closed assignment, allow it — there is
   no limit, or nothing is being opened.
3. Count the **open** assignments of this position in this unit, excluding the row being
   written from its own count.
4. If that count has reached `max_holders`, refuse, naming the position, the unit, the current
   holder count and the limit.
5. Otherwise allow it.

**Why no unique index does this, whatever emits it.** The limit is `position.max_holders`, which
lives in another table, so an index predicate cannot express it — and a partial index
predicate may not contain a subquery in any case. Nothing declarative handles `max_holders > 1`
either: an index can say *at most one*, never *at most n, where n is a column of another table's
row*. None of that argument was about the mechanism that D-072 deleted; it stands, and it now
reads as a statement about what the migration must be able to express and cannot. **This is the
weakest-enforced rule in this document.** It is shape 3 of
[open question F-10](../open-questions.md#f-10--which-invariants-the-orm-cannot-express-and-who-writes-those),
the class whose answer comes from another table, and F-10's remedy for that class has two parts:
a check inside the writing transaction, plus a report. The first is required above; the second
does not exist — §9 lists no over-limit report — so if the migration omits its guard, the limit
holds only for as long as every caller chooses to obey it.

**Note the absence of a uniqueness rule on the assignment triple.** There is deliberately
no uniqueness over the triple of person, position and unit: a person may hold the same position in
the same unit across *separate periods* (left in 2020, returned in 2024), which is
historical fact and must remain representable. Overlap is still prevented, directly on the
row:

One person, one position, one unit: no two assignments of the same person to the same position
in the same unit may cover the same date. Periods are half-open, so a row ending on a day and a
row beginning on that same day do not collide.

Without this, the same person could be double-counted as holder of the same position in the
same unit over overlapping dates — which would defeat the holder limit itself by consuming
two of the slots.

**What no database constraint can enforce, and must be handled elsewhere:**

**7.1 `requires_membership` and `min_age`.** Both depend on temporal state in other tables, so
no FK or check constraint can express them. They are application-level validations plus a
periodic report:

* **Holders who are not currently paid-up members.** Every assignment still in post, of a
  position that asks for membership, whose holder `is_current_member()` says is not a member.
  Needs attention, but is **not** an access problem — see the note below.
* **Holders below the position's minimum age.** Every assignment still in post, of a position
  that sets `min_age`, whose holder has not yet reached that age today. A holder with **no
  recorded birth date** is reported as well: eligibility cannot be established for them
  either.

> **An unpaid volunteer holding a position is a bookkeeping problem, not a
> safeguarding one.** The important consequences:
>
> - Note that `requires_membership` here is a *report*, while `role.requires_membership` is
>   *enforced* by the resolver ([D-039](../decisions/decision-log.md#d-039--member-permissions-require-a-current-paid-membership)).
>   The holder may lose their **system access** the moment the fee lapses, while still
>   legitimately holding the **position**. That asymmetry is intentional — see
>   [03-membership.md §6](03-membership.md#6-membership-and-the-authorization-system) — but
>   any role that exists to make a position work should almost certainly be defined with
>   `requires_membership = false`, or the volunteer loses access to the tools their position
>   needs.
> - **No background checks are recorded in this system at all**
>   ([D-043](../decisions/decision-log.md#d-043--no-background-checks-are-recorded-in-this-system)).
>   If the organization ever introduces them, the natural home is a dated record with an
>   `expires_at`, plus a `person_identifier` scheme — and it would warrant a daily alerting
>   report, because a lapsed clearance is a safeguarding matter rather than a data-quality
>   one.

**7.2 Holder limits are a per-position declaration, not a structural rule.** See the holder
limit above and `max_holders`. The important consequences:

- **Multiple occupancy is the default.** `max_holders IS NULL` means unlimited, so a new
  position kind accepts several holders without anyone having to state it.
- **Single occupancy never arises from the hierarchy.** A parent unit cannot declare that a
  nested unit has one scoutmaster. The limit is a property the position carries, and the
  positions in a unit are that unit's own business.
- **An over-limit condition is a business error, not a crash.** Two people legitimately
  sharing a position during a handover is a normal transient state; resolution is either
  closing one assignment or raising the limit.


**Positions are not permissions.** Holding `scoutmaster` grants no system capability. The
association between a position and authority is made explicitly through `role_assignment`,
and `position.is_leadership` exists only so a workflow can offer to create both at once.
See [../domain/04-organization-structure.md](../domain/04-organization-structure.md#4-positions).

---

## 8. `unit_participation` lives in 03-membership.md

Taking part in a sub-unit is a separate table from membership of the organization, because
they have different lifetimes — a person may hold a membership while taking part in no
sub-unit at all, or take part in several at once.

The name matters: this is **participation**, not a second kind of membership
([D-041](../decisions/decision-log.md#d-041--belonging-to-a-sub-unit-is-a-participation-record-not-a-membership)).
Everyone registers and pays at the root; the sub-units hold rosters, not memberships.

See [03-membership.md](03-membership.md#5-unit_participation).

---

## 9. Integrity checks

**Invariants to verify**

1. **A stored `path` that disagrees with the actual tree** (§6.2). Counts units whose stored
   path is not the one their parent chain implies; any non-zero count means the insert-time
   denormalisation has drifted.
2. **A unit whose parent is closed but which is itself open.** Counts live units hanging off
   a unit that has ended; non-zero means the tree currently claims to contain something inside
   a unit that no longer exists.
3. **A live unit with no current name row.** Counts live units with no open `org_unit_name`
   row at all; non-zero violates the denormalisation invariant directly — there is no current
   name to copy into `org_unit.name`.
4. **`org_unit.name` disagreeing with the unit's current `org_unit_name` row.** Counts live
   units whose denormalised display name differs from the open name row; non-zero means the
   system displays one name and reports another.
5. **A live unit type with no nesting rules at all** — neither as a parent nor as a child.
   Usually fine: nesting is permissive by default and a new type starts unconstrained. But a
   type that has been in use for years with no rules is probably an oversight worth reviewing.
6. **A position assignment whose position's unit type is not the unit's type.** Counts
   assignments pairing a position defined for one type with a unit of another; non-zero means
   the check on write was bypassed.
7. **A unit with exactly one live child.** Non-zero is often a data-entry error and sometimes
   real; it is a list to read, not a failure.
9. **A position holding more people than its own limit allows.** Counts, for each position
   with `max_holders` set, its open assignments, and reports the positions where the count
   exceeds it. Unlike event capacity ([08-events.md §10 check 5](08-events.md#10-integrity-checks))
   an overrun here is **not permitted**: §7 calls it a business error rather than a choice an
   adult may make deliberately, and a non-zero result therefore means the check on write was
   bypassed — an import, a bulk reorganisation, a hand-fixed row. **This check exists because
   the guard alone is not enough to notice.** The holder limit cannot be stated as a constraint
   at all ([F-10 shape 3](../open-questions.md#f-10--which-invariants-the-orm-cannot-express-and-who-writes-those)),
   so if the migration omits it the only evidence that anything was expected is §7's prose,
   which a database cannot read. A limit nobody checks and nothing reports is a limit that
   holds until the first import.
10. **The single-root rule still exists.** A second root is impossible while
   `uq_org_unit_single_root` is carried by a migration, so what is verified here is that the
   migration really emitted it — the rule's existence rather than the data: should it ever be
   dropped, this fails even though nothing in the table has gone wrong, and the build must fail
   with it. The same pattern as the
   `unit_ancestors()` assertion in
   [05-authorization.md](05-authorization.md#11-invariants-to-verify).

**Checks 9 and 10 are not data-quality reports and should not be read like one.** They fail on
a *missing guarantee* rather than on bad rows, so both belong in CI: check 9 is the only thing
that would notice an unenforced holder limit, and check 10 asserts that a migration emitted a
constraint. Check 10 is the structural one — with reparenting prohibited
([§3](#a-unit-never-changes-parent)), the single-root rule and the recursive ancestor walk are
the two things everything else in the authorization model assumes, and both are worth asserting
rather than trusting.

**Checks 3 and 4 are the ones to read every morning.** They detect the denormalisation drifting,
which otherwise produces a system that displays one name and reports under another.

---

## 10. Seed data

The vocabulary is data, so it belongs in a migration. Two parts: the single root, and
whatever sub-unit types the organization actually uses.

Concretely, the organization begins with two rows of data and nothing else: one unit type for
itself — `organization`, not a leaf — and the single root unit that carries it. The root unit
has no parent (§3), and a period that opens early enough to precede anything the organization
will later import and never closes. No sub-unit type is seeded at all: the organization defines
its own (D-054).

> **The sub-unit vocabulary is not seeded, and this is the decision rather than a gap.**
> The seed contains the root and nothing else; `org_unit_type` is **runtime data**, exactly
> like `role` ([D-052](../decisions/decision-log.md#d-052--roles-are-runtime-data-the-seed-set-is-not-a-specification)).
> The organization creates the types it actually uses, renames them, and adds new ones as its
> structure changes ([D-054](../decisions/decision-log.md#d-054--the-sub-unit-vocabulary-is-not-seeded-the-organization-defines-its-own-types)).
>
> Previous revisions seeded a guess — `pack`/`group`/`team`, and before that a
> `national`/`region`/`district` ladder. Both were invented words that read as a
> specification. **Not guessing is the better answer**, because a wrong vocabulary in seed
> data is harder to dislodge than an absent one.
>
> **The words still appear throughout these docs as illustration.** "A pack has its own
> roster" explains a self-governing sub-unit; it is not a type the system ships with. Read
> them as "some sub-unit type the organization has defined".
>
> **Nesting is therefore entirely permissive** — `org_unit_type_rule` (§2; it was called
> `org_unit_type_nesting` here until this round corrected the name) is seeded with
> nothing, so any type may sit under any other, including directly under the root, until the
> organization states a rule. A new type is usable the moment it is created.
>
> **The root type is the one exception and must stay seeded.** Exactly one unit has
> `parent_unit_id IS NULL` ([D-035](../decisions/decision-log.md#d-035--one-root-unit-all-sub-units-nest-arbitrarily-beneath-it))
> and it needs a type, and that is now the *only* thing the seed says about it. It used to add
> `allows_minors = false` — *"no minor belongs to The Organization as a unit"* — and
> [D-095](../decisions/decision-log.md#d-095--units-carry-no-restrictions-joining-one-is-somebody-elses-act)
> removed the column, so the note goes with it. **That removal is a correction and not only a
> deletion:** the claim was false in the model as built, since every minor who pays the fee gets a
> membership at the root and D-050 gives that membership a participation row on the root unit — the
> seed was asserting the opposite of what the membership flow does, about the one unit where it
> matters most.

**Position definitions, by contrast, are a real starting set** and worth filling in — they
are what `position_assignment` hangs off, and `min_age` / `requires_membership` on them are
the eligibility rules §7.1 reports on — reports, because nothing rejects those two at the write.

---

## 11. Open issues

- The real sub-unit type vocabulary (§10). One root and arbitrary nesting are settled; the
  words are not.
- May the root **read** what happens in its sub-units, or must each sub-unit expose its
  scope first? The root owns the registry and the fees, so this is narrower than it was —
  it is about the sub-units' own events and rosters. See
  [../open-questions.md](../open-questions.md#c-1--may-the-root-see-what-happens-in-its-sub-units).
- Whether a person may hold positions in units of different types simultaneously.
- Whether `is_leadership` should automatically create a `role_assignment`, or only suggest it.
- Whether `allows_minors` should also constrain `position_assignment`, or only
  `unit_participation` — currently it is specified for participation and the position side
  relies on `position.min_age` instead (a minor could in principle hold a position defined
  with `min_age IS NULL` in a unit that excludes minors).

**Resolved and no longer open**, kept visible so the reasoning survives: the organizational
structure itself (one root, arbitrary nesting — D-035); retroactive reparenting (prohibited
outright, and enforced inside the database rather than in the application — D-036); organization-wide operational roles (largely
dissolved by D-035, since the root owns the registry and the fees); and background checks
(none are recorded — D-043).

All tracked in [../open-questions.md](../open-questions.md).
