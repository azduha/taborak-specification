# Authorization Model

The permission system end to end. This is the document to read if you read only one.

**Round 10 rewrote this page.**
[D-097](../decisions/decision-log.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)
deleted the unit hierarchy,
[D-099](../decisions/decision-log.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)
the level ladder,
[D-100](../decisions/decision-log.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)
the membership gate and positions,
[D-101](../decisions/decision-log.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree)
the audience's rule/list/inclusion arms, and
[D-102](../decisions/decision-log.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)
event ownership. What is left is smaller than what was there, and every claim that died with them is
marked where it used to be read, because *why it existed* is the part that stops coming back.

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

- Channel 2 has a **legal** character — guardianship is a fact about the world, often court-ordered,
  and the organization records what it was told rather than deciding it. **It does not expire by
  itself.** An earlier version of this bullet said it "expires when a child reaches majority", which
  is exactly the claim
  [D-069](../decisions/decision-log.md#d-069--guardianship-ends-when-a-person-ends-it-the-system-takes-no-position-on-majority)
  withdrew, together with the review queue that asserted it more quietly: a parent's authority over
  health and school records does not end at 18 in many jurisdictions, and in some it ends at a
  different age, so any date the system computed would be a claim it cannot support. A guardianship
  ends when a **party to it** says so, and nobody else — not a job, not a birthday.
- Channel 1 is the only channel that can name **a set** rather than a person
  ([D-042](../decisions/decision-log.md#d-042--grants-may-target-audiences-not-only-individuals)).
  A guardianship is between two named people and an owner is one person. **That is a boundary, not an
  oversight** — it is why an office can be *aimed at* but never *held by* a rule (§4,
  [F-12](../open-questions.md#f-12--closed--may-a-role-be-held-by-a-rule-as-an-audience-is)).
- A deny lives in channel 1 and defeats all three (§7.1). Nowhere else can one be written, and
  nowhere else can one be argued with.

### Roles and groups are not channels

This is the section that used to list four channels, the fourth being **role assignment**, and a
fifth thing — the **membership gate** — being described as "a condition on channels 1 and 3". Both
are gone, for the same reason and a different one.

~~**Role assignment** — what may this person do in the organization? A `role_assignment` joined a
person to a role for a period within a scope, and the role carried the permissions.~~ **Withdrawn
by [D-100](../decisions/decision-log.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape).**
`role_assignment` is now `role_holder`, `role_permission` is deleted, and **a role confers nothing by
itself**. The codes an office carries are the live grants whose audience names `ROLE(x)`. A role is
therefore not a source of authority; it is a **set that grants point at**, in the same sentence as a
group, an event's attendees, and "everyone". Authority still has exactly one source besides ownership
and guardianship, which is
[D-005](../decisions/decision-log.md#d-005--permissions-are-grants-never-derived-from-identity) said
one level down: **being something is not being able to do something.**

~~**The membership gate** — whether a channel applies at all can depend on whether the person is
currently a paid-up member
([D-039](../decisions/decision-log.md#d-039--member-permissions-require-a-current-paid-membership));
channels 2 and 4 were exempt.~~ **Withdrawn by D-100.** The test did not disappear, it **moved into
the expression**: `MEMBERS` is a selector evaluated live on the checked date, and writing it or
leaving it out is now the writer's act rather than the resolver's (§6.1). It is not a channel because
it never granted anything, and it is no longer a clause in the resolver either.

**What did survive as a channel is worth naming, because both were nearly caught in the sweep.**
Ownership and guardianship are unaffected by D-097 through D-102 — neither was ever scoped to a unit,
gated on membership, or graded by a level.

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
consults.

**Which codes may be granted where is data, not prose.** `permission.applies_to` is `unit` or
`unit_and_item`
([D-099](../decisions/decision-log.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)):
`event.create` and `membership.manage` are nonsense *on* an event, and the column says so instead of
hoping a reader agrees. It is checked **when the grant is saved**, not at check time — a grant of
`event.create` written on one event is refused with the reason in the error, because an event cannot
be created twice and a creation permission attached to a thing that already exists answers no
question. The `system` namespace is unit-only for the same reason, which is **who enforces now** for
the old rule that `system.admin` can never arrive through an item grant
([D-081](../decisions/decision-log.md#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now)).

### 2.1 The founding rule, and what is left of it

**This section states a rule that shaped this page for eight rounds and no longer holds.** It is kept
because the reasoning is the expensive part, and because someone will propose the simplification
that reverses it again.

~~**Authority over a unit originates at that unit. It cannot be claimed from outside it.** A parent
unit — including the organization itself — cannot decide permissions inside a sub-unit. The root does
not reach down into a pack; a pack does not reach down into the groups under it. If a sub-unit wants
a higher-level role to have authority over it, the sub-unit must state so explicitly. Nothing is
inherited, nothing is assumed, and there is no configuration flag that enables inheritance.~~

**Withdrawn by
[D-097](../decisions/decision-log.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row),
which did not weaken the rule so much as deprive it of its subject**
([D-031](../decisions/decision-log.md#d-031--no-downward-inheritance-of-authority-scopeexposure-is-the-only-crossing)).
The rule existed to stop the center deciding permissions inside a body it does not run. **With one
unit there is no "outside it" to be stopped from.** Every permission is held at the unit or on an
item, and the unit's people are the only people there are.

It is worth keeping *why it looked right*, because the argument was good:

- **It was a safeguarding property.** Access to a body's children had to be granted *by that body* —
  by the people who know them, who recruited the leader, and who can be asked. **This property is
  gone and nothing in the remaining model reproduces it.** A permission held at the unit reaches
  every member, and `person.view` was already the widest read permission in the system
  ([D-083](../decisions/decision-log.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data),
  [D-086](../decisions/decision-log.md#d-086--a-sensitivity-mark-grades-what-a-grant-exposes-not-the-table-it-reads)).
  What is left of the safeguarding story is a permission held by a named adult, an audit trail whose
  payloads expire after two years
  ([D-088](../decisions/decision-log.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)),
  and a report of who holds the write — **minus the part where the named adult was somebody the body
  chose.** Saying this once, plainly, is the honest version of a deletion.
- **It made every grant attributable to a locus of accountability.** "Who gave this person access to
  this pack?" used to have the answer "a specific person at a specific pack, on a specific date".
  Now it has the answer "a specific person at the unit, on a specific date" — still a name, no longer
  a *nearby* name.
- **It prevented silent blast-radius growth.** Restructuring used to be the risk; with one unit there
  is nothing to restructure, so the property survives for the dull reason that its threat has no
  subject.
- **It matched how the organization actually delegates** — up, not down. That observation was about
  *bodies*, and there are none. What replaces the need it served is the audience: "tell everyone
  about this event" was always the real requirement behind the delegation machinery
  ([D-045](../decisions/decision-log.md#d-045--the-bulk-scope-exposure-tool-is-removed)), and it is
  one grant aimed at `EVERYONE` or `MEMBERS` (§6.2).

**What died with it — all of it by D-097, listed so a reader can tell whether a page they are holding
is stale:** `org_unit` and its types, names, relationships and participations; `scope_exposure` and
the `scope.expose` and `scope.exposure.review` permissions; the direction-of-authority check and the
nightly alert that was its only detector; `unit_ancestors()` and `unit_descendants()` and every
ancestor walk. **Who enforces the direction of authority now: nobody, because there is no direction.**
Not "the application instead of the database" — the question cannot be asked
([D-081](../decisions/decision-log.md#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now)).

### 2.2 The questions people actually ask, before and now

| Question | What this page used to answer | What it answers now |
|---|---|---|
| May the unit's treasurer act on a group's finances? | Only if that body exposed its scope | A unit grant reaches every group. Nothing to ask, nothing to write |
| May `registrar` read a person record? | Yes, because the registry lives at the root | Yes, because it is a unit grant. Same answer, one fewer step of reasoning |
| May a helper see one event? | A per-item grant at `view` | A grant of `event.view` on that event. The same row, minus the level |
| May the center read what happens inside a body? | No — exposure was the only crossing (D-049) | There are no bodies. The question is now "may this person see these people?", which is a `person.view` grant with a name on it |
| Who owns an event? | Exactly one unit (D-058) | **Nobody.** `event.org_unit_id` is deleted; the people connected to an event are named by selectors that bind to it (§6.2) — [D-102](../decisions/decision-log.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it) |
| Who was in the Thursday group in 2011? | A point-in-time read over a unit roster | A point-in-time read over `person_group_member` — dated rows, same answer ([D-098](../decisions/decision-log.md#d-098--a-group-is-a-persongroup-explicit-members-a-lifetime-and-no-authority)) |

### 2.3 `system.admin`

`system.admin` is the one wildcard permission: a check for `X.y` is satisfied by an exact grant of
`X.y` or by `system.admin` and nothing else
([D-068](../decisions/decision-log.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle)).
It used to be described as "the sole exception to the no-downward-inheritance rule", and that framing
went with the rule — there is no boundary for it to cross.

Two properties keep a wildcard from being the hole in the design, and both stand on their own:

1. **Its holders are alarmed on.** The report listing current holders must notify on every change — a
   new holder is either a planned act or an incident, and either way someone should know within the
   hour.
2. **It is not delegatable** (§9), and it is `applies_to = unit`, so it cannot arrive on an item.

> If `system.admin` becomes the mechanism by which ordinary organization-wide work is done, that is a
> signal about the catalog rather than about a boundary rule: the work is telling you it needs a
> permission that does not exist. Record it in
> [../decisions/decision-log.md](../decisions/decision-log.md) instead of working around it.

---

## 3. Permissions — the atomic unit

A permission is a coded capability. It is the only thing the check function ever looks at.

A permission row carries its `code`, the `resource` and `action` it decomposes into, a
`description`, `is_system` — set for the codes the platform ships with, which therefore cannot be
deleted — and the two columns D-099 added: **`applies_to`** (`unit` or `unit_and_item`, above) and
**`right_kind`** (`read` or `write`). `right_kind` exists for exactly one customer: guardianship
(§1, channel 2) grades a guardian at `none` / `view` / `write`, and with the ladder gone that channel
had nothing left to compare a permission against. `none` covers nothing, `view` covers `read` codes,
`write` covers both. **It is a column whose only job is one other mechanism, and saying so is cheaper
than discovering it later**
([D-074](../decisions/decision-log.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular)).

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
([D-074](../decisions/decision-log.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular)).
A guardian's act is checked under the ordinary code for the thing being touched — `person.view`,
`person.contact.edit` — and reaches the guardianship channel by the shape of the request, not by its
name ([D-079](../decisions/decision-log.md#d-079--the-guardianship-channel-is-entered-by-shape-not-by-permission-name)).

**Every capability is narrow and explicit.** A check for `X.y` needs an exact grant of `X.y`, or
`system.admin`. There is no `<resource>.admin` wildcard and no prefix match in the resolver
([D-068](../decisions/decision-log.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle))
— which is what makes the next section load-bearing rather than decorative: **if somebody can do
everything about events, that is a dozen grant rows naming a role, and you can read them.**

### 3.1 The level ladder, withdrawn

~~Each grant carried an `access_level` — `revoked` 0, `view` 10, `contribute` 20, `manage` 30, `admin`
40 — ordered and cumulative, a higher level always subsuming the lower ones, and `permission_level`
said which level satisfied which permission at which scope.~~ **Deleted by
[D-099](../decisions/decision-log.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality).**

| It was | Why it goes |
|---|---|
| `access_level` | A level is a **bundle of permissions identified by one word**. D-068 already refused that idea once, when it deleted `<resource>.admin` and said *roles are the bundle*. This finishes the same thought: **roles and audiences are the bundle, and nothing else is** |
| `permission_level` | Its two jobs moved to `applies_to` and `right_kind`, both on `permission` itself |
| The rank integer ([D-012](../decisions/decision-log.md#d-012--status-strings-compare-by-rank-never-lexicographically)) | There is no ordering left to compare. The famous bug it guarded — `'admin' < 'contribute'` comparing alphabetically and inverting the model — cannot occur in a system with no levels, which is a better fix than the guard |
| `revoked` as a level | Survives as an **effect on a grant row**, checked first, unchanged in substance (§7.1) |

The cost, in rows: an office that used to be one grant at `manage` is now one row per code. The
catalog holds 66 codes, and a broad office is a couple of dozen rows. That is the price of the
question this makes answerable — *"what exactly does this person have?"*, answered by reading rows —
and the price of the one that is no longer askable, which is *"what does `manage` give me on this
event?"*: there is no such word, so there is no such lookup.

---

## 4. Roles are offices; groups are company

Two tables of the same shape, and the difference between them decides **who may edit the
membership**.

| | **Role** (`role`, `role_holder`) | **Group** (`person_group`, `person_group_member`) |
|---|---|---|
| What it is | An **office**: leader, finance, IT. Small, visible holders, expected to be seen | **Company**: the Thursday group, the kitchen crew, this year's camp staff. People who do something together |
| Holder row | `role_holder`(role, person, `valid_from`, `valid_to`, `granted_by`, `note`) | `person_group_member`(group, person, `valid_from`, `valid_to`, `added_by`, `note`) |
| Held where | **At the unit, always.** D-097 left one scope, so there is nothing else to hold it at | The group is its own item, and a grant can be written on it |
| Permission that writes its membership | `role.assign`, `role.unassign` — **🔒🔒, the most sensitive family in the catalog** | `person_group.member.manage` — ⚠ |
| In an expression | `ROLE(x)`, or bare `x` | `GROUP(x)`, or bare `x` |
| Authority by being in it | **None** | **None** |

**Why two tables when they are technically the same shape** — and they *are* the same shape, which is
exactly what
[D-080](../decisions/decision-log.md#d-080--five-contradictions-the-translation-surfaced-and-how-each-was-resolved)
teaches a reader to distrust. The answer is the permission consequence: **one table would merge those
two codes into one.** A single membership table with a `kind` column gives you a single permission
that both adds a child to the Thursday group *and* puts the holder into `SYSTEM_ADMINS`. That is the
merge to refuse. Same columns, **different codes**, and `ROLE(x)` / `GROUP(x)` distinct in the grant
text so the distinction is visible to whoever reads the grant.

**A role confers nothing.** `role_permission` is deleted, and the codes an office carries are **the
live grants whose audience names `ROLE(x)`**. That is what makes *"what may a treasurer do?"* a
question with an answer: it is a query over visible grant rows, not a walk through a bundle table
nobody reads. What "the treasurer's permissions" consists of now:

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
[D-005](../decisions/decision-log.md#d-005--permissions-are-grants-never-derived-from-identity) and
[D-019](../decisions/decision-log.md#d-019--household-membership-grants-no-access) restated one level
down: **participation is not authority**, and storing the participation in a tidier table does not
quietly promote it. A group additionally has no parent and no children, no type vocabulary, no code,
no path, no nesting rules, no rename history, no split or merger edge, no leadership of its own, **no
roles**, and no fee
([D-098](../decisions/decision-log.md#d-098--a-group-is-a-persongroup-explicit-members-a-lifetime-and-no-authority)).

**Both are items.** `person_group` and `role` are registered in `grant_scope_type`, so *"these two may
work this group's roster"* and *"these two may manage the counselors roster"* are grants on one item —
reachable only by someone who already holds the corresponding code at the unit (§2).

**Roles are runtime data, and the seed set is not a specification**
([D-052](../decisions/decision-log.md#d-052--roles-are-runtime-data-the-seed-set-is-not-a-specification),
[D-053](../decisions/decision-log.md#d-053--a-role-is-valid-always-only-its-assignment-is-temporal)):
the organization creates roles, composes them from grants, and deletes the unused ones. The real
definitions live in
[appendix/permission-catalog.md §11](../appendix/permission-catalog.md#11-roles--proposed-seed-set).
One role ships, and ships `is_system` so an editor refuses to delete it: **`counselors`**. A
permanent, organization-wide population is the opposite of the organization's own definition of a
group ("a temporary set of members that do events together"), and the table decides the sensitivity
that protects the set every safeguarding convention hangs from. It is still **only a set** — being in
it confers nothing until a grant names it (§6.2).

### Positions are deleted

~~`position`, `position_assignment`, `is_leadership`, `max_holders`, and the appointment workflows
that created a role assignment alongside a position one.~~ **Deleted by D-100**, along with
[D-033](../decisions/decision-log.md#d-033--multiple-people-may-occupy-the-same-position)'s occupancy
rules. The reason is structural: with no units there is no *body* to be a leader **of**, which is the
only thing a position recorded and a role does not. An elected leader is now a holder of a role, and
the audience rule that used to read `unit_leaders` — which round 6 had to correct because it was
silently matching nobody — is `ROLE(leaders)`, and means what its name says.

**What is genuinely lost** is the *elected-versus-appointed* distinction as stored data. It survives
only as roles the organization invents (`elected_council` next to `appointed_it`) or not at all. Where
the workflows that used to end at a position end now is
[04-organization-structure.md §6](04-organization-structure.md#6-appointments-which-no-longer-end-at-a-position).

**A role is held by exactly one person per row, and that is now settled rather than open.** F-12 asked
whether a role could be held by a rule the way a group is, and refused it: an office record that
cannot answer "who was treasurer in 2023" is not an office record, and a derived holder list cannot
answer that. **[F-12](../open-questions.md#f-12--closed--may-a-role-be-held-by-a-rule-as-an-audience-is) is
closed, and the answer is no** — and the grantee pair F-12 contemplated is no longer even tempting,
because **grants aim at roles instead of roles being filled by grants.**

### The holder period matters

`valid_from` / `valid_to` on `role_holder` means an office ends on a date even if nobody remembers to
revoke it. Leavers are the classic audit failure: the volunteer who stepped down in 2019 still has an
active account with treasurer access in 2026.

**Nothing forces a holder row to end, and the control is the report**
([D-071](../decisions/decision-log.md#d-071--nothing-forces-a-role-assignment-to-end-the-gate-and-the-report-are-the-control),
whose posture transfers from assignments to holder rows unchanged). The old reason to soften that —
that the membership gate would quietly expire dormant authority anyway — went with the gate, so the
report is now carrying more weight than it did (§6.1, §11).

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

### Allow and deny are not symmetrical

**Allowed when some live allow applies and no live deny applies.** Everything else in this document
is elaboration.

**A deny is legal at either scope.** A deny at the unit is precisely the case an expression cannot
serve: *"exclude her from what the unit grants everyone."*

**`-` in an expression is not a deny, and the two are not interchangeable**
([D-099](../decisions/decision-log.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)).
Subtracting a set narrows **one grant's reach**. A deny defeats **every grant** that applies to that
person, including ones written elsewhere, later, or by somebody else. The first cannot express *"she
must not have this, whatever else she is given"*, which is
[D-013](../decisions/decision-log.md#d-013--explicit-deny-revoked-is-checked-before-everything)'s
whole reason for existing: a court-ordered restriction must not be beatable by a broader grant someone
forgot about.

**One report comes with this, and it is the whole hygiene of the thing.** A live deny whose grantee,
scope and code match **no live allow** is dead weight, and it should be reported — a deny that denies
nothing is how a stale restriction survives its reason. Nothing enforces it; the report is the
mechanism.

### Why `scope_type`/`scope_id` and not one column per item type

`scope_id` has no foreign key — it is a polymorphic reference, and this is a deliberate, accepted
trade-off
([D-011](../decisions/decision-log.md#d-011--scopeid-on-accessgrant-is-polymorphic-with-no-foreign-key)):

- **Cost:** no referential integrity. A grant can point at a deleted event.
- **Benefit:** the permission system does not need a schema change every time a new grantable thing
  is invented, which — since documents and everything else are still deferred — will happen
  repeatedly.

Mitigations, all of which are required: the `grant_scope_type` registry validates scope types;
deleting an item of a granted type must close its grants (an application-level obligation, tested); a
nightly job reports orphaned grants; ids are never reused. The heavier alternative — a
`grantable_item` supertable every grantable entity references — was declined for flexibility, and is
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
   ([D-074](../decisions/decision-log.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular)).
   Covered → **yes**. Every other outcome — no row, `none`, a level too low — is **not a refusal**:
   the channel says nothing and the resolver continues, where the person's own grants are tried
   exactly as they always were
   ([D-079](../decisions/decision-log.md#d-079--the-guardianship-channel-is-entered-by-shape-not-by-permission-name)).
   A parent who is also the event registrar holds `view` over their own child and must not be refused
   the roster by their own guardianship.

   - **Nothing escapes by naming.** The act that routes here is chosen by *whose record it touches*,
     so a permission written next year for a field a guardian must edit is covered the day the field
     exists. Under the rule this replaces, dispatch read the code's prefix — and an ordinary
     `person.contact.edit` slipped past it.
   - **An ended guardianship never opens this channel again.** What a former guardian may still do is
     what any other person may do, through their own grants.
   - **The row is the whole test.** The guard must not be rewritten as "the subject is a minor": the
     resolver contains no age branch — since round 12 it contains an `OLDER(n)` **operand**, which is a set a
     grant has to name before anything is looked at, and the difference is the point: **nothing consults a
     birth date unless somebody wrote a rule that needed it**, and no rule is inferred — and
     [D-070](../decisions/decision-log.md#d-070--an-event-has-no-age-ceiling-the-grant-is-the-rule)
     and
     [D-077](../decisions/decision-log.md#d-077--messaging-is-direct-by-default-broadcast-is-an-ordinary-scoped-permission-and-the-recipient-chooses-the-channel)
     keep it that way.

3. **Allow — does any live grant apply?** Two shapes, both boolean, neither ranked against the other:
   - **a unit grant** of this code, to this person directly or to an audience whose expression
     contains them on `at`. It reaches this item because a unit grant reaches every item (§2) —
     **there is no tier to walk and no relation on the item to test.**
   - **an item grant** of this code on exactly this item, to a person or an audience.

   Either → **yes**.
4. **Otherwise → no.**

**The order used to be a rule, and half of it is gone.** ~~Among allows, the most specific scope
determined the effective level, and the first tier that yielded a determination won~~
([D-032](../decisions/decision-log.md#d-032--deny-is-absolute-locality-orders-allows-only)'s second
half, deleted by D-099). With a boolean answer, two allows that both apply produce one answer, so
there is nothing to order and **renumbering steps 1–3 changes nothing about who can do what.** What is
still ordered, and must stay so, is step 0: the deny is asked first and can defeat every allow below
it. Steps 1–3 keep their order for two reasons that are not precedence — cheap checks before expensive
ones, and step 2's "says nothing" fall-through — and neither order is load-bearing for the answer.

Points worth stressing:

- **Default deny.** Step 4. Any new resource starts with nobody able to touch it.
- **Fail closed, in every direction — and *closed* is a direction here, not a safe place to stand.** An
  operand that does not resolve is the empty set; an expression that cannot be evaluated reaches nobody; a
  scope type nobody registered grants nothing. This is the same posture as step 4 and step 0, and it is the
  direction every uncertainty in this model resolves in. **Round 12 kept this rule exactly and refused three
  chances to make it louder** ([D-106](../decisions/decision-log.md#d-106--a-failed-operand-stays-the-empty-set-the-missing-half-was-a-report-not-a-refusal)):
  an empty set *narrows* an allow and **widens** a deny, so fail-closed arithmetic is what the expression
  says, not what safety wants — and the answer chosen was a report, not a refusal.
- **A grant may name an audience instead of a person.** The grantee is resolved by the expression in
  §6.2; the scope and the code are resolved exactly as for a personal grant.
- **Effective permissions are never stored.** They are computed per request. A stored permission
  snapshot *will* drift from the grants that produced it — the only question is how long before
  anyone notices. There is now a second reason to keep that question open: the snapshot is also the
  only artefact that could ever answer *who could read this in 2023*, since set membership is
  recomputed from state that keeps moving and the audit payload that recorded the change expires
  (§6.2, [F-7](../open-questions.md#f-7--dissolved--a-nightly-rebuild-of-cached-answers-and-a-materialized-effective-permission-table-are-one-job)).
- **Time is a parameter.** `at` defaults to now, but the resolver accepts a historical time. This
  enables "could this person have done this on that date?" — needed for auditing past actions, and
  free if built in from the start. It answers *better* than it used to: the dated rows behind
  `MEMBERS`, `GROUP(x)`, `ROLE(x)` and the attendance selectors are all periods (§4, §6.2), so the
  recomputation has something honest to read.

### 6.1 `MEMBERS` — the membership test, moved into the expression

Since round 2 this was **the membership gate**, a clause in the resolver: a role granted nothing while
its holder's membership had lapsed
([D-039](../decisions/decision-log.md#d-039--member-permissions-require-a-current-paid-membership)),
which made the resolver's answer time-sensitive rather than merely scope-sensitive, and needed two
exemptions — `role.requires_membership` for a whole role, and the `system.gate_exempt` permission for
one named person
([D-051](../decisions/decision-log.md#d-051--the-membership-gate-is-waived-by-a-permission-not-only-by-a-role-flag))
— the second of which had to be carefully kept *out* of `can()` and came with a documented lockout
hazard.

**All of it is deleted by
[D-100](../decisions/decision-log.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape):**
the resolver's membership clause, `role.requires_membership`, `system.gate_exempt`,
`person_holds_gate_exempt`. The test is now **a selector term**, and `MEMBERS` is evaluated live on
the checked date like any other operand:

| Old mechanism | New expression |
|---|---|
| The test applied to a role with `requires_membership = true` | `MEMBERS * ROLE(x)` |
| The test waived for a whole role | `ROLE(x)` — write it without `MEMBERS` |
| The test waived for one named person (`system.gate_exempt`) | `MEMBERS * ROLE(x) + PERSON(y)` |
| The test never applied: ownership, guardianship, and every explicit grant | Not written at all — a channel has no expression |

The third row is also writable without a selector, since a grant may be aimed at a person directly
(§5): "and also him" is a second grant, which is how the exemption looks when the writer would rather
not touch the expression everyone else reads.

**The posture reverses, and the new failure mode must be named rather than buried.** The gate was
**default-on**, so forgetting it was impossible. It is now **opt-in per grant**: a grant written as
`ROLE(treasurers)` with no `MEMBERS` authorizes a lapsed member, **silently, forever**. Nothing
errors, nothing reports itself when it happens, and nothing about the grant looks wrong — a lapsed
treasurer is still a treasurer. Three controls, **none of which is the resolver**:

1. **A standing report** of live grants naming a `ROLE(...)` operand whose expression does not
   contain `MEMBERS`. An office held by a non-member is the case worth a human eye, and the report is
   narrow enough to actually be read.
2. **Seeded grants and any grant template carry `MEMBERS`**, so the path of least repetition is the
   safe path.
3. **Import completeness.** `MEMBERS * COUNSELORS` is only as correct as the counselor roster: the
   test used to fall out of membership alone, so an import that misses 300 counselors silently
   un-gates them. It fails closed — nothing breaks, which is exactly why nobody notices. The import
   reconciliation report of
   [D-090](../decisions/decision-log.md#d-090--the-legacy-corpus-is-thousands-of-roster-rows-with-numbers-and-no-money)
   must count people marked as counselors in the corpus against `role_holder` rows written.

**The case the old flag existed for still decides the default.** The organization's answer on who the
gate should spare was *"everything except guardianship and adult volunteers"*: a volunteer whose own
fee is unpaid still runs the Thursday meeting, and losing the roster on the night the fee lapses is
the failure the marking existed to prevent. None of that judgment moved. What changed is that honouring
it no longer needs a flag on a role or a permission on a person — it needs an expression written
without `MEMBERS` — so leaving `MEMBERS` out is now the **normal** shape of a grant to a contractor, a
photographer or a parent helper rather than an exemption somebody must be granted. The line the old
design drew still holds, and it holds harder now that the report is the only mechanism left: **the
report is how the organization notices; the resolver is not how it punishes.**

**Why the test moved rather than vanished.** A resolver clause applies to everything or nothing, and
so had to carry its own exemptions; an expression says which grants are gated, in the text of the
grant, where the person writing it can see it and a report can read it. The old design could not
answer *"is this particular permission meant to require membership?"*, because it never recorded the
answer anywhere. The cost is that recording it is now optional, and the three controls above are what
stands where the guarantee used to be. **Nothing enforces `MEMBERS` being present: a convention, not a
guard**
([D-081](../decisions/decision-log.md#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now)).

The old table of who was gated is kept, because the *answers* did not change — only who gives them:

| Channel | Gated? | Why, and how it is written now |
|---|---|---|
| Ownership (step 1) | **No** | Otherwise a lapse locks a person out of the screen they renew on. Not expressible in an expression at all |
| Guardianship (step 2) | **No** | A legal relationship, not a membership |
| Grants (step 3) | **Only if the expression says so** | `MEMBERS * …`. A grant to a contractor, a photographer or a parent helper who was never a member is written without `MEMBERS` — and that is now the default rather than an exemption |
| A deny (step 0) | **Never, in either direction** | §7.1 |

### 6.2 Audiences — an expression over named sets

A grant names a **person or an audience, never both**
([D-042](../decisions/decision-log.md#d-042--grants-may-target-audiences-not-only-individuals)). An
audience is now **an expression over named sets of people**, stored as a tree of binary nodes and
aimed at by a grant
([D-101](../decisions/decision-log.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree)).
Fields, storage rules and the write-path checks are in
[data-model/05 §8](../data-model/05-authorization.md#8-audience--grants-that-target-a-set-of-people);
what belongs here is the language, and why it is shaped like this.

> **Author in sets. Evaluate per person.**

A check asks about one person, so the resolver compiles the expression down to a predicate and
**never materializes a set**. An implementation that evaluates `MEMBERS` as a list of ids and then
tests for containment pays **a row per member, per request** — at the size
[D-112](../decisions/decision-log.md#d-112--the-systems-scale-is-stated-hundreds-of-people-tens-of-registrants-per-event)
states, a few hundred rows, and every one of them is a row the answer never needed. That is the one way to
get this wrong, which is why it is a requirement rather than an implementation note. **The rule did not
change when the size was written down; the number attached to it did, and the rule is the reason the size
was safe to write. **It has no exception any more.** The corpus used to permit one — *a nightly rebuild may
evaluate per person, because that is what warming a cache is* — and
[D-114](../decisions/decision-log.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation)
deleted the cache, the rebuild, and the exception with them, which is the strongest single argument for that
deletion: **this rule no longer has a place where the design permits itself the thing it forbids.**

**What the rule does not forbid, because the batch API would otherwise violate it:** `which_of(people[], code,
item)` evaluates the predicate for **the people already in hand** — the rows of the page being drawn — and is
therefore a batched predicate, not an expansion. **What stays forbidden is deriving a set in order to answer a
question about one person**, which is the direction that costs a row per member and returns an answer about one
of them. The test is which side you started from: the person, or the set.

The two notations the organization was offered — set algebra, and a per-person boolean formula —
describe the same function: `p ∈ (A ∩ B) ∪ C` **is by definition** `(p ∈ A ∧ p ∈ B) ∨ p ∈ C`. The
choice therefore never decided what the machine computes; it decided **what gets stored and what a
writer is allowed to say**. The set form won. ~~It won because it is the closed one, and closure was
the whole case.~~

**That struck clause was the argument this page made for four rounds, and round 12 withdrew it**
([D-107](../decisions/decision-log.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)).
It is kept here, in the order it was argued, because the argument was reasonable and the place it went
wrong is worth finding:

> [D-060](../decisions/decision-log.md#d-060--eligibility-is-capability-there-is-no-separate-rule-engine)
> refused a rule engine, and a per-person boolean language is the door to one: once `&`, `|` and `!`
> exist, the next operand anybody wants is `AGE >= 15` or `FEE_PAID`, and there is a parser standing
> there to accept it. A set language closes that **by rule instead of by discipline**: *an operand must
> be a named, materializable set of people.* ~~An attribute is not a set of people. Guardianship is
> (`GUARDIANS(x)` is a set), age is not, and the line falls exactly where D-060 already drew it.~~

**The struck sentence is wrong about sets, not about rule engines.** `OLDER(18)` **is** a set of people:
the set of people who are eighteen or older on the date being checked. `MEMBERS` is the set of people who
pass `is_current_member`. ~~`GUARDIANS(x)` is the set of people who hold a row.~~ **That example went in the
same round it left in, and it is worth knowing why, because it was the sentence's best case:** guardianship
*is* a row you can join, so it looked like proof that an attribute-operand can be a set. **It is not an
attribute operand at all — guardianship is a channel that carries its own authority, and
[D-113](../decisions/decision-log.md#d-113--the-guardianship-channel-has-no-expression-guardians-is-not-a-selector)
deletes both spellings of it** (see §*The selectors*). The argument survives losing its best example, which is
what an argument should do: **`MEMBERS` alone already made the point**, and it made it from a table nobody
disputes. **Every operand in the
registry is a test with a set on the other side of it**, and reading one column against one date is not a
different kind of thing from joining one table against one period — so the test this page leaned on was
never holding anything up, and `MEMBERS` would have failed it, since nothing in the model stores the list
of members. **The line was real, and it ran one clause earlier: an operand must be a *named* operand — a
row of the registry.** `OLDER(18)` is a row. `AGE >= 15` is not a row and cannot be one, because **the
language has nowhere to put `>=`**. That is what keeps the rule engine out now, and it is a better fact
than the one it replaced: it does not depend on which predicates a reader happens to grant the status of
"set".

**So: the vocabulary is open and the grammar is closed.** More attribute operands will arrive, as rows and
by decision; the three operators stay the three operators, and [D-060](../decisions/decision-log.md#d-060--eligibility-is-capability-there-is-no-separate-rule-engine)'s
decision stands untouched: no eligibility rule table, no prerequisite system, nothing evaluated anywhere
but in `can()`. **What changed is that a person may now write an age gate out of the vocabulary. What did
not change is that the system applies none of its own accord.** The premise behind opening it at all is
quoted in
[D-107](../decisions/decision-log.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded):
*the people writing these rules know what they are writing*, which is a claim about the authors and not
about the people a rule reaches — the two limits drawn there are this page's business too.

### Grammar

```
expr     := term ( '+' term )*
term     := operand ( ( '*' | '-' ) operand )*
operand  := EVERYONE | MEMBERS
          | ROLE '(' name ')' | GROUP '(' name ')' | name
          | PERSON '(' person ')'
          | AUDIENCE '(' code ')'
          | GUARDIANS [ '(' person ')' ]   ← row DELETED in round 13 (D-113); see below
          | OLDER '(' n ')' | YOUNGER '(' n ')'
          | ATTENDED | PLACED | CONFIRMED | ON_WAITLIST | ORGANIZERS
          | ATTENDED '(' event ')' | PLACED '(' event ')' | CONFIRMED '(' event ')'
          | ON_WAITLIST '(' event ')' | ORGANIZERS '(' event ')'
          | PRESENT '(' event ')'        ← not seeded, by decision; see below
          | '(' expr ')'
```

**Round 12 added two arms to this block and left the operators alone**
([D-107](../decisions/decision-log.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)).
`OLDER(n)` and `YOUNGER(n)` are **ordinary named operands** — `n` a whole number of years, read against the
birth date **on the date being checked**, which is why they landed in the column of the table below headed
"the set, on the checked date" rather than anywhere in a section about conditions.
`MEMBERS * OLDER(13) * YOUNGER(19)` — thirteen to eighteen, a band from two operands — is a set expression in exactly the sense
`MEMBERS * GROUP(cubs) * PERSON(a)` is, and it parses under the two rules above with nothing added to them.

**Round 13 took one arm back out, and the two marked lines in the block are not the same kind of mark.**
`PRESENT(event)` is a selector that was considered and refused a row. `GUARDIANS` was **printed in this grammar
for eleven rounds as though it had one** — in two spellings, with an optional person argument — and
[D-113](../decisions/decision-log.md#d-113--the-guardianship-channel-has-no-expression-guardians-is-not-a-selector)
found that **the registry never had the row**: the seed list has never contained it, in any round. What the
word denoted is not a set the writer can aim a grant at but **the guardianship channel, which is a level over a
child and reaches every action about that child** — so an operand aimed at a child's guardians would offer, one
code at a time, a subset of what those people already hold. It is left printed here, marked, because the
failure it demonstrates is not "this operand does not exist" but **"this operand looked like the others"**, and
a reader of a grammar cannot tell the difference. **The registry is thirteen selectors now** — twelve in round
10, fourteen in round 12, thirteen from here — which is the second time in two rounds this page has had to print
a number it got wrong recently, and the reason it prints the history rather than the figure.

**Boolean spellings were offered for this language and declined, and the reason is the first paragraph of
this section.** `p ∈ (A ∩ B) ∪ C` **is** `(p ∈ A ∧ p ∈ B) ∨ p ∈ C`, so `&`, `|` and `!` would name three
operators this grammar already has, and `!A` is already written `EVERYONE - A` at the same cost once brackets
are printed the way the canonical form requires. **A notation that expresses nothing new is not free:** two
spellings of one operator means the canonical rendering has to pick one, the editor has to accept both, the
write-path checks have to reason about both, and two people's identical rules stop being textually comparable
— which is the property the canonical rendering exists to buy. **`+ - *` remain the only operators**, and
negation stays a subtraction from `EVERYONE`, which has the extra merit of printing the universe it negates
against instead of hiding it behind one character.

**There is still no comparison operator, and that is where the entire safety of this now lives.** No `>=`,
no `<`, no bare `AGE`, no `FEE_PAID` unless `FEE_PAID` is a row of the registry with an evaluator behind it.
A writer composes named operands; **the vocabulary grows by decision, not by typing.**

**Two arms were missing from this block until round 11, and one was missing in the wrong direction.**
`PERSON(p)` and `AUDIENCE(code)` are both in the registry and neither was printed here, so a reader who
learned the language from this page could not have written either operand — the same drift
[F-5](../open-questions.md#f-5--closed--nothing-is-missing-from-the-registry-and-the-last-gap-was-a-selector-that-should-not-have-been-in-it) records for the
other copy of this table. `LIST` was printed here after the round that deleted it. **All three are
corrected above**, and the correction is what makes this block the corpus's canonical grammar again
rather than a stale copy of it.

**A hand-written set of people is a sum, not an arm**: `PERSON(a) + PERSON(b)`. There is no operand for
"the names somebody typed into this audience" and no table behind one
([D-105](../decisions/decision-log.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other));
a set of one is a set, and a set of three is the same thing three times.

Operators: **`+` union, `-` difference, `*` intersection.**

**Precedence: `*` and `-` bind tighter than `+`; `*` and `-` bind equally, left to right; brackets
override.**

**The canonical stored rendering prints every bracket, always.** The alternative is a grant whose
meaning is recoverable only by someone who memorized that table, and the reason this is a requirement
rather than a courtesy is the worked example below: the same string means different things under
different precedence, and a stored grant is read by people years later who did not write it. Because
canonicalization happens on save, **changing the precedence rule later changes nothing already
stored** — a nice property, and the second reason the rendering is a requirement.

*One arm above is not in D-101's printed grammar and is required by its prose twice over: a bare
`name`, resolving against roles and groups together — without it, `MEMBERS * COUNSELORS`, which D-100
writes as an import control, does not parse.* ***Status:*** *assumption — that a bare name is legal;
recorded in [../open-questions.md](../open-questions.md).*

**Names are one namespace, and that is a new dependency.** A bare name resolves against `role` and
`person_group` together, since `ROLE()` and `GROUP()` no longer have to disambiguate. So names are
unique across both tables — and **no single constraint spans two tables**, so the write path carries
the rule and an integrity check asserts that it does
([D-081](../decisions/decision-log.md#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now))
— with case, whitespace and separators folded on write. **Every `selector_type.code` is a reserved
name**, so a group called `MEMBERS` is refused at the save rather than silently rewriting every
expression in the system. What is stored is always kind + id, so **a rename never rewrites a grant**.

### The selectors

| Selector | The set, on the checked date | Argument | Notes |
|---|---|---|---|
| `EVERYONE` | Any person, including non-members and the public | none | Legal — and the reason the editor must show its reach (§*The cost*) |
| `MEMBERS` | Anyone with a current membership | none | Evaluated live. §6.1 |
| `OLDER(n)` | Anyone whose birth date makes them `n` or more years old **on the checked date** | a whole number of years | [D-107](../decisions/decision-log.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded). The first operand in the registry whose argument is **not a thing** — an integer, so it references nothing: nothing to repoint on a merge, nothing for a cascade |
| `YOUNGER(n)` | Anyone strictly under `n` years old **on the checked date** | a whole number of years | The pair exists so the complement is not written `EVERYONE - OLDER(n)`, which is correct and unreadable. The two partition the population **among people who have a birth date**: someone without one is in neither, and that is not a failure — see §*The rules that make the tree safe* |
| ~~`GUARDIANS` / `GUARDIANS(p)`~~ | **— not a selector** | **removed; there is no argument** | [D-113](../decisions/decision-log.md#d-113--the-guardianship-channel-has-no-expression-guardians-is-not-a-selector). **This row was wrong for eleven rounds and the row above the table never caught it:** the seed list never contained a `GUARDIANS` row, so the sentence in this cell — *"guardians of the person this item is about"* — described a selector that could not be written, and its second half described one that was never needed. **Guardianship is a channel, not a set:** a `right_level` of `none`/`view`/`write` on the live `guardianship` row, reaching **any action about that child**, which is wider than any grant an operand could have assembled and narrower in the only way that matters ([D-074](../decisions/decision-log.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular)). A kept list of a child's contact adults is a `person_group` |
| `PERSON(p)` | Just that person | a person | How a named individual's exception lives inside the expression that granted the rule; since [D-105](../decisions/decision-log.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other) also how several named people are written — summed |
| `ROLE(x)` / `x` | Holders of role `x` (`role_holder`) | a role name | |
| `GROUP(x)` / `x` | Members of group `x` (`person_group_member`) | a group name | |
| `AUDIENCE(code)` | Another saved audience's set, evaluated live | an audience code | [D-103](../decisions/decision-log.md#d-103--an-audience-may-name-another-audience); the one operand whose argument is a decision about access rather than a roster, so the one that can name another audience (§6.2) |
| `ATTENDED` / `ATTENDED(e)` | Said yes to this event / to `e` | optional event | `response = attending` |
| `PLACED` / `PLACED(e)` | Said yes and is not waitlisted — **the capacity set** | optional event | The set the events module counts |
| `CONFIRMED` / `CONFIRMED(e)` | Holds a paid place: `PLACED` and `is_confirmed` | optional event | |
| `ON_WAITLIST` / `ON_WAITLIST(e)` | Attending and waitlisted | optional event | |
| `ORGANIZERS` / `ORGANIZERS(e)` | Runs this event | optional event | Appointed on the event, and still grants nothing by itself (§*Event sets*) |
| `PRESENT(e)` | — | **not seeded** | §*Event sets*. Not seeded **by decision** — since [D-107](../decisions/decision-log.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded) nothing here could refuse it as a kind |

**Thirteen selectors, and this table is a copy of
[data-model/05-authorization.md §8](../data-model/05-authorization.md#the-selector-registry), which is the
registry.** **Fourteen when this sentence was first written:** [D-113](../decisions/decision-log.md#d-113--the-guardianship-channel-has-no-expression-guardians-is-not-a-selector)
deleted the `GUARDIANS` row the round after, and this copy lost it in the same edit. That is worth saying
out loud, because it is the same failure one round on and by luck alone — **a count printed in prose is a
count somebody has to reprint when the table changes, and no check prints it.** It is worth recording how far this copy had drifted before round 11 noticed: it never grew a row
for `PERSON` ([D-101](../decisions/decision-log.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree)'s
late amendment) or for `AUDIENCE`
([D-103](../decisions/decision-log.md#d-103--an-audience-may-name-another-audience)) while still carrying the
`LIST` row that round deleted, so a reader who learned the language here could not have written either
operand — and nothing in §11's checks could have said so, because this is prose. **The instance belongs to
[F-5](../open-questions.md#f-5--closed--nothing-is-missing-from-the-registry-and-the-last-gap-was-a-selector-that-should-not-have-been-in-it)**, whose finding was
that a second copy of the registry drifted from the first; this is a third copy, drifting the same way, one
round later.

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
argument is used to be three hard-coded lists. Now the parser reads its reserved words from this
table, the editor builds its dropdown from it, and the write path checks arity against it. **The
language became data.**

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
grant — nearly the whole membership instead of a handful of counselors. D-101 records the corrected
bracketed form as `(MEMBERS - GROUP(schuzka2026-1)) * COUNSELORS`, and that is what the editor writes
to storage whichever way the typed string parses, so **no stored expression is ever ambiguous and
none is ever read bare.** What canonicalization does *not* do is tell the writer, after the fact, that
the expression they typed meant the wide thing. That is the editor's preview, and it is the same
requirement as §*The cost*.

*One note, corrected in round 13. This page spent two rounds closing with a hedge — "if `*` was ever meant
to bind tighter, that is a decision to record" — because it read D-101 as containing two precedence rules.
**It does not.** D-101 states equal-and-left-to-right, states that the choice was made **to match the reading
the writer already had** rather than to be defensible on other grounds, and then **retracts its own first
draft in print**: "This entry's first draft got its own rule wrong — it asserted that the bare form had
changed meaning, which is the `*`-tighter reading this entry then refused." So the sentence this page was
hedging against was a retraction, not a rival ruling, and the hedge was itself the stale claim: **a question
a page keeps asking after the decision log answered it is how a resolved design looks undecided to the next
reader.** The hazard paragraph above stands on its own terms — the wide reading is what an implementer gets
if they reach for arithmetic precedence in the parser, which is precisely the failure D-101 says the
always-bracketed canonical form exists to make impossible. The bare form does not *mean* the wide thing
under this design; a parser with the wrong table would *compute* it, and then the stored brackets would
disagree with the answer.*

### Event sets, and the two sets that are refused

**Nothing owns an event.** `event.org_unit_id` is deleted, and with it `can_event()` — the
unit-authority test that almost every event permission in this system used to be reached through
([D-102](../decisions/decision-log.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)).
An event is an item like any other: `event.create` is held at the unit and creates one, and a unit
grant reaches every event because there is no tier between the unit and the item and no owner to
test.

**`ORGANIZERS` is what replaces unit authority over an event**, and it is not a contradiction of
[D-062](../decisions/decision-log.md#d-062--organizers-are-appointed-on-the-event-not-granted): *an
`event_organizer` row grants nothing* still stands, because **an operand is a set, not a grant.** What
changed is that the appointment is now *aimed at* by grants rather than special-cased inside the
resolver. The rule that used to be hard-coded prose — "answers are read by that event's organizers"
([D-061](../decisions/decision-log.md#d-061--event-answers-are-read-by-that-events-organizers)) — is
now *said* where permissions are said: **a seeded grant of `event.answer.view` on an event, aimed at
`ORGANIZERS`.**

**Presence is refused, and saying so here is the point.** `PRESENT(<event>)` over `was_present` is not
a selector, and the reason is the failure direction: `was_present` is `NULL` until someone takes a
register, so an operand built on it would revoke a child's access to their own camp photos because a
volunteer forgot to tick a box. That column is a safeguarding signal, **three-valued on purpose**
([D-067](../decisions/decision-log.md#d-067--presence-is-a-three-valued-fact-on-the-registration)),
and keeping it out of this language is what keeps it meaning *"a person recorded this"* rather than
*"this is who may see things."* Wherever presence tempts a reader, that is the answer.

**`WHITELISTED` does not exist yet — there is no stored state to name.** The nearest facts are
`source = staff` (an organizer entered them) and promotion off the waitlist. Either it means one of
those or it is a new column on `event_registration`, which is an events decision and not a selector
decision, so it stays an open question in [../open-questions.md](../open-questions.md) **rather than
being implied by a word in a grammar.**

### The rules that make the tree safe

The expression is stored as a tree: one row per node, a node being `operator` + `left_id` +
`right_id`, a leaf being `selector_kind` + `selector_arg_id`, with `audience_id` denormalized onto
every row so the read path is one indexed fetch and never walks a parent chain. **Nothing bounds how tall
or how wide an expression may get.** `selector_depth_limit` used to sit on the audience row and bound the
height; [D-105](../decisions/decision-log.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)
deleted the column, the check that read it, and the placeholder number in this page's own question list, and
**refused to replace it with another bound of either shape.** **The tree is stored exactly as the writer
wrote it** — one row per node, two operands and one operator, left to right, no rebalancing — because a
rebalanced tree is a different expression from the one a person wrote, and storing *that* expression rather
than a normalized equivalent is the entire reason the tree exists. So *"a check costs a bounded amount"* is
no longer a property of this system: **an expansion is bounded only by acyclicity**, and the sentence that
mattered here was never about cost, it was about a number nobody had measured.

- **Exactly one shape per row.** A node has an operator and children and no selector; a leaf has a
  selector and neither. Expressible, so it stays a constraint.
- **One parent, never a DAG.** A side table letting two expressions share a node is refused: editing
  the shared node would silently widen every grant using it. Structure, plus a CI check that no such
  table exists.
- **Cycles are refused when the row is saved, and the two walks that look for them are now the only
  structural guard this module has.** Structurally hard to build, refused rather than trusted, for the
  reason D-091 gives for its own guard: *a hand-fixed row, a restore from before the guard existed.*
  **1. Inside one tree:** walk the parent chain from the row upward and refuse a revisit.
  **2. Across audiences:** follow every `AUDIENCE` leaf and refuse a cycle through them at any distance
  ([D-103](../decisions/decision-log.md#d-103--an-audience-may-name-another-audience)). **This page asserted
  for one round that a tree cannot cycle and the walk over a graph was therefore dead, and D-103 struck that:
  a forest of audiences naming each other is not a tree.** **D-105 deleted the height bound that used to
  travel with these walks and deliberately kept both**, and they must not be relaxed alongside it — an
  expansion that never terminates is the failure the deleted bound was never protecting against, and with
  the bound gone nothing else is standing there. **The read path gets neither a hop counter nor a cycle
  check**, which used to be a back-up position and is now the whole design: a cap on the read path *becomes
  the thing that decides who a grant reaches*, in exactly the case where the data is already wrong. What
  replaces the retired size rule is **a tab on the permissions page**, not the standing report this page
  advertised for one round: [D-109](../decisions/decision-log.md#d-109--nothing-a-rule-names-is-deleted-deprecated-hidden-disabled--and-a-tab-instead-of-a-report)
  removed the report *and the question about it* by refusing to delete anything a rule can name. The tab
  lists the rules that name something deprecated, hidden or disabled, or that fail to resolve at all.
  **It is still not a guard in D-081's sense** — nothing is blocked, no write is refused — but a report has
  to be remembered and a tab is where the person already is, which is the difference between a convention
  and a decoration. **F-21's "who reads it?" resolves to *nobody, because there is nothing to read.***
- **`selector_arg_id` has no foreign key** — it points at `role`, `person_group`, `person`, `event` or
  `audience`, **five kinds of entity**, depending on kind, **or at nothing at all**, since `OLDER(n)` and
  `YOUNGER(n)` write their integer into the same column and an `18` is not a reference
  ([D-107](../decisions/decision-log.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)).
  It is
  [D-011](../decisions/decision-log.md#d-011--scopeid-on-accessgrant-is-polymorphic-with-no-foreign-key)'s
  already-accepted trade-off, with its compensating orphan check.
  **The trade-off stopped being cheap in round 11 and became cheap again in round 13, and this is the bullet
  where both happened.** The hand-typed names used to live in `audience_member`, whose `person_id` was an
  ordinary foreign key, so a merged-away person's rows moved correctly on their own. **Now every hand-named
  person in the system is a value in this keyless column**, so round 11 recorded a duty: a person merge and a
  redaction must repoint every leaf naming the absorbed or erased person, in all five entity kinds.
  **[D-109](../decisions/decision-log.md#d-109--nothing-a-rule-names-is-deleted-deprecated-hidden-disabled--and-a-tab-instead-of-a-report)
  halves that duty and names the half that survives: retiring a role, a group or an audience is now one write
  to that row, never N writes to N expressions — but `PERSON(x)` names a *person*, and
  [D-088](../decisions/decision-log.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)
  lets a redaction require the row to actually go. Erasure wins.** So a merge repoints leaves, a redaction
  repoints leaves, and **nothing else in this system can produce a leaf that names nothing anymore** — which
  is a much smaller domain than round 11 assumed and the reason the compensating scan went from mechanism to
  backstop to, now, nearly-vestigial. The reason the duty cannot be expressed anywhere better is
  [F-10](../open-questions.md#f-10--which-invariants-the-orm-cannot-express-and-who-writes-those)'s —
  **the ORM has no key to follow.** And the failure is not tidiness: a leaf naming nobody is the empty set,
  which is quiet on the allow side and loud on the deny side, so **`EVERYONE - PERSON(x)` with an
  un-repointed `x` stops subtracting anybody and denies everybody.**
- **An operand that does not resolve is the empty set**, and an expression that cannot be evaluated
  reaches nobody. Fail closed, in every direction. **Since D-109 this has exactly one cause in a lawful
  database — a redacted person — because nothing else a leaf can name is deletable any more.** That is not
  the same sentence as the one this page carried for twelve rounds; it is the same *semantics* over a domain
  small enough to state, which is the difference between a rule and a worry. **A hand-edited row can still
  produce one**, and `disabled` deliberately produces the same answer by design (below), so the evaluator's
  behaviour must not change: the empty set, narrowing an allow and widening a deny, now listed in the tab
  rather than in a report nobody opens.
- **Nothing a rule can name is deleted. It is given a state instead** — and the three states must stay three
  different things or one of them will quietly become another
  ([D-109](../decisions/decision-log.md#d-109--nothing-a-rule-names-is-deleted-deprecated-hidden-disabled--and-a-tab-instead-of-a-report)):

  | State | Still resolves? | Offered when writing a rule? | Flagged? |
  |---|---|---|---|
  | **`deprecated`** | **yes, unchanged** | no — not addable to a new rule, not introduceable by editing one | **yes**, highlighted wherever the editor shows it |
  | **`hidden`** | **yes, unchanged** | no | no — it is not obsolete, it is not everybody's business |
  | **`disabled`** | **no — the empty set** | no | yes, **and it is the only state that changes an answer** |

  **The invariant that stops `deprecated` drifting into `disabled` is checkable and cheap: deprecating or
  hiding what an expression names must not change the set the expression resolves to.** That is the precise
  failure this whole design exists to make impossible — a rule that quietly stops granting because somebody
  tidied a list — so it belongs beside the two cycle walks as something a reviewer checks, not as a
  convention
  ([D-081](../decisions/decision-log.md#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now)).
  **`disabled` is the loudest switch in this system:** it stops every rule naming that role, group or
  audience, in every scope, at once, and re-enabling restores all of them — a widening in which nobody
  edited a grant. So **the flag is an audited write that prints the rules it touches**, resolved before and
  after, which is the same report D-104 and D-105 adopted for their own migrations; it is a ruleset write for
  D-111's reasons (§8); and it is the answer to the question this corpus kept meeting — *how do I turn off
  that whole naming without editing forty grants?* — which until now had no answer except a deny per grant.
  A deprecated or disabled name **stays reserved** (D-101), so nothing new can claim the word and split its
  meaning in two.

~~**A group is filled three ways: a rule arm, a manual arm, and an inclusion arm naming other groups,
and its membership is the union of whichever it has.**~~ **Superseded by D-101, which amends D-091
rather than reversing it.** The rule arm became the selectors, the manual arm became the `LIST` leaf —
**a leaf that survived one round before
[D-105](../decisions/decision-log.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)
deleted it, so the manual arm's destination was temporary and the sentence above should be read as a step
rather than an endpoint; the arm's function now lives in `PERSON(a) + PERSON(b)`** — and **the inclusion
arm is gone**: `audience_include`, `include_depth_limit`, the transitive walk and
the write-time cycle check over a *graph* all went, because a tree cannot cycle. The outcome D-091
wanted survives and is better served — `GROUP(kitchen) + ROLE(troop_staff)` composes as much as an
edge ever did, and does it in one grant, where the old audience had **no intersection and no
difference at all**, which is why the counselor example above was not writable in any notation.

~~**`audience_member` stays**, re-roled as the `LIST` leaf: the audience's own dated list of people.~~
**Deleted by [D-105](../decisions/decision-log.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other),
and the sentence above is kept struck because it was this page's answer for a whole round.** A hand-written
set of people is now written where every other set is written: `PERSON(a) + PERSON(b)`, inside the
expression. The table, its per-person dates, its `added_by` and its row in the registry all went with it.

**What survives is the refusal, not the table, and the refusal is the reason the replacement is a sum of
`PERSON()` leaves rather than a group.** Merging the hand-written names into `GROUP(x)` was weighed and
refused twice over, and both reasons are untouched by the deletion: naming three people in one grant would
create a row in the group browser that is not a group anybody talks about, and **a group's members are the
organization's record of who is in it, true when no grant points at it**
([D-098](../decisions/decision-log.md#d-098--a-group-is-a-persongroup-explicit-members-a-lifetime-and-no-authority)) —
so editing a roster to move one grant's reach edits a fact that other grants read. **`PERSON(a)` is the
answer that respects that rule; `GROUP(kitchen) += Honza` is not, and never was.** What did change is that
the *apology* got smaller: `audience_member` was the second dated-member table this design kept on purpose
and explained to D-080, and **now there is one. `person_group_member` is the only dated set of people the
system stores.**

**What is genuinely lost with the inclusion edge** is one-edit widening: *"add the kitchen crew to
everything the troop-staff group is used for"* is no longer a single edit. The answer is that named
sets are the composition mechanism now — name the composite once, aim grants at it — which is D-091's
outcome reached without a graph nobody could see the shape of.

**The cost lands on the editor, not the resolver — and it moved in round 10.** A grant's reach was
never visible in the row that grants it, and D-091 made seeing it a requirement on the screen rather
than a nicety: the person saving the grant must see **the people**, not the audience's name, because
nothing in the grammar stops an expression from containing `EVERYONE`. **After D-102 the preview can
no longer be computed from the grant alone**: `PLACED` means different people on different events, so
the preview is computed **for an item** and says so on screen. That is a real increase in what the
editor has to do, and it is the only thing standing between a writer and a grant that reaches **everybody
the organization has**. (At the sizes stated in
[D-112](../decisions/decision-log.md#d-112--the-systems-scale-is-stated-hundreds-of-people-tens-of-registrants-per-event)
that is a few hundred people, which is not reassuring — it is the same warning with a number under it, and
the number says the preview will not be slow.)

**"Who could read this in 2023?" is answered by the words, and that is the whole of the answer.**
[D-110](../decisions/decision-log.md#d-110--the-expression-is-the-record-of-whom-a-grant-reached) decided it
this way in four words — *"Words only — the expression is the record"* — so this page no longer promises an
answer and no longer keeps a list that would have been one. What that settles, and what it leaves open:

- **The expression is the record of a grant's reach.** The preview still prints a resolved set before a save,
  and the audit row logs that printing as *a rendering on a date*, not as a statement of who was in it. A row
  saying *this grant reached these 214 people* starts decaying the night somebody's birthday falls; a row
  saying *this person wrote these words on this date about this item* cannot go stale. **The audit trail got
  smaller and more honest, which is worth saying out loud, because the usual direction of this kind of change
  is the other way.**
- **What was refused, and why it matters here.** Keeping the preview's list beside the audit row is the
  roster table this corpus has deleted twice, and it would store — indefinitely, against
  [D-088](../decisions/decision-log.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)'s
  window — a per-person record of people who were **never granted anything**, only covered. Every page in
  this module has refused that trade when it was offered in another shape.
- **Why words-only is sound now and would not have been an hour ago:**
  [D-109](../decisions/decision-log.md#d-109--nothing-a-rule-names-is-deleted-deprecated-hidden-disabled--and-a-tab-instead-of-a-report)
  means the nouns survive. A retired office still resolves; a deprecated group still resolves; a name stays
  reserved. **Refuse to delete the nouns and then keeping only the words is not an amputation** — without that
  ruling, this answer would mean *"the past is usually unanswerable"*; with it, the past is usually
  computable and what is left is honestly bounded. That is why these two entries are one design and should be
  read together.
- **Still honest for `ROLE`, `GROUP` and `MEMBERS`** (all periods, all dated), **still unanswerable for bound
  event operands** (`event_registration` records the current fact), and **still lost for the hand-typed names
  once their audit payloads expire** — the hole D-091 accepted for nested audiences, one table wider, which
  [F-17](../open-questions.md) closes against D-110 rather than solving.
- **The conceded part, named so nobody finds it later:** editing a shared audience changes what **every grant
  naming it** has meant all along, because those grants hold a word and not a copy. **An edit to a shared
  audience is a retrospective edit to every rule that names it**, and a recomputation for May will use
  today's inner expression. D-103 accepted this as the price of reuse; D-110 records that it is also the
  reason a past-date answer can be *wrong* rather than merely missing. The control is D-103's existing one —
  **the editor prints the resolved set before an edit to a shared expression saves**, so the person editing
  sees at least once the thing they are changing backwards in time. What is *not* kept is a history of inner
  expressions: **the audit trail records the edit, not the meaning that existed before it.**

~~**F-7 is the route back** — a materialized `effective_permission` snapshot kept *as history* rather than as a
cache — which until this round looked like a performance question.~~ **Retracted, in the same round that wrote
it, and kept here because it was this page's answer for ten minutes.** The route back closed because the thing
it led to was refused for a different reason: a snapshot of whom a rule reached is the roster (§ above), and
[F-7](../open-questions.md) itself dissolved when
[D-111](../decisions/decision-log.md#d-111--the-permission-cache-is-rebuilt-nightly-on-any-ruleset-change-and-on-request)
made the cache a nightly rebuild — a materialized table and a warmed cache turning out to be the same job.
**So there is no route back, and nothing is waiting at the end of one.**

*One clause on that retraction, because it rested on a thing that has since been deleted:* the dissolution was
"the two are one job", and [D-114](../decisions/decision-log.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation)
removed one of the two. **F-7 stays dissolved and its reason changes, which is the kind of thing that comes back
to haunt a corpus if it is not written down** — the answer no longer depends on a rebuild existing, it is simply
that **the expression is the record** and a snapshot of whom it reached is a roster nobody maintains
([D-110](../decisions/decision-log.md#d-110--the-expression-is-the-record-of-whom-a-grant-reached)).
**What does return, and only at D-112's trigger, is the materialized table — on its own merits, as a
performance structure with a per-person invalidation handle and a stated staleness window, not as a route back
into the past.**

---

## 7. Precedence

Two separate questions used to live here. One of them is gone, and the section keeps its shape so that
a reader arriving from the decision log can see which half died.

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
([D-013](../decisions/decision-log.md#d-013--explicit-deny-revoked-is-checked-before-everything)).

**A deny is also never subject to the membership test, in either direction.** A deny blocks someone
who is not a member, which is obvious. What is worth stating: a deny **to an audience** blocks the
people in that audience whether or not they are current members, because the deny is evaluated against
who the expression matches, not against whether they are paid up. Suspensions are absolute; `MEMBERS`
is a condition on a *grant of authority*, and there is no authority here to condition.

**A deny is legal at the unit as well as on an item**, and "exclude her from what the unit grants
everyone" is the case only a deny can serve (§5).

### 7.2 There is nothing left to order

~~Among competing allows, the most specific scope determined the effective level: item grant → unit
grant → organization grant → role. The first tier that yielded a determination decided the level, and
a per-event `manage` therefore gave you `manage` on that event even if your only unit-level grant was
`view`.~~

**Withdrawn by
[D-099](../decisions/decision-log.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality),
which deleted half of
[D-032](../decisions/decision-log.md#d-032--deny-is-absolute-locality-orders-allows-only) — and it is
worth being exact about which half, because the surviving half is the reason this section still
exists.**

**Locality only ever ranked allows against each other.** It answered "two grants both apply and they
say different *amounts*" — a question that cannot be asked when a grant says yes-or-no about one
permission code. Two allows that both apply produce one answer. **Once the answer is boolean, there is
nothing left to order**, and the tie-break, the tier ladder, and `permission_level`'s "is this level
high enough" went with it. D-032's first half — **deny is absolute** — survives intact and is now its
entire content.

What the old consequences guaranteed, and where it comes from now:

| Used to follow from locality | Follows from |
|---|---|
| A per-event grant gives you control of that event even with a narrow unit grant | A grant on that item applying, full stop (§6 step 3) |
| A unit role keeps working for the unit's other events | A unit grant reaches every item, and no item grant can retract it — only a deny can (§7.1) |
| A specific `view` grant works for someone with no role at all — a contractor, a parent photographer | The same, and with no `MEMBERS` in the expression it is not even conditioned on membership (§6.1) |
| Locality orders grants but does **not** create authority | Still true, and now blunt: creating a grant required `access_grant.create` on that item. That is where the authority to make it came from |

---

## 8. There is no permission cache, and what replaces it

Permission checks happen on every request, so this section has been rethought three times in four rounds. It
was a **key plus an invalidation table** for six rounds; [D-111](../decisions/decision-log.md#d-111--the-permission-cache-is-rebuilt-nightly-on-any-ruleset-change-and-on-request)
replaced the table with **a rebuild and a version integer**; and
[D-114](../decisions/decision-log.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation)
deleted the cache the rebuild was warming. **The answer to "how do we make the permission cache effective?"
turned out to be "we don't, and it was not safe either"** — which is worth saying plainly, because the middle
design was not a mistake inside its own frame: given a stored answer, the version integer was the right way to
keep it honest. The mistake was the stored answer.

**What a check costs, with nothing cached.** One indexed read fetches the checked person's live grant rows —
a few dozen rows at the size [D-112](../decisions/decision-log.md#d-112--the-systems-scale-is-stated-hundreds-of-people-tens-of-registrants-per-event)
states — and each candidate grant's expression is evaluated against a handful of indexed point lookups in
`membership`, `role_holder`, `person_group_member`, `event_registration` and the guardianship rows. **The
arithmetic was never the problem. The N+1 across one screen was**: a 50-row list asking four codes per row is
two hundred checks, and two hundred checks doing the same person's grant read two hundred times is the shape
that made a cache look necessary. The replacement fixes that shape directly.

**Three things do the work the cache was supposed to do:**

1. **A compiled expression is cached** — parsed once, operand kinds resolved once, the parameterized predicate
   emitted once, keyed by the expression's root and `ruleset_version`. **It holds no person and no item**,
   because both arrive as parameters, and that is precisely why it survives across everyone in the organization
   while an answer never could: nothing in a compilation depends on whom or where it is being asked about.
2. **A request memoizes.** The checked person's grant rows are read once and every code, item and date in that
   request is answered from them in memory; a named operand that recurs in one request (`ROLE(leader)`,
   `GROUP(cubs)`) is resolved once. **Its lifetime is the request, so it has no invalidation policy and no
   staleness window — there is nothing to invalidate.**
3. **The bulk screens batch.** `can_many(person, codes[], item?)` answers a screen's affordances from one
   resolution; `which_of(people[], code, item)` answers a list's from one pass. The per-item preview (§6.2,
   F-15) and the permissions tab (D-109) are written against these, not against a loop of single checks.

**The one thing still cached across requests is a named roster**: `ROLE(x)` over `role_holder`, `GROUP(x)` over
`person_group_member`, keyed by `x`. Two conditions, and together they are the whole difference from what was
deleted. **The key is the thing a write touches**, so invalidation is local to the row that changed and never
global — which is the property the answer cache could never have, because an answer's key names a person and the
write that changes it usually names nobody. And the cache holds **the dated rows, or the set with its validity
ranges**, never the set as of today, so the checked date is still applied at check time and a period ending at
midnight needs no job to be seen. A roster is also something a person maintains and can point at; an answer never
was. **The exception is exactly two selectors wide.** `MEMBERS` is not a roster — nobody writes its rows, and the
1 January sweep rewrites the `membership` dates it reads for everybody at once, which is the bulk event this round
removed from every invalidation list. `ORGANIZERS` is not one either: it has holder rows, but it is bound to an
item ([D-102](../decisions/decision-log.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)),
so a cache keyed by it would be a stored answer to "who was at this event", which is the set D-102 declined to
make permanent.

**What may never be stored again is invariant 19** (§11 of
[data-model/05-authorization.md](../data-model/05-authorization.md#11-invariants-to-verify)): **no row,
table or field may map a person — or a person and a code, or a person and an item — to a permission answer.** Its
enforcement is structural, which is the best kind this corpus has: **the schema has nowhere to put one**, because
the only table that could hold it was deleted. The residue is named rather than glossed — an implementer who
wants a cache back is stopped by this page and by review, not by a constraint, so for them it is
**a convention, not a guard** ([D-081](../decisions/decision-log.md#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now)),
and [D-114](../decisions/decision-log.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation)
lists the three things a returning cache must carry: a per-person invalidation handle next to the global one, an
explicit statement of which tables it watches, and that statement **derived from the operand registry rather than
from a list of ideas**.

**Why deleting it is a strengthening and not a trade.** Every answer is now computed from live rows at the
moment it is asked, so:

- **"The safeguarding case is immediate" is true by construction.** A revoke, a deny, a closed period, an ended
  guardianship, a `membership.terminate`, a cancelled registration — all visible on the **next check**, with no
  job in between and no list to remember to include them in.
- **[D-107](../decisions/decision-log.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)'s
  accepted drift stops existing.** What that ruling waived was the calendar moving an answer between rebuilds: a
  birthday crossing `OLDER(n)`, a period reaching its own `valid_to`, the 1 January sweep. Under live resolution
  all three move the answer **at the instant they happen**. The ruling stands — *"IT IS FINE"* — and its
  mechanism is no longer needed, which is the best outcome a ruling can have. **"Up to one night stale" is
  deleted from this corpus.**
- **The bump set shrinks from eight kinds of write to two tables.** A compilation depends on an expression's
  shape and the seeded vocabulary and on nothing else, so `ruleset_version` is bumped by a write to
  **`audience_operand`** or **`selector_type`** only — where D-111's set was six tables, D-109's flag and a merge.
  `access_grant` drops out because **grants are not compiled**: a check reads the person's live grant rows, so a
  new, edited or revoked grant changes what that read returns and leaves nothing stale to drop; the `deprecated | hidden | disabled` flag drops out because a
  state is **not compiled in** — resolution reads it live, once per request, memoized, which is also why
  `disabled` still means *now*
  ([D-109](../decisions/decision-log.md#d-109--nothing-a-rule-names-is-deleted-deprecated-hidden-disabled--and-a-tab-instead-of-a-report));
  and `role_holder`, `person_group_member`, `guardianship_permission` and a person merge drop out because they
  move rosters and rows that are read live or invalidated locally. **Concretely: adding a child to a group,
  which used to drop the entire cache, now drops nothing.**
- **The question that defeated the old design becomes answerable.** "Whom does this change reach?" was
  unanswerable without evaluating, because it fanned out to **people**. A compilation is finite and enumerable
  over the audience tree, so *"an edit to a shared audience invalidates everything"* becomes *"it invalidates the
  compilations that embed it"* — a bounded walk over rows that already exist.
  **One qualification, stated in the direction and not the spirit:** it is *not* the walk the save path performs
  for cycles, which runs forward from the tree being saved. Invalidation needs the **reverse** direction, the one
  the delete-refusal check already runs. **Same forest, same rows, opposite way** — and the cost of listing that
  forest is registered as unverified at any size in `data-model/05` §13, so what is claimed here is **bounded**,
  not **cheap** ([D-103](../decisions/decision-log.md#d-103--an-audience-may-name-another-audience)).

**The key, and the one thing of it that survives.**

```
~~(person_id, permission_code, scope_type, scope_id, at_bucket)~~
```

The key is deleted with the table. **Its lesson is not**: since D-102 a bound operand means the *same*
expression yields different people on different items, so **a compiled form computed while checking one item may
never be served for another**. With no key, that survives as a rule about binding — the item is a parameter of a
predicate, and a predicate bound to event 1204 is not the predicate for event 1205. That observation is the part
of F-6 that outlived both designs.

**What was retracted, kept in print.** The section used to carry two lists and to say of them: *"~~the line
between those two lists is the entire safety property~~"*, and *"~~every withdrawal a person performs is a
ruleset write … the safeguarding case is immediate~~"*. The first list was `access_grant`, `audience_operand`,
`guardianship_permission`, `permission`, `role_holder`, `person_group_member`, the D-109 flag, and a merge; the
second permitted a birthday, the yearly sweep, an expiry arriving on its own **and a registration write** to be a
night stale. **Both lists survive in full in D-111, which is where the text of a decision lives; what is being
deleted here is a live rule, not a record.** The reason they go is not that they were untidy but that they were
**wrong in the sensitive direction: `membership` appeared on neither list, although
[data-model/03-membership.md](../data-model/03-membership.md) §6 had demanded it three rounds earlier** — *"The
permission cache must be invalidated on every membership transition … retrofitting it is where the bugs will be"*
— and `membership.terminate` ⛔ is
`safeguarding_officer`, *"whoever finds the problem and whoever ends a membership over it are the same person, and
nobody else"* — is the most safeguarding-shaped write in the catalog.** A member was terminated, `MEMBERS`
shrank, nothing rebuilt, and a cached `true` behind `MEMBERS * …` stood until the nightly job ran. Nor was the
fix to add a row: a correct invalidation set is **every table any operand can read transitively**, which is the
read path, and a hand-maintained copy of the read path is a second source of truth about what an expression
means — the same defect class as a registry whose prose contradicts it
([D-104](../decisions/decision-log.md#d-104--a-permission-codes-last-segment-is-an-action-and-a-registry-that-prose-contradicts-is-a-fiction)).
**What is retracted is the claim that those lists were a safety property at all: a safety property that must be
re-derived from the grammar every time an operand is seeded is a chore with a reassuring name.**

**What is genuinely lost.** A nightly job used to pre-pay the expensive screens. The per-item preview, the
permissions tab and the "who holds this" listing now do their work when somebody opens them, which is affordable
at the stated size and was always the plan for the tab ([D-109](../decisions/decision-log.md#d-109--nothing-a-rule-names-is-deleted-deprecated-hidden-disabled--and-a-tab-instead-of-a-report))
— **but that ruling now has no fallback, and that is a dependency, not a comfort.** At
[D-112](../decisions/decision-log.md#d-112--the-systems-scale-is-stated-hundreds-of-people-tens-of-registrants-per-event)'s
trigger the reopen answer is named rather than vague: materialize `effective_permission` per person, **and call it
that** — a real materialization with a per-person invalidation handle and a stated staleness window, which is the
honest shape of the object deleted here.

**What the rebuild does not lift** is the rule this page has carried since the expression tree arrived, and it is
now the only rule left in this section: **inside a check, an expression is compiled to a predicate on the person
being asked, never materialized as a set** (§6.2). There is no longer a nightly job permitted to do exactly that
on the side, which removes the one place the corpus had allowed itself the forbidden object and then had to
explain it.

## 9. Delegation

A leader going on leave, a treasurer handing over during an audit — the common need to lend authority
temporarily.

A delegation is an **ordinary grant** with its provenance set: `is_delegated`, `delegated_from` naming
the person whose authority is being lent, `grant_reason`, and a `valid_to`. Round 10 makes this
*easier* to get right rather than changing it: because a grant is **one permission code**, "do not lend
more than you hold" is a set-membership test rather than a comparison of levels
([D-099](../decisions/decision-log.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)).

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

~~`role.is_delegatable`~~ — the role-level switch that made a whole office lendable — went with the
rest of the role configuration in D-100, which lists `role`'s surviving columns as `code`, `name`,
`description`, `is_system`, `sort_order`. *Lending is therefore said on the grant, not on the role.*
***Status:*** *assumption — D-100 names the column in neither the deleted nor the kept list; recorded
in [../open-questions.md](../open-questions.md).*

---

## 10. Anti-patterns this design rejects

Stated explicitly, because each is a common and expensive mistake:

| Rejected | Why | Instead |
|----------|-----|---------|
| `person.is_admin` boolean | Cannot scope, cannot date, cannot audit, cannot delegate | A grant at the unit, aimed at a role |
| Role on `person` (`person.role = 'leader'`) | One role per person, no history | `role_holder`, many per person |
| Checking membership type in code (`if type == 'adult'`) | Rules change; the check is invisible and untestable | A permission, granted deliberately. There is one membership type now, so this is doubly wrong |
| **Deriving access from holding a role or being in a group** | Being something is not being able to do something (D-005), and a role confers nothing by itself | A live grant whose audience names `ROLE(x)` or `GROUP(x)` — §4 |
| **A grant written as `ROLE(x)` when it meant `MEMBERS * ROLE(x)`** | The test used to be impossible to forget; now it is a term the writer must type, and forgetting it silently authorizes a lapsed member | The standing report of role grants without `MEMBERS`, seeded grants that carry it, and the import count — §6.1 |
| **An `access_level` coming back as a comparison** | It re-imports `permission_level`, the rank rule, and locality's tie-break, all of which were deleted with their only consumers | Roles and audiences as the bundle — what D-068 already said — and one row per code when you need it in writing |
| **`-` in an expression used instead of a deny** | Subtracting narrows one grant's reach; it cannot say "whatever else she is given" | A deny, which defeats every grant — §5, §7.1 |
| **An expression whose reach nobody saw** | `EVERYONE` is a legal operand, and a bound operand means different people on different items | The editor expands the set **for an item** at the moment of granting — §6.2 |
| `PRESENT(e)` over `was_present` | `NULL` until someone takes a register: a volunteer's forgotten tick would revoke a child's own photos | The four attendance tiers, and presence stays a safeguarding signal — §6.2 |
| Role → permission mapping hardcoded in the app | Cannot be reviewed by the organization, cannot change without deployment | Grant rows naming `ROLE(x)` — readable, and the answer to "what may a treasurer do?" |
| Deriving access from guardianship without a right | Authorization by identity is unauditable and unsafe | The explicit right level on the `guardianship` row, compared against `right_kind` |
| Deleting a grant to revoke it | Loses the record of what was revoked when | `valid_to`, and a `deny` when the *fact* of the restriction matters |
| A live deny that matches no allow | A deny that denies nothing is how a stale restriction survives its reason | The dead-weight-deny report — §5 |
| Two authorization implementations | They diverge; the weaker one becomes the exploit | One resolver, §6 |
| Unit leader sees all member data by default | Fails safeguarding review | Scoped grants, resolved per operation — and §2.1 on what protection is gone |
| ~~Downward inheritance of authority through the unit tree, and `scope_exposure` rows written at the covered unit~~ | **Withdrawn by D-097.** The rejected thing and its replacement both needed a hierarchy; there is one unit | A grant at the unit, which reaches every item — §2 |
| ~~"Most specific scope always wins", including against a deny~~ | Still rejected, and the rejection now has nothing to bite on: only allows were ever ordered | Deny absolute, and no ordering at all — §7 |
| ~~Treating an organization-scoped role as universal "so the registrar can work"~~ | The distinction it protected (the root's data vs a sub-unit's data) has no second side anymore | Everything is unit data. If a permission is missing, add the permission |

---

## 11. Open issues

- **Which grants are meant to carry `MEMBERS`?** Nothing enforces it (§6.1), and the tab that lists the
  answer is decided while its threshold is not — *every* `ROLE(...)` operand without `MEMBERS`, or only
  the offices marked sensitive? It lands in the tab's `Unusual` section either way
  ([F-13](../open-questions.md#f-13--closed--a-rule-that-resolves-correctly-but-looks-odd-is-listed-as-unusual-never-as-broken),
  [F-21](../open-questions.md#f-21--closed--no-report-a-tab-on-the-permissions-page-and-unbounded-cost-is-accepted-at-the-stated-size)),
  so what is still undecided is only how wide that section is.
- **The holder period.** Nothing forces a `role_holder` row to end, and the report that used to be
  backstopped by the gate now stands alone (§4, D-071).
- **Who may compose an expression?** `audience.manage` covers creating and editing a set, and the
  catalog is silent on the edit that puts `EVERYONE` into a grant's audience
  ([appendix/permission-catalog.md §12](../appendix/permission-catalog.md#12-open-issues)). No new
  code was invented for this — the gap is the finding.
Round 13 emptied most of this list, and what emptied it is worth naming rather than quietly pruning: the
questions left were not answered with a mechanism, they were answered by **refusing the mechanism** — no
fingerprint, no TTL, no materialized history, no `WHITELISTED`. Five of the nine bullets that stood here an
hour ago are now in the paragraph below, and one of them was closed by noticing the cache it worried about
has no TTL to tune.

**Resolved and no longer open**, kept visible so the reasoning survives:
**duplicate expressions** — two expressions with the same meaning stay two different row sets, and nothing
computes their equality, not even a warning fingerprint; the fingerprint this page proposed as "informing a
human, not gating one" was refused outright, because computing it means evaluating both sides and
[F-14](../open-questions.md#f-14--closed--nothing-computes-semantic-equality-of-two-expressions-and-nothing-will)
decided the language's meaning is not something the platform computes
([D-110](../decisions/decision-log.md#d-110--the-expression-is-the-record-of-whom-a-grant-reached));
**`WHITELISTED`** — stays unseeded, there is no state to evaluate, and the feature it was wanted for
arrives as grants anyway ([F-20](../open-questions.md#f-20--closed--whitelisted-stays-unseeded-because-there-is-no-state-to-evaluate-and-the-feature-arrives-anyway));
**which selectors ship** — the thirteen in the table above, seeded, organization-read-only, and a fourteenth is a
decision entry plus a seed row
([F-5](../open-questions.md#f-5--closed--nothing-is-missing-from-the-registry-and-the-last-gap-was-a-selector-that-should-not-have-been-in-it),
D-113 removed one rather than any of these adding one);
**the cache TTL** — asked three times in four rounds and answered differently each time: a TTL and an
invalidation table; then no TTL and a rebuild with every entry stamped `ruleset_version`, valid only while the
versions match ([D-111](../decisions/decision-log.md#d-111--the-permission-cache-is-rebuilt-nightly-on-any-ruleset-change-and-on-request));
then **no cache at all** — nothing maps a person to an answer, the only cached things are a compiled expression
and a memo that dies with the request, and `ruleset_version` bumps on two tables instead of eight kinds of write
(§8, [D-114](../decisions/decision-log.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation));
**whether a historical check must be answerable** for bound event operands — yes, by the same evaluator
running over history as it is written, and the materialized effective-permission table this page kept
proposing is the nightly rebuild wearing a different name
([F-7](../open-questions.md#f-7--dissolved--a-nightly-rebuild-of-cached-answers-and-a-materialized-effective-permission-table-are-one-job));
and **whether the dead-weight and ungated-office reports are a job or a screen** — a screen: a tab on the
permissions page with a `Broken` and an `Unusual` section, computed when opened, with no cadence to record
because nothing runs
([D-109](../decisions/decision-log.md#d-109--nothing-a-rule-names-is-deleted-deprecated-hidden-disabled--and-a-tab-instead-of-a-report),
F-13, F-21). Earlier rounds: whether any permission is
conditioned on membership being current (**no resolver condition — the writer says so with `MEMBERS`;
D-039's clause and D-051's two exemptions are deleted, §6.1**); whether the gate should also reach item
grants (the question is dissolved: it reaches nothing, and an expression is where the choice lives);
whether a role may be held by a rule as a group is (**no** — F-12 closed by D-100, §4); polymorphic
`scope_id` (confirmed — §5, F-2); the bulk exposure tool, the direction-of-authority check, whether
the root may read into its sub-units, and whether a body may expose its scope (**all dissolved by
D-097 — there are no sub-units, §2.1**); whether a group may be a rule *and* a list, or contain
another group (both superseded by D-101: the arms became selectors, the `LIST` leaf, and `+`; §6.2);
and whether a grant needs a level (no — D-099, §3.1).

All tracked in [../open-questions.md](../open-questions.md).
