# Data Model — Fees and Payments

> ## ⚠ PROVISIONAL ON POLICY, SETTLED ON ARCHITECTURE
>
> **How money moves is now decided.** Money arrives from a **bank API** and is requested by a
> **variable symbol and a QR code**
> ([D-075](../decisions/decision-log.md#d-075--money-arrives-from-a-bank-api-a-payment-is-requested-by-variable-symbol-and-qr-code));
> money that cannot be matched **waits for a person**
> ([D-076](../decisions/decision-log.md#d-076--money-that-cannot-be-matched-waits-for-a-person)).
> There is no card gateway, no checkout and no dispute handling, and §2a is the consequence.
>
> **What the money is for is still open.** Amount, proration, discounts, whether the fee buys
> insurance, and who may waive it are all unanswered — §5. Those are policy questions this
> document cannot answer, and several need somebody in the organization to be asked.
>
> This document exists because membership activation depends on payment
> ([../domain/05-membership-lifecycle.md](../domain/05-membership-lifecycle.md#1-the-flow-you-described)),
> and because the yearly expiry and renewal window
> ([D-040](../decisions/decision-log.md#d-040--the-fee-expires-yearly-a-date-tracked-renewal-window-replaces-a-grace-status))
> need somewhere to read a due date from.

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

**Unspecified** — the fee *amount*, proration, family discounts, who may authorize a waiver,
whether the fee buys insurance, and currency.

**Settled in round 6, and it was the big one** — the organization **collects**, but not through
a card gateway: money is requested by **variable symbol + QR code** and **arrives from the bank
API** already tagged (§2a, [D-075](../decisions/decision-log.md#d-075--money-arrives-from-a-bank-api-a-payment-is-requested-by-variable-symbol-and-qr-code)).

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

**`org_unit_id` is deleted with the units**
([D-097](../decisions/decision-log.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)),
and what it was for is the part worth keeping on the record. The column was optional, `NULL` meant
organization-wide, and it existed so that one body could carry *a supplementary fee above the
organization's*. Nobody ever asked for one:
[D-095](../decisions/decision-log.md#d-095--units-carry-no-restrictions-joining-one-is-somebody-elses-act)
had already ruled that entry below the membership carries no money — *"into the sub-units, there is
no fee"* — so the column was a possibility no answer had taken, and round 10 deleted both the column
and the bodies it could have pointed at. **A fee is now what it has always been charged as: flat,
per person, at the unit**
([D-037](../decisions/decision-log.md#d-037--exactly-one-membership-type-the-fee-is-flat-and-per-person)).
What a schedule may still vary is the membership type — one row, so nothing in practice — and the
period during which that price was the price. If a group ever needs a charge of its own, that is a
policy question for §5 and a new shape of obligation, not a column to keep reserved against a table
that no longer exists.

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
| `event_registration_id` | reference to event registration, optional | One of the three target columns. The event arm is real, not a hedge: an event with a `fee_schedule` creates one obligation per registration (D-066), and payment confirms the place. It replaced the dormant `household_id` arm that D-057 removed — same shape, but with data behind it this time |
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

> **The household arm is gone, and an event arm took its place — a real one.** [D-037](../decisions/decision-log.md#d-037--exactly-one-membership-type-the-fee-is-flat-and-per-person)
> settled the fee as flat and per person; [D-057](../decisions/decision-log.md#d-057--household-is-removed)
> then removed the `household` table itself, so `household_id`, its CHECK arm and
> `ix_obligation_household` went with it. Events then supplied a third target that is
> genuinely used: one obligation per registration, created by the code that places the
> registration, paid to confirm the place. **Nothing creates it if that code is not written** — the
> obligation used to be created by a database trigger, and a trigger could not be forgotten; see
> [00-conventions §6a](00-conventions.md#6a-who-enforces-an-invariant-now). An event with a fee and
> no obligation is invisible until someone reconciles money against the roster. ([D-066](../decisions/decision-log.md#d-066--payment-confirms-the-place-and-the-release-deadline-is-the-one-automatic-transition)).
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
> What is worth keeping from this rule's history is its **shape**: the previous version admitted
> *at most two* of the three, because one of the arms was a dormant `household_id` kept against a
> hypothetical. At most two with a hedge is not the same domain as exactly one over three real
> targets, and the difference
> only shows up when someone adds a fourth: **if a new target appears, ask whether it is *used*
> before widening this, and expect the answer to be no.**
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
| `method` | text, required | One of: `bank_transfer`, `cash`, `voucher`, `credit_note`, `other`. **`card` and `direct_debit` removed** — there is no card gateway and no mandate system ([D-075](../decisions/decision-log.md#d-075--money-arrives-from-a-bank-api-a-payment-is-requested-by-variable-symbol-and-qr-code)) |
| `variable_symbol` | text, optional | The symbol the money arrived under, copied verbatim from the bank statement. Set on every row the import created; the join back to `payment_request`. **Never typed by hand** |
| `reference` | text, optional | Bank reference, transaction id, receipt number |
| `paid_by_person_id` | reference to person, optional | Who actually paid. May differ from the person the fee is for — a parent paying for a child, a grandparent paying for a grandchild, a sponsor. This is the act-on-behalf record for money |
| `on_behalf_of` | reference to person, optional | |
| `status` | text, required | Default `confirmed`. **`confirmed` or `reversed`, and nothing else.** A bank transfer the bank has reported does not later fail, expire, or get reversed by a card network; the two remaining values describe whether *we* still stand behind the row. `pending` and `failed` were deleted with the card gateway ([D-075](../decisions/decision-log.md#d-075--money-arrives-from-a-bank-api-a-payment-is-requested-by-variable-symbol-and-qr-code)) |
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

[D-075](../decisions/decision-log.md#d-075--money-arrives-from-a-bank-api-a-payment-is-requested-by-variable-symbol-and-qr-code).
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

**The renewal window stops being a promise.** [D-040](../decisions/decision-log.md#d-040--the-fee-expires-yearly-a-date-tracked-renewal-window-replaces-a-grace-status)
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

[D-076](../decisions/decision-log.md#d-076--money-that-cannot-be-matched-waits-for-a-person).

**An unmatched transaction is a fact with no subject, so the absence gets stored rather than
guessed at** — the same discipline as "unanswered is the absence of a row"
([D-059](../decisions/decision-log.md#d-059--unanswered-is-the-absence-of-a-row-a-registration-stores-two-values)).
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
| **Refund** it, by hand | Nothing was meant to be owed. A second payment in the opposite direction ([D-075](../decisions/decision-log.md#d-075--money-arrives-from-a-bank-api-a-payment-is-requested-by-variable-symbol-and-qr-code)) |

**Why the tempting shortcut is refused.** Falling back to the payer's identity when the symbol
fails looks like it removes most of the queue. It removes most of the queue's *accuracy* instead:
*a parent with two children pays one amount against one symbol* is the normal case, not the edge
case, and an identity fallback resolves it to whichever child the query reaches first. **A fee
recorded against the wrong child is a finance error, a membership that appears paid when it is
not, and — if the fee buys insurance — a coverage record that is untrue, all at once.** A fallback
is not allowed to be wrong on the common path.

Auto-refunding is refused for two reasons: it needs the bank integration to work outbound as well
as inbound, which is a second integration with its own authorization; and it returns the
grandparent's attempt at a camp contribution.

**Cancellation is where most of the volume comes from, and it is decided now rather than later.**
[D-064](../decisions/decision-log.md#d-064--there-is-no-event-status-visibility-is-the-permission-model)
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
intended, described in an email, or reported by a payer who believes they sent it. Under D-075
this rule got sharper rather than weaker: `pending` is gone from `payment.status`, so there is no
longer a state for a transfer that is on its way — either the bank has reported it and it is
confirmed, or the system has not heard of it. **A member is activated by the first, never by the
second.**

---

## 4. How this connects to membership

**The activation gate.** A membership's fee is settled when **no obligation attached to it has a
positive balance after discounts** — where obligations carrying `waived`, `written_off` or
`refunded` are excluded from the question entirely, because a waived fee that nobody is going to
collect must not read as an unpaid one. "Settled" is the only thing money says about membership; it
does not grant permissions by itself
([D-005](../decisions/decision-log.md#d-005--permissions-are-grants-never-derived-from-identity)).
What changed in round 10 is the route from a settled fee to anything a person may do: the fee makes
`is_current_member()` true, `is_current_member()` is what `MEMBERS` evaluates, and only a grant
whose expression names `MEMBERS` cares
([D-100](../decisions/decision-log.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape))
— which is one step longer than the old resolver clause and one place less where money could quietly
become authority.

### The yearly expiry sweep

Run on 1 January ([D-047](../decisions/decision-log.md#d-047--the-fee-expires-on-1-january)).
**This is the one automatic membership transition in the system**, and the only thing in this
document that changes a person's status.

For every membership that is **active**, has an obligation with a **positive balance**, and whose
**due date has passed**:

1. Mark it **lapsed**, ending it **at the expiry date** — not at today. The period ended on that
   date whether or not anyone noticed.
2. **Invalidate the permission cache per person, for every person returned** — not per scope
   ([domain/06 §8](../domain/06-authorization-model.md#8-caching-and-the-rebuild-that-replaced-invalidation)). A lapsed member
   whose gated grants still resolve is a member who keeps leading. **The step survives the deletion
   of the gate that motivated it, and the reason changed**: there is no resolver clause to
   invalidate any more, but `MEMBERS` is evaluated live on the checked date
   ([D-100](../decisions/decision-log.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)),
   so a membership transition still changes who every gated grant reaches.
   [D-101](../decisions/decision-log.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree)
   lets a cache key on an operand rather than a person, which makes this event *one* invalidation of
   the `MEMBERS` operand — cheaper, and no less mandatory.
3. Open the **renewal window** as a date, never as a status. The resolver does not know windows exist.

**The old step 2 was the root `unit_participation` row** — *do not close it, move its `valid_to`
forward, so that a renewal inside the window extends one continuous row rather than starting a
second one*
([D-050](../decisions/decision-log.md#d-050--a-renewal-inside-the-window-extends-the-existing-root-participation-row),
[03-membership.md §5](03-membership.md#5-unit_participation--deleted-by-d-097)). **It is deleted rather than folded
into the steps above**
([D-097](../decisions/decision-log.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)),
and this is written down so the sweep's meaning cannot drift silently: the row it edited does not
exist, so there is nothing to extend and no second record of the person's presence to keep in step
with the first. **Nothing else in the sweep changed.** Step 1 still writes the only data this job
produces, the backdated renewal period the extension used to mirror is still produced by the payment
rule above it, and the renewal window is still a date. Had the step simply been dropped from the
list, the sweep would read as a job that had always had three steps, and nobody could ask what
became of the fourth.

**Note the personnel consequence, which is easy to miss and fatal to get wrong.** This runs for
everyone at once, **including the person who runs it.** Until round 10 the answer was
`system.gate_exempt`
([D-051](../decisions/decision-log.md#d-051--the-membership-gate-is-waived-by-a-permission-not-only-by-a-role-flag)):
a permission that waived the membership test for named people, so the administrator kept their
access on 1 January. **That mechanism is deleted**
([D-100](../decisions/decision-log.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape))
— no `system.gate_exempt`, no `person_holds_gate_exempt`, no resolver clause to waive. The answer is
now the grant text: a grant written `MEMBERS * ROLE(it)` stops applying to its holder at the sweep,
and a grant written `ROLE(it)` keeps applying, because the set test is simply not in it.
*Assumption:* **which offices are written that way is not settled by D-100**, and getting it wrong
fails in the direction that locks a person out with no permission left with which to undo it — the
standing report of live grants naming a `ROLE(...)` operand without `MEMBERS` is what makes each
such choice visible before 1 January rather than on it ([03-membership.md
§6](03-membership.md#6-membership-and-the-authorization-system)).

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
   that is fair is a policy question; whether the data model supports it is `amount_due` vs
   `amount_expected`.
2. **Are there family/sibling discounts?** `amount_discount` exists but the rules are
   unspecified. With a flat per-person fee ([D-037](../decisions/decision-log.md#d-037--exactly-one-membership-type-the-fee-is-flat-and-per-person)),
   this is the only remaining fee variation, so it is worth a deliberate yes or no. Note
   that [D-057](../decisions/decision-log.md#d-057--household-is-removed) has now removed the
   `household` grouping, so a **per-family** discount is no longer a constraint change — it
   needs that grouping designed again first. A **per-person** discount is unaffected and is
   just `amount_discount`.
3. ~~**Refunds:** policy, and who may authorize them. Affects the `payment.status` values.~~
   **Mostly answered by [D-075](../decisions/decision-log.md#d-075--money-arrives-from-a-bank-api-a-payment-is-requested-by-variable-symbol-and-qr-code):**
   a refund is a second payment in the opposite direction, not a status, so it cannot corrupt the
   original record and there is no reversal state to authorize. **Still open: who may authorize
   initiating one**, which is the part the question was actually about and which `fee.refund`
   already flags 🔒.
4. ~~**Payment methods:** which does the organization actually accept? The enum is a guess.~~
   **Closed** — `bank_transfer` arrives by import, `cash` is recorded by hand, and `card` plus
   `direct_debit` are deleted (§2). `voucher` and `credit_note` stay until someone says otherwise.
5. **Invoicing:** does the organization issue invoices (legal requirement in some
   jurisdictions)? If so, an `invoice` entity and a numbering sequence are needed. **Sharper now:**
   a `payment_request` looks like an invoice, prints like one, and is not one — it has no
   tax identity, no sequence required by law, and no delivery record. If invoices are legally
   required, the honest answer is a second document over the same obligation, not a renaming of
   this one.
6. ~~**Is the organization collecting payments or only recording them?**~~ **Closed** — it collects,
   by bank API with a variable symbol and a QR code, and there is **no card gateway**
   ([D-075](../decisions/decision-log.md#d-075--money-arrives-from-a-bank-api-a-payment-is-requested-by-variable-symbol-and-qr-code),
   §2a). The renewal window's dependence on reliable payment dates is what made this urgent, and the
   bank import is what resolved it.
7. **Accounting integration:** does anything need to be exported to an accounting system?
8. **Currency and jurisdiction** — currently assumed `EUR`.
9. **Does the fee cover insurance?** If so, "member on the date of the incident" becomes a
   legal record with its own retention needs. This one interacts directly with the new
   lapse rule ([D-040](../decisions/decision-log.md#d-040--the-fee-expires-yearly-a-date-tracked-renewal-window-replaces-a-grace-status)):
   if the fee buys insurance, then **the date the membership lapses is the date cover
   ends**, and the renewal window does *not* extend it. That is worth confirming with
   whoever handles the policy, because the softer "still covered during grace" reading was
   the alternative D-040 explicitly rejected.
10. **Scholarships/hardship waivers** — a `waived` status exists but the process is unspecified, and
    in a
    youth organization this is often a sensitive, need-to-know process that must not be visible to
    every adult who runs a group. **This got harder in round 10 rather than easier, and it is the
    finance module's share of
    [D-097](../decisions/decision-log.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)'s
    first loss.** With no units there is no smaller scope a waiver can live inside: a `fee.view`
    held at the unit reaches every person's money, because after D-097 there is nothing between the
    unit and an item except the items themselves. What separates a hardship waiver from general
    visibility is now only **which codes exist and who holds them** — `fee.view` against
    `fee.waive`, plus the deny effect
    ([D-099](../decisions/decision-log.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)),
    which can exclude a named person from a unit grant but cannot carve a private subset out of one.
    Worth a deliberate answer rather than a shrug.
11. **What gets a variable symbol, and one per what?** — **new, and raised by
    [D-075](../decisions/decision-log.md#d-075--money-arrives-from-a-bank-api-a-payment-is-requested-by-variable-symbol-and-qr-code)
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

**Resolved and no longer open**, kept visible so the reasoning survives: activation on
payment or on approval (on payment — [D-040](../decisions/decision-log.md#d-040--the-fee-expires-yearly-a-date-tracked-renewal-window-replaces-a-grace-status));
whether the fee is per person or per household (per person, flat and ageless —
[D-037](../decisions/decision-log.md#d-037--exactly-one-membership-type-the-fee-is-flat-and-per-person));
and whether the household grouping survives at all (**no** — removed entirely,
[D-057](../decisions/decision-log.md#d-057--household-is-removed)); and, from round 6, whether the
organization collects or records (**collects**, by bank API — D-075) and what payment methods exist
(the enum is no longer a guess — D-075 again).

**Count honestly, because the number moved in both directions.** Of the eleven above, **two are
fully closed** (4, 6) and **one is half closed** (3: the mechanics of a refund are settled, the
authority to initiate one is not). But **a new one arrived** in the same round, because D-075 fixed
how money moves and thereby exposed what it moves *for* — question 11. And D-057 did not close
question 2: with no grouping, a *per-family* discount needs one designed again before it can be
priced. **Nine open questions, of which one is new and one got sharper by being answered.**

**The character of the list changed, and that is the real outcome.** Until round 6 it held
architectural questions — collect or record, which gateway, what statuses. It now holds only
**policy questions that require somebody in the organization to be asked**: proration, discounts,
insurance, waivers, invoices, accounting. *This document no longer needs a rewrite; it needs
answers.*

All tracked in [../open-questions.md](../open-questions.md).
