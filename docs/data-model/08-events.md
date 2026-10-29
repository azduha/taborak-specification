# Data Model — Events

`event`, `event_organizer`, `event_registration`, `event_question`, `event_answer`.

Domain rationale: [../domain/07-events.md](../domain/07-events.md).

**Nothing here is provisional.** This module was designed against the authorization model
rather than beside it, and every hook it uses — `access_grant` scoped to an item,
`grant_scope_type`, audiences and their selectors — was already in place and seeded. The
tables below fill those hooks; they do not extend the model.

Round 10 removed one thing this module was built around: **an event has no owning unit**
([D-102](../decisions/round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)).
`event.org_unit_id` is gone, `can_event()` is gone, and the unit-authority rule that every
event permission used to be reached through is gone. What the module uses instead is a set
of **selectors that bind to the event being checked**, specified in §8.


**Section numbers are shared across the two parts** and never renumbered, because other pages cite them by number and their anchors are built from them: [08-events.md](08-events.md) holds §1–§7, [08a](08a-event-guards-and-checks.md) §8–§11 (projections and guards, the three queries that matter, integrity checks, open issues).
---

## 1. Why these five tables, and no `event_series`

| Table | What it is |
|---|---|
| `event` | The occasion. A date, a registration window, an optional capacity — and no owner (§2) |
| `event_organizer` | Who is running it — an appointment on the event, not a grant (§5) |
| `event_registration` | One person's answer: attending, or not attending. *Unanswered is the absence of a row* |
| `event_question` | What this event asks registrants |
| `event_answer` | What one person said to one question |

