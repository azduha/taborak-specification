# Decision Log — Refinement round 10 — the deletions, part 2 (D-101 … D-104)

> Offices and groups as two tables of one shape, and the audience rebuilt as an expression tree over named sets.

[Refinement round 10 — the deletions, part 1 (D-097 … D-100) ←](round-10a.md) | [All decisions](index.md) | [Refinement rounds 11 and 12 (D-105 … D-108) →](round-11-12.md)

---

## D-101 — An audience is an expression over named sets, stored as a tree

**Status:** decided (from your answers)
**Date:** refinement round 10
**Follows:** [D-098](round-10a.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority),
[D-100](round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)

**Amends:** [D-091](round-09.md#d-091--a-permission-group-is-a-rule-and-a-list-at-once-and-a-rule-may-name-another-group)
in its third arm.
**Confirms:** [D-060](round-05.md#d-060--eligibility-is-capability-there-is-no-separate-rule-engine),
[D-011](round-01a.md#d-011--scope_id-on-access_grant-is-polymorphic-with-no-foreign-key).

**Your words.** *"A group can be used as a selector in the audience rule (e.g.
`MEMBERS - GROUP(schuzka2026-1) * COUNSELORS` — meaning all counselors that are not part of the group
`schuzka2026-1`)."* Asked which of two notations to build on: *"Would it be easier for the system if we
wrote an evaluator for each person (`MEMBER & COUNSELOR | ROLE(TREASURER)`) or as a union/difference of
groups?"* — and then: *"I dislike the lack of operand precedence. I would like to be able to use
brackets."* — and then: *"Can we not store it as expressions? Each row has two operands and one operator,
and the operands can be either another row or a selector."*

**First, the reframe that makes the notation question smaller than it looks.** `p ∈ (A ∩ B) ∪ C` **is by
definition** `(p ∈ A ∧ p ∈ B) ∨ p ∈ C`. The two notations you were offered are the same function written
from two ends, so the choice does not decide what the machine computes; it decides **what gets stored and
what a writer is allowed to say**. The answer is therefore both, split by direction:

> **Author in sets. Evaluate per person.**

A check asks about one person, so the resolver compiles the expression down to a predicate and never
materializes a set. An implementation that evaluates `MEMBERS` as a list of ids and then tests for
containment pays three thousand rows per request, which is the one way to get this wrong and the reason
the requirement is written here rather than left to whoever builds it.

**Why the set form is the source language, in one argument each.**

- **It is no weaker.** `-` is complement against `EVERYONE`, `*` distributes over `+`, so every boolean
  formula has an equal expression here. The predicate form buys **zero** expressive power.
- **It is the closed one, and that is the whole case.** D-060 refused a rule engine, and a per-person
  boolean language is the door to one: once `&`, `|` and `!` exist, the next operand somebody wants is
  `AGE >= 15` or `FEE_PAID`, and there is a parser standing there to accept it. A set language closes it
  **by rule instead of by discipline**: *an operand must be a named, materializable set of people*. An
  attribute is not a set of people. Guardianship is (`GUARDIANS(x)` is a set), age is not, and the line
  falls exactly where D-060 already drew it — eligibility stays capability.
- **The three workloads the corpus already promises.** "Who does this grant reach?" must be **shown,
  expanded, in front of a human** — D-091 made that a requirement on the screen, not a nicety, and a
  predicate can only report `true`, while a set *is* the answer. "What may a treasurer do?" (D-100) needs
  the person→set index, and `role_holder` and `person_group_member` **are** it; an expression is
  unindexable. ~~Caching ([F-6](../open-questions.md#f-6)) can
  key on an operand and be reused across every grant, and `role_holder` changes are the invalidation.~~ **This
  third workload was argued on a cache that [D-114](round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation) deleted, and it survives the deletion for a different
  reason: what a named operand makes reusable is a *compilation*, which is keyed by the expression and the ruleset
  version and therefore shared across every grant and every person, while the rows an operand reads are fetched
  live. The workload itself — showing a grant's reach to a human — was never the cache's job; the preview does it
  on open (`data-model/05` §*The cost of composition*).**
- **It is the schema that exists.** An audience's manual arm, its included groups, and `everyone` /
  `all_members` / `guardians_of` are already named sets; the only genuinely new symbols are `*` and `-`.
  Today's audience has **no intersection and no difference at all**, which is why your example was not
  writable in any notation.

**Grammar.**

```
expr    := term ( '+' term )*
term    := operand ( ( '*' | '-' ) operand )*
operand := EVERYONE | MEMBERS | LIST | PERSON '(' person ')'
         | GUARDIANS [ '(' person ')' ]
         | ATTENDED [ '(' event ')' ]     | PLACED [ '(' event ')' ]
         | CONFIRMED [ '(' event ')' ]    | ON_WAITLIST [ '(' event ')' ]
         | ORGANIZERS [ '(' event ')' ]              argumentless = bound, [D-102]
         | ROLE '(' name ')' | GROUP '(' name ')' | AUDIENCE '(' code ')'
         | name                                      bare; the shared namespace below
         | '(' expr ')'
```

**`MEMBERS` names a set the membership module already defines, and does not define it here.** It evaluates
`is_current_member(person)` — status `active` with a period covering the checked date, **no grace
coalescing**, because the renewal window is a date range for rejoining and not a state in which somebody
is a member ([data-model/03-membership.md §3](../data-model/03-membership.md#current-membership-queries),
[domain/06-authorization-model.md §6.1](../domain/06-authorization-model.md#61-members--the-membership-test-moved-into-the-expression)).
That is the whole reason the language works: an operand is the *name* of a set somebody else already
provably owns, which is what "materializable" has to mean for this to stay out of rule-engine territory.

*(The `AUDIENCE` arm is [D-103](#d-103--an-audience-may-name-another-audience)'s, added the same round
this entry was written, and it is the reason this grammar is marked as amended rather than final: an entry
that ships a grammar and then grows an arm is worth seeing to have grown one.)*

*(The `LIST` arm is since gone. [D-105](round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)
deleted it, and a hand-written set is now written the way every other set in this grammar is written — as
an operand, `PERSON(a) + PERSON(b)`. The arm is left printed here because this entry shipped it; the
registry that has to be true today has **thirteen** rows — twelve for the round that deleted
`LIST`, plus the two attribute rows
[D-107](round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded) added, minus
the `GUARDIANS` row [D-113](round-13.md#d-113--the-guardianship-channel-has-no-expression-guardians-is-not-a-selector)
deleted. **This footnote said "fourteen rows, not thirteen" until round 13, and a footnote whose number has to be
re-typed by whoever changes the table is the same defect the footnote itself is describing** — which is why it
keeps its own history rather than just its new number.)*

*(Two arms have been added since this entry shipped, also by
[D-107](round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded):
`OLDER(n)` and `YOUNGER(n)`. **No operator was added.** The boolean spellings `&`, `|`, `!` were proposed
along with them and **declined** — `+ - *` are still the only three, and a negation is still written
`EVERYONE -`. **This entry's grammar is therefore amended twice**, and the second amendment is the one that
changes what a writer may say: an age test is now statable in this language, which this entry's own appeal to
D-060 said it was not. The materializability test this entry leaned on is corrected there too — it was never
what was doing the work.)*

**Two arms the first draft of this grammar omitted, and both were load-bearing elsewhere in the round.**
`PERSON(x)` names one person — a set of one, so it passes the materializability test, and it is how
the membership gate's *"except Honza"* is written inside the expression that granted the rule in the first
place, which keeps the exception visible next to the thing it exempts. **(This entry's first draft credited
that pattern to `system.gate_exempt`, which [D-100](round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)
had already deleted in the same round: the waiver is an expression now, not a permission code. A live pattern
pointed at by a dead code is F-19's defect wearing a decision entry's clothes, so it is named rather than
quietly corrected.)** And **bare `name`**, because the
round's own control is written `MEMBERS * COUNSELORS`: an expression that does not parse is not a control.
`ROLE()` and `GROUP()` remain as explicit qualification, required in the canonical rendering.

**Both arms were still missing from the seeded registry when the registry was written, and that is worth
recording rather than fixing quietly.** [data-model/05a-audience-and-grammar.md §8](../data-model/05a-audience-and-grammar.md#the-selector-registry)
was written from the evaluator's arm list, not from this grammar, and an arm list copied from an
implementation is exactly the kind of source that loses an arm nobody had implemented yet. The registry
carries **thirteen** rows and `PERSON` is one of them: `takes_argument` true, `argument_type` `person`,
`binds_to_item` false. Its distinction from `LIST` is real and is why both survive — `PERSON(x)` is an
argument, so it composes and can be subtracted on its own, while `LIST` is one set of several people
belonging to one audience and subtracting it removes everybody on it. D-103's kitchen example needs both,
which is the proof that they are not the same operand wearing two names. The class of defect is
[F-19](../open-questions.md#f-19),
it arrived here in a second registry inside the same round, and
[D-104](#d-104--a-permission-codes-last-segment-is-an-action-and-a-registry-that-prose-contradicts-is-a-fiction)
is the answer to it.

> **Amended by [D-105](round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other),
> which deleted the half of this paragraph's distinction that was not `PERSON`.** The registry carries
> **twelve** rows; `LIST` is a tombstone where its row was. The finding stands on its own — an arm list
> copied from an implementation is what lost the arm — but the closing proof left with the thing it proved.
> `PERSON(x)` and `LIST` were never the same operand wearing two names, and they no longer have to be
> distinguished at all, because one of them was a table. What `PERSON` carries now, alone, is every
> hand-named person the language can name: the *"except Honza"* in `MEMBERS * ROLE(x) + PERSON(y)` — the
> expression that replaced the deleted gate's waiver, not a permission code of its own,
> and the run of leaves that spells out the set a list used to hold.

`*` and `-` bind tighter than `+`; **`*` and `-` bind equally, left to right**; brackets override. The rule
is arithmetic-shaped so nobody has to learn a table, with one deliberate departure from arithmetic: `-`
does **not** sit beneath `*`. The reason is the first expression anybody writes in this language —
`MEMBERS - GROUP(schuzka2026-1) * COUNSELORS`, meant as *"all counselors not in that group"* — which is
what left-to-right gives and is **not** what `*`-tighter-than-`-` gives. Precedence was chosen to match
the reading the writer already had, not to be defensible on other grounds.

**The canonical form prints every bracket, always.** Not for legibility, so that the paragraph above is
never load-bearing when somebody reads a grant two years from now: the stored form of the example is
`(MEMBERS - GROUP(schuzka2026-1)) * COUNSELORS`, the editor rewrites what is typed into that before
saving, and an implementer who reaches for arithmetic precedence in their parser builds a **different
expression** than the one the writer meant. **This entry's first draft got its own rule wrong** — it
asserted that the bare form had changed meaning, which is the `*`-tighter reading this entry then refused
— and the correction is worth keeping in place of the claim, because the mistake is exactly the one the
always-bracketed canonical form exists to make impossible: two precedence rules can sit in one document,
agree with each other in the abstract, and disagree the moment an expression is written without brackets.

**Storage: the tree you described, not a normal form.** Each row is a node: `operator` + `left_id` +
`right_id`, or a leaf's `selector_kind` + `selector_arg_id`. My alternative was to normalize to a union of
terms on save; **yours is better and the reason is the round's thesis** — the normalizer is the code
(distribute, dedupe, sort, survive blow-up), and a binary tree needs one evaluator of about fifteen lines
and keeps the writer's brackets instead of silently rewriting them. It also makes the depth limit the only
complexity bound, since `(A + B) * C` costs nothing. The rules that come with it:

| Rule | Where it is enforced |
|---|---|
| **Exactly one shape.** A node has `operator`, `left_id`, `right_id` and no selector; a leaf has `selector_kind` and no operator or children. | A check on the row — expressible, so it stays a constraint |
| **One parent, never a DAG.** `parent_id` lives on the child, so a node belongs to exactly one expression. A side table letting two expressions share a node is refused: editing the shared node would silently widen every grant using it, which is D-091's inclusion hazard re-imported | Structure, plus a CI check that no such table exists |
| **Cycles and depth refused when the row is saved** — walk the parent chain, refuse a revisit, refuse past `selector_depth_limit`. Structurally hard to build; refused rather than trusted, for D-091's own reason: *a hand-fixed row, a restore from before the guard existed*. **Amended by [D-103](#d-103--an-audience-may-name-another-audience):** the parent-chain walk sees one tree, and `AUDIENCE()` makes cycles possible *between* trees, so the guard is a reachability walk over the reference closure and the depth bound is counted there too. **Amended a second time by [D-105](round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other), which deleted the depth half of this row**: no parameter, no save-time bound, nothing to count — the walk stays and now guards termination alone, so this row is the cycle check with a history as a size check | The write path, exactly as `uq_audience_include_acyclic` was |
| **`selector_arg_id` has no foreign key** — it points at `role`, `person_group`, `audience`, `person` or `event` depending on kind | [D-011](round-01a.md#d-011--scope_id-on-access_grant-is-polymorphic-with-no-foreign-key)'s already-accepted trade-off, with its compensating orphan check |
| **An operand that does not resolve is the empty set.** Fail closed, in every direction, as §Evaluation of `data-model/05` already rules for audiences | The resolver |
| **The whole tree is fetched in one indexed read** by denormalizing `audience_id` onto every row, then assembled in memory. The read path never walks a parent chain. **Amended by [D-103](#d-103--an-audience-may-name-another-audience):** still one read per *audience*, but an expression that names another audience needs one per audience in its closure, so the honest claim is "no parent-chain walking", not "one query" | A stated implementation requirement |

**A naming ruling, written down because the table sits outside the naming conventions and somebody will
notice.** [`data-model/00-conventions.md §2`](../data-model/00-conventions.md#2-naming) admits two shapes —
a junction table named `<a>_<b>` alphabetically, and a lookup table named for the vocabulary it *is* —
and `audience_operand` is **neither**: it is a recursive structure, which the conventions have no rule for
because until now the model had none. It is kept for the reason the two existing rules exist: the name
should tell a reader what a row means. *Operand* is the word the grammar itself uses, so the table teaches
the language; `audience_node` was weighed and refused, because it names a graph shape and would leave a
reader who has not met the grammar no better off than `audience_thing`. Worth marking anyway, because it is
the reading that gets a migration wrong — singular-for-an-aggregate invites someone to build one row per
audience, when **the aggregate is the tree and a row is one node of it**. The diagram caption and the data
model's first line both say *rows of one audience's expression tree* for that reason. *This entry's first
draft justified the name by citing a naming decision that turned out not to exist* — the rule is a
conventions table, not a numbered decision, and a citation invented to settle an argument is the kind of
thing this log keeps a record of.

**`selector_type` is a seeded registry, not an enum.** Which operands take an argument, which may bind to
the item, and what type their argument is — that was three hard-coded lists (the `resolver_key` enum
written out in prose, the reserved-word list, the "meaningless without a `resolver_key`" rule). It becomes
one seeded table in the shape `grant_scope_type` already is: `code`, `takes_argument`, `binds_to_item`,
`argument_type`. The parser reads its reserved words from it, the editor builds its dropdown from it, and
the write path checks arity against it. **The language becomes data.** `audience.resolver_key` and
`scope_parameter` are deleted into it.

**Two sentences this paragraph needed, and did not have.** The registry is data, so say what is *not*
thereby open: **every `selector_type` row is seeded and `is_system`, and the organization may not add one at
runtime.** "Closed language" and "the language is a table" are contradictory unless the table is read-only
to tenants, and the read-only version is the one that keeps D-060's line — an operand is a shipped
predicate, not a thing a well-meaning registrar invents at 23:00. One consequence of that rule is a refusal
worth naming because it was nearly built: **a set of *grants* is not an operand.** `GRANTS(<ids>)` — "all
the people these grants reach", wanted as a way to move a bundle of grants at once — cannot be one, because
an operand must resolve to a set of **people**, and that is what a grantee is; the bulk operation it was
wanted for is a screen over the grant list, not a meaning a stored grantee can carry. Refusing it on the
type rather than on permissions is also what removes the awkward status such a row would have had: with
this rule, every seeded selector is a shipped selector, and there is no third kind. What the deletion of `resolver_key` does
leave unsaid is where a code meets its implementation: the resolver dispatches on `code`, and a seeded row
with no shipped resolver is a **deployment bug that shows up as an empty set**, fail closed like
everything else in the round. Second: this is what makes the age question answerable at all. Attribute
operands are refused above, so *"13 and over"* cannot be typed by a writer; under
[D-070](round-05.md#d-070--an-event-has-no-age-ceiling-the-grant-is-the-rule) the answer stays *"open the event to the
set whose members are that age"* — a group somebody maintains — and an `AGED_13_PLUS`-style operand becomes
legal **only** as a shipped selector, which is the one route this paragraph allows and the events document
was right to guess. **Nothing of the kind is seeded at go-live**, because one shipped age band is the
first step onto a ladder nobody asked for.

**The inclusion arm dies, and composition survives by changing hands.**
[D-091](round-09.md#d-091--a-permission-group-is-a-rule-and-a-list-at-once-and-a-rule-may-name-another-group) let a
group pull in other groups through `audience_include`, because a group could otherwise not be composed.
Under [D-098](round-10a.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority) a group's
membership **is** its dated rows, and composition now lives in the expression: `GROUP(kitchen) +
ROLE(troop_staff)` composes as much as an edge ever did. What goes with the edge table is a great deal of
machinery — the transitive walk, `include_depth_limit`, the write-time cycle walk over a *graph*, and
integrity check 20's job of asserting that the walk exists — because a **tree cannot cycle**, so the only
acyclicity guard left is the cheap parent-chain one. ~~That sentence is the second-most-durable claim in
this entry.~~ [D-103](#d-103--an-audience-may-name-another-audience), written the same round, lets an
operand name another audience, and a **forest of trees pointing at each other does cycle**: the save-time
reachability walk comes back — **and the depth bound that came back with it has since left again**,
[D-105](round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other) deleting the parameter
and the save-time check with it, so the walk returns alone and bounds termination rather than cost. What stays deleted is the
edge table and the materialized closure check 20 asserted — the edges are `AUDIENCE` leaves in the table
that already exists. What is genuinely lost: *"add the kitchen crew to
everything the troop-staff group is used for"* is no longer one edit. The answer is that named sets are
the composition mechanism now — name the composite once, aim grants at it — which is D-091's outcome
reached without a graph nobody could see the shape of.

~~**`audience_member` stays, re-roled as the `LIST` leaf.**~~ **Did, for one round, and
[D-105](round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other) deleted it and the
operand with it**, so what follows is kept as the argument it was and is now an argument about a table that
does not exist. It is the audience's own dated list of people, reachable in an expression as one operand. Merging it into `GROUP(x)` was weighed and refused twice over:
naming three people in one grant would create a row in the group browser that is not a group anybody
talks about, and D-098 already wrote the rule that keeps the two dated-member tables apart (a group's
members are true with no grant pointing at them; a selector's additions are meaningless outside the
selector). The duplication D-080 would flag is therefore **kept on purpose**, and the mitigation is the
one D-091 already required: the editor shows which mechanism each person arrived through.

**Names are one namespace, and that is a new dependency.** Bare `COUNSELORS` resolves against roles and
groups together, since `ROLE()` and `GROUP()` no longer have to disambiguate. So: names unique across
`role` and `person_group` — and `audience.code` joins them in [D-103](#d-103--an-audience-may-name-another-audience),
so it is three tables and **no single constraint spans three of them** — which means the write path carries it and an
integrity check asserts it exists, per [D-081](round-06.md#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now);
case, whitespace and separators folded on write; and **every `selector_type.code` is a reserved name**, so a
group called `MEMBERS` is refused at the save rather than silently rewriting every gate expression in the
system. What is stored is always kind + id, so a rename never rewrites a grant.

**Given up, once.** Storing a tree means two expressions with the same meaning are two different row sets,
so *"you already granted exactly this set on that row"* no longer falls out of storage. The route back is a
normalized **fingerprint** computed on save as a derived value used only for a warning — and if the
expansion overflows, skip the warning rather than refuse the write: normalization informing a human, not
gating one. Registered as an open question rather than promised. Similarly, DNF could have flagged
term-matches-nobody syntactically; the tree catches only `X - X` on a single node, so "this selector
reaches nobody" belongs to the editor preview that already has to exist.

**Two-way door?** The language is a wide-open door — it is one seeded table plus an evaluator, and an
operand can be added by any later decision. Precedence is the closed half: once expressions are stored in
canonical fully-bracketed form, changing what binds tighter changes nothing already stored, which is a
nice property and the reason the canonical rendering is a requirement rather than a convenience.

**See:** [data-model/05a-audience-and-grammar.md §8](../data-model/05a-audience-and-grammar.md#8-audience--grants-that-target-a-set-of-people),
[domain/06-authorization-model.md §6](../domain/06-authorization-model.md),
[glossary.md](../glossary.md) (Audience, Selector, Filling rule, Locality).

---

## D-102 — Nothing owns an event. The people connected to it are named by selectors that bind to it

**Status:** decided (from your answer)
**Date:** refinement round 10
**Follows:** [D-097](round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row),
[D-099](round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality),
[D-101](#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree)

**Reverses:** [D-058](round-05.md#d-058--an-event-is-a-dated-occasion-owned-by-exactly-one-unit)'s ownership,
[D-063](round-05.md#d-063--an-event-is-an-artifact-of-its-unit-not-a-child-of-it),
[D-094](round-09.md#d-094--the-root-unit-owns-every-imported-event).

**Amends:** [D-061](round-05.md#d-061--event-answers-are-read-by-that-events-organizers),
[D-062](round-05.md#d-062--organizers-are-appointed-on-the-event-not-granted),
[D-065](round-05.md#d-065--capacity-is-a-waitlist-threshold-and-organizers-may-exceed-it),
[D-067](round-05.md#d-067--presence-is-a-three-valued-fact-on-the-registration).

**Your words.** *"The events are owned by the root unit, so anyone with a permission to create an event can
create an event."* Then: *"I also want to include `ATTENDING(<event>)` (meaning is registered to an
event)"*, and on the tiers: *"let the user pick which they mean — mainly 'registered and confirmed', or
'registered and is confirmed or whitelisted or waiting for confirmation'"*, and on the argument-less form:
*"unparameterized form is great, I like that."*

**Decision.** **`event.org_unit_id` is deleted and there is no owner of an event.** An event is an item in
`grant_scope_type` like any other: `event.create` is held at the unit and creates an event; a unit-scope
grant reaches every event, because after D-097 there is no tier between the unit and the item and nothing
left to test. That deletes `can_event()`, the unit-authority rule that every event permission in this
module was reached through, and the integrity checks that guarded the owner column. D-063's famous
*artifact, not child* distinction has no artifact-and-unit pair left to distinguish, so it goes too.

**1. Bound operands.** Some selectors name a set **relative to the item being checked**, and write it
without an argument:

| Operand | On the item checked means | Explicit form |
|---|---|---|
| `ATTENDED` | said yes to this event | `ATTENDED(<event>)` |
| `PLACED` | said yes and is not waitlisted — **the capacity set**, the one §5 counts and the index already serves | `PLACED(<event>)` |
| `CONFIRMED` | holds a paid place on this event | `CONFIRMED(<event>)` |
| `ON_WAITLIST` | is waiting for a place on this event | `ON_WAITLIST(<event>)` |
| `ORGANIZERS` | runs this event | `ORGANIZERS(<event>)` |
| `GUARDIANS` | are the guardians of the person this item is about | `GUARDIANS(<person>)` |

**Every one of these is a seeded `is_system` row of `selector_type`, and `is_system` is not decoration
here.** [D-101](#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree) made the registry
read-only to an organization, so no tenant action can add an operand; what `is_system` guards is the
*platform's own* delete path, and it is also the flag that tells a reader this code is vocabulary rather
than content. The alternative — seeded but deletable — is a grant breaker with no crime attached: remove
`ORGANIZERS` and every `event.answer.view` grant in the system silently resolves to nobody while the audit
trail goes on reporting them live. `ROLE` and `GROUP` are the only kinds an organization populates, and it
does so by writing `role` and `person_group` rows, not registry rows.

The argument-less form is the important half, and it exists to kill a specific flaw: `ATTENDING(<event
1204>)` — *attending* being this round's starting word for the idea, refused above in favour of four tiers
that each name a stored column — written on event 1204 is one grant per event with the event's own id typed
into it, so "every
participant may see the other participants" is a thing you do 400 times and forget on the 401st. Bound,
it is one expression written the same way every time. Two rules make it safe:

- **A bound operand is legal only on an item-scope grant.** At the unit there is nothing to bind it to, so
  it is refused when the grant is saved, with the operand named in the message.
- **A bound operand is legal only on a matching item type.** `PLACED` on a `person_group` grant is refused
  because that item is not an event. This is `selector_type.argument_type` checked against
  `grant_scope_type` — which is a reason the registry of D-101 is doing real work and not merely tidying.

**2. `ORGANIZERS` is what replaces unit authority over an event, and it is not a contradiction of
D-062.** With the owning unit gone, "the people running this event" has no other expression, and
[D-061](round-05.md#d-061--event-answers-are-read-by-that-events-organizers)'s rule (answers are read by that event's
organizers) has to be *said* somewhere now rather than hard-coded in prose. It is said as a seeded grant:
`event.answer.view` on an event to `ORGANIZERS`. [D-062](round-05.md#d-062--organizers-are-appointed-on-the-event-not-granted)
and its *"an `event_organizer` row grants nothing"* both stand untouched, because **an operand is a set,
not a grant** — the same sentence §8 of the authorization model already repeats twice for `unit_leaders`
and audiences generally. What changed is only that the appointment is now *aimed at* by grants instead of
being special-cased inside the resolver.

**And a seeded grant carrying a bound operand is not one row — a sentence this entry omitted and the
events module then had to assume.** A grant's scope is the unit or exactly one item, and a bound operand
is legal only on an item-scope grant, so there is **no row** that says *"every event's answers go to its
organizers"*: the one row that would say it needs the unit as its scope, which is precisely where the
operand is refused. What is seeded is therefore a **template**, and the event-creation path instantiates it
beside the event row. Two consequences, both kept:

- **The import owes one instantiation per event row it writes** — this module's share of
  [D-093](round-09.md#d-093--the-one-off-import-may-create-memberships-both-ends-dated)'s shape, and cheap, because it
  is the same insert the event row already needs.
- **An event whose creation failed between the event row and the grant has nobody who can read its
  answers.** So the two writes are one transaction, and the check is a report — *events with no
  answer-view grant* — because "these two rows exist together" is
  [F-10 shape 1](../open-questions.md#f-10)
  and no layer this project owns can express it.

What the per-event row buys, and it is not accidental: answers-view is **revocable on one event** without
touching anyone's appointment, which is the kind of thing an organizer asks for the week before a camp.

**3. Four attendance tiers, and the refusal of a fifth.** You asked the writer to pick; picking requires
that the choices be the stored facts and not four new ideas, so each tier names columns of
`event_registration` and nothing else. `PRESENT(<event>)` over `was_present` is **refused**, and the
reason is the failure direction: `was_present` is `NULL` until someone takes a register, so an operand
built on it would revoke a child's access to their own camp photos because a volunteer forgot to tick a
box. That column is a safeguarding signal — *three-valued on purpose*, per
[D-067](round-05.md#d-067--presence-is-a-three-valued-fact-on-the-registration) — and keeping it out of the selector
language is what keeps it meaning "a person recorded this" rather than "this is who may see things".
`WHITELISTED` has **no stored state to name**: the nearest facts are `source = staff` (an organizer
entered them) and promotion off the waitlist. Either it means one of those or it is a new column on
`event_registration`, which is an events decision and not a selector decision, so it stays an open
question rather than being implied by a word in a grammar.

**4. The set a grant reaches is now per-item.** D-091's requirement that the editor show the expanded
people — *"the person saving the grant is looking at one row that mentions no person at all"* — can no
longer be answered from the grant alone: `PLACED` means different people on different events. So the
preview is computed **for an item** and says so on screen, and the cache key for a bound operand must
include the item ([F-6](../open-questions.md#f-6) amended).
**Import consequence:** the one-off import owes `event` rows and `event_registration` rows
([D-090](round-07-08.md#d-090--the-legacy-corpus-is-thousands-of-roster-rows-with-numbers-and-no-money),
D-093's shape), and it owes **no owner column**, which is the import-side saving D-097 already counted.
[D-094](round-09.md#d-094--the-root-unit-owns-every-imported-event) is deleted rather than reversed: there is no
column for an imported event to have.

**Two-way door?** Narrow and expensive. Re-introducing ownership means the owner column, the resolver
tier that reads it, and every check that the module deleted — but the selectors added here are not in the
way, because an ownership grant and a bound operand answer different questions and can coexist. That is
the difference between this and [D-097](round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row):
that entry deletes a dimension, this one removes a *test* and leaves the vocabulary intact.

**See:** [data-model/08-events.md §2, §8](../data-model/08a-event-guards-and-checks.md#8-projections-and-guards),
[domain/07-events.md](../domain/07-events.md),
[data-model/05c-access-log-and-resolver.md §10](../data-model/05c-access-log-and-resolver.md#10-the-resolver).

---

## D-103 — An audience may name another audience

**Status:** decided (from your answer)
**Date:** refinement round 10
**Follows:** [D-091](round-09.md#d-091--a-permission-group-is-a-rule-and-a-list-at-once-and-a-rule-may-name-another-group),
[D-098](round-10a.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority),
[D-101](#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree)

**Amends:** D-101's grammar, its "a tree cannot cycle" claim, and its one-indexed-read fetch.

**Your words.** *"What is a `LIST`? Also it should allow nesting AUDIENCEs."* The second sentence is the
decision; the first is the reason this entry has to be written at all, and §1 below is its answer.

### 1. What `LIST` is, said plainly

**`LIST` is this audience's own hand-typed list of people** — the rows of `audience_member`, which is the
one table in the module that holds persons rather than rules. It is the only operand that is not a rule
about people: `MEMBERS` is a test, `ROLE(vedoucí)` is an office with dated holders, `PLACED` is a join
against an event, and `LIST` is *the names somebody typed into this one grant*.

It exists so that **a grant can carry its own exceptions without creating a thing everybody can see.**
*"Everyone in the kitchen crew, plus Honza, minus the two people who left"* is
`(GROUP(kitchen) + LIST) - PERSON(a) - PERSON(b)`. The alternative — making Honza a member of
`GROUP(kitchen)` to reach one grant — edits a roster that other grants read, which is D-091's hazard, and
it also invents a group nobody talks about, which is the rule D-098 wrote. So `LIST` is scoped to the one
expression that contains it, is invisible in the group browser, and dies with the audience.

The name is the weak part of this design and the question you asked is the evidence: nothing in `LIST`
says *whose* list. The registry entry carries the gloss *"the people written into this audience"*, and the
editor renders the operand as `LIST (this audience)`. Renaming the code was refused only because the round
has already propagated it through four files and the gloss costs nothing; if it keeps causing this
question, the replacement is `ADDED`, which says where the rows came from.

> **Amended by [D-105](round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other),
> which deleted the operand this section exists to explain.** Read it as the answer to the question that was
> asked; what it describes is now a table that does not exist. **Two things in it survived, and one of them
> is why the deletion was cheap.** *"A grant can carry its own exceptions without creating a thing everybody
> can see"* is still true, and still the requirement — a run of `PERSON(…)` leaves scopes exactly as `LIST`
> scoped, is invisible in the group browser exactly as `LIST` was, and dies with the audience. D-105 removed
> a table without removing a capability, which is the test this round should have applied to `LIST` before
> keeping it. **The hazard paragraph is now the load-bearing one:** the choice in front of whoever composes a
> grant is between editing a roster that other grants read and writing the names into the expression, and
> D-105 turned that from a theoretical choice into the only choice, by deleting the third option where
> somebody could have both. **What is moot** is this paragraph: `LIST` needs no better name, and `ADDED` is
> not coming, because there is nothing left to call.

### 2. The decision, and the hole it closes in D-101

**An operand may name another saved audience: `AUDIENCE(<code>)`.** It is an ordinary selector — one row
in `selector_type`, `takes_argument = true`, `argument_type = audience`, and it therefore costs one seeded
row plus a resolver arm of about the same length as `GROUP`'s.

The stronger reason is that **D-101 did not deliver the answer it claimed to.** Having deleted
`audience_include`, it answered *"add the kitchen crew to everything the troop-staff rule is used for"*
with *"named sets are the composition mechanism now — name the composite once, aim grants at it."* But
under D-101's own grammar the only names available were `GROUP()` and `ROLE()`, and **both name a roster,
not a rule**: a group's members are its dated rows. The rule you wanted to reuse had no name to point at,
so the composite could be named only by copying its rows into a second audience — which is `audience_include`
with the copy step done by hand. Nesting is the half of that answer that was missing: **`AUDIENCE()` is
what makes a rule namable.**

It is also the arm that composes the two things the round kept apart. `ROLE()` names an office, `GROUP()`
names company, `ATTENDED()` names attendance; only `AUDIENCE()` names a **decision about access**, so it
is the only arm that can say *"the same people that grant may see the fee ledger, plus the accountant"*.

### 3. The three named sets, which are not the same thing

*Printed with four columns, because that is what this entry compared. **The `LIST` column is dead** —
[D-105](round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other) deleted the operand and
its table, and the honest reading of the column is that everything in it is now either in the `GROUP(x)`
column (a roster somebody maintains, with dates) or in the expression itself (a run of `PERSON(…)` leaves,
with none). The three-way version that replaced this is in
[data-model/05a-audience-and-grammar.md](../data-model/05a-audience-and-grammar.md#the-selector-registry); this one is kept
four-wide so the deletion has something to be measured against.*

| | `GROUP(x)` | `AUDIENCE(x)` | `LIST` |
|---|---|---|---|
| What it is | A dated roster somebody maintains | A saved expression, evaluated live | Rows on this one audience |
| Who may change who is in it | `person_group.member.manage` | `audience.update` on that audience | whoever may edit this audience |
| Does it exist outside a grant? | **Yes** — D-098: a group's members are true with nothing pointing at them | No — it exists to aim a grant | No |
| *"Was she in it on 1 June 2024?"* | **Answerable**, from the dated rows | **Not answerable** past the audit window | Not answerable |
| Sensitive as | ⚠ company | 🔒🔒 authority | 🔒 |

That fourth row is the honest cost and it is the D-100 distinction replayed one level down. `GROUP(x)` is
materialized, so it keeps a history you can be asked about; `AUDIENCE(x)` is a live rule whose past shape
survives only in the audit trail, and [D-088](round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)
expires those payloads after 24 months. So *"who could see this child's data in 2024?"* is answerable when
the grant pointed at a group and **is not** answerable when it pointed at a nested audience. A rule whose
reach cannot be reconstructed is still the right tool for a rule — the roster is the wrong tool for
*everyone over 13* — but the gap should be closed by the report in §5, not by pretending the question has
an answer.

### 4. Rules that come with it

| Rule | Why, and where it is enforced |
|---|---|
| **A reference names a `code`, not a name, and only audiences that have one may be referenced.** `audience.code` is optional and unique-where-set; naming stays opt-in, and an unnamed audience is simply not composable. The leaf may not point at a null code — a check reading another table, [F-10 shape 3](../open-questions.md#f-10). | Audiences were allowed to be anonymous before this round and there is no reason to force a name onto a grant's private addressee list. |
| **The code joins the shared namespace** of D-101 — `role`, `person_group`, `audience`, and every reserved `selector_type.code`. Still no single constraint spans three tables: the write path carries it and an integrity check asserts the write path exists, per D-081. | A name that resolves two ways is a silent grant. |
| **Bare names do *not* resolve to audiences.** `MEMBERS * COUNSELORS` stays a role or a group; the audience arm must be written `AUDIENCE(veterans)`. | Adding a third table to bare resolution would change what existing stored expressions mean, and the explicit form costs four characters at the one place where being careful is the point. |
| **Cycles are refused across audiences, at save.** | See below. |
| ~~**Depth is bounded over the expanded tree, not the local one** — the bound is the same `selector_depth_limit`, counted after references are followed.~~ **Deleted by [D-105](round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other).** The reasoning here was sound and is now moot: a bound measured per-audience *is* a bound on nothing, and this round's answer was to measure it across the closure, which D-105 then refused to keep at all. **What survives is the walk this row needed in order to count anything** — the reachability walk over the closure, refusing a cycle rather than a length | Was the write path; now nothing, and the widest-audience report is a convention ([F-21](../open-questions.md#f-21)) |
| **An audience may not be ended or deleted while a live grant, or a live audience reachable from a live grant, names it.** Refused at save; the reverse lookup is a query over `audience_operand` rows whose `selector_kind = 'AUDIENCE'`. | Without this, "ended" would be a way to silently empty an expression, and under `-` an empty operand makes the result **wider**. |
| **The same refusal extends to `person_group` — ruled here, in the round after the row above — and it has to be ruled in both directions, which the audience row above does not say loudly enough.** Ending a group that something live names is refused; **so is writing a grant whose expression contains `GROUP(x)` onto a group that is already ended**, or naming an ended group from an audience. Two causes put a row on the report and only one of them is a broken write path: a rule that constrains *ending* leaves the second cause untouched, and the hazard is identical either way. | The group module found it by writing the opposite as the safe direction: a live grant on an ended group *is* safe on the allow side and **widens a deny** on the `-` side, which is the same asymmetry wearing a different table's clothes. The argument is identical, so the check is: refused at save in both directions, over `audience_operand` rows whose `selector_kind = 'GROUP'`. |
| **`ROLE(x)` needs no such rule, and the difference is worth naming.** An office has no way to be emptied quietly: there is no `role.retire`, no status, and deletion is already refused while holder rows exist. | A group has a lifetime, so ending it is one click that empties a set. A role's members are ended one row at a time, on a screen that shows each person. **The hazard is a property of the shape, not of the idea**, which is why this row is an exception list rather than a third copy of the check. |
| **An unresolvable leaf is still the empty set.** On the allow side that is quiet and safe; on the deny side `EVERYONE - <nothing>` denies everybody, which is loud. | The loud failure is the one you want. The quiet alternative is discovered in an audit, two years late. |
| **Naming an audience requires reading it,** and grants no read of it to the people it contains. | Fail closed, and *see what you name* is already D-091's requirement. |

**One of D-101's sentences is now false and stays struck.** *"a tree cannot cycle, so the only acyclicity
guard left is the cheap parent-chain one"* — true of one tree, false of a **forest of trees pointing at
each other**, which is what this decision makes possible. `audience_include` is not coming back: the edges
are the `AUDIENCE` leaves, so there is no edge table, no transitive walk over rows, and no
`include_depth_limit`; what returns is the write-time reachability walk D-091 already required, over a
graph built at save time from rows that already exist. The machinery D-101 counted as deleted stays
deleted; only its confidence was wrong.

### 5. What this costs, stated as the hazard it is

**Editing an audience changes grants you did not make.** Add a person to `AUDIENCE(veterans)` and every
grant that names it now reaches them — including grants their owner wrote for a different purpose, and
including grants this editor cannot see because they are not theirs. This is not a new failure mode:
`GROUP(x)` has had this property since D-091, and the round accepted it there for the reason it is
accepted here, which is that **a named set is worth being reusable and a reusable thing has more than one
user**. The mitigation is D-091's, extended to the second user: saving an edit to a referenced audience
shows *which grants name it, and at what depth*, before it commits, and the same listing is what closes
the history gap in §3 as a report rather than as a reconstruction.

*Assumption:* the listing is cheap at the sizes this organization runs at, because the edges are indexed
rows in the table that already holds every expression. Unverified at any size, and a slow save screen is
a real risk if the audit-and-import corpus's row-count estimates are wrong.

**Two-way door?** Narrower than D-101's and wider than D-102's. Removing nesting later means finding every
stored `AUDIENCE` leaf — they are one indexed query — and inlining the subtree it pointed at, which
changes no grant's meaning on the day it runs and makes every one of them unmaintainable afterwards. So:
the door closes quietly rather than loudly, which is the reason the reference listing is a requirement rather
than a suggestion. **The depth bound used to be named beside it in this sentence, and
[D-105](round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other) deleted it**, so the
listing is alone now and the thing that replaced the bound is a report with no named reader
([F-21](../open-questions.md#f-21)).

**See:** [D-101](#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree) for the language
this adds one arm to, [data-model/05a-audience-and-grammar.md §8](../data-model/05a-audience-and-grammar.md#8-audience--grants-that-target-a-set-of-people)
for the table, and [D-091](round-09.md#d-091--a-permission-group-is-a-rule-and-a-list-at-once-and-a-rule-may-name-another-group),
whose inclusion edge this replaces for the second time.

---

## D-104 — A permission code's last segment is an action, and a registry that prose contradicts is a fiction

**Status:** decided — **by the assistant at the close of round 10, not from an answer of yours.**
Reversible, and cheap to reverse today; the day the first grant row exists it becomes a migration, which is
the only reason it is written as a decision rather than fixed as a typo.
**Date:** refinement round 10

**Resolves:** [F-19](../open-questions.md#f-19).

**Follows:** [D-055](round-04.md#d-055--the-permission-catalog-is-deliberately-comprehensive-and-granular),
[D-068](round-05.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle),
[D-072](round-06.md#d-072--the-documentation-carries-no-sql-the-schema-is-the-orms-job),
[D-075](round-06.md#d-075--money-arrives-from-a-bank-api-a-payment-is-requested-by-variable-symbol-and-qr-code),
[D-081](round-06.md#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now),
[D-101](#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree).

### 1. What happened to the QR capability, which is the part worth reading

F-19's third instance was a permission code named two ways in one round: the event door code, written
`event.qr` in one place and `event.qr.rotate` in another, against a catalog that states its naming patterns
as descriptions of the codes it already had.

**It was not resolved by choosing a spelling. The capability is gone.** Grepping the closed round finds
neither string anywhere in the corpus — not in the catalog, not in the events module, not in the ERD, not in
this log. What survives of it is F-19's own description of the dispute.

What happened, stated plainly: **a capability entered this round as prose, was half-designed in the course of
arguing about its name, and left as prose** — swept away by the same parallel rewriting that introduced it,
with no entry in this log involved at either end. Presence is what
[D-067](round-05.md#d-067--presence-is-a-three-valued-fact-on-the-registration) and
[EV-5](../open-questions.md#ev-5) left it: somebody
holding `event.presence.mark` records who came, with a clipboard if necessary. The only QR code in this system
belongs to a payment, and [D-075](round-06.md#d-075--money-arrives-from-a-bank-api-a-payment-is-requested-by-variable-symbol-and-qr-code)
already rules that **a QR code is a rendering, not data** — it encodes three stored facts and is worth keeping
no row of.

**So the answer to "did we decide not to have check-in codes?" is no, and that is the finding.** Not a typo,
not a disagreement about morphology: a thing was possible in prose, argued over as though it were in the
model, and removed without ever having been in the model. The registry — the one place a permission legally
exists, since D-072 made these documents the specification rather than a description of a schema — never had
a row, so nothing refused anything. A reviewer who had asked "which seeded row carries this?" would have
ended the argument in one sentence, and nobody asked, because the argument was written in two files that
both looked like they were describing something real.

**Closed as follows: there is no QR capability, seeded or deferred, in the events module or anywhere
else.** If door scanning is ever wanted it arrives as an open question, then as a decision entry naming the
permission, the artifact that gets rotated, and who may reprint it — not as a code appearing beside a
paragraph about a door.

### 2. The naming grammar, promoted from a description to a rule

The catalog described two shapes — `<resource>.<action>` and `<resource>.<subresource>.<action>` — and the
dispute could not be settled by them because **both readings of `event.qr` fit the description.** A
description of how existing names happen to look cannot arbitrate a new name; that is why the `answer` /
`answers` case was easy (the catalog was self-consistent, so naming it the arbiter worked) and the QR case
was not. Three rules for a code being **added**, which is the only moment they cost nothing:

| Rule | The test, and what it refuses |
|---|---|
| **The last segment names the action.** | Read the code alone and ask *what does this let me do?* `event.grant_access` answers it; `event.qr` does not. A noun-final code states an object, and since [D-099](round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality) a grant states exactly one thing — a grant of an object would need a second sentence to say what it permits, and a second sentence is where a permission's real scope always hides. |
| **A middle segment names something the schema stores.** | `answer` is `event_answer`, `presence` is a column of `event_registration`, `contact`, `credential`, `member`, `participant`, `request` are all rows. **`qr` is nothing** — D-075 is explicit that it is a rendering of a symbol, an amount and a recipient. **A permission may not be built out of an artifact the database does not keep**, because a grant has to be checkable against stored state and there is none. This is the substantive test the QR case needed, and it decides the case without appealing to morphology at all. |
| **No grade words, and no prefix.** | `admin`, `all`, `everything`, and any code whose meaning is "every sibling under this prefix" — [D-068](round-05.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle) deleted sixteen of them and computed the wrong answer for `dependent.admin`. **Restated here as a rule about codes that have not been written yet**, which is the only form of that decision that can still prevent anything. |

**One exception, named, because a rule with an unnamed exception is a rumour:** `system.admin`. Its last
segment is not an action and it stays. It survives because its meaning is *defined by the resolver* — checked
outright, `applies_to = unit`, never reachable through an item grant — rather than read off its name, and
because D-068 exempted it in so many words rather than by omission. **It is the only code in this system
allowed to be a noun, and the exemption is not a precedent**; `<resource>.admin` is exactly what rule 3
refuses and exactly what was deleted.

**The rules were applied to the registry as it now stands, and found nothing to correct**: of the
**sixty-six live codes in the catalog's tables**, sixty-five satisfy both the action test and the stored-state
test, and the sixty-sixth is `system.admin`. That is worth recording precisely because it is a null result —
the corpus was already following the rule, the rule was nowhere written, and the QR capability arrived anyway.
**A convention that is followed and not stated fails exactly once, on the first thing nobody thought to
compare.**

### 3. The report, adopted

F-19's recommended option is adopted: **before a round closes, every dotted token in prose is diffed against
the seeded registries** — `permission.code`, `selector_type.code`, `grant_scope_type.code`, `reason_code.code`,
and the seeded audiences — in both directions, so the report says which tokens name no row *and* which rows
no prose names.

- **It is a report run by hand.** This repository has no build step and no CI to hang a check on, so
  [D-081](round-06.md#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now)'s
  wording applies exactly: **a convention, not a guard.** Saying that is part of adopting it, not a caveat
  appended afterwards.
- **It would have caught all four instances, including the one this round has not yet noticed.** The fourth:
  `PERSON(` is written into [D-100](round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)
  and [D-101](#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree) and used in four module
  pages, while the seeded `selector_type` registry — copied from the evaluator's arm list instead of from
  D-101's grammar — carried twelve rows with no `PERSON` in them. **So a control the round wrote for itself,
  `system.gate_exempt` as `MEMBERS * ROLE(x) + PERSON(y)`, did not parse,** and the pages that noticed
  resolved it by reading `PERSON(y)` as `LIST`, which is the wrong reading: `LIST` is one set belonging to one
  audience, so subtracting it removes everybody on it. D-101's registry amendment adds the thirteenth row.
  **Two registries, one round, same defect** — which is the strongest argument this entry contains for the
  report, and it was found by reading, in a file nobody had been asked to check.
- **Allow-listing is the cost and it is not small:** illustrative codes, and deleted codes shown struck on
  purpose, both match no live row. The report is worth running only if its allow-list is re-read rather than
  frozen, which is the same discipline the struck-text rule already imposes on this log.
- It runs **on the documents**, because there is no schema to check against
  ([D-072](round-06.md#d-072--the-documentation-carries-no-sql-the-schema-is-the-orms-job)). That is the condition that
  makes the whole class possible: **the prose *is* the specification, so prose is free to contradict the
  registry, and there is no compiler to notice.**

### 4. What this is worth, and how it fails

**Two-way door.** Wide for the grammar, which renames nothing today. Already closed for `system.admin`'s
exemption, which every round since D-068 has leaned on. And irrelevant for the report, **which cannot be
violated — only forgotten.** That is this decision's failure mode and it is the only one: nothing in the
system will ever notice a code drifting from its row, including after this entry, because the enforcement
adopted here is a person remembering to run a script.

**What would make it obsolete.** An actual implementation, with a seed directory and a test that loads it.
Until then the registry and the prose are two copies of one thing
([F-10](../open-questions.md#f-10)'s general
shape, in its cheapest instance), and the report is the check that they still agree.

**See:** [F-19](../open-questions.md#f-19),
which this closes, [data-model/05a-audience-and-grammar.md §8](../data-model/05a-audience-and-grammar.md#the-selector-registry)
for the registry (**thirteen rows today** — back to thirteen, which is the number this sentence started with
and not the set it counted: twelve for the one round
[D-105](round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other) owned, thirteen as it was
written, fourteen once [D-107](round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)
added two, and thirteen again after
[D-113](round-13.md#d-113--the-guardianship-channel-has-no-expression-guardians-is-not-a-selector) removed one — **five
numbers, the first and the last are equal, and they are not the same thirteen: the old one held `GUARDIANS` and
no age operands, this one holds both age operands and no guardian operand**), and
[permission-catalog §1](../appendix/permission-catalog.md#1-conventions) for the naming patterns, which are
now rules and are written there as such.

---
