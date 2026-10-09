# Appendix — Entity Relationship Diagrams

Diagrams of the schema in [../data-model/00-conventions.md](../data-model/00-conventions.md).
Split by subject area so each
stays readable; the areas connect through `person`, which appears in all of them.

Notation: `→` is a foreign key pointing at the referenced table. `⇒` is a polymorphic
reference (no database-level foreign key). Temporal tables are marked `[T]`.

---

## 1. Identity

```
                          ┌─────────────────────────────────┐
                          │            person               │
                          │  id, public_id                  │
                          │  given_name, family_name        │
                          │  birth_date, birth_date_precision│
                          │  record_origin, data_confidence │
                          │  merged_into_person_id ──┐ self  │
                          │  redacted_at             └──────┘│
                          └───────────────┬─────────────────┘
                                          │
        ┌──────────────┬──────────────────┼──────────────────┬───────────────┐
        │              │                  │                  │               │
        ▼              ▼                  ▼                  ▼               ▼
  ┌───────────┐ ┌─────────────┐  ┌────────────────┐ ┌──────────────┐ ┌────────────┐
  │person_name│ │  account    │  │ person_contact │ │person_       │ │identity_   │
  │    [T]    │ │             │  │      [T]       │ │identifier    │ │hypothesis  │
  │           │ │ person_id → │  │                │ │     [T]      │ │            │
  │ valid_from│ │ status      │  │ contact_type   │ │ scheme,value │ │ person_a_id│
  │ valid_to  │ │             │  │ purpose        │ │              │ │ person_b_id│
  └───────────┘ └──────┬──────┘  │ is_primary     │ └──────────────┘ │ confidence │
                       │         │ verified_at    │                  │ match_     │
                       ▼         └────────────────┘                  │  signals   │
              ┌──────────────────┐                                  │ status     │
              │account_credential│                                  └─────┬──────┘
              │  [T]             │                                        │
              │ credential_type  │                                        ▼
              │ secret_hash      │                                 ┌──────────────┐
              │ external_ref     │                                 │ person_merge │
              │ valid_to         │                                 │ surviving_id │
              └──────────────────┘                                 │ merged_id    │
                                                                   │ hypothesis_id│
                                                                   │ reversed_at  │
                                                                   └──────┬───────┘
                                                                          ▼
                                                                  ┌────────────────┐
                                                                  │ field_conflict │
                                                                  └────────────────┘
```

