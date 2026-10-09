# Authorization Model

The permission system end to end. This is the document to read if you read only one.

---

## 1. The four channels of authority

Every question of the form "may person P do X?" is answered by exactly one of four
mechanisms. They are separate tables because they have different lifetimes, different
granters, and different revocation semantics.

| # | Channel | Question it answers | Table | Grants authority over |
|---|---------|--------------------|-------|----------------------|
| 1 | **Role assignment** | What may this person do *in the organization*? | `role_assignment` | Everything within its scope |
| 2 | **Guardianship permission** | What may this person do *regarding this child*? | `guardianship_permission` | One dependent |
| 3 | **Access grant** | What may this person do *to this specific item*? | `access_grant` | One record (event, document, unit) |
| 4 | **Resource ownership** | Is this *their own* data? | (derived) | The row's owner |

Channel 4 is not a table. It is the rule that a person may always act on their own
profile, their own requests, their own memberships. It is resolved by comparing
`person_id` before any other channel is consulted.

**Why keep channels 1–3 apart rather than one unified grants table.** They differ in ways
that matter:

- Channel 2 has a **legal** character — guardianship is a fact about the world, often
  court-ordered, that expires when a child reaches majority. Channel 1 does not.
- Channel 3 is **per-record** and therefore high-volume and short-lived. Channel 1 is
  low-volume and long-lived. Mixing them makes both hard to reason about.
- A single table would need a discriminator column and every query would need a `WHERE`
  on it, and someone would eventually join across meanings by accident.

That said, `role_assignment` and `access_grant` **share a resolver and a scope model**, so
the check logic is written once. See §5.

---

## 2. Permissions — the atomic unit

A permission is a coded capability. It is the only thing the check function ever looks at.

```
permission(
    id,
    code,                     -- 'membership.request.approve'
    resource,                 -- 'membership_request'
    action,                   -- 'approve'
    description,
    is_system                 -- true = cannot be deleted; seeded by the platform
)
```

Codes are `resource.action` and are **stable identifiers**, never display strings. The UI
shows a human label; the code never changes. Renaming a permission code is a breaking
change and must be avoided.

### Naming convention

| Pattern | Meaning | Example |
|---------|---------|---------|
| `<resource>.view` | Read | `person.view` |
| `<resource>.create` | Create | `event.create` |
| `<resource>.<field>.edit` | Edit a field subset | `person.contact.edit` |
| `<resource>.delete` | Delete (soft, and audited) | `document.delete` |
| `<resource>.admin` | **Everything** on that resource | `event.admin` |
| `dependent.<x>` | Acting on a supervised person | `dependent.fee.pay` |

Per your instruction: **every resource exposes an `admin` permission** that subsumes all
narrower ones for that resource. The resolver treats `X.admin` as satisfying any check for
`X.<anything>`. This is checked structurally (`code` prefix match), so adding a new narrow
permission to a resource does not require updating every role that grants `X.admin`.

---

## 3. Roles — bundles of permissions

A role is a named set of permissions, assigned to a person for a period, within a scope.

```
role(id, code, name, description, is_system, scope_required)
role_permission(role_id, permission_id)

role_assignment(
    id,
    person_id, role_id,
    scope_type,               -- 'organization' | 'org_unit'
    scope_id,                 -- null for organization
    valid_from, valid_to,
    granted_by, granted_at,
    grant_reason,
    delegation_of             -- nullable; set if this came from a delegation
)
```

### Scope

`scope_type`/`scope_id` is what makes "treasurer of Troop 12" and "treasurer of the
organization" the same row shape. It also means adding a new scope kind later (a region,
an event series, a committee) is a data change, not a schema change.

