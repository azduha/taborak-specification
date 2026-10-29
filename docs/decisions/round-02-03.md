# Decision Log — Refinement rounds 2 and 3 (D-031 … D-046)

> The first answers to the open questions: no downward inheritance, deny absolute, one root unit, one membership type, the fee and its renewal window, audiences as grantees.

[The founding decisions (D-016 … D-030) ←](round-01b.md) | [All decisions](index.md) | [Refinement round 4 (D-047 … D-057) →](round-04.md)

---

## D-031 — No downward inheritance of authority; `scope_exposure` is the only crossing

**Status:** decided
**Date:** refinement round 2
**Reverses:** [D-015](round-01a.md#d-015--authority-inherits-downward-through-the-unit-hierarchy--reversed)

**Decision.** Authority is **settled at the scope where it is granted** and never inherited
downward. A role assigned over a district does not cover the troops in it. The permission
resolver performs **no ancestor walk** — `unit_ancestors()` must not appear in `can()`,
`grant_satisfies()`, or `can_act_for_dependent()`, and integrity check 13 is a CI assertion
that this stays true.

Authority crosses **downward** through exactly one mechanism: a `scope_exposure` row,
written by the **unit granting coverage over itself**, naming a specific
`role_assignment` — not a role — with its own validity period and withdrawal trail. The
crossing is offered from below, never imposed from above.

**Why.** Your rule, stated twice: *"The organization itself should not be able to itself
decide permissions over the nested unit, it must come from the unit itself up. The only
exception is the system admin."* Downward inheritance violates it structurally, because a
single row written anywhere above a unit would silently decide authority inside it.

**The exception.** The `system_admin` flag is checked **before** the resolver runs and is
therefore outside this rule. It is scoped to the whole system, not to a unit, so it is not
a counterexample to "authority originates at the unit" — but it is all-or-nothing and
should be rare.

**See:** [../domain/06-authorization-model.md](../domain/06-authorization-model.md#2-scopes--the-unit-and-the-item),
[../data-model/05-authorization.md](../data-model/05-authorization.md#5-scope_exposure--deleted-by-d-097).

---

## D-032 — Deny is absolute; locality orders allows only

**Status:** decided
**Date:** refinement round 2
**Amends:** [D-013](round-01a.md#d-013--explicit-deny-revoked-is-checked-before-everything)

**Decision.** Two separate rules that were previously conflated into "local overrides
global":

1. **Deny is absolute and scope-independent.** An explicit `revoked` at *any* scope wins
   over everything, including a more specific allow, the `admin` level, ownership, and
   guardianship. The deny check does not walk ancestors — a deny is matched at the
   organization scope or at the exact same scope, and that is sufficient to be absolute.
2. **Locality orders allows.** Among allows, the most specific scope determines the
   *level*: item grant → unit grant (exact or exposed) → organization grant → role. First
   sufficient tier wins.

**Why.** "The local permission overrides the global one" is true for allows and dangerous
for denies. Court-ordered restrictions and safeguarding suspensions must not be
overridable by the accident of a grant being written closer to the item. Separating the
two rules keeps the local-override intuition where it is correct and removes the one case
where it is a safety failure.

**See:** [../domain/06-authorization-model.md](../domain/06-authorization-model.md#7-precedence),
[../data-model/05-authorization.md](../data-model/05-authorization.md#6-access_grant--the-per-item-layer).

---

## D-033 — Multiple people may occupy the same position

**Status:** decided
**Date:** refinement round 2

**Superseded by [D-100](round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape), along with the position module.** That more than one person may hold an
office at once survives as `role_holder` being a dated holder *row* rather than a column — the same
answer, given to a different table.

**Decision.** Position occupancy is many-to-one by default. `position.max_holders` is
`NULL` (**unlimited, the default**) or `N ≥ 1` for a genuinely single-holder position (a
chair). Overlap for the same person in the same position in the same unit is still
prevented by an exclusion constraint; the *holder limit* is enforced by the
`check_position_holder_limit()` trigger.

**Why.** Two co-leaders, three quartermasters, a shared secretary — the common case is
multi-occupancy, so the schema must not make it a workaround. Keeping `max_holders`
optional and defaulted to unlimited means the single-holder chair is the special case, not
the rule.

**Note.** Position is **not** authority ([D-005](round-01a.md#d-005--permissions-are-grants-never-derived-from-identity)).
Holding a position grants nothing by itself; `is_leadership` only *suggests* a
`role_assignment`.

**See:** [../data-model/02-organization.md](../data-model/02-organization.md#5-what-this-page-held-before-round-10),
[../domain/04-organization-structure.md](../domain/04-organization-structure.md#6-appointments).

---

## D-034 — The person record holds no deceased flag

**Status:** decided
**Date:** refinement round 2

**Decision.** There is no `deceased_at`, no `is_deceased`, and no person-level death
constraint anywhere in the model. Personhood ends when it ends; the organization does not
record it.

**Why.** Your instruction: *"Person does not need to hold the 'deceased' parameter, we do
not log that."* A death flag is also a data-protection liability (special-category data in
some jurisdictions) and a merge hazard — it would need to survive `person_merge` conflicts
that have no good resolution.

**Consequence.** "Deceased" now has exactly one encoding, and it is indirect: a membership
that ended, a `position_assignment` that ended, a guardianship that ended. Historical
records stay correct without it, because every participation is already a period
([D-002](round-01a.md#d-002--everything-temporal-is-a-period-never-a-boolean)).

---

## D-035 — One root unit; all sub-units nest arbitrarily beneath it

**Status:** decided (from your answer)
**Date:** refinement round 3

**Superseded by [D-097](round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row): there is one unit, and nothing nests, because there is no unit row to nest
underneath.**

**Decision.** There is **exactly one top-level unit: the organization itself.** Every other
unit is a sub-unit of it, nested to **arbitrary depth and in arbitrary combination** —
weekly meeting groups, smaller packs, sections, teams. The nesting is not a fixed ladder of
national → region → district → group → troop.

**Membership lives at the root.** People register and pay **at the organization**, and the
membership is theirs as a member of the organization. The sub-units do not hold
memberships; they hold *participation* ([D-041](#d-041--belonging-to-a-sub-unit-is-a-participation-record-not-a-membership))
and they are self-governing — their own events, their own local leadership, their own
roster.

**Why.** Your answer: *"The people are members of the main top-level unit. The smaller ones
are totally arbitrary and can be arbitrarily nested… they all answer to the main unit, the
people are mainly registered (and paid) under the top unit, but they can be also part of
the smaller packs, that can have their own events, local leadership and so on."*

**Consequence.** The single root was enforced structurally, not by convention — the statement of
the moment, kept as it was decided:

```sql
-- Exactly one unit may exist at the root.
CREATE UNIQUE INDEX uq_org_unit_single_root ON org_unit ((true))
    WHERE parent_unit_id IS NULL;
```

*The requirement now: at most one unit may have no parent, whatever emits the schema cannot emit
it, and the migration owes it — [02-organization §3](../data-model/02-organization.md#5-what-this-page-held-before-round-10),
via [data-model/00 §6a](../data-model/00-conventions.md#6a-who-enforces-an-invariant-now).*

**This largely dissolves the organization-wide-role problem (C-1).** That problem existed
because "the organization" and "the units holding the data" were assumed to be different
things. In this model they are the same: the root unit **owns** the person registry, the
memberships and the fees, so a treasurer or registrar working at the root is not reaching
into anything — that data is its own. What remains is a reporting question (may the root
*see* what happens in the packs?), not a permission-inheritance one.

The no-downward-inheritance rule ([D-031](#d-031--no-downward-inheritance-of-authority-scope_exposure-is-the-only-crossing))
still does real work in the other direction: the root cannot decide permissions *inside* a
pack, and a pack that wants the root's help must expose its scope.

**See:** [../domain/04-organization-structure.md](../domain/04-organization-structure.md),
[../data-model/02-organization.md](../data-model/02-organization.md#5-what-this-page-held-before-round-10).

---

## D-036 — Units cannot be reparented; a unit that moves is a new unit

**Status:** decided (from your answer)
**Date:** refinement round 3

**Superseded by [D-097](round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row) — there is no parent column left whose change could be refused.** This was
the design's only instance of an immutable column, so [F-10 shape 4](../open-questions.md#f-10--which-invariants-the-orm-cannot-express-and-who-writes-those)
lost its subject here, which is what that entry now records.

**Resolves:** C-2

**Decision.** `org_unit.parent_unit_id` is **immutable**. A unit never changes parent. If a
troop genuinely transfers from one group to another, the **old unit closes and a new unit
is created** under the new parent, the people are moved across, and the lineage is recorded
in `org_unit_relationship` with a `transferred_to` relationship.

**Why.** Your answer, to the question of whether a unit may be reparented: *"Not allowed at
all — a unit that moves is a new unit."*

**Consequence — a large simplification.** Because the parent never changes:

- The materialized `path`/`depth` **never needs a subtree cascade rewrite.** The existing
  "reparenting is rare and dangerous; make it a single named procedure" warning disappears
  along with the danger.
- **Historical reports cannot silently change.** "Who was in the 4th Troop in 2001?" keeps
  answering the same thing forever, because no unit's ancestry is ever edited.
- The denormalized path stays trustworthy without versioning, which was the main reason
  retroactive reparenting was expensive.

**Enforcement.** A trigger rejects any change to `parent_unit_id` on an existing row.
`org_unit.transferred_to_unit_id` (or the relationship row) records where the people went.

> **Amended after [D-072](round-06.md#d-072--the-documentation-carries-no-sql-the-schema-is-the-orms-job).**
> There is no trigger, and this is the one enforcement in this log that cannot be moved down a
> layer. `parent_unit_id` immutability is not expressible as a constraint — not because PostgreSQL
> lacks the feature an ORM fails to emit, but because *no* declarative constraint can talk about
> what a row used to be. So the rule now lives as a guard in the write path, and the record here
> has to be honest about what was lost on the way:
> This entry's original claim was that a trigger made reparenting unreachable from *any* client,
> including the legacy import. A write-path guard is reachable from exactly the clients the trigger
> was chosen to exclude. The
> compensations available are narrow and named in
> [open question F-10, shape 4](../open-questions.md#f-10--which-invariants-the-orm-cannot-express-and-who-writes-those):
> a single named repository operation for hierarchy writes, and a test that attempts the update.

**See:** [../data-model/02-organization.md](../data-model/02-organization.md#5-what-this-page-held-before-round-10).

---

## D-037 — Exactly one membership type; the fee is flat and per person

**Status:** decided (from your answer)
**Date:** refinement round 3
**Supersedes:** the `child`/`adult`/`counselor`/`honorary`/`lifetime` seed set

**Decision.** There is **one membership**: everyone who is a member is a `member`. The
yearly fee is **flat and per person** — it does not vary by age, by household, or by
whether the person is a child or an adult. Being a counselor or leader is a **position**
([D-033](#d-033--multiple-people-may-occupy-the-same-position)), never a membership type.

**Why.** Your answers: *"Only one for all, counselor is a position"*, and between one type
with an age-varying fee, two types, or one flat fee, *"One type, and the fee does not vary
by age either."*

**The table is kept, with one seeded row.** `membership_type` survives as a table rather
than collapsing into a constant, because the document's own principle is that vocabularies
are rows and not enums, and because a second type (an honorary or supporting membership) is
a plausible future that would otherwise require a migration. The cost is an FK that
currently always holds one value — an honest, small cost, recorded here rather than hidden.

**Consequence.** `membership.membership_type_id` becomes effectively constant, and the
overlap exclusion constraint is no longer scoped by type — see
[D-041](#d-041--belonging-to-a-sub-unit-is-a-participation-record-not-a-membership) and
[../data-model/03-membership.md](../data-model/03-membership.md#3-membership).

---

## D-038 — Membership is ageless

**Status:** decided (from your answer)
**Date:** refinement round 3
**Removes:** `membership_type.category`, `min_age`, `max_age`, and the age-out workflow

**Decision.** **Age has no bearing on membership.** There is no age ceiling, no age floor, no
automatic age-out, and no `child`/`adult` category on a membership. A person may be a member
for life.

**Why.** Your answer: *"No age boundary at all — anyone can be a member forever."*

**What survives.** Age is still a **fact about a person** (`person.birth_date`) and it still
matters where the law makes it matter:

- **Guardianship** — a minor has a guardian, and consent is a guardian's act. This is a legal
  relationship, not a membership rule.
- **Safeguarding** — a unit may declare whether minors take part in it.
- **Position eligibility** — a scoutmaster may be required to be an adult.

What disappears is the machinery that made belonging *conditional on age*: the age-out
worklist, `max_age`-driven `completed` transitions, the child→adult transition workflow, and
the "is this person a child?" query.

**Retired questions.** D-3 (age-out timing), D-4 (child→adult transition) and D-5
(membership type vocabulary) are resolved by this decision and by
[D-037](#d-037--exactly-one-membership-type-the-fee-is-flat-and-per-person).

---

## D-039 — Member permissions require a current paid membership

**Status:** decided (from your answer)
**Date:** refinement round 3
**Resolves:** A-2

**Decision.** The permission resolver **does** evaluate membership state. Authority held
through a role is honoured **only while the holder has a current membership**, with exactly
two carve-outs:

| Channel / case | Membership required? |
|---|---|
| Roles with `role.requires_membership = true` | **Yes** — no current membership, no access |
| Roles with `requires_membership = false` (appointed counselors, local leaders) | **No** — an adult volunteer keeps their leadership access with an unpaid fee |
| Guardianship (`dependent.*`) | **No** — guardianship comes from a legal relationship, not a membership |
| Ownership (your own record) | **No** — otherwise a lapse would lock a person out of the screen they renew on |

**Why.** Your answer: *"Yes — permissions conditioned on membership"*, and on how far the
rule reaches: *"Everything except guardianship and adult volunteers."* The third option —
locking an unpaid person out of even their own profile — was explicitly not chosen, which is
why ownership joins guardianship as exempt.

**The cost, stated plainly.** This is a real coupling and it is worth naming rather than
discovering later:

- ~~**The cache must be invalidated on every membership transition**, including the yearly
  expiry sweep, which is a bulk event touching everyone at once. ~~ ~~The cache design must be
  built for this from the start, not retrofitted.~~ **The origin of a warning that was copied twice and read
  zero times.** This bullet is where the requirement was first written;
  [`data-model/03-membership.md` §6](../data-model/03-membership.md#6-membership-and-the-authorization-system)
  restated it in the round that moved the gate to `MEMBERS`, and **the two lists that
  [D-111](round-13.md#d-111--the-permission-cache-is-rebuilt-nightly-on-any-ruleset-change-and-on-request) drew three rounds
  later named every table except `membership`** — so the sentence existed in two files, in the module that had the
  coupling, while the boundary was drawn in the module that owned the cache.
  [D-114](round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation) deletes the obligation along with the cache and records both facts, because the useful lesson is the
  *copying*, not the requirement: **a dependency stated in prose at the far end of a coupling is not a constraint
  on the page that has to satisfy it.** `membership` is still read live by `MEMBERS`, so the coupling this bullet
  was afraid of is now the design rather than a hazard in it.
- **A lapse silently removes access.** That is the intent, but "why can't I see this?"
  becomes a question whose answer is a date, not a decision someone made.
- **`role.requires_membership` changes meaning** — from "reported, drives a worklist" to
  "enforced by the resolver". The "leaver with access" report remains useful, since it now
  detects roles that should have been closed rather than the mechanism doing the blocking.

**See:** [../domain/06-authorization-model.md](../domain/06-authorization-model.md#6-the-resolver),
[../data-model/05-authorization.md](../data-model/05c-access-log-and-resolver.md#10-the-resolver).

---

## D-040 — The fee expires yearly; a date-tracked renewal window replaces a grace status

**Status:** decided (from your answer)
**Date:** refinement round 3
**Resolves:** A-3, D-3 (grace modelling)

**Decision.** Membership activates **on payment**, and the fee is
**yearly**, expiring at a fixed organizational date (typically January). When it expires:

1. The membership **lapses** — the person is **not a member** and holds no member
   permissions from that date. There is no third "grace" status in the resolver.
2. A **renewal window** — a fixed period such as three months, tracked as **dates, not a
   status** — follows the expiry. During it the person may **renew without re-applying**.
3. A payment **inside the window opens the new membership period at the expiry date**, so the
   membership history shows continuous coverage with no gap and the person is not
   misclassified as a returning member.
4. A payment **after the window** opens a new membership at the payment date, and the gap is
   real. It still does not require a new application.

**The tension, named.** You described the grace period as existing *"for them to pay to stay
members"*, and separately confirmed that during it they are *"expired now, but they can
rejoin without re-applying."* Those pull in different directions on one point: whether the
person is a member during the window.

**This decision resolves it as: not a member during the window, but the record shows no gap
once they pay.** The alternative reading — genuinely continuing as a member through the
window — would mean a lapse is not detectable until the window closes, and would put a third
state into every permission check. If the organization would rather have the softer version,
it is a change to `membership.renewal_grace_days` and the renewal rule, not a rewrite.

**See:** [../domain/05-membership-lifecycle.md](../domain/05-membership-lifecycle.md#6-renewal-and-the-yearly-fee).

---

## D-041 — Belonging to a sub-unit is a participation record, not a membership

**Status:** decided (from your answer)
**Date:** refinement round 3

**Reversed as to the sub-unit by [D-097](round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row); kept as to the distinction by [D-098](round-10a.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority).** Being a member and
being on a group's roster are still two rows, with two lifetimes and two different permissions guarding
them. Only the right-hand side changed: it is a `person_group` now.

**Decision.** `unit_membership` is renamed **`unit_participation`** and reframed. A person
holds **exactly one membership** (at the root unit, paid yearly — [D-035](#d-035--one-root-unit-all-sub-units-nest-arbitrarily-beneath-it))
and **zero or more participation rows**, one per sub-unit they take part in.

**Why.** Your answer, to how the schema should record being "part of a smaller pack": *"A
participation record, separate from membership."* The rename matters because the old name
asserted something untrue — that belonging to a pack was a species of membership — and
"three memberships, three statuses, three fee questions" is exactly the ambiguity the answer
avoids.

**Consequence — the overlap constraint simplifies.** With one membership type
([D-037](#d-037--exactly-one-membership-type-the-fee-is-flat-and-per-person)), the exclusion
constraint drops `membership_type_id` and becomes a person-level invariant — quoted as decided, in
the form the constraint had at the time:

```sql
ALTER TABLE membership ADD CONSTRAINT ex_membership_no_overlap
    EXCLUDE USING gist (
        person_id WITH =,
        daterange(valid_from, valid_to, '[)') WITH &&
    )
    WHERE (status IN ('pending_payment','active','suspended'));
```

*The requirement now: **one person, one open membership, ever**, where "open" means those three
statuses — a no-overlap rule over a period, which is exactly the shape an ORM will not generate
([open question F-10 shape 1](../open-questions.md#f-10--which-invariants-the-orm-cannot-express-and-who-writes-those));
the temporal pattern is in [00-conventions §6](../data-model/00-conventions.md#6-the-temporal-pattern)
and the check that catches a bypass is 1b in
[03-membership §7](../data-model/03-membership.md#7-integrity-checks).*

**"Am I a paid-up member?" is now one row, one status, one date.** That question was the
reason the type was in the constraint.

**A root participation row is created with the membership**, so "everyone in unit X" is one
uniform query whether X is the organization or a Thursday-evening pack.

**See:** [../data-model/03-membership.md](../data-model/03-membership.md#5-unit_participation--deleted-by-d-097).

---

## D-042 — Grants may target audiences, not only individuals

**Status:** decided (from your answer)
**Date:** refinement round 3

**Decision.** A grant can name an **audience** instead of a person. Two kinds:

| Kind | Evaluated | Examples |
|---|---|---|
| **Built-in audiences** | By a rule the resolver knows, not by a stored list | `everyone`, `all_members`, the guardians of a given person, the participants of a given unit, the leaders of a given unit |
| **Named groups** | From a stored membership list someone administers | "the summer camp kitchen crew" |

`access_grant` therefore carries `person_id` **or** `audience_id`, never both.

**Why.** This came out of your answer about `scope_exposure`: *"If the unit wants to expose
something (a single event eg), they set the permissions to that event for 'everyone' or a
group of people to expose it to them."* The design had **no way to express that** — every
grant named a person — which is a genuine gap your answer surfaced rather than a detail.

**Built-in audiences are rules, not lists**, and that is the important property: a new pack
member automatically receives what the pack was granted, with no rows to maintain and no
stale-group problem. Named groups are the escape hatch, and they carry that problem
knowingly — nobody ever removes anyone from a group.

**See:** [../data-model/05-authorization.md](../data-model/05a-audience-and-grammar.md#8-audience--grants-that-target-a-set-of-people).

---

## D-043 — No background checks are recorded in this system

**Status:** decided (from your answer)
**Date:** refinement round 3
**Resolves:** A-4

**Decision.** The system records **no background checks**: no `person_identifier` scheme, no
`requires_background_check` flag on membership types, positions or roles, no expiry report,
no daily alert, and no `person.background_check.*` permissions.

**Why.** Your answer: *"We do not have any background checks in place, at least not ones
handled by the system."*

**What this removes.** The whole `person.background_check.*` permission pair, the
`background_check` requirement code, the `background_check_officer` seed role, the
"leader with expired clearance" report, and one of the two reasons
`position.requires_adult_membership` existed.

**If that changes**, the cleanest route is a `requirement_code` row plus an
`expires_at`-bearing record — the machinery this decision removes was general enough to
carry it. Recorded here so re-adding it is a deliberate act with a visible history rather
than a surprise.

---

## D-044 — Nothing gates a membership request except identity and payment

**Status:** decided (from your answer)
**Date:** refinement round 3

**Decision.** A membership request is accepted on **identity and payment alone**. The
`requirement_code` and `membership_request_requirement` tables are **removed** — there is no
blocking checklist, no evidence collection, and no waiver workflow.

**Why.** Your answer, asked what a request must contain to be accepted: *"Just identity and
the fee — nothing to verify."* The option to keep the mechanism as empty infrastructure was
offered and not taken.

**What survives.** **Guardian consent for a minor's account** is unaffected — that is a
guardianship-layer fact ([D-005](round-01a.md#d-005--permissions-are-grants-never-derived-from-identity)),
not a membership requirement, and its removal here does not weaken it.

---

## D-045 — The bulk scope-exposure tool is removed

**Status:** decided (from your answer)
**Date:** refinement round 3

**Decision.** The bulk exposure tool is **removed**, along with the `bulk:<batch>` reason
marker, the bulk branch in `check_exposure_direction()`, and integrity check 12 that listed
bulk rows for review. **Every `scope_exposure` row is written by the unit it covers.**

**Why.** Two answers, in sequence. Asked whether the tool should exist, you said you did not
know what it meant and described instead how you actually think about exposure — *"they set
the permissions to that event for 'everyone' or a group of people"*. Once **audiences**
([D-042](#d-042--grants-may-target-audiences-not-only-individuals)) were added to cover that
case, the question was put again and your answer was: *"Not needed if audiences are added."*

**Consequence — the rule is now absolute.** There is no sanctioned bypass, no marker prefix,
no exception to explain. `scope.expose` held **at the covered unit** is the only way a row is
created, and it is enforced by the same predicate at three layers
([domain/06 §2](../domain/06-authorization-model.md#2-scopes--the-unit-and-the-item)).

**This is a genuine simplification**, and it removes the design's most uncomfortable
paragraph — the one arguing that the rule had to bend for scale.

---

## D-046 — Guardianship defaults depend on how the guardianship was created

**Status:** decided (from your answer)
**Date:** refinement round 3
**Resolves:** E-1

**Decision.** The default permission set granted when a guardianship is created depends on
its `source`:

| How it arose | Default |
|---|---|
| A parent **self-registers their own child** | **Full authority** — `dependent.admin` |
| Recorded **manually** by staff, or from a court order | **Set at creation** — the person creating it chooses the set |

**Why.** Your answer: *"A parent self registering their own child gets full access, if it is
created manually later, it can be set on creation."*

**Consequence.** `guardianship.source` and `guardianship_permission.grant_reason` are what
make the difference auditable — the same word ("guardian") now means two different default
scopes depending on paperwork, and the record says which was chosen and why.

---
