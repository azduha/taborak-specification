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
  │  allows_minors │  ──────►│  child_type_id      │
  │  is_leaf       │         │  is_required        │
  │  max_depth     │         └─────────────────────┘
  │  sort_order    │
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
  ┌──────────────────┐    ┌──────────────────────┐        ┌──────────────┐
  │     position     │◄───│ position_assignment  │───────►│    person    │
  │  unit_type_id    │    │  position_id         │        └──────────────┘
  │  code            │    │  org_unit_id    ─────┼───► org_unit
  │  max_holders     │    │  person_id      ─────┘
  │  is_leadership   │    │  valid_from/to  [T]  │
  │  min_age         │    │  is_primary          │
  │  requires_       │    │  ended_reason_code   │
  │   membership     │    └──────────────────────┘
  │  (REPORTED, not │
  │   enforced — the │
  │   enforced flag  │
  │   is on `role`)  │
  └──────────────────┘
```

**Key point:** `path`/`depth` are denormalized for fast subtree queries; `unit_ancestors()`
and `unit_descendants()` are the authority — **for reporting only**. They are never used in
a permission path: authority does not flow down the unit tree. Positions do **not** grant
permissions, and several people may occupy the same position (`position.max_holders`).

See [../data-model/02-organization.md](../data-model/02-organization.md) and
[../domain/06-authorization-model.md](../domain/06-authorization-model.md#2-scope-authority--no-downward-inheritance).

---

## 3. Membership

```
  ┌─────────────────────────┐
  │ membership_type         │   ONE ROW: 'member'
  │  code = 'member'        │   The vocabulary is a table so it can grow,
  │  duration_months        │   not because it varies today.  (D-037)
  │  expiry_month, _day     │   ← the organizational calendar: 1 Jan  (D-047)
  │  renewal_grace_days     │   ← the renewal WINDOW: 60 days, not a status (D-048)
  └─────────┬───────────────┘
            │
            ▼
  ┌──────────────────────────┐         ┌──────────────────────────┐
  │      membership          │         │   membership_request     │
  │  person_id ──────────────┼────────►│  person_id (SUBJECT) ────┼──► person
  │  membership_type_id ─────┘         │  submitted_by_person_id ─┼──► person
  │  status                   [T]      │  requested_unit_id ──────┼──► org_unit
  │  valid_from / valid_to    │        │  status                  │
  │  renewed_from ──┐ self    │        │  membership_id ──────────┼──► membership
  │                 └─────────┘        │  previous_membership_id ─┼──► membership
  │  outstanding_balance      │        └──────────────────────────┘
  │  EXCLUDE no-overlap       │
  │   on person_id ALONE      │   ← no membership_type_id: one type, so
  └───────────────────────────┘     "one person, one open membership" is absolute

  — no membership_request_requirement table: nothing gates a request
    except identity and payment.                          (D-044)

  ┌──────────────────────────┐
  │   unit_participation     │   person_id → person   (NOT membership_id — see below)
  │  org_unit_id ────────────┼──► org_unit
  │  valid_from/to      [T]  │
  │  join_reason_code        │
  │  EXCLUDE no-overlap      │
  └──────────────────────────┘
     ↑ PARTICIPATION, not membership. Every member also gets a row on the
       ROOT unit, so "everyone in unit X" is one query whether X is the
       organization or a Thursday-evening pack.            (D-041)
