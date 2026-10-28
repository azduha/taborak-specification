# Data Model — Authorization

`permission`, `role`, `role_holder`, `selector_type`, `audience`, `audience_operand`,
`audience_member`, `access_grant`, `access_log`.

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
audience_member ────────── the dated rows behind its `LIST` leaf — this audience's own
                          hand-typed list of people

guardianship_permission ── authority over a PERSON.     (04-relationships.md)
access_log ─────────────── what was decided, and by what authority.
```

**One table grants.** `access_grant` is the only place authority is written ([D-005](../decisions/decision-log.md#d-005--permissions-are-grants-never-derived-from-identity)),
plus one table over a single person: `guardianship_permission` (§10, channel guardianship).
**Everything else on this page decides *whom a grant reaches*, which has never been the same
thing** — a role holder, a group member and an audience operand are all sets of people, and being
in one is worth exactly what the grant aimed at it says. That sentence was already true of
audiences before this round; round 10 made it true of roles too, which is the whole of
[D-100](../decisions/decision-log.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape).

**And the rule that answers every check** ([D-099](../decisions/decision-log.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)):

> **allowed** when some live **allow** applies, and **no** live **deny** applies.

That is the entire precedence rule. "Live" means the row has started as of the checked date, has
not ended on it, and has not been revoked; "applies" is decided per channel in §10. There is no
level to reach, no rank to compare, and no nearer grant that beats a further one — the ladder and
locality were deleted in the same breath, because locality only ever ordered *allows* against each
other and a boolean answer has nothing to order. What survives of the old ordering is deny's
absoluteness, which was [D-032](../decisions/decision-log.md#d-032--deny-is-absolute-locality-orders-allows-only)'s
first half and is now its entire content.

> **The rule that used to govern all of these tables, and where it went.** This section opened
> with *"authority over a unit originates **at that unit** and cannot be claimed from outside it —
> not by a parent unit, and not by the organization"*, and named `scope_exposure` as the only
> crossing. **Withdrawn by [D-097](../decisions/decision-log.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row),
> and the withdrawal is precise: [D-031](../decisions/decision-log.md#d-031--no-downward-inheritance-of-authority-scope_exposure-is-the-only-crossing)
> was not weakened, it was deprived of its subject.** There is one unit, it is the organization,
> and it is not a row — so there is no "outside it" to be stopped from, and every permission is
> held either at the unit or on an item. The sentence is kept here, struck through in spirit,
> because a reader who arrives from an older draft will look for the rule and should find the reason
> it is gone rather than an empty space. **What of its reasoning still holds is carried by two
> things that were never about units: deny is absolute (§10), and the ownership and guardianship
> channels answer for a person rather than for a body.** What is lost is stated once in §5 and in
> D-097, and is not argued away there or here.

**The two tables that used to be one idea at two granularities, and what they are now.**
[D-010](../decisions/decision-log.md#d-010--role-assignments-and-access-grants-share-a-scope-model-and-a-resolver)
read `role_assignment` and `access_grant` as the same mechanism at different sizes and gave them a
shared scope model and a shared resolver. **Both halves are reversed** — the scope model because
[D-097](../decisions/decision-log.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)
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
([D-099](../decisions/decision-log.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)).
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
| `applies_to` | enum: `unit`, `unit_and_item` | **New, [D-099](../decisions/decision-log.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality).** Where this code may be granted at all: at the unit only, or at the unit *and* on an item. Checked **when the grant is saved**, never at check time — see *`applies_to`* below. |
| `right_kind` | enum: `read`, `write` | **New, [D-099](../decisions/decision-log.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality).** Exists for exactly one customer: the guardianship channel's `none` / `view` / `write` ([D-074](../decisions/decision-log.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular)). Say the one customer out loud — see *`right_kind`* below. |
| `namespace` | text, optional | `system`, or absent. What it still does, and what it stopped doing, is its own subsection below. |
| `description` | text, required | What it means, for whoever has to read it. |
| `display_name` | text, required | Human label for the permission editor. |
| `is_system` | boolean | Default false. True: seeded by the platform, cannot be deleted or have its `code` changed. |
| `is_assignable` | boolean | Default true. False: a permission **no grant may name directly** — a deprecated code kept only so historical audit rows still resolve to something readable. Before [D-068](../decisions/decision-log.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle) this also flagged wildcard `.admin` codes; there are none now. |
| `created_at` | timestamp, audit time | |

**Deleted from this table by round 10:** `requires_scope`. Its job — "a unit-level permission
cannot be granted organization-wide by mistake" — was about *which unit* a permission was held at,
and [D-097](../decisions/decision-log.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)
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
  ([D-074](../decisions/decision-log.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular))
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
[D-068](../decisions/decision-log.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle)**,
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
([D-099](../decisions/decision-log.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)).
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
([D-099](../decisions/decision-log.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)).
[D-074](../decisions/decision-log.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular)
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
**[D-074](../decisions/decision-log.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular)
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
| `scope_required` | "is this office held org-wide or at a unit?" | Nobody — the question has no subject. [D-097](../decisions/decision-log.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row) left one scope, so a role is always held at the unit (§4 has no scope columns). |
| `requires_membership` | the membership gate, default-on, enforced in the resolver ([D-039](../decisions/decision-log.md#d-039--member-permissions-require-a-current-paid-membership)) | **The expression**, per grant: `MEMBERS * ROLE(x)` gates on a current membership, `ROLE(x)` alone does not (§8, §10). The posture reversed from default-on to opt-in, and §11's report is the control. |
| `max_term_months` | the prefilled term, and with it the "expiry is the default" nudge | Nothing. Nothing forces a holder row to end and the report is the control (§4, [D-071](../decisions/decision-log.md#d-071--nothing-forces-a-role-assignment-to-end-the-gate-and-the-report-are-the-control)); the prefilled date was doing a job the report also does, and it went with the scope columns it was calibrated against. |
| `is_delegatable` | the refusal to let an office's authority be delegated ([domain/06 §9](../domain/06-authorization-model.md#9-delegation)) | Nothing about roles. Delegation of *authority* survives only on a grant row (`is_delegated` + `delegated_from`), where the grant's own expiry is the control (§6). |

**`role` is runtime data, not a fixed vocabulary.** The organization creates offices, names them,
fills them, and deletes the ones nobody ever held. Two rows ship with the platform, and the list is
deliberately short: `counselors`, marked `is_system`
([D-100](../decisions/decision-log.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape);
a permanent, organization-wide population is the opposite of D-098's definition of a group, and the
table is what decides the sensitivity that protects the set). §12 states what is seeded and what is
starter material.

> **`role` has no `valid_from` / `valid_to`, deliberately** ([D-053](../decisions/decision-log.md#d-053--a-role-is-valid-always-only-its-assignment-is-temporal)).
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
([D-100](../decisions/decision-log.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)).
That is not a relabelling; it moves the definition of an office's power out of a bundle table and
into grant rows that are individually visible, individually dated, individually auditable, and
individually revocable. What it buys is the question the old design could not answer cleanly —
*"what may a treasurer do?"* — which is now a query over rows a screen can show rather than a walk
through a table nobody reads. This is where
[D-068](../decisions/decision-log.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle)
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
([D-100](../decisions/decision-log.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)):
*"these two people may manage the counselors roster"* is a grant of `role.assign` on one role, which
is [D-098](../decisions/decision-log.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority)'s
move applied symmetrically. Without it the only way to say that is a grant at the unit, which
reaches every office — the exact over-reach this table's sensitivity exists to avoid.

**Why a role and a group are two tables when they are technically the same shape** is answered where
the difference bites — [D-100](../decisions/decision-log.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)
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
([D-100](../decisions/decision-log.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)).
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
| `note` | text, optional | Why, in the writer's words. The only place the reason survives the audit trail's payload window ([D-088](../decisions/decision-log.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)). |
| `created_at` | timestamp, audit time | |
| `updated_at` | timestamp, audit time | |
| `updated_by` | reference to person | |

**Gone with the table's rename:** `scope_type` and `scope_id`
([D-097](../decisions/decision-log.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row) —
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

- **The trail's payloads do not last** ([D-088](../decisions/decision-log.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short));
  the before-and-after images are emptied after 24 months. **"Who put her in charge of the money?" has
  to be answerable in year five**, from the same screen that shows when the appointment started, and an
  answer that requires `audit.view`, a date range and an intact payload is not an answer to a question
  about the current officer.
- **The row's readers are not the trail's readers.** `role_holder` is read by whoever administers
  offices; the trail is read by whoever holds `audit.view` 🔒🔒, and
  [D-086](../decisions/decision-log.md#d-086--a-sensitivity-mark-grades-what-a-grant-exposes-not-the-table-it-reads)
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
  the identical rule on `person_group_member`, [D-002](../decisions/decision-log.md#d-002--everything-temporal-is-a-period-never-a-boolean),
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

This is [D-071](../decisions/decision-log.md#d-071--nothing-forces-a-role-assignment-to-end-the-gate-and-the-report-are-the-control)'s
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
[D-031](../decisions/decision-log.md#d-031--no-downward-inheritance-of-authority-scope_exposure-is-the-only-crossing)
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
([D-097](../decisions/decision-log.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)).
A permission held at the unit reaches every member, and `person.view` was already the widest read
permission in the system
([D-083](../decisions/decision-log.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data),
[D-086](../decisions/decision-log.md#d-086--a-sensitivity-mark-grades-what-a-grant-exposes-not-the-table-it-reads)).
What is left of the safeguarding story is the same three things D-095 was left with — a permission
held by a named adult, an audit trail whose payloads expire after two years
([D-088](../decisions/decision-log.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)),
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
one is absent. See [D-078](../decisions/decision-log.md#d-078--an-exposure-extends-an-assignment-never-a-direct-grant),
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
([D-099](../decisions/decision-log.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)).

**Fields** (`grant_scope_type`)

| Field | Kind | Notes |
|---|---|---|
| `code` | text, required, unique | `unit`, `event`, `person_group`, `role`, `document`. The key a grant points at. |
| `name` | text, required | |
| `item_table` | text, required | The table `scope_id` references — `event`. For the unit, nothing: the row exists so the scope type has a name, and `is_item_scoped` is what says so. |
| `is_item_scoped` | boolean | Default true. **False for exactly one row: `unit`.** A grant at a non-item scope has no `scope_id`, and that single fact is what "the unit is a scope, not a row" means in the schema ([D-097](../decisions/decision-log.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)). |
| `description` | text, optional | |

**Seeded rows**, and the list is short on purpose:

| `code` | Item-scoped | Means |
|---|---|---|
| `unit` | **No** | The organization. There is exactly one, and it is not a row anywhere else. |
| `event` | Yes | One event. Nothing owns it ([D-102](../decisions/decision-log.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)); a unit grant reaches every event and an event grant reaches one. |
| `person_group` | Yes | One group ([D-098](../decisions/decision-log.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority)) — how "these two may work this group's roster" is said without inventing a scope. |
| `role` | Yes | One office ([D-100](../decisions/decision-log.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)) — the same move applied symmetrically. |
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
| `permission_id` | reference to `permission`, required | **One code, not a bundle** ([D-099](../decisions/decision-log.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)). What `level` used to stand in for, without the ladder. |
| `effect` | enum: `allow`, `deny`, required | **Allowed iff some live allow applies and no live deny applies.** [D-013](../decisions/decision-log.md#d-013--explicit-deny-revoked-is-checked-before-everything)'s deny survives as an effect on a row rather than as a level called `revoked`, and its reason for existing is unchanged: a court-ordered restriction must not be beatable by a broader grant. |
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
  absolute and is checked first**, which is [D-032](../decisions/decision-log.md#d-032--deny-is-absolute-locality-orders-allows-only)
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
([D-099](../decisions/decision-log.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)),
and it follows from two deletions rather than from a new rule: after
[D-097](../decisions/decision-log.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)
there is no intermediate scope left between the unit and an item, and after
[D-102](../decisions/decision-log.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)
there is no ownership relation to test.

**This is [D-006](../decisions/decision-log.md#d-006--per-item-permissions-are-capabilities-on-the-item)
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
([D-099](../decisions/decision-log.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)),
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
([D-099](../decisions/decision-log.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)):

| | `effect = deny` | `-` in an audience expression |
|---|---|---|
| Narrows | **Every grant** that applies to the person, including ones written elsewhere, later, or by somebody else | **One grant's** reach |
| Says | "she must not have this, whatever else she is given" | "this grant is not for the people in that set" |
| Beatable by | Nothing. Checked first, absolute, scope-independent | Yes — any other grant that reaches her |
| Lives on | A grant row | An operand of the grant's audience (§8) |

**The first cannot be expressed by the second, which is why denies stay** — that is
[D-013](../decisions/decision-log.md#d-013--explicit-deny-revoked-is-checked-before-everything)'s whole
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

**This is the rule's shape, not an implementation detail of an index** ([D-072](../decisions/decision-log.md#d-072--the-documentation-carries-no-sql-the-schema-is-the-orms-job)),
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
   ([D-102](../decisions/decision-log.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)).
4. **The audience's expression is well-formed, acyclic and within its depth limit** (§8) — **and
   "acyclic" and "depth" are now measured over the expanded tree, so this check follows the
   `AUDIENCE` leaves into the audiences this one names**
   ([D-103](../decisions/decision-log.md#d-103--an-audience-may-name-another-audience)). Saving a grant
   is not where a cycle is *created*, but it is where a person is standing to be told about one, and a
   grant must never be saved pointing at an expression that cannot be evaluated.
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
[D-101](../decisions/decision-log.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree)
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
rule, because [D-071](../decisions/decision-log.md#d-071--nothing-forces-a-role-assignment-to-end-the-gate-and-the-report-are-the-control)'s
posture applies here too: nothing in the schema forces a grant to end, and the report of
long-lived open grants is the control. **What changed in round 10 is that the nudge lost its
machinery.** The prefilled term (`role.max_term_months`) is deleted, and the membership gate that
used to make a forgotten row harmless is deleted; a forgotten grant is now simply live.

---

## 7. `permission_level` — deleted by D-099

**This section, and the table it described, are deleted**
([D-099](../decisions/decision-log.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)).
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
[D-068](../decisions/decision-log.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle)
had already refused the same idea once when it deleted `<resource>.admin` and said *roles are the
bundle*. Round 9 was half the thought: **roles and audiences are the bundle, and nothing else is.**

**Levels can come back as names for sets of codes with no comparison defined** — which is what a
role already is, so no new mechanism would be needed to approximate one. A real ordering coming back
means re-importing this table, the rank rule
([D-012](../decisions/decision-log.md#d-012--status-strings-compare-by-rank-never-lexicographically)),
and locality's tie-break
([D-032](../decisions/decision-log.md#d-032--deny-is-absolute-locality-orders-allows-only)'s deleted
half), all of which were deleted with their only consumers. **That is the two-way door, and it is
narrow on the ordering side and wide on the naming side.**

---

## 8. `audience` — grants that target a set of people

A grant can name a **person** or an **audience** (D-042). **An audience is now an expression over
named sets, stored as a tree**
([D-101](../decisions/decision-log.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree)):
`MEMBERS * ROLE(treasurers) - GROUP(schuzka2026-1)` is one grant's grantee, and the three-arm shape
it replaces — a rule arm, a manual arm, an inclusion arm, unioned — is deleted. D-091's outcome
survives the reversal: composing *"the kitchen crew, plus whoever leads this pack"* in **one** grant
is what round 9 bought and round 10 keeps, and the intersection and difference round 9 could not
express at all can now be written.

**Fields** (`audience`)

| Field | Kind | Notes |
|---|---|---|
| `id` | integer identity | Surrogate key. |
| `code` | text, optional, unique where set | **Two different jobs, and round 10 gave it a second one.** (1) Since D-101: a stable handle for the seeded rows (`everyone`, `all_members`) and for reports — an audience is *aimed at* by a grant through `access_grant.audience_id`, a reference, and that has not changed. (2) **New, [D-103](../decisions/decision-log.md#d-103--an-audience-may-name-another-audience): the only thing another audience can name.** `AUDIENCE(<code>)` resolves through this column, so **naming an audience is what makes it composable, and an unnamed audience is simply not one.** Naming stays opt-in — there is no reason to force a handle onto a grant's private addressee list — and the leaf may not point at a null code, which is a check reading another table and therefore not a constraint (§11, check 12). **`code` now joins the shared namespace** of roles, groups and reserved words; `name` does not, and the two are different columns serving different questions. |
| `name` | text, required | What a human calls it in the editor. |
| `description` | text, optional | Why it exists, for whoever finds it in three years. |
| `selector_depth_limit` | integer, required, defaults to 3 | **How tall this audience's expression tree may get.** The bound the save-time guard reads (§*The expression tree*), and it lives on the row for the reason D-048 gives for the renewal window: it is a number the organization may move, moving it must not need a release, and **a screen or a job that contains the literal `3` has quietly turned a parameter back into a constant.** It bounds how tall a *configuration* may get — not a safety net under a broken tree, which is why nothing in the read path consults it. **Replaces `include_depth_limit`**, which bounded a chain of inclusions rather than a tree. **Counted over the expanded tree, not the local one** ([D-103](../decisions/decision-log.md#d-103--an-audience-may-name-another-audience)): the number is compared *after* `AUDIENCE()` references have been followed, because a bound measured per-audience is a bound on nothing — five nested audiences each three deep are fifteen deep, and a per-audience check sees five passes. |
| `is_system` | boolean | Default false. Set on the seeded rows so an editor can refuse to delete one. |
| `valid_from` | date, optional | |
| `valid_to` | date, optional | Absent = open. **An ended audience reaches nobody**, and that is the one test that gates the whole expression (§*Evaluation*). **Which is precisely why ending one is a save-time refusal once anything names it** — see the rule below, and note that under `-` an emptied operand makes the result **wider**, so "ended" would otherwise be a way to widen a grant by editing a different screen. |
| `created_at` | timestamp, audit time | |
| `created_by` | reference to person | |

**Rules** (`audience`)

- **The expression is the audience.** An audience with no root operand row is an empty set, and a
  freshly created one is exactly that — not a misconfiguration, and how an expression gets built one
  node at a time. What is *not* legal is a grant aimed at one being reported as granting something,
  which is the editor's job (§*The cost of composition*) and integrity check 7 (§11).
- **An audience is *aimed at* by reference and *named* by code, and those are different relations.**
  A grant points at `audience.id`; another audience points at `audience.code`. **What changed in this
  round is only the second half** — D-101's sentence, *"an audience is referred to, never named, and
  that is why the name collision problem does not reach this table"*, was true of a grammar whose
  only names were `GROUP()` and `ROLE()`, and
  [D-103](../decisions/decision-log.md#d-103--an-audience-may-name-another-audience) retires it.
  **The name collision problem now does reach this table**, and §*Names are one namespace* is where
  the rule lives.
- **Bare names do not resolve to audiences.** `MEMBERS * COUNSELORS` names a role or a group, exactly
  as it did before, and the audience arm has to be written `AUDIENCE(veterans)` (D-103). **This is a
  backward-compatibility rule and it is worth more than the four characters it costs:** letting a bare
  name reach a third table would silently change what stored expressions *mean*, which is the one
  change this round's own canonical-rendering rule exists to prevent.
- **`code` is unique among the rows that have one**, and joins the shared namespace (§*Names are one
  namespace*).
- **An audience may not be ended or deleted while something live names it** — a live grant aimed at
  it, or a live audience reachable from a live grant through any number of `AUDIENCE` leaves
  (D-103). Refused at save, and the reverse lookup is one indexed query over `audience_operand` rows
  whose `selector_kind` is `AUDIENCE`, so the machinery the reference needs is the machinery the
  protection needs. **Without this, "ended" is a way to empty an expression from a screen nobody
  associates with it** — and under `-` an empty operand makes the answer wider, not narrower. No
  foreign key does this job: the reference is a `code` inside a polymorphic column, not a foreign
  key (§*The expression tree*).
- **Naming an audience requires the right to read it — `audience.view` over it, in the catalog's
  vocabulary — and grants nothing to the people it contains**
  ([../appendix/permission-catalog.md](../appendix/permission-catalog.md)). Fail closed, and *see what
  you name* is already D-091's requirement. **`AUDIENCE(veterans)` in a grant someone else saves is how
  one person's composition decision becomes another's authority, and the read permission is the only
  place that asymmetry is visible to the writer.**
- `selector_depth_limit` is greater than zero.
- Where both ends of the period are set, `valid_to` is later than `valid_from`.

**Deleted from this table:** `resolver_key`, `scope_parameter` and `include_depth_limit`. The first
two are absorbed into the `selector_type` registry (§*The selector registry*) — which operands exist,
whether they take an argument and what type it is was three hard-coded lists (the enum written out in
prose, the reserved-word list, and the "meaningless without a `resolver_key`" rule) and is now one
seeded table. `audience_include`, the inclusion arm, is deleted outright (§*What each operand costs*).
~~`kind`, required, `builtin` exactly when `resolver_key` was set~~ — deleted by D-091 one round
earlier, and the deletion is kept visible because three rounds of prose rested on it and its
successor (`resolver_key`) is now gone too: **an audience has no kind and no rule key, only an
expression.**

### Author in sets. Evaluate per person.

**This is the split that makes the notation question smaller than it looks.** `p ∈ (A ∩ B) ∪ C` **is
by definition** `(p ∈ A ∧ p ∈ B) ∨ p ∈ C`, so the two notations considered in D-101 are the same
function read from two ends. The choice decides **what gets stored and what a writer is allowed to
say**, not what the machine computes:

- **Sets are the source language, and they are the closed one.** `-` is complement against
  `EVERYONE` and `*` distributes over `+`, so the set form is no weaker than a boolean one — it buys
  zero expressive power and everything in the way of safety. D-060 refused a rule engine, and a
  per-person boolean language is the door to one: once `&`, `|` and `!` exist, the next operand
  somebody wants is `AGE >= 15` or `FEE_PAID`, and there is a parser standing there to accept it. A
  set language closes it **by rule instead of by discipline**: *an operand must be a named,
  materializable set of people*. An attribute is not a set of people. Guardianship is
  (`GUARDIANS(x)` is a set), age is not, and the line falls exactly where D-060 already drew it —
  eligibility stays capability.
- **A check never materializes a set.** The resolver compiles the expression down to a predicate for
  the person being checked. **An implementation that evaluates `MEMBERS` as a list of ids and then
  tests for containment pays three thousand rows per request** — which is the one way to get this
  wrong, and the reason the requirement is written here rather than left to whoever builds it.
  Integrity check 16 (§11) is the CI assertion of that sentence.
- **The workloads the corpus already promised need sets, not predicates.** "Who does this grant
  reach?" must be **shown, expanded, in front of a human** — D-091 made that a requirement on the
  screen, and a predicate can only report `true` while a set *is* the answer. "What may a treasurer
  do?" (D-100) needs the person→set index, and `role_holder` and `person_group_member` **are** it; an
  expression is unindexable. And a cache can key on an operand and be reused across every grant
  (§10).

### Grammar, precedence, and the canonical rendering

```
expr    := term ( '+' term )*
term    := operand ( ( '*' | '-' ) operand )*
operand := EVERYONE | MEMBERS
         | GUARDIANS [ '(' person ')' ]
         | ATTENDED | PLACED | CONFIRMED | ON_WAITLIST | ORGANIZERS
         | ROLE '(' name ')' | GROUP '(' name ')' | LIST
         | AUDIENCE '(' code ')'
         | '(' expr ')'

  Each of ATTENDED, PLACED, CONFIRMED, ON_WAITLIST and ORGANIZERS appears either
  bare — bound to the item the grant sits on — or written '(' event ')'.  A bare
  bound operand on a unit-scope grant is refused (§6, *What is refused when a
  grant is saved*).

  LIST takes nothing: it is this audience's own hand-typed list, rendered in the
  editor as `LIST (this audience)`.  AUDIENCE names another saved audience by its
  `code`; an audience with no code cannot be named, and a bare name never
  resolves to one ([D-103](../decisions/decision-log.md#d-103--an-audience-may-name-another-audience)).
```

- `+` union, `*` intersection, `-` difference.
- **`*` and `-` bind tighter than `+`; `*` and `-` bind equally, left to right; brackets override.**
- **The canonical rendering prints every bracket, always.** The rendering is derived from the rows
  and is what every screen shows; if it is also kept as a column for search, it is a copy and the
  rows win (see §*The expression tree*).

**Printing every bracket is not a courtesy, and the example is the proof.** Under this precedence,
the unbracketed `MEMBERS - GROUP(schuzka2026-1) * COUNSELORS` means *"everyone except the counselors
in that group"*, which is **not** what its author meant — they meant *"all counselors not in that
group"*, whose stored form is `(MEMBERS - GROUP(schuzka2026-1)) * COUNSELORS`. The editor rewrites
what is typed into canonical form before saving, so **no expression in this system is ever read bare**.
The consequence is a nice property worth having: once everything is stored fully bracketed, changing
what binds tighter later changes nothing already stored, which is why the canonical rendering is a
requirement and precedence is the closed half of D-101's two-way door.

### The selector registry

**`selector_type` is a seeded table, not an enum**
([D-101](../decisions/decision-log.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree)):
**the language becomes data.** The parser reads its reserved words from it, the editor builds its
dropdown from it, and the write path checks arity against it. Three hard-coded lists became one
seeded registry in the shape `grant_scope_type` already has.

**Fields** (`selector_type`)

| Field | Kind | Notes |
|---|---|---|
| `code` | text, required, unique | The reserved word: `MEMBERS`, `ROLE`, `PLACED`. |
| `name` | text, required | For the editor's dropdown. |
| `takes_argument` | boolean, required | Whether the code **may** be written with an argument. The arity check reads this column and nothing else. |
| `binds_to_item` | boolean, required | True exactly when the **argument-less** form means "relative to the item being checked" ([D-102](../decisions/decision-log.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)). |
| `argument_type` | text, optional | Which table the argument names a row of — `role`, `person_group`, `person`, `event`, **`audience`**. Absent exactly when `takes_argument` is false. This is what the save path compares against the grant's item type, which is a reason the registry is doing real work and not merely tidying. **It is not always a `grant_scope_type`**: `person` never was and `audience` never will be, because a grant is never *about* an audience — it is aimed *through* one. The two coincide for exactly the item-scoped operands, which is the set the binding check reads. |
| `description` | text, optional | The sentence a writer reads before using it. `LIST` and `AUDIENCE` carry their gloss here, because both names mislead without one. |
| `is_system` | boolean, required | Default true, and **every seeded row is true with no row planned false.** This column exists to make the table refuse an edit, not to mark a category. |

**Seeded selectors**, in full, because this table *is* the language — **thirteen rows**, all of them
shipped. `PERSON` is the last one added and it was added *late, in this same round, by a decision entry that
had already said it was here*: this table was written from the evaluator's arm list rather than from
[D-101](../decisions/decision-log.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree)'s
grammar, and an arm list copied from an implementation loses the arm nobody implemented. The whole episode is
[D-104](../decisions/decision-log.md#d-104--a-permission-codes-last-segment-is-an-action-and-a-registry-that-prose-contradicts-is-a-fiction),
whose finding is that **no check in §11 could have caught this one**: check 12 compares rows against rows,
and the disagreement was between a row and a decision entry. The remedy it adopts is a report run over the
documents before a round closes, not a database constraint — see §13.

| `code` | Argument | Binds to item | Means |
|---|---|---|---|
| `EVERYONE` | never | no | Any person, including those with no account and no membership. |
| `MEMBERS` | never | no | Holds a membership live on the checked date — **the same predicate the deleted gate applied** ([D-039](../decisions/decision-log.md#d-039--member-permissions-require-a-current-paid-membership)); the clause died, the test did not. |
| `PERSON` | required (`person`) | no | **One named person** — a set of one, which is a set, so it passes the materializability test like every other operand. How an exception for a named individual lives *inside* the expression that granted the rule, next to the thing it exempts ([D-100](../decisions/decision-log.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)). Distinct from `LIST`, which is several people and belongs to one audience: `PERSON(a)` composes and subtracts on its own, `LIST` cannot be split. |
| `GUARDIANS` | optional (`person`) | yes, `person` | Guardians of that person. Bound: the guardians of the person this item is about. |
| `LIST` | never | no | **This audience's own hand-typed list of people** — the dated rows of `audience_member`, and the only operand with no argument behind it (`PERSON` names a rule-free set too, but it names exactly one person and it is an argument). *The people written into this audience*, and the editor writes it as `LIST (this audience)`, because the bare name does not say whose list it is (§*What `LIST` is, said plainly*). |
| `ROLE` | required (`role`) | no | Holders of that office live on the checked date (`role_holder`). |
| `GROUP` | required (`person_group`) | no | Members of that group live on the checked date (`person_group_member`). |
| `AUDIENCE` | required (**`audience`**) | no | **The value of another saved audience's expression**, evaluated live on the checked date. **New, [D-103](../decisions/decision-log.md#d-103--an-audience-may-name-another-audience)**; the one operand whose argument is a *decision about access* rather than a roster, and so the one that makes a rule namable. |
| `ATTENDED` | optional (`event`) | yes, `event` | `response = attending`. |
| `PLACED` | optional (`event`) | yes, `event` | Attending **and not waitlisted** — **the capacity set**, the one the events module counts and the index already serves. |
| `CONFIRMED` | optional (`event`) | yes, `event` | `PLACED` **and** `is_confirmed` — holds a paid place. |
| `ON_WAITLIST` | optional (`event`) | yes, `event` | Attending and waitlisted. |
| `ORGANIZERS` | optional (`event`) | yes, `event` | Runs the event (`event_organizer`). |

**Rules** (`selector_type`)

- Rows are platform-seeded. **Adding an operand is a decision entry plus a seed row**, never a row
  somebody types into a screen: each operand is a branch of the evaluator and a fact about stored
  data, and an editor that could invent one would produce an expression nothing evaluates — which
  then resolves to the empty set and denies quietly forever (§*Evaluation*).
- **The registry is organization-read-only, and saying that out loud is what makes "a closed
  language" true of a table rather than merely asserted.** Every row ships with the platform, every
  row is `is_system`, no screen edits this table, and no organization adds to it
  ([D-103](../decisions/decision-log.md#d-103--an-audience-may-name-another-audience)). *The language
  becomes data* means the parser and the editor read one place instead of three; it has never meant
  the language is extensible at runtime. **A `code` in this table with no shipped resolver arm is a
  deployment bug, and it surfaces as an empty set** — an operand that reaches nobody, an allow that
  allows nobody, and a deny that on the `-` side denies everybody. That is the whole hazard of
  calling a closed set "data", and it is why the seeding of this table is release engineering rather
  than configuration. **There is no third kind of row** — the taxonomy is *shipped and seeded*, and
  "seeded, marked system, but not implemented" is not a category this model allows, however useful it
  would be as a roadmap marker. `GRANTS` was the candidate for that third kind, and it is refused on
  type grounds one clause below rather than admitted with a status flag that would put a broken operand
  inside the language and an empty set inside every grant that named it.
- **Every `code` is a reserved name** in the shared role / group / audience namespace
  (§*Names are one namespace*).
- `argument_type` is absent exactly when `takes_argument` is false, and names a real table exactly
  when it is true.
- The four attendance tiers name columns of `event_registration` and nothing else. That is the
  requirement that keeps the writer's choice honest — picking between tiers only means something if
  the choices are the stored facts.

**Three operands are refused on purpose, and each refusal is load-bearing.**

- **`PRESENT(<event>)` over `was_present` is refused.** The reason is the failure direction:
  `was_present` is `NULL` until somebody takes a register, so an operand built on it would revoke a
  child's access to their own camp photos because a volunteer forgot to tick a box. That column is a
  safeguarding signal, *three-valued on purpose*
  ([D-067](../decisions/decision-log.md#d-067--presence-is-a-three-valued-fact-on-the-registration)),
  and keeping it out of the selector language is what keeps it meaning "a person recorded this"
  rather than "this is who may see things". **Say this wherever presence tempts a reader**, and this
  is one of the two places that reader will look.
- **`GRANTS` is refused, and its refusal is a different kind from the two above.** It was wanted so that
  an expression could name *"the people reached by these grants"* — a bulk-editing affordance dressed as
  an operand. **An operand must resolve to a set of people, and a set of grants is not one**, which is
  not a judgement about usefulness but the closure property of §*Author in sets* doing the job it exists
  for: the moment an expression can name the grant table, `MEMBERS - GRANTS(...)` is expressible, and a
  language in which a grant can subtract a grant is a language in which the answer to *"who may do
  this?"* requires evaluating the whole expression tree of every other grant to answer one check. The
  bulk edit it was asked for is real and is an **editor affordance** — select the grants, change their
  grantees, in one screen, which changes rows and leaves every stored expression meaning what it meant.
  **Refusing it here is what keeps that screen a UI feature instead of a resolver feature.**
- **`WHITELISTED` does not exist.** There is no stored state to name: the nearest facts are
  `source = staff` (an organizer entered them) and promotion off the waitlist. Either it means one of
  those or it is a new column on `event_registration`, which is an events decision and not a selector
  decision, so it stays [an open question](../open-questions.md) rather than being implied by a word
  in a grammar.
**`PERSON(x)` is in the registry, and this page is the reason anyone noticed it was missing.** Two decision
entries write it — [D-100](../decisions/decision-log.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)
has the waived-for-one-person case as `MEMBERS * ROLE(x) + PERSON(y)` and
[D-103](../decisions/decision-log.md#d-103--an-audience-may-name-another-audience)
has the kitchen crew as `(GROUP(kitchen) + LIST) - PERSON(a) - PERSON(b)` — and the seeded table this page
documents did not carry it, which this page read as *"the language has no such operand"* and the modules read
as a licence to rewrite both examples as `LIST`. **That reading was wrong, and the wrongness is the proof**:
D-103's example uses `LIST` and `PERSON()` **in the same expression**, so the two are being distinguished on
purpose, and no substitution can work because `LIST` is one set — `+ LIST` adds Honza and `- LIST` would take
him back away again, so the two who left have to be subtracted through something that names only them.
`PERSON` is that operand, `argument_type = person`, and the row now sits above. **The distinction to keep in
mind is `PERSON` is an argument and `LIST` is a set of this audience's rows**: an argument composes freely,
and a set that belongs to one grant cannot be split to serve one clause of its own expression.

The other half of what this page objected to was right, and is worth keeping as the reason the row took a
whole round to appear: **putting a person's id into the language means an operand is no longer only the name
of a set somebody else owns** — `PERSON(a)` is a set nobody maintains, created by being typed. That is
tolerable for exactly one operand, at the size of one person, in the one place where the alternative (a second
grant aimed at that person, which stays legal and is arguably clearer for a permanent exception) leaves the
exception invisible next to the rule it exempts. What was **not** tolerable is a control that does not parse.

### What `LIST` is, said plainly

**`LIST` is this audience's own hand-typed list of people** — the rows of `audience_member`, which is
the one table in this module that holds *persons* rather than *rules*. **It is the only operand with
no argument and no rule behind it** — `MEMBERS` is a test, `ROLE(vedoucí)` is an office with dated holders,
`PLACED` is a join against an event, and `LIST` is the names somebody typed into this one grant;
`PERSON(a)`, added last, is the one other operand that names a human instead of a rule, and it names
exactly one
([D-103](../decisions/decision-log.md#d-103--an-audience-may-name-another-audience)).

**It exists so a grant can carry its own exceptions without creating a thing everybody can see.**
D-103's example is *"everyone in the kitchen crew, plus Honza, minus the two people who left"*:
`(GROUP(kitchen) + LIST) - PERSON(a) - PERSON(b)`. **That expression is what proves `LIST` and
`PERSON` are two operands and not one wearing two names** — `+ LIST` adds Honza, and there is nothing
left to subtract with, because the one list this audience owns already contains him. The two who left
go in as themselves, one `PERSON()` each, which is the whole reason that operand exists
([D-101](../decisions/decision-log.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree)'s
amendment, [D-104](../decisions/decision-log.md#d-104--a-permission-codes-last-segment-is-an-action-and-a-registry-that-prose-contradicts-is-a-fiction)).
What is still true of `LIST` alone is that it is **not enumerable from outside**: it has no name, so a
nested audience cannot reach into another audience's list, and an exception written on a list is
invisible to every other grant until somebody opens this one.

The alternative to `LIST` — making Honza a member of
`GROUP(kitchen)` in order to reach one grant — edits a roster that other grants read, which is the
hazard this section spends its length on, and it invents a group nobody talks about, which is the rule
[D-098](../decisions/decision-log.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority)
wrote. So `LIST` is scoped to the one expression containing it, invisible in the group browser, and it
dies with the audience.

**The name is the weak part of the design, and the decision says so.** Nothing in `LIST` says *whose*
list, which is why the registry gloss is *"the people written into this audience"* and the editor
renders the operand as `LIST (this audience)`
([../appendix/permission-catalog.md](../appendix/permission-catalog.md)). Renaming the code was refused
only because the round has already carried it through four files and the gloss costs nothing; **if the
question keeps being asked, the replacement is `ADDED`**, which says where the rows came from. That is
registered rather than promised, and §13 keeps it.

### The expression tree

**Each row of `audience_operand` is one node** — the storage D-101 chose over a normalized union of
terms, "because a binary tree needs one evaluator of about fifteen lines and keeps the writer's
brackets instead of silently rewriting them".

**Fields** (`audience_operand`)

| Field | Kind | Notes |
|---|---|---|
| `id` | integer identity | Surrogate key. |
| `audience_id` | reference to `audience`, required | **Denormalized onto every row so that the whole tree is one indexed fetch.** The read path never walks a parent chain; it selects by `audience_id` and assembles in memory. **Amended by [D-103](../decisions/decision-log.md#d-103--an-audience-may-name-another-audience): one read *per audience in the closure*, not one read per check.** D-101's sentence counted one tree and stopped; an expression naming `AUDIENCE(veterans)` has to fetch that audience's rows as well, so the honest count is one indexed read for every audience the expression can reach. **The claim that survives is the one that mattered** — no transitive walk over `audience_operand` rows and no recursive query, just a bounded number of flat reads, bounded by rule (the same `selector_depth_limit`) and known at save time. Every row also carries its parent's `audience_id`, so a node never belongs to a different audience than the one above it (checked on save, asserted by check 10). |
| `parent_id` | reference to `audience_operand`, optional | **On the child**, so a node belongs to exactly one expression. Absent on the root. |
| `operator` | enum: `+`, `-`, `*`, optional | Set on a node, absent on a leaf. |
| `left_id` | reference to `audience_operand`, optional | Set on a node. **Left and right are not interchangeable:** `-` is not commutative, and the pair is the expression's meaning. |
| `right_id` | reference to `audience_operand`, optional | Set on a node. |
| `selector_kind` | reference to `selector_type`, optional | Set on a leaf, absent on a node. |
| `selector_arg_id` | integer, optional | **Polymorphic, and deliberately without a foreign key** — it points at `role`, `person_group`, `person`, `event` or **`audience`** depending on kind. [D-011](../decisions/decision-log.md#d-011--scope_id-on-access_grant-is-polymorphic-with-no-foreign-key)'s already-accepted trade-off, with its compensating orphan check (§11, check 2). Absent exactly when the selector's `takes_argument` is false. **An `AUDIENCE` leaf stores the referenced audience's row here and is therefore also the reference edge** (rule below), and the extra condition on that leaf is that the audience it names **has a `code`** — a check reading another table, which is why it is an integrity check and not a constraint (§11, check 12). |
| `created_at` | timestamp, audit time | |
| `created_by` | reference to person | Who wrote this node. An expression is a decision about how far a grant reaches, and the person who saved it is the answer to the question asked afterwards. |

**Rules** (`audience_operand`)

- **Exactly one shape.** A node has `operator`, `left_id` and `right_id`, and no `selector_kind`; a
  leaf has `selector_kind` (and `selector_arg_id` where the registry says it takes one) and no
  operator and no children. **Expressible on the row, so this one stays a real constraint** — the
  only rule in this section a migration can state by itself, which is worth noticing among the ones
  that cannot.
- **One parent, never a DAG.** `parent_id` lives on the child. A side table letting two expressions
  share a node is **refused**: editing the shared node would silently widen every grant using it,
  which is D-091's inclusion hazard re-imported through the back door. Check 15 (§11) is a CI
  assertion that no such table exists.
- **Cycles and depth are refused when the row is saved, and there are now two walks to run.**
  1. **Inside the tree:** walk the parent chain from the row upward — refuse a revisit, refuse
     anything deeper than the audience's `selector_depth_limit`. The tree shape makes a cycle
     structurally hard to build (a node cannot be its own ancestor if it did not exist when its
     parent was written) and it is **refused rather than trusted** for D-091's own reason: *a
     hand-fixed row, a restore from before the guard existed*.
  2. **Across audiences:** follow every `AUDIENCE` leaf in the closure and refuse a cycle through
     them. **This is the walk [D-103](../decisions/decision-log.md#d-103--an-audience-may-name-another-audience)
     makes necessary, and it is the sentence D-101 got wrong, struck here rather than quietly
     corrected:** ~~a tree cannot cycle, so the only acyclicity guard left is the cheap parent-chain
     one~~ — true of one tree, false of a **forest of trees pointing at each other**, which is what
     naming an audience creates. Half a is cheap; half b is the write-time reachability walk D-091
     already required, over a graph **built at save time from rows that already exist**. Depth is
     measured on the same expanded tree. Application layer for both walks, and the layer is named
     because each spans rows rather than columns of one row, which is
     [F-10 shape 3](../open-questions.md#f-10--which-invariants-the-orm-cannot-express-and-who-writes-those),
     so no migration can emit either.

  **What did not come back is worth as much as what did.** `audience_include` stays deleted: the
  edges *are* the `AUDIENCE` leaves, so there is no edge table to maintain, no transitive walk over
  rows at read time, and no `include_depth_limit` column. **The machinery D-101 counted as deleted
  stays deleted; only its confidence was wrong.**
- **Arity and binding are checked against `selector_type`** on save: an argument present exactly when
  the registry allows one, and a **bound** (argument-less, `binds_to_item`) operand legal only on an
  item-scope grant whose type matches `argument_type` (§6, *What is refused when a grant is saved*).
- **An operand that does not resolve is the empty set** — including an `AUDIENCE` leaf whose target
  has gone (D-103). A dangling `selector_arg_id`, a selector kind the evaluator does not implement, a
  role or group whose row has been deleted — each is the empty set, and an expression that cannot be
  evaluated reaches nobody (§*Evaluation*). **Fail closed on the allow side, and note that the same
  rule is fail-*open* looking, which is why it is stated with its two halves rather than as a
  slogan**: an empty operand reached through `-` makes the result **wider**, so `EVERYONE - <nothing>`
  denies everybody. D-103 keeps the rule for exactly that reason — **the loud failure is the one you
  want**, and the quiet alternative is discovered in an audit two years late. The protection above
  (an audience named by a live grant cannot be ended or deleted) is what keeps the wide case from
  arriving by ordinary administration.
- **The `AUDIENCE` leaves *are* the reference edges, and there is no edge table**
  ([D-103](../decisions/decision-log.md#d-103--an-audience-may-name-another-audience)). Every
  question about nesting — *does this cycle*, *how deep does this get*, *which grants name this
  audience*, *may this audience be deleted* — is answered by selecting rows from this one table where
  `selector_kind = 'AUDIENCE'`, which is why the round could delete `audience_include` and add nesting
  in the same breath. **The two-directional index that makes that cheap is `(selector_kind,
  selector_arg_id)`**, and it is the second reason the reference is stored as a row rather than parsed
  out of a rendering: an edge inside a string answers none of those questions without a table scan.
- **A node belongs to exactly one tree, and to exactly one audience.** Every row's `audience_id`
  equals its parent's; there is exactly one row with no parent; no row is its own descendant. Check 10
  (§11) counts these. **Nesting does not soften this**: `AUDIENCE(x)` points a *whole tree* at another
  whole tree. It is not a node shared between two expressions, and the rule above about one parent and
  no sharing table is exactly what keeps `AUDIENCE()` from being `audience_include` again by another
  name.
- **The whole tree is written together.** An expression is one act of authorship, so inserting a
  grant's audience inserts its nodes in one transaction, and deleting an audience deletes them.
  A node whose parent arrives in a later transaction is an orphan, and an orphan is check 10, not a
  transient state to be tolerated.

**Why a tree and not a string, and why not a normal form.** A string would have to be re-parsed on
every check and would make the arity and depth rules text-processing rather than row-writing. A
**union of terms** (the normalization D-101's author offered and D-101 declined) needs the
normalizer — distribute, dedupe, sort, survive blow-up — and would rewrite the writer's brackets
behind their back. The tree needs one fifteen-line evaluator, keeps the brackets, and makes the depth
limit the only complexity bound, since `(A + B) * C` costs nothing.

**What that costs, once.** Two expressions with the same meaning are two different row sets, so *"you
already granted exactly this set on that row"* no longer falls out of storage. The route back is a
normalized **fingerprint** computed on save as a derived value used only for a warning — and if the
expansion overflows, skip the warning rather than refuse the write: **normalization informing a human,
not gating one.** Registered in §13 rather than promised, and the same reasoning is why
"this selector reaches nobody" belongs to the editor preview that has to exist anyway (§*The cost of
composition*) rather than to a syntactic check the tree cannot perform — a tree catches `X - X` on one
node and nothing else.

### `audience_member`, re-roled as the `LIST` leaf

**It stays** ([D-101](../decisions/decision-log.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree)).
It is the audience's own dated list of people, reachable in an expression as one operand: `LIST`.

**Fields** (`audience_member`)

| Field | Kind | Notes |
|---|---|---|
| `id` | integer identity | Surrogate key. |
| `audience_id` | reference to `audience`, required | |
| `person_id` | reference to person, required | |
| `valid_from` | date, required | Default today. |
| `valid_to` | date, optional | Absent = open. |
| `added_by` | reference to person, optional | |
| `created_at` | timestamp, audit time | |

**Rules** (`audience_member`)

- `valid_to` is either absent or strictly after `valid_from`.
- **No overlapping memberships**, counted over **all** rows and not only the open ones. Periods are
  half-open, so a membership ending on a day and another beginning that same day do not collide.
- **A member row is legal on any audience that is not `is_system`.** D-091's reversal stands —
  a list beside a rule is the ordinary shape of *"whoever leads this pack, plus these two people"*,
  and the round that deleted the rule arm kept the list precisely because a hand-written set of three
  people is not derivable from anything.
- **A member row on a seeded `is_system` audience is refused.** Those rows are the resolver's own
  vocabulary; adding a person to `everyone` is not a widening, it is a category error. **The refusal
  belongs to the write path and no integrity check hunts it** — the old rule was a check, and what is
  left of it is a convention enforced by the editor that will not offer the row. (§11's check 7 looks
  at the opposite failure: an audience a live grant aims at that reaches nobody.)
- **`LIST` is legal in an expression with no rows**, and resolves to the empty set. A grant whose
  whole reach is a list of nobody is inert, and check 7 reports it when a live grant names it.

**Why it is not merged into `GROUP(x)`, said twice because both refusals were real.** Naming three
people in one grant would create a row in the group browser that is not a group anybody talks about;
and [D-098](../decisions/decision-log.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority)
already wrote the rule that keeps the two dated-member tables apart — **a group's members are true
when no grant points at them; a selector's additions are meaningless outside the expression they
complete.** `person_group_member` and `audience_member` are therefore two dated sets of people
**on purpose**, and the duplication D-080 would flag is kept deliberately: **merging them would make
the permission table the system's roster**, the same mistake D-062 refused when it declined to answer
"who is running this camp?" by reading the grant table. The mitigation is the one D-091 already
required and D-101 re-endorsed: **the editor shows which operand each person arrived through.**

### Three named sets, and the one question nesting cannot answer

**`GROUP(x)`, `AUDIENCE(x)` and `LIST` are all "some people" and none of them is the same kind of
thing** ([D-103](../decisions/decision-log.md#d-103--an-audience-may-name-another-audience)). Writing
the three side by side is the fastest way to see why the round kept them apart and what it accepted by
putting a third one in the language:

| | `GROUP(x)` | `AUDIENCE(x)` | `LIST` |
|---|---|---|---|
| What it is | A dated roster somebody maintains | A saved expression, evaluated live | Rows on this one audience |
| Who may change who is in it | `person_group.member.manage` | `audience.manage` on that audience | Whoever may edit this audience |
| Does it exist outside a grant? | **Yes** — D-098: a group's members are true with nothing pointing at them | No — it exists to aim a grant | No |
| *"Was she in it on 1 June 2024?"* | **Answerable**, from the dated rows | **Not answerable** past the audit window | Not answerable |
| Sensitive as | ⚠ company | 🔒🔒 authority | 🔒 |

**The fourth row is the honest cost, and it is the D-100 distinction replayed one level down.**
`GROUP(x)` is materialized, so its past is reconstructable from its own rows; `AUDIENCE(x)` is a live
rule, and its past shape survives only in the audit trail — where
[D-088](../decisions/decision-log.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)
empties the payloads after 24 months. So **"who could see this child's data in 2024?" is answerable when
the grant pointed at a group and is not answerable when it pointed at a nested audience.** D-103
records that rather than arguing it away, and the reasoning is the one this corpus already uses for
derived membership: a rule whose reach cannot be reconstructed is still the right tool for a rule —
`MEMBERS` is not going to be replaced by a roster of everyone — but the gap gets closed by a report,
not by pretending the question has an answer. The report is the save-time listing in §*The cost of
composition*, kept over time rather than shown once; whether that is worth building is registered in
§13 and is the same question as
[F-7](../open-questions.md#f-7--cache-vs-materialized-effective_permission-table) wearing a different
hat.

### Names are one namespace, and reserved words are the other half

**Bare `COUNSELORS` resolves against roles and groups together**, since `ROLE()` and `GROUP()` no
longer have to disambiguate — which makes **the name namespace load-bearing** in a way it was not
when a name was only a label
([D-101](../decisions/decision-log.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree)).
Five rules, and the layer each one lives in is the point:

1. **Names are unique across `role`, `person_group` and `audience.code`**
   ([D-103](../decisions/decision-log.md#d-103--an-audience-may-name-another-audience) adds the third
   table; `audience.name` is not in the namespace, only its `code`, because `code` is what resolves
   and `name` is what a screen displays). **No single constraint spans three tables**, so the write
   path carries it and integrity check 12 (§11) asserts the write path exists —
   [D-081](../decisions/decision-log.md#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now)
   wording, because a rule with no database backstop is a convention until a check says otherwise.
2. **Case, whitespace and separators are folded on write**, so `Schuzka 2026-1`, `schuzka_2026_1` and
   `SCHUZKA2026-1` are one name and not three sets that look different in an editor.
3. **Every `selector_type.code` is reserved.** A group called `MEMBERS` is refused at the save rather
   than silently rewriting every expression in the system.
4. **Bare names still resolve to exactly two kinds: a role or a group.** An audience is reachable only
   through its own keyword, `AUDIENCE(veterans)` — naming the namespace a third way **without**
   widening bare resolution, which is what keeps stored expressions meaning what they meant when they
   were written (D-103; the `audience` rules at the head of this section).
5. **What is stored is always kind + id**, never a name — so **a rename never rewrites a grant**.
   A role renamed still carries everything aimed at it, which is the property the old
   `code`-keyed designs kept advertising and never quite had. **`AUDIENCE` obeys this like every other
   leaf**: the resolution happens once, at save, into `selector_arg_id`, and renaming the audience
   afterwards rewrites nothing.

**What is given up:** a name is now a security-relevant string. Two organizations that both call
something `leaders` and one of them a *group* and the other a *role* get one namespace deciding which
`leaders` a grant meant, and the answer is that they cannot, because the write path refused the second
one at the save. **Round 10 widened what that sentence covers**: an audience code colliding with an
office code was a cosmetic problem while nothing could name an audience, and is a silent grant once
something can.

### What each operand costs

The distinction that used to be load-bearing — built-in *versus* named, rule *xor* list *xor*
inclusion — is gone, and what remains worth comparing is whether a set is **derived** or **kept**:

| | A derived operand | A kept operand |
|---|---|---|
| Which | `EVERYONE`, `MEMBERS`, `ROLE`, `GROUP`, `GUARDIANS`, `ATTENDED`, `PLACED`, `CONFIRMED`, `ON_WAITLIST`, `ORGANIZERS`, and `AUDIENCE` — **derived from another expression rather than from a fact table, which makes it the odd one and the reason this table has a footnote below** | `LIST` |
| How evaluated | A live read of the fact that defines it, at the checked date | `audience_member` rows |
| When someone joins | They are in it immediately — **automatically** | Nothing happens. Someone must add them. |
| Maintenance | None. **It cannot rot.** | The classic stale-group problem: nobody ever removes anyone |
| Membership stored? | No — and therefore not retrievable after the facts move (§*The cost of composition*) | Yes, dated |
| Examples | "everyone who holds a place on this event", "the counselors", "the guardians of this child" | "the summer camp kitchen crew" |

**Prefer a derived operand where one exists.** A grant to `PLACED` gets the right answer forever: a
new registrant is covered the moment they are placed, and someone who withdraws stops being covered,
with no rows to maintain. The same grant to `LIST` silently rots the moment the roster changes. **That
half of the old argument survives both rounds untouched** — what changed is that choosing between them
stopped being a choice about the *kind* of set, so one expression can hold the derived set and the
names it cannot reach, in one grant.

**The inclusion arm is deleted, and the second round had to give half of the answer back.** D-091 let a
group pull in other groups through `audience_include`, because a group could otherwise not be composed.
Under D-098 a group's membership **is** its dated rows, and composition moved into the expression:
`GROUP(kitchen) + ROLE(troop_staff)` composes as much as an edge ever did. What went with the edge table
was a great deal of machinery — the transitive walk, `include_depth_limit`, the write-time cycle walk
over a **graph**, and the CI assertion that the walk exists at all — and round 10 was right that a tree
needs none of it **within one tree**.

**Where round 10's arithmetic was wrong, stated plainly because the sentence is still in D-101.** It
claimed the write-time cycle walk was dead because *a tree cannot cycle*, and it claimed *"add the
kitchen crew to everything the troop-staff rule is used for"* was answered by **naming the composite
once and aiming grants at it**. Under its own grammar the only names available were `GROUP()` and
`ROLE()`, and **both name a roster, not a rule** — so the composite rule had no name to point at, and
the "naming" answer could only be carried out by copying rows into a second audience, which is
`audience_include` with the copy step done by hand. [D-103](../decisions/decision-log.md#d-103--an-audience-may-name-another-audience)
adds the missing arm, and with it **the cheap guard stops being the only guard**: one write-time
reachability walk returns, across audiences rather than over an edge table (§*The expression tree*).
**What stays deleted is the table, the column and the read-time walk** — the edges are leaves — so the
machinery that came back is smaller than the machinery that left, which is the honest version of the
claim. `AUDIENCE()` is also the only arm that names **a decision about access** rather than people, so
it is the only one that can say *"the same people that grant may see the fee ledger, plus the
accountant"*.

**`AUDIENCE` is derived, and it is derived from something nobody maintains, which is its one genuinely
new property.** Every other derived operand reads a fact table someone is already keeping — a
membership, a holder row, a registration. `AUDIENCE(x)` reads **an expression**. So the "maintenance:
none, it cannot rot" row of the table above is true of it in the sense that there are no rows to
maintain, and misleading in the sense that **the thing it is derived from is edited by whoever holds
`audience.manage` on it, for their own reasons**. That is the hazard of §*The cost of composition*, and
it is why this operand is graded as authority rather than as company.

### Evaluation

An audience grant is evaluated as part of the person's own permissions — the resolver expands it, so
a grant to an audience is checked *as if* the person held it directly. **The expansion is a
predicate, not a set** (§*Author in sets*).

A grant applies when **one** grant row satisfies all of these. These are conditions on a single row,
tested together — their order carries no meaning:

1. The grant names an audience; a personal grant is not this question's business.
2. Its `scope_type` is the scope type being checked, and its `scope_id` matches the scope id being
   checked, with an absent id counting as equal to an absent checked id.
3. Its `effect` is `allow` — denies belong to the channel that runs first (§10).
4. It has not been revoked.
5. It has started as of the checked date and has not ended on that date.
6. Its `permission_id` **is** the checked permission — or is `system.admin`, the one code that means
   everything (§2). **There is no `permission_level` row to consult and no rank to compare**; the
   comparison this condition used to perform is the whole reason that table existed and it is gone.
7. `person_in_audience(person, audience, at, item)` puts the person in that audience on the checked
   date, **for the item being checked** — because a bound operand means different people on different
   items ([D-102](../decisions/decision-log.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)).

`person_in_audience()` is where the language lives. It takes the item so that bound operands have
something to bind to, and it answers one question: **is this person in the value of this expression,
evaluated as a predicate?**

1. **The audience itself must not have ended** — no `valid_to`, or a `valid_to` after the checked
   date. An ended audience covers nobody, **and this is the one test that gates the whole tree**: the
   expression belongs to the audience that has ended, not to one of its operands.
2. **Evaluate the tree bottom-up, as a predicate.** A leaf asks its selector; a node combines its two
   children with its operator; `p ∈ A - B` is `p ∈ A ∧ ¬(p ∈ B)`, and so on for `+` and `*`.
   **No set of people is ever built** — the same fifteen lines answer every operand, and the cost of
   a check is one indexed read per operand, not one per member. **`AUDIENCE(x)` is the one leaf that
   recurses** (§*Three named sets*): it hands the same `person`, `at` and `item` to the other
   audience's tree and returns that answer, **predicating all the way down**
   ([D-103](../decisions/decision-log.md#d-103--an-audience-may-name-another-audience)). Nesting does
   not turn the evaluator into a set-builder; it turns one fifteen-line function into the same function
   with one more branch, and the recursion is bounded by the same `selector_depth_limit` that was
   checked at save over the **expanded** tree — which is why the read path never needs its own cap.
3. **A leaf's selector is one read** — except `AUDIENCE`, which is one read per audience in the
   closure. `MEMBERS` is the membership predicate at `at`;
   `ROLE(x)` is one open `role_holder` row for this person and this role at `at`; `GROUP(x)` likewise
   in `person_group_member`; `LIST` likewise in `audience_member`; `PLACED` is this person's
   `event_registration` row for the bound event with `response = attending` and `is_waitlisted`
   false; `EVERYONE` is true.
4. **A bound operand binds to the item under check.** `PLACED` with no argument means the event in
   the check's scope. **At the unit there is nothing to bind it to, and such a grant could not have
   been saved** (§6's save-time list) — so an unbound-at-unit shape reaching here is a fault, and it
   resolves to the empty set rather than to "everyone at the unit", which is the direction a helpful
   implementation would get wrong.
5. **Failure is denial, in every direction.** An operand whose `selector_arg_id` names nothing, whose
   `selector_kind` no evaluator implements, whose tree cannot be assembled, or whose depth exceeds
   its bound **reaches nobody**. Nothing here falls back to "so it probably includes everyone", and
   nothing here guesses the half of a tree it could resolve: **an expression that cannot be evaluated
   is an empty set**, which is the direction this model fails in everywhere else — default deny (§10),
   deny absolute (channel 0), and an audience whose rule was quietly wrong reaching nobody rather than
   everybody. **This supersedes the old fallback twice over:** first, an absent `resolver_key` used to
   mean "so it is a stored list"; now an absent selector is a **fault**, not a hint. Second, the
   inclusion walk used to be the one place a cycle could make the answer depend on where the walk
   started, and round 10 said ~~a tree cannot cycle, so there is nothing left to fail on~~. **That is
   true of a tree and false of a forest of audiences pointing at each other, and D-103 struck it.**
   **The consequence for the read path is deliberately nothing at all:** a cycle through `AUDIENCE`
   leaves is refused where it is written, so an evaluator meeting one is meeting data that should not
   exist, and the rule that covers that is this one — reach nobody, do not recurse forever and do not
   guess. **The reason the write-path check has to be a cross-audience reachability walk and not a
   parent-chain walk is exactly here** (check 15): if the read path is ever the thing that notices a
   cycle, some grant has already been evaluated wrong.

**Note that `ORGANIZERS` and `ROLE` read their tables without themselves being authority grants.**
Membership in an audience confers nothing on its own — it only decides whether *this* grant, which
someone already created deliberately, reaches this person. An appointed organizer does not become able
to do anything by being on the roster; they become able to do exactly what the grant aimed at
`ORGANIZERS` says, on that event. **This is [D-062](../decisions/decision-log.md#d-062--organizers-are-appointed-on-the-event-not-granted)
standing untouched**, and it is the sentence D-102 leans on: the appointment is now *aimed at* by
grants instead of being special-cased inside the resolver.

### What audiences do **not** do

- **They are not a permission.** Being in an audience is not authority; it is membership of a
  set. All authority still comes from a grant.
- **They do not replace `guardianship_permission`.** `GUARDIANS` lets an organization open something
  to a child's guardians; it does not let a guardian edit the child's record. That remains the
  guardianship channel (§10) and its `right_level`
  ([D-074](../decisions/decision-log.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular)).
- ~~**They do not nest.**~~ ~~**Withdrawn by D-091; the mechanism was removed by D-101.**~~
  **Nesting returns in the same round, through [D-103](../decisions/decision-log.md#d-103--an-audience-may-name-another-audience),
  and the three-stage history is worth keeping because the diagnosis never changed.** The sentence read
  *"an audience cannot contain another audience — that is how you get evaluation cycles and answers
  nobody can predict"*. Round 9 refused the cycle when the edge was saved; round 10 declared the
  problem **unsayable**, because an operand is a leaf naming a set and not a pointer into another
  expression; and D-103 found that the second round had answered *"reuse a rule"* with *"name the
  composite"*, while its own grammar offered no name for a rule — so the arm came back as
  `AUDIENCE(<code>)`. **What the ban was for survives intact, in a different place:** cycles are still
  impossible to *store*, they are just no longer impossible to *write*, so the guard is a
  cross-audience reachability walk on the save path instead of a shape argument (§*The expression
  tree*, check 15). **What the ban cost is also back, and honestly back:** *"the kitchen crew plus
  whoever leads this pack"* was the complaint round 10 solved in one grant, and it stays solved —
  `AUDIENCE()` does not undo it, it adds the case round 10 could not express, which is reusing a
  composite **rule** rather than copying it.
- **Nesting is not sharing.** `AUDIENCE(x)` evaluates the whole of another audience's expression; it
  does not splice one of its nodes into this tree. **Two expressions never share a row**, so editing a
  node inside `veterans` changes exactly the grants that name `veterans` and no others — which is the
  distinction that keeps this from being the DAG this corpus has now refused three times.
- **`everyone` is genuinely everyone**, including people with no account and no membership.
  It is the right target for a public event page and the wrong one for anything else. **And it is
  reachable by `+` from inside any expression**, which is what the deletion of the inclusion arm
  changes: nothing stops an expression from unioning the seeded `EVERYONE` operand, and a writer with
  `audience.manage` can widen a grant to the whole world in one edit. That is not a hole in the model —
  holding `EVERYONE` directly is already legal and already alarmed (check 8, §11) — it is that a
  language with union in it makes the same reach available without even pretending to compose it
  carefully. The mitigation is the editor's expanded set below, not a rule about which operands may
  appear where.
- **A role cannot be held by a rule.** `role_holder` names one person, and
  [F-12](../open-questions.md#f-12--closed--may-a-role-be-held-by-a-rule-as-an-audience-is) **is closed by
  [D-100](../decisions/decision-log.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape),
  and its answer is no** — a derived holder list cannot answer "who was treasurer in 2023", and an
  office record that cannot answer that is not an office record. The grantee pair F-12 contemplated is
  no longer even tempting, because grants now aim **at** roles instead of roles being filled **by**
  grants.
- **An expression cannot say anything about a person's attributes.** That is the closure property
  §*Author in sets* exists to protect, and it is worth restating as a negative because the temptation
  is permanent: `AGE >= 15` is not an operand, is not expressible, and there is no open question
  asking for it. Eligibility is capability ([D-060](../decisions/decision-log.md#d-060--eligibility-is-capability-there-is-no-separate-rule-engine));
  a set of people is a set of people.

### The cost of composition

**A grant's reach stops being visible in the row that grants it.** Derived membership has never been
stored — D-042 accepted that, and these documents recommended it, because a rule does not rot the way
a list does. Rounds 9 and 10 together **widened how much of the permission answer is recomputed
rather than recorded**, and round 10 added a sharper wrinkle.

- **The editor must show the set a grant actually reaches, expanded** — the people, not the
  expression's text — and it is a requirement on the screen rather than a nicety. Composition turns a
  three-deep expression into a silent widening, and the person saving the grant is looking at one row
  that mentions no person at all. **This is the same posture as the cache question in §10: the answer
  exists, it is just not stored, so somewhere has to compute it in front of a human** — and here the
  human is the only control there is.
- **And the preview is now per-item, which it structurally cannot be from the grant alone**
  ([D-102](../decisions/decision-log.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)).
  `PLACED` means different people on different events, so "who does this grant reach?" is unanswerable
  as written when the expression contains a bound operand. **The preview is therefore computed for an
  item and says so on screen** — an honest screen names the event whose people it is showing — and the
  cache key for a bound operand must include the item (§10). This is the one place where D-102's
  convenience costs a screen an editor's design has to notice, and §13 keeps it open rather than
  assuming it away.
- **Editing an audience changes grants you did not make, and the screen has to say so before it
  commits** ([D-103](../decisions/decision-log.md#d-103--an-audience-may-name-another-audience)).
  Add a person to `AUDIENCE(veterans)` and every grant naming it now reaches them — including grants
  their owners wrote for another purpose, and including grants this editor cannot see because they are
  not theirs. **This is not a new failure mode and pretending otherwise would be the actual mistake:**
  `GROUP(x)` has had the property since D-091, and the round that accepted it there accepted it for the
  reason that stands — **a named set is worth being reusable, and a reusable thing has more than one
  user.** The mitigation is D-091's, extended to the second user: **saving an edit to a referenced
  audience shows which grants name it, and at what depth, before it commits.** It is one indexed query
  over the leaf rows (§*The expression tree*), and it doubles as the report that partially closes the
  history gap in §*Three named sets*. **D-103 registers this as an assumption rather than a measured
  fact** — cheap at this organization's size because the edges are indexed rows in the table that
  already holds every expression, unverified at any size, and **a slow save screen is a real risk if the
  import corpus's row-count estimates turn out wrong**. §13 keeps it.
- **"Who could read this in 2023?" now has one fewer answer.** The audit trail used to hold the change
  that made it true, and [D-088](../decisions/decision-log.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)
  empties those payloads after 24 months; the derived membership was never stored at all. After two
  years the question is answered by re-running expressions against state that has itself moved on, and
  it is answered with today's confidence. **[F-7](../open-questions.md#f-7--cache-vs-materialized-effective_permission-table)
  is the route back** — a materialized `effective_permission` snapshot kept *as history* rather than as
  a cache — which until round 9 read as a performance question and is now the only thing that could
  make the unanswerable question answerable. Caching is §10's subject; **history is F-7's.**

---

## 9. `access_log`

The audit trail. Append-only; no updates, no deletes.

**Fields**

| Field | Kind | Notes |
|---|---|---|
| `id` | integer identity | Surrogate key. |
| `occurred_at` | timestamp, audit time | Default now. |
| `actor_person_id` | reference to person, optional | Who performed the action. Absent for system actions. |
| `subject_person_id` | reference to person, optional | Whose data was affected. Differs from the actor when acting on behalf. |
| `on_behalf` | boolean | Default false. True when the actor and the subject differ and the action was performed **for** the subject — guardianship, delegation. See [04-relationships.md](04-relationships.md) §6. |
| `authorization_channel` | enum: `deny`, `ownership`, `guardianship`, `unit_grant`, `item_grant`, `none`, or absent | Which channel answered this. Makes the audit answerable: "by what authority did this person do that?" `deny` records that a deny row defeated the allows; `none` records that nothing answered at all. **`role` and `system` are gone from this enum** — there is no role channel to name ([D-100](../decisions/decision-log.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)), and `system` was never a channel rather than a namespace. **An answer of `role` in an old row is now unreadable by the model that reads this table**, which is the honest state of a historical value: the audit trail keeps the word that was written, and nothing can keep a channel that no longer exists. |
| `authorization_ref_id` | integer, optional | No foreign key: it names a row in one of several tables — `access_grant.id` or `guardianship_permission.id`. Lets an auditor go directly to the grant that permitted the action. |
| `permission_code` | text, optional | The permission checked, as its code. Absent for pure read events that are logged for access-trail purposes rather than permission decisions. |
| `scope_type` | text, optional | `unit`, or an item type. |
| `scope_id` | integer, optional | Absent for a check at the unit. |
| `action` | text, required | `membership.request.approve`, `person.view`. |
| `entity_type` | text, optional | |
| `entity_id` | integer, optional | |
| `result` | enum: `allowed`, `denied`, `error` | Required. |
| `denial_reason` | text, optional | |
| `session_id` | text, optional | Acting context, for forensics. |
| `ip_address` | an IP address, optional | Acting context, for forensics. |
| `user_agent` | text, optional | Acting context, for forensics. |
| `request_id` | text, optional | Acting context, for forensics. |
| `before_state` | free-form jsonb, optional | For write actions. |
| `after_state` | free-form jsonb, optional | For write actions. **Redacted fields must be stripped before logging** — an audit log that leaks the data it audits is worse than none. |

**Rules**

- A `denied` result carries a `denial_reason`. There is no unexplained denial in this table.

**Indexes**

- the subject lookup covers only rows that name a subject;
- one index over denied rows only, newest first;
- one over acting-on-behalf rows only, newest first.

**`authorization_channel` and `authorization_ref_id` are what make this an audit trail
rather than a log.** A record saying "person 100 changed person 200's address" answers
*what* and *who*. A record that also names the `guardianship_permission` row that
authorized it answers *why they were allowed to* — and whether that authority was valid at
the time. When a custody dispute arises eighteen months later, that is the question asked.

**The channel enum got smaller in round 10 and the audit answer got better, which is worth saying in
the same breath.** `item_grant` and `unit_grant` are now the only two ways a permission is granted,
and both name a row the auditor can open. Under the ladder, a row saying `role` plus an assignment id
answered "by what authority" with a *bundle* — the auditor still had to expand `manage` into codes to
learn what the person could actually do, and the table doing the expansion was `permission_level`.
**Now the row names the grant, and the grant names one code.** That is the one place where deleting
the levels makes the trail more useful rather than less.

**`denied` results are logged too.** A series of denials is the signature of someone
probing for access they do not have. Logging only successes discards the signal.

**`before_state`/`after_state` must be redacted, and the sentence is the reason this document is
cited everywhere else.** Copying a value out of a guarded record into a table guarded by different
people, on a different path, for longer than the record is kept, produces a copy with less protection
than the original — and the copy is the one that gets read by auditors, exported for reports and
mirrored into backups. Redaction therefore happens **before the insert**, in the logging function, and
never in a job that might not run — the ordering is the part of this rule with teeth, and it survives
[D-072](../decisions/decision-log.md#d-072--the-documentation-carries-no-sql-the-schema-is-the-orms-job)
taking the trigger that used to enforce it.

**One clause of that sentence is now bounded, and the bounded half is not the half that mattered.**
*For longer than the record is kept* was written when this table's state columns and `audit_log`'s
payloads were both permanent. If
[F-8](../open-questions.md#f-8--retention-policy-for-access_log) is confirmed, the state columns expire on
the window
[D-088](../decisions/decision-log.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)
proposes for the change trail, which inverts that arithmetic: the copy becomes shorter-lived than the
business row it was copied from. The conclusion is unmoved, because what the rule guards is the
*audience*. A window decides how long a copied value is readable; it does not decide who may read it
while it is readable, and the readers here are whoever holds `audit.view`, not whoever may see the
record. A sensitive value copied into a less-protected table is a protection failure on the day it is
copied, not only for as long as it then survives.

**How far the argument reaches, now that the person record has no sensitive corner.** It is an argument
about *the copy's guard*, not about the copy's contents, and reading it as an instruction to empty
payloads is the mistake this section made once and corrected. [D-083](../decisions/decision-log.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)
removed the subset that a field list selects from — everything about a person beyond name, gender and
age is a value in `person_attribute` ([09-attributes.md](09-attributes.md)) — which rules out
name-keyed scrubbing of personal data for good: there is no list, and `allergy` is not on it. It leaves
two conclusions, and they point in opposite directions from the obvious one:

- **The credential case stays, and it is the only one a name list can serve.** Values where *being in a
  log at all* is the harm — secrets, tokens, credentials — are stripped on the way in, by key name,
  everywhere a listed key turns up ([06-audit-and-import.md §2.2](06-audit-and-import.md#22-redaction-before-logging)).
- **The person-data case is answered by grading the copy, not by thinning it.** `audit_log` holds
  before and after images of a child's descriptive values, because
  [D-085](../decisions/decision-log.md#d-085--the-identity-machinery-stays-structured-the-boundary-is-rules-not-sensitivity)
  made that trail the only history those values have. So **"the copy must not be less guarded than the
  original" is a requirement on `audit.view`'s sensitivity mark** — the top tier, beside `person.view` —
  and not a rule about which keys may appear in a jsonb column. Written as a requirement in
  [00-conventions.md §8 item 7](00-conventions.md#8-personal-data-and-erasure) and demanded of the
  catalog in [../appendix/permission-catalog.md §8](../appendix/permission-catalog.md#8-audit-and-system);
  erasure reaching those payloads stays absolute
  ([06-audit-and-import.md §4](06-audit-and-import.md#4-redaction-log)).

**Append-only enforcement:**

Any update or delete against `access_log` is refused row by row, before it happens, with an
error saying the table is append-only. Nothing is left to the application remembering this.

**That sentence has two exceptions, and written as a blanket refusal it defeats the retention policy.**
Emptying a row's payloads once it passes the window below is an update, and so is scrubbing one person's
values out of a row after an erasure. Neither is a correction: nobody is making a version of this table
right, and the answer the row gives to *who, what, when, by what authority* is untouched in both cases.
So both fall inside what "append-only" forbids in spirit and outside what it may forbid in practice.
**State the guard as a refusal of rewrites rather than a refusal of writes** — the only actor allowed to
change a row is the erasure or the reduction, the only columns either may touch are the state columns,
and every other field on the row is immutable. The literal version of this rule is the more dangerous
one, because it fails silently and what it fails is the policy. The same reasoning applies to
`audit_log` and is stated with the operations themselves in
[06-audit-and-import.md §2.2](06-audit-and-import.md#22-redaction-before-logging).

**Retention: the same window as `audit_log`'s payloads, as a proposal rather than a decision.** This
paragraph used to read *"never delete them — the partition retention policy is a legal question, not a
technical one"*, and the second half of that is still exactly right. What has changed is that the
decision which bounded the change trail's payloads
([D-088](../decisions/decision-log.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short))
proposes the same window here — **24 months on the state columns, rows kept, 12 months as the floor** —
and records it as [F-8](../open-questions.md#f-8--retention-policy-for-access_log), **which still needs
confirming**. Until it is confirmed, that is a default awaiting a person and not this document's
position.

**Why the question is weaker here, which is structural and not luck: this table does not hold the
contents of reads.** `before_state` and `after_state` are populated for write actions only, so a read
records *who asked, for what, under which permission, through which channel, and whether it was
allowed* — and stops. Recording what the read *saw* would copy every record a permitted glance touched
into a table read by a wider audience than the record itself, which is the exact act this section
argues against two paragraphs above. So the window here protects considerably less than it protects
over in `audit_log`, and what survives it is everything this table was built to answer. **The valuable
fact about a read is that it happened and by what authority, and that is precisely the part no
reduction touches.**

Consider partitioning by month once volume justifies it, and moving old partitions to
cheaper storage. Rows are not deleted on either answer; the window is carried out by emptying the state
columns, which is the job and the over-age check described for the change trail in
[06-audit-and-import.md §5](06-audit-and-import.md#5-integrity-checks). **If F-8 is confirmed, that check
has to be written for this table too** — a reduction with no check under it is a reduction that quietly
stops happening, which is the failure mode §2.2 of that document names as the only one this operation
has.

*Assumption:* `access_log` may be queried by staff with a specific permission, but writing
is automatic. If the organization needs human annotation of audit entries, add a separate
`access_log_note` table rather than making this table mutable.

---

## 10. The resolver

### Steps the resolver leans on

**Three helpers keep `can()` readable, and one of them is fifteen lines long.**

**`grant_satisfies(person, scope_type, scope_id, permission, at)`** — does the person hold a live
**allow** of **this code** on **this exact scope**? Exact match only. It covers both a personal grant
and one made to an audience the person is in. Any one grant row meeting all of these satisfies it:

1. Its `scope_type` equals the checked scope type and its `scope_id` matches the checked scope
   id, with an absent id equal to an absent checked id.
2. Its `permission_id` **is** the checked permission, or is `system.admin`.
3. Its `effect` is `allow` — denies are handled by the channel that runs first.
4. It has not been revoked.
5. It has started as of `at` and has not ended on `at`.
6. The grantee is this person, or an audience containing them at `at` for this item (§8).

**Two of the old seven conditions are gone, and both were the level.** There is no
`permission_level` row to join and no rank to compare, which means the helper now asks a question with
a yes-or-no answer instead of one with a threshold. **`level_satisfies()` is deleted with them** — it
existed only to compare a grant's level with the level a permission required at a scope type, and with
no levels its arguments do not exist.

**`person_in_audience(person, audience, at, item)`** — is the person in the value of this audience's
expression on this date? It gained the `item` argument in this round, because a bound operand means
different people on different items and there is no other way to tell it which event it is asking
about (§8, *Evaluation*). An unresolvable operand is the empty set; an expression that cannot be
evaluated reaches nobody.

**`operand_holds(person, operand, at, item)`** — the evaluator's one recursive step: a leaf asks its
selector, a node combines its children. **It is written once and it is short**; the requirement
inside it is that every selector is evaluated as a predicate about this person and never as a set of
ids (§8, *Author in sets*).

**One leaf does not ask a selector, it asks this function again.** `AUDIENCE(x)` calls
`person_in_audience(person, <the audience x names>, at, item)` and returns what comes back
([D-103](../decisions/decision-log.md#d-103--an-audience-may-name-another-audience)) — the same three
arguments carried straight through, because a nested audience means the same people on the same date
for the same item, and **the same predicate shape, because nesting is the moment at which a lazy
implementation would most plausibly decide to materialize the inner set and test containment.** That is
§11's check 16 and it covers recursion explicitly: an operand cache keyed on
`(person, selector_kind, selector_arg_id, …)` already has a key for a nested audience, which is what
makes the recursion shallow in practice and not merely shallow in argument. **The recursion terminates
by construction, not by a counter**: a cycle through `AUDIENCE` leaves cannot be saved (§8), so a
read-path depth cap would be a thing that decides who a grant reaches in exactly the case where the
data is already wrong.

**Deleted from this list:** `scope_exposure_covers_assignment(org_unit_id, role_assignment_id, at)`
(the exposure table is gone, D-097) and `person_holds_gate_exempt(person, at)` (the gate is gone,
D-100). **The second deletion retires a hazard with it.** That helper had to be carefully kept *out*
of `can()` — routed through the resolver, a lapsed holder of the exemption would be denied by the very
rule it existed to lift, "a lockout with no error message, on the one day of the year it would hurt
most". **There is no such lockout any more, because there is no gate to lapse through.** The special
case is gone rather than fixed, and the lockout D-051 existed to survive is listed as retired below,
in §12.

The single authorization entry point. One implementation, used everywhere. Algorithm:
[../domain/06-authorization-model.md](../domain/06-authorization-model.md#6-the-resolver).

**`can(person, permission_code, scope_type, scope_id, at, owner_person_id)`** returns allowed
or denied. `scope_type` and `scope_id` are optional, `at` defaults to today, and
`owner_person_id` is supplied only where the ownership or guardianship channel is in play.

**The order of these steps is a rule for one reason and not the other.** Each step either returns or
falls through, so a step never gets to contradict an earlier one. **The deny step must run first, and
that is the only ordering with a consequence for the answer.** The allow steps are alternatives
producing the same boolean, so their order decides **which channel the audit names** and how quickly
the answer arrives — never what the answer is. That is exactly what the deletion of locality means,
and it is worth stating here because "the tiers are ordered and the first sufficient one wins" is a
sentence this document repeated for nine rounds and no longer believes.

1. **Look the permission up by code.** If no permission carries that code, **return false** —
   an unknown permission is a deny, and it is settled before anything else is considered.
2. **Resolve merge chains.** Replace the person with the survivor of any merge, so permissions
   are never evaluated for a tombstoned person.
3. **Channel 0 — explicit deny. Absolute and scope-independent.** A live `deny` grant of this code
   applicable to this person blocks access no matter **what** scope it sits at: a per-event grant can
   never restore access that a unit-wide restriction removed
   ([D-013](../decisions/decision-log.md#d-013--explicit-deny-revoked-is-checked-before-everything)).
   A deny counts when it is itself unrevoked, has started as of `at`, has not ended on `at`, and
   applies to the person — where "applies" means it names them **or** names an audience they are in
   at `at` for the item being checked. A personal deny and an audience deny are equally absolute, and
   **a personal allow cannot beat an audience deny, because channel 0 has already returned.** Its
   scope applies when either of these holds:

   - it sits at the **unit**, and then it applies everywhere — every item of every type, because a
     unit grant reaches every item and a unit deny is the same shape with the opposite effect;
   - it sits on the exact thing being checked — same scope type, same id.

   **There is no third bullet, and the second half of that sentence is the round.** The old list had a
   third: *it sits on a unit and the check is about that same unit*, with a note that a deny on a unit
   covered **only** that unit because authority does not flow down. That case is now the first bullet —
   there is one unit and it is not a row — and the ancestor walk the note refused to perform has no
   function left to refuse it. Any such grant: **return false.**
4. **Channel 1 — a grant at the unit.** `grant_satisfies(person, 'unit', NULL, permission, at)`.
   Because a unit grant reaches every item of every type (§6), this one step is the tier that used to
   be three: the organization grant, the unit grant, and the exposure branch that connected them.
5. **Channel 2 — a grant on this exact item.** `grant_satisfies(person, scope_type, scope_id,
   permission, at)`, reached only when both a scope type and a scope id were supplied. **This is the
   step `can_event()` used to precede**, and nothing precedes it now: a unit grant reaches the item,
   an item grant reaches the item, and there is no owner to ask
   ([D-102](../decisions/decision-log.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)).
6. **Channel 3 — ownership.** If an owner was supplied and that owner resolves to this same
   person, **return true**. Your own data.
7. **Channel 4 — guardianship. Consulted when the check is about someone other than the actor;
   answers with an allow only.** The test is a comparison, not a name: an owner was supplied, it
   resolves to a real person, and that person is **not** the actor. The question is whether the
   actor holds a **live guardianship over that subject at `at`** whose `right_level` covers the
   checked permission — and **this is where `permission.right_kind` is read, by its only customer**:
   `none` covers nothing, `view` covers codes marked `read`, `write` covers both.
   **If such a guardianship exists and covers the permission, return true. In every other case — no
   guardianship, `none`, or a right that does not cover this code — the channel returns nothing at all
   and the resolver continues.** It does not deny. Defined in
   [04-relationships.md §4](04-relationships.md#4-how-the-resolver-uses-these-tables); the reasoning
   for both halves is
   [D-079](../decisions/decision-log.md#d-079--the-guardianship-channel-is-entered-by-shape-not-by-permission-name).

   Two properties of this channel survive, and the third changed shape:

   - **Entered by shape, not by namespace** (D-079, following D-074). A parent correcting their
     child's address is checked under `person.address.edit` — an ordinary, un-prefixed code — and
     still routes here. A permission added next year for a field a guardian must edit is covered
     the day the field exists, provided it is marked `write`, which is the seeding default (§2).
   - **Silent rather than final.** Under the old prefix rule this channel gave the last word.
     It still does not take it, and with a boolean answer there is no longer even a shortfall to
     fall through: a guardian whose right does not cover the code simply does not answer, and the
     actor's own grants get their turn. **A real prohibition is still possible and still absolute —
     it is a deny row, step 3.**
   - ~~**Gate-exempt.**~~ **Withdrawn by [D-100](../decisions/decision-log.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape),
     and this was the property that made the channel need explaining.** A guardian whose own
     membership lapsed had not stopped being the child's guardian, so the gate had to be declared not
     to apply here. Now nothing is declared, because no channel is gated: `MEMBERS` is an operand some
     writer typed into some expression, and guardianship is not an expression.

   **The rest of this channel's older commentary survives unchanged and is not repeated here:** the
   guard must not be weakened into "the subject is a minor" (the existence of a guardianship row is the
   whole test, and an age lookup would put a branch in the resolver that D-070 and D-077 rule out), and
   personal attributes reach this resolver through no new door — everything beyond name, gender and age
   is descriptive data read by `person.view` and written by `person.edit` through the channels above,
   with no `attribute.*` read permission, no fifth channel, and no branch on *what a value is about*
   ([09-attributes.md §4](09-attributes.md#4-who-may-read-and-who-may-write),
   [D-083](../decisions/decision-log.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)).
   **The temptation that paragraph refuses — "a leader may see allergy data, but only for the children
   in their unit" — has lost half its grammar in round 10: there is no "their unit" to refer to**, and
   what remains of the refusal is the older and better reason that a branch on content is the privileged
   medical subset returning through the resolver after D-083 refused it through the permission list.
8. **Default deny. Return false.**

> **There is no membership gate anywhere in this function, and that is the deletion to notice while
> reading it.** Nine rounds put one clause in the role channel — `AND (NOT r0.requires_membership OR
> is_current_member(p_person_id) OR person_holds_gate_exempt(p_person_id, p_at))` — and called it the
> thing most likely to be "optimized" away. **All three disjuncts are gone**: the first with the
> column, the second into the `MEMBERS` operand, the third with the permission
> ([D-051](../decisions/decision-log.md#d-051--the-membership-gate-is-waived-by-a-permission-not-only-by-a-role-flag)
> deleted entirely). The predicate `is_current_member` survives inside the evaluator, evaluated
> live at `at` like every other operand, and the three old shapes map exactly:
>
> | Old mechanism | Expression now |
> |---|---|
> | The gate applied to a role with `requires_membership = true` | `MEMBERS * ROLE(x)` |
> | The gate waived for a whole role | `ROLE(x)` — written without `MEMBERS` |
> | The gate waived for one named person | `MEMBERS * ROLE(x) + PERSON(y)` — the exception inside the expression that granted the rule, so it is read next to the thing it exempts. A second grant aimed at that person alone is equivalent and arguably clearer for something permanent; what was never allowed is a row that does not parse (§8, `PERSON`) |
>
> **The posture reversed from default-on to opt-in, and the new failure mode is named rather than
> buried** (D-100). Forgetting `MEMBERS` is now invisible, silent and permanent, and nothing in the
> resolver can see it. Three controls, none of which is the resolver: the standing report of
> `ROLE(...)` grants with no `MEMBERS` (check 6, §11); seeded grants carrying `MEMBERS` so that the
> path of least repetition is the safe path; and **import completeness** — `MEMBERS * COUNSELORS` is
> only as correct as the counselor roster, so an import that misses 300 counselors silently un-gates
> them, and the reconciliation report of
> [D-090](../decisions/decision-log.md#d-090--the-legacy-corpus-is-thousands-of-roster-rows-with-numbers-and-no-money)
> must count people marked as counselors in the corpus against `role_holder` rows written. **It fails
> closed — nothing breaks, which is exactly why nobody notices.**

### Cache invalidation, revisited

The answer cache and the operand cache are two different things, and round 10 separated them because
D-101 made operand results reusable in a way the old union-of-arms model never was.

**Fields** (`permission_cache`)

| Field | Kind | Notes |
|---|---|---|
| `person_id` | reference to person, required | |
| `permission_code` | text, required | The code, as checked. |
| `scope_type` | text, optional | |
| `scope_id` | integer, optional | |
| `allowed` | boolean, required | The answer that was computed. |
| `computed_at` | timestamp, audit time | |
| `expires_at` | timestamp, required | How long the answer may still be used. |

**Rules**

- One row per person, permission code, scope type and scope id — where an absent scope type and
  an absent scope id each count as a key value of their own, not as "any scope".

**An operand cache beside it**, keyed `(person, selector_kind, selector_arg_id)` for an operand that
does not bind, and **`(person, selector_kind, selector_arg_id, item)` for a bound one**
([D-102](../decisions/decision-log.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it):
*the cache key for a bound operand must include the item*). **A bound operand cached without the item
in its key is a wrong answer waiting for the next event** — `PLACED` is different people on every
event, and a cache that does not know which event it answered will answer for all of them. The win is
that an operand result computed for one grant is reused by every grant that names the same operand,
which the three-arm model could not do because its answer was a walk rather than a value.

**An `AUDIENCE` leaf is an ordinary operand for keying purposes and an extraordinary one for
invalidation** ([D-103](../decisions/decision-log.md#d-103--an-audience-may-name-another-audience)).
Ordinary, because `(person, AUDIENCE, <audience id>[, item])` is exactly the shape above and needs no
new column. Extraordinary, because **the answer under that key depends on rows belonging to a different
audience than the one being evaluated** — which is the paragraph below, and why it had to be rewritten
in this round rather than left alone.

**Indexes**

- on `expires_at`, for the expiry sweep;
- on `person_id`, because a membership transition must invalidate by **person**, fast — `MEMBERS` is
  now an operand, so every cached answer that depends on it is this person's.

Invalidated on any write to `role_holder`, `person_group_member`, `access_grant`, `audience`,
`audience_operand`, `audience_member`, `guardianship_permission`, a person merge —
**and on every membership transition, including the yearly expiry sweep, which touches every member at
once.** **Read the `audience` and `audience_operand` entries as wider than they look**: a write to one
audience's tree invalidates every audience that can *reach* it, not only the one written — see the hard
case below.

**The shape of the hard case changed, and the lesson did not — and the case itself is now two.** Under
D-091 the dangerous write was `audience_include`: one edge three levels down silently changed every
group above it, and the code saving the edge had no list of what depended on it, so these documents
assumed the blunt answer — invalidate the audience-derived entries wholesale.

Round 10 said the graph was gone and the hazard with it, **and D-103 half-took that back.** A write to
`veterans` now changes the value of every audience whose expression names `AUDIENCE(veterans)`, and of
every grant aimed at those — and the code saving `veterans` still has no list of what depends on it.
**The hazard came back in a genuinely smaller form, and the difference is worth naming rather than
glossing:** the edges are rows in the table that already holds every expression, so the *direct*
referrers are one indexed query on `(selector_kind, selector_arg_id)`, and D-103 already requires that
query for a different purpose (refusing to delete a referenced audience, §8). **The reverse closure is
therefore computable where it once was not** — which is a real improvement and still not a reason to
compute it inside an invalidation path, because "computable" and "cheap enough to run on every write"
are different claims and the second is the one that gets decided wrongly under load. **The blunt answer
stands: invalidate audience-keyed operand entries wholesale.**

**The second hard case is a table, not a graph.** Adding one person to an office changes every grant
whose expression names `ROLE(that_office)` — including grants written later by other people for reasons
the writer has never seen — and the code that inserts a holder row has no list of those grants either.
**Neither invalidation can be keyed on the rows that were written.** Both are listed here rather than
left to whoever implements them for the same reason the membership sweep always was: **the expensive
invalidation is the one that is easy to decide is unnecessary.**

### Properties to verify when reviewing this function

1. **Deny is checked before everything**, including ownership and guardianship. A restricted
   account's owner permissions are denied by a `deny` row if that is what the organization wants.
2. **`at` is threaded through every branch.** Permission checks are time-travel capable, and an
   operand evaluated at "now" inside a check performed at a past date is a wrong answer that looks
   like a right one.
3. **There is no wildcard except `system.admin`.** No prefix match, no implied capability.
   If a holder can do a thing, a row says so (D-068) — and now a row says **which** thing, because
   there is no level standing in for a set of them.
4. **`resolve_person` is called on entry**, so a tombstoned person's id still resolves.
5. **A deny is scope-independent.** Channel 0 matches a unit deny and an exact-item deny and does
   **not** walk ancestors — so a deny at the unit blocks every item, which is what makes a
   suspension absolute.
6. **There is no hierarchy to walk, and nothing left to assert about it.** ~~`unit_ancestors()` must
   not appear in this function~~ — the function itself is deleted
   ([D-097](../decisions/decision-log.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)),
   which is a stronger guarantee than the CI assertion that replaced it in round 8 and then died with
   the SQL in D-072. **The surviving time-bomb is a different one** — no permission path may
   materialize a set of people — and it is check 16 (§11).
7. **Audience grants are evaluated through the same channels as personal ones**, via
   `grant_satisfies()`. A grant to `EVERYONE` and a grant to a named person differ only in how
   *grantee* is satisfied, never in how the scope or the code is resolved.
8. **Expression evaluation is a walk over a forest that fails closed.** An unresolvable operand is the
   empty set, and an expression that cannot be assembled reaches nobody (§8, *Evaluation* item 5).
   **The failure this property forbids is a helpful implementation**: a walk that returns what it
   managed to reach when something downstream breaks turns a broken expression into a widening, and a
   widening is the only direction in which this channel can do harm. **Forest, not tree, since
   D-103** — the walk crosses an audience boundary at an `AUDIENCE` leaf, and a partially-evaluated
   outer tree over a failed inner one is precisely the shape that produces a widening.
9. **A check that supplies no item cannot answer a bound operand, and must not guess one.** `PLACED`
   with nothing to bind to is not "everyone" and not "nobody at this unit" — it is a caller error, and
   the answer is denial with a `denial_reason` that says so. **This is the new cousin of the
   unscoped-check caveat below, and it is enforced in the same place: the calling convention, not the
   data.**
10. **`right_kind` is read in exactly one place.** If a second comparison of `read` against `write`
    appears anywhere else in the resolver, that is a mechanism being built on a column D-099 documents
    as having one customer.
11. **A nested audience is evaluated at the caller's `at` and the caller's item, with neither
    re-defaulted** ([D-103](../decisions/decision-log.md#d-103--an-audience-may-name-another-audience)).
    The recursion has to carry all three arguments through or it is not the same question being asked
    again, and **of the two, the silently wrong one is the date**: an inner audience re-defaulted to
    today answers *"was she in it?"* with *is she in it*, which is the exact substitution property 2
    exists to forbid, one level down and invisible in every test that checks only one audience.

**A caveat on an unscoped check.** "Can this person do X anywhere?" returns true if *any* grant
grants it. That is correct for UI decisions like "show the admin menu?" but **wrong for enforcement**.
Every enforcing call must pass a scope. Enforce this in the calling convention — make scope mandatory
at the API layer for mutating operations.

The cache definition and its invalidation rules are above, immediately after the resolver —
they are part of the resolver's contract, not a separate concern.

The person-merge case remains the easiest to forget —
see [01-identity.md](01-identity.md#8-identity_hypothesis-and-person_merge).

---

## 11. Invariants to verify

These were queries. They are now invariants to be verified by something, in whichever way the
implementation chooses, and what follows states what each one counts and what a non-zero result
would mean. **They are renumbered for round 10**, because several lost their subjects
(`requires_scope`, the membership gate, `system.gate_exempt`, `permission_level`, the three
`scope_exposure` checks) and the survivors were closed up rather than left with holes.

**Three of the old checks were CI assertions that read the text of the stored resolver to prove a rule
was still inside it (14, 15 and 19 in the previous numbering). Nothing can read that text any more.**
Their successors below are written as assertions about behaviour rather than about program text,
because that is the strongest form still available, and
[D-081](../decisions/decision-log.md#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now)
requires saying so: **a prohibition nobody runs is a convention, not a guard.**

**Invariants to verify**

- **1. Live grants for a person who has been merged away.** An open `access_grant` whose person
  has been merged into somebody else. A row means authority is still attached to a tombstone;
  it should have been closed or moved at merge time.
- **2. Orphaned item grants, and orphaned selector arguments.** Per scope type, generated from
  `grant_scope_type`: a grant whose `scope_id` names no row in the item table it points at — and the
  same scan over `audience_operand.selector_arg_id`, which is polymorphic for the same reason and
  takes the same mitigation. A row is exactly the risk the polymorphic columns accept (§6,
  [D-011](../decisions/decision-log.md#d-011--scope_id-on-access_grant-is-polymorphic-with-no-foreign-key),
  extended to operands by
  [D-101](../decisions/decision-log.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree)),
  and this is that trade's compensating control. **An orphaned operand is the quiet half**: it
  resolves to the empty set, so the grant is inert rather than dangerous, and inert authority is the
  failure nobody notices.

  **Since [D-103](../decisions/decision-log.md#d-103--an-audience-may-name-another-audience) the scan
  covers one more target kind, and this is the one place its asymmetry has to be stated rather than
  assumed away.** `selector_arg_id` now also points at `audience`, and an orphaned `AUDIENCE` leaf is
  **not necessarily quiet**: quietness is a property of the leaf's *position*, not of the leaf. Reached
  through `+` or `*` it removes people; reached through `-` it adds everyone the missing audience was
  excluding. **So run the scan, and route its output to check 7's second report rather than to this
  one's** — an orphaned `ROLE` leaf belongs with inert authority and an orphaned `AUDIENCE` leaf
  belongs with the grants that got wider, which is the same fact about the operator being the thing
  that decides the direction of a failure, said once in §8's evaluation rules and again here because a
  reviewer reading only this list would otherwise file all of it under "inert". **In practice: one scan,
  two outputs**, splitting on whether the orphan sits under an odd number of `-` right-hand positions.
- **3. A grant at a scope its code forbids.** An open grant whose `scope_id` is present while the
  permission's `applies_to` is `unit` — or any grant of a `system.` permission whose `applies_to` is
  not `unit`, which is the seeding rule §2 depends on. **Zero expected, and a row means the save-time
  check was skipped, not that a constraint was disabled** — no constraint spans those two tables.
  This is the report that stands in for a database rule, which makes it worth alerting on.
- **4. A bound operand where it cannot bind.** An `audience_operand` whose selector has
  `binds_to_item = true` and which sits in an audience aimed at a `unit`-scope grant, or whose
  `selector_type.argument_type` differs from the item type of every grant aimed at that audience. Zero
  expected for the same reason as 3: refused on save, unenforced by any constraint, and a row means
  the write path was bypassed. `PLACED` aimed at a group, or `ORGANIZERS` aimed at nothing, should be
  unsaveable, and this check catches the build in which they are not.
- **5. A deny that denies nothing.** A live `deny` whose grantee, scope and code match no live allow
  anywhere. **Probably intended as a removal rather than as a restriction; verify the intent.** D-099
  requires this one by name: a deny that denies nothing is how a stale restriction survives its
  reason, and the resolver will never tell anyone it is dead, because a deny never needs to.
- **6. A grant naming an office with no `MEMBERS`.** A live grant whose audience expression contains a
  `ROLE(...)` operand and no `MEMBERS` operand anywhere in the tree
  ([D-100](../decisions/decision-log.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)'s
  standing report). **A row is not an error** — writing an office without the gate is a legitimate act
  and is exactly how an appointed officer keeps serving while their own fee is unpaid — but it is the
  case worth a human eye, because it authorizes a lapsed member silently and forever. This is the
  successor to the old "leavers with access" and "holders of the gate exemption" checks, and it is
  deliberately narrower than either: **the report has to be short enough to actually be read**, which
  the two it replaces were not.
- **7. A grant aimed at an audience that reaches nobody — or everybody.** A live `access_grant` naming
  an audience whose expression contains no operand that can hold a person — a `LIST` with no open rows,
  a `GROUP(x)` whose group has ended, an operand whose `selector_arg_id` is orphaned, **an
  `AUDIENCE(x)` leaf whose target has ended or gone (§8, and D-103)**, a tree that cannot be assembled.
  **The grant join is what makes this check worth running**: an empty audience on its own is a work in
  progress, but an empty audience a live grant points at is a permission configured, visible in an
  editor as granted, and reaching nobody — the same inert-authority shape the previous version of this
  document recorded for a rule that matched no person, and the one an administrator cannot see from the
  grant screen.

  **Run the same scan for the mirror-image case and report it separately, because it is the more
  dangerous of the two:** an empty operand reached through `-` makes the expression **wider**, so
  `EVERYONE - AUDIENCE(x)` with `x` gone reaches *everybody* — an allow that meant to exclude now
  includes, and a deny that meant to exclude now falls on everyone. D-103 counts that loudness as the
  reason to keep fail-closed evaluation at all, **and loud is only an advantage over quiet when
  somebody is listening**, which is what this check is for. `MEMBERS - AUDIENCE(x)` is the quiet
  version: **the exclusion is the grant's whole point and its
  target is gone, which reads on screen as a grant that still names the audience it excludes.** The
  save-time refusal (an audience named by anything live cannot be ended or deleted) is the primary
  control; this check is the one that fires when the refusal was bypassed by a restore or a manual
  delete, and unlike the empty side it should alert rather than be read weekly.
- **8. A grant whose expression contains `EVERYONE`.** Live, and naming `EVERYONE` anywhere in the
  tree. Not a violation: it is what a public page is for, and holding it directly was always legal.
  It is on the list because a language with union in it lets one edit widen a grant to every person
  with no account and no membership, and the person who made the edit is the only control
  (§8, *What audiences do not do*).
- **9. Holders of `system.admin`.** Everyone with a live allow of it, however they came by it —
  through a personal grant or through an expression naming an office. This should be a very short
  list, and it should alert on change.
- **10. Expression trees that are not trees.** Any of: a node with a selector, or a leaf with an
  operator; a node with one child; a row whose `audience_id` differs from its parent's; a row whose
  `parent_id` names no row; an audience with zero or several root rows. **Zero expected, and every
  shape here means the write path let a tree be assembled one row at a time.** §8's first rule is the
  one check a migration *can* state; the rest of the list cannot be, which is exactly why it is here.
  **Nesting did not relax any of it**: `AUDIENCE(x)` is a leaf pointing at another audience's *root*,
  never at one of its interior rows, so a tree still has one parent per node and one audience per
  tree — and a row whose `parent_id` crosses an audience boundary is this check firing, not a feature.
- **11. A delegation that cannot expire.** A live `access_grant` with `is_delegated` true and no
  `valid_to`. The row rule forbids it and no constraint enforces it. **Half of the old delegation
  check is gone**: "or whose source assignment has ended" had an assignment to point at, and
  `delegation_of` is deleted (§4), so expiry is now the *only* guard against a delegation outliving its
  reason.
- **12. Two names that are one name, and a reference that points at an unnamed thing.** Three shapes,
  one namespace:
  1. A `role.code` equal to a `person_group.code` after case, whitespace and separator folding;
  2. either of those equal to a `selector_type.code`, **or any of the three equal to an
     `audience.code`** — the third table is in the namespace now, because `AUDIENCE(<code>)` resolves
     through it ([D-103](../decisions/decision-log.md#d-103--an-audience-may-name-another-audience));
  3. an `AUDIENCE` leaf whose `selector_arg_id` names an audience **whose `code` is absent** — legal on
     every column of both rows and unsayable as a constraint, because the check reads a third table
     ([F-10 shape 3](../open-questions.md#f-10--which-invariants-the-orm-cannot-express-and-who-writes-those)).

  **Zero expected; no single constraint spans three tables, and no constraint at all covers the
  reserved-word half or the null-code half**, so the write path carries all of it and this check asserts
  the write path exists. A row here is not untidy: a group called `MEMBERS` would silently rewrite the
  meaning of every expression in the system, **and an audience sharing an office's code is the same
  accident one arm over — the kind of the name decides which set a bare expression meant, and after
  D-103 there are three kinds that can collide instead of two.**
- **13. Orphaned permissions.** An assignable permission that **no live grant names**, at any scope.
  This check exists **because of** D-068 and survives D-100's deletion of `role_permission` by
  retargeting: the net was "no role grants it", and now nothing grants anything, so the question has
  to be asked of the grants themselves. **Expected: empty after a seeding pass.** A row means either a
  permission nobody has bundled into an office yet — fine on a roadmap, wrong in production — or a
  module was added and its grants were not. **Note what it cannot see:** a permission granted to *an*
  office but not to the office that arguably should have it. That residual is the accepted cost of
  D-068 and nothing closes it; it is a human reading the starter list in §12 against the catalog.
- **14. Offices nobody holds, and holder rows pointing at an office that is gone.** The first is
  **expected and is not an error**: a role nobody holds is either one about to be used or one stopped
  using and not deleted, and there is no third possibility, because a role has no period
  ([D-053](../decisions/decision-log.md#d-053--a-role-is-valid-always-only-its-assignment-is-temporal))
  and cannot be switched off, only held or not held. Delete the mistakes, keep the ones on the
  roadmap. The second should be zero — the delete guard on `role` enforces it, and the check exists
  because a restored dump or a manually disabled guard bypasses it, and the loss is unrecoverable.
- **15. TIME-BOMB: an expression must be refused at the write, never survived at the read.** The
  successor to the old inclusion-cycle assertion, same shape, and it asserts a **guarantee rather than
  a set of rows**. Three halves, and the last is the one that fails silently.
  1. **A cycle must be unsayable, and there are now two walks to try.** Assert that saving is refused
     for **both** shapes — a node whose parent chain revisits a row inside one tree, **and** an
     `AUDIENCE` leaf whose target audience reaches back to the audience being saved, at any distance
     ([D-103](../decisions/decision-log.md#d-103--an-audience-may-name-another-audience)).
     **The second half is the one this document got wrong**, in D-101's words and therefore in its own:
     it claimed the write-time cycle walk had been deleted because *a tree cannot cycle*, and a forest
     of audiences naming each other is not a tree. Both are tested as a test that *tries*, not one that
     counts, because after the fact there are none to count. **Zero is the expected result every time
     this runs, and a non-zero result is not bad data but a missing guard.**
  2. **Depth must be refused at the same moment, over the expanded tree.** Past the audience's
     `selector_depth_limit`, with the count taken **after `AUDIENCE` references are followed**, because
     a bound measured per-audience is a bound on nothing — five nested audiences three deep are fifteen
     deep and each passes a local check. Same reasoning as before: the bound is on how tall a
     *configuration* may get, and it is a stored column rather than a constant for D-048's reason — a
     job containing the literal `3` has turned a parameter back into a constant.
     **Note what the bound does not bound, because nesting is the first thing to make it matter:
     `selector_depth_limit` limits height, and an expression's cost is now proportional to the number of
     *audiences* it reaches, which is breadth.** Fifty `+ AUDIENCE(...)` leaves at depth one are legal
     under any depth bound and cost fifty fetches per check. Nothing here mints a fan-out limit — that
     would be a new parameter and a new decision — but a reviewer optimizing this area should know that
     **the stored bound does not bound the thing the cache now pays for**, and §13's question about the
     default number is really a question about both shapes.
  3. **No sharing table may exist, and the read path must grow neither a depth cap nor a cycle
     check.** The tree's one-parent rule is worth nothing if a later round adds a side table letting
     two expressions share a node — editing the shared node would silently widen every grant using it,
     which is D-091's inclusion hazard re-imported. `AUDIENCE` is not that table and must not become
     it: it points at an audience's whole expression, never at an interior node. And a forest met at
     read time by a hop counter is survivable-looking, so whoever meets one adds a cap, and **the cap
     becomes the thing that decides who a grant reaches** — which is the reason the read path must
     depend on the write guard rather than back it up. **A build that passes halves 1 and 2 and fails
     this one is a build where the write guard has been removed and papered over, and it is the
     specific shape D-103 makes easy to reach** because nesting gives the read path somewhere to want a
     counter.
  4. **A referenced audience may not be emptied from the other end.** Saving must refuse to end or
     delete an audience while a live grant, or a live audience reachable from a live grant, names it
     (§8, *Rules*). It is a save-path refusal like the others and it belongs to this assertion for the
     same reason: **the data after the fact is perfectly well-formed** — an ended audience and a leaf
     naming it are both legal rows — and the damage is that every expression doing `X - <that one>`
     silently got wider. **Of the four halves this is the one most likely to be implemented as a
     warning**, because a delete that pops a confirmation dialog feels like sufficient care and a
     refuse feels like an obstacle. It is the one where a warning is not enough.

  **Why this is a CI assertion and not a report:** three of the four guards are walks over rows rather
  than comparisons within one row, which means they live in application code and no migration can emit
  them
  ([F-10 shape 3](../open-questions.md#f-10--which-invariants-the-orm-cannot-express-and-who-writes-those)).
  **A guard that lives in code is deleted by a refactor and the data looks fine afterwards** — which is
  why D-072's removal of the build-time greps is recorded as a weakening rather than a cleanup.
- **16. TIME-BOMB: no permission path may materialize a set.** The requirement is that
  **`operand_holds` decides membership for one person and never loads a set of ids to test containment
  in.** An operand is a *named, materializable* set for the purposes of the editor's preview and the
  cache key; in the resolver it is a predicate, and D-101 writes the distinction down precisely
  because an implementation is one lazy join away from getting it the other way and paying three
  thousand rows per check. **This replaces the old "no permission path may inherit" assertion, whose
  subject — the unit hierarchy — no longer exists**, and it is the same *kind* of rule: a requirement
  about how the code computes, which no migration can state and no reviewer will notice missing until
  the first slow day.

  **Nesting is where this assertion earns its keep, so assert on a nested expression specifically.** A
  flat `ROLE(x)` is awkward to write as a set load and natural to write as a predicate; an inner
  `AUDIENCE(veterans)` inside an outer expression reads like a job for *"fetch the inner set once and
  reuse it"*, which is the tempting optimization, is correct as an answer, and is the thing that makes a
  check slow at exactly the depth the depth bound allows. **A test exercising only single-level
  expressions passes on an implementation that materializes at every nesting level.** Assert that the
  recursion takes a person and returns a boolean, and that no path between two audiences hands over a
  collection.
- **17. TIME-BOMB: `.admin` prefix matching, and any ordering comparison, must stay deleted.** Two
  parts, both prose since D-072 removed the SQL that could be grepped, which that entry records as a
  real weakening. **First, no step of the resolver may build a permission code by concatenating a
  resource with `.admin`,** and no permission may have `admin` as its *action* except **exactly one**:
  `system.admin`. [D-074](../decisions/decision-log.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular)
  withdrew the four exemptions D-068 had allowed, so the allow-list is a single code and the check is
  an equality, not a set membership. Zero rows expected; the point of the entry is that the first
  version of the second half accepted five exceptions and the second accepts one, **because an
  allow-list is where a wildcard comes back to life.** **Second, and new: no comparison of
  `access_level` ranks, no `required_level` lookup, and no "at least `contribute`" anywhere.** D-099
  notes that the bug
  [D-012](../decisions/decision-log.md#d-012--status-strings-compare-by-rank-never-lexicographically)
  existed to catch — `'admin' < 'contribute'` read alphabetically — cannot occur in a system with no
  levels, which is a better fix than the guard. **The one ordering this model still performs is
  `right_kind` containment in the guardianship channel**, so a build where a second ordering has
  appeared has not reintroduced a bug; it has started reintroducing the ladder.

**Checks 3, 4, 5, 6 and 9 are the ones to wire to alerts, plus one half of 7.**

- **3 and 4 are the reports that stand in for the database rules that do not exist.** A row in either
  is not data drift — it is a save-path check that stopped running, which is the failure mode §5 of
  this document used to need a whole table for.
- **5 and 6 are the two reports round 10 created**, one for each mechanism it simplified: a deny that
  denies nothing, and an office granted without the membership operand. Both are lists a human reads,
  and both are the entire remaining control on their failure.
- **9 should email someone every time its result changes** — a new holder of `system.admin` is either
  a planned change or an incident, and either way someone should know within the hour.
- **Check 7 is the exception to the rule that this list is read rather than alerting on.** Its empty
  half — a grant reaching nobody — is inert and belongs on a weekly list. **Its wide half, a grant that
  got wider because something under a `-` stopped resolving, is the only entry in §11 that describes
  authority increasing**, and it should go to the same place check 9 does. **Splitting 7 is not
  tidiness**: a single report containing both halves has the wide row sitting between nineteen inert
  ones, which is how a widening gets read.
- **Checks 15 and 16 are CI assertions, not reports.** They are the automated guards on the two rules
  most likely to be "simplified" away when someone optimizes the resolver: the refusal of a malformed
  expression at the write, and the refusal to compute a set where a predicate will do. Both fail the
  build rather than silently changing who can do what, and both live in code rather than in the schema,
  which is why neither can be a migration. **D-103 moved weight onto 15 in particular** — with nesting
  available, the write path is guarding a graph rather than a row, and it now guards three things at
  once (cycles, expanded depth, and not emptying something that is named).

---

## 12. What the organization starts with

Starting catalog. Expect to edit this heavily; it is a proposal, not a specification.

> **This section and [../appendix/permission-catalog.md](../appendix/permission-catalog.md) are
> the same list written twice, and they drift.** When this was reconciled, **22 documented
> permissions had no seed row** — among them a code five of the catalog's own seed roles assigned, and
> one of the two codes D-068 exists to protect. A further 12 were the `event.*` set, added to the
> catalog when events were designed and never carried here. **Under the old wildcard much of this was
> harmless**: a role holding a resource's `.admin` reached a code whether or not the row existed, so
> the catalog could advertise a capability the database could not name and nothing noticed. The
> permission editor was the only place the gap showed.
> **[D-068](../decisions/decision-log.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle)
> removed that cushion,** and round 10 removed a second one: with `role_permission` gone there is no
> per-role list left to compare a catalog row against, so a documented code that nothing grants is
> now invisible in a way it never was. **Integrity check 13** reads the grants for exactly that reason.
>
> **There is no SQL check for this** — one side is a Markdown file. The discipline is the
> check: when adding a permission, add it in **both** places in the same edit, and treat a catalog
> row that no grant names as a bug of the same class as a missing migration. The reconciliation is
> mechanical enough to script: a diff of the codes the catalog lists against the codes that exist.
> Anything in the catalog and not in the database is a permission that cannot be granted; anything in
> the database and not in the catalog is an undocumented capability. Both were present at the same
> time.

**Off the catalog now, and named rather than quietly dropped:** the eighteen `dependent.*` codes (a
guardian's authority is a `right_level` on the relationship, not a bundle of permissions — D-074);
`scope.expose` and `scope.exposure.review` (the table they guarded is deleted — D-097);
`system.gate_exempt` (the gate it waived is deleted — D-100); every `position.*` code and the
appointment workflows behind them (D-100); and the codes that were about *bodies* rather than people —
a unit's renaming, restructuring and closing, and participation in a sub-unit — all deleted with the
hierarchy (D-097). `role.assign` and `role.unassign` survive but are **retargeted at `role_holder`**,
as do `role.create`, `role.view`, `role.edit` and `role.delete` — and `role.edit` no longer reaches
anyone's authority (§3).

**Roles are data, and the organization administers them at runtime.** This section seeds the
*permissions* — the vocabulary of things anyone might do — and one role. The role names used
throughout the docs are worked examples of composing those permissions into grants, not a fixed list.
Creating a role, naming it, filling it and deleting an unused one are all supported operations.

**What is seeded as a role, and it is one row: `counselors`, marked `is_system`**
([D-100](../decisions/decision-log.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)).
A permanent, organization-wide population is the opposite of D-098's definition of a group (*"a
temporary set of members that do events together"*), and which table it lives in decides the
sensitivity that every safeguarding convention in this area hangs from. **It ships `is_system` so an
editor refuses to delete it**, and it confers nothing: this is a **set**, and being in it is worth
only what a grant naming `ROLE(counselors)` says
([D-005](../decisions/decision-log.md#d-005--permissions-are-grants-never-derived-from-identity)).
**Consistency requirement, and it is the import's problem too:** `MEMBERS * ROLE(counselors)` is only
as correct as that roster, so the import reconciliation of D-090 counts people marked as counselors in
the corpus against `role_holder` rows written.

**Everything else is starter material the organization edits** — including the `system_admin` office
the catalog sketches, whose reason for existing is that someone has to hold `system.admin` before
anything can be granted. **What §12 must fix, and does, is the *shape* rather than the list**: a
`system.` permission is seeded `applies_to = unit`, so it can never arrive through an item grant. That
is not a configuration choice — it is the structural guarantee that a shared item cannot hand someone
authority over the permission system, and it is now carried by a column value instead of by a resolver
branch (§2).

**What the organization starts with, in one list.** The platform ships:

- **The permission vocabulary** — each code marked `is_system` so it cannot be deleted or renamed —
  spanning people, accounts, membership, groups, audiences, roles, guardianship, item grants, audit,
  legacy import, reporting, the thirteen `event.*` codes, and messaging. **The one complete list is
  [../appendix/permission-catalog.md](../appendix/permission-catalog.md)**; this document deliberately
  no longer keeps a second copy of it, because the two copies disagreed for exactly the reason the
  note above describes.
- **`grant_scope_type`**: `unit` (the only row that is not item-scoped), `event`, `person_group`,
  `role`, and `document` (deferred).
- **`selector_type`**: the thirteen operands of §8's language, **every one of them seeded, `is_system`
  and implemented in the shipped evaluator, because there is no fourth combination and no third kind**
  (§8, *The selector registry*). **This registry is what both the grant editor's dropdown and the
  parser's reserved words read**, which is what D-101 means by *the language becomes data* — a new
  operand is a decision entry, a seed row **and a resolver arm in one release**, never a row typed into
  a screen and never a row shipped ahead of the code that evaluates it. `AUDIENCE` is the newest operand
  anyone *designed* ([D-103](../decisions/decision-log.md#d-103--an-audience-may-name-another-audience));
  `PERSON` is the thirteenth row and the last one to arrive, added because two decision entries had used it
  for a whole round while this table did not carry it (§8, [D-104](../decisions/decision-log.md#d-104--a-permission-codes-last-segment-is-an-action-and-a-registry-that-prose-contradicts-is-a-fiction)) —
  which is the difference between a registry and a list of what somebody remembered. `GRANTS` is refused and
  therefore absent (§8).
- **Two audiences, both `is_system`, and both must have a `code`**: `everyone`, whose expression is
  `EVERYONE`, and `all_members`, whose expression is `MEMBERS`. **The code is not cosmetic any more** —
  since D-103 it is the only way another audience can name them, so a seeded row without one is a
  piece of the resolver's vocabulary that nothing can compose with, and §11's check 12 is the net for
  the leaf side of that. **Whether `code` should simply be *required* on an `is_system` audience rather
  than merely seeded is a question this document does not settle** (§13). **The parameterized seeded
  audiences are gone**, and their three
  names are worth tracing because each became something smaller: `unit_participants` is `MEMBERS`
  (there is one unit), `unit_leaders` is `ROLE(x)` — **and it is the case this document had to correct
  in round 6, because the stored rule matched nobody while every grant aimed at it looked granted,
  which is the cautionary tale §8's evaluation rules are written against** — and `guardians_of` is the
  operand `GUARDIANS(person)`, or bound as `GUARDIANS` on a grant about that person. Nothing needs a
  row per unit any more, because there is one unit and no per-unit audience to parameterize. **A
  member row on either `is_system` row is refused**, and that is the whole of what survived `kind`:
  seeded rows are the resolver's own vocabulary rather than a set somebody curates (§8,
  *`audience_member`, re-roled as the `LIST` leaf*).
- **The `counselors` role**, above.
- **One seeded grant, and it replaces a hard-coded sentence: `event.answer.view` on an event, aimed at
  an audience whose expression is `ORGANIZERS`** — the code in the catalog's singular spelling, which is
  the registered one
  ([D-102](../decisions/decision-log.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it),
  amending [D-061](../decisions/decision-log.md#d-061--event-answers-are-read-by-that-events-organizers)).
  "Answers are read by that event's organizers" used to be prose the resolver implemented; now it is a
  row a reader can find, narrow, or delete, and it is the worked example of a **bound operand**:
  item-scoped, argument-less, meaning *the organizers of whichever event this grant is on* — which is
  why it is one grant in the seed rather than one per event. **[D-062](../decisions/decision-log.md#d-062--organizers-are-appointed-on-the-event-not-granted)
  is not contradicted**: the appointment still grants nothing by itself, because an operand is a set
  and not a grant. **It is written without `MEMBERS`** and must not be "corrected" to include it: an
  organizer appointed for one weekend is not required to be a paying member, and D-062's appointment
  model assumes exactly that.
- **The effects and the enums.** `allow` and `deny` arrive with the schema, as do the two values of
  `applies_to` and the two of `right_kind`. **This is the same argument the five levels used to be
  given** — a comparison the organization can edit at runtime is a security control with no owner —
  only now there is no comparison to edit, which is the point of
  [D-099](../decisions/decision-log.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality).
  The old sentence about `revoked` at rank 0 and `admin` at rank 40 is deleted with the ranks.

A few of the surviving codes carry a decision in their shape, and those are worth naming:

- **`person.merge` and `person.redact` are separate codes**, not flavours of `person.edit`. **They are
  separate for reach, not for irreversibility, and the two words were used as one here until round 9.**
  `person.redact` is irreversible — that is what an erasure is. `person.merge` is **not**:
  [D-087](../decisions/decision-log.md#d-087--merge-chains-stay-because-reversing-a-merge-is-a-supported-operation)
  made reversing a merge a supported operation, with the undo written as its own audit entry. What both
  codes share is that they act on **every row of a person's life** rather than on one field, which is
  the reason they were pulled out of `person.edit` — and with no `person.admin` to imply them (D-068),
  a role that reaches them does so by listing them, visibly.
- **`person.view` reaches the whole record, and round 10 made it reach further still.** Since
  [D-083](../decisions/decision-log.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)
  there is no privileged corner of the record for it to stop outside: whoever holds it over a person
  reads their descriptive values — the allergy list, the insurance number, the note about who the child
  actually lives with — on the same grant that reads their name
  ([09-attributes.md §4](09-attributes.md#4-who-may-read-and-who-may-write)). **And since D-097, a
  grant of it at the unit reaches every member in the organization**, because that is what "at the
  unit" now means; the safeguarding property that used to narrow it — access to a body's children
  granted *by that body* — is recorded as lost in §5 and in D-097. It is therefore the widest read
  permission in the system, and **the catalog's sensitivity mark is where that has to be visible**
  ([D-086](../decisions/decision-log.md#d-086--a-sensitivity-mark-grades-what-a-grant-exposes-not-the-table-it-reads)):
  the honest mark is the top tier, worded around *whose* data a grant exposes rather than around a
  category of fields, because a category is what D-083 deleted.
- **`audit.view` is graded against what the trail quotes, not against what a log is usually for.**
  `audit_log` carries before and after images, and since
  [D-085](../decisions/decision-log.md#d-085--the-identity-machinery-stays-structured-the-boundary-is-rules-not-sensitivity)
  those images are the only place a child's past descriptive values exist; reading history has to sit
  in the same tier as reading a person. **D-088 bounds the exposure to 24 months and fixes nothing**,
  and the bound is the realistic control for an organization of this size rather than an argument that
  the mark is right — see §9 and
  [AT-4](../open-questions.md#at-4--is-one-permission-enough-to-guard-a-trail-that-holds-person-data)
  for why two years is not a short interval when the question is about a child.
- **`attribute.define` is the narrow half of a deliberate pair**: values are open to anyone who may
  already edit the person, so that the fact gets recorded, and codes are held by few people, because
  the codes are what make the data queryable
  ([09-attributes.md §2](09-attributes.md#2-attribute_definition--the-vocabulary)). An ordinary
  permission — no namespace, no resolver branch, no structural consequence.
- **`person_group.member.manage` is how "joining a group is somebody else's act" is said now**
  ([D-098](../decisions/decision-log.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority),
  carrying
  [D-095](../decisions/decision-log.md#d-095--units-carry-no-restrictions-joining-one-is-somebody-elses-act)
  across the rename): held at the unit, where it reaches every group, or granted on one group as an
  item. **There is no self-scoped variant and none will be added** — nobody writes themselves onto a
  roster. Its counterpart for offices is `role.assign` 🔒🔒, and the gap between the two marks is the
  whole content of D-100's "why two tables".
- **`role.unassign` is one of the only two things that end authority** (the other is a holder row's
  `valid_to`), because a role has no period (D-053) and nothing forces a holder row to end (D-071).
- **`membership.terminate` expels**, and is restricted as such; `membership.lapse` is an
  administrative end for non-payment. **Neither now changes what a role grants** — that used to be the
  interesting part of both, and it was the membership gate's business, which is gone. A lapse changes
  what `MEMBERS` means, which is a different thing, in a different place.
- **`event.presence.mark` stays a separate code from `event.manage_participants` on purpose**, and
  **`event.register_self` *is* the eligibility rule**
  ([D-060](../decisions/decision-log.md#d-060--eligibility-is-capability-there-is-no-separate-rule-engine))
  rather than an expression of one. Under the ladder the first sentence meant "one rank below"; with
  ranks gone it means what it should have meant all along — **a volunteer leader is handed the register
  without being handed the roster** — and that difference is now two grant rows rather than a rung.
- **There is no wildcard at all, and that is worth noticing.** `dependent.admin` was the last
  deliberate one, and D-074 replaced it with `right_level = write`, which does the same job **without
  being a permission**. The residue is the opposite problem: with no wildcard, nothing implies
  anything, so a role that should have a new permission must be told (check 13 is the net).
- **Reporting is seeded coarse, and left open on purpose.** Only `report.view` and `report.export` are
  starters. Whether reporting is per-report or one permission with row-level filtering is still open
  (catalog §12). Do not ship both shapes; pick one when reporting is designed.

> **`system.admin` is deliberately a single top-level permission**, not a
> per-resource one. Holding it satisfies everything, and check 9 in §11 alerts on its
> holders. Keeping the most dangerous capability concentrated and alarmed is safer than
> spreading equivalents of it across every resource. **Under the deleted ladder it was also the level
> called `admin**, which is how this corpus came to have two unrelated things named "admin" and to
> need a paragraph telling readers they were different. That paragraph is now about one thing.

---

## 13. Open issues

- The complete permission catalog and real role definitions (§12) — needs your input. **The question
  changed shape with
  [D-100](../decisions/decision-log.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape):**
  it used to ask which roles are marked `requires_membership = false`, a per-row switch. There is no
  switch now, so the question is **which starter grants are written with `MEMBERS` in the expression
  and which are not** — and it has to be answered per grant rather than per role, with check 6 (§11)
  as the net and the seeded grants as the default.
- **Whether the API should refuse a check that names an item for a unit-only code (§2).**
  `applies_to` is deliberately a save-time rule, and D-099 says so in as many words, so the mismatched
  *grant* cannot exist — but a *caller* that asks `can(person, 'event.create', 'event', 1204, …)`
  gets the unit's answer rather than an error. **Assumption, not a ruling:** the honest answer is a
  refusal at the API layer naming the code and the scope, because a caller that asks that question has
  a bug worth surfacing. Nothing in D-097..D-103 settles it.
- **What the default `selector_depth_limit` should be (§8).** **It is written here as 3, which is a
  placeholder chosen to be small, and it is a parameter rather than a rule precisely so that answering
  this bullet is an `UPDATE` rather than a release** (D-048's argument for the same shape on the
  renewal window, inherited here from `include_depth_limit`). What would justify a different number is
  a real count of how expressions get composed in practice, which nobody has yet — **and since D-103
  the question is two questions, because the bound measures height while the cost of an expression is
  now proportional to how many *audiences* it reaches.** A depth-3 limit allows a wide flat sum of
  twenty `AUDIENCE()` leaves and prices each one at a fetch (§11, check 15 half 2), so answering "is 3
  right?" without also deciding whether fan-out needs a bound of its own answers only the half that was
  already here. **No fan-out limit is asserted anywhere in this document**, on the grounds that inventing
  a second parameter nobody asked for is not this page's call to make.
- **Whether an expression's *fingerprint* should be computed on save (§8).** D-101 registered it
  rather than promising it: two expressions with the same meaning are two different row sets, so "you
  already granted exactly this set on that item" no longer falls out of storage. **A warning, never a
  refusal** — normalization informing a human, not gating one — and if the expansion overflows, skip
  the warning.
- **The per-item reach preview (§8) is a screen nobody has designed.** `PLACED` means different people
  on different events, so the editor's expanded set must be computed *for an item* and say so on
  screen
  ([D-102](../decisions/decision-log.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)).
  D-091 made the expanded set a requirement; D-102 made it depend on an input the grant does not
  contain. Which item the editor picks by default — the grant's item, an event the writer chooses, the
  next event with registrants — is not decided anywhere.
- **`WHITELISTED` (§8): no stored state to name, so no selector.** Either it means `source = staff`,
  or it means promotion off the waitlist, or it is a new column on `event_registration` — which is an
  events decision and not a selector decision. It is listed here so that it stays a question rather
  than becoming a word in a grammar.
- **`PERSON(x)` — closed by this round, and the way it closed is the open item.** Two decision entries wrote
  `PERSON()` and the seeded registry in §8 did not contain it, so this page concluded the operand did not
  exist and read both examples as `LIST`. **That was the wrong reading** (it cannot express D-103's example),
  the registry was the side that was wrong, and the row is seeded now: `argument_type = person`, thirteen rows
  total ([D-101's amendment](../decisions/decision-log.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree),
  [D-104](../decisions/decision-log.md#d-104--a-permission-codes-last-segment-is-an-action-and-a-registry-that-prose-contradicts-is-a-fiction)).
  **What is still open is the class, not this operand:** nothing in this module, or in this repository,
  compares the dotted tokens these documents write against the seeded registries they describe, so the same
  drift will happen again in whichever table is written next. D-104 adopts a hand-run report over the
  documents as the answer, and states plainly that **a report nobody runs is a convention** — there is no CI
  here to make it a guard, and no layer of this spec can tell a writer that `PERSON(` had no row behind it.
- **Whether the `LIST` gloss is enough, or the operand should be renamed `ADDED` (§8).** D-103 records
  the name as the weak part of the design and refuses the rename only because the round has carried
  `LIST` through four files and a registry gloss costs nothing. **The cost of a rename goes up every
  round it is deferred**, since stored expressions would need rewriting and this corpus has already
  declared that stored expressions are never silently rewritten. If it is going to change, now is
  cheaper than later.
- **Whether the reference listing is actually cheap (§8, §10).** D-103 registers the assumption: "which
  live grants name this audience, and at what depth" is one indexed query over the leaf rows, cheap at
  this organization's size, **unverified at any size**. It is on the save path of a screen a person is
  standing at, and it is also what the wholesale cache invalidation is standing in for. If the import
  corpus's row-count estimates are wrong, the two decisions that follow — compute the closure on save,
  or keep invalidating everything — are one decision, not two.
- **Whether `audience.code` should be required rather than optional on `is_system` rows (§8, §12).**
  The seeded audiences are the resolver's vocabulary and cannot be composed with by anything that lacks
  a code, which makes the code mandatory in every practical sense while leaving it nullable in the
  schema. **A check is being asked to assert what a column could have guaranteed**; making the column
  required-where-`is_system` would be the honest fix and is not this document's call to make.
- **Whether a nested audience's past reach should be reconstructable (§8, *Three named sets*).**
  `GROUP(x)` answers *"was she in it on 1 June 2024?"* from its dated rows and `AUDIENCE(x)` cannot,
  because it is a rule and the trail that recorded its shape is reduced after 24 months
  ([D-088](../decisions/decision-log.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)).
  D-103 says the gap should be closed by a report rather than by pretending the question has an answer.
  **The report is the same listing as the bullet above, kept over time** — which makes this a question
  about whether to store history, i.e. [F-7](../open-questions.md#f-7--cache-vs-materialized-effective_permission-table),
  and it is filed there rather than answered here.
- **Whether `membership` belongs in `grant_scope_type` (§6).** It is not seeded, and that is an
  inference from what D-097 and D-099 list rather than a ruling; the old seed had the row.
- Whether `valid_to` should be mandatory for high-authority holder rows and long-lived item grants
  (§4, §6).
- Polymorphic `scope_id` vs a `grantable_item` supertable (§6) — a real fork, now covering
  `selector_arg_id` too.
- How long a `permission_cache` entry may live (§10) —
  **[F-6](../open-questions.md#f-6--the-permission-cache-lifetime-and-what-invalidates-it), whose
  shape
  round 10 changed.** It used to be a question about the membership sweep's TTL. It is now two caches
  with different keys — an answer cache and a per-operand cache, the second keyed on the item whenever
  the operand binds — and **there are now two invalidations that cannot be keyed on the rows that were
  written**, not one: `role_holder` (one holder row, every grant naming that office) and a write to any
  audience's tree, which since D-103 must also clear every audience that can *reach* the one written.
  **The blunt answer — invalidate audience-keyed entries wholesale — is the recommendation, and the
  open question is whether it stays affordable** (see the reference-listing bullet above).
- Cache vs materialized effective-permission table (§8, §10) —
  **[F-7](../open-questions.md#f-7--cache-vs-materialized-effective_permission-table), and D-091 is the
  round that made it a history question rather than a performance one.**
- Retention policy for `access_log` — legal input required
  ([F-8](../open-questions.md#f-8--retention-policy-for-access_log)).
- Whether `access_log` needs human annotation (recommend a separate table if so).

**Resolved and no longer open**, kept visible so the reasoning survives: **whether a role may be held
by a rule — [F-12](../open-questions.md#f-12--closed--may-a-role-be-held-by-a-rule-as-an-audience-is), closed
by D-100, and the answer is no**; whether an audience may compose other sets (**yes, three times over,
and the third answer is the settled one**: D-091 through an inclusion graph, D-101 through an
expression naming only rosters, and D-103 through `AUDIENCE()` — the edge table stays deleted and the
edges are leaves); whether a saved rule may be reused by name (**yes, and only if it has a `code`,**
which D-103 settled after D-101 answered it in effect by accident); whether permissions depend on
membership status (**the gate is deleted and membership is an operand**, with the posture opt-in per
grant); the bulk exposure tool (removed — D-045), the exposure model itself (deleted — D-097), the
level ladder (deleted — D-099), positions and their appointment workflows (deleted — D-100), and
background-check permissions (removed — D-043).

All tracked in [../open-questions.md](../open-questions.md).
