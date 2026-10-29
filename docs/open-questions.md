# Open Questions

Everything still unresolved, each with its **schema impact** — what changes once you answer.
Ordered roughly by how much they block.

Marked: 🔴 **blocking** something else · 🟡 **important** · 🟢 can be deferred.

**Resolved items are not deleted.** They are moved to the bottom of this file with a link to
the decision that settled them, so the reasoning survives — see
[§ R. Resolved](#r-resolved--moved-to-the-decision-log).

---

## A. Blocking the core design

### A-1 ✅ **Closed** — the unit type vocabulary is not seeded at all

**Answered: the sub-unit vocabulary is not a question the specification can answer, so it is
not seeded** ([D-054](decisions/round-04.md#d-054--the-sub-unit-vocabulary-is-not-seeded-the-organization-defines-its-own-types)).

`org_unit_type` is **runtime data**, like `role` ([D-052](decisions/round-04.md#d-052--roles-are-runtime-data-the-seed-set-is-not-a-specification)).
The seed contains the root type and nothing else; the organization creates the types it uses.
The previous placeholder — `pack`/`group`/`team`, and before it a
`national`/`region`/`district` ladder — is gone.

**Why this is a better answer than a correct list would have been.** The organization's own
vocabulary is not knowable at specification time, and a wrong word in seed data is harder to
dislodge than an absent one, because it reads as a specification to whoever implements the
system. The *shape* was always the settled part: one root, arbitrary nesting beneath it
([D-035](decisions/round-02-03.md#d-035--one-root-unit-all-sub-units-nest-arbitrarily-beneath-it)).

**What remains true and worth knowing.** Nesting is **permissive by default** —
`org_unit_type_rule` is seeded with nothing, so any type may sit under any other until the
organization states a rule, and a new type is usable the moment it is created. Every rule
added later is a constraint deliberately chosen. The words `pack`, `troop` and `section` still
appear across these docs **as illustration only** — read them as "some sub-unit type the
organization has defined".

**See:** [data-model/02 §10](data-model/02-organization.md#7-seed-data),
[domain/04 §1–2](domain/04-organization-structure.md#1-the-organization-is-one-unit-and-the-unit-is-a-scope)

---

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

## B. Identity and history — closed

All four are answered, in
[round 8](decisions/round-07-08.md#d-087--merge-chains-stay-because-reversing-a-merge-is-a-supported-operation).
What is kept below is the reasoning, because each of these answers bought something *and* paid for it,
and the payment is the half a later editor is tempted to forget.

### B-1 ✅ **Closed** — thousands of roster rows, numbers present, no payment data

**Answered: thousands of rows, one export, 1990s to now, a legacy member number on most of them, no
payment data, and free-text columns alongside**
([D-090](decisions/round-07-08.md#d-090--the-legacy-corpus-is-thousands-of-roster-rows-with-numbers-and-no-money)).

**Re-described one round later, and read this note before the answer above.** The corpus's second half is
not a roster: the rows are **people with their membership periods at the root**, and **events with
attendance**, and they name no units at all.
[D-092](decisions/round-09.md#d-092--the-corpus-is-people-and-events-and-it-names-no-units) retires
the roster frame and
[D-093](decisions/round-09.md#d-093--the-one-off-import-may-create-memberships-both-ends-dated) lifts
the ban on imported memberships that the reasoning below had made absolute one round earlier. The
corrected shape is in [C-5](#c-5--closed--the-corpus-names-no-units-and-none-are-assigned). **What
survived untouched is everything this item was about** — the volume, the legacy number, the absence of
money, and the attribute vocabulary arriving from the free-text columns. Its heading is left as written so
the links into it keep working: it is closed, on a different description of the file.

**The corpus answers the question the import was going to default.** This item's own warning was that
membership-vs-participation gets *harder* with volume, because an inferred open-ended `membership` makes
every 2003 roster a current member with authority today
([D-039](decisions/round-02-03.md#d-039--member-permissions-require-a-current-paid-membership)). That
defect never arrives: **the import carries no payment data at all**, so the exception arm of
"participation unless there is payment evidence" has nothing to fire on. Every historical row is a
`unit_participation`; `membership` rows come only from the current register. The default was correct
and is now simply the rule
([data-model/06 §6](data-model/06-audit-and-import.md#6-open-issues) drops the question accordingly).

**What is unchanged, and was the reason this was worth asking.** The legacy number goes to
[person_identifier](data-model/01-identity.md#7-person_identifier) with `scheme = 'legacy'`, imported
verbatim and never reissued; where it is present the match is **exact**, and the heuristics in
[domain/03 §4](domain/03-identity-and-legacy.md#4-match-signals) are for **backfilling** it rather than
for deciding identity. [D-004](decisions/round-01a.md#d-004--no-automatic-merging-ever) is
*strengthened*, not relaxed: at this size the number-bearing rows are the trustworthy set and the rest
is a work queue a human settles.

**One consequence this answer created that no earlier document predicted.** Under
[D-084](decisions/round-07-08.md#d-084--descriptive-data-is-organization-defined-at-runtime) every
leftover free-text column becomes an attribute code, so one file arrives carrying the organization's
descriptive vocabulary. Those codes are `live` on arrival — a curator reviewed the map as one object,
which is why the map lives on the batch
([data-model/06 §3](data-model/06-audit-and-import.md#3-import-pipeline)) — and `proposed` keeps its
meaning of *improvised later by a person at a desk*. Letting several hundred codes arrive `proposed`
would open the curation queue full and teach everybody that its age signal is noise.

**Still unknown, and still operational.** The exact count and the exact year range. Both are inputs the
batch carries; neither touches a table. What they do decide is A-4's arithmetic — with attendance and
no money, [06 §3.1](data-model/06-audit-and-import.md#31-what-a-source-row-actually-evidences) is the
load-bearing section of the import and the year boundary is what an end date gets inferred from.

---

### B-2 ✅ **Closed** — merge chains stay, because unmerge is required

**Answered: chains, and an explicit unmerge**
([D-087](decisions/round-07-08.md#d-087--merge-chains-stay-because-reversing-a-merge-is-a-supported-operation)).

**The answer ran the argument backwards, which is the interesting part.** Chains were chosen *because*
flattening would make unmerge nearly impossible — an assumption resting on a capability nobody had
asked for. You asked for it, so now the capability is the requirement and the chain is its consequence.
Flattening is closed off, not merely slower, and "flattening is faster" is no longer a trade against
tidiness but a trade against a feature someone named.

**What the question's own framing got wrong.** It costed the two options in query speed. The real cost
of a permanent chain is that it needs rules it did not have: a **cycle must be impossible at the merge**
(a merge is refused when the chosen survivor resolves to the person being absorbed — checked on the way
in, never by a read-side hop limit, because a step limit's only achievement is choosing which wrong
answer to return), and **chain length becomes a signal** — resolution has no bound, but a chain over
three hops is reported, because four merges on one line of people is a statement about the matcher's
queue and not about the row.
[01-identity §10](data-model/08-events.md#10-integrity-checks) treated "survivor itself tombstoned"
as a breach; with chains decided, that is normal, and only the length means anything.

**The asymmetry worth remembering.** A merge can be undone; **the merged period cannot be.** The four
reversal steps in [domain/03 §6](domain/03-identity-and-legacy.md#6-reversing-a-merge) lift the tombstone
and return rows created *before* the merge, but rows created inside the window — above all the
`access_grant` rows, which are flagged rather than guessed — stay one row's history, because the grants
exercised there really were exercised by somebody the record can no longer separate. Unmerging needs no
new permission code: undoing an identity correction is the same act as making one, so it is
`person.merge`.

---

### B-3 ✅ **Closed** — the accounting skeleton is permanent, the audit trail is short

**Answered: the skeleton stays, the trail ages out**
([D-088](decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)).

**The two clocks, which are deliberately opposite.** `membership`, `fee_obligation`, `payment` and the
anonymised `person` row: **no clock**, because that is the organization's own history and the shape this
item had already settled ("redact the person, keep the skeleton") is now *justified* rather than merely
unopposed; `redaction_log.retained_reason` has a real value to hold. `audit_log`: **payloads for 24
months, rows forever** — after the window a row is *reduced*, `old_values`/`new_values` emptied,
everything else standing, so the trail answers "who changed this, when, and were they allowed to" for
the life of the system and stops answering "and to what" after two years.

**What this pays for, and it is not free.** [D-086](decisions/round-07-08.md#d-086--a-sensitivity-mark-grades-what-a-grant-exposes-not-the-table-it-reads)
accepts that `audit.view` exposes whatever the payloads hold; a bounded window is the cheapest control
that organization will ever get for that, and it is the strongest thing
[AT-4](#at-4--is-one-permission-enough-to-guard-a-trail-that-holds-person-data) will hear. **What it
costs is the history that D-085 was justified by.** Values live in one overwritten row, the copy of them
depends on a write path remembering to log, and the copy now expires — so *"what did we believe about
this child in 2019"* is unanswerable twice over, and the honest description of the trade is **no long
history**, not merely **no temporal columns**. If a case ever needs the long version the fix is temporal
values (D-085 reversed), not a longer trail, since stretching the trail stretches exactly what D-086
graded and D-083 refuses to duplicate.

**Also: the legal review this item asked for is narrower now, not gone.** *Indefinite* retention of
named membership and fee rows is a claim that needs a basis, and a decision log cannot grant one; what
exists to review is now a concrete policy instead of a blank, and it is recorded as an
[assumption with a name attached](#i-assumption-index) rather than as settled law.

**Residual, non-technical.** Confirm the accounting retention period with whoever is liable for the
books, and confirm the same 24-month window for `access_log` (**F-8**, proposed at the same value).

---

### B-4 ✅ **Closed** — one live account; a colliding sign-up files a claim

**Answered: refuse, and queue a claim**
([D-089](decisions/round-07-08.md#d-089--one-live-account-a-colliding-sign-up-files-a-claim-and-creates-nothing)).

**The rule that enforces it, and it is not a new table.** One live account per person stands
([01-identity §4](data-model/01-identity.md#4-account)); joined to it, **an account may not reach
`active` while an unresolved `identity_hypothesis` names its person.** The identity review queue already
existed, already records its signals and already has a role for it, so the collision case is a *gate on
activation* plus a hypothesis raised at sign-up — no fourth queue, no new permission
(`person.merge`, already held by `identity_reviewer`).

**Where the danger actually sat, and the threshold is the whole answer.** The tempting version — link
automatically once the e-mail verifies — is [D-004](decisions/round-01a.md#d-004--no-automatic-merging-ever)
under another name, and its failure mode is one human's descriptive data becoming another human's record.
The version you chose has its own failure mode, which is a **brand-new person blocked by a false
positive**, so the trigger is a *strong* match only (exact legacy number, or exact birth date with a
normalized name) and the soft scoring band must not raise a hypothesis at all. Two obligations come with
it and both are checks rather than intentions: **an age check on a hypothesis that is blocking an
account**, alerting rather than logging, because a stalled identity queue is now a specific child who
cannot sign up for a camp; and **a refusal that confirms nothing**, since a sign-up form that answers
"yes, that person exists" is an existence oracle over a roster of children.

**The everyday case is not this case.** "I have a new e-mail" was never a second account —
`account_credential` holds many credentials for one account, so it is an addition to the login a person
already has. The collision case is a person arriving through a door the system did not know they had.

---

## C. Organization — closed

Six questions, closed in two rounds. **C-2 was resolved long ago** and never appeared here: a unit may
not be reparented at all, so a unit that moves is a new unit
([D-036](decisions/round-02-03.md#d-036--units-cannot-be-reparented-a-unit-that-moves-is-a-new-unit)).

### C-1 ✅ **Closed** — the root may not read into its sub-units

**Answered in round 3, closed here for tidiness: no — `scope_exposure` is the only crossing, and no
reporting channel is built**
([D-049](decisions/round-04.md#d-049--the-root-may-not-read-into-its-sub-units-scope_exposure-is-the-only-crossing)).

**What was not obvious until it was answered.** The question existed on the assumption that
the root needed a way *around* the no-inheritance rule in order to report nationally. It
does not, because the root **owns the membership registry and the fees** — so "how many
members in 2019?", "who is currently a member?" and "what fees are outstanding?" are all
answered from the root's own tables, with no exposure at all. Only the sub-units' own
material — their events, their rosters, their local leadership — requires one.

The consequence that will be misread as a bug: `registrar` holds `unit_participation.view` at
organization scope and **cannot** read a pack roster. Scope is an exact match; it reads the
root participation rows, which mirror membership
([D-041](decisions/round-02-03.md#d-041--belonging-to-a-sub-unit-is-a-participation-record-not-a-membership)).
See [domain/06 §2.1](domain/06-authorization-model.md#21-systemadmin).
**D-094 gave this the same shape in the other direction**: imported events belong to the root, so a
unit-scoped "our events" report sees historical camps it did not run — a date filter, not a unit filter,
is what makes either list mean what it looks like it means.

---

### C-3 ✅ **Closed** — a reused unit number is a new unit

**Answered: a new unit, unless somebody records the continuity**
([D-096](decisions/round-09.md#d-096--a-reused-unit-number-is-a-new-unit-unless-someone-records-the-continuity)).

**The question came back as a question, and that was the answer.** Asked whether a number appearing
twice across decades is one unit or two, the reply was *"what is a unit number?"* — which is the right
thing to ask, because a `code` turns out to be a short human label somebody types (`T12`, `4. oddíl`),
not an identity, not a name (names are temporal rows in `org_unit_name`), and not unique: uniqueness is
per parent among live rows, which is precisely why a closed unit's number is free again
([data-model/02 §3](data-model/02-organization.md#5-what-this-page-held-before-round-10)). A label that gets retyped is not a
continuity.

**What was decided, and what was refused.** One `org_unit` per unit that existed; continuity is an
assertion, written as `org_unit_relationship` with `successor_of`, never a match on the label. The
opposite default is what "match on code" does if nobody says, and it invents a thirty-year lifespan.
**What this lost is almost nothing, and the reason is C-5:** the corpus names no units at all, so there
is no import-time collision to get wrong. This question outlived its urgency by exactly one round, which
is worth knowing when reading it.

**See:** [domain/04 §3, §6](domain/04-organization-structure.md#4-a-name-carries-no-identity)

---

### C-4 ✅ **Closed** — a group is filled by a rule and a list, and appointing creates nothing

**Answered: filling rules on groups, and the two things the model refused to do**
([D-091](decisions/round-09.md#d-091--a-permission-group-is-a-rule-and-a-list-at-once-and-a-rule-may-name-another-group)).

**The question was about a convenience workflow and the answer was about the group model, which is why
it is the largest decision of the round.** Asked whether appointing someone to a position should create
the matching role assignment, the answer described *filling rules*: each permission group states who is
placed in it **on top of the manually added people** — "everyone with membership", "a leader role",
"anyone", "members of permission group ABC" — with worked examples from a system where a group's
population derives from enrolment in a course.

Three of those four rules already existed (`everyone`, `all_members`, `unit_leaders`), which is the
quiet part of the answer: **an appointment creates no role assignment, because the derivation belongs on
the group's rule rather than copied per appointment, where it would have to be found again and revoked.**
*(Positions are deleted, D-100 — see the round-10 note at the end of this entry.)*
Two parts were forbidden and are now decided:

- **A group is a rule *and* a list.** `audience.kind`'s builtin-XOR-group split is gone; membership is
  the union of a rule arm, a manual arm and an inclusion arm.
- **A group may include another group.** The one-line ban — *"They do not nest"* — is withdrawn, and its
  reason (cycles, unpredictable answers) is answered the way D-087 answered the same reason for merge
  chains: **the cycle is refused when the edge is saved**, not defended against in the read path.

**What was deliberately *not* taken from the answer.** In the system described, permissions sit on the
group; here a *role* is still held by one named person, because `role_assignment` is the office record
that answers "who was treasurer in 2023" and a derived holder list cannot. That extension is
[F-12](#f-12--closed--may-a-role-be-held-by-a-rule-as-an-audience-is), not a silent schema change.

**What it costs, and where to look for the bill.** A grant's reach is no longer visible in the row that
grants it, so the editor must show the expanded set; and "who could read this in 2023" now depends on a
recomputation of sets that were never stored, on state that has moved, with the audit payload that also
held the answer expired by
[D-088](decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short).
~~**[F-7](#f-7--dissolved--a-nightly-rebuild-of-cached-answers-and-a-materialized-effective-permission-table-are-one-job)
is the route back** and is no longer only a performance question.~~ — **this sentence stood until round 13 and was
the last live claim in this entry pointing at a question that no longer exists.** Two things happened to it, and
the second is the one that matters. **The rebuild arrived** ([D-111](decisions/round-13.md#d-111--the-permission-cache-is-rebuilt-nightly-on-any-ruleset-change-and-on-request))
and F-7 was **dissolved** rather than answered, because a nightly rebuild of cached answers and a materialized
effective-permission table turned out to be one job with two names — **and round 14 deleted the rebuild**
([D-114](decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation)),
which changes nothing here: this paragraph's conclusion rests on the second event, not the first. **Then the bill this paragraph was pointing
at was cancelled rather than paid:** [D-110](decisions/round-13.md#d-110--the-expression-is-the-record-of-whom-a-grant-reached)
ruled that **the audit record of whom a grant reached *is the expression***, with the preview logged only as
*a rendering on a date* — so *"who could read this in 2023"* is a question the system no longer owes anybody an
answer to. Recomputing it stays possible and is **never promised**; the control that stands in place of the lost
answer is procedural, **the editor printing the resolved set before a shared expression saves.**

**Round 10 redrew the line this answer drew, and it still holds — in a different place.** D-091's
*"a group is a rule **and** a list **and** other groups, unioned"* is no longer how a set is built: an
**audience** is now an **expression tree** over named sets with `+ - *` and brackets
([D-101](decisions/round-10b.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree)),
and a **group** is the opposite of a rule — a `person_group` **states its members** and nothing derives them
([D-098](decisions/round-10a.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority)).
So the union that D-091 built into one table became an operator in a language, and the hand-kept list that
D-091 insisted on survived **twice over**: as `LIST` inside an audience, and as the whole content of a
group. **That was round 10; round 11 deleted one of the two** — `LIST` and `audience_member` are gone
([D-105](decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)),
so the hand-kept set survives as a group's roster, or inside an expression as `PERSON(a) + PERSON(b)`, which is
the second of those two and not a third thing. The two halves of D-091's answer that were refusals — an appointment writes no assignment, a cycle is
refused when the edge is saved — both stand, the first confirmed by D-100 and the second widened to
references across audiences by D-103. What is now dead wording here is `audience.kind`, the `unit_leaders`
rule, "level", and the link to §4 of domain/04, which was about positions.

**See:** [data-model/05 §8](data-model/05a-audience-and-grammar.md#8-audience--grants-that-target-a-set-of-people),
[domain/04](domain/04-organization-structure.md) — its §4 held the positions this round deleted

---

### C-5 ✅ **Closed** — the corpus names no units, and none are assigned

**Asked, and answered by correcting the premise: the corpus is people and events, and it says nothing
about sub-units**
([D-092](decisions/round-09.md#d-092--the-corpus-is-people-and-events-and-it-names-no-units),
[D-093](decisions/round-09.md#d-093--the-one-off-import-may-create-memberships-both-ends-dated),
[D-094](decisions/round-09.md#d-094--the-root-unit-owns-every-imported-event)).

This question was not in the register. It appeared when [B-1](#b-1--closed--thousands-of-roster-rows-numbers-present-no-payment-data)
was read against the unit model: the import matches roster rows to `org_unit` rows, `org_unit.unit_type_id`
is required, no sub-unit type is seeded (D-054), and the pipeline's only documented behaviour for an
unknown unit is a warning that does not block. **Something had to create those units, and nothing said
what.**

**The answer removed the question.** *The rows are mainly "person with names, birthdate and when they
were members of the root unit", "events with attendance". Not much more — do not solve assignment to org
units.* So:

- **People** arrive as a `person` plus a **bounded** `membership` — D-090's absolute ban on imported
  memberships is narrowed to what it was protecting, *never open-ended and never inferred from
  attendance* — and ~~each membership brings its root participation row with it, as
  [03-membership §5.1](data-model/03-membership.md#5-unit_participation--deleted-by-d-097) requires~~. **That obligation is
  gone** ([D-097](decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row));
  what survives of the sentence is the part that was load-bearing for the import: **an imported membership
  is bounded at both ends, always**. **No `fee_obligation` is created**: the corpus has no money, and an
  obligation per historical year would arrive as debt.
- **Events** arrive ~~owned by **the root**, which satisfies D-058's exactly-one-unit with a rule instead of
  a judgement~~ — **withdrawn by
  [D-102](decisions/round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)**,
  which deleted `event.org_unit_id` and with it the question of who an imported event belongs to; the
  import writes an `event` row and registrations, and **owes one answer-view grant per event row** instead
  (F-10 shape 1). Attendance becomes registrations — with `not_attending` written for nobody, because an
  export lists who came and silence is not a refusal (D-059).
- **Units are not imported, not created, and not matched.** The parser keeps its `parsed_unit_code` for
  the day an export surprises someone; nothing reads it.

**The consequence to keep in sight: the historical record contains no sub-units.** "Who was in pack X in
2011?" has no answer on day one — not a wrong one, none — and the first answer it has will be typed in by
hand. Nothing in the model is missing; the source cannot say it. This is also the round to note that
**B-1's closure now rests on a different description of the corpus than the one recorded in it**, which
is why B-1 carries a pointer rather than an edit to its own wording.

**See:** [domain/03 §7](domain/03-identity-and-legacy.md#7-legacy-import-pipeline),
[data-model/06 §3.1](data-model/06-audit-and-import.md#31-what-a-source-row-actually-evidences)

---

### C-6 ✅ **Closed** — units carry no restrictions; joining one is somebody else's act

**Answered: no restrictions on units, and no self-assignment anywhere**
([D-095](decisions/round-09.md#d-095--units-carry-no-restrictions-joining-one-is-somebody-elses-act)).

Asked whether a unit type marked `allows_minors = false` should refuse a minor's *position* as it refuses
their participation, the answer refused the premise from both sides: *a unit does not have any
restrictions — however, persons can't assign themselves; they will be assigned to the unit by the
counselors* — and on entry, *into the root unit there is a fee; into the sub-units there is no fee, it is
entirely managed by the organization, including adding more members*.

**Two entry paths, one gate each.** The root: you pay, and the membership flow is the only self-service
entry in the system. A sub-unit: somebody else writes the row, through `unit_participation.manage` held
at that unit, **with no self-scoped variant and none to be added**; the same for position assignment. No
fee anywhere below the root, and no model wants one.

**What was deleted, and what that leaves.** `org_unit_type.allows_minors` goes, with the check it drove
and the seed's `allows_minors = false` on the root type — a flag documented as a safeguard and enforced on
one of two write paths is a receipt, not a safeguard. D-081's requirement is answered with a change of
kind: the rule *"do not place a child where nobody supervises them"* is now enforced by **who may write
the row** — an audited write by a named adult — rather than by a boolean on a type. It is a stronger
control for the wrong-person case and it is **silent on the which-units-are-for-children question, which
the system can no longer answer at all**; with D-043 recording no background checks either, that is the
whole of the organization module's safeguarding story, stated where it can be argued with.

**See:** [domain/04 §1, §4](domain/04-organization-structure.md#1-the-organization-is-one-unit-and-the-unit-is-a-scope),
[data-model/02 §1](data-model/02-organization.md#5-what-this-page-held-before-round-10)

---

## D. Membership

### D-6 ✅ **Closed** — the gate was deleted, so there is nothing left to waive

**Withdrawn by [D-100](decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape),**
which deleted the membership gate outright: `role.requires_membership`, the person-level permission
`system.gate_exempt`, and the row that recorded an exemption for a named person. There is no clause in
the resolver left to waive, and no flag a configuration screen could weaken. What carries the control now
is the **expression** — a grant that should stop with membership says `MEMBERS * ROLE(x)` and one that
should not says `ROLE(x)` — so the exemption this entry recorded became a different operand rather than a
permission. The posture reversal, and the three things standing in for the deleted guard, are in D-100 and
in [domain/06 §6.1](domain/06-authorization-model.md#61-members--the-membership-test-moved-into-the-expression).

**Answered, and kept because the reason still applies to its replacement**
([D-051](decisions/round-04.md#d-051--the-membership-gate-is-waived-by-a-permission-not-only-by-a-role-flag)):
the gate was waived by a person-level permission in addition to the role-level flag, because otherwise
the 1 January sweep locks the administrator out of the system on the day it needs repair. **That argument
did not go away; it moved.** It is now the argument for why the seeded grants name `MEMBERS` explicitly
rather than assuming it, and it is the first thing to re-check if a `MEMBERS` term is ever added back to a
grant nobody thought about.

**"Which other roles carried it" was never answered here, and there is nothing left to answer.** Roles are
runtime data ([data-model/05 §3](data-model/05-authorization.md#3-role--an-office)); the exemption was a
configuration act, not a specification fact. ~~An `access_grant` cannot lift the membership gate, because
`system.gate_exempt` sits in the `system` namespace and so can only arrive through a role~~ — the guarantee
was real and its subject is gone; its descendant is the one D-100 records instead, that a role confers
nothing, so nothing arrives through an office at all until a grant says so.

**The report survived, renamed.** What was check 7b is now the standing *report* D-100 lists among its
controls — §11 of [data-model/05](data-model/05d-invariants-and-seed.md#11-invariants-to-verify) was renumbered for
round 10 and no longer has a gate to report on.

---

### D-7 ✅ **Closed** — the root participation row is deleted

**The subject of this question was deleted by
[D-097](decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row),** which took
`unit_participation` with it, root row included: there is one unit, it is the organization, and it is a
scope rather than a row, so there is no row to extend at renewal. The answer below stands as the answer
that *was* given, and the reasoning behind it is not dead —
[data-model/03 §9](data-model/03-membership.md#9-open-issues) keeps it visible because the argument about
backdated periods is what the renewal rule in §3 still rests on, and
[§5](data-model/03-membership.md#5-unit_participation--deleted-by-d-097) is the tombstone. The accepted cost below — a lapse
erased from the roster view — has no carrier any more, which is one of the losses D-097 records rather than
replaces.

**Answered: it is extended, not closed and reopened**
([D-050](decisions/round-04.md#d-050--a-renewal-inside-the-window-extends-the-existing-root-participation-row)).

The yearly sweep moves the root row's `valid_to` forward to the expiry date rather than
closing it, and a renewal inside the window stretches that one row over the new period. The
join between the two is **person and date** (`new_m.valid_from = up.valid_to`), not a
membership FK — the participation table has none, deliberately.

**The accepted cost, recorded rather than hidden.** This erases the visual evidence of the
lapse: a person who lapsed and renewed looks, in `unit_participation`, exactly like a person
who never lapsed. Accepted because `membership` remains the authority on payment and the
lapse is fully visible there, while the participation table answers a *roster* question — and
for "who was in this pack when" a child who was present across the period has one answer, not
two.

**See:** [data-model/03 §5](data-model/03-membership.md#5-unit_participation--deleted-by-d-097) (the §5.1 this used to cite
was the root-row subsection; it is gone, and §5 is kept deliberately as the tombstone)

---

### D-8 ✅ **Closed** — retired with the table it asked about

**Retired by [D-097](decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row),**
which deleted `unit_participation`, so there is no table left to add a nullable `membership_id` to. This is
**not the refusal of the argument but the removal of its subject**, and the refusal still matters:
[data-model/03 §9](data-model/03-membership.md#9-open-issues) records the retirement and keeps the reasoning,
because the same argument recurs one table later — participation had to survive without a membership, which
is exactly why `person_group_member` is keyed on a **person** and not on a membership
([data-model/02 §2](data-model/02-organization.md#2-person_group_member)). Read the answer there rather than
re-arguing it here.

**Question, as asked.** A nullable `membership_id` on `unit_participation` would give referential
integrity between "paid up" and "takes part", at the cost of being unenforceable for imported
historical rows, where no membership exists to point at.

**Impact, as assessed.** Integrity vs. import coverage. The current design chose person-based linkage for
exactly that reason — and round 10 left that reason intact while deleting the table that had it.

**See:** [data-model/03 §5](data-model/03-membership.md#5-unit_participation--deleted-by-d-097),
[data-model/03 §9](data-model/03-membership.md#9-open-issues)

---

### D-9 ✅ **Closed** — `household` is removed entirely

**Answered: drop it** ([D-057](decisions/round-04.md#d-057--household-is-removed)).
`household`, `household_member`, `fee_obligation.household_id`, its CHECK arm,
`ix_obligation_household` and integrity check 7 are all gone.

**Why removal rather than a derived view.** D-037 had already taken the load-bearing half —
the fee is flat and per person, so there is no family price. The two survivors were both
served by tables that must exist anyway: a billing address is a `person_contact` row where
`contact_type = 'postal' AND purpose = 'billing'`, and "who lived at this address in 2003?"
is a query over that table's own `valid_from`/`valid_to` history. The household table was
duplicating the address under a second key, and the copy had already gone stale — its
`postal_address` was documented as denormalised *from* the contact row, with nothing keeping
it true.

**The safeguarding property is untouched, and this is the point to check first.** Shared
address never granted access: **a child's records are reachable only through a guardianship
row**, whatever the household arrangement beside it. Removing a table that granted nothing
cannot grant anything.
[D-019](decisions/round-01b.md#d-019--household-membership-grants-no-access) stays in the
log, marked superseded, because "why does living together not imply access?" will be asked
again.

**The one thing genuinely lost.** A household was a group with a name and its own lifetime;
two people at one address are now related by a query, not a row. There is nowhere to hang
"the Novák family" as a first-class thing. Accepted because nothing used it. If family-level
communication or a family discount is ever wanted, the grouping comes back as a group with a
period — not a fake person.

**One knock-on worth knowing.** Finance question 2 (family/sibling discounts) is now *more*
open, not less: a per-family discount needs the grouping designed again before it can be
priced. A per-person discount is unaffected.

**See:** [data-model/04 §3](data-model/04-relationships.md#3-there-is-no-household-table)

---

## E. Guardianship

### E-2 ✅ **Closed** — the system takes no position on majority

**Answered: nothing at all.** No job, no review queue, no computed candidate date
([D-069](decisions/round-05.md#d-069--guardianship-ends-when-a-person-ends-it-the-system-takes-no-position-on-majority),
reversing D-024). A guardianship is ended by a person ending it.

**What was wrong with the review queue** the docs had recommended: it was still automatic, and
it computed a date the system has no authority to assert. Deferring a decision is not the same
as declining to make one.

**This closes E-2 and immediately opens E-5 below.** With no automatic end and no queue, the
only exit is `guardianship.end` — and the adult who is the *subject* of the row holds no
permission over it.

### E-5 ✅ **Closed** — the parties administer their own row

**Answered: the guardian and the subject both act on the row themselves; there is no
management-team route** ([D-073](decisions/round-06.md#d-073--guardianship-is-administered-by-its-own-parties-not-by-staff)).

**All three of the shapes above were wrong in the same direction.** Support request, ownership
channel, and request object each assumed the answer had to come from somewhere *other than the
people in the relationship*. It does not. A guardianship is a relationship between two people, both
of them are principals on the row, and either may end it. A guardian may add another guardian. No
staff approval, and no workflow invented for the purpose.

**It is not the ownership channel, which is why option (2) was the right answer for the wrong
reason.** Ownership is *your own record*; a guardianship row belongs to neither party alone. The
guardianship channel simply gained a direction — from "may guardian G act on D's records?" to also
"may a party act on this row?" — and the resolver still has four channels.

**The gap this closes was real, and it is now closed at the only place it could be.** D-069 removed
both the automatic end and the queue, leaving `guardianship.end` as the sole exit and the subject
unable to reach it. That was a door with no handle on the inside.

**Two things this opens, both below.**

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

### E-7 ✅ **Closed** — one level cannot separate the medical record from the profile, and nobody wanted to

**Raised by [D-074](decisions/round-06.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular),
which deleted the eighteen `dependent.*` codes that existed for this case.**

**What could not be said.** *"This guardian may register the child for events but may not read the
medical record."* *"Read-only, except not the health data."* *"The grandmother may see the roster and
nothing else."* A guardian either sees everything about the child or nothing. The case the old
namespace was built around — a court order restricting one parent's medical access while their other
access continues — was inexpressible.

**Why it was accepted anyway.** Three values a volunteer treasurer can hold in their head, versus
eighteen whose differences nobody outside a court uses. And the alternative had a failure mode of its
own: a granular list that administrators ticked without reading is not more protective than a coarse
one, it only looks more precise.

**Answered (round 7), and the answer was not the one the question expected.** The question assumed a
medical record worth separating. Asked directly, you answered: *"ignore 'court order', guardian has
all rights on a child if it's permissions say so. Medical data is not different in any way."* Recorded
as [D-083](decisions/round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data).

**So this closes as a dissolved question, not an answered one.** "Everything except the medical record"
is not a sentence the organization wants to say, which means the missing granularity was never a gap —
it was the absence of a feature nobody asked for. There is now no inside and outside to the person
record, because there is no separate record: everything the system knows about a person other than
name, gender and age is one class of data, reached by `person.view` and governed by the guardian right
level whole.

**What the closure trades away, in one sentence and on purpose:** a system that cannot express
*"everything except the diagnoses"* cannot express an arrangement a court might order, and will
express it instead as a guardian who either has the record or does not. If the case arrives in
reality, the route back is **one new grant scope over a defined set of data, argued once as a
decision entry** — not a namespace of eighteen codes, which is what was deleted and why this question
existed.

**Impact.** None left open. One value, three choices, over the whole record.

**See:** [D-083](decisions/round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data),
[data-model/09-attributes.md](data-model/09-attributes.md),
[glossary — Descriptive data](glossary.md#personal-data).

### E-3 🟢 Guardian acting for an adult child

**Question.** Can a parent register their adult child for an event, with the child's consent?

**Recommendation.** An explicit consent-based delegation, not a guardianship — the legal
basis differs and `access_grant.is_delegated` already supports it.

**Note.** Now that grants can target **audiences**
([D-042](decisions/round-02-03.md#d-042--grants-may-target-audiences-not-only-individuals)),
the *event-wide* version of this question — "register everyone in this group" — is answered
without touching guardianship at all. What remains is the individual case.

---

### E-4 🟢 Guardianship lifetime, now that the gate it was exempt from is gone

**Question, restated — and it is sharper than it was.** Guardianship used to be *exempt from the
membership gate*
([D-039](decisions/round-02-03.md#d-039--member-permissions-require-a-current-paid-membership)), so a
lapsed parent kept their guardian's right over their child's records. The gate is now deleted
([D-100](decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)),
and that does not resolve this — it **removes the thing that used to make the exemption visible**. The
membership test moved into grant expressions, and a guardianship is not a grant: it is one of the three
channels, reached through `guardianship_permission`, and there is no expression in it to write `MEMBERS`
in. So a lapsed parent keeps their right exactly as before, **and there is now no mechanism anywhere that
could condition it** short of a new rule in the resolver. Confirm that is intended rather than inherited:
an unpaid parent and a paid one are indistinguishable inside the guardianship channel, and they have become
indistinguishable everywhere else too. ~~unless somebody writes `MEMBERS * GUARDIANS(p)` into a grant — which
grants the *permission*, not the *relationship*, and is therefore not the same lever.~~ — **and that last lever
has now been removed, which converts this entry from "confirm it is intended" to "there is nothing left to
confirm".** `GUARDIANS` **is not a selector in either arity**
([D-113](decisions/round-13.md#d-113--the-guardianship-channel-has-no-expression-guardians-is-not-a-selector)):
no expression can name a ward's guardians, so a grant cannot condition on guardianship either, and **this entry's
conclusion — that membership and access deliberately do not meet inside the guardianship channel — is now a
structural fact rather than an oversight with an escape hatch.** **D-113 also sharpens what the channel is**, in
a way this entry should not be read without: a check reads **`guardianship.right_level ∈ none | view | write`**
off a live `guardianship` row, and `guardianship_permission` is that value's **history** — no grantee, no
permission code, no audience, no expression column — so **there was never anywhere in it for a selector to be
seeded**, and a guardian's authority is *a level over a child*, not a list of codes.

**Impact.** None structurally, and that is the answer being asked for in writing. It is the one place where
membership and access deliberately do not meet, and "why can this person still see that?" should have a
written answer rather than a retired gate to blame.

---

## F. Authorization

### F-1 ✅ **Closed** — the catalog stays comprehensive and granular

**Answered: keep the catalog large and granular; more permissions arrive with the unbuilt
modules** ([D-055](decisions/round-04.md#d-055--the-permission-catalog-is-deliberately-comprehensive-and-granular)).

It is a **menu**, not a checklist. Administrators assign people only the permissions they
actually need, and that is only possible if the capabilities exist as separate rows to assign.
The parts of the question that remain — the exact contents — are tracked in
[appendix/permission-catalog.md §12](appendix/permission-catalog.md#12-open-issues) and will
move as events, documents, communication and reporting land.

**Note the asymmetry with roles, because it looks like an inconsistency and is not.** Roles
are *runtime data* the organization invents ([D-052](decisions/round-04.md#d-052--roles-are-runtime-data-the-seed-set-is-not-a-specification));
permissions are *capabilities the code implements*. You cannot assign a power that is not
expressible in the schema, so a comprehensive catalog costs only rows. A comprehensive *role*
list, by contrast, would be a specification pretending to be data.

**The sharp edge.** Granularity only buys least-privilege if the grants are narrow, and
[D-007](decisions/round-01a.md#d-007--every-resource-has-an-admin-level-that-subsumes-narrower-ones--reversed)
means any new permission in a namespace is **retroactively held by everyone with that
namespace's `.admin`**, with no assignment written. That is intended — and it is the reason
`role.edit` is marked 🔒🔒.

---

### F-3 ✅ **Closed** — nothing forces an assignment to end

**Answered: nothing — rely on the gate, and on the report.** No `NOT NULL`, no application-layer
requirement, no per-role policy
([D-071](decisions/round-05.md#d-071--nothing-forces-a-role-assignment-to-end-the-gate-and-the-report-are-the-control)).
The docs had recommended *yes, at the application layer*; that recommendation is withdrawn. **Half of the
answer's title has since lost its subject** — the gate is deleted, D-100 — and the report half is what the
decision now rests on entirely, which is argued immediately below rather than papered over here.

**Why the recommendation was wrong, as argued at the time.** It claimed the membership gate makes an
open-ended assignment *more* dangerous. It makes it less: the gate already expires authority for exactly
the population an expiry date would target, and ties expiry to a fact the organization maintains on purpose
rather than to a date somebody typed. That argument is **withdrawn along with the mechanism**; the
conclusion did not need it, and the paragraph after this one is the one to read.

**The residue, restated — the answer survives its own reasoning.** This decision leaned on the membership
gate, and [D-100](decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)
deleted the gate, so the sentence "`unit_leader` and `assistant_leader` have `requires_membership = false`"
names a column that no longer exists. **The residue it described is bigger now, not smaller:** the case used
to be a handful of roles flagged as exempt, and it is now **any grant written without a `MEMBERS` term**,
which is the default way to write one. So the conclusion is unchanged and the emphasis is: a periodic human
review over open-ended rows is not a nice-to-have, it is the entire defence. D-053 put the weight on
`role_assignment.valid_to`; that table is `role_holder`, the column is the same, and D-100 declined to add a
guard rail there too. Read the two decisions, and D-100's three controls, as one set.

**See:** [data-model/05 §4](data-model/05-authorization.md#4-role_holder--who-holds-an-office),
[§4's own conclusion](data-model/05-authorization.md#nothing-forces-a-holder-row-to-end-and-the-report-is-the-control)

### F-4 ✅ **Closed** — the question was answered by deleting the premise

**Answered obliquely and decisively.** Asked whether `person.admin` should subsume
`person.merge`/`person.redact`, the answer was *"Only the system should have admin permissions,
not the individual items"* — which removed the subsumer rather than choosing between the two
options offered
([D-068](decisions/round-05.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle),
reversing D-007).

**The question moved rather than dissolved — and then moved again.** A role bundling all `person.*` codes
still reaches `person.merge` and `person.redact`. What changed at the time was *where* that is decided: it
used to be a resolver rule, invisible in every role editor and true for every resource whether or not anyone
wanted it. It became **the contents of a role somebody wrote** — and the answer given in round 6 named a
table: ~~visible in `role_permission`, dated, alarmable, and audited on change~~.
[D-100](decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)
deleted `role_permission`, because **an office confers nothing**, so the bundle is now the live **grant
rows naming `ROLE(x)`**, one row per code, each dated and each auditable in its own right. The guidance is
the same sentence with a different carrier, and it got *more* visible rather than less: there is no longer a
role editor where the bundling could hide, because there is no such editor — you have to look at the grants.

**What carries the guidance now** is the seed table and the grant rows beside it, not the schema: no seeded
role is meant to have `person.merge`/`person.redact` bundled with routine `person.edit`, and
`identity_reviewer` is the one that deliberately holds `person.merge`. A role that *does* gather a resource
including its irreversible codes should be named for it.

**See:** [appendix/permission-catalog.md §11](appendix/permission-catalog.md#11-roles--proposed-seed-set)

### F-4a ✅ **Closed** — the catalog is the only list now

**Surfaced by D-068, not created by it.** When the two were reconciled during that work,
**22 documented permissions had no `INSERT` row** — including `unit_participation.view`, which
five of the catalog's *own* seed roles assign, and `person.redact`, one of the two codes
D-068 exists to protect. A further 12 were the `event.*` set, catalogued when events were
designed and never seeded. **All 34 are now fixed**; both sides list 91 codes and the diff is
empty.

**Why nobody noticed, which is the part worth keeping.** [D-068](decisions/round-05.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle)
made a harmless inconsistency into a live one. Under the prefix-match wildcard, a role holding
`unit_participation.admin` reached `unit_participation.view` whether or not a `permission` row
existed — the catalog could advertise a capability the database could not name, and nothing
noticed, because the wildcard papered over the gap and only the permission editor showed it.
**The cushion was itself the bug's hiding place.**

**What is open is the discipline, not the data.** There is **no SQL check for this** — one side
is a Markdown file. Integrity check 18 reads the table, so it can find a permission no role
grants; it cannot find a permission the catalog promises and the seed never contained. The
reconciliation is scripted in [data-model/05 §12](data-model/05d-invariants-and-seed.md#12-what-the-organization-starts-with),
and it is a review rule, not a test.

**The actual question:** should the catalog be **generated from** `permission` rather than
maintained beside it? That is the only change that makes the two incapable of disagreeing.
Against it: the catalog's value is its prose — the sensitivity marks, the rationale notes, the
§5a and §8a argumentation — none of which belongs in a table. A middle path is to keep the
prose in Markdown and generate the code tables from the database, so only the commentary can
drift.

**Impact.** If left manual, this recurs on every module added, and D-055's decision to keep
growing the catalog guarantees modules get added.

**✅ Closed — answered by deleting one of the two lists.** Asked whether to generate the catalog
from the seed, the answer was **"delete the schema, I will use ORM anyway"**
([D-072](decisions/round-06.md#d-072--the-documentation-carries-no-sql-the-schema-is-the-orms-job)),
which removed the seed blocks, the DDL and the 19 integrity checks from the documentation
altogether.

**The generation question dissolved rather than being settled, and the difference matters for what
is still true.** Nothing is generated, because there is no longer a table to generate *from*.
**The catalog is now the only list that exists** — which answers the drift problem completely and
removes, at the same time, the executable form of every rule the DDL had been carrying. That trade
is D-072's to make and its entry records what it costs: integrity check 18, the orphaned-permission
check that was the safety net for the deleted wildcard, is now a prose instruction rather than a
query. **A check nobody runs is a convention.**

**What remains genuinely open is the thing the check was guarding.** With no seed and no wildcard,
a capability in the catalog that no role bundles is unusable and silent. It is now caught by review
of the catalog, and there is no automated backstop at all.

---

### F-5 ✅ **Closed** — nothing is missing from the registry, and the last gap was a selector that should not have been in it

**Answered by [D-113](decisions/round-13.md#d-113--the-guardianship-channel-has-no-expression-guardians-is-not-a-selector),
and the answer came from the wrong direction, which is the part worth keeping.** This entry spent three rounds
asking **which primitive facts the language still cannot state**, and its final open bullet turned out not to be
a missing fact at all: `GUARDIANS` **is not a selector, in either arity**, the registry **drops to thirteen**,
and the thing the word was pointing at is **the guardianship channel — a `right_level` of `view` or `write` over
a child, which is a relationship carrying its own authority and not a set anything resolves.** A guardian at
`write` may already perform any action whose subject is their ward, so an operand aimed at a ward's guardians
would have offered **a subset of what those people already hold**, one code at a time. **The count of open
bullets in this entry is zero**: round 12 closed the age bullet with `OLDER`/`YOUNGER`, round 13 closed this
one by deletion rather than by addition, and the `SCHOOL` question was refused as
[D-108](decisions/round-11-12.md#d-108--there-is-no-school-operand-a-selector-may-only-name-a-fact-the-model-stores).

**What it cost, since the cost is real and D-113 records it rather than smoothing it.** Deleting the operand
removes **no capability** — but it does confirm absent **a thing nobody ever wrote down wanting**: nothing in
this language can now denote *"whatever guardians the person this item is about has"*. D-113's own first draft
thought that was a loss and minted an open question for it, **then the user's ruling dissolved the premise ten
minutes later**, because the worry presumed `view`/`write` is a ceiling on *codes* when it is a ceiling on *acts
about that child*. **So there is no F-24.** The residual case — *guardians of this child should get at something
that is not about the child* — is not a permissions question: **it is a list of people, and lists are groups**,
which is why the substitute is a named `GROUP(x)` with kept members and not a new operand. **A derived guardian
list is a feature this system does not have**, checked rather than assumed, and saying so in the entry that
closes this one is the honest place to leave it: a missing feature is a decision entry, never an operand nobody
checked for.

**One seam the two rulings left between them, recorded here because neither of them owns it.**
[D-109](decisions/round-13.md#d-109--nothing-a-rule-names-is-deleted-deprecated-hidden-disabled--and-a-tab-instead-of-a-report)
ruled that **nothing a stored expression may name is ever deleted while a rule may name it** — you give it a state
instead. D-113 then **deleted a row outright**, and the argument that carries the deletion is about *authority*
(`write` already reaches any act about the child), not about *what is already sitting in `audience_operand`*.
**The bound form could never be saved; the explicit one plausibly could.** `GUARDIANS` shipped with
`takes_argument` optional and `argument_type` `person`; the item-type match is a check the **binding** rule reads,
and the events module says out loud that **the explicit form stays legal at the unit**
([data-model/08](data-model/08-events.md#selectors-that-bind-to-an-event)) — so `GUARDIANS(p)` on a
unit-scope grant is not obviously refused by any save rule I can point at. **If such a leaf exists anywhere,
deleting its row turns it into a failing leaf, which is the state D-109 retired deletion in order to prevent and
the state D-109 said only a redacted person could still produce.** What is needed is one sentence, in D-113 or at
the resolver: **either no `GUARDIANS(p)` was ever savable — name the check that refused it and the seam closes —
or existing leaves are found and repointed, the way a person merge repoints leaves.** **This is deliberately not a
new F-entry**: it leaves no design choice open, only a migration statement missing, and *"run one query over the
leaves and fix the rows"* is not a question to put in front of anybody. It is here, in the entry that closed the
operand, so that the row deletion does not read as cost-free.

**Two rules this closure leaves behind, both belonging to F-10's list rather than to this entry.** First: ***every
selector name that appears in a document must be a `selector_type` row, and a check should be able to say so*** —
a lint of documents against a seed list, which is a strange thing to want until the fourteenth selector turns out
to be a prose idiom. Second, D-113's verdict on the method this file trusts: **a count is a good alarm and a bad
oracle.** Fourteen disagreed with six pages using a fifteenth name, and that alarm correctly said *something is
wrong* twice and correctly said *which side was wrong* neither time — the first pass blamed the prose, the ruling
blamed the registry.

**Round 10 answered the question that was asked and left a different one standing.** C-4's four filling
rules — "anyone", "everyone with membership", "a leader role", "members of a named group"
([D-091](decisions/round-09.md#d-091--a-permission-group-is-a-rule-and-a-list-at-once-and-a-rule-may-name-another-group))
— all exist now, and none of them is an audience: they are the operands `EVERYONE`, `MEMBERS`, `ROLE(x)`
and `GROUP(x)`
([data-model/05 §8](data-model/05a-audience-and-grammar.md#the-selector-registry),
[D-101](decisions/round-10b.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree)).
**The seeded audiences went the other way — down to two** (`everyone`, `all_members`), because a built-in
audience turned out to be a sentence someone else composes rather than a row the code ships. So this entry
is no longer "how many built-ins"; it is **which primitive facts the language still cannot state**, one
bullet per missing fact. **No count appears in this heading, because the count changed while this entry was
being written** — see the first answer below.

**Answered while this entry stood open, and answered against its own assumption:** `PERSON(x)` is a seeded
row, not shorthand, **and the registry was one row short when this entry said so in bold.** `PERSON` arrived
as the **thirteenth** row — `takes_argument` true, `argument_type` `person`, `binds_to_item` false — added by
the amendment paragraph at the end of D-101's grammar
([D-101](decisions/round-10b.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree)).
**The table is twelve rows now**: the round after this one deleted `LIST` and the table behind it
([D-105](decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)).
That is the honest sequence rather than the tidy one, and it is written out because this entry has now printed
a count that stopped being true twice — which is exactly the argument for why the heading carries no number.
What this entry got right was the *need*: a grant does not need the operand, because the grantee pair already
names one person, but an **audience** does, because a saved expression aimed at several things cannot carry a
grantee — so the "except Honza" in `MEMBERS * ROLE(x) + PERSON(y)`, the control that replaced the membership
gate's exemption, had nowhere to live. The registry was written from the evaluator's arm list instead of from
the grammar, and an arm list copied from an implementation loses the arm nobody has implemented yet. As a
`selector_type.code` it also **joins the reserved namespace**, which is the reservation this entry's Impact
used to ask for. **The wrong repair was already circulating**: the pages that noticed the gap read
`PERSON(y)` as `LIST`, and that is not a wider spelling of the same thing — `LIST` is one set of several
people belonging to one audience, so subtracting it removes everybody on it. The defect class is
[F-19](#f-19--closed--a-permission-code-is-a-row-prose-names-codes-and-nothing-checks-the-two), which this
round also closed. **That particular repair is now unwritable**: one spelling is left, so there is nothing to
substitute — the only way in which
[D-105](decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)
ended a bug this entry described without anybody deciding to end it. **The class it was an instance of is
untouched**, and `PERSON(x)` is now the operand that would be misread, since it went from a curiosity to the
only way to name a set of people by hand.

**Round 11 found the same defect again, this time in prose.**
[domain/06a](domain/06a-audiences-and-selectors.md#the-selectors) keeps its own copy of this table for readers
who never open the data model, and that copy had never grown a `PERSON` row or an `AUDIENCE` row while still
carrying the `LIST` row D-105 deleted — so the page that teaches this language to everybody who is not
implementing it taught a language in which two of the twelve operands could not be written, and taught one
that no longer exists. **Third instance of one defect, one round apart:** a decision entry adds an operand,
the seeded table gets the row because somebody is holding it, and every prose copy is updated by whoever
happens to read it. **F-19 counted four instances of this defect in ten rounds, every one of them a table
disagreeing with prose; this one is prose disagreeing with prose, which is why no diff over rows would have
caught it either.** The remedy is the one [F-19](#f-19--closed--a-permission-code-is-a-row-prose-names-codes-and-nothing-checks-the-two)
adopted and D-104 argued for, aimed at documents instead of codes: **a token written in three files is not
one fact stored three times, and nothing in §11 can see any of the three.**

**Retired by the round, listed so nobody re-raises them.**

- **"everyone who registered for this event"** — shipped four times over as `ATTENDED`, `PLACED`,
  `CONFIRMED`, `ON_WAITLIST`, plus `ORGANIZERS`, all bindable to the event a grant is scoped to (D-102).
  The joining-instructions rule this bullet used to ask for is `ATTENDED`, and it is *more* precise than
  what was asked: the old rule could not distinguish someone the capacity refused.
- **"everyone in this section and everything under it"** — there is no hierarchy to walk
  ([D-097](decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)), so the
  D-031 argument this bullet carried is not answered but **unaskable**. `unit_ancestors()` is deleted.
- **"are parameterised groups seeded per instance or created on demand?"** — moot. There were never any
  per-instance audiences to parameterize once there was one unit, and the three parameterized seeded
  audiences are gone with the names they carried (§12 of
  [data-model/05](data-model/05d-invariants-and-seed.md#12-what-the-organization-starts-with)).

**The bullets this entry carried, and where each one stands now.**

- ✅ ~~**A bound `GUARDIANS` cannot be written on any legal grant.**~~ — **closed by
  [D-113](decisions/round-13.md#d-113--the-guardianship-channel-has-no-expression-guardians-is-not-a-selector),
  and the finding is kept visible in full because it is the evidence that the registry and the prose had drifted
  apart.** The registry gives `GUARDIANS` `binds_to_item = true` with `argument_type = person`, and §8 says the
  binding check compares that column against the grant's item type. But `grant_scope_type` is seeded with `unit`,
  `event`, `person_group`, `role` and `document` — **there is no `person` item**, because authority over a person
  arrives through the guardianship *channel*, not through a grant. So the bound form passes the arity check and is
  then refused by the binding check on every scope that exists, and §12's claim that `GUARDIANS` may be "bound as
  `GUARDIANS` on a grant about that person" describes a grant that cannot be saved. **The two options this entry
  offered were "`person` joins `grant_scope_type`" and "`binds_to_item` is false for `GUARDIANS`", and D-113 took
  neither: it removed the row.** *Was the contradiction real?* Yes, on both sides of it — which is why the bullet
  stays verbatim rather than being summarised. **The registry had a row that should not have been in the registry
  at all**, so the contradiction this entry read as *"the model cannot host this operand"* was in fact *"the model
  never had this operand"*, and the six pages that used the argument-less form were describing a channel with a
  selector's syntax. **A defect report that is accurate about the symptoms and wrong about the cause is still the
  most useful kind of defect report**, and this is the one that found it: the registry row, the §8 binding check,
  the §12 claim of a grant that could not be saved, and the absence of any `person` item type were all correctly
  observed and all correctly refused to add up. **D-113 also clears the word out of the prose that used it live**,
  and the site that mattered most is `domain/06` §6.2's operand table, whose row promised *"guardians of the
  person this item is about"* — a selector no grant could write — and now stands struck with the channel spelled
  out in its place. **No guardian-shaped operand is bound to anything, because there is no guardian-shaped
  operand**, so `binds_to_item` keeps its meaning and loses its exhibit: what justifies the column now is
  **the five event operands** (`ATTENDED`, `PLACED`, `CONFIRMED`, `ON_WAITLIST`, `ORGANIZERS`), which is a large
  and ordinary reason instead of one strange case that was never real.
- **~~Age is now unsayable in the model, and one of these questions will want it.~~ — closed by
  [D-107](decisions/round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded):
  age was a set all along.** The bullet argued that age has no table to point at — `argument_type` names a
  table, an age band is a range and not a row — and offered two exits: seed a band table for the sake of two
  or three rows, or write down that **age never enters the selector language**. **Both exits were wrong in the
  same direction, and the direction is the interesting part.** `argument_type` has gained a scalar: `OLDER(n)`
  takes a whole number of years, which points at no table and needs none. And the premise under the whole
  bullet — that an operand has to be a *stored* set — is the sentence D-107 deleted, along with "*an attribute
  is not a set of people … age is not*". `OLDER(n)` and `YOUNGER(n)` are seeded rows now, read against the
  birth date **on the date being checked**, so `event.register_self` granted to `MEMBERS * YOUNGER(15)` states
  a ceiling in this language. **EV-1's escape hatch is therefore open rather than closed, which changes the
  reason that entry is closed and not its answer.** What the bullet got right is still true and is why it is
  written up as a closure instead of deleted: age arrived exactly the way the rules for new facts require —
  a decision entry and a seed row, never a row typed into a screen — and *"leaving it unstated is the one
  option that gets worse quietly"* was the correct call, because this bullet was three rounds from being
  quoted as a design principle.

- **~~A prose expression names an operand that does not exist: `all_in_school`.~~ — retracted; that defect is
  not in this corpus, and writing it here is the real finding.** The paragraph this bullet replaced cited
  [domain/07-events.md §1](domain/07-events.md) as opening its age-gating story with an audience named
  `all_in_school`, and argued from there that the prose was advertising a registry row nobody had minted.
  **The token appears nowhere in this repository** — not on the line cited, not in that file, not in any file:
  a grep for `SCHOOL` and `in_school` across `docs/` returns this bullet and nothing else. It arrived from a
  subagent's report of a defect it said it had found and deliberately not touched, it was plausible — the
  registry genuinely has no `SCHOOL`, and the sentence it described is the kind of sentence that page does
  write — and it entered the register **without the one grep that would have killed it**, which is the same
  operation this entry's entire finding consists of. [D-104](decisions/round-10b.md#d-104--a-permission-codes-last-segment-is-an-action-and-a-registry-that-prose-contradicts-is-a-fiction)
  named the class: prose contradicting a registry is a fiction. **This is the fourth page of that class and the
  only one that was *about* the registry**, filed in the file whose job is to hold verified open questions —
  which is what makes it the expensive kind. **A wrong entry in a domain page describes something wrong; a wrong
  entry here directs work**, and nothing checks this file: no CI, no schema, no resolver, and no reader who
  would notice, because every sentence in it is written as a question and a question cannot be falsified by
  reading it. **The control this suggests is not "trust reports less", it is the same control as everywhere
  else in this module: grep before you write**, including — especially — when the sentence being written is an
  accusation against somebody else's page.
- **`SCHOOL` — asked directly, and refused: it is not an important selector, at least not for now.** The
  question above was worth answering even though its premise was invented, because the underlying question is
  real: could a `SCHOOL(x)` operand be added, and should it? It could be, and it is not, and
  [D-108](decisions/round-11-12.md#d-108--there-is-no-school-operand-a-selector-may-only-name-a-fact-the-model-stores)
  is where that is decided — with the reason, the shape to use instead (**a `person_group` per school, which is
  expressible today**), and the one thing that would reopen it. **"For now" is honoured by naming the trigger
  rather than a date.**

**What rounds 11, 12 and 13 changed here, and what this entry still does not own.** **No bullet is open** —
round 12 closed the age one with `OLDER`/`YOUNGER`, and round 13 closed the `GUARDIANS` one by **deleting the
selector rather than hosting it** ([D-113](decisions/round-13.md#d-113--the-guardianship-channel-has-no-expression-guardians-is-not-a-selector)),
which is the fourth way this file has closed a question about a missing operand: build it, refuse it, discover it
was already expressible, or **discover it was never about the language**. `PERSON(x)` did not close either of them, and deleting `LIST`
did not open a third, because **the language can state exactly the same facts about people as it could with
thirteen operands** — a claim that was true of round 11 and is *narrower* than round 12, which is the
difference between deleting an operand that added nothing and adding one that adds a kind of fact. The one thing
that went with `LIST` is the *dates on individual names*, and that is not a missing operand: no row could
restore it, and [D-105](decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)
ruled that a windowed exception is a second grant with its own period instead. Two adjacent questions are
**deliberately not this entry's**, and are named so they are not folded in: `WHITELISTED` is a refused
candidate, not a missing fact, and it is
[F-20](#f-20--closed--whitelisted-stays-unseeded-because-there-is-no-state-to-evaluate-and-the-feature-arrives-anyway)'s
to answer — **and it has now answered, refused, with the need served by a `person_group` per whitelist** — with
[EV-6](#ev-6--whitelisted--the-word-people-reach-for-with-no-stored-state-to-name) carrying its events half;
counting it here would be counting a refusal as a gap. And the legibility of a hand-typed set of forty names
is [F-22](#f-22--closed--the-editor-may-fold-and-flatten-for-display-the-stored-canonical-string-never-changes),
**also now closed**: D-105 pointed it at this entry's neighbourhood, but it was never a question about a missing
fact — the language states it fine, and reading it back is the problem, which is an editor question.

**Impact.** The `GUARDIANS` bullet is the cheap one — either one row in `grant_scope_type`, or one corrected
registry row and one corrected sentence in §8 and §12. The age bullet is the expensive one in kind rather than
in size: it is a new *kind* of fact in a language whose rules for new facts are now written down — **an
operand is a decision entry plus a seed row, never a row typed into a screen** (D-101), which is what keeps
this 🟢, since the cost is not code, it is the argument. **The one bullet this round settled cost exactly what
this paragraph predicted a missing operand would cost** — one seed row, one reserved word, one namespace
reservation — which is the only way in which it was a cheap question: it was cheap to *fix* and took a whole
round to notice. **Round 12 paid the age bill and it came to precisely this invoice, plus one deleted
sentence**: two seed rows, two reserved words, [D-107](decisions/round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded),
and the correction of a claim this corpus repeated for four rounds because it sounded like a type system.
The bill was never the expensive part; **not noticing which claim you were leaning on was.** **Round 13 then
presented the only invoice in this entry with a negative line: closing the last bullet cost one *deleted*
registry row and no seed row at all** — no reserved word gained, no namespace reservation, no decision about
whether a person is an item, and the orphan check left untouched, because `person` never joined
`grant_scope_type` after all. What it did cost is everywhere the word was: **31 occurrences outside the decision
log, across eight pages, counted with grep rather than remembered** — and the cheap-looking half of that bill is
the part this entry's whole existence argues for, because a notation that parses reads as a decision somebody
made, and thirteen pages of prose had silently made one.

---

### F-6 ✅ **Closed** — the permission cache is rebuilt nightly, on any ruleset write, and on request

*Retitled twice. Round 10 moved the weight of this question: it used to be "how long may an answer be
reused", with the invalidation list settled underneath it, and the list became the hard half while the TTL
became a number nobody could pick until the list was. Round 13 refused both halves, and the reason the entry
could be closed at all is that **the thing underneath both was removed rather than answered.**

**Amended by [D-114](decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation)
in round 14, and the amendment is a deletion rather than a correction: there is no permission cache, so this
entry's subject no longer exists.** **The heading is kept exactly as it stands, and on purpose — this is**
[D-081](decisions/round-06.md#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now)**'s
shape applied to a title: the name outlived the mechanism, and the entry's job now is to say what closed it rather
than to look current.** So read this heading as **the name of the round-13 closure**, not as a description of the
current design; anyone who takes the title for the design has been warned by the first line beneath it. It is also
infrastructure — three files link to this slug, ten links — and a question that died by having its premise removed
earns a stale heading far more cheaply than this corpus earns a broken link. What round 13 left standing, item by
item. **The key dies**: `(person_id, permission_code,
scope_type, scope_id, at_bucket)` left with the table that held it, so part (a) and part (b) are not answered but
**unaddressable** — there is no entry to put a lifetime on and no entry to invalidate. **The version integer
survives, narrowed**: it now keys a *compiled expression* rather than an answer, and its bump set is
**`audience_operand` and `selector_type`** — two tables where D-111 named **eight kinds of write: six tables, the
D-109 flag and a merge**. **And one finding out
lives its own key**, which is the part this entry must keep visible: [D-102](decisions/round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)
made a grant's reached set a function of **the item**, and that is a property of an expression, not of storage.
**A form computed while checking one item may never be served for another** — but note where the binding now
sits, because D-114 is precise about it and this entry should not be sloppier than the decision it amends: a
compilation holds *"no person and no item"*, both arriving as parameters, so the item binds at **resolution**,
not at compilation. Anything that caches a *resolution* — a named roster, an expansion keyed per
`(audience, item)` — is keyed by the item or it is wrong on the 401st event. **Why the object was deleted rather
than repaired** belongs here too, since this entry is where the reasoning lives: the boundary round 13 made
load-bearing, *"the line between those two lists is the entire safety property"*, omitted `membership` — while
`membership.terminate` ⛔ is the most safeguarding-shaped write in the catalog — and the list could not be fixed
by adding a row, because a correct invalidation set is **the read path** and not a policy boundary anybody can
keep true by hand. **Everything below is kept as printed, including the invalidation table and the two lists,
which now describe a mechanism that does not exist.** They are still the best four rounds of reasoning in this
file about *which answers move*, a question that has outlived every answer it was ever given.

~~**Question, in two parts.** (a) What TTL is acceptable on a resolved `(person, permission, item)` answer?
(b) **What events invalidate a cached answer, and how wide is each one's fan-out?**~~

**Answered by [D-111](decisions/round-13.md#d-111--the-permission-cache-is-rebuilt-nightly-on-any-ruleset-change-and-on-request):
one policy, three triggers.** Every cached authorization answer is rebuilt **(a) nightly, in full; (b)
immediately on any write to the ruleset; (c) on explicit request** — an administrative action, which sits on
the same permissions page as [the tab F-21 now has](#f-21--closed--no-report-a-tab-on-the-permissions-page-and-unbounded-cost-is-accepted-at-the-stated-size).
**No TTL per entry, no asymmetric TTL, and no partial invalidation list to get right.** The user's answer,
verbatim: *"All cache is represhed at night every day OR on manual request and ruleset change."*

**All three of those triggers are retired by [D-114](decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation):
(a) and (c) went with the cache they served, (b) went with the boundary it was defending.** What follows in this
entry is therefore **what round 13 decided and why**, not what the system does — kept because the reasoning is
the entry's real content and because the invalidation table below is still the clearest statement anywhere in
these documents of *which answers move*.

**What that refused, said plainly, because this entry spent four rounds building the thing that was refused.**
Part (a) is refused outright: there is no per-entry lifetime to configure, so there is no number to argue
about and no asymmetry between an allow and a deny. Part (b) is refused **by removing its premise** — the
fan-out question was only hard because per-entry invalidation was assumed. What replaces the whole table
below is **a rebuild plus one rule about what counts as a ruleset change**, and that is a smaller thing to be
right about: one boundary to state, versus a row per write type whose width had to be computed correctly
every time, including by the next person who adds a table and does not know this one exists.

**The whole design now hangs on one boundary, so it is quoted rather than summarised.** The ruleset is: a
write to `access_grant`, `audience_operand`, `guardianship_permission` or `permission`; to `role_holder` and
`person_group_member`; **to the `deprecated | hidden | disabled` flag of anything in
[D-109](decisions/round-13.md#d-109--nothing-a-rule-names-is-deleted-deprecated-hidden-disabled--and-a-tab-instead-of-a-report)'s
table**; and a person merge or unmerge. **That flag must itself be a ruleset write, and D-111 says so in
these terms: if it is not, "turn off this naming" waits until midnight, which is exactly the failure the flag
exists to prevent.** A control whose effect arrives the next morning is not the control anybody agreed to.
**Read that list as the defect, not the design.** It is quoted here in full because round 13 called this
boundary the whole safety property — and it omits `membership`, while `membership.terminate` ⛔ is held by
`safeguarding_officer` and is the most safeguarding-shaped write the catalog carries. Under
[D-114](decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation)
the flag is not a version bump at all: it is **read live** at check time, which is why *"disabling takes effect
now"* no longer depends on anybody remembering to put a table on a list.

**What "immediately" means, because the hardest writes are the ones that name nobody — the mechanism D-111
added the same round, since the ruling was incomplete without it.** ~~The cache key is
`(person_id, permission_code, scope_type, scope_id, at_bucket)`, and **an audience appears in it nowhere.**~~
Ending one `role_holder` row names its person; ending one `person_group_member` row names its person; **an edit
to a shared `audience_operand` tree names nobody at all** — ~~the people it stops reaching are whatever the
expression happens to resolve to, and finding them means evaluating the expression for everyone, **which is the
rebuild itself and not a way around it.**~~ That is the exact reason this entry's fan-out table looked intractable
for four rounds: per-entry invalidation has no answer for a write whose subject set is a computation.
**D-114 dissolves the hard half from the other side, and it is worth naming how:** a *compilation* is keyed by an
expression's root, not by the people it reaches, so the unanswerable question *"whom did this edit stop
reaching?"* is simply never asked — and because a compilation is finite and enumerable over the audience tree,
*"an edit to a shared audience invalidates everything"* becomes **"it invalidates the compilations that embed
it"**, which is a bounded walk: the same reachability walk the save path already performs for cycles
([D-103](decisions/round-10b.md#d-103--an-audience-may-name-another-audience)). **The fan-out that made this
entry hard was only hard because it fanned out to people.**
**The answer is one integer — a ruleset version, bumped by any write in the set above, ~~carried in every cache
entry, and an entry is valid only while its version matches~~.** *"Rebuild immediately on a ruleset change"* then
means **bump the version**: one write to one row, which never needs to know whom a rule reaches. ~~The nightly full
rebuild stays as the correctness backstop for what the version cannot cover — the calendar cases — and the manual
request becomes *bump it and warm it*.~~ **What D-114 kept of this mechanism is the integer and nothing else:** it
is now carried by a *compilation* rather than an answer, and its bump set is **`audience_operand` and
`selector_type`** — the two things a compilation actually depends on, an expression's shape and the seeded
vocabulary it is written in. `access_grant` dropped out because **grants are not compiled at all**: the expression
lives on the `audience` and its operand rows are already inside the surviving set, while a check reads the person's
grant rows live — so inserting, editing or revoking a grant changes what that read returns and leaves no compilation
behind to drop. `role_holder`, `person_group_member` and a person merge dropped out for the adjacent reason: they
move **rosters**, which are the other thing still cached across requests — keyed by the name the write touches,
holding dated rows, invalidated locally rather than folded into a version. **Concretely: adding a child to a group, which used to
drop the entire cache, now drops nothing.** **What it does not buy: it is not a version per audience and not a version
per grant,** and a system large enough to want either is the system
[D-112](decisions/round-13.md#d-112--the-systems-scale-is-stated-hundreds-of-people-tens-of-registrants-per-event)
says this one is not — which is the trigger that reopens this entry alongside the size numbers. **The check worth
writing, in D-111's words, survives its mechanism:** ~~if the `deprecated | hidden | disabled` flag ever stops
bumping the version~~, the failure to watch for is now **a flag that has been compiled into a cached form** —
D-109's *"deprecating or hiding must not change the answer"* would still hold while *"disabling takes effect now"*
silently stopped being true, and under D-114 that can only happen if somebody stops reading the flag live.

**Why the key changed shape.** The answer used to be a function of a person and a permission, with a scope
that was either the organization or a unit somewhere in a tree. [D-102](decisions/round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)
made the reached set depend on **the item itself** — a bound operand like `PLACED` or `ORGANIZERS` means the
same grant says something different about every event it is written on — so ~~**the item must be in the key**,
not merely the scope type~~. Two consequences worth stating before anyone builds this: ~~an item-scope grant can
no longer be answered by one cached row per person, and a per-item preview is a per-item cache entry~~
([F-15](#f-15--closed--the-per-item-preview-is-cheap-at-the-stated-size-and-this-is-what-reopens-it)).
**Both were statements about a table that no longer exists, and neither was a statement about the wrong thing.**
The dependency D-102 discovered is in the expression, not in the storage: a bound operand is evaluated against
the item under check, so **nothing computed while checking one item may be served for another.** Under
[D-114](decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation)
the item is a *parameter* of a compilation rather than a component of a key — which is stronger than what this
paragraph asked for, not weaker: a compilation is reusable across items exactly because nothing in it has been
resolved to one yet.

**Why the invalidation list grew a transitive edge.** [D-103](decisions/round-10b.md#d-103--an-audience-may-name-another-audience)
lets an audience name another, so ~~a cached answer now depends on~~ **a compiled expression depends on**
**every audience its expression references, transitively** — not only the ones a grant names directly. Editing
`volunteers` must invalidate anything whose closure reaches `volunteers`, three levels up if something is three
levels up. The walk that computes that closure is the same reachability walk the save path already performs to
refuse cycles, which is the convenient reading; **whether it is cheap enough to run on every edit is exactly what
[F-16](#f-16--closed--listing-the-grants-that-name-an-audience-is-a-scan-over-a-small-table-at-the-stated-size) asks, and nothing has
measured it.** ~~An invalidation that is too slow to run is not a slow feature, it is a stale allow.~~ **The
sentence's failure mode went with the answer cache** ([D-114](decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation)):
a compilation drop that is slow to run delays an edit, it does not widen anyone's access, because a stale
compilation can only be wrong about the *words* it holds and never about who is in a set. **But the transitive
edge itself is not history** — it is now the reachability walk that finds the compilations to drop, so F-16's
question returns, in a bounded form rather than a fan-out-to-people form.

**The invalidation table, kept visible and replaced.** ~~What invalidates what, as of round 11.~~ **Every row
below is superseded — first by D-111's rebuild, then by [D-114](decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation)
deleting the thing the rebuild rebuilt** — none of it is what an implementation does now. It stays because it
is four rounds of reasoning about *which answers move*, and that question survives even though its answer no
longer does: ~~read the column "Invalidates" as **"what the nightly rebuild would have to notice anyway"**,
which is exactly what a full rebuild does notice, for free, without a single one of these rules being
implemented correctly by hand~~ — **read it now as the read path**, which is the only honest reading left: every
row is a table some operand can reach, and D-114's finding is that a correct invalidation list is exactly that
set, which is why it could not be maintained as a policy boundary. **Two rows are worth reading against what
replaced them rather than struck through, and one of them is the reason there was anything to replace:**
**`membership` open and close has a row in this table**, dated round 11,
and **it is missing from the single boundary D-111 substituted for the whole table two rounds later.** That is
the hole, recorded in this file the entire time it was open: the narrowing that made the list smaller is what
made it wrong.

| Write | Invalidates *(what D-111 rebuilt instead, and what D-114 made moot — no row here is a rule any more)* |
|---|---|
| `access_grant` insert, update, revoke | that grantee × that permission × that scope (and the unit, for the dead-weight-deny report's sake) |
| `audience_operand` — the tree, not just the rows | every answer whose expression reaches this audience, **transitively** (D-103). **Since D-105 this is also the row that covers "somebody added a name"**: adding a person edits the expression, so the widest cache-busting write in the module got one step more common and one step less visible, and two clerks editing one audience at once can now lose one of the two additions unless the editor carries a concurrency check |
| ~~`audience_member` (the `LIST` leaf)~~ | **retired** — the table is deleted ([D-105](decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)), and the write that replaced it is the row above |
| `role_holder` | everyone holding that office × each permission granted to `ROLE(x)` |
| `person_group_member` | everyone in that group × each permission granted to `GROUP(x)` — and anything naming an audience that references the group |
| `membership` open/close, and the 1 January sweep | by **person**, not by scope, and only where an expression contains `MEMBERS` — the sweep is no longer the universal invalidator it was while the gate existed |
| `event_registration` insert, waitlist move, `is_confirmed` | every cached answer **on that event** for the four attendance tiers, which are computed rather than stored |
| `person` merge or unmerge | both directions, by person id, since sets are keyed on person — **and since D-105 invalidating is not enough**: every `audience_operand` leaf whose `selector_arg_id` names the absorbed person has to be *repointed*, because a leaf that resolves to nobody is the empty set, which is silent on the allow side and **widens a deny on the `-` side** ([F-10](#f-10--which-invariants-the-orm-cannot-express-and-who-writes-those)) |
| **no write at all** — somebody turns sixteen | every cached answer **about that person** whose expression contains `OLDER(16)` or `YOUNGER(16)`, at midnight, entirely predictable and announced by nothing. This is the list's **first entry with no causing write**, and [D-107](decisions/round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded) accepts it **by ruling, not by oversight**: *"I know, that the time will change, how the rules resolve and IT IS FINE."* The row is here so that nobody implements it as a bug — the cache is already keyed to a date, a check for a past date has to answer for that past date, and there is no row to expire because nothing was ever stored. **No new mechanism, and one more reason the TTL below is the actual question** |
| ~~a unit's parent changing~~, ~~a `scope_exposure` write~~ | **retired** — the hierarchy and `scope_exposure` are deleted (D-097), and with them the two widest fan-outs the list used to have |

**The residual window, and why it is not the thing this entry was afraid of.** ~~D-111 allows exactly one kind
of answer to be up to a night stale: **an answer that moved without a write** — a birthday crossing
`OLDER(n)`/`YOUNGER(n)`, the 1 January membership sweep, a role or group period ending on its own date,
attendance writes behind the event tiers.~~ **There is no window, and the sentence above is the one D-114
deleted rather than defended.** A birthday, a sweep, a period reaching its own `valid_to` and a registration
write all move the answer **at the instant they happen**, because the answer is computed when it is asked for.
The fear this entry carried for four rounds was the opposite case:
*a stale allow is a permission the organization has already withdrawn*, with the safeguarding story behind the
withdrawal. **That case is impossible, and not for the reason this entry gave** — ~~because every withdrawal a
person performs is a write — revoke, add a deny, close a grant's period, end a guardianship, end a role
assignment, set the `disabled` flag. Each one is a ruleset write, so each one rebuilds immediately.~~ That
argument was load-bearing and it had a hole in it: the boundary it leaned on did not list `membership`, so
`membership.terminate` ⛔ rebuilt nothing. **What actually delivers the asymmetry now is that nothing is stored**
— a withdrawal cannot be stale because there is no copy of the answer left to go stale. **The safeguarding case
and the calendar case are now immediate for the same reason.** The asymmetric TTL this entry kept proposing as
"the obvious answer nobody wrote down" is not needed at all: the asymmetry it wanted to buy no longer has a
mechanism to be bought for, which beats both a clock and a boundary.

**This is [D-107](decisions/round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)'s
ruling ~~with its mechanism attached~~ with its mechanism removed.** *"I know, that the time will change, how the
rules resolve and IT IS
FINE"* described a behaviour when it was written and described a **policy** under D-111: the acceptance had a number
in it (one refresh) and the refresh had a cause (the nightly rebuild). ~~That is the difference between a
known-and-accepted gap and a gap nobody has decided to accept, which is the distinction this file keeps
insisting on.~~ **D-114 keeps the ruling and retires the need for it:** under live resolution the calendar moves
the answer when it moves, so what D-107 waived has stopped being a gap in the first place. **A ruling that turns
out to be unnecessary is a better outcome than a ruling that had to be defended** — and this file's discipline of
writing the acceptance down anyway is what let it be recognised as discharged rather than quietly forgotten.

**What it cost.** The transitive-audience invalidation problem this entry called the hard half **dissolved
rather than solved** — ~~a full rebuild reaches the closure by definition, so "can it be invalidated
incrementally at all?" has no answer required.~~ The price is honest and D-112 pays it: ~~a nightly full rebuild
is affordable **specifically at the stated size** (a few hundred people × 66 codes × a small number of items),
and D-111 says in the same breath that this would be a different decision at ten thousand people. The second
price is that an answer can be a night stale on the calendar cases, and the corpus has now said that out loud
rather than inheriting it from `OLDER(n)~~` — **D-114 retires both prices, and with the second one goes the only
staleness this file ever accepted on purpose.** The remaining cost is on the other side of the ledger: the key's
space at that size was a few hundred people × 66 codes, order tens of thousands of entries, so the rebuild was
cheap too — but `role_holder` and `person_group_member` were two of the eight kinds of write D-111 named — six
tables, the D-109 flag and a merge — and they are the two most ordinary writes in this organization, so every
Thursday group edit dropped the whole cache and the effective hit rate was
*time since the last group edit*. **A cache whose invalidation is free and total is one step from no cache.**

**What reopens it.** The same trigger as [F-15](#f-15--closed--the-per-item-preview-is-cheap-at-the-stated-size-and-this-is-what-reopens-it):
the population reaching **a few thousand people, or a thousand registrants on one event**
([D-112](decisions/round-13.md#d-112--the-systems-scale-is-stated-hundreds-of-people-tens-of-registrants-per-event)).
~~There the rebuild is the **last** of that round's list to hurt and the last to need redesigning~~ — which is why
this entry closes at the size rather than in principle. **What returns at that trigger is now named instead of
vague** ([D-114](decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation)):
materialize `effective_permission` per person, **call it that**, and carry three things this entry's cache lacked
— a per-person invalidation handle beside the global one, a stated list of the tables it watches, and that list
derived from the operand registry rather than from a list of ideas.

**Impact.** ~~No schema. What changes is a job that has to exist, a definition of the ruleset the write path has
to obey~~ — **round 14 inverts this line: the schema change is a deletion, `permission_cache` goes**
([D-114](decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation)),
the job disappears, and the definition the write path had to obey goes with it. What is left to build is a
request-scoped memo and two batch entry points, neither of which is a table. The D-103
incremental-invalidation question stays closed, now for the second time: first because a rebuild reached the
closure anyway, now because the only thing invalidated through the closure is a compilation and that walk is
bounded and already exists. The per-person effect of the sweep is no longer an invalidation question at all
([data-model/05 §10](data-model/05c-access-log-and-resolver.md#10-the-resolver)) — it is a fact about what `MEMBERS`
evaluates to on the checked date, which is a description of *what moves*, and nothing more.

---

### F-7 ✅ **Dissolved** — a nightly rebuild of cached answers and a materialized effective-permission table are one job

**Dissolved by [D-111](decisions/round-13.md#d-111--the-permission-cache-is-rebuilt-nightly-on-any-ruleset-change-and-on-request),
which is a different event from being answered, and is written as such on purpose.** This entry asked the
system to pick **one of two designs**. What happened is that the design got chosen for another reason
altogether — a rebuild cadence, decided in F-6 — and *a nightly full rebuild of cached answers and a nightly
materialized `effective_permission` table turned out to be the same job with two names.* There is now one job.
Nothing weighed A against B, no trade-off was adjudicated, and **a dissolved question is the kind that comes
back if nobody writes down that it dissolved**, so this heading is the writing-down — and like
[F-6](#f-6--closed--the-permission-cache-is-rebuilt-nightly-on-any-ruleset-write-and-on-request)'s,
**the heading is kept as the name of what round 13 did, not as a description of what exists**
([D-081](decisions/round-06.md#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now)):
five files link this slug, thirteen links, and the two designs it names are now one deleted and one unbuilt.
[domain/06 §8](domain/06-authorization-model.md)
carries the longer argument; this entry is the pointer, not a second copy of it.

**Re-amended by [D-114](decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation),
because one of the two things this entry dissolved between has just been deleted.** Read the paragraph above as
history or it becomes a false statement: there is no longer "one job", because the nightly rebuild of cached
answers is gone and a materialized `effective_permission` table was never built. **So the dissolution has to be
restated in the terms that survive it, and these are the honest ones.** The two designs did converge in 2026 —
a nightly full rebuild *is* a materialization with a worse name, and D-111 saw that — but they converged **into
an object that round 14 removed**. What F-7 actually established is the part that does not depend on which of
them was built: **there was never a third thing to choose**, no design in which you cache answers per person in
one place and materialize them per person in another. That finding stands, and it stands *more* cleanly now that
only one of the two arms is even on the table. **What is therefore not settled, and never was:** whether this
system should ever hold `effective_permission` rows at all. At D-112's trigger that table returns **on its own
merits** — not as the surviving half of a dissolved choice, but as a decision entered under its own name, with a
per-person invalidation handle and a stated staleness window, which is what D-114 says the deleted cache should
have carried if it was going to exist at all
([D-112](decisions/round-13.md#d-112--the-systems-scale-is-stated-hundreds-of-people-tens-of-registrants-per-event)).

~~**Recommendation.** Start with cache-only. Materializing is a denormalization requiring transactional
maintenance, and a silent refresh failure is an access bug nothing detects.~~ ~~**That recommendation was right
and is now unaddressable**, because there is no longer a choice to make: the rebuild exists, and whether its
output is called a cache or a table is a naming decision about one job.~~ **It is unaddressable still, and for a
starker reason than the one above gave:** neither arm exists now. Note what the reasoning was *for* —
**the fear of a refresh that fails silently and changes who has access**. ~~is a real property of the surviving
design, and it survives as a duty on the nightly job rather than as a reason to prefer the other arm~~ — **that
fear was the best argument in this entry, and D-114 answers it the way it answers everything else: there is no
refresh to fail.** ~~a duty on the nightly job~~ is gone, and with it the failure mode F-7 was weighing when it
said *cache-only*. If `effective_permission` is ever materialized at D-112's trigger, **this is the paragraph
that obligation comes back to**, and it comes back as a monitoring duty on a real table rather than as a tiebreak
between two designs nobody is choosing between.

~~**Impact.** Performance only; revisit if measurement demands it. The membership gate makes materializing
harder, not easier — every membership transition would have to rewrite rows.~~ **The membership gate half of
that sentence was already dead** when it was written — the gate is deleted by
[D-100](decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)
— and it is kept here struck because it is the clearest illustration in this file of an entry reasoning from
a mechanism nobody had noticed removing.

**The one constraint that is *not* dissolved, because it points the other way — and it is now the whole
surviving content of this entry.** ~~The rebuild may evaluate expressions per person — that is what warming a
cache is, and at~~ at
[D-112](decisions/round-13.md#d-112--the-systems-scale-is-stated-hundreds-of-people-tens-of-registrants-per-event)'s
size ~~it is cheap~~ a per-person evaluation would have been cheap; there is no longer a job that does it. What
stays forbidden is the way to get this wrong that
[domain/06 §8](domain/06-authorization-model.md) names: **inside a check, an
expression is compiled to a predicate on the person being asked and never materialized as a set.** Otherwise
~~the nightly job is correct and~~ every request still costs three thousand rows. A reader who takes from this
entry that "materializing was accepted" has taken the wrong thing **in both rounds it has been written**: the
*job* was adopted and then deleted, and the *read path* was never adopted at all. ~~the *job* was adopted, the
*read path* was not~~ **What is left standing is a prohibition with no permission next to it** — which is the
correct shape for a system that stores no answers, and the reason invariant 19's structural half is that the
schema now has nowhere to put a per-person answer even if somebody wants one.

**What reopens it.** ~~Nothing reopens the choice, because there is nothing left to choose between.~~ **Round 14
reopened the choice by deleting one side of it, which is the one way this heading could become false** — so the
honest line is that the entry stays dissolved **as a choice** and stays closed **as a plan**. What can move it is
the D-112 trigger — **a few thousand people, or a thousand registrants on one event** —
at which point ~~the question is no longer cache-versus-table but whether a full rebuild is the right shape at
all,~~ **the question is exactly one question: does this system materialize `effective_permission` per person,
under that name, with a per-person invalidation handle and a stated staleness window.** It is a genuine question
and, per [D-114](decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation),
**it must arrive as a decision entry of its own** — not as this one quietly reopened, and not as a cache
reintroduced in a migration.

---

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
   [F-16](#f-16--closed--listing-the-grants-that-name-an-audience-is-a-scan-over-a-small-table-at-the-stated-size). `permission.code`
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

### F-12 ✅ **Closed** — may a role be held by a rule, as an audience is?

**Answered: no, and the split is the design**
([D-100](decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)).
The first of the three options below is the decision. A **role is an office** held by a named person for a
period and it **confers nothing**; a **group is company**, a dated set of people with no authority of its
own; and what reaches a set of people with a permission is a **grant**, which has had a grantee pair since
D-042. Round 10 did not defend that boundary so much as **make it cleaner than the question assumed**: it
renamed `role_assignment` to `role_holder`, deleted `role_permission`, deleted positions, and deleted the
membership gate — so "everyone with a current membership holds role X" is now not a missing feature of the
office table but a **sentence about who the grants reach**, written `MEMBERS * ROLE(x)` where it is wanted.

**Why the answer is no, in the decision's own terms.** `role_holder` is the **office record**: it is what a
report reads to answer "who was treasurer in 2023", and a holder list derived from live state cannot answer
that, because there is nothing to date. D-100 keeps the two tables specifically because they answer
different questions and because merging them would put 🔒🔒 `role.assign` in one table with ⚠
`person_group.member.manage` in another — **the same objection this entry raised, accepted, and then
sharpened**. The office record stays the one human-readable answer in the permission model, which is also
the resolution of [assumption 51](#i-assumption-index).

**What closed the other two options.** Both began by putting a grantee pair on the office table. With
`role_permission` gone there is nothing left *for* a rule-held office to carry, so the second arm's
materialization sweep would be recording membership in a thing that grants nothing — at which point it is a
**group**, which already exists, is already dated, and does not pretend to be an office. The third arm's
cost was never worth having: it deletes the office record's guarantee to buy a row the group table already
gives you. ~~**[F-7](#f-7--dissolved--a-nightly-rebuild-of-cached-answers-and-a-materialized-effective-permission-table-are-one-job) stays open**~~
**and stays the right place for the materializing question; it is no longer coupled to this one.** *(This sentence
was written before round 13 and got one clause wrong from the day it was published: F-7 is* **dissolved***, not
open. Round 14 makes the pointer worth keeping and corrects the clause —*
[F-7](#f-7--dissolved--a-nightly-rebuild-of-cached-answers-and-a-materialized-effective-permission-table-are-one-job)
*is where the materializing question lives, amended rather than reopened by*
[D-114](decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation)*,
and the table it speaks of would now arrive on its own merits at* [D-112](decisions/round-13.md#d-112--the-systems-scale-is-stated-hundreds-of-people-tens-of-registrants-per-event)*'s
trigger.)*

**What the question was, kept because the reasoning recurs.** Raised by
[D-091](decisions/round-09.md#d-091--a-permission-group-is-a-rule-and-a-list-at-once-and-a-rule-may-name-another-group),
which refused to decide it: the answer that produced D-091 described *permission groups* — a set of people
with filling rules, **carrying permissions** — and that was expressible here for anything an `access_grant`
could target, but not for a role, which named one person, one role, one scope, one period with no grantee
pair like the one D-042 put on `access_grant`. ~~"everyone with a current membership holds role X" cannot
be written~~ was true of the old table and is false of the language: what cannot be written, still, is a
**rule-held office** — which is the thing that was asked for and refused.

**Left open by the answer, deliberately.** Whether an office should record **elected versus appointed**,
and what an election writes, was a property of the deleted `position` tables and is
[F-18](#f-18--does-a-role-record-elected-versus-appointed-and-what-does-an-election-write). Whether a grant
naming `ROLE(x)` should carry a `MEMBERS` term is [F-13](#f-13--closed--a-rule-that-resolves-correctly-but-looks-odd-is-listed-as-unusual-never-as-broken).

---

### F-13 ✅ **Closed** — a rule that resolves correctly but looks odd is listed as unusual, never as broken

**Answered: a listing, not a lint — and no decision entry was needed, because the surface it needed was
already being built for another reason.** [D-109](decisions/round-13.md#d-109--nothing-a-rule-names-is-deleted-deprecated-hidden-disabled--and-a-tab-instead-of-a-report)
built **a tab on the permissions page**, and it refused every save-time refusal. A grant naming `ROLE(x)` with
no `MEMBERS` term resolves perfectly and looks odd, which is this entry's entire population. So the second and
third positions below ("warning at save", "require an explicit choice") are refused by the same move that
refused every refusal in this module: **the save always succeeds.**

**The tab has two sections, and the split is this entry's contribution — recorded here because it arrived as a
collision, not as a design.** D-109 defines **Broken**: a live rule whose expression names a deprecated,
hidden or disabled thing, or fails to resolve at all. A grant that omits `MEMBERS` is **none of those** — it
resolves, its set is exactly what the writer asked for, and calling it broken would be the same category error
[F-21](#f-21--closed--no-report-a-tab-on-the-permissions-page-and-unbounded-cost-is-accepted-at-the-stated-size)
refuses, where an expression that is merely *surprising* gets reported as though it were *wrong*. So the tab
is split: **"Broken" holds only what D-109 defines, and "Unusual" holds rules that resolve correctly and look
odd** — this entry's population, and nothing else. The two sections are kept apart because they carry
different claims about the writer: *Broken* says something has happened to your rule behind your back;
*Unusual* says your rule means what you wrote and somebody else finds it hard to read. Collapsing them would
make the safeguarding signal depend on how tidy the reader's taste runs, which is a fast route to ignoring
the half that matters. **Each section belongs to the entry that defines it: Broken is D-109's and is carried
by F-21; Unusual is this entry's, and its answer therefore stays here rather than moving into F-21.**

**The premise that closed it, which is D-107's and not this entry's.** The whole reason this was a question
rather than a one-line rule was that the test **fires on the intended case as often as on the mistake** —
`ROLE(counselors)` without `MEMBERS` is how an appointed counselor keeps serving through a lapsed year, and
that is the point of D-100, not an accident of it. A warning that cries wolf dies, and a refusal that cries
wolf is worse: it teaches the writer to route around it. Against that, this corpus now has an explicit
premise to lean on, stated when D-107 opened the grammar to attribute operands and refused to add lint to
match: **the people writing these rules know what they are writing.** They are organizers naming their own
groups and their own offices, not anonymous input. Given that premise, a save-time prompt is not protection,
it is a doubt expressed on somebody's Tuesday, and the listing — where a writer who is *already in the
permissions page* can see what they wrote next to what everything else they wrote does — is the honest amount
of doubt to encode.

**What it cost: one section of a page, and the finding is in how small that is.** No column, no refusal, no
new page — the tab already exists for D-109's purposes and it gained a heading. **The cost is carried by the
weaker answer instead**: the failure this entry described (a person with an office and no powers, discovered
by the person least able to diagnose it) is still not prevented by anything. It is *listed, in a section that
says the rule works*. That is D-081's shape again — **a convention, not a guard** — and this entry now joins
[F-21](#f-21--closed--no-report-a-tab-on-the-permissions-page-and-unbounded-cost-is-accepted-at-the-stated-size)
and [F-19](#f-19--closed--a-permission-code-is-a-row-prose-names-codes-and-nothing-checks-the-two) as the
third instance of the module choosing to show rather than to stop, with the same weakness and, since D-109,
the same single place to look. **The one thing the split buys is honest labelling**: a reader who has decided
the tab's Broken section is full of false alarms can still tell that its Unusual section says something
different, which is the difference between a signal and noise.

**What would reopen it.** Not another odd-looking rule. The trigger is a count: **if the Unusual section's
`MEMBERS`-less office grants turn out to be mostly mistakes rather than mostly deliberate, the premise above
is falsified for this case**, and a save-time prompt on `is_system` roles only — the narrow arm of the
recommendation below — becomes worth its false positives again. That would be a decision entry, and it would
be the first refusal this module has made about the *content* of an expression rather than its arithmetic.

**Question.** [D-100](decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)
moved the membership test out of the resolver and into the expression, and reversed the posture while doing
it: **the gate used to be default-on with named carve-outs, and now every sentence about membership is
written by hand.** Three controls were accepted in place of the deleted mechanism — a standing report, the
promise that **seeded** grants carry `MEMBERS`, and an import-time counselor count. None of the three
inspects a **hand-written** grant at the moment it is saved. So: when somebody writes
`ROLE(treasurer)` where they meant `MEMBERS * ROLE(treasurer)`, should the editor **warn at save**, or is
the standing report the whole control?

**Why it is a question and not a lint rule.** The two forms are both legal and one is not always wrong —
that is the entire point of the decision, since `ROLE(counselors)` *without* `MEMBERS` is how an appointed
counselor keeps serving through a lapsed year. A warning therefore fires on the intended case as often as on
the mistake, which is the classic way a warning dies. Against that: the mistake is **invisible in the row**
(a grant with a missing operand looks exactly like a grant that was finished) and its symptom is a person
with an office and no powers, discovered by the person least able to diagnose it.

**Positions.**
- **Report only** — what D-100 says today. Cheapest, no false positives, and the failure is at least
  *aggregate-visible*: a report listing role grants whose expression contains no `MEMBERS` term is a list
  somebody can read down once a period.
- **Warning at save, not a refusal** — the editor already parses the expression to store the tree, so the
  test is one node lookup, and the save still succeeds. The cost is a prompt on the legitimate case, which
  D-100's own example shows is not rare.
- **Require an explicit choice** — the editor asks "must this holder be a current member?" and writes the
  `MEMBERS` term or a comment field. Honest, and it is designing a new column out of a question nobody
  asked yet.

~~**Recommendation.** The report, plus one **narrow** save-time warning: fire only when the expression names
`ROLE(x)` for a role whose `is_system` is true **and** contains no `MEMBERS` term~~ — **the report half is the
answer; the warning half is refused.** It is kept struck rather than deleted because it is the best-designed
version of the refused option in this file, and because `is_system` really is the only signal in the schema
distinguishing "the organization's own vocabulary" from "a role somebody invented this afternoon" — which is
why the narrow arm survives above as the thing that would reopen this entry. **A convention, not a guard**, in
D-081's wording, is now the whole answer rather than the residue of one: nothing stops a client from writing
the grant anyway, and nothing warns the writer while they write it. One section of one tab notices
afterwards, and says *unusual* rather than *wrong*.

**Schema impact.** None for the report or the warning — both read `access_grant` joined to the
`audience_operand` subtree. The third arm is a column. **No seeded row changes.**

**Needed.** Before the grant editor ships, because "we warn on nothing" and "we warn on this" are different
products and the second is cheaper to add first.

---

### F-14 ✅ **Closed** — nothing computes semantic equality of two expressions, and nothing will

**Answered: refused, on three grounds, none of them cost.**

1. **The stored canonical string is the only identity an expression has.** [D-105](decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)
   ruled that the tree is stored **exactly as the writer wrote it**, and this round's [F-22](#f-22--closed--the-editor-may-fold-and-flatten-for-display-the-stored-canonical-string-never-changes)
   closes the last route around that: **display is free, storage is not**, because the write-path checks — the
   cycle walk, the reserved-name rule, the listing of what names an audience — all reason over the stored form.
   A fingerprint is a *second* identity, and a second identity is a second answer to "is this the same
   audience?", which is precisely the question D-101 gave up in order to keep storage honest.
2. **It is not decidable anyway, and this entry already knew that.** With `AUDIENCE(code)` references, two
   expressions can fingerprint differently and reach identically because the difference is inside a referenced
   audience — so the honest design was always "a warning over the expression as written, references treated as
   opaque atoms". **A check that must advertise how much it cannot see is not a control**, and D-105's deletion
   of `selector_depth_limit` removed even the bounded resolver run that would have made the strong version
   possible on a deadline.
3. **Nobody is deduplicating audiences, at this system's size.** [D-112](decisions/round-13.md#d-112--the-systems-scale-is-stated-hundreds-of-people-tens-of-registrants-per-event)
   fixes the population at a few hundred people; the near-duplicate this entry feared "accumulates slowly" is a
   problem at a scale this corpus will not reach, and the third arm's *syntactic* fix — storing `+` children
   sorted — is now explicitly refused by ground 1. **That answers the sentence this entry flagged as unwritten**
   ("whether sorting the children of a commutative operator falls inside what D-105 refused is a sentence nobody
   has written"): **it does not fall inside; it is outside, and it is refused.** The stored form is what was
   typed, including the order.

**What this concedes, since a refusal read as a resolution is the usual damage.** Two audiences meaning one
thing are still two audiences, and the failure this entry described is untouched: an organization names the
stale copy, a grant points at it, and the fix looks like a permission change because it is one. **The
mitigation is not a fingerprint, it is the listing** — *which grants name this audience* — which D-103 already
requires and [F-16](#f-16--closed--listing-the-grants-that-name-an-audience-is-a-scan-over-a-small-table-at-the-stated-size)
now prices; plus the D-109 flag, which lets a redundant audience be **hidden** rather than reconciled with the
copy nobody uses. Two ways to live with the duplicate, and no way to detect it, which is the trade D-101 chose
and this entry confirms rather than relitigates.

**What would reopen it.** A real organisation reporting that two audiences diverged and a grant followed the
wrong one — not two audiences existing. The trigger is an incident, not untidiness, and the entry stays
findable under [assumption 59](#i-assumption-index), which already says nothing will compute equality.

**Question.** [D-101](decisions/round-10b.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree)
gave up semantic equality to keep storage honest: two audiences are equal when their trees are equal, so
`MEMBERS + ROLE(x)` and `ROLE(x) + MEMBERS` are **two different stored expressions with one meaning**, and
the canonical fully-bracketed rendering does not fix it because it canonicalizes *brackets*, not *order*.
Should the system compute a derived **fingerprint** — canonicalize operands into a sorted multiset per
operator, normalize `*`/`-` where the algebra allows — and warn when a second audience fingerprints the same
as a first?

**Why it is 🟢 and why it is still here.** Nothing depends on it. Two identical sets cost one extra row and
one extra evaluation, and the confusion is cosmetic until someone edits one copy. But D-101 explicitly
registered this as a question rather than a promise, and the failure mode it prevents is a slow one: an
organization accumulates near-duplicate audiences, a grant names the stale one, and the fix is indistinguishable
from a permission change — which is audited, alarmed, and requires explaining to somebody.

**The part that should not be oversold.** The fingerprint is **not decidable in general** once
`AUDIENCE(code)` references exist (D-103): two expressions can fingerprint differently and reach identically
because the difference is inside a referenced audience, and expanding the closure to compare them is a
resolver run, not a save-time check. **So the honest design is a warning over the expression as written, with
references treated as opaque atoms** — which catches operand reordering and misses everything nested, and must
say so in the UI rather than implying an equivalence proof.

**What round 11 did to it, and it was in both directions at once.** `PERSON(a) + PERSON(b)` is now the
*ordinary* way to write a set of people
([D-105](decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)),
so the near-duplicate this entry assumed would accumulate slowly now arrives **the first time two people type
the same twelve names in a different order**. The duplicate is no longer entropy, it is the normal output of
hand-typing — and "the confusion is cosmetic until someone edits one copy" describes the common case rather
than the rare one. The option that made the duplicate *syntactically* equal, storing `+` children sorted, is
meanwhile in tension with the same round's ruling that **the tree is stored exactly as the writer wrote it,
with no rebalancing**: sorting the children of a commutative operator is not rebalancing, but it is the same
temptation in a milder uniform, and whether it falls inside what D-105 refused is a sentence nobody has
written — which is now a thing that has to be said before it can be done. And the fallback already called the
honest one, expanding the reference closure to compare two expressions, **lost its bound** with
`selector_depth_limit`, so a warning that wanted one resolver run now wants a walk of no promised length.
**The colour stays 🟢**: nothing depends on the answer, and a duplicate still costs one extra row and one extra
evaluation. What changed is how often it is paid, not what it costs.

**Positions.** Warn on equal fingerprints (catches the common case, false-positives on deliberately
identical sets like two events' `ORGANIZERS`); compute nothing and let the *which grants name this audience*
listing (F-16) do the work of showing redundancy; or normalize at write so `+` children are always stored
sorted, which makes the common duplicate *syntactically* equal and needs no new machinery — at the cost of
storing an order the language says does not matter.

**Schema impact.** One derived column on `audience`, or nothing, and **it must never be a unique constraint**:
a warning that became a constraint would refuse two audiences that legitimately reach the same people, and
D-101's reason for giving up equality is precisely that the two are not the same question.

**Needed.** Not before implementation. Revisit when the first organization has enough audiences that someone
asks why two of them behave the same.

---

### F-15 ✅ **Closed** — the per-item preview is cheap at the stated size, and this is what reopens it

**Answered by [D-112](decisions/round-13.md#d-112--the-systems-scale-is-stated-hundreds-of-people-tens-of-registrants-per-event),
which supplied the missing number rather than a missing optimisation.** The size is written down now, in the
decision's own words: **a few hundred people in the organization, a few dozen registrants on a typical event, a
big camp on the order of two hundred.** At that size a preview that resolves an audience for one item is
"evaluating a couple of hundred predicates — nobody will feel it". **So the preview stays exactly as it was:
per-item and lazy** ([assumption 60](#i-assumption-index)), **no cap, no background job, no cache of its own.**

**Why this closes an entry that had asked for a measurement for three rounds.** The measurement was never the
missing thing; **the population was.** "At what size does that stop being an interaction and start being a job?"
is unanswerable without a size, which is why it stayed 🟡 through three rounds of increasingly precise reasoning
about a cost nobody had bounded. D-112 names the failure mode directly — *"a cost argument without a number is
not an argument, it is a mood"* — and notes the number is not a target but **this corpus's own scale**: the
legacy export is a few hundred people and their events.

**What it costs, and what is now explicitly *not* done.** The second and third positions below are both
declined, and the third deserves the note because it was the entry's own favourite: **the preview does not
decline to list above a threshold.** That arm was attractive precisely because it cost the model nothing, and it
is still true that a threshold on a *listing* is legitimate where a threshold on a *check* is refused — but
**a threshold nobody needs is not a cheap feature, it is an untestable screen state and a number nobody can
justify.** It comes back only with the trigger below. The cost that *is* paid is honest and stated: **nothing
bounds what a preview can evaluate**, and that is now **accepted at a stated size** rather than merely
unmeasured, which is a different epistemic state and the only one this entry was ever going to reach.

**What reopens it — the trigger, because a stated assumption without a trigger is a guess with more confidence.**
If the population reaches **a few thousand people, or a thousand registrants on one event**, reopen this entry
**first**: D-112's ordering is that the preview is "the first thing a user will feel and ~~the nightly rebuild the
last~~" — **and D-112's own copy of that sentence now carries the same correction: the nightly rebuild was last in
that list and is now deleted; what sits in its place is nothing, so the order is unchanged and one shorter.**
Reopening does not mean the design was wrong; it means the two rules that must survive any growth —
**a check compiles its expression to a predicate and never materializes the set**, and **a listing is
paginated** — start earning their keep here before anywhere else.

**A dependency recorded by [D-114](decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation),
which changes what this entry's cheapness is paid for.** The preview is still cheap, and nothing about the size
argument above moves. **What changed is who pays.** A nightly job used to pre-pay this work off the interaction —
not by design, just as a side effect of a cache that had to be warmed anyway — and with the answer cache deleted
**the preview now computes on open, every time, with no fallback behind it.** The batch entry point exists for
exactly this: a screen of affordances is one `can_many(person, codes[], item?)`, not a loop of single checks, so
the N+1 that made a cache look necessary is removed at the place that actually caused it. **Recorded as a
dependency and not as a risk:** the preview's stated affordability now rests on the memo and on `can_many`
existing, which is an implementation duty these documents can name but cannot enforce —
[assumption 60](#i-assumption-index) is amended to say so.

**Question.** Before D-102 the question "whom does this grant reach?" had one answer per grant. Now a bound
operand makes the reached set **a function of the item**, so an editor that wants to show *whom this reaches*
must compute it **per item**: for a camp, the audience's tree evaluated against that camp's registrations,
waitlist, confirmations and organizer roster. At what size does that stop being an interaction and start
being a job?

**Why this arrived with round 10 and not before.** The preview used to be one expansion of a rule against a
set of people. D-102 made `ATTENDED`, `PLACED`, `CONFIRMED`, `ON_WAITLIST` and `ORGANIZERS` read the item's
own tables, and D-103 made each `AUDIENCE(code)` node a **nested evaluation** rather than a row fetch — so
one preview can now touch four registrations tables and re-evaluate a tree per referenced audience, and the
number of people it expands to is the size of an event roster. [F-7](#f-7--dissolved--a-nightly-rebuild-of-cached-answers-and-a-materialized-effective-permission-table-are-one-job)
asked whether answers should be materialized for *enforcement*; this is the same cost centre for *preview*,
where staleness is a UI lie rather than an access bug — which is the softer failure and the more tempting one
to ship.

**What is assumed and not measured.** That expanding a few hundred people at a screen is fine, and that the
tree walk is cheap because it is small. Neither has been measured against a corpus of **thousands of roster
rows** (B-1) and an event with a real registration list, and the case that hurts is the nested audience three
levels deep, evaluated once per item in a list of items.

**What round 11 took away.** The second of those assumptions used to have a backstop it never mentioned: the
depth bound made *"the tree walk is cheap because it is small"* true by construction rather than by habit, and
[D-105](decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)
deleted it, so the size of a preview is now bounded by the same nothing a check is bounded by — acyclicity, and
whatever the writer typed. The hand-typed set is the new thing in the walk as well: forty names are forty
leaves, expanded per item, where they used to be one `LIST` leaf over a table with an index. And the save-time
cost moved too: the closure whose size a preview walks is **discovered by walking it**, so the first preview of
a wide audience and the save that accepted it pay for the same traversal. **What this does not change is which
answer is honest.** Of the three positions below, the third — refuse to list above a threshold, show a count —
is now the *only* local bound on offer, and unlike a cap on the enforcement path it costs the model nothing,
because a preview that declines to list changes what a screen shows and not whom a grant reaches. That
distinction is the whole reason a threshold is acceptable here and refused in
[F-21](#f-21--closed--no-report-a-tab-on-the-permissions-page-and-unbounded-cost-is-accepted-at-the-stated-size). **Still 🟡**:
this was already a measurement the editor owes before shipping, and the round made the measurement more urgent
without changing who takes it.

**Positions.** Preview lazily, per item, on demand, and never for a list of items (the honest default: a
count, not a name list, until somebody opens one). Cache the expansion per `(audience, item)` with the key
shape F-6 settles. Or refuse previews above a threshold and show "too many to list; export instead", which
is cheap, honest, and the kind of answer a spec is allowed to give before it has a number.

**Schema impact.** None for the lazy form. ~~A cache is not a table, but the **key must include the item**
(D-102) and the dependency set must include every referenced audience transitively (D-103), so F-6 and this
are one decision about keys taken twice if they are not decided together.~~ *(Round 14 makes this paragraph a
report on a decision about keys that no longer has any keys to decide —*
[D-114](decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation)
*deletes the answer cache, so the item is a parameter of a compilation rather than a component of a key. Both
findings inside it outlive that wording: whatever is served for an item was resolved for that item, and anything
reached through `AUDIENCE(x)` is reached transitively — which is now the walk that drops the compilations
embedding an edited audience, exactly as* [§ F-16](#f-16--closed--listing-the-grants-that-name-an-audience-is-a-scan-over-a-small-table-at-the-stated-size)
*has it.)* **Still none, and now for a stronger reason: there is no cache left to key.**

**Needed.** A measurement before the editor ships, because "show the set" is a promise the resolver has to
keep on a UI thread. **Assumption in the meantime:** previews are per-item and lazy, and no screen expands a
set for more than one item at a time.

---

### F-16 ✅ **Closed** — listing the grants that name an audience is a scan over a small table, at the stated size

**Answered by [D-112](decisions/round-13.md#d-112--the-systems-scale-is-stated-hundreds-of-people-tens-of-registrants-per-event):
D-103's assumption is true, now on stated grounds rather than on hope.** Listing the grants that name an
audience is *"a scan over a small table with a handful of referencing rows each"*, at **a few hundred people and
a few dozen registrants per event, a big camp on the order of two hundred**. **Pagination is a UI nicety, not a
requirement.** So both D-103 protections that hang off this query — refusing to end a referenced audience a live
grant reaches, and showing *which grants name it, and at what depth* before such an edit saves — **stand as
written**, and the fallback this entry kept polished (*weaken the D-103 rule, in the open, as a decision entry*)
is not needed.

**What it cost, and one caller that quietly disappeared.** No schema, no decision entry, and — worth recording,
because this entry's whole argument was that the walk had *gained* callers — **[F-6](#f-6--closed--the-permission-cache-is-rebuilt-nightly-on-any-ruleset-write-and-on-request)
has just removed one of them.** Round 12's worry was that cache invalidation across the reference closure might
be too expensive to run on every edit ("*an invalidation that is too slow to run is not a slow feature, it is a
stale allow*"). ~~D-111 deletes that caller: a nightly full rebuild does the walk itself, in batch, and the
incremental version is never implemented.~~ **Round 14 removes the rebuild too, and hands the caller back in a
smaller shape** ([D-114](decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation)):
the only thing now invalidated through the closure is a **compilation**, and because a compilation is finite and
enumerable over the audience tree, *"an edit to a shared audience invalidates everything"* is *"it invalidates the
compilations that embed it"* — a bounded walk, over the same closure, using the walk the save path already
performs. **So the caller count is two, not one:** the cycle check on save, which is mandatory and was always
mandatory, and compilation invalidation, which is optional in the sense that a compilation can simply be dropped
and re-made. **What changed about being fast is the consequence of being slow, and it got much smaller:** a slow
walk now delays an edit instead of leaving a stale allow standing, because nothing an expression reaches is
cached as an answer any more. **At this size both are cheap, and only one of them has to be correct.**

**The reasoning stays, because it is the part that transfers.** Everything below about the reverse-edge walk —
that the index serving *"what is in this tree"* does not serve *"what points here"*, and that the plausible
answer *"a `selector_arg_id` index"* is the kind of answer that stops being true the first time an `OR` over
`selector_kind` and `selector_arg_id` walks past it — **is still how the query has to be thought about**, and
still unwritten. D-112 makes it affordable; it does not make it correct. **These documents still contain no SQL**
(D-072), so what is settled is the *cost*, not the *plan*, and a future implementation that reads this entry as
"already solved" will write the slow version of a query that is only fast because the table is small.

**What reopens it.** The D-112 trigger — **a few thousand people, or a thousand registrants on one event** — with
this entry **second** in that list, after the preview. Note what reopening costs here and nowhere else: the
fallback is not a slower screen but **a weaker D-103 rule**, which is a decision entry, because the property
being traded is the one that keeps a retired set from widening access.

**Question.** [D-103](decisions/round-10b.md#d-103--an-audience-may-name-another-audience) makes two
safety rules depend on one query: **an audience may not be ended or deleted while a live grant — or a live
audience reachable from one — names it**, and **saving an edit to a referenced audience must show which
grants name it, and at what depth**. The decision entry states its premise as an *assumption*: that finding
the referrers is cheap. **Nothing has measured it, and the whole of D-103's protection is built on it.**

**Why the answer is not obviously yes.** `audience_operand` denormalizes `audience_id` so that "what nodes
are in this audience's tree" is indexed — that is the cheap direction. The protection needs the **opposite**
direction: *which other audiences contain a leaf pointing here*, then transitively upward, then the grants
aimed at each of those. That is a reverse-edge walk over a tree table, and the index that makes the forward
walk fast does not serve it. A `selector_arg_id` index probably answers it — one lookup per level — which is
exactly the kind of answer that looks certain until the first `OR` over `selector_kind` and `selector_arg_id`
stops using it.

**Why it matters more than a UI query.** Because **under `-` an empty operand makes the result wider, not
narrower**: an audience that stops resolving does not quietly stop granting, it can start granting. That is
why the listing is not a nicety on top of the deletion rule but the *only* way an editor can tell a person
what they are about to widen. **A protection you cannot see is a protection you will route around** — and
the route is right there, because naming an audience is optional, so an editor that blocks the safe action
teaches people to inline the subexpression instead, which removes the reference the safety rule needed.

**Positions.** Add the reverse index and state it as an invariant to verify (cheap, and it is a row in §11 of
[data-model/05](data-model/05d-invariants-and-seed.md#11-invariants-to-verify) rather than a design change); ~~cap the
listing by depth so the walk is bounded by `selector_depth_limit`, which D-101 already enforces and which
makes the worst case finite by construction~~ — **this position is void, and it was the cheapest of the three**:
the parameter and the save-time bound behind it are both deleted
([D-105](decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)),
so there is no number for a listing to inherit, and the walk is finite only because the closure is acyclic and
is discovered by walking it; or drop the "and at what depth" half of the requirement, which
removes the transitive walk and keeps the single-hop refusal.

**What round 11 did to it: this measurement gained callers rather than changing shape.** Adding a name to an
audience used to be an insert into `audience_member`; **it is now a save of the whole expression** (D-105), so
every hand-typed exception added to an audience that references another one runs the editor's referrer walk —
the listing is priced **per name added**, which is a different traffic pattern from *once, when somebody edits
a rule*, and it arrives next to the two-writers problem D-105 names in the same breath. The same walk also
became, in the same round, **the only structural guard the save path has at all**: the cycle check across
audiences is a reachability walk over the closure, and with the depth bound gone it is the only thing standing
between a saved expression and one that never terminates. One measurement therefore now answers two questions —
is D-103's protection cheap enough to be obeyed, and does saving a wide audience cost anything an editor can
feel — and the second is a question nobody had to ask last round. **Still 🟡**, for its original reason: the
fallback is already written down as a decision entry (weaken the D-103 rule, in the open), so the exposure is a
guard people route around rather than a design with no answer.

**Needed.** Before an editor offers to name an audience. If the answer is "not cheap", the fallback is not a
slower screen but **a weaker D-103 rule**, which is a decision entry, not an implementation detail — and it
should be taken in the open, because the property being traded is the one that keeps a deleted set from
widening access.

**Impact.** If the walk is slow at real sizes, either the guard is skipped under time pressure or the
feature people use is the one that bypasses it. Both are worse than the measurement.

---

### F-17 ✅ **Closed** — the expression is the record, so a nested audience's past is recomputed and never promised

**Answered by [D-110](decisions/round-13.md#d-110--the-expression-is-the-record-of-whom-a-grant-reached),
which removed the premise rather than filling the gap.** *"Whom did this grant reach in May?"* is answered, if
at all, **by evaluating the words against the data of May**, and these documents do not promise the answer. The
audit record of a grant's reach **is the expression**; the preview is logged as *a rendering on a date*, not as a
statement of members. **None of the three positions below is adopted** — not acceptance-by-declaration, not
materialized dated expansions, and notably **not the `audience_revision` row this entry recommended**, because
D-110 refuses exactly what made it attractive: *the audit trail records the edit, not the meaning that existed
before it*, so a history of inner expressions is not being kept and a table for it would be a promise these
documents have just declined to make.

**Why the question lost its force rather than its argument.** Two things changed the ground under it. First
[D-109](decisions/round-13.md#d-109--nothing-a-rule-names-is-deleted-deprecated-hidden-disabled--and-a-tab-instead-of-a-report):
**if nothing a rule names is deleted, the words stay evaluable long after their reason is gone** — a retired
office still resolves, a deprecated group still resolves, a name stays reserved — so a past-date recomputation
is usually *computable* rather than usually impossible. Second D-110's own refusal of the roster: the tempting
fix was always "keep the list", and **the list is the table this corpus has deleted twice**. What is left is
honestly bounded, which is the most any answer here was ever going to be.

**The part that is conceded rather than solved, written down so nobody finds it sideways.** Editing a shared
audience changes what **every grant that names it** has meant all along, because those grants hold a word and
not a copy — **an edit to a shared audience is therefore a retrospective edit to every rule that names it** — and
a re-evaluation for a past date uses *today's* inner expression. This is why a past-date answer can be **wrong**
rather than merely missing, which is worse and is the reason the entry was 🟡. **What D-103 already provides is
the control, and it is the only one there will be: the editor prints the resolved set before an edit to a shared
expression saves**, so the person editing sees, at least once, the thing they are changing backwards in time.
**What is not kept is a history of inner expressions.** D-103 accepted this as the price of reuse; D-110 makes it
an explicit consequence for the audit question instead of an implication.

**The one asymmetry that survives, and it is the real residue.** A **group** still answers *"was she in it on
1 June 2024?"* from dated rows, and an **audience** still does not. D-110 settles what an audience *records*, not
what it *can reconstruct*, and the guidance this entry already gave stays the guidance: **a set you must be able
to reconstruct across time is a group, not an audience** — which is now advice backed by a ruling about the record
rather than by a gap in the storage.

**What reopens it.** An incident, not a gap. Specifically: **a question asked during an actual safeguarding or
dispute review that a recomputation could not answer**, because that is the moment the promise these documents
just declined starts costing something, and D-110's honest boundary ("possible, never promised") is the sentence
that will be quoted at somebody. A second trigger is the D-112 size trigger, since a recomputation over years of
data is cheap at a few hundred people and may not be at a few thousand.

**Question.** "Whom did this grant reach on 1 June 2024?" is answerable for a **group** — its roster rows are
dated — and unanswerable for an **audience**, whose expression is evaluated live. D-103 makes that sharper:
with `AUDIENCE(code)` a rule can now contain another rule, so the set reached in 2024 depended on the shape
of an expression **that nothing has stored a copy of**, edited ever since. The one place the old shape existed
is the audit trail, and its payloads **expire after 24 months**
([D-088](decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)).
So past a two-year window, a nested audience's past reach is **not reconstructable at all** — not imprecise,
unavailable. Is that acceptable, or is this the case that finally justifies
[F-7](#f-7--dissolved--a-nightly-rebuild-of-cached-answers-and-a-materialized-effective-permission-table-are-one-job)'s materialized table?

**Why this is the strongest version of F-7's argument, and why it is stated separately.** ~~F-7 is framed as
performance and answered "start with cache-only"~~, which is right on its own terms. *(Two corrections from
later rounds, both against this sentence rather than this entry: F-7 was* **dissolved** *in round 13 and never
answered, and* [D-114](decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation)
*has since deleted the cache-only arm the recommendation preferred — so there is no longer a first arm to start
with, and a materialized table would arrive on its own merits at* [D-112](decisions/round-13.md#d-112--the-systems-scale-is-stated-hundreds-of-people-tens-of-registrants-per-event)*'s
trigger. The question raised below is untouched by that, and is the harder one.)* This question is not about
speed: it is that **the audit trail's short half and the question's long half do not overlap**. A safeguarding
question ("who could see this child's record while X was treasurer?") is asked years later, of a system whose
expressions are recomputed from state that has moved, over a set — referenced audiences — that nobody
versioned. D-103's own note that the listing matters "more than it looks" is the same observation one hop
away.

**The uncomfortable symmetry, which round 11 made sharper.** D-098 kept `person_group_member` and
`audience_member` as **two dated sets of people** on purpose, and refused to unify them, because a group states
its members and an audience computes them — and that refusal is exactly what made one of them answerable
across time and the other not. **D-105 deleted the second of those two tables**, so the pair these documents
have to live with is now a group's dated roster against a `PERSON(x)` leaf that carries no date at all. The
hand-written set, which used to be the half of an audience that *could* answer *"was she in it in 2024?"*,
moved to the unanswerable side along with the rest of the expression: same asymmetry, one table narrower, and
worse in one specific way — **a set somebody keeps by hand was the cheap instance of the reconstructable
answer, and there is no hand-kept set left inside an audience that can give it.** Any answer here still pushes
toward making an audience a **dated snapshot series**, which is what D-101 refused to store and D-098 refused
to merge; what changed is that the pressure now arrives from the plainest audiences in the system rather than
from the nested ones this entry was written about.

**Positions.** **Accept it, and write it down** — these documents state plainly that an audience has no
reconstructable reach beyond the audit window, and that a set you need to be able to reconstruct is a
**group** (cheap, honest, and consistent with D-098's "a group states its members; a selector picks them";
**this is the default these documents currently assume**). **Materialize dated expansions** for audiences a
live grant names — F-7's option, arriving with a sweep that must not fail silently, since a silent refresh
failure is an access bug nothing detects. **Version the expression instead of the result** — an
`audience_revision` row per edit, small because it is a tree of ids, which answers "what did the rule *say*"
but not "whom did it reach", and is a much cheaper promise to keep.

**What round 11 did to it: it widened the hole and raised the value of one answer.** D-105 did not dodge the
history question — with `audience_member` deleted, *"who was on this audience in 2026?"* joins the questions
that are a recomputation over audit payloads, the payloads expire after 24 months
([D-088](decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)), and
so the question stops being answerable in 2028: the same hole, one table wider, **accepted rather than papered
over**. What moved is the worth of the third position. `audience_revision` used to answer *"what did the rule
say?"* and to stop there, because the hand-typed people lived outside the rule in a table of their own. **A
name somebody typed is now part of the rule**, so versioning the expression versions the names with it: for a
hand-written set — and for exactly that part of any audience — a revision row now answers the reached-set
question outright, dated by *edit* rather than by *validity*, which is the as-of/audit-time distinction the
glossary insists on rather than a new one. It still answers nothing for `GROUP(x)`, `ROLE(x)` or a referenced
audience, all of which move under an expression without being written in it. **A narrower promise than the
entry implied, and a real one.** The colour stays 🟡: this is the same question with more evidence behind one
option, and still no question implementation waits on.

**Recommendation.** The third, plus the first. Storing the *expression* per edit is nearly free, it is the
question a reviewer actually asks, and it keeps the answer honest about what it is; the *reached set* stays a
group's job and these documents should say so out loud rather than leaving a reader to discover the gap during
an incident. **The second only if a real question demands it**, and then decided together with F-7 rather than
as a history feature, because a maintenance sweep that can fail silently is the same liability either way.

**Schema impact.** One append-only table (`audience_revision`, or a dated copy of `audience_operand`); or
materialized expansion rows and the sweep that keeps them true; or nothing, and a sentence in domain/06 and
the glossary fixing what an audience does **not** promise. **Note the tension with D-101's design note that an
audience's history is not stored** — whichever way this goes, that note has to be checked against it.

**Needed.** Before someone asks the question during an incident, which is when the answer gets written as an
emergency migration.

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

### F-19 ✅ **Closed** — A permission code is a row, prose names codes, and nothing checks the two

**Answered: the class is real, the naming grammar is now rules, and the check is a hand-run report**
([D-104](decisions/round-10b.md#d-104--a-permission-codes-last-segment-is-an-action-and-a-registry-that-prose-contradicts-is-a-fiction)).
The question is kept whole below rather than summarised, because the answer turns on what the fourth instance
turned out to be, and that is only visible against the three that came first. **One of the four was resolved
by deleting the thing, not by deciding its name** — which is the part of this entry worth reading twice.

**Question.** A permission is a **seeded row** whose `code` is a stable identifier; the catalog is **prose
about rows**; and the rest of these documents are **prose about the prose**. Two hops, and no reference back.
This is the **fourth time the gap has produced a defect**, and the four are different defects, which is why
one entry covers them instead of four:

| Instance | What disagreed | How it was fixed | What that fix cannot do |
|---|---|---|---|
| `dependent.medical.view` | a **code vs a rule over codes** — the code was correct, the namespace/prefix reading made it reach further than anyone granted | the subsumer was deleted: no per-resource `admin`, no prefix match ([D-068](decisions/round-05.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle)) | it removed *one* way prose could be wrong about a code; it did not make the catalog and the rows incapable of disagreeing |
| `event.answer.view` / `event.answers.view` | a **code vs its own spelling** — [D-102](decisions/round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it) wrote the plural while its entry was new, and §12 of [data-model/05](data-model/05d-invariants-and-seed.md#12-what-the-organization-starts-with) did too | **reconciled.** Declared: the catalog's spelling is the registered one, **one code, not two** ([data-model/08 §8](data-model/08-events.md#selectors-that-bind-to-an-event)). The plural is now **gone corpus-wide — grep reports zero**, so this row is fixed rather than disputed | it relied on **the catalog being the arbiter**, and that assumption is what the third case breaks |
| the event **QR** capability | a **code vs the catalog's own naming grammar** — it was being registered as `event.qr` while prose elsewhere called the same capability `event.qr.rotate`, against patterns the catalog stated as *descriptions* of the codes it already had | **closed: neither spelling was chosen — the capability never existed.** Neither string survives anywhere in the corpus. It entered the round as prose, was half-designed in the course of arguing about its name, and left as prose, **with no decision entry involved at either end** | **it proves the registry refuses nothing.** A capability that never had a row never had a check, so the argument could run for a whole round in two files that both looked like they were describing something real |
| `PERSON(` | **two decisions vs a second registry** — [D-100](decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape) and [D-101](decisions/round-10b.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree) both wrote `PERSON(x)` from the start, while the seeded `selector_type` registry — copied from the evaluator's arm list rather than from D-101's grammar — carried twelve rows without it, **for the whole round** | the registry grew its thirteenth row (D-101's amendment; see [F-5](#f-5--closed--nothing-is-missing-from-the-registry-and-the-last-gap-was-a-selector-that-should-not-have-been-in-it)). **The control this round wrote for itself, `MEMBERS * ROLE(x) + PERSON(y)`, did not parse** — and the pages that noticed the gap "fixed" it by reading `PERSON(y)` as `LIST`, the wrong reading, since `LIST` is one set belonging to one audience and subtracting it removes everybody on it | **this is the instance that argues for the report**, and it was found by reading, in a file nobody had been asked to check — one round, two registries, same defect |

**What the third case actually was, because this entry guessed wrong about it.** It asked whether `qr` was an
object with actions hanging off it — rotate, print, preview — or the whole action, and answered itself that
"the answer is which shape the seeded row has". **There is no seeded row, and D-104 says the question was the
wrong one to ask.** Grepping the closed round finds neither string anywhere: not in the catalog, not in the
events module, not in the ERD, not in the decision log. What survives of the event door code is this entry's
own description of a dispute about it. Presence is left where
[D-067](decisions/round-05.md#d-067--presence-is-a-three-valued-fact-on-the-registration) and
[EV-5](#ev-5--closed--it-split-and-the-new-permission-sits-a-level-lower) put it: somebody holding
`event.presence.mark` records who came, with a clipboard if necessary. **So the honest answer to "did we
decide against check-in codes?" is no** — and that is the finding, not a typo and not a morphological
disagreement: a thing was possible in prose, argued over as though it were in the model, and removed without
ever having been in the model. **There is no QR capability in this system, seeded or deferred, in the events
module or anywhere else**; if door scanning is ever wanted it arrives as an open question, then as a decision
entry naming the permission, the artifact that gets rotated and who may reprint it — not as a code appearing
beside a paragraph about a door. The only QR code in these documents belongs to a payment, and
[D-075](decisions/round-06.md#d-075--money-arrives-from-a-bank-api-a-payment-is-requested-by-variable-symbol-and-qr-code)
already rules that **a QR code is a rendering, not data**.

**Why the earlier fixes could not have caught it, stated once.** `answers` versus `answer` was settled by
naming an arbiter, and that worked **only because the catalog was self-consistent**; the QR case was the first
where it was not, because both readings of `event.qr` fit the catalog's two stated shapes — resource+action,
or resource+subresource+action. **A description of how existing names happen to look cannot arbitrate a new
name.** And the fourth instance was not a code at all but a *selector*, in a different registry, in the same
round — which is why the fix below is a diff over every registry rather than a rule about permissions.
Underneath all four is one sentence from D-104: **a convention that is followed and not stated fails exactly
once, on the first thing nobody thought to compare.** It applied the rules below to the registry as it stands
and **found nothing to correct** — of the sixty-six live codes in the catalog, sixty-five satisfy both tests
and the sixty-sixth is the named exception. The corpus was already right, the rule was nowhere written, and
the capability arrived anyway.

**The naming grammar, promoted from a description to three rules**
([D-104 §2](decisions/round-10b.md#d-104--a-permission-codes-last-segment-is-an-action-and-a-registry-that-prose-contradicts-is-a-fiction),
written up as rules where the patterns live, in
[permission-catalog §1](appendix/permission-catalog.md#1-conventions)). Three, for a code being **added** —
the only moment they cost nothing:

| Rule | What it refuses |
|---|---|
| **The last segment names the action.** | Read the code alone and ask *what does this let me do?* `event.grant_access` answers it, `event.qr` does not. A noun-final code states an object, and since [D-099](decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality) a grant states exactly one thing: a grant of an object would need a second sentence to say what it permits, **and a second sentence is where a permission's real scope always hides**. |
| **A middle segment names something the schema stores.** | `answer` is `event_answer`, `presence` is a column of `event_registration`; `contact`, `credential`, `member`, `participant`, `request` are rows. **`qr` is nothing** — D-075 is explicit that it is a rendering of a symbol, an amount and a recipient. A permission may not be built out of an artifact the database does not keep, because **a grant has to be checkable against stored state and there is none**. This is the substantive test the QR case needed, and it settles the case without appealing to morphology at all. |
| **No grade words, and no prefix.** | `admin`, `all`, `everything`, and any code whose meaning is "every sibling under this prefix" — [D-068](decisions/round-05.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle) deleted sixteen of them and computed the wrong answer for `dependent.admin`. **Restated as a rule about codes that have not been written yet**, which is the only form of that decision that can still prevent anything. |

**`system.admin` is the single named exception, and a rule with an unnamed exception is a rumour.** Its last
segment is not an action and it stays, because its meaning is **defined by the resolver** — checked outright,
`applies_to = unit`, never reachable through an item grant — rather than read off its name, and because D-068
exempted it in so many words rather than by omission. **It is the only code in this system allowed to be a
noun, and the exemption is not a precedent**: `<resource>.admin` is exactly what the third rule refuses and
exactly what was deleted.

**Adopted: the diff report, stated honestly.** Before a round closes, every dotted token in prose is diffed
against **every** seeded registry these documents keep by hand — `permission.code`, `selector_type.code`,
`grant_scope_type.code`, `reason_code.code`, the seeded audiences — **in both directions**, so the report says
which tokens name no row *and* which rows no prose names. This entry's own recommendation, taken: it is the
only option that would have caught **all four** instances, including the two the catalog wrote itself and the
one nobody had noticed.

- **It is a report run by hand.** This repository has no build step and no CI to hang a check on, so
  [D-081](decisions/round-06.md#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now)'s
  wording applies exactly: **a convention, not a guard.** Saying that is part of adopting it, not a caveat
  appended afterwards — **nothing in the system will ever notice a code drifting from its row, including after
  this entry**, because the enforcement adopted here is a person remembering to run a script.
- **It runs on the documents**, because there is no schema to check against
  ([D-072](decisions/round-06.md#d-072--the-documentation-carries-no-sql-the-schema-is-the-orms-job)) —
  and that is the condition that makes the whole class possible: **the prose *is* the specification, so prose
  is free to contradict the registry, and there is no compiler to notice.**
- **The cost is the allow-list and it is not small:** illustrative codes, and deleted codes shown struck on
  purpose, both match no live row. The report is worth running only if that list is **re-read rather than
  frozen** — the same discipline the struck-text rule already imposes on the decision log.

**The half of this that was time-critical, and still is.** A code is the only identifier in this system
explicitly **not renameable**: the catalog's own words are that adding one is free and renaming one is a
migration over every grant row naming it. **Today the cost of a naming mistake is a grep; the day the first
grant row exists it becomes a migration** — and that asymmetry, not the typo, is why D-104 was written as a
decision rather than fixed quietly. Related, and **still unfixed**, because D-104 reaches codes and not
attributes: `permission.applies_to` and `permission.right_kind` are seeded columns prose gets to contradict the
same way, and a code named in prose with the wrong `applies_to` is a subtler version of all four instances
above — a capability described as grantable somewhere it cannot be. The report diffs tokens, so it will not
catch this one either.

**The two options not adopted, and why.**

- **Declare the catalog the registry and link every prose mention** — a code appearing in prose is a link to
  its catalog row. Correct in principle, unenforceable here: a link nobody is required to write is a review
  convention, in D-081's exact wording, *a convention, not a guard*. It is also what the report makes easy
  afterwards rather than a substitute for it, since a wrong code linked to the wrong row is still a wrong code.
- **Ban codes from prose** — no. The codes *are* the specification's vocabulary; a document that cannot name
  `event.presence.mark` cannot say what it grants.

*(The third option, the diff script, is the adopted one above. Its own wording before closure was the honest
part of it: it said the check "generalises for free to the other registries these documents keep by hand", and
the fourth instance landed in exactly one of those — `selector_type`, against §8's table — one round later,
having been found by nobody who had been asked to look there.)*

**Schema impact.** **No rows change.** The grammar renames nothing today; `system.admin`'s exemption already
existed and is only now written down; and the QR capability is **absent, not renamed** — the seeded
`permission` row this entry was braced for is a row that never ships. The report is zero-schema (D-072), and
what it will diff against is [data-model/05 §8](data-model/05a-audience-and-grammar.md#the-selector-registry) with its
thirteen rows — twelve for the whole of round 10, thirteen when this entry was written, twelve again for the one
round after `LIST` went
([D-105](decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)),
fourteen with the two age operands, and **thirteen since D-113 deleted a row that was never a selector** — the
catalog's sixty-six codes, `grant_scope_type`, `reason_code` and the two seeded audiences. **The
count moving under the report is the point of adopting it**: a row appearing or vanishing is exactly what the
diff exists to notice, and the round that deleted `LIST` is the round that would have caught a page still
naming it, had anyone run the script. **The registry has now changed size in four consecutive rounds, which is
the strongest argument this file has for a diff over a sentence** — and note what a diff would *not* have caught:
`GUARDIANS` was in the table, in the prose and in the count, and agreed with itself everywhere
([F-5](#f-5--closed--nothing-is-missing-from-the-registry-and-the-last-gap-was-a-selector-that-should-not-have-been-in-it)).

**What stays open after this.** The failure mode is the only one it has, and D-104 says so plainly: **a report
that cannot be violated, only forgotten.** The entry becomes obsolete when there is an implementation with a
seed directory and a test that loads it; until then the registry and the prose are two copies of one thing
([F-10](#f-10--which-invariants-the-orm-cannot-express-and-who-writes-those)'s general shape, in its cheapest
instance) and the report is the check that they still agree. The `applies_to` / `right_kind` half above is the
same class, explicitly unfixed, and four instances in ten rounds is not bad luck — every module added
([D-055](decisions/round-04.md#d-055--the-permission-catalog-is-deliberately-comprehensive-and-granular))
multiplies the surface it would have to catch.

---

### F-20 ✅ **Closed** — `WHITELISTED` stays unseeded because there is no state to evaluate, and the feature arrives anyway

**Answered: refused, and the refusal is not the loss it has been reading like since it was filed.** The operand
stays out of the registry for its own stated ground — **there is no state to evaluate** — and it is confirmed
rather than re-argued by [D-113](decisions/round-13.md#d-113--the-guardianship-channel-has-no-expression-guardians-is-not-a-selector),
which deleted a selector for exactly this class of error: **a name in the language with no `selector_type` row
behind it, or a selector naming a mechanism the model implements somewhere else.** `WHITELISTED` is the same
shape one step earlier — the row would be minted to describe a flag no table carries — and D-108's `SCHOOL`
refusal is the third instance of the same refusal. Three refusals, one rule: *an operand names a fact the model
stores, or it is not an operand.*

**The part of this entry that was always about a feature, now answered as one.** What people reach for the word
`WHITELISTED` to get is *"these particular adults, and only these, may do this"* — and that need is served today,
by **a `person_group` per whitelist**, aimed at the grant, dated by the grant's own period, revocable, deny-able.
**D-109 is what makes that answer newly good rather than merely adequate:** retiring such a group is now a
**`deprecated` or `hidden` flag, not a delete**, so a per-event whitelist can be retired without the repoint
every expression naming it would once have needed, and without the empty-operand-widens-a-deny hazard that made
retiring a set dangerous in the first place. **So the thing people actually wanted from the operand — a named
set you can point grants at, and put away when you are done — exists, as grants over groups.** What the operand
would still add is a *derived* set, and this system derives no such thing: it stores a `guardianship` row and no
query over it as an audience (D-113 checked this rather than assuming it), exactly as it stores no
`is_whitelisted` column.

**What it cost.** One sentence in the tiers-and-refusals list, which is all this entry ever asked for, and the
continued obligation that **the two halves stay decided together**: if EV-6's *"invited, has not answered, we
made room"* ever gets a column, `WHITELISTED` arrives as its operand automatically, and at that moment it stops
being a refusal and becomes a seed row with a fact underneath it. **That is the reopen, stated as a condition
rather than a date**: `WHITELISTED` is unseeded because there is nothing to evaluate, so it becomes seedable the
day there is — and the day there is, this entry's answer flips without needing a new argument.

**This is one question asked in two modules, and it is carried twice on purpose.** The **events** half —
whether a person's standing on one event ("invited, has not answered, we made room") deserves stored state —
is **[EV-6](#ev-6--whitelisted--the-word-people-reach-for-with-no-stored-state-to-name)**, where the tier
algebra lives. This entry is the **language** half, which is smaller and gets answered first.

**Question.** [D-102](decisions/round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)
shipped four attendance tiers and refused `PRESENT` on a stated, representable ground: nothing is stored until
a person marks it. `WHITELISTED` is the second name people reach for, and it must be refused **on its own
ground rather than by inheriting that one** — because unlike `PRESENT` there *is* something that could be
stored, and the refusal is therefore a decision rather than an observation.

**The answer these documents already imply, stated once so it stops being re-derived.** "Let these people
register" is an **allow grant** on the event naming `event.register_self`, aimed at an audience whose
expression is either the hand-typed `PERSON(a) + PERSON(b)` or a `GROUP(x)` — revocable, deny-able, aimed at a
**set** rather than a flag, and **dated by the grant's own `valid_to`** now that the per-name dates of
`audience_member` are deleted
([D-105](decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)):
*"these three until August"* is that grant carrying a period, and a different set for August is a **second
grant**, which is the shape this refusal now has to keep paying for. **Which of the two spellings the sentence
wants is something these documents do not settle, and it is written out rather than picked**: the handful of
names a leader ticks for one event is the sum, the standing camp-staff list is the group, and D-105 kept both
on purpose — a set that outlives the event belongs in a roster somebody maintains, while a set that exists only
to widen one grant must not become one, because editing a roster moves every grant that reads it
([D-098](decisions/round-10a.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority),
and D-105 restates that reason as unchanged). **A `WHITELISTED` operand would reimplement grants with fewer
powers**, and it would do it in the one place where the model has just spent a round deleting hard-coded
sentences from the resolver and replacing them with grant rows (D-102's whole move). So: **refuse it**, and
say why beside the `PRESENT` refusal. What is *not* answered here is the narrower sentence EV-6 carries, and
if that one ever gets a column, `WHITELISTED` arrives as its operand automatically — which is the reason this
entry exists as a pointer rather than being folded into EV-6: **the two halves have to be decided together,
and the language half is the one that gets decided first, by whoever adds the column.**

**Needed.** A paragraph where the tiers and the refusals are listed. Nothing else, and nothing before
implementation.

---

### F-21 ✅ **Closed** — no report; a tab on the permissions page; and unbounded cost is accepted at the stated size

**Answered in two pieces, by two decisions, and the second is the one that made the first affordable.**

**1. There is no report. There is a tab.** [D-109](decisions/round-13.md#d-109--nothing-a-rule-names-is-deleted-deprecated-hidden-disabled--and-a-tab-instead-of-a-report)
retires the standing reports **about rules** with **one tab on the permissions page**, and this entry is the third
of the three its Supersedes line names — D-106's failing-leaf report, D-105's merge-repoint duty, and part of
this entry. **Precision matters here, because "every report" would be false:** reports outside the expression
language survive it — the dead-deny hygiene line in *Deny* (a live deny matching no live allow is dead weight),
and D-071's report of role assignments nobody forced to end. **What the tab replaces is a standing report about
what an expression names and what it costs**, which is exactly what this entry was. Its **Broken** section lists every live rule whose
expression names a deprecated, hidden or disabled thing, **or fails to resolve at all** — which is D-106's
failing-leaf column, arriving on the page instead of on a report. **It does not list wide audiences, because
nothing produces that list any more**, and the reason is the elegant part of D-109: **the leaf broke because the
thing it named was deleted, and here nothing is deleted.** A deprecated group still resolves; a hidden office
still resolves; a disabled one resolves to the empty set *knowingly*, with the flag write printing the rules it
touches. **The reader question this entry spent a round on — "who reads it?" — resolves to *nobody, because
there is nothing to read*, and that is a better answer than naming a person and a cadence would have been.**
What replaces it is better than a report for the ordinary reason D-109 gives: **a report has to be remembered and
a tab is where the person already is.**

**The tab has two sections, and this entry owns only one of them.** **Broken** is D-109's definition and this
entry's population: *something has happened to your rule behind your back*. **"Unusual"** — rules that resolve
correctly and merely look odd — is [F-13](#f-13--closed--a-rule-that-resolves-correctly-but-looks-odd-is-listed-as-unusual-never-as-broken)'s,
and its answer stays there. **The two are not one list, and neither entry may claim the other's population**: a
grant that omits `MEMBERS` is not broken, and putting it in Broken would train readers that the safeguarding
section is a matter of taste.

**2. Nothing bounds what a check costs, and that is now accepted at a stated size rather than merely
unaddressed.** [D-112](decisions/round-13.md#d-112--the-systems-scale-is-stated-hundreds-of-people-tens-of-registrants-per-event)
put a number under the refusal: **a few hundred people, a few dozen registrants on a typical event, a big camp on
the order of two hundred.** At that size *"nothing bounds what an expression can cost"* is **accepted**, which is
a different claim from *"nothing bounds it and nobody has looked"*. **The refusal of a cap is untouched and gets
stronger**: a budget the resolver stops at is an operand resolving to nobody, an empty set behind a `-`, and
**the cap becomes the thing that decides who a grant reaches**. D-112 states the same boundary from the other
side — *"nothing in the design depends on the number, on purpose"*, with the two rules that must survive any
growth being *a check compiles to a predicate and never materializes the set* and *a listing is paginated*, so
**the system gets slow before it gets wrong**.

**What it cost.** Three reports retired, one tab built, no schema, and **the last standing report of this shape
gone** — which retires the meta-filing below rather than confirming it, and is worth reading against the
paragraph underneath this one. The residual hazard is unchanged and now honestly labelled: **the wide audience
nobody looked at, on a check path that has no reason to complain.** It is survivable because of a number, so the
reopen is that number.

**What reopens it.** D-112's trigger — **a few thousand people, or a thousand registrants on one event** — which
reopens F-15, F-16, F-7 and this entry, in that order. ~~**This entry last**, deliberately: the nightly rebuild is
the cheapest of the four to redesign and the expensive ones are the ones a user feels first.~~ **Round 14
re-arranges that ordering rather than confirming it, because the thing ranked last has been deleted**
([D-114](decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation)):
the rebuild was the cheap one to redesign precisely because it was affordable, and what it quietly paid for —
pre-resolving the expensive screens off the user's thread — is now paid for **on open**. **The ordering is
unchanged and one shorter, matching what [D-112](decisions/round-13.md#d-112--the-systems-scale-is-stated-hundreds-of-people-tens-of-registrants-per-event)
now says in its own copy of that list: what used to be buffered by a nightly job is buffered by nothing.**

**A dependency recorded by [D-114](decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation),
and this entry is where it belongs because this entry owns the tab.** [D-109](decisions/round-13.md#d-109--nothing-a-rule-names-is-deleted-deprecated-hidden-disabled--and-a-tab-instead-of-a-report)
ruled that the permissions tab is **computed when opened** rather than kept as a standing report — a ruling that
was comfortable while a nightly job was resolving expressions anyway, and which **now has no fallback**: an
opening tab walks the live grant and expression rows, resolves each expression, and does it in front of the
person who clicked. **That is affordable at the stated size and the ruling stands; what changed is that it is now
the only thing standing under it.** The tab is written against `which_of(people[], code, item)` and
`can_many(person, codes[], item?)` rather than a loop of single checks, so the cost is one pass and not N — and
"unbounded per-check cost accepted at a stated size" now means **unbounded cost paid at open**, which is the same
number with a different name on it. Recorded as a dependency, not as a risk, and the reopen is the same number as
ever.

**Three findings, and the answer that ended them.** ~~Three things are missing from it and all three are this
entry: no role is named as its reader, no cadence is set, and no number says where *wide* becomes *too wide*.~~
That diagnosis was correct and the fix it argued for — *name a person, name a cadence* — is not what happened.
**The user's answer was to stop building reports and put one tab where the writer already is**, which retires the
reader-and-cadence-and-threshold problem by removing the thing that needed a reader. The finding that named this
pattern is kept verbatim at the end of this entry, because it is the discovery and D-109 is the answer to it.

**Question.** For ten rounds a permission check cost a bounded amount, and the bound came from one place:
`selector_depth_limit`, applied at save over the expanded tree.
[D-105](decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)
deleted the parameter and the save-time check with it, and ruled that the tree is stored **exactly as its
author wrote it** — one row per node, left to right, no rebalancing, because a rebalanced tree is a different
expression than the one a person wrote. What survives as a structural guard is **the two cycle walks**: one
inside the expression, one across audiences through every `AUDIENCE(x)` leaf. They refuse an expansion that
never terminates and they say nothing whatsoever about one that merely costs a lot. **A check's cost is now
bounded by acyclicity alone** — no bound on height, and none was ever asserted on breadth — and the
expensive shapes are not exotic: `EVERYONE` is one leaf that reaches everyone the resolver can see, and a
hand-typed set of forty names is forty leaves where the last round kept one leaf and an indexed table.

**What replaced the invariant, and what kind of thing it is.** This is D-081's pattern executed exactly: the
rule's name outlives its mechanism. *"Depth must be refused at save, over the expanded tree"* retires as an
invariant and survives as **a standing report of the widest and deepest audiences with their per-check cost**,
beside the operand cache. D-105 states the weak half itself rather than letting it be discovered: **a report,
with no CI behind it — a convention, not a guard**, and the third control of this shape the authorization
module now depends on, after [F-13](#f-13--closed--a-rule-that-resolves-correctly-but-looks-odd-is-listed-as-unusual-never-as-broken)
and [F-19](#f-19--closed--a-permission-code-is-a-row-prose-names-codes-and-nothing-checks-the-two). **Three
things are missing from it and all three are this entry: no role is named as its reader, no cadence is set,
and no number says where *wide* becomes *too wide*.**

**The half that is refused on purpose, and has to stay refused.** Whoever reads this entry will reach for a
cap on the read path — a depth the resolver declines to walk, a budget it stops at — and the design refuses
that for a reason that got **stronger**, not weaker, when the bound went: *the cap becomes the thing that
decides who a grant reaches*, because a walk that stops early is an operand resolving to nobody, and an empty
set behind a `-` makes the answer wider. Until last round that refusal was the back-up position behind a
guard that existed at save time; **now it is the entire design**, and the only sentence left to say about cost
is a number on a report somebody has to choose to open. The line worth keeping is the one
[F-15](#f-15--closed--the-per-item-preview-is-cheap-at-the-stated-size-and-this-is-what-reopens-it) already walks: a limit on what
a **preview lists** changes what a person sees and is allowed; a limit on what a **check walks** changes who
has access and is not.

**Positions.** **Name a reader and a cadence** — the cheapest answer in this file, one sentence, and it changes
no data; the report exists and nobody owns it. **Print a warning threshold** — honest only while it stays
advice in the report's own text, because the moment somebody is forced to obey a threshold it has become the
cap the paragraph above refuses, and a guard that pretends to be a report is worse than either. **Or accept
unbounded per-check cost as a property of the system** and lean on the operand cache and the assumption behind
it ([assumption 61](#i-assumption-index)) — which is what an implementation would do by default anyway, and
the reason this entry exists: to stop that being an accident. *(Of the three arms, this one aged best and then
strangely: both caches behind it were deleted.* [D-114](decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation)
*takes the answer cache and the operand cache together, and the operand cache deserves the sharper blame: it was
keyed* `(person, selector_kind, selector_arg_id[, item])`*, so it named a person in the key exactly like its
neighbour did — which is why no narrowing of a bump set could have saved either of them. **What survives is a
roster, and a roster is a different object:** keyed by a name, holding dated rows, with no person and no item in
the key. `MEMBERS` is not a roster and cannot be cached as one; it is evaluated on the checked date. The
per-request memo is the nearest surviving relative of an operand cache, and it is not an answer cache because it
dies with the request.* [assumption 61](#i-assumption-index) *is struck, so this arm's backing row is a history
row.)*

**Schema impact.** **None, and that is the trap.** There is no column to hold a limit, deliberately: a limit in
a column is a limit in the check, which is the refused thing, and D-072 means these documents will not write
the query either — what exists is a walk over `audience_operand` that someone has to run.

**Needed.** Before an implementation ships a resolver and no report. 🟡 and not 🔴 because nothing blocks the
schema and the likeliest answer is one sentence naming a person; but the failure this entry describes is not a
slow system, it is **the wide audience nobody looked at, on a check path that has no reason left to complain**,
and unlike F-16 there is no measurement that makes it go away — only a reader.

**Round 12 gave this report a second column, and it should not become a second page.**
[D-106](decisions/round-11-12.md#d-106--a-failed-operand-stays-the-empty-set-the-missing-half-was-a-report-not-a-refusal)
refused every refusal that would have made a broken operand stop a save, and what it bought instead is a list:
*the audiences with a leaf that resolves to nobody*. That is the same page, the same audience owner, the same
"somebody has to open it" weakness — **one report, two columns: the widest expansions, and the failing leaves**
— and [F-23](#f-23--closed--words-only-the-expression-is-the-record-and-the-preview-is-a-rendering-on-a-date)
would have added a third ("whom does this reach today, against whom it reached when it was saved"). **Three
findings from three rounds, each of which concluded that the answer is a report nobody is obliged to read, is
itself a finding**: this module now has a page it cannot do without and no decision that anyone looks at it.
Whoever answers this entry is answering all three, and the honest version of the answer names a person and a
cadence rather than a feature.

**How all three were actually answered, recorded against the prediction above.** Not by naming a person, and
not by a feature either — by **removing two of the three lists and putting the third where the writer already
stands.** The widest-expansions column is gone because nothing produces it (D-109 deletes the cause of the
broken leaf, and D-112 accepts the cost of the wide one). The failing-leaves column survives as the tab's
**Broken** section, which is this entry's population and D-109's definition. **F-23's third column was refused
outright by [D-110](decisions/round-13.md#d-110--the-expression-is-the-record-of-whom-a-grant-reached)** —
the words are the record, so there is no then-and-now comparison to display, and the page stays two things deep
rather than three. **The weakness the paragraph above found was real, and it was cured by subtraction**, which
is the pattern round 13 keeps landing on.

---

### F-22 ✅ **Closed** — the editor may fold and flatten for display; the stored canonical string never changes

**Answered, as an editor decision with one hard limit on it. The first position below is the answer.** The
editor **may** fold a sum of same-kind leaves onto one line and render `PERSON(a) + PERSON(b) + PERSON(c)` as a
list rather than as thirty-nine pairs of brackets; it may do the same for any sum of like operands. **What it
may not do is change the stored canonical string.** The rendering is a rendering, and these documents now say
so in one place: **display is free, storage is not.**

**Why the limit is load-bearing and not aesthetic.** D-105's ruling that the tree is stored **exactly as its
author wrote it** is not a nostalgia rule, and this round's [F-14](#f-14--closed--nothing-computes-semantic-equality-of-two-expressions-and-nothing-will)
is the reason it cannot be bent for comfort: **the stored form is the only identity an expression has**, and the
write-path checks — the cycle walk over the reference closure, the reserved-name rule, the listing of which
grants name an audience — all reason over *that*. **An editor that stored its own tidier spelling would be
rewriting the expression it was handed**, which is the one thing D-105 named as making a stored grant mean
something nobody wrote. So the flattening happens on the way to the screen and never on the way to the row, and
a reviewer who needs the exact stored text — during an incident, or a diff, or an audit export — can still be
shown it, because nothing overwrote it. **This is the same ruling F-14 reached from the other side**: sorting
`+` children so duplicates collapse is refused for being a storage change, and this entry refuses the identical
temptation for being legible instead of being tidy, which is the more persuasive version of the same error.

**What is *not* decided, and stays open inside a closed entry.** Nothing here sets a size at which a writer is
**told** to reach for a `person_group`, and the second position — **refuse above a size** — stays refused for
the reason this entry already gave: an editor that blocks the safe action teaches the unsafe one, and here the
unsafe one is inventing a group that other grants will read, which is the exact widening D-105 spent its entry
arguing against. **D-105 named the destination (*a set big enough to be unreadable is a `person_group`*) and no
round has set a trigger, and none needs to**: the flattened rendering removes the pressure that would have made
a trigger necessary, and the judgement is left where it was always going to be left, with the writer.

**What it cost.** No schema — not one column, as this entry predicted — and one rule an editor has to obey:
**the renderer is allowed to lie about shape and forbidden to lie about content.** The cost that *is* real shows
up in [F-21](#f-21--closed--no-report-a-tab-on-the-permissions-page-and-unbounded-cost-is-accepted-at-the-stated-size)'s
world rather than here, and the paragraph below about the widest-audiences report is now superseded by D-109
and D-112, which deleted the report: **a hand-typed set no longer competes for a page nobody is building.**

**Question.** [D-105](decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)
left D-101's canonical form standing: **the stored rendering prints every bracket, always**, and a sum is a
binary tree, so a hand-typed set of *n* people is *n*−1 nested pairs. Forty names is thirty-nine pairs before
a single `-` or `*` appears. D-105 saw this coming and said the honest thing — storage and display both say
what was written, and if that turns out unreadable then **a set of people big enough to be unreadable is a
`person_group`** — and then pointed this judgement at F-5's neighbourhood. **F-5 has already declined it**, in
its own entry: that one asks which facts about people the language cannot state, and the language states this
one perfectly. What is left is a question about **reading**, and it belongs to whoever opens the editor.

**What D-105 did not decide, and what would be decided here.** It named the destination and not the trigger.
Nothing in the corpus says at what point a writer is *told* to reach for a group, or whether anyone is told at
all; nothing says whether the fully-bracketed form is what a reviewer is **shown**, or merely what is stored —
D-101's ruling is about the stored rendering, and it already has the editor rewriting what is typed into that
form before saving, so the two are separable and nobody has said whether they are. And nothing says whether an
unreadable-but-exact expression is an acceptable thing for a second person to audit a year later, which is the
actual question: **the model is fine with the forty-name tree either way**, and only the editor cares.

**Positions.** **Say the canonical form is storage, not display** — show a flattened `PERSON(a, b, c)` on
screen, keep the nested tree in the rows, and write down that the screen is a rendering; cheapest, and it keeps
D-105's "we store what was written" untouched. **Or refuse above a size** — the editor will not save a sum of
more than *n* names and says *"make this a group"*. That is a cap, and the honest difference from the cap
[F-21](#f-21--closed--no-report-a-tab-on-the-permissions-page-and-unbounded-cost-is-accepted-at-the-stated-size) refuses is that
it governs what an author may *write* and not whom a stored grant reaches — but it carries the same hazard
F-16 names for the deletion guard: **an editor that blocks the safe action teaches people the unsafe one**, and
here the unsafe one is inventing a group other grants will read, which is the exact thing D-105 kept its whole
argument about. **Or do nothing** and let the widest-and-deepest report be the feedback — which is dumber than
it sounds only because of the next paragraph.

**The link to F-21 that made this entry worth more than a style preference** *(kept as filed; its premise is
gone — the report below was retired by D-109 and its cost question answered by D-112, so this paragraph is now
evidence about how the two entries got coupled, not a live argument)*. With no depth bound, a
hand-typed set is **the deepest thing most organizations will have**, and a forty-name list will top the
deepest-audiences report while costing less than a two-level nested audience. So the report F-21 has to find a
reader for will spend its top rows on typing rather than on structure — **the signal is about who typed a lot,
not about who composed something expensive.** A threshold here, or a flattened display there, is what keeps
that report legible as a cost report. Say which of the two it is, before the report is the only control left.

**Why this is 🟢, and what would move it.** The corpus gives no hand-typed set bigger than a handful — every
worked example in these documents names one to three people, and the thousands-of-rows legacy import arrives as
memberships and participations, never as an audience expression (D-090). So the forty-name audience is a shape
the editor must not make *painful*, not a shape that has happened. It becomes 🟡 the first time a reviewer
quotes back an expression they could not read, or the first time somebody types twenty names because making a
group felt like more paperwork than they were owed — **and that second one is a story about the editor, which
is the whole point of keeping this entry separate from the model.**

**Schema impact.** None. Not one column: a size rule lives in the editor, a flattened display lives in the
editor, and the storage stays what D-105 ruled it is. **Needed:** when the audience editor is designed, which
is also the moment someone decides what a grant looks like on a screen.

---

### F-23 ✅ **Closed** — words only: the expression is the record, and the preview is a rendering on a date

**Answered by [D-110](decisions/round-13.md#d-110--the-expression-is-the-record-of-whom-a-grant-reached), in
four words: *"Words only — the expression is the record."* The first row of the table below is the answer, the
third is refused, and the middle row — the reach query — is **not adopted either**, which is the part a reader
who only skims this entry will get wrong.** The audit record of a grant's reach **is the expression**. The
preview still prints a resolved set before a save, and that printing is logged as ***a rendering on a date***,
not as a statement of who was in it. "Whom did this grant reach in May?" is answered, if at all, by evaluating
the words against the data of May, and **these documents do not promise the answer.**

**Why the refused row is refused, in the two terms that settled it.** Storing the resolved set beside the audit
row is **the roster table this corpus has deleted twice** — `audience_member` in D-105, and the assumption row
recording every prior attempt at it — and it would hold, indefinitely and against
[D-088](decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)'s
window, a per-person record of **people who were never granted anything**: everyone a rule happened to cover,
kept after the rule was withdrawn. **Storing that to make a historical question comfortable is the trade this
corpus has refused every single time it has been offered**, and this is the fourth offering. The tell this entry
already named is the right one and survives the closure: the middle row answers a question a person asks, while
the third stores an answer to a question nobody asked, about people who did nothing, indefinitely.

**What the answer concedes, since "words only" is not a free answer.** A row now says *this person wrote these
words on this date about this item* — which is a fact that cannot go stale — instead of *this grant reached
these 214 people*, which starts decaying the night somebody's birthday falls. **The audit trail gets smaller and
more honest**, and what it gives up is any claim to know whom a grant reached. That trade was only payable
because of [D-109](decisions/round-13.md#d-109--nothing-a-rule-names-is-deleted-deprecated-hidden-disabled--and-a-tab-instead-of-a-report):
**refuse to delete the nouns, and keeping only the words is not an amputation** — a retired office still
resolves, a deprecated group still resolves, so the words stay evaluable long after their reason is gone. Without
D-109 this ruling would have meant "the past is usually unanswerable"; with it, the past is usually computable
and what is left is honestly bounded. [F-17](#f-17--closed--the-expression-is-the-record-so-a-nested-audiences-past-is-recomputed-and-never-promised)
carries the half about a shared audience being edited backwards in time.

**What reopens it.** Not the calendar, and not a stale snapshot — both were ruled on in D-107 and D-111 and are
settled, **and [D-114](decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation)
settled them further by deleting the snapshot: there is no cached answer that could be stale, so the only thing
left to be stale is a *record* that was never a snapshot in the first place.** **The reopen is an incident**: a
real review in which a recomputation over the data of the date could not answer, and the missing list was the
thing that would have. If that day comes, the temptation returns in its
fifth costume, and this entry — with its table and its tell — is where the answer is argued against.

**(arrived with round 12, from [D-107](decisions/round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded).)**

**The question.** A grant's reach is printed by the editor before the grant is saved, and that printing is
what the audit trail keeps as "whom this grant was made to mean". Until round 12 every operand in the language
moved only when somebody **wrote** something, so the snapshot and the set could only diverge for as long as a
cache was warm. `OLDER(n)` and `YOUNGER(n)` are the first operands whose set moves on its own, at midnight,
with no row changing and no event to subscribe to — so the record of a decision made in March is now a snapshot
of a set that has, by November, quietly changed members. **What exactly is the record of: the words, or the
people the words reached on the day they were saved?**

**What this is *not*, stated so it is not raised again.** It is not a performance question, not a cache
correctness question, and not a request to make the language static. Those three were put and answered
([F-6](#f-6--closed--the-permission-cache-is-rebuilt-nightly-on-any-ruleset-write-and-on-request) carries the ruling: *"I know, that the time
will change, how the rules resolve and IT IS FINE"*), and a check for a past date already answers for that past
date. **What survived the ruling is the record, not the resolution** — the difference being that resolution
has an answer for every date, while the *audit trail* has an answer only for the date it was written.

**Options, none of them free.**

**Options, none of them free — verdict added by [D-110](decisions/round-13.md#d-110--the-expression-is-the-record-of-whom-a-grant-reached),
the reasoning left exactly as filed.** Row one **adopted**; row two **not adopted** (a query nobody is obliged to
run is what row one already is, and D-109 deleted the page it would have lived on); row three **refused**.

| Option | What it buys | What it costs |
|---|---|---|
| **Nothing — the words are the record** ✅ **adopted** | The design stays exactly as decided; an audit row records an expression and a person's act, which is arguably all a document about a rule can honestly hold | The people-list printed in March stops being reproducible, so "who could read this in May" has no answer in the audit trail and must be re-derived from birth dates on demand |
| **Re-derive on demand: a "whom does this reach today, and on any date" query** | A real answer for any date, computed from data the model already keeps, with no new stored set | It is a report nobody is obliged to read, i.e. **a convention, not a guard**, and it is the same page [F-21](#f-21--closed--no-report-a-tab-on-the-permissions-page-and-unbounded-cost-is-accepted-at-the-stated-size) and [D-106](decisions/round-11-12.md#d-106--a-failed-operand-stays-the-empty-set-the-missing-half-was-a-report-not-a-refusal) already put on one page — which argues for building them together, once |
| **Store the resolved set with each preview** ❌ **refused — it is the roster table this corpus has deleted twice, and it holds data about people who were never granted anything** | The March snapshot stays readable forever | A per-person history of an audience is **exactly the roster table this corpus deleted twice** ([D-105](decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other) and the assumption row behind it), and it would hold personal data about people who were never granted anything — which collides with the redaction window |

~~**How to answer it.** Pick the middle row and say plainly that the third is refused~~ — **row one was picked
instead, and the entry was wrong about its own middle row in a way worth keeping.** The reasoning for refusing
the third row was exactly right and survives verbatim: the temptation to keep the list is the oldest reflex in
this module and it has now been declined in **four** costumes, not three. What the entry got wrong was thinking a
query someone might not run was better than no query at all — D-109's finding, that **a report has to be
remembered and a tab is where the person already is**, applies to a reach query just as flatly as it applied to
the widest-audience report. **The tell that this is the right shape** still reads true and is what makes the
first row survivable: the middle row answers a question a person asks, while the third row stores an answer to a
question nobody asked, about people who did nothing, indefinitely — and D-110 added the third possibility this
file had not considered, which is that **the words themselves answer the question, given that nothing a rule
names is ever deleted.**

**Needed.** One sentence in the audit module about what a preview snapshot *is* — a rendering of the words on
a date, not a statement of fact about people — and a decision about whether the reach query is one page with
F-21's two columns or a third page nobody will open.

---

## G. Events — designed, with three things left open

The module is written: [domain/07-events.md](domain/07-events.md) and
[data-model/08-events.md](data-model/08-events.md). Fifteen questions have been answered
(D-058 … D-067, plus EV-1 and EV-5 in a later round); what remains below is what those answers
did **not** settle. None of it blocks implementation.

### EV-1 ✅ **Closed** — there is no age ceiling; the grant is the rule

**Answered: leave it.** No `min_age`/`max_age` on `event`, and no age test anywhere in the path
that places a registration ([D-070](decisions/round-05.md#d-070--an-event-has-no-age-ceiling-the-grant-is-the-rule)).

**The residual risk is accepted, not eliminated**, and it is worth restating so nobody
"closes" it later without knowing: an event opened to `all_members` can be registered for by a
nine-year-old and **nothing objects**. What makes it survivable is attribution
(`source = 'staff'`), a roster query one join away from birth dates, and the fact that the
age-bounded case is already handled by opening an event to the right unit.

**If it ever needs closing, the shape is a built-in audience, not a column on the row** —
`all_members` is a rule the resolver evaluates, so `members_aged_13_plus` can be one too. That
keeps every answer to "who may register" inside `access_grant`, which is the property D-060
bought and D-070 defended.

> **Round 12: this entry stays closed, and its reason changed.** The escape hatch above assumed an age test
> would have to be *built in* — a named audience, a row somebody ships. [D-107](decisions/round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)
> seeded the test instead: `event.register_self` granted to `MEMBERS * YOUNGER(15)` is the ceiling, written by
> an organizer on the day they want it, previewed, and attributed. **So the ceiling is now statable and this
> entry is still answered "leave it", which makes it a choice the organization makes per event rather than a
> consequence of the model being unable to say otherwise.** That is a strictly better place for a closed
> question to sit, and it is worth marking as such — because the previous reason was a limitation dressed as a
> decision, and a limitation quietly stops being one the day the vocabulary grows. **Nothing else in this entry
> moves**: the nine-year-old, the tick box nobody ticked, `source = 'staff'`, and the roster query one join from
> birth dates are all still exactly as accepted.

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

### EV-3 ✅ **Closed** — cancelling voids the request, and paid money queues

**Answered by [D-076](decisions/round-06.md#d-076--money-that-cannot-be-matched-waits-for-a-person),
in the finance module rather than here.** The recommendation was right and the mechanism arrived
before the policy did:

- **Cancelling an event voids its outstanding payment requests**, recording why
  ([finance model §2b](data-model/07-finance.md#2b-money-that-cannot-be-matched)).
- **Money already received becomes a queue item** for a person to refund or carry forward. Not
  auto-refunded — that needs an outbound bank integration and would return a grandparent's
  mistaken camp fee.

**Why the recommendation held.** It said neither, automatically, because an automatic release would
be a second automatic transition in a module with exactly one
([D-066](decisions/round-05.md#d-066--payment-confirms-the-place-and-the-release-deadline-is-the-one-automatic-transition)).
That argument was strong enough to survive contact with the payment design unchanged. **Voiding an
outstanding request is not that second transition** — a request nobody has paid against has no state
to preserve and nobody is disadvantaged by its withdrawal, which is exactly the property the waitlist
release had and this does not.

**What actually moved.** The question assumed cancellation was the interesting case and payment an
afterthought parked in finance. It is the reverse: cancellation is where **most of the unmatched
queue's volume comes from**, because a cancelled event keeps its registrations
([D-064](decisions/round-05.md#d-064--there-is-no-event-status-visibility-is-the-permission-model))
and therefore its money obligations, unless something explicitly voids them.

**Impact.** Answered; the queue itself lives in the finance module.

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

### EV-5 ✅ **Closed** — it split, and the new permission sits a level lower

**Resolved in favour of the split: `event.presence.mark`, at `contribute`.**

The reasoning recommended the split and the recommendation stood. Marking the register at a
camp door is not the same trust as deleting a child from the roster, and one permission forced
organizations to hand the clipboard-holder both. Note where the new permission landed:
`contribute`, not `manage` — **so the volunteer taking the register is somebody who could
already register themselves**, which is the right bar for the job and plainly the wrong bar
for altering who is coming. Same shape as `membership.lapse` versus `membership.terminate`
(D-022): one routine, one consequential.

Thirteen `event.*` codes now exist; `event.admin` is not one of them
([D-068](decisions/round-05.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle)).

**Round 10 note, because the answer's wording no longer exists.** The split **stands**; the *level* it was
placed at does not — [D-099](decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)
deleted `access_level`, `permission_level` and the rank integer, so "at `contribute`, not `manage`" is now
carried by nothing but the two codes themselves. Read it as: **`event.presence.mark` is a separate code
precisely so it can be granted without `event.manage_participants`**, and the gradation the level expressed
is now expressed by which code a grant names. The comparison to `membership.lapse` versus
`membership.terminate` (D-022) is the part that still says what it meant.

**See:** [appendix/permission-catalog.md §8a](appendix/permission-catalog.md#8a-events)

---

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
for the deletion; [F-20](#f-20--closed--whitelisted-stays-unseeded-because-there-is-no-state-to-evaluate-and-the-feature-arrives-anyway) settles
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
  ([permission-catalog §11](appendix/permission-catalog.md#11-roles--proposed-seed-set)) is the place
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
([permission-catalog §8](appendix/permission-catalog.md#8-audit-and-system)). Three positions exist and
none is recorded as taken:

- **The guard is enough** (current documents). One permission, marked honestly, and a rule that whoever
  holds it is reading person data. Simple, and it makes the auditor role — which has `audit.view` and
  not `person.view` — a reader of the entire person record
  ([permission-catalog §11 note 3](appendix/permission-catalog.md#11-roles--proposed-seed-set)).
- **Per-entry filtering in the history view:** show an audit row's values only where the reader could
  also see the live field. Consistent with everything §9 of
  [data-model/05-authorization.md](data-model/05c-access-log-and-resolver.md#9-access_log) says about channels, and
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

Each of these is referenced by the schema and has hooks left for it — **except health records, which
has no hooks because it has no design at all, and whose missing design is load-bearing in two other
documents. Read H-0 below before the table.**

| Area | Hooks already in place | Notes |
|------|------------------------|-------|
| **Events** ✅ | **Designed** — [domain/07](domain/07-events.md), [data-model/08](data-model/08-events.md) | Fifteen questions answered; three left in § G above. |
| **Fees and payments** | [data-model/07-finance.md](data-model/07-finance.md) — **architecture settled, policy open** | **Nine open questions**, of which one is new. Round 6 closed the architectural ones: money arrives by **bank API**, is requested by **variable symbol + QR code**, there is **no card gateway**, and unmatched money **queues** ([D-075](decisions/round-06.md#d-075--money-arrives-from-a-bank-api-a-payment-is-requested-by-variable-symbol-and-qr-code), [D-076](decisions/round-06.md#d-076--money-that-cannot-be-matched-waits-for-a-person)). What remains needs somebody in the organization asked: proration, discounts, insurance, waivers, invoices. |
| **Documents** | `access_grant.scope_type = 'document'`; the evidence-reference hook belonged to the removed requirement tables | Needs: storage, versions, retention, consent-driven access. |
| **Consents** | No `dependent.consent.*` any more — a guardian at `write` may give and manage consents ([D-074](decisions/round-06.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular)) | Needs: template, per-activity consent, expiry, revocation, who may consent. No longer connected to a membership requirement ([D-044](decisions/round-02-03.md#d-044--nothing-gates-a-membership-request-except-identity-and-payment)). **`is_legal_decision_maker` on the guardianship row is the existing hook for "who may sign" — and it is now the only place that distinction lives**, since the right level cannot express it. |
| **Health records** ✅ | **Designed — as [domain/08](domain/08-person-data.md) and [data-model/09](data-model/09-attributes.md)** | **Highest-sensitivity data in the system, and the exposure grew in round 6.** [D-074](decisions/round-06.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular) deleted the codes that used to gate medical visibility, so "read everything except the health file" is no longer sayable — see **E-7**. This raises the case for designing the module **before** the coarse default is relied on, rather than after: separate retention, separate access, likely separate storage, and its own legal review. |
| **Communication** | `message.send_direct`, `message.broadcast` (scoped) — shape decided, detail undesigned | **Shape decided by [D-077](decisions/round-06.md#d-077--messaging-is-direct-by-default-broadcast-is-an-ordinary-scoped-permission-and-the-recipient-chooses-the-channel):** internal first, external channels are delivery; everyone may send direct; `broadcast` is one scoped permission; **the recipient picks the channel.** Needs: templates, opt-out granularity, retention, moderation. The rule against contacting minors directly was **declined as a sender restriction** — see **MSG-1** below. |
| **Reporting** | `report.*` permissions sketched | The historical queries in [domain/05](domain/05-membership-lifecycle.md#8-since-1985--the-ten-queries-this-design-must-answer) are the starting set. Query 10 (members per year since 1985) is the acceptance test. |
| **API and UI** | — | Not started. The resolver's `p_at` parameter exists partly for this. |
| **Notifications** | — | Expiring roles, members inside the renewal window, unpaid fees. Note the renewal window makes this *dated* rather than status-driven — a nightly job over `in_renewal_window()`. |
| **Payment gateway** | — | **Answered, so this row is now narrower than it was.** The organization collects via **bank API**, not a card gateway ([D-075](decisions/round-06.md#d-075--money-arrives-from-a-bank-api-a-payment-is-requested-by-variable-symbol-and-qr-code)): no webhooks, no disputes, no processor reconciliation. What remains undesigned is the **statement import** itself — file formats, the idempotency key, and what happens to an account the bank revises. |
| **Multi-language** | — | Unit names and permission display names are all in the database. Whether they need translation columns is unanswered. |

---

### H-0 ✅ **Closed** — the medical record was cited everywhere and defined nowhere, and it turns out there was nothing to define

**Found while starting the health-records module, and it changes what that module is.** Sentences
across five files discuss who may read *the medical record* as though it were a table:

| Where | What it says |
|---|---|
| §H, this file, Health records row | "a `view` guardian already sees them" |
| [E-7](#e-7--closed--one-level-cannot-separate-the-medical-record-from-the-profile-and-nobody-wanted-to) | "a guardian either sees everything about the child or nothing" |
| [permission-catalog §9](appendix/permission-catalog.md#9-there-is-no-dependent-namespace) | a `view` guardian "reaches the fee history and the health record" |
| [data-model/08 §7](data-model/08-events.md#health-facts-and-the-discipline-this-requires) | "the medical file, which **no event permission reaches**" |
| [data-model/04 §2](data-model/04-relationships.md#2-the-guardians-right-none-view-or-write) | the case the old codes existed for is "access to medical information" |

**No document defines one.** There is no health or medical entity in any
[data-model](data-model/00-conventions.md) file and no box in [the ERD](appendix/erd.md). The only
thing that ever had a medical shape in this model was a `medical_form` **requirement code**, and
[D-044](decisions/round-02-03.md#d-044--nothing-gates-a-membership-request-except-identity-and-payment)
deleted that table. So the referent is a habit of speech inherited from the old
`dependent.medical.*` permission codes, which named a sub-resource of a table that was itself
removed with [D-074](decisions/round-06.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular).

**What this does to the arguments built on it — most of them survive, one does not.**

- **E-7 stands, and is sharper than it looked.** "One right level cannot separate the medical record
  from the profile" is *still true* about a record that does not exist: it says the guardian model has
  no granularity to offer whenever something sensitive is later attached to a person. That is a real
  finding about the model, not about a table.
- **"No event permission reaches the medical record" is true but empty.** Nothing reaches it, because
  nothing is there. The paragraph in 08-events that leans on this to reassure is right about
  permissions and wrong about the risk: **the only health data the system actually holds today is in
  `event_answer.value`** — free text typed into a form, read by whoever runs the event, with no
  retention policy ([EV-2](#ev-2--retention-of-event_answer)). The sensitive data is in the weakest
  place, not the strongest.
- **"A `view` guardian already sees them" is simply false**, and was written as a reason not to design
  the module early. It is replaced by the question below.

**The question, before any field is designed.** *What is a health record in this system?* Not "which
fields" — the shape. Three coherent answers, and they imply different systems:

1. **Structured entries** (allergy, medication, condition, instruction) — queryable, so "who in this
   unit has a nut allergy" is answerable, and the price is that the organization is now a custodian of
   diagnosable data with everything that implies.
2. **Documents only** — a scanned form filed against the person, using the `document` scope that
   already exists in the catalog. Cheap, legally simple, and useless in an emergency, because nobody
   reads a PDF at 23:00 in a tent.
3. **Hybrid** — a small set of structured, actionable entries plus documents behind them for anything
   a form can hold. This is what organizations actually do on paper, and the option the rest of the
   corpus seems to assume.

**Why this is H-0 and not a row in the table.** Every other open question about health — who may read
it, whether the guardian default changes, what event organizers get, how long answers survive,
whether E-7 needs its exception — takes a different answer depending on this one. It is also the only
module whose *absence* is already load-bearing: two documents cite the medical record's protections in
order to argue that something else is safe.

**Answered (round 7), by rejecting the framing.** You answered the three-way question with a fourth
answer: *"I consider everything apart from name, gender and age a 'medical record'. It is fields in
the database, not files."* So the referent was not missing — the **category** was missing, and the
phrase in those five files was groping at a distinction nobody makes: there is no medical record
inside the person record, because the person record is the thing, and it is fields. Recorded as
[D-083](decisions/round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data),
with the shape of the layer in [D-084](decisions/round-07-08.md#d-084--descriptive-data-is-organization-defined-at-runtime)
and the boundary in [D-085](decisions/round-07-08.md#d-085--the-identity-machinery-stays-structured-the-boundary-is-rules-not-sensitivity).
The three options above are recorded nowhere else, which is right: they were the shape of the question,
not the shape of the answer.

**See:** [section Ga](#ga-personal-attributes--designed-with-four-things-left-open),
[data-model/09-attributes.md](data-model/09-attributes.md).

---

### MSG-1 ✅ **Closed** — a direct message to a minor is mirrored to their guardians

**Raised by [D-077](decisions/round-06.md#d-077--messaging-is-direct-by-default-broadcast-is-an-ordinary-scoped-permission-and-the-recipient-chooses-the-channel),
which declined the restriction rather than forgetting it.**

**The situation.** Messaging has two sender tiers — direct, which everyone may do, and `broadcast`,
which is a permission. **Neither tier mentions age.** So any person with an account may send a
private message to any child with an account, and nothing in the model prevents it, records it as
unusual, or tells anyone. This is not a gap created by oversight: the question asked whether staff
may address a child or only their guardians, and the answer replaced it with a model in which
age is not a sender concept at all. **The rule the communication section had promised — "a rule
against contacting minors directly" — is therefore not implemented, and it is worth being blunt
that this is the most consequential unanswered question in the file.**

**Why restricting senders is the wrong fix here.** An age branch in the resolver is what
[D-070](decisions/round-05.md#d-070--an-event-has-no-age-ceiling-the-grant-is-the-rule)
refused for events, on the grounds that a condition evaluated at check time which the capability
model does not know about becomes the first rule in a rule engine nobody wants. It would also be
the kind of restriction that gets loosened the first time it inconveniences a leader, and a
permission that is routinely bypassed on a messaging system is worse than none, because it makes
the bypass normal.

**Recommendation — restrict visibility, not permission.** Mirror direct messages reaching a minor
to that minor's guardians, and make the mirroring visible to the sender. Then:

- nothing is blocked, so the resolver still has no age branch;
- nothing is secretly unread, which is the actual safeguarding property;
- it is built on the guardianship rows the organization already maintains, so it needs no new
  authority concept;
- and it degrades honestly — a child with no guardian on record gets no mirroring, which is the
  same safeguarding gap **check 4** in [data-model/04 §6](data-model/04-relationships.md#6-invariants-to-verify)
  already alerts on, arriving through a second channel.

**The variant to reject.** "Only guardians and unit leaders may message a child." That is the
restriction wearing the visibility recommendation's clothes: it is a sender rule, it needs the age
branch, and it silently tells a child that the adult messaging them has been vetted — which the
model does not establish, and the organization records no background checks
([D-043](decisions/round-02-03.md#d-043--no-background-checks-are-recorded-in-this-system)).

**Answered (round 6): the recommendation is adopted**, as
[D-082](decisions/round-07-08.md#d-082--a-direct-message-to-a-minor-is-mirrored-to-the-minors-guardians)
— mirror to guardians, tell the sender, block nothing. Three details were settled with it, because
"mirror it to the guardians" does not by itself say who the guardians are *to this message*:

- **Which guardians.** Those whose right level is `view` or `write`. A guardian at `none` receives
  nothing: `none` is the organization having already decided that this party sees nothing about the
  child, and a safeguarding rule is not a licence to undo a recorded decision by side effect. **A
  minor whose guardians are all `none` is therefore reported with the minors who have no guardian at
  all** — otherwise the exclusion would be a way to make a child silently unwatched.
- **Which set, as of when.** The guardianships open *at the moment the message is sent*, frozen into
  the delivery. A guardianship closed afterwards does not lose its mirror, and a guardian added later
  does not acquire old threads — same discipline as
  [06-audit §2](data-model/06-audit-and-import.md#2-audit_log), which keeps the
  trail answering "what was true then".
- **Broadcast is not mirrored.** A scoped broadcast is already addressed to a set, recorded, and
  attributable; mirroring exists for the *private* case, which is the one that can be invisible.

**What mirroring is not.** Not approval, not a gate, and not evidence anyone read it. It buys the one
property the safeguarding argument actually needs — **no private conversation about a child is
secretly unread** — without putting an age into the resolver.

**See:** [D-082](decisions/round-07-08.md#d-082--a-direct-message-to-a-minor-is-mirrored-to-the-minors-guardians),
[permission-catalog's `message` row](appendix/permission-catalog.md#10-deferred-namespaces),
[glossary — Mirroring](glossary.md#communication).

---

## R. Resolved — moved to the decision log

Kept here so a reader of this file knows the question was asked and where the answer lives,
rather than finding it silently deleted.

| Was | Question | Settled by | In one line |
|-----|----------|-----------|-------------|
| A-1 | The organizational structure | [D-035](decisions/round-02-03.md#d-035--one-root-unit-all-sub-units-nest-arbitrarily-beneath-it) | One root; all sub-units nest arbitrarily beneath it. |
| A-1 | The unit type vocabulary | [D-054](decisions/round-04.md#d-054--the-sub-unit-vocabulary-is-not-seeded-the-organization-defines-its-own-types) | Not seeded — `org_unit_type` is runtime data; only the root type ships. |
| B-1 | How much legacy data, in what shape? | [D-056](decisions/round-04.md#d-056--the-legacy-import-expects-a-large-corpus-with-legacy-member-numbers) | Large, with legacy member numbers — exact matches, so review is a work queue. **Fully answered in round 8:** thousands of roster rows, no payment data at all, so every historical row is a participation ([D-090](decisions/round-07-08.md#d-090--the-legacy-corpus-is-thousands-of-roster-rows-with-numbers-and-no-money)). |
| D-9 | Is `household` load-bearing at all? | [D-057](decisions/round-04.md#d-057--household-is-removed) | No — removed entirely. Addresses are temporal `person_contact` rows. |
| F-1 | Which permissions and roles does the organization need? | [D-055](decisions/round-04.md#d-055--the-permission-catalog-is-deliberately-comprehensive-and-granular) | The catalog stays large and granular; it is a menu, not a checklist. |
| — | Eligibility for an event — a separate rule engine? | [D-060](decisions/round-05.md#d-060--eligibility-is-capability-there-is-no-separate-rule-engine) | No — eligibility **is** capability. `event.register_self` at `contribute`, via audiences. |
| — | Is `unanswered` a stored attendance value? | [D-059](decisions/round-05.md#d-059--unanswered-is-the-absence-of-a-row-a-registration-stores-two-values) | No — absence of a row. Two stored values: `attending`, `not_attending`. |
| — | Is a weekly meeting an event? | [D-058](decisions/round-05.md#d-058--an-event-is-a-dated-occasion-owned-by-exactly-one-unit) | No — it is `unit_participation`. No recurrence, no series table. |
| — | One owning unit per event, or several? | [D-058](decisions/round-05.md#d-058--an-event-is-a-dated-occasion-owned-by-exactly-one-unit) | Exactly one. A joint camp is one unit's event another unit participates in. |
| — | Are organizers a grant or a roster? | [D-062](decisions/round-05.md#d-062--organizers-are-appointed-on-the-event-not-granted) | A roster on the event — labelled and ordered. Grants stay separate. |
| — | Do unit roles reach the unit's own events? | [D-063](decisions/round-05.md#d-063--an-event-is-an-artifact-of-its-unit-not-a-child-of-it) | Yes — an event is an **artifact** of its unit, not a child. Not inheritance (D-031 stands). |
| — | Does an event have a status (`draft`, `published`)? | [D-064](decisions/round-05.md#d-064--there-is-no-event-status-visibility-is-the-permission-model) | No status column. Visibility **is** the permission model; cancellation is a fact. |
| — | What happens when a full event gets another registration? | [D-065](decisions/round-05.md#d-065--capacity-is-a-waitlist-threshold-and-organizers-may-exceed-it) | Waitlisted for self-service; admitted for organizers; the overrun reported. |
| — | Does paying confirm a place? | [D-066](decisions/round-05.md#d-066--payment-confirms-the-place-and-the-release-deadline-is-the-one-automatic-transition) | Yes when the event has a fee; most events are free and confirm immediately. |
| — | Do organizers record who actually came? | [D-067](decisions/round-05.md#d-067--presence-is-a-three-valued-fact-on-the-registration) | Yes — `was_present`, three-valued. It is the "who was in our care" record. |
| — | May an event form collect medical detail? | [D-061](decisions/round-05.md#d-061--event-answers-are-read-by-that-events-organizers) | Effectively yes: answers are read by that event's organizers, and **no event permission reaches the health record**, so the form is the only route for a camp leader to learn an allergy at all. A recorded widening, restated after D-074 removed the namespace the original wording relied on. |
| A-2 | Permissions conditioned on membership status | [D-039](decisions/round-02-03.md#d-039--member-permissions-require-a-current-paid-membership) | Yes, enforced by the resolver, with guardianship and ownership carved out. |
| A-3 | Activate on payment or on approval? | [D-040](decisions/round-02-03.md#d-040--the-fee-expires-yearly-a-date-tracked-renewal-window-replaces-a-grace-status) | On payment; the fee expires yearly and a dated renewal window replaces a grace status. |
| A-4 | Background checks | [D-043](decisions/round-02-03.md#d-043--no-background-checks-are-recorded-in-this-system) | None are recorded in this system. |
| A-4 | The expiry date | [D-047](decisions/round-04.md#d-047--the-fee-expires-on-1-january) | 1 January; the organizational year runs with the calendar. |
| A-4 | The renewal window length | [D-048](decisions/round-04.md#d-048--the-renewal-window-is-60-days-and-is-a-configuration-parameter) | 60 days, stored as a parameter rather than compiled in. |
| C-1 | May the root read into its sub-units? | [D-049](decisions/round-04.md#d-049--the-root-may-not-read-into-its-sub-units-scope_exposure-is-the-only-crossing) | No. `scope_exposure` is the only crossing; no reporting channel is built. **Formally closed in round 9**, and [D-094](decisions/round-09.md#d-094--the-root-unit-owns-every-imported-event) gave it a mirror: imported events belong to the root, so a unit's own event list contains history it did not run. |
| C-3 | Is a reused unit number the same unit? | [D-096](decisions/round-09.md#d-096--a-reused-unit-number-is-a-new-unit-unless-someone-records-the-continuity) | A **new** unit, unless someone records continuity as `successor_of`. A `code` is a typed label, not an identity. |
| C-4 | Does appointing someone create a role assignment? | [D-091](decisions/round-09.md#d-091--a-permission-group-is-a-rule-and-a-list-at-once-and-a-rule-may-name-another-group), restated by [D-098](decisions/round-10a.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority), [D-100](decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape), [D-101](decisions/round-10b.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree) | No. **Round 10 redrew the line the answer drew:** the union-of-three-arms became an expression language (`+ - *`), a **group** became a hand-stated dated roster, and an **audience** became the rule. Appointing still creates nothing, and there are no positions left to appoint. Rule-filled *roles* went to [F-12](#f-12--closed--may-a-role-be-held-by-a-rule-as-an-audience-is), which round 10 closed **no**. |
| C-5 | What creates the units the import's rows point at? | [D-092](decisions/round-09.md#d-092--the-corpus-is-people-and-events-and-it-names-no-units), [D-093](decisions/round-09.md#d-093--the-one-off-import-may-create-memberships-both-ends-dated), [D-094](decisions/round-09.md#d-094--the-root-unit-owns-every-imported-event) | Nothing, because the rows name no units. People arrive as bounded memberships, events as root-owned events with registrations. **The historical record has no sub-units in it.** |
| C-6 | Should `allows_minors` refuse a minor's position as it refuses their participation? | [D-095](decisions/round-09.md#d-095--units-carry-no-restrictions-joining-one-is-somebody-elses-act) | Neither: units carry no restrictions and the flag is removed. The control is that nobody joins a unit or takes a position themself — a counselor writes the row. |
| D-6 | How may the membership gate be waived? | [D-051](decisions/round-04.md#d-051--the-membership-gate-is-waived-by-a-permission-not-only-by-a-role-flag) | A person-level `system.gate_exempt` permission, in addition to the role flag. |
| D-7 | The root participation row at renewal | [D-050](decisions/round-04.md#d-050--a-renewal-inside-the-window-extends-the-existing-root-participation-row) | Extended across the renewed period; one row, no gap. |
| B-3 (part) | Erasure: what shape? | your answer, round 5 | Redact the person, keep the financial and membership skeleton. **Retention decided in round 8** — the skeleton is kept indefinitely, audit payloads expire ([D-088](decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)); what is left is the legal review of the indefinite half, not the design. | |
| C-1 (largely) | Organization-wide operational roles without downward inheritance | [D-035](decisions/round-02-03.md#d-035--one-root-unit-all-sub-units-nest-arbitrarily-beneath-it) | The problem dissolves: the root owns the registry and the fees. What remains is a reporting question — see C-1. |
| C-2 | May units be reparented retroactively? | [D-036](decisions/round-02-03.md#d-036--units-cannot-be-reparented-a-unit-that-moves-is-a-new-unit) | Not at all — a unit that moves is a new unit. |
| D-1 | Fee per person or per household? | [D-037](decisions/round-02-03.md#d-037--exactly-one-membership-type-the-fee-is-flat-and-per-person) | Per person, flat, yearly. |
| D-2 | One open membership, or several of different types? | [D-037](decisions/round-02-03.md#d-037--exactly-one-membership-type-the-fee-is-flat-and-per-person), [D-041](decisions/round-02-03.md#d-041--belonging-to-a-sub-unit-is-a-participation-record-not-a-membership) | One type, so one open membership, enforced person-wide. |
| D-3 | Age-out timing | [D-038](decisions/round-02-03.md#d-038--membership-is-ageless) | Retired — there is no age-out. |
| D-4 | Child → adult transition | [D-038](decisions/round-02-03.md#d-038--membership-is-ageless) | Retired — there are no membership categories to transition between. |
| D-5 | Membership type vocabulary | [D-037](decisions/round-02-03.md#d-037--exactly-one-membership-type-the-fee-is-flat-and-per-person) | One type, `member`; counselor is a position, not a type. |
| E-1 | Default rights when a guardianship is created | [D-046](decisions/round-02-03.md#d-046--guardianship-defaults-depend-on-how-the-guardianship-was-created) | `write` for a self-registered child's guardian; `view` for staff-created and imported rows; chosen at creation when recorded manually. **D-074 turned the answer from a code bundle into one level**, which is why the decision still stands on its original wording. |
| F-2 | Polymorphic `scope_id` vs a `grantable_item` supertable | your answer, round 6 | Polymorphic — `scope_type` plus `scope_id`, as currently designed. |
| — | The bulk scope-exposure tool | [D-045](decisions/round-02-03.md#d-045--the-bulk-scope-exposure-tool-is-removed) | Removed once audiences existed to cover the case it was for. |
| — | What a membership request must contain | [D-044](decisions/round-02-03.md#d-044--nothing-gates-a-membership-request-except-identity-and-payment) | Identity and the fee. The whole requirement mechanism is gone. |
| — | Whether grants may target groups | [D-042](decisions/round-02-03.md#d-042--grants-may-target-audiences-not-only-individuals) | Yes — built-in rule-evaluated audiences plus admin-managed named groups. |
| E-2 | What happens to guardianship at majority? | [D-069](decisions/round-05.md#d-069--guardianship-ends-when-a-person-ends-it-the-system-takes-no-position-on-majority) | Nothing — no job, no queue, no computed date. A person ends the row. *(Reverses D-024.)* |
| F-3 | Must a high-authority role assignment have an end date? | [D-071](decisions/round-05.md#d-071--nothing-forces-a-role-assignment-to-end-the-gate-and-the-report-are-the-control) | No. The membership gate plus a human review report; the earlier "yes" recommendation is withdrawn. |
| F-4 | Should `person.admin` subsume merge and redact? | [D-068](decisions/round-05.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle) | Moot — there are no per-resource `admin` permissions. The choice moved into reviewable role contents. *(Reverses D-007.)* |
| — | Should every resource expose an `admin` permission? | [D-068](decisions/round-05.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle) | No. Sixteen codes and the resolver's prefix match are gone; roles are the bundle. |
| EV-1 | Does an event need an age ceiling? | [D-070](decisions/round-05.md#d-070--an-event-has-no-age-ceiling-the-grant-is-the-rule) | No. The grant is the rule; a future ceiling would be a built-in audience, not a column. |
| EV-5 | Should `event.manage_participants` split? | this round | Yes — `event.presence.mark` at `contribute`, one level below the roster. **Round 10 note:** the split stands; the level does not ([D-099](decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)). |
| D-8 | Should `unit_participation` reference the membership? | [D-097](decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row) | Retired with the table. The refusal is still live reasoning: participation had to survive without a membership, which is why `person_group_member` is keyed on a person. See [data-model/03 §9](data-model/03-membership.md#9-open-issues). |
| F-12 | May a role be held by a rule, as an audience is? | [D-100](decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape) | **No.** An office is held by a named person and confers nothing; a group is company; a **grant** is what reaches a set. The office record stays the one dated, human-readable answer. |
| — | Is there more than one unit, and does anything belong to it? | [D-097](decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row) | No. `org_unit` and friends, `unit_participation`, `scope_exposure` and the traversal functions are deleted; **the unit is a scope, not a row**. Two-way door: no. |
| — | What is a group? | [D-098](decisions/round-10a.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority) | `person_group`: named, dated, **states its members**, has a lifetime, grants nothing by itself. A group is company; a selector picks people; a grant is what reaches them. |
| — | What does a grant do, and how much? | [D-099](decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality) | Allows **or** denies one permission at one scope, for a period. Allowed iff some live allow applies and no live deny applies. No levels, no rank integer, no locality. |
| — | Is a role a bundle of permissions, and is membership a precondition? | [D-100](decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape) | Neither. `role_assignment` → `role_holder`; `role_permission`, positions and the membership gate are deleted; the test moved into the expression (`MEMBERS * ROLE(x)`). Posture: default-on → **opt-in**. |
| — | How is an audience stored? | [D-101](decisions/round-10b.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree) | As an **expression tree** over named sets — `+ - *`, brackets, fully-bracketed canonical form, cycles refused at save, the language seeded as `selector_type`. Semantic equality given up (see F-14). |
| — | Who owns an event, and whom does a grant about it reach? | [D-102](decisions/round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it) | **Nobody owns it.** `event.org_unit_id`, `can_event()` and the artifact rule are deleted; four attendance tiers and `ORGANIZERS` **bind to the item**, and the answer-view grant is a seeded template instantiated per event. |
| — | May a rule be reused by name? | [D-103](decisions/round-10b.md#d-103--an-audience-may-name-another-audience) | Yes: `AUDIENCE(code)`, referenced by code, one namespace with roles and groups, cycles refused across audiences at save, and an audience named by a live grant may not be ended. Its past reach is not reconstructable (see F-17). **Amended in the same round:** the same refusal now extends to a **group** named by a live grant — see [assumption 63](#i-assumption-index). |
| F-19 | A permission code is a row, prose names codes, and nothing checks the two | [D-104](decisions/round-10b.md#d-104--a-permission-codes-last-segment-is-an-action-and-a-registry-that-prose-contradicts-is-a-fiction) | The class is real — **four instances in ten rounds, in two different registries.** The naming grammar is now three rules (action-final; a middle segment names stored state; no grade words, no prefix) with `system.admin` the single named exception. **The event QR capability never existed**: invented in prose, deleted in prose, no decision entry at either end. The check adopted is a **hand-run diff report** — a convention, not a guard. |

---

## I. Assumption index

Every *Assumption:* in the documentation, so they can be reviewed as a group. Once you confirm
one, it should be promoted to a numbered decision and struck from [§ R](#r-resolved--moved-to-the-decision-log).

Rows marked **†** are now backed by a decision rather than a bare assumption — kept here
because the docs still cite them and because the decision is worth seeing in this list.

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
| 11 | Merge chains are allowed, because reversing a merge has to stay possible (D-087) † | [data-model/01](data-model/01-identity.md#9-views) |
| 12 | Only confirmed payments count toward a balance | [data-model/07](data-model/07-finance.md#3-keeping-membershipoutstanding_balance-honest) |
| ~~13~~ | ~~No sub-unit types are seeded; nesting is permissive by default~~ (D-054) — **deleted, not reversed**: `org_unit_type` and `org_unit_type_rule` went with the hierarchy ([D-097](decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)), so there is nothing left to seed and no nesting to be permissive about. A-1's closure is the decision of record | [data-model/02](data-model/02-organization.md#5-what-this-page-held-before-round-10) |
| 14 | `membership_type` is seeded with exactly one row (D-037) † | [data-model/03](data-model/03-membership.md#8-seed-data) |
| 15 | `person.gender` is needed for reporting | [data-model/01](data-model/01-identity.md#2-person) |
| 16 | Imported rosters end at the organizational year end (D-028) † | [data-model/06](data-model/06-audit-and-import.md#3-import-pipeline) |
| 17 | All business tables are audited | [data-model/06](data-model/06-audit-and-import.md#6-open-issues) |
| 18 | Currency is EUR | [data-model/07](data-model/07-finance.md#2-minimal-provisional-shape) |
| 19 | `access_log` is not human-annotatable | [data-model/05](data-model/05c-access-log-and-resolver.md#9-access_log) |
| ~~20~~ | ~~Each permission has an `admin` sibling~~ — **superseded**: no per-resource wildcard codes (D-068) | throughout |
| 21 | No downward inheritance; ~~exposures are written by the unit~~ (D-031) † — **deprived of its subject, not weakened** ([D-097](decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)): the rule was always about a hierarchy that no longer exists, and what survives is the ordinary reading of a scope — **a grant reaches its scope and nothing beside it** | [domain/06 §2](domain/06-authorization-model.md#2-scopes--the-unit-and-the-item) |
| 22 | The person record holds no deceased flag (D-034) † | [data-model/01](data-model/01-identity.md#2-person) |
| ~~23~~ | ~~Positions are multi-holder unless `max_holders` says otherwise~~ (D-033) — **deleted by D-100** with `position`, `position_assignment`, `is_leadership` and `max_holders`. The vacancy question it answered is now unanswered by construction; see [F-18](#f-18--does-a-role-record-elected-versus-appointed-and-what-does-an-election-write) | [domain/04](domain/04-organization-structure.md) |
| 24 | Membership is ageless — no category, no `min_age`, no `max_age` (D-038) † | [data-model/03](data-model/03-membership.md#1-membership_type--one-row-kept-as-a-table) |
| 25 | A grant targets a person **or** an audience, never both (D-042) † | [data-model/05](data-model/05-authorization.md#6-access_grant--the-per-item-layer) |
| 26 | ~~Built-in audiences are rules evaluated by the resolver, not stored lists~~ (D-042) † — **reversed twice, and the second reversal is the one to keep.** Round 10 found both halves wrong in opposite directions: no built-in audiences (two seeded rows remain, and the rules are the `selector_type` operands), and an audience **does** contain a stored list — its `LIST` leaf ([D-101](decisions/round-10b.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree), [D-103](decisions/round-10b.md#d-103--an-audience-may-name-another-audience)). **Round 11 deleted that leaf** ([D-105](decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)), so an audience stores **an expression and nothing else**: a hand-written set is `PERSON(x)` leaves *inside* the expression — rows of the tree, not rows of a roster, with no dates of their own. **D-042's original half is therefore true of an audience again, and true for a new reason**: the words are what is stored, and the words can happen to name people. (The count this row quoted was stale the moment assumption 58 recorded a thirteenth row arriving, and is twelve again now that `LIST` is gone — **right by subtraction, not by the same fact**.) | [data-model/05](data-model/05a-audience-and-grammar.md#the-selector-registry) |
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
| 42 | Event answers are read by that event's organizers (D-061) † — **still true, and no longer a resolver clause**: it is one seeded grant row (`event.answer.view`, scoped to the event, aimed at `ORGANIZERS`) instantiated per event, which D-102 calls out as the deliberate move from prose to data. **An event created without its grant has organizers who can read nothing** | [data-model/08](data-model/08-events.md#selectors-that-bind-to-an-event) |
| 43 | Organizers are a roster on the event, not grants (D-062) † | [data-model/08](data-model/08-events.md#3-event_organizer) |
| ~~44~~ | ~~An event is an artifact of its unit, so unit roles reach it~~ (D-063) † — **deleted by [D-102](decisions/round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)**, along with `can_event()`. Nothing reaches an event from a unit any more; authority arrives through a grant scoped to the event itself, and the sentence "an event is an artifact, not a child" is withdrawn rather than restated | [domain/07](domain/07-events.md) |
| 45 | There is no event status; visibility is the permission model (D-064) † | [data-model/08](data-model/08-events.md#2-event) |
| 46 | Capacity is a waitlist threshold organizers may exceed (D-065) † | [data-model/08](data-model/08-events.md#5-capacity-and-the-waitlist) |
| 47 | Payment confirms a place; free events confirm immediately (D-066) † | [data-model/08](data-model/08-events.md#6-payments-and-confirmation) |
| 48 | Presence is a three-valued fact, not a boolean (D-067) † | [data-model/08](data-model/08-events.md#4-event_registration) |
| 49 | Keeping named membership and fee rows **indefinitely** after an erasure request has a legal basis (D-088) — **unverified, and commissioning the review is the organization's job** | [data-model/00](data-model/00-conventions.md#8-personal-data-and-erasure) |
| 50 | `access_log` needs the same window as audit payloads, neither longer nor shorter (proposed, **F-8**) | [data-model/05](data-model/05c-access-log-and-resolver.md#9-access_log) |
| 51 | **Audience** membership is recomputed at check time and never stored, so "who could read this in 2023" may be unanswerable once the audit payloads expire (D-091, restated for D-098/D-101) † — **the half of this that used to be true of roles is no longer at risk**: an office is a dated `role_holder` row and a group is a dated roster, both stored, and F-12 closed on exactly that ground. What remains exposed is the expression, and it is now a question with a number: [F-17](#f-17--closed--the-expression-is-the-record-so-a-nested-audiences-past-is-recomputed-and-never-promised) | [data-model/05](data-model/05b-expression-tree.md#three-named-sets-and-the-one-question-nesting-cannot-answer) |
| 52 | The historical record contains no sub-unit participation, because the corpus names no units (D-092) † — **now true for a second, stronger reason**: even if the corpus had named them there would be nowhere to put the answer (D-097). The finding about the *source* is what matters and is unchanged | [data-model/06](data-model/06-audit-and-import.md#31-what-a-source-row-actually-evidences) |
| 53 | An imported membership carries no fee obligation, and its `outstanding_balance` is NULL rather than zero (D-093) † | [data-model/07](data-model/07-finance.md#3-keeping-membershipoutstanding_balance-honest) |
| 54 | A bare name in an expression resolves to a **role or a group only**, never to an audience — and the one-namespace rule across `role`, `person_group` and `audience.code`, with every `selector_type.code` reserved, is carried by the write path with **no constraint spanning three tables** (D-101, D-103) † | [data-model/05](data-model/05b-expression-tree.md#names-are-one-namespace-and-reserved-words-are-the-other-half) |
| 55 | Delegation is a set-membership test, and `role.is_delegatable` does not exist — the model has no column that says an office may delegate (*no decision; domain/06 carries it as an assumption*) | [domain/06](domain/06-authorization-model.md#11-open-issues) |
| 56 | Finding **which grants name an audience, and at what depth**, is cheap enough to show before saving an edit to a referenced audience (D-103) — **stated as an assumption in the decision itself and measured by nobody** | [F-16](#f-16--closed--listing-the-grants-that-name-an-audience-is-a-scan-over-a-small-table-at-the-stated-size) |
| 57 | A grant's scope is the unit **or exactly one item**, so the seeded answer-view grant is a **template instantiated per event** rather than one row for every event (D-102) † | [data-model/08](data-model/08-events.md#selectors-that-bind-to-an-event) |
| 58 | ~~The `PERSON(x)` appearing in D-100's and D-101's worked expressions is **shorthand** for a second grant row, not a missing seeded operand~~ (D-101's registry amendment, class in D-104) **†** — **the opposite: it was seeded** — **as the thirteenth row to arrive** (`takes_argument` true, `argument_type` `person`, `binds_to_item` false), and **today as one of the twelve that remain**, because [D-105](decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other) deleted `LIST` in the round after. The ordinal belongs to round 10 and the count to round 11: **the registry has never held thirteen rows at the same time as it held twelve**, and neither number says anything about how many it holds now. The registry was the side that was wrong. It was written by two decision entries while the seeded table — copied from the evaluator's arm list rather than from D-101's grammar — carried twelve rows without it, so `MEMBERS * ROLE(x) + PERSON(y)` did not parse for a whole round and the wrong repair (`PERSON(y)` read as `LIST`, which subtracts everybody on the list) was already circulating — **a repair that is now impossible to write, the only fix this one got without a decision**. **The assumption this row recorded was the wrong answer, and saying so is the point: the registry was checked against nothing** | [D-101](decisions/round-10b.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree), [F-5](#f-5--closed--nothing-is-missing-from-the-registry-and-the-last-gap-was-a-selector-that-should-not-have-been-in-it) |
| 59 | Two expressions with one meaning are **two audiences**: nothing computes semantic equality, and nothing will (D-101) † | [F-14](#f-14--closed--nothing-computes-semantic-equality-of-two-expressions-and-nothing-will) |
| 60 | An audience preview is **per-item and lazy**, and no screen expands a set for more than one item at a time (consequence of D-102's per-item reached set) — **unmeasured at real event sizes**; **round 14 amended this row without changing the assumption: it adds a dependency.** Nothing pre-pays a preview any more — the nightly job used to warm what a preview reads, and with the answer cache deleted the preview **computes on open** ([D-114](decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation)). Its affordability now rests on the request memo and on `can_many` existing, which these documents can name and cannot enforce | [F-15](#f-15--closed--the-per-item-preview-is-cheap-at-the-stated-size-and-this-is-what-reopens-it) |
| 61 | ~~A cache key is `(person, permission, item)`, and a stale allow is the failure that matters because deny is absolute (D-102, D-099) — **the asymmetric-TTL answer is proposed in [F-6](#f-6--closed--the-permission-cache-is-rebuilt-nightly-on-any-ruleset-write-and-on-request) and decided by nobody** — **round 12 made the key short by one component**: `OLDER(n)` puts the **date being checked** inside the answer with no write behind it, so a key of `(person, permission, item)` can hold an answer from before a birthday unless the cache cannot outlive the day.~~ — **round 14 deleted this row's subject rather than settling it: there is no cache, so there is no key, no TTL and no stale allow** ([D-114](decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation); see also [D-111](decisions/round-13.md#d-111--the-permission-cache-is-rebuilt-nightly-on-any-ruleset-change-and-on-request), whose answer this is). **Two halves of the row outlive the object they were written about, and both turn out to be about meaning rather than storage:** (i) the **item** belongs to whatever a permission predicate is bound to — a compilation carries the item as a *parameter* and holds no item, so nothing resolved while checking one item may be served for another: D-102's finding, surviving the key it was first written into; (ii) the **checked date** belongs inside the answer, which is why a cached roster must hold dated rows or validity ranges and never "today's set". [D-107](decisions/round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)'s acceptance is **discharged, not amended** — under live resolution a birthday moves the answer at the instant it happens, so [F-6](#f-6--closed--the-permission-cache-is-rebuilt-nightly-on-any-ruleset-write-and-on-request) no longer carries a consequence | [D-114](decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation), [data-model/05 §10](data-model/05c-access-log-and-resolver.md#10-the-resolver) |
| 62 | A `person_group_member` row **lies inside its group's own period** — assumed in §2 of [data-model/02](data-model/02-organization.md#2-person_group_member), reported by integrity check 2 as "a list to read rather than a breach", and **ruled nowhere**. Raised by the page's own author as an assumption these documents are standing on | [data-model/02 §8](domain/04-organization-structure.md#8-open-issues) |
| 63 | ~~A **group** may be ended while a live grant or a live expression names it~~ (D-103, amended in the round after the audience row) **†** — **refused at save, in both directions**: ending a group while a live grant, or a live audience reachable from one, names it, **and** writing a new grant onto an already-ended group. The reason is the `-` asymmetry, not the allow side — a live grant on an ended group is safe on the allow side and **widens a deny** on the `-` side, so an ended operand is a way to silently empty a set that was narrowing something. Checked over `audience_operand` rows whose `selector_kind = 'GROUP'`, the same query as the audience rule. **`ROLE(x)` needs no such rule, and the difference is the finding:** an office has no `role.retire`, no status, and deletion is already refused while holder rows exist, so **an office cannot be emptied quietly while a group can be emptied in one click.** The hazard is a property of the shape, not of the idea | [D-103](decisions/round-10b.md#d-103--an-audience-may-name-another-audience), [data-model/02 §8](domain/04-organization-structure.md#8-open-issues) |
| 64 | An operand's set moves **when somebody writes** — twelve rounds of invalidation lists were built on this and none of them said it out loud † — **falsified by design by [D-107](decisions/round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)**: `OLDER(n)` and `YOUNGER(n)` move at midnight, for one person, with no row to change and no event to subscribe to. ~~**Accepted, not fixed** — *"I know, that the time will change, how the rules resolve and IT IS FINE"* — and the residue that survived the ruling is not resolution but **the record**, which is [F-23](#f-23--closed--words-only-the-expression-is-the-record-and-the-preview-is-a-rendering-on-a-date)~~ — **round 14 closed the gap this row accepted, and in doing so found the one in the opposite direction** ([D-114](decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation)). **The calendar case is discharged:** with resolution live and no answer stored, a birthday moves the answer at the instant it happens, so the acceptance has nothing left to accept and its *"IT IS FINE"* stands with no mechanism owed. **The write case was never safe:** the lists assumed a write is what moves a set and then could not say *which* writes — and the boundary D-111 finally drew left out `membership`, whose `membership.terminate` ⛔ is the corpus's most safeguarding-shaped write. **So the corrected form of this row is not "sets move on writes" but "sets move whenever anything they can read changes", which is the read path, not a list** | [F-6](#f-6--closed--the-permission-cache-is-rebuilt-nightly-on-any-ruleset-write-and-on-request), [D-114](decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation) |

---

## How to answer

**The blocking set is still empty, and round 10 is the reason nobody should find that reassuring.** Ten
rounds in, nothing here has to be answered before implementation could start — but round 10 was not a round
that closed questions about the model, it was a round that **redesigned the model**: the unit hierarchy, the
permission levels, positions and the membership gate are gone, and in their place are a group table, an
office table, a grant that allows or denies one thing, and an expression language stored as a tree. That is
[D-097](decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)
through [D-103](decisions/round-10b.md#d-103--an-audience-may-name-another-audience), and it is the
largest change since the documents began. **The blocking set stayed empty because the round's cost went into
questions that were not open before it**, and eight of them are new in this file.

What remains is genuinely deferrable, and the most useful next ones are — **a list that round 13 had to cut
roughly in half, which is worth saying before the list itself is trusted again**:

1. **F-10** — which invariants the ORM cannot express. Round 10 put three new instances into shape 3 and
   emptied shape 4, so the shape list is now the shortest path to everything the write path has to carry: an
   `event` row that obliges a grant row, requiredness conditioned on a value in `selector_type`, a check that
   reads a referenced row, a name namespace across three tables, and exclusion constraints over **all** rows
   rather than open ones. **Round 13 handed it a fifth shape it has never had: an invariant over the
   documents rather than over the data** — ***every selector name that appears in a document must be a
   `selector_type` row, and a check should be able to say so***
   ([D-113](decisions/round-13.md#d-113--the-guardianship-channel-has-no-expression-guardians-is-not-a-selector)'s
   rule, minted when the fourteenth selector turned out to be a prose idiom). It is a lint of prose against a seed
   list, which belongs to [F-19](#f-19--closed--a-permission-code-is-a-row-prose-names-codes-and-nothing-checks-the-two)'s
   machinery rather than to the write path, and it is now the *only* check that would have caught it.
2. **F-18** — does a role record elected versus appointed, and what does an election write? **This is the sole
   survivor of what used to be items 2 through 5 of this list**, and it is here on its own merits, not by
   inheritance: it is a property of the deleted `position` tables that a real elected committee still needs a
   place for.

**What round 13 removed from this list, so the removal is auditable rather than silent.** Four of the nine
items below were closed by [D-109](decisions/round-13.md#d-109--nothing-a-rule-names-is-deleted-deprecated-hidden-disabled--and-a-tab-instead-of-a-report)
through [D-113](decisions/round-13.md#d-113--the-guardianship-channel-has-no-expression-guardians-is-not-a-selector),
and their reasoning lives on in the entries rather than here: **old item 2** was F-17 with F-18 and the
*which-grants-name-this-audience* measurement — F-17 is closed by D-110 (the words are the record), the listing is
closed by D-112 (cheap at the stated size), and **the third protection named there, cache invalidation across the
reference closure, is the one D-111 deleted outright** — **and round 14 deleted the rebuild that deleted it, which
hands that walk back as a bounded job over compilations**
([D-114](decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation),
[§ F-16](#f-16--closed--listing-the-grants-that-name-an-audience-is-a-scan-over-a-small-table-at-the-stated-size));
**old item 3** was F-6, closed by D-111, and the open half it was ranked on — *a stale allow is a permission
already withdrawn* — turned out to be impossible rather than managed, ~~because every withdrawal is a write~~
**because nothing stores the answer** — **the first reason was the one the corpus wrote, and it had `membership`
missing from it; the second is D-114's correction and does not depend on anybody having listed the right tables**;
**old item 4** was F-21 with F-22, closed by D-109 (no report, a
tab) and by an editor ruling (display free, storage fixed); **old item 5** was F-5, closed by D-113 deleting the
last operand it thought was missing. **Note what the pattern is:** four of these did not receive the answer the
entry was built to receive. They were closed by **removing a mechanism** — a report, a per-entry TTL, a history
question, a registry row — which is the move this round made repeatedly and the one a register of open questions
is structurally bad at predicting.
3. **AT-2 / AT-4** — who curates the attribute vocabulary day to day, and whether one
   permission is trusted to guard a trail that holds person data. These are one question seen
   from two ends: the data that lands in the trail arrives through the vocabulary.
4. **EV-2** — how long an event answer is kept once the event it answered is gone, which is a
   sharper question now that the audit payloads which also held those values have a clock on them
   ([B-3](#b-3--closed--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)).
5. **F-19** — the one thing in this file that could be settled this afternoon: **four** times in ten rounds
   prose and a seeded registry disagreed — three about a permission code and the fourth about a *selector* in
   a different registry — and the fix is a script that extracts the code-shaped words from these documents and
   diffs them against the registries in both directions. It costs no schema and would have caught all four,
   including the two the catalog itself wrote. **Round 11 found the same defect in prose rather than in a
   table** — `domain/06`'s own selector list, which had silently kept `LIST` and never gained `PERSON` or
   `AUDIENCE` (F-5 carries the instance) — which is the sharper argument of the two: **a diff of tokens against
   rows catches four of them and misses the copy that is only ever read by a human.** **Round 13 made it five,
   and the fifth is the one that argues for the script hardest**: `GUARDIANS` was a name in six pages of prose with
   a row in the registry behind it that should not have been there, so **both sides of the diff were wrong at once**
   — and unlike the first four, this one was not hand-typed into a screen anywhere, it was a *prose idiom* that
   parsed. D-113's rule (*every selector name in a document must be a `selector_type` row, and a check should be
   able to say so*) is this item, extended from permission codes to selectors, in the round that proved the check
   was needed in the registry's own direction too.
6. **The legal review**, which is not a question this register can answer and now has a concrete
   policy in front of it: named membership and fee rows kept indefinitely, audit payloads kept
   24 months. Assumption 49 is that review's subject — **and since
   [D-093](decisions/round-09.md#d-093--the-one-off-import-may-create-memberships-both-ends-dated) the
   indefinitely-kept population includes thousands of imported people who never used the system**, which is
   the same judgement at a scale the review has not yet been shown.

Everything else can be answered as we go. The schema is built so that most answers change
data rather than structure — which is why the ones above are worth a moment and the rest are
not.

**Answered in round 10:** the organization's *shape*, in the other direction. **F-12 closed no** (D-100) — an
office is held by a named person and confers nothing. And five questions' **subjects were deleted rather than
answered**, which is recorded here rather than quietly erased: the membership gate that D-6 and E-4 were
argued against, the root participation row of D-7 and D-8, the unit types of A-1 and C-1, `scope_exposure`,
positions, and the level ladder that EV-5's answer and A-1's framing both leaned on. **The pattern worth
noticing is not the deletions, it is what happened to the questions**: a question about a mechanism outlives
the mechanism, and the honest options are *restate it against whatever replaced the mechanism* (E-4, F-3,
F-6) or *say that the premise is gone and keep the reasoning* (D-6, D-7, D-8, C-5, C-4). Both were done here,
and neither touches the reasoning that a later round may need. Eight new questions came in, and they are all
consequences of the new machinery rather than new wishes: the listing D-103's protections lean on is unmeasured
(F-17), a preview is now per-item (F-16), a cache key gained the item and a transitive dependency (F-6), an
audience has no past (F-17's neighbour F-18 is the materializing case), and three operands the language wants
do not exist (F-5). **One habit from the round is worth carrying: the entries that survived did it by naming
what enforces a rule now** — D-081's discipline, applied to sections that had been written as if the
hierarchy were permanent. *(One of those four consequences has since lost its subject: the cache key F-6 gained
in this round was deleted whole by* [D-114](decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation) *in
round 14, and the item survived it — not as a key component but as what a resolved predicate is bound to. That
is the pattern above working as intended: the mechanism went, the question about the mechanism stayed, and the
entry is where the difference is written down.)*

**Answered in round 9:** the organization, in whole — groups and their filling rules (C-4, D-091), the
shape of the corpus (C-5, D-092/093/094), who may join a unit and the deletion of `allows_minors`
(C-6, D-095), and what a reused unit number means (C-3, D-096). Two things came out of the round that are
worth more than the questions that were asked. **A rule that lives only as prose in one section is still a
rule**: "audiences do not nest" sat in `data-model/05 §8` for three rounds and quietly cost two grants for
one intention, until an answer asked for the forbidden thing. And **a decision recorded from a description
of the data is only as durable as the description** — D-090's absolute import rule lasted one round because
nobody had read the file, which is why D-092 exists and why the corpus questions are now asked in the
present tense about a real export.

**Answered in round 8:** identity and history, in whole — merge chains and unmerge (B-2, D-087),
the two retention clocks (B-3, D-088), the second account (B-4, D-089), and the shape of the
legacy corpus (B-1, D-090). None of the four changed a table, which is why they were worth holding to
the end: they were questions about the organization rather than about the model, and three of the four
turned out to be answerable simply by looking at what the organization already has — a roster with no
money in it settled a rule that had been written as a default, and a wanted feature settled a trade that
had been written as an assumption.

**Answered in round 4:** the unit type vocabulary (A-1 — not seeded, D-054); the permission
catalog (F-1 — comprehensive and granular on purpose, D-055); the legacy corpus
(B-1 — large, with member numbers, D-056); and `household` (D-9 — removed entirely, D-057).
All four are in [§ R](#r-resolved--moved-to-the-decision-log) with links to the decisions that
settled them.

**Answered in round 3, for reference:** the organizational calendar (A-4 — 1 January, 60
days); the root's read access into sub-units (C-1 — `scope_exposure` only); the membership
gate's waiver (D-6 — a person-level permission, in addition to the role flag); and the root
participation row at renewal (D-7 — extended).
