# Data Model — Membership

`membership_type`, `membership`, and `membership_request`.

**`unit_participation` used to be documented here and no longer is** — the table is deleted,
together with every sub-unit it pointed at
([D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)).
§5 is where that is recorded and where the discipline it carried is retargeted at groups. Belonging
to the organization is a `membership`; belonging to a **group** is
[`person_group_member`](02-organization.md#1-person_group), specified in the groups module.

Domain rationale: [../domain/05-membership-lifecycle.md](../domain/05-membership-lifecycle.md).

---

## 1. `membership_type` — one row, kept as a table

**Fields**

| Field | Kind | Notes |
|---|---|---|
| `code` | text, required | `'member'` — and nothing else, for now. |
| `name` | text, required | |
| `description` | text, optional | |
| `duration_months` | integer, required, defaults to 12 | 12: the fee is yearly. Kept as a column rather than a constant so a type with a different term could be added as a row, with no migration. |
| `expiry_month`, `expiry_day` | integers, required, both defaulting to 1 | **When the fee expires** (D-047): 1 January. The organizational year runs with the calendar, so "a member this year" means what a reader expects, and the sweep, the campaign and the reports all land on a boundary nobody has to look up. These are columns, not a constant in a scheduled job, for the reason the user gave for the window below: the date is a parameter the organization may move, and moving it must not require a code change. Every lapse date, the yearly sweep and the renewal worklist derive from these two values. |
| `renewal_grace_days` | integer, required, defaults to 60 | The renewal window after `valid_to`, during which a payment restores the membership **without re-applying** and backdates the new period to the expiry date. Dates, not a status: the person is expired throughout (D-040). 60 days (D-048). **Read it from here; never hardcode 60 in a job or a front end** (D-048). The requirement attached to that answer was precisely that the value stays tunable. |
| `is_self_registerable` | boolean, required, defaults to true | |
| `requires_approval` | boolean, required, defaults to true | |
| `sort_order` | integer rank, required, defaults to 0 | |
| `valid_from`, `valid_to` | period (from/to, open-ended allowed); both ends optional | |
| `created_at` | timestamp, audit time | |

**Rules**

- `code` is unique over **all** rows.
- `expiry_month` is between 1 and 12; `expiry_day` is between 1 and 31.
- Where both ends of the period are set, `valid_to` is later than `valid_from`. Either end may
  be absent, and no comparison is attempted when one is.

### Why this table still exists with one row

**There is exactly one membership** (D-037). Everyone who is a member holds
`membership_type = 'member'`, the fee is flat and per person, and being a counselor or a leader
is a **role**, never a type ([D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)).

The table survives rather than collapsing into a constant for two reasons:

1. **Consistency with the design's own principle.** Vocabularies are rows, not enums —
   the same argument that keeps the seeded registries as tables (`grant_scope_type`,
   `selector_type`; the two examples this bullet used to give, `org_unit_type` and `position`,
   were both deleted in round 10 by
   [D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row) and
   [D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)).
   A second kind of membership (a supporting or honorary one) would then be a data change.
2. **A place for the organizational calendar to live.** The term, the expiry date and the
   renewal window are genuinely type-dependent parameters even when there is one type — and
   they are the parameters most likely to be tuned. Putting them in a row rather than in code
   is what makes *"it should not be hard to modify"* ([D-048](../decisions/round-04.md#d-048--the-renewal-window-is-60-days-and-is-a-configuration-parameter))
   true by construction rather than by discipline.

The cost is honest and small: an FK that currently always holds one value. Recorded here
rather than hidden.

### What was removed, and why

| Removed | Reason |
|---|---|
| `category` (`child`/`adult`/`special`) | Membership is ageless (D-038). Age is a fact about the person. |
| `min_age`, `max_age` | No age floor, ceiling, or automatic age-out. |
| `requires_background_check` | The system records no background checks (D-043). |
| `requires_references`, `requires_guardian_consent` | Nothing gates a request but identity and payment (D-044). |
| `allows_concurrent` | With one type and a person-scoped overlap constraint, this cannot arise. |
| `grace_period_days` (as a status) | Replaced by `renewal_grace_days` — a window, not a state (D-040). |
| `fee_schedule_id` | The fee is flat and per person (D-037), so there is nothing type-specific to schedule. The schedule attaches to the **obligation** instead — [07-finance.md §2](07-finance.md#2-minimal-provisional-shape). |

**The age checks that used to sit on the type go with them** (`ck_membership_type_ages` was
their name). With no ages on the row there is nothing for a migration to express and nothing left
for a report to verify, so the removal is complete rather than a rule left hanging.

---

## 2. `membership_request`

**Fields**

| Field | Kind | Notes |
|---|---|---|
| `id` | surrogate id | Internal only. |
| `public_id` | uuid, required, generated | The identifier used outside the system; unique. |
| `person_id` | reference to `person`, required | The **subject**: the person who would become a member. For a minor's application this is the **child**, not the parent. |
| `submitted_by_person_id` | reference to `person`, optional | Who actually submitted it. Equals `person_id` for self-application; differs when a guardian (or staff) applies on behalf. This is the act-on-behalf record. |
| `requested_membership_type_id` | reference to `membership_type`, required | |
| `status` | text, required, defaults to `draft` | One of `draft`, `submitted`, `under_review`, `approved`, `rejected`, `withdrawn`, `expired`. |
| `submitted_at` | timestamp, optional | |
| `decided_at` | timestamp, optional | |
| `decided_by` | reference to `person`, optional | |
| `rejection_reason_code` | text, optional | |
| `rejection_note` | text, optional | |
| `membership_id` | reference to `membership`, optional | Set on approval. The reference is added only once `membership` exists (§3): this is the design's circular pair, resolved with a deferred reference. |
| `previous_membership_id` | reference to `membership`, optional | Links a renewal or re-application to the prior membership. This is how a returning member's chain is expressed. |
| `expires_at` | timestamp, optional | An unreviewed request eventually goes stale. Needed so the review queue does not accumulate abandoned drafts forever. |
| `notes` | text, optional | |
| `source` | text, optional | `self`, `guardian`, `staff` or `import`. |
| `created_at`, `created_by`, `updated_at`, `updated_by` | timestamp, audit time; reference to `person` | The standard audit columns. |

**Rules**

- A request in `approved` or `rejected` has **both** `decided_at` and `decided_by`. There is no
  decision without a decider and a time.
- Any request that is not `draft` has a `submitted_at`.
- An `approved` request points at a `membership`. The one allowance is a request decided at a
  time still in the future, which is how the request and the membership are inserted in two
  steps inside one transaction; the link is not optional once that transaction is over.
- **At most one open request per person per membership type.** Open means `draft`, `submitted`
  or `under_review`. Decided requests — `approved`, `rejected`, `withdrawn`, `expired` — are
  outside the rule, which is what lets a person apply again after being turned down.

**Indexes**

- On `person_id` with `submitted_at` descending: one person's applications, newest first.
- A partial index over the review queue only — rows in `submitted` or `under_review`, which is
  the whole queue and nothing else.
- On `submitted_by_person_id`, covering only the rows where that optional column is actually
  set.

**`person_id` vs `submitted_by_person_id` is the most important pair in this table.** The
subject is the child; the submitter is the parent. Collapsing them into one column — which
is what most systems do — makes it impossible to answer "who applied for this child?" and
falsely attributes the parent's action to the child. See
[../domain/02-actors.md](../domain/02-actors.md#5-acting-on-behalf).

**Why requests are a separate table from memberships.** A rejected request produces no
membership and must not pollute member listings; a person may submit several over time; and
review data (who decided, why) has no meaning on a membership. See
[../domain/05-membership-lifecycle.md](../domain/05-membership-lifecycle.md#2-membership-request).

**A request asks for membership of the unit, and names nothing else.** `requested_unit_id` is
**deleted**
([D-098](../decisions/round-10a.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority)),
along with the index over it. ~~The applicant may express a preference, or the organization may
assign the unit at approval.~~ **Withdrawn by D-098**, which also removed the thing the column could
have referenced
([D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)).
The want behind it is real — a reviewer would like to know where the applicant expects to turn up —
and it is served by the free-text `notes` the row already has, which is what the field always
actually was: a sentence addressed to whoever reads the request, carrying no authority. Placing the
person is a separate act and a separate row — one `person_group_member` row, written by a person
holding `person_group.member.manage` — and an approved request with no group beside it is a
complete, ordinary outcome. **Which group a new member lands in is a write on the group, not a
preference on the request.**

**A rejection requires a reason code** (`ck_request_rejection_reason` is the rule's name): no
rejected request may be written without one. Two columns of the same row, so a migration can state
it directly as a check on the row — and it belongs there rather than only in the model layer,
because the two paths that most need catching, an import and a hand-corrected row, never reach a
model-layer guard. "Why was this
application turned down?" is asked months later, sometimes by the family. A rejection with
no recorded reason is an answerable question made unanswerable.

**`previous_membership_id`** is what makes the returning-member chain explicit rather than
inferred from date arithmetic.

---

## 3. `membership`

**Fields**

| Field | Kind | Notes |
|---|---|---|
| `id` | surrogate id | Internal only. |
| `public_id` | uuid, required, generated | The identifier used outside the system; unique. |
| `person_id` | reference to `person`, required | |
| `membership_type_id` | reference to `membership_type`, required | |
| `status` | text, required | One of `pending_payment`, `active`, `suspended`, `lapsed`, `terminated`, `completed`. No default — the state is always chosen deliberately. |
| `valid_from` | date, required | |
| `valid_to` | date, optional | NULL = open / current. **Never NULL on an imported row** — both ends are what makes an imported membership safe, and check 1 of [06-audit-and-import.md §5](06-audit-and-import.md#5-integrity-checks) counts the rows that broke it ([D-093](../decisions/round-09.md#d-093--the-one-off-import-may-create-memberships-both-ends-dated)). |
| `joined_via_request_id` | reference to `membership_request`, optional | |
| `renewed_from_membership_id` | self-reference to `membership` (the previous one), optional | Forms the renewal chain. See domain/05 §6. |
| `outstanding_balance` | money amount, optional | **Denormalised** from `fee_obligation`/`payment`. [07-finance.md](07-finance.md) §3 recommends **dropping** this column in favour of `v_fee_obligation_balance` — a wrong balance suspends the wrong child. Kept here only until that decision is taken. **NULL on every imported row, and since [D-093](../decisions/round-09.md#d-093--the-one-off-import-may-create-memberships-both-ends-dated) put memberships back into the import that is load-bearing rather than incidental:** the export carries no payment data, and a zero would be a claim — *settled* — that the export does not support. There is no `fee_obligation` underneath these rows either, which is what makes the NULL unambiguous rather than merely uncomputed ([07-finance.md §2](07-finance.md#2-minimal-provisional-shape), [D-090](../decisions/round-07-08.md#d-090--the-legacy-corpus-is-thousands-of-roster-rows-with-numbers-and-no-money)). |
| `termination_reason_code` | text, optional | |
| `termination_note` | text, optional | |
| `ended_by` | reference to `person`, optional | |
| `ended_at` | timestamp, optional | |
| `data_confidence` | text, required, defaults to `high` | One of `high`, `medium`, `low`. |
| `import_batch_id` | reference to the import batch, optional | Set on imported rows. |
| `notes` | text, optional | |
| `created_at`, `created_by`, `updated_at`, `updated_by` | timestamp, audit time; reference to `person` | The standard audit columns. |

**Rules**

- Where both ends of the period are set, `valid_to` is later than `valid_from`.
- A `terminated` membership has **both** a `termination_reason_code` and an `ended_at`.
- A membership may not be renewed from itself: `renewed_from_membership_id` never points at its
  own row.
- **THE critical rule — one person, one membership, full stop.** Two rows for the same person
  may not cover the same date while either of them is `pending_payment`, `active` or
  `suspended`. Periods are half-open, so one ending on a day and another beginning on that day
  do not collide. Statuses outside those three are outside the rule entirely, and the rule
  reaches every person regardless of membership type — the type is not part of it, and that
  omission is deliberate, as the next section explains.

**Indexes**

- `ix_membership_current` — per person, over rows that are open **and** `active`. The
  membership gate reads through this, and it is the index a far-future sentinel date would
  defeat — see *Why `valid_to IS NULL` and not a sentinel* below.
- On `valid_to` over active rows that have one. **This drives the renewal worklist: who
  expires soon, who is in their renewal window.**
- On (`status`, `valid_to`) over `active` and `pending_payment` rows — the states anyone is
  actually queried in.
- On `person_id` with `valid_from` descending, and a period index per person: one person's
  membership history, and the range scan the overlap rule and every point-in-time question use.

### The constraint dropped `membership_type_id` — that is the point

The old constraint was scoped to the type, to permit an honorary member who is also an
active member. **With one membership type (D-037) that case cannot arise**, so the type is
gone from the constraint and "one person, one open membership" becomes an enforceable
invariant rather than a convention. It is conditional uniqueness — one open row per person —
which is the shape [00-conventions.md §6a](00-conventions.md#6a-who-enforces-an-invariant-now)
says a migration must emit by hand: a unique constraint over *all* rows is a different rule and
the wrong one, because it forbids the second closed membership that the person's history
requires.

This is what makes `is_current_member()` a question about **one row, one status, one date**, rather
than one that has to reconcile three concurrent memberships. That is worth keeping in mind now that
the predicate's consumer has changed: the resolver no longer calls it per grant, because the
membership gate left the resolver for the `MEMBERS` selector (§6,
[D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)),
but `MEMBERS` is evaluated live on the checked date and evaluates to exactly this predicate. The
constraint is what makes that evaluation cheap and unambiguous either way.

### `renewed_from_membership_id` and the renewal window

When a person pays inside the renewal window
([D-040](../decisions/round-02-03.md#d-040--the-fee-expires-yearly-a-date-tracked-renewal-window-replaces-a-grace-status)),
the new membership's `valid_from` is set to the **previous row's `valid_to`**, not to the
payment date. Two consequences worth stating:

- **The history shows continuous coverage** — no gap, no spurious "returning member".
- **The person is nevertheless expired during the window** (D-040). The two facts are
  compatible because the window is a *date range*, not a status: they were not a member
  while it was open, and the record of that period is filled in retrospectively once they
  pay. Nothing needs backdating in the audit sense, because the new row's as-of start is the
  expiry date and its audit time is the payment date — the two-times distinction in
  [00-conventions.md](00-conventions.md).

A payment *after* the window opens the new membership at the payment date, and the gap is
real.

### The exclusion constraint and status transitions

The overlap rule covers only `pending_payment`, `active`, `suspended`. A
`terminated`/`lapsed`/`completed` row is excluded, so a new membership can be created with
a `valid_from` inside an old one's period without violating the constraint. **This is
deliberate** — a returning member's new membership may legitimately overlap the tail of a
lapsed one if the dates were entered imprecisely. Historical imports rely on this.

**Consequence:** the constraint does not prevent two *active* memberships with overlapping
periods if one was inserted while in another status and then transitioned. A status update
re-evaluates the constraint (PostgreSQL does check exclusion constraints on UPDATE), so
this is safe — but the transition from `lapsed` back to `active` can therefore **fail with
a constraint violation**. That is correct behaviour: it means the person has two
overlapping claims to membership and someone must resolve it. Handle it as a business
error, not a crash.

**Which layer carries all of that: the migration.** A status transition that re-checks the overlap
is only a violation if the constraint is in the database, and no ORM emits an exclusion over a
period assembled from `valid_from` and `valid_to` scoped to three statuses — the migration writes
it, as [00-conventions.md §6a](00-conventions.md#6a-who-enforces-an-invariant-now) requires. The
same check performed in the model layer returns a friendlier message a moment earlier and
guarantees nothing: a batch that imports the legacy people export writes memberships by the thousand
again. [D-090](../decisions/round-07-08.md#d-090--the-legacy-corpus-is-thousands-of-roster-rows-with-numbers-and-no-money)
took that sentence away last round, on the reading that the corpus produces participations only, and
[D-093](../decisions/round-09.md#d-093--the-one-off-import-may-create-memberships-both-ends-dated)
gives it back; §5 keeps the record of both readings. **Round 10 removes the participations altogether**
([D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)), and the
argument here never depended on them: it rests on the memberships the people export produces, and on the
hand-corrected row that never passes through the model layer either. Both meet the constraint in the
database; neither would ever meet a model-layer check.

### Why `valid_to IS NULL` and not a sentinel

Repeated from the conventions because it is the mistake most likely to be made here.
A `'9999-12-31'` sentinel breaks `IS NULL` checks, makes `daterange` spans enormous, and
defeats the `ix_membership_current` partial index. Use NULL.

### `renewed_from_membership_id`

Renewal opens a **new** row (Shape A in
[../domain/05-membership-lifecycle.md](../domain/05-membership-lifecycle.md#6-renewal-and-the-yearly-fee)).
The self-reference makes the chain explicit:

```
membership 501  member  1990-09-01 → 1991-06-30   completed
     ↑ renewed_from
membership 502  member  1991-09-01 → 1992-06-30   completed
     ↑ renewed_from
membership 503  member  1992-09-01 → 1993-06-30   completed
```
*(The type is `member` on every row — there is only one type, and the person's age is not
part of it: [§1](#1-membership_type--one-row-kept-as-a-table), D-037, D-038.)*

"Why does this person have 15 membership rows?" is then answerable by following the chain
rather than by reasoning about dates. And a gap — a missing link — is visible as data.

### Current-membership queries

Five questions the membership table has to answer, each with the exact rule that decides it.
The wording of each is load-bearing; the differences between them are the design.

* **Is this person a member right now?** `is_current_member(person)` — true when they have a
  membership whose status is `active` and whose period covers today: `valid_from` on or before
  today, `valid_to` absent or after today. **No grace coalescing:** a lapsed membership is
  lapsed, and the renewal window
  ([domain/05 §6](../domain/05-membership-lifecycle.md#6-renewal-and-the-yearly-fee)) is a date
  range for rejoining, not a state in which the person is a member. **This predicate is what the
  `MEMBERS` selector evaluates** on the checked date (§6) — it is no longer called by the resolver
  on someone else's behalf, which changes its callers and not its meaning.
* **Was this person a member on a given past date?** `was_member_on(person, date)` — true when
  a membership of theirs covers that date, on the same half-open terms, and its status is
  anything **except** `pending_payment`. Note the asymmetry with the question above: *now*
  demands `active`, *then* admits every terminal status, because how a membership ended does not
  change that it existed.
* **When does the organizational year containing a date expire?** `membership_expiry_date(as_of)`
  — `expiry_month` and `expiry_day` read off the `member` row, applied to the year of `as_of`.
  Always derived from those two columns and never from a constant (D-047).
* **May this person renew without re-applying?** `in_renewal_window(person, as_of)` — true when
  they have a membership of theirs that has ended (`valid_to` set) with `valid_to` on or before
  `as_of`, and `valid_to` plus that type's `renewal_grace_days` still after `as_of`; in other
  words the window is `[expiry, expiry + grace)`, half-open like every other period here. No
  status is consulted — this is arithmetic on dates alone. D-040: expired, but inside the
  window. This is the distinction a `grace_period_days` membership status would have blurred:
  they are **not** a member, and they **may** rejoin cheaply. 60 days, read from the row
  (D-048). Not a member during the window: this answers "may they rejoin cheaply?", never "do
  they have access?".
* **How long has this person been a member?** `membership_years(person)` — the sum of the
  lengths of their memberships, with today standing in for an open `valid_to` and any
  `pending_payment` row left out, expressed in years of 365.25 days.

`membership_years` sums the periods rather than subtracting the first join date from today.
The difference is the 14-year gap in the returning-member case, and getting it wrong
mislabels a returning member as having 36 years of service.

**`current_member_category()` is gone.** It existed to answer "is this person currently a
child or an adult?", which is no longer a question the membership table can answer, because
membership is ageless (D-038). Age is a fact about the person:

**Is this person a minor?** `is_minor(person, as_of)` — true when `person.birth_date` is
recorded **and** `as_of` falls before their eighteenth birthday. A person with no recorded birth
date is not a minor by this test; nothing guesses one. A fact about the person, never about
their membership.

This matters for **guardianship and safeguarding**, which are where age legitimately bears —
not for whether someone may be a member.

---

## 4. No request requirements — removed entirely

`requirement_code` and `membership_request_requirement` **do not exist** (D-044).

**Why.** Your answer, asked what a membership request must contain in order to be accepted:
*"Just identity and the fee — nothing to verify."* The option of keeping the mechanism as
empty infrastructure was offered and not taken, so it is gone rather than left dangling.

**What a request therefore is:** a person, a submitted timestamp, a reviewer, a decision, and
a payment. The `membership_request` table in [§2](#2-membership_request) is complete as it
stands — it never referenced requirements except through this table.

**Guardian consent is unaffected.** It was never a *membership* requirement; it belongs to
the guardianship layer, where it is a relationship fact rather than a checklist item. See
[04-relationships.md](04-relationships.md#2-the-guardians-right-none-view-or-write).

**If a requirement ever appears** — a form, an interview, a document — the honest starting
point is to add the table back deliberately, with the requirement that made it necessary
recorded as a decision. The removed design was general enough to carry one; it is recorded
in the decision log rather than deleted from history.

---

## 5. `unit_participation` — deleted by D-097

**Deleted by
[D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row).**
There is one unit, it is the organization, and it is a **scope** rather than a row — so there is no
body below it to belong to, and no table to record belonging in. Everything the table carried goes
with it: the sub-unit rosters, **the root participation row every membership owed**, the transfers
between units, `role_in_unit`, the `join_reason_code` / `leave_reason_code` vocabulary,
`is_primary`, and the `data_confidence` value those rows carried into an import.

**Why it existed, kept because the reasoning outlives the table.** ~~Belonging to a sub-unit is
**participation**, not a species of membership~~
([D-041](../decisions/round-02-03.md#d-041--belonging-to-a-sub-unit-is-a-participation-record-not-a-membership)).
The name `unit_membership` had been asserting otherwise, and the rename was the fix: a "unit
membership" read as a second species of membership, which raised questions about which membership
was which and whether a fee was owed twice, and participation removed the questions. **That
distinction is still true one level down** — membership of a group confers nothing and owes nothing,
no more than belonging anywhere else does, because participation is not authority and the fact that
it is now stored in a tidier table does not quietly promote it
([D-098](../decisions/round-10a.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority),
restating
[D-005](../decisions/round-01a.md#d-005--permissions-are-grants-never-derived-from-identity)).
The same holds for the column this document argued hardest for: `person_id`, never `membership_id`,
because a person may belong somewhere with no membership behind them and a row about 1998 must not
become unrepresentable because the record of 1998 status is thin or absent. `person_group_member` is
keyed on a person for that same reason and inherits the argument whole.

**Where each question goes now** ([D-098](../decisions/round-10a.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority))
— two shapes, and no longer one shape with a depth in it:

| Question | Read |
|---|---|
| Who is in the organization on date D? | `membership` — one query over the period and status of §3 |
| Who is in group G on date D? | `person_group_member` — a point-in-time read over the dated rows, [02-organization.md §1](02-organization.md#1-person_group) |

The one thing the deleted §5.1 bought was a **single query shape for both rows of that table**, and
that is what is given up. What is given back is the redundancy: two tables kept in step only by an
obligation on every writer, and a report watching for the writers who forgot.

### The write obligation is retired, and so is the check that watched it

**The import owes no participation rows to anything**
([D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)).
The old §5.1 required that **no write may change a membership's period, or open or close one,
without making the matching change to that person's root-unit participation row in the same
transaction** — two rows holding one fact — and integrity check 1b was the report that found whoever
skipped it.

**Who enforces that rule now: nobody, because there is nothing left to enforce.** The second row is
deleted, so the pairing is not a rule running without a guard, it is a redundancy that has been
removed; `membership` is the single record and cannot disagree with a copy of itself. Both the
obligation and check 1b retire rather than being restated somewhere else, which is the outcome D-081
asks for stated plainly rather than left as a silence.

> **Marked withdrawn rather than deleted, because this obligation was reversed twice inside three
> rounds and a reader is entitled to the whole record.** ~~When a membership is created, a matching
> `unit_participation` row for the root unit is created over the same period, and similarly closed
> when the membership ends.~~ Round 8 corrected the section to say an ordinary import "touches
> neither arm of this pair", because a roster produced participations and no memberships; round 9
> reversed the correction
> ([D-093](../decisions/round-09.md#d-093--the-one-off-import-may-create-memberships-both-ends-dated)),
> because the corpus turned out to state membership periods after all; round 10 deleted the arm both
> readings were arguing about. Every step of round 8 was true of the input it was describing, and
> the input was described wrong
> ([D-092](../decisions/round-09.md#d-092--the-corpus-is-people-and-events-and-it-names-no-units)).
> What each round got right and keeps is the framing rather than the conclusion: **the obligation
> was never about one batch** — import, renewal, extension and hand-corrected row each owed the
> paired write exactly as much — and the reason the answer moved twice is that nobody had read the
> file. That is worth remembering about imports in general, and the reversals are recorded against
> D-093 and the round-10 block rather than being quietly unwritten here.

~~The root row was the only participation row that is *extended* rather than closed and reopened~~
([D-050](../decisions/round-04.md#d-050--a-renewal-inside-the-window-extends-the-existing-root-participation-row)):
the yearly sweep moved its open end to the expiry date and a renewal inside the window stretched the
same row to the new period's end, so a person who lapsed and renewed looked exactly like one who
never had. **Withdrawn with the table**, and the condition that made the match exact — the renewal
beginning exactly where the row was swept to, matched by person and date because the row carried no
membership reference — goes with it, as does the accepted cost that the lapse stopped being visible
in the roster. What is worth keeping is why the trade was acceptable: the roster answers *who was in
this body when*, and for that question a child who was there across the lapse has exactly one
answer, while `membership` remains the authority on payment. With the row gone both facts live in
`membership` alone; **the renewal rule that backdates the new period is untouched** (§3, and
[../domain/05-membership-lifecycle.md
§6](../domain/05-membership-lifecycle.md#6-renewal-and-the-yearly-fee)).

### Moving between groups closes one row and opens another

[D-098](../decisions/round-10a.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority)
retargets this section's discipline at groups and changes nothing else: **moving a person from one
group to another is two writes, closing one `person_group_member` row and opening another**, never
an edit of the group on the existing row. Close-and-open is what preserves "where was this child in
2003?"; an in-place update destroys it, and the whole temporal design exists to answer that
question. Nothing about the person's membership, their fee, or their standing as a member changes,
because moving was never a membership event — which is exactly the expense D-041 removed when it
made belonging below the organization a different fact from being a member, and which is why the
same discipline survives the move to a different table.

**Who enforces it now.** The close-and-open pair is the write path's, behind
`person_group.member.manage`, audited and naming who wrote the row; the invariant underneath it —
**no two rows for one person and one group overlap, counted over all rows and not only the open
ones**, half-open so a row ending on a day and one beginning that day do not collide — is [open
question
F-10](../open-questions.md#f-10--which-invariants-the-orm-cannot-express-and-who-writes-those) shape
1, which a hand-written migration emits and the ORM will not. A person who left in 2020 and came
back in 2024 is therefore **two rows, never one row edited in place**: the edit destroys the answer
to "was she in the group in 2019?". The groups module owns both, and this document does not
re-specify them — [02-organization.md §1–§2](02-organization.md#1-person_group) and
[../domain/04-organization-structure.md](../domain/04-organization-structure.md).

**What died with the unit version of this, named as a loss.** A group that splits is an old group
that ended and two that began, **with no edge between them unless somebody writes one**:
`org_unit_relationship`'s `split_from` / `merged_into` / `successor_of` are deleted, so
restructuring has stopped being a recorded event
([D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)'s
third loss). The bulk unit-reorganisation transfer — close and open across every member, with
`join_reason_code = 'reorganisation'`, as one named procedure with a dry run because it will be run
over hundreds of rows — goes with it. There is no reorganisation to perform in one statement, and
the lineage it recorded is now a thing a person would have to write down on purpose.

**The other columns, given up rather than moved**
([D-098](../decisions/round-10a.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority)
lists them, and "no special features" was the instruction): no `join_reason_code` /
`leave_reason_code` and so no `transfer` / `promotion` / `reorganisation` / `unit_closed` vocabulary
to maintain or to get wrong, no `is_primary` saying which of a person's groups to show first, no
`role_in_unit` display label, and no `data_confidence` with nothing left to import into — the corpus
names no groups either, so every group member row is typed by a person, which is also the only way
one can be true
([D-092](../decisions/round-09.md#d-092--the-corpus-is-people-and-events-and-it-names-no-units)).

---

## 6. Membership and the authorization system

**The resolver no longer asks whether you are a member. The grant does.** This is the round's
largest deletion
([D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)),
and it is still the single largest coupling between these two modules, so it is stated in full
rather than in a footnote. What was withdrawn:

```
~~A role grants access ONLY IF the holder has a current membership,~~
    ~~unless  role.requires_membership = false    (appointed counselors, local leaders)~~
    ~~or      the channel is guardianship         (a legal relationship, not a membership)~~
    ~~or      the channel is ownership            (your own record — see below)~~
```

**Withdrawn by D-100.** The clause above ran on every grant the resolver examined, and it needed two
escape mechanisms to be livable. `MEMBERS` is now a selector operand, evaluated live on the checked
date, and the question "must this person be a current member to hold this?" is answered by whether
the expression says so:

| Old mechanism | New expression |
|---|---|
| The gate applied to a role with `requires_membership = true` | `MEMBERS * ROLE(x)` |
| The gate waived for a whole role | `ROLE(x)` — write it without `MEMBERS` |
| The gate waived for one named person (`system.gate_exempt`) | `MEMBERS * ROLE(x)`, plus a second grant for that one person |

`role.requires_membership`, `system.gate_exempt` and `person_holds_gate_exempt` are all deleted,
together with the resolver's membership clause and the special-case path that had to be carefully
kept *out* of `can()`. **Who enforces the rule now: whoever writes the grant**, by putting `MEMBERS`
in the expression or leaving it out, and the expression is a row that can be read.

*Corrected in this round:* an earlier draft of this page read D-100's `PERSON(y)` as shorthand for the
audience's own `LIST`, on the grounds that the seeded `selector_type` registry did not carry the code. **The
registry was the side that was wrong** — `PERSON` was seeded then, as the thirteenth row
([data-model/05 §8](05a-audience-and-grammar.md#the-selector-registry), [D-101's amendment](../decisions/round-10b.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree)),
so `MEMBERS * ROLE(x) + PERSON(y)` parses as written. **`LIST` was never a substitute**, which was the part
worth remembering at the time: it is one set belonging to one audience, so `+ LIST` brings everybody on it and
nothing on that list can except one person from itself. **That confusion can no longer recur**, because
[D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)
deleted `LIST` and its table in the round after this correction was written, leaving twelve seeded rows — fourteen
since [D-107](../decisions/round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded) put age in the language — and one way to name a person by hand — which is the outcome the paragraph was arguing for, arrived at by deleting the
thing it had to argue against. Writing the waiver as **a second grant aimed at the person** is still legal and
still clearer for something permanent, and is now the only way to date it
([D-105 §2](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)).

**Two of the three carve-outs were never carve-outs.** **Guardianship** (a parent's authority comes
from a legal relationship, and an unpaid fee must not stop a parent acting for their child) and
**ownership** (otherwise a lapse locks a person out of the very screen they renew on) stay channels
and are unaffected — they were never gated, whatever the shape of that block suggested. Only the
third, the appointed counselors and local leaders the organization needs present regardless of their
own fee status, was a real waiver of a real gate, and it is now the second row of the table: write
the office without `MEMBERS`.

**The posture reverses, and the new failure mode is named rather than buried.** The gate was
**default-on**, so forgetting it was impossible. It is now **opt-in per grant**: a grant written
`ROLE(TREASURERS)` with no `MEMBERS` authorizes a lapsed member, silently, forever. Three controls,
none of which is the resolver:

- **A standing report** of live grants naming a `ROLE(...)` operand whose expression does not contain
  `MEMBERS` — check 1 of §7. An office held by a non-member is the case worth a human eye, and the
  report is narrow enough to actually be read.
- **Seeded grants and any grant template carry `MEMBERS`**, so the path of least repetition is the
  safe path.
- **Import completeness.** `MEMBERS * COUNSELORS` is only as correct as the counselor roster: the
  gate used to
  fall out of membership alone, so an import that misses 300 counselors silently un-gates them. It fails
  closed — nothing breaks, which is exactly why nobody notices — and the import reconciliation report of
  [D-090](../decisions/round-07-08.md#d-090--the-legacy-corpus-is-thousands-of-roster-rows-with-numbers-and-no-money)
  must count people marked as counselors in the corpus against `role_holder` rows written.

**What still costs, unchanged by the move:**

- ~~**The permission cache must be invalidated on every membership transition** — including the yearly
  expiry sweep, which is a bulk event touching every member at once.~~ ~~The coupling did not leave with the
  resolver clause: `MEMBERS` is evaluated live, so a transition still changes who an expression reaches.
  **The cache design has to be built for this from the start; retrofitting it is where the bugs will be.**~~
  **This requirement is discharged by deletion, and it has to be struck rather than left as history, because it
  was a live instruction aimed at a table that no longer exists**
  ([D-114](../decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation)).
  **Read it against the page it was aimed at.** This sentence was written in the round that moved the membership
  gate out of the resolver, three rounds *before* [D-111](../decisions/round-13.md#d-111--the-permission-cache-is-rebuilt-nightly-on-any-ruleset-change-and-on-request)
  wrote the cache policy — and when that policy was finally written, **`membership` was not on its invalidation
  list**, while `membership.terminate` is precisely the ⛔ action a concerned guardian waits for. The sentence
  here was right, the page it was asking for did not hear it, and the way to close a coupling like this one is not
  a louder requirement but an invariant that has nowhere to be violated: `MEMBERS` is evaluated live at the
  checked date, there is no answer stored to go stale, and
  [D-111](../decisions/round-13.md#d-111--the-permission-cache-is-rebuilt-nightly-on-any-ruleset-change-and-on-request)'s
  claim that *"the safeguarding case is immediate"* is true here by construction instead of by trigger.
  ~~D-101 helps rather than excuses it — a cache may key on an operand and reuse it across every grant~~ — and
  the yearly expiry sweep keeps every other thing it had to do; what it no longer has to do is invalidate
  anything, because
  [§11's invariant 19](05d-invariants-and-seed.md#11-invariants-to-verify) forbids the row that would need it.
- **A lapse silently removes access** — from exactly those grants whose expression names `MEMBERS`,
  and from
  none of the others. "Why can't I see this?" now has an answer that is a date *and* a line of grant
  text.

**The "leaver with access" report remains valuable, and it is now two reports.**
[D-071](../decisions/round-05.md#d-071--nothing-forces-a-role-assignment-to-end-the-gate-and-the-report-are-the-control)'s
posture transfers intact to `role_holder`: nothing forces a holder row to end, and the control is
the report. Checks 1 and 2 of §7 are that control — one for grants that gate nothing, one for
offices held by people who are not members.

**Dormant authority is a real hazard, and slightly larger than it was.** A membership that lapses
and is renewed a year later resurrects every still-open `role_holder` row the person accumulated in
the interim, including ones a human had quietly decided not to reinstate — and where the grant
behind that role was written without `MEMBERS`, it was not dormant at all in the meantime, it was
live. Closing the holder row at the same time as the membership is the honest fix; the reports find
the ones that were missed. **A role holder row should not outlive the membership that justified
it.**

**A role is held at the unit and nowhere else.** `role_holder` carries no scope columns, because
[D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)
left one scope; there is no body to hold an office *of*. The table, the `ROLE(x)` selector and the codes
an office carries belong to [05-authorization.md §3 `role` and §4 `role_holder`](05-authorization.md#3-role--an-office).

---

## 7. Integrity checks

**Invariants to verify.** **The numbering restarted at 1 this round.** Every check below old 3
either lived or died with `unit_participation`, and leaving holes in a renumbered list is only
honest while the surviving numbers still mean what their citations claim — which they no longer
would. The retired numbers, and what happened to each, are listed after the live ones, because the
decision log cites "integrity check 2 of `03-membership.md §7`" by name and that citation should
land on an explanation rather than on a gap.

* **1. Live grants that gate nothing.** Counts live grants whose audience expression names a `ROLE(...)`
  operand and does not contain `MEMBERS` — D-100's standing report, restated here because this is
  the module whose data it reads. **Enforced by no layer, and no layer can**: whether an office is
  written with `MEMBERS` is a choice made in the grant text, so the controls are this report, plus
  seeded grants and any template carrying `MEMBERS` so the common path is the gated one (§6). **A
  non-zero count is not a fault** — it is the list of offices worth a human eye, and it is narrow
  enough to actually be read.
* **2. Non-members holding an office.** Counts open `role_holder` rows whose holder
  `is_current_member()`
  says is not a member (§3). **Enforced by nothing, deliberately**:
  [D-071](../decisions/round-05.md#d-071--nothing-forces-a-role-assignment-to-end-the-gate-and-the-report-are-the-control)'s
  posture transfers to `role_holder`, so no constraint and no sweep ends a holder row and this
  report *is* the control. Read it with check 1, which says whether that role's grants are gated: on
  a gated role this is **dormant authority** that springs back to life at the next renewal, and on
  an ungated one it is access that is live today (§6). The old wording of this check — "the resolver
  blocks these, so it is not an access breach" — is the sentence the round retired, and it must not
  be copied forward.
* **3. Approved requests that never produced a membership.** Counts requests that are `approved`,
  carry no
  `membership_id`, and were decided more than seven days ago. Non-zero is an approval that went
  nowhere. **Enforced by** the §2 requirement that an approved request points at a `membership` once
  the deciding transaction is over — a deferred reference rather than a suggestion, and one a
  migration can state on the row.
* **4. Memberships expiring soon.** Counts `active` memberships ending within the next 90 days — the
  renewal
  campaign worklist ([domain/05
  §6](../domain/05-membership-lifecycle.md#6-renewal-and-the-yearly-fee)), not a fault. **Run by
  whoever runs the campaign**; nothing here guards it, because there is nothing to guard.
* **5. Renewal chains with a broken link.** Counts memberships whose `renewed_from_membership_id`
  names a row
  that does not exist. Non-zero means the chain is followed into nothing. **Enforced by** the
  ordinary foreign key on that column, which any migration emits; the check survives as the
  assertion that the key is there, which is the form [00-conventions.md
  §6a](00-conventions.md#6a-who-enforces-an-invariant-now) prescribes for a constraint this
  project's ORM does not generate on its own.
* **6. Renewals inside the window whose new period does not start at the previous expiry date.** Counts
  renewals whose `valid_from` differs from the previous membership's `valid_to` and begins less than
  91 days after it. The renewal rule (D-040) backdates the new period, so a mismatch means either a
  genuine post-window rejoin or a bug. **Enforced by nothing**: both answers are legal data, so only
  a report separates them, and only a reader decides which one it is looking at.

**Checks 1 and 2 are the ones that matter now**, and they are what the old check 3 became. The old
check could assume the resolver had already handled access and confine itself to the stale row
behind it; that assumption was the gate, and with the gate in the grant text the same predicate
splits into a report about grants and a report about people. Neither one alone is the control.

**Check 4 is operational** (a worklist for the renewal campaign). The rest are data-quality checks
for cases no constraint rejects at the write.

**Two checks this module deliberately does not hold.** The one [D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)
asks for — a live `deny` whose grantee, scope and code match no live allow, and so denies nothing — is a
report over grants, not over memberships, and belongs to
[05d-invariants-and-seed.md §11](05d-invariants-and-seed.md#11-invariants-to-verify). The no-overlap invariant over
`person_group_member` belongs to the groups module, [02-organization.md §6](02-organization.md#6-integrity-checks).
Naming both here is to stop either being written twice and drifting.

**Retired with `unit_participation`** (§5), listed so that a citation of an old number lands somewhere:

| Old | Was | Where it went |
|---|---|---|
| 1 | participation rows with no membership at that time | Deleted with the table (D-097). Its reasoning survives as a caution rather than a query: the check spent two rounds carrying an import exclusion because every imported row satisfied the predicate by design, which is the shape of a report whose floor is thousands of meaningless findings — worth remembering before writing any "row without its obvious partner row" report here |
| 1b | the root participation row disagreeing with the membership it mirrored | Deleted with the redundancy it watched (§5). There is no second row, so there is nothing to disagree and no writer left to name |
| 2 | ⚠ participants in units that do not allow minors | Withdrawn by [D-095](../decisions/round-09.md#d-095--units-carry-no-restrictions-joining-one-is-somebody-elses-act) one round before the table itself went. **Who enforces the rule now**: `person_group.member.manage`, held at the unit — which reaches every group — or granted on one group as an item, audited and naming who wrote the row (D-098). **What is lost** is unchanged and unrecoverable: no column says which groups take children, so the system can neither answer the question nor report on it |

---

## 8. Seed data

The organization starts with a single membership type — `member`, named and described in plain
words, open for a person to register themselves for, and left to `requires_approval` at its
default of true. The term and the calendar parameters on that row are §1's, not constants
anywhere else.

**One row, and that is the whole vocabulary** (D-037). The fee is flat and per person, so
there is nothing to vary by type; being a counselor or a leader is a **role**, not a type
([D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape));
and membership is ageless, so there are no age limits to seed (D-038).

**Nothing else is seeded here.** The `counselors` role that D-100 seeds — shipped `is_system`, so an
editor refuses to delete it — is a row of the authorization module
([05d-invariants-and-seed.md §12](05d-invariants-and-seed.md#12-what-the-organization-starts-with)) and not of this one,
and it is a **set** that confers nothing until a grant names it: no more than a membership type has ever
conferred.

**All three are settled, and all three are §1's columns** — 12 months, 1 January, 60 days
([D-047](../decisions/round-04.md#d-047--the-fee-expires-on-1-january),
[D-048](../decisions/round-04.md#d-048--the-renewal-window-is-60-days-and-is-a-configuration-parameter)).
**The sentence this one replaces called the 12-month term "a placeholder that nothing currently
depends on", and that was stale in two directions at once.** It is §1's `duration_months` default,
stated there as a value with a reason attached (the fee is yearly), and things do depend on it: the
yearly lapse sweep ([07-finance.md §4](07-finance.md#4-how-this-connects-to-membership)) and the
period a renewal opens both read a term, and a term of the wrong length produces a membership that
ends on a date nobody chose. What survives the correction is the part that was always the point —
**none of the three is a constant**, so tuning any of them is an `UPDATE`, not a release, and the
difference between a settled value and a hard-coded one is exactly that difference.

> **The one rule about these four values: read them from the row.** A scheduled job, a front
> end or a report that contains the literal `60` or `1` has quietly reverted a parameter to a
> constant, and the organization will discover it the first time it changes its mind.

**No `requirement_code` seed.** That table does not exist (D-044). The formerly seeded rows
— `guardian_consent`, `background_check`, `medical_form`, `references`,
`previous_unit_transfer`, `photo_consent` — are all gone:
consent moved to the guardianship layer where it belongs, background checks are not recorded
at all (D-043), and the rest were never required.

---

## 9. Open issues

- Nothing about the type-level parameters is open any more (§1, §8): 12 months, 1 January and 60
  days are all settled and all three are columns read from the row. **What is left of this bullet is
  a question about the values rather than about the mechanism** — whether 60 days is the right
  window for an organization whose renewal campaign is a handful of people, which only a year of
  real lapses can answer.
- Whether `outstanding_balance` should exist as a denormalised column or be computed
  (§3) — depends on the finance design in [07-finance.md](07-finance.md).
- **Which offices are written without `MEMBERS`.** The membership gate left the resolver for the grant
  text (§6, D-100), so somebody has to decide, per office, that a lapsed member may still hold it —
  and nothing in the model records who decided it or why, only whether the expression contains the
  word. The standing report of §7 check 1 is the control over the outcome, not over the choice.
  *Assumption:* this is left to whoever writes the grant, which is the honest reading of D-100
  rather than a ruling in it.
- Whether a group is ever allowed to state an age rule of its own — the question `position.min_age`
  used to
  answer for offices, which
  [D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)
  deleted along with positions, and which nothing in the round-10 model answers for groups either: a
  group carries no eligibility, and
  [D-098](../decisions/round-10a.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority)
  refuses it one. Left as a question for [../open-questions.md](../open-questions.md) rather than
  answered here; today the answer is a report over `person_group_member` and `is_minor()`.

**Resolved and no longer open**, kept visible so the reasoning survives: whether a person may hold
several open memberships (no — one type, person-scoped constraint, §3); whether membership activates
on payment (yes, §3); whether permissions depend on membership state (it did, through a resolver
clause — D-039; since D-100 the grant says so itself with `MEMBERS`, §6, and the carve-outs turned
out to be channels that were never gated); the age limits and age-out (§8); the grace period as a
status (§6 of domain/05); the whole requirement mechanism (§4); **whether `unit_participation`
should reference the membership** for referential integrity (moot — the table is deleted, D-097, and
open question D-8 retires with it. The argument is kept because it recurs: the pointer was refused
because participation had to survive without a membership, which is precisely why
`person_group_member` is still keyed on a person and not on a membership, §5); what the root-unit
participation row did when a membership was renewed inside the window (**extended across the
retrospectively filled period, never closed and reopened — D-050. The row is gone, D-097, and the
answer is kept because the reasoning about backdated periods is what the renewal rule in §3 still
rests on**; the same rule had reached the imported consecutive periods D-093 introduced); and
whether the legacy import may create a `membership` at all (**yes, bounded at both ends,
`data_confidence = 'low'`, one row per period the source states —
[D-093](../decisions/round-09.md#d-093--the-one-off-import-may-create-memberships-both-ends-dated),
after a round in which the answer was no; the reasoning either way is [06-audit-and-import.md
§3.1](06-audit-and-import.md#31-what-a-source-row-actually-evidences)**).

All tracked in [../open-questions.md](../open-questions.md).
