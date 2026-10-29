# Identity Resolution and Legacy Data

How the system decides that two records describe the same human, and how four decades
of paper and spreadsheet history gets brought in without corrupting live data.

This is the highest-risk area of the project. Get it wrong and either the history is
unusable, or worse, two people's records get merged and you leak one member's data to
another. The design below is deliberately conservative.

---

## 1. Why this is hard

A 1994 row has: a name, maybe a birth date, **the period that person was a member**, and, on most
rows, a legacy member number
([D-090](../decisions/round-07-08.md#d-090--the-legacy-corpus-is-thousands-of-roster-rows-with-numbers-and-no-money)),
with free text — an address, remarks — in columns beside it. None of it can log in: the number keys
the organization's paper, not a session, and it is missing from precisely the rows that most need the
heuristics below — those predating the numbering, and those where it was written illegibly. Meanwhile:

- Names change (marriage, adoption, correction of a misspelling).
- Names repeat. In a youth organization spanning decades, "Jan Novák" is many people.
- Diacritics and transliterations vary across decades of manual entry (`Novák` / `Novak`).
- Birth dates are often wrong by a digit, or recorded as year-only.
- The same human appears in multiple rosters under slightly different spellings.

So: **automatic matching will produce both false positives and false negatives.**
False positive (two people merged) is a privacy incident. False negative (one person
split) is a data-quality annoyance. The design must therefore bias hard toward false
negatives — never merge on a guess.

**This document is about one half of a person.** Everything it resolves is *identity*: the fields
that make a row a particular human — names, birth date, the account, contact points, issued
identifiers. Everything the organization records about that human beyond those is
**descriptive data**, and it is deliberately absent from every table below: no descriptive value is
a match signal, and none may become one. A clothing size or a dietary habit identifies nobody, and
making matching depend on one would make the reliability of a person's history depend on what the
organization happened to collect about them
([08-person-data.md](08-person-data.md),
[D-085](../decisions/round-07-08.md#d-085--the-identity-machinery-stays-structured-the-boundary-is-rules-not-sensitivity)).
The line between the two halves is drawn by *what a machine may act on without a human*, not by
how delicate a fact feels; the test is stated in
[08-person-data.md](08-person-data.md#the-three-exceptions-and-why-they-are-exceptions).

---

## 2. The three record classes

Every `person` row carries `record_origin`:

| Origin | Meaning | Confidence | Has account? |
|--------|---------|-----------|--------------|
| `self_registered` | A human created this by registering | high | yes |
| `staff_created` | A registrar entered this person | high | maybe |
| `legacy_import` | Imported from historical records | **low** | no |

Legacy-imported people are **provisional**. They are fully queryable — a member who left in 1998 is
findable by name and birth date — but they are marked as unverified, they cannot be logged
into, and they are the only rows eligible to be absorbed by a merge.

**Rule: a merge always absorbs the lower-confidence row into the higher-confidence one.**
An import can never overwrite a self-registered person's data.

---

## 3. Identity hypotheses, not merges

The core mechanism. An **identity hypothesis** is a *proposal* that two person rows are
the same human. It is a first-class table row, with a confidence score, evidence, a
status, and a human decision.

The row holds the pair as `person_a_id` and `person_b_id`, stored in one order: `person_a_id`
names the lower id, and the two are never the same person — a pair has one canonical spelling
rather than two.

`confidence` is the matcher's score between 0 and 1; `match_signals` records which fields
agreed and how strongly, which is what a reviewer reads to see *why* it was proposed. `status`
is one of `proposed`, `needs_review`, `confirmed`, `rejected`, `superseded`. `proposed_by`
says where the proposal came from — `import_job`, `match_job` (the nightly batch matcher),
`person` or `staff` — and `proposed_at` when. `reviewed_by`, `reviewed_at` and `review_note` are the
human part, and a hypothesis may not reach `confirmed` or `rejected` without a `reviewed_at`. At most
one live hypothesis exists per pair — live means `proposed`, `needs_review` or `confirmed`.

### Lifecycle

```
  matcher proposes ──> proposed ──┬── staff confirms ──> confirmed ──> [merge executed]
                                  ├── staff rejects  ──> rejected (the pair becomes
                                  │                       proposable again — see §4)
                                  └── person asserts ──> needs_review → staff confirms/rejects
```

Three entry points:

1. **Import or background matching** proposes hypotheses automatically at low confidence.
2. **A registering person asserts their own history** — "I was a member 1990–2010" — which
   creates a hypothesis against the candidate rows, usually with `proposed_by = 'person'`.
3. **A sign-up that strong-matches a person who already exists** raises one by itself, without
   anyone asserting anything, and that hypothesis holds the new account out of `active`
   (§4,
   [D-089](../decisions/round-07-08.md#d-089--one-live-account-a-colliding-sign-up-files-a-claim-and-creates-nothing)).
   The queue is the same queue and the review is the same review; what a person at a registration
   form adds is the ability to put a row in it.

A person's own assertion is *evidence*, not proof. It must still be reviewed, because
claiming someone else's history is the obvious attack on an import-based system — and the
prize is that person's data. **Never auto-confirm a self-asserted link.**

---

## 4. Match signals

The matcher scores candidate pairs on independent signals. Recorded in `match_signals`
so a reviewer sees *why* the system proposed a match:

| Signal | Strength | Notes |
|--------|----------|-------|
| **Exact legacy member number** | **decisive** | The corpus carries these ([D-056](../decisions/round-04.md#d-056--the-legacy-import-expects-a-large-corpus-with-legacy-member-numbers)). Same number, same person — matched, not scored. |
| Exact birth date + exact normalised name | strong | Still not automatic — twins with similar names exist. |
| Birth date within ±1 day or year-only match + name | moderate | Common with hand-written records. |
| Name match after normalisation (diacritics, case, spacing) | moderate | Necessary but weak alone; "Jan Novák" is not unique. |
| Same postal address at the same time | moderate | Strong if the address is distinctive. Read from `person_contact` history — there is no household table ([D-057](../decisions/round-04.md#d-057--household-is-removed)). |
| Guardian name match | weak | Useful for minors in old records. |
| Name-only fuzzy match | **weak — never sufficient alone** | |

> **The decisive row changes the matcher's job.** With a number on the record, the question is
> not "are these two the same person?" but "does this number already point somewhere?" — a
> lookup. The scored signals below are then for the rows the number **cannot** resolve: legacy
> records predating the numbering, records where the number is illegible, and people who were
> never issued one. At thousands of rows
> ([D-056](../decisions/round-04.md#d-056--the-legacy-import-expects-a-large-corpus-with-legacy-member-numbers))
> this split is what makes
> [D-004](../decisions/round-01a.md#d-004--no-automatic-merging-ever) affordable: the numbered rows
> are the trustworthy set and the rest is a work queue.

### Normalisation

Applied before comparison, and the normalised form is stored so matching is
reproducible:

- Unicode NFKD, strip diacritics, casefold, collapse whitespace.
- Common nickname/legal-name equivalences (configurable per locale — `Jan`/`Jano`,
  `Josef`/`Josip`).
- Typo distance (Levenshtein/Jaro-Winkler) above a threshold counts as a partial match,
  never a full one.

### Thresholds

- **`confidence < 0.60`** — not surfaced. Stored only for diagnostics.
- **`0.60 ≤ confidence < 0.90`** — proposed, queued for human review.
- **`confidence ≥ 0.90`** — still requires human confirmation, but flagged as high
  priority. *There is no auto-merge threshold.*

**No automatic merging at all, even for a near-certain match**
([D-004](../decisions/round-01a.md#d-004--no-automatic-merging-ever)), and the rule does not need the
premise that a merge cannot be undone — it can (§6). It rests on what the reversal cannot reach: the
merged window stays one row's history, and the union of permissions is exercised from the moment the
merge commits, whatever is discovered afterwards. A privacy incident from a bad merge is worse than any
amount of manual review. The volume of the corpus — thousands of rows in two exports
([D-092](../decisions/round-09.md#d-092--the-corpus-is-people-and-events-and-it-names-no-units)), most
people rows carrying a number that makes the match a lookup rather than a judgement — is known, so no
auto-merge tier is needed and none is reserved.

### The same signals at sign-up, split at the top of the band

A registration form collides with these signals too. **A sign-up that strong-matches an existing
person raises an `identity_hypothesis` and is then held out of `active` by it** — an account may not
reach `active` while an unresolved hypothesis names its person
([D-089](../decisions/round-07-08.md#d-089--one-live-account-a-colliding-sign-up-files-a-claim-and-creates-nothing)).
The sign-up's own rows are created exactly as any sign-up creates them and stay
`pending_verification`; what "creates nothing" rules out is the *outcome* — **nothing is merged,
nothing is linked, nothing is activated**. The address the person typed stays on the pending account
as the credential it was offered as, which matters because the reviewer's other answer is "this is a
different person", and that answer should leave the applicant finishing the sign-up they started
rather than starting it again
([01-identity.md §4](../data-model/01-identity.md#4-account),
[02-actors.md §3](02-actors.md#3-account-state-machine)). Confirming the hypothesis merges the two
rows under §5 and the pending account goes with the row that was absorbed; rejecting it lifts the gate
and the account activates.

**Here the threshold is not a tuning parameter, it is the entire answer.** The band is split at its
top, and only the top reaches the gate:

| Signal at sign-up | Raises a blocking hypothesis? |
|---|---|
| Exact legacy member number | **yes** |
| Exact birth date **and** exact normalised name | **yes** |
| Birth date ±1 day, or year-only + name | no |
| Name-only fuzzy match, shared address, guardian name | no |

The soft band raises nothing at sign-up; the nightly matcher may still propose the pair for review, at
a confidence that queues it rather than blocking anybody. The tempting rule, "raise one whenever the
score is high", produces the failure this design would most deserve: a stranger's registration blocked
by a fuzzy score. The cost of the version chosen is bounded and self-correcting (a true duplicate slips
through, is matched nightly, and is reviewed); the cost of the tempting version is a child who cannot
sign up for a camp on the day the form closes, which is not self-correcting at all.

Two obligations come with the gate, and neither is a queue-management nicety:

- **A hypothesis that is blocking an account gets an age check, and it alerts.** Its victim is a
  specific person who cannot log in and whose only remaining channel is to telephone someone. The check
  is shaped like `field_conflict`'s thirty days
  ([08a-event-guards-and-checks.md §10](../data-model/08a-event-guards-and-checks.md#10-integrity-checks)); the alerting is the point.
- **The holding message confirms nothing.** It says the request was received and will be checked. It
  says nothing about whether the name, the birth date or the number matched anything, because a
  sign-up form that can answer "yes, that person exists" is an existence oracle, and this system's
  roster is children.

"I have a new e-mail address" is not this case and must not be routed through it:
`account_credential` holds many credentials for one account, so a new address is an addition to the
login a person already has. The collision case is narrower than signing up twice — it is a person
arriving through a door the system did not know they had. Resolving the claim is confirming or
rejecting a hypothesis, so it is `person.merge`, held by `identity_reviewer`
([../appendix/permission-catalog.md §2](../appendix/permission-catalog.md#2-people-and-identity));
there is deliberately no `account.link` code, because an automatic link would be D-004 under another
name.

---

## 5. The merge operation

Merging is a **soft merge**: the absorbed row survives as a tombstone.

```
person (surviving, id=100)          person (absorbed, id=847, tombstoned)
        ▲                                     │
        │                                     ▼
        └────────── person_merge ────► merged_into_person_id = 100
                 (id, surviving_person_id, merged_person_id,
                  merged_at, merged_by, hypothesis_id, reason)
```

### What moves

| Table | Action |
|-------|--------|
| `person_contact` | Reassigned to survivor. Conflicts (two `is_primary` of the same type) resolved by review, not by rule. |
| `person_identifier` | Reassigned. Duplicate scheme+value collapses to one. |
| `person_attribute` | Reassigned. **Two current values for one code is a review item, never a choice made by rule** — this table holds one value per person and code with no validity period to keep both, so unlike two past addresses a merge cannot leave the pair standing: the pair is raised as a `field_conflict` and a human decides, exactly as two `is_primary` contacts of one type are decided. Where the definition allows several values (`allow_multiple`), the two rows simply coexist and nothing is decided ([../data-model/09-attributes.md §3](../data-model/09-attributes.md#3-person_attribute--a-value-one-person-has)). |
| `person_name` | Reassigned, keeping validity periods — this is how a maiden name survives. |
| `account` | Reassigned to survivor. **If the survivor already has an account, the absorbed account is closed, not deleted.** |
| `membership` | Reassigned. Overlapping periods flagged for review — with one type (D-037) and a person-level no-overlap rule, an overlap here means a bad merge. An imported period can produce one too: the source states its own periods and nothing in the file knows that one human appears on two rows. Two imported periods covering the same date are outside the exclusion constraint — it watches the live statuses only — so the merge review is where they surface, and the honest reading of a pair is "the source said this", not "somebody decided this". |
| `person_group_member` | Reassigned, with the same overlap check. **Two rows for one person in one group over overlapping dates is a review item and not a dedupe**: two people who turn out to be one may genuinely have been put in the group twice, on different evidence, and the honest repair is one row whose dates a person chose. |
| `role_holder` | Reassigned. An office held twice by one person over overlapping periods is the same review case, with the same refusal to guess silently — and it is read out loud rather than filed quietly, because this table's rows are exactly what `ROLE(x)` reaches, so a duplicate holder row is a duplicate audience member. |
| `guardianship` (as dependent) | Reassigned. |
| `guardianship` (as guardian) | Reassigned. |
| `access_grant` | Reassigned. **Union of permissions results — this is the security-critical step.** Merging two people silently merges two sets of authority, and since [D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality) that union is literally the rows both people leave behind: no rank resolves a collision, so a `deny` on the absorbed row survives alongside the survivor's allows rather than being deduplicated away, which is the outcome to read out loud at review. |
| `audience_operand`, where `selector_kind` is `PERSON` | **Repointed, not reassigned.** Every hand-named person in the system is a `selector_arg_id` — a column with deliberately no foreign key ([D-011](../decisions/round-01a.md#d-011--scope_id-on-access_grant-is-polymorphic-with-no-foreign-key)), which is why this row is a requirement on the merge and not something the database notices ([D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)). **The failure is asymmetric and it is the loud one:** a leaf that resolves to nobody is the empty set, so a grant reading `EVERYONE - PERSON(x)` where `x` was merged away stops subtracting anybody and denies everybody. An orphan scan is the backstop; the merge is the mechanism. The same walk covers the other four argument kinds — an absorbed `person_group`, a deleted `role`, an `event`, a nested `audience` — because none of them has a key either |
| `person_merge` | Row inserted here. |
| `field_conflict` | Populated for anything that could not be resolved automatically. |

### What does *not* happen

- Nothing is deleted. The absorbed `person` row keeps its id and gains
  `merged_into_person_id`. All historical foreign keys pointing at it still resolve, so a
  question about who belonged to something in 1998 keeps working.
- Overlapping memberships are **never silently deduplicated**. Two overlapping memberships
  after a merge is suspicious — it may mean the merge was wrong. It becomes a review item.

### The cycle is refused here, not at the read

Chains are permanent (§6): `merged_into_person_id` is never rewritten forward, so A→B→C stays a chain
and `resolve_person()` walks it. A chain that loops would make that walk never end, so **a merge is
refused when the person chosen as survivor resolves — by walking the chain — to the person being
absorbed**
([D-087](../decisions/round-07-08.md#d-087--merge-chains-stay-because-reversing-a-merge-is-a-supported-operation)).
That subsumes the case already ruled out, nobody merges into themselves, and catches the one that
actually happens: absorbing B into A when A has already been absorbed into B.

Checking on the way in is the whole guard, and a read-side step limit is not an acceptable
substitute. A hop bound does not prevent the cycle; its only achievement is deciding which of two
wrong answers to return, and the wrong answer it returns is a tombstoned id — the exact failure
`resolve_person()` exists to prevent.

The other half of the same rule is softer and needs a net under it. "Every place that accepts a
person id from outside must call `resolve_person()`" is a rule application code can forget, and the
schema carries no way to catch it
([D-072](../decisions/round-06.md#d-072--the-documentation-carries-no-sql-the-schema-is-the-orms-job)).
What catches it is a report of live rows that reference a tombstoned person, which is the only form of
this failure that is visible after the fact
([../data-model/08a-event-guards-and-checks.md §10](../data-model/08a-event-guards-and-checks.md#10-integrity-checks)).

### The security rule that must not be skipped

Merging unions the two people's permissions. If a bad merge is performed, the survivor
gains the absorbed person's access. Therefore:

1. A merge is always performed by a human with `person.merge` permission.
2. The merged result's **effective permissions are re-displayed for confirmation** before
   the merge commits.
3. A merge can be undone (§6). The merged period cannot: `access_grant` rows created during it
   cannot be attributed to either human. Hence rule 2 — an unmerge repairs the record afterwards
   and does not repair this.
4. Nothing is invalidated by a merge, because nothing is stored that a merge could invalidate: no row
   maps a person to an answer
   ([D-114](../decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation)),
   and a merge is not a write that bumps the ruleset version. What the merge does to an answer is what
   the next check computes, from the survivor's grant rows and the `PERSON(x)` leaves the merge
   repointed. **That is the same fact that makes rule 2 load-bearing rather than courteous**: with
   nothing stored, the re-displayed effective permissions are the only place the merged answer is
   computed *before* the merge commits. See
   [06-authorization-model.md §8](06-authorization-model.md#8-there-is-no-permission-cache-and-what-replaces-it).

---

## 6. Reversing a merge

Unmerge is **a required operation**, not a courtesy for mistakes an organization hopes it will not
make
([D-087](../decisions/round-07-08.md#d-087--merge-chains-stay-because-reversing-a-merge-is-a-supported-operation)).
It is also why merge chains exist: over a chain a reversal is a replay of pointers, while over a
flattened pointer it would be a reconstruction of facts nobody recorded. **Flattening is therefore
closed off, not merely slower** — it is a trade against a named feature, not against tidiness.

A permanent chain needs two rules, and neither is enforced on the read:

- **No cycle, checked at the merge** (§5). Resolution deliberately has no hop limit.
- **Chain length is a signal, not an error.** Resolution is unbounded; a chain longer than **three
  hops is reported**. Four merges in a row on one line of people does not mean the row is odd — it
  means the matcher is producing duplicates faster than a human can settle them, which is a statement
  about the queue and not about the row. A survivor that has itself been absorbed is *normal*; only
  the length means anything
  ([../data-model/08a-event-guards-and-checks.md §10](../data-model/08a-event-guards-and-checks.md#10-integrity-checks)).

The reversal is four steps, and they restore the row split:

1. Clear `person.merged_into_person_id` on the absorbed row. The tombstone comes off.
2. Reassign rows **created before** `merged_at` back to the absorbed person.
3. Flag rows **created after** `merged_at` for human review. Those are the ambiguous ones, and
   they are reviewed rather than split by a rule.
4. Record the unmerge on the `person_merge` row as `reversed_at`, `reversed_by` and `reversal_note`.
   `person_merge` is append-only, so an unmerge records that a merge was undone rather than erasing
   the record of the mistake.

The `access_grant` rows are the specific hazard. Any grant created *during* the merged
window might belong to either human. Flag every one of them; do not guess.

**The asymmetry, stated plainly: the merge is reversible and the merged window is not.** Steps 1, 2
and 4 repair the record. Step 3 is an admission. Whatever those two humans did while they were one row
stays one row's history, because the grants exercised in that window were really exercised by somebody
the record can no longer separate — which is precisely why the confirmation-before-commit rule in §5 is
not made redundant by the existence of a reversal.

**Unmerge needs no permission code of its own.** Undoing an identity correction is the same act as
making one, performed by a named human, so it is `person.merge`
([../appendix/permission-catalog.md §2](../appendix/permission-catalog.md#2-people-and-identity)). A
`person.unmerge` code would grade undoing a mistake as safer than making one. Like the merge, the
reversal splits a person's permissions back in two, and there is nothing to invalidate: the split is
simply visible on the next check.

---

## 7. Legacy import pipeline

Staged, reviewed, idempotent. Never a direct write into live tables.

**What is arriving is two exports, and neither is a roster**
([D-092](../decisions/round-09.md#d-092--the-corpus-is-people-and-events-and-it-names-no-units)). A
roster is evidence of presence in a unit, which is not what the source says. The source says two
things:

| Half | What a row says | What the batch writes |
|---|---|---|
| **The membership export** | a name, a birth date, and **when that person was a member of the organization** | a `person`, and a **bounded** `membership` — both ends dated, `data_confidence = 'low'`, batch id on it ([D-093](../decisions/round-09.md#d-093--the-one-off-import-may-create-memberships-both-ends-dated)) |
| **The attendance export** | an event, and who came to it | an `event`, and one `event_registration` per attendee at `attending` / `was_present = true` ([D-094](../decisions/round-09.md#d-094--the-root-unit-owns-every-imported-event)) |

**Neither names a sub-unit, and nothing is assigned to one.** The parser keeps its parsed unit code —
an export that surprises whoever runs it with a unit column is exactly what that field and its
`unit_not_found` warning are for, and keeping them costs nothing — but **nothing reads them, no
`org_unit` is created by any batch, and no sub-unit participation row is ever imported**. Two halves
also means two shapes of batch on one `import_batch`: a people batch and an events batch, each carrying
the field map and the checks that fit its half, rather than one batch holding two mappers that can never
both apply.

**Say where it hurts, because somebody will ask this question.** The historical record this import
leaves behind **contains no sub-units**. "Who was in Pack 12 in 2011?" has no answer at go-live — not
a wrong one, none — and the first answer anyone reads will be a roster somebody typed in by hand.
Nothing in the model is missing: it is what the source can say, and it is written here so that the first
person to ask finds the sentence rather than the absence.

```
  source file(s)
       │
       ▼
  [1] staging_import          ── raw rows, verbatim, with the source file + line ref
       │
       ▼
  [2] staging_import_row      ── parsed: normalised name, parsed birth date,
       │                          detected unit, parse warnings
       ▼
  [3] matching                ── for each row, find candidate person rows and score them
       │
       ▼
  [4] review queue            ── human confirms: link to existing | create new | discard
       │
       ▼
  [5] apply                   ── a people batch writes person + bounded membership; an events
       │                          batch writes event + event_registration. Never an org_unit,
       │                          never a sub-unit participation row, never an open-ended
       │                          membership
       │
       ▼
  [6] import_log              ── what was applied, by whom, when; reversal instructions
```

### Requirements

- **Idempotent.** Re-running the same import must not duplicate people. Each staged row
  carries a deterministic `source_row_hash`; re-import matches on it.
- **Reversible per batch.** `import_log` records every row created or modified in a batch,
  so a bad batch can be rolled back without touching other data.
- **Never overwrites self-registered data.** If a legacy row matches a `self_registered`
  person, the import may *add* what the export evidences — a bounded historical membership
  period, a registration on an imported event — but never alters names, contacts, identifiers,
  or descriptive values the person maintains themselves. An added closed period contradicts
  nothing the person typed: it is a dated claim about the past, sitting beside their live row
  rather than over it. An *open-ended* period would be a different thing entirely, which is why
  the surviving ban is exactly that one.
- **Preserves provenance.** Every imported row records `import_batch_id` and
  `source_reference` (file + line), so any value can be traced back to the paper it came
  from. When someone disputes a historical record, you can show them where it came from.
- **Records uncertainty rather than guessing.** A row that cannot be parsed cleanly goes
  to the review queue with the raw value intact — it does not get a best-effort guess
  written as if it were fact.

### Raw columns become codes

Old rosters carry columns about the *person* — a remarks column, a "medical" column, a list of shirt
sizes — and each of those arrives at step [5] as a value against a **code**, not as a blob beside the
record
([D-084](../decisions/round-07-08.md#d-084--descriptive-data-is-organization-defined-at-runtime)).
Those columns are in the **membership export**; the attendance export brings nothing that maps to an
attribute code
([D-090](../decisions/round-07-08.md#d-090--the-legacy-corpus-is-thousands-of-roster-rows-with-numbers-and-no-money)).
The map therefore belongs to the people batch and a code-to-registration map to the events batch: one
batch, one map. That makes the first import the single largest event in the life of this vocabulary —
several hundred codes out of one file. The rest of the rules live in staging
([../data-model/09-attributes.md §7](../data-model/09-attributes.md#7-the-legacy-import-which-is-where-the-vocabulary-comes-from));
three consequences follow from arriving all at once.

- **The map is authored and read before the batch applies, not after.** The mapping is recorded on the
  batch as one object rather than per staged row because it is one artefact a person reads once, top to
  bottom, and the reading is what makes the codes it names trustworthy. Reading it afterwards would put
  the live vocabulary at the mercy of whatever the batch had already written. Changing an applied map is
  curation with an audit entry, not a migration.
- **A raw column that maps to no code stops the batch**, unless someone maps it or marks it
  `discarded` with a reason. An unmapped column is a decade of something the organization used to
  collect vanishing quietly.
- **A column nobody recognises becomes a code named from the column**, never a guess at an existing
  code: an import-time merge is invisible and unreviewable, and the review queue above is for people,
  not for vocabulary. **The codes the map names arrive `live`.** A curator has just read every name in
  the map, which is exactly the endorsement `proposed` withholds. `proposed` keeps its meaning of
  *improvised later by a person at a desk* — a fact with no code yet — and not "whatever the import did
  not understand". Several hundred codes landing `proposed` on day one would open the curation queue
  full, make its age signal meaningless before it had ever meant anything, and teach the organization
  that the attribute layer's warning queue is noise. Who holds `attribute.define` day to day, and how
  long a runtime proposal may sit, stays open
  ([AT-2](../open-questions.md#at-2--who-curates-the-vocabulary-and-how-long-may-a-proposal-sit)).

### What each source row lands on

| What the source says | It becomes | Why |
|---|---|---|
| "Jan Novák, born 1962, member 1990–1995" | a `person` with `record_origin = 'legacy_import'`, and **one `membership` per period the source states** — `valid_from` *and* `valid_to` set, `data_confidence = 'low'`, `import_batch_id` set, the renewal chain left to whoever reconstructs it | A stated period is evidence of membership and infers nothing; a closed period cannot gate anything ([D-093](../decisions/round-09.md#d-093--the-one-off-import-may-create-memberships-both-ends-dated)) |
| the same, with the year repeated in the file | a **second `membership` only if the source states a second period**; consecutive stated years stretch to one row, a gap in the source opens another | One row per stated period keeps one row per membership, and a lapse stays visible in the one table that means it |
| an event, and who came to it | an `event` **with no owner column at all**, one `event_registration` per attendee at `attending` with `was_present = true`, and the per-event instantiation of the seeded answers-view grant | Nothing owns an event: its people are named by selectors that bind to it ([D-102](../decisions/round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)) |
| a person who might have come and did not | **nothing** | An export lists who came. Writing `not_attending` from silence puts words in a source that said nothing ([D-059](../decisions/round-05.md#d-059--unanswered-is-the-absence-of-a-row-a-registration-stores-two-values)) |
| a sub-unit | **nothing, ever** — and there is now nothing that could be one | The corpus names none (§7) and there is no structure to attach a name to. The row stays because it is the one a reader holding a 1998 spreadsheet will ask, and the answer has to be written down rather than inferred from absence |
| money | **nothing** — and no `fee_obligation` | The corpus has no money in it (D-090) |

**The ban is one sentence, and it is the whole point: never an open-ended membership, and never one
inferred from an attendance row.** `is_current_member()` and the permission gate
([D-039](../decisions/round-02-03.md#d-039--member-permissions-require-a-current-paid-membership)) both
read `membership`, so a row running to no `valid_to` hands whoever signs up under that name authority in
the present. The ban is sized for what it now guards: one reviewed batch whose map is read before it
applies, on a corpus that will never arrive twice.

**The line the whole design turns on is evidence against inference.** A row that says *member
1990–1995* is evidence of a membership; a row that says *in Pack 12 in 1998* is evidence of presence and
nothing more. Generating a membership for every historical row because the old data model implied it,
and then marking it inferred, is the refusal that stands. A related observation worth keeping in front of
anybody implementing this: **a conditional with one live arm is not a safe default** — wording of the
form "X unless there is payment evidence", on a corpus that carries no payment data at all, leaves an arm
with an empty set to fire on while still inviting somebody to build it.

**Four consequences that arrive with the memberships.**

- **No obligation, no payment, no balance.** An imported membership creates **no `fee_obligation`**, and
  that has to be a rule rather than an accident: an obligation per historical year would land as
  `unpaid` and turn a decade of members into a wall of debt with a 1999 `due_date` for the lapse sweep to
  choke on. Related, and load-bearing rather than incidental: `outstanding_balance` is **null** on these
  rows — a zero would be a claim of *settled* that no export supports.
- **The person-level no-overlap rule is in the import's path.** One row per period the source states,
  not one per calendar year, is a rule with a consequence: two stated periods covering one date violate
  it and reach the review queue (§5).
- **These rows are the oldest layer of the skeleton D-088 keeps forever**
  ([D-088](../decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)):
  thousands of named people with birth dates who were never asked and never used the system, held on an
  unverified legal basis. Same judgement as for live rows, much larger population.
- **Every cross-decade member count is a mixture** of an export and a register, distinguished only by
  `data_confidence` and `import_batch_id`. A membership-rate chart spanning the import boundary compares
  a source that *states* membership with a system that *records* it, and nothing in the query knows the
  difference.

**A historical membership is also obtainable as a human act.** Where the organization has a period the
export does not state — a ledger found later, a written confirmation, a person who was a member in a year
the file lost — the period is entered by hand under `membership.backdate`
([../appendix/permission-catalog.md §4](../appendix/permission-catalog.md#4-membership)). The pipeline
carries the stated ones; this is the route for the unstated: deliberate, attributed, outside the batch.

**End dates are still often unknown, and this is the sharpest case of it.** A period the export leaves
open — someone last seen in a 2003 row with no end stated — cannot be written open: that is the one shape
refused outright, and an unbounded historical record is the same hazard wearing a different name.
Convention: **end it at the end of the school/organizational year of the last row they appear in, marked
as inferred.** That is the *only* date the import infers — the periods themselves are stated — and it is
precisely what the organizational year boundary is needed for, which is still open
([A-4](../open-questions.md#a-4-remainder--the-organizational-calendar)). With attendance and no money in
the corpus, it is the sharpest remaining import question. Document the rule you choose; it will be
questioned.

---

## 8. The returning-member case

The scenario member 1990–2010, returns 2024, should be the *smooth* path, because it is a common and
important one (returning alumni become adult leaders and donors).

Flow:

1. Person registers in 2024, self-asserting past membership.
2. The system matches them against legacy rows and proposes hypotheses.
3. A registrar reviews and confirms.
4. The historical membership (1990–2010) and the current membership (2024–present) now sit
   under one `person` row, as **two `membership` rows**.
5. Their profile shows their full history; the gap is explicit data.
6. Any seniority or "years of service" calculation reads across both.

**A 1990–2010 `membership` appears only where the source states the period or somebody records it by hand
on evidence** (`membership.backdate`, §7). The smooth path restores a person's member history without a
human typing it, and what makes that safe is that the source **states** the period rather than the import
guessing one.

Steps 2–3 can be streamlined when the match is strong (exact old membership number), but
the confirmation step remains, for the reason in §3.

**What the activation gate costs this path.** The gate does not distinguish why a hypothesis exists: an
account may not reach `active` while an unresolved hypothesis *names its person*, and a self-asserted
claim names that person exactly as a collision does. So the smooth path has a human between registration
and login, where the review could otherwise happen after the person was already using the system. The
mitigation is the age check that alerts (§4), plus the fact that with a legacy number in hand step 2 is a
lookup a registrar settles in seconds. What is *not* settled is whether a hypothesis the person raised
about themselves should hold their account out of `active` at all, as against a hypothesis the system
raised about a stranger who happened to match. Recorded in §9.

### Self-service without weakening the guarantee

Rather than auto-linking, give the person a **claim** flow: they assert a past membership,
staff confirm. Record the assertion on the hypothesis row, so that if the claim later
proves false, you can see it was self-asserted rather than discovered.

---

## 9. Open issues

Still open, and tracked in [../open-questions.md](../open-questions.md):

- Whether twins/siblings with similar names and the same birth date need a documented
  disambiguation procedure (recommend: yes, and never merge them automatically). The sign-up gate in §4
  sharpens this: same birth date plus a normalised name is exactly the collision pair, and a collision
  now stops a registration instead of merely queueing a card.
- Whether a hypothesis a person raised about *themselves* should hold their account out of `active`,
  as against one the system raised because a stranger's sign-up strong-matched them (§8).
- The organizational year boundary that historical end dates get inferred from
  ([A-4](../open-questions.md#a-4-remainder--the-organizational-calendar)). With stated membership
  periods, attendance, and no money (§7) it is load-bearing by itself, and the inferred date closes a
  `membership` row, so the number of rows it touches is large.
- Whether indefinite retention of named membership and fee rows has a legal basis. The design keeps that
  skeleton indefinitely as the organization's own history while audit payloads are emptied after 24
  months
  ([D-088](../decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short));
  a decision log cannot grant the basis, so it is recorded as an assumption awaiting review.

---

*Decisions behind this page: D-004, D-011, D-037, D-038, D-039, D-056, D-057, D-059, D-072, D-084, D-085,
D-087, D-088, D-089, D-090, D-092, D-093, D-094, D-097, D-099, D-102, D-105, D-114.*
