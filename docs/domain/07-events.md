# Events

Camps, trips, hikes, and the occasional district jamboree: things that happen on a date,
that people register for, and that somebody has to run.

This module was the one the whole authorization model was built toward. `access_grant`
shipped with `scope_type = 'event'` from the first draft
([D-006](../decisions/decision-log.md#d-006--per-item-permissions-are-capabilities-on-the-item)),
`grant_scope_type` has carried a placeholder row for it since, and **audiences**
([D-042](../decisions/decision-log.md#d-042--grants-may-target-audiences-not-only-individuals))
exist partly to express *"tell everyone about this event."* Those hooks are now filled in.

Domain model: [data-model/08-events.md](../data-model/08-events.md).

---

## 1. What an event is, and what it is not

An event is **a thing with a date that people sign up for**.

> **A weekly meeting is not an event.** It is `unit_participation`. A Thursday group that
> meets forty times a year is already recorded — "this child takes part in this Thursday
> group" — and making each meeting an event would create forty rows saying what one row
> says, with forty capacities, forty organizer rosters and forty chances to be wrong. Events
> are the things you *register* for: camps, trips, hikes, the summer jamboree.

This is a genuine boundary and worth stating plainly, because the two are easy to confuse
and the confusion has a cost. If someone wants to know "was Jan at the meeting on 14 March?",
the answer is not in the events module. That is presence tracking for a *standing group*,
which is a different feature; what is modelled here is presence at a *dated occasion*.

The consequence: **there is no recurrence.** No `event_series`, no RFC 5545 rule, no
occurrence table. A pack that camps four weekends a year has four events. This was
considered and rejected in favour of the boundary above — recurrence is what makes event
tables complicated, and the thing that needed it (meetings) is already modelled elsewhere.

---

## 2. An event belongs to one unit

`event.org_unit_id` is `NOT NULL`. Every event has exactly one owning unit, and for
anything a pack runs, that is the pack.

A joint camp between two packs is **Pack A's event that Pack B's children register for.**
Pack B is a guest, and its access is written explicitly — an audience grant, or a named
person, at the level that fits. Nobody has to arbitrate "whose event is this?", and one
unit remains the author of the record.

This is forced by
[D-049](../decisions/decision-log.md#d-049--the-root-may-not-read-into-its-sub-units-scope_exposure-is-the-only-crossing),
not merely preferred by it. If an event could belong to two units, then the root's inability
to read a sub-unit's events would have an exception shaped exactly like a joint camp, and
there is no principled place to stop. One owner keeps the rule total.

**The root may not read a pack's events.** This is the rule the whole no-inheritance design
exists to produce, and events are where it is most visible: an organization-scoped
`registrar` cannot see a camp's roster. That is not a bug to be reported — see
[§7](#7-what-the-root-can-and-cannot-see).

---

## 3. Registration: one record, two stored answers, and no "unanswered"

A person's relationship to an event is captured in **one row** — `event_registration`.

| What you asked for | How it is stored |
|---|---|
| attending | `response = 'attending'` |
| not attending | `response = 'not_attending'` |
| *unanswered* | **no row at all** |

> **"Unanswered" is not a value, and that is deliberate.** It is the *absence* of a
> registration. Writing a row that says "this person has not answered" means writing rows
> for people who have not acted, which then have to be cleaned up when the event ends and
> which cannot distinguish "asked and silent" from "never asked" without a third table.

Returning someone to unanswered means **removing the row** (`DELETE`, recorded in
`audit_log`) — which is the honest act, and the one that leaves the least behind.

**Who counts as unanswered?** `(people who could contribute to this event) MINUS (people
with a registration)`. The question "who hasn't replied yet?" is a subtraction, and it is a
query — [data-model/08 §9](../data-model/08-events.md#9-the-three-queries-that-matter).

### The registration window

Registration is open inside a period and closed outside it:

```sql
event.registration_opens_at  TIMESTAMPTZ   -- NULL = as soon as the event is visible
event.registration_closes_at TIMESTAMPTZ   -- NULL = when the event starts
```

`NULL` on the close means **until the event starts**, which is the "unlimited" case you
described. `NULL` on the open means immediately — appropriate for a hike, wrong for a
jamboree whose sign-up should not open before the committee has decided the dates.

---

## 4. Who may register: capability, not a separate rule engine

Registration requires **`contribute` capability on that event.** Nothing else.

This is the answer to the question [D-006](../decisions/decision-log.md#d-006--per-item-permissions-are-capabilities-on-the-item)
left open. D-006 said *"eligibility ... will be a separate concept when events are
specified."* Your answer was that people with `contribute` on the item should be able to
register — and that turns out to **dissolve** the deferral rather than satisfy it: there is
no separate eligibility concept, because the capability ladder already is one.

```
view        may SEE the event           ─┐
contribute  may REGISTER for it          │  one grant on the event
manage      may ORGANIZE it              │  decides all three
admin       may control it               ─┘
```

The rows are already in `permission_level`
([data-model/05 §7](../data-model/05-authorization.md#7-permission_level--connecting-permissions-to-grant-levels)):

| permission | scope_type | required_level |
|---|---|---|
| `event.view` | event | `view` |
| `event.register_self` | event | `contribute` |
| `event.manage_participants` | event | `manage` |
| `event.grant_access` | event | `admin` |

**This is why audiences matter here.** Registering 200 children one at a time is 200 grant
rows — but opening the event to members is **one**:

```sql
-- "any current member may register for this camp"
INSERT INTO access_grant (scope_type, scope_id, audience_id, level)
VALUES ('event', :camp_id,
        (SELECT id FROM audience WHERE code = 'all_members'), 'contribute');
```

That single row is what D-042 was built for, and it is the normal way to run an open event.
Per-person grants are for the exceptions.

### An age rule is an audience, not a rule

The obvious objection is a camp for 11–14 year-olds. How does `contribute` express "only
11-to-14s"? **The built-in audiences.** `unit:<id>:participants` is a rule the resolver
evaluates, so an event for the older section is opened to that section's participants and
nothing else. An age-gated camp is a camp open to a unit whose participants are that age.

**What this does not do:** it does not enforce an age *ceiling* on a registration for an
open event. If a 9-year-old holds `contribute` on a camp for teenagers, they can register.
Whether that is acceptable is [§11](../data-model/08-events.md#11-open-issues) — the honest
statement is that this design **decides eligibility by who may register, not by checking the
person**, and the check is the grant.

---

## 5. Organizers are appointed, not granted

An event has a **set of organizers** — the people running it. That list is
`event_organizer`, and it is **the authority**, checked directly.

> **Organizers are not `access_grant`s at `manage` level.** This was the explicit choice.
> `access_grant` remains what it is good at — showing a treasurer the books, opening the
> page to an audience, naming a parent who may register their child — and organizers are a
> separate concept: *who is running this*.

The consequence worth understanding: an organizer is an **appointment on the thing being
run**, which makes `event_organizer` the event-scoped analogue of `position_assignment`
([data-model/02 §7](../data-model/02-organization.md#7-position-and-position_assignment)). Like a
position, it can carry a **label** (`'lead'`, `'cook'`, `'driver'`) and an order. Like a
position, it is not a permission bundle — it does not grant `event.edit`; it says who the
organizers are, and the event permissions say what organizers may do.

**Why the two do not drift.** The tempting design writes an `access_grant` whenever an
organizer is added, so "organizers" is just a query over grants. It fails on the label (a
grant has no room for "cook"), on the ordering, and on the reverse question — *"who is
running this camp?"* should not be answered by reading a permission table. Two concepts,
each doing its own job.

**What an organizer gets.** Membership of `event_organizer` is **one input** to the resolver,
not a bypass of it. See [§6](#6-the-hinge-organizers-and-the-scope-mismatch), which is the
part of this module that needed a real decision.

---

## 6. The hinge: organizers and the scope mismatch

This is the structural problem the module had to solve, and it is worth stating in full
because it is easy to "fix" wrongly later.

**The resolver matches scope exactly** ([D-031](../decisions/decision-log.md#d-031--no-downward-inheritance-of-authority-scope_exposure-is-the-only-crossing),
[data-model/05 §10](../data-model/05-authorization.md#10-the-resolver-in-sql)). A check for
`event.view` at `('event', 42)` looks for a grant or role at **that exact scope**. A
`unit_leader` role is at `('org_unit', 7)`.

```
unit_leader  ── holds role at ──►  org_unit 7  (the pack)
                                       │
                                       │  ✗ NO PATH
                                       ▼
event 42 "Summer camp"  ◄── owned by ──┘     resolver checks scope exactly
```

So the pack's leader — a person whose *job* is running the pack's camp — **does not pass
`can(leader, 'event.view', 'event', 42)`.** Nothing is broken; the answer is simply no.

**The three ways out, and why two are rejected:**

| Option | Why not |
|---|---|
| Give the leader an `access_grant` at `manage` on every event | Correct but fragile: a grant per event per leader, and it must be written by someone who thought of it |
| Let authority inherit from the unit down to the unit's events | **This is D-031/D-015, and it is reversed.** Events are precisely the "own records of a sub-unit" the whole rule protects |
| **Let the event's own owning unit supply authority** | Chosen |

**The chosen rule, stated precisely:**

> A person satisfies a permission checked at `('event', E)` if the permission would be
> satisfied at **the event's owning unit** — `('org_unit', E.org_unit_id)` — *and* the event
> is **owned by that same unit**.

This is **not** inheritance downward through the hierarchy. It is not inheritance at all.
It is the recognition that **an event is not a child of its unit; it is an artifact of it.**
The unit's authority already covers the unit; the event is a thing the unit made, and asking
"may this person do this in Pack 7?" is asking the right question about the right scope.

The distinction that makes this safe:

| | Inheritance (rejected) | Artifact rule (chosen) |
|---|---|---|
| What it would let a leader do | Act in the pack's **sub-units** too | Act on the pack's **own events** |
| Blast radius | Grows when the hierarchy is restructured | Fixed — the event's owner is one unit |
| Reverses | D-015, D-031 | Nothing |

Restructuring the hierarchy still changes nothing about who may do what. Adding a sub-unit
still grants nobody anything. The rule is exactly as narrow as it needs to be, and no
narrower.

**And it is a two-way door.** If the organization later decides that a leader should not
automatically run every event their unit creates — that events should be opt-in even for
leaders — the rule is one clause in the resolver, and turning it off makes organizers
`access_grant`-based without touching a single row of data.

### Organizers still matter, and here is how

Membership of `event_organizer` is what makes someone an organizer **in the domain sense**:
the person on the list, with a label, whose name the parents see. Authority for *acting* on
the event comes from the owning unit's roles, from an explicit grant, or from
`system.admin` — normal, resolvable authority.

Concretely, for the pack's camp:

| Who | How they may manage it |
|---|---|
| Pack leader | `unit_leader` role at the pack → §6 rule → `manage` |
| Assistant leader | `assistant_leader` role at the pack → same |
| A parent who volunteered to cook | **An explicit `access_grant` at `manage`**, or a role — because no role of theirs reaches the pack's events |
| The root's treasurer | **Nothing.** Not without the pack exposing its scope (D-049) |
| `system_admin` | Everything — the sole exception, as everywhere |

That second-to-last row is the whole no-inheritance policy in one line, and it is correct.

---

## 7. What the root can and cannot see

Following directly from [D-049](../decisions/decision-log.md#d-049--the-root-may-not-read-into-its-sub-units-scope_exposure-is-the-only-crossing):

| Question | Answer | Why |
|---|---|---|
| "How many members do we have?" | **Yes** | The root owns the membership registry |
| "What fees are outstanding?" | **Yes** | The root owns the fee data |
| "What camps did the packs run in 2019?" | **Only if each pack exposed its scope** | Events belong to the sub-unit |
| "Who is coming to Pack B's camp?" | **No** | Same |

> **A `registrar` holding `event.view` at organization scope cannot read a pack's camp.** It
> reads the organization's own events — which is to say, almost none. Scope is an exact
> match. This will look like a bug and is not one; the fix, if the organization genuinely
> wants it, is the pack writing one `scope_exposure` row naming one assignment, which is a
> deliberate, dated, revocable act. Forty of those is forty deliberate acts, and that is the
> auditability, not the drudgery.

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
there are two spare tents should not be blocked by a number they cannot edit mid-camp. The
overrun is permitted, attributed, and **reported**
([data-model/08 §10](../data-model/08-events.md#10-integrity-checks)): an event running over
its stated capacity is a fact the organization can see, not a state it cannot reach.

So capacity is three things at once, and all three are intentional:

| | Behaviour |
|---|---|
| Self-registration when full | **Waitlisted** — never refused, never admitted |
| Organizer registration when full | **Admitted**, the overrun reported |
| Any capacity change | An `UPDATE`, visible and attributed |

---

## 9. Presence: what actually happened

The registration says what someone *said*. Presence says what *happened*.

`event_registration.was_present` is a **nullable boolean**:
`NULL` = not yet marked, `true` = turned up, `false` = marked absent. The three-valued
column is not sloppiness — it distinguishes *"we did not take a register"* from *"we took a
register and they were not there"*, which are different facts and only one of them is a
safeguarding signal.

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

---

## 10. Cancellation, and why there is no `status` column

**There is no lifecycle status.** An event is a row with dates, a unit, and a set of grants.

**Visibility *is* the permission model.** A newly created event has no grants beyond its
organizers' own authority, so nobody else can see it. Publishing is not a state change — it
is **granting** someone access: an audience, a group, a unit. This is your answer, and it is
better than a `status` enum for the usual reason: a status column and a permission system
that both claim to say "who may see this" will eventually disagree, and the one that gets
enforced is whoever wrote the last `IF`.

So the questions that a `draft` status would answer are answered by grants:

| Question | Answer |
|---|---|
| "Is this ready to be seen?" | Has anyone been granted `view`? |
| "Who can see it before it is announced?" | Its organizers, and anyone already granted |
| "How do I hide it again?" | Revoke the grant — `revoked_at` set, row kept |

**Cancellation is a fact, not a status** — and this is where the logic diverges, because the
audience is different:

```sql
event.cancelled_at    TIMESTAMPTZ
event.cancelled_by    BIGINT REFERENCES person(id)
event.cancel_reason   TEXT
```

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
arm of `fee_obligation`'s target CHECK, restored after
[D-057](../decisions/decision-log.md#d-057--household-is-removed) removed the household arm,
and this time it is a *real* arm with data behind it rather than a dormant hedge.

**The `is_confirmed` / deadline interaction is the one automatic transition in this module**,
and it is worth flagging as such: the design has spent effort avoiding automatic state
changes ([D-023](../decisions/decision-log.md#d-023--nothing-is-auto-lapsed-or-auto-terminated),
[D-040](../decisions/decision-log.md#d-040--the-fee-expires-yearly-a-date-tracked-renewal-window-replaces-a-grace-status)),
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
[D-044](../decisions/decision-log.md#d-044--nothing-gates-a-membership-request-except-identity-and-payment),
and it earns its keep only when the same question must mean the same thing across events.
Tent preference does not: what one camp asks and what another needs are allowed to differ,
and per-event definitions keep them from having to agree.

### Health data, and the widening this represents

You confirmed that **event answers are readable by that event's organizers, with no extra
gate.** Two consequences follow, and the second is the significant one.

**1. Only preference-level detail belongs on a form.** A dietary *preference* ("vegetarian",
"no pork") is an operational note for the cook. A *condition* ("coeliac", "nut allergy") is
medical data, and nothing in the schema distinguishes them — the difference is what the
organizer types into a label. So the discipline is in the form design, not the constraint:
[data-model/08 §7](../data-model/08-events.md#7-event_question-and-event_answer) states it,
and it is guidance, not enforcement.

**2. This is the route by which a leader learns a child has a nut allergy, and that is a
deliberate widening.** The `dependent.*` namespace resolves **only** against
`guardianship_permission` — never against roles or grants
([appendix/permission-catalog.md §9](../appendix/permission-catalog.md#9-the-dependent-namespace)):

> *"A unit leader does not get these by virtue of leading the unit — that is a safeguarding
> property."*

So a camp leader **cannot reach `dependent.medical.*` at all.** Not by leading the pack, not
by running the camp, not by being an organizer. There is no permission that changes it.

Which means: an allergy recorded on a camp form is **the only way the people running the camp
will know**. That is a coherent and defensible position — *the parent tells the people
present, per event, and the medical file stays closed* — but it is a widening from "few
people, via a guardianship-scoped permission" to "every organizer of any event the child
registers for", and it is recorded as such in
[D-061](../decisions/decision-log.md#d-061--event-answers-are-read-by-that-events-organizers),
with the reasoning, so that nobody later "fixes" the apparent duplication between the two
stores by tightening this one.

**Event answers are not a medical record.** They are operational detail for one event, they
are read by that event's organizers, and they end with the event. See
[§11](../data-model/08-events.md#11-open-issues) for the retention question, which is open.

---

## 13. Open issues

Moved to [../open-questions.md](../open-questions.md) under **G. Events**, where they are
tracked with the rest. The ones this module raises:

- **The age ceiling on an open event** (§4). Eligibility is decided by who may register; a
  `contribute` grant does not check the person's age. Whether that is enough.
- **Event answer retention** (§12). Answers end with the event — but a dietary answer citing
  a medical condition is health data with a retention obligation, and there is no policy yet.
- **Cancelled events and fees** (§10–11). Cancelling keeps the registrations; whether it
  releases the obligations, refunds them, or neither is the finance module's call.
- **Presence for minors and the safeguarding record** (§9). `was_present` is the "who was in
  our care" record. Whether it needs its own retention or its own permission is unresolved.
- **Whether organizers should be an `access_grant` after all** (§5–6). The rule in §6 makes
  the unit's roles reach its events; if the organization would rather organizers be
  opt-in per event, that is one clause to change.
