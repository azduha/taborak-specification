# Data Model — Authorization: the audience table, the grammar, the selector registry

What an audience is as a row, how an expression is written and rendered, and
which operands the language has.

**Section numbers are shared across the six parts** and never renumbered, because other
pages cite them by number and their anchors are built from them: [05-authorization.md](05-authorization.md) holds §1–§7, [05a](05a-audience-and-grammar.md) §8 (the `audience` table, the grammar, the selector registry), [05b](05b-expression-tree.md) §8 continued (the tree and what each operand costs), [05c](05c-access-log-and-resolver.md) §9–§10 (`access_log` and the resolver), and [05d](05d-invariants-and-seed.md) §11–§13 (invariants, seed data, open issues), and [05e](05e-keys-and-callers.md) §14–§17 (a key, and what it may hold).

---

## 8. `audience` — grants that target a set of people

A grant can name a **person**, an **audience** or a **registered key** (D-042, widened by
[D-116](../decisions/round-16.md#d-116--a-caller-that-is-not-a-person-is-a-registered-key-and-a-key-is-a-third-grantee-kind)).
**This section is the language of the middle one**: a person is a reference and so is a key
([05e §14](05e-keys-and-callers.md)), while an audience is a set, and a set needs a language. **An
audience is an expression over
named sets, stored as a tree**
([D-101](../decisions/round-10b.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree)):
`MEMBERS * ROLE(treasurers) - GROUP(schuzka2026-1)` is one grant's grantee. One grant composes a
rule and a roster — *"the kitchen crew, plus whoever leads this pack"* — in the same expression, and
it intersects and differences as well as unions.

**Fields** (`audience`)

| Field | Kind | Notes |
|---|---|---|
| `id` | integer identity | Surrogate key. |
| `code` | text, optional, unique where set | **Two jobs.** (1) A stable handle for the seeded rows (`everyone`, `all_members`) and for reports — an audience is *aimed at* by a grant through `access_grant.audience_id`, a reference. (2) **The only thing another audience can name**: `AUDIENCE(<code>)` resolves through this column, so **naming an audience is what makes it composable, and an unnamed audience is simply not one** ([D-103](../decisions/round-10b.md#d-103--an-audience-may-name-another-audience)). Naming stays opt-in — there is no reason to force a handle onto a grant's private addressee list — and the leaf may not point at a null code, which is a check reading another table and therefore not a constraint (§11, check 12). **`code` joins the shared namespace** of roles, groups and reserved words; `name` does not, and the two are different columns serving different questions. |
| `name` | text, required | What a human calls it in the editor. |
| `description` | text, optional | Why it exists, for whoever finds it in three years. |
| `is_system` | boolean | Default false. Set on the seeded rows so an editor can refuse to delete one. |
| `valid_from` | date, optional | |
| `valid_to` | date, optional | Absent = open. **An ended audience reaches nobody**, and that is the one test that gates the whole expression (§*Evaluation*). Ending one is therefore a save-time refusal once anything names it (rule below): under `-` an emptied operand makes the result **wider**, so "ended" would otherwise be a way to widen a grant by editing a different screen. |
| `created_at` | timestamp, audit time | |
| `created_by` | reference to person | |

**Rules** (`audience`)

- **The expression is the audience.** An audience with no root operand row is an empty set, and a
  freshly created one is exactly that — not a misconfiguration, and how an expression gets built one
  node at a time. What is *not* legal is a grant aimed at one being reported as granting something,
  which is the editor's job (§*The cost of composition*) and integrity check 7 (§11).
- **An audience is *aimed at* by reference and *named* by code, and those are different relations.**
  A grant points at `audience.id`; another audience points at `audience.code`. **The name collision
  problem therefore does reach this table**, and §*Names are one namespace* is where the rule lives
  ([D-103](../decisions/round-10b.md#d-103--an-audience-may-name-another-audience)).
- **Bare names do not resolve to audiences.** `MEMBERS * COUNSELORS` names a role or a group, and the
  audience arm has to be written `AUDIENCE(veterans)`. **Why:** letting a bare name reach a third
  table would silently change what stored expressions *mean* —
  [D-103](../decisions/round-10b.md#d-103--an-audience-may-name-another-audience) keeps bare
  resolution at its two kinds.
- **`code` is unique among the rows that have one**, and joins the shared namespace (§*Names are one
  namespace*).
- **An audience may not be ended or deleted while something live names it** — a live grant aimed at
  it, or a live audience reachable from a live grant through any number of `AUDIENCE` leaves. Refused
  at save, and the reverse lookup is one indexed query over `audience_operand` rows whose
  `selector_kind` is `AUDIENCE`. **Why:** without this, "ended" is a way to empty an expression from
  a screen nobody associates with it, and under `-` an empty operand makes the answer wider, not
  narrower ([D-103](../decisions/round-10b.md#d-103--an-audience-may-name-another-audience)). No
  foreign key does this job: the reference is a `code` inside a polymorphic column, not a foreign key
  (§*The expression tree*).
- **Naming an audience requires the right to read it — `audience.view` over it, in the catalog's
  vocabulary — and grants nothing to the people it contains**
  ([../appendix/permission-catalog.md](../appendix/permission-catalog.md)). Fail closed.
  **Why:** `AUDIENCE(veterans)` in a grant someone else saves is how one person's composition
  decision becomes another's authority, and the read permission is the only place that asymmetry is
  visible to the writer — *see what you name* is
  [D-091's requirement](../decisions/round-09.md#d-091--a-permission-group-is-a-rule-and-a-list-at-once-and-a-rule-may-name-another-group).
- **The row carries no size rule.** There is no depth limit, no width limit and no node budget on an
  audience, and nothing replaces them on this row
  ([D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other))
  — the tree is stored exactly as the writer wrote it. What a large expression costs is a report's
  job (§*The cost of composition*), and a report with nothing behind it is a convention and not a
  guard
  ([D-081](../decisions/round-06.md#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now)).
- Where both ends of the period are set, `valid_to` is later than `valid_from`.

**This table carries no rule key, no kind, no scope parameter and no configuration column: an
audience has no kind and no rule key, only an expression.** Which operands exist, whether they take
an argument and what type it is live in the `selector_type` registry (§*The selector registry*), and
no bound on an expression's size is configured anywhere (D-105).

### Author in sets. Evaluate per person.

`p ∈ (A ∩ B) ∪ C` **is by definition** `(p ∈ A ∧ p ∈ B) ∨ p ∈ C`: the set notation and the per-person
boolean test are the same function read from two ends. The choice decides **what gets stored and
what a writer is allowed to say**, not what the machine computes:

- **Sets are the source language, and they are the closed one.** `-` is complement against
  `EVERYONE` and `*` distributes over `+`, so the set form is no weaker than a boolean one — it buys
  zero expressive power and everything in the way of safety. **The operators are `+`, `-` and `*`,
  one spelling each; there are no boolean spellings** — no `&`, no `|`, no `!`, which were offered
  with the age operands and declined ([D-107](../decisions/round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)).
  D-060 refused a rule engine, and a per-person boolean language is the door to one.
- **An operand must be a named registry row — a row of §*The selector registry* — and a writer may
  compose seeded operands and nothing else.** Every row denotes a set of people: `MEMBERS` denotes
  the people who pass `is_current_member` and stores nothing; `OLDER(15)` denotes the people who are
  fifteen or older on the checked date, the same shape of thing. **What an operand requires is the
  name, not a table behind the set** — an attribute may be an operand
  ([D-107](../decisions/round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)).
  `OLDER(18)` is a row, seeded, shipped with its evaluator arm like every other row; `AGE >= 18` is
  not a row and cannot be, **because the language has no `>=` to put anywhere**.
- **Eligibility is capability**
  ([D-060](../decisions/round-05.md#d-060--eligibility-is-capability-there-is-no-separate-rule-engine)):
  no eligibility rule table, no prerequisite system, nothing evaluated outside `can()`. **There is
  no gate the system applies on its own, and the language holds a vocabulary a person may use to
  write one.**
- **A check never materializes a set.** The resolver compiles the expression down to a predicate for
  the person being checked. **An implementation that evaluates `MEMBERS` as a list of ids and then
  tests for containment pays three thousand rows per request** — the one way to get this wrong, and
  the reason the requirement is written here rather than left to whoever builds it. Integrity check
  16 (§11) is the CI assertion of that sentence.
- **The workloads this corpus promises need sets, not predicates.** "Who does this grant reach?" must
  be **shown, expanded, in front of a human** — a requirement on the screen (D-091), and a predicate
  can only report `true` while a set *is* the answer. "What may a treasurer do?" (D-100) needs the
  person→set index, and `role_holder` and `person_group_member` **are** it; an expression is
  unindexable. And naming an operand is what makes a **compilation** reusable: a compiled predicate
  is keyed by the expression it came from and the ruleset version, so one edit to a shared name
  refreshes every grant that embeds it (§10,
  [D-114](../decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation)).

### Grammar, precedence, and the canonical rendering

```
expr    := term ( '+' term )*
term    := operand ( ( '*' | '-' ) operand )*
operand := EVERYONE | MEMBERS
         | OLDER '(' n ')' | YOUNGER '(' n ')'
         | ATTENDED | PLACED | CONFIRMED | ON_WAITLIST | ORGANIZERS
         | ROLE '(' name ')' | GROUP '(' name ')'
         | PERSON '(' person ')'
         | AUDIENCE '(' code ')'
         | '(' expr ')'

  OLDER(n) and YOUNGER(n) read person.birth_date AS OF THE DATE THE CHECK IS MADE,
  so `MEMBERS * OLDER(13) * YOUNGER(19)` reaches different people on different
  dates with no write, and can(..., on date) for a past date answers for that
  past date. Their argument is an INTEGER — the only operand argument in the
  registry that is not an entity reference (§*The selector registry*). There is
  no comparison operator anywhere in this grammar: no '>=', no '<', no bare AGE
  -- which is where D-060's refusal of a rule engine lives.  See the prose
  under this block, and D-107.

  '+', '-' and '*' are the whole operator set, each with one spelling. OLDER
  and YOUNGER are ordinary named operands, composed by the same three
  operators as every other row.

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

- `+` union, `*` intersection, `-` difference — three operators, one spelling each. `MEMBERS *
  OLDER(13) * YOUNGER(19)` is an ordinary term.
- **There is no comparison operator in the language.** No `>=`, no `<`, no bare `AGE`: an operand is
  a registry row and `AGE >= 15` has no row to be, which is the whole of D-060's protection now
  (§*Author in sets*, and [D-107](../decisions/round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)).
- **`*` and `-` bind tighter than `+`; `*` and `-` bind equally, left to right; brackets override.**
- **The canonical rendering prints every bracket, always.** The rendering is derived from the rows
  and is what every screen shows; if it is also kept as a column for search, it is a copy and the
  rows win (see §*The expression tree*).

**Printing every bracket is not a courtesy, and the example is the proof.** Under this precedence,
the unbracketed `MEMBERS - GROUP(schuzka2026-1) * COUNSELORS` means *"everyone except the counselors
in that group"*, which is **not** what its author meant — they meant *"all counselors not in that
group"*, whose stored form is `(MEMBERS - GROUP(schuzka2026-1)) * COUNSELORS`. The editor rewrites
what is typed into canonical form before saving, so **no expression in this system is ever read
bare**; and once everything is stored fully bracketed, changing what binds tighter later changes
nothing already stored.

**A hand-typed sum of twenty people is a left-to-right chain, so it prints as nineteen nested pairs
of brackets.** That is what "storage and display both say what was written" buys, and it is asked
for. If it turns out unreadable, the answer is that a set of people big enough to be unreadable is a
`person_group` — not a flattening rule invented in advance (D-105).

### The selector registry

**`selector_type` is a seeded table, not an enum**
([D-101](../decisions/round-10b.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree)):
**the language becomes data.** The parser reads its reserved words from it, the editor builds its
dropdown from it, and the write path checks arity against it. It is the shape `grant_scope_type`
already has.

**Fields** (`selector_type`)

| Field | Kind | Notes |
|---|---|---|
| `code` | text, required, unique | The reserved word: `MEMBERS`, `ROLE`, `PLACED`. |
| `name` | text, required | For the editor's dropdown. |
| `takes_argument` | boolean, required | Whether the code **may** be written with an argument. The arity check reads this column and nothing else. |
| `binds_to_item` | boolean, required | True exactly when the **argument-less** form means "relative to the item being checked" ([D-102](../decisions/round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)). |
| `argument_type` | text, optional | Which table the argument names a row of — `role`, `person_group`, `person`, `event`, **`audience`** — **or a scalar: `integer`, the argument kind `OLDER` and `YOUNGER` take ([D-107](../decisions/round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)). Six values, five of them entity kinds and one of them not an entity.** Absent exactly when `takes_argument` is false. This is what the save path compares against the grant's item type, which is a reason the registry is doing real work and not merely tidying. **It is not always a `grant_scope_type`**: `person` never was and `audience` never will be, because a grant is never *about* an audience — it is aimed *through* one. The two coincide for exactly the item-scoped operands, which is the set the binding check reads. **A scalar argument is never in that set**, since `OLDER` binds to nothing. |
| `description` | text, optional | The sentence a writer reads before using it. `AUDIENCE` carries its gloss here, because the name misleads without one. |
| `is_system` | boolean, required | Default true, and **every seeded row is true with no row planned false.** This column exists to make the table refuse an edit, not to mark a category. |

**Seeded selectors**, in full, because this table *is* the language — **thirteen rows, all of them
shipped**. The number is only the cheap form of the real check: *this list is the language*, so an
operand appearing anywhere other than here — in a screen's dropdown, in a resolver's switch, in a
decision entry that never reached this table — is a bug, and §13 keeps the document-level report
that hunts exactly that. Every seeded row is either a rule about people or takes an argument, so the
registry carries no special case left to explain; `OLDER` and `YOUNGER` are the
only rows whose argument is not an entity reference.

| `code` | Argument | Binds to item | Means |
|---|---|---|---|
| `EVERYONE` | never | no | Any person, including those with no account and no membership. |
| `MEMBERS` | never | no | Holds a membership live on the checked date — the same predicate the membership gate applied ([D-039](../decisions/round-02-03.md#d-039--member-permissions-require-a-current-paid-membership)). |
| `OLDER` | required (**`integer`**) | no | **The people who are `n` years old or older on the date being checked**, from `person.birth_date` — the only operand in the registry whose argument is **a number rather than a row** ([D-107](../decisions/round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)). It is a row here for the reason the whole table exists: **it is a named operand, and it denotes a set of people** — the same shape of thing `MEMBERS` denotes, which is a test over membership rows and stores nothing either. **A person with no birth date is not in the set**, as a person with no membership row is not in `MEMBERS`: that is an ordinary answer, **not a resolution failure**, and §11's report of unresolved leaves must not page about it (§*Evaluation*). **Its membership moves at midnight with no write** — see §*The cost of composition*. |
| `YOUNGER` | required (**`integer`**) | no | **The people strictly younger than `n` on the date being checked** — `OLDER`'s mirror, `n` and up against under `n`. **Each is the complement of the other, and the language has no complement a bare leaf can carry** (only `-`, which needs something on its left), so both are seeded rather than one being spelled out of the other; that is the whole of their relationship, and it is why **there is no `AGE_BAND` row and none is wanted** — a band is composed out of the operators every other row is composed with, and `OLDER(13) - OLDER(18)` is thirteen to seventeen. Same argument kind, same date rule, same non-failure for a missing birth date. |
| `PERSON` | required (`person`) | no | **One named person** — a set of one, which is a set, so it is a named operand like every other row: the exception for a named individual lives *inside* the expression that granted the rule, next to the thing it exempts ([D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)). A hand-written set of several people is written the same way, as a sum of these — `PERSON(a) + PERSON(b)` — because a set of one is a set, and a set of three is the same thing three times ([D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)). There is no separate "hand-typed list" operand and no table behind one. |
| `ROLE` | required (`role`) | no | Holders of that office live on the checked date (`role_holder`). |
| `GROUP` | required (`person_group`) | no | Members of that group live on the checked date (`person_group_member`). |
| `AUDIENCE` | required (**`audience`**) | no | **The value of another saved audience's expression**, evaluated live on the checked date — the one operand whose argument is a *decision about access* rather than a roster, and so the one that makes a rule namable ([D-103](../decisions/round-10b.md#d-103--an-audience-may-name-another-audience)). |
| `ATTENDED` | optional (`event`) | yes, `event` | `response = attending`. |
| `PLACED` | optional (`event`) | yes, `event` | Attending **and not waitlisted** — **the capacity set**, the one the events module counts and the index already serves. |
| `CONFIRMED` | optional (`event`) | yes, `event` | `PLACED` **and** `is_confirmed` — holds a paid place. |
| `ON_WAITLIST` | optional (`event`) | yes, `event` | Attending and waitlisted. |
| `ORGANIZERS` | optional (`event`) | yes, `event` | Runs the event (`event_organizer`). |

**Two operands a reader might reach for are not in this table.** `LIST` is not an operand: a
hand-written set of people is a sum, `PERSON(a) + PERSON(b)`, written inside the expression like
every other set
([D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)).
`GUARDIANS` is not a selector either: guardianship is a channel carrying a `right_level` over a
child on the `guardianship` row, not a set a grant may be aimed at, and an operand naming it would
re-grant, one code at a time, what that channel grants whole
([D-113](../decisions/round-13.md#d-113--the-guardianship-channel-has-no-expression-guardians-is-not-a-selector)).

**Rules** (`selector_type`)

- Rows are platform-seeded. **Adding an operand is a decision entry plus a seed row**, never a row
  somebody types into a screen: each operand is a branch of the evaluator and a fact about stored
  data, and an editor that could invent one would produce an expression nothing evaluates — which
  then resolves to the empty set and denies quietly forever (§*Evaluation*).
- **The registry is organization-read-only, and saying that out loud is what makes "a closed
  language" true of a table rather than merely asserted.** Every row ships with the platform, every
  row is `is_system`, no screen edits this table, and no organization adds to it
  ([D-103](../decisions/round-10b.md#d-103--an-audience-may-name-another-audience)). *The language
  becomes data* means the parser and the editor read one place instead of three; it does not mean
  the language is extensible at runtime. **A `code` in this table with no shipped resolver arm is a
  deployment bug, and it surfaces as an empty set** — an operand that reaches nobody, an allow that
  allows nobody, and a deny that on the `-` side denies everybody. That is the whole hazard of
  calling a closed set "data", and it is why the seeding of this table is release engineering rather
  than configuration. **There is no third kind of row** — the taxonomy is *shipped and seeded*, and
  "seeded, marked system, but not implemented" is not a category this model allows, however useful
  it would be as a roadmap marker.
- **Every `code` is a reserved name** in the shared role / group / audience namespace
  (§*Names are one namespace*).
- `argument_type` is absent exactly when `takes_argument` is false, and names a real table exactly
  when it is true — **one exception: the scalar domain `integer`, which `OLDER` and `YOUNGER` take
  and which names no table because it names no row
  ([D-107](../decisions/round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded))**.
  Anything reading this column has to know the scalar case exists, and has to know what the scalar
  is *not* — **it is not a reference**. That is why §11's check 2 walks two keyless columns
  (`access_grant.scope_id`, `audience_operand.selector_arg_id`) and why the design's wider count of them —
  **seven**, kept in [00 §9](00-conventions.md#9-referential-integrity-rules) — never reaches an operand:
  an `18` sitting in `selector_arg_id` points at nothing,
  so there is nothing for a merge to repoint, nothing for a cascade to find, and nothing for the
  orphan scan to walk. The check counts *references*, and `18` is not one (§*A hand-named person is
  now a keyless reference*, where the argument kinds are enumerated).
- The four attendance tiers name columns of `event_registration` and nothing else. That is the
  requirement that keeps the writer's choice honest — picking between tiers only means something if
  the choices are the stored facts.

**Three operands are not in this table, and each absence is load-bearing.**

- **`PRESENT(<event>)` over `was_present` is refused, and this paragraph is the whole reason.** The
  reason is the failure direction: `was_present` is `NULL` until somebody takes a register, so an
  operand built on it would revoke a child's access to their own camp photos because a volunteer
  forgot to tick a box. That column is a safeguarding signal, *three-valued on purpose*
  ([D-067](../decisions/round-05.md#d-067--presence-is-a-three-valued-fact-on-the-registration)),
  and keeping it out of the selector language is what keeps it meaning "a person recorded this"
  rather than "this is who may see things". **It is refused because of what it would do on the `-`
  side of an expression when a volunteer forgets a tick box** — not because of what it is: a
  predicate over a column is an ordinary kind of operand
  ([D-107](../decisions/round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)).
- **`GRANTS` is refused.** It was wanted so that an expression could name *"the people reached by
  these grants"* — a bulk-editing affordance dressed as an operand. **An operand must resolve to a
  set of people, and a set of grants is not one:** the moment an expression can name the grant
  table, `MEMBERS - GRANTS(...)` is expressible, and a language in which a grant can subtract a
  grant is a language in which the answer to *"who may do this?"* requires evaluating the whole
  expression tree of every other grant to answer one check — the closure property of §*Author in
  sets* doing the job it exists for. The bulk edit it was asked for is real and is an **editor
  affordance** — select the grants, change their grantees, in one screen, which changes rows and
  leaves every stored expression meaning what it meant. **Refusing it here is what keeps that screen
  a UI feature instead of a resolver feature.**
- **`WHITELISTED` is not seeded, and the reason is that there is nothing to evaluate.** The nearest
  facts are `source = staff` (an organizer entered them) and promotion off the waitlist. Either it
  means one of those or it is a new column on `event_registration`, which is an events decision and
  not a selector decision, so it stays [an open question](../open-questions.md) rather than being
  implied by a word in a grammar. **An operand that reads no state is not a vocabulary item but a
  syntax error wearing one's clothes.** [F-20](../open-questions.md#f-20)
  is a question about whether the *feature* is wanted, not about whether the language could hold
  the word.

**`PERSON(x)` is a registry row, and a hand-named person is a set nobody maintains**: `PERSON(a)` is
created by being typed. That is tolerable for exactly one operand, at the size of one person,
because the alternative — a second grant aimed at that person, which stays legal and is arguably
clearer for a permanent exception — leaves the exception invisible next to the rule it exempts. A
grant aimed at one person is the ordinary expression of a temporary exception, and its cost is not
the typing: a typed person is a `selector_arg_id` with no foreign key behind it, and §*A hand-named
person is now a keyless reference* is where the repointing requirement that hangs on that lives.

### What `LIST` is, said plainly — withdrawn by D-105

**`LIST` is not an operand and `audience_member` is not a table.** The answer to *"plus Honza"* is
`PERSON(a) + PERSON(b)`, written in the expression where every other set in this language is written
([D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)).

**Naming three people inside a grant must not mean making them members of a `person_group`.** A
group's members are true when no grant points at them
([D-098](../decisions/round-10a.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority)),
so editing a roster to move one grant's reach edits a set that other grants read — and it invents a
group nobody talks about. The answer to *"plus Honza"* is `PERSON(honza)`, and the answer is not a
roster edit. An exception written this way is invisible to every other grant until somebody opens
this one and has no name of its own, and `AUDIENCE(x)` still resolves to another audience's whole
expression and nothing less, so nobody can reach into the middle of it from outside.

**The limits of writing people in the expression.** There are no per-person dates: `audience_operand`
carries no period and gains none, so a June-to-August exception is its own grant with its own period
([D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality))
— where there is one audience and one grant there are now two grants, and a reviewer asking *"what
does Honza have?"* must find both. There is no per-name provenance: `created_by` on a node answers
*"who last saved this tree"* and not *"who added Honza"*. *"Who was on this audience in 2026"* is a
recomputation over audit payloads that expire after 24 months
([D-088](../decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)),
so the question stops being answerable in 2028. And two writers can collide: a hand-written set is
one expression edited as a whole, so **whoever builds the editor owes this an optimistic-concurrency
check or a queue** — a silent lost update here quietly removes somebody's access, and nothing in the
schema will notice.

---

*Decisions behind this page: D-039, D-042, D-060, D-067, D-081, D-088, D-091, D-098, D-099, D-100,
D-101, D-102, D-103, D-105, D-107, D-113, D-114.*
