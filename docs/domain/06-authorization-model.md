# Authorization Model

The permission system end to end. This is the document to read if you read only one.

> **The whole model, stated once.**
>
> **Scopes.** There are two. **The unit** — the organization, of which there is exactly one, and
> which is a scope and never a row — and **one item**: an event, a group, a role, later a document.
> A grant at the unit reaches every item of every type; a grant on an item reaches that item and
> nothing else. There is no tier between them and nothing to test.
>
> **A grant** is: a grantee (a person or an audience) + a scope + **one permission code** + an
> effect of **allow** or **deny** + a period.
>
> **The answer.** Allowed when some live allow applies **and** no live deny applies. There is no
> level, nothing is inherited downward, and no nearer grant beats a further one — because once the
> answer is boolean, there is nothing left to order.
>
> **Roles and groups are not sources of authority.** They are named sets of people that a grant aims
> at.

---

## 1. The three channels of authority

Every question of the form "may person P do X?" is answered by consulting three mechanisms. They
are separate because they have different lifetimes, different granters, and different revocation
semantics.

| # | Channel | Question it answers | Where the answer comes from | Reaches |
|---|---------|--------------------|-----------------------|---------|
| 1 | **Grants** | What has this person, **or this set of people**, been given? | `access_grant`, aimed at a person or an `audience` | The unit, or one item |
| 2 | **Guardianship** | What may this person do *regarding this child*? | `guardianship.right_level` compared with `permission.right_kind` | One dependent |
| 3 | **Resource ownership** | Is this *their own* data? | (derived) | The row's owner |

Channel 3 is not a table. It is the rule that a person may always act on their own profile, their
own requests, their own memberships. It is resolved by comparing `person_id` before the other
channels are consulted.

> **What a channel reaches once one of them says yes.** Each of the three answers *whether*, never
> *how much of a person*: there is one read rule and one write rule over a person's record, and no
> narrower tier standing beside them, so a grant that reaches the record reaches all of it. What that
> consists of, and why there is no sensitive corner left inside it to withhold, is
> [08-person-data.md](08-person-data.md) — worth reading before proposing a fourth channel that
> reaches "only" one kind of fact.

**Why the channels stay apart rather than one unified grants table.** They differ in ways that
matter:

