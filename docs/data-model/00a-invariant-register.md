# Data Model — 00a. Who enforces each invariant

> One row for every rule this schema states, saying what carries it, what would notice a breach, and what a breach looks like. Written so that the answer to "is that rule guarded?" is one lookup instead of twenty pages.

[← 00-conventions](00-conventions.md) | [01-identity](01-identity.md)

---

**This page does not restate any rule.** It links to the page that owns each one, because a restated
rule is a second copy of it, and the defect this corpus keeps hitting is a copy that drifted — the story
the catalog's §12 tells about a seeded table copied from an evaluator's arm list, and the reason
[D-127](../decisions/round-18.md#d-127--the-registry-diff-is-a-committed-script-and-it-gates-a-round)
diffs documents against their own registries rather than against a list. What is *here* is the three
facts a rule's own page is allowed to leave implicit — **which layer carries it, which report would see
a breach, and what a breach looks like** — and the register is where a blank in those two columns is
visible instead of being a sentence on page 412 that nobody re-reads.

**The four shapes, and the layer each is assigned** ([D-130](../decisions/round-18.md#d-130--one-register-answers-who-enforces-an-invariant-and-f-10-closes)):

| Shape | What it is | The layer that carries it | Why not another layer |
|---|---|---|---|
| **1** | No two rows overlap in time | A hand-written PostgreSQL exclusion constraint, emitted by a migration | The ORM cannot generate one, and an application check is bypassed by the import, the bulk edit and the fix at 2am ([00 §6's rule 3](00-conventions.md#6-the-temporal-pattern)) |
| **2** | Unique, but only among rows meeting a condition | A partial unique index, emitted by a migration | The unconditioned constraint is a different and usually wrong rule — it forbids the second closed row, which history requires |
| **3** | The answer reads another table, a resolver, or a graph | The write path, inside the transaction that writes | No constraint spans two tables. The layer named in this register is always the write path; **what varies is whether a report was named beneath it** |
| **4** | A value that may never change once set | Nothing automatic. The rule, the referrer listing, and the review | There is no offending row to catch — only a rewritten history — and [00 §10's rule](00-conventions.md#10-migration-discipline) against rewriting a historical row's meaning is the prose that stands behind it |

**How to read the two right-hand columns.** *Backstop* names the report that would list a breach, by
the page and number where that report is written. **`none` in bold** is not an omission of this page and not a
slur on the rule: it means the corpus names no such report anywhere, which is the finding. Eleven rows are
in that state and **all eleven are shape-3 rows**, whose only enforcement is a line of code. Where the blank
is a question rather than simply a report nobody has written, the row names it — six of the eleven,
[F-28](../open-questions.md#f-28) to [F-33](../open-questions.md#f-33) — and none is quietly filled with an
invented check. *Breach* is what the bad data looks like afterwards, because a shape-1 breach and a shape-2
breach both read as "two rows" and only one of them is a duplicate.

**Nine numbered checks, on three pages, are assertions about the code rather than reports over data**
— the six `TIME-BOMB` checks of
[05d §11](05d-invariants-and-seed.md#11-invariants-to-verify) (15, 16, 17, 18, 19 and 22),
[02 §6](02-organization.md#6-integrity-checks) check 4, and
[08a §10](08a-event-guards-and-checks.md#10-integrity-checks) checks 1 and 9. They are cited below
as `save-refusal`, never as a report: they verify that a guard still exists, never that the data is
clean. Filing one as a backstop would overstate coverage in exactly the direction that matters.

---

## 1. No two rows overlap in time

Four rules. All four are a hand-written exclusion constraint over a range built from `valid_from` and
`valid_to`, half-open, so that a row ending 2010-06-30 and one starting 2010-06-30 do not collide.

**A report beneath a real constraint is a courtesy, not a control** — the constraint cannot be breached
quietly — so a `none` in this table or the next is only a finding where the layer is the write path.

| The rule | Stated in | Key it excludes on | Rows it counts | Backstop | Breach |
|---|---|---|---|---|---|
| A person is in a group once at a time | [02 §2](02-organization.md#2-person_group_member) | `(person_group_id, person_id)` | **all rows**, open and closed — there is no status to scope it by | [02 §6 check 1](02-organization.md#6-integrity-checks) | Two member rows for one person in one group, one of them a history row nobody can tell was ever superseded |
| A person holds one membership at a time | [03 §3](03-membership.md#3-membership) | `(person_id)`, predicate: either row is `pending_payment`, `active` or `lapsed` | three statuses only | [03 §7](03-membership.md#7-integrity-checks) | Two live memberships, so `MEMBERS` counts the person twice |
| A person holds an office once | [05 §4](05-authorization.md#4-role_holder--who-holds-an-office) | `(person_id, role_id)` | **all rows** | [05d §11](05d-invariants-and-seed.md#11-invariants-to-verify) | Two holder rows, so authority survives the row that was meant to end it |
| A guardian is a guardian of a child once | [04 §1](04-relationships.md#1-guardianship) | `(guardian_person_id, dependent_person_id)` | **all rows**, and past ones are expected and unlimited | [04 §6](04-relationships.md#6-invariants-to-verify) — **added by D-130, which is what closing F-10 owed this row** | Two guardianship rows for one pair with different `right_level`, so whose word the child's record takes is a query-order accident |

**The predicate is part of the constraint, not a comment on it.** `membership` counts three statuses and
`guardianship` counts none, and a migration that copies the first constraint and edits the table names
produces a rule that refuses a lapsed row beside a new one — which history requires. This is the same
mistake [00 §6a](00-conventions.md#6a-who-enforces-an-invariant-now) records as already having been made
once, in an index.

## 2. Unique, but only among rows meeting a condition

Fifteen rules, each a partial unique index whose predicate is the interesting half.

| The rule | Stated in | Unique on | The predicate | Backstop | Breach |
|---|---|---|---|---|---|
| One live account per person | [01a §4](01a-accounts-and-contacts.md#4-account) | `person_id` | status is pending, active or suspended | [01b §10](01b-merges-views-and-checks.md#10-integrity-checks) | A person logs in twice and gets two different sets of grants |
| A username is used by one live account | [01a §4](01a-accounts-and-contacts.md#4-account) | `lower(username)` | has one, and is not closed | same | Two people type the same username and one is quietly rejected at the form |
| One current credential per external identity | [01a §5](01a-accounts-and-contacts.md#5-account_credential) | `(external_issuer, external_ref)` | kind is `oauth` and the row is current | **none** | An issuer's login lands on whichever credential the index happened to keep |
| One primary contact per kind | [01a §6](01a-accounts-and-contacts.md#6-person_contact) | `(person_id, contact_type, purpose)` | `is_primary` and current | **none** | A guardian mail merge picks one of two primaries at random |
| One live hypothesis per pair | [01b §8](01b-merges-views-and-checks.md#8-identity_hypothesis-and-person_merge) | `(person_a_id, person_b_id)` | status is open | [01b §10](01b-merges-views-and-checks.md#10-integrity-checks) | Two reviewers work the same pair in the queue and merge on top of a merge |
| One open request per person per type | [03 §2](03-membership.md#2-membership_request) | `(person_id, membership_type_id)` | `draft`, `submitted` or `pending_payment` | [03 §7](03-membership.md#7-integrity-checks) | A parent's two attempts both arrive and one person is approved twice |
| One open membership per person | [03 §3](03-membership.md#3-membership) | `person_id` | the row is open | [03 §7](03-membership.md#7-integrity-checks) | Two rows both say the person is a member, with different types |
| One open permission history row | [04 §1](04-relationships.md#1-guardianship) | `guardianship_id` | the row is open | [04 §6 check 6](04-relationships.md#6-invariants-to-verify), which reads the disagreement, not the count | `guardianship.right_level` has two histories and one current value |
| One open holder row | [05 §4](05-authorization.md#4-role_holder--who-holds-an-office) | `(person_id, role_id)` | the row is open | subsumed — [the shape-1 constraint above](#1-no-two-rows-overlap-in-time) already refuses it, and **only one of the two is a constraint** | nothing: the all-rows constraint is the stricter rule |
| One live allow per grantee, scope and permission — **three indexes**, one per grantee kind | [05 §6](05-authorization.md#6-access_grant--the-per-item-layer) | `(grantee, scope_type, scope_id, permission_code)` | open, unrevoked, and `allow` — denies are outside all three | [05d §11](05d-invariants-and-seed.md#11-invariants-to-verify) | Two allows, and the answer stops being a function of the data |
| An audience's code is used once | [05a §8](05a-audience-and-grammar.md#8-audience--grants-that-target-a-set-of-people) | `code` | the row has one | [05d §11 check 12](05d-invariants-and-seed.md#11-invariants-to-verify) | `AUDIENCE(x)` resolves to whichever of two audiences the query found |
| A key's code is used once | [05e §14](05e-keys-and-callers.md#14-api_key--a-caller-that-is-nobody) | `code` | the row is live | [05d §11](05d-invariants-and-seed.md#11-invariants-to-verify) | A call authenticates and the trail cannot say which integration made it |
| A key's secret is not shared | [05e §14](05e-keys-and-callers.md#14-api_key--a-caller-that-is-nobody) | `secret_hash` | the row is live | as above — **and its layer row names only `code`, which D-130 corrects** | Two integrations authenticate as each other in the audit trail |
| One live payment request per obligation | [07 §2a](07-finance.md#2a-how-money-actually-arrives) | `fee_obligation_id` | **undefined** — `voided_at` absent, or unexpired, or both | **none**, and the predicate is not written down | Two QR codes for one debt, and the money arrives twice |
| One primary organizer per event | [08 §3](08-events.md#3-event_organizer) | `event_id` | `is_primary` | [08a §10](08a-event-guards-and-checks.md#10-integrity-checks) | Two people receive the one notification meant for the lead |

Two rules that read like this shape and are not: `person_identifier (scheme, value)` and
`person_attribute (person_id, attribute_definition_id)`. Both conditions live in **another table** —
`identifier_scheme.is_unique` and `attribute_definition.allow_multiple` — which makes them shape 3, and
[00 §6a](00-conventions.md#6a-who-enforces-an-invariant-now) tells the story of the index that got this
wrong once by ignoring a flag. Uniqueness stated over **all** rows — `permission.code`, `role.code`,
`payment_request.variable_symbol`, the `public_id` columns, the one-row-per-pair rules on registrations
and answers — is a plain unique constraint and is not listed here at all.

## 3. The answer reads another table, a resolver, or a graph

Forty-one rules. **In this shape the layer is always the write path** — no constraint spans two tables —
so the layer column is gone from this table and only two columns remain. **The report column is the one
worth reading**: `none` means a rule that holds until somebody edits the write path and nothing
downstream ever says so.

| The rule | Stated in | Save-time check | Report |
|---|---|---|---|
| An identifier is unique only for schemes that say so | [01a §7](01a-accounts-and-contacts.md#7-person_identifier) | the write path | **none — and [00 §6a](00-conventions.md#6a-who-enforces-an-invariant-now) promises one, which is why D-130 adds it to [01b §10](01b-merges-views-and-checks.md#10-integrity-checks)** |
| One current attribute value, unless the definition allows several | [09 §3](09-attributes.md#3-person_attribute--a-value-one-person-has) | inside the writing transaction | [09 §8 check 4](09-attributes.md#8-integrity-checks) |
| A value is the type its definition declares | [09 §5](09-attributes.md#5-what-this-design-cannot-do) | a warning; a human may always save | none, deliberately |
| `allow_multiple` may go true only freely | [09 §2](09-attributes.md#2-attribute_definition--the-vocabulary) | a confirmation report at the save | [09 §8 check 4](09-attributes.md#8-integrity-checks) |
| The denormalised name agrees with the name history | [01 §2](01-identity.md#2-person) | same transaction | **none** — [F-28](../open-questions.md#f-28) |
| A name belongs to one of office, group or audience | [02 §1](02-organization.md#1-person_group) | the write path, including the reserved-word half | [05d §11 check 12](05d-invariants-and-seed.md#11-invariants-to-verify) — a save-refusal, so it asserts the guard still exists |
| An office's code is not a group's name | [05 §3](05-authorization.md#3-role--an-office) | the write path | same check |
| An operand's arity and binding match its registry row | [05a §8](05a-audience-and-grammar.md#8-audience--grants-that-target-a-set-of-people) | one of six checks in one transaction | [05d §11 checks 3 and 4](05d-invariants-and-seed.md#11-invariants-to-verify) |
| An `AUDIENCE` leaf may not point at an audience with no code | [05a §8](05a-audience-and-grammar.md#8-audience--grants-that-target-a-set-of-people) | the grant save | [05d §11 check 12](05d-invariants-and-seed.md#11-invariants-to-verify) |
| A grant's `scope_id` is present exactly when the permission applies to an item | [05 §6](05-authorization.md#6-access_grant--the-per-item-layer) | the write path | [05d §11 check 3](05d-invariants-and-seed.md#11-invariants-to-verify) |
| Every `system.*` permission applies at the unit | [05 §2](05-authorization.md#2-permission) | the seeding rule | [05d §11 check 3](05d-invariants-and-seed.md#11-invariants-to-verify) |
| A bound operand is legal only on a grant that can bind it | [05 §6](05-authorization.md#6-access_grant--the-per-item-layer) | the write path | [05d §11 checks 3 and 4](05d-invariants-and-seed.md#11-invariants-to-verify) |
| An event arrives with the grant that lets its organizers read its answers | [08a §8](08a-event-guards-and-checks.md#8-projections-and-guards) | the insert path, and the importer's | [08a §10 check 2](08a-event-guards-and-checks.md#10-integrity-checks) |
| A registration creates its fee obligation | [07 §4](07-finance.md#4-how-this-connects-to-membership) | the registration path | [08a §10 check 10](08a-event-guards-and-checks.md#10-integrity-checks) for events; **none** for memberships |
| A merge repoints every operand that named the person | [05b](05b-expression-tree.md) | the merge reassignment table | [05d §11 check 2](05d-invariants-and-seed.md#11-invariants-to-verify), a backstop and not the control |
| An audience may not reach itself | [05b](05b-expression-tree.md) | two walks at save, the whole guard | [05d §11 check 15](05d-invariants-and-seed.md#11-invariants-to-verify) — `save-refusal` |
| A key may not be granted one of five codes | [05e §15](05e-keys-and-callers.md#15-what-a-key-may-hold) | the save path only | [05d §11 check 20](05d-invariants-and-seed.md#11-invariants-to-verify), the entire net |
| Deleting an item closes the grants written on it | [05 §6](05-authorization.md#6-access_grant--the-per-item-layer) | an application obligation, tested | [05d §11 check 2](05d-invariants-and-seed.md#11-invariants-to-verify) |
| An item-scoped grant carries an end date | [05 §6](05-authorization.md#6-access_grant--the-per-item-layer) | application validation | the report of long-lived open grants, named beside an admission that nothing backstops it |
| An office does not outlive its own term limit | [05 §4](05-authorization.md#4-role_holder--who-holds-an-office) | none — the column is a prefilled nudge | the report of offices held past their end date |
| An ended group is not named by a new grant | [02 §3](02-organization.md#3-a-group-is-an-item-a-grant-can-be-written-on-one) | the write path | [02 §6 check 5](02-organization.md#6-integrity-checks), which watches whether the refusal is still there |
| A member row sits inside its group's period | [02 §2](02-organization.md#2-person_group_member) | none — containment is assumed | [02 §6 check 2](02-organization.md#6-integrity-checks), a list to read |
| A request and the membership it produces refer to each other | [03 §2](03-membership.md#2-membership_request) | the two-step insert | **none** |
| A guardian's right agrees with its open history row | [04 §1](04-relationships.md#1-guardianship) | none — the row wins on disagreement | [04 §6 check 6](04-relationships.md#6-invariants-to-verify) |
| No live row points at a merged-away person | [01b §10](01b-merges-views-and-checks.md#10-integrity-checks) | the reassignment table | the same section |
| An audit row holds no unredacted payload | [05c §9](05c-access-log-and-resolver.md#9-access_log) | the application's obligation, in order | none reaches the ordering |
| Every audited table is in fact audited | [06b §5](06b-redaction-and-checks.md#5-integrity-checks) | the write itself | the check of a change the trail never saw, whose ceiling is stated there |
| An actor label is on the vocabulary | [00 §7a](00-conventions.md#7a-what-an-empty-actor-column-means) | nothing refuses one | [06b §5](06b-redaction-and-checks.md#5-integrity-checks) |
| A write is not audited against a key that was already ended | [06b §5](06b-redaction-and-checks.md#5-integrity-checks) | none | **none, and the page says so** — [F-29](../open-questions.md#f-29) |
| Which audit views a holder may open follows the payload, not the table | [06 §2](06-audit-and-import.md#2-audit_log) | none | **none** — [F-29](../open-questions.md#f-29) |
| A hand edit to an audited row is visible afterwards | [06b §5](06b-redaction-and-checks.md#5-integrity-checks) | impossible — the write is outside the application | the same check, whose ceiling is that table |
| A polymorphic reference with no foreign key still points somewhere | [erd-b](../appendix/erd-b-inventory.md) | none for five of them | **none** — [F-30](../open-questions.md#f-30) |
| A registration is inside its event's window | [08a §8](08a-event-guards-and-checks.md#8-projections-and-guards) | every insert path | [08a §10 check 9](08a-event-guards-and-checks.md#10-integrity-checks) |
| An event's capacity is not silently exceeded | [08 §5](08-events.md#5-capacity-and-the-waitlist) | the placing procedure | [08a §10 check 5](08a-event-guards-and-checks.md#10-integrity-checks); an overrun is permitted, attributed and reported |
| Only members register | [08 §4](08-events.md#4-event_registration) | none, and none is wanted — eligibility is capability | none, by design |
| One staged row makes one event | [06a §3](06a-import.md#3-import-pipeline) | the application, deliberately | **none** |
| `membership.outstanding_balance` agrees with the allocations | [07 §3](07-finance.md#3-keeping-membershipoutstanding_balance-honest) | **unassigned** — the section opens the choice | **none** — [F-31](../open-questions.md#f-31) |
| An operand that resolves to nothing is said out loud | [05b](05b-expression-tree.md) | none — no save is refused | the report of audiences that reach nobody, with an owner |
| An expression tree stays a size that resolves | [05a §8](05a-audience-and-grammar.md#8-audience--grants-that-target-a-set-of-people) | none, by design | a report the corpus says has nothing behind it |
| A compilation is invalidated by exactly the right edits | [05c §10](05c-access-log-and-resolver.md#10-the-resolver) | the write path, `audience_operand` plus `selector_type` | **none** — the listing it depends on is itself unmeasured |
| A delegation does not exceed the delegator | [domain/06](../domain/06-authorization-model.md) | grant time, and again at use | **none** — [F-32](../open-questions.md#f-32) |
| Every selector row has a resolver behind it | [05a §8](05a-audience-and-grammar.md#8-audience--grants-that-target-a-set-of-people) | release engineering | none can: it is program text, and it surfaces as an empty set |
| A code's `right_kind` matches what the code says | [05 §2](05-authorization.md#2-permission) | the save | **none** — [F-33](../open-questions.md#f-33) |

**`none` in this table is not an indictment of the rule.** Four of them are `none` because the design
refused a guard on purpose — eligibility is capability, a warning is not an error, a size rule would be
a limit nobody asked for, and a resolver arm is code. The register keeps those rows precisely so that
"we checked" and "we chose not to" are different words in the same column.

## 4. A value that may never change once set

**This shape is not empty.** It was described as empty on the strength of one deleted instance; four live
ones were already in these pages, and the test that separates them from a column nobody would think to
rename is the same test that made the two named candidates worth naming: **a rename rewrites what
references it, and nothing leaves a row in the wrong state for a report to find.**

| The value | Stated in | What references it | What carries the rule |
|---|---|---|---|
| A member row's `group_id` and `person_id` | [02 §2](02-organization.md#2-person_group_member) | the row's own meaning | the close-and-open pair, which is the write path; **never an edit of the row** |
| A bank transaction, every column | [07 §2a](07-finance.md#2a-how-money-actually-arrives) | reconciliation against money already matched | "immutable once imported", and a re-import or a new row instead |
| `person.merged_into_person_id` | [01b](01b-merges-views-and-checks.md#8-identity_hypothesis-and-person_merge) | every walk that resolves who a person is now — chains are expected and walked | the rule against rewriting a historical row's meaning |
| A permission's `code` | [05 §2](05-authorization.md#2-permission) | every `access_grant` row, and the seeded roles, which list codes by value | **stated twice and enforced nowhere**; now a rule with a referrer listing behind it ([D-131](../decisions/round-18.md#d-131--shape-4-is-not-empty-and-a-code-that-is-referenced-may-not-be-renamed)) |
| A selector's `code` | [05a §8](05a-audience-and-grammar.md#8-audience--grants-that-target-a-set-of-people) | every stored expression, through `selector_kind` | the same rule; **this is the instance the register was looking for and the candidate list did not carry** |
| A key's `code` | [05e §14](05e-keys-and-callers.md#14-api_key--a-caller-that-is-nobody) | grants, audit rows, and the report of who called | the same rule ([D-131](../decisions/round-18.md#d-131--shape-4-is-not-empty-and-a-code-that-is-referenced-may-not-be-renamed)) |
| An audience's `code` | [05a §8](05a-audience-and-grammar.md#8-audience--grants-that-target-a-set-of-people) | **nothing, after the save** — `AUDIENCE(x)` resolves once, into `selector_arg_id` | **not immutable, and this row is the correction**: a rename rewrites no grant, which is what §5 of the name namespace promises out loud and what [the candidate list F-10 carried had forgotten](../open-questions.md#f-10) |

---

## What the register cannot say

- **It cannot say whether a write path still contains its rule.** Every shape-3 row above rests on code
  this repository does not contain. Where a numbered check exists for such a rule, it is a
  `save-refusal`: it re-asks whether the guard is there, and it is the only thing standing between a
  removed line of code and a silent rule.
- **It cannot reach a rule stated only once, in prose, on the page it governs.** That is what the
  inventory behind this page was for, and what it found in the way of absences is in
  [the open questions](../open-questions.md), each one naming the page it is missing from.
- **It cannot rank the `none`s.** Two modules are far more exposed than the rest, and for the same
  reason: [07-finance.md](07-finance.md) and [06a-import.md](06a-import.md) carry no "Invariants to
  verify" section of their own, so every rule they state is unassigned by construction rather than by
  oversight. Two pages, and most of this table's `none`.
- **It is not a substitute for the constraint.** A row here saying `migration` is not the migration.
  [00 §6a](00-conventions.md#6a-who-enforces-an-invariant-now) is the rule about what must be emitted
  below the application; this page is the evidence that the rule was applied to every row and told where
  it was not.

---

See also [00-conventions §6a](00-conventions.md#6a-who-enforces-an-invariant-now),
[05d §11](05d-invariants-and-seed.md#11-invariants-to-verify),
[the registry diff](../decisions/round-18.md#d-127--the-registry-diff-is-a-committed-script-and-it-gates-a-round),
and the decisions [D-130](../decisions/round-18.md#d-130--one-register-answers-who-enforces-an-invariant-and-f-10-closes)
and [D-131](../decisions/round-18.md#d-131--shape-4-is-not-empty-and-a-code-that-is-referenced-may-not-be-renamed).
