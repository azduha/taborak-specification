# Data Model — Authorization: the expression tree and what each operand costs

The storage half of §8: the `audience_operand` tree itself, the namespace rule,
what each operand costs, and how a tree is evaluated.

**Section numbers are shared across the five parts** and never renumbered, because other
pages cite them by number and their anchors are built from them: [05-authorization.md](05-authorization.md) holds §1–§7, [05a](05a-audience-and-grammar.md) §8 (the `audience` table, the grammar, the selector registry), [05b](05b-expression-tree.md) §8 continued (the tree and what each operand costs), [05c](05c-access-log-and-resolver.md) §9–§10 (`access_log` and the resolver), and [05d](05d-invariants-and-seed.md) §11–§13 (invariants, seed data, open issues).

---

### The expression tree

**Each row of `audience_operand` is one node** — the storage D-101 chose over a normalized union of
terms, "because a binary tree needs one evaluator of about fifteen lines and keeps the writer's
brackets instead of silently rewriting them".

**Fields** (`audience_operand`)

| Field | Kind | Notes |
|---|---|---|
| `id` | integer identity | Surrogate key. |
| `audience_id` | reference to `audience`, required | **Denormalized onto every row so that the whole tree is one indexed fetch.** The read path never walks a parent chain; it selects by `audience_id` and assembles in memory. **Amended by [D-103](../decisions/round-10b.md#d-103--an-audience-may-name-another-audience): one read *per audience in the closure*, not one read per check.** D-101's sentence counted one tree and stopped; an expression naming `AUDIENCE(veterans)` has to fetch that audience's rows as well, so the honest count is one indexed read for every audience the expression can reach. **The claim that survives is the one that mattered** — no transitive walk over `audience_operand` rows and no recursive query, just one indexed flat read per audience in the closure. **What had to be corrected is the second half of that sentence:** it used to say the number of reads was *"bounded by rule (the same `selector_depth_limit`)"*, and there is no rule bounding it any more ([D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)). **The honest statement is closure size, discovered by walking it at save — not bounded by a number.** The cost is known before the first check runs, because the walk that checks acyclicity has already counted the audiences; it is not known in advance of the expression, and the page says so wherever it was tempting to imply otherwise. Every row also carries its parent's `audience_id`, so a node never belongs to a different audience than the one above it (checked on save, asserted by check 10). |
| `parent_id` | reference to `audience_operand`, optional | **On the child**, so a node belongs to exactly one expression. Absent on the root. |
| `operator` | enum: `+`, `-`, `*`, optional | Set on a node, absent on a leaf. |
| `left_id` | reference to `audience_operand`, optional | Set on a node. **Left and right are not interchangeable:** `-` is not commutative, and the pair is the expression's meaning. |
| `right_id` | reference to `audience_operand`, optional | Set on a node. |
| `selector_kind` | reference to `selector_type`, optional | Set on a leaf, absent on a node. |
| `selector_arg_id` | integer, optional | **Polymorphic, and deliberately without a foreign key** — it points at `role`, `person_group`, `person`, `event` or **`audience`** depending on kind — **or it points at nothing, which is new in [D-107](../decisions/round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded): `OLDER` and `YOUNGER` write their integer into this same column**, because the column is an integer and the value is one. **This is the one place the round could have broken an invariant and did not**: §11 asserts that exactly two polymorphic columns in this design go without a foreign key, and it still holds at **thirteen** operands — **it held at fourteen and it held at twelve, and this is the one count in this module that a row arriving or leaving cannot break, because the invariant is about columns and the row move is about operands; `GUARDIANS` leaving removed a kind that *did* reference, so the referenced set (`role`, `person_group`, `person`, `event`, `audience`) is unchanged and the orphan scan still walks exactly those five** — **for the right reason rather than by luck** — the count is of *references*, and `18` is not one: nothing to repoint on a merge, nothing for a cascade to find, nothing for the orphan scan to walk, **which is precisely why that scan filters on the selector's kind and walks the five entity kinds rather than every row in this column** (§*A hand-named person is now a keyless reference*). **A reader who takes "polymorphic" to mean "always a row id" will write that scan wrong, which is why the sentence is here.** [D-011](../decisions/round-01a.md#d-011--scope_id-on-access_grant-is-polymorphic-with-no-foreign-key)'s already-accepted trade-off, with its compensating orphan check (§11, check 2). Absent exactly when the selector's `takes_argument` is false. **An `AUDIENCE` leaf stores the referenced audience's row here and is therefore also the reference edge** (rule below), and the extra condition on that leaf is that the audience it names **has a `code`** — a check reading another table, which is why it is an integrity check and not a constraint (§11, check 12). |
| `created_at` | timestamp, audit time | |
| `created_by` | reference to person | Who wrote this node. An expression is a decision about how far a grant reaches, and the person who saved it is the answer to the question asked afterwards. |

**Rules** (`audience_operand`)

- **Exactly one shape.** A node has `operator`, `left_id` and `right_id`, and no `selector_kind`; a
  leaf has `selector_kind` (and `selector_arg_id` where the registry says it takes one) and no
  operator and no children. **Expressible on the row, so this one stays a real constraint** — the
  only rule in this section a migration can state by itself, which is worth noticing among the ones
  that cannot.
- **One parent, never a DAG.** `parent_id` lives on the child. A side table letting two expressions
  share a node is **refused**: editing the shared node would silently widen every grant using it,
  which is D-091's inclusion hazard re-imported through the back door. Check 15 (§11) is a CI
  assertion that no such table exists.
- **Cycles are refused when the row is saved, there are two walks to run, and between them they are now
  the only structural guard this module has.** Both survived
  [D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)
  **deliberately, and they must not be relaxed alongside the bound they used to travel with**: an
  expansion that never terminates is the failure the deleted height limit was never protecting against
  anyway, and with the bound gone nothing else stands between a saved expression and an unbounded one.
  1. **Inside the tree:** walk the parent chain from the row upward — refuse a revisit. The tree shape makes a cycle
     structurally hard to build (a node cannot be its own ancestor if it did not exist when its
     parent was written) and it is **refused rather than trusted** for D-091's own reason: *a
     hand-fixed row, a restore from before the guard existed*.
  2. **Across audiences:** follow every `AUDIENCE` leaf in the closure and refuse a cycle through
     them. **This is the walk [D-103](../decisions/round-10b.md#d-103--an-audience-may-name-another-audience)
     makes necessary, and it is the sentence D-101 got wrong, struck here rather than quietly
     corrected:** ~~a tree cannot cycle, so the only acyclicity guard left is the cheap parent-chain
     one~~ — true of one tree, false of a **forest of trees pointing at each other**, which is what
     naming an audience creates. Half a is cheap; half b is the write-time reachability walk D-091
     already required, over a graph **built at save time from rows that already exist** — and it is the
     walk that also counts the closure whose size the read path pays for, since it is already visiting
     every audience in it. **The height limit that used to be measured on the same expanded tree is
     gone, and this is the exact spot where it was enforced.** Application layer for both walks, and the layer is named
     because each spans rows rather than columns of one row, which is
     [F-10 shape 3](../open-questions.md#f-10--which-invariants-the-orm-cannot-express-and-who-writes-those),
     so no migration can emit either.

  **What did not come back is worth as much as what did.** `audience_include` stays deleted: the
  edges *are* the `AUDIENCE` leaves, so there is no edge table to maintain, no transitive walk over
  rows at read time, and no `include_depth_limit` column. **The machinery D-101 counted as deleted
  stays deleted; only its confidence was wrong.**
- **The tree is stored exactly as the writer wrote it: one row per node, two operands and one operator,
  left to right, and no rebalancing**
  ([D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)).
  This is written as a rule because rebalancing was the tempting engineering answer the moment the height
  bound was removed — a balanced tree is cheaper to walk, and nothing here wants a cheaper walk badly
  enough to pay for it. **A rebalanced tree is a different expression from the one a person wrote**, which
  is the whole reason this storage exists rather than a normalized union of terms (D-101's choice, restated
  at the top of this section), and a quietly flattened tree is one whose canonical rendering no longer
  prints what its author saw.
- **Nothing bounds how big an expression may get, and this page calls that what it is: a convention, not a
  guard.** [D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)
  deleted the parameter and refused to mint a replacement, so **the size of an audience's expansion is now
  bounded only by acyclicity** — a bound on height no longer exists and a bound on breadth was never
  asserted. What replaces the retired invariant is a **standing report of the widest and deepest audiences
  and their cost per check**, together with ~~the operand cache of §10~~. **That pairing got weaker in round 14 and
  the bullet should say so rather than keep advertising a mitigation that is gone:** cached answers meant a wide
  expansion was paid for once per person per night, so the cost of a thousand-person `EVERYONE` stopped being
  anybody's problem between rebuilds; with the answers deleted ([D-114](../decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation)) it is paid per check, memoized
  within a request and cached nowhere wider — compiling once per version removes the parsing and the name
  resolution from that cost, not the reads. **So this convention now carries more load with the same enforcement.**
  Nothing refuses a save on size, no CI job fails, and the report stops being a control the moment nobody reads
  it. That is
  [D-081](../decisions/round-06.md#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now)'s
  case exactly — the rule's name outlives the mechanism and the text must say which of the two happened —
  and **D-105 counts this as the third control of that shape the authorization module now depends on.**
- **Arity and binding are checked against `selector_type`** on save: an argument present exactly when
  the registry allows one, and a **bound** (argument-less, `binds_to_item`) operand legal only on an
  item-scope grant whose type matches `argument_type` (§6, *What is refused when a grant is saved*).
- **An operand that does not resolve is the empty set** — including an `AUDIENCE` leaf whose target
  has gone (D-103). A dangling `selector_arg_id`, a selector kind the evaluator does not implement, a
  role or group whose row has been deleted — each is the empty set, and an expression that cannot be
  evaluated reaches nobody (§*Evaluation*). **Fail closed on the allow side, and note that the same
  rule is fail-*open* looking, which is why it is stated with its two halves rather than as a
  slogan**: an empty operand reached through `-` makes the result **wider**, so `EVERYONE - <nothing>`
  denies everybody. **The corpus's word for this was *"loud"*, and round 12 retired it**
  ([D-106](../decisions/round-11-12.md#d-106--a-failed-operand-stays-the-empty-set-the-missing-half-was-a-report-not-a-refusal)):
  `-` was never noisy, it is **the only operator whose failed operand can grant**, and naming a direction
  "noise" is how a rule gets read backwards. The sentence to keep is the directional one — **a failed
  operand on the `+` or `*` side narrows the set, a failed operand on the `-` side widens it** — because
  *fail closed* names a direction and not a safe state, and `EVERYONE - PERSON(x)` with a dead `x` is
  fail-closed **and** a lockout of everybody in one breath. D-103 kept the rule because a silent widening is
  discovered in an audit two years late; **what round 12 added is a page, not a rule.** An audience carrying
  a leaf that does not resolve is **listed for its owner**, in a second column of the report
  [F-21](../open-questions.md#f-21--closed--no-report-a-tab-on-the-permissions-page-and-unbounded-cost-is-accepted-at-the-stated-size)
  already asks for. **No save is refused because a leaf is broken, and no expression is pinned to the set it
  resolved to when it was saved** — pinning would make the stored expression a ceiling on truth, and a grant
  would freeze at the shape it had on the day somebody typed it. **The report is a query with an owner:
  D-081's
  [convention, not a guard](../decisions/round-06.md#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now)**,
  written as though it were a guard by the round that offered it.
  **And the line D-106 draws is narrower than it looks: an operand that resolves fine and simply does not
  contain the person is not on that list.** A person with no birth date is not a failed `OLDER(18)` — the
  operand resolves to the people who are that age on the checked date, and the person is not among them,
  exactly as a person with no membership row is not a failed `MEMBERS`. **A missing attribute on the person
  being asked about is an ordinary answer, not a resolution failure**, and a report that conflated the two
  would page about every incomplete import in the country. The protection above (an audience named by a live
  grant cannot be ended or deleted) is what keeps the wide case from arriving by ordinary administration.
- **The `AUDIENCE` leaves *are* the reference edges, and there is no edge table**
  ([D-103](../decisions/round-10b.md#d-103--an-audience-may-name-another-audience)). Every
  question about nesting — *does this cycle*, *how deep does this get*, *which grants name this
  audience*, *may this audience be deleted* — is answered by selecting rows from this one table where
  `selector_kind = 'AUDIENCE'`, which is why the round could delete `audience_include` and add nesting
  in the same breath. **The two-directional index that makes that cheap is `(selector_kind,
  selector_arg_id)`**, and it is the second reason the reference is stored as a row rather than parsed
  out of a rendering: an edge inside a string answers none of those questions without a table scan.
- **A node belongs to exactly one tree, and to exactly one audience.** Every row's `audience_id`
  equals its parent's; there is exactly one row with no parent; no row is its own descendant. Check 10
  (§11) counts these. **Nesting does not soften this**: `AUDIENCE(x)` points a *whole tree* at another
  whole tree. It is not a node shared between two expressions, and the rule above about one parent and
  no sharing table is exactly what keeps `AUDIENCE()` from being `audience_include` again by another
  name.
- **The whole tree is written together.** An expression is one act of authorship, so inserting a
  grant's audience inserts its nodes in one transaction, and deleting an audience deletes them.
  A node whose parent arrives in a later transaction is an orphan, and an orphan is check 10, not a
  transient state to be tolerated.

**Why a tree and not a string, and why not a normal form.** A string would have to be re-parsed on
every check and would make the arity and depth rules text-processing rather than row-writing. A
**union of terms** (the normalization D-101's author offered and D-101 declined) needs the
normalizer — distribute, dedupe, sort, survive blow-up — and would rewrite the writer's brackets
behind their back. The tree needs one fifteen-line evaluator, keeps the brackets, and makes the depth
limit the only complexity bound, since `(A + B) * C` costs nothing.

**What that costs, once.** Two expressions with the same meaning are two different row sets, so *"you
already granted exactly this set on that row"* no longer falls out of storage. The route back is a
normalized **fingerprint** computed on save as a derived value used only for a warning — and if the
expansion overflows, skip the warning rather than refuse the write: **normalization informing a human,
not gating one.** Registered in §13 rather than promised, and the same reasoning is why
"this selector reaches nobody" belongs to the editor preview that has to exist anyway (§*The cost of
composition*) rather than to a syntactic check the tree cannot perform — a tree catches `X - X` on one
node and nothing else.

### `audience_member`, re-roled as the `LIST` leaf — deleted by D-105

**This section, and the table it described, are deleted**
([D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)).
D-101 had kept it with the words *"it stays"*, and this section's whole job in the last round was to
defend that keeping; a hand-written set of people is now written in the expression, as
`PERSON(a) + PERSON(b)`, in the same place every other set in this language is written. **The heading is
kept so that the pages linking here land on the deletion rather than on nothing.**

**What the table was, and what died with it.** `audience_member` held *persons* rather than *rules*: one
row per person per audience, with `valid_from` / `valid_to` on a half-open period and a no-overlap rule
counted over all rows, plus `added_by` naming who put that one person there. Its rules leave with it —
the no-overlap rule, the refusal to add a person to a seeded `is_system` audience (adding somebody to
`everyone` was a category error, and the refusal lived in the write path with the editor as its only
detector), the editor affordance that rendered the operand as `LIST (this audience)`, and one entry in
~~the cache-invalidation trigger list of §10~~ — **a list that no longer exists either** ([D-114](../decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation)), so
deleting this table has no cache to coordinate with any more. **The `is_system` refusal is a rule whose mechanism is gone
and whose name should not survive it:** there is no row left to refuse, so unlike the reports above this
one retires completely rather than becoming a report.

**What survives, and it is the reason this deletion is not a reversal of D-098.** The refusal to solve a
grant's exception by editing a group roster stands untouched, because the hazard is real and unchanged:
making three people members of `GROUP(kitchen)` in order to reach one grant **edits a roster that other
grants read**, and it creates a row in the group browser that is not a group anybody talks about.
[D-098](../decisions/round-10a.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority)
is still the rule that says so — **a group's members are true when no grant points at them** — and
`PERSON(a) + PERSON(b)` is now the answer that respects it. What is genuinely gone from that paragraph is
its *counterparty*: this table was one of the two dated-member tables the design apologised for, the
duplication D-080 would flag had two instances to explain, and **now it has one. `person_group_member` is
the only dated set of people the system keeps, and "the permission table must not become the system's
roster" is no longer a rule with a live counterexample sitting beside it.**

**The mitigation that no longer has anything to mitigate.** D-091 required that **the editor show which
operand each person arrived through**, and the requirement was interesting only because a person could
arrive through a rule *or* through a list. Both are now the same kind of thing — a leaf in one expression
— so the requirement reduces to *"show the expression"*, which the canonical rendering already does.
**The two-writers hazard this table used to absorb is stated where its absence is felt:
§*What `LIST` is, said plainly — withdrawn by D-105*.**

### Three named sets, and the one question nesting cannot answer

**`GROUP(x)`, `AUDIENCE(x)` and `PERSON(x)` are all "some people" and none of them is the same kind of
thing** ([D-103](../decisions/round-10b.md#d-103--an-audience-may-name-another-audience)). Writing
them side by side is the fastest way to see why the rounds kept them apart and what was accepted by
putting a nameable audience into the language. **The table had a fourth column until last round** — the
comparison this section and its neighbours drew was a four-way one over `GROUP(x)` / `AUDIENCE(x)` /
`LIST` / `PERSON(x)`, and
[D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)
made it three-way by deleting one of them, so what is compared below is an office's holders, a group's
roster and an audience's expression, with no fourth shape:

| | `GROUP(x)` | `AUDIENCE(x)` | `PERSON(x)` |
|---|---|---|---|
| What it is | A dated roster somebody maintains | A saved expression, evaluated live | One named person, typed into this expression |
| Who may change who is in it | `person_group.member.manage` | `audience.manage` on that audience | Whoever may edit this expression |
| Does it exist outside a grant? | **Yes** — D-098: a group's members are true with nothing pointing at them | No — it exists to aim a grant | No — and it is not a set anybody maintains |
| *"Was she in it on 1 June 2024?"* | **Answerable**, from the dated rows | **Not answerable** past the audit window | **Not answerable** past the audit window |
| Sensitive as | ⚠ company | 🔒🔒 authority | 🔒 one named person |

**The fourth row is the honest cost, and it is the D-100 distinction replayed one level down.**
`GROUP(x)` is materialized, so its past is reconstructable from its own rows; `AUDIENCE(x)` is a live
rule, and its past shape survives only in the audit trail — where
[D-088](../decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)
empties the payloads after 24 months. So **"who could see this child's data in 2024?" is answerable when
the grant pointed at a group and is not answerable when it pointed at a nested audience.** D-103
records that rather than arguing it away, and the reasoning is the one this corpus already uses for
derived membership: a rule whose reach cannot be reconstructed is still the right tool for a rule —
`MEMBERS` is not going to be replaced by a roster of everyone — but the gap gets closed by a report,
not by pretending the question has an answer. The report is the save-time listing in §*The cost of
composition*, kept over time rather than shown once; whether that is worth building is registered in
§13 and is the same question as
[F-7](../open-questions.md#f-7--dissolved--a-nightly-rebuild-of-cached-answers-and-a-materialized-effective-permission-table-are-one-job) wearing a different
hat. **One half of that identity has since been deleted** — [D-114](../decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation) removed the cached-answers side of
F-7 — so the comparison no longer points at a live mechanism. **What survives it is the history question, standing
on its own:** a saved snapshot of whom a grant reached is still the only thing that could answer about 2011, and it
is still D-110's record rather than a cache.

### Names are one namespace, and reserved words are the other half

**Bare `COUNSELORS` resolves against roles and groups together**, since `ROLE()` and `GROUP()` no
longer have to disambiguate — which makes **the name namespace load-bearing** in a way it was not
when a name was only a label
([D-101](../decisions/round-10b.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree)).
Five rules, and the layer each one lives in is the point:

1. **Names are unique across `role`, `person_group` and `audience.code`**
   ([D-103](../decisions/round-10b.md#d-103--an-audience-may-name-another-audience) adds the third
   table; `audience.name` is not in the namespace, only its `code`, because `code` is what resolves
   and `name` is what a screen displays). **No single constraint spans three tables**, so the write
   path carries it and integrity check 12 (§11) asserts the write path exists —
   [D-081](../decisions/round-06.md#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now)
   wording, because a rule with no database backstop is a convention until a check says otherwise.
2. **Case, whitespace and separators are folded on write**, so `Schuzka 2026-1`, `schuzka_2026_1` and
   `SCHUZKA2026-1` are one name and not three sets that look different in an editor.
3. **Every `selector_type.code` is reserved.** A group called `MEMBERS` is refused at the save rather
   than silently rewriting every expression in the system.
4. **Bare names still resolve to exactly two kinds: a role or a group.** An audience is reachable only
   through its own keyword, `AUDIENCE(veterans)` — naming the namespace a third way **without**
   widening bare resolution, which is what keeps stored expressions meaning what they meant when they
   were written (D-103; the `audience` rules at the head of this section).
5. **What is stored is always kind + id**, never a name — so **a rename never rewrites a grant**.
   A role renamed still carries everything aimed at it, which is the property the old
   `code`-keyed designs kept advertising and never quite had. **`AUDIENCE` obeys this like every other
   leaf**: the resolution happens once, at save, into `selector_arg_id`, and renaming the audience
   afterwards rewrites nothing. **Read the rule for exactly what it says: a *rename* rewrites nothing,
   because a rename leaves the row and its id where they were.** A person **merge** is not a rename — it
   retires an id — and every hand-named person in the system is now a leaf holding one, which is the
   subject of the next section rather than an exception hiding in this one.

**What is given up:** a name is now a security-relevant string. Two organizations that both call
something `leaders` and one of them a *group* and the other a *role* get one namespace deciding which
`leaders` a grant meant, and the answer is that they cannot, because the write path refused the second
one at the save. **Round 10 widened what that sentence covers**: an audience code colliding with an
office code was a cosmetic problem while nothing could name an audience, and is a silent grant once
something can.

### A hand-named person is now a keyless reference

**This is the thing [D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)
made load-bearing, and no page in this corpus required it before.** `PERSON` leaves used to be a
curiosity: the hand-typed people lived in `audience_member`, whose `person_id` was an ordinary foreign
key, so its rows moved or vanished correctly on their own and nobody had to think about it. **Now every
hand-named person in the system is a `selector_arg_id`, and that column deliberately has no foreign key**
([D-011](../decisions/round-01a.md#d-011--scope_id-on-access_grant-is-polymorphic-with-no-foreign-key)'s
accepted trade-off, extended to this column by D-101 and backstopped by an orphan scan rather than by the
database).

**Requirement, and it is new: a person merge, and a redaction, must repoint every `audience_operand` leaf
whose `selector_arg_id` names the absorbed or erased person, in all five argument kinds that name an entity.** The merge
reassignment table gains the row, the erasure path gains the scan, and the nightly orphan check (§11,
check 2) **becomes the backstop rather than the mechanism** — a scan that runs the following morning is
not a reassignment, and by the time it reports, an expression has already resolved wrong. It belongs to
[F-10](../open-questions.md#f-10--which-invariants-the-orm-cannot-express-and-who-writes-those)'s register
for precisely the reason that register exists: **the ORM cannot express it, because the column has no key
to follow.**

**Why this is not housekeeping.** A leaf that resolves to nobody is the empty set, which **narrows** the
result on the `+` and `*` sides and **widens** it on the `-` side — ~~quiet on the allow side and loud on
the deny side~~, in the wording [D-106](../decisions/round-11-12.md#d-106--a-failed-operand-stays-the-empty-set-the-missing-half-was-a-report-not-a-refusal)
retired — and this module's own recurring worked example is a subtraction: `EVERYONE - PERSON(x)`. **Un-repointed, `x` stops subtracting anybody and the grant denies everybody** —
the failure the rules two sections back have been pointing at for two rounds, now reachable by an ordinary
merge rather than by a hand-edited row. Repointing was not required before, and that was defensible only
while the volume of hand-named people sat in a table that had a key to follow.

**Why all five kinds, and not just `person`.** The scan is over one column, and the column does not know
what it points at. A merge is the case that made the requirement, but an erased event, a deleted group, a
retired office or an ended audience leave the identical orphan behind them, and **writing the rule as
"`PERSON` leaves only" would put the hazard straight back where it has been sitting for two rounds.**
The five kinds a scan walks are `person`, `role`, `person_group`, `event` and `audience`.
~~And they are the values `selector_type.argument_type` takes.~~ **That clause was true until round 12 and
here is its successor, because `argument_type` has gained a sixth value that is not a kind of thing a scan
could follow: `integer`, the argument of `OLDER` and `YOUNGER`.**
([D-107](../decisions/round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)).
**Six values, five of them entity kinds, and the scans walk the five.** This is the one place to say why,
because it looks like an omission and is not: **an `18` in `selector_arg_id` is not a reference**, so there
is no row behind it to merge away, none to erase, none for a cascade to find and none for the orphan scan to
report. **The number this section is about — that exactly two polymorphic columns in this design go without
a foreign key — is therefore still two, and still two for the reason it was two before**: the count is of
*keys*, and a scalar stored in a key's column is not one. **Nobody has to add a `person.birth_date` branch
to a merge script, and anyone who does has misread this paragraph.**

### What each operand costs

The distinction that used to be load-bearing — built-in *versus* named, rule *xor* list *xor*
inclusion — is gone, and what remained worth comparing was whether a set is **derived** or **kept**.
**The right-hand column is now empty, and that is what this round deleted:** `LIST` was the only operand
whose members were rows somebody maintained, and with it gone every operand in the registry reads a fact
that exists independently of the expression.

| | A derived operand | A kept operand |
|---|---|---|
| Which | All twelve of `EVERYONE`, `MEMBERS`, `OLDER`, `YOUNGER`, `ROLE`, `GROUP`, `ATTENDED`, `PLACED`, `CONFIRMED`, `ON_WAITLIST`, `ORGANIZERS` and `AUDIENCE` — **derived from another expression rather than from a fact table, which makes `AUDIENCE` the odd one and the reason this table has a footnote below**, plus `PERSON`, which is neither: see below. **`OLDER` and `YOUNGER` sit here on the strength of the row above them** — a live read of a stored fact at the checked date, exactly like `MEMBERS` reading `membership` — **but they are the first whose answer to *"when does someone join?"* is not "when a row is written"**: the row was written at birth, and the set changes on its own. §*The cost of composition* carries what that costs | **None since [D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other) deleted `LIST`.** The rows it held, the `valid_from` / `valid_to` pair, the no-overlap rule and the staleness this column existed to warn about are all gone with it |
| How evaluated | A live read of the fact that defines it, at the checked date | — |
| When someone joins | They are in it immediately — **automatically** | — |
| Maintenance | None. **It cannot rot.** | — |
| Membership stored? | No — and therefore not retrievable after the facts move (§*The cost of composition*) | — |
| Examples | "everyone who holds a place on this event", "the counselors", "anyone thirteen or older" | — |

**`PERSON(x)` is not the occupant of that column, and pretending it is would lose the distinction.** It
is a **constant**: the answer is written into the leaf itself, so it reads no fact table *and* maintains no
roster. It cannot rot the way a kept set rots — nobody has to remove anybody, because nobody is *in* it
except the one person named. What it can do is **dangle**, which is a different failure with a sharper
edge, and §*A hand-named person is now a keyless reference* is where that is handled.

**Prefer a derived operand where one exists.** A grant to `PLACED` gets the right answer forever: a
new registrant is covered the moment they are placed, and someone who withdraws stops being covered,
with no rows to maintain. A grant listing names by hand does not do that, and the old warning against it
— *the same grant silently rots the moment the roster changes* — **survives as advice even though the
operand it was written about is gone: a sum of `PERSON()` leaves goes stale exactly as a list did, it just
goes stale one leaf at a time.** What the two rounds changed is that choosing between derived and named
stopped being a choice about the *kind* of set, so one expression can hold the derived set and the names it
cannot reach, in one grant. **The other half of the old argument is now stated as a size rule rather than a
kind rule: a set of people big enough to be a roster is a `person_group`, and a set small enough to type is
a sum of `PERSON()` leaves** ([D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)'s
judgement, registered where missing operands are registered in [../open-questions.md](../open-questions.md)).

**The inclusion arm is deleted, and the second round had to give half of the answer back.** D-091 let a
group pull in other groups through `audience_include`, because a group could otherwise not be composed.
Under D-098 a group's membership **is** its dated rows, and composition moved into the expression:
`GROUP(kitchen) + ROLE(troop_staff)` composes as much as an edge ever did. What went with the edge table
was a great deal of machinery — the transitive walk, `include_depth_limit`, the write-time cycle walk
over a **graph**, and the CI assertion that the walk exists at all — and round 10 was right that a tree
needs none of it **within one tree**.

**Where round 10's arithmetic was wrong, stated plainly because the sentence is still in D-101.** It
claimed the write-time cycle walk was dead because *a tree cannot cycle*, and it claimed *"add the
kitchen crew to everything the troop-staff rule is used for"* was answered by **naming the composite
once and aiming grants at it**. Under its own grammar the only names available were `GROUP()` and
`ROLE()`, and **both name a roster, not a rule** — so the composite rule had no name to point at, and
the "naming" answer could only be carried out by copying rows into a second audience, which is
`audience_include` with the copy step done by hand. [D-103](../decisions/round-10b.md#d-103--an-audience-may-name-another-audience)
adds the missing arm, and with it **the cheap guard stops being the only guard**: one write-time
reachability walk returns, across audiences rather than over an edge table (§*The expression tree*).
**What stays deleted is the table, the column and the read-time walk** — the edges are leaves — so the
machinery that came back is smaller than the machinery that left, which is the honest version of the
claim. `AUDIENCE()` is also the only arm that names **a decision about access** rather than people, so
it is the only one that can say *"the same people that grant may see the fee ledger, plus the
accountant"*.

**`AUDIENCE` is derived, and it is derived from something nobody maintains, which is its one genuinely
new property.** Every other derived operand reads a fact table someone is already keeping — a
membership, a holder row, a registration. `AUDIENCE(x)` reads **an expression**. So the "maintenance:
none, it cannot rot" row of the table above is true of it in the sense that there are no rows to
maintain, and misleading in the sense that **the thing it is derived from is edited by whoever holds
`audience.manage` on it, for their own reasons**. That is the hazard of §*The cost of composition*, and
it is why this operand is graded as authority rather than as company.

### Evaluation

An audience grant is evaluated as part of the person's own permissions — the resolver expands it, so
a grant to an audience is checked *as if* the person held it directly. **The expansion is a
predicate, not a set** (§*Author in sets*).

A grant applies when **one** grant row satisfies all of these. These are conditions on a single row,
tested together — their order carries no meaning:

1. The grant names an audience; a personal grant is not this question's business.
2. Its `scope_type` is the scope type being checked, and its `scope_id` matches the scope id being
   checked, with an absent id counting as equal to an absent checked id.
3. Its `effect` is `allow` — denies belong to the channel that runs first (§10).
4. It has not been revoked.
5. It has started as of the checked date and has not ended on that date.
6. Its `permission_id` **is** the checked permission — or is `system.admin`, the one code that means
   everything (§2). **There is no `permission_level` row to consult and no rank to compare**; the
   comparison this condition used to perform is the whole reason that table existed and it is gone.
7. `person_in_audience(person, audience, at, item)` puts the person in that audience on the checked
   date, **for the item being checked** — because a bound operand means different people on different
   items ([D-102](../decisions/round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)).

`person_in_audience()` is where the language lives. It takes the item so that bound operands have
something to bind to, and it answers one question: **is this person in the value of this expression,
evaluated as a predicate?**

1. **The audience itself must not have ended** — no `valid_to`, or a `valid_to` after the checked
   date. An ended audience covers nobody, **and this is the one test that gates the whole tree**: the
   expression belongs to the audience that has ended, not to one of its operands.
2. **Evaluate the tree bottom-up, as a predicate.** A leaf asks its selector; a node combines its two
   children with its operator; `p ∈ A - B` is `p ∈ A ∧ ¬(p ∈ B)`, and so on for `+` and `*`.
   **No set of people is ever built** — the same fifteen lines answer every operand, and the cost of
   a check is one indexed read per operand, not one per member. **`AUDIENCE(x)` is the one leaf that
   recurses** (§*Three named sets*): it hands the same `person`, `at` and `item` to the other
   audience's tree and returns that answer, **predicating all the way down**
   ([D-103](../decisions/round-10b.md#d-103--an-audience-may-name-another-audience)). Nesting does
   not turn the evaluator into a set-builder; it turns one fifteen-line function into the same function
   with one more branch. **The recursion is bounded by nothing any more, and the sentence saying it was
   bounded by the save-time `selector_depth_limit` is deleted with the limit**
   ([D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)).
   **What still holds is the refusal that went with it: the read path gets no depth cap and no cycle
   check of its own.** That refusal used to be a back-up for a guard that existed at save time, and it was
   argued as *"the cap becomes the thing that decides who a grant reaches"* — **now it is the whole
   design**, so the acyclicity walk at save (§*The expression tree*) is the only thing standing between a
   saved expression and one that never finishes evaluating.
3. **A leaf's selector is one read** — except `AUDIENCE`, which is one read per audience in the
   closure. `MEMBERS` is the membership predicate at `at`;
   `ROLE(x)` is one open `role_holder` row for this person and this role at `at`; `GROUP(x)` likewise
   in `person_group_member`; **`PERSON(x)` is the cheapest leaf in the language — it is the comparison
   `x = p` against a value already stored in the row, so a hand-written sum of twenty names is twenty of
   those and no fact table is consulted**; `PLACED` is this person's
   `event_registration` row for the bound event with `response = attending` and `is_waitlisted`
   false; `EVERYONE` is true. **`OLDER(n)` and `YOUNGER(n)` are the two cheapest reads in the language
   after `PERSON`: one row already in hand — `person.birth_date` — compared against `n` at `at`, no join
   and no fact table.** **They are also the only operands whose answer `at` changes on its own**: every
   other leaf asks whether a *row* was live at `at`, and these two ask arithmetic about one, which is why
   a check for a past date has a right answer here (`can(p, view, doc, on 2024-05-01, about q)` computes
   the age that day) and why the set can move with no write to invalidate
   ([D-107](../decisions/round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)).
   **A person whose `birth_date` is null is not in either set**, and that is this rule answering, not
   failing — item 5 below is about leaves that resolve to nothing, and this is not one of them.
4. **A bound operand binds to the item under check.** `PLACED` with no argument means the event in
   the check's scope. **At the unit there is nothing to bind it to, and such a grant could not have
   been saved** (§6's save-time list) — so an unbound-at-unit shape reaching here is a fault, and it
   resolves to the empty set rather than to "everyone at the unit", which is the direction a helpful
   implementation would get wrong.
5. **Failure is denial, in every direction.** An operand whose `selector_arg_id` names nothing, whose
   `selector_kind` no evaluator implements, or whose tree cannot be assembled **reaches nobody** — the
   case this list used to carry as *"whose depth exceeds its bound"* left with the bound
   ([D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)),
   and a leaf whose argument names a person who has been merged away is on this list too, which is why
   §*A hand-named person is now a keyless reference* makes repointing a requirement rather than a
   nicety. Nothing here falls back to "so it probably includes everyone", and
   nothing here guesses the half of a tree it could resolve: **an expression that cannot be evaluated
   is an empty set**, which is the direction this model fails in everywhere else — default deny (§10),
   deny absolute (channel 0), and an audience whose rule was quietly wrong reaching nobody rather than
   everybody. **This supersedes the old fallback twice over:** first, an absent `resolver_key` used to
   mean "so it is a stored list"; now an absent selector is a **fault**, not a hint. Second, the
   inclusion walk used to be the one place a cycle could make the answer depend on where the walk
   started, and round 10 said ~~a tree cannot cycle, so there is nothing left to fail on~~. **That is
   true of a tree and false of a forest of audiences pointing at each other, and D-103 struck it.**
   **The consequence for the read path is deliberately nothing at all:** a cycle through `AUDIENCE`
   leaves is refused where it is written, so an evaluator meeting one is meeting data that should not
   exist, and the rule that covers that is this one — reach nobody, do not recurse forever and do not
   guess. **The reason the write-path check has to be a cross-audience reachability walk and not a
   parent-chain walk is exactly here** (check 15): if the read path is ever the thing that notices a
   cycle, some grant has already been evaluated wrong.

**Note that `ORGANIZERS` and `ROLE` read their tables without themselves being authority grants.**
Membership in an audience confers nothing on its own — it only decides whether *this* grant, which
someone already created deliberately, reaches this person. An appointed organizer does not become able
to do anything by being on the roster; they become able to do exactly what the grant aimed at
`ORGANIZERS` says, on that event. **This is [D-062](../decisions/round-05.md#d-062--organizers-are-appointed-on-the-event-not-granted)
standing untouched**, and it is the sentence D-102 leans on: the appointment is now *aimed at* by
grants instead of being special-cased inside the resolver.

### What audiences do **not** do

- **They are not a permission.** Being in an audience is not authority; it is membership of a
  set. All authority still comes from a grant.
- **They do not replace `guardianship_permission`, and they cannot reach guardianship at all.**
  ~~`GUARDIANS` lets an organization open something to a child's guardians; it does not let a guardian edit the
  child's record.~~ **Both halves of that sentence were wrong in the same way, and
  [D-113](../decisions/round-13.md#d-113--the-guardianship-channel-has-no-expression-guardians-is-not-a-selector)
  deleted the operand it was written about: a guardian's authority is not a set of codes an audience could
  extend one at a time. It is a `right_level` of `none` / `view` / `write` on the live `guardianship` row
  (§10, [D-074](../decisions/round-06.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular)),
  and it reaches **any action about that child** — wider than any grant could assemble, and narrower in the only
  direction that matters, because it reaches nothing that is not about the child.** So an audience neither
  opens nor closes guardianship: **a deny still overrides the channel, because the deny channel runs first and
  is scope-independent (§10)**, which is the one thing an audience can do to it. What an audience *can* do with
  a guardian is be a group the organization keeps — the six contact adults of these children are
  `GROUP(x)`, a roster with a lifetime and no authority
  ([D-098](../decisions/round-10a.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority))
  — which is a different fact, written down, about different people.
- ~~**They do not nest.**~~ ~~**Withdrawn by D-091; the mechanism was removed by D-101.**~~
  **Nesting returns in the same round, through [D-103](../decisions/round-10b.md#d-103--an-audience-may-name-another-audience),
  and the three-stage history is worth keeping because the diagnosis never changed.** The sentence read
  *"an audience cannot contain another audience — that is how you get evaluation cycles and answers
  nobody can predict"*. Round 9 refused the cycle when the edge was saved; round 10 declared the
  problem **unsayable**, because an operand is a leaf naming a set and not a pointer into another
  expression; and D-103 found that the second round had answered *"reuse a rule"* with *"name the
  composite"*, while its own grammar offered no name for a rule — so the arm came back as
  `AUDIENCE(<code>)`. **What the ban was for survives intact, in a different place:** cycles are still
  impossible to *store*, they are just no longer impossible to *write*, so the guard is a
  cross-audience reachability walk on the save path instead of a shape argument (§*The expression
  tree*, check 15). **What the ban cost is also back, and honestly back:** *"the kitchen crew plus
  whoever leads this pack"* was the complaint round 10 solved in one grant, and it stays solved —
  `AUDIENCE()` does not undo it, it adds the case round 10 could not express, which is reusing a
  composite **rule** rather than copying it.
- **Nesting is not sharing.** `AUDIENCE(x)` evaluates the whole of another audience's expression; it
  does not splice one of its nodes into this tree. **Two expressions never share a row**, so editing a
  node inside `veterans` changes exactly the grants that name `veterans` and no others — which is the
  distinction that keeps this from being the DAG this corpus has now refused three times.
- **`everyone` is genuinely everyone**, including people with no account and no membership.
  It is the right target for a public event page and the wrong one for anything else. **And it is
  reachable by `+` from inside any expression**, which is what the deletion of the inclusion arm
  changes: nothing stops an expression from unioning the seeded `EVERYONE` operand, and a writer with
  `audience.manage` can widen a grant to the whole world in one edit. That is not a hole in the model —
  holding `EVERYONE` directly is already legal and already alarmed (check 8, §11) — it is that a
  language with union in it makes the same reach available without even pretending to compose it
  carefully. The mitigation is the editor's expanded set below, not a rule about which operands may
  appear where.
- **A role cannot be held by a rule.** `role_holder` names one person, and
  [F-12](../open-questions.md#f-12--closed--may-a-role-be-held-by-a-rule-as-an-audience-is) **is closed by
  [D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape),
  and its answer is no** — a derived holder list cannot answer "who was treasurer in 2023", and an
  office record that cannot answer that is not an office record. The grantee pair F-12 contemplated is
  no longer even tempting, because grants now aim **at** roles instead of roles being filled **by**
  grants.
- **An expression cannot compute with a person's attributes.** ~~An expression cannot say anything about
  a person's attributes.~~ That bullet stood for rounds and
  [D-107](../decisions/round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)
  narrowed it rather than deleting it, because it was standing on the sentence §*Author in sets* has now
  withdrawn — that an attribute is not a set of people. **`OLDER(15)` says something about an attribute and
  it is a row of the registry**, so the negative that survives is about *terms*, not about subject matter:
  **`AGE >= 15` is not an operand, is not expressible, and there is still no open question asking for it**,
  because there is no comparison operator for it to use and no way to add a row from a screen. **What an
  author may write is what shipped**; that, and not the type of the thing written about, is the closure
  property §*Author in sets* protects. Eligibility is capability
  ([D-060](../decisions/round-05.md#d-060--eligibility-is-capability-there-is-no-separate-rule-engine))
  in the sentence that is now true of it: **no rule is evaluated outside `can()`, no eligibility rule table
  exists, and the system gates nobody on its own — an age rule is a grant somebody wrote, visible in the
  grant list, revocable like one.**

### The cost of composition

**A grant's reach stops being visible in the row that grants it.** Derived membership has never been
stored — D-042 accepted that, and these documents recommended it, because a rule does not rot the way
a list does. Rounds 9 and 10 together **widened how much of the permission answer is recomputed
rather than recorded**, and round 10 added a sharper wrinkle.

- **The editor must show the set a grant actually reaches, expanded** — the people, not the
  expression's text — and it is a requirement on the screen rather than a nicety. Composition turns a
  three-deep expression into a silent widening, and the person saving the grant is looking at one row
  that mentions no person at all. **This is the same posture as the cache question in §10: the answer
  exists, it is just not stored, so somewhere has to compute it in front of a human** — and here the
  human is the only control there is.
- **And the preview is now per-item, which it structurally cannot be from the grant alone**
  ([D-102](../decisions/round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)).
  `PLACED` means different people on different events, so "who does this grant reach?" is unanswerable
  as written when the expression contains a bound operand. **The preview is therefore computed for an
  item and says so on screen** — an honest screen names the event whose people it is showing — and after
  [D-114](../decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation) the rule that a bound operand may never answer for another item is a rule about **how a predicate
  is bound** rather than about what a key must contain — the item is a parameter of the compiled predicate (§10),
  which is the same requirement with one fewer place to get it wrong. This is the one place where D-102's
  convenience costs a screen an editor's design has to notice, and §13 keeps it open rather than
  assuming it away.
- **Editing an audience changes grants you did not make, and the screen has to say so before it
  commits** ([D-103](../decisions/round-10b.md#d-103--an-audience-may-name-another-audience)).
  Add a person to `AUDIENCE(veterans)` and every grant naming it now reaches them — including grants
  their owners wrote for another purpose, and including grants this editor cannot see because they are
  not theirs. **This is not a new failure mode and pretending otherwise would be the actual mistake:**
  `GROUP(x)` has had the property since D-091, and the round that accepted it there accepted it for the
  reason that stands — **a named set is worth being reusable, and a reusable thing has more than one
  user.** The mitigation is D-091's, extended to the second user: **saving an edit to a referenced
  audience shows which grants name it, and at what depth, before it commits.** It is one indexed query
  over the leaf rows (§*The expression tree*), and it doubles as the report that partially closes the
  history gap in §*Three named sets*. **D-103 registers this as an assumption rather than a measured
  fact** — cheap at this organization's size because the edges are indexed rows in the table that
  already holds every expression, unverified at any size, and **a slow save screen is a real risk if the
  import corpus's row-count estimates turn out wrong**. §13 keeps it.
- **"Who could read this in 2023?" now has one fewer answer.** The audit trail used to hold the change
  that made it true, and [D-088](../decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)
  empties those payloads after 24 months; the derived membership was never stored at all. After two
  years the question is answered by re-running expressions against state that has itself moved on, and
  it is answered with today's confidence. ~~**F-7 is the route back** — a materialized
  `effective_permission` snapshot kept *as history* rather than as a cache~~ — **there is no route back, and
  round 13 is the round that said so.**
  [F-7](../open-questions.md#f-7--dissolved--a-nightly-rebuild-of-cached-answers-and-a-materialized-effective-permission-table-are-one-job)
  was **dissolved**, not answered: a nightly rebuild of cached answers and a nightly materialized
  `effective_permission` table turned out to be one job with two names, so the snapshot this bullet kept
  proposing as the thing that would make history answerable **is the cache, wearing the other name, and it
  does not make history answerable either** — a table of *today's* answers, rebuilt nightly, is as blind to
  2011 as the cache is. **The honest statement of this limitation is now the flat one: a historical check is
  re-running today's expressions over whatever state survives, and after the payloads expire that state has
  moved on.** Caching was §10's subject until round 14 deleted the thing, and the deletion changed only the verb
  tense of that sentence: **history has no owner, and that is recorded as a limit rather than a to-do.** The cache
  was as blind to 2011 as no-cache is — which is precisely what made F-7 one question and not two, and what keeps
  its dissolution valid after the cache is gone.
- **Something has to keep count of how big expressions get, because nothing refuses them any more.**
  [D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)
  deleted the height bound along with the parameter that held it, and refused to mint a replacement, so
  **the size of an audience's expansion is bounded only by acyclicity** and *"a check costs a bounded
  amount"* is deleted from this system's properties — that property came from the bound and nowhere else.
  What replaces it is a **standing report**: the widest and deepest audiences, their closure size, and
  their cost per check, kept running rather than computed once at save. **It is a report with no CI
  behind it — a convention, not a guard**
  ([D-081](../decisions/round-06.md#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now)),
  and it is the third control of that shape this module depends on. **Say it in those words wherever the
  old bound is missed**, because the failure mode of a report nobody reads is that it stops being read and
  nothing else happens. **Who reads it was the last open half of this bullet, and round 13 answered it with
  the cheapest object available: not a report and not a job, a
  [tab](../open-questions.md#f-21--closed--no-report-a-tab-on-the-permissions-page-and-unbounded-cost-is-accepted-at-the-stated-size)
  on the permissions page.** The answer to *who reads it* is therefore still *nobody, necessarily* — a tab is
  read by whoever opens it — and that is now a decision rather than an oversight, with
  [D-112](../decisions/round-13.md#d-112--the-systems-scale-is-stated-hundreds-of-people-tens-of-registrants-per-event)'s
  stated size underneath it and a trigger on top. The save-time walk that computes it is the same walk that checks acyclicity
  (§*The expression tree*), so the number costs nothing extra to obtain; what costs something is deciding
  to look at it.

---