- **Channel 2 has a legal character** — guardianship is a fact about the world, often court-ordered,
  and the organization records what it was told rather than deciding it. **It does not expire by
  itself.** A guardianship ends when a **party to it** says so, and nobody else — not a job, not a
  birthday.
  *Why:* a parent's authority over health and school records does not end at 18 in many
  jurisdictions, and in some it ends at a different age, so any date the system computed would be a
  claim it cannot support
  ([D-069](../decisions/round-05.md#d-069--guardianship-ends-when-a-person-ends-it-the-system-takes-no-position-on-majority)).
- **Channel 1 is the only channel that can name a set** rather than a person
  ([D-042](../decisions/round-02-03.md#d-042--grants-may-target-audiences-not-only-individuals)).
  A guardianship is between two named people and an owner is one person. **That is a boundary, not an
  oversight** — it is why an office can be *aimed at* but never *held by* a rule (§4,
  [F-12](../open-questions.md#f-12--closed--may-a-role-be-held-by-a-rule-as-an-audience-is)).
- **A deny lives in channel 1 and defeats all three** (§7.1). Nowhere else can one be written, and
  nowhere else can one be argued with.

Ownership and guardianship carry no scope, no membership condition, and no level. Nothing in §2 or §6
changes either channel.

### Roles and groups are not channels

A role confers nothing by itself: it is a named set of people that a grant aims at, in the same
sentence as a group, an event's attendees, and "everyone". The codes an office carries are the live
grants whose audience names `ROLE(x)`. Authority therefore has exactly one source besides ownership
and guardianship, and it is [D-005](../decisions/round-01a.md#d-005--permissions-are-grants-never-derived-from-identity)
said one level down: **being something is not being able to do something.**

Whether a person's membership counts is not a channel either. It is a term inside a grant's
expression — `MEMBERS`, evaluated live on the checked date (§6.1) — and never a clause the resolver
adds on its own.

---

## 2. Scopes — the unit and the item

> **There are exactly two scopes.**
>
> **The unit** is the organization. There is one. It is not a row, not a table, and not the top of a
> structure: it is the non-item scope that `grant_scope_type` already carries, whose code is `unit`,
> whose `is_item_scoped` is false, and at which a grant simply has no item to name.
>
> **An item** is exactly one thing: one event, one group, one role, and later one document. A grant
> on it names it.
>
> **Reach is one-directional and there is nothing to test.** A grant at the unit reaches every item
> of every type. A grant on one item reaches that item and nothing else. No item reaches another
> item, and no item reaches the unit.

That is the complete theory of scope. There is no nesting, no path, no depth, no tier between the
unit and the item, and no relation on the item — no owner, no parent, no covering body — that a check
consults. A point-in-time question about people — *who was in the Thursday group in 2011?* — is a
point-in-time read over `person_group_member`, whose rows are dated
([D-098](../decisions/round-10a.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority)).

**Which codes may be granted where is data, not prose.** `permission.applies_to` is `unit` or
`unit_and_item`
([D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)):
`event.create` and `membership.manage` are nonsense *on* an event, and the column says so instead of
hoping a reader agrees. It is checked **when the grant is saved**, not at check time. *Why:* a grant
of `event.create` written on one event is refused with the reason in the error, because an event
cannot be created twice and a creation permission attached to a thing that already exists answers no
question. The `system` namespace is unit-only for the same reason, which makes this column **who
enforces now** the rule that `system.admin` can never arrive through an item grant
([D-081](../decisions/round-06.md#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now)).

**Nothing in the model reproduces "access was granted by the body itself".** There is one unit, so a
`person.view` grant at unit scope reaches every member's whole record — and `person.view` is the
widest read permission in the system
([D-083](../decisions/round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data),
[D-086](../decisions/round-07-08.md#d-086--a-sensitivity-mark-grades-what-a-grant-exposes-not-the-table-it-reads)).
What stands between a person and that read is a `person.view` grant held by a named adult, an audit
trail whose payloads expire after two years
([D-088](../decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)),
and a report of who holds the write.

**Every grant is attributable to one locus of accountability.** *"Who gave this person access to this
record?"* is always answered by a named person at the unit, on a date. It is not necessarily a
*nearby* name: nobody's authority is derived from the body a piece of data belongs to, because there
is one body. There is likewise nothing to restructure, so a grant's blast radius cannot grow by
reorganization.

**Nobody enforces a direction of authority, because there is no direction.** The question *"may the
center read what happens inside a body?"* cannot be asked — not "the application instead of the
database", but unaskable
([D-081](../decisions/round-06.md#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now);
the rule it enforced was
[D-031](../decisions/round-02-03.md#d-031--no-downward-inheritance-of-authority-scope_exposure-is-the-only-crossing)).
The real requirement behind that machinery was *"tell everyone about this event"*, and it is one
grant aimed at `EVERYONE` or `MEMBERS` (§6.2).

### 2.1 `system.admin`

`system.admin` is the one wildcard permission: a check for `X.y` is satisfied by an exact grant of
`X.y` or by `system.admin` and nothing else
([D-068](../decisions/round-05.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle)).
It crosses no boundary, because there is no boundary for it to cross.

Two properties keep a wildcard from being the hole in the design, and both stand on their own:

1. **Its holders are alarmed on.** The report listing current holders must notify on every change — a
   new holder is either a planned act or an incident, and either way someone should know within the
   hour.
2. **It is not delegatable** (§9), and it is `applies_to = unit`, so it cannot arrive on an item.

> If `system.admin` becomes the mechanism by which ordinary organization-wide work is done, that is a
> signal about the catalog rather than about a boundary rule: the work is telling you it needs a
> permission that does not exist. Record it in [the decision log](../decisions/index.md) instead of
> working around it.

---

## 3. Permissions — the atomic unit

A permission is a coded capability. It is the only thing the check function ever looks at.

A permission row carries its `code`, the `resource` and `action` it decomposes into, a
`description`, `is_system` — set for the codes the platform ships with, which therefore cannot be
deleted — and two more columns: **`applies_to`** (`unit` or `unit_and_item`, above) and
**`right_kind`** (`read` or `write`). `right_kind` exists for exactly one customer: guardianship
(§1, channel 2) grades a guardian at `none` / `view` / `write`, and that channel needs something to
compare a permission against. `none` covers nothing, `view` covers `read` codes, `write` covers both.
**It is a column whose only job is one other mechanism, and saying so is cheaper than discovering it
later**
([D-074](../decisions/round-06.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular)).

Codes are `resource.action` and are **stable identifiers**, never display strings. The UI shows a
human label; the code never changes. Renaming a permission code is a breaking change and must be
avoided.

### Naming convention

| Pattern | Meaning | Example |
|---------|---------|---------|
| `<resource>.view` | Read | `person.view` |
| `<resource>.create` | Create (always `applies_to = unit`) | `event.create` |
| `<resource>.<field>.edit` | Edit a field subset | `person.contact.edit` |
| `<resource>.delete` | Delete (soft, and audited) | `document.delete` |
| `<resource>.member.manage` | Write one set's membership | `person_group.member.manage` |

There is no row here for acting on a supervised person, because there is no `dependent.*` namespace
to name
([D-074](../decisions/round-06.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular)).
A guardian's act is checked under the ordinary code for the thing being touched — `person.view`,
`person.contact.edit` — and reaches the guardianship channel by the shape of the request, not by its
name ([D-079](../decisions/round-06.md#d-079--the-guardianship-channel-is-entered-by-shape-not-by-permission-name)).

**Every capability is narrow and explicit.** A check for `X.y` needs an exact grant of `X.y`, or
`system.admin`. There is no `<resource>.admin` wildcard and no prefix match in the resolver
([D-068](../decisions/round-05.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle)).

**An office is a stack of rows, not one word.** The catalog holds 66 codes, and a broad office is a
couple of dozen rows
([appendix/permission-catalog.md §11](../appendix/permission-catalog.md#11-roles--proposed-seed-set)).
*Why:* that is the price of *"what exactly does this person have?"* being answerable by reading rows,
and the reason there is no word like `manage` whose contents a reader would have to look up. Roles
and audiences are the bundle, and nothing else is
([D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)).

---

## 4. Roles are offices; groups are company

Two tables of the same shape, and the difference between them decides **who may edit the
membership**.

| | **Role** (`role`, `role_holder`) | **Group** (`person_group`, `person_group_member`) |
|---|---|---|
| What it is | An **office**: leader, finance, IT. Small, visible holders, expected to be seen | **Company**: the Thursday group, the kitchen crew, this year's camp staff. People who do something together |
| Holder row | `role_holder`(role, person, `valid_from`, `valid_to`, `granted_by`, `note`) | `person_group_member`(group, person, `valid_from`, `valid_to`, `added_by`, `note`) |
| Held where | **At the unit, always.** There is one scope, so there is nothing else to hold it at | The group is its own item, and a grant can be written on it |
| Permission that writes its membership | `role.assign`, `role.unassign` — **🔒🔒, the most sensitive family in the catalog** | `person_group.member.manage` — ⚠ |
| In an expression | `ROLE(x)`, or bare `x` | `GROUP(x)`, or bare `x` |
| Authority by being in it | **None** | **None** |

`role` carries `code`, `name`, `description`, `is_system`, `sort_order` — and no scope column, no
membership flag, no term, and no delegation flag. Lending is said on the grant, not on the role (§9).

**Why two tables when they are technically the same shape** — and they *are* the same shape, which is
exactly what
[D-080](../decisions/round-06.md#d-080--five-contradictions-the-translation-surfaced-and-how-each-was-resolved)
teaches a reader to distrust. The answer is the permission consequence: **one table would merge those
two codes into one.** A single membership table with a `kind` column gives you a single permission
that both adds a child to the Thursday group *and* puts the holder into `SYSTEM_ADMINS`. That is the
merge to refuse. Same columns, **different codes**, and `ROLE(x)` / `GROUP(x)` distinct in the grant
text so the distinction is visible to whoever reads the grant.

**A role confers nothing.** The codes an office carries are **the live grants whose audience names
`ROLE(x)`**. That is what makes *"what may a treasurer do?"* a question with an answer: it is a query
over visible grant rows, not a walk through a bundle table nobody reads. What "the treasurer's
permissions" consists of:

```
role         code = treasurer                (a name, a description, is_system = false)
role_holder  treasurer ← Ana, 2026-01-01 → open
access_grant audience = MEMBERS * ROLE(treasurers)   scope = unit
             permission = fee.view            effect = allow
access_grant audience = MEMBERS * ROLE(treasurers)   scope = unit
             permission = payment.record      effect = allow
access_grant audience = MEMBERS * ROLE(treasurers)   scope = unit
             permission = report.finance.view effect = allow
  … one row per code, and the list is the office
```

**Neither a role nor a group authorizes anything by existing**, which is
[D-005](../decisions/round-01a.md#d-005--permissions-are-grants-never-derived-from-identity) and
[D-019](../decisions/round-01b.md#d-019--household-membership-grants-no-access) restated one level
down: **participation is not authority**, and storing the participation in a tidier table does not
quietly promote it. A group additionally has no parent and no children, no type vocabulary, no code,
no path, no nesting rules, no rename history, no split or merger edge, no leadership of its own, **no
roles**, and no fee
([D-098](../decisions/round-10a.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority)).

**Both are items.** `person_group` and `role` are registered in `grant_scope_type`, so *"these two may
work this group's roster"* and *"these two may manage the counselors roster"* are grants on one item —
reachable only by someone who already holds the corresponding code at the unit (§2).

**Roles are runtime data, and the seed set is not a specification**
([D-052](../decisions/round-04.md#d-052--roles-are-runtime-data-the-seed-set-is-not-a-specification),
[D-053](../decisions/round-04.md#d-053--a-role-is-valid-always-only-its-assignment-is-temporal)):
the organization creates roles, composes them from grants, and deletes the unused ones. The real
definitions live in
[appendix/permission-catalog.md §11](../appendix/permission-catalog.md#11-roles--proposed-seed-set).
One role ships, and ships `is_system` so an editor refuses to delete it: **`counselors`**. A
permanent, organization-wide population is the opposite of the organization's own definition of a
group ("a temporary set of members that do events together"), and the table decides the sensitivity
that protects the set every safeguarding convention hangs from. It is still **only a set** — being in
it confers nothing until a grant names it (§6.2).

**An elected leader is a holder of a role**, and the audience that names them is `ROLE(leaders)`,
meaning what its name says. What is genuinely not stored is the *elected-versus-appointed*
distinction: it survives only as roles the organization invents (`elected_council` next to
`appointed_it`) or not at all, which is the open question
[F-18](../open-questions.md#f-18--does-a-role-record-elected-versus-appointed-and-what-does-an-election-write).
Where the appointment workflows end is
[04-organization-structure.md §6](04-organization-structure.md#6-appointments).

**A role is held by exactly one person per row.** A role cannot be held by a rule the way a group is:
an office record that cannot answer "who was treasurer in 2023" is not an office record, and a derived
holder list cannot answer that
([F-12](../open-questions.md#f-12--closed--may-a-role-be-held-by-a-rule-as-an-audience-is)).
Grants aim at roles rather than roles being filled by grants, which is the same fact seen from the
other side.

### The holder period matters

`valid_from` / `valid_to` on `role_holder` means an office ends on a date even if nobody remembers to
revoke it. Leavers are the classic audit failure: the volunteer who stepped down in 2019 still has an
active account with treasurer access in 2026.

**Nothing forces a holder row to end, and the report is the control**
([D-071](../decisions/round-05.md#d-071--nothing-forces-a-role-assignment-to-end-the-gate-and-the-report-are-the-control)).
No other mechanism stands behind it: the report is carrying the whole weight of expiring authority
(§6.1, §11).

---

## 5. The grant — one permission, one effect

A grant is the whole of channel 1, and its shape is the whole of this section:

> **grantee + scope + one `permission_id` + effect + period.**
>
> **Grantee:** a person **or** an audience, never both and never neither. **Scope:** the unit, or
> exactly one item. **Effect:** `allow` or `deny`. **Period:** `valid_from`, `valid_to`, live on the
> checked date.

Plus provenance: `granted_by`, `granted_at`, `grant_reason`, and for a lent authority `is_delegated`
with `delegated_from` naming who it came from (§9).

**One code per grant, not a set.** That is what makes the answer readable: *"what exactly does this
person have?"* is a list of rows, and *"who else can do this?"* is the same list read the other way.

**Writing a grant is itself an authorized act:** creating one requires `access_grant.create` at the
matching scope. Composing an expression grants nothing (§6.2).

### Allow and deny are not symmetrical

**Allowed when some live allow applies and no live deny applies.** Everything else in this document
is elaboration.

**A deny is legal at either scope.** A deny at the unit is precisely the case an expression cannot
serve: *"exclude her from what the unit grants everyone."*

**`-` in an expression is not a deny, and the two are not interchangeable.** Subtracting a set narrows
**one grant's reach**. A deny defeats **every grant** that applies to that person, including ones
written elsewhere, later, or by somebody else. The first cannot express *"she must not have this,
whatever else she is given"*, which is
[D-013](../decisions/round-01a.md#d-013--explicit-deny-revoked-is-checked-before-everything)'s whole
reason for existing: a court-ordered restriction must not be beatable by a broader grant someone
forgot about
([D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)).

**One report comes with this, and it is the whole hygiene of the thing.** A live deny whose grantee,
scope and code match **no live allow** is dead weight, and it should be reported — a deny that denies
nothing is how a stale restriction survives its reason. Nothing enforces it; the report is the
mechanism (§11).

### Why `scope_type`/`scope_id` and not one column per item type

`scope_id` has no foreign key — it is a polymorphic reference, and this is a deliberate, accepted
trade-off
([D-011](../decisions/round-01a.md#d-011--scope_id-on-access_grant-is-polymorphic-with-no-foreign-key)):

- **Cost:** no referential integrity. A grant can point at a deleted event.
- **Benefit:** the permission system does not need a schema change every time a new grantable thing
  is invented, which — since documents and everything else are still deferred — will happen
  repeatedly.

Mitigations, all of which are required: the `grant_scope_type` registry validates scope types;
deleting an item of a granted type must close its grants (an application-level obligation, tested); a
nightly job reports orphaned grants; ids are never reused. The heavier alternative — a
`grantable_item` supertable every grantable entity references — is declined for flexibility, and is
[../open-questions.md](../open-questions.md) if anyone wants to overrule it (F-2).

---

## 6. The resolver

One function answers every authorization question. Written once, used everywhere — an authorization
rule that exists in two places will diverge.

The call names **a person, a permission code, a scope, and a date.** The scope is the unit or exactly
one item: asking at the unit is how "may this person create an event?" is asked, and asking at an item
is how "may this person edit event 1204?" is asked. `at` defaults to now. Where the thing being
touched has an owner, the caller passes the owner too, because one step below needs to know whose
record this is. The answer is allowed or denied; the function has no other output, and no part of it
is stored. (Field names and the exact signature are in
[data-model/05 §10](../data-model/05-authorization.md#10-the-resolver).)

The steps run in this order:

0. **Deny — absolute, at any scope.** If any live deny applies — its scope is the unit or the exact
   item being checked, its code is the code being checked, its grantee is this person or an audience
   whose expression contains them on the checked date — **the answer is no**. No scope outranks a
   deny, and neither does a channel: a per-event allow cannot restore what a unit-scope suspension
   removed (§7.1).
1. **Ownership.** If the target resource's owner is this person → **yes** for the read, edit and
   self-service actions. Never conditioned on anything (§6.1): a lapsed person must still be able to
   reach the screen they renew on.
2. **Guardianship — entered by the shape of the request, and it answers with allows only.** Compare
   the actor with the owner of the thing being touched. Same person, and this channel is not in play
   at all. Different people, and the question is whether the actor holds a **live guardianship over
   that subject as of `at`** whose right level covers the checked permission's `right_kind` — `view`
   covers `read`, `write` covers both, `none` covers nothing
   ([D-074](../decisions/round-06.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular)).
   Covered → **yes**. Every other outcome — no row, `none`, a level too low — is **not a refusal**:
   the channel says nothing and the resolver continues, where the person's own grants are tried
   exactly as they always were
   ([D-079](../decisions/round-06.md#d-079--the-guardianship-channel-is-entered-by-shape-not-by-permission-name)).
   A parent who is also the event registrar holds `view` over their own child and must not be refused
   the roster by their own guardianship.

   - **Nothing escapes by naming.** The act that routes here is chosen by *whose record it touches*,
     so a permission written next year for a field a guardian must edit is covered the day the field
     exists. Dispatch never reads a code's prefix: an ordinary `person.contact.edit` must reach this
     step like any other act.
   - **An ended guardianship never opens this channel again.** What a former guardian may still do is
     what any other person may do, through their own grants.
   - **The row is the whole test.** The guard must not be rewritten as "the subject is a minor": the
     resolver contains no age branch. It contains an `OLDER(n)` **operand**, which is a set a grant has
     to name before anything is looked at, and the difference is the point: **nothing consults a birth
     date unless somebody wrote a rule that needed it**, and no rule is inferred — and
     [D-070](../decisions/round-05.md#d-070--an-event-has-no-age-ceiling-the-grant-is-the-rule) and
     [D-077](../decisions/round-06.md#d-077--messaging-is-direct-by-default-broadcast-is-an-ordinary-scoped-permission-and-the-recipient-chooses-the-channel)
     keep it that way.

3. **Allow — does any live grant apply?** Two shapes, both boolean, neither ranked against the other:
   - **a unit grant** of this code, to this person directly or to an audience whose expression
     contains them on `at`. It reaches this item because a unit grant reaches every item (§2) —
     **there is no tier to walk and no relation on the item to test.**
   - **an item grant** of this code on exactly this item, to a person or an audience — `event.view`
     on event 1204 is how a helper sees one event and no other.

   Either → **yes**.
4. **Otherwise → no.**

**Steps 1–3 are not a precedence.** With a boolean answer, two allows that both apply produce one
answer, so there is nothing to order and **renumbering steps 1–3 changes nothing about who can do
what.** Their order stands for two reasons that are not precedence — cheap checks before expensive
ones, and step 2's "says nothing" fall-through — and neither order is load-bearing for the answer.
What is ordered, and must stay so, is step 0: the deny is asked first and can defeat every allow below
it ([D-032](../decisions/round-02-03.md#d-032--deny-is-absolute-locality-orders-allows-only)).

Points worth stressing:

- **Default deny.** Step 4. Any new resource starts with nobody able to touch it.
- **Fail closed, in every direction — and *closed* is a direction here, not a safe place to stand.** An
  operand that does not resolve is the empty set; an expression that cannot be evaluated reaches
  nobody; a scope type nobody registered grants nothing. This is the same posture as step 4 and step 0,
  and it is the direction every uncertainty in this model resolves in. *Why:* an empty set *narrows* an
  allow and **widens** a deny, so fail-closed arithmetic is what the expression says, not what safety
  wants — which is why the answer to a failing operand is a report and not a refusal
  ([D-106](../decisions/round-11-12.md#d-106--a-failed-operand-stays-the-empty-set-the-missing-half-was-a-report-not-a-refusal)).
- **A grant may name an audience instead of a person.** The grantee is resolved by the expression in
  §6.2; the scope and the code are resolved exactly as for a personal grant.
- **Effective permissions are never stored.** They are computed per request. A stored permission
  snapshot *will* drift from the grants that produced it — the only question is how long before anyone
  notices. There is a second reason to keep that question open: the snapshot is also the only artefact
  that could ever answer *who could read this in 2023*, since set membership is recomputed from state
  that keeps moving and the audit payload that recorded the change expires (§6.2,
  [F-7](../open-questions.md#f-7--dissolved--a-nightly-rebuild-of-cached-answers-and-a-materialized-effective-permission-table-are-one-job)).
- **Time is a parameter.** `at` defaults to now, but the resolver accepts a historical time. This
  enables "could this person have done this on that date?" — needed for auditing past actions, and
  free if built in from the start. The dated rows behind `MEMBERS`, `GROUP(x)`, `ROLE(x)` and the
  attendance selectors are all periods (§4, §6.2), so the recomputation has something honest to read.

### 6.1 `MEMBERS` — the membership test, moved into the expression

Whether a person's membership counts is **a selector term**, not a clause of the resolver. `MEMBERS`
is evaluated live on the checked date like any other operand, and writing it or leaving it out is the
grant writer's act (§6.2). The resolver has no membership branch and carries no exemption for one.

The four things a writer needs to be able to say:

| To | Write |
|---|---|
| gate an office on a current membership | `MEMBERS * ROLE(x)` |
| leave a whole office ungated | `ROLE(x)` — the same expression without `MEMBERS` |
| waive it for one named person inside a gated rule | `MEMBERS * ROLE(x) + PERSON(y)` |
| apply it to nobody: ownership, guardianship, and any grant aimed at a person | nothing — a channel has no expression, and a personal grant has none (§5) |

The third row is also writable without a selector: "and also him" is a second grant aimed at that
person, which is how the waiver looks when the writer would rather not touch the expression everyone
else reads.

**The test is opt-in per grant, and the failure mode must be named rather than buried.** A grant
written as `ROLE(treasurers)` with no `MEMBERS` authorizes a lapsed member, **silently, forever**.
Nothing errors, nothing reports itself when it happens, and nothing about the grant looks wrong — a
lapsed treasurer is still a treasurer. Three controls, **none of which is the resolver**:

1. **A standing report** of live grants naming a `ROLE(...)` operand whose expression does not contain
   `MEMBERS`. An office held by a non-member is the case worth a human eye, and the report is narrow
   enough to actually be read.
2. **Seeded grants and any grant template carry `MEMBERS`**, so the path of least repetition is the
   safe path.
3. **Import completeness.** `MEMBERS * COUNSELORS` is only as correct as the counselor roster: an
   import that misses 300 counselors silently un-gates them. It fails closed — nothing breaks, which is
   exactly why nobody notices. The import reconciliation report of
   [D-090](../decisions/round-07-08.md#d-090--the-legacy-corpus-is-thousands-of-roster-rows-with-numbers-and-no-money)
   must count people marked as counselors in the corpus against `role_holder` rows written.

**Who the test should spare is a decision the organization has already made,** and it decides the
default: *"everything except guardianship and adult volunteers."* A volunteer whose own fee is unpaid
still runs the Thursday meeting, and losing the roster on the night the fee lapses is the failure to
prevent. So leaving `MEMBERS` out is the **normal** shape of a grant to a contractor, a photographer
or a parent helper, not an exemption somebody must be granted. The line that judgment draws holds, and
it holds hardest where only a report stands behind it: **the report is how the organization notices;
the resolver is not how it punishes.**

*Why the test sits in the expression.* A resolver clause applies to everything or nothing, and so has
to carry its own exemptions; an expression says which grants are gated, in the text of the grant,
where the person writing it can see it and a report can read it. A clause cannot answer *"is this
particular permission meant to require membership?"*, because it records the answer nowhere. **Nothing
enforces `MEMBERS` being present: a convention, not a guard**
([D-081](../decisions/round-06.md#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now)).

Who is gated:

| Channel | Gated? | Why, and how it is written |
|---|---|---|
| Ownership (step 1) | **No** | Otherwise a lapse locks a person out of the screen they renew on. Not expressible in an expression at all |
| Guardianship (step 2) | **No** | A legal relationship, not a membership |
| Grants (step 3) | **Only if the expression says so** | `MEMBERS * …`. A grant to a contractor, a photographer or a parent helper who was never a member is written without `MEMBERS` |
| A deny (step 0) | **Never, in either direction** | §7.1 |

### 6.2 Audiences — an expression over named sets

A grant aimed at a set of people names **an expression over named sets** — `MEMBERS * ROLE(treasurers)`,
`EVERYONE - GROUP(x)`, `PERSON(a) + PERSON(b)` — stored as a tree of binary nodes, evaluated live on the
checked date, and never materialized. The language and its operators, precedence and canonical rendering,
the thirteen seeded selectors and the argument each takes, the rules that make the tree safe (cycles, the
three states, keyless leaves, the editor's preview), and what a grant's reach is recorded in are a
self-contained subject and live on their own page:
**[06a-audiences-and-selectors.md](06a-audiences-and-selectors.md)**. What the resolver does with an
audience is §6 above; what a grant is, and how allow and deny interact, is §5 and §7.

---

## 7. Precedence

### 7.1 Who decides — deny is absolute

```
1. Deny          (a live deny applies at ANY scope)   ← WINS OVER EVERYTHING
2. Ownership     (it's your own row)
3. Guardianship  (the act is about someone else — allows only)
4. Any live allow (unit grant or item grant — §6 step 3)
5. Deny          (nothing matched)
```

**A deny is checked before anything else and is never subject to any ordering.** A deny at the unit
blocks access to one event even if a grant on that event explicitly allows it. There is no scope
local enough to override a suspension
([D-013](../decisions/round-01a.md#d-013--explicit-deny-revoked-is-checked-before-everything);
[D-032](../decisions/round-02-03.md#d-032--deny-is-absolute-locality-orders-allows-only)'s first half,
which is the whole of its surviving content).

**A deny is also never subject to the membership test, in either direction.** A deny blocks someone
who is not a member, which is obvious. What is worth stating: a deny **to an audience** blocks the
people in that audience whether or not they are current members, because the deny is evaluated against
who the expression matches, not against whether they are paid up. Suspensions are absolute; `MEMBERS`
is a condition on a *grant of authority*, and there is no authority here to condition.

**A deny is legal at the unit as well as on an item**, and "exclude her from what the unit grants
everyone" is the case only a deny can serve (§5).

**Nothing else orders.** Two allows that both apply produce one answer, so there is no tie-break, no
tier ladder, and no "is this amount high enough" question anywhere in the resolver: a grant says
yes-or-no about one code. So a grant on an item applies at full force whatever the person holds at the
unit, a unit grant keeps working for the unit's other items, and **no grant can retract another — only
a deny can**
([D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)).

---

## 8. There is no permission cache, and what replaces it

**There is no permission cache.** A check resolves; a request memoizes; the only thing cached across
requests is a compilation. Nothing in this system stores a permission answer, and no part of `can()` is
written to a table
([D-114](../decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation)).

**What a check costs.** One indexed read fetches the checked person's live grant rows — a few dozen rows
at the size
[D-112](../decisions/round-13.md#d-112--the-systems-scale-is-stated-hundreds-of-people-tens-of-registrants-per-event)
states — and each candidate grant's expression is evaluated against a handful of indexed point lookups
in `membership`, `role_holder`, `person_group_member`, `event_registration` and the guardianship rows.
**The arithmetic is not the problem; the N+1 across one screen is:** a 50-row list asking four codes per
row is two hundred checks, and two hundred checks doing the same person's grant read two hundred times
is the shape that makes a cache look necessary. The three mechanisms below fix that shape directly.

1. **A compiled expression is cached** — parsed once, operand kinds resolved once, the parameterized
   predicate emitted once, keyed by the expression's root and `ruleset_version`. **It holds no person and
   no item**, because both arrive as parameters, and that is precisely why it survives across everyone in
   the organization while an answer never could: nothing in a compilation depends on whom or where it is
   being asked about.
2. **A request memoizes.** The checked person's grant rows are read once and every code, item and date in
   that request is answered from them in memory; a named operand that recurs in one request
   (`ROLE(leader)`, `GROUP(cubs)`) is resolved once. **Its lifetime is the request, so it has no
   invalidation policy and no staleness window — there is nothing to invalidate.**
3. **The bulk screens batch.** `can_many(person, codes[], item?)` answers a screen's affordances from one
   resolution; `which_of(people[], code, item)` answers a list's from one pass. The per-item preview
   ([06a §6.2](06a-audiences-and-selectors.md), F-15) and the permissions tab (D-109) are written against these, not against a loop of single
   checks.

**The one thing cached across requests besides a compilation is a named roster**: `ROLE(x)` over
`role_holder`, `GROUP(x)` over `person_group_member`, keyed by `x`. Two conditions, and together they are
the whole of the exception. **The key is the thing a write touches**, so invalidation is local to the row
that changed and never global — the property an answer cache could never have, because an answer's key
names a person and the write that changes it usually names nobody. And the cache holds **the dated rows,
or the set with its validity ranges**, never the set as of today, so the checked date is still applied at
check time and a period ending at midnight needs no job to be seen. A roster is also something a person
maintains and can point at; an answer never was. **The exception is exactly two selectors wide.**
`MEMBERS` is not a roster — nobody writes its rows, and the 1 January sweep rewrites the `membership`
dates it reads for everybody at once. `ORGANIZERS` is not one either: it has holder rows, but it is bound
to an item
([D-102](../decisions/round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)),
so a cache keyed by it would be a stored answer to "who was at this event", which is the set D-102
declined to make permanent.

**What may never be stored again is invariant 19** (§11 of
[data-model/05-authorization.md](../data-model/05-authorization.md#11-invariants-to-verify)): **no row,
table or field may map a person — or a person and a code, or a person and an item — to a permission
answer.** Its enforcement is structural, which is the best kind this corpus has: **the schema has
nowhere to put one.** The residue is named rather than glossed — an implementer who wants a cache back is
stopped by this page and by review, not by a constraint, so for them it is **a convention, not a guard**
([D-081](../decisions/round-06.md#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now)),
and [D-114](../decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation)
lists the three things a returning cache must carry: a per-person invalidation handle next to the global
one, an explicit statement of which tables it watches, and that statement **derived from the operand
registry rather than from a list of ideas.**

**What live resolution buys.**

- **"The safeguarding case is immediate" is true by construction.** A revoke, a deny, a closed period, an
  ended guardianship, a `membership.terminate` ⛔ — `safeguarding_officer`, the most safeguarding-shaped write in the catalog — or a cancelled registration — all visible on the **next
  check**, with no job in between and no list to remember to include them in. A terminated member stops
  satisfying `MEMBERS` at the instant the row closes: [data-model/03-membership.md §6](../data-model/03-membership.md)
  asks for exactly that, and asks it of nothing, because `MEMBERS` reads `membership` live (§6.1).
- **The calendar cannot drift an answer.** A birthday crossing `OLDER(n)`, a period reaching its own
  `valid_to`, the 1 January sweep — each moves the answer **at the instant it happens**.
  [D-107](../decisions/round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)'s
  ruling stands — *"IT IS FINE"* — and needs no mechanism to hold it.
- **`ruleset_version` is bumped by a write to `audience_operand` or `selector_type` only.** A compilation
  depends on an expression's shape and the seeded vocabulary and on nothing else. `access_grant` is not in
  that set because **grants are not compiled**: a check reads the person's live grant rows, so a new,
  edited or revoked grant changes what that read returns and leaves nothing stale to drop; the
  `deprecated | hidden | disabled` flag is not in it because a state is **not compiled in** — resolution
  reads it live, once per request, memoized, which is also why `disabled` still means *now* (D-109);
  `role_holder`, `person_group_member`, `guardianship_permission` and a person merge are not in it because
  they move rosters and rows that are read live or invalidated locally. **Concretely: adding a child to a
  group drops nothing.**
- **"Whom does this change reach?" is answerable.** A compilation is finite and enumerable over the
  audience tree, so *"an edit to a shared audience invalidates everything"* becomes *"it invalidates the
  compilations that embed it"* — a bounded walk over rows that already exist. **One qualification, stated
  in the direction and not the spirit:** it is *not* the walk the save path performs for cycles, which runs
  forward from the tree being saved. Invalidation needs the **reverse** direction, the one the
  delete-refusal check already runs. **Same forest, same rows, opposite way** — and the cost of listing
  that forest is registered as unverified at any size in `data-model/05` §13, so what is claimed here is
  **bounded**, not **cheap**
  ([D-103](../decisions/round-10b.md#d-103--an-audience-may-name-another-audience)).

**A compiled form is bound to its item.** Since a bound operand means the *same* expression yields
different people on different items, **a compiled form computed while checking one item may never be
served for another**: the item is a parameter of a predicate, and a predicate bound to event 1204 is not
the predicate for event 1205 (F-6).

**What is given up.** Nothing pre-pays the expensive screens. The per-item preview, the permissions tab
and the "who holds this" listing do their work when somebody opens them, which is affordable at the
stated size — **but D-109's ruling has no fallback, and that is a dependency, not a comfort.** At
[D-112](../decisions/round-13.md#d-112--the-systems-scale-is-stated-hundreds-of-people-tens-of-registrants-per-event)'s
trigger the reopen answer is named rather than vague: materialize `effective_permission` per person, **and
call it that** — a real materialization with a per-person invalidation handle and a stated staleness
window.

**What is not given up** is the rule stated in [06a §6.2](06a-audiences-and-selectors.md), and it is the whole cost model of this page: **inside a
check, an expression is compiled to a predicate on the person being asked, never materialized as a set.**
No job anywhere is permitted to do the opposite.

## 9. Delegation

A leader going on leave, a treasurer handing over during an audit — the common need to lend authority
temporarily.

A delegation is an **ordinary grant** with its provenance set: `is_delegated`, `delegated_from` naming
the person whose authority is being lent, `grant_reason`, and a `valid_to`. Because a grant is **one
permission code**, "do not lend more than you hold" is a set-membership test
([D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)).

Rules:

- **A delegation always has an end date.** Enforced on the write path.
- **A delegation cannot exceed the delegator's own authority** — validate at grant time that the code
  being delegated is one the delegator currently resolves to, and re-check at use time, because the
  delegator may lose it mid-delegation.
- **The provenance is recorded**, so an audit can answer "who really had this authority on that date?"
  — it lists both the holder and the delegator.
- **A deny cannot be lent and cannot be lent around.** A delegation is an allow; the delegatee's
  answer is computed from their own rows plus the lent one, and their own denies still apply.
- **Delegation of `system.admin` is prohibited outright.**

**Lending is said on the grant, not on the role:** `role` has no `is_delegatable` column, and nothing
about an office says whether its authority may be lent.

*Assumption:* D-100 names `is_delegatable` in neither its deleted nor its kept list of `role`'s columns.
Recorded in [../open-questions.md](../open-questions.md); the open list carries it as item 55.

---

## 10. Anti-patterns this design rejects

Stated explicitly, because each is a common and expensive mistake:

| Rejected | Why | Instead |
|----------|-----|---------|
| `person.is_admin` boolean | Cannot scope, cannot date, cannot audit, cannot delegate | A grant at the unit, aimed at a role |
| Role on `person` (`person.role = 'leader'`) | One role per person, no history | `role_holder`, many per person |
| Checking membership type in code (`if type == 'adult'`) | Rules change; the check is invisible and untestable | A permission, granted deliberately. There is one membership type now, so this is doubly wrong |
| **Deriving access from holding a role or being in a group** | Being something is not being able to do something (D-005), and a role confers nothing by itself | A live grant whose audience names `ROLE(x)` or `GROUP(x)` — §4 |
| **A grant written as `ROLE(x)` when it meant `MEMBERS * ROLE(x)`** | It is a term the writer must type, and forgetting it silently authorizes a lapsed member | The standing report of role grants without `MEMBERS`, seeded grants that carry it, and the import count — §6.1 |
| **An `access_level`, or any comparison of "how much" a grant gives** | A level is a bundle of permissions under one word, and it re-imports the rank rule and a tie-break that have no consumers | Roles and audiences as the bundle — what D-068 already said — and one row per code when you need it in writing. §3, D-099 |
| **`-` in an expression used instead of a deny** | Subtracting narrows one grant's reach; it cannot say "whatever else she is given" | A deny, which defeats every grant — §5, §7.1 |
| **An expression whose reach nobody saw** | `EVERYONE` is a legal operand, and a bound operand means different people on different items | The editor expands the set **for an item** at the moment of granting — [06a §6.2](06a-audiences-and-selectors.md) |
| `PRESENT(e)` over `was_present` | `NULL` until someone takes a register: a volunteer's forgotten tick would revoke a child's own photos | The four attendance tiers, and presence stays a safeguarding signal — [06a §Event sets](06a-audiences-and-selectors.md#event-sets-and-the-two-sets-that-are-refused) |
| **A `GUARDIANS` operand** | Guardianship is a channel with its own `right_level` over a child, reaching every action about that child; an operand would offer a subset of what they hold | The guardianship channel (§1, §6 step 2); for a kept list of contact adults, a `person_group` — D-113 |
| **A `LIST` operand, or a table of an audience's own names** | A hand-written set is not a different kind of thing from a named one | `PERSON(a) + PERSON(b)` inside the expression — §Grammar, D-105 |
| **Downward inheritance of authority through a unit tree, and `scope_exposure` rows** | Both need a hierarchy, and there is one unit | A grant at the unit, which reaches every item — §2, D-097 |
| **"Most specific scope always wins", including against a deny** | Only allows could ever be ordered, and allows are not ordered | Deny absolute, and no ordering at all — §7, D-099 |
| **A bulk "expose this body's scope" tool** | There is one unit and nothing to expose | One grant at the unit, or one grant aimed at `EVERYONE` / `MEMBERS` — §2, D-045 |
| **Treating an organization-scoped role as universal "so the registrar can work"** | Everything is unit data; there is no second side of that distinction | If a permission is missing, add the permission — §2.1 |
| Role → permission mapping hardcoded in the app | Cannot be reviewed by the organization, cannot change without deployment | Grant rows naming `ROLE(x)` — readable, and the answer to "what may a treasurer do?" |
| Deriving access from guardianship without a right | Authorization by identity is unauditable and unsafe | The explicit right level on the `guardianship` row, compared against `right_kind` |
| Deleting a grant to revoke it | Loses the record of what was revoked when | `valid_to`, and a `deny` when the *fact* of the restriction matters |
| A live deny that matches no allow | A deny that denies nothing is how a stale restriction survives its reason | The dead-weight-deny report — §5 |
| Two authorization implementations | They diverge; the weaker one becomes the exploit | One resolver, §6 |
| Unit leader sees all member data by default | Fails safeguarding review | Scoped grants, resolved per operation — and §2 on the protection that is not in the model |

---

## 11. Open issues

- **Which grants are meant to carry `MEMBERS`?** Nothing enforces it (§6.1), and the tab that lists the
  answer is decided while its threshold is not — *every* `ROLE(...)` operand without `MEMBERS`, or only
  the offices marked sensitive? It lands in the tab's `Unusual` section either way, so what is still
  undecided is only how wide that section is
  ([F-13](../open-questions.md#f-13--closed--a-rule-that-resolves-correctly-but-looks-odd-is-listed-as-unusual-never-as-broken),
  [F-21](../open-questions.md#f-21--closed--no-report-a-tab-on-the-permissions-page-and-unbounded-cost-is-accepted-at-the-stated-size)).
- **The holder period.** Nothing forces a `role_holder` row to end, and the report stands alone (§4,
  [D-071](../decisions/round-05.md#d-071--nothing-forces-a-role-assignment-to-end-the-gate-and-the-report-are-the-control)).
- **Who may compose an expression?** `audience.manage` covers creating and editing a set, and the
  catalog is silent on the edit that puts `EVERYONE` into a grant's audience
  ([appendix/permission-catalog.md §12](../appendix/permission-catalog.md#12-open-issues)). No new code
  was invented for this — the gap is the finding.
- **What reopens the settled answers on this page.** Two named conditions, both carried so nobody has to
  rediscover them: a materialized `effective_permission` table becomes worth building at
  [D-112](../decisions/round-13.md#d-112--the-systems-scale-is-stated-hundreds-of-people-tens-of-registrants-per-event)'s
  size trigger, and then only as a performance structure with a per-person invalidation handle and a
  stated staleness window — never as a record of whom a rule reached (§8); and a historical check is
  answered by the same evaluator running over history as it is written, which is not a promise for the
  operands whose set is a current fact
  ([06a](06a-audiences-and-selectors.md#what-a-grants-reach-is-recorded-in),
  [F-7](../open-questions.md#f-7--dissolved--a-nightly-rebuild-of-cached-answers-and-a-materialized-effective-permission-table-are-one-job),
  [F-17](../open-questions.md#f-17--closed--the-expression-is-the-record-so-a-nested-audiences-past-is-recomputed-and-never-promised)).

All tracked in [../open-questions.md](../open-questions.md).

---

*Decisions behind this page: D-005, D-011, D-013, D-019, D-031, D-032, D-042, D-045, D-052, D-053, D-068, D-069, D-070, D-071, D-074, D-077, D-079, D-080, D-081, D-083, D-086, D-088, D-090, D-097, D-098, D-099, D-100, D-102, D-103, D-105, D-106, D-107, D-109, D-112, D-113, D-114.*
