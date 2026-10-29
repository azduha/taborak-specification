# Glossary — Authorization terms

The authorization half of the [glossary](glossary.md): the words a grant, an audience, an
expression or an audit row is written out of. Terms defined elsewhere in the glossary —
[person](glossary.md#identity), [group and office](glossary.md#organization),
[guardianship](glossary.md#relationships) — are not repeated here.

---

## Authorization

**Permission** — The atomic unit of authority: a coded capability such as
`membership.request.approve` or `person.view`. Permissions are the only things the
authorization layer actually checks. Each row carries `applies_to` (`unit`, or
`unit_and_item` — where the code may be granted at all, checked when a grant is saved, so
a grant of `event.create` *written on* an event is refused rather than evaluated) and
`right_kind` (`read` | `write`, which exists for exactly one customer: the guardianship
channel). Codes are stable identifiers, never display strings, and there is no
`<resource>.admin` wildcard and no prefix match
([D-068](decisions/round-05.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle)).
Specified in [data-model/05 §2](data-model/05-authorization.md#2-permission).

**Role** — **An office**, not a bundle: see [Organization](glossary.md#organization). The one
sentence people get wrong — **a role confers nothing**, and the codes it carries are the
live grants naming `ROLE(x)`. Roles are runtime data: the organization invents them,
composes them out of grants and deletes the unused ones, except for the one seeded role
([D-052](decisions/round-04.md#d-052--roles-are-runtime-data-the-seed-set-is-not-a-specification)).

**Scope** — What a grant applies to: **the unit, or exactly one item** (`scope_type` +
`scope_id`), never a nested body and never a choice between several items. Items are
registered in `grant_scope_type` — `event`, `person_group`, `role`, and `document`
deferred — and `unit` is the one row that is not item-scoped. **Inheritance, stated
once:** a grant at the unit reaches every item of every type, because nothing is left
between them and there is no owner to test; a grant on one item reaches that item and
nothing else
([domain/06 §2](domain/06-authorization-model.md#2-scopes--the-unit-and-the-item)).

**Grant** — The whole of the grants channel, and its shape is the whole definition:
**grantee + scope + one `permission_id` + effect + period**, in `access_grant`. The
grantee is a person, an audience **or** an API key — **exactly one of the three, never
two and never none** ([D-116](decisions/round-16.md#d-116--a-caller-that-is-not-a-person-is-a-registered-key-and-a-key-is-a-third-grantee-kind));
the scope is the unit or one item; the effect is `allow` or `deny`; the period is
`valid_from` / `valid_to`, live on the checked date. Plus provenance — `granted_by`,
`granted_at`, `grant_reason`, and for lent authority `is_delegated` with
`delegated_from`. **One code per grant, not a set and not a level**, which is what makes
*"what exactly does this person have?"* a list of rows — a key's list is the same list of
the same kind — and *"who else can do this?"* the same list read the other way. Nothing
adds a membership test to a grant — see **Selector** below. See
[domain/06 §5](domain/06-authorization-model.md#5-the-grant--one-permission-one-effect).

**API key** — `api_key`: **one registered integration that calls this system over an
API**, installed in the system by a named person, and **a grantee** in the same sense a
person is — the third kind named in **Grant** above
([D-116](decisions/round-16.md#d-116--a-caller-that-is-not-a-person-is-a-registered-key-and-a-key-is-a-third-grantee-kind)).
One row is one caller and holds one live secret, which **rotates in place**: replacing the
secret moves no grant and no audit reference, and the row carries a `code` so a grant and
an audit row name the same integration across years. `valid_to` is optional and absent
means current, and **nothing about a key is derived from whoever installed it** —
`created_by` is attribution for an act, and `owner_person_id` is a contact, not a channel
([D-119](decisions/round-16.md#d-119--a-key-is-one-row-holding-one-live-secret-and-it-rotates-in-place),
[D-120](decisions/round-16.md#d-120--a-key-outlives-whoever-created-it-and-the-report-is-the-control)).
What a key is **not**: not an **account**, which is a way for a person to log in; not an
**office**, which a person holds and which confers nothing; not a **selector**, since no
expression may name one and no set contains one, `EVERYONE` included
([D-117](decisions/round-16.md#d-117--a-key-is-never-inside-an-expression-thirteen-selectors-and-none-of-them-can-name-one));
and not a grantable item, because `api_key` is not in `grant_scope_type`. **A key may never
be granted `system.admin`, nor any of `api_key.view`, `api_key.create`, `api_key.rotate`,
`api_key.end`** — *a key may not change what a key can do, and may not become everything* —
refused when the grant is saved, with integrity check 20 the whole net for rows that skipped
the save ([D-122](decisions/round-16.md#d-122--what-a-key-owes-the-catalog-four-codes-at-the-unit-and-the-fourth-owed-thing-declined)).
Specified in [data-model/05e](data-model/05e-keys-and-callers.md).

**Caller** — **Whoever a permission check is answered about: a person, or a key.** The word
is invariant 19's subject: written about a person alone, that invariant would not have
forbidden a table keyed by `api_key_id` and `permission_code` and holding a boolean, and
*"the integration's permissions"* is the most natural such table in this system to write
([D-123](decisions/round-16.md#d-123--invariant-19-reads-a-caller-not-a-person)). **A
request authenticates as a person or as a key, never as both**, and in both audit trails
`actor_person_id` and `api_key_id` are mutually exclusive. One resolver, and one entry point
per kind of caller — **`can(person, permission_code, scope_type, scope_id, at,
owner_person_id)`** and **`can_key(api_key, permission_code, scope_type, scope_id, at)`** —
and the second **takes no person of any kind**: a claimed person would make the trail's word
for who acted an input
([D-121](decisions/round-16.md#d-121--a-key-never-carries-a-persons-authority)).
**Nothing else is** — this system writing to itself is not a third caller, it is an empty actor
column, and it holds no grants (*An empty actor column* below).

**An empty actor column** — `actor_person_id` with nothing in it, in `access_log` or in
`audit_log`, or an empty `created_by` / `updated_by`: **read as this system acting on its own, a
complete answer to "who did this" rather than a missing one.** It is **not a caller** — a check is
answered about a person or a key (see **Caller** above) — and this system holds no grants, is
named by no grant and appears in no `role_holder` row; nothing in a permission check reads an
empty actor column to decide an answer. Two limits keep it narrow: **only where empty is legal**
(`import_batch.created_by` and `api_key.created_by` are required, and a grant's `granted_by`
names a person) and **only in an actor column** — an absent `scope_id` is a check at the unit,
not a writer. **Where the trail has a label column, the writer's name comes from a fixed list**,
so a label such as `system:renewal-sweep` is one of the few names this system signs its own
writes with and **bare `system` is retired**; the list, what it costs, and the check that reports
an off-list label are stated once in
[00-conventions §7a](data-model/00-conventions.md#7a-what-an-empty-actor-column-means)
([D-125](decisions/round-17.md#d-125--an-empty-actor-column-is-this-system-acting-on-its-own-and-its-name-comes-from-a-fixed-list)).

**Allow / deny, and the decision rule** — **Allowed when some live allow applies and no
live deny applies.** That is the whole of precedence, and everything else in the model is
elaboration ([domain/06 §7](domain/06-authorization-model.md#7-precedence)). **A deny is
absolute**: it is checked before anything else, at any scope, so no item is local enough
to override a suspension. A deny is legal at the unit as well as on an item, and is never
conditioned on membership in either direction. **`-` inside an expression is not a deny
and the two are not interchangeable**: subtracting a set narrows *one grant's reach*, while
a deny defeats *every grant* that applies to the grantee it names, written anywhere by
anyone — "she must not have this, whatever else she is given" is only ever a deny.
**Absolute over the grantee it names, and over no other**: a deny on a person leaves a key
standing, and a deny on a key leaves the person who installed it standing
([D-118](decisions/round-16.md#d-118--the-two-channels-that-compare-people-cannot-fire-for-a-key-and-a-deny-on-a-person-does-not-slow-a-key-down)).
The hygiene rule that comes with it is a
report, not a constraint: **a live deny whose grantee, scope and code match no live allow
is dead weight**, and a deny that denies nothing is how a stale restriction survives its
reason.

**Channel** — **There are three, and one absolute deny in front of them**: grants,
guardianship, and resource ownership. Guardianship is reached **when the person the act is
about is not the person performing it**, which nobody has to remember, because the shape
of the call decides — not the permission's name, since a parent editing their child's
address is an ordinary `person.contact.edit` and a name-based rule would have skipped it
([D-079](decisions/round-06.md#d-079--the-guardianship-channel-is-entered-by-shape-not-by-permission-name)).
**Corollary, and the part people get wrong:** the guardianship channel can only say *yes*.
When there is no guardianship, or the right is too low, it says nothing and the person's
grants are still tried — otherwise a parent who is also the event registrar would be
blocked from the roster by their own `view` over their child. Prohibitions are not made
here; they are explicit denies. Roles and groups are not channels: they are sets that
grants point at, and a key is not a fourth one. **Two of these three cannot fire for a key
at all**, because ownership compares a person's id against a row and guardianship needs a
party to a `guardianship` row — neither is refused by a new rule, each is simply
unreachable, so **a key's authority is its grants, in full and only**. A check answered for
a key records `unit_grant` or `item_grant` exactly as one for a person does: **what the
trail adds is *who*, not *how***
([D-118](decisions/round-16.md#d-118--the-two-channels-that-compare-people-cannot-fire-for-a-key-and-a-deny-on-a-person-does-not-slow-a-key-down)).

**Audience** — **The organization's word is *permission group*; the table is `audience`;
both mean one thing.** An audience is **an expression over named sets of people, stored as
a tree of binary rows and aimed at by a grant**
([D-101](decisions/round-10b.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree)).
**Author in sets, evaluate per person**: a check asks about one person, so the resolver
compiles the expression down to a predicate and never materializes a set. The named sets
are the whole vocabulary — `GROUP(x)` (a dated roster), `ROLE(x)` (an office),
`AUDIENCE(code)` (another saved expression), `PERSON(x)` (**one person**, and the only way
to write a set somebody typed by hand: `PERSON(a) + PERSON(b)`) — plus `EVERYONE`,
`MEMBERS`, the two age operands `OLDER(n)` and `YOUNGER(n)`, and the five event operands.
The operators are `+ - *`; the age operands are ordinary named operands composed by those
three, so `MEMBERS * OLDER(13) * YOUNGER(19)` is an ordinary term. **`GUARDIANS` is not in
that list, in either spelling**: guardianship is a channel and not a set, so a kept list
of contact adults is a `GROUP(x)`
([D-113](decisions/round-13.md#d-113--the-guardianship-channel-has-no-expression-guardians-is-not-a-selector)).
**A count of the operands belongs only in the registry table itself**
([data-model/05 §8](data-model/05a-audience-and-grammar.md#the-selector-registry)).
**Fail closed in every direction:** an operand that does not resolve is the empty set, and
an expression that cannot be evaluated reaches nobody. **The direction is the half people
get backwards:** a failed operand on the `+` or `*` side narrows the set and a failed
operand on the `-` side **widens** it, so `EVERYONE - PERSON(x)` with a dead `x` is
fail-closed **and** locks out everybody, in one step, which is not a safe state. An
audience carrying a leaf that does not resolve is listed for its owner, and **no save is
refused because a leaf is broken**. **A missing value on the person being asked about is
not a failure at all** — a person with no birth date is simply not in `OLDER(18)`, exactly
as a person with no membership row is not in `MEMBERS`. Because **a grant's reach is not
visible in the row that grants it**, whoever edits a grant or an audience is shown the
expanded set of people — **for a specific item** — rather than a name
([domain/06 §6.2](domain/06a-audiences-and-selectors.md#62-audiences--an-expression-over-named-sets)).

**Selector** — One **operand** of an audience expression: **a named operand, which means a
row** in the seeded registry `selector_type` (`code`, `takes_argument`, `binds_to_item`,
`argument_type`). The parser reads its reserved words from that table, the editor builds
its dropdown from it, and the save path checks arity against it. **A row is not removable
out from under a rule:** since
[D-109](decisions/round-13.md#d-109--nothing-a-rule-names-is-deleted-deprecated-hidden-disabled--and-a-tab-instead-of-a-report)
a named thing a rule may still name is retired as `deprecated` or `hidden`, both of which
keep resolving, and only `disabled` changes the answer — see *Deprecated / hidden /
disabled*. **What is required of an operand is that it be named, in the registry and not
merely in a sentence** — and that holds of prose too: **every selector name that appears in
these documents must be a `selector_type` row**, which is what a count is a good alarm and a
bad oracle looks like. The registry is a **closed language**: every row ships with
the platform, the table is organization-read-only, and a new operand is a decision entry
plus a seed row, never a row somebody types into a screen. **That closure is the line that
keeps [D-060](decisions/round-05.md#d-060--eligibility-is-capability-there-is-no-separate-rule-engine)'s
refusal of a rule engine true:** `OLDER(13)` is a row, and `AGE >= 13` is not one and
cannot be, because **the language has no `>=` anywhere to put it**. **Eligibility stays
capability: the system applies no gate on its own; a person may write one with the
vocabulary that ships**, and **membership is never implicit**: it is a term the writer puts
in, so requiring it is `MEMBERS * ROLE(x)`, waiving it for a whole office is `ROLE(x)`
alone, and waiving it for one named person is `MEMBERS * ROLE(x) + PERSON(y)`. A grant
naming `ROLE(x)` with no `MEMBERS` authorizes a lapsed member, silently and forever, and
nothing enforces the term — **a convention, not a guard** (see *The permissions tab*, and
the seeded grants and templates that carry `MEMBERS`).
*Why:* the resolver applies no membership test of its own at any scope, so the term is
either written into the expression or it is nowhere
([D-100](decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)).

| Operand | The set, on the checked date | Argument |
|---|---|---|
| `EVERYONE` | Any person, including those with no account and no membership | none |
| `MEMBERS` | Holds a membership live on the checked date | none |
| `OLDER(n)` / `YOUNGER(n)` | **`n` or older** / **strictly under `n`**, both read from the birth date **on the checked date** — so this set gains and loses people at midnight with no write, and `can(..., on date)` for a past date answers for that past date. **A person with no birth date is in neither of them, which is an ordinary answer and not a resolution failure** — as a person with no membership row is not in `MEMBERS` | a whole number of years — **the registry's first argument that is not an entity**, and therefore nothing for a merge to repoint |
| `ROLE(x)` / bare `x` | Holders of that office (`role_holder`) | a role name |
| `GROUP(x)` / bare `x` | Members of that group (`person_group_member`) | a group name |
| `AUDIENCE(code)` | The value of another saved audience's expression | an audience `code` |
| `PERSON(x)` | **One named person** — a set of one, which is a set, so it is an ordinary row of the registry like every other operand. Summed, it is also **the hand-typed set**: `PERSON(a) + PERSON(b)` | a person |
| `ATTENDED` / `PLACED` / `CONFIRMED` / `ON_WAITLIST` / `ORGANIZERS` | The four attendance tiers and the organizer roster | optional event |

Refused, and worth naming because a reader reaches for them: `PRESENT(e)` — a predicate
over the check-in box would revoke a leader's access to their own camp photos whenever
somebody forgot to tick it; `WHITELISTED` — no stored state to evaluate
([EV-6](open-questions.md#ev-6--whitelisted--the-word-people-reach-for-with-no-stored-state-to-name)).
Both are refusals rather than type errors, and neither is seeded
([D-107](decisions/round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)).

**A hand-written set is a sum of `PERSON` leaves.** It inherits the properties a named set
needs: belonging to this one expression, invisible in the group browser, dying with the
audience, and editable one name at a time — `(GROUP(kitchen) + PERSON(honza)) - PERSON(a) - PERSON(b)`.
**What has no spelling is a date on a name**: a sum of leaves carries no `valid_from` /
`valid_to`, so **a time-windowed exception is a second grant with its own period**, and a
reviewer asking *what does this person have?* must find two grants rather than one
audience. Since every hand-named person is a `selector_arg_id`, and **that column
deliberately has no foreign key**, a merge must repoint the leaves that name the absorbed
person ([shape 3](data-model/00a-invariant-register.md#3-the-answer-reads-another-table-a-resolver-or-a-graph)).

**Names are one namespace** across `role`, `person_group` and `audience.code`, and every
`selector_type.code` is a **reserved name** — a group called `MEMBERS` is refused at the
save rather than silently rewriting every expression in the system. No single constraint
spans three tables, so the write path carries the rule and an integrity check asserts the
write path exists
([D-081](decisions/round-06.md#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now)).
What is stored is always kind + id, so **a rename never rewrites a grant**. Bare names do
**not** resolve to audiences: `AUDIENCE(veterans)` is written out
([D-103](decisions/round-10b.md#d-103--an-audience-may-name-another-audience)). And
**nothing a stored expression can name is ever deleted while a rule may name it** — a
`selector_type` row, a `role`, a `person_group`, an `audience` is **given a state instead
of a `DELETE`** — because the namespace has to be stable against renames, deletions and
quiet retirements alike, all three of which rewrite what a rule means without anybody
editing the rule.

**Operand, operator, and the canonical form** — An expression is built from **`+` union,
`-` difference, `*` intersection**, with brackets. **`*` and `-` bind tighter than `+`;
`*` and `-` bind equally, left to right; brackets override** — arithmetic-shaped on
purpose, with one deliberate departure: `-` does not sit beneath `*`, because the first
expression anybody writes in this language, `MEMBERS - GROUP(schuzka2026-1) * COUNSELORS`,
is meant the left-to-right way. **The canonical stored rendering prints every bracket,
always** — `(MEMBERS - GROUP(schuzka2026-1)) * COUNSELORS` — the editor rewriting what is
typed into that form before it saves, so that a grant read two years from now means what
its author meant and a later change of precedence changes nothing already stored. Storage
is a **binary tree**, one row per node (`operator` + `left_id` + `right_id`) or leaf
(`selector_kind` + `selector_arg_id`), with `audience_id` denormalized onto every row; one
parent per node, never a DAG, because a shared node would let one edit silently widen
every grant using it. The tree is stored **exactly as its author wrote it** — one row per
node, left to right, no rebalancing. Cycles are refused at the save by a **reachability
walk over the reference closure**, not just the cheap parent-chain one, because a forest of
trees pointing at each other does cycle. **That walk is the only structural guard:**
**an expansion is bounded by acyclicity alone** — no bound on height, no bound on breadth,
and deliberately no cap on the read path, because a cap there would become the thing that
decides who a grant reaches. So **"a check costs a bounded amount" is not a property of
this system**, and what is accepted instead is a stated size: a few hundred people, a few
dozen registrants on a typical event, a big camp on the order of two hundred
([D-112](decisions/round-13.md#d-112--the-systems-scale-is-stated-hundreds-of-people-tens-of-registrants-per-event)),
with the two rules that must survive any growth being *a check compiles its expression to a
predicate and never materializes the set* and *a listing is paginated*. **Nothing lists the
widest or deepest audiences** — the permissions tab lists only what is broken and what looks
odd — and that is **a convention and not a guard** either way. See
[F-21](open-questions.md#f-21).

**`AUDIENCE(code)`** — The operand that names **another saved audience's expression**,
evaluated live. It is what makes a **rule namable**: `GROUP()` and `ROLE()` name rosters,
so without it the advice *"name the composite once and aim grants at it"* had nothing to
name, and it is the only arm whose argument is a **decision about access** rather than a
roster — *"the same people that grant may see the fee ledger, plus the accountant"*. A
reference names a `code` (optional, unique-where-set) and may not point at an audience
with none; **an audience may not be ended or deleted while a live grant, or a live
audience reachable from a live grant, names it**, because "ended" would otherwise be a way
to silently empty an operand and an empty operand behind a `-` makes the result **wider**;
naming an audience requires reading it and grants no read of it to the people inside it.
**What to do instead of deleting one:** retire it as `deprecated` or `hidden`, both of
which still resolve, and use `disabled` only when emptying it is the intent — see
*Deprecated / hidden / disabled*. **What it costs:** editing a referenced audience is
**a retrospective edit to every grant naming it**, which is why saving such an edit shows
**which grants name it, at what depth, and the set it resolves to** before it commits.
**The record of whom a grant reached is the expression**, the preview is logged as *a
rendering on a date*, and **a history of inner expressions is not kept**; so *"who could
see this child's data in 2024?"* is reconstructable when the grant pointed at a **group**,
whose membership rows are dated, and is **not owed** when it pointed at a nested audience
([D-110](decisions/round-13.md#d-110--the-expression-is-the-record-of-whom-a-grant-reached)).
Recomputation for a past date stays possible and is **never promised**.

Three shapes a set can arrive in: a roster somebody maintains, a saved expression
evaluated live, and one person written into the expression itself.

| | `GROUP(x)` | `AUDIENCE(x)` | `PERSON(x)` |
|---|---|---|---|
| What it is | A dated roster somebody maintains | A saved expression, evaluated live | One person, typed into this expression |
| Who changes who is in it | `person_group.member.manage` | `audience.update` on that audience | whoever may edit this audience |
| Exists outside a grant? | **Yes** | No | No |
| *"Was she in it on 1 June 2024?"* | **Answerable** | **Not past the audit window** | **Not past the audit window** — the leaf is a row of the tree, and the tree's past is an audit payload |
| Sensitive as | ⚠ company | 🔒🔒 authority | 🔒 |

**Bound operand** — The **argument-less** form of an operand that means *relative to the
item being checked*: `PLACED` on the event under check, not `PLACED(1204)`. The form
exists to kill a specific flaw — one grant per event with the event's own id typed into it
is a thing you do 400 times and forget on the 401st — and two rules keep it safe, **both
enforced when the grant is saved**, with the operand named in the refusal: a bound operand
is legal **only on an item-scope grant** (at the unit there is nothing to bind it to) and
**only on a matching item type** (`PLACED` on a group grant is refused, because that item
is not an event — `selector_type.argument_type` checked against `grant_scope_type`). The
consequence: **the set a grant reaches is per-item**, so the editor's preview is computed
for an item and says so on screen. A *Compiled expression* holds no item precisely because
the item arrives as a parameter, so the item is bound at **resolution**, not at
compilation — and nothing resolved while checking one item (a bound operand's set, a
preview's expansion) may ever be served for another. Anything that does cache a
resolution, including a roster cache or an expansion keyed per `(audience, item)`, is
keyed by the item or is wrong on the 401st event. `selector_type.binds_to_item` is true
exactly for **the five event operands — `ATTENDED`, `PLACED`, `CONFIRMED`, `ON_WAITLIST`,
`ORGANIZERS` — which cannot be evaluated without the event the grant sits on**, and is
false for everything else. A bound operand never meant *the subject of the item* and never
will; there is no third binding kind.

**`admin`** — A word to avoid: readers bring three different meanings to it and only one of
them exists here. There is **no grant level** (`access_level`, `permission_level` are not in
this schema, and a grant does not rank) and **no per-resource wildcard** (`person.admin`,
`event.admin` are not codes and nothing matches a prefix). What survives of "can do
everything": **`system.admin`** — the only wildcard permission, seeded
`applies_to = unit`, so it can never arrive through an item grant — and **roles and
audiences**, the bundles the organization composes, where "someone who can do everything
about events" is written out as a couple of dozen grant rows rather than implied by a
resolver rule.

**`is_system`** — The flag meaning *the platform shipped this, so a screen must not destroy
it*. It sits on `permission` (a shipped code can neither be deleted nor renamed), on
`role` (**`counselors` ships with it so an editor refuses to delete the set every
safeguarding convention hangs from**), on the two seeded audiences `everyone` and
`all_members`, and on every `selector_type` row — where its job is specifically **to make
the registry refuse an edit**, which is what makes "a closed language" true of a table
rather than merely asserted. The same protection extends to **organization-named things**
differently: a role, a group or an audience nobody shipped is never deleted at all, only
retired as `deprecated`, `hidden` or `disabled`. It is not a sensitivity mark and not a
category: `applies_to` and `right_kind` grade what a code does, and the catalog's 🔒 marks
grade what it exposes
([D-086](decisions/round-07-08.md#d-086--a-sensitivity-mark-grades-what-a-grant-exposes-not-the-table-it-reads)).

**What is seeded** — Membership ships **one row** (`member` in `membership_type`, kept as a
table so a second kind is a data change rather than a migration); **no group ships at
all**, because a seeded group would be an invented one; and **one role ships**,
`counselors`, marked `is_system`, because a permanent organization-wide population is the
opposite of what a group is. Plus the platform's own vocabulary: the permission codes, the
`grant_scope_type` rows, the `selector_type` rows, and the two audiences `everyone` and
`all_members`. **"Every event's answers go to its organizers" ships as a grant template
rather than a row** — a bound operand is only legal on an item-scope grant, so the
event-creation path instantiates that grant beside each event. Roles, groups and their
rosters are **runtime data** in every other case
([D-052](decisions/round-04.md#d-052--roles-are-runtime-data-the-seed-set-is-not-a-specification)).

**Effective permission** — The union of everything a person may do right now, computed from
live grants whose expressions contain them on the checked date, plus ownership and
guardianship. **Never a table, always derived**, so it cannot drift out of sync with the
grants that produce it: a check resolves against live rows every time, and the only things
that may be kept are a *Compiled expression*, *The request memo* and *The batch reads*.
The *historical* question points at no table either, because **the record of whom a grant
reached is the expression**, not a snapshot of people; a materialized `effective_permission`
table would have to arrive on its own merits, when the stated size says it must, and be named
for what it is ([F-7](open-questions.md#f-7)).

**Compiled expression** — **The only thing in this system that may be cached across
requests, and it is not an answer.** Parse the stored tree once, resolve operand kinds
once, emit the parameterized predicate once — keyed by **the expression's root plus
`ruleset_version`**, and holding **no person and no item**, because both of those arrive as
parameters. Nothing in it depends on whom or where it is being asked about, so the only
writes that can stale one are a change to the words and a change to the seeded vocabulary
they are written in: `ruleset_version`'s entire bump set is **`audience_operand` and
`selector_type`**. **A named roster may also be cached across requests** — `ROLE(x)` over
`role_holder`, `GROUP(x)` over `person_group_member`, keyed by the name — on two
conditions: **the key is the thing the write touches**, so invalidation is local to the row
that changed and never global, and the cache holds **the dated rows, or the set with its
validity ranges**, never *the set as of today*, so the checked date is still applied at
check time and a period ending at midnight needs no job to be seen. **An answer may never
be stored:** invariant 19, TIME-BOMB — **no row, table or field may map a caller, or a
caller-and-code, or a caller-and-item, to a permission answer**, a caller being a person or
a key. `api_key.last_used_at` is not such a row — it says an event happened, and nothing
reads it to decide an answer now
([D-114](decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation),
[D-123](decisions/round-16.md#d-123--invariant-19-reads-a-caller-not-a-person)).
Half of that guard is structural — **the schema has nowhere to put one** — and the residue
is honest: anyone who wants a cache back must arrive with a decision entry carrying a
per-person invalidation handle and a stated list of watched tables **derived from the
operand registry** rather than from a list of ideas; until then it is **a convention, not a
guard**.

**The request memo** — **In-process only, and confined to one request.** One indexed read
fetches the checked caller's live grant rows; every code, item and date that request asks
about is evaluated against them in memory, and a named operand that recurs —
`ROLE(leader)`, `GROUP(cubs)` — is resolved once per request instead of once per check. The
`deprecated | hidden | disabled` flag is read the same way: once per request, memoized for
that request, **consulted live rather than compiled in**. **Lifetime is the request, so it
has no invalidation policy and no staleness window at all**
([D-114](decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation)).

**The batch reads** — **`can_many(person, codes[], item?)` and `which_of(people[], code,
item)`** — the entry points a screen's affordances and a list's people are answered from:
one resolution, one pass. The cost that made a cache look necessary was never one check, it
was the N+1 across a screen. The per-item preview and the permissions tab are written
against these, not against a loop of single checks, and they therefore do their work **on
open**; at the size stated above that is affordable, and it is recorded as **a dependency,
not a measurement**
([F-15](open-questions.md#f-15)).

**Deprecated / hidden / disabled** — **The three states a named thing gets instead of being
deleted**, and the rule that keeps them three different things: **only `disabled` changes
an answer.** Nothing a stored expression can name — a `selector_type` row, a `role`, a
`person_group`, an `audience` — **is ever deleted while a rule may name it**
([D-109](decisions/round-13.md#d-109--nothing-a-rule-names-is-deleted-deprecated-hidden-disabled--and-a-tab-instead-of-a-report)):

| State | Still resolves? | Offered when writing a rule? | Flagged? |
|---|---|---|---|
| `deprecated` | **yes, unchanged** | no — not addable, not introducible by an edit | **yes**, highlighted in the editor wherever it appears |
| `hidden` | **yes, unchanged** | no | no — not obsolete, just not everybody's business |
| `disabled` | **no — the empty set** | no | **yes, and this is the only state that changes an answer** |

**The invariant that stops `deprecated` drifting into `disabled`: deprecating or hiding
what an expression names must not change the set the expression resolves to.** Disabling is
the loudest switch in the module — it stops every rule naming that thing, in every scope,
at once, and re-enabling restores all of them without anybody editing a grant — so
**disabling and re-enabling are audited writes that print the rules they touch**, resolved
before and after. **The flag takes effect *now*** because resolution **consults it live**,
once per request and memoized for that request: a state is **not compiled in** to the
compiled form, which is why the flag left `ruleset_version`'s bump set while still meaning
*now*. **The check worth writing:** if a flag ever *is* compiled into a cached form,
*"deprecating and hiding must not change the answer"* keeps holding while *"disabling takes
effect now"* silently stops being true. Its upside is the answer to *"how do I turn off that
whole naming without editing forty grants?"* **One exception, and it is the only way left to
make a broken leaf: `PERSON(x)` names a person, and redaction can require the row to
actually go — erasure wins.** A person is not a selector, and no convenience owed to an
expression author survives a former member's right to be deleted.

**The permissions tab** — **One place on the permissions page that lists rules worth a
writer's attention, and it has exactly two sections.** **Broken** — a live rule whose
expression names a deprecated, hidden or disabled thing, **or fails to resolve at all**;
its dominant cause is a redacted person. **Unusual** — a rule that resolves correctly and
merely looks odd (a grant naming `ROLE(x)` with no `MEMBERS`), kept **out** of Broken on
purpose: *Broken* says something happened to your rule behind your back, *Unusual* says
your rule means what you wrote. **The two sections make different claims about the writer
and must not be merged.** **It is a convention, not a guard** in a strong sense: **nothing
it lists is blocked, and nothing is refused because it is listed** — what it buys is that a
report has to be remembered and **a tab is where the person already is**. What is on that
page is the tab and nothing else.

**Delegation** — Temporarily granting someone your authority (a leader going on leave).
Modeled as an ordinary grant with its provenance set: `is_delegated`, `delegated_from`
naming who it came from, `grant_reason`, and a mandatory `valid_to`. Because a grant is
**one permission code**, "do not lend more than you hold" is a set-membership test. A deny
cannot be lent and cannot be lent around, and `system.admin` is never delegated. **Lending
is said on the grant, not on the role** (*an assumption; see the index in
[open-questions.md](open-questions.md#i-assumption-index)*).

---

*Decisions behind this page: D-052, D-060, D-068, D-079, D-081, D-086, D-100, D-101, D-103, D-107, D-109, D-110, D-112, D-113, D-114, D-116, D-117, D-118, D-119, D-120, D-121, D-122, D-123, D-125.*
