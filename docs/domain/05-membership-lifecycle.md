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

**Decided: membership activates on payment**
([D-040](../decisions/decision-log.md#d-040--the-fee-expires-yearly-a-date-tracked-renewal-window-replaces-a-grace-status)).
`membership` opens at stage 5, and `pending_payment` is a real membership status so that
"approved, awaiting payment" is a visible worklist rather than an invisible backlog.

---

## 2. Membership request

A request records the person it is **for**, the membership type asked for, and the unit the
applicant would like — optional, because the organization may assign the unit at approval
instead. `status` is one of `draft`, `submitted`, `under_review`, `approved`, `rejected`,
`withdrawn`, `expired`, and `submitted_at` says when it went in. The review is carried on the
same row: who took it up, when they decided, and on a rejection a
`rejection_reason_code` with a free-text `rejection_note` beside it. When an approval produces
a membership, `membership_id` is set to it.

An approved request points at the membership it produced; the link is not optional once the
approval exists.

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

### There are no request requirements

**Removed entirely** ([D-044](../decisions/decision-log.md#d-044--nothing-gates-a-membership-request-except-identity-and-payment)).
A request is accepted on **identity and payment alone**: no blocking checklist, no evidence
collection, no waiver workflow, no `requirement_code` and no
`membership_request_requirement` table.

Your answer, asked what a request must contain to be accepted: *"Just identity and the fee —
nothing to verify."* The option to keep the mechanism as empty infrastructure for later was
offered and not taken, which is the right call — a checklist that is always empty is a
checklist nobody maintains, and it would have implied a gate that does not exist.

**What this does not weaken.** Two things that *look* like requirements are unaffected,
because neither was a membership requirement to begin with:

- **Guardian consent for a minor's account** is a fact about the guardianship relation, held
  in `guardianship_permission`, not a box ticked during an application
  ([data-model/04](../data-model/04-relationships.md#2-the-guardians-right-none-view-or-write)).
- **Position eligibility** — a scoutmaster must be an adult — is a property of the position
  ([data-model/02 §7.1](../data-model/02-organization.md#7-position-and-position_assignment)),
  not of membership. Membership is ageless
  ([D-038](../decisions/decision-log.md#d-038--membership-is-ageless)).

**And background checks do not exist in this system at all**
([D-043](../decisions/decision-log.md#d-043--no-background-checks-are-recorded-in-this-system)).
If the organization introduces them, the home is a dated record with an expiry, and it
belongs at the position-eligibility layer rather than the membership gate — a lapsed check is
a reason someone may not hold a role, not a reason they stop being a member.

---

## 3. Membership

A membership row belongs to one person and one membership type, and carries a `status` of
`pending_payment`, `active`, `lapsed`, `terminated`, `completed` or `suspended` — always chosen
deliberately, never defaulted. The period is `valid_from` and `valid_to`, and an absent
`valid_to` means the period is still open: it is the current membership, not a row someone
forgot to close. `joined_via_request_id` records the request it came out of,
`termination_reason_code` the reason it was ended, `data_confidence` is `high`, `medium` or
`low` — legacy imports are `low` — and `import_batch_id` is set on imported rows and on nothing
else.

### Overlap rules — the invariant that matters

A person must not hold two **open** memberships at the same time, and the rule is enforced by
the database rather than by application code. Its precise statement is in
`data-model/03-membership.md` §3; what it says, in words:

- Two membership periods of one person may not cover the same date while either of them is
  `pending_payment`, `active` or `suspended`. Those three statuses are the whole of the rule's
  reach — a `lapsed` row, a `terminated` one and a `completed` one are outside it, which is why
  an ending period and a later beginning one sit beside each other without complaint.
- Periods are half-open, so a membership ending on 30 June and another opening on 30 June do
  not collide.

The constraint used to be scoped to `membership_type_id`, because a person might
legitimately be an `honorary` and an `adult` member at once. With **one membership type**
([D-037](../decisions/decision-log.md#d-037--exactly-one-membership-type-the-fee-is-flat-and-per-person))
that escape hatch is gone, and the constraint becomes the clean person-level invariant:
**one person, one open membership, ever.** The type column was what made "am I a paid-up
member?" a hard question; now it is one row, one status, one date
([D-041](../decisions/decision-log.md#d-041--belonging-to-a-sub-unit-is-a-participation-record-not-a-membership)).

*Assumption:* `btree_gist` is available (PostgreSQL), because a temporal overlap is the one
rule that can only be refused *during* the write that would create it. If the target database
cannot express exclusion constraints, the fallback is a check inside the writing transaction
plus the nightly consistency report — **one of the strongest guarantees in the model degrading
into the weakest class** ([data-model/00 §6a](../data-model/00-conventions.md#6a-who-enforces-an-invariant-now),
[open question F-10 shape 1](../open-questions.md#f-10--which-invariants-the-orm-cannot-express-and-who-writes-those)):
an application-level count is wrong exactly when two writers run at once, which is when an
overlap is actually created, and the report finds it a day later in a form nobody can attribute.
So it is not merely "weaker" and must be recorded as an accepted risk, chosen deliberately,
rather than discovered in a migration tool's limitations.

### There is one membership type, and membership is ageless

A type row is a `code` and a `name`, four calendar values, and a `sort_order`. The calendar
values start at twelve months' duration, `expiry_month` 1 and `expiry_day` 1 — the fee expires
on 1 January (D-047) — and `renewal_grace_days` 60, which is the renewal window and not a
status (D-048).

Seeded with **exactly one row**, `member`
([D-037](../decisions/decision-log.md#d-037--exactly-one-membership-type-the-fee-is-flat-and-per-person)).
Everything the old type carried — `category`, `min_age`, `max_age`,
`requires_background_check`, `requires_guardian_consent`, `fee_schedule_id` — is gone, and
what is left is the two parameters a *period* needs: how long it lasts, and how long after it
the person may renew without re-applying. The fee itself is not a property of the type at
all: it is a flat per-person amount that lives on `fee_schedule` and is snapshotted onto each
obligation, so "what did we charge in 1998?" is answered from the obligation, not the type.

**Membership is ageless** ([D-038](../decisions/decision-log.md#d-038--membership-is-ageless)).
No age floor, no age ceiling, no age-out, no child→adult transition. Age survives as a fact
about a **person** (`person.birth_date`) and matters where the law makes it matter:
guardianship, safeguarding, and position eligibility
([§7 was the age-transition section — there is no longer a §7](#7-there-are-no-age-transitions)).
Being a counselor or a leader is a **position**, never a membership type.

---

## 4. Multiple memberships over a lifetime

This is your 1990–2010 / 2024–present case. It is not an edge case; it is the normal
shape of a long-lived organization's data.

```
person 100 — Jan Novák
  ├── membership #1   member   1990-09-01 → 2010-06-30   terminated  (left)
  │     └── unit_participation   Pack 12  1990-09-01 → 1998-06-30
  │     └── unit_participation   Pack 31  1998-09-01 → 2010-06-30
  ├── (gap 2010 → 2024 — 14 years, no membership rows)
  └── membership #2   member   2024-10-01 → NULL          active
        └── unit_participation   Group 5  2024-10-01 → NULL
        └── position_assignment  scoutmaster, Group 5  2025-01-01 → NULL
```

Note what the two membership rows now *share*: the same type. They differ only in their
period and their end reason. In the original framing this person was a **child** member and
then an **adult** member; in this one they were a **member**, twice, and were a child and
then an adult the whole time. The second framing is the true one, and it is why the
memorable case still works: the person never changed, and neither did the type — only the
period did.

Everything the system needs follows from this:

- **"Is this person a member?"** → is there a membership with `valid_to IS NULL` (or
  covering today) and `status = 'active'`?
- **"How long have they been a member?"** → sum of membership period lengths, not
  today − first join date. The gap must not count.
- **"How old were they when they joined?"** → `membership #2.valid_from − person.birth_date`.
- **"Are they an adult?"** → `is_minor(person_id)`, computed from `person.birth_date`. In
  2005 the same query said yes. The membership row is identical either way; only the person's
  birth date and today's date moved.

> **Never** store `is_member`, `member_since`, `member_type`, or `is_child` on `person`.
> Every one of those is derivable, and every one of them will be wrong the moment history
> is corrected or a person returns.

---

## 5. Transitions and who can perform them

| From | To | Trigger | Permission required |
|------|-----|---------|---------------------|
| — | `draft` | person starts an application | own |
| `draft` | `submitted` | person submits | `membership.request.create` (own, or the guardianship channel at `write` for a guardian — D-074) |
| `submitted` | `under_review` | reviewer picks it up | `membership.request.review` |
| `under_review` | `approved` | reviewer approves | `membership.request.approve` |
| `under_review` | `rejected` | reviewer rejects | `membership.request.approve` |
| any | `withdrawn` | applicant withdraws | own, or guardian with permission |
| `approved` | membership `pending_payment` | approval processed | system |
| `pending_payment` | `active` | payment confirmed | system (or `fee.record` for manual) |
| `active` | `lapsed` | fee unpaid past the organization's expiry date | `membership.lapse` or the yearly sweep |
| `active` | `terminated` | disciplinary / cause | `membership.terminate` — **separate, more restricted permission** |
| `active` | `suspended` | temporary hold | `membership.suspend` |

There is no `completed` row any more. It existed only for ageing out, and ageing out no
longer exists ([D-038](../decisions/decision-log.md#d-038--membership-is-ageless)).

**Termination must not be the same permission as lapsing.** A lapse is administrative
(nobody paid). A termination is a decision about a person's standing in a youth
organization, often with safeguarding implications. Conflating them means every volunteer
who chases unpaid fees can also expel a member.

**A lapse has two faces, and only one of them is a human decision.** A lapse triggered by
non-payment is the yearly sweep doing its job — nobody decided anything, and "why did I lose
access?" has a date for an answer rather than a person. A lapse triggered by a staff decision
is a deliberate act with a permission behind it. Both land in the same status; `access_log`
is what distinguishes them, which is another reason the lapse is recorded as an event and not
just a column change.

---

## 6. Renewal and the yearly fee

The fee is **flat, per person, yearly**, and it **expires on a fixed date** — typically
January ([D-040](../decisions/decision-log.md#d-040--the-fee-expires-yearly-a-date-tracked-renewal-window-replaces-a-grace-status)).
The membership-relevant part, in full:

### Renewal opens a new period, not an extended one

**Shape A, decided** ([D-016](../decisions/decision-log.md#d-016--renewal-opens-a-new-membership-row-not-an-extended-valid_to)).
The previous row closes and a new one opens, linked by
`membership.renewed_from_membership_id`. Extending `valid_to` in place would be fewer rows
and would silently lose the most commonly asked question about renewals — did they renew
every year, or skip one and come back?

### The renewal window replaces the grace status

The old design had a grace *status*: during it the person was still a member. That is gone.
What replaces it is a **window tracked as dates, not as a status**
([D-040](../decisions/decision-log.md#d-040--the-fee-expires-yearly-a-date-tracked-renewal-window-replaces-a-grace-status)):

| When | What is true |
|---|---|
| On 1 January | The membership **lapses**. They are not a member, and member permissions stop. |
| Inside the window (60 days after expiry) | Still not a member — but they may **renew without re-applying**, and a payment now **opens the new period at the expiry date**, so the record shows no gap. |
| After 2 March | A payment opens a new membership at the **payment date**. The gap is real. Still no new application required. |

**The 1 January date has a consequence that reaches past the membership table.** The yearly
sweep is the only *bulk* event in a system carefully built to have none: on a single day,
every membership in the organization lapses at once. That makes it the day the permission
cache is invalidated for everyone, the day renewal traffic peaks, and — if
`system.gate_exempt` were not in place — the day the system administrator would lose access to
the system they administer ([D-051](../decisions/decision-log.md#d-051--the-membership-gate-is-waived-by-a-permission-not-only-by-a-role-flag)).


**All four calendar values are columns —
`duration_months`, `expiry_month`, `expiry_day`, `renewal_grace_days` — and that is a requirement rather than a convenience.**
The organizational year runs with the calendar, and 60 days was chosen for the window on the
explicit condition that it stays easy to change
([D-048](../decisions/decision-log.md#d-048--the-renewal-window-is-60-days-and-is-a-configuration-parameter)):
*"Make it 60 days, but it should not be hard to modify."* Because the window and the date live
in a row rather than in a scheduled job, moving them is an `UPDATE`. The failure this prevents
is a job that contains the literal `60` — invisible, and wrong the first time the organization
changes its mind.

**Why dates rather than a status.** Your own answers pointed two ways on this, and it is
worth being honest about that: you described the window as existing *"for them to pay to stay
members"* — which implies still being a member — and separately confirmed they are *"expired
now, but they can rejoin without re-applying."* D-040 resolves it as **not a member during
the window, but the record shows no gap once they pay**, because the alternative puts a third
state into every permission check and makes a lapse undetectable until the window closes. If
the softer reading is what the organization actually wants, it is a change to the renewal
rule, not a rewrite.

**The backdating is the load-bearing detail.** Without it, someone who pays in February for a
January expiry is recorded as having a one-month gap and is misclassified as a *returning*
member — which would pollute the returning-member query and, worse, `is_current_member()`
would have said "no" for a month when the person considers themselves continuously paid up.

So the rule to implement is one decision, not a formula on dates alone: **the renewal period
starts at the old expiry, not at the payment date**, whenever the payment lands inside the
window. Landing inside the window is what selects the expiry date, and it is what produces no
gap; landing after it selects the payment date, and the gap stands.

**Note the consequence for the permission cache.** The lapse happens to everyone at once, on
the same date, in a bulk sweep
([D-039](../decisions/decision-log.md#d-039--member-permissions-require-a-current-paid-membership)).
That is one cache-invalidation event touching every member rather than a steady trickle.
See [data-model/05 §10](../data-model/05-authorization.md#10-the-resolver).

---

## 7. There are no age transitions

This section used to describe two automatic transitions — ageing out of a child membership,
and becoming an adult member. **Both are gone**
([D-038](../decisions/decision-log.md#d-038--membership-is-ageless)). In their place, one
sentence: a person's membership does not change when they turn 18, because it was never
about their age.

What a system built around this must still handle — none of it a membership transition:

| Concern | Where it lives now |
|---|---|
| A guardian's authority at majority | Guardianship — and the system does **not** notice the birthday. No auto-expiry and no review queue; a person ends the row (D-069) |
| Whether a unit takes minors at all | `org_unit_type.allows_minors` — a safeguarding flag |
| Whether a person may hold a leadership position | `position.min_age`, and `is_minor()` in the eligibility report |
| Consent for a minor's own account | `guardianship_permission`, not a membership requirement |
| Planning around age groups | A query over `person.birth_date`. It is a report, not a state change. |

**The edge case this removes.** The old design had to reason about a person who was
simultaneously finishing a child membership and starting an adult one, and about whether the
overlap constraint would block it. That case cannot arise: there is one membership, it
runs continuously, and turning 18 is an event in the person's life that the membership does
not notice.

---

## 8. Since 1985 — the ten queries this design must answer

Stated explicitly so they can be tested. All are point-in-time queries and all must remain
answerable indefinitely:

1. Who is an active member today?
2. Who was a member on any given date in the past?
3. Who was in unit U on date D? (requires `unit_participation`, and for the organization
   itself the root participation row makes it the same query — see
   [D-041](../decisions/decision-log.md#d-041--belonging-to-a-sub-unit-is-a-participation-record-not-a-membership))
4. What is the full membership history of person P, including gaps?
5. Who is **inside the renewal window** right now? (a case needing follow-up — the worklist
   that replaced "who is in grace")
6. Who was approved but never paid? (a case needing follow-up)
7. Which members are **under 18 and have no guardian recorded**? (a safeguarding gap, not a
   membership one — the old background-check query was retired by
   [D-043](../decisions/decision-log.md#d-043--no-background-checks-are-recorded-in-this-system))
8. Which minors are in units that do not accept them? (a data-quality check against
   `org_unit_type.allows_minors`)
9. Who are the returning members — more than one membership with a gap between?
10. How many members did the organization have in each year since 1985? (historical
    reporting — must include closed memberships and must not double-count)

Query 10 is the one that fails in most systems, and it fails specifically because someone
made membership a boolean.

Query 1 is now *slightly* harder than it looks, and deliberately: it is not
`status = 'active'` alone, because a membership also stops being current at `valid_to`.
`is_current_member()` is the single place that decision lives, and every caller should use it
rather than re-deriving the predicate — otherwise the queries disagree with the permission
resolver, which is the worst kind of bug to find.

---

## 9. Open issues

- The organizational calendar: which date the fee expires on, and how long the renewal window
  is (§6). The mechanism is settled; the two numbers are a guess.
- What the root-unit participation row does when someone renews inside the window, given the
  backdated period (§6, and
  [data-model/03 §5.1](../data-model/03-membership.md#51-a-participation-row-on-the-root-unit)).
- Whether `unit_participation` should reference the membership, for referential integrity at
  the cost of the import case (§3).
- Which roles are exempt from the membership gate — a decision per role, not a default
  ([data-model/05 §3](../data-model/05-authorization.md#3-role-and-role_permission)).

**Resolved and no longer open**, kept visible so the reasoning survives: activation on
payment or approval (on payment, §1); per person or per household (per person and flat, §6 —
and the household grouping has since been removed entirely,
[D-057](../decisions/decision-log.md#d-057--household-is-removed));
renewal shape A or B (A, §6); age-out timing and the child→adult transition (neither exists,
§7); background checks as a requirement (§2); and simultaneous memberships of different types
(impossible — one type, one open membership, §3).

All tracked in [../open-questions.md](../open-questions.md).
