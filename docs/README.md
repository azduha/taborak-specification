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
cannot express it, and cannot answer "who was in Troop 12 in 1998?" six years from now.

So there are three rules the schema obeys throughout:

| # | Rule | Consequence |
|---|------|-------------|
| 1 | Personhood is separate from participation | `person` holds identity only. No member flags. |
| 2 | Participation is a period, not a boolean | `membership`, `unit_membership`, `guardianship`, `position_assignment` all carry `valid_from` / `valid_to`. |
| 3 | Access is granted, never implied by identity | Being a parent does not by itself grant access to the child's data — a `guardianship_permission` row does. |

---

## Reading order

### Domain (what the organization actually is)

| Document | Covers |
|----------|--------|
| [glossary.md](glossary.md) | Ubiquitous language. Read this first. |
| [domain/01-overview.md](domain/01-overview.md) | The model in plain language, actors, lifecycles. |
| [domain/02-actors.md](domain/02-actors.md) | Accounts, self-registration, unauthenticated people. |
| [domain/03-identity-and-legacy.md](domain/03-identity-and-legacy.md) | Historical records, matching, merging people. |
| [domain/04-organization-structure.md](domain/04-organization-structure.md) | Units, nesting, restructuring over decades. |
| [domain/05-membership-lifecycle.md](domain/05-membership-lifecycle.md) | Register → request → accept → pay → member → lapse → return. |
| [domain/06-authorization-model.md](domain/06-authorization-model.md) | The permission model end to end. |

### Data model (tables)

| Document | Covers |
|----------|--------|
| [data-model/00-conventions.md](data-model/00-conventions.md) | Naming, keys, temporal patterns, enums. **Read before reviewing any DDL.** |
| [data-model/01-identity.md](data-model/01-identity.md) | `person`, `account`, contact points, identifiers. |
| [data-model/02-organization.md](data-model/02-organization.md) | `org_unit`, types, hierarchy, positions. |
| [data-model/03-membership.md](data-model/03-membership.md) | `membership`, `membership_request`, `unit_membership`. |
| [data-model/04-relationships.md](data-model/04-relationships.md) | `guardianship`, `guardianship_permission`, households. |
| [data-model/05-authorization.md](data-model/05-authorization.md) | `permission`, `role`, `role_assignment`, `access_grant`. |
| [data-model/06-audit-and-import.md](data-model/06-audit-and-import.md) | Audit trail, merge log, legacy import. |
| [data-model/07-finance.md](data-model/07-finance.md) | Fees and payments. **Provisional — you have not specified this yet.** |

### Reference

| Document | Covers |
|----------|--------|
| [appendix/erd.md](appendix/erd.md) | Entity-relationship diagrams. |
| [appendix/permission-catalog.md](appendix/permission-catalog.md) | Every permission code. |
| [decisions/decision-log.md](decisions/decision-log.md) | Decisions taken, with rationale. |
| [open-questions.md](open-questions.md) | Unresolved items, each with a schema impact. |

---

## Scope boundaries

**In scope now:** identity, accounts, membership over time, organizational units,
guardianship, and the authorization system.

**Deliberately deferred** (referenced so the schema does not block them, not designed):
events, fees and payment processing, communication/messaging, documents, health
records, reporting, and the API/UI layer. Each is listed in
[open-questions.md](open-questions.md) with the hooks already left for it.

---

## How to change this documentation

You are expected to iterate. When refining:

1. Update the affected document(s) — data model files carry the DDL, domain files carry the reasoning.
2. Record anything non-obvious that you overrule in [decisions/decision-log.md](decisions/decision-log.md).
3. Move resolved items out of [open-questions.md](open-questions.md) rather than deleting them, so the reasoning survives.

Where this documentation states an assumption you did not make, it is written as
*Assumption:* in italics so you can find and kill it with a search.
