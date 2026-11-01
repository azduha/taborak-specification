# Domain — Personal Data

What the system knows about a person, why it is all one kind of thing, and what that choice costs.
The tables are in [../data-model/09-attributes.md](../data-model/09-attributes.md); the reasoning is
[D-083](../decisions/round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data),
[D-084](../decisions/round-07-08.md#d-084--descriptive-data-is-organization-defined-at-runtime) and
[D-085](../decisions/round-07-08.md#d-085--the-identity-machinery-stays-structured-the-boundary-is-rules-not-sensitivity).

---

## 1. One class of data, and no privileged corner

**Everything about a person apart from their name, their gender and their age is personal data, stored
in fields rather than files — and it is not different in any way.**

There is no special shelf inside the person record, no code list whose names begin with something
clinical, no access path that exists only for the sensitive part. A drug dosage, a preferred contact
language and a shoe size are the same kind of fact: something the organization wrote down about
somebody, which will be out of date in three years, which nobody could have enumerated when the schema
was designed.

**The consequence is uncomfortable and intended: the permission that reads a person's record now reads
everything in it.** A volunteer with that permission sees the allergy list and the insurance number and
the note about who in the family the child actually lives with. That is what "not different in any way"
means, and it is why the catalog marks reading a person as one of the serious permissions in the system
rather than an ordinary one.

### The three exceptions, and why they are exceptions

Name, gender and age stay structured, in the identity model
([03-identity-and-legacy.md](03-identity-and-legacy.md)). Not because they are less sensitive — a name
is the most persistent piece of data here — but because **they answer a different question**. They are
what a person is called and counted as; everything else is what the organization happens to have
noticed. The three are also the only descriptive facts that have been stable across every system this
organization has used, which is the practical test for whether something earns a column.

**`gender` is the exception whose recorded reason turned out to be false, and the true one is smaller.**
The column exists because Czech inflects a past tense for the sex of the person being talked about: any
sentence the system forms about a person has more than one form and something has to pick one, so the
value set — `male`, `female`, `other`, and the column is required — is **a form of address, not a
category of person** ([D-174](../decisions/round-23.md#d-174--persongender-is-how-the-system-declines-a-verb-and-it-is-required)).
The reason this register carried since the first round, that youth organizations must report the value, is
falsified; no report groups on it and none will be cited for it again. That is also why the column stayed
a column when the alternative was to move it into the vocabulary: anything that renders a sentence about a
person reads it on the least privileged path in the design, and a value in a vocabulary the organization
edits at runtime cannot be required to exist.

The boundary between "identity machinery" and "descriptive data" is drawn by a harsher test than
sensitivity: **a fact keeps its own table when there is a rule about it that an open layer cannot
express.** "Exactly one primary postal contact", "a school id may repeat but a birth number may not",
"one current name" — those rules need a known set of columns, and an open layer's whole value is that it
has none.

---

## 2. The vocabulary is the system

If the organization decides at runtime what it collects, then the *list of things it collects* is the
part of the design that matters. The tables are trivial; the vocabulary is not.

An open vocabulary left open decays the same way every open vocabulary does. Within months there will
be `allergy`, `Allergy`, `alergie`, and `allergies (2)`, each with some of the values, and after that the
layer still stores everything and answers nothing. Three defences, none clever:

- **Codes are compared in normalized form**, so the obvious duplicates are refused rather than filed.
- **Recording a value is open; naming a thing is not.** Anyone who can edit a person can write down
  what the doctor said tonight. Creating a code — deciding that this is now a thing the organization
  knows about people — takes a permission and a person who reads what they are given.
- **An improvised need has somewhere to go, and it is not a queue — and now it has nowhere else.** The
  failure this is aimed at is specific and familiar: at 23:00 on a Friday, there is no field for "carries
  an adrenaline auto-injector". Until this round there was still a box the leader could type into — the
  free-text `notes` column on `person` — and it is deleted: **there is no longer a place on the person
  record to write what the vocabulary has no code for**
  ([D-191](../decisions/round-23.md#d-191--personnotes-is-deleted-and-the-vocabulary-takes-the-job)).
  The typed sentence now goes to paper or a phone call rather than to a column nobody reads, and the box
  had been the worse option all along: invisible to any report on a code, invisible to the screen the
  first aider reads, and — kept off the redactor's list — invisible to an erasure too.
  **The answer is blunter than the proposal stage it replaced:** naming the code is the act of whoever holds
  `attribute.define`, and it is live the moment they save it — **the permission is the curator**, and a person
  holding a permission is faster than a review list
  ([D-141](../decisions/round-20.md#d-141--a-definition-is-live-at-the-save-the-proposal-stage-its-queue-and-its-check-are-deleted)).
  **The leader at 23:00 does not hold it, and this design no longer pretends otherwise**; what it keeps is
  that a value recorded against a code *does* exist and reaches the screen that gets read at 23:00
  ([../data-model/09-attributes.md §4](../data-model/09-attributes.md#4-who-may-read-and-who-may-write)).

**Curation is a job, and the documents say so rather than assuming it happens.** The queue that used to make
the job visible is gone, and with it the age signal that said nobody had read the vocabulary in a month. What
carries it now is narrower: `attribute.define` is held by few people, **every definition they save is live at
once with nobody between the save and the record**, and the report that notices a vocabulary rotting is the one
that lists a live code whose values contradict its type, a live code nobody ever used, and two codes close
enough to be the same thing
([../data-model/09-attributes.md §8](../data-model/09-attributes.md#8-integrity-checks)).

---

## 3. Who needs to know what

| Who | What they need | What the design gives them |
|---|---|---|
| **A leader** | The allergies and instructions for the children they lead, tonight, without asking permission | **Whatever the organization has granted them, and nothing more** — with the cost attached: there is no scope smaller than *the whole organization* except a single item, so "the children in their unit" has no scope to be granted *as such*. A `person.view` at unit scope hands over **every member's entire record, allergy lists included**; the narrower thing a leader actually wanted is a group roster or an event. The starting grant set gives leadership rosters and events but **not** a read over the person record |
| **A guardian** | Everything about their child, or nothing, depending on what the organization decided | The guardian right level — `none`, `view`, `write` — over the whole record ([D-074](../decisions/round-06.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular)) |
| **The person themselves** | Their own data | Their own record, which is not a special case in the resolver — "about you" is already a channel |
| **An event organizer** | What matters on the day, for the people who registered | The registration, and the event form that asks. Where the organization already recorded a fact, **the form prefills it as a suggestion the answerer confirms or edits, and confirming writes a fresh value back dated today** — the question binds to the definition and never to a stored row ([D-139](../decisions/round-20.md#d-139--an-event-question-may-bind-to-a-stored-value-it-prefills-as-a-suggestion-and-writes-back-as-an-answer), [AT-1](../open-questions.md#at-1)) |
| **A first aider at a camp** | The short list: what is this child allergic to, what do they take, what should we do | The values are fields, so a list can be produced — which is the argument for fields over documents |

**Read the leader row twice: it is the sharpest edge in this module.** There is no privileged subset of
the record to be kept away from anybody, so nothing in the model can promise that a leader cannot read a
child's data. What carries the protection is that **no leadership role written from the worked examples
carries a read over the record, because leadership is not guardianship** — and an office confers nothing at
all
([D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)),
so the only thing that could give a leader that read is a grant, written somewhere, naming them. The
organization may hand it over deliberately, in one grant, and see exactly what that exposes.
([permission-catalog §11 note 3](../appendix/permission-catalog-b-roles-and-open-issues.md#11-roles--worked-examples-of-writing-one))

The last row is the one that justifies the whole shape. A scanned form in a drawer is a legally tidy
answer and a useless one at 23:00 in a tent; the fact has to be something a screen can show somebody who
is not thinking clearly.

---

## 4. What was refused, and what it cost

**One level cannot separate the medical record from the profile.** The design therefore cannot say
*"everything except the diagnoses"*, which is the shape an arrangement a court might order takes. It
expresses such a case as a guardian who either has the record or does not, and somebody will have to
explain the difference to a parent. The model **fails visibly** — one decision, in one place, audited —
where a capability list fails quietly, because a list of eighteen ticks nobody read is not a safeguard,
it is a receipt. If the case arrives in reality, the route back is **one new grant scope over a defined
set of data, argued once as a decision**, and not a fresh namespace of suggestive permission names.
Why: [D-074](../decisions/round-06.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular),
[D-083](../decisions/round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data).

**There is no per-field type wall.** A field declared as a date warns when someone types `2019`, and
lets them save it. A wall is the wrong tool precisely where the true value is imprecise and the
imprecise answer beats none: *probably allergic to wasp stings, mother thinks it was only once* is a fact
worth keeping, and a validation error would discard it in favor of an empty field.

**No history on the row, and no long history anywhere.** Values are overwritten and the audit trail holds
the sequence — the values themselves, not a note that something changed, since a trail that will not say
*what* changed cannot serve as a history. Elsewhere the model keeps history in business tables when "what
was it on that date?" is routine; guardianship is the standing example. Here it is not routine, it is what
someone asks during an incident. So the history of a child's allergy list lives in the one control these
documents elsewhere admit is discipline rather than guarantee
([D-081](../decisions/round-06.md#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now)),
**in two dependencies, not one: somebody has to write the audit row, on every path including the ones
nobody thinks of, and somebody has to keep the trail guarded as the copy of the whole person record that
it is.** On top of that, the trail's values are emptied 24 months after they were written, though the
rows remain
([D-088](../decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)):
two years of a child's changing facts are recoverable, and what the organization believed in 2019 is not
recoverable at all. That is a real risk, accepted in the open; the entry to reverse if the long version is
ever genuinely needed is [D-085](../decisions/round-07-08.md#d-085--the-identity-machinery-stays-structured-the-boundary-is-rules-not-sensitivity),
not a longer trail.

---

## 5. Forgetting

Two operations that look alike and must not be confused.

- **Retiring a thing the organization collects** keeps what was collected. The label leaves the form;
  the values stay readable and reportable, and the label can come back. Deleting a name must not delete
  nine years of facts, or nobody will ever retire a badly-named thing and the list will only ever grow.
- **Erasing a person** deletes what was collected, everywhere, including in the trail's payloads. The
  organization keeps that it held a record and that it was removed — and not what the record said.
  **Two things now qualify that "everywhere", and both are decisions rather than gaps.** Erasure **empties**
  free text that sits beside a row the organization keeps and lets the row stand: an event answer's `value`
  ([D-140](../decisions/round-20.md#d-140--nothing-about-an-event-is-deleted-on-a-schedule-and-erasure-empties-an-answer-without-deleting-it)),
  and since [round 25](../decisions/round-25.md) the `notes` of a membership, of a membership request and of
  a payment ([D-215](../decisions/round-25.md#d-215--the-three-notes-columns-stay-and-erasure-empties-them)) —
  the fee, the ask and the membership survive, the remark on them does not. And **one body of text stands
  outside erasure altogether**: a message, its body and the rows recording whom it reached are neither emptied
  nor deleted, on the ground that a message is correspondence — an act this organization performed on a date —
  while the argument that once deleted `person.notes` applies to it word for word and **was put and refused**
  ([D-211](../decisions/round-25.md#d-211--nothing-about-a-message-ages-out-and-erasure-does-not-reach-messages)).
  [../data-model/06b §4](../data-model/06b-redaction-and-checks.md#4-redaction-log) holds the whole list, with
  the columns that are still only questioned named there too.

**The audit trail carries these values, in the clear, because it is the only place they have a
history.** What changed is not what the trail holds but who may read it: an entry about a person is as
sensitive as the person data it quotes, so the permission that opens the trail sits with the serious
permissions rather than among the administrative ones
([permission-catalog §8](../appendix/permission-catalog-a-codes.md#8-audit-and-system)). There is no list of
sensitive *field names* the trail scrubs, and there must not be one: such a list is only as good as
somebody having predicted the name of every field that would matter, and this organization invents those
names at runtime. **The protection is the guard** — one line in one table of one appendix, and the
documents say so where they describe it
([../data-model/09-attributes.md §6](../data-model/09-attributes.md#6-erasure-retirement-and-the-audit-payload)).

**What erasure does is absolute in a way the guard is not.** It deletes the values and reaches into the
trail to delete them again from copies written years earlier, lawfully, when nobody was asking questions
about them.

**A third way values leave the trail, and it is a policy rather than a right.** Every two years' worth of
audit rows have their contents emptied whether anybody asked or not
([D-088](../decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)).
The distinction from erasure is worth holding onto, because the two are easy to conflate and only one of
them is a person's entitlement: erasure is *requested* and *verifiable* — the check is that nothing
survives — while expiry is neither requested nor satisfied by nothing surviving, since the row itself
remains and only its values go. **So its failure mode is the opposite one: it fails by not happening.**
That is why it is a scheduled job with a check that reports an over-age row still holding content, and
not a line in a policy document
([data-model/06 §2.2](../data-model/06-audit-and-import.md#22-redaction-before-logging) keeps that apart
from redaction, which must never be deferred). It is also why the sentence *the trail is a second copy of
the person record* — the sentence that decides who may read it — is true for two years and untrue
afterwards. **No clock of that kind runs on a message.** The two that run are this one — a trail's values
emptied 24 months after they were written — and the access trail's own rows, which are **deleted** at 24
months ([D-145](../decisions/round-20.md#d-145--access_log-rows-are-deleted-at-24-months-and-the-job-that-does-it-has-a-name));
nothing about a message is scheduled away, and erasure does not reach it either
([D-211](../decisions/round-25.md#d-211--nothing-about-a-message-ages-out-and-erasure-does-not-reach-messages)).
What makes keeping text survivable is that a message is never edited — a body written is a body kept — so a
design that keeps it forever is not also a design that rewrites it
([../data-model/10-messaging.md](../data-model/10-messaging.md#3-message--one-author-one-target-and-no-second-version)).

---

## 6. Where each part is described

- Tables, rules, permissions and integrity checks —
  [../data-model/09-attributes.md](../data-model/09-attributes.md)
- Identity: the three exceptions and their rules —
  [../domain/03-identity-and-legacy.md](03-identity-and-legacy.md),
  [../data-model/01-identity.md](../data-model/01-identity.md)
- Who may ask, and how the answer is reached —
  [../domain/06-authorization-model.md](06-authorization-model.md),
  [../data-model/05-authorization.md](../data-model/05-authorization.md)
- Erasure and the audit payload —
  [../data-model/00-conventions.md §8](../data-model/00-conventions.md#8-personal-data-and-erasure),
  [../data-model/06-audit-and-import.md](../data-model/06-audit-and-import.md)
- What the organization starts collecting — nothing is seeded. The vocabulary arrives with the
  legacy import
  ([../data-model/09-attributes.md §7](../data-model/09-attributes.md#7-the-legacy-import-which-is-where-the-vocabulary-comes-from)).

---

*Decisions behind this page: D-074, D-081, D-083, D-084, D-085, D-088, D-097, D-100, D-174, D-191, D-211, D-215.*
