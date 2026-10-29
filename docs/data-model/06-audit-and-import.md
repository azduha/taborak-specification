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
[../appendix/permission-catalog.md §8](../appendix/permission-catalog-a-codes.md#8-audit-and-system)
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
([../appendix/permission-catalog.md §8](../appendix/permission-catalog-a-codes.md#8-audit-and-system)), and
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
non-identifying — and the review is the one [B-3](../open-questions.md#b-3)
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
