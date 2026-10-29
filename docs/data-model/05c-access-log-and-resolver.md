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
| `authorization_channel` | enum: `deny`, `ownership`, `guardianship`, `unit_grant`, `item_grant`, `none`, or absent | Which channel answered this. Makes the audit answerable: "by what authority did this person do that?" `deny` records that a deny row defeated the allows; `none` records that nothing answered at all. **`role` and `system` are gone from this enum** — there is no role channel to name ([D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)), and `system` was never a channel rather than a namespace. **An answer of `role` in an old row is now unreadable by the model that reads this table**, which is the honest state of a historical value: the audit trail keeps the word that was written, and nothing can keep a channel that no longer exists. |
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

**The channel enum got smaller in round 10 and the audit answer got better, which is worth saying in
the same breath.** `item_grant` and `unit_grant` are now the only two ways a permission is granted,
and both name a row the auditor can open. Under the ladder, a row saying `role` plus an assignment id
answered "by what authority" with a *bundle* — the auditor still had to expand `manage` into codes to
learn what the person could actually do, and the table doing the expansion was `permission_level`.
**Now the row names the grant, and the grant names one code.** That is the one place where deleting
the levels makes the trail more useful rather than less.

**`denied` results are logged too.** A series of denials is the signature of someone
probing for access they do not have. Logging only successes discards the signal.

