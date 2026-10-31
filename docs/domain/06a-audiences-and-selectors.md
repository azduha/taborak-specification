# Audiences and Selectors

The language a grant is aimed at a set of **people** in: the expression grammar, the seeded selector
registry, the rules that keep the tree safe, and what a grant's reach is recorded in. Every set this
language names is a set of people, and a grant may instead name one person or one registered key — and
a key is inside no set this language can name
([06 §10a](06-authorization-model.md#10a-a-key--a-caller-that-is-not-a-person)). This is the audience half
of [06-authorization-model.md](06-authorization-model.md) and continues its numbering at §6.2 — read that
page first for scopes, channels, grants, the resolver and precedence.

### 6.2 Audiences — an expression over named sets

A grant names a **person, an audience or a registered key — exactly one of the three, never two**
([D-042](../decisions/round-02-03.md#d-042--grants-may-target-audiences-not-only-individuals),
[D-116](../decisions/round-16.md#d-116--a-caller-that-is-not-a-person-is-a-registered-key-and-a-key-is-a-third-grantee-kind)).
An audience is **an expression over named sets of people**, stored as a tree of binary nodes and aimed at
by a grant
([D-101](../decisions/round-10b.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree)).
Fields, storage rules and the write-path checks are in
[data-model/05 §8](../data-model/05a-audience-and-grammar.md#8-audience--grants-that-target-a-set-of-people);
what belongs here is the language, and why it is shaped like this.

> **Author in sets. Evaluate per person.**

A check asks about one person, so the resolver compiles the expression down to a predicate and
**never materializes a set**. An implementation that evaluates `MEMBERS` as a list of ids and then tests
for containment pays **a row per member, per request** — at the size
[D-112](../decisions/round-13.md#d-112--the-systems-scale-is-stated-hundreds-of-people-tens-of-registrants-per-event)
states, a few hundred rows, and every one of them is a row the answer never needed. That is the one way
to get this wrong, which is why it is a requirement rather than an implementation note, and **it has no
exception**: nothing in this design expands a set in order to warm a store, because no store of answers
exists ([06 §8](06-authorization-model.md#8-there-is-no-permission-cache-and-what-replaces-it)).

**What the rule does not forbid, because the batch API would otherwise violate it:** `which_of(people[],
code, item)` evaluates the predicate for **the people already in hand** — the rows of the page being
drawn — and is therefore a batched predicate, not an expansion. **What stays forbidden is deriving a set
in order to answer a question about one person**, which is the direction that costs a row per member and
returns an answer about one of them. The test is which side you started from: the person, or the set.

The two notations this language could have used — set algebra, and a per-person boolean formula —
describe the same function: `p ∈ (A ∩ B) ∪ C` **is by definition** `(p ∈ A ∧ p ∈ B) ∨ p ∈ C`. The choice
therefore never decided what the machine computes; it decided **what gets stored and what a writer is
allowed to say**. The set form won, and [D-060](../decisions/round-05.md#d-060--eligibility-is-capability-there-is-no-separate-rule-engine)
is the reason: a per-person boolean language is the door to a rule engine, because once `&`, `|` and `!`
exist, the next operand anybody wants is `AGE >= 15` or `FEE_PAID`, and there is a parser standing there
to accept it.

*Why a set language closes that by rule instead of by discipline:* **an operand must be a named operand
— a row of the registry**
([D-107](../decisions/round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)).
`OLDER(18)` is a row, and it denotes a set: the people who are eighteen or older on the date being
checked. `AGE >= 15` is not a row and cannot be one, because **the language has nowhere to put `>=`**.
**Every operand in the registry is a test with a set on the other side of it**, so reading one column
against one date (`MEMBERS`) is not a different kind of thing from joining one table against one period
(`GROUP(x)`) — nothing in the model stores the list of members either. That is what keeps the rule
engine out, and it does not depend on which predicates a reader happens to grant the status of "set".

**So: the vocabulary is open and the grammar is closed.** More attribute operands will arrive, as rows
and by decision; the three operators stay the three operators; and
[D-060](../decisions/round-05.md#d-060--eligibility-is-capability-there-is-no-separate-rule-engine)'s
decision stands untouched: no eligibility rule table, no prerequisite system, nothing evaluated anywhere
but in `can()`. A person may write an age gate out of the vocabulary; **the system applies none of its
own accord.** The premise behind opening the vocabulary is quoted in
[D-107](../decisions/round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded):
*the people writing these rules know what they are writing* — a claim about the authors and not about
the people a rule reaches, so the two limits drawn there are this page's business too.

### Grammar

```
expr     := term ( '+' term )*
term     := operand ( ( '*' | '-' ) operand )*
operand  := EVERYONE | MEMBERS
          | ROLE '(' name ')' | GROUP '(' name ')' | name
          | PERSON '(' person ')'
          | AUDIENCE '(' code ')'
          | OLDER '(' n ')' | YOUNGER '(' n ')'
          | ATTENDED | PLACED | CONFIRMED | ON_WAITLIST | ORGANIZERS
          | ATTENDED '(' event ')' | PLACED '(' event ')' | CONFIRMED '(' event ')'
          | ON_WAITLIST '(' event ')' | ORGANIZERS '(' event ')'
          | PRESENT '(' event ')'   ← considered and refused; never in the registry. See §Event sets
          | '(' expr ')'
```

`OLDER(n)` and `YOUNGER(n)` are **ordinary named operands** — `n` a whole number of years, read against
the birth date **on the date being checked**, which is why they sit in the column of the table below
headed "the set, on the checked date" rather than anywhere in a section about conditions.
`MEMBERS * OLDER(13) * YOUNGER(19)` — thirteen to eighteen, a band from two operands — is a set
expression in exactly the sense `MEMBERS * GROUP(cubs) * PERSON(a)` is, and it parses under the rules
below with nothing added to them.

**This block and §*The selectors* are copies of the registry** in
[data-model/05 §8](../data-model/05a-audience-and-grammar.md#the-selector-registry), **which is the registry** —
the seeded rows, not the prose. An operand that is not a seeded row does not exist however natural it
looks in a grammar, and copies of a table drift from it
([F-5](../open-questions.md#f-5));
nothing checks a copy, so treat the registry as the source and re-copy rather than re-derive.

**Boolean spellings are offered for this language and declined.** `p ∈ (A ∩ B) ∪ C` **is**
`(p ∈ A ∧ p ∈ B) ∨ p ∈ C`, so `&`, `|` and `!` would name three operators this grammar already has, and
`!A` is already written `EVERYONE - A` at the same cost once brackets are printed the way the canonical
form requires. **A notation that expresses nothing new is not free:** two spellings of one operator means
the canonical rendering has to pick one, the editor has to accept both, the write-path checks have to
reason about both, and two people's identical rules stop being textually comparable — which is the
property the canonical rendering exists to buy. **`+ - *` are the only operators**, and negation is a
subtraction from `EVERYONE`, which has the extra merit of printing the universe it negates against
instead of hiding it behind one character.

**There is no comparison operator, and that is where the safety of this language lives.** No `>=`, no
`<`, no bare `AGE`, no `FEE_PAID` unless `FEE_PAID` is a row of the registry with an evaluator behind it.
A writer composes named operands; **the vocabulary grows by decision, not by typing.**

**A hand-written set of people is a sum, not an arm**: `PERSON(a) + PERSON(b)`. There is no operand for
"the names somebody typed into this audience" and no table behind one
([D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other));
a set of one is a set, and a set of three is the same thing three times.

**Merging the hand-written names into `GROUP(x)` is refused, and the refusal is why the replacement is a
sum of `PERSON()` leaves rather than a group.** Naming three people in one grant would create a row in the
group browser that is not a group anybody talks about, and **a group's members are the organization's
record of who is in it, true when no grant points at it**
([D-098](../decisions/round-10a.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority))
— so editing a roster to move one grant's reach edits a fact that other grants read. `PERSON(a)` is the
answer that respects that rule, and `GROUP(kitchen) += Honza` is not. **`person_group_member` is the only
dated set of people the system stores.**

**Widening everything a named set is used for is not a single edit.** *"add the kitchen crew to everything
the troop-staff group is used in"* is one edit per rule that names it. Named sets are the composition
mechanism: `GROUP(kitchen) + ROLE(troop_staff)` composes as much as a naming edge ever did, in one grant,
and a composite used more than once is named once as a saved audience and aimed at (D-091). The language has
intersection and difference as well as union, which is why the counselor example below is writable at all.

Operators: **`+` union, `-` difference, `*` intersection.**

**Precedence: `*` and `-` bind tighter than `+`; `*` and `-` bind equally, left to right; brackets
override.**

**The canonical stored rendering prints every bracket, always.** The alternative is a grant whose
meaning is recoverable only by someone who memorized that table, and the reason this is a requirement
rather than a courtesy is the worked example below: the same string means different things under
different precedence, and a stored grant is read by people years later who did not write it. Because
canonicalization happens on save, **changing the precedence rule later changes nothing already
stored** — a nice property, and the second reason the rendering is a requirement.

*Assumption:* a bare `name` operand is legal. It is not in D-101's printed grammar and is required by
its prose twice over — without it, `MEMBERS * COUNSELORS`, which D-100 writes as an import control, does
not parse. Recorded in [../open-questions.md](../open-questions.md).

**Names are one namespace, and that is a dependency.** A bare name resolves against `role` and
`person_group` together, since `ROLE()` and `GROUP()` do not have to disambiguate. So names are unique
across both tables — and **no single constraint spans two tables**, so the write path carries the rule
and an integrity check asserts that it does
([D-081](../decisions/round-06.md#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now))
— with case, whitespace and separators folded on write. **Every `selector_type.code` is a reserved
name**, so a group called `MEMBERS` is refused at the save rather than silently rewriting every
expression in the system. What is stored is always kind + id, so **a rename never rewrites a grant**.

### The selectors

| Selector | The set, on the checked date | Argument | Notes |
|---|---|---|---|
| `EVERYONE` | Any person, including non-members and the public | none | Legal — and the reason the editor must show its reach (§*The cost lands on the editor*) |
| `MEMBERS` | Anyone who passes `is_current_member`, on the checked date | none | Evaluated live. [06 §6.1](06-authorization-model.md#61-members--the-membership-test-moved-into-the-expression) |
| `OLDER(n)` | Anyone whose birth date makes them `n` or more years old **on the checked date** | a whole number of years | [D-107](../decisions/round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded). The only operand in the registry whose argument is **not a thing** — an integer, so it references nothing: nothing to repoint on a merge, nothing for a cascade |
| `YOUNGER(n)` | Anyone strictly under `n` years old **on the checked date** | a whole number of years | The pair exists so the complement is not written `EVERYONE - OLDER(n)`, which is correct and unreadable. The two partition the population **among people who have a birth date**: someone without one is in neither, and that is not a failure — see §*The rules that make the tree safe* |
| `PERSON(p)` | Just that person | a person | How a named individual's exception lives inside the expression that granted the rule; since [D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other) also how several named people are written — summed |
| `ROLE(x)` / `x` | Holders of role `x` (`role_holder`) | a role name | |
| `GROUP(x)` / `x` | Members of group `x` (`person_group_member`) | a group name | |
| `AUDIENCE(code)` | Another saved audience's set, evaluated live | an audience code | [D-103](../decisions/round-10b.md#d-103--an-audience-may-name-another-audience); the one operand whose argument is a decision about access rather than a roster, so the one that can name another audience (§6.2) |
| `ATTENDED` / `ATTENDED(e)` | Said yes to this event / to `e` | optional event | `response = attending` |
| `PLACED` / `PLACED(e)` | Said yes and is not waitlisted — **the capacity set** | optional event | The set the events module counts |
| `CONFIRMED` / `CONFIRMED(e)` | Holds a paid place: `PLACED` and `is_confirmed` | optional event | |
| `ON_WAITLIST` / `ON_WAITLIST(e)` | Attending and waitlisted | optional event | |
| `ORGANIZERS` / `ORGANIZERS(e)` | Runs this event | optional event | Appointed on the event, and still grants nothing by itself (§*Event sets*) |
| `PRESENT(e)` | — | **not seeded** | §*Event sets*. Refused **by decision** — nothing in the language could refuse it as a kind, so the refusal is a rule about the failure direction |

**Guardianship is not a selector, in either spelling** — `GUARDIANS` and `GUARDIANS(p)` are not rows of
the registry and were never seeded
([D-113](../decisions/round-13.md#d-113--the-guardianship-channel-has-no-expression-guardians-is-not-a-selector)).
Guardianship is a **channel** carrying a `right_level` of `none`/`view`/`write` on the live
`guardianship` row, reaching **any action about that child** — wider than any grant an operand could
have assembled, and narrower in the only way that matters ([06 §1](06-authorization-model.md#1-the-three-channels-of-authority),
[D-074](../decisions/round-06.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular)).
An operand aimed at a child's guardians would therefore offer, one code at a time, a subset of what
those people already hold. A kept list of a child's contact adults is a `person_group`.

**Thirteen selectors, and this table is a copy of
[data-model/05a-audience-and-grammar.md §8](../data-model/05a-audience-and-grammar.md#the-selector-registry), which is the
registry.** Which selectors ship is settled: these thirteen, seeded, organization-read-only, and a
fourteenth is a decision entry plus a seed row
([F-5](../open-questions.md#f-5)).
A count printed in prose is a count somebody has to reprint when the table changes, and no check prints
it, so the registry row set is the number.

**A key can never be one of them.** No selector names a registered caller, no operand may hold one in
either of its reference arms, and a fourteenth row for "the integrations" was offered and refused: **a
caller is one row and never a set**, for the same reason an office is one person and never a rule — a set
is the wrong grain for a thing that must be individually revocable. So a grant aimed at integrations is
one grant per caller, and there is no set they are all in, `EVERYONE` included, since that operand reads
*any person*. **The registry stays at thirteen**, and the module's largest machinery is untouched: nothing
about a key is compiled, and `ruleset_version` still bumps on `audience_operand` plus `selector_type` and
on nothing else
([D-117](../decisions/round-16.md#d-117--a-key-is-never-inside-an-expression-thirteen-selectors-and-none-of-them-can-name-one),
[06 §10a](06-authorization-model.md#10a-a-key--a-caller-that-is-not-a-person)).

**Bound operands — the argument-less forms — are the important half, and they exist to kill a specific
flaw.** `ATTENDED(<event 1204>)` written on event 1204 is one grant per event with the event's own id
typed into it, so "every participant may see the other participants" is a thing you do 400 times and
forget on the 401st. Bound, it is one expression written the same way every time. Two rules make that
safe, and **both are enforced when the grant is saved**, refused with the operand named in the
message:

- **A bound operand is legal only on an item-scope grant.** At the unit there is nothing to bind it
  to.
- **A bound operand is legal only on a matching item type.** `PLACED` on a group grant is refused,
  because that item is not an event. This is `selector_type.argument_type` checked against
  `grant_scope_type`.

**`selector_type` is a seeded registry, not an enum** — `code`, `takes_argument`, `binds_to_item`,
`argument_type`. Which operands take an argument, which may bind to the item, and what type their
argument is are **columns of this table, not lists in code**: the parser reads its reserved words from
it, the editor builds its dropdown from it, and the write path checks arity against it. **The language
is data.**

### The example, worked

The organization wrote:

```
MEMBERS - GROUP(schuzka2026-1) * COUNSELORS
```

meaning *"all counselors that are not part of the group `schuzka2026-1`"*. Under the fixed precedence
— `-` and `*` equal, **left to right** — it parses as:

```
(MEMBERS - GROUP(schuzka2026-1)) * COUNSELORS
```

which is what its author meant, and **that is the string that gets stored**, brackets and all: the
canonical rendering of what was typed.

**The hazard is real even though this string lands safely, and that is exactly why the rendering is a
requirement.** Read with `*` taking the tighter binding — the other natural choice, and the one a
writer who thinks of `-` as "everything except" will assume — the identical text means:

```
MEMBERS - (GROUP(schuzka2026-1) * COUNSELORS)
```

*"everyone except the counselors in that group"*: a different set of people, and a **far wider**
grant — nearly the whole membership instead of a handful of counselors. The corrected bracketed form is
`(MEMBERS - GROUP(schuzka2026-1)) * COUNSELORS`, and that is what the editor writes to storage
whichever way the typed string parses, so **no stored expression is ever ambiguous and none is ever read
bare.** What canonicalization does *not* do is tell the writer, after the fact, that the expression they
typed meant the wide thing. That is the editor's preview, and it is the same requirement as §*The cost
lands on the editor*. The bare form does not *mean* the wide thing under this design; a parser with the
wrong table would *compute* it, and then the stored brackets would disagree with the answer.

### Event sets, and the two sets that are refused

**Nothing owns an event.** There is no `event.org_unit_id` and no unit-authority test standing behind an
event permission: an event is an item like any other, `event.create` is held at the unit and creates
one, and a unit grant reaches every event because there is no tier between the unit and the item and no
owner to test
([D-102](../decisions/round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)).
The people connected to an event are named by selectors that bind to it.

**`ORGANIZERS` is how the people running an event are named**, and it is not a
contradiction of
[D-062](../decisions/round-05.md#d-062--organizers-are-appointed-on-the-event-not-granted): *an
`event_organizer` row grants nothing* stands, because **an operand is a set, not a grant.** An
appointment is *aimed at* by grants; it is not special-cased inside the resolver. So the rule that
answers are read by that event's organizers
([D-061](../decisions/round-05.md#d-061--event-answers-are-read-by-that-events-organizers)) is *said*
where permissions are said: **a seeded grant of `event.answer.view` on an event, aimed at
`ORGANIZERS`.**

**Presence is refused, and saying so here is the point.** `PRESENT(<event>)` over `was_present` is not
a selector, and the reason is the failure direction: `was_present` is `NULL` until someone takes a
register, so an operand built on it would revoke a child's access to their own camp photos because a
volunteer forgot to tick a box. That column is a safeguarding signal, **three-valued on purpose**
([D-067](../decisions/round-05.md#d-067--presence-is-a-three-valued-fact-on-the-registration)),
and keeping it out of this language is what keeps it meaning *"a person recorded this"* rather than
*"this is who may see things."* Wherever presence tempts a reader, that is the answer.

**`WHITELISTED` does not exist — there is no stored state to name.** The nearest facts are
`source = staff` (an organizer entered them) and promotion off the waitlist. Either it means one of
those or it is a new column on `event_registration`, which is an events decision and not a selector
decision — **and that decision is made: refused, with no reserved name**
([D-148](../decisions/round-20.md#d-148--there-is-no-whitelisted-and-the-refusal-is-written-where-the-tiers-are)).
It stays unseeded **rather than being implied by a word in a grammar**, and the refusal lives where the
presence tiers are listed ([07a §9](07a-capacity-presence-and-forms.md#9-presence-what-actually-happened)).

### The rules that make the tree safe

The expression is stored as a tree: one row per node, a node being `operator` + `left_id` +
`right_id`, a leaf being `selector_kind` + `selector_arg_id`, with `audience_id` denormalized onto
every row so the read path is one indexed fetch and never walks a parent chain. **Nothing bounds how
tall or how wide an expression may get**: there is no depth or width limit on an expression, in the
column or in the code, and nothing stands in for one
([D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)).
*"A check costs a bounded amount"* is therefore **not** a property of this system: an expansion is
bounded only by acyclicity. **The tree is stored exactly as the writer wrote it** — one row per node,
two operands and one operator, left to right, no rebalancing — because a rebalanced tree is a different
expression from the one a person wrote, and storing *that* expression rather than a normalized
equivalent is the entire reason the tree exists.

- **Exactly one shape per row.** A node has an operator and children and no selector; a leaf has a
  selector and neither. Expressible, so it stays a constraint.
- **One parent, never a DAG.** A side table letting two expressions share a node is refused: editing
  the shared node would silently widen every grant using it. Structure, plus a CI check that no such
  table exists.
- **Cycles are refused when the row is saved, and the two walks that look for them are the only
  structural guard this module has.** Structurally hard to build, refused rather than trusted, for the
  reason D-091 gives for its own guard: *a hand-fixed row, a restore from before the guard existed.*
  **1. Inside one tree:** walk the parent chain from the row upward and refuse a revisit.
  **2. Across audiences:** follow every `AUDIENCE` leaf and refuse a cycle through them at any distance
  ([D-103](../decisions/round-10b.md#d-103--an-audience-may-name-another-audience)). A single tree
  cannot cycle; **a forest of audiences naming each other is not a tree**, so the walk over a graph is
  not dead code, and it must never be relaxed — an expansion that never terminates is the failure
  nothing else here is standing against.
  **The read path gets neither a hop counter nor a cycle check,** which is the whole design: a cap on
  the read path *becomes the thing that decides who a grant reaches*, in exactly the case where the
  data is already wrong.
  **The listing of what a rule names is a tab on the permissions page**, with a `Broken` and an
  `Unusual` section, computed when opened, with no cadence to record because nothing runs; it lists the
  rules that name something deprecated, hidden or disabled, or that fail to resolve at all
  ([D-109](../decisions/round-13.md#d-109--nothing-a-rule-names-is-deleted-deprecated-hidden-disabled--and-a-tab-instead-of-a-report)).
  **It is not a guard in D-081's sense** — nothing is blocked, no write is refused — but a report has to
  be remembered and a tab is where the person already is, which is the difference between a convention
  and a decoration. Unbounded cost is accepted at the stated size, and nobody is expected to go looking
  for a report (F-21).
- **`selector_arg_id` has no foreign key** — it points at `role`, `person_group`, `person`, `event` or
  `audience`, **five kinds of entity**, depending on kind, **or at nothing at all**, since `OLDER(n)` and
  `YOUNGER(n)` write their integer into the same column and an `18` is not a reference
  ([D-107](../decisions/round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)).
  It is
  [D-011](../decisions/round-01a.md#d-011--scope_id-on-access_grant-is-polymorphic-with-no-foreign-key)'s
  already-accepted trade-off, with its compensating orphan check.
  **Every hand-named person in the system is a value in this keyless column**, so **a person merge and a
  redaction must repoint every leaf naming the absorbed or erased person, in all five entity kinds.**
  Retiring a role, a group or an audience is not part of that duty: it is one write to that row, never N
  writes to N expressions
  ([D-109](../decisions/round-13.md#d-109--nothing-a-rule-names-is-deleted-deprecated-hidden-disabled--and-a-tab-instead-of-a-report)),
  so a leaf that names a retired thing is not possible. **`PERSON(x)` names a *person*, and
  [D-088](../decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)
  lets a redaction require the row to actually go. Erasure wins.** The reason the duty cannot be
  expressed anywhere better is stated in
  [shape 3](../data-model/00a-invariant-register.md#3-the-answer-reads-another-table-a-resolver-or-a-graph)
  — **the ORM has no key to follow.** And the failure is not tidiness: a leaf naming nobody is the empty
  set, which is quiet on the allow side and loud on the deny side, so **`EVERYONE - PERSON(x)` with an
  un-repointed `x` stops subtracting anybody and denies everybody.**
- **An operand that does not resolve is the empty set**, and an expression that cannot be evaluated
  reaches nobody. Fail closed, in every direction. **In a lawful database this has exactly one cause — a
  redacted person — because nothing else a leaf can name is deletable any more.** **A hand-edited row can
  still produce one**, and `disabled` deliberately produces the same answer by design (below), so the
  evaluator's behaviour must not change: the empty set, narrowing an allow and widening a deny, listed in
  the tab above.
- **Nothing a rule can name is deleted. It is given a state instead** — and the three states must stay
  three different things or one of them will quietly become another
  ([D-109](../decisions/round-13.md#d-109--nothing-a-rule-names-is-deleted-deprecated-hidden-disabled--and-a-tab-instead-of-a-report)):

  | State | Still resolves? | Offered when writing a rule? | Flagged? |
  |---|---|---|---|
  | **`deprecated`** | **yes, unchanged** | no — not addable to a new rule, not introduceable by editing one | **yes**, highlighted wherever the editor shows it |
  | **`hidden`** | **yes, unchanged** | no | no — it is not obsolete, it is not everybody's business |
  | **`disabled`** | **no — the empty set** | no | yes, **and it is the only state that changes an answer** |

  **The invariant that stops `deprecated` drifting into `disabled` is checkable and cheap: deprecating or
  hiding what an expression names must not change the set the expression resolves to.** That is the
  precise failure this whole design exists to make impossible — a rule that quietly stops granting
  because somebody tidied a list — so it belongs beside the two cycle walks as something a reviewer
  checks, not as a convention
  ([D-081](../decisions/round-06.md#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now)).
  **`disabled` is the loudest switch in this system:** it stops every rule naming that role, group or
  audience, in every scope, at once, and re-enabling restores all of them — a widening in which nobody
  edited a grant. So **the flag is an audited write that prints the rules it touches**, resolved before
  and after, which is the report shape D-104 and D-105 adopted for their own migrations, and it is a
  ruleset write (D-111); it is also the answer to *how do I turn off that whole naming without editing
  forty grants?*, which otherwise has no answer except a deny per grant. A deprecated or disabled name
  **stays reserved** (D-101), so nothing new can claim the word and split its meaning in two.

**The cost lands on the editor, not the resolver.** A grant's reach is not visible in the row that grants
it, and seeing it is a requirement on the screen rather than a nicety: the person saving the grant must
see **the people**, not the audience's name, because nothing in the grammar stops an expression from
containing `EVERYONE`, and because `PLACED` means different people on different events (D-091, D-102).
So the preview is computed **for an item** and says so on screen. That is a real amount of work for the
editor, and it is the only thing standing between a writer and a grant that reaches **everybody the
organization has**. At the sizes stated in
[D-112](../decisions/round-13.md#d-112--the-systems-scale-is-stated-hundreds-of-people-tens-of-registrants-per-event)
that is a few hundred people, which is not reassuring — it is the same warning with a number under it,
and the number says the preview will not be slow (F-15, F-16).

### What a grant's reach is recorded in

**"Who could read this in 2023?" is answered by the words, and that is the whole of the answer** —
*"Words only — the expression is the record"*
([D-110](../decisions/round-13.md#d-110--the-expression-is-the-record-of-whom-a-grant-reached)).
This page promises no other answer and stores no list that would be one.

- **The expression is the record of a grant's reach.** The preview still prints a resolved set before a
  save, and the audit row logs that printing as *a rendering on a date*, not as a statement of who was in
  it. A row saying *this grant reached these 214 people* starts decaying the night somebody's birthday
  falls; a row saying *this person wrote these words on this date about this item* cannot go stale.
- **What is refused beside it:** keeping the preview's list alongside the audit row. That is a roster
  table, and it would store — indefinitely, against
  [D-088](../decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)'s
  window — a per-person record of people who were **never granted anything**, only covered. This module
  refuses that trade whenever it is offered in another shape.
- *Why words-only is sound:* **nothing a rule can name is deleted** (§ above), so the nouns survive. A
  retired office still resolves; a deprecated group still resolves; a name stays reserved. Refuse to
  delete the nouns and keeping only the words is not an amputation: without that ruling this answer would
  mean *"the past is usually unanswerable"*; with it, the past is usually computable and what is left is
  honestly bounded
  ([D-110](../decisions/round-13.md#d-110--the-expression-is-the-record-of-whom-a-grant-reached)).
- **Answerable for `ROLE`, `GROUP` and `MEMBERS`** (all periods, all dated), **unanswerable for bound
  event operands** (`event_registration` records the current fact), and **lost for the hand-typed names
  once their audit payloads expire** — which is what
  [F-17](../open-questions.md#f-17)
  states rather than solves.
- **The conceded part, named so nobody finds it later:** editing a shared audience changes what **every
  grant naming it** has meant all along, because those grants hold a word and not a copy. **An edit to a
  shared audience is a retrospective edit to every rule that names it**, and a recomputation for May will
  use today's inner expression. D-103 accepted this as the price of reuse; D-110 records that it is also
  the reason a past-date answer can be *wrong* rather than merely missing. The control is D-103's — **the
  editor prints the resolved set before an edit to a shared expression saves**, so the person editing sees
  at least once the thing they are changing backwards in time. What is *not* kept is a history of inner
  expressions: **the audit trail records the edit, not the meaning that existed before it.**
- **There is no snapshot, and no route to one.** A materialized table of whom a rule reached is the
  roster just refused, and
  [F-7](../open-questions.md#f-7)
  is dissolved. What returns at
  [D-112](../decisions/round-13.md#d-112--the-systems-scale-is-stated-hundreds-of-people-tens-of-registrants-per-event)'s
  trigger is a materialized table **on its own merits** — a performance structure with a per-person
  invalidation handle and a stated staleness window, not a way back into the past ([06 §8](06-authorization-model.md#8-there-is-no-permission-cache-and-what-replaces-it)).

*Decisions behind this page: D-011, D-042, D-060, D-061, D-062, D-067, D-074, D-081, D-088, D-091, D-098, D-100, D-101, D-102, D-103, D-104, D-105, D-107, D-109, D-110, D-111, D-112, D-113, D-116, D-117.*
