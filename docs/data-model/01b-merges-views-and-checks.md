# Data Model — Identity: identity hypotheses, merges, views, checks

`identity_hypothesis` and `person_merge` — two rows becoming one person: the signals a proposal
carries, the conflicts a merge could not decide, and what a reversal can and cannot undo. Then the views that
encode *"exclude merged and redacted"* and *"as of a date"* so application code cannot forget them,
the checks that run nightly, and what is still open.

Every pattern referenced here is defined in [00-conventions.md](00-conventions.md).

**Section numbers are shared across the three parts** and never renumbered, because other pages cite
them by number and their anchors are built from them:
[01-identity.md](01-identity.md) holds §1–§3 (the central claim, `person`, `person_name`),
[01a](01a-accounts-and-contacts.md) §4–§7 (`account`, `account_credential`, `person_contact`,
`person_identifier`), and [01b](01b-merges-views-and-checks.md) §8–§11 (`identity_hypothesis`,
`person_merge`, the views, the integrity checks, open issues).

---

## 8. `identity_hypothesis` and `person_merge`

**Fields**

| Field | Kind | Notes |
|---|---|---|
| `id` | surrogate id | |
| `person_a_id` | reference to person, required | The lower of the two ids — canonical ordering, so that `(a,b)` and `(b,a)` cannot both exist |
| `person_b_id` | reference to person, required | |
| `confidence` | number between 0 and 1, required | Inclusive of both ends |
| `match_signals` | jsonb, required | A list of signals, each with a name, a weight and whether it matched — `[{signal: 'birth_date_exact', weight: 0.4, matched: true}, {signal: 'name_normalised', weight: 0.3, matched: true}, …]`. Stored so a human reviewer can see **WHY** the matcher proposed this |
| `status` | text, required | One of: `proposed`, `needs_review`, `confirmed`, `rejected`, `superseded`. Default `proposed` |
| `proposed_by` | text, required | One of: `import_job`, `match_job`, `person`, `staff`. `match_job` is the nightly batch matcher, as opposed to a person suggesting a match by hand |
| `proposed_by_person_id` | reference to person, optional | Set when a person proposed it |
| `proposed_at` | timestamp, audit time | Default: now |
| `reviewed_by` | reference to person, optional | |
| `reviewed_at` | timestamp, audit time, optional | |
| `review_note` | text, optional | |
| `created_at` | timestamp, audit time | |

**Rules**

- `person_a_id` names a lower person id than `person_b_id`, and the two are never the same
  person.
- A hypothesis cannot be `confirmed` or `rejected` without a `reviewed_at`.
- One live hypothesis per pair: unique over `(person_a_id, person_b_id)` while the status is
  `proposed`, `needs_review` or `confirmed`. A `rejected` or `superseded` hypothesis does not
  block a new one, so the pair can be re-proposed later.

**Indexes**

- The review queue: status, then `confidence` highest first, restricted to the rows still
  waiting — `proposed` and `needs_review`.

**`person_merge`** — the record that one person row was absorbed into another.

**Fields**

| Field | Kind | Notes |
|---|---|---|
| `id` | surrogate id | |
| `surviving_person_id` | reference to person, required | |
| `merged_person_id` | reference to person, required | The absorbed row. It keeps its id; `person.merged_into_person_id` points here |
| `hypothesis_id` | reference to identity hypothesis, optional | The hypothesis this merge came from, when one did |
| `merged_at` | timestamp, audit time | Default: now |
| `merged_by` | reference to person, required | |
| `reason` | text, optional | |
| `reversed_at` | timestamp, audit time, optional | |
| `reversed_by` | reference to person, optional | |
| `reversal_note` | text, optional | |
| `created_at` | timestamp, audit time | |

**Rules**

- A person may not be merged into themselves: `surviving_person_id` and `merged_person_id`
  are never the same person.
