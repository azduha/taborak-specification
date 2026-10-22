# Identity Resolution and Legacy Data

How the system decides that two records describe the same human, and how four decades
of paper and spreadsheet history gets brought in without corrupting live data.

This is the highest-risk area of the project. Get it wrong and either the history is
unusable, or worse, two people's records get merged and you leak one member's data to
another. The design below is deliberately conservative.

---

## 1. Why this is hard

A 1994 roster has: a name, maybe a birth date, an address, a unit, and a year. No email,
no unique key, no way to log in. Meanwhile:

- Names change (marriage, adoption, correction of a misspelling).
- Names repeat. In a youth organization spanning decades, "Jan Novák" is many people.
- Diacritics and transliterations vary across decades of manual entry (`Novák` / `Novak`).
- Birth dates are often wrong by a digit, or recorded as year-only.
- The same human appears in multiple rosters under slightly different spellings.

So: **automatic matching will produce both false positives and false negatives.**
False positive (two people merged) is a privacy incident. False negative (one person
split) is a data-quality annoyance. The design must therefore bias hard toward false
negatives — never merge on a guess.

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
says where the proposal came from — `import_job`, `system`, `person` or `staff` — and
`proposed_at` when. `reviewed_by`, `reviewed_at` and `review_note` are the human part, and a
hypothesis may not reach `confirmed` or `rejected` without a `reviewed_at`. At most one live
hypothesis exists per pair — live means `proposed`, `needs_review` or `confirmed`.

### Lifecycle

```
  matcher proposes ──> proposed ──┬── staff confirms ──> confirmed ──> [merge executed]
                                  ├── staff rejects  ──> rejected (the pair becomes
                                  │                       proposable again — see §4)
                                  └── person asserts ──> needs_review → staff confirms/rejects
```

Two entry points:

1. **Import or background matching** proposes hypotheses automatically at low confidence.
2. **A registering person asserts their own history** — "I was a member 1990–2010" — which
   creates a hypothesis against the candidate rows, usually with `proposed_by = 'person'`.

A person's own assertion is *evidence*, not proof. It must still be reviewed, because
claiming someone else's history is the obvious attack on an import-based system — and the
prize is that person's data. **Never auto-confirm a self-asserted link.**

---

## 4. Match signals

The matcher scores candidate pairs on independent signals. Recorded in `match_signals`
so a reviewer sees *why* the system proposed a match:

