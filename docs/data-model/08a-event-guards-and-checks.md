# Data Model — Events: guards, the three queries, integrity checks

How authority reaches an event, what the module may assume, the three questions a screen asks it, and the checks that hold it together.

**Section numbers are shared across the two parts** and never renumbered, because other pages cite them by number and their anchors are built from them: [08-events.md](08-events.md) holds §1–§7, [08a](08a-event-guards-and-checks.md) §8–§11 (projections and guards, the three queries that matter, integrity checks, open issues).

---

## 8. Projections and guards

### The unit-authority rule, and `can_event()` — both deleted

**Every event check goes through the ordinary `can()` and nothing else** — or through `can_key()`, which is
that same function's other door and takes no person
([05c §10](05c-access-log-and-resolver.md#10-the-resolver)); an integration's call at `('event', 42)` is
matched exactly the same way, by an allow at the unit or on that event. There is no
`can_event(person, permission_code, event, at)` wrapper and no unit-authority rule for events:
an event is an item like any other, and the resolver matches scope exactly. The person whose
job is to run the organization's camps passes a check at `('event', 42)` because their allow is
at the unit, not because anything tested the event.

**Who enforces it — `can()`, with no event-shaped clause in it.** The only non-item scope is
the unit, and a grant at the unit reaches every item of every type
([D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)),
so there is no gap between a unit grant and one of that unit's events for anything to close.
**Why nothing closes one:** there is **no scope between the unit and an event** — nothing to
inherit through and nothing to test on the way. Authority reaches an event the same way it
reaches any other item, and an event carries no authority of its own
([D-102](../decisions/round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)).

### Selectors that bind to an event

Five sets describe the people connected to an event, and each is a **selector that binds to
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
checked. **There is no sixth operand, and nothing guardian-shaped can become one.** A guardian's
authority is a `right_level ∈ none | view | write` held **over a child**, read off the
`guardianship` row when the check is about someone other than the actor; it is not a set that
the expression language resolves, and `GUARDIANS` is not a row of `selector_type` in either
spelling
([D-113](../decisions/round-13.md#d-113--the-guardianship-channel-has-no-expression-guardians-is-not-a-selector),
[D-074](../decisions/round-06.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular)).

**`PRESENT(<event>)` is refused.** An operand over `was_present` is the obvious sixth
attendance tier and it is not available, and the reason is the failure direction:
`was_present` is `NULL` until somebody takes a register, so a grant aimed at `PRESENT` would
revoke a child's access to their own camp photos because a volunteer forgot to tick a box.
The column is a safeguarding signal and is three-valued on purpose
([D-067](../decisions/round-05.md#d-067--presence-is-a-three-valued-fact-on-the-registration));
keeping it out of the selector language is what keeps it meaning "a person recorded this"
rather than "this is who may see things". Where presence is needed it is needed as a report
(§9), and the report is honest about the rows it does not have.

**`WHITELISTED` does not exist, and nothing reserves the name.** There is no stored state to name:
the nearest facts are `source = 'staff'` (an organizer entered them) and promotion off the waitlist.
**A tier is a state of a registration, and an invitation is not about a registration at all** —
*invited* is a grant aimed at that person, a person who never registered is described by the absence
of a row ([D-059](../decisions/round-05.md#d-059--unanswered-is-the-absence-of-a-row-a-registration-stores-two-values)),
and one who registers onto a full event is already `ON_WAITLIST`. So the need is met by rows that
exist and this is settled rather than pending: no `is_whitelisted` column, no fifth tier, no operand,
and **anyone adding `is_whitelisted` is reimplementing grants badly**. The sentence belongs where the
tiers are listed, beside the `PRESENT` refusal, and it stands there in
[../domain/07a §9](../domain/07a-capacity-presence-and-forms.md#9-presence-what-actually-happened)
([D-148](../decisions/round-20.md#d-148--there-is-no-whitelisted-and-the-refusal-is-written-where-the-tiers-are)).
**The count of operands refused here does not move**: `WHITELISTED` was already one of the operands
this table does not hold.

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

**The twelve grants an event arrives with, one of which is `event.answer.view` on `ORGANIZERS`.**
"Answers are read by that event's organizers"
([D-061](../decisions/round-05.md#d-061--event-answers-are-read-by-that-events-organizers))
is a row in `access_grant`, not a clause in the resolver: authority over an event lives in
grant rows, and so does this. It is aimed at a **set**, so it does not contradict
[D-062](../decisions/round-05.md#d-062--organizers-are-appointed-on-the-event-not-granted)
and does not make `event_organizer` a grant table: adding a cook to the roster changes a set,
and the grant keeps pointing at the set. The registered spelling is the catalog's
`event.answer.view`, singular *answer*; `event.answers.view` is that one code misspelled, not a
second code. **It is not alone and it is not shipped:** the act that creates an event writes
**one item-scope allow per event code** beside the event row, in the same transaction, each aimed at an
audience whose expression is the bare operand `ORGANIZERS` — every `event.*` code whose `applies_to`
admits an event, which is all thirteen of them but `event.create`, held at the unit because nothing owns an
event. **Twelve rows, derived rather than curated**, so the list cannot drift from the catalog the way a
hand-written one does
([D-151](../decisions/round-21.md#d-151--creating-an-event-writes-the-events-authority-and-its-organizers-may-grant-on-it)).

**Who writes them, which is the question D-102 left open and this section used to hedge.** The person
creating the event, through the create; the import, once per event it writes, or an imported camp's
organizers cannot read that camp's answers. **Nothing ships either row**, so the module no longer reads a
"seed template" — the row-count question that made a template necessary was that a bound operand is legal
only on an item-scope grant, so **one row could never cover every event**, and per-event rows are what the
check has always counted. That is also the correction this round owed
[05d §12](05d-invariants-and-seed.md#12-what-day-one-looks-like), which claimed the opposite in as many
words. **What the bundle contains besides the answer row is the part to read twice:** `event.grant_access` is
in it, so whoever runs an event may grant access to *that* event without holding `access_grant.create` at
the unit, and `event.organizer.manage` is in it, so an organizer may add an organizer and widen all eleven
others. The ceiling on both is the scope and `applies_to` — `system.admin` is unit-only and cannot be
written onto an item at all, which is the guarantee D-099 left behind when it deleted the levels.
**Integrity check 2 in §10 is the net for a missing bundle, and check 1 for a grant saved at a scope that
cannot bind it.**

**The preview requirement this creates.** "Who does this grant reach?" is not a property of a
grant row once an operand binds: `PLACED` is different people on different events. The
editor must therefore compute the expansion **for an item** and name the item it computed
against. The same bound holds inside a check: the item is bound at **resolution**, so nothing
expanded while computing one item may be reused for another. Stated as a requirement
in [../domain/07-events.md §7](../domain/07-events.md#7-the-people-connected-to-an-event). That expansion
is not capped or deferred: a few dozen registrants on a
typical event and a big camp on the order of two hundred is a preview nobody feels — a size
**stated, not measured**, with a named trigger to reopen it
([D-112](../decisions/round-13.md#d-112--the-systems-scale-is-stated-hundreds-of-people-tens-of-registrants-per-event)).

**There is no permission cache.** A check resolves; a request memoizes; the only cached thing is
a compilation — an expression root plus `ruleset_version`, holding no person and no item
([D-114](../decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation)).
`ruleset_version` keys that compilation, not an answer, and it is bumped by **`audience_operand`
and `selector_type`** alone: a write to `event_registration` changes no rule's text and is not a
ruleset write.

**So a registration write is visible on the next check.** Marking a register, confirming a place,
flipping `is_confirmed` or promoting somebody off the waitlist changes who is in `ATTENDED`,
`PLACED`, `CONFIRMED` and `ON_WAITLIST`, and the change is visible on the check immediately after
the write, with no job in between, because a check resolves the expression against live rows. The
same is true of `ORGANIZERS`, which reads the organizer rows and not the registration table at
all: five bound operands, five live reads, and a birthday crossing `OLDER(n)` moves an answer on
exactly the same footing as a registration write does. **This immediacy is by construction, not
by policy:** no row anywhere in the schema maps a person to an answer
([invariant 19](05d-invariants-and-seed.md#11-invariants-to-verify)), so no answer can lag the
rows it is computed from.

**Who enforces "a registration change reaches an answer" — nobody, because there is nothing left
to invalidate**
([D-081](../decisions/round-06.md#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now)).
The read path does it, and a page cannot opt out of a read path the way it can forget to add a
row to a list.

### Guards

**Guard 1 — the registration window.** No registration row may be created for an event whose
window does not admit it. The guard runs inside the transaction that inserts the row, on every
insert path — which makes that coverage a requirement on the paths, not a property the database
supplies for them. Steps 4 and 5 read the
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

Four numbers an organizer needs about one event, in one row, all counted over that event's
`attending` registrations: how many are not waitlisted (coming), how many are waitlisted
(waiting), how many are unconfirmed and not waitlisted (holding a place without having paid),
and the event's `capacity` — the limit. An event with no registrations still has to produce the
row, with zeros. `attending > capacity` is the overrun, and it is visible here rather than
prevented (§10 check 5).

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

**Nor does the column have a clock of its own or a permission of its own, and that is a ruling.**
Presence is a column of a registration and inherits everything a registration is: the retention
registrations have, which is no expiry and no clock, and the codes that already reach the roster and
the mark ([D-147](../decisions/round-20.md#d-147--presence-stays-on-the-registration-no-clock-of-its-own-no-permission-of-its-own)).
A `presence.retention` shorter than the event's was refused because it would delete the answer to this
query on somebody's number, and a `presence.view` narrower than the roster's was refused because it
would be a permission whose whole purpose is to hide a fact from the people who are asking because
they were there. **There is no `presence_record` table and nothing behind this roster is a register:**
this system keeps no safeguarding register — no background checks are recorded
([D-043](../decisions/round-02-03.md#d-043--no-background-checks-are-recorded-in-this-system))
and there is no medical record
([D-083](../decisions/round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data))
— and a column with a special clock and a special permission would have been the first wall of an
archive this design has refused four times. **What protects the column is that it is boring:** the
index behind this query (§4) serves a report and no operand, the rows are readable with the codes that
reach the event, and erasure reaches them the way it reaches organizational history — the person stops being
identifiable and the mark stays ([00-conventions §8](00-conventions.md#8-personal-data-and-erasure)).

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
2. **An event whose organizers do not hold the twelve.** Counts non-cancelled events for which
   any of the twelve is missing — a live `allow`, on that event, of each `event.*` code except
   `event.create`, aimed at an audience whose expression is the bare operand `ORGANIZERS` (§8).
   **Every event is counted, not only events that already have an organizer row:** the twelve are
   written at the create, while that set is still empty, so an event nobody has staffed yet is owed
   all twelve already. The report names **which** of the twelve are missing, because eleven of a
   bundle is the same defect wearing different clothes — a missing `event.answer.view` means the
   organizers cannot read the answers of the camp they are running (⚠⚠, and the row this report was
   originally written for), a missing `event.manage_participants` means they cannot fix the roster at
   the gate. The failure shape is the one check 10 knows well: an event imported or created by a path
   that forgot, where every row it left behind is individually correct. **Since
   [D-151](../decisions/round-21.md#d-151--creating-an-event-writes-the-events-authority-and-its-organizers-may-grant-on-it)
   this report has an author to name:** an event arrived without its bundle through some one create or
   some one batch, which makes it a bug report about a path rather than about a missing migration. The
   count is the same either way, and so is the camp whose organizers cannot read anything.
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
   ([../domain/07a-capacity-presence-and-forms.md §8](../domain/07a-capacity-presence-and-forms.md#8-capacity-and-the-waitlist)) — so this
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
   `created_at` — the moment the row was written, which is the moment Guard 1 governs, and not
   `responded_at`, which is when the answer was given — falls before the window opens or after it
   closes, excluding the ones an organizer recorded deliberately (`source = 'staff'`, whose window is
   the event's own period). Guard 1 in §8 is supposed to make the first two shapes impossible, and
   **there is no constraint behind that guard** — a window spans two columns of two tables, so
   the check runs inside the writing transaction or nowhere
   ([shape 3](00a-invariant-register.md#3-the-answer-reads-another-table-a-resolver-or-a-graph)).
   A non-zero result is therefore evidence about the code, not the data: someone added a second
   path that places a registration.
10. **A fee-bearing event with registrations and no obligations.** Counts non-cancelled events
   that require a fee and have at least one registration, where no `fee_obligation` exists for
   some of those registrations. **The obligation is created by the code that places the
   registration** ([§6](08-events.md#6-payments-and-confirmation)); there is no rule attached to the registration row
   that would create it, so a path that forgets produces a person with a confirmed place and no
   bill — invisible to every check here, because every row it left behind is individually
   correct. Money-versus-roster reconciliation
   ([07-finance.md §2](07-finance.md#2-minimal-provisional-shape)) is the same discovery arriving later and
   more expensively; this is the version worth running nightly.

**Checks 1, 2 and 10 are the same shape and should be read as one warning.** Each tests
whether a piece of *code* that nothing else depends on actually ran: the grant save, the event
creation, the placing rule. Each will read empty on correct data and each is the kind of bug
that a schema change never surfaces, because every row a forgotten step leaves behind is
individually valid.

**Check 5 is the important one to read correctly.** It will produce rows, and that is not a
failure — exceeding capacity is a permitted, attributed act
([../domain/07a-capacity-presence-and-forms.md §8](../domain/07a-capacity-presence-and-forms.md#8-capacity-and-the-waitlist)). What the
report is *for* is the pattern: an event that overruns every year has a capacity number that
is wrong, and the fix is to change the number rather than to start refusing people.

*Numbering:* the numbers of checks 1–10 are cited from other files; they are not reassigned.

---

## 11. Open issues

Tracked in [../open-questions.md](../open-questions.md) under **G. Events**.

- **The age ceiling on an open event: there is none**
  ([D-070](../decisions/round-05.md#d-070--an-event-has-no-age-ceiling-the-grant-is-the-rule)).
  No `min_age`/`max_age` on `event`, no age branch anywhere in the registration path. If it is
  ever revisited the shape is a new **seeded selector operand**, not a column on the row.
- **`event.manage_participants` and `event.presence.mark` are two codes.** Marking a register is
  a separate code, not a level below the roster — there are no levels — which is the same
  protection stated in the only vocabulary D-099 leaves
  ([D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality);
  §4, EV-5).
- **What else an organizer should hold — settled: everything the event has, on that event.** The question
  was asked because D-102 shipped `event.answer.view` alone, leaving an organizer who held no unit-scope
  grant able to read the answers of a camp and able to do nothing else at it, which read as an omission and
  was not resolved by this module adding rows on its own initiative. **It is resolved by not seeding
  anything:** the create writes one allow per event code whose `applies_to` admits an event, so the answer to
  "what may an organizer do?" is twelve rows anyone can list, and the answer to "what may an organizer do
  *elsewhere*?" is nothing, which is the shape D-100 says an office has anyway (§3, §8,
  [D-151](../decisions/round-21.md#d-151--creating-an-event-writes-the-events-authority-and-its-organizers-may-grant-on-it)).
- **Who writes the per-event grant — settled: the create, and the import.** This used to be answered as "a
  template the creation path and the import both instantiate", with the observation that D-102 does not say
  (§8, check 2). **There is no template, because there is no seed** — the rows are ordinary grants written in
  the event's own transaction by whoever holds `event.create`, and the import owes twelve of them for every
  event row it writes
  ([D-151](../decisions/round-21.md#d-151--creating-an-event-writes-the-events-authority-and-its-organizers-may-grant-on-it)).
- **Retention of `event_answer` — settled: nothing expires, and erasure empties the value.** Neither a
  registration nor an answer ends with its event, and neither ends on a clock; what reaches an answer
  is erasure, which sets `value` to empty and leaves the row (§7,
  [00-conventions §8](00-conventions.md#8-personal-data-and-erasure)). The asymmetry this question
  rested on — the same fact kept indefinitely as a `person_attribute` and quietly discarded as the
  answer a camp leader reads — is closed by making the two rules agree, which is the stronger answer
  than the clock it replaces ([D-083](../decisions/round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data),
  [D-140](../decisions/round-20.md#d-140--nothing-about-an-event-is-deleted-on-a-schedule-and-erasure-empties-an-answer-without-deleting-it);
  [EV-2](../open-questions.md#ev-2)).
- **Cancelled events and fees.** Cancelling keeps the registrations. What it does to the
  obligations is the finance module's (§6), and for events it has an answer
  ([D-076](../decisions/round-06.md#d-076--money-that-cannot-be-matched-waits-for-a-person)):
  cancelling voids the outstanding requests, and money that already arrived waits in the
  unmatched queue ([07-finance.md §2b](07-finance.md#2b-money-that-cannot-be-matched)).
- **`was_present` as a safeguarding record — settled: it stays a column of the registration.** No
  retention of its own and no permission of its own: it inherits both from the registration, and the
  codes that already reach the roster are the codes that read it (§9). `PRESENT` stays refused, so
  presence governs nothing about access, and no `presence_record` table is coming either, because
  **this system keeps no safeguarding register** — no background checks are recorded
  ([D-043](../decisions/round-02-03.md#d-043--no-background-checks-are-recorded-in-this-system)),
  no medical record exists
  ([D-083](../decisions/round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data))
  — and a clock plus a permission would have been the first wall of one
  ([D-147](../decisions/round-20.md#d-147--presence-stays-on-the-registration-no-clock-of-its-own-no-permission-of-its-own);
  [EV-4](../open-questions.md#ev-4)).
- **Whether organizers should be `access_grant`s after all.** The mechanism is settled —
  a set named by a selector, aimed at by grants — and D-062's answer stands: the roster is not
  itself a grant. What used to hang off that question — whether more codes should reach `ORGANIZERS` — is
  settled beside it, by the create writing the event's whole code family onto the event
  ([../domain/07-events.md §5](../domain/07-events.md#5-organizers-are-appointed-not-granted)).
- **Waitlist notification.** Promotion is deliberate; telling the promoted person is not
  designed. It belongs to the communication module.

---

*Decisions behind this page: D-013, D-043, D-059, D-061, D-062, D-067, D-070, D-074, D-076, D-081, D-083, D-099, D-101, D-102, D-112, D-113, D-114, D-140, D-147, D-148.*
