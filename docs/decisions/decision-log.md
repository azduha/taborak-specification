# Decision Log

Decisions taken, with the reasoning that produced them. Recorded so they are not
re-litigated from scratch — and so that when a decision is reversed, the reason for the
original choice is visible.

**Status values:** `decided` — settled, schema reflects it. `proposed` — recommended,
awaiting your confirmation. `assumption` — taken by default, stated in italics in the
docs, easily reversed.

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
`scope_type`, the level model, and one `can()` function. Three authority channels
(roles, item grants, guardianship), each dispatching from the permission's namespace.

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

**Note:** unit *scope* does inherit downward (D-015). That is a different axis.

---

## D-015 — Authority inherits downward through the unit hierarchy

**Status:** assumption ⚠ *confirm*

**Decision.** A role assigned at a unit covers that unit and all descendants. A district
treasurer can act on troops within the district.

**Why.** Matches how organizations actually work — a district officer has district-wide
responsibility.

**Reverse if:** your organization requires explicit per-unit grants with no inheritance.
That is a one-line change in the resolver (`unit_ancestors` call) but a system-wide change
in who can do what, so it must be deliberate.

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

**Status:** decided
**Date:** initial design

**Decision.** The system produces worklists; humans act. Grace periods absorb late payments.
Age-out is driven by `membership_type.max_age` but the transition is reviewed.

**Why.** Automatically removing a child's membership because a bank transfer was recorded
late is a real harm. Automation should stop short of the consequence.

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

## Reversed decisions

*(none yet — record reversals here with the date and the reason, rather than editing the
original entry)*
