# Information System — Design Documentation

Design documentation for the organization's information system: people, accounts, membership
over time, the groups and offices people belong to, and permissions.

> **Status:** draft, actively being specified. Nothing here is frozen.
> [Decisions](decisions/index.md) holds what is settled and why;
> [open questions](open-questions.md) holds what is not.

These documents **are** the specification. There is no schema file and no code to disagree with, so
a rule that is not written down here does not exist. Every page states the design as it is now;
what a page used to say, and the argument that changed it, lives in the
[decision log](decisions/index.md) — nowhere else.

---

## The one idea this whole design rests on

**A person is not a type. A person is a person.**

Nothing about being a child, an adult, a counselor, a parent, or a member is a property of a human
being. Each of those is either

- an **event or period** — membership, guardianship, holding an office, being in a group; or
- a **derived** fact — *a person whose recorded birth date makes them a minor on the date being
  asked about*, or *one side of an active `guardianship` row*.

There is one membership type, and it is **ageless**: no floor, no ceiling, no age-out, no
child→adult transition. Age is a fact about the person, recorded once as `person.birth_date`, and it
matters where the law says it matters — guardianship, and whatever rule an organizer writes for one
event. It never matters in a membership row. No column anywhere says which bodies are for children;
the control that does that job is that a named adult holds the write, and nobody joins anything by
their own act.

The case that forced this: a person who was a member from September 1990 to June 2010, and again
from October 2024 to the present. They were a child member, then nothing, then an adult counselor.
That is one `person` row and **two `membership` rows**. A model with `is_member` or `member_type` on
the person cannot express it.

The legacy corpus arrives as **two exports** — people, with the period each was a member of the
organization, and events, with who attended. Because the people export states membership periods,
the import writes bounded `membership` rows: both ends dated, `data_confidence = 'low'`, one row per
stated period, never open-ended and never inferred from attendance — an open membership satisfies
`is_current_member()`, so an inferred one would make every 1998 roster a current member today. The
import writes no sub-unit history, because the corpus names no sub-units and there are no sub-units
to name; a group's roster before go-live is a thing a person types in. **"Who was in Pack 12 in
1998?" has no answer**, and that is a property of the design rather than a gap in the data.

Five rules the data model obeys throughout:

| # | Rule | Consequence |
|---|------|-------------|
| 1 | Personhood is separate from participation | `person` holds identity only. No member flags. |
| 2 | Participation is a period, not a boolean | `membership`, `person_group_member`, `guardianship`, `role_holder` all carry `valid_from` / `valid_to`. |
| 3 | Access is granted, never implied by identity | Being a parent does not by itself reach the child's data — the `guardianship` row's `right_level` does, and `none` is a value it is allowed to hold. |
| 4 | A group is not membership, and neither is an office | There is **one** membership, at the unit. A `person_group` holds a dated roster and a `role` holds dated holders, and **neither grants anything** by being what it is. |
| 5 | Authority is one permission, allowed or denied | A grant names one permission code, one scope (the unit, or exactly one item) and an effect. **Allowed when some live allow applies and no live deny applies.** No levels, no "nearer wins", deny absolute. |

Rule 4 has two subjects and they are kept apart on purpose. A `person_group` is **a set of people** —
a lifetime, a dated roster, no authority, joinable only by somebody else's act. A `role` is **an
office**: a named thing like *chair* or *treasurer*, with dated holders and no permissions inside it.
An office confers nothing at all; what a chair may do is a grant written somewhere that names
`ROLE(chair)`. "Am I a paid-up member?" is one row, one status, one date, however many
Thursday-evening groups the person turns up to and however many of them they run.

**Why the two are never merged:** a group's roster is materialized and dated, while an office is
held by a rule that is re-evaluated on the date being asked about. One of them has a reconstructable
past and the other does not, and a grant's reach must be readable from the grant.

Rule 5 replaced an older principle rather than inheriting it. Where this page states a boolean
answer, an earlier design stated *"authority does not flow down the hierarchy: a unit is covered only
if it exposes its scope"*. That died with the hierarchy — **the unit is a scope, not a row**, and
there is exactly one of it, so there is nothing above or below to flow between.

