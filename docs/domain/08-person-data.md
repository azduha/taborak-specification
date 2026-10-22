# Domain — Personal Data

What the system knows about a person, why it is all one kind of thing, and what that choice costs.
The tables are in [../data-model/09-attributes.md](../data-model/09-attributes.md); the reasoning is
[D-083](../decisions/decision-log.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data),
[D-084](../decisions/decision-log.md#d-084--descriptive-data-is-organization-defined-at-runtime) and
[D-085](../decisions/decision-log.md#d-085--the-identity-machinery-stays-structured-the-boundary-is-rules-not-sensitivity).

This module began as "design the health records module". It ended as this, because the first
question — what is a health record here — turned out to have a much larger answer than the one the
question was expecting.

---

## 1. One class of data, and no privileged corner

Asked how to protect medical data, the answer given was that **everything about a person apart from
their name, their gender and their age is medical data, stored in fields rather than files — and
that medical data is not different in any way.**

Read as a scoping decision it removes the category the module was supposed to be about. There is no
special shelf inside the person record, no code list whose names begin with something clinical, no
access path that exists only for the sensitive part. A drug dosage, a preferred contact language and
a shoe size are the same kind of fact: something the organization wrote down about somebody, which
will be out of date in three years, which nobody could have enumerated when the schema was designed.

**The consequence is uncomfortable and intended: the permission that reads a person's record now
reads everything in it.** A volunteer with that permission sees the allergy list and the insurance
number and the note about who in the family the child actually lives with. That is not an accident
of implementation, it is what "not different in any way" means, and it is why the catalog marks
reading a person as one of the serious permissions in the system rather than an ordinary one.

### The three exceptions, and why they are exceptions

Name, gender and age stay structured, in the identity model
([../domain/03-identity-and-legacy.md](03-identity-and-legacy.md)). Not because they are less
sensitive — a name is the most persistent piece of data here — but because **they answer a different
question**. They are what a person is called and counted as; everything else is what the organization
happens to have noticed. The three are also the only descriptive facts that have been stable across
every system this organization has used, which is the practical test for whether something earns a
column.

The boundary between "identity machinery" and "descriptive data" is drawn by a harsher test than
sensitivity, and it is worth stating plainly because it is the test a reviewer will want to argue
with: **a fact keeps its own table when there is a rule about it that an open layer cannot express.**
"Exactly one primary postal contact", "a school id may repeat but a birth number may not", "one
current name" — those rules need a known set of columns, and an open layer's whole value is that it
has none.

---

## 2. The vocabulary is the system

If the organization decides at runtime what it collects, then the *list of things it collects* is the
part of the design that matters. The tables are trivial; the vocabulary is not.

An open vocabulary left open decays the same way every open vocabulary does. Within months there will
be `allergy`, `Allergy`, `alergie`, and `allergies (2)`, each with some of the values, and after that
the layer still stores everything and answers nothing — which is the single thing an attribute layer
exists to avoid. Three defences, none clever:

- **Codes are compared in normalized form**, so the obvious duplicates are refused rather than filed.
- **Recording a value is open; naming a thing is not.** Anyone who can edit a person can write down
  what the doctor said tonight. Creating a code — deciding that this is now a thing the organization
  knows about people — takes a permission and a person who reads what they are given.
- **An improvised need becomes a proposal, not a workaround.** The failure this is aimed at is
  specific and familiar: at 23:00 on a Friday, there is no field for "carries an adrenaline
  auto-injector", so the leader types it into a notes box, and it is never read by anyone again. A
  proposal is visible, queued and curable; a notes box is neither.

**Curation is a job, and the documents say so rather than assuming it happens.** An unwatched proposal
queue is the same information loss arriving slowly instead of all at once
([../data-model/09-attributes.md §8](../data-model/09-attributes.md#8-integrity-checks)).

---

## 3. Who needs to know what

| Who | What they need | What the design gives them |
|---|---|---|
| **A unit leader** | The allergies and instructions for the children in their unit, tonight, without asking permission | **Whatever the organization has granted them, and nothing more.** The starting role set gives a leader their unit's roster and events but **not** a read over the child's record — that is a deliberate choice about a role, not a wall in the model, and granting `person.view` on the unit hands over the entire record including the allergy list. See the paragraph below the table |
| **A guardian** | Everything about their child, or nothing, depending on what the organization decided | The guardian right level — `none`, `view`, `write` — over the whole record ([D-074](../decisions/decision-log.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular)) |
| **The person themselves** | Their own data | Their own record, which is not a special case in the resolver — "about you" is already a channel |
| **An event organizer** | What matters on the day, for the people who registered | The registration, and the event form that asks. Where the organization already recorded a fact, [AT-1](../open-questions.md#at-1--should-an-event-question-bind-to-an-attribute-code) asks whether the form should prefill from it rather than re-asking every camper every season |
| **A first aider at a camp** | The short list: what is this child allergic to, what do they take, what should we do | The values are fields, so a list can be produced. This is the argument for fields over documents, and it is the reason "files" was rejected in the answer that started this module |

**The leader row carries the sharpest edge in this module, and it should be read twice.** Before
round 7 the corpus asserted that a leader *cannot* reach a child's medical information — which was
argued from a namespace that no longer exists, then from the absence of an `event.*` code, and is now
simply not a property of the model: **there is no privileged subset to be kept away from anybody.**
What remains is the same decision wearing its honest clothes — **the starting roles do not give
leadership a read over the record, because leadership is not guardianship** — plus the fact that the
organization may hand it over deliberately, in one grant, and see exactly what that exposes. That is
a better position than a guarantee nobody could have configured away, and a worse one than the
documents used to claim
([permission-catalog §11 note 3](../appendix/permission-catalog.md#11-roles--proposed-seed-set)).

The last row is the one that justifies the whole shape. A scanned form in a drawer is a legally tidy
answer and a useless one at 23:00 in a tent; the fact has to be something a screen can show somebody
who is not thinking clearly.

---

## 4. What was refused, and what it cost

**The granular medical file, refused on the merits.** Every previous design of this system carried a
way to restrict one person's access to the medical part of a child's record while leaving the rest.
Its justification was always a story about a court order. That story was put to you directly and
declined: *a guardian's rights are what the guardian's permission says; medical data is not different*
([E-7, closed](../open-questions.md#e-7--closed--one-level-cannot-separate-the-medical-record-from-the-profile-and-nobody-wanted-to)).

**What is genuinely lost.** A system that cannot say *"everything except the diagnoses"* cannot
express an arrangement a court might actually order. It will instead express it as a guardian who
either has the record or does not, and somebody will have to explain the difference to a parent. The
trade made is that the current model **fails visibly** — one decision, in one place, audited — while
the granular model fails quietly, because a list of eighteen ticks nobody read is not a safeguard, it
is a receipt. If the case ever arrives in reality, the route back is **one new grant scope over a
defined set of data, argued once as a decision**, and not a fresh namespace of suggestive permission
names.

**The per-field type wall, refused deliberately.** A field declared as a date warns when someone
types `2019`, and lets them save it. The wall is the wrong tool precisely in the cases that matter
most to health data, where the true value is imprecise and the imprecise answer is better than no
answer: *probably allergic to wasp stings, mother thinks it was only once* is a fact worth keeping, and
a validation error would discard it in favor of an empty field.

**The narrow one: no history on the row.** Values are overwritten and the audit trail holds the
sequence — holds the values themselves, not a note that something changed, since a trail that will not
say what changed cannot serve as a history and the trade below would be a lie. Elsewhere the model
keeps history in business tables when the question "what was it on that date?" is routine — guardianship
is the standing example. Here it is not routine; it is what someone asks during an incident. So the
history of a child's allergy list lives in the one control these documents elsewhere admit is now
discipline rather than guarantee
([D-081](../decisions/decision-log.md#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now)),
**and it lives there in two dependencies, not one: somebody has to write the audit row, on every path
including the ones nobody thinks of, and somebody has to keep the trail guarded as the copy of the whole
person record that it is.**
That is a real risk, accepted in the open rather than discovered later, and
[D-085](../decisions/decision-log.md#d-085--the-identity-machinery-stays-structured-the-boundary-is-rules-not-sensitivity)
is the entry to reverse if it ever bites.

---

## 5. Forgetting

Two operations that look alike and must not be confused.

- **Retiring a thing the organization collects** keeps what was collected. The label leaves the form;
  the values stay readable and reportable, and the label can come back. Deleting a name must not
  delete nine years of facts, or nobody will ever retire a badly-named thing and the list will only
  ever grow.
- **Erasing a person** deletes what was collected, everywhere, including in the trail's payloads.
  The organization keeps that it held a record and that it was removed — and not what the record
  said.

Between them sits the rule that changed twice in one round, and the second change is the one to keep.

**The audit trail carries these values, in the clear, because it is the only place they have a
history.** What changed is not what the trail holds but who may read it: an entry about a person is as
sensitive as the person data it quotes, so the permission that opens the trail sits with the serious
permissions rather than among the administrative ones
([permission-catalog §8](../appendix/permission-catalog.md#8-audit-and-system)). The trail used to
scrub a list of sensitive *field names*, which made sense while there was a sensitive subset and became
incoherent the moment there was not — a list of names is only as good as somebody having predicted the
name of every field that would matter, and this organization invents those names at runtime. **An
interim draft of these documents responded by refusing to log descriptive values at all, and that was
withdrawn**: it put medical-shaped fields in a stricter class than a change of address, which is the
privileged corner this module exists to have deleted, and it left the history empty, which is the thing
[D-085](../decisions/decision-log.md#d-085--the-identity-machinery-stays-structured-the-boundary-is-rules-not-sensitivity)
was chosen for. The protection is the guard. It is one line in one table of one appendix, and the
documents say so where they describe it ([../data-model/09-attributes.md §6](../data-model/09-attributes.md#6-erasure-retirement-and-the-audit-payload)).

**What erasure does is absolute in a way the guard is not.** It deletes the values and reaches into the
trail to delete them again from copies written years earlier, lawfully, when nobody was asking questions
about them.

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
