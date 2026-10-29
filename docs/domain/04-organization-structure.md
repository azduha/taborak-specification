# Groups

One organization, and the named sets of people inside it.

**The vocabulary, first, because everything here leans on it.**

| Word | Means | Stored as |
|---|---|---|
| **unit** | the organization itself. There is exactly one. It is a **scope**, never a row | nothing — a code in `grant_scope_type` |
| **group** | a named set of people with explicitly dated members and a lifetime. A set, not a body | `person_group` + `person_group_member` |
| **role** | an office: a small, visible set of holders — leaders, finance, IT | `role` + `role_holder` |
| **audience** | an expression over named sets, which a grant is aimed at | `audience` |
| **selector** | one operand of that expression: `MEMBERS`, `GROUP(x)`, `ROLE(x)`, … | `selector_type`, `audience_operand` |

Roles and audiences belong to the authorization model
([06-authorization-model.md](06-authorization-model.md), [../data-model/05-authorization.md](../data-model/05-authorization.md))
and are not re-specified here. This page owns the unit and the group.

---

## 1. The organization is one unit, and the unit is a scope

**There is one unit and it is the organization.** It has no parent, no children, no type, no code, no
path, no depth, and no row. It is the non-item scope that `grant_scope_type` already carries — code
`unit`, `is_item_scoped = false` — and a grant written at it has no `scope_id`. Nothing in the schema
represents it, because there is nothing to represent: a second unit cannot appear, for the same reason a
second answer to a question cannot appear in a field that does not exist.

**Membership is unchanged and is not a group.** One membership per person, at the unit, paid for yearly:

- **"everyone in the organization"** is one query against `membership`;
- **"everyone in the Thursday group"** is one query against `person_group_member`.

