# Decision Log

Decisions taken, with the reasoning that produced them. Recorded so they are not
re-litigated from scratch — and so that when a decision is reversed, the reason for the
original choice is visible.

**Status values:** `decided` — settled, the data model reflects it *(since D-072: the documents, not a schema file)*. `proposed` — recommended,
awaiting your confirmation. `assumption` — taken by default, stated in italics in the
docs, easily reversed. `reversed` — no longer in force; the entry is kept, marked, and the
replacement is linked. Reversals are also listed together in
[Reversed decisions](#reversed-decisions), which sits where it was written — **mid-way through this log**,
between D-080 and D-081, not at the end. It has not been moved, because a section with a stable anchor is
worth more than a section in a tidier place.

**Five SQL fences survive in this log, and only here.** [D-072](#d-072--the-documentation-carries-no-sql-the-schema-is-the-orms-job) moved the schema out of the
documentation, but it did not rewrite the entries that had been written *in* the schema — at
[D-035](#d-035--one-root-unit-all-sub-units-nest-arbitrarily-beneath-it),
[D-041](#d-041--belonging-to-a-sub-unit-is-a-participation-record-not-a-membership),
[D-060](#d-060--eligibility-is-capability-there-is-no-separate-rule-engine),
[D-066](#d-066--payment-confirms-the-place-and-the-release-deadline-is-the-one-automatic-transition)
and [D-068](#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle). Each is a
**quotation of the shape a decision was made in**, and each says below it where the requirement
actually lives now. No later entry adds a fence: the rule for writing this log from here is
[D-081](#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now)
— state the requirement, name the layer that owes it, and let an identifier be a name rather than
an actor.

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

**Superseded by [D-097](#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row), outright: the table is gone.** Its reasoning that a type is a label and
not a permission survives into `person_group`; the self-referencing hierarchy it was proud of is the
exact thing the round deleted.

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

**Amended again by [D-079](#d-079--the-guardianship-channel-is-entered-by-shape-not-by-permission-name),
and this reaches the sentence above the amendment.** "Each dispatching from the permission's
namespace" was how the channels were *found*, and it is gone: dispatch is now `subject ≠ actor`
for guardianship, and `system.` remains the only namespace with resolver-visible meaning. **The
four channels themselves are untouched** — that part of this decision was durable for six rounds
and is the part worth keeping. What the namespace rule turned out to be was a way of skipping the
guardianship channel whenever the permission's *name* happened not to mark it as a guardian act,
which is a thing a name cannot do. **Note the shape of the failure for future amendments: the
channel list was right and the routing over it was wrong, and every document that cited the
routing copied the error.**

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

**Superseded by [D-099](#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality): the levels are gone, so the bug this guarded is unconstructible.** The hazard
is not forgotten — the one surviving ordered triple, a guardian's `none` / `view` / `write`, still sorts
wrong alphabetically, and [data-model/00-conventions.md](../data-model/00-conventions.md) says so where
this entry used to.

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

**See:** [../domain/06-authorization-model.md](../domain/06-authorization-model.md#21-the-founding-rule-and-what-is-left-of-it),
[../data-model/05-authorization.md](../data-model/05-authorization.md#5-scope_exposure--deleted-by-d-097).

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

**Superseded by [D-100](#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape), along with the position module.** That more than one person may hold an
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

**Note.** Position is **not** authority ([D-005](#d-005--permissions-are-grants-never-derived-from-identity)).
Holding a position grants nothing by itself; `is_leadership` only *suggests* a
`role_assignment`.

**See:** [../data-model/02-organization.md](../data-model/02-organization.md#5-what-this-page-held-before-round-10),
[../domain/04-organization-structure.md](../domain/04-organization-structure.md#6-appointments-which-no-longer-end-at-a-position).

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

**Superseded by [D-097](#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row): there is one unit, and nothing nests, because there is no unit row to nest
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

**Superseded by [D-097](#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row) — there is no parent column left whose change could be refused.** This was
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

> **Amended after [D-072](#d-072--the-documentation-carries-no-sql-the-schema-is-the-orms-job).**
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

- **The cache must be invalidated on every membership transition**, including the yearly
  expiry sweep, which is a bulk event touching everyone at once. The cache design must be
  built for this from the start, not retrofitted.
- **A lapse silently removes access.** That is the intent, but "why can't I see this?"
  becomes a question whose answer is a date, not a decision someone made.
- **`role.requires_membership` changes meaning** — from "reported, drives a worklist" to
  "enforced by the resolver". The "leaver with access" report remains useful, since it now
  detects roles that should have been closed rather than the mechanism doing the blocking.

**See:** [../domain/06-authorization-model.md](../domain/06-authorization-model.md#6-the-resolver),
[../data-model/05-authorization.md](../data-model/05-authorization.md#10-the-resolver).

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

**Reversed as to the sub-unit by [D-097](#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row); kept as to the distinction by [D-098](#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority).** Being a member and
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
([domain/06 §2.5](../domain/06-authorization-model.md#21-the-founding-rule-and-what-is-left-of-it)).

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

**Superseded by [D-097](#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row). The crossing is gone because both of its sides are gone.** The property this
bought — that access to a body's members had to be granted *by that body*, by people who recruited the
leader and can be asked — is recorded as **lost** in `docs/README.md` and in D-097's own costing, rather
than being dropped quietly.

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
[03-membership.md §5.1](../data-model/03-membership.md#5-unit_participation--deleted-by-d-097)).
This will be misread as a mistake by someone who assumes a parent can see its children. It is
not a mistake, and the catalog says so in place.

**See:** [../domain/06-authorization-model.md §2](../domain/06-authorization-model.md#21-the-founding-rule-and-what-is-left-of-it),
[../data-model/05-authorization.md §5](../data-model/05-authorization.md#5-scope_exposure--deleted-by-d-097).

---

## D-050 — A renewal inside the window extends the existing root participation row

**Status:** decided (from your answer)
**Date:** refinement round 4

**Superseded by [D-097](#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row) and [D-098](#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority): there is no participation row, so a renewal extends nothing but
the `membership`.** The renewal-window semantics [D-040](#d-040--the-fee-expires-yearly-a-date-tracked-renewal-window-replaces-a-grace-status)
defined are untouched.

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

**Reversed entirely by D-100.** [D-100](#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape) moves the gate into the audience expression, and this
entry's `system.gate_exempt` is deleted together with the lockout hazard it documented. The diagnosis
that produced it — a membership check performed *inside* `can()` is a lockout nobody can see — is still
the reason the round kept every one of these tests out of the resolver.

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

**See:** [../data-model/05-authorization.md §3](../data-model/05-authorization.md#3-role--an-office),
[../data-model/05 §12](../data-model/05-authorization.md#12-what-the-organization-starts-with),
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

**Superseded by [D-097](#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row): there is no unit-type vocabulary left to seed or to withhold.** 'The
organization defines its own labels and the platform ships none' transfers intact to `person_group` and
`role`, where it remains the rule.

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
([data-model/02 §10](../data-model/02-organization.md#7-seed-data)); it is now true with no
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
change is confined to [data-model/02 §10](../data-model/02-organization.md#7-seed-data).

**See:** [../data-model/02-organization.md §10](../data-model/02-organization.md#7-seed-data),
[../domain/04-organization-structure.md §1–2](../domain/04-organization-structure.md#1-the-organization-is-one-unit-and-the-unit-is-a-scope).

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

**Ownership reversed by [D-102](#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it); the dated-occasion half stands.** An event is still an occasion with
dates rather than a recurring template, and still has exactly one set of dates. There is simply no unit
for it to belong to, and the people connected to it are named by selectors that bind to it.

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
individually is 200 grant rows — but opening an event to members is **one**, which the shape of the
row made visible at the time:

```sql
INSERT INTO access_grant (scope_type, scope_id, audience_id, level)
VALUES ('event', :camp_id,
        (SELECT id FROM audience WHERE code = 'all_members'), 'contribute');
```

*The requirement now, without the statement: an `access_grant` may address an **audience** instead of
a person, so "everyone who is a current member may take part in this event" is one row rather than
one per member — [05-authorization §8](../data-model/05-authorization.md#8-audience--grants-that-target-a-set-of-people).*

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
[data-model/05 §7](../data-model/05-authorization.md#7-permission_level--deleted-by-d-099).

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
[appendix/permission-catalog.md §9](../appendix/permission-catalog.md#9-there-is-no-dependent-namespace).

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

**Superseded by [D-102](#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it).** The argument's shape survives — an item's people are *named*, never
inherited from a container — but with no unit and no owner the question 'whose event is this?' has no
column left to answer it from.

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

**See:** [../domain/07-events.md §6](../domain/07-events.md#6-how-authority-reaches-an-event),
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
produces. The predicate as decided:

```sql
-- Only at a full event, only with a fee configured, only past the deadline,
-- only unpaid, only self-service, never a cancelled event.
e.fee_schedule_id IS NOT NULL
AND e.waitlist_deadline IS NOT NULL
AND e.waitlist_deadline < now()
AND r.source = 'self' AND r.is_confirmed = false
AND e.cancelled_at IS NULL
```

*The requirement now, in words: release happens **only** at a full event that has a fee, a deadline
that has passed, an unpaid self-service registration, and is not cancelled — six conditions, each of
which is load-bearing, and the list is the rule rather than an illustration of it. Stated in
[08-events §5](../data-model/08-events.md#when-an-unpaid-registration-releases-its-place).*

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
the existing list in [../data-model/05 §11](../data-model/05-authorization.md#11-invariants-to-verify).
It was written as an executable query, and this is it as decided:

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

*The requirement now: **every assignable permission that no role bundles is reported**, which is the
net the `.admin` wildcard used to be; the check is item 18 of
[05-authorization §11](../data-model/05-authorization.md#11-invariants-to-verify), and like the other
eighteen it is now something to be verified rather than something that runs.*

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
[../domain/06-authorization-model.md §4](../domain/06-authorization-model.md#4-roles-are-offices-groups-are-company).

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

**See:** [../data-model/04-relationships.md §2](../data-model/04-relationships.md#2-the-guardians-right-none-view-or-write),
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

**See:** [../data-model/05-authorization.md §4](../data-model/05-authorization.md#4-role_holder--who-holds-an-office),
[../open-questions.md F-3](../open-questions.md#f-3--closed--nothing-forces-an-assignment-to-end).

---

## D-072 — The documentation carries no SQL; the schema is the ORM's job

**Status:** decided (from your answer) — **closes F-4a**
**Date:** refinement round 6

**Your answer.** Asked whether the permission catalog should be *generated from* the seed data
rather than maintained beside it, you answered **"Delete the schema, I will use ORM anyway."**

**The question was a symptom.** F-4a was about two lists disagreeing. The real cause is that the
documentation was asserting a deployment. It carried **4,689 lines of PostgreSQL across 19
files — 31% of the repository**: every `CREATE TABLE`, a `can()` function, trigger bodies,
91 `INSERT INTO permission` rows whose only purpose was to make a list executable, and one
integrity check whose entire job was to read `pg_proc` and grep a function definition for a
string. Under an ORM, not one of those lines would ever be run as written. Hand-written
migrations and ORM-generated migrations disagree about who owns the schema, and the docs
asserting DDL was the losing side of that argument before it started.

**Decision.** No SQL in the documentation. Field lists, types at the level of *what kind of
thing this is* (a period, an amount, an identifier), nullability, uniqueness, no-overlap rules,
temporality, indexes that exist for a reason, and derived facts are all stated as
**requirements**, in the document that owns the entity.

**The deletion is a translation, and this is the part that matters.** The DDL was not
illustration; in most places it was the only *precise* statement of a rule, and prose beside it
was the argument. Deleting the block and keeping the argument would silently drop the rule.
What must survive as written requirements, at minimum:

- the **no-overlap** rules — one open participation per person per unit, one open
  guardianship per pair, one open role assignment per person-role-scope, no two overlapping
  current contact points of one purpose. The *rule* is the design; the GiST index that
  PostgreSQL happens to use for it is not
- **the resolver's channels and their order** ([D-010](#d-010--role-assignments-and-access-grants-share-a-scope-model-and-a-resolver))
- **three-valued `was_present`**, where `NULL` means "no register was taken" and not "absent"
  ([D-067](#d-067--presence-is-a-three-valued-fact-on-the-registration))
- **`birth_date_precision`**, because an imported `1990-01-01` often means *year 1990*
- **tombstone and redaction both survive on `person`**, with the two partial indexes that
  exist because every ordinary listing excludes both
- a person may not be merged into themselves, and `merged_into` / `merged_at` are set together
  or not at all

**A rule for writing the docs from here.** Where a rule can only be stated precisely enough to
be checked, state it that precisely. *"A guardianship may not overlap another guardianship for
the same pair"* is a requirement. `EXCLUDE USING gist (guardian_id WITH =, dependent_id WITH =,
period WITH &&)` was that same requirement wearing an implementation's clothes.

**What got genuinely weaker, which should not be written as though it were free.** The 19
integrity checks were executable. They are now **invariants to be verified by something** —
listed in the document that owns them, with no query attached. The one that suffers most is the
time-bomb added in the last round, which failed the build if `.admin` prefix-matching ever
reappeared in the resolver
([D-068](#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle)). It is now
a sentence in a Markdown file. **A prohibition nobody runs is a convention, not a guard.** It
stays, because the alternative is silently forgetting it existed; it should not be described as
equivalent.

**Seed data goes with it.** There is no seed `INSERT` set, so there is no seeded role list and
no seeded permission list in the docs. This is what
[D-052](#d-052--roles-are-runtime-data-the-seed-set-is-not-a-specification) already argued —
roles are runtime data and the seed set is not a specification — and D-072 removes the one
place the docs kept pretending otherwise. Starter roles and starter permissions are described
as *what the organization begins with*, not as rows.

**F-4a closes by dissolution.** With no seed block there is exactly one list of permissions,
which is the catalog. Two artifacts cannot drift when only one of them exists.

**Two-way door?** No. Re-deriving 4,689 lines of DDL from prose is a redesign, not a
restoration — the constraints encode decisions the prose does not always restate. Git has them.

**See:** [../data-model/00-conventions.md](../data-model/00-conventions.md),
[../open-questions.md F-4a](../open-questions.md#f-4a--closed--the-catalog-is-the-only-list-now).

---

## D-073 — Guardianship is administered by its own parties, not by staff

**Status:** decided (from your answer) — **closes E-5**
**Date:** refinement round 6

**Your answer.** *"The guardian has the same rights as the user, so they can modify their own
guardians as well as the guardians with the write permissions. There is no need to take this
through the management team."* and, when asked how far that reaches, *"Guardian can be assigned
by other guardian."*

**Decision.** **The parties to a guardianship are principals on that row, not third parties
holding a grant on it.** A guardian may end the arrangement, may add another guardian to the
same child, and may change the permission level of the row they are a party to. The adult who is
the *subject* of a guardianship may end it over themselves. **None of these routes through
staff.** A staff member remains *a* way for it to happen and is never *the* way.

**This is the founding principle, applied one level down.** The rule this system was built on is
that authority over a nested thing originates at that thing and cannot be claimed from outside
it; the organization itself may not decide permissions over a sub-unit, and only the system
administrator is exempt. [D-031](#d-031--no-downward-inheritance-of-authority-scope_exposure-is-the-only-crossing)
applied that to units. **A guardianship is a nested thing, and its "unit" is the people in it.**
A staff role reaching in to decide who is responsible for a child is exactly the move the
authorization model refuses everywhere else.

**E-5 closes, and it closes differently from every option on offer.** E-5 asked how an adult
ends a guardianship over themselves and offered three shapes — support request, ownership
channel, request object — all of which assumed the answer must come from *somewhere other than
the people involved*. It does not. Note also that the answer is not the **ownership** channel:
ownership is *your own record*, and a guardianship row is not the subject's record any more than
it is the guardian's. It is a record **of a relationship between them**, and both parties hold it.

**Mechanically this is a direction, not a fifth channel.** The resolver has four channels and
[D-010](#d-010--role-assignments-and-access-grants-share-a-scope-model-and-a-resolver) keeps them
at four. The guardianship channel already asks *"may guardian G act on D's records?"*; D-073 gives
it a second question, *"may a party act on the guardianship row itself?"*, answered for exactly
three acts — end the row, add another guardian, change the permission level. Adding a channel
would have been the same capability at the price of touching every document that enumerates them,
and enumeration is how the order stays a rule.

**Read D-069 and D-073 as one decision in two halves.** D-069 refused to let a birthday end a
guardianship and deleted the review queue, on the grounds that a person decides. It left the
question of *which person, using what* open — the exit it assumed had no door. D-073 is the
door. Without it D-069 was a refusal with no alternative; with it the pair says something quite
coherent: **a legal relationship between two people ends when one of those people says so, and
the organization's job is to be told, not to permit it.**

**The asymmetry, stated plainly, because it is real.** A guardian may appoint a guardian. So
anyone with authority over a child can give a second person that same authority with no
approval from the organization — the ordinary case being a mother adding the father, and the
case that is not being everything else. The design accepts this and holds one line instead:
**the act is attributed.** Who added whom, when, from which account, is audited, and the other
party is notified. That is a deterrent and an evidence trail, not a prevention.

**Not decided:** whether adding a guardian over a **minor** should notify anyone at the
organization beyond the audit log, and whether a subject may refuse a guardian appointed over
them. See **E-6**.

**See:** [../data-model/04-relationships.md](../data-model/04-relationships.md),
[../open-questions.md E-5](../open-questions.md#e-5--closed--the-parties-administer-their-own-row).

---

## D-074 — A guardian's rights are `none`, `view`, or `write`. Nothing more granular

**Status:** decided (from your answer) — **supersedes the mechanism of D-020; deletes `dependent.*`**
**Date:** refinement round 6

**Your answer.** *"Guardian rights should be only 'none', 'view', or 'write', nothing more
granular."*

**The docs had it the other way round, deliberately.** `guardianship_permission` was a table of
per-capability grants — `dependent.profile.view`, `dependent.medical.admin`,
`dependent.consent.admin`, `dependent.event.register`, `dependent.fee.pay` — and the glossary
asserted *"Being a guardian grants nothing by itself. Every capability is a separate, revocable,
audited row."* That was drawn as a consequence of the standing instruction that both read and
write permissions be explicit. **It went further than that instruction said: explicit and
granular are not the same property.** Explicit means *nothing is implied by identity*. That is
fully preserved here — a `guardianship` row with level `none` grants nothing at all.

**Decision.** **One value per guardianship row, from exactly three: `none`, `view`, `write`.**
Not a capability list. A guardian either cannot see the child's records, can see them, or can
change them.

**It is the same ladder, not a new one — which is the part that keeps the model honest.** The
design already ranks authority as `revoked`(0) < `view`(10) < `contribute`(20) < `manage`(30) <
`admin`(40) and compares by integer, never by string
([D-012](#d-012--status-strings-compare-by-rank-never-lexicographically)).
The three guardian rights map onto it: `none` → 0, `view` → 10, `write` → 20. **Guardian
authority is therefore a range of an existing ladder, not a parallel enum**, and the resolver
compares it with the machinery it already uses for grants. A fourth guardian value would have
been the beginning of a second authorization model.

> **Amended by [D-099](#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality),
> which deleted the ladder this paragraph leans on.** The three values and everything they mean stand — the
> decision was never the numbers — but there is no rank left to map onto. The comparison now runs against a
> column on the permission: **`permission.right_kind ∈ read | write`**, where `none` covers nothing, `view`
> covers the codes marked `read`, and `write` covers both
> ([data-model/05-authorization.md §1](../data-model/05-authorization.md#right_kind-a-column-with-exactly-one-customer)).
> That column has exactly one customer, and this entry is who it was added for. **The paragraph's real work
> was never the shared arithmetic:** a guardian not being staff is carried by the channel's shape test
> ([D-079](#d-079--the-guardianship-channel-is-entered-by-shape-not-by-permission-name)) — a check that is
> not about this child never reaches the guardianship channel, whatever its right level. And the closing
> warning survives intact, only cheaper to honour: a fourth value would still be the start of a second
> authorization model, and three values against two kinds is a lookup rather than a scale to keep in step.

**What this deletes.** Every `dependent.*` permission code, including `dependent.admin` and the
three sub-resource `.admin` codes that D-068 deliberately exempted. The consequence is worth
noticing: **after D-068 deleted `admin` as a wildcard and D-074 deletes it as an action, the
only things in the entire system still spelled `admin` are `access_level.admin` (a rank) and
`system.admin` (the one wildcard permission).** The word is no longer ambiguous three ways; it
is ambiguous two ways, and the third is recorded as deleted.

> **And since [D-099](#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)
> deleted the ladder, it is ambiguous one way.** `access_level.admin` was a rank in a table that no longer
> exists; **`system.admin` is now the only live permission code in the system whose last segment is not an
> action**, and it is allowed to be one for the two reasons D-104 records: its meaning is defined by the
> resolver rather than read off the name, and D-068 exempted it explicitly rather than by silence.

**What it gives up, written down rather than discovered later.** It is no longer expressible
that *this* guardian may register the child for events but may not read the medical record, or
that a grandmother may see the roster but nothing else. Under D-074 she either can see
everything about her grandchild or nothing. The rescue is that `write` is not `manage`: a
guardian at `write` still cannot do organization-wide things, cannot see a *different*
dependent's records, and cannot reach beyond the records the dependent's own record contains.
**If the split turns out to be needed in real operation it is a new decision (E-7), and it
should not be reintroduced as a permission nobody argued for.**

**D-046 survives, simplified.** Defaults still differ by how the guardianship came into being —
a parent recorded at creation starts at `write`; a court-appointed guardian and a
grandmother-added emergency contact start elsewhere. What differs is now one value instead of a
set.

**See:** [../data-model/04-relationships.md](../data-model/04-relationships.md),
[../appendix/permission-catalog.md](../appendix/permission-catalog.md),
[../open-questions.md E-7](../open-questions.md#e-7--closed--one-level-cannot-separate-the-medical-record-from-the-profile-and-nobody-wanted-to).

---

## D-075 — Money arrives from a bank API; a payment is requested by variable symbol and QR code

**Status:** decided (from your answer) — **closes finance questions 3, 5 and 6**
**Date:** refinement round 6

**Your answer.** *"Collection via gateway is the closest. It will be collected from the bank API
and payments will be requested through variable symbol + a QR code."*

**This is not the gateway the finance document was braced for.** Its question 6 anticipated a
*card* gateway and listed what that drags in: checkout, webhooks, disputes, chargebacks,
reconciliation, PCI. What you describe is the **bank-account** model, and it is a different
animal: nobody pays by card through this system. The system issues a **payment request**
carrying a **variable symbol**; the payer is shown that symbol and a **QR code** containing it;
their own bank moves the money; the **bank API reports the incoming transfer with the symbol
still attached**. The system never touches the payment — it reads a statement.

**Four consequences, in descending order of how much they change the schema.**

1. **The variable symbol is the design, so it must be unique forever.** It is the only
   correlation key between *"we expect money for this membership"* and *"money arrived at this
   account"*, which makes the payment request — not the payment — the entity the finance module
   is built around. Uniqueness is not per year, not per membership, not per unit: **a symbol
   issued in 2019 must never resolve to a 2026 obligation**, because bank statements are
   replayed and late payments are the entire reason the renewal window exists.
2. **A symbol is a sequence, never a derivation.** Anyone can type eleven digits into a payment
   form. A symbol derived from a birth date, a membership id or a member number is guessable,
   and guessing one redirects a stranger's money into a child's financial record — a wrong fee
   balance, a membership that appears paid, a child recorded as covered who is not. Unguessable
   is not a privacy preference here; it is the integrity of the ledger.
3. **There are no reversals, so there is almost no status column.** Bank transfers do not
   bounce, are not disputed by the payer's bank and do not expire. `payment.status` needs
   nothing resembling `pending`, `failed`, `declined` or `disputed`. **A refund is a second
   payment in the opposite direction, not a transition of the first.** The status enum that
   question 3 asked about collapses, and refunds — a policy question with no answer for six
   rounds — mostly answer themselves.
4. **A QR code is a rendering, not data.** It encodes the symbol, amount and recipient that
   already exist. No stored image, no re-generation job, nothing to invalidate.

**The consequence for D-040 is the one that matters operationally.** The renewal window opens a
new membership period *at* the expiry date when payment lands inside the window, and D-040's
own note said the reliability of that rule depended on payment dates arriving reliably. Until
now they arrived when somebody noticed a transfer. **They now arrive from the bank.** The
backdating rule stops being a promise about someone's February and becomes a property of the
import.

**What is not decided, and is now the interesting part of the module.** Whether event fees get
a symbol as well as membership fees; whether a symbol is issued per person, per membership
period, or per individual liability (a camp is a separate payable from a fee); and what the
amount mismatch means when a payer enters 500 for a 550 request. See **F-10**.

**See:** [../data-model/07-finance.md](../data-model/07-finance.md),
[D-040](#d-040--the-fee-expires-yearly-a-date-tracked-renewal-window-replaces-a-grace-status).

---

## D-076 — Money that cannot be matched waits for a person

**Status:** decided (from your answer) — **closes EV-3 and finance question 1's sibling**
**Date:** refinement round 6

**Decision.** A bank transfer that resolves to no live payment request — unknown symbol, the
symbol of a cancelled event, an already-satisfied request, an amount that does not match, more
than the request asked for — is recorded as an incoming transaction and **enters a queue**. The
system neither applies it nor returns it.

**The queue's outcomes, all chosen by a human:** attach it to a different request; split it
across several; record it as a donation with no obligation behind it; or refund it by hand.

**Why not auto-apply by payer identity, which is the tempting answer.** Because the case it gets
wrong is not the edge case. *A parent with two children pays one amount against one symbol* is
the ordinary shape of family payment in a youth organization, and an identity-based fallback
resolves it to whichever child the query reaches first. A fee recorded against the wrong child
is simultaneously a finance error, a membership that appears paid when it is not, and — where the
fee buys insurance — a coverage record that is untrue. **The fallback would be wrong on the
common path, which is the one place a fallback is never allowed to be wrong.**

**Why not auto-refund.** It requires the bank integration to work outbound as well as inbound —
a second integration, with its own authorization. And it returns the grandparent's attempt at a
camp contribution.

**Where most of the queue's volume will actually come from: cancellation.** [D-064](#d-064--there-is-no-event-status-visibility-is-the-permission-model)
made cancellation a recorded fact rather than a state, which means the event survives, the
registrations survive, and **so does an outstanding payment request against an occasion that is
not going to happen.** So: cancelling voids the outstanding requests, and money that had already
arrived becomes a queue item for a person to refund or carry forward. **This is EV-3's answer**,
which is why EV-3 is closed rather than deferred to finance.

**The pattern, third occurrence.** Across six rounds the design has permitted exactly two
automatic state changes — the fee sweep ([D-040](#d-040--the-fee-expires-yearly-a-date-tracked-renewal-window-replaces-a-grace-status))
and the waitlist release
([D-066](#d-066--payment-confirms-the-place-and-the-release-deadline-is-the-one-automatic-transition))
— and refused every other offer to act on a person's behalf. D-076 is the third refusal, and
the first in the opposite direction: **the earlier two released a person from something they
owed; this one declines to release money from the person it belongs to.** Unmatched money is a
fact with no subject, and per
[D-059](#d-059--unanswered-is-the-absence-of-a-row-a-registration-stores-two-values)'s discipline
the absence gets stored rather than inferred.

**See:** [../data-model/07-finance.md](../data-model/07-finance.md),
[../open-questions.md EV-3](../open-questions.md#ev-3--closed--cancelling-voids-the-request-and-paid-money-queues).

---

## D-077 — Messaging is direct by default, `broadcast` is an ordinary scoped permission, and the recipient chooses the channel

**Status:** decided (from your answer) — **first decision of the communication module** *(amended by
[D-082](#d-082--a-direct-message-to-a-minor-is-mirrored-to-the-minors-guardians), which supplied the
thing this entry declined and left unprovided: a rule for the private message to a child)*

**Date:** refinement round 6

**Your answer.** *"There will be internal messaging through the system. Personnel with
'broadcast' permissions are able to send messages to everyone, other users only to direct
persons. The messages get then directed to email, push notifications or IM depending on the
user's choices."* — and, asked about the unit leader left out by that split, you chose a
**scoped** permission.

**Three decisions in one sentence, and the first is structural.**

1. **The system is the medium; email, push and IM are delivery.** A message is written once,
   internally, and then *distributed*. This is the load-bearing choice, because the alternative
   — the system as a mail relay — has no record of what anyone was told.
2. **Two sender tiers.** Everyone may write **direct** messages. **Broadcast** is a permission.
3. **The recipient chooses the channel.** The sender chooses who; the recipient chooses how it
   reaches them.

**Therefore: one message, one recipient row each, and the medium resolved at delivery.**
A `message` plus a `message_recipient` per addressee carrying read state; the channel is
selected per recipient against their own contact points. A bounced email is a failed delivery on
one channel, not a lost message. `person_contact.purpose` gains a messaging purpose and each
contact point carries its own opt-in, which is the existing contact-point model doing work rather
than a new subsystem beside it.

**`broadcast` is granted at a scope, which is the whole authorization model speaking again.**
Granted organization-wide it reaches everyone; granted on a unit it reaches that unit's people.
No new mechanism — role assignments already carry a scope. **A single global `broadcast` flag
would have made a pack leader announcing a 9 a.m. start either the holder of an
organization-wide power or the author of twelve identical messages, and the first of those is
precisely the arrangement every other part of this design exists to prevent.** Note that this
lands on scope authority rather than on audiences: *who may address* a set is authority over that
set, and authority over a set originates inside it.

**Age is not a sender concept, and that is a decision, not an omission.** The question asked
whether staff may address a child directly or only their guardians; the answer replaced it with a
sender-tier model that has no age in it. Consistent with
[D-070](#d-070--an-event-has-no-age-ceiling-the-grant-is-the-rule), there is no age branch in the
resolver. **The residue is stated rather than hidden: any account in the system may send a direct
message to any other account, including a child's.** The rule the communication section had
promised — *"a rule against contacting minors directly"* — is **not** implemented as a
restriction on senders. See **MSG-1** for the recommendation, which is to restrict *visibility*
rather than permission: direct messages reaching a minor mirrored to their guardians, so nothing
is blocked, nothing is secretly unread, and the resolver still has no age branch.

**Two-way door?** The delivery half yes — adding a channel is a new contact purpose. The sender
tiers no: once people can message each other, retracting that is a feature removal, and any
later safeguarding rule has to be written as surveillance over a channel that already exists.

**See:** [../domain/02-actors.md](../domain/02-actors.md),
[../appendix/permission-catalog.md](../appendix/permission-catalog.md),
[../open-questions.md § Communication](../open-questions.md#h-not-yet-designed).

---

## D-078 — An exposure extends an assignment, never a direct grant

**Status:** decided — **found by deleting the SQL, not by running it**
**Date:** refinement round 6

**Superseded by [D-097](#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row) with the exposure table itself.** Its distinction, that widening an
inherited reach is a different act from writing a grant, has no subject after [D-099](#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality): a grant has exactly
one shape, and there is nothing to extend it.

**What happened.** Translating the resolver out of SQL for
[D-072](#d-072--the-documentation-carries-no-sql-the-schema-is-the-orms-job) meant reading each
branch for what it *decides* rather than what it says. The unit-grant tier had two branches, and
the second one consulted `scope_exposure`. It joined the direct grant to `se.org_unit_id` while
also requiring `se.org_unit_id =` the unit being checked. Both conditions pin the grant to the
checked unit — which the first branch had already tested. **The branch could never succeed where
the first one failed.**

**It was not a vulnerability.** A branch that can only ever return true where another branch
already returned true grants nothing. The damage is to the reader: a tier that appears to widen
direct grants through exposures is a tier that will be trusted, reviewed and extended on that
basis. It survived every review of the SQL precisely because it reads correctly.

**The rule, now stated.** `scope_exposure.role_assignment_id` points at a **specific person's
assignment**. The unit is agreeing that *this person, in this role, for this period* may act here
— which is what makes the exposure legible as an act of the unit rather than a grant to a
whoever-holds. A direct `access_grant` contains no assignment for an exposure to attach to, and
a grant already at the checked unit needs no extension to work there. **So the role channel is
the table's only consumer, and the unit-grant tier matches exactly.**

**Why the tempting repair must be refused.** "Exposures don't extend my direct grant — that looks
like an oversight, let's add it back" produces a system where a unit that exposed *a treasurer
role assignment* has also, silently, exposed itself to every direct grant held by every person
who happens to hold some other assignment there. The repair would widen an exposure to cover
people the exposing unit never approved, in the one direction the founding principle forbids.
Anyone reaching for it should read this entry first, which is why it is a decision and not a
comment.

**What this says about D-072's trade.** The deleted SQL contained a bug and the prose cannot
contain it, because the prose does not have a dead branch. This is the one case where removing
the schema was an unambiguous improvement, and it is worth recording beside the cases where the
removal cost something real.

**Two-way door?** No, in the sense that matters: adding a second route back is a widening. In
every other sense yes — nothing here constrains a future mechanism that names a grant in an
exposure row deliberately, which would need a new column and a new argument.

**See:** [../data-model/05-authorization.md §5](../data-model/05-authorization.md#5-scope_exposure--deleted-by-d-097).

---

## D-079 — The guardianship channel is entered by shape, not by permission name

**Status:** decided — consequence of [D-074](#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular)
**Date:** refinement round 6

**Before.** The resolver picked a channel by string: a permission code beginning `dependent.` went
down the guardianship channel, everything else went down the ordinary path. This was elegant, and
it had a hole nobody noticed while it was true.

**The hole.** A parent correcting their child's address is performing `person.address.edit`. That
code has no `dependent.` prefix — it is the same code a person uses to correct their own address.
**So the act did not route through guardianship at all.** It resolved against the parent's own
roles and item grants, which say nothing about this child, and the answer was deny — correct by
accident, for a reason that had nothing to do with the relationship that made the act legitimate.
Any future `person.*` act a guardian needed would have inherited the same dead end, and the fix
each time would have been a new `dependent.*` code, which is how the namespace grew to eighteen.

**Now: the channel is entered when the subject of the act is not the actor.** The resolver is
already handed both — the actor, and the owner of the thing being touched. Compare them; if they
are different people, ask the guardianship question. **That question may answer only "yes".** If
the answer is yes the check is finished and the act is allowed; in every other case the channel
falls silent and the resolver carries on to the actor's own roles and grants. **It is not the last
word, and the paragraph below explains why that had to change as well** — the first draft of this
decision kept the old finality, and the two halves are inconsistent within one page, which is
itself instructive about how a rule outlives the reason it had.

**Three things this buys.** *(a)* Nothing escapes by naming: a permission added next year for a
field a guardian must edit is covered the day the field exists, because dispatch reads the shape
of the request rather than a list maintained beside it. *(b)* It is one comparison instead of a
prefix match against a namespace that has to be kept in step with the catalog by hand. *(c)* The
rule is stated in the resolver, where a reader looking for "how does a guardian get authority"
will find it, rather than in a column's comment.

**What it costs.** Dispatch is now invisible in the data. Under the prefix rule you could look at
a permission code and know which channel would answer for it; now you have to know whether the
check is being made about somebody else, which is a property of the call site, not of the
permission. **This is the price of every shape-based rule and it is worth paying here**: the
alternative was a rule that was legible and wrong. The audit side of it is unchanged — an act
performed on behalf of a minor is recorded as such regardless of which code was checked
([04-relationships §5](../data-model/04-relationships.md#5-acting-on-behalf--recording-it)).

**Where the boundary sits, because `subject ≠ actor` is far broader than guardianship.** A
treasurer entering a payment for a child, a leader marking a roster, a registrar correcting a name
they imported: all of these are subject≠actor checks, and none of them is a guardian acting on a
ward. If the channel answered for all of them, the treasurer would be asked whether they are the
child's guardian, told no, and **denied an act their role plainly authorises.** So the channel
speaks only when there is something to ask: **a live guardianship row joining this actor to this
subject, at this date.** No row, no answer, and the resolver falls through to the allow tiers
exactly as it always did. There is no age test in that guard, which is deliberate — the
guardianship row *is* the relationship, and adults who file one for themselves
([D-073](#d-073--guardianship-is-administered-by-its-own-parties-not-by-staff)) are covered by the
same two words as minors are. An age branch would also contradict
[D-070](#d-070--an-event-has-no-age-ceiling-the-grant-is-the-rule) and
[D-077](#d-077--messaging-is-direct-by-default-broadcast-is-an-ordinary-scoped-permission-and-the-recipient-chooses-the-channel),
both of which insist the resolver has no age in it.

**The consequence is a real weakening of the channel, and it should be read as such.** Under the
prefix rule the guardianship channel gave the **final** answer: `dependent.medical.view` was a
guardian-only code, no role held it, so "the guardian's right is `view`, this is a write" could
safely end the check. Now that the channel carries ordinary codes a role might also grant,
finality turns into a trap — **the parent who is also the event registrar, holding `view` over
their own child, denied the right to do their job.** So the guardianship channel now returns
**allows only**: sufficient right → true; insufficient, or `none`, or no row → silence, and the
actor's own roles and grants are still tried. What is *not* lost:

- **`none` still grants nothing**, which is what D-074 actually promised. It was never a promise
  to block unrelated authority.
- **A genuine prohibition is still available and still absolute** — an explicit deny in channel 0,
  which runs before everything and does not care about scope. That is where "this person must not
  touch this child's record" belongs, and it is stronger than what a guardianship level could do.
- Nothing an actor reaches by falling through is authority the guardianship row was hiding: their
  role already gave it to them, guardianship row or not.

**What is lost is the ability to say "not even your role".** No guardian's `view` can ever be
that sentence again. In a safeguarding system that sentence has to exist, and D-032 already put it
in the deny channel rather than distributed across capability levels — so the loss is of a
convenient place to write it, not of the mechanism.

**Two-way door?** Yes in principle, no in practice — the old dispatch can only be restored by
re-inventing the namespace D-074 deleted.

**See:** [../data-model/05-authorization.md §10](../data-model/05-authorization.md#10-the-resolver),
[../data-model/04-relationships.md §4](../data-model/04-relationships.md#4-how-the-resolver-uses-these-tables),
[../appendix/permission-catalog.md §9](../appendix/permission-catalog.md#9-there-is-no-dependent-namespace).

---

## D-080 — Five contradictions the translation surfaced, and how each was resolved

**Status:** decided — **each resolution is a correction, not a choice between options**
**Date:** refinement round 6

**Why this entry exists.** [D-072](#d-072--the-documentation-carries-no-sql-the-schema-is-the-orms-job)
required every SQL block to be read for what it *decides* before it was deleted. That reading is
the first time these documents were checked against themselves line by line, and it found five
places where a document said two contradictory things — in three cases three things, one of them
executable. **They had been invisible precisely because one of them worked.** A query that returns
the wrong rows is not visibly wrong. Each is resolved here rather than left as a note, because
with the SQL gone there is nothing left to disagree with the prose: **the prose is now the only
place the rule lives, so it has to be right.**

| # | The contradiction | Resolution |
|---|---|---|
| 1 | `identifier_scheme.is_unique` said a school id may repeat; the uniqueness rule applied to every scheme and never read the flag | **The flag decides.** A second child at the same school with the same number is not a duplicate identifier, and would have been rejected at import by a constraint its own table called wrong. [01-identity §7](../data-model/01-identity.md#7-person_identifier) |
| 2 | §9 of the identity document opened by saying its views encode "always exclude merged **and redacted**"; `v_person` excluded merged only, while §1 and §2 both required both | **Both exclusions.** A redacted child in a list of children is not a formatting issue. Rows still resolve; people do not appear. [01-identity §9](../data-model/01-identity.md#9-views) |
| 3 | The audit redactor kept an *always-redacted* list of free-text fields — and nothing read it | **Kept, and labelled as intent.** It is the clearest illustration in the whole repository of what a declarative list nobody consults is worth. [06-audit §2.2](../data-model/06-audit-and-import.md#22-redaction-before-logging) |
| 4 | The unit-grant tier appeared to widen direct grants through `scope_exposure`, and did not | Dead branch. **The rule is now stated once, in the direction that is true:** an exposure extends an assignment and never a grant. [D-078](#d-078--an-exposure-extends-an-assignment-never-a-direct-grant) |
| 5 | `is_leadership` lives on `position`, and the audience rule for `unit_leaders` read it as though it lived on `role` | **Fixed where it is read.** The audience is "holds a live assignment to a leadership *position* at that unit", which is what everyone had been assuming it meant. [05-authorization §8](../data-model/05-authorization.md#8-audience--grants-that-target-a-set-of-people) |

**One pattern, four instances.** Every one of these is a **second statement of a rule that the
first statement did not consult**: a flag beside a constraint, a view beside a section heading, a
list beside a loop, a column on the wrong table. Two copies of a rule diverge — the reason this log
exists at all — and the divergence is only found by someone reading both. That is also why the
permission catalog is now the catalog's alone, why §11 of the conventions points at Rules blocks
instead of restating them, and why the count in that sentence is not a coincidence.

**What was *not* resolved, in the same spirit.** Item 3's fix is a label, not an enforcement;
item 5's check still cannot run automatically; and a correction nobody re-tests is exactly how
item 2 got into the documents. **The five resolutions are therefore themselves invariants** — if
someone regenerates a schema from these documents and produces a per-table identifier constraint
or a redacted-inclusive listing, this entry is the thing that was violated.

**Two-way door?** No, and deliberately: each of these was a bug whose "fix" is indistinguishable
from a regression. If one returns, it returns as a bug report, not as a reversal.

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
- **Merge chains as an assumption.** Decided by
  [D-087](#d-087--merge-chains-stay-because-reversing-a-merge-is-a-supported-operation), in
  the same direction the assumption pointed — chains persist and `resolve_person()` walks them.
  It is in this list because of *how* it was argued: the docs justified chains by saying
  flattening would make unmerge impossible, which is a reason resting on a capability nobody
  had asked for. Reversing a human-approved merge is now a requirement, so the conclusion is
  unchanged and the argument behind it is not — and flattening, previously "faster", is now a
  trade against a named feature. The integrity check that read a tombstoned survivor as a
  breach was corrected the same round: under decided chains it is normal.
- **The audit trail as the permanent keeper of values.** Narrowed by
  [D-088](#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short) to a payload
  window of 24 months (rows survive; `old_values`/`new_values` are emptied). [D-085](#d-085--the-identity-machinery-stays-structured-the-boundary-is-rules-not-sensitivity)
  is **not** reversed and its overwrite-in-place stands, but its stated justification —
  "the trail is the history" — is true for two years and untrue afterwards, which changes what
  that decision costs. Read the two entries together; neither is complete alone.
- **"A historical roster may create a `membership` if there is payment evidence"** (the safe
  default kept open in `06-audit-and-import.md` §6). Retired rather than answered by
  [D-090](#d-090--the-legacy-corpus-is-thousands-of-roster-rows-with-numbers-and-no-money):
  the corpus carries no payment data at all, so the exception arm has nothing to fire on and the
  default is simply the rule. Historical rows are `unit_participation`; `membership` comes only
  from the current register. Recorded because the *reason* for the rule — an inferred open-ended
  membership would make a 2003 roster a current member with authority today
  ([D-039](#d-039--member-permissions-require-a-current-paid-membership)) — is the part worth
  keeping if a corpus with money in it ever arrives. **Retired outright one round later, which is the
  more instructive half:** the corpus turned out to state membership periods directly, so the rule was
  replaced by [D-093](#d-093--the-one-off-import-may-create-memberships-both-ends-dated) and the frame
  it rested on by [D-092](#d-092--the-corpus-is-people-and-events-and-it-names-no-units). The reason
  survives; the rule does not. A decision recorded from a description of the data is only as durable as
  the description.

- **"An audience does not nest", and `audience.kind`'s rule-*xor*-list split.** Both withdrawn by
  [D-091](#d-091--a-permission-group-is-a-rule-and-a-list-at-once-and-a-rule-may-name-another-group):
  a group is now a rule arm, a manual arm and an inclusion arm whose membership is their union, and a
  group may include another. Neither was ever a numbered decision — both were prose in
  `data-model/05 §8`, which is how they survived three rounds of review unexamined while doing real work
  (they are the reason "the crew, plus everyone who leads this pack" needed two grants and why a
  composition the organization asked for in round 9 had been silently impossible). The cycle the nesting
  ban existed to prevent is refused at the write instead, which is the same answer D-087 gave for merge
  chains one round earlier — **worth reading as the pattern rather than the reversal**: when a rule was
  written to prevent a hard case, the first question is whether the hard case can be refused at the write
  rather than defended against at the read.
- **`org_unit_type.allows_minors`, and the write-path check it drove** (integrity check 2 in
  `03-membership.md §7`). Removed by
  [D-095](#d-095--units-carry-no-restrictions-joining-one-is-somebody-elses-act): units carry no
  restrictions, and the control is that nobody joins a unit or takes a position in one themself. This is
  in this list because of what replaced it, not because a column went — a *flag on a type* became *a
  permission held by named adults*, which is D-081's "say who enforces it now" answered with a change of
  kind rather than a rename. The consequence is symmetrical: the system can no longer tell anyone which
  units are for children.
- **The correction made to `03-membership.md §5.1` in round 8** — that "an ordinary import touches
  neither arm of this pair", because a roster writes participations and no memberships. Reversed by
  [D-093](#d-093--the-one-off-import-may-create-memberships-both-ends-dated) within one round: the
  membership export writes memberships by the thousand, so the root-participation obligation points at
  the import again, which is what that section said before round 8 for entirely different reasons.
  Recorded because a *correction* that gets reversed is the kind a reader will not trust, and the reason
  to trust it here is that both rounds were wrong about the same unknown thing — the shape of a file
  nobody had read.

**Round 10 removed a dimension of the model, and the reversals below are the largest single set in this
log.** They are grouped rather than listed one per line, because they are not twelve independent
reversals: they are one diagnosis (*"I have over-specified the system and this complicates things"*)
drawn through the unit hierarchy, the authority ladder, the membership gate and event ownership at once.

- **The unit hierarchy itself** — `org_unit`, its types, names, relationships, participations and the
  upward `scope_exposure` crossing. Deleted by
  [D-097](#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row): there is one unit, it is the
  organization, and it is a **scope** rather than a row. Reverses D-008, D-035, D-036, D-041, D-049, D-050,
  D-054, D-078, D-096 and deprives [D-031](#d-031--no-downward-inheritance-of-authority-scope_exposure-is-the-only-crossing)
  of its subject. The property this bought — access to a body's children had to be granted *by that body* —
  is recorded in D-097 as lost, not as replaced.
- **The level ladder** (`access_level`, `permission_level`, the rank integer, and everything that compared
  levels). Deleted by
  [D-099](#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality): a grant is one
  permission code with an effect of `allow` or `deny`. This reverses
  [D-012](#d-012--status-strings-compare-by-rank-never-lexicographically) including the reason it was
  written (a level string compared alphabetically inverts the model — now there is no level to compare),
  makes [D-013](#d-013--explicit-deny-revoked-is-checked-before-everything)'s deny an effect rather than a
  level, and **deletes half of [D-032](#d-032--deny-is-absolute-locality-orders-allows-only)**: locality
  only ever ordered allows against each other, and a boolean answer has nothing to order.
  [D-074](#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular) survives on a new
  `permission.right_kind` column, which D-099 names as a column with exactly one customer.
- **The membership gate as a resolver clause** (`role.requires_membership`, `system.gate_exempt`,
  `person_holds_gate_exempt`). Deleted by
  [D-100](#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape), which moves the
  test into the selector: `MEMBERS * ROLE(x)` gates on current membership because `MEMBERS` is evaluated
  live, and leaving `MEMBERS` out is how a role is exempt. Reverses the enforcement half of
  [D-039](#d-039--member-permissions-require-a-current-paid-membership) and all of
  [D-051](#d-051--the-membership-gate-is-waived-by-a-permission-not-only-by-a-role-flag), including the
  lockout hazard D-051 had to document. **The posture reverses from default-on to opt-in**, and the new
  failure mode — a grant written without `MEMBERS` authorizing a lapsed member, silently — is answered with
  a report and an import count, not by the resolver.
- **Positions** (`position`, `position_assignment`, `is_leadership`, `max_holders`) and **`role_assignment`**
  (becoming `role_holder`, with no scope), by
  [D-100](#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape), which also
  deletes `role_permission`: a role confers nothing by itself, and the codes an office carries are the
  grants whose audience names `ROLE(x)`. The elected-versus-appointed distinction survives only as a role
  the organization invents. [F-12](../open-questions.md#f-12--closed--may-a-role-be-held-by-a-rule-as-an-audience-is)
  is closed, and the answer is no.
- **The audience's three arms, and the inclusion edge.** `audience.resolver_key`, `scope_parameter`,
  `audience_include` and `include_depth_limit` are deleted by
  [D-101](#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree), which replaces them with an
  expression over named sets stored as a tree of binary rows. This **amends
  [D-091](#d-091--a-permission-group-is-a-rule-and-a-list-at-once-and-a-rule-may-name-another-group) rather
  than reversing it**: the outcome D-091 wanted — composing *"the kitchen crew, plus whoever leads this
  pack"* in one grant — survives, and the intersection and difference it could not express now can be
  written. What dies with the edge table is the transitive walk, the graph-shaped cycle check and its CI
  assertion, because a tree cannot cycle. The one thing genuinely lost is one-edit widening
  (*"add the crew to everywhere this group is used"*), answered by naming the composite.
- **Event ownership** (`event.org_unit_id`, `can_event()`, the unit-authority rule). Deleted by
  [D-102](#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it),
  which reverses [D-058](#d-058--an-event-is-a-dated-occasion-owned-by-exactly-one-unit)'s ownership,
  [D-063](#d-063--an-event-is-an-artifact-of-its-unit-not-a-child-of-it) and
  [D-094](#d-094--the-root-unit-owns-every-imported-event), and answers "who is connected to this event?"
  with selectors that bind to the item being checked (`ORGANIZERS`, `PLACED`, `CONFIRMED`, …) instead.
  [D-062](#d-062--organizers-are-appointed-on-the-event-not-granted) stands untouched: an operand is a set,
  not a grant.

---

## D-081 — Rule names survive the deletion of their mechanisms; a renamed rule must say who enforces it now

**Status:** decided (editorial ruling, ratified this round)
**Date:** refinement round 6
**Follows:** [D-072](#d-072--the-documentation-carries-no-sql-the-schema-is-the-orms-job), [D-080](#d-080--five-contradictions-the-translation-surfaced-and-how-each-was-resolved)

**What was found.** With the DDL gone, roughly sixty sentences still credited a database object
with acting: "the trigger in §3 enforces it", "the schema cannot express", "`ck_request_rejection_reason`
requires a reason code", "refused by trigger (§8)". None was false when it was written. Each became
a **false claim about the present** the moment D-072 removed the thing it named, and a reader who
trusts the sentence does the one thing this corpus cannot afford — assuming a guarantee exists and
not writing it.

**Ruling 1 — the identifiers stay; the agency goes.** `ck_org_unit_closed`,
`uq_org_unit_single_root`, `uq_access_grant_live` and the rest are kept **as names of rules**, not
as claims about objects:

| Before | After |
|---|---|
| "`ck_org_unit_closed` states the invariant explicitly" | "**A unit cannot be closed without an end date** (`ck_org_unit_closed` is this rule's name)" + which layer carries it |
| "the trigger refuses deletion" | "Guard 2 is the rule, the no-cascade reference is what refuses it, and `event.delete` only decides who may ask" |

Deleting the names would be a repository-wide rename touching every cross-reference, and a rule with
a stable handle is worth more than a purer vocabulary. **The line is agency, not vocabulary:** an
identifier may survive its table as long as no sentence asks it to do anything.

**Ruling 2 — renaming the mechanism is never the fix.** Where a rule loses its enforcement, the
sentence must state what is now required **and which layer owes it**, in the register of
[data-model/00 §6a](../data-model/00-conventions.md#6a-who-enforces-an-invariant-now). "The trigger
guarantees X" and "X is validated in the model" are not adjacent statements; the first is a
guarantee on every path and the second is a friendly message on the intended one. Softening one
into the other without saying so is how a deleted schema turns into a silently weaker system. Where
the honest answer is "no layer enforces this and none can", the text now says that — *a convention,
not a guard* — rather than letting the reader infer it.

**Ruling 3 — a rule that lost both its guard and its report gets a report.** Three had neither,
which is worse than losing the guard alone, because a missing guard is at least visible to whoever
writes the migration:

| Rule | Where the guard went | Net added |
|---|---|---|
| `position.max_holders` | no constraint can state a count over other rows (F-10 shape 3) | [02-organization §9 check 9](../data-model/02-organization.md#6-integrity-checks) — over-limit means *bypassed*, unlike event capacity, which may be exceeded deliberately |
| Registration outside its window | Guard 1, inside the writing transaction | [08-events §10 check 9](../data-model/08-events.md#10-integrity-checks) — a row here is evidence about the code, not the data |
| `fee_obligation`, created by the code that places a registration | nothing ever enforced it | [08-events §10 check 10](../data-model/08-events.md#10-integrity-checks) — a confirmed place with no bill leaves every row individually correct |

One rule keeps **no** net, deliberately, with the absence named instead of smoothed over:
`org_unit.parent_unit_id` immutability ([D-036](#d-036--units-cannot-be-reparented-a-unit-that-moves-is-a-new-unit)).
A reparent leaves nothing malformed to count, so it became F-10's fourth shape rather than a check.

**One contradiction of D-080's class, found and settled.** §2.1 of
[data-model/06](../data-model/06-audit-and-import.md#21-the-trigger) said `DELETE` is outside the
audited operations "because nothing in this data model is hard-deleted", while §3's import revert
removes the `person`, `membership` and `unit_participation` rows a batch created. Written together
they meant **a rollback could erase live rows without a trace** — the one event someone is most
certain to ask about later. Settled in favour of the audit log: **a revert writes one audited entry
per deleted row, naming the batch**, and `DELETE` stays outside the audited operations only because
no other path reaches a business row with a delete.

**The residual that could not be closed.** Audit *completeness* used to be answerable from the
database's own catalog — ask which tables carry triggers, compare against the business tables. There
is no catalog to ask now: a table is audited because the code writing it remembers to, so the
nightly comparison runs between two hand-maintained lists, and **both can go stale together and
still report zero.** The replacement is an assertion over the paths that may write or delete a
business row; until that exists this is recorded as a known hole rather than as a solved problem.

**Ruling 4 — the decision log may quote SQL; nothing else may, and a quotation must say where the
rule lives now.** Five fences survived in this log, and deleting them would be the wrong
correction: an entry that says "the exclusion constraint drops `membership_type_id`" is *about* that
constraint, and rewriting it into prose would quietly revise a record of what was decided in order
to keep the vocabulary clean — the same mistake D-080 catalogued, arriving from the opposite
direction. So the fences stay, each followed by one italic line naming **the requirement as it is now
stated, the document that owns it, and the layer that owes it**. The header of this log says the same
thing once, so that no fence is read as a specification by someone who arrived at it directly.
That is the whole distinction: **the documentation describes a system; this log records how the
description got here, and a record is allowed to quote things it no longer endorses.**

**See:** [data-model/00 §6a](../data-model/00-conventions.md#6a-who-enforces-an-invariant-now),
[open question F-10](../open-questions.md#f-10--which-invariants-the-orm-cannot-express-and-who-writes-those)
(now four shapes), [D-072](#d-072--the-documentation-carries-no-sql-the-schema-is-the-orms-job).

---

## D-082 — A direct message to a minor is mirrored to the minor's guardians

**Status:** decided (from your answer) — **closes MSG-1**
**Date:** refinement round 7
**Follows:** [D-077](#d-077--messaging-is-direct-by-default-broadcast-is-an-ordinary-scoped-permission-and-the-recipient-chooses-the-channel)

**Your answer.** Asked which of the two available safeguards you wanted, having been shown that
[D-077](#d-077--messaging-is-direct-by-default-broadcast-is-an-ordinary-scoped-permission-and-the-recipient-chooses-the-channel)
had declined the sender restriction and left nothing in its place, you chose **mirror to guardians**.

**The rule.** A direct message whose recipient is a minor is delivered **also** to that minor's
guardians, and the sender is told, before sending, that it will be. Nothing is blocked. No permission
is involved, and no check in the resolver looks at an age.

**Why this direction and not the other one.** The corpus already refused an age branch at check time,
for events, in [D-070](#d-070--an-event-has-no-age-ceiling-the-grant-is-the-rule), on the ground that a
condition the capability model does not know about is the first rule in a rule engine nobody asked
for. Messaging was going to reintroduce exactly that condition by a different door. Mirroring gets
the safeguarding property without it: **the property nobody was ever arguing for was "an adult cannot
reach a child", and the property actually needed was "no private exchange about a child is secretly
unread."** Those are not the same rule, and only the second one survives contact with a volunteer
organization, where a restriction that inconveniences a leader on a Friday evening gets bypassed by
Monday — and a routinely-bypassed restriction is worse than none, because it teaches everyone that the
rule is decorative.

**Three things "mirror it to the guardians" does not say, settled here rather than in code:**

1. **Which guardians — those at `view` or `write`.** A guardian whose right level is `none` receives
   nothing. `none` is not an oversight; it is the organization having already decided that this party
   sees nothing about the child, and a safeguarding convenience is not a reason to reverse a recorded
   decision as a side effect of a message.
   **The consequence is named rather than left to be found:** a minor whose guardians are *all* `none`
   is exactly as unwatched as a minor with no guardian row at all, so both are reported together by
   the existing completeness check in
   [04-relationships §6](../data-model/04-relationships.md#6-invariants-to-verify). Mirroring must not
   become a channel through which `none` quietly stops meaning anything.
2. **Which set, as of when — frozen at send time.** The guardianships open at the moment the message
   is sent are the recipients, recorded into the delivery. A guardianship closed later does not lose
   its copy; a guardian added later does not acquire old threads. This is the same discipline that
   makes the audit log answer "what did this role say on that date" rather than "what does it say
   now" ([06-audit §2](../data-model/06-audit-and-import.md#2-audit_log)) — a safeguarding question
   about a past message has to be answerable against the arrangement that existed then, because the
   question "did anyone tell the father?" is asked months later, about a family that has since
   separated.
3. **Broadcast is not mirrored.** A scoped broadcast is addressed to a set, recorded, attributable,
   and not private; mirroring exists precisely for the private case, where "nobody saw this" is a
   claim nobody can check. Extending it to broadcast would deliver the same content twice to the same
   guardians and would blur the one distinction the rule depends on.

**What mirroring is explicitly not.** Not approval — nobody consents before a message is sent, so the
channel stays open and the organization stays out of the middle of ordinary communication. Not
delivery confirmation; the mirror inherits the recipient's own channel choice
([D-077](#d-077--messaging-is-direct-by-default-broadcast-is-an-ordinary-scoped-permission-and-the-recipient-chooses-the-channel))
and can therefore fail to be read exactly like any other message. And not a record of concern: it is
a copy, not a report, and the organization learns of a message only through the ordinary routes.

**The variant rejected, and why it will come back.** *"Only guardians and unit leaders may message a
child."* It is the sender rule wearing the visibility rule's clothes: it needs the age branch, it is
bypassed the first time it is in the way, and worst of all it **tells a child that the adult messaging
them has been vetted** — a claim the system cannot support, since no background checks are recorded at
all ([D-043](#d-043--no-background-checks-are-recorded-in-this-system)). Recorded here because the
proposal is intuitive and will return.

**Impact.** One mirroring rule, one notice to the sender, one extended completeness report. No new
permission, no resolver branch, no new table. **The undesigned module now has a constraint on it
before it is designed**, which is the point of taking this decision early: a messaging design that
ships private delivery to minors with neither restriction nor mirroring would have to be reopened
after the fact, when the storage of message bodies and the retention policy are already fixed.

**See:** [MSG-1, closed](../open-questions.md#msg-1--closed--a-direct-message-to-a-minor-is-mirrored-to-their-guardians),
[permission-catalog](../appendix/permission-catalog.md#10-deferred-namespaces),
[glossary — Mirroring](../glossary.md#communication).

---

## D-083 — There is no medical record: personal data is one class of data

**Status:** decided (from your answer) — **closes E-7, resolves H-0, retires the health module**
**Date:** refinement round 7

**Your answer.** *"I consider everything apart from name, gender and age a 'medical record'. It is
fields in the database, not files. In general, ignore 'court order', guardian has all rights on a
child if it's permissions say so. Medical data is not different in any way."*

**This was asked as a scoping question and it answered itself a size larger.** The question on the
table was how to protect a health module. The answer removes the category: there is no privileged
subset of the person record, because the whole thing is equally the sensitive thing. Name, gender and
age are identity — they are what a person is *called and counted as*; everything else the system
knows is descriptive data of one kind, held in fields, and none of it is a different kind of object
from any other.

**Four things this dissolves, and none of them quietly:**

| What the documents said | What it means now |
|---|---|
| **E-7**: one right level cannot separate the medical record from the profile | **Closed, because the sentence describes something nobody wants.** "Read everything except the diagnoses" was the case the eighteen `dependent.*` codes were built for; the answer is that the case is not real and the exception is not wanted. The guardian's right level applies to the record, whole, and that is the end of it |
| **H-0**: the medical record is cited by five files and defined by none | **Resolved by removing the referent, not by building it.** Nothing was hiding behind the phrase; the phrase was inherited from deleted permission codes |
| *"a `view` guardian already sees them"* — the reason the module was deferred | It was false (there was nothing to see) and it is now moot: a `view` guardian sees the person's data, which is the same sentence with a table behind it |
| *"the medical file, which no event permission reaches"* — 08-events' reassurance | **Corrected, not restated.** No file, no reach. See [D-085](#d-085--the-identity-machinery-stays-structured-the-boundary-is-rules-not-sensitivity) for who reads what instead |

**The court-order case, refused on the merits rather than waved away.** The granular model existed for
one story: a parent with access to everything about their child except the medical file, by order of a
court. That story was the entire justification for a sensitive sub-resource, and it is declined —
**a guardian's rights are what the guardian's permission says, and no data inside the record changes
that.** It is worth recording what was traded, because the story is not absurd: the model now cannot
express an arrangement a court might order. The trade made is that a system which cannot express it
**fails visibly** — a guardian either has the access or does not, in one place, auditable — whereas a
system that can express it has a per-field exception nobody outside a courtroom can configure
correctly, and a list of eighteen codes is a list somebody ticks without reading.

**Where protection actually lives now — three places, two of them machinery and the third a sentence
somebody has to keep true:**

1. **Grants.** Whoever holds `person.view` over that person's scope reads the record. This is why
   [the permission catalog](../appendix/permission-catalog.md) raises `person.view` rather than
   inventing a code: a permission that reads everything about a child is not a ⚠, it is in the top
   tier.
2. **The guardian right level** ([D-074](#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular)),
   applied to the whole record.
3. **The guard on the audit trail** ([00-conventions §8 item
   7](../data-model/00-conventions.md#8-personal-data-and-erasure)) — the trail quotes the whole
   record, so the permission that opens it is graded accordingly. Erasure reaching it is unchanged and
   absolute.

**The one thing that must not survive the round: protection keyed by field name.** The redactor used
to scrub a *list of sensitive keys* out of logged row images. That list was coherent when there was a
sensitive subset; with one class of data it is a list of exceptions to a rule that has no exceptions,
and it fails on the first value stored under a column named `note` — or under a code named `allergy`,
which is worse, because the attribute layer generates such names faster than anybody can list them.

**What replaces it, after one reversal inside this same round.** The first answer written down here was
that the audit payload therefore carries no descriptive values at all: who changed which code, for
whom, when, and that a value existed. **That rule is withdrawn, and it was withdrawn by this decision's
own logic.** Stripping attribute values from the trail while a change of address is logged with its old
and new values is a sensitive *subset* of the person record re-enacted in the logging rules — the
privileged corner arriving as a list of table names after it was refused as a list of permission names —
and it empties the history that [D-085](#d-085--the-identity-machinery-stays-structured-the-boundary-is-rules-not-sensitivity)
chose overwrite-in-place in order to have. **So the trail holds the values, and what rises instead is
the guard: an audit entry about a person is as sensitive as the person data it quotes, which puts
`audit.view` in the catalog's top tier next to `person.view`.** That is a line in a document rather than
a mechanism, and it is the weakest link in this design on purpose, so that a reader can see where the
protection actually sits
([09-attributes.md §6](../data-model/09-attributes.md#6-erasure-retirement-and-the-audit-payload)
argues it through, [06-audit-and-import.md §2.2](../data-model/06-audit-and-import.md#22-redaction-before-logging)
keeps the withdrawn rule visible). Erasure reaching the payload is unaffected and remains absolute.

**What is genuinely lost.** The ability to say *"everything except the diagnoses"* — to a court, to a
doctor, to a future board that wants a narrower access tier. It is lost deliberately. If the case ever
arrives in reality the way E-7 hoped it would not, the fix is a **second grant scope over a defined set
of data**, taken as a decision with these documents in front of the reader, and **not** the return of
a code list: one scope, argued once, rather than eighteen flags that encode the same distinction in
the names of permissions nobody reads.

**See:** [D-084](#d-084--descriptive-data-is-organization-defined-at-runtime),
[D-085](#d-085--the-identity-machinery-stays-structured-the-boundary-is-rules-not-sensitivity),
[data-model/09-attributes.md](../data-model/09-attributes.md),
[domain/08-person-data.md](../domain/08-person-data.md).

---

## D-084 — Descriptive data is organization-defined at runtime

**Status:** decided (from your answer)
**Date:** refinement round 7
**Follows:** [D-083](#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)

**Your answer.** Asked whether the field vocabulary is a fixed typed set, a hybrid, or entirely
organization-defined, you chose **entirely organization-defined**; on typing, **typed for rendering,
not for law**; on curation, **values anywhere, codes by permission**; on retirement, **a retired code
keeps its values, redaction erases**.

**Decision.** Two tables. **`attribute_definition`** is the vocabulary the organization maintains:
a code, a label, a value type, whether several values may be open at once, and a status of live or
retired. **`person_attribute`** is a value one person has: the definition it belongs to, the value,
who recorded it and when. Nothing in the schema names a fact about a scout.

**Why this is the shape and not the safer-looking one.** The alternative — a column per fact — makes
every collection habit a release. This organization's list of things it wants to know changes with the
program: shoe sizes for a camp season, an insurance number for one country's requirement, a
preferred contact language for one intake. A schema where that needs a migration produces the real
failure instead of the apparent one: the field does not get added, and the information is collected on
paper, photographed, and lost. **[D-083](#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)
removed the argument for a fixed set** — a closed typed set is justified by needing to *constrain* the
important fields, and the answer was that no field is more important than another.

**Typing for rendering, not for law.** A definition declares text, number, date, yes/no, one-of-a-list,
or free text with a unit. The system uses it to draw the right input, to sort a list, and to warn —
*"that is not a date"* — and it does not use it to refuse a save a human insists on. The reason the
warning must not be a wall is that the value is not the system's to overrule: `2019` as a year for
`last_checkup` is a truer record than an empty field behind a validation error, and the person typing
it knows and the form does not. **What this costs is stated plainly in
[09-attributes §5](../data-model/09-attributes.md#5-what-this-design-cannot-do)**: no database type
checking, no constraint can reference a value, and no report may assume it understands a code.

**Curation, because a vocabulary is the design.** Anyone who may edit a person may record a value
against an existing code. Creating a code needs **`attribute.define`**, which is a small permission
held by few people. An improvised need at 23:00 is recorded as a **proposal**: the value is written
into an uncatalogued code that is visible, unusable-by-default, and waiting for whoever curates the
vocabulary to accept, rename, or merge it. The reason is the one failure this design is exposed to
more than any other: an open vocabulary left open becomes `allergy`, `Allergy`, `alergie` and
`allergies (2)`, after which the layer still stores everything and answers nothing — which is the
entirety of what the attribute table was built to do.

**Two rules that keep a runtime vocabulary from decaying immediately:**

- **Codes are normalized before comparison** — trimmed, case-folded, whitespace-collapsed — and
  uniqueness is checked against the normalized form. This is not a nicety; it is the difference
  between four spellings surviving a week and four spellings surviving a decade, and it is a rule the
  database *can* still enforce.
- **Retiring a code never deletes values.** A retired code disappears from data entry and remains
  readable, reportable, and revivable. Deleting the label must not delete the fact underneath it —
  a code discovered to have been badly named is an administrative event, and if it destroys nine years
  of records it will never be retired, and the vocabulary accretes instead of being curated.
  **Redaction is the opposite case and the only eraser:** when a person is anonymised
  ([00-conventions §8](../data-model/00-conventions.md#8-personal-data-and-erasure)), their values go.

**See:** [data-model/09-attributes.md](../data-model/09-attributes.md),
[D-085](#d-085--the-identity-machinery-stays-structured-the-boundary-is-rules-not-sensitivity),
[open question F-10](../open-questions.md#f-10--which-invariants-the-orm-cannot-express-and-who-writes-those)
for which of its rules the attribute layer can and cannot express.

---

## D-085 — The identity machinery stays structured; the boundary is rules, not sensitivity

**Status:** decided (from your answer)
**Date:** refinement round 7
**Follows:** [D-083](#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data), [D-084](#d-084--descriptive-data-is-organization-defined-at-runtime)

**Your answer.** Asked where the attribute layer starts, you chose **keep the identity machinery
structured** — attributes take everything that has no table today, not the tables that exist.

**The boundary, and it is a different boundary than "sensitive versus ordinary".**

| Stays structured | Becomes attributes |
|---|---|
| `person_name` history, `gender`, `birth_date` + `birth_date_precision` | health and medical facts, education, occupations, languages, insurance, measurements, dietary habits, preferences, notes — everything with no table today |
| `person_contact` — purpose, primary flag, validity period | |
| `person_identifier` — per-scheme uniqueness, decided by the scheme ([D-080](#d-080--five-contradictions-the-translation-surfaced-and-how-each-was-resolved) item 1) | |
| `account`, `account_credential` | |

**The test is whether a rule exists that the attribute layer physically cannot hold.** *"Exactly one
primary postal contact among the open rows"*, *"a school id may repeat but a birth number may not"*,
*"this person has one current name"* — each is a constraint over a **known set of columns**, and a
key/value table has no known set. Folding those tables in would not have simplified the model; it
would have moved four working constraints into application code and called it uniformity, which is
[F-10 shape 3](../open-questions.md#f-10--which-invariants-the-orm-cannot-express-and-who-writes-those)
manufactured on purpose. **Descriptive data is open-ended because nobody can enumerate it; identity is
closed because it was enumerated years ago and has not changed.** That is the whole boundary.

**Values are overwritten; `audit_log` is the history.** Chosen over a history table, and worth
noticing as a **departure from the shape guardianship uses**, where
`guardianship_permission` keeps current value plus history. The difference is real and not
inertia: a guardianship row is **authority**, and authority is asked "what was it on that date" as a
routine part of answering whether an action was permitted — while a descriptive value is a description,
and nobody queries the allergy list of 2019 except in an incident, which is exactly the case the audit
trail exists for. **The dependency is stated rather than glossed, and it has two halves.**
[D-081](#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now)
records that audit completeness is now a discipline rather than a guarantee, so choosing the trail as
the only history buys simplicity with the one control the corpus admits is weakest — and the trail here
is not a pointer into the record, it is **the only copy of the values that ever existed**, since the row
itself holds one belief at a time. So the history exists if, and only if: **(a)** every write path
writes its audit row, including the import, the sweep and the hand-fix, and **(b)** the trail is guarded
as the copy of a child's whole record that this makes it
([D-083](#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data) records why the values
are logged rather than stripped, and what that demands of `audit.view`). If a safeguarding question is
ever unanswerable because the trail was not written, or answerable by somebody who should not have been
able to answer it, this is the decision that made that possible, and it should be reversed with those
two sentences in front of the reader.

**Who reads it: whoever the grants already say.** A unit leader holding `person.view` over their own
unit's members reads their descriptive data — no age branch, no special channel, no per-event grant,
consistent with [D-083](#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)'s
"not different in any way". **This changes D-061's status without reversing it:** the per-event answer
form was designed as *the only* route by which an organizer learns a child has a nut allergy, because
nothing else was readable. It is now the fallback for a fact the organization has not recorded, rather
than the ceiling on what an organizer may know — and the discipline in
[08-events §7](../data-model/08-events.md#health-facts-and-the-discipline-this-requires) about what
belongs on a form survives unchanged, because it was always about not re-collecting what the
organization already holds.

**Amends [D-061](#d-061--event-answers-are-read-by-that-events-organizers).** Its decision stands —
answers are read by that event's organizers — but its premise that this is the only route to a health
fact is superseded by this entry.

**See:** [data-model/09-attributes.md](../data-model/09-attributes.md),
[domain/08-person-data.md](../domain/08-person-data.md),
[data-model/01-identity.md](../data-model/01-identity.md).

---

## D-086 — A sensitivity mark grades what a grant exposes, not the table it reads

**Status:** decided — **by the assistant, during round-7 propagation, not from an answer of yours.**
It follows mechanically from [D-083](#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data),
which is why it was taken rather than asked, but it changes two rows of a table you will read, so it is
numbered and flagged rather than folded into prose. Reverse it if you read the marks differently.

**Date:** refinement round 7
**Follows:** [D-083](#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data),
[D-085](#d-085--the-identity-machinery-stays-structured-the-boundary-is-rules-not-sensitivity)

**The problem the round produced.** Two codes were found to be graded against their table's reputation
rather than their payload's contents. `audit.view` sat at ⚠ while
[D-085](#d-085--the-identity-machinery-stays-structured-the-boundary-is-rules-not-sensitivity)
had just made its `old_values`/`new_values` the only surviving copy of a child's descriptive values — a
log read by people who need not hold `person.view`, holding more than `person.view` shows.
`event.answer.view` sat at ⚠ beside a note conceding that the answers under it "can be clinical".

**Decision.** The mark follows the content. **`audit.view`, `event.answer.view` and `person.view` are
all ⚠⚡**, and the legend's top tier was reworded so it names *whose* data a grant exposes instead of
naming a category of fields — "children's personal data, or the same about an adult where the code reads
a whole person record". Wording matters here more than usual: the previous legend read "children's
personal data **or health data**", which is a category D-083 deleted, and a legend that names a category
invites somebody to write the code that separates it.

**What a raise does and does not do.** It changes **no grant, no scope and no channel.** An event's
organizers still read that event's answers with no additional gate
([D-061](#d-061--event-answers-are-read-by-that-events-organizers) stands); an auditor still reads the
trail. A mark is the sentence a reviewer reads before ticking a box, and the reason it was worth two
rows is the seed roles: `auditor` is now honestly described as a ⚠⚡ read over everything the system has
ever believed about a child, which "just the logs" concealed, and `event.answer.view` arriving in a role
handed to thirty volunteers is now visible at a glance.

**Where this is enforced: nowhere.** A sensitivity mark is a line in
[the catalog](../appendix/permission-catalog.md#1-conventions), reviewed by a human, and
the check that a payload's contents match its code's mark does not exist and cannot be written against a
runtime vocabulary — see [AT-4](../open-questions.md#at-4--is-one-permission-enough-to-guard-a-trail-that-holds-person-data),
which asks whether one permission is the right shape for a trail that holds person data at all.

**See:** [appendix/permission-catalog.md §8](../appendix/permission-catalog.md#8-audit-and-system),
[data-model/09-attributes.md §6](../data-model/09-attributes.md#6-erasure-retirement-and-the-audit-payload).
---

## D-087 — Merge chains stay, because reversing a merge is a supported operation

**Status:** decided (from your answer)
**Date:** refinement round 8
**Follows:** [D-004](#d-004--no-automatic-merging-ever),
[D-056](#d-056--the-legacy-import-expects-a-large-corpus-with-legacy-member-numbers)

**Your answer.** Asked whether the system must be able to reverse a merge that a human approved —
framed as the question that decides B-2, since chains make a reversal a replay and flattening makes it
a rebuild — you chose **chains, and an explicit unmerge**.

**Decision.** `person.merged_into_person_id` stays a pointer that is *not* rewritten forward when the
survivor is itself later absorbed. A→B→C remains a chain and `resolve_person()` keeps walking it
([01-identity.md §9](../data-model/01-identity.md#9-views)). Flattening is now **closed off**, not
merely slower.

**What this decision actually changes is the direction of the argument.** These documents have argued
for chains *because* unmerge would otherwise be impossible — an assumption resting on a capability that
nothing had asked for. You have asked for the capability, so the reasoning runs the other way now:
unmerge is a requirement, and chains are its consequence. That matters for how the rule is defended
later, because "flattening is faster" is no longer a trade being weighed against an abstract
tidiness — it is a trade against a feature someone named.

**Two rules a permanent chain needs, and neither existed until this entry.**

1. **A cycle cannot be created, and the place it cannot be created is the merge, not the read.**
   A merge is refused when the person chosen as survivor resolves — by walking the chain — to the
   person being absorbed. That includes the one-hop case already ruled out (nobody merges into
   themselves) and the case that actually happens: absorbing B into A when A has already been absorbed
   into B. Checking at write time is the whole guard; a read-side step limit would merely decide which
   of two wrong answers to return.
2. **Chain length is a signal, not an error.** Resolution has no hop limit — a bound would silently
   return a tombstoned id, which is the failure the function exists to prevent. Instead, a chain longer
   than **three hops** is reported. Four merges in a row on one line of people does not mean the data
   is odd, it means the matcher is producing duplicates faster than a human can settle them, which is a
   statement about the queue and not about the row.
   [01-identity.md §10](../data-model/01-identity.md#10-integrity-checks) stated this as a breach and
   is corrected: with chains decided, *a survivor that has itself been absorbed is normal*, and only the
   length means anything.

**What was already built, and is confirmed rather than changed.** `person_merge` exists and is
append-only with `reversed_at`/`reversed_by`/`reversal_note`, so an unmerge records that a merge was
undone instead of erasing the record of the mistake
([01-identity.md §8](../data-model/01-identity.md#8-identity_hypothesis-and-person_merge)); and the
reversal procedure is written in four steps
([domain/03-identity-and-legacy.md §6](../domain/03-identity-and-legacy.md#6-reversing-a-merge))
— tombstone off, rows created *before* the merge go back, rows created *inside* the merged window are
flagged for a human, and every `access_grant` from that window is flagged rather than guessed.
**That asymmetry is the honest core of this entry: a merge can be undone and the merged period cannot
be.** Whatever those two humans did while they were one row stays one row's history, because the grants
exercised in that window were really exercised by somebody who can no longer be identified from the
record. Two further things follow and are stated where they belong:

- **Reversal needs no new permission.** Unmerging is the same act as merging — an identity correction
  made by a named human — so it is `person.merge`, already held by the identity reviewer. A
  `person.unmerge` code would grade undoing a mistake as safer than making one.
- **The resolve-on-entry rule now has a check under it.** "Every place that accepts a person id from
  outside must call `resolve_person()`" is a rule application code can forget, and D-072 removed the
  database-level ways of catching it; the net is a report for live rows that reference a tombstoned
  person, which is the only form of this failure that is visible afterwards.

**Closes:** [B-2](../open-questions.md#b-2--closed--merge-chains-stay-because-unmerge-is-required).

**See:** [data-model/01-identity.md §9–§10](../data-model/01-identity.md#9-views),
[domain/03-identity-and-legacy.md §6](../domain/03-identity-and-legacy.md#6-reversing-a-merge).

---

## D-088 — The accounting skeleton is permanent; the audit trail is short

**Status:** decided (from your answer). The retention *periods* are a policy you have chosen; whether
they survive a legal review is a different question and stays open, recorded as an assumption with a
name attached rather than as settled law.

**Date:** refinement round 8
**Follows:** [D-083](#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data),
[D-085](#d-085--the-identity-machinery-stays-structured-the-boundary-is-rules-not-sensitivity),
[D-086](#d-086--a-sensitivity-mark-grades-what-a-grant-exposes-not-the-table-it-reads)

**Your answer.** Of the four retention shapes, **the skeleton stays and the trail ages out**:
membership and fee history is the organization's own record and is kept indefinitely; the audit trail
keeps its values for a bounded window and is then reduced to who did what to which row, when.

**Decision — two clocks, and they are deliberately opposite.**

- **`membership`, `fee_obligation`, `payment` and the anonymised `person` row: no clock.** An erasure
  redacts the person and leaves this skeleton standing, which is the shape
  [00-conventions §8](../data-model/00-conventions.md#8-personal-data-and-erasure) already required;
  what is new is that it is now *because it is the organization's history* rather than because nobody
  decided when it ends. `redaction_log.retained_reason` has a real value to hold.
- **`audit_log`: payloads live 24 months, rows live forever.** After the window a row is **reduced** —
  its `old_values`/`new_values` are emptied and everything else survives: actor, on-behalf-of,
  operation, table, record id, changed fields, transaction, session, channel. The trail keeps
  answering *"who changed this, and when, and were they allowed to"* for as long as the system exists,
  and stops answering *"and to what"* after two years. Twelve months is the floor the window may be set
  to; anything shorter stops covering a full year of a child's activities, which is the unit an
  incident is asked in.

**A third operation on the trail, and it is not redaction.** These documents say
[D-072](#d-072--the-documentation-carries-no-sql-the-schema-is-the-orms-job)-era
([06-audit-and-import.md §2.2](../data-model/06-audit-and-import.md#22-redaction-before-logging)) that
redaction runs on the way in and *"never in a cleanup job that might not run"*, and that sentence is
about a secret that must never have existed in the table. **Reduction is the opposite case and must not
be argued from that sentence**: its entire purpose is to happen later than the write, and its failure
mode is that it does not run at all. So it is a scheduled job with a check on it — a row older than the
window still carrying a payload is a finding that alerts — and the two rules coexist without
contradiction because one forbids late *unwriting of a credential* and the other requires late
*unwriting of history*.

**What this buys, at a price, and both halves are recorded.**

- **It answers [D-086](#d-086--a-sensitivity-mark-grades-what-a-grant-exposes-not-the-table-it-reads)
  more cheaply than any guard could.** The exposure that decision accepts is a wrongly-graded
  `audit.view` reading a child's descriptive values. The window does not fix that — it **bounds how
  long it can**, which for a small organization is the realistic control. This is the strongest argument
  AT-4 will receive and it is not an argument for keeping one permission forever; it is an argument for
  keeping the payload short.
- **It puts a horizon under [D-085](#d-085--the-identity-machinery-stays-structured-the-boundary-is-rules-not-sensitivity),
  and that has to be said plainly rather than discovered in an incident.** Overwrite-in-place was chosen
  because the trail is the history. Now the trail's values expire. So *"what did we believe about this
  child's allergy list in 2019"* is unanswerable **twice over**: the values were never kept in the
  business rows, and after 24 months they are nowhere at all. The real cost of D-085 is therefore not
  "no temporal columns", it is *no long history* — three accepted things stacked: values live in one
  overwritten row, the copy of them depends on a write path remembering to log, and the copy ages out.
  **If a case ever needs the long version, the fix is temporal columns on the value — D-085 reversed —
  and not a longer trail**, because stretching the trail stretches the thing D-086 graded and D-083
  refuses to keep separately.

**Erasure is unaffected and still immediate.** A redaction scrubs that person's values from payloads
whatever their age; the window is a ceiling on how long anything can be there, not a waiting period.

**Legal status of the "forever" half.** Indefinite retention of `membership` and fee rows about a named
person is a claim that needs a basis, and this log is not the place that grants it. What the corpus
states now, as an **assumption pending review**: organizational history plus accounting obligations,
against a redacted person row that keeps the skeleton non-identifying — and the review is the same one
B-3 already names, now with a concrete policy to review rather than a blank.

**Also decided from here:** `access_log` takes the same window as `audit_log`'s payloads as a proposed
default (**F-8**, which needs your confirmation, and which is a weaker question because
[05-authorization §9](../data-model/05-authorization.md#9-access_log) keeps the payloads of *reads*
out of that table to begin with).

**Closes:** [B-3](../open-questions.md#b-3--closed--the-accounting-skeleton-is-permanent-the-audit-trail-is-short).

**See:** [data-model/06-audit-and-import.md §2.2, §4, §6](../data-model/06-audit-and-import.md),
[data-model/00-conventions.md §8](../data-model/00-conventions.md#8-personal-data-and-erasure),
[data-model/09-attributes.md §6](../data-model/09-attributes.md#6-erasure-retirement-and-the-audit-payload).

---

## D-089 — One live account; a colliding sign-up files a claim and creates nothing

**Status:** decided (from your answer)
**Date:** refinement round 8
**Follows:** [D-004](#d-004--no-automatic-merging-ever),
[D-056](#d-056--the-legacy-import-expects-a-large-corpus-with-legacy-member-numbers)

**Your answer.** Asked what happens when a person who already has an account signs up again with a
different e-mail: **refuse, and queue a claim** — not an automatic link, and not a second account.

**Decision, stated as the gate that enforces it.** One live account per person stands
([01-identity.md §4](../data-model/01-identity.md#4-account)) and is joined by a second rule: **an
account may not reach `active` while an unresolved `identity_hypothesis` names its person.** That is the
whole mechanism — there is no new table and no new queue, because the identity review queue already
exists, already records its signals, and already has the reviewer role for it. A sign-up that
strong-matches an existing person runs into that gate on its way to being usable, the person who typed
it sees a holding message, and a human decides.

**The trigger is a strong match only, and the threshold is the load-bearing part.** A hypothesis is
raised at sign-up on an exact legacy member number, or an exact birth date together with a normalized
name match — the same signal set [domain/03 §4](../domain/03-identity-and-legacy.md#4-match-signals)
already weights, at the top of its band. **The soft band must not raise one.** Blocking a stranger's
registration on a fuzzy score is the failure this rule would most deserve, and the cost of letting a
true duplicate through is bounded, reviewable and nightly-matched anyway; the cost of stopping a new
member is a child who cannot sign up to a camp on the day the form closes.

**Two costs, both accepted in the open.**

- **A brand-new person who happens to match waits for a human.** So the blocking condition gets an age
  check shaped like `field_conflict`'s thirty days, and it alerts rather than logs, because a stalled
  identity queue is no longer a data-quality problem — it is a specific person who cannot log in and
  has no way to say so except to telephone someone.
- **The refusal must not confirm that an account exists.** The holding message says the request was
  received and will be checked. It says nothing about whether the name, the birth date or the number
  matched anything, because a sign-up form that answers "yes, that person exists" is an existence
  oracle over the roster, and this system's roster is children
  ([05-authorization.md](../data-model/05-authorization.md)).

**What the answer refuses, and why those were the alternatives.** *Link automatically once the e-mail
is verified and the signals are strong* would have been the convenient one and is
[D-004](#d-004--no-automatic-merging-ever) under another name: a false-positive merge is a privacy
incident in which one human's medical data becomes another human's record, and the merge is the hard
part to undo even with [D-087](#d-087--merge-chains-stay-because-reversing-a-merge-is-a-supported-operation)'s
reversal. *Allow two live accounts* drops the uniqueness rule and splits a person's consents, payments
and attributes across two ids until somebody notices — and the records that must be complete are
exactly the ones where nobody notices.

**The everyday case is not the collision case, and it is worth naming so this rule is not oversold.**
"I have a new e-mail address" is not a second account and was never one: `account_credential` holds
many credentials for one account, so a new address is an *addition* to the login a person already has.
The collision case is narrower than "signing up twice" — it is a person arriving through a door the
system did not know they had.

**No new permission.** Resolving a claim is confirming or rejecting a hypothesis, which is `person.merge`
and already sits with `identity_reviewer`. Note the seed role still has no read over the *person record*
(`person.view` is not in it), so a reviewer decides identity questions from signals and names. That is
defensible — the signals *are* the decision — but [D-089](#d-089--one-live-account-a-colliding-sign-up-files-a-claim-and-creates-nothing)'s
gate means a reviewer's answer now decides whether a child can log in, which is more than tidying a
queue, and it is registered as
[F-11](../open-questions.md#f-11--does-the-identity-reviewer-need-to-read-the-person-record-to-settle-a-claim)
rather than settled here.

**Closes:** [B-4](../open-questions.md#b-4--closed--one-live-account-a-colliding-sign-up-files-a-claim).

**See:** [data-model/01-identity.md §4–§5, §8](../data-model/01-identity.md#4-account),
[domain/03-identity-and-legacy.md §4](../domain/03-identity-and-legacy.md#4-match-signals).

---

## D-090 — The legacy corpus is thousands of roster rows with numbers and no money

**Status:** decided (from your answer)
**Date:** refinement round 8
**Follows:** [D-056](#d-056--the-legacy-import-expects-a-large-corpus-with-legacy-member-numbers),
[D-041](#d-041--belonging-to-a-sub-unit-is-a-participation-record-not-a-membership),
[D-084](#d-084--descriptive-data-is-organization-defined-at-runtime)

**Your answer.** Thousands of roster rows, **one export**, 1990s to now, carrying a legacy member
number, **no payment data**, and free-text columns alongside.

**The consequence that does most of the work: the corpus decides the question the import was going to
default.** [06-audit-and-import.md §6](../data-model/06-audit-and-import.md#6-open-issues) had kept
open whether a historical roster should create a `membership` or only a `unit_participation`, with
"participation unless there is payment evidence" as the safe default. **There is no payment evidence in
the corpus at all**, so the default's exception has an empty set: every imported historical row is a
participation, and `membership` rows come only from the current register. A conditional rule with one
arm is not a safe default, it is the rule, and saying so retires the question rather than answering it.
The stakes were already named in D-041 and
[D-039](#d-039--member-permissions-require-a-current-paid-membership): an inferred open-ended membership
would make every 2003 roster a *current member* with authority today.

**The vocabulary arrives all at once, which changes how the mapping has to be reviewed.** Under
[D-084](#d-084--descriptive-data-is-organization-defined-at-runtime) every legacy column that is not
identity machinery becomes an attribute code, so the first import is the single largest event in the
life of that vocabulary — hundreds of codes from one file. Two things follow:

- **The map is reviewed before the batch applies, not after.** That is precisely why the mapping is
  recorded on the batch as one object
  ([06-audit-and-import.md §3](../data-model/06-audit-and-import.md#3-import-pipeline)) rather than per
  staged row: it is one artefact a person reads once, top to bottom. The codes it names arrive **`live`**,
  because a curator has just read them.
- **`proposed` keeps its meaning.** It stays the status for what a *human at a desk* improvises later —
  a fact with no code yet — and not for "whatever the import did not understand". If several hundred
  codes arrive `proposed` on day one, the curation queue
  ([09-attributes.md §8](../data-model/09-attributes.md#8-integrity-checks) check 1) opens full, its age
  signal is meaningless, and the first lesson the organization learns about the attribute layer is that
  its warning queue is noise. **This is a partial answer to AT-2, which stays open** for the runtime
  case: who holds `attribute.define` day to day, and how long a proposal may sit.

**What is confirmed rather than decided.** The legacy number goes to `person_identifier` with
`scheme = 'legacy'`, imported verbatim and never reissued; where it is present the match is exact and
the heuristics are for backfilling it, not for deciding identity (D-056). At thousands of rows the
review is a work queue with a trustworthy set at the top of it, which
[B-1](../open-questions.md#b-1--closed--thousands-of-roster-rows-numbers-present-no-payment-data) already
called a strengthening of D-004 rather than a relaxation.

**What this makes sharper rather than smaller.** With attendance and no money,
[06-audit §3.1](../data-model/06-audit-and-import.md#31-what-a-source-row-actually-evidences) is the
load-bearing section of the whole import — a roster row evidences *presence in a unit*, and everything
beyond that is inference. Which leaves **A-4**, the organizational year boundary, as the sharpest
remaining import question, because it is what an end date gets inferred from.

**Still not known, and it is operational.** The exact record count and the year range. Both are inputs a
batch carries; neither changes a table. B-1 is closed on the design and these two numbers are recorded
as the import's own inputs.

**Closes:** [B-1](../open-questions.md#b-1--closed--thousands-of-roster-rows-numbers-present-no-payment-data).

**See:** [domain/03-identity-and-legacy.md §7](../domain/03-identity-and-legacy.md#7-legacy-import-pipeline),
[data-model/06-audit-and-import.md §3](../data-model/06-audit-and-import.md#3-import-pipeline),
[data-model/09-attributes.md §7](../data-model/09-attributes.md#7-the-legacy-import-which-is-where-the-vocabulary-comes-from).

**Amended one round later, in part.** The corpus this entry describes was the wrong shape in its
second half: the rows are people with their membership periods, and events with attendance, and they
name no units at all. Read [D-092](#d-092--the-corpus-is-people-and-events-and-it-names-no-units) and
[D-093](#d-093--the-one-off-import-may-create-memberships-both-ends-dated), which retire this entry's
absolute ban on an imported `membership`. **What survives intact is the other half** — the legacy
member number, the absence of money, and the reviewed-before-apply field map that decides where the
whole attribute vocabulary comes from. Three entries describe one import and none is complete alone.

---

## D-091 — A permission group is a rule and a list at once, and a rule may name another group

**Status:** decided (from your answer)
**Date:** refinement round 9

**Amended twice, by [D-101](#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree) and [D-103](#d-103--an-audience-may-name-another-audience), and the arm this entry is named for is the one that
changed.** A rule may still name another set — as `GROUP(x)` or `AUDIENCE(x)` inside an expression — but
`audience_include` is deleted, the list arm is the `LIST` leaf, and 'other groups' became an operand kind
rather than a table. The write-time acyclicity requirement survives, widened into reachability across
audiences.

**Follows:** [D-042](#d-042--grants-may-target-audiences-not-only-individuals),
[D-033](#d-033--multiple-people-may-occupy-the-same-position),
[D-087](#d-087--merge-chains-stay-because-reversing-a-merge-is-a-supported-operation)

**Your answer.** Asked whether appointing someone to a position should also create a role assignment,
the answer described something one level further out: *within the permission groups there should be
"filling rules" for each, which specify who will be placed in that group on top of manually added
people — "everyone with membership", "a leader role", "anyone", "members of permission group ABC"*.
The examples given were from another system, where a group's population is derived from enrolment in
a course: `studpredmet 1433 kod PV160` puts the students and teachers of one course in a group.

**What was already here, because the answer describes most of an existing mechanism.** The
organization already has rule-filled groups: an `audience` is a named set that a permission is granted
to, whose membership a rule decides at check time (D-042). Three of the four rules named exist
verbatim — `everyone` is "anyone", `all_members` is "everyone with membership", and `unit_leaders` is
"a leader role", derived live from position assignments marked `is_leadership`. Named groups are the
manually-added arm. **What the answer added, and what this decision is about, are the two things the
model refused.**

**Decision, in three parts.**

1. **`audience.kind` is gone.** A group has an **optional rule arm** (`resolver_key` plus
   `scope_parameter`), an **optional manual arm** (`audience_member` rows) and an **optional inclusion
   arm** (`audience_include` rows naming other groups). Its membership on a date is the **union of all
   three**. The old rule — a group is a rule *xor* a list, and a member row on a rule "would look
   authoritative" — is withdrawn. It forced two grants for the common case of *"the kitchen crew, plus
   whoever leads this pack"*, and two rows in two places is how one of them gets forgotten.
2. **A group may include another group.** This was refused outright — *"They do not nest. An audience
   cannot contain another audience — that is how you get evaluation cycles and answers nobody can
   predict."* The refusal is withdrawn and its reason answered where D-087 answered the same reason for
   merge chains: **the cycle is refused when the edge is saved, not in the read path.** Inclusion edges
   are stored rows, so the cycle is decidable at write time by walking them, and nothing about
   evaluation gets a hop limit or a guess. Inclusion chains get a length bound, stored as a parameter in
   the way the renewal window is ([D-048](#d-048--the-renewal-window-is-60-days-and-is-a-configuration-parameter)
   is the precedent for that shape of parameter), and an unresolvable chain **denies**: a group that
   cannot be evaluated reaches nobody, which is the direction this model fails in everywhere else.
3. **An appointment still creates no role assignment.** `position.is_leadership` keeps the one job it
   has always had — driving the derived `unit_leaders` rule, and marking which roles exist to make a
   position work. Copying a role assignment at appointment time would duplicate a derivation, and a
   copy is the thing that outlives its reason: it has to be found and revoked when the position ends,
   whereas the rule stops covering the person on the day the assignment closes. **That is the answer to
   the question that was asked, and it is the cheapest part of it** — no schema, no workflow.

**What was *not* taken from the answer, and it needs saying rather than burying.** In the system you
described, permissions sit on the group. Here, permissions sit on a group at one scope through
`access_grant` — which is how "all leaders of pack X may take part in its roster" is one row today — but
a **role** is still held by one named person, because `role_assignment` is the record of who holds which
office and it is read to answer "who was treasurer in 2023". A derived holder list cannot answer that,
and an office record that cannot answer it is not an office record. So a rule-filled role is **not**
decided here: it is registered as
[F-12](../open-questions.md#f-12--closed--may-a-role-be-held-by-a-rule-as-an-audience-is) — the change is one
grantee pair on `role_assignment`, exactly the shape D-042 already put on `access_grant`, and it wants
an answer about the historical question before it wants an implementation.

**The cost, stated where it will be felt.** Membership of a rule group has never been stored — D-042
accepted that, and the docs even recommended it, because a rule does not rot the way a list does. This
decision **widens how much of the permission answer is recomputed rather than recorded**: a grant that
once named three people now names a chain of sets whose membership depends on positions, participations
and memberships as they are today. Two consequences follow, and the second is the one to keep in view:

- **A grant's reach stops being visible in the row.** The editor must show the resolved set — who this
  grant actually reaches, expanded — and not the group's name. Composition makes a three-deep inclusion
  a silent widening, and `everyone` is a legal member of the graph: nothing in part 2 stops a group from
  including one that includes the whole world, which is already grantable directly and is now grantable
  by three edits and a save.
- **"Who could read this in 2023?" now has one fewer answer.** The audit trail used to hold the change
  that made it true, and [D-088](#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)
  empties those payloads after 24 months; the derived membership was never stored at all. So after two
  years the question is answered by re-running rules against state that has itself moved on. **The route
  back is [F-7](../open-questions.md#f-7--cache-vs-materialized-effective_permission-table)** — a
  materialized effective-permission snapshot, kept as history rather than as a cache — which until now
  looked like a performance question and is now also the only thing that could make this answerable.

**Naming, since your word and this file's word differ.** What you called a *permission group* is the
`audience` table, and the table keeps the name — not to avoid work, but because `group` is already taken
inside it for one of the two kinds this decision deletes, and a document that renames a table and keeps
the word for a fragment of it is worse than one that renames neither. The glossary carries both words.
What does change is that **`group` no longer names a kind of anything**: there is one thing, and it has
arms.

**Closes:** [C-4](../open-questions.md#c-4--closed--a-group-is-filled-by-a-rule-and-a-list-and-appointing-creates-nothing).

**See:** [data-model/05-authorization.md §8](../data-model/05-authorization.md#8-audience--grants-that-target-a-set-of-people),
[domain/06-authorization-model.md](../domain/06-authorization-model.md#21-the-founding-rule-and-what-is-left-of-it),
[domain/04-organization-structure.md §4](../domain/04-organization-structure.md#6-appointments-which-no-longer-end-at-a-position).

---

## D-092 — The corpus is people and events, and it names no units

**Status:** decided (from your answer)
**Date:** refinement round 9
**Follows:** [D-090](#d-090--the-legacy-corpus-is-thousands-of-roster-rows-with-numbers-and-no-money),
[D-041](#d-041--belonging-to-a-sub-unit-is-a-participation-record-not-a-membership),
[D-058](#d-058--an-event-is-a-dated-occasion-owned-by-exactly-one-unit)

**Your answer.** Asked what creates the units the roster rows point at: *the rows are mainly "person
with names, birthdate and when they were members of the root unit", "events with attendance". Not much
more — do not solve assignment to org units.*

**So the corpus has two halves and neither is a roster.** D-090 recorded it as *roster rows*: people
attending units. That word was wrong in its second half, and the whole import design hung off it,
because a roster is evidence of *presence in a unit* and that is what
[06-audit-and-import.md §3.1](../data-model/06-audit-and-import.md#31-what-a-source-row-actually-evidences)
was written to police. What is actually arriving is a **membership export** and an **attendance
export**. Each is evidence of a different thing, and neither is evidence of a sub-unit:

| Half | What a row says | What the import writes |
|---|---|---|
| **People** | name, birth date, **member of the organization for a period** | a `person`, and a bounded `membership` ([D-093](#d-093--the-one-off-import-may-create-memberships-both-ends-dated)), which brings its root participation row with it |
| **Events** | an event, and who attended it | an `event` owned by the root ([D-094](#d-094--the-root-unit-owns-every-imported-event)) and an `event_registration` per attendee |

**Unit assignment is out of scope, by instruction, and that is a decision with a consequence rather
than an omission.** `parsed_unit_code` and `parsed_unit_name` stay in the parser — an export that
surprises whoever runs it with a unit column is exactly what those fields and the `unit_not_found`
warning are for, and they cost nothing to keep. But nothing resolves them, no `org_unit` is created by
any batch, and no sub-unit `unit_participation` row is ever imported. **The consequence, plainly: the
system's historical record has no sub-units in it.** "Who was in pack X in 2011?" has no answer on day
one and will have one only from live data forward, and the first answer anyone reads is a roster
somebody typed in. That is not a gap in the model — the model has always been able to hold it — it is
what the source can say, and it is written here so that the first person to ask the question finds the
sentence rather than the absence.

**What this retires, and what it leaves alone.** Retired: the roster frame, and with it D-090's rule
that an imported row is a participation and never a membership
([D-093](#d-093--the-one-off-import-may-create-memberships-both-ends-dated) replaces it), and the
import exclusion that rule forced into integrity check 1 in
[03-membership.md §7](../data-model/03-membership.md#7-integrity-checks) — with no imported
participations, that exclusion goes and the check starts finding what it was written to find. Left
alone, because none of it depended on units: the legacy member number going to `person_identifier` and
the exact-match identity story (D-056), the absence of money, the attribute vocabulary arriving wholesale
from the free-text columns through a map read before the batch applies, the end-date inference, and the
revert mechanics.

**The one thing the answer makes harder rather than clearer.** Two halves means two shapes of batch, and
the pipeline has one `import_batch` with one `field_mapping` on it. An events export has nothing to map
to an attribute code and a people export has nothing to map to a registration, so **either the batch
types itself** (a people batch, an events batch, each with the mapping and the checks that fit) **or one
batch carries two mappers that can never both apply.** The first is the smaller change and it is what
these documents now assume; it is recorded as a design consequence here rather than as a new question,
because the answer that decided the shape also decided this about it.

**Closes:** [C-5](../open-questions.md#c-5--closed--the-corpus-names-no-units-and-none-are-assigned).

**See:** [domain/03-identity-and-legacy.md §7](../domain/03-identity-and-legacy.md#7-legacy-import-pipeline),
[data-model/06-audit-and-import.md §3](../data-model/06-audit-and-import.md#3-import-pipeline).

---

## D-093 — The one-off import may create memberships, both ends dated

**Status:** decided (from your answer)
**Date:** refinement round 9
**Follows:** [D-090](#d-090--the-legacy-corpus-is-thousands-of-roster-rows-with-numbers-and-no-money),
[D-092](#d-092--the-corpus-is-people-and-events-and-it-names-no-units),
[D-050](#d-050--a-renewal-inside-the-window-extends-the-existing-root-participation-row),
[D-039](#d-039--member-permissions-require-a-current-paid-membership)

**Your answer.** *The import will be a one-off — allow creation of memberships.*

**Decision.** A batch may create `membership` rows, with `valid_from` **and** `valid_to` set, from a
source that states a period of membership. One row per period the source states — not one row per
calendar year — with `data_confidence = 'low'` and the batch id on it, and the
`renewed_from_membership_id` chain left to whoever reconstructs it, because an export of consecutive
years is a period, not a renewal history. **D-090's ban is narrowed to the thing it was actually
protecting, in one sentence that survives unchanged: never an open-ended membership, and never one
inferred from an attendance row.** The reason is D-039 and it has not moved — a membership with no
`valid_to` satisfies `is_current_member()`, so an inferred 1998 membership hands whoever signs up under
that name authority in the present. That is why the ban was absolute and it is why *this* half of it can
go: a closed period cannot gate anything.

**"One-off" is doing real work in the answer, and it is worth naming what it buys.** The argument for
the original ban was about a standing hazard — an import that infers, run by whoever is holding the
file, repeatedly, for years. What is being decided here is one reviewed batch whose mapping is read
before it applies, on a corpus that will never arrive twice. A rule written for a recurring process is
too strict for a one-time one, and the safety that mattered is not the ban but the review.

**Four consequences, in the order they arrive.**

- **The root participation obligation now points at the import again.**
  [03-membership.md §5.1](../data-model/03-membership.md#5-unit_participation--deleted-by-d-097) had
  just been corrected to say that an ordinary import "touches neither arm of this pair". With
  memberships arriving by the thousand it does: every imported membership owes its root-unit
  participation row in the same transaction, which is what keeps *who is in unit X* one query
  (D-041). Consecutive imported years for one person therefore stretch one root row rather than opening
  a second, and a gap in the source is a lapse that produces two — the same rule as a renewal, and the
  same accepted cost: the lapse stops being visible in the participation table.
- **No obligation, no payment, no balance.** An imported membership creates **no `fee_obligation`**.
  The corpus has no money in it (D-090), so an obligation per historical year would arrive as `unpaid`
  and turn a decade of members into a wall of debt on a ledger that has never heard of them, with a
  `due_date` in 1999 for the lapse sweep to choke on. The sweep is already safe — it acts on active
  memberships with a positive-balance obligation, and an imported row is neither — but the *absence*
  becomes a rule, because the alternative failure is silent and enormous.
- **`outstanding_balance` is NULL on these rows, and that is now load-bearing rather than incidental**
  ([07-finance.md](../data-model/07-finance.md#2-minimal-provisional-shape)). A zero would be a claim —
  *settled* — that the export does not support.
- **These rows are the oldest layer of the skeleton D-088 keeps forever.** That decision held named
  membership periods indefinitely on legitimate interest, on an unverified legal basis
  ([assumption 49](../open-questions.md#i-assumption-index)). From this round the indefinite-retention
  half of D-088 covers thousands of named people with birth dates who were never asked and never used
  the system. It is the same judgement, applied to a much larger population, and the review commissioning
  it is unchanged in kind and much changed in scale.

**What this makes true about reports.** Every cross-decade member count is now a mix of an export and a
register, distinguished only by `data_confidence` and `import_batch_id`. A membership-rate chart that
spans the import boundary is comparing a source that states membership with a system that records it,
and nothing in the query knows the difference.

**Closes:** [C-5](../open-questions.md#c-5--closed--the-corpus-names-no-units-and-none-are-assigned)
(together with [D-092](#d-092--the-corpus-is-people-and-events-and-it-names-no-units)).

**See:** [data-model/06-audit-and-import.md §3.1](../data-model/06-audit-and-import.md#31-what-a-source-row-actually-evidences),
[data-model/03-membership.md §5.1](../data-model/03-membership.md#5-unit_participation--deleted-by-d-097),
[domain/03-identity-and-legacy.md §7](../domain/03-identity-and-legacy.md#7-legacy-import-pipeline).

---

## D-094 — The root unit owns every imported event

**Status:** decided (from your answer)
**Date:** refinement round 9

**Deleted rather than reversed by [D-102](#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it): there is no owner column for an imported event to
have.** The import still owes one `event` row per event in the corpus, and now owes the per-event grant
instantiation D-102 added with it.

**Follows:** [D-058](#d-058--an-event-is-a-dated-occasion-owned-by-exactly-one-unit),
[D-092](#d-092--the-corpus-is-people-and-events-and-it-names-no-units),
[D-067](#d-067--presence-is-a-three-valued-fact-on-the-registration)

**Your answer.** Asked what owns an imported event, given that every event belongs to exactly one unit
(D-058) and that unit assignment is out of scope: **the root unit owns them all.**

**Decision.** `event.org_unit_id` on an imported event is the single root unit, as a rule rather than a
judgement. D-058's "exactly one owning unit" is satisfied without inventing a unit, without a per-event
decision, and without the import touching the unit vocabulary at all — which is what makes this
compatible with the instruction that decided D-092. The root is the only unit the corpus speaks of, so
it is also the honest answer, not merely the convenient one.

**Attendance becomes registrations, and the three-valued rule decides what is *not* written.** An
attendance export lists the people who came. Each one becomes an `event_registration` with `attending`
and `was_present = true` (D-067). **Nobody else gets a row**: a person who might have come and did not is
not in the export, and inventing `not_attending` rows from silence would put words in a source that said
nothing ([D-059](#d-059--unanswered-is-the-absence-of-a-row-a-registration-stores-two-values)). So
imported events have a population exactly as large as the evidence for them, and the historical
attendance figures these documents will be asked for are *arrived*, not *registered*.

**Three costs, one of which is the reason this decision was worth recording separately.**

- **The root's event list becomes mostly history.** "What's on" stops being a unit filter and has to be a
  date filter — and the unit-scoped report that asks "our events this term" shows an imported camp
  because the root is its owner, which is the same class of misreading D-049 recorded for
  `unit_participation.view` at organization scope.
- **Imported events have no organizers**, so nobody holds them at unit scope: `event_organizer` is empty
  on them by construction, and editing one takes organization-scope authority
  ([D-062](#d-062--organizers-are-appointed-on-the-event-not-granted)). An imported event is therefore
  read-only for the people who would ordinarily run an event, which is correct and will still surprise
  somebody.
- **Correcting an owner is one column, and it moves the audience.** Unlike participation history, which
  is never rewritten, `event.org_unit_id` is editable — and because an event is an artifact of its unit
  ([D-063](#d-063--an-event-is-an-artifact-of-its-unit-not-a-child-of-it)), moving an event from the root
  to a pack silently changes who can read it. So corrections are allowed and expected, and each is an
  audited write with a reason; and the audit record of *who moved it* is readable for 24 months
  ([D-088](#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)) while the event itself
  is kept indefinitely.

**Closes:** [C-5](../open-questions.md#c-5--closed--the-corpus-names-no-units-and-none-are-assigned)
(together with [D-092](#d-092--the-corpus-is-people-and-events-and-it-names-no-units)).

**See:** [data-model/08-events.md §2–§4](../data-model/08-events.md#2-event),
[data-model/06-audit-and-import.md §3](../data-model/06-audit-and-import.md#3-import-pipeline).

---

## D-095 — Units carry no restrictions; joining one is somebody else's act

**Status:** decided (from your answer)
**Date:** refinement round 9
**Follows:** [D-038](#d-038--membership-is-ageless),
[D-043](#d-043--no-background-checks-are-recorded-in-this-system),
[D-081](#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now)

**Your answer.** Asked whether a unit that declares it does not supervise minors should refuse a minor's
*position* as it refuses their participation: *a unit does not have any restrictions — however, persons
can't assign themselves. They will be assigned to the unit by the counselors.* And on the shape of
entry: *into the root unit, there is a fee for entry; into the sub-units, there is no fee, it is entirely
managed by the organization, including adding more members.*

**Decision.** Two entry paths, each with exactly one gate, and no third control:

| | **The root unit** | **A sub-unit** |
|---|---|---|
| **How you get in** | You pay. The membership flow is the only self-service entry in the system, and it opens the membership and its root participation row (D-041, D-050) | Somebody else writes the row |
| **What stops you** | The fee | `unit_participation.manage` at that unit — held by the people who run it, **with no self-scoped variant, and none will be added** |
| **Money** | The yearly fee | Nothing. There is no fee for taking part in a pack, and no model wants one |

The same holds for `position_assignment`: nobody appoints themselves. There is no code in the catalog
that could express either, and D-095's instruction is not to add one.

**`org_unit_type.allows_minors` is removed.** It was introduced as a **safeguarding** flag — the thing
that let the system refuse to place a minor in a unit that does not supervise them without hardcoding
which type codes those are. After this answer it enforces nothing about positions, and a flag that is
documented as a safeguard and enforced on one of two write paths is precisely the thing these documents
elsewhere refuse to keep: *a list of eighteen ticks nobody read is not a safeguard, it is a receipt*
([domain/08 §4](../domain/08-person-data.md#4-what-was-refused-and-what-it-cost)). What goes with the
column: its check in [03-membership.md §7](../data-model/03-membership.md#7-integrity-checks) (check 2,
*participants in units that do not allow minors*), the root type's `allows_minors = false` in the seed,
and the sentence in [02-organization.md §1](../data-model/02-organization.md#5-what-this-page-held-before-round-10) that
explains why there is no `allows_adults` sibling.

**D-081 requires naming who enforces the rule now, and the honest form of that answer is a shift in
kind.** The rule the flag existed to express — *do not place a child where nobody is responsible for
them* — is now enforced by **who is allowed to write the row**: a person able to add a child to a unit is
a person the unit's leadership trusts with its roster, the write is audited, and the assignment names who
made it. That is a stronger control than a boolean on a type, because a boolean only ever refused a
placement nobody had thought about and the permission refuses every placement by the wrong person
regardless of the child's age.

**What is genuinely lost, and it is the safeguarding story in one paragraph.** **The system no longer
knows which units are for children.** `allows_minors` was the only machine-readable answer to that
question; nothing replaces it, because "entirely managed by the organization" is a statement about people
rather than data. Combined with D-043 — no background checks recorded anywhere — the organization
module's safeguarding story after D-095 is: a permission held by named adults, an audit trail whose
values expire after two years, and a report list of who holds the write. If that turns out to be too
little — after a real incident, or an insurer's question — the route back is **a rule about who may be
placed where, argued once as a decision, with its enforcement layer named** in D-081's terms, and not a
resurrected column whose name implies it enforces something.

**Not changed by this, because it was never about units:** membership stays ageless (D-038), `position.min_age`
stays a real eligibility constraint about the *position* (a scoutmaster must be an adult), and the
guardianship channel is untouched.

**Closes:** [C-6](../open-questions.md#c-6--closed--units-carry-no-restrictions-joining-one-is-somebody-elses-act).

**See:** [domain/04-organization-structure.md §1, §4](../domain/04-organization-structure.md#1-the-organization-is-one-unit-and-the-unit-is-a-scope),
[data-model/02-organization.md §1](../data-model/02-organization.md#5-what-this-page-held-before-round-10),
[domain/05-membership-lifecycle.md](../domain/05-membership-lifecycle.md#1-the-flow-you-described).

---

## D-096 — A reused unit number is a new unit unless someone records the continuity

**Status:** decided (from your answer, and one question back)
**Date:** refinement round 9
**Follows:** [D-036](#d-036--units-cannot-be-reparented-a-unit-that-moves-is-a-new-unit),
[D-054](#d-054--the-sub-unit-vocabulary-is-not-seeded-the-organization-defines-its-own-types),
[D-092](#d-092--the-corpus-is-people-and-events-and-it-names-no-units)

**Question, put back to you, and the answer's shape.** Asked whether a unit number appearing twice —
one unit closed in the 1990s, another carrying the number now — is the same unit or a new one, the
answer was *"what is a unit number?"*. That question is the useful part of this entry, so it is answered
before the decision is. A `code` is **a short human label typed by somebody**: `T12`, `4. oddíl`. It is
not the unit's identity, which is the row; it is not its name, which is a temporal row of its own
(`org_unit_name`); and it is not unique, deliberately — uniqueness is per parent and among live rows
only, which is exactly why a closed unit's number is free again
([02-organization.md §3](../data-model/02-organization.md#5-what-this-page-held-before-round-10)). Once it is described as a label,
the question answers itself in the direction the docs already argued.

**Decision.** **A reused number is a new unit.** One `org_unit` row per unit that existed, each with its
own period; the continuity between two of them is not a property of the label but an assertion somebody
makes and records as an `org_unit_relationship` with `successor_of`
([§5](../data-model/02-organization.md#5-what-this-page-held-before-round-10)). The opposite
default — reuse the row and let a thirty-year gap show inside one unit's life — is what a system drifts
into if nobody says, because it is what "match on code" does. And the two cases the docs separate are
unchanged and are *not* this case: **a renumber is one unit with two name rows** (same participants,
continuity asserted by the rename itself), while **a unit that moves parent is a new unit** (D-036).

**The cost is a decision the organization has to make in words, occasionally, and it is cheap.** When a
number really does come back — a troop refounded after a decade dormant — someone writes down that this
unit is the successor of that one, and "who was in Pack 12 in 1984?" follows the relationship instead of
guessing from an overlapping name. Refusing to default either way was considered, and it is what
`domain/04 §6` used to say (*"record which was chosen and why on the unit"*); what D-096 adds is the
direction the record goes in when nobody records anything, because a default that is unstated is a
default that gets implemented by whoever writes the matching screen.

**Closes:** [C-3](../open-questions.md#c-3--closed--a-reused-unit-number-is-a-new-unit).

**See:** [domain/04-organization-structure.md §3, §6](../domain/04-organization-structure.md#4-a-name-carries-no-identity),
[data-model/02-organization.md §4–§5](../data-model/02-organization.md#5-what-this-page-held-before-round-10).

**Superseded by [D-097](#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row).** There are no
sub-units left to number, close, or declare a successor of, and no `org_unit` row for a `code` to sit on.
The reasoning survives as a method — *a label carries no identity, so continuity is asserted and never
matched* — and it transfers intact to `person_group`, where a group name that comes back after a decade
is a new group unless somebody says otherwise.

---

## D-097 — There are no sub-units. The unit is a scope, not a row

**Status:** decided (from your answer)
**Date:** refinement round 10
**Reverses:** [D-008](#d-008--organizations-units-are-one-self-referencing-table-with-configurable-types),
[D-035](#d-035--one-root-unit-all-sub-units-nest-arbitrarily-beneath-it),
[D-036](#d-036--units-cannot-be-reparented-a-unit-that-moves-is-a-new-unit),
[D-041](#d-041--belonging-to-a-sub-unit-is-a-participation-record-not-a-membership),
[D-049](#d-049--the-root-may-not-read-into-its-sub-units-scope_exposure-is-the-only-crossing),
[D-050](#d-050--a-renewal-inside-the-window-extends-the-existing-root-participation-row),
[D-054](#d-054--the-sub-unit-vocabulary-is-not-seeded-the-organization-defines-its-own-types),
[D-078](#d-078--an-exposure-extends-an-assignment-never-a-direct-grant),
[D-096](#d-096--a-reused-unit-number-is-a-new-unit-unless-someone-records-the-continuity).
Amends [D-031](#d-031--no-downward-inheritance-of-authority-scope_exposure-is-the-only-crossing)
and [D-095](#d-095--units-carry-no-restrictions-joining-one-is-somebody-elses-act), whose subject was
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
| `org_unit_type`, `org_unit_type_rule` | the runtime unit vocabulary, `is_leaf`, `max_depth`, the seven-step nesting check, and the whole of [D-054](#d-054--the-sub-unit-vocabulary-is-not-seeded-the-organization-defines-its-own-types)'s argument about not guessing words |
| `org_unit_name` | rename and renumber history, `change_reason`, and the denormalised `org_unit.name` it fed |
| `org_unit_relationship` | `split_from`, `merged_into`, `successor_of`, `renamed_to` |
| `unit_participation` | sub-unit rosters, the root participation row every membership owed, and the transfers between units |
| `scope_exposure`, `scope.expose` | the only downward crossing, the direction-of-authority check, the `scope.exposure.review` code, and the nightly alert that was its sole detector |
| `unit_ancestors()`, `unit_descendants()` | the recursive walk, the path-consistency check, and the CI assertion that the resolver never calls it |
| `role_assignment.scope_type` / `scope_id` | a role is always held at the unit; there is nothing else to hold it at |
| the resolver's unit tier | the ladder of [D-032](#d-032--deny-is-absolute-locality-orders-allows-only) drops from four tiers to the ones [D-099](#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality) states |

**Why this is affordable now, when it was not affordable in round 1.** Because of
[D-092](#d-092--the-corpus-is-people-and-events-and-it-names-no-units), which your own answer supplied:
**the legacy corpus names no units.** Two exports — people with their membership period at the root, and
events with attendance — and no unit column anywhere. So the hierarchy has no recorded history to lose;
"who was in pack X in 2011" already had no answer at go-live, and was already written down as a
consequence rather than a bug. A structure that describes nothing imported and (per
[D-095](#d-095--units-carry-no-restrictions-joining-one-is-somebody-elses-act)) restricts nothing is a
structure that carries no information, which is the definition of the over-specification you were
pointing at.

**The rule that dies hardest is the founding one.** [D-031](#d-031--no-downward-inheritance-of-authority-scope_exposure-is-the-only-crossing)
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
   permission in the system ([D-083](#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data),
   [D-086](#d-086--a-sensitivity-mark-grades-what-a-grant-exposes-not-the-table-it-reads)). What is left of
   the safeguarding story is the same three things D-095 was left with — a permission held by a named
   adult, an audit trail whose payloads expire after two years
   ([D-088](#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)), and a report of who
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
**Supersedes the subject of:** [D-041](#d-041--belonging-to-a-sub-unit-is-a-participation-record-not-a-membership)

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
[D-005](#d-005--permissions-are-grants-never-derived-from-identity) and
[D-019](#d-019--household-membership-grants-no-access) restated one level down — participation is not
authority, and the fact that the participation is now stored in a tidier table does not quietly promote it.

**Why the word "audience" survives at all, and where the line is.** You named the inversion, and it is
the load-bearing part of this entry: **a group states its members; a selector picks them.**
`person_group` is the domain fact — a thing a user sees, names, opens, and ends. `audience` is the
grantee a grant names, and one of its operands may be a `person_group`
([D-101](#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree)).
Two tables answer "who is in it", which is precisely the shape
[D-080](#d-080--five-contradictions-the-translation-surfaced-and-how-each-was-resolved) teaches to be
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
[D-050](#d-050--a-renewal-inside-the-window-extends-the-existing-root-participation-row)'s renewal
mechanism narrows to exactly what it always claimed to be about: the `membership` row, per
[D-016](#d-016--renewal-opens-a-new-membership-row-not-an-extended-valid_to).

**Joining a group is still somebody else's act, and D-095's reasoning transfers intact.** The gate is
`person_group.member.manage`, held at the unit (which reaches every group, per D-099) or granted on one
group as an item. There is no self-scoped variant and none will be added: nobody writes themselves onto a
roster, which was the whole of D-095 and is unchanged by moving the roster. `membership_request`
**loses `requested_unit_id`** — a request is for membership of the unit, and which group a new member
lands in is a write on the group, not a preference on the request.

**So the history question has an answer, and it is the same answer every dated row in this system
gives.** "Who was in `schuzka2026-1` on 14 March 2026?" is a point-in-time read over
`person_group_member`, exactly as `domain/05`'s query 3 was for a unit, and it survives the audit
trail's 24-month payload expiry ([D-088](#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short))
because it does not depend on the trail. **The group's own `valid_from`/`valid_to` and the member rows'
periods are two different facts** and both are kept: the first says the group existed over that span,
the second says who was in it. An open group with dated members answers the historical question just
fine, which is the whole reason the rows are dated — the naming in your own example (`schuzka2026-1`)
becomes a habit the organization may or may not keep, rather than the mechanism history depends on.

**Dating the rows imports the invariant set that dating always imports**, and naming them here is the
work: where both ends are set, `valid_to` is later than `valid_from`; **no two rows for the same person
and group may overlap**, counted over **all** rows and not only the open ones, half-open so a row ending
on a day and one beginning that same day do not collide (the
[D-002](#d-002--everything-temporal-is-a-period-never-a-boolean) shape, and
[F-10](../open-questions.md#f-10--which-invariants-the-orm-cannot-express-and-who-writes-those) shape 1,
so a hand-written migration emits it and the ORM will not); a person who left in 2020 and came back in
2024 is **two rows**, never one row edited in place, because the edit destroys the answer to "was she in
the group in 2019?"; and moving from one group to another closes one row and opens another —
`03-membership.md §5.2`'s transfer discipline, retargeted at groups and otherwise unchanged.

**The duplication is now real, which is why the two tables are said apart by their rules and not only
by their names.** `person_group_member` and `audience_member` are both dated sets of people, which is
precisely the pair
[D-080](#d-080--five-contradictions-the-translation-surfaced-and-how-each-was-resolved) teaches a reader
to distrust — two statements that can drift, one of which will be the one the screens read. They stay
apart because the *maintenance* differs, and the dated shape makes the difference sharper rather than
softer: a group's members are the organization's record of who attends, kept by the people who run the
group, and it is true when no grant exists; `audience_member` rows are a selector's additions, kept by
whoever composes permissions, and are meaningless outside the selector they complete. **Merging them
would make the permission table the system's roster**, which is the same mistake D-062 refused when it
declined to answer "who is running this camp?" by reading the grant table.

**What is actually given up against `unit_participation` is small and worth listing, because "no special
features" was the instruction.** No `join_reason_code` / `leave_reason_code` (and so no `transfer`,
`promotion`, `reorganisation`, `unit_closed` vocabulary to maintain or to get wrong), no `is_primary`
saying which of a person's groups to show first, no `role_in_unit` display label, no `data_confidence`
and nothing to import into: the corpus names no groups, so every member row is written by a person
([D-092](#d-092--the-corpus-is-people-and-events-and-it-names-no-units),
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
**Reverses:** [D-012](#d-012--status-strings-compare-by-rank-never-lexicographically)
(including the reason it was written), [D-013](#d-013--explicit-deny-revoked-is-checked-before-everything)
as a *level*, [D-032](#d-032--deny-is-absolute-locality-orders-allows-only)'s second half,
[D-074](#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular)'s level form,
[D-010](#d-010--role-assignments-and-access-grants-share-a-scope-model-and-a-resolver).
Amends [D-055](#d-055--the-permission-catalog-is-deliberately-comprehensive-and-granular),
[D-068](#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle) and
[D-079](#d-079--the-guardianship-channel-is-entered-by-shape-not-by-permission-name).

**Your words.** *"This is more complicated. I said that there are read, write, none permissions. This is
not correct. What would make the most sense is if items would inherit all unit-scope permissions and would
have their own item-scope permissions in the same format (e.g. `event.edit`). Both of those permissions are
essentially the same, however in the item-scope some of them don't make sense (e.g. on an event,
`membership.manage`, or `event.create`, make no sense). On the item-scope there should also be a
deny-permission, not just allow-permission."* And on whether anything still needs a ladder: **"only
allow/deny on the same permissions as on the root unit."**

**Decision.** **One grant is: a grantee, a scope, one permission code, an effect, and a period.** The
grantee is a person or an audience ([D-042](#d-042--grants-may-target-audiences-not-only-individuals),
unchanged). The scope is the unit or exactly one item ([D-097](#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)).
The effect is `allow` or `deny`. The answer is:

> **allowed** when some live allow applies and **no** live deny applies.

That is the whole of the precedence rule. What it replaces, item by item:

| Deleted | Was | Why it goes |
|---|---|---|
| `access_level` | `revoked` 0, `view` 10, `contribute` 20, `manage` 30, `admin` 40 | A level is a **bundle** of permissions identified by one word. [D-068](#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle) already refused that idea once, when it deleted `<resource>.admin` and said *roles are the bundle*. This finishes the same thought: roles and audiences are the bundle, and nothing else is |
| `permission_level` | which level satisfies which permission at which scope type | Its two jobs move to two columns on `permission` itself (§below) |
| The rank integer | [D-012](#d-012--status-strings-compare-by-rank-never-lexicographically) | There is no ordering left to compare. The famous bug it guarded — `'admin' < 'contribute'` — cannot occur in a system with no levels, which is a better fix than the guard |
| Locality | [D-032](#d-032--deny-is-absolute-locality-orders-allows-only): a nearer allow beats a further one | **Locality only ever ranked allows against each other.** With a boolean answer, two allows that both apply produce one answer; there is nothing to order. D-032's first half — deny is absolute — survives intact and is now its entire content |
| `revoked` as a level | resolver channel 0 | Deny survives as an **effect on a grant row**. [D-013](#d-013--explicit-deny-revoked-is-checked-before-everything)'s requirement — a court-ordered restriction must not be beatable by a broader grant — is unchanged and is still checked first |

**`permission` gains two columns, and only one of them is comfortable.**

- **`applies_to` ∈ `unit`, `unit_and_item`** — where a code may be granted at all. This is your
  observation that `event.create` and `membership.manage` are nonsense *on* an event, written as data
  instead of as prose. It is checked when the grant is saved, not at check time: a grant of
  `event.create` written on one event is refused with the reason in the error, because an event cannot
  be created twice, and a creation permission attached to a thing that already exists answers no
  question.
- **`right_kind` ∈ `read`, `write`** — and it exists for exactly one customer.
  [D-074](#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular) fixes a guardian's
  rights at three values, and with the ladder gone the guardianship channel has nothing left to compare
  a permission against. This column is that thing: `none` covers nothing, `view` covers `read` codes,
  `write` covers both. **It is a column whose only job is one other mechanism, and saying so is cheaper
  than discovering it later.** The alternative was to store permission codes on the guardianship row,
  which D-074 refused on the grounds that a volunteer cannot maintain a 74-code checklist per child.

**Inheritance, stated once.** A grant at the unit reaches **every item of every type**, because after
[D-097](#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row) there is no intermediate scope left
between the unit and an item, and no ownership relation to test. A grant on one item reaches that item
and nothing else. This is [D-006](#d-006--per-item-permissions-are-capabilities-on-the-item) —
per-item permissions are capabilities on the item — with the unit tier left standing, and it deletes
`can_event()` outright ([D-102](#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)).

**`-` in a selector is not a deny, and the two are not interchangeable.** An audience expression may
subtract a set (`MEMBERS - GROUP(x)`), which narrows **one grant's reach**. A deny defeats **every grant**
that applies to that person, including ones written elsewhere, later, or by somebody else. The first
cannot express "she must not have this, whatever else she is given", which is
[D-013](#d-013--explicit-deny-revoked-is-checked-before-everything)'s whole reason for existing, so denies
stay — and they are legal at the unit as well as on an item, since "exclude her from what the unit grants
everyone" is exactly the case the selector cannot serve.

**The round silently upgraded deny, and the upgrade needs naming because it changes an operator's job.**
[D-013](#d-013--explicit-deny-revoked-is-checked-before-everything) did not say a deny beats everything; it
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

**Reverses:** [D-039](#d-039--member-permissions-require-a-current-paid-membership)'s resolver clause,
[D-051](#d-051--the-membership-gate-is-waived-by-a-permission-not-only-by-a-role-flag) entirely,
[D-033](#d-033--multiple-people-may-occupy-the-same-position) and the position module,
[D-009](#d-009--unit-membership-links-to-person-not-to-membership)'s remaining subject.

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
[D-068](#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle) was already going; it
just went the rest of the way. `role.create`, `role.edit`, `role.delete`, `role.view`, `role.assign`,
`role.unassign` survive, retargeted: the last two write `role_holder`.
`role.scope_required` and `role.requires_membership` are deleted with their mechanisms.
`role` joins `person_group` in `grant_scope_type`, so *"these two may manage the counselors roster"* is a
grant on one role, which is D-098's move applied symmetrically.

**2. Positions are deleted.** `position`, `position_assignment`, `is_leadership`, `max_holders` and the
appointment workflows go: with no units there is no *body* to be a leader **of**, which is the only thing a
position recorded and a role does not
([D-033](#d-033--multiple-people-may-occupy-the-same-position)'s own reasoning for why leadership is a
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
[D-039](#d-039--member-permissions-require-a-current-paid-membership) made the resolver ask, for every
grant, whether the holder currently holds a membership;
[D-051](#d-051--the-membership-gate-is-waived-by-a-permission-not-only-by-a-role-flag) then needed
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
gated. [D-071](#d-071--nothing-forces-a-role-assignment-to-end-the-gate-and-the-report-are-the-control)'s
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
  of [D-090](#d-090--the-legacy-corpus-is-thousands-of-roster-rows-with-numbers-and-no-money) must count
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
organization out of its own system.** [D-040](#d-040--the-fee-expires-yearly-a-date-tracked-renewal-window-replaces-a-grace-status)
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
it is the answer to [D-080](#d-080--five-contradictions-the-translation-surfaced-and-how-each-was-resolved)'s
lesson about two same-shaped tables: **these are not two statements of one rule, they are two different
grants of power.** Same columns, different codes, and `ROLE(x)` / `GROUP(x)` distinct in the grant text so
the distinction is visible to whoever reads the grant — which is where you asked for it.

**`COUNSELORS` is seeded, as a role.** A permanent, organization-wide population is the opposite of your
own definition of a group (*"a temporary set of members that do events together"*), and the table decides
the sensitivity that protects the set every safeguarding convention hangs from. It ships `is_system` so an
editor refuses to delete it. Consistent with [D-005](#d-005--permissions-are-grants-never-derived-from-identity):
this is a **set**, and being in it confers nothing until a grant names it — audience membership has never
been authority
([D-042](#d-042--grants-may-target-audiences-not-only-individuals), restated in
[D-091](#d-091--a-permission-group-is-a-rule-and-a-list-at-once-and-a-rule-may-name-another-group)).
Bare `COUNSELORS` is legal in an expression, which makes the name namespace load-bearing
([D-101](#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree)).

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

## D-101 — An audience is an expression over named sets, stored as a tree

**Status:** decided (from your answers)
**Date:** refinement round 10
**Follows:** [D-098](#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority),
[D-100](#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)

**Amends:** [D-091](#d-091--a-permission-group-is-a-rule-and-a-list-at-once-and-a-rule-may-name-another-group)
in its third arm.
**Confirms:** [D-060](#d-060--eligibility-is-capability-there-is-no-separate-rule-engine),
[D-011](#d-011--scope_id-on-access_grant-is-polymorphic-with-no-foreign-key).

**Your words.** *"A group can be used as a selector in the audience rule (e.g.
`MEMBERS - GROUP(schuzka2026-1) * COUNSELORS` — meaning all counselors that are not part of the group
`schuzka2026-1`)."* Asked which of two notations to build on: *"Would it be easier for the system if we
wrote an evaluator for each person (`MEMBER & COUNSELOR | ROLE(TREASURER)`) or as a union/difference of
groups?"* — and then: *"I dislike the lack of operand precedence. I would like to be able to use
brackets."* — and then: *"Can we not store it as expressions? Each row has two operands and one operator,
and the operands can be either another row or a selector."*

**First, the reframe that makes the notation question smaller than it looks.** `p ∈ (A ∩ B) ∪ C` **is by
definition** `(p ∈ A ∧ p ∈ B) ∨ p ∈ C`. The two notations you were offered are the same function written
from two ends, so the choice does not decide what the machine computes; it decides **what gets stored and
what a writer is allowed to say**. The answer is therefore both, split by direction:

> **Author in sets. Evaluate per person.**

A check asks about one person, so the resolver compiles the expression down to a predicate and never
materializes a set. An implementation that evaluates `MEMBERS` as a list of ids and then tests for
containment pays three thousand rows per request, which is the one way to get this wrong and the reason
the requirement is written here rather than left to whoever builds it.

**Why the set form is the source language, in one argument each.**

- **It is no weaker.** `-` is complement against `EVERYONE`, `*` distributes over `+`, so every boolean
  formula has an equal expression here. The predicate form buys **zero** expressive power.
- **It is the closed one, and that is the whole case.** D-060 refused a rule engine, and a per-person
  boolean language is the door to one: once `&`, `|` and `!` exist, the next operand somebody wants is
  `AGE >= 15` or `FEE_PAID`, and there is a parser standing there to accept it. A set language closes it
  **by rule instead of by discipline**: *an operand must be a named, materializable set of people*. An
  attribute is not a set of people. Guardianship is (`GUARDIANS(x)` is a set), age is not, and the line
  falls exactly where D-060 already drew it — eligibility stays capability.
- **The three workloads the corpus already promises.** "Who does this grant reach?" must be **shown,
  expanded, in front of a human** — D-091 made that a requirement on the screen, not a nicety, and a
  predicate can only report `true`, while a set *is* the answer. "What may a treasurer do?" (D-100) needs
  the person→set index, and `role_holder` and `person_group_member` **are** it; an expression is
  unindexable. Caching ([F-6](../open-questions.md#f-6--the-permission-cache-lifetime-and-what-invalidates-it)) can
  key on an operand and be reused across every grant, and `role_holder` changes are the invalidation.
- **It is the schema that exists.** An audience's manual arm, its included groups, and `everyone` /
  `all_members` / `guardians_of` are already named sets; the only genuinely new symbols are `*` and `-`.
  Today's audience has **no intersection and no difference at all**, which is why your example was not
  writable in any notation.

**Grammar.**

```
expr    := term ( '+' term )*
term    := operand ( ( '*' | '-' ) operand )*
operand := EVERYONE | MEMBERS | LIST | PERSON '(' person ')'
         | GUARDIANS [ '(' person ')' ]
         | ATTENDED [ '(' event ')' ]     | PLACED [ '(' event ')' ]
         | CONFIRMED [ '(' event ')' ]    | ON_WAITLIST [ '(' event ')' ]
         | ORGANIZERS [ '(' event ')' ]              argumentless = bound, [D-102]
         | ROLE '(' name ')' | GROUP '(' name ')' | AUDIENCE '(' code ')'
         | name                                      bare; the shared namespace below
         | '(' expr ')'
```

**`MEMBERS` names a set the membership module already defines, and does not define it here.** It evaluates
`is_current_member(person)` — status `active` with a period covering the checked date, **no grace
coalescing**, because the renewal window is a date range for rejoining and not a state in which somebody
is a member ([data-model/03-membership.md §3](../data-model/03-membership.md#current-membership-queries),
[domain/06-authorization-model.md §6.1](../domain/06-authorization-model.md#61-members--the-membership-test-moved-into-the-expression)).
That is the whole reason the language works: an operand is the *name* of a set somebody else already
provably owns, which is what "materializable" has to mean for this to stay out of rule-engine territory.

*(The `AUDIENCE` arm is [D-103](#d-103--an-audience-may-name-another-audience)'s, added the same round
this entry was written, and it is the reason this grammar is marked as amended rather than final: an entry
that ships a grammar and then grows an arm is worth seeing to have grown one.)*

**Two arms the first draft of this grammar omitted, and both were load-bearing elsewhere in the round.**
`PERSON(x)` names one person — a set of one, so it passes the materializability test, and it is how
`system.gate_exempt`'s "except Honza" is written inside the expression that granted the rule in the first
place, which keeps the exception visible next to the thing it exempts. And **bare `name`**, because the
round's own control is written `MEMBERS * COUNSELORS`: an expression that does not parse is not a control.
`ROLE()` and `GROUP()` remain as explicit qualification, required in the canonical rendering.

**Both arms were still missing from the seeded registry when the registry was written, and that is worth
recording rather than fixing quietly.** [data-model/05-authorization.md §8](../data-model/05-authorization.md#the-selector-registry)
was written from the evaluator's arm list, not from this grammar, and an arm list copied from an
implementation is exactly the kind of source that loses an arm nobody had implemented yet. The registry
carries **thirteen** rows and `PERSON` is one of them: `takes_argument` true, `argument_type` `person`,
`binds_to_item` false. Its distinction from `LIST` is real and is why both survive — `PERSON(x)` is an
argument, so it composes and can be subtracted on its own, while `LIST` is one set of several people
belonging to one audience and subtracting it removes everybody on it. D-103's kitchen example needs both,
which is the proof that they are not the same operand wearing two names. The class of defect is
[F-19](../open-questions.md#f-19--closed--a-permission-code-is-a-row-prose-names-codes-and-nothing-checks-the-two),
it arrived here in a second registry inside the same round, and
[D-104](#d-104--a-permission-codes-last-segment-is-an-action-and-a-registry-that-prose-contradicts-is-a-fiction)
is the answer to it.

`*` and `-` bind tighter than `+`; **`*` and `-` bind equally, left to right**; brackets override. The rule
is arithmetic-shaped so nobody has to learn a table, with one deliberate departure from arithmetic: `-`
does **not** sit beneath `*`. The reason is the first expression anybody writes in this language —
`MEMBERS - GROUP(schuzka2026-1) * COUNSELORS`, meant as *"all counselors not in that group"* — which is
what left-to-right gives and is **not** what `*`-tighter-than-`-` gives. Precedence was chosen to match
the reading the writer already had, not to be defensible on other grounds.

**The canonical form prints every bracket, always.** Not for legibility, so that the paragraph above is
never load-bearing when somebody reads a grant two years from now: the stored form of the example is
`(MEMBERS - GROUP(schuzka2026-1)) * COUNSELORS`, the editor rewrites what is typed into that before
saving, and an implementer who reaches for arithmetic precedence in their parser builds a **different
expression** than the one the writer meant. **This entry's first draft got its own rule wrong** — it
asserted that the bare form had changed meaning, which is the `*`-tighter reading this entry then refused
— and the correction is worth keeping in place of the claim, because the mistake is exactly the one the
always-bracketed canonical form exists to make impossible: two precedence rules can sit in one document,
agree with each other in the abstract, and disagree the moment an expression is written without brackets.

**Storage: the tree you described, not a normal form.** Each row is a node: `operator` + `left_id` +
`right_id`, or a leaf's `selector_kind` + `selector_arg_id`. My alternative was to normalize to a union of
terms on save; **yours is better and the reason is the round's thesis** — the normalizer is the code
(distribute, dedupe, sort, survive blow-up), and a binary tree needs one evaluator of about fifteen lines
and keeps the writer's brackets instead of silently rewriting them. It also makes the depth limit the only
complexity bound, since `(A + B) * C` costs nothing. The rules that come with it:

| Rule | Where it is enforced |
|---|---|
| **Exactly one shape.** A node has `operator`, `left_id`, `right_id` and no selector; a leaf has `selector_kind` and no operator or children. | A check on the row — expressible, so it stays a constraint |
| **One parent, never a DAG.** `parent_id` lives on the child, so a node belongs to exactly one expression. A side table letting two expressions share a node is refused: editing the shared node would silently widen every grant using it, which is D-091's inclusion hazard re-imported | Structure, plus a CI check that no such table exists |
| **Cycles and depth refused when the row is saved** — walk the parent chain, refuse a revisit, refuse past `selector_depth_limit`. Structurally hard to build; refused rather than trusted, for D-091's own reason: *a hand-fixed row, a restore from before the guard existed*. **Amended by [D-103](#d-103--an-audience-may-name-another-audience):** the parent-chain walk sees one tree, and `AUDIENCE()` makes cycles possible *between* trees, so the guard is a reachability walk over the reference closure and the depth bound is counted there too | The write path, exactly as `uq_audience_include_acyclic` was |
| **`selector_arg_id` has no foreign key** — it points at `role`, `person_group`, `audience`, `person` or `event` depending on kind | [D-011](#d-011--scope_id-on-access_grant-is-polymorphic-with-no-foreign-key)'s already-accepted trade-off, with its compensating orphan check |
| **An operand that does not resolve is the empty set.** Fail closed, in every direction, as §Evaluation of `data-model/05` already rules for audiences | The resolver |
| **The whole tree is fetched in one indexed read** by denormalizing `audience_id` onto every row, then assembled in memory. The read path never walks a parent chain. **Amended by [D-103](#d-103--an-audience-may-name-another-audience):** still one read per *audience*, but an expression that names another audience needs one per audience in its closure, so the honest claim is "no parent-chain walking", not "one query" | A stated implementation requirement |

**A naming ruling, written down because the table sits outside the naming conventions and somebody will
notice.** [`data-model/00-conventions.md §2`](../data-model/00-conventions.md#2-naming) admits two shapes —
a junction table named `<a>_<b>` alphabetically, and a lookup table named for the vocabulary it *is* —
and `audience_operand` is **neither**: it is a recursive structure, which the conventions have no rule for
because until now the model had none. It is kept for the reason the two existing rules exist: the name
should tell a reader what a row means. *Operand* is the word the grammar itself uses, so the table teaches
the language; `audience_node` was weighed and refused, because it names a graph shape and would leave a
reader who has not met the grammar no better off than `audience_thing`. Worth marking anyway, because it is
the reading that gets a migration wrong — singular-for-an-aggregate invites someone to build one row per
audience, when **the aggregate is the tree and a row is one node of it**. The diagram caption and the data
model's first line both say *rows of one audience's expression tree* for that reason. *This entry's first
draft justified the name by citing a naming decision that turned out not to exist* — the rule is a
conventions table, not a numbered decision, and a citation invented to settle an argument is the kind of
thing this log keeps a record of.

**`selector_type` is a seeded registry, not an enum.** Which operands take an argument, which may bind to
the item, and what type their argument is — that was three hard-coded lists (the `resolver_key` enum
written out in prose, the reserved-word list, the "meaningless without a `resolver_key`" rule). It becomes
one seeded table in the shape `grant_scope_type` already is: `code`, `takes_argument`, `binds_to_item`,
`argument_type`. The parser reads its reserved words from it, the editor builds its dropdown from it, and
the write path checks arity against it. **The language becomes data.** `audience.resolver_key` and
`scope_parameter` are deleted into it.

**Two sentences this paragraph needed, and did not have.** The registry is data, so say what is *not*
thereby open: **every `selector_type` row is seeded and `is_system`, and the organization may not add one at
runtime.** "Closed language" and "the language is a table" are contradictory unless the table is read-only
to tenants, and the read-only version is the one that keeps D-060's line — an operand is a shipped
predicate, not a thing a well-meaning registrar invents at 23:00. One consequence of that rule is a refusal
worth naming because it was nearly built: **a set of *grants* is not an operand.** `GRANTS(<ids>)` — "all
the people these grants reach", wanted as a way to move a bundle of grants at once — cannot be one, because
an operand must resolve to a set of **people**, and that is what a grantee is; the bulk operation it was
wanted for is a screen over the grant list, not a meaning a stored grantee can carry. Refusing it on the
type rather than on permissions is also what removes the awkward status such a row would have had: with
this rule, every seeded selector is a shipped selector, and there is no third kind. What the deletion of `resolver_key` does
leave unsaid is where a code meets its implementation: the resolver dispatches on `code`, and a seeded row
with no shipped resolver is a **deployment bug that shows up as an empty set**, fail closed like
everything else in the round. Second: this is what makes the age question answerable at all. Attribute
operands are refused above, so *"13 and over"* cannot be typed by a writer; under
[D-070](#d-070--an-event-has-no-age-ceiling-the-grant-is-the-rule) the answer stays *"open the event to the
set whose members are that age"* — a group somebody maintains — and an `AGED_13_PLUS`-style operand becomes
legal **only** as a shipped selector, which is the one route this paragraph allows and the events document
was right to guess. **Nothing of the kind is seeded at go-live**, because one shipped age band is the
first step onto a ladder nobody asked for.

**The inclusion arm dies, and composition survives by changing hands.**
[D-091](#d-091--a-permission-group-is-a-rule-and-a-list-at-once-and-a-rule-may-name-another-group) let a
group pull in other groups through `audience_include`, because a group could otherwise not be composed.
Under [D-098](#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority) a group's
membership **is** its dated rows, and composition now lives in the expression: `GROUP(kitchen) +
ROLE(troop_staff)` composes as much as an edge ever did. What goes with the edge table is a great deal of
machinery — the transitive walk, `include_depth_limit`, the write-time cycle walk over a *graph*, and
integrity check 20's job of asserting that the walk exists — because a **tree cannot cycle**, so the only
acyclicity guard left is the cheap parent-chain one. ~~That sentence is the second-most-durable claim in
this entry.~~ [D-103](#d-103--an-audience-may-name-another-audience), written the same round, lets an
operand name another audience, and a **forest of trees pointing at each other does cycle**: the save-time
reachability walk comes back, as does a depth bound counted over the closure. What stays deleted is the
edge table and the materialized closure check 20 asserted — the edges are `AUDIENCE` leaves in the table
that already exists. What is genuinely lost: *"add the kitchen crew to
everything the troop-staff group is used for"* is no longer one edit. The answer is that named sets are
the composition mechanism now — name the composite once, aim grants at it — which is D-091's outcome
reached without a graph nobody could see the shape of.

**`audience_member` stays, re-roled as the `LIST` leaf.** It is the audience's own dated list of people,
reachable in an expression as one operand. Merging it into `GROUP(x)` was weighed and refused twice over:
naming three people in one grant would create a row in the group browser that is not a group anybody
talks about, and D-098 already wrote the rule that keeps the two dated-member tables apart (a group's
members are true with no grant pointing at them; a selector's additions are meaningless outside the
selector). The duplication D-080 would flag is therefore **kept on purpose**, and the mitigation is the
one D-091 already required: the editor shows which mechanism each person arrived through.

**Names are one namespace, and that is a new dependency.** Bare `COUNSELORS` resolves against roles and
groups together, since `ROLE()` and `GROUP()` no longer have to disambiguate. So: names unique across
`role` and `person_group` — and `audience.code` joins them in [D-103](#d-103--an-audience-may-name-another-audience),
so it is three tables and **no single constraint spans three of them** — which means the write path carries it and an
integrity check asserts it exists, per [D-081](#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now);
case, whitespace and separators folded on write; and **every `selector_type.code` is a reserved name**, so a
group called `MEMBERS` is refused at the save rather than silently rewriting every gate expression in the
system. What is stored is always kind + id, so a rename never rewrites a grant.

**Given up, once.** Storing a tree means two expressions with the same meaning are two different row sets,
so *"you already granted exactly this set on that row"* no longer falls out of storage. The route back is a
normalized **fingerprint** computed on save as a derived value used only for a warning — and if the
expansion overflows, skip the warning rather than refuse the write: normalization informing a human, not
gating one. Registered as an open question rather than promised. Similarly, DNF could have flagged
term-matches-nobody syntactically; the tree catches only `X - X` on a single node, so "this selector
reaches nobody" belongs to the editor preview that already has to exist.

**Two-way door?** The language is a wide-open door — it is one seeded table plus an evaluator, and an
operand can be added by any later decision. Precedence is the closed half: once expressions are stored in
canonical fully-bracketed form, changing what binds tighter changes nothing already stored, which is a
nice property and the reason the canonical rendering is a requirement rather than a convenience.

**See:** [data-model/05-authorization.md §8](../data-model/05-authorization.md#8-audience--grants-that-target-a-set-of-people),
[domain/06-authorization-model.md §6](../domain/06-authorization-model.md),
[glossary.md](../glossary.md) (Audience, Selector, Filling rule, Locality).

---

## D-102 — Nothing owns an event. The people connected to it are named by selectors that bind to it

**Status:** decided (from your answer)
**Date:** refinement round 10
**Follows:** [D-097](#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row),
[D-099](#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality),
[D-101](#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree)

**Reverses:** [D-058](#d-058--an-event-is-a-dated-occasion-owned-by-exactly-one-unit)'s ownership,
[D-063](#d-063--an-event-is-an-artifact-of-its-unit-not-a-child-of-it),
[D-094](#d-094--the-root-unit-owns-every-imported-event).

**Amends:** [D-061](#d-061--event-answers-are-read-by-that-events-organizers),
[D-062](#d-062--organizers-are-appointed-on-the-event-not-granted),
[D-065](#d-065--capacity-is-a-waitlist-threshold-and-organizers-may-exceed-it),
[D-067](#d-067--presence-is-a-three-valued-fact-on-the-registration).

**Your words.** *"The events are owned by the root unit, so anyone with a permission to create an event can
create an event."* Then: *"I also want to include `ATTENDING(<event>)` (meaning is registered to an
event)"*, and on the tiers: *"let the user pick which they mean — mainly 'registered and confirmed', or
'registered and is confirmed or whitelisted or waiting for confirmation'"*, and on the argument-less form:
*"unparameterized form is great, I like that."*

**Decision.** **`event.org_unit_id` is deleted and there is no owner of an event.** An event is an item in
`grant_scope_type` like any other: `event.create` is held at the unit and creates an event; a unit-scope
grant reaches every event, because after D-097 there is no tier between the unit and the item and nothing
left to test. That deletes `can_event()`, the unit-authority rule that every event permission in this
module was reached through, and the integrity checks that guarded the owner column. D-063's famous
*artifact, not child* distinction has no artifact-and-unit pair left to distinguish, so it goes too.

**1. Bound operands.** Some selectors name a set **relative to the item being checked**, and write it
without an argument:

| Operand | On the item checked means | Explicit form |
|---|---|---|
| `ATTENDED` | said yes to this event | `ATTENDED(<event>)` |
| `PLACED` | said yes and is not waitlisted — **the capacity set**, the one §5 counts and the index already serves | `PLACED(<event>)` |
| `CONFIRMED` | holds a paid place on this event | `CONFIRMED(<event>)` |
| `ON_WAITLIST` | is waiting for a place on this event | `ON_WAITLIST(<event>)` |
| `ORGANIZERS` | runs this event | `ORGANIZERS(<event>)` |
| `GUARDIANS` | are the guardians of the person this item is about | `GUARDIANS(<person>)` |

**Every one of these is a seeded `is_system` row of `selector_type`, and `is_system` is not decoration
here.** [D-101](#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree) made the registry
read-only to an organization, so no tenant action can add an operand; what `is_system` guards is the
*platform's own* delete path, and it is also the flag that tells a reader this code is vocabulary rather
than content. The alternative — seeded but deletable — is a grant breaker with no crime attached: remove
`ORGANIZERS` and every `event.answer.view` grant in the system silently resolves to nobody while the audit
trail goes on reporting them live. `ROLE` and `GROUP` are the only kinds an organization populates, and it
does so by writing `role` and `person_group` rows, not registry rows.

The argument-less form is the important half, and it exists to kill a specific flaw: `ATTENDING(<event
1204>)` — *attending* being this round's starting word for the idea, refused above in favour of four tiers
that each name a stored column — written on event 1204 is one grant per event with the event's own id typed
into it, so "every
participant may see the other participants" is a thing you do 400 times and forget on the 401st. Bound,
it is one expression written the same way every time. Two rules make it safe:

- **A bound operand is legal only on an item-scope grant.** At the unit there is nothing to bind it to, so
  it is refused when the grant is saved, with the operand named in the message.
- **A bound operand is legal only on a matching item type.** `PLACED` on a `person_group` grant is refused
  because that item is not an event. This is `selector_type.argument_type` checked against
  `grant_scope_type` — which is a reason the registry of D-101 is doing real work and not merely tidying.

**2. `ORGANIZERS` is what replaces unit authority over an event, and it is not a contradiction of
D-062.** With the owning unit gone, "the people running this event" has no other expression, and
[D-061](#d-061--event-answers-are-read-by-that-events-organizers)'s rule (answers are read by that event's
organizers) has to be *said* somewhere now rather than hard-coded in prose. It is said as a seeded grant:
`event.answer.view` on an event to `ORGANIZERS`. [D-062](#d-062--organizers-are-appointed-on-the-event-not-granted)
and its *"an `event_organizer` row grants nothing"* both stand untouched, because **an operand is a set,
not a grant** — the same sentence §8 of the authorization model already repeats twice for `unit_leaders`
and audiences generally. What changed is only that the appointment is now *aimed at* by grants instead of
being special-cased inside the resolver.

**And a seeded grant carrying a bound operand is not one row — a sentence this entry omitted and the
events module then had to assume.** A grant's scope is the unit or exactly one item, and a bound operand
is legal only on an item-scope grant, so there is **no row** that says *"every event's answers go to its
organizers"*: the one row that would say it needs the unit as its scope, which is precisely where the
operand is refused. What is seeded is therefore a **template**, and the event-creation path instantiates it
beside the event row. Two consequences, both kept:

- **The import owes one instantiation per event row it writes** — this module's share of
  [D-093](#d-093--the-one-off-import-may-create-memberships-both-ends-dated)'s shape, and cheap, because it
  is the same insert the event row already needs.
- **An event whose creation failed between the event row and the grant has nobody who can read its
  answers.** So the two writes are one transaction, and the check is a report — *events with no
  answer-view grant* — because "these two rows exist together" is
  [F-10 shape 1](../open-questions.md#f-10--which-invariants-the-orm-cannot-express-and-who-writes-those)
  and no layer this project owns can express it.

What the per-event row buys, and it is not accidental: answers-view is **revocable on one event** without
touching anyone's appointment, which is the kind of thing an organizer asks for the week before a camp.

**3. Four attendance tiers, and the refusal of a fifth.** You asked the writer to pick; picking requires
that the choices be the stored facts and not four new ideas, so each tier names columns of
`event_registration` and nothing else. `PRESENT(<event>)` over `was_present` is **refused**, and the
reason is the failure direction: `was_present` is `NULL` until someone takes a register, so an operand
built on it would revoke a child's access to their own camp photos because a volunteer forgot to tick a
box. That column is a safeguarding signal — *three-valued on purpose*, per
[D-067](#d-067--presence-is-a-three-valued-fact-on-the-registration) — and keeping it out of the selector
language is what keeps it meaning "a person recorded this" rather than "this is who may see things".
`WHITELISTED` has **no stored state to name**: the nearest facts are `source = staff` (an organizer
entered them) and promotion off the waitlist. Either it means one of those or it is a new column on
`event_registration`, which is an events decision and not a selector decision, so it stays an open
question rather than being implied by a word in a grammar.

**4. The set a grant reaches is now per-item.** D-091's requirement that the editor show the expanded
people — *"the person saving the grant is looking at one row that mentions no person at all"* — can no
longer be answered from the grant alone: `PLACED` means different people on different events. So the
preview is computed **for an item** and says so on screen, and the cache key for a bound operand must
include the item ([F-6](../open-questions.md#f-6--the-permission-cache-lifetime-and-what-invalidates-it) amended).
**Import consequence:** the one-off import owes `event` rows and `event_registration` rows
([D-090](#d-090--the-legacy-corpus-is-thousands-of-roster-rows-with-numbers-and-no-money),
D-093's shape), and it owes **no owner column**, which is the import-side saving D-097 already counted.
[D-094](#d-094--the-root-unit-owns-every-imported-event) is deleted rather than reversed: there is no
column for an imported event to have.

**Two-way door?** Narrow and expensive. Re-introducing ownership means the owner column, the resolver
tier that reads it, and every check that the module deleted — but the selectors added here are not in the
way, because an ownership grant and a bound operand answer different questions and can coexist. That is
the difference between this and [D-097](#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row):
that entry deletes a dimension, this one removes a *test* and leaves the vocabulary intact.

**See:** [data-model/08-events.md §2, §8](../data-model/08-events.md#8-projections-and-guards),
[domain/07-events.md](../domain/07-events.md),
[data-model/05-authorization.md §10](../data-model/05-authorization.md#10-the-resolver).

---

## D-103 — An audience may name another audience

**Status:** decided (from your answer)
**Date:** refinement round 10
**Follows:** [D-091](#d-091--a-permission-group-is-a-rule-and-a-list-at-once-and-a-rule-may-name-another-group),
[D-098](#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority),
[D-101](#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree)

**Amends:** D-101's grammar, its "a tree cannot cycle" claim, and its one-indexed-read fetch.

**Your words.** *"What is a `LIST`? Also it should allow nesting AUDIENCEs."* The second sentence is the
decision; the first is the reason this entry has to be written at all, and §1 below is its answer.

### 1. What `LIST` is, said plainly

**`LIST` is this audience's own hand-typed list of people** — the rows of `audience_member`, which is the
one table in the module that holds persons rather than rules. It is the only operand that is not a rule
about people: `MEMBERS` is a test, `ROLE(vedoucí)` is an office with dated holders, `PLACED` is a join
against an event, and `LIST` is *the names somebody typed into this one grant*.

It exists so that **a grant can carry its own exceptions without creating a thing everybody can see.**
*"Everyone in the kitchen crew, plus Honza, minus the two people who left"* is
`(GROUP(kitchen) + LIST) - PERSON(a) - PERSON(b)`. The alternative — making Honza a member of
`GROUP(kitchen)` to reach one grant — edits a roster that other grants read, which is D-091's hazard, and
it also invents a group nobody talks about, which is the rule D-098 wrote. So `LIST` is scoped to the one
expression that contains it, is invisible in the group browser, and dies with the audience.

The name is the weak part of this design and the question you asked is the evidence: nothing in `LIST`
says *whose* list. The registry entry carries the gloss *"the people written into this audience"*, and the
editor renders the operand as `LIST (this audience)`. Renaming the code was refused only because the round
has already propagated it through four files and the gloss costs nothing; if it keeps causing this
question, the replacement is `ADDED`, which says where the rows came from.

### 2. The decision, and the hole it closes in D-101

**An operand may name another saved audience: `AUDIENCE(<code>)`.** It is an ordinary selector — one row
in `selector_type`, `takes_argument = true`, `argument_type = audience`, and it therefore costs one seeded
row plus a resolver arm of about the same length as `GROUP`'s.

The stronger reason is that **D-101 did not deliver the answer it claimed to.** Having deleted
`audience_include`, it answered *"add the kitchen crew to everything the troop-staff rule is used for"*
with *"named sets are the composition mechanism now — name the composite once, aim grants at it."* But
under D-101's own grammar the only names available were `GROUP()` and `ROLE()`, and **both name a roster,
not a rule**: a group's members are its dated rows. The rule you wanted to reuse had no name to point at,
so the composite could be named only by copying its rows into a second audience — which is `audience_include`
with the copy step done by hand. Nesting is the half of that answer that was missing: **`AUDIENCE()` is
what makes a rule namable.**

It is also the arm that composes the two things the round kept apart. `ROLE()` names an office, `GROUP()`
names company, `ATTENDED()` names attendance; only `AUDIENCE()` names a **decision about access**, so it
is the only arm that can say *"the same people that grant may see the fee ledger, plus the accountant"*.

### 3. The three named sets, which are not the same thing

| | `GROUP(x)` | `AUDIENCE(x)` | `LIST` |
|---|---|---|---|
| What it is | A dated roster somebody maintains | A saved expression, evaluated live | Rows on this one audience |
| Who may change who is in it | `person_group.member.manage` | `audience.update` on that audience | whoever may edit this audience |
| Does it exist outside a grant? | **Yes** — D-098: a group's members are true with nothing pointing at them | No — it exists to aim a grant | No |
| *"Was she in it on 1 June 2024?"* | **Answerable**, from the dated rows | **Not answerable** past the audit window | Not answerable |
| Sensitive as | ⚠ company | 🔒🔒 authority | 🔒 |

That fourth row is the honest cost and it is the D-100 distinction replayed one level down. `GROUP(x)` is
materialized, so it keeps a history you can be asked about; `AUDIENCE(x)` is a live rule whose past shape
survives only in the audit trail, and [D-088](#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)
expires those payloads after 24 months. So *"who could see this child's data in 2024?"* is answerable when
the grant pointed at a group and **is not** answerable when it pointed at a nested audience. A rule whose
reach cannot be reconstructed is still the right tool for a rule — the roster is the wrong tool for
*everyone over 13* — but the gap should be closed by the report in §5, not by pretending the question has
an answer.

### 4. Rules that come with it

| Rule | Why, and where it is enforced |
|---|---|
| **A reference names a `code`, not a name, and only audiences that have one may be referenced.** `audience.code` is optional and unique-where-set; naming stays opt-in, and an unnamed audience is simply not composable. The leaf may not point at a null code — a check reading another table, [F-10 shape 3](../open-questions.md#f-10--which-invariants-the-orm-cannot-express-and-who-writes-those). | Audiences were allowed to be anonymous before this round and there is no reason to force a name onto a grant's private addressee list. |
| **The code joins the shared namespace** of D-101 — `role`, `person_group`, `audience`, and every reserved `selector_type.code`. Still no single constraint spans three tables: the write path carries it and an integrity check asserts the write path exists, per D-081. | A name that resolves two ways is a silent grant. |
| **Bare names do *not* resolve to audiences.** `MEMBERS * COUNSELORS` stays a role or a group; the audience arm must be written `AUDIENCE(veterans)`. | Adding a third table to bare resolution would change what existing stored expressions mean, and the explicit form costs four characters at the one place where being careful is the point. |
| **Cycles are refused across audiences, at save.** | See below. |
| **Depth is bounded over the expanded tree, not the local one** — the bound is the same `selector_depth_limit`, counted after references are followed. | A bound measured per-audience is a bound on nothing. |
| **An audience may not be ended or deleted while a live grant, or a live audience reachable from a live grant, names it.** Refused at save; the reverse lookup is a query over `audience_operand` rows whose `selector_kind = 'AUDIENCE'`. | Without this, "ended" would be a way to silently empty an expression, and under `-` an empty operand makes the result **wider**. |
| **The same refusal extends to `person_group` — ruled here, in the round after the row above — and it has to be ruled in both directions, which the audience row above does not say loudly enough.** Ending a group that something live names is refused; **so is writing a grant whose expression contains `GROUP(x)` onto a group that is already ended**, or naming an ended group from an audience. Two causes put a row on the report and only one of them is a broken write path: a rule that constrains *ending* leaves the second cause untouched, and the hazard is identical either way. | The group module found it by writing the opposite as the safe direction: a live grant on an ended group *is* safe on the allow side and **widens a deny** on the `-` side, which is the same asymmetry wearing a different table's clothes. The argument is identical, so the check is: refused at save in both directions, over `audience_operand` rows whose `selector_kind = 'GROUP'`. |
| **`ROLE(x)` needs no such rule, and the difference is worth naming.** An office has no way to be emptied quietly: there is no `role.retire`, no status, and deletion is already refused while holder rows exist. | A group has a lifetime, so ending it is one click that empties a set. A role's members are ended one row at a time, on a screen that shows each person. **The hazard is a property of the shape, not of the idea**, which is why this row is an exception list rather than a third copy of the check. |
| **An unresolvable leaf is still the empty set.** On the allow side that is quiet and safe; on the deny side `EVERYONE - <nothing>` denies everybody, which is loud. | The loud failure is the one you want. The quiet alternative is discovered in an audit, two years late. |
| **Naming an audience requires reading it,** and grants no read of it to the people it contains. | Fail closed, and *see what you name* is already D-091's requirement. |

**One of D-101's sentences is now false and stays struck.** *"a tree cannot cycle, so the only acyclicity
guard left is the cheap parent-chain one"* — true of one tree, false of a **forest of trees pointing at
each other**, which is what this decision makes possible. `audience_include` is not coming back: the edges
are the `AUDIENCE` leaves, so there is no edge table, no transitive walk over rows, and no
`include_depth_limit`; what returns is the write-time reachability walk D-091 already required, over a
graph built at save time from rows that already exist. The machinery D-101 counted as deleted stays
deleted; only its confidence was wrong.

### 5. What this costs, stated as the hazard it is

**Editing an audience changes grants you did not make.** Add a person to `AUDIENCE(veterans)` and every
grant that names it now reaches them — including grants their owner wrote for a different purpose, and
including grants this editor cannot see because they are not theirs. This is not a new failure mode:
`GROUP(x)` has had this property since D-091, and the round accepted it there for the reason it is
accepted here, which is that **a named set is worth being reusable and a reusable thing has more than one
user**. The mitigation is D-091's, extended to the second user: saving an edit to a referenced audience
shows *which grants name it, and at what depth*, before it commits, and the same listing is what closes
the history gap in §3 as a report rather than as a reconstruction.

*Assumption:* the listing is cheap at the sizes this organization runs at, because the edges are indexed
rows in the table that already holds every expression. Unverified at any size, and a slow save screen is
a real risk if the audit-and-import corpus's row-count estimates are wrong.

**Two-way door?** Narrower than D-101's and wider than D-102's. Removing nesting later means finding every
stored `AUDIENCE` leaf — they are one indexed query — and inlining the subtree it pointed at, which
changes no grant's meaning on the day it runs and makes every one of them unmaintainable afterwards. So:
the door closes quietly rather than loudly, which is the reason the depth bound and the reference listing
are requirements rather than suggestions.

**See:** [D-101](#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree) for the language
this adds one arm to, [data-model/05-authorization.md §8](../data-model/05-authorization.md#8-audience--grants-that-target-a-set-of-people)
for the table, and [D-091](#d-091--a-permission-group-is-a-rule-and-a-list-at-once-and-a-rule-may-name-another-group),
whose inclusion edge this replaces for the second time.

---

## D-104 — A permission code's last segment is an action, and a registry that prose contradicts is a fiction

**Status:** decided — **by the assistant at the close of round 10, not from an answer of yours.**
Reversible, and cheap to reverse today; the day the first grant row exists it becomes a migration, which is
the only reason it is written as a decision rather than fixed as a typo.
**Date:** refinement round 10

**Resolves:** [F-19](../open-questions.md#f-19--closed--a-permission-code-is-a-row-prose-names-codes-and-nothing-checks-the-two).

**Follows:** [D-055](#d-055--the-permission-catalog-is-deliberately-comprehensive-and-granular),
[D-068](#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle),
[D-072](#d-072--the-documentation-carries-no-sql-the-schema-is-the-orms-job),
[D-075](#d-075--money-arrives-from-a-bank-api-a-payment-is-requested-by-variable-symbol-and-qr-code),
[D-081](#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now),
[D-101](#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree).

### 1. What happened to the QR capability, which is the part worth reading

F-19's third instance was a permission code named two ways in one round: the event door code, written
`event.qr` in one place and `event.qr.rotate` in another, against a catalog that states its naming patterns
as descriptions of the codes it already had.

**It was not resolved by choosing a spelling. The capability is gone.** Grepping the closed round finds
neither string anywhere in the corpus — not in the catalog, not in the events module, not in the ERD, not in
this log. What survives of it is F-19's own description of the dispute.

What happened, stated plainly: **a capability entered this round as prose, was half-designed in the course of
arguing about its name, and left as prose** — swept away by the same parallel rewriting that introduced it,
with no entry in this log involved at either end. Presence is what
[D-067](#d-067--presence-is-a-three-valued-fact-on-the-registration) and
[EV-5](../open-questions.md#ev-5--closed--it-split-and-the-new-permission-sits-a-level-lower) left it: somebody
holding `event.presence.mark` records who came, with a clipboard if necessary. The only QR code in this system
belongs to a payment, and [D-075](#d-075--money-arrives-from-a-bank-api-a-payment-is-requested-by-variable-symbol-and-qr-code)
already rules that **a QR code is a rendering, not data** — it encodes three stored facts and is worth keeping
no row of.

**So the answer to "did we decide not to have check-in codes?" is no, and that is the finding.** Not a typo,
not a disagreement about morphology: a thing was possible in prose, argued over as though it were in the
model, and removed without ever having been in the model. The registry — the one place a permission legally
exists, since D-072 made these documents the specification rather than a description of a schema — never had
a row, so nothing refused anything. A reviewer who had asked "which seeded row carries this?" would have
ended the argument in one sentence, and nobody asked, because the argument was written in two files that
both looked like they were describing something real.

**Closed as follows: there is no QR capability, seeded or deferred, in the events module or anywhere
else.** If door scanning is ever wanted it arrives as an open question, then as a decision entry naming the
permission, the artifact that gets rotated, and who may reprint it — not as a code appearing beside a
paragraph about a door.

### 2. The naming grammar, promoted from a description to a rule

The catalog described two shapes — `<resource>.<action>` and `<resource>.<subresource>.<action>` — and the
dispute could not be settled by them because **both readings of `event.qr` fit the description.** A
description of how existing names happen to look cannot arbitrate a new name; that is why the `answer` /
`answers` case was easy (the catalog was self-consistent, so naming it the arbiter worked) and the QR case
was not. Three rules for a code being **added**, which is the only moment they cost nothing:

| Rule | The test, and what it refuses |
|---|---|
| **The last segment names the action.** | Read the code alone and ask *what does this let me do?* `event.grant_access` answers it; `event.qr` does not. A noun-final code states an object, and since [D-099](#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality) a grant states exactly one thing — a grant of an object would need a second sentence to say what it permits, and a second sentence is where a permission's real scope always hides. |
| **A middle segment names something the schema stores.** | `answer` is `event_answer`, `presence` is a column of `event_registration`, `contact`, `credential`, `member`, `participant`, `request` are all rows. **`qr` is nothing** — D-075 is explicit that it is a rendering of a symbol, an amount and a recipient. **A permission may not be built out of an artifact the database does not keep**, because a grant has to be checkable against stored state and there is none. This is the substantive test the QR case needed, and it decides the case without appealing to morphology at all. |
| **No grade words, and no prefix.** | `admin`, `all`, `everything`, and any code whose meaning is "every sibling under this prefix" — [D-068](#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle) deleted sixteen of them and computed the wrong answer for `dependent.admin`. **Restated here as a rule about codes that have not been written yet**, which is the only form of that decision that can still prevent anything. |

**One exception, named, because a rule with an unnamed exception is a rumour:** `system.admin`. Its last
segment is not an action and it stays. It survives because its meaning is *defined by the resolver* — checked
outright, `applies_to = unit`, never reachable through an item grant — rather than read off its name, and
because D-068 exempted it in so many words rather than by omission. **It is the only code in this system
allowed to be a noun, and the exemption is not a precedent**; `<resource>.admin` is exactly what rule 3
refuses and exactly what was deleted.

**The rules were applied to the registry as it now stands, and found nothing to correct**: of the
**sixty-six live codes in the catalog's tables**, sixty-five satisfy both the action test and the stored-state
test, and the sixty-sixth is `system.admin`. That is worth recording precisely because it is a null result —
the corpus was already following the rule, the rule was nowhere written, and the QR capability arrived anyway.
**A convention that is followed and not stated fails exactly once, on the first thing nobody thought to
compare.**

### 3. The report, adopted

F-19's recommended option is adopted: **before a round closes, every dotted token in prose is diffed against
the seeded registries** — `permission.code`, `selector_type.code`, `grant_scope_type.code`, `reason_code.code`,
and the seeded audiences — in both directions, so the report says which tokens name no row *and* which rows
no prose names.

- **It is a report run by hand.** This repository has no build step and no CI to hang a check on, so
  [D-081](#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now)'s
  wording applies exactly: **a convention, not a guard.** Saying that is part of adopting it, not a caveat
  appended afterwards.
- **It would have caught all four instances, including the one this round has not yet noticed.** The fourth:
  `PERSON(` is written into [D-100](#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)
  and [D-101](#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree) and used in four module
  pages, while the seeded `selector_type` registry — copied from the evaluator's arm list instead of from
  D-101's grammar — carried twelve rows with no `PERSON` in them. **So a control the round wrote for itself,
  `system.gate_exempt` as `MEMBERS * ROLE(x) + PERSON(y)`, did not parse,** and the pages that noticed
  resolved it by reading `PERSON(y)` as `LIST`, which is the wrong reading: `LIST` is one set belonging to one
  audience, so subtracting it removes everybody on it. D-101's registry amendment adds the thirteenth row.
  **Two registries, one round, same defect** — which is the strongest argument this entry contains for the
  report, and it was found by reading, in a file nobody had been asked to check.
- **Allow-listing is the cost and it is not small:** illustrative codes, and deleted codes shown struck on
  purpose, both match no live row. The report is worth running only if its allow-list is re-read rather than
  frozen, which is the same discipline the struck-text rule already imposes on this log.
- It runs **on the documents**, because there is no schema to check against
  ([D-072](#d-072--the-documentation-carries-no-sql-the-schema-is-the-orms-job)). That is the condition that
  makes the whole class possible: **the prose *is* the specification, so prose is free to contradict the
  registry, and there is no compiler to notice.**

### 4. What this is worth, and how it fails

**Two-way door.** Wide for the grammar, which renames nothing today. Already closed for `system.admin`'s
exemption, which every round since D-068 has leaned on. And irrelevant for the report, **which cannot be
violated — only forgotten.** That is this decision's failure mode and it is the only one: nothing in the
system will ever notice a code drifting from its row, including after this entry, because the enforcement
adopted here is a person remembering to run a script.

**What would make it obsolete.** An actual implementation, with a seed directory and a test that loads it.
Until then the registry and the prose are two copies of one thing
([F-10](../open-questions.md#f-10--which-invariants-the-orm-cannot-express-and-who-writes-those)'s general
shape, in its cheapest instance), and the report is the check that they still agree.

**See:** [F-19](../open-questions.md#f-19--closed--a-permission-code-is-a-row-prose-names-codes-and-nothing-checks-the-two),
which this closes, [data-model/05-authorization.md §8](../data-model/05-authorization.md#the-selector-registry)
for the registry with thirteen rows, and
[permission-catalog §1](../appendix/permission-catalog.md#1-conventions) for the naming patterns, which are
now rules and are written there as such.
