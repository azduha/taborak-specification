# Data Model — Authorization: `access_log` and the resolver

What a check writes down, and the one place in the system that computes an
answer.

**Section numbers are shared across the five parts** and never renumbered, because other
pages cite them by number and their anchors are built from them: [05-authorization.md](05-authorization.md) holds §1–§7, [05a](05a-audience-and-grammar.md) §8 (the `audience` table, the grammar, the selector registry), [05b](05b-expression-tree.md) §8 continued (the tree and what each operand costs), [05c](05c-access-log-and-resolver.md) §9–§10 (`access_log` and the resolver), and [05d](05d-invariants-and-seed.md) §11–§13 (invariants, seed data, open issues).

---

## 9. `access_log`

The audit trail. Append-only; no updates, no deletes.

**Fields**

| Field | Kind | Notes |
|---|---|---|
| `id` | integer identity | Surrogate key. |
| `occurred_at` | timestamp, audit time | Default now. |
| `actor_person_id` | reference to person, optional | Who performed the action. Absent for system actions. |
| `subject_person_id` | reference to person, optional | Whose data was affected. Differs from the actor when acting on behalf. |
| `on_behalf` | boolean | Default false. True when the actor and the subject differ and the action was performed **for** the subject — guardianship, delegation. See [04-relationships.md](04-relationships.md) §6. |
| `authorization_channel` | enum: `deny`, `ownership`, `guardianship`, `unit_grant`, `item_grant`, `none`, or absent | Which channel answered this. Makes the audit answerable: "by what authority did this person do that?" `deny` records that a deny row defeated the allows; `none` records that nothing answered at all. **Six values, and `role` is not one of them**: there is no role channel to name ([D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)), and `system` was never a channel rather than a namespace. **An answer of `role` in an old row is now unreadable by the model that reads this table**, which is the honest state of a historical value: the audit trail keeps the word that was written, and nothing can keep a channel that no longer exists. |
| `authorization_ref_id` | integer, optional | No foreign key: it names a row in one of several tables — `access_grant.id` or `guardianship_permission.id`. Lets an auditor go directly to the grant that permitted the action. |
| `permission_code` | text, optional | The permission checked, as its code. Absent for pure read events that are logged for access-trail purposes rather than permission decisions. |
| `scope_type` | text, optional | `unit`, or an item type. |
| `scope_id` | integer, optional | Absent for a check at the unit. |
| `action` | text, required | `membership.request.approve`, `person.view`. |
| `entity_type` | text, optional | |
| `entity_id` | integer, optional | |
| `result` | enum: `allowed`, `denied`, `error` | Required. |
| `denial_reason` | text, optional | |
| `session_id` | text, optional | Acting context, for forensics. |
| `ip_address` | an IP address, optional | Acting context, for forensics. |
| `user_agent` | text, optional | Acting context, for forensics. |
| `request_id` | text, optional | Acting context, for forensics. |
| `before_state` | free-form jsonb, optional | For write actions. |
| `after_state` | free-form jsonb, optional | For write actions. **Redacted fields must be stripped before logging** — an audit log that leaks the data it audits is worse than none. |

**Rules**

- A `denied` result carries a `denial_reason`. There is no unexplained denial in this table.

**Indexes**

- the subject lookup covers only rows that name a subject;
- one index over denied rows only, newest first;
- one over acting-on-behalf rows only, newest first.

**`authorization_channel` and `authorization_ref_id` are what make this an audit trail
rather than a log.** A record saying "person 100 changed person 200's address" answers
*what* and *who*. A record that also names the `guardianship_permission` row that
authorized it answers *why they were allowed to* — and whether that authority was valid at
the time. When a custody dispute arises eighteen months later, that is the question asked.

**Every value in that enum names a row the auditor can open.** `unit_grant` and `item_grant` are the two
ways a permission is granted, and a grant names one code, so the row answers "by what authority" with the
authority itself. **Why that is worth stating:** an audit answer naming a *bundle* is not an answer — the
reader still has to expand it into codes to learn what the person could actually do, and the table that
used to do the expanding holds nothing
([D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)).

**`denied` results are logged too.** A series of denials is the signature of someone
probing for access they do not have. Logging only successes discards the signal.

