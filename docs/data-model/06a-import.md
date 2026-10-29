# Data Model — Audit and Import: the legacy import pipeline

`import_batch`, the staging tables, the six stages, the field→code mapping, reversibility,
idempotency, and what a source row actually evidences. The trail these stages write to is
[§2](06-audit-and-import.md#2-audit_log).

**Section numbers are shared across the three parts** and never renumbered, because other pages cite
them by number and their anchors are built from them:
[06-audit-and-import.md](06-audit-and-import.md) holds §1–§2 (the two audit trails and the `audit_log`
table), [06a](06a-import.md) §3 (the legacy import pipeline), and
[06b](06b-redaction-and-checks.md) §4–§6 (the redaction log, the integrity checks, open issues).

---

## 3. Import pipeline

Six stages, from
[../domain/03-identity-and-legacy.md](../domain/03-identity-and-legacy.md#7-legacy-import-pipeline).
The guiding requirements: **idempotent**, **reversible per batch**, **never overwrites
self-registered data**, **preserves provenance**.

**What arrives is two exports, and each is evidence of a different thing.**
[D-090](../decisions/round-07-08.md#d-090--the-legacy-corpus-is-thousands-of-roster-rows-with-numbers-and-no-money)
recorded the corpus as *roster rows* — people attending units — and nearly everything below was built on
that word, including the section that policed what a roster may be read as proving.
[D-092](../decisions/round-09.md#d-092--the-corpus-is-people-and-events-and-it-names-no-units)
corrected the description from the source itself: a **membership export** and an **attendance export**.

| Half | What one source row says | What the pipeline writes |
|---|---|---|
| **People** | name, birth date, *member of the organization for a period* | a `person`, and a bounded `membership` ([D-093](../decisions/round-09.md#d-093--the-one-off-import-may-create-memberships-both-ends-dated)), which brings its root participation row with it |
| **Events** | an event, and who attended it | an `event` that belongs to nobody ([D-102](../decisions/round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)) and one `event_registration` per listed attendee |

**Neither half names a unit, and unit assignment is out of scope by instruction — a consequence, not an
omission.** `parsed_unit_code` and `parsed_unit_name` stay in the parser (§3's staged-row table says what
reads them now, which is nothing), no batch creates a body of any kind, and no belonging row is ever
imported for one. **The consequence in one sentence: the system's historical record contains no
sub-unit participation**, so "who was in pack X in 2011?" has no answer on day one and gets one only from
live data forward. The model has always been able to hold that history; the source cannot say it, and the
sentence is here so that the first person to ask the question finds the sentence instead of the absence.

**`import_batch`** — one run of the pipeline, and the unit revert works on.

**Fields**

| Field | Kind | Notes |
|---|---|---|
| `id` | surrogate id | |
| `name` | text, required | |
| `batch_kind` | text, required | One of: `people`, `events`. **A batch types itself**, and it does so because it has to rather than because it is tidy: one `field_mapping` cannot serve both halves of the corpus, so the kind is what decides which mapping shape, which parse rules, which `source_row_hash` definition (Idempotency below) and which of `staging_import_row`'s created ids get read. There is no default — a batch that does not say which it is does not leave `staging`. Recorded as a consequence of the answer that split the corpus in two ([D-092](../decisions/round-09.md#d-092--the-corpus-is-people-and-events-and-it-names-no-units)), not as an open question, because the same answer decided this about it |
| `description` | text, optional | |
| `source_type` | text, required | One of: `csv`, `xlsx`, `json`, `sql_dump`, `manual_entry`, `other` |
| `source_reference` | text, optional | Where the file lives, or what it is. Enough to find the original again |
| `source_hash` | text, optional | SHA-256 of the source file. Detects re-importing the same file under a new name |
| `row_count` | integer, optional | |
| `status` | text, required | One of: `staging`, `parsed`, `matching`, `review`, `applying`, `applied`, `reverted`, `failed`. Default `staging` |
| `dry_run` | boolean, required | Default false. A dry run parses and matches but writes nothing to business tables |
| `created_by` | reference to person, required | |
| `created_at` | timestamp, audit time | |
| `applied_at` | timestamp, audit time, optional | |
| `applied_by` | reference to person, optional | |
| `reverted_at` | timestamp, audit time, optional | |
| `reverted_by` | reference to person, optional | |
| `revert_note` | text, optional | |
| `field_mapping` | free-form jsonb, optional | **This batch's raw-column → attribute-code map**: one entry per raw column in the source, each naming one code or `discard` with a reason. Fixed for the batch, reviewed as a unit, editable only as a new decision — see *The legacy field→code mapping* below, which explains why the grain is a column and not a row. **On an events batch this map is mostly `discard`, and that is its honest shape rather than a smell**: event title and date become `parsed_event_*` values, not attribute codes, and the only columns on such a file worth a code are the descriptive ones riding along on the attendee |
| `error_summary` | text, optional | |
| `notes` | text, optional | |

**Indexes**

- Batches by status — the queue of runs that are not finished.

**`staging_import`** — one source row, kept exactly as it arrived.

**Fields**

| Field | Kind | Notes |
|---|---|---|
| `id` | surrogate id | |
| `batch_id` | reference to import batch, required | |
| `source_row_number` | integer, optional | |
| `raw_data` | free-form jsonb, required | The row VERBATIM. Never modified. This is the evidence |
| `source_row_hash` | text, required | Deterministic hash of the meaningful fields. The idempotency key: re-importing a file matches on this and skips already-applied rows |

**Rules**

- `(batch_id, source_row_hash)` is unique — one staged row per batch per source row. It
  covers all rows, not only unapplied ones.

**Indexes**

- The staged rows of one batch.

**`staging_import_row`** — what the parser made of that source row, and what became of it.
**One staged row is one person**, on both halves of the corpus: a person's membership period on a people
batch, a person's attendance at one event on an events batch. That is a decision rather than an
observation, because an attendance export arrives most often as one row per *event* with the attendees
packed into a cell, and unpacking it there would put the idempotency key and the review queue at the wrong
grain — a batch that resolves half an event's attendee list would have nothing to skip on the re-run. **So
the parser unpacks a packed attendee list into one staged row per attendee before this table**, and the
event's own columns repeat down those rows, which is what the matching rule below is for.

**Fields**

| Field | Kind | Notes |
|---|---|---|
| `id` | surrogate id | |
| `staging_id` | reference to staging row, required | |
| `parsed_given_name` | text, optional | |
| `parsed_family_name` | text, optional | |
| `parsed_name_normalised` | text, optional | Diacritics stripped, casefolded |
| `parsed_birth_date` | date, optional | |
| `parsed_birth_precision` | text, optional | Reuses the `person.birth_date_precision` values |
| `parsed_unit_code` | text, optional | **Parsed, and read by nobody.** Kept deliberately: an export that surprises whoever runs it with a unit column is exactly what this field and the `unit_not_found` warning are for, and keeping them costs nothing. Nothing resolves them, no batch creates an `org_unit`, and no imported sub-unit participation row can appear as a result ([D-092](../decisions/round-09.md#d-092--the-corpus-is-people-and-events-and-it-names-no-units), §3). An earlier draft had these two columns driving unit creation and the identity of a historical unit; that machinery is gone, the columns are not |
| `parsed_unit_name` | text, optional | As `parsed_unit_code` |
| `parsed_period_from` | date, optional | **A people batch.** The start of the membership period the export states |
| `parsed_period_to` | date, optional | **A people batch.** Often NULL in the source; see the inference rules below. An imported membership is never left open-ended (§3.1) |
| `parsed_event_title` | text, optional | **An events batch.** The occasion as the export states it. Normalised at match time rather than stored twice; the verbatim value is in `staging_import.raw_data` |
| `parsed_event_date` | date, optional | **An events batch.** With the title, what an attendee row is matched against, so that ten thousand attendees produce the events that happened rather than a copy each — the rule is below |
| `parse_status` | text, required | One of: `ok`, `warning`, `error`. Default `ok` |
| `parse_warnings` | list of text | For example `birth_date_year_only`, `unit_not_found`, `ambiguous_name`. Warnings do not block; errors do. `unit_not_found` still fires on a file that carries a unit column and still changes nothing, because nothing reads the parsed unit |
| `resolution` | text, optional | One of: `link_existing`, `create_new`, `discard`, `deferred` |
| `resolved_person_id` | reference to person, optional | |
| `resolved_by` | reference to person, optional | |
| `resolved_at` | timestamp, audit time, optional | |
| `resolution_note` | text, optional | |
| `applied` | boolean, required | Default false |
| `applied_person_id` | reference to person, optional | What this row created |
| `applied_membership_id` | reference to membership, optional | What this row created — **set on every row of a people batch whose source states a membership period**, because the export does state periods and importing one is not inference (§3.1, [D-093](../decisions/round-09.md#d-093--the-one-off-import-may-create-memberships-both-ends-dated)). **Empty on every row of an events batch**, and a set value on an events row is §3.1 having been broken: membership may be imported from a period the source states, never from an attendance list |
| `applied_event_id` | reference to event, optional | **An events batch.** The event this attendee row was matched to, or created by it. **Shared across rows**, which is the difference from the four ids above: a hundred attendees of one camp name one event, and revert has to know that (§Reversibility) |
| `applied_registration_id` | reference to event registration, optional | **An events batch.** What this row created — one per attendee, and the only row an attendee who was *not* listed gets, which is none (§3.1, [D-059](../decisions/round-05.md#d-059--unanswered-is-the-absence-of-a-row-a-registration-stores-two-values)) |
| `created_at` | timestamp, audit time | |

**Rules**

- **One event per (title, date), not one per attendee.** `uq_staging_event_match` is this rule's name.
  Enforced inside the transaction that applies a staged row, in this order: 1. normalise the title and
  take the date; 2. look for an event this batch has already created with that pair, then for an event
  already in the system with it; 3. reuse what was found, otherwise create it and record it on this row;
  4. write the registration. **Application layer, deliberately** — the pair spans rows of one batch rather
  than columns of one row, and a uniqueness claim across a batch describes how the file is read, not what
  the data holds ([`00-conventions.md §6a`](00-conventions.md#6a-who-enforces-an-invariant-now) is the
  register for that kind of answer). The failure it prevents is the loud kind run quietly: ten thousand
  attendee rows becoming ten thousand events, none of them deletable except by revert.
- **Which created ids a row may carry is decided by `import_batch.batch_kind`, not by the row.** A people
  batch fills `applied_person_id` and `applied_membership_id`; an events batch
  fills `applied_person_id` — an attendee who had to be created is still a person created — plus
  `applied_event_id` and `applied_registration_id`. A row carrying one from each group is a batch that was
  typed wrongly, and revert reads this rule to know what it is about to delete.

**Indexes**

- The staged rows of one parsed row.
- The review queue: parse status and resolution, restricted to rows with no resolution or a
  `deferred` one. Decided rows are not in it.
- Applied rows only.

### The legacy field→code mapping

Any legacy column that is not identity machinery becomes an attribute code, and **this is where the
vocabulary comes from**: most of the first two hundred definitions arrive here rather than from a
deliberate act of design ([09-attributes.md §7](09-attributes.md#7-the-legacy-import-which-is-where-the-vocabulary-comes-from)
owns the rule, and states why; what follows is only what the pipeline has to obey).

- **Every raw field name in a batch maps to a code, or is mapped to `discard` with a reason, or the
  batch stops.** An unmapped column maps to a **`proposed`** code named from the raw column — never to
  an existing code picked by similarity, because an import-time merge is invisible and unreviewable
  and a human makes that judgement afterwards, with both codes in front of them.
- **The mapping is recorded on the batch**, in `import_batch.field_mapping`, so a mapping later found
  wrong can be re-run rather than reverse-engineered from the damage it did. The mapping is not the
  schema: changing it is an act of curation with an audit entry, not a migration.
- **Which table it is *not* on, because the wrong one is plausible.** An earlier draft of this
  subsection said the mapping sat "on `staging_import_row` alongside the raw value", and that is the
  wrong grain twice over: `staging_import_row` is one row per *person* and holds a fixed set of
  `parsed_*` columns, so a per-column fact has nowhere to sit there, and anything per-row would be a
  mapping that can differ between two people in the same batch — which is precisely how one legacy
  column ends up as two codes, quietly, with nothing to review. The raw values themselves stay where
  they always were, verbatim in `staging_import.raw_data`; the map is one table up.

**What this costs is a stage that is allowed to fail loudly.** A batch with unmapped columns does not
apply, and somebody has to say what those columns were — friction at the worst possible moment, since
imports are always late. It is the cheaper failure. The alternative is a silent drop, which is the
same loss as deleting the column and the same one §3's guiding requirements were written against: in
2031 someone asks what the old system's `POZNAMKA` column held, and the answer is that a script
nobody still works with decided it was not interesting.

### Reversibility

`staging_import_row` holding the created ids is what makes per-batch revert possible, and the two batch
kinds leave different ids behind — which is why the order below is one list rather than one per kind.
Revert removes only what this batch created, and it runs in this order:

1. Take every staged row of the batch being reverted.
2. Undo what they created, **dependents first**, in this dependency order: the `event_registration` rows,
   then the `event` rows those registrations pointed at, then the
   `membership` rows, then the `person` rows — and a row the batch created outright is removed rather than
   merely amended. A people batch leaves the first two arms empty and an events batch leaves the `membership`
   arm empty (§3.1); both arms exist, and neither may be skipped in the general implementation just because the
   batch in hand does not use it. Four arms, and the implementation walks all four.
3. Finally mark the staged rows themselves unapplied.

**An event is deleted at most once, which is the one place revert is not row-local.** `applied_event_id`
is shared across the attendee rows of one occasion, so step 2 must collect the *distinct* events the batch
created and delete each after the last registration pointing at it is gone. **An event the batch created
that anything outside the batch now references is the refusal below, not a delete** — and the pre-flight
check has to look for that reference specifically, because a row referencing an event does not reference
the staged row that made it, so the ordinary reference scan cannot see it.

**Revert is only safe before live data references the imported rows.** Once a real person
has been linked, or an attendance recorded against an imported person, or a live registration attached to
an imported event, deleting the row breaks it. Therefore:

- Revert is allowed only while `import_batch.status = 'applied'` **and** no row created by
  the batch has been referenced by a later live record.
- Detecting that requires checking for references — implement as a pre-flight check that
  reports which rows cannot be reverted, and refuse rather than partially applying.
- After that window, corrections are made by editing the data, not by reverting. This is
  the honest behaviour; a "revert" that silently orphans references is worse than refusing.
- **Step 2's removals are audited like any other write**, one entry per row deleted, each
  naming the batch. This is the only hard delete a business row can meet, and it is precisely
  the case where someone will later ask "this person existed in March and is gone now — what
  happened?" An undo that erases the rows and leaves no trace of having erased them is not a
  rollback but a cover-up, and it is the same undo a reviewer is trusting when they agree to
  revert at all. [`00-conventions.md §4`](00-conventions.md#4-deletion-policy) is why no other
  path is allowed to do this.

> **Bias toward import in small batches and review before applying.** Reversibility is a
> safety net, not a workflow.

### Idempotency

The `(batch_id, source_row_hash)` uniqueness above makes re-staging cheap. Idempotency across
*batches* needs the hash to be computed from the row's semantic content, not its position — and since
[D-092](../decisions/round-09.md#d-092--the-corpus-is-people-and-events-and-it-names-no-units) the
corpus has two semantic contents, so **`batch_kind` selects which of the two definitions below runs**. A
people row and an events row about the same person must not look like the same row, and they cannot: their
last two inputs come from different halves of the world.

A **people** batch, one row per membership period — unchanged from the previous round, and unchanged on
purpose:

```
source_row_hash = sha256(
    normalise(given_name) || '|' ||
    normalise(family_name) || '|' ||
    coalesce(birth_date::text,'') || '|' ||
    coalesce(unit_code,'') || '|' ||
    coalesce(period_from::text,'')
)
```

An **events** batch, one row per attendee at one occasion:

```
source_row_hash = sha256(
    normalise(given_name) || '|' ||
    normalise(family_name) || '|' ||
    coalesce(birth_date::text,'') || '|' ||
    normalise(event_title) || '|' ||
    coalesce(event_date::text,'')
)
```

**Read `unit_code` in the first definition honestly: for this corpus it is empty on every row**, since
the export names no units, so it is a constant input doing nothing. It stays, because removing it is a
version change that buys nothing and the rule under this block is the one that matters — **the hash
function must be stable**, changing it invalidates every previously staged row, and *version it if it must
change* rather than editing it in place. Two definitions where one was expected is the same rule applied
to a corpus that turned out to be two files: nothing staged under the people definition is disturbed by
the events one, and both are versioned from here.

Then a re-import of an overlapping export produces rows that match already-applied ones, and the pipeline
can skip them. Note what the two hashes are keyed on, since the events one is the weaker instrument: it
keys on a *title and a date*, which is the most the export states, so a source that spells one camp two
ways is two rows, and two sources that spell two camps one way on one day is one row. The matching rule
above inherits both, and neither is fixable in the pipeline — the fix is a human in the review queue.

### End-date inference

A membership export rarely states when a period ended, and since
[D-093](../decisions/round-09.md#d-093--the-one-off-import-may-create-memberships-both-ends-dated) it
is allowed to answer: an imported row is now a real `membership`, so what its end date is inferred from is
a live question again rather than a question about a participation row. Three defensible options:

| Rule | Effect | Risk |
|------|--------|------|
| Leave `valid_to` NULL | Person appears to be current | **Wrong and dangerous** — inflates the member count, and an open row reads as present-tense belonging. **And it is dangerous in the loaded sense again**: an open imported `membership` satisfies `is_current_member()`, so it passes the permission gate (D-039). The row above this one said, one round ago, that "a roster batch can no longer take" that route because a roster batch makes no membership — [D-093](../decisions/round-09.md#d-093--the-one-off-import-may-create-memberships-both-ends-dated) withdrew the premise, and with it the only reason this option had stopped being a live hazard. It is a hazard again, which is why *Never NULL* below is a rule and not a preference |
| End at the end of the organizational year of the last period the person appears in | Defensible, documented | May truncate a period that continued |
| End at the last date the person appears in *any* export | Best fidelity, needs all exports | Requires the complete dataset |

**Recommended default:** end at the end of the organizational year of the last period in
which the person appears, marked `data_confidence = 'low'` and with a parse warning. Never
NULL — **and read that as the surviving half of the ban D-090 left standing: never an open-ended
membership, and never one inferred from an attendance row** (§3.1). Both ends of the period are what makes
an imported membership safe; the import itself is not.

### 3.1 What a source row actually evidences

**The question is what a source row may be read as proving**, and the answer has two halves that are not the
same answer, because the corpus is two exports and not one roster: between them they evidence presence *at an
occasion* and membership *of the organization*, and evidence no unit at all
([D-090](../decisions/round-07-08.md#d-090--the-legacy-corpus-is-thousands-of-roster-rows-with-numbers-and-no-money),
[D-092](../decisions/round-09.md#d-092--the-corpus-is-people-and-events-and-it-names-no-units)).

**A people row evidences a bounded membership, and the import writes one.** The source states a name, a
birth date and *the period during which this person was a member of the organization* — which is a
membership claim made by the source rather than inferred by the reader, and that distinction is the whole
of what [D-093](../decisions/round-09.md#d-093--the-one-off-import-may-create-memberships-both-ends-dated)
changed. So a people batch writes a `membership` with **both** `valid_from` and `valid_to` set,
`data_confidence = 'low'`, the batch id on it — **and nothing else in the temporal layer**: one row in the
transaction, and no second row to keep it company
([03-membership.md §5](03-membership.md#5-unit_participation--deleted-by-d-097)). **One row per period the
source states, not one per calendar year**: an
export of consecutive years is a period, and the `renewed_from_membership_id` chain is left to whoever
reconstructs it by hand, because a renewal chain asserted by a parser is a lineage nobody chose and it is
the kind of derived history
[D-096](../decisions/round-09.md#d-096--a-reused-unit-number-is-a-new-unit-unless-someone-records-the-continuity)
refuses to infer about units for the same reason.

**An events row evidences presence at one occasion, and nothing beyond it.** It writes an
`event_registration` for the listed attendee with `was_present = true`, against an event that **belongs to
nobody** ([D-102](../decisions/round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)),
so the import owes no owner choice at all — and **no row at all for anybody who is not listed**: inventing `not_attending` from silence would
put words in a source that said nothing ([D-059](../decisions/round-05.md#d-059--unanswered-is-the-absence-of-a-row-a-registration-stores-two-values)).
**Neither half of the import writes a belonging row for a body.** A people row produces a `membership` and an
events row a registration; D-041's second species of belonging is not a thing either half could write
([D-041](../decisions/round-02-03.md#d-041--belonging-to-a-sub-unit-is-a-participation-record-not-a-membership),
[D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)).
**What an imported event does owe, since D-102, is the per-event instantiation of the seeded
answers-view grant** — one insert beside the event row, in the same transaction, or the imported event has
nobody who can read its answers.

**Never an open-ended membership, and never one inferred from an attendance row.** The reason is D-039 and it has not moved — an
open membership satisfies `is_current_member()`, so an inferred 1998 row hands whoever signs up under that
name authority in the present, through every gated role, decades after the file that mentioned them was
last opened. The end-date rule above is what stops an imported period from reading as current; this
sentence is what stops the class, and check 1 in §5 is what catches a batch that did it anyway. **What
changed is how much of the class the rule has to cover, not whether it covers it.** D-090 banned the row
outright because the input looked like a roster and any membership in it would have been an inference;
D-093 withdrew the ban because the input states periods, and because the hazard the ban was sized for was
a *standing* one — an import that infers, run by whoever holds the file, repeatedly, for years — whereas
what is being decided is one reviewed batch, mapping read before it applies, on a corpus that will never
arrive twice. A rule sized for a recurring process is too strict for a one-time one, and the safety that
mattered was never the ban, it was the review. **The stakes were named in D-041 and D-039 before they were
resolved, and they are why what remains is a rule rather than a preference.**

**Both failure modes stay on the record, because the next import will be a third shape.** The rule once
hedged — import a participation, *unless* there is evidence of payment, in which case a membership may be
inferred — and was then stated as its opposite: **"a roster row makes a participation and nothing else;
`membership` rows come only from the current register."** Both were arguing against something real. The
hedge was a rule waiting to be misapplied by whoever found a dues column in a later file and read it as
permission. The flat ban was correct about rosters and wrong about the corpus: it generalised from *this file
has no money in it* to *no membership may arrive from a file*, and the corpus arrived with membership
periods in it.

**What this gives up, since it gives up something.** *"Did they pay?"* has no answer for any imported
period — no money arrives in either export, so there is no `fee_obligation` and no balance on these rows
at all ([07-finance.md §2](07-finance.md#2-minimal-provisional-shape)), and every cross-decade member
count is a mix of an export and a register distinguished only by `data_confidence` and `import_batch_id`.
**What remains given up is that the imported membership
is the source's claim about a status rather than a record of the act: nobody paid a fee in this system for
1998, and the row says *the organization's export said so*, which is the most the evidence supports.*
