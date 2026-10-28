# Information System — Design Documentation

Design documentation for the organization's information system: people, accounts,
membership over time, organizational structure, and permissions.

> **Status:** draft, actively being specified. Nothing here is frozen.
> See [decisions/decision-log.md](decisions/decision-log.md) for what is settled and
> [open-questions.md](open-questions.md) for what is not.

---

## The one idea this whole design rests on

**A person is not a type. A person is a person.**

Nothing about being a child, an adult, a counselor, a parent, or a member is a
property of a human being. Each of those is either

- an **event or period** — membership, guardianship, holding an office, being in a group; or
- a **derived** fact — "child" means "a person whose recorded birth date makes them a minor *today*",
  "parent" means "is one side of an active `guardianship` row".

**There is no membership of type `child`, and there never was more than one membership type at all**
([D-037](decisions/decision-log.md#d-037--exactly-one-membership-type-the-fee-is-flat-and-per-person)),
and membership is **ageless** — no floor, no ceiling, no age-out, no child→adult transition
([D-038](decisions/decision-log.md#d-038--membership-is-ageless)). This list used to define "child" as
*an open membership of type `child`*, which was wrong twice over: it named a type that does not exist and
it made an age into an enrollment. Age is a fact about the person, and it matters where the law says it
matters — guardianship, and whatever rule an organizer writes for one event — never in the
membership row, and **no longer in anything an organization unit carries**: `org_unit_type.allows_minors`
went with D-095 and the unit itself went with
[D-097](decisions/decision-log.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row), so **no
column anywhere says which bodies are for children** — the control that replaced the flag is that a named
adult holds the write, and nobody joins anything themself
([D-095](decisions/decision-log.md#d-095--units-carry-no-restrictions-joining-one-is-somebody-elses-act)).

This matters because of a case you named explicitly: someone who was a member from
September 1990 to June 2010, and again from October 2024 to the present. They were a
*child member*, then nothing, then an *adult counselor*. That is one `person` row and
**two `membership` rows**. A model that puts `is_member` or `member_type` on the person
cannot express it, and cannot answer "who was in Pack 12 in 1998?" six years from now.
(The 1990–2010 membership is now the *reachable* half of that sentence rather than the optimistic one.
The legacy corpus is **two exports** — people, with the period each was a member of the organization, and
events, with who attended — and the people export **states membership periods**, so the import writes
bounded `membership` rows, both ends dated and marked `data_confidence = 'low'`
([D-092](decisions/decision-log.md#d-092--the-corpus-is-people-and-events-and-it-names-no-units),
[D-093](decisions/decision-log.md#d-093--the-one-off-import-may-create-memberships-both-ends-dated)).
A period the export does not state still exists only where somebody recorded it on evidence, and an
imported period never runs open-ended and is never inferred from attendance.
**"Who was in Pack 12 in 1998?" is not answered either way**, and round 10 made the question doubly
unanswerable: neither export named a sub-unit, and there are no sub-units to name now
([D-092](decisions/decision-log.md#d-092--the-corpus-is-people-and-events-and-it-names-no-units),
[D-097](decisions/decision-log.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)). A group's
roster before go-live is a thing a person types in, never a thing the import inferred.)

So there are five rules the data model obeys throughout:

| # | Rule | Consequence |
|---|------|-------------|
| 1 | Personhood is separate from participation | `person` holds identity only. No member flags. |
| 2 | Participation is a period, not a boolean | `membership`, `person_group_member`, `guardianship`, `role_holder` all carry `valid_from` / `valid_to`. |
| 3 | Access is granted, never implied by identity | Being a parent does not by itself grant access to the child's data — the `guardianship` row's `right_level` does, and `none` is a value it is allowed to hold ([D-074](decisions/decision-log.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular)). |
| 4 | A group is not membership, and neither is an office | There is **one** membership, at the unit. A `person_group` holds a dated roster and a `role` holds dated holders, and **neither grants anything** by being what it is. |
| 5 | Authority is one permission, allowed or denied | A grant names one permission code, one scope (the unit, or exactly one item) and an effect. **Allowed when some live allow applies and no live deny applies.** No levels, no "nearer wins", deny absolute. |

Rule 4 is load-bearing, and it is now carried by two tables instead of one:
[D-098](decisions/decision-log.md#d-098--a-group-is-a-persongroup-explicit-members-a-lifetime-and-no-authority)
for groups, [D-100](decisions/decision-log.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)
for offices, both standing on
[D-005](decisions/decision-log.md#d-005--permissions-are-grants-never-derived-from-identity).
"Am I a paid-up member?" is one row, one status, one date — regardless of how many
Thursday-evening groups the person turns up to, and regardless of whether they run any of them.

Rule 5 replaced the organization's old constitutional principle rather than inheriting it. What used to
sit here was *"authority does not flow down the hierarchy: a unit is covered only if it exposes its
scope"*, and it died with the hierarchy
([D-031](decisions/decision-log.md#d-031--no-downward-inheritance-of-authority-scopeexposure-is-the-only-crossing),
[D-049](decisions/decision-log.md#d-049--the-root-may-not-read-into-its-sub-units-scopeexposure-is-the-only-crossing),
both deleted by [D-097](decisions/decision-log.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)).
**The property it bought is gone and this page says so plainly:** access to a body's children used to have
to be granted *by that body*, by people who recruited the leader and can be asked. With one unit there is
no such body, a unit-scope grant reaches every member, and what remains of the safeguarding story is a
named adult holding the write, an audit trail whose payloads expire after two years, and a report — minus
the part where the adult was somebody the body chose. What the round did **not** lose is the half of the
rule that still has a subject: nothing is implied by who somebody is, and a deny cannot be outvoted
([D-013](decisions/decision-log.md#d-013--explicit-deny-revoked-is-checked-before-everything)).

---

## Reading order

### Domain (what the organization actually is)

| Document | Covers |
|----------|--------|
| [glossary.md](glossary.md) | Ubiquitous language. Read this first. |
| [domain/01-overview.md](domain/01-overview.md) | The model in plain language, actors, lifecycles. |
| [domain/02-actors.md](domain/02-actors.md) | Accounts, self-registration, unauthenticated people. |
| [domain/03-identity-and-legacy.md](domain/03-identity-and-legacy.md) | Historical records, matching, merging people. |
| [domain/08-person-data.md](domain/08-person-data.md) | What the system knows about a person, and why it is all one kind of data. Read it next to the identity document above — together they draw the boundary. |
| [domain/04-organization-structure.md](domain/04-organization-structure.md) | Units, nesting, restructuring over decades. |
| [domain/05-membership-lifecycle.md](domain/05-membership-lifecycle.md) | Register → request → accept → pay → member → lapse → return. |
| [domain/06-authorization-model.md](domain/06-authorization-model.md) | The permission model end to end. |
| [domain/07-events.md](domain/07-events.md) | Events, registration, capacity, presence, forms. |

### Data model (tables)

| Document | Covers |
|----------|--------|
| [data-model/00-conventions.md](data-model/00-conventions.md) | Naming, keys, temporal patterns, enums. **Read before reviewing any data-model document — §6a says who enforces what.** |
| [data-model/01-identity.md](data-model/01-identity.md) | `person`, `account`, contact points, identifiers. |
| [data-model/09-attributes.md](data-model/09-attributes.md) | `attribute_definition`, `person_attribute`, `attribute_option` — everything about a person that is not a name, a gender or an age. |
| [data-model/02-organization.md](data-model/02-organization.md) | `person_group`, `person_group_member` — named sets of people, their lifetimes, their dated rosters. There is no unit table; the unit is a scope. |
| [data-model/03-membership.md](data-model/03-membership.md) | `membership`, `membership_request` — the period, the renewal window, the sweep. (`unit_participation` is deleted by D-097; §5 of that page is the tombstone.) |
| [data-model/04-relationships.md](data-model/04-relationships.md) | `guardianship`, `guardianship_permission`. |
| [data-model/05-authorization.md](data-model/05-authorization.md) | `permission`, `role`, `role_holder`, `access_grant` (one code, allow or deny), `audience` + `audience_operand` + `selector_type` (the grantee expression). |
| [data-model/06-audit-and-import.md](data-model/06-audit-and-import.md) | Audit trail, merge log, legacy import. |
| [data-model/07-finance.md](data-model/07-finance.md) | Fees and payments. **Provisional — you have not specified this yet.** |
| [data-model/08-events.md](data-model/08-events.md) | `event`, registration, capacity, presence, questions. |

### Reference

| Document | Covers |
|----------|--------|
| [appendix/erd.md](appendix/erd.md) | Entity-relationship diagrams. |
| [appendix/permission-catalog.md](appendix/permission-catalog.md) | Every permission code. |
| [decisions/decision-log.md](decisions/decision-log.md) | Decisions taken, with rationale. |
| [open-questions.md](open-questions.md) | Unresolved items, each with a schema impact. Sections are closed as they are answered and the reasoning is kept: **section B, identity and history, is closed in full** — merge chains and unmerge, the two retention clocks, the second account, and the shape of the legacy corpus ([D-087](decisions/decision-log.md#d-087--merge-chains-stay-because-reversing-a-merge-is-a-supported-operation)–[D-090](decisions/decision-log.md#d-090--the-legacy-corpus-is-thousands-of-roster-rows-with-numbers-and-no-money)) — and **section C, organization, is closed with it** — the root's read into a sub-unit, a reused unit number, what a permission group is and what appointing writes, what the corpus names, and who may place a person in a unit ([D-091](decisions/decision-log.md#d-091--a-permission-group-is-a-rule-and-a-list-at-once-and-a-rule-may-name-another-group)–[D-096](decisions/decision-log.md#d-096--a-reused-unit-number-is-a-new-unit-unless-someone-records-the-continuity)). **Round 10 then deleted the subject of several of those answers** by removing the hierarchy they were all about ([D-097](decisions/decision-log.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)); they stay where they are, readable, marked. **Closed sections are not empty ones**: what they closed stays readable, and the questions that moved out of them are elsewhere — F-12 for a rule-filled role, A-4 for the organizational year, and the composition power over a group in the catalog's §12. |

---

## Scope boundaries

**In scope now:** identity, everything else the organization records about a person, accounts,
membership over time, organizational units, guardianship, events, and the authorization system.

**Deliberately deferred** (referenced so the data model does not block them, not designed):
fees and payment processing beyond the provisional shape in
[data-model/07-finance.md](data-model/07-finance.md), documents,
reporting, notifications, and the API/UI layer. Each is listed in
[open-questions.md](open-questions.md) with the hooks already left for it.

**Communication sits between the two lists, and the line is worth drawing rather than guessing.**
This list used to name it flatly as undesigned, which stopped being true when its **shape** was decided:
internal first, external channels are delivery rather than a product, everyone may send a direct message,
`broadcast` is one ordinary scoped permission, and **the recipient chooses the channel**
([D-077](decisions/decision-log.md#d-077--messaging-is-direct-by-default-broadcast-is-an-ordinary-scoped-permission-and-the-recipient-chooses-the-channel)),
with a direct message to a minor mirrored to its guardians and no sender-side age check anywhere
([D-082](decisions/decision-log.md#d-082--a-direct-message-to-a-minor-is-mirrored-to-the-minors-guardians)).
Its codes are in [appendix/permission-catalog.md](appendix/permission-catalog.md). **What is still
undesigned is the module**: templates, opt-out granularity, retention, moderation — the Communication row
of [open-questions.md](open-questions.md)'s section H. **Notifications stay genuinely undesigned** — the
renewal window made them dated rather than status-driven, which is a design note, not a design.

**Off this list, because the module it named does not exist:** *health records*. There is no health
module waiting to be designed. [D-083](decisions/decision-log.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)
decided that everything the organization knows about a person beyond a name, a gender and an age is
**one class of data**, held in fields the organization defines while it runs — so the health file
this list used to promise is ordinary descriptive data, specified in
[domain/08-person-data.md](domain/08-person-data.md) and
[data-model/09-attributes.md](data-model/09-attributes.md). Events also came off this list, for the
opposite reason — they were designed: [domain/07-events.md](domain/07-events.md) and
[data-model/08-events.md](data-model/08-events.md).

---

## How to change this documentation

You are expected to iterate. When refining:

1. Update the affected document(s) — data model files carry the rules and the fields they bind, domain files carry the reasoning. No data model file carries SQL: since [D-072](decisions/decision-log.md#d-072--the-documentation-carries-no-sql-the-schema-is-the-orms-job) a rule is written as a requirement, and [data-model/00-conventions.md §6a](data-model/00-conventions.md#6a-who-enforces-an-invariant-now) names the layer that must carry it.
2. Record anything non-obvious that you overrule in [decisions/decision-log.md](decisions/decision-log.md).
3. Move resolved items out of [open-questions.md](open-questions.md) rather than deleting them, so the reasoning survives.

Where this documentation states an assumption you did not make, it is written as
*Assumption:* in italics so you can find and kill it with a search.
