# Data Model — Authorization: permissions, offices, grants

`permission`, `role`, `role_holder` and `access_grant`: the four tables a permission
is made of, plus the numbers of the two that no longer exist.

**Section numbers are shared across the five parts** and never renumbered, because other
pages cite them by number and their anchors are built from them: [05-authorization.md](05-authorization.md) holds §1–§7, [05a](05a-audience-and-grammar.md) §8 (the `audience` table, the grammar, the selector registry), [05b](05b-expression-tree.md) §8 continued (the tree and what each operand costs), [05c](05c-access-log-and-resolver.md) §9–§10 (`access_log` and the resolver), and [05d](05d-invariants-and-seed.md) §11–§13 (invariants, seed data, open issues).

---

# Data Model — Authorization

`permission`, `role`, `role_holder`, `selector_type`, `audience`, `audience_operand`,
`access_grant`, `access_log`.

This is the direct answer to your question about system-wide and per-item permissions.
Design rationale: [../domain/06-authorization-model.md](../domain/06-authorization-model.md).

---

## 1. The shape of the answer

```
permission ─────────────── the atomic capability.       'membership.request.approve'
                            + where it may be granted:  applies_to  unit | unit_and_item
                            + read or write:            right_kind

access_grant ───────────── THE ONE TABLE THAT GRANTS.   grantee (person | audience),
                                                       scope ('unit' | exactly one item),
                                                       one code, effect (allow | deny),
                                                       period

role ───────────────────── an office, conferring nothing.     'treasurers'
role_holder ────────────── who holds it, for a period.        person X, 'treasurers',
                                                              2026-03-01 → open

selector_type ──────────── the language: every operand that   'ROLE', 'MEMBERS', 'PLACED',
                          may appear in an expression.          'AUDIENCE'
                          Seeded, is_system, read-only.

audience ───────────────── a set a grant aims at, nameable     MEMBERS * ROLE(treasurers)
                          by code from another audience.
audience_operand ───────── one node of that expression        (a tree, not a string; an
                          — an AUDIENCE leaf doubles as       AUDIENCE leaf is also the
                          the reference edge to another tree)  edge to another audience)

guardianship_permission ── authority over a PERSON.     (04-relationships.md)
access_log ─────────────── what was decided, and by what authority.
```

