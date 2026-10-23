# Data Model — Authorization

`permission`, `role`, `role_permission`, `role_assignment`, `scope_exposure`,
`access_grant`, `permission_level`, `access_log`.

This is the direct answer to your question about system-wide and per-item permissions.
Design rationale: [../domain/06-authorization-model.md](../domain/06-authorization-model.md).

---

## 1. The shape of the answer

```
permission ────────────── the atomic capability.      'membership.request.approve'
     ▲
     │ many-to-many
role ───────────────────── a named bundle.            'registrar', 'unit_leader'
     ▲
     │ assigned for a period, within a scope
role_assignment ────────── SYSTEM-WIDE authority.     person X, role R,
                                                      scope 'org_unit' 12,
                                                      2026-01-01 → 2026-12-31

access_grant ───────────── PER-ITEM authority.        person X, item ('event', 55),
                                                      level 'manage', until 2026-06-30

guardianship_permission ── authority over a PERSON.   (04-relationships.md)

scope_exposure ─────────── upward delegation.         unit 7 agrees that assignment
                                                      912's authority covers unit 7.
```

Four tables carry authority. They are separate because their lifetimes, granters, and
revocation semantics differ — argued in
[../domain/06-authorization-model.md](../domain/06-authorization-model.md#1-the-four-channels-of-authority).

**And the rule that governs all of them:** authority over a unit originates **at that
unit** and cannot be claimed from outside it — not by a parent unit, and not by the
organization. `scope_exposure` (§5) is the only way it crosses a boundary downward, and
`system_admin` is the sole exception. See
[../domain/06-authorization-model.md](../domain/06-authorization-model.md#2-scope-authority--no-downward-inheritance).

**The key insight:** `role_assignment` and `access_grant` are not two unrelated
mechanisms. They are the **same idea at two granularities** — authority held for a period,
within a scope, granted by someone. They share the scope model and the resolver, and differ
only in what they point at:

| | `role_assignment` | `access_grant` |
|---|---|---|
| Points at | A `role` (a bundle of permissions) | Always exactly one permission's worth of intent, at a level |
| Scope | `organization` or `org_unit` | Any registered `scope_type`, including concrete items |
| Cardinality | Few rows per person, long-lived | Many rows, frequently short-lived |
| Typical use | "is the treasurer" | "may manage this event" |

---

## 2. `permission`

**Fields**

| Field | Kind | Notes |
|---|---|---|
| `id` | integer identity | Surrogate key. |
| `code` | text, required, unique | The stable identifier — `membership.request.approve`. The **code never changes**; `display_name` can. |
| `resource` | text, required | What the permission is about — `membership_request`. |
| `action` | text, required | What may be done to it — `approve`. |
| `namespace` | text, optional | `system`, or absent. It says one thing: a `system.` permission is resolved against role assignments and never against an item grant. It no longer selects a channel — see §2. |
| `description` | text, required | What it means, for whoever has to read it. |
| `display_name` | text, required | Human label for the permission editor. |
| `is_system` | boolean | Default false. True: seeded by the platform, cannot be deleted or have its `code` changed. |
| `is_assignable` | boolean | Default true. False: a permission **no grant may name directly** — a deprecated narrow code kept only so historical audit rows still resolve to something readable. Before [D-068](../decisions/decision-log.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle) this also flagged wildcard `.admin` codes; there are none now. |
| `requires_scope` | enum: `organization`, `org_unit`, or absent | A value here forces the granting role/assignment to be scoped accordingly — a unit-level permission cannot be granted organization-wide by mistake. |
| `created_at` | timestamp, audit time | |

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

**Indexes**

- one covering only the rows that carry a `namespace`.

### There is no wildcard permission

A check for `X.y` is satisfied by **an exact grant of `X.y`**, or by `system.admin`, which is
checked outright and is the only permission meaning *everything*.

```
A check for permission 'X.y' is satisfied by:
    - an exact grant of 'X.y', OR
    - a grant of 'system.admin'   (NULL-namespace permissions only)
```

**There are no `<resource>.admin` codes.** The convention that every resource should expose
one, matched by prefix in the resolver, was **reversed by
[D-068](../decisions/decision-log.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle)**,
which also removed the resolver branch that implemented it. "Can do everything about events"
is a **role** composed from the thirteen `event.*` codes, because roles are runtime data the
organization composes (D-052) and a wildcard was the code guessing at that bundle instead.

**The cost is the one D-007 existed to prevent, and it is accepted:** a new narrow permission
is not automatically covered by the roles that should imply it. Integrity check **18**
(permissions no role grants) is the net the wildcard used to be. It fails closed.

`is_assignable = false` exists for permissions that only make sense as part of a bundle —
a deprecated narrow permission kept for historical audit readability, for instance.

### What `namespace` does now, and what it no longer does

| `namespace` | Resolved against | Example |
|-------------|------------------|---------|
| absent | roles, item grants, ownership | `membership.request.approve` |
| `system` | `role_assignment` only (never item grants) | `system.permission.edit` |

There used to be a third value, and this section was about it. `dependent.` prefixed every
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

What remains for the column is `system`, and it earns its keep: a `system.` permission is
never satisfiable by an item grant, so no one can hand someone authority over the permission
system by sharing an item with them. A new namespace is still a data change plus one resolver
branch — that much of the original design survives, it just has only one tenant now.

---

## 3. `role` and `role_permission`

**Fields** (`role`)

| Field | Kind | Notes |
|---|---|---|
| `id` | integer identity | Surrogate key. |
| `code` | text, required, unique | `registrar`, `unit_leader`. |
| `name` | text, required | |
| `description` | text, optional | |
| `is_system` | boolean | Default false. True: seeded — cannot be **deleted**, and its `code` cannot be changed, though its permissions may be edited. False: an ordinary role the organization created and may delete. |
| `scope_required` | enum: `organization`, `org_unit`, or absent | Absent = assignable at either scope. `organization` = only org-wide. `org_unit` = only within a unit. |
| `requires_membership` | boolean | Default true. **The membership gate (D-039), at role level.** True: the resolver honours this role only while the holder has a current membership — a lapse silently withholds the role's permissions. False: the role is honoured regardless, which is what keeps appointed counselors and local leaders able to serve while their own fee is unpaid. Enforced by the resolver, not merely reported. This is the **blunt** form of the exemption: it exempts everyone holding this role, everywhere. The **precise** form is `system.gate_exempt` (D-051), which exempts a named person across every role they hold. The resolver honours a role if **either** applies; the two compose and answer different questions. |
| `max_term_months` | integer, optional | Default term length. Used to prefill `valid_to`, and to flag assignments that have run past their expected term. |
| `is_delegatable` | boolean | Default true. False for `system_admin` and similar. See domain/06 §2.6. |
| `sort_order` | integer, required | Default 0. |
| `created_at` | timestamp, audit time | |
| `updated_at` | timestamp, audit time | |
| `updated_by` | reference to person | Who last changed it. |

**Rules**

- `code` is unique.
- `scope_required` is `organization`, `org_unit`, or absent.
- `max_term_months` is either absent or greater than zero.
- The membership gate cannot be enforced on the row: whether it bites depends on membership,
  which is temporal state in another table. It is consulted at check time instead (D-039).

> **`role` has no `valid_from` / `valid_to`, deliberately** ([D-053](../decisions/decision-log.md#d-053--a-role-is-valid-always-only-its-assignment-is-temporal)).
> A role is a **definition** — a named bundle of permissions — and a definition does not come
> into and out of force. It is valid all the time, for as long as the row exists.
>
> **The period belongs on the assignment.** `role_assignment.valid_from` / `valid_to` is where
> "this person holds this role from March until December" lives, and it is unchanged. The
> distinction is between *what the role is* and *who holds it*: the first is not a historical
> fact, the second is.
>
> This removes the whole retirement mechanism. There is no `role.retire` permission, no
> resolver check on the role's period, and no report of roles expiring while still held. A
> role the organization no longer uses is one nobody holds any more.

**Fields** (`role_permission`)

| Field | Kind | Notes |
|---|---|---|
| `id` | integer identity | Surrogate key. |
| `role_id` | reference to `role`, required | |
| `permission_id` | reference to `permission`, required | |
| `granted_by` | reference to person, optional | Who put the pair together. |
| `granted_at` | timestamp, audit time | |

**Rules**

- A role names a given permission at most once.
- The row carries no period. The pair either stands or it does not, which is why editing it
  takes effect immediately for every holder.

**`role` is runtime data, not a fixed vocabulary.** The organization creates roles, composes
them from permissions, assigns them to people, edits what they grant, and deletes the ones
nobody ever held. The seed set in §12 is a starting point to edit, not a specification.

The one asymmetry: a role that has ever been assigned **cannot be deleted**. Three reasons, in
order of how loudly they would bite:

1. **`role_assignment.role_id` is an FK.** Deleting the row would either fail or take the
   assignment history with it, and D-003 forbids the latter.
2. **The history is the point.** "What authority did this person have in 2019?" must survive
   the role being abolished, which is exactly when someone asks.
3. **`is_system` roles must survive regardless** — deleting `system_admin` would remove the
   only route to `system.admin` and lock everyone out permanently.

**Deletion is therefore reserved for a role created by mistake and never assigned.** A role
that was used is left as it is: it is valid always
([D-053](../decisions/decision-log.md#d-053--a-role-is-valid-always-only-its-assignment-is-temporal)),
so there is nothing to switch off. A role the organization no longer wants is simply one
nobody holds — the assignments end, and the definition stays as the answer to "what did that
role mean?".

The guard runs on each row before it is deleted, and refuses in this order:

1. If any `role_assignment` references the role, the delete is refused, with a message in terms
   the operator can act on — this role has assignments and cannot be deleted, end the
   assignments instead so the history survives.
2. Otherwise, if the role is marked `is_system`, the delete is refused outright.

Both refusals are absolute. A role that clears both was created by mistake and never assigned,
and deleting it is legitimate.

**Editing a role's permissions takes effect immediately**, with no assignment touched — every
holder's next permission check sees the new set. That is the intended behaviour and it is also
the sharpest edge in the whole authorization system: `role.edit` is a bulk privilege change
wearing the clothes of a configuration screen. `role_permission` is therefore audited like any
other business table ([06-audit-and-import.md](06-audit-and-import.md)), so "what did this
role grant on that date?" is answerable after the fact — which is the only defence, since
there is nothing to check *before* the fact. The catalog marks `role.edit` 🔒🔒 for this
reason, alongside `role.assign`.

> **This is why a role having no period matters more than it looks.** Because a role is valid
> always, the *only* thing that makes authority end is the assignment ending. That puts the
> entire weight on `role_assignment.valid_to` — which is exactly where the design already
> wanted it, and why the open-ended assignment is called out as the classic access failure
> (§4).

**`role.requires_membership` is enforced by the resolver, not by a constraint.** It depends on
temporal state in another table, so no `CHECK` can express it — but unlike a mere report
flag, it is consulted at every permission check (D-039). A role with
`requires_membership = true` held by someone without a current membership **grants nothing**,
though the assignment row survives so the history is intact and a renewal can reinstate it.

**The "leaver with access" report is still worth running** — not to prevent access, which the
resolver already does, but to find assignments that should have been *closed* and were not.
Dormant authority that springs back on renewal is the failure mode this gate introduces; see
[03-membership.md](03-membership.md#6-membership-and-the-authorization-system).

**`max_term_months` turns "the volunteer who never got removed" into a visible expiry.**
The classic access failure is not a malicious grant; it is a legitimate one that nobody
remembered to end. Prefilling `valid_to` from a term length makes expiry the default and
permanence the deliberate act.

**No permission inheritance between roles.** A `unit_leader` does not get the
`assistant_leader` permissions by being implicitly senior. Inheritance chains in an RBAC
model produce authorization answers that nobody can predict by reading the configuration,
which is exactly what makes such systems undebuggable. If `unit_leader` should have them,
grant them explicitly.

---

## 4. `role_assignment` — system-wide authority

**Fields**

| Field | Kind | Notes |
|---|---|---|
| `id` | integer identity | Surrogate key. |
| `person_id` | reference to person, required | Who holds the role. |
| `role_id` | reference to `role`, required | |
| `scope_type` | enum: `organization`, `org_unit` | Required. Default `organization`. |
| `scope_id` | reference to `org_unit`, optional | Absent for organization scope; a unit id otherwise. |
| `valid_from` | date, required | Default today. |
| `valid_to` | date, optional | Absent = open-ended. **Discouraged** — see below. |
| `granted_by` | reference to person, required | An authority nobody granted is not something this table records. |
| `granted_at` | timestamp, audit time | |
| `grant_reason` | text, optional | |
| `ended_by` | reference to person, optional | |
| `ended_at` | timestamp, audit time, optional | |
| `ended_reason_code` | text, optional | |
| `ended_note` | text, optional | |
| `delegation_of` | reference to `role_assignment`, optional | Set when this assignment is a delegation of another assignment's authority. Forms a chain; the resolver re-validates the source at use time. |
| `created_at` | timestamp, audit time | |
| `updated_at` | timestamp, audit time | |
| `updated_by` | reference to person | |

**Rules**

- `scope_type` and `scope_id` agree exactly: organization scope means `scope_id` is absent, unit
  scope requires one. There is no third shape.
- `valid_to` is either absent or strictly after `valid_from`.
- An assignment is never its own delegation: `delegation_of` does not equal `id`.
- An ending is recorded only on a closed row: if `ended_at` is set, `valid_to` is set. The
  converse is not required — a period can be closed without naming who closed it.
- **At most one open assignment** of a given role to a given person in a given scope, and
  organization-wide and one specific unit are different scopes. It counts **open rows only**: a
  person may have been treasurer of unit 7 three times, and be treasurer of it once.

**Indexes**

- over open rows only, by scope — the query is "who has authority over unit 7 right now";
- over open rows only, by person and role;
- restricted to rows expiring within the next 60 days, which is the read the nightly expiry
  report below depends on.

### The open-ended assignment is the classic access failure

> *"The volunteer who stepped down in 2019 still has treasurer access in 2026."*

Every high-authority role assignment should have a `valid_to`. Two mechanisms push toward
that:

1. `role.max_term_months` prefills it.
2. A **nightly report** of assignments expiring within 60 days
   (`ix_role_assignment_expiring` is the index for it), so renewal is an active decision
   rather than a forgotten default.

*Assumption:* `valid_to` is optional in the schema but required by application validation
for any role with `scope_required` set. Making it a database `NOT NULL` would break
historical imports (where end dates are genuinely unknown), so the requirement is enforced
one level up. Tracked in [../open-questions.md](../open-questions.md).

### Scope — exact match, plus explicit exposures

A unit-scoped role assignment covers **that unit only**. It does **not** cover the unit's
children. Authority does not flow down the hierarchy — see
[../domain/06-authorization-model.md](../domain/06-authorization-model.md#2-scope-authority--no-downward-inheritance)
for the full reasoning.

Authority crosses a unit boundary downward through exactly one mechanism: an explicit
`scope_exposure` row, written at the subordinate unit, granting a specific role assignment
coverage over it. See §5.

**The resolver matches `scope_id` exactly, plus exposures.** It must **not** call
`unit_ancestors()`. Any occurrence of `unit_ancestors()` in a permission path is a bug —
see §10, integrity check 13.


### `delegation_of`

Delegations are `role_assignment` rows pointing at the assignment they delegate. Two
required properties:

- **A delegation must always have `valid_to`.** Enforce with a constraint:

  if `delegation_of` is set, `valid_to` must be set — a delegation is never open-ended.

- **The delegation may not exceed the source.** Validated at grant time *and* re-validated
  at every permission check, because the delegator may have lost the authority
  mid-delegation. A stale delegation is a privilege-escalation vector.

---

## 5. `scope_exposure` — how a unit delegates upward

The only mechanism by which authority crosses a unit boundary downward. Read
[../domain/06-authorization-model.md](../domain/06-authorization-model.md#2-scope-authority--no-downward-inheritance)
first — this table exists to implement that rule, and it is easy to misread as inheritance.

**Fields**

| Field | Kind | Notes |
|---|---|---|
| `id` | integer identity | Surrogate key. |
| `org_unit_id` | reference to `org_unit`, required | **The unit granting coverage over itself.** This is the grantor. It is never the unit being reached into from above. |
| `role_assignment_id` | reference to `role_assignment`, required | The assignment whose authority is honoured over this unit. Points at a specific **assignment**, not at a role — so a unit approves a person-in-a-role, not a role that any future holder would inherit. |
| `valid_from` | date, required | Default today. |
| `valid_to` | date, optional | Absent = open. |
| `exposed_by` | reference to person, required | The person who exposed the scope. **Must hold `scope.expose` at `org_unit_id`.** **This check cannot be a constraint** — no foreign key or check clause can express "this person holds a permission at that unit as of that date", because the answer comes from the resolver. So it belongs in the write path, **inside the same transaction as the row**, asking the resolver for the answer as of `valid_from` rather than as of now. That placement is the requirement: checked after the insert it can be raced, checked in a form that validates a draft it can be bypassed by any writer that skips the form. **The check asks the resolver, and so an ancestor-unit holder is rejected — exposure cannot be imposed from above** ([../domain/06-authorization-model.md §2.5](../domain/06-authorization-model.md#25-enforcing-the-direction-of-authority)); nothing about moving the schema into an ORM relaxes that. Because no database rule backs it, invariant 10 is not a belt-and-braces report here — it is the only thing that detects the check being missing. |
| `exposed_at` | timestamp, audit time | |
| `exposure_reason` | text, required | e.g. "the treasurer handles our finances", "the registrar processes our membership". Required because the point of the rule is that coverage is deliberate and attributable. |
| `withdrawn_by` | reference to person, optional | |
| `withdrawn_at` | timestamp, audit time, optional | |
| `withdrawal_reason` | text, optional | |
| `created_at` | timestamp, audit time | |

**Rules**

- `valid_to` is either absent or strictly after `valid_from`.
- A withdrawal names who made it: if `withdrawn_at` is set, `withdrawn_by` is set.
- **At most one live exposure per unit and assignment.** Live means still open *and* not
  withdrawn; withdrawn or ended rows do not count against it, so a unit may expose and withdraw
  against the same assignment repeatedly over the years.

**Indexes**

- both lookup directions — by unit, and by the assignment exposed — restricted to live rows,
  which is the only state the resolver ever reads.

### An exposure extends an assignment. It never extends a grant.

An exposure row points at a `role_assignment_id`. Not at a role, and not at an
`access_grant`. That is not a detail of the table, it is the whole mechanism: the unit is
agreeing that **this person, in this role, for this period** may act here, which is why the
resolver's role channel (§10, tier D) is the only channel that reads this table.

**Direct grants are not extended, and could not be.** A grant names a person and a scope;
there is no assignment in it for an exposure to attach to, and a grant already at the checked
unit needs no extension to work there. So the unit-grant tier matches exactly and stops.

> **How we know this, and why it is written down.** Until D-072 deleted the SQL, the unit-grant
> tier had a *second* branch that looked like it consulted exposures. It did not: it joined the
> grant to the exposure's own unit, and required the exposure to be at the unit being checked,
> so the two conditions pinned the grant to the checked unit — which the first branch had just
> tested. The branch could never succeed where the first branch failed. It was dead code, and it
> had survived every review because it *read* correctly.
>
> Removing the SQL surfaced it. Nothing here changes what the system decides — a dead branch
> decides nothing — but two things are now different. The prose states one route, because
> stating two would describe a capability that never existed. And the reason the branch is
> absent is recorded here, on purpose, because "why doesn't an exposure extend my direct
> grant?" is going to look like an oversight to whoever asks it next, and the tempting repair
> would let a unit's direct grant reach a subordinate unit through an exposure written for
> someone's *role* — quietly widening an exposure to cover a person the exposing unit never
> approved. See [D-078](../decisions/decision-log.md#d-078--an-exposure-extends-an-assignment-never-a-direct-grant).

### There is no bulk tool and no reason-prefix convention

**Every row in this table is written by the unit it covers.** There is no administrative
shortcut, no `bulk:` marker, no exemption branch in the write-time check, and no review report
(D-045).

This was previously the design's most uncomfortable compromise — a tool that let a parent
write exposures on a child's behalf, argued for on grounds of scale. Your answer removed the
need for it: *"If the unit wants to expose something (a single event eg), they set the
permissions to that event for 'everyone' or a group of people."* Once **audiences** (§8) can
express "open this to everyone", the bulk case largely evaporates, and the rule becomes
absolute with nothing to explain.

**If a unit genuinely wants a higher-level officer to have authority over it,** its own
leadership writes the exposure. That is the whole rule, and now it has no exceptions.

### Why the key is the unit, and not the assignment

`org_unit_id` is the **subject and the grantor simultaneously** — the unit is granting
coverage over itself. This is what makes the direction of authority structural rather than
a convention:

- A row `(org_unit_id = 7, role_assignment_id = 912)` means *unit 7 has agreed that the
  authority held by assignment 912 applies to unit 7*.
- There is no way to express "assignment 912 covers unit 7 whether unit 7 likes it or not",
  because that row would still have to be written at unit 7.

A parent unit that wanted to reach down would have to insert a row naming the child as
grantor — which `trg_exposure_direction` rejects (domain §2.5), and which integrity check 9 reports.

### Why it points at an assignment, not a role

Pointing at `role_id` would mean a unit exposes its scope to *"whoever holds the treasurer
role"*. A person appointed treasurer two years later would silently gain access to that unit
without the unit ever being consulted. Pointing at the assignment forces a **new exposure
decision** whenever the holder changes — which is the behaviour the rule is for.

### The `scope.expose` permission

Creating an exposure requires:

```
can(actor, 'scope.expose', 'org_unit', <the unit being covered>)
```

Note the scope is the unit being covered, not the actor's own unit. An officer holding
`scope.expose` at a **parent** unit **cannot** satisfy this for a sub-unit, because they
hold nothing at the sub-unit. That single fact is what makes the whole rule enforceable.

`scope.expose` is an ordinary, narrow permission with **no wildcard that implies it** —
[D-068](../decisions/decision-log.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle)
deleted `org_unit.admin`, which previously reached it by prefix match. **That is an improvement
worth naming.** Under the old rule, "may administer this unit" silently included "may hand a
parent unit authority over this unit's records" — the single most consequential act available
at unit scope, carried as an implication of a general-purpose administrative permission and
invisible in the role editor. It is now grantable **only by naming it**, which is the correct
weight for the door it opens. See §11 for the seed row.

### Practical scale — no bulk tool, and why that is now fine

Exposing many units one at a time would be tedious, and the earlier design addressed that
with a bulk tool. **It is removed** (D-045), for a reason worth recording: once grants can
target **audiences** (§8), the common case it existed for — "let everyone / the whole group
see this event" — has a direct expression that needs no exposure row at all.

What remains is the genuinely narrower case: *this specific person, in this specific role,
should have authority over our unit.* That is a deliberate act by the unit, it happens
rarely, and doing it once per unit is the correct amount of friction rather than an
obstacle.

---

## 6. `access_grant` — the per-item layer

This is the "per-item permission" table. You specified it means a **capability on that
item**: "person X may act on item Y".

**Fields** (`grant_scope_type`)

| Field | Kind | Notes |
|---|---|---|
| `code` | text, required, unique | `event`, `document`, `org_unit`, `membership`. The key a grant points at. |
| `name` | text, required | |
| `item_table` | text, required | The table `scope_id` references — `event`. |
| `is_item_scoped` | boolean | Default true. False for scope kinds that are organizational rather than a concrete item (`organization` itself). |
| `supports_levels` | boolean | Default true. |
| `description` | text, optional | |

**Rules** (`grant_scope_type`)

- Every `access_grant.scope_type` names a row here. This is the one piece of referential
  integrity the polymorphic scope does get.

**Fields** (`access_grant`)

| Field | Kind | Notes |
|---|---|---|
| `id` | integer identity | Surrogate key. |
| `person_id` | reference to person, optional | The grantee, when the grant names one person. |
| `audience_id` | reference to `audience`, optional | The grantee, when the grant names a set. This is how "open this event to everyone" or "to the whole group" is expressed (§8); a grant to an audience is evaluated against the person being checked. |
| `scope_type` | reference to `grant_scope_type`, required | |
| `scope_id` | integer, optional | The concrete item id. Absent only when the scope type is not item-scoped. **No foreign key: polymorphic by design.** See the note below. |
| `level` | reference to `access_level`, required | `revoked`, `view`, `contribute`, `manage`, or `admin`. |
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
- `scope_id` is absent only at `organization` scope — and that is the whole of what the rule
  says. It constrains the absent case alone; `grant_scope_type.item_table` is what states which
  table an id belongs to.
- `is_delegated` and `delegated_from` agree in both directions: the flag is true exactly when a
  delegating person is named.
- A grant is never a delegation from the person it is granted to: `delegated_from` does not
  equal `person_id`.
- A revocation names who made it: if `revoked_at` is set, `revoked_by` is set.
- **A delegation must expire:** if `is_delegated` is true, `valid_to` is set.

### The uniqueness rule has to be careful with audiences

The obvious index — one live grant per (grantee, scope) — no longer works, because a person
can legitimately hold a **personal** grant *and* be covered by an **audience** grant on the
same item, and those are different rows with different lifetimes.

**Rules**

- **At most one live non-deny grant per person per scope** — counted over the rows that name a
  person and are open, unrevoked, and not at level `revoked`.
- **At most one live non-deny grant per audience per scope**, counted the same way over the rows
  that name an audience.

**Indexes**

- person, audience and scope lookups, each restricted to open rows;
- a deny-only index over open rows at level `revoked`, keyed by grantee and scope — channel 0
  runs a deny lookup on every check, at every scope.

**Denies are excluded from both unique indexes**, so a deny may coexist with a grant — which
is exactly what makes an explicit deny meaningful. A **personal deny beats an audience
allow**, because the deny check runs first and is scope-independent (§9, channel 0).

**Audience grants cannot be delegated.** `is_delegated` requires `delegated_from`, which is a
person, and delegating "everyone" is not a coherent act — so a check constraint enforces it:

If `audience_id` is set, `is_delegated` is false.

### `level` is the heart of the design

The four **grant levels** below are a different thing from the deleted `<resource>.admin`
*permissions*, and the shared name is an accident worth guarding against: a level says **how
much** authority a grant carries and is compared by rank; a permission code says **which**
capability. Only the codes were deleted. The ordered levels (defined in
[00-conventions.md](00-conventions.md#5-enumerations)):

| Level | Rank | Means |
|-------|------|-------|
| `revoked` | 0 | **Explicitly denied. Overrides every other grant, including roles.** |
| `view` | 10 | Read |
| `contribute` | 20 | Read and add (sign up, comment, submit) |
| `manage` | 30 | Full control of the item |
| `admin` | 40 | Everything, including granting others access to this item |

**Comparisons must use `access_level.rank`, never the strings.**
`'admin' < 'contribute'` lexicographically — a string comparison silently inverts the
order and makes the most powerful level the least. This is a security bug that throws no
error, and it is why the ranks are in a table rather than computed in code.

### Live-grant uniqueness excludes denies — deliberately

A deny must be able to coexist with a grant on the same scope, because that is the only
way to express "this person has access to the unit's events, except this one". So the rule
that keeps one live grant per person, item and scope — carried here as
`uq_access_grant_live` — **covers allow levels only**; a `deny` row is outside it by design,
and the resolver checks denies first.

**This is the rule's shape, not an implementation detail of an index** ([D-072](../decisions/decision-log.md#d-072--the-documentation-carries-no-sql-the-schema-is-the-orms-job)),
and the distinction is load-bearing here rather than pedantic: "unique among live *allowing*
grants" is a **conditional** rule, so the migration must emit a partial unique index whose
predicate excludes `deny`. A plain unique constraint over the same columns is a different and
wrong rule — it would refuse the deny beside the grant, which is precisely the pair the domain
requires. See [open question F-10, shape 2](../open-questions.md#f-10--which-invariants-the-orm-cannot-express-and-who-writes-those).

### No foreign key on `scope_id` — the accepted trade-off

`scope_id` has no FK because it is polymorphic. This is a deliberate choice:

| | Polymorphic `scope_id` | `grantable_item` supertable |
|---|---|---|
| **Adding a grantable type** | One row in `grant_scope_type` | New table + FK from supertable + migration |
| **Referential integrity** | None — can point at a deleted item | Full |
| **Query cost** | Direct | Requires a join |
| **Risk** | Orphaned grants after an item is deleted | Migration churn on every new feature |

You have deferred events, documents, and most other grantable things. Polymorphism means
adding each one is a config row rather than a schema change, which matters a great deal
given how much of this system is not yet specified.

The mitigations are mandatory, not optional:

1. `grant_scope_type` validates the `scope_type` value (FK above).
2. Deleting an item must close its grants — an application obligation, and tested.
3. A **nightly orphan check** per scope type (§10, check 2).
4. `scope_id` is `BIGINT` and ids are never reused.

**To overrule this**, add a `grantable_item(id, item_type)` supertable and give every
grantable entity an FK to it. Tracked in
[../open-questions.md](../open-questions.md) — it is a real fork and worth a deliberate
decision.

### Why `valid_to` is discouraged here too

Same reasoning as roles, more acutely: an item grant is typically for one event, so an
open-ended item grant is nearly always a mistake. Application validation should require
`valid_to` for item-scoped grants, with `access_grant.grant_reason` explaining any
exception.

---

## 7. `permission_level` — connecting permissions to grant levels

**Fields**

| Field | Kind | Notes |
|---|---|---|
| `id` | integer identity | Surrogate key. |
| `permission_id` | reference to `permission`, required | |
| `scope_type` | reference to `grant_scope_type`, required | |
| `required_level` | reference to `access_level`, required | What `access_grant.level` is needed for this permission on this scope kind. |
| `created_at` | timestamp, audit time | |

**Rules**

- One row per (permission, scope type) pair.

This table is what lets **one** `access_grant.level` serve many different permission codes
without a hardcoded mapping in application code. Example:

| permission | scope_type | required_level |
|-----------|-----------|----------------|
| `event.view` | event | `view` |
| `event.register_self` | event | `contribute` |
| `event.edit` | event | `manage` |
| `event.manage_participants` | event | `manage` |
| `event.presence.mark` | event | `contribute` |
| `event.grant_access` | event | `admin` |
| `org_unit.view` | org_unit | `view` |
| `org_unit.manage` | org_unit | `manage` |

Without it, every permission check would need to know its own level — a mapping in code,
invisible to the organization, and impossible to review. With it, "what does `manage` on an
event actually let someone do?" is a query.

The audit question "what does `contribute` on an event grant?" is that same read: the codes and
display names of the permissions whose scope type is `event` and whose required level is
`contribute`.

---

## 8. `audience` — grants that target a set of people

A grant can name a **person** or an **audience** (D-042). This is how "open this event to
everyone" or "let the whole group see it" is expressed — the case that surfaced when the
question of exposing a scope was answered with *"they set the permissions to that event for
'everyone' or a group of people."*

**Fields** (`audience`)

| Field | Kind | Notes |
|---|---|---|
| `id` | integer identity | Surrogate key. |
| `code` | text, optional, unique where set | Set for **built-in** audiences; absent for named groups. |
| `name` | text, required | |
| `description` | text, optional | |
| `kind` | enum: `builtin`, `group` | Required. `builtin` — evaluated as a **rule** by the resolver; no membership rows exist. `group` — a stored, administered list in `audience_member`. |
| `resolver_key` | text, optional | For built-ins, which rule the resolver applies. Set exactly when `kind` is `builtin`. The values: `everyone` — any person, including non-members and the public; `all_members` — anyone with a current membership; `unit_participants` — participants of the unit in `scope_parameter`; `unit_leaders` — holders of a live assignment to a leadership **position** in that unit; `guardians_of` — active guardians of the person in `scope_parameter`. |
| `scope_parameter` | integer, optional | For the parameterised built-ins: which unit, or which person. |
| `is_system` | boolean | Default false. |
| `valid_from` | date, optional | |
| `valid_to` | date, optional | Absent = open. |
| `created_at` | timestamp, audit time | |
| `created_by` | reference to person | |

**Rules** (`audience`)

- `kind` is `builtin` exactly when `resolver_key` is set; the two agree in both directions.
- A `group` has no `code`. Codes belong to built-ins.
- `code` is unique among the rows that have one.

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
- **No overlapping memberships.** A person may not hold two rows for the same audience whose
  periods overlap, counted over **all** rows and not only the open ones. Periods are half-open,
  so a membership ending on a day and another beginning that same day do not collide.
- Only named groups have members. A built-in audience is a rule, so a row here would be
  meaningless and, worse, would look authoritative — and nothing about the row itself gives it
  away. Integrity check 12 (§11) is what finds them.

### Built-in audiences are rules, not lists — and that is the whole point

The distinction is the load-bearing one:

| | Built-in audience | Named group |
|---|---|---|
| **How evaluated** | A rule the resolver applies at check time | A stored list of `audience_member` rows |
| **When a person joins the unit** | They immediately receive what the unit granted — **automatically** | Nothing happens. Someone must add them. |
| **Maintenance** | None | The classic stale-group problem: nobody ever removes anyone |
| **Examples** | `everyone`, `all_members`, the participants of unit X, the guardians of person Y | "the summer camp kitchen crew" |

**Prefer built-ins.** A pack that grants `view` on its events to
`unit_participants` of itself gets the correct behaviour forever: next year's new members
inherit it, and people who leave stop being covered, with no rows to maintain. The same grant
to a *named group* silently rots the moment the roster changes.

Named groups exist because some sets genuinely are ad hoc — a camp kitchen crew is not a unit
and is not derivable from anything. They are the escape hatch, and they carry their known
cost.

### Evaluation

An audience grant is evaluated as part of the person's own permissions — the resolver
expands it, so a grant to an audience is checked *as if* the person held it directly:

An audience grant applies when **one** grant row satisfies all of these. These are conditions
on a single row, tested together — their order carries no meaning:

1. The grant names an audience; a personal grant is not this question's business.
2. Its `scope_type` is the scope type being checked, and its `scope_id` matches the scope id
   being checked, with an absent id counting as equal to an absent checked id.
3. Its level is not `revoked` — denies belong to channel 0.
4. It has not been revoked.
5. It has started as of the checked date and has not ended on that date.
6. A `permission_level` row exists for the checked permission at the grant's scope type, and the
   grant's level ranks at least as high as the level that row requires.
7. `person_in_audience()` puts the person in that audience on the checked date.

`person_in_audience()` is where the built-in rules live:

The rule the resolver applies, in this order:

1. The audience itself must not have ended — no `valid_to`, or a `valid_to` after the checked
   date. An ended audience covers nobody, of whatever kind.
2. `everyone` — always true.
3. `all_members` — the person has a current membership.
4. `unit_participants` — the person has a unit participation row for the unit named in
   `scope_parameter`, covering the checked date.
5. `unit_leaders` — the person holds a **position assignment** at the unit named in
   `scope_parameter`, live on the checked date, **to a position marked `is_leadership`**.
   **Corrected in round 6, and the correction is the interesting part.** This rule used to ask
   for a *role* assignment "of a role marked `is_leadership`" — and no such flag is on `role`.
   `is_leadership` lives on `position`
   ([02-organization.md §7](02-organization.md#7-position-and-position_assignment)), where it does
   something else again:
   it exists "only so a workflow can offer to create both at once". **The fix cannot be to delete
   the condition**, because then `unit_leaders` would match anyone holding any assignment at the
   unit — a member of the `unit_participants` audience by another name, and an audience whose name
   lies about its membership is worse than a broad one. **Nor can the fix be to add the flag to
   `role`**, because a role is deliberately position-independent and organization-reusable: a
   person is a leader *of a unit*, which is exactly what a position assignment records and exactly
   what a role does not.
   **This does not contradict "position is not authority"**
   ([D-005](../decisions/decision-log.md#d-005--permissions-are-grants-never-derived-from-identity),
   restated in D-033):
   audience membership is not authority, it is a test of who one existing grant reaches. Being
   elected troop leader still confers nothing until someone grants something to `unit_leaders`.
   **Note what depends on this and was therefore quietly broken.** Audiences of this kind are
   created per unit that needs one (§12), and every grant aimed at one was **inert**: the rule
   matched no person, so the authority was configured, visible in the editor as granted, and
   reached nobody. It failed closed, which is the least noisy way for a permission rule to be
   wrong — nothing broke, which is exactly why nobody noticed.
6. `guardians_of` — the person is the guardian of the person named in `scope_parameter`, under a
   guardianship covering the checked date. A lapsed membership does not remove a guardian, but an
   **ended** guardianship does.
7. Anything else — a named group: the person has an `audience_member` row for this audience
   covering the checked date.

Branch 7 is the fallback: anything whose `resolver_key` is absent, or matches no rule above, is
read as a stored group membership.

**Note `unit_leaders` reads the position tables without itself being an authority grant.** Membership in an audience confers nothing on its own — it only decides whether *this
grant*, which someone already created deliberately, reaches this person. A leader does not
become able to do anything by being in the `unit_leaders` audience; they become able to do
exactly what that grant says, on that item.

### What audiences do **not** do

- **They are not a permission.** Being in an audience is not authority; it is membership of a
  set. All authority still comes from a grant.
- **They do not replace `guardianship_permission`.** `guardians_of` lets a unit open something
  to a child's guardians; it does not let a guardian edit the child's record. That remains the
  guardianship channel.
- **They do not nest.** An audience cannot contain another audience — that is how you get
  evaluation cycles and answers nobody can predict.
- **`everyone` is genuinely everyone**, including people with no account and no membership.
  It is the right target for a public event page and the wrong one for anything else.

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
| `authorization_channel` | enum: `ownership`, `guardianship`, `item_grant`, `role`, `system`, `none`, or absent | Which channel authorized this. Makes the audit answerable: "by what authority did this person do that?" `none` records that none did. |
| `authorization_ref_id` | integer, optional | No foreign key: it names a row in one of several tables — `role_assignment.id`, `access_grant.id`, or `guardianship_permission.id`. Lets an auditor go directly to the grant that permitted the action. |
| `permission_code` | text, optional | The permission checked, as its code. Absent for pure read events that are logged for access-trail purposes rather than permission decisions. |
| `scope_type` | text, optional | |
| `scope_id` | integer, optional | |
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
while it is readable, and the readers here are whoever holds `audit.view`, not whoever may see the record.
A sensitive value copied into a less-protected table is a protection failure on the day it is copied, not
only for as long as it then survives.

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
change a row is the erasure or the reduction, the only columns either may touch are the state columns, and
every other field on the row is immutable. The literal version of this rule is the more dangerous one,
because it fails silently and what it fails is the policy. The same reasoning applies to `audit_log` and
is stated with the operations themselves in
[06-audit-and-import.md §2.2](06-audit-and-import.md#22-redaction-before-logging).

**Retention: the same window as `audit_log`'s payloads, as a proposal rather than a decision.** This
paragraph used to read *"never delete them — the partition retention policy is a legal question, not a
technical one"*, and the second half of that is still exactly right. What has changed is that the decision
which bounded the change trail's payloads
([D-088](../decisions/decision-log.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short))
proposes the same window here — **24 months on the state columns, rows kept, 12 months as the floor** —
and records it as [F-8](../open-questions.md#f-8--retention-policy-for-access_log), **which still needs
confirming**. Until it is confirmed, that is a default awaiting a person and not this document's position.

**Why the question is weaker here, which is structural and not luck: this table does not hold the
contents of reads.** `before_state` and `after_state` are populated for write actions only, so a read
records *who asked, for what, under which permission, through which channel, and whether it was allowed*
— and stops. Recording what the read *saw* would copy every record a permitted glance touched into a
table read by a wider audience than the record itself, which is the exact act this section argues against
two paragraphs above. So the window here protects considerably less than it protects over in `audit_log`,
and what survives it is everything this table was built to answer. **The valuable fact about a read is
that it happened and by what authority, and that is precisely the part no reduction touches.**

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

Two small helpers keep `can()` readable. Both are `STABLE`.

**`grant_satisfies(person, scope_type, scope_id, permission, at)`** — does the person hold a
grant **on this exact scope** whose level meets what the permission requires at that scope kind?
Exact match only, no inheritance. It covers both a personal grant and one made to an audience
the person is in. Any one grant row meeting all of these satisfies it:

1. Its `scope_type` equals the checked scope type and its `scope_id` matches the checked scope
   id, with an absent id equal to an absent checked id.
2. A `permission_level` row joins the checked permission to the grant's scope type.
3. The grant's level ranks at least as high as the level that row requires.
4. Its level is not `revoked` — denies are handled in channel 0.
5. It has not been revoked.
6. It has started as of `at` and has not ended on `at`.
7. The grantee is this person, or an audience containing them at `at` (§8).

**`level_satisfies(level, permission, scope_type)`** — is this grant's level sufficient for the
permission at this scope kind? The rank of the given level is compared with the `required_level`
recorded for that pair. **When no `permission_level` row exists for the pair the answer is
false**: an unmapped permission is satisfied by no level rather than by every one.

**`scope_exposure_covers_assignment(org_unit_id, role_assignment_id, at)`** — does an exposure at
this unit cover this assignment? The exposure is the **only** way authority crosses a unit
boundary downward. True when some `scope_exposure` row names this unit and this assignment and is
at `at` still open, not withdrawn, and already started. Whether the assignment itself is still
live is the caller's check, not this one's.

**`person_holds_gate_exempt(person, at)`** — does this person hold `system.gate_exempt`, and is
the exemption itself still live (D-051)? True when some `role_assignment` of that person is live
at `at` and its role grants `system.gate_exempt`, and — if that assignment is a delegation — its
source assignment is itself live at `at`.

This last one is **deliberately not expressed as a call to `can()`**. `can()` applies the
membership gate, and the exemption exists to lift that gate; asking the resolver would make a
lapsed holder unable to hold the permission that says a lapse does not matter. It is read
directly from `role_assignment`. An `access_grant` can never confer this: system-namespace
permissions are unreachable by the item channel, which is the structural guarantee that an item
grant cannot lift the gate.

The single authorization entry point. One implementation, used everywhere. Algorithm:
[../domain/06-authorization-model.md](../domain/06-authorization-model.md#6-the-resolver).

**`can(person, permission_code, scope_type, scope_id, at, owner_person_id)`** returns allowed
or denied. `scope_type` and `scope_id` are optional, `at` defaults to today, and
`owner_person_id` is supplied only where the ownership channel is in play.

**The order of these steps is a rule.** Each step either returns or falls through, so a step
never gets to contradict an earlier one; reordering them silently changes who can do what.

1. **Look the permission up by code.** If no permission carries that code, **return false** —
   an unknown permission is a deny, and it is settled before anything else is considered.
2. **Resolve merge chains.** Replace the person with the survivor of any merge, so permissions
   are never evaluated for a tombstoned person.
3. **Channel 0 — explicit deny. Absolute and scope-independent.** A `revoked` grant applicable
   to this person blocks access no matter **what** scope it sits at: a per-event grant can never
   restore access that an organization-wide suspension removed. Locality orders *allows* (the
   tiers below); it never outranks a deny. See the authorization model §7.1. A grant counts when
   it is itself unrevoked, has started as of `at`, has not ended on `at`, and applies to the
   person — where "applies" means it names them **or** names an audience they are in at `at`
   (§8). A personal deny and an audience deny are equally absolute, and a personal allow further
   down cannot beat an audience deny, because channel 0 has already returned. Its scope applies
   when any of these holds:

   - it sits at organization scope, and then it applies everywhere;
   - it sits on the exact thing being checked — same scope type, same id;
   - it sits on a unit and the check is about that same unit. A deny on a unit covers **only**
     that unit: authority does not flow down, so there is no ancestor walk here either.

   Any such grant: **return false.**
4. **Channel 1 — ownership.** If an owner was supplied and that owner resolves to this same
   person, **return true**. Your own data.
5. **Channel 2 — guardianship. Consulted when the check is about someone other than the actor;
   answers with allows only.** The test is a comparison, not a name: an owner was supplied, it
   resolves to a real person, and that person is **not** the actor. The question is whether the
   actor holds a **live guardianship over that subject at `at`** whose `right_level` is at least
   what the checked permission needs — `view` for a read, `write` for a change; `none` satisfies
   nothing. **If such a guardianship exists and the level suffices, return true. In every other
   case — no guardianship, `none`, or a level too low — the channel returns nothing at all and the
   resolver continues to step 6.** It does not deny. Defined in
   [04-relationships.md §4](04-relationships.md#4-how-the-resolver-uses-these-tables); the
   reasoning for both halves is
   [D-079](../decisions/decision-log.md#d-079--the-guardianship-channel-is-entered-by-shape-not-by-permission-name).

   Three properties of this channel, each of which has a decision behind it:

   - **Entered by shape, not by namespace** (D-079, following D-074). A parent correcting their
     child's address is checked under `person.address.edit` — an ordinary, un-prefixed code — and
     still routes here. A permission added next year for a field a guardian must edit is covered
     the day the field exists.
   - **Silent rather than final.** Under the old prefix rule this channel gave the last word,
     because `dependent.*` codes belonged to no role. Now that it carries ordinary codes, taking
     the last word would deny the parent who is also the event registrar the right to run the
     roster: `view` over their own child, asked to write, refused by their own guardianship. So a
     shortfall falls through to the actor's own roles and grants. **A real prohibition is still
     possible and still absolute — it is an explicit deny, step 3, channel 0.**
   - **Gate-exempt.** A guardian whose own membership lapses has not stopped being the child's
     guardian; see D-039 and D-051. No membership test appears anywhere in this step.

   The **guard must not be weakened into "the subject is a minor."** The existence of a guardianship
   row is the whole test; an age lookup here would put a branch in the resolver that D-070 and
   D-077 rule out, and it would be redundant: without a row there is no channel to enter, which is already true today.

   **Personal attributes reach this resolver through no new door, and the sentence is worth writing
   down because the data looks like it wants one.** Everything the organization knows about a person
   beyond their name, gender and age is descriptive data in one table
   ([09-attributes.md](09-attributes.md)), and it is read by `person.view` and written by
   `person.edit` — the two codes that already cover the person — through the channels already listed
   above. No `attribute.*` read permission exists, because there is nothing to gate that
   `person.view` does not already gate; there is no fifth channel; and there is no branch anywhere on
   *what a value is about*, because a branch on content is the privileged medical subset returning
   through the resolver after [D-083](../decisions/decision-log.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)
   refused it through the permission list
   ([09-attributes.md §4](09-attributes.md#4-who-may-read-and-who-may-write)). **The temptation this
   invites is precisely the age branch the paragraph above refuses** — *"a leader may see allergy data,
   but only for the children in their unit"* reads as prudent and is a rule about an age and about the
   contents of a value, two things this resolver deliberately cannot see. The grant already says
   everything it is entitled to say: whoever holds `person.view` over this person reads this person.
   **What changed is the reach of one existing answer, not the route to any answer** — see §12 for the
   code, which is `person.view`, and for why its mark in the catalog has to rise with its reach. The only genuinely new capability in the area is curation of the vocabulary
   itself, `attribute.define`, and it arrives as an ordinary narrow permission through a role like
   every other: nothing structural hangs off it.
6. **Channels 3-5 — allows, ordered by locality, most specific first.** The first tier that
   yields a determination decides the effective level for this check; if that level is
   insufficient, fall through to the next tier. This is what "local permissions override global"
   means, and it applies to **allows only** — denies were already settled in step 3. The units
   whose grants apply to a check are the checked unit itself, and any unit that has explicitly
   exposed its scope to a relevant assignment. **No `unit_ancestors()` call appears anywhere in
   this function.**

   1. **Tier A — an item grant on this exact scope**, the most specific thing there is. Reached
      only when both a scope type and a scope id were supplied. Satisfied by
      `grant_satisfies(person, scope_type, scope_id, permission, at)`.
   2. **Tier B — a unit grant: `grant_satisfies(person, 'org_unit', scope_id, permission, at)`.**
      Reached only when the checked scope is a unit and an id was supplied. **Exact match, and
      one route only — an exposure does not extend a direct grant,** for the reason set out in
      §5; the role channel below is the only consumer of that table.
   3. **Tier C — an organization-scoped grant:** `grant_satisfies(person, 'organization', NULL,
      permission, at)`.
   4. **Tier D — roles: exact scope match, or a unit exposed to the assignment.** No downward
      inheritance.

      **The membership gate (D-039):** a role grants anything only while the holder has a
      current membership, unless (a) the **role** is marked `requires_membership = false`, or
      (b) the **person** holds `system.gate_exempt` (D-051). Guardianship and ownership were
      already answered in steps 4 and 5 and are deliberately exempt. (b) is resolved by
      **direct lookup**, not through `can()`. Routing it through the resolver would be circular:
      a lapsed holder of the exemption would be denied it by the very rule it exists to lift,
      and the lockout would have no error message.

      All of the following must hold of one assignment (these are conditions on a single row,
      listed in the resolver's own order):

      - it names this person and is live at `at`;
      - **there is no check on the role's own period.** A role is valid always and the temporal
        question is the assignment's (D-053); the place such a check would have sat does not
        exist;
      - the gate holds: the role's `requires_membership` is false, **or** the person has a
        current membership, **or** `person_holds_gate_exempt(person, at)`;
      - the role grants a permission whose code equals the checked code, **or** the checked
        permission has no namespace and the role grants `system.admin`. There is **no `.admin`
        prefix-match branch**: there are no per-resource admin permissions (D-068, reversing
        D-007), and a role that can do everything about events lists all thirteen `event.*`
        codes explicitly;
      - the scope fits, in one of three ways — the assignment is organization-scoped and the
        check is at organization scope or unscoped, except that `system.admin` qualifies whatever
        the checked scope is, since an organization-wide grant of it has to reach everywhere; or
        the assignment is unit-scoped, the check is about a unit, and either that unit is the
        assignment's own unit or it carries an open, unwithdrawn, started exposure naming
        **this** assignment; or the check is unscoped ("can they do this anywhere?"), in which
        case any live assignment qualifies — **for UI decisions only; never enforce a mutation
        on an unscoped check**;
      - and, if the assignment is a delegation, its source assignment is still live at `at`.

      Any such assignment: **return true.**
7. **Channel 5 — default deny. Return false.**

> **The membership gate is one clause, and it is the clause most likely to be "optimized"
> away.** `AND (NOT r0.requires_membership OR is_current_member(p_person_id) OR
> person_holds_gate_exempt(p_person_id, p_at))` is the whole of D-039 as amended by D-051.
> Removing any disjunct because "the join is expensive" reverses a decision taken
> deliberately, and nothing else in the schema would notice. If it becomes a measured
> performance problem, the fix is to cache `is_current_member()` — a single indexed lookup on
> `(person_id, status, valid_to)` — or to inline `person_holds_gate_exempt` as a join, not to
> drop a condition.
>
> **The third disjunct is the one that must never be routed through `can()`.** It is a plain
> read of `role_assignment`; going back through the resolver would mean asking the gate
> whether the gate applies, and a lapsed holder of `system.gate_exempt` would be denied the
> permission whose entire job is to say that a lapse does not matter. That is a lockout with
> no error message, on the one day of the year it would hurt most.

### Cache invalidation, revisited

The membership gate makes this harder than it was, and it must be built in from the start
(D-039):

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

**Indexes**

- on `expires_at`, for the expiry sweep;
- on `person_id`, because the membership gate means a bulk expiry sweep must invalidate by
  **person**, fast.

Invalidated on any write to `role_assignment`, `access_grant`, `guardianship_permission`,
`role_permission`, `audience`, `audience_member`, a person merge — **and on every membership
transition, including the yearly expiry sweep, which touches every member at once.**

### Properties to verify when reviewing this function

1. **Deny is checked before everything**, including ownership. A suspended account's owner
   permissions are denied by a `revoked` grant if that is what the organization wants.
2. **Ownership short-circuits before roles.** A person's access to their own record does not
   depend on any grant, which is what makes the system usable by non-members.
3. **There is no wildcard except `system.admin`.** No prefix match, no implied capability.
   If a holder can do a thing, a row says so (D-068).
4. **`p_at` is threaded through every branch.** Permission checks are time-travel capable.
5. **Delegation sources are re-validated at check time**, closing the
   stale-delegation escalation.
6. **`resolve_person` is called on entry**, so a tombstoned person's id still resolves.
7. **A deny is scope-independent.** Channel 0 matches organization-level denies and
   same-scope denies, and does **not** walk ancestors — so a `revoked` grant at
   organization scope blocks every unit, which is what makes a suspension absolute.
8. **`unit_ancestors()` does not appear in this function.** Authority does not flow down.
   A unit's grants reach it only via exact match or an explicit `scope_exposure`. This is
   asserted by a test, not just a comment — integrity check 13.
9. **Locality orders allows only.** Tiers A→D are consulted in order and the first
   sufficient level wins; none of them can override channel 0.
10. **The membership gate applies to roles only, in tier D.** Ownership (channel 1) and
    guardianship (channel 2) return before it, which is what keeps a lapsed parent able to
    act for their child and a lapsed person able to see their own renewal screen. Item and
    unit grants are *not* gated — a grant someone deliberately made to an unpaid person is
    honoured, because it was an explicit act rather than an inherited role.
11. **Audience grants are evaluated through the same tiers as personal ones**, via
    `grant_satisfies()`. A grant to `everyone` and a grant to a named person differ only in
    how `grantee` is satisfied, never in how the level or the scope is resolved.

**A caveat on `p_scope_type IS NULL` in tier D.** An unscoped check ("can this person do
X anywhere?") returns true if *any* assignment grants it. That is correct for UI decisions
like "show the admin menu?" but **wrong for enforcement**. Every enforcing call must pass a
scope. Enforce this in the calling convention — make scope mandatory at the API layer for
mutating operations.

The cache definition and its invalidation rules are above, immediately after the resolver —
they are part of the resolver's contract, not a separate concern.

The person-merge case remains the easiest to forget —
see [01-identity.md](01-identity.md#8-identity_hypothesis-and-person_merge).

---

## 11. Invariants to verify

These were queries. They are now invariants to be verified by something, in whichever way the
implementation chooses, and what follows states what each one counts and what a non-zero result
would mean. Two of them were CI assertions that read the text of the stored resolver to prove a
rule was still inside it (14 and 15), and a third was the same shape again (19). Nothing can
read that text any more. **The time-bomb in check 19 — that `.admin` prefix-matching must never
reappear in the resolver — is now a written prohibition and nothing more.** A prohibition nobody
runs is a convention, not a guard; it stays because silently forgetting it existed would be
worse, and it should not be described as equivalent to what it was.

**Invariants to verify**

- **1. Live grants for a person who has been merged away.** An open `access_grant` whose person
  has been merged into somebody else. A row means authority is still attached to a tombstone;
  it should have been closed or moved at merge time.
- **2. Orphaned item grants.** Per scope type, generated from `grant_scope_type`: a grant whose
  `scope_id` names no row in the item table it points at. A row is exactly the risk the
  polymorphic `scope_id` accepts (§6), and this is mitigation 3 of that trade.
- **3. Leavers with access.** Open role assignments, for roles requiring membership, held by
  people with no current membership. The highest-value report here; the resolver already withholds
  the authority, so a row is an assignment that should have been closed and was not.
- **4. Assignments that violate `requires_scope`.** A role assignment whose scope type differs
  from the `requires_scope` of a permission its role grants. A row means a unit-level permission
  is being held organization-wide, or the reverse.
- **5. Delegations whose source has ended.** A delegation that is open-ended — which the row
  rule forbids — or whose source assignment has already ended. A row is the stale-delegation
  privilege-escalation, live.
- **6. A deny that stands alone.** An open `revoked` grant on a scope where the same person has
  no other open grant at any other level. Probably intended as a removal rather than as a deny;
  verify the intent.
- **7. Holders of `system.admin`.** Everyone with an open assignment of the `system_admin` role.
  This should be a very short list, and it should alert on change.
- **7b. Holders of `system.gate_exempt`.** Everyone who keeps authority without a current
  membership (D-051), through any role granting it, over assignments live today. Like check 7
  this should be a very short list and should alert on change, but it is a **different** list:
  check 7 catches who can rewrite the system, this catches who keeps access while lapsed.
- **7c. The gate's own soundness.** Nobody should be in the position where the direct lookup
  says they hold the exemption, the resolver says they do not, and they have no current
  membership. A row means `person_holds_gate_exempt()` is being routed through `can()`
  somewhere, and the exemption has become unreachable for the person who needs it (D-051).
- **8. Permissions no level can express.** A permission with no `permission_level` row at any
  scope type — or none at a scope type where grants of it actually exist. Such a permission is
  unreachable: every grant against it fails condition 6 of the audience evaluation and step 2 of
  the role channel, so it reads as denied forever, and the person who was promised it will be
  told they lack a permission that no configuration could ever grant. **The scan used to be
  narrower, and D-074 accidentally corrected that:** it scanned only the `dependent.*` namespace,
  on the theory that a guardian capability nobody could grant was the case worth catching. There
  is no such namespace now, so nothing scopes the scan — the right outcome, because the bug was
  never specific to guardians. Also confirm the mapping the guardianship channel depends on is
  coherent: `view` must land at or above `view` and `write` at `contribute` or higher, or a
  guardian's `write` cannot actually change the child's record.
- **9. Scope-authority violation.** An exposure naming an assignment scoped to a unit that is
  neither the exposing unit nor an ancestor of it — the shape that means authority is being
  claimed from a sibling or a descendant, which is never a legitimate exposure. **Note the
  direction:** it is correct, not a violation, for an exposure to name a district-scoped
  assignment, because the row is keyed on the troop and the troop is doing the exposing
  (domain/06-authorization-model.md §2.3). What is forbidden is a row that reaches across, not
  one that reaches up. This is the one legitimate use of `unit_ancestors()` in this document:
  checking for violations, never resolving permissions.
- **10. Exposures made without the permission.** An exposure whose exposing person does not, as
  of the exposure's own start, satisfy `scope.expose` at the covered unit. There is no longer
  any exception to this — the bulk tool is removed (D-045), so **every** row must satisfy the
  predicate §5 requires of every write. **A row here means the write-time check was skipped, not
  that a constraint was disabled** — there is no constraint to disable. This is the report that
  stands in for a database rule, which makes it the one exposure check worth alerting on.
- **11. Exposures pointing at a dead assignment.** An open, unwithdrawn exposure naming an
  assignment that has already ended. Harmless — the resolver re-validates — but worth cleaning
  up.
- **12. Member rows on a built-in audience.** Any `audience_member` row whose audience is
  `builtin`. Built-ins are rules, not lists (§8); a stored member row is meaningless and would
  look authoritative.
- **13. Named groups with no members.** A live `group` audience with no open member row.
  Probably abandoned; worth confirming.
- **14. TIME-BOMB for the resolver: no permission path may inherit.** The requirement is that
  **no part of the permission path — resolver, grant lookup, guardianship lookup, or any view an
  authorization check reads — may walk the unit hierarchy.** A unit's ancestors are not in scope
  for a check, full stop; `unit_ancestors()` exists for the *structural* questions (nesting
  rules, paths, reports) and must never be reachable from an authorization decision. Anything
  that reaches it means authority is flowing downward through a permission path, which the design
  forbids. **What was lost here is the mechanism, not the rule:** this used to be a build-time
  assertion that grepped the stored definitions of the three resolver functions, so an inheriting
  view added by a later migration failed the build rather than passing review. D-072 removed the
  SQL and with it the only form of this check that could fail automatically. It is now a code
  review instruction, and the ORM makes it *harder*, not easier, to write the bad thing
  conspicuously — an implicit join through a parent relation looks like ordinary fetching.
  Whoever builds this should restore an automatic version, in whatever the ORM's test layer is.
- **15. TIME-BOMB for the membership gate (D-039).** Same shape, same loss: the role channel had
  to contain **both** the gate (`is_current_member`) **and** the role-level opt-out
  (`requires_membership`), so that neither could be dropped quietly — deleting the gate revives
  the problem D-039 closed, and deleting the opt-out makes a role that is supposed to survive a
  lapse unable to. The requirement stands as written in step 6 of §10; only the grep that enforced
  it is gone.
- **16. Role deletions.** A `role_assignment` pointing at a role that is no longer there. The
  delete guard on `role` enforces this; the check exists because a restored dump or a manually
  disabled guard bypasses it, and the loss is unrecoverable — the assignments go with the role.
  Zero expected.
- **17. Unused roles.** A non-system role with no assignment that is open or still in the
  future. A role nobody holds is **not** an error: it is either one about to be used or one
  stopped using and not deleted, and there is no third possibility, because a role has no period
  (D-053) and cannot be switched off, only held or not held. Expected: unused, non-system roles.
  Delete the mistakes, keep the ones on the roadmap.
- **18. Orphaned permissions.** An assignable permission that no role grants. This check exists
  **because of** D-068: with no `.admin` wildcard, a permission that ought to be inside some role
  and was never added to it is silently unusable, and no resolver rule covers it by accident any
  more. This is the net the wildcard used to be. Expected: empty after a seeding pass. A row
  means either a permission nobody has bundled yet — fine on a roadmap, wrong in production — or
  a module was added and its roles were not. **Note what it cannot see:** a permission granted
  to *a* role but not to the role that arguably should have it. That residual is the accepted
  cost of D-068 and nothing closes it; it is a human reading the starter list in §12 against the
  catalog.
- **19. TIME-BOMB for D-068: the `.admin` prefix match must stay deleted.** Two parts, both
  written as CI assertions when this document still carried SQL; both are prose now, which
  D-072 records as a real weakening. First, **no step of the resolver may build a permission code
  by concatenating a resource with `.admin`.** This is a rule about the code, not about a
  particular query, and it survives the move to an ORM untouched — it is the one invariant here
  that is about program text rather than about data, and it is the one an ORM migration will never
  violate on its own. A reintroduced wildcard re-creates implied capabilities for every resource,
  including resources added after the day it was added back. Second, no permission may have
  `admin` as its *action* except **exactly one**: `system.admin`. D-068 exempted four others on
  purpose, and **[D-074](../decisions/decision-log.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular)
  withdrew all four exemptions** along with the namespace they lived in, so the allow-list is a
  single code and the check is now an equality, not a set membership. `system.admin` is explained
  in the catalog's §1 as one of the **two** things still named "admin"; anything else carrying
  `admin` as an action is a re-created wildcard. **Zero rows expected.** The whole point of this
  entry is that the first version of the second half accepted five exceptions and the second
  version accepts one: an allow-list is where a wildcard comes back to life.

Checks 3, 7, 7b, 14 and 15 are the ones to wire to alerts.

- **Check 7b is the new one worth wiring to an alert.** Check 7 answers "who can rewrite the
  system?"; 7b answers "who keeps authority while lapsed?" — a shorter list with a different
  failure mode, and the one the membership gate introduces. Neither should ever grow quietly.
- **Check 7 should email someone every time its result changes** — a new `system_admin` is
  either a planned change or an incident, and either way someone should know within the hour.
- **Checks 14 and 15 are CI assertions, not reports.** They are the automated guards on the
  two rules most likely to be "simplified" away when someone optimizes the resolver: the
  no-inheritance rule and the membership gate. Both fail the build rather than silently
  changing who can do what.
- **Check 9 catches the direction being broken in the way the resolver cannot see.** A row
  that reaches sideways to a sibling unit, or down to a descendant, would be honoured
  happily by `can()` — nothing else in this list would notice it, and it is precisely the
  shape that lets authority be claimed from outside.
- **Checks 12 and 13 guard the audience model.** Built-ins must not accumulate member rows
  (they are rules), and an empty named group is usually an abandoned one.

---

## 12. What the organization starts with

Starting catalog. Expect to edit this heavily; it is a proposal, not a specification.

> **This section and [../appendix/permission-catalog.md](../appendix/permission-catalog.md) are
> the same list written twice, and they drift.** When this was reconciled, **22 documented
> permissions had no `INSERT` row** — among them `unit_participation.view`, which **five** of
> the catalog's own seed roles assign, and `person.redact`, which is one of the two codes
> D-068 exists to protect. A further 12 were the `event.*` set, added to the catalog when
> events were designed and never carried here. **Under the old wildcard much of this was
> harmless**: a role holding `unit_participation.admin` reached the code whether or not the row
> existed, so the catalog could advertise a capability the database could not name and nothing
> noticed. The permission editor was the only place the gap showed. **[D-068](../decisions/decision-log.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle)
> removed that cushion.** Now a role that lists a code with no row either fails to insert or
> grants nothing, and integrity check 18 reads the *table*, so it cannot see that the catalog
> promised something the seed never contained.
>
> **There is no SQL check for this** — one side is a Markdown file. The discipline is the
> check: when adding a permission, add it in **both** places in the same edit, and treat a
> catalog row with no `INSERT` row as a bug of the same class as a missing migration. The
> reconciliation is mechanical enough to script if this file ever grows again:
>
> a diff of the codes the catalog lists against the codes that exist. Anything in the catalog
> and not in the database is a permission that cannot be granted; anything in the database and
> not in the catalog is an undocumented capability. Both were present at the same time.

**Roles are data, and the organization administers them at runtime.** This section seeds the
*permissions* — the vocabulary of things anyone might do. The role names used throughout the
docs are worked examples of composing those permissions into groups, not a fixed list.
Creating a role, changing what it grants, assigning it and deleting an unused one
are all supported operations (`role.create`, `role.edit`, `role.assign`, `role.unassign`,
`role.delete`).

The consequence for this document: **it does not need to know which roles exist, and where it
names a role it is illustrating, not specifying.** In particular, *which* roles carry
`system.gate_exempt` is a configuration decision that belongs to the organization, not to the
specification.

> **What §12 must fix, and does, is the *shape*.** `system.gate_exempt` is a `system`-
> namespace permission: it can only arrive through a role, never through an item grant. That
> is not a configuration choice — it is the structural guarantee that an `access_grant` can
> never lift the membership gate. Whether the organization puts it in one role or five is its
> own business.

**What the organization starts with.** The platform ships a vocabulary — the permissions, each
marked as a system row so it cannot be deleted or renamed — and that is the whole of what these
documents fix. Roles, assignments and grants are runtime data (D-052): the organization
composes them, edits what they grant, and deletes the ones nobody held. The starter roles the
catalog sketches are proposals to edit, and the permissions themselves are starter material too.

Those permissions span the namespaces this document and its neighbours describe: people —
viewing, creating, editing, merging, contacts, and the two irreversible codes; the vocabulary of
personal attributes, where **recording a value needs no new code and naming a thing needs
`attribute.define`**; accounts,
including suspension, closure and credential reset; membership, including requests, activation,
lapse, suspension, termination and backdating; participation in sub-units; units, their
renaming, restructuring and closing; scope exposure and its review; audiences; positions;
guardianship and the granting of guardian permissions; the administration of roles and
permissions themselves; item grants; audit; legacy import; reporting; the thirteen `event.*`
codes; and the messaging codes. **What is not on that list is the set that used to follow it: the
eighteen `dependent.*` codes are deleted, because a guardian's authority is now a level on the
guardianship row rather than a bundle of permissions
([D-074](../decisions/decision-log.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular)),
and the guardian-facing acts that survive are ordinary `guardianship.*` codes in the catalog.
**The one
remaining list is [../appendix/permission-catalog.md](../appendix/permission-catalog.md).** It
is the catalog; this document deliberately no longer keeps a second copy of it, because the two
copies disagreed for exactly the reason the note above describes.

A few of those codes carry a decision in their shape, and those are worth naming:

- **`person.merge` and `person.redact` are separate codes**, not flavours of `person.edit`. They are
  irreversible, and with no `person.admin` to imply them (D-068) a role that reaches them does so by
  listing them, visibly. `identity_reviewer` holds `person.merge`; no starter role holds
  `person.redact`. **This bullet named a third code, `person.unmerge`, and
  [D-087](../decisions/decision-log.md#d-087--merge-chains-stay-because-reversing-a-merge-is-a-supported-operation)
  removed the premise for it.** Reversing a merge is the same act as performing one — an identity
  correction made by a named human, through the same queue, with the same consequence for the same rows —
  so it is `person.merge`, which that reviewer already holds. **A separate code would grade undoing a
  mistake as safer than making one**, which inverts the only reason these acts were pulled out of
  `person.edit` at all. [The catalog](../appendix/permission-catalog.md) carried the row and has dropped
  it, recording the removal where the row stood so a reader of an older draft can find out where it went;
  no seed role held it, so no role lost anything by the change.
- **`person.view` reaches the whole record, and that is a change of reach rather than a new
  capability.** Since [D-083](../decisions/decision-log.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)
  there is no privileged corner of the record for it to stop outside: whoever holds it over a person
  reads their descriptive values — the allergy list, the insurance number, the note about who the child
  actually lives with — on the same grant that reads their name
  ([09-attributes.md §4](09-attributes.md#4-who-may-read-and-who-may-write)). It is therefore the widest
  read permission in the system, and **the catalog's sensitivity mark is where that has to be visible**:
  a mark set when "read a person" meant name and birth date now understates the code, and the honest
  mark is the catalog's top tier — which is worded around *whose* data a grant exposes rather than
  around a category of fields, because a category is what D-083 deleted. Read a bundling role with
  that in front of you — `person.view` inside a role now means *this role reads medical facts*, because
  that is what reading a person means. **Any future narrowing is a decision entry about a second grant
  scope over a defined set of data, and not a code with a suggestive name**; the case for it
  ("everything except the diagnoses") was put and declined
  ([domain/08-person-data.md §4](../domain/08-person-data.md#4-what-was-refused-and-what-it-cost)).
- **`audit.view` is graded against what the trail quotes, not against what a log is usually for.**
  `audit_log` carries before and after images, and since
  [D-085](../decisions/decision-log.md#d-085--the-identity-machinery-stays-structured-the-boundary-is-rules-not-sensitivity)
  those images are the only place a child's past descriptive values exist; an entry is therefore as
  sensitive as the person data it quotes, and reading history has to sit in the same tier as reading a
  person. **The alternative — keeping the values out of the payload — was taken once during this round
  and withdrawn** ([D-083](../decisions/decision-log.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)),
  because it graded descriptive fields above a change of address and left the history empty; what is
  left is this bullet, which is a mark on a line of a table and nothing else, and is the reason
  [09-attributes.md §6](09-attributes.md#6-erasure-retirement-and-the-audit-payload) calls the guard the
  weakest link rather than the last line of defence.
  **What the payload window adds to this bullet is a horizon, not a repair.**
  [D-088](../decisions/decision-log.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)
  empties those images 24 months after they are written, so a wrongly-graded grant of this permission
  reads a child's descriptive values **for two years instead of for as long as the system survives** —
  which bounds the exposure [D-086](../decisions/decision-log.md#d-086--a-sensitivity-mark-grades-what-a-grant-exposes-not-the-table-it-reads)
  graded and does nothing whatsoever to fix it. **The bound is the realistic control for an organization
  of this size, and it is the strongest argument
  [AT-4](../open-questions.md#at-4--is-one-permission-enough-to-guard-a-trail-that-holds-person-data)
  will receive; it is not an argument that the mark is set correctly, and it is certainly not an argument
  for keeping one permission forever.** The mark still has to be right for two reasons the window does
  not touch. Two years is not a short interval when the question is about a child, and it is roughly the
  interval in which a safeguarding question actually gets asked. And a reduced row is not a harmless row:
  it still names the person, the table, the record, the field that changed and the person who changed it,
  which is a statement about a child even with the value gone — so the tier this code sits in survives the
  window intact, and the window only shortens how long a mistake in it is worth exploiting.
- **`attribute.define` is the narrow half of a deliberate pair**: values are open to anyone who may
  already edit the person, so that the fact gets recorded, and codes are held by few people, because the
  codes are what make the data queryable
  ([09-attributes.md §2](09-attributes.md#2-attribute_definition--the-vocabulary)). It is an ordinary
  permission — no namespace, no resolver branch, no structural consequence — and it is the only code
  this area adds.
- **`scope.expose` is scoped to the unit being covered.** A parent unit's officer cannot satisfy
  it for a child unit, which is what makes the no-inheritance rule enforceable, and there is no
  bulk variant (D-045): every exposure row is written by the unit it covers.
- **`role.unassign` is the only thing that ends authority**, because a role has no period
  (D-053) and nothing forces an assignment to end (D-071).
- **`system.gate_exempt` sits in the `system` namespace on purpose** (D-051), so it can only
  arrive through a role assignment and never through an item grant. It is scope-independent by
  design: the gate is a property of the person, so the waiver has to be. Holding it means every
  gated role you hold keeps granting whether or not your own fee is current.
- **`membership.terminate` expels**, and is restricted as such; `membership.lapse` is an
  administrative end for non-payment.
- **`org_unit.restructure` is split, merge and successor units** — it is not reparenting
  (D-036).
- **`unit_participation.view` held at organization scope reads the root's own participation
  rows**, not a pack roster, because scope is matched exactly. That looks like a bug and is not
  (D-049).
- **`event.presence.mark` sits one level below `event.manage_participants` on purpose**, and
  **`event.register_self` *is* the eligibility rule** (D-060) rather than an expression of one.
  No wildcard sits among the thirteen, so a role that runs events holds all thirteen explicitly;
  the rationale is in catalog §8a.
- **There is no wildcard left at all, and that is worth noticing.** `dependent.admin` was the
  last deliberate one — one stored fact granting everything for one child — and D-074 replaced it
  with `right_level = write`, which does the same job **without being a permission**: it is a
  property of the relationship, so it cannot be listed in a role, granted to a unit, or
  discovered by prefix matching. The catalog's §1 now lists two things named "admin" where it once
  listed three. The residue is the opposite problem: with no wildcard, nothing implies anything,
  so a role that should have a new permission must be told (invariant 18 is the net).
- **`audit` has no `audit.admin`** — per-resource admin codes were removed (D-068).

**Reporting is seeded coarse, and left open on purpose.** Only `report.view` and `report.export`
are starters. Whether reporting is per-report (`report.finance.view`,
`report.membership.view`, `report.safeguarding.view`) or one `report.view` with row-level
filtering is still open (catalog §12), and the starter roles in catalog §11 name the granular
ones only to illustrate that unresolved choice. Do not ship both shapes; pick one when reporting
is designed.

**Levels and scope types are vocabulary, not configuration.** The five levels — `revoked` at
rank 0, then `view`, `contribute`, `manage`, `admin` — arrive with the schema, because a rank
ordering that can be edited at runtime is a security control with no owner; their meanings are in
§6 and in [00-conventions.md](00-conventions.md#5-enumerations). The grantable scope types start
as `organization`, which is not item-scoped, then `org_unit`, `membership`, `event` (designed in
[08-events.md](08-events.md)) and `document` (a document layer still to be designed).

**Built-in audiences come in two shapes.** `everyone` and `all_members` exist once for the whole
system, marked as system rows. The parameterised ones are created where they are needed rather
than seeded everywhere: `unit_participants` and `unit_leaders` one row per unit that needs one,
with `scope_parameter` naming that unit — the case that replaced the bulk exposure tool, and
named by convention along the lines of `unit:42:participants` and `unit:42:leaders` — and
`guardians_of` one per dependent whose guardians need a shared target. None of them ever has
member rows (integrity check 12, §11).

> **`system.admin` is deliberately a single top-level permission**, not a
> per-resource one. Holding it satisfies everything, and check 7 in §11 alerts on its
> holders. Keeping the most dangerous capability concentrated and alarmed is safer than
> spreading equivalents of it across every resource.

---

## 13. Open issues

- The complete permission catalog and real role definitions (§12) — needs your input.
  Specifically: which roles are marked `requires_membership = false`. That flag is now the
  line between "a lapse silently removes this" and "it does not", and it needs a deliberate
  answer per role rather than a default.
- Whether `valid_to` should be mandatory for high-authority assignments (§4).
- Polymorphic `scope_id` vs a `grantable_item` supertable (§6) — a real fork.
- Which built-in audiences are needed beyond `everyone` and `all_members`, and whether the
  parameterised ones are seeded per instance or created on demand (§8).
- How long a `permission_cache` entry may live given the membership gate (§10) — the
  shorter the TTL, the smaller the window in which a lapse has not yet taken effect.
- Cache vs materialized effective-permission table (§10).
- Retention policy for `access_log` — legal input required.
- Whether `access_log` needs human annotation (recommend a separate table if so).

**Resolved and no longer open**, kept visible so the reasoning survives: the bulk exposure
tool (removed — D-045); whether permissions depend on membership status (yes, with three
carve-outs — D-039); background-check permissions (removed — D-043); and the
organization-wide-roles tension (§4), which is much reduced now that membership and the
registry live at the single root unit (D-035).

All tracked in [../open-questions.md](../open-questions.md).
