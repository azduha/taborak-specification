# Glossary — Ubiquitous Language

Terms used consistently across every document in this folder. Where everyday
language is ambiguous, the definition here wins and the schema follows it.

---

## The three-way split that everything else depends on

These three words are frequently conflated in real organizations. This design keeps
them strictly apart, because conflating them is the single most common source of
unfixable data models in this domain.

| Term | Definition | Table |
|------|-----------|-------|
| **Person** | A human being the organization knows about, now or ever. Exists independent of whether they have ever logged in, paid, or applied. | `person` |
| **Account** | A set of login credentials attached to a person. Optional — a person imported from a 1994 paper roster has no account. | `account` |
| **Member** | *Not a noun in this system.* A person is "a member" at a moment in time if they hold a qualifying membership. It is always a question with a date attached. | `membership` |

A fourth, related distinction:

| Term | Definition | Table |
|------|-----------|-------|
| **User** | Avoid entirely. When you mean the account, say account; when you mean the human, say person. Most systems use "user" for the wrong one and it never gets fixed. | — |

---

## Identity

**Person** — A human. Stores given name, family name, birth date, and gender. Nothing
else. In particular: no member status, no child/adult flag, no troop, no role, and
**no deceased flag** — the organization does not record death.

**Account** — Credentials and login state for a person. A person may have zero or
more accounts over their lifetime (e.g. a childhood account abandoned in 2010, a new
one created in 2024). Accounts are never shared between people, not even between a
parent and child.

**Contact point** — A single email address, phone number, or postal address belonging
to a person. Stored as many rows per person, not as columns, so that a person can have
five email addresses, or a new kind invented later, without a migration. Each has a
`type`, a `purpose`, and a verification timestamp.

**Identity hypothesis** — A *proposed* but unconfirmed link between two `person` rows
that may actually be the same human. Created during legacy import or when someone
registers claiming a historical identity. Confirming one triggers a merge.

**Merge** — The act of declaring two person rows to be one human, and collapsing them.
Never a delete: the absorbed row survives as a tombstone pointing at the survivor, so
that historical foreign keys keep resolving.

---

## Organization

**Org unit** — Any node in the organization's structural hierarchy. Two kinds, and the
difference is load-bearing:

- **The organization itself** — the single root unit. There is exactly one, and it is where
  people are members.
- **Sub-units** — weekly meeting groups, packs, sections, teams. Created by the organization
  or by other sub-units, nested to **arbitrary depth**. They run themselves: their own
  events, their own local leadership, their own roster.

There is no fixed ladder of levels. Types are configurable rows, not a hardcoded enum,
because the vocabulary will change over decades while the data must not.

**Unit type** — A category of org unit (`organization`, `pack`, `group`, `section`, …).
Defines whether units of that type may nest, and inside which other types. Most types carry
**no nesting rules at all**, which leaves them unconstrained — the organization can invent a
kind of group and nest it wherever it likes without asking the schema's permission.

**Position** — A defined role within a unit that people can occupy:
`scoutmaster`, `assistant_leader`, `unit_treasurer`, `quartermaster`. A position is a
*slot*; it exists whether or not anyone fills it.

**Multiple people may occupy the same position at the same time.** The schema makes no
assumption of single occupancy. Some positions are organizationally limited to one holder
at a time (`position.max_holders`), but that is a per-position *limit*, not a structural
rule — and it is a limit the position declares about itself, never one imposed from
outside the unit.

**Position assignment** — The period during which a specific person occupies a specific
position in a specific unit. Carries a start, an optional end, and a primary flag. Several
assignments may be open against the same position simultaneously.

---

## Membership

**Membership** — The period during which a person is a member **of the organization**.
Holds `valid_from`, `valid_to` (null = open/current), and a status in an approval workflow.
A person accumulates multiple memberships over time; they never overwrite one another.

**There is exactly one membership, and it is ageless.** Membership does not distinguish
children from adults, has no age ceiling, and does not end because a person got older. Being
a counselor or a leader is a **position**, never a membership type.

