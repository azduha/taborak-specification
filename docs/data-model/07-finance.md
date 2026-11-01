# Data Model — Fees and Payments

> ## ⚠ PROVISIONAL ON POLICY, SETTLED ON ARCHITECTURE
>
> **How money moves is now decided.** Money arrives from a **bank API** and is requested by a
> **variable symbol and a QR code**
> ([D-075](../decisions/round-06.md#d-075--money-arrives-from-a-bank-api-a-payment-is-requested-by-variable-symbol-and-qr-code));
> money that cannot be matched **waits for a person**
> ([D-076](../decisions/round-06.md#d-076--money-that-cannot-be-matched-waits-for-a-person)).
> There is no card gateway, no checkout and no dispute handling, and §2a is the consequence.
>
> **What the money is for is answered.** The fee is priced in **koruna**
> ([D-155](../decisions/round-22.md#d-155--the-currency-is-koruna-and-the-modules-own-money-path-said-so)),
> it buys **membership and nothing else**
> ([D-156](../decisions/round-22.md#d-156--the-fee-buys-nothing-but-membership)), there is one live
> price edited in place, and the number on an obligation is the number a person wrote there
> ([D-161](../decisions/round-22.md#d-161--one-live-price-and-the-amount-is-filed-as-a-question-at-last),
> [D-160](../decisions/round-22.md#d-160--no-proration-rule-and-the-row-is-the-amount)). Nobody waives
> a fee and nothing refunds one inside the system
> ([D-157](../decisions/round-22.md#d-157--there-are-no-hardship-waivers),
> [D-158](../decisions/round-22.md#d-158--a-refund-happens-at-the-bank)).
>
> **Five questions are open**, listed and numbered in §5: discounts, invoices, the accounting export,
> jurisdiction, and what gets a variable symbol. Those are policy questions this document cannot
> answer, and each needs somebody in the organization to be asked.
>
> This document exists because membership activation depends on payment
> ([../domain/05-membership-lifecycle.md](../domain/05-membership-lifecycle.md#1-the-flow-you-described)),
> and because the yearly expiry and renewal window
> ([D-040](../decisions/round-02-03.md#d-040--the-fee-expires-yearly-a-date-tracked-renewal-window-replaces-a-grace-status))
> need somewhere to read a due date from.

---

## 1. What the domain requires

**Settled:**

- There is a **yearly fee**, **flat**, **per person** — it does not vary by age, by
  household, or by membership type, because there is one membership type
  ([D-037](../decisions/round-02-03.md#d-037--exactly-one-membership-type-the-fee-is-flat-and-per-person)).
- Becoming a member requires **paying** it; the membership activates on payment
  ([D-040](../decisions/round-02-03.md#d-040--the-fee-expires-yearly-a-date-tracked-renewal-window-replaces-a-grace-status)).
- The fee **expires on a fixed organizational date**, typically January. At that date the
  membership **lapses** — the person is not a member — and a **renewal window** follows
  during which they may renew without re-applying. A payment inside the window **opens the
  new period at the expiry date**, so the record shows no gap.
- There is **no grace *status***. The window is tracked as dates, and the resolver does not
  know it exists.
- The fee is charged in **koruna**. One currency, and a second one is refused rather than deferred;
  the column stays because the refusal is cheap to reverse with it
  ([D-155](../decisions/round-22.md#d-155--the-currency-is-koruna-and-the-modules-own-money-path-said-so)).
- The fee buys **membership** — no insurance is bought with it, sold with it, or implied by it, so
  **no date in this system is evidence of cover**
  ([D-156](../decisions/round-22.md#d-156--the-fee-buys-nothing-but-membership)).
- There is **one live price**, edited in place when a billing year is reopened, because what a person
  owed was never stored in the price list anyway (§2)
  ([D-161](../decisions/round-22.md#d-161--one-live-price-and-the-amount-is-filed-as-a-question-at-last)).
- What a person owes is **whatever their obligation says**. No proration rule and no waiver mechanism
  decide it: a reduced fee is an obligation written with a smaller `amount_due`, the same act that
  writes any other amount
  ([D-160](../decisions/round-22.md#d-160--no-proration-rule-and-the-row-is-the-amount),
  [D-157](../decisions/round-22.md#d-157--there-are-no-hardship-waivers)).
- Money out is recorded exactly like money in — **a refund is a `payment` in the opposite
  direction**, and nobody initiates one inside this system
  ([D-158](../decisions/round-22.md#d-158--a-refund-happens-at-the-bank)).
- **What a person was asked to pay is never edited.** A changed amount voids the live request and
  issues a new one under a new variable symbol, because the old figure is already printed on a QR code
  in somebody's hand; the liability underneath is edited in place, and no column holds a reduction —
  `amount_discount` is gone, and the balance lost its term with it
  ([D-183](../decisions/round-23.md#d-183--a-changed-ask-is-a-voided-request-and-a-new-symbol-and-amount_discount-goes)).
- **An invoice is a second row over the same ask**, written only because a payer asked for one. A
  `payment_request` is not an invoice and does not become one ([D-187](../decisions/round-23.md#d-187--an-invoice-is-a-document-a-payer-asks-for)).

**Unspecified** — whether anything is exported to an accounting system, and what the law of this
country requires of a fee, which is also what decides what an invoice must contain. Both are in §5,
together with what a payment that does not fit its ask settles.

**Settled, and the big one** — the organization **collects**, but not through
a card gateway: money is requested by **variable symbol + QR code** and **arrives from the bank
API** already tagged (§2a, [D-075](../decisions/round-06.md#d-075--money-arrives-from-a-bank-api-a-payment-is-requested-by-variable-symbol-and-qr-code)).

---

## 2. Minimal provisional shape

Seven tables, deliberately small and easy to replace. This sentence printed **four** for two rounds while
**six** were defined underneath it, which is what a typed count does; `invoice` is the seventh and the only
one added since ([D-187](../decisions/round-23.md#d-187--an-invoice-is-a-document-a-payer-asks-for)).

**`fee_schedule`** — a price. One is live at a time, and it is edited in place when a billing year is
reopened; there is no price history, and none is needed, because what a person owed was never in here.

**Fields**

| Field | Kind | Notes |
|---|---|---|
| `id` | surrogate id | |
| `code` | text, required | |
| `name` | text, required | |
| `description` | text, optional | |
| `membership_type_id` | reference to membership type, optional | `NULL` = applies to any type, e.g. an organization-wide surcharge |
| `period_months` | integer, required | Default 12 |
| `amount` | money, required | Zero or more |
| `currency` | three-letter currency code, required | `CZK`, and the only value this organization writes. Required and explicit anyway: a second currency is refused for now, and the column is what makes that refusal cheap to reverse ([D-155](../decisions/round-22.md#d-155--the-currency-is-koruna-and-the-modules-own-money-path-said-so)) |
| `is_active` | boolean, required | Default true |
| `created_at` | timestamp, audit time | |
| `created_by` | reference to person, optional | |

**Nothing on a schedule is scoped to a body.** A `fee_schedule` is scoped to a membership type — one row,
so nothing in practice — and to nothing else at all: it is the price, current until somebody writes a
different one into the same row. **A fee is what it has always been charged as: flat, per person, at the
unit** ([D-037](../decisions/round-02-03.md#d-037--exactly-one-membership-type-the-fee-is-flat-and-per-person)).
**Why nothing narrower:** [D-095](../decisions/round-09.md#d-095--units-carry-no-restrictions-joining-one-is-somebody-elses-act)
had already ruled that entry below the membership carries no money — *into the sub-units, there is no fee* —
so a supplementary fee for one body was a possibility no answer ever took. If a group ever needs a charge of
its own, that is a policy question for §5 and a new shape of obligation, not a column to hold in reserve.

**Rules**

- `code` is unique. It covers all rows, not only active ones.
- `amount` is zero or more.

**Indexes**

- The one lookup that matters is the live schedule for one membership type: the type and `is_active`
  together, which are expected to return one row.

**One live price, and why editing it in place is safe.** `fee_obligation` snapshots `fee_schedule_id`
"so the amount is reproducible even if the schedule is edited", and it copies `amount_due` beside the
reference — so the record of what a person owed was never in the schedule at all. Only the price list
was, and a price list is not a record
([D-161](../decisions/round-22.md#d-161--one-live-price-and-the-amount-is-filed-as-a-question-at-last)).
What is given up is the price list's own history: nobody can ask this system what a membership cost in
2027. The answer available is an aggregate over the obligations of 2027, which reports what people were
actually asked rather than what a list said. **No code is named for editing the price row**, and the gap
is named rather than filled: on the reading this design carries, opening a billing year is reached by
whatever grant already lets a person write a fee at that scope, which is this corpus's inference from
[D-161](../decisions/round-22.md#d-161--one-live-price-and-the-amount-is-filed-as-a-question-at-last)
and not a ruling inside it.

**`fee_obligation`** — one thing someone owes.

**Fields**

| Field | Kind | Notes |
|---|---|---|
| `id` | surrogate id | |
| `person_id` | reference to person, required | The person the fee is **for**. Not the payer — see `paid_by_person_id` on `payment` |
| `membership_id` | reference to membership, optional | One of the three target columns; exactly one is set |
| `membership_request_id` | reference to membership request, optional | One of the three target columns |
| `event_registration_id` | reference to event registration, optional | One of the three target columns. The event arm is real, not a hedge: an event with a `fee_schedule` creates one obligation per registration (D-066), and payment confirms the place. |
| `fee_schedule_id` | reference to fee schedule, required | Snapshotted so the amount is reproducible even if the schedule is edited |
| `description` | text, required | |
| `period_from` | date, required | |
| `period_to` | date, required | |
| `amount_due` | money, required | The number this person owes, and it may be written again: editing it in place is how a fee is reduced, corrected, or negotiated, and nothing records that a reduction happened ([D-183](../decisions/round-23.md#d-183--a-changed-ask-is-a-voided-request-and-a-new-symbol-and-amount_discount-goes)) |
| `amount_paid` | money, required | Default 0 |
| `currency` | three-letter currency code, required | `CZK`, as on the schedule it came from |
| `status` | text, required | Default `unpaid`. One of: `unpaid`, `partially_paid`, `paid` — **and nothing else.** The three values say how much of this obligation has arrived, and nothing more: lateness is read from `due_date`, and a fee nobody is going to pay is a row with a smaller `amount_due` ([D-159](../decisions/round-22.md#d-159--the-status-enum-keeps-three-of-its-seven-values)) |
| `due_date` | date, required | The yearly fee expires on a fixed organizational date (D-040); this obligation's `due_date` is what the lapse sweep compares against (§4). The renewal window that follows is carried as dates, not as a status (§1). **This is also the only place lateness lives:** an obligation past this date and not paid is overdue, and no status value says so ([D-159](../decisions/round-22.md#d-159--the-status-enum-keeps-three-of-its-seven-values)) |
| `created_at` | timestamp, audit time | |
| `created_by` | reference to person, optional | |
| `updated_at` | timestamp, audit time | |
| `updated_by` | reference to person, optional | |

**Rules**

- `period_to` is later than `period_from`.
- `amount_due` and `amount_paid` are each zero or more.
- Exactly one of `membership_id`, `membership_request_id` and `event_registration_id` is
  set — one, not zero and not two. Every obligation is for exactly one thing: a membership
  period, a membership request, or one person's place at one event. The per-person choice
  for events is deliberate: the fee is flat and per person (D-037), and a per-family price
  would need the household grouping designed again first (D-057).
- `status` is arithmetic, not a decision. It reports how much of `amount_due` has arrived, so there is
  no value to set for a fee that will not be collected and no value to set because `due_date` has
  passed. A fee nobody is going to pay is an obligation written with a smaller `amount_due`; being late
  is a report over a date
  ([D-157](../decisions/round-22.md#d-157--there-are-no-hardship-waivers),
  [D-159](../decisions/round-22.md#d-159--the-status-enum-keeps-three-of-its-seven-values)).

**Indexes**

- One person's obligations, by status.
- Obligations ordered by `due_date`, restricted to the rows still open — `unpaid` or `partially_paid`.
  Closed rows are not in it. **Read down this index past today's date and it is the overdue list**: one
  fact stored once, with no status value to keep in step with the calendar.
- Obligations carrying the event arm, and obligations carrying the membership arm — each
  restricted to the rows where that column is set.
- Obligations within a `period_from` / `period_to` range.

> **The event arm is the third target that is genuinely used.** [D-037](../decisions/round-02-03.md#d-037--exactly-one-membership-type-the-fee-is-flat-and-per-person)
> settled the fee as flat and per person, so an event carrying a `fee_schedule` has **one obligation per
> registration**, created by the code that places the registration and paid to confirm the place
> ([D-066](../decisions/round-05.md#d-066--payment-confirms-the-place-and-the-release-deadline-is-the-one-automatic-transition)).
> **Nothing creates it if that code is not written:** no trigger writes it, and a trigger could not have been
> forgotten — the trade is stated in
> [00-conventions §6a](00-conventions.md#6a-who-enforces-an-invariant-now). An event with a fee and no
> obligation is invisible until someone reconciles money against the roster.
>
> **Exactly one, never zero and never two — and unlike most rules in these documents this one can
> still be stated declaratively, so a migration should state it.** Three columns, exactly one set:
> count how many are present and require that count to be one, which is a condition on the row and
> nothing else. No subquery, no other table, and therefore emittable by any migration that can put a
> condition on a row at all — the case where the ORM argument simply does not apply. **It is worth
> naming explicitly, because it is the counterexample to the general worry** — most of what D-072
> deleted genuinely cannot be restated declaratively
> ([shape 3](00a-invariant-register.md#3-the-answer-reads-another-table-a-resolver-or-a-graph)),
> and this is not one of them.
>
> **If a fourth target is ever proposed, ask whether it is *used*, and expect the answer to be no.**
> "At most two of three," with one arm kept against a hypothetical, is not the same domain as exactly one
> over three real targets, and the difference only shows up when somebody adds the fourth.
>
> **If a family discount is ever wanted**, the row is still the right shape — one obligation
> covering several people — but it now needs the grouping to be re-introduced first, as a
> group with a period rather than a fake person ([04 §3](04-relationships.md#3-there-is-no-household-table)).

**`payment`** — money that moved, as one recorded act.

**Fields**

| Field | Kind | Notes |
|---|---|---|
| `id` | surrogate id | |
| `public_id` | external identifier, required | Unique. Appears in URLs and exports; `id` stays internal (00-conventions §3) |
| `amount` | money, required | Never zero. A negative amount is money going out — a refund, a correction, or a reversal. **This is the only way money leaves**: there is no refund state anywhere for a row like this to point at, so a refund is written as one of these and the person who recorded it is in the row ([D-158](../decisions/round-22.md#d-158--a-refund-happens-at-the-bank)) |
| `currency` | three-letter currency code, required | `CZK`, on money going out exactly as on money coming in |
| `paid_at` | timestamp, required | When the payment occurred, which may differ from when it was recorded — a bank transfer recorded a week later. Both matter |
| `recorded_at` | timestamp, audit time | Default: now |
| `method` | text, required | One of: `bank_transfer`, `cash`, `voucher`, `credit_note`, `other`. **`card` and `direct_debit` removed** — there is no card gateway and no mandate system ([D-075](../decisions/round-06.md#d-075--money-arrives-from-a-bank-api-a-payment-is-requested-by-variable-symbol-and-qr-code)) |
| `variable_symbol` | text, optional | The symbol the money arrived under, copied verbatim from the bank statement. Set on every row the import created; the join back to `payment_request`. **Never typed by hand** |
| `reference` | text, optional | Bank reference, transaction id, receipt number |
| `paid_by_person_id` | reference to person, optional | Who actually paid. May differ from the person the fee is for — a parent paying for a child, a grandparent paying for a grandchild, a sponsor. This is the act-on-behalf record for money |
| `on_behalf_of` | reference to person, optional | |
| `status` | text, required | Default `confirmed`. **`confirmed` or `reversed`, and nothing else.** A bank transfer the bank has reported does not later fail, expire, or get reversed by a card network, so the two values describe whether *we* still stand behind the row. There is no `pending` and no `failed`: a promised transfer is not a state ([D-075](../decisions/round-06.md#d-075--money-arrives-from-a-bank-api-a-payment-is-requested-by-variable-symbol-and-qr-code)) |
| `confirmed_by` | reference to person, optional | |
| `notes` | text, optional | |
| `created_at` | timestamp, audit time | |
| `created_by` | reference to person, optional | |

**Rules**

- `amount` is never zero; zero is meaningless. Negative amounts are reversals.
- `public_id` is unique.

**Indexes**

- A payer's payments, newest `paid_at` first.
- Payments by date, newest first.
- Lookup by `reference`, restricted to rows that have one.

**`payment_allocation`** — which payments satisfy which obligations. It is many-to-many in
both directions: one payment may cover several obligations, and one obligation may be paid in
instalments.

**Fields**

| Field | Kind | Notes |
|---|---|---|
| `id` | surrogate id | |
| `payment_id` | reference to payment, required | |
| `fee_obligation_id` | reference to fee obligation, required | |
| `amount` | money, required | Never zero |
| `allocated_at` | timestamp, audit time | Default: now |
| `allocated_by` | reference to person, optional | |
| `note` | text, optional | |

**Rules**

- A given payment is allocated to a given obligation at most once — one row per pair, over
  all rows.
- `amount` is never zero.

**Indexes**

- Allocations of one payment, and allocations of one obligation — both directions are asked.

**The allocation table is the part most likely to be right.** A payment and an obligation
are genuinely many-to-many, and any design that puts `payment_id` on the obligation (or
vice versa) breaks the first time a parent pays for three children in one transfer. That
is the common case in this organization, not an edge case.

---

## 2a. How money actually arrives

[D-075](../decisions/round-06.md#d-075--money-arrives-from-a-bank-api-a-payment-is-requested-by-variable-symbol-and-qr-code).
The system **requests** a payment and then **reads** one. It never touches the money.

The flow, in order:

1. A liability exists — a membership period, a membership request, a place at an event.
2. The system issues a **`payment_request`** carrying a **variable symbol** and an amount. Every
   payable gets one — the yearly fee and a camp fee alike — because a liability with no symbol has
   money arriving against nothing and no list where that would show ([D-181](../decisions/round-23.md#d-181--every-payable-has-a-variable-symbol)).
3. The payer is shown the symbol, the amount, and a **QR code** that encodes all three.
4. The payer's own bank moves the money. The system is not involved and learns nothing yet.
5. A **bank import** reads the account statement and produces a **`bank_transaction`** for each
   incoming transfer, with the variable symbol still attached.
6. The symbol resolves to a live request. The fetch creates a `payment`, links it, and the
   obligation's balance falls. Both rows belong to the fetch's own actor, `system:bank-pull`, because
   resolving a symbol is not a human act ([D-182](../decisions/round-23.md#d-182--matching-money-is-a-code-of-its-own-and-the-automatic-half-is-systembank-pulls)).
7. If the symbol resolves to nothing live, the transaction stays exactly as it arrived: **unmatched,
   which is not a queue** (§2b) ([D-180](../decisions/round-23.md#d-180--there-is-no-queue-for-money-that-does-not-fit)).

**`payment_request`** — the liability rendered payable.

**Fields**

| Field | Kind | Notes |
|---|---|---|
| `id` | surrogate id | |
| `variable_symbol` | text, required | **Unique across all rows, forever, including cancelled and long-settled ones.** Eleven digits from a sequence |
| `fee_obligation_id` | reference to fee obligation, required | What is owed. The request never invents an amount of its own |
| `amount` | money, required | Copied from the obligation at issue time, so a later price change cannot rewrite what someone was asked for |
| `currency` | three-letter currency code, required | `CZK`, copied alongside the amount for the same reason |
| `recipient_account` | text, required | The account the QR code tells people to pay into |
| `issued_at` | timestamp, audit time | |
| `expires_at` | date, optional | When the request stops being payable — the close of a renewal window, or the day before an event |
| `voided_at` | timestamp, optional | Set by a person, or by cancelling the event the request was for (§2b) |
| `voided_reason` | text, optional | |

**Rules**

- **`variable_symbol` is unique over every row that ever existed**, not over live rows. A symbol
  issued in 2019 must never resolve to a 2026 obligation, because bank statements get re-imported
  and late payments are the entire reason the renewal window exists.
- **The symbol comes from a sequence.** It is never derived from a birth date, a membership id,
  a member number, or anything else a person can guess or work out. Anyone can type eleven digits
  into a payment form at their bank; a guessable symbol means a stranger's money lands in a
  child's record, and the damage is not cosmetic — it reads as **a paid fee and an active membership
  that nobody earned**, in the one part of this database that is kept with no end date
  ([D-088](../decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)).
  A fee row is the organization's own history from the moment it is written, not a draft somebody
  confirms later. That is also the ceiling on the damage: since the fee buys membership and nothing
  else ([D-156](../decisions/round-22.md#d-156--the-fee-buys-nothing-but-membership)), no date here can
  be read as anything more than that.
- `amount` is a **copy**, not a live reference. What a person was asked to pay is a historical
  fact about the ask, and recomputing it from the current schedule would make every price change
  rewrite history.
- One obligation may have several requests over time — a first request expires, or the ask changes,
  which is a void and a new symbol rather than an edit ([D-183](../decisions/round-23.md#d-183--a-changed-ask-is-a-voided-request-and-a-new-symbol-and-amount_discount-goes)) — but **at most one live
  request per obligation**. `amount_due` on the obligation is edited in place; `amount` on a request
  never is, because the figure has already been shown to somebody standing at their own bank.
- A request is not an invoice. Nothing is delivered, nothing is numbered for a tax authority. An
  invoice is a separate row over the same ask, written only because a payer asked for it
  ([D-187](../decisions/round-23.md#d-187--an-invoice-is-a-document-a-payer-asks-for)).

**`invoice`** — a document somebody asked for. It exists or it does not.

| Field | Kind | Notes |
|---|---|---|
| `id` | surrogate id | |
| `number` | text, required | **Unique, and never reused.** Its own sequence, beside the variable symbol's and independent of it: a symbol resolves a payment to an ask, a number identifies a document to a tax authority, and nothing promises the two agree ([D-187](../decisions/round-23.md#d-187--an-invoice-is-a-document-a-payer-asks-for)) |
| `payment_request_id` | reference to payment request, required | The ask it documents. Never a bare obligation, because the request is what the payer was shown |
| `amount` | money, required | Copied from the request, for the same reason the request copies it from the obligation: an edit to the liability must not rewrite a document that has already been handed over ([D-183](../decisions/round-23.md#d-183--a-changed-ask-is-a-voided-request-and-a-new-symbol-and-amount_discount-goes)) |
| `currency` | three-letter currency code, required | `CZK` |
| `issued_at` | timestamp, required | |
| `issued_by` | reference to person, required | Whoever holds `invoice.issue`. Not the payer who asked, because there is no row for the asking |

**Rules**

- **No state.** No `requested`, no `sent`, no `delivered`. A column meaning *somebody owes this person
  a document*, with nobody assigned to it and nothing counting it, is the queue this module just
  deleted wearing a different coat ([D-180](../decisions/round-23.md#d-180--there-is-no-queue-for-money-that-does-not-fit)). The ask that precedes the row is a conversation
  the organization had with the payer, held outside the database — the way two groups being the same
  group is said and not stored ([D-173](../decisions/round-23.md#d-173--that-two-groups-are-the-same-group-is-said-not-stored)).
- **Nothing sends the invoice to anybody** ([D-164](../decisions/round-22.md#d-164--nobody-is-told-and-no-page-may-say-otherwise)). It exists on a screen and is handed over
  by a person, or printed by one.
- A voided request keeps its invoice. Both rows are permanent.
- Most obligations have no invoice at all, and no report is planned over the requests that have none.
  If forgetting one turns out to be a real failure, the fix is that report, not a status
  ([D-187](../decisions/round-23.md#d-187--an-invoice-is-a-document-a-payer-asks-for)).
- What else a document of this kind must contain is a legal question the design does not answer, and no
  column is invented for it here (§5).

**`bank_transaction`** — one incoming transfer as the bank reported it.

| Field | Kind | Notes |
|---|---|---|
| `id` | surrogate id | |
| `bank_account` | text, required | |
| `bank_reference` | text, required | **Unique per bank account.** This is the idempotency key: the same statement imported twice must create nothing the second time |
| `arrived_at` | date, required | The bank's date, not the import's — this is the date D-040's renewal window is measured against |
| `amount` | money, required | |
| `variable_symbol` | text, optional | As reported. Can be absent, wrong, or a stranger's |
| `payer_description` | text, optional | Whatever the bank gives: a name, sometimes an address |
| `matched_payment_request_id` | reference to payment request, optional | NULL means **unmatched**: the absence of a match, not a queue and not a piece of work ([D-180](../decisions/round-23.md#d-180--there-is-no-queue-for-money-that-does-not-fit)) |
| `imported_at` | timestamp, audit time | When the fetch wrote the row. Which fetch is in that row's own actor column — `system:bank-pull` — and there is no batch to point at, because the batch table is gone ([D-190](../decisions/round-23.md#d-190--the-legacy-import-is-a-script-and-a-key-and-the-pipeline-is-gone)) |

**Rules**

- `bank_reference` is unique within a bank account. Re-importing a statement is safe and must be.
- A transaction is **immutable once imported.** Corrections are new rows or a re-import, never an
  edit — this is the organization's copy of somebody else's ledger, and the only version of it
  that will ever agree with the bank.

**The renewal window stops being a promise.** [D-040](../decisions/round-02-03.md#d-040--the-fee-expires-yearly-a-date-tracked-renewal-window-replaces-a-grace-status)
backdates a renewal to the expiry date when payment lands inside the window, and its own note
said that rule was only as good as the reliability of payment dates. Until now they arrived when
somebody noticed a transfer. **They now arrive from the bank**, dated by the bank. The sweep in §4
can run unattended because the thing it depends on is no longer a person remembering in February.

**What this deletes from the design.** No checkout, no card tokens, no PCI surface, no webhook
endpoint to authenticate, no dispute or chargeback state, no reconciliation report against a
processor's payout. `payment.status` loses `pending` and `failed`: a bank transfer the bank has
reported is confirmed on arrival, and there is no in-between state to model. What remains in
`status` is whether *we* still stand behind the row — `confirmed` or `reversed`.

---

## 2b. Money that cannot be matched

[D-076](../decisions/round-06.md#d-076--money-that-cannot-be-matched-waits-for-a-person).

**An unmatched transaction is a fact with no subject, so the absence gets stored rather than
guessed at** — the same discipline as "unanswered is the absence of a row"
([D-059](../decisions/round-05.md#d-059--unanswered-is-the-absence-of-a-row-a-registration-stores-two-values)).
`matched_payment_request_id IS NULL` is the absence of a match and nothing besides — not a worklist,
not a count, not a page somebody is expected to clear. **There is no queue here**
([D-180](../decisions/round-23.md#d-180--there-is-no-queue-for-money-that-does-not-fit)): most money that lands in this account has nothing to do with a member at all —
a grant, a donation, a shop's sponsorship — and an unmatched row is the ordinary shape of the
statement rather than an exception to it. D-076's rule survives untouched: a row gets no subject
assigned by a match on an amount and a date. What goes is the picture underneath the rule, that an
unmatched row means a person is waiting somewhere behind it.

**Why a transaction has no match:** the symbol matches no request. The symbol matches a request
that has been voided. The request is already settled. The amount is less than asked, or more.
There is no symbol at all — cash-basis donors and people who type their own name in the wrong
field.

**What the system does with any of those: nothing.** It records the money. No page opens on it,
nothing counts it, and nothing sends anything to anyone about it
([D-164](../decisions/round-22.md#d-164--nobody-is-told-and-no-page-may-say-otherwise)).

When a person does decide to act, tying the transaction to a request is a write with a code of its
own, `payment.match`, held at the organization's scope by whoever runs the accounting
([D-182](../decisions/round-23.md#d-182--matching-money-is-a-code-of-its-own-and-the-automatic-half-is-systembank-pulls)). **There are exactly four outcomes they can choose between:**

| Outcome | When |
|---|---|
| **Attach** it to a different request | The symbol was mistyped; the real obligation is obvious from the payer |
| **Split** it across requests | One transfer, three siblings — the ordinary shape of family payment here |
| **Record as a donation** | Money with no obligation behind it, which is not the same as money that is missing one |
| **Refund** it, by hand | Nothing was meant to be owed. A second payment in the opposite direction ([D-075](../decisions/round-06.md#d-075--money-arrives-from-a-bank-api-a-payment-is-requested-by-variable-symbol-and-qr-code)): the transfer goes out at the bank, and what arrives here is a `payment` naming whoever recorded it ([D-158](../decisions/round-22.md#d-158--a-refund-happens-at-the-bank)) |

**Why the tempting shortcut is refused.** Falling back to the payer's identity when the symbol
fails looks like it clears most of the unmatched rows. It clears most of their *accuracy* instead:
*a parent with two children pays one amount against one symbol* is the normal case, not the edge
case, and an identity fallback resolves it to whichever child the query reaches first. **A fee
recorded against the wrong child is a finance error and a membership that appears paid when it is
not, both at once — and the sibling it was meant for stays the one who looks unpaid.** Both halves
sit in rows that are kept with no end date. A fallback is not allowed to be wrong on the common
path, and this is the common path.

Auto-refunding is refused for two reasons: it needs the bank integration to work outbound as well
as inbound, which is a second integration with its own authorization; and it returns the
grandparent's attempt at a camp contribution. **The first of those has changed kind while the refusal
stands.** Calls coming *in* are a designed thing now — a registered key, granted like any other caller
([05e](05e-keys-and-callers.md)) — so "outbound is a second integration with its own authorization" is no
which is no
longer an absence but a decision with a shape to copy. The outbound direction is answered, not
designed: an outbound call is either a named person acting or this system's own job under a label from
the fixed list, and nothing about it is built yet ([D-146](../decisions/round-20.md#d-146--an-outbound-call-is-a-persons-act-or-a-job-and-nothing-about-it-is-designed-yet),
[F-27](../open-questions.md#f-27)). The second reason was never a mechanism, and stands alone.

**Cancellation is where most of the volume comes from, and it is decided now rather than later.**
[D-064](../decisions/round-05.md#d-064--there-is-no-event-status-visibility-is-the-permission-model)
made cancellation a recorded fact rather than a state, so the event survives, the registrations
survive — and so would an outstanding request against an occasion that is not going to happen.
So:

- **Cancelling an event voids its outstanding payment requests**, recording why.
- **Money already received for a cancelled event stays where it is**, tied to the obligation that has
  stopped meaning anything, for a person to refund by hand or carry forward to a later event. It is
  not auto-refunded, for the reasons above.

**This is EV-3's answer**, which is why it is closed here rather than left parked in the events
module. What has not changed since that answer was written is the seam: **this is where the system
stops and a person begins**, and that person's next act is at the organization's bank, not on a screen
in this design
([D-158](../decisions/round-22.md#d-158--a-refund-happens-at-the-bank)).

**No page counts what nobody is looking at, and that is a cost being paid on purpose.** A transfer
aimed at a camp whose request nobody ties anything to can sit in this table forever, and nothing
anywhere distinguishes it from a grant payment nobody needed to classify — after
([D-180](../decisions/round-23.md#d-180--there-is-no-queue-for-money-that-does-not-fit)) there is no list of rows that need looking at, and after
([D-164](../decisions/round-22.md#d-164--nobody-is-told-and-no-page-may-say-otherwise)) nobody is told that money arrived. The alternative refused was a worklist whose
first entry is always a sponsorship nobody wants to classify, and a worklist nobody clears is a lie
about supervision. What makes the no-queue survivable is that the money is not lost, only
unattributed, and every row is on the same screen in date order: the payer's belief and the
organization's belief are reconciled by a person who was asked, not by a count.

---

## 3. Keeping `membership.outstanding_balance` honest

[03-membership.md](03-membership.md#3-membership) has a denormalised
`outstanding_balance`. If it stays, it must be maintained in the same transaction as any
allocation change, or it will drift. Two options:

| Option | Pros | Cons |
|--------|------|------|
| Maintain it inside the transaction that writes `payment_allocation` | Always current, no recompute | Every path that writes an allocation has to do it — the trigger that used to do it for all of them at once is gone — and the arithmetic is easy to get subtly wrong |
| Drop the column, compute on demand | Cannot drift | Slower worklist queries |
| Keep as a materialized view | Cannot drift, fast | Refresh lag |

**Recommendation:** drop the column and use a view. The "approved but unpaid" worklist is
not a hot path, and a wrong balance produces either a wrongly-suspended member or a
wrongly-chased family. A wrong number here has a human consequence.

**The definition, stated once, wherever it is implemented:**

> *balance* = `amount_due` − the sum of allocations whose payment is **`confirmed`**

The discount term left with the column it was named after ([D-183](../decisions/round-23.md#d-183--a-changed-ask-is-a-voided-request-and-a-new-symbol-and-amount_discount-goes)): a reduced fee is a
smaller `amount_due`, and a gap between what was asked and what is owed lives in the ask, not in a term
beside it.

**Only confirmed payments count.** An obligation is not settled by money that has been promised,
intended, described in an email, or reported by a payer who believes they sent it. **There is no state for
a transfer that is on its way** (D-075): either the bank has reported it and it is confirmed, or the system
has not heard of it. **A member is activated by the first, never by the second.**

---

## 4. How this connects to membership

**The activation gate.** A membership's fee is settled when **no obligation attached to it has a
positive balance after discounts**, and that is the whole test with no status excepted from it — a fee
nobody is going to collect is an obligation written with a smaller `amount_due`, so it never presents
itself as a balance to work around
([D-157](../decisions/round-22.md#d-157--there-are-no-hardship-waivers),
[D-159](../decisions/round-22.md#d-159--the-status-enum-keeps-three-of-its-seven-values)). This test
used to exclude obligations carrying `waived`, `written_off` or `refunded` outright, and every one of
those values is gone, so the exclusion would now exclude nothing — which is the way you see it was a
repair and not a rule. "Settled" is the only thing money says about membership; it
does not grant permissions by itself
([D-005](../decisions/round-01a.md#d-005--permissions-are-grants-never-derived-from-identity)).
The route from a settled fee to anything a person may do goes through a set: the fee makes
`is_current_member()` true, `is_current_member()` is what `MEMBERS` evaluates, and only a grant
whose expression names `MEMBERS` cares
([D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape))
— which is why money cannot become authority by itself.

### The yearly expiry sweep

Run on 1 January ([D-047](../decisions/round-04.md#d-047--the-fee-expires-on-1-january)).
**This is the one automatic membership transition in the system**, and the only thing in this
document that changes a person's status.

For every membership that is **active**, has an obligation with a **positive balance**, and whose
**due date has passed**:

1. Mark it **lapsed**, ending it **at the expiry date** — not at today. The period ended on that
   date whether or not anyone noticed.
2. Open the **renewal window** as a date, never as a status. The resolver does not know windows exist.

**Nothing has to be told afterwards.** `MEMBERS` is evaluated live on the checked date
([D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)),
so the two facts step 1 writes — the period ending and the `lapsed` status — are visible to the next check,
with no job in between and no stored answer to invalidate
([D-114](../decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation),
[domain/06 §8](../domain/06-authorization-model.md#8-there-is-no-permission-cache-and-what-replaces-it)).
What the sweep costs is stated where cost belongs: on 1 January the answer moves for every member at once,
and a screen opened that day computes it rather than reading it
([D-112](../decisions/round-13.md#d-112--the-systems-scale-is-stated-hundreds-of-people-tens-of-registrants-per-event)).

**Note the personnel consequence, which is easy to miss and fatal to get wrong.** This runs for
everyone at once, **including the person who runs it**, and nothing waives the membership test for a
named person: [D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)
deleted `system.gate_exempt`, `person_holds_gate_exempt` and the resolver clause behind them. The answer is
the grant text. A grant written `MEMBERS * ROLE(it)` stops applying to its holder at the sweep;
a grant written `ROLE(it)` keeps applying, because the set test is simply not in it.
*Assumption:* **which offices are written that way is not settled by D-100**, and getting it wrong
fails in the direction that locks a person out with no permission left with which to undo it — the
standing report of live grants naming a `ROLE(...)` operand without `MEMBERS` is what makes each
such choice visible before 1 January rather than on it ([03-membership.md
§6](03-membership.md#6-membership-and-the-authorization-system)).

> **The expiry is the one automatic transition in this design, and what makes it allowable is that it is
> not a decision** ([D-023](../decisions/round-01b.md#d-023--nothing-is-auto-lapsed-or-auto-terminated),
> [D-040](../decisions/round-02-03.md#d-040--the-fee-expires-yearly-a-date-tracked-renewal-window-replaces-a-grace-status)):
> the fee covers a fixed period and the period ends, and the renewal window absorbs the late-transfer case,
> because a payment inside it backdates the new period to the expiry date and the record shows no gap.
>
> **What the window cannot absorb** is a payment that *arrived* before the expiry but was *recorded*
> after it. That is a data-entry lag, not a non-payment, and it is corrected with
> `membership.backdate` rather than left as a real gap. Worth a report: members who lapsed and then paid
> within a few days.

---

## 4a. Integrity checks

**Invariants to verify.** This section arrived late and by decision
([D-135](../decisions/round-19.md#d-135--the-two-modules-with-no-check-list-get-one-each)); what it does is
not new to this folder, it is what every other page here already had. The rules below are all stated
somewhere above this heading — §2, §2a and §3 each state one and then said nothing about what would notice
a breach.

1. **The balance the system shows, recomputed from §3's definition.** `amount_due` − the sum of
   allocations whose payment is **`confirmed`**, per obligation, and the same sum rolled up
   wherever a membership's balance is displayed. Three states put a row on this list: an allocation whose
   payment has since been `reversed` still sitting in the total, an obligation whose `amount_due` was
   edited in place while a request issued at the old amount is still live — a screen and an ask that
   disagree is the state [D-183](../decisions/round-23.md#d-183--a-changed-ask-is-a-voided-request-and-a-new-symbol-and-amount_discount-goes) exists to prevent — and a roll-up summing a different set of
   allocations than the screen does. **What it cannot catch is the definition being wrong on both sides** —
   a screen and a report that each recompute `amount_due` − `amount_paid` agree perfectly and are both
   counting money that was only promised. **If §3's recommendation is taken and the column becomes a view,
   this check does not retire.** It moves from "the copy agrees with the sum" to "the view implements the
   sum", which is the same query and the same failure list, and D-075's rule that only confirmed payments
   count is what it is checking either way.
2. **A payment whose allocations do not account for its amount, and an obligation allocated past what it
   owes.** `payment_allocation` is many-to-many in both directions and §2's rules constrain the pair and the
   sign of each amount, never the sums. So a payment with unallocated remainder is money that moved and was
   never attributed to anything, and an obligation allocated beyond its `amount_due` is an
   overpayment that nobody has refunded. **The layer here is the write path, and there is no constraint to
   sit beneath it**: the sums span rows of two tables, which is
   [shape 3](00a-invariant-register.md#3-the-answer-reads-another-table-a-resolver-or-a-graph), so this
   report is not a net under a rule — it is the whole of the backstop. §2 called this table "the part most
   likely to be right", and that is an argument about the shape, not about the data ten years in.
3. **Money nobody ever asked for.** Two readings of one failure, cheapest first: an obligation still at
   `unpaid` or `partially_paid` whose `due_date` has passed with **no live `payment_request`** pointing at
   it, so nothing has ever carried a variable symbol to anybody. The two conditions are read together and
   neither is stored twice: `due_date` past plus a status that is not `paid` *is* overdue, which is why no
   status value carries it (§2)
   ([D-159](../decisions/round-22.md#d-159--the-status-enum-keeps-three-of-its-seven-values)); and
   upstream of that, an `event_registration` for an event carrying a `fee_schedule` with no
   `fee_obligation` behind it, which §2 already warned of in one sentence —
   *an event with a fee and no obligation is invisible until someone reconciles money against the roster*,
   because nothing creates the obligation and no trigger could have been forgotten. **This is not about
   money that arrived and did not fit.** An unmatched `bank_transaction` is money with no subject, most of
   it never meant for a member at all, and the design keeps it that way on purpose (§2b,
   [D-180](../decisions/round-23.md#d-180--there-is-no-queue-for-money-that-does-not-fit)). This is the other side of the same ledger: a liability with no ask
   attached, silent in both directions — nobody is chased and nobody pays. It is the one failure on this list
   that no unmatched row would ever reveal, because with no queue there is nowhere the two could meet.

**Checks 1 and 2 are the two that matter, and §3 says why in one line: a wrong number here has a human
consequence** — either a wrongly-suspended member or a wrongly-chased family. Check 3 is the one that finds
a whole class of missing money rather than a wrong row, and it is the only one of the three that can be
non-empty because a feature was never written rather than because a row is wrong.

---

## 5. Open issues — the whole of this document, essentially

**Three questions are open, and they are the three below.** Three that were here when this section last
counted itself were answered while the round was running — who may reduce a fee, whether the organization
issues invoices, and what gets a variable symbol — and each is listed at the end of the page beside the
decision that closed it.

1. **Accounting integration:** does anything need to be exported to an accounting system? **What is
   open here is the direction.** Who may call this system is designed ([05e](05e-keys-and-callers.md));
   this system calling anyone else is answered and undesigned — an outbound call is a person's act or this
   system's own job under a label from the fixed list, and no integration is built
   ([D-146](../decisions/round-20.md#d-146--an-outbound-call-is-a-persons-act-or-a-job-and-nothing-about-it-is-designed-yet), [F-27](../open-questions.md#f-27)).
2. **Jurisdiction.** This is the half of an item that used to read "currency and jurisdiction", and only
   the currency half was answerable: the currency is koruna, on all four tables that carry one (§2)
   ([D-155](../decisions/round-22.md#d-155--the-currency-is-koruna-and-the-modules-own-money-path-said-so)).
   What is left is what the law of this country asks of a fee, which this design does not know and has no
   column for: whether the invoices §2 now has a table for are compulsory rather than issued only when a
   payer asks, and whether the
   organization owes anything about its money to anybody outside itself. This is the finance module's
   share of the same sitting that already holds the four data policies in front of a legal review
   ([00-conventions §8](00-conventions.md#8-personal-data-and-erasure),
   [06b §6](06b-redaction-and-checks.md#6-open-issues)).
3. **What is a payment that does not fit?** The item this sat inside asked three questions; the first
    two are answered — **every** payable gets a symbol, and **one live request per liability**
    ([D-181](../decisions/round-23.md#d-181--every-payable-has-a-variable-symbol)). What is left is the case neither of them reaches.

    - 500 sent against a 550 request **stays unmatched**: the symbol resolves, the amount does not fit,
      and nothing settles anything on its own. That is a mechanism with no policy under it. Whether a
      partial payment settles a liability, whether 4.90 against 5.00 is a shortfall or noise, and whether
      the shortfall is what the balance should read — none of it is decided, and `payment_allocation`
      will happily hold the 500 and leave the row at `partially_paid` forever.
    - **And nobody finds out.** Nothing sends anything to anyone ([D-164](../decisions/round-22.md#d-164--nobody-is-told-and-no-page-may-say-otherwise)), and after
      [D-180](../decisions/round-23.md#d-180--there-is-no-queue-for-money-that-does-not-fit) there is no list of unmatched rows for a person to notice it on. So *finds out*
      means somebody telephoning the payer because they were asked to, which is a procedure and not a
      design. The volume arrives the first spring the fetch runs, on a screen in date order, where it
      looks exactly like the sponsorship payments that were never supposed to match anything.

    **Why this is not a footnote:** it is the one place the module can still end up with two money paths —
    the automatic one, and a hand-corrected one running beside it. §2b is the hand half already; this
    question decides how wide it gets.

**What this section used to ask, and where each answer lives.** The list below now runs to nine items. They are kept here in one line each, because for most
of them this page is the only place the question was ever written:

- **The fee amount** — the question this page asserted twice and never filed, which is why nothing could
  ever have closed it. Filed now as item 12 of the old numbering and answered in the same act: one live
  price, edited in place, and the amount a person owes is the number written on their obligation
  ([D-161](../decisions/round-22.md#d-161--one-live-price-and-the-amount-is-filed-as-a-question-at-last)).
- **Is the fee prorated for mid-year joins** — no rule. Someone joining in October gets an `amount_due`
  of whatever the person opening it writes, and the renewal twelve months later is written by the same
  kind of act. Nobody will be able to point at a rule and say this organization prorates, or refuses to
  ([D-160](../decisions/round-22.md#d-160--no-proration-rule-and-the-row-is-the-amount)).
- **Who may authorize a refund** — nobody, because nothing is initiated here. The transfer goes out at
  the bank; what arrives here is a `payment` naming whoever recorded it
  ([D-158](../decisions/round-22.md#d-158--a-refund-happens-at-the-bank)).
- **Does the fee cover insurance** — it does not. No date in this system is evidence of cover, so the
  retention question that would have followed from one never arrives, and the softer "still covered
  during grace" reading D-040 rejected was about a thing that does not exist
  ([D-156](../decisions/round-22.md#d-156--the-fee-buys-nothing-but-membership)).
- **Scholarships and hardship waivers** — no mechanism, at any level of granularity. What this item used
  to be hard about was that a waiver had to be visible to few people and invisible to the rest, with only
  which codes exist standing between the two; the problem is dissolved rather than solved, because there
  is nothing to see
  ([D-157](../decisions/round-22.md#d-157--there-are-no-hardship-waivers)).
- **Family and sibling discounts** — there is no discount column to grant one with. `amount_discount` is
  deleted and a reduced fee is an `amount_due` written smaller, which is the same act that writes any other
  amount and leaves no mark that a reduction happened; **no report will ever count what that discretion was
  used for** ([D-183](../decisions/round-23.md#d-183--a-changed-ask-is-a-voided-request-and-a-new-symbol-and-amount_discount-goes)).
- **Invoicing** — an invoice is a document a payer asks for: its own table, its own sequence, no state,
  and a `payment_request` still is not one ([D-187](../decisions/round-23.md#d-187--an-invoice-is-a-document-a-payer-asks-for)). What the law requires of one is item 2.
- **What gets a variable symbol, and one per what** — every payable, one live request per liability, never
  per person and never per person-year. The remainder of that item is open issue 3 above
  ([D-181](../decisions/round-23.md#d-181--every-payable-has-a-variable-symbol)).
- **Payment methods, and collecting rather than recording** — both closed earlier by
  [D-075](../decisions/round-06.md#d-075--money-arrives-from-a-bank-api-a-payment-is-requested-by-variable-symbol-and-qr-code).
  `bank_transfer` arrives by import and `cash` is recorded by hand; `voucher` and `credit_note` stay in
  the enum until somebody says otherwise; there is no card and no direct debit (§2). What remained in
  those two items was maintenance, not a decision.

**The count, recounted.** **Three questions are open**: the accounting export, jurisdiction, and what a
payment that does not fit settles. The number this section printed was **nine
remaining open**, and nine was right, while the list printed underneath it named **seven** of those nine and
counted the variable-symbol item twice — eight printed, with *who may authorize a refund* and *currency*
missing, which are the two this round closed. A summary that is right above a list that is wrong is worse than a
wrong summary: the summary is what a reader quotes, and the list is what a reader answers from. The claim at the top of this document, repeated in §1, that the fee
*amount* is unanswered named a question that was not on the list either, so it had to be filed before
anything could answer it. A count next to a sentence is a claim, and the count was the part nobody had
checked.

**None of the three is architectural.** The architecture is why they can be left open: how money arrives,
how it is requested, and what happens to money that does not match are all decided, so what remains is
**policy that requires somebody in the organization to be asked** — discounts, invoices, the accounting
export, jurisdiction, and the choices item 5 names. *This document does not need a rewrite; it needs
answers.*

**None of the three is registered in [the open-questions register](../open-questions.md),** and this page is why:
the register's finance row reports a number of open questions and names none of them, so a reader who
never opens this document finds no finance question at all. The questions settled along the way —
activation on payment, the flat per-person fee, the absence of a household grouping, collecting rather
than recording — are registered there with the decision that settled each, and nothing else on this page
is. The three above are the finance module's own open issues until somebody registers them or says here why
not. One finance question *is* registered now, and it arrived this round: [K-10](../open-questions.md#k-10--are-the-money-permission-codes-still-deferred).
This module's permission codes — `fee.view`, `fee.create`, `payment.view`, `payment.record`,
`payment.reverse`, `report.finance.view`, and now `payment.match` and `invoice.issue` — are listed in
[the catalog's deferred namespaces](../appendix/permission-catalog-b-roles-and-open-issues.md#10-deferred-namespaces),
which is the page for a namespace whose module does not exist yet, and this module's money already moves
([D-182](../decisions/round-23.md#d-182--matching-money-is-a-code-of-its-own-and-the-automatic-half-is-systembank-pulls)).
