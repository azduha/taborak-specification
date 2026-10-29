# Decision Log — The founding decisions (D-016 … D-030)

> Renewal and requests, guardianship, the two audit trails, the legacy import, and finance as a provisional placeholder.

[The founding decisions (D-001 … D-015) ←](round-01a.md) | [All decisions](index.md) | [Refinement rounds 2 and 3 (D-031 … D-046) →](round-02-03.md)

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
([D-057](round-04.md#d-057--household-is-removed)), so there is no household membership left to grant
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

**Status:** ⚠ **partly superseded** by [D-040](round-02-03.md#d-040--the-fee-expires-yearly-a-date-tracked-renewal-window-replaces-a-grace-status)
and [D-038](round-02-03.md#d-038--membership-is-ageless)

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
| "Grace periods absorb late payments" | The grace *status* is gone. There is a **renewal window** — dates, not a state ([D-040](round-02-03.md#d-040--the-fee-expires-yearly-a-date-tracked-renewal-window-replaces-a-grace-status)). |
| "Age-out is driven by `membership_type.max_age`" | There is no `max_age` and no age-out. Membership is ageless ([D-038](round-02-03.md#d-038--membership-is-ageless)). |

**The expiry is the one automatic transition.** D-040 resolves the tension the original
"why" names, and resolves it by removing the *decision* rather than the *automation*: the
fee covers a fixed period, the period ends on a date everyone already knows, and nobody
chooses anything. The late-bank-transfer case the original wording was protecting is
absorbed by the window's backdating rule instead. The reversal is recorded in full at
[../data-model/07-finance.md §4](../data-model/07-finance.md#4-how-this-connects-to-membership),
including the one case the window cannot absorb.

---

## D-024 — Guardianship does not auto-expire at majority ⚠ **REVERSED**

**Status:** ~~assumption~~ **reversed by [D-069](round-05.md#d-069--guardianship-ends-when-a-person-ends-it-the-system-takes-no-position-on-majority)**
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
