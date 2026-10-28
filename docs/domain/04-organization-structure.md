# Groups

One organization, and the named sets of people inside it.

**This page used to describe a hierarchy.** [D-097](../decisions/decision-log.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)
deleted it, and not by simplifying it: the module's subject stopped being a structure and became two
things that were previously buried inside it — the organization, which is one unit and is not stored, and
the **group**, which is a set of people and is
([D-098](../decisions/decision-log.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority)).
What follows says what the organization is now, what that costs, what a group is and is not, and where the
workflows that used to end at a position now end.

**The vocabulary, first, because everything here leans on it.**

| Word | Means | Stored as |
|---|---|---|
| **unit** | the organization itself. There is exactly one. It is a **scope**, never a row | nothing — a code in `grant_scope_type` |
| **group** | a named set of people with explicitly dated members and a lifetime. A set, not a body | `person_group` + `person_group_member` |
| **role** | an office: a small, visible set of holders — leaders, finance, IT | `role` + `role_holder` ([D-100](../decisions/decision-log.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)) |
| **audience** | an expression over named sets, which a grant is aimed at | `audience` ([D-101](../decisions/decision-log.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree)) |
| **selector** | one operand of that expression: `MEMBERS`, `GROUP(x)`, `ROLE(x)`, … | `selector_type`, `audience_operand` |

Roles and audiences belong to the authorization model
([06-authorization-model.md](06-authorization-model.md), [../data-model/05-authorization.md](../data-model/05-authorization.md))
and are not re-specified here. This page owns the unit and the group.

---

## 1. The organization is one unit, and the unit is a scope

**There is one unit and it is the organization.** It has no parent, no children, no type, no code, no
path, no depth, and no row. It is the non-item scope that `grant_scope_type` already carries — code
`unit`, `is_item_scoped = false`, and a grant written at it has no `scope_id`. Nothing in the schema
represents it, because there is nothing to represent: a second unit cannot appear, for the same reason a
second answer to a question cannot appear in a field that does not exist
([D-097](../decisions/decision-log.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)).

**Membership is unchanged and is not a group.** One membership per person, at the unit, paid for yearly.
It used to be issued with a participation row on the root unit so that "everyone in unit X" was one
uniform query whether X was the organization or a Thursday-evening pack; that row is deleted with the
units. So now:

- **"everyone in the organization"** is one query against `membership`;
- **"everyone in the Thursday group"** is one query against `person_group_member`.

