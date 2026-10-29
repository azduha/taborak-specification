# Data Model — Events: guards, the three queries, integrity checks

How authority reaches an event, what the module may assume, the three questions a screen asks it, and the checks that hold it together.

**Section numbers are shared across the two parts** and never renumbered, because other pages cite them by number and their anchors are built from them: [08-events.md](08-events.md) holds §1–§7, [08a](08a-event-guards-and-checks.md) §8–§11 (projections and guards, the three queries that matter, integrity checks, open issues).

---

## 8. Projections and guards

### The unit-authority rule, and `can_event()` — both deleted

~~A permission is satisfied at `('event', E)` if it is satisfied at the event's owning unit
`('org_unit', E.org_unit_id)` AND the event's owner is that same unit.~~ **Withdrawn by
[D-102](../decisions/round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it),**
which deleted `event.org_unit_id` (§2) and with it the whole rule, together with
[D-063](../decisions/round-05.md#d-063--an-event-is-an-artifact-of-its-unit-not-a-child-of-it)'s
artifact-and-child distinction. `can_event(person, permission_code, event, at)` is deleted;
**every event check goes through the ordinary `can()` and nothing else.**

**Who enforces it now — `can()`, with no event-shaped clause in it.** The resolver matches
scope exactly, exactly as before, and the gap D-063 was written to close cannot open: the
only non-item scope is the unit, and a grant at the unit reaches every item of every type
([D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)).
The person whose job is to run the organization's camps passes a check at `('event', 42)`
because their allow is at the unit, not because anything tested the event.

**D-063's reasoning, kept because the problem it named is still a problem.** The old design
refused to let authority inherit from a body down to that body's events, and bought a narrow
rule instead of a wide one, on the grounds that inheritance's blast radius grows with every
restructure while an owner column's does not. Both halves of that pair are gone: there are no
bodies and no restructures
([D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)),
so there is nothing left to keep narrow. What replaced the distinction is not inheritance and
not a test — it is the **absence of an intermediate scope**. Between the unit and an event
there is now nothing to inherit through, which is the same outcome D-063 was reaching for by
way of a rule.

**D-063's two-way door, spent.** It promised that "deleting the second `can()` call is the
whole change, and it needs no data migration", because nothing had been written to
`access_grant` to make the rule work. Round 10 collected on that: deleting the rule is the
whole change and needed no migration. The door back is narrower now — an owner column, a
resolver tier that reads it, and the checks this section deletes — and the bound selectors
below would survive it unchanged, because an ownership grant and a bound operand answer
different questions.

### Selectors that bind to an event

Six sets describe the people connected to an event, and each is a **selector that binds to
the item being checked** — written with no argument inside an item-scope grant, and with an
explicit event in every other context. They are seeded rows of `selector_type`, the registry
of [data-model/05 §8](05a-audience-and-grammar.md#8-audience--grants-that-target-a-set-of-people), and
that registry is what makes the two write-path rules below checkable rather than a matter of
tact
([D-101](../decisions/round-10b.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree),
[D-102](../decisions/round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)).

**The four attendance tiers, defined over `event_registration` columns and nothing else:**

| Operand | Definition | Read it as |
|---|---|---|
| `ATTENDED` | `response` is `attending` | said yes to this event |
| `PLACED` | `response` is `attending` **and** `is_waitlisted` is false | holds a place — **the capacity set** (§5) |
| `CONFIRMED` | `PLACED` **and** `is_confirmed` is true | the place is paid for, or the event was free |
| `ON_WAITLIST` | `response` is `attending` **and** `is_waitlisted` is true | waiting for a place |

These are definitions, not four new ideas, and their shape is arithmetic on two existing
columns: `CONFIRMED ⊆ PLACED`, `PLACED` and `ON_WAITLIST` partition `ATTENDED`, and a `not_attending`
row is in none of them. Nothing is a level and nothing orders anything else; `CONFIRMED` is
not "more" than `ON_WAITLIST`, it is a different conjunction. **The extension of `PLACED` is
the set §5 counts against `capacity`**, and the same partial index serves both (§4).

`ORGANIZERS` is the fifth, and its definition is the roster in §3 — the labelled, ordered,
domain answer to "who runs this", evaluated over `event_organizer` rows for the event
checked. **There is no sixth, and this page printed one until round 13.** The `GUARDIANS` that sat in
that sentence was never an operand at all, in either spelling: a guardian's authority is a
`right_level ∈ none | view | write` held **over a child**, read off the `guardianship` row when the check
is about someone other than the actor, and it is not a set that the expression language resolves
([D-113](../decisions/round-13.md#d-113--the-guardianship-channel-has-no-expression-guardians-is-not-a-selector),
[D-074](../decisions/round-06.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular)).
Counting it alongside these five was the error, not a narrower way of stating the channel — which is why
the paragraph below already called `PRESENT` the obvious sixth.

**`PRESENT(<event>)` is refused.** An operand over `was_present` is the obvious sixth
attendance tier and it is not available, and the reason is the failure direction:
`was_present` is `NULL` until somebody takes a register, so a grant aimed at `PRESENT` would
revoke a child's access to their own camp photos because a volunteer forgot to tick a box.
The column is a safeguarding signal and is three-valued on purpose
([D-067](../decisions/round-05.md#d-067--presence-is-a-three-valued-fact-on-the-registration));
keeping it out of the selector language is what keeps it meaning "a person recorded this"
rather than "this is who may see things". Where presence is needed it is needed as a report
(§9), and the report is honest about the rows it does not have.

**`WHITELISTED` does not exist.** There is no stored state to name: the nearest facts are
`source = 'staff'` (an organizer entered them) and promotion off the waitlist. Until the
organization decides which of those it means, or adds a column, the operand is not available
and the name is not reserved (§11).

**Two binding rules, both refused when the grant is saved, both naming the operand in the
message:**

1. **A bound (argument-less) operand is legal only on an item-scope grant.** At the unit there
   is no item for it to bind to, so a grant at the unit whose expression names `PLACED`,
   `ATTENDED`, `CONFIRMED`, `ON_WAITLIST` or `ORGANIZERS` is refused. The explicit form
   (`PLACED(<event>)`) remains legal at the unit, and it means the same words with the event
   written down — which is the difference between the two, not an accident of parsing.
2. **A bound operand is legal only on a matching item type.** `PLACED` on a `person_group`
   grant is refused, because that item is not an event. This is `selector_type.argument_type`
   checked against `grant_scope_type` at the write — which is the reason D-101's registry is
   doing real work and not merely tidying a table.

A consequence of rule 1 worth naming for whoever builds the editor: **an audience is a stored
row and a grant is a different stored row**, so an audience whose expression contains a bound
operand is perfectly storable and simply cannot be aimed at a unit-scope grant. The refusal
lands on the grant, where D-102 puts it, and the audience browser should show which scopes an
expression is usable at rather than letting the save discover it
([../domain/07-events.md §7](../domain/07-events.md#7-the-people-connected-to-an-event)).

**The seeded grant: `event.answer.view` on an event to `ORGANIZERS`.** This is where
[D-061](../decisions/round-05.md#d-061--event-answers-are-read-by-that-events-organizers)'s
"answers are read by that event's organizers" now lives — a row in `access_grant`, not a
clause in the resolver, which is the same move D-102 made to the whole of unit authority over
an event. It is aimed at a **set**, so it does not contradict
[D-062](../decisions/round-05.md#d-062--organizers-are-appointed-on-the-event-not-granted)
and does not make `event_organizer` a grant table: adding a cook to the roster changes a set,
and the grant keeps pointing at the set. The registered spelling of the code is the catalog's
`event.answer.view`, singular *answer*, which [D-102](../decisions/round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)
now uses too — it wrote `event.answers.view` while the entry was new, and the two spellings were
one code, not two.

*Assumption:* a grant's scope is the unit or exactly one item, and a bound operand is legal
only on an item-scope grant, so the seeded grant **cannot be one row for every event**. This
module reads it as a **seed template instantiated by the event-creation path**, which writes
one item-scope grant on each new event; the one-off import owes the same row for every event
it writes, or an imported camp's organizers cannot read that camp's answers. D-102 does not
say who writes the row. Integrity check 1 in §10 is the net.

**The preview requirement this creates.** "Who does this grant reach?" stops being a property
of a grant row once an operand binds: `PLACED` is different people on different events. The
editor must therefore compute the expansion **for an item** and name the item it computed
against, and ~~the cache key for a bound operand must include the item~~ — the answer cache that had a key is
deleted ([D-114](../decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation)),
but the rule survives it at the layer below: the item is bound at **resolution**, so nothing expanded while
computing one item may be reused for another. Stated as a requirement
in [../domain/07-events.md §7](../domain/07-events.md#7-the-people-connected-to-an-event). That expansion
is not capped or deferred, and the ground is now stated rather than assumed: a few dozen registrants on a
typical event and a big camp on the order of two hundred is a preview nobody feels — a size
**stated, not measured**, with a named trigger to reopen it
([D-112](../decisions/round-13.md#d-112--the-systems-scale-is-stated-hundreds-of-people-tens-of-registrants-per-event)).

**A write to `event_registration` is not a ruleset write — and since [D-114](../decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation)
that buys it no staleness whatsoever.** ~~There is one cache policy and three triggers — rebuilt nightly in full,
immediately on any write to the ruleset, and on explicit request — with no per-entry TTL and no invalidation table
to get right ([D-111](../decisions/round-13.md#d-111--the-permission-cache-is-rebuilt-nightly-on-any-ruleset-change-and-on-request)).
The ruleset is the grant and expression rows, the permission registry, the guardianship rows, `role_holder` and
`person_group_member`; **`event_registration` is not in it**. So marking a register, confirming a place, or
promoting somebody off the waitlist changes who is in `ATTENDED`, `PLACED`, `CONFIRMED` and `ON_WAITLIST` and
rebuilds nothing: a cached answer behind those four tiers **may be up to one night stale, by design**. This is the
module where an implementer would most confidently assume the opposite, so it is stated here rather than only in
the authorization page. What stays immediate is everything a person actually does to authority — revoke, deny,
close a grant period, end an assignment — because every one of those is a ruleset write.~~

**What is true now:** marking a register, confirming a place, flipping `is_confirmed` or promoting somebody off the
waitlist changes who is in `ATTENDED`, `PLACED`, `CONFIRMED` and `ON_WAITLIST`, and **the change is visible on the
next check** — the one after the write, with no job in between — because a check resolves the expression against
live rows and there is no cached answer left to sit behind the roster
([D-114](../decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation)).
**The same is true of `ORGANIZERS`**, which reads the organizer rows and not the registration table at all: five
bound operands, five live reads, and a birthday crossing `OLDER(n)` moves an answer on exactly the same footing as
a registration write does. **Immediacy here is by construction, not by policy:** nothing maps a person to an
answer anywhere in the schema, so there is no row that could be a night old. **And this module was right to be uneasy about the paragraph above.**
Four tiers computed from four registration tables, with the boundary of what counts drawn in a different file from
the read path it had to describe, is precisely the shape that made the cache untenable — the deletion this page
reports arrived because lists like that one omitted `membership` while `membership.terminate` ⛔ was the most
safeguarding-shaped write in the catalog. **What survives of the old vocabulary, said precisely:** a registration
write is still not a ruleset write, now in the narrowed sense that **it changes no rule's text**, and
`ruleset_version` — which keys a *compiled expression*, not an answer — is bumped by **`audience_operand` and
`selector_type`** alone, so a registration write is not a ruleset write at all now, in the only sense the phrase
still has. *"Not a ruleset write" no longer buys a night of staleness; it says which two-table bump set you are
not in, and nothing more.* **And the rule whose mechanism just went has to say who enforces it now**
([D-081](../decisions/round-06.md#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now)),
which is the question this paragraph would otherwise leave hanging: **nobody enforces it, because there is nothing
left to invalidate.** The old sentence's job — *"a registration change reaches an answer"* — is now done by the
read path itself, and a page cannot opt out of a read path the way it can forget to add a row to a list.

### Guards

**Guard 1 — the registration window.** No registration row may be created for an event whose
window does not admit it. The guard runs inside the transaction that inserts the row, on every
insert path — and since there is nothing left to attach it to, that coverage is now a requirement
on the paths rather than a property the database supplies for them. Steps 4 and 5 read the
event's own dates and step 2 exempts a source value, so no constraint states this rule and no
report would catch a violation the way a window violation should be caught: at the write.
**The order is a rule**: "there is no such event" must be settled
before anything reads the event's dates, and the staff carve-out must be answered before the
checks it overrides.

1. Read the event the registration names. If there is no such event, refuse the row — a
   registration cannot name an event that does not exist.
2. If `source` is `staff`, admit the row and stop here. Staff may always register, including
   at a cancelled event (to record who had been coming) — they are acting deliberately and
   are attributed.
3. Otherwise refuse the row if the event is cancelled (`cancelled_at` is set).
4. Refuse it if `registration_opens_at` is set and has not yet arrived.
5. Refuse it if the effective close has passed — `registration_closes_at`, or `starts_at`
   when `registration_closes_at` is absent. This is where "`NULL` = open until the event
   starts" is enforced.
6. Admit the row.

**Guard 2 — an event with registrations cannot be deleted.** Deleting an event is refused as
soon as the event has any registration row at all, and the refusal says what to do instead:
cancel it (set `cancelled_at`) so the record of who was coming survives. Cancellation is the
mechanism.

> **Guard 2 is what makes the cascade in §3 safe.** Organizers cascade when an
> event is deleted — but an event that anyone registered for cannot be deleted at all. So
> the cascade can only ever fire on a draft with no registrations, which is the only case
> where losing the roster is harmless.

---

## 9. The three queries that matter

### Who has not replied yet?

"Unanswered" is a subtraction ([../domain/07-events.md §3](../domain/07-events.md#3-registration-one-record-two-stored-answers-and-no-unanswered)).
The subtrahend is *who the event is open to* — which, for an open event, is an audience.

The question asked of one camp is: **every person who may register for it and has not
answered.** The audience is the eligible set, the registration table is the answered set, and
the answer is the difference between them, listed by preferred name. What makes the question
answerable at all:

- The eligible set is *evaluated*, not stored: it is the people named by the live **allow**
  grants of `event.register_self` — at the unit, which reaches this event, or on this event —
  through their audiences, assessed as of the day the question is asked, not as of the day the
  grant was written. A child who joined a group last week is on this list; a child who has
  left is not.
- Only live allows count, and a person against whom a live **deny** of the same code applies
  is not eligible however many allows reach them — deny is absolute, and an eligibility list
  that ignored it would chase people who were deliberately excluded
  ([D-013](../decisions/round-01a.md#d-013--explicit-deny-revoked-is-checked-before-everything)).
- Where the grant's expression contains a bound operand, the eligible set is computed
  **against this event**, which is the only thing it can mean (§8).
- The answered set is one row per person at most (§4), so the subtraction cannot leave the
  same person on the list twice.
- People who have been merged away are excluded, so a tombstone never turns up on a list
  somebody is being asked to chase.

**This is the query that would be impossible if `unanswered` were a stored value**, because
the eligible set — an audience, evaluated as a rule — is what defines the question. Storing
"unanswered" rows would mean enumerating an audience into rows, and re-enumerating whenever
a child joins a group.

### Who is actually coming?

Four numbers about one event, in one answer, all counted over that event's `attending`
registrations: how many are not waitlisted (coming), how many are waitlisted (waiting), how
many are unconfirmed and not waitlisted (holding a place without having paid), and the
event's `capacity`. An event with no registrations still has to produce the row, with zeros.

The four numbers an organizer needs, in one row: coming, waiting, holding a place without
having paid, and the limit. `attending > capacity` is the overrun, and it is visible here
rather than prevented (§10 check 5).

The first two of the four are `PLACED` and `ON_WAITLIST` counted rather than listed, and the
third is `PLACED` minus `CONFIRMED`. The selector definitions in §8 and the counts here are
one set of facts stated twice on purpose: the screen and the grant must not be able to
disagree about who "coming" means.

### Who was actually there?

For one camp, the attending registrations listed with each person's preferred name, birth
date and `was_present`, **with the unmarked listed first** — the unmarked sort ahead of both
a mark and an absence recorded as `false`, because the unmarked are the work remaining. This
is the camp roster as a safeguarding record, not a plan.

`NULLS FIRST` puts the unmarked at the top, which is the work remaining. Once every row is
`true` or `false`, this is the answer to "who was in the organization's care at that camp" —
and it is the reason `was_present` is three-valued rather than a boolean defaulting to false.

**This report has no selector twin, and that is the point.** Nothing in the selector language
computes over `was_present`, so no grant can reach fewer people because the register was
never taken. §8 states the refusal; this query is the reason it matters.

---

## 10. Integrity checks

**Invariants to verify**

1. **A bound selector on a grant that cannot bind it.** Counts live grants whose expression
   contains `ATTENDED`, `PLACED`, `CONFIRMED`, `ON_WAITLIST` or `ORGANIZERS` in argument-less
   form and whose scope is the unit, or whose scope is an item of a type other than the
   operand's `argument_type`. **Both rules are refused on the write path** (§8), so a non-zero
   result is evidence about the code, not the data: somebody added a path that saves a grant
   without going through the check, and a grant like this resolves to the empty set and
   silently authorizes nobody.
2. **An event whose organizers hold no seeded answer-view grant.** Counts non-cancelled events
   that have at least one `event_organizer` row and no live allow of `event.answer.view` on
   that event aimed at `ORGANIZERS`. The seeded grant is written by the code that creates the
   event (§8), so the failure shape is the one check 10 knows well: an event imported or
   created by a path that forgot, where the organizers cannot read the answers of the camp
   they are running, and every row they left behind is individually correct.
3. **An event with no organizer.** Counts events that are neither cancelled nor already begun
   and have no `event_organizer` row at all — an event nobody is running: either abandoned
   mid-setup, or a data-entry error. Not a rule on write, because an event is legitimately
   created before its organizers are named.
4. **A registration held by a person who has been merged away.** Counts registrations whose
   person carries a merge pointer. The merge should have repointed them; a non-zero result
   catches the ones it missed.
5. **An event running over its stated capacity.** Counts, for each non-cancelled event that
   has a capacity, its `PLACED` registrations, and reports the events where that count exceeds
   the capacity. PERMITTED — a staff registration may exceed deliberately
   ([../domain/07-events.md §8](../domain/07a-capacity-presence-and-forms.md#8-capacity-and-the-waitlist)) — so this
   is a report, not an error. A pattern of overruns means the capacity numbers are wrong, not
   that the rule is.
6. **An unpaid registration holding a place past the waitlist deadline.** Counts attending,
   non-waitlisted registrations on a non-cancelled event whose `waitlist_deadline` has passed
   and whose fee obligation stands at `unpaid`, `partially_paid` or `overdue`. It should be
   empty once the release in §5 has run — a non-empty result means the job is not running.
7. **An answer to a question the person was never registered for.** Counts answers whose
   person has no registration for the event that owns the question. Either the registration
   was deleted, or the answer was written against the wrong person.
8. **Presence marked on a registration that declined.** Counts `not_attending` registrations
   whose `was_present` is not absent. Contradictory: you cannot have been present at a thing
   you said you were not attending. Nothing above forbids the combination, so this is a
   written prohibition and a check rather than a guard — a prohibition nobody runs is a
   convention, not a guarantee.

9. **A registration outside its event's registration window.** Counts registrations whose
   `registered_at` falls before the window opens or after it closes, excluding the ones an
   organizer recorded deliberately (`source = 'staff'`, whose window is the event's own
   period). Guard 1 in §8 is supposed to make the first two shapes impossible, and
   **there is no constraint behind that guard** — a window spans two columns of two tables, so
   the check runs inside the writing transaction or nowhere
   ([F-10 shape 3](../open-questions.md#f-10--which-invariants-the-orm-cannot-express-and-who-writes-those)).
   A non-zero result is therefore evidence about the code, not the data: someone added a second
   path that places a registration.
10. **A fee-bearing event with registrations and no obligations.** Counts non-cancelled events
   that require a fee and have at least one registration, where no `fee_obligation` exists for
   some of those registrations. **The obligation is created by the code that places the
   registration** ([§6](08-events.md#6-payments-and-confirmation)); there is no rule attached to the registration row
   that would create it, so a path that forgets produces a person with a confirmed place and no
   bill — invisible to every check here, because every row it left behind is individually
   correct. Money-versus-roster reconciliation (§6) is the same discovery arriving later and
   more expensively; this is the version worth running nightly.

**Checks 1, 2 and 10 are the same shape and should be read as one warning.** Each tests
whether a piece of *code* that nothing else depends on actually ran: the grant save, the event
creation, the placing rule. Each will read empty on correct data and each is the kind of bug
that a schema change never surfaces, because every row a forgotten step leaves behind is
individually valid.

**Check 5 is the important one to read correctly.** It will produce rows, and that is not a
failure — exceeding capacity is a permitted, attributed act
([../domain/07-events.md §8](../domain/07a-capacity-presence-and-forms.md#8-capacity-and-the-waitlist)). What the
report is *for* is the pattern: an event that overruns every year has a capacity number that
is wrong, and the fix is to change the number rather than to start refusing people.

*Numbering note:* checks 1 and 2 were rewritten in place rather than dropped, and 3–10 keep
the numbers other files cite them by.

---

## 11. Open issues

Tracked in [../open-questions.md](../open-questions.md) under **G. Events**.

- ~~**The age ceiling on an open event.**~~ **Settled: there is none**
  ([D-070](../decisions/round-05.md#d-070--an-event-has-no-age-ceiling-the-grant-is-the-rule)).
  No `min_age`/`max_age` on `event`, no age branch anywhere in the registration path. If it is
  ever revisited the shape is a new **seeded selector operand**, not a column on the row.
- ~~**Whether `event.manage_participants` should split.**~~ **It did**, into
  `event.presence.mark` — no longer "a level lower", because there are no levels, but a
  separate code, which is the same protection stated in the only vocabulary D-099 leaves
  (§4, EV-5).
- **What else should be seeded to `ORGANIZERS`.** D-102 seeds `event.answer.view` and nothing
  else, so an organizer who holds no unit-scope grant can read the answers of a camp they are
  running and can do nothing else at it. Whether that is the intended shape or an omission is
  not settled, and this module has not seeded more on its own initiative (§3, §8).
- **Who writes the per-event seeded grant.** Read as a template the creation path and the
  import both instantiate; D-102 does not say (§8, check 2).
- **`WHITELISTED`.** No stored state to name, so no operand and no reserved name (§8).
- **Retention of `event_answer`.** Answers end with the event and there is no policy saying when (§7).
  This used to be argued from the answer being *health data*, which
  [D-083](../decisions/round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)
  left without a referent: it is personal data, which makes the question ordinary rather than
  answered — and sharper, since the same sentence recorded as a `person_attribute` follows a different
  retention rule on purpose ([EV-2](../open-questions.md#ev-2--retention-of-event_answer)).
- **Cancelled events and fees.** Cancelling keeps the registrations. Whether it releases the
  obligations, refunds them, or neither is the finance module's decision (§6). That decision
  has since been taken for events
  ([D-076](../decisions/round-06.md#d-076--money-that-cannot-be-matched-waits-for-a-person)):
  cancelling voids the outstanding requests and money that already arrived waits in the
  unmatched queue ([07-finance.md §2b](07-finance.md#2b-money-that-cannot-be-matched)).
- **`was_present` as a safeguarding record.** Whether presence needs its own retention or its
  own permission, given what it is (§9 of the domain doc). D-102's refusal of `PRESENT` makes
  the second half of that question sharper: presence now governs nothing about access, which
  is either why it needs no permission of its own or why its retention is all that is left.
- **Whether organizers should be `access_grant`s after all.** D-102 settled the *mechanism* —
  a set named by a selector, aimed at by grants — without changing D-062's answer that the
  roster is not itself a grant. What remains open is smaller than it used to be: whether more
  codes should be seeded to `ORGANIZERS`, which is the question above
  ([../domain/07-events.md §5](../domain/07-events.md#5-organizers-are-appointed-not-granted)).
- **Waitlist notification.** Promotion is deliberate; telling the promoted person is not
  designed. It belongs to the communication module.
