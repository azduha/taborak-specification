# Data Model — Audit and Import: the two audit trails, and `audit_log`

`audit_log` and its trigger, what is stripped before a row is written, and the history query.
`access_log` (the authorization audit trail) is in
[05c-access-log-and-resolver.md](05c-access-log-and-resolver.md#9-access_log).

**Section numbers are shared across the three parts** and never renumbered, because other pages cite
them by number and their anchors are built from them:
[06-audit-and-import.md](06-audit-and-import.md) holds §1–§2 (the two audit trails and the `audit_log`
table), [06a](06a-import.md) §3 (the legacy import pipeline), and
[06b](06b-redaction-and-checks.md) §4–§6 (the redaction log, the integrity checks, open issues).

---

## 1. Two audit trails, and why both

| | `access_log` | `audit_log` |
|---|---|---|
| Records | Who did what, and by what authority | Which fields of a row changed, and their values before and after — **including a person's descriptive values, which are in the entry deliberately** (§2.2) |
| Answers | "Who accessed this child's record, and were they allowed to?" | "When did this person's address change, and who changed it?" |
| Volume | Very high | High |
| Raised by | Application code, on every permission check and action | **Every write to an audited table, on every path** — §2.1 names who owes that write, since no trigger is defined anywhere |

Keeping them separate is deliberate. They have different retention needs, different query
patterns, and different access permissions. Merging them produces a table that is too
large to query and too sensitive to expose to anyone who needs one half of it.

**Both questions are asked about the whole record, and that wording is load-bearing.** There is no medical
record to ask about —
[D-083](../decisions/round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)
removed the referent rather than building it — so there is one record about a person, and everything in it
other than name, gender and age lives in `person_attribute` ([09-attributes.md](09-attributes.md)). *"Who
accessed this child's record, and were they allowed to?"* is the question `person.view` really guards.

**The same holds for what this trail's payloads hold.** A person's descriptive values are in an audit
entry deliberately (§2.2), and they are emptied once the entry passes the payload window
([D-088](../decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)).
Both halves belong in this table's own summary, because **a summary that contradicts the section
underneath it is the more dangerous kind of stale, and a summary is what people read.**

---

## 2. `audit_log`

**Fields**

| Field | Kind | Notes |
|---|---|---|
| `id` | surrogate id | |
| `occurred_at` | timestamp, audit time | Default: now |
| `transaction_id` | integer, required | Default: the id of the enclosing transaction. Groups all changes made in one transaction, so a multi-table operation (approve a request → create a membership) reads as one event rather than two unrelated ones. |
| `actor_person_id` | reference to person, optional | Taken from the request context, not from the row. `NULL` when an integration made the call — `api_key_id` below carries the actor then — and `NULL` for the writers that have no request context at all: a migration, the yearly expiry sweep, a run of the import pipeline, whose person is in `import_batch.created_by` and not here. [00-conventions §7a](00-conventions.md#7a-what-an-empty-actor-column-means) reads that empty as **this system acting on its own**, which is an answer and not a missing one. **A correction made by hand through the application is not one of those writers** — somebody was in front of a screen, and their name goes in this column |
| `api_key_id` | reference to `api_key`, optional | Which registered integration made the call, when the request authenticated as a caller rather than as a person ([05e-keys-and-callers.md §14](05e-keys-and-callers.md)). **Set together with `actor_person_id` never**: a request is made by a person or by a key, and a row naming both answers *who did this* twice, which is the impersonation this design refuses at the resolver instead ([D-121](../decisions/round-16.md#d-121--a-key-never-carries-a-persons-authority)). It names the caller and nothing beside it — not the person who installed that key, whose column is attribution for an act and never an actor here |
| `actor_label` | text, optional | **Not free text: a value from the label list of [00-conventions §7a](00-conventions.md#7a-what-an-empty-actor-column-means)** — `system:renewal-sweep`, `system:payload-reduction`, `system:log-reduction`, `system:bank-pull`, `migration:0042`, `import_batch:17` are instances of its rows, and bare `system` is retired, because it means "one of the above, and I am not saying which" ([D-125](../decisions/round-17.md#d-125--an-empty-actor-column-is-this-system-acting-on-its-own-and-its-name-comes-from-a-fixed-list)). It exists for the writers that have no row of their own, and **a writer that is not on that list joins it there before it writes** — the list is prose, so nothing in the database refuses a label outside it and check 4 of [06b §5](06b-redaction-and-checks.md#5-integrity-checks) is what notices. A caller that is not a person is a row in `api_key_id`, not a label, so an integration's write never arrives here. A row naming none of the three is no longer this trail's gap, because §7a says what it means; what check 4 counts now is a label that is not on the list, and a write path that owed a person and named none |
| `operation` | text, required | One of: `insert`, `update`, `delete` |
| `table_name` | text, required | |
| `record_id` | surrogate id, required | The row that changed. No reference: the table is named per row, so it points at any table in the database |
| `changed_fields` | list of text | Which columns changed. Enables targeted history queries without parsing JSON |
| `old_values` | free-form jsonb, optional | **Redacted before insert**, and **emptied once the row passes the payload window**. See §2.2 for all three operations and why they are not one |
| `new_values` | free-form jsonb, optional | **Redacted before insert**, and **emptied once the row passes the payload window**. See §2.2 |
| `on_behalf_of` | reference to person, optional | Set when the actor was acting for another person. Mirrors `access_log.on_behalf` (04-relationships.md §5) |
| `session_id` | text, optional | |
| `ip_address` | network address, optional | |
| `request_id` | text, optional | |

**Indexes**

- One row's history: table name and `record_id`, newest `occurred_at` first.
- One actor's actions, newest first — **two of these, not one**, because an actor is a person in one
  column and a key in another: rows naming a person, and rows naming a key. The review that asks what an
  integration wrote is asked by key.
- Everything in one transaction, by `transaction_id`.
- By time alone, newest first.
- Rows by a *member of* `changed_fields`. The targeted history queries ask "which rows
  changed this column", so the list has to be searchable element-wise rather than as a whole
  value.

### 2.1 The trigger

**Nothing in this repository defines a trigger, so this section's guarantee is a rule and not a mechanism**
([D-072](../decisions/round-06.md#d-072--the-documentation-carries-no-sql-the-schema-is-the-orms-job)):
**every insert and every update to an audited table writes exactly one `audit_log` row, and the change and
its audit row stand or fail together.** "The audit trail usually has it" is not a version of this rule — the
trail is how the organization answers "who changed this child's address, and when?", and an answer that
depends on which code path made the change is not an answer. **The layer that owes it is the write itself,
on every path**: the screens, the legacy import, the yearly expiry sweep, a bulk reorganisation, a call
made with a key — which names its key — and a row somebody corrects by hand through the application, which
names that person. The paths with nobody in front of a screen and no key behind them are the scheduled
writers and the migrations, and an empty actor column is their name, with `actor_label` saying which of
them ([00-conventions §7a](00-conventions.md#7a-what-an-empty-actor-column-means)). Model-layer validation
logs the intended path, which is the only path that was never at risk; check 5 in §5 is the net under the
rest, and it is a report, not a guard. **The one thing this rule cannot reach is a change made from outside
the application altogether** — it writes no audit row because there is no write to attach one to, and
[§5's report of a change the trail never saw](06b-redaction-and-checks.md#5-integrity-checks) is what
notices afterwards, not before.

The steps below are what is owed, in the order that makes it safe. The order is a rule, not a
detail: the redaction step has to run before the write, and the "nothing changed" test has to run
before anything is spent on a row that would log noise.

1. Read the acting person, the acting key where the request authenticated as one, and the
   on-behalf-of person from the request context (`app.current_person_id`, `app.on_behalf_of`);
   an unset or empty value means no *person* actor, not an error — [00-conventions §7a](00-conventions.md#7a-what-an-empty-actor-column-means)
   reads it as this system acting on its own, and step 7 is where that gets its name. A context naming a
   key has an actor and is not that case: the key goes in `api_key_id`, and a row whose actor is a key never
   sets `on_behalf_of`, because a key acts for itself
   ([D-121](../decisions/round-16.md#d-121--a-key-never-carries-a-persons-authority)).
2. On an **insert**, take the new row as the after-image.
3. On an **update**, take both the old and the new row, and work out the changed fields:
   the keys present in both images whose values differ, named in key order.
4. If that comparison found nothing, stop and write nothing — a no-op update must not log
   noise.
5. On a **delete**, take the old row as the before-image; there is no after-image.
6. Redact both images (§2.2): the credential values that must never be logged at all, and —
   where the row belongs to a redacted person — the personal data erasure has already removed
   from the business tables. Everything else is stored as it stands, including a person's
   descriptive values, which are guarded by §8 item 7 rather than stripped here.
7. Write one audit row carrying: the actor — `actor_person_id` or `api_key_id`, never both — **and, where
   the write had no actor of either kind, the `actor_label` naming which of this system's own writers it
   was, taken from the list in [00-conventions §7a](00-conventions.md#7a-what-an-empty-actor-column-means):
   the renewal sweep, payload reduction, the bank statement pull, a named migration, or a named batch.**
   The label is not a fallback for a writer that could have named someone — a person who corrects a row by
   hand through the application is `actor_person_id`, and a call that authenticated is `api_key_id` — so a
   row arriving here with none of the three has not joined the list, and check 4 of
   [06b §5](06b-redaction-and-checks.md#5-integrity-checks) reports it. Then the
   on-behalf-of person, the operation as lower-cased `insert`, `update` or `delete`, the table name,
   the record id taken from the new row and falling back to the old one, the changed fields, both
   redacted images, and the session id, ip address and request id from the request context.
8. Change nothing about the row being written. The audit row describes the change and never
   amends it — and it commits in the same transaction as the change. That togetherness is what a
   trigger gave for free and what a logging step written beside the write must supply deliberately:
   one transaction, so there is no moment in which the change exists and its audit entry does not.

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

**`person_attribute` is inside that obligation on exactly the same terms as any other business table,
and the sentence is worth writing down because this document asked for an exception here and was
refused.** A write to a descriptive value owes its audit row like any write, and it carries its
before and after images like any write
([00-conventions §8 item 7](00-conventions.md#8-personal-data-and-erasure)). The reason no exception
survives is that both halves of the design collapse without one:
[D-085](../decisions/round-07-08.md#d-085--the-identity-machinery-stays-structured-the-boundary-is-rules-not-sensitivity)
chose overwrite-in-place on the strength of this trail being the only history a value has, so a trail
recording *a value changed* without recording which one would be a history of nothing; and
[D-083](../decisions/round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)
says a diagnosis is not a different kind of fact from a shoe size, so excluding attribute values from
the payload while `person_contact` changes are logged with their values would be a sensitive *subset*
of the person record re-enacted inside the logging rules — the privileged corner arriving as a list of
table names after it was deleted as a list of permission names.

**Therefore this table holds a child's allergy list in the clear, in a table designed to be read by
auditors and kept longer than the record it describes — which since
[D-088](../decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)
is true of the payloads for 24 months and is untrue afterwards (§2.2).** That is the design, not an accident of it,
and what it means is that the guard on `audit_log` is now load-bearing in a way it was not: **an audit
entry about a person is as sensitive as the person data it quotes**, which is stated as a requirement
on `audit.view`'s sensitivity mark in
[appendix/permission-catalog-a-codes.md §8](../appendix/permission-catalog-a-codes.md#8-audit-and-system)
and argued in [05c-access-log-and-resolver.md §9](05c-access-log-and-resolver.md#9-access_log) — where the case against
copying data into a less-guarded place applies to this table directly, since this table is the copy.
The failure mode inverts, and it is worth naming because the shape is unfamiliar: everywhere else the
worry is a table nobody audits, and here it is a table whose payloads outrank its own permission. No
check in §5 can see that — a sensitivity mark is a line in a document, not a row in the database — so
it is a review item with exactly one place it is written down, and that is the fragility.

**What the payload window does to that paragraph, and what it conspicuously does not.** The window does
not repair the grading; it **shortens the period during which a wrong grading is a leak**, which for an
organization of this size is the only control that will ever actually be in place
([D-086](../decisions/round-07-08.md#d-086--a-sensitivity-mark-grades-what-a-grant-exposes-not-the-table-it-reads)
is the decision that named the exposure, and the strongest argument
[AT-4](../open-questions.md#at-4)
ever put up for it is that the payload is temporary rather than that the guard is good — an argument that
outlived the question it was made against, since
[D-138](../decisions/round-20.md#d-138--one-permission-guards-the-whole-audit-trail-and-the-widening-is-on-the-record)
settled that one code is the gate and a window can only bound how long it reads for, never how far). It does not retire the
mark either. A reduced row about a `person_attribute` change still names the table, the record id, the
field that changed, the actor and the moment — which is to say it still says *this child had a value of
this kind recorded, here, by this person*, and that is a statement about a child even with the value
gone. So the mark stays where
[D-088](../decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)
leaves it, at the top tier, and the window is a bound on the damage rather than a discount on the
permission.

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
the obligation above. **It is true of ordinary operation and false of exactly two moments.**

**The first is §3's import revert,** which *does* hard-delete business rows — the `person`,
`membership`, `event_registration` and `event` rows a batch created — which of them depends on which kind
of batch it was, and §3's Reversibility is the list — and those rows were live, referenced and visible to
real users before they went. So **a revert writes audit entries for its deletes, naming the
batch and the row it removed.**

**The second is §4's erasure,** which deletes the `person_attribute` rows of the person being
anonymised ([00-conventions §4](00-conventions.md#4-deletion-policy) records why that one table is
erased by deletion rather than by overwriting, and the condition on which that stays safe — nothing may
reference an attribute row).
It is recorded **once, in `redaction_log`, naming `person_attribute` in `redacted_tables`** — and not
as one `audit_log` row per erased value. That is a consequence of §2.2 rather than an exception to the
revert rule, and the difference is worth seeing: revert deletes rows whose *contents* are safe to
quote and whose *existence* is what someone will ask about, while erasure deletes rows whose contents
must not be quotable afterwards and whose existence is the only fact that may survive. **Note what
this argument is, because §2.1's argument is the opposite one and both have to be true at once:** per-value
audit entries here would either write the erased value into a row that outlives the erasure — which is
a redaction that failed, and precisely the copy §2.2 exists to destroy — or accumulate hundreds of
identical rows whose entire content is "something was erased", which is exactly what §4's log is for.
So values are quoted in the trail as a rule, and the rule stops at the moment the person they describe
asks not to be described any more.

`DELETE` is outside the audited operations everywhere else only because there is no **third** path
that reaches a business row with a delete. That makes revert the one place the list in §5 check 5
cannot be derived from table names alone: an audited *operation* rather than an audited *table*,
which is why check 5's replacement assertion enumerates the paths that may delete, not just the
tables that may be written. Erasure is the second such path and belongs on that enumerated list too;
it audits nothing per row, so the assertion has to know it exists rather than infer it.

### 2.2 Redaction before logging

**Three operations act on this table's payloads, and they are told apart by two questions: when does it
run, and whose interest does it serve.** A fourth is tempting and is refused below, where the refusal
carries the reasons. The three are not variations on one idea and must not be implemented as one job. Two of them run on the
way in or on request, on the strength of a person's right or a credential's nature; the third runs on a
calendar, on the strength of nobody's right at all. Collapsing the third into the second is the easy
mistake available here — both empty the same two columns — and §5 carries a separate check for each
because they fail in opposite directions.

> **An audit log that stores the data it audits is a second copy of that data, with weaker access
> controls and a longer retention period.** This is true of `audit_log`, which holds the whole person
> record in its payloads, and the answer is not an empty payload. The copy's access controls and its
> retention are what is wrong about it; emptying the payload fixes neither while destroying the table's
> reason for existing. So each half is answered with what it is: the guard is `audit.view` at the top
> tier of the catalog, and the retention is a 24-month window on the payloads (mechanism three). See
> [00-conventions.md §8 item 7](00-conventions.md#8-personal-data-and-erasure) and
> [05c-access-log-and-resolver.md §9](05c-access-log-and-resolver.md#9-access_log), which argues against copying data into a
> less-guarded place and, read against this table, names the copy in question.

**Mechanism one is a small set of values that must never enter the trail at all.** Credentials,
tokens, the secret half of an integration: for these, *being in a log* is the harm, and no guard is
wide enough to make them safe there. This is the only job the key-name list below has.

**Mechanism two is erasure reaching payloads that were written lawfully at the time.** Redacting a
person removes their values from images already in the trail (§4, and check 6 in §5); nothing here
prevents those values from having been written, and the erasure is what unmakes them.

**Mechanism three is the calendar doing the same thing to everybody: payload reduction.** A row older
than the retention window has `old_values` and `new_values` emptied and every other field left exactly as
it was. It is a scheduled job, it is owed to no one, and it applies whether or not the person whose data
the row quotes has asked for anything. [D-088](../decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)
is where the window was set and why; the argument that it is not a second species of redaction — and the
reason the sentence further down about *never in a cleanup job* does not forbid it — is stated under
**The third operation, in full** further below. That is out of order on purpose: the sentence about
cleanup jobs belongs with the steps it governs, and this operation has to survive it before it can be
used.

The redactor takes one table name and one row image and does this:

1. If there is no image at all, there is nothing to redact — return no value.
2. For each key in the credential list — `secret_hash` and the integration secrets beside it — if the
   image carries that key, replace its value with the marker `«redacted»`. Keys the image does not
   have are left alone. The list is applied wherever a listed key turns up, in any table.
3. Return the image.

**That is the whole mechanism, and the list is short on purpose.** It is keyed on field names, which is
the right shape for it: a name-based rule is the only kind that reaches a credential hidden in an
unexpected column, and a credential is safe behind no guard, so the rule has to fire on sight.

**The fourth operation, refused here because somebody will propose it.** It reduces a `person_attribute`
image to its two references — `person_id` and `attribute_definition_id` — saying *whose* fact and *which*
fact and nothing of its content, with no `«redacted»` marker either, on the grounds that a log read by
more people than the record should not hold what the record holds. It is refused for two reasons, both of
them this section's own decisions:

- **It re-creates, inside the logging rules, the sensitive subset that D-083 deleted**
  ([D-083](../decisions/round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)).
  A rule that strips attribute values while `person_contact` changes are logged with their values is a
  list of more-sensitive-than fields wearing a table name instead of a permission name.
- **It leaves D-085's history empty.** Overwrite-in-place was chosen because the trail is the history;
  an entry that records *a value changed* without recording which one is a history of nothing, and the
  question this table's history is actually asked for — *what did we believe about this child in
  March?* — would be unanswerable by design rather than by accident.

What is right about the proposal is kept as the guard instead: the copy *is* as sensitive as what it
quotes, so the permission that reads it belongs at the top of the catalog
([appendix/permission-catalog-a-codes.md §8](../appendix/permission-catalog-a-codes.md#8-audit-and-system)), and
that is a line in a document rather than a mechanism, which is the weakness to keep in view.

**What the credential list is not, stated where a reviewer will read it.** It is not the thing
protecting personal data, and it cannot become that, because **a list of names is only as good as
somebody having predicted the name of every field that would ever matter** — and this system generates
those names at runtime, one per code the organization invents. `allergy` is not on the list and never
will be, which is now the correct state of affairs rather than a hole: an allergy is a value in
`person_attribute`, it is logged, and it is protected by who may read the table it was logged into.

**The requirement is an ordering, not a database feature, and it applies to mechanism one alone:
credential stripping runs on the way in, never in a cleanup job that might not run.** A trigger was one way
to guarantee that ordering and this repository defines none
([D-072](../decisions/round-06.md#d-072--the-documentation-carries-no-sql-the-schema-is-the-orms-job)),
so what guarantees it is the shape of the write — redact, then write. **A path that writes and repairs afterwards does not
satisfy it**, because for one transaction the secret is in the log and readable, and because the repair
*is* the cleanup job being forbidden here. Nothing stops that third option except whoever writes it,
which is exactly why the sentence is about ordering. Mechanism two runs in the opposite direction — it reaches rows already
written, which is the only way an erasure can affect a trail that must not be rewritten — and the two
are not in tension because one is about a value that should never have been written and the other is
about a value that was. See
[00-conventions.md §8](00-conventions.md#8-personal-data-and-erasure) for what else the move to
generated schema took out of this section's defence in depth.

**The third operation, in full: payload reduction, and the paragraph above is the first thing it has to
survive.** [D-088](../decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)
set two clocks for this system and they point in opposite directions. The accounting skeleton —
`membership`, `fee_obligation`, `payment`, and the anonymised `person` row they hang from — has **no
clock at all** (§4, and [00-conventions §8 item 3](00-conventions.md#8-personal-data-and-erasure)). This
table has two clocks in one row: **the rows live as long as the system does, and the payloads live 24
months.** After the window a row is *reduced* — `old_values` and `new_values` emptied, everything else
left untouched: actor person, actor key, on-behalf-of, operation, table name, record id, changed
fields, transaction, session, channel. The trail goes on answering *"who changed this row, when, and
were they allowed to"* for the life of the system, and stops answering *"and to what"* after two years. Twelve months is the
**floor** a window may be set to, not a stylistic preference: anything shorter stops covering a full
year of a child's activities, and a year is the unit an incident is asked in.

**Why the cleanup-job sentence does not forbid this, which matters because the two rules are one word
apart.** Read literally, *"never in a cleanup job that might not run"* describes reduction exactly: it
is late, it is a job, and it unwrites content from rows already committed. **It is still not the same
rule, because these two are distinguished by what their failure costs and not by what their mechanism
looks like.** The credential rule forbids the *late unwriting of a secret*, and its failure mode is
lateness — write first and repair afterwards and the secret sits in a table that `audit.view` reaches for
one whole transaction, which is the harm arriving before the repair can. Reduction requires the *late
unwriting of history*, and its failure mode is not lateness but **absence**: a job that stopped running,
an over-age row still holding a child's allergy list because nobody looked. A rule whose failure mode is
lateness has to be pinned to the write, because the write is the only moment at which it can still be
obeyed. A rule whose failure mode is absence cannot be pinned to the write at all — **carrying out
reduction at the moment of writing is not obeying it, it is refusing it**, because the window is the
entire content of the rule and at write time there is no window to have passed. So reduction is a
scheduled job with a check underneath it, and the check *is* the rule rather than a reassurance about
it: check 7 in §5 counts rows older than the window that still carry a payload, and nothing about that count
is sent anywhere ([D-164](../decisions/round-22.md#d-164--nobody-is-told-and-no-page-may-say-otherwise)). The sentence
above forbids late unwriting of a credential; this paragraph requires late unwriting of history; both
are true at once and neither is an exception to the other.

**Reduction is not redaction, and it is not revert, and the three are worth setting side by side because
only one of them is anybody's right.**

| | Runs | On whose behalf | What disappears | Row survives? | Caught by |
|---|---|---|---|---|---|
| **Stripping** — mechanism one | Before the insert, on every write path | No one; the value should never have been in the table | The listed credential keys, replaced by the marker | Yes — it is written once, already clean | Nothing; it is an ordering rule, and its breach is one readable transaction |
| **Redaction** — mechanism two | When a person asks, immediately | The person the row is about | That person's values, from rows of any age, permanently | Yes, with the values gone | Check 6: a redacted person's payload still holding content |
| **Reduction** — mechanism three | On a schedule, once a row passes the window | No one; it is policy | Both payloads of every over-age row, indiscriminately | Yes, standing empty | Check 7: an over-age row still carrying content |

**What none of the three ever does is delete an `audit_log` row.** The rows are the permanent half; a
reduction that pruned rows would quietly delete the answer to *"who changed this, and when"*, which is
the half D-088 chose to keep. Every delete near this table is on some other table: a revert (§3)
hard-deletes *business* rows a batch created and writes audit entries for having done so; an erasure (§4)
deletes `person_attribute` rows and records that in `redaction_log` rather than one entry per value; and
since round 20 a scheduled job deletes [`access_log` rows whole at 24
months](../decisions/round-20.md#d-145--access_log-rows-are-deleted-at-24-months-and-the-job-that-does-it-has-a-name)
— **a delete on the other trail, which is precisely the distinction the two clocks were drawn to make.**

**All three operations are updates, and an append-only guard has to be written knowing that.** Nothing in
this repository defines an append-only trigger ([D-072](../decisions/round-06.md#d-072--the-documentation-carries-no-sql-the-schema-is-the-orms-job)), but the property is
still asserted in prose, and the neighbouring trail states it as a literal refusal of updates
([05c-access-log-and-resolver.md §9](05c-access-log-and-resolver.md#9-access_log)). **A blanket refusal of updates blocks the
erasure scrub and the reduction job alike**, quietly, from the side of the rule that looks safest. What is
worth keeping is not *nothing changes* but **nothing is corrected**: no write may alter what a row says
about who did what, to which row, when; the only writes permitted after the fact are the two that remove
content and never add or amend any.

**Erasure is untouched by all of this and still immediate.** A redaction scrubs that person's values
from payloads whatever their age, including rows written yesterday and rows two days from reduction; the
window is a ceiling on how long anything may be in there, not a waiting period anything has to serve.
**This is the sentence to keep if only one is kept: reduction never satisfies an erasure request, and an
erasure never waits for reduction.** Check 6 and check 7 exist separately because a system can pass one
and fail the other, and the two failures mean opposite things — check 6 firing means a person's right was
not honoured, check 7 firing means a policy was not applied.

**What it costs.** The window is the cheapest thing this design will ever do
about the exposure [D-086](../decisions/round-07-08.md#d-086--a-sensitivity-mark-grades-what-a-grant-exposes-not-the-table-it-reads)
accepts, and it bounds that exposure without repairing it (above, after §2's paragraph on the guard).
What it *spends* is the past: [D-085](../decisions/round-07-08.md#d-085--the-identity-machinery-stays-structured-the-boundary-is-rules-not-sensitivity)
was justified by the trail being the history, and now that history's values expire, so *"what did we
believe about this child's allergy list in 2019"* is unanswerable twice over — the value was never kept
in the business row, and the copy of it is gone. **The honest name for that trade is *no long history*,
not *no temporal columns***, and it is drawn out next to the values in
[09-attributes.md §6](09-attributes.md#6-erasure-retirement-and-the-audit-payload). If a case ever needs
the long version, the fix is temporal columns on the value — D-085 reversed — and **not** a longer
window, because stretching the window stretches precisely the guard D-086 graded and re-creates the
second copy D-083 refuses to keep.

**The half of this that is not settled, and is not pretending to be.** Indefinite retention of named
`membership` and fee rows is a claim that needs a legal basis and a decision log cannot grant one. What
the corpus now states, as an **assumption pending review** rather than as settled law, is organizational
history plus accounting obligations, held up by a redacted person row that keeps the skeleton
non-identifying — and the review is the one [B-3](../open-questions.md#b-3)
already asked for, now with a concrete policy in front of it instead of a blank (§6).

**The neighbouring trail takes the same window and the opposite shape.** `access_log` sits at the same 24
months, and it was [decided there by round 20](../decisions/round-20.md#d-145--access_log-rows-are-deleted-at-24-months-and-the-job-that-does-it-has-a-name):
**its rows are deleted rather than emptied**
([05c-access-log-and-resolver.md §9](05c-access-log-and-resolver.md#9-access_log)). Same clock, different kind. The
reduction above may never touch a row, because *what changed* is the half D-088 chose to keep forever; on the
read trail nobody needs the row at year three, the payloads of reads are not held there anyway, and a row that
answers nothing identifiable is not worth the exception. **This is the third named exception to
[00 §4](00-conventions.md#4-deletion-policy)'s "nothing is hard-deleted", and the only one driven by a clock** —
the other two exceptions that page names are a staging truncate between batches and a delete a person asked
for. **Mechanism three above is a job too, and the difference between them is the difference the corpus keeps
insisting on: mechanism three empties a row that stays, this one deletes the row.**

**No free-text field about a person is on the credential list, and none is being added to it.** The list
once carried `notes`, `custody_arrangement`, `termination_note`, `rejection_note` and `status_note` beside
`secret_hash`, on the theory that free text is where a diagnosis hides. All of them are logged with their
values now, for the two reasons this section has already given: person data is one class
([D-083](../decisions/round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)),
and a scrubbed history is a history that did not happen. A name-based rule cannot tell sensitive free text
from sensitive structured text anyway, which is why the list is keyed on credentials only.
**The residual risk is stated rather than left implicit:** an audit table holding a child's descriptive
values is a wider surface than any single screen, and what stands between it and a volunteer with an
interest is one sensitivity mark plus whoever implements it.

**What still argues against `person.notes`, and it is not this.**
Consider whether
`person.notes` should exist at all: it is the last free text about a person outside the attribute
vocabulary, the vocabulary is where such a sentence is visible to a report and to a curator rather
than only to whoever next opens the record, and the open question is argued there in
[01-identity.md §2](01-identity.md#what-is-deliberately-not-on-this-table) as well as here.

### 2.3 History query

The full change history of one row is found by taking the `audit_log` rows for its table
name and record id, newest `occurred_at` first, and reading out when it happened, the operation,
which fields changed, the old and new values, and who did it. That last one has three answers, not
two: the actor's person name where the row names a person, the integration's `code` where it names a
key — never anything derived from its secret, which this table does not hold in the first place —
and `actor_label` where it names neither
([D-121](../decisions/round-16.md#d-121--a-key-never-carries-a-persons-authority)). The third answer is a
label from [00-conventions §7a](00-conventions.md#7a-what-an-empty-actor-column-means)'s list and not a
string somebody typed, so it names a writer rather than marking an absence — which is what lets the history
view print it as an answer.

**For a `person_attribute` row this query *is* the history, not a shadow of it.** Values are
overwritten in place
([D-085](../decisions/round-07-08.md#d-085--the-identity-machinery-stays-structured-the-boundary-is-rules-not-sensitivity)),
so every value a child's allergy list ever held sits under one `record_id`, and this is where the
question *"what did we believe about this child in March, and who wrote it down?"* gets answered — for a
March inside the payload window. **After the window the same query returns the same rows and a different
kind of answer**: who, when, which row, which field, and no value (§2.2, mechanism three). That is not a
degradation to be smoothed over on the screen. An entry with a reduced payload and an entry that
genuinely recorded no value are two different facts, and a history view that renders both as an empty
cell tells a reader the organization never knew something it has since stopped holding — so the reduced
state has to be *said*, the way a key's `code` or an `actor_label` is said when the row names no person.
The date the row crossed the window is not stored anywhere and should not be: it is the row's own
`occurred_at` plus the
window, which is configuration a reader of the screen may not have, so the honest label is that the
values are no longer retained rather than a date of when they went.

The consequence is the one §2.2 spends its length on, restated where it bites: **a history screen over this
table is a person-data surface.** It is reached through `audit.view`, and it deserves to be reached
through `person.view` too — a reader who may see that an allergy was recorded in 2019 but may not see
the allergy is holding the second question and will ask it out loud. The guard on the trail is what is
relied on; a per-entry *"could this reader see this field"* check inside the history view was
considered and left unimplemented, because it would mean running the resolver per audit row against a
value that no longer exists anywhere as a row to resolve against. It is a registered question rather
than an omission now:
[AT-4](../open-questions.md#at-4).