**Membership type** — A table kept for the future, currently holding **one row**: `member`.
It survives as a table rather than collapsing into a constant so that a second kind of
membership (a supporting or honorary one) would be a data change rather than a migration.
The fee is flat and per person, so the type does not affect pricing either.

**Participation** — The period during which a person takes part in **one sub-unit**. This is
what a pack's roster is. Distinct from membership in every way: a person holds exactly one
membership and any number of participations, participation is free, and it ends when the
person stops attending rather than when a fee is unpaid. A participation row for the root
unit is created alongside each membership, so "everyone in unit X" is one uniform query.

**Membership request** — A person's application to become a member. Separate from the
membership itself, because a request has its own lifecycle (submitted, under review,
rejected, withdrawn) and can be rejected without ever producing a membership. **Nothing
gates a request except identity and payment** — there is no checklist to satisfy.

**Lapse** — A membership ending because the yearly fee was not paid or the person withdrew.
Distinct from termination for cause, which requires a reason code. **A lapsed person is not
a member and holds no member permissions**, though a renewal window lets them rejoin without
re-applying.

**Renewal window** — The fixed period after a membership expires during which payment
restores it **without re-applying**, and — importantly — opens the new period *at the expiry
date*, so the record shows continuous coverage and the person is not misclassified as a
returning member. Tracked as **dates, not a status**: during the window the person is simply
expired.

**Returning member** — A person whose new membership follows a gap. The system detects
this rather than treating them as new. This is the case you described: 1990–2010, gap,
2024–present.

---

## Relationships

**Guardianship** — A period during which one person is responsible for another. Directional:
guardian → dependent. Carries relationship kind (`parent`, `legal_guardian`, `foster`,
`other`) and an optional expiry, because guardianship ends when a child turns 18 or when
a court order changes.

**Guardianship permission** — An explicit grant that a guardian may *do* something with
the dependent's records: view, edit contacts, register for events, pay fees. **Being a
guardian grants nothing by itself.** Every capability is a separate, revocable,
audited row. This is a deliberate consequence of your answer that both read and write
permissions should be explicit.

**Household** — A shared postal address and billing grouping. Convenience, not
authority: belonging to a household grants no access. Included so that one payment can
cover several siblings without inventing a fake "family" person row.

**Acting on behalf** — Performing an operation as another person, under a guardianship
permission. Every such operation records both the acting person and the subject person.

---

## Authorization

**Permission** — The atomic unit of authority: a coded capability such as
`membership.request.approve` or `unit.manage`. Permissions are the only things the
authorization layer actually checks.

**Role** — A named bundle of permissions (`unit_leader`, `registrar`, `treasurer`,
`system_admin`). Roles exist so that operationally meaningful sets can be assigned and
reviewed as a unit.

**Role assignment** — The period during which a person holds a role. Carries a **scope**:
organization-wide, or limited to a specific org unit. Same mechanism for both, because
"treasurer of Pack 12" and "treasurer of the organization" differ only in scope.

