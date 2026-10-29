# Decision Log — Refinement round 10 — the deletions, part 1 (D-097 … D-100)

> The unit becomes a scope rather than a row, and a grant becomes one permission that either allows or denies.

[Refinement round 9 — organization (D-091 … D-096) ←](round-09.md) | [All decisions](index.md) | [Refinement round 10 — the deletions, part 2 (D-101 … D-104) →](round-10b.md)

---

## D-097 — There are no sub-units. The unit is a scope, not a row

**Status:** decided (from your answer)
**Date:** refinement round 10
**Reverses:** [D-008](round-01a.md#d-008--organizations-units-are-one-self-referencing-table-with-configurable-types),
[D-035](round-02-03.md#d-035--one-root-unit-all-sub-units-nest-arbitrarily-beneath-it),
[D-036](round-02-03.md#d-036--units-cannot-be-reparented-a-unit-that-moves-is-a-new-unit),
[D-041](round-02-03.md#d-041--belonging-to-a-sub-unit-is-a-participation-record-not-a-membership),
[D-049](round-04.md#d-049--the-root-may-not-read-into-its-sub-units-scope_exposure-is-the-only-crossing),
[D-050](round-04.md#d-050--a-renewal-inside-the-window-extends-the-existing-root-participation-row),
[D-054](round-04.md#d-054--the-sub-unit-vocabulary-is-not-seeded-the-organization-defines-its-own-types),
[D-078](round-06.md#d-078--an-exposure-extends-an-assignment-never-a-direct-grant),
[D-096](round-09.md#d-096--a-reused-unit-number-is-a-new-unit-unless-someone-records-the-continuity).
Amends [D-031](round-02-03.md#d-031--no-downward-inheritance-of-authority-scope_exposure-is-the-only-crossing)
and [D-095](round-09.md#d-095--units-carry-no-restrictions-joining-one-is-somebody-elses-act), whose subject was
always the nested unit.

**Your words.** *"I want to remove the sub-organizations completely. They are more of a 'group of
people'. They are useful in permission groups, however they should not hide any information or have any
special features. I have over-specified the system and this complicates things."* Asked whether anything
below the organization should still scope authority, the answer was **no** — and asked whether the root
unit is still a table, the answer was **"no table — the unit is a scope"**, with the vocabulary settled
in the same breath: **unit** means the root, the organization itself, of which there is one; **group**
means a set of people, which is where [D-098](#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority)
goes.

**Decision.** **The organization has no internal structure in this system.** There is one unit, it is the
organization, and it is not a row: it is the non-item scope that `grant_scope_type` already carries
(`is_item_scoped = false`, a grant at it has no `scope_id`). Its code is `unit`. Everything that existed
to describe the inside of an organization is deleted:

| Deleted | With it goes |
|---|---|
| `org_unit` | the root row, the one-root partial unique index, `path`, `depth`, `status`, `code`, `data_confidence` on units |
| `org_unit_type`, `org_unit_type_rule` | the runtime unit vocabulary, `is_leaf`, `max_depth`, the seven-step nesting check, and the whole of [D-054](round-04.md#d-054--the-sub-unit-vocabulary-is-not-seeded-the-organization-defines-its-own-types)'s argument about not guessing words |
| `org_unit_name` | rename and renumber history, `change_reason`, and the denormalised `org_unit.name` it fed |
| `org_unit_relationship` | `split_from`, `merged_into`, `successor_of`, `renamed_to` |
| `unit_participation` | sub-unit rosters, the root participation row every membership owed, and the transfers between units |
| `scope_exposure`, `scope.expose` | the only downward crossing, the direction-of-authority check, the `scope.exposure.review` code, and the nightly alert that was its sole detector |
| `unit_ancestors()`, `unit_descendants()` | the recursive walk, the path-consistency check, and the CI assertion that the resolver never calls it |
| `role_assignment.scope_type` / `scope_id` | a role is always held at the unit; there is nothing else to hold it at |
| the resolver's unit tier | the ladder of [D-032](round-02-03.md#d-032--deny-is-absolute-locality-orders-allows-only) drops from four tiers to the ones [D-099](#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality) states |

**Why this is affordable now, when it was not affordable in round 1.** Because of
[D-092](round-09.md#d-092--the-corpus-is-people-and-events-and-it-names-no-units), which your own answer supplied:
**the legacy corpus names no units.** Two exports — people with their membership period at the root, and
events with attendance — and no unit column anywhere. So the hierarchy has no recorded history to lose;
"who was in pack X in 2011" already had no answer at go-live, and was already written down as a
consequence rather than a bug. A structure that describes nothing imported and (per
[D-095](round-09.md#d-095--units-carry-no-restrictions-joining-one-is-somebody-elses-act)) restricts nothing is a
structure that carries no information, which is the definition of the over-specification you were
pointing at.

**The rule that dies hardest is the founding one.** [D-031](round-02-03.md#d-031--no-downward-inheritance-of-authority-scope_exposure-is-the-only-crossing)
—"authority over a unit originates at that unit and cannot be claimed from outside it"— existed to stop
the center deciding permissions inside a body it does not run. **With one unit there is no "outside it"
to be stopped from.** The rule is not weakened by this decision, it is *deprived of its subject*: every
permission is held at the unit or on an item, and the unit's people are the only people there are. What
D-031's reasoning still supports is carried forward by [D-099](#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)
(deny is absolute) and by the ownership and guardianship channels, neither of which was ever about units.

**What is genuinely lost, said once and not argued away.**

1. **The unit is no longer a locus of accountability for a child's records.** D-031's safeguarding
   property was that access to a pack's children had to be granted *by that pack*, by people who recruited
   the leader and can be asked. That property is gone, and nothing in the remaining model reproduces it:
   a permission held at the unit reaches every member, and `person.view` was already the widest read
   permission in the system ([D-083](round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data),
   [D-086](round-07-08.md#d-086--a-sensitivity-mark-grades-what-a-grant-exposes-not-the-table-it-reads)). What is left of
   the safeguarding story is the same three things D-095 was left with — a permission held by a named
   adult, an audit trail whose payloads expire after two years
   ([D-088](round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)), and a report of who
   holds the write — **minus the part where the named adult was somebody the unit chose.**
2. **"Who was in the Thursday group in 2011?"** stays answerable, because
   [D-098](#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority) dates its
   member rows. What is lost is the *unit* framing: there is no "and everything nested under it" left to
   ask about, so the subtree question that justified the materialized path has no subject.
3. **Restructuring stops being a recorded event.** Splits, mergers and successions were the organization
   module's whole history problem (`domain/04 §3`) and they are simply gone: a group that splits is an old
   group that ended and two that began, with no edge between them unless somebody writes one.
4. **Unit-scoped reports** — a pack's roster, a pack's events, "which units exist" — have no subject to
   report on. The organizational-year reports that mattered are membership and fee reports, which live at
   the unit and are unaffected.

**One thing gets easier that nobody counted.** [F-10](../open-questions.md#f-10--which-invariants-the-orm-cannot-express-and-who-writes-those)
shape 4 — a column that may not change once set, the only shape with **no report at all** because a
violation leaves every row individually valid — had exactly one instance in the whole design,
`org_unit.parent_unit_id`. It has none now. The single-root conditional uniqueness (shape 2) goes too,
along with integrity checks 1–10 of `data-model/02-organization.md §9` and check 10's peculiar job of
asserting that a migration had emitted a constraint.

**Import, restated.** The one-off import owes `person`, `membership` (D-093) and — since D-102 — events
and registrations. It owes **no participation rows to anything**, which retires D-093's knock-on about
the root participation row and `03-membership.md §5.1`'s write obligation with it. Group membership is
never inferred from anything: the corpus does not name groups either, so every `person_group_member` row
is typed by a person, which is also the only way it can be true.

**Two-way door?** **No.** This is a deletion of a dimension, not a flag. The route back is a decision
with a reason attached — most plausibly "the organization has grown past one center's visibility" — and
that decision would have to re-argue D-031 from its own premises, because the mechanism that made it
work (`scope_exposure`, written by the covered unit) no longer exists.

**See:** [domain/04-organization-structure.md](../domain/04-organization-structure.md) (rewritten as the
groups module), [data-model/02-organization.md](../data-model/02-organization.md),
[data-model/05-authorization.md §6](../data-model/05-authorization.md#6-access_grant--the-per-item-layer),
[data-model/03-membership.md §5](../data-model/03-membership.md#5-unit_participation--deleted-by-d-097).

---

## D-098 — A group is a `person_group`: explicit members, a lifetime, and no authority

**Status:** decided (from your answer)
**Date:** refinement round 10
**Follows:** [D-097](#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)
**Supersedes the subject of:** [D-041](round-02-03.md#d-041--belonging-to-a-sub-unit-is-a-participation-record-not-a-membership)

**Closes:** — 

**Your words.** *"A group defined by display name and an audience… A group is just an audience, but it is
visible to the users of the system (if the permissions say so)."* Then, when the choice was put back as
*group-is-an-audience* or *audience-is-a-selector*: *"person_group, but let's make it upside down — a
group will have explicitly stated members and a person_group can be used as an audience selector"*, and
*"a group will have explicitly stated members (all members live, while the group lives). The group can
have a lifetime (start and end date)."*

**Decision.** **`person_group`** — a `name`, a `description`, its own `valid_from`/`valid_to`, the
standard audit columns. **`person_group_member`** — (`person_group_id`, `person_id`, `valid_from`, `valid_to`, who wrote it,
when). **The member row is dated**: assignment, removal and re-assignment are all periods on the same
pair, so the roster has a history of its own rather than borrowing the audit trail's. `person_group`
is registered in `grant_scope_type`, so **a group is an item** and a grant can be written on one —
which is how "these two people may work this group's roster" is said without inventing a scope
([D-099](#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)).

**What a group is not, in one list, because this is the part the previous design got wrong.** It has no
parent and no children, no type and no vocabulary of types, no `code`, no path, no nesting rules, no
rename history, no split or merger edge, no leadership of its own, **no roles** (your words: *"screw
them, the groups don't have any roles, only the root unit"*), and no fee. It holds no permissions over
its members by being a group: a member of a group is not able to do anything, which is
[D-005](round-01a.md#d-005--permissions-are-grants-never-derived-from-identity) and
[D-019](round-01b.md#d-019--household-membership-grants-no-access) restated one level down — participation is not
authority, and the fact that the participation is now stored in a tidier table does not quietly promote it.

**Why the word "audience" survives at all, and where the line is.** You named the inversion, and it is
the load-bearing part of this entry: **a group states its members; a selector picks them.**
`person_group` is the domain fact — a thing a user sees, names, opens, and ends. `audience` is the
grantee a grant names, and one of its operands may be a `person_group`
([D-101](round-10b.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree)).
Two tables answer "who is in it", which is precisely the shape
[D-080](round-06.md#d-080--five-contradictions-the-translation-surfaced-and-how-each-was-resolved) teaches to be
suspicious of, so the difference is stated rather than implied: a group's members are a **list of people
that is true whether or not any permission points at it**; `audience_member` rows are an **addition to a
rule**, meaningful only inside the selector they complete. A group exists to be talked about; a selector
exists to be aimed at something.

**Membership of the unit is unchanged and is not a group.** One membership per person, at the unit, paid
for yearly (D-037, D-040, D-047). `unit_participation` is deleted with the units
([D-097](#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)), including the root row every
membership used to be issued with, so **"everyone in the organization" is now one query against
`membership` and "everyone in the Thursday group" is one query against `person_group_member`** — two
shapes, and no longer one shape with a depth in it.
[D-050](round-04.md#d-050--a-renewal-inside-the-window-extends-the-existing-root-participation-row)'s renewal
mechanism narrows to exactly what it always claimed to be about: the `membership` row, per
[D-016](round-01b.md#d-016--renewal-opens-a-new-membership-row-not-an-extended-valid_to).

**Joining a group is still somebody else's act, and D-095's reasoning transfers intact.** The gate is
`person_group.member.manage`, held at the unit (which reaches every group, per D-099) or granted on one
group as an item. There is no self-scoped variant and none will be added: nobody writes themselves onto a
roster, which was the whole of D-095 and is unchanged by moving the roster. `membership_request`
**loses `requested_unit_id`** — a request is for membership of the unit, and which group a new member
lands in is a write on the group, not a preference on the request.

**So the history question has an answer, and it is the same answer every dated row in this system
gives.** "Who was in `schuzka2026-1` on 14 March 2026?" is a point-in-time read over
`person_group_member`, exactly as `domain/05`'s query 3 was for a unit, and it survives the audit
trail's 24-month payload expiry ([D-088](round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short))
because it does not depend on the trail. **The group's own `valid_from`/`valid_to` and the member rows'
periods are two different facts** and both are kept: the first says the group existed over that span,
the second says who was in it. An open group with dated members answers the historical question just
fine, which is the whole reason the rows are dated — the naming in your own example (`schuzka2026-1`)
becomes a habit the organization may or may not keep, rather than the mechanism history depends on.

**Dating the rows imports the invariant set that dating always imports**, and naming them here is the
work: where both ends are set, `valid_to` is later than `valid_from`; **no two rows for the same person
and group may overlap**, counted over **all** rows and not only the open ones, half-open so a row ending
on a day and one beginning that same day do not collide (the
[D-002](round-01a.md#d-002--everything-temporal-is-a-period-never-a-boolean) shape, and
[F-10](../open-questions.md#f-10--which-invariants-the-orm-cannot-express-and-who-writes-those) shape 1,
so a hand-written migration emits it and the ORM will not); a person who left in 2020 and came back in
2024 is **two rows**, never one row edited in place, because the edit destroys the answer to "was she in
the group in 2019?"; and moving from one group to another closes one row and opens another —
`03-membership.md §5.2`'s transfer discipline, retargeted at groups and otherwise unchanged.

**The duplication is now real, which is why the two tables are said apart by their rules and not only
by their names.** `person_group_member` and `audience_member` are both dated sets of people, which is
precisely the pair
[D-080](round-06.md#d-080--five-contradictions-the-translation-surfaced-and-how-each-was-resolved) teaches a reader
to distrust — two statements that can drift, one of which will be the one the screens read. They stay
apart because the *maintenance* differs, and the dated shape makes the difference sharper rather than
softer: a group's members are the organization's record of who attends, kept by the people who run the
group, and it is true when no grant exists; `audience_member` rows are a selector's additions, kept by
whoever composes permissions, and are meaningless outside the selector they complete. **Merging them
would make the permission table the system's roster**, which is the same mistake D-062 refused when it
declined to answer "who is running this camp?" by reading the grant table.

> **Amended by [D-105](round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other),
> which deleted one half of the pair.** There is no `audience_member` any more, so the distrust this
> paragraph arranges is aimed at a table that no longer exists — and the duplication it feared is gone
> rather than reconciled. What survives is the *distinction*, now carried by a leaf instead of a table:
> a group's dated roster is the organization's record of who attends and is true when no grant exists,
> while `PERSON(x)` inside an expression is an addition made by whoever composes permissions and means
> nothing outside it. **The closing refusal survives, and is cheaper to honour than it was.** The temptation
> to answer "who is running this camp?" from the grant table was always resisted by saying *use the roster
> instead*; when the roster was the only dated set of people, that was a real constraint on the composer.
> Now there is a second way to name the same people — a run of `PERSON(...)` leaves written beside the
> grant — so the hazard this entry named has moved from "two tables drift" to "the composer chose the
> wrong one", which is what [data-model/02-organization.md](../data-model/02-organization.md) now says out
> loud, and what a `MEMBERS * ROLE(...)` expression exists to make the obvious answer.

**What is actually given up against `unit_participation` is small and worth listing, because "no special
features" was the instruction.** No `join_reason_code` / `leave_reason_code` (and so no `transfer`,
`promotion`, `reorganisation`, `unit_closed` vocabulary to maintain or to get wrong), no `is_primary`
saying which of a person's groups to show first, no `role_in_unit` display label, no `data_confidence`
and nothing to import into: the corpus names no groups, so every member row is written by a person
([D-092](round-09.md#d-092--the-corpus-is-people-and-events-and-it-names-no-units),
[D-097](#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)).

**Two-way door?** The periods are the door and they are open. What to refuse later is the *vocabulary*
that used to hang off them — a controlled `leave_reason_code` list is exactly the eighteen-ticks-without-a-receipt
shape D-095 removed, and a `role_in_unit` column is the thing that always turns into an authorization
check the moment somebody is asked "can she edit the roster?"

**See:** [domain/04-organization-structure.md](../domain/04-organization-structure.md),
[data-model/02-organization.md §1–§2](../data-model/02-organization.md#1-person_group),
[data-model/03-membership.md §5](../data-model/03-membership.md#5-unit_participation--deleted-by-d-097).

---

## D-099 — A grant allows or denies one permission. There is no level, and no locality

**Status:** decided (from your answer)
**Date:** refinement round 10
**Reverses:** [D-012](round-01a.md#d-012--status-strings-compare-by-rank-never-lexicographically)
(including the reason it was written), [D-013](round-01a.md#d-013--explicit-deny-revoked-is-checked-before-everything)
as a *level*, [D-032](round-02-03.md#d-032--deny-is-absolute-locality-orders-allows-only)'s second half,
[D-074](round-06.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular)'s level form,
[D-010](round-01a.md#d-010--role-assignments-and-access-grants-share-a-scope-model-and-a-resolver).
Amends [D-055](round-04.md#d-055--the-permission-catalog-is-deliberately-comprehensive-and-granular),
[D-068](round-05.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle) and
[D-079](round-06.md#d-079--the-guardianship-channel-is-entered-by-shape-not-by-permission-name).

**Your words.** *"This is more complicated. I said that there are read, write, none permissions. This is
not correct. What would make the most sense is if items would inherit all unit-scope permissions and would
have their own item-scope permissions in the same format (e.g. `event.edit`). Both of those permissions are
essentially the same, however in the item-scope some of them don't make sense (e.g. on an event,
`membership.manage`, or `event.create`, make no sense). On the item-scope there should also be a
deny-permission, not just allow-permission."* And on whether anything still needs a ladder: **"only
allow/deny on the same permissions as on the root unit."**

**Decision.** **One grant is: a grantee, a scope, one permission code, an effect, and a period.** The
grantee is a person or an audience ([D-042](round-02-03.md#d-042--grants-may-target-audiences-not-only-individuals),
unchanged). The scope is the unit or exactly one item ([D-097](#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)).
The effect is `allow` or `deny`. The answer is:

> **allowed** when some live allow applies and **no** live deny applies.

That is the whole of the precedence rule. What it replaces, item by item:

| Deleted | Was | Why it goes |
|---|---|---|
| `access_level` | `revoked` 0, `view` 10, `contribute` 20, `manage` 30, `admin` 40 | A level is a **bundle** of permissions identified by one word. [D-068](round-05.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle) already refused that idea once, when it deleted `<resource>.admin` and said *roles are the bundle*. This finishes the same thought: roles and audiences are the bundle, and nothing else is |
| `permission_level` | which level satisfies which permission at which scope type | Its two jobs move to two columns on `permission` itself (§below) |
| The rank integer | [D-012](round-01a.md#d-012--status-strings-compare-by-rank-never-lexicographically) | There is no ordering left to compare. The famous bug it guarded — `'admin' < 'contribute'` — cannot occur in a system with no levels, which is a better fix than the guard |
| Locality | [D-032](round-02-03.md#d-032--deny-is-absolute-locality-orders-allows-only): a nearer allow beats a further one | **Locality only ever ranked allows against each other.** With a boolean answer, two allows that both apply produce one answer; there is nothing to order. D-032's first half — deny is absolute — survives intact and is now its entire content |
| `revoked` as a level | resolver channel 0 | Deny survives as an **effect on a grant row**. [D-013](round-01a.md#d-013--explicit-deny-revoked-is-checked-before-everything)'s requirement — a court-ordered restriction must not be beatable by a broader grant — is unchanged and is still checked first |

**`permission` gains two columns, and only one of them is comfortable.**

- **`applies_to` ∈ `unit`, `unit_and_item`** — where a code may be granted at all. This is your
  observation that `event.create` and `membership.manage` are nonsense *on* an event, written as data
  instead of as prose. It is checked when the grant is saved, not at check time: a grant of
  `event.create` written on one event is refused with the reason in the error, because an event cannot
  be created twice, and a creation permission attached to a thing that already exists answers no
  question.
- **`right_kind` ∈ `read`, `write`** — and it exists for exactly one customer.
  [D-074](round-06.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular) fixes a guardian's
  rights at three values, and with the ladder gone the guardianship channel has nothing left to compare
  a permission against. This column is that thing: `none` covers nothing, `view` covers `read` codes,
  `write` covers both. **It is a column whose only job is one other mechanism, and saying so is cheaper
  than discovering it later.** The alternative was to store permission codes on the guardianship row,
  which D-074 refused on the grounds that a volunteer cannot maintain a 74-code checklist per child.

**Inheritance, stated once.** A grant at the unit reaches **every item of every type**, because after
[D-097](#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row) there is no intermediate scope left
between the unit and an item, and no ownership relation to test. A grant on one item reaches that item
and nothing else. This is [D-006](round-01a.md#d-006--per-item-permissions-are-capabilities-on-the-item) —
per-item permissions are capabilities on the item — with the unit tier left standing, and it deletes
`can_event()` outright ([D-102](round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)).

**`-` in a selector is not a deny, and the two are not interchangeable.** An audience expression may
subtract a set (`MEMBERS - GROUP(x)`), which narrows **one grant's reach**. A deny defeats **every grant**
that applies to that person, including ones written elsewhere, later, or by somebody else. The first
cannot express "she must not have this, whatever else she is given", which is
[D-013](round-01a.md#d-013--explicit-deny-revoked-is-checked-before-everything)'s whole reason for existing, so denies
stay — and they are legal at the unit as well as on an item, since "exclude her from what the unit grants
everyone" is exactly the case the selector cannot serve.

**The round silently upgraded deny, and the upgrade needs naming because it changes an operator's job.**
[D-013](round-01a.md#d-013--explicit-deny-revoked-is-checked-before-everything) did not say a deny beats everything; it
said `revoked` beats `deny`, which left an escape hatch — a stale denial could be outranked by a newer act,
and *revoking* it was a decision somebody could take late and still take. Deleting the ranking deleted the
hatch. **A live deny now beats every live allow with no tie-break of any kind, and the only thing that
removes one is a person ending its period.** That is why the integrity check below is a requirement rather
than a nicety, and why a deny is the row on which `access_grant.valid_to` earns its keep: everywhere else an
open-ended grant that outlived its reason costs a tidy database, and here it costs a child who cannot see
their own camp photos. A date is the only remedy that works without somebody remembering to act.

**What it costs, in rows.** A role that used to be one grant at `manage` is now one row per code. The
catalog holds 66 codes; a broad office is a couple of dozen rows. That is the price of the question you
are now able to ask — *"what exactly does this person have?"* answered by reading rows — and the price of
the one you can no longer ask, which is *"what does `manage` give me on this event?"*: there is no such
word, so there is no such lookup. **Integrity check to add:** a live grant whose `effect` is `deny` and
whose grantee, scope and code match no live allow is dead weight and should be reported, because a deny
that denies nothing is how a stale restriction survives its reason.

**Two-way door?** Cheap in one direction, expensive in the other. Levels can come back as **names for
sets of codes** with no comparison defined — which is what a role already is, so no new mechanism is
needed to approximate one. A real ordering coming back means re-importing `permission_level`, the rank
rule, and locality's tie-break, all of which were deleted with their only consumers.

**See:** [data-model/05-authorization.md §2, §6–§7](../data-model/05-authorization.md#6-access_grant--the-per-item-layer),
[domain/06-authorization-model.md](../domain/06-authorization-model.md),
[appendix/permission-catalog.md](../appendix/permission-catalog.md).

---

## D-100 — A role is an office and a group is company: two tables of the same shape

**Status:** decided (from your answer)
**Date:** refinement round 10
**Follows:** [D-097](#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row),
[D-098](#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority),
[D-099](#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)

**Reverses:** [D-039](round-02-03.md#d-039--member-permissions-require-a-current-paid-membership)'s resolver clause,
[D-051](round-04.md#d-051--the-membership-gate-is-waived-by-a-permission-not-only-by-a-role-flag) entirely,
[D-033](round-02-03.md#d-033--multiple-people-may-occupy-the-same-position) and the position module,
[D-009](round-01a.md#d-009--unit-membership-links-to-person-not-to-membership)'s remaining subject.

**Closes:** [F-12](../open-questions.md#f-12--closed--may-a-role-be-held-by-a-rule-as-an-audience-is).

**Your words.** *"A `role_assignment` is no longer necessary, as it can be supplemented by a `ROLE`
selector in the audience string."* Then, when asked whether roles go too: **"Role and group are technically
the same, but not semantically. A role was meant to be for a single person / a small couple of individuals
that are visible as the leaders / financial / IT managers of the organization, while the group is a
temporary set of members that do e.g. events together."* And on the gate: *"This should be sortable with
the audiences, right? Some permission (e.g. `event.create`) can be assigned to `MEMBERS * COUNSELORS`."*

**Decision.** Three things, of which the first is the one that looks like nothing.

**1. `role_assignment` becomes `role_holder`.** (`role_id`, `person_id`, `valid_from`, `valid_to`,
`granted_by`, `note`) — no scope columns, because [D-097](#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)
left one scope. `role` keeps `code`, `name`, `description`, `is_system`, `sort_order`. **`role_permission`
is deleted**: a role confers nothing by itself, and the codes an office carries are the live grants whose
audience names `ROLE(x)`. What that buys is the question the old design could not answer cleanly — *"what
may a treasurer do?"* — which is now a query over visible grant rows rather than a walk through a bundle
table nobody reads. This is where
[D-068](round-05.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle) was already going; it
just went the rest of the way. `role.create`, `role.edit`, `role.delete`, `role.view`, `role.assign`,
`role.unassign` survive, retargeted: the last two write `role_holder`.
`role.scope_required` and `role.requires_membership` are deleted with their mechanisms.
`role` joins `person_group` in `grant_scope_type`, so *"these two may manage the counselors roster"* is a
grant on one role, which is D-098's move applied symmetrically.

**2. Positions are deleted.** `position`, `position_assignment`, `is_leadership`, `max_holders` and the
appointment workflows go: with no units there is no *body* to be a leader **of**, which is the only thing a
position recorded and a role does not
([D-033](round-02-03.md#d-033--multiple-people-may-occupy-the-same-position)'s own reasoning for why leadership is a
position-assignment fact and not a role fact). An elected leader is now a holder of a role, and the
audience rule that used to read `unit_leaders` — which round 6 had to correct because it was silently
matching nobody — is `ROLE(leaders)` and means what its name says. What is genuinely lost is the
*elected-versus-appointed* distinction as stored data: it survives only as a role the organization
invents (`elected_council` next to `appointed_it`) or not at all.
**F-12 is closed and its answer is no**: `role_holder` names one person. The reason the register refused
it — a derived holder list cannot answer "who was treasurer in 2023", and an office record that cannot
answer that is not an office record — is untouched, and the grantee pair that F-12 contemplated is no
longer even tempting, because grants now aim **at** roles instead of roles being filled **by** grants.

**3. The gate moves from the resolver into the selector, and this is the round's largest deletion.**
[D-039](round-02-03.md#d-039--member-permissions-require-a-current-paid-membership) made the resolver ask, for every
grant, whether the holder currently holds a membership;
[D-051](round-04.md#d-051--the-membership-gate-is-waived-by-a-permission-not-only-by-a-role-flag) then needed
`system.gate_exempt` and `person_holds_gate_exempt` to let appointed people through anyway, with the
documented hazard that a permission check performed *through* `can()` there means a lockout with no error
message. Now `MEMBERS` is a selector operand evaluated live on the checked date, and:

| Old mechanism | New expression |
|---|---|
| The gate applied to a role with `requires_membership = true` | `MEMBERS * ROLE(x)` |
| The gate waived for a whole role | `ROLE(x)` — write it without `MEMBERS` |
| The gate waived for one named person (`system.gate_exempt`) | `MEMBERS * ROLE(x) + PERSON(y)` |

`role.requires_membership`, `system.gate_exempt` and `person_holds_gate_exempt` are all deleted, the
resolver's membership clause is deleted, and the special-case path that had to be carefully kept *out* of
`can()` goes with it. **Ownership and guardianship stay channels and are unaffected** — they were never
gated. [D-071](round-05.md#d-071--nothing-forces-a-role-assignment-to-end-the-gate-and-the-report-are-the-control)'s
posture transfers to `role_holder`: nothing forces a holder row to end, and the control is the report.

**The posture reverses, and the new failure mode is named rather than buried.** The gate used to be
**default-on**, so that forgetting it was impossible. It is now **opt-in per grant**: a grant written as
`ROLE(TREASURERS)` with no `MEMBERS` authorizes a lapsed member, silently, forever. Three controls, none
of which is the resolver:

- **A standing report** of live grants naming a `ROLE(...)` operand whose expression does not contain
  `MEMBERS`. An office held by a non-member is the case worth a human eye, and this report is narrow
  enough to actually be read.
- **Seeded grants and any grant template carry `MEMBERS`**, so the path of least repetition is the safe
  path.
- **Import completeness.** `MEMBERS * COUNSELORS` is only as correct as the counselor roster: the gate
  used to fall out of membership alone, so an import that misses 300 counselors silently un-gates them.
  It fails closed — nothing breaks, which is exactly why nobody notices. The import reconciliation report
  of [D-090](round-07-08.md#d-090--the-legacy-corpus-is-thousands-of-roster-rows-with-numbers-and-no-money) must count
  people marked as counselors in the corpus against `role_holder` rows written.

**`PERSON(y)` is a selector, and this entry is the reason it had to become one.** The grammar D-101 first
shipped did not include it — `LIST` and `GROUP(x)` cover the enumeration cases, and a language with no
attribute operands has no obvious place for one person — which left the third row of the table above
unparseable in the very entry that wrote it down. It is seeded in `selector_type` like every other operand,
it takes a person, and it passes the materializability test for the plain reason that a set of one is a
set. The workaround the membership module reached for before this was repaired — *write a second grant
whose grantee is that person* — stays legal and is arguably clearer for a permanent exception; what was not
acceptable is a control that does not parse.

**A consequence of moving the gate that no entry in this round had named: the expiry sweep can lock the
organization out of its own system.** [D-040](round-02-03.md#d-040--the-fee-expires-yearly-a-date-tracked-renewal-window-replaces-a-grace-status)
lapses memberships **on a date, to everyone at once**, and whoever runs that sweep is a member too. Under
D-039 the collision existed but `system.gate_exempt` was the purpose-built hole in it, and that mechanism is
deleted above. So **an administrative office whose grants read `MEMBERS * ROLE(...)` stops working at the
instant the sweep lapses its holder** — including the office that would have been asked to fix it. What
carries the case now is the second control: the seeded grants for offices that must survive a lapse are
written `ROLE(...)` with no `MEMBERS`, which turns a flag nobody read into a written expression with an
outage attached to getting it wrong. *Assumption:* the seeded `is_system` role set contains at least one
such office; nothing in the catalog requires it to, and if it does not, 1 January is a support call.

**Why two tables, when you said they are technically the same.** Because the difference decides **who may
edit the membership**, and one table would merge those two permissions into one. `role.*` is the most
sensitive code family in the catalog (🔒🔒); writing a group's roster is `person_group.member.manage` (⚠).
One `person_group` table with a `kind` column and one membership table gives a single code that both adds
a child to the Thursday group and puts the holder into `SYSTEM_ADMINS`. That is the merge to refuse, and
it is the answer to [D-080](round-06.md#d-080--five-contradictions-the-translation-surfaced-and-how-each-was-resolved)'s
lesson about two same-shaped tables: **these are not two statements of one rule, they are two different
grants of power.** Same columns, different codes, and `ROLE(x)` / `GROUP(x)` distinct in the grant text so
the distinction is visible to whoever reads the grant — which is where you asked for it.

**`COUNSELORS` is seeded, as a role.** A permanent, organization-wide population is the opposite of your
own definition of a group (*"a temporary set of members that do events together"*), and the table decides
the sensitivity that protects the set every safeguarding convention hangs from. It ships `is_system` so an
editor refuses to delete it. Consistent with [D-005](round-01a.md#d-005--permissions-are-grants-never-derived-from-identity):
this is a **set**, and being in it confers nothing until a grant names it — audience membership has never
been authority
([D-042](round-02-03.md#d-042--grants-may-target-audiences-not-only-individuals), restated in
[D-091](round-09.md#d-091--a-permission-group-is-a-rule-and-a-list-at-once-and-a-rule-may-name-another-group)).
Bare `COUNSELORS` is legal in an expression, which makes the name namespace load-bearing
([D-101](round-10b.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree)).

**Two-way door?** The gate is the expensive half. Restoring a default-on membership test means re-adding
a resolver clause *and* re-deciding which permissions it applies to, because a system where every
expression is explicit has no record of which grants were meant to be gated. The role/group split is a
cheap door in both directions: the tables have the same shape, so merging them is a migration, and the
only thing to re-argue is the permission separation this entry records.

**See:** [data-model/05-authorization.md §3–§4](../data-model/05-authorization.md#3-role--an-office),
[domain/06-authorization-model.md](../domain/06-authorization-model.md),
[domain/02-actors.md](../domain/02-actors.md),
[appendix/permission-catalog.md §11](../appendix/permission-catalog.md#11-roles--proposed-seed-set).

---
