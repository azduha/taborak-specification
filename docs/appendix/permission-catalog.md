# Appendix — Permission Catalog

Every permission code, its namespace, and the grant that carries it.

This is the **proposed** catalog, seeded in
[../data-model/05-authorization.md](../data-model/05-authorization.md#12-what-the-organization-starts-with).

> **Round 10 rewrote this page.**
> [D-097](../decisions/decision-log.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)
> deleted the unit hierarchy,
> [D-099](../decisions/decision-log.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)
> the level ladder,
> [D-100](../decisions/decision-log.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)
> positions, `role_permission` and the membership gate,
> [D-101](../decisions/decision-log.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree)
> the audience's rule/list/inclusion arms, and
> [D-102](../decisions/decision-log.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)
> event ownership. Thirteen codes here lost their subject, and five arrived for the two new tables.
> What changed shape is not only the list: a code is no longer paired with a level, so a row in this
> catalog is a capability and nothing more. **Whoever grants it says how far it reaches, for how
> long, and to whom** — in one row, whose grantee is an expression
> ([§1](#what-a-grant-is-and-what-it-used-to-carry)). **And §1's two naming shapes are rules now**, not
> descriptions of the rows below: the last segment names the action, a middle segment names something
> the schema stores, no grade words and no prefix — with `system.admin` named as the single exception
> ([D-104](../decisions/decision-log.md#d-104--a-permission-codes-last-segment-is-an-action-and-a-registry-that-prose-contradicts-is-a-fiction)).

> **Deliberately comprehensive and granular, and staying that way**
> ([D-055](../decisions/decision-log.md#d-055--the-permission-catalog-is-deliberately-comprehensive-and-granular)).
> This is a **menu, not a checklist.** Administrators assign people only the permissions they
> actually need; that is only possible if the capabilities exist as separate rows to assign.
> Further permissions arrive with the modules not yet specified — documents and communication.
> Events were on that list and are no longer: §8a carries their thirteen codes
> ([§10](#10-deferred-namespaces)).
>
> **This is the opposite disposition from roles, and the asymmetry is deliberate.** Roles are
> *runtime data* the organization invents ([D-052](../decisions/decision-log.md#d-052--roles-are-runtime-data-the-seed-set-is-not-a-specification));
> permissions are *capabilities the code implements*. You cannot assign a power the data model
> cannot express, so a comprehensive permission catalog costs only rows — while a
> comprehensive *role* list would be a specification pretending to be data.
>
> Codes are still **stable identifiers**: adding one is free, renaming one is a migration
> ([§1](#code-shape)). What is *not* yet settled is the exact contents — tracked in §12.

---

## 1. Conventions

### Code shape

```
<resource>.<action>               e.g.  person.edit
<resource>.<subresource>.<action> e.g.  event.answer.view
```

`resource` is always the first segment and matches `permission.resource`. Codes are
**stable identifiers** — the `display_name` may change, the code may not. Renaming a code is a
breaking change requiring a migration that rewrites every `access_grant` row naming it. Before
[D-100](../decisions/decision-log.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)
the same migration also rewrote `role_permission` rows; that table is deleted, and a grant is now
the only place a code is written down — which makes the rule *smaller*, not weaker.

**Those two shapes are rules for adding a code, and since
[D-104](../decisions/decision-log.md#d-104--a-permission-codes-last-segment-is-an-action-and-a-registry-that-prose-contradicts-is-a-fiction)
they are written here as rules rather than as a description of what is already in the tables below.**
As a description they arbitrated nothing: both readings of one disputed name fitted them exactly, and
that dispute ended with the capability deleted rather than either spelling chosen (§12). Three rules,
and the moment they cost nothing is the moment a code is added:

1. **The last segment names the action.** Read the code on its own and ask *what does this let me
   do?* `event.grant_access` answers it; a noun-final code states an object instead. Since
   [D-099](../decisions/decision-log.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)
   a grant permits exactly one thing, so a grant of an object would need a second sentence to say
   what it permits — and a second sentence is where a permission's real scope always hides.
2. **A middle segment names something the schema stores.** `answer` is `event_answer`, `presence` is
   a column of `event_registration`, and `contact`, `credential`, `member`, `participant` and
   `request` are rows. **A permission may not be built out of an artifact the database does not
   keep**, because a grant has to be checkable against stored state and there is none to check
   against: the payment's QR code is exactly that artifact, and
   [D-075](../decisions/decision-log.md#d-075--money-arrives-from-a-bank-api-a-payment-is-requested-by-variable-symbol-and-qr-code)
   already ruled it a rendering of three stored facts rather than data. **No code in this catalog
   spells `qr`, and none may** (§12).
3. **No grade words, and no prefix.** Not `admin`, `all` or `everything`, and not any code whose
   meaning is *"every sibling under this prefix"* —
   [D-068](../decisions/decision-log.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle)
   deleted sixteen of them and computed the wrong answer for the one it chose to exempt,
   `dependent.admin` — which [D-074](../decisions/decision-log.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular)
   then deleted too, for having no set left to stand for (the table further below). D-104 restates that
   decision as a rule about codes that have not been written yet, **which is the only form of it that
   can still prevent anything.**

**One exception, named because a rule with an unnamed exception is a rumour: `system.admin`.** Its
last segment is not an action, and it stays. It survives because its meaning is *defined by the
resolver* — checked outright, `applies_to = unit`, never reachable through an item grant (§7) — rather
than read off its name, and because D-068 exempted it in so many words rather than by omission. **It
is the only code in this system allowed to be a noun, and the exemption sets no precedent**:
`<resource>.admin` is precisely what rule 3 refuses and precisely what was deleted.

**The three rules were run against the sixty-six live codes in the tables below and corrected
nothing** — sixty-five satisfy both tests, and the sixty-sixth is `system.admin`. That null result is
the reason this section changed voice rather than its contents: **a convention that is followed and
not stated fails exactly once, on the first thing nobody thought to compare**, and the thing this
round failed on had never existed anywhere but in prose (§12). **Nothing in the schema will ever
notice a code drifting from its row** — the check D-104 adopts is a person remembering to run a report
over the seeded registries in both directions, which this repository can only ever do by hand
([F-19](../open-questions.md#f-19--closed--a-permission-code-is-a-row-prose-names-codes-and-nothing-checks-the-two)).

### What a grant is, and what it used to carry

**A grant is five things: a grantee (a person or an audience expression) + a scope (the unit, or
exactly one item) + one permission code + `effect ∈ allow, deny` + a period.** The answer it feeds:

> **allowed** when some live allow applies **and no** live deny applies.
> ([D-099](../decisions/decision-log.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality))

That is the whole of the precedence rule, and this catalog carries no column beside a code because
of it. What the level column used to promise, and what covers it now:

| ~~`access_level` used to~~ | Now |
|---|---|
| ~~bundle several codes under one word — "`manage` on this event"~~ | One grant row per code. A bundle is a **role** or an **audience**, which is what [D-068](../decisions/decision-log.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle) already said: *roles are the bundle* |
| ~~grade one act at two strengths — `view` against `edit`~~ | Two codes, plus `permission.right_kind ∈ read \| write` saying which side each sits on |
| ~~decide whether a grant was enough for the code being checked~~ | Nothing to decide. A grant names exactly one code, and the answer is yes or no |
| ~~order two grants that both apply — locality, [D-032](../decisions/decision-log.md#d-032--deny-is-absolute-locality-orders-allows-only)~~ | Nothing to order: two allows that apply produce one answer. **Deny is absolute, and that half of D-032 survives untouched** |
| ~~carry `revoked` as the bottom rung~~ | `effect = deny` on a grant row, and it is still asked first |

**Withdrawn by
[D-099](../decisions/decision-log.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality).**
The rank integer it rested on went with it
([D-012](../decisions/decision-log.md#d-012--status-strings-compare-by-rank-never-lexicographically)),
and so did `permission_level`, the table that mapped levels onto codes: the famous bug it guarded —
`'admin' < 'contribute'` comparing alphabetically and inverting the model — cannot occur in a system
with no levels, which is a better fix than the guard. The question that dies with the column is
*"what does `manage` give me on this event?"*: there is no such word, so there is no such lookup.
The question it buys is *"what exactly does this person have?"*, answered by reading grant rows.

**Two columns moved onto `permission` itself, and only one of them is comfortable.**

- **`right_kind ∈ read | write`** survives **only** so that
  [D-074](../decisions/decision-log.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular)'s
  guardianship channel has something to compare a permission against now that the ladder is gone:
  `none` covers nothing, `view` covers `read` codes, `write` covers both. Nothing else in the system
  compares it. **It is a column whose only job is one other mechanism, and saying so is cheaper than
  discovering it later** (§6).
- **`applies_to ∈ unit | unit_and_item`** is where a code may be granted at all, and it is checked
  **when the grant is saved**, not at check time: an item scope is refused for codes like
  `event.create` (an event cannot be created twice, so a creation permission attached to a thing that
  already exists answers no question) and `membership.terminate` (a membership is a fact about a
  person at the unit, not something an event owns). *The example D-099 gives for the second half is
  `membership.manage`, and this catalog has never carried a code of that name — §12 records that
  rather than minting it.* The `system` namespace is unit-only the same way, which is **who enforces
  now** for the old
  rule that `system.admin` can never arrive through an item grant
  ([D-081](../decisions/decision-log.md#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now)).

**Scope is two things, not a ladder.** A grant at the unit — the organization, of which there is one,
and which is a scope and never a row
([D-097](../decisions/decision-log.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)) —
reaches **every item of every type**. A grant on one item reaches that item and nothing else. There
is no tier between them and no relation on the item to test: no owner, no parent, no covering body.

### A grantee is an expression

Wherever this catalog writes a grantee, it is a legal expression in the selector language of
[D-101](../decisions/decision-log.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree):
the leaves `EVERYONE`, `MEMBERS`, `PERSON(person)`, `ROLE(name)`, `GROUP(name)`,
`AUDIENCE(name)`, the two age sets `OLDER(n)` and `YOUNGER(n)`, and the five event-bound sets
`ATTENDED`, `PLACED`, `CONFIRMED`, `ON_WAITLIST`, `ORGANIZERS` — each writable with its argument spelled,
or bound to the item being checked
([D-102](../decisions/decision-log.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it))
— combined with **`+` union, `-` difference, `*` intersection**, and brackets. **Those three operators are
unchanged: round 12 added two operands and no operator**
([D-107](../decisions/decision-log.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)),
so `(MEMBERS * OLDER(18)) - YOUNGER(6)` — brackets printed as always, since `*` and `-` bind equally and
the stored form never relies on a reader who memorized it — is an ordinary expression of the grammar that
already existed, and nothing in this file's grant rows, in `audience_operand`, or in §11's tables is
shaped differently for it.
**There is no comparison operator in the language** — no `>=`, no `<`, no bare `AGE` — and after this
round that, not any claim about what counts as a set, is the clause keeping eligibility rule engines out
([D-060](../decisions/decision-log.md#d-060--eligibility-is-capability-there-is-no-separate-rule-engine),
as amended by [D-107](../decisions/decision-log.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)).
**A hand-written set of
people is not a leaf and has no table: it is a sum**, `PERSON(a) + PERSON(b)`, because the leaf that used
to hold one and the table behind it are both deleted
([D-105](../decisions/decision-log.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)).

**Those thirteen leaves are the registry, not a sample of it** — fourteen for round 12 alone, until
[D-113](../decisions/decision-log.md#d-113--the-guardianship-channel-has-no-expression-guardians-is-not-a-selector)
removed a row that should never have been in the registry, and neither `GUARDIANS` nor `GUARDIANS(p)` is a
selector in its place: *"True, GUARDIANS should not be selectable in the audience, guardians can perform
ANY action (their read/write perms grant) on behalf of the child."* A guardian's authority is a
`right_level ∈ none | view | write` over a child, not a set this language resolves
([D-074](../decisions/decision-log.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular)).
They are the seeded `selector_type` rows:
the eleven that [D-101](../decisions/decision-log.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree)
copied from the evaluator's arm list and that survived it, plus `PERSON`, which arrived as the thirteenth
to repair a waiver expression that did not parse — the episode
[D-104](../decisions/decision-log.md#d-104--a-permission-codes-last-segment-is-an-action-and-a-registry-that-prose-contradicts-is-a-fiction)
settles — minus `LIST`, which left in the round after
([D-105](../decisions/decision-log.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)),
plus `OLDER(n)` and `YOUNGER(n)`, which arrive this round and are the first operands whose argument is a
number rather than a row of some table
([D-107](../decisions/decision-log.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)).
**So the count has been twelve, thirteen, twelve, fourteen and now thirteen, and it is still not a
contradiction: the second number counted an arrival, the third a departure, the fourth two arrivals more,
the fifth a row that should never have been counted, and only the last is a fact about today.** This page
has now printed the registry's size twice and been wrong twice, which is the lesson rather than an
excuse: **a page repeating a registry's row count is a copy of the registry**, and a copy is stale the
moment the original moves. This corpus already ruled that an ordinal and a count are different facts —
*"the thirteenth to arrive"* and *"one of the twelve that remain"* were both true of `PERSON` at the same
time — and round 12 is the round where **one of them moved twice**, so the rule now has a worked example
rather than an assertion: **the ordinals are durable and the counts are not.** Every number in that
sentence except the last is a true sentence about history and will stay true forever; the last one is a
sentence about the seeded rows as of this round and is the only one the next round has to re-check.

**Two of these leaves move with the calendar, and that is new.** `OLDER(n)` and `YOUNGER(n)` read
`person.birth_date` **as of the date the check is made**, so a person joins or leaves one of those sets
with no write of any kind, one person at a time, at midnight — and a check asked about a past date
answers for that past date, which is a question no snapshot design could answer. **Exactly these two, and
no others:** the other dated operands — `ROLE`, `GROUP`, `AUDIENCE` — move when somebody makes a write with
a date on it, which is a different claim and is not the one this sentence makes. Nothing is stored, so there
is nothing to invalidate — and since round 14 there is no stored answer left to invalidate either:
~~the cache is rebuilt nightly in full, immediately on any write to the ruleset, and on explicit request, and
an answer that moved without one of those is simply allowed to be a night stale~~
([D-111](../decisions/decision-log.md#d-111--the-permission-cache-is-rebuilt-nightly-on-any-ruleset-change-and-on-request))
is retired by [D-114](../decisions/decision-log.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation),
which deletes the answer cache and with it the claim that anything could be a night stale. A check resolves
against live rows, so **a birthday moves an age set at the instant it happens**, with no job standing between
the birthday and the answer. **What this costs the catalog is a sentence it used to be able to write:** *this
is cheap because it is cached.* It cannot write that any more, and the cheapness argument is now one indexed
read of the checked person's grant rows per request, plus the two batch reads — `can_many(person, codes[],
item?)` for a screen's affordances and `which_of(people[], code, item)` for a list's people. No table changes
when a person turns eighteen, so there is no row to expire and no cache of *membership* to
keep — which is exactly the property age **bands** would not have had, and why bands are not in this design.
The editor's preview is a workbench and never was a record, and **the record is the expression**: the audit
row logs the words, and the preview is logged as *a rendering on a date* rather than as a statement of who
was in it ([D-110](../decisions/decision-log.md#d-110--the-expression-is-the-record-of-whom-a-grant-reached),
§12).

**A leaf outside that registry does not parse**, and that sentence is now the whole of what keeps a rule
engine out: an operand must be a **named** operand — a row — and `AGE >= 18` is not a row and cannot
become one while the language has nowhere to put `>=`. The test this corpus gave for the same rule, from
[../domain/06-authorization-model.md §6](../domain/06-authorization-model.md), is quoted here so that this
file's rule is not read as resting on it again: ~~"an attribute is not a set of people; guardianship is
(`GUARDIANS(x)` is a set), age is not, and the line falls exactly where D-060 already drew it."~~ **That
test is withdrawn, and it was never holding anything up**: `OLDER(18)` is the set of people who are
eighteen or older on the date being checked, exactly as `MEMBERS` is the set of people who pass
`is_current_member` and `ROLE(name)` is the set of people who hold that office — every operand in the
registry is a test with a set behind it, and reading one column is not a different kind of thing from joining
one table — and `MEMBERS` would have failed the old test too, since nothing in this system stores the member
list. D-060's decision stands; its sentence does not
([D-107](../decisions/decision-log.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)).
**The quoted sentence turned out to be wrong in a second way, and the quotation stands anyway:** its parenthetical
treated guardianship as a set the language resolves, and round 13 ruled that it is not one in either spelling
([D-113](../decisions/decision-log.md#d-113--the-guardianship-channel-has-no-expression-guardians-is-not-a-selector)) —
which is a reason not to quote that sentence as a test, never a reason to rewrite what this file once printed.
The refusals below are operands people ask for that the registry does not carry.

**Every expression below is printed in the canonical stored form, which brackets every bracket,
always.** `*` and `-` bind tighter than `+`; `*` and `-` bind equally, left to right; and the stored
string never relies on a reader who memorized that
([../domain/06-authorization-model.md §6.2](../domain/06-authorization-model.md#62-audiences--an-expression-over-named-sets)).
So `event.answer.view` on an event is aimed at `ORGANIZERS`, an open camp is opened by
`MEMBERS`, a gated office is `MEMBERS * ROLE(treasurers)`, and the exemption for one named person is
`(MEMBERS * ROLE(treasurers)) + PERSON(jan)` — a second grant aimed at a person is the other way to
write the same thing, and keeps the exception off the expression everyone else reads.

**Three refusals belong next to the language, because each is a temptation this catalog creates, and a
reader could now mistake the first two for type errors. They are not, and never were**
([D-107](../decisions/decision-log.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)):
a selector is allowed to be a hard-coded computation in the resolver, because `MEMBERS` is one today, and
an operand may read a column against a date, because `OLDER(n)` does. **Nothing is kept out of the
registry for what it is** — the word that sounded like it did, ~~"not materializable"~~, is retired with
the test it belonged to — **so every refusal standing here is an argument about consequences, which is
what all three have always been.**

- **`PRESENT(<event>)` is not seeded, on the argument that always carried it.** `was_present` is `NULL`
  until somebody takes a register, so an operand over it would revoke a child's access to their own camp
  photos — a leader's access to their own camp — because a volunteer forgot to tick a box. Presence stays a
  three-valued safeguarding signal
  ([D-067](../decisions/decision-log.md#d-067--presence-is-a-three-valued-fact-on-the-registration)),
  and nowhere in this file is it a set anyone may be granted over. **The language would not stop anybody
  writing it now, and that is exactly why the consequence has to be the thing that says no.**
- **`WHITELISTED` is not seeded because there is nothing stored to evaluate**
  ([F-20](../open-questions.md#f-20--closed--whitelisted-stays-unseeded-because-there-is-no-state-to-evaluate-and-the-feature-arrives-anyway)):
  no type system is objecting — there is no type system left to object — but an operand with no argument,
  nothing bound to the checked item and no column behind it is a word pointing at a state this system does
  not keep. **F-20 is closed, and closed by that reasoning rather than by a decision about the feature:** the
  operand stays unseeded because there is nothing to evaluate, and the feature it was wanted for arrives as
  grants anyway. Whether the *feature* is wanted at all is an events question, and this catalog no longer
  carries it — **which is the closure's real content: a selector question that was really an events question
  went back to the events module instead of being answered here.**
- **A bare name is one namespace across roles and groups**
  ([D-101](../decisions/decision-log.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree)),
  which makes §11's office names a load-bearing vocabulary, and makes every selector code a reserved
  name: an office called `MEMBERS` is refused when it is saved. **Two more reserved names arrive with this
  round** — an office, a group or an audience called `OLDER` or `YOUNGER` is refused on the same rule, and
  it is the parser rather than a review that saves a reader from `OLDER(18)` meaning an office with that
  name.

### There is no wildcard, except `system.admin`

Every capability in this catalog is **narrow and explicit**. A check for `X.y` is satisfied
by an exact grant of `X.y` — or by `system.admin`, which is checked outright and is the only
permission in the system that means *everything*.

```
A check for 'X.y' is satisfied by: an exact grant of 'X.y', OR 'system.admin'.
```

There are **no per-resource `admin` permissions.** The earlier convention that every resource
should expose an `<resource>.admin` subsuming its narrower codes — a prefix match computed in
the resolver — was **reversed by [D-068](../decisions/decision-log.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle)**,
which also deleted the resolver branch that implemented it.

**"Someone who can do everything about events" is a role, not a permission** — the
organization composes it from the thirteen `event.*` codes. That is the division D-052 already
drew: **the code implements capabilities, the organization groups them.** A per-resource
`admin` was the code guessing at a bundle on the organization's behalf. Since
[D-100](../decisions/decision-log.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)
the composition is literal: a role confers nothing, so the bundle is thirteen live grants whose
expression names `ROLE(x)` — thirteen rows you can read, which is what D-068 was reaching for.

**The cost, because it is real.** A new narrow permission is *not* automatically covered by the
offices that should imply it; someone must write the grant row. Integrity check **18** is the safety
net the wildcard used to be — it lists permissions **no live grant names**, which is what a missed
bundle looks like now that no role carries a permission list of its own. It fails **closed**: a
capability goes unheld and somebody says so, rather than a capability going unmeant and nobody
saying so.

### Two things named "admin", which are not the same thing

The word used to be ambiguous three ways. Three rounds of deletion left one, and the others are
recorded as deleted rather than quietly dropped:

| Shape | What it is | Status |
|-------|-----------|--------|
| ~~`access_level.admin` (rank 40)~~ | A **grant level** — how much authority a grant carries, in `view` < `contribute` < `manage` < `admin`. Used by `permission_level` to decide whether a given grant satisfies a given permission. | **Deleted** — the whole ladder, top rung included, by [D-099](../decisions/decision-log.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality). This row read "real, untouched" until round 10, which is what "untouched" was worth |
| `system.admin` | The **one wildcard permission**: everything, carried by a grant at the unit and never on an item (`applies_to = unit`) | **Real, and the one named exception** — the only code in this system allowed to end in a noun. Exempted by name in words by D-068, and named as an exception by [D-104](../decisions/decision-log.md#d-104--a-permission-codes-last-segment-is-an-action-and-a-registry-that-prose-contradicts-is-a-fiction), because its meaning is defined by the resolver rather than read off the name. **Not a precedent** (§1) |
| `<resource>.admin` | A **wildcard permission code** implying every sibling on that resource | **Deleted** — all sixteen, by [D-068](../decisions/decision-log.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle), and refused in advance for codes not yet written by [D-104](../decisions/decision-log.md#d-104--a-permission-codes-last-segment-is-an-action-and-a-registry-that-prose-contradicts-is-a-fiction): a grade word, and a prefix read as a permission |
| `dependent.medical.admin`, `dependent.admin` | An **action** meaning "edit", paired against `.view` inside a sub-resource; plus a shorthand for the whole set | **Deleted** — by [D-074](../decisions/decision-log.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular), which reduced a guardian's rights to `none` / `view` / `write` |

**D-068 exempted `dependent.admin` on purpose, and D-074 withdrew the exemption.** The reason
D-068 kept it was sound at the time: it was not a prefix match inferred by code but a value a
person deliberately stored on one row about one child. What changed is not the reasoning about
wildcards but the thing it was a value *of* — there is no longer a set of guardian capabilities for
a shorthand to stand for. **Read the two decisions together before reinstating anything that
spells `admin`.**

### Namespaces

| Namespace | Resolved against | Channel |
|-----------|------------------|---------|
| *(absent)* | `access_grant` — aimed at a person or at an audience — and ownership | 1, 3 |
| `system` | `access_grant` **at the unit only** — `applies_to = unit`, so **never** on an item | 1 |

The channel numbers are the three in
[../domain/06-authorization-model.md §1](../domain/06-authorization-model.md#1-the-three-channels-of-authority):
grants, guardianship, ownership. **There used to be a fourth row in this table and a fourth channel
above it** — `role_assignment`, the channel a `system` permission could only be reached through.
**Withdrawn by
[D-100](../decisions/decision-log.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape):**
`role_assignment` is `role_holder`, a role confers nothing, and every code in this catalog —
`system.admin` included — arrives through the one grant channel now. *Who enforces that a `system`
code stays out of item grants: `applies_to`, checked on save*
([D-081](../decisions/decision-log.md#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now)),
not the absence of a channel.

**There is no `dependent` namespace** ([D-074](../decisions/decision-log.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular));
§9 explains what replaced it, and what was lost with it.

**That leaves the guardianship channel with no prefix to dispatch on, which has to be answered
rather than left implied.** It used to route on `dependent.`, and the reason for routing by prefix
was that **no caller should decide which channel applies** — otherwise the same authorization rule
gets implemented twice, once correctly. It now routes on a fact about the request instead of a fact
about the name: **the channel is consulted whenever the person the action is *about* differs from
the person performing it.** That is stronger than the prefix rule, not weaker — under the old rule a
guardian asking to change their child's address with a `person.contact.edit` code would not have
routed through guardianship at all, because the code did not carry the right prefix. Nobody chooses
a channel; the shape of the request selects it.

The `guardianship.*` codes are additionally satisfiable by **being a party to the row**, and not
only by a grant ([D-073](../decisions/decision-log.md#d-073--guardianship-is-administered-by-its-own-parties-not-by-staff)).

`system` permissions remain non-grantable on an item: `system.admin` must never be delegable to a
single event, a group, or an office. What enforces it is no longer the shape of the channel that
could carry it but a column on the code itself.

### Sensitivity marker

The **Sens.** column flags permissions that need extra care:

| Mark | Meaning |
|------|---------|
| ⚠ | Granting it exposes personal data |
| ⚠⚠ | Granting it exposes children's personal data — or the same about an adult, where the code reads a whole person record rather than one field of it. Since [D-083](../decisions/decision-log.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data) there is **no separate *health data* class to name**: the mark grades what a grant *exposes*, not which field the code points at |
| 🔒 | Granting it confers authority over the permission system itself |
| 🔒🔒 | The **escalating** half of that family: granting it changes what **other people** can do, not merely what the holder can do. `role.*` is marked this way in [D-100](../decisions/decision-log.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape), which names it "the most sensitive code family in the catalog" |
| ⛔ | Granting it can end someone's membership or standing |

These marks should drive UI warnings and the alerting in
[../data-model/05-authorization.md](../data-model/05-authorization.md#11-invariants-to-verify).
**A mark grades what a grant exposes, not the table a code names**
([D-086](../decisions/decision-log.md#d-086--a-sensitivity-mark-grades-what-a-grant-exposes-not-the-table-it-reads)),
and the two new families are placed by that rule: `person_group.member.manage` takes **⚠** because a
roster is a list of people, and `role.*` keeps **🔒🔒** because writing a holder row writes who may
hold everything else.

---

## 2. People and identity

| Code | Namespace | Sens. | Grants |
|------|-----------|-------|--------|
| `person.view` | — | ⚠⚠ | See person records — **all of them, including every descriptive value** |
| `person.create` | — | | Add a person record |
| `person.edit` | — | ⚠ | Change person details, including descriptive values |
| `person.contact.view` | — | ⚠ | See contact points |
| `person.contact.edit` | — | ⚠ | Change contact points |
| `person.merge` | — | 🔒 | Confirm identity matches and merge people — **and reverse a merge, and resolve a sign-up collision; there is no separate code for any of the three** |
| `person.redact` | — | 🔒 | Perform a GDPR-style erasure |
| `attribute.define` | — | | **Curate the vocabulary** of descriptive data — create, rename, merge or retire a code |

> `person.merge` and `person.redact` are separated from `person.edit` deliberately: both have privacy
> consequences far beyond editing a record. This paragraph used to justify the separation by calling
> both *irreversible in practice*, and
> [D-087](../decisions/decision-log.md#d-087--merge-chains-stay-because-reversing-a-merge-is-a-supported-operation)
> has withdrawn that premise for one of them — a merge can be reversed, and reversing it is a required
> operation. What survives the correction is the half the separation actually rests on: the merged
> **window** cannot be reversed, so the union of two people's permissions is real from the moment the
> merge commits, whatever is discovered afterwards. The separation stands on the narrower reason.
>
> **Three operations, and not one new code.** Round 8 introduced two capabilities and, each time,
> checked whether the catalog needed a row for it
> ([D-087](../decisions/decision-log.md#d-087--merge-chains-stay-because-reversing-a-merge-is-a-supported-operation),
> [D-089](../decisions/decision-log.md#d-089--one-live-account-a-colliding-sign-up-files-a-claim-and-creates-nothing)):
>
> - **Unmerge — reversing a merge a human approved: `person.merge`.** Undoing an identity correction
>   is the *same act* as making one, done by a named human, through the same queue, over the same rows.
>   A `person.unmerge` code would grade undoing a mistake as safer than making one. **Such a row stood
>   in §2 until round 8 and is removed here**; no seed role held it, so no role loses anything, and it
>   is recorded rather than quietly deleted because a reader of an older draft will look for it.
> - **Resolving a sign-up collision — working the claim a colliding registration files:
>   `person.merge`.** Resolving it is confirming or rejecting an `identity_hypothesis`, which is what
>   `person.merge` already means ([../domain/03-identity-and-legacy.md §4](../domain/03-identity-and-legacy.md#4-match-signals)).
> - **Linking a colliding sign-up to the person it matched: nothing, deliberately.** There is no
>   `account.link` and no `account_claim` table (§3). An automatic link once the e-mail verifies is
>   [D-004](../decisions/decision-log.md#d-004--no-automatic-merging-ever) under another name, and its
>   failure mode is one human's descriptive data becoming another human's record.
>
> The check itself is the point: this file is the only list of grantable codes, so a code minted while
> propagating a decision is a migration nobody decided.
>
> **Before [D-068](../decisions/decision-log.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle),**
> the way to keep them apart was to carve them out of `person.admin`'s prefix match — a
> special case in the resolver that was invisible in every role editor. Now there is no
> wildcard to carve out of, and the question moves somewhere reviewable: an office bundling all
> of `person.*` reaches them, and you can *see* it — since
> [D-100](../decisions/decision-log.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)
> deleted `role_permission`, the bundle *is* the live grant rows naming `ROLE(x)`, one row per code,
> dated and attributable. **The guidance that replaces the special case is in §11** — no seeded
> office mixes `person.merge` or `person.redact` with routine `person.edit`, and one that does should
> be named for what it is. This is now a report a person can read, not a caveat about a resolver rule.

> **`person.background_check.*` is gone** ([D-043](../decisions/decision-log.md#d-043--no-background-checks-are-recorded-in-this-system)).
> The organization has no background checks handled by this system, so there is nothing to
> view and nothing to record. If that changes, the permission pair and a dated record with an
> `expires_at` are the natural shape — and it would belong here, next to `person.*`, because
> a clearance is a fact about a person and not about their membership.

> ### Descriptive data: two old codes and one new one
>
> Everything the system knows about a person other than their name, their gender and their age is
> one class of data, in fields the organization defines while it runs
> ([../domain/08-person-data.md](../domain/08-person-data.md),
> [../data-model/09-attributes.md](../data-model/09-attributes.md),
> [D-083](../decisions/decision-log.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data),
> [D-084](../decisions/decision-log.md#d-084--descriptive-data-is-organization-defined-at-runtime)).
> The catalog's whole involvement in that is one row added and none removed:
>
> - **Read: `person.view`. Write: `person.edit`. That is the entire access story.** **No read or
>   write code was added** for descriptive data, because there is nothing left for one to gate —
>   a code that separated, say, the allergy list from the rest of the record would reinstate the
>   privileged subset [D-083](../decisions/decision-log.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)
>   refused on the merits. There is therefore **no `health.*` or `medical.*` namespace and no
>   per-field access rule**, deliberately: `category` on a definition groups a form and grants
>   nothing. If a narrower tier is ever genuinely needed, the route is a decision entry about a
>   **second grant scope over a defined set of data**, not a code with a suggestive name.
> - **`attribute.define` is the new one, and it is the narrow one**
>   ([D-084](../decisions/decision-log.md#d-084--descriptive-data-is-organization-defined-at-runtime)):
>   it creates, renames, merges and retires a code — deciding what the organization *collects*,
>   which is what makes the data queryable. Recording a value against a code that does not exist
>   needs no such permission: it saves as a `proposed` definition and waits in the curation queue.
>   The mark column stays empty for it because it reads nobody's data — the vocabulary is rows
>   about codes, and the values underneath it are reached through `person.view` like anything else.
> - **`person.view` moved from ⚠ to ⚠⚠**, and the reason is the same decision: the marker grades
>   what a grant *exposes*, and this one now exposes everything known about a child — an allergy
>   list, an insurance number, a note about who the child actually lives with — through a single
>   code that used to be graded as ordinary personal data from when the record was smaller than
>   the person.
>
> `person.redact` reaches the layer too, and in the opposite direction from retiring a code:
> retiring one keeps the values, redacting a person erases theirs — in the audit trail as well as in
> the row, since a trail that still reads out an erased value has preserved it rather than missed it
> ([../data-model/09-attributes.md §6](../data-model/09-attributes.md#6-erasure-retirement-and-the-audit-payload)).

## 3. Accounts

| Code | Namespace | Sens. | Grants |
|------|-----------|-------|--------|
| `account.view` | — | ⚠ | See account records |
| `account.create` | — | | Create an account for someone |
| `account.suspend` | — | ⚠ | Suspend an account |
| `account.close` | — | ⚠ | Close an account |
| `account.credential.reset` | — | 🔒 | Issue a credential reset |

> `account.suspend` is **not** `membership.suspend`. Suspending a login does not remove
> someone from the organization; the two are separate lifecycles and separate permissions.

> **Nothing in this namespace links an account to a person it already belongs to, and the absence is
> decided, not overlooked.** A sign-up that strong-matches an existing person raises an
> `identity_hypothesis` and brings nothing into the world that a human has not approved — nothing
> merged, nothing linked, nothing activated; the account sits at `pending_verification` until a
> reviewer decides, and deciding is `person.merge` (§2,
> [D-089](../decisions/decision-log.md#d-089--one-live-account-a-colliding-sign-up-files-a-claim-and-creates-nothing)).
> So there is **no `account.link` code** and no claim object for one to act on: the second live
> account those would manage is exactly what the rule forbids, and the case they would have been asked
> to solve most often is already handled underneath permissions — `account_credential` holds many
> credentials for one account, so a member with a new e-mail address is adding a credential to the
> login they have, not acquiring a second one.

## 4. Membership

| Code | Namespace | Sens. | Grants |
|------|-----------|-------|--------|
| `membership.view` | — | ⚠ | See membership records |
| `membership.request.create` | — | | Submit an application |
| `membership.request.review` | — | ⚠ | Read and work an application |
| `membership.request.approve` | — | ⛔ | Approve or reject an application |
| `membership.activate` | — | | Activate a membership |
| `membership.lapse` | — | ⛔ | Lapse a membership (administrative, non-payment) |
| `membership.suspend` | — | ⛔ | Temporarily suspend a membership |
| `membership.terminate` | — | ⛔ | **End a membership for cause / expel** |
| `membership.backdate` | — | ⚠ | Enter or correct historical membership periods |

> **Two rows stood at the foot of this table and are gone.** ~~`unit_participation.view` and
> `unit_participation.manage` — see who takes part in a sub-unit; add, move or end participation~~
> were **deleted by
> [D-097](../decisions/decision-log.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)**
> with the table they read and the sub-units that had rosters. Their work is retargeted, not lost:
> *"who is in the organization?"* is `membership.view` — one query over `membership`, with no depth in
> it — and *"who is in this group?"* and *"write that group's roster"* are `person_group.view` and
> `person_group.member.manage` (§5a,
> [D-098](../decisions/decision-log.md#d-098--a-group-is-a-persongroup-explicit-members-a-lifetime-and-no-authority)).
> Everything D-095 said of `unit_participation.manage` — never self-scoped, the write is somebody
> else's act, the report is the control — transfers to the new code intact, and is written there.

> **`membership.terminate` is the most consequential non-system permission in the
> catalog.** A lapse is administrative; a termination is a decision about a person's
> standing in a youth organization, frequently with safeguarding and reputational
> consequences. It should be held by very few people, and it must not be implied by
> `membership.lapse`. Grant it explicitly, per person — which since
> [D-099](../decisions/decision-log.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)
> is the only thing a grant *can* be: one code, one effect.

> **`membership.transfer` is gone, and round 10 removed the sentence that pointed at a replacement.**
> "Transfer a member between units" was an artefact of units holding memberships, and it was last
> answered by *"moving between sub-units is `unit_participation.manage` — close one row, open another"*
> ([D-041](../decisions/decision-log.md#d-041--belonging-to-a-sub-unit-is-a-participation-record-not-a-membership)).
> **That replacement is now itself deleted** ([D-097](../decisions/decision-log.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)).
> The discipline survives and the object moved: moving a person from one group to another is
> `person_group.member.manage` — close one dated row, open another
> ([D-098](../decisions/decision-log.md#d-098--a-group-is-a-persongroup-explicit-members-a-lifetime-and-no-authority),
> [../data-model/02-organization.md §4](../data-model/02-organization.md#4-joins-leaves-and-transfers-close-one-row-open-another))
> — and it does not touch the person's membership at all. There is still nothing to transfer.

> **`person_group.member.manage` has no self-scoped variant, and none will be added**
> ([D-095](../decisions/decision-log.md#d-095--units-carry-no-restrictions-joining-one-is-somebody-elses-act),
> whose reasoning
> [D-098](../decisions/decision-log.md#d-098--a-group-is-a-persongroup-explicit-members-a-lifetime-and-no-authority)
> transfers intact). Every grant of it means *"over this group's roster"* or *"over every group's
> roster"*, never *"over my own row"* — so **"nobody writes themselves into a group"** is not a check
> the write performs, it is the shape of the thing being granted: there is no smaller grant to make
> yourself. The same holds for `role.assign` (§7): **nobody appoints themselves**, and D-095's
> instruction was explicitly not to mint a code that could express either act. This is also where the
> safeguarding story moved to. `org_unit_type.allows_minors` was removed a round ago and the units it
> graded are now gone too, so no column anywhere says which sets are for children and nothing here
> refuses to place a minor in one; what is left is this code held by named adults at the unit, the
> write audited the way any business-table write is, its recorded values emptied after 24 months
> ([D-088](../decisions/decision-log.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)),
> and a report of who holds it
> ([../domain/04-organization-structure.md §3](../domain/04-organization-structure.md#3-joining-a-group-is-somebody-elses-act)).
> **What is lost is not in this list:** D-097 names it plainly — the named adult used to be somebody
> the body chose, and there is no body
> ([../domain/04-organization-structure.md §1](../domain/04-organization-structure.md#1-the-organization-is-one-unit-and-the-unit-is-a-scope)).
> The gate in front of a *membership* is the fee; a group has no fee and no second gate, so this
> permission is the only one
> ([../domain/05-membership-lifecycle.md §1](../domain/05-membership-lifecycle.md#1-the-flow-you-described)).

> ~~**These permissions are gated by membership when held through a role that requires one**
> ([D-039](../decisions/decision-log.md#d-039--member-permissions-require-a-current-paid-membership)).
> The gate is a property of the *role*, not of the permission, so it is not visible in this table.
> The single exception is `system.gate_exempt` (§7), which *is* the gate's waiver and is therefore
> exempt from the gate itself
> ([D-051](../decisions/decision-log.md#d-051--the-membership-gate-is-waived-by-a-permission-not-only-by-a-role-flag)).~~
> **Withdrawn by
> [D-100](../decisions/decision-log.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape).**
> Nothing about a code says whether it requires a paid-up holder, so this table has nothing to hide
> and nothing to warn about. **Who performs the membership test now: the grantee expression**, which
> says `MEMBERS * ROLE(x)` when the fee is meant to matter and omits it when it is not — evaluated
> live on the checked date (§11,
> [../domain/06-authorization-model.md §6.1](../domain/06-authorization-model.md#61-members--the-membership-test-moved-into-the-expression)).

## 5. Organization and positions

**Nothing is granted here, because nothing described is left.** Both halves of this title died in round
10 for different reasons: the six `org_unit.*` codes went with the unit hierarchy
([D-097](../decisions/decision-log.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row))
and the two `position.*` codes went with positions
([D-100](../decisions/decision-log.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)).
The heading stays so that a reader arriving from an old bookmark finds the reason and not an empty
space, and because this catalog is the only list of grantable codes — a code leaving it silently is a
migration nobody decided (§2).

| ~~Deleted code~~ | Went with | Where the act is now |
|---|---|---|
| ~~`org_unit.view`~~ | `org_unit` (D-097) | Nowhere. The unit is a **scope**, not a row: there is no list of units to read, and no "which units exist" report to run |
| ~~`org_unit.create`~~ | ditto | Nowhere, and nothing needs creating. The unit arrives as a code in `grant_scope_type`, not as data |
| ~~`org_unit.edit`~~, ~~`org_unit.rename`~~ | `org_unit_name` and its rename history (D-097) | Renaming a **group** is `person_group.edit` (§5a), and it is cheap: a grant and an expression store kind + id, never a name, so a rename rewrites nothing (D-101) |
| ~~`org_unit.restructure`~~ | splits, mergers and successions (D-097) | Nowhere, and the loss is stated once in D-097: a group that splits is an old group that ended and two that began, with no edge between them unless somebody writes one |
| ~~`org_unit.close`~~ | `org_unit.status` (D-097) | `person_group.end` (§5a) — which ends a **set**, and is graded accordingly |
| ~~`position.view`~~, ~~`position.assign`~~ | `position`, `position_assignment`, `is_leadership`, `max_holders`, the appointment workflows (D-100) | `role.view` and `role.assign` (§7). An elected leader is a holder of a role, and the audience rule that used to read `unit_leaders` is `ROLE(leaders)` — which, unlike the rule round 6 had to correct because it was silently matching nobody, means what its name says |

**Why `position.assign` was split from everything else, kept because the reasoning outlived the code.**
An appointment was made *to* a person by somebody else, was never self-scoped, and came with
eligibility rules about the office rather than the appointment — `position.min_age`, `max_holders`,
`requires_membership`
([D-095](../decisions/decision-log.md#d-095--units-carry-no-restrictions-joining-one-is-somebody-elses-act)).
All three of those columns are deleted with the table, and none of them is a self-service door in the
new model either: `role.assign` has no self-scoped form (§7). The reasoning that survives is the one
that made `role.assign` 🔒🔒 — **nobody appoints themselves**, and no code in this catalog can be
sharpened into that act.

**"An appointment writes one row, not two" — and now nothing writes a second row either.** The
sentence existed to stop a leadership position silently deriving authority: the derivation from a
position to a set of people lived in a group's *filling rule*, where it stopped covering the person on
the day the assignment closed
([D-091](../decisions/decision-log.md#d-091--a-permission-group-is-a-rule-and-a-list-at-once-and-a-rule-may-name-another-group)).
**Filling rules were superseded by
[D-101](../decisions/decision-log.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree)
and positions by D-100, so the derivation is gone rather than relocated:** a holder row is written by a
named person under `role.assign`, and the only thing that turns it into authority is a grant naming
`ROLE(x)`. *What is genuinely lost is the elected-versus-appointed distinction as stored data*
(D-100): it survives only as offices the organization invents — `elected_council` beside
`appointed_it` — or not at all
([../domain/04-organization-structure.md §6](../domain/04-organization-structure.md#6-appointments-which-no-longer-end-at-a-position)).

> `org_unit.restructure` was separated from routine editing because a split rewrites the answer to
> historical questions. **Reparenting had already been taken out of it** — a unit could not change
> parent at all ([D-036](../decisions/decision-log.md#d-036--units-cannot-be-reparented-a-unit-that-moves-is-a-new-unit),
> itself now reversed by D-097) — and the splits and mergers it did grant are gone too, so the
> separation is recorded here rather than kept anywhere live.

## 5a. Groups, roles and audiences

Three things the catalog used to describe with units, exposure rows and filling rules, and which are
now three small tables: **a group** (`person_group`, dated member rows, a lifetime) is company
([D-098](../decisions/decision-log.md#d-098--a-group-is-a-persongroup-explicit-members-a-lifetime-and-no-authority));
**a role** (`role`, `role_holder`) is an office, and confers nothing
([D-100](../decisions/decision-log.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape));
**an audience** is an expression over named sets, and is what a grant aims at
([D-101](../decisions/decision-log.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree)).
Writing a group's roster and writing an office's holder list are **different codes on purpose** — that
difference is the whole reason there are two tables — and the office codes are in §7.

| Code | Namespace | Sens. | Grants |
|------|-----------|-------|--------|
| `person_group.view` | — | ⚠ | See which groups exist, their lifetimes, and **who is in them** — a roster is a list of people, which is what ⚠ grades |
| `person_group.create` | — | | Create a group: a name, a description, a lifetime. `applies_to = unit` |
| `person_group.edit` | — | | Change a group's name or description. A rename rewrites no grant (§5) |
| `person_group.end` | — | | Set the group's `valid_to`. It ends a **set**, not anyone's standing — hence no ⛔, deliberately |
| `person_group.member.manage` | — | ⚠ | **Add, move or end a member.** Never self-scoped (§4); `applies_to = unit_and_item` |
| `audience.view` | — | | See the expressions a grant can be aimed at, and **the people each one resolves to** |
| `audience.manage` | — | ⚠ | Create an audience; change its expression — **which is now the whole of it**: the `LIST` this gloss used to add, and the table behind it, are deleted, so a hand-named person is a `PERSON(x)` leaf the same permission already reaches ([D-105](../decisions/decision-log.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)) |

> ~~**`scope.expose` and `scope.exposure.review` stood at the top of this section, and `scope.expose`
> was arguably the most consequential permission in the authorization model.** It was the only door
> between unit levels: authority never inherits downward
> ([D-031](../decisions/decision-log.md#d-031--no-downward-inheritance-of-authority-scopeexposure-is-the-only-crossing)),
> and this was the single mechanism that crossed the boundary — graded 🔒 despite the obscure name, and
> made safe by *who could write it*, since every `scope_exposure` row was written by the unit it
> covers, so a parent's officer could not satisfy it for a child unit
> ([D-049](../decisions/decision-log.md#d-049--the-root-may-not-read-into-its-sub-units-scopeexposure-is-the-only-crossing)).
> There was no bulk variant, and every row was a deliberate, attributable decision about one
> assignment
> ([D-045](../decisions/decision-log.md#d-045--the-bulk-scope-exposure-tool-is-removed)).~~
> **Deleted by
> [D-097](../decisions/decision-log.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row),
> with the table, the direction-of-authority check, and the nightly alert that was its only detector.**
> They are kept here struck because the question they answered — *may the center read what happens
> inside a body it does not run?* — **no longer has a subject**, and someone who remembers the answer
> "no, unless the body says so" should find that fact rather than a silent gap. The same reasoning is
> worked through in
> [../domain/06-authorization-model.md §2.1](../domain/06-authorization-model.md#21-the-founding-rule-and-what-is-left-of-it).

> **`person_group.member.manage` is a ⚠ next to a 🔒🔒 two rows away, and the gap is the design.**
> [D-100](../decisions/decision-log.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)
> refuses to merge `person_group` and `role` into one table with a `kind` column precisely because one
> membership table gives a single code that both adds a child to the Thursday group **and** puts the
> holder into `SYSTEM_ADMINS`. Same columns, different codes, and `GROUP(x)` / `ROLE(x)` distinct in
> the grant text so the difference is visible to whoever reads the grant. **A group additionally
> authorizes nothing by existing**: no parent, no type, no leadership, no roles of its own, no fee —
> a member of a group can *do* nothing, which is
> [D-005](../decisions/decision-log.md#d-005--permissions-are-grants-never-derived-from-identity) one
> level down ([../domain/04-organization-structure.md §2](../domain/04-organization-structure.md#2-what-a-group-is-and-everything-a-group-is-not)).

> **A group and a role are both *items*, which is what makes "these two may work this roster" a
> grant.** Both are registered in `grant_scope_type`, so the code above can be held at the unit —
> reaching **every** group, existing and future, because nothing stands between a unit grant and an
> item after D-097 — or written on one group, reaching that roster only
> ([../data-model/02-organization.md §3](../data-model/02-organization.md#3-a-group-is-an-item-a-grant-can-be-written-on-one)).
> Reaching the second requires the first: a grant on an item is written by someone who holds the code
> at the unit, or holds a grant on that item.
>
> A **live grant whose group has ended** is a listed oddity rather than a failure: it applies to
> nobody, which is the safe direction, and the report of such rows is where the stale one surfaces
> ([../data-model/02-organization.md §6](../data-model/02-organization.md#6-integrity-checks)).

> **`audience.manage` is the permission that creates a grant target, and it is wider than it was.**
> Whoever holds it can assemble a set of people which a later `access_grant` may then address
> ([D-042](../decisions/decision-log.md#d-042--grants-may-target-audiences-not-only-individuals)) —
> authority over *who could be granted*, one step removed from granting. Whether it belongs to a
> dedicated office or to whoever runs things is open (§12).
>
> **It used to be one code over three arms; it is now one code over a whole expression, and the
> hazard changed shape rather than leaving.**
> [D-091](../decisions/decision-log.md#d-091--a-permission-group-is-a-rule-and-a-list-at-once-and-a-rule-may-name-another-group)
> let a group be filled by a rule, a hand-kept list, or an inclusion of other groups, and the
> inclusion arm was the one that worried, because *"add the kitchen crew to everything the troop-staff
> group is used for"* silently widened every grant aimed at anything including it. **`audience_include`
> is deleted by [D-101](../decisions/decision-log.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree),**
> along with `include_depth_limit`, the transitive walk and the write-time cycle check over a graph —
> an audience is a tree of `+ - *` now, a tree cannot cycle, and composition happens in the grant
> (`GROUP(kitchen) + ROLE(troop_staff)`) instead of in an edge nobody could see the shape of. What
> did **not** get smaller: `EVERYONE` is a legal operand, so nothing in this table distinguishes
> *"add these five people"* from *"this grant reaches the whole organization"*, and no separate code
> was invented to do it. That stays an open question, not an answer (§12), and until it is answered
> the only control is the one D-091 named and D-102 sharpened: **the editor shows the people a grant
> reaches, expanded, computed for an item, rather than the expression's name**
> ([../domain/06-authorization-model.md §6.2](../domain/06-authorization-model.md#62-audiences--an-expression-over-named-sets)).
>
> **The display is itself a read over people, and this catalog does not grade that yet.** Showing a
> resolved set means enumerating which humans an expression currently covers — which is what
> `audience.view` is for, on a row carrying no sensitivity mark. Listing the holders of
> *"everyone except the counselors in `schuzka2026-1`"* is not the same kind of act as listing the
> kitchen crew, and the grading was written before the two could be one query (§12).

---

## 6. Guardianship

| Code | Namespace | Sens. | Grants |
|------|-----------|-------|--------|
| `guardianship.view` | — | ⚠⚠ | See guardianship relationships |
| `guardianship.create` | — | ⚠⚠ | Record a guardianship |
| `guardianship.end` | — | ⚠⚠ | End a guardianship |
| `guardianship.assign` | — | ⚠⚠ | Add another guardian over the same dependent |
| `guardianship.change_right` | — | 🔒 | Change a guardianship's `right_level` |

> **These four are the only codes in the catalog that a private individual holds over their own
> household, without being granted them.** [D-073](../decisions/decision-log.md#d-073--guardianship-is-administered-by-its-own-parties-not-by-staff)
> makes the parties to a guardianship principals on the row: a guardian may end it, add another
> guardian, and change its level; the adult subject may end it over themselves. Staff hold the same
> codes and are **an** route, never **the** route.
>
> `guardianship.permission.grant` is **deleted** — it granted individual codes from the
> `dependent.*` namespace, and there is no such namespace to grant from
> ([D-074](../decisions/decision-log.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular)).
> `guardianship.change_right` replaces it, and does less: one value, three choices.
>
> **What the three choices are compared against, now that the ladder is gone.** D-074's `none` /
> `view` / `write` used to be read off the access-level ladder — `write` reached `contribute`, `view`
> reached `view`. **That comparison was deleted with the ladder by
> [D-099](../decisions/decision-log.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality),**
> and the guardianship channel would have had nothing left to compare a permission against. It
> compares against a column instead: `permission.right_kind ∈ read | write`, where `none` covers
> nothing, `view` covers the `read` codes, and `write` covers both. **That is the column's only
> customer in the whole system** (§1), and it is why a code added to this catalog has to be typed
> `read` or `write` at all: the column is required, because a nullable one whose null-ness silently
> means something would let a permission arrive with a guardian's answer already decided by nobody.

## 7. Permissions administration

| Code | Namespace | Sens. | Grants |
|------|-----------|-------|--------|
| `role.view` | `system` | | See the offices that exist and **who has held them, over what period** (`role_holder`) |
| `role.create` | `system` | 🔒🔒 | Create an office: a code, a name, a description. It carries no permission — see the note below |
| `role.edit` | `system` | 🔒🔒 | Change an office's name or description |
| `role.delete` | `system` | 🔒🔒 | Delete an office. Only possible if it was **never held** and is not a system role |
| `role.assign` | `system` | 🔒🔒 | **Write a `role_holder` row** — make someone a holder. `applies_to = unit_and_item`: on one role, this is "manage the counselors roster" |
| `role.unassign` | `system` | 🔒 | Close a `role_holder` row — set its `valid_to` |
| `permission.view` | `system` | | See the permission catalog |
| `permission.edit` | `system` | 🔒🔒 | Change the permission catalog |
| `access_grant.create` | — | ⚠ | Create a grant — the act that turns a code into someone's authority |
| `access_grant.revoke` | — | ⚠ | End a grant early, or write a `deny` |
| `system.admin` | `system` | 🔒🔒 | **Everything.** Single top-level capability, `applies_to = unit` |
| ~~`system.gate_exempt`~~ | `system` | ~~🔒~~ | **Deleted by [D-100](../decisions/decision-log.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)** — see the note below the table |

> **A role confers nothing.** That is the sentence that rewrites this whole section, and it is worth
> reading before the table above, because three of the six rows above used to mean something they can
> no longer mean. `role_permission` is deleted, and with it the answer to *"what does this role
> grant?"*: **the codes an office carries are the live grants whose expression names `ROLE(x)`**
> ([D-100](../decisions/decision-log.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape),
> [../domain/06-authorization-model.md §4](../domain/06-authorization-model.md#4-roles-are-offices-groups-are-company)).
> What `role.create` and `role.edit` touch is a **name, a description, an order** — an office is a set
> with a label, and a set is not a grant
> ([D-005](../decisions/decision-log.md#d-005--permissions-are-grants-never-derived-from-identity)).
> `role.view` used to read "see roles and their permissions", and what it shows now is the holder
> register, which is the question the table can still answer and the one
> [F-12](../open-questions.md#f-12--closed--may-a-role-be-held-by-a-rule-as-an-audience-is) was closed to keep
> answerable: *who was treasurer in 2023?*

> **`role.assign` is the permission to escalate privilege.** Whoever holds it can write themselves a
> holder row in an office that grants them `system.admin`. It must be held by very few people and
> every holder row must be logged and alerted on. Note that `system.admin` is deliberately a **single
> top-level permission** rather than a per-resource one — concentrating the most dangerous capability
> and alarming on its holders is safer than scattering equivalents of it. **`role.assign` has no
> self-scoped form and none will be added** (§4,
> [D-095](../decisions/decision-log.md#d-095--units-carry-no-restrictions-joining-one-is-somebody-elses-act)):
> the reason it is not a check the write performs is that there is no smaller grant to make yourself.

> **Roles are runtime data, and these six permissions are how the organization administers them.**
> `role.create` names a new office; `role.edit` renames one; `role.delete` removes one created by
> mistake; the reach of any of them is written by `access_grant.create` down the table. §11 is
> therefore a *starting point to be edited*, not a fixed vocabulary — which is why §11 no longer
> claims to answer "which roles are exempt from the membership gate". That question is not answered in
> configuration any more either: it is answered in the text of each grant, by whether its expression
> contains `MEMBERS`.

> **There is no `role.retire`, and a role cannot be switched off**
> ([D-053](../decisions/decision-log.md#d-053--a-role-is-valid-always-only-its-assignment-is-temporal)).
> A role is a definition and is valid always; the period lives on the **holder row**. Ending a role's
> use means closing holder rows, which is `role.unassign` — one person at a time, or a loop over the
> holders. This is still the right shape, and the round that deleted the role's own permission list
> left this alone on purpose: what ends is *someone's authority*, and that is a fact about a person,
> not about a definition. **What died with the gate is the reassurance that used to come with it** —
> the old note pointed out that a dormant authority would quietly expire anyway when the holder's fee
> lapsed. Nothing does that now, so the report of holder rows that never end
> ([D-071](../decisions/decision-log.md#d-071--nothing-forces-a-role-assignment-to-end-the-gate-and-the-report-are-the-control),
> whose posture transfers from assignments to holder rows) is carrying all of the weight.

> ~~**`role.edit` is a bulk privilege change wearing the clothes of a settings screen.** Editing a
> role's permissions takes effect immediately for **every holder**, with no assignment touched and no
> notification. It is marked 🔒🔒 alongside `role.assign` for that reason. The two are different
> powers — `role.assign` escalates one person, `role.edit` escalates everyone holding the role — and
> neither is implied by the other.~~ **Withdrawn in substance by
> [D-100](../decisions/decision-log.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape):
> there are no longer any permissions on a role to edit,** so the screen this paragraph warned about
> has nothing dangerous left on it. **The hazard it named did not go away — it moved to the grant.**
> Whoever can save a grant aimed at `ROLE(x)` escalates **everyone holding `x`**, immediately, without
> touching a holder row and without notifying anybody: that is the new bulk privilege change, it is
> `access_grant.create` with an expression in it, and it is exactly why `role.*` stays 🔒🔒 while the
> composition of grants is the least-graded write in the catalog (§12). The two powers are still not
> each other, and neither is implied by the other.

> **`role.delete` only works on an office that has never been held** and is not `is_system` — which is
> what protects the one seeded role, `counselors`, from an editor (§11). No delete may leave a
> `role_holder` pointing at a role that is gone:
> [../data-model/05-authorization.md §3](../data-model/05-authorization.md#3-role--an-office)
> states the guard and the order it refuses in. The two halves are not equally strong, and the
> difference is the reason this permission is not self-policing. The first is referential
> integrity — `role_holder.role_id` references `role.id`, a migration-level constraint, so it refuses
> a delete that arrives from an import, from a manual fix, or from a second client as surely as from
> the screens. The second, `is_system`, is a property of the row being deleted and no index can see
> it: it is a check inside the transaction that deletes, and a model-layer guard there is a friendlier
> message, not the refusal. A role that has been held is left in place, so the answer to "what office
> did this person hold in 2019?" survives — which is precisely when someone asks it.
>
> **`system.gate_exempt` is deleted, and this is the round's largest deletion seen from here.** It used
> to be the *permission* that waived the membership gate for one named person
> ([D-051](../decisions/decision-log.md#d-051--the-membership-gate-is-waived-by-a-permission-not-only-by-a-role-flag)),
> alongside `role.requires_membership`, which waived it for a whole office, and both existed only
> because the resolver asked the question of every grant
> ([D-039](../decisions/decision-log.md#d-039--member-permissions-require-a-current-paid-membership)).
> The resolver no longer asks it, so there is nothing to waive and no exemption to be granted: the
> waiver is now the **expression the grant was written with** — `MEMBERS * ROLE(x)` where the fee must
> hold, `ROLE(x)` where it need not, and `(MEMBERS * ROLE(x)) + PERSON(y)` when one named person is to
> survive their own lapse. `person_holds_gate_exempt` goes with it, and so does the lockout hazard
> that came from performing a permission check *through* `can()` inside the exemption
> (§11, [../domain/06-authorization-model.md §6.1](../domain/06-authorization-model.md#61-members--the-membership-test-moved-into-the-expression)).
>
> ~~**`access_grant.create` is scoped by `permission_level`:** holding it lets you grant others
> access *to items you have `admin` on*, and only at a level at or below your own. Without that
> restriction, any item-grant holder becomes a universal grantor.~~ **Withdrawn by
> [D-099](../decisions/decision-log.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality),**
> which deleted the ladder the ceiling was drawn from. **What bounds a grantor now:** the code is one
> code, `applies_to` refuses it on an item it does not fit, the scope is the item the grant names or
> the unit, `MEMBERS` is the writer's act, and a delegation may not exceed the delegator's own
> authority — but that test is written only for delegations
> ([../domain/06-authorization-model.md §9](../domain/06-authorization-model.md#9-delegation)).
> **For an ordinary grant, no decision in D-097..D-102 says you may grant only what you hold.**
> *D-099 noticed the hazard and answered a different half of it: the price of one row per code is paid
> in rows, and the report of dead-weight denies is the hygiene that came with it.* The ceiling is
> therefore recorded as an open question (§12), not as a rule this catalog holds.

## 8. Audit and system

| Code | Namespace | Sens. | Grants |
|------|-----------|-------|--------|
| `audit.view` | — | ⚠⚠ | Read the audit log — **including the before/after values it carries, which are person data like any other** |
| `audit.export` | — | ⚠⚠ | Export audit records |
| `import.view` | — | ⚠ | See import batches |
| `import.stage` | — | | Stage an import |
| `import.apply` | — | 🔒 | Apply a staged import |
| `import.revert` | — | 🔒 | Revert an applied import |
| `report.view` | — | ⚠ | Run standard reports |
| `report.export` | — | ⚠⚠ | Export report data |

> **`audit.view` is graded ⚠⚠, and the reason is a property of the trail rather than of any field
> it touches.** `audit_log` carries the before and after images of what changed, which makes it
> **a second copy of the person record** — descriptive values included, on the same terms as a
> `person_contact` or a note change. There is no exclusion list doing that work, and there must not
> be one: a rule naming the person fields whose values may not be logged is a privileged *subset* of
> the record, which is precisely what
> [D-083](../decisions/decision-log.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)
> refused — and it would hollow out [D-085](../decisions/decision-log.md#d-085--the-identity-machinery-stays-structured-the-boundary-is-rules-not-sensitivity),
> whose entire justification for overwriting a value in place is that the trail holds the sequence.
> So reading the trail over a scope **is** reading person data over that scope, and reading *more*
> than `person.view` shows: the current row is the organization's present belief, the trail is every
> belief it has held. What protects the trail is therefore the guard on it — scope, this mark, and
> who is granted it — exactly as the guard on `person.view` protects the record. The grading rule this
> applies — **the mark follows what a grant exposes, not the table a code names** — is
> [D-086](../decisions/decision-log.md#d-086--a-sensitivity-mark-grades-what-a-grant-exposes-not-the-table-it-reads),
> taken during propagation rather than from an answer, and reversible on one line.
>
> **The contents expire, which bounds this exposure without fixing it.** A row lives for the life of
> the system; its `old_values`/`new_values` are emptied **24 months after they were written**, by a
> scheduled job this corpus calls **payload reduction** — a third operation on the trail, distinct
> from redaction (a person's erasure, immediate and absolute, whatever the age of the row) and from an
> import revert ([D-088](../decisions/decision-log.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)).
> So *"the trail is every belief it has held"* is, since round 8, true only of the values less than two
> years old; about anything older the trail answers *who touched this row, when, and were they allowed
> to* and not *and to what*. For the risk this note is actually about — a grant graded wrongly, or
> simply held by the wrong person — that is a control worth having: it does not make the exposure
> impossible, it puts a horizon under it, which for an organization of this size is the realistic form
> the same protection takes. **AT-4 stays open**, because a window on the payload is an argument about
> how *long* a bad grant can do harm, not an answer to whether one permission should guard the trail.
>
> **Payload reduction needs no code here, and saying so is the check that it was considered.** Nobody
> performs it interactively: it is scheduled, and the guard on it is a check that alerts when a row
> past the window still carries a payload
> ([../data-model/06-audit-and-import.md §2.2](../data-model/06-audit-and-import.md#22-redaction-before-logging)).
> A permission for it would imply a person choosing not to run it.
>
> **The excluded-keys list survives, with a smaller and honest job.** Values that must never be
> logged *at all* belong on it: credential secrets, tokens, session material. Personal data does
> not, because personal data is protected by who may read the table, not by a list of its names.
>
> **Erasure reaches the payload.** A redaction that rewrote the business tables while the erased
> values stayed readable in the trail is a failed redaction, not a partial one
> ([../data-model/06-audit-and-import.md](../data-model/06-audit-and-import.md) §2,
> [../data-model/09-attributes.md](../data-model/09-attributes.md) §6).
>
> **`audit.export` sits at ⚠⚠ for a reason unrelated to what it reads.** An export carries the
> payload outside every mechanism this catalog governs: scope stops at the file, revoking the grant
> does not recall the copy, and a later redaction cannot reach it. It is graded by where the data
> goes, not by what the code is allowed to see.
>
> **Whether one permission is enough of a guard for all that is itself open** — tracked as **AT-4**
> ([../open-questions.md](../open-questions.md#at-4--is-one-permission-enough-to-guard-a-trail-that-holds-person-data)).
> The grading above is what is settled: the trail is read with the guard of person data, whichever
> permission or combination of permissions that guard turns out to be.

## 8a. Events

The per-item grant scope the whole authorization model was built toward — and since
[D-102](../decisions/decision-log.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it),
**an item like any other**. Nothing owns an event: `event.org_unit_id` is deleted, and with it
`can_event()` — the unit-authority rule nearly every code below used to be reached through. A grant at
the unit reaches every event because there is no tier between the unit and the item and no owner to
test; **every event check goes through the ordinary resolver and nothing else.** **Registration is
eligibility** — a live allow of `event.register_self` *is* the rule for who may sign up, and there is
no separate eligibility mechanism
([D-060](../decisions/decision-log.md#d-060--eligibility-is-capability-there-is-no-separate-rule-engine)).
**And there is no door code.** The capability these thirteen codes are sometimes read as containing
was never registered anywhere — not in this table, not in any other page
([D-104](../decisions/decision-log.md#d-104--a-permission-codes-last-segment-is-an-action-and-a-registry-that-prose-contradicts-is-a-fiction),
§12); arriving people are recorded by whoever holds `event.presence.mark`, with a clipboard if
necessary, and [D-075](../decisions/decision-log.md#d-075--money-arrives-from-a-bank-api-a-payment-is-requested-by-variable-symbol-and-qr-code)
keeps the only QR code in this system attached to a payment, where it is a rendering and not a row.

| Code | Namespace | Sens. | Grants |
|------|-----------|-------|--------|
| `event.view` | — | | See an event |
| `event.create` | — | | Create an event. **Held at the unit** — there is no owner to create one *for* since D-102 deleted the column that would have named one |
| `event.edit` | — | | Change an event's details, dates, capacity |
| `event.cancel` | — | ⚠ | **Cancel an event** — keeps registrations, notifies nobody by itself |
| `event.organizer.manage` | — | ⚠ | Add or remove organizers — a **roster write**, which aims `ORGANIZERS` at more people and so widens every grant pointed at that set |
| `event.register_self` | — | | **Register yourself** — this is the eligibility rule |
| `event.register_other` | — | ⚠ | Register someone else (a minor, a walk-in) |
| `event.manage_participants` | — | ⚠ | **Manage the roster** — add or remove registrations, work the waitlist, promote |
| `event.presence.mark` | — | ⚠ | **Mark who turned up** — nothing else, and never a set anyone is granted over (§1) |
| `event.answer.view` | — | ⚠⚠ | **Read registrant answers** (tent, dietary, …) — the note below, and the seeded grant |
| `event.question.manage` | — | ⚠ | Define what the event asks |
| `event.grant_access` | — | 🔒 | Grant access to an event. **The level it used to demand is gone**; what distinguishes it from `access_grant.create` now is the scope, not a rung (§12) |
| `event.delete` | — | 🔒 | Delete an event — only possible with **no** registrations |

**Where each of these may be granted, and what kind of right it is** — the two columns
[D-099](../decisions/decision-log.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)
added, replacing the table of required levels that stood here:

| Code | `applies_to` | `right_kind` |
|---|---|---|
| `event.create` | `unit` | `write` |
| `event.view`, `event.answer.view` | `unit_and_item` | `read` |
| every other `event.*` code | `unit_and_item` | `write` |

**`unit_and_item` is the whole of the old per-scope table,** and it says less: at the unit a code
reaches every event, on one event it reaches that event, and no level rides on top of either. The
`read` rows are `read` because a guardian's `view` is meant to reach them (§6) — which is the only
reason the column exists.

> **The five sets bound to an event are grantees, not codes.** `ATTENDED`, `PLACED`, `CONFIRMED`,
> `ON_WAITLIST` and `ORGANIZERS` name the people connected to the item a grant is written on, and they
> belong to the audience language, not to this catalog: **an operand is a set, and a set is not a
> grant**
> ([D-062](../decisions/decision-log.md#d-062--organizers-are-appointed-on-the-event-not-granted)
> survives untouched — *an `event_organizer` row grants nothing*). Two refusals come with them and both
> land when the grant is saved: a **bound** (argument-less) operand is legal only on an item-scope
> grant, and only where `selector_type.argument_type` matches the item — `PLACED` on a group grant is
> refused because that item is not an event. And `PRESENT(<event>)` is refused outright (§1).
> The definitions, and the reason `PLACED` rather than `ATTENDED` is the capacity set, are in
> [../data-model/08-events.md §8](../data-model/08-events.md#selectors-that-bind-to-an-event).

> **`event.presence.mark` is split off `event.manage_participants` on purpose, and it used to sit a
> level *lower*.** Marking presence is a task handed to whoever is at the door with a clipboard;
> managing the roster is a task for the event's leadership. One permission covering both forces the
> organization to hand the clipboard-holder the ability to delete a child from the camp roster.
> Splitting it costs two rows and makes the ordinary delegation ordinary. **What the split was graded
> with is gone** — the note used to add *"and note the level: presence is `contribute`, the same bar as
> being able to register"*, and there is no bar to compare now
> ([D-099](../decisions/decision-log.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)).
> **The split is worth more than the level was:** the distinction the level made softly — this
> volunteer is not roster leadership — is now written as the only thing a grant can say, one code, and
> granting `event.presence.mark` on an event cannot smuggle in `event.manage_participants` the way
> `contribute` once sat underneath `manage`. It follows the shape of `membership.lapse` versus
> `membership.terminate`
> ([D-022](../decisions/decision-log.md#d-022--lapsing-and-termination-are-different-permissions)) —
> one routine, one consequential — and it is free to add because the catalog is a menu, not a fixed set
> ([D-055](../decisions/decision-log.md#d-055--the-permission-catalog-is-deliberately-comprehensive-and-granular)).
> **It was previously an open question (EV-5); it is resolved there as a split, and the split
> outlived the ladder it was graded on.**

> **`event.register_self` is the whole of
> [D-060](../decisions/decision-log.md#d-060--eligibility-is-capability-there-is-no-separate-rule-engine).**
> Opening an event to the membership is **one row**: an `access_grant` scoped to that event, of
> `event.register_self`, aimed at `MEMBERS`. One row is the point — nobody is enumerated, so nobody is
> left out when the roster changes, and nothing has to be re-run when someone joins. **It used to be
> one row at `contribute`,** and the level was doing a second job there that nobody assigned it: it
> made the eligibility grant the same *size* as the presence task. With the level gone the row says one
> thing, which is the smaller claim and the one that survives review.
>
> An age-restricted camp is a **narrower expression** instead — `MEMBERS * GROUP(camp_2026_junior)`
> aimed at the same one code, or the same subtraction pattern read the other way. **There is no age
> rule on the event and there will not be one** — an open event with an age ceiling is accepted as a
> risk, on the grounds that a registration-time condition the capability model does not know about is
> the first rule-engine rule
> ([D-070](../decisions/decision-log.md#d-070--an-event-has-no-age-ceiling-the-grant-is-the-rule)).
> If it ever needs closing, the shape is a new **selector** in the `selector_type` registry, not a
> column
> ([../domain/07-events.md §4](../domain/07-events.md#an-age-rule-is-an-audience-not-a-rule)) —
> and note that `GROUP(...)` is a set somebody maintains, so *"who is eligible"* stays a roster with a
> person's name on every row rather than a predicate the resolver evaluates.

> **`event.cancel` is separated from `event.edit` deliberately.** Cancelling is the most
> consequential thing anyone does to an event: it affects every registrant, it usually
> involves money, and it is a decision rather than an edit. It does not notify anyone — that
> is the communication module's job, and conflating the two makes "who cancelled this, and
> when?" harder to answer than it should be.

> **`event.delete` is on this list and nothing else has an equivalent, because events are the
> one thing in this data model that can be deleted.** (The comparison used to be with `org_unit`,
> which had no delete permission and had six codes of its own; §5.) A draft event with no
> registrations is a mistake to be cleaned up; anything else is cancelled, not deleted
> ([D-064](../decisions/decision-log.md#d-064--there-is-no-event-status-visibility-is-the-permission-model)).
> **No event with even one registration row may be deleted** — Guard 2 in
> [../data-model/08-events.md §8](../data-model/08-events.md#guards) is the rule, and cancelling
> is what to do instead. The obligation is not the permission's to carry: `event.delete` decides
> who may ask, and only a migration-level constraint — `event_registration.event_id` referencing
> `event.id` with no cascade — refuses the same delete when it arrives from an import or a
> hand-written fix instead of a screen. Enforcing this in the model layer alone would leave the
> record of who was coming deletable by everything except the intended route.

> **`event.answer.view` is where [D-061](../decisions/decision-log.md#d-061--event-answers-are-read-by-that-events-organizers) lives, and since round 10 it
> lives there as a *grant*.** The sentence "answers are read by that event's organizers" used to be
> hard-coded prose beside the resolver, reached through the event's owning unit. **`event.org_unit_id`
> is deleted, so the sentence is now said where permissions are said: a seeded grant of
> `event.answer.view`, scoped to the event, aimed at `ORGANIZERS`**
> ([D-102](../decisions/decision-log.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)).
> *Because a bound operand is legal only on an item-scope grant, this cannot be one row for every event:
> what ships is a **template**, and D-102 now says plainly that the event-creation path instantiates it
> beside the event row, in the same transaction as the event, and that the import owes one instantiation
> per event it writes
> ([../data-model/08-events.md §8](../data-model/08-events.md#selectors-that-bind-to-an-event)).*
> *What remains open is only the safety net: an event whose two writes were not one transaction has no
> organizer who can read its answers, and "these two rows exist together" is a report —* events with no
> answer-view grant — *that no layer of this project can express as a constraint*
> ([F-10](../open-questions.md#f-10--which-invariants-the-orm-cannot-express-and-who-writes-those)).
> The rule itself is unchanged: whoever runs an event reads that event's answers with no additional
> gate, because holding an office grants nothing (§7) and leadership is not guardianship — guardianship
> authority belongs to the guardians (§9). That is a deliberate widening and it is recorded as one.
> The catalog's registered spelling is **`event.answer.view`**, singular — the arbiter for a spelling the
> round briefly had two of, and the reason §12 says a code is a row and prose is only prose (§12,
> [F-19](../open-questions.md#f-19--closed--a-permission-code-is-a-row-prose-names-codes-and-nothing-checks-the-two)).
>
> **Its premise has since been narrowed, and not by reversing it**
> ([D-085](../decisions/decision-log.md#d-085--the-identity-machinery-stays-structured-the-boundary-is-rules-not-sensitivity)).
> D-061 was written when an event form was the *only* route by which a camp leader learned a child
> has a nut allergy, because nothing else was readable. Descriptive data now exists
> ([../domain/08-person-data.md](../domain/08-person-data.md)) and a leader holding `person.view`
> over that unit reads a recorded allergy there, so the form is **the fallback for a fact the
> organization has not recorded, not the ceiling on what an organizer may know**. What survives
> unchanged is the decision itself, and the discipline below it.
>
> **This code is graded ⚠⚠, and it is the second time in this round that the marker followed the
> content rather than the category.** It sat at ⚠ beside a paragraph conceding that the answers under
> it can be clinical, which is the same mismatch `audit.view` had one section above: a payload that is
> children's personal data, graded as though it were logistics. [D-083](../decisions/decision-log.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)
> refuses a class of data more delicate than the rest, so either an adrenaline-pen answer is person
> data — it is — or the grading on the audit trail was wrong. **The raise narrows nothing**: D-061
> stands, an event's organizers read that event's answers with no additional gate, and all that changed
> is what a reviewer should notice before ticking the box for the grant that reaches thirty volunteers —
> and since D-102 there is a box to tick: the seeded grant above, rather than a clause in a resolver
> nobody can read.
>
> **Which leaves the discipline exactly where it was, and says so plainly:** the rule that only
> preference-level detail belongs on a form is guidance on the form's label and nothing more. No layer
> enforces it and no layer can: nothing distinguishes
> "vegetarian" from "carries an adrenaline pen" to a database
> ([../data-model/08-events.md §7](../data-model/08-events.md#health-facts-and-the-discipline-this-requires)).
> It rests entirely on whoever writes the form — a convention, not a guard, and D-072's own
> sentence is the right way to read that.

## 9. There is no `dependent.*` namespace

**Eighteen codes deleted by [D-074](../decisions/decision-log.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular).**
A guardian's rights are `none`, `view`, or `write` — one value on the guardianship row, not a
capability list. **Nothing in this namespace may be reinstated by pattern-matching the old names;
there is no set of codes left for a name to stand for.**

| Old code | Became |
|---|---|
| `dependent.profile.view`, `dependent.contact.view`, `dependent.membership.view`, `dependent.event.view`, `dependent.fee.view`, `dependent.medical.view`, `dependent.achievement.view`, `dependent.document.view` | **`view`** — all of them, together. They can no longer be separated |
| `dependent.profile.admin`, `dependent.contact.manage`, `dependent.medical.admin`, `dependent.consent.admin` | **`write`** |
| `dependent.membership.request`, `dependent.event.register`, `dependent.event.answer`, `dependent.fee.pay`, `dependent.consent.give` | **`write`** — an act is not a narrower category than an edit |
| `dependent.admin` | Nothing. There is no set left to be a shorthand for |

**What is lost, stated as plainly as it should be.** A court order restricting one parent's access
to a child's medical record while leaving everything else in place **cannot be expressed**.
"Read-only, but not the medical file" cannot be expressed. A grandmother granted roster visibility
and nothing else is now a `view` guardian, which reaches the fee history and everything else the
system holds about that child. The old namespace existed for exactly these cases, and D-074 traded
them for a vocabulary a volunteer treasurer can hold in their head.

**The separation was then declined, not merely left unimplemented — and the difference matters to
anyone reading this table as a to-do list.**
[D-083](../decisions/decision-log.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)
put the court-order story to the organization directly and it was refused on the merits
(*"medical data is not different in any way"*), and the same answer removed the referent: there is
no medical record inside the person record to be shut out of, because everything other than name,
gender and age is one class of data reached by `person.view` and governed by the guardian's right
level whole ([../domain/08-person-data.md](../domain/08-person-data.md)). So *"read everything
except the diagnoses"* is not a sentence waiting on a mechanism somebody has yet to build; it is a
sentence the organization declined to want, which is why
[E-7 closed](../open-questions.md#e-7--closed--one-level-cannot-separate-the-medical-record-from-the-profile-and-nobody-wanted-to)
as a dissolved question rather than an answered one. **Read the inexpressibility above as settled,
not as pending work.**

**What still holds:**

- ~~`write` ranks at `contribute` (20), **not** `manage`.~~ **Withdrawn by
  [D-099](../decisions/decision-log.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality):**
  there is no ladder for it to rank on, and the bullet's real content was never its rung. What it was
  guarding is untouched by D-099 — **a guardian cannot do organization-wide things, and cannot reach a
  different dependent's records: authority is per guardianship row**, because the channel is entered by
  whose record the act touches and answers only about that row
  ([D-079](../decisions/decision-log.md#d-079--the-guardianship-channel-is-entered-by-shape-not-by-permission-name)).
  What `write` now means is *this row's dependent, both kinds*: it covers the `write` codes and the
  `read` ones, where `view` covers only `read` and `none` covers nothing — compared against
  `permission.right_kind`, not against a level (§6).
- The **deny is untouched.** A live deny beats every allow that applies, at any scope, in any channel
  (D-032's first half, now its entire content, restated by
  [D-099](../decisions/decision-log.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)),
  so "this guardian, nothing" remains expressible — a `deny` at the unit aimed at the person,
  `PERSON(x)`. There is no "that child's guardians" operand to aim one at, and round 13 settled that there
  never was one to have: the channel resolves no sets, so the name an expression can carry here is the
  person's ([D-113](../decisions/decision-log.md#d-113--the-guardianship-channel-has-no-expression-guardians-is-not-a-selector)).
  What was lost is a *narrow* deny, not the ability to refuse.
- A guardianship at `none` grants literally nothing, so **being a guardian still grants nothing by
  itself** — the safeguarding property that motivated the eighteen codes survives without them.
- Answers to an event's questions are still read through `event.answer.view`, which is a permission on
  the grant side, carried by the seeded grant to `ORGANIZERS` (§8a), and never was a guardian one
  ([D-061](../decisions/decision-log.md#d-061--event-answers-are-read-by-that-events-organizers)).

**If the split turns out to matter in operation it is still a new decision** — one grant scope over
a defined set of data, argued from the current documents — and not a restoration from this table.
[E-7 is closed](../open-questions.md#e-7--closed--one-level-cannot-separate-the-medical-record-from-the-profile-and-nobody-wanted-to),
so reopening it means producing the case that was declined, not finding the code that was deleted.

See [../data-model/04-relationships.md §2](../data-model/04-relationships.md#2-the-guardians-right-none-view-or-write)
for the value, its defaults by `source`, and the three-value ordering it is a range of — `none` < `view`
< `write`, which is D-074's own ordering over one column and **not** the access-level ladder
[D-099](../decisions/decision-log.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)
deleted. Nothing in this catalog is a range of anything.

## 10. Deferred namespaces

Placeholders for features you have not specified. Listed so the naming convention is
established before anyone invents an inconsistent one.

| Resource | Permission | Notes |
|----------|-----------|-------|
| `document` | `document.view`, `document.create`, `document.edit`, `document.delete`, `document.grant_access` | `document` is already a row of `grant_scope_type`, marked deferred — the item exists in the registry before the module does, which is what the polymorphic `scope_id` is for (D-011). The code is the one this catalog's own §1 rule pays for: `document.grant_access` sits beside `access_grant.create` exactly as `event.grant_access` does, and §12 asks the question once for both. |
| `fee` | `fee.view`, `fee.create`, `fee.waive`, `fee.refund` | ⛔ `fee.waive` and `fee.refund` are sensitive — a hardship waiver must not be visible to whoever happens to run a group. There is no unit level to be below any more, so the mark and the grant list are the whole control. |
| `payment` | `payment.view`, `payment.record`, `payment.reverse` | |
| `report` | `report.finance.view`, `report.membership.view`, `report.safeguarding.view` | ⚠⚠ `report.safeguarding.view` |
| `consent` | `consent.template.edit`, `consent.record.view` | |
| `message` | `message.send_direct`, `message.broadcast` | **Decided in shape, undesigned in detail** ([D-077](../decisions/decision-log.md#d-077--messaging-is-direct-by-default-broadcast-is-an-ordinary-scoped-permission-and-the-recipient-chooses-the-channel)). Everyone may send direct; `broadcast` is an ordinary **scoped** permission. **D-077 wrote "one code at two scopes" when there were two scopes to have** — a unit and the organization; after [D-097](../decisions/decision-log.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row) they are the same scope, so the code reaches everyone when it is held at the unit, and the narrower reading the pair used to buy would have to be a **grant on a `person_group`**, reaching that roster — which is the shape D-099 makes available and D-077 could not have. *Which of those messaging means, and whether `message.broadcast` should be `applies_to = unit_and_item`, is messaging's decision, not this catalog's* (§12). Recipient chooses the channel, which is not a permission at all. **A direct message to a minor is mirrored to that minor's guardians and the sender is told it will be** — no permission, no age branch in the resolver ([D-082](../decisions/decision-log.md#d-082--a-direct-message-to-a-minor-is-mirrored-to-the-minors-guardians)) |
| `partner` | *(namespace)* | For external organizations, if the model expands. |

**What each new resource owes the authorization module changed in round 10, and the old sentence about
it is deleted rather than adapted.** ~~Generate each resource's `permission_level` rows at the same
time.~~ That table is deleted by
[D-099](../decisions/decision-log.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality),
so what a new resource owes is now four things, all of them cheap and all of them required: **codes**
(two or more lowercase segments, first segment = `resource`), each with a **`right_kind`** — `read` or
`write`, required, because that column is a guardian's answer and not a hint (§6) — each with an
**`applies_to`**, checked on save (§1); and a row in **`grant_scope_type`** if its records are things a
grant can be written on, which is what makes a document or a group an item at all.

---

## 11. Roles — proposed seed set

**A starting point, not a specification.** *The heading is kept because its slug is cited from the
decision log and from four other pages, not because the words still fit:* this section used to list
roles with their permissions attached to them, and a role has no contents now. ~~Scope required ·
`Req.` · Waives gate · Key permissions~~ — `role_permission` is deleted, with `role.scope_required`
and `role.requires_membership` beside it
([D-100](../decisions/decision-log.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)),
so **the codes an office carries are the live grants whose expression names it**: one row per code,
each with its own scope and its own period. `MEMBERS * ROLE(treasurers)` on `fee.create` is one such
row, and it — not the office, and not a bundle table nobody read — is what lets a treasurer issue a
fee. What a role *is* now is two things: a name a grant can be aimed at, and the register that answers
*who held this in 2023* (`role_holder` — which is exactly why
[F-12](../open-questions.md#f-12--closed--may-a-role-be-held-by-a-rule-as-an-audience-is) is closed, with the
answer *no*: a holder row names one person). Roles stay runtime data — the organization creates them,
names them, writes and closes their holders, and deletes the unused ones
([§7](../data-model/05-authorization.md#3-role--an-office)). **What is no longer runtime data
is reach**, which is administered through `access_grant.create` and `access_grant.revoke` and is
therefore reviewed in `access_grant`, not in a role editor (§7).

### What the seed ships

**Counting only the tables this section is about: one role and one grant, and the role is empty.**
Everything else the seed carries is vocabulary — the permission rows of this catalog, the
`selector_type` operands (§1), the `grant_scope_type` rows that make an event or a group or a role an
item, and two `is_system` audiences whose expressions are `EVERYONE` and `MEMBERS`
([§7](../data-model/05-authorization.md#12-what-the-organization-starts-with)). **None of those is
authority**, and the sentence is repeated here because this section is where a reader looks for it.

| Seeded row | Table | `is_system` | Holders at seed | What it grants |
|------------|-------|-------------|-----------------|----------------|
| `counselors` | `role` | **yes** | **nobody** — `role_holder` is empty | **Nothing.** A set is not a grant (§1, §5a) |
| `event.answer.view`, item-scoped on an event, aimed at `ORGANIZERS` | `access_grant` | — | — | The one rule that used to be prose in the resolver: answers are read by that event's organizers ([D-061](../decisions/decision-log.md#d-061--event-answers-are-read-by-that-events-organizers), amended by [D-102](../decisions/decision-log.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)) |

**Why a role and not a group**, when D-098's own definition of a group is *"a temporary set of members
that do events together"* and counselors are neither temporary nor event-shaped: the table decides
**which code protects the set**, and every safeguarding convention in this area hangs from that answer
being unchangeable by an ordinary grant — `role.*` is 🔒🔒, `person_group.member.manage` is ⚠
(§5a). **It ships `is_system` so that an editor refuses to delete it**, and so that the §7 rule
*deletable only if never held, and never if it is a system role* has something to refuse.

**Nothing in the seed names `ROLE(counselors)`, and that is the design rather than an omission.**
Being a counselor confers nothing until someone writes the grant
([D-005](../decisions/decision-log.md#d-005--permissions-are-grants-never-derived-from-identity));
D-100 repeats the sentence D-042 has always said. **What that leaves open is not a permission but a
number**, and it is the price D-100 names for moving the gate into the expression: the reach of the
counselor office is only as correct as the roster, so the import reconciliation of
[D-090](../decisions/decision-log.md#d-090--the-legacy-corpus-is-thousands-of-roster-rows-with-numbers-and-no-money)
counts people marked as counselors in the legacy corpus against `role_holder` rows written. An import
that misses three hundred counselors **fails closed** — nobody's access breaks — which is exactly why
nobody notices.

**Who may make someone a counselor, over just that one office.** `role.assign` writes a `role_holder`
row and is `applies_to = unit_and_item` (§7), so holding it **at the unit** lets you fill every office
in the organization, which is what 🔒🔒 is for, while a grant of it **on the item `counselors`** says
*these two may manage the counselor roster* and nothing else. That is D-098's move read symmetrically,
and it is why `role` is a row of `grant_scope_type`.

**The one seeded grant is written without `MEMBERS`, and must not be "corrected."** An organizer
appointed for one weekend is not required to hold a current membership — D-062's appointment model
assumes exactly that — so a `MEMBERS` on that row would take an organizer's read of their own event's
answers away the night their fee lapsed. **It is also the seed's only grant, which means no seeded
grant carries `MEMBERS` at all**, and that is worth stating because one of D-100's three controls
reads *"seeded grants and any grant template carry `MEMBERS`, so the path of least repetition is the
safe path"*: in this seed the path of least repetition carries nothing (§12). *And the seeded row is a
**template** rather than one grant covering every event — a bound operand cannot sit on a unit-scope
grant — so the row a reader finds is written beside each event by the event-creation path (§8a).*

### The worked-example offices

**None of the following ships.** These are the names the rest of the corpus uses whenever it needs an
office to talk about, written out the way an office now has to be written: as grant rows. Each row
below is **one grant per code**, all aimed at one expression, all at the unit — there is nowhere else
for a code about people to be aimed (§1) — each with its own period. Do not read a row as a
requirement, and do not expect the list to survive contact with the organization.

| Office | The grant rows that are its reach | Grantee expression | Why that expression |
|--------|------------------------------------------|--------------------|---------------------|
| `system_admin` | `system.admin` — **one row, and it is enough** | `ROLE(system_admin)` | **no `MEMBERS`**, deliberately: the 1 January case below |
| `registrar` | `person.view` ⚠⚠, `person.create`, `person.edit` ⚠, `person.contact.view` ⚠, `person.contact.edit` ⚠, `account.view` ⚠, `account.create`, `account.suspend` ⚠, `account.close` ⚠, `account.credential.reset` 🔒, `membership.view` ⚠, `membership.request.create`, `membership.request.review` ⚠, `membership.activate`, `membership.backdate` ⚠, `import.view` ⚠, `import.stage`, `import.apply` 🔒, `import.revert` 🔒 — **nineteen rows** | `MEMBERS * ROLE(registrar)` | staff working the organization's own records; the office stops when the fee lapses |
| `membership_approver` | `membership.request.review` ⚠, `membership.request.approve` ⛔ | `MEMBERS * ROLE(membership_approver)` | as above |
| `treasurer` | `fee.view`, `fee.create`, `fee.waive`, `fee.refund`, `payment.view`, `payment.record`, `payment.reverse`, `report.finance.view` | `MEMBERS * ROLE(treasurer)` | as above |
| `safeguarding_officer` | `membership.view` ⚠, `report.safeguarding.view` ⚠⚠, `membership.terminate` ⛔ | `MEMBERS * ROLE(safeguarding_officer)` | whoever finds the problem and whoever ends a membership over it are the same person, and nobody else |
| `leaders` | the thirteen `event.*` codes (§8a), `membership.view` ⚠, `person_group.view` ⚠, `report.membership.view` ⚠ — **sixteen rows** | `ROLE(leaders)` | **this is what `unit_leader` was**, including its `Req. = no`: volunteers, so no `MEMBERS` (property 4) — and nothing bounds it to one unit any more |
| `audience_admin` | `audience.view`, `audience.manage` ⚠ | `MEMBERS * ROLE(audience_admin)` | §5a, including the naming rule this office is subject to |
| `identity_reviewer` | `person.merge` 🔒, `import.view` ⚠, `import.apply` 🔒 | `MEMBERS * ROLE(identity_reviewer)` | and **no `person.view`** — property 5 |
| `auditor` | `audit.view` ⚠⚠, `audit.export` ⚠⚠, `report.view` ⚠ — **read-only, no writes** | `ROLE(auditor)` | **no `MEMBERS`**: an auditor who forgets to pay must not lose the read (property 4) |

**`Term` left the table and went to two places, and that is worth knowing before you set either.**
The old table had one twelve-month column per role. An office is now held for a period
(`role_holder.valid_from`/`valid_to`) **and** every one of its grants has a period of its own, so an
office's reach is an intersection of up to twenty dates, and the question *when does this person stop
being able to do that?* has more than one right answer. Nothing forces either kind of row to end —
[D-071](../decisions/decision-log.md#d-071--nothing-forces-a-role-assignment-to-end-the-gate-and-the-report-are-the-control)
transfers to `role_holder` intact, and the control is still the report.

**Three of these offices name codes this catalog has not registered, and one office is made entirely
of them.** The treasurer's eight rows are `fee.*`, `payment.*` and `report.finance.view`, and all
three of those namespaces are [§10](#10-deferred-namespaces) placeholders — so **that office cannot
be written today**, and its row count is a wish rather than a migration. `safeguarding_officer` and
`leaders` each name one deferred report code among otherwise live rows, which is the milder form of
the same thing. The counts above therefore say what an office would hold once finance ships; the live
half of each list is what a seed migration could insert now. Nothing in the schema stops a grant row
naming a code that does not exist, so this paragraph is
[F-19](../open-questions.md#f-19--closed--a-permission-code-is-a-row-prose-names-codes-and-nothing-checks-the-two)
one section further along: the catalog names the office, the office names the code, and no row agrees.

**Read `event.*` above as a count, not as a wildcard.** Since
[D-068](../decisions/decision-log.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle)
there is no resolver rule that makes `person.*` mean anything; the notation means *"every `person.`
code listed in §2"*, and a real office has an explicit **grant row** for each — which since D-100 is
the only place such a list exists at all. Three consequences for whoever writes these:

1. **`registrar` omits `person.merge` and `person.redact` by not having those rows, and the exclusion
   was always this literal.** It used to be phrased as a caveat about a wildcard's prefix match, and as
   a caveat it was worth a paragraph; now it is simply the two rows nobody inserted, visible in
   `access_grant` with a date and an author and alarmable like any other row. `identity_reviewer` is
   the office that *does* hold `person.merge` — and since round 8 `person.merge` is the whole of
   identity correction: merging, reversing a merge, and deciding a sign-up collision (§2) — listed
   beside `registrar` so the difference between the two is legible. **An office that bundles a resource
   *including* its 🔒 codes should be named for that**, since nothing else records the choice any more;
   the wording here used to say *irreversible* codes, and
   [D-087](../decisions/decision-log.md#d-087--merge-chains-stay-because-reversing-a-merge-is-a-supported-operation)
   removed one of the two that wording pointed at, so the marker is the honest referent —
   `person.redact` is irreversible, `person.merge` is undoable but unions permissions the moment it
   runs.
2. **`leaders` holding `event.*` means thirteen explicit rows** (§8a), and a fourteenth added later is
   *not* in the office until someone writes it. Integrity check 18 surfaces an orphaned permission — one
   **no live grant names** — and it does not surface *"this office arguably should have had it."* That is
   the cost D-068 accepts, and since round 10 it lands here rather than being absorbed silently by a
   resolver: with `role_permission` gone there is no per-office list left for a reader to compare a
   catalog row against, so a documented code that nothing grants is now invisible in a way it never was.
3. **`auditor` is an office that reads the whole person record, and does it without `person.view`.**
   `audit.view` is graded ⚠⚠ in §8 precisely because the payload is a second copy of the record, so
   this row grants a ⚠⚠ read over what the system believed about a child and when it believed it.
   Since [D-088](../decisions/decision-log.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)
   that read has a floor it did not have before: payloads older than 24 months are emptied, so what is
   exposed reaches back two years and no further, while the who-did-what-to-which-row part reaches back
   for the life of the system. That bounds this row's exposure and does not soften its grading. Nothing
   here forbids it — it is a plausible office — but the row must not be described to anyone as "just the
   logs", and it is scoped and dated for the same reason the ⚠⚠ rows above it are.

### The gate moved into the expression

~~`Req.`~~ was `role.requires_membership`: whether the office stopped conferring anything the moment
its holder's fee lapsed
([D-039](../decisions/decision-log.md#d-039--member-permissions-require-a-current-paid-membership)).
~~Waives gate~~ was the separate, person-level *permission* `system.gate_exempt`
([D-051](../decisions/decision-log.md#d-051--the-membership-gate-is-waived-by-a-permission-not-only-by-a-role-flag)),
and the two columns answered different questions and were never alternatives: the flag exempted
everyone holding an office, everywhere, while the permission exempted one named person across every
office they held. **Both columns, both mechanisms and the resolver clause that implemented them are
deleted by D-100.** `MEMBERS` is an operand now, evaluated live on the checked date, and whether an
office survives its holder's lapse is a property of the expression written on the grant:

| Old mechanism | New expression | What the writer is saying |
|---------------|----------------|---------------------------|
| The gate applied to an office with `requires_membership = true` | `MEMBERS * ROLE(x)` | this office is for people who are members right now |
| The gate waived for a whole office | `ROLE(x)` | written **without** `MEMBERS`; a lapse in the fee ledger does not stop this office |
| The gate waived for one named person (`system.gate_exempt`) | `(MEMBERS * ROLE(x)) + PERSON(y)` | one person is the exception, and the exception is visible to everyone who reads the grant |

**A second grant aimed at `PERSON(y)` is the other way to write the third row**, leaving the gated
expression alone; D-100 keeps both legal and calls the second arguably clearer for a permanent
exception, because it keeps the exception off the expression everyone else reads. What is gone is the
*permission* — not the ability.

**The posture reversed, so name the new failure instead of burying it.** The gate used to be
**default-on**, which made forgetting it impossible and waiving it a deliberate act. It is now
**opt-in per grant**: an expression written `ROLE(treasurers)` with no `MEMBERS` authorizes a lapsed
member, silently, for as long as the grant lives. Three controls, none of which is the resolver:

- **The tab on the permissions page, in its `Unusual` section: live grants that name a `ROLE(…)`
  operand and contain no `MEMBERS`.** An office held by a non-member is the case worth a human eye, and
  this population is narrow enough to actually be read — `system_admin`, `leaders` and `auditor` are on it
  here, and all three are on it *because someone chose them*, which is the whole point. It is a section of
  a tab rather than a report, because a report has to be remembered and the writer is already standing on
  that page; and it says *unusual*, never *broken*, because such a grant resolves exactly as written
  ([F-13](../open-questions.md#f-13--closed--a-rule-that-resolves-correctly-but-looks-odd-is-listed-as-unusual-never-as-broken),
  [D-109](../decisions/decision-log.md#d-109--nothing-a-rule-names-is-deleted-deprecated-hidden-disabled--and-a-tab-instead-of-a-report)).
- **Seeded grants and any grant template carry `MEMBERS`**, so the path of least repetition is the
  safe path. *In this seed that control has nothing to work on: the seed's one grant must not carry
  `MEMBERS`, and it is the only one, so every office grant anyone ever writes will have been written by
  hand — the safe path is not the short one. Recorded in §12.*
- **Import completeness.** The counselor office is only as correct as the roster behind it, and the
  gate used to fall out of membership alone; the duty is stated above, and it fails closed.

**One value in the old table was never a preference, and it is the one to copy carefully.**
`system_admin` was marked *Waives gate = yes* because on 1 January the expiry sweep of
[D-040](../decisions/decision-log.md#d-040--the-fee-expires-yearly-a-date-tracked-renewal-window-replaces-a-grace-status)
lapses every membership in the organization including the administrator's, and without the exemption
the person who would repair the system loses the ability to use it on the day it breaks. That is a
property of the system, not a policy choice, and it is carried now by **writing that one row
`ROLE(system_admin)`, with no `MEMBERS`** — which turns a flag nobody read into an expression with
an outage attached to getting it wrong. The loud mistake is the opposite one: writing
`MEMBERS * ROLE(system_admin)` "for consistency" reproduces the lockout, silently, with no error
message — D-051's documented hazard outlives the mechanism that produced it. **Whether any office
in the shipped seed is written this way is a different question, and the answer is no: the seed
contains no office grants at all** ([What the seed ships](#what-the-seed-ships), §12).

> **~~`registrar` holding `unit_participation.view` at organization scope is not a bug, and it will be
> read as one.~~** Both halves of that note died with the hierarchy. The code is deleted (§4), and the
> oddity it defended — a scope that matched only the root's own rows and refused to read into a pack's
> roster, because crossing into a sub-unit took a `scope_exposure`
> ([D-049](../decisions/decision-log.md#d-049--the-root-may-not-read-into-its-sub-units-scopeexposure-is-the-only-crossing),
> [D-041](../decisions/decision-log.md#d-041--belonging-to-a-sub-unit-is-a-participation-record-not-a-membership)) —
> has no subject after [D-097](../decisions/decision-log.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row):
> there is one scope, so there is nothing for it to fail to reach, and `membership.view` answers *who is
> in the organization?* on its own. **What is genuinely lost is the mistake nobody can make any more.**
> The old hazard was a well-meaning administrator widening a parent's role to see a child unit's roster,
> silently reversing D-049; there is no child unit to widen toward, and the equivalent act today — a
> grant at the unit — is not a hazard but the ordinary case.

**Eight properties worth noting: six carried over from the old table and retargeted, two new because
round 10 created them:**

1. **`membership_approver` is separate from `registrar`.** Deciding who becomes a member is
   a different act from processing records. If your organization wants one person to do
   both, hold both offices — which now literally means two holder rows and two sets of grant rows —
   but keep them separately attributable, because that separation is the only thing the office names
   buy.
2. **`safeguarding_officer` holds `membership.terminate`.** The permission to end someone's
   membership sits with the person responsible for safeguarding, not with whoever chases
   fees. This is deliberate. Note that the office **lost** `person.background_check.*` and
   gained nothing in its place, because the organization records no background checks
   ([D-043](../decisions/decision-log.md#d-043--no-background-checks-are-recorded-in-this-system)).
   What it also does not have here is `person.view`: three rows, and the ⚠⚠ one is the report rather
   than the record. **If working a case needs the record, that is a fourth grant row** — scoped, dated,
   attributable, and visible to anyone who asks what this office can read, which is the review §2 moved
   to when it graded `person.view` ⚠⚠.
3. **No office is a guardian.** There used to be a rule that no role bundles
   `dependent.*`, and the namespace it named no longer exists
   ([D-074](../decisions/decision-log.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular)).
   The safeguarding property it protected is the one that survives, restated against the mechanism
   that now provides it: **the guardianship channel is only consulted when the subject of the act
   is someone else, and it only finds a guardianship row.** Leadership is not guardianship, so no
   office hands anyone a guardian's right over a child — not the right to act for that child, and not
   the row that decides what the family may see.
   **What an office can now do, and does openly, is read the child's record.** That sentence used to
   be false, and [D-083](../decisions/decision-log.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)
   is why it is not: with no privileged subset inside the person record, a leader granted `person.view`
   reads the whole of a member's descriptive data, allergy list included
   ([../domain/08-person-data.md](../domain/08-person-data.md)) — **and round 10 widened what one such
   grant means**, because after D-097 there is no narrower scope than the unit for a code about people,
   so that single row reaches every member in the organization (§1). Nothing about leading anything
   grants it: no channel opens on its own, and the row that would is explicit, scoped, dated and
   readable in `access_grant`. That is also why §2 now grades that code ⚠⚠: the safeguarding review
   moved from *"is there a code we kept out of offices?"* to *"which grants were given this one?"*,
   which is a question the catalog can actually answer.
   **Do not re-derive the old rule as a list of codes to keep out of offices** — the rule is about
   the channel, and there is no code left to quarantine.
4. **`system_admin`, `leaders` and `auditor` are the three example offices written without `MEMBERS`,
   and the last two are the successors to the old `Req. = no`.** The rule the old column followed was
   one sentence — **staff-like offices working on the organization's own records require a membership;
   volunteer-facing offices do not** — and it survives as a writing habit, because a resolver clause
   does not survive otherwise.
   The failure it prevents is specific: the volunteer whose own fee is unpaid still runs the Thursday
   meeting, and must not lose their roster the night it lapses. ~~The corresponding
   `position.requires_membership` stays `true`, so the unpaid volunteer shows up on a chase-up report.~~
   Positions are deleted (D-100), so the noticing moved: that volunteer's office now appears in the
   `Unusual` section of the tab on the permissions page — grants naming a `ROLE(…)` operand with no
   `MEMBERS` — **which is how the organization notices, and the resolver is still not how it punishes**. See
   [../domain/06-authorization-model.md §4](../domain/06-authorization-model.md#4-roles-are-offices-groups-are-company).
5. **`identity_reviewer` decides identity questions about children without a read over the person
   record.** The office carries three rows — `person.merge`, `import.view`, `import.apply` — and
   **`person.view` is not among them**: the reviewer works from the candidate pair, the
   `match_signals` recorded against it, and the names and dates those signals compare. That is
   deliberate as it stands — the question being decided is whether two rows are one human, and the
   descriptive values underneath are not evidence about that — and it is the same shape as `auditor`
   reading the trail without holding `person.view`.
   What round 8 changed is the pressure on it. This is now also the office a **blocked sign-up** lands
   on: an account held out of `active` by an unresolved hypothesis, with an age check alerting because
   the stalled item is a person who cannot log in
   ([D-089](../decisions/decision-log.md#d-089--one-live-account-a-colliding-sign-up-files-a-claim-and-creates-nothing)).
   **If reviewers begin asking for context they cannot see, that is the finding to act on**, and the two
   honest answers are a scoped, dated `person.view` on this office, or a review screen that shows more
   of the *signals*. Reaching instead for an organization-wide `person.view` would put the catalog's
   largest ⚠⚠ read in the office with the most write authority over identity. Tracked as
   [F-11](../open-questions.md#f-11--does-the-identity-reviewer-need-to-read-the-person-record-to-settle-a-claim),
   where none of the three positions is yet recorded as taken.
6. **No office in this set holds `person_group.member.manage`, and that is a hole rather than a neutral
   omission** — the sentence used to be about `unit_participation.manage`, and the code is deleted. What
   D-095 decided has not moved: joining a set is somebody else's act, the write is never self-scoped, and
   this code is now the only thing standing between a person and a group's roster (§5a). As written,
   `leaders` may *see* a roster and cannot write one. **The gap is wider than it was, not narrower**,
   because the answer behind D-095 was *"they will be assigned to the unit by the counselors"* — and the
   counselor office is seeded with no grants at all ([What the seed ships](#what-the-seed-ships)), so
   on the shipped seed nobody at all may write a roster. **It is recorded here instead of added to
   the table on purpose**: which volunteer office may put a child on a group's roster is the
   organization's decision, and an appendix that quietly hands it to `leaders` would be making a
   safeguarding choice on someone else's behalf (§12).
7. **`attribute.define` is held by nothing here, and an office is the wrong shape for the answer.**
   [open-questions AT-2](../open-questions.md#at-2--who-curates-the-vocabulary-and-how-long-may-a-proposal-sit)
   points at this section as the place the question gets answered, and the honest answer for a volunteer
   organization is one or two people rather than an office: **a grant aimed at `PERSON(x)`** (§1) is the
   form that fits, with a date on it, and an office would only be a way of making one person's job
   look like a policy. What is *not* the answer is leaving it unheld while proposals keep arriving
   through ordinary data entry (§12).
8. **An office name is now load-bearing in a way it never was, because names are one namespace.**
   A bare name in an expression resolves against `role` and `person_group` together, so an office
   called `leaders` and a group called `leaders` cannot both exist, and the collision is caught on the
   write path rather than by a constraint (there is no constraint spanning two tables)
   ([D-101](../decisions/decision-log.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree),
   [D-081](../decisions/decision-log.md#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now)).
   Every `selector_type.code` is reserved on top of that, so an office called `MEMBERS` is refused when
   it is saved rather than silently rewriting every expression in the system. **`audience_admin` is
   therefore a name with a second duty**: as well as saying who may edit audiences (§5a), it occupies a
   name no group may take — and note that it grants nothing over `person_group` at all, so whoever
   manages audiences and whoever manages groups may be, and here are, different people.

---

## 12. Open issues

- **The catalog's disposition is settled; its contents are not.** It stays comprehensive and
  granular ([D-055](../decisions/decision-log.md#d-055--the-permission-catalog-is-deliberately-comprehensive-and-granular)),
  so there is no longer a "prune this down" review to do.
  What remains is *additive*: each unbuilt module brings its own permissions as it is
  specified, and unused rows cost nothing.
- **Which offices' grants carry `MEMBERS` is now a decision with no default recorded anywhere.**
  ~~Both were attributes of roles, and roles are runtime data the organization administers, so the
  values shown were reasoned defaults~~
  ([D-039](../decisions/decision-log.md#d-039--member-permissions-require-a-current-paid-membership),
  [D-051](../decisions/decision-log.md#d-051--the-membership-gate-is-waived-by-a-permission-not-only-by-a-role-flag)
  — both mechanisms deleted by D-100). The answer is now written into a grant's expression, and the control
  D-100 nominated for it exists — as a section of a page, not a report: **the `Unusual` section of the tab
  on the permissions page lists live grants naming a `ROLE(…)` operand whose expression contains no
  `MEMBERS`** (§11). Round 13 retired the questions this bullet said the specification still owed. *Who runs
  it, how often* has no referent, because a tab is not run; *a warning at save time or a listing afterwards*
  was F-13, and it closed on the weaker half on purpose — nothing is refused and nothing is warned at the
  save, because that test fires on the intended case as often as on the mistake, and a prompt that cries
  wolf teaches the writer to route around it
  ([F-13](../open-questions.md#f-13--closed--a-rule-that-resolves-correctly-but-looks-odd-is-listed-as-unusual-never-as-broken),
  [D-109](../decisions/decision-log.md#d-109--nothing-a-rule-names-is-deleted-deprecated-hidden-disabled--and-a-tab-instead-of-a-report)).
  What is still owed is the thing F-13 itself nominates: whether those `MEMBERS`-less office grants turn out
  to be mistakes or choices.
- **Nothing bounds what a holder of `access_grant.create` may write, and the catalog no longer
  pretends otherwise.** ~~A grant could not carry a level above the writer's own~~ — that was
  `permission_level`'s second job, and the table is deleted by
  [D-099](../decisions/decision-log.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality).
  So **anyone with `access_grant.create` can grant `system.admin` to anyone, including themselves**, and
  the only remaining guard is `applies_to = unit`, which stops the *shape* of the grant and not the act
  (§1, §7). Every earlier answer to "who can grant what" is gone with it: the ceiling was the one thing
  the deleted ladder was still doing, and nothing replaced it. Whether the answer is a second code for
  granting the `system.` namespace, a two-person rule, or "the audit trail and a small organization's
  judgment" is open, and it is the sharpest hole round 10 left in this file.
- **`event.grant_access` may now be an orphan, and it is one the round created.** Its whole purpose was
  to demand a *level* over an event that the general grant path could not express; with the level gone,
  what distinguishes it from `access_grant.create` is the scope alone (§8a). Either it is a scoped
  front door onto the same table — in which case the catalog should say so and the two codes'
  relationship should be an invariant — or it is a code with no remaining subject, which is the class of
  bug D-068 made visible. **It is left in the catalog, marked, rather than deleted here**: deleting a
  code because one mechanism died is the events module's call, not an appendix's.
- **A `deny` that matches no `allow` is invisible, and D-099 asks for a report nobody has written.** The
  new integrity report is *"a live deny matching no live allow is dead weight"* (§9 restates it). It is
  not the same question as integrity check 18's — that one asks which **permissions** no grant names,
  this one asks which **grants** do nothing — and it is easy to under-build: a deny aimed at a set that
  currently resolves nobody looks identical to a deny that is working. Open only as a report with no
  owner; the semantics are settled.
- **A leaf that names nothing is still the empty set, and it is now also a line on a page.** Nothing about
  resolution moved: `EVERYONE - PERSON(x)` with a dead `x` still subtracts nobody and therefore still
  denies everybody, and nothing is refused at save because a leaf is broken
  ([D-106](../decisions/decision-log.md#d-106--a-failed-operand-stays-the-empty-set-the-missing-half-was-a-report-not-a-refusal)).
  What arrived is the report — **an audience carrying a leaf that does not resolve is listed, for the
  audience's owner, in a second column of the page
  [F-21](../open-questions.md#f-21--closed--no-report-a-tab-on-the-permissions-page-and-unbounded-cost-is-accepted-at-the-stated-size)
  already asks for** — and it is the thing that separates the two rows this bullet is about: a deny over a
  set that is genuinely empty, and a deny whose operand has quietly stopped resolving. **The direction is
  the fact worth carrying, not a volume**: a failed operand on the `+` or `*` side *narrows* the set, and a
  failed operand on the `-` side *widens* it, so `-` is not the noisy operator, it is the only one whose
  failed operand can grant — and a check that "fails closed" on that side is fail-closed and
  lockout-everybody in the same step. **And one thing is not a failure at all**: a person with no birth
  date is not a broken `OLDER(18)`. The operand resolves perfectly well, to the set of people who are that
  age on the date being checked, and that person is simply not in it, exactly as a person with no
  membership row is not in `MEMBERS`. A missing value on the person being asked about never reaches the
  report, which is the distinction the page has to preserve or it pages about every incomplete import in
  the legacy corpus. **The page is a query with an owner, not a guard** (D-081's phrase, applied to it by
  D-106): no save depends on it, and the catalog mints no code for reading it.
- **`audience.manage` is one code over an expression, and the largest act it covers is still
  unmarked.** ~~D-091's inclusion arm~~ is gone, and composition *is* the expression now
  ([D-101](../decisions/decision-log.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree)):
  the arm that used to need its own code is an ordinary `+` beside a leaf, and the leaf that should
  worry everyone is `EVERYONE`. What the round took away is an option, not a safeguard: the code's
  former second half — editing a `LIST`'s names apart from the rule — lost its operand when
  [D-105](../decisions/decision-log.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)
  deleted the list, so *may tick names on this audience* without *may rewrite the rule* is no longer a
  shape any code could cover even if one were written; if the need is ever real it is a new question
  about the editor, not an argument that the deletion was wrong.
  The shape of the concern is unchanged and one edit shorter: **whoever can edit one expression can
  widen every live grant aimed at it**, including by writing `EVERYONE`, which is legal, reachable, and
  resolves to non-members and the public — **and the reach is now transitive**, because
  [D-103](../decisions/decision-log.md#d-103--an-audience-may-name-another-audience) lets one audience be
  named inside another, so editing a widely-named audience widens every grant aimed at every audience
  that names it. Either composition is documented as plainly inside
  `audience.manage` — accepting exactly that consequence — or it gets a code of its own; **no code was
  invented here to fill the gap**. The interim control is the editor showing the expanded set and the
  affected grants *before* the save, which is a user-interface requirement carried in
  [../domain/06-authorization-model.md §6.2](../domain/06-authorization-model.md#62-audiences--an-expression-over-named-sets),
  not a permission.
- **Nothing bounds what a permission check costs, and that was a property of this system until this
  round.** The bound lived in `audience.selector_depth_limit` and was refused at the save, which is
  where the sentence *"a check costs a bounded amount"* came from;
  [D-105](../decisions/decision-log.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)
  deleted the column, the bound and the save-time depth refusal together, and kept the two cycle walks
  — inside the tree, and across audiences through every `AUDIENCE(x)` leaf — as the only structural
  guard there is. An expansion that never terminates is still refused, because acyclicity is the one
  thing the deletion did not relax; what a *terminating* expansion costs is bounded by nothing, and that
  is now **accepted rather than merely unaddressed, because the size is finally stated**: a few hundred
  people in the organization, a few dozen registrants on a typical event, a big camp on the order of two
  hundred — a size stated rather than measured, with the trigger written down beside it that a few
  thousand people, or a thousand registrants on one event, reopens the question
  ([D-112](../decisions/decision-log.md#d-112--the-systems-scale-is-stated-hundreds-of-people-tens-of-registrants-per-event)).
  **Round 13 also withdrew the report this bullet used to name:** there is no standing report of the
  widest and deepest audiences, because there are no standing reports of that kind any more — what exists
  is **the tab on the permissions page**, and it lists rules that name something deprecated, hidden or
  disabled or that fail to resolve, saying nothing about how wide any of them is
  ([D-109](../decisions/decision-log.md#d-109--nothing-a-rule-names-is-deleted-deprecated-hidden-disabled--and-a-tab-instead-of-a-report)).
  Two of the three same-shaped controls D-105 counted here have therefore moved: the widest-and-deepest
  report is gone outright, and §11's no-`MEMBERS` listing is now the tab's **Unusual** section rather than
  a report somebody has to remember to run; D-104's by-hand registry diff is the one still a report
  (D-081's *convention, not a guard* survives all three moves). No number makes an audience too wide and
  nothing in the language caps one. The two rules that must outlive any growth are already written —
  a check compiles its expression to a predicate and never materializes the set, and a listing is
  paginated — so this module gets slow before it gets wrong. The catalog mints
  nothing against it: no code governs expansion, and none could — whoever can write `EVERYONE` into
  an expression already holds `audience.manage` (§5a).
- **A grant's reach now moves with the calendar, and there is no write to mark the moment.** `OLDER(n)` and
  `YOUNGER(n)` are ordinary named operands composed by the same three operators as every other (§1), and
  they are the first whose membership changes **with no write at all**
  ([D-107](../decisions/decision-log.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)):
  a person turns eighteen, joins the set, and no row was touched — which is exactly why age *bands*, with
  the per-person expiry dates they would need, are not in this design. **There is no longer an invalidation
  model for this to be an exception to** — because there is no cache left for one to be about.
  ~~The cache is rebuilt nightly in full, immediately on any write to the ruleset, and on explicit request,
  with no per-entry TTL and no table of which write invalidates how wide a fan-out~~
  ([D-111](../decisions/decision-log.md#d-111--the-permission-cache-is-rebuilt-nightly-on-any-ruleset-change-and-on-request))
  and ~~a birthday is not a ruleset write, so a cached answer about an age set may be up to one night stale,
  and the nightly rebuild is what fixes it~~ are both retired by
  [D-114](../decisions/decision-log.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation),
  which deletes the stored answer outright; what survives of D-111 is the version integer, its bump set cut
  to the two tables whose rows change what an expression *means* — `audience_operand` and `selector_type` —
  and what a bump drops is now a compilation, never an answer. **A birthday moves the set at the instant it
  happens.** What [D-107](../decisions/decision-log.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)
  waived was the calendar arriving between two rebuilds, and there are no rebuilds any more: its ruling
  stands, *"...how the rules resolve and IT IS FINE"*, with nothing left for it to be fine about, and
  **"up to one night stale" is deleted from this corpus** — under live resolution a birthday, a period reaching its own
  `valid_to` and a registration write each move the answer at the instant they happen, and so does a
  membership termination, which is the one this design used to get wrong. **One thing follows that is open, and one that is closed, and keeping them apart is the whole
  point.** **Open: nothing bounds what such a check costs** — the bound this system had was a depth bound
  and
  [D-105](../decisions/decision-log.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)
  deleted it, so an age-bearing expression is one more set to expand and it is bounded by nothing; that is
  [F-21](../open-questions.md#f-21--closed--no-report-a-tab-on-the-permissions-page-and-unbounded-cost-is-accepted-at-the-stated-size),
  whose shape this round did not change and whose width it did, and the catalog mints nothing against it:
  **no code, no column, no number, no threshold.** **Closed, and deliberately not a finding here: whom a
  derived set reached.** The preview a writer looked at is a workbench, never a record, and **the record is
  the expression**
  ([D-110](../decisions/decision-log.md#d-110--the-expression-is-the-record-of-whom-a-grant-reached)):
  the audit row says *this person wrote these words, about this item, on this date*, and what the preview
  printed beside it is logged as **a rendering on a date**, never as a statement of who was in it. The
  alternative was keeping that list indefinitely — a per-person record, past
  [D-088](../decisions/decision-log.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)'s
  window, of people who were never granted anything. Ask whom a grant reached in May and the model does not
  read a stored list back, because there is none: it evaluates the words against the data of May, which is
  the property D-107 bought rather than a hole it left, and these documents do not promise the answer.
  Words-only is affordable rather than brave only because nothing a rule names is deleted any more, so the
  words keep resolving
  ([D-109](../decisions/decision-log.md#d-109--nothing-a-rule-names-is-deleted-deprecated-hidden-disabled--and-a-tab-instead-of-a-report));
  what it costs is named here rather than found sideways — **an edit to a shared audience is a
  retrospective edit to every rule that names it**, and the control is the editor printing the resolved set
  before such an edit saves.
  **The premise this rests on is the organization's
  own** — *the people writing the rules WILL know what they are doing* — and it is written down in
  [D-107](../decisions/decision-log.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)
  with its two limits, because a claim about the authors buys nothing about the people a rule reaches and
  nothing about the write that is never recorded.
- **`audience.view` carries no sensitivity mark, and the thing it shows is a list of people.** A grant
  aimed at a name used to point at a set whose contents were mostly typed in; now the same row resolves
  through dated holder rows, group rosters and `MEMBERS`, and an expression containing `EVERYONE`
  resolves to the whole organization and beyond it. Whether reading a resolved expression needs a grade
  of its own — or whether `person.view` already covers it and the *display* is the leak to watch — is
  unsettled (§5a).
- **~~Whether `PERSON(x)` exists~~ — closed: it is a seeded `selector_type` row** (the thirteenth to arrive,
  one of the twelve that remained after round 11 — `LIST` left afterwards, D-105 — one of the fourteen
  D-107 seeded, for one round — and one of the **thirteen** seeded today, D-113 having removed the
  `GUARDIANS` row that should never have been in the registry).** This
  bullet recorded the round's sharpest disagreement, and
  [D-104](../decisions/decision-log.md#d-104--a-permission-codes-last-segment-is-an-action-and-a-registry-that-prose-contradicts-is-a-fiction)
  settles it the way [D-100](../decisions/decision-log.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)
  and D-101's registry amendment already had: *"`PERSON(y)` is a selector, and this entry is the reason
  it had to become one."* So `(MEMBERS * ROLE(x)) + PERSON(y)` parses (§1, §11), and the waiver D-100
  wrote for itself is legal against the registry at last. **`LIST` was never a stand-in, and the reason
  was arithmetic**: `+ LIST` added everyone on that list and `- LIST` removed everyone on it, so an
  audience could not use it to except one person from itself. **That argument is what
  [D-105](../decisions/decision-log.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)
  overturned — not by finding the arithmetic wrong but by deleting the operand it was about**, which is
  worth saying because the arithmetic was the reason both survived one round and the arithmetic was never
  the thing a reader needed. **What is left is a repair, not a question**
  — the two module pages that call `PERSON(…)` *"not in the language at all"*, one of them refusing the
  leaf while its own gate table writes it, and the domain grammar that omits it for the same reason,
  need this round's correction; the registry row and the printed grammar belong to
  [../data-model/05-authorization.md §8](../data-model/05-authorization.md#8-audience--grants-that-target-a-set-of-people)
  and [../domain/06-authorization-model.md §6.2](../domain/06-authorization-model.md#62-audiences--an-expression-over-named-sets),
  not to this appendix. **The fallback survives the answer**: a second grant aimed at the person is the
  other way to write the exception, and the better one when the exception should not appear in the
  expression everybody else reads (§11).
- **The shipped seed contains no office grants at all, so D-100's 1 January assumption is unmet.** The
  entry assumes *"the seeded `is_system` role set contains at least one such office"* written without
  `MEMBERS`; the seed is one empty role and one grant about event answers (§11). Either the seed grows
  an administrative office, or **the first January after go-live is a support call** — and the seed
  control *"seeded grants carry `MEMBERS`, so the path of least repetition is the safe path"* has
  nothing to apply to, which means every office grant in existence will have been written by hand.
- Whether `report.*` should be per-report permissions or one `report.view` with
  row-level filtering.
- Whether the organization has offices this catalog does not anticipate (a chaplain, a
  quartermaster, a camp chief). **This is answerable by the organization itself** rather than by a
  change to the data model and a migration — one `role` row and some grants — which is the point of
  roles being runtime data. Since D-098 the same is true of a set of people who simply do things
  together, and the two are told apart by which table they are in and therefore by which code protects
  them (§5a).
- Which seeded audiences the organization needs beyond `everyone` and `all_members`, and who may create
  a `person_group` — `audience_admin` is proposed, and it is an office rather than a unit leader's extra
  code now that there are no units
  ([D-042](../decisions/decision-log.md#d-042--grants-may-target-audiences-not-only-individuals),
  [F-5](../open-questions.md#f-5--closed--nothing-is-missing-from-the-registry-and-the-last-gap-was-a-selector-that-should-not-have-been-in-it)).
  This bullet used to say *"named groups"* as a kind, opposed to *"built-in audiences"*;
  [D-091](../decisions/decision-log.md#d-091--a-permission-group-is-a-rule-and-a-list-at-once-and-a-rule-may-name-another-group)
  deleted the kinds and D-101 deleted the filling rules, so what is left is genuinely two questions:
  which `selector_type` operands ship — **the count is thirteen today (§1): thirteen for exactly one
  round until [D-105](../decisions/decision-log.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)
  deleted `LIST`, twelve from there until
  [D-107](../decisions/decision-log.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)
  seeded `OLDER(n)` and `YOUNGER(n)` — fourteen, for one round — until
  [D-113](../decisions/decision-log.md#d-113--the-guardianship-channel-has-no-expression-guardians-is-not-a-selector)
  removed the `GUARDIANS` row that should never have been seeded. Closing that row closed the last bullet
  F-5 was still carrying, and by refusal rather than by arrival: the question was *which operand names a
  person's guardians*, and the answer is that none does, because the channel carries a level over a child
  and not a set. Its age bullet had closed in round 12, when `OLDER(n)` and `YOUNGER(n)` arrived as
  registry rows exactly as that entry said they would have to and not as a rule engine; `WHITELISTED`, the
  one name still without stored state, is F-20's question now and not a gap in this registry**
  (§1) — and who may create a group, which is `person_group.create` (§5a).
- **Which office may put a person on a group's roster is unanswered, and on the shipped seed nobody
  may.** ~~Which role holds the right to place a person in a unit~~ — the code and the unit are both
  gone, and what replaced them is `person_group.member.manage`: one code, `applies_to = unit_and_item`,
  never self-scoped, and the only thing between a person and a roster (§5a, §11 property 6). The
  catalog's side is settled; what is missing is a decision the organization records as `role` rows and
  grant rows, not a code.
- **`message.broadcast` lost a scope it was specified against, and messaging has not ruled on the
  consequence.** [D-077](../decisions/decision-log.md#d-077--messaging-is-direct-by-default-broadcast-is-an-ordinary-scoped-permission-and-the-recipient-chooses-the-channel)
  wrote *"one code at two scopes"* — the organization, or one unit — and D-097 collapsed the pair into
  the single unit scope. So a broadcaster reaches everyone, and the narrower reading now has to be a
  grant aimed at a `person_group`, which is a different shape of decision (who may create the group, and
  whether it is the *broadcast* grant or the group roster that carries the ⚠). §10 records it as
  messaging's call; **the catalog has not silently re-specified it either way**, including whether the
  code should become `applies_to = unit_and_item`.
- **`membership.manage` does not exist, and five places in this round's documents refuse it.** D-099
  quotes the organization's own observation — *"on an event, `membership.manage`, or `event.create`, make
  no sense"* — the domain model and the authorization module each restate that sentence as the reason
  `applies_to` exists, and the events page carries a refusal row naming the code. **This catalog has
  never registered it** — membership acts are `membership.activate`, `.lapse`, `.suspend`,
  `.terminate`, `.backdate` and the request pair (§4) — and **no code is minted here to make an example
  true**: a refusal that names nothing refuses nothing, which is the class of bug D-097's `unit_leaders`
  correction exists to warn about. Either those five places re-point the example at a registered code —
  `membership.terminate` is the exact fit, a fact about a person at the unit that no event owns — or the
  code is registered here first, and then it owes what every registered code owes: a `right_kind`, an
  `applies_to`, a ⛔ mark, and a row in §4. **This was one instance of the gap D-104 closes as
  [F-19](../open-questions.md#f-19--closed--a-permission-code-is-a-row-prose-names-codes-and-nothing-checks-the-two):
  a code is a seeded row, this catalog is prose about rows, and the check adopted is a two-way report
  over the seeded registries, run by hand.** D-104 supplied the grammar and the report; **it did not
  re-point these five sentences**, and that repair still belongs to whoever owns each of those pages.
- **The registered spelling of the answer-read code is the catalog's, singular, and the round said so
  out loud.** [../data-model/08-events.md §8](../data-model/08-events.md#selectors-that-bind-to-an-event)
  records that D-102 wrote the plural while its own entry was new, that the two spellings were one code
  and not two, and that **the catalog is the arbiter** — so the seeded grant in §11 and the code in §8a
  are `event.answer.view`, and no other spelling is registered anywhere. That case was easy, because
  the catalog was self-consistent and naming it arbiter settled something. **The hard case ended
  differently, and how it ended is the finding:**
  [D-104](../decisions/decision-log.md#d-104--a-permission-codes-last-segment-is-an-action-and-a-registry-that-prose-contradicts-is-a-fiction)
  greps the closed round for the door-code capability the round spent a dispute on and finds it
  **nowhere** — not in this catalog, not in the events module, not in the ERD, not in the decision log.
  **There is no QR capability, seeded or deferred, anywhere in this system.** A thing was possible in
  prose, was half-designed in the course of arguing about its name, and left as prose: the registry —
  the one place a permission legally exists, since
  [D-072](../decisions/decision-log.md#d-072--the-documentation-carries-no-sql-the-schema-is-the-orms-job)
  made these documents the specification rather than a description of a schema — never had a row, so
  nothing refused anything, and no reviewer asked the one question that ends the argument, *which seeded
  row carries this?* What survives of the dispute is §1's three rules, the report D-104 adopts, and a
  presence story that is `event.presence.mark` and nothing more (§8a,
  [D-067](../decisions/decision-log.md#d-067--presence-is-a-three-valued-fact-on-the-registration)).
  **If door scanning is ever wanted it arrives as an open question and then a decision entry naming the
  permission, the artifact that rotates and who may reprint it — not as a code beside a paragraph about
  a door.**
- **`attribute.define` is in the catalog and in no seed office, and that gap is the open half of the
  design.** The permission and its rules are settled (§2); who holds it, and how long a `proposed`
  code may sit before it is an embarrassment rather than a queue, are not — tracked as **AT-2** in
  [../open-questions.md](../open-questions.md#at-2--who-curates-the-vocabulary-and-how-long-may-a-proposal-sit),
  and §11 property 7 records the shape the answer should take (a dated grant aimed at one person, not an
  office). The risk of leaving it unheld is specific and slow:
  proposals keep arriving through ordinary data entry, and a vocabulary nobody curates stops
  answering questions while still storing everything
  ([../data-model/09-attributes.md §8](../data-model/09-attributes.md#8-integrity-checks)).
  **The import half of this is now answered**, and only that half: the codes the legacy batch's
  column→code map names arrive `live`, because a curator reads the map as one object before the batch
  applies, so the queue does not open several-hundred-deep on day one
  ([D-090](../decisions/decision-log.md#d-090--the-legacy-corpus-is-thousands-of-roster-rows-with-numbers-and-no-money),
  [../domain/03-identity-and-legacy.md §7](../domain/03-identity-and-legacy.md#7-legacy-import-pipeline)).
  Who holds the permission afterwards, day to day, is still what is open.
- **Which role holds the right to place a person in a unit is unanswered in the seed set**, and it is
  now the only question standing between a child and a unit's roster (§11 property 6). The catalog's
  side of it is settled — one code, unit-scoped, never self-scoped — so what is missing is not a code
  but a decision the organization has to record in `role` rows.

**Resolved and no longer open**, kept visible so the reasoning survives: whether
`person.admin` should subsume `person.merge` and `person.redact` (moot — there are no
per-resource `admin` permissions at all, and the question moved into reviewable office contents,
D-068); whether `event.manage_participants` should split off presence (it did, into
`event.presence.mark` — EV-5 asked whether the new code sat a level lower, and
[round 10 deleted the ladder](../decisions/decision-log.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality),
so what survives is the split and the two codes' different `right_kind` (§8a)); the `event` resource's
real permission set (§8a, thirteen codes); ~~whether any permission should require current membership
status (yes, via the role — D-039)~~ — **reversed: no permission requires it**, and the expression on
each grant says who does (D-100, §11); `person.background_check.*` (removed — D-043);
~~`membership.transfer` (obsolete once participation replaced unit membership — D-041)~~ — the
replacement was itself deleted with the hierarchy, so the code is gone outright and moving a person
between groups is `person_group.member.manage` (§5a); whether `org_unit.restructure` includes
reparenting (~~it cannot — D-036~~ — moot twice over: reparenting needed a hierarchy, and
[D-097](../decisions/decision-log.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)
deleted it, so the code is off this catalog and the act is the organization renaming a scope it no
longer stores (§5)); whether reversing a merge deserves a code of its own (it does not —
undoing an identity correction is the same act as making one, so `person.unmerge` is gone from §2 and
unmerge is `person.merge`, D-087); and whether a colliding sign-up needs a claim object and a way to
link it (it needs neither — the hypothesis queue already exists and deciding it is `person.merge`,
D-089). From round 9: whether a person may hold ~~`unit_participation.manage`~~ or ~~`position.assign`~~
over themselves — ~~no, because there is no self-scoped form of either~~ **the same answer, on the two
codes that replaced them**: neither `person_group.member.manage` nor `role.assign` has a self-scoped
form and none will be added, D-095's reasoning transferring intact (§4, §7); whether anything below the
root needed a gate of its own (it did not — and there is no root-or-below any more, and no gate; the
unit type carried no restriction, and D-100 deleted the resolver's membership clause, D-095, D-097);
whether an appointment should also write a role assignment (~~it should not — the derivation belongs on
a group's filling rule, D-091~~ — positions are deleted, filling rules are deleted, and
[F-12](../open-questions.md#f-12--closed--may-a-role-be-held-by-a-rule-as-an-audience-is) is **closed with the
answer no**: a holder row names one person, which is the only way an office can answer *who held this
in 2023*, D-100); and whether group membership needs a rule against nesting now that groups nest
(~~it does not — a cycle is refused when the edge is saved~~ — the edge table is deleted and nesting
moved into the expression tree, where a tree could not cycle on its own; when
[D-103](../decisions/decision-log.md#d-103--an-audience-may-name-another-audience) reopened *an audience
naming another audience*, cycles became possible **between** audiences and the guard came back as a
reachability walk over the reference closure, refused when the row is saved — a depth bound came with
it and [D-105](../decisions/decision-log.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)
deleted that bound while the walks, inside the tree and across audiences, stayed as the only
structural guard there is —
**still a write path with no permission of its own**,
which is the part this catalog cares about, D-101, D-103, D-105). From round 10, additionally: whether a grant
should carry a strength, a locality, or more than one code (no, no, and no — D-099); whether the unit is
a row or a scope (a scope — D-097); whether
anything may be exposed across a unit boundary (there is no boundary to cross — D-031, D-049 and
D-045's `scope.exposure` review are all deleted together); whether leadership is a position (it is an
office, and the elected/appointed distinction survives only as a name the organization invents, D-100);
whether an event has an owner (no — D-102, and `can_event()` with it); whether presence is a set anyone
may be granted over (it is not — `PRESENT` is not seeded, **on the argument it has always stood on and
with the answer unchanged**: a forgotten tick box revoking a leader's access to their own camp. The
refusal is written down in three documents so that nobody re-adds it as a convenience, and nothing in the
language would have caught it structurally in any case — a selector may read a column against a date,
because `OLDER(n)` does, and may be a hard-coded computation in the resolver, because `MEMBERS` is
(D-107, §1)); whether a code's last segment had to be an
action, or merely usually was (**it is a rule now — D-104 promotes §1's two shapes from description to
requirement, names `system.admin` as the single noun allowed, and finds sixty-five of the sixty-six
live codes already obeying it**); and whether `PERSON(x)` is in the selector language at all (it is —
it arrived as the thirteenth seeded `selector_type` row, D-101's amendment, D-104, with `LIST`
deleted it was one of the twelve that remained, D-105, one of the fourteen D-107 seeded, for exactly one
round, and one of the **thirteen** seeded today — D-113 removed a row that should never have been counted,
which is the fourth time this page has had to re-type this number). From round
12, whether `OLDER(n)` may be an operand (**it may: an operand must be a named row of the registry, and
this is a row** — `AGE >= 18` is not expressible because the language has no comparison operator to build
it out of, and D-060's refusal of a rule engine survives the sentence that used to argue for it, D-107),
and whether an unresolvable leaf should stop a save (**no** — it stays the empty set, and it is listed in
the `Broken` section of the tab on the permissions page rather than on a report nobody runs, D-106 as
corrected by D-109, §12 — and round 13 narrowed what can produce one to a single cause, a redacted person). **What closed those two is worth
keeping beside them:** the report D-104 adopts diffs every dotted token in prose against every seeded
registry in both directions, would have caught all four of the round's instances, and **can only ever
be run by hand here, because this repository has no build step** — a convention, not a guard, and the
one that decides whether this catalog's tables and the corpus's prose are still one thing next round.

All tracked in [../open-questions.md](../open-questions.md).