| Signal | Strength | Notes |
|--------|----------|-------|
| **Exact legacy member number** | **decisive** | The corpus carries these ([D-056](../decisions/decision-log.md#d-056--the-legacy-import-expects-a-large-corpus-with-legacy-member-numbers)). Same number, same person — matched, not scored. |
| Exact birth date + exact normalised name | strong | Still not automatic — twins with similar names exist. |
| Birth date within ±1 day or year-only match + name | moderate | Common with hand-written records. |
| Name match after normalisation (diacritics, case, spacing) | moderate | Necessary but weak alone; "Jan Novák" is not unique. |
| Same unit + overlapping membership period | moderate | Corroborating, not identifying. |
| Same postal address at the same time | moderate | Strong if the address is distinctive. Read from `person_contact` history — there is no household table ([D-057](../decisions/decision-log.md#d-057--household-is-removed)). |
| Guardian name match | weak | Useful for minors in old records. |
| Name-only fuzzy match | **weak — never sufficient alone** | |

> **The decisive row changes the matcher's job.** With a number on the record, the question is
> not "are these two the same person?" but "does this number already point somewhere?" — a
> lookup. The scored signals below are then for the rows the number **cannot** resolve: legacy
> records predating the numbering, records where the number is illegible, and people who were
> never issued one. At thousands of rows ([D-056](../decisions/decision-log.md#d-056--the-legacy-import-expects-a-large-corpus-with-legacy-member-numbers))
> this split is what makes [D-004](../decisions/decision-log.md#d-004--no-automatic-merging-ever)
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
  worse than any amount of manual review, and merges are irreversible in practice.

*Assumption:* you want **no automatic merging at all**, even for near-certain matches.
If the volume of historical data makes that infeasible, an explicit opt-in auto-merge
tier can be added — but it should be a deliberate decision, recorded in the decision log.

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
| `person_name` | Reassigned, keeping validity periods — this is how a maiden name survives. |
| `account` | Reassigned to survivor. **If the survivor already has an account, the absorbed account is closed, not deleted.** |
| `membership` | Reassigned. Overlapping periods flagged for review — with one type (D-037) and a person-level no-overlap rulet, an overlap here means a bad merge. |
| `unit_participation` | Reassigned, with the same overlap check. |
| `guardianship` (as dependent) | Reassigned. |
| `guardianship` (as guardian) | Reassigned. |
| `role_assignment`, `access_grant` | Reassigned. **Union of permissions results — this is the security-critical step.** |
| `person_merge` | Row inserted here. |
| `field_conflict` | Populated for anything that could not be resolved automatically. |

### What does *not* happen

- Nothing is deleted. The absorbed `person` row keeps its id and gains
  `merged_into_person_id`. All historical foreign keys pointing at it still resolve,
  so "who was in Troop 12 in 1998" keeps working.
- Overlapping memberships are **never silently deduplicated**. Two overlapping child
  memberships after a merge is suspicious — it may mean the merge was wrong. It becomes
  a review item.

### The security rule that must not be skipped

Merging unions the two people's permissions. If a bad merge is performed, the survivor
gains the absorbed person's access. Therefore:

1. A merge is always performed by a human with `person.merge` permission.
2. The merged result's **effective permissions are re-displayed for confirmation** before
   the merge commits.
3. Every merge is reversible via `person_merge` in the sense that the assignment can be
   moved back — but `access_grant` rows created during the merged period cannot be
   attributed. Hence rule 2.
4. Merges invalidate cached permissions. See
   [06-authorization-model.md](06-authorization-model.md#8-caching-and-invalidation).

---

## 6. Reversing a merge

Support **unmerge**, because mistakes will happen. It is not symmetric — you cannot know
which grants were exercised while merged — but you can restore the row split:

1. Clear `person.merged_into_person_id` on the absorbed row. The tombstone comes off.
2. Reassign rows **created before** `merged_at` back to the absorbed person.
3. Flag rows **created after** `merged_at` for human review. Those are the ambiguous ones, and
   they are reviewed rather than split by a rule.
4. Record the unmerge on the `person_merge` row, as `reversed_at` and `reversed_by`.

The `access_grant` rows are the specific hazard. Any grant created *during* the merged
window might belong to either human. Flag every one of them; do not guess.

---

## 7. Legacy import pipeline

Staged, reviewed, idempotent. Never a direct write into live tables.

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
  [5] apply                   ── writes person / membership / unit_participation
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
  person, the import may *add* historical memberships but never alters names, contacts,
  or identifiers the person maintains themselves.
- **Preserves provenance.** Every imported row records `import_batch_id` and
  `source_reference` (file + line), so any value can be traced back to the paper it came
  from. When someone disputes a historical record, you can show them where it came from.
- **Records uncertainty rather than guessing.** A row that cannot be parsed cleanly goes
  to the review queue with the raw value intact — it does not get a best-effort guess
  written as if it were fact.

### Historical memberships from imports

An imported roster row typically yields:

- a `person` with `record_origin = 'legacy_import'`
- a `membership` with `valid_from` = roster year start, `valid_to` = roster year end (or
  null if it was the last known roster and the member's status is unknown)
- a `unit_participation` row linking them to the historical unit
- `data_confidence = 'low'` on all of the above

**What a 1998 roster actually tells you is participation, not membership.** This is the
one place the membership/participation split ([D-041](../decisions/decision-log.md#d-041--belonging-to-a-sub-unit-is-a-participation-record-not-a-membership))
really bites on legacy data, and it is worth being deliberate about rather than generating
both rows by reflex:

| The old record says | It becomes | Confidence |
|---|---|---|
| "was in Pack 12 in 1998" | `unit_participation`, 1998-01-01 → 1998-12-31 | Reasonable — the roster is decent evidence of this |
| "was a member in 1998" (a membership list, or a fee ledger) | `membership` | Good — a payment record is strong evidence |
| "was in Pack 12 in 1998" with no fee evidence | `unit_participation` **and** a `membership` marked `data_confidence = 'low'` | Weak — this is an **inference**, and the discussion below applies |

The temptation is to generate a membership for every roster row, because that is what the
old data model implied. **Do it, but mark it as inferred**, because
`is_current_member()` and the permission gate ([D-039](../decisions/decision-log.md#d-039--member-permissions-require-a-current-paid-membership))
both read `membership`, and an inferred membership from 1998 is harmless while an inferred
membership row that runs to `valid_to IS NULL` would make someone a member today. The
**no-overlap rule** makes this concrete, whatever ends up enforcing it: a person-level "one open
membership" rule means
the import must **not** leave an open membership for someone whose only evidence is a
roster.

**End dates are often unknown.** For an imported member last seen in a 2003 roster, the
membership should end at a defensible date — not left open, which would falsely make them
a current member, and not guessed. Convention: end at the end of the school/organizational
year of the last roster they appear in, marked as inferred. The participation row can be
bounded the same way. Document the rule you choose; it will be questioned.

---

## 8. The returning-member case

The scenario you described — member 1990–2010, returns 2024 — should be the *smooth* path,
because it is a common and important one (returning alumni become adult leaders and donors).

Flow:

1. Person registers in 2024, self-asserting past membership.
2. The system matches them against legacy rows and proposes hypotheses.
3. A registrar reviews and confirms.
4. The person's two memberships (1990–2010, 2024–present) now sit under one `person` row.
5. Their profile shows their full history; the gap is explicit data.
6. Any seniority or "years of service" calculation reads across both.

Steps 2–3 can be streamlined when the match is strong (exact old membership number), but
the confirmation step remains, for the reason in §3.

### Self-service without weakening the guarantee

Rather than auto-linking, give the person a **claim** flow: they assert a past membership,
staff confirm. Record the assertion on the hypothesis row, so that if the claim later
proves false, you can see it was self-asserted rather than discovered.

---

## 9. Open issues

- Volume and formats of historical data — determines whether manual review of every match
  is feasible, or whether a high-confidence tier is needed.
- Whether the old system issued member numbers (would make §4's strongest signal available).
- **How much of an old roster becomes a membership and how much becomes participation**
  (§7). This got harder when the two were split apart
  ([D-041](../decisions/decision-log.md#d-041--belonging-to-a-sub-unit-is-a-participation-record-not-a-membership)):
  the import must decide per record class, and an inferred membership running to today
  would make a 2003 roster member a current member under the permission gate.
- Retention periods for members who request erasure — the *shape* is settled (redact the
  person, keep the financial and membership skeleton), but the durations need legal input.
  See [../open-questions.md](../open-questions.md#b-3--erasure-the-policy-not-the-mechanism).
- Whether twins/siblings with similar names and the same birth date need a documented
  disambiguation procedure (recommend: yes, and never merge them automatically).

**Resolved and no longer open**, kept visible so the reasoning survives: the erasure
*mechanism* (redact the person, keep the financial and membership skeleton) — only the
retention durations remain open.

All tracked in [../open-questions.md](../open-questions.md).
