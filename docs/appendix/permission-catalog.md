# Appendix — Permission Catalog

Every permission code, its namespace, and the grant that carries it.

This is the **proposed** catalog, seeded in
[../data-model/05d-invariants-and-seed.md](../data-model/05d-invariants-and-seed.md#12-what-the-organization-starts-with).

> **What a row here is.** A capability, and nothing more. There is no level paired with a code —
> [D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)
> deleted the ladder that paired them — so **whoever grants it says how far it reaches, for how
> long, and to whom** — in one row, whose grantee is an expression
> ([§1](#what-a-grant-is)). **And §1's two naming shapes are rules now**, not
> descriptions of the rows below: the last segment names the action, a middle segment names something
> the schema stores, no grade words and no prefix — with `system.admin` named as the single exception
> ([D-104](../decisions/round-10b.md#d-104--a-permission-codes-last-segment-is-an-action-and-a-registry-that-prose-contradicts-is-a-fiction)).

> **Deliberately comprehensive and granular, and staying that way**
> ([D-055](../decisions/round-04.md#d-055--the-permission-catalog-is-deliberately-comprehensive-and-granular)).
> This is a **menu, not a checklist.** Administrators assign people only the permissions they
> actually need; that is only possible if the capabilities exist as separate rows to assign.
> Further permissions arrive with the modules not yet specified — documents and communication.
> Events were on that list and are no longer: §8a carries their thirteen codes
> ([§10](permission-catalog-b-roles-and-open-issues.md#10-deferred-namespaces)).
>
> **This is the opposite disposition from roles, and the asymmetry is deliberate.** Roles are
> *runtime data* the organization invents ([D-052](../decisions/round-04.md#d-052--roles-are-runtime-data-the-seed-set-is-not-a-specification));
> permissions are *capabilities the code implements*. You cannot assign a power the data model
> cannot express, so a comprehensive permission catalog costs only rows — while a
> comprehensive *role* list would be a specification pretending to be data.
>
> Codes are still **stable identifiers**: adding one is free, renaming one is a migration
> ([§1](#code-shape)). What is *not* yet settled is the exact contents — tracked in §12.


**Section numbers are shared across the parts** and never renumbered, because other pages cite them by number and their anchors are built from them: §1–§8a (conventions, then every code); [permission-catalog-b](permission-catalog-b-roles-and-open-issues.md) §9–§12 (the namespaces that are not here, the deferred ones, the role seed, open issues).
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
[D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)
the same migration also rewrote `role_permission` rows; that table is deleted, and a grant is now
the only place a code is written down — which makes the rule *smaller*, not weaker.

**Those two shapes are rules for adding a code, and since
[D-104](../decisions/round-10b.md#d-104--a-permission-codes-last-segment-is-an-action-and-a-registry-that-prose-contradicts-is-a-fiction)
they are written here as rules rather than as a description of what is already in the tables below.**
As a description they arbitrated nothing: both readings of one disputed name fitted them exactly, and
that dispute ended with the capability deleted rather than either spelling chosen (§12). Three rules,
and the moment they cost nothing is the moment a code is added:

1. **The last segment names the action.** Read the code on its own and ask *what does this let me
   do?* `event.grant_access` answers it; a noun-final code states an object instead. Since
   [D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)
   a grant permits exactly one thing, so a grant of an object would need a second sentence to say
   what it permits — and a second sentence is where a permission's real scope always hides.
2. **A middle segment names something the schema stores.** `answer` is `event_answer`, `presence` is
   a column of `event_registration`, and `contact`, `credential`, `member`, `participant` and
   `request` are rows. **A permission may not be built out of an artifact the database does not
   keep**, because a grant has to be checkable against stored state and there is none to check
   against: the payment's QR code is exactly that artifact, and
   [D-075](../decisions/round-06.md#d-075--money-arrives-from-a-bank-api-a-payment-is-requested-by-variable-symbol-and-qr-code)
   already ruled it a rendering of three stored facts rather than data. **No code in this catalog
   spells `qr`, and none may** (§12).
3. **No grade words, and no prefix.** Not `admin`, `all` or `everything`, and not any code whose
   meaning is *"every sibling under this prefix"* —
   [D-068](../decisions/round-05.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle)
   deleted sixteen of them and computed the wrong answer for the one it chose to exempt,
   `dependent.admin` — which [D-074](../decisions/round-06.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular)
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

### What a grant is

**A grant is five things: a grantee (a person or an audience expression) + a scope (the unit, or
exactly one item) + one permission code + `effect ∈ allow, deny` + a period.** The answer it feeds:

> **allowed** when some live allow applies **and no** live deny applies.
> ([D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality))

That is the whole of the precedence rule, and it is why nothing in this catalog carries a rank beside a
code. Four things a rank used to promise, and what does each of them now:

- **Bundle several codes under one word** — one grant row per code, and the bundle is a **role** or an
  **audience** ([D-068](../decisions/round-05.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle)),
  which is what *roles are the bundle* already said.
- **Grade one act at two strengths** — two codes, with
  `permission.right_kind ∈ read | write` saying which side each sits on (§6).
- **Decide whether a grant is enough for the code being checked** — nothing to decide: a grant names
  exactly one code and the answer is yes or no.
- **Order two grants that both apply** — two allows produce one answer. **Deny is absolute and is asked
  first** (`effect = deny` on a grant row), which is
  [D-032](../decisions/round-02-03.md#d-032--deny-is-absolute-locality-orders-allows-only)'s surviving half and the
  whole of it.

So there is no word `manage` standing over a set of codes, and *"what does `manage` give me on this
event?"* has no lookup to answer it; *"what exactly does this person have?"* is answered by reading their
grant rows. The rank integer that ladder rested on is gone
([D-012](../decisions/round-01a.md#d-012--status-strings-compare-by-rank-never-lexicographically)), along with the
table that mapped levels onto codes — and the bug that table's guard existed for, `'admin' < 'contribute'`
comparing alphabetically and inverting the model, cannot occur where there are no levels, which is a better
fix than the guard was.

**Two columns moved onto `permission` itself, and only one of them is comfortable.**

- **`right_kind ∈ read | write`** survives **only** so that
  [D-074](../decisions/round-06.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular)'s
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
  ([D-081](../decisions/round-06.md#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now)).

**Scope is two things, not a ladder.** A grant at the unit — the organization, of which there is one,
and which is a scope and never a row
([D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)) —
reaches **every item of every type**. A grant on one item reaches that item and nothing else. There
is no tier between them and no relation on the item to test: no owner, no parent, no covering body.

### A grantee is an expression

Wherever this catalog writes a grantee, it is a legal expression in the selector language of
[D-101](../decisions/round-10b.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree): the
leaves `EVERYONE`, `MEMBERS`, `OLDER(n)`, `YOUNGER(n)`, `PERSON(person)`, `ROLE(name)`, `GROUP(name)`,
`AUDIENCE(name)`, and the five event-bound sets `ATTENDED`, `PLACED`, `CONFIRMED`, `ON_WAITLIST`,
`ORGANIZERS` — each written with its argument spelled out, or bound to the item being checked
([D-102](../decisions/round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it))
— combined with **`+` union, `-` difference, `*` intersection**, and brackets. `*` and `-` bind tighter than
`+`, `*` and `-` bind equally with each other, left to right, and **the stored form brackets every bracket
anyway** ([../domain/06a-audiences-and-selectors.md §6.2](../domain/06a-audiences-and-selectors.md#62-audiences--an-expression-over-named-sets)),
so `(MEMBERS * OLDER(18)) - YOUNGER(6)` is printed exactly as it is stored and nobody has to hold a
precedence table to read a grant row.

**Those leaves are the registry, not a sample of it**, and the registry itself is the seeded `selector_type`
rows: [../data-model/05d-invariants-and-seed.md §12](../data-model/05d-invariants-and-seed.md#12-what-the-organization-starts-with)
states them and counts them, once. The names are repeated here so a grant row can be read where it is
written; a second page printing the count would only be a second thing to go stale.

**A leaf outside that registry does not parse.** Three things the language therefore does not have:

- **No comparison operator.** There is no `>=`, no `<`, no bare `AGE`, so `AGE >= 18` is not an expression and
  cannot become one: an operand must be a **named** row of `selector_type`, and there is nowhere in the
  grammar to put an operator between two things that are not sets. That clause — not any claim about what
  counts as a set — is what keeps eligibility rule engines out
  ([D-060](../decisions/round-05.md#d-060--eligibility-is-capability-there-is-no-separate-rule-engine), as
  amended by [D-107](../decisions/round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)).
  It is not because an attribute differs in kind from a set: `OLDER(18)` is the set of people who are eighteen
  on the date checked exactly as `MEMBERS` is the set of people who pass `is_current_member`, and every
  operand in the registry is a test with a set behind it.
- **No hand-written set.** A list of people typed into a rule is not a leaf and has no table of its own: it is
  a sum, `PERSON(a) + PERSON(b)`
  ([D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)).
  Anything dated and shared is a `person_group` instead — a roster with a lifetime and an owner, rather than a
  second list the permission system keeps.
- **No guardian set.** A guardian's authority is `right_level ∈ none | view | write` over a child (§6,
  [D-074](../decisions/round-06.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular)),
  entered by the shape of the request; the channel resolves no sets, so `GUARDIANS` is not a selector in
  either spelling and no expression names one child's guardians
  ([D-113](../decisions/round-13.md#d-113--the-guardianship-channel-has-no-expression-guardians-is-not-a-selector)).

**Two leaves move with the calendar.** `OLDER(n)` and `YOUNGER(n)` read `person.birth_date` **as of the date
the check is made**, so a person joins or leaves one of those sets with no write of any kind — and a check
asked about a past date answers for that past date. Exactly these two, and no others: the other dated
operands, `ROLE`, `GROUP` and `AUDIENCE`, move when somebody makes a write with a date on it. Nothing is
stored about the answer, so there is nothing to invalidate; a check resolves against live rows, and **a
birthday moves an age set at the instant it happens**, with no job standing between the two
([D-114](../decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation)).
What that costs this catalog is one sentence it used to be able to write — *this is cheap because it is
cached*. What it says instead is what a check actually reads: one indexed read of the checked person's grant
rows per request, plus two batch reads for the shapes that need them, `can_many(person, codes[], item?)` for
a screen's affordances and `which_of(people[], code, item)` for a list's people. No table changes when a
person turns eighteen, so there is no row to expire — which is the property age **bands** would not have
had, and why bands are not in this design.

**The record is the expression.** The editor's preview is a workbench: an audit row logs the words, and a
preview is logged as *a rendering on a date*, never as a statement of who was in it
([D-110](../decisions/round-13.md#d-110--the-expression-is-the-record-of-whom-a-grant-reached), §12).

So `event.answer.view` on an event is aimed at `ORGANIZERS`, an open camp is opened by `MEMBERS`, a gated
office is `MEMBERS * ROLE(treasurers)`, and the exemption for one named person is
`(MEMBERS * ROLE(treasurers)) + PERSON(jan)` — a second grant aimed at that person is the other way to write
the same thing, and it keeps the exception off the expression everyone else reads.

**Three refusals belong next to the language, because each is a temptation this catalog creates.** None of
them is refused on a type argument: a selector may be a hard-coded computation in the resolver, because
`MEMBERS` is one, and an operand may read a column against a date, because `OLDER(n)` does. **Nothing is kept
out of the registry for what it is**, so every refusal here is an argument about consequences.

- **`PRESENT(<event>)` is not seeded,** on the argument that always carried it: `was_present` is `NULL` until
  somebody takes a register, so an operand over it would revoke a child's access to their own camp photos — a
  leader's access to their own camp — because a volunteer forgot to tick a box. Presence stays a three-valued
  safeguarding signal ([D-067](../decisions/round-05.md#d-067--presence-is-a-three-valued-fact-on-the-registration)),
  and nowhere in this file is it a set anyone may be granted over. Nothing in the grammar would stop anybody
  adding it, which is exactly why the consequence has to be the thing that says no.
- **`WHITELISTED` is not seeded because there is nothing stored to evaluate**
  ([F-20](../open-questions.md#f-20--closed--whitelisted-stays-unseeded-because-there-is-no-state-to-evaluate-and-the-feature-arrives-anyway)):
  an operand with no argument, nothing bound to the checked item and no column behind it is a word pointing at
  a state this system does not keep. The feature it was wanted for arrives as grants anyway; whether it is
  wanted at all is an events question, which is where it now lives.
- **A bare name is one namespace across roles and groups**
  ([D-101](../decisions/round-10b.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree)),
  which makes §11's office names a load-bearing vocabulary and makes every selector code a reserved name: an
  office called `MEMBERS` is refused when it is saved, and so is one called `OLDER` or `YOUNGER`. It is the
  parser that refuses them, not a review, which is what keeps `OLDER(18)` from ever meaning an office with
  that name.

### There is no wildcard, except `system.admin`

Every capability in this catalog is **narrow and explicit**. A check for `X.y` is satisfied
by an exact grant of `X.y` — or by `system.admin`, which is checked outright and is the only
permission in the system that means *everything*.

```
A check for 'X.y' is satisfied by: an exact grant of 'X.y', OR 'system.admin'.
```

There are **no per-resource `admin` permissions.** The earlier convention that every resource
should expose an `<resource>.admin` subsuming its narrower codes — a prefix match computed in
the resolver — was **reversed by [D-068](../decisions/round-05.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle)**,
which also deleted the resolver branch that implemented it.

**"Someone who can do everything about events" is a role, not a permission** — the
organization composes it from the thirteen `event.*` codes. That is the division D-052 already
drew: **the code implements capabilities, the organization groups them.** A per-resource
`admin` was the code guessing at a bundle on the organization's behalf. Since
[D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)
the composition is literal: a role confers nothing, so the bundle is thirteen live grants whose
expression names `ROLE(x)` — thirteen rows you can read, which is what D-068 was reaching for.

**The cost, because it is real.** A new narrow permission is *not* automatically covered by the
offices that should imply it; someone must write the grant row. Integrity check **18** is the safety
net the wildcard used to be — it lists permissions **no live grant names**, which is what a missed
bundle looks like now that no role carries a permission list of its own. It fails **closed**: a
capability goes unheld and somebody says so, rather than a capability going unmeant and nobody
saying so.

### Two things named "admin", which are not the same thing

Two meanings survive in this catalog, and they are not the same one:

- **`system.admin`** is the **one wildcard permission**: everything, carried by a grant at the unit and never
  on an item (`applies_to = unit`). It is the only code in this system allowed to end in a noun — exempted by
  name in words by D-068 and named as an exception by
  [D-104](../decisions/round-10b.md#d-104--a-permission-codes-last-segment-is-an-action-and-a-registry-that-prose-contradicts-is-a-fiction),
  because its meaning is defined by the resolver rather than read off the name. **It is not a precedent** (§1).
- **`.admin` is not an action in this catalog.** §1's first naming rule is that the last segment names an
  action ([D-104](../decisions/round-10b.md#d-104--a-permission-codes-last-segment-is-an-action-and-a-registry-that-prose-contradicts-is-a-fiction)),
  and `admin` is a grade word rather than an act: no code here pairs `read` against `admin`, and the rule
  refuses the spelling in codes that have not been written yet. What a bundle of codes is for, a **role** does
  (§1).

Every other thing that spelled `admin` — a grant level, a per-resource wildcard, a shorthand over a
guardian's capabilities — is gone and is indexed in [removed-concepts](removed-concepts.md). Two of those
deletions are worth reading together before reinstating anything that spells the word:
[D-068](../decisions/round-05.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle)
refused a wildcard per resource but deliberately kept one stored shorthand, and
[D-074](../decisions/round-06.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular)
withdrew that exemption when the set it stood for went away — the reasoning about wildcards never changed,
the thing it was a value *of* did.

### Namespaces

| Namespace | Resolved against | Channel |
|-----------|------------------|---------|
| *(absent)* | `access_grant` — aimed at a person or at an audience — and ownership | 1, 3 |
| `system` | `access_grant` **at the unit only** — `applies_to = unit`, so **never** on an item | 1 |

Two prefixes, because only two things are dispatched by a name. The channel numbers are the three in
[../domain/06-authorization-model.md §1](../domain/06-authorization-model.md#1-the-three-channels-of-authority):
grants, guardianship, ownership. **Every code in this catalog — `system.admin` included — arrives through the
one grant channel**, because an office confers nothing by being held
([D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape))
and there is no second route to a code. **What keeps a `system` code out of an item grant is `applies_to`,
checked when the grant is saved**
([D-081](../decisions/round-06.md#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now)),
not the shape of a channel that could carry it: `system.admin` must never reach a single event, a group or an
office.

There is no `dependent` namespace (§9,
[D-074](../decisions/round-06.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular)): a
guardian's rights are one value on the guardianship row, and the `guardianship.*` codes of §6 administer that
row from the grant side — a resource namespace like any other, not the guardianship channel.

**Which leaves the guardianship channel with no prefix to dispatch on, which has to be said rather than left
implied.** It routes on a fact about the request instead of a fact about the name: **the channel is consulted
whenever the person the action is *about* differs from the person performing it.** That holds the invariant
the prefix was standing in for — **no caller chooses a channel**, because a caller who chooses one is the same
authorization rule written twice, once correctly — and it holds it more widely: under a prefix rule, a
guardian asking to change their child's address with a `person.contact.edit` code did not route through
guardianship at all, because the code did not carry the right prefix. Nobody chooses; the shape of the request
selects.

The `guardianship.*` codes are additionally satisfiable by **being a party to the row**, and not only by a
grant ([D-073](../decisions/round-06.md#d-073--guardianship-is-administered-by-its-own-parties-not-by-staff)).

### Sensitivity marker

The **Sens.** column flags permissions that need extra care:

| Mark | Meaning |
|------|---------|
| ⚠ | Granting it exposes personal data |
| ⚠⚠ | Granting it exposes children's personal data — or the same about an adult, where the code reads a whole person record rather than one field of it. Since [D-083](../decisions/round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data) there is **no separate *health data* class to name**: the mark grades what a grant *exposes*, not which field the code points at |
| 🔒 | Granting it confers authority over the permission system itself |
| 🔒🔒 | The **escalating** half of that family: granting it changes what **other people** can do, not merely what the holder can do. `role.*` is marked this way in [D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape), which names it "the most sensitive code family in the catalog" |
| ⛔ | Granting it can end someone's membership or standing |

These marks should drive UI warnings and the alerting in
[../data-model/05d-invariants-and-seed.md](../data-model/05d-invariants-and-seed.md#11-invariants-to-verify).
**A mark grades what a grant exposes, not the table a code names**
([D-086](../decisions/round-07-08.md#d-086--a-sensitivity-mark-grades-what-a-grant-exposes-not-the-table-it-reads)),
and the two families a reader is most likely to place wrongly are placed by it: `person_group.member.manage` takes **⚠** because a
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
> [D-087](../decisions/round-07-08.md#d-087--merge-chains-stay-because-reversing-a-merge-is-a-supported-operation)
> has withdrawn that premise for one of them — a merge can be reversed, and reversing it is a required
> operation. What survives the correction is the half the separation actually rests on: the merged
> **window** cannot be reversed, so the union of two people's permissions is real from the moment the
> merge commits, whatever is discovered afterwards. The separation stands on the narrower reason.
>
> **Three operations, and not one new code.** Round 8 introduced two capabilities and, each time,
> checked whether the catalog needed a row for it
> ([D-087](../decisions/round-07-08.md#d-087--merge-chains-stay-because-reversing-a-merge-is-a-supported-operation),
> [D-089](../decisions/round-07-08.md#d-089--one-live-account-a-colliding-sign-up-files-a-claim-and-creates-nothing)):
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
>   [D-004](../decisions/round-01a.md#d-004--no-automatic-merging-ever) under another name, and its
>   failure mode is one human's descriptive data becoming another human's record.
>
> The check itself is the point: this file is the only list of grantable codes, so a code minted while
> propagating a decision is a migration nobody decided.
>
> **Before [D-068](../decisions/round-05.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle),**
> the way to keep them apart was to carve them out of `person.admin`'s prefix match — a
> special case in the resolver that was invisible in every role editor. Now there is no
> wildcard to carve out of, and the question moves somewhere reviewable: an office bundling all
> of `person.*` reaches them, and you can *see* it — since
> [D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)
> deleted `role_permission`, the bundle *is* the live grant rows naming `ROLE(x)`, one row per code,
> dated and attributable. **The guidance that replaces the special case is in §11** — no seeded
> office mixes `person.merge` or `person.redact` with routine `person.edit`, and one that does should
> be named for what it is. This is now a report a person can read, not a caveat about a resolver rule.

> **`person.background_check.*` is gone** ([D-043](../decisions/round-02-03.md#d-043--no-background-checks-are-recorded-in-this-system)).
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
> [D-083](../decisions/round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data),
> [D-084](../decisions/round-07-08.md#d-084--descriptive-data-is-organization-defined-at-runtime)).
> The catalog's whole involvement in that is one row added and none removed:
>
> - **Read: `person.view`. Write: `person.edit`. That is the entire access story.** **No read or
>   write code was added** for descriptive data, because there is nothing left for one to gate —
>   a code that separated, say, the allergy list from the rest of the record would reinstate the
>   privileged subset [D-083](../decisions/round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)
>   refused on the merits. There is therefore **no `health.*` or `medical.*` namespace and no
>   per-field access rule**, deliberately: `category` on a definition groups a form and grants
>   nothing. If a narrower tier is ever genuinely needed, the route is a decision entry about a
>   **second grant scope over a defined set of data**, not a code with a suggestive name.
> - **`attribute.define` is the new one, and it is the narrow one**
>   ([D-084](../decisions/round-07-08.md#d-084--descriptive-data-is-organization-defined-at-runtime)):
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
> [D-089](../decisions/round-07-08.md#d-089--one-live-account-a-colliding-sign-up-files-a-claim-and-creates-nothing)).
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
> [D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)**
> with the table they read and the sub-units that had rosters. Their work is retargeted, not lost:
> *"who is in the organization?"* is `membership.view` — one query over `membership`, with no depth in
> it — and *"who is in this group?"* and *"write that group's roster"* are `person_group.view` and
> `person_group.member.manage` (§5a,
> [D-098](../decisions/round-10a.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority)).
> Everything D-095 said of `unit_participation.manage` — never self-scoped, the write is somebody
> else's act, the report is the control — transfers to the new code intact, and is written there.

> **`membership.terminate` is the most consequential non-system permission in the
> catalog.** A lapse is administrative; a termination is a decision about a person's
> standing in a youth organization, frequently with safeguarding and reputational
> consequences. It should be held by very few people, and it must not be implied by
> `membership.lapse`. Grant it explicitly, per person — which since
> [D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)
> is the only thing a grant *can* be: one code, one effect.

> **`membership.transfer` is gone, and round 10 removed the sentence that pointed at a replacement.**
> "Transfer a member between units" was an artefact of units holding memberships, and it was last
> answered by *"moving between sub-units is `unit_participation.manage` — close one row, open another"*
> ([D-041](../decisions/round-02-03.md#d-041--belonging-to-a-sub-unit-is-a-participation-record-not-a-membership)).
> **That replacement is now itself deleted** ([D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)).
> The discipline survives and the object moved: moving a person from one group to another is
> `person_group.member.manage` — close one dated row, open another
> ([D-098](../decisions/round-10a.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority),
> [../data-model/02-organization.md §4](../data-model/02-organization.md#4-joins-leaves-and-transfers-close-one-row-open-another))
> — and it does not touch the person's membership at all. There is still nothing to transfer.

> **`person_group.member.manage` has no self-scoped variant, and none will be added**
> ([D-095](../decisions/round-09.md#d-095--units-carry-no-restrictions-joining-one-is-somebody-elses-act),
> whose reasoning
> [D-098](../decisions/round-10a.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority)
> transfers intact). Every grant of it means *"over this group's roster"* or *"over every group's
> roster"*, never *"over my own row"* — so **"nobody writes themselves into a group"** is not a check
> the write performs, it is the shape of the thing being granted: there is no smaller grant to make
> yourself. The same holds for `role.assign` (§7): **nobody appoints themselves**, and D-095's
> instruction was explicitly not to mint a code that could express either act. This is also where the
> safeguarding story moved to. `org_unit_type.allows_minors` was removed a round ago and the units it
> graded are now gone too, so no column anywhere says which sets are for children and nothing here
> refuses to place a minor in one; what is left is this code held by named adults at the unit, the
> write audited the way any business-table write is, its recorded values emptied after 24 months
> ([D-088](../decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)),
> and a report of who holds it
> ([../domain/04-organization-structure.md §3](../domain/04-organization-structure.md#3-joining-a-group-is-somebody-elses-act)).
> **What is lost is not in this list:** D-097 names it plainly — the named adult used to be somebody
> the body chose, and there is no body
> ([../domain/04-organization-structure.md §1](../domain/04-organization-structure.md#1-the-organization-is-one-unit-and-the-unit-is-a-scope)).
> The gate in front of a *membership* is the fee; a group has no fee and no second gate, so this
> permission is the only one
> ([../domain/05-membership-lifecycle.md §1](../domain/05-membership-lifecycle.md#1-the-flow-you-described)).

> ~~**These permissions are gated by membership when held through a role that requires one**
> ([D-039](../decisions/round-02-03.md#d-039--member-permissions-require-a-current-paid-membership)).
> The gate is a property of the *role*, not of the permission, so it is not visible in this table.
> The single exception is `system.gate_exempt` (§7), which *is* the gate's waiver and is therefore
> exempt from the gate itself
> ([D-051](../decisions/round-04.md#d-051--the-membership-gate-is-waived-by-a-permission-not-only-by-a-role-flag)).~~
> **Withdrawn by
> [D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape).**
> Nothing about a code says whether it requires a paid-up holder, so this table has nothing to hide
> and nothing to warn about. **Who performs the membership test now: the grantee expression**, which
> says `MEMBERS * ROLE(x)` when the fee is meant to matter and omits it when it is not — evaluated
> live on the checked date (§11,
> [../domain/06-authorization-model.md §6.1](../domain/06-authorization-model.md#61-members--the-membership-test-moved-into-the-expression)).

## 5. Organization and positions

**Nothing is granted here, because nothing described is left.** Both halves of this title died in round
10 for different reasons: the six `org_unit.*` codes went with the unit hierarchy
([D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row))
and the two `position.*` codes went with positions
([D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)).
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
([D-095](../decisions/round-09.md#d-095--units-carry-no-restrictions-joining-one-is-somebody-elses-act)).
All three of those columns are deleted with the table, and none of them is a self-service door in the
new model either: `role.assign` has no self-scoped form (§7). The reasoning that survives is the one
that made `role.assign` 🔒🔒 — **nobody appoints themselves**, and no code in this catalog can be
sharpened into that act.

**"An appointment writes one row, not two" — and now nothing writes a second row either.** The
sentence existed to stop a leadership position silently deriving authority: the derivation from a
position to a set of people lived in a group's *filling rule*, where it stopped covering the person on
the day the assignment closed
([D-091](../decisions/round-09.md#d-091--a-permission-group-is-a-rule-and-a-list-at-once-and-a-rule-may-name-another-group)).
**Filling rules were superseded by
[D-101](../decisions/round-10b.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree)
and positions by D-100, so the derivation is gone rather than relocated:** a holder row is written by a
named person under `role.assign`, and the only thing that turns it into authority is a grant naming
`ROLE(x)`. *What is genuinely lost is the elected-versus-appointed distinction as stored data*
(D-100): it survives only as offices the organization invents — `elected_council` beside
`appointed_it` — or not at all
([../domain/04-organization-structure.md §6](../domain/04-organization-structure.md#6-appointments)).

> `org_unit.restructure` was separated from routine editing because a split rewrites the answer to
> historical questions. **Reparenting had already been taken out of it** — a unit could not change
> parent at all ([D-036](../decisions/round-02-03.md#d-036--units-cannot-be-reparented-a-unit-that-moves-is-a-new-unit),
> itself now reversed by D-097) — and the splits and mergers it did grant are gone too, so the
> separation is recorded here rather than kept anywhere live.

## 5a. Groups, roles and audiences

Three things the catalog used to describe with units, exposure rows and filling rules, and which are
now three small tables: **a group** (`person_group`, dated member rows, a lifetime) is company
([D-098](../decisions/round-10a.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority));
**a role** (`role`, `role_holder`) is an office, and confers nothing
([D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape));
**an audience** is an expression over named sets, and is what a grant aims at
([D-101](../decisions/round-10b.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree)).
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
| `audience.manage` | — | ⚠ | Create an audience; change its expression — **which is now the whole of it**: the `LIST` this gloss used to add, and the table behind it, are deleted, so a hand-named person is a `PERSON(x)` leaf the same permission already reaches ([D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)) |

> ~~**`scope.expose` and `scope.exposure.review` stood at the top of this section, and `scope.expose`
> was arguably the most consequential permission in the authorization model.** It was the only door
> between unit levels: authority never inherits downward
> ([D-031](../decisions/round-02-03.md#d-031--no-downward-inheritance-of-authority-scope_exposure-is-the-only-crossing)),
> and this was the single mechanism that crossed the boundary — graded 🔒 despite the obscure name, and
> made safe by *who could write it*, since every `scope_exposure` row was written by the unit it
> covers, so a parent's officer could not satisfy it for a child unit
> ([D-049](../decisions/round-04.md#d-049--the-root-may-not-read-into-its-sub-units-scope_exposure-is-the-only-crossing)).
> There was no bulk variant, and every row was a deliberate, attributable decision about one
> assignment
> ([D-045](../decisions/round-02-03.md#d-045--the-bulk-scope-exposure-tool-is-removed)).~~
> **Deleted by
> [D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row),
> with the table, the direction-of-authority check, and the nightly alert that was its only detector.**
> They are kept here struck because the question they answered — *may the center read what happens
> inside a body it does not run?* — **no longer has a subject**, and someone who remembers the answer
> "no, unless the body says so" should find that fact rather than a silent gap. The same reasoning is
> worked through in
> [../domain/06-authorization-model.md §2](../domain/06-authorization-model.md#2-scopes--the-unit-and-the-item).

> **`person_group.member.manage` is a ⚠ next to a 🔒🔒 two rows away, and the gap is the design.**
> [D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)
> refuses to merge `person_group` and `role` into one table with a `kind` column precisely because one
> membership table gives a single code that both adds a child to the Thursday group **and** puts the
> holder into `SYSTEM_ADMINS`. Same columns, different codes, and `GROUP(x)` / `ROLE(x)` distinct in
> the grant text so the difference is visible to whoever reads the grant. **A group additionally
> authorizes nothing by existing**: no parent, no type, no leadership, no roles of its own, no fee —
> a member of a group can *do* nothing, which is
> [D-005](../decisions/round-01a.md#d-005--permissions-are-grants-never-derived-from-identity) one
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
> ([D-042](../decisions/round-02-03.md#d-042--grants-may-target-audiences-not-only-individuals)) —
> authority over *who could be granted*, one step removed from granting. Whether it belongs to a
> dedicated office or to whoever runs things is open (§12).
>
> **It used to be one code over three arms; it is now one code over a whole expression, and the
> hazard changed shape rather than leaving.**
> [D-091](../decisions/round-09.md#d-091--a-permission-group-is-a-rule-and-a-list-at-once-and-a-rule-may-name-another-group)
> let a group be filled by a rule, a hand-kept list, or an inclusion of other groups, and the
> inclusion arm was the one that worried, because *"add the kitchen crew to everything the troop-staff
> group is used for"* silently widened every grant aimed at anything including it. **`audience_include`
> is deleted by [D-101](../decisions/round-10b.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree),**
> along with `include_depth_limit`, the transitive walk and the write-time cycle check over a graph —
> an audience is a tree of `+ - *` now, a tree cannot cycle, and composition happens in the grant
> (`GROUP(kitchen) + ROLE(troop_staff)`) instead of in an edge nobody could see the shape of. What
> did **not** get smaller: `EVERYONE` is a legal operand, so nothing in this table distinguishes
> *"add these five people"* from *"this grant reaches the whole organization"*, and no separate code
> was invented to do it. That stays an open question, not an answer (§12), and until it is answered
> the only control is the one D-091 named and D-102 sharpened: **the editor shows the people a grant
> reaches, expanded, computed for an item, rather than the expression's name**
> ([../domain/06-authorization-model.md §6.2](../domain/06a-audiences-and-selectors.md#62-audiences--an-expression-over-named-sets)).
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
> household, without being granted them.** [D-073](../decisions/round-06.md#d-073--guardianship-is-administered-by-its-own-parties-not-by-staff)
> makes the parties to a guardianship principals on the row: a guardian may end it, add another
> guardian, and change its level; the adult subject may end it over themselves. Staff hold the same
> codes and are **an** route, never **the** route.
>
> `guardianship.permission.grant` is **deleted** — it granted individual codes from the
> `dependent.*` namespace, and there is no such namespace to grant from
> ([D-074](../decisions/round-06.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular)).
> `guardianship.change_right` replaces it, and does less: one value, three choices.
>
> **What the three choices are compared against, now that the ladder is gone.** D-074's `none` /
> `view` / `write` used to be read off the access-level ladder — `write` reached `contribute`, `view`
> reached `view`. **That comparison was deleted with the ladder by
> [D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality),**
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
| ~~`system.gate_exempt`~~ | `system` | ~~🔒~~ | **Deleted by [D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)** — see the note below the table |

> **A role confers nothing.** That is the sentence that rewrites this whole section, and it is worth
> reading before the table above, because three of the six rows above used to mean something they can
> no longer mean. `role_permission` is deleted, and with it the answer to *"what does this role
> grant?"*: **the codes an office carries are the live grants whose expression names `ROLE(x)`**
> ([D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape),
> [../domain/06-authorization-model.md §4](../domain/06-authorization-model.md#4-roles-are-offices-groups-are-company)).
> What `role.create` and `role.edit` touch is a **name, a description, an order** — an office is a set
> with a label, and a set is not a grant
> ([D-005](../decisions/round-01a.md#d-005--permissions-are-grants-never-derived-from-identity)).
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
> [D-095](../decisions/round-09.md#d-095--units-carry-no-restrictions-joining-one-is-somebody-elses-act)):
> the reason it is not a check the write performs is that there is no smaller grant to make yourself.

> **Roles are runtime data, and these six permissions are how the organization administers them.**
> `role.create` names a new office; `role.edit` renames one; `role.delete` removes one created by
> mistake; the reach of any of them is written by `access_grant.create` down the table. §11 is
> therefore a *starting point to be edited*, not a fixed vocabulary — which is why §11 no longer
> claims to answer "which roles are exempt from the membership gate". That question is not answered in
> configuration any more either: it is answered in the text of each grant, by whether its expression
> contains `MEMBERS`.

> **There is no `role.retire`, and a role cannot be switched off**
> ([D-053](../decisions/round-04.md#d-053--a-role-is-valid-always-only-its-assignment-is-temporal)).
> A role is a definition and is valid always; the period lives on the **holder row**. Ending a role's
> use means closing holder rows, which is `role.unassign` — one person at a time, or a loop over the
> holders. This is still the right shape, and the round that deleted the role's own permission list
> left this alone on purpose: what ends is *someone's authority*, and that is a fact about a person,
> not about a definition. **What died with the gate is the reassurance that used to come with it** —
> the old note pointed out that a dormant authority would quietly expire anyway when the holder's fee
> lapsed. Nothing does that now, so the report of holder rows that never end
> ([D-071](../decisions/round-05.md#d-071--nothing-forces-a-role-assignment-to-end-the-gate-and-the-report-are-the-control),
> whose posture transfers from assignments to holder rows) is carrying all of the weight.

> ~~**`role.edit` is a bulk privilege change wearing the clothes of a settings screen.** Editing a
> role's permissions takes effect immediately for **every holder**, with no assignment touched and no
> notification. It is marked 🔒🔒 alongside `role.assign` for that reason. The two are different
> powers — `role.assign` escalates one person, `role.edit` escalates everyone holding the role — and
> neither is implied by the other.~~ **Withdrawn in substance by
> [D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape):
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
> ([D-051](../decisions/round-04.md#d-051--the-membership-gate-is-waived-by-a-permission-not-only-by-a-role-flag)),
> alongside `role.requires_membership`, which waived it for a whole office, and both existed only
> because the resolver asked the question of every grant
> ([D-039](../decisions/round-02-03.md#d-039--member-permissions-require-a-current-paid-membership)).
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
> [D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality),**
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
> [D-083](../decisions/round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)
> refused — and it would hollow out [D-085](../decisions/round-07-08.md#d-085--the-identity-machinery-stays-structured-the-boundary-is-rules-not-sensitivity),
> whose entire justification for overwriting a value in place is that the trail holds the sequence.
> So reading the trail over a scope **is** reading person data over that scope, and reading *more*
> than `person.view` shows: the current row is the organization's present belief, the trail is every
> belief it has held. What protects the trail is therefore the guard on it — scope, this mark, and
> who is granted it — exactly as the guard on `person.view` protects the record. The grading rule this
> applies — **the mark follows what a grant exposes, not the table a code names** — is
> [D-086](../decisions/round-07-08.md#d-086--a-sensitivity-mark-grades-what-a-grant-exposes-not-the-table-it-reads),
> taken during propagation rather than from an answer, and reversible on one line.
>
> **The contents expire, which bounds this exposure without fixing it.** A row lives for the life of
> the system; its `old_values`/`new_values` are emptied **24 months after they were written**, by a
> scheduled job this corpus calls **payload reduction** — a third operation on the trail, distinct
> from redaction (a person's erasure, immediate and absolute, whatever the age of the row) and from an
> import revert ([D-088](../decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)).
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
[D-102](../decisions/round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it),
**an item like any other**. Nothing owns an event: `event.org_unit_id` is deleted, and with it
`can_event()` — the unit-authority rule nearly every code below used to be reached through. A grant at
the unit reaches every event because there is no tier between the unit and the item and no owner to
test; **every event check goes through the ordinary resolver and nothing else.** **Registration is
eligibility** — a live allow of `event.register_self` *is* the rule for who may sign up, and there is
no separate eligibility mechanism
([D-060](../decisions/round-05.md#d-060--eligibility-is-capability-there-is-no-separate-rule-engine)).
**And there is no door code.** The capability these thirteen codes are sometimes read as containing
was never registered anywhere — not in this table, not in any other page
([D-104](../decisions/round-10b.md#d-104--a-permission-codes-last-segment-is-an-action-and-a-registry-that-prose-contradicts-is-a-fiction),
§12); arriving people are recorded by whoever holds `event.presence.mark`, with a clipboard if
necessary, and [D-075](../decisions/round-06.md#d-075--money-arrives-from-a-bank-api-a-payment-is-requested-by-variable-symbol-and-qr-code)
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
[D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)
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
> ([D-062](../decisions/round-05.md#d-062--organizers-are-appointed-on-the-event-not-granted)
> survives untouched — *an `event_organizer` row grants nothing*). Two refusals come with them and both
> land when the grant is saved: a **bound** (argument-less) operand is legal only on an item-scope
> grant, and only where `selector_type.argument_type` matches the item — `PLACED` on a group grant is
> refused because that item is not an event. And `PRESENT(<event>)` is refused outright (§1).
> The definitions, and the reason `PLACED` rather than `ATTENDED` is the capacity set, are in
> [../data-model/08a-event-guards-and-checks.md §8](../data-model/08a-event-guards-and-checks.md#selectors-that-bind-to-an-event).

> **`event.presence.mark` is split off `event.manage_participants` on purpose, and it used to sit a
> level *lower*.** Marking presence is a task handed to whoever is at the door with a clipboard;
> managing the roster is a task for the event's leadership. One permission covering both forces the
> organization to hand the clipboard-holder the ability to delete a child from the camp roster.
> Splitting it costs two rows and makes the ordinary delegation ordinary. **What the split was graded
> with is gone** — the note used to add *"and note the level: presence is `contribute`, the same bar as
> being able to register"*, and there is no bar to compare now
> ([D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)).
> **The split is worth more than the level was:** the distinction the level made softly — this
> volunteer is not roster leadership — is now written as the only thing a grant can say, one code, and
> granting `event.presence.mark` on an event cannot smuggle in `event.manage_participants` the way
> `contribute` once sat underneath `manage`. It follows the shape of `membership.lapse` versus
> `membership.terminate`
> ([D-022](../decisions/round-01b.md#d-022--lapsing-and-termination-are-different-permissions)) —
> one routine, one consequential — and it is free to add because the catalog is a menu, not a fixed set
> ([D-055](../decisions/round-04.md#d-055--the-permission-catalog-is-deliberately-comprehensive-and-granular)).
> **It was previously an open question (EV-5); it is resolved there as a split, and the split
> outlived the ladder it was graded on.**

> **`event.register_self` is the whole of
> [D-060](../decisions/round-05.md#d-060--eligibility-is-capability-there-is-no-separate-rule-engine).**
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
> ([D-070](../decisions/round-05.md#d-070--an-event-has-no-age-ceiling-the-grant-is-the-rule)).
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
> ([D-064](../decisions/round-05.md#d-064--there-is-no-event-status-visibility-is-the-permission-model)).
> **No event with even one registration row may be deleted** — Guard 2 in
> [../data-model/08a-event-guards-and-checks.md §8](../data-model/08a-event-guards-and-checks.md#guards) is the rule, and cancelling
> is what to do instead. The obligation is not the permission's to carry: `event.delete` decides
> who may ask, and only a migration-level constraint — `event_registration.event_id` referencing
> `event.id` with no cascade — refuses the same delete when it arrives from an import or a
> hand-written fix instead of a screen. Enforcing this in the model layer alone would leave the
> record of who was coming deletable by everything except the intended route.

> **`event.answer.view` is where [D-061](../decisions/round-05.md#d-061--event-answers-are-read-by-that-events-organizers) lives, and since round 10 it
> lives there as a *grant*.** The sentence "answers are read by that event's organizers" used to be
> hard-coded prose beside the resolver, reached through the event's owning unit. **`event.org_unit_id`
> is deleted, so the sentence is now said where permissions are said: a seeded grant of
> `event.answer.view`, scoped to the event, aimed at `ORGANIZERS`**
> ([D-102](../decisions/round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)).
> *Because a bound operand is legal only on an item-scope grant, this cannot be one row for every event:
> what ships is a **template**, and D-102 now says plainly that the event-creation path instantiates it
> beside the event row, in the same transaction as the event, and that the import owes one instantiation
> per event it writes
> ([../data-model/08a-event-guards-and-checks.md §8](../data-model/08a-event-guards-and-checks.md#selectors-that-bind-to-an-event)).*
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
> ([D-085](../decisions/round-07-08.md#d-085--the-identity-machinery-stays-structured-the-boundary-is-rules-not-sensitivity)).
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
> children's personal data, graded as though it were logistics. [D-083](../decisions/round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)
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
