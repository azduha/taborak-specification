# Data Model — Groups

`person_group` and `person_group_member`: named sets of people with dated members, a group as an item a
grant can be written on, and an honest ledger of what this page held before
[D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row) deleted
its subject.

**What is not on this page, and where it went.** `org_unit`, `org_unit_type`, `org_unit_type_rule`,
`org_unit_name`, `org_unit_relationship`, `unit_participation`, `scope_exposure`, the hierarchy traversal
and the position module are all deleted, not moved — §5 is the ledger, with what each took with it. The
unit itself has no table here, because it is a scope: `grant_scope_type` carries a code `unit` with
`is_item_scoped = false`, and there is exactly one of it. Membership of it is in
[03-membership.md](03-membership.md). Roles and `role_holder` are in
[05-authorization.md §3–§4](05-authorization.md#3-role--an-office).

Domain rationale: [../domain/04-organization-structure.md](../domain/04-organization-structure.md).

---

## 1. `person_group`

A group is a named set of people with a lifetime. It is not a body: no parent, no type, no code, no path,
no permissions of its own. The full argument for each absence is in
[../domain/04-organization-structure.md §2](../domain/04-organization-structure.md#2-what-a-group-is-and-everything-a-group-is-not),
and the absence table below is the same list stated as columns.

**Fields**

| Field | Kind | Notes |
|---|---|---|
| `id` | surrogate id | Internal only; never exposed. |
| `public_id` | uuid, required, generated | The identifier used outside the system, and unique. |
| `name` | text, required | The one the organization uses in speech and in an expression as `GROUP(name)`. Carries no identity — see the naming rules below. |
| `description` | text, optional | What the group is for, for whoever finds it in a list two years from now. |
| `valid_from` | date, required | When the group began. |
| `valid_to` | date, optional | NULL = open. An ended group is never deleted: its member rows still answer the historical question (§4). **Setting it is refused while a live grant, or a live audience reachable from one, names the group** (§3). |
| `created_at`, `created_by`, `updated_at`, `updated_by` | timestamp, audit time; reference to `person` | The standard audit columns. `created_by` is NULL for system jobs. |

**Rules**

- Where both ends of the period are set, `valid_to` is later than `valid_from`. Either end may be absent
  on `valid_to`, and no comparison is attempted when it is.
- **`name` is unique across `person_group`, `role` and `audience` together**, compared after folding case,
  whitespace and separators on write. Bare `COUNSELORS` resolves against roles and groups at once, since
  `ROLE()` and `GROUP()` no longer have to disambiguate, so one namespace is what makes an expression mean
  one thing
  ([D-101](../decisions/round-10b.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree));
  `audience.code` joined it when audiences became nameable operands, since a name that resolves two ways is
  a silent grant ([D-103](../decisions/round-10b.md#d-103--an-audience-may-name-another-audience)). Note
  the asymmetry: `audience.code` is optional and unique-where-set, so an unnamed audience is simply not
  composable, while a group's `name` is required — a group that cannot be named cannot be talked about
  either. **No constraint spans three tables, so the write path carries this rule** and integrity checks 3
  and 4 in [§6](#6-integrity-checks) cover both halves of it — the split D-081 requires, stated here rather
  than assumed.
- **Every `selector_type.code` is a reserved name.** A group called `MEMBERS` is refused when it is saved,
  not discovered later as an expression whose meaning moved
  ([D-101](../decisions/round-10b.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree)).
  The reserved list is read from the registry rather than duplicated, which is one of the jobs that makes
  `selector_type` real data and not a tidying.
- **There is no `import_batch_id` on either table in this document, and that is a fact rather than an
  omission.** The corpus names no groups ([D-092](../decisions/round-09.md#d-092--the-corpus-is-people-and-events-and-it-names-no-units))
  and the import owes no group rows
  ([D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)), so
  no row here can ever have been produced by the batch. A column that is always NULL, on the one table
  whose whole content is a human decision, would advertise a capability the module does not have.

**Columns a body would have had, and are not here.** Each is absent by a decision, not by omission, and
the list is worth keeping next to the table because "no special features" was the instruction:

| Not present | Gone with |
|---|---|
| `parent_group_id`, `path`, `depth`, any nesting rule | the hierarchy itself (D-097) |
| `group_type_id`, and any vocabulary of group kinds | `org_unit_type`, and D-054's argument about not guessing words |
| `code` | D-096's method says a label carries no identity, so a second label would only create a second way to be wrong (§1's naming rules) |
| `status` (`proposed`/`active`/`closed`), `closed_reason_code` | a group has a period. Two states, `valid_to` NULL or not, and no `status` that can disagree with it |
| `data_confidence` | the rows are typed by a person (§4); there is nothing uncertain about how they arrived |
| name history rows | `org_unit_name` is deleted and nothing replaces it — a rename edits `name` and the old name is gone |
| any split / merger / `successor_of` edge | `org_unit_relationship` is deleted, and D-098 refuses group-to-group edges outright |
| `join_reason_code`, `leave_reason_code`, `is_primary`, `role_in_unit` | the same list, on the member table (§2) |
| `allows_minors`, or any flag about who may belong | D-095, and nothing on a group replaces it ([../domain/04-organization-structure.md §3](../domain/04-organization-structure.md#3-joining-a-group-is-somebody-elses-act)) |
| `fee_*`, `dues_*` | membership at the unit is the only thing that costs money |
| any role, office or leadership column | D-098: the groups have no roles; D-100: positions are deleted |

**Naming, and the rule that a name does not carry.** A name that comes back after a decade is a **new
`person_group` row**, unless somebody records the continuity
([D-096](../decisions/round-09.md#d-096--a-reused-unit-number-is-a-new-unit-unless-someone-records-the-continuity),
whose subject was units and whose *method* — continuity is asserted, never matched — transfers intact).
The default is stated because an unstated one gets implemented by whoever writes the matching screen, and
that screen matches on name. **Where the assertion would be recorded is not decided**: the field it used
to live in (`org_unit_relationship.successor_of`) is deleted and no group table replaces it, so the
enforceable half of the rule is the default and the rest is prose. The domain page states the cost:
[../domain/04-organization-structure.md §4](../domain/04-organization-structure.md#4-a-name-carries-no-identity).
What *is* settled is that a rename is cheap and safe: a grant and an expression store **kind + id**, never
a name, so renaming a group never rewrites a grant (D-101).

**`person_group` is registered in `grant_scope_type`** — which is what makes a group an item, and is §3.

---

## 2. `person_group_member`

**The roster, as dated rows.** One row per person per membership period. Joining, leaving and coming back
are all periods on the same pair, which is what lets the roster answer a question about the past without
asking the audit trail — whose payloads expire after two years
([D-088](../decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short))
and which must not become the history of record for anything
([D-098](../decisions/round-10a.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority)).

**Fields**

| Field | Kind | Notes |
|---|---|---|
| `group_id` | reference to `person_group`, required | |
| `person_id` | reference to `person`, required | Never a membership, never a user account: a person ([D-009](../decisions/round-01a.md#d-009--unit-membership-links-to-person-not-to-membership)'s rule, transferred to the table that outlived `unit_participation`). |
| `valid_from` | date, required | The first day the person is in the group. |
| `valid_to` | date, optional | NULL = still in the group. The day the person is **no longer** in it, half-open — see the overlap rule. |
| `added_by` | reference to `person`, required | Who wrote it. Required, not optional: no row in this table is allowed to be unattributed, because the permission that writes it is the module's only safeguard (§4). |
| `note` | text, optional | Why, in the organization's words. Free text, deliberately — see below for what it is not. |
| `created_at`, `created_by`, `updated_at`, `updated_by` | timestamp, audit time; reference to `person` | The standard audit columns. |

**Rules**

- Where both ends of the period are set, `valid_to` is later than `valid_from`.
- **No two rows for the same (`group_id`, `person_id`) may cover the same date.** The rule counts
  **every** row, open and closed alike — there is no status to scope it by, and scoping it to the open
  rows would be a different and weaker rule. Periods are **half-open**, so a row ending on a day and a row
  beginning on that same day do not collide ([D-002](../decisions/round-01a.md#d-002--everything-temporal-is-a-period-never-a-boolean)).
  Consequences, both wanted: a person who left in 2020 and returned in 2024 is **two rows**, and a
  hand-edited single row that hides the gap is refused by the shape of the data rather than by a rule
  nobody remembered to write.
- **A person may be in any number of groups at the same time.** No cross-group rule of any kind, and no
  `is_primary` deciding which roster to show first.
- **`group_id` and `person_id` are never edited on an existing row.** Close the row and open a new one
  (§4).
- **A member row whose period lies outside its group's period is reported, not refused.** The two periods
  are two facts and D-098 keeps both without ruling that one contains the other, so containment is
  assumed here and nowhere decided. **Status:** assumption — see integrity check 2, and
  [§8](#8-open-issues).

**Who enforces the overlap rule now.** [D-081](../decisions/round-06.md#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now)
does not let a rule keep a mechanism it no longer has, so the answer is specific. **The migration layer**,
by the standing rule of [00-conventions.md §6a](00-conventions.md#6a-who-enforces-an-invariant-now): a
correctness property of the data belongs in the database, *even when the ORM cannot generate it and the
migration must be written by hand*. Application validation still belongs on the write path, because it
produces the error message a volunteer can read — but it is a usability feature and not the invariant.
Underneath, integrity check 1 is the nightly net.

**And this is F-10 shape 1, which is the problem.** The overlap invariant needs an exclusion constraint
over a range built from two columns; no ORM emits one
([F-10](../open-questions.md#f-10--which-invariants-the-orm-cannot-express-and-who-writes-those)), and F-10
is still **open** — nobody has ruled per shape which layer writes these. Three specific traps on the way
to writing this one by hand:

- **Shape 1 is described in F-10 as "no two *open* rows overlap", and this rule is not that rule.** Copying
  the shape as worded — a constraint scoped to rows with no `valid_to` — would permit a closed row and an
  open row for the same person and group to overlap, which is exactly the pair that makes "who was in this
  group in 2019?" have two answers. It is the same mistake §6a warns about from the other side: a
  conditioned constraint over unconditioned columns is a different rule. This one must be written over all
  rows.
- **`valid_to` is NULL for an open row, and the corpus refuses a sentinel date**
  ([03-membership.md §3](03-membership.md#why-valid_to-is-null-and-not-a-sentinel)), so the range cannot be
  built from the columns as they stand; it has to be built from an expression that supplies an upper
  bound. That is a second reason a generated schema will not have this constraint, and the reason the
  hand-written version is the deliverable rather than the annotation.
- **Half-open is part of the rule, not an implementation detail.** A closed-open range (`[from, to)`) makes
  a leaving day and a joining day coexist, which is what §4's transfer relies on. An inclusive range
  refuses every transfer that happens on a single day and would be quietly loosened by whoever hits it.

Until that migration exists, this is **a convention, not a guard** — the phrase
[00-conventions.md §6a](00-conventions.md#6a-who-enforces-an-invariant-now) reserves for exactly this case.
It is stated here rather than softened because the alternative is a document that implies a database
refuses overlapping rows when nothing yet does.

---

## 3. A group is an item: a grant can be written on one

**`person_group` has a row in `grant_scope_type`, so a group is a thing a grant may be written on** — which
is how "these two people may work this group's roster" is said without inventing a scope
([D-098](../decisions/round-10a.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority)).
The scope types now are `unit` (not item-scoped, the organization itself), `event`, `person_group`, `role`,
and `document` (deferred). `role` joins as an item for the same reason and by the same move
([D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)).

| Shape of grant on a group | Reaches | Written by |
|---|---|---|
| at the unit, `person_group.member.manage` | **every** group, existing and future — nothing stands between a unit-scope grant and an item after D-097 | `access_grant.create` at the unit |
| on one group, `person_group.member.manage` | that roster only | a holder of the code at the unit, or of a grant on that group |
| either of the above, `effect = deny` | defeats every allow that applies to that person, including ones written elsewhere, later, or by somebody else | the same — denies are legal at the unit and on an item (D-099) |

**`person_group.member.manage` is therefore `applies_to = unit_and_item`** on the `permission` row
([D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)):
the two arms above are what that value is *for*. There is no self-scoped variant and none will be added —
nobody writes themselves onto a roster
([D-095](../decisions/round-09.md#d-095--units-carry-no-restrictions-joining-one-is-somebody-elses-act),
transferred intact in D-098).

**The same group is also a leaf in an expression.** `GROUP(name)` names this table's set, and the set is
the member rows live on the date being checked
([D-101](../decisions/round-10b.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree);
storage of the expression tree is not this page's subject). Three consequences worth stating next to the
table they touch:

- **Membership confers nothing.** The group is a set; a set is not a grant, and reaching a person through
  `GROUP(x)` happens only because some grant's expression says so
  ([D-005](../decisions/round-01a.md#d-005--permissions-are-grants-never-derived-from-identity)).
- **An operand that does not resolve is the empty set.** A deleted group id, an orphaned argument, a
  broken expression: it reaches nobody, and the answer is denial. Fail closed in every direction, as the
  resolver's rules already require. `GROUP(nonexistent)` is not an error at check time and must never
  become a permissive default.
- **The polymorphic id has no foreign key**, exactly as `access_grant.scope_id` accepted it
  ([D-011](../decisions/round-01a.md#d-011--scope_id-on-access_grant-is-polymorphic-with-no-foreign-key)),
  and the compensating orphan check is specified once in
  [05-authorization.md §11](05-authorization.md#11-invariants-to-verify). This page does not re-state it.

**Ending a group is refused at save while something live names it, and the reason is the subtraction, not
the grant.** [D-103](../decisions/round-10b.md#d-103--an-audience-may-name-another-audience) rules it for
audiences — an audience may not be ended or deleted while a live grant, or a live audience reachable from a
live grant, names it — and extends the same refusal to `person_group` in the round after, on identical
reasoning. The reverse lookup is the audience arm's own query, one index: `audience_operand` rows whose
`selector_kind = 'GROUP'`, together with the grants whose scope is the group. **Why a refusal, and not the
report this page first wrote:** an empty set is not neutral. A grant that merely has an ended group as its
*scope* reaches nobody and is dead weight on the allow side, of the kind D-099 already reports for denies
that deny nothing; named **inside an expression** the same emptiness points the other way, because
`EVERYONE - GROUP(x)` with an empty `GROUP(x)` denies *everybody*. One field set on one group's row would
then silently widen a deny that somebody else wrote, inside a grant the person who ended the group may never
open. **The refusal has two arms and the second is the one people forget, because it is not about ending
anything:** saving a *new* grant whose expression contains `GROUP(x)` for a group that is already ended is
refused by the same rule, since the writer is pointing a live grant at an empty set, and `EVERYONE - GROUP(x)`
is the same mistake arriving from the other end. A rule written only around the end-date field would leave
that grant savable and this page's own report populated with something that looked allowed. The write path
refuses both saves and integrity check 5 in [§6](#6-integrity-checks) is the net beneath it — the split D-081
asks for, since a refusal that no code implements enforces nothing.

**`ROLE(x)` needs no equivalent rule, and the difference is the shape of the set, not the idea of naming
one.** An office cannot be emptied quietly: there is no `role.retire`, no status column, and deleting a role
is already refused while holder rows exist, so ending an office means ending `role_holder` rows one at a time,
on a screen that shows each person. A group has a lifetime, and `valid_to` is one field that empties a set in
one save. That is why the refusal names groups and audiences and not roles
([D-103](../decisions/round-10b.md#d-103--an-audience-may-name-another-audience), whose own exception row
states the point: the hazard is a property of the shape).

**A group's set is stable across items, and that is worth one sentence of contrast.** `GROUP(x)` means the
same people whoever is being checked, so the grant editor's expansion of a group grant is per grant; the
operands that bind to the item (`PLACED`, `ORGANIZERS`, …) mean different people on different events and
must be previewed per item
([D-102](../decisions/round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)).
The presence operand is not among them: `PRESENT(<event>)` over `was_present` is **refused**, because a
column that is NULL until somebody takes a register would revoke a child's access to their own photos
because a volunteer forgot a tick box.

**A deny that matches no live allow is dead weight and is reported** — the check is specified in
[05-authorization.md §11](05-authorization.md#11-invariants-to-verify) and applies to group-scope denies as
to any other, because a deny that denies nothing is how a stale restriction survives its reason (D-099).

---

## 4. Joins, leaves and transfers: close one row, open another

**Every change to a roster is a period ending and a period beginning. Nothing on a member row is edited to
move a person anywhere.** The discipline is `03-membership.md` §5.2's, retargeted at groups and otherwise
unchanged, and it carries the same design rule the deleted participation section carried:

> **Never rewrite a member row to point at a different person or a different group.** Close it and open a
> new one. Rewriting destroys the answer to "where was this child in 2003?" — and unlike most tempting
> edits, this one leaves no bad row behind, only a history that quietly stopped being true.

| Change | The write | Rows afterwards |
|---|---|---|
| Someone joins | insert one row, `valid_from` = the day, `added_by` = the writer | 1 |
| Someone leaves | set `valid_to` on the open row — **the only in-place edit this table permits**, and only on the row that is open | 1 |
| They come back later | insert a **second** row. Never reopen the first, never extend it | 2 |
| They move from group A to group B on 1 June | close A's row with `valid_to` = 1 June, open B's row with `valid_from` = 1 June | 2, one in each group |
| A group splits in two | create the two groups, insert member rows for whoever is in each, move whatever grants name the old one, and **only then** end it — `valid_to` is refused while a live grant or expression names the group (§3). **No edge connects them** — see §1's absence table | old group closed, two open |
| A name comes back years later | a **new** `person_group` row (§1) | 2 groups, same name, no relation |

**Half-open is what makes the transfer row land on one day.** A row ending on 1 June and a row beginning
on 1 June do not overlap, so a handover has no gap and no double-count, and no one has to invent a
midnight.

**A row is written by a person, and that is the whole of how the roster gets populated.** The import owes
no member rows and nothing is inferred from attendance, from an event, or from a unit that no longer
exists ([D-092](../decisions/round-09.md#d-092--the-corpus-is-people-and-events-and-it-names-no-units),
[D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)). The gate
is `person_group.member.manage`, at the unit or on one group (§3), the write is audited, and the row names
who wrote it — which is D-095's answer to *do not place a child where nobody is responsible for them*,
retold with the table changed and the reasoning untouched
([D-081](../decisions/round-06.md#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now)).

**Two things the deleted table could say that this one cannot, on purpose.** No `join_reason_code` /
`leave_reason_code` — so no `transfer`, `promotion`, `reorganisation`, `unit_closed` vocabulary to
maintain, get wrong, or pretend is a safeguard (the eighteen-ticks-without-a-receipt shape D-095 removed).
No `role_in_unit` display label, because a label like that always becomes an authorization check the
moment somebody asks "can she edit the roster?". The `note` column is where any of that reasoning goes, as
prose, unread by the resolver
([D-098](../decisions/round-10a.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority)).

**There used to be a second dated set of people beside this one, and the argument for keeping them apart is
worth keeping even though one of them is gone.** `audience_member` held the names somebody typed into one
audience; it was the same shape D-080 teaches a reader to distrust, and this page argued at length that the
two must never be merged, because **merging them would make the permission table the system's roster**.
[D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)
deleted that table and its `LIST` operand — a hand-named person is now a `PERSON(x)` leaf inside the
expression itself — so **the duplication is gone rather than reconciled**, and one of the two tables D-080
would have flagged no longer exists to be flagged.

**What did not go is the hazard, and it is the reason this paragraph survives its subject.** The temptation
when a grant needs one more person is to add that person to a group, because a group is the thing with a
roster editor. That is still refused, and for the same reason
[D-098](../decisions/round-10a.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority)
gave: **a group's rows are true when no grant points at them**, so editing one to move one grant's reach
edits a roster that other grants read, and it invents a group nobody talks about. Since D-105 the refusal has
a clean alternative next to it instead of a competing table: write `PERSON(honza)` in the expression that
needed him, where it is visible, dated by the grant that carries it, and meaningless outside it
([D-101](../decisions/round-10b.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree)).

---

## 5. What this page held before round 10

**The ledger, so that a reader who arrives from an old link or an old report knows what happened.** Every
row is a deletion, not a move, unless the last column says otherwise.

| Deleted | With it goes | Who enforces the surviving rule now |
|---|---|---|
| `org_unit` | the root row, the single-root conditional uniqueness, `path`, `depth`, `status`, `code`, `data_confidence`, the closed-without-end-date check | nothing enforces "there is one unit" — there is no row to violate it with. That is the replacement, not a gap |
| `org_unit_type`, `org_unit_type_rule` | the runtime vocabulary, `is_leaf`, `max_depth`, the seven-step ordered nesting check, `allows_minors`' last context | no nesting to check. *Do not place a child where nobody is responsible* is `person_group.member.manage` (§4) |
| `org_unit_name` | rename and renumber history, `change_reason`, the denormalised `org_unit.name` and the write rule that paired them | nothing. A group rename edits one column and the previous name is gone (§1) |
| `org_unit_relationship` | `split_from`, `merged_into`, `successor_of`, `renamed_to`, and D-096's only home | nobody. A split is an ended group and two begun groups, with no edge (§4); where a claimed continuity goes is undecided (§8) |
| `unit_participation` | sub-unit rosters, the root participation row every membership owed, `is_primary`, `role_in_unit`, the reason codes, and the transfers between units | `person_group_member` (§2) is the roster; the membership row in [03-membership.md](03-membership.md#5-unit_participation--deleted-by-d-097) is the membership. **Moved, not deleted** — the only row in this table that is |
| `scope_exposure`, `scope.expose`, `scope.exposure.review` | the only downward crossing, the direction-of-authority check, and the nightly alert that was its sole detector | nobody. There is no "outside it" to be stopped from (D-097); what D-031's reasoning still supports is carried by deny-is-absolute and by the ownership and guardianship channels |
| `unit_ancestors()`, `unit_descendants()`, the materialized path | the recursive walk, the path-consistency check, and the CI assertion that the resolver never calls the function | nothing, and an assertion about a function that does not exist is not a guard |
| the reparenting guard on `parent_unit_id` | **F-10 shape 4, and with it the whole class** — see below | nothing, because there is nothing to guard |
| `position`, `position_assignment` | `is_leadership`, `max_holders`, `min_age`, `requires_membership`, `appointment_reference`, the holder-count check, and the appointment workflows (D-100) | `role_holder` in [05-authorization.md §4](05-authorization.md#4-role_holder--who-holds-an-office); the membership test is an operand, not a resolver clause; the last stored eligibility rule in this module is gone, so eligibility is capability and age is nobody's check (D-060) |

**Shape 4 has no instance, and the sentence is worth its weight.**
[F-10](../open-questions.md#f-10--which-invariants-the-orm-cannot-express-and-who-writes-those) shape 4 —
a column that may not change once set — is the only shape in that list with **no report at all**, because
a violation leaves every row individually valid and satisfies every constraint; nothing can be compared
afterwards, so the guard in the write path is the entire enforcement and the test that attempts the update
is the only remaining evidence it was meant to stay. Its one instance in the whole design was
`org_unit.parent_unit_id`. **It has none now.** Two consequences, in both directions: this document no
longer contains a rule that nothing can enforce, which is a real gain nobody counted (D-097 calls it the
one thing that got easier); and F-10 loses its sharpest example, so the question stays open on the
strength of shapes 1–3 alone — of which shape 1 has a fresh occupant, §2.

**Checks 1–10 of the old §9, and where each went.** The numbering restarts in [§6](#6-integrity-checks)
because almost none of them has a subject:

| Old check | Fate |
|---|---|
| 1 stored path vs. actual tree | dead — no path, no tree |
| 2 live unit under a closed parent | dead — no nesting |
| 3 live unit with no current name row | dead — no name table, no denormalised copy |
| 4 `org_unit.name` disagreeing with the open name row | dead — same reason. This pair was "the one to read every morning"; there is nothing left to drift |
| 5 a live unit type with no nesting rules | dead — no types |
| 6 a position assignment pairing a position with a unit of another type | dead — positions are deleted (D-100) |
| 7 a unit with exactly one live child | dead — no children |
| 9 a position holding more people than its own limit | dead with `max_holders`. Note what this retires: it was the report that was supposed to be the second half of F-10 shape 3's remedy, and the document's own sharpest admission of a rule that might not be enforced at all |
| 10 the single-root constraint really exists in the schema | dead with the constraint — the check whose peculiar job was asserting that a **migration had emitted a guarantee** rather than that any row was clean |

*(There was no old check 8; the numbering had a hole in it from an earlier round. The list below is
numbered from 1 and is contiguous, which is the point of this note.)*

**Check 10's pattern survives even though check 10 does not.** A CI assertion that a guarantee exists,
rather than that the data looks fine, has a new occupant: names unique across `person_group` and `role`
cannot be carried by any constraint, so the write path carries them and something has to assert that the
write path still does (D-081's rule, D-101's requirement). That is check 4 below.

---

## 6. Integrity checks

**Invariants to verify**

1. **Two member rows for the same person and group covering the same date** (§2). Counts overlapping pairs
   over **all** rows, half-open, so it agrees with the constraint it is the net beneath. §2 names the
   migration as the enforcing layer; this report is what notices if that migration was never written,
   which — F-10 being unanswered — is the state of things today.
2. **A member row lying outside its group's own period** (§2). A list to read rather than a breach: the two
   periods are two facts and containment is assumed here, not ruled
   (**Status:** assumption — [§8](#8-open-issues)). A large count means people are editing old rows
   instead of opening new ones.
3. **A group name that collides** — with another group, with a role, with a set `audience.code`, or with a
   reserved `selector_type.code` (§1). Reports the collisions the write path should have refused; a non-zero
   count means a path exists that bypasses it, which in a system with an import, a data fix and a second
   client is a question of when.
4. **The cross-table name rule is still carried by the write path** (§1). Not a data report: an automated
   test that attempts to save a duplicate name, and a second that attempts `MEMBERS`, and expects both
   refusals. No constraint can hold this rule, so if the code loses it, nothing else notices — the same
   job the retired check 10 did for the single-root constraint, and the reason it is numbered here rather
   than left to the test suite's own memory.
5. **A live grant whose scope is a group that has ended, or a live expression with a `GROUP(x)` leaf on one.**
   **The same number, and a different kind of check: this one used to watch a rule nobody had made and now
   watches one that has been made.**
   [D-103](../decisions/round-10b.md#d-103--an-audience-may-name-another-audience) refuses the end date at
   save while a live grant, or a live audience reachable from a live grant, names the group; §3 states the
   rule, the query behind it, and why an empty operand on the `-` side is dangerous rather than merely inert.
   What the report still earns is D-081's half of the arrangement — the refusal is application code, and
   application code loses things. **Two causes put a row on this list and both are now regressions:** either
   the write path stopped refusing the end, which means fixing the code and then the rows; or the grant was
   written *onto* a group that was already ended — a direction the rule needed saying twice, because a
   constraint on *ending* alone would leave this report full of behaviour that looked permitted
   ([D-103](../decisions/round-10b.md#d-103--an-audience-may-name-another-audience) refuses both). That
   second cause is why the question about hiding ended groups from pickers (§8) is not cosmetic. Read the leaves sitting inside a subtraction first: `EVERYONE - GROUP(ended)` denies
   everybody, where the same ended group as a plain scope denies nobody.
6. **An open group with no open member rows for a long period.** A data-quality list in the family the old
   check 7 was: often legitimate (a project group between seasons), sometimes a group that ended and nobody
   set `valid_to`. Nothing should reject it; somebody should be able to see it.

**Checks 1 and 4 fail on different things and must not be read alike.** Check 1 finds bad rows; check 4
finds a missing guarantee while every row is still clean. Only check 4 belongs in CI.

**What this section no longer contains, and why that is not an oversight:** path consistency, nesting
legality, name denormalisation drift, holder-limit overrun and the single-root constraint assertion — the
five subjects are gone, and §5 says which decision took each.

---

## 7. Seed data

**No group is seeded, and that is the decision rather than a gap.** The seed ships zero `person_group`
rows. The corpus names no groups, so there is nothing to import and nothing to infer
([D-092](../decisions/round-09.md#d-092--the-corpus-is-people-and-events-and-it-names-no-units)); a
seeded group would be an invented one, which is the exact error D-054 recorded about the unit vocabulary —
*a wrong vocabulary in seed data is harder to dislodge than an absent one*. Groups are **runtime data**,
exactly as `role` is ([D-052](../decisions/round-04.md#d-052--roles-are-runtime-data-the-seed-set-is-not-a-specification)):
the organization creates them, names them in its own words, and ends them.

**The one set people expect to find here is a role, and it is not on this page.** `counselors` ships as a
**role** with `is_system` so an editor refuses to delete it
([D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)):
a permanent, organization-wide population is the opposite of what a group is. The seeded grant
`event.answer.view` on an event to `ORGANIZERS` is likewise not here (§3 explains why a group is an item;
[D-102](../decisions/round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)
owns that row).

**What the old seed said, for the record.** Two rows and nothing else: one unit type for the organization
itself, and the single root unit carrying it. **Neither exists.** There is no root row to create and no
type to give it; the unit arrives as a code in `grant_scope_type`, which is a lookup row in the
authorization module and not data this page seeds. The old §10's long note about the root type's
`allows_minors = false` asserting the opposite of what the membership flow does — the correction D-095 made
by deleting the column — is retired with the column, and the paragraph's real lesson survives where it was
written: a seed that contradicts the runtime behaviour is worse than no seed.

---

## 8. Open issues

- **Where a claimed group continuity is recorded.** §1 states the default (a returning name is a new
  group) and D-096's method says the continuity is asserted, never matched — but the table that accepted
  the assertion is deleted and D-098 refuses group-to-group edges. Tracked in
  [../open-questions.md](../open-questions.md).
- **Whether a member row must lie inside its group's period.** Assumed in §2, reported in §6 check 2, and
  nowhere ruled. A one-sentence decision either way; left open rather than decided by a document.
- **Which layer writes the no-overlap constraint.** That is **F-10**, still open, and §2 spells out the
  three ways this particular instance of shape 1 gets written wrong if nobody answers it
  ([../open-questions.md](../open-questions.md#f-10--which-invariants-the-orm-cannot-express-and-who-writes-those)).
- **Whether an ended group is hidden from pickers, and whether it may be reopened.** Closed units had a
  stated behaviour; `person_group` has a period and no rule about which screens read it. Reopening an ended
  group by clearing `valid_to` would also collide with §1's rule that a returning name is a new group, so
  the two questions are one question.

**Resolved and no longer open**, kept visible so the reasoning survives: the sub-unit vocabulary and the
nesting rules (there is no structure — D-097, closing the question D-054 had left open); retroactive
reparenting (the dimension is gone, so the question cannot be asked, let alone answered — D-036);
organization-wide operational roles (the unit is the only scope, so there is no "wider" to be
organization-wide against); whether the unit may read into what these docs used to call its sub-units
(**moot** after D-097 — the question presumed two scopes and there is one, and it used to be this page's
largest open item); whether `allows_minors` should also constrain positions (both columns are deleted —
D-095, D-100); whether `is_leadership` should create a role assignment (positions are deleted, and a role
now confers nothing at all — D-100); background checks (none are recorded — D-043); whether a group may be
ended while a live grant, or a live audience reachable from one, names it (**refused at save** — D-103 wrote
its audience row first and extended it to `person_group` in the round after, on the `-`-widens reasoning;
§3 and §6 check 5); whether a `PERSON` selector should exist so that D-100's one-person exemption is
writable (it is one of the **fourteen** seeded rows — thirteen until
[D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)
removed `LIST`, twelve until [D-107](../decisions/round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded) added `OLDER` and `YOUNGER` — and it arrived late by
[D-101](../decisions/round-10b.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree)'s
amendment, because the registry had been copied from the evaluator's arm list and lost the arm, which
[D-104](../decisions/round-10b.md#d-104--a-permission-codes-last-segment-is-an-action-and-a-registry-that-prose-contradicts-is-a-fiction)
is the answer to); and whether a hand-typed set of people needs a table of its own (**no** — D-105 deleted
`audience_member`, and the round that added `PERSON(x)` had already removed the only reason it had for
existing).

All tracked in [../open-questions.md](../open-questions.md).
