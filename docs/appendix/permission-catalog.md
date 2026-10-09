# Appendix — Permission Catalog

Every permission code, its namespace, and the channel that resolves it.

This is the **proposed** catalog, seeded in
[../data-model/05-authorization.md](../data-model/05-authorization.md#12-seed-data--permissions).

> **Deliberately comprehensive and granular, and staying that way**
> ([D-055](../decisions/decision-log.md#d-055--the-permission-catalog-is-deliberately-comprehensive-and-granular)).
> This is a **menu, not a checklist.** Administrators assign people only the permissions they
> actually need; that is only possible if the capabilities exist as separate rows to assign.
> Further permissions arrive with the modules not yet specified — events, documents,
> communication, reporting ([§10](#10-deferred-namespaces)).
>
> **This is the opposite disposition from roles, and the asymmetry is deliberate.** Roles are
> *runtime data* the organization invents ([D-052](../decisions/decision-log.md#d-052--roles-are-runtime-data-the-seed-set-is-not-a-specification));
> permissions are *capabilities the code implements*. You cannot assign a power the schema
> cannot express, so a comprehensive permission catalog costs only rows — while a
> comprehensive *role* list would be a specification pretending to be data.
>
> Codes are still **stable identifiers**: adding one is free, renaming one is a migration
> ([§1](#code-shape)). What is *not* yet settled is the exact contents — tracked in §12.

---

## 1. Conventions

### Code shape

```
<resource>.<action>              e.g.  membership.request.approve
<resource>.<subresource>.<action> e.g.  unit_participation.view
```

`resource` is always the first segment and matches `permission.resource`. Codes are
**stable identifiers** — the `display_name` may change, the code may not. Renaming a code
is a breaking change requiring a migration that rewrites `role_permission` rows.

### There is no wildcard, except `system.admin`

Every capability in this catalog is **narrow and explicit**. A check for `X.y` is satisfied
by an exact grant of `X.y` — or by `system.admin`, which is checked outright and is the only
permission in the system that means *everything*.

```
A check for 'X.y' is satisfied by: an exact grant of 'X.y', OR 'system.admin'.
```

There are **no per-resource `admin` permissions.** The earlier convention that every resource
should expose an `<resource>.admin` subsuming its narrower codes — a prefix match computed in
the resolver — was **reversed by [D-068](../decisions/decision-log.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle)**,
which also deleted the resolver branch that implemented it.

**"Someone who can do everything about events" is a role, not a permission** — the
organization composes it from the thirteen `event.*` codes. That is the division D-052 already
drew: **the code implements capabilities, the organization groups them.** A per-resource
`admin` was the code guessing at a bundle on the organization's behalf.

**The cost, because it is real.** A new narrow permission is *not* automatically covered by
roles that should imply it; someone must add it. Integrity check **18** is the safety net the
wildcard used to be — it lists permissions no role grants, which is what a missed bundle looks
like. It fails **closed**: a capability goes unheld and somebody says so, rather than a
capability going unmeant and nobody saying so.

### Three things named "admin", which are not the same thing

The word survives in three unrelated places. When it comes up in conversation, say which:

| Shape | What it is | Deleted by D-068? |
|-------|-----------|-------------------|
| `access_level.admin` (rank 40) | A **grant level** — how much authority a grant carries, in `view` < `contribute` < `manage` < `admin`. Used by `permission_level` to decide whether a given grant satisfies a given permission. | **No** — different mechanism, shares only a name |
| `<resource>.admin` | A **wildcard permission code** implying every sibling on that resource | **Yes** — all sixteen gone |
| `dependent.medical.admin` | An **action** meaning "edit", paired against `.view` inside a sub-resource. Implies nothing. | **No** — not a wildcard |

**`dependent.admin` also survives, and is worth understanding rather than pattern-matching.**
It is not a prefix-match artefact: it is a code a staff member *chooses and stores*, one row
in `guardianship_permission`, granting the full set for **one child**. A wildcard somebody
deliberately wrote is what D-068 endorses. It also has a property no resolver rule can have —
an explicit `is_granted = false` row **overrides** it, so a court-ordered restriction survives
a broad grant. See §9.

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
[../data-model/05-authorization.md](../data-model/05-authorization.md#11-integrity-checks).

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

> `person.merge` and `person.redact` are separated from `person.edit` deliberately. Both
> are irreversible in practice and both have privacy consequences far beyond editing a
> record.
>
> **Before [D-068](../decisions/decision-log.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle),**
> the way to keep them apart was to carve them out of `person.admin`'s prefix match — a
> special case in the resolver that was invisible in every role editor. Now there is no
> wildcard to carve out of, and the question moves somewhere reviewable: a role bundling all
> of `person.*` reaches them, and you can *see* it in `role_permission`. **The guidance that
> replaces the special case is in §11** — no seeded role mixes `person.merge` or
> `person.redact` with routine `person.edit`, and one that does should be named for what it
> is. This is now a report a person can read, not a caveat about a resolver rule.

> **`person.background_check.*` is gone** ([D-043](../decisions/decision-log.md#d-043--no-background-checks-are-recorded-in-this-system)).
> The organization has no background checks handled by this system, so there is nothing to
> view and nothing to record. If that changes, the permission pair and a dated record with an
> `expires_at` are the natural shape — and it would belong here, next to `person.*`, because
> a clearance is a fact about a person and not about their membership.

## 3. Accounts

| Code | Namespace | Sens. | Grants |
|------|-----------|-------|--------|
| `account.view` | — | ⚠ | See account records |
| `account.create` | — | | Create an account for someone |
| `account.suspend` | — | ⚠ | Suspend an account |
| `account.close` | — | ⚠ | Close an account |
| `account.credential.reset` | — | 🔒 | Issue a credential reset |

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
| `unit_participation.view` | — | ⚠ | See who takes part in a sub-unit |
| `unit_participation.manage` | — | ⚠ | Add, move or end participation |

> **`membership.terminate` is the most consequential non-system permission in the
> catalog.** A lapse is administrative; a termination is a decision about a person's
> standing in a youth organization, frequently with safeguarding and reputational
> consequences. It should be held by very few people, and it must not be implied by
> `membership.lapse`. Grant it explicitly, per person.

> **`membership.transfer` is gone.** "Transfer a member between units" was an artefact of
> units holding memberships. With participation ([D-041](../decisions/decision-log.md#d-041--belonging-to-a-sub-unit-is-a-participation-record-not-a-membership)),
> moving between sub-units is `unit_participation.manage` — close one row, open another —
> and it does not touch the person's membership at all. There is nothing to transfer.

> **These permissions are gated by membership when held through a role that requires one**
> ([D-039](../decisions/decision-log.md#d-039--member-permissions-require-a-current-paid-membership)).
> The gate is a property of the *role*, not of the permission, so it is not visible in this
> table — see [../data-model/05-authorization.md §3](../data-model/05-authorization.md#3-role-and-role_permission).
> The single exception is `system.gate_exempt` (§7), which *is* the gate's waiver and is
> therefore exempt from the gate itself ([D-051](../decisions/decision-log.md#d-051--the-membership-gate-is-waived-by-a-permission-not-only-by-a-role-flag)).

## 5. Organization and positions

| Code | Namespace | Sens. | Grants |
|------|-----------|-------|--------|
| `org_unit.view` | — | | See units |
| `org_unit.create` | — | | Create a unit |
| `org_unit.edit` | — | | Edit a unit's details |
| `org_unit.rename` | — | | Rename or renumber a unit |
| `org_unit.restructure` | — | ⚠ | Split or merge units |
| `org_unit.close` | — | ⚠ | Close a unit |
| `position.view` | — | | See positions |
| `position.assign` | — | ⚠ | Appoint someone to a position |

> `org_unit.restructure` is separated because a split rewrites the answer to historical
> questions. It is not routine editing. **Reparenting is no longer among the things it
> grants** — a unit cannot change parent at all
> ([D-036](../decisions/decision-log.md#d-036--units-cannot-be-reparented-a-unit-that-moves-is-a-new-unit)),
> so the permission covers splits and mergers and the closing of a unit that "moved".

## 5a. Scope exposure and audiences

Two mechanisms that had been missing from this catalog while sitting in the seed data and
carrying some of the design's weight. Both are now listed, and the first is arguably the most
consequential permission in the authorization model.

| Code | Namespace | Sens. | Grants |
|------|-----------|-------|--------|
| `scope.expose` | — | 🔒 | **Expose this unit's scope** to a parent unit's role assignment |
| `scope.exposure.review` | — | ⚠ | See and revoke the exposures made over this unit |
| `audience.view` | — | | See built-in audiences and named groups |
| `audience.manage` | — | ⚠ | Create and populate named groups |

> **`scope.expose` is the only door between unit levels.** Authority never inherits downward
> ([D-031](../decisions/decision-log.md#d-031--no-downward-inheritance-of-authority-scope_exposure-is-the-only-crossing)),
> and this permission is the single mechanism that crosses the boundary — so it is graded 🔒
> despite being an obscure-sounding code, and it is *higher*-stakes than several codes with
> more obvious names.
>
> **What makes it safe is who can write it.** Every `scope_exposure` row is written **by the
> unit it covers**: a parent unit's officer cannot satisfy it for a child unit, which is what
> makes the no-inheritance rule enforceable rather than aspirational
> ([D-049](../decisions/decision-log.md#d-049--the-root-may-not-read-into-its-sub-units-scope_exposure-is-the-only-crossing)).
> There is no bulk variant ([D-045](../decisions/decision-log.md#d-045--the-bulk-scope-exposure-tool-is-removed)) —
> every row is a deliberate, individual, attributable decision about one assignment.

> **`audience.manage` is the permission that creates a grant target.** Whoever holds it can
> assemble a named list of people which a later `access_grant` may then address
> ([D-042](../decisions/decision-log.md#d-042--grants-may-target-audiences-not-only-individuals)) —
> so it is authority over *who could be granted*, one step removed from granting. Whether it
> belongs to a dedicated `audience_admin` or to unit leaders is open (§12).

---

## 6. Guardianship

| Code | Namespace | Sens. | Grants |
|------|-----------|-------|--------|
| `guardianship.view` | — | ⚠⚠ | See guardianship relationships |
| `guardianship.create` | — | ⚠⚠ | Record a guardianship |
| `guardianship.end` | — | ⚠⚠ | End a guardianship |
| `guardianship.permission.grant` | — | 🔒 | **Grant guardian permissions** |

## 7. Permissions administration

| Code | Namespace | Sens. | Grants |
|------|-----------|-------|--------|
| `role.view` | `system` | | See roles and their permissions |
| `role.create` | `system` | 🔒🔒 | Create a role |
| `role.edit` | `system` | 🔒🔒 | Change what a role grants — **takes effect immediately for every holder** |
| `role.delete` | `system` | 🔒🔒 | Delete a role. Only possible if it was **never assigned** and is not a system role |
| `role.assign` | `system` | 🔒🔒 | **Assign a role to a person** |
| `role.unassign` | `system` | 🔒 | End a role assignment |
| `permission.view` | `system` | | See the permission catalog |
| `permission.edit` | `system` | 🔒🔒 | Change the permission catalog |
| `access_grant.create` | — | ⚠ | Create an item grant |
| `access_grant.revoke` | — | ⚠ | Revoke an item grant |
| `system.admin` | `system` | 🔒🔒 | **Everything.** Single top-level capability. |
| `system.gate_exempt` | `system` | 🔒 | **Waive the membership gate for this person.** Every gated role they hold keeps granting while their fee is unpaid (D-051). |

> **`role.assign` is the permission to escalate privilege.** Whoever holds it can grant
> themselves `system.admin`. It must be held by very few people and every assignment must
> be logged and alerted on. Note that `system.admin` is deliberately a **single top-level
> permission** rather than a per-resource one — concentrating the most dangerous capability
> and alarming on its holders is safer than scattering equivalents of it.
>
> **Roles are runtime data, and these four permissions are how the organization administers
> them.** `role.create` composes a new permission group; `role.edit` changes what an existing
> one grants; `role.delete` removes one that was created by mistake. The seed roles in §11 are
> therefore a *starting point to be edited*, not a fixed vocabulary — which is why §11 no
> longer claims to answer "which roles carry `system.gate_exempt`". That is a configuration
> decision the organization makes at runtime, not one the specification can make for it.
>
> **There is no `role.retire`, and a role cannot be switched off**
> ([D-053](../decisions/decision-log.md#d-053--a-role-is-valid-always-only-its-assignment-is-temporal)).
> A role is a definition and is valid always; the period lives on the **assignment**. Ending a
> role's use means ending its assignments, which is `role.unassign` — one person at a time, or
> a loop over the holders. This is the right shape: what ends is *someone's authority*, and
> that is a fact about a person, not about a definition.
>
> **`role.edit` is a bulk privilege change wearing the clothes of a settings screen.** Editing
> a role's permissions takes effect immediately for **every holder**, with no assignment
> touched and no notification. It is marked 🔒🔒 alongside `role.assign` for that reason. The
> two are different powers — `role.assign` escalates one person, `role.edit` escalates
> everyone holding the role — and neither is implied by the other.
>
> **`role.delete` only works on a role that has never been assigned** and is not `is_system`;
> the trigger in
> [../data-model/05-authorization.md §3](../data-model/05-authorization.md#3-role-and-role_permission)
> enforces it. A role that has been held is left in place, so the answer to "what authority
> did this person have in 2019?" survives — which is precisely when someone asks it.
>
> **`access_grant.create` is scoped by `permission_level`:** holding it lets you grant
> others access *to items you have `admin` on*, and only at a level at or below your own.
> Without that restriction, any item-grant holder becomes a universal grantor.

## 8. Audit and system

| Code | Namespace | Sens. | Grants |
|------|-----------|-------|--------|
| `audit.view` | — | ⚠ | Read the audit log |
| `audit.export` | — | ⚠⚠ | Export audit records |
| `import.view` | — | ⚠ | See import batches |
| `import.stage` | — | | Stage an import |
| `import.apply` | — | 🔒 | Apply a staged import |
| `import.revert` | — | 🔒 | Revert an applied import |
| `report.view` | — | ⚠ | Run standard reports |
| `report.export` | — | ⚠⚠ | Export report data |

## 8a. Events

The per-item grant scope the whole authorization model was built toward. **Registration is
eligibility** — `event.register_self` at `contribute` *is* the rule for who may sign up, and
there is no separate eligibility mechanism ([D-060](../decisions/decision-log.md#d-060--eligibility-is-capability-there-is-no-separate-rule-engine)).

| Code | Namespace | Sens. | Grants |
|------|-----------|-------|--------|
| `event.view` | — | | See an event |
| `event.create` | — | | Create an event |
| `event.edit` | — | | Change an event's details, dates, capacity |
| `event.cancel` | — | ⚠ | **Cancel an event** — keeps registrations, notifies nobody by itself |
| `event.organizer.manage` | — | ⚠ | Add or remove organizers |
| `event.register_self` | — | | **Register yourself** — this is the eligibility rule |
| `event.register_other` | — | ⚠ | Register someone else (a minor, a walk-in) |
| `event.manage_participants` | — | ⚠ | **Manage the roster** — add or remove registrations, work the waitlist, promote |
| `event.presence.mark` | — | ⚠ | **Mark who turned up** — nothing else |
| `event.answer.view` | — | ⚠ | **Read registrant answers** (tent, dietary, …) |
| `event.question.manage` | — | ⚠ | Define what the event asks |
| `event.grant_access` | — | 🔒 | Grant access to an event. Requires level `admin` |
| `event.delete` | — | 🔒 | Delete an event — only possible with **no** registrations |

| Permission | scope_type | required_level |
|---|---|---|
| `event.view` | event | `view` |
| `event.register_self` | event | `contribute` |
| `event.presence.mark` | event | `contribute` |
| `event.edit`, `event.manage_participants`, `event.cancel` | event | `manage` |
| `event.grant_access`, `event.delete` | event | `admin` |

> **`event.presence.mark` is split off `event.manage_participants` on purpose, and it sits a
> level *lower*.** Marking presence is a task handed to whoever is at the door with a
> clipboard; managing the roster is a task for the event's leadership. One permission covering
> both forces the organization to hand the clipboard-holder the ability to delete a child from
> the camp roster. Splitting it costs two rows and makes the ordinary delegation ordinary —
> and note the level: presence is `contribute`, so **the volunteer taking the register is
> somebody with `contribute` on the event, which is the same bar as being able to register.**
> That is the right bar for the job, and it is not the bar for altering who is coming.
>
> It follows the shape of `membership.lapse` versus `membership.terminate`
> ([D-022](../decisions/decision-log.md#d-022--lapsing-and-termination-are-different-permissions)) —
> one routine, one consequential — and it is free to add because the catalog is a menu, not a
> fixed set ([D-055](../decisions/decision-log.md#d-055--the-permission-catalog-is-deliberately-comprehensive-and-granular)).
> **It was previously an open question (EV-5); it is resolved here as a split.**

> **`event.register_self` at `contribute` is the whole of [D-060](../decisions/decision-log.md#d-060--eligibility-is-capability-there-is-no-separate-rule-engine).** Granting a
> whole audience `contribute` on an event — one row — is how an open camp is opened:
>
> ```sql
> INSERT INTO access_grant (scope_type, scope_id, audience_id, level)
> VALUES ('event', :camp, (SELECT id FROM audience WHERE code = 'all_members'),
>         'contribute');
> ```
>
> An age-restricted camp is a `unit:<id>:participants` audience instead. **There is no age
> rule on the event and there will not be one** — an open event with an age ceiling is
> accepted as a risk, on the grounds that a registration-time condition the capability model
> does not know about is the first rule-engine rule
> ([D-070](../decisions/decision-log.md#d-070--an-event-has-no-age-ceiling-the-grant-is-the-rule)).
> If it ever needs closing, the shape is a new **built-in audience**, not a column.

> **`event.cancel` is separated from `event.edit` deliberately.** Cancelling is the most
> consequential thing anyone does to an event: it affects every registrant, it usually
> involves money, and it is a decision rather than an edit. It does not notify anyone — that
> is the communication module's job, and conflating the two makes "who cancelled this, and
> when?" harder to answer than it should be.

> **`event.delete` is on this list and `org_unit` has no equivalent, because events are the
> one thing in this schema that can be deleted.** A draft event with no registrations is a
> mistake to be cleaned up; anything else is cancelled, not deleted
> ([D-064](../decisions/decision-log.md#d-064--there-is-no-event-status-visibility-is-the-permission-model)).
> The trigger refuses deletion once anyone has registered.

> **`event.answer.view` is where [D-061](../decisions/decision-log.md#d-061--event-answers-are-read-by-that-events-organizers) lives.** Answers to an event's questions
> are readable by that event's organizers with no additional gate — which makes an event form
> the route by which a camp leader learns a child has a nut allergy, because the
> `dependent.*` namespace is unreachable by unit leaders. That is a deliberate widening and
> it is recorded as one. **Note that this permission is therefore a ⚠ on health-adjacent
> data**, and the discipline that only preference-level detail belongs on a form is guidance
> on the form's label, not a constraint the schema enforces.

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
| `dependent.event.view` | ⚠ | See the dependent's event registrations | Granted |
| `dependent.event.register` | | Register the dependent for events | Granted (self-registered) |
| `dependent.event.answer` | ⚠ | Answer an event's questions on their behalf | Granted (self-registered) |
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
| `document` | `document.view`, `document.create`, `document.edit`, `document.delete`, `document.grant_access` | |
| `fee` | `fee.view`, `fee.create`, `fee.waive`, `fee.refund` | ⛔ `fee.waive` and `fee.refund` are sensitive — hardship waivers must not be visible to unit leaders. |
| `payment` | `payment.view`, `payment.record`, `payment.reverse` | |
| `report` | `report.finance.view`, `report.membership.view`, `report.safeguarding.view` | ⚠⚠ `report.safeguarding.view` |
| `consent` | `consent.template.edit`, `consent.record.view` | |
| `message` | `message.send_to_unit`, `message.send_to_org` | |
| `partner` | *(namespace)* | For external organizations, if the model expands. |

Generate each resource's `permission_level` rows at the same time — see
[../data-model/05-authorization.md](../data-model/05-authorization.md#7-permission_level--connecting-permissions-to-grant-levels).

---

## 11. Roles — proposed seed set

**A starting point, not a specification.** Roles are runtime data: the organization creates
them, composes them from permissions, assigns them, edits what they grant, and deletes the
unused ones
([§7](../data-model/05-authorization.md#3-role-and-role_permission)). This section exists to
show the *shape* of a plausible set, so that the model can be reviewed against something
concrete. Do not read a row here as a requirement, and do not expect the list to survive
contact with the organization.

| Role | Scope required | `Req.` | Waives gate | Key permissions | Term |
|------|---------------|--------|-------------|-----------------|------|
| `system_admin` | organization | — | **yes** | `system.admin`, `system.gate_exempt` | 12 mo |
| `registrar` | organization | yes | no | `membership.request.*`, `membership.activate`, `person.*` (except merge/redact), `unit_participation.view` (root rows only — see note), `import.*` | 12 mo |
| `membership_approver` | organization | yes | no | `membership.request.review`, `membership.request.approve` | 12 mo |
| `treasurer` | organization or unit | yes | no | `fee.*`, `payment.*`, `report.finance.view` | 12 mo |
| `safeguarding_officer` | organization | yes | no | `report.safeguarding.view`, `membership.terminate` | 12 mo |
| `unit_admin` | org_unit | yes | no | `org_unit.view`, `unit_participation.view`, `position.view`, `org_unit.edit` (own unit only) | 12 mo |
| `unit_leader` | org_unit | **no** | no | `org_unit.view`, `unit_participation.view`, `position.view`, `event.*` (own unit), `report.membership.view` (own unit) | 12 mo |
| `assistant_leader` | org_unit | **no** | no | Subset of `unit_leader` | 12 mo |
| `audience_admin` | organization or unit | yes | no | `audience.view`, `audience.manage` | 12 mo |
| `identity_reviewer` | organization | yes | no | `person.merge`, `import.view`, `import.apply` | 12 mo |
| `auditor` | organization | **no** | no | `audit.view`, `audit.export`, `report.view` — **read-only, no writes** | 12 mo |

**Read the `*` shorthand as a bundle to be written out, not a wildcard to be relied on.**
Since [D-068](../decisions/decision-log.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle)
there is no resolver rule that makes `person.*` mean anything; the notation here is an
abbreviation for *"every `person.` code listed in §2"*, and a real role holds an explicit
`role_permission` row for each. Two consequences for whoever seeds this:

1. **`registrar` is written as `person.*` *except* `person.merge` and `person.redact`, and
   that exclusion is now literal.** It used to be a caveat about a wildcard's prefix match.
   It is now just the rows you do not insert — and it is visible in `role_permission`, dated,
   and alarmable. `identity_reviewer` is the role that *does* hold `person.merge`, listed
   beside it so the difference between the two is legible. **A role that bundles a resource
   *including* its irreversible codes should be named for that**, since nothing else records
   the choice any more.
2. **`unit_leader` holding `event.*` means thirteen explicit rows** (§8a), and a fourteenth
   added later is *not* in the role until someone adds it. Integrity check 18 surfaces an
   orphaned permission — one no role grants at all. It does not surface "this role arguably
   should have had it." That is the cost D-068 accepts, and it lands here, in the seed table,
   rather than being absorbed silently by the resolver.
holder's fee lapses ([D-039](../decisions/decision-log.md#d-039--member-permissions-require-a-current-paid-membership)).
The proposals follow one rule — **staff-like roles working on the organization's own records
require a membership; volunteer-facing roles do not.**

**`Waives gate`** is the separate, person-level *permission* `system.gate_exempt`
([D-051](../decisions/decision-log.md#d-051--the-membership-gate-is-waived-by-a-permission-not-only-by-a-role-flag)).
The two columns answer different questions and are not alternatives: `Req. = no` exempts
everyone who holds the role, everywhere; `system.gate_exempt` exempts a named person across
every role they hold. `system_admin` carries it because on 1 January the sweep lapses every
membership including the administrator's — without the exemption, the person who would repair
the system loses the ability to use it on the day it breaks.

> **This table is a starting set, not a specification** — and the `Waives gate` column is the
> clearest case of why. Roles are runtime data: the organization creates, edits and deletes
> them ([§7](../data-model/05-authorization.md#3-role-and-role_permission)). Whether a
> treasurer or a safeguarding officer should also survive their own lapse is a configuration
> decision the organization makes in the admin UI, not one this document can settle for it.
> Only `system_admin` is marked certain, because the lockout case above is a property of the
> system rather than a policy preference.

> **`registrar` holding `unit_participation.view` at organization scope is not a bug, and it
> will be read as one** ([D-049](../decisions/decision-log.md#d-049--the-root-may-not-read-into-its-sub-units-scope_exposure-is-the-only-crossing)).
> Scope is an exact match: the registrar's scope is the root unit, so the role reads the
> **root** participation rows — which is what "who is in the organization?" needs
> ([D-041](../decisions/decision-log.md#d-041--belonging-to-a-sub-unit-is-a-participation-record-not-a-membership)).
> It does **not** reach into any pack's roster; that requires the pack to write a
> `scope_exposure`. Someone who assumes a parent can see its children will "fix" this by
> widening the role, and that fix would silently reverse D-049.

**Four properties worth noting:**

1. **`membership_approver` is separate from `registrar`.** Deciding who becomes a member is
   a different act from processing records. If your organization wants one person to do
   both, grant both roles — but keep them separately attributable.
2. **`safeguarding_officer` holds `membership.terminate`.** The permission to end someone's
   membership sits with the person responsible for safeguarding, not with whoever chases
   fees. This is deliberate. Note that the role **lost** `person.background_check.*` and
   gained nothing in its place, because the organization records no background checks
   ([D-043](../decisions/decision-log.md#d-043--no-background-checks-are-recorded-in-this-system)).
3. **No role bundles `dependent.*` permissions.** Those come only from guardianship. A role
   that granted them would let a unit leader see members' medical records by virtue of a
   role assignment, which fails safeguarding review.
4. **`unit_leader` and `assistant_leader` are `Req. = no`.** They are held by volunteers, and
   the failure this prevents is specific: the volunteer whose own fee is unpaid still runs
   the Thursday meeting, and must not lose their roster the night it lapses. The
   corresponding `position.requires_membership` stays `true`, so the unpaid volunteer shows
   up on a chase-up report — **the report is how the organization notices, the resolver is
   not how it punishes.** See
   [../domain/06-authorization-model.md §4](../domain/06-authorization-model.md#4-roles--bundles-of-permissions).

---

## 12. Open issues

- **The catalog's disposition is settled; its contents are not.** It stays comprehensive and
  granular ([D-055](../decisions/decision-log.md#d-055--the-permission-catalog-is-deliberately-comprehensive-and-granular)),
  so there is no longer a "prune this down" review to do.
  What remains is *additive*: each unbuilt module brings its own permissions as it is
  specified, and unused rows cost nothing.
- **`Req.` and `Waives gate` are configuration, not specification.** Both columns are
  attributes of roles, and roles are runtime data the organization administers
  ([§7](../data-model/05-authorization.md#3-role-and-role_permission)). The values shown are
  reasoned defaults to start from
  ([D-039](../decisions/decision-log.md#d-039--member-permissions-require-a-current-paid-membership),
  [D-051](../decisions/decision-log.md#d-051--the-membership-gate-is-waived-by-a-permission-not-only-by-a-role-flag));
  the organization changes them in the admin UI. The one value that is *not* a preference is
  `system_admin` carrying `system.gate_exempt` — the 1 January lockout is a property of the
  system, not a policy choice.
- Whether `report.*` should be per-report permissions or one `report.view` with
  row-level filtering.
- Whether the organization has roles this catalog does not anticipate (a chaplain, a
  quartermaster, a camp chief). **This is now answerable by the organization itself** rather
  than by a schema change — which is the point of roles being runtime data.
- Which built-in audiences the organization needs, and who may create named groups —
  `audience_admin` is proposed, but it may belong to unit leaders instead
  ([D-042](../decisions/decision-log.md#d-042--grants-may-target-audiences-not-only-individuals)).

**Resolved and no longer open**, kept visible so the reasoning survives: whether
`person.admin` should subsume `person.merge` and `person.redact` (moot — there are no
per-resource `admin` permissions at all, and the question moved into reviewable role contents,
D-068); whether `event.manage_participants` should split off presence (it did, into
`event.presence.mark` at `contribute` — EV-5); the `event` resource's real permission set
(§8a, thirteen codes); whether any permission should require current membership status (yes,
via the role — D-039);
`person.background_check.*` (removed — D-043); `membership.transfer` (obsolete once
participation replaced unit membership — D-041); and whether `org_unit.restructure` includes
reparenting (it cannot — D-036).

All tracked in [../open-questions.md](../open-questions.md).
