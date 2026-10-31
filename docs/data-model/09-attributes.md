# Data Model — Personal Attributes

The layer every fact about a person lives in, once you subtract what they are *called* and
*counted as*. Written because [D-083](../decisions/round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)
removed the category this file might otherwise have been built around — a privileged medical
record — and [D-084](../decisions/round-07-08.md#d-084--descriptive-data-is-organization-defined-at-runtime)
put an organization-maintained vocabulary in its place.

**Read [domain/08-person-data.md](../domain/08-person-data.md) first** if the word "attribute"
makes this look like a dumping ground. It is the opposite: a layer with a defined boundary, a
curated vocabulary, and an explicit list of what it cannot do.

---

## 1. The sentence, and the boundary it draws

**Everything the system knows about a person other than their name, their gender and their age
is descriptive data of one class, held in fields, whose meaning the organization defines at
runtime.** Not files. Not a per-domain table each with its own permission codes. One kind of data,
one kind of access, one vocabulary.

That sentence is a scope claim inherited almost verbatim from the answer that produced
[D-083](../decisions/round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data),
and it is deliberately wider than "health data". A drug dosage and a shoe size are the same kind of
object: something the organization recorded about a person, which will be wrong in three years,
which nobody can enumerate in advance.

**The boundary is drawn by rules, not by sensitivity.**

| Stays structured, in its own table | Becomes an attribute |
|---|---|
| `person_name` history, `gender`, `birth_date` + `birth_date_precision` — [01-identity §2–3](01-identity.md#2-person) | Health: allergies, medication, conditions, instructions, checkups |
| `person_contact` — purpose, primary flag, validity — [01a §6](01a-accounts-and-contacts.md#6-person_contact) | Education, occupations, qualifications, languages |
| `person_identifier` — per-scheme uniqueness — [01a §7](01a-accounts-and-contacts.md#7-person_identifier) | Insurance numbers, membership numbers of other bodies, measurements, clothing sizes |
| `account`, `account_credential` — [01a §4–5](01a-accounts-and-contacts.md#4-account) | Dietary habits, transport preferences, notes, anything collected this season |

**The test for the left column: does a rule exist that this layer physically cannot hold?**
*"Exactly one primary postal contact among the open rows"*, *"a school id may repeat, a birth
number may not"*, *"one current name per person"* — each is a constraint over a **known set of
columns**. A key/value table has no known set of columns; that is its entire purpose. Folding
those four tables in would have relocated working constraints into application code and been
called uniformity, which is
[shape 3](00a-invariant-register.md#3-the-answer-reads-another-table-a-resolver-or-a-graph)
built on purpose. Identity is closed because it was enumerated years ago and has not changed since.
Description is open because nobody can enumerate it. **That is the whole boundary, and it is worth
restating in review whenever a new table tempts someone to put it in either column.**

**What is not here either**, because it is not data *about* a person: relationships
([04-relationships](04-relationships.md)), belonging
([03-membership](03-membership.md)), money ([07-finance](07-finance.md)), event registrations and
their answers ([08-events](08-events.md)), authority
([05-authorization](05-authorization.md)).

---

## 2. `attribute_definition` — the vocabulary

**Fields**

| Field | Kind | Notes |
|---|---|---|
| `id` | surrogate id | |
| `code` | text, required | The stable handle. **Stored as typed, compared normalized** — see the rules below. |
| `label` | text, required | What a human sees. One language, and see the note on the vocabulary below ([D-149](../decisions/round-20.md#d-149--words-are-stored-in-one-language-and-a-label-is-not-translated)). |
| `description` | free text, optional | *What belongs in this field and what does not.* Cheap to write, and the only defence against a code meaning four things to four people. |
| `value_type` | text, required | One of: `text`, `long_text`, `number`, `date`, `yes_no`, `one_of`, `date_year`. Governs the input drawn and the warning given — **not** what may be saved (§4 of this file's rules, [D-084](../decisions/round-07-08.md#d-084--descriptive-data-is-organization-defined-at-runtime)). |
| `value_unit` | text, optional | Display suffix — `kg`, `cm`. Rendering only. |
| `allow_multiple` | boolean, required, default false | Whether more than one value may be current at once. Allergies: yes. Blood type: no. |
| `status` | text, required | One of: `live`, `retired`. **Two values, no third** ([D-084](../decisions/round-07-08.md#d-084--descriptive-data-is-organization-defined-at-runtime), [D-141](../decisions/round-20.md#d-141--a-definition-is-live-at-the-save-the-proposal-stage-its-queue-and-its-check-are-deleted)) — a definition is live at its save and retired is the only other thing it can be. See the status rules. |
| `category` | text, optional | Display grouping — `health`, `contact-admin`, `program`. **Grouping only: it grants nothing and restricts nothing**, and any sentence that says otherwise is reintroducing the sub-resource [D-083](../decisions/round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data) removed. |
| `sort_order` | integer, optional | |
| `retired_at`, `retired_reason` | timestamp, free text | Retiring is an administrative act and is explained. |
| Standard columns | | [00-conventions §7](00-conventions.md#7-standard-columns). |

**Allowed values for `one_of`** live in a small child table, **`attribute_option`**: `definition`,
`code`, `label`, `sort_order`, `status`. It is a table rather than a comma-separated string because
options are renamed, retired and re-ordered, and a retired option must keep meaning what it meant
on the day it was chosen — a value stored against it is a historical fact.

**Words are stored in one language: the one the organization writes in**
([D-149](../decisions/round-20.md#d-149--words-are-stored-in-one-language-and-a-label-is-not-translated)).
No `label_cs`/`label_en` pair, no translation table, no per-language row, no locale column in either
table above. The refusal is about what a label *is*: `label` is *what a human sees*, and a label is
not a rendering of something more authoritative underneath it — a row holding two labels would have
to be asked **which of the two the record is**, and whichever answer was chosen would demote the
other to a translation of it. The families who read another language are served by whoever reads the
question aloud or writes it down, and by an event form's own question text, which is free text typed
in whichever language the event is run in and is not a vocabulary item: **the vocabulary is for the
record, the form is for the conversation**, and only one of the two has to be stable enough to query.
What it costs: an imported label arrives in whatever language the paper form was in and stays there,
so correcting it is a curation act under `attribute.define` and not a locale switch — and an
organization that genuinely runs in two languages will hold two codes for one fact, a misery this
design does not prevent and does not pretend to.

**Rules**

- **Codes are unique in normalized form.** Before comparison a code is trimmed, case-folded and
  has internal whitespace collapsed. `Allergy`, `allergy` and `allergy ` are one code, and the
  second one is refused on write. This is the only anti-duplication rule the *database* can still
  enforce here, which is exactly why it is stated as a rule and not as a convention.
- **A definition is live at the save.** `attribute.define` is the curating permission, and the
  same person's write that names a code publishes it — no review list, no waiting, no age-out, and
  no curator role: **the permission is the curator**
  ([D-141](../decisions/round-20.md#d-141--a-definition-is-live-at-the-save-the-proposal-stage-its-queue-and-its-check-are-deleted)),
  because a role is an office that confers nothing
  ([D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape))
  and the only thing here that curates is a permission. **A value may not invent a code**: a value
  recorded for a code that does not exist is an error at the write, not a definition waiting for
  somebody. What this costs is stated rather than smoothed over — a bad code is live the moment it
  is saved, and every value recorded against it, a real value on a real person, inherits it from
  that moment. The defence is three things and there is no fourth: the save needs a permission, the
  trail records every save, and the code can be `retired` — which keeps its values and stops new
  ones ([D-109](../decisions/round-13.md#d-109--nothing-a-rule-names-is-deleted-deprecated-hidden-disabled--and-a-tab-instead-of-a-report)).
- **Retiring keeps the values.** A retired code leaves data entry and stays readable, reportable
  and revivable. **Deleting the label must never delete the fact underneath it**: a code discovered
  to have been named badly is an administrative event, and if retiring it destroyed nine years of
  records it will never be retired, and the vocabulary accretes instead of being curated — the
  slow failure this whole table is arranged to avoid.
- **A definition with values may not be deleted**, only retired
  ([00-conventions §9](00-conventions.md#9-referential-integrity-rules) — references restrict, none
  cascade). A definition with no values ever recorded may be deleted, and that is the only delete
  this table offers.
- **Changing `value_type` does not rewrite values.** Existing values are kept as they were written;
  the new type governs what is typed from then on. A type change is a display decision, and the
  history is not the display's to correct.
- **`allow_multiple` may go false → true freely, and true → false only with a report.** Turning it
  off does not merge existing multiples; it leaves the database holding a shape the definition
  forbids, which §8 check 3 will then report forever. Ask first whether the multiples are real.

**Permission.** Creating, renaming, merging or retiring a definition needs **`attribute.define`**
([permission catalog](../appendix/permission-catalog.md)). Recording a value needs no new
permission — see §4. **One of those four acts stopped being freely available in round 20, and it is the
rename:** a definition whose code an event question is bound to is now a code something references, and
[a code that is referenced may not be renamed](../decisions/round-18.md#d-131--shape-4-is-not-empty-and-a-code-that-is-referenced-may-not-be-renamed)
— a rename would silently re-answer every form that was asked under the old name, leaving no row in the wrong
state for a report to find, which is the shape this rule exists for
([D-139](../decisions/round-20.md#d-139--an-event-question-may-bind-to-a-stored-value-it-prefills-as-a-suggestion-and-writes-back-as-an-answer)).
**A merge is still a merge, and it is the deliberate half:** merging two codes carries the questions bound to
the disappearing one over to the surviving one as part of the act, because an answer recorded under a code has
to keep meaning what it meant when it was given. Retiring was never affected: a retired definition keeps its
code, and a bound question asked against a retired code is the design working, not a dangling reference.

---

## 3. `person_attribute` — a value one person has

**Fields**

| Field | Kind | Notes |
|---|---|---|
| `id` | surrogate id | |
| `person_id` | reference to person, required | |
| `attribute_definition_id` | reference to `attribute_definition`, required | Points at the vocabulary, live or retired; never at nothing. A value with no code is a note, and notes are their own code. |
| `value` | text, required | **One column, always text.** Not a `jsonb`, not parallel typed columns. See the note below. |
| `value_option_id` | reference to `attribute_option`, optional | Set when the type is `one_of`; the `value` text is then a denormalisation kept for display, and the option reference is the truth. |
| `recorded_note` | free text, optional | *"the doctor said this may change in spring"*. Kept beside the value rather than inside it, so the value stays comparable. |
| `source` | text, optional | `self`, `guardian`, `staff`, `legacy_import`. |
| Standard columns | | `created_at` / `created_by` double as *recorded at* / *recorded by*. |

**There are no `valid_from` / `valid_to` columns, and that is a decision rather than an omission.**
A row here is **the current belief**, overwritten in place; the sequence of beliefs is in
`audit_log` ([D-085](../decisions/round-07-08.md#d-085--the-identity-machinery-stays-structured-the-boundary-is-rules-not-sensitivity)),
which holds those values and is therefore the table §6 is about — this document's history is a
permission mark away from being an empty list, and saying the two are connected is the most this
section can honestly do about it.
The corpus gives periods to things that are *true over an interval* — a membership, a contact
address, an assignment — and a descriptive value is not that: it is a statement whose truth is
asserted now about whatever it is about, with a timestamp on the assertion. Putting periods here
would invite a UI that asks when an allergy began, which is a medical question the organization is
not competent to record and has no rule that could use.

**`value` is one text column, and there are no typed siblings.** A `value_number` and a
`value_date` beside it would let the database do something useful with a date — and would then make
`2019`, recorded as a year for a checkup, unsavable, which is the failure [D-084](../decisions/round-07-08.md#d-084--descriptive-data-is-organization-defined-at-runtime)
refuses: an empty field behind a validation error is a worse record than an imprecise one. **The
type belongs to the definition and to the form renderer; the storage stays uniform.** What that
costs is listed in §5 rather than discovered later.

**Rules**

- A value may not be blank. Absence is the absence of a row
  ([D-059](../decisions/round-05.md#d-059--unanswered-is-the-absence-of-a-row-a-registration-stores-two-values));
  an empty string is a lie that looks like an answer.
- **At most one current value per `(person, definition)` unless the definition allows multiple.**
  One row per pair, because there is no history — so the rule is a plain uniqueness rule *except*
  that whether it applies depends on a column in another table, which no constraint can express:
  [shape 3](00a-invariant-register.md#3-the-answer-reads-another-table-a-resolver-or-a-graph).
  **Check inside the writing transaction, and report the survivors** (§8 check 3). A partial unique
  index would be the right tool for the single-valued definitions and the wrong tool for the rest;
  choosing per definition is how this rule becomes a report instead of a guarantee.
- **Overwriting is an update, not a delete-and-insert.** The row keeps its `created_at` — that is
  when this fact first entered the system, which is a question someone asks — and the changed value
  with its author lands in the audit trail.

**A bound event question may prefill from this table and write back into it.** The binding lives on
the question, not here: `event_question.bound_attribute_code`, nullable, pointing at a **definition
code** and never at a `person_attribute` row ([D-139](../decisions/round-20.md#d-139--an-event-question-may-bind-to-a-stored-value-it-prefills-as-a-suggestion-and-writes-back-as-an-answer)).
The form **prefills** the person's current value as a *suggestion* the answerer confirms or edits —
nothing is hidden from them and nothing is silently copied — and submitting performs a **second act**:
a new value in this table, dated **today**, recorded as written by the person who answered, while the
answer itself stays a row of the event. The binding survives everything it could be accused of
because of what it names: a definition code is never deleted and is retired instead, so it outlives
the person whose values sit under it, and [00-conventions §4](00-conventions.md#4-deletion-policy)'s
rule that nothing may reference a `person_attribute` **row** — the condition on which erasure's one
hard delete stays invisible — is untouched. **What the binding may never become**: a reference to a
row id, which stays exactly as forbidden as §4 says it is, and a second home for the value, which it
is not — prefill is a suggestion, the write-back is a fresh value, and a form answer and a stored
value are two dated statements of one fact at two moments, the same shape this corpus already uses
for a name.

**Indexes** — on `person_id` (every read is per person), on `attribute_definition_id` (every report
is per code), and the per-`(person, definition)` rule above.

---

## 4. Who may read, and who may write

**Read: `person.view`, and nothing else.** No `attribute.*` read permission exists, because there is
nothing to gate that `person.view` does not already gate
([D-083](../decisions/round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)).
The three channels behave normally:

- **A unit leader** holding `person.view` scoped to their own unit reads their own members'
  descriptive data, including an allergy list.
- **A guardian** at `view` or `write` reads the child's whole record; at `none`, none of it.
- **A person** reads their own.

**This makes `person.view` the widest read permission in the system**, and the catalog marks it
accordingly rather than leaving it at the level it had when the record was smaller than the person.
Any future narrowing — *"read everything except…"* — is a decision entry about a second grant
scope, not a new code with a suggestive name
([E-7 is closed for exactly this reason](../open-questions.md#e-7)).

**Write: `person.edit` for values, `attribute.define` for the vocabulary.** That split is the design:
data entry is open to anyone who can already edit the person, because the alternative is the fact
never getting recorded; the vocabulary is narrow, because the vocabulary is what makes the data
queryable. **What the split no longer offers is an escape valve.** A value arriving for a code that
does not exist is an error at the write, not a proposal waiting for somebody
([D-141](../decisions/round-20.md#d-141--a-definition-is-live-at-the-save-the-proposal-stage-its-queue-and-its-check-are-deleted)):
the leader with a drug name at 23:00 either types it under a code that exists or says nothing, and
that failure — the fact buried in a `notes` value, or the fact absent — is the price the strict rule
pays on purpose, because a vocabulary is the one registry where an unreviewed addition is permanent
*in effect* even where it is deletable *in principle*. **The write-back of a bound form question is
not a third path either**: it goes through the same `person.edit` the answering channel already
uses, is audited with the answerer as its actor, and is refused — the form still saving its answer —
where the write is not permitted, so a form never half-writes a person
([D-139](../decisions/round-20.md#d-139--an-event-question-may-bind-to-a-stored-value-it-prefills-as-a-suggestion-and-writes-back-as-an-answer)).

---

## 5. What this design cannot do

Stated here because an open key/value layer is repeatedly described as flexible by people who have
not yet needed any of these, and because
[D-084](../decisions/round-07-08.md#d-084--descriptive-data-is-organization-defined-at-runtime)
was taken with them in view rather than in the abstract.

| Cannot | Why | What is done instead |
|---|---|---|
| Constrain a value | No constraint can reference the contents of a row chosen at runtime | The definition's type drives a **warning**; a human may always save |
| Type-check at the database | Values are one text column | ISO-format by convention, and §8 check 6 reports a type that is wrong for the whole definition |
| Compare or aggregate safely | `12` and `12 kg` and `twelve` are three strings | Report on the `one_of` codes; treat free text as a list to read, not a number |
| Express the one-value rule as a constraint | The rule reads another table ([shape 3](00a-invariant-register.md#3-the-answer-reads-another-table-a-resolver-or-a-graph)) | **Enforced in the writing transaction** (§3), which is a guard and not a constraint; §8 check 3 reports what got past it. The two are not alternatives — one stops it, the other notices it did not |
| Answer "what did we believe in 2019" from business data | Rows hold the current belief only | `audit_log`, which holds the values themselves (§6) and which [D-081](../decisions/round-06.md#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now) records as the corpus's weakest control. **This is the accepted risk, not a footnote: the history is real and nothing but an omitted line of code stands between it and being empty** — and since [D-088](../decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short), **nothing at all** stands between it and being empty after the payload window closes (§6) |
| Restrict one field to some readers | [D-083](../decisions/round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data) refused a privileged subset | One scope over one record; a court-ordered exception is a decision entry, not a code |
| Trust that a code means one thing | Codes are typed by humans | Normalized uniqueness, `description` on every definition, §8 check 1, and a save that needs `attribute.define` — the permission is the curator ([D-141](../decisions/round-20.md#d-141--a-definition-is-live-at-the-save-the-proposal-stage-its-queue-and-its-check-are-deleted)) |
| Keep a bound form's answer and the stored value equal | A bound question prefills from the value and writes a new one back ([D-139](../decisions/round-20.md#d-139--an-event-question-may-bind-to-a-stored-value-it-prefills-as-a-suggestion-and-writes-back-as-an-answer)); the two are one fact stated at two dated moments, and nothing reconciles them | The value wins as of today, because it is the row dated today; the prefill is where a disagreement shows itself, and neither row is rewritten when the other changes |

---

## 6. Erasure, retirement, and the audit payload

**Two opposite operations, and confusing them is the obvious mistake.**

- **Retiring a code** is administrative and keeps values. The *label* leaves service; the facts stay.
- **Redacting a person** is legal and erases values. When a person is anonymised
  ([00-conventions §8](00-conventions.md#8-personal-data-and-erasure)), every row in this table
  belonging to them is deleted. **A redacted person with attribute values attached is a redaction
  that did not happen** — §8 check 5, and the one check here that should alert rather than log.

**The trail holds these values, and that is the load-bearing consequence of the whole module.**
An audit entry about a `person_attribute` carries the before and after images, as it does for a contact
point or an assignment. Three things had to be true for that to be the right call, and it is worth
reading them as a dependency rather than as reassurance:

- **D-083 says a diagnosis is not a different kind of fact from a shoe size,** so a rule that stripped
  attribute values out of the payload while logging a change of address with its value would be a
  sensitive *subset* of the person record, reintroduced as a list of table names after it was deleted
  as a list of permission names.
- **D-085 overwrites values in place because the trail is their history,** so a payload without values
  is not a conservative trail, it is no trail: the question in §5's table becomes unanswerable by
  design, and the reason overwrite was cheap enough to choose disappears with it.
- **Therefore the guard on `audit_log` carries person data now.** An audit entry about a person is as
  sensitive as the person data it quotes, which is written as a requirement on `audit.view` in
  [appendix/permission-catalog-a-codes.md §8](../appendix/permission-catalog-a-codes.md#8-audit-and-system) and
  argued in [05-authorization §9](05c-access-log-and-resolver.md#9-access_log) — where the case against copying
  data into a less-guarded place is, in this table, a description of the table itself. **That single
  guard is a decision, not an omission: `audit.view` is the whole gate** — one permission, one check,
  no per-entry filter ([D-138](../decisions/round-20.md#d-138--one-permission-guards-the-whole-audit-trail-and-the-widening-is-on-the-record)).
  The alternative was a per-entry check inside the history view asking whether this reader could see
  this field; it would have been correct, and it would have made what an officer can read about 2019
  depend on an audience expression changed last week — and the trail's value is that it is legible
  without re-resolving the past, which is exactly what such a check spends. **The widening is
  therefore a stated property of the code rather than something left to be discovered: it opens the
  entire trail, it is granted rarely, and it is marked.**

**Those payloads now expire, which is a consequence of [D-088](../decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)
and not a detail of it.** Audit rows live as long as the system; their `old_values`/`new_values` are
emptied 24 months after they are written. Read that against the paragraph above and both halves are
true at once: **the trail is the only history this table has, and it stops being a history after two
years.** The honest description of what §5's row costs is therefore not "no temporal columns" but **no
long history** — three decisions stacked, none of them wrong on its own: values live in one row that is
overwritten, the copy of them depends on a write path remembering to log, and the copy ages out.

**The window is not a mitigation of that property, and it is not the guard either.** It bounds how
long a value sits where a holder of `audit.view` can read it, not who can read it while it sits.
**If the long history is ever actually needed — by a safeguarding review, or by a dispute about what
was known and when — the fix is
temporal columns on the value, which reverses
[D-085](../decisions/round-07-08.md#d-085--the-identity-machinery-stays-structured-the-boundary-is-rules-not-sensitivity).**
It is *not* a longer payload window, because stretching the window stretches exactly the guard
[D-086](../decisions/round-07-08.md#d-086--a-sensitivity-mark-grades-what-a-grant-exposes-not-the-table-it-reads)
graded, and [D-083](../decisions/round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)
refuses to keep a second copy somewhere safer.

**What is left of the redactor is small, and says so.** It scrubs the values that must never be logged
at all — credentials, tokens, integration secrets — and it stopped carrying the personal-data case
when the sensitive subset went: a key-name list cannot protect a table whose column names this
organization invents at runtime, and `allergy` is not on it and never will be.
[00-conventions §8](00-conventions.md#8-personal-data-and-erasure) states that once for the whole
schema, and [06-audit §2.2](06-audit-and-import.md#22-redaction-before-logging) keeps the withdrawn
rule visible so nobody reinstates it by inference.

**Erasure is the one thing here that is absolute.** Erasing a person deletes their rows *and* removes
their values from payloads already written, however lawfully
([06-audit §4](06b-redaction-and-checks.md#4-redaction-log)); a trail that keeps what the person asked to
have forgotten is not a history, it is the thing they asked to be rid of, filed where it reads well.

---

## 7. The legacy import, which is where the vocabulary comes from

The old system's columns become codes, and this is the largest single event in the life of the
attribute layer — most of the first few hundred definitions arrive here rather than from a deliberate
act of design, because [the corpus you have](../decisions/round-07-08.md#d-090--the-legacy-corpus-is-thousands-of-roster-rows-with-numbers-and-no-money)
is thousands of roster rows with free-text columns beside them. **That is one file arriving with the
organization's descriptive vocabulary in it, and it changes how the mapping has to be reviewed.**

- **Every raw field name in a batch must map to a code, be mapped to `discarded` with a reason, or
  stop the batch.** Silently dropping an unmapped column is how a decade of a fact the organization
  collected disappears on a Tuesday.
- **An unmapped column is an error at apply time.** The batch refuses and names the column; a value
  may not invent a code, and a column may not borrow one by similarity either. Nothing guesses at
  import time, because an import-time merge is invisible and unreviewable — merging near-duplicates
  is a curation act afterwards, by a human holding `attribute.define`, where the trail can see it
  ([D-141](../decisions/round-20.md#d-141--a-definition-is-live-at-the-save-the-proposal-stage-its-queue-and-its-check-are-deleted)).
- **The map is authored against a vocabulary that already exists.** The import does not bootstrap the
  vocabulary, it fills it in: every code the map names must be defined and `live` before the batch
  applies, or the batch refuses. This is not a trap but the shape the largest single event in this
  layer's life actually has — the map is authored and read *before* the batch applies, as one
  artefact, top to bottom, so whoever wrote the map wrote the vocabulary first, and the codes arrive
  `live` because they were `live` before the batch was ever typed. The cost is stated plainly: the
  first few hundred definitions are a writing job under `attribute.define` that must happen *before*
  the import that seemingly produces them, and a batch held at the door for an undefined column is
  this design working, not failing.
- **The mapping is recorded on the batch**, in `import_batch.field_mapping`, one entry per raw column
  ([06-audit §3](06a-import.md#3-import-pipeline) explains why the grain is a column and not a
  staged row, which is the plausible wrong answer). The mapping is not the schema; changing it is an
  act of curation with an audit entry, not a migration.

---

## 8. Integrity checks

**Invariants to verify**

1. **Codes close enough to be the same thing** — same normalized form after stripping punctuation
   and collapsing plural forms, or the same label. A list to read, not a failure, and the
   continuous cost of an open vocabulary.
2. **A live definition with no values ever recorded.** Retirable. Worth knowing: a dead code in a
   picker is a small tax paid by everyone who opens the form.
3. **More than one current value for a definition that forbids multiples.** The bypass of §3's
   cross-table rule — an import, a hand-fix, a path that skipped the check. Non-zero means the
   guard is missing, not that the data is odd.
4. **A value that is blank, whitespace, or longer than the type could have produced.** A
   `yes_no` code with a three-sentence value is a definition being used as a note field, and the
   report is a conversation about which one it should have been.
5. **A redacted person with attribute rows, or with attribute values still present in `audit_log`.**
   Should never be non-empty; this is the erasure guarantee and it alerts.
6. **A definition whose values contradict its declared type wholesale** — a `date` code where
   nothing parses as a date. The type is advisory for one value and a signal for all of them: at
   that point the definition is wrong, not the data.

**Check 5 is the one that alerts:** a person's data outliving their erasure. **Check 3 is the one
that indicts the code rather than the data:** non-zero there means some write path skipped §3's
guard, and the fix is the path, not the rows. **Check 1 is the vocabulary talking** — never a
failure, only the permanent cost of an open vocabulary, and the list worth reading before saving a
near-duplicate. Everything else on this list is housekeeping.

---

## 9. Open issues

**None registered.** The questions this layer raises most are answered by design on the page rather
than left in [open-questions.md](../open-questions.md): an event question may bind to a code and
prefill from it, as a suggestion the answerer confirms and a fresh dated value on submit, never as a
copy or a reference to a value row ([D-139](../decisions/round-20.md#d-139--an-event-question-may-bind-to-a-stored-value-it-prefills-as-a-suggestion-and-writes-back-as-an-answer));
a definition is live at the save of whoever holds `attribute.define`, and that permission is the
curator, so no proposal may sit anywhere because none can exist
([D-141](../decisions/round-20.md#d-141--a-definition-is-live-at-the-save-the-proposal-stage-its-queue-and-its-check-are-deleted));
the vocabulary is in one language and a label is not translated
([D-149](../decisions/round-20.md#d-149--words-are-stored-in-one-language-and-a-label-is-not-translated));
and one permission, granted rarely and marked, is the whole guard on the trail that holds a child's
values — a position, not an omission
([D-138](../decisions/round-20.md#d-138--one-permission-guards-the-whole-audit-trail-and-the-widening-is-on-the-record)).
What remains unknown here is not a question with an owner but the cost §6 states: the history of a
value is a copy that depends on a write path remembering to log, and that copy ages out.
