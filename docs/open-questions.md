# Open Questions

Everything unresolved, each with its **schema impact** — what changes once you answer.
Ordered roughly by how much they block.

Marked: 🔴 **blocking** something else · 🟡 **important** · 🟢 can be deferred.

---

## A. Blocking the core design

### A-1 🔴 The real organizational structure

**Question.** What are the actual unit types, and what may nest inside what?

**Assumption in place.** `national → region → district → group → troop|pack`, groups may
also sit directly under national. See
[data-model/02-organization.md](data-model/02-organization.md#10-seed-data).

**Impact if wrong.** Only the two `INSERT` statements in the seed data change. The schema
does not — that is the point of making types and rules rows. But the trigger's behavior and
every picker depend on getting it right before data entry starts.

**Needed.** Unit type codes and names; the nesting rules; whether a unit may have two
parents; whether any level is optional.

---

### A-2 🔴 Permissions conditioned on membership status

**Question.** Should any permission require the person to be a *current* member — e.g. can a
lapsed member still see their unit's events?

**Impact.** If yes, the permission resolver must evaluate `is_current_member()`, which means
the cache must be invalidated on every membership transition, and a lapse silently removes
access.

**Recommendation.** Condition only the narrow set that genuinely requires it
(member-only event signup, member pricing) and revoke roles explicitly when a membership
ends. Do not make the resolver's general answer depend on membership state — it makes the
permission system much harder to reason about.

**See:** [data-model/03-membership.md](data-model/03-membership.md#6-membership-and-the-authorization-system)

---

### A-3 🔴 Does membership activate on payment or on approval?

**Question.** You said a person becomes a member after being accepted **and** paying. Does
the membership row exist before payment (in a `pending_payment` status), or is payment
tracked separately as debt?

**Impact.** Whether `pending_payment` is a membership status at all. Affects the exclusion
constraint's `WHERE` clause, every "list members" query, and the lapse flow.

**Recommendation.** Activate on payment (your description), keeping `pending_payment` as a
membership status so "approved but unpaid" is a visible worklist. The alternative — activate
on approval, track payment as debt — is common and equally defensible.

---

### A-4 🔴 Background checks: required, and how long valid?

**Question.** Is a background check a blocking requirement for any membership type or
position? What is its validity period? Who may record the result?

**Impact.** `membership_type.requires_background_check`,
`position.requires_background_check`, `requirement_code.default_validity_months`, and the
alerting in the integrity checks.

**Why it matters beyond the schema.** A leader with a lapsed check is a safeguarding risk,
not a data-quality issue. This is the one integrity check that should run daily and alert.

---

## B. Identity and history

### B-1 🟡 How much historical data, and in what state?

**Question.** How many records, in what format, over what years? Do the records have birth
dates? Are there old membership numbers?

**Impact.** Determines whether manual review of every match is feasible (D-004 assumes it
is). An exact legacy member number would make matching dramatically more reliable —
[person_identifier](data-model/01-identity.md#7-person_identifier) exists for it.

**Needed.** Record counts and a sample.

---

### B-2 🟡 Merge chains: allowed or flattened?

**Question.** If A is merged into B, and later B into C, does A point at B (a chain) or is
A repointed at C (flattened)?

**Current design.** Chains. `resolve_person()` follows them recursively.

**Impact.** Flattening is faster to query but rewrites pointers and makes unmerge nearly
impossible. Chains need `resolve_person()` called everywhere an external id enters the
system — a rule application code can forget.

---

### B-3 🟡 Erasure policy

**Question.** What must be redacted, what must be retained, for how long? Does the
organization have a legal obligation to keep membership records after an erasure request?

**Impact.** `redaction_log.retained_reason` is a placeholder for the judgement. The
mechanism (redact, do not delete) is designed; the policy is not.

**Needed.** Legal review. Not a technical question.

---

### B-4 🟢 Can a person hold two live accounts?

**Recommendation.** No. Enforced by the partial unique index already in the schema.

**Impact.** If yes, the index is dropped and identity attribution weakens.

---

## C. Organization

### C-1 🟡 Does authority inherit downward? (D-015)

**Question.** Does a district-level role cover the troops inside it, or must each unit be
granted separately?

**Current design.** Inherits downward via `unit_ancestors()`.

**Impact.** One resolver change, but a system-wide change in who can do what.

---

### C-2 🟡 May units be reparented retroactively?

**Question.** A troop reassigned to a different district in 2001 — is that recorded as of
2001, or as of when someone noticed in 2026?

**Impact.** Retroactive reparenting means historical unit-scoped reports change
retroactively, and `role_assignment` scope inheritance with them. This is much harder than a
forward reparent and may be worth prohibiting.

---

### C-3 🟢 Units with the same number across decades

**Question.** When a troop closes and a new troop with the same number starts ten years
later, is it the same unit or a new one?

**Impact.** An organizational judgement, not a technical one — but it must be *recorded*,
or it will be re-litigated every time someone asks about the 80s troop with that number.

---

### C-4 🟢 Does appointing someone to a position auto-create a role assignment?

**Current design.** Separate. `position.is_leadership` lets a workflow offer both.

**Impact.** Purely a workflow question; the schema is unaffected.

---

## D. Membership

### D-1 🟡 Fee per person or per household?

**Impact.** Whether `fee_obligation` targets a person or a household, and whether
`household` is load-bearing or can be dropped.

**See:** [data-model/07-finance.md](data-model/07-finance.md).

---

### D-2 🟡 One open membership, or several of different types?

**Question.** May a person be both an `honorary` and an `adult` member simultaneously?

**Current design.** Permitted — the exclusion constraint is scoped to
`membership_type_id`.

**Impact.** Dropping the type from the constraint is stricter and simpler, and makes
"one person, one membership" an enforceable invariant. Your call.

---

### D-3 🟡 Age-out timing

**Question.** A member turns 18 in March — do they age out on the birthday or at the end of
the organizational year?

**Current design.** Leaves it to `membership_type.max_age` plus a reviewed transition.

**Impact.** Affects the age-out worklist and whether a member can be in a camp after their
birthday.

---

### D-4 🟡 Child → adult transition

**Question.** Turning 18 is not enough to work with children. Does an adult membership
require a new request, a new background check, and a new acceptance?

**Impact.** Whether the transition is automatic or (recommended) a new application.
`membership_type.requires_*` supports either.

---

### D-5 🟢 Membership type vocabulary

**Current seed.** `child`, `adult`, `counselor`, `honorary`, `lifetime`.

**Question.** What are the real ones? Is `counselor` distinct from `adult`, or is it an
`adult` membership plus a position?

**Note.** If your organization uses "leader" to mean something narrower (a trained,
appointed youth leader), avoid it as a membership type name — it will collide with the
position vocabulary.

---

## E. Guardianship

### E-1 🟡 Default permissions when a guardianship is created

**Question.** What is granted automatically, and does it differ between a parent
self-registering their child and staff recording a court-ordered guardianship?

**Current proposal.** Conservative default (read + consent), `dependent.admin` for a parent
registering their own child.

**Impact.** The first is an application rule; the second is an authorization decision worth
stating explicitly.

---

### E-2 🟡 Guardianship at majority

**Question.** Confirm: review-queue, not auto-expire? (D-024)

**Impact.** Auto-expiry silently strips access. Review leaves access in place until someone
acts — the opposite failure.

---

### E-3 🟢 Guardian acting for an adult child

**Question.** Can a parent register their adult child for an event, with the child's consent?

**Recommendation.** An explicit consent-based delegation, not a guardianship — the legal
basis differs and `access_grant.is_delegated` already supports it.

---

## F. Authorization

### F-1 🔴 The permission catalog and role definitions

**Question.** Which of the proposed permissions does your organization actually need? Which
roles exist?

**Impact.** Data only — adding a permission is one row plus `permission_level` rows, and
D-007 ensures existing `.admin` grants cover it automatically.

**Needed.** Your review of
[appendix/permission-catalog.md](appendix/permission-catalog.md).

---

### F-2 🟡 Polymorphic `scope_id` vs a `grantable_item` supertable (D-011)

**A real fork.** Polymorphic: flexible, no referential integrity. Supertable: full integrity,
migration per new grantable type.

**Recommendation.** Polymorphic, given how much of this system is unspecified. But it is
worth a deliberate decision rather than a default.

---

### F-3 🟡 `valid_to` mandatory on high-authority role assignments?

**Recommendation.** Yes, enforced at the application layer (not `NOT NULL`, which would
break historical imports).

**Impact.** Turns "the volunteer who never got removed" from an invisible risk into a
60-day expiry report.

---

### F-4 🟡 Should `person.admin` subsume `person.merge` and `person.redact`?

**Recommendation.** No. Both are irreversible in practice with privacy consequences far
beyond editing a record. Grant them explicitly.

---

### F-5 🟢 Cache vs materialized `effective_permission` table

**Recommendation.** Start with cache-only. Materializing is a denormalization requiring
transactional maintenance, and a silent refresh failure is an access bug nothing detects.

**Impact.** Performance only; revisit if measurement demands it.

---

### F-6 🟢 Retention policy for `access_log`

Legal input required. Recommend monthly partitioning from the start, with archival to cold
storage and **never deletion**.

---

## G. Not yet designed

Each of these is referenced by the schema and has hooks left for it. None blocks the current
design.

| Area | Hooks already in place | Notes |
|------|------------------------|-------|
| **Events** | `access_grant.scope_type = 'event'`; `grant_scope_type` has a row; `event.*` permissions sketched | The per-item permission case you named. Needs: event entity, registration/participation, capacity, eligibility gates, attendance. Note that **participation** and **capability** are different — see D-006. |
| **Fees and payments** | [data-model/07-finance.md](data-model/07-finance.md) is provisional | Twelve open questions in that document. |
| **Documents** | `access_grant.scope_type = 'document'`; `membership_request_requirement.evidence_reference` is a free-text pointer | Needs: storage, versions, retention, consent-driven access. |
| **Consents** | `dependent.consent.*` permissions exist; `requirement_code` exists | Needs: template, per-activity consent, expiry, revocation, who may consent. |
| **Health records** | `dependent.medical.*` permissions exist | **Highest-sensitivity data in the system.** Separate retention, separate access, likely separate storage. Requires its own design and legal review before implementation. |
| **Communication** | `message.*` permissions sketched | Needs: audiences, channels, templates, opt-out, and a rule against contacting minors directly. |
| **Reporting** | `report.*` permissions sketched | The ten historical queries in [domain/05](domain/05-membership-lifecycle.md#8-queries-this-design-must-support) are the starting set. Query 10 (members per year since 1985) is the acceptance test. |
| **API and UI** | — | Not started. The resolver's `p_at` parameter exists partly for this. |
| **Notifications** | — | Expiring checks, expiring roles, ageing-out members, unpaid fees. |
| **Payment gateway** | — | Only if the organization collects rather than records payments. Adds webhooks, reconciliation, idempotency. |
| **Multi-language** | — | Unit names, membership type names, and permission display names are all in the database. Whether they need translation columns is unanswered. |

---

## H. Assumption index

Every *Assumption:* in the documentation, so they can be reviewed as a group.

| # | Assumption | Where |
|---|-----------|-------|
| 1 | PostgreSQL 14+ with `btree_gist` | [data-model/00](data-model/00-conventions.md#1-target-platform) |
| 2 | No automatic merging (D-004) | [domain/03](domain/03-identity-and-legacy.md#4-match-signals) |
| 3 | Minors need guardian consent for an account | [domain/02](domain/02-actors.md#2-who-registers-and-why) |
| 4 | Parent self-registering a child gets `dependent.admin` | [data-model/04](data-model/04-relationships.md#2-guardianship_permission) |
| 5 | Authority inherits downward (D-015) | [domain/04](domain/04-organization-structure.md#6-units-and-permissions) |
| 6 | Membership activates on payment (A-3) | [domain/05](domain/05-membership-lifecycle.md#1-the-flow-you-described) |
| 7 | Fee is per person, yearly | [domain/05](domain/05-membership-lifecycle.md#6-renewal-and-the-yearly-fee) |
| 8 | Renewal is Shape A (new row) | [domain/05](domain/05-membership-lifecycle.md#6-renewal-and-the-yearly-fee) |
| 9 | Guardianship reviewed at majority, not auto-expired (D-024) | [data-model/04](data-model/04-relationships.md#1-guardianship) |
| 10 | Display name uses `preferred_name` if set | [data-model/01](data-model/01-identity.md#3-person_name--name-history) |
| 11 | Merge chains allowed (B-2) | [data-model/01](data-model/01-identity.md#9-views) |
| 12 | Only confirmed payments count toward a balance | [data-model/07](data-model/07-finance.md#3-keeping-membershipoutstanding_balance-honest) |
| 13 | Placeholder unit types and nesting rules (A-1) | [data-model/02](data-model/02-organization.md#10-seed-data) |
| 14 | Placeholder membership types and age limits (D-5) | [data-model/03](data-model/03-membership.md#8-seed-data) |
| 15 | `person.gender` is needed for reporting | [data-model/01](data-model/01-identity.md#2-person) |
| 16 | Imported rosters end at organizational year end (D-028) | [data-model/06](data-model/06-audit-and-import.md#3-import-pipeline) |
| 17 | All business tables are audited | [data-model/06](data-model/06-audit-and-import.md#6-open-issues) |
| 18 | Currency is EUR | [data-model/07](data-model/07-finance.md#2-minimal-provisional-shape) |
| 19 | `access_log` is not human-annotatable | [data-model/05](data-model/05-authorization.md#7-access_log) |
| 20 | Each permission has an `admin` sibling (your instruction, D-007) | throughout |

---

## How to answer

Pick any subset — they are independent. The most valuable to resolve first, if you want the
core schema to be final:

1. **A-1** organizational structure
2. **A-3** activation on payment vs. approval
3. **A-4** background checks
4. **F-1** permission catalog
5. **D-2** one membership or several
6. **C-1** authority inheritance

Everything else can be answered as we go, and the schema is designed so that most answers
change data rather than structure.
