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
[F-10 shape 3](../open-questions.md#f-10--which-invariants-the-orm-cannot-express-and-who-writes-those)
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
| `label` | text, required | What a human sees. |
| `description` | free text, optional | *What belongs in this field and what does not.* Cheap to write, and the only defence against a code meaning four things to four people. |
| `value_type` | text, required | One of: `text`, `long_text`, `number`, `date`, `yes_no`, `one_of`, `date_year`. Governs the input drawn and the warning given — **not** what may be saved (§4 of this file's rules, [D-084](../decisions/round-07-08.md#d-084--descriptive-data-is-organization-defined-at-runtime)). |
| `value_unit` | text, optional | Display suffix — `kg`, `cm`. Rendering only. |
| `allow_multiple` | boolean, required, default false | Whether more than one value may be current at once. Allergies: yes. Blood type: no. |
| `status` | text, required | One of: `proposed`, `live`, `retired`. See the status rules. |
| `category` | text, optional | Display grouping — `health`, `contact-admin`, `program`. **Grouping only: it grants nothing and restricts nothing**, and any sentence that says otherwise is reintroducing the sub-resource [D-083](../decisions/round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data) removed. |
| `sort_order` | integer, optional | |
| `proposed_by`, `proposed_at` | person, timestamp | Set when a value arrived for a code that did not exist. |
| `retired_at`, `retired_reason` | timestamp, free text | Retiring is an administrative act and is explained. |
| Standard columns | | [00-conventions §7](00-conventions.md#7-standard-columns). |

**Allowed values for `one_of`** live in a small child table, **`attribute_option`**: `definition`,
`code`, `label`, `sort_order`, `status`. It is a table rather than a comma-separated string because
options are renamed, retired and re-ordered, and a retired option must keep meaning what it meant
on the day it was chosen — a value stored against it is a historical fact.

**Rules**

- **Codes are unique in normalized form.** Before comparison a code is trimmed, case-folded and
  has internal whitespace collapsed. `Allergy`, `allergy` and `allergy ` are one code, and the
  second one is refused on write. This is the only anti-duplication rule the *database* can still
  enforce here, which is exactly why it is stated as a rule and not as a convention.
- **`proposed` is a real status with real behaviour.** A value recorded against a code that does
  not exist creates a definition in `proposed`, owned by whoever proposed it. Proposed definitions
  appear nowhere in data entry, appear in the curation queue (§8 check 1), and their values are
  readable by anyone entitled to read the person — the person's data is not hidden from the
  organization because a label is waiting for approval. Curation promotes, merges, renames or
  discards it.
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
  forbids, which §8 check 4 will then report forever. Ask first whether the multiples are real.

**Permission.** Creating, renaming, merging or retiring a definition needs **`attribute.define`**
([permission catalog](../appendix/permission-catalog.md)). Recording a value needs no new
permission — see §4.

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
  [F-10 shape 3](../open-questions.md#f-10--which-invariants-the-orm-cannot-express-and-who-writes-those).
  **Check inside the writing transaction, and report the survivors** (§8 check 4). A partial unique
  index would be the right tool for the single-valued definitions and the wrong tool for the rest;
  choosing per definition is how this rule becomes a report instead of a guarantee.
- **Overwriting is an update, not a delete-and-insert.** The row keeps its `created_at` — that is
  when this fact first entered the system, which is a question someone asks — and the changed value
  with its author lands in the audit trail.
- Values recorded against a `proposed` definition are hidden from forms and reports until curation,
  and are **not** hidden from anyone with read access to the person. The organization's data quality
  problem is not the family's confidentiality problem.

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
queryable. An improvised need saves as a proposal, which is the one path out of the failure where a
leader types a drug name into a `notes` field at 23:00 and it is never seen by a report again.

---

## 5. What this design cannot do

Stated here because an open key/value layer is repeatedly described as flexible by people who have
not yet needed any of these, and because
[D-084](../decisions/round-07-08.md#d-084--descriptive-data-is-organization-defined-at-runtime)
was taken with them in view rather than in the abstract.

| Cannot | Why | What is done instead |
|---|---|---|
| Constrain a value | No constraint can reference the contents of a row chosen at runtime | The definition's type drives a **warning**; a human may always save |
| Type-check at the database | Values are one text column | ISO-format by convention, and §8 check 7 reports a type that is wrong for the whole definition |
| Compare or aggregate safely | `12` and `12 kg` and `twelve` are three strings | Report on the `one_of` codes; treat free text as a list to read, not a number |
| Express the one-value rule as a constraint | The rule reads another table ([F-10 shape 3](../open-questions.md#f-10--which-invariants-the-orm-cannot-express-and-who-writes-those)) | **Enforced in the writing transaction** (§3), which is a guard and not a constraint; §8 check 4 reports what got past it. The two are not alternatives — one stops it, the other notices it did not |
| Answer "what did we believe in 2019" from business data | Rows hold the current belief only | `audit_log`, which holds the values themselves (§6) and which [D-081](../decisions/round-06.md#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now) records as the corpus's weakest control. **This is the accepted risk, not a footnote: the history is real and nothing but an omitted line of code stands between it and being empty** — and since [D-088](../decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short), **nothing at all** stands between it and being empty after the payload window closes (§6) |
| Restrict one field to some readers | [D-083](../decisions/round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data) refused a privileged subset | One scope over one record; a court-ordered exception is a decision entry, not a code |
| Trust that a code means one thing | Codes are typed by humans | Normalized uniqueness, `description` on every definition, §8 check 2, and a named curator |

---

## 6. Erasure, retirement, and the audit payload

**Two opposite operations, and confusing them is the obvious mistake.**

- **Retiring a code** is administrative and keeps values. The *label* leaves service; the facts stay.
- **Redacting a person** is legal and erases values. When a person is anonymised
  ([00-conventions §8](00-conventions.md#8-personal-data-and-erasure)), every row in this table
  belonging to them is deleted. **A redacted person with attribute values attached is a redaction
  that did not happen** — §8 check 6, and the one check here that should alert rather than log.

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
  [../appendix/permission-catalog.md §8](../appendix/permission-catalog-a-codes.md#8-audit-and-system) and
  argued in [05-authorization §9](05c-access-log-and-resolver.md#9-access_log) — where the case against copying
  data into a less-guarded place is, in this table, a description of the table itself. **Whether that
  single guard is the right shape is not settled here**: filtering history per entry, or splitting the
  permission into the trail's shape and its payloads, are both live options and both have costs
  ([AT-4](../open-questions.md#at-4--is-one-permission-enough-to-guard-a-trail-that-holds-person-data)),
  the largest being that one of the three is already built, so declining to choose is a choice nobody has
  to sign.

**Those payloads now expire, which is a consequence of [D-088](../decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)
and not a detail of it.** Audit rows live as long as the system; their `old_values`/`new_values` are
emptied 24 months after they are written. Read that against the paragraph above and both halves are
true at once: **the trail is the only history this table has, and it stops being a history after two
years.** The honest description of what §5's row costs is therefore not "no temporal columns" but **no
long history** — three decisions stacked, none of them wrong on its own: values live in one row that is
overwritten, the copy of them depends on a write path remembering to log, and the copy ages out.

That is also the cheapest thing this module will ever do about
[AT-4](../open-questions.md#at-4--is-one-permission-enough-to-guard-a-trail-that-holds-person-data),
and it should be read that way rather than as a resolution: a wrongly-graded `audit.view` can still read
a child's descriptive values, but only for as long as they are recent. **If the long history is ever
actually needed — by a safeguarding review, or by a dispute about what was known and when — the fix is
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
- **An unmapped column maps to a `proposed` code**, named from the raw column, not to an existing
  code by similarity. A human merges near-duplicates afterwards; nothing guesses at import time,
  because an import-time merge is invisible and unreviewable.
- **At this scale, `proposed` is the last resort and not the outcome.** The map is authored and read
  *before* the batch applies — it is one artefact, top to bottom — so a column that survives that
  reading has been named by a human and its codes arrive **`live`**. `proposed` is for what a person at
  a desk improvises later. If several hundred codes arrive `proposed` instead, check 1 opens full, its
  age signal means nothing from the first day, and the first lesson the organization learns about this
  layer is that its warning queue is noise. That is a real risk of this corpus and is the honest half
  of an answer to [AT-2](../open-questions.md#at-2--who-curates-the-vocabulary-and-how-long-may-a-proposal-sit),
  which stays open for the runtime case.
- **The mapping is recorded on the batch**, in `import_batch.field_mapping`, one entry per raw column
  ([06-audit §3](06a-import.md#3-import-pipeline) explains why the grain is a column and not a
  staged row, which is the plausible wrong answer). The mapping is not the schema; changing it is an
  act of curation with an audit entry, not a migration.

---

## 8. Integrity checks

**Invariants to verify**

1. **Values recorded against a `proposed` definition, by age.** The curation queue. Non-empty is
   normal; *old* is the finding: a proposal nobody has looked at for a quarter is a fact the
   organization is storing in a private language.
2. **Codes close enough to be the same thing** — same normalized form after stripping punctuation
   and collapsing plural forms, or the same label. A list to read, not a failure, and the
   continuous cost of an open vocabulary.
3. **A live definition with no values ever recorded.** Retirable. Worth knowing: a dead code in a
   picker is a small tax paid by everyone who opens the form.
4. **More than one current value for a definition that forbids multiples.** The bypass of §3's
   cross-table rule — an import, a hand-fix, a path that skipped the check. Non-zero means the
   guard is missing, not that the data is odd.
5. **A value that is blank, whitespace, or longer than the type could have produced.** A
   `yes_no` code with a three-sentence value is a definition being used as a note field, and the
   report is a conversation about which one it should have been.
6. **A redacted person with attribute rows, or with attribute values still present in `audit_log`.**
   Should never be non-empty; this is the erasure guarantee and it alerts.
7. **A definition whose values contradict its declared type wholesale** — a `date` code where
   nothing parses as a date. The type is advisory for one value and a signal for all of them: at
   that point the definition is wrong, not the data.

**Check 1 and check 6 are the two that matter.** One is the vocabulary rotting; the other is a
person's data outliving their erasure. Everything else on this list is housekeeping.

---

## 9. Open issues

Four, all registered in [open-questions.md](../open-questions.md): whether event questions should
bind to codes so a returning camper's allergy is prefilled rather than re-typed
(**AT-1**), who holds `attribute.define` in the starting role set and how long a proposal may sit
(**AT-2**), whether definition labels need translation (**AT-3**, inherited from the
multi-language question in §H), and — the one this document cannot settle — **whether one permission is
enough to guard a trail that holds a child's values** (**AT-4**), which is §6's weakest link stated as a
question rather than as a design.
