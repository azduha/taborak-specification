# Data Model — Audit and Import

`audit_log`, `import_batch`, staging tables, and the redaction log.

`access_log` (the authorization audit trail) is in
[05-authorization.md](05-authorization.md#9-access_log). This document covers the
data-change audit trail, the legacy import pipeline, and erasure.

---

## 1. Two audit trails, and why both

| | `access_log` | `audit_log` |
|---|---|---|
| Records | Who did what, and by what authority | What a row's field values were before and after |
| Answers | "Who accessed this child's medical record, and were they allowed to?" | "When did this person's address change, and who changed it?" |
| Volume | Very high | High |
| Raised by | Application code, on every permission check and action | **Every write to an audited table, on every path** — §2.1 names who owes that write now that no trigger is defined anywhere |

Keeping them separate is deliberate. They have different retention needs, different query
patterns, and different access permissions. Merging them produces a table that is too
large to query and too sensitive to expose to anyone who needs one half of it.

---

## 2. `audit_log`

**Fields**

| Field | Kind | Notes |
|---|---|---|
| `id` | surrogate id | |
| `occurred_at` | timestamp, audit time | Default: now |
| `transaction_id` | integer, required | Default: the id of the enclosing transaction. Groups all changes made in one transaction, so a multi-table operation (approve a request → create a membership → open a unit participation) reads as one event rather than three unrelated ones |
| `actor_person_id` | reference to person, optional | Taken from the request context, not from the row. `NULL` for migrations, imports, and batch jobs |
| `actor_label` | text, optional | `system`, `migration:0042`, `import_batch:17` — for changes with no person actor. Otherwise a forensic gap |
| `operation` | text, required | One of: `insert`, `update`, `delete` |
| `table_name` | text, required | |
| `record_id` | surrogate id, required | The row that changed. No reference: the table is named per row, so it points at any table in the database |
| `changed_fields` | list of text | Which columns changed. Enables targeted history queries without parsing JSON |
| `old_values` | free-form jsonb, optional | **Redacted before insert.** See §2.2 |
| `new_values` | free-form jsonb, optional | **Redacted before insert.** See §2.2 |
| `on_behalf_of` | reference to person, optional | Set when the actor was acting for another person. Mirrors `access_log.on_behalf` (04-relationships.md §5) |
| `session_id` | text, optional | |
| `ip_address` | network address, optional | |
| `request_id` | text, optional | |

**Indexes**

- One row's history: table name and `record_id`, newest `occurred_at` first.
- One actor's actions, newest first.
- Everything in one transaction, by `transaction_id`.
- By time alone, newest first.
- Rows by a *member of* `changed_fields`. The targeted history queries ask "which rows
  changed this column", so the list has to be searchable element-wise rather than as a whole
  value.

### 2.1 The trigger

**The heading is kept because the obligation under it is unchanged; what changed is that nothing
in this repository defines a trigger any more.** A trigger used to be how this section guaranteed
its own rule, and D-072 removed it without removing the rule, so the rule is now stated as what
it is: **every insert and every update to an audited table writes exactly one `audit_log` row,
and the change and its audit row stand or fail together.** "The audit trail usually has it" is
not a version of this rule — the trail is how the organization answers "who changed this child's
address, and when?", and an answer that depends on which code path made the change is not an
answer. **The layer that owes it is the write itself, on every path**: the screens, the legacy
import, the yearly expiry sweep, a bulk reorganisation, and a row somebody corrects by hand.
Model-layer validation logs the intended path, which is the only path that was never at risk;
check 5 in §5 is the net under the rest, and it is a report, not a guard.

The steps below are what is owed, in the order that makes it safe. The order is a rule, not a
detail: the redaction step has to run before the write, and the "nothing changed" test has to run
before anything is spent on a row that would log noise.

1. Read the acting person and the on-behalf-of person from the request context
   (`app.current_person_id`, `app.on_behalf_of`); an unset or empty value means no actor,
   not an error.
2. On an **insert**, take the new row as the after-image.
3. On an **update**, take both the old and the new row, and work out the changed fields:
   the keys present in both images whose values differ, named in key order.
4. If that comparison found nothing, stop and write nothing — a no-op update must not log
   noise.
5. On a **delete**, take the old row as the before-image; there is no after-image.
6. Redact both images (§2.2). Never store sensitive values in the audit trail.
7. Write one audit row carrying: the actor and the on-behalf-of persons, the operation as
   lower-cased `insert`, `update` or `delete`, the table name, the record id taken from the
   new row and falling back to the old one, the changed fields, both redacted images, and
   the session id, ip address and request id from the request context.
8. Change nothing about the row being written. The audit row describes the change and never
   amends it — and it commits in the same transaction as the change. That togetherness is the
   property a trigger used to supply for nothing, and the one a logging step written beside the
   write has to supply deliberately.

**The obligation covers inserts and updates on** `person`, `membership`, `guardianship`,
`role_assignment` and `access_grant`; on `role` and `role_permission` — the role *tables*,
not just the assignments, because a role is runtime data the organization edits (D-052) and
editing one changes effective permissions for every holder at once with no assignment
written, so without these two tables the single largest privilege change available in the
system leaves no trace on any other audited row; and on every remaining business table — the
exact set is still open in §6, and the recommendation there is all of them. **There is nothing
left to attach this to, which changes what the sentence is and not what it covers.** It is the
list of tables for which a write path owes an audit row; a business table created next year is
inside it from the day it exists; and check 5 in §5 is what notices when the list and the write
paths drift apart.

> **`role` and `role_permission` are audited for a reason the other tables do not share.**
> Everywhere else, the audit log answers "who changed this record?". Here it answers the
> harder question the *next* incident will ask: **"what did role X grant on the date this
> decision was made?"** Because a role edit rewrites the meaning of every assignment that
> points at it, in place, there is no way to answer that from the assignments — the
> assignments did not change. The log is the only record of what the role said at the time.

**`DELETE` is intentionally outside the audited operations on business tables**, because
nothing in this data model is hard-deleted (see
[00-conventions.md](00-conventions.md#4-deletion-policy)). Staging tables do get deleted;
they are not audited. The absence is a consequence of the deletion policy rather than a gap in
the obligation above. **It is, however, true of ordinary operation and false of exactly one
moment**, and saying so is the honest version of the paragraph: §3's import revert *does*
hard-delete business rows — the `person`, `membership` and `unit_participation` rows a batch
created — and those rows were live, referenced and visible to real users before they went. So
**a revert writes audit entries for its deletes, naming the batch and the row it removed**, and
`DELETE` is outside the audited operations everywhere else only because there is no other path
that reaches a business row with a delete. That makes revert the one place the list in §5 check 5
cannot be derived from table names alone: an audited *operation* rather than an audited *table*,
which is why check 5's replacement assertion enumerates the paths that may delete, not just the
tables that may be written.

### 2.2 Redaction before logging

The redactor takes one table name and one row image and does this:

1. If there is no image at all, there is nothing to redact — return no value.
2. For each key in the redaction list — `secret_hash`, `notes`, `custody_arrangement`,
   `termination_note`, `rejection_note`, `status_note` — if the image carries that key,
   replace its value with the marker `«redacted»`. Keys the image does not have are left
   alone.
3. Return the image.

The rule is keyed on the field name and not on the table: the table name arrives with the
image, and the same list is applied wherever a listed key turns up.

> **An audit log that stores the data it audits is a second copy of the sensitive data,
> with weaker access controls and a longer retention period.** Redaction happens before the
> insert — never in a cleanup job that might not run.

**Which part of that sentence is a requirement, and which was a mechanism.** "In the trigger"
used to appear here, and D-072 deleted the trigger. What survives is the ordering, which is the
part with the teeth: redaction runs **on the way in**, so an unredacted value never exists in the
audit table. The trigger was one way to guarantee that; a code path that redacts, then writes, is
another; **a code path that writes and repairs afterwards is not that**, because for one
transaction the secret is in the log and readable, and because the repair is the cleanup job this
paragraph forbids. With no trigger there is nothing stopping the third option except whoever
writes it, which is why the sentence is now stated as a rule about ordering rather than about a
database feature. See
[00-conventions.md §8](00-conventions.md#8-personal-data-and-erasure) for what else the move to
generated schema took out of this section's defence in depth.

A second, shorter list — `notes` and `custody_arrangement` — is kept as the
*always-redacted* set: free-text fields that could plausibly contain medical or custody
information. Both are already in the list above, so today the second list records intent
rather than adding behaviour. `notes` is the usual offender: someone types a diagnosis into
a general notes field, and it is now in the audit trail forever. Consider whether
`person.notes` should exist at all.

### 2.3 History query

The full change history of one row is found by taking the `audit_log` rows for its table
name and record id, newest `occurred_at` first, and reading out when it happened, the
operation, which fields changed, the old and new values, and who did it — the actor's
person name where there is an actor, and `actor_label` where there is not.

---

## 3. Import pipeline

Six stages, from
[../domain/03-identity-and-legacy.md](../domain/03-identity-and-legacy.md#7-legacy-import-pipeline).
The guiding requirements: **idempotent**, **reversible per batch**, **never overwrites
self-registered data**, **preserves provenance**.

**`import_batch`** — one run of the pipeline, and the unit revert works on.

**Fields**

| Field | Kind | Notes |
|---|---|---|
| `id` | surrogate id | |
| `name` | text, required | |
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
| `parsed_unit_code` | text, optional | |
| `parsed_unit_name` | text, optional | |
| `parsed_period_from` | date, optional | |
| `parsed_period_to` | date, optional | Often NULL; see the inference rules below |
| `parse_status` | text, required | One of: `ok`, `warning`, `error`. Default `ok` |
| `parse_warnings` | list of text | For example `birth_date_year_only`, `unit_not_found`, `ambiguous_name`. Warnings do not block; errors do |
| `resolution` | text, optional | One of: `link_existing`, `create_new`, `discard`, `deferred` |
| `resolved_person_id` | reference to person, optional | |
| `resolved_by` | reference to person, optional | |
| `resolved_at` | timestamp, audit time, optional | |
| `resolution_note` | text, optional | |
| `applied` | boolean, required | Default false |
| `applied_person_id` | reference to person, optional | What this row created |
| `applied_membership_id` | reference to membership, optional | What this row created |
| `applied_participation_id` | reference to unit participation, optional | What this row created |
| `created_at` | timestamp, audit time | |

**Indexes**

- The staged rows of one parsed row.
- The review queue: parse status and resolution, restricted to rows with no resolution or a
  `deferred` one. Decided rows are not in it.
- Applied rows only.

### Reversibility

`staging_import_row` holding the three created ids is what makes per-batch revert possible.
Revert removes only what this batch created, and it runs in this order:

1. Take every staged row of the batch being reverted.
2. Undo what they created, **dependents first**: the `unit_participation` rows, then the
   `membership` rows, then the `person` rows — and a row the batch created outright is
   removed rather than merely amended.
3. Finally mark the staged rows themselves unapplied.

**Revert is only safe before live data references the imported rows.** Once a real person
has been linked, or an event attendance recorded against an imported membership, deleting
the row breaks it. Therefore:

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
*batches* needs the hash to be computed from the row's semantic content, not its position:

```
source_row_hash = sha256(
    normalise(given_name) || '|' ||
    normalise(family_name) || '|' ||
    coalesce(birth_date::text,'') || '|' ||
    coalesce(unit_code,'') || '|' ||
    coalesce(period_from::text,'')
)
```

Then a re-import of an overlapping roster produces rows that match already-applied ones,
and the pipeline can skip them. **The hash function must be stable** — changing it
invalidates every previously staged row. Version it if it must change.

### End-date inference

Imported rosters rarely state when a period ended. Three defensible options:

| Rule | Effect | Risk |
|------|--------|------|
| Leave `valid_to` NULL | Person appears to be current | **Wrong and dangerous** — inflates the member count, and an open `membership` also passes the permission gate (§3.1) |
| End at the end of the organizational year of the last roster the person appears in | Defensible, documented | May truncate a period that continued |
| End at the last date the person appears in *any* roster | Best fidelity, needs all rosters | Requires the complete dataset |

**Recommended default:** end at the end of the organizational year of the last roster in
which the person appears, marked `data_confidence = 'low'` and with a parse warning. Never
NULL.

### 3.1 What a roster actually evidences

A roster proves that someone **took part in a unit in a period**. It does not prove they paid
a fee, and under [D-041](../decisions/decision-log.md#d-041--belonging-to-a-sub-unit-is-a-participation-record-not-a-membership)
sub-unit belonging is a `unit_participation`, not a membership at all — which is the
row the import should create by default, and the row for which "the last date they appear"
is a genuinely good answer.

**The dangerous case is the inferred membership.** If the import *also* generates a
`membership` row for each historical participant — plausibly, because the fee was paid — then
an open-ended one from 1998 does something a participation row never does: it satisfies
`is_current_member()`, so a 2003 roster member would hold current member authority today
through every role that is gated. The end-date rule above is what prevents that, and check 1
in §5 is what catches it when the rule is not applied.

**Where the money is unknown, prefer participation.** Import a participation row with a
period, and leave the membership to be inferred only where there is evidence of payment —
a receipt, a ledger, a dues column. Erring toward participation loses a little fidelity in
"were they a member in 1998?" and removes an entire class of false-current-member.

---

## 4. Redaction log

**Fields**

| Field | Kind | Notes |
|---|---|---|
| `id` | surrogate id | |
| `person_id` | reference to person, required | The row is NOT deleted. The id survives so historical references resolve |
| `requested_at` | timestamp, audit time | Default: now |
| `requested_by` | reference to person, optional | |
| `legal_basis` | text, optional | `gdpr_art17`, `court_order`, `internal_policy` — required for accountability |
| `performed_at` | timestamp, audit time, optional | |
| `performed_by` | reference to person, optional | |
| `redacted_tables` | list of text | Which tables had values overwritten |
| `retained_reason` | text, optional | Why some data was kept. Membership periods and unit participation periods are organizational history, not personal data, and removing them would falsify records the organization may be obliged to keep. This field records that judgement per case |
| `note` | text, optional | |

**Rules**

- A redaction cannot record when it was performed without recording who performed it:
  `performed_at` without `performed_by` is illegal.

**Indexes**

- A person's redaction history.

**This log is the answer to "prove you honoured the erasure request".** It records what
was removed, when, on what legal basis, and — importantly — what was deliberately retained
and why. A redaction performed without a record is indistinguishable from a data loss
incident.

---

## 5. Integrity checks

**Invariants to verify**

- **Imported memberships with no end date.** Count `membership` rows that carry an
  `import_batch_id` and have no `valid_to`. Zero is the only acceptable answer: these are
  the rows that silently satisfy the permission gate, so this is a security check as much as
  a data-quality one (§3).
- **Imported people who were later merged away.** Count people whose `record_origin` is
  `legacy_import` and whose merge pointer is set. Non-zero is probably fine and worth an eye.
- **Batches left in a non-terminal state for a long time.** Count `import_batch` rows whose
  status is none of `applied`, `reverted`, `failed` and which were created more than 30 days
  ago; non-zero means a run somebody stopped steering.
- **Audit rows with no actor at all.** Count `audit_log` rows with neither an
  `actor_person_id` nor an `actor_label`; any non-zero count is a forensic gap.
- **Tables whose write path does not audit.** Compare the business tables this system has —
  staging tables excluded — against the maintained list of audited ones. Non-zero means a table is
  writing history that is never recorded. **Read this one carefully, because its meaning got worse
  rather than weaker.** While a trigger existed, a table was audited by being named in a trigger
  definition, and forgetting one was a decision somebody made in a migration and could see. Now a
  table is audited because the code that writes it calls the audit entry point, so **the list and
  the code are two artifacts that must agree and nothing forces them to** — which makes this report
  the entire control over the completeness of the audit trail, and the one check here that should
  alert rather than log. If it ever reports a table, the finding is not "some history is missing";
  it is "every change to that table since it was added is unrecorded, and that period cannot be
  reconstructed later." 
- **Redacted people with surviving personal data.** Count redacted people whose names are
  not the redaction marker and who still have a current contact point whose value is not
  redacted; non-zero means an erasure was left half done.

**Check 5 is worth automating as a test**, not just a nightly query — a test that reads the
table list in these documents and asserts every business table on it appears on the audited list,
since that is the nearest thing left to what asking the database used to answer. A new table
added without being put on that list is a silent, permanent hole in the audit trail — and it will
be discovered only when someone needs the history that was never recorded.

---

## 6. Open issues

- Which tables must be audited. Recommend: all business tables. The cost is storage; the
  cost of a gap is unbounded.
- Retention period for `audit_log` before archival to cold storage. Legal input required.
- Whether `audit_log` should be partitioned by month from the start (recommend yes, given
  the write volume and the multi-decade horizon).
- The definitive end-date inference rule for imported rosters
  ([§3.1](#31-what-a-roster-actually-evidences)) — needs your input on the organizational
  year boundary (tracked as [../open-questions.md](../open-questions.md) A-4).
- **Whether the import should create a `membership` at all** for a historical roster, or
  only a `unit_participation` ([§3.1](#31-what-a-roster-actually-evidences)). The safe
  default is participation-only; the alternative needs payment evidence per row.
- Exact redaction scope: which fields are personal data vs. organizational history (§4).
  Requires legal review.
- Whether `person.notes` should exist at all, given the redaction burden it creates.

All tracked in [../open-questions.md](../open-questions.md).