```

**Three points that matter:**

- `membership_request` has **two** person references:
  `person_id` (the child, who would become a member) and `submitted_by_person_id` (the
  parent, who applied). Collapsing them makes the audit trail false.
- `unit_participation.person_id` points at **person**, not membership. This is the deliberate
  trade-off that makes the 1990s import possible — an imported roster records who took part,
  and frequently no membership row exists to point at:
  [../data-model/03-membership.md](../data-model/03-membership.md#5-unit_participation).
- **`membership_type` exists with exactly one row**, and `category`, `min_age`, `max_age`
  and `requires_background_check` are all gone. Membership is ageless
  ([D-038](../decisions/decision-log.md#d-038--membership-is-ageless)); age is read from
  `person.birth_date` where it matters, which is guardianship and position eligibility, not
  membership.

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

        ┌─────────────────────────────────────────┐
        │  NO `household` TABLE (D-057)           │
        │  An address is a person_contact row     │
        │  (contact_type = 'postal', purpose =    │
        │  'billing'), temporal like any contact. │
        └─────────────────────────────────────────┘
          ↑ SHARED ADDRESS GRANTS NO ACCESS — all dependent.* authority comes from
            guardianship + guardianship_permission (D-019, which outlives the table)
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
                    │  namespace       │   'event.register_self'
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
    │  requires_member │          │   revoked…admin     │     NEVER BY STRING
    │   _ship         │          └─────────┬──────────┘
    │  (no period)     │  ← a ROLE is a DEFINITION and is valid ALWAYS (D-053).
    └────────┬─────────┘    The period lives on role_assignment, never here. A role
             │              ever assigned cannot be deleted, and is never switched off
             │                              │
             │   the membership gate has TWO waivers:
             │     role.requires_membership = false   (this ROLE)
             │     system.gate_exempt, a permission   (this PERSON, D-051)
             │   — the second arrives by the same route as any permission,
             │     through role_permission, and is never reachable by a grant
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
             │              ┌───────────────┘
             │              │
             │              │      ╔═════════════════════════╗
             │              │      ║     scope_exposure      ║
             │              │      ║  THE ONLY DOWNWARD      ║
             │              │      ║  CROSSING               ║
             │              │      ║                         ║
             │              │      ║ org_unit_id  = GRANTOR  ║──► org_unit
             │              │      ║ role_assignment_id ─────╫──► role_assignment
             │              │      ║ valid_from / valid_to[T]║
             │              │      ║ exposed_by / exposed_at ║
             │              │      ║ withdrawn_by / _at      ║
             │              │      ╚═════════════════════════╝
             │              │                 │
             │              │  the unit offers │ its own
             │              │  coverage over   │ assignment
             │              │  itself ─────────┘
             │              │
             │              │      ╔═════════════════════════╗
             │              │      ║        audience         ║  A grant may name a
             │              │      ║  kind: builtin | group  ║  SET of people instead
             │              │      ║  rule_key  (builtin)    ║  of a person.      (D-042)
             │              │      ║  ─────────────────────  ║
             │              │      ║  audience_member [T]    ║  ← only for kind='group';
             │              │      ║   (named groups only)   ║    built-ins are RULES,
             │              │      ╚═════════════┬═══════════╝    not stored lists
             │              │                    │
             └──────────────┴───────────────┬────┴──────────┘
                                            ▼
                 ╔═══════════════════════╗
                 ║       can(p, perm,    ║   ONE resolver.
                 ║         scope, at)    ║   Deny first, then
                 ╚═══════════┬═══════════╝   locality. Four steps.
                             │
              ┌──────────────┼──────────────┬───────────────┬──────────────┐
              ▼              ▼              ▼               ▼              ▼
       0. explicit      1. ownership   2. guardian-    3. ALLOW:      4. default
          DENY           (own row)      ship            most specific    DENY
          (revoked)      ─ gate-exempt  (dependent.*)   scope wins
          ABSOLUTE at                   ─ gate-exempt   the LEVEL
          ANY scope                                     │
          ─ to a person                                │
            OR an                                     │
            audience                                 │
                                       ┌──────────────┼──────────────┐
                                       ▼              ▼              ▼
                                  a. ITEM grant   b. UNIT grant   c. ORG grant
                                     (access_        (access_        (access_
                                      grant)          grant)          grant)
                                       │              │              │
                                       │              │ exact scope  │
                                       │              │ or exposed   │
                                       │              │ via scope_   │
                                       │              │ exposure     │
                                       └──────────────┴──────────────┴──► d. ROLE
                                                                            (role_assignment;
                                                                             org role or
                                                                             exact unit;
                                                                             NOT inherited)
                                                                            ⚠ MEMBERSHIP GATE
                                                                              applies HERE ONLY
                                                                              (D-039): no current
                                                                              membership → the
                                                                              role grants nothing,
                                                                              unless the role
                                                                              opts out.
```

