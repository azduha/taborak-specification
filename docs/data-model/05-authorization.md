# Data Model — Authorization

`permission`, `role`, `role_permission`, `role_assignment`, `scope_exposure`,
`access_grant`, `permission_level`, `access_log`.

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

scope_exposure ─────────── upward delegation.         unit 7 agrees that assignment
                                                      912's authority covers unit 7.
```

Four tables carry authority. They are separate because their lifetimes, granters, and
revocation semantics differ — argued in
[../domain/06-authorization-model.md](../domain/06-authorization-model.md#1-the-four-channels-of-authority).

**And the rule that governs all of them:** authority over a unit originates **at that
unit** and cannot be claimed from outside it — not by a parent unit, and not by the
organization. `scope_exposure` (§5) is the only way it crosses a boundary downward, and
`system_admin` is the sole exception. See
[../domain/06-authorization-model.md](../domain/06-authorization-model.md#2-scope-authority--no-downward-inheritance).

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
    -- NULL → the normal role/item/ownership path. See §9 (the resolver).

    description     TEXT NOT NULL,
    display_name    TEXT NOT NULL,
    -- Human label for the permission editor. The CODE never changes; this can.

    is_system       BOOLEAN NOT NULL DEFAULT false,
    -- True: seeded by the platform, cannot be deleted or have its code changed.

    is_assignable   BOOLEAN NOT NULL DEFAULT true,
    -- False: a permission no grant may name directly — a deprecated narrow code kept
    -- only so historical audit rows still resolve to something readable. (Before D-068
    -- this also flagged wildcard `.admin` codes; there are none now.)

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

### There is no wildcard permission

A check for `X.y` is satisfied by **an exact grant of `X.y`**, or by `system.admin`, which is
checked outright and is the only permission meaning *everything*.

```
A check for permission 'X.y' is satisfied by:
    - an exact grant of 'X.y', OR
    - a grant of 'system.admin'   (NULL-namespace permissions only)
```

**There are no `<resource>.admin` codes.** The convention that every resource should expose
one, matched by prefix in the resolver, was **reversed by
[D-068](../decisions/decision-log.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle)**,
which also removed the resolver branch that implemented it. "Can do everything about events"
is a **role** composed from the thirteen `event.*` codes, because roles are runtime data the
organization composes (D-052) and a wildcard was the code guessing at that bundle instead.

**The cost is the one D-007 existed to prevent, and it is accepted:** a new narrow permission
is not automatically covered by the roles that should imply it. Integrity check **18**
(permissions no role grants) is the net the wildcard used to be. It fails closed.

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
    -- A role has NO PERIOD. It is valid all the time, for as long as the row exists.

    is_system       BOOLEAN NOT NULL DEFAULT false,
    -- True: seeded, cannot be DELETED or have its `code` changed (its permissions may be
    -- edited). False: an ordinary role the organization created and may delete.
    --
    -- This flag is not decoration: without a guard, deleting `system_admin` would remove
    -- the only route to system.admin and lock everyone out permanently.

    scope_required  TEXT CHECK (scope_required IN ('organization','org_unit')),
    -- NULL = assignable at either scope. 'organization' = only org-wide.
    -- 'org_unit' = only within a unit.

    requires_membership BOOLEAN NOT NULL DEFAULT true,
    -- THE MEMBERSHIP GATE (D-039), ROLE-LEVEL. True: the resolver honours this role
    -- only while the holder has a current membership — a lapse silently withholds the
    -- role's permissions. False: the role is honoured regardless, which is what keeps
    -- appointed counselors and local leaders able to serve while their own fee is
    -- unpaid. Enforced by the resolver, not merely reported.
    --
    -- This is the BLUNT form of the exemption: it exempts everyone holding this role,
    -- everywhere. The PRECISE form is the system.gate_exempt permission (D-051), which
    -- exempts a named person across every role they hold. The resolver honours a role if
    -- EITHER applies; the two compose and answer different questions.
    --
    -- Not expressible as a constraint: membership is temporal, in another table.

    max_term_months INTEGER,
    -- Default term length. Used to prefill valid_to, and to flag assignments that
    -- have run past their expected term.

    is_delegatable  BOOLEAN NOT NULL DEFAULT true,
    -- False for system_admin and similar. See domain/06 §2.6.

    sort_order      INTEGER NOT NULL DEFAULT 0,

    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ,
    updated_by      BIGINT REFERENCES person(id),

    CONSTRAINT ck_role_term CHECK (max_term_months IS NULL OR max_term_months > 0)
);
```

