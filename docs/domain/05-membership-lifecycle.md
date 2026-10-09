# Membership Lifecycle

Register → request → accept → pay → member. Plus the parts that are usually forgotten:
gaps, returns, multiple periods, and renewal.

---

## 1. The flow you described

> *"The people can register on their own to get access to the system, however they become
> member only if they request a membership, they get accepted and pay a yearly fee."*

Four distinct stages, each a separate record, because each can independently fail,
stall, or be reversed:

| Stage | Record | Can be reversed? | What it means |
|-------|--------|------------------|---------------|
| 1. Register | `person` + `account` | account can be closed | "This person can log in." |
| 2. Request | `membership_request` | yes — reject/withdraw | "This person applied." |
| 3. Accept | `membership_request.status = 'approved'` | yes — revoke before activation | "The organization said yes." |
| 4. Pay | `fee_obligation` + `payment` | refund | "The obligation is met." |
| 5. Activate | `membership` opened | yes — lapse/terminate | "This person is a member." |

**Why stage 5 is separate from stage 3.** Approval and activation are distinct because
payment sits between them. A person can be approved and never pay; the organization needs
to see that state ("approved, awaiting payment") to chase it, and it must not appear as a
member.

*Assumption:* membership activates on payment. Some organizations activate on approval and
track payment separately as debt. If yours does, `membership` opens at stage 3 and
`fee_obligation` becomes the tracking mechanism instead of a gate. Confirm via
[../open-questions.md](../open-questions.md).

---

## 2. Membership request

```
membership_request(
    id,
    person_id,
    requested_membership_type_id,    -- child | adult | counselor | ...
    requested_unit_id,               -- nullable; may be assigned by the organization
    status,                          -- draft | submitted | under_review | approved
                                     -- | rejected | withdrawn | expired
    submitted_at,
    reviewed_by, reviewed_at,
    rejection_reason_code, rejection_note,
    membership_id                    -- set when approval produces a membership
)
```

### Why a request is not a membership with a status

Tempting to collapse them, but:

- A request can be **rejected**, producing no membership at all. A `membership` row with
  status `rejected` would pollute every "list members" query forever.
- A person may submit **several requests over time** (rejected in 2024, approved in 2025).
  One table for both would need a request-version column and every query would need to
  filter it.
- Requests carry **review data** (who reviewed, why, what was checked) that has no meaning
  on a membership.
- Requests have **different permissions**: submitting is self-service; reviewing is a
  staff capability.

### Request-specific requirements

```
membership_request_requirement(
    id, request_id, requirement_code,
    status,                          -- pending | satisfied | waived | failed
    satisfied_by, satisfied_at,
    evidence_reference
)
```

Real applications need: guardian consent (for minors), background check (for adults
working with children), references, medical form, previous-unit transfer confirmation.
Modeling these as rows rather than columns means the requirement set can change per
membership type and per year without a migration.

Critically: **a background check for adults is not a nice-to-have.** In a youth
organization it is frequently a legal prerequisite. Model it as a blocking requirement
with an expiry date, so that a leader whose check has lapsed is detectable — see §7.

---

## 3. Membership

```
membership(
    id,
    person_id,
    membership_type_id,
    status,                          -- pending_payment | active | lapsed
                                     -- | terminated | completed | suspended
    valid_from, valid_to,            -- the period. valid_to null = open/current
    joined_via_request_id,
    termination_reason_code,
    data_confidence,                 -- high | medium | low (legacy imports are low)
    import_batch_id                  -- nullable; set for imported rows
)
```

### Overlap rules — the invariant that matters

A person must not hold two **open** memberships of conflicting types at the same time.
Enforce with a database constraint:

```sql
-- Conceptual; concrete DDL in data-model/03-membership.md
EXCLUDE USING gist (
    person_id WITH =,
    membership_type_id WITH =,
    daterange(valid_from, valid_to, '[)') WITH &&
) WHERE (status IN ('active', 'pending_payment'))
```

*Assumption:* `btree_gist` is available (PostgreSQL). If the target database cannot express
exclusion constraints, this becomes a trigger plus a nightly consistency report — weaker,
and it should be recorded as an accepted risk.

Note the constraint is scoped to `membership_type_id`, not to `person_id` alone, because
some combinations are legitimate: a person may simultaneously be an `honorary` member and
an `adult` member. Whether that is *desirable* is an organizational decision; the schema
permits it and [../open-questions.md](../open-questions.md) tracks the decision.

### Membership types are rows

```
membership_type(
    id, code, name,
    category,                        -- child | adult | special
    requires_background_check,
    requires_guardian_consent,
    min_age, max_age,                -- nullable; drives automatic age-out
    duration_months,                 -- typically 12; null = indefinite (lifetime)
    fee_schedule_id,
    sort_order
)
```

*Assumption:* `category` rather than treating type codes as all-equal, because the
permission and validation rules genuinely differ between a child and an adult in a youth
organization, and expressing that once on the type is far better than scattering
`if membership_type == 'child'` through the codebase.

---

## 4. Multiple memberships over a lifetime

This is your 1990–2010 / 2024–present case. It is not an edge case; it is the normal
shape of a long-lived organization's data.

```
person 100 — Jan Novák
  ├── membership #1   child   1990-09-01 → 2010-06-30   completed  (aged out)
  │     └── unit_membership   Troop 12  1990-09-01 → 1998-06-30
  │     └── unit_membership   Troop 31  1998-09-01 → 2010-06-30
  ├── (gap 2010 → 2024 — 14 years, no membership rows)
  └── membership #2   adult   2024-10-01 → NULL          active
        └── unit_membership   Group 5  2024-10-01 → NULL
        └── position_assignment  scoutmaster, Group 5  2025-01-01 → NULL
```