- **A merge is refused when the chosen survivor resolves — by walking the chain — to the person being
  absorbed.** That includes the one-hop case just stated and the case that actually happens: absorbing B
  into A when A has already been absorbed into B.
  [D-087](../decisions/round-07-08.md#d-087--merge-chains-stay-because-reversing-a-merge-is-a-supported-operation)
  puts this check on the **merge** and not on the read, and the placement is the substance of the rule: a
  cycle refused on the way in cannot be reached, whereas a step limit on `resolve_person()` achieves
  nothing except deciding *which of two wrong answers to return* — the tombstone, or wherever the walk
  happened to stop. There is no schema object that spans two rows of a walk, so this is a rule about an
  operation; the cycle check in §10 is a canary for it having leaked, not the guard.

**Indexes**

- Merges by surviving person, and merges by merged person — both directions get asked.
- Merges by merged person that have not been reversed — the "who is this person now" query.

**The canonical ordering (`person_a_id` before `person_b_id`) is not cosmetic.** Without it
the matcher can create both `(100, 847)` and `(847, 100)`, and a reviewer will confirm one
while the other sits in the queue forever — or worse, confirm both. The ordering rule plus
the partial unique index makes the pair identity unambiguous.

**`match_signals` as JSONB** rather than columns, because the signal set will evolve as the
matcher improves, and because these are write-once-read-for-review, never queried
analytically.

**`person_merge` is append-only** — `reversed_at` is set, rows are never deleted. An
unmerge does not remove the merge record; it records that it was undone, so the history of
the mistake is visible. See
[../domain/03-identity-and-legacy.md](../domain/03-identity-and-legacy.md#6-reversing-a-merge).

**Reversing a merge is a required operation, not an accommodation.** Those three columns exist because
someone asked for the capability, and
[D-087](../decisions/round-07-08.md#d-087--merge-chains-stay-because-reversing-a-merge-is-a-supported-operation)
is where it was asked for; §9 explains that this is the reason chains were kept rather than the other way
round. Two consequences sit under it, and both are easy to lose later.

- **Reversal needs no permission of its own.** Unmerging is the same act as merging — an identity
  correction made by a named human — so it is `person.merge`, which `identity_reviewer` already holds.
  A separate code would grade undoing a mistake as safer than making one, which is precisely backwards:
  the mistake is the thing that needed the guard.
- **A merge can be undone; the merged period cannot.** The reversal procedure lifts the tombstone and
  returns the rows created *before* the merge, but the rows created *inside* the window are flagged for a
  human rather than guessed at — and every `access_grant` from that window is flagged, not redistributed,
  because the authority exercised in there really was exercised by somebody the record can no longer
  separate. **That asymmetry is the honest core of the feature: the row is restorable, the interval is
  not.** Anyone who reads `reversed_at` as "as if it never happened" is reading the wrong column for
  that claim, which is why the reversal record is kept rather than deleted.

### Merge conflicts

**`field_conflict`** — one field the merge could not decide.

**Fields**

| Field | Kind | Notes |
|---|---|---|
| `id` | surrogate id | |
| `merge_id` | reference to person merge, required | |
| `entity_table` | text, required | `person`, `person_contact`, `membership`, … |
| `entity_id` | surrogate id, required | The row in `entity_table`. No reference — with the table named per row it would point at any table in the schema |
| `field_name` | text, required | |
| `surviving_value` | text, optional | |
| `merged_value` | text, optional | |
| `resolution` | text, optional | One of: `kept_surviving`, `took_merged`, `manual`, `unresolved` |
| `resolved_value` | text, optional | |
| `resolved_by` | reference to person, optional | |
| `resolved_at` | timestamp, audit time, optional | |
| `created_at` | timestamp, audit time | |

**Indexes**

- A merge's conflicts by resolution.
- A merge's conflicts that are still `unresolved` — the reportable set.

Every field the merge could not resolve automatically lands here as `unresolved`. **A
merge with unresolved conflicts must be visible in an operational report** — otherwise
these rows accumulate silently and the data is quietly wrong.

Conflict cases worth naming, because each needs a human decision and none has a safe rule:

| Case | Why it cannot be automatic |
|------|---------------------------|
| Two `is_primary` emails of the same purpose | Which one does the person actually use? |
| Two different `birth_date` values | One is a typo; guessing produces a wrong legal record. |
| Two overlapping memberships | May be legitimate, or may mean the merge is *wrong*. |
| Two different current names | One may be a maiden name, or they may be different people. |
| Two accounts, both active | Which one is in use? |

---

## 9. Views

Convenience views that encode the "always exclude merged and redacted" and "point in
time" rules, so that application code cannot forget them.

**`v_person`** — the person rows most queries actually want: a person who is neither merged
away nor redacted. **Both exclusions, not one.** They are different reasons and they must not be
collapsed: a merged row is a *duplicate* that points at the real answer, while a redacted row is a
*person who was erased*, whose names and contacts no longer exist. Neither belongs in a list of
people, and a listing that shows one and hides the other is worse than either, because it teaches
the reader that the redacted child is a data-entry error.

> **Nothing else carries this rule.** There is no view definition anywhere in this repository (§1 of
> [D-072](../decisions/round-06.md#d-072--the-documentation-carries-no-sql-the-schema-is-the-orms-job)), so this page is the only place the rule lives and it has to be right.
> [D-080](../decisions/round-06.md#d-080--five-contradictions-the-translation-surfaced-and-how-each-was-resolved)
> records the time it was not: the view excluded merged rows while §1 and §2 required both of them, and the
> prose lost.

**What is deliberately *not* excluded anywhere: the row itself.** A redacted person is still a
row with a still-working id, so historical references keep resolving
([§2](01-identity.md#2-person)'s `redacted_at`). Anything that must reach a merged or redacted
row — audit, as-of reconstruction, `resolve_person` — queries `person` directly and says so.
`v_person` is the view for "people", and people is not what an audit trail is asking for.

**`resolve_person(id)`** — turns a possibly-merged id into the survivor. These steps run in
this order, and the order is the rule:

1. Begin at the person row carrying the given id.
2. If that row has no `merged_into_person_id`, stop; this id is the answer.
3. Otherwise move to the row its `merged_into_person_id` names and repeat from step 2.

**`v_person_display`** — one row per person `v_person` admits, carrying `id`, `public_id`, a
display given name (`preferred_name` where present, `given_name` otherwise), `family_name`,
a display name formed by putting the two together with a space, `birth_date`,
`birth_date_precision` and `redacted_at`.

**What `v_person_display` does not carry, and why that is a rule rather than an omission.** It is a
*display* row — the columns needed to name a person in a list — and it carries **no descriptive
values**. It cannot: a view is a fixed list of columns and the attribute layer is the part of a
person with no fixed list, which is §2's test arriving from the other side. Naming the boundary
matters because the failure mode is silent. **Anything asked about a *person*, rather than about what
they are called, reads `person` and `person_attribute` together under the one `person.view` that
reaches both** ([09-attributes.md §4](09-attributes.md#4-who-may-read-and-who-may-write)) — the
allergy list a first aider asks for, the record a guardian opens, the form a leader fills in. A screen
built on `v_person_display` alone answers those questions with a name and a birth date, shows no
empty field where an allergy should be, and looks entirely healthy while doing it
([domain/08-person-data.md §3](../domain/08-person-data.md#3-who-needs-to-know-what)). The view stays
narrow for the reason it exists — every picker and roster in the system reads it and none of them
needs the record — and the obligation sits on the caller: **do not answer a question about a person
out of a view that only knows how to print one.**

`resolve_person` follows every hop because merges chain: A absorbed into B, later B absorbed
into C. A single-level pointer lookup would return B, whose row is itself tombstoned.
**Every place that accepts a person id from outside must call this.** Getting it wrong
means a historical record links to a tombstone and the UI shows a blank name — or the
wrong one.

**Chains are a decision, not an assumption.** They stay because reversing a merge is a required operation
rather than a convenience — someone asked for it as a requirement (§8), and
[D-087](../decisions/round-07-08.md#d-087--merge-chains-stay-because-reversing-a-merge-is-a-supported-operation) is that request.
The shape of the trade follows from it: with chains kept, a reversal is a replay; with flattening, it is a
rebuild. **Flattening is therefore closed off, not merely slower**, and "flattening is faster" buys nothing
except the death of a feature somebody named.

**Two rules keep a permanent chain safe.**

- **A cycle cannot be created, and the place it cannot be created is the merge, not the read** (§8's
  rule). A read-side hop limit is not a weaker version of this guard; it is a different and worse thing,
  because it always returns an answer.
- **Chain length is a signal, not an error.** Resolution has **no hop limit** — a bound would silently
  hand back a tombstoned id, which is the single failure this function exists to prevent, and the
  argument for following every hop above is the argument for having no bound. Instead a chain longer
  than **three hops is reported**, because four merges in a row on one line of people does not mean the
  data is odd: it means the matcher is producing duplicates faster than a human can settle them, which is
  a statement about the queue and not about the row. Check 3 in §10 is written for exactly this: **a
  survivor that has itself been absorbed is what a chain looks like when it works**, so only the depth of a
  chain means anything.

"Every place that accepts a person id from outside must call this" is a rule about application code, which
application code can forget, and
[D-072](../decisions/round-06.md#d-072--the-documentation-carries-no-sql-the-schema-is-the-orms-job) took away the database-level ways
of catching the forgetting. **Check 4 in §10 is the net under it** — live rows that reference a tombstoned
person, the only form of this failure that is still visible after the fact.

---

## 10. Integrity checks

Checks that should run nightly and alert. These encode invariants that no per-column rule
above can express.

**Invariants to verify**

- **A person with more than one live account.** Count `account` rows per person whose status
  is `pending_verification`, `active` or `suspended`; anything above one is a breach of the
  rule in §4, and the point of the check is to confirm that rule really does exclude the
  pending-plus-active combination.
- **A tombstoned person with no merge record.** Count persons whose merge pointer is set but
  who do not appear as the merged person of any un-reversed `person_merge` row; non-zero
  means a pointer was written without the record that explains it, which is the case the
  append-only table in §8 exists to make impossible.
- **A merge chain longer than three hops.** Walk each tombstone's pointer and count the hops to the
  survivor; report the chains over three. **This is a report about a queue, not a finding about a row.**
  How *many* survivors have themselves been absorbed means nothing: with chains kept
  [D-087](../decisions/round-07-08.md#d-087--merge-chains-stay-because-reversing-a-merge-is-a-supported-operation),
  a person absorbed twice has a survivor who was absorbed, by construction, so that count is the normal
  shape of the data and its expected value is not zero. What carries information is the *depth*: four merges
  in a row on one line of people means the matcher is producing duplicates faster than a human can settle
  them. It is read alongside the review queue's age, never on
  its own, and it is not alertable — there is nothing wrong to fix on the row, and an alert that can only
  be answered by "work faster" trains people to ignore alerts.
- **A live row that references a tombstoned person.** Count rows in any table that names a person which
  point at a person whose merge pointer is set, where the referring row is itself live. **This is the
  only net under §9's rule that every entry point calls `resolve_person()`, and it exists because D-072
  took the database-level ones away.** Getting that call wrong is invisible at the moment it happens — a
  blank name in a list, at worst the wrong name — and permanent afterwards, because the row is written and
  referenced by whatever came after it. **This one alerts rather than logs**: the gap is not reconstructable
  later, and unlike a missing audit entry it misattributes a person rather than merely forgetting them.
- **A cycle in the merge graph.** Walk the pointers and look for a row reachable from itself. There should
  never be a single row here: §8 refuses a merge whose chosen survivor resolves to the person being
  absorbed, so **a non-zero count is not untidy data, it is that rule having failed**, and it is the one
  merge finding that should stop work rather than fill a report — `resolve_person()` does not terminate on
  a cycle, and every screen and every resolver hop that touches the affected people goes with it.
- **An account held below `active` by an unresolved hypothesis for more than 30 days.** Count accounts
  whose status is not `active` or `closed`, whose person is named by a hypothesis still in `proposed` or
  `needs_review`, where that hypothesis is older than 30 days — the same shape as the conflict-age check
  below, for the same reason. **It alerts rather than logs, and the reason is worth keeping in the check's
  own text: a stalled identity queue stopped being a data-quality problem the day it acquired the power to
  hold a login.** Behind each row is a specific person who cannot sign up — often to a camp whose form
  closes this week — and no channel by which to tell anyone except a telephone call.
- **Unresolved merge conflicts older than 30 days.** Count `field_conflict` rows resolved to
  `unresolved` and created more than 30 days ago; non-zero means the review queue is being
  ignored and the data is quietly wrong.
- **Redacted people still referenced by a live account.** Count `account` rows that are not
  closed and belong to a person with `redacted_at` set; non-zero means an erasure left a
  working login behind.
- **Imported people with no membership period.** Count people whose `record_origin` is
  `legacy_import` and who have no `membership` row at all. **What makes this a check rather than a census
  is the ratio:** a batch in which nobody has a period is a batch whose rows simply said nothing, and a
  batch whose stated-coverage figure disagrees with the periods written is a partially applied one. A row
  that created a membership its export did not state is a different finding, and lives in
  [06-audit-and-import.md §5](06b-redaction-and-checks.md#5-integrity-checks).
  **A check whose trigger condition is normal for the whole corpus is not a check.** This row is really a
  claim about what an import is allowed to conclude, and it has had to pass that test twice. Once when a
  roster-only row was the ordinary condition of the entire legacy corpus, so the check reported all of it
  as a failed batch — which is why
  [D-090](../decisions/round-07-08.md#d-090--the-legacy-corpus-is-thousands-of-roster-rows-with-numbers-and-no-money)
  turned it to *no participation row*. Once when the people export turned out to **state membership
  periods**, so the import writes bounded `membership` rows for precisely those people and nobody else
  ([D-093](../decisions/round-09.md#d-093--the-one-off-import-may-create-memberships-both-ends-dated)).
  The reading in between is void on its own terms: the participation table it named is deleted
  ([D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)).
  What survived both reversals is the test, which is why the row is read as a ratio and not as a count.
- **A redacted person with descriptive values still attached.** Stated where the rows are, as check 6
  of [09-attributes.md §8](09-attributes.md#8-integrity-checks) — attribute rows belonging to a
  redacted person, and attribute values still present in `audit_log`. It is named here because the
  redaction checks above are the same erasure guarantee read from the identity side, and a half-finished
  erasure does not announce which table it stopped in. Of everything on either list, that is the one
  that should alert rather than log.

---

## 11. Open issues

- Erasure policy specifics: what must be redacted vs. retained. **The retention shape is decided; what is
  open is whether it has a basis.** The shape is
  ([D-088](../decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short))
  — so what is left is the question a decision log cannot settle, namely whether indefinite retention of
  *named* `membership` and fee rows has a basis. See
  [00-conventions.md](00-conventions.md#8-personal-data-and-erasure) and
  [06-audit-and-import.md §6](06b-redaction-and-checks.md#6-open-issues).
- Whether `person.gender` is needed at all; if so, what value set.
- Whether the organization has (or will have) a national SSO identity provider — this
  determines how much of `account_credential` is actually used.

Both questions this page grew up around are settled and closed in the register: whether merge chains stay
(they do, and the two rules a permanent chain needs are written where they are obeyed — the cycle refusal
in §8, the length report in §10), and whether a person may hold two live accounts at once
(**no** — and the case that made that question hard is answered by a gate rather than an exception, so a
colliding sign-up files a claim and activates nothing instead of becoming a second account). See
[B-2](../open-questions.md#b-2) and [B-4](../open-questions.md#b-4).

All tracked in [../open-questions.md](../open-questions.md).
