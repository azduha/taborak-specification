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
> **What the money is for is still open.** Amount, proration, discounts, whether the fee buys
> insurance, and who may waive it are all unanswered — §5. Those are policy questions this
> document cannot answer, and several need somebody in the organization to be asked.
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

**Unspecified** — the fee *amount*, proration, family discounts, who may authorize a waiver,
whether the fee buys insurance, and currency.

**Settled, and the big one** — the organization **collects**, but not through
a card gateway: money is requested by **variable symbol + QR code** and **arrives from the bank
API** already tagged (§2a, [D-075](../decisions/round-06.md#d-075--money-arrives-from-a-bank-api-a-payment-is-requested-by-variable-symbol-and-qr-code)).

---

## 2. Minimal provisional shape

Four tables, deliberately small and easy to replace.

**`fee_schedule`** — a price, together with the period during which that price was the price.

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
| `currency` | three-letter currency code, required | Default `EUR`. Explicit even though the organization is single-currency — multi-currency later is far easier with the column already present |
| `valid_from` | date, required | Fee amounts change yearly, so a price is stored against a validity period rather than overwritten |
| `valid_to` | date, optional | `NULL` = still the current price. Storing the amount this way means a historical obligation can be recomputed correctly — critical for "what did we charge in 1998?" and for correcting a mis-applied fee |
| `is_active` | boolean, required | Default true |
| `created_at` | timestamp, audit time | |
| `created_by` | reference to person, optional | |

**Nothing on a schedule is scoped to a body.** A `fee_schedule` is scoped to a membership type — one row,
so nothing in practice — and to the period during which that price was the price. **A fee is what it has
always been charged as: flat, per person, at the unit**
([D-037](../decisions/round-02-03.md#d-037--exactly-one-membership-type-the-fee-is-flat-and-per-person)).
**Why nothing narrower:** [D-095](../decisions/round-09.md#d-095--units-carry-no-restrictions-joining-one-is-somebody-elses-act)
had already ruled that entry below the membership carries no money — *into the sub-units, there is no fee* —
so a supplementary fee for one body was a possibility no answer ever took. If a group ever needs a charge of
its own, that is a policy question for §5 and a new shape of obligation, not a column to hold in reserve.

**Rules**

- `code` is unique. It covers all rows, not only active ones.
- `valid_to` is either absent or later than `valid_from`.
- `amount` is zero or more.

**Indexes**

- The one lookup that matters is "the schedules for one membership type, `valid_from`
  newest first, restricted to active ones".

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
| `amount_due` | money, required | |
| `amount_discount` | money, required | Default 0 |
| `amount_paid` | money, required | Default 0 |
| `currency` | three-letter currency code, required | |
| `status` | text, required | Default `unpaid`. One of: `unpaid`, `partially_paid`, `paid`, `waived`, `refunded`, `written_off`, `overdue` |
| `due_date` | date, required | The yearly fee expires on a fixed organizational date (D-040); this obligation's `due_date` is what the lapse sweep compares against (§4). The renewal window that follows is carried as dates, not as a status (§1) |
| `waived_by` | reference to person, optional | |
| `waived_reason` | text, optional | |
| `created_at` | timestamp, audit time | |
| `created_by` | reference to person, optional | |
| `updated_at` | timestamp, audit time | |
| `updated_by` | reference to person, optional | |
| `import_batch_id` | reference to import batch, optional | Set on imported rows |

**Rules**

- `period_to` is later than `period_from`.
- `amount_due`, `amount_discount` and `amount_paid` are each zero or more.
- Exactly one of `membership_id`, `membership_request_id` and `event_registration_id` is
  set — one, not zero and not two. Every obligation is for exactly one thing: a membership
  period, a membership request, or one person's place at one event. The per-person choice
  for events is deliberate: the fee is flat and per person (D-037), and a per-family price
  would need the household grouping designed again first (D-057).
- A status of `waived` requires both `waived_by` and `waived_reason`. There is no waived
  obligation whose waiver is unattributed or unexplained.

**Indexes**

- One person's obligations, by status.
- Obligations ordered by `due_date`, restricted to the rows still open — status `unpaid`,
  `partially_paid` or `overdue`. Closed rows are not in it.
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
> deleted genuinely cannot be restated declaratively ([open question
> F-10](../open-questions.md#f-10--which-invariants-the-orm-cannot-express-and-who-writes-those)),
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
| `amount` | money, required | Never zero. A negative amount represents a reversal |
| `currency` | three-letter currency code, required | |
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
| `import_batch_id` | reference to import batch, optional | Set on imported rows |
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
2. The system issues a **`payment_request`** carrying a **variable symbol** and an amount.
3. The payer is shown the symbol, the amount, and a **QR code** that encodes all three.
4. The payer's own bank moves the money. The system is not involved and learns nothing yet.
5. A **bank import** reads the account statement and produces a **`bank_transaction`** for each
   incoming transfer, with the variable symbol still attached.
6. The symbol resolves to a live request. The import creates a `payment`, links it, and the
   obligation's balance falls.
7. If the symbol resolves to nothing live, the row goes to the **queue** (§2b).

**`payment_request`** — the liability rendered payable.

**Fields**

| Field | Kind | Notes |
|---|---|---|
| `id` | surrogate id | |
| `variable_symbol` | text, required | **Unique across all rows, forever, including cancelled and long-settled ones.** Eleven digits from a sequence |
| `fee_obligation_id` | reference to fee obligation, required | What is owed. The request never invents an amount of its own |
| `amount` | money, required | Copied from the obligation at issue time, so a later price change cannot rewrite what someone was asked for |
| `currency` | three-letter currency code, required | |
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
  child's record, and the damage is not cosmetic — it reads as a paid fee, an active membership,
  and possibly insurance cover that does not exist.
- `amount` is a **copy**, not a live reference. What a person was asked to pay is a historical
  fact about the ask, and recomputing it from the current schedule would make every price change
  rewrite history.
- One obligation may have several requests over time — a first request expires, or the amount is
  corrected — but **at most one live request per obligation**.
- A request is not an invoice. Nothing is delivered, nothing is numbered for a tax authority, and
  whether the organization *also* owes people invoices is still an open question (§5).

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
| `matched_payment_request_id` | reference to payment request, optional | NULL means **unmatched**, which is the queue |
| `imported_at` | timestamp, audit time | |
| `import_batch_id` | reference to import batch, optional | |

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
`matched_payment_request_id IS NULL` *is* the queue; there is no separate worklist table to fall
out of sync with the rows it describes.

**How a transaction ends up there:** the symbol matches no request. The symbol matches a request
that has been voided. The request is already settled. The amount is less than asked, or more.
There is no symbol at all — cash-basis donors and people who type their own name in the wrong
field.

**What the system does with any of those: nothing.** It records the money and waits.

**A person decides, and there are exactly four outcomes:**

| Outcome | When |
|---|---|
| **Attach** it to a different request | The symbol was mistyped; the real obligation is obvious from the payer |
| **Split** it across requests | One transfer, three siblings — the ordinary shape of family payment here |
| **Record as a donation** | Money with no obligation behind it, which is not the same as money that is missing one |
| **Refund** it, by hand | Nothing was meant to be owed. A second payment in the opposite direction ([D-075](../decisions/round-06.md#d-075--money-arrives-from-a-bank-api-a-payment-is-requested-by-variable-symbol-and-qr-code)) |

**Why the tempting shortcut is refused.** Falling back to the payer's identity when the symbol
fails looks like it removes most of the queue. It removes most of the queue's *accuracy* instead:
*a parent with two children pays one amount against one symbol* is the normal case, not the edge
case, and an identity fallback resolves it to whichever child the query reaches first. **A fee
recorded against the wrong child is a finance error, a membership that appears paid when it is
not, and — if the fee buys insurance — a coverage record that is untrue, all at once.** A fallback
is not allowed to be wrong on the common path.

Auto-refunding is refused for two reasons: it needs the bank integration to work outbound as well
as inbound, which is a second integration with its own authorization; and it returns the
grandparent's attempt at a camp contribution. **The first of those has changed kind while the refusal
stands.** Calls coming *in* are a designed thing now — a registered key, granted like any other caller
([05e](05e-keys-and-callers.md)) — so "outbound is a second integration with its own authorization" is no
longer an absence but a decision with a shape to copy, and the outbound direction itself is
[F-27](../open-questions.md#f-27). The second reason was never a mechanism, and stands alone.

**Cancellation is where most of the volume comes from, and it is decided now rather than later.**
[D-064](../decisions/round-05.md#d-064--there-is-no-event-status-visibility-is-the-permission-model)
made cancellation a recorded fact rather than a state, so the event survives, the registrations
survive — and so would an outstanding request against an occasion that is not going to happen.
So:

- **Cancelling an event voids its outstanding payment requests**, recording why.
- **Money already received for a cancelled event becomes a queue item**, for a person to refund or
  to carry forward to a later event. It is not auto-refunded, for the reasons above.

**This is EV-3's answer**, which is why it is closed here rather than left parked in the events
module.

**The queue is not allowed to be silently ignored.** It is a count on a dashboard, not a page
nobody navigates to, and its oldest item is a number someone sees monthly. Unmatched money is the
one finance backlog that gets worse by itself: the payer believes they have paid, and the
organization believes they have not.

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

> *balance* = `amount_due` − `amount_discount` − the sum of allocations whose payment is
> **`confirmed`**

**Only confirmed payments count.** An obligation is not settled by money that has been promised,
intended, described in an email, or reported by a payer who believes they sent it. **There is no state for
a transfer that is on its way** (D-075): either the bank has reported it and it is confirmed, or the system
has not heard of it. **A member is activated by the first, never by the second.**

---

## 4. How this connects to membership

**The activation gate.** A membership's fee is settled when **no obligation attached to it has a
positive balance after discounts** — where obligations carrying `waived`, `written_off` or
`refunded` are excluded from the question entirely, because a waived fee that nobody is going to
collect must not read as an unpaid one. "Settled" is the only thing money says about membership; it
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

## 5. Open issues — the whole of this document, essentially

1. **Is the fee prorated** for mid-year joins? Note this is a sharper question than it was:
   with the expiry on a fixed date ([D-040](../decisions/round-02-03.md#d-040--the-fee-expires-yearly-a-date-tracked-renewal-window-replaces-a-grace-status)),
   someone joining in October pays for three months of a twelve-month fee unless the
   organization prorates — and the *renewal* twelve months later is a full year. Whether
   that is fair is a policy question; whether the data model supports it is `amount_due` vs
   `amount_expected`.
2. **Are there family/sibling discounts?** `amount_discount` exists but the rules are
   unspecified. With a flat per-person fee ([D-037](../decisions/round-02-03.md#d-037--exactly-one-membership-type-the-fee-is-flat-and-per-person)),
   this is the only remaining fee variation, so it is worth a deliberate yes or no. A **per-family**
   discount needs a grouping to be designed first — there is none
   ([D-057](../decisions/round-04.md#d-057--household-is-removed)) — so it is not a constraint change but a
   shape. A **per-person** discount is unaffected and is just `amount_discount`.
3. **Who may authorize a refund.** The mechanics are settled by
   [D-075](../decisions/round-06.md#d-075--money-arrives-from-a-bank-api-a-payment-is-requested-by-variable-symbol-and-qr-code):
   a refund is a second payment in the opposite direction, not a status, so it cannot corrupt the original
   record and there is no reversal state to authorize. **The authority to initiate one is not settled**, and
   it is the part this question was always about; `fee.refund` already flags it 🔒.
4. **Payment methods, settled.** `bank_transfer` arrives by import and `cash` is recorded by hand;
   `voucher` and `credit_note` are in the enum until somebody says otherwise, and there is no card and no
   direct debit (§2). What is left here is a maintenance question, not a decision.
5. **Invoicing:** does the organization issue invoices (legal requirement in some
   jurisdictions)? If so, an `invoice` entity and a numbering sequence are needed. **Sharper now:**
   a `payment_request` looks like an invoice, prints like one, and is not one — it has no
   tax identity, no sequence required by law, and no delivery record. If invoices are legally
   required, the honest answer is a second document over the same obligation, not a renaming of
   this one.
6. **Collecting, not recording — settled.** The organization collects: money arrives by bank API with a
   variable symbol and a QR code, and there is **no card gateway**
   ([D-075](../decisions/round-06.md#d-075--money-arrives-from-a-bank-api-a-payment-is-requested-by-variable-symbol-and-qr-code),
   §2a). Reliable payment dates are what the renewal window depends on, and the bank import is what
   supplies them.
7. **Accounting integration:** does anything need to be exported to an accounting system? **What is
   open here is the direction.** Who may call this system is designed ([05e](05e-keys-and-callers.md));
   this system calling anyone else is [F-27](../open-questions.md#f-27).
8. **Currency and jurisdiction** — currently assumed `EUR`.
9. **Does the fee cover insurance?** If so, "member on the date of the incident" becomes a
   legal record with its own retention needs. This one interacts directly with the
   lapse rule ([D-040](../decisions/round-02-03.md#d-040--the-fee-expires-yearly-a-date-tracked-renewal-window-replaces-a-grace-status)):
   if the fee buys insurance, then **the date the membership lapses is the date cover
   ends**, and the renewal window does *not* extend it. That is worth confirming with
   whoever handles the policy, because the softer "still covered during grace" reading was
   the alternative D-040 explicitly rejected.
10. **Scholarships/hardship waivers** — a `waived` status exists but the process is unspecified, and
    in a
    youth organization this is often a sensitive, need-to-know process that must not be visible to
    every adult who runs a group. **This got harder in round 10 rather than easier, and it is the
    finance module's share of
    [D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)'s
    first loss.** With no units there is no smaller scope a waiver can live inside: a `fee.view`
    held at the unit reaches every person's money, because after D-097 there is nothing between the
    unit and an item except the items themselves. What separates a hardship waiver from general
    visibility is now only **which codes exist and who holds them** — `fee.view` against
    `fee.waive`, plus the deny effect
    ([D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)),
    which can exclude a named person from a unit grant but cannot carve a private subset out of one.
    Worth a deliberate answer rather than a shrug.
11. **What gets a variable symbol, and one per what?** — **new, and raised by
    [D-075](../decisions/round-06.md#d-075--money-arrives-from-a-bank-api-a-payment-is-requested-by-variable-symbol-and-qr-code)
    rather than left over.** That decision fixed *how* money arrives and named the `payment_request`
    that carries it, but not the two choices the module is actually built from.

    - **Scope.** Do event fees get a symbol, or only membership fees? A camp fee is the same
      mechanism, and a symbol is what lets a family pay for it at their own bank without staff
      involvement. **Recommendation: every payable**, because the alternative is a second,
      hand-recorded money path sitting beside an automatic one — and hand-recorded is what D-040's
      renewal window just escaped.
    - **Granularity.** One live request per liability, matching the `fee_obligation` row exactly —
      which is what §2a already assumes. Not per person, because a parent paying for two children in
      one transfer is the ordinary case and per-person symbols make that impossible to match.
      **Not per person-year either**: a camp is a separate liability from a fee and must never share
      a symbol with one.
    - **The amount mismatch, which D-076 defers and this question cannot.** 500 sent against a 550
      request goes to the queue, which is correct as a mechanism and silent as a policy. Whether
      partial payment settles anything, whether 4.90 vs 5.00 is a shortfall, and what a payer is
      told when their money lands and does not fit — those are undecided, **and the queue will show
      them at volume the first spring the import runs.**

    **Why this is question 11 and not a footnote:** it decides whether the module has one money path
    or two.

**The count, honestly.** Of the eleven numbered above, **two are closed** (4, 6) and **one is half
closed** (3: the mechanics of a refund are settled, the authority to initiate one is not). **Nine remain
open.**

**None of the nine is architectural.** The architecture is why they can be left open: how money arrives,
how it is requested, and what happens to money that does not match are all decided, so what remains is
**policy that requires somebody in the organization to be asked** — proration, discounts, insurance,
waivers, invoices, accounting, and the two choices question 11 names. *This document does not need a
rewrite; it needs answers.*

The questions settled along the way — activation on payment, the flat per-person fee, the absence of a
household grouping, collecting rather than recording — are registered in
[../open-questions.md](../open-questions.md) with the decision that settled each.
