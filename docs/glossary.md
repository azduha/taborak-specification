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

**Person** — A human. Stores given name, family name, birth date, gender, and a
deceased flag. Nothing else. In particular: no member status, no child/adult flag,
no troop, no role.

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

**Org unit** — Any node in the organization's structural hierarchy: a troop, a pack, a
group, a section, a region, or the national body itself. Units nest. Types are
configurable rows, not a hardcoded enum, because your unit vocabulary will change over
decades while the data must not.

**Unit type** — A category of org unit (`troop`, `pack`, `region`, …). Defines whether
units of that type may nest, and inside which other types.

**Position** — A defined role within a unit that a person can occupy:
`scoutmaster`, `assistant_leader`, `unit_treasurer`, `quartermaster`. A position is a
*slot*; it exists whether or not anyone fills it.

**Position assignment** — The period during which a specific person fills a specific
position in a specific unit. Carries a start, an optional end, and a primary/secondary
flag.

---

## Membership

**Membership** — The period during which a person is a member of the organization.
Holds `valid_from`, `valid_to` (null = open/current), a membership type, and a status
in an approval workflow. A person accumulates multiple memberships over time; they
never overwrite one another.

**Membership type** — What kind of participation: `child`, `adult`, `counselor`,
`honorary`, `lifetime`. **This, not the person, is what "child" and "adult" mean in
this system.** A person's type is per-membership, so the same human can be a `child`
member in 1995 and an `adult` member in 2024.

> Naming caution: prefer `adult`/`counselor` over `leader` if the organization uses
> "leader" to mean something narrower (a trained, appointed youth leader). See
> [open-questions.md](open-questions.md).

**Membership request** — A person's application to become a member. Separate from the
membership itself, because a request has its own lifecycle (submitted, under review,
rejected, waitlisted) and can be rejected without ever producing a membership. Multiple
sequential and re-application cases are supported.

**Unit membership** — The period during which a *member* belongs to a specific org unit.
Separate from membership because they have different lifetimes: someone may hold an
organization-wide membership while between units, or (rarely) belong to two units at
once.

**Lapse** — A membership ending because the yearly fee was not paid or the person withdrew.
Distinct from termination for cause, which requires a reason code.

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
"treasurer of Troop 12" and "treasurer of the organization" differ only in scope.

**Access grant** — The item-scoped layer you asked for: a period during which a person
may act on one specific record — this event, this document, this unit's data — with a
level (`revoked` < `view` < `contribute` < `manage` < `admin`). This is what "per-item
permission" means in this design.

**Scope** — What a grant applies to. Either an org unit, a concrete item (via
`scope_type` + `scope_id`), or the whole organization.

**`admin`** — Per your instruction, every grantable resource exposes an `admin` level
that subsumes all narrower ones. A permission check therefore asks *"at least level X?"*
and `admin` always answers yes. Consequently there is no separate "superuser" concept
except the organization-wide `system_admin` role.

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
*"Who was in Troop 12 on 1 June 1998?"*, *"Was this person a member when they attended
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
| "child member" | `membership` with type `child`, currently open |
| "adult counselor" | `membership` with type `adult`/`counselor` + a position assignment |
| "parent" / "caretaker" | party to an active `guardianship` row |
| "leader of Troop 12" | `role_assignment` of a leadership role, scoped to that `org_unit` |
| "ex-member" | person with a `membership` whose `valid_to` has passed |
| "registered but not a member" | person with an `account` and no open `membership` |
| "they're allowed to attend" | `access_grant` on that event at level `view` or above |
| "the treasurer" | `role_assignment` of `treasurer`, scope = org or unit |
