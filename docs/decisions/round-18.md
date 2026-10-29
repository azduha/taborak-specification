# Decision Log — Refinement round 18 (D-127 … D-132)

> A round is closed by a script now, not by a reader who happened to look; one page answers who enforces each invariant; a reason is something somebody typed; and a name that other rows are written against may not be renamed.

[Refinement round 17 (D-125 … D-126) ←](round-17.md) | [All decisions](index.md)

**What was asked.** [F-10](../open-questions.md#f-10) was the last item on the "answer next" list that no
answer could settle, because it is not one question. It asks, of every invariant in this schema, *which
layer carries it* — and it had been open for eleven rounds because the honest answer is per-rule, not
per-shape. Round 18 was scoped, when you picked it, to four things: make the registry diff an executable
that gates a round; answer F-10 per instance rather than per shape; decide what shape 4 actually contains;
and make a referenced `code` immutable by rule. Everything else on this page was found by doing those.

**What the round found, which is why it is longer than it was scoped to be.** The gate ran before the
answers were written, and the answers were written against what it said. Its first report was 281 findings;
its last is twenty. Nothing was silenced to get there: the difference is a rule set that stopped holding
opinions, where every exemption comes from a page in this corpus rather than a line in a script.
What those twenty are is recorded in `scripts/registry-baseline.txt` with a reason beside each. In the
course of writing the register that closes F-10, **eight places were found where this corpus disagreed
with itself** — a count that counted only what somebody had looked at, a check reading a column no table
has, a rule two pages stated and nothing enforced. Those eight are [D-129](#d-129--where-the-register-and-the-page-disagree-the-page-is-wrong),
and they are the round's real output: the gate is machinery, the disagreement was the defect.

**One decision on this page is not yet in the model.**
[D-132](#d-132--day-one-is-one-account-holding-systemadmin-and-every-role-after-it-is-written-by-the-organization)
was ruled here and is applied in round 19; it says so in its own status line, because a decided change
that the documents have not caught up with is exactly the state [D-129](#d-129--where-the-register-and-the-page-disagree-the-page-is-wrong)
exists to make visible.

---

## D-127 — The registry diff is a committed script, and it gates a round

**Status:** decided (from your answer, including that this repository stops being markdown-only)
**Date:** refinement round 18
**Amends:** [D-104](round-10b.md#d-104--a-permission-codes-last-segment-is-an-action-and-a-registry-that-prose-contradicts-is-a-fiction)'s
machinery — what it adopted was "a hand-run diff report", which is a habit, and habits do not survive a
round that finds nothing. **Enables:** [F-10's closure](#d-130--one-register-answers-who-enforces-an-invariant-and-f-10-closes)
rests on it, because a register of 69 rows is a claim about 20 pages. **Costs this repository:** its first
file that is not markdown (`scripts/check-registries.py`, plus `scripts/registry-baseline.txt`).

**Decision. Four parts.**

1. **The diff is `scripts/check-registries.py`, committed.** Python, no dependencies, reads markdown and
   nothing else, writes nothing except with `--update-baseline`. It exits non-zero on a finding that is not
   in the baseline, so "the round is finished" is a thing a reader can be shown rather than a thing the
   writer says.
2. **The registries are the documents, never a list beside them.** Each register the script reads is a
   section of a page that already holds it: the catalog's code rows (70), catalog-b §10's deferred
   namespaces (19) and §9's headings, which declare a whole namespace absent,
   [removed-concepts.md](../appendix/removed-concepts.md)'s first column (24 dead names), 05a's selector
   registry (13), 05's `grant_scope_type` seed (5), and
   [00 §7a](../data-model/00-conventions.md#7a-what-an-empty-actor-column-means)'s label table (5). Three of
   those counts are stated in prose elsewhere — thirteen selectors, five labels, five scope types — and the
   script reads thirteen, five and five out of the tables, which is the only agreement between the
   documents and the script that means anything. **A vocabulary §11 calls seeded and no page enumerates is
   reported rather than skipped**, and the claim of which vocabularies are seeded is read from §11 on every
   run: that is how `reason_code` was reported all round and why the finding disappeared by itself when
   [D-128](#d-128--a-reason-is-text-the-reason_code-table-is-deleted) deleted the table.
3. **A register that stops parsing is a finding, not an empty set.** `no-registry` is the loudest kind the
   script emits, because an unparsed registry makes every token in the corpus a finding for about one
   second and then, once silenced, no finding at all — which is the failure mode worth spending a finding
   kind on.
4. **A round is not closed while a finding is unbaselined.** The baseline is a file, not a setting:
   every line is a finding somebody read and decided to keep, and **the text after the `#` is the record of
   why**. Two kinds of thing live in it now. Five names the corpus uses *in order to refuse them* —
   `person.admin`, `event.admin`, `event.answers.view`, `membership.manage`, `GUARDIANS` — where the fix the
   script wants would delete the refusal. And ten registered permission codes that no page names outside
   the catalog, which the finding correctly calls a question rather than a defect, and which were each
   asked and answered.

**Why "code-shaped" is a rule the corpus already had.** Most dotted tokens in these files are
`table.column`, and treating them as codes produced the first run's four hundred-odd noise findings. The
script does not decide what a code looks like; it reads the catalog's own §1 grammar back at the prose —
a code's last segment is an act, its first segment names stored state, and both vocabularies come from the
registered codes. So an invented act is caught *by the registry's vocabulary*, not by a guess about
English, and a column named `person.contact` is a column because a `**Fields** (`person`)` block says so.
An ALL-CAPS word counts as an operand only inside a backtick span containing an expression operator, since
in these files the same shape also carries SQL keywords, column types and one group's name.

**What the first run actually found, since a gate nobody believes is decoration.** Two names prose used
as if they were granted. `membership.manage` was the example of a save-time refusal in five places — three
of which were refusing to save a grant of a code that has never existed, which refuses nothing — and
catalog-b §12 had *already asked* for it to be re-pointed at `membership.terminate` and had been left
open; the diff is what closed it. `person.address.edit` was named twice, in 05 and 05c, for an edit whose
real code is `person.contact.edit`. Both are fixed here. It also found that `decisions/` must be exempt
outright, that the corpus's own §9 and §10 are the right source for the namespaces that are absent or
deferred on purpose, and that **a finding's identity must not contain a line number**, or moving a
sentence re-opens a finding somebody already read.

**What it cannot see, stated because a gate that overstates itself is worse than none.**

- **A name that is nowhere.** A word the prose never uses cannot be missing from it; this checks prose
  against registries and registries for readers, not for coverage of the world.
- **Both sides wrong at once**, which is the failure D-104 recorded five times and the one this script is
  weakest against: if a registry row and the sentence quoting it were invented together, the diff is
  green. `GUARDIANS` was exactly that — a name in six pages *and* a row that should never have been minted.
- **Whether a write path still contains its rule.** This repository has no code, so 43 of the register's
  69 rows rest on it. That limit is not new and is not this script's to close; it is why
  [00a](../data-model/00a-invariant-register.md) says so in its own last section.

**What it costs, stated as costs.** A script is a second thing to maintain, and its registers are the
sections it parses, so a page that renames "The selector registry" produces a `no-registry` finding rather
than a silently narrower check. The baseline can hide things, which is why a line without a reason after
the `#` is a defect in the baseline itself. And there is no CI: this repository has no build step, so the
gate runs when somebody runs it, and what changed is that *finishing a round* now means running it.

---

## D-128 — A reason is text; the `reason_code` table is deleted

**Status:** decided (from your answer — "write it as a string everywhere")
**Date:** refinement round 18
**Deletes:** the `reason_code` table and the claim that its contents are a seeded vocabulary.
**Renames:** `status_reason_code`, `rejection_reason_code`, `termination_reason_code` and
`ended_reason_code` to `status_reason`, `rejection_reason`, `termination_reason` and `ended_reason` —
[01a §2](../data-model/01a-accounts-and-contacts.md#4-account), [01 §3](../data-model/01-identity.md#3-person_name--name-history),
[03 §4 and §6](../data-model/03-membership.md), [04 §1](../data-model/04-relationships.md#1-guardianship),
and the naming row in [00 §2](../data-model/00-conventions.md#2-naming). **Amends:**
[erd-b's reference vocabularies](../appendix/erd-b-inventory.md), five down to four.
**Reverses:** nothing — the table had no decision entry of its own, which is the second half of why it went.

**Decision.** Every `<verb>_reason` is a text column, required where the act needs a why and free text
where it does, and **a value somebody types rather than a row of a table**. `08-events` already made this
argument for `organizer_role` and cited [D-095](round-09.md#d-095--units-carry-no-restrictions-joining-one-is-somebody-elses-act)
for refusing a closed list of reason codes; round 18 applies the refusal corpus-wide instead of in one
column. Where a reason is also a permission question the answer is unchanged: a rejection requires a
reason ([03 §4](../data-model/03-membership.md)), a termination records one, and *what the words were* is
audited, not *which bucket they came from*.

**Why this was the right shape rather than the cheap one.** The table was the corpus's only
`no-registry` vocabulary: [00 §10](../data-model/00-conventions.md#10-migration-discipline) promised it
as seed data and **no page anywhere enumerated a row of it**. A vocabulary that nobody lists cannot be
granted, cannot be checked, and cannot be translated — it can only be copied by an implementation that
has to guess, which is how environments disagree. The second reason is the design's own: a reason code
becomes a statistic, and a statistic somebody maintains by hand is a report that silently under-counts
every reason that was typed differently. Free text is counted only when people happen to write the same
words, and [05's note on why a grant has no reason column](../data-model/05-authorization.md#2-permission)
now says exactly that rather than implying a tidy vocabulary was waiting somewhere.

**What it costs, stated as costs.** **No grouping without a vocabulary**: "why do memberships end?" is a
text search, and the answer will be a list of near-duplicates rather than a bar chart. Four renames across
five tables are a migration, and a rename is the one change
[00 §10](../data-model/00-conventions.md#10-migration-discipline) treats a rename as a data migration rather than
a schema one. And one sentence stays deliberately stale: [02 §1's "Not present" table](../data-model/02-organization.md#1-person_group)
still names `join_reason_code` and `closed_reason_code`, because those are columns this design refuses
outright and never had under either spelling — the argument for their absence is about the *absence*, not
the suffix.

---

## D-129 — Where the register and the page disagree, the page is wrong

**Status:** decided (needed in order to write [D-130](#d-130--one-register-answers-who-enforces-an-invariant-and-f-10-closes),
and then used eight times in one pass)
**Date:** refinement round 18
**States once:** as consequence 4 of [00 §6a](../data-model/00-conventions.md#6a-who-enforces-an-invariant-now);
everywhere else it is applied, not restated.
**Direction, not a new rule:** this is [D-104](round-10b.md#d-104--a-permission-codes-last-segment-is-an-action-and-a-registry-that-prose-contradicts-is-a-fiction)'s
"prose contradicts a registry" moved from names to claims. **Reverses nothing.**

**Decision. Two halves, and the second is the load-bearing one.**

1. **[00a](../data-model/00a-invariant-register.md) holds no rule.** Every row links to the page that owns
   the rule and adds only the three facts that page is allowed to leave implicit: which layer carries it,
   which report would see a breach, what a breach looks like. **Where a register row and the page it cites
   disagree, the page is wrong** and is edited in the round that noticed; the register row is never softened
   to match a page's error, because a register that restates rules is a fourth copy of them and this corpus
   keeps getting copies wrong.
2. **A register row is a claim about a page and is verified against it, never asserted.** Every quotation
   in the register was grepped out of the file it cites before it was written down. This is not a style
   rule. Two of the eight disagreements below were found by an agent's report that was confidently wrong,
   one "correction" of an earlier draft arrived with a sentence and a line number that did not exist, and
   **a register whose rows are remembered rather than re-derived decays into the thing it replaced** — a
   page that says who enforces a rule, with the same authority and less evidence.

**The eight, in the order they were found.** Each was a place where two documents disagreed, not a place
where one document was silent.

| What the corpus said | What the other page said | What changed |
|---|---|---|
| [00 §9](../data-model/00-conventions.md#9-referential-integrity-rules): "exactly **two** reference-less keys" | Five more polymorphic columns are read by no orphan scan at all — `access_log.scope_id`, `.authorization_ref_id`, `.entity_id`, `field_conflict.entity_id`, `audit_log.record_id` | The row says **two validated, five not**, and names all five. The old count was the count of the ones somebody looked at; the five are [F-30](../open-questions.md#f-30) |
| [05d §11](../data-model/05d-invariants-and-seed.md#11-invariants-to-verify) check on group names, reading `person_group.code` | `person_group` has no `code`; §1's naming rule refuses one, and the section's own head promises no check reads a column the schema lacks | The check reads `person_group.name` |
| [05e §14](../data-model/05e-keys-and-callers.md#14-api_key--a-caller-that-is-nobody)'s layer row: `secret_hash` unique among live rows | The same page's §17 report needs `code` unique too, or two keys share a name and the trail of who called is ambiguous | The row names **both** columns |
| [01 §3](../data-model/01-identity.md#3-person_name--name-history)'s name table: an ordering rule only | [01b §10](../data-model/01b-merges-views-and-checks.md#10-integrity-checks) needed a "current name" to check against, which requires at most one `person_name` row per `(person, name_type)` with `valid_to` absent | The rule is stated where the table is, which is where the write path reads it from |
| [00 §6a](../data-model/00-conventions.md#6a-who-enforces-an-invariant-now)'s consequence 2, exemplified by "one live exposure per unit and assignment" | `scope_exposure` was deleted by [D-097](round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row) | The example is now `access_grant`'s one live allow per grantee, scope and permission — the partial index that is still there |
| the same paragraph, promising a report "where uniqueness is decided by data" | no page contained such a report, in any round | [01b §10](../data-model/01b-merges-views-and-checks.md#10-integrity-checks) gains the duplicate-identifier count the paragraph had promised since it was written |
| [04 §1](../data-model/04-relationships.md#1-guardianship): one guardianship per pair, "enforced by the write path" | every other shape-1 rule in the corpus names a hand-written exclusion constraint, and shape 1's layer row in 00a says the write path is never the answer | A hand-written exclusion constraint over **all** rows, plus 04 §6 check 7 appended |
| [03 §4](../data-model/03-membership.md): the circular pair is broken with an optional column | [00 §9](../data-model/00-conventions.md#9-referential-integrity-rules) is the rule that says so, and the page did not cite it, so the choice read as local | The row cites it |

**Why the tie-break points that way and not the other.** The alternative — the register is the summary and
the page is the detail, so a conflict means the summary is stale — is normally right and is wrong here,
because the register's three columns are *exactly* the things a page states once, in passing, three
sections away from where the enforcement is decided. It is a lookup, and a lookup that has to be believed
more than the page it points at has stopped being a lookup.

---

## D-130 — One register answers who enforces an invariant, and F-10 closes

**Status:** decided
**Date:** refinement round 18
**Closes:** [F-10](../open-questions.md#f-10), open since round 3 and last argued in round 10.
**Adds:** [data-model/00a](../data-model/00a-invariant-register.md), one page, 69 rows.
**Amends:** [00 §6a](../data-model/00-conventions.md#6a-who-enforces-an-invariant-now), which stops
answering "which layer for which rule" by example and points at the register instead.
**Adds questions:** [F-28](../open-questions.md#f-28)–[F-31](../open-questions.md#f-31), which are the
register's blanks, kept as questions because a blank filled with an invented check is worse than a blank.

**F-10's answer, in one line per shape, and then the part that is not one line.** Shape 1 is a
hand-written PostgreSQL exclusion constraint emitted by a migration. Shape 2 is a partial unique index,
where the predicate *is* the rule. Shape 3 is the write path, inside the transaction. Shape 4 is
[D-131](#d-131--shape-4-is-not-empty-and-a-code-that-is-referenced-may-not-be-renamed). That half was
already the recommendation in §6a and was never the hard part; **the hard part was that "shape 3 is the
write path" answers a question nobody was asking**, because every reader wants to know about *their* rule.
So the decision is not the four lines, it is the 69 rows: **4 shape 1, 15 shape 2, 43 shape 3, 7 in
shape 4's section**, each naming the page that owns the rule, the layer, the report that would notice, and
what a breach looks like afterwards.

**Why the answer is a page and not a decision entry.** A migration is written by somebody reading one
data-model page at a time, and the question "is this rule guarded?" arises at the row, not at the summary.
An answer that lives in a decision log is invisible at exactly the moment it is needed, which is how F-10
stayed open for eleven rounds while its four shapes were cited by name from every module of the data model.

**What listing them found, which is why the listing is the decision.**

- **Eleven of the 69 rows name no report at all, and every one of them is a shape-3 row.** That is the
  finding, and its shape is the argument: a shape-1 or shape-2 rule with no backstop still sits under a
  constraint, which is the strong case, while **a shape-3 rule with no report is a rule whose only
  enforcement is a line of code and whose only evidence is silence.** Eleven is a number the corpus did not
  have before this round, and one of them — per-scheme identifier uniqueness, which §6a's own sentence has
  promised a report for since round 6 — is the row round 18 filled.
- **Two modules have no check list at all.** [07-finance.md](../data-model/07-finance.md) and
  [06a-import.md](../data-model/06a-import.md) state rules and carry no "Invariants to verify" section, so
  every rule they state is unassigned **by construction rather than by oversight** — which is where most of
  the nineteen live, and is [F-31](../open-questions.md#f-31).
- **Nine numbered checks are assertions about the code, not reports over data** — the six `TIME-BOMB`
  checks of 05d §11 (15, 16, 17, 18, 19, 22), 02 §6 check 4, and 08a §10 checks 1 and 9. They verify that a
  guard still exists; they never verify that the data is clean, and a check whose result is "evidence about
  the code" was being cited as a backstop before anyone counted. **Filing one as a backstop overstates
  coverage in exactly the direction that matters**, so 00a cites them as `save-refusal` and never as a
  report — which is also why this register's coverage claims are narrower than a reader might expect.
- **A report beneath a real constraint is a courtesy, not a control.** Most of the nineteen are already
  caught below the application, and saying so is the difference between a register and a list of worries.

**What closing F-10 cost, honestly.** F-10's page described "four shapes, each appearing dozens of times"
and named about fifteen instances between its bullets. Listing them took an inventory of every **Rules** block and every
**Invariants to verify** section in 21 data-model pages — nine pages have such a section — and came back
with 69 rows, nine checks that were assertions, and eleven blanks. **The count, not the colour, is what was wrong about the question.**
And the page has a maintenance obligation that the decision cannot discharge: its rows are quotations of
other pages, its value decays the moment those pages move, and the registry diff cannot see any of it —
`check-registries.py` checks names, not claims. Re-deriving the rows belongs to any round that changes
which layer carries something.

---

## D-131 — Shape 4 is not empty, and a code that is referenced may not be renamed

**Status:** decided (found by writing the register, in the section F-10 had called empty)
**Date:** refinement round 18
**Corrects:** the candidate list [F-10](../open-questions.md#f-10) carried, which named two members and got
one of them wrong in each direction.
**States:** in [00a §4](../data-model/00a-invariant-register.md#4-a-value-that-may-never-change-once-set),
and in the three pages that own the three values. **Reverses nothing** — it declines a shape-4 membership
that was never granted.

**The test, taken from the deleted instance rather than invented.** `org_unit.parent_unit_id` was shape
4's only member and died with the hierarchy
([D-036](round-02-03.md#d-036--units-cannot-be-reparented-a-unit-that-moves-is-a-new-unit) reversed by
[D-097](round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)), which left the shape
"currently empty" on the strength of one column. The reason a reparent was shape 4 at all is the test:
**every row stays individually valid while the meaning of what references it moves under it, and nothing
left behind is a row a report could find.** Run that test against the corpus and the shape has six
members, four of which were already stated somewhere and two of which nobody had thought to ask.

| The value | A rename rewrites | Verdict |
|---|---|---|
| `permission.code` | every `access_grant` row, which holds the code **by value**, and every role definition listing it | **immutable**, and the catalog's own "adding one is free, renaming one is a migration" was a wish with no rule behind it |
| `selector_type.code` | every stored expression, through `selector_kind` | **immutable**, and the truest instance in the shape: it is the word the language is written in, and F-10 did not carry it |
| `api_key.code` | the grants issued to it, the audit rows, and the report of who called | **immutable**, for the reason 05e §17 already needed the uniqueness for |
| `person_group_member`'s `group_id`/`person_id`, an imported bank transaction, `person.merged_into_person_id` | their own meaning; each page already forbids the edit | immutable, already stated, now in the register |
| `audience.code` | **nothing** | **not immutable, and this is the correction** |

**Why an audience's code is not in the shape, which is the part that was wrong rather than missing.**
`AUDIENCE(code)` is resolved **once, at save**, into `selector_arg_id` on the leaf
([05b §5](../data-model/05b-expression-tree.md)); the stored tree holds the audience's identity, not its
name, so "renaming the audience afterwards rewrites nothing" — which is not a discovery about immutability
but rule 5 of the name namespace, stated out loud on the page that owns it, being contradicted by a
candidate list eleven rounds old. **F-10's shape-4 candidate was the defect D-129 is about**, wearing a
question entry's clothes. `audience.code` keeps its partial unique index (one code per audience, among the
ones that have a code — shape 2) and loses its claim to immutability, and a rename of a named audience is
an ordinary audited edit.

**What carries the rule, and what that is worth.** Not a trigger. **The referrer listing that
[D-103](round-10b.md#d-103--an-audience-may-name-another-audience) already requires before an audience may
be renamed, extended to the three codes**: the editor shows, before it lets the name change, every grant
holding that permission code, every expression using that selector, every grant and audit row naming that
key. Behind it, the prose that was always the real rule — [00 §10's](../data-model/00-conventions.md#10-migration-discipline)
prohibition on rewriting a historical row's meaning — and in front of it, **the retirement path, which is
the only sanctioned rename: mint the new code, migrate the grants, end the old row, and let both appear in
the trail.**

**The honest limit.** The listing reaches rows, not sentences. A renamed `permission.code` also rewrites
every page that named it, and no query lists prose — that is
[D-127](#d-127--the-registry-diff-is-a-committed-script-and-it-gates-a-round)'s half, and the two
half-diffs together are the whole guarantee, which is weaker than a constraint and is what D-072 traded
away on purpose. `00a`'s shape-4 rows carry the word `nothing` in their layer column and this entry is
where `nothing` is explained rather than apologised for.

---

## D-132 — Day one is one account holding `system.admin`, and every role after it is written by the organization

**Status:** decided (from your answer) — **not yet applied.** The seed is still described in
[05d §12](../data-model/05d-invariants-and-seed.md#12-what-the-organization-starts-with), and the sweep
that removes it is round 19. It is recorded here because it was ruled here, and because a ruling that
lives only in a conversation is a ruling that gets re-litigated.
**Deletes (in round 19):** the seeded roles, the two seeded audiences, the seeded `event.answer.view`
grant, the worked-example offices that 05d §12 presents as seed, `role.is_system` and `audience.is_system`.
**Confirms:** `permission`, `grant_scope_type` and `selector_type` **do** ship as seed data.
**Reverses:** [D-068](round-05.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle)'s
habit of shipping a starter bundle — not its rule, which stands and is the reason this is affordable.

**Decision. Four parts.**

1. **Day one is one account holding `system.admin`, and nothing else.** No role, no audience, no grant.
   The person who sets the system up holds the only capability that ships, and every authority after that
   is a role they write, aimed at an audience they wrote, granted with codes from the catalog. **The
   requirement was one system administrator, and they will set everything up** — which is the same position
   [D-068](round-05.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle) already
   takes about per-resource admin codes: the bundle is not the design's job.
2. **Three vocabularies still ship**: `permission`, `grant_scope_type`, `selector_type`. They are not
   configuration, they are the language — a grant naming a code that does not exist is not a narrow
   permission but a save-time refusal, and a selector added at runtime is a word no resolver knows. That
   distinction is exactly [00 §10's](../data-model/00-conventions.md#10-migration-discipline) argument for
   putting them in migrations, and it survives the seed deletion untouched.
3. **Ten catalog codes are granted by nobody at first** — `event.cancel`, `event.delete`,
   `event.organizer.manage`, `event.question.manage`, the four `guardianship.*`, `person_group.edit`,
   `person_group.end`. They stay registered, they keep their `right_kind` and their `applies_to`, and they
   are grantable from day one by whoever holds `system.admin`. A permission the catalog carries and no
   seeded role happens to hold is not dead weight; **it is the list the organization reads in order to
   decide what to grant**, which is the second half of why the catalog exists at all.
4. **`role.is_system` and `audience.is_system` go with the seed they flagged.** A column saying *this row
   came from the migration* is a flag whose only function is to protect rows the design has just stopped
   shipping, and `system.admin` needs no protection because it is a permission, not a role.

**The consequence the round has to say out loud: event answers.**
[D-102](round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)
made creating an event oblige an `event.answer.view` grant aimed at `ORGANIZERS`, and 08a §10 check 2
reports the events that arrived without one. With the seed gone, **the organization writes that grant
itself**, once, as an ordinary grant — there is no exception carved for event-answer privacy and none is
needed, because the check that catches a missing one does not care who wrote it. The failure shape is
unchanged and now has one more way to happen: an organizer is a person with a title and no permissions,
and it reads as a bug report rather than a constraint violation.

**What it costs, stated as costs.** **A first run of the system has no useful permissions until somebody
writes them**, which is a real onboarding cost and the reason this was worth deciding rather than
discovering; the honest mitigation is that the catalog is written to be read as a checklist. **Every
worked example that used a seeded role becomes an example of writing one**, so round 19 is a sweep of
twenty-five pages rather than a deletion — and `ORGANIZERS`, which appears most of those twenty-five
times, is a selector and stays. **And nothing refuses the setup account a bad day**: one account holding
everything is the shape with the least ceremony and the most blast radius, and
[D-126](round-17.md#d-126--break-glass-is-a-report-and-a-written-procedure-not-a-mechanism)'s check 9 is
already the report that watches whether that account can still sign in.

---

See also [00a — who enforces each invariant](../data-model/00a-invariant-register.md),
[data-model/00 §6a](../data-model/00-conventions.md#6a-who-enforces-an-invariant-now),
[D-104](round-10b.md#d-104--a-permission-codes-last-segment-is-an-action-and-a-registry-that-prose-contradicts-is-a-fiction)
for the diff this round made executable, and
[D-072](round-06.md#d-072--the-documentation-carries-no-sql-the-schema-is-the-orms-job) for why the answer
to "who writes the constraint?" is a document.
