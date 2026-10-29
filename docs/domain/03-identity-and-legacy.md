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
with free text — an address, remarks — in columns beside it. This opening sentence used to read
"a unit, a year"; the corpus
([D-092](../decisions/round-09.md#d-092--the-corpus-is-people-and-events-and-it-names-no-units))
names no unit at all, which costs §7 more than it costs this section. What this section used to open
with instead — "no unique key" — was written before the corpus had been described and was wrong in the
useful direction. What is still true is that none of it can log in:
the number keys the organization's paper, not a session, and it is missing from precisely the rows
that most need the heuristics below — those predating the numbering, and those where it was written
illegibly. Meanwhile:

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

Legacy-imported people are **provisional**. They are fully queryable — "who was in
Troop 12 in 1998" must work — but they are marked as unverified, they cannot be logged
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
`person` or `staff` — and `proposed_at` when. `reviewed_by`, `reviewed_at` and `review_note` are the human part, and a
hypothesis may not reach `confirmed` or `rejected` without a `reviewed_at`. At most one live
hypothesis exists per pair — live means `proposed`, `needs_review` or `confirmed`.

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
   (§4, [D-089](../decisions/round-07-08.md#d-089--one-live-account-a-colliding-sign-up-files-a-claim-and-creates-nothing)).
   The queue is the same queue and the review is the same review; what is new is that a person
   arriving at a registration form can put a row in it.

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
| Same unit + overlapping membership period | moderate | Corroborating, not identifying. |
| Same postal address at the same time | moderate | Strong if the address is distinctive. Read from `person_contact` history — there is no household table ([D-057](../decisions/round-04.md#d-057--household-is-removed)). |
| Guardian name match | weak | Useful for minors in old records. |
| Name-only fuzzy match | **weak — never sufficient alone** | |

> **The decisive row changes the matcher's job.** With a number on the record, the question is
> not "are these two the same person?" but "does this number already point somewhere?" — a
> lookup. The scored signals below are then for the rows the number **cannot** resolve: legacy
> records predating the numbering, records where the number is illegible, and people who were
> never issued one. At thousands of rows ([D-056](../decisions/round-04.md#d-056--the-legacy-import-expects-a-large-corpus-with-legacy-member-numbers))
> this split is what makes [D-004](../decisions/round-01a.md#d-004--no-automatic-merging-ever)
> affordable: the numbered rows are the trustworthy set and the rest is a work queue.

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
  priority. *There is no auto-merge threshold.* A privacy incident from a bad merge is
  worse than any amount of manual review.

This paragraph used to rest the no-auto-merge rule on merges being "irreversible in practice", and
that premise has been withdrawn: [D-087](../decisions/round-07-08.md#d-087--merge-chains-stay-because-reversing-a-merge-is-a-supported-operation)
made unmerge a required operation (§6). The rule does not need the false premise. It rests on what
the reversal cannot reach — the merged window stays one row's history — and on the union of
permissions being exercised from the moment the merge commits, whatever is discovered afterwards.

*Assumption, now settled:* **no automatic merging at all**, even for near-certain matches
([D-004](../decisions/round-01a.md#d-004--no-automatic-merging-ever)). This document left an
escape hatch open on the theory that the volume of historical data might make manual review
infeasible, and offered an opt-in auto-merge tier for that case. The volume is now known: thousands
of rows arriving in two exports ([D-092](../decisions/round-09.md#d-092--the-corpus-is-people-and-events-and-it-names-no-units)),
most of the people rows carrying a number that makes the match a lookup rather than a judgement
([D-090](../decisions/round-07-08.md#d-090--the-legacy-corpus-is-thousands-of-roster-rows-with-numbers-and-no-money)).
The hatch is not needed, and it is not reserved.

### The same signals at sign-up, split at the top of the band

Until now these signals were read only by machinery working over the import. A registration form
collides with them too. **A sign-up that strong-matches an existing person raises an
`identity_hypothesis` and is then held out of `active` by it** — an account may not reach `active`
while an unresolved hypothesis names its person
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
| Name-only fuzzy match, shared unit, shared address, guardian name | no |

The soft band raises nothing at sign-up. It keeps doing what it always did — the nightly matcher may
propose the pair for review, at a confidence that queues it rather than blocking anybody. The
tempting rule, "raise one whenever the score is high", produces the failure this design would most
deserve: a stranger's registration blocked by a fuzzy score. The cost of the version chosen is
bounded and self-correcting (a true duplicate slips through, is matched nightly, and is reviewed);
the cost of the tempting version is a child who cannot sign up for a camp on the day the form closes,
which is not self-correcting at all.

Two obligations come with the gate, and neither is a queue-management nicety:

- **A hypothesis that is blocking an account gets an age check, and it alerts.** A stalled identity
  queue used to be a data-quality problem with no victim you could name. Now its victim is a specific
  person who cannot log in and whose only remaining channel is to telephone someone. The check is
  shaped like `field_conflict`'s thirty days
  ([01-identity.md §10](../data-model/01-identity.md#10-integrity-checks)); the alerting is the part
  that changed.
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
| `membership` | Reassigned. Overlapping periods flagged for review — with one type (D-037) and a person-level no-overlap rule, an overlap here means a bad merge. **That used to be the only way to make one; since D-093 an imported period can produce it too**, because the source states its own periods and nothing in the file knows that one human appears on two rows. Two imported periods covering the same date are outside the exclusion constraint — it watches the live statuses only — so the merge review is where they surface, and the honest reading of a pair is "the source said this", not "somebody decided this". |
| `person_group_member` | Reassigned, with the same overlap check. **Two rows for one person in one group over overlapping dates is a review item and not a dedupe**: two people who turn out to be one may genuinely have been put in the group twice, on different evidence, and the honest repair is one row whose dates a person chose. |
| `role_holder` | Reassigned. An office held twice by one person over overlapping periods is the same review case, with the same refusal to guess silently — and it is read out loud rather than filed quietly, because this table's rows are exactly what `ROLE(x)` reaches, so a duplicate holder row is a duplicate audience member. |
| `guardianship` (as dependent) | Reassigned. |
| `guardianship` (as guardian) | Reassigned. |
| `access_grant` | Reassigned. **Union of permissions results — this is the security-critical step.** Merging two people silently merges two sets of authority, and since [D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality) that union is literally the rows both people leave behind: no rank resolves a collision, so a `deny` on the absorbed row survives alongside the survivor's allows rather than being deduplicated away, which is the outcome to read out loud at review. `role_assignment` is gone from this table — the office rows moved to `role_holder` above, where an overlap is already a review case |
| `audience_operand`, where `selector_kind` is `PERSON` | **Repointed, not reassigned, and this row is newer than the rest of the table.** [D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other) deleted `audience_member`, so every hand-named person in the system is now a `selector_arg_id` — a column with deliberately no foreign key ([D-011](../decisions/round-01a.md#d-011--scope_id-on-access_grant-is-polymorphic-with-no-foreign-key)), which is why this row is a requirement on the merge and not something the database notices. **The failure is asymmetric and it is the loud one:** a leaf that resolves to nobody is the empty set, so a grant reading `EVERYONE - PERSON(x)` where `x` was merged away stops subtracting anybody and denies everybody. An orphan scan is the backstop; the merge is the mechanism. The same walk covers the other four argument kinds — an absorbed `person_group`, a deleted `role`, an `event`, a nested `audience` — because none of them has a key either |
| `person_merge` | Row inserted here. |
| `field_conflict` | Populated for anything that could not be resolved automatically. |

### What does *not* happen

- Nothing is deleted. The absorbed `person` row keeps its id and gains
  `merged_into_person_id`. All historical foreign keys pointing at it still resolve,
  so "who was in Troop 12 in 1998" keeps working.
- Overlapping memberships are **never silently deduplicated**. Two overlapping memberships
  after a merge is suspicious — it may mean the merge was wrong. It becomes
  a review item. (This bullet used to say *child* memberships, a distinction the model stopped
  making with one membership type and ageless membership
  ([D-037](../decisions/round-02-03.md#d-037--exactly-one-membership-type-the-fee-is-flat-and-per-person),
  [D-038](../decisions/round-02-03.md#d-038--membership-is-ageless)); what it described — two open periods
  on one person — is the same suspicious shape.)

### The cycle is refused here, not at the read

Chains are permanent (§6): `merged_into_person_id` is never rewritten forward, so A→B→C stays a chain
and `resolve_person()` walks it. A chain that loops would make that walk never end, so **a merge is
refused when the person chosen as survivor resolves — by walking the chain — to the person being
absorbed** ([D-087](../decisions/round-07-08.md#d-087--merge-chains-stay-because-reversing-a-merge-is-a-supported-operation)).
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
([../data-model/01-identity.md §10](../data-model/01-identity.md#10-integrity-checks)).

### The security rule that must not be skipped

Merging unions the two people's permissions. If a bad merge is performed, the survivor
gains the absorbed person's access. Therefore:

1. A merge is always performed by a human with `person.merge` permission.
2. The merged result's **effective permissions are re-displayed for confirmation** before
   the merge commits.
3. A merge can be undone (§6). The merged period cannot: `access_grant` rows created during it
   cannot be attributed to either human. Hence rule 2 — an unmerge repairs the record afterwards
   and does not repair this.
4. ~~Merges invalidate cached permissions.~~ **There are no cached permissions to invalidate** —
   [D-114](../decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation)
   deleted the answer cache, and a person merge is one of the writes that dropped out of the surviving bump
   set with it: a merge changes which grant rows and operand leaves name the person, and both are read live now. What the merge does to
   an answer is therefore just what the next check computes, from the survivor's grant rows and the `PERSON(x)`
   leaves the merge repointed. **That is the same fact that makes rule 2 load-bearing rather than courteous**: with nothing stored,
   the re-displayed effective permissions are the only place the merged answer is computed *before* the merge
   commits. See [06-authorization-model.md](06-authorization-model.md#8-there-is-no-permission-cache-and-what-replaces-it).

---

## 6. Reversing a merge

Unmerge is **a required operation**, not a courtesy for mistakes an organization hopes it will not
make ([D-087](../decisions/round-07-08.md#d-087--merge-chains-stay-because-reversing-a-merge-is-a-supported-operation)).
It is also the reason merge chains exist, so it is worth being honest about which way the
justification now runs. Chains were argued for *because* flattening would make a reversal impossible —
an assumption resting on a capability nobody had asked for. Somebody has asked for it now, so the
capability is the requirement and the chain is its consequence. Over a chain a reversal is a replay of
pointers; over a flattened pointer it would be a reconstruction of facts nobody recorded.
**Flattening is therefore closed off, not merely slower**, and "flattening is faster" is no longer a
trade against tidiness — it is a trade against a feature someone named.

A permanent chain needs two rules, and neither is enforced on the read:

- **No cycle, checked at the merge** (§5). Resolution deliberately has no hop limit.
- **Chain length is a signal, not an error.** Resolution is unbounded; a chain longer than **three
  hops is reported**. Four merges in a row on one line of people does not mean the row is odd — it
  means the matcher is producing duplicates faster than a human can settle them, which is a statement
  about the queue and not about the row. With chains decided, a survivor that has itself been absorbed
  is *normal*; only the length means anything
  ([../data-model/01-identity.md §10](../data-model/01-identity.md#10-integrity-checks)).

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
reversal splits a person's permissions back in two — and since nothing maps a person to an answer any more
([D-114](../decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation)),
there is nothing to invalidate: the split is simply visible on the next check, which is the same §5 rule
stated on the way back.

---

## 7. Legacy import pipeline

Staged, reviewed, idempotent. Never a direct write into live tables.

**What is actually arriving is two exports, and neither is a roster**
([D-092](../decisions/round-09.md#d-092--the-corpus-is-people-and-events-and-it-names-no-units)).
This section spent two rounds describing *roster rows* — people attending units — and the whole
pipeline hung off that word, because a roster is evidence of presence in a unit and that is not what
the source says. It says two things:

| Half | What a row says | What the batch writes |
|---|---|---|
| **The membership export** | a name, a birth date, and **when that person was a member of the root unit** | a `person`, and a **bounded** `membership` — both ends dated, `data_confidence = 'low'`, batch id on it — which brings its root-unit participation row with it ([D-093](../decisions/round-09.md#d-093--the-one-off-import-may-create-memberships-both-ends-dated)) |
| **The attendance export** | an event, and who came to it | an `event` owned by **the root**, and one `event_registration` per attendee at `attending` / `was_present = true` ([D-094](../decisions/round-09.md#d-094--the-root-unit-owns-every-imported-event)) |

**Neither names a sub-unit, and nothing is assigned to one.** The parser keeps its parsed unit code
— an export that surprises whoever runs it with a unit column is exactly what that field and its
`unit_not_found` warning are for, and keeping them costs nothing — but **nothing reads them, no
`org_unit` is created by any batch, and no sub-unit `unit_participation` row is ever imported**. Two
halves also means two shapes of batch on one `import_batch`: a people batch and an events batch, each
carrying the field map and the checks that fit its half, rather than one batch holding two mappers
that can never both apply.

**Say where it hurts, because somebody will ask this question.** The historical record this import
leaves behind **contains no sub-units**. "Who was in Pack 12 in 2011?" has no answer at go-live — not
a wrong one, none — and the first answer anyone reads will be a roster somebody typed in by hand.
Nothing in the model is missing: participation rows, historical units and unit relationships have
always been able to hold it. It is what the source can say, and it is written here so that the first
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
  [5] apply                   ── a people batch writes person + bounded membership (+ its
       │                          root participation row); an events batch writes event
       │                          (owned by the root) + event_registration. Never an
       │                          org_unit, never a sub-unit participation row, never an
       │                          open-ended membership
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
  period and its root participation row, a registration on an imported event — but never alters
  names, contacts, identifiers, or descriptive values the person maintains themselves. The
  distinction is that an added closed period contradicts nothing the person typed: it is a dated
  claim about the past, sitting beside their live row rather than over it. An *open-ended* period
  would be a different thing entirely, which is why D-093's surviving ban is exactly that one.
- **Preserves provenance.** Every imported row records `import_batch_id` and
  `source_reference` (file + line), so any value can be traced back to the paper it came
  from. When someone disputes a historical record, you can show them where it came from.
- **Records uncertainty rather than guessing.** A row that cannot be parsed cleanly goes
  to the review queue with the raw value intact — it does not get a best-effort guess
  written as if it were fact.

### Raw columns become codes

The pipeline was drawn when a legacy column could only ever be a name, a date or a unit. Old
rosters also carry columns about the *person* — a remarks column, a "medical" column, a list of
shirt sizes — and each of those arrives at step [5] as a value against a **code**, not as a blob
beside the record ([D-084](../decisions/round-07-08.md#d-084--descriptive-data-is-organization-defined-at-runtime)).
The corpus carries those columns alongside the identity columns, in the **membership export** — they
are columns about a person, and the attendance export brings nothing that maps to an attribute code
([D-090](../decisions/round-07-08.md#d-090--the-legacy-corpus-is-thousands-of-roster-rows-with-numbers-and-no-money),
[D-092](../decisions/round-09.md#d-092--the-corpus-is-people-and-events-and-it-names-no-units));
the map therefore belongs to the people batch, and a code-to-registration map to the events batch,
which is what "one batch, one map" survives as once a batch states which half it carries. That makes
the first import the single largest event in the life of this vocabulary: several hundred codes out
of one file. The rest of the rules for this live in staging
([../data-model/09-attributes.md §7](../data-model/09-attributes.md#7-the-legacy-import-which-is-where-the-vocabulary-comes-from));
three consequences follow from arriving all at once.

- **The map is authored and read before the batch applies, not after.** That is precisely why the
  mapping is recorded on the batch as one object rather than per staged row: it is one artefact a
  person reads once, top to bottom, and the reading is what makes the codes it names trustworthy.
  Reading it afterwards would put the live vocabulary at the mercy of whatever the batch had already
  written. Changing an applied map is curation with an audit entry, not a migration.
- **A raw column that maps to no code stops the batch**, unless someone maps it or marks it
  `discarded` with a reason. An unmapped column is a decade of something the organization used to
  collect vanishing quietly, which is the class of failure the rest of this document exists to
  prevent on the identity side.
- **A column nobody recognises becomes a code named from the column**, never a guess at an existing
  code: an import-time merge is invisible and unreviewable, and the review queue above is for people,
  not for vocabulary. **The codes the map names arrive `live`.** This document said they arrived
  `proposed`, and the error is worth keeping in view because it costs more than the word: a curator
  has just read every name in the map, which is exactly the endorsement `proposed` withholds.
  `proposed` keeps its meaning of *improvised later by a person at a desk* — a fact with no code yet —
  and not "whatever the import did not understand". Several hundred codes landing `proposed` on day
  one would open the curation queue full, make its age signal meaningless before it had ever meant
  anything, and teach the organization that the attribute layer's warning queue is noise. Who holds
  `attribute.define` day to day, and how long a runtime proposal may sit, is a different question and
  stays open ([AT-2](../open-questions.md#at-2--who-curates-the-vocabulary-and-how-long-may-a-proposal-sit)).

### What each source row lands on

This subsection was headed "Historical rows from imports" and said that an imported **roster** row
yields a `person`, a `unit_participation` bounded to the roster's year, and **no `membership`** — the
rule [D-090](../decisions/round-07-08.md#d-090--the-legacy-corpus-is-thousands-of-roster-rows-with-numbers-and-no-money)
recorded, before there was a heading to withdraw. **That frame is superseded in its second half, one
round later, by
[D-092](../decisions/round-09.md#d-092--the-corpus-is-people-and-events-and-it-names-no-units) and
[D-093](../decisions/round-09.md#d-093--the-one-off-import-may-create-memberships-both-ends-dated)**,
and the sequence is worth leaving visible: both rounds reasoned correctly from a file nobody had
read. What the source states, and what arrives:

| What the source says | It becomes | Why |
|---|---|---|
| "Jan Novák, born 1962, member 1990–1995" | a `person` with `record_origin = 'legacy_import'`, and **one `membership` per period the source states** — `valid_from` *and* `valid_to` set, `data_confidence = 'low'`, `import_batch_id` set, the renewal chain left to whoever reconstructs it | A stated period is evidence of membership and infers nothing; a closed period cannot gate anything ([D-093](../decisions/round-09.md#d-093--the-one-off-import-may-create-memberships-both-ends-dated)) |
| the same, with the year repeated in the file | a **second `membership` only if the source states a second period**; consecutive stated years stretch to one row, a gap in the source opens another | This row used to be the *root participation row* the membership obligation required, stretched by exactly this rule and carrying exactly one cost: the lapse stopped being visible in the participation table. [D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row) deleted the row, and the cost with it — **a lapse is now visible in one table, which is the table that means it** ([D-050](../decisions/round-04.md#d-050--a-renewal-inside-the-window-extends-the-existing-root-participation-row), superseded) |
| an event, and who came to it | an `event` **with no owner column at all**, one `event_registration` per attendee at `attending` with `was_present = true`, and — since [D-102](../decisions/round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it) — the per-event instantiation of the seeded answers-view grant | There is no unit to own it and no rule asking for a root: an event's people are named by selectors that bind to it, which is also the import-side saving [D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row) counted ([D-102](../decisions/round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)) |
| a person who might have come and did not | **nothing** | An export lists who came. Writing `not_attending` from silence puts words in a source that said nothing ([D-059](../decisions/round-05.md#d-059--unanswered-is-the-absence-of-a-row-a-registration-stores-two-values)) |
| a sub-unit | **nothing, ever** — and there is now nothing that could be one | The corpus names none (§7), and [D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row) deleted the thing a name could have attached to. The row stays because it is the one a reader holding a 1998 spreadsheet will ask, and the answer has to be written down rather than inferred from absence |
| money | **nothing** — and no `fee_obligation` | The corpus has no money in it (D-090) |

**The ban that survives is one sentence, and it is the one that was always the point: never an
open-ended membership, and never one inferred from an attendance row.** The reason has not moved since
the two were split apart — `is_current_member()` and the permission gate
([D-039](../decisions/round-02-03.md#d-039--member-permissions-require-a-current-paid-membership))
both read `membership`, so a row running to no `valid_to` hands whoever signs up under that name
authority in the present. What narrowed the ban is that it was written for a **standing** hazard — an
import that infers, run by whoever holds the file, repeatedly, for years — and this is one reviewed
batch whose map is read before it applies, on a corpus that will never arrive twice. A rule sized for
a recurring process is too strict for a one-time one; the safety that mattered was the review, not the
prohibition.

**What the withdrawn rule got right, kept in view because it is the part that still binds.** The
section was written against a real temptation — generate a membership for every historical row because
that is what the old data model implied, then mark it inferred — and that refusal stands. The line the
whole exchange turns on is **evidence against inference**: a row that says *member 1990–1995* is
evidence of a membership, and a row that says *in Pack 12 in 1998* is evidence of presence and nothing
more. D-093 moved only the first half, because it turned out the file states periods; the reading that
*"a 1998 roster row is participation, not membership"* remains exactly true of a roster row, and there
simply are no roster rows. Note too the observation that outlived the rule it justified: **a
conditional with one live arm is not a safe default** — the old wording read "participation unless
there is payment evidence", and since the corpus carries no payment data at all, the exception arm had
an empty set to fire on while still inviting somebody to implement it.

**Four consequences that arrive with the memberships.**

- **The root-participation obligation points at the import again.** Round 8 corrected that section to
  say an ordinary import "touches neither arm of this pair"; with memberships arriving by the thousand
  it does, in the same transaction, which is what keeps *who is in unit X* one query
  ([D-041](../decisions/round-02-03.md#d-041--belonging-to-a-sub-unit-is-a-participation-record-not-a-membership)).
- **No obligation, no payment, no balance.** An imported membership creates **no `fee_obligation`**,
  and that has to be a rule rather than an accident: an obligation per historical year would land as
  `unpaid` and turn a decade of members into a wall of debt with a 1999 `due_date` for the lapse sweep
  to choke on. Related, and now load-bearing rather than incidental: `outstanding_balance` is **null**
  on these rows — a zero would be a claim of *settled* that no export supports.
- **The person-level no-overlap rule is back in the import's path.** Round 8's tidy sentence — "with no
  imported membership there is nothing for it to violate"
  ([05-membership-lifecycle.md §3](05-membership-lifecycle.md#3-membership)) — is gone with the premise
  under it. One row per period the source states, not one per calendar year, is now a rule with a
  consequence rather than a tidiness.
- **These rows are the oldest layer of the skeleton D-088 keeps forever**
  ([D-088](../decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)):
  thousands of named people with birth dates who were never asked and never used the system, held on
  an unverified legal basis. Same judgement as before, much larger population.

**What this makes true about reports.** Every cross-decade member count is now a mixture of an export
and a register, distinguished only by `data_confidence` and `import_batch_id`. A membership-rate chart
spanning the import boundary compares a source that *states* membership with a system that *records*
it, and nothing in the query knows the difference.

**A historical membership is also obtainable as a human act, and that route did not go away — it
changed what it is for.** Where the organization has a period the export does not state (a ledger
found later, a written confirmation, a person who was a member in a year the file lost), the period is
entered by hand under `membership.backdate`
([../appendix/permission-catalog.md §4](../appendix/permission-catalog.md#4-membership)). Under the old
rule this was the *only* way to get a historical membership at all; under D-093 the pipeline carries
the stated ones and this remains the route for the unstated, still deliberate, still attributed, still
outside the batch.

**End dates are still often unknown, and this is now the sharpest case of it.** A period the export
leaves open — someone last seen in a 2003 row with no end stated — cannot be written open: that is the
one shape D-093 refuses outright, and an unbounded historical record is the same hazard wearing a
different name. Convention, unchanged from before the corpus was known: **end it at the end of the
school/organizational year of the last row they appear in, marked as inferred.** That remains the *only*
date the import infers — the periods themselves are now stated rather than inferred — and it is
precisely what the organizational year boundary is needed for, which is still open
([A-4](../open-questions.md#a-4-remainder--the-organizational-calendar)) and, with attendance and no
money in the corpus, is the sharpest remaining import question. Document the rule you choose; it will
be questioned.

---

## 8. The returning-member case

The scenario you described — member 1990–2010, returns 2024 — should be the *smooth* path,
because it is a common and important one (returning alumni become adult leaders and donors).

Flow:

1. Person registers in 2024, self-asserting past membership.
2. The system matches them against legacy rows and proposes hypotheses.
3. A registrar reviews and confirms.
4. The historical membership (1990–2010) and the current membership (2024–present) now sit
   under one `person` row.
5. Their profile shows their full history; the gap is explicit data.
6. Any seniority or "years of service" calculation reads across both.

**Step 4 is two `membership` rows, and one round ago this document said the opposite.** It then held
that what the import holds for 1990–2010 is `unit_participation`, so the profile read as twelve years
of participation plus a membership from 2024 — "the truth of what the organization can evidence", with
a historical membership appearing only if somebody typed one. That was true of a corpus of roster
rows. The corpus is a **membership export**, which states the period, so the twelve years arrive as a
bounded membership row, and one row only:
[D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row) deleted the
root-unit participation row it used to be written beside in one transaction, so the pair this sentence
described is now a single row
([D-093](../decisions/round-09.md#d-093--the-one-off-import-may-create-memberships-both-ends-dated));
what the sentence is still refusing is the *inference*, and the assertion that survives unchanged is
the one that matters for this case: **a 1990–2010 `membership` appears only where the source states the
period or somebody records it by hand on evidence** (`membership.backdate`, §7). Note what did not
survive, because it is the part a reader will otherwise rely on: the smooth path now restores a
person's member history without a human typing it, which is what round 8's rule existed to prevent.
What makes it safe now, and only now, is that the source **states** the period instead of the import
guessing one.

Steps 2–3 can be streamlined when the match is strong (exact old membership number), but
the confirmation step remains, for the reason in §3.

**One thing D-089 changed about this path, and it is a cost rather than a clarification.** The
activation gate does not distinguish why a hypothesis exists: an account may not reach `active` while
an unresolved hypothesis *names its person*, and a self-asserted claim names that person exactly as a
collision does. So the smooth path now has a human between registration and login, where before the
review happened after the person was already using the system. The mitigation is the same one the
collision case gets — the age check that alerts (§4) — plus the fact that with a legacy number in hand
step 2 is a lookup a registrar settles in seconds. What is *not* settled is whether a hypothesis the
person raised about themselves should hold their account out of `active` at all, as against a
hypothesis the system raised about a stranger who happened to match. Recorded in §9.

### Self-service without weakening the guarantee

Rather than auto-linking, give the person a **claim** flow: they assert a past membership,
staff confirm. Record the assertion on the hypothesis row, so that if the claim later
proves false, you can see it was self-asserted rather than discovered.

---

## 9. Open issues

Still open:

- Whether twins/siblings with similar names and the same birth date need a documented
  disambiguation procedure (recommend: yes, and never merge them automatically). The sign-up gate in
  §4 sharpens this rather than softening it: same birth date plus a normalised name is exactly the
  collision pair, and a collision now stops a registration instead of merely queueing a card for
  somebody else to settle later.
- Whether a hypothesis a person raised about *themselves* should hold their account out of `active`,
  as against one the system raised because a stranger's sign-up strong-matched them (§8). D-089
  decided the second case, and its wording covers both.
- The organizational year boundary that historical end dates get inferred from
  ([A-4](../open-questions.md#a-4-remainder--the-organizational-calendar)). With stated membership
  periods, attendance, and no money (§7) this is load-bearing by itself rather than one of several open
  import questions — and since D-093 the inferred date now closes a `membership` row rather than only a
  participation row, so the number of rows it touches went up, not down.

**Resolved, kept visible so the reasoning survives:**

- Volume and formats of historical data — thousands of rows in **two** exports, people and events,
  1990s to now, free-text columns alongside
  ([B-1](../open-questions.md#b-1--closed--thousands-of-roster-rows-numbers-present-no-payment-data),
  [D-090](../decisions/round-07-08.md#d-090--the-legacy-corpus-is-thousands-of-roster-rows-with-numbers-and-no-money),
  [D-092](../decisions/round-09.md#d-092--the-corpus-is-people-and-events-and-it-names-no-units)).
  "One export" is what this bullet said until round 9; the correction is only about shape, and the
  answers it produced stand. This section used to ask the question in order to decide whether manual
  review was affordable and to hold open a high-confidence auto-merge tier; the corpus is modest and
  number-bearing, so the tier is not needed and is not reserved (§4).
- Whether the old system issued member numbers — **it did**, on most rows: imported verbatim into
  `person_identifier` under the legacy scheme and never reissued
  ([D-056](../decisions/round-04.md#d-056--the-legacy-import-expects-a-large-corpus-with-legacy-member-numbers),
  D-090). §4's strongest signal is available, and where a number is present the match is a lookup
  rather than a score.
- **How much of an old roster becomes a membership** — this round's answer is "the periods the export
  states" (§7), and it is the reversal of the previous one, which was *none of it*: the question was
  "how much", the corpus carried no payment evidence, and so the arm of the old rule that produced
  memberships could not be reached
  ([D-041](../decisions/round-02-03.md#d-041--belonging-to-a-sub-unit-is-a-participation-record-not-a-membership)).
  [D-093](../decisions/round-09.md#d-093--the-one-off-import-may-create-memberships-both-ends-dated)
  reached the same conclusion by a different road — the source states a membership period directly, so
  no payment evidence was ever the only way in — and left the old rule's *purpose* intact as the ban
  described in §7. The stakes this section named are why that ban is shaped as it is: an inferred
  membership running to today would make a 2003 roster member a current member under the permission gate
  ([D-039](../decisions/round-02-03.md#d-039--member-permissions-require-a-current-paid-membership)),
  which is exactly what a period with both ends dated cannot do.
- Retention — both the erasure *mechanism* (redact the person, keep the financial and membership
  skeleton) and the durations: that skeleton indefinitely as the organization's own history, audit
  payloads emptied 24 months after writing ([D-088](../decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)).
  The half that stays open is not a design question — whether indefinite retention of named membership
  and fee rows has a legal basis, which a decision log cannot grant
  ([B-3](../open-questions.md#b-3--closed--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)).

Section B of the register — identity and history — is closed in full. §7's shape is registered in the
organization section rather than here: [C-5](../open-questions.md#c-5--closed--the-corpus-names-no-units-and-none-are-assigned)
closed the question of whether the corpus names units, and what it closed leaves the unit-level question
in §7's "where it hurts" column with no system answer to give. All tracked in
[../open-questions.md](../open-questions.md).
