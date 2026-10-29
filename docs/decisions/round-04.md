# Decision Log — Refinement round 4 (D-047 … D-057)

> The organisational year, the gate and its waiver, roles as runtime data, and the removal of `household`.

[Refinement rounds 2 and 3 (D-031 … D-046) ←](round-02-03.md) | [All decisions](index.md) | [Refinement round 5 — the events module (D-058 … D-071) →](round-05.md)

---

## D-047 — The fee expires on 1 January

**Status:** decided (from your answer)
**Date:** refinement round 4
**Resolves:** A-4 (the date half)

**Decision.** The organizational membership year runs with the calendar: the fee for a year
expires on **1 January**. The yearly expiry sweep runs on that date, and the renewal campaign
follows it.

**Why.** Your answer, from the three options offered: *"1 January"*. It aligns the year with
the calendar, so "a member this year" means what a reader expects, and the sweep, the campaign
and the reports all land on a boundary nobody has to look up.

**Consequence.** `membership_type.expiry_month` / `expiry_day` carry it as data rather than as
a constant, because a date written into code is a date the organization cannot move when it
changes its mind. Every lapse date, the sweep, the renewal worklist ~~and the cache invalidation~~
derive from this one parameter **(`cache invalidation` left the list with the cache itself — see D-039's first
cost bullet and [D-114](round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation)); changing it re-dates every *future* period but leaves
historical ones alone, which is the reason it is a parameter and not an expression computed
into stored rows.

