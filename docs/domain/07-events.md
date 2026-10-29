# Events

Camps, trips, hikes, and the occasional jamboree: things that happen on a date,
that people register for, and that somebody has to run.

This module was the one the whole authorization model was built toward. `access_grant`
shipped with `scope_type = 'event'` from the first draft
([D-006](../decisions/round-01a.md#d-006--per-item-permissions-are-capabilities-on-the-item)),
`grant_scope_type` has carried a row for it since, and **audiences**
([D-042](../decisions/round-02-03.md#d-042--grants-may-target-audiences-not-only-individuals))
exist partly to express *"tell everyone about this event."* Those hooks are now filled in.

Round 10 changed what they hook into. **Nothing owns an event**
([D-102](../decisions/round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)),
so every sentence this module used to write about the unit that runs an event is now a
sentence about a grant at the unit, or about a **selector that binds to the event being
checked**. The reasoning behind the sentences is kept below, marked withdrawn, because the
problem each one solved is still a problem; only its answer moved.

Domain model: [data-model/08-events.md](../data-model/08-events.md).


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

This is a genuine boundary and worth stating plainly, because the two are easy to confuse
and the confusion has a cost. If someone wants to know "was Jan at the meeting on 14 March?",
the answer is not in the events module. That is presence tracking for a *standing group*,
which is a different feature; what is modelled here is presence at a *dated occasion*.

The consequence: **there is no recurrence.** No `event_series`, no RFC 5545 rule, no
occurrence table. A group that camps four weekends a year has four events. This was
considered and rejected in favour of the boundary above — recurrence is what makes event
tables complicated, and the thing that needed it (meetings) is already modelled elsewhere.

---

## 2. Nothing owns an event

An event is **an item**, registered in `grant_scope_type` under the code `event`, like a
group or a role is. It has no owner. There is no column on `event` naming a person, a
group, or a unit, and nothing in the resolver tests one
([D-102](../decisions/round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)).

Two facts replace the whole of ownership:

| | |
|---|---|
| **A grant at the unit** | reaches **every event there is**, because after [D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row) there is no scope between the unit and an item, and no ownership relation to test |
| **A grant on one event** | reaches that event and nothing else |

Creating one needs `event.create`, whose `applies_to` is `unit`: anybody holding it creates
an event, and nobody else does. Writing `event.create` **on** an event is refused when the
grant is saved, with the reason in the message — an event cannot be created twice, and a
creation permission attached to a thing that already exists answers no question
([D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)).

**Withdrawn: `event.org_unit_id`, and with it [D-058](../decisions/round-05.md#d-058--an-event-is-a-dated-occasion-owned-by-exactly-one-unit)'s
ownership, [D-063](../decisions/round-05.md#d-063--an-event-is-an-artifact-of-its-unit-not-a-child-of-it)'s
artifact rule, and [D-094](../decisions/round-09.md#d-094--the-root-unit-owns-every-imported-event)'s
import default.** D-058 recorded *"one owning unit"* and insisted that a joint camp is
**Pack A's event that Pack B's children register for**, so that nobody had to arbitrate
"whose event is this?" and one body remained the author of the record. It was not a
preference but a consequence of D-049: two owners would have made the root's blindness to a
sub-unit's events *partial*, with an exception shaped exactly like a joint camp and no
principled place to stop. That argument has no premise left. With one unit and no
sub-units there is no root to keep blind, and with no owner column there is nothing to
arbitrate — **a joint camp is an event**, and the second group's children reach it because a
grant names them, exactly like every other reader.

~~An event belongs to exactly one unit, and for anything a group runs, that is the group.~~
**Withdrawn by D-102.** What survives of the boundary is the part that was never about
ownership: an event is one dated row, and the question "who may see this event?" has one
home, which is the grant table.

### Writing an event on one event

Because a unit-scope grant reaches everything, an item grant is for the narrow case, and the
two are not interchangeable. This is where the model refuses things at the save rather than
discovering them at the check:

| Written | Result |
|---|---|
| `event.edit` on one event | **Allowed.** A capability on the item — [D-006](../decisions/round-01a.md#d-006--per-item-permissions-are-capabilities-on-the-item) unchanged |
| `event.create` on one event | **Refused at save**, with the reason: `applies_to` is `unit` |
| `membership.manage` on one event | **Refused at save**, for the same reason |
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
with a registration)`. The question "who hasn't replied yet?" is a subtraction, and it is a
query — [data-model/08 §9](../data-model/08a-event-guards-and-checks.md#9-the-three-queries-that-matter).
Nothing changed about that in round 10 except what fills the first bracket: the reachable
set is a set of people named by grants, which is what makes the subtraction a query at all.

### The registration window

Registration is open inside a period and closed outside it, and the period is two columns on
the event — `registration_opens_at` and `registration_closes_at`.

`NULL` on the close means **until the event starts**, which is the "unlimited" case you
described. `NULL` on the open means the window opens as soon as the event is visible at all —
appropriate for a hike, wrong for a jamboree whose sign-up should not open before the dates
have been decided.

---

## 4. Who may register: capability, not a separate rule engine

Registering yourself requires **one permission: `event.register_self`, held on that event** —
either by an allow on the event itself, or by an allow at the unit, which after D-097
reaches the event along with every other. Nothing else.

This is the answer to the question [D-006](../decisions/round-01a.md#d-006--per-item-permissions-are-capabilities-on-the-item)
left open. D-006 said *"eligibility ... will be a separate concept when events are
specified."* Your answer was that a person holding the capability on the item should be able
to register — and that turns out to **dissolve** the deferral rather than satisfy it: there
is no separate eligibility concept, because the capability already is one
([D-060](../decisions/round-05.md#d-060--eligibility-is-capability-there-is-no-separate-rule-engine)).
Round 10 removed the *ladder* the answer was phrased on
([D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality));
it did not touch the answer.

~~`view` may SEE · `contribute` may REGISTER · `manage` may ORGANIZE · `admin` may CONTROL~~
— **withdrawn by D-099.** There is no ladder to climb and no level to compare, so the four
words above name nothing. What replaces them is four questions, each answered by one row of
`access_grant` and each with its own code:

| Question | Code |
|---|---|
| May they see it? | `event.view` |
| May they register for it? | `event.register_self` |
| May they run its roster? | `event.manage_participants` |
| May they mark the register? | `event.presence.mark` |

Each is `allow` or `deny`, and the answer to a check is *allowed* when some live allow
applies and no live deny applies. Two of those codes being held by one person is two rows,
not a person who sits at some level — which is what makes "what exactly does this person
have on this camp?" a question with an answer.

**This is why audiences matter here.** Registering 200 children one at a time is 200 grant
rows — but opening the event to everybody who currently holds a membership is **one**: a
grant whose scope is that event, whose grantee is an audience whose expression is `MEMBERS`,
and whose effect is `allow`. That single row is what D-042 was built for, and it is the
normal way to run an open event. Per-person grants are for the exceptions.

### An age rule is an audience, not a rule

The obvious objection is a camp for 11–14 year-olds. How does a grant express "only
11-to-14s"? **A named set.** ~~`unit:<id>:participants` is a rule the resolver evaluates, so
an event for the older section is opened to that section's participants~~ — **withdrawn by
D-097**, which deleted the units those audiences were built over. The sentence's shape is
unchanged and the mechanism is now plainly the one D-098 made: the organization keeps a
group of the older section and opens the camp to `GROUP(<that group>)`. An age-gated camp is
a camp opened to a set whose members are that age.

**There is now a second way to write that sentence, and it is the same kind of thing.**
`OLDER(n)` and `YOUNGER(n)` are seeded operands of the registry
([D-107](../decisions/round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)),
so the camp for 11-to-14s is also writable as `(MEMBERS * OLDER(11)) - YOUNGER(15)` —
one grant, one expression, no roster to keep current. The group is still the better answer where
the section is a real group with a real roster behind it, because a maintained group says who
is in it and an age expression only says who qualifies; the two are not rivals and an
organization will use both.

**What this page said for four rounds, and what is true now.** Until this round the model
could not state an age *ceiling* at all, and that inability was the reason a camp could not
have one: a 9-year-old holding `event.register_self` on a camp for teenagers could register,
and ~~nothing in the system objects~~ — there was nothing in the system that *could*.
`YOUNGER(n)` is a seeded operand now
([D-107](../decisions/round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)),
so the ceiling is an ordinary grant: `event.register_self` on this event, aimed at
`MEMBERS * YOUNGER(15)`. **[D-070](../decisions/round-05.md#d-070--an-event-has-no-age-ceiling-the-grant-is-the-rule)
therefore stays closed for a different reason than it was closed**, and the difference is the
whole point of this section: it closed because the sentence was unwritable, and it stays
closed because the organization **chooses** not to write it and keeps the judgement in the
roster a leader reads and in the attributed registration that records who let a child through.
A closed question that could now be opened is a decision, and it should be read as one every
time the next restriction is requested.

What has *not* moved is the column. There are still no `min_age`/`max_age` on `event` and
there will not be some, and the reason is untouched by the new operands: **a condition
evaluated at registration time that the capability model does not know about is the first
rule-engine rule**, and the second is always cheaper than the first. Two years after that, the
answer to "who can register for this?" stops being readable from `access_grant`. A ceiling
written in a grant is readable there; a ceiling written on the event row is exactly the thing
that is not.

What makes the residual risk survivable is not a check but three properties the schema already
has. The registration is **attributable** — `source = 'staff'` with a named `created_by`, so
the judgement belongs to somebody. Age is **one join away** — `person.birth_date`, which the
roster query in [data-model/08 §9](../data-model/08a-event-guards-and-checks.md#9-the-three-queries-that-matter)
already selects, so any list a leader works from can carry it without a new column anywhere;
and as of this round the same column is also **one operand away**, which is what makes the
ceiling above a writing choice rather than a feature request. And the age-bounded case, the
ordinary one, is handled twice over now: open the event to the set whose members are that age,
by a group somebody maintains or by the age operands themselves.

**The shape recurred, and the fix this page predicted is the one that arrived.** It was never
going to be a column on `event`, and never a rule the organizer types; it was another
**operand** — a shipped row in `selector_type`, alongside `MEMBERS`, whose predicate the
resolver owns. That is what shipped: `OLDER(n)` and `YOUNGER(n)`, read against
`person.birth_date` **on the date being checked**, composed by `+ - *` like every other operand
([D-107](../decisions/round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)).
~~It ships nothing of the kind today~~ was true when it was written and is the sentence this
round retired.

**A writer still may not type `AGE >= 13`, and the reason this page gave for that was wrong.**
~~because an attribute is not a set of people~~ — `OLDER(13)` is exactly a set of people: the
ones who are thirteen or older on the date being checked, in the same way `MEMBERS` is the set
of people who pass `is_current_member` and `ROLE(x)` is the set who hold that office. Every
operand in the registry is a test with a set behind it, so the old test would have barred
`MEMBERS` too, since nothing here stores the member list. What was doing the work, and is the
clause to quote from now on, is that **an operand must be a named operand — a row of the
registry** — and this language has no comparison operator for `AGE >= 13` to be assembled out
of. **The guardianship channel is deliberately absent from that list, in both spellings**
(`GUARDIANS` and `GUARDIANS(x)`) — the parenthesised one was in the enumeration immediately above until
round 13 removed it, and this page has no table of seeded values to have carried the other
([D-113](../decisions/round-13.md#d-113--the-guardianship-channel-has-no-expression-guardians-is-not-a-selector)):
*"True, GUARDIANS should not be selectable in the audience, guardians can perform ANY action (their
read/write perms grant) on behalf of the child."* A check about a child asks whether a live `guardianship`
row links the two people and reads `right_level ∈ none | view | write` off it — a lookup over a
relationship, not a set the language resolves — so an aimed-at-guardians operand would hand those people,
one code at a time, a subset of what the channel already gives them. The registry is organization-read-only, so the next predicate anyone wants arrives the way
an age band did: as a deployment, with its evaluator arm shipped beside it, and not as a
setting. Either way every answer to "who may register" keeps living in one table, which is the
property worth defending.

---

## 5. Organizers are appointed, not granted

An event has a **set of organizers** — the people running it. That list is
`event_organizer`, and it is **the domain answer** to "who is running this?", labelled,
ordered, attributed.

> **An `event_organizer` row grants nothing.** This was the explicit choice and it stands
> untouched ([D-062](../decisions/round-05.md#d-062--organizers-are-appointed-on-the-event-not-granted)),
> including through D-102. `access_grant` remains what it is good at — showing a treasurer
> the books, opening the page to an audience, naming a parent who may register their child —
> and organizers are a separate concept: *who is running this*. **An operand is a set, not a
> grant** (D-102's own words), so naming `ORGANIZERS` in an expression says who is in the
> set and confers nothing, in exactly the way that naming `ROLE(leaders)` or any audience has
> never conferred anything
> ([D-005](../decisions/round-01a.md#d-005--permissions-are-grants-never-derived-from-identity),
> [D-042](../decisions/round-02-03.md#d-042--grants-may-target-audiences-not-only-individuals)).

The consequence worth understanding: an organizer is an **appointment on the thing being
run**. It can carry a **label** (`'lead'`, `'cook'`, `'driver'`) and an order, and it is not a
permission bundle — it does not carry `event.edit`, it says who the organizers are.
~~It is the event-scoped analogue of `position_assignment`~~ — **withdrawn by
[D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape),**
which deleted positions along with the bodies they were held in. The comparison that still
holds is the one D-100 left standing: like a role, an organizer is a person named against
something, and the codes that follow from it are the live grants that aim at them.

**Why the two do not drift.** The tempting design writes an `access_grant` whenever an
organizer is added, so "organizers" is just a query over grants. It fails on the label (a
grant has no room for "cook"), on the ordering, and on the reverse question — *"who is
running this camp?"* should not be answered by reading a permission table. Two concepts,
each doing its own job.

**What an organizer gets.** Membership of `event_organizer` makes a person a member of the
set `ORGANIZERS`. What that set may *do* is whatever a live grant aims at it — and today that
is one seeded grant, `event.answer.view` on the event to `ORGANIZERS` (§12). Everything else
reaches an organizer the way it reaches anybody else: through a grant that person holds.

---

## 6. How authority reaches an event

This section is the hinge the module was built around
([D-063](../decisions/round-05.md#d-063--an-event-is-an-artifact-of-its-unit-not-a-child-of-it)).
The hinge is gone, and the problem it solved is worth keeping in view, because the current
answer only looks trivial against it.

**The problem was this.** The resolver matches scope **exactly**. A check for `event.view`
at `('event', 42)` looks for a grant at **that exact scope** — and the person whose *job* is
running the camp held theirs somewhere else:

```
unit_leader  ── holds a role at ──►  org_unit 7  (the pack)
                                          │
                                          │  ✗ NO PATH
                                          ▼
event 42 "Summer camp"  ◄──── owned by ───┘     resolver checks scope exactly
```

Nothing was broken; the answer to `can(leader, 'event.view', 'event', 42)` was simply no. The
module could not ship with that gap, so D-063 closed it with a test on the owner column —
**`can_event()`**: satisfied at `('event', E)` if satisfied at the event's owning unit *and*
that unit is the owner. It argued, carefully, that this was *not* inheritance downward
because an event is an artifact of its unit rather than a child of it, and that the blast
radius was fixed at one owner.

**Withdrawn by [D-102](../decisions/round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it):**
`event.org_unit_id`, `can_event()`, and the unit-authority rule are all deleted, together
with the artifact-and-unit distinction D-063 existed to draw — there is no artifact-and-unit
pair left to distinguish. The mismatch in the diagram cannot arise, for two reasons that
compound: there is no `org_unit` scope to hold a role at
([D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)),
and there is no owner column to test even if there were. The gap closed because the ladder
between the two scopes disappeared, not because a test was added across it.

**The three ways out D-063 weighed, and where each stands:**

| Option | Then | Now |
|---|---|---|
| A grant per event per leader | Correct but fragile — 400 events, 400 forgetting opportunities | Still the fallback, and bound operands take most of its sting out (§7) |
| Authority inherits from the unit down to its events | Rejected — it was D-015/D-031 | Rejected for a reason that no longer exists; there is nothing to inherit *from* |
| The owning unit supplies authority | **Chosen** | **Withdrawn by D-102** |
| A grant at the unit reaches every item, and the people connected to an event are named by selectors that bind to it | — | **Chosen** |

D-063 advertised itself as a two-way door — "deleting the second `can()` call is the whole
change, and it needs no data migration". The door turned out to swing the other way: removing
the test was indeed the whole change and needed no migration, which is the same property
D-063 claimed, spent once. Going back the other way is now
[the narrow and expensive door D-102 names](../decisions/round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)
— an owner column, the resolver tier that reads it, and every check this module deleted —
though the bound selectors added in round 10 would survive it untouched, because an
ownership grant and a bound operand answer different questions.

### Organizers still matter, and here is how

Membership of `event_organizer` is what makes someone an organizer **in the domain sense**:
the person on the list, with a label, whose name the parents see. Authority for *acting* on
the event comes from grants, as it does everywhere else:

| Who | How they may manage it |
|---|---|
| The person who runs the organization's camps | `event.manage_participants` **at the unit** — the grant reaches every event |
| Somebody trusted with one camp | the same code **on that event**, as an item grant |
| An organizer, as such | only what a grant aims at `ORGANIZERS` — today, the seeded `event.answer.view` |
| Somebody the organization has excluded | a **deny** on the event or at the unit; deny is absolute and beats every allow ([D-013](../decisions/round-01a.md#d-013--explicit-deny-revoked-is-checked-before-everything)) |
| `system.admin` | Everything — the sole exception, as everywhere |

The fourth row is the one the old model could not draw, and it is worth naming: the row that
used to read *"the treasurer — nothing, not without an exposure"* was the whole no-inheritance
policy in one line. There is no exposure left to withhold, so the policy is now stated
positively — a person holds what the rows name — and negatively, by deny, when holding it is
the thing that must be impossible
([D-013](../decisions/round-01a.md#d-013--explicit-deny-revoked-is-checked-before-everything)).
What was given up is recorded once, in
[D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row):
the named adult who granted access to a body's children was somebody that body chose, and
there is no body left to choose them.

---

## 7. The people connected to an event

~~What the root can and cannot see~~ — this section used to answer "can the center read a
pack's camp roster?", and the answer was **no**, by D-049. Round 10 deleted the pack and the
exposure that was the only way across, so the question has no subject
([§6](#6-how-authority-reaches-an-event)). What replaces it is the question D-102 actually
answers, and it is a better question for the module: **who is connected to this event?**

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
[data-model/08 §8](../data-model/08a-event-guards-and-checks.md#selectors-that-bind-to-an-event). They are
ordered by containment rather than by rank — `CONFIRMED` ⊆ `PLACED`, `PLACED` and
`ON_WAITLIST` partition `ATTENDED`, and a person who declined is in none of them — and no
level or ladder is involved in any of them
([D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)).

**The bound form is the important half, and it kills a specific flaw.** `ATTENDED(<event
1204>)` written on event 1204 is one grant per event with the event's own id typed into it,
so "every participant may see the other participants" is a thing you do 400 times and forget
on the 401st. Bound, it is one expression written the same way every time. That is the whole
reason the argument-less form exists, and the two rules that make it safe are write-path
rules, stated as requirements in [data-model/08 §8](../data-model/08a-event-guards-and-checks.md#selectors-that-bind-to-an-event).

**`PRESENT(<event>)` is refused, and this is where presence tempts a reader.** The obvious
sixth operand is "the ones who actually turned up", computed over `was_present` (§9). It is
refused, and the reason is the failure direction: `was_present` is `NULL` until somebody
takes a register, so an operand built on it would revoke a child's access to their own camp
photos because a volunteer forgot to tick a box. `was_present` is three-valued *on purpose*
as a safeguarding signal — **keeping it out of the selector language is what keeps it
meaning "a person recorded this" rather than "this is who may see things"**, and
[D-067](../decisions/round-05.md#d-067--presence-is-a-three-valued-fact-on-the-registration)'s
reasoning for the third value is the reasoning for the refusal. **And this consequence is the
whole of the refusal**, which is worth saying out loud now that the language has an operand
that reads a column against a date: `OLDER(n)` reads `person.birth_date`
([D-107](../decisions/round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)),
so nothing structural stops anybody writing `PRESENT` — there is only ever going to be this
argument standing in the way, and it holds on its own.

**`WHITELISTED` does not exist, and is not a selector.** The nearest stored facts are
`source = 'staff'` (an organizer entered them) and promotion off the waitlist. Either the
word is to mean one of those or it names a new column on `event_registration`, which is an
events decision and not a selector decision — so it stays an open question rather than being
implied by a word in a grammar. Nothing in this module reserves the name.

### The screen must say which event it is talking about

D-091 made the audience preview a requirement rather than a nicety: *"the person saving the
grant is looking at one row that mentions no person at all"*, so the editor must **show the
expanded people** a grant reaches. Round 10 moves the requirement one level down and makes it
sharper.

**The preview is computed for an item, and the screen says so.** `PLACED` means different
people on different events, so "who does this grant reach?" is no longer answerable from the
grant row alone — for a grant whose expression contains a bound operand, it is answerable
only as *"on event 1204, these 84 people"*, and the screen must name the event it computed
against rather than presenting the list as a property of the grant. The consequences are
requirements on the editor and ~~the cache~~ **the read path**, not on the schema:

- An expression containing a bound operand is previewed **per item**. Asking for a preview of
  such a grant at the unit is not a large computation, it is a refused one — the same refusal
  the save applies. **The per-item preview carries no cap, no cache and no background job, and now
  on stated grounds rather than hope:** the system is specified against a few hundred people in the
  organization, a few dozen registrants on a typical event and a big camp on the order of two hundred,
  so previewing one item evaluates a couple of hundred predicates and nobody feels it
  ([D-112](../decisions/round-13.md#d-112--the-systems-scale-is-stated-hundreds-of-people-tens-of-registrants-per-event)).
  That size is **stated, not measured** — nothing in these documents has measured anything here — and the
  trigger for reopening it is a few thousand people, or a thousand registrants on one event. **One dependency
  arrived since:** the nightly rebuild used to pre-pay this work off the interaction, and with the cache deleted
  the preview computes it **on open** — still affordable, now with no fallback behind it
  ([D-114](../decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation)).
- Where no item is in hand, the editor says what the expression *means*, not who it reaches.
- ~~The cache key for a bound operand **includes the item**~~ — the answer cache that had that key is deleted
  ([D-114](../decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation)),
  and the reason it was there is untouched: the same grant on two events has two answers
  ([D-102](../decisions/round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)).
  A compiled expression holds no item precisely because the item arrives as a parameter, so the item is now bound
  at **resolution** — nothing expanded or resolved while checking one event may be served for another, and any
  cache of a *resolution* rather than of a compilation is keyed by the item or it is wrong.
- **A registration write is not a ruleset write, and that no longer means what this bullet said it meant.**
  ~~There is one cache policy and three triggers — rebuilt nightly in full, immediately on any write to the
  ruleset, and on explicit request — and `event_registration` is not part of the ruleset
  ([D-111](../decisions/round-13.md#d-111--the-permission-cache-is-rebuilt-nightly-on-any-ruleset-change-and-on-request)).
  So an answer that runs through `PLACED`, `CONFIRMED`, `ATTENDED` or `ON_WAITLIST` **may be up to one
  night behind the roster**, and this is the module where an implementer would most confidently assume
  otherwise. It is the same residual window as a birthday, and it is not the safeguarding window: every
  withdrawal a person actually *performs* — a revoke, a deny, ending a grant's period, ending an
  assignment — is a ruleset write and rebuilds at once. What waits for the night is what nobody does.~~
  **What is true now:** marking a register, confirming a place, flipping `is_confirmed` or promoting somebody off
  the waitlist moves `ATTENDED`, `PLACED`, `CONFIRMED` and `ON_WAITLIST`, and the new state is visible **on the
  next check**, because resolution is live and there is no answer stored anywhere to be behind the roster — and
  `ORGANIZERS`, the fifth bound operand, moves on its own rows with the same immediacy
  ([D-114](../decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation)).
  **This page was right to be uneasy.** A window opened by a boundary drawn in another file, over four tiers this
  module computes and that file never listed, is the exact shape that got the cache deleted — the omission that
  did it was `membership`, and the write that made it fatal was `membership.terminate` ⛔. **What is still true of
  the old wording, precisely:** a registration write changes no rule's text, so it is not a ruleset write in the
  only sense the phrase now carries, and `ruleset_version` is bumped by `audience_operand` and `selector_type`
  alone. Being outside that set buys a compilation nothing; it buys a check nothing either. **And since this
  bullet just deleted the mechanism behind a rule, it owes the D-081 answer**
  ([D-081](../decisions/round-06.md#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now)):
  **nobody enforces "a registration change must reach an answer" any more, because there is nothing left to
  invalidate** — the read path does it, and unlike a bullet in a list, a read path cannot be forgotten.

Fail closed as everywhere else in the model, **with the direction stated rather than implied**:
an operand that resolves to nothing contributes the empty set, which *narrows* what a `+` or a
`*` reaches and *widens* what a `-` takes away — `EVERYONE - PERSON(x)` with a dead `x` denies
everybody, lockout and fail-closed being the same event
([D-106](../decisions/round-11-12.md#d-106--a-failed-operand-stays-the-empty-set-the-missing-half-was-a-report-not-a-refusal)).
A person with no birth date is not that kind of failure: the operand resolves perfectly well and
they are simply not in `OLDER(18)`, exactly as a person with no membership row is not in
`MEMBERS`. A broken leaf is no longer silent and still stops nothing — it is listed on the **tab on the
permissions page**, and no save is refused for it
([D-109](../decisions/round-13.md#d-109--nothing-a-rule-names-is-deleted-deprecated-hidden-disabled--and-a-tab-instead-of-a-report)).
**And that tab has become nearly empty by construction, which is the point of the ruling:** nothing a rule
names is deleted any more. A retired office, group or audience is flagged `deprecated`, `hidden` or
`disabled` and keeps resolving — only `disabled` changes the answer, and it changes it to the empty set
because somebody asked for exactly that. The one thing still able to break a leaf is a person, because
[D-088](../decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)
lets a redaction require the row to actually go and erasure wins: **a redacted person is the corpus's only
remaining way to produce a broken leaf.**

**A preview is a statement about the day it was taken.** `OLDER(n)` and `YOUNGER(n)` make that
true of every age-bearing expression in the sharpest form there is: the 84 names on the screen
are the people who qualify *today*, and a birthday moves the list with no write and no edit to the
grant. Nothing is told about it and nothing needs to be: ~~the cache is rebuilt nightly, on any ruleset
write, and on request, and an answer that moved without a ruleset write is simply allowed to be one
night stale ([D-111](../decisions/round-13.md#d-111--the-permission-cache-is-rebuilt-nightly-on-any-ruleset-change-and-on-request))~~
— **there is nothing to be stale** ([D-114](../decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation)):
a birthday moves the answer at the instant it happens, because every check resolves against live rows. What the
preview is a statement about is **the date it was taken**, and that is a fact about the calendar, not a lag to be
closed.
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
uses *today's* inner expression. That was always true and was never written; the control is the preview
this very section is about — the editor prints the resolved set before an edit to a shared expression
saves, so the person editing sees at least once what they are changing backwards in time. And a preview
that cannot be computed still shows that it could not be computed, rather than an empty list.

---
