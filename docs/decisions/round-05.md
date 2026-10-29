# Decision Log — Refinement round 5 — the events module (D-058 … D-071)

> Events designed end to end, plus the withdrawal of per-resource `admin` permissions and of anything that forced an assignment to end.

[Refinement round 4 (D-047 … D-057) ←](round-04.md) | [All decisions](index.md) | [Refinement round 6 — the no-SQL round (D-072 … D-081) →](round-06.md)

---

## D-058 — An event is a dated occasion owned by exactly one unit

**Status:** decided (from your answer)
**Date:** refinement round 5

**Ownership reversed by [D-102](round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it); the dated-occasion half stands.** An event is still an occasion with
dates rather than a recurring template, and still has exactly one set of dates. There is simply no unit
for it to belong to, and the people connected to it are named by selectors that bind to it.

**Decision.** `event.org_unit_id` is `NOT NULL` — **exactly one owning unit.** A weekly
meeting group is **not** an event; it is `unit_participation`. Events are the things people
*register* for: camps, trips, hikes, jamborees.

**Why.** Two answers, and the second is the structural one.

- On ownership: *"One owning unit."* A joint camp between two packs is **Pack A's event that
  Pack B's children register for.** Pack B is a guest, and its access is written explicitly —
  an audience grant, a named person, at the level that fits. Nobody arbitrates "whose event
  is this?", and one unit remains the author of the record.
- On recurrence: *"No recurrence — meetings are participation."* A Thursday group meeting
  forty times a year is already recorded as "this child takes part in this Thursday group."
  Forty event rows would say what one participation row says, with forty capacities, forty
  organizer rosters, and forty chances to be wrong.

