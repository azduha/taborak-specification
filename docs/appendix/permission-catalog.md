# Appendix — Permission Catalog

Every permission code, its namespace, and the channel that resolves it.

This is the **proposed** catalog, seeded in
[../data-model/05-authorization.md](../data-model/05-authorization.md#12-what-the-organization-starts-with).

> **Deliberately comprehensive and granular, and staying that way**
> ([D-055](../decisions/decision-log.md#d-055--the-permission-catalog-is-deliberately-comprehensive-and-granular)).
> This is a **menu, not a checklist.** Administrators assign people only the permissions they
> actually need; that is only possible if the capabilities exist as separate rows to assign.
> Further permissions arrive with the modules not yet specified — documents and communication.
> Events were on that list and are no longer: §8a carries their thirteen codes
> ([§10](#10-deferred-namespaces)).
>
> **This is the opposite disposition from roles, and the asymmetry is deliberate.** Roles are
> *runtime data* the organization invents ([D-052](../decisions/decision-log.md#d-052--roles-are-runtime-data-the-seed-set-is-not-a-specification));
> permissions are *capabilities the code implements*. You cannot assign a power the data model
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

### Two things named "admin", which are not the same thing

The word used to be ambiguous three ways. Two rounds of deletion left two, and the third is
recorded as deleted rather than quietly dropped:

| Shape | What it is | Status |
|-------|-----------|--------|
| `access_level.admin` (rank 40) | A **grant level** — how much authority a grant carries, in `view` < `contribute` < `manage` < `admin`. Used by `permission_level` to decide whether a given grant satisfies a given permission. | **Real, untouched** |
| `system.admin` | The **one wildcard permission**: everything, held through a role, never through an item grant | **Real, untouched** |
| `<resource>.admin` | A **wildcard permission code** implying every sibling on that resource | **Deleted** — all sixteen, by [D-068](../decisions/decision-log.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle) |
| `dependent.medical.admin`, `dependent.admin` | An **action** meaning "edit", paired against `.view` inside a sub-resource; plus a shorthand for the whole set | **Deleted** — by [D-074](../decisions/decision-log.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular), which reduced a guardian's rights to `none` / `view` / `write` |

**D-068 exempted `dependent.admin` on purpose, and D-074 withdrew the exemption.** The reason
D-068 kept it was sound at the time: it was not a prefix match inferred by code but a value a
person deliberately stored on one row about one child. What changed is not the reasoning about
wildcards but the thing it was a value *of* — there is no longer a set of guardian capabilities for
a shorthand to stand for. **Read the two decisions together before reinstating anything that
spells `admin`.**

### Namespaces

| Namespace | Resolved against | Channel |
|-----------|------------------|---------|
| `NULL` | `role_assignment`, `access_grant`, ownership | 1, 3, 4 |
| `system` | `role_assignment` only — **never** item grants | 4 |

**There is no `dependent` namespace** ([D-074](../decisions/decision-log.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular));
§9 explains what replaced it, and what was lost with it.

**That leaves the guardianship channel with no prefix to dispatch on, which has to be answered
rather than left implied.** It used to route on `dependent.`, and the reason for routing by prefix
was that **no caller should decide which channel applies** — otherwise the same authorization rule
gets implemented twice, once correctly. It now routes on a fact about the request instead of a fact
about the name: **the channel is consulted whenever the person the action is *about* differs from
the person performing it.** That is stronger than the prefix rule, not weaker — under the old rule a
guardian asking to change their child's address with a `person.contact.edit` code would not have
routed through guardianship at all, because the code did not carry the right prefix. Nobody chooses
a channel; the shape of the request selects it.

The `guardianship.*` codes are additionally satisfiable by **being a party to the row**, and not
only by a grant ([D-073](../decisions/decision-log.md#d-073--guardianship-is-administered-by-its-own-parties-not-by-staff)).

`system` permissions remain non-grantable by item grant: `system.admin` must never be delegable to
a single event or to a parent.

### Sensitivity marker

The **Sens.** column flags permissions that need extra care:

| Mark | Meaning |
|------|---------|
| ⚠ | Granting it exposes personal data |
| ⚠⚠ | Granting it exposes children's personal data — or the same about an adult, where the code reads a whole person record rather than one field of it. Since [D-083](../decisions/decision-log.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data) there is **no separate *health data* class to name**: the mark grades what a grant *exposes*, not which field the code points at |
| 🔒 | Granting it confers authority over the permission system itself |
| ⛔ | Granting it can end someone's membership or standing |

These marks should drive UI warnings and the alerting in
[../data-model/05-authorization.md](../data-model/05-authorization.md#11-invariants-to-verify).

---

## 2. People and identity

| Code | Namespace | Sens. | Grants |
|------|-----------|-------|--------|
| `person.view` | — | ⚠⚠ | See person records — **all of them, including every descriptive value** |
| `person.create` | — | | Add a person record |
| `person.edit` | — | ⚠ | Change person details, including descriptive values |
| `person.contact.view` | — | ⚠ | See contact points |
| `person.contact.edit` | — | ⚠ | Change contact points |
| `person.merge` | — | 🔒 | Confirm identity matches and merge people — **and reverse a merge, and resolve a sign-up collision; there is no separate code for any of the three** |
| `person.redact` | — | 🔒 | Perform a GDPR-style erasure |
| `attribute.define` | — | | **Curate the vocabulary** of descriptive data — create, rename, merge or retire a code |

> `person.merge` and `person.redact` are separated from `person.edit` deliberately: both have privacy
> consequences far beyond editing a record. This paragraph used to justify the separation by calling
> both *irreversible in practice*, and
> [D-087](../decisions/decision-log.md#d-087--merge-chains-stay-because-reversing-a-merge-is-a-supported-operation)
> has withdrawn that premise for one of them — a merge can be reversed, and reversing it is a required
> operation. What survives the correction is the half the separation actually rests on: the merged
> **window** cannot be reversed, so the union of two people's permissions is real from the moment the
> merge commits, whatever is discovered afterwards. The separation stands on the narrower reason.
>
> **Three operations, and not one new code.** Round 8 introduced two capabilities and, each time,
> checked whether the catalog needed a row for it
> ([D-087](../decisions/decision-log.md#d-087--merge-chains-stay-because-reversing-a-merge-is-a-supported-operation),
> [D-089](../decisions/decision-log.md#d-089--one-live-account-a-colliding-sign-up-files-a-claim-and-creates-nothing)):
>
> - **Unmerge — reversing a merge a human approved: `person.merge`.** Undoing an identity correction
>   is the *same act* as making one, done by a named human, through the same queue, over the same rows.
>   A `person.unmerge` code would grade undoing a mistake as safer than making one. **Such a row stood
>   in §2 until round 8 and is removed here**; no seed role held it, so no role loses anything, and it
>   is recorded rather than quietly deleted because a reader of an older draft will look for it.
> - **Resolving a sign-up collision — working the claim a colliding registration files:
>   `person.merge`.** Resolving it is confirming or rejecting an `identity_hypothesis`, which is what
>   `person.merge` already means ([../domain/03-identity-and-legacy.md §4](../domain/03-identity-and-legacy.md#4-match-signals)).
> - **Linking a colliding sign-up to the person it matched: nothing, deliberately.** There is no
>   `account.link` and no `account_claim` table (§3). An automatic link once the e-mail verifies is
>   [D-004](../decisions/decision-log.md#d-004--no-automatic-merging-ever) under another name, and its
>   failure mode is one human's descriptive data becoming another human's record.
>
> The check itself is the point: this file is the only list of grantable codes, so a code minted while
> propagating a decision is a migration nobody decided.
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

> ### Descriptive data: two old codes and one new one
>
> Everything the system knows about a person other than their name, their gender and their age is
> one class of data, in fields the organization defines while it runs
> ([../domain/08-person-data.md](../domain/08-person-data.md),
> [../data-model/09-attributes.md](../data-model/09-attributes.md),
> [D-083](../decisions/decision-log.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data),
> [D-084](../decisions/decision-log.md#d-084--descriptive-data-is-organization-defined-at-runtime)).
> The catalog's whole involvement in that is one row added and none removed:
>
> - **Read: `person.view`. Write: `person.edit`. That is the entire access story.** **No read or
>   write code was added** for descriptive data, because there is nothing left for one to gate —
>   a code that separated, say, the allergy list from the rest of the record would reinstate the
>   privileged subset [D-083](../decisions/decision-log.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)
>   refused on the merits. There is therefore **no `health.*` or `medical.*` namespace and no
>   per-field access rule**, deliberately: `category` on a definition groups a form and grants
>   nothing. If a narrower tier is ever genuinely needed, the route is a decision entry about a
>   **second grant scope over a defined set of data**, not a code with a suggestive name.
> - **`attribute.define` is the new one, and it is the narrow one**
>   ([D-084](../decisions/decision-log.md#d-084--descriptive-data-is-organization-defined-at-runtime)):
>   it creates, renames, merges and retires a code — deciding what the organization *collects*,
>   which is what makes the data queryable. Recording a value against a code that does not exist
>   needs no such permission: it saves as a `proposed` definition and waits in the curation queue.
>   The mark column stays empty for it because it reads nobody's data — the vocabulary is rows
>   about codes, and the values underneath it are reached through `person.view` like anything else.
> - **`person.view` moved from ⚠ to ⚠⚠**, and the reason is the same decision: the marker grades
>   what a grant *exposes*, and this one now exposes everything known about a child — an allergy
>   list, an insurance number, a note about who the child actually lives with — through a single
>   code that used to be graded as ordinary personal data from when the record was smaller than
>   the person.
>
> `person.redact` reaches the layer too, and in the opposite direction from retiring a code:
> retiring one keeps the values, redacting a person erases theirs — in the audit trail as well as in
> the row, since a trail that still reads out an erased value has preserved it rather than missed it
> ([../data-model/09-attributes.md §6](../data-model/09-attributes.md#6-erasure-retirement-and-the-audit-payload)).

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

> **Nothing in this namespace links an account to a person it already belongs to, and the absence is
> decided, not overlooked.** A sign-up that strong-matches an existing person raises an
> `identity_hypothesis` and brings nothing into the world that a human has not approved — nothing
> merged, nothing linked, nothing activated; the account sits at `pending_verification` until a
> reviewer decides, and deciding is `person.merge` (§2,
> [D-089](../decisions/decision-log.md#d-089--one-live-account-a-colliding-sign-up-files-a-claim-and-creates-nothing)).
> So there is **no `account.link` code** and no claim object for one to act on: the second live
> account those would manage is exactly what the rule forbids, and the case they would have been asked
> to solve most often is already handled underneath permissions — `account_credential` holds many
> credentials for one account, so a member with a new e-mail address is adding a credential to the
> login they have, not acquiring a second one.

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

> **`unit_participation.manage` has no self-scoped variant, and none will be added**
> ([D-095](../decisions/decision-log.md#d-095--units-carry-no-restrictions-joining-one-is-somebody-elses-act)).
> Every grant of it means *"over this unit's roster"*, never *"over my own row"* — so **"nobody writes
> themselves into a unit"** is not a check the write performs, it is the shape of the thing being
> granted: there is no smaller grant to make yourself. The same holds for `position.assign` (§5):
> **nobody appoints themselves**, and D-095's instruction was explicitly not to mint a code that could
> express either act. This is also where the safeguarding story moved to. `org_unit_type.allows_minors`
> is removed, so no column says which units are for children and nothing here refuses to place a minor
> anywhere; what is left is this row held by named adults at one unit, the write audited the way any
> business-table write is, its recorded values emptied after 24 months
> ([D-088](../decisions/decision-log.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)),
> and a report of who holds it
> ([../domain/04-organization-structure.md §1](../domain/04-organization-structure.md#1-one-root-arbitrary-sub-units)).
> The gate in front of a *membership* is the fee; below the root there is no second gate and no fee, so
> this permission is the only one
> ([../domain/05-membership-lifecycle.md §1](../domain/05-membership-lifecycle.md#1-the-flow-you-described)).

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

> **`position.assign` is not something you can hold over yourself.** Appointments are made *to* people
> by whoever runs the unit, and there is no self-scoped form of the code and none is planned
> ([D-095](../decisions/decision-log.md#d-095--units-carry-no-restrictions-joining-one-is-somebody-elses-act),
> §4 above). The eligibility rules that do exist are about the position and not about the appointment —
> `position.min_age`, `max_holders`, `requires_membership` — and none of them is a self-service door.
>
> **An appointment writes one row, not two.** It does not create a role assignment, and no code in this
> catalog implies one: the derivation from a leadership position to a set of people lives in a group's
> filling rule, where it stops covering the person on the day the assignment closes
> ([D-091](../decisions/decision-log.md#d-091--a-permission-group-is-a-rule-and-a-list-at-once-and-a-rule-may-name-another-group),
> [../domain/04-organization-structure.md §4](../domain/04-organization-structure.md#4-positions)).

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
| `audience.view` | — | | See the sets a grant can be aimed at, and how each is filled |
| `audience.manage` | — | ⚠ | Create a group; change its filling rule, its listed people, or which groups it includes |

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
> assemble a set of people which a later `access_grant` may then address
> ([D-042](../decisions/decision-log.md#d-042--grants-may-target-audiences-not-only-individuals)) —
> so it is authority over *who could be granted*, one step removed from granting. Whether it
> belongs to a dedicated `audience_admin` or to unit leaders is open (§12).
>
> **Since [D-091](../decisions/decision-log.md#d-091--a-permission-group-is-a-rule-and-a-list-at-once-and-a-rule-may-name-another-group)
> this is one code over three powers, and it should not be read as though that were settled.** A group is
> now filled by an optional rule, an optional hand-kept list and an optional set of included groups, and
> the catalog has exactly one write code over the table — so the row above is read as covering all three
> arms, including **composition**: pointing a group at another group widens every grant aimed at any group
> that includes it, transitively, and `everyone` is a legal thing to include. Nothing here distinguishes
> *"add these five people"* from *"make this group contain everybody"*, and no separate code was invented
> to do it. That is recorded as an open question, not an answer (§12), and until it is answered the only
> control is the one D-091 names: **the editor that shows the people a grant actually reaches, expanded,
> rather than the group's name**
> ([../domain/06-authorization-model.md §6.2](../domain/06-authorization-model.md#62-audiences--a-rule-a-list-and-other-groups)).
>
> **The display is itself a read over people, and this catalog does not grade that yet.** Showing the
> resolved set means enumerating which humans a rule currently covers — which is what `audience.view` is
> for, on a row carrying no sensitivity mark. Listing the members of *"the leaders of every unit"* is not
> the same kind of act as listing the members of *"the kitchen crew"*, and the grading was written before
> the two could be the same query (§12).

---

## 6. Guardianship

| Code | Namespace | Sens. | Grants |
|------|-----------|-------|--------|
| `guardianship.view` | — | ⚠⚠ | See guardianship relationships |
| `guardianship.create` | — | ⚠⚠ | Record a guardianship |
| `guardianship.end` | — | ⚠⚠ | End a guardianship |
| `guardianship.assign` | — | ⚠⚠ | Add another guardian over the same dependent |
| `guardianship.change_right` | — | 🔒 | Change a guardianship's `right_level` |

> **These four are the only codes in the catalog that a private individual holds over their own
> household, without being granted them.** [D-073](../decisions/decision-log.md#d-073--guardianship-is-administered-by-its-own-parties-not-by-staff)
> makes the parties to a guardianship principals on the row: a guardian may end it, add another
> guardian, and change its level; the adult subject may end it over themselves. Staff hold the same
> codes and are **an** route, never **the** route.
>
> `guardianship.permission.grant` is **deleted** — it granted individual codes from the
> `dependent.*` namespace, and there is no such namespace to grant from
> ([D-074](../decisions/decision-log.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular)).
> `guardianship.change_right` replaces it, and does less: one value, three choices.

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
> **`role.delete` only works on a role that has never been assigned** and is not `is_system`.
> No delete may leave a `role_assignment` pointing at a role that is gone:
> [../data-model/05-authorization.md §3](../data-model/05-authorization.md#3-role-and-role_permission)
> states the guard and the order it refuses in. The two halves are not equally strong, and the
> difference is the reason this permission is not self-policing. The first is referential
> integrity — `role_assignment.role_id` references `role.id`, which is a migration-level
> constraint, so it refuses a delete that arrives from an import, from a manual fix, or from a
> second client as surely as from the screens. The second, `is_system`, is a property of the row
> being deleted and no index can see it: it is a check inside the transaction that deletes, and
> a model-layer guard there is a friendlier message, not the refusal. A role that has been held
> is left in place, so the answer to "what authority did this person have in 2019?" survives —
> which is precisely when someone asks it.
>
> **`access_grant.create` is scoped by `permission_level`:** holding it lets you grant
> others access *to items you have `admin` on*, and only at a level at or below your own.
> Without that restriction, any item-grant holder becomes a universal grantor.

## 8. Audit and system

| Code | Namespace | Sens. | Grants |
|------|-----------|-------|--------|
| `audit.view` | — | ⚠⚠ | Read the audit log — **including the before/after values it carries, which are person data like any other** |
| `audit.export` | — | ⚠⚠ | Export audit records |
| `import.view` | — | ⚠ | See import batches |
| `import.stage` | — | | Stage an import |
| `import.apply` | — | 🔒 | Apply a staged import |
| `import.revert` | — | 🔒 | Revert an applied import |
| `report.view` | — | ⚠ | Run standard reports |
| `report.export` | — | ⚠⚠ | Export report data |

> **`audit.view` is graded ⚠⚠, and the reason is a property of the trail rather than of any field
> it touches.** `audit_log` carries the before and after images of what changed, which makes it
> **a second copy of the person record** — descriptive values included, on the same terms as a
> `person_contact` or a note change. There is no exclusion list doing that work, and there must not
> be one: a rule naming the person fields whose values may not be logged is a privileged *subset* of
> the record, which is precisely what
> [D-083](../decisions/decision-log.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)
> refused — and it would hollow out [D-085](../decisions/decision-log.md#d-085--the-identity-machinery-stays-structured-the-boundary-is-rules-not-sensitivity),
> whose entire justification for overwriting a value in place is that the trail holds the sequence.
> So reading the trail over a scope **is** reading person data over that scope, and reading *more*
> than `person.view` shows: the current row is the organization's present belief, the trail is every
> belief it has held. What protects the trail is therefore the guard on it — scope, this mark, and
> who is granted it — exactly as the guard on `person.view` protects the record. The grading rule this
> applies — **the mark follows what a grant exposes, not the table a code names** — is
> [D-086](../decisions/decision-log.md#d-086--a-sensitivity-mark-grades-what-a-grant-exposes-not-the-table-it-reads),
> taken during propagation rather than from an answer, and reversible on one line.
>
> **The contents expire, which bounds this exposure without fixing it.** A row lives for the life of
> the system; its `old_values`/`new_values` are emptied **24 months after they were written**, by a
> scheduled job this corpus calls **payload reduction** — a third operation on the trail, distinct
> from redaction (a person's erasure, immediate and absolute, whatever the age of the row) and from an
> import revert ([D-088](../decisions/decision-log.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)).
> So *"the trail is every belief it has held"* is, since round 8, true only of the values less than two
> years old; about anything older the trail answers *who touched this row, when, and were they allowed
> to* and not *and to what*. For the risk this note is actually about — a grant graded wrongly, or
> simply held by the wrong person — that is a control worth having: it does not make the exposure
> impossible, it puts a horizon under it, which for an organization of this size is the realistic form
> the same protection takes. **AT-4 stays open**, because a window on the payload is an argument about
> how *long* a bad grant can do harm, not an answer to whether one permission should guard the trail.
>
> **Payload reduction needs no code here, and saying so is the check that it was considered.** Nobody
> performs it interactively: it is scheduled, and the guard on it is a check that alerts when a row
> past the window still carries a payload
> ([../data-model/06-audit-and-import.md §2.2](../data-model/06-audit-and-import.md#22-redaction-before-logging)).
> A permission for it would imply a person choosing not to run it.
>
> **The excluded-keys list survives, with a smaller and honest job.** Values that must never be
> logged *at all* belong on it: credential secrets, tokens, session material. Personal data does
> not, because personal data is protected by who may read the table, not by a list of its names.
>
> **Erasure reaches the payload.** A redaction that rewrote the business tables while the erased
> values stayed readable in the trail is a failed redaction, not a partial one
> ([../data-model/06-audit-and-import.md](../data-model/06-audit-and-import.md) §2,
> [../data-model/09-attributes.md](../data-model/09-attributes.md) §6).
>
> **`audit.export` sits at ⚠⚠ for a reason unrelated to what it reads.** An export carries the
> payload outside every mechanism this catalog governs: scope stops at the file, revoking the grant
> does not recall the copy, and a later redaction cannot reach it. It is graded by where the data
> goes, not by what the code is allowed to see.
>
> **Whether one permission is enough of a guard for all that is itself open** — tracked as **AT-4**
> ([../open-questions.md](../open-questions.md#at-4--is-one-permission-enough-to-guard-a-trail-that-holds-person-data)).
> The grading above is what is settled: the trail is read with the guard of person data, whichever
> permission or combination of permissions that guard turns out to be.

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
| `event.answer.view` | — | ⚠⚠ | **Read registrant answers** (tent, dietary, …) — see the note in §8a |
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
> whole audience `contribute` on an event is how an open camp is opened, and it is **one row**: an
> `access_grant` scoped to that event, addressed to the `all_members` audience, at level
> `contribute`. One row is the point — nobody is enumerated, so nobody is left out when the roster
> changes, and nothing has to be re-run when someone joins.
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
> one thing in this data model that can be deleted.** A draft event with no registrations is a
> mistake to be cleaned up; anything else is cancelled, not deleted
> ([D-064](../decisions/decision-log.md#d-064--there-is-no-event-status-visibility-is-the-permission-model)).
> **No event with even one registration row may be deleted** — Guard 2 in
> [../data-model/08-events.md §8](../data-model/08-events.md#guards) is the rule, and cancelling
> is what to do instead. The obligation is not the permission's to carry: `event.delete` decides
> who may ask, and only a migration-level constraint — `event_registration.event_id` referencing
> `event.id` with no cascade — refuses the same delete when it arrives from an import or a
> hand-written fix instead of a screen. Enforcing this in the model layer alone would leave the
> record of who was coming deletable by everything except the intended route.

> **`event.answer.view` is where [D-061](../decisions/decision-log.md#d-061--event-answers-are-read-by-that-events-organizers) lives.** Answers to an event's questions
> are readable by that event's organizers with no additional gate, because a unit leader holds
> no guardianship over the children in their unit — guardianship authority belongs to the guardians
> (§9). That is a deliberate widening and it is recorded as one.
>
> **Its premise has since been narrowed, and not by reversing it**
> ([D-085](../decisions/decision-log.md#d-085--the-identity-machinery-stays-structured-the-boundary-is-rules-not-sensitivity)).
> D-061 was written when an event form was the *only* route by which a camp leader learned a child
> has a nut allergy, because nothing else was readable. Descriptive data now exists
> ([../domain/08-person-data.md](../domain/08-person-data.md)) and a leader holding `person.view`
> over that unit reads a recorded allergy there, so the form is **the fallback for a fact the
> organization has not recorded, not the ceiling on what an organizer may know**. What survives
> unchanged is the decision itself, and the discipline below it.
>
> **This code is graded ⚠⚠, and it is the second time in this round that the marker followed the
> content rather than the category.** It sat at ⚠ beside a paragraph conceding that the answers under
> it can be clinical, which is the same mismatch `audit.view` had one section above: a payload that is
> children's personal data, graded as though it were logistics. [D-083](../decisions/decision-log.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)
> refuses a class of data more delicate than the rest, so either an adrenaline-pen answer is person
> data — it is — or the grading on the audit trail was wrong. **The raise narrows nothing**: D-061
> stands, an event's organizers read that event's answers with no additional gate, and all that changed
> is what a reviewer should notice before ticking the box for a role handed to thirty volunteers.
>
> **Which leaves the discipline exactly where it was, and says so plainly:** the rule that only
> preference-level detail belongs on a form is guidance on the form's label and nothing more. No layer
> enforces it and no layer can: nothing distinguishes
> "vegetarian" from "carries an adrenaline pen" to a database
> ([../data-model/08-events.md §7](../data-model/08-events.md#health-facts-and-the-discipline-this-requires)).
> It rests entirely on whoever writes the form — a convention, not a guard, and D-072's own
> sentence is the right way to read that.

## 9. There is no `dependent.*` namespace

**Eighteen codes deleted by [D-074](../decisions/decision-log.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular).**
A guardian's rights are `none`, `view`, or `write` — one value on the guardianship row, not a
capability list. **Nothing in this namespace may be reinstated by pattern-matching the old names;
there is no set of codes left for a name to stand for.**

| Old code | Became |
|---|---|
| `dependent.profile.view`, `dependent.contact.view`, `dependent.membership.view`, `dependent.event.view`, `dependent.fee.view`, `dependent.medical.view`, `dependent.achievement.view`, `dependent.document.view` | **`view`** — all of them, together. They can no longer be separated |
| `dependent.profile.admin`, `dependent.contact.manage`, `dependent.medical.admin`, `dependent.consent.admin` | **`write`** |
| `dependent.membership.request`, `dependent.event.register`, `dependent.event.answer`, `dependent.fee.pay`, `dependent.consent.give` | **`write`** — an act is not a narrower category than an edit |
| `dependent.admin` | Nothing. There is no set left to be a shorthand for |

**What is lost, stated as plainly as it should be.** A court order restricting one parent's access
to a child's medical record while leaving everything else in place **cannot be expressed**.
"Read-only, but not the medical file" cannot be expressed. A grandmother granted roster visibility
and nothing else is now a `view` guardian, which reaches the fee history and everything else the
system holds about that child. The old namespace existed for exactly these cases, and D-074 traded
them for a vocabulary a volunteer treasurer can hold in their head.

**The separation was then declined, not merely left unimplemented — and the difference matters to
anyone reading this table as a to-do list.**
[D-083](../decisions/decision-log.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)
put the court-order story to the organization directly and it was refused on the merits
(*"medical data is not different in any way"*), and the same answer removed the referent: there is
no medical record inside the person record to be shut out of, because everything other than name,
gender and age is one class of data reached by `person.view` and governed by the guardian's right
level whole ([../domain/08-person-data.md](../domain/08-person-data.md)). So *"read everything
except the diagnoses"* is not a sentence waiting on a mechanism somebody has yet to build; it is a
sentence the organization declined to want, which is why
[E-7 closed](../open-questions.md#e-7--closed--one-level-cannot-separate-the-medical-record-from-the-profile-and-nobody-wanted-to)
as a dissolved question rather than an answered one. **Read the inexpressibility above as settled,
not as pending work.**

**What still holds:**

- `write` ranks at `contribute` (20), **not** `manage`. A guardian cannot do organization-wide
  things, and cannot reach a different dependent's records — authority is per guardianship row.
- The **organization-wide deny channel is untouched.** A deny still beats any grant, at any scope
  ([D-032](../decisions/decision-log.md#d-032--deny-is-absolute-locality-orders-allows-only)), so
  "this guardian, nothing" remains expressible. What was lost is a *narrow* deny, not the ability
  to refuse.
- A guardianship at `none` grants literally nothing, so **being a guardian still grants nothing by
  itself** — the safeguarding property that motivated the eighteen codes survives without them.
- Answers to an event's questions are still read through `event.answer.view`, which is a role-side
  permission and never was a guardian one
  ([D-061](../decisions/decision-log.md#d-061--event-answers-are-read-by-that-events-organizers)).

**If the split turns out to matter in operation it is still a new decision** — one grant scope over
a defined set of data, argued from the current documents — and not a restoration from this table.
[E-7 is closed](../open-questions.md#e-7--closed--one-level-cannot-separate-the-medical-record-from-the-profile-and-nobody-wanted-to),
so reopening it means producing the case that was declined, not finding the code that was deleted.

See [../data-model/04-relationships.md §2](../data-model/04-relationships.md#2-the-guardians-right-none-view-or-write)
for the value, its defaults by `source`, and the ladder it is a range of.

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
| `message` | `message.send_direct`, `message.broadcast` | **Decided in shape, undesigned in detail** ([D-077](../decisions/decision-log.md#d-077--messaging-is-direct-by-default-broadcast-is-an-ordinary-scoped-permission-and-the-recipient-chooses-the-channel)). Everyone may send direct; `broadcast` is an ordinary **scoped** permission, so granted on a unit it reaches that unit and granted organization-wide it reaches everyone. The older `send_to_unit` / `send_to_org` pair is replaced by one code at two scopes. Recipient chooses the channel, which is not a permission at all. **A direct message to a minor is mirrored to that minor's guardians and the sender is told it will be** — no permission, no age branch in the resolver ([D-082](../decisions/decision-log.md#d-082--a-direct-message-to-a-minor-is-mirrored-to-the-minors-guardians)) |
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
   and alarmable. `identity_reviewer` is the role that *does* hold `person.merge` — and since
   round 8, `person.merge` is the whole of identity correction: merging, unmerging, and deciding a
   sign-up collision (§2) — listed beside `registrar` so the difference between the two is legible.
   **A role that bundles a resource *including* its 🔒 codes should be named for that**, since
   nothing else records the choice any more. The wording here used to say *irreversible* codes;
   [D-087](../decisions/decision-log.md#d-087--merge-chains-stay-because-reversing-a-merge-is-a-supported-operation)
   removed one of the two codes that wording pointed at, and the marker is the honest referent —
   `person.redact` is irreversible, `person.merge` is undoable but unions permissions the moment it
   runs.
2. **`unit_leader` holding `event.*` means thirteen explicit rows** (§8a), and a fourteenth
   added later is *not* in the role until someone adds it. Integrity check 18 surfaces an
   orphaned permission — one no role grants at all. It does not surface "this role arguably
   should have had it." That is the cost D-068 accepts, and it lands here, in the seed table,
   rather than being absorbed silently by the resolver.
3. **`auditor` is a role that reads the whole person record, and does it without `person.view`.**
   `audit.view` is graded ⚠⚠ in §8 precisely because the payload is a second copy of the record,
   so this row grants a ⚠⚠ read over what the system believed about a child and when it believed it.
   Since [D-088](../decisions/decision-log.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)
   that read has a floor it did not have before: payloads older than 24 months are emptied, so what is
   exposed reaches back two years and no further, while the who-did-what-to-which-row part reaches
   back for the life of the system. That bounds this row's exposure and does not soften its grading.
   Nothing here forbids it — it is a plausible role — but the row must not be
   described to anyone as "just the logs", and it is scoped and term-limited for the same reason
   the ⚠⚠ rows above it are.

`Req.` is `role.requires_membership`: whether the role stops granting anything when the
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

**Five properties worth noting:**

1. **`membership_approver` is separate from `registrar`.** Deciding who becomes a member is
   a different act from processing records. If your organization wants one person to do
   both, grant both roles — but keep them separately attributable.
2. **`safeguarding_officer` holds `membership.terminate`.** The permission to end someone's
   membership sits with the person responsible for safeguarding, not with whoever chases
   fees. This is deliberate. Note that the role **lost** `person.background_check.*` and
   gained nothing in its place, because the organization records no background checks
   ([D-043](../decisions/decision-log.md#d-043--no-background-checks-are-recorded-in-this-system)).
3. **No role is a guardian.** There used to be a rule that no role bundles
   `dependent.*`, and the namespace it named no longer exists
   ([D-074](../decisions/decision-log.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular)).
   The safeguarding property it protected is the one that survives, restated against the mechanism
   that now provides it: **the guardianship channel is only consulted when the subject of the act
   is someone else, and it only finds a guardianship row.** Leadership is not guardianship, so no
   role hands anyone a guardian's right over a child — not the right to act for that child, and not
   the row that decides what the family may see.
   **What a role can now do, and does openly, is read the child's record.** That sentence used to
   be false, and [D-083](../decisions/decision-log.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)
   is why it is not: with no privileged subset inside the person record, a leader granted
   `person.view` over their own unit reads the whole of a member's descriptive data, allergy list
   included ([../domain/08-person-data.md](../domain/08-person-data.md)). Nothing about leading a
   unit grants it — no channel opens on its own, and the row that would is explicit, scoped, dated
   and readable in `role_permission`. That is also why §2 now grades that code ⚠⚠: the safeguarding
   review moved from *"is there a code we kept out of roles?"* to *"which roles were given this
   one?"*, which is a question the catalog can actually answer.
   **Do not re-derive the old rule as a list of codes to keep out of roles** — the rule is about
   the channel, and there is no code left to quarantine.
4. **`unit_leader` and `assistant_leader` are `Req. = no`.** They are held by volunteers, and
   the failure this prevents is specific: the volunteer whose own fee is unpaid still runs
   the Thursday meeting, and must not lose their roster the night it lapses. The
   corresponding `position.requires_membership` stays `true`, so the unpaid volunteer shows
   up on a chase-up report — **the report is how the organization notices, the resolver is
   not how it punishes.** See
   [../domain/06-authorization-model.md §4](../domain/06-authorization-model.md#4-roles--bundles-of-permissions).
5. **`identity_reviewer` decides identity questions about children without a read over the person
   record.** The row carries `person.merge`, `import.view` and `import.apply`, and **`person.view` is
   not in it**: the reviewer works from the candidate pair, the `match_signals` recorded against it,
   and the names and dates those signals compare. That is deliberate as it stands — the question being
   decided is whether two rows are one human, and the descriptive values underneath are not evidence
   about that — and it is the same shape as `auditor` reading the trail without holding `person.view`.
   What round 8 changed is the pressure on it. This is now also the role a **blocked sign-up** lands
   on: an account held out of `active` by an unresolved hypothesis, with an age check alerting because
   the stalled item is a person who cannot log in
   ([D-089](../decisions/decision-log.md#d-089--one-live-account-a-colliding-sign-up-files-a-claim-and-creates-nothing)).
   **If reviewers begin asking for context they cannot see, that is the finding to act on**, and the two
   honest answers are a scoped, dated `person.view` on this role, or a review screen that shows more of
   the *signals*. Reaching instead for an organization-wide `person.view` would put the catalog's
   largest ⚠⚠ read in the role with the most write authority over identity.
6. **No role in this seed set holds `unit_participation.manage`, and since
   [D-095](../decisions/decision-log.md#d-095--units-carry-no-restrictions-joining-one-is-somebody-elses-act)
   that is a hole rather than a neutral omission.** As written, `unit_admin` and `unit_leader` may *see* a
   roster and cannot write one, which was survivable while a placement could be argued about from a unit
   type; it is not survivable now that this permission is the only thing standing between a person and a
   unit's roster, and that the answer behind D-095 is *"they will be assigned to the unit by the
   counselors"*. Whoever seeds this owes the write to whoever runs the unit — per unit, dated, and
   readable in the report that replaces the deleted flag. **It is recorded here instead of added to the
   table on purpose**: which volunteer role may place a child in a unit is the organization's decision to
   make, and an appendix that quietly hands it to `unit_leader` would be making a safeguarding choice on
   someone else's behalf.

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
  than by a change to the data model and a migration — which is the point of roles being runtime data.
- Which built-in groups the organization needs, and who may create the named ones —
  `audience_admin` is proposed, but it may belong to unit leaders instead
  ([D-042](../decisions/decision-log.md#d-042--grants-may-target-audiences-not-only-individuals),
  [F-5](../open-questions.md#f-5--which-built-in-audiences-are-needed-beyond-the-four-now-named)).
  This bullet used to say *"named groups"* as a kind, opposed to *"built-in audiences"*;
  [D-091](../decisions/decision-log.md#d-091--a-permission-group-is-a-rule-and-a-list-at-once-and-a-rule-may-name-another-group)
  deleted the kinds, so the open question is now only about who may create a group and which rules ship.
- **One code covers three powers over a group, and nothing separates the largest of them.**
  `audience.manage` is the only write code over the table, and since D-091 that table can be filled by a
  rule, by a hand-kept list, or by including other groups. **The inclusion arm is the one that worries**:
  it is the difference between adding five people and making a group contain everybody, and the second
  takes three edits and a save. Either the catalog documents composition as plainly inside
  `audience.manage` — accepting that whoever can edit a group can widen every grant aimed at any group
  that includes it — or composition gets a code of its own. **No code was invented here to fill the gap**;
  the interim control is the editor showing the expanded set, which is a user-interface requirement
  carried in [../domain/06-authorization-model.md §6.2](../domain/06-authorization-model.md#62-audiences--a-rule-a-list-and-other-groups),
  not a permission.
- **`audience.view` carries no sensitivity mark, and after D-091 the thing it shows is a list of people.**
  A grant aimed at a group used to name a set whose contents were mostly typed in; now the same row can
  resolve through positions, participations and memberships, and a group that includes `everyone` resolves
  to the whole organization. Whether reading a group's resolved membership needs a grade of its own — or
  whether `person.view` already covers it and the display is the leak to watch — is unsettled (§5a).
- **`attribute.define` is in the catalog and in no seed role, and that gap is the open half of the
  design.** The permission and its rules are settled (§2); who holds it, and how long a `proposed`
  code may sit before it is an embarrassment rather than a queue, are not — tracked as **AT-2** in
  [../open-questions.md](../open-questions.md#at-2--who-curates-the-vocabulary-and-how-long-may-a-proposal-sit). The risk of leaving it unheld is specific and slow:
  proposals keep arriving through ordinary data entry, and a vocabulary nobody curates stops
  answering questions while still storing everything
  ([../data-model/09-attributes.md §8](../data-model/09-attributes.md#8-integrity-checks)).
  **The import half of this is now answered**, and only that half: the codes the legacy batch's
  column→code map names arrive `live`, because a curator reads the map as one object before the batch
  applies, so the queue does not open several-hundred-deep on day one
  ([D-090](../decisions/decision-log.md#d-090--the-legacy-corpus-is-thousands-of-roster-rows-with-numbers-and-no-money),
  [../domain/03-identity-and-legacy.md §7](../domain/03-identity-and-legacy.md#7-legacy-import-pipeline)).
  Who holds the permission afterwards, day to day, is still what is open.
- **Which role holds the right to place a person in a unit is unanswered in the seed set**, and it is now
  the only question standing between a child and a unit's roster (§11.6). The catalog's side of it is
  settled — one code, unit-scoped, never self-scoped — so what is missing is not a code but a decision the
  organization has to record in `role` rows.

**Resolved and no longer open**, kept visible so the reasoning survives: whether
`person.admin` should subsume `person.merge` and `person.redact` (moot — there are no
per-resource `admin` permissions at all, and the question moved into reviewable role contents,
D-068); whether `event.manage_participants` should split off presence (it did, into
`event.presence.mark` at `contribute` — EV-5); the `event` resource's real permission set
(§8a, thirteen codes); whether any permission should require current membership status (yes,
via the role — D-039);
`person.background_check.*` (removed — D-043); `membership.transfer` (obsolete once
participation replaced unit membership — D-041); whether `org_unit.restructure` includes
reparenting (it cannot — D-036); whether reversing a merge deserves a code of its own (it does not —
undoing an identity correction is the same act as making one, so `person.unmerge` is gone from §2 and
unmerge is `person.merge`, D-087); and whether a colliding sign-up needs a claim object and a way to
link it (it needs neither — the hypothesis queue already exists and deciding it is `person.merge`,
D-089). From round 9: whether a person may hold `unit_participation.manage` or `position.assign` over
themselves (no — there is no self-scoped form of either and none will be added, D-095); whether anything
below the root needs a gate of its own (it does not — the fee is at the root and `unit_participation.manage`
is everywhere else, and the unit type carries no restriction at all, D-095); whether an appointment should
also write a role assignment (it should not — the derivation belongs on a group's filling rule, D-091,
which is a different question from whether a *role* may be held by a rule, and that one is still open as
F-12); and whether group membership needs a rule against nesting now that groups nest (it does not — a
cycle is refused when the edge is saved, which is a write path with no permission of its own, D-091).

All tracked in [../open-questions.md](../open-questions.md).