**A safeguarding property went with the hierarchy and nothing here reproduces it.** Access to a
body's children used to have to be granted *by that body*, by the people who know them, who
recruited the leader, and who can be asked. With one unit, a `person.view` grant at unit scope
reaches every member's entire record — the widest read permission in the system. What stands between
a person and that read is a named adult holding the write, an audit trail whose payloads expire after
two years, and a report of who holds the write. What did not go with it is the half of the rule that
still has a subject: nothing is implied by who somebody is, and a deny cannot be outvoted.

---

## Reading order

### Domain — what the organization actually is

| Document | Covers |
|----------|--------|
| [glossary.md](glossary.md) | Ubiquitous language. Read this first. |
| [glossary-authorization.md](glossary-authorization.md) | The words the permission system is made of: grants, scopes, operands, expressions. |
| [domain/01-overview.md](domain/01-overview.md) | The model in plain language: actors, lifecycles, how a person's history reads. |
| [domain/02-actors.md](domain/02-actors.md) | Accounts, self-registration, unauthenticated people. |
| [domain/03-identity-and-legacy.md](domain/03-identity-and-legacy.md) | Historical records, matching, merging and unmerging people. |
| [domain/08-person-data.md](domain/08-person-data.md) | What the system knows about a person, and why it is all one kind of data. Read it next to the identity document above — together they draw the boundary. |
| [domain/04-organization-structure.md](domain/04-organization-structure.md) | The unit as a scope, groups, offices, and what joining one means. |
| [domain/05-membership-lifecycle.md](domain/05-membership-lifecycle.md) | Register → request → accept → pay → member → lapse → return. |
| [domain/06-authorization-model.md](domain/06-authorization-model.md) | The permission model end to end. The one to read if you read only one. |
| [domain/06a-audiences-and-selectors.md](domain/06a-audiences-and-selectors.md) | Who a grant is aimed at: the expression grammar, the selector registry, and the rules that keep a tree safe. |
| [domain/07-events.md](domain/07-events.md) | Events, registration, and how authority reaches an event. §1–§7. |
| [domain/07a-capacity-presence-and-forms.md](domain/07a-capacity-presence-and-forms.md) | Capacity and the waitlist, presence, cancellation, payments, the forms. §8–§13. |

### Data model — the tables

| Document | Covers |
|----------|--------|
| [data-model/00-conventions.md](data-model/00-conventions.md) | Naming, keys, temporal patterns, enums. **Read before reviewing any data-model document — §6a says who enforces what.** |
| [data-model/01-identity.md](data-model/01-identity.md) | `person` — what the organization knows about a human, no status, no role, no type — what is deliberately not on it, and `person_name`. §1–§3. |
| [01a](data-model/01a-accounts-and-contacts.md) | `account`, `account_credential`, `person_contact`, `person_identifier` — signing in, being reached, and being named by other systems. §4–§7. |
| [01b](data-model/01b-merges-views-and-checks.md) | `identity_hypothesis`, `person_merge`, the views that exclude merged and redacted rows, the nightly checks, open issues. §8–§11. The three parts share one section numbering. |
| [data-model/09-attributes.md](data-model/09-attributes.md) | `attribute_definition`, `person_attribute`, `attribute_option` — everything about a person that is not a name, a gender or an age. |
| [data-model/02-organization.md](data-model/02-organization.md) | `person_group`, `person_group_member` — named sets of people, their lifetimes, their dated rosters. There is no unit table; the unit is a scope. |
| [data-model/03-membership.md](data-model/03-membership.md) | `membership_type`, `membership_request`, `membership` — the period, the renewal window, the sweep. |
| [data-model/04-relationships.md](data-model/04-relationships.md) | `guardianship`, and the history of its right level. |
| [data-model/05-authorization.md](data-model/05-authorization.md) | `permission`, `role`, `role_holder`, `access_grant`. §1–§7. |
| [05a](data-model/05a-audience-and-grammar.md) · [05b](data-model/05b-expression-tree.md) | The grantee expression: `audience`, the grammar, `selector_type`, and the `audience_operand` tree. §8. |
| [05c](data-model/05c-access-log-and-resolver.md) | `access_log` and the resolver. §9–§10. |
| [05d](data-model/05d-invariants-and-seed.md) | The invariants, what ships seeded, and what is open. §11–§13. The six parts share one section numbering, so a `§` citation names a number and this table says where it lives. |
| [05e](data-model/05e-keys-and-callers.md) | `api_key` — a caller that is nobody: what it may hold, what it may never hold, and how its calls reach the same resolver. §14–§17. |
| [data-model/06-audit-and-import.md](data-model/06-audit-and-import.md) | `audit_log` — the data-change trail, its trigger, what is stripped before a row is written, the history query. §1–§2. |
| [06a](data-model/06a-import.md) | `import_batch`, the staging tables, the six stages, reversibility, idempotency, and what a source row actually evidences. §3. |
| [06b](data-model/06b-redaction-and-checks.md) | `redaction_log`, the integrity checks over both trails, open issues. §4–§6. The three parts share one section numbering. |
| [data-model/07-finance.md](data-model/07-finance.md) | Fees and payments. **Provisional — you have not specified this yet.** |
| [data-model/08-events.md](data-model/08-events.md) | `event`, organizers, registrations, questions, answers. §1–§7. |
| [08a](data-model/08a-event-guards-and-checks.md) | How authority reaches an event, the three queries that matter, integrity checks, open issues. §8–§11. The two parts share one section numbering. |