> **`role` has no `valid_from` / `valid_to`, deliberately** ([D-053](../decisions/decision-log.md#d-053--a-role-is-valid-always-only-its-assignment-is-temporal)).
> A role is a **definition** — a named bundle of permissions — and a definition does not come
> into and out of force. It is valid all the time, for as long as the row exists.
>
> **The period belongs on the assignment.** `role_assignment.valid_from` / `valid_to` is where
> "this person holds this role from March until December" lives, and it is unchanged. The
> distinction is between *what the role is* and *who holds it*: the first is not a historical
> fact, the second is.
>
> This removes the whole retirement mechanism. There is no `role.retire` permission, no
> resolver check on the role's period, and no report of roles expiring while still held. A
> role the organization no longer uses is one nobody holds any more.

```sql
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

**`role` is runtime data, not a fixed vocabulary.** The organization creates roles, composes
them from permissions, assigns them to people, edits what they grant, and deletes the ones
nobody ever held. The seed set in §12 is a starting point to edit, not a specification.

The one asymmetry: a role that has ever been assigned **cannot be deleted**. Three reasons, in
order of how loudly they would bite:

1. **`role_assignment.role_id` is an FK.** Deleting the row would either fail or take the
   assignment history with it, and D-003 forbids the latter.
2. **The history is the point.** "What authority did this person have in 2019?" must survive
   the role being abolished, which is exactly when someone asks.
3. **`is_system` roles must survive regardless** — deleting `system_admin` would remove the
   only route to `system.admin` and lock everyone out permanently.

**Deletion is therefore reserved for a role created by mistake and never assigned.** A role
that was used is left as it is: it is valid always
([D-053](../decisions/decision-log.md#d-053--a-role-is-valid-always-only-its-assignment-is-temporal)),
so there is nothing to switch off. A role the organization no longer wants is simply one
nobody holds — the assignments end, and the definition stays as the answer to "what did that
role mean?".

```sql
-- The guard. A role with any assignment is immutable as to deletion, forever.
CREATE OR REPLACE FUNCTION forbid_delete_assigned_role()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM role_assignment WHERE role_id = OLD.id) THEN
        RAISE EXCEPTION
            'role % has assignments and cannot be deleted; end the assignments instead '
            'so the history survives', OLD.code
            USING ERRCODE = 'restrict_violation';
    END IF;
    IF OLD.is_system THEN
        RAISE EXCEPTION 'system role % cannot be deleted', OLD.code
            USING ERRCODE = 'restrict_violation';
    END IF;
    RETURN OLD;
END $$;

CREATE TRIGGER trg_role_no_delete
    BEFORE DELETE ON role
    FOR EACH ROW EXECUTE FUNCTION forbid_delete_assigned_role();
```

**Editing a role's permissions takes effect immediately**, with no assignment touched — every
holder's next permission check sees the new set. That is the intended behaviour and it is also
the sharpest edge in the whole authorization system: `role.edit` is a bulk privilege change
wearing the clothes of a configuration screen. `role_permission` is therefore audited like any
other business table ([06-audit-and-import.md](06-audit-and-import.md)), so "what did this
role grant on that date?" is answerable after the fact — which is the only defence, since
there is nothing to check *before* the fact. The catalog marks `role.edit` 🔒🔒 for this
reason, alongside `role.assign`.

> **This is why a role having no period matters more than it looks.** Because a role is valid
> always, the *only* thing that makes authority end is the assignment ending. That puts the
> entire weight on `role_assignment.valid_to` — which is exactly where the design already
> wanted it, and why the open-ended assignment is called out as the classic access failure
> (§4).

**`role.requires_membership` is enforced by the resolver, not by a constraint.** It depends on
temporal state in another table, so no `CHECK` can express it — but unlike a mere report
flag, it is consulted at every permission check (D-039). A role with
`requires_membership = true` held by someone without a current membership **grants nothing**,
though the assignment row survives so the history is intact and a renewal can reinstate it.

**The "leaver with access" report is still worth running** — not to prevent access, which the
resolver already does, but to find assignments that should have been *closed* and were not.
Dormant authority that springs back on renewal is the failure mode this gate introduces; see
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

### Scope — exact match, plus explicit exposures

A unit-scoped role assignment covers **that unit only**. It does **not** cover the unit's
children. Authority does not flow down the hierarchy — see
[../domain/06-authorization-model.md](../domain/06-authorization-model.md#2-scope-authority--no-downward-inheritance)
for the full reasoning.

Authority crosses a unit boundary downward through exactly one mechanism: an explicit
`scope_exposure` row, written at the subordinate unit, granting a specific role assignment
coverage over it. See §5.

**The resolver matches `scope_id` exactly, plus exposures.** It must **not** call
`unit_ancestors()`. Any occurrence of `unit_ancestors()` in a permission path is a bug —
see §10, integrity check 13.


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

## 5. `scope_exposure` — how a unit delegates upward

The only mechanism by which authority crosses a unit boundary downward. Read
[../domain/06-authorization-model.md](../domain/06-authorization-model.md#2-scope-authority--no-downward-inheritance)
first — this table exists to implement that rule, and it is easy to misread as inheritance.

```sql
CREATE TABLE scope_exposure (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    org_unit_id     BIGINT NOT NULL REFERENCES org_unit(id),
    -- THE UNIT GRANTING COVERAGE OVER ITSELF. This is the grantor. It is never
    -- the unit being reached into from above.

    role_assignment_id BIGINT NOT NULL REFERENCES role_assignment(id),
    -- The assignment whose authority is honoured over this unit. Points at a specific
    -- ASSIGNMENT, not at a role — so a unit approves a person-in-a-role, not a role
    -- that any future holder would inherit.

    valid_from      DATE NOT NULL DEFAULT CURRENT_DATE,
    valid_to        DATE,          -- NULL = open

    exposed_by      BIGINT NOT NULL REFERENCES person(id),
    -- The person who exposed the scope. MUST hold scope.expose AT org_unit_id.
    -- Enforced by trg_exposure_direction (see domain §2.5) — a FK cannot express
    -- "holds a permission there". The trigger calls can(), so an ancestor-unit
    -- holder is rejected: exposure cannot be imposed from above.

    exposed_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    exposure_reason TEXT NOT NULL,
    -- e.g. 'the treasurer handles our finances', 'the registrar processes our
    -- membership'. Required: the point of the rule is that coverage is deliberate
    -- and attributable.

    withdrawn_by    BIGINT REFERENCES person(id),
    withdrawn_at    TIMESTAMPTZ,
    withdrawal_reason TEXT,

    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT ck_exposure_period CHECK (valid_to IS NULL OR valid_to > valid_from),
    CONSTRAINT ck_exposure_withdrawn CHECK (
        withdrawn_at IS NULL OR withdrawn_by IS NOT NULL)
);

-- One live exposure per (unit, assignment):
CREATE UNIQUE INDEX uq_exposure_unit_assignment
    ON scope_exposure (org_unit_id, role_assignment_id)
    WHERE valid_to IS NULL AND withdrawn_at IS NULL;

CREATE INDEX ix_exposure_unit       ON scope_exposure (org_unit_id)
    WHERE valid_to IS NULL AND withdrawn_at IS NULL;
CREATE INDEX ix_exposure_assignment ON scope_exposure (role_assignment_id)
    WHERE valid_to IS NULL AND withdrawn_at IS NULL;
```

### There is no bulk tool and no reason-prefix convention

**Every row in this table is written by the unit it covers.** There is no administrative
shortcut, no `bulk:` marker, no branch in the trigger, and no review report (D-045).

This was previously the design's most uncomfortable compromise — a tool that let a parent
write exposures on a child's behalf, argued for on grounds of scale. Your answer removed the
need for it: *"If the unit wants to expose something (a single event eg), they set the
permissions to that event for 'everyone' or a group of people."* Once **audiences** (§8) can
express "open this to everyone", the bulk case largely evaporates, and the rule becomes
absolute with nothing to explain.

**If a unit genuinely wants a higher-level officer to have authority over it,** its own
leadership writes the exposure. That is the whole rule, and now it has no exceptions.

### Why the key is the unit, and not the assignment

`org_unit_id` is the **subject and the grantor simultaneously** — the unit is granting
coverage over itself. This is what makes the direction of authority structural rather than
a convention:

- A row `(org_unit_id = 7, role_assignment_id = 912)` means *unit 7 has agreed that the
  authority held by assignment 912 applies to unit 7*.
- There is no way to express "assignment 912 covers unit 7 whether unit 7 likes it or not",
  because that row would still have to be written at unit 7.

A parent unit that wanted to reach down would have to insert a row naming the child as
grantor — which `trg_exposure_direction` rejects (domain §2.5), and which integrity check 9 reports.

### Why it points at an assignment, not a role

Pointing at `role_id` would mean a unit exposes its scope to *"whoever holds the treasurer
role"*. A person appointed treasurer two years later would silently gain access to that unit
without the unit ever being consulted. Pointing at the assignment forces a **new exposure
decision** whenever the holder changes — which is the behaviour the rule is for.

### The `scope.expose` permission

Creating an exposure requires:

```
can(actor, 'scope.expose', 'org_unit', <the unit being covered>)
```

Note the scope is the unit being covered, not the actor's own unit. An officer holding
`scope.expose` at a **parent** unit **cannot** satisfy this for a sub-unit, because they
hold nothing at the sub-unit. That single fact is what makes the whole rule enforceable.

`scope.expose` is an ordinary, narrow permission with **no wildcard that implies it** —
[D-068](../decisions/decision-log.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle)
deleted `org_unit.admin`, which previously reached it by prefix match. **That is an improvement
worth naming.** Under the old rule, "may administer this unit" silently included "may hand a
parent unit authority over this unit's records" — the single most consequential act available
at unit scope, carried as an implication of a general-purpose administrative permission and
invisible in the role editor. It is now grantable **only by naming it**, which is the correct
weight for the door it opens. See §11 for the seed row.

### Practical scale — no bulk tool, and why that is now fine

Exposing many units one at a time would be tedious, and the earlier design addressed that
with a bulk tool. **It is removed** (D-045), for a reason worth recording: once grants can
target **audiences** (§8), the common case it existed for — "let everyone / the whole group
see this event" — has a direct expression that needs no exposure row at all.

What remains is the genuinely narrower case: *this specific person, in this specific role,
should have authority over our unit.* That is a deliberate act by the unit, it happens
rarely, and doing it once per unit is the correct amount of friction rather than an
obstacle.

---

## 6. `access_grant` — the per-item layer

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

    person_id       BIGINT REFERENCES person(id),
    audience_id     BIGINT REFERENCES audience(id),
    -- EXACTLY ONE of person_id / audience_id is set. This is how "open this event
    -- to everyone" or "to the whole group" is expressed — see §8. A grant to an
    -- audience is evaluated against the person being checked.

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

    CONSTRAINT ck_access_grant_grantee CHECK (
        (person_id IS NOT NULL) <> (audience_id IS NOT NULL)),
    -- Exactly one grantee. A grant to neither is meaningless; a grant to both
    -- would be ambiguous (any person in the audience, or only this one?).

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
```

### The uniqueness rule has to be careful with audiences

The obvious index — one live grant per (grantee, scope) — no longer works, because a person
can legitimately hold a **personal** grant *and* be covered by an **audience** grant on the
same item, and those are different rows with different lifetimes.

```sql
-- One live NON-DENY grant per PERSON per scope:
CREATE UNIQUE INDEX uq_access_grant_live_person
    ON access_grant (person_id, scope_type, COALESCE(scope_id, 0))
    WHERE person_id IS NOT NULL
      AND valid_to IS NULL AND revoked_at IS NULL AND level <> 'revoked';

-- One live NON-DENY grant per AUDIENCE per scope:
CREATE UNIQUE INDEX uq_access_grant_live_audience
    ON access_grant (audience_id, scope_type, COALESCE(scope_id, 0))
    WHERE audience_id IS NOT NULL
      AND valid_to IS NULL AND revoked_at IS NULL AND level <> 'revoked';

CREATE INDEX ix_access_grant_person   ON access_grant (person_id, scope_type, scope_id)
    WHERE person_id IS NOT NULL AND valid_to IS NULL;
CREATE INDEX ix_access_grant_audience ON access_grant (audience_id, scope_type, scope_id)
    WHERE audience_id IS NOT NULL AND valid_to IS NULL;
CREATE INDEX ix_access_grant_scope    ON access_grant (scope_type, scope_id)
    WHERE valid_to IS NULL;
CREATE INDEX ix_access_grant_deny     ON access_grant
    (COALESCE(person_id, 0), scope_type, scope_id)
    WHERE level = 'revoked' AND valid_to IS NULL;
```

**Denies are excluded from both unique indexes**, so a deny may coexist with a grant — which
is exactly what makes an explicit deny meaningful. A **personal deny beats an audience
allow**, because the deny check runs first and is scope-independent (§9, channel 0).

**Audience grants cannot be delegated.** `is_delegated` requires `delegated_from`, which is a
person, and delegating "everyone" is not a coherent act — so a check constraint enforces it:

```sql
ALTER TABLE access_grant ADD CONSTRAINT ck_access_grant_audience_not_delegated CHECK (
    audience_id IS NULL OR NOT is_delegated);
```

### `level` is the heart of the design

The four **grant levels** below are a different thing from the deleted `<resource>.admin`
*permissions*, and the shared name is an accident worth guarding against: a level says **how
much** authority a grant carries and is compared by rank; a permission code says **which**
capability. Only the codes were deleted. The ordered levels (defined in
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
3. A **nightly orphan check** per scope type (§10, check 2).
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

## 7. `permission_level` — connecting permissions to grant levels

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
| `event.presence.mark` | event | `contribute` |
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

## 8. `audience` — grants that target a set of people

A grant can name a **person** or an **audience** (D-042). This is how "open this event to
everyone" or "let the whole group see it" is expressed — the case that surfaced when the
question of exposing a scope was answered with *"they set the permissions to that event for
'everyone' or a group of people."*

```sql
CREATE TABLE audience (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    code            TEXT UNIQUE,        -- set for BUILT-IN audiences; NULL for named groups
    name            TEXT NOT NULL,
    description     TEXT,

    kind            TEXT NOT NULL CHECK (kind IN ('builtin','group')),
    -- 'builtin' — evaluated as a RULE by the resolver. No membership rows exist.
    -- 'group'   — a stored, administered list in audience_member.

    resolver_key    TEXT,
    -- For built-ins, which rule the resolver applies. Set iff kind = 'builtin'.
    --   'everyone'         — any person, including non-members and the public
    --   'all_members'      — anyone with a current membership
    --   'unit_participants'— participants of the unit in scope_parameter
    --   'unit_leaders'     — holders of a leadership role in that unit
    --   'guardians_of'     — active guardians of the person in scope_parameter
    scope_parameter BIGINT,
    -- For the parameterised built-ins: which unit, or which person.

    is_system       BOOLEAN NOT NULL DEFAULT false,
    valid_from      DATE,
    valid_to        DATE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by      BIGINT REFERENCES person(id),

    CONSTRAINT ck_audience_kind CHECK (
        (kind = 'builtin') = (resolver_key IS NOT NULL)),
    CONSTRAINT ck_audience_group_has_code CHECK (
        kind <> 'group' OR code IS NULL)
);

CREATE UNIQUE INDEX uq_audience_code ON audience (code) WHERE code IS NOT NULL;
CREATE INDEX ix_audience_kind ON audience (kind);

CREATE TABLE audience_member (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    audience_id     BIGINT NOT NULL REFERENCES audience(id),
    person_id       BIGINT NOT NULL REFERENCES person(id),

    valid_from      DATE NOT NULL DEFAULT CURRENT_DATE,
    valid_to        DATE,
    added_by        BIGINT REFERENCES person(id),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT ck_audience_member_period CHECK (
        valid_to IS NULL OR valid_to > valid_from)
);

-- Only named groups have members. A built-in audience is a rule, so a row here
-- would be meaningless — and, worse, would look authoritative.
ALTER TABLE audience_member ADD CONSTRAINT ex_audience_member_no_overlap
    EXCLUDE USING gist (
        audience_id WITH =,
        person_id   WITH =,
        daterange(valid_from, valid_to, '[)') WITH &&
    );

CREATE INDEX ix_audience_member_audience ON audience_member (audience_id, valid_to);
CREATE INDEX ix_audience_member_person   ON audience_member (person_id, valid_to);
```

### Built-in audiences are rules, not lists — and that is the whole point

The distinction is the load-bearing one:

| | Built-in audience | Named group |
|---|---|---|
| **How evaluated** | A rule the resolver applies at check time | A stored list of `audience_member` rows |
| **When a person joins the unit** | They immediately receive what the unit granted — **automatically** | Nothing happens. Someone must add them. |
| **Maintenance** | None | The classic stale-group problem: nobody ever removes anyone |
| **Examples** | `everyone`, `all_members`, the participants of unit X, the guardians of person Y | "the summer camp kitchen crew" |

**Prefer built-ins.** A pack that grants `view` on its events to
`unit_participants` of itself gets the correct behaviour forever: next year's new members
inherit it, and people who leave stop being covered, with no rows to maintain. The same grant
to a *named group* silently rots the moment the roster changes.

Named groups exist because some sets genuinely are ad hoc — a camp kitchen crew is not a unit
and is not derivable from anything. They are the escape hatch, and they carry their known
cost.

### Evaluation

An audience grant is evaluated as part of the person's own permissions — the resolver
expands it, so a grant to an audience is checked *as if* the person held it directly:

```sql
-- Is this person covered by an audience grant applicable to this scope and level?
CREATE OR REPLACE FUNCTION audience_grant_applies(
    p_person_id BIGINT, p_scope_type TEXT, p_scope_id BIGINT,
    p_permission_id BIGINT, p_at DATE
) RETURNS BOOLEAN LANGUAGE sql STABLE AS $$
    SELECT EXISTS (
        SELECT 1
          FROM access_grant g
          JOIN audience a ON a.id = g.audience_id
          JOIN permission_level pl
            ON pl.permission_id = p_permission_id
           AND pl.scope_type = g.scope_type
          JOIN access_level req  ON req.level  = pl.required_level
          JOIN access_level have ON have.level = g.level
         WHERE g.scope_type = p_scope_type
           AND g.scope_id IS NOT DISTINCT FROM p_scope_id
           AND g.level <> 'revoked'
           AND g.revoked_at IS NULL
           AND g.valid_from <= p_at
           AND (g.valid_to IS NULL OR g.valid_to > p_at)
           AND have.rank >= req.rank
           AND person_in_audience(p_person_id, a.id, p_at)
    );
$$;
```

`person_in_audience()` is where the built-in rules live:

```sql
CREATE OR REPLACE FUNCTION person_in_audience(
    p_person_id BIGINT, p_audience_id BIGINT, p_at DATE
) RETURNS BOOLEAN LANGUAGE sql STABLE AS $$
    SELECT EXISTS (
        SELECT 1 FROM audience a
         WHERE a.id = p_audience_id
           AND (a.valid_to IS NULL OR a.valid_to > p_at)
           AND CASE a.resolver_key
               WHEN 'everyone'          THEN true
               WHEN 'all_members'       THEN is_current_member(p_person_id)
               WHEN 'unit_participants' THEN EXISTS (
                       SELECT 1 FROM unit_participation up
                        WHERE up.person_id   = p_person_id
                          AND up.org_unit_id = a.scope_parameter
                          AND up.valid_from <= p_at
                          AND (up.valid_to IS NULL OR up.valid_to > p_at))
               WHEN 'unit_leaders'      THEN EXISTS (
                       SELECT 1 FROM role_assignment ra
                        JOIN role r2 ON r2.id = ra.role_id
                        WHERE ra.person_id  = p_person_id
                          AND r2.is_leadership
                          AND ra.scope_type = 'org_unit'
                          AND ra.scope_id   = a.scope_parameter
                          AND ra.valid_from <= p_at
                          AND (ra.valid_to IS NULL OR ra.valid_to > p_at))
               WHEN 'guardians_of'      THEN EXISTS (
                       SELECT 1 FROM guardianship gd
                        WHERE gd.guardian_person_id  = p_person_id
                          AND gd.dependent_person_id = a.scope_parameter
                          -- a lapsed membership does not remove a guardian,
                          -- but an ENDED guardianship does
                          AND gd.valid_from <= p_at
                          AND (gd.valid_to IS NULL OR gd.valid_to > p_at))
               ELSE EXISTS (
                       SELECT 1 FROM audience_member am
                        WHERE am.audience_id = a.id
                          AND am.person_id   = p_person_id
                          AND am.valid_from <= p_at
                          AND (am.valid_to IS NULL OR am.valid_to > p_at))
               END
    );
$$;
```

**Note `unit_leaders` calls the resolver's role tables without itself being an authority
grant.** Membership in an audience confers nothing on its own — it only decides whether *this
grant*, which someone already created deliberately, reaches this person. A leader does not
become able to do anything by being in the `unit_leaders` audience; they become able to do
exactly what that grant says, on that item.

### What audiences do **not** do

- **They are not a permission.** Being in an audience is not authority; it is membership of a
  set. All authority still comes from a grant.
- **They do not replace `guardianship_permission`.** `guardians_of` lets a unit open something
  to a child's guardians; it does not let a guardian edit the child's record. That remains the
  guardianship channel.
- **They do not nest.** An audience cannot contain another audience — that is how you get
  evaluation cycles and answers nobody can predict.
- **`everyone` is genuinely everyone**, including people with no account and no membership.
  It is the right target for a public event page and the wrong one for anything else.

---

## 9. `access_log`

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
    -- FOR the subject (guardianship, delegation). See 04-relationships.md §6.

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

## 10. The resolver in SQL

### Helper functions used by the resolver

Two small helpers keep `can()` readable. Both are `STABLE`.

```sql
-- Does the person hold a grant ON THIS EXACT SCOPE whose level meets what the
-- permission requires at that scope kind? Exact match only — no inheritance.
-- Covers BOTH a personal grant and one made to an audience the person is in.
CREATE OR REPLACE FUNCTION grant_satisfies(
    p_person_id BIGINT, p_scope_type TEXT, p_scope_id BIGINT,
    p_permission_id BIGINT, p_at DATE
) RETURNS BOOLEAN LANGUAGE sql STABLE AS $$
    SELECT EXISTS (
        SELECT 1
          FROM access_grant g
          JOIN permission_level pl
            ON pl.permission_id = p_permission_id
           AND pl.scope_type = g.scope_type
          JOIN access_level req  ON req.level  = pl.required_level
          JOIN access_level have ON have.level = g.level
         WHERE g.scope_type = p_scope_type
           AND g.scope_id IS NOT DISTINCT FROM p_scope_id
           AND g.level <> 'revoked'          -- denies handled in channel 0
           AND g.revoked_at IS NULL
           AND g.valid_from <= p_at
           AND (g.valid_to IS NULL OR g.valid_to > p_at)
           AND have.rank >= req.rank
           -- the grantee: this person, or an audience containing them (§8)
           AND (g.person_id = p_person_id
                OR (g.audience_id IS NOT NULL
                    AND person_in_audience(p_person_id, g.audience_id, p_at)))
    );
$$;

-- Is this grant's level sufficient for the permission at this scope kind?
CREATE OR REPLACE FUNCTION level_satisfies(
    p_level TEXT, p_permission_id BIGINT, p_scope_type TEXT
) RETURNS BOOLEAN LANGUAGE sql STABLE AS $$
    SELECT COALESCE((
        SELECT have.rank >= req.rank
          FROM permission_level pl
          JOIN access_level req  ON req.level  = pl.required_level
          JOIN access_level have ON have.level = p_level
         WHERE pl.permission_id = p_permission_id
           AND pl.scope_type = p_scope_type
    ), false);
$$;

-- Is the assignment still live, and does an exposure at this unit cover it?
-- The exposure is the ONLY way authority crosses a unit boundary downward.
CREATE OR REPLACE FUNCTION scope_exposure_covers_assignment(
    p_org_unit_id BIGINT, p_role_assignment_id BIGINT, p_at DATE
) RETURNS BOOLEAN LANGUAGE sql STABLE AS $$
    SELECT EXISTS (
        SELECT 1 FROM scope_exposure se
         WHERE se.org_unit_id = p_org_unit_id
           AND se.role_assignment_id = p_role_assignment_id
           AND se.valid_to IS NULL
           AND se.withdrawn_at IS NULL
           AND se.valid_from <= p_at
    );
$$;

-- Does this person hold system.gate_exempt, and is the exemption itself still live?
-- (D-051.) Deliberately NOT expressed as can(...): can() applies the membership gate,
-- and the exemption exists to lift that gate. Calling can() here would make a lapsed
-- holder unable to hold the permission that says a lapse does not matter.
--
-- Read directly from role_assignment. An access_grant can never confer this:
-- system-namespace permissions are unreachable by the item channel, which is the
-- structural guarantee that an item grant cannot lift the gate.
CREATE OR REPLACE FUNCTION person_holds_gate_exempt(
    p_person_id BIGINT, p_at DATE DEFAULT CURRENT_DATE
) RETURNS BOOLEAN LANGUAGE sql STABLE AS $$
    SELECT EXISTS (
        SELECT 1
          FROM role_assignment ra
          JOIN role_permission rp ON rp.role_id = ra.role_id
          JOIN permission p2      ON p2.id = rp.permission_id
         WHERE ra.person_id = p_person_id
           AND ra.valid_from <= p_at
           AND (ra.valid_to IS NULL OR ra.valid_to > p_at)
           AND p2.code = 'system.gate_exempt'
           -- a delegated exemption must still be backed by a live source
           AND (ra.delegation_of IS NULL OR EXISTS (
                   SELECT 1 FROM role_assignment src
                    WHERE src.id = ra.delegation_of
                      AND src.valid_from <= p_at
                      AND (src.valid_to IS NULL OR src.valid_to > p_at)))
    );
$$;
```

The single authorization entry point. One implementation, used everywhere. Algorithm:
[../domain/06-authorization-model.md](../domain/06-authorization-model.md#6-the-resolver).

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

    -- CHANNEL 0: explicit deny. ABSOLUTE AND SCOPE-INDEPENDENT.
    --
    -- A 'revoked' grant applicable to this permission blocks access no matter
    -- WHAT scope it sits at. A per-event grant can never restore access that an
    -- organization-wide suspension removed. Locality orders ALLOWS (the tiering
    -- below); it never outranks a deny. See the authorization model, §7.1.
    --
    -- "Applicable" means: the deny's scope is the checked scope, an ancestor of
    -- the checked unit, organization-level, or the deny names this permission
    -- (or its resource's .admin).
    IF EXISTS (
        SELECT 1 FROM access_grant g
         WHERE g.level = 'revoked'
           AND g.revoked_at IS NULL
           AND g.valid_from <= p_at
           AND (g.valid_to IS NULL OR g.valid_to > p_at)
           -- A deny applies to this person if it names them, OR if it names an
           -- audience they are in (§8). A personal deny and an audience deny are
           -- equally absolute; a PERSONAL allow below cannot beat an AUDIENCE deny,
           -- because channel 0 has already returned.
           AND (g.person_id = p_person_id
                OR (g.audience_id IS NOT NULL
                    AND person_in_audience(p_person_id, g.audience_id, p_at)))
           AND (
                 -- organization-wide deny: applies everywhere
                 g.scope_type = 'organization'
                 -- deny on the exact thing being checked
              OR (p_scope_type IS NOT NULL
                  AND g.scope_type = p_scope_type AND g.scope_id = p_scope_id)
                 -- deny on a unit: applies to that unit and, since authority does
                 -- not flow down, ONLY that unit. No ancestor walk.
              OR (p_scope_type = 'org_unit' AND g.scope_type = 'org_unit'
                  AND g.scope_id = p_scope_id)
           )
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

    -- CHANNELS 3-5: ALLOWS, ORDERED BY LOCALITY (most specific first).
    --
    -- The first tier that yields a determination decides the effective level for
    -- this check. If that level is insufficient, fall through to the next tier.
    -- This is what "local permissions override global" means, and it applies to
    -- ALLOWS ONLY — denies were already resolved in channel 0.

    -- Resolve the units whose grants apply to this check:
    --   * the checked unit itself
    --   * any unit that has explicitly exposed its scope to a relevant assignment
    -- NOTE: no unit_ancestors() call anywhere in this function.

    -- TIER A — item grant on this exact scope (most specific).
    IF p_scope_type IS NOT NULL AND p_scope_id IS NOT NULL THEN
        IF grant_satisfies(p_person_id, p_scope_type, p_scope_id,
                           v_perm.id, p_at) THEN
            RETURN true;
        END IF;
    END IF;

    -- TIER B — unit grant: on this unit, or on a unit whose assignment this unit
    -- has exposed via scope_exposure.
    IF p_scope_type = 'org_unit' AND p_scope_id IS NOT NULL THEN
        IF grant_satisfies(p_person_id, 'org_unit', p_scope_id, v_perm.id, p_at)
           OR EXISTS (
                SELECT 1
                  FROM scope_exposure se
                  JOIN access_grant g
                    ON g.scope_type = 'org_unit' AND g.scope_id = se.org_unit_id
                 WHERE se.org_unit_id = p_scope_id
                   AND se.valid_to IS NULL AND se.withdrawn_at IS NULL
                   AND se.valid_from <= p_at
                   AND g.person_id = p_person_id
                   AND g.revoked_at IS NULL
                   AND g.valid_from <= p_at
                   AND (g.valid_to IS NULL OR g.valid_to > p_at)
                   AND level_satisfies(g.level, v_perm.id, 'org_unit')
                  -- the exposure must cover this very assignment
                   AND scope_exposure_covers_assignment(
                         se.org_unit_id, se.role_assignment_id, p_at)
                  AND se.role_assignment_id IN (
                        SELECT ra2.id FROM role_assignment ra2
                         WHERE ra2.person_id = p_person_id
                           AND ra2.valid_from <= p_at
                           AND (ra2.valid_to IS NULL OR ra2.valid_to > p_at))
           ) THEN
            RETURN true;
        END IF;
    END IF;

    -- TIER C — organization-scoped grant.
    IF grant_satisfies(p_person_id, 'organization', NULL, v_perm.id, p_at) THEN
        RETURN true;
    END IF;

    -- TIER D — roles: EXACT scope match, or a unit exposed to the assignment.
    -- No downward inheritance.
    --
    -- MEMBERSHIP GATE (D-039): a role grants anything only while the holder has a
    -- current membership, unless (a) the ROLE is marked requires_membership = false,
    -- or (b) the PERSON holds system.gate_exempt (D-051). Guardianship and ownership
    -- were already answered in channels 1 and 2 and are deliberately exempt.
    --
    -- (b) is resolved by DIRECT LOOKUP, not through can(). Routing it through the
    -- resolver would be circular: a lapsed holder of the exemption would be denied it
    -- by the very rule it exists to lift, and the lockout would have no error message.
    RETURN EXISTS (
        SELECT 1
          FROM role_assignment ra
          JOIN role r0             ON r0.id = ra.role_id
          JOIN role_permission rp  ON rp.role_id = ra.role_id
          JOIN permission p2       ON p2.id = rp.permission_id
         WHERE ra.person_id = p_person_id
           AND ra.valid_from <= p_at
           AND (ra.valid_to IS NULL OR ra.valid_to > p_at)
           -- NO check on the role's own period: a role is valid always, and the temporal
           -- question is the ASSIGNMENT's (D-053). The line above is the only place the
           -- role's lifetime would have been consulted, and it does not exist.
           AND (NOT r0.requires_membership                 -- (a) the carve-out
                OR is_current_member(p_person_id)          -- the gate
                OR person_holds_gate_exempt(p_person_id, p_at))  -- (b) D-051
           AND (
                 p2.code = p_permission_code
              -- NO '.admin' prefix-match branch. There are no per-resource admin
              -- permissions (D-068, reversing D-007); a role that can do everything
              -- about events lists all thirteen event.* codes explicitly.
              OR (v_perm.namespace IS NULL AND p2.code = 'system.admin')
           )
           AND (
                 -- organization-scoped assignment: applies only at org level
                 -- (system.admin excepted, below)
                 (ra.scope_type = 'organization'
                  AND (p2.code = 'system.admin' OR p_scope_type IS NULL
                       OR p_scope_type = 'organization'))
                 -- unit-scoped: the exact unit only, or a unit that exposed
                 -- its scope to THIS assignment
              OR (ra.scope_type = 'org_unit' AND p_scope_type = 'org_unit'
                  AND p_scope_id IS NOT NULL
                  AND (ra.scope_id = p_scope_id
                       OR EXISTS (
                            SELECT 1 FROM scope_exposure se
                             WHERE se.org_unit_id = p_scope_id
                               AND se.role_assignment_id = ra.id
                               AND se.valid_to IS NULL
                               AND se.withdrawn_at IS NULL
                               AND se.valid_from <= p_at)))
                 -- unscoped check ("can they do this anywhere?") — any live
                 -- assignment qualifies. For UI decisions only; never enforce
                 -- a mutation on an unscoped check.
              OR (p_scope_type IS NULL)
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

> **The membership gate is one clause, and it is the clause most likely to be "optimized"
> away.** `AND (NOT r0.requires_membership OR is_current_member(p_person_id) OR
> person_holds_gate_exempt(p_person_id, p_at))` is the whole of D-039 as amended by D-051.
> Removing any disjunct because "the join is expensive" reverses a decision taken
> deliberately, and nothing else in the schema would notice. If it becomes a measured
> performance problem, the fix is to cache `is_current_member()` — a single indexed lookup on
> `(person_id, status, valid_to)` — or to inline `person_holds_gate_exempt` as a join, not to
> drop a condition.
>
> **The third disjunct is the one that must never be routed through `can()`.** It is a plain
> read of `role_assignment`; going back through the resolver would mean asking the gate
> whether the gate applies, and a lapsed holder of `system.gate_exempt` would be denied the
> permission whose entire job is to say that a lapse does not matter. That is a lockout with
> no error message, on the one day of the year it would hurt most.

### Cache invalidation, revisited

The membership gate makes this harder than it was, and it must be built in from the start
(D-039):

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
-- The membership gate means a bulk expiry sweep must invalidate by PERSON, fast:
CREATE INDEX ix_permission_cache_person ON permission_cache (person_id);
```

Invalidated on any write to `role_assignment`, `access_grant`, `guardianship_permission`,
`role_permission`, `audience`, `audience_member`, a person merge — **and on every membership
transition, including the yearly expiry sweep, which touches every member at once.**

### Properties to verify when reviewing this function

1. **Deny is checked before everything**, including ownership. A suspended account's owner
   permissions are denied by a `revoked` grant if that is what the organization wants.
2. **Ownership short-circuits before roles.** A person's access to their own record does not
   depend on any grant, which is what makes the system usable by non-members.
3. **There is no wildcard except `system.admin`.** No prefix match, no implied capability.
   If a holder can do a thing, a row says so (D-068).
4. **`p_at` is threaded through every branch.** Permission checks are time-travel capable.
5. **Delegation sources are re-validated at check time**, closing the
   stale-delegation escalation.
6. **`resolve_person` is called on entry**, so a tombstoned person's id still resolves.
7. **A deny is scope-independent.** Channel 0 matches organization-level denies and
   same-scope denies, and does **not** walk ancestors — so a `revoked` grant at
   organization scope blocks every unit, which is what makes a suspension absolute.
8. **`unit_ancestors()` does not appear in this function.** Authority does not flow down.
   A unit's grants reach it only via exact match or an explicit `scope_exposure`. This is
   asserted by a test, not just a comment — integrity check 13.
9. **Locality orders allows only.** Tiers A→D are consulted in order and the first
   sufficient level wins; none of them can override channel 0.
10. **The membership gate applies to roles only, in tier D.** Ownership (channel 1) and
    guardianship (channel 2) return before it, which is what keeps a lapsed parent able to
    act for their child and a lapsed person able to see their own renewal screen. Item and
    unit grants are *not* gated — a grant someone deliberately made to an unpaid person is
    honoured, because it was an explicit act rather than an inherited role.
11. **Audience grants are evaluated through the same tiers as personal ones**, via
    `grant_satisfies()`. A grant to `everyone` and a grant to a named person differ only in
    how `grantee` is satisfied, never in how the level or the scope is resolved.

**A caveat on `p_scope_type IS NULL` in tier D.** An unscoped check ("can this person do
X anywhere?") returns true if *any* assignment grants it. That is correct for UI decisions
like "show the admin menu?" but **wrong for enforcement**. Every enforcing call must pass a
scope. Enforce this in the calling convention — make scope mandatory at the API layer for
mutating operations.

The cache definition and its invalidation rules are above, immediately after the resolver —
they are part of the resolver's contract, not a separate concern.

The person-merge case remains the easiest to forget —
see [01-identity.md](01-identity.md#8-identity_hypothesis-and-person_merge).

---

## 11. Integrity checks

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

-- 7b. People holding system.gate_exempt — everyone who keeps authority without a
--     current membership (D-051). Like check 7, this should be a very short list and
--     it should alert on change. It is a different list: check 7 catches who can
--     rewrite the system, this catches who keeps access while lapsed.
SELECT ra.person_id, p.family_name, p.given_name, r.code AS via_role,
       ra.valid_from, ra.valid_to
  FROM role_assignment ra
  JOIN role_permission rp ON rp.role_id = ra.role_id
  JOIN permission pe      ON pe.id = rp.permission_id AND pe.code = 'system.gate_exempt'
  JOIN role r             ON r.id = ra.role_id
  JOIN person p           ON p.id = ra.person_id
 WHERE ra.valid_from <= CURRENT_DATE
   AND (ra.valid_to IS NULL OR ra.valid_to > CURRENT_DATE);

-- 7c. The gate's own soundness check: nobody holds system.gate_exempt whose
--     assignment is itself being withheld by the gate. If this ever returns a row,
--     person_holds_gate_exempt() is being routed through can() somewhere and the
--     exemption has become unreachable for the person who needs it (D-051).
SELECT ra.id, ra.person_id
  FROM role_assignment ra
 WHERE NOT can(ra.person_id, 'system.gate_exempt', NULL, NULL, CURRENT_DATE, NULL)
   AND person_holds_gate_exempt(ra.person_id, CURRENT_DATE)
   AND NOT is_current_member(ra.person_id);

-- 8. Permissions in the dependent.* namespace that lack a permission_level row
SELECT p.code FROM permission p
 WHERE p.namespace = 'dependent'
   AND NOT EXISTS (SELECT 1 FROM permission_level pl WHERE pl.permission_id = p.id);

-- 9. SCOPE-AUTHORITY VIOLATION: an exposure naming a grantor that is NOT the unit
--    itself nor an ancestor of it. That shape would mean authority is being
--    claimed from a sibling or a descendant — never a legitimate exposure.
--
--    NOTE THE DIRECTION. It is CORRECT (not a violation) for an exposure to name
--    a district-scoped assignment, because the row is keyed on the troop and the
--    troop is doing the exposing — see domain/06-authorization-model.md §2.3. What
--    is forbidden is a row that reaches across, not one that reaches up.
--
--    This is the one legitimate use of unit_ancestors() in this document: checking
--    for violations, never resolving permissions.
SELECT se.id, se.org_unit_id, se.exposed_by, ra.scope_type, ra.scope_id
  FROM scope_exposure se
  JOIN role_assignment ra ON ra.id = se.role_assignment_id
 WHERE ra.scope_type = 'org_unit'
   AND ra.scope_id <> se.org_unit_id
   AND ra.scope_id NOT IN (SELECT id FROM unit_ancestors(se.org_unit_id));

-- 10. Exposures whose exposing person does not hold scope.expose at the covered unit.
--     There is no longer any exception to this: the bulk tool is removed (D-045),
--     so EVERY row must satisfy the predicate the trigger enforces. A result here
--     means the direction trigger was bypassed or a data fix was applied by hand.
SELECT se.id, se.org_unit_id, se.exposed_by, se.exposure_reason
  FROM scope_exposure se
 WHERE NOT can(se.exposed_by, 'scope.expose', 'org_unit', se.org_unit_id,
               se.valid_from, NULL);

-- 11. Exposures pointing at a role assignment that has since ended — harmless
--     (the resolver re-validates) but worth cleaning up
SELECT se.id FROM scope_exposure se
  JOIN role_assignment ra ON ra.id = se.role_assignment_id
 WHERE se.valid_to IS NULL AND se.withdrawn_at IS NULL
   AND ra.valid_to IS NOT NULL AND ra.valid_to <= CURRENT_DATE;

-- 12. Audience member rows on a BUILT-IN audience. Built-ins are rules, not lists
--     (§8); a stored member row would be meaningless and would look authoritative.
SELECT am.id, a.code, am.person_id
  FROM audience_member am
  JOIN audience a ON a.id = am.audience_id
 WHERE a.kind = 'builtin';

-- 13. Named groups with no members (probably abandoned, worth confirming)
SELECT a.id, a.name FROM audience a
 WHERE a.kind = 'group' AND a.valid_to IS NULL
   AND NOT EXISTS (SELECT 1 FROM audience_member am
                    WHERE am.audience_id = a.id AND am.valid_to IS NULL);

-- 14. TIME-BOMB for the resolver: any permission path that would inherit.
--     Schema-level assertion — fails if a future migration adds an inheriting
--     view or function. Run in CI, not nightly.
SELECT p.proname
  FROM pg_proc p JOIN pg_namespace n ON n.oid = p.pronamespace
 WHERE n.nspname = 'public'
   AND p.proname IN ('can', 'grant_satisfies', 'can_act_for_dependent')
   AND pg_get_functiondef(p.oid) LIKE '%unit_ancestors%';
-- EXPECTED: zero rows. A non-empty result means authority is flowing downward
-- through a permission path, which the design forbids.

-- 15. TIME-BOMB for the membership gate (D-039). CI assertion, same idea:
--     the resolver must still consult the gate, and roles must still be able to
--     opt out of it. If someone deletes the condition, this fails the build.
SELECT p.proname
  FROM pg_proc p JOIN pg_namespace n ON n.oid = p.pronamespace
 WHERE n.nspname = 'public'
   AND p.proname = 'can'
   AND (pg_get_functiondef(p.oid) NOT LIKE '%is_current_member%'
        OR pg_get_functiondef(p.oid) NOT LIKE '%requires_membership%');
-- EXPECTED: zero rows.

-- 16. ROLE DELETIONS. A role that has ever been assigned must not be deletable, and a
--     system role must never be deleted at all. The trigger on `role` enforces this; the
--     check exists because a restored dump or a manual `ALTER TABLE ... DISABLE TRIGGER`
--     bypasses it, and the loss is unrecoverable — the assignments are gone with the role.
SELECT ra.role_id, r.code,
       count(*) AS orphaned_assignments
  FROM role_assignment ra
  LEFT JOIN role r ON r.id = ra.role_id
 WHERE r.id IS NULL
 GROUP BY ra.role_id, r.code;
-- EXPECTED: zero rows.

-- 17. UNUSED ROLES. A role nobody holds is not an error — it is either a role the
--     organization is about to start using, or one it has stopped using and not deleted.
--     There is no third possibility, because a role has no period (D-053): it cannot be
--     switched off, only held or not held. Worth a glance before a catalog review.
SELECT r.code, r.name, r.created_at
  FROM role r
 WHERE NOT EXISTS (
     SELECT 1 FROM role_assignment ra
      WHERE ra.role_id = r.id
        AND (ra.valid_to IS NULL OR ra.valid_to > CURRENT_DATE))
   AND r.is_system = false
 ORDER BY r.created_at;
-- EXPECTED: unused, non-system roles. Delete the mistakes; keep the ones on the roadmap.

-- 18. ORPHANED PERMISSIONS — a capability no role grants. This check exists BECAUSE of
--     D-068: with no `.admin` wildcard, a permission that ought to be inside some role and
--     was never added to it is silently unusable, and there is no longer a resolver rule
--     that would have covered it by accident. This is the net the wildcard used to be.
SELECT p.code, p.resource, p.display_name
  FROM permission p
 WHERE p.is_assignable
   AND NOT EXISTS (SELECT 1 FROM role_permission rp
                    WHERE rp.permission_id = p.id)
 ORDER BY p.resource, p.code;
-- EXPECTED: empty after a seeding pass. A non-empty row means either a permission nobody
-- has bundled yet (fine on a roadmap, wrong in production) or a module was added and its
-- roles were not. NOTE what this CANNOT see: a permission granted to *a* role but not to
-- the role that arguably should have it. That residual is the accepted cost of D-068 and
-- no query closes it — it is a human reading §11's seed table against the catalog.

-- 19. TIME-BOMB for D-068: the `.admin` prefix match must STAY deleted. A reintroduced
--     wildcard re-creates implied capabilities for every resource, including ones added
--     after the day it was added back. CI assertion, same shape as 14 and 15.
SELECT p.proname
  FROM pg_proc p JOIN pg_namespace n ON n.oid = p.pronamespace
 WHERE n.nspname = 'public'
   AND p.proname IN ('can', 'grant_satisfies', 'can_act_for_dependent')
   AND pg_get_functiondef(p.oid) LIKE '%|| ''.admin''%';
-- EXPECTED: zero rows. Non-empty means an implied-capability rule is back.
SELECT count(*) AS wildcard_codes_present
  FROM permission WHERE action = 'admin'
   AND code NOT IN ('system.admin','dependent.admin',
                    'dependent.profile.admin','dependent.medical.admin',
                    'dependent.consent.admin');
-- EXPECTED: zero. The five listed survivors are deliberate and each is explained in the
-- catalog §1 ("three things named admin"). Anything else with action='admin' is a
-- re-created wildcard.
```

Checks 3, 7, 7b, 14 and 15 are the ones to wire to alerts.

- **Check 7b is the new one worth wiring to an alert.** Check 7 answers "who can rewrite the
  system?"; 7b answers "who keeps authority while lapsed?" — a shorter list with a different
  failure mode, and the one the membership gate introduces. Neither should ever grow quietly.
- **Check 7 should email someone every time its result changes** — a new `system_admin` is
  either a planned change or an incident, and either way someone should know within the hour.
- **Checks 14 and 15 are CI assertions, not reports.** They are the automated guards on the
  two rules most likely to be "simplified" away when someone optimizes the resolver: the
  no-inheritance rule and the membership gate. Both fail the build rather than silently
  changing who can do what.
- **Check 9 catches the direction being broken in the way the resolver cannot see.** A row
  that reaches sideways to a sibling unit, or down to a descendant, would be honoured
  happily by `can()` — nothing else in this list would notice it, and it is precisely the
  shape that lets authority be claimed from outside.
- **Checks 12 and 13 guard the audience model.** Built-ins must not accumulate member rows
  (they are rules), and an empty named group is usually an abandoned one.

---

## 12. Seed data — permissions

Starting catalog. Expect to edit this heavily; it is a proposal, not a specification.

> **This block and [../appendix/permission-catalog.md](../appendix/permission-catalog.md) are
> the same list written twice, and they drift.** When this was reconciled, **22 documented
> permissions had no `INSERT` row** — among them `unit_participation.view`, which **five** of
> the catalog's own seed roles assign, and `person.redact`, which is one of the two codes
> D-068 exists to protect. A further 12 were the `event.*` set, added to the catalog when
> events were designed and never carried here. **Under the old wildcard much of this was
> harmless**: a role holding `unit_participation.admin` reached the code whether or not the row
> existed, so the catalog could advertise a capability the database could not name and nothing
> noticed. The permission editor was the only place the gap showed. **[D-068](../decisions/decision-log.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle)
> removed that cushion.** Now a role that lists a code with no row either fails to insert or
> grants nothing, and integrity check 18 reads the *table*, so it cannot see that the catalog
> promised something the seed never contained.
>
> **There is no SQL check for this** — one side is a Markdown file. The discipline is the
> check: when adding a permission, add it in **both** places in the same edit, and treat a
> catalog row with no `INSERT` row as a bug of the same class as a missing migration. The
> reconciliation is mechanical enough to script if this file ever grows again:
>
> ```sql
> -- Run alongside a parse of permission-catalog.md column 1. Anything in the catalog and not
> -- here is a permission that cannot be granted; anything here and not there is an
> -- undocumented capability. Both were present in this document at the same time.
> SELECT code FROM permission ORDER BY code;
> ```

**Roles are data, and the organization administers them at runtime.** This section seeds the
*permissions* — the vocabulary of things anyone might do. The role names used throughout the
docs are worked examples of composing those permissions into groups, not a fixed list.
Creating a role, changing what it grants, assigning it and deleting an unused one
are all supported operations (`role.create`, `role.edit`, `role.assign`, `role.unassign`,
`role.delete`).

The consequence for this document: **it does not need to know which roles exist, and where it
names a role it is illustrating, not specifying.** In particular, *which* roles carry
`system.gate_exempt` is a configuration decision that belongs to the organization, not to the
specification.

> **What §12 must fix, and does, is the *shape*.** `system.gate_exempt` is a `system`-
> namespace permission: it can only arrive through a role, never through an item grant. That
> is not a configuration choice — it is the structural guarantee that an `access_grant` can
> never lift the membership gate. Whether the organization puts it in one role or five is its
> own business.

```sql
INSERT INTO permission (code, resource, action, namespace, display_name, description, is_system) VALUES
-- People
('person.view',              'person', 'view',   NULL, 'View people',            'See person records', true),
('person.create',            'person', 'create', NULL, 'Create people',          'Add a person record', true),
('person.edit',              'person', 'edit',   NULL, 'Edit people',            'Change person details', true),
('person.merge',             'person', 'merge',  NULL, 'Merge people',           'Confirm identity matches and merge', true),
('person.contact.view',      'person', 'contact.view', NULL, 'View contacts',   'See contact points', true),
('person.contact.edit',      'person', 'contact.edit', NULL, 'Edit contacts',   'Change contact points', true),
-- Irreversible, and deliberately separate codes. There is no `person.admin` that implies
-- them (D-068), so a role reaching them does so by listing them, visibly. `identity_reviewer`
-- holds person.merge; no seeded role holds person.redact.
('person.unmerge',           'person', 'unmerge',  NULL, 'Reverse a merge',    'Undo a confirmed merge', true),
('person.redact',            'person', 'redact',   NULL, 'Redact a person',    'GDPR-style erasure; keeps the financial skeleton', true),

-- Accounts
('account.view',   'account', 'view',   NULL, 'View accounts',  '', true),
('account.create', 'account', 'create', NULL, 'Create accounts','', true),
('account.suspend','account', 'suspend',NULL, 'Suspend accounts','', true),
('account.close','account', 'close',NULL, 'Close accounts','', true),
('account.credential.reset','account','credential.reset',NULL,'Reset credentials','', true),

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

-- Participation in sub-units (D-041). NOTE `unit_participation.view` is what the
-- registrar holds at ORG scope, and exact-match scope means it reads the root's own
-- participation rows, not a pack roster. That looks like a bug and is not (D-049).
('unit_participation.view',   'unit_participation', 'view',   NULL, 'View participation', 'See who takes part in a sub-unit', true),
('unit_participation.manage', 'unit_participation', 'manage', NULL, 'Manage participation', 'Add, move or end participation', true),

-- Organization
('org_unit.view',   'org_unit', 'view',   NULL, 'View units',   '', true),
('org_unit.create', 'org_unit', 'create', NULL, 'Create units', '', true),
('org_unit.edit',   'org_unit', 'edit',   NULL, 'Edit units',   '', true),
('org_unit.rename', 'org_unit', 'rename', NULL, 'Rename or renumber a unit','', true),
('org_unit.restructure','org_unit','restructure',NULL,'Restructure units','Split/merge, create successor units. NOT reparenting (D-036).', true),
('org_unit.close',  'org_unit', 'close',  NULL, 'Close a unit','', true),
-- Scope exposure: grants a higher-level role coverage over THIS unit.
-- Scoped to the unit being covered. A parent unit's officer cannot satisfy this
-- for a child unit, which is what makes the no-inheritance rule enforceable.
-- There is no bulk variant (D-045): every row is written by the unit it covers.
('scope.expose',    'scope',    'expose', NULL, 'Expose unit scope','Grant an external role authority over this unit', true),
('scope.exposure.review','scope','exposure.review',NULL,'Review scope exposures','See and revoke exposures over this unit', true),

-- Audiences (§8). Grants may target a set of people rather than one person.
('audience.view',   'audience', 'view',   NULL, 'View audiences',   'See built-in audiences and named groups', true),
('audience.manage', 'audience', 'manage', NULL, 'Manage named groups','Create and populate named groups', true),

-- Positions
('position.view',   'position', 'view',   NULL, 'View positions', '', true),
('position.assign', 'position', 'assign', NULL, 'Appoint to positions','', true),

-- Guardianship
('guardianship.view',   'guardianship', 'view',   NULL, 'View relationships','', true),
('guardianship.create', 'guardianship', 'create', NULL, 'Record guardianship','', true),
('guardianship.end','guardianship', 'end', NULL, 'End a guardianship',
 'The ONLY exit from a guardianship — nothing expires automatically (D-069). Note that the
 subject of the row cannot currently hold this; see open question E-5.', true),
('guardianship.permission.grant','guardianship','permission.grant',NULL,'Grant guardian permissions','', true),

-- Roles and permissions themselves
('role.view',        'role', 'view',  'system', 'View roles',        '', true),
('role.create',      'role', 'create','system', 'Create a role',     'Compose a new permission group', true),
('role.edit',        'role', 'edit',  'system', 'Edit roles',        'Takes effect immediately for every holder', true),
('role.delete',      'role', 'delete','system', 'Delete a role',     'Only if never assigned and not a system role', true),
('role.assign',      'role', 'assign','system', 'Assign roles',      '', true),
('role.unassign',    'role', 'unassign','system','End a role assignment',
 'The ONLY thing that ends authority, since a role has no period (D-053) and nothing forces
 an assignment to end (D-071).', true),
('permission.view',  'permission', 'view','system','View permissions','', true),
('permission.edit',  'permission', 'edit','system','Edit permissions','', true),
('access_grant.create','access_grant','create',NULL,'Create an item grant','', true),
('access_grant.revoke','access_grant','revoke',NULL,'Revoke an item grant','', true),
('system.admin',     'system', 'admin','system','System administrator','Full system control', true),
('system.gate_exempt','system','gate_exempt','system','Exempt from the membership gate',
 'Hold this and the membership gate never applies to you: every gated role you hold keeps '
 'granting whether or not your fee is current (D-051). system namespace, so it can only '
 'arrive through a role assignment — never through an item grant. Scope-independent by '
 'design: the gate is a property of the person, so the waiver has to be too.', true),

-- Audit. No audit.admin — per-resource admin codes were removed (D-068).
('audit.view',   'audit', 'view',  NULL, 'View audit log',   '', true),
('audit.export', 'audit', 'export',NULL, 'Export audit log', '', true),

-- Legacy import (D-056)
('import.view',  'import', 'view',  NULL, 'View import batches','', true),
('import.stage', 'import', 'stage', NULL, 'Stage an import','', true),
('import.apply', 'import', 'apply', NULL, 'Apply a staged import','', true),
('import.revert','import', 'revert',NULL, 'Revert an applied import','', true),

-- Reports. Only the coarse pair is seeded: whether reporting is per-report
-- (`report.finance.view`, `report.membership.view`, `report.safeguarding.view`) or one
-- `report.view` with row-level filtering is STILL OPEN (catalog §12), and the seed roles in
-- catalog §11 name the granular ones as an illustration of that unresolved choice. Do not
-- seed both shapes; pick one when reporting is designed.
('report.view',   'report', 'view',   NULL, 'Run standard reports','', true),
('report.export', 'report', 'export', NULL, 'Export report data','', true);

-- Events (data-model/08). Thirteen codes, no wildcard among them (D-068): a role that runs
-- events holds all thirteen explicitly. Full rationale in permission-catalog §8a.
INSERT INTO permission (code, resource, action, namespace, display_name, description, is_system) VALUES
('event.view',               'event', 'view',               NULL, 'View event', '', true),
('event.create',             'event', 'create',             NULL, 'Create event', '', true),
('event.edit',               'event', 'edit',               NULL, 'Edit event', 'Details, dates, capacity', true),
('event.cancel',             'event', 'cancel',             NULL, 'Cancel event', 'Keeps registrations; notifies nobody by itself (D-064)', true),
('event.organizer.manage',   'event', 'organizer.manage',   NULL, 'Manage organizers', 'The roster, not a grant (D-062)', true),
('event.register_self',      'event', 'register_self',      NULL, 'Register yourself', 'THIS is the eligibility rule (D-060)', true),
('event.register_other',     'event', 'register_other',     NULL, 'Register someone else', 'A minor, a walk-in, a substitute', true),
('event.manage_participants','event', 'manage_participants',NULL, 'Manage the roster', 'Add/remove registrations, work the waitlist', true),
('event.presence.mark',      'event', 'presence.mark',      NULL, 'Mark presence', 'One level BELOW manage_participants on purpose (EV-5)', true),
('event.answer.view',        'event', 'answer.view',        NULL, 'Read registrant answers', 'Health-adjacent; where D-061 lives', true),
('event.question.manage',    'event', 'question.manage',    NULL, 'Manage event questions', '', true),
('event.grant_access',       'event', 'grant_access',       NULL, 'Grant event access', 'Requires level admin', true),
('event.delete',             'event', 'delete',             NULL, 'Delete event', 'Only possible with no registrations', true);

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
('dependent.event.answer',    'dependent', 'event.answer',    'dependent', 'Answer event questions', 'On their behalf (D-061)', true),
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
    ('event','Event','event',true),          -- designed: data-model/08
    ('document','Document','document',true); -- document layer to be designed

-- Built-in audiences (§8). These are RULES the resolver evaluates, not lists —
-- no audience_member rows ever exist for them (integrity check 12).
-- The parameterised ones are seeded per instance, not once:
--   'unit_participants' / 'unit_leaders' — one row per unit that needs one, with
--                                          scope_parameter = that unit's id
--   'guardians_of'                       — one per dependent whose guardians need
--                                          a shared target
INSERT INTO audience (code, name, kind, resolver_key, is_system, description) VALUES
    ('everyone',    'Everyone',            'builtin', 'everyone',    true,
     'Any person, including non-members and the public'),
    ('all_members', 'All members',         'builtin', 'all_members', true,
     'Anyone with a current membership');

-- Parameterised built-ins, created as needed. Example: opening a unit's events to
-- its own participants and leaders — the case that replaced the bulk exposure tool.
INSERT INTO audience (code, name, kind, resolver_key, scope_parameter, is_system) VALUES
    ('unit:42:participants', 'Participants of unit 42', 'builtin', 'unit_participants', 42, true),
    ('unit:42:leaders',      'Leaders of unit 42',      'builtin', 'unit_leaders',      42, true);
```

> **`system.admin` is deliberately a single top-level permission**, not a
> per-resource one. Holding it satisfies everything, and check 7 in §11 alerts on its
> holders. Keeping the most dangerous capability concentrated and alarmed is safer than
> spreading equivalents of it across every resource.

---

## 13. Open issues

- The complete permission catalog and real role definitions (§12) — needs your input.
  Specifically: which roles are marked `requires_membership = false`. That flag is now the
  line between "a lapse silently removes this" and "it does not", and it needs a deliberate
  answer per role rather than a default.
- Whether `valid_to` should be mandatory for high-authority assignments (§4).
- Polymorphic `scope_id` vs a `grantable_item` supertable (§6) — a real fork.
- Which built-in audiences are needed beyond `everyone` and `all_members`, and whether the
  parameterised ones are seeded per instance or created on demand (§8).
- How long a `permission_cache` entry may live given the membership gate (§10) — the
  shorter the TTL, the smaller the window in which a lapse has not yet taken effect.
- Cache vs materialized effective-permission table (§10).
- Retention policy for `access_log` — legal input required.
- Whether `access_log` needs human annotation (recommend a separate table if so).

**Resolved and no longer open**, kept visible so the reasoning survives: the bulk exposure
tool (removed — D-045); whether permissions depend on membership status (yes, with three
carve-outs — D-039); background-check permissions (removed — D-043); and the
organization-wide-roles tension (§4), which is much reduced now that membership and the
registry live at the single root unit (D-035).

All tracked in [../open-questions.md](../open-questions.md).