*Assumption:* authority inherits **downward** through the unit hierarchy — a role at
`district` covers all its `group`s and `troop`s. See
[04-organization-structure.md](04-organization-structure.md#6-units-and-permissions).
This is a policy choice; the resolver can be switched to non-inheriting if you prefer.

### Seed roles (starting set — expects your refinement)

| Role | Scope | Key permissions |
|------|-------|-----------------|
| `system_admin` | organization | all, plus `system.*` |
| `registrar` | organization | `membership.request.*`, `person.*`, `unit_membership.*` |
| `treasurer` | organization or unit | `fee.*`, `payment.*`, `report.finance.view` |
| `unit_leader` | org_unit | `event.*` for own unit, `unit_member.view`, `unit_report.view` |
| `assistant_leader` | org_unit | subset of `unit_leader` |
| `group_admin` | org_unit | administrative management of a group and its children |
| `background_check_officer` | organization | `person.background_check.*` |

### The role assignment period matters

`valid_from`/`valid_to` on `role_assignment` means authority ends on a date even if nobody
remembers to revoke it. **Every assignment of a role with real authority should have an
end date.** Leavers are the classic audit failure: the volunteer who stepped down in 2019
still has an active account with treasurer access in 2026. A default term (e.g. one
organizational year, renewed explicitly) turns that from an invisible risk into a visible
expiry report.

*Recommendation:* require `valid_to` on all roles flagged `scope_required = true`, and
produce a periodic report of assignments expiring in the next 60 days. Tracked in
[../open-questions.md](../open-questions.md).

---

## 4. Access grants — the per-item layer

This is the "per-item permission" you asked for, and you specified it means a **capability
on that item**: "person X may act on item Y". Not a statement of attendance, and not a
separate eligibility check — those are other tables.

```
access_grant(
    id,
    person_id,
    scope_type,               -- 'event' | 'document' | 'org_unit' | 'membership' | ...
    scope_id,                 -- the concrete item
    level,                    -- revoked | view | contribute | manage | admin
    valid_from, valid_to,
    is_delegated,
    delegated_from,           -- person_id whose authority this came from
    granted_by, granted_at,
    grant_reason
)
```

### Levels

Ordered, cumulative — a higher level always subsumes the lower ones:

| Level | Numeric | Means |
|-------|---------|-------|
| `revoked` | 0 | Explicitly denied. **Overrides any other grant** — see §6. |
| `view` | 10 | Read the item |
| `contribute` | 20 | Read and add to it (sign up, comment, submit) |
| `manage` | 30 | Full control short of permissions administration |
| `admin` | 40 | Everything, including granting others access to this item |

`revoked` at 0 is important: without an explicit deny level there is no way to say "this
person must not see this event" when a broader grant would otherwise allow it.

### Why `scope_type`/`scope_id` and not one column per item type

`scope_id` has no foreign key — it is a polymorphic reference. This is a deliberate,
accepted trade-off:

- **Cost:** no referential integrity. A grant can point at a deleted event.
- **Benefit:** the permission system does not need a schema change every time a new
  grantable thing is invented, which — since you have deferred events, documents, and
  everything else — will happen repeatedly.

Mitigations, all of which are required:

1. A `scope_type` registry table validates `scope_type` values.
2. Deleting an item of a granted type must close its grants (an application-level
   obligation, tested).
3. A nightly consistency job reports orphaned grants.
4. `scope_id` is `BIGINT` and ids are never reused.

> If you would rather have strict referential integrity, the alternative is a
> `grantable_item` supertable that every grantable entity references. That is a heavier
> design; I have chosen polymorphism for flexibility, and flagged it here so you can
> overrule it. See [../open-questions.md](../open-questions.md).

---

## 5. The resolver

One function answers every authorization question. Written once, used everywhere — an
authorization rule that exists in two places will diverge.

```
can(person_id, permission_code, scope_type = null, scope_id = null, at = now()) → bool
```

Algorithm:

```
1. If person has an `access_grant` at level `revoked` covering this
   (scope_type, scope_id) and the resolved permission → return false.
   # explicit deny wins over everything, including roles

2. If scope_type is provided and the operation is on an item:
     look for an `access_grant` for this person on this item
     if found and level >= required_level_for(permission_code) → true

3. Ownership:
     if the target resource's owner is this person → true for `*.view`,
     `*.edit`, and self-service actions

4. Guardianship channel:
     if permission_code starts with 'dependent.' →
       resolve against guardianship_permission for the (guardian, dependent) pair
       (requires an active guardianship row)

5. Role channel:
     collect the person's active role_assignments at time `at`
     for unit-scoped operations, include assignments at ancestor units
     union their permissions
     if any grants permission_code (directly, or via its resource's `.admin`) → true

6. Otherwise → false
```

Points worth stressing:

- **Default deny.** Step 6. Any new resource starts with nobody able to touch it.
- **Explicit deny is checked first.** A suspension or a safeguarding restriction must not
  be overridable by an unrelated role. This ordering is the whole reason `revoked` exists.
- **Effective permissions are never stored.** They are computed per request. A stored
  permission snapshot *will* drift from the grants that produced it — the only question is
  how long before anyone notices.
- **Time is a parameter.** `at` defaults to now, but the resolver accepts a historical
  time. This enables "could this person have done this on that date?" — needed for auditing
  past actions, and free if built in from the start.

### Permission → required level mapping

```
permission_level(permission_id, level)   -- per scope_type
```

Example: `event.view` requires level `view`; `event.edit` requires `contribute`;
`event.manage` requires `manage`; `event.grant_access` requires `admin`. This table is what
lets one `access_grant` level serve many different permission codes without a hardcoded
mapping in code.

---

## 6. Precedence

When several channels apply, precedence is:

```
1. Explicit deny  (access_grant.level = 'revoked')     ← wins over everything
2. Ownership      (it's your own row)
3. Guardianship   (dependent.* permissions)
4. Item grant     (access_grant on this item)
5. Role           (role_assignment, widest scope)
6. Deny           (nothing matched)
```

Note that **item grant outranks role.** A unit leader's broad role does not override an
explicit `revoked` grant on a specific event, and a specific `manage` grant on one document
works even for someone with no organizational role at all — which is exactly the case for
an external contractor or a parent photographer.

---

## 7. Caching and invalidation

Permission checks happen on every request. Compute cheaply, cache carefully.

**Cache key must include everything the answer depends on:**

```
(person_id, permission_code, scope_type, scope_id, at_bucket)
```

where `at_bucket` truncates the timestamp to a granularity shorter than the shortest grant
duration you allow. If grants can start/end at an arbitrary second, a time-bucketed cache
is unsafe — use now() and a short TTL instead.

**Invalidate on:**

- any write to `role_assignment`, `access_grant`, `guardianship_permission`,
  `role_permission`
- **a merge** — this is the one that gets missed. Merging two people unions their
  permissions, so the survivor's cache must be cleared. See
  [03-identity-and-legacy.md](03-identity-and-legacy.md#5-the-merge-operation).
- a unit's parent changing (affects ancestor-inherited roles)
- a membership ending, if any permission is conditioned on membership status

**Alternative worth considering:** materialize `effective_permission` as a table refreshed
on write rather than cached per-request. Faster reads, but it is a denormalization and it
must be maintained transactionally — if a refresh fails silently you have an access bug
that nothing detects. If you take this path, add a verification job that recomputes and
compares. Recommendation: start with cache-only, add materialization only if measurement
demands it.

---

## 8. Delegation

A leader going on leave, a treasurer handing over during an audit — the common need to
lend authority temporarily.

```
access_grant(
    ...,
    is_delegated = true,
    delegated_from = <person_id>,
    valid_to = <required — delegations always expire>,
    grant_reason = 'annual leave 2026-07-01 to 2026-08-15'
)
```

Rules:

- A delegation **always** has an end date. Enforce with a constraint.
- Delegation cannot exceed the delegator's own authority — validate at grant time that
  every permission being delegated is one the delegator currently holds, and re-check at
  use time, because the delegator may lose it mid-delegation.
- The provenance is recorded, so an audit can answer "who really had this authority on
  that date?" — it lists both the holder and the delegator.
- Delegation of `system_admin` should be prohibited outright.

---

## 9. Anti-patterns this design rejects

Stated explicitly, because each is a common and expensive mistake:

| Rejected | Why | Instead |
|----------|-----|---------|
| `person.is_admin` boolean | Cannot scope, cannot date, cannot audit, cannot delegate | `role_assignment` |
| Role on `person` (`person.role = 'leader'`) | One role per person, no scope, no history | `role_assignment`, many per person |
| Checking membership type in code (`if type == 'adult'`) | Rules change; the check is invisible and untestable | A permission, granted to a role |
| Role → permission mapping hardcoded in the app | Cannot be reviewed by the organization, cannot change without deployment | `role_permission` table |
| Deriving access from guardianship without a grant | Authorization by identity is unauditable and unsafe | Explicit `guardianship_permission` |
| Deleting a grant to revoke it | Loses the audit trail of what was revoked when | `valid_to` + `revoked_at` |
| Two authorization implementations | They diverge; the weaker one becomes the exploit | One resolver, §5 |
| Unit leader sees all member data by default | Fails safeguarding review | Scoped role permissions, resolved per operation |

---

## 10. Open issues

- The complete permission catalog and the real role definitions — the starting set in §3 is
  a proposal awaiting your input.
- Whether authority inherits downward through the unit hierarchy (§3).
- Whether role assignments must have end dates (§3).
- Polymorphic `scope_id` vs a `grantable_item` supertable (§4).
- Whether any permission should be conditioned on membership being current — e.g. can a
  lapsed member still see their unit's events? Affects cache invalidation (§7).

All tracked in [../open-questions.md](../open-questions.md).
