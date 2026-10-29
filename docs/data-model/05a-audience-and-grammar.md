# Data Model — Authorization: the audience table, the grammar, the selector registry

What an audience is as a row, how an expression is written and rendered, and
which operands the language has.

**Section numbers are shared across the five parts** and never renumbered, because other
pages cite them by number and their anchors are built from them: [05-authorization.md](05-authorization.md) holds §1–§7, [05a](05a-audience-and-grammar.md) §8 (the `audience` table, the grammar, the selector registry), [05b](05b-expression-tree.md) §8 continued (the tree and what each operand costs), [05c](05c-access-log-and-resolver.md) §9–§10 (`access_log` and the resolver), and [05d](05d-invariants-and-seed.md) §11–§13 (invariants, seed data, open issues).

---

## 8. `audience` — grants that target a set of people

A grant can name a **person** or an **audience** (D-042). **An audience is now an expression over
named sets, stored as a tree**
([D-101](../decisions/round-10b.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree)):
`MEMBERS * ROLE(treasurers) - GROUP(schuzka2026-1)` is one grant's grantee, and the three-arm shape
it replaces — a rule arm, a manual arm, an inclusion arm, unioned — is deleted. D-091's outcome
survives the reversal: composing *"the kitchen crew, plus whoever leads this pack"* in **one** grant
is what round 9 bought and round 10 keeps, and the intersection and difference round 9 could not
express at all can now be written.

**Fields** (`audience`)