**See:** [D-040](round-02-03.md#d-040--the-fee-expires-yearly-a-date-tracked-renewal-window-replaces-a-grace-status),
[../data-model/03-membership.md §1](../data-model/03-membership.md#1-membership_type--one-row-kept-as-a-table).

---

## D-048 — The renewal window is 60 days, and is a configuration parameter

**Status:** decided (from your answer)
**Date:** refinement round 4
**Resolves:** A-4 (the window half)

**Decision.** The renewal window after the expiry date is **60 days**. It is stored as a
parameter (`membership_type.renewal_grace_days`), not compiled into the application.

**Why.** Your answer: *"Make it 60 days, but it should not be hard to modify (even if it would
be in the code)."* The 60 is a starting value; the requirement is that it can be changed
without a code change.

**The design is already the parameter, deliberately.** The window lives in the database, and
`in_renewal_window()` reads it. So the second half of the answer is not a constraint to
satisfy — it is a description of what is already built. The one thing that must *not* happen
is a front-end or a scheduled job hardcoding `90` or `60`; every reader goes through the
column.

**Consequence.** Seat the sweep and the renewal campaign to read the window from the row, and
the value can be tuned between years as the organization learns what actually gets paid.

**See:** [D-040](round-02-03.md#d-040--the-fee-expires-yearly-a-date-tracked-renewal-window-replaces-a-grace-status),
[../data-model/03-membership.md §3](../data-model/03-membership.md#3-membership).

---

## D-049 — The root may not read into its sub-units; `scope_exposure` is the only crossing

**Status:** decided (from your answer)
**Date:** refinement round 4

**Superseded by [D-097](round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row). The crossing is gone because both of its sides are gone.** The property this
bought — that access to a body's members had to be granted *by that body*, by people who recruited the
leader and can be asked — is recorded as **lost** in `docs/README.md` and in D-097's own costing, rather
than being dropped quietly.

**Resolves:** C-1

**Decision.** There is **no reporting channel outside the permission model** and none is
built. A unit's own material — its events, its rosters, its local leadership — is visible to
the root **only** when that unit writes a `scope_exposure` naming the assignment it is exposed
to. Every crossing is a written, attributed act by the unit that owns the data.

**Why.** Your answer, from the three routes offered: *"scope_exposure only"*. The
no-downward-inheritance rule ([D-031](round-02-03.md#d-031--no-downward-inheritance-of-authority-scope_exposure-is-the-only-crossing))
is the organization's own constitutional principle — *"the organization itself should not be
able to itself decide permissions over the nested unit, it must come from the unit itself
up."* A reporting channel would be an exception to it that grows, because every subsequent
question ("can the root see X?") has a plausible answer of "yes, for reporting". The rule is
easier to keep when there is no side door to argue about.

**The cost, named.** The root must ask, per unit, per period, and nobody can make a pack
expose its scope. For the questions the root genuinely needs to answer, this is less painful
than it sounds — see the consequence below, which is the part that makes this decision
affordable.

**Consequence — most of C-1 dissolved when the root became the membership unit.** The root
**owns** the registry, the memberships and the fees ([D-035](round-02-03.md#d-035--one-root-unit-all-sub-units-nest-arbitrarily-beneath-it)),
so a treasurer or registrar working at the root is not reaching into anyone else's data. These
need no exposure at all:

| Question | Answered from | Exposure needed |
|---|---|---|
| How many members were there in 2019? | `membership` — the root's own table | **No** |
| Who is currently a member? | `membership` | **No** |
| What fees are outstanding? | `fee_obligation` | **No** |
| Was this person a member on this date? | `membership` | **No** |
| Who was in the 4th Pack in 1998? | `unit_participation`, scoped to that unit | **Yes** |
| Which events did a pack run? | the pack's own material | **Yes** |
| Who leads a pack? | `position_assignment`, scoped to that unit | **Yes** |

The upper half is the organization's own records. The lower half is the unit's. This split is
the whole of D-049: **the root does not need to see into a unit to answer a question about
membership, because membership is the root's.**

**One thing that now looks like a bug and is not.** The `registrar` role
([appendix/permission-catalog.md §11](../appendix/permission-catalog.md#11-roles--proposed-seed-set))
holds `unit_participation.view` at organization scope. Under exact-match scoping that does
**not** let the registrar read any sub-unit's roster — the role's scope is the root, and a
sub-unit roster is a different scope. It reads the **root** participation rows, which is what
the registrar actually needs ([D-041](round-02-03.md#d-041--belonging-to-a-sub-unit-is-a-participation-record-not-a-membership),
[03-membership.md §5.1](../data-model/03-membership.md#5-unit_participation--deleted-by-d-097)).
This will be misread as a mistake by someone who assumes a parent can see its children. It is
not a mistake, and the catalog says so in place.

**See:** [../domain/06-authorization-model.md §2](../domain/06-authorization-model.md#2-scopes--the-unit-and-the-item),
[../data-model/05-authorization.md §5](../data-model/05-authorization.md#5-scope_exposure--deleted-by-d-097).

---

## D-050 — A renewal inside the window extends the existing root participation row

**Status:** decided (from your answer)
**Date:** refinement round 4

**Superseded by [D-097](round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row) and [D-098](round-10a.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority): there is no participation row, so a renewal extends nothing but
the `membership`.** The renewal-window semantics [D-040](round-02-03.md#d-040--the-fee-expires-yearly-a-date-tracked-renewal-window-replaces-a-grace-status)
defined are untouched.

**Resolves:** D-7

**Decision.** When a membership lapses on 1 January and the person pays inside the window, the
new membership period is backdated to the expiry date ([D-040](round-02-03.md#d-040--the-fee-expires-yearly-a-date-tracked-renewal-window-replaces-a-grace-status))
and the **root-unit participation row is extended** to cover the same span. It is not closed
and reopened.

Mechanically, the sweep does **not** close the root row: it moves `valid_to` forward to
1 January, and the renewal clears it back to `NULL` (or sets the new period end), so the row
tracks the membership across the boundary without ever being two rows.

**Why.** Your answer: *"Extend the existing row."* The alternative — close at the expiry date,
open a new backdated row — is more literal about what happened, but it makes the renewal path
diverge from the initial-creation path, and it produces two rows per person per year for the
one row the schema most wants to be simple.

**The honest cost, recorded rather than hidden.** Extending **erases the evidence that a lapse
occurred**: a person who lapsed and renewed looks, in `unit_participation`, exactly like a
person who never lapsed. The gap exists only if you go and look at the membership rows. This
is accepted deliberately, because:

1. `membership` remains the authority on payment, and the lapse is fully visible there —
   the two rows disagree about nothing, they simply answer different questions.
2. The participation table is a *roster* history ("who was in this unit when"), not a
   *payment* history. Erasing a gap in the roster is the correct thing to do: the child was
   in the pack across that period, and the question the table exists to answer has one
   answer, not two.

**Consequence for the participation overlap constraint.** `ex_unit_participation_no_overlap`
([03-membership.md §5](../data-model/03-membership.md#5-unit_participation--deleted-by-d-097)) is what makes the
close-and-reopen alternative awkward, and extending avoids the constraint entirely. The
integrity check that verifies the root row mirrors the membership
([03-membership.md §7](../data-model/03-membership.md#7-integrity-checks), check 1b) remains
valid and unchanged: after a renewal the two agree, and during a lapse-only period — before
any payment — the membership has ended while the root row has not yet been swept, which is
why the sweep must run and must run before anything reads the roster for authority.

**See:** [../data-model/03-membership.md §5.1](../data-model/03-membership.md#5-unit_participation--deleted-by-d-097).

---

## D-051 — The membership gate is waived by a permission, not only by a role flag

**Status:** decided (from your answer)
**Date:** refinement round 4

**Reversed entirely by D-100.** [D-100](round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape) moves the gate into the audience expression, and this
entry's `system.gate_exempt` is deleted together with the lockout hazard it documented. The diagnosis
that produced it — a membership check performed *inside* `can()` is a lockout nobody can see — is still
the reason the round kept every one of these tests out of the resolver.

**Resolves:** D-6

**Decision.** A new **permission**, `system.gate_exempt`, waives the membership gate
([D-039](round-02-03.md#d-039--member-permissions-require-a-current-paid-membership)) for anyone who holds
it. It is delivered the way every other permission is: by being placed in a **role**, which is
then assigned to a person at the root or at a unit.

- It is a **`system`-namespace** permission, so it can only arrive through a
  `role_assignment` — **never** through an `access_grant`. An item-level grant must not be
  able to lift the gate.
- It is **exempt from the gate itself.** Holding it does not depend on membership, or it
  could not do its job.
- It is **scope-independent**: a person who holds it anywhere is waived everywhere. This is
  what makes it "system-wide" — the gate is a property of the person's membership, so the
  waiver has to be too.

**Why.** Your answer: *"Let's create a system-wide permission, that means that their
permissions do not end if their membership lapses... The `system.gate_exempt` is one of the
permissions that can be assigned to the permission groups."*

This replaces the earlier framing, in which `role.requires_membership` was the only switch and
the question was therefore which *roles* to exempt. It is a better fit for the model as it
actually works: every organizational role is a **permission group**, a person may hold several
at once (a leader may also hold a role carrying `system_admin`; a counselor may hold a role
carrying event creation and `person.view`), and a role may be assigned at the root or at a
unit. A flag on the role answers "is this role membership-dependent?"; a permission answers
"is *this person* exempt?", which is the question the exemption actually is.

**`role.requires_membership` stays.** It is not superseded — the two compose, and they answer
different questions:

| | Question | Granularity | Effect |
|---|---|---|---|
| `role.requires_membership = false` | Is this **role** membership-dependent? | the role | the role grants regardless of membership |
| `system.gate_exempt` | Is this **person** exempt? | the person | **every** gated role they hold is honoured |

A role flag is the blunt form: it exempts everyone who holds that role, everywhere.
The permission is the precise form: it exempts named people, and can be granted and revoked
as an act of its own. The resolver honours a role if **either** applies.

**Who holds it.** `system_admin` — without it, the 1 January sweep lapses every membership
including the administrator's, and the person who would repair the system loses the ability to
use it on the day it breaks. That is a lockout, not a policy. Beyond `system_admin`, which
roles carry it is settled in the role review
([F-1](../appendix/permission-catalog.md#11-roles--proposed-seed-set)) — the mechanism is
fixed here, the membership of the list is data.

**The evaluation must not go through `can()`.** Reading the permission through the resolver
would be circular: `can()` would have to evaluate the gate in order to learn whether the gate
applies, and a lapsed holder of `system.gate_exempt` would be denied it by the very rule it
exists to lift — an unbreakable lockout with no error message. The resolver therefore checks
for the permission by **direct lookup against live role assignments**, outside its own gate
condition. This is the one place the resolver reads the role tables without consulting
itself, and it is deliberate.

**Consequence.** Integrity reports gain a row: who currently holds an exemption, and under
which assignment. It is a small list of people who keep authority without paying, and it
should be as visible as the `system.admin` holders already are.

**See:** [../data-model/05-authorization.md §3](../data-model/05-authorization.md#3-role--an-office),
[../data-model/05 §12](../data-model/05d-invariants-and-seed.md#12-what-the-organization-starts-with),
[../appendix/permission-catalog.md §11](../appendix/permission-catalog.md#11-roles--proposed-seed-set).

---

## D-052 — Roles are runtime data; the seed set is not a specification

**Status:** decided (from your answer)
**Date:** refinement round 4
**Resolves:** the remainder of D-6, and the framing of F-1

**Decision.** Roles are **created, edited, assigned and deleted by the organization at
runtime** — they are not a vocabulary the specification fixes. A person may hold several
roles at once, at the root or at a unit, so a leader can hold a leadership role *and* a role
carrying administrative permissions, and a counselor can hold a role carrying event creation
and `person.view`.

**Why.** Your answer: *"The roles should be create-able in the system, and it should be also
possible to assign people, delete the roles and so on. So you don't really need to know which
roles carry `system.gate_exempt`."*

This is a correction to how the documentation was framing F-1. Three documents presented the
role list as something awaiting approval, with a `Waives gate` column to be filled in. That
was wrong: a role is a **permission group**, and which permissions an organization puts in a
group is a configuration act, not a design decision. The seed set survives as a worked example
of the shape; it is explicitly not a requirement list.

**What this does *not* delegate.** The *shape* stays fixed, and two properties of it are
load-bearing precisely because a configuration screen must not be able to weaken them:

1. **`system.gate_exempt` is `system`-namespace**, so it can only arrive through a role and
   never through an `access_grant`. An item grant cannot lift the membership gate.
2. **A role that has ever been assigned cannot be deleted**, so the assignment history
   survives. Deleting `system_admin` would remove the only route to `system.admin`
   permanently.

**Consequences, and what had to change in the schema.**

| Gap | Fix |
|---|---|
| `is_system` claimed "cannot be deleted" with nothing enforcing it | A `BEFORE DELETE` trigger: refuses deletion of any role with assignments, and of any system role |
| No permissions existed for role lifecycle | `role.create` and `role.delete` added to the catalog, both 🔒🔒 |
| Integrity check 16 | Orphaned assignments |

> **This decision was amended by [D-053](#d-053--a-role-is-valid-always-only-its-assignment-is-temporal),
> which removed the retirement mechanism D-052 originally introduced.** D-052 as first written
> gave `role` a `valid_from`/`valid_to`, added a `role.retire` permission, made the resolver
> check the role's period, replaced `UNIQUE (code)` with a partial index so retired codes
> could be reused, and added check 17 reporting roles expiring while still held. All of that is
> gone: a role is valid always. The correction came from the user in the same round, and the
> superseded reasoning is kept here rather than edited away, because the *reason* it looked
> right is instructive — retirement appears to be the elegant way to abolish a role in one
> act, and it is only when you ask what "a role that is not in force" means for an assignment
> made in 2019 that the problem shows.

**The sharpest consequence, recorded because it is easy to miss.** Editing a role's
permissions takes effect **immediately for every holder** — no assignment touched, nobody
notified. `role.edit` is a bulk privilege change wearing the clothes of a settings screen, and
it is now marked as such. `role.assign` escalates one person; `role.edit` escalates everyone
holding the role. Neither implies the other.

**See:** [../data-model/05-authorization.md §3](../data-model/05-authorization.md#3-role--an-office),
[../appendix/permission-catalog.md §11](../appendix/permission-catalog.md#11-roles--proposed-seed-set).

---

## D-053 — A role is valid always; only its assignment is temporal

**Status:** decided (from your answer)
**Date:** refinement round 4
**Amends:** [D-052](#d-052--roles-are-runtime-data-the-seed-set-is-not-a-specification)

**Decision.** `role` has **no `valid_from` / `valid_to`**. A role is valid all the time, for as
long as the row exists. The only period in the picture is
`role_assignment.valid_from` / `valid_to` — who held it, and from when to when.

**Why.** Your answer: *"The roles should be valid all the time, but their assignment to people
shouldn't."*

D-052 had just given `role` a period, on the reasoning that retiring a role is a neat way to
abolish one in a single act. That was wrong, and the reason is worth recording because it is
not obvious until you push on it: **a role is a definition, and a definition does not come into
and out of force.** "What did `unit_leader` grant?" has one answer, and it is the same answer
for every date. What varies is *who held it*, which is what `role_assignment` records.

The proposed retirement also creates a question with no good answer. If a role has a period and
an assignment does not, then an assignment from 2019 rests on a role that is "not in force" —
so was that person a leader in 2019? The honest answers are either "yes, and the role's period
is irrelevant" (in which case the role's period never did anything) or "who knows" (in which
case the design has damaged its own history). Making the role permanently valid avoids the
question entirely.

**What this removes.** The whole retirement mechanism D-052 introduced:

| Removed | Replaced by |
|---|---|
| `role.valid_from`, `role.valid_to`, `ck_role_period`, `ix_role_current` | nothing — the columns are gone |
| `role.retire` permission | `role.unassign`, per assignment. A role nobody holds is unused, not retired |
| The resolver's check on the role's period (channel 4) | nothing. Channel 4 already checks the *assignment's* period, which was always the load-bearing one |
| `uq_role_code_current` (partial unique, so retired codes could be reused) | `code TEXT NOT NULL UNIQUE` — plain, because codes are never in competition |
| Integrity check 17 (roles expiring while held) | Reformulated as check 17 (unused roles) — a glance, not a warning |

**What this keeps from D-052.** Roles are still runtime data: created, edited, assigned and —
if never assigned — deleted. `is_system` still guard-rails deletion. `role` and
`role_permission` are still audited, because `role.edit` still changes effective permissions
for every holder at once. The `BEFORE DELETE` trigger stays.

**The consequence worth carrying forward.** Because a role never expires, the **only** thing
that ends authority is the assignment ending. That puts the entire weight on
`role_assignment.valid_to`, which is exactly where the design already wanted it — and it is why
the open-ended assignment is called the classic access failure
([data-model/05 §4](../data-model/05-authorization.md#nothing-forces-a-holder-row-to-end-and-the-report-is-the-control)).
A role-based permission now has no expiry of its own; it is the assignment or nothing.

**See:** [../data-model/05-authorization.md §3](../data-model/05-authorization.md#3-role--an-office),
[../appendix/permission-catalog.md §7](../appendix/permission-catalog.md#7-permissions-administration).

---

## D-054 — The sub-unit vocabulary is not seeded; the organization defines its own types

**Status:** decided (from your answer)
**Date:** refinement round 4

**Superseded by [D-097](round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row): there is no unit-type vocabulary left to seed or to withhold.** 'The
organization defines its own labels and the platform ships none' transfers intact to `person_group` and
`role`, where it remains the rule.

**Amends:** [D-008](round-01a.md#d-008--organizations-units-are-one-self-referencing-table-with-configurable-types)
in spirit; the self-referencing table is untouched

**Decision.** The unit-type seed data contains **exactly one row**: the root. No sub-unit
types are seeded at all. `org_unit_type` is **runtime data**, like `role`
([D-052](#d-052--roles-are-runtime-data-the-seed-set-is-not-a-specification)): the
organization creates the types it uses, renames them, and adds new ones as its structure
changes.

**Why.** Your answer: *"Seed only the root."*

`pack`/`group`/`team` was a placeholder, and it was the last thing in the schema that was
comfortably wrong — three invented words that would have read as a specification to anyone
implementing the system. The deeper reason to remove rather than correct it: **the
organization's own vocabulary is not knowable at specification time**, and guessing it
badly is worse than not guessing. This is the same argument as D-052 applied to units. The
retired `national`/`region`/`district` ladder ([D-035](round-02-03.md#d-035--one-root-unit-all-sub-units-nest-arbitrarily-beneath-it))
was a guess; so was its replacement.

**Consequence: nesting is entirely permissive.** `org_unit_type_rule` exists and is
seeded with nothing, so any type may sit under any other — including under the root — until
the organization states a rule. This was already true with the placeholder
([data-model/02 §10](../data-model/02-organization.md#7-seed-data)); it is now true with no
ambiguity about *which* types the permissiveness applies to. A new type is usable the moment
it is created.

**Consequence: the root type is special and must be seeded.** The `organization` row stays,
because exactly one unit must have `parent_unit_id IS NULL`
([D-035](round-02-03.md#d-035--one-root-unit-all-sub-units-nest-arbitrarily-beneath-it)) and that unit
needs a type. It also carries the property that matters: `allows_minors = false` on the root
type, since no minor belongs to "The Organization" as a *unit* — minors hold memberships and
sub-unit participation.

> **What this means for every example in these docs.** The words `pack`, `troop`, `section`
> and `group` still appear throughout the documentation as *illustration* — "a pack has its
> own roster" is how the prose explains a self-governing sub-unit. They are not types the
> system ships with. Read them as "some sub-unit type the organization has defined", the same
> way `unit_leader` in §11 of the permission catalog is a role the organization may not have.

**What this removes.** The three placeholder rows (`pack`, `group`, `team`) and the
"PLACEHOLDER" note that graded them. Nothing else: no columns, no constraints, no checks. The
change is confined to [data-model/02 §10](../data-model/02-organization.md#7-seed-data).

**See:** [../data-model/02-organization.md §10](../data-model/02-organization.md#7-seed-data),
[../domain/04-organization-structure.md §1–2](../domain/04-organization-structure.md#1-the-organization-is-one-unit-and-the-unit-is-a-scope).

---

## D-055 — The permission catalog is deliberately comprehensive and granular

**Status:** decided (from your answer)
**Date:** refinement round 4
**Amends:** [D-030](round-01b.md#d-030--finer-permissions-will-be-added-incrementally)

**Decision.** The permission catalog is **large and granular on purpose**, and it stays that
way. It is a *menu* from which administrators assign people only what they actually need —
not a checklist every deployment is expected to use in full. Adding a permission remains one
row plus its `permission_level` rows ([D-007](round-01a.md#d-007--every-resource-has-an-admin-level-that-subsumes-narrower-ones--reversed)),
and further permissions will arrive with the modules not yet specified (events, documents,
communication, reporting).

**Why.** Your answer, in full: *"The permissions will be added by the additional modules I am
yet to specify. It is good, that the list is large and granular so that the admins can assign
people only the permissions they actually need."*

This settles **F-1**, and it settles it in the opposite direction from the roles question.
The two are not symmetrical and it is worth saying why, because the asymmetry looks like an
inconsistency:

| | Roles | Permissions |
|---|---|---|
| What it is | A *grouping* an organization invents | A *capability* the code implements |
| Who defines it | The organization, at runtime | The system, at build time |
| Why | Nobody can guess your vocabulary | You cannot assign a power that is not expressible |

A permission is not a preference. `membership.terminate` exists because the *code* has a
terminate operation; an organization that never expels anyone simply never grants it. A role
is the opposite: `unit_leader` is only meaningful because someone in this organization chose
that word. So a comprehensive permission catalog costs nothing but rows, while a comprehensive
role list would be a specification pretending to be data.

**The sharp edge.** Granularity is what makes least-privilege possible, so it is load-bearing
rather than decorative — but **`.admin` subsumption means a new permission is
retroactively held by everyone with the namespace's `.admin`.** Split a broad permission in
two and an existing holder of the `.admin` gains both halves without an assignment being
written. That is the intended behaviour ([D-007](round-01a.md#d-007--every-resource-has-an-admin-level-that-subsumes-narrower-ones--reversed)),
and it is also why `role.edit` is marked 🔒🔒: the catalog's granularity only helps if the
grants are actually narrow.

**What this does not settle.** The catalog's *contents* remain open to revision as the
unbuilt modules land — this decision fixes the **disposition** (comprehensive, granular,
menu-like), not the exact 90 rows. `permission.edit` exists for later pruning, and
[appendix/permission-catalog.md §12](../appendix/permission-catalog.md#12-open-issues) tracks
what is still being decided.

**See:** [../appendix/permission-catalog.md](../appendix/permission-catalog.md),
[../open-questions.md](../open-questions.md) F-1.

---

## D-056 — The legacy import expects a large corpus with legacy member numbers

**Status:** decided (from your answer)
**Date:** refinement round 4

**Decision.** The import is designed for a **substantial** historical corpus — thousands of
records, not hundreds — and the old records **carry a legacy member number**. That number is
imported into `person_identifier` with `scheme = 'legacy'`
([data-model/01 §7](../data-model/01-identity.md#7-person_identifier)).

**Why.** Your answer: *"Large, with legacy member numbers."*

This is the favourable case for [D-004](round-01a.md#d-004--no-automatic-merging-ever), and it materially
changes what the import has to be:

| | If there were no numbers | With legacy numbers |
|---|---|---|
| Matching | Name + birth date + address, probabilistic, review-heavy | Exact key when the number is present; heuristics only for backfilling it |
| Review burden | Every match needs a human (D-004 assumed this) | Only the unmatched remainder does |
| Confidence | "Probably the same person" | "Same number, same person" |

**The consequence for the review design.** D-004's "no automatic merging, ever" was costed on
the assumption that review was the bottleneck and the corpus was small enough to review by
hand. With thousands of rows,"review everything" is no longer feasible, and the honest
position is that **the number-bearing rows are the trustworthy set and the rest is a work
queue**. The number does the work the human would have done; the human handles the rows the
number cannot resolve. This is a *strengthening* of D-004, not a weakening — the rule is
unchanged, but the input is better, so the rule is cheaper to obey.

**What must hold for this to work.** The legacy number must be imported **verbatim and never
reissued**. `person_identifier` is already the right home: it records a scheme and a value
with a period, so a second numbering era can coexist with the first. The check that matters
is that no legacy number is ever assigned to two people — worth an integrity check on the
`(scheme, value)` uniqueness, which the table's index already provides.

**The part that gets harder, not easier.** Volume and numbers make *identity* resolution
reliable, but they do nothing for the **membership-vs-participation** question raised by
[D-041](round-02-03.md#d-041--belonging-to-a-sub-unit-is-a-participation-record-not-a-membership). At this
scale, a 1998 roster almost certainly records *which unit someone attended* and not *whether
their fee was paid*, and the import must decide per row which of the two it becomes. The safe
default — **participation, unless there is payment evidence** — matters more at thousands of
rows than at hundreds, because the failure mode compounds: an inferred open-ended `membership`
would make every 2003 roster member a *current* member today through the gate
([D-039](round-02-03.md#d-039--member-permissions-require-a-current-paid-membership)).

**Not settled here:** the exact volume, the format, and the year range — those are operational
inputs the import batch will carry. B-1 stays open for the sample, but the *shape* of the
answer is now known.

**See:** [../data-model/06-audit-and-import.md](../data-model/06-audit-and-import.md),
[../domain/03-identity-and-legacy.md](../domain/03-identity-and-legacy.md),
[../open-questions.md](../open-questions.md) B-1.

---

## D-057 — `household` is removed

**Status:** decided (from your answer)
**Date:** refinement round 4
**Supersedes:** [D-019](round-01b.md#d-019--household-membership-grants-no-access) — *the table it described
is gone, but the principle it stated is not, and that is deliberate*. **Amends:**
[D-037](round-02-03.md#d-037--exactly-one-membership-type-the-fee-is-flat-and-per-person)

**Decision.** The `household` and `household_member` tables are **removed**, along with
`fee_obligation.household_id`, its CHECK arm, and `ix_obligation_household`. A person's
address is a `person_contact` row of type `postal` —
[data-model/01 §6](../data-model/01-identity.md#6-person_contact) — which already exists,
already keeps history, and already carries a `purpose` (`'billing'`) that the permission
model can distinguish. Same-address matching for the legacy import becomes a **query over
`person_contact`**, not a maintained table.

**Why.** Your answer: *"Drop household entirely."*

D-037 had already removed the load-bearing half: the fee is flat and per person, so there is
no per-family price for a household to hold. What remained was two conveniences — "one invoice
per household" and "which children lived at this address in 2003?" — and both are served by
tables that must exist anyway:

- **The invoice.** `person_contact` with `purpose = 'billing'` is where a billing address
  belongs. A household table was duplicating it under a different key, and the duplication
  had already gone stale: `household.postal_address` was documented as *"denormalised from the
  billing contact's primary postal contact"*, which is a copy with no trigger keeping it true.
- **The 2003 address question.** `person_contact` is temporal (`valid_from` / `valid_to`,
  *"Addresses change; history is required"*). So "who lived at this address in 2003?" is
  answered from the contacts table directly — and more honestly, because it asks about the
  address a *person* had, rather than requiring that someone first grouped those people into
  a household row that has itself since been renamed or split.

**The one thing genuinely lost.** A household is a *group* with a name and its own lifetime,
and `person_contact` records addresses per person. Two people at one address are related by a
query, not by a row — so there is nowhere to hang "the Novák family" as a first-class thing,
and no `valid_from` for the *grouping*. Accepted, because no feature was using it: nothing set
`fee_obligation.household_id`, and the display-name use (`household.name`) has no consumer in
the design.

**What this does not change.** The safeguarding property D-019 was written to protect survives
intact, and this is the point worth checking before deleting anything: **being at the same
address still grants no access.** It never came from the household table in the first place —
all access comes from `guardianship` + `guardianship_permission`
([D-020](round-01b.md#d-020--guardian-permissions-are-scoped-to-the-guardianship-row)). Removing a table
that granted nothing cannot grant anything. The old D-019 entry stays in the log, marked
superseded, because "why does living together not imply access?" is a question that will be
asked again.

**Also removed with it:** integrity check 7 (households with no address and no billing
contact), which has nothing left to check; the `household` bullet in
[data-model/04 §7](../domain/02-actors.md#7-open-issues); and D-9 in
[open-questions.md](../open-questions.md).

**See:** [../data-model/04-relationships.md](../data-model/04-relationships.md),
[../data-model/07-finance.md §2](../data-model/07-finance.md#2-minimal-provisional-shape).

---
