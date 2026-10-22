# Data Model — Membership

`membership_type`, `membership`, `membership_request`, and `unit_participation`.

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
`membership_type = 'member'`, the fee is flat and per person, and being a counselor or a
leader is a **position**, never a type.

The table survives rather than collapsing into a constant for two reasons:

1. **Consistency with the design's own principle.** Vocabularies are rows, not enums —
   the same argument that keeps `org_unit_type` and `position` as tables. A second kind of
   membership (a supporting or honorary one) would then be a data change.
2. **A place for the organizational calendar to live.** The term, the expiry date and the
   renewal window are genuinely type-dependent parameters even when there is one type — and
   they are the parameters most likely to be tuned. Putting them in a row rather than in code
   is what makes *"it should not be hard to modify"* ([D-048](../decisions/decision-log.md#d-048--the-renewal-window-is-60-days-and-is-a-configuration-parameter))
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
| `requested_unit_id` | reference to `org_unit`, optional | The applicant may express a preference, or the organization may assign the unit at approval. |
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
- On `submitted_by_person_id` and on `requested_unit_id`, each covering only the rows where
  those optional columns are actually set.

**`person_id` vs `submitted_by_person_id` is the most important pair in this table.** The
subject is the child; the submitter is the parent. Collapsing them into one column — which
is what most systems do — makes it impossible to answer "who applied for this child?" and
falsely attributes the parent's action to the child. See
[../domain/02-actors.md](../domain/02-actors.md#5-acting-on-behalf).

**Why requests are a separate table from memberships.** A rejected request produces no
membership and must not pollute member listings; a person may submit several over time; and
review data (who decided, why) has no meaning on a membership. See
[../domain/05-membership-lifecycle.md](../domain/05-membership-lifecycle.md#2-membership-request).

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
| `valid_to` | date, optional | NULL = open / current. |
| `joined_via_request_id` | reference to `membership_request`, optional | |
| `renewed_from_membership_id` | self-reference to `membership` (the previous one), optional | Forms the renewal chain. See domain/05 §6. |
| `outstanding_balance` | money amount, optional | **Denormalised** from `fee_obligation`/`payment`. [07-finance.md](07-finance.md) §3 recommends **dropping** this column in favour of `v_fee_obligation_balance` — a wrong balance suspends the wrong child. Kept here only until that decision is taken. NULL for imported historical memberships with no payment data. |
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

This is what makes the membership gate (D-039) implementable: `is_current_member()` is a
question about **one row, one status, one date**, not a question that has to reconcile three
concurrent memberships.

### `renewed_from_membership_id` and the renewal window

When a person pays inside the renewal window
([D-040](../decisions/decision-log.md#d-040--the-fee-expires-yearly-a-date-tracked-renewal-window-replaces-a-grace-status)),
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
guarantees nothing: the legacy import writes memberships by the thousand and a hand-corrected
row never passes through the model layer either. Both still meet the constraint; neither would
ever meet a model-layer check.

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
  lapsed, and the renewal window (§6) is a date range for rejoining, not a state in which the
  person is a member.
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

## 5. `unit_participation`

**Renamed from `unit_membership`.** Belonging to a sub-unit is **participation**, not a
species of membership (D-041). The old name asserted something untrue, and the rename is the
fix.

**Fields**

| Field | Kind | Notes |
|---|---|---|
| `person_id` | reference to `person`, required | **Deliberately `person_id`, not `membership_id`.** Participation history must survive independently of how organization membership is recorded: imported 1998 rosters often have a unit and a year but no formal membership row, and linking to membership would make those unrepresentable — which would break the whole historical dataset. The trade-off is that nothing here can enforce "participation implies membership": it is application-level validation plus invariant 1 in §7, named as such rather than pretended away, in the register of [00-conventions.md §6a](00-conventions.md#6a-who-enforces-an-invariant-now). |
| `org_unit_id` | reference to `org_unit`, required | May be the **root** unit. A participation row on the root is created alongside each membership, so that "everyone in unit X" is one uniform question whether X is the organization or a Thursday-evening pack. See §5.1. |
| `role_in_unit` | text, optional | One of `member`, `leader`, `assistant`, `guest`. A denormalised convenience for display and historical import. **Not** an authorization fact — authority is in `role_assignment`. |
| `valid_from` | date, required | |
| `valid_to` | date, optional | NULL = current. |
| `join_reason_code` | text, optional | `initial`, `transfer`, `promotion` or `reorganisation`. |
| `leave_reason_code` | text, optional | `transfer_out`, `unit_closed` or `stopped_attending`. |
| `is_primary` | boolean, required, defaults to true | Which group to show first, for a person in several. |
| `data_confidence` | text, required, defaults to `high` | One of `high`, `medium`, `low`. |
| `import_batch_id` | reference to the import batch, optional | Set on imported rows. |
| `source` | text, optional | `self`, `staff` or `legacy_import`. |
| `created_at`, `created_by`, `updated_at`, `updated_by` | timestamp, audit time; reference to `person` | The standard audit columns. |

**Rules**

- Where both ends of the period are set, `valid_to` is later than `valid_from`.
- **A person takes part in a given unit only once at a time.** No two participation rows for the
  same person and the same unit may cover the same date. The rule covers **every row, open and
  closed alike**; taking part again later is a separate, later period and is fine.

**Indexes**

- On `person_id`, and on `org_unit_id`, both with `valid_from` descending: a person's roster
  history, and a unit's, newest first.
- On (`org_unit_id`, `person_id`) restricted to **open** rows — the current roster of a unit,
  which stays small while the history does not.
- A period index per unit, which is what the no-overlap rule and "was this row open on that
  date" both scan.

### 5.1 A participation row on the root unit

When a membership is created, a matching **`unit_participation` row for the root unit** is
created over the same period, and similarly closed when the membership ends.

This buys one thing: **"everyone in unit X" is one query, with one shape, at every level.**

The question is *who is in unit X on date D*, and `unit_participation` answers it on its own:
the rows of that unit whose `valid_from` is on or before D and whose `valid_to` is absent or
after D, read with the person, ordered by family name and then given name. It works whether X is
the organization (depth 0) or a Thursday group (depth 4). The date has to be applied to the
participation rows themselves; filtering the unit, or a membership above it, by that date and
leaving these rows unfiltered answers a different question.

Without it, "who is in the organization?" would be a query against `membership` and "who is
in a pack?" a query against `unit_participation` — two shapes for one question, and every
report would have to know which case it was in.

**The redundancy is deliberate and bounded.** The root row and the membership always have
the same period, so the root row is derivable — and it is derived by nothing. **No write may
change a membership's period, or open or close one, without making the matching change to that
person's root-unit participation row in the same transaction.** The two rows are one fact written
twice, so the obligation falls on every path that writes a membership, the legacy import above
all: it creates memberships by the thousand and must create their root rows beside them.
Integrity check 1b in [§7](#7-integrity-checks) is the net under that, not the guard — it finds
the drift afterwards, on a report somebody has to run. The alternative, a `UNION` in every
roster query, is worse.

**The root row is the only participation row that is *extended* rather than closed and
reopened** ([D-050](../decisions/decision-log.md#d-050--a-renewal-inside-the-window-extends-the-existing-root-participation-row)).
A transfer between sub-units is still close-and-open ([§5.2](#52-transfers-between-sub-units-are-cheap));
the root row is different because it mirrors a period that is itself backdated:

1. The yearly expiry sweep gives the **membership** a `valid_to` of the expiry date and moves
   its status to `lapsed`.
2. The root participation row is **not** closed with it — it is moved forward to the same date,
   so it is neither open-ended nor a second row (D-050). Only that person's still-open row on
   the root unit is touched; a participation row carries no membership reference, so person and
   unit are how it is found.
3. A renewal inside the window opens a **new** membership row starting at the expiry date
   ([D-016], D-040).
4. The root row is then stretched to the new period's end, which is exactly "extend the existing
   row": one row spanning both periods, no gap, no overlap.

Steps 2 and 4 are the same edit — moving the open end of the root row — performed at two
different moments.

> **The match in step 4 is the whole of D-050, and it is easy to get wrong.**
> The root row is matched to the *new* membership by **person and date**, not through
> `renewed_from_membership_id` — the participation row carries no membership FK, deliberately
> ([D-008](../open-questions.md#d-8--should-unit_participation-reference-the-membership), §5).
> So the condition is `new_m.valid_from = up.valid_to`: the renewal begins exactly where the
> root row was swept to. Anything looser would stretch a single row across a genuine
> post-window rejoin, where the gap is real and must stay.

> **This erases the visual evidence of the lapse, and that is the accepted trade (D-050).**
> A person who lapsed and renewed looks, in `unit_participation`, exactly like a person who
> never lapsed. The lapse is still fully visible in `membership`, which is the authority on
> payment. The participation table answers "who was in this unit when" — a roster question —
> and for that question a child who was in the pack across the period has exactly one answer.

**"Who was in the 4th Pack on 1 June 1998?"** is then exactly the query above.

### 5.2 Transfers between sub-units are cheap

Because participation is not membership (D-041), moving a person between groups is **one row
edit** — close one, open another. Nothing about their membership, their fee, or their status
as a member changes.

Moving person 100 from pack 12 to pack 31 effective 1998-09-01 is two writes, in this order:

1. Close the row that is open for person 100 in pack 12: `valid_to` becomes 1998-09-01,
   `leave_reason_code` becomes `transfer_out`, and `updated_at`/`updated_by` record who did it.
2. Open a row for pack 31 with `valid_from` 1998-09-01, `join_reason_code` `transfer`, a
   `source` of `staff`, and the actor recorded as `created_by`.

Rewriting the old row would destroy the answer to "where was this child in 2003?" — the
question the whole temporal design exists to answer. Close and open; never update
`org_unit_id` in place.

**Under the old model this was much more expensive**: a "unit membership" was a membership,
so moving a child between groups raised questions about which membership was which and
whether a fee was owed twice. Participation removes the question.

### Unit reorganizations

When a unit is split or merged, members are transferred by the same close-and-open
pattern, with `join_reason_code = 'reorganisation'` and the
`org_unit_relationship` row recording the lineage. A bulk operation should be a single
named procedure with a dry-run mode — it will be run on hundreds of rows during an import
and must be testable before it commits.

---

## 6. Membership and the authorization system

**The resolver evaluates membership state.** This is settled (D-039) and it is the single
largest coupling in the design, so it is worth stating in full rather than in a footnote.

```
A role grants access ONLY IF the holder has a current membership,
    unless  role.requires_membership = false    (appointed counselors, local leaders)
    or      the channel is guardianship         (a legal relationship, not a membership)
    or      the channel is ownership            (your own record — see below)
```

**The carve-outs, and why each exists:**

| Carve-out | Why |
|---|---|
| **Guardianship** | A parent's authority over their child comes from a legal relationship. An unpaid fee must not make a parent unable to act for their child. |
| **Appointed counselors and local leaders** | The organization needs them present regardless of their own fee status. Marked per-role with `requires_membership = false`. |
| **Ownership** | Otherwise a lapse locks a person out of the very screen they renew on. |

**The cost, named plainly:**

- **The permission cache must be invalidated on every membership transition** — including
  the yearly expiry sweep, which is a bulk event touching every member at once. The cache
  design has to be built for this from the start; retrofitting it is where the bugs will be.
- **A lapse silently removes access.** That is the intent, but "why can't I see this?" now
  has an answer that is a date rather than a decision.
- **`role.requires_membership` changed meaning** — from a flag that drove a report to a value
  the resolver enforces.

**The "leaver with access" report remains valuable**, but its purpose changes. It no longer
*prevents* access — the resolver already does that — so what it now detects is a role that
should have been **closed** and was not. That is still worth a worklist, because a stale
assignment silently springs back to life the moment the person renews:

Concretely: every `role_assignment` still open whose holder `is_current_member()` says is not a
member, shown with the role's own `requires_membership` and with the enforced ones first — those
are the assignments the resolver is holding back today, and the ones that will matter on renewal.

**Dormant authority is a real hazard.** A membership that lapses and is renewed a year later
would otherwise resurrect every role the person held in the interim, including ones a human
had quietly decided not to reinstate. Closing the assignment at the same time as the
membership is the honest fix; this report finds the ones that were missed.

**A role assignment should not outlive the membership that justified it.**

---

## 7. Integrity checks

**Invariants to verify**

* **1. Participation rows without a corresponding organization membership at that time.**
  Counts participation rows for which the same person has no membership that is not
  `pending_payment` and whose period overlaps the participation's — one beginning on or before
  the participation ends (or begins, if it is still open) and ending after the participation
  begins. Non-zero is the case no constraint here can express, deliberately: someone taking part
  who was never a member.
* **1b. The root participation row disagreeing with the membership it mirrors** (§5.1). Counts
  memberships whose root-unit participation row has either end of its period different from the
  membership's own. Nothing maintains the root row on its own behalf — §5.1 makes the pairing an
  obligation on whoever writes the membership — so a non-zero count names the path that wrote one
  row and forgot the other.
* **2. Participants in units that do not allow minors.** Counts open participation rows in a
  unit whose type says `allows_minors = false`, where the person has a recorded birth date that
  makes them under 18 today. A unit that does not supervise minors may not have any placed in
  it — safeguarding, not membership: membership itself is ageless (D-038).
* **3. Non-members holding a role that requires membership.** Counts open role assignments on a
  role with `requires_membership` true whose holder is not a current member. The resolver blocks
  these (D-039), so this is not an access breach — it is a stale assignment that will spring back
  to life when the person renews (§6).
* **4. Approved requests that never produced a membership.** Counts requests that are `approved`,
  carry no `membership_id`, and were decided more than seven days ago. Non-zero is an approval
  that went nowhere.
* **5. Memberships expiring soon.** Counts `active` memberships ending within the next 90 days —
  the renewal campaign worklist (§6 of domain/05), not a fault.
* **6. Renewal chains with a broken link.** Counts memberships whose `renewed_from_membership_id`
  names a row that does not exist. Non-zero means the chain is followed into nothing.
* **7. Renewals inside the window whose new period does not start at the previous expiry date.**
  Counts renewals whose `valid_from` differs from the previous membership's `valid_to` and begins
  less than 91 days after it. The renewal rule (D-040) backdates the new period, so a mismatch
  means either a genuine post-window rejoin or a bug.

**Check 3 is the one that matters most now.** Under D-039 the resolver already blocks a
non-member's roles, so this is no longer an access breach — but it detects *dormant*
authority, which is the failure mode the membership gate introduces: a role nobody closed
that silently reactivates on renewal.

**Check 5 is operational** (a worklist for the renewal campaign), and **check 1b** guards the
one deliberate redundancy in the model (§5.1). The rest are data-quality checks for cases no
constraint rejects at the write.

---

## 8. Seed data

The organization starts with a single membership type — `member`, named and described in plain
words, open for a person to register themselves for, and left to `requires_approval` at its
default of true. The term and the calendar parameters on that row are §1's, not constants
anywhere else.

**One row, and that is the whole vocabulary** (D-037). The fee is flat and per person, so
there is nothing to vary by type; being a counselor or leader is a position, not a type; and
membership is ageless, so there are no age limits to seed (D-038).

**The calendar is now settled** — 1 January, 60 days
([D-047](../decisions/decision-log.md#d-047--the-fee-expires-on-1-january),
[D-048](../decisions/decision-log.md#d-048--the-renewal-window-is-60-days-and-is-a-configuration-parameter)).
The term (12 months) remains a placeholder that nothing currently depends on. All four are
columns rather than constants, so tuning any of them is an `UPDATE`, not a release.

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

- The real membership term and renewal-window length (§1, §8) — the two remaining
  type-level parameters.
- Whether `outstanding_balance` should exist as a denormalised column or be computed
  (§3) — depends on the finance design in [07-finance.md](07-finance.md).
- Whether `unit_participation` should reference `membership_id` in addition to `person_id`,
  to get referential integrity without losing the import case. Possible as a nullable
  column, but it would be unenforced for imports.
- What the root-unit participation row does when a membership is renewed inside the
  window — it must extend across the (retrospectively filled) period without creating an
  overlapping row (§5.1).

**Resolved and no longer open**, kept visible so the reasoning survives: whether a person
may hold several open memberships (no — one type, person-scoped constraint, §3); whether
membership activates on payment (yes, §3); whether permissions depend on membership state
(yes, with carve-outs — D-039, §6); the age limits and age-out (§8); the grace period as a
status (§6); and the whole requirement mechanism (§4).

All tracked in [../open-questions.md](../open-questions.md).
