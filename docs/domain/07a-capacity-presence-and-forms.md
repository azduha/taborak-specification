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
([data-model/08 §10](../data-model/01-identity.md#10-integrity-checks)): an event running over
its stated capacity is a fact the organization can see, not a state it cannot reach.

The mechanism of *how* an organizer gets past the number is unchanged by round 10 and was
never the resolver: the waitlist fires only for `source = 'self'`, and a registration written
by a person holding `event.register_other` arrives as `source = 'staff'` and is admitted.
What changed is where that permission came from — before, the owning unit supplied it; now it
is a grant at the unit or on the event, like every other code
([D-102](../decisions/round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)).

So capacity is three things at once, and all three are intentional:

| | Behaviour |
|---|---|
| Self-registration when full | **Waitlisted** — never refused, never admitted |
| A staff registration when full | **Admitted**, the overrun reported |
| Any capacity change | An `UPDATE`, visible and attributed |

The set capacity is compared against has a name now: it is **`PLACED`**, the attending
non-waitlisted registrations of an event (§7) — the same set `PLACED` selects and the same
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
of who was actually in the organization's care. That is the row that matters if the fee buys
insurance (finance question 9: *"member on the date of the incident"*), and it is the row
that cannot be reconstructed afterwards from registrations. It is also why the column is
marked by an organizer and recorded with who marked it and when.

**Presence is not registration.** A child who registered and did not come is a registration
with `was_present = false`. A child who turned up without registering — a sibling along for
the day — is not representable, deliberately: that child was not in the organization's care
and must not silently appear to have been. Recording them means registering them, which
means they have a guardian and the organizers have a name.

**And presence is not an audience.** The temptation to build `PRESENT(<event>)` on this
column — to let "everyone who came" be a set a grant names — is refused, and §7 states why:
the column is `NULL` until somebody takes a register, so an operand over it makes access
depend on a volunteer's diligence, and it would turn a safeguarding record into an access
control. Attendance for the purposes of a grant stops at `ATTENDED`, `PLACED`, `CONFIRMED`
and `ON_WAITLIST`.

---

## 10. Cancellation, and why there is no `status` column

**There is no lifecycle status.** An event is a row with dates and a set of grants.

**Visibility *is* the permission model.** A newly created event has no grants of its own, so
whoever can see it can see it because of a grant they already hold — normally an
`event.view` at the unit, which reaches every event and therefore every new one the moment it
is created. Publishing is not a state change — it is **granting** someone access: an audience,
a group, a role. This is your answer, and it is
better than a `status` enum for the usual reason: a status column and a permission system
that both claim to say "who may see this" will eventually disagree, and the one that gets
enforced is whoever wrote the last `IF`.

That has a consequence worth saying out loud, because it is the opposite of the old
behaviour. ~~A newly created event has no grants beyond its organizers' own authority, so
nobody else can see it~~ — under
[D-064](../decisions/round-05.md#d-064--there-is-no-event-status-visibility-is-the-permission-model)
a draft reached exactly one audience: the owning unit's own people, whom
[D-063](../decisions/round-05.md#d-063--an-event-is-an-artifact-of-its-unit-not-a-child-of-it)'s
rule carried across to it, and nobody else. After D-102 there is **no such narrow default**: a
person holding `event.view` at the unit sees a half-typed event the instant it is committed,
and there is no narrower scope a grant could have sat at instead. A genuinely private event is
therefore an *act* — an item grant, plus a deny at the unit if the audience is broad — rather
than the absence of one. D-064's reasoning about the two-writer problem is untouched; what
moved is which side of the pair the default sits on.

So the questions that a `draft` status would answer are answered by grants:

| Question | Answer |
|---|---|
| "Is this ready to be seen?" | Has anyone been granted `event.view` beyond the unit-scope holders? |
| "Who can see it before it is announced?" | Whoever a live allow names — including every unit-scope holder |
| "How do I hide it again?" | Revoke the grant — `revoked_at` set, row kept — or write a deny |

**Cancellation is a fact, not a status** — and this is where the logic diverges, because the
audience is different:

Three columns carry it: `cancelled_at` says when, `cancelled_by` says who — a person, so the
decision has a name attached to it — and `cancel_reason` says why.

> **Cancelling by revoking grants would hide the cancellation from exactly the people who
> need it.** The registrants are the ones who must be told the camp is off; if the event is
> hidden by revoking their `view`, they see nothing at all — not "cancelled", just gone.
> So cancellation is recorded, and the event stays visible, marked.

A cancelled event **stops accepting registrations** (the registration window closes
implicitly) and **keeps every existing row**: those registrations are the record that the
camp was planned and who was coming. That record is exactly what is needed afterwards — to
notify people, and to refund them.

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

The only new schema here is a **pointer**: `fee_obligation.event_registration_id`. It is one
arm of `fee_obligation`'s exactly-one rule, restored after
[D-057](../decisions/round-04.md#d-057--household-is-removed) removed the household arm,
and this time it is a *real* arm with data behind it rather than a dormant hedge.

**The `is_confirmed` / deadline interaction is the one automatic transition in this module**,
and it is worth flagging as such: the design has spent effort avoiding automatic state
changes ([D-023](../decisions/round-01b.md#d-023--nothing-is-auto-lapsed-or-auto-terminated),
[D-040](../decisions/round-02-03.md#d-040--the-fee-expires-yearly-a-date-tracked-renewal-window-replaces-a-grace-status)),
and payment-confirms-the-place reintroduces one. It is a *deadline*, not a sweep: it applies
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

**Reusable question libraries were considered and rejected.** A shared pool of question
definitions is structurally the requirement machinery removed in
[D-044](../decisions/round-02-03.md#d-044--nothing-gates-a-membership-request-except-identity-and-payment),
and it earns its keep only when the same question must mean the same thing across events.
Tent preference does not: what one camp asks and what another needs are allowed to differ,
and per-event definitions keep them from having to agree.

### Health data, and the widening this represents

You confirmed that **event answers are readable by that event's organizers, with no extra
gate** ([D-061](../decisions/round-05.md#d-061--event-answers-are-read-by-that-events-organizers)),
and round 10 changed only *where that sentence is written down*. It is no longer prose inside
the resolver; it is **a seeded grant** — `event.answer.view` on an event, aimed at
`ORGANIZERS`
([D-102](../decisions/round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)).
Two things follow, and neither weakens D-061:

- **"No extra gate" is now literally true and visible.** The seeded grant *is* the whole
  mechanism; there is no clause special-casing organizers. Anyone who wants to see who may
  read an event's answers reads a grant row.
- **The reach of that grant is per-event, which D-061 always asserted and round 10 makes
  checkable.** `ORGANIZERS` with no argument binds to the event the grant sits on, so the
  seeded row cannot accidentally name the organizers of every camp at once.

Two consequences of D-061 follow, and the second is the significant one.

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
[appendix/permission-catalog.md §9](../appendix/permission-catalog.md#9-there-is-no-dependent-namespace)).
The namespace that used to spell this out is deleted, the safeguarding property it carried is not:

> *"A person does not get these by virtue of leading — that is a safeguarding
> property."*

**Corrected in round 7, because this sentence was doing work it could no longer do.** It used to read
*"so a camp leader cannot reach a child's medical record at all"* — and after
[D-083](../decisions/round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)
there is no medical record to be unreachable, so the sentence is not merely out of date, it describes a
guarantee the model never had once the category disappeared. What is actually true, in the two forms
that matter:

- **No role gets it by leading.** The starting role set gives a leadership role its rosters and
  its events — and **no read over a person's data**
  ([permission-catalog §11](../appendix/permission-catalog.md#11-roles--proposed-seed-set)). That
  is the safeguarding property, exactly as before: leadership is not guardianship, and the
  guardianship channel answers only for the person its row names.
- **It is now one grant away, and round 10 widened what "one grant" means.** Whoever holds
  `person.view` **at the unit** reads every child's whole record, allergy list included — and
  after [D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)
  a grant at the unit has no narrower reading available, because the unit is the only scope
  there is. Nothing in the resolver will stop that and nothing should — but a document that
  promised it was impossible would have been trusted, and a promise the model does not make is
  worse than none.

**The widening in the next paragraph is therefore unchanged in substance and better stated: the
protection is a decision about a role, revisitable by whoever administers roles, not a wall."

Which means: under the starting roles, an allergy recorded on a camp form is **the only way the people
running the camp will know**. That is a coherent and defensible configuration — *the parent tells the
people present, per event, and nobody outside the family holds the fact* — but it is a widening from "few
people, via a guardianship-scoped permission" to "every organizer of any event the child
registers for", and it is recorded as such in
[D-061](../decisions/round-05.md#d-061--event-answers-are-read-by-that-events-organizers),
with the reasoning, so that nobody later "fixes" the apparent duplication between the two
stores by tightening this one.

**Event answers are not the person's record.** They are operational detail for one event, read by that
event's organizers, and they end with the event — while the same fact, recorded on the person, is
audited, curable and erased with them. **[D-083](../decisions/round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)
made those two copies the same class of data**, which is what turns the retention question below into
a real one, and [AT-1](../open-questions.md#at-1--should-an-event-question-bind-to-an-attribute-code)
into the alternative: collect the fact once, confirm it at the door. See
[§11](../data-model/08a-event-guards-and-checks.md#11-open-issues) for the retention question, which is open.

---

## 13. Open issues

Moved to [../open-questions.md](../open-questions.md) under **G. Events**, where they are
tracked with the rest. The ones this module raises:

- ~~**The age ceiling on an open event**~~ — **settled: accepted as a risk**, the grant is
  the rule, and closing it later would mean a new operand rather than a column (§4,
  [D-070](../decisions/round-05.md#d-070--an-event-has-no-age-ceiling-the-grant-is-the-rule)).
  **That prediction has come true and it changes the shape of the answer, not the answer:** the
  operand arrived as `YOUNGER(n)`, so an age ceiling is writable today as
  `event.register_self` aimed at `MEMBERS * YOUNGER(15)`. **EV-1 stays closed, now as a choice
  the organization renews rather than a limit it inherits** — nobody has to be told the ceiling
  cannot be stated, only whether it should be (§4,
  [D-107](../decisions/round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)).
- **What else should be seeded to `ORGANIZERS`.** D-102 seeds exactly one grant,
  `event.answer.view`. Everything else an organizer needs — editing the event, working the
  roster — now reaches them only through a unit-scope or item grant they happen to hold, and
  no decision says whether that is the intended shape or an oversight (§5, §6). This module
  does not seed more of its own accord.
- **Whether a bound selector makes its audience single-scope.** An audience whose expression
  names `PLACED` cannot be aimed at a unit-scope grant, so a shared audience row can stop
  being reusable across scopes. The refusal lands on the grant, which is faithful to the rule
  as written; whether the editor should warn at the audience instead is unsettled (§7).
- **`WHITELISTED`.** No stored state to name it, so it is not a selector (§7) — a question about
  whether the feature is wanted, and not one about whether the language could hold it: a
  predicate over a column is an ordinary operand now
  ([D-107](../decisions/round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)).
- **Event answer retention** (§12). Answers end with the event — but a dietary answer naming a
  condition is data of exactly the same class as what the person record holds, held under weaker rules
  and fresher. No policy yet; see
  [EV-2](../open-questions.md#ev-2--retention-of-event_answer).
- **Cancelled events and fees** (§10–11). Cancelling keeps the registrations; whether it
  releases the obligations, refunds them, or neither is the finance module's call.
- **Presence for minors and the safeguarding record** (§9). `was_present` is the "who was in
  our care" record. Whether it needs its own retention or its own permission is unresolved —
  and §7's refusal of `PRESENT` is the sharp edge of why that matters.
