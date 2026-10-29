# Data Model — Audit and Import

`audit_log`, `import_batch`, staging tables, and the redaction log.

`access_log` (the authorization audit trail) is in
[05c-access-log-and-resolver.md](05c-access-log-and-resolver.md#9-access_log). This document covers the
data-change audit trail, the legacy import pipeline, and erasure.

---

## 1. Two audit trails, and why both

| | `access_log` | `audit_log` |
|---|---|---|
| Records | Who did what, and by what authority | Which fields of a row changed, and their values before and after — **including a person's descriptive values, which are in the entry deliberately** (§2.2) |
| Answers | "Who accessed this child's record, and were they allowed to?" | "When did this person's address change, and who changed it?" |
| Volume | Very high | High |
| Raised by | Application code, on every permission check and action | **Every write to an audited table, on every path** — §2.1 names who owes that write now that no trigger is defined anywhere |

Keeping them separate is deliberate. They have different retention needs, different query
patterns, and different access permissions. Merging them produces a table that is too
large to query and too sensitive to expose to anyone who needs one half of it.

**One wording change, because this table used to ask about a thing that no longer exists.** The
first cell read "who accessed this child's *medical record*", a phrase this corpus cited in five
places and defined in none. [D-083](../decisions/round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)
resolved it by removing the referent rather than by building it: there is one record about a person,
and everything in it other than name, gender and age lives in `person_attribute`
([09-attributes.md](09-attributes.md)). **The question this trail answers is unchanged and is now
sharper** — it is asked about the whole record, which is the thing `person.view` really reaches.

**A second cell in that table was stale in the opposite direction, and it is corrected rather than
quietly rewritten.** It read *"except a person's descriptive values, which are never in the entry"* —
which was §2.2's withdrawn rule surviving in a summary row after §2.2 itself had retracted it. Anyone
who read §1 and stopped there would have concluded the payload is clean, which is the one thing this
table is not. **A summary that contradicts the section underneath it is the more dangerous kind of stale,
because a summary is what people read.** The payload holds those values deliberately, and loses them 24
months later; both halves are in the entry, and neither is a detail.

---

## 2. `audit_log`

**Fields**

| Field | Kind | Notes |
|---|---|---|
| `id` | surrogate id | |
| `occurred_at` | timestamp, audit time | Default: now |
| `transaction_id` | integer, required | Default: the id of the enclosing transaction. Groups all changes made in one transaction, so a multi-table operation (approve a request → create a membership) reads as one event rather than two unrelated ones. *(The example used to be three steps, ending "open a unit participation"; [D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row) deleted that row, and the two-step version is still the case this column exists for — §3.1's import transaction, which used to write a pair and now writes one row, is the other.)* |
| `actor_person_id` | reference to person, optional | Taken from the request context, not from the row. `NULL` for migrations, imports, and batch jobs |
| `actor_label` | text, optional | `system`, `migration:0042`, `import_batch:17` — for changes with no person actor. Otherwise a forensic gap |
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
6. Redact both images (§2.2): the credential values that must never be logged at all, and —
   where the row belongs to a redacted person — the personal data erasure has already removed
   from the business tables. Everything else is stored as it stands, including a person's
   descriptive values, which are guarded by §8 item 7 rather than stripped here.
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
[../appendix/permission-catalog.md §8](../appendix/permission-catalog.md#8-audit-and-system)
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
[AT-4](../open-questions.md#at-4--is-one-permission-enough-to-guard-a-trail-that-holds-person-data)
will receive is that the payload is temporary rather than that the guard is good). It does not retire the
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
the obligation above. **It is, however, true of ordinary operation and false of exactly two
moments**, and saying so is the honest version of the paragraph.

**The first is §3's import revert,** which *does* hard-delete business rows — the `person`,
`membership`, `event_registration` and `event` rows a batch created (which of the three depends on which
kind of batch it was — §3's Reversibility is the list; **there were four arms here until
[D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row) deleted the
`unit_participation` one, and a revert of an old batch finds nothing of that kind to remove**) — and those rows were live, referenced and
visible to real users before they went. So **a revert writes audit entries for its deletes, naming the
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
run, and whose interest does it serve. An earlier draft of this section described a fourth, and that
fourth has been withdrawn below rather than quietly deleted, because the mistake is the useful part.**
The three are not variations on one idea and must not be implemented as one job. Two of them run on the
way in or on request, on the strength of a person's right or a credential's nature; the third runs on a
calendar, on the strength of nobody's right at all. Collapsing the third into the second is the easy
mistake available here — both empty the same two columns — and §5 carries a separate check for each
because they fail in opposite directions.

> **An audit log that stores the data it audits is a second copy of that data, with weaker access
> controls and a longer retention period.** This sentence is still true, and it still describes
> `audit_log`, which holds the whole person record in its payloads. **What changed is which half of it
> is treated as the defect.** The first response was to empty the payload; the answer here is the
> other half — the log's access controls and retention are what is wrong about the copy, and emptying
> the payload fixes neither while destroying the reason the table exists. See
> [00-conventions.md §8 item 7](00-conventions.md#8-personal-data-and-erasure) and
> [05c-access-log-and-resolver.md §9](05c-access-log-and-resolver.md#9-access_log), which argues against copying data into a
> less-guarded place and, read against this table, names the copy in question.
>
> **One clause of that sentence has since been changed from the side it complained about.** The copy's
> *longer retention period* is no longer unbounded: the payloads are emptied 24 months after they are
> written (mechanism three, argued in full below). That is a fix to the half the sentence called a
> defect, and it is not the answer the first response wanted — the payload is emptied while the table
> keeps its whole reason for existing, which is what the sentence above was warning against.

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

**The rule that used to sit above these steps, and why it is gone.** An earlier draft reduced a
`person_attribute` image to its two references — `person_id` and `attribute_definition_id`, saying
*whose* fact and *which* fact and nothing of its content, with no `«redacted»` marker either — on the
grounds that a log read by more people than the record should not hold what the record holds. It is
withdrawn, for two reasons that came from the decisions this section already reflects:

- **It re-created, inside the logging rules, the sensitive subset D-083 deleted**
  ([../decisions/decision-log.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data](../decisions/round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)).
  A rule that strips attribute values while `person_contact` changes are logged with their values is a
  list of more-sensitive-than fields wearing a table name instead of a permission name.
- **It left D-085's history empty.** Overwrite-in-place was chosen because the trail is the history;
  an entry that records *a value changed* without recording which one is a history of nothing, and the
  question this table's history is actually asked for — *what did we believe about this child in
  March?* — would have been unanswerable by design rather than by accident.

What the draft got right survives as the guard instead: the copy *is* as sensitive as what it quotes,
so the permission that reads it belongs at the top of the catalog
([../appendix/permission-catalog.md §8](../appendix/permission-catalog.md#8-audit-and-system)), and
that is a line in a document rather than a mechanism, which is the honest weakness.

**What the credential list is not, stated where a reviewer will read it.** It is not the thing
protecting personal data, and it cannot become that, because **a list of names is only as good as
somebody having predicted the name of every field that would ever matter** — and this system generates
those names at runtime, one per code the organization invents. `allergy` is not on the list and never
will be, which is now the correct state of affairs rather than a hole: an allergy is a value in
`person_attribute`, it is logged, and it is protected by who may read the table it was logged into.

**Which half of that sentence is the requirement, and which was a mechanism.** "In the trigger"
used to appear here, and D-072 deleted the trigger. What survives is the ordering, which is the
part with the teeth and which now applies to mechanism one alone: **credential stripping runs on the
way in, never in a cleanup job that might not run.** The trigger was one way to guarantee that; a code
path that redacts, then writes, is another; **a code path that writes and repairs afterwards is not
that**, because for one transaction the secret is in the log and readable, and because the repair *is*
the cleanup job this sentence forbids. With no trigger there is nothing stopping the third option
except whoever writes it, which is why the sentence is stated as a rule about ordering rather than
about a database feature. Mechanism two runs in the opposite direction — it reaches rows already
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
left untouched: actor, on-behalf-of, operation, table name, record id, changed fields, transaction,
session, channel. The trail goes on answering *"who changed this row, when, and were they allowed to"*
for the life of the system, and stops answering *"and to what"* after two years. Twelve months is the
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
it: check 7 in §5 counts rows older than the window that still carry a payload, and alerts. The sentence
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
the half D-088 chose to keep. The two deletes that exist near this table are elsewhere and are about
other tables: a revert (§3) hard-deletes *business* rows a batch created and writes audit entries for
having done so, and an erasure (§4) deletes `person_attribute` rows and records that in
`redaction_log` rather than one entry per value.

**All three operations are updates, and an append-only guard has to be written knowing that.** Nothing in
this repository defines an append-only trigger — D-072 removed the last of them — but the property is
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

**What it costs, stated rather than buried.** The window is the cheapest thing this design will ever do
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
non-identifying — and the review is the one [B-3](../open-questions.md#b-3--closed--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)
already asked for, now with a concrete policy in front of it instead of a blank (§6).

**The neighbouring trail takes the same window, as a proposal rather than a decision.** `access_log` is
proposed at the same 24 months under
[F-8](../open-questions.md#f-8--retention-policy-for-access_log), which still needs confirming; it is a
weaker question than this one because that table keeps the payloads of *reads* out of itself to begin
with ([05c-access-log-and-resolver.md §9](05c-access-log-and-resolver.md#9-access_log)).

**The personal-data entries in the old redaction list are gone, and they were removed rather than
renamed.** It used to read `secret_hash`, `notes`, `custody_arrangement`, `termination_note`,
`rejection_note`, `status_note`, on the theory that free text is where a diagnosis hides; a second,
shorter *always-redacted* set repeated `notes` and `custody_arrangement` for emphasis, which already
told you the mechanism was running on intuition about which fields looked sensitive. All of them are
logged now, for the same two reasons as above: the fields are person data and D-083 refuses to grade
person data, and a scrubbed history is a history that did not happen. **The residual risk is stated
plainly rather than left implicit — an audit table holding a child's descriptive values is a wider
surface than any single screen, and the thing standing between it and a volunteer with an interest is
one sensitivity mark plus whoever implements it.**

**What still argues against `person.notes`, and it is not this.**
Consider whether
`person.notes` should exist at all: it is the last free text about a person outside the attribute
vocabulary, the vocabulary is where such a sentence is visible to a report and to a curator rather
than only to whoever next opens the record, and the open question is argued there in
[01-identity.md §2](01-identity.md#what-is-deliberately-not-on-this-table) as well as here.

### 2.3 History query

The full change history of one row is found by taking the `audit_log` rows for its table
name and record id, newest `occurred_at` first, and reading out when it happened, the
operation, which fields changed, the old and new values, and who did it — the actor's
person name where there is an actor, and `actor_label` where there is not.

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
state has to be *said*, the way `actor_label` is said when there is no actor person. The date the row
crossed the window is not stored anywhere and should not be: it is the row's own `occurred_at` plus the
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
[AT-4](../open-questions.md#at-4--is-one-permission-enough-to-guard-a-trail-that-holds-person-data).

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
| **Events** | an event, and who attended it | an `event` owned by the root ([D-094](../decisions/round-09.md#d-094--the-root-unit-owns-every-imported-event)) and one `event_registration` per listed attendee |

**Neither half names a unit, and unit assignment is out of scope by instruction — a consequence, not an
omission.** `parsed_unit_code` and `parsed_unit_name` stay in the parser (§3's staged-row table says what
reads them now, which is nothing), no batch creates an `org_unit`, and no sub-unit `unit_participation`
row is ever imported. **The consequence in one sentence: the system's historical record contains no
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
| `applied_membership_id` | reference to membership, optional | What this row created — **set on every row of a people batch whose source states a membership period** (§3.1). **This note said the opposite until this round:** it read "empty for every row of a roster batch, which creates participations only", and [D-093](../decisions/round-09.md#d-093--the-one-off-import-may-create-memberships-both-ends-dated) reversed it, because the export states membership periods and the ban it rested on was about *inferring* them. Empty on every row of an events batch, and a set value on an events row is still the rule in §3.1 having been broken — membership may be imported from a period the source states, never from an attendance list |
| ~~`applied_participation_id`~~ | — | **Deleted by [D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row).** It held the id of the root-unit participation row a membership brought with it, and its whole purpose was to say *"a membership row with this column empty wrote half a pair"* — a check on a pair that no longer exists. Nothing replaces it: §3.1's transaction writes one row, so there is no second id to record and no half to be missing |
| `applied_event_id` | reference to event, optional | **An events batch.** The event this attendee row was matched to, or created by it. **Shared across rows**, which is the difference from the four ids above: a hundred attendees of one camp name one event, and revert has to know that (§Reversibility) |
| `applied_registration_id` | reference to event registration, optional | **An events batch.** What this row created — one per attendee, and the only row an attendee who was *not* listed gets, which is none (§3.1, [D-059](../decisions/round-05.md#d-059--unanswered-is-the-absence-of-a-row-a-registration-stores-two-values)) |
| `created_at` | timestamp, audit time | |

**Rules**

- **One event per (title, date), not one per attendee.** `uq_staging_event_match` is this rule's name.
  Enforced inside the transaction that applies a staged row, in this order: 1. normalise the title and
  take the date; 2. look for an event this batch has already created with that pair, then for an event the
  root already owns with it; 3. reuse what was found, otherwise create it and record it on this row;
  4. write the registration. **Application layer, deliberately** — the pair spans rows of one batch rather
  than columns of one row, and a uniqueness claim across a batch describes how the file is read, not what
  the data holds ([`00-conventions.md §6a`](00-conventions.md#6a-who-enforces-an-invariant-now) is the
  register for that kind of answer). The failure it prevents is the loud kind run quietly: ten thousand
  attendee rows becoming ten thousand events, all owned by the root, all undeletable except by revert.
- **Which created ids a row may carry is decided by `import_batch.batch_kind`, not by the row.** A people
  batch fills `applied_person_id` and `applied_membership_id`; an events batch
  fills `applied_person_id` — an attendee who had to be created is still a person created — plus
  `applied_event_id` and `applied_registration_id`. A row carrying one from each group is a batch that was
  typed wrongly, and revert reads this rule to know what it is about to delete. **The people arm used to
  name a third column,** `applied_participation_id`, and it went with the row it pointed at
  ([D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)); a batch
  applied before go-live that filled it has nothing extra waiting to be reverted.

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
   batch in hand does not use it. **This list had a fifth arm until
   [D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)** — the
   `unit_participation` rows sat between the events and the memberships, because a people batch used to write
   a pair — and it is gone rather than dormant: there is no such row for a revert to find, in an old batch or
   a new one.
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

*This heading read "What a roster actually evidences" until round 9. The question it asks was always the
right one — what may a row be read as proving? — and it was the noun that was wrong.* A roster is evidence
of presence in a unit, and the corpus
[D-090](../decisions/round-07-08.md#d-090--the-legacy-corpus-is-thousands-of-roster-rows-with-numbers-and-no-money)
described as one turned out to be two exports that between them evidence presence *at an occasion* and
membership *of the organization*, and evidence no unit at all
([D-092](../decisions/round-09.md#d-092--the-corpus-is-people-and-events-and-it-names-no-units)). The
answer therefore has two halves now, and they are not the same answer.

**A people row evidences a bounded membership, and the import writes one.** The source states a name, a
birth date and *the period during which this person was a member of the organization* — which is a
membership claim made by the source rather than inferred by the reader, and that distinction is the whole
of what [D-093](../decisions/round-09.md#d-093--the-one-off-import-may-create-memberships-both-ends-dated)
changed. So a people batch writes a `membership` with **both** `valid_from` and `valid_to` set,
`data_confidence = 'low'`, the batch id on it — **and nothing else in the temporal layer.** It used to write
that row *together with* a root `unit_participation` row, in one transaction, under a check whose whole job
was that the pair existed together and agreed; [D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)
deleted the second row, so the transaction has one row in it and the check has nothing left to compare,
which is what [03-membership.md §5](03-membership.md#5-unit_participation--deleted-by-d-097) now records rather than what it
argues. **One row per period the source states, not one per calendar year**: an
export of consecutive years is a period, and the `renewed_from_membership_id` chain is left to whoever
reconstructs it by hand, because a renewal chain asserted by a parser is a lineage nobody chose and it is
the kind of derived history
[D-096](../decisions/round-09.md#d-096--a-reused-unit-number-is-a-new-unit-unless-someone-records-the-continuity)
refuses to infer about units for the same reason.

**An events row evidences presence at one occasion, and nothing beyond it.** It writes an
`event_registration` for the listed attendee with `was_present = true`, against an event that **belongs to
nobody** — [D-102](../decisions/round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)
deleted `event.org_unit_id` and [D-094](../decisions/round-09.md#d-094--the-root-unit-owns-every-imported-event) with it, so the
import owes no owner choice at all, which is one of the savings
[D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row) counted in
passing — and **no row at all for anybody who is not listed**: inventing `not_attending` from silence would
put words in a source that said nothing ([D-059](../decisions/round-05.md#d-059--unanswered-is-the-absence-of-a-row-a-registration-stores-two-values)).
Sub-unit belonging used to be a `unit_participation` rather than a membership
([D-041](../decisions/round-02-03.md#d-041--belonging-to-a-sub-unit-is-a-participation-record-not-a-membership));
there is no such row left to decline to write, and the imported halves still produce nothing of either kind.
**What an imported event does owe, since D-102, is the per-event instantiation of the seeded
answers-view grant** — one insert beside the event row, in the same transaction, or the imported event has
nobody who can read its answers.

**The half of the old ban that survives, in the sentence that survives it unchanged: never an open-ended
membership, and never one inferred from an attendance row.** The reason is D-039 and it has not moved — an
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

**Superseded, and kept visible because the reasoning is the useful part.** This section used to hedge:
import a participation, *unless* there is evidence of payment, in which case a membership may be inferred —
and then, one round later, to state the opposite as flat fact: **"a roster row makes a
`unit_participation` and nothing else; `membership` rows come only from the current register."** Both
sentences were arguing against something real. The first was a rule waiting to be misapplied by whoever
found a dues column in a later file and read the older text as permission, which is why it was tightened.
The second was correct about rosters and wrong about the corpus: it generalised from *this file has no
money in it* to *no membership may arrive from a file*, and the corpus arrived with membership periods in
it. Neither half of that history is deleted above, because the next import will be a third shape and
whoever writes it needs both failure modes on the record, not a clean line.

**What the two halves agree on is the thing nobody asked about: neither names a unit.** `parsed_unit_code`
still fills and still goes unread (§3), no batch creates an `org_unit`, and no sub-unit participation row
is imported. **The system's historical record therefore contains no sub-units.** "Who was in pack X in
2011?" is unanswerable on day one, and the first answer anyone reads will be a roster somebody typed in —
which is why the sentence belongs here rather than in the decision log: the absence is in the source, but
the surprise is in this pipeline.

**What this gives up, since it gives up something.** *"Did they pay?"* has no answer for any imported
period — no money arrives in either export, so there is no `fee_obligation` and no balance on these rows
at all ([07-finance.md §2](07-finance.md#2-minimal-provisional-shape)), and every cross-decade member
count is a mix of an export and a register distinguished only by `data_confidence` and `import_batch_id`.
What the previous round gave up is narrower now, and what remains given up is that the imported membership
is the source's claim about a status rather than a record of the act: nobody paid a fee in this system for
1998, and the row says *the organization's export said so*, which is the most the evidence supports.

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
  ([§2.2](#22-redaction-before-logging)); afterwards it is the thing the person asked for the system to
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
  ([§3.1](#31-what-a-source-row-actually-evidences)) — needs your input on the organizational
  year boundary (tracked as [../open-questions.md](../open-questions.md) A-4). **Sharper, not smaller,
  since [D-093](../decisions/round-09.md#d-093--the-one-off-import-may-create-memberships-both-ends-dated)
  put memberships back on the receiving end of it:** the inferred end date is not the end of a record nobody
  reads, it is the `valid_to` of a row that gates authority, so the year boundary is the value
  standing between the import and the permission gate. (When this bullet was written the row in question was a
  `unit_participation`; [D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)
  removed that table, which sharpens the point rather than softening it — there is now exactly one period an
  inferred date can be ending, and it is the consequential one.)
- **✅ Resolved — whether the import should create a `membership` at all** for a historical period, or
  only a `unit_participation` ([§3.1](#31-what-a-source-row-actually-evidences)). Settled by
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