**No recurrence.** A weekly meeting is a **group** — a `person_group` with dated member rows
([D-098](../decisions/round-10a.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority)) —
not an event
([../domain/07-events.md §1](../domain/07-events.md#1-what-an-event-is-and-what-it-is-not)).
Adding `event_series` would mean every downstream table — registrations, capacity, presence,
organizers, questions — needs a second possible home, and the feature that needed recurrence
is already modelled.

**No `event_status` column.** Visibility is the permission model; cancellation is a fact
([../domain/07-events.md §10](../domain/07a-capacity-presence-and-forms.md#10-cancellation-and-why-there-is-no-status-column)).

---

## 2. `event`

**Fields**

| Field | Kind | Notes |
|---|---|---|
| `id` | surrogate id | Internal only |
| `public_id` | external identifier, required | Unique. Generated when the event is created |
| `title` | text, required | |
| `description` | text, optional | The committee's own notes — internal |
| `public_note` | text, optional | Shown to registrants. Separate from `description`, which is internal: "bring a sleeping bag and a torch" vs. the committee's own notes |
| `location` | text, optional | Free text: a camp site, an address, "the usual place" |
| `location_detail` | free-form jsonb, optional | `{lat, lon, meeting_point, …}` when known |
| `starts_at` | instant in time, required | An instant, not a date. A Thursday group meets at 5pm; a camp starts on Saturday morning. The instant carries a timezone, and the timezone is the organization's, recorded rather than assumed |
| `ends_at` | instant in time, required | An instant, not a date, for the same reason |
| `all_day` | boolean, required | Default false. Display only — an all-day camp still has instants underneath |
| `registration_opens_at` | instant in time, optional | `NULL` = open as soon as the event is visible. The event is visible to whoever holds `event.view`, which after D-102 normally includes everyone holding it at the unit — see [../domain/07-events.md §10](../domain/07a-capacity-presence-and-forms.md#10-cancellation-and-why-there-is-no-status-column) for what that does to the private-by-default draft. So `NULL` is a reasonable default and wrong for a jamboree whose sign-up should not open before the dates are fixed |
| `registration_closes_at` | instant in time, optional | `NULL` = when the event starts. This is the "unlimited" case: registration stays open until the thing happens |
| `capacity` | integer, optional | `NULL` = unlimited. Bed count, bus seats, fire-safety limit. Enforced as a WAITLIST threshold, not a block, and a staff registration may exceed it ([../domain/07-events.md §8](../domain/07a-capacity-presence-and-forms.md#8-capacity-and-the-waitlist)) |
| `waitlist_deadline` | instant in time, optional | When an unpaid registration at a full event releases its place to the waitlist (§6). `NULL` = never releases. Only meaningful when the event has a fee AND a capacity; ignored otherwise. This is the ONE automatic transition in this module — see §6 for why it is accepted and what it costs |
| `fee_schedule_id` | reference to fee schedule, optional | `NULL` = this event is free, which most are. Set = a fee applies; registering creates a `fee_obligation` (§6). The amount and currency live in `fee_schedule`, not here — events do not price themselves |
| `cancelled_at` | instant in time, optional | Cancellation is a FACT, not a status, and this is the point where the "no status column" reasoning deliberately diverges: revoking grants would hide the cancellation from the registrants, who are exactly the people who must be told. A cancelled event stops accepting registrations and KEEPS every registration row — those rows are the record that the camp was planned and who was coming |
| `cancelled_by` | reference to person, optional | Who cancelled. Set exactly when `cancelled_at` is set |
| `cancel_reason` | text, optional | Free text, and it may be absent ("cancelled — see email") |
| `created_at` | timestamp, audit time | |
| `created_by` | reference to person, optional | Who created the row. **Not an owner** — `created_by` is attribution, and [D-005](../decisions/round-01a.md#d-005--permissions-are-grants-never-derived-from-identity) still holds that a permission is never derived from an identity |
| `updated_at` | timestamp, audit time, optional | |
| `updated_by` | reference to person, optional | |
| `import_batch_id` | reference to import batch, optional | Set on imported rows |

**Rules**

- `ends_at` is later than `starts_at`.
- `capacity` is either absent or greater than zero.
- When both `registration_opens_at` and `registration_closes_at` are set, the close is later
  than the open. When either one is absent nothing is required of the other — each is
  independently meaningful on its own.
- `cancelled_at` and `cancelled_by` are set together or not at all. A cancellation has a who
  and a when, or neither. The reason is free text and may be absent ("cancelled — see email").
- `waitlist_deadline` may be set only when both `capacity` and `fee_schedule_id` are set. A
  waitlist deadline is meaningless without a capacity to fill or a fee to pay, and stating
  this prevents a column that silently does nothing.
- `public_id` is unique.
- **No column of `event` names a scope.** There is no owner, no holding group, no creating
  unit, and no rule anywhere in this module that reads one (§8).

**Indexes**

- Upcoming events by `starts_at`, and events by `registration_closes_at` — both restricted to
  rows that are not cancelled. Every "what is happening" and "what is still open" list
  excludes cancelled events, so the cancelled ones are simply not in the index.

### There is no owner column

~~`org_unit_id` — reference to org unit, required. EXACTLY ONE owning unit, and it is never
absent.~~ **Deleted by
[D-102](../decisions/round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it).**
The column's note used to carry the argument that forced it: a joint camp is one unit's
event that another unit's children register for via an audience grant, and two owners would
have created an exception to "the root may not read a sub-unit's events" shaped exactly like
a joint camp, with no principled place to stop. That argument was sound while
[D-049](../decisions/round-04.md#d-049--the-root-may-not-read-into-its-sub-units-scope_exposure-is-the-only-crossing)
was alive. [D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)
deleted the sub-units, D-049 with them, and there is nothing left for the column to protect.

**An event is an item in `grant_scope_type` under the code `event`, and nothing more.** A
grant at the unit reaches every event; a grant on one event reaches that event and nothing
else; `event.create` has `applies_to = unit`, so writing it on an event is refused when the
grant is saved, with the reason in the message
([D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)).

**The deletion leaves no residue in this file, which is worth recording as a fact rather than
a hope.** There is no index on an owner (the lists above are the whole set), no check in §10
that reads one, no cascade, and no rule in §5 or §8 that compares one. The people connected
to an event are reached through `event_organizer` and `event_registration`, which point at
the event directly and never needed the owner.

**Import consequence.** The one-off import owes `event` rows and `event_registration` rows
and it owes **no owner column** — one less thing to invent a value for
([D-090](../decisions/round-07-08.md#d-090--the-legacy-corpus-is-thousands-of-roster-rows-with-numbers-and-no-money),
[D-102](../decisions/round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)).
It does owe the per-event seeded grant in §8, which is the residue the deletion *does* leave.

### No `status` column, and why that is not an omission

Nothing is stored that can be derived. "Is this event over?" is `ends_at` in the past. "Is it
cancelled?" is `cancelled_at` set. "Needs attention now" — the list an admin screen runs — is
every event with `cancelled_at` absent and `ends_at` not yet past, ordered by `starts_at`.

`completed` is derived, never stored, so there is no state to keep consistent and no job to
move rows between states. **Draft** is not a state either: publishing is an `access_grant`,
not an `UPDATE`. A status column and a permission system that both claim to answer "who may
see this?" will eventually disagree, and the one that gets enforced is whoever wrote the last
`IF`.

One clause of the old argument went with the owner column. ~~A new event has no grants beyond
its organizers, so nobody else can see it~~ — with no owner, a fresh event is visible to
everybody already holding `event.view` at the unit, which is the normal case. Privacy is
therefore an act rather than a default; see
[../domain/07-events.md §10](../domain/07a-capacity-presence-and-forms.md#10-cancellation-and-why-there-is-no-status-column).

### Why `fee_schedule_id` and not an `event_fee` table

The fee amount, currency and validity already live in `fee_schedule`
([07-finance.md §2](07-finance.md#2-minimal-provisional-shape)), which is temporal — so a
1998 camp's fee recomputes correctly from the 1998 schedule. An `event_fee` table would
duplicate that and immediately drift. An event points at the schedule that prices it.

---

## 3. `event_organizer`

**The absence of a `valid_to` is deliberate.** This is a *roster*, not a period: you are on
the list, or you are not. An organizer who drops out is removed (recorded in `audit_log`),
because "was Jan an organizer of that camp?" must have one answer, not a set of intervals.

**Fields**

| Field | Kind | Notes |
|---|---|---|
| `id` | surrogate id | Internal only |
| `event_id` | reference to event, required | The event this person is on. Deleting the event removes its organizer rows — the one cascade in this design, and guard 2 in §8 is what makes it safe |
| `person_id` | reference to person, required | |
| `organizer_role` | text, optional | `lead`, `assistant`, `cook`, `driver`, `medic`, `quartermaster` — free text. NOT a controlled vocabulary: every organization labels these differently, and a closed list here would be a guess of the kind [D-095](../decisions/round-09.md#d-095--units-carry-no-restrictions-joining-one-is-somebody-elses-act) refused for reason codes. *(This note pointed at D-054 until D-097 deleted the unit-type vocabulary it argued about; the argument is unchanged and the living precedent for "the system does not ship somebody's vocabulary" is D-095.)* |
| `is_primary` | boolean, required | Default false. The person the parents are told to call. At most one per event — a uniqueness rule the schema can express, so it is a constraint and not a report (Rules, below) |
| `sort_order` | integer, required | Default 0. Display order for the list. Cooks before drivers is a real preference and not something to derive |
| `note` | text, optional | |
| `added_by` | reference to person, optional | Who put them on the roster |
| `created_at` | timestamp, audit time | |

**Rules**

- One row per person per event — the (`event_id`, `person_id`) pair is unique, over all rows.
- At most one organizer of an event has `is_primary` set. The rule covers every row of the
  event; rows where the flag is not set are unrestricted, so an event may have any number of
  ordinary organizers and exactly one primary.
- Removing an organizer is a removal of the row, not the ending of a period, and `audit_log`
  is where the history of it lives. There is nothing to overlap, so there is no no-overlap
  rule here.

> **Cascade on delete here, and nowhere else in this data model.** It is justified because
> `event_organizer` is a roster of *assignments on the event*, not a business record: a
> deleted event has no organizers in the domain sense either. **In practice nothing deletes
> an event** — the deletion policy is temporal closure, and cancellation sets `cancelled_at`.
> The cascade exists so that a mistaken `INSERT` into a draft event can be cleaned up
> without leaving orphan rows, and it is the only cascade in the design. Deleting an event
> that has registrations is refused outright (§8, Guard 2), and the refusal belongs in the database
> rather than in the delete path: the reference from `event_registration` to `event` carries no
> cascade, so an import or a hand-written fix meets the same wall the screens do. A refusal only
> the screens knew about would delete the record of who was coming.

### Organizers are appointments, not grants

`event_organizer` is the **domain** answer to "who is running this camp?" — the labelled,
ordered list that parents see. It is deliberately **not** an `access_grant`, and
[D-062](../decisions/round-05.md#d-062--organizers-are-appointed-on-the-event-not-granted)
is untouched by round 10
([../domain/07-events.md §5](../domain/07-events.md#5-organizers-are-appointed-not-granted)):

- A grant has no room for `organizer_role = 'cook'`.
- "Who is running this camp?" should not be answered by reading the permission table.
- Revoking a grant to remove a cook would also revoke their ability to see the event at
  all, which is not what "they are no longer cooking" means.

**Authority to act on the event does not come from this table.** It comes from a live allow —
at the unit, which reaches this event, or on this event — and never from a role or an
appointment conferring anything by itself
([D-005](../decisions/round-01a.md#d-005--permissions-are-grants-never-derived-from-identity)).

What *did* change is what this table is now **aimed at**. It is the extension of the selector
`ORGANIZERS`, so a grant can name the people running an event without any of them being
granted anything by being listed
([D-102](../decisions/round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)).
**An operand is a set, not a grant** — the same sentence
[data-model/05 §8](05a-audience-and-grammar.md#8-audience--grants-that-target-a-set-of-people) repeats
for named sets generally, and it is why D-062 survives the deletion of the mechanism that used
to make organizers matter. See §8 for the seeded grant that aims at this table.

---

## 4. `event_registration`

One row per person per event. **Two stored values; "unanswered" is the absence of a row.**

**Fields**

| Field | Kind | Notes |
|---|---|---|
| `id` | surrogate id | Internal only |
| `event_id` | reference to event, required | |
| `person_id` | reference to person, required | `person_id`, NOT `membership_id` — the reasoning `unit_participation` gave and [D-098](../decisions/round-10a.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority) carried over to `person_group_member`, and here it is stronger. An event's roster must survive independently of how membership is recorded, and imported historical attendance has no membership row to point at. A 1998 camp roster is participation, and an inferred open-ended membership would put every one of those children inside `MEMBERS` today — see the note below |
| `response` | enum: `attending` / `not_attending`, required | TWO values. `unanswered` is written NOWHERE. It is the absence of a row, so "who has not replied yet?" is a subtraction, not a stored state ([../domain/07-events.md §3](../domain/07-events.md#3-registration-one-record-two-stored-answers-and-no-unanswered)). Returning someone to unanswered deletes the row, which `audit_log` records — the honest act, and the one that leaves least behind |
| `responded_at` | timestamp, required | Default now. When the ANSWER was given, which may differ from when it was recorded. A phone call on Tuesday entered on Thursday has two dates and both matter |
| `source` | enum: `self` / `staff` / `guardian` / `import`, required | Default `self`. How this person got here, and the audit answer to "how did they get in?". `staff` is written by a person holding `event.register_other`, and it bypasses the registration window and the waitlist deliberately (§5, Guard 1): whoever has the permission may register anyone. `guardian` is acting-under-guardianship; the acting person is in `access_log` |
| `registered_by` | reference to person, optional | `NULL` when `source` is `self`. Set otherwise: which organizer, or which guardian |
| `is_waitlisted` | boolean, required | Default false |
| `waitlist_position` | integer, optional | Order within the waitlist. Assigned on insert when the event is at capacity, and rewritten on promotion. See §5 |
| `is_confirmed` | boolean, required | Default false. Registration is not the same as a held place. An event with NO fee confirms immediately on registration; an event WITH a fee confirms on payment (§6). This is the "payment confirms the place" rule, and it is the only place in this module where money changes a registration's meaning |
| `confirmed_at` | instant in time, optional | Set exactly when `is_confirmed` is true |
| `was_present` | boolean, three-valued | `NULL` = not yet marked — no register was taken. `true` = turned up. `false` = marked absent. THREE-VALUED ON PURPOSE: "we did not take a register" and "we took one and they were not there" are different facts, and only one is a safeguarding signal. For a camp this is the record of who was actually in the organization's care, and it cannot be reconstructed afterwards (§9). **It is deliberately not the basis of any selector** — `PRESENT(<event>)` is refused, and why is in §8 |
| `presence_marked_by` | reference to person, optional | The person who took the register. Held by whoever has been *allowed* `event.presence.mark` — deliberately a separate code from `event.manage_participants`, not a rung beneath it: after [D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality) there is no ladder for one permission to sit below another, and that is the stronger form of the same protection. The volunteer at the door is not also the person who can delete a child from the roster, because they were granted one code and not the other |
| `presence_marked_at` | instant in time, optional | When the register was taken |
| `fee_obligation_id` | reference to fee obligation, optional | Set when the event has a `fee_schedule` and this registration created an obligation. The reverse pointer from `fee_obligation.event_registration_id` also exists (§6) — both directions, because each is asked a different question: "what does this person owe for this camp?" and "what is this obligation for?" |
| `created_at` | timestamp, audit time | |
| `updated_at` | timestamp, audit time, optional | |
| `updated_by` | reference to person, optional | |
| `import_batch_id` | reference to import batch, optional | Set on imported rows |

**Rules**

- One row per person per event, full stop — the (`event_id`, `person_id`) pair is unique over
  all rows. This is what makes "unanswered = absence" work: there is exactly one place an
  answer could live.
- A `not_attending` row has `is_waitlisted` false and `is_confirmed` false. A decline is not
  waitlisted and not confirmed; otherwise a "no" could hold a place on the waitlist, which is
  nonsense.
- `is_confirmed` is true exactly when `confirmed_at` is set.
- `is_waitlisted` is true exactly when `waitlist_position` is set.
- Presence is marked all together or not at all: `was_present`, `presence_marked_by` and
  `presence_marked_at` are either all present or all absent, and `was_present` absent is the
  same condition as the other two absent. A partially-set trio is a bug, not a state.

**Indexes**

- **The set the capacity test counts** — an event's registrations whose `response` is
  `attending` and which are not waitlisted. Capacity is compared against exactly this set
  (§5), and the other registrations of an event must not slow it down. **This index is also
  exactly the extension of the `PLACED` selector** (§8), so the audience the capacity rule
  counts and the audience a grant may name are the same rows, served by the same index — no
  second index and no second definition.
- An event's waitlist in `waitlist_position` order, restricted to waitlisted rows — which is
  the extension of `ON_WAITLIST` (§8).
- An event's registrations by `was_present`, restricted to rows where presence has been
  marked at all. Note that this index serves a **report** (§9) and no selector: the rows it
  is missing are precisely the unmarked ones, and that is the reason `PRESENT` is refused.

### Why `person_id`, not `membership_id`

The argument `unit_participation` made
([03-membership.md §5](03-membership.md#5-unit_participation--deleted-by-d-097), before D-097 deleted it) and
[D-098](../decisions/round-10a.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority)
transferred to `person_group_member`, and it is stronger here. An
imported 1998 camp roster names children who have no membership row to point at. With the
corpus being large and number-bearing
([D-056](../decisions/round-04.md#d-056--the-legacy-import-expects-a-large-corpus-with-legacy-member-numbers)),
linking to `membership` would make those rows unrepresentable.

**And the harm moved rather than went away.** It used to be argued through the membership
gate, which made a 1998 camper a current member with authority today. The gate is deleted
([D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)),
and the same harm now runs through the selector: `MEMBERS` is evaluated live on the checked
date, so an inferred open-ended membership puts every one of those children inside `MEMBERS`
today, and every live grant whose expression contains `MEMBERS` reaches them. An
open-ended row is the dangerous object under both models; only the mechanism changed.

**The trade-off, stated:** no database constraint can enforce "only members may register", and
none is wanted — eligibility is capability ([../domain/07-events.md §4](../domain/07-events.md#4-who-may-register-capability-not-a-separate-rule-engine)),
and capability is a grant, not a membership row.

---

## 5. Capacity and the waitlist

**Capacity is a threshold, not a block.** Registering for a full event succeeds and produces
a waitlisted row.

**Is this event at capacity?** The question is asked of one event and answered only from the
registrations it has: count its `attending`, non-waitlisted registrations — **its `PLACED`
set** (§8) — and compare that count with its `capacity`. An event with no `capacity` is never
full — with no capacity set there is nothing to reach, and the answer is no.

**The placing rule** runs before the row is written, once per row, on every insert, so that
EVERY insert path obeys it — self-service, staff, guardian and import alike.
Application-level placement would let one of the four paths forget, and the forgotten one
would be the one that matters. **The order of these steps is a rule**: the decline branch
settles all four flags and ends the rule, and the capacity test is counted before confirmation
is decided, because confirmation is a property of the place the earlier steps gave the row.

1. Read the event the registration names.
2. A decline never occupies a place. If `response` is not `attending`, set `is_waitlisted`
   false and `waitlist_position` absent, set `is_confirmed` false and `confirmed_at` absent,
   and stop here — none of what follows applies to a "no".
3. Waitlisting is a SELF-SERVICE outcome. Waitlist the row when all three of these hold:
   `source` is `self`; the event has a `capacity`; and the event's `attending`,
   non-waitlisted registrations already number at least that capacity. Then set
   `is_waitlisted` true and `waitlist_position` to one past the highest position already on
   that event's waitlist — `1` when the waitlist is empty. If any of the three fails, set
   `is_waitlisted` false and `waitlist_position` absent. A staff registration is admitted
   even past capacity: the organizer who knows there are two spare tents is not to be blocked
   by a number they cannot edit mid-camp
   ([../domain/07-events.md §8](../domain/07a-capacity-presence-and-forms.md#8-capacity-and-the-waitlist),
   [D-065](../decisions/round-05.md#d-065--capacity-is-a-waitlist-threshold-and-organizers-may-exceed-it)).
   The overrun is permitted, attributed, and REPORTED (§10, check 5).
4. Confirmation: immediate when there is no fee to wait for. If the event has no
   `fee_schedule_id`, set `is_confirmed` true and `confirmed_at` to now. Otherwise set
   `is_confirmed` false and `confirmed_at` absent — §6, payment confirms the place.
5. Write the row carrying those flags.

The rule runs on insert only; a later edit of the row does not re-run it. Promotion and the
release below write the same flags deliberately.

> **The `source = 'self'` disjunct is the whole of "organizers may register anyone", made
> mechanical.** Removing it silently reverses the answer: every staff registration would be
> waitlisted behind self-service ones, and the leader adding a child on the day would be
> told the camp is full when they can see two spare beds. Note what this rule does **not**
> consult: not a level, not a role, and since D-102 not an owning unit. `source` is a stored
> fact written by whoever holds `event.register_other`, and the capacity rule reads the fact.

### Promotion, which is a deliberate act

Promotion is **not automatic** — no trigger, no job. An organizer picks someone from the
waitlist:

1. Take the one registration this person holds at this event — the pair names exactly one row
   (§4).
2. Clear the waitlist on it: `is_waitlisted` false, `waitlist_position` absent.
3. Set `is_confirmed` and `confirmed_at` by exactly the test the placing rule uses: confirmed
   now when the event has no `fee_schedule_id`, unconfirmed with no `confirmed_at` when it has
   one.

The promotion deliberately bypasses the capacity test: the whole point of promoting is that a
place has freed up, and re-testing would just fail again.

Promotion writes the same two flags the placing rule would have, so a promoted registration
and an admitted one are indistinguishable afterwards — which is correct, because the
difference between them is *when*, not *what*.

### When an unpaid registration releases its place

If `waitlist_deadline` is set, an unpaid registration at a full event releases its place to
the waitlist at that moment. This is **the one automatic transition in this module**, and it
is recorded as such. The release is scoped as narrowly as the rule can be: only at a full
event, only with a fee configured, only past the deadline, only unpaid, and never a staff
registration (which is admitted by hand and by a human who can see the roster).

1. Take every registration that is `attending`, not already waitlisted, `source` `self`, and
   not confirmed.
2. Keep only those whose event has a `fee_schedule_id`, has a `waitlist_deadline`, has that
   deadline already past, and is not cancelled.
3. Move each one onto the waitlist: `is_waitlisted` true, `waitlist_position` one past the
   highest position already on that event's waitlist — `1` when the waitlist is empty.
4. Take the place back: `is_confirmed` false, `confirmed_at` absent.

> **Why this is accepted despite the design's habit of avoiding automatic transitions.** The
> design has spent real effort keeping state changes deliberate
> ([D-023](../decisions/round-01b.md#d-023--nothing-is-auto-lapsed-or-auto-terminated),
> [D-040](../decisions/round-02-03.md#d-040--the-fee-expires-yearly-a-date-tracked-renewal-window-replaces-a-grace-status)),
> and "payment confirms the place" reintroduces one. It is a *deadline*, not a sweep: it
> applies to a narrow conjunction, it is opt-in per event (`waitlist_deadline` is `NULL` by
> default, so most events never run it), and the state it produces is visible — the person
> is on the waitlist, not silently deleted. The alternative, no deadline at all, means a
> place is held forever by someone who never paid, which is worse.

---

## 6. Payments and confirmation

**Registering creates a fee obligation; payment confirms the place.**

**Creating the obligation** runs after the registration row is written, so that the
registration has an id to be pointed at. The order is a rule: the obligation cannot be
created before the registration it belongs to exists, and the registration's
`fee_obligation_id` cannot be written before the obligation does.

1. Read the event the registration is for.
2. If the event has no `fee_schedule_id`, or the registration is not `attending`, stop — a
   free event owes nothing, and a place someone declined owes nothing.
3. Read the fee schedule the event points at.
4. Create one `fee_obligation` for this registration, carrying: `person_id` taken from the
   registration; `event_registration_id` set to the registration; the event's
   `fee_schedule_id`; the event's title as the description; the event's start and end as the
   obligation's period; the schedule's amount and currency; and a due date of the event's
   `waitlist_deadline`, falling back to the event's `starts_at` when it has none.
5. Write the new obligation's id into the registration's `fee_obligation_id`.

**The pointer that had to be restored.** [D-057](../decisions/round-04.md#d-057--household-is-removed)
removed the household arm from the exactly-one rule over `fee_obligation`'s target columns,
leaving two of them (membership or membership request, never both). An event fee needs an arm back — and this time it is a *real* arm
with data behind it, not the dormant hedge the household column was.

The arm lives in `fee_obligation` and is stated there in full
([07-finance.md §2](07-finance.md#2-minimal-provisional-shape)): exactly one of
`membership_id`, `membership_request_id` and `event_registration_id` is set on every
obligation. Still exactly one, not "at most three" — every obligation is for exactly one
thing: a membership period, a membership request, or one person's place at one event. The
per-person choice is deliberate, because the fee is flat and per person (D-037) and a family
price would need the household grouping designed again first. Obligations carrying the event
arm are indexed on `event_registration_id`, restricted to the rows where it is set.

### Confirming on payment

`confirm_event_place(obligation)` is called by the payment flow. It is **not** a rule on
`fee_obligation`'s status — the payment module owns that transition, and a rule there would
make every fee, membership or event alike, confirm an event place.

1. Take the obligation the call names.
2. Follow its `event_registration_id` to the registration it pays for.
3. Confirm that registration only when it is `attending` and not waitlisted — in the
   selector vocabulary, only when it is `PLACED` (§8); a waitlisted person stays waiting
   until promoted (§5), so paying does not by itself place them.
4. Confirming means setting `is_confirmed` true and `confirmed_at` to now.

> **`confirm_event_place` is deliberately an operation the finance module calls, not a rule
> hanging off `fee_obligation`'s status change.** The argument is about ownership and does not
> depend on where the code lives: anything that fires because a fee became paid fires for
> membership fees and event fees alike, and "the fee is paid" means something different in each
> case: a membership activates
> ([D-040](../decisions/round-02-03.md#d-040--the-fee-expires-yearly-a-date-tracked-renewal-window-replaces-a-grace-status)),
> an event place confirms. Two transitions, two owners.

**Free events confirm immediately** — see the placing rule in §5. An event with no
`fee_schedule_id` has nothing to wait for, and requiring "confirmation" for a free hike
would be a state with no meaning.

---

## 7. `event_question` and `event_answer`

**Fields — `event_question`**

| Field | Kind | Notes |
|---|---|---|
| `id` | surrogate id | Internal only |
| `event_id` | reference to event, required | The event that asks it. A question is defined per event, never shared (§7) |
| `label` | text, required | `Tent preference`, `Dietary requirements` |
| `help_text` | text, optional | |
| `position` | integer, required | Default 0. Display order |
| `data_type` | enum: `text` / `long_text` / `integer` / `decimal` / `bool` / `date` / `choice` / `multichoice`, required | |
| `choices` | list of text, optional | For `choice` and `multichoice` only. An ordered list on the question rather than a child table: the options are a property of the question, they are ordered, and they are never referenced by anything else |
| `is_required` | boolean, required | Default false. The person REGISTERING must answer. Not a gate on registration itself: a form that blocks sign-up is a form nobody completes, and the organizer would rather have the registration and chase the answer |
| `applies_to` | enum: `attendee` / `organizer` / `all`, required | Default `attendee`. Who is asked. Organizers may be asked things attendees are not (T-shirt size for the leaders' shirts) and vice versa |
| `valid_from` | date, required | Default today |
| `valid_to` | date, optional | `NULL` = still asked. A question can be retired after people have answered it. Answers survive (an answer is never removed with its question), because "what did they say?" must outlive "do we still ask this?" |
| `created_at` | timestamp, audit time | |
| `created_by` | reference to person, optional | |

**Rules — `event_question`**

- `choices` is present exactly when `data_type` is `choice` or `multichoice`, and never
  otherwise. Stated as an equivalence rather than a one-way requirement so that a `text`
  question cannot carry a stray `choices` list that the UI might honour.
- `valid_to` is either absent or later than `valid_from`.

**Fields — `event_answer`**

| Field | Kind | Notes |
|---|---|---|
| `id` | surrogate id | Internal only |
| `question_id` | reference to event question, required | |
| `person_id` | reference to person, required | Who ANSWERED — for a child, the child. The person who submitted on their behalf is in `access_log` and in `registered_by`, not here. Answers are about the person the question concerns |
| `value` | free-form jsonb, required | Typed by `question.data_type`. One loose value rather than a column per type: the alternative is eight nullable columns only one of which is ever set, which is the shape 01-identity.md §6 rejected for `person_contact` |
| `answered_at` | timestamp, audit time | Default now |
| `answered_by` | reference to person, optional | |

**Rules — `event_answer`**

- One answer per question per person — the (`question_id`, `person_id`) pair is unique over
  all rows.
- An answer is not removed when its question is retired: there is no delete rule from
  `event_question` to `event_answer`.

### Answers as rows, not JSONB on the registration

This is the choice that makes the feature worth having. The whole reason to collect
"dietary requirements" is to be able to answer **"who needs a gluten-free meal, and how
many?"** — and that is a question the data must answer directly: for one event and one
question, take every answer given to it, group the answers by the value given, and count each
group, largest group first.

With answers stored as a JSONB blob on the registration, that becomes JSON traversal, an
index that does not help, and a report nobody writes. The cost is one row per answer — which
is exactly the number of things the organization must act on.

### Reusable question libraries were considered and rejected

A shared pool of question definitions — `question_code`, assigned to events — is
structurally the requirement machinery removed in
[D-044](../decisions/round-02-03.md#d-044--nothing-gates-a-membership-request-except-identity-and-payment).
It earns its keep only when the same question must mean the same thing across events, and
tent preference does not: what one camp asks and what another needs are allowed to differ.
Per-event definitions keep them from having to agree, and avoid reviving a removed pattern
for a benefit nobody asked for.

### Health facts, and the discipline this requires

> **An event form is how the people running an event find out what they need to know about the
> people who came.** It used to be the *only* way. [D-085](../decisions/round-07-08.md#d-085--the-identity-machinery-stays-structured-the-boundary-is-rules-not-sensitivity)
> ended that, and the guidance below is still worth reading as a warning rather than a nicety —
> anything a form asks is read by whoever runs that event, and the number of such people is decided
> by whoever creates the event
> ([D-061](../decisions/round-05.md#d-061--event-answers-are-read-by-that-events-organizers),
> [../domain/07-events.md §12](../domain/07a-capacity-presence-and-forms.md#12-the-forms-questions-and-answers)).
>
> **Round 10 moved that sentence from the resolver into a row.** "Read by whoever runs that
> event" is now a seeded grant — `event.answer.view` on the event, aimed at `ORGANIZERS` (§8).
> That makes the warning *checkable* in a way it was not before: the number of people who can
> read an event's answers is a grant plus the roster in §3, and both are readable.

**This sentence's reason has now been rewritten twice, and the second rewriting killed the claim.**
It began as "the `dependent.*` namespace is unreachable by unit leaders"; [D-074](../decisions/round-06.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular)
deleted that namespace and the claim survived on a better reason — no `event.*` permission includes
the medical record, and no wildcard is left to sweep it in (D-068). **Both halves are now gone: there
is no medical record** ([D-083](../decisions/round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)),
and the facts that would have been in one are attributes on the person, which
**a person holding `person.view` at the unit can read** — and after
[D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row) the unit is the
only scope there is, so that grant reads everyone's
([09-attributes §4](09-attributes.md#4-who-may-read-and-who-may-write)). A claim that had outlived two
of its reasons should not be repaired a third time; it is stated as what is now true:

- **The form is no longer the ceiling on what an organizer may know.** An organizer who holds
  `person.view` may already have read the allergy. Any document implying the contrary was
  quietly making a privacy promise the model does not keep.
- **What the form is for changed accordingly** — it asks *now*, about *this* event, of a person who
  may not be in the system at all, and its answer carries a date. That is a genuine property the
  record does not have: a recorded attribute says what somebody believed, once, at no particular
  time. Whether the two should meet at all is [AT-1](../open-questions.md#at-1--should-an-event-question-bind-to-an-attribute-code),
  and the recommendation there is a confirmation pass rather than a silent prefill, precisely because
  a stale health fact that arrives looking authoritative is worse data than an asked question.
- **Nothing in the data model distinguishes a preference from a condition**, and now nothing *could*:
  [D-083](../decisions/round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)
  refused the category. "Vegetarian" and "coeliac" are both `data_type = 'text'` in
  `event_answer.value`, so the line is what an organizer types into `label` — **form design guidance,
  not an enforced constraint**:

| Belongs on an event form | Belongs on the person, as an attribute |
|---|---|
| What the organizers need **on the day**, for this event | Diagnoses, medication, allergies, conditions |
| What a visitor who is not in the system must supply | Anything already recorded, curable and audited on the record |
| T-shirt size for a camp that is ordering shirts now | Anything whose value outlives the event that asked |

Asking a returning camper to restate a recorded allergy at every event is not a privacy measure; it
is the same fact, fresher in one table and unmanaged in it. **The honest reading of this section is
that the event answer is where a health fact lands when the organization has not collected it
properly** — and the fix is the record plus a confirmation pass, not a cleverer form.

**Open:** the retention policy for answers. A dietary answer citing a medical condition is data of
exactly the same class as everything else the organization holds about a person — [D-083](../decisions/round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)
settled that there is no specially-sensitive category, not that this data is insignificant — and
there is no policy for how long answers survive their event. See
**[EV-2](../open-questions.md#ev-2--retention-of-event_answer)**, which notes that until it is
answered the weakest-protected copy of a health fact is the freshest one.

---
