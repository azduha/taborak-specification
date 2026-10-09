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

## D-007 — Every resource has an `admin` level that subsumes narrower ones

**Status:** decided (from your answer)
**Date:** initial design

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

**Status:** decided
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
([D-024](#d-024--guardianship-does-not-auto-expire-at-majority)) all still work this way.

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

## D-024 — Guardianship does not auto-expire at majority

**Status:** assumption ⚠ *confirm*

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
