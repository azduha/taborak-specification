# Decision Log — Refinement round 17 (D-125 … D-126)

> An empty actor column means this system acting on its own, it says so from a fixed list, and the people who could lock themselves out are a report rather than a mechanism.

[Refinement round 16 (D-116 … D-124) ←](round-16.md) | [All decisions](index.md)

**What was asked.** The two questions round 16 left open on purpose, both of them about a writer that is
not a caller: [F-25](../open-questions.md#f-25), what this system's own name is when it writes to itself,
and [F-26](../open-questions.md#f-26), what happens when nobody who can hold `system.admin` can log in.
**Both are closed here and neither one got a mechanism** — which is the shape both answers wanted.

**The answer to the first did not come from the three positions on the page.** They were: leave it as free
text, bend `api_key` into a secretless second kind, or add a `system_writer` table. The answer given was a
question — *"can we see NULL everywhere as the system acting on its own?"* — and it is better than all
three, because it names what is already in the columns instead of adding a thing that would have to be
kept in step with them. A question that improves on its own options is worth recording as the answer,
which is why this entry says so.

**The second answer was already half-built.** [Check 9](../data-model/05d-invariants-and-seed.md#11-invariants-to-verify)
lists everyone holding `system.admin` and emails someone when its result changes. The half that was
missing is the half that turns a list into a warning: whether those people can sign in.

---

## D-125 — An empty actor column is this system acting on its own, and its name comes from a fixed list

**Status:** decided (from your answer, in your words rather than from the positions written for it)
**Date:** refinement round 17
**Closes:** [F-25](../open-questions.md#f-25)
**States once:** in [00-conventions §7a](../data-model/00-conventions.md#7a-what-an-empty-actor-column-means);
everywhere else cites it rather than restating it.
**Narrows:** integrity check 4 of
[06b §5](../data-model/06b-redaction-and-checks.md#5-integrity-checks) — what that check is *allowed* to
call a forensic gap. **Reverses nothing.** No column, table or code changes; one meaning is written down.

**Decision. Three sentences, and the order is the argument.**

1. **An actor column left empty is read as this system acting on its own, and that is a complete answer to
   "who did this".** Not a missing answer, not a gap, not a thing to be apologised for in a footnote. In
   `access_log.actor_person_id`, in `audit_log.actor_person_id`, and in the standard `created_by` and
   `updated_by`. In the access trail this settles a sentence round 16 wrote wrong: it read "with neither
   set never" while the same cell explained that a row naming neither is this system writing to itself —
   and `access_log` has no label column, so under that wording a system write to that trail was unsayable
   ([05c §9](../data-model/05c-access-log-and-resolver.md#9-access_log)).
2. **Only where empty is legal, and only in an actor column.** `import_batch.created_by` is required,
   `api_key.created_by` is required by [D-116](round-16.md#d-116--a-caller-that-is-not-a-person-is-a-registered-key-and-a-key-is-a-third-grantee-kind),
   and a grant's `granted_by` names a person: those rows have no empty to read. And NULL in a column that
   is not an actor column means what that column has always meant — an absent `scope_id` is a check at the
   unit, an absent `authorization_ref_id` is no grant involved. **A rule about actors stated as a rule
   about NULLs would be misread in every table it never touched.**
3. **Where the trail has a label column, the label comes from this list** — the one place a writer's name
   is written, so that a row nobody recognises has something to be compared against:

| The label | Who wrote the row | What it was doing there |
|---|---|---|
| `system:renewal-sweep` | the 1 January renewal sweep | Expiring memberships whose window closed, and nothing else it was never allowed to touch ([04 §1](../data-model/04-relationships.md): **Never by a job**) |
| `system:payload-reduction` | payload reduction | Emptying `old_values` and `new_values` once a row passes the payload window ([D-088](round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)) |
| `system:bank-pull` | the bank statement fetch | Writing the payments that answer a variable symbol ([D-075](round-06.md#d-075--money-arrives-from-a-bank-api-a-payment-is-requested-by-variable-symbol-and-qr-code)) |
| `migration:<id>` | a named migration | Any structural change, **and any one-off correction**: a fix that is not in a migration is a fix nobody can attribute |
| `import_batch:<id>` | a run of the import pipeline | Not anonymous, and never was — `import_batch.created_by` is required and names the person who uploaded the file ([06a §3](../data-model/06a-import.md#3-import-pipeline)) |

**Bare `system` is retired by this decision.** It was the example [06 §2](../data-model/06-audit-and-import.md)
and `00-conventions §7` both carried, and it means "one of the above, and I am not saying which",
which is the drift F-25 was actually about: `system` today and `system:cleanup` tomorrow with no row behind
either. A writer that is not on the list **joins the list on this page before it writes**, and the check
reports any label that is not on it.

**Why this is not the thing the corpus warns about.** [05-authorization §2](../data-model/05-authorization.md)
is right that "a nullable one whose null-ness silently means something" is how a channel acquires an answer
that depends on a value nobody typed — and that warning is why `guardianship` has no inferred answer. This
NULL has the shape and not the danger, for two reasons that are checkable rather than reassuring. **It
carries attribution and never an answer:** nothing in a permission check reads an empty actor column, which
is what [check 22](../data-model/05d-invariants-and-seed.md#11-invariants-to-verify) and
[invariant 19](../data-model/05d-invariants-and-seed.md#11-invariants-to-verify) already hold for a key's
own columns, and this round adds nothing to read. **And the meaning is declared, not silent:** a rule in
one section, a list a check counts against, and a report that speaks when a row falls outside it.

**What it costs, stated as costs.**

- **Nothing in the database refuses an off-list label.** This is a documented vocabulary, not a table, so
  enforcement is the check and the review, in that order. It was chosen *because* it costs no column; a
  `system_writer` registry would refuse the label at the door and cost a table, four codes nobody would
  ever grant, and a seeding rule.
- **A row written by the sweep and a row written by an unlogged one-off script now look the same** if that
  script guessed at a label from the list. The vocabulary makes a guessed label *plausible*, which is a
  worse-looking downside than free text and is the honest price of the first bullet.
- **The list is a maintenance obligation on this page.** A writer added without adding its line is a
  writer the check will report, forever, until somebody writes the line — which is the intended failure
  direction: the report complains rather than the row lying quiet.

---

## D-126 — Break-glass is a report and a written procedure, not a mechanism

**Status:** decided (from your answer)
**Date:** refinement round 17
**Closes:** [F-26](../open-questions.md#f-26)
**Widens:** [check 9](../data-model/05d-invariants-and-seed.md#11-invariants-to-verify) gains its second
column — who *can sign in*, not only who could hold it.
**Adds a home, not a feature:** the procedure lives in
[domain/02-actors §3](../domain/02-actors.md#when-nobody-who-can-hold-systemadmin-can-sign-in), beside the
state machine it operates
on. **Reverses nothing.**

**Decision. Three parts, none of them a mechanism.**

1. **The report.** Check 9 already lists everyone with a live allow of `system.admin`, however they came by
   it, and already emails someone when its result changes. It gains a second column: **for each of them, is
   `account.status` `active`, and is their credential live** (`account_credential.valid_to` unset or in the
   future, not revoked — the table is
   [01a §5](../data-model/01a-accounts-and-contacts.md#5-account_credential)). **The alert is the new half:** an empty result — a
   world where somebody could hold the capability and nobody can reach a screen — goes to the same place
   check 9 already goes, within the hour.
2. **The procedure.** Written where account state is described, and it says what to do *before* it says how
   to recover: who is the person who can be telephoned, who may ask them, and what gets written afterwards.
   **The recovery is performed on an account, never on a grant** — an un-suspended account, a re-issued
   credential, and then the ordinary screens, so every authority change that follows is an application write
   with `granted_by` and an audit row like anybody's. **D-120's `owner_person_id` is explicitly not the
   person to telephone**; that column answers *whose integration is this*, not *who fixes it*.
3. **What the model still refuses.** A sealed `recovery` key holding `system.admin` stays refused, and the
   refusal is unchanged from [D-121](round-16.md#d-121--a-key-never-carries-a-persons-authority) and
   [D-122](round-16.md#d-122--what-a-key-owes-the-catalog-four-codes-at-the-unit-and-the-fourth-owed-thing-declined):
   a key carries nobody's authority and may not hold that code, so it cannot be the thing that walks in when
   a person cannot. A time-boxed self-service path stays out too — it is a request, an approver, an expiry
   and a family of codes, which is a module, and this design has no self-service anywhere: nobody joins,
   appoints or un-suspends themselves, and an emergency path that lets somebody do that would be the second
   and weaker authorization this corpus rejects by name.

**The honest limit, which is the reason the report is the answer and not the escape hatch.** The recovery
edit is made outside the application, so it writes no audit row, and nothing in the schema distinguishes a
legitimate recovery from a hand-edited account. This corpus's habit when it refuses to design a bypass is to
name the gap in a check, so that gap gets one: **a row in an audited table whose newest audit row predates
its `updated_at`** — a change the trail never saw. It is a bullet in
[06b §5](../data-model/06b-redaction-and-checks.md#5-integrity-checks), appended rather than inserted so no
existing check changes number, and it is a report rather than a guard, like the two beside it. **What it
cannot catch:** an edit that also inserts its own audit row by hand — the trail is append-only to the
application, not to whoever holds the database — and, after twenty-four months, nothing: payload reduction
empties the values and keeps the row, so coverage outlives content by design
([D-088](round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)).

**What it costs, stated as costs.** The report is somebody's job and says so in the domain page; an empty
result may be entirely ordinary in an organization where the treasurer does everything, so the alert reads
as a question rather than an incident; and the new check is one more line that will be mostly empty and has
to be read anyway, because it is exactly the line that is quiet until the day it is not.

---

## What this round changes elsewhere in the corpus

- **A new section, [00-conventions §7a](../data-model/00-conventions.md#7a-what-an-empty-actor-column-means)**,
  is where the meaning lives. `05c §9`, `06 §2`, `06b §5` and `05e §17` cite it instead of each carrying
  their own sentence about NULL — which is how the four of them came to disagree in round 16.
- **`actor_label` is no longer free text** where the trail has one: its examples become the five labels
  above, and bare `system` is retired. The forensic-gap check's "gap" narrows to *a write path that owed a
  person and named none, or a label outside the list*.
- **Check 9 gains a column and an empty-result alert**; `05d §11` says what the second column is read from.
- **One check appended to `06b §5`**: an audited row whose newest audit row predates its `updated_at`.
- **`domain/02-actors §3` gains the procedure** — the first place in the documentation where something is
  written down as something a person *does* rather than a state the system holds.
- **Both questions leave [open-questions.md](../open-questions.md)** with one row each in § R, so every link
  written against `F-25` and `F-26` this month still lands somewhere true.

## What this round refused, and what it still declines

- **A `system_writer` registry, and a secretless kind of `api_key`.** Both were on F-25's page and both are
  declined for the reason on that page: a table whose rows may or may not carry a secret is a table whose
  invariants become conditional, and a job is not a caller and should not have to authenticate. **The
  vocabulary buys the same report for no column.** If a fourth writer arrives whose name cannot be fixed
  this way, that is the moment to reopen this, not before.
- **A fourth kind of caller.** This system is not a caller: it holds no grants, appears in no `role_holder`
  row, and cannot be aimed at by a grant. Reading an empty actor column as "the system" is a rule about
  attribution, and it changes nothing about who may hold what — the reason `api_key` stayed at three grantee
  kinds and thirteen selectors stayed at thirteen.
- **A recovery mechanism of any kind** — sealed credential, emergency grant template, break-glass screen.
  The refusal is the decision. What is designed is the visibility, and the writing.
- **Whether `system.admin` should be held by more than one person as a rule.** F-26 asked whether a minimum
  should be seeded. It is not, because the report makes a single-holder world *visible* and a seeded minimum
  would only make it quieter — and [D-120](round-16.md#d-120--a-key-outlives-whoever-created-it-and-the-report-is-the-control)'s
  posture is the report, again. **It stays a decision the organization makes, and the alert is what makes it
  an informed one.**
