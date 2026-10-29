# Data Model — Audit and Import: the redaction log, the integrity checks, open issues

`redaction_log`, the checks that run over both trails, and what is still outstanding. The trail the
redaction writes into is [§2](06-audit-and-import.md#2-audit_log); the batches the checks watch are
[§3](06a-import.md#3-import-pipeline).

**Section numbers are shared across the three parts** and never renumbered, because other pages cite
them by number and their anchors are built from them:
[06-audit-and-import.md](06-audit-and-import.md) holds §1–§2 (the two audit trails and the `audit_log`
table), [06a](06a-import.md) §3 (the legacy import pipeline), and
[06b](06b-redaction-and-checks.md) §4–§6 (the redaction log, the integrity checks, open issues).

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
| `redacted_tables` | list of text | Which tables had values overwritten — **and which had rows deleted.** `person_attribute` is erased by deletion rather than by overwriting ([00-conventions §4](00-conventions.md#4-deletion-policy)), so naming it here is what records that the erasure reached the person's descriptive data, and omitting it is indistinguishable from not having reached it |
| `retained_reason` | text, optional | Why some data was kept. **It has a standing answer to hold now.** Membership periods, fee obligations, payments and this anonymised `person` row are kept with no end date because they are the organization's own history, which is the judgement this field was built to carry and which, until [D-088](../decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short), nothing in these documents had actually made. What the field adds per case is that *this* erasure made it knowingly, and the reason for anything retained beyond the skeleton. The basis underneath the standing answer is an assumption pending legal review (§6), not settled law |
| `note` | text, optional | |

**Rules**

- A redaction cannot record when it was performed without recording who performed it:
  `performed_at` without `performed_by` is illegal.
- **An erasure must also rewrite the expressions that named the person, and say what it changed.**
  Since [D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)
  a hand-named person is a `PERSON(x)` leaf of `audience_operand`, and `selector_arg_id` carries no foreign
  key, so nothing refuses the deletion underneath it. **The failure is not a dangling row, it is an inverted
  grant:** a leaf that resolves to nobody is the empty set, and the empty set subtracts nothing, so an
  expression reading `EVERYONE - PERSON(x)` begins denying everybody the moment `x` is erased. So the erasure
  walks `audience_operand` for leaves naming that person, removes or rewrites them under the same
  `access_grant` guard that covers any other change to reach, **prints the resolved set before and after for
  every expression it touched** — the same report
  [D-104](../decisions/round-10b.md#d-104--a-permission-codes-last-segment-is-an-action-and-a-registry-that-prose-contradicts-is-a-fiction)
  adopted — and names `audience_operand` in `redacted_tables`, because a field that lists which tables the
  erasure reached is worth nothing if the one table where the person still appears is left off it. The nightly
  orphan scan in [05d-invariants-and-seed.md §11](05d-invariants-and-seed.md#11-invariants-to-verify) is the backstop for
  this, and is not the control: the control is the erasure path itself, because a scan that reports a grant
  denying everybody every night is a report somebody stops reading.

**Indexes**

- A person's redaction history.

**This log is the answer to "prove you honoured the erasure request".** It records what
was removed, when, on what legal basis, and — importantly — what was deliberately retained
and why. A redaction performed without a record is indistinguishable from a data loss
incident.

**Two clocks, and this log is where the permanent one gets written down.** An erasure now performs three
acts with three different lifetimes. It overwrites the person row's names and contact points,
immediately and irreversibly; it deletes the `person_attribute` rows, so that `redacted_tables` naming
that table is the only sentence left saying they existed; and it scrubs that person's values out of the
trail's payloads — out of rows which, since
[D-088](../decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short),
are scheduled to lose their payloads anyway (§2.2). **What an erasure does not do is touch
`membership`, `fee_obligation`, `payment`, or this row's `person_id`** — and the reason is now a stated
justification rather than nobody having decided when those rows end. That difference, between a rule
nobody defended and a rule with a reason attached, is exactly what `retained_reason` carries.

**This log is not subject to payload reduction, and that is a decision rather than an oversight.**
Reduction empties the payloads of rows past the window. A `redaction_log` row holds no values to empty —
a person id, a legal basis, a list of table names, and the reasoning — and it is the *evidence* that a
person's request was honoured, which is the class of statement D-088 chose to keep for the life of the
system when it chose to keep the skeleton. **Reaching this table with reduction would delete the proof of
an erasure in order to apply a policy about history, and those are not the same act.**

**For the descriptive part of a person's record this log is the only surviving record, by design.**
The attribute rows are deleted; the audit entries that quoted their values are scrubbed by the same act
(§2.2's mechanism two, which is the only direction in which a trail that must not be rewritten can
still be erased); and the codes they pointed at stay live because a code belongs to the organization
and not to the erased person
([09-attributes.md §6](09-attributes.md#6-erasure-retirement-and-the-audit-payload) draws the two
directions: retiring a code is an act about the vocabulary and keeps values, erasing a person is an act
about the person and removes them). So `redacted_tables` naming `person_attribute` is the whole of what
the system can honestly say — *this person had descriptive data and it is gone* — and it is enough,
because the sentence the organization is entitled to keep is that it held a record and removed it, not
what the record said.

---

## 5. Integrity checks

**Invariants to verify**

- **Imported memberships with no end date.** Count `membership` rows that carry an
  `import_batch_id` and have no `valid_to`. Zero is the only acceptable answer: these are
  the rows that silently satisfy the permission gate, so this is a security check as much as
  a data-quality one (§3). **Do not read this as a data-quality report any more, because since
  [D-093](../decisions/round-09.md#d-093--the-one-off-import-may-create-memberships-both-ends-dated)
  it is the only thing standing between an imported row and the membership gate.** While imports made
  participations this check was theoretical — there were no imported memberships to find — and it is now
  the load-bearing one, since the corpus is expected to create thousands of rows that would each satisfy
  `is_current_member()` if their end date were missing.
  **Its sibling is re-pointed rather than removed.** The previous round's version, from
  [D-090](../decisions/round-07-08.md#d-090--the-legacy-corpus-is-thousands-of-roster-rows-with-numbers-and-no-money),
  read "an imported membership from a batch whose source is a roster, whatever its dates say", and that
  finding no longer exists as a finding — imported memberships are expected now. What replaces it is the
  surviving half of the same ban (§3.1): **count a `membership` carrying an `import_batch_id` whose
  `batch_kind` is `events`.** An attendance export states presence, and a membership drawn from one is the
  inference somebody re-enabled because they found a column that looked like dues. Run both halves on the
  same report: the first catches a missing end date, the second catches the wrong kind of source.
- **Imported people who were later merged away.** Count people whose `record_origin` is
  `legacy_import` and whose merge pointer is set. Non-zero is probably fine and worth an eye.
- **Batches left in a non-terminal state for a long time.** Count `import_batch` rows whose
  status is none of `applied`, `reverted`, `failed` and which were created more than 30 days
  ago; non-zero means a run somebody stopped steering.
- **Audit rows whose actor names nothing.** The trail has three ways to say *who did this*: a person, a
  registered integration ([05e-keys-and-callers.md §14](05e-keys-and-callers.md)), and — for the writers
  that have no row of their own — a label from the list in
  [00-conventions §7a](00-conventions.md#7a-what-an-empty-actor-column-means). The report runs over all
  three columns, because a version of it that looked only at `actor_person_id` and `actor_label` would
  count every integration write as a finding until whoever reads it stopped reading. **What it no longer
  counts as a gap is the shape it was built to count.** A row naming no person and no key is not a row that
  failed to answer *who did this*: §7a reads it as this system acting on its own, and the renewal sweep,
  payload reduction, the bank statement pull and a named migration write rows in exactly that shape,
  correctly and by design ([00-conventions §7](00-conventions.md#7-standard-columns)). Two things are
  reported instead. **(a) A row whose `actor_label` is not one of the labels §7a lists, including a row
  naming no person, no key and no label at all** — the vocabulary is a documented list and not a table, so
  nothing in the database refuses a label from outside it and this count is the only thing that ever notices
  ([D-125](../decisions/round-17.md#d-125--an-empty-actor-column-is-this-system-acting-on-its-own-and-its-name-comes-from-a-fixed-list)).
  A row that reaches the trail with nobody and nothing in it has not joined that list, which is the failure
  the list exists to catch. **(b) A row on a write path that owed a person and named none**, in the two
  shapes a reader can actually test: a transaction whose request context carried a `current_person_id`
  ([06 §2.1 step 1](06-audit-and-import.md#21-the-trigger)) while `actor_person_id` stayed empty, and any audit row about one of the rows §7a names as
  having no empty to interpret — `import_batch.created_by` and `api_key.created_by` are required and a
  grant's `granted_by` names a person, so a business row that cannot lawfully be authorless cannot have
  been written by a writer that is.
  **What this check cannot catch, said because two rows a reader would want are not among them.** A row
  naming a key *and* a person — the row a forensic reader most wants flagged — is never reported here.
  It is illegal, and the rule carried by the two columns is what refuses it
  ([05e-keys-and-callers.md §16](05e-keys-and-callers.md),
  [D-121](../decisions/round-16.md#d-121--a-key-never-carries-a-persons-authority)); a count over empty
  columns cannot see a row whose columns are full. A row naming a key that no longer exists is stopped
  before any count runs: `audit_log.api_key_id` is an ordinary reference and not one of the two
  reference-less keys, and no key row is hard-deleted
  ([00-conventions §4](00-conventions.md#4-deletion-policy)). What stays uncounted, and uncounted
  everywhere in this section, is the pair no rule compares — a write audited against a key whose
  `valid_to` or `revoked_at` fell *before* the row's `occurred_at`, which leaves every column filled and
  this check, which reads emptiness rather than dates, silent.

  **That silence is now a ruling rather than an oversight, and the reason matters more than the ruling**
  ([D-133](../decisions/round-19.md#d-133--two-trail-rules-stay-unchecked-and-say-so-out-loud)). **The
  window is not the obstacle and it was never honest to say it was**: the three columns such a check would
  compare are `api_key.valid_to`, `api_key.revoked_at` and this table's own `occurred_at`, every one of them
  accounting skeleton, every one outliving the payload by decades. A report could be written over them
  tomorrow and would work in year thirty. **What was decided is that it will not be written**, which leaves
  the design without a guarantee it had been reading as though it had: nobody will be able to demonstrate
  that no write was ever audited against a key that had already ended, and no count anywhere will ever
  answer that question — not after 24 months, and not before them either. **What this section does hold, and
  what the sentence above should never be read as replacing**, is narrower and worth restating while it is
  being narrowed: every audited write left a row; that row's envelope — actor, table, record, moment — is
  intact for as long as the row exists; and the payload is emptied on schedule rather than lingering. Those
  three are checked. The fourth was wanted by nobody who read it, so it is stated as a rule with no report
  beneath it, which is the only remaining honest state — and
  [00a](00a-invariant-register.md) now says so in the same words this page does, because a register row
  claiming a report that no page has is the defect D-129 exists to catch. A reader who needs the fourth
  guarantee needs a different instrument than this table: the trail is a record of what happened to people,
  and what an ended key did after it ended is tracked on the key's own page
  ([05e-keys-and-callers.md](05e-keys-and-callers.md)).
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
  redacted; non-zero means an erasure was left half done. **The count now reaches two more places.**
  First, `person_attribute`: a redacted person with **any** attribute row is an erasure that did not
  happen, since those rows are deleted rather than overwritten
  ([00-conventions §4](00-conventions.md#4-deletion-policy)). That is check 6 of
  [09-attributes.md §8](09-attributes.md#8-integrity-checks) read from this side — the same assertion,
  not a second one. **Second, and a different assertion, which only exists because values are logged
  on purpose: for a redacted person, no `audit_log` row about one of their `person_attribute` changes
  may still carry content.** Content means `value`, `value_option_id` or `recorded_note` inside
  `old_values` or `new_values`; `person_id`, `attribute_definition_id` and `source` are not content and
  survive the scrub deliberately, because they are the only way this check can still find the rows after
  the erasure deleted the business ones — an audit row keeps its `table_name` and `record_id` when the
  row they named is gone, and its `person_id` is what ties it back to the person who asked to be
  forgotten. Read this check correctly and it has exactly one meaning: **the scrub did not run.** Before
  an erasure, a payload full of descriptive values is the design working
  ([§2.2](06-audit-and-import.md#22-redaction-before-logging)); afterwards it is the thing the person asked for the system to
  stop having. Note what the check structurally *cannot* see — a copy that is present, readable, and
  perfectly legal, held by somebody whose permission is graded below its contents — because that failure
  leaves no rows to count; it is the guard, and the guard is reviewed by a person.
  **This check, check 5 and check 7 are the three here that should alert rather than log.** A redaction
  property that is reported once a month is a redaction property that fails between the reports, and
  unlike a missing audit row, a value that outlives its erasure is not something anyone notices until a
  regulator asks what the table holds.
- **An audit row past the payload window that still carries a payload.** Count `audit_log` rows whose
  `occurred_at` is older than the retention window and whose `old_values` or `new_values` still holds
  anything. **This is check 6's mirror, and merging the two is the way to lose both.** Check 6 asks
  whether an *erasure* ran, fires on one person's rows, and fails as a right not honoured; this one asks
  whether the *calendar* ran, fires on everybody's rows alike, and fails as a policy not applied
  (§2.2's three operations, which fail in different directions). A system passes one while failing the
  other in both directions, so they are two queries, not one query with two clauses.
  **It alerts rather than logs, and the reason is the one §2.2 gives: reduction's failure mode is not
  running.** Nothing about the trail looks wrong from inside it — a reduced row and a row that escaped
  reduction both still answer *who, what, when*, which is the half that was supposed to survive — so the
  only difference between them is a payload nobody looks at until somebody with `audit.view` opens a
  history screen and finds a child's allergy list still sitting there past the window it was meant to
  have left. **Count the rows, do not sample them**: a job that stopped after the newest partition keeps
  the oldest rows full and looks entirely healthy to a sample. And read the window from the same place
  the job does, because a check holding one value and a job holding another reports clean forever, which
  is the exact failure this check exists to prevent and the one it can cause by itself.

- **A change the trail never saw: an audited row whose newest audit row predates its own `updated_at`.**
  For every table [06 §2.1](06-audit-and-import.md#21-the-trigger) obligates, take each row's `updated_at`
  and the newest `occurred_at` among the audit
  rows naming that table and `record_id`, and report the rows where the change is newer than the trail's
  knowledge of it. **It exists because of the one write this design performs outside the application**: the
  recovery in the break-glass procedure un-suspends an account or re-issues a credential by hand, produces
  no audit row, and leaves a row that is live, referenced and invisible to every other check in this section
  ([domain/02-actors.md §3](../domain/02-actors.md#when-nobody-who-can-hold-systemadmin-can-sign-in),
  [D-126](../decisions/round-17.md#d-126--break-glass-is-a-report-and-a-written-procedure-not-a-mechanism)).
  **It can see the recovery at all because `account` is a business table**, and a business table owes an
  audit row on every insert and update ([06 §2.1](06-audit-and-import.md#21-the-trigger)); which tables
  those are is a recommendation awaiting confirmation (§6), and that is this report's real ceiling —
  **a table nobody confirmed is a table this check reads as never changing.**
  Nothing in the schema distinguishes a legitimate recovery from somebody editing a row they had no business
  editing, so this is a report and not a guard, like every item above it. **What it cannot catch.** An edit
  that also inserts its own audit row by hand — the trail is append-only to the application, not to whoever
  holds the database. And an edit that leaves `updated_at` alone, which is the quieter half of the blind
  spot: [00-conventions §7](00-conventions.md#7-standard-columns) is explicit that nothing maintains
  `updated_at` unless somebody says so, so **this report is exactly as wide as whatever maintains that
  column**, and an application that sets it only on its own screens narrows it to those screens. **What it
  does not lose to payload reduction:** reduction empties `old_values` and `new_values` and keeps the row
  ([D-088](../decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)),
  and a reduced row keeps its `occurred_at` — so 24 months after the values went, this check still has both
  timestamps to compare. Coverage outlives content by design, which is the one part of this list that gets
  no worse with age.

**Check 5 is worth automating as a test**, not just a nightly query — a test that reads the
table list in these documents and asserts every business table on it appears on the audited list,
since that is the nearest thing left to what asking the database used to answer. A new table
added without being put on that list is a silent, permanent hole in the audit trail — and it will
be discovered only when someone needs the history that was never recorded.

---

## 6. Open issues

- Which tables must be audited. Recommend: all business tables. The cost is storage; the
  cost of a gap is unbounded. Still open as a *decision*, closed as a *recommendation* — §2.1
  already obligates every business table, so what is actually outstanding is somebody
  confirming the list rather than deriving it.
- **Retention period for `audit_log` — decided as policy, still open as law**
  ([D-088](../decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)).
  It used to read "retention period before archival to cold storage; legal input required", which got the
  question wrong in two ways at once: it assumed the answer was a storage tier rather than a *shape*, and
  it assumed one clock rather than two. The policy is now **rows forever, payloads 24 months, 12 months
  as the floor a window may be set to**, enforced by the job and the check in §2.2 and §5 rather than by
  an archive nobody queries. What remains open is the half a decision log cannot settle: whether the
  indefinite retention of *named* `membership` and `fee_obligation` rows has a lawful basis. That is
  recorded as an assumption with a name attached
  ([../open-questions.md](../open-questions.md#i-assumption-index)), not as settled law, and the review
  now has a concrete policy in front of it instead of a blank.
- Whether `audit_log` should be partitioned by month from the start. **Recommend yes, and the reasons
  changed when the payload window arrived.** The old reason was "the write volume and the multi-decade
  horizon", which is still true of the *rows* — they are the permanent half — but the bulk of a row is
  its payloads, and those are now on a 24-month clock. Monthly partitions serve the reduction job too: a
  partition entirely past the window can be reduced as one unit rather than as a sweep across a table
  that grows for the life of the system. The open part is which the deployment does first, not whether
  the horizon justifies it.
- The definitive end-date inference rule for imported membership periods
  ([§3.1](06a-import.md#31-what-a-source-row-actually-evidences)) — needs your input on the organizational
  year boundary (tracked as [../open-questions.md](../open-questions.md) A-4). **Sharper, not smaller,
  since [D-093](../decisions/round-09.md#d-093--the-one-off-import-may-create-memberships-both-ends-dated)
  put memberships back on the receiving end of it:** the inferred end date is not the end of a record nobody
  reads, it is the `valid_to` of a row that gates authority, so the year boundary is the value
  standing between the import and the permission gate. (When this bullet was written the row in question was a
  `unit_participation`; [D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)
  removed that table, which sharpens the point rather than softening it — there is now exactly one period an
  inferred date can be ending, and it is the consequential one.)
- **✅ Resolved — whether the import should create a `membership` at all** for a historical period, or
  only a `unit_participation` ([§3.1](06a-import.md#31-what-a-source-row-actually-evidences)). Settled by
  [D-090](../decisions/round-07-08.md#d-090--the-legacy-corpus-is-thousands-of-roster-rows-with-numbers-and-no-money)
  on the shape of the corpus rather than on the merits of the two options — the corpus carried no payment
  data, so the exception arm of "participation unless there is payment evidence" had an empty set to fire
  on — and **then narrowed by
  [D-093](../decisions/round-09.md#d-093--the-one-off-import-may-create-memberships-both-ends-dated),
  which is what this bullet now records: the corpus turned out to state membership periods, so a bounded
  membership may be imported, both ends dated, `data_confidence = 'low'`.** What the resolution actually
  settled was never "no imported memberships" but "no inferred ones", and that half still holds in both
  directions: never open-ended, never from an attendance row. **Superseded here and kept visible: this
  bullet used to end "participation only, always; `membership` rows come only from the current register."**
- **Not a question, because the answer that split the corpus already answered it: a batch types itself**
  (`import_batch.batch_kind`, §3). Two halves of corpus mean two shapes of row, and one `field_mapping`
  cannot serve both — an events export has no column that maps to an attribute code and a people export has
  nothing to map to a registration. Recording it as an open question would invite somebody to answer it
  with the larger alternative (one batch, two mappers that can never both apply), which the answer in D-092
  explicitly passed over as the bigger change.
- Exact redaction scope: which fields are personal data vs. organizational history (§4). Requires legal
  review — **much narrower than it was, and still not closed.** D-083 removed the *category* question
  (there is no specially-graded subset of the person record), and
  [D-088](../decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)
  has since drawn the *line*: identity and descriptive values are erased, the accounting skeleton is
  retained, and the trail's payloads expire. What the review is asked about is therefore no longer "which
  fields" but "on what basis does the retained half survive indefinitely" — one question about one list,
  which is the item above.
- Whether `person.notes` should exist at all, given the redaction burden it creates.

All tracked in [../open-questions.md](../open-questions.md).
