# Appendix — Permission Catalog

Every permission code, its namespace, and the grant that carries it.

This is the **proposed** catalog, seeded in
[../data-model/05d-invariants-and-seed.md](../data-model/05d-invariants-and-seed.md#12-what-the-organization-starts-with).

> **What a row here is.** A capability, and nothing more. There is no level paired with a code —
> [D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)
> deleted the ladder that paired them — so **whoever grants it says how far it reaches, for how
> long, and to whom** — in one row, whose grantee is one person, one registered key, or a set written
> as an expression ([§1](#what-a-grant-is)). **And §1's two naming shapes are rules now**, not
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


**Section numbers are shared across the three parts** and never renumbered, because other pages cite them by number and their anchors are built from them: [permission-catalog.md](permission-catalog.md) holds §1, the conventions; [permission-catalog-a-codes.md](permission-catalog-a-codes.md) holds §2–§8b, the codes; [permission-catalog-b-roles-and-open-issues.md](permission-catalog-b-roles-and-open-issues.md) holds §9–§12, the namespaces that are not here, the deferred ones, the role seed and what is open.

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

**The three rules were run against the sixty-six live codes the tables below held when D-104 ran them,
and corrected nothing** — sixty-five satisfy both tests, and the sixty-sixth is `system.admin`. Four
codes have arrived since that count — the `api_key.*` rows of
[§8b](permission-catalog-a-codes.md#8b-keys--a-caller-that-is-nobody) — and they satisfy the three rules
rather than testing them
([D-122](../decisions/round-16.md#d-122--what-a-key-owes-the-catalog-four-codes-at-the-unit-and-the-fourth-owed-thing-declined)).
That null result is the reason this section changed voice rather than its contents: **a convention that is
followed and
not stated fails exactly once, on the first thing nobody thought to compare**, and the thing this
round failed on had never existed anywhere but in prose (§12). **Nothing in the schema will ever
notice a code drifting from its row** — the check D-104 adopts is a person remembering to run a report
over the seeded registries in both directions, which this repository can only ever do by hand
([F-19](../open-questions.md#f-19)).

**This file is the only list of grantable codes, and both directions are decisions.** A code minted while
a decision is being propagated, and a code that simply stops appearing here, are the same mistake: a
migration nobody decided. A decision entry that wants a code adds one to the table of the resource it acts
on, in the same round; a decision entry that removes one leaves a row in
[removed-concepts.md](removed-concepts.md#the-codes-that-left-the-catalog).

### What a grant is

**A grant is five things: a grantee (one person, one audience expression, or one registered key) +
a scope (the unit, or exactly one item) + one permission code + `effect ∈ allow, deny` + a period.**
The answer it feeds:

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

### A grantee is a person, a key, or a set

**A grant names exactly one grantee, and two of the three kinds are a single reference rather than an
expression:** one person, or one registered key (§8b,
[D-116](../decisions/round-16.md#d-116--a-caller-that-is-not-a-person-is-a-registered-key-and-a-key-is-a-third-grantee-kind))
— each read exactly as written, with no set behind it and nothing to evaluate. **The third kind is a set,
and a set is always written as an expression**, in the selector language of
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
  ([F-20](../open-questions.md#f-20)):
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
| *(absent)* | `access_grant` — aimed at a person, at an audience expression, or at a registered key — and ownership | 1, 3 |
| `system` | `access_grant` **at the unit only** — `applies_to = unit`, so **never** on an item | 1 |

Two namespaces, because only two things are dispatched by a name — and the four `api_key.*` codes of
[§8b](permission-catalog-a-codes.md#8b-keys--a-caller-that-is-nobody) are ordinary codes in the row above,
not a third one: their first segment already names a stored table, so a prefix would be a second, drifting
copy of a name the code carries. The channel numbers are the three in
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