### Reference

| Document | Covers |
|----------|--------|
| [appendix/erd.md](appendix/erd.md) | Entity-relationship diagrams. |
| [appendix/permission-catalog.md](appendix/permission-catalog.md) | Every permission code, and the offices the organization starts with. |
| [appendix/removed-concepts.md](appendix/removed-concepts.md) | Names that are not in the model, what to use instead of each, and the decision that took it. |
| [decisions/index.md](decisions/index.md) | Every decision, its reasoning, and the round that took it. |
| [open-questions.md](open-questions.md) | What is unresolved, each with its schema impact, plus the assumption index. |

---

## Scope boundaries

**In scope now:** identity, everything else the organization records about a person, accounts,
membership over time, groups and offices, guardianship, events, and the authorization system.

**Deliberately deferred** — referenced so the data model does not block them, not designed: fee and
payment processing beyond the provisional shape in
[data-model/07-finance.md](data-model/07-finance.md), documents, reporting, notifications, and the
API and UI layers. Each is listed in [open-questions.md](open-questions.md) with the hooks already
left for it.

**Communication sits between the two lists, and the line is worth drawing rather than guessing.**
Its **shape** is decided: internal first, external channels are delivery rather than a product,
anyone may send a direct message, `broadcast` is one ordinary scoped permission, the recipient
chooses the channel, and a direct message to a minor is mirrored to that minor's guardians. Its
codes are in the catalog. **What is undesigned is the module** — templates, opt-out granularity,
retention, moderation. Notifications stay genuinely undesigned: the renewal window made them dated
rather than status-driven, which is a design note, not a design.

**There is no health module, and none is waiting to be designed.** Everything the organization knows
about a person beyond a name, a gender and an age is **one class of data**, held in fields the
organization defines while it runs — [domain/08-person-data.md](domain/08-person-data.md) and
[data-model/09-attributes.md](data-model/09-attributes.md). Sensitivity is graded by **what a grant
exposes**, never by which table a permission code names.

---

## How to change this documentation

You are expected to iterate. When refining:

1. **State what is.** A page carries the current design and no history. When you overrule
   something, delete the old statement from the page and let the decision entry own the exchange.
   Where a reader would plausibly reach for the thing you removed, leave one line naming it, saying
   it is not there, and saying what to use instead — that is a guardrail, not a memory.
2. Update the affected documents. Domain files carry the model in plain language; data-model files
   carry the rules and the fields they bind. No file carries SQL: a rule is written as a numbered
   requirement, and
   [data-model/00-conventions.md §6a](data-model/00-conventions.md#6a-who-enforces-an-invariant-now)
   names the layer that must carry it. Where no layer can enforce a rule, the text says *a
   convention, not a guard* rather than letting a reader assume a guarantee.
3. Record anything non-obvious that you overrule in the [decision log](decisions/index.md), in the
   round that took it, and add it to that page's index.
4. Move a resolved item out of [open-questions.md](open-questions.md) rather than deleting it, so
   the reasoning survives.
5. A name that leaves the model gets one row in the
   [removed-concepts appendix](appendix/removed-concepts.md) and an entry in the log. The
   organization may still be using the word, so it is not deleted from its vocabulary — only from the
   model.

Where this documentation states an assumption you did not make, it is written as *Assumption:* in
italics, so you can find and kill it with a search.

---

*Decisions behind this page: D-001, D-005, D-037, D-038, D-083, D-086, D-088, D-090, D-092, D-093,
D-097, D-098, D-099, D-100.*
