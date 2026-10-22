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

- an **event or period** — membership, guardianship, holding a position; or
- a **derived** fact — "child" means "has an open membership of type `child`",
  "parent" means "is the subject of a guardianship relation".

This matters because of a case you named explicitly: someone who was a member from
September 1990 to June 2010, and again from October 2024 to the present. They were a
*child member*, then nothing, then an *adult counselor*. That is one `person` row and
**two `membership` rows**. A model that puts `is_member` or `member_type` on the person
cannot express it, and cannot answer "who was in Pack 12 in 1998?" six years from now.

So there are five rules the data model obeys throughout:

| # | Rule | Consequence |
|---|------|-------------|
| 1 | Personhood is separate from participation | `person` holds identity only. No member flags. |
| 2 | Participation is a period, not a boolean | `membership`, `unit_participation`, `guardianship`, `position_assignment` all carry `valid_from` / `valid_to`. |
| 3 | Access is granted, never implied by identity | Being a parent does not by itself grant access to the child's data — a `guardianship_permission` row does. |
| 4 | Belonging to a sub-unit is not membership | There is **one** membership, at the organization. Sub-units hold participation records. |
| 5 | Authority does not flow down the hierarchy | A unit is covered only if it exposes its scope — including the root, and including for reading. |

Rule 4 is load-bearing: [D-041](decisions/decision-log.md#d-041--belonging-to-a-sub-unit-is-a-participation-record-not-a-membership).
"Am I a paid-up member?" is one row, one status, one date — regardless of how many
Thursday-evening groups the person turns up to.

Rule 5 is the organization's own constitutional principle, and it has no exceptions short of
the alarmed `system_admin` escape hatch: [D-031](decisions/decision-log.md#d-031--no-downward-inheritance-of-authority-scope_exposure-is-the-only-crossing).
It applies to **reading** as well as acting — the root does not see into a pack's events and
rosters unless the pack exposes them
([D-049](decisions/decision-log.md#d-049--the-root-may-not-read-into-its-sub-units-scope_exposure-is-the-only-crossing)).
Most of what the root needs is not a crossing at all, because the membership registry and the
fees belong to the root in the first place.

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
| [data-model/02-organization.md](data-model/02-organization.md) | `org_unit`, types, hierarchy, positions. |
| [data-model/03-membership.md](data-model/03-membership.md) | `membership`, `membership_request`, `unit_participation`. |
| [data-model/04-relationships.md](data-model/04-relationships.md) | `guardianship`, `guardianship_permission`. |
| [data-model/05-authorization.md](data-model/05-authorization.md) | `permission`, `role`, `role_assignment`, `access_grant`. |
| [data-model/06-audit-and-import.md](data-model/06-audit-and-import.md) | Audit trail, merge log, legacy import. |
| [data-model/07-finance.md](data-model/07-finance.md) | Fees and payments. **Provisional — you have not specified this yet.** |
| [data-model/08-events.md](data-model/08-events.md) | `event`, registration, capacity, presence, questions. |

### Reference

| Document | Covers |
|----------|--------|
| [appendix/erd.md](appendix/erd.md) | Entity-relationship diagrams. |
| [appendix/permission-catalog.md](appendix/permission-catalog.md) | Every permission code. |
| [decisions/decision-log.md](decisions/decision-log.md) | Decisions taken, with rationale. |
| [open-questions.md](open-questions.md) | Unresolved items, each with a schema impact. |

---

## Scope boundaries

**In scope now:** identity, everything else the organization records about a person, accounts,
membership over time, organizational units, guardianship, events, and the authorization system.

**Deliberately deferred** (referenced so the data model does not block them, not designed):
fees and payment processing beyond the provisional shape in
[data-model/07-finance.md](data-model/07-finance.md), communication/messaging, documents,
reporting, and the API/UI layer. Each is listed in
[open-questions.md](open-questions.md) with the hooks already left for it.

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
