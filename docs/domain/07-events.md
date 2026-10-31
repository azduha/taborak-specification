# Events

Camps, trips, hikes, and the occasional jamboree: things that happen on a date,
that people register for, and that somebody has to run.

An event is **an item** in the permission system: `grant_scope_type` carries a row for it, a grant may be
scoped to one event and mean that event alone
([D-006](../decisions/round-01a.md#d-006--per-item-permissions-are-capabilities-on-the-item)), and
**audiences** exist partly to express *"tell everyone about this event"*
([D-042](../decisions/round-02-03.md#d-042--grants-may-target-audiences-not-only-individuals)).
**Nothing owns an event**
([D-102](../decisions/round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)):
authority reaches one from a grant at the unit or a grant on it and from nowhere else, and the people
connected to it are named by **selectors that bind to the event being checked**.

Data model: [data-model/08-events.md](../data-model/08-events.md) and
[data-model/08a](../data-model/08a-event-guards-and-checks.md) (the bound selectors, the three queries,
the integrity checks).

**Section numbers are shared across the two parts** and never renumbered, because other pages cite them by number and their anchors are built from them: [07-events.md](07-events.md) holds §1–§7, [07a](07a-capacity-presence-and-forms.md) §8–§13 (capacity and the waitlist, presence, cancellation, payments, the forms, open issues).

---

## 1. What an event is, and what it is not

An event is **a thing with a date that people sign up for**.

> **A weekly meeting is not an event.** It is a **group** — a `person_group` whose dated
> member rows already say "this child takes part in this Thursday group"
> ([D-098](../decisions/round-10a.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority)).
> A Thursday group that meets forty times a year is already recorded, and making each
> meeting an event would create forty rows saying what one row says, with forty capacities,
> forty organizer rosters and forty chances to be wrong. Events are the things you
> *register* for: camps, trips, hikes, the summer jamboree.

The boundary has a cost, and it is worth knowing before asking the question. **"Was Jan at the meeting
on 14 March?" is not answerable from the events module.** That is presence tracking for a *standing
group*, which is a different feature; what is modelled here is presence at a *dated occasion*.

**There is no recurrence.** No `event_series`, no RFC 5545 rule, no occurrence table: a group that camps
four weekends a year has four events. Recurrence is what makes event tables complicated, and the one
thing that looked as though it needed it — meetings — is already modelled as a group.

---

## 2. Nothing owns an event

An event is **an item**, registered in `grant_scope_type` under the code `event`, like a
group or a role is. It has no owner. There is no column on `event` naming a person, a
group, or a unit, and nothing in the resolver tests one
([D-102](../decisions/round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)).

Two facts are the whole of how authority arrives:

| | |
|---|---|
| **A grant at the unit** | reaches **every event there is**, because after [D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row) there is no scope between the unit and an item, and no ownership relation to test |
| **A grant on one event** | reaches that event and nothing else |

**A joint camp is an event.** The second group's children reach it because a grant names them, exactly
like every other reader, and nobody has to arbitrate *"whose event is this?"* — the question has no
column to be asked of.

Creating one needs `event.create`, whose `applies_to` is `unit`: anybody holding it creates
an event, and nobody else does. Writing `event.create` **on** an event is refused when the
grant is saved, with the reason in the message — an event cannot be created twice, and a
creation permission attached to a thing that already exists answers no question
([D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)).

**The anti-pattern, named once.** An event does not belong to a unit, a group or a person:
`event.org_unit_id` is not in the schema, `can_event()` is not in the resolver, and there is no
unit-authority rule to reach across
([appendix/removed-concepts.md](../appendix/removed-concepts.md)). An event is one dated row, and the
question *"who may see this event?"* has one home, which is the grant table.

### Writing an event on one event

Because a unit-scope grant reaches everything, an item grant is for the narrow case, and the
two are not interchangeable. This is where the model refuses things at the save rather than
discovering them at the check:

| Written | Result |
|---|---|
| `event.edit` on one event | **Allowed.** A capability on the item — [D-006](../decisions/round-01a.md#d-006--per-item-permissions-are-capabilities-on-the-item) unchanged |
| `event.create` on one event | **Refused at save**, with the reason: `applies_to` is `unit` |
| `membership.terminate` on one event | **Refused at save**, for the same reason — a membership is a fact about a person at the unit, which no event owns |
| A grant naming `PLACED` at the unit | **Refused at save**, naming the operand — there is no item for it to bind to (§7) |

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

**Who counts as unanswered?** `(the people a live grant reaches on this event) MINUS (people
with a registration)`. The question "who hasn't replied yet?" is a subtraction, and it is
a query — [data-model/08a §9](../data-model/08a-event-guards-and-checks.md#9-the-three-queries-that-matter).
The reachable side is a set of people named by grants, which is what makes the subtraction a
query at all.

### The registration window

Registration is open inside a period and closed outside it, and the period is two columns on
the event — `registration_opens_at` and `registration_closes_at`.

`NULL` on the close means **until the event starts** — the unlimited case. `NULL` on the open
means the window opens as soon as the event is visible at all: appropriate for a hike, wrong
for a jamboree whose sign-up should not open before the dates
have been decided.

---

## 4. Who may register: capability, not a separate rule engine

Registering yourself requires **one permission: `event.register_self`, held on that event** —
either by an allow on the event itself, or by an allow at the unit, which after D-097
reaches the event along with every other item. Nothing else.

*Why there is no eligibility rule:* **the capability already is one.** A person holding
`event.register_self` on an event may register for it, and there is no second question behind that — no
age table, no prerequisite, no eligibility row, nothing evaluated outside `can()`
([D-060](../decisions/round-05.md#d-060--eligibility-is-capability-there-is-no-separate-rule-engine)).

**There is no level to compare.** `view`, `contribute`, `manage` and `admin` as ranks name nothing: a
grant allows or denies **one** code at one scope, and the answer to a check is *allowed* when some live
allow applies and no live deny applies
([D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)).
Four questions, four codes, each answered by its own row of `access_grant`:

| Question | Code |
|---|---|
| May they see it? | `event.view` |
| May they register for it? | `event.register_self` |
| May they run its roster? | `event.manage_participants` |
| May they mark the register? | `event.presence.mark` |

Two of those codes being held by one person is two rows, not a person who sits at some level — which is
what makes "what exactly does this person have on this camp?" a question with an answer.

**This is why audiences matter here.** Registering 200 children one at a time is 200 grant
rows — but opening the event to everybody who currently holds a membership is **one**: a
grant whose scope is that event, whose grantee is an audience whose expression is `MEMBERS`,
and whose effect is `allow`. That row is what [D-042](../decisions/round-02-03.md#d-042--grants-may-target-audiences-not-only-individuals)
was built for, and it is the normal way to run an open event. Per-person grants are for the exceptions.

### An age rule is an audience, not a rule

The obvious objection is a camp for 11–14 year-olds: how does a grant express "only
11-to-14s"? **A named set.** The organization keeps a group of the older section and opens the camp to
`GROUP(<that group>)`
([D-098](../decisions/round-10a.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority)).
An age-gated camp is a camp opened to a set whose members are that age.

**There is a second way to write that sentence, and it is the same kind of thing.**
`OLDER(n)` and `YOUNGER(n)` are seeded operands of the registry
([D-107](../decisions/round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)):
shipped rows of `selector_type`, alongside `MEMBERS`, whose predicate the resolver owns, read against
`person.birth_date` **on the date being checked** and composed by `+ - *` like every other operand. So the
camp for 11-to-14s is also writable as `(MEMBERS * OLDER(11)) - YOUNGER(15)` —
one grant, one expression, no roster to keep current. The group is still the better answer where
the section is a real group with a real roster behind it, because a maintained group says who
is in it and an age expression only says who qualifies; the two are not rivals and an
organization will use both.

**An age ceiling is writable, and it is not written.** `event.register_self` on this event, aimed at
`MEMBERS * YOUNGER(15)`, is an ordinary grant that stops a 9-year-old registering for a camp for
teenagers. Write no such grant and nothing in the system objects, because nothing in it could: an event
has no age ceiling of its own. **[D-070](../decisions/round-05.md#d-070--an-event-has-no-age-ceiling-the-grant-is-the-rule)
is therefore closed as a choice, not as a limit** — the organization keeps the judgement in the roster a
leader reads and in the attributed registration that records who let a child through. Read it as a
decision every time the next restriction is requested.

**There are no `min_age`/`max_age` columns on `event`, and there will not be some.**

*Why:* **a condition evaluated at registration time that the capability model does not know about is the
first rule-engine rule**, and the second is always cheaper than the first. Two years after that, the
answer to "who can register for this?" stops being readable from `access_grant`. A ceiling
written in a grant is readable there; a ceiling written on the event row is exactly the thing
that is not.

**What makes the residual risk survivable is three properties the schema already has.** The registration
is **attributable** — `source = 'staff'` with a named `created_by`, so the judgement belongs to somebody.
Age is **one join away** — `person.birth_date`, which the roster query in
[data-model/08a §9](../data-model/08a-event-guards-and-checks.md#9-the-three-queries-that-matter)
already selects, so any list a leader works from can carry it without a new column anywhere. And age is
**one operand away**, which is what makes the ceiling above a writing choice rather than a feature
request. The ordinary case — the age-bounded camp — is handled twice over: open the event to the set
whose members are that age, by a group somebody maintains or by the age operands themselves.

**A writer may not type `AGE >= 13`.** The clause to quote is that **an operand must be a named operand —
a row of the registry** — and this language has no comparison operator for `AGE >= 13` to be assembled out
of ([D-107](../decisions/round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)).
`OLDER(13)` *is* a set of people: the ones who are thirteen or older on the date being checked, in the
same way `MEMBERS` is the set of people who pass `is_current_member` and `ROLE(x)` is the set who hold
that office. Every operand in the registry is a test with a set behind it
([06a §6.2](06a-audiences-and-selectors.md#62-audiences--an-expression-over-named-sets)).

**Guardianship is deliberately not a selector, in either spelling** (`GUARDIANS` and `GUARDIANS(x)`)
([D-113](../decisions/round-13.md#d-113--the-guardianship-channel-has-no-expression-guardians-is-not-a-selector)):
*"True, GUARDIANS should not be selectable in the audience, guardians can perform ANY action (their
read/write perms grant) on behalf of the child."* A check about a child asks whether a live `guardianship`
row links the two people and reads `right_level ∈ none | view | write` off it — a lookup over a
relationship, not a set the language resolves — so an aimed-at-guardians operand would hand those people,
one code at a time, a subset of what the channel already gives them.

**The registry is organization-read-only**, so the next predicate anyone wants arrives as a deployment —
a shipped row with its evaluator arm beside it — and not as a setting. Either way every answer to
"who may register" keeps living in one table, which is the property worth defending.

---

## 5. Organizers are appointed, not granted

An event has a **set of organizers** — the people running it. That list is
`event_organizer`, and it is **the domain answer** to "who is running this?", labelled,
ordered, attributed.

> **An `event_organizer` row grants nothing.** `access_grant` remains what it is good at — showing a
> treasurer the books, opening the page to an audience, naming a parent who may register their child —
> and organizers are a separate concept: *who is running this*
> ([D-062](../decisions/round-05.md#d-062--organizers-are-appointed-on-the-event-not-granted)).
> **An operand is a set, not a grant**, so naming `ORGANIZERS` in an expression says who is in the
> set and confers nothing, in exactly the way that naming `ROLE(leaders)` or any audience has
> never conferred anything
> ([D-005](../decisions/round-01a.md#d-005--permissions-are-grants-never-derived-from-identity),
> [D-042](../decisions/round-02-03.md#d-042--grants-may-target-audiences-not-only-individuals)).

The consequence worth understanding: an organizer is an **appointment on the thing being
run**. It can carry a **label** (`'lead'`, `'cook'`, `'driver'`) and an order, and it is not a
permission bundle — it does not carry `event.edit`, it says who the organizers are. Like a role, an
organizer is a person named against something, and the codes that follow from it are the live grants that
aim at them ([D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)).

**Why the two do not drift.** The tempting design writes an `access_grant` whenever an
organizer is added, so "organizers" is just a query over grants. It fails on the label (a
grant has no room for "cook"), on the ordering, and on the reverse question — *"who is
running this camp?"* should not be answered by reading a permission table. Two concepts,
each doing its own job.

**What an organizer gets.** Membership of `event_organizer` makes a person a member of the
set `ORGANIZERS`. What that set may *do* is whatever a live grant aims at it, and **the act that creates
the event writes twelve of those grants in the same transaction as the event row** — one item-scope
`allow` per code whose `applies_to` admits an event, every one aimed at the bare operand `ORGANIZERS`,
the set derived rather than hand-picked
([D-151](../decisions/round-21.md#d-151--creating-an-event-writes-the-events-authority-and-its-organizers-may-grant-on-it);
[§12](07a-capacity-presence-and-forms.md#12-the-forms-questions-and-answers)).
One of the twelve is `event.grant_access`: an organizer hands access to the event they run **without
holding `access_grant.create` at the unit**, bounded by the scope they can name and by `applies_to`.
Everything outside those twelve reaches an organizer the way it reaches anybody else — through a grant
that person holds.

---

## 6. How authority reaches an event

**Through a grant, and through nothing else.** A grant at the unit reaches every event; a grant on one
event reaches that event (§2). The resolver matches scope exactly, so a check for `event.view` at
`('event', 42)` looks for a grant at **that exact scope**, and a person whose job is running the camp
succeeds there only because their grant sits at the unit — the widest scope there is, with nothing between
it and an item ([D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)).

**Nothing inherits, and nothing is bridged.** There is no `org_unit` scope to hold a role at, no owner
column for a check to read, and no wrapper adding a second `can()` call for events: `can_event()` is not
in the resolver, and the artifact-and-unit distinction it existed to draw has no pair left to distinguish
([D-102](../decisions/round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)).
The check is plain `can()`. What an organizer, an `ORGANIZERS` grant, and a unit-scope grant each mean is
in [§7](#7-the-people-connected-to-an-event) and in the table below.

**Nothing in the model reproduces "access was granted by the body itself".** With one unit there is no
body that chooses which named adult may reach its children, and no scope between the unit and the item for
such a choice to live at
([D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row); the same
loss, stated for a person's whole record, is at
[06 §2](06-authorization-model.md#2-scopes--the-unit-and-the-item)).

### Organizers still matter, and here is how

Membership of `event_organizer` is what makes someone an organizer **in the domain sense**:
the person on the list, with a label, whose name the parents see. Authority for *acting* on
the event comes from grants, as it does everywhere else:

| Who | How they may manage it |
|---|---|
| The person who runs the organization's camps | `event.manage_participants` **at the unit** — the grant reaches every event |
| Somebody trusted with one camp | the same code **on that event**, as an item grant |
| An organizer, as such | only what a grant aims at `ORGANIZERS` — the twelve the event's creation wrote, answer-view among them |
| Somebody the organization has excluded | a **deny** on the event or at the unit; deny is absolute and beats every allow ([D-013](../decisions/round-01a.md#d-013--explicit-deny-revoked-is-checked-before-everything)) |
| `system.admin` | Everything — the sole exception, as everywhere |

**The policy is stated positively and, where it must be, negatively.** Positively: a person holds what the
rows name, and there is no wider default to be exposed by and no narrow one to be trapped by. Negatively:
where holding something must be impossible, a **deny** says so, and deny is absolute
([D-013](../decisions/round-01a.md#d-013--explicit-deny-revoked-is-checked-before-everything)). A genuinely
private event is therefore an act — an item grant, plus a deny at the unit when the audience is broad
([§10](07a-capacity-presence-and-forms.md#10-cancellation-and-why-there-is-no-status-column)).

---

## 7. The people connected to an event

**Who is connected to this event?** There is no question about which *body* may read a roster: with one
unit and no exposure between bodies, the question has no subject
([§6](#6-how-authority-reaches-an-event)).

Five sets answer it, and each is a **selector that binds to the event being checked** —
written with no argument when the grant is written on an event:

| Operand | On the event being checked means | Explicit form |
|---|---|---|
| `ATTENDED` | said yes to this event | `ATTENDED(<event>)` |
| `PLACED` | said yes and is not waitlisted — **the capacity set** | `PLACED(<event>)` |
| `CONFIRMED` | holds a confirmed place | `CONFIRMED(<event>)` |
| `ON_WAITLIST` | is waiting for a place | `ON_WAITLIST(<event>)` |
| `ORGANIZERS` | runs this event | `ORGANIZERS(<event>)` |

The four attendance sets are not four ideas; each is a definition over two columns of
`event_registration`, and the definitions are stated with the columns in
[data-model/08a §8](../data-model/08a-event-guards-and-checks.md#selectors-that-bind-to-an-event). They are
ordered by containment rather than by rank — `CONFIRMED` ⊆ `PLACED`, `PLACED` and
`ON_WAITLIST` partition `ATTENDED`, and a person who declined is in none of them — and no
level or ladder is involved in any of them
([D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)).

**The bound form is the important half, and it kills a specific flaw.** `ATTENDED(<event
1204>)` written on event 1204 is one grant per event with the event's own id typed into it,
so "every participant may see the other participants" is a thing you do 400 times and forget
on the 401st. Bound, it is one expression written the same way every time. That is the whole
reason the argument-less form exists, and the two rules that make it safe are write-path
rules, stated as requirements in [data-model/08a §8](../data-model/08a-event-guards-and-checks.md#selectors-that-bind-to-an-event).

**`PRESENT(<event>)` is refused, and this is where presence tempts a reader.** The obvious
sixth operand is "the ones who actually turned up", computed over `was_present`
([§9](07a-capacity-presence-and-forms.md#9-presence-what-actually-happened)). It is
refused, and the reason is the failure direction: `was_present` is `NULL` until somebody
takes a register, so an operand built on it would revoke a child's access to their own camp
photos because a volunteer forgot to tick a box. `was_present` is three-valued *on purpose*
as a safeguarding signal — **keeping it out of the selector language is what keeps it
meaning "a person recorded this" rather than "this is who may see things"**, and
[D-067](../decisions/round-05.md#d-067--presence-is-a-three-valued-fact-on-the-registration)'s
reasoning for the third value is the reasoning for the refusal. **And this consequence is the
whole of the refusal**, which is worth saying out loud: `OLDER(n)` reads `person.birth_date`
([D-107](../decisions/round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)),
so nothing structural stops anybody writing `PRESENT` — there is only ever going to be this
argument standing in the way, and it holds on its own
([06a](06a-audiences-and-selectors.md#event-sets-and-the-two-sets-that-are-refused)).

**`WHITELISTED` does not exist, and is not a selector.** The nearest stored facts are
`source = 'staff'` (an organizer entered them) and promotion off the waitlist. Either the
word is to mean one of those or it names a new column on `event_registration`, which is an
events decision and not a selector decision — **and the events decision is now made: refused**
([D-148](../decisions/round-20.md#d-148--there-is-no-whitelisted-and-the-refusal-is-written-where-the-tiers-are)).
**Nothing here reserves the name**, and the refusal is written where the presence tiers are listed
([07a §9](07a-capacity-presence-and-forms.md#9-presence-what-actually-happened)) rather than being implied by a
word in a grammar.

### The screen must say which event it is talking about

The audience preview is a requirement rather than a nicety: *"the person saving the
grant is looking at one row that mentions no person at all"*, so the editor must **show the
expanded people** a grant reaches
([D-091](../decisions/round-09.md#d-091--a-permission-group-is-a-rule-and-a-list-at-once-and-a-rule-may-name-another-group)).

**The preview is computed for an item, and the screen says so.** `PLACED` means different
people on different events, so "who does this grant reach?" is not answerable from the grant
row alone — for a grant whose expression contains a bound operand, it is answerable
only as *"on event 1204, these 84 people"*, and the screen must name the event it computed
against rather than presenting the list as a property of the grant. The consequences are
requirements on the editor and on the read path, not on the schema:

- An expression containing a bound operand is previewed **per item**. Asking for a preview of
  such a grant at the unit is not a large computation, it is a refused one — the same refusal
  the save applies. **The per-item preview carries no cap, no cache and no background job,** on
  stated grounds: the system is specified against a few hundred people in the
  organization, a few dozen registrants on a typical event and a big camp on the order of two hundred,
  so previewing one item evaluates a couple of hundred predicates and nobody feels it
  ([D-112](../decisions/round-13.md#d-112--the-systems-scale-is-stated-hundreds-of-people-tens-of-registrants-per-event)).
  That size is **stated, not measured** — nothing in these documents has measured anything here — and the
  trigger for reopening it is a few thousand people, or a thousand registrants on one event. Nothing
  pre-pays this work: the preview computes it **on open**, still affordable, now with no fallback behind
  it ([D-114](../decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation)).
- Where no item is in hand, the editor says what the expression *means*, not who it reaches.
- **A compiled expression holds no item**, precisely because the item arrives as a parameter, so the item
  is bound at **resolution**: nothing expanded or resolved while checking one event may be served for
  another, and any cache of a *resolution* rather than of a compilation is keyed by the item or it is
  wrong. The reason is the one behind the bound form — the same grant on two events has two answers
  ([D-102](../decisions/round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it),
  [06 §8](06-authorization-model.md#8-there-is-no-permission-cache-and-what-replaces-it)).
- **A registration write is not a ruleset write**, and that is a statement about compilations, not about
  answers: `ruleset_version` is bumped by a write to `audience_operand` or `selector_type` alone, and a
  compilation holds no person and no item, so being outside that set buys a check nothing. Marking a
  register, confirming a place, flipping `is_confirmed` or promoting somebody off the waitlist moves
  `ATTENDED`, `PLACED`, `CONFIRMED` and `ON_WAITLIST`, and the new state is visible **on the next check**,
  because resolution is live and there is no answer stored anywhere to be behind the roster; `ORGANIZERS`,
  the fifth bound operand, moves on its own rows with the same immediacy
  ([D-114](../decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation)).
  **And the D-081 answer to "who enforces this": nobody enforces "a registration change must reach an
  answer", because there is nothing left to invalidate**
  ([D-081](../decisions/round-06.md#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now)) —
  the read path does it, and a read path cannot be forgotten.

Fail closed as everywhere else in the model, **with the direction stated rather than implied**:
an operand that resolves to nothing contributes the empty set, which *narrows* what a `+` or a
`*` reaches and *widens* what a `-` takes away — `EVERYONE - PERSON(x)` with a dead `x` denies
everybody, lockout and fail-closed being the same event
([D-106](../decisions/round-11-12.md#d-106--a-failed-operand-stays-the-empty-set-the-missing-half-was-a-report-not-a-refusal)).
A person with no birth date is not that kind of failure: the operand resolves perfectly well and
they are simply not in `OLDER(18)`, exactly as a person with no membership row is not in
`MEMBERS`. A broken leaf is not silent and still stops nothing — it is listed on the **tab on the
permissions page**, and no save is refused for it
([D-109](../decisions/round-13.md#d-109--nothing-a-rule-names-is-deleted-deprecated-hidden-disabled--and-a-tab-instead-of-a-report)).
**And that tab is nearly empty by construction, which is the point of the ruling: nothing a rule
names is ever deleted.** A retired office, group or audience is flagged `deprecated`, `hidden` or
`disabled` and keeps resolving — only `disabled` changes the answer, and it changes it to the empty set
because somebody asked for exactly that. The one thing still able to break a leaf is a person, because
[D-088](../decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)
lets a redaction require the row to actually go and erasure wins: **a redacted person is the corpus's only
remaining way to produce a broken leaf.**

**A preview is a statement about the day it was taken.** `OLDER(n)` and `YOUNGER(n)` make that
true of every age-bearing expression in the sharpest form there is: the 84 names on the screen
are the people who qualify *on that date*, and a birthday moves the list with no write and no edit to the
grant. Nothing is told about it and nothing needs to be: **there is nothing to be stale**, because every
check resolves against live rows and a birthday moves the answer at the instant it happens
([D-114](../decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation)).
What the preview is a statement about is **the date it was taken**, and that is a fact about the
calendar, not a lag to be closed.

**The preview is a workbench, not a record — and the record is the expression**
([D-110](../decisions/round-13.md#d-110--the-expression-is-the-record-of-whom-a-grant-reached)).
The audit row written when a grant is saved says *this person wrote these words, about this item, on this
date*. What the preview printed alongside it is logged as **a rendering on a date**, never as a statement
of who was in it: a stored list of everyone a rule happened to cover, kept after the rule was withdrawn,
is the roster table this corpus has deleted twice. So *"whom did this grant reach in May?"* is answered,
if at all, by evaluating the words against the data of May — and these documents do not promise the
answer. Words-only is affordable rather than brave only because of
[D-109](../decisions/round-13.md#d-109--nothing-a-rule-names-is-deleted-deprecated-hidden-disabled--and-a-tab-instead-of-a-report):
since nothing a rule names is deleted, the words keep resolving long after their reason is gone.
**What that concedes, so nobody finds it later:** a shared audience holds a word, not a copy, so **an edit
to a shared audience is a retrospective edit to every rule that names it**, and a re-evaluation for May
uses *today's* inner expression. The control is the preview
this very section is about — the editor prints the resolved set before an edit to a shared expression
saves, so the person editing sees at least once what they are changing backwards in time. And a preview
that cannot be computed still shows that it could not be computed, rather than an empty list.

---

*Decisions behind this page: D-005, D-006, D-013, D-042, D-060, D-062, D-067, D-070, D-081, D-088, D-091, D-097, D-098, D-099, D-100, D-102, D-106, D-107, D-109, D-110, D-112, D-113, D-114.*
