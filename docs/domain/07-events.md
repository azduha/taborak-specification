# Events

Camps, trips, hikes, and the occasional jamboree: things that happen on a date,
that people register for, and that somebody has to run.

This module was the one the whole authorization model was built toward. `access_grant`
shipped with `scope_type = 'event'` from the first draft
([D-006](../decisions/decision-log.md#d-006--per-item-permissions-are-capabilities-on-the-item)),
`grant_scope_type` has carried a row for it since, and **audiences**
([D-042](../decisions/decision-log.md#d-042--grants-may-target-audiences-not-only-individuals))
exist partly to express *"tell everyone about this event."* Those hooks are now filled in.

Round 10 changed what they hook into. **Nothing owns an event**
([D-102](../decisions/decision-log.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)),
so every sentence this module used to write about the unit that runs an event is now a
sentence about a grant at the unit, or about a **selector that binds to the event being
checked**. The reasoning behind the sentences is kept below, marked withdrawn, because the
problem each one solved is still a problem; only its answer moved.

Domain model: [data-model/08-events.md](../data-model/08-events.md).

---

## 1. What an event is, and what it is not

An event is **a thing with a date that people sign up for**.

> **A weekly meeting is not an event.** It is a **group** — a `person_group` whose dated
> member rows already say "this child takes part in this Thursday group"
> ([D-098](../decisions/decision-log.md#d-098--a-group-is-a-persongroup-explicit-members-a-lifetime-and-no-authority)).
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
([D-102](../decisions/decision-log.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)).

Two facts replace the whole of ownership:

| | |
|---|---|
| **A grant at the unit** | reaches **every event there is**, because after [D-097](../decisions/decision-log.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row) there is no scope between the unit and an item, and no ownership relation to test |
| **A grant on one event** | reaches that event and nothing else |

Creating one needs `event.create`, whose `applies_to` is `unit`: anybody holding it creates
an event, and nobody else does. Writing `event.create` **on** an event is refused when the
grant is saved, with the reason in the message — an event cannot be created twice, and a
creation permission attached to a thing that already exists answers no question
([D-099](../decisions/decision-log.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)).

**Withdrawn: `event.org_unit_id`, and with it [D-058](../decisions/decision-log.md#d-058--an-event-is-a-dated-occasion-owned-by-exactly-one-unit)'s
ownership, [D-063](../decisions/decision-log.md#d-063--an-event-is-an-artifact-of-its-unit-not-a-child-of-it)'s
artifact rule, and [D-094](../decisions/decision-log.md#d-094--the-root-unit-owns-every-imported-event)'s
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
| `event.edit` on one event | **Allowed.** A capability on the item — [D-006](../decisions/decision-log.md#d-006--per-item-permissions-are-capabilities-on-the-item) unchanged |
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
query — [data-model/08 §9](../data-model/08-events.md#9-the-three-queries-that-matter).
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

This is the answer to the question [D-006](../decisions/decision-log.md#d-006--per-item-permissions-are-capabilities-on-the-item)
left open. D-006 said *"eligibility ... will be a separate concept when events are
specified."* Your answer was that a person holding the capability on the item should be able
to register — and that turns out to **dissolve** the deferral rather than satisfy it: there
is no separate eligibility concept, because the capability already is one
([D-060](../decisions/decision-log.md#d-060--eligibility-is-capability-there-is-no-separate-rule-engine)).
Round 10 removed the *ladder* the answer was phrased on
([D-099](../decisions/decision-log.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality));
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
([D-107](../decisions/decision-log.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)),
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
([D-107](../decisions/decision-log.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)),
so the ceiling is an ordinary grant: `event.register_self` on this event, aimed at
`MEMBERS * YOUNGER(15)`. **[D-070](../decisions/decision-log.md#d-070--an-event-has-no-age-ceiling-the-grant-is-the-rule)
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
roster query in [data-model/08 §9](../data-model/08-events.md#9-the-three-queries-that-matter)
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
([D-107](../decisions/decision-log.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)).
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
([D-113](../decisions/decision-log.md#d-113--the-guardianship-channel-has-no-expression-guardians-is-not-a-selector)):
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
> untouched ([D-062](../decisions/decision-log.md#d-062--organizers-are-appointed-on-the-event-not-granted)),
> including through D-102. `access_grant` remains what it is good at — showing a treasurer
> the books, opening the page to an audience, naming a parent who may register their child —
> and organizers are a separate concept: *who is running this*. **An operand is a set, not a
> grant** (D-102's own words), so naming `ORGANIZERS` in an expression says who is in the
> set and confers nothing, in exactly the way that naming `ROLE(leaders)` or any audience has
> never conferred anything
> ([D-005](../decisions/decision-log.md#d-005--permissions-are-grants-never-derived-from-identity),
> [D-042](../decisions/decision-log.md#d-042--grants-may-target-audiences-not-only-individuals)).

The consequence worth understanding: an organizer is an **appointment on the thing being
run**. It can carry a **label** (`'lead'`, `'cook'`, `'driver'`) and an order, and it is not a
permission bundle — it does not carry `event.edit`, it says who the organizers are.
~~It is the event-scoped analogue of `position_assignment`~~ — **withdrawn by
[D-100](../decisions/decision-log.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape),**
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
([D-063](../decisions/decision-log.md#d-063--an-event-is-an-artifact-of-its-unit-not-a-child-of-it)).
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

**Withdrawn by [D-102](../decisions/decision-log.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it):**
`event.org_unit_id`, `can_event()`, and the unit-authority rule are all deleted, together
with the artifact-and-unit distinction D-063 existed to draw — there is no artifact-and-unit
pair left to distinguish. The mismatch in the diagram cannot arise, for two reasons that
compound: there is no `org_unit` scope to hold a role at
([D-097](../decisions/decision-log.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)),
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
[the narrow and expensive door D-102 names](../decisions/decision-log.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)
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
| Somebody the organization has excluded | a **deny** on the event or at the unit; deny is absolute and beats every allow ([D-013](../decisions/decision-log.md#d-013--explicit-deny-revoked-is-checked-before-everything)) |
| `system.admin` | Everything — the sole exception, as everywhere |

The fourth row is the one the old model could not draw, and it is worth naming: the row that
used to read *"the treasurer — nothing, not without an exposure"* was the whole no-inheritance
policy in one line. There is no exposure left to withhold, so the policy is now stated
positively — a person holds what the rows name — and negatively, by deny, when holding it is
the thing that must be impossible
([D-013](../decisions/decision-log.md#d-013--explicit-deny-revoked-is-checked-before-everything)).
What was given up is recorded once, in
[D-097](../decisions/decision-log.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row):
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
[data-model/08 §8](../data-model/08-events.md#selectors-that-bind-to-an-event). They are
ordered by containment rather than by rank — `CONFIRMED` ⊆ `PLACED`, `PLACED` and
`ON_WAITLIST` partition `ATTENDED`, and a person who declined is in none of them — and no
level or ladder is involved in any of them
([D-099](../decisions/decision-log.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)).

**The bound form is the important half, and it kills a specific flaw.** `ATTENDED(<event
1204>)` written on event 1204 is one grant per event with the event's own id typed into it,
so "every participant may see the other participants" is a thing you do 400 times and forget
on the 401st. Bound, it is one expression written the same way every time. That is the whole
reason the argument-less form exists, and the two rules that make it safe are write-path
rules, stated as requirements in [data-model/08 §8](../data-model/08-events.md#selectors-that-bind-to-an-event).

**`PRESENT(<event>)` is refused, and this is where presence tempts a reader.** The obvious
sixth operand is "the ones who actually turned up", computed over `was_present` (§9). It is
refused, and the reason is the failure direction: `was_present` is `NULL` until somebody
takes a register, so an operand built on it would revoke a child's access to their own camp
photos because a volunteer forgot to tick a box. `was_present` is three-valued *on purpose*
as a safeguarding signal — **keeping it out of the selector language is what keeps it
meaning "a person recorded this" rather than "this is who may see things"**, and
[D-067](../decisions/decision-log.md#d-067--presence-is-a-three-valued-fact-on-the-registration)'s
reasoning for the third value is the reasoning for the refusal. **And this consequence is the
whole of the refusal**, which is worth saying out loud now that the language has an operand
that reads a column against a date: `OLDER(n)` reads `person.birth_date`
([D-107](../decisions/decision-log.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)),
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
requirements on the editor and the cache, not on the schema:

- An expression containing a bound operand is previewed **per item**. Asking for a preview of
  such a grant at the unit is not a large computation, it is a refused one — the same refusal
  the save applies. **The per-item preview carries no cap, no cache and no background job, and now
  on stated grounds rather than hope:** the system is specified against a few hundred people in the
  organization, a few dozen registrants on a typical event and a big camp on the order of two hundred,
  so previewing one item evaluates a couple of hundred predicates and nobody feels it
  ([D-112](../decisions/decision-log.md#d-112--the-systems-scale-is-stated-hundreds-of-people-tens-of-registrants-per-event)).
  That size is **stated, not measured** — nothing in these documents has measured anything here — and the
  trigger for reopening it is a few thousand people, or a thousand registrants on one event.
- Where no item is in hand, the editor says what the expression *means*, not who it reaches.
- The cache key for a bound operand **includes the item**
  ([D-111](../decisions/decision-log.md#d-111--the-permission-cache-is-rebuilt-nightly-on-any-ruleset-change-and-on-request)),
  because the same grant on two events has two answers
  ([D-102](../decisions/decision-log.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)).
- **A registration write is not a ruleset write.** There is one cache policy and three triggers — rebuilt
  nightly in full, immediately on any write to the ruleset, and on explicit request — and
  `event_registration` is not part of the ruleset
  ([D-111](../decisions/decision-log.md#d-111--the-permission-cache-is-rebuilt-nightly-on-any-ruleset-change-and-on-request)).
  So an answer that runs through `PLACED`, `CONFIRMED`, `ATTENDED` or `ON_WAITLIST` **may be up to one
  night behind the roster**, and this is the module where an implementer would most confidently assume
  otherwise. It is the same residual window as a birthday, and it is not the safeguarding window: every
  withdrawal a person actually *performs* — a revoke, a deny, ending a grant's period, ending an
  assignment — is a ruleset write and rebuilds at once. What waits for the night is what nobody does.

Fail closed as everywhere else in the model, **with the direction stated rather than implied**:
an operand that resolves to nothing contributes the empty set, which *narrows* what a `+` or a
`*` reaches and *widens* what a `-` takes away — `EVERYONE - PERSON(x)` with a dead `x` denies
everybody, lockout and fail-closed being the same event
([D-106](../decisions/decision-log.md#d-106--a-failed-operand-stays-the-empty-set-the-missing-half-was-a-report-not-a-refusal)).
A person with no birth date is not that kind of failure: the operand resolves perfectly well and
they are simply not in `OLDER(18)`, exactly as a person with no membership row is not in
`MEMBERS`. A broken leaf is no longer silent and still stops nothing — it is listed on the **tab on the
permissions page**, and no save is refused for it
([D-109](../decisions/decision-log.md#d-109--nothing-a-rule-names-is-deleted-deprecated-hidden-disabled--and-a-tab-instead-of-a-report)).
**And that tab has become nearly empty by construction, which is the point of the ruling:** nothing a rule
names is deleted any more. A retired office, group or audience is flagged `deprecated`, `hidden` or
`disabled` and keeps resolving — only `disabled` changes the answer, and it changes it to the empty set
because somebody asked for exactly that. The one thing still able to break a leaf is a person, because
[D-088](../decisions/decision-log.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)
lets a redaction require the row to actually go and erasure wins: **a redacted person is the corpus's only
remaining way to produce a broken leaf.**

**A preview is a statement about the day it was taken.** `OLDER(n)` and `YOUNGER(n)` make that
true of every age-bearing expression in the sharpest form there is: the 84 names on the screen
are the people who qualify *today*, and a birthday moves the list with no write and no edit to the
grant. Nothing is told about it and nothing needs to be: the cache is rebuilt nightly, on any ruleset
write, and on request, and an answer that moved without a ruleset write is simply allowed to be one
night stale ([D-111](../decisions/decision-log.md#d-111--the-permission-cache-is-rebuilt-nightly-on-any-ruleset-change-and-on-request)).
**The preview is a workbench, not a record — and the record is the expression**
([D-110](../decisions/decision-log.md#d-110--the-expression-is-the-record-of-whom-a-grant-reached)).
The audit row written when a grant is saved says *this person wrote these words, about this item, on this
date*. What the preview printed alongside it is logged as **a rendering on a date**, never as a statement
of who was in it: a stored list of everyone a rule happened to cover, kept after the rule was withdrawn,
is the roster table this corpus has deleted twice. So *"whom did this grant reach in May?"* is answered,
if at all, by evaluating the words against the data of May — and these documents do not promise the
answer. Words-only is affordable rather than brave only because of
[D-109](../decisions/decision-log.md#d-109--nothing-a-rule-names-is-deleted-deprecated-hidden-disabled--and-a-tab-instead-of-a-report):
since nothing a rule names is deleted, the words keep resolving long after their reason is gone.
**What that concedes, so nobody finds it later:** a shared audience holds a word, not a copy, so **an edit
to a shared audience is a retrospective edit to every rule that names it**, and a re-evaluation for May
uses *today's* inner expression. That was always true and was never written; the control is the preview
this very section is about — the editor prints the resolved set before an edit to a shared expression
saves, so the person editing sees at least once what they are changing backwards in time. And a preview
that cannot be computed still shows that it could not be computed, rather than an empty list.

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
([D-065](../decisions/decision-log.md#d-065--capacity-is-a-waitlist-threshold-and-organizers-may-exceed-it)).
The overrun is permitted, attributed, and **reported**
([data-model/08 §10](../data-model/08-events.md#10-integrity-checks)): an event running over
its stated capacity is a fact the organization can see, not a state it cannot reach.

The mechanism of *how* an organizer gets past the number is unchanged by round 10 and was
never the resolver: the waitlist fires only for `source = 'self'`, and a registration written
by a person holding `event.register_other` arrives as `source = 'staff'` and is admitted.
What changed is where that permission came from — before, the owning unit supplied it; now it
is a grant at the unit or on the event, like every other code
([D-102](../decisions/decision-log.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)).

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
([D-067](../decisions/decision-log.md#d-067--presence-is-a-three-valued-fact-on-the-registration)).

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
[D-064](../decisions/decision-log.md#d-064--there-is-no-event-status-visibility-is-the-permission-model)
a draft reached exactly one audience: the owning unit's own people, whom
[D-063](../decisions/decision-log.md#d-063--an-event-is-an-artifact-of-its-unit-not-a-child-of-it)'s
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
gate** ([D-061](../decisions/decision-log.md#d-061--event-answers-are-read-by-that-events-organizers)),
and round 10 changed only *where that sentence is written down*. It is no longer prose inside
the resolver; it is **a seeded grant** — `event.answer.view` on an event, aimed at
`ORGANIZERS`
([D-102](../decisions/decision-log.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)).
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
([D-074](../decisions/decision-log.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular),
[D-079](../decisions/decision-log.md#d-079--the-guardianship-channel-is-entered-by-shape-not-by-permission-name);
[appendix/permission-catalog.md §9](../appendix/permission-catalog.md#9-there-is-no-dependent-namespace)).
The namespace that used to spell this out is deleted, the safeguarding property it carried is not:

> *"A person does not get these by virtue of leading — that is a safeguarding
> property."*

**Corrected in round 7, because this sentence was doing work it could no longer do.** It used to read
*"so a camp leader cannot reach a child's medical record at all"* — and after
[D-083](../decisions/decision-log.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)
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
  after [D-097](../decisions/decision-log.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)
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
[D-061](../decisions/decision-log.md#d-061--event-answers-are-read-by-that-events-organizers),
with the reasoning, so that nobody later "fixes" the apparent duplication between the two
stores by tightening this one.

**Event answers are not the person's record.** They are operational detail for one event, read by that
event's organizers, and they end with the event — while the same fact, recorded on the person, is
audited, curable and erased with them. **[D-083](../decisions/decision-log.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)
made those two copies the same class of data**, which is what turns the retention question below into
a real one, and [AT-1](../open-questions.md#at-1--should-an-event-question-bind-to-an-attribute-code)
into the alternative: collect the fact once, confirm it at the door. See
[§11](../data-model/08-events.md#11-open-issues) for the retention question, which is open.

---

## 13. Open issues

Moved to [../open-questions.md](../open-questions.md) under **G. Events**, where they are
tracked with the rest. The ones this module raises:

- ~~**The age ceiling on an open event**~~ — **settled: accepted as a risk**, the grant is
  the rule, and closing it later would mean a new operand rather than a column (§4,
  [D-070](../decisions/decision-log.md#d-070--an-event-has-no-age-ceiling-the-grant-is-the-rule)).
  **That prediction has come true and it changes the shape of the answer, not the answer:** the
  operand arrived as `YOUNGER(n)`, so an age ceiling is writable today as
  `event.register_self` aimed at `MEMBERS * YOUNGER(15)`. **EV-1 stays closed, now as a choice
  the organization renews rather than a limit it inherits** — nobody has to be told the ceiling
  cannot be stated, only whether it should be (§4,
  [D-107](../decisions/decision-log.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)).
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
  ([D-107](../decisions/decision-log.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)).
- **Event answer retention** (§12). Answers end with the event — but a dietary answer naming a
  condition is data of exactly the same class as what the person record holds, held under weaker rules
  and fresher. No policy yet; see
  [EV-2](../open-questions.md#ev-2--retention-of-event_answer).
- **Cancelled events and fees** (§10–11). Cancelling keeps the registrations; whether it
  releases the obligations, refunds them, or neither is the finance module's call.
- **Presence for minors and the safeguarding record** (§9). `was_present` is the "who was in
  our care" record. Whether it needs its own retention or its own permission is unresolved —
  and §7's refusal of `PRESENT` is the sharp edge of why that matters.
