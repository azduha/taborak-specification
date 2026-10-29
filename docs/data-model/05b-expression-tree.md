# Data Model — Authorization: the expression tree and what each operand costs

The storage half of §8: the `audience_operand` tree itself, the namespace rule,
what each operand costs, and how a tree is evaluated.

**Section numbers are shared across the six parts** and never renumbered, because other
pages cite them by number and their anchors are built from them: [05-authorization.md](05-authorization.md) holds §1–§7, [05a](05a-audience-and-grammar.md) §8 (the `audience` table, the grammar, the selector registry), [05b](05b-expression-tree.md) §8 continued (the tree and what each operand costs), [05c](05c-access-log-and-resolver.md) §9–§10 (`access_log` and the resolver), and [05d](05d-invariants-and-seed.md) §11–§13 (invariants, seed data, open issues), and [05e](05e-keys-and-callers.md) §14–§17 (a key, and what it may hold).

---

### The expression tree

**Each row of `audience_operand` is one node** — a binary tree: two operands and one operator per row.
**Why:** one evaluator of about fifteen lines answers every operand, and the tree keeps the writer's
brackets instead of silently rewriting them ([D-101](../decisions/round-10b.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree)).

**Fields** (`audience_operand`)

| Field | Kind | Notes |
|---|---|---|
| `id` | integer identity | Surrogate key. |
| `audience_id` | reference to `audience`, required | **Denormalized onto every row so that the whole tree is one indexed fetch.** The read path never walks a parent chain; it selects by `audience_id` and assembles in memory. **One indexed read per audience in the closure, not one per check** ([D-103](../decisions/round-10b.md#d-103--an-audience-may-name-another-audience)): an expression naming `AUDIENCE(veterans)` has to fetch that audience's rows as well. No transitive walk over `audience_operand` rows, and no recursive query. **The closure's size is discovered by walking it at save, not bounded by a number** — the walk that checks acyclicity has already counted the audiences, so the cost is known before the first check runs, and it is not known in advance of the expression (rule below, and §*The cost of composition*). Every row also carries its parent's `audience_id`, so a node never belongs to a different audience than the one above it (checked on save, asserted by check 10). |
| `parent_id` | reference to `audience_operand`, optional | **On the child**, so a node belongs to exactly one expression. Absent on the root. |
| `operator` | enum: `+`, `-`, `*`, optional | Set on a node, absent on a leaf. |
| `left_id` | reference to `audience_operand`, optional | Set on a node. **Left and right are not interchangeable:** `-` is not commutative, and the pair is the expression's meaning. |
| `right_id` | reference to `audience_operand`, optional | Set on a node. |
| `selector_kind` | reference to `selector_type`, optional | Set on a leaf, absent on a node. |
| `selector_arg_id` | integer, optional | **Polymorphic, and deliberately without a foreign key** — it points at `role`, `person_group`, `person`, `event` or **`audience`** depending on kind — **or it points at nothing: `OLDER` and `YOUNGER` write their integer into this same column** ([D-107](../decisions/round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)), because the column is an integer and the value is one. **An integer in this column is not a reference**: nothing to repoint on a merge, nothing for a cascade to find, nothing for the orphan scan to walk — **which is precisely why that scan filters on the selector's kind and walks the five entity kinds rather than every row in this column** (§*A hand-named person is now a keyless reference*). A reader who takes "polymorphic" to mean "always a row id" will write that scan wrong, which is why the sentence is here. §11's check 2 walks **two** of this design's seven keyless columns — `access_grant.scope_id` and this one — its check 23 walks four more, and [00 §9](00-conventions.md#9-referential-integrity-rules) keeps the count and says which one is walked by nothing — and none of that moves at **thirteen** operands; the count is of *keys*, so a scalar sitting in a key's column does not move it, and an operand arriving or leaving cannot move it either. [D-011](../decisions/round-01a.md#d-011--scope_id-on-access_grant-is-polymorphic-with-no-foreign-key)'s accepted trade-off, with its compensating orphan check (§11, check 2). Absent exactly when the selector's `takes_argument` is false. **An `AUDIENCE` leaf stores the referenced audience's row here and is therefore also the reference edge** (rule below), and the extra condition on that leaf is that the audience it names **has a `code`** — a check reading another table, which is why it is an integrity check and not a constraint (§11, check 12). |
| `created_at` | timestamp, audit time | |
| `created_by` | reference to person | Who wrote this node. An expression is a decision about how far a grant reaches, and the person who saved it is the answer to the question asked afterwards. |

**Rules** (`audience_operand`)

- **Exactly one shape.** A node has `operator`, `left_id` and `right_id`, and no `selector_kind`; a
  leaf has `selector_kind` (and `selector_arg_id` where the registry says it takes one) and no
  operator and no children. **Expressible on the row, so this one stays a real constraint** — the
  only rule in this section a migration can state by itself, which is worth noticing among the ones
  that cannot.
- **One parent, never a DAG.** `parent_id` lives on the child. A side table letting two expressions
  share a node is **refused**. **Why:** editing the shared node would silently widen every grant
  using it — the inclusion hazard re-imported through the back door (D-091). Check 15 (§11) is a CI
  assertion that no such table exists.
- **Cycles are refused when the row is saved, and the two walks below are the only structural guard
  this module has.** Nothing else stands between a saved expression and one that never terminates, so
  they are not relaxed for any reason: an expansion that never terminates is precisely what they
  refuse.
  1. **Inside the tree:** walk the parent chain from the row upward — refuse a revisit. The tree shape
     makes a cycle structurally hard to build (a node cannot be its own ancestor if it did not exist
     when its parent was written), and it is **refused rather than trusted** for D-091's own reason:
     *a hand-fixed row, a restore from before the guard existed*.
  2. **Across audiences:** follow every `AUDIENCE` leaf in the closure and refuse a cycle through
     them. **Why:** a tree cannot cycle, and an expression naming audiences is a **forest of trees
     pointing at each other** ([D-103](../decisions/round-10b.md#d-103--an-audience-may-name-another-audience)
     is what makes this half necessary). Half 1 is cheap; half 2 is a write-time reachability walk over
     a graph **built at save time from rows that already exist**, and it is the walk that also counts
     the closure whose size the read path pays for, since it is already visiting every audience in it.
     **No size is measured here:** the walk refuses a cycle and nothing else.

  Application layer for both walks, and the layer is named because each spans rows rather than columns
  of one row, which is
  [shape 3](00a-invariant-register.md#3-the-answer-reads-another-table-a-resolver-or-a-graph),
  so no migration can emit either.
- **There is no edge table and no depth parameter.** `audience_include` and `include_depth_limit` are
  not in the model: the edges *are* the `AUDIENCE` leaves, so there is nothing to maintain and no
  transitive walk over rows at read time
  ([D-101](../decisions/round-10b.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree),
  [D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)).
- **The tree is stored exactly as the writer wrote it: one row per node, two operands and one
  operator, left to right, and no rebalancing**
  ([D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)).
  **Why:** a rebalanced tree is a different expression from the one a person wrote — which is the whole
  reason this storage exists rather than a normalized union of terms — and a quietly flattened tree is
  one whose canonical rendering does not print what its author saw. A balanced tree is cheaper to walk
  and nothing here wants a cheaper walk badly enough to pay for it.
- **Nothing bounds how big an expression may get, and this page calls that what it is: a convention,
  not a guard.** There is no depth bound, no width bound and no node budget on an audience;
  `selector_depth_limit` is not a parameter and nothing replaces it
  ([D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)),
  so **the size of an audience's expansion is bounded only by acyclicity** — height was never bounded
  across a closure and breadth was never bounded at all. **"A check costs a bounded amount" is
  therefore not a property of this system**; that property came from a bound and nowhere else. What
  stands in place of the check is a **standing report of the widest and deepest audiences, their
  closure size and their cost per check**, kept running rather than computed once at save, and its home
  is the tab on the permissions page
  ([F-21](../open-questions.md#f-21)).
  **Nothing refuses a save on size, no CI job fails, and the report stops being a control the moment
  nobody reads it** — [D-081](../decisions/round-06.md#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now)'s
  convention rather than a guard, and the third control of that shape this module depends on. **The
  cost it reports is paid per check:** there is no stored answer to pay it once
  ([D-114](../decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation)),
  a request memoizes it, and a compilation is cached once per version and holds no person and no item
  (§10) — so compiling removes the parsing and the name resolution from the cost, not the reads. A wide
  `EVERYONE` is therefore nobody's problem only until somebody checks it.
- **Arity and binding are checked against `selector_type`** on save: an argument present exactly when
  the registry allows one, and a **bound** (argument-less, `binds_to_item`) operand legal only on an
  item-scope grant whose type matches `argument_type` (§6, *What is refused when a grant is saved*).
- **An operand that does not resolve is the empty set** — including an `AUDIENCE` leaf whose target has
  gone (D-103). A dangling `selector_arg_id`, a selector kind the evaluator does not implement, a role
  or group whose row has been deleted — each is the empty set, and an expression that cannot be
  evaluated reaches nobody (§*Evaluation*). **Fail closed on the allow side, and note that the same rule
  is fail-*open* looking, which is why it is stated with its two halves rather than as a slogan: a
  failed operand on the `+` or `*` side narrows the set, and a failed operand on the `-` side widens
  it** ([D-106](../decisions/round-11-12.md#d-106--a-failed-operand-stays-the-empty-set-the-missing-half-was-a-report-not-a-refusal)).
  `-` is the only operator whose failed operand can grant, so *fail closed* names a direction and not a
  safe state: `EVERYONE - PERSON(x)` with a dead `x` is fail-closed **and** a lockout of everybody in
  one breath. **Why** the answer stays the empty set: a silent widening is discovered in an audit two
  years late, so the visibility goes on a page instead — **an audience carrying a leaf that does not
  resolve is listed for its owner**, in a second column of the report
  [F-21](../open-questions.md#f-21)
  already asks for. **No save is refused because a leaf is broken, and no expression is pinned to the
  set it resolved to when it was saved** — pinning would make the stored expression a ceiling on truth,
  and a grant would freeze at the shape it had on the day somebody typed it. **The report is a query
  with an owner and is a convention, not a guard**
  ([D-081](../decisions/round-06.md#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now)).
  **The line is narrower than it looks: an operand that resolves fine and simply does not contain the
  person is not on that list.** A person with no birth date is not a failed `OLDER(18)` — the operand
  resolves to the people who are that age on the checked date, and the person is not among them,
  exactly as a person with no membership row is not a failed `MEMBERS`. **A missing attribute on the
  person being asked about is an ordinary answer, not a resolution failure**, and a report that
  conflated the two would page about every incomplete import in the country. What keeps the wide case
  from arriving by ordinary administration is that **an audience a live grant names cannot be ended or
  deleted** (§8, in [05a](05a-audience-and-grammar.md)).
- **The `AUDIENCE` leaves *are* the reference edges, and there is no edge table**
  ([D-103](../decisions/round-10b.md#d-103--an-audience-may-name-another-audience)). Every
  question about nesting — *does this cycle*, *how deep does this get*, *which grants name this
  audience*, *may this audience be deleted* — is answered by selecting rows from this one table where
  `selector_kind = 'AUDIENCE'`. **The two-directional index that makes that cheap is `(selector_kind,
  selector_arg_id)`**, and it is the second reason the reference is stored as a row rather than parsed
  out of a rendering: an edge inside a string answers none of those questions without a table scan.
- **A node belongs to exactly one tree, and to exactly one audience.** Every row's `audience_id`
  equals its parent's; there is exactly one row with no parent; no row is its own descendant. Check 10
  (§11) counts these. **Nesting does not soften this**: `AUDIENCE(x)` points a *whole tree* at another
  whole tree. It is not a node shared between two expressions, and the rule above about one parent and
  no sharing table is exactly what keeps `AUDIENCE()` from being a node-sharing design by another name.
- **The whole tree is written together.** An expression is one act of authorship, so inserting a
  grant's audience inserts its nodes in one transaction, and deleting an audience deletes them.
  A node whose parent arrives in a later transaction is an orphan, and an orphan is check 10, not a
  transient state to be tolerated.

**Why a tree and not a string, and why not a normal form.** A string would have to be re-parsed on
every check and would make the arity rules text-processing rather than row-writing. A **union of
terms** needs the normalizer — distribute, dedupe, sort, survive blow-up — and would rewrite the
writer's brackets behind their back. The tree needs one fifteen-line evaluator and keeps the brackets;
`(A + B) * C` costs nothing.

**What that costs.** Two expressions with the same meaning are two different row sets, so *"you already
granted exactly this set on that row"* does not fall out of storage — **and that is accepted, not
mitigated: nothing computes the semantic equality of two expressions**, so no warning fires when a
second audience means what a first one means
([F-14](../open-questions.md#f-14),
[D-110](../decisions/round-13.md#d-110--the-expression-is-the-record-of-whom-a-grant-reached)). The
same reasoning is why *"this selector reaches nobody"* belongs to the editor preview that has to exist
anyway (§*The cost of composition*) rather than to a syntactic check the tree cannot perform — a tree
catches `X - X` on one node and nothing else.

### `audience_member`, re-roled as the `LIST` leaf — deleted by D-105

**`audience_member` is not a table and `LIST` is not an operand**
([D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)).
A hand-written set of people is written in the expression, as `PERSON(a) + PERSON(b)`, in the same
place every other set in this language is written; a set that is dated and shared between grants is a
`person_group`. **The heading is kept so that pages linking here land on the guardrail rather than on
nothing.** None of these are in the system: a per-person `valid_from` / `valid_to` half-open period with
its no-overlap rule, an `added_by` naming who put one person there, an editor rendering an operand as
`LIST (this audience)`, and a refusal to add a person to a seeded `is_system` audience — adding somebody
to `everyone` is a category error, and with no list there is no row left to refuse, so that one retires
instead of becoming a report. What an expression carries is one period — its grant's — and `created_by`
on a node, which answers *who last saved this tree*.

**Not a roster edit.** The refusal to solve a grant's exception by editing a group roster stands,
because the hazard is real: making three people members of `GROUP(kitchen)` in order to reach one grant
**edits a roster that other grants read**, and it creates a row in the group browser that is not a group
anybody talks about. [D-098](../decisions/round-10a.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority)
is the rule that says so — **a group's members are true when no grant points at them** — and
`PERSON(a) + PERSON(b)` is the answer that respects it. **`person_group_member` is the only dated set of
people the system keeps.** The hazards a hand-named person now carries — no per-name date, no per-name
adder, and two writers editing one expression at once — are stated once in
[05a](05a-audience-and-grammar.md), §*What `LIST` is, said plainly*.

### Three named sets, and the one question nesting cannot answer

**`GROUP(x)`, `AUDIENCE(x)` and `PERSON(x)` are all "some people" and none of them is the same kind of
thing** ([D-103](../decisions/round-10b.md#d-103--an-audience-may-name-another-audience)). A
hand-written set of people is not a fourth kind of thing: it is a sum of `PERSON()` leaves
([D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)).

| | `GROUP(x)` | `AUDIENCE(x)` | `PERSON(x)` |
|---|---|---|---|
| What it is | A dated roster somebody maintains | A saved expression, evaluated live | One named person, typed into this expression |
| Who may change who is in it | `person_group.member.manage` | `audience.manage` on that audience | Whoever may edit this expression |
| Does it exist outside a grant? | **Yes** — D-098: a group's members are true with nothing pointing at them | No — it exists to aim a grant | No — and it is not a set anybody maintains |
| *"Was she in it on 1 June 2024?"* | **Answerable**, from the dated rows | **Not answerable** past the audit window | **Not answerable** past the audit window |
| Sensitive as | ⚠ company | 🔒🔒 authority | 🔒 one named person |

**The fourth row is the honest cost.** `GROUP(x)` is materialized, so its past is reconstructable from
its own rows; `AUDIENCE(x)` is a live rule, and its past shape survives only in the audit trail — where
[D-088](../decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)
empties the payloads after 24 months. So **"who could see this child's data in 2024?" is answerable when
the grant pointed at a group and is not answerable when it pointed at a nested audience.** A rule whose
reach cannot be reconstructed is still the right tool for a rule — `MEMBERS` is not going to be replaced
by a roster of everyone — but the gap gets closed by a report, not by pretending the question has an
answer. The report is the save-time listing in §*The cost of composition*, kept over time rather than
shown once; whether that is worth building is registered in §13 and is the same question as
[F-7](../open-questions.md#f-7),
which is **dissolved** (§*The cost of composition*). **A saved snapshot of whom a grant reached is the
only thing that could answer about 2011, and the system keeps none** — the expression is the record, and
it is a rule, not a snapshot
([D-110](../decisions/round-13.md#d-110--the-expression-is-the-record-of-whom-a-grant-reached)).

### Names are one namespace, and reserved words are the other half

**Bare `COUNSELORS` resolves against roles and groups together**, since `ROLE()` and `GROUP()` do not
have to disambiguate — which makes **the name namespace load-bearing**: a name in this system is not a
label, it is what resolves
([D-101](../decisions/round-10b.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree)).
Five rules, and the layer each one lives in is the point:

1. **Names are unique across `role`, `person_group` and `audience.code`** — the third of them because
   `code` is what resolves and `audience.name` is what a screen displays, so `name` is not in the
   namespace ([D-103](../decisions/round-10b.md#d-103--an-audience-may-name-another-audience)). **No
   single constraint spans three tables**, so the write path carries it and integrity check 12 (§11)
   asserts the write path exists —
   [D-081](../decisions/round-06.md#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now)
   wording, because a rule with no database backstop is a convention until a check says otherwise.
2. **Case, whitespace and separators are folded on write**, so `Schuzka 2026-1`, `schuzka_2026_1` and
   `SCHUZKA2026-1` are one name and not three sets that look different in an editor.
3. **Every `selector_type.code` is reserved.** A group called `MEMBERS` is refused at the save rather
   than silently rewriting every expression in the system.
4. **Bare names resolve to exactly two kinds: a role or a group.** An audience is reachable only
   through its own keyword, `AUDIENCE(veterans)` — naming the namespace a third way **without**
   widening bare resolution. **Why:** bare resolution is what keeps stored expressions meaning what
   they meant when they were written (the `audience` rules at the head of §8).
5. **What is stored is always kind + id**, never a name — so **a rename never rewrites a grant**.
   A role renamed still carries everything aimed at it. **`AUDIENCE` obeys this like every other
   leaf**: the resolution happens once, at save, into `selector_arg_id`, and renaming the audience
   afterwards rewrites nothing. **Read the rule for exactly what it says: a *rename* rewrites nothing,
   because a rename leaves the row and its id where they were.** A person **merge** is not a rename —
   it retires an id — and every hand-named person in the system is a leaf holding one, which is the
   next section.

**What is given up:** a name is a security-relevant string. Two organizations that both call something
`leaders` and one of them a *group* and the other a *role* get one namespace deciding which `leaders` a
grant meant, and the answer is that they cannot, because the write path refused the second one at the
save. **An audience code colliding with an office code is in that namespace too**, and it is not
cosmetic: something can name an audience, so a collision is a silent grant.

### A hand-named person is now a keyless reference

**Every hand-named person in the system is a `selector_arg_id`, and that column deliberately has no
foreign key** — [D-011](../decisions/round-01a.md#d-011--scope_id-on-access_grant-is-polymorphic-with-no-foreign-key)'s
accepted trade-off, extended to this column by D-101 and backstopped by an orphan scan rather than by
the database. **This is what makes the requirement below load-bearing.**

**Requirement: a person merge, and a redaction, must repoint every `audience_operand` leaf whose
`selector_arg_id` names the absorbed or erased person, in all five argument kinds that name an entity.**
The merge reassignment table carries the row, the erasure path carries the scan, and the nightly orphan
check (§11, check 2) **is the backstop rather than the mechanism** — a scan that runs the following
morning is not a reassignment, and by the time it reports, an expression has already resolved wrong. It is
[shape 3 of the invariant
register](00a-invariant-register.md#3-the-answer-reads-another-table-a-resolver-or-a-graph) for precisely
the reason the register exists: **the ORM cannot express it, because the column has no key to follow.**

**Why this is not housekeeping.** A leaf that resolves to nobody is the empty set, which **narrows** the
result on the `+` and `*` sides and **widens** it on the `-` side
([D-106](../decisions/round-11-12.md#d-106--a-failed-operand-stays-the-empty-set-the-missing-half-was-a-report-not-a-refusal)),
and this module's own recurring worked example is a subtraction: `EVERYONE - PERSON(x)`.
**Un-repointed, `x` stops subtracting anybody and the grant denies everybody** — reachable by an
ordinary merge rather than by a hand-edited row.

**Why all five kinds, and not just `person`.** The scan is over one column, and the column does not know
what it points at. A merge is the case that made the requirement, but an erased event, a deleted group,
a retired office or an ended audience leave the identical orphan behind them, and **writing the rule as
"`PERSON` leaves only" would put the hazard straight back where it is sitting.** The five kinds a scan
walks are `person`, `role`, `person_group`, `event` and `audience`. **`selector_type.argument_type` takes
six values: five of them entity kinds, and the sixth `integer`, the argument of `OLDER` and `YOUNGER`**
([D-107](../decisions/round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded))
— **and the scans walk the five.** This is the one place to say why, because it looks like an omission
and is not: **an `18` in `selector_arg_id` is not a reference**, so there is no row behind it to merge
away, none to erase, none for a cascade to find and none for the orphan scan to report. **The number this
section is about — how many keyless columns check 2 walks, which is two — does not move, and it is a count of
*keys*: a scalar stored in a key's column is not one. **The whole design has seven keyless columns, not two,
and [00 §9](00-conventions.md#9-referential-integrity-rules) is where that count lives;** the other five
belong to the two trails and to a merge conflict, none of which holds an operand argument. **Nobody has
to add a `person.birth_date` branch to a merge script, and anyone who does has misread this paragraph.**

### What each operand costs

What is worth comparing is whether a set is **derived** or **kept**. Every operand in the registry reads
a fact that exists independently of the expression:

| | A derived operand |
|---|---|
| Which | **Twelve of the thirteen** — `EVERYONE`, `MEMBERS`, `OLDER`, `YOUNGER`, `ROLE`, `GROUP`, `ATTENDED`, `PLACED`, `CONFIRMED`, `ON_WAITLIST`, `ORGANIZERS` and `AUDIENCE` — are **derived from another expression rather than from a fact table**, which makes `AUDIENCE` the odd one and the reason this table has a footnote below. The thirteenth, `PERSON`, is neither derived nor kept: see below. **`OLDER` and `YOUNGER` sit here on the strength of the row below them** — a live read of a stored fact at the checked date, exactly like `MEMBERS` reading `membership` — **but they are the first whose answer to *"when does someone join?"* is not "when a row is written"**: the row was written at birth, and the set changes on its own. §*The cost of composition* carries what that costs |
| How evaluated | A live read of the fact that defines it, at the checked date |
| When someone joins | They are in it immediately — **automatically** |
| Maintenance | None. **It cannot rot.** |
| Membership stored? | No — and therefore not retrievable after the facts move (§*The cost of composition*) |
| Examples | "everyone who holds a place on this event", "the counselors", "anyone thirteen or older" |

**Nothing is kept.** No operand's members are rows somebody maintains, so there is no per-person date,
no no-overlap rule and no staleness warning anywhere in this module: `LIST`, the one operand whose
members were maintained rows, is not in the model
([D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)).
A set that is dated, shared and maintained by hand is a `person_group`
(§*`audience_member`, re-roled as the `LIST` leaf*).

**`PERSON(x)` is not a kept operand either, and pretending it is would lose the distinction.** It is a
**constant**: the answer is written into the leaf itself, so it reads no fact table *and* maintains no
roster. It cannot rot the way a kept set rots — nobody has to remove anybody, because nobody is *in* it
except the one person named. What it can do is **dangle**, which is a different failure with a sharper
edge, and §*A hand-named person is now a keyless reference* is where that is handled.

**Prefer a derived operand where one exists.** A grant to `PLACED` gets the right answer forever: a new
registrant is covered the moment they are placed, and someone who withdraws stops being covered, with no
rows to maintain. A grant listing names by hand does not do that: **a sum of `PERSON()` leaves goes
stale, one leaf at a time.** So the choice is a size question and not a question about the kind of set:
**a set of people big enough to be a roster is a `person_group`, and a set small enough to type is a sum
of `PERSON()` leaves**, and one expression may hold the derived set and the names it cannot reach in one
grant
([D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)'s
judgement, registered where missing operands are registered in [../open-questions.md](../open-questions.md)).

**Composition is written in the expression, not in an edge.** `GROUP(kitchen) + ROLE(troop_staff)`
composes as much as an inclusion edge ever did, because a group's membership **is** its dated rows
([D-098](../decisions/round-10a.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority)),
and reusing a whole saved expression is `AUDIENCE(<code>)`
([D-103](../decisions/round-10b.md#d-103--an-audience-may-name-another-audience)). So there is no
transitive walk over a graph and no `include_depth_limit` to enforce it with — the guard that came back
is the write-time reachability walk across audiences (§*The expression tree*), which is smaller
machinery than the table it replaced. `AUDIENCE()` is also the only arm that names **a decision about
access** rather than people, so it is the only one that can say *"the same people that grant may see the
fee ledger, plus the accountant"*.

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

1. The grant names an audience; a grant naming one person, or one registered key, is not this question's
   business — neither is a set, so neither is evaluated here at all
   ([D-117](../decisions/round-16.md#d-117--a-key-is-never-inside-an-expression-thirteen-selectors-and-none-of-them-can-name-one)).
2. Its `scope_type` is the scope type being checked, and its `scope_id` matches the scope id being
   checked, with an absent id counting as equal to an absent checked id.
3. Its `effect` is `allow` — denies belong to the channel that runs first (§10).
4. It has not been revoked.
5. It has started as of the checked date and has not ended on that date.
6. Its `permission_id` **is** the checked permission — or is `system.admin`, the one code that means
   everything (§2). **There is no `permission_level` row to consult and no rank to compare**: a grant
   answers one code ([D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)).
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
   with one more branch. **The recursion is bounded by nothing, and the read path gets no depth cap and
   no cycle check of its own.** **Why:** a cap applied while reading becomes the thing that decides who
   a grant reaches, so the refusal is deliberate
   ([D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other))
   — which is why the acyclicity walk at save (§*The expression tree*) is the only thing standing
   between a saved expression and one that never finishes evaluating.
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
   `selector_kind` no evaluator implements, or whose tree cannot be assembled **reaches nobody**, and a
   leaf whose argument names a person who has been merged away is on this list too — which is why
   §*A hand-named person is now a keyless reference* makes repointing a requirement rather than a
   nicety. **An absent selector is a fault, not a hint.** Nothing here falls back to "so it probably
   includes everyone", and nothing here guesses the half of a tree it could resolve: **an expression
   that cannot be evaluated is an empty set**, which is the direction this model fails in everywhere
   else — default deny (§10), deny absolute (channel 0), and an audience whose rule was quietly wrong
   reaching nobody rather than everybody. **A cycle through `AUDIENCE` leaves is refused where it is
   written**, so an evaluator meeting one is meeting data that should not exist, and the rule that
   covers that is this one — reach nobody, do not recurse forever and do not guess. **The reason the
   write-path check has to be a cross-audience reachability walk and not a parent-chain walk is exactly
   here** (check 15): if the read path is ever the thing that notices a cycle, some grant has already
   been evaluated wrong.

**Note that `ORGANIZERS` and `ROLE` read their tables without themselves being authority grants.**
Membership in an audience confers nothing on its own — it only decides whether *this* grant, which
someone already created deliberately, reaches this person. An appointed organizer does not become able
to do anything by being on the roster; they become able to do exactly what the grant aimed at
`ORGANIZERS` says, on that event. **This is [D-062](../decisions/round-05.md#d-062--organizers-are-appointed-on-the-event-not-granted)
standing untouched**, and it is the sentence D-102 leans on: the appointment is *aimed at* by grants
rather than special-cased inside the resolver.

### What audiences do **not** do

- **They are not a permission.** Being in an audience is not authority; it is membership of a
  set. All authority still comes from a grant.
- **They cannot reach guardianship at all.** A guardian's authority is not a set of codes an audience
  could extend one at a time: it is a `right_level` of `none` / `view` / `write` on the live
  `guardianship` row (§10,
  [D-074](../decisions/round-06.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular)),
  and it reaches **any action about that child** — wider than any grant could assemble, and narrower in
  the only direction that matters, because it reaches nothing that is not about the child. **Neither
  `GUARDIANS` nor `guardianship_permission` is in the model**
  ([D-113](../decisions/round-13.md#d-113--the-guardianship-channel-has-no-expression-guardians-is-not-a-selector)).
  So an audience neither opens nor closes guardianship: **a deny still overrides the channel, because
  the deny channel runs first and is scope-independent (§10)** — which is the one thing an audience can
  do to it. What an audience *can* do with a guardian is be a group the organization keeps: the six
  contact adults of these children are `GROUP(x)`, a roster with a lifetime and no authority
  ([D-098](../decisions/round-10a.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority))
  — a different fact, written down, about different people.
- **They nest, through `AUDIENCE(x)` alone**
  ([D-103](../decisions/round-10b.md#d-103--an-audience-may-name-another-audience)). **A cycle is
  impossible to store and possible to write**, so the guard is a cross-audience reachability walk on the
  save path rather than a shape argument (§*The expression tree*, check 15), and the thing to remember
  is that nesting buys **reuse of a composite rule**: *"the kitchen crew plus whoever leads this pack"*
  is one grant either way, and `AUDIENCE()` adds the case that could not be expressed without it rather
  than undoing it.
- **Nesting is not sharing.** `AUDIENCE(x)` evaluates the whole of another audience's expression; it
  does not splice one of its nodes into this tree. **Two expressions never share a row**, so editing a
  node inside `veterans` changes exactly the grants that name `veterans` and no others — which is the
  distinction that keeps this from being the node-sharing design this corpus refuses.
- **`everyone` is genuinely everyone**, including people with no account and no membership.
  It is the right target for a public event page and the wrong one for anything else. **And it is
  reachable by `+` from inside any expression**: nothing stops an expression from unioning the seeded
  `EVERYONE` operand, and a writer with `audience.manage` can widen a grant to the whole world in one
  edit. That is not a hole in the model — holding `EVERYONE` directly is already legal and already
  alarmed (check 8, §11) — it is that a language with union in it makes the same reach available
  without even pretending to compose it carefully. The mitigation is the editor's expanded set below,
  not a rule about which operands may appear where.
- **A role cannot be held by a rule.** `role_holder` names one person, and
  [F-12](../open-questions.md#f-12) **is closed by
  [D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape),
  and its answer is no** — a derived holder list cannot answer "who was treasurer in 2023", and an
  office record that cannot answer that is not an office record. Grants aim **at** roles; roles are not
  filled **by** grants.
- **An expression cannot compute with a person's attributes**, in the one direction that is still a
  negative. `OLDER(15)` says something about an attribute and it is a row of the registry
  ([D-107](../decisions/round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)),
  so what is refused is a *term* and not a subject matter: **`AGE >= 15` is not an operand, is not
  expressible, and there is still no open question asking for it**, because there is no comparison
  operator for it to use and no way to add a row from a screen. **What an author may write is what
  shipped**; that, and not the type of the thing written about, is the closure property §*Author in
  sets* protects. Eligibility is capability
  ([D-060](../decisions/round-05.md#d-060--eligibility-is-capability-there-is-no-separate-rule-engine)):
  **no rule is evaluated outside `can()`, no eligibility rule table exists, and the system gates nobody
  on its own — an age rule is a grant somebody wrote, visible in the grant list, revocable like one.**

### The cost of composition

**A grant's reach stops being visible in the row that grants it.** Derived membership is not stored —
D-042 accepted that, and these documents recommend it, because a rule does not rot the way a list does.
Most of the permission answer is therefore recomputed rather than recorded, and composition makes that
sharper.

- **The editor must show the set a grant actually reaches, expanded** — the people, not the
  expression's text — and it is a requirement on the screen rather than a nicety. Composition turns a
  three-deep expression into a silent widening, and the person saving the grant is looking at one row
  that mentions no person at all. **This is the same posture as the resolver's in §10: the answer
  exists, it is just not stored, so somewhere has to compute it in front of a human** — and here the
  human is the only control there is.
- **The preview is per-item, which it structurally cannot be from the grant alone**
  ([D-102](../decisions/round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)).
  `PLACED` means different people on different events, so "who does this grant reach?" is unanswerable
  as written when the expression contains a bound operand. **The preview is therefore computed for an
  item and says so on screen** — an honest screen names the event whose people it is showing — and a
  bound operand may never answer for another item: **the item is a parameter of the compiled predicate**
  (§10), which is one requirement with one fewer place to get it wrong. This is the one place where
  D-102's convenience costs a screen an editor's design has to notice, and §13 keeps it open rather than
  assuming it away.
- **Editing an audience changes grants you did not make, and the screen has to say so before it
  commits** ([D-103](../decisions/round-10b.md#d-103--an-audience-may-name-another-audience)).
  Add a person to `AUDIENCE(veterans)` and every grant naming it now reaches them — including grants
  their owners wrote for another purpose, and including grants this editor cannot see because they are
  not theirs. **This is not a new failure mode:** `GROUP(x)` has the same property (D-091), and the
  reason for accepting it there is the reason for accepting it here — **a named set is worth being
  reusable, and a reusable thing has more than one user.** The mitigation is D-091's, extended to the
  second user: **saving an edit to a referenced audience shows which grants name it, and at what depth,
  before it commits.** It is one indexed query over the leaf rows (§*The expression tree*), and it
  doubles as the report that partially closes the history gap in §*Three named sets*. **D-103 registers
  this as an assumption rather than a measured fact** — cheap at this organization's size because the
  edges are indexed rows in the table that already holds every expression, unverified at any size, and
  **a slow save screen is a real risk if the import corpus's row-count estimates turn out wrong**. §13
  keeps it.
- **"Who could read this in 2023?" has no owner.** The audit trail holds the change that made it true
  only until [D-088](../decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)
  empties those payloads after 24 months, and derived membership is not stored at all. After two years
  the question is answered by re-running expressions against state that has itself moved on, and it is
  answered with today's confidence. **That is the flat statement of the limitation: a historical check
  is re-running today's expressions over whatever state survives.** [F-7](../open-questions.md#f-7)
  is **dissolved, not answered**: a nightly rebuild of cached answers and a nightly materialized
  `effective_permission` table turned out to be one job with two names, and neither would have made
  history answerable — a table of *today's* answers, rebuilt nightly, is as blind to 2011 as no table
  is. Nothing computes a snapshot of whom a grant reached
  ([D-110](../decisions/round-13.md#d-110--the-expression-is-the-record-of-whom-a-grant-reached)).
  **History has no owner, and that is recorded as a limit rather than a to-do.**
- **Something has to keep count of how big expressions get, because nothing refuses them** (§*The
  expression tree* states the rule and what replaced the check). The standing report of the widest and
  deepest audiences, their closure size and their cost per check is kept running rather than computed
  once at save, and **it has no CI behind it — a convention, not a guard**
  ([D-081](../decisions/round-06.md#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now));
  the failure mode of a report nobody reads is that it stops being read and nothing else happens. **Who
  reads it is answered with the cheapest object available: not a report and not a job, a
  [tab](../open-questions.md#f-21)
  on the permissions page.** The answer to *who reads it* is therefore *nobody, necessarily* — a tab is
  read by whoever opens it — and that is a decision rather than an oversight, with
  [D-112](../decisions/round-13.md#d-112--the-systems-scale-is-stated-hundreds-of-people-tens-of-registrants-per-event)'s
  stated size underneath it and a trigger on top. The save-time walk that computes the numbers is the
  same walk that checks acyclicity (§*The expression tree*), so the number costs nothing extra to
  obtain; what costs something is deciding to look at it.

---

*Decisions behind this page: D-011, D-042, D-060, D-062, D-074, D-081, D-088, D-091, D-098, D-099, D-100, D-101, D-102, D-103, D-105, D-106, D-107, D-110, D-112, D-113, D-114.*