**`before_state`/`after_state` must be redacted, and the sentence is the reason this document is
cited everywhere else.** Copying a value out of a guarded record into a table guarded by different
people, on a different path, for longer than the record is kept, produces a copy with less protection
than the original — and the copy is the one that gets read by auditors, exported for reports and
mirrored into backups. Redaction therefore happens **before the insert**, in the logging function, and
never in a job that might not run — the ordering is the part of this rule with teeth, and it survives
[D-072](../decisions/round-06.md#d-072--the-documentation-carries-no-sql-the-schema-is-the-orms-job)
taking the trigger that used to enforce it.

**One clause of that sentence is now bounded, and the bounded half is not the half that mattered.**
*For longer than the record is kept* was written when this table's state columns and `audit_log`'s
payloads were both permanent. If
[F-8](../open-questions.md#f-8--retention-policy-for-access_log) is confirmed, the state columns expire on
the window
[D-088](../decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)
proposes for the change trail, which inverts that arithmetic: the copy becomes shorter-lived than the
business row it was copied from. The conclusion is unmoved, because what the rule guards is the
*audience*. A window decides how long a copied value is readable; it does not decide who may read it
while it is readable, and the readers here are whoever holds `audit.view`, not whoever may see the
record. A sensitive value copied into a less-protected table is a protection failure on the day it is
copied, not only for as long as it then survives.

**How far the argument reaches, now that the person record has no sensitive corner.** It is an argument
about *the copy's guard*, not about the copy's contents, and reading it as an instruction to empty
payloads is the mistake this section made once and corrected. [D-083](../decisions/round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)
removed the subset that a field list selects from — everything about a person beyond name, gender and
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
  catalog in [../appendix/permission-catalog.md §8](../appendix/permission-catalog.md#8-audit-and-system);
  erasure reaching those payloads stays absolute
  ([06-audit-and-import.md §4](06-audit-and-import.md#4-redaction-log)).

**Append-only enforcement:**

Any update or delete against `access_log` is refused row by row, before it happens, with an
error saying the table is append-only. Nothing is left to the application remembering this.

**That sentence has two exceptions, and written as a blanket refusal it defeats the retention policy.**
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

**Retention: the same window as `audit_log`'s payloads, as a proposal rather than a decision.** This
paragraph used to read *"never delete them — the partition retention policy is a legal question, not a
technical one"*, and the second half of that is still exactly right. What has changed is that the
decision which bounded the change trail's payloads
([D-088](../decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short))
proposes the same window here — **24 months on the state columns, rows kept, 12 months as the floor** —
and records it as [F-8](../open-questions.md#f-8--retention-policy-for-access_log), **which still needs
confirming**. Until it is confirmed, that is a default awaiting a person and not this document's
position.

**Why the question is weaker here, which is structural and not luck: this table does not hold the
contents of reads.** `before_state` and `after_state` are populated for write actions only, so a read
records *who asked, for what, under which permission, through which channel, and whether it was
allowed* — and stops. Recording what the read *saw* would copy every record a permitted glance touched
into a table read by a wider audience than the record itself, which is the exact act this section
argues against two paragraphs above. So the window here protects considerably less than it protects
over in `audit_log`, and what survives it is everything this table was built to answer. **The valuable
fact about a read is that it happened and by what authority, and that is precisely the part no
reduction touches.**

Consider partitioning by month once volume justifies it, and moving old partitions to
cheaper storage. Rows are not deleted on either answer; the window is carried out by emptying the state
columns, which is the job and the over-age check described for the change trail in
[06-audit-and-import.md §5](06-audit-and-import.md#5-integrity-checks). **If F-8 is confirmed, that check
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

**Two of the old seven conditions are gone, and both were the level.** There is no
`permission_level` row to join and no rank to compare, which means the helper now asks a question with
a yes-or-no answer instead of one with a threshold. **`level_satisfies()` is deleted with them** — it
existed only to compare a grant's level with the level a permission required at a scope type, and with
no levels its arguments do not exist.

**`person_in_audience(person, audience, at, item)`** — is the person in the value of this audience's
expression on this date? It gained the `item` argument in this round, because a bound operand means
different people on different items and there is no other way to tell it which event it is asking
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
§11's check 16 and it covers recursion explicitly. **What was asserted here until round 14 was that the operand
cache keyed on `(person, selector_kind, selector_arg_id, …)` already had an entry for a nested audience, which is
what made the recursion shallow in practice and not merely shallow in argument. That sentence is retired with the
cache** ([D-114](../decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation)), and **the replacement should be stated at its real size rather than at the old one:**
within a request the memo resolves a recurring named operand once, so a screen that asks the same question about
the same person several times pays the depth once; **across requests the recursion runs to whatever depth somebody
typed, every time.** Since D-105 deleted the depth bound that is the honest price of nesting, and it is why §*What
each operand costs* and the width report of §*The cost of composition* are the controls here rather than a cache
that would have amortized it away. **The recursion terminates
by construction, not by a counter**: a cycle through `AUDIENCE` leaves cannot be saved (§8), so a
read-path depth cap would be a thing that decides who a grant reaches in exactly the case where the
data is already wrong. **[D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)
did not change this sentence; it changed what the sentence is standing on.** It used to be a back-up for a
guard that existed at save time, and now the save-time cycle walk *is* the guard and this refusal *is* the
whole design — which is why the walk must not be relaxed along with the bound it travelled with, and why
"the recursion terminates by construction" is a claim about a write-path check rather than about a number.

**Deleted from this list:** `scope_exposure_covers_assignment(org_unit_id, role_assignment_id, at)`
(the exposure table is gone, D-097) and `person_holds_gate_exempt(person, at)` (the gate is gone,
D-100). **The second deletion retires a hazard with it.** That helper had to be carefully kept *out*
of `can()` — routed through the resolver, a lapsed holder of the exemption would be denied by the very
rule it existed to lift, "a lockout with no error message, on the one day of the year it would hurt
most". **There is no such lockout any more, because there is no gate to lapse through.** The special
case is gone rather than fixed, and the lockout D-051 existed to survive is listed as retired below,
in §12.

The single authorization entry point. One implementation, used everywhere. Algorithm:
[../domain/06-authorization-model.md](../domain/06-authorization-model.md#6-the-resolver).

**`can(person, permission_code, scope_type, scope_id, at, owner_person_id)`** returns allowed
or denied. `scope_type` and `scope_id` are optional, `at` defaults to today, and
`owner_person_id` is supplied only where the ownership or guardianship channel is in play.

**The order of these steps is a rule for one reason and not the other.** Each step either returns or
falls through, so a step never gets to contradict an earlier one. **The deny step must run first, and
that is the only ordering with a consequence for the answer.** The allow steps are alternatives
producing the same boolean, so their order decides **which channel the audit names** and how quickly
the answer arrives — never what the answer is. That is exactly what the deletion of locality means,
and it is worth stating here because "the tiers are ordered and the first sufficient one wins" is a
sentence this document repeated for nine rounds and no longer believes.

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

   **There is no third bullet, and the second half of that sentence is the round.** The old list had a
   third: *it sits on a unit and the check is about that same unit*, with a note that a deny on a unit
   covered **only** that unit because authority does not flow down. That case is now the first bullet —
   there is one unit and it is not a row — and the ancestor walk the note refused to perform has no
   function left to refuse it. Any such grant: **return false.**
4. **Channel 1 — a grant at the unit.** `grant_satisfies(person, 'unit', NULL, permission, at)`.
   Because a unit grant reaches every item of every type (§6), this one step is the tier that used to
   be three: the organization grant, the unit grant, and the exposure branch that connected them.
5. **Channel 2 — a grant on this exact item.** `grant_satisfies(person, scope_type, scope_id,
   permission, at)`, reached only when both a scope type and a scope id were supplied. **This is the
   step `can_event()` used to precede**, and nothing precedes it now: a unit grant reaches the item,
   an item grant reaches the item, and there is no owner to ask
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

   Two properties of this channel survive, and the third changed shape:

   - **Entered by shape, not by namespace** (D-079, following D-074). A parent correcting their
     child's address is checked under `person.address.edit` — an ordinary, un-prefixed code — and
     still routes here. A permission added next year for a field a guardian must edit is covered
     the day the field exists, provided it is marked `write`, which is the seeding default (§2).
   - **Silent rather than final.** Under the old prefix rule this channel gave the last word.
     It still does not take it, and with a boolean answer there is no longer even a shortfall to
     fall through: a guardian whose right does not cover the code simply does not answer, and the
     actor's own grants get their turn. **A real prohibition is still possible and still absolute —
     it is a deny row, step 3.**
   - ~~**Gate-exempt.**~~ **Withdrawn by [D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape),
     and this was the property that made the channel need explaining.** A guardian whose own
     membership lapsed had not stopped being the child's guardian, so the gate had to be declared not
     to apply here. Now nothing is declared, because no channel is gated: `MEMBERS` is an operand some
     writer typed into some expression, and guardianship is not an expression.

   **The rest of this channel's older commentary survives unchanged and is not repeated here:** the
   guard must not be weakened into "the subject is a minor" (the existence of a guardianship row is the
   whole test, and an age lookup would put a branch in the resolver that D-070 and D-077 rule out), and
   personal attributes reach this resolver through no new door — everything beyond name, gender and age
   is descriptive data read by `person.view` and written by `person.edit` through the channels above,
   with no `attribute.*` read permission, no fifth channel, and no branch on *what a value is about*
   ([09-attributes.md §4](09-attributes.md#4-who-may-read-and-who-may-write),
   [D-083](../decisions/round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)).
   **The temptation that paragraph refuses — "a leader may see allergy data, but only for the children
   in their unit" — has lost half its grammar in round 10: there is no "their unit" to refer to**, and
   what remains of the refusal is the older and better reason that a branch on content is the privileged
   medical subset returning through the resolver after D-083 refused it through the permission list.
8. **Default deny. Return false.**

> **There is no membership gate anywhere in this function, and that is the deletion to notice while
> reading it.** Nine rounds put one clause in the role channel — `AND (NOT r0.requires_membership OR
> is_current_member(p_person_id) OR person_holds_gate_exempt(p_person_id, p_at))` — and called it the
> thing most likely to be "optimized" away. **All three disjuncts are gone**: the first with the
> column, the second into the `MEMBERS` operand, the third with the permission
> ([D-051](../decisions/round-04.md#d-051--the-membership-gate-is-waived-by-a-permission-not-only-by-a-role-flag)
> deleted entirely). The predicate `is_current_member` survives inside the evaluator, evaluated
> live at `at` like every other operand, and the three old shapes map exactly:
>
> | Old mechanism | Expression now |
> |---|---|
> | The gate applied to a role with `requires_membership = true` | `MEMBERS * ROLE(x)` |
> | The gate waived for a whole role | `ROLE(x)` — written without `MEMBERS` |
> | The gate waived for one named person | `MEMBERS * ROLE(x) + PERSON(y)` — the exception inside the expression that granted the rule, so it is read next to the thing it exempts. A second grant aimed at that person alone is equivalent and arguably clearer for something permanent; what was never allowed is a row that does not parse (§8, `PERSON`) |
>
> **The posture reversed from default-on to opt-in, and the new failure mode is named rather than
> buried** (D-100). Forgetting `MEMBERS` is now invisible, silent and permanent, and nothing in the
> resolver can see it. Three controls, none of which is the resolver: the standing report of
> `ROLE(...)` grants with no `MEMBERS` (check 6, §11); seeded grants carrying `MEMBERS` so that the
> path of least repetition is the safe path; and **import completeness** — `MEMBERS * COUNSELORS` is
> only as correct as the counselor roster, so an import that misses 300 counselors silently un-gates
> them, and the reconciliation report of
> [D-090](../decisions/round-07-08.md#d-090--the-legacy-corpus-is-thousands-of-roster-rows-with-numbers-and-no-money)
> must count people marked as counselors in the corpus against `role_holder` rows written. **It fails
> closed — nothing breaks, which is exactly why nobody notices.**

### The cache is deleted: nothing in this schema holds a permission answer

~~The cache is rebuilt, not invalidated~~ — **the section title has now been wrong twice, and both times about
the same thing**: first it was an invalidation policy, then a rebuild policy, and
[D-114](../decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation)
ended it by deleting the object both titles were about. **`permission_cache` is not in this schema.** Its
columns — ~~`person_id`, `permission_code`, `scope_type`, `scope_id`, `allowed`, `computed_at`,
`ruleset_version`~~, and `expires_at` before them — are gone, along with the operand cache keyed
`(person, selector_kind, selector_arg_id[, item])`, and the full text of the policy that governed them is
[D-111](../decisions/round-13.md#d-111--the-permission-cache-is-rebuilt-nightly-on-any-ruleset-change-and-on-request),
where the text of a decision lives. What is deleted here is a live rule; nothing in this corpus silently forgets
a past one.

**Why the deletion reached the data model rather than stopping at an implementation note:** the table mapped a
person to a boolean, and **that is the object §*Author in sets. Evaluate per person.* and §*Evaluation* forbid**
— *"The expansion is a predicate, not a set"*, *"No set of people is ever built"* — **a materialized answer to
"does this person satisfy this expression", kept where no check looks at it.** A design that forbids an object in
one path and permits it in another spends the rest of its prose explaining the difference, and this section had
grown exactly that prose. **The rule is now unconditional, which is what it gains.**

**What the checks use instead, and what may be held in memory:**

1. **A compiled expression.** Parsed once, operand kinds resolved once, a parameterized predicate emitted once,
   keyed by the expression's root and `ruleset_version`, **holding no person and no item**. It is process-local
   and **not a table**: nothing about it is queryable, durable, or a source of truth, and a restart discards it.
   `ruleset_version` therefore bumps on **`audience_operand`** (a subtree changed, so every compilation embedding
   it is stale) and on **`selector_type`** (the vocabulary changed) — two tables, down from the eight kinds of write D-111 named — six tables, the D-109 flag and a merge.
   `access_grant` is absent because **grants are not compiled**: a check reads the person's live grant rows, so
   adding, editing or revoking one changes what that read returns and leaves nothing stale to drop — and where a
   grant is created together with a new audience, the write that matters is the one on `audience_operand`, which
   *is* in the set; the `deprecated | hidden | disabled` flag is absent because **a state is not
   compiled in** — resolution consults it live, once per request, which is also what makes `disabled` take effect
   now ([D-109](../decisions/round-13.md#d-109--nothing-a-rule-names-is-deleted-deprecated-hidden-disabled--and-a-tab-instead-of-a-report));
   and `role_holder`, `person_group_member`, `guardianship_permission`, `event_registration`, a membership
   transition and a person merge are absent because **there is no answer to invalidate**.
2. **A request-scoped memo.** The checked person's live grant rows, read once; within the same request, a named
   operand that recurs. **Lifetime is the request.** It is worth stating in a data model precisely because it is
   *not* one: the reason this does not need a section, an index or an invalidation list is that its lifetime is
   shorter than any question about consistency.
3. **Two batch reads**, `can_many(person, codes[], item?)` and `which_of(people[], code, item)`, so a screen is
   one resolution rather than a loop. **`which_of` is not a materialization** — it evaluates the predicate for
   people already in hand; what stays forbidden is deriving a set in order to answer about one person.

**Named rosters are the one thing still held across requests**: `ROLE(x)` and `GROUP(x)` keyed by the name,
holding **the dated rows or the set with its validity ranges**, never the set as of today, so the checked date is
applied at check time and a period ending at midnight needs no job. **The reason this one survives while the
answer cache does not is that its key is the thing the write touches:** a `role_holder` insert invalidates one
roster, by identity, without asking whom it reaches.
**And one exclusion, so the exception does not eat the rule:** `MEMBERS` is **not** a roster and may not be cached
this way. It is not a row anybody writes — it is the read predicate over `membership`, whose dated rows the
**1 January sweep** rewrites for every member at once, which is the same bulk event under another name and lands
straight back on the invalidation list D-114 deleted. **A roster is a set with a name and its own holder rows;
`MEMBERS` is neither**, and the two age operands beside it are a birth date read at the checked date, which is not
a cacheable set either (§*What each operand costs*).

**One thing on this page is reversed by that change of denominator, and it has to be described accurately to be
reversed honestly.** The reverse closure over `audience_operand` — which expressions embed the audience being
written — was **never refused on cost grounds.** It was **bypassed**: [D-111](../decisions/round-13.md#d-111--the-permission-cache-is-rebuilt-nightly-on-any-ruleset-change-and-on-request)
chose a mechanism that did not need it, because the version integer **"never needs to know whom a rule reaches"**,
and per-entry invalidation had no answer at all for an edit to a shared audience's tree, which is why *"F-6's table
spent four rounds pretending the fan-out was tractable."* **That was the right call about the object it had.**
Removing the answers removes the fan-out it was avoiding: an edit to `veterans` now invalidates the set of
**compilations** that embed `veterans`, which is finite, enumerable, and named by rows that already exist —
**not** by the reached people, which is the unbounded side and the side that stayed unenumerable.
**Note the direction, because the save path already walks the other one:** the cycle refusal of
§*The expression tree* and check 15 walks **forward** from the tree being saved, while invalidation needs the
**reverse** direction — the same one the delete-refusal check walks when it asks whether a live grant, or a live
audience reachable from one through any number of `AUDIENCE` leaves, names this audience (§*The expression tree*,
§11 check 15). **So this is a new use of an existing direction, not a free ride on an existing query**, and the
listing whose cost §13 still registers as unverified is the same listing: **what this reversal inherits is that
open question, not a solved one.** It is recorded there rather than resolved here.

**What the deleted indexes were for, and where those needs live now.** An index on `expires_at` served an expiry
sweep that no longer exists; there is no sweep, because nothing expires. An index on `person_id` existed so a
membership transition could invalidate by person fast — and
[`03-membership.md` §6](03-membership.md#6-membership-and-the-authorization-system) had made that a hard
requirement three rounds before the policy it was aimed at was written: *"The permission cache must be
invalidated on every membership transition — including the yearly expiry sweep … retrofitting it is where the
bugs will be."* **The requirement is discharged by deletion, which is the only way those two pages can now agree**
([D-114](../decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation));
what it cost to notice is recorded there and in D-114, and the index that survives is the ordinary one on
`access_grant(grantee…)`, because **a check now reads a person's grants directly** — which is the same index the
resolver needed anyway, and the reason the deletion costs nothing measurable at the size
[D-112](../decisions/round-13.md#d-112--the-systems-scale-is-stated-hundreds-of-people-tens-of-registrants-per-event)
states.

**What none of this touches.** The merge and redaction duties on `audience_operand` leaves (§*A hand-named person
is now a keyless reference*, §11 check 2) are **unchanged and remain urgent** — they were never cache
maintenance. What is deleted is the sentence *"and invalidating the cache afterwards"*; what remains is that a
missed repoint writes nothing, so nothing is triggered, and the dangling leaf under `-` **denies everybody**. Two
other things this section used to own and does not lose: the **bound-operand rule** — an operand computed while
checking one item may never answer for another, now a rule about how a predicate is bound rather than about a key
([D-102](../decisions/round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it))
— and D-109's check pair, *"deprecating or hiding must not change an answer"* and *"disabling takes effect now,
and must say whose"*, which are properties of resolution and were always being tested against the wrong
mechanism.

### Properties to verify when reviewing this function

1. **Deny is checked before everything**, including ownership and guardianship. A restricted
   account's owner permissions are denied by a `deny` row if that is what the organization wants.
2. **`at` is threaded through every branch.** Permission checks are time-travel capable, and an
   operand evaluated at "now" inside a check performed at a past date is a wrong answer that looks
   like a right one.
3. **There is no wildcard except `system.admin`.** No prefix match, no implied capability.
   If a holder can do a thing, a row says so (D-068) — and now a row says **which** thing, because
   there is no level standing in for a set of them.
4. **`resolve_person` is called on entry**, so a tombstoned person's id still resolves.
5. **A deny is scope-independent.** Channel 0 matches a unit deny and an exact-item deny and does
   **not** walk ancestors — so a deny at the unit blocks every item, which is what makes a
   suspension absolute.
6. **There is no hierarchy to walk, and nothing left to assert about it.** ~~`unit_ancestors()` must
   not appear in this function~~ — the function itself is deleted
   ([D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)),
   which is a stronger guarantee than the CI assertion that replaced it in round 8 and then died with
   the SQL in D-072. **The surviving time-bomb is a different one** — no permission path may
   materialize a set of people — and it is check 16 (§11).
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
   the answer is denial with a `denial_reason` that says so. **This is the new cousin of the
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

What used to be the cache definition and its invalidation rules — and what replaced them — are above, immediately
after the resolver, because they are part of the resolver's contract and not a separate concern. **That placement is
why [D-114](../decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation) is written here rather than filed as a deployment note:** the question was never only where to
keep answers, it was what a check is.

The person-merge case remains the easiest to forget —
see [01-identity.md](01-identity.md#8-identity_hypothesis-and-person_merge).

---