Two shapes, and neither one borrows the other's table. Renewal opens a new `membership` row rather than
extending the old one
([D-016](../decisions/round-01b.md#d-016--renewal-opens-a-new-membership-row-not-an-extended-valid_to)).

**A grant at the unit reaches everything** — every item of every type — because nothing stands between
the unit and an item and there is no ownership relation to test. That is a sentence about the permission
system; it is stated here only because it is what "scope" means now that "row" does not.

Why the design carries no hierarchy: the legacy corpus names no units at all — two exports, people with
their membership period and events with attendance, no unit column anywhere
([D-092](../decisions/round-09.md#d-092--the-corpus-is-people-and-events-and-it-names-no-units)) — and a
structure that describes nothing imported and restricts nothing carries no information
([D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)).

### What that costs, said once

These are properties the hierarchy was carrying, listed here rather than distributed through the page.
They are not argued away.

1. **The unit is not a locus of accountability for a child's records.** This is the one that matters.
   **Nothing in the model reproduces "access to a body's children was granted by that body"** — by the
   people who know them, who recruited its leader, and who can be asked. With one unit there is no
   "outside it" to be stopped from, so the rule has no subject rather than a weaker form. A permission
   held at the unit reaches every member, and `person.view` is the widest read permission in the system
   ([D-083](../decisions/round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data),
   [D-086](../decisions/round-07-08.md#d-086--a-sensitivity-mark-grades-what-a-grant-exposes-not-the-table-it-reads)).
   What stands between a child and a stranger's read is a permission held by a named adult, an audit
   trail whose payloads expire after two years
   ([D-088](../decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)),
   and a report of who holds the write.
2. **There is no subtree question.** "Who was in the Thursday group in 2011?" stays answerable, because
   group member rows are dated (§5). "And everything nested under it" has no subject: a set of people has
   no sub-sets stored inside it.
3. **Restructuring is not a recorded event.** A group that splits is an old group that ended and two that
   began, with no edge between them — and no table where such an edge could go (§4).
4. **Unit-scoped reports have nothing to report on.** "A pack's roster", "a pack's events", "which units
   exist" are not hard questions, they are questions with no subject. The organizational-year reports that
   matter — membership and fees — live at the unit and are untouched.

**One invariant class lost its only named instance here:** shape 4 of
[the invariant register](../data-model/00a-invariant-register.md#4-a-value-that-may-never-change-once-set) —
a column that may not change once set, whose violation leaves every row individually valid — and
`parent_unit_id` was the only member anybody had pointed at. **Empty and unnamed are two different claims**,
and [D-131](../decisions/round-18.md#d-131--shape-4-is-not-empty-and-a-code-that-is-referenced-may-not-be-renamed)
found the shape has six members: this deletion removed one of them, not the class.

**It is not a two-way door.** This is the deletion of a dimension, not a flag. Adding structure back is a
decision with a reason attached — most plausibly "the organization has outgrown one center's visibility" —
and it would have to argue the accountability rule from its own premises, because the mechanism that made
it work — a scope written by the body it covered — does not exist.

---

## 2. What a group is, and everything a group is not

**A group is a `person_group`: a name, a description, its own lifetime, and explicitly dated members.**
It is a **set of people, not a body**. Somebody names it, somebody puts people in it, somebody ends it, and
the record of who was in it when is the roster's own (§5). A weekly meeting group, a project crew, a
trainers' pool, `schuzka2026-1` — all the same kind of thing, and the system has no opinion about which
ones deserve to exist. A person may be on several rosters at once; none of them is marked as the one to
show first.

**Everything a body would have had, a group does not have.**

| A group has | Because |
|---|---|
| no parent and no children | there are no sub-units, and groups do not nest |
| no type, and no vocabulary of types | a group needs no word for what kind of set it is |
| no `code`, no path, no depth | a label carries no identity (§4); a set has no position to sit at |
| no nesting rules | there is nothing to nest |
| no rename history | the name is a column, and the old name is not kept (§4) |
| no split, merger or succession edge | restructuring is not an event (§1, cost 3) |
| no leadership of its own | see §6 |
| **no roles** | an office is a role and a role is held at the unit; a group has none of its own, and no leadership column will be added to make one look derivable |
| no fee | membership is at the unit and is the only thing that costs money |
| **no permissions over its members** | see immediately below |

**Membership of a group confers nothing, and tidier storage does not quietly change that.** A member of a
group cannot do anything: participation is not authority, and it stays not-authority when it moves into a
table with better columns. Authority arrives only through a grant that names the group, which is §4 of
[../data-model/02-organization.md](../data-model/02-organization.md#3-a-group-is-an-item-a-grant-can-be-written-on-one).

**Where the line against an audience is drawn — the two are one row apart in shape and a mile apart in
meaning: a group states its members, a selector picks them.** A group's members are a list of people that
is true whether or not any permission points at it. A leaf in an audience — a `PERSON(y)` row
([D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)) —
is an addition to an expression, meaningful only inside the expression it completes. A group exists to be
talked about; a selector exists to be aimed at something. Merging them would make the permission table the
system's roster.

**Where the line against a role is drawn, in one sentence, because it decides who may edit the list.** A
role is an office with a small, visible set of holders and is written by the most sensitive code family in
the catalog (`role.*`, 🔒🔒); a group is company, and its roster is written by `person_group.member.manage`
(⚠). One table with a `kind` column would give a single permission that both adds a child to the Thursday
group and puts the holder among the administrators
([D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)).
`GROUP(x)` and `ROLE(x)` stay distinct in the grant text so the distinction is visible to whoever reads
the grant.

---

## 3. Joining a group is somebody else's act

**Nobody writes themselves onto a roster.** The gate is `person_group.member.manage`, held at the unit —
which reaches every group, because nothing stands between a unit-scope grant and an item — or granted on
one group as an item, which is how "these two people may work *this* roster" is said without inventing a
scope
([D-098](../decisions/round-10a.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority),
[D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)).
There is no self-scoped variant and none will be added.

**Who enforces "do not place a child where nobody is responsible for them":** whoever may write the member
row in `person_group_member`, audited and naming who wrote it. A permission refuses every write by the
wrong person regardless of the child's age
([D-081](../decisions/round-06.md#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now)).

**What that costs.** The system cannot say which groups are for children. Nothing on a `person_group`
answers that question and, consistent with "no special features", nothing will: no `allows_minors`, no
`is_children`, no type to hang it on. Combined with no recorded background checks
([D-043](../decisions/round-02-03.md#d-043--no-background-checks-are-recorded-in-this-system)) and with
cost 1 above, the safeguarding story of this module is a permission held by named adults, an audit trail
that forgets values after two years, and a report. If that turns out to be too little — after an incident,
or an insurer's question — the route back is a rule about who may be placed where, argued once as a
decision with its enforcement layer named in D-081's terms, and **not** a resurrected column whose name
implies it enforces something.

**A membership request is a request for membership of the unit, and carries no group.** There is no
`requested_unit_id` on a request: which group a new member lands in is a write on the group, not a
preference on the request. The request flow in [05-membership-lifecycle.md](05-membership-lifecycle.md)
ends at the unit; a roster is somebody else's decision afterwards.

---

## 4. A name carries no identity

**A group name is a label, and a label is not the group: a group name that comes back after a decade is a
new group, unless somebody records that it is not.**

Why the default matters: continuity is not a property of a label, it is a claim about the world, and only a
human knows whether the crew refounded in 2026 *is* the crew of 2016. Left unstated, the question is
answered anyway — by whoever writes the matching screen, who will match on name and let a thirty-year gap
sit inside one group's life. So the default points at **a new `person_group` row**. A rename is an edit to
one column and the previous name is not kept (§2).

**The continuity claim has nowhere to live.** Groups keep no group-to-group edges — no split, no merger, no
succession — so an assertion of continuity has **no field to hold it**
([D-098](../decisions/round-10a.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority)).
What the method guarantees is therefore the direction of the default, which is the half that was ever
enforceable: a returning name is a new group, and two groups that are really one look like two unless a
person writes that down somewhere. *Where that sentence goes is not decided.* The cheapest true answer
available today is a `note` on the second group's member rows and on the group's `description`, which
nothing reads and nothing links; the honest alternative is to accept that the organization's memory of its
own continuity is prose.
**Status:** assumption — this page does not choose, and the question is recorded in
[../open-questions.md](../open-questions.md).

**Names are one namespace with roles and audiences.** Because `ROLE(x)` and `GROUP(x)` do not have to
disambiguate, a bare `COUNSELORS` resolves against roles and groups together, so names are unique across the
tables, case/whitespace/separators are folded on write, and **every `selector_type.code` is a reserved
name** — a group called `MEMBERS` is refused at the save rather than silently rewriting every expression in
the system
([D-101](../decisions/round-10b.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree)).
`audience.code` is in the namespace too
([D-103](../decisions/round-10b.md#d-103--an-audience-may-name-another-audience)), and the pair of rules is
worth holding apart: **a bare name never resolves to an audience** — the arm must be written
`AUDIENCE(veterans)` — yet a group still may not *borrow* an audience's code, because a name that resolves
two ways is a silent grant whatever the resolution rules say. No single constraint spans the three tables,
so the write path carries the rule and an integrity check asserts that it does. What a grant stores is kind
+ id, never a name, so **renaming a group never rewrites a grant**. Mechanics:
[../data-model/02-organization.md §1](../data-model/02-organization.md#1-person_group).

---

## 5. A roster is history

**Member rows are dated, and that is what makes the roster answerable.** `person_group_member` carries
`valid_from` and `valid_to` per person, so joining, leaving and coming back are all periods on the same
pair, and the roster has a history of its own instead of borrowing the audit trail's. "Who was in
`schuzka2026-1` on 14 March 2026?" is a point-in-time read over those rows. It survives the audit trail's
24-month payload expiry
([D-088](../decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short))
because it does not depend on the trail — which is the entire reason the rows are dated rather than a live
flag, and the reason a naming habit like `schuzka2026-1` is a habit an organization may or may not keep
rather than the mechanism history rests on.

**This is where a group is ahead of the operand that looks most like it.** An audience named as an operand
evaluates live, so its past shape survives only in the audit trail and stops surviving when the payloads
expire; a group's set is its dated rows, so it keeps a past the audit trail cannot take away. "Who could
see this child's data in 2024?" is answerable when the grant pointed at a group and is not answerable when
it pointed at a nested audience
([D-103](../decisions/round-10b.md#d-103--an-audience-may-name-another-audience)). That asymmetry is a fact
about which of the two is a roster, and it is the strongest reason the pair stays two tables.

**Two facts, both kept, and not to be conflated.** The group's `valid_from`/`valid_to` says the group
existed over that span; the member rows' periods say who was in it. An open group with dated members
answers the historical question perfectly well, and an ended group's rows are not tidied up. **Ending the
group is not an edit anyone makes on their own:** setting that end date is refused while a live grant, or a
live audience reachable from one, names the group, because an empty set inside a subtraction widens a deny
that the person ending the group did not write and would not look at again (the write path and the checks
that watch it are
[../data-model/02-organization.md §3](../data-model/02-organization.md#3-a-group-is-an-item-a-grant-can-be-written-on-one)).

**A person who left in 2020 and came back in 2024 is two rows**, never one row edited in place, because the
edit destroys the answer to "was she in the group in 2019?"
([D-016](../decisions/round-01b.md#d-016--renewal-opens-a-new-membership-row-not-an-extended-valid_to),
[D-002](../decisions/round-01a.md#d-002--everything-temporal-is-a-period-never-a-boolean)).

**Moving from one group to another closes one row and opens another: never rewrite a member row to point at
a different group.** Rewriting destroys "where was this child in 2003?", and unlike most tempting edits
this one leaves no evidence that anything happened. Mechanics:
[../data-model/02-organization.md §4](../data-model/02-organization.md#4-joins-leaves-and-transfers-close-one-row-open-another).

**No member row is ever inferred.** The corpus names no groups any more than it names units
([D-092](../decisions/round-09.md#d-092--the-corpus-is-people-and-events-and-it-names-no-units)), so the
one-off import owes no group rows and no member rows at all: **every `person_group_member` row in this
system is typed by a person**, which is also the only way one could be true.

---

## 6. Appointments

**An appointment is a `role_holder` row:** a role, a person, a period, who granted it, a note. Written by
`role.assign` and removed by `role.unassign`, always held at the unit, because there is one scope and
nowhere else to hold an office. It confers nothing by itself: the codes an office carries are the live
grants whose expression names `ROLE(x)`
([../data-model/05-authorization.md §3–§4](../data-model/05-authorization.md#3-role--an-office)).
"That these two may manage the counselors roster" is a grant on the *role*, the same move a group gets.
There is no position, no slot, no `max_holders`, and no `is_leadership` flag: nothing in the system records
a seat that exists unfilled.

**This module holds no eligibility rule of any kind.** There is no `requires_membership` and no `min_age` on
an office, and no gate in the resolver: membership is an operand, written into the grant.

The expression that says each thing, in the form D-101's canonical rendering stores it — every **compound**
operand bracketed, a leaf left bare:

| The rule to express | The expression |
|---|---|
| the office applies only to current members | `(MEMBERS * ROLE(x))` |
| the office applies whether or not the holder is a member | `ROLE(x)`, written without `MEMBERS` |
| one named person is exempt from the membership requirement | `(MEMBERS * ROLE(x)) + PERSON(y)` |

**`PERSON(y)` is the only way to name a human being in an expression.** A set of named people is written
`PERSON(a) + PERSON(b)`, and there is no second spelling of it
([D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)).
A person who must be excepted is subtracted as themselves, and the exemption belongs `+ PERSON(y)` inside
the very grant that carries the rule, so the exception is read next to the thing it exempts. The registry of
named operands lives in one table —
[the selector registry](../data-model/05a-audience-and-grammar.md#the-selector-registry) — and this page does not
recite its row count.

The posture is **opt-in per grant**, so a grant written as `ROLE(TREASURERS)` with no `MEMBERS` authorizes a
lapsed member silently and forever. The controls are a standing report of live grants that name a
`ROLE(...)` operand without `MEMBERS`, seeded grants that carry `MEMBERS`, and an import count — not the
resolver. Nothing forces a holder row to end either; the report is the control
([D-071](../decisions/round-05.md#d-071--nothing-forces-a-role-assignment-to-end-the-gate-and-the-report-are-the-control)).
All of that belongs to the authorization model and is named here only because these were this module's
workflows: [06-authorization-model.md](06-authorization-model.md).

**Three consequences, stated plainly.**

- **"The leader of the Thursday group" has no referent.** A group has no leadership and no roles (§2), so
  the sentence means *a person on that roster who also holds some office*, and nothing links the two. The
  office is `ROLE(leaders)` and means what its name says.
- **Elected versus appointed is not stored data.** It survives only as roles the organization invents
  (`elected_council` beside `appointed_it`) — or not at all.
- **A vacancy is not a reportable state.** "This seat has been empty since March" needs a slot that exists
  unfilled. An empty office is the absence of rows in `role_holder`, and absence has no start date on the
  office. A rule-filled role stays refused: **F-12's answer is no**, `role_holder` names one person, because
  an office record that cannot answer "who was treasurer in 2023" is not an office record
  ([F-12](../open-questions.md#f-12)).

---

## 7. The module and the permission system, in one table

Stated once here so that nothing below the line is re-specified in this page's voice. Full detail:
[06-authorization-model.md](06-authorization-model.md) and
[../data-model/05-authorization.md](../data-model/05-authorization.md).

| Question | Answer | Owner |
|---|---|---|
| Where is authority held? | at the unit, or on exactly one item — nothing in between | D-097, D-099 |
| What is a group to the resolver? | an **item** in `grant_scope_type`, and a `GROUP(x)` leaf in an expression | D-098, D-101 |
| Does being in a group grant anything? | no. A set is not a grant | D-005, D-098, D-102 for `ORGANIZERS` |
| What may a role do? | read the live grants whose expression names `ROLE(x)` — a role confers nothing | D-100 |
| How is precedence decided? | allowed iff some live allow applies and no live deny applies. There is no level and no locality | D-099 |
| Does a unit-scope grant reach an item? | yes, every item of every type. A grant on one item reaches that item only | D-099, D-102 |
| Is there a membership gate in the resolver? | no. `MEMBERS` is an operand, evaluated live on the checked date | D-100 |
| Can the center be locked out of a body's data? | the question has no subject: there is one body and its people are the only people there are | D-097 |

**There is no ancestor walk, because there is no tree**: no `unit_ancestors()`, no `unit_descendants()`, no
path-consistency check. The permission check matches scope exactly — the unit, or the item.

---

## 8. Open issues

Open, and tracked in [../open-questions.md](../open-questions.md):

- **Where a claimed group continuity is recorded.** The method says continuity is asserted, never matched
  (§4); no table accepts the assertion. Until somebody rules, the default is the whole rule: a returning
  name is a new group.
- **Whether a group's previous name should be kept at all.** It is not, deliberately, as part of "no
  special features". If the organization turns out to rename groups often, the answer is a decision and not
  a column someone adds quietly.
- **Whether an ended group should be hidden from pickers.** A `person_group` with `valid_to` set has no
  stated behaviour either way yet.

---

*Decisions behind this page: D-002, D-005, D-016, D-043, D-081, D-083, D-086, D-088, D-092, D-096, D-097,
D-098, D-099, D-100, D-101, D-102, D-103, D-105, D-071.*
