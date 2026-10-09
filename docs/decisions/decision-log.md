# Decision Log

Decisions taken, with the reasoning that produced them. Recorded so they are not
re-litigated from scratch — and so that when a decision is reversed, the reason for the
original choice is visible.

**Status values:** `decided` — settled, schema reflects it. `proposed` — recommended,
awaiting your confirmation. `assumption` — taken by default, stated in italics in the
docs, easily reversed. `reversed` — no longer in force; the entry is kept, marked, and the
replacement is linked. Reversals are also listed together at the
[bottom](#reversed-decisions).

---

## D-001 — Person, account, and membership are three separate things

**Status:** decided (from your requirements)
**Date:** initial design

**Decision.** `person` holds identity only. `account` holds login credentials and is
optional. `membership` holds participation and is temporal. No member flags, no
child/adult flag, no `is_member` on `person`.

**Why.** You described a person who was a member 1990–2010 and again from 2024. That is one
person and two membership periods. Any design with `person.is_member` cannot express it,
cannot answer "who was in Troop 12 in 1998?", and silently destroys 36 years of history
the first time someone corrects a record.

**Consequence.** Membership questions are always date-qualified:
[../data-model/03-membership.md](../data-model/03-membership.md) provides `is_current_member()`,
`was_member_on()`, `current_member_category()`, and `membership_years()`.

---

## D-002 — Everything temporal is a period, never a boolean

**Status:** decided
**Date:** initial design

**Decision.** `valid_from` / `valid_to` with `valid_to IS NULL` meaning "still true", and
half-open `[from, to)` ranges. Overlap prevented by `EXCLUDE USING gist` constraints.

**Why.** Required by D-001, guardianship expiry, unit membership history, role terms, and
grant expiry. Enforcing overlap in the database rather than in application code is
essential: an import script, a manual SQL fix, or a future API will bypass application
validation.

**Consequence.** Requires PostgreSQL with `btree_gist`. On MySQL, the guarantee weakens to
triggers plus nightly checks — a materially weaker invariant to be recorded as an accepted
risk if that platform is chosen.

---

## D-003 — Never hard-delete; merges leave tombstones

**Status:** decided
**Date:** initial design

**Decision.** No `deleted_at`, no business-data `DELETE`, no `ON DELETE CASCADE` anywhere.
Ended periods get `valid_to`. Merged people keep their row with `merged_into_person_id`.
Erasure is redaction, not deletion.

**Why.** "Who attended this camp in 2003?" must resolve forever. A hard delete breaks the
safeguarding record. Merges must be reversible because bad matches are inevitable.

**Consequence.** Every query must exclude merged and redacted rows — hence the `v_person`
view and `resolve_person()` function, which exist so application code cannot forget.

---

## D-004 — No automatic merging, ever

**Status:** assumption ⚠ *confirm or overrule*

**Decision.** Every identity match, however strong, requires human confirmation. There is
no confidence threshold above which the system merges on its own.

**Why.** A false-positive merge is a privacy incident: the survivor gains the absorbed
person's permissions, and two people's records become one. A false negative is an
inconvenience someone can fix. The asymmetry justifies the cost.

**Reverse if:** the volume of historical data makes manual review infeasible. If so, the
high-confidence tier should be narrow (exact external identifier match only) and its
application must be logged and alerted.

**See:** [../domain/03-identity-and-legacy.md](../domain/03-identity-and-legacy.md#4-match-signals)

---

## D-005 — Permissions are grants, never derived from identity

**Status:** decided (from your answer)
**Date:** initial design

**Decision.** Being a parent, a member, a leader, or a long-serving volunteer grants
nothing. Every capability comes from an explicit, dated, revocable row.

You answered that **both read and write access should be explicit** for caretakers.

**Why.** The classic failure: a relationship ends (custody changes, a leader steps down) but
access persists, because it was implied rather than granted. Explicit grants make access
auditable and revocable.

**Consequence.** A `guardianship` row alone grants nothing; `guardianship_permission` rows
do. A `position_assignment` alone grants nothing; `role_assignment` does.

---

## D-006 — Per-item permissions are capabilities on the item

**Status:** decided (from your answer)
**Date:** initial design

**Decision.** You clarified that "per-item permission" means *capability on that item* —
"person X may act on item Y" — not a participation record and not an eligibility gate.
Implemented as `access_grant` with an ordered `level`
(`revoked` < `view` < `contribute` < `manage` < `admin`).

**Why.** Isolates authorization from participation (D-005) and from eligibility, which will
be a separate concept when events are specified.

**Consequence.** `permission_level` connects permission codes to the level they require,
so one grant level serves many permissions without a hardcoded mapping.

---

## D-007 — Every resource has an `admin` level that subsumes narrower ones ⚠ **REVERSED**

**Status:** ~~decided~~ **reversed by [D-068](#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle)**
**Date:** initial design · reversed refinement round 5

> **Reversed.** The per-resource `<resource>.admin` *permissions* and the resolver's prefix
> match are gone. **The `admin` grant LEVEL (rank 40) is untouched** — this decision conflated
> the two, and the collision is what made it hard to reverse cleanly. See D-068.

**Decision.** Per your instruction, every grantable resource exposes `<resource>.admin`,
checked by prefix match, plus a single top-level `system.admin`.

**Why.** Without it, every new narrow permission requires updating every role that should
already have implied it — and someone will miss one, producing a permission that silently
is not granted. The prefix match makes new permissions automatically covered.

**Consequence.** The check is computed, not mapped. `person.admin` etc. are real
permission rows so they appear in the role editor.

---

## D-008 — Organizations units are one self-referencing table with configurable types

**Status:** decided (from your answer)
**Date:** initial design

**Decision.** One `org_unit` table with `parent_unit_id` self-reference and a configurable
`org_unit_type`. Hierarchy via materialized `path` plus recursive CTE functions.

**Why.** You confirmed sub-units are core. Depth is a data question, not a schema question —
a 40-year-old organization has changed its levels. One table means "everyone in this
district" is one recursive query rather than a hand-written union.

**Consequence.** Nesting rules live in `org_unit_type_rule` plus a trigger. Units that
closed remain queryable forever.

---

## D-009 — Unit membership links to `person`, not to `membership`

**Status:** decided
**Date:** initial design

**Decision.** `unit_membership.person_id → person.id`, deliberately not `membership_id`.

**Why.** 1990s rosters have a unit and a year but no membership workflow. Linking to
`membership` would make that data unrepresentable and lose the whole historical dataset.

**Cost.** Nothing enforces that a person with a unit membership holds an organization
membership. Mitigated by application validation plus a nightly check
([../data-model/03-membership.md](../data-model/03-membership.md#7-integrity-checks), check 1).

---

## D-010 — Role assignments and access grants share a scope model and a resolver

**Status:** decided
**Date:** initial design

**Decision.** `role_assignment` and `access_grant` are separate tables but share
`scope_type`, the level model, and one `can()` function. Four authority channels
(ownership, guardianship, item grants, roles), each dispatching from the permission's
namespace, with an absolute deny check in front of them.

**Amended** (see D-031, D-032): the resolver's allow channels are now ordered by
**locality** rather than by channel, and the deny channel is scope-independent.

**Why.** They are the same idea at two granularities — authority for a period, in a scope,
granted by someone. A single resolver prevents the divergence that makes the weaker of two
implementations an exploit. Separate tables because their lifetimes, granters, and
revocation semantics genuinely differ.

---

## D-011 — `scope_id` on `access_grant` is polymorphic, with no foreign key

**Status:** assumption ⚠ *a real fork — worth a deliberate decision*

**Decision.** `access_grant.scope_type` + `scope_id` with no FK. Validated by
`grant_scope_type` plus nightly orphan checks.

**Why.** Most of this system is unspecified (events, documents, and more). Polymorphism
makes each new grantable type a config row rather than a schema migration.

**Cost.** No referential integrity. Mitigated by: `grant_scope_type` FK, application-level
grant closure on item delete, nightly orphan detection, non-reused `BIGINT` ids.

**Alternative.** A `grantable_item(id, item_type)` supertable referenced by every grantable
entity — full integrity, heavier design, migration per new type. **Overrule this if you
prefer integrity to flexibility.**

---

## D-012 — Status strings compare by rank, never lexicographically

**Status:** decided
**Date:** initial design

**Decision.** `access_level` is a lookup table with an integer `rank`. All level comparisons
use `rank`.

**Why.** `'admin' < 'contribute'` alphabetically. A string comparison silently inverts the
levels and makes the most powerful level the least. It throws no error and passes most
tests. This is the single most dangerous easy mistake in the design.

---

## D-013 — Explicit deny (`revoked`) is checked before everything

**Status:** decided
**Date:** initial design

**Decision.** Resolver channel 0. A `revoked` grant overrides roles, item grants, and
ownership. In the guardianship channel, `is_granted = false` overrides a granted
`dependent.admin`.

**Why.** Without an explicit deny level there is no way to express "this person must not
see this event" or "this guardian may not see medical records" when a broader grant would
otherwise allow it. Court-ordered restrictions must not be overridable by a broader grant.

---

## D-014 — Roles do not inherit from other roles

**Status:** decided
**Date:** initial design

**Decision.** No role-to-role inheritance. If `unit_leader` should have `assistant_leader`
permissions, they are granted explicitly.

**Why.** Inheritance chains produce authorization answers nobody can predict by reading the
configuration. Predictability matters more than configuration economy in an authorization
system — the people who must reason about it are volunteers, not engineers.

**Note:** unit *scope* inheritance was a separate axis. It was **reversed** — see D-031.
That reversal does not disturb this decision: role-to-role inheritance remains prohibited
for the same reason it always was.

---

## D-015 — Authority inherits downward through the unit hierarchy ⚠ **REVERSED**

**Status:** **reversed by [D-031](#d-031--no-downward-inheritance-of-authority-scope_exposure-is-the-only-crossing)**
**Date:** initial design

**Decision (original).** A role assigned at a unit covers that unit and all descendants. A
district treasurer can act on troops within the district.

**Why (original).** Matches how organizations actually work — a district officer has
district-wide responsibility.

**Why it is reversed.** Your rule: *"The organization itself should not be able to itself
decide permissions over the nested unit, it must come from the unit itself up. The only
exception is the system admin."* Downward inheritance makes every unit's authority
decidable from above — a role written at the district level silently reaches into troops
that never agreed to it. That is exactly the direction you excluded. The replacement is
`scope_exposure`, where the **unit** grants coverage over itself.

**Consequence, accepted.** Organization-wide operational roles (national registrar,
national treasurer) no longer work by assigning a role high in the tree. Tracked as the
reworked [C-1](../open-questions.md).

---

## D-016 — Renewal opens a new membership row, not an extended `valid_to`

**Status:** decided
**Date:** initial design

**Decision.** Shape A. A renewal closes the prior membership and opens a new one, linked by
`renewed_from_membership_id`.

**Why.** Extending `valid_to` destroys the ability to see that someone skipped a year and
re-joined — the most commonly asked question about renewals — and makes retroactive
corrections ambiguous. You asked for history preserved across decades.

**Cost.** More rows; queries must handle a chain. The self-reference makes the chain
explicit rather than inferred.

---

## D-017 — Requests are separate from memberships

**Status:** decided
**Date:** initial design

**Decision.** `membership_request` is its own table. A rejected request produces no
membership row.

**Why.** A rejected request must not pollute member listings; a person may apply several
times; review data has no meaning on a membership; submitting is self-service while
reviewing is a staff capability.

---

## D-018 — `membership_request` records the subject and the submitter separately

**Status:** decided (from your answer)
**Date:** initial design

**Decision.** `person_id` is the person who would become a member (the child).
`submitted_by_person_id` is who submitted it (the parent).

**Why.** Collapsing them — the common shortcut — makes it impossible to answer "who applied
for this child?" and falsely attributes the parent's action to the child. You confirmed
caretakers act on behalf, which requires both parties to be recorded.

**Consequence.** The same pattern applies to `payment.paid_by_person_id` /
`payment.on_behalf_of` and to `access_log.on_behalf`.

---

## D-019 — Household membership grants no access

**Status:** ⚠ **PARTLY SUPERSEDED** — the `household` tables are gone
([D-057](#d-057--household-is-removed)), so there is no household membership left to grant
anything. **The principle remains true and is the reason to keep this entry:** shared address
never implied access, the access never came from these tables, and it still does not.
**Date:** initial design

**Decision.** `household` exists for billing and address grouping only. Being in a
household grants no permission over any other member of it.

**Why.** A stepparent with no guardianship row has no access to the children's records. All
access comes from `guardianship` + `guardianship_permission`. This is a safeguarding
property, not an oversight.

---

## D-020 — Guardian permissions are scoped to the guardianship row

**Status:** decided (from your answer)
**Date:** initial design

**Decision.** `guardianship_permission.guardianship_id`, not the `(guardian, dependent)`
person pair.

**Why.** You answered that both read and write access must be explicit. Scoping to the pair
would let a guardianship ending and a new one beginning (a renewed court order) silently
retain all prior permissions. Scoping to the row forces a deliberate re-grant.

**Cost.** A re-granting step in a rare case. Accepted.

---

## D-021 — Health/medical access is separate from consent authority

**Status:** decided
**Date:** initial design

**Decision.** `dependent.medical.view` and `dependent.consent.give` are distinct
permissions.

**Why.** A parent who may consent to a camp is not necessarily a parent who may read a
medical file, and vice versa. Court orders frequently restrict one without the other.
Conflating them makes the common restriction inexpressible.

---

## D-022 — Lapsing and termination are different permissions

**Status:** decided
**Date:** initial design

**Decision.** `membership.lapse` (administrative, non-payment) and `membership.terminate`
(end for cause) are separate permissions, the latter held by very few.

**Why.** Conflating them means every volunteer who chases unpaid fees can expel a member.
Termination in a youth organization is frequently a safeguarding decision.

---

## D-023 — Nothing is auto-lapsed or auto-terminated

**Status:** ⚠ **partly superseded** by [D-040](#d-040--the-fee-expires-yearly-a-date-tracked-renewal-window-replaces-a-grace-status)
and [D-038](#d-038--membership-is-ageless)
**Date:** initial design
**Superseded in part by:** D-038 (age-out), D-040 (expiry), D-043 (background checks)

**Decision (as originally written).** The system produces worklists; humans act. Grace
periods absorb late payments. Age-out is driven by `membership_type.max_age` but the
transition is reviewed.

**Why.** Automatically removing a child's membership because a bank transfer was recorded
late is a real harm. Automation should stop short of the consequence.

### What survives, and what does not

The principle survives and is still the design's default: **for anything that is a
judgement, the system produces a worklist and a human decides.** Terminations for cause,
safeguarding removals, and guardianship expiry at majority
([D-024](#d-024--guardianship-does-not-auto-expire-at-majority--reversed)) all still work this way.

Two halves of the original text do not survive:

| Original claim | Now |
|---|---|
| "Grace periods absorb late payments" | The grace *status* is gone. There is a **renewal window** — dates, not a state ([D-040](#d-040--the-fee-expires-yearly-a-date-tracked-renewal-window-replaces-a-grace-status)). |
| "Age-out is driven by `membership_type.max_age`" | There is no `max_age` and no age-out. Membership is ageless ([D-038](#d-038--membership-is-ageless)). |

**The expiry is the one automatic transition.** D-040 resolves the tension the original
"why" names, and resolves it by removing the *decision* rather than the *automation*: the
fee covers a fixed period, the period ends on a date everyone already knows, and nobody
chooses anything. The late-bank-transfer case the original wording was protecting is
absorbed by the window's backdating rule instead. The reversal is recorded in full at
[../data-model/07-finance.md §4](../data-model/07-finance.md#4-how-this-connects-to-membership),
including the one case the window cannot absorb.

---

## D-024 — Guardianship does not auto-expire at majority ⚠ **REVERSED**

**Status:** ~~assumption~~ **reversed by [D-069](#d-069--guardianship-ends-when-a-person-ends-it-the-system-takes-no-position-on-majority)**
**Date:** initial design · reversed refinement round 5

> **Reversed — but not in the direction you might expect.** The alternative was *not*
> auto-expiry. D-024's sin was the review queue: still an automatic behaviour, still computing
> a majority date the system has no authority to assert. D-069 removes the queue *and* the
> date. The conclusion D-024 reached — do not silently strip access — is kept; the mechanism
> is withdrawn.

**Decision.** The system computes the candidate date and puts it on a review queue. Staff
close the row.

**Why.** In many jurisdictions a parent's authority over health and school records does not
end at 18, and thresholds vary. An automatic cutoff will silently strip legally valid
access.

---

## D-025 — Audit log redacts sensitive values before insert

**Status:** decided
**Date:** initial design

**Decision.** `audit_trigger` calls `redact_audit_values()` before writing. Free-text fields
that may contain personal data are redacted.

**Why.** An audit log that stores the data it audits is a second copy of sensitive data with
weaker access controls and longer retention. Redaction in a cleanup job is not sufficient —
the job might not run.

---

## D-026 — Two audit trails

**Status:** decided
**Date:** initial design

**Decision.** `access_log` (who accessed what, by what authority) and `audit_log` (field
values before/after) are separate tables.

**Why.** Different retention needs, query patterns, and access permissions. Merging them
produces a table too large to query and too sensitive to expose wholesale.

**Consequence.** `access_log.authorization_channel` + `authorization_ref_id` are what make
it an audit *trail* rather than a log — they answer "by what authority?", which is the
question asked in a dispute.

---

## D-027 — Legacy import is staged, reviewed, idempotent, and per-batch reversible

**Status:** decided (from your answer)
**Date:** initial design

**Decision.** Six stages (staging → parse → match → review → apply → log). Dry-run mode.
Deterministic `source_row_hash` for idempotency. Per-batch revert while no live data
references the imported rows, refusing rather than partially applying.

**Why.** You confirmed historical records must be imported. Import errors into a
four-decade dataset are expensive and often silent.

**Consequence.** Revert past the safe window is refused, not attempted — a "revert" that
orphans live references is worse than an honest refusal.

---

## D-028 — Imported memberships never get a NULL `valid_to`

**Status:** decided
**Date:** initial design

**Decision.** Imported rosters end at the end of the organizational year of the last roster
the person appears in, marked `data_confidence = 'low'`.

**Why.** A NULL `valid_to` makes a 1998 member a current member in 2026 — inflating the
member count and granting member privileges to people who left decades ago. This is the most
dangerous possible default.

---

## D-029 — Finance design is provisional and will be rewritten

**Status:** assumption / open
**Date:** initial design

**Decision.** [../data-model/07-finance.md](../data-model/07-finance.md) exists only so that
membership activation has a referent. Expect to rewrite it.

**What is likely right regardless:** `payment_allocation` as a many-to-many between payments
and obligations (a parent paying for three children in one transfer is the common case, not
an edge case), and `fee_schedule` with validity periods so historical amounts are
reproducible.

**See:** the twelve open questions in that document.

---

## D-030 — Finer permissions will be added incrementally

**Status:** decided
**Date:** initial design

**Decision.** The permission catalog in
[../appendix/permission-catalog.md](../appendix/permission-catalog.md) is a starting point.
Adding a permission is a data change (one row plus `permission_level` rows), not a schema
change.

**Why.** You asked for granularity and an `admin` fallback at every resource; the prefix-match
rule (D-007) means new permissions are automatically covered by existing `.admin` grants, so
granularity can be increased later without touching existing roles.

---

## D-031 — No downward inheritance of authority; `scope_exposure` is the only crossing

**Status:** decided
**Date:** refinement round 2
**Reverses:** [D-015](#d-015--authority-inherits-downward-through-the-unit-hierarchy--reversed)

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

**See:** [../domain/06-authorization-model.md](../domain/06-authorization-model.md#2-scope-authority--no-downward-inheritance),
[../data-model/05-authorization.md](../data-model/05-authorization.md#5-scope_exposure--how-a-unit-delegates-upward).

---

## D-032 — Deny is absolute; locality orders allows only

**Status:** decided
**Date:** refinement round 2
**Amends:** [D-013](#d-013--explicit-deny-revoked-is-checked-before-everything)

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

**Decision.** Position occupancy is many-to-one by default. `position.max_holders` is
`NULL` (**unlimited, the default**) or `N ≥ 1` for a genuinely single-holder position (a
chair). Overlap for the same person in the same position in the same unit is still
prevented by an exclusion constraint; the *holder limit* is enforced by the
`check_position_holder_limit()` trigger.

**Why.** Two co-leaders, three quartermasters, a shared secretary — the common case is
multi-occupancy, so the schema must not make it a workaround. Keeping `max_holders`
optional and defaulted to unlimited means the single-holder chair is the special case, not
the rule.

**Note.** Position is **not** authority ([D-005](#d-005--permissions-are-grants-never-derived-from-identity)).
Holding a position grants nothing by itself; `is_leadership` only *suggests* a
`role_assignment`.

**See:** [../data-model/02-organization.md](../data-model/02-organization.md#7-position-and-position_assignment),
[../domain/04-organization-structure.md](../domain/04-organization-structure.md#4-positions).

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
([D-002](#d-002--everything-temporal-is-a-period-never-a-boolean)).

---

## D-035 — One root unit; all sub-units nest arbitrarily beneath it

**Status:** decided (from your answer)
**Date:** refinement round 3

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

**Consequence.** The single root is enforced structurally, not by convention:

```sql
-- Exactly one unit may exist at the root.
CREATE UNIQUE INDEX uq_org_unit_single_root ON org_unit ((true))
    WHERE parent_unit_id IS NULL;
```

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
[../data-model/02-organization.md](../data-model/02-organization.md#3-org_unit).

---

## D-036 — Units cannot be reparented; a unit that moves is a new unit

**Status:** decided (from your answer)
**Date:** refinement round 3
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

**See:** [../data-model/02-organization.md](../data-model/02-organization.md#5-org_unit_relationship--splits-mergers-succession).

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

- **The cache must be invalidated on every membership transition**, including the yearly
  expiry sweep, which is a bulk event touching everyone at once. The cache design must be
  built for this from the start, not retrofitted.
- **A lapse silently removes access.** That is the intent, but "why can't I see this?"
  becomes a question whose answer is a date, not a decision someone made.
- **`role.requires_membership` changes meaning** — from "reported, drives a worklist" to
  "enforced by the resolver". The "leaver with access" report remains useful, since it now
  detects roles that should have been closed rather than the mechanism doing the blocking.

**See:** [../domain/06-authorization-model.md](../domain/06-authorization-model.md#6-the-resolver),
[../data-model/05-authorization.md](../data-model/05-authorization.md#10-the-resolver-in-sql).

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
constraint drops `membership_type_id` and becomes a person-level invariant:

```sql
ALTER TABLE membership ADD CONSTRAINT ex_membership_no_overlap
    EXCLUDE USING gist (
        person_id WITH =,
        daterange(valid_from, valid_to, '[)') WITH &&
    )
    WHERE (status IN ('pending_payment','active','suspended'));
```

**"Am I a paid-up member?" is now one row, one status, one date.** That question was the
reason the type was in the constraint.

**A root participation row is created with the membership**, so "everyone in unit X" is one
uniform query whether X is the organization or a Thursday-evening pack.

**See:** [../data-model/03-membership.md](../data-model/03-membership.md#5-unit_participation).

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

**See:** [../data-model/05-authorization.md](../data-model/05-authorization.md#8-audience--grants-that-target-a-set-of-people).

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
guardianship-layer fact ([D-005](#d-005--permissions-are-grants-never-derived-from-identity)),
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
([domain/06 §2.5](../domain/06-authorization-model.md#25-enforcing-the-direction-of-authority)).

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
changes its mind. Every lapse date, the sweep, the renewal worklist and the cache invalidation
derive from this one parameter; changing it re-dates every *future* period but leaves
historical ones alone, which is the reason it is a parameter and not an expression computed
into stored rows.

**See:** [D-040](#d-040--the-fee-expires-yearly-a-date-tracked-renewal-window-replaces-a-grace-status),
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

**See:** [D-040](#d-040--the-fee-expires-yearly-a-date-tracked-renewal-window-replaces-a-grace-status),
[../data-model/03-membership.md §3](../data-model/03-membership.md#3-membership).

---

## D-049 — The root may not read into its sub-units; `scope_exposure` is the only crossing

**Status:** decided (from your answer)
**Date:** refinement round 4
**Resolves:** C-1

**Decision.** There is **no reporting channel outside the permission model** and none is
built. A unit's own material — its events, its rosters, its local leadership — is visible to
the root **only** when that unit writes a `scope_exposure` naming the assignment it is exposed
to. Every crossing is a written, attributed act by the unit that owns the data.

**Why.** Your answer, from the three routes offered: *"scope_exposure only"*. The
no-downward-inheritance rule ([D-031](#d-031--no-downward-inheritance-of-authority-scope_exposure-is-the-only-crossing))
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
**owns** the registry, the memberships and the fees ([D-035](#d-035--one-root-unit-all-sub-units-nest-arbitrarily-beneath-it)),
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
the registrar actually needs ([D-041](#d-041--belonging-to-a-sub-unit-is-a-participation-record-not-a-membership),
[03-membership.md §5.1](../data-model/03-membership.md#51-a-participation-row-on-the-root-unit)).
This will be misread as a mistake by someone who assumes a parent can see its children. It is
not a mistake, and the catalog says so in place.

**See:** [../domain/06-authorization-model.md §2](../domain/06-authorization-model.md#2-scope-authority--no-downward-inheritance),
[../data-model/05-authorization.md §5](../data-model/05-authorization.md#5-scope_exposure--how-a-unit-delegates-upward).

---

## D-050 — A renewal inside the window extends the existing root participation row

**Status:** decided (from your answer)
**Date:** refinement round 4
**Resolves:** D-7

**Decision.** When a membership lapses on 1 January and the person pays inside the window, the
new membership period is backdated to the expiry date ([D-040](#d-040--the-fee-expires-yearly-a-date-tracked-renewal-window-replaces-a-grace-status))
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
([03-membership.md §5](../data-model/03-membership.md#5-unit_participation)) is what makes the
close-and-reopen alternative awkward, and extending avoids the constraint entirely. The
integrity check that verifies the root row mirrors the membership
([03-membership.md §7](../data-model/03-membership.md#7-integrity-checks), check 1b) remains
valid and unchanged: after a renewal the two agree, and during a lapse-only period — before
any payment — the membership has ended while the root row has not yet been swept, which is
why the sweep must run and must run before anything reads the roster for authority.

**See:** [../data-model/03-membership.md §5.1](../data-model/03-membership.md#51-a-participation-row-on-the-root-unit).

---

## D-051 — The membership gate is waived by a permission, not only by a role flag

**Status:** decided (from your answer)
**Date:** refinement round 4
**Resolves:** D-6

**Decision.** A new **permission**, `system.gate_exempt`, waives the membership gate
([D-039](#d-039--member-permissions-require-a-current-paid-membership)) for anyone who holds
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

**See:** [../data-model/05-authorization.md §3](../data-model/05-authorization.md#3-role-and-role_permission),
[../data-model/05 §12](../data-model/05-authorization.md#12-seed-data--permissions),
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

**See:** [../data-model/05-authorization.md §3](../data-model/05-authorization.md#3-role-and-role_permission),
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
([data-model/05 §4](../data-model/05-authorization.md#the-open-ended-assignment-is-the-classic-access-failure)).
A role-based permission now has no expiry of its own; it is the assignment or nothing.

**See:** [../data-model/05-authorization.md §3](../data-model/05-authorization.md#3-role-and-role_permission),
[../appendix/permission-catalog.md §7](../appendix/permission-catalog.md#7-permissions-administration).

---

## D-054 — The sub-unit vocabulary is not seeded; the organization defines its own types

**Status:** decided (from your answer)
**Date:** refinement round 4
**Amends:** [D-008](#d-008--organizations-units-are-one-self-referencing-table-with-configurable-types)
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
retired `national`/`region`/`district` ladder ([D-035](#d-035--one-root-unit-all-sub-units-nest-arbitrarily-beneath-it))
was a guess; so was its replacement.

**Consequence: nesting is entirely permissive.** `org_unit_type_rule` exists and is
seeded with nothing, so any type may sit under any other — including under the root — until
the organization states a rule. This was already true with the placeholder
([data-model/02 §10](../data-model/02-organization.md#10-seed-data)); it is now true with no
ambiguity about *which* types the permissiveness applies to. A new type is usable the moment
it is created.

**Consequence: the root type is special and must be seeded.** The `organization` row stays,
because exactly one unit must have `parent_unit_id IS NULL`
([D-035](#d-035--one-root-unit-all-sub-units-nest-arbitrarily-beneath-it)) and that unit
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
change is confined to [data-model/02 §10](../data-model/02-organization.md#10-seed-data).

**See:** [../data-model/02-organization.md §10](../data-model/02-organization.md#10-seed-data),
[../domain/04-organization-structure.md §1–2](../domain/04-organization-structure.md#1-one-root-arbitrary-sub-units).

---

## D-055 — The permission catalog is deliberately comprehensive and granular

**Status:** decided (from your answer)
**Date:** refinement round 4
**Amends:** [D-030](#d-030--finer-permissions-will-be-added-incrementally)

**Decision.** The permission catalog is **large and granular on purpose**, and it stays that
way. It is a *menu* from which administrators assign people only what they actually need —
not a checklist every deployment is expected to use in full. Adding a permission remains one
row plus its `permission_level` rows ([D-007](#d-007--every-resource-has-an-admin-level-that-subsumes-narrower-ones--reversed)),
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
written. That is the intended behaviour ([D-007](#d-007--every-resource-has-an-admin-level-that-subsumes-narrower-ones--reversed)),
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

This is the favourable case for [D-004](#d-004--no-automatic-merging-ever), and it materially
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
[D-041](#d-041--belonging-to-a-sub-unit-is-a-participation-record-not-a-membership). At this
scale, a 1998 roster almost certainly records *which unit someone attended* and not *whether
their fee was paid*, and the import must decide per row which of the two it becomes. The safe
default — **participation, unless there is payment evidence** — matters more at thousands of
rows than at hundreds, because the failure mode compounds: an inferred open-ended `membership`
would make every 2003 roster member a *current* member today through the gate
([D-039](#d-039--member-permissions-require-a-current-paid-membership)).

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
**Supersedes:** [D-019](#d-019--household-membership-grants-no-access) — *the table it described
is gone, but the principle it stated is not, and that is deliberate*. **Amends:**
[D-037](#d-037--exactly-one-membership-type-the-fee-is-flat-and-per-person)

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
([D-020](#d-020--guardian-permissions-are-scoped-to-the-guardianship-row)). Removing a table
that granted nothing cannot grant anything. The old D-019 entry stays in the log, marked
superseded, because "why does living together not imply access?" is a question that will be
asked again.

**Also removed with it:** integrity check 7 (households with no address and no billing
contact), which has nothing left to check; the `household` bullet in
[data-model/04 §7](../data-model/04-relationships.md#7-open-issues); and D-9 in
[open-questions.md](../open-questions.md).

**See:** [../data-model/04-relationships.md](../data-model/04-relationships.md),
[../data-model/07-finance.md §2](../data-model/07-finance.md#2-minimal-provisional-shape).

---

## D-058 — An event is a dated occasion owned by exactly one unit

**Status:** decided (from your answer)
**Date:** refinement round 5

**Decision.** `event.org_unit_id` is `NOT NULL` — **exactly one owning unit.** A weekly
meeting group is **not** an event; it is `unit_participation`. Events are the things people
*register* for: camps, trips, hikes, jamborees.

**Why.** Two answers, and the second is the structural one.

- On ownership: *"One owning unit."* A joint camp between two packs is **Pack A's event that
  Pack B's children register for.** Pack B is a guest, and its access is written explicitly —
  an audience grant, a named person, at the level that fits. Nobody arbitrates "whose event
  is this?", and one unit remains the author of the record.
- On recurrence: *"No recurrence — meetings are participation."* A Thursday group meeting
  forty times a year is already recorded as "this child takes part in this Thursday group."
  Forty event rows would say what one participation row says, with forty capacities, forty
  organizer rosters, and forty chances to be wrong.

**The ownership rule is forced by [D-049](#d-049--the-root-may-not-read-into-its-sub-units-scope_exposure-is-the-only-crossing),
not merely preferred by it.** If an event could belong to two units, the root's inability to
read a sub-unit's events would have an exception shaped exactly like a joint camp, with no
principled place to stop. One owner keeps the rule total.

**What this forecloses.** There is no `event_series`, no RFC 5545 rule, no occurrence table,
and no `event_unit` join table. Each would require every downstream table — registrations,
capacity, presence, organizers, questions — to carry a second possible home.

**Consequence worth stating.** "Was Jan at the meeting on 14 March?" is **not answerable from
the events module.** That is presence tracking for a standing group, which is a different
feature. The boundary is deliberate; the confusion between the two is the thing to watch for.

**See:** [../domain/07-events.md §1–2](../domain/07-events.md#1-what-an-event-is-and-what-it-is-not),
[../data-model/08-events.md §2](../data-model/08-events.md#2-event).

---

## D-059 — "Unanswered" is the absence of a row; a registration stores two values

**Status:** decided (from your answer)
**Date:** refinement round 5

**Decision.** `event_registration.response` has **two** values — `'attending'` and
`'not_attending'`. **`'unanswered'` is written nowhere.** It is the *absence* of a
registration row. "Who has not replied yet?" is a subtraction:
*(people who could contribute to this event) MINUS (people with a registration)*.

**Why.** Your answer: *"Absent row — two stored values."*

The framing that settled it was your own correction: registration is *"positive with
additional fields, or negative (or none)"*. **"None" is not a third stored value** — it is the
lack of a record, and storing it would mean writing rows for people who have not acted.

**Three reasons absence beats a stored value**, and the third is decisive:

| | Absent row | Stored `'unanswered'` |
|---|---|---|
| Rows written before anyone acts | None | One per person asked |
| "Asked and silent" vs "never asked" | Distinguishable — the eligible set is a query | Indistinguishable without an invite table |
| **"Who has not replied?"** | **A subtraction against an audience** | Requires enumerating the audience into rows |

The third is the real argument. The eligible set is an **audience** — a rule the resolver
evaluates ([D-042](#d-042--grants-may-target-audiences-not-only-individuals)) such as
`unit:7:participants` or `all_members`. Enumerating it into `'unanswered'` rows would mean
re-enumerating every time a child joins the pack, and the stored rows would drift out of
agreement with the rule that generated them.

**Returning someone to unanswered removes the row** (`DELETE`, recorded in `audit_log`). That
is the honest act — it leaves the least behind, and "no row" then means the same thing
whether the person never answered or their answer was withdrawn.

**Consequence.** `unit_participation` uses the same reasoning for the same reason, and this
decision makes the pattern explicit: **where a state is the absence of a fact, store the
absence.** Compare [D-002](#d-002--everything-temporal-is-a-period-never-a-boolean) for the
temporal case and [D-053](#d-053--a-role-is-valid-always-only-its-assignment-is-temporal)
for the definitional one.

**See:** [../data-model/08-events.md §4](../data-model/08-events.md#4-event_registration),
[../domain/07-events.md §3](../domain/07-events.md#3-registration-one-record-two-stored-answers-and-no-unanswered).

---

## D-060 — Eligibility is capability; there is no separate rule engine

**Status:** decided (from your answer)
**Date:** refinement round 5
**Resolves:** the deferral in [D-006](#d-006--per-item-permissions-are-capabilities-on-the-item)

**Decision.** Registration requires **`contribute` capability on that event.** Nothing else.
There is no eligibility rule table, no age gate, no prerequisite system. `event.register_self`
is already mapped to `contribute` in `permission_level`.

**Why.** Your answer: *"I feel like the people with 'contribute' permissions (capabilities) on
that item should be allowed to register."*

**This dissolves D-006's deferral rather than satisfying it.** D-006 said *"eligibility ...
will be a separate concept when events are specified."* Your answer says the separate concept
was never needed: **the capability ladder already is one.**

```
view        may SEE the event
contribute  may REGISTER for it
manage      may ORGANIZE it
admin       may control it
```

**Why audiences make this sufficient rather than merely simple.** Registering 200 children
individually is 200 grant rows — but opening an event to members is **one**:

```sql
INSERT INTO access_grant (scope_type, scope_id, audience_id, level)
VALUES ('event', :camp_id,
        (SELECT id FROM audience WHERE code = 'all_members'), 'contribute');
```

An age-gated camp is a camp opened to `unit:<id>:participants` for a unit whose participants
are that age. **This is the case audiences ([D-042](#d-042--grants-may-target-audiences-not-only-individuals))
were built for**, and events are where the investment pays off.

**What this does not do, stated plainly.** It does **not** enforce an age *ceiling* on an
open event. If a nine-year-old holds `contribute` on a camp for teenagers, they can register.
The design **decides eligibility by who may register, not by inspecting the person** — the
check *is* the grant. Whether that is sufficient is carried in
[../open-questions.md](../open-questions.md) rather than hidden.

**Organizers are not bound by it.** Anyone holding `event.manage_participants` may register
anyone, and the registration records `source = 'staff'`. That is the permission's purpose:
the leader who knows there is a spare bed is trusted, and the act is attributed.

**See:** [../domain/07-events.md §4](../domain/07-events.md#4-who-may-register-capability-not-a-separate-rule-engine),
[data-model/05 §7](../data-model/05-authorization.md#7-permission_level--connecting-permissions-to-grant-levels).

---

## D-061 — Event answers are read by that event's organizers

**Status:** decided (from your answer)
**Date:** refinement round 5

**Decision.** Answers to `event_question` are readable by **the organizers of that event**,
with no additional permission. You confirmed the consequence explicitly: **the event form is
the route by which a camp leader learns a child has a nut allergy.**

**Why, and the part that must be recorded.** This is only coherent — and only defensible —
because the `dependent.*` namespace is **unreachable by unit leaders**. The permission
catalog states it outright:

> *"Resolved **only** against `guardianship_permission`, never against roles. A unit leader
> does not get these by virtue of leading the unit — that is a safeguarding property."*

So a camp leader **cannot reach `dependent.medical.*` at all.** Not by leading the pack, not
by running the camp, not by being an organizer. There is no permission that changes it.
Which means an allergy recorded on a camp form is the *only* way the people running the camp
will know.

**This is a widening, and it is recorded as one.** Access to a child's health information
moves from *"few people, via a guardianship-scoped permission granted by the guardian"* to
*"every organizer of any event the child registers for."* That is a coherent position — the
parent tells the people present, per event, and the medical file stays closed — but it is
**not** an accident of where the gate was placed, and it must not be "fixed" later by
tightening the wrong thing.

**Two consequences that follow.**

1. **Only preference-level detail belongs on a form.** Nothing in the schema distinguishes
   "vegetarian" from "coeliac" — both are `data_type = 'text'` in `event_answer.value`. The
   discipline is in the form *label*, so it is guidance, not a constraint. A `CHECK` cannot
   tell them apart, and a keyword list would fail on the first unusual phrasing.
2. **Event answers are not a medical record.** They are operational detail for one event,
   read by that event's organizers, and ending with the event. The two stores are not
   duplicates of each other and should not be merged or synchronised.

**Open:** the retention policy. A dietary answer citing a medical condition is health data
with a retention obligation, and there is no policy yet.

**See:** [../data-model/08-events.md §7](../data-model/08-events.md#7-event_question-and-event_answer),
[../domain/07-events.md §12](../domain/07-events.md#12-the-forms-questions-and-answers),
[appendix/permission-catalog.md §9](../appendix/permission-catalog.md#9-the-dependent-namespace).

---

## D-062 — Organizers are appointed on the event, not granted

**Status:** decided (from your answer)
**Date:** refinement round 5

**Decision.** Events have an `event_organizer` roster, and it is **the domain answer** to
"who is running this?" — labelled, ordered, attributed. It is **not** an `access_grant`, and
it does not by itself confer authority to act on the event.

**Why.** Your answer: *"Roster only; grants stay separate."*

**The tempting alternative, and why it fails.** Write an `access_grant` at `manage` whenever
an organizer is added, so "the organizers" is a query over grants and the two can never
disagree. It fails on three counts:

| | Grant at `manage` | `event_organizer` |
|---|---|---|
| A cook's label | No room for `organizer_role = 'cook'` | `organizer_role`, free text |
| Display order | Not expressible | `sort_order`, `is_primary` |
| "Who is running this camp?" | Read the permission table | Read the roster |
| Removing the cook | Revokes their ability to *see* the event | Removes them from the list |

That last row is the practical one: "they are no longer cooking" does not mean "they may no
longer see the camp."

**`event_organizer` is the event-scoped analogue of `position_assignment`** — an appointment
on the thing being run. Like a position it may carry a label and an order; like a position it
is not a permission bundle. `organizer_role` is **free text, not a CHECK**: every
organization labels these differently, and a controlled vocabulary here would be a guess of
the kind [D-054](#d-054--the-sub-unit-vocabulary-is-not-seeded-the-organization-defines-its-own-types)
removed for unit types.

**It has no `valid_to`, deliberately.** A roster is not a period: you are on the list or you
are not. An organizer who drops out is removed (audited), because "was Jan an organizer of
that camp?" must have one answer, not a set of intervals.

**How authority actually reaches an organizer** is [D-063](#d-063--an-event-is-an-artifact-of-its-unit-not-a-child-of-it) —
the unit's roles reach its events.

**See:** [../data-model/08-events.md §3](../data-model/08-events.md#3-event_organizer),
[../domain/07-events.md §5](../domain/07-events.md#5-organizers-are-appointed-not-granted).

---

## D-063 — An event is an ARTIFACT of its unit, not a child of it

**Status:** decided (from your answer, as a consequence you did not have to state)
**Date:** refinement round 5
**Amends:** nothing. **Extends:** [D-031](#d-031--no-downward-inheritance-of-authority-scope_exposure-is-the-only-crossing)

**The problem.** The resolver matches scope **exactly**. There is therefore no path from a
`unit_leader` role held at `('org_unit', 7)` to a check made at `('event', 42)` — even when
unit 7 owns event 42:

```
unit_leader ── holds role at ──► org_unit 7 (the pack)
                                     │
                                     │  ✗ NO PATH
                                     ▼
event 42 "Summer camp" ◄─ owned by ──┘    resolver checks scope exactly
```

The pack's leader — the person whose *job* is running the pack's camp — does not pass
`can(leader, 'event.view', 'event', 42)`. Nothing is broken; the answer is simply no. But the
module cannot ship with that gap, because it would mean the leader must be granted every
event their own unit creates.

**Decision.** A permission is satisfied at `('event', E)` if it is satisfied at **the event's
owning unit**, `('org_unit', E.org_unit_id)`, *and* that unit is the event's owner. One
wrapper function, `can_event()`, calling `can()` twice.

**Why this is not inheritance downward, and why that distinction is the whole point.**

| | Inheritance (rejected, D-015/D-031) | Artifact rule (chosen) |
|---|---|---|
| What a leader gains | Authority in the unit's **sub-units** too | Authority over the unit's **own events** |
| Blast radius | Grows on every restructure | Fixed — one owner, pinned by D-049 |
| Reverses | **D-015, D-031** | Nothing |

**An event is not a child of its unit; it is a thing the unit made.** The unit's authority
already covers the unit. Asking "may this person do this in Pack 7?" is asking the right
question about the right scope — and it is a question the resolver already answers correctly.

Restructuring the hierarchy still changes nothing about who may do what. Adding a sub-unit
still grants nobody anything. **D-015 and D-031 stand untouched**, and the rule is exactly as
narrow as the case requires.

**Why a wrapper function rather than a change inside `can()`.** Putting this clause inside
the resolver would make every permission check — on people, memberships, units, fees —
evaluate an event-shaped rule. Keeping it in `can_event()` means the exception is visible,
named, and confined to the module that needs it.

**And it is a two-way door.** `can_event()` calls `can()` twice and adds no authority of its
own; nothing is written to `access_grant` to make it work. If the organization decides that
leaders should *not* automatically run every event their unit creates, **deleting the second
`can()` call is the entire change, and it needs no data migration.**

**The root is unaffected.** An organization-scoped `registrar` still cannot see a pack's camp
— events are precisely the sub-unit records [D-049](#d-049--the-root-may-not-read-into-its-sub-units-scope_exposure-is-the-only-crossing)
protects. The fix, if the root wants it, is one `scope_exposure` row naming one assignment.

**See:** [../domain/07-events.md §6](../domain/07-events.md#6-the-hinge-organizers-and-the-scope-mismatch),
[../data-model/08-events.md §8](../data-model/08-events.md#8-projections-and-guards).

---

## D-064 — There is no event status; visibility is the permission model

**Status:** decided (from your answer)
**Date:** refinement round 5

**Decision.** `event` has **no `status` column.** Draft is not a state: a new event has no
grants beyond its organizers' own authority, so nobody else can see it, and **publishing is
an `access_grant`, not an `UPDATE`.** `completed` is derived (`ends_at < now()`).
Cancellation is a recorded fact — `cancelled_at`, `cancelled_by`, `cancel_reason`.

**Why.** Your answer, which is the right instinct: *"Isn't the draft solved by not giving
anyone else permissions, but the organizer?"* It is, and it is better than a status enum for
a reason worth stating:

> **A status column and a permission system that both claim to answer "who may see this?"
> will eventually disagree — and the one that gets enforced is whoever wrote the last `IF`.**

With no status column there is nothing to disagree. The questions a `draft` flag would answer
are all answered by grants:

| Question | Answer |
|---|---|
| "Is this ready to be seen?" | Has anyone been granted `view`? |
| "Who can see it before it is announced?" | Its organizers, and anyone already granted |
| "How do I hide it again?" | Revoke the grant — `revoked_at` set, the row kept |

**Where the logic deliberately diverges: cancellation.** If cancelling were done by revoking
grants, **the event would vanish for exactly the people who need to know it is off** — the
registrants. They would see nothing at all: not "cancelled", just gone. So cancellation is a
fact, the event stays visible, and it is marked.

Draft and cancellation therefore use *different mechanisms on purpose*, because they have
different audiences: draft is about who may **discover** an event, cancellation is about who
must be **told**.

**A cancelled event** stops accepting registrations (the window closes implicitly) and
**keeps every registration row** — those rows are the record that the camp was planned and
who was coming, which is precisely what is needed to notify and refund.

**See:** [../domain/07-events.md §10](../domain/07-events.md#10-cancellation-and-why-there-is-no-status-column),
[../data-model/08-events.md §2](../data-model/08-events.md#2-event).

---

## D-065 — Capacity is a waitlist threshold, and organizers may exceed it

**Status:** decided (from your answer)
**Date:** refinement round 5

**Decision.** Registering for a full event **succeeds and produces a waitlisted row** — it is
never refused. Organizers may register past capacity outright, and the overrun is
**permitted, attributed and reported** rather than prevented. Promotion from the waitlist is
a deliberate act by an organizer, never automatic.

**Why.** Two answers, and they only look contradictory:

- *"Waitlist"* — the thirteenth caller for a twelve-bed camp is not turned away, they are
  written down.
- *"Organizers might exceed, also they might choose to include people from the waiting
  list"* — a leader who knows there are two spare tents should not be blocked by a number
  they cannot edit mid-camp.

**The two coexist because the waitlist is a SELF-SERVICE outcome.** The trigger applies it
only when `source = 'self'`. A staff registration is admitted regardless. So:

| Path | At a full event |
|---|---|
| Self-service | Waitlisted, ordered |
| Staff / organizer | **Admitted**, the overrun reported |
| Promotion | Deliberate — an organizer picks who comes off the waitlist |
| Capacity change | An `UPDATE` — visible and attributed |

**Capacity is therefore three things at once, on purpose:** a rule for self-service, a number
organizers can exceed, and a report. [data-model/08 §10 check 5](../data-model/08-events.md#10-integrity-checks)
produces rows and **that is not a failure** — an event that overruns every year has a wrong
capacity number, and the fix is the number, not refusing people.

**Promotion is not automatic** because a place freeing up is not the same as it being right
to give it to the next person — the organizer may know the next child cannot come on those
dates. What *is* automatic is one narrow release rule, recorded as such in
[D-066](#d-066--payment-confirms-the-place-and-the-release-deadline-is-the-one-automatic-transition).

**See:** [../data-model/08-events.md §5](../data-model/08-events.md#5-capacity-and-the-waitlist),
[../domain/07-events.md §8](../domain/07-events.md#8-capacity-and-the-waitlist).

---

## D-066 — Payment confirms the place, and the release deadline is the one automatic transition

**Status:** decided (from your answer)
**Date:** refinement round 5

**Decision.** An event may have a fee (`event.fee_schedule_id`), and **payment confirms the
place**. Registering creates a `fee_obligation`; a paid obligation sets
`is_confirmed = true` via `confirm_event_place()`. **Events without a fee confirm
immediately, and most events have no fee** — you were explicit that payment *"does not have
to be at all events."*

**Why.** Your answer: *"Payment confirms the place, also the payment does not have to be at
all events."*

The second half is the part that shapes the schema: `fee_schedule_id` is **nullable**, and
`NULL` is the common case. A free hike confirms on registration, and there is no
"confirmation" state with no meaning.

**The accepted cost, recorded rather than hidden.** This design has spent real effort
avoiding automatic state changes ([D-023](#d-023--nothing-is-auto-lapsed-or-auto-terminated),
[D-040](#d-040--the-fee-expires-yearly-a-date-tracked-renewal-window-replaces-a-grace-status)),
and payment-confirms-the-place reintroduces one: an unpaid registration at a full event
**releases its place to the waitlist** at `waitlist_deadline`. It is accepted because it is a
**deadline, not a sweep** — narrowly scoped, opt-in per event, and visible in what it
produces:

```sql
-- Only at a full event, only with a fee configured, only past the deadline,
-- only unpaid, only self-service, never a cancelled event.
e.fee_schedule_id IS NOT NULL
AND e.waitlist_deadline IS NOT NULL
AND e.waitlist_deadline < now()
AND r.source = 'self' AND r.is_confirmed = false
AND e.cancelled_at IS NULL
```

`waitlist_deadline` is `NULL` by default, so **an event that does not opt in never runs this
rule at all.** The alternative — no deadline — means a place is held forever by someone who
never paid, which is worse.

**A function, not a trigger.** `confirm_event_place()` is called by the finance module and is
**not** a trigger on `fee_obligation.status`, because a trigger would fire for membership
fees and event fees alike and "the fee is paid" means something different in each case: a
membership *activates* (D-040), an event place *confirms*. Two transitions, two owners.

**See:** [../data-model/08-events.md §6](../data-model/08-events.md#6-payments-and-confirmation),
[../domain/07-events.md §11](../domain/07-events.md#11-payments-on-events).

---

## D-067 — Presence is a three-valued fact on the registration

**Status:** decided (from your answer)
**Date:** refinement round 5

**Decision.** `event_registration.was_present` is a **nullable boolean**, marked by an
organizer with `presence_marked_by` / `presence_marked_at`.

| Value | Meaning |
|---|---|
| `NULL` | Not yet marked — no register was taken |
| `true` | Turned up |
| `false` | Marked absent — a register was taken and they were not there |

**Why three-valued rather than a boolean defaulting to false.** *"We did not take a
register"* and *"we took a register and they were not there"* are **different facts**, and
only the second is a safeguarding signal. A boolean defaulting to `false` would assert
absence where the organization only failed to look.

**Why it matters more than it looks.** For a camp, the end-of-week presence record **is the
record of who was actually in the organization's care.** That is the row that matters if the
fee buys insurance (finance question 9 — *"member on the date of the incident"*), and it is
the row that cannot be reconstructed afterwards from registrations.

**Presence is not registration**, and the distinction is enforced: a `not_attending`
registration with `was_present` set is contradictory and reported
([data-model/08 §10 check 8](../data-model/08-events.md#10-integrity-checks)).

**A walk-in is not representable, deliberately.** A sibling who turns up on the day was not
in the organization's care — no guardian recorded, no name on the roster — and must not
*silently appear* to have been. Recording them means registering them, which means the
organizers have a name and a guardian. That is the correct friction.

**Note the contrast with D-059.** There, absence of a row was the right encoding for
*unanswered*. Here, a stored `NULL` is the right encoding for *not marked*. The difference:
"unanswered" is the absence of a **fact about the person**, while "not marked" is a fact
about the **organization's incomplete work** — and the work being incomplete is itself worth
recording, because it is a task still outstanding.

**See:** [../data-model/08-events.md §4](../data-model/08-events.md#4-event_registration),
[../domain/07-events.md §9](../domain/07-events.md#9-presence-what-actually-happened).

---

## D-068 — There are no per-resource `admin` permissions; roles are the bundle

**Status:** decided (from your answer) — **reverses [D-007](#d-007--every-resource-has-an-admin-level-that-subsumes-narrower-ones--reversed)**
**Date:** refinement round 5

**Your answer.** Asked whether `person.admin` should subsume `person.merge` and
`person.redact` — the standing case against prefix subsumption, since both are irreversible
and both are privacy incidents if granted wrongly — you answered: *"Only the system should
have admin permissions, not the individual items."*

The phrase needed disambiguating, because *"individual items"* names two different things in
this schema: the per-resource permission (`person.admin`, over the whole resource) and the
item-scoped grant (`access_grant` over one event). You confirmed the first reading.

**Decision.** The **sixteen** `<resource>.admin` permission codes are **deleted** — the ten
documented ones (`person.admin`, `account.admin`, `membership.admin`,
`unit_participation.admin`, `org_unit.admin`, `position.admin`, `guardianship.admin`,
`audit.admin`, `event.admin`, `audience.admin`) and the six sitting in deferred namespaces
(`document`, `fee`, `payment`, `report`, `consent`, `message`). So is the resolver's
prefix-match branch. What remains:

- **`system.admin`** is the only permission in the system that means *everything*, and it is
  reached only through a role assignment (`system` namespace — never an item grant, never
  guardianship). Unchanged.
- **"Someone who can do everything about events"** is a **role** the organization composes,
  bundling the thirteen `event.*` codes. Not a permission the code invents for them.
- **`access_level.admin` (rank 40) is untouched.** This is a different thing that shares a
  name, and the collision is the most likely place for a later reader to go wrong. The level
  answers *"how much authority does this grant carry"* — `view` < `contribute` < `manage` <
  `admin`, used by `permission_level` to decide whether a `contribute`-level grant satisfies
  `event.register_self`. The permission code answered *"does this capability imply that one"*.
  The ladder survives; only the wildcard code dies.

**Why this is coherent with the rest of the design rather than an exception to it.** D-052
already settled that **roles are runtime data and the seed set is not a specification** — the
organization composes permission groups at runtime. A per-resource `admin` code is the code
composing a permission group *on the organization's behalf*, in advance, for a bundle nobody
asked for. Deleting it makes the two mechanisms agree: **the code implements capabilities,
the organization groups them.** It is the same division D-055 drew when it refused to prune
the catalog — a large menu of narrow things, composed by whoever needs them.

**The cost is real, and it is the cost D-007 existed to prevent.** Stated in D-007's own
words: without the wildcard, *every new narrow permission requires updating every role that
should already have implied it — and someone will miss one, producing a permission that
silently is not granted.* That failure mode is back. It is accepted because it fails
**closed**: someone cannot do a thing they were arguably meant to be able to do, and they say
so, rather than doing a thing nobody meant them to be able to do. D-007 traded a loud
inconvenience for a quiet hazard. The reversal takes the opposite side of the same trade.

**What replaces the protection** — since the wildcard is gone, reachability needs a check of
its own. **Integrity check 18** lists permissions that **no role grants**, which is the query
that surfaces a permission silently orphaned by the absence of a wildcard (numbering follows
the existing list in [../data-model/05 §11](../data-model/05-authorization.md#11-integrity-checks)):

```sql
-- 18. ORPHANED PERMISSIONS — granted by no role at all. With no .admin wildcard
--     (D-068), a new permission nobody bundles is silently unusable. This report is
--     the safety net the wildcard used to be.
SELECT p.code, p.resource
  FROM permission p
 WHERE p.is_assignable
   AND NOT EXISTS (SELECT 1 FROM role_permission rp WHERE rp.permission_id = p.id)
 ORDER BY p.resource, p.code;
```

**What happens to the F-4 question that prompted this.** It does not dissolve — it **moves,
and becomes visible.** A role bundling all eleven `person.*` permissions still reaches
`person.merge` and `person.redact`, because those are ordinary codes in the bundle. The
difference is where the decision lives: previously a *resolver rule* made the implication,
invisible in every role editor and true for every resource whether or not anyone wanted it.
Now the implication appears **as the contents of a role the organization wrote**, reviewable
line by line in `role_permission`, dated, and alarmable. `role.edit` on that role is already
audited for exactly this reason (D-052). **The guidance therefore moves from the schema to
the seed:** a role bundling a resource *including* its irreversible codes should be named for
what it is, and the seed roles in §11 are written so that no seeded role mixes
`person.merge`/`person.redact` with routine `person.edit`. That is now expressible as a
report rather than a caveat.

**Two survivors, and why neither is an exception.** Both look like wildcards and neither is
the thing being deleted:

- **`dependent.admin` stays.** It is **not** a prefix-match artefact — it is a code a staff
  member *chooses and stores*, one row in `guardianship_permission`, granting the full set for
  one child. A wildcard that must be deliberately written is what this decision endorses, not
  what it removes. It also has a property no role wildcard can have: an explicit
  `is_granted = false` row **overrides** it, so a court-ordered restriction survives a broad
  grant. Deleting `dependent.admin` would make the common restriction *easier* to express, not
  harder — listing nineteen narrow rows per child where a court case needs two. **The
  distinction to keep: `person.admin` implied capabilities nobody wrote down;
  `dependent.admin` is a shorthand for capabilities somebody did write down, in a specific
  row, about a specific child.**
- **`system.admin` stays**, for the reasons already in §7 — it is the break-glass capability,
  concentrating the most dangerous thing in one alarmable holder rather than scattering
  equivalents. It was never a prefix-match beneficiary; it is checked outright.

**A third thing called "admin", which also stays.** `dependent.profile.admin`,
`dependent.medical.admin`, `dependent.consent.admin` are **not** wildcards at all — they are
*actions* meaning "edit" inside a sub-resource, paired against `.view`. Nothing is implied by
them. Three unrelated meanings now share one word in this schema — the access **level**
(rank 40), the deleted resource **wildcard**, and an **edit** action — and any of the three
may be what a reader means. When one of them comes up in conversation, say which.

**Migration.** Deleting `role_permission` rows for the sixteen codes; no other data moves.
Any role that held only `person.admin` becomes an empty role, which is *correct* and visible
rather than quietly over-privileged — and `role.delete` still refuses to remove a role that
was ever assigned (D-052), so the empty shell survives as evidence of what someone once
meant. Re-deriving it means naming the bundle, which is the point.

**Two-way door?** No. Re-adding a wildcard later is mechanically cheap and semantically loud
— it re-creates the implication silently for resources added after the day you added it.
Treat it as a fresh decision, not a revert.

**See:** [../appendix/permission-catalog.md §1](../appendix/permission-catalog.md#1-conventions),
[../data-model/05-authorization.md §2](../data-model/05-authorization.md#2-permission),
[../domain/06-authorization-model.md §4](../domain/06-authorization-model.md#4-roles--bundles-of-permissions).

---

## D-069 — Guardianship ends when a person ends it; the system takes no position on majority

**Status:** decided (from your answer) — **reverses [D-024](#d-024--guardianship-does-not-auto-expire-at-majority--reversed)**
**Date:** refinement round 5

**Your answer.** Asked what the system does when a guarded child turns 18 — review queue,
auto-expire, or nothing — you answered **"Nothing at all."**

**Decision.** No job, no review queue, no computed candidate date, no flag. A guardianship
row is ended by a person ending it (`guardianship.end`), or by import, and the system does
not notice birthdays in this connection at all.

**Why this is better than the queue D-024 proposed, and where D-024 went wrong.** D-024
reasoned from *"fail open rather than silently strip access"* and picked the gentler of two
automatic behaviours. **Both were automatic.** The queue was not a refusal to act; it was a
deferral of the action, and it smuggled in a claim the system cannot support: that majority
is a date the system knows. It is not. D-024's own rationale said thresholds vary by
jurisdiction — and then computed a date anyway. A review queue is not a neutral container for
a wrong date; it is a worklist of cases staff are told to decide, and the item on it asserts
something the organization has not decided.

**The deeper problem with the queue: it inverts who decides.** Under D-024 the system raises
the question at 18 whether or not anyone wanted it asked, in every case, for every family —
including the ones where the adult child asks their parent to keep handling their medical
correspondence. The queue's default is that the arrangement is suspect. That is the wrong
default for a relationship the organization did not create.

**What "nothing" costs, stated honestly.** Nothing is tracked, so **"who is still listed as my
guardian, and since when?" has no automatic answer.** It has a manual one: `guardianship`
carries `valid_from`/`valid_to`, so the question is a query on a person's rows and the answer
includes the date each was ended. What is lost is a *prompt*, not a *record* — which is the
same trade the module makes everywhere. See the pattern below.

**This is the latest in a consistent line of refusals, and the reasoning is identical each
time.** Across five rounds the design has allowed itself exactly two automatic transitions —
the yearly fee sweep (D-040) and the event waitlist release (D-066) — and has refused, among
others, automatic membership lapse states (D-023), event status (D-064), and recurrence
(D-058). Guardianship expiry is the next one refused. The pattern: **an automatic transition is cheap to design and expensive to defend, because it
acts on every case including the ones it was not designed for.** A nightly job that ends
guardianships at 18 fails closed and strips a legally valid arrangement overnight; a queue
fails open and adds a standing assertion the org never made. The third option — a person who
knows the family ends the row — is the only one that can also decide *not* to.

**Consequence to carry: nothing here weakens the exit path, so the exit path must exist.**
With no automatic end, `guardianship.end` is the only door, and it must be reachable by
someone. Two things follow, both worth stating because they are now load-bearing in a way they
were not when a job existed to help:

1. **The adult child must be able to end it about themselves.** They are the subject of the
   row and currently hold no permission over it — they are not a guardian of themselves. This
   needs a route, and it is now the module's sharpest open item.
2. **A stale row is invisible by design**, so the query, not the job, is the control. A
   periodic human review is a good idea and is explicitly *not* a scheduled system behaviour.

**Follow-up raised: E-2 is closed and replaced by E-5** — *"how does an adult end a guardianship
over themselves?"* That question existed before this decision and was masked by a review queue
that would have surfaced it. It is now unavoidable.

**See:** [../data-model/04-relationships.md §2](../data-model/04-relationships.md#2-guardianship_permission),
[../domain/02-actors.md §5](../domain/02-actors.md#5-acting-on-behalf).

---

## D-070 — An event has no age ceiling; the grant is the rule

**Status:** decided (from your answer)
**Date:** refinement round 5

**Your answer.** Asked about the one gap in *eligibility is capability*
([D-060](#d-060--eligibility-is-capability-there-is-no-separate-rule-engine)) — an event
opened to `all_members` can be registered for by a nine-year-old even if the camp was planned
for teenagers — you answered **"Leave it — the grant is the rule."**

**Decision.** No `min_age`/`max_age` on `event`. No age check in `place_event_registration()`.
Age restriction is expressed **entirely** by choosing the audience the event is opened to.

**Why the option was tempting, and why refusing it is right.** The offered design was the
cheap one: a column pair plus one branch, **reported** rather than blocking, matching
`position.min_age`. It would have cost little and reversed nothing. It is refused on
consistency grounds, which are the only grounds worth having here. A condition evaluated at
registration time that the capability model does not know about is **the first rule-engine
rule**. Not because age is special — because the moment one exists, the second is cheap, and
within two years the honest answer to "who can register for this?" is "check the grants, and
also the age columns, and also whatever else we added there." D-060 dissolved a deferred
question by noticing the capability model already answered it; a condition living beside it
reopens the question by insisting the capability model is not enough.

**The residual risk, stated rather than waved away.** A leader registers a child for an event
the child is too young for, and **nothing in the system objects.** Accepted, on three
conditions that are all already true in the schema:

1. **It is attributable.** Staff-driven registrations carry `source = 'staff'` and a
   `created_by`, so the judgement is recorded as belonging to a named person.
2. **It is visible.** §9's roster query lists registrants with birth dates, so age is on the
   page a leader looks at while confirming.
3. **It is the normal case correctly handled already.** A genuinely age-bounded event is
   opened to the unit whose members are that age, and that is how a section-based organization
   works today. What is *not* covered is one narrow shape — an event open to everyone that
   should be restricted — and it is narrow enough that a column pair would be a permanent
   mechanism serving an exception.

**If it is ever revisited,** the trigger is specific: the shape recurring often enough that
leaders routinely open the wrong event to the wrong people. Then the right answer is probably
still not columns on `event` but **an audience that encodes the age band** — `all_members` is
a rule the resolver evaluates, and so could `members_aged_13_plus` be. That keeps eligibility
in one place, which is the property being protected here. **Do not reach for a condition on
the row when the mechanism for evaluating membership of a set already exists.**

**See:** [../domain/07-events.md §4](../domain/07-events.md#4-who-may-register-capability-not-a-separate-rule-engine),
[../data-model/08-events.md §9](../data-model/08-events.md#9-the-three-queries-that-matter).

---

## D-071 — Nothing forces a role assignment to end; the gate and the report are the control

**Status:** decided (from your answer) — **overrides the recommendation in F-3**
**Date:** refinement round 5

**Your answer.** Asked whether `valid_to` should be mandatory on high-authority role
assignments — the classic *volunteer who was never removed* — you answered **"Nothing — rely
on the gate."**

**The docs had recommended the other way.** F-3 said *yes, at the application layer*, and
argued the membership gate made an open-ended assignment more dangerous, not less. You
disagree, and the disagreement is worth recording because the recommendation was not
obviously wrong.

**Decision.** `role_assignment.valid_to` stays nullable with no application-layer requirement
and no per-role policy. The controls are the **membership gate**
([D-039](#d-039--member-permissions-require-a-current-paid-membership)) and a **report**. No
new constraint anywhere.

**Why the recommendation was wrong, in one place.** F-3 said the gate makes open-ended
assignments *more* dangerous. It is the other way round: **the gate already does what an
expiry date would do, for exactly the population an expiry date would target, and it does it
without inventing a date nobody chose.** A forced `valid_to` is an guess about when authority
should lapse, written by whoever made the assignment — usually inherited from a form default.
The gate instead ties expiry to a fact the organization already maintains and renews on
purpose: whether this person is a member. When the fee lapses, gated roles stop granting. The
expiry date was always going to be a worse approximation of that.

**What the gate does not cover — the honest residue.** `unit_leader` and `assistant_leader`
have `requires_membership = false` by explicit decision (a volunteer whose own fee lapses
still runs the Thursday meeting), so a lapsed leader keeps leading. Also any role held by a
non-member, and anything carrying `system.gate_exempt`. For those, the answer is a **periodic
human review over open-ended assignments**, and D-068 now makes that query sharper, since a
role's full reach is visible in `role_permission` with no wildcard hiding implications in the
resolver.

**Note the dependency this decision creates.** D-053 put *all* the weight on
`role_assignment.valid_to` as the only thing that ends authority, and warned that the
open-ended assignment is the classic access failure. **This decision declines to add a guard
rail at precisely that point**, so the two together should be read as one load-bearing pair:
authority ends only when somebody ends it, and the only defence left is that somebody looks.
The report is not a nice-to-have here; it is the entire control.

**See:** [../data-model/05-authorization.md §4](../data-model/05-authorization.md#4-role_assignment--system-wide-authority),
[../open-questions.md F-3](../open-questions.md#f-3--closed--nothing-forces-an-assignment-to-end).

---

## Reversed decisions

- **D-015 — Authority inherits downward through the unit hierarchy.** Reversed by
  [D-031](#d-031--no-downward-inheritance-of-authority-scope_exposure-is-the-only-crossing)
  (refinement round 2). The organization must not be able to decide permissions over a
  nested unit; authority originates at the unit. The original entry is kept above, marked
  reversed, rather than edited away.
- **"Local permissions override global ones"** (a phrasing used in the domain docs, never a
  numbered decision). Amended by
  [D-032](#d-032--deny-is-absolute-locality-orders-allows-only): still true for **allows**,
  and deliberately **not** true for denies. The statement in isolation was the source of
  the ambiguity, so it no longer appears unqualified anywhere in the docs.
- **Person `deceased` field** (never assigned a decision number; it appeared in the person
  table and the permission catalog). Removed by
  [D-034](#d-034--the-person-record-holds-no-deceased-flag).
- **`position.is_unique_per_unit`** (a boolean). Replaced by `position.max_holders`
  ([D-033](#d-033--multiple-people-may-occupy-the-same-position)).
- **The single-rooted hierarchy as an *assumption*** (§2 of the organization docs described a
  national → region → district → group → troop ladder, with groups permitted directly under
  national). Replaced by
  [D-035](#d-035--one-root-unit-all-sub-units-nest-arbitrarily-beneath-it): one root, arbitrary
  nesting beneath it.
- **Retroactive reparenting as an open question** (C-2). Resolved by
  [D-036](#d-036--units-cannot-be-reparented-a-unit-that-moves-is-a-new-unit): not permitted
  at all.
- **`membership_type.category`, `min_age`, `max_age`, and the age-out workflow.** Removed by
  [D-038](#d-038--membership-is-ageless).
- **`unit_membership`** (the name, and the claim that sub-unit belonging is a species of
  membership). Renamed and reframed by
  [D-041](#d-041--belonging-to-a-sub-unit-is-a-participation-record-not-a-membership).
- **The bulk scope-exposure tool**, its `bulk:` reason marker, and integrity check 12.
  Removed by [D-045](#d-045--the-bulk-scope-exposure-tool-is-removed); their replacements are
  audiences ([D-042](#d-042--grants-may-target-audiences-not-only-individuals)).
- **Background checks in every form** (`requires_background_check`, the permission pair, the
  requirement code, the `background_check_officer` role, the expiry report). Removed by
  [D-043](#d-043--no-background-checks-are-recorded-in-this-system).
- **`requirement_code` and `membership_request_requirement`.** Removed by
  [D-044](#d-044--nothing-gates-a-membership-request-except-identity-and-payment).
- **The "condition only a narrow set of permissions on membership" recommendation** (a
  recommendation, never a numbered decision). Reversed by
  [D-039](#d-039--member-permissions-require-a-current-paid-membership): the resolver *does*
  evaluate membership state, with guardianship, ownership and exempt role classes carved out.
- **`role.valid_from` / `valid_to`, the `role.retire` permission, and the resolver's check on
  a role's own period** — all introduced by
  [D-052](#d-052--roles-are-runtime-data-the-seed-set-is-not-a-specification) and removed the
  same round by [D-053](#d-053--a-role-is-valid-always-only-its-assignment-is-temporal). A
  role is a definition and is valid always; the period lives on `role_assignment`. The
  superseded reasoning is kept in D-052's entry, because *why* it looked right is worth
  knowing.
- **`role.requires_membership` as the *only* way to waive the gate.** Widened by
  [D-051](#d-051--the-membership-gate-is-waived-by-a-permission-not-only-by-a-role-flag): the
  flag survives and still answers "is this role membership-dependent?", but a person-level
  `system.gate_exempt` permission now waives the gate for a named individual regardless of
  which roles they hold. The original framing — in which D-6 was a question about which *roles*
  to exempt — is what this supersedes.
- **The seeded sub-unit vocabulary** (`pack`, `group`, `team`, and before them the
  `national`/`region`/`district`/`group`/`troop` ladder). Removed by
  [D-054](#d-054--the-sub-unit-vocabulary-is-not-seeded-the-organization-defines-its-own-types):
  the unit-type seed is the root and nothing else, and the organization defines its own types
  as runtime data. The words still appear across these docs as illustration — they are not
  types the system ships with.
- **`household` and `household_member`**, plus `fee_obligation.household_id`, its CHECK arm,
  `ix_obligation_household`, and integrity check 7. Removed by
  [D-057](#d-057--household-is-removed). The address is a temporal `person_contact` row of type
  `postal`. **Note this is not in the list as a reversal of [D-019](#d-019--household-membership-grants-no-access):**
  D-019's *principle* — shared address grants no access — is untouched and still binding, since
  the access never came from these tables. Only its subject was deleted.
- **The trimmed-permission-catalog direction implied by F-1** (a review that would cut the
  catalog down to what the organization needs now). Resolved the other way by
  [D-055](#d-055--the-permission-catalog-is-deliberately-comprehensive-and-granular): the
  catalog is a deliberately large, granular *menu*, and further permissions arrive with the
  modules not yet specified.

- **`<resource>.admin`, and the resolver's prefix match.** All sixteen per-resource wildcard
  permission codes (`person.admin`, `event.admin`, …) and the `X.admin` branch of `can()` were
  removed by [D-068](#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle),
  reversing [D-007](#d-007--every-resource-has-an-admin-level-that-subsumes-narrower-ones--reversed).
  **Two things sharing the name survive and are not reversals:** the `admin` **grant level**
  (rank 40), which is a different mechanism, and `dependent.admin`, which is a shorthand a
  person deliberately stores on one guardianship row rather than an implied capability. The
  failure mode D-007 was written to prevent — a new permission nobody bundled into a role — is
  **accepted**, and integrity check 18 is the net that replaces the wildcard.
- **The guardianship review queue at majority**, together with the computed candidate date it
  relied on. Removed by
  [D-069](#d-069--guardianship-ends-when-a-person-ends-it-the-system-takes-no-position-on-majority),
  reversing [D-024](#d-024--guardianship-does-not-auto-expire-at-majority--reversed). Note the
  direction: the replacement is **not** auto-expiry. Both automatic behaviours went. D-024's
  *conclusion* — never silently strip a legally valid arrangement — is kept; its mechanism was
  a deferral that still asserted a date the system cannot justify.
- **The "require `valid_to` on high-authority role assignments" recommendation** (F-3, a
  recommendation, never a numbered decision). Withdrawn by
  [D-071](#d-071--nothing-forces-a-role-assignment-to-end-the-gate-and-the-report-are-the-control):
  the membership gate already expires what an expiry date would have expired, for the same
  population, without inventing a date. Read together with D-053, which placed all the weight
  on `role_assignment.valid_to` — the human review report is now the entire control.
- **The proposal to give `event` a `min_age`/`max_age` pair** (raised as EV-1 within this
  round, never built). Declined by
  [D-070](#d-070--an-event-has-no-age-ceiling-the-grant-is-the-rule): a registration-time
  condition the capability model does not know about is the first rule-engine rule. No
  reversal, since nothing was shipped — recorded here because the idea will return.