**The ownership rule is forced by [D-049](round-04.md#d-049--the-root-may-not-read-into-its-sub-units-scope_exposure-is-the-only-crossing),
not merely preferred by it.** If an event could belong to two units, the root's inability to
read a sub-unit's events would have an exception shaped exactly like a joint camp, with no
principled place to stop. One owner keeps the rule total.

**What this forecloses.** There is no `event_series`, no RFC 5545 rule, no occurrence table,
and no `event_unit` join table. Each would require every downstream table — registrations,
capacity, presence, organizers, questions — to carry a second possible home.

**Consequence worth stating.** "Was Jan at the meeting on 14 March?" is **not answerable from
the events module.** That is presence tracking for a standing group, which is a different
feature. The boundary is deliberate; the confusion between the two is the thing to watch for.

**See:** [../domain/07-events.md §1–2](../domain/07-events.md#1-what-an-event-is-and-what-it-is-not),
[../data-model/08-events.md §2](../data-model/08-events.md#2-event).

---

## D-059 — "Unanswered" is the absence of a row; a registration stores two values

**Status:** decided (from your answer)
**Date:** refinement round 5

**Decision.** `event_registration.response` has **two** values — `'attending'` and
`'not_attending'`. **`'unanswered'` is written nowhere.** It is the *absence* of a
registration row. "Who has not replied yet?" is a subtraction:
*(people who could contribute to this event) MINUS (people with a registration)*.

**Why.** Your answer: *"Absent row — two stored values."*

The framing that settled it was your own correction: registration is *"positive with
additional fields, or negative (or none)"*. **"None" is not a third stored value** — it is the
lack of a record, and storing it would mean writing rows for people who have not acted.

**Three reasons absence beats a stored value**, and the third is decisive:

| | Absent row | Stored `'unanswered'` |
|---|---|---|
| Rows written before anyone acts | None | One per person asked |
| "Asked and silent" vs "never asked" | Distinguishable — the eligible set is a query | Indistinguishable without an invite table |
| **"Who has not replied?"** | **A subtraction against an audience** | Requires enumerating the audience into rows |

The third is the real argument. The eligible set is an **audience** — a rule the resolver
evaluates ([D-042](round-02-03.md#d-042--grants-may-target-audiences-not-only-individuals)) such as
`unit:7:participants` or `all_members`. Enumerating it into `'unanswered'` rows would mean
re-enumerating every time a child joins the pack, and the stored rows would drift out of
agreement with the rule that generated them.

**Returning someone to unanswered removes the row** (`DELETE`, recorded in `audit_log`). That
is the honest act — it leaves the least behind, and "no row" then means the same thing
whether the person never answered or their answer was withdrawn.

**Consequence.** `unit_participation` uses the same reasoning for the same reason, and this
decision makes the pattern explicit: **where a state is the absence of a fact, store the
absence.** Compare [D-002](round-01a.md#d-002--everything-temporal-is-a-period-never-a-boolean) for the
temporal case and [D-053](round-04.md#d-053--a-role-is-valid-always-only-its-assignment-is-temporal)
for the definitional one.

**See:** [../data-model/08-events.md §4](../data-model/08-events.md#4-event_registration),
[../domain/07-events.md §3](../domain/07-events.md#3-registration-one-record-two-stored-answers-and-no-unanswered).

---

## D-060 — Eligibility is capability; there is no separate rule engine

**Status:** decided (from your answer)
**Date:** refinement round 5
**Resolves:** the deferral in [D-006](round-01a.md#d-006--per-item-permissions-are-capabilities-on-the-item)

**Decision.** Registration requires **`contribute` capability on that event.** Nothing else.
There is no eligibility rule table, no age gate, no prerequisite system. `event.register_self`
is already mapped to `contribute` in `permission_level`.

> **Amended by [D-107](round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)
> in round 12, in the direction of this entry's purpose rather than of its letter.** The words *"no age gate"*
> were doing two jobs in that paragraph. As **"the system applies no eligibility test of its own; there is no
> rule table; nothing is evaluated outside `can()`"** — they stand, and that is the decision this entry was
> recording. As **"nobody may write an age test in this model"** — they are now false, and were only ever true
> because of a sentence in [domain/06 §6](../domain/06-authorization-model.md) that round 12 deleted:
> *"an attribute is not a set of people … age is not."*
> `OLDER(n)` and `YOUNGER(n)` are seeded operands now, so `event.register_self` may be granted to
> `MEMBERS * YOUNGER(15)`, and the age ceiling this entry explicitly declined to enforce — the one
> [EV-1](../open-questions.md#ev-1--closed--there-is-no-age-ceiling-the-grant-is-the-rule) went on to record as
> unenforced — is **statable**. **What has not moved is who decides.** A gate is a grant somebody wrote, shown
> by the preview, attributed in the audit trail; it is not a conclusion the system draws from a birth date.
> This entry's real subject was always that, and it is why the entry is amended rather than superseded.

**Why.** Your answer: *"I feel like the people with 'contribute' permissions (capabilities) on
that item should be allowed to register."*

**This dissolves D-006's deferral rather than satisfying it.** D-006 said *"eligibility ...
will be a separate concept when events are specified."* Your answer says the separate concept
was never needed: **the capability ladder already is one.**

```
view        may SEE the event
contribute  may REGISTER for it
manage      may ORGANIZE it
admin       may control it
```

**Why audiences make this sufficient rather than merely simple.** Registering 200 children
individually is 200 grant rows — but opening an event to members is **one**, which the shape of the
row made visible at the time:

```sql
INSERT INTO access_grant (scope_type, scope_id, audience_id, level)
VALUES ('event', :camp_id,
        (SELECT id FROM audience WHERE code = 'all_members'), 'contribute');
```

*The requirement now, without the statement: an `access_grant` may address an **audience** instead of
a person, so "everyone who is a current member may take part in this event" is one row rather than
one per member — [05-authorization §8](../data-model/05a-audience-and-grammar.md#8-audience--grants-that-target-a-set-of-people).*

An age-gated camp is a camp opened to `unit:<id>:participants` for a unit whose participants
are that age. **This is the case audiences ([D-042](round-02-03.md#d-042--grants-may-target-audiences-not-only-individuals))
were built for**, and events are where the investment pays off.

**What this does not do, stated plainly.** *(Round 12: this paragraph describes a choice now, not a limitation
— `YOUNGER(n)` is seeded, so an organizer who wants a ceiling grants `event.register_self` to
`MEMBERS * YOUNGER(15)` and sees whom it reaches before saving. What still does not exist is a test the system
runs by itself. [D-107](round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded).)*
It does **not** enforce an age *ceiling* on an
open event. If a nine-year-old holds `contribute` on a camp for teenagers, they can register.
The design **decides eligibility by who may register, not by inspecting the person** — the
check *is* the grant. Whether that is sufficient is carried in
[../open-questions.md](../open-questions.md) rather than hidden.

**Organizers are not bound by it.** Anyone holding `event.manage_participants` may register
anyone, and the registration records `source = 'staff'`. That is the permission's purpose:
the leader who knows there is a spare bed is trusted, and the act is attributed.

**See:** [../domain/07-events.md §4](../domain/07-events.md#4-who-may-register-capability-not-a-separate-rule-engine),
[data-model/05 §7](../data-model/05-authorization.md#7-permission_level--deleted-by-d-099).

---

## D-061 — Event answers are read by that event's organizers

**Status:** decided (from your answer)
**Date:** refinement round 5

**Decision.** Answers to `event_question` are readable by **the organizers of that event**,
with no additional permission. You confirmed the consequence explicitly: **the event form is
the route by which a camp leader learns a child has a nut allergy.**

**Why, and the part that must be recorded.** This is only coherent — and only defensible —
because the `dependent.*` namespace is **unreachable by unit leaders**. The permission
catalog states it outright:

> *"Resolved **only** against `guardianship_permission`, never against roles. A unit leader
> does not get these by virtue of leading the unit — that is a safeguarding property."*

So a camp leader **cannot reach `dependent.medical.*` at all.** Not by leading the pack, not
by running the camp, not by being an organizer. There is no permission that changes it.
Which means an allergy recorded on a camp form is the *only* way the people running the camp
will know.

**This is a widening, and it is recorded as one.** Access to a child's health information
moves from *"few people, via a guardianship-scoped permission granted by the guardian"* to
*"every organizer of any event the child registers for."* That is a coherent position — the
parent tells the people present, per event, and the medical file stays closed — but it is
**not** an accident of where the gate was placed, and it must not be "fixed" later by
tightening the wrong thing.

**Two consequences that follow.**

1. **Only preference-level detail belongs on a form.** Nothing in the schema distinguishes
   "vegetarian" from "coeliac" — both are `data_type = 'text'` in `event_answer.value`. The
   discipline is in the form *label*, so it is guidance, not a constraint. A `CHECK` cannot
   tell them apart, and a keyword list would fail on the first unusual phrasing.
2. **Event answers are not a medical record.** They are operational detail for one event,
   read by that event's organizers, and ending with the event. The two stores are not
   duplicates of each other and should not be merged or synchronised.

**Open:** the retention policy. A dietary answer citing a medical condition is health data
with a retention obligation, and there is no policy yet.

**See:** [../data-model/08-events.md §7](../data-model/08-events.md#7-event_question-and-event_answer),
[../domain/07-events.md §12](../domain/07a-capacity-presence-and-forms.md#12-the-forms-questions-and-answers),
[appendix/permission-catalog.md §9](../appendix/permission-catalog.md#9-there-is-no-dependent-namespace).

---

## D-062 — Organizers are appointed on the event, not granted

**Status:** decided (from your answer)
**Date:** refinement round 5

**Decision.** Events have an `event_organizer` roster, and it is **the domain answer** to
"who is running this?" — labelled, ordered, attributed. It is **not** an `access_grant`, and
it does not by itself confer authority to act on the event.

**Why.** Your answer: *"Roster only; grants stay separate."*

**The tempting alternative, and why it fails.** Write an `access_grant` at `manage` whenever
an organizer is added, so "the organizers" is a query over grants and the two can never
disagree. It fails on three counts:

| | Grant at `manage` | `event_organizer` |
|---|---|---|
| A cook's label | No room for `organizer_role = 'cook'` | `organizer_role`, free text |
| Display order | Not expressible | `sort_order`, `is_primary` |
| "Who is running this camp?" | Read the permission table | Read the roster |
| Removing the cook | Revokes their ability to *see* the event | Removes them from the list |

That last row is the practical one: "they are no longer cooking" does not mean "they may no
longer see the camp."

**`event_organizer` is the event-scoped analogue of `position_assignment`** — an appointment
on the thing being run. Like a position it may carry a label and an order; like a position it
is not a permission bundle. `organizer_role` is **free text, not a CHECK**: every
organization labels these differently, and a controlled vocabulary here would be a guess of
the kind [D-054](round-04.md#d-054--the-sub-unit-vocabulary-is-not-seeded-the-organization-defines-its-own-types)
removed for unit types.

**It has no `valid_to`, deliberately.** A roster is not a period: you are on the list or you
are not. An organizer who drops out is removed (audited), because "was Jan an organizer of
that camp?" must have one answer, not a set of intervals.

**How authority actually reaches an organizer** is [D-063](#d-063--an-event-is-an-artifact-of-its-unit-not-a-child-of-it) —
the unit's roles reach its events.

**See:** [../data-model/08-events.md §3](../data-model/08-events.md#3-event_organizer),
[../domain/07-events.md §5](../domain/07-events.md#5-organizers-are-appointed-not-granted).

---

## D-063 — An event is an ARTIFACT of its unit, not a child of it

**Status:** decided (from your answer, as a consequence you did not have to state)
**Date:** refinement round 5

**Superseded by [D-102](round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it).** The argument's shape survives — an item's people are *named*, never
inherited from a container — but with no unit and no owner the question 'whose event is this?' has no
column left to answer it from.

**Amends:** nothing. **Extends:** [D-031](round-02-03.md#d-031--no-downward-inheritance-of-authority-scope_exposure-is-the-only-crossing)

**The problem.** The resolver matches scope **exactly**. There is therefore no path from a
`unit_leader` role held at `('org_unit', 7)` to a check made at `('event', 42)` — even when
unit 7 owns event 42:

```
unit_leader ── holds role at ──► org_unit 7 (the pack)
                                     │
                                     │  ✗ NO PATH
                                     ▼
event 42 "Summer camp" ◄─ owned by ──┘    resolver checks scope exactly
```

The pack's leader — the person whose *job* is running the pack's camp — does not pass
`can(leader, 'event.view', 'event', 42)`. Nothing is broken; the answer is simply no. But the
module cannot ship with that gap, because it would mean the leader must be granted every
event their own unit creates.

**Decision.** A permission is satisfied at `('event', E)` if it is satisfied at **the event's
owning unit**, `('org_unit', E.org_unit_id)`, *and* that unit is the event's owner. One
wrapper function, `can_event()`, calling `can()` twice.

**Why this is not inheritance downward, and why that distinction is the whole point.**

| | Inheritance (rejected, D-015/D-031) | Artifact rule (chosen) |
|---|---|---|
| What a leader gains | Authority in the unit's **sub-units** too | Authority over the unit's **own events** |
| Blast radius | Grows on every restructure | Fixed — one owner, pinned by D-049 |
| Reverses | **D-015, D-031** | Nothing |

**An event is not a child of its unit; it is a thing the unit made.** The unit's authority
already covers the unit. Asking "may this person do this in Pack 7?" is asking the right
question about the right scope — and it is a question the resolver already answers correctly.

Restructuring the hierarchy still changes nothing about who may do what. Adding a sub-unit
still grants nobody anything. **D-015 and D-031 stand untouched**, and the rule is exactly as
narrow as the case requires.

**Why a wrapper function rather than a change inside `can()`.** Putting this clause inside
the resolver would make every permission check — on people, memberships, units, fees —
evaluate an event-shaped rule. Keeping it in `can_event()` means the exception is visible,
named, and confined to the module that needs it.

**And it is a two-way door.** `can_event()` calls `can()` twice and adds no authority of its
own; nothing is written to `access_grant` to make it work. If the organization decides that
leaders should *not* automatically run every event their unit creates, **deleting the second
`can()` call is the entire change, and it needs no data migration.**

**The root is unaffected.** An organization-scoped `registrar` still cannot see a pack's camp
— events are precisely the sub-unit records [D-049](round-04.md#d-049--the-root-may-not-read-into-its-sub-units-scope_exposure-is-the-only-crossing)
protects. The fix, if the root wants it, is one `scope_exposure` row naming one assignment.

**See:** [../domain/07-events.md §6](../domain/07-events.md#6-how-authority-reaches-an-event),
[../data-model/08-events.md §8](../data-model/08a-event-guards-and-checks.md#8-projections-and-guards).

---

## D-064 — There is no event status; visibility is the permission model

**Status:** decided (from your answer)
**Date:** refinement round 5

**Decision.** `event` has **no `status` column.** Draft is not a state: a new event has no
grants beyond its organizers' own authority, so nobody else can see it, and **publishing is
an `access_grant`, not an `UPDATE`.** `completed` is derived (`ends_at < now()`).
Cancellation is a recorded fact — `cancelled_at`, `cancelled_by`, `cancel_reason`.

**Why.** Your answer, which is the right instinct: *"Isn't the draft solved by not giving
anyone else permissions, but the organizer?"* It is, and it is better than a status enum for
a reason worth stating:

> **A status column and a permission system that both claim to answer "who may see this?"
> will eventually disagree — and the one that gets enforced is whoever wrote the last `IF`.**

With no status column there is nothing to disagree. The questions a `draft` flag would answer
are all answered by grants:

| Question | Answer |
|---|---|
| "Is this ready to be seen?" | Has anyone been granted `view`? |
| "Who can see it before it is announced?" | Its organizers, and anyone already granted |
| "How do I hide it again?" | Revoke the grant — `revoked_at` set, the row kept |

**Where the logic deliberately diverges: cancellation.** If cancelling were done by revoking
grants, **the event would vanish for exactly the people who need to know it is off** — the
registrants. They would see nothing at all: not "cancelled", just gone. So cancellation is a
fact, the event stays visible, and it is marked.

Draft and cancellation therefore use *different mechanisms on purpose*, because they have
different audiences: draft is about who may **discover** an event, cancellation is about who
must be **told**.

**A cancelled event** stops accepting registrations (the window closes implicitly) and
**keeps every registration row** — those rows are the record that the camp was planned and
who was coming, which is precisely what is needed to notify and refund.

**See:** [../domain/07-events.md §10](../domain/07a-capacity-presence-and-forms.md#10-cancellation-and-why-there-is-no-status-column),
[../data-model/08-events.md §2](../data-model/08-events.md#2-event).

---

## D-065 — Capacity is a waitlist threshold, and organizers may exceed it

**Status:** decided (from your answer)
**Date:** refinement round 5

**Decision.** Registering for a full event **succeeds and produces a waitlisted row** — it is
never refused. Organizers may register past capacity outright, and the overrun is
**permitted, attributed and reported** rather than prevented. Promotion from the waitlist is
a deliberate act by an organizer, never automatic.

**Why.** Two answers, and they only look contradictory:

- *"Waitlist"* — the thirteenth caller for a twelve-bed camp is not turned away, they are
  written down.
- *"Organizers might exceed, also they might choose to include people from the waiting
  list"* — a leader who knows there are two spare tents should not be blocked by a number
  they cannot edit mid-camp.

**The two coexist because the waitlist is a SELF-SERVICE outcome.** The trigger applies it
only when `source = 'self'`. A staff registration is admitted regardless. So:

| Path | At a full event |
|---|---|
| Self-service | Waitlisted, ordered |
| Staff / organizer | **Admitted**, the overrun reported |
| Promotion | Deliberate — an organizer picks who comes off the waitlist |
| Capacity change | An `UPDATE` — visible and attributed |

**Capacity is therefore three things at once, on purpose:** a rule for self-service, a number
organizers can exceed, and a report. [data-model/08 §10 check 5](../data-model/01-identity.md#10-integrity-checks)
produces rows and **that is not a failure** — an event that overruns every year has a wrong
capacity number, and the fix is the number, not refusing people.

**Promotion is not automatic** because a place freeing up is not the same as it being right
to give it to the next person — the organizer may know the next child cannot come on those
dates. What *is* automatic is one narrow release rule, recorded as such in
[D-066](#d-066--payment-confirms-the-place-and-the-release-deadline-is-the-one-automatic-transition).

**See:** [../data-model/08-events.md §5](../data-model/08-events.md#5-capacity-and-the-waitlist),
[../domain/07-events.md §8](../domain/07a-capacity-presence-and-forms.md#8-capacity-and-the-waitlist).

---

## D-066 — Payment confirms the place, and the release deadline is the one automatic transition

**Status:** decided (from your answer)
**Date:** refinement round 5

**Decision.** An event may have a fee (`event.fee_schedule_id`), and **payment confirms the
place**. Registering creates a `fee_obligation`; a paid obligation sets
`is_confirmed = true` via `confirm_event_place()`. **Events without a fee confirm
immediately, and most events have no fee** — you were explicit that payment *"does not have
to be at all events."*

**Why.** Your answer: *"Payment confirms the place, also the payment does not have to be at
all events."*

The second half is the part that shapes the schema: `fee_schedule_id` is **nullable**, and
`NULL` is the common case. A free hike confirms on registration, and there is no
"confirmation" state with no meaning.

**The accepted cost, recorded rather than hidden.** This design has spent real effort
avoiding automatic state changes ([D-023](round-01b.md#d-023--nothing-is-auto-lapsed-or-auto-terminated),
[D-040](round-02-03.md#d-040--the-fee-expires-yearly-a-date-tracked-renewal-window-replaces-a-grace-status)),
and payment-confirms-the-place reintroduces one: an unpaid registration at a full event
**releases its place to the waitlist** at `waitlist_deadline`. It is accepted because it is a
**deadline, not a sweep** — narrowly scoped, opt-in per event, and visible in what it
produces. The predicate as decided:

```sql
-- Only at a full event, only with a fee configured, only past the deadline,
-- only unpaid, only self-service, never a cancelled event.
e.fee_schedule_id IS NOT NULL
AND e.waitlist_deadline IS NOT NULL
AND e.waitlist_deadline < now()
AND r.source = 'self' AND r.is_confirmed = false
AND e.cancelled_at IS NULL
```

*The requirement now, in words: release happens **only** at a full event that has a fee, a deadline
that has passed, an unpaid self-service registration, and is not cancelled — six conditions, each of
which is load-bearing, and the list is the rule rather than an illustration of it. Stated in
[08-events §5](../data-model/08-events.md#when-an-unpaid-registration-releases-its-place).*

`waitlist_deadline` is `NULL` by default, so **an event that does not opt in never runs this
rule at all.** The alternative — no deadline — means a place is held forever by someone who
never paid, which is worse.

**A function, not a trigger.** `confirm_event_place()` is called by the finance module and is
**not** a trigger on `fee_obligation.status`, because a trigger would fire for membership
fees and event fees alike and "the fee is paid" means something different in each case: a
membership *activates* (D-040), an event place *confirms*. Two transitions, two owners.

**See:** [../data-model/08-events.md §6](../data-model/08-events.md#6-payments-and-confirmation),
[../domain/07-events.md §11](../domain/07a-capacity-presence-and-forms.md#11-payments-on-events).

---

## D-067 — Presence is a three-valued fact on the registration

**Status:** decided (from your answer)
**Date:** refinement round 5

**Decision.** `event_registration.was_present` is a **nullable boolean**, marked by an
organizer with `presence_marked_by` / `presence_marked_at`.

| Value | Meaning |
|---|---|
| `NULL` | Not yet marked — no register was taken |
| `true` | Turned up |
| `false` | Marked absent — a register was taken and they were not there |

**Why three-valued rather than a boolean defaulting to false.** *"We did not take a
register"* and *"we took a register and they were not there"* are **different facts**, and
only the second is a safeguarding signal. A boolean defaulting to `false` would assert
absence where the organization only failed to look.

**Why it matters more than it looks.** For a camp, the end-of-week presence record **is the
record of who was actually in the organization's care.** That is the row that matters if the
fee buys insurance (finance question 9 — *"member on the date of the incident"*), and it is
the row that cannot be reconstructed afterwards from registrations.

**Presence is not registration**, and the distinction is enforced: a `not_attending`
registration with `was_present` set is contradictory and reported
([data-model/08 §10 check 8](../data-model/01-identity.md#10-integrity-checks)).

**A walk-in is not representable, deliberately.** A sibling who turns up on the day was not
in the organization's care — no guardian recorded, no name on the roster — and must not
*silently appear* to have been. Recording them means registering them, which means the
organizers have a name and a guardian. That is the correct friction.

**Note the contrast with D-059.** There, absence of a row was the right encoding for
*unanswered*. Here, a stored `NULL` is the right encoding for *not marked*. The difference:
"unanswered" is the absence of a **fact about the person**, while "not marked" is a fact
about the **organization's incomplete work** — and the work being incomplete is itself worth
recording, because it is a task still outstanding.

**See:** [../data-model/08-events.md §4](../data-model/08-events.md#4-event_registration),
[../domain/07-events.md §9](../domain/07a-capacity-presence-and-forms.md#9-presence-what-actually-happened).

---

## D-068 — There are no per-resource `admin` permissions; roles are the bundle

**Status:** decided (from your answer) — **reverses [D-007](round-01a.md#d-007--every-resource-has-an-admin-level-that-subsumes-narrower-ones--reversed)**
**Date:** refinement round 5

**Your answer.** Asked whether `person.admin` should subsume `person.merge` and
`person.redact` — the standing case against prefix subsumption, since both are irreversible
and both are privacy incidents if granted wrongly — you answered: *"Only the system should
have admin permissions, not the individual items."*

The phrase needed disambiguating, because *"individual items"* names two different things in
this schema: the per-resource permission (`person.admin`, over the whole resource) and the
item-scoped grant (`access_grant` over one event). You confirmed the first reading.

**Decision.** The **sixteen** `<resource>.admin` permission codes are **deleted** — the ten
documented ones (`person.admin`, `account.admin`, `membership.admin`,
`unit_participation.admin`, `org_unit.admin`, `position.admin`, `guardianship.admin`,
`audit.admin`, `event.admin`, `audience.admin`) and the six sitting in deferred namespaces
(`document`, `fee`, `payment`, `report`, `consent`, `message`). So is the resolver's
prefix-match branch. What remains:

- **`system.admin`** is the only permission in the system that means *everything*, and it is
  reached only through a role assignment (`system` namespace — never an item grant, never
  guardianship). Unchanged.
- **"Someone who can do everything about events"** is a **role** the organization composes,
  bundling the thirteen `event.*` codes. Not a permission the code invents for them.
- **`access_level.admin` (rank 40) is untouched.** This is a different thing that shares a
  name, and the collision is the most likely place for a later reader to go wrong. The level
  answers *"how much authority does this grant carry"* — `view` < `contribute` < `manage` <
  `admin`, used by `permission_level` to decide whether a `contribute`-level grant satisfies
  `event.register_self`. The permission code answered *"does this capability imply that one"*.
  The ladder survives; only the wildcard code dies.

**Why this is coherent with the rest of the design rather than an exception to it.** D-052
already settled that **roles are runtime data and the seed set is not a specification** — the
organization composes permission groups at runtime. A per-resource `admin` code is the code
composing a permission group *on the organization's behalf*, in advance, for a bundle nobody
asked for. Deleting it makes the two mechanisms agree: **the code implements capabilities,
the organization groups them.** It is the same division D-055 drew when it refused to prune
the catalog — a large menu of narrow things, composed by whoever needs them.

**The cost is real, and it is the cost D-007 existed to prevent.** Stated in D-007's own
words: without the wildcard, *every new narrow permission requires updating every role that
should already have implied it — and someone will miss one, producing a permission that
silently is not granted.* That failure mode is back. It is accepted because it fails
**closed**: someone cannot do a thing they were arguably meant to be able to do, and they say
so, rather than doing a thing nobody meant them to be able to do. D-007 traded a loud
inconvenience for a quiet hazard. The reversal takes the opposite side of the same trade.

**What replaces the protection** — since the wildcard is gone, reachability needs a check of
its own. **Integrity check 18** lists permissions that **no role grants**, which is the query
that surfaces a permission silently orphaned by the absence of a wildcard (numbering follows
the existing list in [../data-model/05 §11](../data-model/05d-invariants-and-seed.md#11-invariants-to-verify).
It was written as an executable query, and this is it as decided:

```sql
-- 18. ORPHANED PERMISSIONS — granted by no role at all. With no .admin wildcard
--     (D-068), a new permission nobody bundles is silently unusable. This report is
--     the safety net the wildcard used to be.
SELECT p.code, p.resource
  FROM permission p
 WHERE p.is_assignable
   AND NOT EXISTS (SELECT 1 FROM role_permission rp WHERE rp.permission_id = p.id)
 ORDER BY p.resource, p.code;
```

*The requirement now: **every assignable permission that no role bundles is reported**, which is the
net the `.admin` wildcard used to be; the check is item 18 of
[05-authorization §11](../data-model/05d-invariants-and-seed.md#11-invariants-to-verify), and like the other
eighteen it is now something to be verified rather than something that runs.*

**What happens to the F-4 question that prompted this.** It does not dissolve — it **moves,
and becomes visible.** A role bundling all eleven `person.*` permissions still reaches
`person.merge` and `person.redact`, because those are ordinary codes in the bundle. The
difference is where the decision lives: previously a *resolver rule* made the implication,
invisible in every role editor and true for every resource whether or not anyone wanted it.
Now the implication appears **as the contents of a role the organization wrote**, reviewable
line by line in `role_permission`, dated, and alarmable. `role.edit` on that role is already
audited for exactly this reason (D-052). **The guidance therefore moves from the schema to
the seed:** a role bundling a resource *including* its irreversible codes should be named for
what it is, and the seed roles in §11 are written so that no seeded role mixes
`person.merge`/`person.redact` with routine `person.edit`. That is now expressible as a
report rather than a caveat.

**Two survivors, and why neither is an exception.** Both look like wildcards and neither is
the thing being deleted:

- **`dependent.admin` stays.** It is **not** a prefix-match artefact — it is a code a staff
  member *chooses and stores*, one row in `guardianship_permission`, granting the full set for
  one child. A wildcard that must be deliberately written is what this decision endorses, not
  what it removes. It also has a property no role wildcard can have: an explicit
  `is_granted = false` row **overrides** it, so a court-ordered restriction survives a broad
  grant. Deleting `dependent.admin` would make the common restriction *easier* to express, not
  harder — listing nineteen narrow rows per child where a court case needs two. **The
  distinction to keep: `person.admin` implied capabilities nobody wrote down;
  `dependent.admin` is a shorthand for capabilities somebody did write down, in a specific
  row, about a specific child.**
- **`system.admin` stays**, for the reasons already in §7 — it is the break-glass capability,
  concentrating the most dangerous thing in one alarmable holder rather than scattering
  equivalents. It was never a prefix-match beneficiary; it is checked outright.

**A third thing called "admin", which also stays.** `dependent.profile.admin`,
`dependent.medical.admin`, `dependent.consent.admin` are **not** wildcards at all — they are
*actions* meaning "edit" inside a sub-resource, paired against `.view`. Nothing is implied by
them. Three unrelated meanings now share one word in this schema — the access **level**
(rank 40), the deleted resource **wildcard**, and an **edit** action — and any of the three
may be what a reader means. When one of them comes up in conversation, say which.

**Migration.** Deleting `role_permission` rows for the sixteen codes; no other data moves.
Any role that held only `person.admin` becomes an empty role, which is *correct* and visible
rather than quietly over-privileged — and `role.delete` still refuses to remove a role that
was ever assigned (D-052), so the empty shell survives as evidence of what someone once
meant. Re-deriving it means naming the bundle, which is the point.

**Two-way door?** No. Re-adding a wildcard later is mechanically cheap and semantically loud
— it re-creates the implication silently for resources added after the day you added it.
Treat it as a fresh decision, not a revert.

**See:** [../appendix/permission-catalog.md §1](../appendix/permission-catalog.md#1-conventions),
[../data-model/05-authorization.md §2](../data-model/05-authorization.md#2-permission),
[../domain/06-authorization-model.md §4](../domain/06-authorization-model.md#4-roles-are-offices-groups-are-company).

---

## D-069 — Guardianship ends when a person ends it; the system takes no position on majority

**Status:** decided (from your answer) — **reverses [D-024](round-01b.md#d-024--guardianship-does-not-auto-expire-at-majority--reversed)**
**Date:** refinement round 5

**Your answer.** Asked what the system does when a guarded child turns 18 — review queue,
auto-expire, or nothing — you answered **"Nothing at all."**

**Decision.** No job, no review queue, no computed candidate date, no flag. A guardianship
row is ended by a person ending it (`guardianship.end`), or by import, and the system does
not notice birthdays in this connection at all.

**Why this is better than the queue D-024 proposed, and where D-024 went wrong.** D-024
reasoned from *"fail open rather than silently strip access"* and picked the gentler of two
automatic behaviours. **Both were automatic.** The queue was not a refusal to act; it was a
deferral of the action, and it smuggled in a claim the system cannot support: that majority
is a date the system knows. It is not. D-024's own rationale said thresholds vary by
jurisdiction — and then computed a date anyway. A review queue is not a neutral container for
a wrong date; it is a worklist of cases staff are told to decide, and the item on it asserts
something the organization has not decided.

**The deeper problem with the queue: it inverts who decides.** Under D-024 the system raises
the question at 18 whether or not anyone wanted it asked, in every case, for every family —
including the ones where the adult child asks their parent to keep handling their medical
correspondence. The queue's default is that the arrangement is suspect. That is the wrong
default for a relationship the organization did not create.

**What "nothing" costs, stated honestly.** Nothing is tracked, so **"who is still listed as my
guardian, and since when?" has no automatic answer.** It has a manual one: `guardianship`
carries `valid_from`/`valid_to`, so the question is a query on a person's rows and the answer
includes the date each was ended. What is lost is a *prompt*, not a *record* — which is the
same trade the module makes everywhere. See the pattern below.

**This is the latest in a consistent line of refusals, and the reasoning is identical each
time.** Across five rounds the design has allowed itself exactly two automatic transitions —
the yearly fee sweep (D-040) and the event waitlist release (D-066) — and has refused, among
others, automatic membership lapse states (D-023), event status (D-064), and recurrence
(D-058). Guardianship expiry is the next one refused. The pattern: **an automatic transition is cheap to design and expensive to defend, because it
acts on every case including the ones it was not designed for.** A nightly job that ends
guardianships at 18 fails closed and strips a legally valid arrangement overnight; a queue
fails open and adds a standing assertion the org never made. The third option — a person who
knows the family ends the row — is the only one that can also decide *not* to.

**Consequence to carry: nothing here weakens the exit path, so the exit path must exist.**
With no automatic end, `guardianship.end` is the only door, and it must be reachable by
someone. Two things follow, both worth stating because they are now load-bearing in a way they
were not when a job existed to help:

1. **The adult child must be able to end it about themselves.** They are the subject of the
   row and currently hold no permission over it — they are not a guardian of themselves. This
   needs a route, and it is now the module's sharpest open item.
2. **A stale row is invisible by design**, so the query, not the job, is the control. A
   periodic human review is a good idea and is explicitly *not* a scheduled system behaviour.

**Follow-up raised: E-2 is closed and replaced by E-5** — *"how does an adult end a guardianship
over themselves?"* That question existed before this decision and was masked by a review queue
that would have surfaced it. It is now unavoidable.

**See:** [../data-model/04-relationships.md §2](../data-model/04-relationships.md#2-the-guardians-right-none-view-or-write),
[../domain/02-actors.md §5](../domain/02-actors.md#5-acting-on-behalf).

---

## D-070 — An event has no age ceiling; the grant is the rule

**Status:** decided (from your answer)
**Date:** refinement round 5

**Your answer.** Asked about the one gap in *eligibility is capability*
([D-060](#d-060--eligibility-is-capability-there-is-no-separate-rule-engine)) — an event
opened to `all_members` can be registered for by a nine-year-old even if the camp was planned
for teenagers — you answered **"Leave it — the grant is the rule."**

**Decision.** No `min_age`/`max_age` on `event`. No age check in `place_event_registration()`.
Age restriction is expressed **entirely** by choosing the audience the event is opened to.

**Why the option was tempting, and why refusing it is right.** The offered design was the
cheap one: a column pair plus one branch, **reported** rather than blocking, matching
`position.min_age`. It would have cost little and reversed nothing. It is refused on
consistency grounds, which are the only grounds worth having here. A condition evaluated at
registration time that the capability model does not know about is **the first rule-engine
rule**. Not because age is special — because the moment one exists, the second is cheap, and
within two years the honest answer to "who can register for this?" is "check the grants, and
also the age columns, and also whatever else we added there." D-060 dissolved a deferred
question by noticing the capability model already answered it; a condition living beside it
reopens the question by insisting the capability model is not enough.

**The residual risk, stated rather than waved away.** A leader registers a child for an event
the child is too young for, and **nothing in the system objects.** Accepted, on three
conditions that are all already true in the schema:

1. **It is attributable.** Staff-driven registrations carry `source = 'staff'` and a
   `created_by`, so the judgement is recorded as belonging to a named person.
2. **It is visible.** §9's roster query lists registrants with birth dates, so age is on the
   page a leader looks at while confirming.
3. **It is the normal case correctly handled already.** A genuinely age-bounded event is
   opened to the unit whose members are that age, and that is how a section-based organization
   works today. What is *not* covered is one narrow shape — an event open to everyone that
   should be restricted — and it is narrow enough that a column pair would be a permanent
   mechanism serving an exception.

**If it is ever revisited,** the trigger is specific: the shape recurring often enough that
leaders routinely open the wrong event to the wrong people. Then the right answer is probably
still not columns on `event` but **an audience that encodes the age band** — `all_members` is
a rule the resolver evaluates, and so could `members_aged_13_plus` be. That keeps eligibility
in one place, which is the property being protected here. **Do not reach for a condition on
the row when the mechanism for evaluating membership of a set already exists.**

**See:** [../domain/07-events.md §4](../domain/07-events.md#4-who-may-register-capability-not-a-separate-rule-engine),
[../data-model/08-events.md §9](../data-model/08a-event-guards-and-checks.md#9-the-three-queries-that-matter).

---

## D-071 — Nothing forces a role assignment to end; the gate and the report are the control

**Status:** decided (from your answer) — **overrides the recommendation in F-3**
**Date:** refinement round 5

**Your answer.** Asked whether `valid_to` should be mandatory on high-authority role
assignments — the classic *volunteer who was never removed* — you answered **"Nothing — rely
on the gate."**

**The docs had recommended the other way.** F-3 said *yes, at the application layer*, and
argued the membership gate made an open-ended assignment more dangerous, not less. You
disagree, and the disagreement is worth recording because the recommendation was not
obviously wrong.

**Decision.** `role_assignment.valid_to` stays nullable with no application-layer requirement
and no per-role policy. The controls are the **membership gate**
([D-039](round-02-03.md#d-039--member-permissions-require-a-current-paid-membership)) and a **report**. No
new constraint anywhere.

**Why the recommendation was wrong, in one place.** F-3 said the gate makes open-ended
assignments *more* dangerous. It is the other way round: **the gate already does what an
expiry date would do, for exactly the population an expiry date would target, and it does it
without inventing a date nobody chose.** A forced `valid_to` is an guess about when authority
should lapse, written by whoever made the assignment — usually inherited from a form default.
The gate instead ties expiry to a fact the organization already maintains and renews on
purpose: whether this person is a member. When the fee lapses, gated roles stop granting. The
expiry date was always going to be a worse approximation of that.

**What the gate does not cover — the honest residue.** `unit_leader` and `assistant_leader`
have `requires_membership = false` by explicit decision (a volunteer whose own fee lapses
still runs the Thursday meeting), so a lapsed leader keeps leading. Also any role held by a
non-member, and anything carrying `system.gate_exempt`. For those, the answer is a **periodic
human review over open-ended assignments**, and D-068 now makes that query sharper, since a
role's full reach is visible in `role_permission` with no wildcard hiding implications in the
resolver.

**Note the dependency this decision creates.** D-053 put *all* the weight on
`role_assignment.valid_to` as the only thing that ends authority, and warned that the
open-ended assignment is the classic access failure. **This decision declines to add a guard
rail at precisely that point**, so the two together should be read as one load-bearing pair:
authority ends only when somebody ends it, and the only defence left is that somebody looks.
The report is not a nice-to-have here; it is the entire control.

**See:** [../data-model/05-authorization.md §4](../data-model/05-authorization.md#4-role_holder--who-holds-an-office),
[../open-questions.md F-3](../open-questions.md#f-3--closed--nothing-forces-an-assignment-to-end).

---