| Field | Kind | Notes |
|---|---|---|
| `id` | integer identity | Surrogate key. |
| `code` | text, optional, unique where set | **Two different jobs, and round 10 gave it a second one.** (1) Since D-101: a stable handle for the seeded rows (`everyone`, `all_members`) and for reports — an audience is *aimed at* by a grant through `access_grant.audience_id`, a reference, and that has not changed. (2) **New, [D-103](../decisions/round-10b.md#d-103--an-audience-may-name-another-audience): the only thing another audience can name.** `AUDIENCE(<code>)` resolves through this column, so **naming an audience is what makes it composable, and an unnamed audience is simply not one.** Naming stays opt-in — there is no reason to force a handle onto a grant's private addressee list — and the leaf may not point at a null code, which is a check reading another table and therefore not a constraint (§11, check 12). **`code` now joins the shared namespace** of roles, groups and reserved words; `name` does not, and the two are different columns serving different questions. |
| `name` | text, required | What a human calls it in the editor. |
| `description` | text, optional | Why it exists, for whoever finds it in three years. |
| `is_system` | boolean | Default false. Set on the seeded rows so an editor can refuse to delete one. |
| `valid_from` | date, optional | |
| `valid_to` | date, optional | Absent = open. **An ended audience reaches nobody**, and that is the one test that gates the whole expression (§*Evaluation*). **Which is precisely why ending one is a save-time refusal once anything names it** — see the rule below, and note that under `-` an emptied operand makes the result **wider**, so "ended" would otherwise be a way to widen a grant by editing a different screen. |
| `created_at` | timestamp, audit time | |
| `created_by` | reference to person | |

**Rules** (`audience`)

- **The expression is the audience.** An audience with no root operand row is an empty set, and a
  freshly created one is exactly that — not a misconfiguration, and how an expression gets built one
  node at a time. What is *not* legal is a grant aimed at one being reported as granting something,
  which is the editor's job (§*The cost of composition*) and integrity check 7 (§11).
- **An audience is *aimed at* by reference and *named* by code, and those are different relations.**
  A grant points at `audience.id`; another audience points at `audience.code`. **What changed in this
  round is only the second half** — D-101's sentence, *"an audience is referred to, never named, and
  that is why the name collision problem does not reach this table"*, was true of a grammar whose
  only names were `GROUP()` and `ROLE()`, and
  [D-103](../decisions/round-10b.md#d-103--an-audience-may-name-another-audience) retires it.
  **The name collision problem now does reach this table**, and §*Names are one namespace* is where
  the rule lives.
- **Bare names do not resolve to audiences.** `MEMBERS * COUNSELORS` names a role or a group, exactly
  as it did before, and the audience arm has to be written `AUDIENCE(veterans)` (D-103). **This is a
  backward-compatibility rule and it is worth more than the four characters it costs:** letting a bare
  name reach a third table would silently change what stored expressions *mean*, which is the one
  change this round's own canonical-rendering rule exists to prevent.
- **`code` is unique among the rows that have one**, and joins the shared namespace (§*Names are one
  namespace*).
- **An audience may not be ended or deleted while something live names it** — a live grant aimed at
  it, or a live audience reachable from a live grant through any number of `AUDIENCE` leaves
  (D-103). Refused at save, and the reverse lookup is one indexed query over `audience_operand` rows
  whose `selector_kind` is `AUDIENCE`, so the machinery the reference needs is the machinery the
  protection needs. **Without this, "ended" is a way to empty an expression from a screen nobody
  associates with it** — and under `-` an empty operand makes the answer wider, not narrower. No
  foreign key does this job: the reference is a `code` inside a polymorphic column, not a foreign
  key (§*The expression tree*).
- **Naming an audience requires the right to read it — `audience.view` over it, in the catalog's
  vocabulary — and grants nothing to the people it contains**
  ([../appendix/permission-catalog.md](../appendix/permission-catalog.md)). Fail closed, and *see what
  you name* is already D-091's requirement. **`AUDIENCE(veterans)` in a grant someone else saves is how
  one person's composition decision becomes another's authority, and the read permission is the only
  place that asymmetry is visible to the writer.**
- **The row carries no size rule.** There is no depth limit, no width limit and no node budget on an
  audience: **[D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)
  deleted the bound, and nothing replaces it on this row** — the tree is stored exactly as the writer
  wrote it. What a large expression costs is a report's job (§*The cost of composition*), and a report
  with nothing behind it is a convention and not a guard
  ([D-081](../decisions/round-06.md#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now)).
- Where both ends of the period are set, `valid_to` is later than `valid_from`.

**Deleted from this table:** `resolver_key`, `scope_parameter`, `include_depth_limit` and
`selector_depth_limit`. The first two are absorbed into the `selector_type` registry (§*The selector
registry*) — which operands exist, whether they take an argument and what type it is was three
hard-coded lists (the enum written out in prose, the reserved-word list, and the "meaningless without
a `resolver_key`" rule) and is now one seeded table. `audience_include`, the inclusion arm, is deleted
outright (§*What each operand costs*). **`selector_depth_limit` is the newest deletion and it has no
successor at all:** it bounded the height of the tree over the expanded expression, and
[D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)
removed both the number and the check that read it, so the column's own justification — D-048's rule
that a number somebody may want to change belongs in a configuration column
([D-048](../decisions/round-04.md#d-048--the-renewal-window-is-60-days-and-is-a-configuration-parameter)) —
outlived the parameter it was written to place. **There is no bound left to place anywhere.**
~~`kind`, required, `builtin` exactly when `resolver_key` was set~~ — deleted by D-091 one round
earlier, and the deletion is kept visible because three rounds of prose rested on it and its
successor (`resolver_key`) is now gone too: **an audience has no kind and no rule key, only an
expression.**

### Author in sets. Evaluate per person.

**This is the split that makes the notation question smaller than it looks.** `p ∈ (A ∩ B) ∪ C` **is
by definition** `(p ∈ A ∧ p ∈ B) ∨ p ∈ C`, so the two notations considered in D-101 are the same
function read from two ends. The choice decides **what gets stored and what a writer is allowed to
say**, not what the machine computes:

- **Sets are the source language, and they are the closed one.** `-` is complement against
  `EVERYONE` and `*` distributes over `+`, so the set form is no weaker than a boolean one — it buys
  zero expressive power and everything in the way of safety. D-060 refused a rule engine, and a per-person
  boolean language is the door to one. **That half of the argument survived round 12 untouched:** `+`, `-`
  and `*` are the only operators this language has, one spelling each; the boolean spellings `&`, `|` and
  `!` were put to it in the round that admitted the age operands and **were declined**, which is the record
  [D-107](../decisions/round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)
  keeps under *why the operators stayed three*. **The vocabulary grew by two rows and the grammar did not
  grow at all** — that is the whole of what this round did to the language. What did not survive is the
  second half of the same sentence, the test it offered for what an operand
  may be: ~~an operand must be a named, materializable set of people. An attribute is not a set of people.
  Guardianship is (`GUARDIANS(x)` is a set), age is not, and the line falls exactly where D-060 already
  drew it.~~ **That test is wrong, and [D-107](../decisions/round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)
  deleted it rather than repairing it.** `OLDER(15)` is a property of a person and it *is* a set of
  people: the people who are fifteen or older on the checked date — **the same shape of thing**
  `MEMBERS` denotes (the people who pass `is_current_member`). ~~And `GUARDIANS(x)` denotes the people who
  hold a row.~~ **That second example was withdrawn with its operand one round later**
  ([D-113](../decisions/round-13.md#d-113--the-guardianship-channel-has-no-expression-guardians-is-not-a-selector)),
  and it is worth knowing it was the test's *strongest* example rather than hiding it: guardianship is a row
  you can join, so it proved the rule beautifully — and the reason it is not an operand is not that it fails
  the set test, which it passes, but that **the relationship carries its own authority**, so an operand naming
  it would re-grant, one code at a time, what the guardianship channel grants whole. **The set test survives
  losing its best case, because `MEMBERS` was always the load-bearing example** and `MEMBERS` stores nothing
  at all. **Every operand in the registry is a test with a set on the other side of it**; reading
  one column is a different thing from joining one table, but it is not a different *kind of answer*.
  Read as written, the materializability test would have excluded `MEMBERS` too, since nothing anywhere
  stores the member list — which is how it took a round of being quoted in three documents before anybody
  noticed it proved too much.
- **What was doing the work all along, and it is the clause that stays:** an operand must be **named** —
  a row in §*The selector registry*. **A writer may compose seeded operands and nothing else.**
  `OLDER(18)` is a row, seeded, shipped with its evaluator arm like every other row; `AGE >= 18` is not
  one and cannot be, **because the language has no `>=` to put anywhere**. That is a smaller and sturdier
  door than the one this bullet used to claim, and it is the one D-060 needed. D-060's decision is
  untouched — no eligibility rule table, no prerequisite system, nothing evaluated outside `can()` — only
  its stated test for what an operand may be is replaced. Eligibility stays capability, and the change
  round 12 makes to it is exactly this: **there is still no gate the system applies on its own, and there
  is now a vocabulary a person may use to write one.**
- **A check never materializes a set.** The resolver compiles the expression down to a predicate for
  the person being checked. **An implementation that evaluates `MEMBERS` as a list of ids and then
  tests for containment pays three thousand rows per request** — which is the one way to get this
  wrong, and the reason the requirement is written here rather than left to whoever builds it.
  Integrity check 16 (§11) is the CI assertion of that sentence.
- **The workloads the corpus already promised need sets, not predicates.** "Who does this grant
  reach?" must be **shown, expanded, in front of a human** — D-091 made that a requirement on the
  screen, and a predicate can only report `true` while a set *is* the answer. "What may a treasurer
  do?" (D-100) needs the person→set index, and `role_holder` and `person_group_member` **are** it; an
  expression is unindexable. And naming an operand is what makes a **compilation** reusable at all: a compiled
  predicate is keyed by the expression it came from and the ruleset version, so one edit to a shared name refreshes
  every grant that embeds it, which is more reuse than an inlined subtree could ever be given
  (§10, [D-114](../decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation)).

### Grammar, precedence, and the canonical rendering

```
expr    := term ( '+' term )*
term    := operand ( ( '*' | '-' ) operand )*
operand := EVERYONE | MEMBERS
         | OLDER '(' n ')' | YOUNGER '(' n ')'
         | GUARDIANS [ '(' person ')' ]   ← row deleted in round 13, D-113; not a selector
         | ATTENDED | PLACED | CONFIRMED | ON_WAITLIST | ORGANIZERS
         | ROLE '(' name ')' | GROUP '(' name ')'
         | PERSON '(' person ')'
         | AUDIENCE '(' code ')'
         | '(' expr ')'

  OLDER(n) and YOUNGER(n) read person.birth_date AS OF THE DATE THE CHECK IS MADE,
  so `MEMBERS * OLDER(13) * YOUNGER(19)` reaches different people on different
  dates with no write, and can(..., on date) for a past date answers for that
  past date. Their argument is an INTEGER — the first operand argument in the
  registry that is not an entity reference (§*The selector registry*). There is
  no comparison operator anywhere in this grammar: no '>=', no '<', no bare AGE
  -- which is where D-060's refusal of a rule engine now lives.  See the prose
  under this block, and D-107.

  The operators did not change this round and there are no new ones: '+', '-'
  and '*' are the whole set, each with one spelling. What grew is the operand
  list, and nothing else — OLDER and YOUNGER are ordinary named operands,
  composed by the same three operators as every other row.

  Each of ATTENDED, PLACED, CONFIRMED, ON_WAITLIST and ORGANIZERS appears either
  bare — bound to the item the grant sits on — or written '(' event ')'.  A bare
  bound operand on a unit-scope grant is refused (§6, *What is refused when a
  grant is saved*).

  PERSON takes a person and names a set of one.  A hand-written set of people is
  therefore a sum, not a leaf: `PERSON(a) + PERSON(b)`
  ([D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)).
  AUDIENCE names another saved audience by its
  `code`; an audience with no code cannot be named, and a bare name never
  resolves to one ([D-103](../decisions/round-10b.md#d-103--an-audience-may-name-another-audience)).
```

- `+` union, `*` intersection, `-` difference — **three operators, and round 12 added none of its own.**
  What it added was two operands the same three operators compose:
  `MEMBERS * OLDER(13) * YOUNGER(19)` is an ordinary term
  ([D-107](../decisions/round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)).
- **There is no comparison operator in the language.** No `>=`, no `<`, no bare `AGE`: an operand is a
  registry row and `AGE >= 15` has no row to be, which is the whole of D-060's protection now
  (§*Author in sets*, and [D-107](../decisions/round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)).
- **`*` and `-` bind tighter than `+`; `*` and `-` bind equally, left to right; brackets override.**
- **The canonical rendering prints every bracket, always.** The rendering is derived from the rows
  and is what every screen shows; if it is also kept as a column for search, it is a copy and the
  rows win (see §*The expression tree*).

**Printing every bracket is not a courtesy, and the example is the proof.** Under this precedence,
the unbracketed `MEMBERS - GROUP(schuzka2026-1) * COUNSELORS` means *"everyone except the counselors
in that group"*, which is **not** what its author meant — they meant *"all counselors not in that
group"*, whose stored form is `(MEMBERS - GROUP(schuzka2026-1)) * COUNSELORS`. The editor rewrites
what is typed into canonical form before saving, so **no expression in this system is ever read bare**.
The consequence is a nice property worth having: once everything is stored fully bracketed, changing
what binds tighter later changes nothing already stored, which is why the canonical rendering is a
requirement and precedence is the closed half of D-101's two-way door.

**The rule is unchanged by [D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other),
and its cost is now visible:** a hand-typed sum of twenty people is a left-to-right chain, so it
prints as nineteen nested pairs of brackets. That is what "storage and display both say what was
written" buys, and it was asked for. If it turns out unreadable, the answer is that a set of people
big enough to be unreadable is a `person_group` — not a flattening rule invented in advance.

### The selector registry

**`selector_type` is a seeded table, not an enum**
([D-101](../decisions/round-10b.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree)):
**the language becomes data.** The parser reads its reserved words from it, the editor builds its
dropdown from it, and the write path checks arity against it. Three hard-coded lists became one
seeded registry in the shape `grant_scope_type` already has.

**Fields** (`selector_type`)

| Field | Kind | Notes |
|---|---|---|
| `code` | text, required, unique | The reserved word: `MEMBERS`, `ROLE`, `PLACED`. |
| `name` | text, required | For the editor's dropdown. |
| `takes_argument` | boolean, required | Whether the code **may** be written with an argument. The arity check reads this column and nothing else. |
| `binds_to_item` | boolean, required | True exactly when the **argument-less** form means "relative to the item being checked" ([D-102](../decisions/round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)). |
| `argument_type` | text, optional | Which table the argument names a row of — `role`, `person_group`, `person`, `event`, **`audience`** — **or a scalar: `integer`, new in [D-107](../decisions/round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded) and the argument kind `OLDER`/`YOUNGER` take. Six values now, five of them entity kinds and one of them not an entity**, which is the sentence every page that enumerated these as though they were all entities has carried from this round. Absent exactly when `takes_argument` is false. This is what the save path compares against the grant's item type, which is a reason the registry is doing real work and not merely tidying. **It is not always a `grant_scope_type`**: `person` never was and `audience` never will be, because a grant is never *about* an audience — it is aimed *through* one. The two coincide for exactly the item-scoped operands, which is the set the binding check reads. **A scalar argument is never in that set**, since `OLDER` binds to nothing. |
| `description` | text, optional | The sentence a writer reads before using it. `AUDIENCE` carries its gloss here, because the name misleads without one; `LIST` used to be the other one, and its gloss went with its row ([D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)). |
| `is_system` | boolean, required | Default true, and **every seeded row is true with no row planned false.** This column exists to make the table refuse an edit, not to mark a category. |

**Seeded selectors**, in full, because this table *is* the language — **thirteen rows**, all of them
shipped. **The count has moved four times in four rounds, so it is stated as a history rather than as a
number:** thirteen while `LIST` existed, **twelve for exactly one round** after
[D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)
deleted it, **fourteen as of
[D-107](../decisions/round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)**,
which seeded `OLDER` and `YOUNGER`, and **back to thirteen in the next round** when
[D-113](../decisions/round-13.md#d-113--the-guardianship-channel-has-no-expression-guardians-is-not-a-selector)
deleted `GUARDIANS`. **Anyone reading a fourteen-row page written last round should not carry that number
forward, and anyone reading a thirteen-row page from three rounds ago should not assume theirs is the same
thirteen** — the earlier one had `LIST` and no age operands. The two rows round 12 added are the first operands
added since `PERSON` and the first whose argument is not an entity reference. What the deletions bought is still
stated where it can be checked rather than as a mood: **every one of the thirteen is either a rule about people
or takes an argument**, so the registry has no special case left to explain — the operand with neither property was `LIST`, and the two newcomers have both of them at once,
since `OLDER(18)` is a rule about people *and* takes an integer. `PERSON` was the last row added *until
this round*, and it was added *late, in that round, by a decision entry that
had already said it was here*: this table was written from the evaluator's arm list rather than from
[D-101](../decisions/round-10b.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree)'s
grammar, and an arm list copied from an implementation loses the arm nobody implemented. The whole episode is
[D-104](../decisions/round-10b.md#d-104--a-permission-codes-last-segment-is-an-action-and-a-registry-that-prose-contradicts-is-a-fiction),
whose finding is that **no check in §11 could have caught this one**: check 12 compares rows against rows,
and the disagreement was between a row and a decision entry. The remedy it adopts is a report run over the
documents before a round closes, not a database constraint — see §13.

| `code` | Argument | Binds to item | Means |
|---|---|---|---|
| `EVERYONE` | never | no | Any person, including those with no account and no membership. |
| `MEMBERS` | never | no | Holds a membership live on the checked date — **the same predicate the deleted gate applied** ([D-039](../decisions/round-02-03.md#d-039--member-permissions-require-a-current-paid-membership)); the clause died, the test did not. |
| `OLDER` | required (**`integer`**) | no | **The people who are `n` years old or older on the date being checked**, from `person.birth_date` — the first operand in the registry whose argument is **a number rather than a row** ([D-107](../decisions/round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)). It is a row here for the reason the whole table exists: **it is a named operand, and it denotes a set of people** — the same shape of thing `MEMBERS` denotes, which is a test over membership rows and stores nothing either. **A person with no birth date is not in the set**, as a person with no membership row is not in `MEMBERS`: that is an ordinary answer, **not a resolution failure**, and §11's report of unresolved leaves must not page about it (§*Evaluation*). **Its membership moves at midnight with no write**, which is the property this round accepted on purpose — see §*The cost of composition*. |
| `YOUNGER` | required (**`integer`**) | no | **The people strictly younger than `n` on the date being checked** — `OLDER`'s mirror, `n` and up against under `n`. **Each is the complement of the other, and the language has no complement a bare leaf can carry** (only `-`, which needs something on its left), so both are seeded rather than one being spelled out of the other; that is the whole of their relationship, and it is why **there is no `AGE_BAND` row and none is wanted** — a band is composed out of the operators every other row is composed with, and `OLDER(13) - OLDER(18)` is thirteen to seventeen. Same argument kind, same date rule, same non-failure for a missing birth date. |
| `PERSON` | required (`person`) | no | **One named person** — a set of one, which is a set, so it is a named operand like every other row. How an exception for a named individual lives *inside* the expression that granted the rule, next to the thing it exempts ([D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)). **And since [D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other) it is how several named people are written too:** a hand-written set is a sum of these — `PERSON(a) + PERSON(b)` — because a set of one is a set, and a set of three is the same thing three times. There is no separate "hand-typed list" operand and no table behind one. |
| `ROLE` | required (`role`) | no | Holders of that office live on the checked date (`role_holder`). |
| `GROUP` | required (`person_group`) | no | Members of that group live on the checked date (`person_group_member`). |
| `AUDIENCE` | required (**`audience`**) | no | **The value of another saved audience's expression**, evaluated live on the checked date. **New, [D-103](../decisions/round-10b.md#d-103--an-audience-may-name-another-audience)**; the one operand whose argument is a *decision about access* rather than a roster, and so the one that makes a rule namable. |
| `ATTENDED` | optional (`event`) | yes, `event` | `response = attending`. |
| `PLACED` | optional (`event`) | yes, `event` | Attending **and not waitlisted** — **the capacity set**, the one the events module counts and the index already serves. |
| `CONFIRMED` | optional (`event`) | yes, `event` | `PLACED` **and** `is_confirmed` — holds a paid place. |
| `ON_WAITLIST` | optional (`event`) | yes, `event` | Attending and waitlisted. |
| `ORGANIZERS` | optional (`event`) | yes, `event` | Runs the event (`event_organizer`). |

**Two rows have been deleted from this table, and the second is the more instructive.** `LIST` went first
([D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)):
its table went with it (§*`audience_member`, re-roled as the `LIST` leaf — deleted by D-105*) and its grammar arm
went too, so there was nothing left for the row to point at — a row that references nothing. `GUARDIANS` went
second ([D-113](../decisions/round-13.md#d-113--the-guardianship-channel-has-no-expression-guardians-is-not-a-selector))
**with a table of its own to point at, a row in this registry, and a meaning that belonged to a different
mechanism**: guardianship is a channel carrying a `right_level` over a child, not a set a grant may be aimed at,
and its row's `Binds to item` cell was using that column to talk about a person — while the bound form the row
promised was unsavable on every scope, because the same registry says `person` is not a scope. **The table above
is exactly thirteen rows; a fourteenth would be a bug**, and the same would have been true of whatever number
this table held in any previous round. **The number is not the point; the closure is** — and D-113 adds the
sharper half of that lesson: **a row can sit in this table, be counted correctly, and still be a bug.** Fourteen
was arithmetically true of a registry containing a row nobody could legally use as described, so *every page
that repeated "fourteen" was reinforcing a fiction with arithmetic.* What is checkable here is not the count but
**each row against the save path that must accept it**. What the sentence
asserts is that *this list is the language*, so a row appearing anywhere other than here — in a screen's
dropdown, in a resolver's switch, in a decision entry that never reached this table — is a bug: that is
what `PERSON` was for one round, in the other direction. The count is written down only because it is the
cheapest way to run that check by eye, and a count that has been thirteen, then twelve for exactly one
round, then fourteen, then **thirteen again for the opposite reason** — a row removed rather than a pair added —
is the argument for writing it down rather than for trusting what a reader remembers. **A number that returns to
a previous value is especially worth printing with its history**, since "thirteen" read on a page written three
rounds ago and "thirteen" read here are not the same thirteen. §*What `LIST` is, said plainly — withdrawn by D-105* keeps the reasoning that survives
the deletion.

**Rules** (`selector_type`)

- Rows are platform-seeded. **Adding an operand is a decision entry plus a seed row**, never a row
  somebody types into a screen: each operand is a branch of the evaluator and a fact about stored
  data, and an editor that could invent one would produce an expression nothing evaluates — which
  then resolves to the empty set and denies quietly forever (§*Evaluation*).
- **The registry is organization-read-only, and saying that out loud is what makes "a closed
  language" true of a table rather than merely asserted.** Every row ships with the platform, every
  row is `is_system`, no screen edits this table, and no organization adds to it
  ([D-103](../decisions/round-10b.md#d-103--an-audience-may-name-another-audience)). *The language
  becomes data* means the parser and the editor read one place instead of three; it has never meant
  the language is extensible at runtime. **A `code` in this table with no shipped resolver arm is a
  deployment bug, and it surfaces as an empty set** — an operand that reaches nobody, an allow that
  allows nobody, and a deny that on the `-` side denies everybody. That is the whole hazard of
  calling a closed set "data", and it is why the seeding of this table is release engineering rather
  than configuration. **There is no third kind of row** — the taxonomy is *shipped and seeded*, and
  "seeded, marked system, but not implemented" is not a category this model allows, however useful it
  would be as a roadmap marker. `GRANTS` was the candidate for that third kind, and it is refused on
  type grounds one clause below rather than admitted with a status flag that would put a broken operand
  inside the language and an empty set inside every grant that named it.
- **Every `code` is a reserved name** in the shared role / group / audience namespace
  (§*Names are one namespace*).
- `argument_type` is absent exactly when `takes_argument` is false, and names a real table exactly
  when it is true — **one exception, new in
  [D-107](../decisions/round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded):
  the scalar domain `integer`, which `OLDER` and `YOUNGER` take and which names no table because it names
  no row.** **Amend the check rather than admire the rule**: anything reading this column now has to know
  the scalar case exists, and has to know what the scalar is *not* — **it is not a reference**. That is
  why §11's assertion that exactly two polymorphic keys in this design go without a foreign key
  (`access_grant.scope_id`, `audience_operand.selector_arg_id`) **is still true at thirteen rows, and true
  for the right reason rather than by luck**: an `18` sitting in `selector_arg_id` points at nothing, so
  there is nothing for a merge to repoint, nothing for a cascade to find, and nothing for the orphan scan
  to walk. The check counts *references*, and `18` is not one (§*A hand-named person is now a keyless
  reference*, where the argument kinds are enumerated).
- The four attendance tiers name columns of `event_registration` and nothing else. That is the
  requirement that keeps the writer's choice honest — picking between tiers only means something if
  the choices are the stored facts.

**Three operands are not in this table, and each absence is load-bearing — but as of this round two of
them are *decisions* rather than type errors.** Round 12 deleted the kind of argument those two were
refused on. While the corpus claimed an attribute was not a set of people, a predicate over a column could
be excluded by *what it is*; `OLDER` is a row, so that class of argument is gone and nothing may be
excluded that way again. What remains are arguments about consequences, which are less tidy and are the
real reasons they were always refused
([D-107](../decisions/round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)).
**Both answers are unchanged; only the grounds moved.**

- **`PRESENT(<event>)` over `was_present` is refused, and this paragraph is the whole reason.** The reason
  is the failure direction:
  `was_present` is `NULL` until somebody takes a register, so an operand built on it would revoke a
  child's access to their own camp photos because a volunteer forgot to tick a box. That column is a
  safeguarding signal, *three-valued on purpose*
  ([D-067](../decisions/round-05.md#d-067--presence-is-a-three-valued-fact-on-the-registration)),
  and keeping it out of the selector language is what keeps it meaning "a person recorded this"
  rather than "this is who may see things". **Say this wherever presence tempts a reader**, and this
  is one of the two places that reader will look. **What this round withdrew is one clause of the older
  version of this refusal, not the refusal**: `PRESENT(event)` was previously held to be *unspeakable*
  here, and it is not — it is a predicate over a column, which is now an ordinary kind of operand. **It is
  refused because of what it would do on the `-` side of an expression when a volunteer forgets a tick
  box**, which is an argument about consequences and survives
  [D-107](../decisions/round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)
  untouched.
- **`GRANTS` is refused, and its refusal is a different kind from the two above.** It was wanted so that
  an expression could name *"the people reached by these grants"* — a bulk-editing affordance dressed as
  an operand. **An operand must resolve to a set of people, and a set of grants is not one**, which is
  not a judgement about usefulness but the closure property of §*Author in sets* doing the job it exists
  for: the moment an expression can name the grant table, `MEMBERS - GRANTS(...)` is expressible, and a
  language in which a grant can subtract a grant is a language in which the answer to *"who may do
  this?"* requires evaluating the whole expression tree of every other grant to answer one check. The
  bulk edit it was asked for is real and is an **editor affordance** — select the grants, change their
  grantees, in one screen, which changes rows and leaves every stored expression meaning what it meant.
  **Refusing it here is what keeps that screen a UI feature instead of a resolver feature.**
- **`WHITELISTED` is not seeded, and the reason is that there is nothing to evaluate.** The nearest facts
  are `source = staff` (an organizer entered them) and promotion off the waitlist. Either it means one of
  those or it is a new column on `event_registration`, which is an events decision and not a selector
  decision, so it stays [an open question](../open-questions.md) rather than being implied by a word
  in a grammar. **An operand that reads no state is not a vocabulary item but a syntax error wearing one's
  clothes**, and this refusal is untouched by round 12 — **what moved is the grounds it was previously
  given.** [F-20](../open-questions.md#f-20--closed--whitelisted-stays-unseeded-because-there-is-no-state-to-evaluate-and-the-feature-arrives-anyway)
  is now a question about whether the *feature* is wanted, and no longer about whether the language could
  hold the word: since `OLDER` arrived, a predicate over a column is an ordinary operand, and
  `WHITELISTED` is out on its merits rather than on its type
  ([D-107](../decisions/round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)).
**`PERSON(x)` is in the registry, and this page is the reason anyone noticed it was missing.** Two decision
entries write it — [D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)
has the waived-for-one-person case as `MEMBERS * ROLE(x) + PERSON(y)` and
[D-103](../decisions/round-10b.md#d-103--an-audience-may-name-another-audience)
had the kitchen crew as `(GROUP(kitchen) + LIST) - PERSON(a) - PERSON(b)` — and the seeded table this page
documents did not carry it, which this page read as *"the language has no such operand"* and the modules read
as a licence to rewrite both examples as `LIST`. **That reading was wrong, and the wrongness was a proof of
less than it seemed.** D-103's example used `LIST` and `PERSON()` **in the same expression**, so the two were
being distinguished on purpose, and no substitution could work because `LIST` was then one set: `+ LIST`
added Honza and `- LIST` would have taken him back away again, so the two who left had to be subtracted
through something that named only them. `PERSON` is that operand, `argument_type = person`, and the row now
sits above. **What the example proved *then* was that a set of several and a set of one are different kinds
of thing; [D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)
deleted one of the two it was telling apart**, so the same expression, written the way it is written now,
proves the opposite claim — that a hand-written sum of `PERSON()` leaves does the work of both. **That is the
interesting part, and it is not smoothed over here: the distinction this paragraph drew was real, and it was
not worth a table.** It is also why the deletion was a deletion rather than a redesign — an argument composes
freely, which is the only property `LIST` lacked — so `(GROUP(kitchen) + PERSON(honza)) - PERSON(a) -
PERSON(b)` parses today, unchanged in meaning.

The other half of what this page objected to was right, and is worth keeping as the reason the row took a
whole round to appear: **putting a person's id into the language means an operand is no longer only the name
of a set somebody else owns** — `PERSON(a)` is a set nobody maintains, created by being typed. That is
tolerable for exactly one operand, at the size of one person, in the one place where the alternative (a second
grant aimed at that person, which stays legal and is arguably clearer for a permanent exception) leaves the
exception invisible next to the rule it exempts. What was **not** tolerable is a control that does not parse.
**D-105 pushed this further than the paragraph expected:** with the table gone, *every* hand-named person in
the system is now one of these leaves, and a grant aimed at one person is **no longer a curiosity but the
ordinary expression of a temporary exception**. The cost of that is not the typing, it is that a typed
person is a `selector_arg_id` with no foreign key behind it — see §*A hand-named person is now a keyless
reference*, which is where the requirement D-105 newly makes load-bearing lives.

### What `LIST` is, said plainly — withdrawn by D-105

**This section is withdrawn.** `LIST` is not an operand and `audience_member` is not a table, so the
question this section spent its length on — *how does a grant carry its own hand-written exceptions?* —
now has the answer every other set in this language gives: **write them in the expression, as
`PERSON(a) + PERSON(b)`**
([D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)).
The heading is kept because a decision entry links here and because most of what this section argued is
**not** replaced by anything: it is the reasoning that decides where a hand-written set must *not* be
put, and that reasoning outlived the operand it was written to justify.

**What was withdrawn, and the embarrassment the decision records itself.** This page argued at length
that `LIST` and `PERSON` were **two operands and not one wearing two names**. The argument was correct
about the semantics and wrong about the conclusion, and the difference between those two turned out to
be a table nobody needs. `LIST` was kept by D-101 on the stated ground that *"a hand-written set of
three people is not derivable from anything"* — and D-101 was then amended, late in the same round, to
add `PERSON(x)`: the operand that names exactly one human being. **That amendment removed the table's
reason and the round did not notice**, leaving two ways to write the same set of names. D-103's kitchen
crew is the example the section was built around and it survives with one operand fewer:
`(GROUP(kitchen) + PERSON(honza)) - PERSON(a) - PERSON(b)` — **same meaning, one fewer kind of thing.**

**What survives, because the hazard it guarded is real and unchanged.** Naming three people inside a
grant must not mean making them members of a `person_group`. A group's members are true when no grant
points at them ([D-098](../decisions/round-10a.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority)),
so editing one to move one grant's reach edits a roster that other grants read — and it invents a group
nobody talks about, which is the rule D-098 wrote. **This is now the only argument left standing in this
section, and D-105 keeps it deliberately:** the answer to *"plus Honza"* is `PERSON(honza)`, and the
answer is not a roster edit. The second half survives too — an exception written this way is invisible
to every other grant until somebody opens this one, it has no name of its own, and `AUDIENCE(x)` still
resolves to another audience's whole expression and nothing less, so nobody can reach into the middle of
it from outside.

**What is given up, written as lost rather than as managed.** Per-person dates: `audience_member`
carried `valid_from` / `valid_to` with the half-open no-overlap rule, `audience_operand` carries no
period and gains none, so **a June-to-August exception is its own grant with its own period** — which is
what [D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)'s
shape is for, and the cost is exact: **where there was one audience and one grant there are now two
grants, and a reviewer asking *"what does Honza have?"* must find both.** Per-name provenance:
`added_by` named who put one person on one list, and what remains is `created_by` on a node, which —
because saving an expression rewrites its rows — answers *"who last saved this tree"* and not *"who added
Honza"*. The list's past: *"who was on this audience in 2026"* is now a recomputation over audit
payloads that expire after 24 months
([D-088](../decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)),
so the question stops being answerable in 2028 — the same hole D-091 already accepted for nested
audiences, one table wider. **And two writers at once:** adding a name used to be an insert, so two
clerks could not collide; it is now an edit of one expression, so they can, and **whoever builds the
editor owes this an optimistic-concurrency check or a queue**, because a silent lost update here quietly
removes somebody's access and nothing in the schema will notice.

**The rename question is moot, not answered.** This section's last paragraphs called `LIST` the weak
part of the design and registered `ADDED` as the name to replace it. **There is no operand to rename**,
so §13 deletes the question rather than closing it.