Two shapes instead of one shape with a depth in it, and neither one borrows the other's table. Renewal
narrows to exactly what it always claimed to be about — the `membership` row, a new row per renewal
([D-016](../decisions/decision-log.md#d-016--renewal-opens-a-new-membership-row-not-an-extended-valid_to))
— because the row it used to extend on a renewal is gone with the units, and
[D-050](../decisions/decision-log.md#d-050--a-renewal-inside-the-window-extends-the-existing-root-participation-row)
is reversed rather than narrowed.

**A grant at the unit reaches everything**, every item of every type, because nothing stands between the
unit and an item any more and there is no ownership relation left to test
([D-099](../decisions/decision-log.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality),
[D-102](../decisions/decision-log.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)).
That is a sentence about the permission system; it is stated here only because it is what "scope" means
now that "row" does not.

### What that costs, said once

The hierarchy was not free-standing decoration, and deleting it spent real properties. They are listed
here rather than distributed through the page, and they are not argued away.

1. **The unit is no longer a locus of accountability for a child's records.** This is the one that matters
   and it is the founding rule's.
   [D-031](../decisions/decision-log.md#d-031--no-downward-inheritance-of-authority-scope_exposure-is-the-only-crossing)
   said ~~authority over a unit originates at that unit and cannot be claimed from outside it~~ — it
   existed so that access to a pack's children had to be granted *by that pack*, by the people who
   recruited its leader and can be asked about it. **Reversed by
   [D-097](../decisions/decision-log.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)**, which
   does not weaken the rule but deprives it of its subject: with one unit there is no "outside it" to be
   stopped from. Nothing in the remaining model reproduces the property. A permission held at the unit
   reaches every member, and `person.view` was already the widest read permission in the system
   ([D-083](../decisions/decision-log.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data),
   [D-086](../decisions/decision-log.md#d-086--a-sensitivity-mark-grades-what-a-grant-exposes-not-the-table-it-reads)).
   What survives of the safeguarding story is the same three things D-095 left behind — a permission held
   by a named adult, an audit trail whose payloads expire after two years
   ([D-088](../decisions/decision-log.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)),
   and a report of who holds the write — **minus the part where the named adult was somebody the unit
   chose.**
2. **The subtree question has no subject.** "Who was in the Thursday group in 2011?" stays answerable,
   because group member rows are dated (§5). What is gone is "and everything nested under it", which was
   the only question the materialized path existed to answer. A set of people has no sub-sets stored
   inside it.
3. **Restructuring stops being a recorded event.** Splits, mergers and successions were this module's
   whole history problem, and they are simply gone. A group that splits is an old group that ended and two
   that began, with no edge between them unless somebody writes one — and after
   [D-098](../decisions/decision-log.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority)
   there is no table left where that edge could go (§4).
4. **Unit-scoped reports have nothing to report on.** "A pack's roster", "a pack's events", "which units
   exist" are not hard questions any more, they are questions with no subject. The organizational-year
   reports that actually mattered — membership and fees — live at the unit and are untouched.

**One thing gets easier, and nobody counted it.** The invariant class with no report at all —
[F-10](../open-questions.md#f-10--which-invariants-the-orm-cannot-express-and-who-writes-those) shape 4, a
column that may not change once set, whose violation leaves every row individually valid — had exactly one
instance in the entire design, `org_unit.parent_unit_id`. It has none now. The details, including the ten
integrity checks this retired, are in
[../data-model/02-organization.md §5](../data-model/02-organization.md#5-what-this-page-held-before-round-10).

**Why this was affordable now and was not affordable in round 1**:
[D-092](../decisions/decision-log.md#d-092--the-corpus-is-people-and-events-and-it-names-no-units). The
legacy corpus names no units — two exports, people with their membership period and events with
attendance, no unit column anywhere. A structure that describes nothing imported and, per
[D-095](../decisions/decision-log.md#d-095--units-carry-no-restrictions-joining-one-is-somebody-elses-act),
restricts nothing carries no information. That is the definition of the over-specification the round was
called to remove.

**It is not a two-way door.** This is the deletion of a dimension, not a flag. The route back is a
decision with a reason attached — most plausibly "the organization has outgrown one center's visibility" —
and it would have to re-argue D-031 from its own premises, because the mechanism that made that decision
work (`scope_exposure`, written by the unit it covered) no longer exists.

---

## 2. What a group is, and everything a group is not

**A group is a `person_group`: a name, a description, its own lifetime, and explicitly dated members**
([D-098](../decisions/decision-log.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority)).
It is a **set of people, not a body**. Somebody names it, somebody puts people in it, somebody ends it, and
the record of who was in it when is the roster's own (§5). A weekly meeting group, a project crew, a
trainers' pool, `schuzka2026-1` — all the same kind of thing, and the system has no opinion about which
ones deserve to exist.

**Everything a body would have had, a group does not have.** This is the list the previous design got
wrong, so it is stated flatly:

| A group has | Because |
|---|---|
| no parent and no children | there are no sub-units, and groups do not nest (D-097, D-098) |
| no type, and no vocabulary of types | the runtime unit vocabulary is deleted with `org_unit_type` (D-097); a group needs no word for what kind of set it is |
| no `code`, no path, no depth | a label carries no identity (§4); a set has no position to sit at |
| no nesting rules | there is nothing to nest |
| no rename history | the name is a column, and the old name is not kept (§4) |
| no split, merger or succession edge | restructuring is no longer an event (§1, cost 3) |
| no leadership of its own | positions are deleted (D-100); see §6 |
| **no roles** | an office is a role and a role is held at the unit; a group has none of its own, and no leadership column will be added to make one look derivable (D-098, D-100) |
| no fee | membership is at the unit and is the only thing that costs money |
| **no permissions over its members** | see immediately below |

**Membership of a group confers nothing, and tidier storage does not quietly change that.** A member of a
group cannot do anything. That is
[D-005](../decisions/decision-log.md#d-005--permissions-are-grants-never-derived-from-identity) and
[D-019](../decisions/decision-log.md#d-019--household-membership-grants-no-access) restated one level down:
participation is not authority, and it stays not-authority when it moves into a table with better
columns. Authority arrives only through a grant that names the group, which is §4 of
[../data-model/02-organization.md](../data-model/02-organization.md#3-a-group-is-an-item-a-grant-can-be-written-on-one).

**Where the line against an audience is drawn, because the two are one row apart in shape and a mile apart
in meaning.** The round's inversion is the load-bearing part: **a group states its members; a selector
picks them.** A group's members are a list of people that is true whether or not any permission points at
it; an audience's `LIST` rows are an addition to an expression, meaningful only inside the expression they
complete. A group exists to be talked about; a selector exists to be aimed at something. Two tables that
both answer "who is in it" is exactly the shape
[D-080](../decisions/decision-log.md#d-080--five-contradictions-the-translation-surfaced-and-how-each-was-resolved)
teaches a reader to distrust, so the difference is stated, not implied — and merging them would make the
permission table the system's roster, which is the mistake
[D-062](../decisions/decision-log.md#d-062--organizers-are-appointed-on-the-event-not-granted) already
refused for events.

**Where the line against a role is drawn, in one sentence, because it decides who may edit the list.** A
role is an office with a small, visible set of holders and is written by the most sensitive code family in
the catalog (`role.*`, 🔒🔒); a group is company, and its roster is written by `person_group.member.manage`
(⚠). One table with a `kind` column would give a single permission that both adds a child to the Thursday
group and puts the holder into the administrators — that is the merge to refuse, and D-100 refuses it.
`GROUP(x)` and `ROLE(x)` stay distinct in the grant text so the distinction is visible to whoever reads
the grant.

---

## 3. Joining a group is somebody else's act

**Nobody writes themselves onto a roster.** The gate is `person_group.member.manage`, held at the unit —
which reaches every group, because after D-097 nothing stands between a unit-scope grant and an item — or
granted on one group as an item, which is how "these two people may work *this* roster" is said without
inventing a scope ([D-098](../decisions/decision-log.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority),
[D-099](../decisions/decision-log.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)).
There is no self-scoped variant and none will be added. Moving the roster from `unit_participation` to
`person_group_member` changed the table and not the rule: D-095's reasoning transfers intact.

**What the gate replaced is worth keeping in mind, because it is the reason the gate is trusted.**
`org_unit_type.allows_minors` used to refuse a child's placement by consulting a flag on the unit's type.
[D-095](../decisions/decision-log.md#d-095--units-carry-no-restrictions-joining-one-is-somebody-elses-act)
removed it — *a list of eighteen ticks nobody read is not a safeguard, it is a receipt* — and replaced it
with a permission held by named adults. Per
[D-081](../decisions/decision-log.md#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now),
the rule's name outlived its mechanism, so: *do not place a child where nobody is responsible for them* is
enforced by **who may write the member row**, now in `person_group_member`, audited and naming who wrote
it. A permission refuses every write by the wrong person regardless of the child's age; a boolean only ever
refused a placement nobody had thought about.

**And what it still costs, once.** The system cannot say which groups are for children. Nothing on a
`person_group` answers that question and, consistent with "no special features", nothing will: no
`allows_minors`, no `is_children`, no type to hang it on. Combined with no recorded background checks
([D-043](../decisions/decision-log.md#d-043--no-background-checks-are-recorded-in-this-system)) and with
cost 1 above, the safeguarding story of this module is a permission held by named adults, an audit trail
that forgets values after two years, and a report. If that turns out to be too little — after an incident,
or an insurer's question — the route back is a rule about who may be placed where, argued once as a
decision with its enforcement layer named in D-081's terms, and **not** a resurrected column whose name
implies it enforces something.

**A membership request is a request for membership of the unit, and carries no group.** It used to carry a
preferred unit; `requested_unit_id` is deleted, because which group a new member lands in is a write on
the group and not a preference on the request ([D-098](../decisions/decision-log.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority)).
The request flow in [05-membership-lifecycle.md](05-membership-lifecycle.md) ends at the unit; a roster is
somebody else's decision afterwards, which is the same fact as the paragraph above stated from the other
side.

---

## 4. A name carries no identity

**A group name is a label, and a label is not the group.** This is the method
[D-096](../decisions/decision-log.md#d-096--a-reused-unit-number-is-a-new-unit-unless-someone-records-the-continuity)
reached for units — *"what is a unit number?"* was the answer to the question rather than the question —
and D-097 deleted the units while leaving the reasoning intact, so it transfers to groups: **a group name
that comes back after a decade is a new group, unless somebody records that it is not**
([D-096](../decisions/decision-log.md#d-096--a-reused-unit-number-is-a-new-unit-unless-someone-records-the-continuity),
superseded as to units and standing as to method).

**Why the default matters is the part that was worth deciding.** Continuity is not a property of a label;
it is a claim about the world, and only a human knows whether the crew refounded in 2026 *is* the crew of
2016 or a second crew with the same tasteful name. Left unstated, the question is answered anyway — by
whoever writes the matching screen, who will match on name, and will let a thirty-year gap sit inside one
group's life. So the default is stated and it points at **a new `person_group` row**. The old case the
corpus separates and keeps — *a renumber is one unit with two name rows* — has no survivor: a group has no
name history, so a rename is an edit to one column and the previous name is not kept (§2).

**The honest half: the method outlived its recording mechanism.** D-096 put the continuity claim in
`org_unit_relationship` as `successor_of`. That table is deleted, and
[D-098](../decisions/decision-log.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority)
refuses group-to-group edges outright — no split, no merger, no succession — so the assertion has **no
field to live in**. What the method still guarantees is therefore the direction of the default, which is
the half that was ever enforceable: a returning name is a new group, and two groups that are really one
look like two unless a person writes that down somewhere. *Where that sentence goes is not decided.* The
cheapest true answer available today is a `note` on the second group's member rows and on the group's
`description`, which nothing reads and nothing links; the honest alternative is to accept that the
organization's memory of its own continuity is prose.
**Status:** assumption — this page does not choose, and the question is recorded in
[../open-questions.md](../open-questions.md).

**Names are one namespace with roles and audiences, and that is a new dependency of the naming method.**
Because `ROLE(x)` and `GROUP(x)` no longer have to disambiguate, a bare `COUNSELORS` resolves against roles
and groups together, so names are unique across the tables, case/whitespace/separators are folded on write,
and **every `selector_type.code` is a reserved name** — a group called `MEMBERS` is refused at the save
rather than silently rewriting every expression in the system
([D-101](../decisions/decision-log.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree)).
`audience.code` joined the namespace when an audience became an operand that could be named
([D-103](../decisions/decision-log.md#d-103--an-audience-may-name-another-audience)), and the pair of rules
is worth holding apart: **a bare name never resolves to an audience** — the arm must be written
`AUDIENCE(veterans)` — yet a group still may not *borrow* an audience's code, because a name that resolves
two ways is a silent grant whatever the resolution rules say. No single constraint spans the three tables,
so the write path carries the rule and an integrity check asserts that it does. What a grant stores is kind + id, never a name, so **renaming a group never rewrites a
grant** — the storage follows the method rather than the label. Mechanics:
[../data-model/02-organization.md §1](../data-model/02-organization.md#1-person_group).

---

## 5. A roster is history

**Member rows are dated, and that is what makes the roster answerable.** `person_group_member` carries
`valid_from` and `valid_to` per person, so joining, leaving and coming back are all periods on the same
pair, and the roster has a history of its own instead of borrowing the audit trail's
([D-098](../decisions/decision-log.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority)).
"Who was in `schuzka2026-1` on 14 March 2026?" is a point-in-time read over those rows. It survives the
audit trail's 24-month payload expiry
([D-088](../decisions/decision-log.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short))
because it does not depend on the trail — which is the entire reason the rows are dated rather than a live
flag, and the reason a naming habit like `schuzka2026-1` is a habit an organization may or may not keep
rather than the mechanism history rests on.

**This is the one place the module is ahead of the operand that looks most like it, and it is worth naming
because the two are otherwise easy to confuse.** An audience named as an operand evaluates live, so its
past shape survives only in the audit trail and stops surviving when the payloads expire; a group's set is
its dated rows, so it keeps a past the audit trail cannot take away
([D-103](../decisions/decision-log.md#d-103--an-audience-may-name-another-audience) states this as the cost
of the audience arm, and it belongs to this page as the credit side of the group's). "Who could see this
child's data in 2024?" is answerable when the grant pointed at a group and is not answerable when it
pointed at a nested audience. That asymmetry is a fact about which of the two is a roster, and it is the
strongest reason the pair stays two tables.

**Two facts, both kept, and not to be conflated.** The group's `valid_from`/`valid_to` says the group
existed over that span; the member rows' periods say who was in it. An open group with dated members
answers the historical question perfectly well, and an ended group's rows are not tidied up. **Ending the
group is no longer an edit anyone makes on their own, though:** setting that end date is refused while a live
grant, or a live audience reachable from one, names the group, because an empty set inside a subtraction
widens a deny that the person ending the group did not write and would not look at again
([D-103](../decisions/decision-log.md#d-103--an-audience-may-name-another-audience); the write path and the
check that watch it are
[../data-model/02-organization.md §3](../data-model/02-organization.md#3-a-group-is-an-item-a-grant-can-be-written-on-one)).

**A person who left in 2020 and came back in 2024 is two rows.** Never one row edited in place, because
the edit destroys the answer to "was she in the group in 2019?", which is the same argument
[D-016](../decisions/decision-log.md#d-016--renewal-opens-a-new-membership-row-not-an-extended-valid_to)
makes about renewals and this system makes about every temporal fact
([D-002](../decisions/decision-log.md#d-002--everything-temporal-is-a-period-never-a-boolean)).

**Moving from one group to another closes one row and opens another.** The transfer discipline of
`03-membership.md` §5.2 transfers to groups unchanged, and so does the design rule that used to sit under
participation: **never rewrite a member row to point at a different group.** Close it and open a new one.
Rewriting destroys "where was this child in 2003?", and unlike most tempting edits this one leaves no
evidence that anything happened. A group moving *into* a different parent has no meaning now, because
there is no parent (§2); the old page's answer — the unit closes and a new one is created — was about a
dimension the module no longer has. Mechanics:
[../data-model/02-organization.md §4](../data-model/02-organization.md#4-joins-leaves-and-transfers-close-one-row-open-another).

**No member row is ever inferred.** The corpus names no groups any more than it names units
([D-092](../decisions/decision-log.md#d-092--the-corpus-is-people-and-events-and-it-names-no-units)), so
the one-off import owes no group rows and no member rows at all: **every `person_group_member` row in this
system is typed by a person**, which is also the only way one could be true
([D-097](../decisions/decision-log.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)).

---

## 6. Appointments, which no longer end at a position

**This section used to describe an appointment.** A position was a slot in a unit, a position assignment
filled it, `is_leadership` marked the slots that counted as leading, `max_holders` said how many people
could fill one at once, and the screen offered "appoint as scoutmaster" as one action that could create a
slot-filling and a role assignment together. **All of it is deleted by
[D-100](../decisions/decision-log.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)**,
and the reason is not austerity but that the one thing a position recorded and a role does not — the *body*
someone is a leader **of** — stopped existing when the bodies did.

**What an appointment is now.** A `role_holder` row: a role, a person, a period, who granted it, a note.
Written by `role.assign` and removed by `role.unassign`, always held at the unit, because D-097 left one
scope and there is nowhere else to hold an office. It confers nothing by itself: the codes an office
carries are the live grants whose expression names `ROLE(x)`
([../data-model/05-authorization.md §3–§4](../data-model/05-authorization.md#3-role--an-office)).
"That these two may manage the counselors roster" is a grant on the *role*, the same move a group gets.

**The gate moved from the resolver into the expression, and the posture reversed.** This module no longer
holds an eligibility rule of any kind: `requires_membership` and `min_age` were columns on positions and
they are gone with them. Where the membership test went:

The expression that replaces each, in the form D-101's canonical rendering stores it — every **compound**
operand bracketed, a leaf left bare:

| The old mechanism | The expression that replaces it |
|---|---|
| a role gated on current membership (`requires_membership`) | `(MEMBERS * ROLE(x))` |
| a role exempt from the gate | `ROLE(x)`, written without `MEMBERS` |
| one named person exempt (`system.gate_exempt`) | `(MEMBERS * ROLE(x)) + PERSON(y)` |

**`PERSON` is a seeded selector, so that third row parses.** It did not when this page first printed the
expression: the registry of seeded operands had been written from the evaluator's arm list rather than from
D-101's grammar, and the arm nobody had implemented yet is exactly the kind of thing such a copy loses. The
registry carries **thirteen** rows and `PERSON` is one of them — takes an argument, that argument is a
person, binds to no item. The omission is recorded as an amendment in D-101 rather than fixed quietly, and
the class of defect it belongs to, a registry prose contradicts, is what
[D-104](../decisions/decision-log.md#d-104--a-permission-codes-last-segment-is-an-action-and-a-registry-that-prose-contradicts-is-a-fiction)
answers.

**`PERSON` is an argument; `LIST` is one set belonging to one audience, and both survive because they do
different jobs.** `LIST` is the audience's own dated list of people: `+ LIST` adds everyone on it and
`- LIST` takes all of them back with it, because it is one operand moving as one unit. `PERSON(y)` names one
person, so it composes and can be excepted on its own — which is why the exemption is written
`+ PERSON(y)` inside the very grant that carries the rule, keeping the exception visible next to the thing it
exempts (D-100's placement), and why a person who must be excepted is subtracted as themselves rather than by
subtracting a list they happen to sit on. The kitchen example D-103 works through needs both operands, which
is the proof they are not one operand wearing two names.

The posture flips from **default-on** to **opt-in per grant**, so a grant written as `ROLE(TREASURERS)`
with no `MEMBERS` authorizes a lapsed member silently and forever. The controls are a standing report of
live grants that name a `ROLE(...)` operand without `MEMBERS`, seeded grants that carry `MEMBERS`, and an
import count — not the resolver. Nothing forces a holder row to end either, which is
[D-071](../decisions/decision-log.md#d-071--nothing-forces-a-role-assignment-to-end-the-gate-and-the-report-are-the-control)'s
posture transferred intact: the report is the control. All of that belongs to the authorization model and
is named here only because these were this module's workflows:
[06-authorization-model.md](06-authorization-model.md),
[../data-model/05-authorization.md §3–§4](../data-model/05-authorization.md#3-role--an-office).

**Three consequences, stated plainly.**

- **"The leader of the Thursday group" has no referent.** A group has no leadership and no roles (§2), so
  the sentence means *a person on that roster who also holds some office*, and nothing links the two. The
  old derived group `unit_leaders`, which round 6 had to be corrected for silently matching nobody, is now
  `ROLE(leaders)` and means what its name says.
- **Elected versus appointed is no longer stored data.** It survives only as roles the organization
  invents (`elected_council` beside `appointed_it`) — or not at all.
- **A vacancy is no longer a reportable state.** "This seat has been empty since March" needed a slot that
  exists unfilled, which is what `max_holders` and a position were for. An empty office is now the absence
  of rows in `role_holder`, and absence has no start date on the office. A rule-filled role stays refused:
  **F-12 is closed and its answer is no**, `role_holder` names one person, because an office record that
  cannot answer "who was treasurer in 2023" is not an office record
  ([F-12](../open-questions.md#f-12--closed--may-a-role-be-held-by-a-rule-as-an-audience-is)).

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

**There is no ancestor walk, because there is no tree.** `unit_ancestors()` and `unit_descendants()` are
deleted, along with the path-consistency check and the CI assertion that the resolver never calls them —
an assertion about a function that does not exist is not a guard. The permission check matches scope
exactly: the unit, or the item.

---

## 8. Open issues

Open, and tracked in [../open-questions.md](../open-questions.md):

- **Where a claimed group continuity is recorded.** The method says continuity is asserted, never
  matched (§4); no table accepts the assertion any more. Until somebody rules, the default is the whole
  rule: a returning name is a new group.
- **Whether a group's previous name should be kept at all.** It is not, and D-098 chose that deliberately
  as part of "no special features". If the organization turns out to rename groups the way units used to
  be renamed, the answer is a decision and not a column someone adds quietly.
- **Whether an ended group should be hidden from pickers.** Closed units were excluded from pickers by
  default and included in historical reports always; a `person_group` with `valid_to` set has no stated
  behaviour either way yet.
- **F-10**, which layer writes the no-overlap invariant on member rows. It is named in
  [../data-model/02-organization.md §2](../data-model/02-organization.md#2-person_group_member) and
  remains unanswered.

**Resolved, and no longer open — kept visible so the reasoning survives.** The organizational structure
itself, the sub-unit vocabulary and the nesting rules (there is no structure to name or nest — D-097);
reparenting (the dimension is gone, so the question is not prohibited, it is unaskable); participation
versus membership (participation is deleted; membership at the unit and group rosters are the two shapes —
§1); whether a person may belong to several groups at once (yes, and there is no `is_primary` saying which
to show first); whether the unit may read into what these docs used to call its sub-units (moot after
D-097 — there is one scope and its people are the only people there are); whether a role may be
filled by a rule (**F-12**, closed: no); whether appointing a leader should create a role assignment
(positions are deleted — §6).

All tracked in [../open-questions.md](../open-questions.md).
