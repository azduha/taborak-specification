# Domain Overview

What the organization is, who interacts with the system, and how the core lifecycles
flow. Read [../glossary.md](../glossary.md) first — this document uses its terms
strictly.

---

## 1. The organization

A youth organization (Scout-like: uniformed groups, trained adult leadership, camps
and weekly meetings) with:

- **Child members** — youth participants, typically organized into units.
- **Adult members** — counselors/leaders who run units and hold positions.
- **Caretakers** — parents and legal guardians of child members. They may or may not
  be members themselves.
- **Non-member supporters** — people who interact with the organization (donors,
  volunteers, alumni) without holding a membership.

The organization has **sub-units that nest** and that have been **reorganized repeatedly
over four decades**. Both facts are load-bearing and are handled in
[04-organization-structure.md](04-organization-structure.md).

---

## 2. Actors

The system distinguishes actors by *what they can do*, not by *what they are*. The full
treatment is in [02-actors.md](02-actors.md); the summary:

| Actor | Has account? | Has membership? | Can do |
|-------|-------------|-----------------|--------|
| Anonymous visitor | no | no | see public info, submit a registration or a membership request |
| Registered person | yes | no | maintain own profile, submit/renew a request, view own history |
| Member (child) | yes | yes | own profile, unit membership, event signups, own history |
| Member (adult) | yes | yes | as above, plus whatever their role assignments permit |
| Caretaker | yes | maybe | view/act on their dependents — **only** as explicitly granted |
| Staff / registrar | yes | maybe | organization-wide administrative permissions |
| Historical record | no | yes (closed) | nothing. Data only, never a login. |

The last row matters: imported 1994 rosters create `person` rows with **no account**.
They must never be blocked from import by a "users must have email addresses" rule.

---

## 3. The three lifecycles

Almost everything in the system is one of three multi-step processes. They are separate
because they succeed and fail independently: you can register without applying, apply
without being accepted, be accepted without paying, and pay without ever joining a unit.

### 3.1 Account lifecycle

```
                  ┌─────────────────────────────────────────────┐
                  │                                             │
 (none) ──register──> pending_verification ──verify──> active ──┴──> suspended
                                                            │              │
                                                            └──> closed <──┘
```

An account is about **authentication only**. It says "this person can log in". It says
nothing about membership. A person can hold a verified, active account for years and
never become a member — a parent who only ever manages their child is exactly this case.

### 3.2 Membership lifecycle

```
 (none)
   │
   ├─ request submitted ──> under_review ──accept──> approved ──payment confirmed──> active member
   │                             │                                                    │
   │                             └──reject──> rejected                                 │
   │                                                                                   │
   │                                     ┌─────────────────────────────────────────────┤
   │                                     │                                             │
   │                                     ├──> lapsed (fee expired at the yearly date)  │
   │                                     ├──> terminated (cause, with reason)          │
   │                                     └──> suspended (temporary hold)               │
   │                                                                                   │
   │      ┌──────────────── renewal (no new application) ────────────────────────────┘
   │      │        inside the renewal window → the new period opens at the expiry date
   │      │        after it                  → the new period opens at the payment date
   │      ▼
   │   active member again
   │
   └──────────────────────── re-apply ─────────────────────────────────────────────────┘
```

Every transition creates or closes a row; nothing is overwritten. A person who was a
member 1990–2010 and again from 2024 has two `membership` rows and the gap is visible
as data, not inferred from a date.

