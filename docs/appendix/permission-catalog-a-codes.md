# Appendix — Permission Catalog: the codes

Every code the system ships, grouped by the thing it acts on — people, accounts, membership, the unit, groups and roles and audiences, guardianship, the permission system itself, audit and system, events, and the keys that call from outside — each with the grant that carries it.

**Section numbers are shared across the three parts** and never renumbered, because other pages cite them by number and their anchors are built from them: [permission-catalog.md](permission-catalog.md) holds §1, the conventions; [permission-catalog-a-codes.md](permission-catalog-a-codes.md) holds §2–§8b, the codes; [permission-catalog-b-roles-and-open-issues.md](permission-catalog-b-roles-and-open-issues.md) holds §9–§12, the namespaces that are not here, the deferred ones, the role seed and what is open.

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

> **Why `person.merge` and `person.redact` are not part of `person.edit`:** both have privacy
> consequences far beyond editing a record, and the merged **window** cannot be reversed — the union of
> two people's permissions is real from the moment the merge commits, whatever is discovered afterwards.
> Reversing a merge is a supported operation, and it is the same code, because undoing an identity
> correction is the same act as making one
> ([D-087](../decisions/round-07-08.md#d-087--merge-chains-stay-because-reversing-a-merge-is-a-supported-operation)).
>
> **Three operations, one code.**
>
> - **Unmerging a merge a human approved: `person.merge`.** Same named human, same queue, same rows. A
>   `person.unmerge` code would grade undoing a mistake as safer than making one.
> - **Resolving a sign-up collision — working the claim a colliding registration files: `person.merge`.**
>   Resolving it is confirming or rejecting an `identity_hypothesis`, which is what `person.merge` already
>   means ([../domain/03-identity-and-legacy.md §4](../domain/03-identity-and-legacy.md#4-match-signals)).
> - **Linking a colliding sign-up to the person it matched: nothing, deliberately.** There is no
>   `account.link` and no `account_claim` table (§3). An automatic link once the e-mail verifies is
>   [D-004](../decisions/round-01a.md#d-004--no-automatic-merging-ever) under another name, and its failure
>   mode is one human's descriptive data becoming another human's record.
>
> **What that means for a bundle.** There is no wildcard to carve an exception out of. Since
> [D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)
> deleted `role_permission`, an office holding all of `person.*` *is* the live grant rows naming `ROLE(x)`
> — one row per code, dated, attributable — so a bundle that mixes the dangerous two with routine editing
> is visible in a role editor instead of hidden in a resolver rule. **§11** carries the rule that follows:
> no seeded office mixes `person.merge` or `person.redact` with routine `person.edit`, and one that does
> should be named for what it is.

> **No `person.background_check.*`.** The organization has no background checks handled by this system, so
> there is nothing to view and nothing to record
> ([D-043](../decisions/round-02-03.md#d-043--no-background-checks-are-recorded-in-this-system)). If that
> changes, the permission pair and a dated record with an `expires_at` are the natural shape, and they
> belong here next to `person.*` — a clearance is a fact about a person, not about their membership.

### Descriptive data

Everything the system knows about a person other than their name, their gender and their age is one class
of data, in fields the organization defines while it runs
([../domain/08-person-data.md](../domain/08-person-data.md),
[../data-model/09-attributes.md](../data-model/09-attributes.md),
[D-083](../decisions/round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data),
[D-084](../decisions/round-07-08.md#d-084--descriptive-data-is-organization-defined-at-runtime)).
The catalog's whole involvement in that is one code added and none removed:

- **Read: `person.view`. Write: `person.edit`. That is the entire access story.** No code gates
  descriptive data separately, because there is nothing left for one to gate: a code separating, say, the
  allergy list from the rest of the record would reinstate the privileged subset
  [D-083](../decisions/round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)
  refused on the merits. There is therefore **no `health.*` or `medical.*` namespace and no per-field
  access rule** — `category` on a definition groups a form and grants nothing. If a narrower tier is ever
  genuinely needed, the route is a decision entry about a **second grant scope over a defined set of
  data**, not a code with a suggestive name.
- **`attribute.define` is the one code, and it is the narrow one**
  ([D-084](../decisions/round-07-08.md#d-084--descriptive-data-is-organization-defined-at-runtime)): it
  creates, renames, merges and retires a definition — deciding what the organization *collects*, which is
  what makes the data queryable. **Recording a value against a definition that does not exist is refused, and
  it creates nothing**: a value may not invent a code, so the vocabulary grows only by a save from a person
  holding this code, and it is live at that save
  ([D-141](../decisions/round-20.md#d-141--a-definition-is-live-at-the-save-the-proposal-stage-its-queue-and-its-check-are-deleted))
  — **the permission is the curator**, there being no queue left to hold a proposal and no office that would
  confer the reading of one
  ([D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)).
  Its sensitivity column
  stays empty because it reads nobody's data — the vocabulary is rows about codes, and the values
  underneath it are reached through `person.view` like anything else.
- **`person.view` carries ⚠⚠** because the marker grades what a grant *exposes*, and this one exposes
  everything known about a child — an allergy list, an insurance number, a note about who the child
  actually lives with.

`person.redact` reaches the layer too, and in the opposite direction from retiring a definition: retiring
one keeps the values, redacting a person erases theirs — in the audit trail as well as in the row, since a
trail that still reads out an erased value has preserved it rather than missed it
([../data-model/09-attributes.md §6](../data-model/09-attributes.md#6-erasure-retirement-and-the-audit-payload)).

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
> [D-089](../decisions/round-07-08.md#d-089--one-live-account-a-colliding-sign-up-files-a-claim-and-creates-nothing)).
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

> **Where the two roster questions are answered.** *"Who is in the organization?"* is `membership.view` —
> one query over `membership`, with no depth in it, because there is one unit. *"Who is in this group?"* and
> *"write that group's roster"* are `person_group.view` and `person_group.member.manage` (§5a,
> [D-098](../decisions/round-10a.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority)).
> There is nothing in between to transfer a member across either: moving a person from one group to another
> is `person_group.member.manage` — close one dated row, open another — and it does not touch their
> membership at all
> ([../data-model/02-organization.md §4](../data-model/02-organization.md#4-joins-leaves-and-transfers-close-one-row-open-another)).

> **`membership.terminate` is the most consequential non-system permission in the
> catalog.** A lapse is administrative; a termination is a decision about a person's
> standing in a youth organization, frequently with safeguarding and reputational
> consequences. It should be held by very few people, and it must not be implied by
> `membership.lapse`. Grant it explicitly, per person — which since
> [D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)
> is the only thing a grant *can* be: one code, one effect.

> **`person_group.member.manage` has no self-scoped variant and none will be added**
> ([D-095](../decisions/round-09.md#d-095--units-carry-no-restrictions-joining-one-is-somebody-elses-act),
> whose reasoning [D-098](../decisions/round-10a.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority)
> transfers intact). Every grant of it means *"over this group's roster"* or *"over every group's roster"*,
> never *"over my own row"* — so **"nobody writes themselves into a group"** is not a check the write
> performs, it is the shape of the thing being granted: there is no smaller grant to make yourself. The same
> holds for `role.assign` (§7): **nobody appoints themselves**, and D-095 was explicit that no code should
> exist that could express either act.
>
> **This is also where the safeguarding control lives.** No column anywhere says which sets are for
> children, so nothing refuses to place a minor in one. What is left is that this code is held by named
> adults at the unit, that the write is audited like any business-table write with its recorded values
> emptied after 24 months
> ([D-088](../decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)),
> and that there is a report of who holds it
> ([../domain/04-organization-structure.md §3](../domain/04-organization-structure.md#3-joining-a-group-is-somebody-elses-act)).
> What it gives up is worth naming: nobody collectively chooses the named adult, because there is no body
> to choose ([../domain/04-organization-structure.md §1](../domain/04-organization-structure.md#1-the-organization-is-one-unit-and-the-unit-is-a-scope)).
> A group has no fee, so unlike a *membership* there is no gate in front of it besides this permission
> ([../domain/05-membership-lifecycle.md §1](../domain/05-membership-lifecycle.md#1-the-flow-you-described)).

> **Nothing about a code says whether it requires a paid-up holder**, so this table has nothing to hide
> and nothing to warn about. **Where a grantee is a set, the grantee's expression performs the membership
> test:** it says `MEMBERS * ROLE(x)` when the fee is meant to matter and omits it when it is not,
> evaluated live on the checked date (§11,
> [../domain/06-authorization-model.md §6.1](../domain/06-authorization-model.md#61-members--the-membership-test-moved-into-the-expression)),
> which is where the gate went when [D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)
> deleted it along with the code that waived it. **The two grantees that are not sets carry no such test**:
> a grant written to one named person, or to one registered key (§8b,
> [D-116](../decisions/round-16.md#d-116--a-caller-that-is-not-a-person-is-a-registered-key-and-a-key-is-a-third-grantee-kind)),
> has no expression to evaluate, so the fee is nobody's question there and the grantee's own standing is
> the whole of what was chosen.

## 5. Organization and positions

**Nothing is granted here, because nothing described is left.** The six `org_unit.*` codes went with the
unit hierarchy
([D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)) and the
two `position.*` codes went with positions
([D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)).
Where each act is performed now is in
[removed-concepts.md](removed-concepts.md#the-codes-that-left-the-catalog), which is where a name from an
older draft is looked up. The heading stays so a reader arriving from an old bookmark finds the reason and
not an empty space.

**Two rulings outlived the codes they were written about, and they are why `role.assign` carries 🔒🔒.**

- **Nobody appoints themselves.** An appointment was made *to* a person by somebody else, was never
  self-scoped, and came with eligibility rules about the office rather than the appointment. Those columns
  are deleted with the table and none of them has a self-service form in the new model either:
  `role.assign` has no self-scoped grant (§7).
- **An appointment writes one row, and nothing derives authority from it.** The sentence existed to stop a
  leadership slot silently reaching people through a group's *filling rule*, which stopped covering the
  person on the day the assignment closed
  ([D-091](../decisions/round-09.md#d-091--a-permission-group-is-a-rule-and-a-list-at-once-and-a-rule-may-name-another-group)).
  Filling rules and positions are both gone, so the derivation is gone rather than relocated: a holder row
  is written by a named person under `role.assign`, and the only thing that turns it into authority is a
  grant naming `ROLE(x)`
  ([D-101](../decisions/round-10b.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree)).

*What is genuinely lost is elected-versus-appointed as stored data* (D-100), and **it stays lost by
decision**: [D-136](../decisions/round-19.md#d-136--an-election-is-not-recorded-a-role-holds-only-the-people) closed [F-18](../open-questions.md#f-18) with the ruling that a role holds only the
people who hold it. The distinction survives only as offices the organization invents — `elected_council`
beside `appointed_it` — or not at all
([../domain/04-organization-structure.md §6](../domain/04-organization-structure.md#6-appointments)).

## 5a. Groups, roles and audiences

Three small tables and their codes: **a group** (`person_group`, dated member rows, a lifetime) is company
([D-098](../decisions/round-10a.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority));
**a role** (`role`, `role_holder`) is an office, and confers nothing
([D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape));
**an audience** is an expression over named sets, and is what a grant aims at
([D-101](../decisions/round-10b.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree)).
Writing a group's roster and writing an office's holder list are **different codes on purpose** — that
difference is the whole reason there are two tables — and the office codes are in §7.

| Code | Namespace | Sens. | Grants |
|------|-----------|-------|--------|
| `person_group.view` | — | ⚠ | See which groups exist, their lifetimes, and **who is in them** — a roster is a list of people, which is what ⚠ grades |
| `person_group.create` | — | | Create a group: a name, a description, a lifetime. `applies_to = unit` |
| `person_group.edit` | — | | Change a group's name or description. A rename rewrites no grant (§5) |
| `person_group.end` | — | | Set the group's `valid_to`. It ends a **set**, not anyone's standing — hence no ⛔, deliberately |
| `person_group.member.manage` | — | ⚠ | **Add, move or end a member.** Never self-scoped (§4); `applies_to = unit_and_item` |
| `audience.view` | — | | See the expressions a grant can be aimed at, and **the people each one resolves to** |
| `audience.manage` | — | ⚠ | Create an audience; change its expression — **which is the whole of it**: a hand-named person is a `PERSON(x)` leaf inside that expression, so there is no second object to edit ([D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)) |

> **There is no code for crossing between units, because there are no units to cross.** *May the center
> read what happens inside a body it does not run?* is not a question this model declines to answer; it
> cannot be asked, and [../domain/06-authorization-model.md §2](../domain/06-authorization-model.md#2-scopes--the-unit-and-the-item)
> is where that is worked through. The names — `scope.expose`, `scope.exposure.review`,
> `scope_exposure` — are in [removed-concepts.md](removed-concepts.md), with the rule they enforced.

> **`person_group.member.manage` is a ⚠ next to a 🔒🔒 two rows away, and the gap is the design.**
> [D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)
> refuses to merge `person_group` and `role` into one table with a `kind` column precisely because one
> membership table gives a single code that both adds a child to the Thursday group **and** puts the
> holder into `SYSTEM_ADMINS`. Same columns, different codes, and `GROUP(x)` / `ROLE(x)` distinct in
> the grant text so the difference is visible to whoever reads the grant. **A group additionally
> authorizes nothing by existing**: no parent, no type, no leadership, no roles of its own, no fee —
> a member of a group can *do* nothing, which is
> [D-005](../decisions/round-01a.md#d-005--permissions-are-grants-never-derived-from-identity) one
> level down ([../domain/04-organization-structure.md §2](../domain/04-organization-structure.md#2-what-a-group-is-and-everything-a-group-is-not)).

> **A group and a role are both *items*, which is what makes "these two may work this roster" a
> grant.** Both are registered in `grant_scope_type`, so the code above can be held at the unit —
> reaching **every** group, existing and future, because nothing stands between a unit grant and an
> item after D-097 — or written on one group, reaching that roster only
> ([../data-model/02-organization.md §3](../data-model/02-organization.md#3-a-group-is-an-item-a-grant-can-be-written-on-one)).
> Reaching the second requires the first: a grant on an item is written by someone who holds the code
> at the unit, or holds a grant on that item.
>
> A **live grant whose group has ended** is a listed oddity rather than a failure: it applies to
> nobody, which is the safe direction, and the report of such rows is where the stale one surfaces
> ([../data-model/02-organization.md §6](../data-model/02-organization.md#6-integrity-checks)).

> **`audience.manage` is the permission that creates a grant target, and it is wider than it was.**
> Whoever holds it can assemble a set of people which a later `access_grant` may then address
> ([D-042](../decisions/round-02-03.md#d-042--grants-may-target-audiences-not-only-individuals)) —
> authority over *who could be granted*, one step removed from granting. Whether it belongs to a
> dedicated office or to whoever runs things is open (§12).
>
> **One code over a whole expression, and the hazard moved with it.** An audience is a tree of `+ - *`,
> composition happens in the grant (`GROUP(kitchen) + ROLE(troop_staff)`), and a tree cannot cycle, so
> widening is always a named act in a row somebody wrote. The silent version was `audience_include`:
> *"add the kitchen crew to everything the troop-staff group is used for"* widened every grant aimed at
> anything including it, through an edge nobody could see the shape of. It went with its depth cap, its
> transitive walk and its write-time cycle check in
> [D-101](../decisions/round-10b.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree).
> What
> did **not** get smaller: `EVERYONE` is a legal operand, so nothing in this table distinguishes
> *"add these five people"* from *"this grant reaches the whole organization"*, and no separate code
> was invented to do it. That stays an open question, not an answer (§12), and until it is answered
> the only control is the one D-091 named and D-102 sharpened: **the editor shows the people a grant
> reaches, expanded, computed for an item, rather than the expression's name**
> ([../domain/06a-audiences-and-selectors.md §6.2](../domain/06a-audiences-and-selectors.md#62-audiences--an-expression-over-named-sets)).
>
> **The display is itself a read over people, and this catalog does not grade that yet.** Showing a
> resolved set means enumerating which humans an expression currently covers — which is what
> `audience.view` is for, on a row carrying no sensitivity mark. Listing the holders of
> *"everyone except the counselors in `schuzka2026-1`"* is not the same kind of act as listing the
> kitchen crew, and the grading was written before the two could be one query (§12).

---

## 6. Guardianship

| Code | Namespace | Sens. | Grants |
|------|-----------|-------|--------|
| `guardianship.view` | — | ⚠⚠ | See guardianship relationships |
| `guardianship.create` | — | ⚠⚠ | Record a guardianship |
| `guardianship.end` | — | ⚠⚠ | End a guardianship |
| `guardianship.assign` | — | ⚠⚠ | Add another guardian over the same dependent |
| `guardianship.change_right` | — | 🔒 | Change a guardianship's `right_level` |

> **These are the only codes in the catalog that a private individual holds over their own household
> without being granted them.** [D-073](../decisions/round-06.md#d-073--guardianship-is-administered-by-its-own-parties-not-by-staff)
> makes the parties to a guardianship principals on the row: a guardian may end it, add another
> guardian, and change its level; the adult subject may end it over themselves. Staff hold the same
> codes and are **an** route, never **the** route.
>
> **A guardian's rights are one value with three choices, never a list of codes.**
> `guardianship.change_right` sets `right_level`, and there is nothing else to grant: the per-capability
> `dependent.*` namespace such a grant would have drawn from was refused on the merits
> ([D-074](../decisions/round-06.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular)).
>
> **What the three choices are compared against is a column, not a ladder:**
> `permission.right_kind ∈ read | write`, where `none` covers nothing, `view` covers the `read` codes,
> and `write` covers both. **That is the column's only customer in the whole system** (§1), and it is why
> a code added to this catalog has to be typed `read` or `write` at all: the column is required, because a
> nullable one whose null-ness silently means something would let a permission arrive with a guardian's
> answer already decided by nobody. Nothing else could have used this comparison — since
> [D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)
> a grant carries no level to compare a code against.
>
> **Required, agreeing with nothing, checked by nothing: `right_kind` is a note, and it stays required.**
> Nothing in the schema or the write path asks whether a code typed `read` really is one, and no report counts
> the codes where the two disagree — so **a `right_kind` can contradict its code forever, and only a reader
> will notice** ([D-144](../decisions/round-20.md#d-144--right_kind-is-a-note-required-by-the-schema-checked-against-nothing-and-no-longer-claiming-to-be-checked)).
> **That is what the column is for.** A code whose declared kind reads oddly next to its name is worth noticing
> *while reading a catalog*, which is what this page is; the alternative was a validation rule that would have
> had to hold, somewhere, a second list of which codes are reads — a copy of this column in prose, and the one
> defect this corpus keeps hitting is a copy that drifted. Every marking in the tables below is therefore an
> author's statement, filled in because the column cannot be left empty.

## 7. Permissions administration

| Code | Namespace | Sens. | Grants |
|------|-----------|-------|--------|
| `role.view` | `system` | | See the offices that exist and **who has held them, over what period** (`role_holder`) |
| `role.create` | `system` | 🔒🔒 | Create an office: a code, a name, a description. It carries no permission — see the note below |
| `role.edit` | `system` | 🔒🔒 | Change an office's name or description |
| `role.delete` | `system` | 🔒🔒 | Delete an office. Only possible if it was **never held** and is not a system role |
| `role.assign` | `system` | 🔒🔒 | **Write a `role_holder` row** — make someone a holder. `applies_to = unit_and_item`: on one role, this is "manage the counselors roster" |
| `role.unassign` | `system` | 🔒 | Close a `role_holder` row — set its `valid_to` |
| `permission.view` | `system` | | See the permission catalog |
| `permission.edit` | `system` | 🔒🔒 | Change the permission catalog |
| `access_grant.create` | — | ⚠ | Create a grant — the act that turns a code into someone's authority |
| `access_grant.revoke` | — | ⚠ | End a grant early, or write a `deny` |
| `system.admin` | `system` | 🔒🔒 | **Everything.** Single top-level capability, `applies_to = unit`. **Never grantable to a registered key** (§8b) |

> **A role confers nothing**, and that is the sentence to read before this table. **The codes an office
> carries are the live grants whose expression names `ROLE(x)`**
> ([D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape),
> [../domain/06-authorization-model.md §4](../domain/06-authorization-model.md#4-roles-are-offices-groups-are-company)).
> What `role.create` and `role.edit` touch is a **name, a description, an order** — an office is a set
> with a label, and a set is not a grant
> ([D-005](../decisions/round-01a.md#d-005--permissions-are-grants-never-derived-from-identity)).
> What `role.view` shows is the **holder register**, the one question this part of the catalog answers:
> *who was treasurer in 2023?*

> **`role.assign` is the permission to escalate privilege.** Whoever holds it can write themselves a
> holder row in an office that grants them `system.admin`. It must be held by very few people and
> every holder row must be logged and alerted on. Note that `system.admin` is deliberately a **single
> top-level permission** rather than a per-resource one — concentrating the most dangerous capability
> and alarming on its holders is safer than scattering equivalents of it. **`role.assign` has no
> self-scoped form and none will be added** (§4,
> [D-095](../decisions/round-09.md#d-095--units-carry-no-restrictions-joining-one-is-somebody-elses-act)):
> the reason it is not a check the write performs is that there is no smaller grant to make yourself.

> **Roles are runtime data, and these six permissions are how the organization administers them.**
> `role.create` names a new office; `role.edit` renames one; `role.delete` removes one created by
> mistake; the reach of any of them is written by `access_grant.create` down the table. §11 is
> therefore a *starting point to be edited*, not a fixed vocabulary. Whether an office's authority is
> conditional on a paid-up holder is not configuration either: it is in the text of each grant, which
> says `MEMBERS * ROLE(x)` when the fee is meant to matter.

> **There is no `role.retire`, and a role cannot be switched off**
> ([D-053](../decisions/round-04.md#d-053--a-role-is-valid-always-only-its-assignment-is-temporal)).
> A role is a definition and is valid always; the period lives on the **holder row**. Ending a role's
> use means closing holder rows, which is `role.unassign` — one person at a time, or a loop over the
> holders. The shape is deliberate: what ends is *someone's authority*, a fact about a person and not
> about a definition. **Nothing here expires on its own.** No dormant authority quietly lapses when a
> holder's fee runs out, so the report of holder rows that never end
> ([D-071](../decisions/round-05.md#d-071--nothing-forces-a-role-assignment-to-end-the-gate-and-the-report-are-the-control),
> whose posture transfers from assignments to holder rows) is carrying all of the weight.

> **The bulk privilege change is a grant, not a role edit.** A role carries no permissions, so
> `role.edit` changes a label; what escalates **everyone holding `x`**, immediately, without
> touching a holder row and without notifying anybody, is saving a grant aimed at `ROLE(x)`. That is
> `access_grant.create` with an expression in it, and it is exactly why `role.*` stays 🔒🔒 while the
> composition of grants is the least-graded write in the catalog (§12). Escalating one person and
> escalating an office are different powers, and neither is implied by the other.

> **`role.delete` only works on an office that has never been held** and is not `is_system` — which is
> what protects the one seeded role, `counselors`, from an editor (§11). No delete may leave a
> `role_holder` pointing at a role that is gone:
> [../data-model/05-authorization.md §3](../data-model/05-authorization.md#3-role--an-office)
> states the guard and the order it refuses in. The two halves are not equally strong, and the
> difference is the reason this permission is not self-policing. The first is referential
> integrity — `role_holder.role_id` references `role.id`, a migration-level constraint, so it refuses
> a delete that arrives from an import, from a manual fix, or from a second client as surely as from
> the screens. The second, `is_system`, is a property of the row being deleted and no index can see
> it: it is a check inside the transaction that deletes, and a model-layer guard there is a friendlier
> message, not the refusal. A role that has been held is left in place, so the answer to "what office
> did this person hold in 2019?" survives — which is precisely when someone asks it.
>
> **Nothing waives the membership test, because nothing imposes it.** The resolver asks no membership
> question of a grant, so there is no exemption for a person to hold: the test is the **expression the
> grant was written with** — `MEMBERS * ROLE(x)` where the fee must hold, `ROLE(x)` where it need not,
> and `(MEMBERS * ROLE(x)) + PERSON(y)` when one named person is to survive their own lapse (§11,
> [../domain/06-authorization-model.md §6.1](../domain/06-authorization-model.md#61-members--the-membership-test-moved-into-the-expression)).
> The waiver code, the role flag that waived a whole office, and the resolver function that read them
> are in [removed-concepts.md](removed-concepts.md).
>
> **`access_grant.create` carries no ceiling, and nothing here pretends otherwise.** What bounds a
> grantor is the shape of the grant and nothing else: one code, `applies_to` refusing it on an item it
> does not fit, a scope that is the item the grant names or the unit, `MEMBERS` as the writer's own act.
> The test that an authority may not exceed its holder's is written only for delegations
> ([../domain/06-authorization-model.md §9](../domain/06-authorization-model.md#9-delegation)), so
> **a holder of `access_grant.create` can grant `system.admin` to anyone, including themselves.** That
> is recorded as an open question rather than as a rule this catalog holds, and §12 is where it lives.

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

> **`audit.view` is graded ⚠⚠ because the trail is a second copy of the person record.** `audit_log`
> carries the before and after images of what changed, descriptive values included, on the same terms
> as a `person_contact` row or a note change. So reading the trail over a scope **is** reading person
> data over that scope, and reading *more* than `person.view` shows: the current row is the
> organization's present belief, the trail is every belief it has held. Nothing filters which fields
> that applies to — a rule naming the person fields whose values may not be logged would be a
> privileged *subset* of the record, which is what
> [D-083](../decisions/round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)
> refused, and it would hollow out
> [D-085](../decisions/round-07-08.md#d-085--the-identity-machinery-stays-structured-the-boundary-is-rules-not-sensitivity),
> whose justification for overwriting a value in place is that the trail holds the sequence. What
> protects the trail is the guard on it — scope, this mark, and who holds it — exactly as the guard on
> `person.view` protects the record. *Why: the mark follows what a grant exposes, not the table a code
> names — [D-086](../decisions/round-07-08.md#d-086--a-sensitivity-mark-grades-what-a-grant-exposes-not-the-table-it-reads).*
>
> **And this one code is the whole gate, with no per-entry filter behind it — now decided rather than merely
> unbuilt.** [06 §2.3](../data-model/06-audit-and-import.md#23-history-query) records the per-entry check as
> considered and left unimplemented, and
> [D-138](../decisions/round-20.md#d-138--one-permission-guards-the-whole-audit-trail-and-the-widening-is-on-the-record)
> is the decision that says so: what an officer can read about 2019 does not depend on an expression changed
> last week, which is the legibility the trail exists to provide. The widening above is therefore a
> **stated property of one grant** and not a bug waiting for a filter — which is also what makes ⚠⚠ and the
> question of who holds this code the whole of the control.

> **The contents expire, which bounds that exposure without removing it.** A row lives for the life of
> the system; its `old_values`/`new_values` are emptied **24 months after they were written**, by a
> scheduled job this corpus calls **payload reduction** — a third operation on the trail, distinct
> from redaction (a person's erasure, immediate and absolute, whatever the age of the row) and from an
> import revert ([D-088](../decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)).
> *"Every belief it has held"* is therefore true only of values less than two years old; about anything
> older the trail answers *who touched this row, when, and were they allowed to* and not *and to what*.
> It puts a horizon under the risk rather than making it impossible. **AT-4 stays open**, because a
> window on the payload is an argument about how *long* a bad grant can do harm, not an answer to
> whether one permission should guard the trail.
>
> **Payload reduction needs no code here, and saying so is the check that it was considered.** Nobody
> performs it interactively: it is scheduled, and the guard on it is a check that alerts when a row
> past the window still carries a payload
> ([../data-model/06-audit-and-import.md §2.2](../data-model/06-audit-and-import.md#22-redaction-before-logging)).
> A permission for it would imply a person choosing not to run it.
>
> **The excluded-keys list has one job: values that must never be logged at all.** Credential secrets,
> tokens, session material. Personal data is not on it, because personal data is protected by who may
> read the table, not by a list of its names.
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
> **One permission is the guard, and that is now decided rather than open**: `audit.view` is the whole gate,
> with no per-entry filter behind it
> ([D-138](../decisions/round-20.md#d-138--one-permission-guards-the-whole-audit-trail-and-the-widening-is-on-the-record),
> answering **AT-4** ([../open-questions.md](../open-questions.md#at-4))). The grading above is what the
> decision rests on: the trail is read with the guard of person data, and the widening that comes with one code
> over a second copy of the record is written here as a property rather than left to be discovered. **What the
> decision spends is exactly what it names:** a history screen over the trail is a person-data surface, so
> ⚠⚠ and the question of who holds this code are the whole of the control, and a grant to a wider audience
> widens reading about every year at once.

## 8a. Events

An event is **an item like any other** ([D-102](../decisions/round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)).
**Nothing owns an event** — there is no owner column and no unit-authority shortcut — so a grant at the
unit reaches every event because there is no tier between the unit and the item and no owner to test,
and **every event check goes through the ordinary resolver and nothing else.** **Registration is
eligibility**: a live allow of `event.register_self` *is* the rule for who may sign up, and there is no
separate eligibility mechanism
([D-060](../decisions/round-05.md#d-060--eligibility-is-capability-there-is-no-separate-rule-engine)).
**And there is no door code.** Nothing in this catalog grants a gate-crashing capability, and none was
ever registered here or on any other page (§12,
[D-104](../decisions/round-10b.md#d-104--a-permission-codes-last-segment-is-an-action-and-a-registry-that-prose-contradicts-is-a-fiction));
arriving people are recorded by whoever holds `event.presence.mark`, with a clipboard if necessary, and
[D-075](../decisions/round-06.md#d-075--money-arrives-from-a-bank-api-a-payment-is-requested-by-variable-symbol-and-qr-code)
keeps the only QR code in this system attached to a payment, where it is a rendering and not a row.

| Code | Namespace | Sens. | Grants |
|------|-----------|-------|--------|
| `event.view` | — | | See an event |
| `event.create` | — | | Create an event. **Held at the unit** — nothing owns an event, so there is no one to create one *for* |
| `event.edit` | — | | Change an event's details, dates, capacity |
| `event.cancel` | — | ⚠ | **Cancel an event** — keeps registrations, notifies nobody by itself |
| `event.organizer.manage` | — | ⚠ | Add or remove organizers — a **roster write**, which aims `ORGANIZERS` at more people and so widens every grant pointed at that set |
| `event.register_self` | — | | **Register yourself** — this is the eligibility rule |
| `event.register_other` | — | ⚠ | Register someone else (a minor, a walk-in) |
| `event.manage_participants` | — | ⚠ | **Manage the roster** — add or remove registrations, work the waitlist, promote |
| `event.presence.mark` | — | ⚠ | **Mark who turned up** — nothing else, and never a set anyone is granted over (§1) |
| `event.answer.view` | — | ⚠⚠ | **Read registrant answers** (tent, dietary, …) — the note below, and the seeded grant |
| `event.question.manage` | — | ⚠ | Define what the event asks |
| `event.grant_access` | — | 🔒 | Grant access to an event. What distinguishes it from `access_grant.create` is the scope alone, which is why §12 asks whether it is still a code with a subject |
| `event.delete` | — | 🔒 | Delete an event — only possible with **no** registrations |

**Where each of these may be granted, and what kind of right it is** (§1) — nothing else rides on top:

| Code | `applies_to` | `right_kind` |
|---|---|---|
| `event.create` | `unit` | `write` |
| `event.view`, `event.answer.view` | `unit_and_item` | `read` |
| every other `event.*` code | `unit_and_item` | `write` |

**At the unit a code reaches every event; on one event it reaches that event; nothing rides on top of
either.** The `read` rows are `read` because a guardian's `view` is meant to reach them (§6) — which is
the only reason the column exists. *Why: a grant allows or denies one permission and carries no level —
[D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality).*

> **The five sets bound to an event are grantees, not codes.** `ATTENDED`, `PLACED`, `CONFIRMED`,
> `ON_WAITLIST` and `ORGANIZERS` name the people connected to the item a grant is written on, and they
> belong to the audience language, not to this catalog: **an operand is a set, and a set is not a
> grant**
> ([D-062](../decisions/round-05.md#d-062--organizers-are-appointed-on-the-event-not-granted)
> survives untouched — *an `event_organizer` row grants nothing*). Two refusals come with them and both
> land when the grant is saved: a **bound** (argument-less) operand is legal only on an item-scope
> grant, and only where `selector_type.argument_type` matches the item — `PLACED` on a group grant is
> refused because that item is not an event. And `PRESENT(<event>)` is refused outright (§1).
> **A grantee is not always one of these sets**, and the other two kinds are named rather than implied: a
> grant written to one named person, or to one registered key (§8b), has no operand in it and no set behind
> it, because no selector names a key and a key is in nobody's set — including the set of every person
> ([D-117](../decisions/round-16.md#d-117--a-key-is-never-inside-an-expression-thirteen-selectors-and-none-of-them-can-name-one)).
> The definitions, and the reason `PLACED` rather than `ATTENDED` is the capacity set, are in
> [../data-model/08a-event-guards-and-checks.md §8](../data-model/08a-event-guards-and-checks.md#selectors-that-bind-to-an-event).

> **`event.presence.mark` is split off `event.manage_participants` on purpose.** Marking presence is a
> task handed to whoever is at the door with a clipboard; managing the roster is a task for the event's
> leadership. One permission covering both forces the organization to hand the clipboard-holder the
> ability to delete a child from the camp roster. Splitting it costs two rows and makes the ordinary
> delegation ordinary, and the distinction is written as the only thing a grant can say: one code, so
> granting `event.presence.mark` on an event cannot smuggle in `event.manage_participants`. *Why: it
> follows `membership.lapse` versus `membership.terminate` — one routine, one consequential
> ([D-022](../decisions/round-01b.md#d-022--lapsing-and-termination-are-different-permissions)) — and
> adding a row is free because the catalog is a menu, not a fixed set
> ([D-055](../decisions/round-04.md#d-055--the-permission-catalog-is-deliberately-comprehensive-and-granular)).
> [EV-5](../open-questions.md#ev-5) asked whether the split was needed; the split is the answer, and the
> rung it originally came with is
> [D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)'s.*

> **`event.register_self` is the whole of
> [D-060](../decisions/round-05.md#d-060--eligibility-is-capability-there-is-no-separate-rule-engine).**
> Opening an event to the membership is **one row**: an `access_grant` scoped to that event, of
> `event.register_self`, aimed at `MEMBERS`. One row is the point — nobody is enumerated, so nobody is
> left out when the roster changes, and nothing has to be re-run when someone joins. The row says exactly
> one thing, which is the eligibility, and says nothing about anyone else's task.
>
> An age-restricted camp is a **narrower expression** instead — `MEMBERS * GROUP(camp_2026_junior)`
> aimed at the same one code, or the same subtraction pattern read the other way. **There is no age
> rule on the event and there will not be one** — an open event with an age ceiling is accepted as a
> risk, on the grounds that a registration-time condition the capability model does not know about is
> the first rule-engine rule
> ([D-070](../decisions/round-05.md#d-070--an-event-has-no-age-ceiling-the-grant-is-the-rule)).
> If it ever needs closing, the shape is a new **selector** in the `selector_type` registry, not a
> column
> ([../domain/07-events.md §4](../domain/07-events.md#an-age-rule-is-an-audience-not-a-rule)) —
> and note that `GROUP(...)` is a set somebody maintains, so *"who is eligible"* stays a roster with a
> person's name on every row rather than a predicate the resolver evaluates.

> **`event.cancel` is separated from `event.edit` deliberately.** Cancelling is the most
> consequential thing anyone does to an event: it affects every registrant, it usually
> involves money, and it is a decision rather than an edit. It does not notify anyone — that
> is the communication module's job, and conflating the two makes "who cancelled this, and
> when?" harder to answer than it should be.

> **`event.delete` is on this list and nothing else has an equivalent, because events are the
> one thing in this data model that can be deleted.** A draft event with no
> registrations is a mistake to be cleaned up; anything else is cancelled, not deleted
> ([D-064](../decisions/round-05.md#d-064--there-is-no-event-status-visibility-is-the-permission-model)).
> **No event with even one registration row may be deleted** — Guard 2 in
> [../data-model/08a-event-guards-and-checks.md §8](../data-model/08a-event-guards-and-checks.md#guards) is the rule, and cancelling
> is what to do instead. The obligation is not the permission's to carry: `event.delete` decides
> who may ask, and only a migration-level constraint — `event_registration.event_id` referencing
> `event.id` with no cascade — refuses the same delete when it arrives from an import or a
> hand-written fix instead of a screen. Enforcing this in the model layer alone would leave the
> record of who was coming deletable by everything except the intended route.

> **`event.answer.view` is where
> [D-061](../decisions/round-05.md#d-061--event-answers-are-read-by-that-events-organizers) lives, and it
> lives there as a grant.** *"Answers are read by that event's organizers"* is said where permissions are
> said: **a seeded grant of `event.answer.view`, scoped to the event, aimed at `ORGANIZERS`**
> ([D-102](../decisions/round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)).
> Because a bound operand is legal only on an item-scope grant, this cannot be one row for every event:
> what ships is a **template**, which the event-creation path instantiates beside the event row in the
> same transaction as the event, and which the import owes one instantiation per event it writes
> ([../data-model/08a-event-guards-and-checks.md §8](../data-model/08a-event-guards-and-checks.md#selectors-that-bind-to-an-event)).
> What is open is the safety net rather than the rule: an event whose two writes were not one
> transaction has no organizer who can read its answers, and "these two rows exist together" is a
> report — *events with no answer-view grant* — that no layer of this project can express as a
> constraint ([shape 3](../data-model/00a-invariant-register.md#3-the-answer-reads-another-table-a-resolver-or-a-graph)).
>
> **Whoever runs an event reads that event's answers with no additional gate.** Holding an office grants
> nothing (§7), and leadership is not guardianship: guardianship authority belongs to the guardians (§9)
> and is not reachable by leading an event. *Why: D-061 names this a widening and records it as one — the
> parent tells the people who are present, per event.* The catalog's registered spelling is
> **`event.answer.view`**, singular, and §12 says what it means for a code to be a row rather than prose
> ([F-19](../open-questions.md#f-19)).
>
> **The form is the fallback for a fact the organization has not recorded, not the ceiling on what an
> organizer may know.** Descriptive data exists
> ([../domain/08-person-data.md](../domain/08-person-data.md)), and a leader holding `person.view` over
> that unit reads a recorded allergy there. *Why: D-061 was written when the form was the only readable
> route to such a fact — the narrowing is
> [D-085](../decisions/round-07-08.md#d-085--the-identity-machinery-stays-structured-the-boundary-is-rules-not-sensitivity)'s,
> and the decision it narrows stands.*
>
> **This code is graded ⚠⚠ because the answers are person data.** A tent size and an adrenaline-pen
> answer live in the same payload, and
> [D-083](../decisions/round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)
> refuses a class of data more delicate than the rest, so the payload is graded as what it exposes
> rather than as the logistics category it is filed under — the same rule §8 applies to `audit.view`
> ([D-086](../decisions/round-07-08.md#d-086--a-sensitivity-mark-grades-what-a-grant-exposes-not-the-table-it-reads)).
> **The grading narrows nothing:** organizers still read with no additional gate; what the mark changes
> is what a reviewer notices before ticking the box on a grant that reaches thirty volunteers.
>
> **Only preference-level detail belongs on a form, and that is guidance on a label, not a guard.** No
> layer enforces it and none can: nothing distinguishes "vegetarian" from "carries an adrenaline pen" to
> a database
> ([../data-model/08-events.md §7](../data-model/08-events.md#health-facts-and-the-discipline-this-requires)).
> It rests entirely on whoever writes the form.

## 8b. Keys — a caller that is nobody

**A registered key is the third thing a permission is held *by*.** An integration that calls this
system over its API is one row in `api_key`, installed by a named person, holding one secret that is
shown once and kept only as a hash — and it is a **grantee**, in the same sense a person is, reached
through the same single grant channel and no other
([D-116](../decisions/round-16.md#d-116--a-caller-that-is-not-a-person-is-a-registered-key-and-a-key-is-a-third-grantee-kind)).
It is not an account, which is a way for a person to log in, and it is not a selector: **no expression
names a key**, so a key holds the grants that name it and nothing besides
([D-117](../decisions/round-16.md#d-117--a-key-is-never-inside-an-expression-thirteen-selectors-and-none-of-them-can-name-one)).
The table itself, what its secret may and may not do, and the resolver entry point a call is checked
through are in [../data-model/05e-keys-and-callers.md](../data-model/05e-keys-and-callers.md); what
the catalog owes is four rows, typed.

| Code | Namespace | Sens. | Grants |
|------|-----------|-------|--------|
| `api_key.view` | — | | Which keys exist, what each of them is granted, and when each was last used |
| `api_key.create` | — | 🔒 | Register a key — mints its secret and shows it once, and never again |
| `api_key.rotate` | — | 🔒 | Replace a live key's secret, showing the new one once — **no window in which both secrets work** |
| `api_key.end` | — | 🔒 | Set a key's `valid_to`, or revoke it now with a reason |

**Where each of these may be granted, and what kind of right it is** (§1) — nothing else rides on top:

| Code | `applies_to` | `right_kind` |
|---|---|---|
| `api_key.view` | `unit` | `read` |
| `api_key.create`, `api_key.rotate`, `api_key.end` | `unit` | `write` |

**The marking changes no answer, and is filled in because the column is required.** `right_kind` has
one customer, the guardianship channel (§6), and that channel asks about one child's record — while
these four codes live at the unit
([../data-model/05-authorization.md §2](../data-model/05-authorization.md#right_kind-a-column-with-exactly-one-customer)).
`api_key.view` is `read` because it is the read of a list, and the three writes are `write` because
each lets its bearer install or unmake a caller. **`api_key.view` carries no sensitivity mark**, on the
precedent of `role.view` and `permission.view` two sections away: reading the register of integrations
exposes nobody's personal data, and the secret the row holds never leaves the row — not on this screen,
not in an export, not in a log line. *Why the mark follows what a grant exposes and not the table a
code names:
[D-086](../decisions/round-07-08.md#d-086--a-sensitivity-mark-grades-what-a-grant-exposes-not-the-table-it-reads).*

> **None of these four is `system.*`, and that is a difference rather than a spelling.** The `system`
> namespace holds the codes that administer *this system's own machinery* — the catalog, the offices,
> the grant rows (§7) — and it is the one place where the rule that `permission.resource` equals the
> code's first segment is waived: in a `system.` code those two disagree on purpose
> ([../data-model/05-authorization.md §2](../data-model/05-authorization.md#2-permission)). These four
> act on a table that exists, exactly as `event.*` and `person_group.*` do, so the first segment
> already *is* the resource and a prefix would be a second, drifting copy of a name the code carries.
> **And a prefix would buy nothing**, because a namespace routes nothing: the resolver stopped
> branching on the prefix, and
> [D-124](../decisions/round-16.md#d-124--two-defects-systemadmin-satisfies-every-code-and-one-prose-code-named-no-row)
> deleted the last reading under which one routed something. The unit-only reach is carried by
> `applies_to` above, where the save checks it; what a reader needs is the 🔒. The precedent is in §7
> and is stronger than anything here: `access_grant.create`, the act that turns a code into somebody's
> authority, carries **no** namespace at all.

> **What a key may never be granted is five named codes, not a set derived by rule: `system.admin` and
> the four above.** The grant is refused when it is saved
> ([../data-model/05-authorization.md §6](../data-model/05-authorization.md#what-is-refused-when-a-grant-is-saved)),
> and **integrity check 20 is the entire net**, because no database rule spans `permission` and
> `access_grant`
> ([D-122](../decisions/round-16.md#d-122--what-a-key-owes-the-catalog-four-codes-at-the-unit-and-the-fourth-owed-thing-declined)).
> One sentence covers both halves — **a key may not change what a key can do, and may not become
> everything.** A bearer secret holding *everything* is the whole organization in a request header; a
> key holding `api_key.create` mints its own replacements, so rotating a stolen key means looking for
> the rows a thief installed rather than the rows a person installed. Like check 17's `.admin`
> assertion this is **an equality against named rows**, and not `*.api_key` and not "any code about
> keys": an allow-list is where a wildcard comes back to life, which is exactly why the refused set is
> spelled out code by code.
>
> **No seeded office holds any of the four**, and none should: whoever holds `system.admin` already
> satisfies every one of these checks, because `system.admin` satisfies every code
> ([D-124](../decisions/round-16.md#d-124--two-defects-systemadmin-satisfies-every-code-and-one-prose-code-named-no-row)).
> **The capability to install a permanent outside authority is the capability to escalate**, and the
> 🔒 on the three writes is that sentence — it arrives through `access_grant.create` like every other
> code, so there is no second route to it and no seeded office that quietly holds it. The fourth thing
> a new resource owes this catalog, a row in `grant_scope_type`, is **declined for a key on purpose**
> ([D-122](../decisions/round-16.md#d-122--what-a-key-owes-the-catalog-four-codes-at-the-unit-and-the-fourth-owed-thing-declined)):
> a key is not a grantable item, so none of these codes can be written *on* one and **"rotate the
> accounting key and no other" is not writable** — anyone who may issue a key may issue any key. That
> is accepted at this scale, and it is recorded here as an unpaid debt rather than as a design feature.

> **A key's authority is its grants, in full and only.** Two of the three channels of authority compare
> a person against a row — ownership and guardianship — and for a key neither is refused by a fresh
> rule so much as unreachable, because there is no person for either to compare
> ([D-118](../decisions/round-16.md#d-118--the-two-channels-that-compare-people-cannot-fire-for-a-key-and-a-deny-on-a-person-does-not-slow-a-key-down)).
> The consequence worth reading twice: **a deny written against the person who installed a key does
> not touch the key.** Deny is absolute, but it defeats the allows of the grantee it names, and these
> are two grantees. What covers that is a list rather than a guard: the **Unusual section of the tab on
> the permissions page** lists live keys beside people, with what each holds, when it was last used and
> whether its contact still has an account, so a review reads one grant list and not two
> ([D-109](../decisions/round-13.md#d-109--nothing-a-rule-names-is-deleted-deprecated-hidden-disabled--and-a-tab-instead-of-a-report),
> [D-120](../decisions/round-16.md#d-120--a-key-outlives-whoever-created-it-and-the-report-is-the-control)).
> **A grant to a key is never a delegation**, on the reasoning that already refuses it for an audience:
> lending is one person's act towards another, and there is no person here to lend
> ([D-116](../decisions/round-16.md#d-116--a-caller-that-is-not-a-person-is-a-registered-key-and-a-key-is-a-third-grantee-kind)).

**§1's naming rules hold here with no exception taken:** every last segment is an act, and the first
segment names stored state — a table that now exists. **`rotate` is a last segment this corpus has
deleted before**, as `event.qr.rotate` in [removed-concepts.md](removed-concepts.md) — a code that never
existed in any registry and was deleted for being prose only
([D-104](../decisions/round-10b.md#d-104--a-permission-codes-last-segment-is-an-action-and-a-registry-that-prose-contradicts-is-a-fiction)).
These rows are not its revival. The lesson of that deletion is *a name must have a row behind it*, and
here the row exists before the prose does
([D-122](../decisions/round-16.md#d-122--what-a-key-owes-the-catalog-four-codes-at-the-unit-and-the-fourth-owed-thing-declined)).
