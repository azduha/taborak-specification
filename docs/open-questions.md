# Open Questions

Everything still unresolved, each with its **schema impact** — what changes once you answer.
Ordered roughly by how much they block.

Marked: 🔴 **blocking** something else · 🟡 **important** · 🟢 can be deferred.

**Resolved items are not deleted.** They are moved to the bottom of this file with a link to
the decision that settled them, so the reasoning survives — see
[§ R. Resolved](#r-resolved--moved-to-the-decision-log).

---

## A. Blocking the core design

### A-1 (remainder) 🔴 The real unit type vocabulary

**Question.** One root and arbitrary nesting are settled
([D-035](decisions/decision-log.md#d-035--one-root-unit-all-sub-units-nest-arbitrarily-beneath-it)).
What is **not** settled is the *vocabulary*: which unit types exist, what they are called, and
which nesting constraints the organization actually wants stated as rules.

**Current state.** [data-model/02 §10](data-model/02-organization.md#10-seed-data) still
seeds the retired ladder (`national`, `region`, `district`, `group`, `troop`, `pack`) as a
placeholder. It does not match the model any more.

**Impact.** Only `INSERT` statements change; the schema does not. But nesting is now
**permissive by default** — a type with no rules is unconstrained — so the rules you do state
carry more weight than before. Each one you add is a constraint you have chosen.

**Needed.** Type codes and names; which types are leaves; which may sit directly under the
root. Expect this to be a short list.

**See:** [domain/04 §1–2](domain/04-organization-structure.md#1-one-root-arbitrary-sub-units)

---

### A-4 (remainder) 🟢 The organizational calendar

**Answered.** The fee expires on **1 January**
([D-047](decisions/decision-log.md#d-047--the-fee-expires-on-1-january)) and the renewal
window is **60 days** ([D-048](decisions/decision-log.md#d-048--the-renewal-window-is-60-days-and-is-a-configuration-parameter)).

**What is left is not a question but a discipline.** Both values live in
`membership_type` as columns — `expiry_month`, `expiry_day`, `renewal_grace_days` — so either
can be moved by an `UPDATE`. The one way to lose that property is a scheduled job or a front
end that contains the literal `60` or `1`. Worth one line in code review: *do these values
come from the row?*

**See:** [data-model/03 §1](data-model/03-membership.md#1-membership_type--one-row-kept-as-a-table),
[domain/05 §6](domain/05-membership-lifecycle.md#6-renewal-and-the-yearly-fee)

---

## B. Identity and history

### B-1 🟡 How much historical data, and in what state?

**Question.** How many records, in what format, over what years? Do the records have birth
dates? Are there old membership numbers?

**Impact.** Determines whether manual review of every match is feasible (D-004 assumes it
is). An exact legacy member number would make matching dramatically more reliable —
[person_identifier](data-model/01-identity.md#7-person_identifier) exists for it.

**Needed.** Record counts and a sample.

**Note.** This is now a larger question than it was, because
[D-041](decisions/decision-log.md#d-041--belonging-to-a-sub-unit-is-a-participation-record-not-a-membership)
split belonging into membership and participation. If the old records recorded "which troop"
but not "whether paid up", the import has to decide which of the two each historical row
becomes — and a 1998 roster probably encodes participation, not a paid membership.

---

### B-2 🟡 Merge chains: allowed or flattened?

**Question.** If A is merged into B, and later B into C, does A point at B (a chain) or is
A repointed at C (flattened)?

**Current design.** Chains. `resolve_person()` follows them recursively.

**Impact.** Flattening is faster to query but rewrites pointers and makes unmerge nearly
impossible. Chains need `resolve_person()` called everywhere an external id enters the
system — a rule application code can forget.

---

### B-3 🟡 Erasure: the policy, not the mechanism

**Question.** What must be redacted, what must be retained, for how long? Does the
organization have a legal obligation to keep membership records after an erasure request?

**Resolved already.** The *shape* is settled: **redact the person, keep the financial and
membership skeleton** — the `person` row is anonymised in place and the `membership`,
`fee_obligation` and `payment` rows survive intact, because the organization's own accounting
and "was this person a member on that date" questions outlive the person's participation.

**Still open.** The retention periods and the legal basis. `redaction_log.retained_reason` is
a placeholder for that judgement.

**Needed.** Legal review. Not a technical question.

**See:** [data-model/06 §4](data-model/06-audit-and-import.md#4-redaction-log)

---

### B-4 🟢 Can a person hold two live accounts?

**Recommendation.** No. Enforced by the partial unique index already in the schema.

**Impact.** If yes, the index is dropped and identity attribution weakens.

---

## C. Organization

### C-1 🟢 May the root *see* what happens in its sub-units?

**Answered: no — `scope_exposure` is the only crossing, and no reporting channel is built**
([D-049](decisions/decision-log.md#d-049--the-root-may-not-read-into-its-sub-units-scope_exposure-is-the-only-crossing)).

**What was not obvious until it was answered.** The question existed on the assumption that
the root needed a way *around* the no-inheritance rule in order to report nationally. It
does not, because the root **owns the membership registry and the fees** — so "how many
members in 2019?", "who is currently a member?" and "what fees are outstanding?" are all
answered from the root's own tables, with no exposure at all. Only the sub-units' own
material — their events, their rosters, their local leadership — requires one.

The consequence that will be misread as a bug: `registrar` holds `unit_participation.view` at
organization scope and **cannot** read a pack roster. Scope is an exact match; it reads the
root participation rows, which mirror membership
([D-041](decisions/decision-log.md#d-041--belonging-to-a-sub-unit-is-a-participation-record-not-a-membership)).
See [domain/06 §2.4](domain/06-authorization-model.md#24-the-organization-wide-role-problem-and-why-it-mostly-dissolved).

---

### C-3 🟢 Units with the same number across decades

**Question.** When a troop closes and a new troop with the same number starts ten years
later, is it the same unit or a new one?

**Impact.** An organizational judgement, not a technical one — but it must be *recorded*,
or it will be re-litigated every time someone asks about the 80s troop with that number.

**See:** [domain/04 §3](domain/04-organization-structure.md#3-unit-names-and-renumbering--the-history-problem)

---

### C-4 🟢 Does appointing someone to a position auto-create a role assignment?

**Current design.** Separate. `position.is_leadership` lets a workflow offer both.

**Impact.** Purely a workflow question; the schema is unaffected.

---

## D. Membership

### D-6 — closed, by making the question the organization's to answer

**Answered: the mechanism** ([D-051](decisions/decision-log.md#d-051--the-membership-gate-is-waived-by-a-permission-not-only-by-a-role-flag)).
The membership gate is waived by a person-level permission, `system.gate_exempt`, in addition
to the role-level flag. `system_admin` holds it — without it the 1 January sweep locks the
administrator out of the system on the day it needs repair.

**And "which other roles carry it" is no longer a question for this document.** Roles are
runtime data: the organization creates them, edits what they grant, assigns them, and retires
them ([data-model/05 §3](data-model/05-authorization.md#3-role-and-role_permission)). Marking
a role as carrying `system.gate_exempt` is therefore a configuration act the organization
performs, not a fact the specification can state. The seed set in
[appendix/permission-catalog.md §11](appendix/permission-catalog.md#11-roles--proposed-seed-set)
shows the shape; it is a starting point to edit, and it explicitly declines to answer this.

**What is *not* delegatable, and is therefore all this document has to get right:** that
`system.gate_exempt` is a `system`-namespace permission, so it can only ever arrive through a
role and never through an item grant. That structural guarantee — an `access_grant` cannot
lift the membership gate — is the part a configuration screen must not be able to weaken.

**Tracked here only for visibility:** check 7b in
[data-model/05 §11](data-model/05-authorization.md#11-integrity-checks) reports who currently
holds the exemption, so the organization can see the list it has configured.

---

### D-7 🟢 What does the root-unit participation row do at renewal?

**Answered: it is extended, not closed and reopened**
([D-050](decisions/decision-log.md#d-050--a-renewal-inside-the-window-extends-the-existing-root-participation-row)).

The yearly sweep moves the root row's `valid_to` forward to the expiry date rather than
closing it, and a renewal inside the window stretches that one row over the new period. The
join between the two is **person and date** (`new_m.valid_from = up.valid_to`), not a
membership FK — the participation table has none, deliberately.

**The accepted cost, recorded rather than hidden.** This erases the visual evidence of the
lapse: a person who lapsed and renewed looks, in `unit_participation`, exactly like a person
who never lapsed. Accepted because `membership` remains the authority on payment and the
lapse is fully visible there, while the participation table answers a *roster* question — and
for "who was in this pack when" a child who was present across the period has one answer, not
two.

**See:** [data-model/03 §5.1](data-model/03-membership.md#51-a-participation-row-on-the-root-unit)

---

### D-8 🟢 Should `unit_participation` reference the membership?

**Question.** A nullable `membership_id` on `unit_participation` would give referential
integrity between "paid up" and "takes part", at the cost of being unenforceable for imported
historical rows, where no membership exists to point at.

**Impact.** Integrity vs. import coverage. The current design chose person-based linkage for
exactly that reason.

**See:** [data-model/03 §5](data-model/03-membership.md#5-unit_participation)

---

### D-9 🟢 Is `household` load-bearing at all?

**Question.** [D-037](decisions/decision-log.md#d-037--exactly-one-membership-type-the-fee-is-flat-and-per-person)
made the fee **flat and per person**, which was the last thing household grouping was doing
for finance. What remains is "same address" as a matching signal for the legacy import, and
as a display convenience.

**Current state of the schema.** `fee_obligation.household_id` still exists but nothing sets
it; it is kept only so that a per-family discount could be added as a constraint change
([data-model/07 §2](data-model/07-finance.md#2-minimal-provisional-shape)). A firm "no family
discounts" answer lets us drop the column, its CHECK arm, its index, and — plausibly —
`household` itself.

**Impact.** If it is only a matching signal, it could become a derived view rather than a
maintained table. If the organization ever wants family communication or family discounts,
it is load-bearing again.

**See:** [data-model/04 §3](data-model/04-relationships.md#3-household-and-household_member)

---

## E. Guardianship

### E-2 🟡 Guardianship at majority

**Question.** Confirm: review-queue, not auto-expire? (D-024)

**Impact.** Auto-expiry silently strips access. Review leaves access in place until someone
acts — the opposite failure.

---

### E-3 🟢 Guardian acting for an adult child

**Question.** Can a parent register their adult child for an event, with the child's consent?

**Recommendation.** An explicit consent-based delegation, not a guardianship — the legal
basis differs and `access_grant.is_delegated` already supports it.

**Note.** Now that grants can target **audiences**
([D-042](decisions/decision-log.md#d-042--grants-may-target-audiences-not-only-individuals)),
the *event-wide* version of this question — "register everyone in this group" — is answered
without touching guardianship at all. What remains is the individual case.

---

### E-4 🟢 Guardianship lifetime vs. the membership gate

**Question.** Guardianship is exempt from the membership gate
([D-039](decisions/decision-log.md#d-039--member-permissions-require-a-current-paid-membership)),
so a lapsed parent keeps full access to their child's records. Confirm that is intended
rather than a side effect: it means an unpaid parent and a paid one are indistinguishable
inside the `dependent.*` namespace.

**Impact.** None structurally. It is worth stating explicitly because it is the one place the
gate is deliberately absent, and "why can this person still see that?" should have a written
answer.

---

## F. Authorization

### F-1 🔴 The permission catalog and role definitions

**Question.** Which of the proposed permissions does your organization actually need? Which
roles exist?

**Impact.** Data only — adding a permission is one row plus `permission_level` rows, and
[D-007](decisions/decision-log.md#d-007--every-resource-has-an-admin-level-that-subsumes-narrower-ones)
ensures existing `.admin` grants cover it automatically.

**Needed.** Your review of [appendix/permission-catalog.md](appendix/permission-catalog.md) —
minus the two namespaces already struck from it (background checks, and the retired
requirement machinery).

---

### F-3 🟡 `valid_to` mandatory on high-authority role assignments?

**Recommendation.** Yes, enforced at the application layer (not `NOT NULL`, which would
break historical imports).

**Impact.** Turns "the volunteer who never got removed" from an invisible risk into a
60-day expiry report. This matters more now than it did: with the membership gate in place, an
open-ended role held by a lapsed member is exactly the "dormant authority"
case [data-model/05 §6](data-model/05-authorization.md#6-access_grant--the-per-item-layer)
warns about.

---

### F-4 🟡 Should `person.admin` subsume `person.merge` and `person.redact`?

**Recommendation.** No. Both are irreversible in practice with privacy consequences far
beyond editing a record. Grant them explicitly.

---

### F-5 🟢 Which built-in audiences are needed?

**Question.** `everyone` and `all_members` are seeded, plus parameterised
`unit:<id>:participants` and `unit:<id>:leaders`
([D-042](decisions/decision-log.md#d-042--grants-may-target-audiences-not-only-individuals)).
Which others are real — "the guardians of this child", "the leaders of the parent unit",
"adults only", "everyone in this section *and everything under it*"?

**Impact.** Each is one `audience` row plus one branch in `person_in_audience()`. Cheap to
add, cheap to remove. But the parameterised ones raise a second question: are
`unit:42:participants` rows **seeded per instance** on demand, or created when first granted?
The first is a migration that must be re-run as units are created; the second needs a
create-on-demand path that bypasses the usual admin permission.

---

### F-6 🟢 The permission cache lifetime under the membership gate

**Question.** [D-039](decisions/decision-log.md#d-039--member-permissions-require-a-current-paid-membership)
means the resolver's answer changes when a membership lapses — including at the yearly sweep,
which touches everyone at once. What TTL is acceptable?

**Impact.** The shorter the TTL, the smaller the window in which a lapsed member still has
access, and the more load on the resolver. The sweep must invalidate by person, not by scope
([data-model/05 §10](data-model/05-authorization.md#10-the-resolver-in-sql)), and that is
settled — this is only about the steady-state TTL.

---

### F-7 🟢 Cache vs materialized `effective_permission` table

**Recommendation.** Start with cache-only. Materializing is a denormalization requiring
transactional maintenance, and a silent refresh failure is an access bug nothing detects.

**Impact.** Performance only; revisit if measurement demands it. The membership gate makes
materializing harder, not easier — every membership transition would have to rewrite rows.

---

### F-8 🟢 Retention policy for `access_log`

Legal input required. Recommend monthly partitioning from the start, with archival to cold
storage and **never deletion**.

---

### F-9 🟢 Should `membership_type` stay a table with one row?

**Question.** [D-037](decisions/decision-log.md#d-037--exactly-one-membership-type-the-fee-is-flat-and-per-person)
kept `membership_type` as a table with a single seeded `member` row, on the principle that
vocabularies are rows and not enums — at the cost of an FK that always holds one value.

**Impact.** A deliberate trade, not an oversight. Worth confirming it is the trade you want,
since it is the one place the design pays a structural cost for a hypothetical future.

**See:** [data-model/03 §1](data-model/03-membership.md#1-membership_type--one-row-kept-as-a-table)

---

## G. Not yet designed

Each of these is referenced by the schema and has hooks left for it. None blocks the current
design.

| Area | Hooks already in place | Notes |
|------|------------------------|-------|
| **Events** | `access_grant.scope_type = 'event'`; `grant_scope_type` has a row; `event.*` permissions sketched; **audiences** now exist to express "exposed to everyone / to this group" | The per-item permission case you named. Needs: event entity, registration/participation, capacity, eligibility gates, attendance. Note that **participation** and **capability** are different — see D-006. |
| **Fees and payments** | [data-model/07-finance.md](data-model/07-finance.md) is provisional | Ten open questions remain in that document (down from twelve — activation-on-payment and person-vs-household are settled). |
| **Documents** | `access_grant.scope_type = 'document'`; the evidence-reference hook belonged to the removed requirement tables | Needs: storage, versions, retention, consent-driven access. |
| **Consents** | `dependent.consent.*` permissions exist | Needs: template, per-activity consent, expiry, revocation, who may consent. No longer connected to a membership requirement ([D-044](decisions/decision-log.md#d-044--nothing-gates-a-membership-request-except-identity-and-payment)). |
| **Health records** | `dependent.medical.*` permissions exist | **Highest-sensitivity data in the system.** Separate retention, separate access, likely separate storage. Requires its own design and legal review before implementation. |
| **Communication** | `message.*` permissions sketched | Needs: channels, templates, opt-out, and a rule against contacting minors directly. Audiences are a natural fit for the recipient side, but "who may *address* an audience" is a separate permission question. |
| **Reporting** | `report.*` permissions sketched | The historical queries in [domain/05](domain/05-membership-lifecycle.md#8-since-1985--the-ten-queries-this-design-must-answer) are the starting set. Query 10 (members per year since 1985) is the acceptance test. |
| **API and UI** | — | Not started. The resolver's `p_at` parameter exists partly for this. |
| **Notifications** | — | Expiring roles, members inside the renewal window, unpaid fees. Note the renewal window makes this *dated* rather than status-driven — a nightly job over `in_renewal_window()`. |
| **Payment gateway** | — | Only if the organization collects rather than records payments. Adds webhooks, reconciliation, idempotency. |
| **Multi-language** | — | Unit names and permission display names are all in the database. Whether they need translation columns is unanswered. |

---

## R. Resolved — moved to the decision log

Kept here so a reader of this file knows the question was asked and where the answer lives,
rather than finding it silently deleted.

| Was | Question | Settled by | In one line |
|-----|----------|-----------|-------------|
| A-1 | The organizational structure | [D-035](decisions/decision-log.md#d-035--one-root-unit-all-sub-units-nest-arbitrarily-beneath-it) | One root; all sub-units nest arbitrarily beneath it. *(The type vocabulary is still open — see A-1 remainder.)* |
| A-2 | Permissions conditioned on membership status | [D-039](decisions/decision-log.md#d-039--member-permissions-require-a-current-paid-membership) | Yes, enforced by the resolver, with guardianship and ownership carved out. |
| A-3 | Activate on payment or on approval? | [D-040](decisions/decision-log.md#d-040--the-fee-expires-yearly-a-date-tracked-renewal-window-replaces-a-grace-status) | On payment; the fee expires yearly and a dated renewal window replaces a grace status. |
| A-4 | Background checks | [D-043](decisions/decision-log.md#d-043--no-background-checks-are-recorded-in-this-system) | None are recorded in this system. |
| A-4 | The expiry date | [D-047](decisions/decision-log.md#d-047--the-fee-expires-on-1-january) | 1 January; the organizational year runs with the calendar. |
| A-4 | The renewal window length | [D-048](decisions/decision-log.md#d-048--the-renewal-window-is-60-days-and-is-a-configuration-parameter) | 60 days, stored as a parameter rather than compiled in. |
| C-1 | May the root read into its sub-units? | [D-049](decisions/decision-log.md#d-049--the-root-may-not-read-into-its-sub-units-scope_exposure-is-the-only-crossing) | No. `scope_exposure` is the only crossing; no reporting channel is built. |
| D-6 | How may the membership gate be waived? | [D-051](decisions/decision-log.md#d-051--the-membership-gate-is-waived-by-a-permission-not-only-by-a-role-flag) | A person-level `system.gate_exempt` permission, in addition to the role flag. |
| D-7 | The root participation row at renewal | [D-050](decisions/decision-log.md#d-050--a-renewal-inside-the-window-extends-the-existing-root-participation-row) | Extended across the renewed period; one row, no gap. |
| B-3 (part) | Erasure: what shape? | your answer, round 5 | Redact the person, keep the financial and membership skeleton. *(The retention policy is still open — see B-3.)* |
| C-1 (largely) | Organization-wide operational roles without downward inheritance | [D-035](decisions/decision-log.md#d-035--one-root-unit-all-sub-units-nest-arbitrarily-beneath-it) | The problem dissolves: the root owns the registry and the fees. What remains is a reporting question — see C-1. |
| C-2 | May units be reparented retroactively? | [D-036](decisions/decision-log.md#d-036--units-cannot-be-reparented-a-unit-that-moves-is-a-new-unit) | Not at all — a unit that moves is a new unit. |
| D-1 | Fee per person or per household? | [D-037](decisions/decision-log.md#d-037--exactly-one-membership-type-the-fee-is-flat-and-per-person) | Per person, flat, yearly. |
| D-2 | One open membership, or several of different types? | [D-037](decisions/decision-log.md#d-037--exactly-one-membership-type-the-fee-is-flat-and-per-person), [D-041](decisions/decision-log.md#d-041--belonging-to-a-sub-unit-is-a-participation-record-not-a-membership) | One type, so one open membership, enforced person-wide. |
| D-3 | Age-out timing | [D-038](decisions/decision-log.md#d-038--membership-is-ageless) | Retired — there is no age-out. |
| D-4 | Child → adult transition | [D-038](decisions/decision-log.md#d-038--membership-is-ageless) | Retired — there are no membership categories to transition between. |
| D-5 | Membership type vocabulary | [D-037](decisions/decision-log.md#d-037--exactly-one-membership-type-the-fee-is-flat-and-per-person) | One type, `member`; counselor is a position, not a type. |
| E-1 | Default permissions when a guardianship is created | [D-046](decisions/decision-log.md#d-046--guardianship-defaults-depend-on-how-the-guardianship-was-created) | `dependent.admin` for a self-registered child; chosen at creation when recorded manually. |
| F-2 | Polymorphic `scope_id` vs a `grantable_item` supertable | your answer, round 6 | Polymorphic — `scope_type` plus `scope_id`, as currently designed. |
| — | The bulk scope-exposure tool | [D-045](decisions/decision-log.md#d-045--the-bulk-scope-exposure-tool-is-removed) | Removed once audiences existed to cover the case it was for. |
| — | What a membership request must contain | [D-044](decisions/decision-log.md#d-044--nothing-gates-a-membership-request-except-identity-and-payment) | Identity and the fee. The whole requirement mechanism is gone. |
| — | Whether grants may target groups | [D-042](decisions/decision-log.md#d-042--grants-may-target-audiences-not-only-individuals) | Yes — built-in rule-evaluated audiences plus admin-managed named groups. |

---

## H. Assumption index

Every *Assumption:* in the documentation, so they can be reviewed as a group. Once you confirm
one, it should be promoted to a numbered decision and struck from [§ R](#r-resolved--moved-to-the-decision-log).

Rows marked **†** are now backed by a decision rather than a bare assumption — kept here
because the docs still cite them and because the decision is worth seeing in this list.

| # | Assumption | Where |
|---|-----------|-------|
| 1 | PostgreSQL 14+ with `btree_gist` | [data-model/00](data-model/00-conventions.md#1-target-platform) |
| 2 | No automatic merging (D-004) † | [domain/03](domain/03-identity-and-legacy.md#4-match-signals) |
| 3 | Minors need guardian consent for an account | [domain/02](domain/02-actors.md#2-who-registers-and-why) |
| 4 | A self-registered child's parent gets `dependent.admin` (D-046) † | [data-model/04](data-model/04-relationships.md#2-guardianship_permission) |
| 5 | Locality orders allows only; deny is absolute (D-032) † | [domain/06](domain/06-authorization-model.md#6-the-resolver) |
| 6 | Membership activates on payment (D-040) † | [domain/05](domain/05-membership-lifecycle.md#1-the-flow-you-described) |
| 7 | The fee is per person and yearly (D-037) † | [domain/05](domain/05-membership-lifecycle.md#6-renewal-and-the-yearly-fee) |
| 8 | Renewal opens a new row, not an extended `valid_to` (D-016) † | [domain/05](domain/05-membership-lifecycle.md#6-renewal-and-the-yearly-fee) |
| 9 | Guardianship reviewed at majority, not auto-expired (D-024) † | [data-model/04](data-model/04-relationships.md#1-guardianship) |
| 10 | Display name uses `preferred_name` if set | [data-model/01](data-model/01-identity.md#3-person_name--name-history) |
| 11 | Merge chains allowed (B-2) | [data-model/01](data-model/01-identity.md#9-views) |
| 12 | Only confirmed payments count toward a balance | [data-model/07](data-model/07-finance.md#3-keeping-membershipoutstanding_balance-honest) |
| 13 | Placeholder unit types and nesting rules (A-1) | [data-model/02](data-model/02-organization.md#10-seed-data) |
| 14 | `membership_type` is seeded with exactly one row (D-037) † | [data-model/03](data-model/03-membership.md#8-seed-data) |
| 15 | `person.gender` is needed for reporting | [data-model/01](data-model/01-identity.md#2-person) |
| 16 | Imported rosters end at the organizational year end (D-028) † | [data-model/06](data-model/06-audit-and-import.md#3-import-pipeline) |
| 17 | All business tables are audited | [data-model/06](data-model/06-audit-and-import.md#6-open-issues) |
| 18 | Currency is EUR | [data-model/07](data-model/07-finance.md#2-minimal-provisional-shape) |
| 19 | `access_log` is not human-annotatable | [data-model/05](data-model/05-authorization.md#9-access_log) |
| 20 | Each permission has an `admin` sibling (D-007) † | throughout |
| 21 | No downward inheritance; exposures are written by the unit (D-031) † | [domain/06](domain/06-authorization-model.md#2-scope-authority--no-downward-inheritance) |
| 22 | The person record holds no deceased flag (D-034) † | [data-model/01](data-model/01-identity.md#2-person) |
| 23 | Positions are multi-holder unless `max_holders` says otherwise (D-033) † | [domain/04](domain/04-organization-structure.md#4-positions) |
| 24 | Membership is ageless — no category, no `min_age`, no `max_age` (D-038) † | [data-model/03](data-model/03-membership.md#1-membership_type--one-row-kept-as-a-table) |
| 25 | A grant targets a person **or** an audience, never both (D-042) † | [data-model/05](data-model/05-authorization.md#6-access_grant--the-per-item-layer) |
| 26 | Built-in audiences are rules evaluated by the resolver, not stored lists (D-042) † | [data-model/05](data-model/05-authorization.md#8-audience--grants-that-target-a-set-of-people) |
| 27 | Belonging to a sub-unit is participation, not membership (D-041) † | [data-model/03](data-model/03-membership.md#5-unit_participation) |
| 28 | Roles require a current membership unless `requires_membership = false` (D-039) † | [data-model/05](data-model/05-authorization.md#3-role-and-role_permission) |
| 29 | There is no bulk exposure tool and no `bulk:` reason marker (D-045) † | [data-model/05](data-model/05-authorization.md#5-scope_exposure--how-a-unit-delegates-upward) |
| 30 | No background checks are recorded anywhere (D-043) † | throughout |
| 31 | `access_grant.scope_id` is polymorphic, with no foreign key (F-2) † | [data-model/05](data-model/05-authorization.md#6-access_grant--the-per-item-layer) |
| 32 | The organizational calendar is 1 January plus a 60-day window (D-047, D-048) † | [data-model/03](data-model/03-membership.md#1-membership_type--one-row-kept-as-a-table) |
| 33 | The root reads into a sub-unit only through `scope_exposure` (D-049) † | [domain/06](domain/06-authorization-model.md#24-the-organization-wide-role-problem-and-why-it-mostly-dissolved) |
| 34 | A renewal extends the root participation row rather than closing it (D-050) † | [data-model/03](data-model/03-membership.md#51-a-participation-row-on-the-root-unit) |
| 35 | The membership gate is waived by a person-level permission, not only a role flag (D-051) † | [data-model/05](data-model/05-authorization.md#3-role-and-role_permission) |

---

## How to answer

Pick any subset — they are independent. The ones that most change the shape of the system, if
you want the core to stop moving:

1. **A-1 remainder** — the unit type vocabulary and nesting rules
2. **F-1** — the permission catalog, and the roles
3. **B-1** — how much legacy data, and in what shape
4. **D-6 remainder** — who holds `system.gate_exempt`, and the `Req.` column per role

Everything else can be answered as we go. The schema is built so that most answers change
data rather than structure — the ones above are the exceptions, which is why they are first.

**Answered in this round:** the organizational calendar (A-4 — 1 January, 60 days);
the root's read access into sub-units (C-1 — `scope_exposure` only); the membership
gate's waiver (D-6 — a person-level permission, in addition to the role flag); and the
root participation row at renewal (D-7 — extended). All four are in
[§ R](#r-resolved--moved-to-the-decision-log) with links to the decisions that settled them.