Everything the system needs follows from this:

- **"Is this person a member?"** → is there a membership with `valid_to IS NULL` (or
  covering today) and `status = 'active'`?
- **"How long have they been a member?"** → sum of membership period lengths, not
  today − first join date. The gap must not count.
- **"How old were they when they joined?"** → `membership #2.valid_from − person.birth_date`.
- **"Are they an adult?"** → their *current* membership has `category = 'adult'`. In 2005
  the same query returned `child`. The person never changed; the membership did.

> **Never** store `is_member`, `member_since`, `member_type`, or `is_child` on `person`.
> Every one of those is derivable, and every one of them will be wrong the moment history
> is corrected or a person returns.

---

## 5. Transitions and who can perform them

| From | To | Trigger | Permission required |
|------|-----|---------|---------------------|
| — | `draft` | person starts an application | own |
| `draft` | `submitted` | person submits | `membership.request.create` (own or `dependent.membership.request`) |
| `submitted` | `under_review` | reviewer picks it up | `membership.request.review` |
| `under_review` | `approved` | reviewer approves | `membership.request.approve` |
| `under_review` | `rejected` | reviewer rejects | `membership.request.approve` |
| any | `withdrawn` | applicant withdraws | own, or guardian with permission |
| `approved` | membership `pending_payment` | approval processed | system |
| `pending_payment` | `active` | payment confirmed | system (or `fee.record` for manual) |
| `active` | `lapsed` | fee unpaid at renewal, or voluntary withdrawal | `membership.lapse` or system |
| `active` | `terminated` | disciplinary / cause | `membership.terminate` — **separate, more restricted permission** |
| `active` | `completed` | aged out per `membership_type.max_age` | system |
| `active` | `suspended` | temporary hold | `membership.suspend` |

**Termination must not be the same permission as lapsing.** A lapse is administrative
(nobody paid). A termination is a decision about a person's standing in a youth
organization, often with safeguarding implications. Conflating them means every volunteer
who chases unpaid fees can also expel a member.

---

## 6. Renewal and the yearly fee

*Assumption:* (fee documentation is provisional — see
[../data-model/07-finance.md](../data-model/07-finance.md)). The membership-relevant
part:

Renewal has two possible shapes and they are genuinely different:

**Shape A — renewal opens a new membership period.** Previous row closes, new row opens.
History is explicit; "how many times have they renewed?" is a row count. More rows, and
every query must handle two rows for one continuous membership.

**Shape B — renewal extends `valid_to` on the same membership.** Fewer rows; but it
**destroys history** (you can no longer see that they skipped a year and re-joined) and
it makes retroactive corrections ambiguous.

**Recommendation: Shape A.** You have explicitly asked for history to be preserved across
decades, and Shape B silently loses the single most commonly asked question about
renewals. Implement Shape A and add a `renewed_from_membership_id` self-reference so the
chain is explicit.

```
membership.renewed_from_membership_id → membership.id   -- nullable
```

### Grace periods and lapse

Model a grace period **as a property of the membership type or fee schedule**, not as a
magic date. During grace, the person is still a member — this matters for insurance and
safeguarding, where "member on the day of the camp" is a legal question.

```
membership_type.grace_period_days = 30
```

*Assumption:* the fee is per-person per-year. If families pay once for several children,
that changes `fee_obligation` to be household-scoped, not person-scoped — see
[../open-questions.md](../open-questions.md). The household table exists precisely so this
change is cheap.

---

## 7. Age transitions

Two automatic transitions the system must handle, both because a youth organization's
whole structure depends on age:

**Aging out of a child membership.** Driven by `membership_type.max_age`. On reaching it,
the membership moves to `completed` at the end of the current term — *not* on the birthday
itself, because a member who turns 18 in March is normally a member through June.

**Becoming an adult member.** A separate membership. The person's child membership closes
and an adult one opens. Whether this requires a new request, a new background check, and a
new acceptance depends on the membership types' `requires_*` flags. It should **not** be
automatic — an 18-year-old working with children needs vetting, and the system must be able
to express "turned 18, has not completed adult requirements, therefore not yet an adult
member".

**A flagged edge case:** a person who is 18 and simultaneously completing a child membership
and starting an adult one. The overlap constraint in §3 would block this if both types share
a category; it will not block it across categories. Verify this against your real rules and
record the decision.

---

## 8. Queries this design must support

Stated explicitly so they can be tested. All are point-in-time queries and all must remain
answerable indefinitely:

1. Who is an active member today?
2. Who was a member on any given date in the past?
3. Who was in unit U on date D? (requires `unit_membership`, not `membership`)
4. What is the full membership history of person P, including gaps?
5. Who has an open membership but no unit? (a case needing staff attention)
6. Who was approved but never paid? (a case needing follow-up)
7. Which adult members have a background check expiring within 90 days?
8. Which children turn 15 in the next year? (planning for age-out)
9. Who are the returning members — more than one membership with a gap between? 
10. How many members did the organization have in each year since 1985? (historical
    reporting — must include closed memberships and must not double-count)

Query 10 is the one that fails in most systems, and it fails specifically because someone
made membership a boolean.

---

## 9. Open issues

- Does membership activate on approval or on payment? (§1)
- Is the fee per person or per household? (§6)
- Renewal shape A vs B — recommendation is A, but it affects row volume. (§6)
- Age-out timing: organizational year-end vs birthday. (§7)
- Whether a background check is a blocking requirement for any membership type, and its
  validity period. (§2)
- Whether simultaneous memberships of different types are permitted. (§3)

All tracked in [../open-questions.md](../open-questions.md).
