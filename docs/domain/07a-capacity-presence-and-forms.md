# Events: capacity, presence, payments and the forms

What happens between a filled capacity and a completed event: the waitlist, attendance, cancellation, the money, and the questions an organizer asks.

**Section numbers are shared across the two parts** and never renumbered, because other pages cite them by number and their anchors are built from them: [07-events.md](07-events.md) holds §1–§7, [07a](07a-capacity-presence-and-forms.md) §8–§13 (capacity and the waitlist, presence, cancellation, payments, the forms, open issues).

---

## 8. Capacity and the waitlist

An event may have a capacity — beds, bus seats, a fire-safety limit. When it fills:

**Registrations past capacity are accepted as waitlisted**, not refused. A person who
registers for a full camp appears on the list, ordered, marked as waiting, and an organizer
promotes them when a place frees up.

This is a real feature rather than a flag, and it is the honest model of how a camp with
twelve beds actually runs: the thirteenth caller is not turned away, they are written down.
See [data-model/08 §5](../data-model/08-events.md#5-capacity-and-the-waitlist) for the
ordering and promotion mechanics.

**And organizers may exceed capacity outright** — deliberately, because a leader who knows
there are two spare tents should not be blocked by a number they cannot edit mid-camp
([D-065](../decisions/round-05.md#d-065--capacity-is-a-waitlist-threshold-and-organizers-may-exceed-it)).
The overrun is permitted, attributed, and **reported**
([data-model/08a §10](../data-model/08a-event-guards-and-checks.md#10-integrity-checks)): an event running over
its stated capacity is a fact the organization can see, not a state it cannot reach.

The way past the number is not the resolver: the waitlist fires only for `source = 'self'`, and a
registration written by a person holding `event.register_other` arrives as `source = 'staff'` and is
admitted. `event.register_other` is a grant at the unit or on the event, like every other code
([D-102](../decisions/round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)).

So capacity is three things at once, and all three are intentional:

| | Behaviour |
|---|---|
| Self-registration when full | **Waitlisted** — never refused, never admitted |
| A staff registration when full | **Admitted**, the overrun reported |
| Any capacity change | An `UPDATE`, visible and attributed |

The set capacity is compared against has a name: it is **`PLACED`**, the attending
non-waitlisted registrations of an event
([§7](07-events.md#7-the-people-connected-to-an-event)) — the same set `PLACED` selects and the same
index the capacity test already uses.

---

## 9. Presence: what actually happened

The registration says what someone *said*. Presence says what *happened*.

`event_registration.was_present` is a **nullable boolean**:
`NULL` = not yet marked, `true` = turned up, `false` = marked absent. The three-valued
column is not sloppiness — it distinguishes *"we did not take a register"* from *"we took a
register and they were not there"*, which are different facts and only one of them is a
safeguarding signal
([D-067](../decisions/round-05.md#d-067--presence-is-a-three-valued-fact-on-the-registration)).

**Why this matters more than it looks.** For a camp, the end-of-week roster is the record
of who was actually in the organization's care — **the only "who was there" this design
keeps**, which is the reason it is marked deliberately rather than derived
([D-156](../decisions/round-22.md#d-156--the-fee-buys-nothing-but-membership) removed the other
reason anybody had to ask: the fee buys membership and nothing else, so no date in this system is
evidence of cover, and the question "was this person a member on the date of the incident" is no
longer a question this system is asked to answer). It is also the row that cannot be reconstructed
afterwards from registrations. It is also why the column is
marked by an organizer and recorded with who marked it and when.

**Presence is not registration.** A child who registered and did not come is a registration
with `was_present = false`. A child who turned up without registering — a sibling along for
the day — is not representable, deliberately: that child was not in the organization's care
and must not silently appear to have been. Recording them means registering them, which
means they have a guardian and the organizers have a name.

**And presence is not a record class.** It is a column of a registration and it inherits everything a
registration is: the same retention — nothing about an event goes on a schedule, so this mark is readable for
as long as the registration is ([D-140](../decisions/round-20.md#d-140--nothing-about-an-event-is-deleted-on-a-schedule-and-erasure-empties-an-answer-without-deleting-it))
— and the same codes that already reach the roster and the mark
([D-147](../decisions/round-20.md#d-147--presence-stays-on-the-registration-no-clock-of-its-own-no-permission-of-its-own)).
**Refused on both halves:** no `presence_record` table with a retention of its own, and no `presence.view`
narrower than the roster's — the second would have been a permission whose whole purpose is to hide the fact of
attendance from the people asking *because they were there*. **This system keeps no safeguarding register:**
there are no background checks here ([D-043](../decisions/round-02-03.md#d-043--no-background-checks-are-recorded-in-this-system))
and no medical record ([D-083](../decisions/round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)),
and a column with a special clock and a special permission would have been the first wall of an archive this
design has refused four times. **The protection this column has is that it is boring**, and the question *"who
was there on 14 March"* is answered by a report over registrations — which is why the index behind
`was_present` serves a report and no selector.

**And presence is not an audience.** The temptation to build `PRESENT(<event>)` on this
column — to let "everyone who came" be a set a grant names — is refused, and
[§7](07-events.md#7-the-people-connected-to-an-event) states why:
the column is `NULL` until somebody takes a register, so an operand over it makes access
depend on a volunteer's diligence, and it would turn a safeguarding record into an access
control. Attendance for the purposes of a grant stops at `ATTENDED`, `PLACED`, `CONFIRMED`
and `ON_WAITLIST`.

**And there is no `WHITELISTED` beside those four.** No `is_whitelisted` column, no fifth tier, no
operand of that name, no reserved selector code waiting for one
([D-148](../decisions/round-20.md#d-148--there-is-no-whitelisted-and-the-refusal-is-written-where-the-tiers-are)).
The word is what people reach for when they want an audience of *the ones we invited*, and **anybody adding
`is_whitelisted` is reimplementing grants badly**: a tier is a state a registration is in, and an invitation is
not about a registration at all — it is a grant aimed at a person, which is a row that already exists and says
who aimed it at whom. The invited person who has not registered is described by **the absence of a row** until
they do, and is `ON_WAITLIST` the moment they register onto a full event
([D-059](../decisions/round-05.md#d-059--unanswered-is-the-absence-of-a-row-a-registration-stores-two-values));
that is not a gap a fifth value fills, because `PLACED` *is* the capacity set, so a whitelist set beside it
misdescribes everybody in it. **What this costs is what every prose refusal costs:** nothing in the database
refuses a future `WHITELISTED` row in `selector_type`, so an operand with no state behind it is a deployment bug
and not a type error — the same exposure an off-list actor label carries.

---

## 10. Cancellation, and why there is no `status` column

**There is no lifecycle status.** An event is a row with dates and a set of grants.

**Visibility *is* the permission model.** A newly created event has no grants of its own, so
whoever can see it can see it because of a grant they already hold — normally an
`event.view` at the unit, which reaches every event and therefore every new one the moment it
is created. Publishing is not a state change — it is **granting** someone access: an audience,
a group, a role.

*Why not a `status` enum:* a status column and a permission system
that both claim to say "who may see this" will eventually disagree, and the one that gets
enforced is whoever wrote the last `IF`
([D-064](../decisions/round-05.md#d-064--there-is-no-event-status-visibility-is-the-permission-model)).

**There is no narrow default, and that is the shape of the model.** After
[D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row) the unit is
the only scope there is, so a person holding `event.view` at the unit sees a half-typed event the instant
it is committed, and there is no narrower scope a grant could have sat at instead. **A genuinely private
event is therefore an *act*** — an item grant, plus a deny at the unit if the audience is broad — rather
than the absence of one.

So the questions that a `draft` status would answer are answered by grants:

| Question | Answer |
|---|---|
| "Is this ready to be seen?" | Has anyone been granted `event.view` beyond the unit-scope holders? |
| "Who can see it before it is announced?" | Whoever a live allow names — including every unit-scope holder |
| "How do I hide it again?" | Revoke the grant — `revoked_at` set, row kept — or write a deny |

**Cancellation is a fact, not a status**, and the logic diverges from visibility here because the audience
is different: the people who need to find out are the people who registered, and they must be able to see
the event to find out anything.

Three columns carry it: `cancelled_at` says when, `cancelled_by` says who — a person, so the
decision has a name attached to it — and `cancel_reason` says why.

> **Cancelling by revoking grants would hide the cancellation from exactly the people who
> need it.** The registrants are the ones who need to read that the camp is off; if the event is
> hidden by revoking their `view`, they see nothing at all — not "cancelled", just gone.
> So cancellation is recorded, and the event stays visible, marked.

A cancelled event **stops accepting registrations** (the registration window closes
implicitly) and **keeps every existing row**: those registrations are the record that the
camp was planned and who was coming. That record is exactly what is needed afterwards — to refund
them, and to know whom a cancellation notice would have to reach, since nothing in this design sends one
([D-164](../decisions/round-22.md#d-164--nobody-is-told-and-no-page-may-say-otherwise)).

**`completed` is derived, never set.** `cancelled_at IS NULL AND ends_at < now()`. There is
no state to keep consistent, and no job to move events between states.

**One more thing, which is structural:** there is no `event.is_published` and no
`cancelled` *status*, but there **is** a `cancelled_at`. An event that is cancelled and an
event that is merely past are distinguished by one `NULL` — and the "what needs attention?"
query is `WHERE cancelled_at IS NULL AND ends_at >= now()`, ordering by start. That is the
whole lifecycle.

---

## 11. Payments on events

An event may cost money, and **payment confirms the place** — but payment is never
mandatory, because plenty of events are free.

The rule, stated once:

| | |
|---|---|
| An event with a fee | Registering creates an obligation; **the place is confirmed on payment** |
| An event without a fee | Registering confirms the place immediately |
| An unpaid registration at capacity | Holds a slot **until the deadline**, then releases to the waitlist |
| Money | **The finance module's problem** — events record that a fee applies and what it is |

The only schema here is a **pointer**: `fee_obligation.event_registration_id`, one arm of
`fee_obligation`'s exactly-one rule — an arm with rows behind it, not a dormant hedge.

**The `is_confirmed` / deadline interaction is the one automatic transition in this module**,
and it is worth flagging as such: the design avoids automatic state changes
([D-023](../decisions/round-01b.md#d-023--nothing-is-auto-lapsed-or-auto-terminated),
[D-040](../decisions/round-02-03.md#d-040--the-fee-expires-yearly-a-date-tracked-renewal-window-replaces-a-grace-status)),
and payment-confirms-the-place is the one it accepts. It is a *deadline*, not a sweep: it applies
only to registrations at a full event with an unpaid fee, and only after the deadline the
organizer set. [data-model/08 §6](../data-model/08-events.md#6-payments-and-confirmation)
records it as an accepted cost with the reasoning, and
[open-questions](../open-questions.md) carries it.

---

## 12. The forms: questions and answers

An event may ask registrants for details it needs — tent preference, dietary preference, T-
shirt size, whether they are coming by bus.

**Questions are defined per event, and answers are rows.**

```
event_question          what this event asks
   │
   └── event_answer     what a person said    ──  one row per question per person
```

Answers as **rows rather than JSONB** is the choice that makes the feature work: *"who needs
a gluten-free meal, and how many?"* is a `GROUP BY`, not a JSON traversal. The cost is a row
per answer, which is correct — the number of answers is the number of things the
organization must actually act on.

Questions may apply to **attendees, organizers, or both**, and may be required or optional.
Required means *the person registering must answer*; it is not a global gate on
registration, because a form that blocks sign-up is a form nobody completes.

**Reusable question libraries are rejected.** A shared pool of question definitions is structurally the
requirement machinery removed in
[D-044](../decisions/round-02-03.md#d-044--nothing-gates-a-membership-request-except-identity-and-payment),
and it earns its keep only when the same question must mean the same thing across events.
Tent preference does not: what one camp asks and what another needs are allowed to differ,
and per-event definitions keep them from having to agree.

### Health data, and the widening this represents

**Event answers are readable by that event's organizers, with no extra gate**
([D-061](../decisions/round-05.md#d-061--event-answers-are-read-by-that-events-organizers)).
The mechanism is **a grant written by the act that creates the event**: `event.answer.view` on that event,
aimed at the bare operand `ORGANIZERS`, in the same transaction as the event row
([D-102](../decisions/round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it),
[D-151](../decisions/round-21.md#d-151--creating-an-event-writes-the-events-authority-and-its-organizers-may-grant-on-it)).
It is one of the twelve the creation writes — every `event.*` code whose `applies_to` admits an event — and
it is written **without** `MEMBERS`, because an organizer appointed for one weekend is not required to be a
paying member. Three things follow:

- **"No extra gate" is literally true and visible.** That grant *is* the whole
  mechanism; there is no clause special-casing organizers. Anyone who wants to see who may
  read an event's answers reads a grant row.
- **The reach of that grant is per-event.** `ORGANIZERS` with no argument binds to the event the grant
  sits on, so the row cannot accidentally name the organizers of every camp at once.
- **A create is the author of an event's authority.** Whoever holds `event.create` decides who will be
  able to read a future event's answers, and the widening is one code deep. What keeps it honest is that
  *"who could read those answers?"* stays a query over rows, and an event whose rows did not arrive is a
  countable failure rather than a rumour.

Two consequences of that reach follow, and the second is the significant one.

**1. Only preference-level detail belongs on a form.** A dietary *preference* ("vegetarian",
"no pork") is an operational note for the cook. A *condition* ("coeliac", "nut allergy") is
medical data, and nothing in the schema distinguishes them — the difference is what the
organizer types into a label. So the discipline is in the form design, not the constraint:
[data-model/08 §7](../data-model/08-events.md#7-event_question-and-event_answer) states it,
and it is guidance, not enforcement.

**2. This is the route by which a leader learns a child has a nut allergy, and that is a
deliberate widening.** A guardian's reach over a child is **one value on the `guardianship` row**
— `none`, `view` or `write` — read by a channel of its own, entered only when the act is about
someone other than the actor and never answered by a role or a grant
([D-074](../decisions/round-06.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular),
[D-079](../decisions/round-06.md#d-079--the-guardianship-channel-is-entered-by-shape-not-by-permission-name);
[appendix/permission-catalog.md §9](../appendix/permission-catalog-b-roles-and-open-issues.md#9-there-is-no-dependent-namespace)).
What a leader gets over a child's data is not of that kind:

> *"A person does not get these by virtue of leading — that is a safeguarding
> property."*

**There is no medical record to be unreachable.** Personal data is one class
([D-083](../decisions/round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)),
so a guarantee that a camp leader *"cannot reach a child's medical record at all"* describes a
category the model does not have. What is true, in the two forms that matter:

- **No role gets it by leading.** A leadership role written out of the worked examples is given its
  rosters and its events — and **no read over a person's data**
  ([permission-catalog §11](../appendix/permission-catalog-b-roles-and-open-issues.md#11-roles--worked-examples-of-writing-one)).
  Leadership is not guardianship, and the guardianship channel answers only for the person its
  row names.
- **It is one grant away.** Whoever holds
  `person.view` **at the unit** reads every child's whole record, allergy list included, and
  a grant at the unit has no narrower reading available, because the unit is the only scope
  there is ([D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)).
  Nothing in the resolver will stop that and nothing should — but the model does not promise it
  is impossible either, and a promise the model does not make is worse than none.

**So the protection is a decision about a role, revisitable by whoever administers roles — not a wall.**

Which means: under any office written the way those examples write one, an allergy recorded on a camp form
is **the only way the people running the camp will know**. That is a coherent and defensible configuration
— *the parent tells the people present, per event, and nobody outside the family holds the fact* — but it
is a widening from "the
few adults whose `guardianship` row names them, at one `right_level`" to "every organizer of any event the
child registers for", and it is recorded as such in
[D-061](../decisions/round-05.md#d-061--event-answers-are-read-by-that-events-organizers),
with the reasoning, so that nobody later "fixes" the apparent duplication between the two
stores by tightening this one.

**Event answers are not the person's record.** They are operational detail for one event, read by that
event's organizers — and **they are kept**: nothing about an event goes on a schedule, so an answer outlives
its event, its organizers and the season that asked the question
([D-140](../decisions/round-20.md#d-140--nothing-about-an-event-is-deleted-on-a-schedule-and-erasure-empties-an-answer-without-deleting-it)),
while the same fact recorded on the person is audited, curable and erased with them. Those two copies are
**the same class of data**
([D-083](../decisions/round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)),
and the retention question that used to sit between them — the same sentence of personal data kept forever in
one table and quietly discarded in another — **is closed by the two rules agreeing, not by a schedule**: an
erasure reaches both, and the only difference left is the shape of the reaching, a delete where the row *is* the
value and an emptying where the row is also a fact about the event. What still differs between the copies is
who may read them, which is the widening the paragraphs above record. See
[AT-1](../open-questions.md#at-1) for the alternative this round took up instead of choosing between the two
stores: **collect the fact once and confirm it at the door** — a bound question prefills from the stored value
as a suggestion and writes back a fresh dated one
([D-139](../decisions/round-20.md#d-139--an-event-question-may-bind-to-a-stored-value-it-prefills-as-a-suggestion-and-writes-back-as-an-answer)).

---

## 13. Open issues

Tracked with the rest in [../open-questions.md](../open-questions.md): the answered ones under
**R. Resolved**, each carrying the decision that answered it, and the live ones where the module map points.
**Five of the seven below are settled and say so rather than reading as still open** — that is deliberate,
because a list of open issues that keeps asking an answered question is how a design gets reopened by a
newcomer who reads the list and not the log. The ones this module raises:

- **The age ceiling on an open event — settled: accepted as a risk.** The grant is the rule, and a
  ceiling is writable today as `event.register_self` aimed at `MEMBERS * YOUNGER(15)`
  ([§4](07-events.md#4-who-may-register-capability-not-a-separate-rule-engine),
  [D-107](../decisions/round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)).
  **EV-1 stays closed as a choice
  the organization renews rather than a limit it inherits** — nobody has to be told the ceiling
  cannot be stated, only whether it should be
  ([§4](07-events.md#4-who-may-register-capability-not-a-separate-rule-engine),
  [D-070](../decisions/round-05.md#d-070--an-event-has-no-age-ceiling-the-grant-is-the-rule)).
- **What else an organizer should hold — settled: the bundle is derived, not curated.** Creating an
  event writes one item-scope `allow` per code whose `applies_to` admits an event — **twelve beside every
  event**, `event.answer.view` among them — each aimed at `ORGANIZERS`
  ([D-151](../decisions/round-21.md#d-151--creating-an-event-writes-the-events-authority-and-its-organizers-may-grant-on-it)).
  A code added to `event.*` is in the next event's bundle without anyone remembering a list. Everything
  outside those twelve reaches an organizer only through a unit-scope or item grant they happen to hold,
  and that is the intended shape: the creation act writes the set of people connected to the item, and
  writes nothing else
  ([§5](07-events.md#5-organizers-are-appointed-not-granted),
  [§6](07-events.md#6-how-authority-reaches-an-event)).
- **Whether a bound selector makes its audience single-scope.** An audience whose expression
  names `PLACED` cannot be aimed at a unit-scope grant, so a shared audience row can stop
  being reusable across scopes. The refusal lands on the grant, which is faithful to the rule
  as written; whether the editor should warn at the audience instead is unsettled
  ([§7](07-events.md#7-the-people-connected-to-an-event)).
- **`WHITELISTED` — settled: refused.** No stored state to name it, so it is not a selector, and there will be
  no fifth presence tier, no `is_whitelisted` column and no reserved name
  ([D-148](../decisions/round-20.md#d-148--there-is-no-whitelisted-and-the-refusal-is-written-where-the-tiers-are)).
  It was a question about whether the feature is wanted rather than about whether the language could hold it —
  a predicate over a column is an ordinary operand now
  ([D-107](../decisions/round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded))
  — **and the need it was reached for is met by rows that already exist**, which §9 states.
- **Event answer retention — settled: nothing expires, and erasure empties rather than deletes** (§12).
  A dietary answer naming a condition *was* data of exactly the same class as what the person record holds,
  held under weaker rules and fresher; **the two rules now agree, so the asymmetry is gone rather than
  mitigated** ([D-140](../decisions/round-20.md#d-140--nothing-about-an-event-is-deleted-on-a-schedule-and-erasure-empties-an-answer-without-deleting-it),
  [EV-2](../open-questions.md#ev-2)).
- **Cancelled events and fees** (§10–11). Cancelling keeps the registrations; whether it
  releases the obligations, refunds them, or neither is the finance module's call.
- **Presence for minors and the safeguarding record — settled: it stays a column of the registration** (§9).
  No retention of its own, no permission of its own, no `presence_record` table, **and no safeguarding register
  behind any of it** ([D-147](../decisions/round-20.md#d-147--presence-stays-on-the-registration-no-clock-of-its-own-no-permission-of-its-own),
  [EV-4](../open-questions.md#ev-4)). [§7](07-events.md#7-the-people-connected-to-an-event)'s refusal of
  `PRESENT` is the surviving sharp edge, and it is the reason no permission of its own was needed: the column is
  a record of what happened, and not a set anybody is granted over.

---

*Decisions behind this page: D-023, D-040, D-043, D-044, D-059, D-061, D-064, D-065, D-067, D-070, D-074,
D-079, D-083, D-097, D-102, D-107, D-139, D-140, D-147, D-148.*
