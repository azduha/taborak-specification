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
([D-040](../decisions/round-02-03.md#d-040--the-fee-expires-yearly-a-date-tracked-renewal-window-replaces-a-grace-status)).
`membership` opens at stage 5, and `pending_payment` is a real membership status so that
"approved, awaiting payment" is a visible worklist rather than an invisible backlog.

### Two doors, one gate each

The flow above is one of two ways a person ends up in the organization's records, and for eight
rounds this document wrote as if it were the only one. There are two entry paths and each has
exactly one gate, with no third control anywhere
([D-095](../decisions/round-09.md#d-095--units-carry-no-restrictions-joining-one-is-somebody-elses-act),
whose reasoning
[D-098](../decisions/round-10a.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority)
transfers to groups intact — joining one is still somebody else's act):

| | **Membership of the unit** | **A group** |
|---|---|---|
| **How you get in** | You pay. Stages 1–5 above are this door, and it is **the only self-service entry in the system** — it opens a `membership` and nothing beside it | Somebody else writes a `person_group_member` row |
| **What stops you** | The fee | `person_group.member.manage`, held at the unit — which reaches every group — or granted on one group as an item |
| **Money** | The yearly fee | Nothing |

**Nobody writes themselves into a group.** The people who run a group add people to it; that is the
whole of the rule, and it is carried by a permission rather than by a workflow.
**`person_group.member.manage` has no self-scoped variant and none will be added** — a grant is
always "over this group's roster", never "over my own", so the shape of request that would let a
person place themselves is not refused by a check, it is not expressible. The same holds for
offices: **nobody appoints themselves**, and the catalog holds no code that could say otherwise
([../appendix/permission-catalog.md §5](../appendix/permission-catalog.md)).

**No fee below the membership, and no model wants one.** The fee is the organization's; joining a
group carries no money — *"into the sub-units, there is no fee, it is entirely managed by the
organization, including adding more members."* That was said about units and it transfers unchanged,
a group being among the things listed as having **no** fee
([D-098](../decisions/round-10a.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority)).
Putting a fee on a member row would immediately ask who sets the amount, who chases it, and what
happens to a child whose family cannot pay a group's arrears, and none of those questions exist in
the corpus or in any answer given. That is a refused model, not an unasked one.

**What the asymmetry costs.** The group door has no membership check behind it — a counselor may add
somebody who is not a member, and nothing in the write stops them, because D-095 refuses a third
gate as firmly as it refuses the first two. What keeps that person from reading anything is
`MEMBERS` in the grants that matter — the test
[D-039](../decisions/round-02-03.md#d-039--member-permissions-require-a-current-paid-membership)
was, now carried in the grant text rather than the resolver
([D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape))
— which is what that test was always for. **A group membership is a fact about belonging, not a
credential**: a member of a group can do nothing by being one, and the tidier table does not quietly
promote it
([D-098](../decisions/round-10a.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority)).
The other cost is directional and appears in the other direction at import: **the membership door is
the only place a person's own initiative can produce a record**, which is why the legacy corpus
could be matched against people and never against groups ([domain/03
§7](03-identity-and-legacy.md#7-legacy-import-pipeline)).

**And one cost is new, named where
[D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)
names it.** Under the deleted hierarchy, access to a body's children had to be granted *by that
body*, by people who recruited its leader and can be asked. A group's roster write is the same shape
of permission and may be held at the unit, where it reaches every group in the organization, so what
is left of the safeguarding story is a permission held by a named adult, an audit trail whose
recorded values expire after two years
([D-088](../decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)),
and a report of who holds the write — **minus the part where the named adult was somebody the body
chose**. Nothing in the remaining model reproduces that property, and this document says so rather
than letting the reader infer it.


---

## 2. Membership request

A request records the person it is **for** and the membership type asked for, and nothing else.
`status` is one of `draft`, `submitted`, `under_review`, `approved`, `rejected`, `withdrawn`,
`expired`, and `submitted_at` says when it went in. The review is carried on the same row: who took
it up, when they decided, and on a rejection a `rejection_reason_code` with a free-text
`rejection_note` beside it. An approved request points at the membership it produced; the link is
not optional once the approval exists.

**A request asks for membership of the unit, and it names no group.** `requested_unit_id` is
**deleted**, along with the index over it
([D-098](../decisions/round-10a.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority)).
~~The unit named on a request is a preference, not a door: a request opens the root and produces a
root participation row, and the pack the applicant wrote down is a sentence addressed to whoever
reviews it.~~ **Withdrawn by D-098**, which also deleted the table the column pointed at
([D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)).
The want behind the field is genuine — a reviewer would like to know where the applicant hopes to
turn up — and it is served by the `notes` the row already carries, which is what the field always
was in effect: a sentence, carrying no authority. **Which group a new member lands in is a write on
the group, not a preference on the request**: one `person_group_member` row, written by somebody
holding `person_group.member.manage` (§1), in a separate act with its own permission and its own
audit entry. An approved request that produced no group row is a complete, ordinary outcome.


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

**Removed entirely** ([D-044](../decisions/round-02-03.md#d-044--nothing-gates-a-membership-request-except-identity-and-payment)).
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
- **Who may hold an office** — a scoutmaster must be an adult — was never a property of membership, and
  after
  [D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)
  it is not a stored property of the office either: `position.min_age` is deleted with positions and
  `role` carries no age column, so what remains is `is_minor()` in a report (§7). Membership is
  ageless ([D-038](../decisions/round-02-03.md#d-038--membership-is-ageless)).

**And background checks do not exist in this system at all**
([D-043](../decisions/round-02-03.md#d-043--no-background-checks-are-recorded-in-this-system)). If
the organization introduces them, the home is a dated record with an expiry, and it belongs with the
office rather than the membership gate — a lapsed check is a reason someone may not hold a role, not
a reason they stop being a member. Which layer would hold it is unresolved, since the layer that
used to hold eligibility went out with positions
([D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape);
§7 and §9).

---

## 3. Membership

A membership row belongs to one person and one membership type, and carries a `status` of
`pending_payment`, `active`, `lapsed`, `terminated`, `completed` or `suspended` — always chosen
deliberately, never defaulted. The period is `valid_from` and `valid_to`, and an absent `valid_to`
means the period is still open: it is the current membership, not a row someone forgot to close.
`joined_via_request_id` records the request it came out of, `termination_reason_code` the reason it
was ended, `data_confidence` is `high`, `medium` or `low`, and `import_batch_id` is set on imported
rows and on nothing else. **For one round these two **For one round these two columns were dead on
this table** — the corpus carried no payment evidence, so the batch wrote `person` rows and left
membership to the live register, and this paragraph said a `membership` row is never imported
[D-093](../decisions/round-09.md#d-093--the-one-off-import-may-create-memberships-both-ends-dated)
reversed that, because it turned out the source states a membership period directly rather than only
attendance: the import now writes `membership` rows for the periods the export states,
`data_confidence = 'low'` and `import_batch_id` set on every one of them, both ends of the period
dated ([domain/03 §7](03-identity-and-legacy.md#7-legacy-import-pipeline)). **What did not come back
is the open-ended row**: an imported membership never runs to today and none is inferred from an
attendance row, which is the half of the old rule that was doing the protecting. So
`data_confidence` on this table has two live sources again and they mean different things: on a
backdated row it is a human's judgement (`membership.backdate`, attributed to whoever typed it), on
an imported row it is the batch speaking for itself.

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

The constraint used to be scoped to `membership_type_id`, because a person might legitimately be an
`honorary` and an `adult` member at once. With **one membership type**
([D-037](../decisions/round-02-03.md#d-037--exactly-one-membership-type-the-fee-is-flat-and-per-person))
that escape hatch is gone, and the constraint becomes the clean person-level invariant: **one
person, one open membership, ever.** The type column was what made "am I a paid-up member?" a hard
question; now it is one row, one status, one date. (This sentence cited
[D-041](../decisions/round-02-03.md#d-041--belonging-to-a-sub-unit-is-a-participation-record-not-a-membership)
until round 10; that decision was about belonging to a sub-unit, its table is deleted
([D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)),
and nothing about this invariant ever depended on it.)

**This is the invariant the import now writes against.** For one round the sentence could be written
the other way — with no imported membership, there is nothing for it to violate — and D-093 removed the
premise, not the rule
([domain/03 §7](03-identity-and-legacy.md#7-legacy-import-pipeline)). Say exactly what fires, because the
rule's reach is narrow: it watches the three live statuses, so what the exclusion constraint refuses at
apply time is an imported period colliding with a **live** membership — an export period that runs into
or past the person's current one, which an open-ended imported row would produce for thousands of people
in one transaction. What it does *not* refuse is an overlap between two closed imported periods: the
statuses are outside its reach by design, so a source file that double-books somebody across 1993 lands
quietly, marked only as `data_confidence = 'low'`. That is the honest cost of the same decision that
keeps a returning member's old period from gating anything today, and it is why the batch is reviewed
before it applies rather than after.

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
([D-037](../decisions/round-02-03.md#d-037--exactly-one-membership-type-the-fee-is-flat-and-per-person)).
Everything the old type carried — `category`, `min_age`, `max_age`,
`requires_background_check`, `requires_guardian_consent`, `fee_schedule_id` — is gone, and
what is left is the two parameters a *period* needs: how long it lasts, and how long after it
the person may renew without re-applying. The fee itself is not a property of the type at
all: it is a flat per-person amount that lives on `fee_schedule` and is snapshotted onto each
obligation, so "what did we charge in 1998?" is answered from the obligation, not the type.

**Membership is ageless** ([D-038](../decisions/round-02-03.md#d-038--membership-is-ageless)).
No age floor, no age ceiling, no age-out, no child→adult transition. Age survives as a fact
about a **person** (`person.birth_date`) and matters where the law makes it matter:
guardianship and safeguarding
([§7 was the age-transition section — there is no longer a §7](#7-there-are-no-age-transitions)).
Being a counselor or a leader is a **role**, never a membership type ([D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)).

---

## 4. Multiple memberships over a lifetime

This is your 1990–2010 / 2024–present case. It is not an edge case; it is the normal
shape of a long-lived organization's data.

```
person 100 — Jan Novák
  ├── membership #1   member   1990-09-01 → 2010-06-30   terminated  (left)
  │     └── (nothing here: the corpus names no groups, so nobody's data says where he was)
  ├── (gap 2010 → 2024 — 14 years, no membership rows)
  └── membership #2   member   2024-10-01 → NULL          active
        └── person_group_member  Thursday group  2024-10-01 → NULL
        └── role_holder          counselors      2025-01-01 → NULL
```

Note what the two membership rows now *share*: the same type. They differ only in their
period and their end reason. In the original framing this person was a **child** member and
then an **adult** member; in this one they were a **member**, twice, and were a child and
then an adult the whole time. The second framing is the true one, and it is why the
memorable case still works: the person never changed, and neither did the type — only the
period did.

**Half of this picture is reachable without a human, and the other half is not.** Membership #1 and
its dates are exactly what the membership export states, so the one-off import writes them —
bounded, `data_confidence = 'low'`, batch id set
([D-093](../decisions/round-09.md#d-093--the-one-off-import-may-create-memberships-both-ends-dated)).
The group row is the other half: **the corpus names no groups either**, so a 1990s roster exists
only because somebody who remembers typed it, and the import owes **no belonging rows of any kind**
([D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row),
[D-098](../decisions/round-10a.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority)).
What the diagram used to draw beside each membership — a **root-unit** participation row mirroring
the very same period — is gone with the table, and the picture is now about the two periods, which
is the most the import can actually say. The 1990s belonging the deleted rows might once have held
was never in the corpus either
([D-092](../decisions/round-09.md#d-092--the-corpus-is-people-and-events-and-it-names-no-units)),
so what is lost is a place it could have been written down, not a fact that was stored and then
thrown away.

**One row of the new diagram is thinner than the row it replaced, and the difference is a fact about
roles.** `position_assignment` could name the body a person led; `role_holder` cannot, because
[D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)
left exactly one scope and there is no body to hold an office *of* — a role is always held at the
unit. So "he was scoutmaster **of that group**" is no longer a stored pair: the office and the group
are two rows about the same person, and the link between them is somebody's reading of them.
[D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)
records the neighbouring loss in the same register — the elected-versus-appointed distinction
survives only as a role the organization invents — and neither is a hole this module can fill.

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
longer exists ([D-038](../decisions/round-02-03.md#d-038--membership-is-ageless)).

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
January ([D-040](../decisions/round-02-03.md#d-040--the-fee-expires-yearly-a-date-tracked-renewal-window-replaces-a-grace-status)).
The membership-relevant part, in full:

### Renewal opens a new period, not an extended one

**Shape A, decided** ([D-016](../decisions/round-01b.md#d-016--renewal-opens-a-new-membership-row-not-an-extended-valid_to)).
The previous row closes and a new one opens, linked by
`membership.renewed_from_membership_id`. Extending `valid_to` in place would be fewer rows
and would silently lose the most commonly asked question about renewals — did they renew
every year, or skip one and come back?

### The renewal window replaces the grace status

The old design had a grace *status*: during it the person was still a member. That is gone.
What replaces it is a **window tracked as dates, not as a status**
([D-040](../decisions/round-02-03.md#d-040--the-fee-expires-yearly-a-date-tracked-renewal-window-replaces-a-grace-status)):

| When | What is true |
|---|---|
| On 1 January | The membership **lapses**. They are not a member, and member permissions stop. |
| Inside the window (60 days after expiry) | Still not a member — but they may **renew without re-applying**, and a payment now **opens the new period at the expiry date**, so the record shows no gap. |
| After 2 March | A payment opens a new membership at the **payment date**. The gap is real. Still no new application required. |

**The 1 January date has a consequence that reaches past the membership table.** The yearly sweep is
the only *bulk* event in a system carefully built to have none: on a single day, every membership in
the organization lapses at once. That makes it the day every `MEMBERS`-gated answer in the organization moves
at once, and the day renewal traffic peaks. **It is no longer also the day the permission cache is invalidated
for everyone:** [D-114](../decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation)
deleted the stored answer, so the period ending and the `lapsed` status are the whole of the change, and each
member's next check sees it. And it used to be, on the same day, the day the system
administrator lost access to the system they administer, which is the hazard
[D-051](../decisions/round-04.md#d-051--the-membership-gate-is-waived-by-a-permission-not-only-by-a-role-flag)
existed to close.

**That mechanism is deleted**
([D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)):
there is no `system.gate_exempt`, no `person_holds_gate_exempt`, and no resolver clause left to hold
a door open. The answer now sits in grant text. A grant written `MEMBERS * ROLE(it)` stops applying
to its holder at the sweep; a grant written `ROLE(it)` does not, because `MEMBERS` is simply not in
it — which is exactly how D-100 says a whole office is made exempt, and the same sentence that makes
the administrator survivable is the one that makes a lapsed treasurer dangerous. *Assumption:*
**which offices are written without `MEMBERS`, and who decides, is not settled by D-100** — the
standing report of live grants naming a `ROLE(...)` operand without `MEMBERS` is what makes each
choice visible to a human ([data-model/03
§6](../data-model/03-membership.md#6-membership-and-the-authorization-system)), and §9 lists the
undecided half as a question.


**All four calendar values are columns — `duration_months`, `expiry_month`, `expiry_day`,
`renewal_grace_days` — and that is a requirement rather than a convenience.** The organizational
year runs with the calendar, and 60 days was chosen for the window on the explicit condition that it
stays easy to change
([D-048](../decisions/round-04.md#d-048--the-renewal-window-is-60-days-and-is-a-configuration-parameter)):
*"Make it 60 days, but it should not be hard to modify."* Because the window and the date live in a
row rather than in a scheduled job, moving them is an `UPDATE`. The failure this prevents is a job
that contains the literal `60` — invisible, and wrong the first time the organization changes its
mind.

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

**Note what the bulk lapse used to cost, and what it costs now.** The lapse happens to everyone at once, on
the same date, in a bulk sweep
([D-039](../decisions/round-02-03.md#d-039--member-permissions-require-a-current-paid-membership)).
~~That is one cache-invalidation event touching every member rather than a steady trickle.~~ **There is no
cache-invalidation event at all**: [D-114](../decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation)
deleted the answers that event used to clear, and a bulk write that shrinks an audience shrinks it live — every
grant written `MEMBERS * …` stops reaching a lapsed member on their next check, with the sweep as the only job
in the sequence rather than the sweep and a rebuild. **What the bulk shape still costs is computation, and it
is now paid on open:** a nightly rebuild used to pre-pay the expensive screens, so the tab on the permissions
page, the per-item preview and the *who holds this* listing each evaluate a changed answer for every one of
those people when somebody opens them — affordable at the size
[D-112](../decisions/round-13.md#d-112--the-systems-scale-is-stated-hundreds-of-people-tens-of-registrants-per-event)
states, and precisely what that entry's trigger reopens, with D-114 naming the reopen answer: materialize
`effective_permission` per person **and call it that**.
See [data-model/05 §10](../data-model/05c-access-log-and-resolver.md#10-the-resolver).

---

## 7. There are no age transitions

This section used to describe two automatic transitions — ageing out of a child membership,
and becoming an adult member. **Both are gone**
([D-038](../decisions/round-02-03.md#d-038--membership-is-ageless)). In their place, one
sentence: a person's membership does not change when they turn 18, because it was never
about their age.

What a system built around this must still handle — none of it a membership transition:

| Concern | Where it lives now |
|---|---|
| A guardian's authority at majority | Guardianship — and the system does **not** notice the birthday. No auto-expiry and no review queue; a person ends the row (D-069) |
| Who may be added to a group | Nowhere in the data. `org_unit_type.allows_minors` was removed by [D-095](../decisions/round-09.md#d-095--units-carry-no-restrictions-joining-one-is-somebody-elses-act) and the units it was a column on by [D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row); **no column says which group takes children, and none will**. The control is `person_group.member.manage`, held at the unit or on one group, in the hands of the people who run it ([D-098](../decisions/round-10a.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority) transfers [D-095](../decisions/round-09.md#d-095--units-carry-no-restrictions-joining-one-is-somebody-elses-act) intact), and [domain/04-organization-structure.md](04-organization-structure.md) owns it |
| Whether a person may hold an office | Nowhere either. `position.min_age` is deleted with positions ([D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)) and `role` carries no age column, so what remains is `is_minor()` in a report over `role_holder`. **That is a deletion rather than a move**: the eligibility check this row pointed at no longer exists, and §9 carries the question |
| Consent for a minor's own account | `guardianship_permission`, not a membership requirement |
| Planning around age groups | A query over `person.birth_date`. It is a report, not a state change. |

**One row of that table is emptier than it looks, and a membership document should say so out
loud.** This section could once answer *"which units take minors?"* from a flag on a type. That flag
is gone, the units went with it a round later, and no column on `person_group` replaces it, so what
this module has to offer on safeguarding is a permission held by named adults, an audit trail whose
recorded values expire after two years
([D-088](../decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)),
and a report of who holds the write. The argument that this is a stronger control than a boolean,
and the plain statement of what it cannot answer, belong to the groups module
([domain/04-organization-structure.md](04-organization-structure.md)); what belongs here is the
observation that **the fee gate never protected a child either** — it protects the organization's
membership roll, and it was never load bearing for placement. **What
[D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)
additionally takes is the part where the adult holding that write was somebody the body itself
chose**; it is recorded as a loss there and not argued away here.

**The edge case this removes.** The old design had to reason about a person who was
simultaneously finishing a child membership and starting an adult one, and about whether the
overlap constraint would block it. That case cannot arise: there is one membership, it
runs continuously, and turning 18 is an event in the person's life that the membership does
not notice.

---

## 8. Since 1985 — the ten queries this design must answer

Stated explicitly so they can be tested. All are point-in-time queries and all must remain
answerable indefinitely — with two exceptions this document now carries openly rather than editing
away: **query 3 has no answer for any group before go-live**, because the corpus names no groups,
and **query 8 has no answer at all any more**, because the thing it checked against no longer
exists. A list of ten that quietly became eight is how a specification loses a requirement:

1. Who is an active member today?
2. Who was a member on any given date in the past?
3. Who was in group G on date D? — **a point-in-time read over `person_group_member`**, whose rows are
   dated at both ends for exactly this question
   ([D-098](../decisions/round-10a.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority));
   the group's own lifetime is a second, different fact and both are kept. "Who was in the
   organization on date D?" is now a `membership` read with no belonging row involved: **two
   queries, two shapes**, and no "and everything nested under it" left to ask about
   ([D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)).
   **For a group this stops at go-live, and the stop is the corpus's, not the query's**: the import
   names no groups either, so "who was in the Thursday group in 2011?" has no answer at all rather
   than a wrong one, and every group row from before launch is somebody's typed recollection
   ([domain/03 §7](03-identity-and-legacy.md#7-legacy-import-pipeline),
   [D-092](../decisions/round-09.md#d-092--the-corpus-is-people-and-events-and-it-names-no-units))
4. What is the full membership history of person P, including gaps?
5. Who is **inside the renewal window** right now? (a case needing follow-up — the worklist
   that replaced "who is in grace")
6. Who was approved but never paid? (a case needing follow-up)
7. Which members are **under 18 and have no guardian recorded**? (a safeguarding gap, not a
   membership one — the old background-check query was retired by
   [D-043](../decisions/round-02-03.md#d-043--no-background-checks-are-recorded-in-this-system))
8. **Which minors are in groups that do not accept them?** — no longer answerable, and left numbered
   rather
   than renumbered away, so that the gap sits on the list instead of off it. It was a data-quality
   check against `org_unit_type.allows_minors`;
   [D-095](../decisions/round-09.md#d-095--units-carry-no-restrictions-joining-one-is-somebody-elses-act)
   removed that column and
   [D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)
   removed the units it was a column on, and a group is explicitly listed as carrying no such rule
   ([D-098](../decisions/round-10a.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority)).
   So there is nothing to check a placement against, in either vocabulary, and no plan for there to
   be one. What stands in its place is upstream — nobody is added to a group by somebody who does
   not hold that group's roster write — plus a report of who holds that write, which is a question
   about grants, not about people (§7)
9. Who are the returning members — more than one membership with a gap between?
10. How many members did the organization have in each year since 1985? (historical
    reporting — must include closed memberships and must not double-count)

**Round 8 said four of these reach only as far back as `membership` rows reach, because the legacy
import created none, and that for the decades arriving from paper queries 2, 4, 9 and 10 return
*participation*. Half of that is now false**
([D-090](../decisions/round-07-08.md#d-090--the-legacy-corpus-is-thousands-of-roster-rows-with-numbers-and-no-money),
[D-093](../decisions/round-09.md#d-093--the-one-off-import-may-create-memberships-both-ends-dated)).
The source states membership periods, so the import writes bounded memberships and those four
queries do reach into the corpus — **over an export, though, not over a register**, and the only
thing telling the two kinds of row apart is `data_confidence = 'low'` and a batch id, which no
report is obliged to notice ([domain/03 §7](03-identity-and-legacy.md#7-legacy-import-pipeline)). So
query 10 is answerable in a form that should be labelled on the way out of the chart: a member count
where the source states a period, and nothing where it does not.

**The wrong answer is still exactly one decision away, and the ban that stops it is one sentence.**
Generate a `membership` per attendance row and every historical query instantly returns a confident
number built on nothing, while `is_current_member()` quietly hands today's authority to people last seen
in 2003 ([D-039](../decisions/round-02-03.md#d-039--member-permissions-require-a-current-paid-membership)).
What stops that is not the column set but the rule: **never an open-ended imported membership, never one
inferred from attendance.** What round 8 got right and kept is the reasoning underneath — evidence and
inference are different rows, and a file that says *member 1990–1995* is the first kind while a line-up
of names at an event is the second.

**The question that did not come back is query 3 for anything before go-live.** Importing membership
rows says nothing about which group a person was in, because a membership is not a placement; the
group answer stays empty until somebody types a roster in by hand — which is the only way a group
row can be written at all, the corpus naming no groups
([D-092](../decisions/round-09.md#d-092--the-corpus-is-people-and-events-and-it-names-no-units),
[D-098](../decisions/round-10a.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority))
— and the honest reading of a pre-go-live roster is that it is somebody's recollection. **What is
*not* lost is the shape of the answer after go-live**: the member rows are dated precisely so that
"who was in the Thursday group in 2011?" stays a point-in-time read that survives the audit trail's
payload expiry
([D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)'s
second loss, which is the *unit* framing — the subtree question — rather than the roster).

These stay on the list because they are answerable, indefinitely, for everything this system registers
itself — and that indefinite half is itself a decision now, the accounting skeleton being kept as the
organization's history
([D-088](../decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)).
For the corpus, print which of the two answers a number came from.

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
- **Which offices are written without `MEMBERS`, and who decides that an office survives its
  holder's lapse.**
  The gate left the resolver for the grant text (§6,
  [D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)),
  so the decision is made one grant at a time and nothing records the *why* — only whether the word
  is in the expression. The standing report makes the outcome visible; it does not make the choice.
  Carried also at [data-model/03 §9](../data-model/03-membership.md#9-open-issues).
- **Whether an age rule has any home now.** `position.min_age` is deleted with positions
  ([D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)),
  a `role`
  carries none, and a `person_group` is refused one
  ([D-098](../decisions/round-10a.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority)),
  so "a scoutmaster must be an adult" survives only as a report over `role_holder` and `is_minor()`
  (§7). If the organization wants that rule enforced rather than reported, it needs a decision this
  round did not make.
- What `status` an imported closed membership carries (§3). The enum offers `pending_payment`, `active`,
  `suspended`, `lapsed`, `terminated`, `completed`, and none of them says *a source stated this
  period and nobody in the system decided anything*: `terminated` claims an end reason the export
  does not give, `completed` claims a lifecycle the model no longer has (§5 says no `completed` row
  is produced any more, while the enum and [data-model/03
  §3](../data-model/03-membership.md#3-membership) both still carry the value and use it in an
  example). This is a naming question with a reporting consequence — a `status` that reads as a
  decision will be reported as one.
- ~~Which roles are exempt from the membership gate~~ — the question became "which grants name
  `ROLE(...)`
  without `MEMBERS`", which is per grant rather than per role and is a report rather than a setting
  ([D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape),
  and the bullet above). **It stays on this list because the decision is still owed**, only the
  shape of it has changed.

**Resolved and no longer open**, kept visible so the reasoning survives: activation on
payment or approval (on payment, §1); per person or per household (per person and flat, §6 —
and the household grouping has since been removed entirely,
[D-057](../decisions/round-04.md#d-057--household-is-removed));
renewal shape A or B (A, §6); age-out timing and the child→adult transition (neither exists,
§7); background checks as a requirement (§2); and simultaneous memberships of different types
(impossible — one type, one open membership, §3). Two from round 9:

- **Whether a body may refuse a minor, and who may add a person to one** — answered twice over, and
  the same
  way both times. No unit carried restrictions of any kind and entry was somebody else's act: the
  fee at the membership, `unit_participation.manage` everywhere below it, no self-scoped variant of
  either
  ([D-095](../decisions/round-09.md#d-095--units-carry-no-restrictions-joining-one-is-somebody-elses-act),
  [C-6](../open-questions.md#c-6--closed--units-carry-no-restrictions-joining-one-is-somebody-elses-act),
  §1). Round 10 deleted the units and
  [D-098](../decisions/round-10a.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority)
  carried the ruling across intact: a group carries no restrictions, nobody writes themselves onto a
  roster, and the gate is `person_group.member.manage`. What that gives up is stated in §7 rather
  than here twice.
- **Whether the one-off import may create memberships** — it may, for the periods the source states,
  both
  ends dated, never open-ended and never inferred from attendance (§3). This was answered *no* one
  round earlier and the answer reversed with the description of the corpus, not with the reasoning
  about what a membership means
  ([D-092](../decisions/round-09.md#d-092--the-corpus-is-people-and-events-and-it-names-no-units),
  [D-093](../decisions/round-09.md#d-093--the-one-off-import-may-create-memberships-both-ends-dated)).

All tracked in [../open-questions.md](../open-questions.md).
