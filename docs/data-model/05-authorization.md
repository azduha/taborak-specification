# Data Model — Authorization

`permission`, `role`, `role_permission`, `role_assignment`, `access_grant`,
`permission_level`, `access_log`.

This is the direct answer to your question about system-wide and per-item permissions.
Design rationale: [../domain/06-authorization-model.md](../domain/06-authorization-model.md).

---

## 1. The shape of the answer

```
permission ────────────── the atomic capability.      'membership.request.approve'
     ▲
     │ many-to-many
role ───────────────────── a named bundle.            'registrar', 'unit_leader'
     ▲
     │ assigned for a period, within a scope
role_assignment ────────── SYSTEM-WIDE authority.     person X, role R,
                                                      scope 'org_unit' 12,
                                                      2026-01-01 → 2026-12-31

access_grant ───────────── PER-ITEM authority.        person X, item ('event', 55),
                                                      level 'manage', until 2026-06-30

guardianship_permission ── authority over a PERSON.   (04-relationships.md)
```

Three tables carry authority. They are separate because their lifetimes, granters, and
revocation semantics differ — argued in
[../domain/06-authorization-model.md](../domain/06-authorization-model.md#1-the-four-channels-of-authority).

**The key insight:** `role_assignment` and `access_grant` are not two unrelated
mechanisms. They are the **same idea at two granularities** — authority held for a period,
within a scope, granted by someone. They share the scope model and the resolver, and differ
only in what they point at:

| | `role_assignment` | `access_grant` |
|---|---|---|
| Points at | A `role` (a bundle of permissions) | Always exactly one permission's worth of intent, at a level |
| Scope | `organization` or `org_unit` | Any registered `scope_type`, including concrete items |
| Cardinality | Few rows per person, long-lived | Many rows, frequently short-lived |
| Typical use | "is the treasurer" | "may manage this event" |

---

## 2. `permission`

```sql
CREATE TABLE permission (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    code            TEXT NOT NULL UNIQUE,      -- 'membership.request.approve'
    resource        TEXT NOT NULL,             -- 'membership_request'
    action          TEXT NOT NULL,             -- 'approve'
    namespace       TEXT,                      -- 'dependent' | 'system' | NULL
    -- The namespace routes a check to the right channel. 'dependent' → guardianship;
    -- NULL → the normal role/item/ownership path. See §6.

    description     TEXT NOT NULL,
    display_name    TEXT NOT NULL,
    -- Human label for the permission editor. The CODE never changes; this can.

    is_system       BOOLEAN NOT NULL DEFAULT false,
    -- True: seeded by the platform, cannot be deleted or have its code changed.

    is_assignable   BOOLEAN NOT NULL DEFAULT true,
    -- False: a permission that exists only to be subsumed by an .admin code.

    requires_scope  TEXT CHECK (requires_scope IN ('organization','org_unit')),
    -- Non-null forces the granting role/assignment to be scoped accordingly.
    -- e.g. a unit-level permission cannot be granted organization-wide by mistake.

    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT ck_permission_code_shape CHECK (
        code ~ '^[a-z_]+(\.[a-z_]+)+$'),
    CONSTRAINT ck_permission_resource_matches CHECK (
        resource = split_part(code, '.', 1)
        OR namespace = 'dependent'
        OR code LIKE 'system.%')
);

CREATE INDEX ix_permission_resource  ON permission (resource);
CREATE INDEX ix_permission_namespace ON permission (namespace) WHERE namespace IS NOT NULL;
```

### The `admin` convention, enforced structurally

Per your instruction: **every resource exposes an `admin` permission that subsumes all
narrower ones.** This is not enforced by rows but by a rule in the resolver:

```
A check for permission 'X.y' is satisfied by:
    - an exact grant of 'X.y', OR
    - a grant of 'X.admin'
```

Because it is a **prefix match on the resource part**, adding a new narrow permission to a
resource does not require updating every role that grants that resource's `admin`. Without
this, every new permission needs a migration to every role that should already have
implied it — and someone will forget one.

`is_assignable = false` exists for permissions that only make sense as part of a bundle —
a deprecated narrow permission kept for historical audit readability, for instance.

### `namespace` routes the permission to a channel

| `namespace` | Resolved against | Example |
|-------------|------------------|---------|
| `NULL` | roles, item grants, ownership | `membership.request.approve` |
| `dependent` | `guardianship_permission` | `dependent.medical.view` |
| `system` | `role_assignment` only (never item grants) | `system.permission.edit` |

This is what makes the resolver dispatchable without hardcoding code lists. A new
namespace (say, `partner.` for external partner organizations) is a data change plus one
resolver branch.

---

## 3. `role` and `role_permission`

```sql
CREATE TABLE role (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    code            TEXT NOT NULL UNIQUE,      -- 'registrar', 'unit_leader'
    name            TEXT NOT NULL,
    description     TEXT,

    is_system       BOOLEAN NOT NULL DEFAULT false,
    -- True: seeded, cannot be deleted (but its permissions may be edited).

    scope_required  TEXT CHECK (scope_required IN ('organization','org_unit')),
    -- NULL = assignable at either scope. 'organization' = only org-wide.
    -- 'org_unit' = only within a unit.

    requires_membership BOOLEAN NOT NULL DEFAULT true,
    -- Holder should be a current member. Drives the "leaver with access" report;
    -- NOT enforced by constraint (membership is temporal).

    requires_background_check BOOLEAN NOT NULL DEFAULT false,
    -- For roles involving contact with children. Reported, not constrained.

    max_term_months INTEGER,
    -- Default term length. Used to prefill valid_to, and to flag assignments that
    -- have run past their expected term.

    is_delegatable  BOOLEAN NOT NULL DEFAULT true,
    -- False for system_admin and similar. See domain/06 §8.

    sort_order      INTEGER NOT NULL DEFAULT 0,
    valid_from      DATE,
    valid_to        DATE,

    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ,
    updated_by      BIGINT REFERENCES person(id),

    CONSTRAINT ck_role_period CHECK (valid_to IS NULL OR valid_from IS NULL
                                     OR valid_to > valid_from),
    CONSTRAINT ck_role_term CHECK (max_term_months IS NULL OR max_term_months > 0)
);

CREATE INDEX ix_role_current ON role (code) WHERE valid_to IS NULL;


CREATE TABLE role_permission (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    role_id         BIGINT NOT NULL REFERENCES role(id),
    permission_id   BIGINT NOT NULL REFERENCES permission(id),

    granted_by      BIGINT REFERENCES person(id),
    granted_at      TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT uq_role_permission UNIQUE (role_id, permission_id)
);

CREATE INDEX ix_role_permission_role ON role_permission (role_id);
CREATE INDEX ix_role_permission_perm ON role_permission (permission_id);
```

**`requires_membership` and `requires_background_check` are flags, not constraints.** They
depend on temporal state in other tables, so no `CHECK` can express them. They drive
reports — the "leaver with access" and "leader with expired clearance" worklists — which
is where the enforcement actually happens. See
[03-membership.md](03-membership.md#6-membership-and-the-authorization-system).

**`max_term_months` turns "the volunteer who never got removed" into a visible expiry.**
The classic access failure is not a malicious grant; it is a legitimate one that nobody
remembered to end. Prefilling `valid_to` from a term length makes expiry the default and
permanence the deliberate act.

**No permission inheritance between roles.** A `unit_leader` does not get the
`assistant_leader` permissions by being implicitly senior. Inheritance chains in an RBAC
model produce authorization answers that nobody can predict by reading the configuration,
which is exactly what makes such systems undebuggable. If `unit_leader` should have them,
grant them explicitly.

---

## 4. `role_assignment` — system-wide authority

```sql
CREATE TABLE role_assignment (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    person_id       BIGINT NOT NULL REFERENCES person(id),
    role_id         BIGINT NOT NULL REFERENCES role(id),

    scope_type      TEXT NOT NULL DEFAULT 'organization'
                    CHECK (scope_type IN ('organization','org_unit')),
    scope_id        BIGINT,
    -- NULL for organization scope; org_unit id otherwise.

    valid_from      DATE NOT NULL DEFAULT CURRENT_DATE,
    valid_to        DATE,          -- NULL = open-ended. DISCOURAGED — see below.

    granted_by      BIGINT NOT NULL REFERENCES person(id),
    granted_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    grant_reason    TEXT,

    ended_by        BIGINT REFERENCES person(id),
    ended_at        TIMESTAMPTZ,
    ended_reason_code TEXT,
    ended_note      TEXT,

    delegation_of       BIGINT REFERENCES role_assignment(id),
    -- Non-null when this assignment is a delegation of another assignment's
    -- authority. Forms a chain; the resolver re-validates the source at use time.

    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ,
    updated_by      BIGINT REFERENCES person(id),

    CONSTRAINT ck_role_assignment_scope CHECK (
        (scope_type = 'organization' AND scope_id IS NULL)
     OR (scope_type = 'org_unit'      AND scope_id IS NOT NULL)),
    CONSTRAINT ck_role_assignment_period CHECK (
        valid_to IS NULL OR valid_to > valid_from),
    CONSTRAINT ck_role_assignment_not_own_delegation CHECK (
        delegation_of IS DISTINCT FROM id),
    CONSTRAINT ck_role_assignment_ended CHECK (
        (ended_at IS NULL) = (valid_to IS NULL) OR ended_at IS NULL)
);

CREATE INDEX ix_role_assignment_person ON role_assignment
    (person_id, valid_from DESC, valid_to);
CREATE INDEX ix_role_assignment_scope ON role_assignment
    (scope_type, scope_id) WHERE valid_to IS NULL;
CREATE INDEX ix_role_assignment_live ON role_assignment (person_id, role_id)
    WHERE valid_to IS NULL;
CREATE INDEX ix_role_assignment_expiring ON role_assignment (valid_to)
    WHERE valid_to IS NOT NULL AND valid_to BETWEEN CURRENT_DATE AND CURRENT_DATE + 60;

-- One live assignment of a given role per person per scope:
CREATE UNIQUE INDEX uq_role_assignment_unique
    ON role_assignment (person_id, role_id, scope_type, COALESCE(scope_id, 0))
    WHERE valid_to IS NULL;
```

### The open-ended assignment is the classic access failure

> *"The volunteer who stepped down in 2019 still has treasurer access in 2026."*

Every high-authority role assignment should have a `valid_to`. Two mechanisms push toward
that:

1. `role.max_term_months` prefills it.
2. A **nightly report** of assignments expiring within 60 days
   (`ix_role_assignment_expiring` is the index for it), so renewal is an active decision
   rather than a forgotten default.

*Assumption:* `valid_to` is optional in the schema but required by application validation
for any role with `scope_required` set. Making it a database `NOT NULL` would break
historical imports (where end dates are genuinely unknown), so the requirement is enforced
one level up. Tracked in [../open-questions.md](../open-questions.md).

### Scope and inheritance

A unit-scoped role assignment covers that unit **and its descendants**, per the
downward-inheritance assumption in
[../domain/04-organization-structure.md](../domain/04-organization-structure.md#6-units-and-permissions).
The resolver expands the scope using `unit_ancestors` — a district treasurer's assignment
at the district covers every troop beneath it.

**To switch to non-inheriting**, the resolver stops calling `unit_ancestors` and matches
`scope_id` exactly. That is a single change, which is why the policy decision is cheap
either way — but it must be made deliberately, because it changes who can do what across
the whole organization.

### `delegation_of`

Delegations are `role_assignment` rows pointing at the assignment they delegate. Two
required properties:

- **A delegation must always have `valid_to`.** Enforce with a constraint:

```sql
ALTER TABLE role_assignment ADD CONSTRAINT ck_delegation_expires CHECK (
    delegation_of IS NULL OR valid_to IS NOT NULL);
```

- **The delegation may not exceed the source.** Validated at grant time *and* re-validated
  at every permission check, because the delegator may have lost the authority
  mid-delegation. A stale delegation is a privilege-escalation vector.

---

## 5. `access_grant` — the per-item layer

This is the "per-item permission" table. You specified it means a **capability on that
item**: "person X may act on item Y".

```sql
CREATE TABLE grant_scope_type (
    code            TEXT PRIMARY KEY,      -- 'event','document','org_unit','membership'
    name            TEXT NOT NULL,
    item_table      TEXT NOT NULL,         -- 'event' — the table scope_id references
    is_item_scoped  BOOLEAN NOT NULL DEFAULT true,
    -- False for scope kinds that are organizational rather than a concrete item
    -- (e.g. 'organization' itself).
    supports_levels BOOLEAN NOT NULL DEFAULT true,
    description     TEXT
);

CREATE TABLE access_grant (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    person_id       BIGINT NOT NULL REFERENCES person(id),

    scope_type      TEXT NOT NULL REFERENCES grant_scope_type(code),
    scope_id        BIGINT,
    -- The concrete item id. NULL only when scope_type is not item-scoped.
    -- NO foreign key: polymorphic by design. See the note below.

    level           TEXT NOT NULL REFERENCES access_level(level),
    -- 'revoked' | 'view' | 'contribute' | 'manage' | 'admin'

    valid_from      DATE NOT NULL DEFAULT CURRENT_DATE,
    valid_to        DATE,          -- NULL = open. Discouraged; see below.

    is_delegated    BOOLEAN NOT NULL DEFAULT false,
    delegated_from  BIGINT REFERENCES person(id),
    -- The person whose authority this delegation carries.

    granted_by      BIGINT NOT NULL REFERENCES person(id),
    granted_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    grant_reason    TEXT,

    revoked_by      BIGINT REFERENCES person(id),
    revoked_at      TIMESTAMPTZ,
    revoke_reason   TEXT,

    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ,
    updated_by      BIGINT REFERENCES person(id),

    CONSTRAINT ck_access_grant_period CHECK (
        valid_to IS NULL OR valid_to > valid_from),
    CONSTRAINT ck_access_grant_scope CHECK (
        (scope_type = 'organization' AND scope_id IS NULL)
     OR (scope_type <> 'organization' AND scope_id IS NOT NULL)
     OR scope_id IS NOT NULL),
    CONSTRAINT ck_access_grant_delegation CHECK (
        is_delegated = (delegated_from IS NOT NULL)),
    CONSTRAINT ck_access_grant_not_own_delegate CHECK (
        delegated_from IS DISTINCT FROM person_id),
    CONSTRAINT ck_access_grant_revoked CHECK (
        revoked_at IS NULL OR revoked_by IS NOT NULL),
    CONSTRAINT ck_access_grant_delegation_expires CHECK (
        NOT is_delegated OR valid_to IS NOT NULL)
);

CREATE INDEX ix_access_grant_person ON access_grant (person_id, scope_type, scope_id)
    WHERE valid_to IS NULL;
CREATE INDEX ix_access_grant_scope  ON access_grant (scope_type, scope_id)
    WHERE valid_to IS NULL;
CREATE INDEX ix_access_grant_live   ON access_grant (person_id, scope_type)
    WHERE valid_to IS NULL AND revoked_at IS NULL;
CREATE INDEX ix_access_grant_deny   ON access_grant (person_id, scope_type, scope_id)
    WHERE level = 'revoked' AND valid_to IS NULL;

-- One live grant per (person, scope, level)? No — see below. One live NON-DENY
-- grant per (person, scope):
CREATE UNIQUE INDEX uq_access_grant_live
    ON access_grant (person_id, scope_type, COALESCE(scope_id, 0))
    WHERE valid_to IS NULL AND revoked_at IS NULL AND level <> 'revoked';
-- Denies are excluded from uniqueness, so a deny may coexist with a grant —
-- which is exactly what makes an explicit deny meaningful.
```

### `level` is the heart of the design

Per your instruction, every grantable resource has an `admin` level that subsumes all
narrower ones. The ordered levels (defined in
[00-conventions.md](00-conventions.md#5-enumerations)):

| Level | Rank | Means |
|-------|------|-------|
| `revoked` | 0 | **Explicitly denied. Overrides every other grant, including roles.** |
| `view` | 10 | Read |
| `contribute` | 20 | Read and add (sign up, comment, submit) |
| `manage` | 30 | Full control of the item |
| `admin` | 40 | Everything, including granting others access to this item |

**Comparisons must use `access_level.rank`, never the strings.**
`'admin' < 'contribute'` lexicographically — a string comparison silently inverts the
order and makes the most powerful level the least. This is a security bug that throws no
error, and it is why the ranks are in a table rather than computed in code.

### The `uq_access_grant_live` index excludes denies — deliberately

A deny must be able to coexist with a grant on the same scope, because that is the only
way to express "this person has access to the unit's events, except this one". The partial
index therefore covers only non-deny levels, and the resolver checks denies first.

### No foreign key on `scope_id` — the accepted trade-off

`scope_id` has no FK because it is polymorphic. This is a deliberate choice:

| | Polymorphic `scope_id` | `grantable_item` supertable |
|---|---|---|
| **Adding a grantable type** | One row in `grant_scope_type` | New table + FK from supertable + migration |
| **Referential integrity** | None — can point at a deleted item | Full |
| **Query cost** | Direct | Requires a join |
| **Risk** | Orphaned grants after an item is deleted | Migration churn on every new feature |

You have deferred events, documents, and most other grantable things. Polymorphism means
adding each one is a config row rather than a schema change, which matters a great deal
given how much of this system is not yet specified.

The mitigations are mandatory, not optional:

1. `grant_scope_type` validates the `scope_type` value (FK above).
2. Deleting an item must close its grants — an application obligation, and tested.
3. A **nightly orphan check** per scope type (§8).
4. `scope_id` is `BIGINT` and ids are never reused.

**To overrule this**, add a `grantable_item(id, item_type)` supertable and give every
grantable entity an FK to it. Tracked in
[../open-questions.md](../open-questions.md) — it is a real fork and worth a deliberate
decision.

### Why `valid_to` is discouraged here too

Same reasoning as roles, more acutely: an item grant is typically for one event, so an
open-ended item grant is nearly always a mistake. Application validation should require
`valid_to` for item-scoped grants, with `access_grant.grant_reason` explaining any
exception.

---

## 6. `permission_level` — connecting permissions to grant levels

```sql
CREATE TABLE permission_level (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    permission_id   BIGINT NOT NULL REFERENCES permission(id),
    scope_type      TEXT NOT NULL REFERENCES grant_scope_type(code),

    required_level  TEXT NOT NULL REFERENCES access_level(level),
    -- What access_grant.level is needed for this permission on this scope kind.

    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT uq_permission_level UNIQUE (permission_id, scope_type)
);

CREATE INDEX ix_permission_level_perm ON permission_level (permission_id);
```

This table is what lets **one** `access_grant.level` serve many different permission codes
without a hardcoded mapping in application code. Example:

| permission | scope_type | required_level |
|-----------|-----------|----------------|
| `event.view` | event | `view` |
| `event.register_self` | event | `contribute` |
| `event.edit` | event | `manage` |
| `event.manage_participants` | event | `manage` |
| `event.grant_access` | event | `admin` |
| `org_unit.view` | org_unit | `view` |
| `org_unit.manage` | org_unit | `manage` |

Without it, every permission check would need to know its own level — a mapping in code,
invisible to the organization, and impossible to review. With it, "what does `manage` on an
event actually let someone do?" is a query.

```sql
-- Audit question: what does 'contribute' on an event grant?
SELECT p.code, p.display_name
  FROM permission_level pl
  JOIN permission p ON p.id = pl.permission_id
 WHERE pl.scope_type = 'event' AND pl.required_level = 'contribute';
```

---

## 7. `access_log`

The audit trail. Append-only; no updates, no deletes.

```sql
CREATE TABLE access_log (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    occurred_at     TIMESTAMPTZ NOT NULL DEFAULT now(),

    actor_person_id BIGINT REFERENCES person(id),
    -- Who performed the action. NULL for system actions.

    subject_person_id BIGINT REFERENCES person(id),
    -- Whose data was affected. Differs from actor when acting on behalf.

    on_behalf       BOOLEAN NOT NULL DEFAULT false,
    -- True when actor_person_id != subject_person_id and the action was performed
    -- FOR the subject (guardianship, delegation). See 04-relationships.md §5.

    authorization_channel TEXT CHECK (authorization_channel IN
                        ('ownership','guardianship','item_grant','role','system','none')),
    -- Which of the four channels authorized this. Makes the audit answerable:
    -- "by what authority did this person do that?"

    authorization_ref_id  BIGINT,
    -- The id of the row that authorized it: role_assignment.id,
    -- access_grant.id, or guardianship_permission.id. Lets an auditor go
    -- directly to the grant that permitted the action.

    permission_code TEXT,
    -- The permission checked. Nullable for pure read events that are logged
    -- for access-trail purposes rather than permission decisions.

    scope_type      TEXT,
    scope_id        BIGINT,

    action          TEXT NOT NULL,     -- 'membership.request.approve', 'person.view'
    entity_type     TEXT,
    entity_id       BIGINT,

    result          TEXT NOT NULL CHECK (result IN ('allowed','denied','error')),
    denial_reason   TEXT,

    -- Acting context, for forensics:
    session_id      TEXT,
    ip_address      INET,
    user_agent      TEXT,
    request_id      TEXT,

    before_state    JSONB,
    after_state     JSONB,
    -- For write actions. Redacted fields must be stripped before logging —
    -- an audit log that leaks the data it audits is worse than none.

    constraint ck_access_log_denied CHECK (
        result <> 'denied' OR denial_reason IS NOT NULL)
);

CREATE INDEX ix_access_log_actor   ON access_log (actor_person_id, occurred_at DESC);
CREATE INDEX ix_access_log_subject ON access_log (subject_person_id, occurred_at DESC)
    WHERE subject_person_id IS NOT NULL;
CREATE INDEX ix_access_log_entity  ON access_log (entity_type, entity_id, occurred_at DESC);
CREATE INDEX ix_access_log_denied  ON access_log (occurred_at DESC)
    WHERE result = 'denied';
CREATE INDEX ix_access_log_behalf  ON access_log (occurred_at DESC)
    WHERE on_behalf;
```

**`authorization_channel` and `authorization_ref_id` are what make this an audit trail
rather than a log.** A record saying "person 100 changed person 200's address" answers
*what* and *who*. A record that also names the `guardianship_permission` row that
authorized it answers *why they were allowed to* — and whether that authority was valid at
the time. When a custody dispute arises eighteen months later, that is the question asked.

**`denied` results are logged too.** A series of denials is the signature of someone
probing for access they do not have. Logging only successes discards the signal.

**`before_state`/`after_state` must be redacted.** Logging the pre-change value of a
medical record into an audit table that fewer people guard than the original is a
privacy regression. Redaction happens before the insert, in the logging function — not in
a job that might not run.

**Append-only enforcement:**

```sql
CREATE OR REPLACE FUNCTION deny_access_log_mutation() RETURNS TRIGGER
LANGUAGE plpgsql AS $$
BEGIN
    RAISE EXCEPTION 'access_log is append-only';
END $$;

CREATE TRIGGER trg_access_log_no_update BEFORE UPDATE OR DELETE ON access_log
    FOR EACH ROW EXECUTE FUNCTION deny_access_log_mutation();
```

Consider partitioning by month once volume justifies it, and moving old partitions to
cheaper storage — but **never delete them**. The partition retention policy is a legal
question, not a technical one.

*Assumption:* `access_log` may be queried by staff with a specific permission, but writing
is automatic. If the organization needs human annotation of audit entries, add a separate
`access_log_note` table rather than making this table mutable.

---

## 8. The resolver in SQL

The single authorization entry point. One implementation, used everywhere. Algorithm:
[../domain/06-authorization-model.md](../domain/06-authorization-model.md#5-the-resolver).

```sql
CREATE OR REPLACE FUNCTION can(
    p_person_id       BIGINT,
    p_permission_code TEXT,
    p_scope_type      TEXT    DEFAULT NULL,
    p_scope_id        BIGINT  DEFAULT NULL,
    p_at              DATE    DEFAULT CURRENT_DATE,
    p_owner_person_id BIGINT  DEFAULT NULL   -- for the ownership channel
) RETURNS BOOLEAN
LANGUAGE plpgsql STABLE AS $$
DECLARE
    v_perm          permission%ROWTYPE;
    v_assignment_id BIGINT;
BEGIN
    SELECT * INTO v_perm FROM permission WHERE code = p_permission_code;
    IF NOT FOUND THEN
        RETURN false;                 -- unknown permission = deny
    END IF;

    -- Resolve merge chains: never evaluate permissions for a tombstoned person.
    p_person_id := resolve_person(p_person_id);

    -- CHANNEL 0: explicit deny. Checked first; overrides everything.
    IF EXISTS (
        SELECT 1 FROM access_grant g
         WHERE g.person_id = p_person_id
           AND g.level = 'revoked'
           AND g.revoked_at IS NULL
           AND g.valid_from <= p_at
           AND (g.valid_to IS NULL OR g.valid_to > p_at)
           AND (p_scope_type IS NULL
                OR (g.scope_type = p_scope_type AND g.scope_id = p_scope_id))
    ) THEN
        RETURN false;
    END IF;

    -- CHANNEL 1: ownership. Your own data.
    IF p_owner_person_id IS NOT NULL
       AND resolve_person(p_owner_person_id) = p_person_id THEN
        RETURN true;
    END IF;

    -- CHANNEL 2: guardianship (dependent.* namespace).
    IF v_perm.namespace = 'dependent' THEN
        RETURN can_act_for_dependent(p_person_id, p_owner_person_id,
                                     p_permission_code, p_at);
    END IF;

    -- CHANNEL 3: item grant on this exact scope.
    IF p_scope_type IS NOT NULL THEN
        SELECT g.id INTO v_assignment_id
          FROM access_grant g
          JOIN permission_level pl
            ON pl.permission_id = v_perm.id AND pl.scope_type = g.scope_type
          JOIN access_level req ON req.level = pl.required_level
          JOIN access_level have ON have.level = g.level
         WHERE g.person_id = p_person_id
           AND g.scope_type = p_scope_type
           AND g.scope_id   = p_scope_id
           AND g.revoked_at IS NULL
           AND g.valid_from <= p_at
           AND (g.valid_to IS NULL OR g.valid_to > p_at)
           AND have.rank >= req.rank
         LIMIT 1;
        IF FOUND THEN
            RETURN true;
        END IF;
    END IF;

    -- CHANNEL 4: roles, expanding unit scope upward.
    RETURN EXISTS (
        SELECT 1
          FROM role_assignment ra
          JOIN role_permission rp ON rp.role_id = ra.role_id
          JOIN permission p2      ON p2.id = rp.permission_id
         WHERE ra.person_id = p_person_id
           AND ra.valid_from <= p_at
           AND (ra.valid_to IS NULL OR ra.valid_to > p_at)
           AND (
                 -- exact permission
                 p2.code = p_permission_code
                 -- or the resource's .admin permission
              OR p2.code = v_perm.resource || '.admin'
                 -- or the top-level .admin
              OR (v_perm.namespace IS NULL AND p2.code = 'system.admin')
           )
           AND (
                 ra.scope_type = 'organization'
              OR (p_scope_type = 'org_unit' AND p_scope_id IS NOT NULL AND (
                     ra.scope_id = p_scope_id
                  -- downward inheritance:
                  OR ra.scope_id IN (SELECT id FROM unit_ancestors(p_scope_id))
                 ))
              OR (p_scope_type IS NULL)   -- unscoped check, any assignment qualifies
           )
           -- delegations must still be backed by a live source
           AND (ra.delegation_of IS NULL OR EXISTS (
                   SELECT 1 FROM role_assignment src
                    WHERE src.id = ra.delegation_of
                      AND src.valid_from <= p_at
                      AND (src.valid_to IS NULL OR src.valid_to > p_at)))
    );

    -- CHANNEL 5: default deny.
    RETURN false;
END $$;
```

### Properties to verify when reviewing this function

1. **Deny is checked before everything**, including ownership. A suspended account's owner
   permissions are denied by a `revoked` grant if that is what the organization wants.
2. **Ownership short-circuits before roles.** A person's access to their own record does not
   depend on any grant, which is what makes the system usable by non-members.
3. **The `.admin` prefix match is computed**, not hardcoded, so new permissions are covered
   automatically.
4. **`p_at` is threaded through every branch.** Permission checks are time-travel capable.
5. **Delegation sources are re-validated at check time**, closing the
   stale-delegation escalation.
6. **`resolve_person` is called on entry**, so a tombstoned person's id still resolves.

**A caveat on `p_scope_type IS NULL` in channel 4.** An unscoped check ("can this person do
X anywhere?") returns true if *any* assignment grants it. That is correct for UI decisions
like "show the admin menu?" but **wrong for enforcement**. Every enforcing call must pass a
scope. Enforce this in the calling convention — make scope mandatory at the API layer for
mutating operations.

### Cache

```sql
CREATE TABLE permission_cache (
    person_id       BIGINT NOT NULL,
    permission_code TEXT   NOT NULL,
    scope_type      TEXT,
    scope_id        BIGINT,
    allowed         BOOLEAN NOT NULL,
    computed_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at      TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (person_id, permission_code, COALESCE(scope_type,''),
                 COALESCE(scope_id, 0))
);

CREATE INDEX ix_permission_cache_expiry ON permission_cache (expires_at);
```

Invalidated on any write to `role_assignment`, `access_grant`, `guardianship_permission`,
`role_permission`, or a person merge. The merge case is the one that gets forgotten —
see [01-identity.md](01-identity.md#8-identity_hypothesis-and-person_merge).

---

## 9. Integrity checks

```sql
-- 1. Live grants for a person who has been merged away
SELECT g.* FROM access_grant g JOIN person p ON p.id = g.person_id
 WHERE p.merged_into_person_id IS NOT NULL AND g.valid_to IS NULL;

-- 2. Orphaned item grants (per scope type; generated from grant_scope_type)
SELECT g.id, g.scope_type, g.scope_id
  FROM access_grant g
 WHERE g.scope_type = 'event'
   AND NOT EXISTS (SELECT 1 FROM event e WHERE e.id = g.scope_id);

-- 3. Role assignments held by people with no current membership, for roles
--    that require one ("leaver with access") — the highest-value report here
SELECT ra.id, p.family_name, p.given_name, r.code, ra.valid_to
  FROM role_assignment ra
  JOIN role r ON r.id = ra.role_id
  JOIN person p ON p.id = ra.person_id
 WHERE ra.valid_to IS NULL AND r.requires_membership AND NOT is_current_member(ra.person_id);

-- 4. Role assignments granting permissions whose requires_scope is violated
SELECT ra.id, r.code, p.code FROM role_assignment ra
  JOIN role_permission rp ON rp.role_id = ra.role_id
  JOIN permission p ON p.id = rp.permission_id
 WHERE p.requires_scope IS NOT NULL AND p.requires_scope <> ra.scope_type;

-- 5. Delegations whose source has ended (stale escalation)
SELECT d.id FROM role_assignment d
  JOIN role_assignment src ON src.id = d.delegation_of
 WHERE d.valid_to IS NULL
    OR (src.valid_to IS NOT NULL AND src.valid_to <= CURRENT_DATE);

-- 6. Access grants at level 'revoked' that are the person's only grant on a scope
--    (probably intended as a removal; verify the intent)
SELECT g.person_id, g.scope_type, g.scope_id FROM access_grant g
 WHERE g.level = 'revoked' AND g.valid_to IS NULL
   AND NOT EXISTS (SELECT 1 FROM access_grant o
                    WHERE o.person_id = g.person_id AND o.scope_type = g.scope_type
                      AND o.scope_id = g.scope_id AND o.level <> 'revoked'
                      AND o.valid_to IS NULL);

-- 7. People holding system.admin — should be a very short list, alert on change
SELECT ra.person_id, p.family_name, p.given_name, ra.valid_from, ra.valid_to
  FROM role_assignment ra
  JOIN role r ON r.id = ra.role_id
  JOIN person p ON p.id = ra.person_id
 WHERE r.code = 'system_admin' AND ra.valid_to IS NULL;

-- 8. Permissions in the dependent.* namespace that lack a permission_level row
SELECT p.code FROM permission p
 WHERE p.namespace = 'dependent'
   AND NOT EXISTS (SELECT 1 FROM permission_level pl WHERE pl.permission_id = p.id);
```

Checks 3 and 7 are the ones to wire to alerts. **Check 7 should email someone every time
its result changes** — a new `system_admin` is either a planned change or an incident, and
either way someone should know within the hour.

---

## 10. Seed data — permissions

Starting catalog. Expect to edit this heavily; it is a proposal, not a specification.

```sql
INSERT INTO permission (code, resource, action, namespace, display_name, description, is_system) VALUES
-- People
('person.view',              'person', 'view',   NULL, 'View people',            'See person records', true),
('person.create',            'person', 'create', NULL, 'Create people',          'Add a person record', true),
('person.edit',              'person', 'edit',   NULL, 'Edit people',            'Change person details', true),
('person.merge',             'person', 'merge',  NULL, 'Merge people',           'Confirm identity matches and merge', true),
('person.admin',             'person', 'admin',  NULL, 'Administer people',      'Full control over person records', true),
('person.contact.edit',      'person', 'contact.edit', NULL, 'Edit contacts',   'Change contact points', true),
('person.background_check.view',   'person', 'background_check.view', NULL, 'View background checks', '', true),
('person.background_check.manage', 'person', 'background_check.manage', NULL, 'Manage background checks', '', true),

-- Accounts
('account.view',   'account', 'view',   NULL, 'View accounts',  '', true),
('account.create', 'account', 'create', NULL, 'Create accounts','', true),
('account.suspend','account', 'suspend',NULL, 'Suspend accounts','', true),
('account.admin',  'account', 'admin',  NULL, 'Administer accounts','', true),

-- Membership
('membership.view',          'membership', 'view',    NULL, 'View memberships', '', true),
('membership.request.create','membership', 'request.create', NULL, 'Submit applications','', true),
('membership.request.review','membership', 'request.review', NULL, 'Review applications','', true),
('membership.request.approve','membership','request.approve',NULL, 'Approve/reject applications','', true),
('membership.activate',      'membership', 'activate',NULL, 'Activate memberships','', true),
('membership.lapse',         'membership', 'lapse',   NULL, 'Lapse memberships',  'Administrative end (non-payment)', true),
('membership.suspend',       'membership', 'suspend', NULL, 'Suspend memberships','', true),
('membership.terminate',     'membership', 'terminate',NULL,'Terminate memberships','Expel. Restricted permission.', true),
('membership.backdate',      'membership', 'backdate',NULL, 'Backdate memberships','Enter historical periods', true),
('membership.admin',         'membership', 'admin',   NULL, 'Administer memberships','', true),

-- Organization
('org_unit.view',   'org_unit', 'view',   NULL, 'View units',   '', true),
('org_unit.create', 'org_unit', 'create', NULL, 'Create units', '', true),
('org_unit.edit',   'org_unit', 'edit',   NULL, 'Edit units',   '', true),
('org_unit.restructure','org_unit','restructure',NULL,'Restructure units','Split/merge/reparent', true),
('org_unit.admin',  'org_unit', 'admin',  NULL, 'Administer units','', true),

-- Positions
('position.view',   'position', 'view',   NULL, 'View positions', '', true),
('position.assign', 'position', 'assign', NULL, 'Appoint to positions','', true),
('position.admin',  'position', 'admin',  NULL, 'Administer positions','', true),

-- Guardianship
('guardianship.view',   'guardianship', 'view',   NULL, 'View relationships','', true),
('guardianship.create', 'guardianship', 'create', NULL, 'Record guardianship','', true),
('guardianship.permission.grant','guardianship','permission.grant',NULL,'Grant guardian permissions','', true),
('guardianship.admin',  'guardianship', 'admin',  NULL, 'Administer guardianship','', true),

-- Roles and permissions themselves
('role.view',        'role', 'view',  'system', 'View roles',        '', true),
('role.edit',        'role', 'edit',  'system', 'Edit roles',        '', true),
('role.assign',      'role', 'assign','system', 'Assign roles',      '', true),
('permission.view',  'permission', 'view','system','View permissions','', true),
('permission.edit',  'permission', 'edit','system','Edit permissions','', true),
('system.admin',     'system', 'admin','system','System administrator','Full system control', true),

-- Audit
('audit.view',   'audit', 'view',  NULL, 'View audit log',   '', true),
('audit.export', 'audit', 'export',NULL, 'Export audit log', '', true),
('audit.admin',  'audit', 'admin', NULL, 'Administer audit', '', true);

-- Dependent namespace (resolved via guardianship_permission)
INSERT INTO permission (code, resource, action, namespace, display_name, description, is_system) VALUES
('dependent.profile.view',    'dependent', 'profile.view',   'dependent', 'View profile',        '', true),
('dependent.profile.admin',   'dependent', 'profile.admin',  'dependent', 'Edit profile',        '', true),
('dependent.contact.view',    'dependent', 'contact.view',   'dependent', 'View contacts',       '', true),
('dependent.contact.manage',  'dependent', 'contact.manage', 'dependent', 'Edit contacts',       '', true),
('dependent.membership.view', 'dependent', 'membership.view','dependent', 'View membership',     '', true),
('dependent.membership.request','dependent','membership.request','dependent','Apply for membership','', true),
('dependent.event.view',      'dependent', 'event.view',     'dependent', 'View events',         '', true),
('dependent.event.register',  'dependent', 'event.register', 'dependent', 'Register for events', '', true),
('dependent.fee.view',        'dependent', 'fee.view',       'dependent', 'View fees',           '', true),
('dependent.fee.pay',         'dependent', 'fee.pay',        'dependent', 'Pay fees',            '', true),
('dependent.medical.view',    'dependent', 'medical.view',   'dependent', 'View medical records','Sensitive; often restricted', true),
('dependent.medical.admin',   'dependent', 'medical.admin',  'dependent', 'Edit medical records','', true),
('dependent.consent.give',    'dependent', 'consent.give',   'dependent', 'Give consent',        '', true),
('dependent.consent.admin',   'dependent', 'consent.admin',  'dependent', 'Manage consents',     '', true),
('dependent.achievement.view','dependent', 'achievement.view','dependent','View achievements',  '', true),
('dependent.document.view',   'dependent', 'document.view',  'dependent', 'View documents',      '', true),
('dependent.admin',           'dependent', 'admin',          'dependent', 'All guardian permissions','Subsumes all dependent.* except explicit denies', true);

INSERT INTO access_level (level, rank, description) VALUES
    ('revoked',0,'Explicitly denied; overrides all other grants'),
    ('view',10,'Read only'),
    ('contribute',20,'Read and add'),
    ('manage',30,'Full control of the item'),
    ('admin',40,'Full control including granting access');

INSERT INTO grant_scope_type (code, name, item_table, is_item_scoped) VALUES
    ('organization','Whole organization','organization',false),
    ('org_unit','Organization unit','org_unit',true),
    ('membership','Membership record','membership',true),
    ('event','Event','event',true),          -- event table to be designed
    ('document','Document','document',true); -- document layer to be designed
```

> **`system.admin` is deliberately a single top-level permission**, not a
> per-resource one. Holding it satisfies everything, and check 7 in §9 alerts on its
> holders. Keeping the most dangerous capability concentrated and alarmed is safer than
> spreading equivalents of it across every resource.

---

## 11. Open issues

- The complete permission catalog and real role definitions (§10) — needs your input.
- Downward inheritance of unit-scoped authority (§4) — a policy decision with system-wide
  effect.
- Whether `valid_to` should be mandatory for high-authority assignments (§4).
- Polymorphic `scope_id` vs a `grantable_item` supertable (§5) — a real fork.
- Whether any permission should depend on current membership status (§9 check 3 relates) —
  affects cache invalidation.
- Cache vs materialized effective-permission table (§8).
- Retention policy for `access_log` — legal input required.
- Whether `access_log` needs human annotation (recommend a separate table if so).

All tracked in [../open-questions.md](../open-questions.md).
