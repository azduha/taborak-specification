# Data Model — Fees and Payments

> ## ⚠ SETTLED ON ARCHITECTURE, AND NOW ON POLICY TOO
>
> **The banner's own left half has been overtaken, and it is kept here saying so.** This heading read *PROVISIONAL
> ON POLICY, SETTLED ON ARCHITECTURE* from the round that drew the money path ahead of the answers, and the
> provision it stood for was the list §5 kept. **Round 24 answered the last item on that list**, so the page is
> not provisional on policy any more — while what is genuinely still outside it is not a question a page can
> answer either: what the country requires of an invoice's contents, which this module refuses to encode
> ([D-197](../decisions/round-24.md#d-197--an-invoice-is-compulsory-so-nobody-issues-one-invoiceissue-is-deleted-and-the-asks-write-writes-it)),
> and who the issuer is, which is configuration
> ([D-198](../decisions/round-24.md#d-198--an-invoices-issuer-is-configuration-its-payers-identification-is-already-in-the-database)).
> **Cost of the retitle:** a reader who arrives from a citation of the old banner finds a different heading, which
> is the trade every renamed heading is — accepted here because a banner that says *provisional* over a page with
> nothing open is worse, it invites the reader to discount rules that are now decisions.
>
> **How money moves is now decided.** Money arrives from a **bank API** and is requested by a
> **variable symbol and a QR code**
> ([D-075](../decisions/round-06.md#d-075--money-arrives-from-a-bank-api-a-payment-is-requested-by-variable-symbol-and-qr-code));
> money that cannot be matched **is matched by nothing** — it has no request attached, it gets no subject
> assigned by a guess at an amount and a date, and it is not a queue anybody is watching
> ([D-076](../decisions/round-06.md#d-076--money-that-cannot-be-matched-waits-for-a-person),
> [D-180](../decisions/round-23.md#d-180--there-is-no-queue-for-money-that-does-not-fit),
> [D-196](../decisions/round-24.md#d-196--the-variable-symbol-is-the-whole-match-what-arrives-under-its-own-symbol-is-attached-in-full-and-the-difference-is-shown));
> **the sentence this header used to print here — that unmatched money "waits for a person" — is the picture
> [D-180](../decisions/round-23.md#d-180--there-is-no-queue-for-money-that-does-not-fit) deleted, and it survived
> that round sitting in this block quote, which is where a header goes wrong: §2b and §2a were swept and this
> summary of them was not.**
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
> **No question is left open on this page.** §5 is where this document kept its open issues and the
> last of them were answered in round 24: what money arriving under or over its ask settles is the
> symbol and nothing else ([D-196](../decisions/round-24.md#d-196--the-variable-symbol-is-the-whole-match-what-arrives-under-its-own-symbol-is-attached-in-full-and-the-difference-is-shown)),
> invoices are compulsory so nobody issues one ([D-197](../decisions/round-24.md#d-197--an-invoice-is-compulsory-so-nobody-issues-one-invoiceissue-is-deleted-and-the-asks-write-writes-it)),
> who the invoice is from is configuration and the payer's identification is already modelled
> ([D-198](../decisions/round-24.md#d-198--an-invoices-issuer-is-configuration-its-payers-identification-is-already-in-the-database)),
> and nothing leaves this system to an accounting system
> ([D-199](../decisions/round-24.md#d-199--nothing-leaves-this-system-to-an-accounting-system-and-an-external-one-is-a-later-versions-design)).
> **What is not this module's to decide shrank in round 25.** The money codes are shipped codes
> ([D-195](../decisions/round-24.md#d-195--the-money-codes-are-shipped-codes-catalog-a-grows-a-money-section-and-catalog-b-10-loses-three-rows)),
> and this module has never spent a code of reporting's: **the six codes named in §5 are the whole of what money
> answers to, and a listing over them has never been one of them.** Round 25 took the question of reporting's
> shape away rather than answering it — **there is no report screen in this design and no reporting code**, and
> what an organization calls a report over this module's money is a message of a type addressed to an audience.
> **The over-or-under payment and the late fee are the two cases [D-210](../decisions/round-25.md#d-210--a-report-is-a-delivered-message-so-all-five-report-codes-are-deleted-and-reporting-stops-being-a-name)
> names as now reaching people instead of waiting for them**
> ([10 §8](10-messaging.md#8-reports-arrive-here-and-stop-being-a-name)). §5 says what the six codes are.
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
- **Money is matched by its variable symbol and by nothing else.** A bank row whose symbol resolves to a
  live request is attached **in full**, and the amount a payer actually sent is information rather than a
  condition — under or over, it is shown and never adjudicated (§2a, §2b,
  [D-196](../decisions/round-24.md#d-196--the-variable-symbol-is-the-whole-match-what-arrives-under-its-own-symbol-is-attached-in-full-and-the-difference-is-shown)).
  This is a trade and not a cleanup: the family that pays one amount against one child's symbol now has
  all of it land on that child, and §2b says so rather than softening it.
- **Every ask has an invoice over it, and nobody is asked whether it should.** The country this
  organization is in requires the document, so the `invoice` row is written **by the same write that
  creates its `payment_request`** and there is no act of issuing left for a permission to authorize —
  `invoice.issue` is deleted (§2,
  [D-197](../decisions/round-24.md#d-197--an-invoice-is-compulsory-so-nobody-issues-one-invoiceissue-is-deleted-and-the-asks-write-writes-it)).
  The organization's half of the document's header is **deployment configuration**, the way the SMTP relay
  and the bank's credentials are, because there is no `unit` row and no `organization` table to hold it
  ([D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row),
  [D-198](../decisions/round-24.md#d-198--an-invoices-issuer-is-configuration-its-payers-identification-is-already-in-the-database)).
  **A `payment_request` is still not an invoice and does not become one** — D-187's renaming never
  happened, only its premise about a payer asking for the document went
  ([D-187](../decisions/round-23.md#d-187--an-invoice-is-a-document-a-payer-asks-for)).

**Answered, since this section last spoke — and the answers are the ones that cost something.** Nothing
is exported to an accounting system: no export, no feed, no periodic journal, and no placeholder waiting
for one; an external accounting package may appear in a later version and will be designed then, in a
document that is not this one ([D-199](../decisions/round-24.md#d-199--nothing-leaves-this-system-to-an-accounting-system-and-an-external-one-is-a-later-versions-design)).
What the law of this country asks of a fee arrived as one fact rather than as a rulebook — the document is
compulsory — and **this module encodes no jurisdiction's rules**: it produces a row whose number is never
reused, and the thing that turns that row into a filing is outside the corpus
([D-197](../decisions/round-24.md#d-197--an-invoice-is-compulsory-so-nobody-issues-one-invoiceissue-is-deleted-and-the-asks-write-writes-it),
[D-198](../decisions/round-24.md#d-198--an-invoices-issuer-is-configuration-its-payers-identification-is-already-in-the-database)).
And what a payment that does not fit its ask settles is decided: it is attached, in full, and the
difference is shown ([D-196](../decisions/round-24.md#d-196--the-variable-symbol-is-the-whole-match-what-arrives-under-its-own-symbol-is-attached-in-full-and-the-difference-is-shown)).

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
  fact stored once, with no status value to keep in step with the calendar. **Lateness is also one of the two
  money cases round 25 turned into a delivered message**, and `fee-overdue` is the code the messaging module
  lists for it ([10 §2](10-messaging.md#2-message_type--a-vocabulary-that-is-also-a-settings-panel)): the people who
  chase a late fee are reached by a type whose audience an installation edits, not by opening this index
  ([D-210](../decisions/round-25.md#d-210--a-report-is-a-delivered-message-so-all-five-report-codes-are-deleted-and-reporting-stops-being-a-name)),
  and which clock fires it is [K-14](../open-questions.md#k-14). **Whether it fires at all is that installation's
  edit** — this design ships no rows at all beyond the first account ([D-150](../decisions/round-21.md#d-150--day-one-is-one-account-holding-systemadmin-and-nothing-else-is-shipped)).
  **The index stays exactly as it was**: a send does not replace the read it is computed from, and no row of this
  table records that either one happened.
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
| `notes` | text, optional | Free text beside the money. **Erasure empties it and the row remains** — the emptied shape, not the deleted one, so the skeleton [D-088](../decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short) keeps stays intact and only the remark on it goes ([D-215](../decisions/round-25.md#d-215--the-three-notes-columns-stay-and-erasure-empties-them), listed in [06b §4](06b-redaction-and-checks.md#4-redaction-log)) |
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
| `amount` | money, required | Never zero. **May exceed the obligation's `amount_due`**, and since [D-196](../decisions/round-24.md#d-196--the-variable-symbol-is-the-whole-match-what-arrives-under-its-own-symbol-is-attached-in-full-and-the-difference-is-shown) it has a routine way to: the automatic attach writes one row carrying the *whole* transfer, and a 1 100 Kč transfer under a 550 Kč symbol allocates 1 100 to a 550 obligation. That row is not a breach and §4a says so |
| `allocated_at` | timestamp, audit time | Default: now |
| `allocated_by` | reference to person, optional | Empty on the row the automatic attach writes (§2a step 6 — the fetch is the actor, and an empty actor column is this system acting on its own, [00-conventions §7a](00-conventions.md#7a-what-an-empty-actor-column-means)); a person's name on every row a hand moved |
| `note` | text, optional | |

**Rules**

- A given payment is allocated to a given obligation at most once — one row per pair, over
  all rows.
- `amount` is never zero.
- **The sums are not constrained, and one of them is now expected to be over.** Nothing here requires an
  allocation to stop at `amount_due`, because the automatic half of §2a cannot know whether the payer meant
  the whole transfer for this child; whether the excess stays is a person's call made with `payment.match`,
  whose *split* outcome already exists for exactly this shape (§2b). The pair rule and the sign rule are
  row-local, which is why they live here and the sums live in a report (§4a,
  [shape 3](00a-invariant-register.md#3-the-answer-reads-another-table-a-resolver-or-a-graph)).

**Indexes**

- Allocations of one payment, and allocations of one obligation — both directions are asked.

**The allocation table is the part most likely to be right.** A payment and an obligation
are genuinely many-to-many, and any design that puts `payment_id` on the obligation (or
vice versa) breaks the first time a parent pays for three children in one transfer. That
is the common case in this organization, not an edge case. **D-196 left the shape alone and changed who
fills it:** the automatic half now writes one row of its own, carrying everything, and the many-to-many is
what a person uses afterwards to move the surplus to the sibling it was meant for. The shape is the reason
that correction is a split rather than a rewrite.

---

## 2a. How money actually arrives

[D-075](../decisions/round-06.md#d-075--money-arrives-from-a-bank-api-a-payment-is-requested-by-variable-symbol-and-qr-code).
The system **requests** a payment and then **reads** one. It never touches the money.

The flow, in order:

1. A liability exists — a membership period, a membership request, a place at an event.
2. The system issues a **`payment_request`** carrying a **variable symbol** and an amount, **and writes the
   `invoice` over it in the same transaction** — the document is compulsory here, so it arrives with the ask
   rather than later, and nobody is asked whether it should
   ([D-197](../decisions/round-24.md#d-197--an-invoice-is-compulsory-so-nobody-issues-one-invoiceissue-is-deleted-and-the-asks-write-writes-it)).
   Every payable gets a symbol — the yearly fee and a camp fee alike — because a liability with no symbol has
   money arriving against nothing and no list where that would show ([D-181](../decisions/round-23.md#d-181--every-payable-has-a-variable-symbol)).
3. The payer is shown the symbol, the amount, and a **QR code** that encodes all three.
4. The payer's own bank moves the money. The system is not involved and learns nothing yet.
5. A **bank import** reads the account statement and produces a **`bank_transaction`** for each
   incoming transfer, with the variable symbol still attached.
6. **The symbol resolves to a live request, and that is the whole test.** The fetch creates a `payment`,
   links it, and writes **one allocation carrying the whole amount**: what arrives under its own symbol is
   attached **in full**, and the sum the payer happened to send is never a condition of a match and never
   becomes one — it is information, and it is shown
   ([D-196](../decisions/round-24.md#d-196--the-variable-symbol-is-the-whole-match-what-arrives-under-its-own-symbol-is-attached-in-full-and-the-difference-is-shown)).
   All three rows belong to the fetch's own actor, `system:bank-pull`, because resolving a symbol is not a
   human act ([D-182](../decisions/round-23.md#d-182--matching-money-is-a-code-of-its-own-and-the-automatic-half-is-systembank-pulls)),
   and the allocation's `allocated_by` is empty for the same reason: an empty actor column is this system
   acting on its own, and its name comes from the fixed list
   ([00-conventions §7a](00-conventions.md#7a-what-an-empty-actor-column-means)). The obligation's balance
   falls by the whole amount, which is exactly what makes `partially_paid` reachable with nobody allocating
   anything, and what lets an obligation read **over** — both are §2b's trade.
7. If the symbol resolves to nothing live, the transaction stays exactly as it arrived: **unmatched,
   which is not a queue** (§2b) ([D-180](../decisions/round-23.md#d-180--there-is-no-queue-for-money-that-does-not-fit)).
   What "nothing live" covers is now the whole of the unmatched population — no symbol at all, a symbol no
   request carries, or a symbol whose request has been voided — because the amount came off that list
   ([D-196](../decisions/round-24.md#d-196--the-variable-symbol-is-the-whole-match-what-arrives-under-its-own-symbol-is-attached-in-full-and-the-difference-is-shown)).

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
- A request is not an invoice, and now has one over it every time. **The request does not *become* the
  document**: the two rows keep their own numbers and their own rows, and a request still has no tax
  identity and no delivery record. What changed is that the invoice is no longer something somebody
  produces later — it is written by the same write that created this request, in the same transaction, so
  there is never a moment in which a request exists and is missing its document
  ([D-197](../decisions/round-24.md#d-197--an-invoice-is-compulsory-so-nobody-issues-one-invoiceissue-is-deleted-and-the-asks-write-writes-it)).
  Nothing is still delivered, and nothing here claims to have delivered anything
  ([D-164](../decisions/round-22.md#d-164--nobody-is-told-and-no-page-may-say-otherwise)).

**`invoice`** — the document every ask has. There is no state of *awaiting one*, because there is nobody
who could be asked: the country this organization is in requires the row, so it is written with its
request ([D-197](../decisions/round-24.md#d-197--an-invoice-is-compulsory-so-nobody-issues-one-invoiceissue-is-deleted-and-the-asks-write-writes-it)).
**Which write, since there is no code for it:** `fee.create` writes the obligation and the request over it,
and the invoice joins that same write — one transaction, one actor, one audit payload covering both rows —
so this module still has no money row whose write is ungated. `invoice.issue` is **deleted**, and what
replaced it is that write rather than a hole in the vocabulary: there is no screen offering a choice about
producing a document, and **a permission nobody can decline is not a permission**.

**Where the header comes from, since no table holds it.** The issuer's half — the organization's name,
address, IČO, DIČ and bank account — is **deployment configuration**, arriving the way the SMTP relay and
the bank's API credentials arrive and named nowhere in the schema. There is no `unit` row to hold them
([D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)) and there
is no `organization` table, and adding one in order to print a header would be
[D-177's](../decisions/round-23.md#d-177--the-list-of-login-methods-is-written-in-the-program) refusal for
login methods repeated: a value with one legal value, one installation, and no screen that writes it.
**Write that down, or an implementer will invent a settings table that this design has refused.** The
payer's half is already modelled and is rows: [`domain/02`](../domain/02-actors.md#external-identifiers)
makes `person_identifier` a `(scheme, value)` pair, unique among current identifiers, and a business
payer's IČO and DIČ are **schemes, not columns** — the invoice reads rows that were designed, for a
completely different reason, before this question was asked ([D-198](../decisions/round-24.md#d-198--an-invoices-issuer-is-configuration-its-payers-identification-is-already-in-the-database)).
**The cost is stated rather than discovered:** an installation with two legal entities cannot have them
both, because the issuer is one set of configuration values and there is no row to choose between. That is
[D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row) made concrete
for the first time — **this design supports one organization**, and it now says so at the one place where
being two would have shown up in the data.

| Field | Kind | Notes |
|---|---|---|
| `id` | surrogate id | |
| `number` | text, required | **Unique, and never reused.** Its own sequence, beside the variable symbol's and independent of it: a symbol resolves a payment to an ask, a number identifies a document to a tax authority, and nothing promises the two agree ([D-187](../decisions/round-23.md#d-187--an-invoice-is-a-document-a-payer-asks-for)). **That sequence is legally required now, not merely tidy:** unique-and-never-reused was hygiene when a document was a courtesy and is a legal fact now that one is compulsory, which is the one clause of D-187's "no tax identity, no legally-required sequence, no delivery record" that changed meaning — the request still has no tax identity and no delivery record, and no delivery of a document is designed here — sending words became possible in round 25 and a tax document was not given a type ([D-197](../decisions/round-24.md#d-197--an-invoice-is-compulsory-so-nobody-issues-one-invoiceissue-is-deleted-and-the-asks-write-writes-it), [D-214](../decisions/round-25.md#d-214--the-system-sends-and-d-164-is-narrowed-to-the-one-thing-it-was-protecting)) |
| `payment_request_id` | reference to payment request, required | The ask it documents. Never a bare obligation, because the request is what the payer was shown |
| `amount` | money, required | Copied from the request, for the same reason the request copies it from the obligation: an edit to the liability must not rewrite a document that has already been handed over ([D-183](../decisions/round-23.md#d-183--a-changed-ask-is-a-voided-request-and-a-new-symbol-and-amount_discount-goes)) |
| `currency` | three-letter currency code, required | `CZK` |
| `issued_at` | timestamp, required | The moment `fee.create` wrote this row and its request, read off that write. Not a second timestamp a person sets, because there is no second write |
| `issued_by` | reference to person, required | The actor of the `fee.create` write that created this request — not a second hand, and not the payer, because there is no row for the asking. **This is the loss D-197 names rather than hides:** D-187 kept the issuing code apart from `payment.match` *"so that the person who can settle a transfer is not automatically the person who can sign a tax document"*, and catalog B repeated it. **That separation is gone.** Whoever holds `fee.create` produces tax documents as a side effect of recording what somebody owes, and no code, no check and no report distinguishes the two acts. The control left is the one [D-188](../decisions/round-23.md#d-188--the-ceiling-reads-a-grant-and-nothing-else-and-what-it-leaves-open-is-written-down) left standing everywhere else in this vocabulary: `fee.create` is rare because somebody granted it, once, in the open |

**Rules**

- **No state.** No `requested`, no `sent`, no `delivered` — the sentence survives word for word, now for
  the stronger reason that **there is no moment at which a document could be missing**. D-187's argument is
  why the column was never drawn and is worth keeping: a column meaning *somebody owes this person a
  document*, with nobody assigned to it and nothing counting it, is the queue this module deleted wearing a
  different coat ([D-180](../decisions/round-23.md#d-180--there-is-no-queue-for-money-that-does-not-fit)).
  Compulsory invoicing does not add that column and does not need one, because **it deletes the debt** —
  and what precedes the row is no longer a conversation with the payer but the same write that created the
  request, which is in the audit trail rather than in a column
  ([D-197](../decisions/round-24.md#d-197--an-invoice-is-compulsory-so-nobody-issues-one-invoiceissue-is-deleted-and-the-asks-write-writes-it)).
- **Nothing delivers the invoice to anybody, and the reason is now a missing row rather than a missing
  mechanism.** Round 25 opened [the messaging module](10-messaging.md), so this design can carry words to a
  person; what it has not been told to carry is a tax document. **No message type is configured for an invoice
  and nobody has configured one** ([D-214](../decisions/round-25.md#d-214--the-system-sends-and-d-164-is-narrowed-to-the-one-thing-it-was-protecting)
  narrows [D-164](../decisions/round-22.md#d-164--nobody-is-told-and-no-page-may-say-otherwise): a page may no
  longer write that nothing *can* be sent, and may still not write a send or a period nobody chose), so the
  document exists on a screen and is handed over by a person, or printed by one. **Everything after this row is
  outside the system in the same way:** getting the document to the payer, filing it, reporting it and
  reconciling it with an accountant are acts this system does not perform, does not record having performed, and
  holds no column claiming it performed
  ([D-198](../decisions/round-24.md#d-198--an-invoices-issuer-is-configuration-its-payers-identification-is-already-in-the-database)).
  D-164 already forbade writing the first of those as if the system did it; D-198 forbids the *schema* implying
  it — and **that half is untouched by the round that opened sending**, because a type is a row an installation
  writes ([10 §2](10-messaging.md#2-message_type--a-vocabulary-that-is-also-a-settings-panel)) and no column of
  this table may hold a delivery.
- A voided request keeps its invoice. Both rows are permanent — and this now **fires on every reissue**
  instead of almost never, because a changed ask is a void plus a new request (§2) and each reissue carries
  a document of its own. The reissued ask gets a new invoice with a fresh number from the same sequence and
  the old number stays retired, because a number a tax authority has seen cannot be handed to a second
  document ([D-197](../decisions/round-24.md#d-197--an-invoice-is-compulsory-so-nobody-issues-one-invoiceissue-is-deleted-and-the-asks-write-writes-it)).
  **The ordinary cost of the automation belongs here:** a request voided five minutes after it was written
  leaves a voided invoice behind forever, in a table that — unlike the audit trail — has
  [no end date at all](../decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short).
- **There is no report over the requests that have no invoice, because that set is empty by
  construction.** D-187's line *"Most obligations have no invoice at all"* is deleted with the premise under
  it, and so is the report it left as the alternative to a status: there is nothing left to report. The
  sequence advances for documents nobody handed to anybody, and that is the price of writing the row
  automatically rather than a defect in it ([D-197](../decisions/round-24.md#d-197--an-invoice-is-compulsory-so-nobody-issues-one-invoiceissue-is-deleted-and-the-asks-write-writes-it)).
- What this row holds is the record that a document exists and what it was for. **What the document must
  contain beyond these columns is decided here and not awaited:** the issuer's half of the header is
  configuration, the payer's address and identifiers are `person_identifier` rows, and any requirement to
  print more than this design holds is met outside it
  ([D-198](../decisions/round-24.md#d-198--an-invoices-issuer-is-configuration-its-payers-identification-is-already-in-the-database)).
  No column is invented for the rest, and no review is pending behind the decision —
  [D-205](../decisions/round-24.md#d-205--there-is-no-legal-review-and-assumption-49-is-retired) retired the
  idea that anybody outside this design would check it, so what stands here is a decision of the person
  designing the system with its risk named.

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

**Why a transaction has no match — and this list is shorter than it was, which is the whole content of
[D-196](../decisions/round-24.md#d-196--the-variable-symbol-is-the-whole-match-what-arrives-under-its-own-symbol-is-attached-in-full-and-the-difference-is-shown):**
there is no symbol at all — cash-basis donors and people who type their own name in the wrong field; the
symbol matches no request; or the symbol matches a request that has been voided. **The symbol and nothing
else decides it.** *"The amount is less than asked, or more"* was the largest entry on that list and is
gone: 500 against a 550 ask and 1 100 against the same ask both match, and both attach in full. **So is
*"the request is already settled,"*** which used to sit beside it — a settled request that has not been
voided is still a live request, so money arriving again under its symbol attaches and the obligation reads
over. That row is not a failed match and not a breach: it is money that arrived twice for one liability,
and a person either moves it or refunds it at the bank. What is left unmatched is therefore money whose
symbol is missing, unknown, or dead — a narrower population than the one
[D-180](../decisions/round-23.md#d-180--there-is-no-queue-for-money-that-does-not-fit) was written about, and
not a queue.

**What the system does with any of those: it records the money, and since round 25 it can tell somebody.**
No page opens on it and nothing counts it. **What changed is the second half of that sentence:** money arriving
under no symbol is one of the two money cases the messaging module hands to a type and an audience — "both are now
a type with an audience", in [10 §8](10-messaging.md#8-reports-arrive-here-and-stop-being-a-name)'s own words, the
other being the late fee below — where [D-210](../decisions/round-25.md#d-210--a-report-is-a-delivered-message-so-all-five-report-codes-are-deleted-and-reporting-stops-being-a-name)
named this section by its other case, the over-or-under payment. So a
notice about such a row is an ordinary `message` authored by `system:messages` under a type whose audience an
installation edits ([D-209](../decisions/round-25.md#d-209--a-message-type-is-a-row-and-the-audience-it-reaches-is-configuration-an-admin-edits)),
and an automated send is authored under that label rather than gated by a code a job would have to hold
([10 §7](10-messaging.md#7-who-may-send-and-what-is-not-checked)). **This module names no code and no type for
it, and does not need one**: the vocabulary is rows in `message_type`, not rows in `permission`, and which clock
fires it is [K-14](../open-questions.md#k-14) — a question this page is not allowed to answer by picking a
night. **What did not change is the absence.** There is still no queue and no state: an unmatched row is not held
somewhere waiting to be cleared ([D-180](../decisions/round-23.md#d-180--there-is-no-queue-for-money-that-does-not-fit)),
a send is an act with its own audit row rather than a condition a row is in, and if such a type's audience
resolves to nobody, no row is parked anywhere — [10 §3](10-messaging.md#3-message--one-author-one-target-and-no-second-version)
calls that case exactly this absence, shaped as words.

When a person does decide to act, tying the transaction to a request is a write with a code of its
own, `payment.match`, held at the organization's scope by whoever runs the accounting
([D-182](../decisions/round-23.md#d-182--matching-money-is-a-code-of-its-own-and-the-automatic-half-is-systembank-pulls)). **There are exactly four outcomes they can choose between:**

| Outcome | When |
|---|---|
| **Attach** it to a different request | The symbol was mistyped; the real obligation is obvious from the payer |
| **Split** it across requests | One transfer, three siblings — the ordinary shape of family payment here |
| **Record as a donation** | Money with no obligation behind it, which is not the same as money that is missing one |
| **Refund** it, by hand | Nothing was meant to be owed. A second payment in the opposite direction ([D-075](../decisions/round-06.md#d-075--money-arrives-from-a-bank-api-a-payment-is-requested-by-variable-symbol-and-qr-code)): the transfer goes out at the bank, and what arrives here is a `payment` naming whoever recorded it ([D-158](../decisions/round-22.md#d-158--a-refund-happens-at-the-bank)) |

**One of those outcomes is now used on a row that has a subject, and that is worth saying where the list
is.** A surplus D-196 creates is not an unmatched transaction — it is a matched payment sitting partly on an
obligation that did not need all of it — and a person moves it with the same **Split** above, exercised
through `payment.match` on a row that is already attached. Nothing was added for it: the allocation table is
many-to-many in both directions exactly so that moving money from one obligation to another is a split and
not a correction.

**Why the tempting shortcut is refused, and why the refusal now covers less ground than it used to.**
Falling back to the payer's identity when the symbol
fails looks like it clears most of the unmatched rows. It clears most of their *accuracy* instead:
*a parent with two children pays one amount against one symbol* is the normal case, not the edge
case, and an identity fallback resolves it to whichever child the query reaches first. **A fee
recorded against the wrong child is a finance error and a membership that appears paid when it is
not, both at once — and the sibling it was meant for stays the one who looks unpaid.** Both halves
sit in rows that are kept with no end date. A fallback is not allowed to be wrong on the common
path, and this is the common path.

**The refusal stands and the mistake has moved, which is the trade and not a footnote to it.** D-076 was
refusing to resolve a *failed* symbol by guessing at a payer; here nothing is guessed, because the payer's
own bank carried the symbol this organization printed. What changed is which error the system makes on its
own. It no longer leaves a family's money with no subject — that was the old failure, and a slower one —
**it now puts all of it somewhere visible and wrong.** The module's own normal case makes it concrete: one
transfer of 1 100 Kč under one child's 550 Kč symbol, with a second child who also has an ask, lands
**entirely** on the first child, who then reads **+550 over** while the sibling reads unpaid. No tolerance
and no threshold is introduced anywhere to soften this — 4,90 against 5,00 is a shortfall like any other,
because a threshold would be a number nobody can defend and everyone would have to remember. **What catches it
is a type and an audience from round 25, and not somebody happening to open the row**: the
over-or-under payment notice is one of the two money cases [D-210](../decisions/round-25.md#d-210--a-report-is-a-delivered-message-so-all-five-report-codes-are-deleted-and-reporting-stops-being-a-name)
names as now reaching people *instead of waiting for them*, and [10 §8](10-messaging.md#8-reports-arrive-here-and-stop-being-a-name)
says the same thing from the sending side. **Which audience is nobody's to pick from here** — it is a row an
installation edits ([D-209](../decisions/round-25.md#d-209--a-message-type-is-a-row-and-the-audience-it-reaches-is-configuration-an-admin-edits)),
and the type's name is not this module's to invent. **What still holds is the absence:** no list holds the row
([D-180](../decisions/round-23.md#d-180--there-is-no-queue-for-money-that-does-not-fit)), and a delivered notice is
an act with an audit row, not a worklist. **What delivery does not buy is the hand:** a message saying a sum
arrived twice still leaves the surplus sitting on an obligation until a person holding `payment.match` moves it,
so a person reading an obligation that says +550, or the family being asked, remains the moment anything is
*decided*. Stating it as the decision states it: the design has traded a silence a treasurer notices in February
for a number that reads like a success — and round 25 gave that number a voice without giving it a hand.

Auto-refunding is refused for two reasons: it needs the bank integration to work outbound as well
as inbound, which is a second integration with its own authorization; and it returns the
grandparent's attempt at a camp contribution. **The first of those has changed kind while the refusal
stands.** Calls coming *in* are a designed thing now — a registered key, granted like any other caller
([05e](05e-keys-and-callers.md)) — so "outbound is a second integration with its own authorization" is no
longer an absence but a decision with a shape to copy. The outbound direction is answered, not
designed: an outbound call is either a named person acting or this system's own job under a label from
the fixed list, and nothing about it is built yet ([D-146](../decisions/round-20.md#d-146--an-outbound-call-is-a-persons-act-or-a-job-and-nothing-about-it-is-designed-yet),
[F-27](../open-questions.md#f-27)). The second reason was never a mechanism, and stands alone. **The one
outbound direction this module was asked about has since been refused outright rather than left
undesigned:** nothing is exported to an accounting system, and an external one is a later version's design
with its own document (§5,
[D-199](../decisions/round-24.md#d-199--nothing-leaves-this-system-to-an-accounting-system-and-an-external-one-is-a-later-versions-design)).

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
([D-180](../decisions/round-23.md#d-180--there-is-no-queue-for-money-that-does-not-fit)) there is no list of rows that need looking at. **What round 25
changed is that such a row can now be told about**: [10 §8](10-messaging.md#8-reports-arrive-here-and-stop-being-a-name)
hands money arriving under no symbol to a type and an audience, and
[D-214](../decisions/round-25.md#d-214--the-system-sends-and-d-164-is-narrowed-to-the-one-thing-it-was-protecting)
is why this page may no longer write the flat sentence that nobody is told — a send if an installation configures
one, and nothing at all if it does not, which is the same absence wearing a different coat rather than a page
promising a notice. **What no configuration buys is the worklist.** The
alternative refused was one whose first entry is always a sponsorship nobody wants to classify, and a worklist
nobody clears is a lie about supervision. What makes the no-queue survivable is that the money is not lost, only
unattributed, and every row is on the same screen in date order: the payer's belief and the
organization's belief are reconciled by a person who was asked, not by a count.
**[D-196](../decisions/round-24.md#d-196--the-variable-symbol-is-the-whole-match-what-arrives-under-its-own-symbol-is-attached-in-full-and-the-difference-is-shown)
shrank the population this cost is paid over and moved part of it somewhere else.** A camp transfer going
unattributed forever still happens, but it now takes a symbol that is missing, unknown, or dead to get
here at all. **A family's part-payment no longer arrives here:** it matched, it attached, and it is
attributed — to one child, when the parents meant two. The absence this section polices got smaller, and
the error it exists to catch moved into the rows that look settled.

---

## 3. Keeping `membership.outstanding_balance` honest

**This heading names a column that no longer exists, and it stays anyway.** `membership.outstanding_balance`
is deleted ([D-200](../decisions/round-24.md#d-200--membershipoutstanding_balance-is-deleted-and-the-balance-is-the-one-definition-it-was-copied-from)),
and the heading is the slug [the invariant register](00a-invariant-register.md), the register of assumptions
([assumption 53](../open-questions.md#i-assumption-index)) and two earlier rounds already resolve to — **a
renamed heading is a dead anchor that no build will report**, so the column's name survives in a title and
nowhere else. **There is one
definition of what is owed, it is the blockquote below, and this is the only place it is stated.** Every
screen, every gate and every API response — and a delivered message that quotes one ([10 §8](10-messaging.md#8-reports-arrive-here-and-stop-being-a-name)) — that shows a balance reads it, over
`fee_obligation` and `payment_allocation`; [03-membership.md §3](03-membership.md#3-membership) shows it and
does not store it. **The view this section used to recommend is not created either** — the definition *is* the
view, and a second name for it is a second thing to get wrong.

**The recommendation this section has been making since round 6 has been taken, so what follows is a rule and
not a menu.** The table it used to print offered three options behind a sentence that said "two", and its
recommendation — *"drop the column and use a view"* — named two of the three at once, which is what a table
looks like when it has outlived its question. The option taken is the middle one, **without the view**: the
column is gone and nothing replaces its name.

**What the column had going for it, because the honest answer is that it had one thing.** Not accuracy. Its
defence was that a membership screen wants a number without joining four tables, and that defence is answered
the way it should have been answered when the column was drawn: **a request memoizes, so the join is not the
expensive thing the column was invented to avoid**
([D-114](../decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation)),
at the scale this design states it runs at
([D-112](../decisions/round-13.md#d-112--the-systems-scale-is-stated-hundreds-of-people-tens-of-registrants-per-event)).

**What survives the deletion is the argument, and §4a is why it had to survive.** A stored balance is a copy,
and a copy is maintained by every path that writes an allocation or it drifts — the trigger that used to do it
for all of them at once is gone ([00-conventions §6a](00-conventions.md#6a-who-enforces-an-invariant-now)).
**A wrong number here has a human consequence: either a wrongly-suspended member or a wrongly-chased family.**
That sentence is why the column is deleted rather than deprecated, and it does not become false once the copy
is gone: a definition implemented in several places can disagree across them just as a stored value can, which
is precisely what §4a's first check now measures instead of comparing two copies.

**The definition, stated once, and read from here:**

> *balance* = `amount_due` − the sum of allocations whose payment is **`confirmed`**

The discount term left with the column it was named after ([D-183](../decisions/round-23.md#d-183--a-changed-ask-is-a-voided-request-and-a-new-symbol-and-amount_discount-goes)): a reduced fee is a
smaller `amount_due`, and a gap between what was asked and what is owed lives in the ask, not in a term
beside it.

**Only confirmed payments count.** An obligation is not settled by money that has been promised,
intended, described in an email, or reported by a payer who believes they sent it. **There is no state for
a transfer that is on its way** (D-075): either the bank has reported it and it is confirmed, or the system
has not heard of it. **A member is activated by the first, never by the second.**

**"No obligations" is not "nothing owed", and that distinction did not die with the column.** Assumption 53
recorded that an imported membership's balance is **NULL and not zero**, because a zero asserts the
organization settled a debt it never saw, and [D-093](../decisions/round-09.md#d-093--the-one-off-import-may-create-memberships-both-ends-dated)
made imported rows believe things. With no column the distinction does not vanish — **it moves into the
absence of rows.** An imported membership has no `fee_obligation` underneath it, because the legacy corpus
carries no money at all ([D-090](../decisions/round-07-08.md#d-090--the-legacy-corpus-is-thousands-of-roster-rows-with-numbers-and-no-money)),
so the definition above returns *nothing* for such a person — and reading that nothing as *nothing is owed*
would be the same lie the zero would have been. It must keep reading as **nothing is known** in the places the
NULL used to be read: in the overdue list §2's index already produces, wherever a balance is rolled up for
display (which is what §4a's first check recomputes), and on any screen that would otherwise print `0 Kč` —
where the honest rendering is *no fee record*, not a number. **The activation gate's answer for such a row is
unchanged, and is written down here rather than inferred:** it asks whether any attached obligation has a
positive balance, an imported membership has none to check, so the test **passes vacuously**. That is correct
for a gate — nobody is being suspended for a debt nobody computed — and it is the same fact that makes an
obligation-less imported membership something a person looks at rather than something the model certifies; the
load's own rows say which they are by carrying `data_confidence = 'low'`, which names who wrote a row and not
whether money is owed, so it is a pointer for a reader and never a rule anything computes.
**Deleting the column removed a number that could lie; it did not remove the absence underneath it, and this
paragraph is the insurance that a later page does not delete the sentence along with the column**
([D-200](../decisions/round-24.md#d-200--membershipoutstanding_balance-is-deleted-and-the-balance-is-the-one-definition-it-was-copied-from)).

---

## 4. How this connects to membership

**The activation gate.** A membership's fee is settled when **no obligation attached to it has a positive
balance**, and that is the whole test with no status excepted from it — a fee
nobody is going to collect is an obligation written with a smaller `amount_due`, so it never presents
itself as a balance to work around
([D-157](../decisions/round-22.md#d-157--there-are-no-hardship-waivers),
[D-159](../decisions/round-22.md#d-159--the-status-enum-keeps-three-of-its-seven-values)). **Two words went
out of that sentence with `amount_discount`:** *"after discounts"* subtracted a term that no longer exists, and
a reduced ask is a smaller `amount_due`, so there is nothing left to subtract
([D-183](../decisions/round-23.md#d-183--a-changed-ask-is-a-voided-request-and-a-new-symbol-and-amount_discount-goes)).
**The balance it reads is §3's definition and nothing else** — the gate joins `fee_obligation` to
`payment_allocation` when asked and stores no answer, because the column beside the membership it could have
read is deleted ([D-200](../decisions/round-24.md#d-200--membershipoutstanding_balance-is-deleted-and-the-balance-is-the-one-definition-it-was-copied-from)).
**[D-196](../decisions/round-24.md#d-196--the-variable-symbol-is-the-whole-match-what-arrives-under-its-own-symbol-is-attached-in-full-and-the-difference-is-shown)
is what makes this test bite in both directions, and the gate did not move to accommodate it:** a short payment
settles nothing (500 Kč against a 550 Kč ask leaves a 50 Kč balance and the membership stays
`pending_payment`), and a long one settles everything (1 100 Kč against that ask leaves no obligation with a
positive balance, so the membership activates **and the surplus is simply visible**: a negative balance on the
sibling obligation, to be moved by `payment.match` if anybody decides it should be moved, with nobody told it is
there and no list counting it ([D-180](../decisions/round-23.md#d-180--there-is-no-queue-for-money-that-does-not-fit),
[D-164](../decisions/round-22.md#d-164--nobody-is-told-and-no-page-may-say-otherwise))). For a
membership with **no obligations attached at all** the test passes vacuously — §3 is where that is stated and
where the reason it is right for a gate is kept apart from the reason it is not a settled debt. This test
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

**Nothing has to be told afterwards, and this sweep tells nothing at all.** `MEMBERS` is evaluated live on the checked date
([D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)),
so the two facts step 1 writes — the period ending and the `lapsed` status — are visible to the next check,
with no job in between and no stored answer to invalidate
([D-114](../decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation),
[domain/06 §8](../domain/06-authorization-model.md#8-there-is-no-permission-cache-and-what-replaces-it)).
**The second half of that lead sentence is round 25's.** This job expires memberships and writes no message;
a renewal notice is a `message` of its own type authored by `system:messages`, which makes the notice a separate
authored act rather than a side effect of the transition, and which clock fires it is
[K-14](../open-questions.md#k-14) ([D-212](../decisions/round-25.md#d-212--systemmessages-is-the-sixth-actor-label-and-the-renewal-sweep-stops-being-a-sender),
and [03-membership §7's check 4](03-membership.md#7-integrity-checks), which says the same thing from the worklist side).
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
   counting money that was only promised. **D-200 deleted the column and this check did not retire with it —
   it changed job.** There is no copy left to agree with the sum, so what is verified is that every place a
   balance appears *implements §3's definition*: the same query, the same failure list, and D-075's rule that
   only confirmed payments count is still what it checks. **That is a harder check than the one it replaced,**
   because a disagreement can now arise between any two of the readers rather than between one reader and a
   stored number, and the number of readers is not written down anywhere
   ([D-200](../decisions/round-24.md#d-200--membershipoutstanding_balance-is-deleted-and-the-balance-is-the-one-definition-it-was-copied-from)).
2. **A payment whose allocations do not account for its amount — and an unmatched payment is not on this
   list, on purpose.** `payment_allocation` is many-to-many in both directions and §2's rules constrain the pair
   and the sign of each amount, never the sums, so a payment carrying no allocation **and** no matched request is
   money that moved and was never attributed to anything. **Since [D-196](../decisions/round-24.md#d-196--the-variable-symbol-is-the-whole-match-what-arrives-under-its-own-symbol-is-attached-in-full-and-the-difference-is-shown)
   this check has to say something it never had to say before: an unmatched payment has no allocations because
   that is what §2b designs.** Counting those rows would report a designed absence as a breach, and it would be
   wrong about most of a real bank statement — grants, donations and sponsorships that were never a member's
   money ([D-180](../decisions/round-23.md#d-180--there-is-no-queue-for-money-that-does-not-fit)). What the check
   reads is therefore a payment whose symbol resolved and whose allocations still sum to less than it, which
   under attach-in-full is a write-path failure and nothing else. **And an obligation allocated beyond its
   `amount_due` is no longer a finding at all:** the automatic attach writes one allocation carrying the whole
   transfer, so a 1 100 Kč transfer under a 550 Kč obligation allocates 1 100 to it by design (§2, §2a step 6).
   The check that used to call that "an overpayment that nobody has refunded" would now fire on the module's own
   happy path, so it is withdrawn here rather than left to be rediscovered as noise. **The layer here is the
   write path, and there is no constraint to sit beneath it**: the sums span rows of two tables, which is
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
   because nothing creates the obligation and no trigger could have been forgotten. **This is not about money
   that arrived and did not fit** — that used to be a category, and
   [D-196](../decisions/round-24.md#d-196--the-variable-symbol-is-the-whole-match-what-arrives-under-its-own-symbol-is-attached-in-full-and-the-difference-is-shown)
   deleted it: money either resolves to a live request or it has a symbol that is missing, unknown or dead, and
   nothing fails to *fit* any more. An unmatched `bank_transaction` is money with no subject, most of
   it never meant for a member at all, and the design keeps it that way on purpose (§2b,
   [D-180](../decisions/round-23.md#d-180--there-is-no-queue-for-money-that-does-not-fit)). This is the other side of the same ledger: a liability with no ask
   attached. **How silent it is is now a configuration question, and the two readings differ.** An obligation
   past its `due_date` and unpaid is exactly what a lateness type is computed from, so if an installation
   configures one, the first half of this row reaches a person as a message and not as a check
   ([10 §2](10-messaging.md#2-message_type--a-vocabulary-that-is-also-a-settings-panel)). **The second half has no date to
   be late about**: an `event_registration` with no obligation behind it has no `due_date`, so no type can be
   computed from it and it stays invisible in both directions — nobody is chased and nobody pays — which is why
   it is this check's finding and not a message type's. It is the one failure on this list
   that no unmatched row would ever reveal, because with no queue there is nowhere the two could meet.

**No check here reads a negative balance, and that is a decision rather than a gap in the list.** An obligation
whose allocations run past its `amount_due` *is* a balance below zero — the **+550 over** §2b names as the thing
a person is supposed to notice — and nothing in this section, and nothing in
[05d §11](05d-invariants-and-seed.md#11-invariants-to-verify), counts those rows. It stays that way for the same
reason §2b refuses a worklist: an overpayment is not an inconsistency but a fact about a family's transfer, the
surplus is moved by a person holding `payment.match` rather than by a report, and a count of rows that are legal
by design is a list whose first entry is always somebody's correct data
([D-180](../decisions/round-23.md#d-180--there-is-no-queue-for-money-that-does-not-fit),
[D-164](../decisions/round-22.md#d-164--nobody-is-told-and-no-page-may-say-otherwise), narrowed but not repealed by
[D-214](../decisions/round-25.md#d-214--the-system-sends-and-d-164-is-narrowed-to-the-one-thing-it-was-protecting)). **So the answer to "what
catches it" is §2b's and it belongs next to the absence: a delivered notice if an installation configures the
type, and then a person reading an obligation that says +550 and deciding where the money goes.**
**A notice is not a count and would not be a check here** — it writes nothing in this table, its audience is an
installation's row ([D-209](../decisions/round-25.md#d-209--a-message-type-is-a-row-and-the-audience-it-reaches-is-configuration-an-admin-edits)), and its clock is
[K-14](../open-questions.md#k-14) — so refusing the count below stands untouched. Writing the count would be a new check, and a new check is a decision this round did not
take — it is named as missing here so that a reader looking for it finds the reason rather than the check.

**Checks 1 and 2 are the two that matter, and §3 says why in one line: a wrong number here has a human
consequence** — either a wrongly-suspended member or a wrongly-chased family. Check 3 is the one that finds
a whole class of missing money rather than a wrong row, and it is the only one of the three that can be
non-empty because a feature was never written rather than because a row is wrong.

---

## 5. Open issues — the whole of this document, essentially

**Nothing is open on this page, and the bullets stay.** Three questions were standing when this section last
counted itself, and every one of them was answered in round 24; each keeps its place here **with its verdict
written into it**, because a bullet deleted from an open-issues list reads to the next person as "still open,
we forgot", which is the failure this round exists to close. Three more were answered while an earlier round was
running — who may reduce a fee, whether the organization issues invoices, and what gets a variable symbol — and
each is listed at the end of the page beside the decision that closed it. **What this module used to leave
unnamed at the bottom of this section is no longer a thing a module could own: reporting was never inherited
here, it was deleted**, and what arrives over this module's money is a type with an audience
([D-210](../decisions/round-25.md#d-210--a-report-is-a-delivered-message-so-all-five-report-codes-are-deleted-and-reporting-stops-being-a-name),
[10 §8](10-messaging.md#8-reports-arrive-here-and-stop-being-a-name)) — the paragraph about this module's codes below
says what that leaves and what it costs.

1. **✅ Closed — accounting integration: nothing leaves this system, and nothing is reserved for a system that
   might arrive** ([D-199](../decisions/round-24.md#d-199--nothing-leaves-this-system-to-an-accounting-system-and-an-external-one-is-a-later-versions-design)).
   The bullet asked whether anything needs to be exported, and the answer is that this design owes a future
   accounting package **nothing at all**: no export, no feed, no periodic journal, no CSV of the day's bank
   rows, no `external_reference` column, no `export` status, and no actor label for accounting. Everything the
   money model asserts lives in this module's tables (§2) and is read out of them a person at a time, on the
   screens this module already has: **there is no export path, and there is no code that gates a list either** —
   reporting's codes went with the screen they gated, so neither the read nor the way out exists any more
   ([D-210](../decisions/round-25.md#d-210--a-report-is-a-delivered-message-so-all-five-report-codes-are-deleted-and-reporting-stops-being-a-name)),
   and a person who wants this module's data out of it has to read it. **The actor list grew by one in round 25 and
   the newcomer has nothing to do with accounting**: `system:messages` joined it for automated sends
   ([D-212](../decisions/round-25.md#d-212--systemmessages-is-the-sixth-actor-label-and-the-renewal-sweep-stops-being-a-sender)),
   and [00-conventions §7a](00-conventions.md#7a-what-an-empty-actor-column-means) is still the whole list, so this
   bullet's refusal stands as it was written. That is the
   concrete shape of a deferral that costs nothing: an integration added later will need a label, and needing
   one someday was not a reason to reserve one now. An external accounting system **may** appear in a later
   version and will be designed then, in a document that is not this one — which is why this closes instead of
   staying filed: the question on the page was never *will there ever be one*, it was *what does this design owe
   it now*. **The direction half of the old wording is still the reason it was ever worth asking:** who may call
   this system is designed ([05e](05e-keys-and-callers.md)), this system calling anyone else is answered and
   undesigned ([D-146](../decisions/round-20.md#d-146--an-outbound-call-is-a-persons-act-or-a-job-and-nothing-about-it-is-designed-yet),
   [F-27](../open-questions.md#f-27)), and D-199 is that answer applied to the one outbound direction this
   module kept asking about.
2. **✅ Closed — jurisdiction: one half was a fact about the country and the other half was a question about a
   header, and neither is a rule this module encodes**
   ([D-197](../decisions/round-24.md#d-197--an-invoice-is-compulsory-so-nobody-issues-one-invoiceissue-is-deleted-and-the-asks-write-writes-it),
   [D-198](../decisions/round-24.md#d-198--an-invoices-issuer-is-configuration-its-payers-identification-is-already-in-the-database)).
   This is the half of an item that used to read "currency and jurisdiction". The currency half was answerable
   and was answered: koruna, on every table that carries one (§2,
   [D-155](../decisions/round-22.md#d-155--the-currency-is-koruna-and-the-modules-own-money-path-said-so)) —
   and the count this bullet printed went stale the day the invoice table arrived, which is what happens to a
   number beside a sentence. **Of the two clauses that were left, one stopped being a question:** invoices are
   **compulsory** in this country, so §2's document row is written beside every ask and the code that used to
   gate it is deleted (D-197) — the module did not encode a rulebook, it was told one fact. **The other half was
   refused at its premise:** who the document is from is **deployment configuration**, because there has been no
   `unit` row since [D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)
   and there is no `organization` table to invent; the payer's IČO and DIČ are already `person_identifier`
   **schemes**; and delivery, filing, reporting and the accountant's reconciliation are acts this system does not
   perform and holds no column claiming it performed (D-198,
   [D-164](../decisions/round-22.md#d-164--nobody-is-told-and-no-page-may-say-otherwise)). **What the module
   encodes of this country's law is therefore one column that is never reused, and it says so at §2.** Whether the
   organization owes anything about its money to anybody outside itself is answered in the same breath: not by
   this schema. **The sitting this bullet used to point at is gone.** It closed by citing "the four data policies
   in front of a legal review"
   ([00-conventions §8](00-conventions.md#8-personal-data-and-erasure),
   [06b §6](06b-redaction-and-checks.md#6-open-issues)) — [D-205](../decisions/round-24.md#d-205--there-is-no-legal-review-and-assumption-49-is-retired)
   retired the review, so what stands behind every retention and paperwork choice in this module is a decision of
   the person designing the system with its risk named in the same paragraph, and **no page here may say a lawful
   basis is outstanding.** The costs are stated where they bite: **two legal entities in one deployment is
   impossible**, and a request voided minutes after it was written leaves a voided tax document behind forever.
3. **✅ Closed — what a payment that does not fit settles: the condition was deleted rather than adjudicated**
    ([D-196](../decisions/round-24.md#d-196--the-variable-symbol-is-the-whole-match-what-arrives-under-its-own-symbol-is-attached-in-full-and-the-difference-is-shown)).
    The item this sat inside asked three questions; two were answered in round 23 — **every** payable gets a
    symbol, and **one live request per liability**
    ([D-181](../decisions/round-23.md#d-181--every-payable-has-a-variable-symbol)) — and the third, the case
    neither of them reached, was answered by removing the premise under it: **the variable symbol is the whole
    match.** A bank row whose symbol resolves to a live request is attached **in full**, the amount is never a
    condition of a match and never becomes one, and the difference is shown
    ([§2a step 6](#2a-how-money-actually-arrives)). What that settled, in the order it hurts:

    - ~~500 sent against a 550 request **stays unmatched**~~ — **it attaches.** The symbol resolves, the whole
      500 Kč lands, `amount_paid` reads 500, the status arithmetic reads `partially_paid`, and the balance is
      50 Kč, with nobody having allocated anything (§2). **No tolerance and no threshold was introduced to go
      with this:** 4,90 against 5,00 is a shortfall like any other, because a threshold would be a number nobody
      can defend and everyone would have to remember. An obligation may equally be paid **too much** — the status
      still reads `paid`, there is no fourth value and no credit concept, and the surplus is an allocation a
      person moves with `payment.match`, whose *split* outcome already existed for exactly this shape.
      **The membership gate did not move to accommodate any of it:** a fee is settled when no attached
      obligation has a positive balance (§4), so a short payment settles nothing and a long one settles
      everything.
    - **And nobody finds out unless an installation has configured a type that says so.** Round 25 opened
      [the messaging module](10-messaging.md), and [D-210](../decisions/round-25.md#d-210--a-report-is-a-delivered-message-so-all-five-report-codes-are-deleted-and-reporting-stops-being-a-name)
      names this exact case — the over-or-under payment — as one of the two money sentences that now reach people
      instead of waiting for them. **This module names no type for it and no page of it may pick the audience**;
      whether such a type exists at all, whom it reaches, and which clock fires it are configuration and
      [K-14](../open-questions.md#k-14). **What stands untouched is that nothing here holds the row**: after
      [D-180](../decisions/round-23.md#d-180--there-is-no-queue-for-money-that-does-not-fit) there is no list of unmatched rows for a person to notice it on, and
      a send is an act with an audit row rather than a state a row waits in. So on the ground *finds out* still
      means somebody telephoning the payer because they were asked to, which is a procedure and not a
      design. **What changed is what there is to find out.** The rows that used to arrive here as
      "money that did not fit" now arrive *matched and mis-attributed*: one 1 100 Kč transfer under one child's
      550 Kč symbol, with a sibling who also has an ask, lands entirely on the first child, who reads **+550
      over** while the sibling reads unpaid, on the module's own normal path. §2b states that trade and
      does not soften it, and what catches it is **a delivered notice where somebody configured one, and then a
      person reading an obligation that says +550 and deciding where the money goes** —
      which is also why no check counts those rows (§4a).

    **Why this is not a footnote, and what became of the fear:** this was the one place the module could still
    end up with two money paths — the automatic one, and a hand-corrected one running beside it. **It has both,
    by choice.** §2b is the hand half and now it is narrower in one way and wider in another: a person no longer
    adjudicates money that failed to match, and instead moves money that arrived under the wrong child's symbol.
    The automatic half stopped being conditional on an amount, so the seam between the two paths is a person
    deciding a surplus belongs somewhere else — which is a decision somebody holds a code for, not a hole.

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
- **Invoicing** — closed in round 23 and reopened by the country rather than by this design. **What D-197
  reversed is precisely the sentence this bullet used to hold** — *"an invoice is a document a payer asks for"*
  — and it was the right answer to a question nobody had asked yet: invoices are **compulsory**, so the row is
  written by `fee.create` beside its request in the same transaction, `invoice.issue` is deleted, and the set of
  requests without a document is empty by construction. What D-187 got right and keeps: its own table, its own
  sequence — now legally required rather than merely tidy — **no state**, and a `payment_request` still is not an
  invoice and never becomes one. What the law requires of one stopped being item 2's open question and became a
  fact plus a refusal: the fact is that the document must exist, and the refusal is that this module encodes no
  jurisdiction's rules (§2,
  [D-197](../decisions/round-24.md#d-197--an-invoice-is-compulsory-so-nobody-issues-one-invoiceissue-is-deleted-and-the-asks-write-writes-it),
  [D-198](../decisions/round-24.md#d-198--an-invoices-issuer-is-configuration-its-payers-identification-is-already-in-the-database)).
  **What the reversal cost is on the page in §2, not here:** D-187 had deliberately kept the issuing code apart
  from `payment.match` so the person who may type in a number is not the person who may sign a tax document, and
  that separation no longer exists.
- **What gets a variable symbol, and one per what** — every payable, one live request per liability, never
  per person and never per person-year. **The remainder of that item — issue 3 above — closed with it in the same
  round** ([D-181](../decisions/round-23.md#d-181--every-payable-has-a-variable-symbol),
  [D-196](../decisions/round-24.md#d-196--the-variable-symbol-is-the-whole-match-what-arrives-under-its-own-symbol-is-attached-in-full-and-the-difference-is-shown)).
- **Payment methods, and collecting rather than recording** — both closed earlier by
  [D-075](../decisions/round-06.md#d-075--money-arrives-from-a-bank-api-a-payment-is-requested-by-variable-symbol-and-qr-code).
  `bank_transfer` arrives by import and `cash` is recorded by hand; `voucher` and `credit_note` stay in
  the enum until somebody says otherwise; there is no card and no direct debit (§2). What remained in
  those two items was maintenance, not a decision.

**The count, recounted — and the recount is the lesson, so the old one stays.** **Nothing is open on this page
now:** the accounting export closed with
[D-199](../decisions/round-24.md#d-199--nothing-leaves-this-system-to-an-accounting-system-and-an-external-one-is-a-later-versions-design),
jurisdiction with
[D-197](../decisions/round-24.md#d-197--an-invoice-is-compulsory-so-nobody-issues-one-invoiceissue-is-deleted-and-the-asks-write-writes-it)
and [D-198](../decisions/round-24.md#d-198--an-invoices-issuer-is-configuration-its-payers-identification-is-already-in-the-database),
and what a payment that does not fit settles with
[D-196](../decisions/round-24.md#d-196--the-variable-symbol-is-the-whole-match-what-arrives-under-its-own-symbol-is-attached-in-full-and-the-difference-is-shown);
the older items below each still stand beside the decision that closed them. **What this section used to print
here is kept because a count beside a sentence is a claim:** the number printed was **nine remaining open**, and
nine was right, while the list underneath it named **seven** of those nine and counted the variable-symbol item
twice — eight printed, with *who may authorize a refund* and *currency* missing, which were the two that round
closed. A summary that is right above a list that is wrong is worse than a wrong summary: **the summary is what a
reader quotes, and the list is what a reader answers from.** And the claim at the very top of this document,
repeated in §1, said **five** questions were open while this section said **three** — the header was still naming
discounts and variable symbols that earlier rounds had already answered, and only a reader would ever have caught
it. Round 24 deleted that header claim rather than reconciling it with this one, because the honest number at both
places was zero. **In the tables this page owns, the whole round changed one column and one permission code:**
`membership.outstanding_balance` gone (§3) and `invoice.issue` gone (§2); everything else it did was prose.

**None of what closed here was architectural either, which is why it could stay open this long.** How money
arrives, how it is requested, and what happens to money that does not match were all decided, so what remained was
**policy that required somebody in the organization to be asked** — and being asked was the only thing that was
ever missing. *This document did not need a rewrite; it needed answers*, and now it has them, which is a different
thing from a document that needed neither.

**The module's permission codes are shipped codes, and the paragraph that complained about it is gone.** Until
round 24 this section closed by pointing at
[the catalog's deferred namespaces](../appendix/permission-catalog-b-roles-and-open-issues.md#10-deferred-namespaces)
and observing that this module's money already moves while its codes sit there as placeholders
([D-182](../decisions/round-23.md#d-182--matching-money-is-a-code-of-its-own-and-the-automatic-half-is-systembank-pulls)).
That was true, and it is closed: [D-195](../decisions/round-24.md#d-195--the-money-codes-are-shipped-codes-catalog-a-grows-a-money-section-and-catalog-b-10-loses-three-rows)
documented them in [catalog A's money section](../appendix/permission-catalog-a-codes.md#4a-money), and the
deferred table lost the rows that called a working module a placeholder. **The six codes this module spends are
`fee.view`, `fee.create`, `payment.view`, `payment.record`, `payment.reverse` and `payment.match`.** **Every one
of them sits at `applies_to = unit`, and no choice is being made: money is not an item.** A `fee_obligation`
hangs off a person and a period, a `payment` hangs off a bank statement, and an `invoice` hangs off a request —
none of them is an occasion an audience could bind to, so a money grant aimed at an item would name a scope the
row underneath it has nothing to point at. **The consequence worth saying out loud is `payment.reverse`:** it sits
at the unit, so whoever may reverse money may reverse **any** of it — nothing in this shape says *this payment and
not that one*, and the only control over that is who was granted the code, once, in the open. **The kind each code
is follows the only thing that reads the column:** `fee.view` and `payment.view` are `read`, and `fee.create`,
`payment.record`, `payment.reverse` and `payment.match` are `write`. `permission.right_kind` is required on every
row and has exactly one customer — the guardianship channel, which compares a guardian's `right_level` against it
([05 §2](05-authorization.md#right_kind-a-column-with-exactly-one-customer)) — so which side of that comparison the
two `view` codes fall on is what decides how far a right of *see* reaches into a child's money, and these two rows
say **all the way in**. That is a guardian's answer and not a hint, which is the only reason the column is filled
in on a money row at all. **And there is no seventh code, which round 25 settled rather than deferred.** Until
last round this paragraph explained why a money report's own code sat deliberately undeclared beside the codes
reporting already had, and why a module could not settle a question about a reporting shape by promoting its own
row. **There is nothing left to wait for, because there is nothing left to gate:** [D-210](../decisions/round-25.md#d-210--a-report-is-a-delivered-message-so-all-five-report-codes-are-deleted-and-reporting-stops-being-a-name)
deleted reporting's codes along with the screen they authorized, so a module is not one row short of a namespace
that no longer exists, and the deferral is not a deferral of anything. **Six codes are the whole of what this
module spends**, and the shape a listing over money takes is not a permission at all: it is a type and an
audience, which is why the two cases this page used to hand to a person who might someday open a list are now
sent ([§2b](#2b-money-that-cannot-be-matched), and `fee-overdue` at the indexes in §2). **`invoice.issue` appears
in neither catalog**, because [D-197](../decisions/round-24.md#d-197--an-invoice-is-compulsory-so-nobody-issues-one-invoiceissue-is-deleted-and-the-asks-write-writes-it)
deleted the code one answer after [D-195](../decisions/round-24.md#d-195--the-money-codes-are-shipped-codes-catalog-a-grows-a-money-section-and-catalog-b-10-loses-three-rows)
registered it. **The finance question that *was* in [the register](../open-questions.md) —
[K-10](../open-questions.md#k-10--are-the-money-permission-codes-still-deferred) — closed with the six codes**,
and the half of it that asked about a money report closed a round later by ceasing to be a question
([10 §8](10-messaging.md#8-reports-arrive-here-and-stop-being-a-name)).