**Key points:**

- `role_assignment` and `access_grant` are the same idea at two granularities: authority
  held for a period, in a scope, granted by someone. They share `scope_type`, the level
  model, and the resolver.
- **There is no wildcard permission.** A check for `X.y` needs an exact grant of `X.y`, or
  `system.admin`. The old `<resource>.admin` prefix match was removed with its sixteen codes
  (D-068, reversing D-007); "can do everything about events" is a **role** listing all
  thirteen `event.*` codes. Note `access_level.admin` (rank 40) is a **grant level** and
  survives — same word, different mechanism.
- **Deny is absolute.** An explicit `revoked` at any scope is checked *first* and beats
  everything — including the `admin` level, ownership, and guardianship. "Most specific
  scope wins" applies **only to allows** (step 3).
- **Authority never inherits downward.** A role assigned over a parent unit does **not**
  cover its sub-units. `unit_ancestors()` is not called by the resolver at all. A sub-unit's
  authority reaches outward **only** through a `scope_exposure` row, and the row is written
  by the sub-unit granting coverage over itself — the crossing is offered from below, never
  imposed from above. The sole exception is `system_admin`.
  **But note what the root owns:** the person registry, the memberships and the fees live at
  the root unit, so an organization-scoped role acting on them is working at its own scope,
  not reaching down ([D-035](../decisions/decision-log.md#d-035--one-root-unit-all-sub-units-nest-arbitrarily-beneath-it)).
- **The membership gate sits on the role tier and nowhere else** ([D-039](../decisions/decision-log.md#d-039--member-permissions-require-a-current-paid-membership)).
  Ownership and guardianship return before it, which is what keeps a lapsed person able to
  reach their own renewal screen and a lapsed parent able to act for their child. Tiers a–c
  are not gated: a grant is an explicit act, not an inherited one.
- **A grantee may be an audience.** `access_grant.person_id` and `audience_id` are mutually
  exclusive. Built-in audiences (`everyone`, `all_members`, the participants of a unit) are
  **rules evaluated at check time**; named groups are stored lists and carry the stale-group
  problem knowingly ([D-042](../decisions/decision-log.md#d-042--grants-may-target-audiences-not-only-individuals)).
- `scope_exposure` points at a specific `role_assignment`, not at a role, so coverage is
  per-person and expires with the assignment. There is **no bulk tool** and no `bulk:` marker
  ([D-045](../decisions/decision-log.md#d-045--the-bulk-scope-exposure-tool-is-removed)).
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
├─ membership #1   member   1990-09-01 ──────────────► 2010-06-30   terminated
│    unit_participation  Pack 12  1990-09-01 ──────► 1998-06-30
│    unit_participation  Pack 31  1998-09-01 ──────────────► 2010-06-30
│
│      ← 14-year gap, no rows. Visible as data, not inferred. →
│
├─ membership #2   member   2024-10-01 ──────────────► NULL (open, current)
│    unit_participation  [ROOT]    2024-10-01 ──────► NULL   ← created with the
│    unit_participation  Pack 5    2024-10-01 ──────► NULL     membership, so the
│    position_assignment  scoutmaster, Pack 5  2025-01-01 ──► NULL   roster is uniform
│    role_assignment  unit_leader @ Pack 5     2025-01-01 ──► 2025-12-31
│                      (requires_membership = false → survives a lapse, D-039;
│                       the person-level alternative is system.gate_exempt, D-051)
│
├─ guardianship → child A    2015-03-01 ──────────► NULL
│    guardianship_permission  dependent.admin          (source='self' → full)
└─ guardianship → child B    2018-07-01 ──────────► NULL
     guardianship_permission  dependent.profile.view   (court-restricted)
```

Note the two membership rows have the **same type**. They differ only in period and end
reason — this person was a member twice, and was a child and then an adult throughout. The
old diagram called them `child` and `adult`; that was the framing the ageless decision
replaced ([D-038](../decisions/decision-log.md#d-038--membership-is-ageless)).

Queries this shape supports, all of which fail against a design with `person.is_member`:

```sql
-- "Was this person a member on 1998-06-01?"
-- "How many years of membership, excluding the gap?"
-- "Which unit were they in during 2003?"
-- "How old were they when they joined the second time?"   ← from person.birth_date
-- "Who are the returning members?" (more than one membership with a gap)
```

---

## 7. Table inventory

| Domain | Tables |
|--------|--------|
| Identity | `person`, `person_name`[T], `account`, `account_credential`[T], `person_contact`[T], `person_identifier`[T], `identifier_scheme`, `identity_hypothesis`, `person_merge`, `field_conflict` |
| Organization | `org_unit_type`, `org_unit_type_rule`, `org_unit`[T], `org_unit_name`[T], `org_unit_relationship`, `position`, `position_assignment`[T] |
| Membership | `membership_type`, `membership`[T], `membership_request`, `unit_participation`[T] |
| Relationships | `guardianship`[T], `guardianship_permission`[T] (`household` removed — D-057) |
| Authorization | `permission`, `role`, `role_permission`, `role_assignment`[T], `scope_exposure`[T], `audience`[T], `audience_member`[T], `access_level`, `grant_scope_type`, `access_grant`[T], `permission_level`, `access_log`, `permission_cache` |
| Audit / import | `audit_log`, `redaction_log`, `import_batch`, `staging_import`, `staging_import_row` |
| Finance *(provisional)* | `fee_schedule`[T], `fee_obligation`, `payment`, `payment_allocation` |
| Events | `event`, `event_organizer`, `event_registration`, `event_question`[T], `event_answer` |
| Reference | `reason_code`, `access_level`, `grant_scope_type`, `identifier_scheme`, `permission`, `org_unit_type` |

> **`event` is the only table in this schema with no `[T]`** — it has no `valid_from` /
> `valid_to`, because an event is a dated occasion rather than a period-tracked record. Its
> lifecycle is `starts_at` / `ends_at` / `cancelled_at`, and it has no `status` column at all
> ([D-064](../decisions/decision-log.md#d-064--there-is-no-event-status-visibility-is-the-permission-model)).
> `event_registration` likewise stores no period: a person is attending, or they are not, and
> "unanswered" is the absence of a row
> ([D-059](../decisions/decision-log.md#d-059--unanswered-is-the-absence-of-a-row-a-registration-stores-two-values)).

**Removed since the first draft**, listed so the inventory stays honest: `requirement_code`
and `membership_request_requirement` (nothing gates a request —
[D-044](../decisions/decision-log.md#d-044--nothing-gates-a-membership-request-except-identity-and-payment));
`unit_membership` (renamed `unit_participation` —
[D-041](../decisions/decision-log.md#d-041--belonging-to-a-sub-unit-is-a-participation-record-not-a-membership));
and every background-check structure
([D-043](../decisions/decision-log.md#d-043--no-background-checks-are-recorded-in-this-system)).

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
| `audit_log.record_id` | Polymorphic; recorded alongside `table_name`. |

`access_grant.grantee` is the one **mutual-exclusion** rather than missing-FK case: exactly
one of `person_id` / `audience_id` is set, enforced by a check constraint
(`(person_id IS NOT NULL) <> (audience_id IS NOT NULL)`) rather than by two nullable FKs
with nothing between them.

Every other column ending in `_id` has a real foreign key with `ON DELETE RESTRICT`.
**No table anywhere uses `ON DELETE CASCADE`** — see
[../data-model/00-conventions.md](../data-model/00-conventions.md#9-referential-integrity-rules).
