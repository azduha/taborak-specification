# Decision Log — Refinement round 20 (D-137 … D-149)

> Thirteen open questions answered in one sitting: the attribute vocabulary loses its proposal stage and its queue, `access_log` rows are deleted at 24 months while the audit trail keeps its shape, a delegation is validated once and stands, a display name's drift gets the check it already had, and four words — `WHITELISTED`, a translated label, an expired registration, a notification nobody receives — are refused in writing. Four questions survive the round untouched and a fifth arrives with it; not one of the five is 🟡.

[Refinement round 19 (D-133 … D-136) ←](round-19.md) | [All decisions](index.md)

**What was asked.** Put the open questions, in batches, and write down what came back. Seventeen were on
the page; thirteen were put and answered, and four were left where they are ([A-4's remainder](../open-questions.md#a-4-remainder--the-organizational-calendar),
[E-3](../open-questions.md#e-3--guardian-acting-for-an-adult-child), [F-9](../open-questions.md#f-9--should-membership_type-stay-a-table-with-one-row), [F-11](../open-questions.md#f-11--does-the-identity-reviewer-need-to-read-the-person-record-to-settle-a-claim)) because
answering them needs a document or a lawyer rather than a ruling. **Every 🟡 on that page was answered this
round** — all six of them — which is why the page now reads as a list of things that can be deferred, and why
[§ J](../open-questions.md#f-33) emptied itself and was
deleted the way sections B, C and D were.

**What the round found while answering, which is again the part worth reading.** Four of the thirteen
questions arrived with a premise the corpus had already invalidated, and in one case the premise and the
answer were on opposite sides of a contradiction the corpus was living inside.

- **F-32 was not a choice between two policies; it was a contradiction with one side already implemented.**
  The question asked whether a stale delegation should be *reported* or left invisible, presuming the design
  re-checks it. [domain/06 §9](../domain/06-authorization-model.md#9-delegation) does promise that — "validate
  at grant time **and re-check at use time**" — and
  [05 §6](../data-model/05-authorization.md#6-access_grant--the-per-item-layer) says flatly the opposite:
  "**nothing about the person who lent it is re-validated when a check runs**". [removed-concepts](../appendix/removed-concepts.md)
  records why: the column that made a use-time re-check possible was deleted, "and with it the second half of
  the guard — there is no source row left to re-validate". So two pages promised a thing two other pages say
  cannot happen, and the invariant register said the rule was enforced twice, once of them silently. **The
  ruling picked the side the data model was already on**, which makes this entry a repair with a reason
  attached rather than a change of behaviour.
- **F-28's register row claimed a rule had no report beneath it. The report was already written.**
  [01b §10](../data-model/01b-merges-views-and-checks.md#10-integrity-checks) counts persons whose
  `given_name`/`family_name` differ from the open `person_name` row — the exact check the open question
  offered as "cheap to write" — and closes by saying the check exists and that what is undecided is whether a
  report is the right thing or the copy is the wrong one. Round 18 minted that row beside the inventory, and
  its `**none**` was wrong **in the understating direction**: the table said nothing watches a rule that
  something watches. [Round 19](round-19.md) found a register row claiming more than its page said; this
  round found the mirror image, and [D-129](round-18.md#d-129--where-the-register-and-the-page-disagree-the-page-is-wrong)
  catches both — **a register row is a claim about a page, and `none` is as much a claim as a citation.**
- **AT-2's proposal stage was a third status no decision had granted.**
  [D-084](round-07-08.md#d-084--descriptive-data-is-organization-defined-at-runtime) settled the
  vocabulary in one sentence — "a status of **live or retired**" — and the pages and the inventory carried
  `proposed` anyway, complete with a `proposed_by`, a `proposed_at`, an import fallback that writes it, and
  [an integrity check](../data-model/09-attributes.md#8-integrity-checks) whose whole job is to age it out.
  A mechanism was built for a status that arrived by transcription.
- **E-6's answer had no addressee.** The question's own recommendation asked for a "safeguarding contact" to
  be notified, and no such office exists: `safeguarding_officer` is listed among the worked examples the
  catalog marks as not shipping, and [D-132](round-18.md#d-132--day-one-is-one-account-holding-systemadmin-and-every-role-after-it-is-written-by-the-organization)
  is about to delete the seed that would have offered one. A question that asks "who should be told" cannot be
  answered by naming a person the design does not have, so the answer is the one that needs nobody: the trail
  is the control.
- **One deletion moved ten citations, all of them ordinals.** Deleting
  [09 §8](../data-model/09-attributes.md#8-integrity-checks)'s first check renumbers the six that follow it,
  and ten sentences cite those checks by number: **six inside the page that owns them**, two in the invariant
  register, one in [01b](../data-model/01b-merges-views-and-checks.md#10-integrity-checks) and one in
  [06b §5](../data-model/06b-redaction-and-checks.md#5-integrity-checks). **Two more citations died with the
  thing they pointed at** — both were the curation queue reaching for the age-out check that is now gone. All
  ten were rewritten, and all ten were found **by grepping the number rather than by remembering to look**: a
  checker aimed at the target of `§8 check 4` keeps passing after the list above it shrinks, because the
  target still exists and still says check 4.
  **An ordinal is a pointer that moves when the list above it changes**, which is the same failure this
  corpus keeps hitting from the other end: a checker verifies a target and never a claim, and nothing at all
  verifies a number beside a sentence. **This round counted this list wrong while writing it** — it said seven
  sentences and then named eight — which is why the count here is stated as grepped, not as remembered.

---

## D-137 — A guardian may appoint a guardian, and nobody at the organization is told

**Status:** applied.

**Question.** [E-6](../open-questions.md#e-6) asked what happens when a guardian adds a *second* guardian over
a child. Guardianship is a channel with a `right_level` ([D-113](round-13.md#d-113--the-guardianship-channel-has-no-expression-guardians-is-not-a-selector)),
so the act is inside the model already: a person with `guardianship.assign` writes a row. What was undecided
was whether the organization should *hear about it* — the page offered a notification to a safeguarding
contact, a review queue, or silence, and it recommended the notification.

**Answer.** **Attribution is enough. No notification, no queue, no addressee.** The act is a write, the write
is audited with the actor who made it and the person it was about, and that trail is the whole control.
There is no office to notify and nothing in this design that would receive a notification at all.

**Why the recommended option was the wrong one, not merely the expensive one.** The recommendation named a
"safeguarding contact" as if the design had one. It does not, and it cannot offer one without a grant aimed
at a person or an office somebody writes — which is exactly the machinery
[D-132](round-18.md#d-132--day-one-is-one-account-holding-systemadmin-and-every-role-after-it-is-written-by-the-organization)
is going to delete from the seed. **A notification whose recipient is a row somebody must remember to create
is a control that is off by default and silent about being off**, which is worse than the trail, because the
trail is on whether or not anyone configured it. This is the same reasoning that refused a report for
[F-29](round-19.md#d-133--two-trail-rules-stay-unchecked-and-say-so-out-loud): a guard nobody reads is not a
control, and a guard nobody configures is not one either.

**What this costs, said plainly.** Nothing will ever tell a parent, a second guardian, or an officer that a
third adult was given authority over a child. The answer to "who added this person, and when" is excellent and
the answer to "did anyone think about it" is *the person who did it, alone, at the moment they did it*. The
mitigation that does exist is that `guardianship.assign` is one of the codes this corpus marks ⚠⚠ — the grant
is the rare thing, not the act.

**Changes no table and no column.** The open question's recommendation is deleted with the question; the
`guardianship.assign` row in [catalog-a §5](../appendix/permission-catalog-a-codes.md#5-organization-and-positions)
is unchanged.

**See:** [domain/06 §1](../domain/06-authorization-model.md#1-the-three-channels-of-authority),
[04 §Guardianship](../data-model/04-relationships.md), and
[E-6](../open-questions.md#e-6) in § R.

---

## D-138 — One permission guards the whole audit trail, and the widening is on the record

**Status:** applied.

**Question.** [AT-4](../open-questions.md#at-4) asked whether `audit.view` is enough to guard a trail that
holds person data. The trail's payloads are values a person wrote — an old address, an allergy, a diagnosis —
emptied 24 months later ([D-088](round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short))
but readable in full until then, and they are readable **whether or not the reader may read the person they
describe**. [06 §2.3](../data-model/06-audit-and-import.md#23-history-query) records that a per-entry "could
this reader see this field" check was considered and left unimplemented; [D-133](round-19.md#d-133--two-trail-rules-stay-unchecked-and-say-so-out-loud)
declined to stretch the trail for a report and explicitly did not answer this.

**Answer.** **`audit.view` is the whole gate. One permission, one check, no per-entry filter, now decided
rather than merely unbuilt.** The history view is a person-data surface and is treated as one: the code is
granted rarely, it is marked, and what it opens is the entire trail.

**What was refused, and what the refusal is really buying.** The alternative was a check inside the history
view comparing each entry's subject against the reader's own reach. It would have been *correct* and it would
have been slow in the way D-114 says this system accepts — a check that resolves rather than caches — but it
would also have made the trail's readability depend on the same audience expressions it exists to explain, so
that a rule changed last week would silently rewrite what an officer can read about 2019.
**The trail's value is that it is legible without re-resolving history, and a per-entry check spends exactly
that.** The widening is therefore accepted as a property, stated in the pages that grant the code instead of
being left to be discovered by whoever first opens the screen.

**What this does not do.** It does not widen anything. No behaviour changes: nothing in the corpus has ever
implemented the per-entry check, so this decision turns an omission into a position and pays for it in a
sentence. It is also not the same question as [F-17](../open-questions.md#f-17) — whether "who could read this
in 2023" is reconstructable at all — which stays open.

**Changes no table and no column.**

**See:** [06 §2.3](../data-model/06-audit-and-import.md#23-history-query),
[05c §9](../data-model/05c-access-log-and-resolver.md#9-access_log),
[D-114](round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation),
[D-133](round-19.md#d-133--two-trail-rules-stay-unchecked-and-say-so-out-loud), and
[AT-4](../open-questions.md#at-4) in § R.

---

## D-139 — An event question may bind to a stored value: it prefills as a suggestion and writes back as an answer

**Status:** applied.

**Question.** [AT-1](../open-questions.md#at-1) asked whether an `event_question` may be tied to an
`attribute_definition` code, so that a camp form asking "do you take any medication" and the person's stored
attribute are the same fact twice, or one fact asked twice. Two reasons had kept it open: the form's answer
and the record's value would disagree with no rule saying which wins, and
[00 §4's erasure exception](../data-model/00-conventions.md#4-deletion-policy) had a condition on its face:
"**This exception is safe only while nothing references an attribute row, and nothing does today**", naming
this very binding as the thing that would break it.

**Answer.** **The binding is allowed, in one direction, with both ends named.** A question may hold a
`bound_attribute_code` — nullable, pointing at the **definition**, never at a value row. The form
**prefills** from the person's current value as a suggestion, which the answerer sees and may change; nothing
is hidden from them and nothing is silently copied. On submit, **the answer writes back** to
`person_attribute` as a new value, dated **today**, recorded as written by the person who submitted the form.
The answer stays a row of the event either way; the write-back is a second act, not the same row twice.

**Why the binding does not detonate the rule it was fenced off by.** The condition in §4 protects erasure's
one hard delete: redaction deletes `person_attribute` rows outright, and that delete is invisible only for as
long as nothing points *at those rows*. **A bound question points at the vocabulary, not at a value** — at
`attribute_definition.code`, which is never deleted, is retired instead, and survives the person entirely.
So the reference edge §9 would have to walk does not exist: the question names a code, the value rows under it
come and go with the person, and erasure's delete stays invisible. This is recorded here rather than left as a
lucky consequence, because the next person to design a binding will reach for a value's key; a reference from
an event row to a `person_attribute` **row id** remains exactly as forbidden as §4 says it is.

**Which one wins, and when neither does.** The person record wins as of today, because the write-back is dated
today and the attribute's history is the record of what was believed when. An answer is not corrected when the
record later changes, and the record is not corrected when an old answer said otherwise — **they are two
dated statements of the same fact at two moments, which is the shape this corpus already uses for a name.**
Where the answer contradicts the stored value, the difference is visible on the form (the prefill *shows* the
stored value) and that is the intended repair route: a person who edits the prefill is editing the record.

**What this costs.** A form can now write to the person record, which is a new path into `person_attribute`
and the first place outside the person's own editing where an attribute value arrives without a staff member
in the middle of it. The write goes through the same `person.edit` permission the answering channel already
uses, is audited with the answerer as its actor, and is refused — with the form still saving its answer — when
that write is not permitted, so a form never half-writes a person. And a bound question now cannot be
re-pointed at a different code without noticing that its past answers belong to the old one; they stay what
they were.

**Adds:** one nullable column, `event_question.bound_attribute_code`, **holding an `attribute_definition.code`
by value and not a row id** — which is what keeps [00 §4](../data-model/00-conventions.md#4-deletion-policy)'s
ban on row references intact, and what makes this decision answer a question shape 4 had never been asked.
**Because a code is now referenced, [D-131](round-18.md#d-131--shape-4-is-not-empty-and-a-code-that-is-referenced-may-not-be-renamed)'s
test reaches a vocabulary code for the first time: `attribute_definition.code` joins shape 4.** A definition may
still be retired, and may still be merged — the merge of two codes is exactly the deliberate re-point this entry
already demands, and it carries the bound questions with it rather than orphaning them — but a code with a
question bound to it may no longer be renamed, because a rename would silently re-answer every form that was
asked under the old name. **The register carries the row**
([00a §4](../data-model/00a-invariant-register.md#4-a-value-that-may-never-change-once-set)), and the register
grew from six members to seven the day a form was allowed to point at a word.
**Retires:** assumption 58's half that a form answer never reaches the person record.

**See:** [09 §3](../data-model/09-attributes.md#3-person_attribute--a-value-one-person-has),
[09 §4](../data-model/09-attributes.md#4-who-may-read-and-who-may-write),
[08 §7](../data-model/08-events.md#7-event_question-and-event_answer),
[00 §4](../data-model/00-conventions.md#4-deletion-policy),
[domain/07a §12](../domain/07a-capacity-presence-and-forms.md#12-the-forms-questions-and-answers), and
[AT-1](../open-questions.md#at-1) in § R.

---

## D-140 — Nothing about an event is deleted on a schedule, and erasure empties an answer without deleting it

**Status:** applied.

**Question.** [EV-2](../open-questions.md#ev-2) asked how long an `event_answer` survives its event. Three
pages said answers "end with the event" and none said when, what happens to them, or who does it; the same
question noted that the identical fact recorded as a `person_attribute` is **not** deleted on a schedule at
all, so the freshest copy of a health fact was the weakest-protected one.

**Answer.** **There is no expiry for registrations or answers. Neither ends with its event, and neither ends
on a clock.** They follow the rule the accounting skeleton already follows: the row is a fact about a dated
occasion, and it is kept. **Erasure does reach them, and it empties them:** a redacted person's
`event_answer.value` is set to empty and the row survives, because "they answered that question" and "this is
what they said" are two different facts and only the second one is theirs to withdraw. The rows of
`event_registration` are kept as they are today; a cancelled event already keeps every registration
([08a §8, guard 2](../data-model/08a-event-guards-and-checks.md#8-projections-and-guards)), and a cancelled event with no registrations would be an
event that demonstrably never happened.

**Why this direction and not a schedule.** The question's own sharpest point was the asymmetry: the same
sentence of personal data, kept forever in one table and quietly discarded in another, with the discarded one
being the copy a camp leader actually reads. A schedule would have had to be justified to the person it
deletes from, and "we forget it after N years because that number is defensible" is a weaker answer than "we
keep what happened and we erase what you ask us to". It also would have been the third retention clock in a
system that has deliberately managed with two ([D-088](round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)).

**What "empty the value, keep the row" costs.** An emptied answer still says something — that a question was
asked and answered, by whom, on what date — and that residue is deliberate, the same residue D-088 leaves in
an audit payload. It is also a rule that store has to implement rather than one the schema enforces:
[00 §8](../data-model/00-conventions.md#8-personal-data-and-erasure) now lists `event_answer` beside
`person_attribute` among the places erasure has to reach, and
[06b §5](../data-model/06b-redaction-and-checks.md#5-integrity-checks)'s erasure check counts emptied-value
answers the way it counts surviving names, so an erasure that forgot the event tables stops passing a check.

**Deletes:** the phrase "answers end with the event" wherever it stands as a policy, and `event_answer`'s
open retention item from two open-issue lists. **Changes no table and no column.**

**See:** [08 §7](../data-model/08-events.md#7-event_question-and-event_answer),
[08a §11](../data-model/08a-event-guards-and-checks.md#11-open-issues),
[07a §12](../domain/07a-capacity-presence-and-forms.md#12-the-forms-questions-and-answers),
[00 §8](../data-model/00-conventions.md#8-personal-data-and-erasure),
[D-083](round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data), and
[EV-2](../open-questions.md#ev-2) in § R.

---

## D-141 — A definition is live at the save; the proposal stage, its queue and its check are deleted

**Status:** applied.

**Question.** [AT-2](../open-questions.md#at-2) asked who curates the attribute vocabulary and how long a
proposed definition may sit before somebody rules on it. The pages described a two-stage life: an
`attribute_definition` could be `proposed`, carrying `proposed_by` and `proposed_at`, waiting in a curation
queue for a curator to make it live — and an import column nobody had mapped arrived there by itself, so the
corpus could acquire vocabulary through nobody deciding anything.

**Answer.** **There is no proposal, and every field must be defined beforehand.** `attribute.define` is the
curating permission and a definition **is live at the save**: the same person's write that names a code
publishes it. `status` keeps the two values [D-084](round-07-08.md#d-084--descriptive-data-is-organization-defined-at-runtime)
granted it — `live` and `retired` — and nothing else. `proposed_by` and `proposed_at` are deleted, there is no
review list, no waiting, no age-out, and no curator role: **the permission is the curator.**

**Refused:** a value inventing a code. A person recording a value under `person.edit` cannot create
vocabulary by typing something adjacent to it, and the mechanism that made that possible — writing the
unknown as a `proposed` definition and letting it wait — is gone. **An import column that maps to no defined
attribute is an error at apply time, not a proposal.** A row that would need a new code either has one
already written by someone holding `attribute.define`, or it does not import and the batch says so. That is
the strictest of the options on the question's page and it was chosen for the reason the answer gave: a
vocabulary is the one registry where an unreviewed addition is permanent in effect even if it is deletable in
principle, because every value recorded against a bad code inherits it.

**What this exposes, stated rather than smoothed over.** `attribute.define` is held by nothing at day one —
the seed that would have held it is deleted by
[D-132](round-18.md#d-132--day-one-is-one-account-holding-systemadmin-and-every-role-after-it-is-written-by-the-organization),
and the vocabulary therefore starts empty and stays empty until a person with the code writes it. Day one has
exactly one account, holding `system.admin`, so day one's vocabulary is written by that account; after that,
whoever the organization aims the code at. Two pages had been asserting a "named curator" as a role that
reads what it is given; both are corrected, because a role is an office that confers nothing
([D-100](round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)) and
the only thing here that curates is a permission.

**What a bad code costs now.** It is live the moment it is saved, with no gate in front of it, and the values
recorded against it are real values on real people from that moment. The defence is three things and no more:
saving a definition needs a permission, the trail records every save, and a code can be `retired` — which
keeps its values and stops new ones ([D-109](round-13.md#d-109--nothing-a-rule-names-is-deleted-deprecated-hidden-disabled--and-a-tab-instead-of-a-report)'s
rule for anything a rule names).

**Deletes:** the `proposed` status, `proposed_by`, `proposed_at`, the curation queue, the "Proposed code"
glossary entry, the import's unmapped-column fallback, and
[09 §8 check 1](../data-model/09-attributes.md#8-integrity-checks) — which ages out a status that no longer
exists. **Renumbering** §8's remaining six checks moves six ordinal citations in other pages and four more in
the same page; all ten are recomputed, not remembered. **Changes one table** (`attribute_definition`: one
status value and two columns gone; `event_question` gains [D-139](#d-139--an-event-question-may-bind-to-a-stored-value-it-prefills-as-a-suggestion-and-writes-back-as-an-answer)'s
column in the same round, so the vocabulary and its first consumer move together).

**See:** [09 §2](../data-model/09-attributes.md#2-attribute_definition--the-vocabulary),
[09 §7](../data-model/09-attributes.md#7-the-legacy-import-which-is-where-the-vocabulary-comes-from),
[06a](../data-model/06a-import.md),
[08a §11](../data-model/08a-event-guards-and-checks.md#11-open-issues),
[catalog-b §12](../appendix/permission-catalog-b-roles-and-open-issues.md#12-open-issues),
[D-084](round-07-08.md#d-084--descriptive-data-is-organization-defined-at-runtime), and
[AT-2](../open-questions.md#at-2) in § R.

---

## D-142 — The displayed name stays a copy, and the check that counts its drift is named at last

**Status:** applied.

**Question.** [F-28](../open-questions.md#f-28) asked whether the denormalised `given_name`/`family_name` on
`person` is a copy to keep in step with `person_name`, or a field to delete so that the displayed name is
always read from the history. The register carried the rule "the denormalised name agrees with the name
history" with **no report beneath it at all**.

**Answer.** **The copy stays, and the drift is reported.** `person.given_name`/`family_name` remain, written
in the same transaction that writes the name history, and the check that counts the persons where they have
driven apart is named as the rule's backstop: [01b §10](../data-model/01b-merges-views-and-checks.md#10-integrity-checks)
counts persons whose two columns differ from the `person_name` row with no `valid_to`. **That check already
existed** — see the lede — so what this decision changes is which page admits it.

**Why keep a denormalised copy at all, in a corpus that has deleted several.** Because the name a reader must
be able to print for a person who has never been opened as a record — a roster printed at a door, a label, a
search hit — should not depend on walking a history table to find the open row. The alternative was a view,
and a view is what this design already has: the copy is the *materialised* half of it, and the drift check is
the price of materialising anything, paid in the open. The display rule is unchanged —
`preferred_name ?? given_name`, from [01 §2](../data-model/01-identity.md#2-person).

**What it costs:** a name can be wrong in one place while right in another, and only a report will notice.
That is what a denormalised column is; the design declines to be surprised by it.

**Deletes:** nothing but a sentence in 01b §10 that was still asking the question the check beside it had
answered, and one `**none**` in [00a](../data-model/00a-invariant-register.md) — the second of the seven to
go, and the first that was wrong because it understated what the design already does.

**Changes no table and no column.**

**See:** [01 §2](../data-model/01-identity.md#2-person),
[01b §10](../data-model/01b-merges-views-and-checks.md#10-integrity-checks),
[00a](../data-model/00a-invariant-register.md),
[D-129](round-18.md#d-129--where-the-register-and-the-page-disagree-the-page-is-wrong), and
[F-28](../open-questions.md#f-28) in § R.

---

## D-143 — A delegation is validated once, when it is written, and stands to its own end date

**Status:** applied.

**Question.** [F-32](../open-questions.md#f-32) asked whether a delegation whose delegator has lost the code
should be reported or left invisible, on the understanding that the design re-checks the delegator at use
time, so that a loan stops working the instant it goes stale and the delegatee gets an ordinary denial that
explains nothing.

**Answer.** **The delegator is checked once, at grant time, and never again. No report is written, nothing
cascades, and the delegation stands until its own `valid_to` or a revocation.** "You may not lend more than you
hold" is a set-membership test on the person writing the grant
([domain/06 §9](../domain/06-authorization-model.md#9-delegation)); it is true of the moment it is checked and
it is not a promise about the term. **The check was simplified as well as scoped**: the register's layer
column no longer claims the rule is enforced twice a day, once of them silently.

**Why this is a repair and not a policy choice.** Because the design was already this way and one page had not
noticed — see the lede. [05 §6](../data-model/05-authorization.md#6-access_grant--the-per-item-layer) states
that nothing about the lender is re-validated when a check runs and draws the consequence itself: *that is
why a delegation must expire*. [removed-concepts](../appendix/removed-concepts.md) records that the column
which made the re-check possible is gone with the table it named. **Keeping domain/06's promise would have
been a design change**; deleting it is the cheapest correct answer available, and the user's ruling said to
simplify the check rather than to build it.

**The two bounds that survive, which are what makes this tolerable rather than merely cheap.**
**A delegation must expire** — `valid_to` is required on a delegated grant and
[integrity check 11](../data-model/05d-invariants-and-seed.md#11-invariants-to-verify) reports one that does not — and **`system.admin`
may not be delegated at all**. So the failure this ruling permits has a shape: a person keeps an authority
their lender no longer holds, **for a term somebody fixed in advance and cannot exceed**, and the trail says
who lent it to whom. What it does not permit is a permanent loan of the only code that can restructure the
system.

**What it costs.** A delegate may be doing something they should no longer be able to do, and nothing will
tell anybody until the loan's own date arrives or someone notices and revokes it. The corpus previously
promised the opposite and promised it *silently* — a stale loan would stop with an ordinary denial, indistinguishable
from never having had it, which is the kind of guarantee that reads as safety and is actually a person
wondering why their tool broke. A bound that is visible and ends is a better object than an invisible one that
might never end.

**Deletes:** the use-time half of the delegation rule in [domain/06 §9](../domain/06-authorization-model.md#9-delegation),
the register's second enforcement point for that row, and F-32's report option. **Changes no table and no
column** — and no code, since the resolver never had the second check to remove.

**See:** [domain/06 §9](../domain/06-authorization-model.md#9-delegation),
[05 §6](../data-model/05-authorization.md#6-access_grant--the-per-item-layer),
[05d §11 check 11](../data-model/05d-invariants-and-seed.md#11-invariants-to-verify),
[removed-concepts](../appendix/removed-concepts.md), and
[F-32](../open-questions.md#f-32) in § R.

---

## D-144 — `right_kind` is a note: required by the schema, checked against nothing, and no longer claiming to be checked

**Status:** applied.

**Question.** [F-33](../open-questions.md#f-33) asked whether a permission's `right_kind` has to agree with
what the code says — `event.answer.view` being `view` — or whether it is a description that the row keeps for
its reader. The register carried "a code's `right_kind` matches what the code says" against the save path,
with no report beneath it.

**Answer.** **It stays required and it agrees with nothing.** No constraint, no check, no report. The column
is required because a row in `permission` is read by a person deciding what to grant, and a code whose
declared kind reads oddly is worth noticing **while reading**; not because anything will ever tell anybody.
It is admitted as a note, which is what [catalog-a §8b](../appendix/permission-catalog-a-codes.md) has been
saying all along with its sentence that the marking changes no answer and is filled in because the column is
required.

**Why keep a required column that nothing checks, when deletion was on the table.** Deleting it was the tidy
answer and it was refused, for a reason worth keeping: the code's naming grammar ([D-104](round-10b.md#d-104--a-permission-codes-last-segment-is-an-action-and-a-registry-that-prose-contradicts-is-a-fiction))
is enforced by a hand-run diff, and a second, independently written word for the same fact is where that kind
of drift surfaces in a human reading rather than in a script. **The column's whole job is to be legible.**
The cost is symmetrical and is now stated in the page rather than hidden in a column comment: **a
`right_kind` can contradict its code forever, and only a reader will notice.**

**What this corrected as it went.** The register row is **withdrawn, not repaired** —
[D-129](round-18.md#d-129--where-the-register-and-the-page-disagree-the-page-is-wrong) again, the third row
this register has had to lose. No page enforces the match; no page claims to; the row was a claim about a save
path that has no such rule. **This is the third of the register's eleven `none` rows to be resolved, and the
only one resolved by deletion.**

**Deletes:** one row of [00a](../data-model/00a-invariant-register.md) and one shape-3 rule from its count.
**Changes no table and no column** — `permission.right_kind` remains required exactly as it was.

**See:** [05 §2](../data-model/05-authorization.md#2-permission),
[catalog-a §8b](../appendix/permission-catalog-a-codes.md),
[00a](../data-model/00a-invariant-register.md),
[D-129](round-18.md#d-129--where-the-register-and-the-page-disagree-the-page-is-wrong), and
[F-33](../open-questions.md#f-33) in § R.

---

## D-145 — `access_log` rows are deleted at 24 months, and the job that does it has a name

**Status:** applied.

**Question.** [F-8](../open-questions.md#f-8) asked whether the access trail is bounded at all. The page that
owns the table had already reversed its own original "never deletion" and put forward the same 24 months
`audit_log`'s payloads get — **as a proposal awaiting a person**, saying so in as many words, with rows *kept*
and their state columns emptied. [Assumption 50](../open-questions.md#i-assumption-index) registered the
legal premise under it.

**Answer.** **Confirmed, with the rows going rather than the contents: an `access_log` row older than 24
months is deleted.** `audit_log` is untouched and keeps [D-088](round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)'s
opposite shape — rows for the life of the system, payloads emptied at 24 months. **The two clocks now differ
in kind as well as in length:** one trail shrinks and stays, the other disappears. Monthly partitioning
survives as the mechanism, because dropping a partition is how a row deletion of this size is done without
locking the table.

**The corpus-wide consequence, which is the reason this entry is long.**
[00 §4](../data-model/00-conventions.md#4-deletion-policy) says "Nothing is hard-deleted. There is no
`deleted_at` and no delete for business data," and then names **two** exceptions — a staging truncate and the
delete erasure has to make. **This is the third**, and it is named in §4 rather than excepted in a corner,
because a page that quietly deletes rows while the conventions page promises none is the kind of page that
gets "fixed" back. The exception is narrow in exactly the way §4 wants its exceptions narrow: **it reaches no
business row**, it deletes only `access_log`, only by age, only forward from the write, and it is the third
writer the append-only guard must let through beside erasure and payload reduction. "Append-only" continues to
mean *no application writes or removes these rows*, which is what it always protected.

**What dies with a row.** Everything the row could answer after its 24th month: that a person opened a record,
that a screen was reached, which channel and which grant answered it. `audit_log` answers what was *changed*,
and answers it forever; nothing answers what was *read* beyond two years. The register and the inventory say
so plainly instead of letting the reader infer permanence from the word "trail", and
[05d §11 check 23](../data-model/05d-invariants-and-seed.md#11-invariants-to-verify) — which walks this table's
three keyless columns, with the legal-absence rule beside them — keeps working unchanged, because a deleted
row cannot be an orphan. It also gains nothing: **the age-out gets its own check**, the sibling of the one that
counts audit rows past their window still holding a payload, because
[D-133](round-19.md#d-133--two-trail-rules-stay-unchecked-and-say-so-out-loud)'s reasoning cuts both ways —
a reduction nobody verifies is a reduction that quietly stops happening, and here the failure direction is
*data kept too long*, which is the failure the window exists to prevent.

**Adds:** a **sixth** actor label, `system:log-reduction`, to the fixed vocabulary in
[00 §7a](../data-model/00-conventions.md#7a-what-an-empty-actor-column-means). A job that deletes rows must be
nameable, and an empty actor column that could mean the renewal sweep, the bank pull, the payload reduction or
a migration is not an answer to "who deleted my access history". **Every sentence in the corpus stating that
the list has five labels is corrected to six** — five pages, one of them the register row for
[F-25](../open-questions.md#f-25), which is the live record of that decision and is amended rather than left
to be contradicted.

**Refused:** emptying the rows instead, which the proposal on the page preferred. It is the weaker rule with
the better story — it keeps "the table never loses a row" — and it was declined because a row that says *this
record was read on this date by this person* is itself the personal data the window was asked about, not a
skeleton worth keeping.

**Changes no table and no column.** **Deletes:** the "rows are never deleted" position in three pages, the
proposal framing in two, and assumption 50, which is now a decision.

**See:** [05c §9](../data-model/05c-access-log-and-resolver.md#9-access_log),
[00 §4](../data-model/00-conventions.md#4-deletion-policy),
[00 §7a](../data-model/00-conventions.md#7a-what-an-empty-actor-column-means),
[06b §5](../data-model/06b-redaction-and-checks.md#5-integrity-checks),
[05d §11](../data-model/05d-invariants-and-seed.md#11-invariants-to-verify),
[D-088](round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short),
[D-125](round-17.md#d-125--an-empty-actor-column-is-this-system-acting-on-its-own-and-its-name-comes-from-a-fixed-list),
[D-134](round-19.md#d-134--four-more-polymorphic-columns-get-an-orphan-scan-and-the-audit-row-never), and
[F-8](../open-questions.md#f-8) in § R.

---

## D-146 — An outbound call is a person's act or a job, and nothing about it is designed yet

**Status:** applied.

**Question.** [F-27](../open-questions.md#f-27) asked what happens when this system calls *out* — everything
designed so far is a person calling in, or one of two inbound jobs pulling data — so who is the actor of an
outbound write, and against what is it authorized?

**Answer.** **No outbound integration is designed, and no third kind of actor will be invented when one is.**
An outbound call is either **a person acting** — the actor column holds them, their permission is checked, and
the trail shows them the way every other act shows them — or **this system acting on its own**, which is the
empty actor column and a label from the fixed vocabulary ([D-125](round-17.md#d-125--an-empty-actor-column-is-this-system-acting-on-its-own-and-its-name-comes-from-a-fixed-list)).
There is no service identity, no key acting as a person, no "the integration did it". If a future integration
needs a caller that is not a person and is not this system, that is [D-132](round-18.md#d-132--day-one-is-one-account-holding-systemadmin-and-every-role-after-it-is-written-by-the-organization)'s
successor conversation, not a column added in passing.

**What was refused with it.** An `api_key` acting as its own actor for outbound calls. Keys were given a
careful, narrow shape last round ([D-116](round-16.md#d-116--a-caller-that-is-not-a-person-is-a-registered-key-and-a-key-is-a-third-grantee-kind)):
a key is a caller *into* this system, is never inside an expression, and is refused five codes by equality.
Making the same object mean "the thing we call out to" as well would put the accountability of an outbound
write on a secret instead of on a person or a job, and a secret is exactly the thing that leaks.

**What this costs.** A real integration, when it comes, will have to make one of the two choices explicitly
and will probably find the choice uncomfortable: a person acting means their permission gates a third party's
system, and a job means an empty actor column on a write the organization cannot pin on anybody. **Both are
answerable; neither is answered here**, and the point of deciding now is that the answer must be one of the
two, so the vocabulary of five labels becoming six
([D-145](#d-145--access_log-rows-are-deleted-at-24-months-and-the-job-that-does-it-has-a-name)) is the only
growth this axis gets by accident.

**Changes no table, no column, no code.**

**See:** [00 §7a](../data-model/00-conventions.md#7a-what-an-empty-actor-column-means),
[05e §A key](../data-model/05e-keys-and-callers.md),
[D-125](round-17.md#d-125--an-empty-actor-column-is-this-system-acting-on-its-own-and-its-name-comes-from-a-fixed-list),
[D-116](round-16.md#d-116--a-caller-that-is-not-a-person-is-a-registered-key-and-a-key-is-a-third-grantee-kind),
and [F-27](../open-questions.md#f-27) in § R.

---

## D-147 — Presence stays on the registration: no clock of its own, no permission of its own

**Status:** applied.

**Question.** [EV-4](../open-questions.md#ev-4) asked whether `was_present` — the three-valued mark of who
actually turned up ([D-067](round-05.md#d-067--presence-is-a-three-valued-fact-on-the-registration)) — needs
its own retention rule or its own permission, because "who was in our care on that day" is the sentence a
safeguarding question would be asked with.

**Answer.** **Neither. Presence is a column of a registration and inherits everything a registration is:** the
same retention [D-140](#d-140--nothing-about-an-event-is-deleted-on-a-schedule-and-erasure-empties-an-answer-without-deleting-it)
just settled for registrations, and the same two codes that already reach the roster and the mark. **It is not
a record class and this system does not keep a safeguarding register.** There are no background checks here
([D-043](round-02-03.md#d-043--no-background-checks-are-recorded-in-this-system)) and no medical record
([D-083](round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)); a column with
a special clock and a special permission would be the first wall of an archive this design has refused four
times.

**What stands in its place, since the need is real.** The question "who was there on 14 March" is answered by
a report over registrations — which is why the index behind it exists and why it serves a report and no
selector — and the answer is legible for as long as the registrations are, which is now *indefinitely* rather
than until somebody's retention number. **The protection this column has is that it is boring:** readable only
with the codes that reach the event, erased by nothing except the person's own erasure, which reaches a
registration the way it reaches an answer.

**Refused** both halves — a `presence.retention` shorter than the event's, and a `presence.view` narrower than
the roster's. The second would have been a permission whose whole purpose is to hide a fact from the people
who are asking because they were there.

**Changes no table and no column.**

**See:** [07a §9](../domain/07a-capacity-presence-and-forms.md#9-presence-what-actually-happened),
[08a §11](../data-model/08a-event-guards-and-checks.md#11-open-issues),
[D-067](round-05.md#d-067--presence-is-a-three-valued-fact-on-the-registration),
[D-140](#d-140--nothing-about-an-event-is-deleted-on-a-schedule-and-erasure-empties-an-answer-without-deleting-it),
and [EV-4](../open-questions.md#ev-4) in § R.

---

## D-148 — There is no `WHITELISTED`, and the refusal is written where the tiers are

**Status:** applied.

**Question.** [EV-6](../open-questions.md#ev-6) named the word people reach for: an audience for "the ones we
invited". The language has four attendance tiers and `ORGANIZERS`, and refuses `PRESENT(<event>)` outright
because `was_present` is `NULL` until somebody takes a register — a volunteer's forgotten tick would revoke a
child's own photos. `WHITELISTED` was never seeded, was described as having no stored state to evaluate, and
was asked about in the open questions because the word kept coming up in the corpus as a refusal without a
home: the question's own instruction was that "no `WHITELISTED`" is a sentence that has to exist somewhere, in
the same paragraph that refuses `PRESENT`.

**Answer.** **Refused, in writing, where the tiers are listed.** No `is_whitelisted` column, no fifth tier, no
operand, and no reserved name. **Anyone adding `is_whitelisted` is reimplementing grants badly**, and the
sentence now appears beside the presence refusal in the one place that named a PRESENT refusal without it
([domain/07a §9](../domain/07a-capacity-presence-and-forms.md#9-presence-what-actually-happened)).

**Why the answer is free here, which is worth noticing.** The refusal already existed four times over —
[08a §8](../data-model/08a-event-guards-and-checks.md#8-projections-and-guards),
[domain/07](../domain/07-events.md), [domain/06a §Event sets](../domain/06a-audiences-and-selectors.md),
[05a](../data-model/05a-audience-and-grammar.md) and the catalog all state it, and three of those passages
already pair it with the presence refusal. **The count of refused operands does not move**: `WHITELISTED` is
already one of "three operands not in this table" and of the two event sets refused in domain/06a. What was
missing was a sentence with the word in it in the presence section, and that is a paragraph, not a design.

**The need underneath, which is not denied.** An invited person who has not registered is, at capacity,
`ON_WAITLIST` if they register onto a full event and described by **the absence of a row** if they never
register ([D-059](round-05.md#d-059--unanswered-is-the-absence-of-a-row-a-registration-stores-two-values)) —
and they are *invited* by a grant aimed at them, which is a row that exists and says who. **A tier is a state
of a registration; an invitation is not about a registration at all.** That is the argument the refusal rests
on, and it is why the fifth tier would have cost the meaning of the four that exist: `PLACED` is the capacity
set, so an invited person who registers onto a full event is already misdescribed the moment a whitelist set
is added beside it.

**What this costs:** the same thing every prose refusal costs — **nothing in the database refuses a future
`WHITELISTED` row in `selector_type`**, so an operand with no state behind it is a deployment bug rather than a
type error, exactly as an off-list actor label is. That is D-125's cost again, on the vocabulary side.

**Changes no table and no column.**

**See:** [domain/06a §Event sets](../domain/06a-audiences-and-selectors.md),
[05a](../data-model/05a-audience-and-grammar.md),
[08a §8](../data-model/08a-event-guards-and-checks.md#8-projections-and-guards),
[07a §9](../domain/07a-capacity-presence-and-forms.md#9-presence-what-actually-happened),
[D-102](round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it),
[F-20](../open-questions.md#f-20), and [EV-6](../open-questions.md#ev-6) in § R.

---

## D-149 — Words are stored in one language, and a label is not translated

**Status:** applied.

**Question.** [AT-3](../open-questions.md#at-3) asked whether `attribute_definition` and `attribute_option`
labels need a second language, because a form that asks a question in a language the family reads is the whole
point of a form.

**Answer.** **One language: the one the organization writes in.** No `label_cs`/`label_en` pair, no translation
table, no per-language row, no locale column anywhere in the attribute vocabulary. The vocabulary is the
organization's own words, written at runtime by whoever it hands the curating permission to
([D-084](round-07-08.md#d-084--descriptive-data-is-organization-defined-at-runtime)), and the page that owns the
table describes a `label` in four words: *what a human sees*
([09 §2](../data-model/09-attributes.md#2-attribute_definition--the-vocabulary)). **A label is not a rendering of
something more authoritative underneath it** — and a second language would need one, because a row holding
`label_cs` and `label_en` has to be asked which of the two the record is, and whichever answer is chosen demotes
the other to a translation of it.

**What happens to a translated form, since the need is real.** The people who need another language are served
by the person reading the question aloud or writing it down, which is how a Scout organisation has always done
it, and by an event form's own question text — a question's `text` is free text somebody types in whichever
language the event is run in, and it is not a vocabulary item. **The vocabulary is for the record; the form is
for the conversation**, and only one of the two has to be stable enough to query.

**What this costs:** an imported label arrives in whatever language the paper form was in and stays there,
which makes correcting it a curation act under `attribute.define` — live at the save, per
[D-141](#d-141--a-definition-is-live-at-the-save-the-proposal-stage-its-queue-and-its-check-are-deleted) — and
means an organisation that genuinely runs in two languages will have two codes for one fact, which is a
misery the design does not prevent and does not pretend to.

**Changes no table and no column.**

**See:** [09 §2](../data-model/09-attributes.md#2-attribute_definition--the-vocabulary),
[09 §5](../data-model/09-attributes.md#5-what-this-design-cannot-do),
[D-084](round-07-08.md#d-084--descriptive-data-is-organization-defined-at-runtime), and
[AT-3](../open-questions.md#at-3) in § R.

---

## What the round did not do

- **It did not apply [D-132](round-18.md#d-132--day-one-is-one-account-holding-systemadmin-and-every-role-after-it-is-written-by-the-organization).**
  That sweep — the seeded roles, the seeded audiences, the seeded `event.answer.view` grant, the
  worked-example offices presented as seed, `role.is_system`, `audience.is_system` — is a cleanup with its
  decision already written, and it was deliberately kept out of this round so that thirteen answers and one
  twenty-five-page sweep would not be committed together. It is **round 21** and it is the next thing this
  repository owes itself. [D-141](#d-141--a-definition-is-live-at-the-save-the-proposal-stage-its-queue-and-its-check-are-deleted)
  and [D-143](#d-143--a-delegation-is-validated-once-when-it-is-written-and-stands-to-its-own-end-date) both
  reach across to it, and both are written so that the sweep has to read them rather than the other way round.
- **It did not answer the four that survive,** and did not manufacture answers for them: F-9 and F-11 turn on
  a decision about what a membership type is for, E-3 turns on how this organisation reads its own civil
  code, and A-4's remainder is the calendar. None is 🟡.
- **It did not answer the question it raised — [F-34](../open-questions.md#f-34).**
  [D-141](#d-141--a-definition-is-live-at-the-save-the-proposal-stage-its-queue-and-its-check-are-deleted)
  deleted the proposal stage without noticing that it was also the answer to a scheduling question: the
  vocabulary the legacy import needs has to exist **before** the import applies, because an unmapped column is
  now an error at apply time rather than a row that arrives `proposed` and waits. So several hundred
  definitions must be authored by holders of `attribute.define` in advance, while
  [D-132](round-18.md#d-132--day-one-is-one-account-holding-systemadmin-and-every-role-after-it-is-written-by-the-organization)
  is about to delete the seed that hands that code to anybody. **Who writes them, when, and who holds the code
  afterwards is a real hole with no answer in it yet,** and answering it here would have been a ruling wearing
  a question's clothes — the same mistake this round refused to make about a safeguarding contact. It is
  recorded in [domain/03 §9](../domain/03-identity-and-legacy.md) and in
  [the catalog's open issues](../appendix/permission-catalog-b-roles-and-open-issues.md), and it is 🟢 only
  because the first import is not next week.
- **It did not touch the legal review,** which is the largest unowned risk in this corpus and now has a third
  policy in front of it: named membership and fee rows kept indefinitely, audit payloads emptied at 24 months,
  **and access rows deleted at 24 months** (assumption 49; [D-145](#d-145--access_log-rows-are-deleted-at-24-months-and-the-job-that-does-it-has-a-name)).
  That review is the organisation's job, not a question this register can close.
- **It added no check it could not point at a page.** The check this round adopted — the age-out count over
  `access_log` — is named in [05c §9](../data-model/05c-access-log-and-resolver.md#9-access_log) and given to
  [06b §5](../data-model/06b-redaction-and-checks.md#5-integrity-checks), where the audit sibling already
  lives. The register's `**none**` count goes from seven to **five**, and every one of the five is a rule whose
  answer is "nothing, by decision".

**The gate ran, and it was not free.** `scripts/check-registries.py` finishes this round at **no unbaselined
finding**, and `mkdocs build --clean --strict` is clean with no link reported. Two of this round's edits touch
pages the checker reads — the attribute statuses in [erd-b](../appendix/erd-b-inventory.md) and the label
vocabulary in [00 §7a](../data-model/00-conventions.md#7a-what-an-empty-actor-column-means) — so the run was made
*after* them, not before. **Three findings had to be met, and each was met on the page rather than in the
baseline:** [04 §1](../data-model/04-relationships.md#1-guardianship) had stopped naming
`guardianship.assign` when this round deleted the notification sentence that named it, so the page now names the
code itself, which is the stronger sentence and clears the finding
([D-137](#d-137--a-guardian-may-appoint-a-guardian-and-nobody-at-the-organization-is-told) is an argument about
that one permission); `presence.view`, spelled twice in order to say it does not exist, is the one line this
round added to `scripts/registry-baseline.txt` with its reason beside it; and the third was
the same `presence.view` from the other file. **The habit worth keeping from this:** a refusal is a sentence the
checker cannot tell from a mistake, so the baseline is where a round writes down that it read the sentence and
meant it — and a baseline line without a reason after the `#` is that mechanism failing quietly, not a formality.

**What the link pass swept up on the way, counted as grepped rather than as remembered.** Six of the thirteen
closed questions were cited from elsewhere by their **heading slug** rather than by the short id § R would
later carry, and deleting an entry deletes the slug it derived. **Twenty-six links** had to move: `AT-4` ten,
`AT-2` four, `AT-1` four, `E-6` three, `EV-2` three, `EV-6` two. All twenty-six now point at the short anchors
§ R carries, which is what they should have pointed at when the convention was written. **Two lessons, and the
second is about this paragraph.** First: **a derived slug has to be recomputed, not remembered** — the old
`EV-2` heading was `### EV-2 🟡 Retention of \`event_answer\`` and its slug was
`ev-2--retention-of-event_answer`, with the emoji gone, the backticks gone and the **underscore kept**, which is
three rules in one string and none of them obvious. This entry stated the slug as `ev-2--retention-of-event`,
cut off at the code span, and that was wrong; round 19 wrote the sentence about `<a id>` tags and this round
needed it about inline code. Second: **the first pass said twenty-two and named six questions whose counts did
not add up, and it missed three live links** — [round-07-08](round-07-08.md), [round-19](round-19.md) and
§ R's own `F-29` row all still pointed at `AT-4`'s dead slug, and nothing I ran told me so until
`mkdocs build --strict` printed it as an INFO line beneath a successful build. **A link that resolves to
nothing is reported at the same volume as a file being copied**, and the count that was wrong was the one I had
written down instead of the one I had grepped.