**`before_state`/`after_state` must be redacted before the insert.** Copying a value out of a guarded record into a table guarded by different
people, on a different path, for longer than the record is kept, produces a copy with less protection
than the original — and the copy is the one that gets read by auditors, exported for reports and
mirrored into backups. Redaction therefore happens **before the insert**, in the logging function, and
never in a job that might not run — the ordering is the part of this rule with teeth. **No database
constraint can carry this one**, because a constraint sees the row after the values are already in it, and
this rule is about never letting them in: it is the application's obligation, and it is stated with the
redactor itself in
[06-audit-and-import.md §2.2](06-audit-and-import.md#22-redaction-before-logging). This is a rule of
[00-conventions.md §6a](00-conventions.md#6a-who-enforces-an-invariant-now)'s last kind — no automatic
enforcement reaches it — so it is written as an obligation, not as a guarantee.

**A retention window does not weaken this rule, and it is worth seeing why.** If
[F-8](../open-questions.md#f-8--retention-policy-for-access_log) is confirmed, this table's state columns
expire on the window
[D-088](../decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)
proposes for the change trail, so the copy is *shorter-lived* than the business row it was copied from.
The conclusion is unmoved, because what the rule guards is the
*audience*. A window decides how long a copied value is readable; it does not decide who may read it
while it is readable, and the readers here are whoever holds `audit.view`, not whoever may see the
record. A sensitive value copied into a less-protected table is a protection failure on the day it is
copied, not only for as long as it then survives.

**How far the argument reaches.** It is an argument
about *the copy's guard*, not about the copy's contents, so it is **not** an instruction to empty
payloads. [D-083](../decisions/round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)
refused the subset a field list would select from — everything about a person beyond name, gender and
age is a value in `person_attribute` ([09-attributes.md](09-attributes.md)) — which rules out
name-keyed scrubbing of personal data for good: there is no list, and `allergy` is not on it. It leaves
two conclusions, and they point in opposite directions from the obvious one:

- **The credential case stays, and it is the only one a name list can serve.** Values where *being in a
  log at all* is the harm — secrets, tokens, credentials — are stripped on the way in, by key name,
  everywhere a listed key turns up ([06-audit-and-import.md §2.2](06-audit-and-import.md#22-redaction-before-logging)).
- **The person-data case is answered by grading the copy, not by thinning it.** `audit_log` holds
  before and after images of a child's descriptive values, because
  [D-085](../decisions/round-07-08.md#d-085--the-identity-machinery-stays-structured-the-boundary-is-rules-not-sensitivity)
  made that trail the only history those values have. So **"the copy must not be less guarded than the
  original" is a requirement on `audit.view`'s sensitivity mark** — the top tier, beside `person.view` —
  and not a rule about which keys may appear in a jsonb column. Written as a requirement in
  [00-conventions.md §8 item 7](00-conventions.md#8-personal-data-and-erasure) and demanded of the
  catalog in [../appendix/permission-catalog.md §8](../appendix/permission-catalog-a-codes.md#8-audit-and-system);
  erasure reaching those payloads stays absolute
  ([06-audit-and-import.md §4](06b-redaction-and-checks.md#4-redaction-log)).

**Append-only enforcement:**

Any update or delete against `access_log` is refused row by row, before it happens, with an
error saying the table is append-only. Nothing is left to the application remembering this.

**Two operations are excepted, and a blanket refusal would defeat the retention policy.**
Emptying a row's payloads once it passes the window below is an update, and so is scrubbing one person's
values out of a row after an erasure. Neither is a correction: nobody is making a version of this table
right, and the answer the row gives to *who, what, when, by what authority* is untouched in both cases.
So both fall inside what "append-only" forbids in spirit and outside what it may forbid in practice.
**State the guard as a refusal of rewrites rather than a refusal of writes** — the only actor allowed to
change a row is the erasure or the reduction, the only columns either may touch are the state columns,
and every other field on the row is immutable. The literal version of this rule is the more dangerous
one, because it fails silently and what it fails is the policy. The same reasoning applies to
`audit_log` and is stated with the operations themselves in
[06-audit-and-import.md §2.2](06-audit-and-import.md#22-redaction-before-logging).

**Retention: a proposal, not this document's position.** The window that
[D-088](../decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)
puts on `audit_log`'s payloads is proposed here too — **24 months on the state columns, rows kept,
12 months as the floor** — and it is recorded as
[F-8](../open-questions.md#f-8--retention-policy-for-access_log), **which still needs confirming**.
Whether an audit trail is bounded at all is a legal question rather than a technical one, so until someone
confirms it this is a default awaiting a person.

**Why the question is weaker here, which is structural and not luck: this table does not hold the
contents of reads.** `before_state` and `after_state` are populated for write actions only, so a read
records *who asked, for what, under which permission, through which channel, and whether it was
allowed* — and stops. Recording what the read *saw* would copy every record a permitted glance touched
into a table read by a wider audience than the record itself, which is the exact act the redaction rule
above exists to prevent. So the window here protects considerably less than it protects
over in `audit_log`, and what survives it is everything this table was built to answer. **The valuable
fact about a read is that it happened and by what authority, and that is precisely the part no
reduction touches.**

Consider partitioning by month once volume justifies it, and moving old partitions to
cheaper storage. Rows are not deleted on either answer; the window is carried out by emptying the state
columns, which is the job and the over-age check described for the change trail in
[06-audit-and-import.md §5](06b-redaction-and-checks.md#5-integrity-checks). **If F-8 is confirmed, that check
has to be written for this table too** — a reduction with no check under it is a reduction that quietly
stops happening, which is the failure mode §2.2 of that document names as the only one this operation
has.

*Assumption:* `access_log` may be queried by staff with a specific permission, but writing
is automatic. If the organization needs human annotation of audit entries, add a separate
`access_log_note` table rather than making this table mutable.

---

## 10. The resolver

### Steps the resolver leans on

**Three helpers keep `can()` readable, and one of them is fifteen lines long.**

**`grant_satisfies(person, scope_type, scope_id, permission, at)`** — does the person hold a live
**allow** of **this code** on **this exact scope**? Exact match only. It covers both a personal grant
and one made to an audience the person is in. Any one grant row meeting all of these satisfies it:

1. Its `scope_type` equals the checked scope type and its `scope_id` matches the checked scope
   id, with an absent id equal to an absent checked id.
2. Its `permission_id` **is** the checked permission, or is `system.admin`.
3. Its `effect` is `allow` — denies are handled by the channel that runs first.
4. It has not been revoked.
5. It has started as of `at` and has not ended on `at`.
6. The grantee is this person, or an audience containing them at `at` for this item (§8).

**The question has a yes-or-no answer, not a threshold.** There is no rank to compare and nothing to join
in order to get one: a grant carries exactly one code and either it is the checked code or it is not
([D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)).

**`person_in_audience(person, audience, at, item)`** — is the person in the value of this audience's
expression on this date? The `item` argument is there because a bound operand means
different people on different items, and there is no other way to tell it which event it is asking
about (§8, *Evaluation*). An unresolvable operand is the empty set; an expression that cannot be
evaluated reaches nobody.

**`operand_holds(person, operand, at, item)`** — the evaluator's one recursive step: a leaf asks its
selector, a node combines its children. **It is written once and it is short**; the requirement
inside it is that every selector is evaluated as a predicate about this person and never as a set of
ids (§8, *Author in sets*).

**One leaf does not ask a selector, it asks this function again.** `AUDIENCE(x)` calls
`person_in_audience(person, <the audience x names>, at, item)` and returns what comes back
([D-103](../decisions/round-10b.md#d-103--an-audience-may-name-another-audience)) — the same three
arguments carried straight through, because a nested audience means the same people on the same date
for the same item, and **the same predicate shape, because nesting is the moment at which a lazy
implementation would most plausibly decide to materialize the inner set and test containment.** That is
§11's check 16 and it covers recursion explicitly. **What the recursion costs:** within one request the memo
resolves a recurring named operand once, so a screen that asks the same question about the same person
several times pays the depth once; **across requests it runs to whatever depth somebody typed, every time**
([D-114](../decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation)).
That is the honest price of a tree with no bound on its height, which is why §*What each operand costs* and
the width report of §*The cost of composition* are the controls here. **The recursion terminates by
construction, not by a counter**: a cycle through `AUDIENCE` leaves cannot be saved (§8), so a read-path
depth cap would be a thing that decides who a grant reaches in exactly the case where the data is already
wrong. **The save-time cycle walk is therefore the whole guard, and it must not be relaxed**: "the
recursion terminates by construction" is a claim about a write-path check, not about a number.

**No channel of `can()` consults membership, and that is a guardrail rather than an omission.**
A membership test performed inside the resolver is an invisible lockout: somebody whose membership lapsed
is denied by the rule that was supposed to exempt them, with no error message, on the one day of the year
it would hurt most. Nothing in this function asks the question, so nothing can be mis-routed — membership
is `MEMBERS`, an operand in an expression, evaluated where expressions are evaluated (§8).

The single authorization entry point. One implementation, used everywhere. Algorithm:
[../domain/06-authorization-model.md](../domain/06-authorization-model.md#6-the-resolver).

**`can(person, permission_code, scope_type, scope_id, at, owner_person_id)`** returns allowed
or denied. `scope_type` and `scope_id` are optional, `at` defaults to today, and
`owner_person_id` is supplied only where the ownership or guardianship channel is in play.

**The order of these steps is a rule for one reason and not the other.** Each step either returns or
falls through, so a step never gets to contradict an earlier one. **The deny step must run first, and
that is the only ordering with a consequence for the answer.** The allow steps are alternatives
producing the same boolean, so their order decides **which channel the audit names** and how quickly
the answer arrives — never what the answer is. **That is what having no locality means**
([D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)):
the allow steps are not ordered by strength, and "the nearest one wins" is not a sentence about this
function.

1. **Look the permission up by code.** If no permission carries that code, **return false** —
   an unknown permission is a deny, and it is settled before anything else is considered.
2. **Resolve merge chains.** Replace the person with the survivor of any merge, so permissions
   are never evaluated for a tombstoned person.
3. **Channel 0 — explicit deny. Absolute and scope-independent.** A live `deny` grant of this code
   applicable to this person blocks access no matter **what** scope it sits at: a per-event grant can
   never restore access that a unit-wide restriction removed
   ([D-013](../decisions/round-01a.md#d-013--explicit-deny-revoked-is-checked-before-everything)).
   A deny counts when it is itself unrevoked, has started as of `at`, has not ended on `at`, and
   applies to the person — where "applies" means it names them **or** names an audience they are in
   at `at` for the item being checked. A personal deny and an audience deny are equally absolute, and
   **a personal allow cannot beat an audience deny, because channel 0 has already returned.** Its
   scope applies when either of these holds:

   - it sits at the **unit**, and then it applies everywhere — every item of every type, because a
     unit grant reaches every item and a unit deny is the same shape with the opposite effect;
   - it sits on the exact thing being checked — same scope type, same id.

   **A deny matching either bullet is the whole answer: return false.** There is no case in which a deny
   at the unit reaches less than everything under it, because there is nothing under it to reach — the unit
   is a scope and there is exactly one of it
   ([D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)) — so no
   walk between scopes stands between a restriction and the item being checked.
4. **Channel 1 — a grant at the unit.** `grant_satisfies(person, 'unit', NULL, permission, at)`.
   Because a unit grant reaches every item of every type (§6), this one step covers every item the
   organization has.
5. **Channel 2 — a grant on this exact item.** `grant_satisfies(person, scope_type, scope_id,
   permission, at)`, reached only when both a scope type and a scope id were supplied. **Nothing is
   consulted before it**: a unit grant reaches the item, an item grant reaches the item, and there is no
   owner to ask
   ([D-102](../decisions/round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)).
6. **Channel 3 — ownership.** If an owner was supplied and that owner resolves to this same
   person, **return true**. Your own data.
7. **Channel 4 — guardianship. Consulted when the check is about someone other than the actor;
   answers with an allow only.** The test is a comparison, not a name: an owner was supplied, it
   resolves to a real person, and that person is **not** the actor. The question is whether the
   actor holds a **live guardianship over that subject at `at`** whose `right_level` covers the
   checked permission — and **this is where `permission.right_kind` is read, by its only customer**:
   `none` covers nothing, `view` covers codes marked `read`, `write` covers both.
   **If such a guardianship exists and covers the permission, return true. In every other case — no
   guardianship, `none`, or a right that does not cover this code — the channel returns nothing at all
   and the resolver continues.** It does not deny. Defined in
   [04-relationships.md §4](04-relationships.md#4-how-the-resolver-uses-these-tables); the reasoning
   for both halves is
   [D-079](../decisions/round-06.md#d-079--the-guardianship-channel-is-entered-by-shape-not-by-permission-name).

   Two properties of this channel:

   - **Entered by shape, not by namespace** (D-079, following D-074). A parent correcting their
     child's address is checked under `person.address.edit` — an ordinary, un-prefixed code — and
     still routes here. A permission added next year for a field a guardian must edit is covered
     the day the field exists, provided it is marked `write`, which is the seeding default (§2).
   - **Silent rather than final.** The channel never takes the last word: a guardian whose right does not
     cover the code simply does not answer, and the actor's own grants get their turn. There is no partial
     answer to fall through either, because the channel returns a yes and nothing else. **A real
     prohibition is still possible and still absolute — it is a deny row, step 3.**

   **Two refusals belong to this channel.** The guard must not be weakened into "the subject is a minor":
   the existence of a guardianship row is the whole test, and an age lookup would put a branch in the
   resolver that D-070 and D-077 rule out. And personal attributes reach this resolver through no new
   door — everything beyond name, gender and age
   is descriptive data read by `person.view` and written by `person.edit` through the channels above,
   with no `attribute.*` read permission, no fifth channel, and no branch on *what a value is about*
   ([09-attributes.md §4](09-attributes.md#4-who-may-read-and-who-may-write),
   [D-083](../decisions/round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)).
   **The temptation this channel is offered — "a leader may see allergy data, but only for the children in
   their unit" — is refused twice.** There is no "their unit" for such a rule to refer to
   ([D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)), and the
   older reason stands on its own: a branch on *what a value is about* is the privileged medical subset
   walking back in through the resolver after
   [D-083](../decisions/round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)
   refused it through the permission list.
8. **Default deny. Return false.**

> **There is no membership gate anywhere in this function.** `MEMBERS` is an operand a writer types into an
> expression, and no channel of the resolver consults membership: a check is about grants, not about whether
> the actor is a paid-up member
> ([D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)).
> The predicate `is_current_member` exists only inside the evaluator, evaluated live at `at` like every
> other operand. Every intent a gate would have served is written in the expression that carries the rule:
>
> | Intent | Expression |
> |---|---|
> | The office counts only while its holder is a member | `MEMBERS * ROLE(x)` |
> | The office counts whatever their membership looks like | `ROLE(x)` — written without `MEMBERS` |
> | The office counts, but one named person is an exception | `MEMBERS * ROLE(x) + PERSON(y)` — the exception sits inside the grant that carries the rule, so it is read next to the thing it exempts. A second grant aimed at that person alone is equivalent, and arguably clearer for something permanent; what is never allowed is a row that does not parse (§8, `PERSON`) |
>
> **The posture is opt-in, and the failure mode is named rather than buried** (D-100). Forgetting `MEMBERS` is invisible, silent and permanent, and nothing in the
> resolver can see it. Three controls, none of which is the resolver: the standing report of
> `ROLE(...)` grants with no `MEMBERS` (check 6, §11); seeded grants carrying `MEMBERS` so that the
> path of least repetition is the safe path; and **import completeness** — `MEMBERS * COUNSELORS` is
> only as correct as the counselor roster, so an import that misses 300 counselors silently un-gates
> them, and the reconciliation report of
> [D-090](../decisions/round-07-08.md#d-090--the-legacy-corpus-is-thousands-of-roster-rows-with-numbers-and-no-money)
> must count people marked as counselors in the corpus against `role_holder` rows written. **It fails
> closed — nothing breaks, which is exactly why nobody notices.**

### The cache is deleted: nothing in this schema holds a permission answer

**Nothing in this schema holds the answer to a permission question.** No row, table or field anywhere maps a
person — or a person and a code, or a person and an item — to an answer. That is
[§11's invariant 19](05d-invariants-and-seed.md#11-invariants-to-verify), and it is why no later optimization
can reintroduce such a table rather than merely disliking it. **A check resolves, a request memoizes, and the
only thing ever cached is a compilation**
([D-114](../decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation)).
The rule is unconditional on purpose: the expansion of an audience is a predicate and not a set
(§*Author in sets. Evaluate per person.*, §*Evaluation*), and a design that forbids a materialized answer in
one path and permits it in another spends the rest of its prose explaining the difference.

**What the checks use instead, and what may be held in memory:**

1. **A compiled expression.** Parsed once, operand kinds resolved once, a parameterized predicate emitted once,
   keyed by the expression's root and `ruleset_version`, **holding no person and no item**. It is process-local
   and **not a table**: nothing about it is queryable, durable, or a source of truth, and a restart discards it.
   `ruleset_version` bumps on **`audience_operand`** — a subtree changed, so every compilation embedding it is
   stale — and on **`selector_type`**, because the vocabulary changed. On nothing else, and the absences are the
   design:
   - `access_grant` is absent because **grants are not compiled**: a check reads the person's live grant rows, so
     adding, editing or revoking one changes what that read returns and leaves nothing stale to drop. Where a
     grant is created together with a new audience, the write that matters is the one on `audience_operand`,
     which *is* in the set;
   - the `deprecated | hidden | disabled` flag is absent because **a state is not compiled in** — resolution
     consults it live, once per request, which is also what makes `disabled` take effect now
     ([D-109](../decisions/round-13.md#d-109--nothing-a-rule-names-is-deleted-deprecated-hidden-disabled--and-a-tab-instead-of-a-report));
   - `role_holder`, `person_group_member`, `guardianship_permission`, `event_registration`, a membership
     transition and a person merge are absent because **there is no answer to invalidate**. That is also what
     [03-membership.md §6](03-membership.md#6-membership-and-the-authorization-system) asks of the yearly sweep.
2. **A request-scoped memo.** The checked person's live grant rows, read once; within the same request, a named
   operand that recurs. **Lifetime is the request.** It is worth stating in a data model precisely because it is
   *not* one: it needs no section, no index and no invalidation list, because it is shorter-lived than any
   question about consistency.
3. **Two batch reads**, `can_many(person, codes[], item?)` and `which_of(people[], code, item)`, so a screen is
   one resolution rather than a loop. **`which_of` is not a materialization** — it evaluates the predicate for
   people already in hand; what stays forbidden is deriving a set in order to answer about one person.

**Named rosters are the one thing held across requests**: `ROLE(x)` and `GROUP(x)` keyed by the name,
holding **the dated rows or the set with its validity ranges**, never the set as of today, so the checked date is
applied at check time and a period ending at midnight needs no job. **This one is allowed because its key is the
thing the write touches:** a `role_holder` insert invalidates one roster, by identity, without asking whom it
reaches.
**And one exclusion, so the exception does not eat the rule:** `MEMBERS` is **not** a roster and may not be cached
this way. It is not a row anybody writes — it is the read predicate over `membership`, whose dated rows the
**1 January sweep** rewrites for every member at once, which is exactly the bulk event that must never need an
invalidation list. **A roster is a set with a name and its own holder rows;
`MEMBERS` is neither**, and the two age operands beside it are a birth date read at the checked date, which is not
a cacheable set either (§*What each operand costs*).

**Invalidation runs from the tree, never from the people.** An edit to a shared audience invalidates the set of
**compilations** that embed it — finite, enumerable, and named by rows that already exist, by walking the
**reverse closure** over `audience_operand`: which expressions embed the audience being written. The
unenumerable side — whom a rule reaches — is never attempted.
**Note the direction, because the save path already walks the other one:** the cycle refusal of
§*The expression tree* and check 15 walks **forward** from the tree being saved, while invalidation needs the
**reverse** direction — the same one the delete-refusal check walks when it asks whether a live grant, or a live
audience reachable from one through any number of `AUDIENCE` leaves, names this audience (§*The expression tree*,
§11 check 15). **So this is a new use of an existing direction, not a free ride on an existing query**, and the
listing whose cost §13 still registers as unverified is the same listing: **what this reversal inherits is that
open question, not a solved one.** It is recorded there rather than resolved here.

**What an index is for here.** A check reads the person's grants directly, so the index that matters is the
ordinary one on `access_grant(grantee…)`, which the resolver needed anyway. Nothing expires, so there is no
sweep and no column to sweep by. At the size
[D-112](../decisions/round-13.md#d-112--the-systems-scale-is-stated-hundreds-of-people-tens-of-registrants-per-event)
states, that is the whole performance story of this section.

**What none of this touches.** The merge and redaction duties on `audience_operand` leaves (§*A hand-named person
is now a keyless reference*, §11 check 2) **remain urgent**: a missed repoint writes nothing, so nothing is
triggered, and the dangling leaf under `-` **denies everybody**. Two other rules belong to this part of the
design and to no storage at all: the **bound-operand rule** — an operand computed while checking one item may
never answer for another, which is a rule about how a predicate is bound
([D-102](../decisions/round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it))
— and D-109's check pair, *"deprecating or hiding must not change an answer"* and *"disabling takes effect now,
and must say whose"*, both properties of resolution.

### Properties to verify when reviewing this function

1. **Deny is checked before everything**, including ownership and guardianship. A restricted
   account's owner permissions are denied by a `deny` row if that is what the organization wants.
2. **`at` is threaded through every branch.** Permission checks are time-travel capable, and an
   operand evaluated at "now" inside a check performed at a past date is a wrong answer that looks
   like a right one.
3. **There is no wildcard except `system.admin`.** No prefix match, no implied capability.
   If a holder can do a thing, a row says so (D-068), and the row says **which** thing: no level
   stands in for a set of them.
4. **`resolve_person` is called on entry**, so a tombstoned person's id still resolves.
5. **A deny is scope-independent.** Channel 0 matches a unit deny and an exact-item deny and does
   **not** walk ancestors — so a deny at the unit blocks every item, which is what makes a
   suspension absolute.
6. **There is no hierarchy to walk.** There is one unit and it is not a row, so a grant is either at
   the unit — and then it reaches every item — or on the exact item, and no comparison between the two
   needs a walk
   ([D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)).
   **The time-bomb in this function is a different one** — no permission path may materialize a set of
   people — and it is check 16 (§11).
7. **Audience grants are evaluated through the same channels as personal ones**, via
   `grant_satisfies()`. A grant to `EVERYONE` and a grant to a named person differ only in how
   *grantee* is satisfied, never in how the scope or the code is resolved.
8. **Expression evaluation is a walk over a forest that fails closed.** An unresolvable operand is the
   empty set, and an expression that cannot be assembled reaches nobody (§8, *Evaluation* item 5).
   **The failure this property forbids is a helpful implementation**: a walk that returns what it
   managed to reach when something downstream breaks turns a broken expression into a widening, and a
   widening is the only direction in which this channel can do harm. **Forest, not tree, since
   D-103** — the walk crosses an audience boundary at an `AUDIENCE` leaf, and a partially-evaluated
   outer tree over a failed inner one is precisely the shape that produces a widening.
9. **A check that supplies no item cannot answer a bound operand, and must not guess one.** `PLACED`
   with nothing to bind to is not "everyone" and not "nobody at this unit" — it is a caller error, and
   the answer is denial with a `denial_reason` that says so. **This is the cousin of the
   unscoped-check caveat below, and it is enforced in the same place: the calling convention, not the
   data.**
10. **`right_kind` is read in exactly one place.** If a second comparison of `read` against `write`
    appears anywhere else in the resolver, that is a mechanism being built on a column D-099 documents
    as having one customer.
11. **A nested audience is evaluated at the caller's `at` and the caller's item, with neither
    re-defaulted** ([D-103](../decisions/round-10b.md#d-103--an-audience-may-name-another-audience)).
    The recursion has to carry all three arguments through or it is not the same question being asked
    again, and **of the two, the silently wrong one is the date**: an inner audience re-defaulted to
    today answers *"was she in it?"* with *is she in it*, which is the exact substitution property 2
    exists to forbid, one level down and invisible in every test that checks only one audience.

**A caveat on an unscoped check.** "Can this person do X anywhere?" returns true if *any* grant
grants it. That is correct for UI decisions like "show the admin menu?" but **wrong for enforcement**.
Every enforcing call must pass a scope. Enforce this in the calling convention — make scope mandatory
at the API layer for mutating operations.

What may be cached is written immediately after the resolver rather than in a deployment note because it is
part of a check's contract: **the question was never only where to keep answers, it was what a check is**
([D-114](../decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation)).

The person-merge case remains the easiest to forget —
see [01b-merges-views-and-checks.md §8](01b-merges-views-and-checks.md#8-identity_hypothesis-and-person_merge).

---

*Decisions behind this page: D-013, D-068, D-070, D-072, D-074, D-077, D-079, D-083, D-085, D-088, D-090,
D-097, D-099, D-100, D-102, D-103, D-109, D-112, D-114.*
