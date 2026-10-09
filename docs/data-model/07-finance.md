# Data Model — Fees and Payments

> ## ⚠ PROVISIONAL — DO NOT BUILD FROM THIS YET
>
> The **shape** of the obligation is now settled, but almost nothing about the money is.
> This document exists because membership activation depends on payment
> ([../domain/05-membership-lifecycle.md](../domain/05-membership-lifecycle.md#1-the-flow-you-described)),
> and because the yearly expiry and renewal window
> ([D-040](../decisions/decision-log.md#d-040--the-fee-expires-yearly-a-date-tracked-renewal-window-replaces-a-grace-status))
> need somewhere to read a due date from.
>
> Expect to rewrite the tables. Read §1 for what is actually settled.

---

## 1. What the domain requires (from what you have said)

**Settled:**

- There is a **yearly fee**, **flat**, **per person** — it does not vary by age, by
  household, or by membership type, because there is one membership type
  ([D-037](../decisions/decision-log.md#d-037--exactly-one-membership-type-the-fee-is-flat-and-per-person)).
- Becoming a member requires **paying** it; the membership activates on payment
  ([D-040](../decisions/decision-log.md#d-040--the-fee-expires-yearly-a-date-tracked-renewal-window-replaces-a-grace-status)).
- The fee **expires on a fixed organizational date**, typically January. At that date the
  membership **lapses** — the person is not a member — and a **renewal window** follows
  during which they may renew without re-applying. A payment inside the window **opens the
  new period at the expiry date**, so the record shows no gap.
- There is **no grace *status***. The window is tracked as dates, and the resolver does not
  know it exists.

**Unspecified** — the fee *amount*, proration, family discounts, refunds, payment methods,
invoices, currency, and whether the organization collects or merely records.

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

    membership_id   BIGINT REFERENCES membership(id),
    membership_request_id BIGINT REFERENCES membership_request(id),
    event_registration_id BIGINT REFERENCES event_registration(id),
    -- What the fee is for. EXACTLY ONE of these three is set.
    --
    -- The event arm is real, not a hedge: an event with a fee_schedule creates one
    -- obligation per registration (D-066), and payment confirms the place. It
    -- replaced the dormant household_id arm that D-057 removed — same shape, but
    -- with data behind it this time.

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
    -- The yearly fee expires on a fixed organizational date (D-040); this obligation's
    -- due_date is what the lapse sweep compares against. The window that follows is

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
      + (event_registration_id IS NOT NULL)::int = 1),
    -- Exactly one target: a membership period, a membership request, or one
    -- person's place at one event. Still "= 1", not "<= 3" — every obligation is
    -- for exactly one thing. The per-person choice for events is deliberate: the
    -- fee is flat and per person (D-037), and a per-family price would need the
    -- household grouping designed again first (D-057).
    CONSTRAINT ck_obligation_waived CHECK (
        status <> 'waived' OR (waived_by IS NOT NULL AND waived_reason IS NOT NULL))
);

CREATE INDEX ix_obligation_person ON fee_obligation (person_id, status);
CREATE INDEX ix_obligation_open   ON fee_obligation (due_date)
    WHERE status IN ('unpaid','partially_paid','overdue');
CREATE INDEX ix_obligation_event_registration ON fee_obligation (event_registration_id)
    WHERE event_registration_id IS NOT NULL;
CREATE INDEX ix_obligation_membership ON fee_obligation (membership_id)
    WHERE membership_id IS NOT NULL;
CREATE INDEX ix_obligation_period     ON fee_obligation (period_from, period_to);
```

> **The household arm is gone, and an event arm took its place — a real one.** [D-037](../decisions/decision-log.md#d-037--exactly-one-membership-type-the-fee-is-flat-and-per-person)
> settled the fee as flat and per person; [D-057](../decisions/decision-log.md#d-057--household-is-removed)
> then removed the `household` table itself, so `household_id`, its CHECK arm and
> `ix_obligation_household` went with it. Events then supplied a third target that is
> genuinely used: one obligation per registration, created by trigger, paid to confirm the
> place ([D-066](../decisions/decision-log.md#d-066--payment-confirms-the-place-and-the-release-deadline-is-the-one-automatic-transition)).
>
> **The CHECK reads `= 1`, which is the point.** Three arms, exactly one set — a membership
> period, a membership request, or one person's place at one event. The previous version read
> `<= 2` with a dormant arm against a hypothetical; this one states the domain. That is the
> difference between a constraint and a hedge, and it is worth preserving: if a fourth target
> is ever added, check whether it is *used* before widening this.
>
> **If a family discount is ever wanted**, the row is still the right shape — one obligation
> covering several people — but it now needs the grouping to be re-introduced first, as a
> group with a period rather than a fake person ([04 §3](04-relationships.md#3-there-is-no-household-table)).

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
SELECT o.id AS fee_obligation_id, o.person_id, o.status,
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

And the yearly expiry sweep — this one **does** change membership status, unlike everything
else in this document:

```sql
-- Run on 1 January (membership_expiry_date(), D-047). This is the ONE automatic
-- membership transition in the system.
SELECT m.id, m.person_id, o.due_date,
       membership_expiry_date(CURRENT_DATE) AS expiry,
       membership_expiry_date(CURRENT_DATE) + mt.renewal_grace_days AS window_ends
  FROM membership m
  JOIN membership_type mt ON mt.id = m.membership_type_id
  JOIN fee_obligation o ON o.membership_id = m.id
  JOIN v_fee_obligation_balance b ON b.fee_obligation_id = o.id
 WHERE m.status = 'active'
   AND b.balance > 0
   AND o.due_date < CURRENT_DATE;
-- → set m.status = 'lapsed', set m.valid_to = the expiry date, and
--   INVALIDATE THE PERMISSION CACHE FOR EVERY ROW RETURNED (by person, not by scope).
--
-- The sweep must NOT close the root unit_participation row — it moves valid_to forward
-- instead, so a renewal inside the window can extend one continuous row (D-050). See
-- 03-membership.md §5.1.
--
-- Note the personnel consequence: this runs for everyone at once, including the person
-- who runs it. Without system.gate_exempt (D-051) the administrator would lock
-- themselves out on this date.
--   BY PERSON for every row returned. See domain/06-authorization-model.md §8.
```

> **This reverses an earlier recommendation, and the reversal is worth recording.** This
> document previously said "do not auto-lapse — produce the worklist and let a human act."
> The reasoning was sound: automatically removing membership from a child because a bank
> transfer was recorded late is a real harm.
>
> [D-040](../decisions/decision-log.md#d-040--the-fee-expires-yearly-a-date-tracked-renewal-window-replaces-a-grace-status)
> resolves it differently, and the resolution is that **the expiry is a date, not a
> decision.** The fee covers a fixed period and the period ends. Nobody decides anything,
> and the renewal window exists to absorb exactly the late-transfer case: a payment inside
> it backdates the new period to the expiry date, so the record shows no gap and the person
> was never misclassified.
>
> **Where the old caution still applies** is the case the window cannot absorb — a payment
> that *arrived* before the expiry but was *recorded* after it. That is a data-entry lag,
> not a non-payment, and it should be corrected with `membership.backdate` rather than left
> as a real gap. Worth a report: members who lapsed and then paid within a few days.

---

## 5. Open issues — the whole of this document, essentially

1. **Is the fee prorated** for mid-year joins? Note this is a sharper question than it was:
   with the expiry on a fixed date ([D-040](../decisions/decision-log.md#d-040--the-fee-expires-yearly-a-date-tracked-renewal-window-replaces-a-grace-status)),
   someone joining in October pays for three months of a twelve-month fee unless the
   organization prorates — and the *renewal* twelve months later is a full year. Whether
   that is fair is a policy question; whether the schema supports it is `amount_due` vs
   `amount_expected`.
2. **Are there family/sibling discounts?** `amount_discount` exists but the rules are
   unspecified. With a flat per-person fee ([D-037](../decisions/decision-log.md#d-037--exactly-one-membership-type-the-fee-is-flat-and-per-person)),
   this is the only remaining fee variation, so it is worth a deliberate yes or no. Note
   that [D-057](../decisions/decision-log.md#d-057--household-is-removed) has now removed the
   `household` grouping, so a **per-family** discount is no longer a constraint change — it
   needs that grouping designed again first. A **per-person** discount is unaffected and is
   just `amount_discount`.
3. **Refunds:** policy, and who may authorize them. Affects the `payment.status` values.
4. **Payment methods:** which does the organization actually accept? The enum is a guess.
5. **Invoicing:** does the organization issue invoices (legal requirement in some
   jurisdictions)? If so, an `invoice` entity and a numbering sequence are needed.
6. **Is the organization collecting payments or only recording them?** If payments go
   through a gateway, there is a whole webhook/reconciliation layer to design. Note the
   renewal window makes this more urgent than it was: a gateway can confirm a payment
   *inside* the window, which is what makes the backdating rule reliable rather than
   dependent on someone recording a transfer by hand in February.
7. **Accounting integration:** does anything need to be exported to an accounting system?
8. **Currency and jurisdiction** — currently assumed `EUR`.
9. **Does the fee cover insurance?** If so, "member on the date of the incident" becomes a
   legal record with its own retention needs. This one interacts directly with the new
   lapse rule ([D-040](../decisions/decision-log.md#d-040--the-fee-expires-yearly-a-date-tracked-renewal-window-replaces-a-grace-status)):
   if the fee buys insurance, then **the date the membership lapses is the date cover
   ends**, and the renewal window does *not* extend it. That is worth confirming with
   whoever handles the policy, because the softer "still covered during grace" reading was
   the alternative D-040 explicitly rejected.
10. **Scholarships/hardship waivers** — a `waived` status exists but the process is
    unspecified, and in a youth organization this is often a sensitive, need-to-know
    process that must not be visible to unit leaders.

**Resolved and no longer open**, kept visible so the reasoning survives: activation on
payment or on approval (on payment — [D-040](../decisions/decision-log.md#d-040--the-fee-expires-yearly-a-date-tracked-renewal-window-replaces-a-grace-status));
whether the fee is per person or per household (per person, flat and ageless —
[D-037](../decisions/decision-log.md#d-037--exactly-one-membership-type-the-fee-is-flat-and-per-person));
and whether the household grouping survives at all (**no** — removed entirely,
[D-057](../decisions/decision-log.md#d-057--household-is-removed)). But note that D-057 did not
close question 2: with no grouping, a *per-family* discount now needs one designed again
before it can be priced. That is why there are still **ten** questions above rather than nine —
one question got sharper as another closed.

All tracked in [../open-questions.md](../open-questions.md). **Rewrite this document once
you specify fees.**
