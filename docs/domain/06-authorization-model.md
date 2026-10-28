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
([D-031](../decisions/decision-log.md#d-031--no-downward-inheritance-of-authority-scope_exposure-is-the-only-crossing)).
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
| Who was in the Thursday group in 2011? | A point-in-time read over a unit roster | A point-in-time read over `person_group_member` — dated rows, same answer ([D-098](../decisions/decision-log.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority)) |

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
([D-098](../decisions/decision-log.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority)).

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
([D-011](../decisions/decision-log.md#d-011--scope_id-on-access_grant-is-polymorphic-with-no-foreign-key)):

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
     resolver contains no age branch, and
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
- **Fail closed, in every direction.** An operand that does not resolve is the empty set; an
  expression that cannot be evaluated reaches nobody; a scope type nobody registered grants nothing.
  This is the same posture as step 4 and step 0, and it is the direction every uncertainty in this
  model resolves in.
- **A grant may name an audience instead of a person.** The grantee is resolved by the expression in
  §6.2; the scope and the code are resolved exactly as for a personal grant.
- **Effective permissions are never stored.** They are computed per request. A stored permission
  snapshot *will* drift from the grants that produced it — the only question is how long before
  anyone notices. There is now a second reason to keep that question open: the snapshot is also the
  only artefact that could ever answer *who could read this in 2023*, since set membership is
  recomputed from state that keeps moving and the audit payload that recorded the change expires
  (§6.2, [F-7](../open-questions.md#f-7--cache-vs-materialized-effective_permission-table)).
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
tests for containment pays three thousand rows per request. That is the one way to get this wrong,
which is why it is a requirement rather than an implementation note.

The two notations the organization was offered — set algebra, and a per-person boolean formula —
describe the same function: `p ∈ (A ∩ B) ∪ C` **is by definition** `(p ∈ A ∧ p ∈ B) ∨ p ∈ C`. The
choice therefore never decided what the machine computes; it decided **what gets stored and what a
writer is allowed to say**. The set form won because it is **the closed one**, and closure was the
whole case.
[D-060](../decisions/decision-log.md#d-060--eligibility-is-capability-there-is-no-separate-rule-engine)
refused a rule engine, and a per-person boolean language is the door to one: once `&`, `|` and `!`
exist, the next operand anybody wants is `AGE >= 15` or `FEE_PAID`, and there is a parser standing
there to accept it. A set language closes that **by rule instead of by discipline**: *an operand must
be a named, materializable set of people.* An attribute is not a set of people. Guardianship is
(`GUARDIANS(x)` is a set), age is not, and the line falls exactly where D-060 already drew it.

### Grammar

```
expr     := term ( '+' term )*
term     := operand ( ( '*' | '-' ) operand )*
operand  := EVERYONE | MEMBERS
          | ROLE '(' name ')' | GROUP '(' name ')' | name
          | PERSON '(' person ')'
          | AUDIENCE '(' code ')'
          | GUARDIANS | GUARDIANS '(' person ')'
          | ATTENDED | PLACED | CONFIRMED | ON_WAITLIST | ORGANIZERS
          | ATTENDED '(' event ')' | PLACED '(' event ')' | CONFIRMED '(' event ')'
          | ON_WAITLIST '(' event ')' | ORGANIZERS '(' event ')'
          | PRESENT '(' event ')'        ← refused, see below
          | '(' expr ')'
```

**Two arms were missing from this block until round 11, and one was missing in the wrong direction.**
`PERSON(p)` and `AUDIENCE(code)` are both in the registry and neither was printed here, so a reader who
learned the language from this page could not have written either operand — the same drift
[F-5](../open-questions.md#f-5--which-operands-are-missing-from-the-selector-registry) records for the
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
| `GUARDIANS` / `GUARDIANS(p)` | Guardians of the person this item is about / of `p` | optional person | |
| `PERSON(p)` | Just that person | a person | How a named individual's exception lives inside the expression that granted the rule; since [D-105](../decisions/decision-log.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other) also how several named people are written — summed |
| `ROLE(x)` / `x` | Holders of role `x` (`role_holder`) | a role name | |
| `GROUP(x)` / `x` | Members of group `x` (`person_group_member`) | a group name | |
| `AUDIENCE(code)` | Another saved audience's set, evaluated live | an audience code | [D-103](../decisions/decision-log.md#d-103--an-audience-may-name-another-audience); the one operand whose argument is a decision about access rather than a roster, so the one that can name another audience (§6.2) |
| `ATTENDED` / `ATTENDED(e)` | Said yes to this event / to `e` | optional event | `response = attending` |
| `PLACED` / `PLACED(e)` | Said yes and is not waitlisted — **the capacity set** | optional event | The set the events module counts |
| `CONFIRMED` / `CONFIRMED(e)` | Holds a paid place: `PLACED` and `is_confirmed` | optional event | |
| `ON_WAITLIST` / `ON_WAITLIST(e)` | Attending and waitlisted | optional event | |
| `ORGANIZERS` / `ORGANIZERS(e)` | Runs this event | optional event | Appointed on the event, and still grants nothing by itself (§*Event sets*) |
| `PRESENT(e)` | — | **refused** | §*Event sets* |

**Twelve selectors, and this table is a copy of
[data-model/05-authorization.md §8](../data-model/05-authorization.md#the-selector-registry), which is the
registry.** It is worth recording how far this copy had drifted before round 11 noticed: it never grew a row
for `PERSON` ([D-101](../decisions/decision-log.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree)'s
late amendment) or for `AUDIENCE`
([D-103](../decisions/decision-log.md#d-103--an-audience-may-name-another-audience)) while still carrying the
`LIST` row that round deleted, so a reader who learned the language here could not have written either
operand — and nothing in §11's checks could have said so, because this is prose. **The instance belongs to
[F-5](../open-questions.md#f-5--which-operands-are-missing-from-the-selector-registry)**, whose finding was
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

*One honest wrinkle, reported rather than smoothed over: D-101 states the precedence as
equal-and-left-to-right and, in the same entry, states that the bare form "now means everyone except
the counselors in that group", which is the `*`-binds-tighter reading. The rule above is the one both
D-101's grammar and round 10's vocabulary fix, and the corrected bracketed form is reproduced as D-101
gives it. If `*` was ever meant to bind tighter, that is a decision to record — and because everything
is stored fully bracketed, nothing already stored would change.*

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
  replaces the retired size rule is a **standing report** of the widest and deepest audiences — a report,
  with nothing behind it, so **a convention and not a guard**
  ([D-081](../decisions/decision-log.md#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now)),
  and [F-21](../open-questions.md#f-21--nothing-bounds-an-audience-expansion-now-who-reads-the-report-of-the-widest-ones)
  is open on who reads it.
- **`selector_arg_id` has no foreign key** — it points at `role`, `person_group`, `person`, `event` or
  `audience`, **five kinds**, depending on kind. It is
  [D-011](../decisions/decision-log.md#d-011--scope_id-on-access_grant-is-polymorphic-with-no-foreign-key)'s
  already-accepted trade-off, with its compensating orphan check.
  **The trade-off stopped being cheap in round 11, and this is the bullet where that bites.** The
  hand-typed names used to live in `audience_member`, whose `person_id` was an ordinary foreign key, so a
  merged-away person's rows moved correctly on their own. **Now every hand-named person in the system is a
  value in this keyless column**, so a **person merge and a redaction must repoint every leaf naming the
  absorbed or erased person, in all five argument kinds**. The nightly orphan scan becomes the **backstop
  rather than the mechanism**: it runs a day late, and it only fires at all if the absorbed person's row is
  actually removed. The reason it cannot be expressed anywhere better is
  [F-10](../open-questions.md#f-10--which-invariants-the-orm-cannot-express-and-who-writes-those)'s —
  **the ORM has no key to follow.** And the failure is not tidiness: a leaf naming nobody is the empty set,
  which is quiet on the allow side and loud on the deny side, so **`EVERYONE - PERSON(x)` with an
  un-repointed `x` stops subtracting anybody and denies everybody.**
- **An operand that does not resolve is the empty set**, and an expression that cannot be evaluated
  reaches nobody. Fail closed, in every direction.

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
([D-098](../decisions/decision-log.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority)) —
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
editor has to do, and it is the only thing standing between a writer and a grant that reaches 3,000
people.

**"Who could read this in 2023?" has one fewer answer than it had.** Set membership is recomputed, not
recorded, and composition widens how much of the permission answer depends on state that has itself
moved on. The audit trail used to hold the change that made it true, and
[D-088](../decisions/decision-log.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)
empties those payloads after 24 months. So after two years the question is answered by re-running
expressions against dated rows — which is honest for `ROLE`, `GROUP` and `MEMBERS`, whose rows are all
periods, and **unanswerable for bound event operands**, since `event_registration` records the current
fact. **Round 11 moved one more case from the first group to the second:** the hand-typed names used to be
`audience_member` rows with `valid_from` / `valid_to`, so *"was Honza on this audience in June?"* was
answerable from the table itself the way a group's membership is; **now it is a recomputation over audit
payloads, and those payloads expire after 24 months, so the question stops being answerable in 2028**
([D-105](../decisions/decision-log.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)).
That is the same hole D-091 already accepted for nested audiences and
[F-17](../open-questions.md#f-17--a-nested-audience-has-no-reconstructable-past-is-that-the-case-for-materializing)
states for them — the same hole, one table wider, accepted rather than papered over. **[F-7](../open-questions.md#f-7--cache-vs-materialized-effective_permission-table) is
the route back** — a materialized `effective_permission` snapshot kept *as history* rather than as a
cache — which until this round looked like a performance question.

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

## 8. Caching and invalidation

Permission checks happen on every request. Compute cheaply, cache carefully.

**The cache key must include everything the answer depends on:**

```
(person_id, permission_code, scope_type, scope_id, at_bucket)
```

where `at_bucket` truncates the timestamp to a granularity shorter than the shortest grant duration you
allow. If grants can start or end at an arbitrary second, a time-bucketed cache is unsafe — use
`now()` and a short TTL instead.

**Since D-102 the item is not optional in that key.** A bound operand means the *same* expression
yields different people on different items — `PLACED` on event 1204 is not `PLACED` on event 1205 —
so a cached answer computed while checking one item may never be served for another, and any cache
keyed per person or per grant alone is now a bug
([F-6](../open-questions.md#f-6--the-permission-cache-lifetime-and-what-invalidates-it), amended).

**Invalidate on:**

- any write to `access_grant`, `audience_operand`, `guardianship_permission` — **and one fewer table than
  this list carried, since `audience_member` is deleted**
  ([D-105](../decisions/decision-log.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)):
  the hand-named people it used to announce are rows of `audience_operand` now, so the row above already
  covers them
- **`role_holder`** — an office gained or lost changes every grant whose expression names `ROLE(x)`.
  This is the index the question "what may a treasurer do?" runs on (§4), which is also why
  operand-level caching pays off: a cached operand can be reused across every grant that names it, and
  `role_holder` changes are the invalidation
- **`person_group_member`**, for the same reason through `GROUP(x)`
- **any write to an audience's tree** — an edit to an expression changes the answer for every grant
  aimed at it, so invalidation cannot be scoped to the row that was touched
- **every membership transition, including the yearly expiry sweep** — `MEMBERS` is evaluated on the
  checked date, so a lapse changes whether a person is in the set for every gated expression in the
  system. Invalidate **by `person_id`, not by scope**, and make it a bulk operation the cache is
  designed for: the sweep touches everyone at once
- **a merge, and an unmerge** — this is the one that gets missed. Merging two people unions their
  permissions, so the survivor's cache must be cleared; reversing a merge splits them back in two, so
  both rows must be cleared, and it gets missed for the opposite reason — nobody thinks of an undo as
  a permission change
  ([D-087](../decisions/decision-log.md#d-087--merge-chains-stay-because-reversing-a-merge-is-a-supported-operation)).
  Unmerge is `person.merge`, not a separate code, so nothing here changes shape; only the list of
  events that must invalidate does. See
  [03-identity-and-legacy.md](03-identity-and-legacy.md#6-reversing-a-merge).
- **a write to `event_registration`** — a new registration, a confirmation, a promotion off the
  waitlist. Every bound attendance operand changes, and this is the invalidation most likely to be
  left out, because the events module does not look like a permission table
- ~~a unit's parent changing~~ and ~~a write to `scope_exposure`~~ — **retired together by D-097**,
  the first because reparenting was already impossible
  ([D-036](../decisions/decision-log.md#d-036--units-cannot-be-reparented-a-unit-that-moves-is-a-new-unit))
  and the second because the table it named no longer exists

**A note on TTL.** Access still changes on a *date* rather than on someone's action — not because of a
gate, but because `MEMBERS`, `GROUP(x)`, `ROLE(x)` and every dated row are read as of the checked
date. The sweep invalidates immediately; the TTL governs the window for transitions that are not the
sweep. Keep the TTL short and measure.

**Alternative worth considering:** materialize `effective_permission` as a table refreshed on write
rather than cached per request. Faster reads, but it is a denormalization and it must be maintained
transactionally — if a refresh fails silently you have an access bug that nothing detects. If you take
this path, add a verification job that recomputes and compares. Recommendation: start with
cache-only, add materialization only if measurement demands it (F-7, and §6.2 for the history argument
that now points the other way).

---

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

- **Which grants are meant to carry `MEMBERS`?** Nothing enforces it (§6.1). The report is the
  control, and the report's threshold — *every* `ROLE(...)` operand without `MEMBERS`, or only the
  offices marked sensitive? — is decided nowhere.
- **Whether the report of dead-weight denies and the report of ungated offices are scheduled jobs or
  screens somebody opens.** Both are entire controls now, and neither has a cadence recorded.
- **The holder period.** Nothing forces a `role_holder` row to end, and the report that used to be
  backstopped by the gate now stands alone (§4, D-071).
- **Who may compose an expression?** `audience.manage` covers creating and editing a set, and the
  catalog is silent on the edit that puts `EVERYONE` into a grant's audience
  ([appendix/permission-catalog.md §12](../appendix/permission-catalog.md#12-open-issues)). No new
  code was invented for this — the gap is the finding.
- **Duplicate expressions.** Two expressions with the same meaning are now two different row sets, so
  *"you already granted exactly this set on that item"* no longer falls out of storage. The route back
  is a normalized **fingerprint** computed on save as a derived value used only for a warning — and if
  the expansion overflows, skip the warning rather than refuse the write: normalization informing a
  human, not gating one. Registered in [../open-questions.md](../open-questions.md), not promised
  (D-101).
- **`WHITELISTED`** — no stored state to name, so no selector. An events decision before it is a
  selector decision (§6.2, D-102).
- **Which selectors the seed ships**, and whether an organization may add one: the language is one
  seeded table plus an evaluator, so an operand can be added by any later decision, and which ones
  ship on day one is not decided
  ([F-5](../open-questions.md#f-5--which-operands-are-missing-from-the-selector-registry)).
- **The cache TTL** under live-evaluated selectors (§8).
- **Whether a historical check must be answerable at all** for bound event operands, and whether that
  is what finally justifies a materialized history table (§6.2, F-7).

**Resolved and no longer open**, kept visible so the reasoning survives: whether any permission is
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