**One table grants.** `access_grant` is the only place authority is written ([D-005](../decisions/round-01a.md#d-005--permissions-are-grants-never-derived-from-identity)),
plus one table over a single person: `guardianship_permission` (§10, channel guardianship).
**Everything else on this page decides *whom a grant reaches*, which has never been the same
thing** — a role holder, a group member and an audience operand are all sets of people, and being
in one is worth exactly what the grant aimed at it says. That sentence was already true of
audiences before this round; round 10 made it true of roles too, which is the whole of
[D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape).
**One of these tables is gone**: the hand-typed names that used to sit in `audience_member` are
written in the expression, as `PERSON(a) + PERSON(b)`, in the place every other set is written
([D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)).

**And the rule that answers every check** ([D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)):

> **allowed** when some live **allow** applies, and **no** live **deny** applies.

That is the entire precedence rule. "Live" means the row has started as of the checked date, has
not ended on it, and has not been revoked; "applies" is decided per channel in §10. There is no
level to reach, no rank to compare, and no nearer grant that beats a further one — the ladder and
locality were deleted in the same breath, because locality only ever ordered *allows* against each
other and a boolean answer has nothing to order. What survives of the old ordering is deny's
absoluteness, which was [D-032](../decisions/round-02-03.md#d-032--deny-is-absolute-locality-orders-allows-only)'s
first half and is now its entire content.

> **The rule that used to govern all of these tables, and where it went.** This section opened
> with *"authority over a unit originates **at that unit** and cannot be claimed from outside it —
> not by a parent unit, and not by the organization"*, and named `scope_exposure` as the only
> crossing. **Withdrawn by [D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row),
> and the withdrawal is precise: [D-031](../decisions/round-02-03.md#d-031--no-downward-inheritance-of-authority-scope_exposure-is-the-only-crossing)
> was not weakened, it was deprived of its subject.** There is one unit, it is the organization,
> and it is not a row — so there is no "outside it" to be stopped from, and every permission is
> held either at the unit or on an item. The sentence is kept here, struck through in spirit,
> because a reader who arrives from an older draft will look for the rule and should find the reason
> it is gone rather than an empty space. **What of its reasoning still holds is carried by two
> things that were never about units: deny is absolute (§10), and the ownership and guardianship
> channels answer for a person rather than for a body.** What is lost is stated once in §5 and in
> D-097, and is not argued away there or here.

**The two tables that used to be one idea at two granularities, and what they are now.**
[D-010](../decisions/round-01a.md#d-010--role-assignments-and-access-grants-share-a-scope-model-and-a-resolver)
read `role_assignment` and `access_grant` as the same mechanism at different sizes and gave them a
shared scope model and a shared resolver. **Both halves are reversed** — the scope model because
[D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)
left one scope and `role_holder` therefore has no scope columns at all, and the shared resolver
because there is no role channel to share (§10). What they have in common now is the temporal
pattern, like every dated row in this system:

| | `role_holder` | `access_grant` |
|---|---|---|
| Says | *this person holds this office in this period* | *this grantee may, or may not, do this one thing here* |
| Carries authority | **No** — confers nothing (§3) | Yes; it is the only thing that does |
| Scope | None. A role is held at the unit, because there is nowhere else | The unit, or exactly one item |
| Decides | Whom a grant naming `ROLE(x)` reaches | Everything, for one code |
| Typical row | "is the treasurer, from March" | "may read this event's answers" |
| Rows per broad capability | One | One **per code** — a broad office is a couple of dozen of them |

**The row count is the price, and it was paid deliberately**
([D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)).
One grant per code is what buys *"what exactly does this person have?"* answered by reading rows,
and it costs the question *"what does `manage` give me on this event?"*, which has no answer because
there is no such word.

---

## 2. `permission`

**Fields**

| Field | Kind | Notes |
|---|---|---|
| `id` | integer identity | Surrogate key. |
| `code` | text, required, unique | The stable identifier — `membership.request.approve`. The **code never changes**; `display_name` can. |
| `resource` | text, required | What the permission is about — `membership_request`. |
| `action` | text, required | What may be done to it — `approve`. |
| `applies_to` | enum: `unit`, `unit_and_item` | **New, [D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality).** Where this code may be granted at all: at the unit only, or at the unit *and* on an item. Checked **when the grant is saved**, never at check time — see *`applies_to`* below. |
| `right_kind` | enum: `read`, `write` | **New, [D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality).** Exists for exactly one customer: the guardianship channel's `none` / `view` / `write` ([D-074](../decisions/round-06.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular)). Say the one customer out loud — see *`right_kind`* below. |
| `namespace` | text, optional | `system`, or absent. What it still does, and what it stopped doing, is its own subsection below. |
| `description` | text, required | What it means, for whoever has to read it. |
| `display_name` | text, required | Human label for the permission editor. |
| `is_system` | boolean | Default false. True: seeded by the platform, cannot be deleted or have its `code` changed. |
| `is_assignable` | boolean | Default true. False: a permission **no grant may name directly** — a deprecated code kept only so historical audit rows still resolve to something readable. Before [D-068](../decisions/round-05.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle) this also flagged wildcard `.admin` codes; there are none now. |
| `created_at` | timestamp, audit time | |

**Deleted from this table by round 10:** `requires_scope`. Its job — "a unit-level permission
cannot be granted organization-wide by mistake" — was about *which unit* a permission was held at,
and [D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)
left one unit and a handful of item types. The question it asked ("may this code be granted on an
event at all?") is real and is answered by `applies_to`, which is the same idea with the hierarchy
taken out of it. **Nobody enforces `requires_scope` now, because nothing enforces it: `applies_to`
does its job and does it at a different moment, on the save rather than in the resolver.**

**Rules**

- `code` is well-formed: two or more dot-separated segments of lowercase letters and
  underscores.
- `resource` equals the first dot-separated segment of `code`, so the code's prefix is never a
  second, drifting copy of the resource column. **One exemption**, deliberate: codes beginning
  `system.`, whose resource is the thing being administered rather than the word `system`. There
  used to be a second exemption for the `dependent` namespace, whose codes had two meaningful
  segments (`dependent.medical.view`); those codes are deleted
  ([D-074](../decisions/round-06.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular))
  and the exemption went with them, so nothing may be added under a namespace prefix again
  without reopening this rule.
- `code` is unique.
- `applies_to` and `right_kind` are both required. A required enum with two values is cheap; a
  nullable one whose null-ness silently means something is how the guardianship channel would have
  acquired an answer that depends on a value nobody typed.
- **A code seeded as `system.` is seeded `applies_to = unit`.** This is not decoration; see
  *What `namespace` does now*.

### There is no wildcard permission

A check for `X.y` is satisfied by **an exact allow of `X.y`**, or by `system.admin`, which is
checked outright and is the only permission meaning *everything*.

```
A check for permission 'X.y' is satisfied by:
    - an exact allow of 'X.y', OR
    - an allow of 'system.admin'   (NULL-namespace permissions only)
```

**There are no `<resource>.admin` codes.** The convention that every resource should expose
one, matched by prefix in the resolver, was **reversed by
[D-068](../decisions/round-05.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle)**,
which also removed the resolver branch that implemented it. "Can do everything about events" is an
**office** composed from the thirteen `event.*` codes — which is to say, a role some grants name,
each grant naming one code (D-052) — because that composition is runtime data the organization
edits, and a wildcard was the code guessing at it instead.

**The cost is the one D-007 existed to prevent, and it is accepted:** a new narrow permission
is not automatically covered by the offices that should imply it. Integrity check **13**
(permissions no live grant names) is the net the wildcard used to be. It fails closed.

`is_assignable = false` exists for permissions that only make sense as part of a bundle —
a deprecated narrow permission kept for historical audit readability, for instance. With levels
gone, "part of a bundle" means *part of a role's set of grants*, and nothing else bundles.

### `applies_to`: where a code may be granted, and when that is asked

**This column is your own observation written as data:** `event.create` and `membership.manage` are
nonsense *on* an event. `unit` means the code may be granted at the unit and nowhere else;
`unit_and_item` means it may be granted at the unit or on one item of a registered type.

**It is checked when the grant is saved, not when a permission is checked**
([D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)).
A grant of `event.create` written on one event is **refused, with the reason in the error**: an
event cannot be created twice, so a creation permission attached to a thing that already exists
answers no question — and a refusal at save time is one human conversation, where the same shape
discovered at check time is a rule inside the resolver that every future reader has to re-derive.

**What enforces it is the write path, and the direction of its failure is worth knowing.** No
database rule spans `permission` and `access_grant` columns, so integrity check 3 (§11) reports any
row that got through — a row there means the check was skipped, not that a constraint was
disabled. And because the rule sits on the save, **a *check* that names an item for a unit-only code
is not refused by it**: the mismatched shape cannot be stored, so the check simply gets the unit's
answer. That is a caller bug rather than a data bug, and §13 registers the question of whether the
API should refuse it out loud.

### `right_kind`: a column with exactly one customer

**Saying so is cheaper than discovering it later**
([D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)).
[D-074](../decisions/round-06.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular)
fixes a guardian's rights at three values — `none`, `view`, `write` — and with the level ladder gone
the guardianship channel had nothing left to compare a checked permission against. This column is
that thing, and it has no other consumer anywhere in the design:

| Guardian's `right_level` | Covers |
|---|---|
| `none` | Nothing. |
| `view` | Codes marked `read`. |
| `write` | Codes marked `read` **and** codes marked `write`. |

**The alternative was to store permission codes on the guardianship row, and D-074 refused it on
the grounds that a volunteer cannot maintain a 74-code checklist per child.** A two-valued column
on the *catalog* side keeps that refusal intact: the organization grades each code once, when it is
written, rather than per child, forever.

**A new code is seeded `write` unless someone marks it `read`,** because `write` is the narrower
guardian reach: an unconsidered new code is then unreachable by a guardian with `view`, which is
the direction this model fails in everywhere else. This is a seeding convention derived from
D-074's fail-closed posture rather than a ruling in D-099, and §11 has no check for it — a code
mis-marked `read` is visible to a human reading the catalog and invisible to the database, which is
worth knowing before trusting it.

### What `namespace` does now, and what it no longer does

| `namespace` | What it means | Example |
|-------------|---------------|---------|
| absent | An ordinary code. | `membership.request.approve` |
| `system` | A code about the system itself. It is **seeded `applies_to = unit`**, so no grant on an item can carry it, and the resolver no longer branches on the prefix. | `system.permission.edit` |

There used to be a third value, and this subsection was about it. `dependent.` prefixed every
guardian capability, and the resolver dispatched on the prefix: a code beginning `dependent.`
went down the guardianship channel, everything else went down the ordinary path.
**[D-074](../decisions/round-06.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular)
deleted all eighteen of those codes,** and with them the only thing the namespace column was
being used to route on.

**So the namespace column no longer selects a channel, and the guardianship channel is now
selected by something the namespace could never express: whether the action is about a
different person from the one performing it.** A parent editing their child's address is checked
under `person.address.edit` — an ordinary, un-prefixed code — and reaches the guardianship
channel anyway, because the subject of the act is not the actor. See §10. The old prefix rule
silently missed exactly that case: a guardian acting under a `person.*` code looked like a
person acting on themselves.

**What the column was *also* guaranteeing, and who guarantees it now.** The surviving sentence in
the old design read "a `system.` permission is resolved against role assignments and never against
an item grant", and it was load-bearing: no one could hand someone authority over the permission
system by sharing an item with them. **Its mechanism died twice over** — there is no role channel
(D-100) and no item-scope path it needs excluding, because `applies_to = unit` already refuses the
grant at save time. So the guarantee survives **as a seeding rule plus integrity check 3**, and the
layer is named because the difference matters: it is no longer structural, and a `system.` code
seeded `unit_and_item` by someone in a hurry would put the old hole back with nothing in the schema
to catch it. A new namespace remains a data change rather than a resolver branch; it just has one
tenant and no routing left.

---

## 3. `role` — an office

**Fields**

| Field | Kind | Notes |
|---|---|---|
| `id` | integer identity | Surrogate key. |
| `code` | text, required, unique among roles, **and unique across roles and groups** | `registrar`, `treasurers`, `counselors`. The cross-table half of the rule is §8's namespace rule; a single constraint cannot span two tables, so the write path carries it (§8, *Names are one namespace*). |
| `name` | text, required | What the office is called on screen. |
| `description` | text, optional | |
| `is_system` | boolean | Default false. True: seeded — cannot be **deleted**, and its `code` cannot be changed. False: an ordinary office the organization created and may delete. |
| `sort_order` | integer, required | Default 0. |
| `created_at` | timestamp, audit time | |
| `updated_at` | timestamp, audit time | |
| `updated_by` | reference to person | Who last changed it. |

**Deleted with their mechanisms, in one list, because D-081 requires each one to be answered:**

| Gone | With it | Who answers the question now |
|---|---|---|
| `scope_required` | "is this office held org-wide or at a unit?" | Nobody — the question has no subject. [D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row) left one scope, so a role is always held at the unit (§4 has no scope columns). |
| `requires_membership` | the membership gate, default-on, enforced in the resolver ([D-039](../decisions/round-02-03.md#d-039--member-permissions-require-a-current-paid-membership)) | **The expression**, per grant: `MEMBERS * ROLE(x)` gates on a current membership, `ROLE(x)` alone does not (§8, §10). The posture reversed from default-on to opt-in, and §11's report is the control. |
| `max_term_months` | the prefilled term, and with it the "expiry is the default" nudge | Nothing. Nothing forces a holder row to end and the report is the control (§4, [D-071](../decisions/round-05.md#d-071--nothing-forces-a-role-assignment-to-end-the-gate-and-the-report-are-the-control)); the prefilled date was doing a job the report also does, and it went with the scope columns it was calibrated against. |
| `is_delegatable` | the refusal to let an office's authority be delegated ([domain/06 §9](../domain/06-authorization-model.md#9-delegation)) | Nothing about roles. Delegation of *authority* survives only on a grant row (`is_delegated` + `delegated_from`), where the grant's own expiry is the control (§6). |

**`role` is runtime data, not a fixed vocabulary.** The organization creates offices, names them,
fills them, and deletes the ones nobody ever held. Two rows ship with the platform, and the list is
deliberately short: `counselors`, marked `is_system`
([D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape);
a permanent, organization-wide population is the opposite of D-098's definition of a group, and the
table is what decides the sensitivity that protects the set). §12 states what is seeded and what is
starter material.

> **`role` has no `valid_from` / `valid_to`, deliberately** ([D-053](../decisions/round-04.md#d-053--a-role-is-valid-always-only-its-assignment-is-temporal)).
> A role is a **definition** — a named office — and a definition does not come into and out of
> force. It is valid all the time, for as long as the row exists.
>
> **The period belongs on the holder row.** `role_holder.valid_from` / `valid_to` is where "this
> person holds this office from March until December" lives (§4). The distinction is between *what
> the office is* and *who holds it*: the first is not a historical fact, the second is.
>
> This removes the whole retirement mechanism. There is no `role.retire` permission, no resolver
> check on the role's period, and no report of roles expiring while still held. A role the
> organization no longer uses is one nobody holds any more.

### `role_permission` is deleted, and the office confers nothing

**The codes an office carries are the live grants whose audience names `ROLE(x)`**
([D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)).
That is not a relabelling; it moves the definition of an office's power out of a bundle table and
into grant rows that are individually visible, individually dated, individually auditable, and
individually revocable. What it buys is the question the old design could not answer cleanly —
*"what may a treasurer do?"* — which is now a query over rows a screen can show rather than a walk
through a table nobody reads. This is where
[D-068](../decisions/round-05.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle)
was already going — *roles are the bundle*, said of `<resource>.admin` — and it went the rest of
the way: **roles and audiences are the bundle, and nothing else is.**

**Three things the old section argued, and where each stands:**

- ~~**"Editing a role's permissions takes effect immediately, and that is the sharpest edge in the
  whole authorization system."**~~ **Withdrawn by D-100, and the de-escalation is worth naming
  rather than skipping.** `role.edit` used to be a bulk privilege change wearing the clothes of a
  configuration screen, defended only by the audit trail because there was nothing to check before
  the fact. It now edits a name, a description and a sort order. **The sharp edge moved to
  `role.assign`**: adding one person to `treasurers` inherits *every* grant that names
  `ROLE(treasurers)`, including ones written later, by other people, for reasons the person doing
  the assigning has never seen. That is the same invisibility §8 records for composition, arriving
  through the office door instead of the expression door, and it is why `role.*` stays the most
  sensitive code family in the catalog (🔒🔒) and why §11's report of `ROLE(...)` grants written
  without `MEMBERS` is worth reading.
- ~~**"A role that has ever been assigned cannot be deleted."**~~ **Same rule, new table, same three
  reasons** — `role_holder.role_id` is a foreign key and D-003 forbids taking the history with the
  row; "what authority did this person have in 2019?" must survive the office being abolished, which
  is exactly when someone asks; and an `is_system` role must survive regardless, because deleting the
  row some grants name would silently widen or narrow whatever they aim at. The guard runs row by
  row, in this order, and both refusals are absolute:
  1. any `role_holder` row references the role — refuse, with a message in terms the operator can act
     on: this office has holders, end the holder rows instead, so the history survives;
  2. otherwise, `is_system` — refuse outright.
  A role that clears both was created by mistake and never held, and deleting it is legitimate.
- ~~**"No permission inheritance between roles."**~~ **Kept, because the reason was never about
  bundles.** A `unit_leader` does not get the `assistant_leader` permissions by being implicitly
  senior: inheritance chains produce authorization answers nobody can predict by reading the
  configuration, which is what makes such systems undebuggable. Composition is available and is
  visible instead — an expression says `ROLE(x) + ROLE(y)`, in the grant, where whoever reads the
  grant sees it (§8).

**`role` is registered in `grant_scope_type`, so an office is an item**
([D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)):
*"these two people may manage the counselors roster"* is a grant of `role.assign` on one role, which
is [D-098](../decisions/round-10a.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority)'s
move applied symmetrically. Without it the only way to say that is a grant at the unit, which
reaches every office — the exact over-reach this table's sensitivity exists to avoid.

**Why a role and a group are two tables when they are technically the same shape** is answered where
the difference bites — [D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)
puts it in one line: **the difference decides who may edit the membership, and one table would merge
those two permissions into one.** `role.*` is the most sensitive family in the catalog (🔒🔒);
writing a group's roster is `person_group.member.manage` (⚠). One table with a `kind` column gives a
single code that both adds a child to the Thursday group and puts the holder into the office whose
grants reach everything. The groups themselves are `person_group`, in
[02-organization.md](02-organization.md#1-person_group) — this document describes only the selector
that reads them.

---

## 4. `role_holder` — who holds an office

`role_assignment` **becomes `role_holder`**
([D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)).
The rename is the small half; the deletion of its scope columns and of the resolver's role channel
is the half that changes how an authorization question gets answered (§10).

**Fields**

| Field | Kind | Notes |
|---|---|---|
| `id` | integer identity | Surrogate key. |
| `person_id` | reference to person, required | Who holds the office. **One person, never a rule** — [F-12](../open-questions.md#f-12--closed--may-a-role-be-held-by-a-rule-as-an-audience-is) is closed by D-100 and its answer is no, for the reason the register always gave: a derived holder list cannot answer "who was treasurer in 2023", and an office record that cannot answer that is not an office record. |
| `role_id` | reference to `role`, required | |
| `valid_from` | date, required | Default today. |
| `valid_to` | date, optional | Absent = open-ended. **Nothing forces it to end** — see below. |
| `granted_by` | reference to **person**, required | **Who appointed this person.** Kept, and *not* the provenance column this section deletes elsewhere — see *What `granted_by` records and what `audit_log` records*, immediately below. **The arrow of this column goes to `person` and never to `audit_log`**: it is a fact about the holder row, readable by anyone who may read the office, and reconstructing it from the trail would put the answer behind `audit.view`. |
| `granted_at` | timestamp, audit time | Set when the row was written. Redundant with `created_at` in the ordinary case and kept because an appointment can be entered retrospectively, which is the only case where the two differ and the one where the distinction matters. |
| `note` | text, optional | Why, in the writer's words. The only place the reason survives the audit trail's payload window ([D-088](../decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)). |
| `created_at` | timestamp, audit time | |
| `updated_at` | timestamp, audit time | |
| `updated_by` | reference to person | |

**Gone with the table's rename:** `scope_type` and `scope_id`
([D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row) —
"a role is always held at the unit; there is nothing else to hold it at"), `delegation_of` and the
re-validation of a delegation's source (§10), and the `ended_by` / `ended_at` /
`ended_reason_code` / `ended_note` quartet. **The last of those needs its "who answers now",**
because it is history, not configuration: the audit trail records who closed a holder row and when,
which is the same question the columns answered, and `note` carries the *why* on the row that opens.
What is genuinely lost is the typed reason code — a `ended_reason_code` vocabulary that could be
counted. Nothing counted it, and D-098 refused the same shape one table over for the same reason:
eighteen ticks without a receipt.

**What `granted_by` records, and what `audit_log` records — the distinction that keeps one column and
deletes four.** The two look like duplicates and are answers to different questions, and this section
initially got it wrong in the direction of deleting too much, so the line is worth drawing properly.
`audit_log` records **an act**: that a particular person, in a particular session, from a particular
address, asked to appoint someone, and whether they were allowed to. It is the record of the *writing*.
`granted_by` records **a fact about the row**: who appointed this person, which is a property of the
office holding in the same way `valid_from` is. *Who is entitled to say* is the audit's question;
*who said it* is the row's.

**Two reasons the fact cannot live only in the trail, and the first is decisive.**

- **The trail's payloads do not last** ([D-088](../decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short));
  the before-and-after images are emptied after 24 months. **"Who put her in charge of the money?" has
  to be answerable in year five**, from the same screen that shows when the appointment started, and an
  answer that requires `audit.view`, a date range and an intact payload is not an answer to a question
  about the current officer.
- **The row's readers are not the trail's readers.** `role_holder` is read by whoever administers
  offices; the trail is read by whoever holds `audit.view` 🔒🔒, and
  [D-086](../decisions/round-07-08.md#d-086--a-sensitivity-mark-grades-what-a-grant-exposes-not-the-table-it-reads)
  graded that deliberately. Making the ordinary screen reach into the audit trail to show an ordinary
  field either widens `audit.view` or leaves the field blank, and neither is acceptable.

**The same argument already decides `access_grant.granted_by` the same way, and nobody proposes
reconstructing that one from the trail** — which is the tell that this is a pattern rather than a
local call, and the reason `ended_by` / `ended_at` / `ended_reason_code` / `ended_note` can be deleted
while `granted_by` cannot. **What separates them is not "an actor column" versus "a provenance column";
it is whether the value is a property of the row that still exists.** An ending describes a row that
nobody is looking at any more, and the question "who closed this" is a question about an act, which is
the trail's subject. An appointment describes a holding somebody is looking at right now. **Consistency
here is about which question is being asked, not about how many actor columns a table has.**

**And one consequence for the diagram, because it was got wrong once.** The relationship drawn from
`granted_by` points at `person`. There is no edge from `role_holder` to `audit_log` and there must never
be one: the trail is written *about* the act, by the same transaction, and it is not something the
holder row refers to or depends on.

**Rules**

- `valid_to` is either absent or strictly after `valid_from`.
- **At most one open holder row for a given person and role.** There is no scope term left to
  distinguish two concurrent holdings, because there is no second scope. A person may have been
  treasurer three times, and be treasurer once.
- **Rows for the same person and role may not overlap, counted over all rows and not only the open
  ones**, half-open so a row ending on a day and one beginning that same day do not collide. Dating
  rows imports this invariant set whether the author wants it or not — it is D-098's argument for
  the identical rule on `person_group_member`, [D-002](../decisions/round-01a.md#d-002--everything-temporal-is-a-period-never-a-boolean),
  and [F-10 shape 1](../open-questions.md#f-10--which-invariants-the-orm-cannot-express-and-who-writes-those),
  which says a hand-written migration must emit it and the ORM will not.
- **A person who left the office in 2020 and returned in 2024 is two rows, never one row edited in
  place**, because the edit destroys the answer to "was she treasurer in 2019?" — and that is the
  question this table exists to answer. Moving from one office to another closes one row and opens
  another.

**Indexes**

- over open rows only, by role — the read that answers "who is in `ROLE(treasurers)` today", which
  is now an operand of a grant rather than a tier of the resolver, and runs on every check that
  names the office;
- over open rows only, by person — the read that answers "what offices does this person hold", for
  the screen where someone is about to be given one more.

### Nothing forces a holder row to end, and the report is the control

This is [D-071](../decisions/round-05.md#d-071--nothing-forces-a-role-assignment-to-end-the-gate-and-the-report-are-the-control)'s
posture, transferred intact to `role_holder`, and the transfer is honest only because the gate it
used to lean on is gone. The old argument ran: nothing forces an assignment to end, **but the
membership gate means a lapse silently withholds it anyway**, so the leaver-with-access report was
tidying rather than defending. **That second half no longer exists.** A holder row that nobody
closes now authorizes for as long as a grant naming the office lives, and the only thing between an
overdue treasurer and a written authority is:

- **the report** — open holder rows, oldest first, with the grants each office is named by, which is
  the same reading that used to be "assignments that should have been closed and were not";
- **`role_holder.valid_to` where a human typed one**, and §13 keeps the question of whether it
  should be mandatory for high-authority offices; and
- **the audience expression**, which is where a lapse now matters: `MEMBERS * ROLE(x)` stops
  reaching a lapsed member the day the membership ends, and `ROLE(x)` never noticed.

**The second failure mode is the one D-100 named rather than buried, and it is the mirror image of
the first.** A holder row that outlives the person is a person with authority they should not have;
a **grant** written as `ROLE(x)` with no `MEMBERS` authorizes a lapsed member silently, forever, and
fails closed-looking so nobody notices. Integrity check 6 (§11) is the standing report of exactly
that shape, and the seeded grants carry `MEMBERS` so that the path of least repetition is the safe
path.

---

## 5. `scope_exposure` — deleted by D-097

**This section is deleted.** Its number is kept so that §6 and onward keep the anchors other pages
link to, and its content is not replaced by anything: this is the one place in this document where
the honest summary is *lost, not replaced*.

**What the table was.** `scope_exposure` was the only mechanism by which authority crossed a unit
boundary downward, and it existed to implement
[D-031](../decisions/round-02-03.md#d-031--no-downward-inheritance-of-authority-scope_exposure-is-the-only-crossing)
— *authority over a unit originates at that unit and cannot be claimed from outside it*. The row was
keyed on the **covered** unit, which made the covered unit the grantor, and pointed at a specific
**assignment** rather than a role, so a unit approved a person-in-a-role rather than a role that any
future holder would inherit. `scope.expose` was deliberately a narrow code with no wildcard above
it, because "may administer this unit" silently including "may hand a parent unit authority over
this unit's records" was, in the words of the section that shipped it, the single most consequential
act available at unit scope carried as an implication.

**What it protected, in the one sentence worth keeping.** Access to a pack's children had to be
granted **by that pack** — by people who recruited the leader, who can be asked, and who chose the
person being let in. **That property is gone and nothing in the remaining model reproduces it**
([D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)).
A permission held at the unit reaches every member, and `person.view` was already the widest read
permission in the system
([D-083](../decisions/round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data),
[D-086](../decisions/round-07-08.md#d-086--a-sensitivity-mark-grades-what-a-grant-exposes-not-the-table-it-reads)).
What is left of the safeguarding story is the same three things D-095 was left with — a permission
held by a named adult, an audit trail whose payloads expire after two years
([D-088](../decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)),
and a report of who holds the write — **minus the part where the named adult was somebody the body
chose.**

**Why there is no replacement, rather than an unfinished one.** With one unit there is no "outside
it" to be stopped from: every permission is held either at the unit or on an item, and the unit's
people are the only people there are. A mechanism that lets a subordinate grant access to itself has
no subordinate to run it. The route back is a decision with a reason attached — most plausibly "the
organization has grown past one center's visibility" — and that decision would have to re-argue D-031
from its own premises, because the table that made it work no longer exists.

**Deleted along with the table, each with who answers it now.** `scope.expose` and
`scope.exposure.review` leave the catalog; the direction-of-authority check leaves the write path,
and nothing replaces it because there is no direction left for a row to have; the nightly exposure
alert leaves the schedule, and it was that check's **only** detector — which is worth remembering as
a shape rather than this table's fate: a write-path rule with a report as its only guard, and a
report that stops running, is a rule that quietly stops existing. `org_unit`, `unit_participation`,
`unit_ancestors()` and `unit_descendants()` are gone with the hierarchy, and so is every rule about
paths, depths, nesting, and reparenting (the whole of [data-model/02-organization.md](02-organization.md)
now describes groups).

**One lesson outlives its subject, and it is kept here because it is the corpus's best argument for
reviewing prose rather than code.** Until D-072 deleted the SQL, the unit-grant tier carried a
*second* branch that looked like it consulted exposures. It did not: it pinned the grant to the unit
being checked, which the branch above had just tested, so it could never succeed where the first
branch failed. **It was dead code, and it had survived every review because it read correctly.**
Nothing here changes what the system decided — a dead branch decides nothing — but the reason the
prose said two routes when one existed, and the fact that removing the SQL is what surfaced it, is
the reason this document states one route for everything it describes and says why a tempting second
one is absent. See [D-078](../decisions/round-06.md#d-078--an-exposure-extends-an-assignment-never-a-direct-grant),
whose rule — an exposure extends an assignment, never a grant — now has no subject: nothing extends
a holder row at all, because a holder row has no scope to extend.

---

## 6. `access_grant` — the per-item layer

This is the "per-item permission" table. You specified it means a **capability on that
item**: "person X may act on item Y". **After round 10 it is also the unit-level table**, because
the unit is now one of the scope types rather than a different kind of thing, and there is no other
grant table to hold the difference. **The heading is deliberately unchanged** — it names only half
of what the table is now, and it is kept because pages across the corpus and in the decision log
link to this anchor.

**One grant is: a grantee, a scope, one permission code, an effect, and a period**
([D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)).

**Fields** (`grant_scope_type`)

| Field | Kind | Notes |
|---|---|---|
| `code` | text, required, unique | `unit`, `event`, `person_group`, `role`, `document`. The key a grant points at. |
| `name` | text, required | |
| `item_table` | text, required | The table `scope_id` references — `event`. For the unit, nothing: the row exists so the scope type has a name, and `is_item_scoped` is what says so. |
| `is_item_scoped` | boolean | Default true. **False for exactly one row: `unit`.** A grant at a non-item scope has no `scope_id`, and that single fact is what "the unit is a scope, not a row" means in the schema ([D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)). |
| `description` | text, optional | |

**Seeded rows**, and the list is short on purpose:

| `code` | Item-scoped | Means |
|---|---|---|
| `unit` | **No** | The organization. There is exactly one, and it is not a row anywhere else. |
| `event` | Yes | One event. Nothing owns it ([D-102](../decisions/round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)); a unit grant reaches every event and an event grant reaches one. |
| `person_group` | Yes | One group ([D-098](../decisions/round-10a.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority)) — how "these two may work this group's roster" is said without inventing a scope. |
| `role` | Yes | One office ([D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)) — the same move applied symmetrically. |
| `document` | Yes | Deferred; a document layer still to be designed. It stays in the registry because the registry's whole point is that a new grantable thing is a row here rather than a migration. |

**`supports_levels` is deleted with the ladder, and so are the `organization` and `org_unit` rows:**
the first is `unit` renamed (a scope with no item under it, which is all it ever was), the second is
deleted with the hierarchy. **`membership` is not in the seed.** Nothing in this design writes a
grant on an individual membership row — the thing a membership is protected by is `membership.*`
codes held at the unit — and if that ever changes, adding it is one row here, which is what the
registry is for. That the row is gone rather than merely unused is an inference from D-097's and
D-099's lists of what is seeded, and §13 records it as one.

**Rules** (`grant_scope_type`)

- Every `access_grant.scope_type` names a row here. This is the one piece of referential
  integrity the polymorphic scope does get.
- Exactly one row — `unit` — has `is_item_scoped` false.

**Fields** (`access_grant`)

| Field | Kind | Notes |
|---|---|---|
| `id` | integer identity | Surrogate key. |
| `person_id` | reference to person, optional | The grantee, when the grant names one person. |
| `audience_id` | reference to `audience`, optional | The grantee, when the grant names a set (§8). Evaluated against the person being checked, per person, as a predicate — never as a list of ids. |
| `scope_type` | reference to `grant_scope_type`, required | `unit`, or an item type. |
| `scope_id` | integer, optional | The concrete item id. **Absent exactly when the scope type is not item-scoped** — that is, exactly at `unit`. **No foreign key: polymorphic by design.** See the note below. |
| `permission_id` | reference to `permission`, required | **One code, not a bundle** ([D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)). What `level` used to stand in for, without the ladder. |
| `effect` | enum: `allow`, `deny`, required | **Allowed iff some live allow applies and no live deny applies.** [D-013](../decisions/round-01a.md#d-013--explicit-deny-revoked-is-checked-before-everything)'s deny survives as an effect on a row rather than as a level called `revoked`, and its reason for existing is unchanged: a court-ordered restriction must not be beatable by a broader grant. |
| `valid_from` | date, required | Default today. |
| `valid_to` | date, optional | Absent = open. Discouraged; see below. |
| `is_delegated` | boolean | Default false. |
| `delegated_from` | reference to person, optional | The person whose authority this delegation carries. |
| `granted_by` | reference to person, required | |
| `granted_at` | timestamp, audit time | |
| `grant_reason` | text, optional | |
| `revoked_by` | reference to person, optional | |
| `revoked_at` | timestamp, audit time, optional | |
| `revoke_reason` | text, optional | |
| `created_at` | timestamp, audit time | |
| `updated_at` | timestamp, audit time | |
| `updated_by` | reference to person | |

**Rules**

- Exactly one of `person_id` and `audience_id` is set. A grant to neither is meaningless; a
  grant to both would be ambiguous — any person in the audience, or only this one?
- `valid_to` is either absent or strictly after `valid_from`.
- `scope_id` is absent exactly at `unit` scope — and that is the whole of what the rule says. It
  constrains the absent case alone; `grant_scope_type.item_table` is what states which table an id
  belongs to.
- `effect` is `allow` or `deny`. There is no third value and no ordering between them: **deny is
  absolute and is checked first**, which is [D-032](../decisions/round-02-03.md#d-032--deny-is-absolute-locality-orders-allows-only)
  entire surviving content.
- **`permission_id` names a permission whose `applies_to` permits this scope shape** — a grant at an
  item requires `unit_and_item`. Refused at save with the reason (§2, *`applies_to`*).
- `is_delegated` and `delegated_from` agree in both directions: the flag is true exactly when a
  delegating person is named.
- A grant is never a delegation from the person it is granted to: `delegated_from` does not
  equal `person_id`.
- A revocation names who made it: if `revoked_at` is set, `revoked_by` is set.
- **A delegation must expire:** if `is_delegated` is true, `valid_to` is set. With `delegation_of`
  deleted (§4) this is the *only* remaining guard against a delegation outliving its reason — the
  old second half, re-validating a source assignment at check time, has no assignment to
  re-validate. Integrity check 11 (§11) reports an open-ended one.
- **An audience grant cannot be delegated.** `is_delegated` requires `delegated_from`, which is a
  person, and delegating "everyone" is not a coherent act: if `audience_id` is set, `is_delegated`
  is false.

### Inheritance, stated once

**A grant at the unit reaches every item of every type.** A grant on one item reaches that item and
nothing else. That is the whole of it
([D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)),
and it follows from two deletions rather than from a new rule: after
[D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)
there is no intermediate scope left between the unit and an item, and after
[D-102](../decisions/round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)
there is no ownership relation to test.

**This is [D-006](../decisions/round-01a.md#d-006--per-item-permissions-are-capabilities-on-the-item)
with the unit tier left standing** — per-item permissions are capabilities on the item — and it
deletes `can_event()` outright, along with the unit-authority rule that nearly every event
permission in this corpus was reached through. **What that rule was doing, so that its absence is
noted rather than assumed:** it asked whether the actor had authority over the event's owning unit
before honouring an event grant. There is no owning unit, so there is nothing to ask, and the
question "who is connected to this event?" is answered by the operands of §8's language instead —
`ORGANIZERS`, `PLACED`, `CONFIRMED` — each of which is a set the item itself defines.

**A unit grant of `system.admin` therefore reaches everywhere on its own.** The old resolver needed
a special clause for that ("`system.admin` qualifies whatever the checked scope is"); it existed
because organization scope and unit scope were different tiers. With one unit scope and plain
inheritance, the clause has nothing to fix.

### The uniqueness rule has to be careful with audiences

The obvious index — one live grant per (grantee, scope) — never worked, because a person can
legitimately hold a **personal** grant *and* be covered by an **audience** grant on the same item,
and those are different rows with different lifetimes. **Round 10 adds a second reason it cannot
work: one code per row, so one person legitimately holds a dozen live allows on one item.**
A broad office is a couple of dozen rows
([D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)),
each a different code, and a rule that permitted one live grant per grantee and item would refuse
the second of them.

**Rules**

- **At most one live allow per (grantee, scope, permission)** — counted over the rows that name a
  person and are open, unrevoked, and `effect = allow`.
- **At most one live allow per (audience, scope, permission)**, counted the same way over the rows
  that name an audience.
- A person and an audience are **different grantees**, so the same code on the same item may exist
  once for the person and once for a set they are in. It grants nothing extra and it is not an
  error; it is two people's decisions about the same capability, which is what the grantee pair has
  always meant.

**Indexes**

- person, audience and scope lookups, each restricted to open rows;
- **a deny-only index over open rows with `effect = deny`, keyed by grantee, scope and permission** —
  the deny lookup runs on every check, at every scope, and it is the first thing the resolver does.

**Denies are excluded from both unique indexes**, so a deny may coexist with an allow on the same
grantee, scope and code — which is exactly what makes an explicit deny meaningful. A **personal deny
beats an audience allow**, because the deny check runs first and is scope-independent (§10).

### `effect`, and why a `-` in an expression is not a deny

**Two mechanisms that both subtract, and are not interchangeable**
([D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)):

| | `effect = deny` | `-` in an audience expression |
|---|---|---|
| Narrows | **Every grant** that applies to the person, including ones written elsewhere, later, or by somebody else | **One grant's** reach |
| Says | "she must not have this, whatever else she is given" | "this grant is not for the people in that set" |
| Beatable by | Nothing. Checked first, absolute, scope-independent | Yes — any other grant that reaches her |
| Lives on | A grant row | An operand of the grant's audience (§8) |

**The first cannot be expressed by the second, which is why denies stay** — that is
[D-013](../decisions/round-01a.md#d-013--explicit-deny-revoked-is-checked-before-everything)'s whole
reason for existing. **And denies are legal at the unit as well as on an item**, since "exclude her
from what the unit grants everyone" is exactly the case an expression cannot serve: subtracting her
from one grant leaves every other grant aimed at the same set intact.

**A deny is a real row and can therefore be wrong in a way an allow cannot be.** A live deny whose
grantee, scope and code match no live allow is dead weight, and a deny that denies nothing is how a
stale restriction survives its reason — integrity check 5 (§11) reports the shape, as D-099 requires.

### Live-grant uniqueness excludes denies — deliberately

A deny must be able to coexist with an allow on the same scope, because that is the only way to
express "this person has access to the unit's events, except this one". So the rule that keeps one
live grant per grantee, item and code — carried here as `uq_access_grant_live` — **covers allows
only**; a `deny` row is outside it by design, and the resolver checks denies first.

**This is the rule's shape, not an implementation detail of an index** ([D-072](../decisions/round-06.md#d-072--the-documentation-carries-no-sql-the-schema-is-the-orms-job)),
and the distinction is load-bearing here rather than pedantic: "unique among live **allowing**
grants" is a **conditional** rule, so the migration must emit a partial unique index whose
predicate excludes `deny`. A plain unique constraint over the same columns is a different and wrong
rule — it would refuse the deny beside the allow, which is precisely the pair the domain requires.
See [open question F-10, shape 2](../open-questions.md#f-10--which-invariants-the-orm-cannot-express-and-who-writes-those).

**The condition also excludes `revoked_at`, which is easy to write wrongly in the other direction.**
A revoked grant must not occupy the unique slot — that is what lets a grant be revoked and re-made
rather than edited. So the predicate is "open *and* unrevoked *and* `allow`", three tests, and a
partial index that gets one of them wrong is invisible until the day someone cannot save a grant
they should be able to.

### What is refused when a grant is saved

**Five checks, one transaction, each with the layer named** — because none of them is a database
rule, and D-081 forbids writing them as if one were:

1. **The code may be granted at this scope.** `permission.applies_to` permits the scope shape
   (§2). Refused with the reason in the message, per D-099's example: a grant of `event.create` on
   one event is refused because an event cannot be created twice.
2. **The code is assignable.** `is_assignable` is true (§2's deprecated-code case).
3. **Every bound operand in the grant's audience may bind here.** An operand whose
   `selector_type.binds_to_item` is true is legal **only** on an item-scope grant, and only where
   `selector_type.argument_type` matches that grant's item type. `PLACED` on a `person_group` grant
   is refused because that item is not an event; `ORGANIZERS` on a `unit` grant is refused because
   at the unit there is nothing to bind it to, **with the operand named in the message**
   ([D-102](../decisions/round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)).
4. **The audience's expression is well-formed and acyclic** (§8) — **and "acyclic" is measured over
   the expanded tree, so this check follows the `AUDIENCE` leaves into the audiences this one names**
   ([D-103](../decisions/round-10b.md#d-103--an-audience-may-name-another-audience)). Saving a grant
   is not where a cycle is *created*, but it is where a person is standing to be told about one, and a
   grant must never be saved pointing at an expression that cannot be evaluated. **There is no longer
   a depth limit to check here:** the height bound was deleted along with its parameter
   ([D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)),
   so this check carries no size rule at all and the cycle walk is the only structural refusal left
   in it.
5. **Every `AUDIENCE` leaf names an audience that exists and that has a `code`** (D-103). Both halves
   read a second table, so neither is a constraint on this row: the dangling case is the orphan check
   of §11 item 2, and the null-code case is that item's neighbour in item 12. **A leaf pointing at an
   unnamed audience is refused rather than resolved-at-read**, because resolving it later would make a
   grant's reach depend on whether somebody had typed a code into a different screen.

**Why the save path and not the check path, said once for all five.** A grant that cannot mean
anything is a data-entry mistake, and a data-entry mistake is refused where the person making it is
standing. The resolver's job in the same situation is the opposite and is already fixed: an operand
that does not resolve is the empty set, so anything that slips past these checks denies rather
than widens (§8, *Evaluation*) — **except through `-`, where an empty operand widens, which is why
these are refusals and not warnings.** Checks 3 and 4 (§11) report what got through, and a row there
means the write path was skipped — there is no constraint to have disabled.

**A sixth refusal lives on the other screen.** Ending or deleting an *audience* is refused while a live
grant, or a live audience reachable from one, names it (§8, *Rules*). It is listed here only so that a
reader of this section does not conclude the grant save is the whole write path.

### No foreign key on `scope_id` — the accepted trade-off

`scope_id` has no FK because it is polymorphic. This is a deliberate choice, and
[D-101](../decisions/round-10b.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree)
extended it to `audience_operand.selector_arg_id`, which is polymorphic for the same reason and
takes the same four mitigations:

| | Polymorphic `scope_id` | `grantable_item` supertable |
|---|---|---|
| **Adding a grantable type** | One row in `grant_scope_type` | New table + FK from supertable + migration |
| **Referential integrity** | None — can point at a deleted item | Full |
| **Query cost** | Direct | Requires a join |
| **Risk** | Orphaned grants after an item is deleted | Migration churn on every new feature |

Polymorphism is what makes a new grantable thing — an event, a group, an office, a document that
does not exist yet — **a configuration row rather than a schema change**, which matters a great deal
given how much of this system is not yet specified.

The mitigations are mandatory, not optional:

1. `grant_scope_type` validates the `scope_type` value (FK above).
2. Deleting an item must close its grants — an application obligation, and tested.
3. A **nightly orphan check** per scope type, and the same scan over `selector_arg_id` (§11, check 2).
4. `scope_id` is `BIGINT` and ids are never reused.

**To overrule this**, add a `grantable_item(id, item_type)` supertable and give every
grantable entity an FK to it. Tracked in
[../open-questions.md](../open-questions.md) — it is a real fork and worth a deliberate
decision.

### Why `valid_to` is discouraged here too

An item grant is typically for one event, so an open-ended item grant is nearly always a mistake.
**Application validation should require `valid_to` for item-scoped grants**, with
`access_grant.grant_reason` explaining any exception — and the sentence has to stay an application
rule, because [D-071](../decisions/round-05.md#d-071--nothing-forces-a-role-assignment-to-end-the-gate-and-the-report-are-the-control)'s
posture applies here too: nothing in the schema forces a grant to end, and the report of
long-lived open grants is the control. **What changed in round 10 is that the nudge lost its
machinery.** The prefilled term (`role.max_term_months`) is deleted, and the membership gate that
used to make a forgotten row harmless is deleted; a forgotten grant is now simply live.

---

## 7. `permission_level` — deleted by D-099

**This section, and the table it described, are deleted**
([D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)).
The number is kept so §8 onward keep their anchors.

**What the table was, and the one job it actually did.** `permission_level` mapped
(permission, scope type) → the level a grant had to reach for that permission at that scope kind. It
existed so that **one** `access_grant.level` could serve many codes without a hardcoded mapping in
application code, and its virtue was reviewability: without it, every permission check would need to
know its own level — a mapping in code, invisible to the organization, and impossible to review.
**"What does `manage` on an event actually let someone do?" was a query, and now there is no such
question to ask**, because there is no such word.

**Its two jobs moved to two columns on `permission` itself**, which is D-099's exact accounting:

| The table's job | Now |
|---|---|
| Which scope kinds this permission means anything at | `permission.applies_to` (§2), checked on save |
| How much of this permission a given grant carries | Nothing — a grant **is** one permission. Either the row exists or it does not |
| (and the comparison the level made possible) | `permission.right_kind`, used by exactly one channel: guardianship (§10) |

**What is genuinely lost, said once.** The ladder was a *bundle with a name*, and a bundle is
something you can ask a question about: `contribute` on this event, for this person, meant a
computable set of codes and the audit trail could say "she held `contribute`". Now the answer to
"what did she have in 2024?" is the set of grant rows that were live then, which is more precise and
less quotable. **A broad office is a couple of dozen rows, and that is the price of the question
*"what exactly does this person have?"*** — D-099 paid it deliberately, and
[D-068](../decisions/round-05.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle)
had already refused the same idea once when it deleted `<resource>.admin` and said *roles are the
bundle*. Round 9 was half the thought: **roles and audiences are the bundle, and nothing else is.**

**Levels can come back as names for sets of codes with no comparison defined** — which is what a
role already is, so no new mechanism would be needed to approximate one. A real ordering coming back
means re-importing this table, the rank rule
([D-012](../decisions/round-01a.md#d-012--status-strings-compare-by-rank-never-lexicographically)),
and locality's tie-break
([D-032](../decisions/round-02-03.md#d-032--deny-is-absolute-locality-orders-allows-only)'s deleted
half), all of which were deleted with their only consumers. **That is the two-way door, and it is
narrow on the ordering side and wide on the naming side.**

---