**Note the shape of the lapse.** There is no `completed` state: it existed only for ageing
out, and membership is ageless ([D-038](../decisions/decision-log.md#d-038--membership-is-ageless)).
And **the lapse happens on a date, to everyone at once** — the yearly expiry — which is why
the renewal path matters more here than the word "grace" suggests
([D-040](../decisions/decision-log.md#d-040--the-fee-expires-yearly-a-date-tracked-renewal-window-replaces-a-grace-status)).

Detailed in [05-membership-lifecycle.md](05-membership-lifecycle.md).

### 3.3 Authorization lifecycle

```
 (none) ──grant──> active ──expire/revoke──> inactive
                     │
                     └──delegate──> delegated grant (with end date, provenance recorded)
```

Every grant has a start, an end, a granter, and a reason. Nothing is permanent by
default and nothing is revoked by deletion. Detailed in
[06-authorization-model.md](06-authorization-model.md).

---

## 4. The relationships between people

Three distinct relationships, deliberately not merged:

| Relationship | Direction | Example | Grants access? |
|--------------|-----------|---------|----------------|
| **Guardianship** | guardian → dependent | parent → child | **No** by itself — only the `right_level` (`none` / `view` / `write`) carried on the live `guardianship` row. Since D-074 that value is the whole authority; `guardianship_permission` keeps only its history. |
| **Membership** | member → the organization | anyone → the root unit | No. |
| **Participation** | participant → sub-unit | child → Pack 12 | No. |
| **Position held** | person → position in a sub-unit | adult → scoutmaster of Pack 12 | No. Only via `role_assignment`. |

**Membership and participation are two rows, not one** ([D-041](../decisions/decision-log.md#d-041--belonging-to-a-sub-unit-is-a-participation-record-not-a-membership)).
A person is a **member of the organization** and a **participant in a pack** — different
facts with different lifetimes, which is why someone who stops attending on Thursdays is
still a paid-up member, and someone who is paid up may take part in nothing.

The recurring theme: **participation is not authority.** A person can be deeply involved
— a parent of three members, a 20-year veteran, a pack's founder — and still have no
administrative access. Access comes only from an explicit grant. This separation is what
makes the permission system auditable and what prevents the classic failure where a
relationship ends (custody changes, a leader steps down) but access silently persists.

### The counselor-who-is-also-a-parent case

You named this case explicitly. It is not special:

- One `person` row.
- One open `membership` — `member`, like everyone else's.
- A `position_assignment` making them a leader of their pack.
- One `unit_participation` row for the pack they lead.
- Two `guardianship` rows (to their own children).
- Separate `guardianship_permission` rows for their parental capabilities.
- `role_assignment` rows for their leadership authority.

Note there is no `counselor` membership type. Being a counselor is the **position**, not a
kind of membership ([D-037](../decisions/decision-log.md#d-037--exactly-one-membership-type-the-fee-is-flat-and-per-person)) —
and this person's membership is identical to that of the child they lead, which is exactly
the point.

Their leadership role grants authority over **the unit's members**. Their guardianship
grants authority over **their own children**. These are different scopes and the system
keeps them separate — critically, being a leader does *not* give them access to other
people's children's records beyond what their leadership role explicitly permits.

> This last point is a safety property, not a convenience. Child-protection rules
> generally require that a leader's access to minors' personal data be bounded by their
> function. Keeping `role_assignment` and `guardianship_permission` as separate tables
> makes that boundary enforceable and reportable.

---

## 5. Multiplicity, in both directions

You specified: *one parent can manage multiple children; multiple children can be managed
by the same parent.* The model generalizes both:

- One guardian → many dependents (many `guardianship` rows).
- Many guardians → one dependent (both parents, stepparents, legal guardians — the
  schema makes no assumption that a child has exactly two, or exactly one).
- A guardian's authority over each dependent is **per-dependent**, so a parent can hold
  full permissions for one child and only read access for another (a realistic custody
  arrangement).

The same person can also be a guardian *of* someone and a dependent of someone else — the
relation is a general graph, not a two-level hierarchy. This costs nothing to allow and
avoids a rewrite when a member turns 18 and becomes guardian to a sibling.

---

## 6. The four decades of history

This is the constraint that most shapes the schema, so it is worth stating plainly.

The system must answer, correctly and indefinitely:

- "Who was in Pack 12 on 1 June 1998?"
- "Was this person a member when they attended that camp in 2003?"
- "This person registered in 2026 claiming they were a member in the 90s — is that true?"
- "What was this unit called in 2001, and what is its successor unit today?"

Consequences, all of which the data model implements:

1. **Everything temporal is a period**, never a boolean or a single date.
2. **Nothing is hard-deleted.** Merges leave tombstones; units that closed keep their rows.
3. **Names change.** Units get renamed and renumbered; people change names. Names live in
   child tables with validity periods, not as columns that get overwritten.
4. **Imported data is low-confidence.** A 1994 roster has names and dates but no reliable
   unique key. Import therefore *proposes* identities and a human confirms them.
   See [03-identity-and-legacy.md](03-identity-and-legacy.md).

---

## 7. What this design deliberately does not decide yet

These are referenced by the schema but not designed, pending your specification:

- **Events** — the schema provides `access_grant.scope_type = 'event'` and leaves the
  event tables to you. See [../open-questions.md](../open-questions.md).
- **Fees and payments** — a provisional shape exists in
  [../data-model/07-finance.md](../data-model/07-finance.md) because membership
  activation depends on it. Expect to rewrite it.
- **Notifications, documents, health records, reporting, API/UI.**

---

## 8. Next

- Terminology → [../glossary.md](../glossary.md)
- Accounts and registration → [02-actors.md](02-actors.md)
- Historical data → [03-identity-and-legacy.md](03-identity-and-legacy.md)
- Units → [04-organization-structure.md](04-organization-structure.md)
- Membership → [05-membership-lifecycle.md](05-membership-lifecycle.md)
- Permissions → [06-authorization-model.md](06-authorization-model.md)