**Scope authority** — The principle that **authority over a unit originates at that unit
and cannot be claimed from outside it.** A parent unit — including the organization itself
— can never decide permissions over a nested unit. Coverage of subordinate units exists
only where the unit itself has granted it, as an explicit `scope_exposure` row. The single
exception is `system_admin`. See
[domain/06-authorization-model.md](domain/06-authorization-model.md#2-scope-authority--no-downward-inheritance).

**Access grant** — The item-scoped layer you asked for: a period during which a person
may act on one specific record — this event, this chat thread, this document, this unit's
data — with a level (`revoked` < `view` < `contribute` < `manage` < `admin`). This is what
"per-item permission" means in this design.

**It may also target an audience** ([D-042](decisions/decision-log.md#d-042--grants-may-target-audiences-not-only-individuals)),
which is how "open this event to everyone" or "to the whole pack" is expressed. A grant
names either a person or an audience, never both.

**Audience** — A grant target that stands for a set of people rather than one. Two kinds:
**built-in audiences**, which are *rules the resolver evaluates* rather than stored lists
(`everyone`, `all_members`, the guardians of a given person, the participants of a given
unit, the leaders of a given unit), and **named groups**, which are stored membership lists
someone administers. The built-in kind is the important one: a new pack member automatically
receives what the pack was granted, with no rows to maintain and no stale-group problem.

**Membership gate** — The rule that authority held through a role is honoured **only while
the holder has a current membership**. Two carve-outs: **guardianship** (a legal
relationship, not a membership) and roles marked `requires_membership = false`
(appointed counselors and local leaders, who must be able to serve regardless of their own
fee). Ownership is exempt too, so a lapse cannot lock someone out of the screen they renew
on. See [domain/06-authorization-model.md](domain/06-authorization-model.md#6-the-resolver).

**Locality** — The rule that **a grant on the specific item always beats a grant from a
broader scope.** A per-event grant outranks a unit-scoped one, which outranks an
organization-wide one. Locality decides between competing *allows* only — a **deny wins
over everything, at any scope.** See
[domain/06-authorization-model.md](domain/06-authorization-model.md#7-precedence).

**Scope** — What a grant applies to. Either an org unit, a concrete item (via
`scope_type` + `scope_id`), or the whole organization.

**`admin`** — Per your instruction, every grantable resource exposes an `admin` level
that subsumes all narrower ones. A permission check therefore asks *"at least level X?"*
and `admin` always answers yes. Consequently there is no separate "superuser" concept
except the organization-wide `system_admin` role.

**Scope exposure** — An explicit row by which a unit grants a parent unit's role
assignment coverage over it. This is the *only* way authority crosses a unit boundary
downward, and it is created at the subordinate unit's own level, never assumed from the
hierarchy. See [data-model/05-authorization.md](data-model/05-authorization.md#5-scope_exposure--how-a-unit-delegates-upward).

**Effective permission** — The union of everything a person may do right now, computed
from role assignments and access grants that are currently valid. Never stored, always
derived, so it cannot drift out of sync with the grants that produce it.

**Delegation** — Temporarily granting someone your authority (e.g. a leader going on
leave). Modeled as an access grant with an explicit end date and a
`delegated_from` reference, so the provenance of authority is visible.

---

## Time

**Temporal row** — Any row with `valid_from` / `valid_to`. `valid_to IS NULL` means
"still true". All permission checks and history queries filter on these. The full
pattern is specified in [data-model/00-conventions.md](data-model/00-conventions.md).

**Point-in-time query** — A question of the form "who/what was true on date D?" —
*"Who was in Pack 12 on 1 June 1998?"*, *"Was this person a member when they attended
camp?"* These are first-class requirements, not an afterthought, because you have four
decades of history to preserve.

**As-of vs audit time** — Two different times, both needed. **As-of** is the date the
fact was true about the world (a membership that ran 1990–2010). **Audit time** is when
the row was written in the system. A membership backdated during a 2026 data-entry
session has as-of 1990–2010 and audit time 2026. Do not conflate them.

---

## Roles in conversation (informal terms — not schema terms)

The words you and the organization will naturally use, and what they map to:

| Informal term | Evidence in the schema |
|---------------|------------------------|
| "child member" | a person with an open `membership` whose `birth_date` makes them a minor — **age is a fact about the person, not a kind of membership** |
| "counselor" / "leader" | a `position_assignment` held by a member — **never a membership type** |
| "parent" / "caretaker" | party to an active `guardianship` row |
| "leader of the Thursday group" | `role_assignment` of a leadership role, scoped to that `org_unit` |
| "in the Thursday group" | an open `unit_participation` row for that sub-unit |
| "ex-member" | person with a `membership` whose `valid_to` has passed |
| "lapsed but can still renew" | `valid_to` passed, within the renewal window |
| "registered but not a member" | person with an `account` and no open `membership` — they may sign in and see their own data, but hold no member permissions |
| "they're allowed to attend" | `access_grant` on that event at level `view` or above, naming them **or an audience they belong to** |
| "open to everyone" | an `access_grant` whose audience is the built-in `everyone` |
| "the treasurer" | `role_assignment` of `treasurer`, scope = org or unit |
