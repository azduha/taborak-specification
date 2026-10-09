# Data Model — Fees and Payments

> ## ⚠ PROVISIONAL — DO NOT BUILD FROM THIS YET
>
> You have not yet specified fees, pricing, or payment handling. This document exists
> **only** because membership activation depends on payment
> ([../domain/05-membership-lifecycle.md](../domain/05-membership-lifecycle.md#1-the-flow-you-described)),
> so the membership tables need somewhere to point.
>
> Expect to rewrite most of this. It is included so that
> `membership.outstanding_balance` and `membership_type.fee_schedule_id` have referents,
> and so that the open questions below are visible rather than discovered later.

---

## 1. What the domain requires (from what you have said)

Only these facts are established:

- There is a **yearly fee**.
- Becoming a member requires **paying** it (or at least, you described the flow that way
  — see open question 1).
- The fee amount **will be described later**, i.e. it varies.

Everything else — proration, family rates, discounts, refunds, payment methods, invoices,
currency, whether the organization collects or merely records — is unspecified.

---

## 2. Minimal provisional shape

Four tables, deliberately small and easy to replace.

```sql
CREATE TABLE fee_schedule (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    code            TEXT NOT NULL UNIQUE,
    name            TEXT NOT NULL,
    description     TEXT,

    membership_type_id BIGINT REFERENCES membership_type(id),
    -- NULL = applies to any type (e.g. an organization-wide surcharge).

    org_unit_id     BIGINT REFERENCES org_unit(id),
    -- NULL = organization-wide. Set for a unit-level supplementary fee.

    period_months   INTEGER NOT NULL DEFAULT 12,

    amount          NUMERIC(12,2) NOT NULL,
    currency        CHAR(3) NOT NULL DEFAULT 'EUR',
    -- Explicit, even though the organization is single-currency. Multi-currency later
    -- is far easier with the column already present.

    valid_from      DATE NOT NULL,
    valid_to        DATE,
    -- Fee amounts change yearly. Storing the amount on the schedule with a validity
    -- period means a historical obligation can be recomputed correctly — critical
    -- for "what did we charge in 1998?" and for correcting a mis-applied fee.

    is_active       BOOLEAN NOT NULL DEFAULT true,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by      BIGINT REFERENCES person(id),

    CONSTRAINT ck_fee_schedule_period CHECK (
        valid_to IS NULL OR valid_to > valid_from),
    CONSTRAINT ck_fee_schedule_amount CHECK (amount >= 0)
);

CREATE INDEX ix_fee_schedule_lookup ON fee_schedule
    (membership_type_id, valid_from DESC) WHERE is_active;
```

```sql
CREATE TABLE fee_obligation (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    person_id       BIGINT NOT NULL REFERENCES person(id),
    -- The person the fee is FOR. Not the payer — see paid_by_person_id in payment.

    household_id    BIGINT REFERENCES household(id),
    -- Set when the fee is charged per household rather than per person.
    -- OPEN QUESTION 2: which is it?

    membership_id   BIGINT REFERENCES membership(id),
    membership_request_id BIGINT REFERENCES membership_request(id),
    -- What the fee is for. One of these is set, not both.

    fee_schedule_id BIGINT NOT NULL REFERENCES fee_schedule(id),
    -- Snapshotted so the amount is reproducible even if the schedule is edited.

    description     TEXT NOT NULL,
    period_from     DATE NOT NULL,
    period_to       DATE NOT NULL,

    amount_due      NUMERIC(12,2) NOT NULL,
    amount_discount NUMERIC(12,2) NOT NULL DEFAULT 0,
    amount_paid     NUMERIC(12,2) NOT NULL DEFAULT 0,
    currency        CHAR(3) NOT NULL,

    status          TEXT NOT NULL DEFAULT 'unpaid' CHECK (status IN
                        ('unpaid','partially_paid','paid','waived','refunded',
                         'written_off','overdue')),

    due_date        DATE NOT NULL,
    -- Drives the grace period in membership_type.grace_period_days.

    waived_by       BIGINT REFERENCES person(id),
    waived_reason   TEXT,

    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by      BIGINT REFERENCES person(id),
    updated_at      TIMESTAMPTZ,
    updated_by      BIGINT REFERENCES person(id),
    import_batch_id BIGINT,

    CONSTRAINT ck_obligation_period CHECK (period_to > period_from),
    CONSTRAINT ck_obligation_amounts CHECK (
        amount_due >= 0 AND amount_discount >= 0 AND amount_paid >= 0),
    CONSTRAINT ck_obligation_target CHECK (
        (membership_id IS NOT NULL)::int
      + (membership_request_id IS NOT NULL)::int
      + (household_id IS NOT NULL)::int <= 2),
    -- At most two targets: a membership (or request) AND optionally a household
    -- grouping, since a household fee may cover several members' obligations.
    CONSTRAINT ck_obligation_waived CHECK (
        status <> 'waived' OR (waived_by IS NOT NULL AND waived_reason IS NOT NULL))
);

CREATE INDEX ix_obligation_person ON fee_obligation (person_id, status);
CREATE INDEX ix_obligation_open   ON fee_obligation (due_date)
    WHERE status IN ('unpaid','partially_paid','overdue');
CREATE INDEX ix_obligation_membership ON fee_obligation (membership_id)
    WHERE membership_id IS NOT NULL;
CREATE INDEX ix_obligation_household  ON fee_obligation (household_id)
    WHERE household_id IS NOT NULL;
CREATE INDEX ix_obligation_period     ON fee_obligation (period_from, period_to);
```

```sql
CREATE TABLE payment (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    public_id       UUID NOT NULL DEFAULT gen_random_uuid() UNIQUE,

    amount          NUMERIC(12,2) NOT NULL,
    currency        CHAR(3) NOT NULL,

    paid_at         TIMESTAMPTZ NOT NULL,
    -- When the payment occurred, which may differ from when it was recorded
    -- (a bank transfer recorded a week later). Both matter.

    recorded_at     TIMESTAMPTZ NOT NULL DEFAULT now(),

    method          TEXT NOT NULL CHECK (method IN
                        ('cash','bank_transfer','card','direct_debit',
                         'voucher','credit_note','other')),
    reference       TEXT,          -- bank reference, transaction id, receipt number

    paid_by_person_id BIGINT REFERENCES person(id),
    -- Who actually paid. May differ from the person the fee is for — a parent
    -- paying for a child, a grandparent paying for a grandchild, a sponsor.
    -- This is the act-on-behalf record for money.

    on_behalf_of    BIGINT REFERENCES person(id),

    status          TEXT NOT NULL DEFAULT 'confirmed' CHECK (status IN
                        ('pending','confirmed','failed','reversed')),
    confirmed_by    BIGINT REFERENCES person(id),

    notes           TEXT,
    import_batch_id BIGINT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by      BIGINT REFERENCES person(id),

    CONSTRAINT ck_payment_amount CHECK (amount <> 0)
    -- Negative amounts represent reversals; zero is meaningless.
);

CREATE INDEX ix_payment_paid_by ON payment (paid_by_person_id, paid_at DESC);
CREATE INDEX ix_payment_date    ON payment (paid_at DESC);
CREATE INDEX ix_payment_ref     ON payment (reference) WHERE reference IS NOT NULL;
```

```sql
-- Allocation: which payments satisfy which obligations.
-- Many-to-many, because one payment may cover several obligations (a parent pays
-- three children's fees at once) and one obligation may be paid in instalments.
CREATE TABLE payment_allocation (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    payment_id      BIGINT NOT NULL REFERENCES payment(id),
    fee_obligation_id BIGINT NOT NULL REFERENCES fee_obligation(id),

    amount          NUMERIC(12,2) NOT NULL CHECK (amount <> 0),
    allocated_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    allocated_by    BIGINT REFERENCES person(id),
    note            TEXT,

    CONSTRAINT uq_payment_allocation UNIQUE (payment_id, fee_obligation_id)
);

CREATE INDEX ix_allocation_payment    ON payment_allocation (payment_id);
CREATE INDEX ix_allocation_obligation ON payment_allocation (fee_obligation_id);
```

**The allocation table is the part most likely to be right.** A payment and an obligation
are genuinely many-to-many, and any design that puts `payment_id` on the obligation (or
vice versa) breaks the first time a parent pays for three children in one transfer. That
is the common case in this organization, not an edge case.

---

## 3. Keeping `membership.outstanding_balance` honest

[03-membership.md](03-membership.md#3-membership) has a denormalised
`outstanding_balance`. If it stays, it must be maintained in the same transaction as any
allocation change, or it will drift. Two options:

| Option | Pros | Cons |
|--------|------|------|
| Maintain with a trigger on `payment_allocation` | Always current, no recompute | Trigger logic is easy to get subtly wrong |
| Drop the column, compute on demand | Cannot drift | Slower worklist queries |
| Keep as a materialized view | Cannot drift, fast | Refresh lag |

**Recommendation:** drop the column and use a view. The "approved but unpaid" worklist is
not a hot path, and a wrong balance produces either a wrongly-suspended member or a
wrongly-chased family. A wrong number here has a human consequence.

```sql
CREATE VIEW v_fee_obligation_balance AS
SELECT o.id AS fee_obligation_id, o.person_id, o.household_id, o.status,
       o.amount_due, o.amount_discount,
       COALESCE(SUM(a.amount), 0) AS amount_allocated,
       o.amount_due - o.amount_discount - COALESCE(SUM(a.amount), 0) AS balance
  FROM fee_obligation o
  LEFT JOIN payment_allocation a ON a.fee_obligation_id = o.id
  LEFT JOIN payment p ON p.id = a.payment_id AND p.status = 'confirmed'
 GROUP BY o.id;
```

*Assumption:* only `confirmed` payments count toward a balance. A pending bank transfer
should not make someone a member.

---

## 4. How this connects to membership

The activation gate:

```sql
-- Is the member's obligation for the current period settled?
CREATE OR REPLACE FUNCTION is_fee_settled(p_membership_id BIGINT)
RETURNS BOOLEAN LANGUAGE sql STABLE AS $$
    SELECT NOT EXISTS (
        SELECT 1 FROM v_fee_obligation_balance b
         WHERE b.fee_obligation_id IN (
                 SELECT id FROM fee_obligation WHERE membership_id = p_membership_id)
           AND b.balance > 0
           AND b.status NOT IN ('waived','written_off','refunded')
    );
$$;
```

And the lapse trigger — a membership whose fee is unpaid past the grace period:

```sql
-- Run daily. Produces the lapse worklist; does NOT auto-lapse.
SELECT m.id, m.person_id, o.due_date, mt.grace_period_days,
       o.due_date + mt.grace_period_days AS grace_ends
  FROM membership m
  JOIN membership_type mt ON mt.id = m.membership_type_id
  JOIN fee_obligation o ON o.membership_id = m.id
  JOIN v_fee_obligation_balance b ON b.fee_obligation_id = o.id
 WHERE m.status = 'active'
   AND b.balance > 0
   AND o.due_date + mt.grace_period_days < CURRENT_DATE;
```

> **Recommendation: do not auto-lapse.** Produce the worklist and let a human act on it.
> Automatically removing membership from a child because a bank transfer was recorded late
> is a real harm, and the grace period exists precisely to absorb those cases. This is a
> case where automation should stop short of the consequence.

---

## 5. Open issues — the whole of this document, essentially

1. **Does membership activate on payment, or on approval with payment tracked as debt?**
   Changes whether `pending_payment` is a membership status at all.
2. **Is the fee per person or per household?** Determines whether `fee_obligation` targets a
   person or a household, and whether `household` is load-bearing.
3. **Is the fee prorated** for mid-year joins?
4. **Are there family/sibling discounts?** `amount_discount` exists but the rules are
   unspecified.
5. **Refunds:** policy, and who may authorize them. Affects the `payment.status` values.
6. **Payment methods:** which does the organization actually accept? The enum is a guess.
7. **Invoicing:** does the organization issue invoices (legal requirement in some
   jurisdictions)? If so, a `invoice` entity and a numbering sequence are needed.
8. **Is the organization collecting payments or only recording them?** If payments go
   through a gateway, there is a whole webhook/reconciliation layer to design.
9. **Accounting integration:** does anything need to be exported to an accounting system?
10. **Currency and jurisdiction** — currently assumed `EUR`.
11. **Does the fee cover insurance?** If so, "member on the date of the incident" becomes a
    legal record with its own retention needs.
12. **Scholarships/hardship waivers** — a `waived` status exists but the process is
    unspecified, and in a youth organization this is often a sensitive, need-to-know
    process that must not be visible to unit leaders.

All tracked in [../open-questions.md](../open-questions.md). **Rewrite this document once
you specify fees.**
