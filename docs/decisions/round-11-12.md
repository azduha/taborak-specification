# Decision Log — Refinement rounds 11 and 12 (D-105 … D-108)

> No `LIST`, no depth bound, and an operand that may name a stored fact — age among them.

[Refinement round 10 — the deletions, part 2 (D-101 … D-104) ←](round-10b.md) | [All decisions](index.md) | [Refinement round 13 (D-109 … D-113) →](round-13.md)

---

## D-105 — There are no `LIST`s: a hand-written set is an expression like any other

**Status:** decided — from your request, with both open points ruled on the same day.
**Date:** refinement round 11

**Ask:** *"Let's completely remove an option to specify people in an audience in a table (as a `LIST`) and
instead list them all in a rule (eg. `PERSON(a) + PERSON(b)`). Will it cause any issues? It feels like a
great simplification."* **Ruled on:** dated names → **no**; the depth bound → **removed, and the tree stored
exactly as the writer wrote it.**

**Follows:** [D-011](round-01a.md#d-011--scope_id-on-access_grant-is-polymorphic-with-no-foreign-key),
[D-048](round-04.md#d-048--the-renewal-window-is-60-days-and-is-a-configuration-parameter),
[D-088](round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short),
[D-091](round-09.md#d-091--a-permission-group-is-a-rule-and-a-list-at-once-and-a-rule-may-name-another-group),
[D-098](round-10a.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority),
[D-099](round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality),
[D-101](round-10b.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree),
[D-103](round-10b.md#d-103--an-audience-may-name-another-audience),
[D-104](round-10b.md#d-104--a-permission-codes-last-segment-is-an-action-and-a-registry-that-prose-contradicts-is-a-fiction).

### 1. What is deleted, and the embarrassment that makes it easy

`audience_member` is deleted, and with it the `LIST` operand and its seed row. **The selector registry is
twelve rows.** A hand-written set of people is now written where every other set is written — in the
expression, as `PERSON(a) + PERSON(b)` — and it parses today, which is the whole reason this is a deletion
rather than a redesign.

The embarrassing part, recorded because it is the same shape as
[D-104](round-10b.md#d-104--a-permission-codes-last-segment-is-an-action-and-a-registry-that-prose-contradicts-is-a-fiction)'s
finding: **`LIST` was kept by D-101 on the stated grounds that "a hand-written set of three people is not
derivable from anything", and D-101 was amended, late in the same round, to add `PERSON(x)`** — the operand
that names exactly one human being. That amendment removed the table's reason and the round did not notice,
so the last round ended with two ways to write the same set of names and a page of prose
([data-model/05 §8, *What `LIST` is, said plainly — withdrawn by D-105*](../data-model/05-authorization.md#what-list-is-said-plainly--withdrawn-by-d-105))
arguing that they were **two operands and not one wearing two names**. They were one. The argument was
correct about the semantics and wrong about the conclusion, and the difference between those two is a table
nobody needs.

**What survives untouched, because the hazard it guarded is real and unchanged:** naming three people inside
a grant must not mean making them members of a `person_group`. A group's members are true when no grant
points at them ([D-098](round-10a.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority));
editing one to move one grant's reach edits a roster other grants read. The old expression
`(GROUP(kitchen) + LIST) - PERSON(a) - PERSON(b)` becomes `(GROUP(kitchen) + PERSON(honza)) - PERSON(a) - PERSON(b)`:
**same meaning, one fewer kind of thing, and the reason not to use a group is unchanged.**

### 2. What is genuinely given up, written as lost rather than as managed

Four things go, and the first three are not recovered by anything in this decision.

**Per-person dates.** `audience_member` carried `valid_from` / `valid_to` with the half-open no-overlap rule;
`audience_operand` carries no period and gains none. **You ruled no**: a person is in the audience or not, and
a June-to-August exception is **its own grant with its own period**, which is what
[D-099](round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)'s shape is for.
The cost is exact: where there was one audience and one grant there are now two grants, and a reviewer asking
*"what does Honza have?"* must find both. **A grant aimed at one person is no longer a curiosity, it is the
ordinary expression of a temporary exception**, which is worth saying because for ten rounds the model's
answer to that was a row in a side table.

**One precondition on that equivalence, because it is not free in every shape.** A grant carries a scope and a
permission as well as a period, so the second grant restates the dated name **only where the first grant's
scope and permission are the ones the exception needs.** *"These three may see the answers until August"*
beside an organization-wide grant restates cleanly; the same sentence meant for one camp does not, because the
second grant must be aimed at that camp, and is then a different reach in two dimensions at once rather than a
dated copy of the first. **That is not an argument for keeping the dates** — the row that carried them could
not express the scope split either, it only hid it inside a list — but *"the language can still state the same
facts"* is true **per scope and permission**, and printing it unqualified would be exactly the kind of sentence
this log has spent two rounds catching itself write.

**Per-name provenance.** `added_by` named who put one person on one list. What remains is `created_by` on a
node, which — because saving an expression rewrites its rows — answers *"who last saved this tree"* and not
*"who added Honza"*. The act is in `audit_log` with its actor taken from the request context, as it is for
every other write; that is a real record and a weaker one, and the difference shows up only when two people
have edited the same audience.

**The list's past.** With the table and its dates gone, *"who was on this audience in 2026"* is a
recomputation over audit payloads, and those payloads expire after 24 months
([D-088](round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)). So the question stops being
answerable in 2028. This is not new exposure of a kind the model had avoided: D-091 already turned *"who
could read this in 2023"* into a recomputation, and
[F-17](../open-questions.md#f-17--closed--the-expression-is-the-record-so-a-nested-audiences-past-is-recomputed-and-never-promised)
already states it for the nested kind of audience. It is the same hole, one table wider, and it is accepted
rather than papered over.

**Two writers at once.** Adding a name was an insert; two clerks adding two people to one audience could not
collide. Adding a name is now an edit of the audience's expression, so they can: **whoever implements the
editor owes this an optimistic-concurrency check or a queue**, and a silent lost update here quietly removes
somebody's access. Nothing in the schema will notice. It is stated here rather than in the rules because the
table whose absence caused it no longer exists to carry a note.

**One thing is lost that does not cost anything today,** and is listed so it is not re-derived as a bug in two
years: there was a moment when the list could have had its own permission — *may tick names on this audience*
without *may rewrite the rule*. It never got one. [Permission-catalog §5a](../appendix/permission-catalog.md#5a-groups-roles-and-audiences)
wrote `audience.manage` as one code covering *"change its expression, or the `LIST` a `LIST` leaf resolves
to"*, so the split option existed in the data model and not in the authorization model, and this decision
closes the option in the data model too. If a real need for a names-only write ever appears, it is a new
question about the editor, not an argument that this decision was wrong.

### 3. The depth bound is removed, and the sentence it was holding up

**`selector_depth_limit` is deleted**, along with the stored-column argument that justified its shape
([D-048](round-04.md#d-048--the-renewal-window-is-60-days-and-is-a-configuration-parameter) is the precedent this design
cites for it — a bound somebody may want to change belongs in a column, because a job containing the literal
`3` has turned a parameter back into a constant). The precedent outlives the column: there is no parameter left
to place. **The tree is stored exactly as the
writer wrote it:** one row of two operands and one operator per node, left-to-right, no rebalancing — which
matters because rebalancing was the tempting engineering answer here, and a rebalanced tree is a different
expression than the one a person wrote, which is the reason the storage exists at all.

**One phrase above needs separating from a neighbouring ruling, because the two read as one sentence and
are not.** *"Stored as the writer wrote it"* is a claim about **the tree's shape**: no rebalancing, no
reassociation, no reordering — the structure is the structure the writer made. It is **not** a claim that the
stored string is what was typed: [D-101](round-10b.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree)
rules that the canonical rendering brackets every bracket and that the editor rewrites typed input into that
form before saving, so what is stored is a **canonical rendering of the writer's tree**, and its shape is
still the writer's. **The distinction has one customer, and it is the one that matters here**: adding brackets
changes no expression, while reassociating one — or sorting children into a canonical order to compare two
audiences for equality, which
[F-14](../open-questions.md#f-14--closed--nothing-computes-semantic-equality-of-two-expressions-and-nothing-will) floats —
changes exactly the thing this paragraph refuses to change. **This entry therefore does not settle F-14; it
draws the line F-14 has to be decided on one side of**, and says so rather than letting "as written" be read
as an answer to a question it was not asked.

**What has to be said about the consequence, because it is the real cost of this ruling and not a footnote:**
for the whole life of this design, one property of authorization checks was that they cost a bounded amount.
That property came from here. With no bound on height and no bound ever asserted on breadth, **the size of an
audience's expansion is now bounded only by acyclicity**, and:

- The save-time walks change role. The cycle walk — inside the tree, and **across audiences** through every
  `AUDIENCE(x)` leaf, which is the one D-103 made necessary — **survives and becomes the only structural
  guard there is.** It must not be relaxed alongside the bound; an expansion that never terminates is the
  failure the removed bound was never protecting against anyway.
- The read path still gets **no** depth cap and **no** cycle check. That refusal was argued as *"the cap
  becomes the thing that decides who a grant reaches"*, and it stands — but it used to be a back-up for a
  guard that existed at save time. **Now it is the whole design**, so the sentence *"a check costs a bounded
  amount"* is deleted from the properties of this system, and what replaces it is the standing report of the
  widest and deepest audiences and their per-check cost, ~~plus the operand cache~~. **One of those two legs was
  removed the round after this one**: [D-114](round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation)
  deleted the cached answers and the operand cache was keyed *per person* — `(person, selector_kind,
  selector_arg_id[, item])` — so it went with them, and what is left on the read path is a **compilation** cache,
  which removes parsing and name resolution from a check but not the reads, and a memo that dies with the request.
  **So this bullet's arithmetic got worse by one control while its prose kept listing two, and the correction is
  recorded here rather than left for a reader to notice: the report is now the only thing between an unbounded
  expression and a slow screen.** **A report, with no CI behind
  it — a convention, not a guard**, in D-081's words, and it is the third control of this shape the
  authorization module now depends on. **Round 14 is the round that made it carry more.**
- The invariant *"depth must be refused at save, over the expanded tree"* retires as an invariant and survives
  as the report above. Retiring it is D-081's case exactly: the rule's name outlives the mechanism, and the
  text must say which of the two happened.
- The existing sentence that breaks is the one claiming the number of reads per check is *"bounded by rule (the
  same `selector_depth_limit`) and known at save time"*. It becomes: one indexed read per audience in the
  closure, **closure size discovered by walking it at save, not bounded by a number**.
- Canonical form still prints every bracket — that ruling stands, and its cost is now visible: **a twenty-name
  hand-typed sum prints as nineteen nested pairs of brackets.** Storage and display both say what was
  written, which is what was asked for. If that turns out unreadable, the answer is that a set of people big
  enough to be unreadable is a `person_group`, and
  [F-5](../open-questions.md#f-5--closed--nothing-is-missing-from-the-registry-and-the-last-gap-was-a-selector-that-should-not-have-been-in-it)'s neighbourhood is
  where that judgement gets registered — not a flattening rule invented in advance.

### 4. The thing this change makes load-bearing, which no page required before

`PERSON(x)` leaves used to be a curiosity: the hand-typed people lived in `audience_member`, whose
`person_id` is an ordinary foreign key. Now **every hand-named person in the system is a
`selector_arg_id`, and that column deliberately has no foreign key**
([D-011](round-01a.md#d-011--scope_id-on-access_grant-is-polymorphic-with-no-foreign-key)'s accepted trade-off, backstopped
by an orphan scan rather than by the database).

So a person who is merged away leaves leaves. A leaf that resolves to nobody is the empty set, which is
**quiet on the allow side and loud on the deny side**, and the docs' own worked example is a subtraction:
`EVERYONE - PERSON(x)`. Un-merged, `x` stops subtracting anybody and the grant denies everybody — the failure
this module has been pointing at for two rounds, now reachable by an ordinary merge.

**Requirement, and it is new:** a **person merge and a redaction must repoint every `audience_operand` leaf**
whose `selector_arg_id` names the absorbed or erased person, in all five argument kinds (`person`, `role`,
`person_group`, `event`, `audience`) — the merge reassignment table gains the row, the erasure path gains the
scan, and the nightly orphan check becomes the backstop rather than the only mechanism. It belongs to
[F-10](../open-questions.md#f-10--which-invariants-the-orm-cannot-express-and-who-writes-those)'s register for the reason that
register exists: **the ORM cannot express it, because the column has no key to follow.** Nothing in the corpus
required this before, and it was defensible before only because the volume of hand-named people was in a table
that had a key.

**And the same failure is reachable by typing, which is the ordinary path; the merge is the rare one.** Before
this round, naming a person by hand was an insert into a keyed table, and an insert could not name nobody —
the database refused it. Now a `PERSON(x)` leaf is a value in a keyless column, so **a mistyped, stale or
half-deleted argument resolves to nobody on the day it is saved**, and on the `-` side of an expression that
means the grant is **wider** than its author wrote, silently. The orphan scan does not catch this one, because
the person row it would look for exists; the id is simply not the one anybody meant. **What closes it is the
preview D-091 already requires and nothing else**: the editor shows the resolved people before the save, and a
subtraction that subtracts nobody is visible on that screen as a subtraction that subtracts nobody. **No new
screen and no new check are added here** — the point is that the preview, bought as a control over *reach*, is
now also the only control over whether a hand-typed name resolves, and whoever builds the editor should know
that a preview they may be tempted to make lazy, cached or skippable is carrying a second duty it was never
argued for. **[F-15](../open-questions.md#f-15--closed--the-per-item-preview-is-cheap-at-the-stated-size-and-this-is-what-reopens-it)
is where that tension is registered**, and this entry names it rather than resolving it.

### 5. What got simpler, counted

- **Twelve registry rows, and every one of them is a rule about people or takes an argument** — the operand
  with neither is gone, so the registry has no special case left to explain.
- The four-way comparison `GROUP(x)` / `AUDIENCE(x)` / `LIST` / `PERSON(x)` is a three-way one, and the third
  and fourth are now "an office's holders, a group's roster, an audience's expression" with no fourth shape.
- `audience_member`'s rules go with it: the no-overlap rule, the refusal to add a person to an `is_system`
  audience, the editor affordance that rendered `LIST (this audience)`, and one entry in the cache-invalidation
  trigger list.
- §13's open question about renaming `LIST` to `ADDED` is **moot, not answered**, and is deleted rather than
  closed.
- D-091's list arm — the last of its three arms still standing — is closed outright.
- One of the two dated-member tables the design apologises for is gone, so the kept-duplication argument
  D-080 would raise has one fewer instance to explain.

**Migration, and where it bites:** no seeded audience and no import used `LIST`, so for a fresh database this
is a table drop and one fewer seed row. Any *existing* audience whose expression names `LIST` has to be
rewritten by hand, **and rewriting an expression changes who a grant reaches** — so the migration prints the
resolved set before and after for every audience it touches, which is the same report
[D-104](round-10b.md#d-104--a-permission-codes-last-segment-is-an-action-and-a-registry-that-prose-contradicts-is-a-fiction)
adopted as its remedy, run once, on the rows this migration puts at risk.

---

## D-106 — A failed operand stays the empty set; the missing half was a report, not a refusal

**Status:** decided (from your answer)
**Date:** refinement round 12
**Amends:** the failure semantics described in
[D-101](round-10b.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree) and written out in
[data-model/05 §8](../data-model/05-authorization.md#the-selector-registry)

**Decision.** Nothing about resolution changes. An operand whose argument names nothing — a deleted
person, a renamed role, a merged-away id — **is the empty set**, and `EVERYONE - PERSON(x)` with a dead
`x` therefore still denies everybody. What is added is not a rule but a page: **an audience with a leaf
that does not resolve is listed**, for the audience's owner, on the same report
[F-21](../open-questions.md#f-21--closed--no-report-a-tab-on-the-permissions-page-and-unbounded-cost-is-accepted-at-the-stated-size)
already asked for, in a second column. No save is refused because a leaf is broken. No expression is
pinned. The failure stays fail-closed and stops being silent.

**Why.** Your answer, in full: *"It still feels unnecessary, it is enough to notify, do not deny (it
might cause very advanced problems more, than it gains to be loud)."*

**Two fixes were on the table and both are declined here, so that neither is proposed again.**

1. **"Treat an unresolvable id as the named one"** — resolve `PERSON(x)` to the person by name when the
   id is gone. Declined: it invents a person the model does not have, and it invents them *on the widening
   side*, which is the one place a wrong answer grants instead of withholds.
2. **"Never wider than saved"** — at save time, record the resolved set and refuse any later resolution
   that reaches more people than the saved one. Declined, and it is worth seeing why: it makes the
   *stored expression* a ceiling on truth, so a person who leaves a unit cannot be removed from what a
   grant means without a write, and a grant silently freezes at the shape it had on the day it was saved.
   It buys a guarantee nobody asked for by breaking the one property an expression has over a snapshot —
   that it means today what it says today.

**The vocabulary is retired, and this is a D-081 case.** The corpus has been saying *"the `-` side is
loud"*, which names a volume where there is only a direction. What is true: **a failed operand on the `+`
or `*` side narrows the set, and a failed operand on the `-` side widens it.** `-` is not noisy; it is the
only operator whose failed operand can grant. Everywhere the corpus says "loud" it should say that, and
everywhere it says "fail closed" it should be clear that *closed* is a direction, not a safe state —
`EVERYONE - PERSON(x)` failing is fail-closed **and** lockout-everybody, in one step.

**The line this entry draws, which is narrower than it looks.** D-106 is about an operand that **cannot be
resolved at all**, because its argument names nothing. It is not about a person who lacks a value. A person
with no birth date is not a failed `OLDER(18)` — the operand resolves perfectly well, to the set of people
who are 18 or older on the date being checked, and that person is simply not in it, exactly as a person with
no membership row is not in `MEMBERS`. **A missing attribute on the person being asked about is not a
resolution failure and never reaches this entry**, which is the distinction the report has to preserve or it
will page about three thousand people with incomplete imports.

**What this costs, said plainly.** A broken leaf on a `-` side denies people with no signal beyond a page
nobody is required to read, and the report is a query with an owner, not a guard — in D-081's phrase,
**a convention, not a guard**. It was offered as one and it is written as one. The reason to accept that is
in [D-107](#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded), which
records the premise that makes a notification enough: the people writing these expressions are the people
who know what they say.

**See:** [domain/06 §6.4](../domain/06-authorization-model.md) for the rules that make the tree safe,
[data-model/05 §8](../data-model/05-authorization.md#the-selector-registry) for where the empty-set rule is
stated, and [F-15](../open-questions.md#f-15--closed--the-per-item-preview-is-cheap-at-the-stated-size-and-this-is-what-reopens-it),
which this does not answer — a report is not a preview and neither is free.

---

## D-107 — The grammar opens: an attribute may be an operand, and the vocabulary stays seeded

**Status:** decided (from your answer)
**Date:** refinement round 12
**Amends:** [D-060](round-05.md#d-060--eligibility-is-capability-there-is-no-separate-rule-engine), whose stated test
for what an operand may be is deleted here; [D-101](round-10b.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree)'s
grammar; [D-105](#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)'s count

**Decision, in five clauses.**

1. **The tree grows attribute leaves.** Two seeded operands arrive — `OLDER(n)` and `YOUNGER(n)` — read
   against the person's birth date **as of the date the check is made**. The registry has fourteen rows —
   **thirteen as this entry is being re-read**, `GUARDIANS` having left in
   [D-113](round-13.md#d-113--the-guardianship-channel-has-no-expression-guardians-is-not-a-selector); the number stays
   printed here because growing the table by two is the whole content of this clause, and it is the only
   measurement in it.
2. **The operators do not change at all.** `+ - *` are the only operators this language has, and
   `OLDER`/`YOUNGER` are just two more operands composed by them — `MEMBERS * OLDER(13) * YOUNGER(19)`, a band,
   is the same shape as `MEMBERS * GROUP(cubs) * PERSON(a)`. **There is no comparison operator**: no `>=`, no
   `<`, no bare `AGE`. The boolean spellings `&`, `|` and `!` were put to this language and **declined**;
   §Why the operators stayed three is the record of that, since this entry was first written granting them.
3. **D-060 survives; its sentence does not.** See below — this is the load-bearing clause.
4. **A selector's membership may change with no write, by ruling.** Recorded in §Time below.
5. **The premise is written down.** Recorded in §Authors below, with the two things it does not buy.

**Why the gate opened, in the words that opened it.** Asked whether the boolean grammar could be given
attribute operands, the answer came back as a question first: *"Can the grammar still work with the sets?
`OLDER(18)` is still a set of people."* It is, and that question is the whole decision, because the corpus's
argument against admitting age was never about age:

> *"an operand must be a named, materializable set of people. An attribute is not a set of people.
> Guardianship is (`GUARDIANS(x)` is a set), age is not, and the line falls exactly where D-060 already drew
> it."* — [domain/06 §6](../domain/06-authorization-model.md), until this round

**That sentence is wrong and it is deleted.** `OLDER(18)` denotes the set of people who are eighteen or
older on the date being checked. `MEMBERS` denotes the set of people who pass `is_current_member`.
`GUARDIANS(x)` denotes the set of people who hold a row. **Every operand in the registry is a test with a
set on the other side of it**; a birth-date comparison is not a different kind of thing, it is a test that
reads one column instead of joining one table. The materializability test was therefore never what kept rule
engines out — `MEMBERS` would have failed it too, since nothing stores the member list.

**What was doing the work, and it is kept.** *An operand must be **named**.* Not "must be a set" —
**must be a row**. `OLDER(18)` is in the registry; `AGE >= 18` is not, and cannot be, because the language
has no place to put `>=`. The door D-060 was guarding is now shut by the clause that actually fits it:
**a writer may compose seeded operands and nothing else.** D-060's decision — no eligibility rule table, no
prerequisite system, no rule evaluated outside `can()` — is untouched, and its `**Decision.**` paragraph is
amended rather than replaced, because *"no age gate"* was its plainest consequence and is now false in the
plain sense and true in the real one: **there is still no gate the system applies on its own; there is a
vocabulary a person may use to write one.**

**The precedent that made this cheap is already in the corpus, and it is the reason no new storage appeared.**
[data-model/01-identity.md](../data-model/01-identity.md) opens by refusing to store age at all: *"There is no
`is_member`, `member_type`, `is_child`, `is_adult`…"* — because a stored age flag is a fact that goes false at
midnight, and this model's rule about facts that go false is to keep the input (the birth date) and compute the
rest. **Round 12 did not change that rule; it used it.** `OLDER(n)` is where a computed fact is allowed to
live in this design — in the resolver, evaluated on the checked date, never in a column — which is also why
adding it cost two seed rows and no table, and why the four-decade-old instinct to add an `is_adult` column
remains refused.

**Why the operators stayed three.** The boolean spellings were put to this language — `&`, `|`, `!` beside
`+ - *` — and the answer came back first as the observation that settled the whole round: *"`OLDER(18)` is
still a set of people."* It is, and once that is seen, boolean notation has no work left to do.
`p ∈ (A ∩ B) ∪ C` **is by definition** `(p ∈ A ∧ p ∈ B) ∨ p ∈ C`, and with `EVERYONE` in the language `!X`
**is** `EVERYONE - X`. So `& | !` would be a **second spelling of three operators the language already has**,
and a second spelling is not free even when it is pure sugar: the canonical rendering has to pick one, the
editor has to accept both, every write-path check has to reason over both, and two people's identical rules
stop being textually comparable — which is the property the canonical rendering exists to buy, and the reason
[F-22](../open-questions.md#f-22--closed--the-editor-may-fold-and-flatten-for-display-the-stored-canonical-string-never-changes)
exists at all. **The case for them was genuine**: a person writing an eligibility rule is thinking in
conditions, not in algebra. But that is an **editor's** case, and it is answered in the editor — what a writer
types is a rendering, what is stored is a set expression, and if the editor ever wants to accept `!` it can
expand it into `EVERYONE -` on the way in and never store that anything happened. **Declined, then, and
recorded as declined** rather than left absent, because this entry granted them twenty minutes earlier and an
entry that reverses itself inside its own round should show that it did.

**One argument this round made and dropped, and why it is on the record anyway.** The case for a closed
*vocabulary* was made in governance terms: volunteers will write `FEE_PAID` into an audience and nobody will
notice until it is wrong. That argument is not answered here, it is **overruled** — see §Authors — and it is
left in this entry because it was aimed at the wrong half of the design. **A row per operand, shipped with
its evaluator arm so that a code with no arm behind it is a deployment bug rather than a held feature
([D-104](round-10b.md#d-104--a-permission-codes-last-segment-is-an-action-and-a-registry-that-prose-contradicts-is-a-fiction)),
costs a trusted author nothing**; what would have cost them something is a language that refuses to grow, and
this one does not. The shape that survived both rulings is worth naming, because the two rulings pull in
opposite directions: **the vocabulary is open, the grammar is closed.** New tests arrive as named rows a
person may compose with the three operators they already know; the language never grows a place to put a
comparison. That is the whole difference between a vocabulary that grows and a parser that accepts anything,
and it is a difference in *where the decision is made*, not in how much freedom anybody has.

**Time, and what accepting it costs.** Your ruling, in full: *"I know, that the time will change, how the
rules resolve and IT IS FINE."* Recorded as accepted rather than as an open risk, with its mechanics stated
so that nobody rediscovers them as a bug:

- A derived set can gain or lose a member with **no write at all**, at midnight, one person at a time.
  This is the first exception to [F-6](../open-questions.md#f-6--closed--the-permission-cache-is-rebuilt-nightly-on-any-ruleset-write-and-on-request)'s
  model in which invalidation is caused by a write; the answer is not a new invalidation path but the
  observation that a cached decision is already keyed to a date and already expires.
- **Nothing is stored, so there is nothing to invalidate.** No table changes when a person turns eighteen;
  there is no row to expire and no cache of *membership* to keep. This is the property that age *bands*
  would not have had, which is why they are not in this design.
- **What it buys is history.** `can(p, view, doc, on 2024-05-01, about q)` now has a right answer for an
  age-bearing rule, computed from a birth date and a date, which is a question no snapshot design could
  answer and which the audit trail will ask.

**The honest residue is not performance, it is the record.** A check for yesterday answers for yesterday,
but *the decision taken yesterday* — "this grant reaches these people", printed by the preview and written
into audit at the moment of the write
([D-104](round-10b.md#d-104--a-permission-codes-last-segment-is-an-action-and-a-registry-that-prose-contradicts-is-a-fiction)) — was a snapshot
of a set that has since moved. That is not a cache problem and it is not raised again as one; it is carried
as [F-23](../open-questions.md#f-23--closed--words-only-the-expression-is-the-record-and-the-preview-is-a-rendering-on-a-date).

**Authors: the premise, and the two things it does not buy.** Your standing answer, quoted because several
entries in this round argue against something it already settled: *"The people writing the rules WILL know,
what they are doing. I know, that the time will change, how the rules resolve and IT IS FINE."* Until now
this was implied by
[D-091](round-09.md#d-091--a-permission-group-is-a-rule-and-a-list-at-once-and-a-rule-may-name-another-group)'s preview
— the entry that requires it — and by the absence of anything like a lint; it is now a premise, and it has
three consequences and two limits.

- **The preview is a workbench, not a guard.** It stays required — but the corpus's justification for it
  ("the writer may not know whom they are reaching") is replaced with *"the writer can ask, and the answer
  is printed and logged"*. Same requirement, different reason, and the difference matters to whoever is
  tempted to make it a confirmation dialog.
- **No new save-time refusal anywhere in this round**, and none is implied by it. The only refusals left in
  the write path are **structural** (a cycle, a dangling `parent_id`, an argument of the wrong kind).
- **A report is offered rather than a block**, which is exactly the shape D-106 chose.
- **It does not buy a different audience.** Competence in the author says nothing about the people the rule
  *reaches*. The fail-closed order, guardianship's allows-only ceiling, and the unreachable `dependent.*`
  namespace are untouched by this premise, because those protect people who did not write the rule. This is
  the boundary of the premise and it is drawn here rather than discovered later.
- **It does not buy an unlogged write.** Every refusal this round declined was a refusal to *stop* a save;
  none of them was a refusal to *record* one. The audit trail is where the premise stops being a
  courtesy — see [D-088](round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short) for what it
  keeps and for how long it keeps it.

**The boundary of each operand, fixed here because nothing else fixed it.** `OLDER(n)` is **`n` years or
older** on the checked date; `YOUNGER(n)` is **strictly under `n`**. The pair therefore partitions everyone
who *has* a birth date, with no overlap and no gap, and `YOUNGER(15)` means what "under 15" means in ordinary
speech — **a fifteen-year-old is outside it**, which is load-bearing for EV-1's ceiling example
`MEMBERS * YOUNGER(15)` and for every camp form that will ever print this as an age limit. Both readings were
already implied in [domain/06 §6.1](../domain/06-authorization-model.md) and in the registry rows; they are
written here because an inclusive-or-exclusive off-by-one in a ceiling is a safeguarding bug with a plausible
implementation behind it, and because a corpus that leaves a boundary to inference will implement it twice.

**A worked example this entry shipped was vacuous, and it is worth keeping as an example of its own.** The
first draft illustrated the two operands with `MEMBERS * OLDER(18) - YOUNGER(6)`. **Nobody is both eighteen
and under six**, so the subtraction excluded nobody and the expression meant `MEMBERS * OLDER(18)`; a
subagent reading the registry rows noticed it while doing unrelated propagation, which is the only reason it
was caught. It matters beyond tidiness because the example was being cited as the *reason both operands
exist* — and an example that needs neither operand argues for neither. The band that genuinely requires both
is **`MEMBERS * OLDER(13) * YOUNGER(19)`**, which is thirteen-to-eighteen and which excludes people at both
ends. **The lesson is the corpus's own, turned on me: an example is an assertion, and it gets checked against
the registry like anything else** ([D-104](round-10b.md#d-104--a-permission-codes-last-segment-is-an-action-and-a-registry-that-prose-contradicts-is-a-fiction));
the person writing the prose is the worst place to check it, including when that person is the one who asked
for the feature.

**Refusals become decisions, and both of them keep their answers.** `PRESENT(event)` and `WHITELISTED` were
refused as *kind* — "not materializable", "no stored state" — and with attribute operands admitted, that
class of argument is gone: a predicate over a column is now an ordinary operand, so nothing can be excluded
by what it *is*. Both stay out, on their own merits, which were always the real reason:

- **`PRESENT(event)` — still not seeded.** A tick box on a check-in screen would become the thing that
  revokes a leader's access to their own camp when somebody forgets to tick it. That is an argument about
  consequences and it survives intact; what is withdrawn is the claim that the language could not express it.
- **`WHITELISTED` — still not seeded**, because there is no state to evaluate
  ([F-20](../open-questions.md#f-20--closed--whitelisted-stays-unseeded-because-there-is-no-state-to-evaluate-and-the-feature-arrives-anyway)),
  and an operand that reads nothing is **a word with nothing behind it** — a row whose evaluator would answer
  the same for every person on every date, which is not what a registry row is for. F-20 stays open as a
  question about whether the *feature* is wanted, and is no longer a question about whether the type system
  forbids it.

**Storage, and the one invariant this could have broken.** `OLDER`'s argument is an **integer**, which makes
it the first operand argument in the registry that is not an entity reference. **The registry still names
exactly two reference-less polymorphic keys** — `access_grant.scope_id` and `audience_operand.selector_arg_id`
— because a scalar stored in `selector_arg_id` is not a key pointing at anything: nothing to repoint on a
merge, nothing for a cascade to find, nothing for F-10's orphan check to walk. **§11's check that the count
is two stays true, and stays true for the right reason rather than by luck**: the check is about *references*,
and `18` is not one. `argument_type` therefore gains a scalar domain, and the pages that enumerated the
argument kinds as though the list were complete now say what it is: **six `argument_type` values, five of which
are tables.** The merge and orphan scans still walk exactly the five that name something, and that is the
sentence those pages should always have carried — the count this corpus keeps getting wrong is the count of
things to scan, not the count of values a column may hold.

**See:** [domain/06 §6 and §6.1](../domain/06-authorization-model.md) for the language and the corrected
argument, [data-model/05 §8](../data-model/05-authorization.md#the-selector-registry) for the fourteen-row
registry, [permission-catalog §1](../appendix/permission-catalog.md#1-conventions) for the leaf list,
[F-5](../open-questions.md#f-5--closed--nothing-is-missing-from-the-registry-and-the-last-gap-was-a-selector-that-should-not-have-been-in-it), which closes on its
age half, and [EV-1](../open-questions.md#ev-1--closed--there-is-no-age-ceiling-the-grant-is-the-rule),
which stays closed for a different reason than it was.

---

## D-108 — There is no `SCHOOL` operand: a selector may only name a fact the model stores

**Status:** decided (from your answer)
**Date:** refinement round 12

**Decision.** No `SCHOOL(x)` operand, no `school` column on `person`, no school-shaped selector of any kind.
Asked whether school should enter the selector language, the answer was that **it is not an important selector —
at least not for now** — and this entry records that as a refusal with a reason, rather than as an oversight.

**The rule it instantiates, which is the useful part.** A selector names a set of people the model **can compute
from data it holds**. `OLDER(n)` passes that test because a birth date is stored; `MEMBERS` because a membership
period is stored; `GROUP(x)` because the roster is stored. A school affiliation is not stored anywhere in this
system, and [D-092](round-09.md#d-092--the-corpus-is-people-and-events-and-it-names-no-units)
put it out of scope on purpose: the corpus is a people export and an event export, and it carries no school.
**So the refusal is not about schools — it is that an operand over an absent column would be a selector whose
answer is always the empty set**, which is the one failure mode this module has decided, repeatedly, to make
impossible rather than handle gracefully.

**What to use instead, which works today.** A `person_group` per school, filled by whoever knows — by hand, or
by the import if it ever carries the fact. `GROUP(zszos_2)` is a selector now, it takes an argument, and
`MEMBERS * GROUP(zszos_2)` is the school-bounded audience. **The difference is not a limitation: a group is a
set somebody is responsible for**, and a school cohort in a Scout organization is exactly that kind of thing —
known by a leader, not derivable from an attribute. A derived operand would have quietly asserted that school
membership is a fact the system owns.

**What would reopen it, and this is the "for now" written as a trigger rather than a date.** Either of these:

- **the import starts carrying a school column** for a meaningful part of the people — at which point school is
  stored, `SCHOOL(x)` becomes computable, and the operand is one decision entry and one seed row
  ([F-5](../open-questions.md#f-5--closed--nothing-is-missing-from-the-registry-and-the-last-gap-was-a-selector-that-should-not-have-been-in-it)'s cost model for a new
  operand, which has now been paid once and came to two rows and a reserved word);
- **a fee, a subsidy or an eligibility rule turns out to depend on school** — at which point the question is no
  longer about a selector at all, because the dependency is a fact with consequences outside authorization, and
  it belongs in the person model first.

**Worth saying about how this entry came to exist.** It was prompted by a finding this round filed against
another page and then retracted: the "`all_in_school` audience the prose names but the registry cannot express"
was never in the corpus
([F-5](../open-questions.md#f-5--closed--nothing-is-missing-from-the-registry-and-the-last-gap-was-a-selector-that-should-not-have-been-in-it) carries that retraction,
with the grep that kills it). **The invented defect asked one true question**, and this entry is the answer to
it, which is the best outcome available from a fabricated citation and the reason the retraction is kept in
print rather than edited out.

**See:** [D-107](#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded) for
what an operand is allowed to be, [D-092](round-09.md#d-092--the-corpus-is-people-and-events-and-it-names-no-units)
for what the corpus actually contains, and
[data-model/02 §3](../data-model/02-organization.md) for `person_group` as a set somebody is answerable for.

---
