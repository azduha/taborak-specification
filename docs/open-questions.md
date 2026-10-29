# Open Questions

Everything still unresolved — fifteen questions, each with its **schema impact**, what changes
once you answer, ordered roughly by how much they block.

Marked: 🔴 **blocking** something else · 🟡 **important** · 🟢 can be deferred.

**A question that has been answered is not kept here.** Its entry is deleted; what remains is one
row in [§ R. Resolved](#r-resolved--moved-to-the-decision-log) naming the question, the decision
that settled it and what the answer cost, and the reasoning lives in that decision entry. Nothing
is silently dropped: a row in § R carries a short anchor, so a link written years ago against
`F-7` still lands somewhere true.

**The section letters are names, not a sequence.** Sections B, C and D held only closed questions
and are gone, but the ids they held — `B-2`, `C-5`, `D-9` — are still how § R means them, and `E-6`
is still the question it was when it was filed.

[§ I](#i-assumption-index) lists every assumption the documentation is standing on;
[§ How to answer](#how-to-answer) says which of these is worth answering next.

---

## A. Blocking the core design

### A-4 (remainder) 🟢 The organizational calendar

**Answered.** The fee expires on **1 January**
([D-047](decisions/round-04.md#d-047--the-fee-expires-on-1-january)) and the renewal
window is **60 days** ([D-048](decisions/round-04.md#d-048--the-renewal-window-is-60-days-and-is-a-configuration-parameter)).

**What is left is not a question but a discipline.** Both values live in
`membership_type` as columns — `expiry_month`, `expiry_day`, `renewal_grace_days` — so either
can be moved by an `UPDATE`. The one way to lose that property is a scheduled job or a front
end that contains the literal `60` or `1`. Worth one line in code review: *do these values
come from the row?*

**See:** [data-model/03 §1](data-model/03-membership.md#1-membership_type--one-row-kept-as-a-table),
[domain/05 §6](domain/05-membership-lifecycle.md#6-renewal-and-the-yearly-fee)

---


## E. Guardianship

### E-6 🟡 A guardian may appoint a guardian

**Raised by closing E-5.** D-073 lets a guardian add another guardian, so anyone with authority
over a child can hand that same authority to a second person **with no approval from the
organization**. The ordinary case is a mother adding the father. The design does not prevent the
non-ordinary case; it attributes it — who added whom, when, from which account, audited, with the
other party notified.

**The open question is whether attribution is enough**, and specifically whether adding a guardian
over a **minor** should also notify somebody at the organization beyond the audit log. A child
gaining a second legal stranger with `write` over their records is not the same kind of event as an
adult adding a co-parent.

**Recommendation.** Notify a safeguarding contact on `guardianship.assign` where the subject is a
minor, and nothing else. Notification is visibility, not approval, so the parties still do not need
the organization's permission — which is the whole point of D-073.

**Impact.** One notification rule. No schema change.

### E-3 🟢 Guardian acting for an adult child

**Question.** Can a parent register their adult child for an event, with the child's consent?

**Recommendation.** An explicit consent-based delegation, not a guardianship — the legal
basis differs and `access_grant.is_delegated` already supports it.

**Note.** Now that grants can target **audiences**
([D-042](decisions/round-02-03.md#d-042--grants-may-target-audiences-not-only-individuals)),
the *event-wide* version of this question — "register everyone in this group" — is answered
without touching guardianship at all. What remains is the individual case.

---

## F. Authorization

### F-8 🟢 Retention policy for `access_log`

**Question.** How long do the login and authorization-decision rows live?

**This entry used to answer itself, in the wrong direction.** It said: partition monthly, archive to
cold storage, **never deletion**. That is right about the *rows* and wrong about everything else, and
the mistake is the same one [D-088](decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)
made salient for `audit_log`: a retention policy stated as one number silently decides what the row
*contains*, which is the part with the person data in it.

**Proposed — and it is a proposal awaiting you, not a position these documents hold:** `access_log`
takes the **same window as `audit_log`'s payloads, 24 months**, with rows kept and their contents
emptied on the same schedule, because a trail of *who was allowed to see what* that outlives the trail
of *what was actually changed* answers the interesting half of an incident and not the other half.
Monthly partitioning survives as the mechanism; it is how the window gets applied cheaply, and it was
recommended long before anybody decided on a window.

**Why the question is structurally weaker here than it is for `audit_log`.**
[05-authorization §9](data-model/05c-access-log-and-resolver.md#9-access_log) keeps the *contents* of a read out of
this table to begin with — it records that a permission was exercised, not what was on the screen — so
there is no payload-expiry argument and no long-history loss to weigh. What remains is the ordinary
tension: a security review wants the login trail back to the start of the system, and a privacy review
wants a record of somebody's late-night browsing to stop existing eventually.
**Inverting the arithmetic is worth noticing:** the original "never deletion" made this table outlive
the person record it describes; the proposal makes it shorter-lived than the business rows, which is a
different objection and a defensible one.

**Needed.** Your confirmation of the 24 months, and the same legal review assumption 49 registers —
which now has both clocks in front of it rather than one.

**Impact if unanswered.** Neither table can be shrunk afterwards without a migration over the two
largest tables in the system, and the first time anybody wants to answer "how long have people been
able to read this?" the honest answer is that nobody wrote down when the logging started.

**See:** [data-model/05 §9](data-model/05c-access-log-and-resolver.md#9-access_log),
[D-088](decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short).

---

### F-9 🟢 Should `membership_type` stay a table with one row?

**Question.** [D-037](decisions/round-02-03.md#d-037--exactly-one-membership-type-the-fee-is-flat-and-per-person)
kept `membership_type` as a table with a single seeded `member` row, on the principle that
vocabularies are rows and not enums — at the cost of an FK that always holds one value.

**Impact.** A deliberate trade, not an oversight. Worth confirming it is the trade you want,
since it is the one place the design pays a structural cost for a hypothetical future.

**See:** [data-model/03 §1](data-model/03-membership.md#1-membership_type--one-row-kept-as-a-table)

---

### F-10 🟡 Which invariants the ORM cannot express, and who writes those

**Question.** [D-072](decisions/round-06.md#d-072--the-documentation-carries-no-sql-the-schema-is-the-orms-job)
moved the schema to an ORM. Most of what the deleted DDL asserted an ORM will generate from a
model definition. **Four shapes it generally cannot**, and each appears dozens of times in these
documents.

The four are not equally bad, and round 10 moved them in opposite directions, which is the reason this
entry changed colour. **Shapes 1, 2 and 3 gained instances** — the round that deleted the hierarchy spent
itself inventing new temporal tables and a new expression language. **Shape 4 lost its only instance,** and
shape 4 was the entire reason this question was red.

1. **No two open rows overlap** — the temporal invariant under memberships, guardianships, grants, and —
   **new** — `person_group_member` (D-098) and `role_holder` (D-100). On PostgreSQL this needs an exclusion
   constraint over a range built from two columns. **The two new ones are stricter than the idiom is
   usually generated:** both state *"may not overlap, counted over all rows and not only the open ones"*,
   which is the opposite of the partial-index habit this shape normally pairs with. An ORM that generates
   the familiar "one open row per key" version silently permits the overlapping closed row that a group
   member's history is full of, and the imported corpus guarantees one.
2. **Unique, but only among rows satisfying a condition** — "one open request per person and type", "one
   primary contact among open rows", and **new**: `audience.code` **unique where set**
   ([D-103](decisions/round-10b.md#d-103--an-audience-may-name-another-audience)), because naming an
   audience is optional and most audiences are a grant's private addressee list. These need a partial unique
   index; a plain unique constraint over the same columns is a *different and wrong rule*, forbidding the
   second `NULL` that history requires — and here it would forbid **every** unnamed audience, which is most
   of them. Gone: "one live exposure per unit and assignment", with `scope_exposure` (D-097).
3. **Anything whose answer comes from another table or from the resolver** — this is where round 10 worked,
   and it had **five** instances where it had three; round 11 added a **sixth**, and it is the first one whose
   subject is a column that *deliberately* has no key to follow:
   - *Gone:* the holder limit (`max_holders`, deleted with positions, D-100), the nesting rules and the
     exposure direction (both D-097). Naming them keeps the count honest.
   - *Kept:* per-scheme identifier uniqueness
     ([D-080](decisions/round-06.md#d-080--five-contradictions-the-translation-surfaced-and-how-each-was-resolved)
     item 1 is this class), and **one current value per `(person, definition)`**, whose condition lives in
     `attribute_definition.allow_multiple` — a uniqueness rule some definitions want and others forbid
     ([data-model/09-attributes.md §3](data-model/09-attributes.md#3-person_attribute--a-value-one-person-has)).
     It stays the cleanest example in the list: the same two columns are unique for one definition and
     repeatable for the next, so no partial index can be written without knowing which definitions exist at
     runtime.
   - *New — requiredness conditioned on another table:* an `audience_operand` leaf must carry
     `selector_arg_id` exactly when its selector's `takes_argument` is true, and must leave it null exactly
     when the operand **binds** to the item
     ([D-102](decisions/round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)).
     The condition is a value in `selector_type`, three tables away from the row it constrains, so
     `NOT NULL` cannot state it and the arity check has to.
   - *New — a check that reads another table:* an `AUDIENCE(...)` leaf **may not point at an audience whose
     `code` is null** (D-103; §11 check 12 of
     [data-model/05](data-model/05d-invariants-and-seed.md#11-invariants-to-verify)). Nothing about the operand row
     tells you this; only the row it references does. The same class carries the **name namespace**, now
     spanning `role`, `person_group` and `audience.code` with every `selector_type.code` reserved against it
     — **no single constraint spans three tables and a fourth table's values**, so the write path carries it
     and check 12 only asserts that the write path exists.
   - *New, and the mirror image of the rest:* **two rows that must coexist.** Creating an `event` obliges an
     instantiated `event.answer.view` grant aimed at `ORGANIZERS` (D-102) — one row in one table requiring a
     row in another, in one transaction, with nothing in either schema stating the debt. A constraint can
     forbid a missing child or an orphan parent; it cannot make an `INSERT` in `event` write a row in
     `access_grant`. The backstop is the *events with no answer-view grant* report, and **an organizer whose
     event arrived without its grant is a person with a title and no permissions** — which reads as a bug
     report, not a constraint violation. The legacy import owes one per event row, so the first occurrence of
     this is expected in bulk, not at the margins.
   - *New in round 11, and the first whose subject is a column with no key on purpose:* **a person merge or a
     redaction must repoint every `audience_operand` leaf whose `selector_arg_id` names the absorbed or erased
     person** ([D-105](decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)).
     The column carries no foreign key by design
     ([D-011](decisions/round-01a.md#d-011--scope_id-on-access_grant-is-polymorphic-with-no-foreign-key)'s
     accepted trade-off), so there is no cascade to inherit and no key for an ORM to walk: the merge
     reassignment table gains the row, the erasure path gains the scan, and both have to reach **all five
     argument kinds** — `person`, `role`, `person_group`, `event`, `audience`. Nothing in the schema notices a
     missed leaf. The nightly orphan check becomes the backstop rather than the only mechanism, and the failure
     is this module's quietest one: **a subtraction that stops subtracting**, because a leaf resolving to
     nobody is the empty set and an empty set behind a `-` makes the result wider. Until this round the
     hand-named people lived in a table that *did* have a key, which is the only reason the instance is new
     rather than long overdue.
4. **A column that may not change once it is set** — its only named instance is **gone**:
   `org_unit.parent_unit_id`
   ([D-036](decisions/round-02-03.md#d-036--units-cannot-be-reparented-a-unit-that-moves-is-a-new-unit))
   was deleted by [D-097](decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row),
   so **this shape is currently empty**. That is a fact about the corpus, not a proof, and the two candidates
   left are worth naming because they were previously hiding behind the dead one:
   `permission.code` — the catalog's own words are *"adding one is free, renaming one is a migration"*, and
   nothing in a schema enforces a migration — and `audience.code` **once something names it**, since
   `AUDIENCE(code)` resolves through that column and a rename rewrites every expression that reached it,
   which is exactly what rule 5 of the name namespace promises does *not* happen for names.

   **What made this shape different from 1–3 was that there is no report,** and that is the half worth
   re-examining rather than inheriting. A reparent left no offending row: every row stayed individually
   valid while the meaning of a subtree's history moved under it, and the `path` the damage would show up in
   was itself derived and would simply be recomputed to match. `audience.code` has a report — *which grants
   name this audience, and at what depth* — and D-103 requires the editor to show it before saving an edit.
   So shape 4 is **no longer the shape with no evidence**, provided that listing is cheap: see
   [F-16](#f-16). `permission.code`
   needs the same query over a different table and nobody has written either. **This entry is 🟡 rather than
   🔴 on exactly that condition, and 🟡 is a bet, not a measurement.**

**Why this is a question and not a task.** The fallback an ORM offers for all four is validation in the
model layer, and
[data-model/00 §6a](data-model/00-conventions.md#6a-who-enforces-an-invariant-now) explains why
that is not the same guarantee: an import, a data fix, and a second client all bypass it. **The
legacy import is the specific case that makes this urgent rather than theoretical** — the corpus
arrives through exactly the path that model-layer validation does not cover, and an overlapping
membership written by the importer is nearly impossible to diagnose afterwards, because the two
rows look like two memberships and only one of them was ever real. Round 10 gave the import two more of
these: **consecutive dated periods for the same person** in whatever table ends up holding them (shape 1),
and **one answer-view grant per event row it creates** (shape 3) — a debt the importer owes in bulk, whose
first failures will therefore also arrive in bulk. Add the third new graph rule to shape 3's list while the
section is open: **a cycle across audiences is refused at save by a reachability walk over the reference
closure** (D-103), which is a rule about a graph spanning two tables and is the least constraint-shaped
thing in the model.

**Needed.** A decision per shape — hand-written migration, database check, or application check
plus report — before the first migration is generated, not discovered during one. **The
recommendation in [data-model/00 §6a](data-model/00-conventions.md#6a-who-enforces-an-invariant-now)
is that shapes 1 and 2 are hand-written migrations, and that this is the condition on which using
an ORM is safe rather than an argument against using one.** Shape 3 needs one more thing than a decision:
its checks are the only enforcement the selector language has, so **the arity and null-argument checks have
to be written before the first expression is saved**, and the §11 list in
[data-model/05](data-model/05d-invariants-and-seed.md#11-invariants-to-verify) — renumbered for round 10, several
checks having lost their subjects — is a review instruction rather than a test.

**Impact if unanswered.** Not a crash. A system whose constraints are quietly absent, whose
integrity checks (every "Invariants to verify" section) then start reporting rows, and whose first
report is read as a data-quality problem rather than as the missing guarantee arriving on schedule.

**See:** [data-model/00 §6a](data-model/00-conventions.md#6a-who-enforces-an-invariant-now),
[appendix/erd.md's inventory](appendix/erd.md), which marks every temporal entity.

---

### F-11 🟢 Does the identity reviewer need to *read* the person record to settle a claim?

**Question.** [D-089](decisions/round-07-08.md#d-089--one-live-account-a-colliding-sign-up-files-a-claim-and-creates-nothing)
routes a colliding sign-up to `identity_reviewer` and resolves it with `person.merge`. The seed role
holds `person.merge`, `import.view` and `import.apply` — and **not** `person.view`. So a reviewer
decides "is this the same child?" from match signals, names and dates, without opening either record.

**Why this is a question now and was not one before.** Merging already needed a human, but the
alternative to merging was doing nothing: a wrong call left two rows side by side, visible in the
nightly duplicate report, correctable next quarter. The activation gate changed the stakes. A reviewer
who *rejects* a hypothesis lets an account go live; one who *confirms* it joins two lives, including a
login, into one row. **Both directions now have a person waiting on the far side of the answer**, which
is a different job from tidying a queue, and a job the permission set does not obviously cover.

**Positions.**
- **Leave it** — the signals are the decision, and a reviewer who needs to read both records is a
  reviewer who is about to merge on a hunch anyway. Cheapest, and consistent with "identity is what the
  match says, adjudicated by a person".
- **Grant `person.view` to `identity_reviewer`** — settles it, and quietly makes an identity role one of
  the roles that can read a child's whole record, which is a bigger thing than the role's name suggests
  and is exactly what the catalog's top tier is reserved for.
- **A narrower read the catalog does not have yet** — the resolver code that would expose only the two
  candidate rows and their signals, which would be a new code and therefore a decision entry, not an
  edit to this file. **It is not proposed here, and would need arguing.**

**Recommendation.** Leave it, and watch the queue rather than the design. If reviewers start resolving
hypotheses at a suspiciously high confirmation rate without asking for context, that is the sign the
signals are not enough — and the honest response is a `person.view` grant discussed as a top-tier
membership, not a new code invented at a desk.

**Needed.** Nothing before implementation. Revisit when the first real import has produced a real queue.

---

### F-18 🟢 Does a role record elected versus appointed, and what does an election write?

**Raised as a loss by [D-100](decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape),
not as a feature request.** `position` carried `is_leadership`, `min_age`, `max_holders` and a
`position_assignment` row, and the corpus's organization keeps an elected committee. Those columns are deleted,
so the model now has **one kind of office** and cannot distinguish "elected for a two-year term by a vote"
from "appointed by whoever holds `role.assign`". `role_holder` has `valid_from`, `valid_to`, `granted_by` and
`note`, which is *nearly* enough to describe an election — and `granted_by` names the person who wrote the
row, which for an election is a secretary, not a mandate.

**Question.** Does a `role` say elected or appointed; and if so, what does an election **write** — one
`role_holder` row whose `note` says who voted, a document attached to the row, or a row in a table that does
not exist yet?

**Why it might be nothing.** An election is an event in the world that the system **records**, not a process it
**runs**: there is no ballot, no candidate table and no quorum rule anywhere in these documents, and D-043
settled that this system does not hold background checks either — it is not the registry of everything true
about a volunteer. `note`, `valid_from`, `valid_to` plus a `document` answer "we voted and here is the
minutes", and `is_system` keeps the seeded offices distinct from the organization's invented ones. **A
convention, not a guard**: nothing will ever refuse to appoint someone to an office the bylaws reserve for an
election.

**Why it might be something.** Two things the deleted tables answered by construction now have no answer at
all: **the vacancy question** (`max_holders` made "two chairpersons is one too many" a check) and the
**term-limit question** (`role.max_term_months` is a per-role cap, not an electoral rule — a two-year term
renewable once is a different claim from "may hold for at most 24 months"). Both recur in a Scout-like body
with annual meetings, and both will arrive as one-off questions.

**Positions.** Nothing — `note` and a document (cheapest, defensible, and consistent with the round's
direction); a boolean on `role` that says only **how the office is filled**, which answers the bylaws question
and writes nothing new; or an `election`/`appointment` record, which is a new module and therefore a decision
entry with an actual argument in it, not a column added here.

**Schema impact.** Either zero, one boolean on `role`, or a table plus its permission codes plus its audit
behaviour. **The boolean is not free either**: it invites a check ("may a non-elected holder be written for
an elected office?") which D-100's posture — opt-in, review by report — would refuse to enforce, and a column
nobody enforces is a column that lies after the first exception.

**Needed.** Not before implementation. Before the first AGM, which is when somebody asks whether the system
can show that the current chair was elected.

---

## G. Events — designed, with three things left open

The module is written: [domain/07-events.md](domain/07-events.md) and
[data-model/08-events.md](data-model/08-events.md). Fifteen questions have been answered
(D-058 … D-067, plus EV-1 and EV-5 in a later round); what remains below is what those answers
did **not** settle. None of it blocks implementation.

### EV-2 🟡 Retention of `event_answer`

**The question, restated once so it stays answerable.** It used to read "a dietary answer citing a
medical condition is health data, and health data has a retention obligation" — and
[D-083](decisions/round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)
removed the second half of that sentence's subject: there is no class of health data with its own
obligation, only personal data, of which a dietary answer is one instance. **The question survives, and
it is now the ordinary version of a question this system has not answered anywhere**: event answers end
with the event, "end" is not a defined policy, and a fact recorded on a form is the same kind of fact as
the same sentence recorded as a `person_attribute` ([data-model/09-attributes.md](data-model/09-attributes.md)),
which raises the sharper form of the question — **should an answer about a child be deleted on a
schedule at all, when the same information held as an attribute is kept until someone retires it?** The
paragraph at the end of this item is where that doubling is worked out; what changed here is only that
the question can no longer be filed under a category of data that no longer exists.

**Why it is not trivial.** [D-061](decisions/round-05.md#d-061--event-answers-are-read-by-that-events-organizers)
made an event form the route by which a camp leader learns a child has a nut allergy. That is
a deliberate widening, and it puts health-adjacent data in a table whose protections are weaker
than the health record's — **and in round 6 that gap widened twice over**: there is no longer a
`dependent.medical.*` code marking which data is the sensitive kind (**E-7**), and the audience
entitled to read an answer is whoever runs that event, a set sized by whoever creates it.
The retention policy is the remaining half of that trade.

**Needed.** Legal input, of the same kind B-3's indefinite retention still needs. The technical question — where does it live, who may read
it — is answered; whether it must be deleted, kept, or archived is not.

**Changed in round 7, in a way that strengthens the case rather than settling it.** [D-083](decisions/round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)
made every fact about a person one class of data held on the person, so an event answer naming an
allergy is now **the same kind of fact stored in two places by two different rules** — one on the
person, where it is audited, curable and erased with the person; one in an event's table, readable by
whoever runs that event, with no retention policy. **The retention question and [AT-1](#at-1--should-an-event-question-bind-to-an-attribute-code)
are the same question from two directions**: an answer worth keeping is an attribute that was
collected at the wrong address, and an answer not worth keeping should be deleted on a schedule rather
than surviving because nobody wrote a policy. Until one of the two is decided, the weakest-protected
copy of a health fact is the one that is freshest.

### EV-4 🟢 `was_present` as a safeguarding record

**The question.** Presence is the record of who was actually in the organization's care
([D-067](decisions/round-05.md#d-067--presence-is-a-three-valued-fact-on-the-registration)).
Does it need its own retention, or its own permission?

**Why it might.** It is the record that answers "was this child at camp on the day of the
incident" — the question insurance and any safeguarding review will ask. That is a heavier
thing than "who said they were coming", and it currently shares both a table and a permission
with the registration.

**Why it might not.** It is meaningless without the registration it belongs to, and splitting
it would put two rows in two places describing one fact.

**Impact.** Splitting it is a table; keeping it is nothing. The argument for splitting is
permissions — a volunteer who takes the register at camp is not the same trust as one who may
alter the roster. See EV-5, which is the same tension.

### EV-6 🟡 `WHITELISTED` — the word people reach for, with no stored state to name

**Question.** [D-102](decisions/round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)
named four attendance tiers a grant may bind to and refused a fifth (`PRESENT`, refused because
`was_present` is `NULL` until somebody marks it). `WHITELISTED` keeps coming up in the same sentence and
**there is nowhere in the model for it to read from**: no flag on `event_registration`, no roster on `event`
besides organizers, no column anywhere that says *this person was let in*. Should the language refuse the
word, or should the model give it state?

**The half that is already answered, and should be said before anything is built.** "These named people may
register for this event" needs no new anything: it is an **allow grant on the event** naming
`event.register_self`, aimed at an audience whose expression is the hand-typed `PERSON(a) + PERSON(b)` or names
a `GROUP` — one row per sentence, revocable, audited, and **dated by the grant rather than by the names**,
since the dated rows those names used to live in are deleted (D-099, D-102, and
[D-105](decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)
for the deletion; [F-20](#f-20) settles
which of the two spellings a given sentence wants, and this entry does not). That is the D-102 answer to the
sentence, and it is better than a flag because a flag cannot be aimed at a group, cannot expire, and cannot be
refused by a deny. **Anyone adding `is_whitelisted` is
reimplementing grants badly.**

**The half that is not answered.** There is a different sentence that sounds identical and is not about
permission: *"she was invited, ahead of the public opening, and she has not answered yet."* That is a **fact
about a person's standing on one event**, and the model cannot state it. Worse, the tiers actively misreport
it: `PLACED` is the capacity set, so an invited person who registers onto a **full** event is
`ON_WAITLIST` — the model says *waiting* where the organizer's head says *has a place, we made room* — and
D-065 records an organizer exceeding capacity **by report, not by state**. So the overrun is real, visible in
a report, and invisible to any selector, which means a grant aimed at "the people we actually have room for"
and a grant aimed at "the people we invited" are the same four tiers stretched over two different questions.

**Positions.**
- **Refuse the word** — say plainly, where the tiers are listed, that there is no `WHITELISTED` and that the
  sentence it wants is a grant. Consistent with D-102's refusal of `PRESENT`, costs nothing, and leaves the
  invited-but-unanswered person described the way `unanswered` already is: **by the absence of a row**
  (D-059). **This is the default these documents hold today.**
- **Give it state** — a boolean or small status on `event_registration`, which makes it a **fifth tier** and
  forces the tier algebra to be restated: is an invited person `PLACED` by right, or only once capacity lets
  them through? Whatever is chosen, `PLACED`'s definition — *the set the capacity let through*, the one the
  index already serves — stops being one predicate, and that is the cost, not the new column.
- **Make it a group** — the invitation list is a `person_group` (D-098), named, dated, and separately
  answerable across time. This is cheap and it is *almost* right: it says who was invited, which is the fact
  people actually ask for later, and it is answerable on 1 June 2024 in a way an audience never is. It is
  wrong for the per-event case, because it makes an invitation a thing with its own lifetime.

**Needed.** Not before implementation, and not before someone asks — but **the word should be refused in
writing now**, in the same paragraph that refuses `PRESENT`, because "no `WHITELISTED`" is a sentence that has
to exist somewhere before the first person implements it as a column. The `PRESENT` refusal is the precedent
to copy: it was refused for a *representable* reason (nothing is stored until a person marks it), and this one
needs its reason stated rather than inherited.

**Impact.** Refusing costs a paragraph. The column costs a restated `PLACED`, a re-derived index, and a
report that now has two ways to be full.

---

## Ga. Personal attributes — designed, with four things left open

The module exists: [domain/08-person-data.md](domain/08-person-data.md) and
[data-model/09-attributes.md](data-model/09-attributes.md), decided by
[D-083](decisions/round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data),
[D-084](decisions/round-07-08.md#d-084--descriptive-data-is-organization-defined-at-runtime) and
[D-085](decisions/round-07-08.md#d-085--the-identity-machinery-stays-structured-the-boundary-is-rules-not-sensitivity).
It arrived instead of the health-records module, because the question "what is a health record here"
answered itself a size larger: everything about a person except name, gender and age is one class of
data, defined by the organization at runtime, with no privileged subset.

### AT-1 🟡 Should an event question bind to an attribute code?

**Raised by [D-085](decisions/round-07-08.md#d-085--the-identity-machinery-stays-structured-the-boundary-is-rules-not-sensitivity),
which made the event form the fallback rather than the ceiling.**

**The situation.** A returning camper types their allergy into every event form, every season, and
the answer lives in `event_answer.value` for that event only. Meanwhile the organization may already
hold the same fact as an attribute on the person, with a name, a `value_type`, and a recorded author.
Nothing connects them.

**Why this is a question and not an obvious improvement.** Prefilling an answer from the record makes
the **record the thing a leader relies on**, and the record is: whatever was typed, by whoever,
possibly two years ago, with no obligation on anyone to update it. Today's arrangement is worse data
and better epistemics — *the form asks now, about this event, and the answer is dated today*. Bind
the two and an out-of-date attribute becomes a wrong answer that looks authoritative, which is the
one failure mode a health fact has that makes it dangerous.

**Recommendation.** Prefill as a **suggestion the registrant confirms or corrects on the way in**, and
write the confirmed value back to the attribute with today's date and this person as its author. Then
the form stays the authority for the event, the record gets refreshed by the act of using it, and
nobody ever relies on a two-year-old entry without a human having just looked at it. **The variant to
reject** is reading the attribute directly into the organizer's view without the registrant's
confirmation pass — that is the same convenience with the safety removed.

**Impact.** One binding on the question definition, one write-back rule, and a rule about which is
authoritative when they disagree. No new permission.

**See:** [D-061](decisions/round-05.md#d-061--event-answers-are-read-by-that-events-organizers)
(as amended), [data-model/08 §7](data-model/08-events.md#health-facts-and-the-discipline-this-requires).

### AT-2 🟡 Who curates the vocabulary, and how long may a proposal sit?

**Raised by [D-084](decisions/round-07-08.md#d-084--descriptive-data-is-organization-defined-at-runtime),
which made `attribute.define` a permission instead of a release.**

An open vocabulary is only as good as somebody tending it, and "somebody" is currently nobody in
particular. Two halves:

- **Who holds `attribute.define`.** The starting role set
  ([permission-catalog §11](appendix/permission-catalog-b-roles-and-open-issues.md#11-roles--proposed-seed-set)) is the place
  this gets answered, and the honest answer is that a volunteer organization has one or two people who
  will do this and not a committee. Too narrow and the proposal queue is a bottleneck that teaches
  people to file facts into notes instead; too wide and it is not a curation.
- **How long a proposal may sit** before it is promoted, merged or discarded. The check exists
  ([09-attributes §8](data-model/09-attributes.md#8-integrity-checks) checks 1 and 2) and the number
  does not. A quarter is a defensible default: long enough that a seasonal field is not judged off a
  single use, short enough that a proposal is answered inside the season that produced it.

**Recommendation.** One named role, a stated age limit on proposals, and a standing decision that an
expired proposal's **values stay** — the curation is about the name, never about deleting what was
recorded.

**Impact.** Configuration and one role, no schema change. The thing it prevents is the slow failure:
a vocabulary nobody curates stops being queryable and the layer keeps storing everything, which looks
like success for years.

### AT-3 🟢 Do attribute labels need translation?

Inherited from the multi-language row in [§H](#h-not-yet-designed), and sharper here than anywhere
else because the vocabulary is runtime data: if a code's label is Czech-only, a Slovak-speaking
volunteer cannot pick the field at all. Whether the answer is a translation column on
`attribute_definition`, a separate label-per-language table, or "the organization is
single-language, stop asking" is unrecorded. **The cost of not answering is asymmetric** — a label
table added later is a migration; a body of codes accumulated with one label each is a data-cleaning
project.

### AT-4 🟡 Is one permission enough to guard a trail that holds person data?

**Raised by the reversal recorded in
[D-083](decisions/round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data),
which decided the audit trail *does* hold a person's descriptive values** — because
[D-085](decisions/round-07-08.md#d-085--the-identity-machinery-stays-structured-the-boundary-is-rules-not-sensitivity)
made that trail the only history such values have, and stripping them would have made the history empty
while quietly grading health-shaped fields above a change of address. What protects the copy is then one
thing: `audit.view`, graded ⚠⚠ beside `person.view`
([permission-catalog §8](appendix/permission-catalog-a-codes.md#8-audit-and-system)). Three positions exist and
none is recorded as taken:

- **The guard is enough** (current documents). One permission, marked honestly, and a rule that whoever
  holds it is reading person data. Simple, and it makes the auditor role — which has `audit.view` and
  not `person.view` — a reader of the entire person record
  ([permission-catalog §11 note 3](appendix/permission-catalog-b-roles-and-open-issues.md#11-roles--proposed-seed-set)).
- **Per-entry filtering in the history view:** show an audit row's values only where the reader could
  also see the live field. Consistent with everything §9 of
  [data-model/05c-access-log-and-resolver.md](data-model/05c-access-log-and-resolver.md#9-access_log) says about channels, and
  it was considered and left unimplemented, because it means running the resolver per audit row against
  rows that may no longer exist — a grant withdrawn last year is exactly the case a history is read for.
- **Split the permission:** the trail's shape (who changed which table, when) apart from its payloads.
  Honest about what an auditor usually needs, and it is the option that reintroduces a sensitive subset
  through the back of the catalog — which is why the documents do not recommend it.

**The cost of not answering is asymmetric in the uncomfortable direction:** the first position is
already implemented by default, so leaving the question open *is* choosing it, and the choice is made
invisible — nobody signs off on "volunteers with `audit.view` can read children's medical history"
because there is no moment at which anybody has to say it.

---

## H. Not yet designed

Each of these is referenced by the schema and has hooks left for it. Two rows carry a ✅ because the
area needed no new module: events was designed in round 5, and the medical record was answered out of
existence in round 7 — what a reader who says "the medical record" is pointing at is the attribute
vocabulary of [§ Ga](#ga-personal-attributes--designed-with-four-things-left-open), one class of
person data with no privileged subset ([D-083](decisions/round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)).

| Area | Hooks already in place | Notes |
|------|------------------------|-------|
| **Events** ✅ | **Designed** — [domain/07](domain/07-events.md), [data-model/08](data-model/08-events.md) | Fifteen questions answered; three left in § G above. |
| **Fees and payments** | [data-model/07-finance.md](data-model/07-finance.md) — **architecture settled, policy open** | **Nine open questions**, of which one is new. Round 6 closed the architectural ones: money arrives by **bank API**, is requested by **variable symbol + QR code**, there is **no card gateway**, and unmatched money **queues** ([D-075](decisions/round-06.md#d-075--money-arrives-from-a-bank-api-a-payment-is-requested-by-variable-symbol-and-qr-code), [D-076](decisions/round-06.md#d-076--money-that-cannot-be-matched-waits-for-a-person)). What remains needs somebody in the organization asked: proration, discounts, insurance, waivers, invoices. |
| **Documents** | `access_grant.scope_type = 'document'`; the evidence-reference hook belonged to the removed requirement tables | Needs: storage, versions, retention, consent-driven access. |
| **Consents** | No `dependent.consent.*` any more — a guardian at `write` may give and manage consents ([D-074](decisions/round-06.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular)) | Needs: template, per-activity consent, expiry, revocation, who may consent. No longer connected to a membership requirement ([D-044](decisions/round-02-03.md#d-044--nothing-gates-a-membership-request-except-identity-and-payment)). **`is_legal_decision_maker` on the guardianship row is the existing hook for "who may sign" — and it is now the only place that distinction lives**, since the right level cannot express it. |
| **Health records** ✅ | **Designed — as [domain/08](domain/08-person-data.md) and [data-model/09](data-model/09-attributes.md)** | **There was no medical record to design.** [D-083](decisions/round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data) ruled that everything about a person except name, gender and age is one class of data, held as fields in a vocabulary the organization defines at runtime ([D-084](decisions/round-07-08.md#d-084--descriptive-data-is-organization-defined-at-runtime)). Reading is `person.view`, writing is `person.edit`, and only the vocabulary needs a code of its own. What is left undesigned is policy around one class rather than a second module: what happens to the history of a value once the audit payloads expire, and whether `attribute.define` is a sufficient gate for a vocabulary free to invent a "health" category tomorrow — which is [AT-4](#at-4--is-one-permission-enough-to-guard-a-trail-that-holds-person-data). |
| **Communication** | `message.send_direct`, `message.broadcast` (scoped) — shape decided, detail undesigned | **Shape decided by [D-077](decisions/round-06.md#d-077--messaging-is-direct-by-default-broadcast-is-an-ordinary-scoped-permission-and-the-recipient-chooses-the-channel):** internal first, external channels are delivery; everyone may send direct; `broadcast` is one scoped permission; **the recipient picks the channel.** Needs: templates, opt-out granularity, retention, moderation. The rule against contacting minors directly was **declined as a sender restriction** and replaced by mirroring — see [MSG-1](#msg-1). |
| **Reporting** | `report.*` permissions sketched | The historical queries in [domain/05](domain/05-membership-lifecycle.md#8-back-to-the-paper--the-ten-queries-this-design-must-answer) are the starting set. Query 10 (members per year, as far back as the records reach) is the acceptance test. |
| **API and UI** | — | Not started. The resolver's `p_at` parameter exists partly for this. |
| **Notifications** | — | Expiring roles, members inside the renewal window, unpaid fees. Note the renewal window makes this *dated* rather than status-driven — a nightly job over `in_renewal_window()`. |
| **Payment gateway** | — | **Answered, so this row is now narrower than it was.** The organization collects via **bank API**, not a card gateway ([D-075](decisions/round-06.md#d-075--money-arrives-from-a-bank-api-a-payment-is-requested-by-variable-symbol-and-qr-code)): no webhooks, no disputes, no processor reconciliation. What remains undesigned is the **statement import** itself — file formats, the idempotency key, and what happens to an account the bank revises. |
| **Multi-language** | — | Unit names and permission display names are all in the database. Whether they need translation columns is unanswered. |

---

## R. Resolved — moved to the decision log

Kept here so a reader of this file knows the question was asked and where the answer lives,
rather than finding it silently deleted.

| Was | Question | Settled by | In one line |
|-----|----------|-----------|-------------|
| <a id="a-1"></a>A-1 | The organizational structure | [D-035](decisions/round-02-03.md#d-035--one-root-unit-all-sub-units-nest-arbitrarily-beneath-it) | One root; all sub-units nest arbitrarily beneath it. **Reversed in round 10:** there are no sub-units at all, and the unit is a scope rather than a row ([D-097](decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)). |
| A-1 | The unit type vocabulary | [D-054](decisions/round-04.md#d-054--the-sub-unit-vocabulary-is-not-seeded-the-organization-defines-its-own-types) | Not seeded — `org_unit_type` is runtime data; only the root type ships. **Deleted with the table** ([D-097](decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)). |
| <a id="b-1"></a>B-1 | How much legacy data, in what shape? | [D-056](decisions/round-04.md#d-056--the-legacy-import-expects-a-large-corpus-with-legacy-member-numbers) | Large, with legacy member numbers — exact matches, so review is a work queue. **Fully answered in round 8:** thousands of roster rows, no payment data at all, so every historical row is a participation ([D-090](decisions/round-07-08.md#d-090--the-legacy-corpus-is-thousands-of-roster-rows-with-numbers-and-no-money)). **Round 10 moved the noun:** the participation table is gone, so an attendance row with no dates imports as a dated `person_group_member` row or nothing at all ([D-097](decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row), [D-098](decisions/round-10a.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority)). |
| <a id="d-9"></a>D-9 | Is `household` load-bearing at all? | [D-057](decisions/round-04.md#d-057--household-is-removed) | No — removed entirely. Addresses are temporal `person_contact` rows. |
| <a id="f-1"></a>F-1 | Which permissions and roles does the organization need? | [D-055](decisions/round-04.md#d-055--the-permission-catalog-is-deliberately-comprehensive-and-granular) | The catalog stays large and granular; it is a menu, not a checklist. |
| — | Eligibility for an event — a separate rule engine? | [D-060](decisions/round-05.md#d-060--eligibility-is-capability-there-is-no-separate-rule-engine) | No — eligibility **is** capability. `event.register_self` at `contribute`, via audiences. |
| — | Is `unanswered` a stored attendance value? | [D-059](decisions/round-05.md#d-059--unanswered-is-the-absence-of-a-row-a-registration-stores-two-values) | No — absence of a row. Two stored values: `attending`, `not_attending`. |
| — | Is a weekly meeting an event? | [D-058](decisions/round-05.md#d-058--an-event-is-a-dated-occasion-owned-by-exactly-one-unit) | No. **Round 10 moved the answer:** a Thursday group is a `person_group` with a dated roster, and `unit_participation` is deleted ([D-097](decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)). Still no recurrence, no series table, no occurrence table, and no row that says who attended a given evening. |
| — | One owning unit per event, or several? | [D-058](decisions/round-05.md#d-058--an-event-is-a-dated-occasion-owned-by-exactly-one-unit) | Exactly one. **Reversed in round 10b:** nothing owns an event — `event.org_unit_id` is deleted and the people connected to it are named by selectors that bind to it ([D-102](decisions/round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)). |
| — | Are organizers a grant or a roster? | [D-062](decisions/round-05.md#d-062--organizers-are-appointed-on-the-event-not-granted) | A roster on the event — labelled and ordered. Grants stay separate. |
| — | Do unit roles reach the unit's own events? | [D-063](decisions/round-05.md#d-063--an-event-is-an-artifact-of-its-unit-not-a-child-of-it) | Yes — an event is an **artifact** of its unit, not a child. **Reversed in round 10b:** the artifact rule and `can_event()` are deleted, and nothing reaches an event from a unit ([D-102](decisions/round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)). D-031's finding survives as the safeguarding property stated in [the authorization ERD](appendix/erd-a-authorization.md#5-authorization--the-whole-answer-in-one-diagram). |
| — | Does an event have a status (`draft`, `published`)? | [D-064](decisions/round-05.md#d-064--there-is-no-event-status-visibility-is-the-permission-model) | No status column. Visibility **is** the permission model; cancellation is a fact. |
| — | What happens when a full event gets another registration? | [D-065](decisions/round-05.md#d-065--capacity-is-a-waitlist-threshold-and-organizers-may-exceed-it) | Waitlisted for self-service; admitted for organizers; the overrun reported. |
| — | Does paying confirm a place? | [D-066](decisions/round-05.md#d-066--payment-confirms-the-place-and-the-release-deadline-is-the-one-automatic-transition) | Yes when the event has a fee; most events are free and confirm immediately. |
| — | Do organizers record who actually came? | [D-067](decisions/round-05.md#d-067--presence-is-a-three-valued-fact-on-the-registration) | Yes — `was_present`, three-valued. It is the "who was in our care" record. |
| — | May an event form collect medical detail? | [D-061](decisions/round-05.md#d-061--event-answers-are-read-by-that-events-organizers) | Effectively yes: answers are read by that event's organizers, and **no event permission reaches the health record**, so the form is the only route for a camp leader to learn an allergy at all. A recorded widening, restated after D-074 removed the namespace the original wording relied on. |
| A-2 | Permissions conditioned on membership status | [D-039](decisions/round-02-03.md#d-039--member-permissions-require-a-current-paid-membership) | Yes, enforced by the resolver, with guardianship and ownership carved out. **Round 10 deleted the gate** ([D-100](decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)): membership is now a term a grant's expression may name, not a precondition the resolver checks. |
| A-3 | Activate on payment or on approval? | [D-040](decisions/round-02-03.md#d-040--the-fee-expires-yearly-a-date-tracked-renewal-window-replaces-a-grace-status) | On payment; the fee expires yearly and a dated renewal window replaces a grace status. |
| A-4 | Background checks | [D-043](decisions/round-02-03.md#d-043--no-background-checks-are-recorded-in-this-system) | None are recorded in this system. |
| A-4 | The expiry date | [D-047](decisions/round-04.md#d-047--the-fee-expires-on-1-january) | 1 January; the organizational year runs with the calendar. |
| A-4 | The renewal window length | [D-048](decisions/round-04.md#d-048--the-renewal-window-is-60-days-and-is-a-configuration-parameter) | 60 days, stored as a parameter rather than compiled in. |
| <a id="c-1"></a>C-1 | May the root read into its sub-units? | [D-049](decisions/round-04.md#d-049--the-root-may-not-read-into-its-sub-units-scope_exposure-is-the-only-crossing) | No. `scope_exposure` is the only crossing; no reporting channel is built. **Formally closed in round 9**, and [D-094](decisions/round-09.md#d-094--the-root-unit-owns-every-imported-event) gave it a mirror: imported events belong to the root, so a unit's own event list contains history it did not run. **Round 10 dissolved the question:** there is no sub-unit to read into and `scope_exposure` is deleted ([D-097](decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)). |
| <a id="c-3"></a>C-3 | Is a reused unit number the same unit? | [D-096](decisions/round-09.md#d-096--a-reused-unit-number-is-a-new-unit-unless-someone-records-the-continuity) | A **new** unit, unless someone records continuity as `successor_of`. A `code` is a typed label, not an identity. **Moot with the table** ([D-097](decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)). |
| <a id="c-4"></a>C-4 | Does appointing someone create a role assignment? | [D-091](decisions/round-09.md#d-091--a-permission-group-is-a-rule-and-a-list-at-once-and-a-rule-may-name-another-group), restated by [D-098](decisions/round-10a.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority), [D-100](decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape), [D-101](decisions/round-10b.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree) | No. **Round 10 redrew the line the answer drew:** the union-of-three-arms became an expression language (`+ - *`), a **group** became a hand-stated dated roster, and an **audience** became the rule. Appointing still creates nothing, and there are no positions left to appoint. Rule-filled *roles* went to [F-12](#f-12), which round 10 closed **no**. |
| <a id="c-5"></a>C-5 | What creates the units the import's rows point at? | [D-092](decisions/round-09.md#d-092--the-corpus-is-people-and-events-and-it-names-no-units), [D-093](decisions/round-09.md#d-093--the-one-off-import-may-create-memberships-both-ends-dated), [D-094](decisions/round-09.md#d-094--the-root-unit-owns-every-imported-event) | Nothing, because the rows name no units. People arrive as bounded memberships, events as root-owned events with registrations. **The historical record has no sub-units in it.** |
| <a id="c-6"></a>C-6 | Should `allows_minors` refuse a minor's position as it refuses their participation? | [D-095](decisions/round-09.md#d-095--units-carry-no-restrictions-joining-one-is-somebody-elses-act) | Neither: units carry no restrictions and the flag is removed. The control is that nobody joins a unit or takes a position themself — a counselor writes the row. **Positions went in round 10** ([D-100](decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)); the control is now `person_group.member.manage`. |
| <a id="d-6"></a>D-6 | How may the membership gate be waived? | [D-051](decisions/round-04.md#d-051--the-membership-gate-is-waived-by-a-permission-not-only-by-a-role-flag) | A person-level `system.gate_exempt` permission, in addition to the role flag. **Both are deleted** ([D-100](decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)). What survives is the reason: a sweep must not lock out the one person who can repair it. |
| <a id="d-7"></a>D-7 | The root participation row at renewal | [D-050](decisions/round-04.md#d-050--a-renewal-inside-the-window-extends-the-existing-root-participation-row) | Extended across the renewed period; one row, no gap. **Retired with the table** ([D-097](decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)). |
| C-1 (largely) | Organization-wide operational roles without downward inheritance | [D-035](decisions/round-02-03.md#d-035--one-root-unit-all-sub-units-nest-arbitrarily-beneath-it) | The problem dissolves: the root owns the registry and the fees. What remains is a reporting question — see [C-1](#c-1). **One unit now, so the shape is gone entirely** ([D-097](decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)). |
| C-2 | May units be reparented retroactively? | [D-036](decisions/round-02-03.md#d-036--units-cannot-be-reparented-a-unit-that-moves-is-a-new-unit) | Not at all — a unit that moves is a new unit. **Moot with the units** ([D-097](decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)). |
| D-1 | Fee per person or per household? | [D-037](decisions/round-02-03.md#d-037--exactly-one-membership-type-the-fee-is-flat-and-per-person) | Per person, flat, yearly. |
| D-2 | One open membership, or several of different types? | [D-037](decisions/round-02-03.md#d-037--exactly-one-membership-type-the-fee-is-flat-and-per-person), [D-041](decisions/round-02-03.md#d-041--belonging-to-a-sub-unit-is-a-participation-record-not-a-membership) | One type, so one open membership, enforced person-wide. The participation half of [D-041](decisions/round-02-03.md#d-041--belonging-to-a-sub-unit-is-a-participation-record-not-a-membership) is moot ([D-097](decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)). |
| D-3 | Age-out timing | [D-038](decisions/round-02-03.md#d-038--membership-is-ageless) | Retired — there is no age-out. |
| D-4 | Child → adult transition | [D-038](decisions/round-02-03.md#d-038--membership-is-ageless) | Retired — there are no membership categories to transition between. |
| D-5 | Membership type vocabulary | [D-037](decisions/round-02-03.md#d-037--exactly-one-membership-type-the-fee-is-flat-and-per-person) | One type, `member`; counselor is a position, not a type. |
| E-1 | Default rights when a guardianship is created | [D-046](decisions/round-02-03.md#d-046--guardianship-defaults-depend-on-how-the-guardianship-was-created) | `write` for a self-registered child's guardian; `view` for staff-created and imported rows; chosen at creation when recorded manually. **D-074 turned the answer from a code bundle into one level**, which is why the decision still stands on its original wording. |
| F-2 | Polymorphic `scope_id` vs a `grantable_item` supertable | your answer, round 6 | Polymorphic — `scope_type` plus `scope_id`, as currently designed. |
| — | The bulk scope-exposure tool | [D-045](decisions/round-02-03.md#d-045--the-bulk-scope-exposure-tool-is-removed) | Removed once audiences existed to cover the case it was for. |
| — | What a membership request must contain | [D-044](decisions/round-02-03.md#d-044--nothing-gates-a-membership-request-except-identity-and-payment) | Identity and the fee. The whole requirement mechanism is gone. |
| — | Whether grants may target groups | [D-042](decisions/round-02-03.md#d-042--grants-may-target-audiences-not-only-individuals) | Yes — built-in rule-evaluated audiences plus admin-managed named groups. |
| <a id="e-2"></a>E-2 | What happens to guardianship at majority? | [D-069](decisions/round-05.md#d-069--guardianship-ends-when-a-person-ends-it-the-system-takes-no-position-on-majority) | Nothing — no job, no queue, no computed date. A person ends the row. *(Reverses D-024.)* |
| <a id="f-3"></a>F-3 | Must a high-authority role assignment have an end date? | [D-071](decisions/round-05.md#d-071--nothing-forces-a-role-assignment-to-end-the-gate-and-the-report-are-the-control) | No. The membership gate plus a human review report; the earlier "yes" recommendation is withdrawn. **Both halves moved:** the gate is deleted ([D-100](decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)) and the report became a tab ([D-109](decisions/round-13.md#d-109--nothing-a-rule-names-is-deleted-deprecated-hidden-disabled--and-a-tab-instead-of-a-report)). |
| <a id="f-4"></a>F-4 | Should `person.admin` subsume merge and redact? | [D-068](decisions/round-05.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle) | Moot — there are no per-resource `admin` permissions. The choice moved into reviewable role contents. *(Reverses D-007.)* |
| — | Should every resource expose an `admin` permission? | [D-068](decisions/round-05.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle) | No. Sixteen codes and the resolver's prefix match are gone; roles are the bundle. |
| <a id="ev-1"></a>EV-1 | Does an event need an age ceiling? | [D-070](decisions/round-05.md#d-070--an-event-has-no-age-ceiling-the-grant-is-the-rule) | No. The grant is the rule; a future ceiling would be a built-in audience, not a column. |
| <a id="ev-5"></a>EV-5 | Should `event.manage_participants` split? | this round | Yes — `event.presence.mark` at `contribute`, one level below the roster. **Round 10 note:** the split stands; the level does not ([D-099](decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)). |
| <a id="d-8"></a>D-8 | Should `unit_participation` reference the membership? | [D-097](decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row) | Retired with the table. The refusal is still live reasoning: participation had to survive without a membership, which is why `person_group_member` is keyed on a person. See [data-model/03 §9](data-model/03-membership.md#9-open-issues). |
| <a id="f-12"></a>F-12 | May a role be held by a rule, as an audience is? | [D-100](decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape) | **No.** An office is held by a named person and confers nothing; a group is company; a **grant** is what reaches a set. The office record stays the one dated, human-readable answer. |
| — | Is there more than one unit, and does anything belong to it? | [D-097](decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row) | No. `org_unit` and friends, `unit_participation`, `scope_exposure` and the traversal functions are deleted; **the unit is a scope, not a row**. Two-way door: no. |
| — | What is a group? | [D-098](decisions/round-10a.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority) | `person_group`: named, dated, **states its members**, has a lifetime, grants nothing by itself. A group is company; a selector picks people; a grant is what reaches them. |
| — | What does a grant do, and how much? | [D-099](decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality) | Allows **or** denies one permission at one scope, for a period. Allowed iff some live allow applies and no live deny applies. No levels, no rank integer, no locality. |
| — | Is a role a bundle of permissions, and is membership a precondition? | [D-100](decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape) | Neither. `role_assignment` → `role_holder`; `role_permission`, positions and the membership gate are deleted; the test moved into the expression (`MEMBERS * ROLE(x)`). Posture: default-on → **opt-in**. |
| — | How is an audience stored? | [D-101](decisions/round-10b.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree) | As an **expression tree** over named sets — `+ - *`, brackets, fully-bracketed canonical form, cycles refused at save, the language seeded as `selector_type`. Semantic equality given up (see F-14). |
| — | Who owns an event, and whom does a grant about it reach? | [D-102](decisions/round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it) | **Nobody owns it.** `event.org_unit_id`, `can_event()` and the artifact rule are deleted; four attendance tiers and `ORGANIZERS` **bind to the item**, and the answer-view grant is a seeded template instantiated per event. |
| — | May a rule be reused by name? | [D-103](decisions/round-10b.md#d-103--an-audience-may-name-another-audience) | Yes: `AUDIENCE(code)`, referenced by code, one namespace with roles and groups, cycles refused across audiences at save, and an audience named by a live grant may not be ended. Its past reach is not reconstructable (see F-17). **Amended in the same round:** the same refusal now extends to a **group** named by a live grant — see [assumption 63](#i-assumption-index). |
| <a id="f-19"></a>F-19 | A permission code is a row, prose names codes, and nothing checks the two | [D-104](decisions/round-10b.md#d-104--a-permission-codes-last-segment-is-an-action-and-a-registry-that-prose-contradicts-is-a-fiction) | The class is real — **four instances in ten rounds, in two different registries.** The naming grammar is now three rules (action-final; a middle segment names stored state; no grade words, no prefix) with `system.admin` the single named exception. **The event QR capability never existed**: invented in prose, deleted in prose, no decision entry at either end. The check adopted is a **hand-run diff report** — a convention, not a guard. |

---

## I. Assumption index

Every *Assumption:* the documentation is standing on, so they can be reviewed as a group. Confirming
one promotes it to a numbered decision: the row keeps its number, gains a **†**, and says which decision
carries it now. A row whose subject was deleted keeps its number too, struck, with the decision that deleted
it — the numbers are stable identifiers, so an earlier round's citation of "assumption 61" still resolves.

The fate of a superseded assumption is one clause here and a decision entry elsewhere; the argument is in
the entry, and this index is a register, not a second copy of it.

| # | Assumption | Where |
|---|-----------|-------|
| 1 | PostgreSQL 14+ with `btree_gist` | [data-model/00](data-model/00-conventions.md#1-target-platform) |
| 2 | No automatic merging (D-004) † | [domain/03](domain/03-identity-and-legacy.md#4-match-signals) |
| 3 | Minors need guardian consent for an account | [domain/02](domain/02-actors.md#2-who-registers-and-why) |
| 4 | A self-registered child's parent gets a `write` right over the child (D-046, as amended by D-074) † | [data-model/04](data-model/04-relationships.md#2-the-guardians-right-none-view-or-write) |
| 5 | ~~Locality orders allows only~~; **deny is absolute** (D-032) † — **half of this row is deleted**: locality went with the levels ([D-099](decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)), and the surviving half is now the whole decision rule: allowed iff some live allow applies **and no live deny applies** | [domain/06](domain/06-authorization-model.md#71-who-decides--deny-is-absolute) |
| 6 | Membership activates on payment (D-040) † | [domain/05](domain/05-membership-lifecycle.md#1-the-flow-you-described) |
| 7 | The fee is per person and yearly (D-037) † | [domain/05](domain/05-membership-lifecycle.md#6-renewal-and-the-yearly-fee) |
| 8 | Renewal opens a new row, not an extended `valid_to` (D-016) † | [domain/05](domain/05-membership-lifecycle.md#6-renewal-and-the-yearly-fee) |
| ~~9~~ | ~~Guardianship reviewed at majority, not auto-expired~~ — **superseded**: neither, the system takes no position (D-069) | [data-model/04](data-model/04-relationships.md#1-guardianship) |
| 10 | Display name uses `preferred_name` if set | [data-model/01](data-model/01-identity.md#3-person_name--name-history) |
| 11 | Merge chains are allowed, because reversing a merge has to stay possible (D-087) † | [data-model/01](data-model/01b-merges-views-and-checks.md#9-views) |
| 12 | Only confirmed payments count toward a balance | [data-model/07](data-model/07-finance.md#3-keeping-membershipoutstanding_balance-honest) |
| ~~13~~ | ~~No sub-unit types are seeded; nesting is permissive by default~~ (D-054) — **deleted, not reversed**: `org_unit_type` and `org_unit_type_rule` went with the hierarchy ([D-097](decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)), so there is nothing left to seed and no nesting to be permissive about. A-1's closure is the decision of record | [data-model/02](data-model/02-organization.md#5-what-this-page-held-before-round-10) |
| 14 | `membership_type` is seeded with exactly one row (D-037) † | [data-model/03](data-model/03-membership.md#8-seed-data) |
| 15 | `person.gender` is needed for reporting | [data-model/01](data-model/01-identity.md#2-person) |
| 16 | Imported rosters end at the organizational year end (D-028) † | [data-model/06](data-model/06a-import.md#3-import-pipeline) |
| 17 | All business tables are audited | [data-model/06](data-model/06b-redaction-and-checks.md#6-open-issues) |
| 18 | Currency is EUR | [data-model/07](data-model/07-finance.md#2-minimal-provisional-shape) |
| 19 | `access_log` is not human-annotatable | [data-model/05](data-model/05c-access-log-and-resolver.md#9-access_log) |
| ~~20~~ | ~~Each permission has an `admin` sibling~~ — **superseded**: no per-resource wildcard codes (D-068) | throughout |
| 21 | No downward inheritance; ~~exposures are written by the unit~~ (D-031) † — **deprived of its subject, not weakened** ([D-097](decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)): the rule was always about a hierarchy that no longer exists, and what survives is the ordinary reading of a scope — **a grant reaches its scope and nothing beside it** | [domain/06 §2](domain/06-authorization-model.md#2-scopes--the-unit-and-the-item) |
| 22 | The person record holds no deceased flag (D-034) † | [data-model/01](data-model/01-identity.md#2-person) |
| ~~23~~ | ~~Positions are multi-holder unless `max_holders` says otherwise~~ (D-033) — **deleted by D-100** with `position`, `position_assignment`, `is_leadership` and `max_holders`. The vacancy question it answered is now unanswered by construction; see [F-18](#f-18--does-a-role-record-elected-versus-appointed-and-what-does-an-election-write) | [domain/04](domain/04-organization-structure.md) |
| 24 | Membership is ageless — no category, no `min_age`, no `max_age` (D-038) † | [data-model/03](data-model/03-membership.md#1-membership_type--one-row-kept-as-a-table) |
| 25 | A grant targets a person **or** an audience, never both (D-042) † | [data-model/05](data-model/05-authorization.md#6-access_grant--the-per-item-layer) |
| 26 | ~~Built-in audiences are rules evaluated by the resolver, not stored lists~~ (D-042) † — **reversed twice, and the second reversal is the one to keep.** An audience stores an expression and nothing else: a hand-written set is `PERSON(x)` leaves *inside* it — rows of the tree, not rows of a roster, with no dates of their own ([D-101](decisions/round-10b.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree) then [D-105](decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other), which deleted the `LIST` leaf round 10 put back). D-042's half about rules is therefore true again, for a new reason: the words are what is stored, and the words can happen to name people. The count this row used to quote is stated once, in [data-model/05d §12](data-model/05d-invariants-and-seed.md#12-what-the-organization-starts-with). | [data-model/05](data-model/05a-audience-and-grammar.md#the-selector-registry) |
| ~~27~~ | ~~Belonging to a sub-unit is participation, not membership~~ (D-041) † — **deleted with the sub-units** ([D-097](decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)). The distinction it drew is now drawn between a **group** (company) and a **grant** (authority), by D-098 | [data-model/02](data-model/02-organization.md#5-what-this-page-held-before-round-10) |
| ~~28~~ | ~~Roles require a current membership unless `requires_membership = false`~~ (D-039) † — **the gate is deleted** (D-100); membership is now a term a writer puts in a grant expression, and the posture is opt-in | [data-model/05](data-model/05-authorization.md#3-role--an-office) |
| ~~29~~ | ~~There is no bulk exposure tool and no `bulk:` reason marker~~ (D-045) † — **moot twice over**: `scope_exposure` itself is deleted (D-097), so there is no tool to build and nothing to mark | [data-model/05](data-model/05-authorization.md#5-scope_exposure--deleted-by-d-097) |
| 30 | No background checks are recorded anywhere (D-043) † | throughout |
| 31 | `access_grant.scope_id` is polymorphic, with no foreign key (F-2) † | [data-model/05](data-model/05-authorization.md#6-access_grant--the-per-item-layer) |
| 32 | The organizational calendar is 1 January plus a 60-day window (D-047, D-048) † | [data-model/03](data-model/03-membership.md#1-membership_type--one-row-kept-as-a-table) |
| ~~33~~ | ~~The root reads into a sub-unit only through `scope_exposure`~~ (D-049) † — **there is no sub-unit and no exposure** (D-097). C-1's closure is the record; the safeguarding property it protected ("a child's records are reachable only through a guardianship row") was never carried by this mechanism and is untouched | [domain/06](domain/06-authorization-model.md#2-scopes--the-unit-and-the-item) |
| ~~34~~ | ~~A renewal extends the root participation row rather than closing it~~ (D-050) † — **the row is deleted** (D-097). The reasoning survives where the row did not: [data-model/03 §9](data-model/03-membership.md#9-open-issues) keeps it, because the renewal rule in §3 still rests on it. See D-7 | [data-model/03](data-model/03-membership.md#5-unit_participation--deleted-by-d-097) |
| ~~35~~ | ~~The membership gate is waived by a person-level permission, not only a role flag~~ (D-051) † — **the gate and `system.gate_exempt` are both deleted** (D-100). What survives is the *reason*: a sweep must not lock out the one person who can repair it, which is now an argument about the seeded grants carrying `MEMBERS`. See D-6 | [data-model/05](data-model/05-authorization.md#nothing-forces-a-holder-row-to-end-and-the-report-is-the-control) |
| 36 | The permission catalog is deliberately comprehensive and granular (D-055) † | [appendix/permission-catalog.md](appendix/permission-catalog.md) |
| 37 | The legacy corpus is large and carries legacy member numbers (D-056) † | [domain/03](domain/03-identity-and-legacy.md#4-match-signals) |
| 38 | There is no `household` table; addresses are temporal `person_contact` rows (D-057) † | [data-model/04](data-model/04-relationships.md#3-there-is-no-household-table) |
| 39 | ~~An event belongs to exactly one unit~~; **a weekly meeting is not an event** (D-058) † — **first half deleted by [D-102](decisions/round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)** (`event.org_unit_id` is gone; nothing owns an event), second half intact but no longer named "participation": a Thursday group is a **group** now (D-097, D-098), and no row says who attended a given evening | [data-model/08](data-model/08-events.md#there-is-no-owner-column) |
| 40 | "Unanswered" is the absence of a registration row (D-059) † | [data-model/08](data-model/08-events.md#4-event_registration) |
| 41 | Eligibility is capability — there is no rule engine (D-060) † | [domain/07](domain/07-events.md#4-who-may-register-capability-not-a-separate-rule-engine) |
| 42 | Event answers are read by that event's organizers (D-061) † — **still true, and no longer a resolver clause**: it is one seeded grant row (`event.answer.view`, scoped to the event, aimed at `ORGANIZERS`) instantiated per event, which D-102 calls out as the deliberate move from prose to data. **An event created without its grant has organizers who can read nothing** | [data-model/08](data-model/08a-event-guards-and-checks.md#selectors-that-bind-to-an-event) |
| 43 | Organizers are a roster on the event, not grants (D-062) † | [data-model/08](data-model/08-events.md#3-event_organizer) |
| ~~44~~ | ~~An event is an artifact of its unit, so unit roles reach it~~ (D-063) † — **deleted by [D-102](decisions/round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)**, along with `can_event()`. Nothing reaches an event from a unit any more; authority arrives through a grant scoped to the event itself, and the sentence "an event is an artifact, not a child" is withdrawn rather than restated | [domain/07](domain/07-events.md) |
| 45 | There is no event status; visibility is the permission model (D-064) † | [data-model/08](data-model/08-events.md#2-event) |
| 46 | Capacity is a waitlist threshold organizers may exceed (D-065) † | [data-model/08](data-model/08-events.md#5-capacity-and-the-waitlist) |
| 47 | Payment confirms a place; free events confirm immediately (D-066) † | [data-model/08](data-model/08-events.md#6-payments-and-confirmation) |
| 48 | Presence is a three-valued fact, not a boolean (D-067) † | [data-model/08](data-model/08-events.md#4-event_registration) |
| 49 | Keeping named membership and fee rows **indefinitely** after an erasure request has a legal basis (D-088) — **unverified, and commissioning the review is the organization's job** | [data-model/00](data-model/00-conventions.md#8-personal-data-and-erasure) |
| 50 | `access_log` needs the same window as audit payloads, neither longer nor shorter (proposed, **F-8**) | [data-model/05](data-model/05c-access-log-and-resolver.md#9-access_log) |
| 51 | **Audience** membership is recomputed at check time and never stored, so "who could read this in 2023" may be unanswerable once the audit payloads expire (D-091, restated for D-098/D-101) † — **the half of this that used to be true of roles is no longer at risk**: an office is a dated `role_holder` row and a group is a dated roster, both stored, and F-12 closed on exactly that ground. What remains exposed is the expression, and it is now a question with a number: [F-17](#f-17) | [data-model/05](data-model/05b-expression-tree.md#three-named-sets-and-the-one-question-nesting-cannot-answer) |
| 52 | The historical record contains no sub-unit participation, because the corpus names no units (D-092) † — **now true for a second, stronger reason**: even if the corpus had named them there would be nowhere to put the answer (D-097). The finding about the *source* is what matters and is unchanged | [data-model/06](data-model/06a-import.md#31-what-a-source-row-actually-evidences) |
| 53 | An imported membership carries no fee obligation, and its `outstanding_balance` is NULL rather than zero (D-093) † | [data-model/07](data-model/07-finance.md#3-keeping-membershipoutstanding_balance-honest) |
| 54 | A bare name in an expression resolves to a **role or a group only**, never to an audience — and the one-namespace rule across `role`, `person_group` and `audience.code`, with every `selector_type.code` reserved, is carried by the write path with **no constraint spanning three tables** (D-101, D-103) † | [data-model/05](data-model/05b-expression-tree.md#names-are-one-namespace-and-reserved-words-are-the-other-half) |
| 55 | Delegation is a set-membership test, and `role.is_delegatable` does not exist — the model has no column that says an office may delegate (*no decision; domain/06 carries it as an assumption*) | [domain/06](domain/06-authorization-model.md#11-open-issues) |
| 56 | Finding **which grants name an audience, and at what depth**, is cheap enough to show before saving an edit to a referenced audience (D-103) — **stated as an assumption in the decision itself and measured by nobody** | [F-16](#f-16) |
| 57 | A grant's scope is the unit **or exactly one item**, so the seeded answer-view grant is a **template instantiated per event** rather than one row for every event (D-102) † | [data-model/08](data-model/08a-event-guards-and-checks.md#selectors-that-bind-to-an-event) |
| 58 | ~~The `PERSON(x)` appearing in D-100's and D-101's worked expressions is **shorthand** for a second grant row, not a missing seeded operand~~ (D-101's registry amendment, class in D-104) † — **the opposite: it was seeded**, as the thirteenth `selector_type` row, and one of the twelve that remained once [D-105](decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other) deleted `LIST`. **This row recorded the wrong answer, and the error is the point: the registry was checked against nothing.** Two decision entries wrote the registry while the seeded table was copied from the evaluator's arm list, so `MEMBERS * ROLE(x) + PERSON(y)` did not parse for a whole round, and the repair already circulating read `PERSON(y)` as `LIST` — which subtracts everybody on the list, and is now impossible to write. The instance is told in [the catalog's open issues](appendix/permission-catalog-b-roles-and-open-issues.md#12-open-issues) and in [F-5](#f-5); the rule it produced is that an operand's registry row and its seed are one fact, not two. | [D-101](decisions/round-10b.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree), [F-5](#f-5) |
| 59 | Two expressions with one meaning are **two audiences**: nothing computes semantic equality, and nothing will (D-101) † | [F-14](#f-14) |
| 60 | An audience preview is **per-item and lazy**, and no screen expands a set for more than one item at a time (consequence of D-102's per-item reached set) — **unmeasured at real event sizes, and round 14 added a dependency without changing the assumption.** Nothing pre-pays a preview any more: with no answer cache to warm, the preview computes on open, so its affordability rests on the request memo and on `can_many` existing — two things these documents can name and cannot enforce ([D-114](decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation), [F-15](#f-15)). | [F-15](#f-15) |
| 61 | ~~A cache key is `(person, permission, item)`, and a stale allow is the failure that matters because deny is absolute~~ (D-102, D-099) † — **round 14 deleted this row's subject rather than settling it: there is no cache, so there is no key, no TTL and no stale allow** ([D-114](decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation); [D-111](decisions/round-13.md#d-111--the-permission-cache-is-rebuilt-nightly-on-any-ruleset-change-and-on-request) was the answer it had been waiting for). **Two halves outlive the object they were written about, and both are about meaning rather than storage:** the **item** belongs to whatever a permission predicate is bound to — a compilation carries the item as a *parameter* and holds no item, so nothing resolved while checking one item may be served for another; the **checked date** belongs inside the answer, which is why any computed roster holds dated rows and never "today's set". | [D-114](decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation), [data-model/05 §10](data-model/05c-access-log-and-resolver.md#10-the-resolver) |
| 62 | A `person_group_member` row **lies inside its group's own period** — assumed in §2 of [data-model/02](data-model/02-organization.md#2-person_group_member), reported by integrity check 2 as "a list to read rather than a breach", and **ruled nowhere**. Raised by the page's own author as an assumption these documents are standing on | [data-model/02 §8](domain/04-organization-structure.md#8-open-issues) |
| 63 | ~~A **group** may be ended while a live grant or a live expression names it~~ (D-103, amended in the round after the audience row) † — **refused at save, in both directions**, and on the `-` side rather than the allow side: a live grant on an ended group is safe where it allows and **widens a deny** where it subtracts, so an ended operand is a way to silently empty a set that was narrowing something. `ROLE(x)` needs no such rule and the difference is the finding — an office has no `role.retire` and cannot be emptied quietly, while a group is emptied in one field. The rule itself is [data-model/02 §3](data-model/02-organization.md#3-a-group-is-an-item-a-grant-can-be-written-on-one). | [D-103](decisions/round-10b.md#d-103--an-audience-may-name-another-audience), [data-model/02 §8](domain/04-organization-structure.md#8-open-issues) |
| 64 | An operand's set moves **when somebody writes** — twelve rounds of invalidation lists were built on this and none of them said it out loud † — **falsified by design by [D-107](decisions/round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)**: `OLDER(n)` and `YOUNGER(n)` move at midnight, for one person, with no row to change and no event to subscribe to. **Round 14 closed the gap that acceptance was papering over** ([D-114](decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation)): with resolution live and no answer stored, a birthday moves the answer at the instant it happens, so the ruling that a calendar drift is fine has nothing left to accept. **The write case was never safe either** — the lists could never say *which* writes, and the boundary [D-111](decisions/round-13.md#d-111--the-permission-cache-is-rebuilt-nightly-on-any-ruleset-change-and-on-request) drew left out `membership`, whose `membership.terminate` is the corpus's most safeguarding-shaped write. **The corrected form is not "sets move on writes" but "sets move whenever anything they can read changes": the read path, not a list.** | [F-6](#f-6), [D-114](decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation) |
| <a id="b-2"></a>B-2 | May a merge be reversed? | [D-087](decisions/round-07-08.md#d-087--merge-chains-stay-because-reversing-a-merge-is-a-supported-operation) | Chains stay, and an explicit unmerge is a supported operation. The argument ran backwards: chains were chosen *because* flattening would make unmerge nearly impossible — an assumption resting on a capability nobody had been asked for. |
| <a id="b-3"></a>B-3 | Erasure: what is kept, and for how long? | [D-088](decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short) | Two deliberately opposite clocks. `membership`, `fee_obligation`, `payment` and the anonymised `person` row carry **no clock** — that is the organization's own history; `audit_log` payloads expire after 24 months. The erasure shape was settled earlier in the same entry: redact the person, keep the skeleton. What is left is the legal review of the indefinite half, not the design (assumption 49). |
| <a id="b-4"></a>B-4 | What may a sign-up do when it collides with a live account? | [D-089](decisions/round-07-08.md#d-089--one-live-account-a-colliding-sign-up-files-a-claim-and-creates-nothing) | Refuse, and queue a claim; nothing is created. One live account per person stands, joined by a write-path rule: an account may not reach `active` while an unresolved `identity_hypothesis` names its person. |
| <a id="e-4"></a>E-4 | Does a guardianship know about membership — does a lapse or a renewal touch `right_level`? | [D-115](decisions/round-15.md#d-115--a-guardianship-does-not-know-about-membership-right_level-outlives-a-lapse-and-survives-a-renewal) | No, and that is now recorded in its own right. A lapse leaves `guardianship.right_level` alone, a renewal finds the access untouched, and ending it is an act somebody performs on the guardianship row rather than a state a sweep arrives at. |
| <a id="e-5"></a>E-5 | Who administers a guardianship row? | [D-073](decisions/round-06.md#d-073--guardianship-is-administered-by-its-own-parties-not-by-staff) | The guardian and the subject both act on the row themselves; there is no management-team route. All three shapes this entry proposed — support request, ownership channel, request object — assumed the answer had to come from somewhere other than the people in the relationship. |
| <a id="e-7"></a>E-7 | Can a guardian see the profile but not the medical record? | [D-083](decisions/round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data) | Refused by deleting the premise: there is **no medical record**, so there is nothing to separate — medical data is not different in any way. [D-074](decisions/round-06.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular) raised it by deleting the eighteen `dependent.*` codes that existed for this case; [D-083](decisions/round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data) is the answer, and "a guardian either sees everything or nothing" is the half that survives. |
| <a id="f-4a"></a>F-4a | Should the catalog be generated from the seed, or the seed from the catalog? | [D-072](decisions/round-06.md#d-072--the-documentation-carries-no-sql-the-schema-is-the-orms-job) | Neither: one of the two lists was deleted. "Delete the schema, I will use ORM anyway" took the seed blocks, the DDL and the 19 integrity checks out of the documentation, which ended a reconciliation that had found 22 catalogued permissions with no seed row and 12 more from the `event.*` set. |
| <a id="f-5"></a>F-5 | Which primitive facts can the expression language still not state? | [D-113](decisions/round-13.md#d-113--the-guardianship-channel-has-no-expression-guardians-is-not-a-selector) | None — and the last open bullet was not a missing fact but a name that should not have been in the registry. `GUARDIANS` is not a selector in either arity, the registry drops to **thirteen**, and what the word pointed at is the guardianship channel: a relationship carrying its own `right_level`, not a set anything resolves. The `SCHOOL` question was refused as [D-108](decisions/round-11-12.md#d-108--there-is-no-school-operand-a-selector-may-only-name-a-fact-the-model-stores). |
| <a id="f-6"></a>F-6 | How long may a cached permission answer be reused, and what invalidates it? | [D-114](decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation) | Nothing is cached, so the question has no subject: a check resolves, a request memoizes, and the only cached thing is a compilation. [D-111](decisions/round-13.md#d-111--the-permission-cache-is-rebuilt-nightly-on-any-ruleset-change-and-on-request) had answered "rebuild nightly, on any ruleset write, on request" — one policy, three triggers, no TTL — and round 14 removed the thing underneath both halves rather than picking between them. The heading is the name of what round 13 did, not a description of what exists. |
| <a id="f-7"></a>F-7 | A nightly rebuild of cached answers, or a materialized effective-permission table? | [D-111](decisions/round-13.md#d-111--the-permission-cache-is-rebuilt-nightly-on-any-ruleset-change-and-on-request) | **Dissolved**, not answered — which is written down on purpose, because a dissolved question comes back if nobody records that it dissolved. The two designs turned out to be one job, chosen for another reason (the cadence decided in F-6); nothing was weighed. [D-114](decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation) then deleted the cache the job filled, so both designs are now one deleted and one unbuilt. |
| <a id="f-13"></a>F-13 | Is a rule that resolves correctly but looks odd a warning at save? | [D-109](decisions/round-13.md#d-109--nothing-a-rule-names-is-deleted-deprecated-hidden-disabled--and-a-tab-instead-of-a-report) | A listing, not a lint. [D-109](decisions/round-13.md#d-109--nothing-a-rule-names-is-deleted-deprecated-hidden-disabled--and-a-tab-instead-of-a-report) put a tab on the permissions page and refused every save-time refusal, so a grant naming `ROLE(x)` with no `MEMBERS` term — this entry's entire population — resolves, saves, and appears under **Unusual**. |
| <a id="f-14"></a>F-14 | May two expressions be tested for reaching the same people? | [D-105](decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other) | Refused on three grounds, none of them cost: the stored canonical string is the only identity an expression has ([D-105](decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other), closed for display by F-22); it is not decidable anyway once `AUDIENCE(code)` references are in the tree, so an honest check must advertise what it cannot see; and nobody is deduplicating audiences at this system's size ([D-112](decisions/round-13.md#d-112--the-systems-scale-is-stated-hundreds-of-people-tens-of-registrants-per-event)). |
| <a id="f-15"></a>F-15 | Is the per-item audience preview affordable? | [D-112](decisions/round-13.md#d-112--the-systems-scale-is-stated-hundreds-of-people-tens-of-registrants-per-event) | Yes, once the size was stated rather than imagined — a few hundred people, a few dozen registrants per event, a big camp on the order of two hundred ([D-112](decisions/round-13.md#d-112--the-systems-scale-is-stated-hundreds-of-people-tens-of-registrants-per-event)). The preview stays per-item and lazy: no cap, no background job, no cache of its own (assumption 60). |
| <a id="f-16"></a>F-16 | Is listing the grants that name an audience affordable? | [D-112](decisions/round-13.md#d-112--the-systems-scale-is-stated-hundreds-of-people-tens-of-registrants-per-event) | It is a scan over a small table with a handful of referencing rows each, at the size [D-112](decisions/round-13.md#d-112--the-systems-scale-is-stated-hundreds-of-people-tens-of-registrants-per-event) states. Pagination is a UI nicety, not a requirement, so both [D-103](decisions/round-10b.md#d-103--an-audience-may-name-another-audience) protections that hang off the query stand as written and the weakened fallback this entry kept polished is not needed. |
| <a id="f-17"></a>F-17 | Whom did a grant reach in May, when a nested audience has changed since? | [D-110](decisions/round-13.md#d-110--the-expression-is-the-record-of-whom-a-grant-reached) | The premise was removed rather than the gap filled: the audit record of a grant's reach **is the expression** [D-110](decisions/round-13.md#d-110--the-expression-is-the-record-of-whom-a-grant-reached), so the answer is recomputed against the data of May and these documents do not promise it. The `audience_revision` table this entry recommended is refused — a history of inner expressions is exactly the promise the round declined to make. |
| <a id="f-20"></a>F-20 | Should `WHITELISTED` be seeded once a whitelist feature exists? | [D-113](decisions/round-13.md#d-113--the-guardianship-channel-has-no-expression-guardians-is-not-a-selector) | Refused, and the refusal is not the loss it has been reading like: there is **no state to evaluate**. [D-113](decisions/round-13.md#d-113--the-guardianship-channel-has-no-expression-guardians-is-not-a-selector) confirms rather than re-argues it, having deleted `GUARDIANS` for the same class of error — a name in the language with no row behind it, or a selector naming a mechanism implemented elsewhere. Three refusals, one rule: an operand names a fact the model stores, or it is not an operand. |
| <a id="f-21"></a>F-21 | Who reads the report about what an expression names and what it costs? | [D-109](decisions/round-13.md#d-109--nothing-a-rule-names-is-deleted-deprecated-hidden-disabled--and-a-tab-instead-of-a-report) | Nobody, because there is nothing to read. [D-109](decisions/round-13.md#d-109--nothing-a-rule-names-is-deleted-deprecated-hidden-disabled--and-a-tab-instead-of-a-report) retires the standing reports *about rules* with one tab on the permissions page — **Broken** lists every live rule naming a deprecated, hidden or disabled thing or failing to resolve — and [D-112](decisions/round-13.md#d-112--the-systems-scale-is-stated-hundreds-of-people-tens-of-registrants-per-event) is what made the cost acceptable. Reports outside the expression language survive it: the dead-deny line in *Deny*, and [D-071](decisions/round-05.md#d-071--nothing-forces-a-role-assignment-to-end-the-gate-and-the-report-are-the-control)'s report of assignments nobody forced to end. |
| <a id="f-22"></a>F-22 | May the editor fold and flatten an expression for display? | [D-105](decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other) | Yes, with one hard limit: **display is free, storage is not.** The editor may fold a sum of same-kind leaves onto one line; it may not change the stored canonical string, because the cycle walk, the reserved-name rule and the listing of what names an audience all reason over the stored form ([D-105](decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)). |
| <a id="f-23"></a>F-23 | Is a resolved audience stored as the record of whom a grant reached? | [D-110](decisions/round-13.md#d-110--the-expression-is-the-record-of-whom-a-grant-reached) | "Words only — the expression is the record." [D-110](decisions/round-13.md#d-110--the-expression-is-the-record-of-whom-a-grant-reached). The preview still prints a resolved set before a save, and the log calls it *a rendering on a date*, not a statement of members. The middle position — a reach query — is **not adopted either**, which is the part a skimming reader gets wrong. |
| <a id="ev-3"></a>EV-3 | What happens to outstanding payment requests when an event is cancelled? | [D-076](decisions/round-06.md#d-076--money-that-cannot-be-matched-waits-for-a-person) | Cancelling voids the event's outstanding payment requests, recording why, and money already received becomes a queue item — answered in the finance module rather than here, by [D-076](decisions/round-06.md#d-076--money-that-cannot-be-matched-waits-for-a-person). |
| <a id="h-0"></a>H-0 | What is *the medical record*, which five files cited and none defined? | [D-083](decisions/round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data) | Found while starting the health-records module, and it changed what that module is: the referent was not missing, the **category** was. Everything about a person except name, gender and age is one class of data, held as fields — [D-083](decisions/round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data), with the shape of the layer in [D-084](decisions/round-07-08.md#d-084--descriptive-data-is-organization-defined-at-runtime) and the boundary in [D-085](decisions/round-07-08.md#d-085--the-identity-machinery-stays-structured-the-boundary-is-rules-not-sensitivity). The three options this entry offered are recorded nowhere else, which is right: they were the shape of the question, not of the answer. |
| <a id="msg-1"></a>MSG-1 | May a volunteer message a minor directly? | [D-082](decisions/round-07-08.md#d-082--a-direct-message-to-a-minor-is-mirrored-to-the-minors-guardians) | Yes — mirror it to the minor's guardians, tell the sender, block nothing ([D-082](decisions/round-07-08.md#d-082--a-direct-message-to-a-minor-is-mirrored-to-the-minors-guardians)). Raised by [D-077](decisions/round-06.md#d-077--messaging-is-direct-by-default-broadcast-is-an-ordinary-scoped-permission-and-the-recipient-chooses-the-channel), which declined the restriction rather than forgetting it; three details were settled with it, because "mirror it to the guardians" does not by itself say who the guardians are *to this message*. |

---

## How to answer

**Nothing here blocks anything.** No question on this page is marked 🔴, and none has been since round 4:
the model is settled enough that most answers here change data rather than structure, which is what makes
them worth a moment rather than a decision meeting. Seven are marked 🟡 and eight 🟢. The list below is
what to answer first — roughly half of what it was before [round 13](decisions/round-13.md) closed four of
its nine items, which is worth saying before the list is trusted again.

1. **F-10** — which invariants the ORM cannot express, and who writes those it cannot. The shape list is
   now the shortest path to everything the write path has to carry: an `event` row that obliges a grant row,
   requiredness conditioned on a value in `selector_type`, a check that reads a referenced row, a name
   namespace across three tables, and exclusion constraints over **all** rows rather than over open ones.
   Round 13 handed it a shape it had never had — **an invariant over the *documents* rather than over the
   data**: *every selector name that appears in a document must be a `selector_type` row, and a check should
   be able to say so* ([D-113](decisions/round-13.md#d-113--the-guardianship-channel-has-no-expression-guardians-is-not-a-selector),
   minted when the fourteenth selector turned out to be a prose idiom). That is a lint of prose against a seed
   list, so it belongs to [F-19](#f-19)'s machinery rather than to the write path — and it is now the only
   check that would have caught it.
2. **F-18** — does a role record elected versus appointed, and what does an election write? A property of the
   deleted `position` tables that a real elected committee still needs a place for.
3. **AT-2 / AT-4** — who curates the attribute vocabulary day to day, and whether one permission is trusted to
   guard a trail that holds person data. These are one question seen from two ends: the data that lands in the
   trail arrives through the vocabulary.
4. **EV-2** — how long an event answer is kept once the event it answered is gone. A sharper question now that
   the audit payloads which also held those values have a clock on them (see [B-3](#b-3)).
5. **F-19** — the one item in this file that could be settled this afternoon. A script extracts the
   code-shaped and selector-shaped words from these documents and diffs them against both registries, in both
   directions. It costs no schema. Prose and a seeded registry disagreed four times in ten rounds, and
   round 13 made it five — the fifth is the argument that reads hardest: `GUARDIANS` was a name in six pages of
   prose **and** a registry row that should never have been minted, so **both sides of the diff were wrong at
   once**. What was adopted instead is a hand-run report: a convention, not a guard
   ([D-104](decisions/round-10b.md#d-104--a-permission-codes-last-segment-is-an-action-and-a-registry-that-prose-contradicts-is-a-fiction)).
6. **The legal review**, which is not a question this register can answer and which now has a concrete policy
   in front of it: named membership and fee rows kept indefinitely, audit payloads kept 24 months. Assumption
   49 is its subject — and since
   [D-093](decisions/round-09.md#d-093--the-one-off-import-may-create-memberships-both-ends-dated) the
   indefinitely-kept population includes thousands of imported people who never used the system, which is the
   same judgement at a scale the review has not yet been shown.

Everything else can be answered as we go.

**What happened to the questions that are not here is in the decision log, not here.**
[§ R](#r-resolved--moved-to-the-decision-log) is the register — the question, the decision that owns the
answer, what the answer cost — and the reasoning is in the entry each row links to. Four rounds are worth
reading for what their entries do not say: [rounds 7 and 8](decisions/round-07-08.md) settled identity and
history without changing a table, [round 9](decisions/round-09.md) settled the organization and produced two
lessons larger than its decisions, [round 10](decisions/round-10a.md) redesigned the model instead of
answering anything, and [round 13](decisions/round-13.md) closed questions by removing the machinery that
raised them. Each of those pages now says so at the top.
