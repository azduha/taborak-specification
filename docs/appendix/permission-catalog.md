# Appendix — Permission Catalog

Every permission code, its namespace, and the channel that resolves it.

This is the **proposed** catalog, seeded in
[../data-model/05-authorization.md](../data-model/05-authorization.md#10-seed-data--permissions).
It is a starting point for your refinement, not a specification. Expect to add, remove, and
rename.

---

## 1. Conventions

### Code shape

```
<resource>.<action>              e.g.  membership.request.approve
<resource>.<subresource>.<action> e.g.  person.background_check.manage
<resource>.admin                 e.g.  event.admin
```

`resource` is always the first segment and matches `permission.resource`. Codes are
**stable identifiers** — the `display_name` may change, the code may not. Renaming a code
is a breaking change requiring a migration that rewrites `role_permission` rows.

### The `admin` rule

Per your instruction: **every resource exposes an `<resource>.admin` permission that
subsumes all narrower ones.**

```
A check for 'X.y' is satisfied by an exact grant of 'X.y' OR a grant of 'X.admin'.
```

This is a **prefix match on the resource**, computed in the resolver, not a mapping table.
Consequence: adding a new narrow permission to a resource requires **no** change to any
role that grants that resource's `admin`. That is the whole point — otherwise every new
permission needs updating every role that should already have implied it, and someone will
miss one.

### Namespaces

| Namespace | Resolved against | Channel |
|-----------|------------------|---------|
| `NULL` | `role_assignment`, `access_grant`, ownership | 1, 3, 4 |
| `dependent` | `guardianship_permission` | 2 |
| `system` | `role_assignment` only — **never** item grants | 4 |

`system` permissions are deliberately non-grantable by item grant or guardianship:
`system.admin` must never be delegable to a single event or to a parent.

### Sensitivity marker

The **Sens.** column flags permissions that need extra care:

| Mark | Meaning |
|------|---------|
| ⚠ | Granting it exposes personal data |
| ⚠⚠ | Granting it exposes children's personal data or health data |
| 🔒 | Granting it confers authority over the permission system itself |
| ⛔ | Granting it can end someone's membership or standing |

These marks should drive UI warnings and the alerting in
[../data-model/05-authorization.md](../data-model/05-authorization.md#9-integrity-checks).

---

## 2. People and identity

| Code | Namespace | Sens. | Grants |
|------|-----------|-------|--------|
| `person.view` | — | ⚠ | See person records |
| `person.create` | — | | Add a person record |
| `person.edit` | — | ⚠ | Change person details |
| `person.contact.view` | — | ⚠ | See contact points |
| `person.contact.edit` | — | ⚠ | Change contact points |
| `person.merge` | — | 🔒 | Confirm identity matches and merge people |
| `person.unmerge` | — | 🔒 | Reverse a merge |
| `person.redact` | — | 🔒 | Perform a GDPR-style erasure |
| `person.background_check.view` | — | ⚠⚠ | See background-check status |
| `person.background_check.manage` | — | ⚠⚠ | Record and update background checks |
| `person.deceased.record` | — | | Mark a person deceased |
| `person.admin` | — | 🔒 | Full control over person records |

> `person.merge` and `person.redact` are separated from `person.edit` deliberately. Both
> are irreversible in practice and both have privacy consequences far beyond editing a
> record. **`person.admin` does not subsume them** — see §7.

## 3. Accounts

| Code | Namespace | Sens. | Grants |
|------|-----------|-------|--------|
| `account.view` | — | ⚠ | See account records |
| `account.create` | — | | Create an account for someone |
| `account.suspend` | — | ⚠ | Suspend an account |
| `account.close` | — | ⚠ | Close an account |
| `account.credential.reset` | — | 🔒 | Issue a credential reset |
| `account.admin` | — | 🔒 | Full control over accounts |

> `account.suspend` is **not** `membership.suspend`. Suspending a login does not remove
> someone from the organization; the two are separate lifecycles and separate permissions.

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
| `membership.transfer` | — | | Transfer a member between units |
| `membership.admin` | — | ⛔ | Full control over memberships |

> **`membership.terminate` is the most consequential non-system permission in the
> catalog.** A lapse is administrative; a termination is a decision about a person's
> standing in a youth organization, frequently with safeguarding and reputational
> consequences. It should be held by very few people, and it must not be implied by
> `membership.lapse`. Grant it explicitly, per person.

## 5. Organization and positions

| Code | Namespace | Sens. | Grants |
|------|-----------|-------|--------|
| `org_unit.view` | — | | See units |
| `org_unit.create` | — | | Create a unit |
| `org_unit.edit` | — | | Edit a unit's details |
| `org_unit.rename` | — | | Rename or renumber a unit |
| `org_unit.restructure` | — | ⚠ | Split, merge, or reparent units |
| `org_unit.close` | — | ⚠ | Close a unit |
| `org_unit.admin` | — | 🔒 | Full control over units |
| `position.view` | — | | See positions |
| `position.assign` | — | ⚠ | Appoint someone to a position |
| `position.admin` | — | 🔒 | Full control over positions |

> `org_unit.restructure` is separated because a reparent or split rewrites the answer to
> historical questions. It is not routine editing.

## 6. Guardianship

| Code | Namespace | Sens. | Grants |
|------|-----------|-------|--------|
| `guardianship.view` | — | ⚠⚠ | See guardianship relationships |
| `guardianship.create` | — | ⚠⚠ | Record a guardianship |
| `guardianship.end` | — | ⚠⚠ | End a guardianship |
| `guardianship.permission.grant` | — | 🔒 | **Grant guardian permissions** |
| `guardianship.admin` | — | 🔒 | Full control over guardianship records |

## 7. Permissions administration

| Code | Namespace | Sens. | Grants |
|------|-----------|-------|--------|
| `role.view` | `system` | | See roles and their permissions |
| `role.edit` | `system` | 🔒 | Change what a role grants |
| `role.assign` | `system` | 🔒🔒 | **Assign a role to a person** |
| `role.unassign` | `system` | 🔒 | End a role assignment |
| `permission.view` | `system` | | See the permission catalog |
| `permission.edit` | `system` | 🔒🔒 | Change the permission catalog |
| `access_grant.create` | — | ⚠ | Create an item grant |
| `access_grant.revoke` | — | ⚠ | Revoke an item grant |
| `system.admin` | `system` | 🔒🔒 | **Everything.** Single top-level capability. |

> **`role.assign` is the permission to escalate privilege.** Whoever holds it can grant
> themselves `system.admin`. It must be held by very few people and every assignment must
> be logged and alerted on. Note that `system.admin` is deliberately a **single top-level
> permission** rather than a per-resource one — concentrating the most dangerous capability
> and alarming on its holders is safer than scattering equivalents of it.
>
> **`access_grant.create` is scoped by `permission_level`:** holding it lets you grant
> others access *to items you have `admin` on*, and only at a level at or below your own.
> Without that restriction, any item-grant holder becomes a universal grantor.

## 8. Audit and system

| Code | Namespace | Sens. | Grants |
|------|-----------|-------|--------|
| `audit.view` | — | ⚠ | Read the audit log |
| `audit.export` | — | ⚠⚠ | Export audit records |
| `audit.admin` | — | 🔒 | Administer audit settings |
| `import.view` | — | ⚠ | See import batches |
| `import.stage` | — | | Stage an import |
| `import.apply` | — | 🔒 | Apply a staged import |
| `import.revert` | — | 🔒 | Revert an applied import |
| `report.view` | — | ⚠ | Run standard reports |
| `report.export` | — | ⚠⚠ | Export report data |

## 9. The `dependent.*` namespace

Resolved **only** against `guardianship_permission`, never against roles. A unit leader
does not get these by virtue of leading the unit — that is a safeguarding property, argued
in [../domain/02-actors.md](../domain/02-actors.md#5-acting-on-behalf).

| Code | Sens. | Grants | Typical default |
|------|-------|--------|-----------------|
| `dependent.profile.view` | ⚠ | See name, birth date, membership state | Granted |
| `dependent.profile.admin` | ⚠ | View and edit the profile | On request |
| `dependent.contact.view` | ⚠ | See contact points | Granted |
| `dependent.contact.manage` | ⚠ | Edit contact points | Granted (self-registered) |
| `dependent.membership.view` | ⚠ | See membership history | Granted |
| `dependent.membership.request` | | Submit or renew a membership | Granted (self-registered) |
| `dependent.event.view` | ⚠ | See event registrations | Granted |
| `dependent.event.register` | | Register for events | Granted (self-registered) |
| `dependent.fee.view` | ⚠ | See fee and payment records | Granted |
| `dependent.fee.pay` | | Pay fees | Granted (self-registered) |
| `dependent.medical.view` | ⚠⚠ | **See medical and allergy records** | Granted; **often restricted** |
| `dependent.medical.admin` | ⚠⚠ | Edit medical records | On request |
| `dependent.consent.give` | ⚠ | Give consents (photo, transport, activity) | Granted |
| `dependent.consent.admin` | ⚠ | Manage consent records | On request |
| `dependent.achievement.view` | | See badges, awards, progress | Granted |
| `dependent.document.view` | ⚠ | See the dependent's documents | Granted |
| `dependent.admin` | 🔒 | **All of the above** | On request |

> **`dependent.medical.view` and `dependent.consent.give` are deliberately separate.** A
> parent who may consent to a camp is not necessarily a parent who may read a medical file,
> and a court order frequently restricts one without the other. Conflating them makes the
> common restriction inexpressible.
>
> An explicit `is_granted = false` row **overrides** `dependent.admin`. A court-ordered
> restriction is not overridable by a broader grant — see
> [../data-model/04-relationships.md](../data-model/04-relationships.md#2-guardianship_permission).

## 10. Deferred namespaces

Placeholders for features you have not specified. Listed so the naming convention is
established before anyone invents an inconsistent one.

| Resource | Permission | Notes |
|----------|-----------|-------|
| `event` | `event.view`, `event.create`, `event.edit`, `event.manage_participants`, `event.register_self`, `event.register_other`, `event.grant_access`, `event.admin` | The per-item grant scope you described. `event.grant_access` requires level `admin`. |
| `document` | `document.view`, `document.create`, `document.edit`, `document.delete`, `document.grant_access`, `document.admin` | |
| `fee` | `fee.view`, `fee.create`, `fee.waive`, `fee.refund`, `fee.admin` | ⛔ `fee.waive` and `fee.refund` are sensitive — hardship waivers must not be visible to unit leaders. |
| `payment` | `payment.view`, `payment.record`, `payment.reverse`, `payment.admin` | |
| `report` | `report.finance.view`, `report.membership.view`, `report.safeguarding.view`, `report.admin` | ⚠⚠ `report.safeguarding.view` |
| `consent` | `consent.template.edit`, `consent.record.view`, `consent.admin` | |
| `message` | `message.send_to_unit`, `message.send_to_org`, `message.admin` | |
| `partner` | *(namespace)* | For external organizations, if the model expands. |

Generate each resource's `permission_level` rows at the same time — see
[../data-model/05-authorization.md](../data-model/05-authorization.md#6-permission_level--connecting-permissions-to-grant-levels).

---

## 11. Roles — proposed seed set

Awaiting your refinement. Each is a bundle; revisit before implementing.

| Role | Scope required | Key permissions | Term |
|------|---------------|-----------------|------|
| `system_admin` | organization | `system.admin` | 12 mo |
| `registrar` | organization | `membership.request.*`, `membership.activate`, `person.*` (except merge/redact), `unit_membership.*`, `import.*` | 12 mo |
| `membership_approver` | organization | `membership.request.review`, `membership.request.approve` | 12 mo |
| `treasurer` | organization or unit | `fee.*`, `payment.*`, `report.finance.view` | 12 mo |
| `safeguarding_officer` | organization | `person.background_check.*`, `report.safeguarding.view`, `membership.terminate` | 12 mo |
| `group_admin` | org_unit | `org_unit.view`, `unit_member.view`, `position.view`, `org_unit.edit` (own unit only) | 12 mo |
| `unit_leader` | org_unit | `org_unit.view`, `unit_member.view`, `position.view`, `event.*` (own unit), `report.membership.view` (own unit) | 12 mo |
| `assistant_leader` | org_unit | Subset of `unit_leader` | 12 mo |
| `identity_reviewer` | organization | `person.merge`, `import.view`, `import.apply` | 12 mo |
| `auditor` | organization | `audit.view`, `audit.export`, `report.view` — **read-only, no writes** | 12 mo |

**Three properties worth noting:**

1. **`membership_approver` is separate from `registrar`.** Deciding who becomes a member is
   a different act from processing records. If your organization wants one person to do
   both, grant both roles — but keep them separately attributable.
2. **`safeguarding_officer` holds `membership.terminate`.** The permission to end someone's
   membership sits with the person responsible for safeguarding, not with whoever chases
   fees. This is deliberate.
3. **No role bundles `dependent.*` permissions.** Those come only from guardianship. A role
   that granted them would let a unit leader see members' medical records by virtue of a
   role assignment, which fails safeguarding review.

---

## 12. Open issues

- **The entire catalog needs your review.** Which of these does your organization actually
  need? Which are missing? Most organizations need fewer roles than they think and more
  granular permissions than they expect.
- Whether `person.admin` should subsume `person.merge` and `person.redact` (recommend no).
- Whether any permission should require current membership status — affects cache
  invalidation.
- Whether `report.*` should be per-report permissions or one `report.view` with
  row-level filtering.
- The `event` resource's real permission set, once events are specified.
- Whether the organization has roles this catalog does not anticipate (a chaplain, a
  quartermaster, a camp chief).

All tracked in [../open-questions.md](../open-questions.md).