**Key point:** everything hangs off `person`, and `person` itself holds only identity.
No status, no role, no membership. See
[../data-model/01-identity.md](../data-model/01-identity.md#1-the-central-claim).

---

## 2. Organization

```
  ┌────────────────┐         ┌─────────────────────┐
  │ org_unit_type  │◄────────│ org_unit_type_rule  │
  │  code          │  parent │  parent_type_id     │
  │  allows_       │  ──────►│  child_type_id      │
  │    children    │         │  is_required        │
  │  allows_adults │         └─────────────────────┘
  │  is_leaf       │
  └───────┬────────┘
          │
          ▼
  ┌──────────────────────┐          ┌──────────────────┐
  │      org_unit        │◄─────────│  org_unit_name   │
  │  unit_type_id ───────┘          │       [T]        │
  │  parent_unit_id ──┐ self        │  name, code      │
  │  code, name       └────────────►│  change_reason   │
  │  status           [T]           │  valid_from/to   │
  │  path, depth      │             └──────────────────┘
  │  valid_from/to    │
  └────┬─────────┬────┘
       │         │
       │         ▼
       │  ┌───────────────────────┐
       │  │ org_unit_relationship │   split_from / merged_into /
       │  │  source_unit_id       │   successor_of / renamed_to
       │  │  target_unit_id       │
       │  │  relationship         │
       │  │  effective_date       │
       │  └───────────────────────┘
       │
       ▼
  ┌──────────────┐        ┌──────────────────────┐        ┌──────────────┐
  │   position   │◄───────│ position_assignment  │───────►│    person    │
  │  unit_type_id│        │  position_id         │        └──────────────┘
  │  code        │        │  org_unit_id    ─────┼───► org_unit
  │  is_unique_  │        │  person_id      ─────┘
  │   per_unit   │        │  valid_from/to  [T]  │
  │  is_          │       │  is_primary          │
  │   leadership  │       │  ended_reason_code   │
  └──────────────┘        └──────────────────────┘
```

**Key point:** `path`/`depth` are denormalized for fast subtree queries; `unit_ancestors()`
and `unit_descendants()` are the authority. Positions do **not** grant permissions. See
[../data-model/02-organization.md](../data-model/02-organization.md).

---

## 3. Membership

```
  ┌────────────────────┐
  │ membership_type    │
  │  code              │
  │  category ─────────┼──► 'child' | 'adult' | 'special'   ← replaces person.is_child
  │  requires_*        │
  │  min_age, max_age  │
  │  grace_period_days │
  │  fee_schedule_id ──┼──► fee_schedule
  └─────────┬──────────┘
            │
            ▼
  ┌──────────────────────────┐         ┌──────────────────────────┐
  │      membership          │         │   membership_request     │
  │  person_id ──────────────┼────────►│  person_id (SUBJECT) ────┼──► person
  │  membership_type_id ─────┘         │  submitted_by_person_id ─┼──► person
  │  status                   [T]      │  requested_membership_   │
  │  valid_from / valid_to    │        │    type_id               │
  │  renewed_from ──┐ self    │        │  status                  │
  │                 └─────────┘        │  membership_id ──────────┼──► membership
  │  outstanding_balance      │        │  previous_membership_id ─┼──► membership
  │  EXCLUDE no-overlap       │        └───────────┬──────────────┘
  └───────────────────────────┘                    │
                                                   ▼
                                    ┌──────────────────────────────┐
                                    │ membership_request_requirement│
                                    │  requirement_code ───────────┼──► requirement_code
                                    │  status                      │
                                    │  expires_at                  │
                                    └──────────────────────────────┘

  ┌────────────────────┐
  │ unit_membership    │   person_id → person        (NOT membership_id — see below)
  │  org_unit_id ──────┼──► org_unit
  │  valid_from/to [T] │
  │  join_reason_code  │
  │  EXCLUDE no-overlap│
  └────────────────────┘
```

**Two points that matter:**

- `membership_request` has **two** person references:
  `person_id` (the child, who would become a member) and `submitted_by_person_id` (the
  parent, who applied). Collapsing them makes the audit trail false.
- `unit_membership.person_id` points at **person**, not membership. This is the deliberate
  trade-off that makes the 1990s import possible:
  [../data-model/03-membership.md](../data-model/03-membership.md#5-unit_membership).

---

## 4. Guardianship

```
        ┌─────────────────────────────────────────┐
        │             guardianship                │
        │  guardian_person_id  ───────────────────┼──► person
        │  dependent_person_id ───────────────────┼──► person
        │  relationship                           │
        │  valid_from / valid_to            [T]   │
        │  is_primary_contact      ← who to phone │
        │  is_legal_decision_maker ← who may sign │
        │  EXCLUDE no-overlap on the pair         │
        └───────────────────┬─────────────────────┘
                            │
                            ▼
        ┌─────────────────────────────────────────┐
        │        guardianship_permission          │
        │  guardianship_id ───────────────────────┘
        │  permission_code  ──────────────────────┼──► permission
        │       (namespace = 'dependent')         │
        │  is_granted       ← false = explicit DENY│
        │  valid_from / valid_to            [T]   │
        └─────────────────────────────────────────┘

        ┌───────────────┐        ┌──────────────────┐
        │  household    │◄───────│ household_member │───────► person
        │  billing_     │        │  [T]             │
        │   contact_    │        └──────────────────┘
        │   person_id   │
        └───────────────┘
          ↑ NO ACCESS GRANTED BY HOUSEHOLD MEMBERSHIP — billing/address only
```

**Key point:** guardianship is a general graph — one guardian → many dependents, many
guardians → one dependent, and a person may be both. Authority is per `guardianship` row,
so a parent can have full access to one child and read-only to another. See
[../data-model/04-relationships.md](../data-model/04-relationships.md).

---

## 5. Authorization — the whole answer in one diagram

```
                    ┌──────────────────┐
                    │    permission    │   'membership.request.approve'
                    │  code, resource  │   'dependent.medical.view'
                    │  namespace       │   'event.admin'
                    └────────┬─────────┘
                             │
              ┌──────────────┴───────────────┐
              │                              │
              ▼                              ▼
    ┌──────────────────┐          ┌────────────────────┐
    │ role_permission  │          │  permission_level  │
    └────────┬─────────┘          │   scope_type       │
             │                    │   required_level   │  ── connects permission
             ▼                    └─────────┬──────────┘     codes to grant LEVELS
    ┌──────────────────┐                    │
    │       role       │          ┌─────────┴──────────┐
    │  code            │          │   access_level     │
    │  scope_required  │          │   rank 0/10/20/30/40│  ← COMPARE BY RANK,
    │  requires_*      │          │   revoked…admin     │     NEVER BY STRING
    └────────┬─────────┘          └─────────┬──────────┘
             │                              │
             ▼                              ▼
   ╔═══════════════════════╗    ╔═════════════════════════╗
   ║   role_assignment     ║    ║      access_grant       ║
   ║  SYSTEM-WIDE AUTHORITY║    ║   PER-ITEM AUTHORITY    ║
   ║                       ║    ║                         ║
   ║ person_id             ║    ║ person_id               ║
   ║ role_id               ║    ║ scope_type ─────────────╫──► grant_scope_type
   ║ scope_type:           ║    ║ scope_id  ⇒ (polymorphic)║
   ║   organization        ║    ║ level ──────────────────╫──► access_level
   ║   | org_unit          ║    ║ valid_from / valid_to   ║
   ║ scope_id              ║    ║ is_delegated            ║
   ║ valid_from/valid_to[T]║    ║ delegated_from ─────────╫──► person
   ║ delegation_of ──┐self ║    ║ revoked_at              ║
   ║                 └─────║    ╚═════════════════════════╝
   ╚═══════════════════════╝
             │                              │
             └──────────────┬───────────────┘
                            ▼
                 ╔═══════════════════════╗
                 ║       can(p, perm,    ║   ONE resolver.
                 ║         scope, at)    ║   Five channels, fixed order.
                 ╚═══════════┬═══════════╝
                             │
              ┌──────────────┼──────────────┬───────────────┐
              ▼              ▼              ▼               ▼
       0. explicit      1. ownership   2. guardianship  3. item      4. roles
          DENY (revoked)  (own row)      (dependent.*)     grant       (scoped,
          overrides                                      (access_     inherits
          everything                                      grant)      downward)
                                                                          │
                                                                          ▼
                                                                   5. default DENY
```

**Key points:**

- `role_assignment` and `access_grant` are the same idea at two granularities: authority
  held for a period, in a scope, granted by someone. They share `scope_type`, the level
  model, and the resolver.
- The `admin` level subsumes narrower ones by **prefix match**, so a new narrow permission
  is automatically covered by existing `.admin` grants.
- Explicit `revoked` is checked **first** — it overrides roles, grants, and ownership.
- `scope_id` is polymorphic (no FK) so a new grantable item type is a config row, not a
  migration. Accepted cost, with mandatory mitigations.

See [../data-model/05-authorization.md](../data-model/05-authorization.md) and
[../domain/06-authorization-model.md](../domain/06-authorization-model.md).

---

## 6. Temporal pattern, illustrated

Every `[T]` table above uses the same shape. The returning-member case shows why:

```
person 100 — Jan Novák
│
├─ membership #1   child    1990-09-01 ──────────────► 2010-06-30   completed
│    unit_membership  Troop 12  1990-09-01 ──────► 1998-06-30
│    unit_membership  Troop 31  1998-09-01 ──────────────► 2010-06-30
│
│      ← 14-year gap, no rows. Visible as data, not inferred. →
│
├─ membership #2   adult    2024-10-01 ──────────────► NULL (open, current)
│    unit_membership  Group 5   2024-10-01 ──────► NULL
│    position_assignment  scoutmaster, Group 5  2025-01-01 ──► NULL
│    role_assignment  unit_leader @ Group 5     2025-01-01 ──► 2025-12-31
│
├─ guardianship → child A    2015-03-01 ──────────► NULL
│    guardianship_permission  dependent.admin
└─ guardianship → child B    2018-07-01 ──────────► NULL
     guardianship_permission  dependent.profile.view   (court-restricted)
```

Queries this shape supports, all of which fail against a design with `person.is_member`:

```sql
-- "Was this person a member on 1998-06-01?"
-- "How many years of membership, excluding the gap?"
-- "Which unit were they in during 2003?"
-- "Were they a child or an adult when they joined the second time?"
-- "Who are the returning members?" (more than one membership with a gap)
```

---

## 7. Table inventory

| Domain | Tables |
|--------|--------|
| Identity | `person`, `person_name`[T], `account`, `account_credential`[T], `person_contact`[T], `person_identifier`[T], `identifier_scheme`, `identity_hypothesis`, `person_merge`, `field_conflict` |
| Organization | `org_unit_type`, `org_unit_type_rule`, `org_unit`[T], `org_unit_name`[T], `org_unit_relationship`, `position`, `position_assignment`[T] |
| Membership | `membership_type`, `membership`[T], `membership_request`, `requirement_code`, `membership_request_requirement`[T], `unit_membership`[T] |
| Relationships | `guardianship`[T], `guardianship_permission`[T], `household`[T], `household_member`[T] |
| Authorization | `permission`, `role`, `role_permission`, `role_assignment`[T], `access_level`, `grant_scope_type`, `access_grant`[T], `permission_level`, `access_log`, `permission_cache` |
| Audit / import | `audit_log`, `redaction_log`, `import_batch`, `staging_import`, `staging_import_row` |
| Finance *(provisional)* | `fee_schedule`[T], `fee_obligation`, `payment`, `payment_allocation` |
| Reference | `reason_code`, `access_level`, `grant_scope_type`, `identifier_scheme`, `requirement_code`, `permission`, `org_unit_type` |

**[T]** = temporal, carries `valid_from` / `valid_to`.

---

## 8. Foreign key summary

Tables with no FK on a column, and why:

| Column | Why no FK |
|--------|-----------|
| `access_grant.scope_id` | Polymorphic by design. Validated by `grant_scope_type` + orphan checks. |
| `access_log.scope_id` | Same. |
| `access_log.authorization_ref_id` | Points at one of three grant tables depending on `authorization_channel`. |
| `access_log.entity_id` | Polymorphic target of the audited action. |
| `field_conflict.entity_id` | Polymorphic; recorded alongside `entity_table`. |
| `membership_request_requirement.evidence_reference` | Free text until the document layer exists. |
| `audit_log.record_id` | Polymorphic; recorded alongside `table_name`. |

Every other column ending in `_id` has a real foreign key with `ON DELETE RESTRICT`.
**No table anywhere uses `ON DELETE CASCADE`** — see
[../data-model/00-conventions.md](../data-model/00-conventions.md#9-referential-integrity-rules).
