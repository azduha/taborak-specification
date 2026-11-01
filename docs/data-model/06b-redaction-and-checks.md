# Data Model — Audit and Import: the redaction log, the integrity checks, open issues

`redaction_log`, the checks that run over both trails, and what is still outstanding. The trail the
redaction writes into is [§2](06-audit-and-import.md#2-audit_log); where the legacy import pipeline used
to be, and what replaced it, is [§3](06-audit-and-import.md#3-import-pipeline--deleted).

**Section numbers are shared across the two parts** and never renumbered, because other pages cite
them by number and their anchors are built from them:
[06-audit-and-import.md](06-audit-and-import.md) holds §1–§3 (the two audit trails, the `audit_log`
table, and a tombstone where the import pipeline was), and
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
| `retained_reason` | text, optional | Why some data was kept. **It has a standing answer to hold now.** Membership periods, fee obligations, payments and this anonymised `person` row are kept with no end date because they are the organization's own history, which is the judgement this field was built to carry and which, until [D-088](../decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short), nothing in these documents had actually made. What the field adds per case is that *this* erasure made it knowingly, and the reason for anything retained beyond the skeleton. **The judgement underneath the standing answer is the designer's own** — [D-205](../decisions/round-24.md#d-205--there-is-no-legal-review-and-assumption-49-is-retired) retired the review that would have settled it, so what the standing answer carries is its risk (these are the one class of row that outlives every safeguard in [00-conventions §8](00-conventions.md#8-personal-data-and-erasure), and nothing outside the design vouches for them) where a basis used to sit (§6) |
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

- **No longer a count: an imported membership with no end date.** Two counts stood here — a `membership`
  carrying an `import_batch_id` with no `valid_to`, and its sibling, one whose batch was an events export — and
  both die with the column and the batch
  ([D-190](../decisions/round-23.md#d-190--the-legacy-import-is-a-script-and-a-key-and-the-pipeline-is-gone)).
  **The rule underneath them is untouched.** An imported membership is never open-ended and never inferred from
  an attendance row; it ends with the calendar year the person was last seen in, and the value written is
  1 January of the following year because every period here is half-open
  ([D-169](../decisions/round-22.md#d-169--an-imported-membership-ends-with-the-calendar-year-it-was-seen-in),
  [D-093](../decisions/round-09.md#d-093--the-one-off-import-may-create-memberships-both-ends-dated)).
  **What is gone is the report, and a hole whose report is gone should be written down rather than quietly
  unstated.** Its shape: a `membership` row with `valid_to` empty whose `audit_log` row names the load's key.
  That is authority and not untidiness — an open membership satisfies `is_current_member()` and so walks
  through the permission gate ([D-039](../decisions/round-02-03.md#d-039--member-permissions-require-a-current-paid-membership))
  — and the answer to "who would notice" is: whoever reads the load's output, on the one occasion there will
  be a load's output to read. Nothing reads it on their behalf, and nothing in this design would tell them if
  it did ([D-164](../decisions/round-22.md#d-164--nobody-is-told-and-no-page-may-say-otherwise)).
- **Imported people who were later merged away.** Count people whose `record_origin` is
  `legacy_import` and whose merge pointer is set. Non-zero is probably fine and worth an eye.
- **No longer a count: a batch left in a non-terminal state.** This bullet policed runs that had stalled
  midway through six stages, and there are no stages, no statuses and no queue
  ([D-190](../decisions/round-23.md#d-190--the-legacy-import-is-a-script-and-a-key-and-the-pipeline-is-gone)).
  **The two bullets in this list that named the pipeline are emptied rather than deleted, and a later editor
  should leave them standing:** the checks below them keep the positions the rest of the corpus counts them
  by, and an emptied bullet is a visible hole where a renumbering is an invisible one.
- **Audit rows whose actor names nothing.** The trail has three ways to say *who did this*: a person, a
  registered integration ([05e-keys-and-callers.md §14](05e-keys-and-callers.md)), and — for the writers
  that have no row of their own — a label from the list in
  [00-conventions §7a](00-conventions.md#7a-what-an-empty-actor-column-means). The report runs over all
  three columns, because a version of it that looked only at `actor_person_id` and `actor_label` would
  count every integration write as a finding until whoever reads it stopped reading. **What it no longer
  counts as a gap is the shape it was built to count.** A row naming no person and no key is not a row that
  failed to answer *who did this*: §7a reads it as this system acting on its own, and the renewal sweep,
  payload reduction, the access trail's age-out, the bank statement pull and a named migration write rows in
  exactly that shape, correctly and by design ([00-conventions §7](00-conventions.md#7-standard-columns)).
  **The age-out's row is new rather than always having been there**, and it is one row per run rather than one
  per deleted row ([D-184](../decisions/round-23.md#d-184--every-table-is-audited-and-the-delete-carve-out-names-the-moments-that-survive)):
  before it, `system:log-reduction` was a name on a vocabulary and on no row at all. Two things are
  reported instead. **(a) A row whose `actor_label` is not one of the labels §7a lists, including a row
  naming no person, no key and no label at all** — the vocabulary is a documented list and not a table, so
  nothing in the database refuses a label from outside it and this count is the only thing that ever notices
  ([D-125](../decisions/round-17.md#d-125--an-empty-actor-column-is-this-system-acting-on-its-own-and-its-name-comes-from-a-fixed-list)).
  A row that reaches the trail with nobody and nothing in it has not joined that list, which is the failure
  the list exists to catch. **(b) A row on a write path that owed a person and named none**, in the two
  shapes a reader can actually test: a transaction whose request context carried a `current_person_id`
  ([06 §2.1 step 1](06-audit-and-import.md#21-the-trigger)) while `actor_person_id` stayed empty, and any audit row about one of the rows §7a names as
  having no empty to interpret — `api_key.created_by` is required and a
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
- **Tables whose write path does not audit.** Take every table this system has, set the two trails aside —
  `audit_log` and `access_log` are the only tables the obligation excludes — and report any table that has a
  write path and produced no audit row. **There is no maintained list of audited tables left to compare
  against:** [D-184](../decisions/round-23.md#d-184--every-table-is-audited-and-the-delete-carve-out-names-the-moments-that-survive)
  turned the obligation into a rule about writes, so one half of this comparison is the schema and the other is
  the code. **Read this one carefully, because its meaning got worse
  rather than weaker.** While a trigger existed, a table was audited by being named in a trigger
  definition, and forgetting one was a decision somebody made in a migration and could see. Now a
  table is audited because the code that writes it calls the audit entry point, so **the rule and
  the code are two artifacts that must agree and nothing forces them to** — which makes this report
  the entire control over the completeness of the audit trail, and the one check here whose
  finding must not wait for the monthly run. If it ever reports a table, the finding is not
  "some history is missing"; it is "every change to that table since it was added is unrecorded, and
  that period cannot be reconstructed later."
  **Because the obligation is now a rule rather than a list, the assertion carries one enumerated list still:
  the paths that may delete.** [§2.1's carve-out](06-audit-and-import.md#21-the-trigger) names two, and a
  table-name comparison yields neither — **erasure**, which deletes `person_attribute` rows and audits nothing
  per row, and **the access trail's age-out**, which deletes from a table the obligation excludes and yet
  writes the one summary row. A delete reaching any other table is this report's finding even when that table
  audits its inserts and updates perfectly, and it is the finding a test should assert rather than a query,
  since nothing in the schema refuses the delete.
- **Redacted people with surviving personal data.** Count redacted people whose names are
  not the redaction marker and who still have a current contact point whose value is not
  redacted; non-zero means an erasure was left half done. **The count now reaches three more places, and the three
  fail in two different shapes.**
  First, `person_attribute`: a redacted person with **any** attribute row is an erasure that did not
  happen, since those rows are deleted rather than overwritten
  ([00-conventions §4](00-conventions.md#4-deletion-policy)). That is check 5 of
  [09-attributes.md §8](09-attributes.md#8-integrity-checks) read from this side — the same assertion,
  not a second one.
  **Second, and its shape is the opposite on purpose: `event_answer`.** A redacted person with an answer row
  still carrying a `value` is an erasure that stopped short of the event tables. Those rows are **not**
  deleted — nothing about an event goes on a schedule, and an answer outlives its event indefinitely — so
  erasure **overwrites**: `value` emptied, and `answered_at`, `answered_by` and the row itself kept, because
  *they were asked and they answered* is the event's fact while *this is what they said* is the person's
  ([D-140](../decisions/round-20.md#d-140--nothing-about-an-event-is-deleted-on-a-schedule-and-erasure-empties-an-answer-without-deleting-it)).
  **`value` is the whole of the content here**, since an answer is one typed value rather than a column per
  type ([08-events.md §7](08-events.md#7-event_question-and-event_answer)) — there is no second field that
  survives an emptied value by holding the answer in another shape, which is the trap a check like this
  would otherwise set for itself. **`event_registration` is counted by nothing here, and that is not an
  oversight:** whether a person came is organizational history rather than something to withdraw,
  [00 §8's item 2](00-conventions.md#8-personal-data-and-erasure) says so by name, and a check that reported
  surviving registrations would be reporting the design working.
  **Third, and a different assertion, which only exists because values are logged
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
  **This check, check 5, check 7 and check 8 are the four here whose findings cannot wait for the
  monthly run** — three because a value that outlives the rule about it is not something a schedule
  notices, and check 8 because it is the same failure wearing the other trail's clothes. **Nothing in
  this design sends any of them to anybody**, so "cannot wait" names a duty to open these four rather
  than a message that arrives on its own
  ([D-164](../decisions/round-22.md#d-164--nobody-is-told-and-no-page-may-say-otherwise)).
  A redaction property that is reported once a month is a redaction property that fails between the
  reports, and unlike a missing audit row, a value that outlives its erasure is not something anyone
  notices until a regulator asks what the table holds.
- **An audit row past the payload window that still carries a payload.** Count `audit_log` rows whose
  `occurred_at` is older than the retention window and whose `old_values` or `new_values` still holds
  anything. **This is check 6's mirror, and merging the two is the way to lose both.** Check 6 asks
  whether an *erasure* ran, fires on one person's rows, and fails as a right not honoured; this one asks
  whether the *calendar* ran, fires on everybody's rows alike, and fails as a policy not applied
  (§2.2's three operations, which fail in different directions). A system passes one while failing the
  other in both directions, so they are two queries, not one query with two clauses.
  **Its finding cannot wait for the monthly run, and the reason is the one §2.2 gives: reduction's
  failure mode is not running.** Nothing about the trail looks wrong from inside it — a reduced row and a row that escaped
  reduction both still answer *who, what, when*, which is the half that was supposed to survive — so the
  only difference between them is a payload nobody looks at until somebody with `audit.view` opens a
  history screen and finds a child's allergy list still sitting there past the window it was meant to
  have left. **Count the rows, do not sample them**: a job that stopped after the newest partition keeps
  the oldest rows full and looks entirely healthy to a sample. And read the window from the same place
  the job does, because a check holding one value and a job holding another reports clean forever, which
  is the exact failure this check exists to prevent and the one it can cause by itself.

- **An `access_log` row older than the window that is still there.** Count rows whose `occurred_at` predates
  the window and which still exist.
  **[This is check 7's sibling and deliberately not its copy](../decisions/round-20.md#d-145--access_log-rows-are-deleted-at-24-months-and-the-job-that-does-it-has-a-name).**
  Check 7 counts payloads that should have been emptied out of rows that stay; this one counts **rows that
  should be gone**, on the other trail. Same clock, opposite operation — and merging them into one
  "anything past 24 months" report is how both are lost, because the two findings are repaired by two
  different jobs, one of which is an update and the other a delete, and because a single count cannot say
  which half of the retention policy stopped. **The direction of failure is the same, and it is the reason
  this finding cannot wait for the monthly run**: a job that stopped leaves a trail that looks entirely
  sound from inside it, since nothing about a growing table reads as a promise broken. The only difference between it
  and a healthy one is rows accumulating past the date the design said they would not exist, and the person
  who notices is the one asked what the system holds about them.
  **Count, do not sample**, for exactly the reason check 7 gives: a job that stopped after the newest
  partition keeps the oldest rows and passes any sample drawn from the top. **And read the window from the
  same configuration the job reads** — this is the second check that can be permanently satisfied by a
  disagreement between two copies of one number, and it is the failure mode each of them would cause alone.
  **What it cannot do is demonstrate that anything was ever deleted.** It counts what remains, which is the
  only thing a count over a table can see, so a job that deletes from the wrong table passes it; the
  standing guarantee here is not this report but the one on the other side of it, that the change trail is
  never pruned ([05c §9](05c-access-log-and-resolver.md#9-access_log)). **This delete is one of the two named
  exceptions to [00 §4](00-conventions.md#4-deletion-policy),** and the only one driven by a calendar rather
  than by a person asking — and since [D-184](../decisions/round-23.md#d-184--every-table-is-audited-and-the-delete-carve-out-names-the-moments-that-survive)
  it is also the only delete in the system that leaves a row in the other trail: one summary row per run,
  naming `system:log-reduction`, the count and the window.

- **A change the trail never saw: an audited row whose newest audit row predates its own `updated_at`.**
  For every table [06 §2.1](06-audit-and-import.md#21-the-trigger) obligates, take each row's `updated_at`
  and the newest `occurred_at` among the audit
  rows naming that table and `record_id`, and report the rows where the change is newer than the trail's
  knowledge of it. **It exists because of the one write this design performs outside the application**: the
  recovery in the break-glass procedure un-suspends an account or re-issues a credential by hand, produces
  no audit row, and leaves a row that is live, referenced and invisible to every other check in this section
  ([domain/02-actors.md §3](../domain/02-actors.md#when-nobody-who-can-hold-systemadmin-can-sign-in),
  [D-126](../decisions/round-17.md#d-126--break-glass-is-a-report-and-a-written-procedure-not-a-mechanism)).
  **It can see the recovery at all because `account` is a table the obligation covers**, and every table the
  application writes owes an audit row on every insert and update ([06 §2.1](06-audit-and-import.md#21-the-trigger)).
  **The set it walks is no longer a recommendation waiting to be confirmed:** §6's first bullet is closed, the
  scope is every table the application writes except the two trails, and nothing stands between that rule and
  this query. **What is left as its ceiling is this bullet's own sentence about `updated_at`,** which is a property
  of the application rather than of this document.
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
table list in these documents and asserts, for every table except the two trails, that whatever writes it
reaches the audit entry point, since that is the nearest thing left to what asking the database used to answer.
**The assertion lost its list and kept its shape.** It no longer asks *is this table on the audited list* —
there is no such list to be off — it asks *does every write path to this table write the row*, and it carries
the two enumerated delete paths beside it, because no enumeration of table names yields either. A new table
whose writer was never wired is a silent, permanent hole in the audit trail — and it will
be discovered only when someone needs the history that was never recorded.

---

## 6. Open issues

- **✅ Closed — which tables must be audited: every table the application writes**
  ([D-184](../decisions/round-23.md#d-184--every-table-is-audited-and-the-delete-carve-out-names-the-moments-that-survive)).
  The bullet asked for somebody to read a list and say yes, and the answer instead retired the list: one
  `audit_log` row per insert and update, on every path, from the day a table exists, with **the two trails
  themselves the only tables outside it** — `audit_log` and `access_log` are the record, and a record of a
  record would have to be recorded in its turn. **A confirmation was worth asking for even though §2.1 already
  claimed the answer**, because a scope written as *everything except the list we never finished* is a scope a
  new table falls out of by nobody noticing, and check 5's assertion that the list and the write paths agree
  had nothing correct to agree with. The cost is storage, and the growth is in the skeleton of a small fixed
  row rather than in a payload, since payloads empty at 24 months
  ([D-088](../decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)).
- **✅ Closed — retention period for `audit_log`: rows forever, payloads 24 months, and nobody is left to
  rule on it**
  ([D-088](../decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short),
  owned as a policy by
  [D-205](../decisions/round-24.md#d-205--there-is-no-legal-review-and-assumption-49-is-retired)).
  It used to read "retention period before archival to cold storage; legal input required", which got the
  question wrong in two ways at once: it assumed the answer was a storage tier rather than a *shape*, and
  it assumed one clock rather than two. The policy is **rows forever, payloads 24 months, 12 months
  as the floor a window may be set to**, enforced by the job and the check in §2.2 and §5 rather than by
  an archive nobody queries. **The half this bullet kept calling open is not open, because nothing is going
  to rule on it: there is no legal review of this design and there will not be one.** Whether the
  indefinite retention of *named* `membership` and `fee_obligation` rows is lawful is therefore decided the
  way everything else here is decided — chosen by the person designing the system because the alternative
  falsifies the organization's own history — and the risk sits where the basis used to sit: **this is the
  one class of row here that outlives every safeguard in
  [00-conventions §8](00-conventions.md#8-personal-data-and-erasure), and nothing outside the design vouches
  for it.** **Five policies stand as decisions of the person designing the system, and they are the five
  D-205 lists:** these rows kept with no end date; the audit payloads emptied at 24 months; the
  `access_log` rows deleted at 24 months
  ([D-145](../decisions/round-20.md#d-145--access_log-rows-are-deleted-at-24-months-and-the-job-that-does-it-has-a-name));
  **that a child may hold an account with no guardian's answer recorded anywhere**
  ([D-166](../decisions/round-22.md#d-166--an-account-is-not-where-authority-over-a-child-lives),
  [domain/02 §2](../domain/02-actors.md#minor-registration)); and what an **invoice** must contain and how
  long it is kept
  ([D-198](../decisions/round-24.md#d-198--an-invoices-issuer-is-configuration-its-payers-identification-is-already-in-the-database)).
  The second and third are this system's own clocks; the first and fourth are the two a data subject asks
  about, and the fourth is the only one of the five that this design answers by *not holding a record at
  all*; the fifth is decided by saying what the row is — an `invoice` row is the record that a document
  exists, and whatever must be printed beyond what this design holds is met outside it.
- Whether `audit_log` should be partitioned by month from the start. **Recommend yes, and the reasons
  changed when the payload window arrived.** The old reason was "the write volume and the multi-decade
  horizon", which is still true of the *rows* — they are the permanent half — but the bulk of a row is
  its payloads, and those are now on a 24-month clock. Monthly partitions serve the reduction job too: a
  partition entirely past the window can be reduced as one unit rather than as a sweep across a table
  that grows for the life of the system. The open part is which the deployment does first, not whether
  the horizon justifies it.
- **✅ Closed — the end-date inference rule for imported membership periods**
  ([§3](06-audit-and-import.md#3-import-pipeline--deleted)). An imported membership ends with the
  calendar year of the last period in which the person appears: their last day as a member is 31 December,
  and the value written into `valid_to` is **1 January of the following year**, because every period here is
  half-open and current membership is read as `valid_to` *after* today — a literal 31 December in that
  column would end every imported row one day early and look correct in every report that does not name the
  day ([D-169](../decisions/round-22.md#d-169--an-imported-membership-ends-with-the-calendar-year-it-was-seen-in)).
  **The boundary was never missing, and that is the part worth keeping:** [D-047](../decisions/round-04.md#d-047--the-fee-expires-on-1-january)
  put it in `membership_type` as `expiry_month` and `expiry_day`, and that row's own note says the
  organizational year runs with the calendar — the four words this bullet asked for were sitting in the row
  the date is read from, which is also why the day is read from those two columns rather than compiled into
  a job as a literal. **Sharper, not smaller,
  since [D-093](../decisions/round-09.md#d-093--the-one-off-import-may-create-memberships-both-ends-dated)
  put memberships back on the receiving end of it:** the inferred end date is not the end of a record nobody
  reads, it is the `valid_to` of a row that gates authority, so the year boundary is the value
  standing between the import and the permission gate. (When this bullet was written the row in question was a
  `unit_participation`; [D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)
  removed that table, which sharpens the point rather than softening it — there is now exactly one period an
  inferred date can be ending, and it is the consequential one.)
  **What the pipeline's removal did not touch is the date itself.** It is a rule about the rows a script
  writes now, not about a parse step inside a stage, and the value is read from `expiry_month` and `expiry_day`
  on the `membership_type` row wherever the load computes it. What died with the stages is the report that
  would have noticed a load ignoring it (§5's first bullet), so this bullet is the only place left where the
  date is written down in full.
- **✅ Resolved — whether the import should create a `membership` at all** for a historical period, or
  only a `unit_participation` ([§3](06-audit-and-import.md#3-import-pipeline--deleted)). Settled by
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
- **✅ Closed — exact redaction scope: which fields are personal data vs. organizational history (§4).**
  The bullet read "requires legal review", and **that review is not coming**
  ([D-205](../decisions/round-24.md#d-205--there-is-no-legal-review-and-assumption-49-is-retired)), so the
  line this page already draws **is** the policy — written by the person designing the system, with its risk
  named in the retention bullet above rather than a basis claimed below it. D-083 removed the *category*
  question (there is no specially-graded subset of the person record), and
  [D-088](../decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)
  drew the *line* the design keeps: a person's names, `gender`, contact points and identifiers, every
  `person_attribute` row and every `event_answer.value` are erased; `membership`, `fee_obligation`,
  `payment`, `event_registration` and the anonymised `person` row are organizational history and survive.
  **Nothing is left asking which of those two lists a field belongs to: a new column about a person joins
  one of them at the design table, and `redacted_tables` in §4 is where the choice becomes visible — once an
  erasure has run and the table it reached is named there.**
- **✅ Deleted — whether `person.notes` should exist at all.** It does not, and the burden this item was written
  about turned out to point the other way ([D-191](../decisions/round-23.md#d-191--personnotes-is-deleted-and-the-vocabulary-takes-the-job)).
  The column was kept off the redactor's list, because naming a column as an exception is the field-name rule
  [D-083](../decisions/round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)
  removed — and the consequence nobody drew was that **a redaction left the notes intact**: erasure overwrites
  names and contacts, deletes every `person_attribute` row, empties an event answer, and did not touch the free
  text this same page admits may hold a diagnosis. Free text about a person is now an attribute definition's
  value, and an attribute row is the one thing this design *deletes* on erasure, so the deletion made erasure
  stronger rather than weaker. **What still exists is free text *about* a person that is not a fact *of* them**,
  and the page says so rather than implying the record is now clean of it: a roster row's `note`, an account's
  `status_reason` and `status_note`, and a `field_conflict` holding the two values a merge could not choose
  between. The boundary is that the person row holds no free text, while plenty of rows about a person do.

All tracked in [../open-questions.md](../open-questions.md).
