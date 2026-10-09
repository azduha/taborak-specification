# Data Model — Organization Structure

`org_unit`, unit types, name history, restructuring, positions, and assignments.

Domain rationale: [../domain/04-organization-structure.md](../domain/04-organization-structure.md).

---

## 1. `org_unit_type`

```sql
CREATE TABLE org_unit_type (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    code            TEXT NOT NULL UNIQUE,      -- 'organization','pack','section','team', ...
    name            TEXT NOT NULL,
    description     TEXT,

    allows_minors   BOOLEAN NOT NULL DEFAULT true,
    -- SAFEGUARDING, not a membership rule. Membership is ageless (D-038); this flag
    -- lets the system refuse to place a minor in a unit that does not supervise them,
    -- without hardcoding which type codes those are.
    --
    -- There is no allows_adults sibling: no unit in this organization excludes adults,
    -- and the units that must contain adults (anything with a leadership position) say
    -- so through position eligibility instead. See §7.

    is_leaf         BOOLEAN NOT NULL DEFAULT false,
    -- A leaf may contain participants but not sub-units. A pack is usually a leaf,
    -- but not necessarily — nesting is arbitrary (D-035).

    max_depth       INTEGER,
    -- Maximum nesting depth for this type, relative to the root. Null = unconstrained.

    sort_order      INTEGER NOT NULL DEFAULT 0,
    valid_from      DATE,
    valid_to        DATE,
    -- Types are retired, not deleted: a 1995 'six' unit type must still resolve in
    -- historical queries.

    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT ck_unit_type_period CHECK (valid_to IS NULL OR valid_from IS NULL
                                          OR valid_to > valid_from)
);

CREATE INDEX ix_unit_type_current ON org_unit_type (code) WHERE valid_to IS NULL;
```

**Types are rows, not an enum**, so the vocabulary can change across decades without a
deployment. See [../domain/04-organization-structure.md](../domain/04-organization-structure.md#1-one-root-arbitrary-sub-units).

**`allows_minors` is the replacement for hardcoded type checks.** The validation "a minor may
not take part in the organization's legal-and-filing unit" reads this flag rather than listing
type codes in code. Note it constrains *participation* and *position assignment*, not
membership: a person of any age may be a member of the organization, because membership is
ageless and lives at the root ([D-038](../decisions/decision-log.md#d-038--membership-is-ageless)).

---

## 2. `org_unit_type_rule`

```sql
CREATE TABLE org_unit_type_rule (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    parent_type_id  BIGINT REFERENCES org_unit_type(id),
    -- NULL parent_type means "at the root" — i.e. this type may be a top-level unit.

    child_type_id   BIGINT NOT NULL REFERENCES org_unit_type(id),

    is_required     BOOLEAN NOT NULL DEFAULT false,
    -- True: a unit of child_type must have a parent of parent_type.
    -- False: permissive.

    max_children    INTEGER,
    -- Optional cap on how many children of this type a parent may have.

    valid_from      DATE,
    valid_to        DATE,

    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT ck_unit_rule_distinct CHECK (
        parent_type_id IS NULL OR parent_type_id <> child_type_id)
);

-- At most one live rule per (parent_type, child_type) pair. Note NULLs need
-- COALESCE: a plain unique index would permit duplicate root rules.
CREATE UNIQUE INDEX uq_unit_rule_pair
    ON org_unit_type_rule (COALESCE(parent_type_id, 0), child_type_id)
    WHERE valid_to IS NULL;
```

**Why a table rather than `CHECK` constraints or code.** Nesting rules in this
organization will change (a new level added, a type retired). A rule expressed in code is
invisible to the people configuring the organization and requires a deployment to change.
A rule in a table can be reviewed, exported, and audited.

**Enforcement note.** A `CHECK` cannot express "the parent's type must be permitted by a
rule", because it requires a lookup. Enforce with a trigger:

```sql
CREATE OR REPLACE FUNCTION check_unit_nesting() RETURNS TRIGGER
LANGUAGE plpgsql AS $$
DECLARE
    v_parent_type BIGINT;
    v_ok BOOLEAN;
BEGIN
    IF NEW.parent_unit_id IS NULL THEN
        SELECT EXISTS (
            SELECT 1 FROM org_unit_type_rule r
             WHERE r.parent_type_id IS NULL
               AND r.child_type_id = NEW.unit_type_id
               AND (r.valid_to IS NULL OR r.valid_to > CURRENT_DATE)
        ) INTO v_ok;
        -- Also permit types with no rules at all (permissive default):
        IF NOT v_ok AND EXISTS (SELECT 1 FROM org_unit_type_rule
                                 WHERE child_type_id = NEW.unit_type_id) THEN
            RAISE EXCEPTION 'unit type % may not exist at the root', NEW.unit_type_id;
        END IF;
        RETURN NEW;
    END IF;

    SELECT unit_type_id INTO v_parent_type
      FROM org_unit WHERE id = NEW.parent_unit_id;

    SELECT EXISTS (
        SELECT 1 FROM org_unit_type_rule r
         WHERE r.parent_type_id = v_parent_type
           AND r.child_type_id   = NEW.unit_type_id
           AND (r.valid_from IS NULL OR r.valid_from <= CURRENT_DATE)
           AND (r.valid_to   IS NULL OR r.valid_to   >  CURRENT_DATE)
    ) INTO v_ok;

    IF NOT v_ok AND EXISTS (
        SELECT 1 FROM org_unit_type_rule WHERE parent_type_id = v_parent_type
    ) THEN
        RAISE EXCEPTION 'unit type % may not be nested under unit type %',
            NEW.unit_type_id, v_parent_type;
    END IF;

    RETURN NEW;
END $$;

CREATE TRIGGER trg_org_unit_nesting
    BEFORE INSERT OR UPDATE OF parent_unit_id, unit_type_id ON org_unit
    FOR EACH ROW EXECUTE FUNCTION check_unit_nesting();
```

Note the permissive fallback: a type with **no** rules defined at all is unconstrained.
This matters during initial setup — the trigger must not block creating the first units
before the rules exist. It also means the rules are opt-in, and
[§9](#9-integrity-checks) verifies them.

---

## 3. `org_unit`

```sql
CREATE TABLE org_unit (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    public_id       UUID NOT NULL DEFAULT gen_random_uuid() UNIQUE,

    unit_type_id    BIGINT NOT NULL REFERENCES org_unit_type(id),
    parent_unit_id  BIGINT REFERENCES org_unit(id),
    -- Nullable ONLY for the single root unit (the organization itself). See the
    -- uq_org_unit_single_root index below, and D-035. Immutable once set — see the
    -- trg_org_unit_no_reparent trigger, and D-036.

    code            TEXT,
    -- Short human code, e.g. 'T12'. Not unique globally — two sub-units may both have a
    -- 'T1'. Unique per (parent, code) among live units, enforced below.

    name            TEXT NOT NULL,
    -- Current display name. DENORMALISED convenience. History is in org_unit_name (§4).
    -- Queries about the past MUST read org_unit_name, never this column.

    status          TEXT NOT NULL DEFAULT 'active'
                    CHECK (status IN ('proposed','active','merged','closed')),

    valid_from      DATE NOT NULL,
    valid_to        DATE,          -- NULL = still exists

    closed_reason_code TEXT,
    closed_note     TEXT,

    -- Denormalised for fast ancestor queries. Maintained by trigger, see §6.
    path            TEXT NOT NULL,
    depth           INTEGER NOT NULL,

    data_confidence TEXT NOT NULL DEFAULT 'high'
                    CHECK (data_confidence IN ('high','medium','low')),

    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by      BIGINT REFERENCES person(id),
    updated_at      TIMESTAMPTZ,
    updated_by      BIGINT REFERENCES person(id),
    import_batch_id BIGINT,

    CONSTRAINT ck_org_unit_period CHECK (valid_to IS NULL OR valid_to > valid_from),
    CONSTRAINT ck_org_unit_not_self_parent CHECK (parent_unit_id IS DISTINCT FROM id),
    CONSTRAINT ck_org_unit_closed CHECK (
        (status <> 'closed') OR valid_to IS NOT NULL)
);

CREATE INDEX ix_org_unit_parent ON org_unit (parent_unit_id);
CREATE INDEX ix_org_unit_type   ON org_unit (unit_type_id) WHERE valid_to IS NULL;
CREATE INDEX ix_org_unit_path   ON org_unit (path text_pattern_ops);
CREATE INDEX ix_org_unit_live   ON org_unit (id) WHERE valid_to IS NULL;

CREATE UNIQUE INDEX uq_org_unit_code_per_parent
    ON org_unit (COALESCE(parent_unit_id, 0), lower(code))
    WHERE code IS NOT NULL AND valid_to IS NULL;

-- Exactly one unit may exist at the root. The organization itself.
CREATE UNIQUE INDEX uq_org_unit_single_root ON org_unit ((true))
    WHERE parent_unit_id IS NULL;
```

**`uq_org_unit_single_root` is the whole of "there is one organization".** It is an index on
a constant expression filtered to root rows, so it permits at most one row with
`parent_unit_id IS NULL` — while ignoring `valid_to`, deliberately: even a closed root is
still *the* root. See [D-035](../decisions/decision-log.md#d-035--one-root-unit-all-sub-units-nest-arbitrarily-beneath-it).

**`ck_org_unit_closed` states the invariant explicitly:** a unit cannot be closed without
an end date. Without it you get closed units with `valid_to IS NULL`, which then appear in
"currently active units" queries forever.

**Why `code` is not globally unique.** Unit numbering restarts and has been reused across
decades, and with arbitrary nesting two sub-units under different parents will legitimately
both be "1". A global unique constraint would reject real historical data during import.
Uniqueness is scoped to the parent and to live rows.

### A unit never changes parent

`parent_unit_id` is **immutable**. This is not a convention — a trigger enforces it:

```sql
CREATE OR REPLACE FUNCTION prevent_unit_reparenting() RETURNS TRIGGER
LANGUAGE plpgsql AS $$
BEGIN
    IF OLD.parent_unit_id IS DISTINCT FROM NEW.parent_unit_id THEN
        RAISE EXCEPTION
            'org_unit.parent_unit_id is immutable (unit %): a unit that moves is a new '
            'unit — close this one and create its successor under the new parent, '
            'recording the lineage in org_unit_relationship',
            OLD.id;
    END IF;
    RETURN NEW;
END $$;

CREATE TRIGGER trg_org_unit_no_reparent
    BEFORE UPDATE OF parent_unit_id ON org_unit
    FOR EACH ROW EXECUTE FUNCTION prevent_unit_reparenting();
```

**Why this is worth a trigger rather than a rule in the application.** Reparenting is the
one edit that would silently rewrite history: it changes what every historical report means,
moves a unit in and out of every ancestor's scope, and invalidates the materialized `path`
for the whole subtree. None of those failures are visible at the moment of the edit. See
[D-036](../decisions/decision-log.md#d-036--units-cannot-be-reparented-a-unit-that-moves-is-a-new-unit).

**The consequence is a simplification, not a loss.** Because the parent never changes, the
`path`/`depth` denormalisation never needs a subtree cascade rewrite, and "who was in this
unit in 2001?" keeps answering the same thing forever.

**A genuine move is recorded as a succession**, and the people are moved across explicitly —
see `org_unit_relationship` in [§5](#5-org_unit_relationship--splits-mergers-succession).

---

## 4. `org_unit_name` — rename and renumber history

```sql
CREATE TABLE org_unit_name (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    org_unit_id     BIGINT NOT NULL REFERENCES org_unit(id),

    name            TEXT NOT NULL,
    code            TEXT,

    valid_from      DATE NOT NULL,
    valid_to        DATE,          -- NULL = current name

    change_reason   TEXT NOT NULL CHECK (change_reason IN
                        ('established','rename','renumber','reorganisation',
                         'correction','import')),
    change_note     TEXT,
    source          TEXT,          -- 'staff' | 'legacy_import'
    import_batch_id BIGINT,

    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by      BIGINT REFERENCES person(id),

    CONSTRAINT ck_org_unit_name_period CHECK (valid_to IS NULL OR valid_to > valid_from)
);

CREATE INDEX ix_org_unit_name_unit ON org_unit_name (org_unit_id, valid_from DESC);
CREATE UNIQUE INDEX uq_org_unit_name_open ON org_unit_name (org_unit_id)
    WHERE valid_to IS NULL;   -- exactly one current name
CREATE INDEX ix_org_unit_name_search ON org_unit_name (lower(name) text_pattern_ops);
```

**`uq_org_unit_name_open` guarantees exactly one current name per unit.** The
denormalised `org_unit.name` must always equal it — maintained by the trigger in §6.

**Renumbering is a rename, not a new unit.** "4th Pack" becoming "Pack 12" with the same
participants is one `org_unit` row and two `org_unit_name` rows. Creating a new unit would
orphan all historical `unit_participation` rows and make "who was in Pack 12 in 1998?"
unanswerable.

**`change_reason` distinguishes a correction from a rename.** A correction means the
record was wrong (a typo fixed in 2026 about a 1998 name); a rename means the world
changed. Only the latter is real history. Conflating them corrupts historical reporting.

---

## 5. `org_unit_relationship` — splits, mergers, succession

```sql
CREATE TABLE org_unit_relationship (
    id                  BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    source_unit_id      BIGINT NOT NULL REFERENCES org_unit(id),
    target_unit_id      BIGINT NOT NULL REFERENCES org_unit(id),

    relationship        TEXT NOT NULL CHECK (relationship IN
                            ('split_from','merged_into','successor_of','renamed_to')),
    -- Direction is source → target. 'split_from': target was created from source.
    -- 'merged_into': source was absorbed into target.

    effective_date      DATE NOT NULL,
    note                TEXT,
    source              TEXT,
    import_batch_id     BIGINT,

    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by          BIGINT REFERENCES person(id),

    CONSTRAINT ck_unit_rel_distinct CHECK (source_unit_id <> target_unit_id)
);

CREATE INDEX ix_unit_rel_source ON org_unit_relationship (source_unit_id);
CREATE INDEX ix_unit_rel_target ON org_unit_relationship (target_unit_id);
```

**This table exists so that historical lineage is answerable.** When Troop 12 splits into
Troop 12 and Troop 31, the question "was this 2003 member in the unit that is now Troop 31?"
requires following the relationship. Without it, the answer is only guessable from
overlapping member sets.

**Note it is not a tree.** A unit may have been split from one parent and merged into
another; the same pair may even have multiple relationships over time (split in 1998,
merged back in 2005). Hence `effective_date` and no uniqueness constraint beyond the pair.

**Do not rewrite history on a split.** Participants who moved to the new unit get a *new*
`unit_participation` row starting at the split date; their old row closes at the same date.
Rewriting the old row destroys "where was this child in 2003?" — see
[§8](#8-unit_participation-lives-in-03-membershipmd).

---

## 6. Hierarchy traversal

Two mechanisms, both maintained automatically.

### 6.1 Materialized path (fast ancestor/descendant queries)

`org_unit.path` holds a slash-delimited id path: `/1/7/42/103/`. `depth` is the number of
segments. Maintained by trigger:

```sql
CREATE OR REPLACE FUNCTION maintain_org_unit_path() RETURNS TRIGGER
LANGUAGE plpgsql AS $$
DECLARE
    v_parent_path TEXT;
    v_parent_depth INTEGER;
BEGIN
    IF NEW.parent_unit_id IS NULL THEN
        NEW.path  := '/' || NEW.id::text || '/';
        NEW.depth := 0;
    ELSE
        SELECT path, depth INTO v_parent_path, v_parent_depth
          FROM org_unit WHERE id = NEW.parent_unit_id;
        IF v_parent_path IS NULL THEN
            RAISE EXCEPTION 'parent unit % not found', NEW.parent_unit_id;
        END IF;
        NEW.path  := v_parent_path || NEW.id::text || '/';
        NEW.depth := v_parent_depth + 1;
    END IF;
    RETURN NEW;
END $$;

CREATE TRIGGER trg_org_unit_path
    BEFORE INSERT OR UPDATE OF parent_unit_id ON org_unit
    FOR EACH ROW EXECUTE FUNCTION maintain_org_unit_path();
```

**No subtree cascade is needed, ever.** Because `parent_unit_id` is immutable
([§3](#a-unit-never-changes-parent)), a unit's path is computed once at insert and never
rewritten. The `UPDATE OF parent_unit_id` in the trigger above is therefore defensive only —
the reparenting trigger rejects the change before this one runs.

This is the payoff of [D-036](../decisions/decision-log.md#d-036--units-cannot-be-reparented-a-unit-that-moves-is-a-new-unit):
the materialized path is a pure insert-time denormalisation, which is the only kind that
stays trustworthy without versioning.

### 6.2 Recursive CTE (correct regardless of path integrity)

```sql
-- All ancestors of a unit, nearest first:
CREATE OR REPLACE FUNCTION unit_ancestors(p_unit_id BIGINT)
RETURNS TABLE (id BIGINT, depth_from_start INTEGER)
LANGUAGE sql STABLE AS $$
    WITH RECURSIVE up AS (
        SELECT u.id, u.parent_unit_id, 0 AS d FROM org_unit u WHERE u.id = p_unit_id
        UNION ALL
        SELECT u.id, u.parent_unit_id, up.d + 1
          FROM org_unit u JOIN up ON u.id = up.parent_unit_id
    )
    SELECT id, d FROM up WHERE d > 0 ORDER BY d;
$$;

-- All descendants of a unit:
CREATE OR REPLACE FUNCTION unit_descendants(p_unit_id BIGINT)
RETURNS TABLE (id BIGINT, depth_from_start INTEGER)
LANGUAGE sql STABLE AS $$
    WITH RECURSIVE down AS (
        SELECT u.id, 0 AS d FROM org_unit u WHERE u.id = p_unit_id
        UNION ALL
        SELECT u.id, down.d + 1
          FROM org_unit u JOIN down ON u.parent_unit_id = down.id
    )
    SELECT id, d FROM down WHERE d > 0;
$$;
```

> **`unit_ancestors()` must NOT be used by the permission resolver.** Authority does not
> flow down the hierarchy. The resolver matches scopes exactly, plus explicit
> `scope_exposure` rows — see
> [../domain/06-authorization-model.md](../domain/06-authorization-model.md#2-scope-authority--no-downward-inheritance).
> `unit_ancestors()` is used for **reporting** ("everyone in this district"), for the
> path-consistency check below, and for the exposure-direction integrity check — never in a
> permission path. Integrity check 13 in
> [05-authorization.md](05-authorization.md#11-integrity-checks) asserts this in CI.

**Both mechanisms are kept.** The path is for set-based queries (`WHERE path LIKE '/1/7/%'`),
which is dramatically faster for "everyone in this district". The recursive CTE is the
authority when the path might be stale, and is used by the nightly consistency check:

```sql
-- Nightly: verify stored paths match the actual tree
SELECT u.id, u.path,
       (SELECT string_agg(a.id::text, '/' ORDER BY a.d DESC)
          FROM unit_ancestors(u.id) a) AS expected_ancestors
  FROM org_unit u
 WHERE u.parent_unit_id IS NOT NULL
   AND u.path <> '/' || (SELECT string_agg(x.id::text,'/' ORDER BY x.d DESC)
                           FROM (SELECT id, d FROM unit_ancestors(u.id)
                                 UNION ALL SELECT u.id, -1) x) || '/';
```

---

## 7. `position` and `position_assignment`

```sql
CREATE TABLE position (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    unit_type_id    BIGINT NOT NULL REFERENCES org_unit_type(id),
    -- A position is defined per unit TYPE, not per unit: every troop has a scoutmaster
    -- slot. The slot is instantiated implicitly by the unit existing.

    code            TEXT NOT NULL,
    title           TEXT NOT NULL,
    description     TEXT,

    max_holders     INTEGER,
    -- How many people may occupy this position in one unit at the same time.
    -- NULL = unlimited. 1 = a single holder (a scoutmaster).
    --
    -- The DEFAULT IS NULL, i.e. unlimited, because multiple occupancy is the
    -- normal case in this organization: a troop may have several assistant
    -- leaders, several quartermasters, several instructors. Single occupancy is
    -- the exception and must be declared by the position itself.
    --
    -- Note this is a limit a position declares about ITSELF. It is never imposed
    -- from outside the unit. See domain/06-authorization-model.md §2 for why
    -- authority over a unit's structure originates at the unit.

    is_leadership   BOOLEAN NOT NULL DEFAULT false,
    -- Flags positions that carry organizational authority. Used to drive the
    -- convenience workflow that also creates a role_assignment.

    requires_membership BOOLEAN NOT NULL DEFAULT true,
    -- What it says here is REPORTED, not enforced. The flag drives the "leaders whose
    -- membership has lapsed" worklist below. Whether holding the corresponding ROLE
    -- survives a lapse is a separate switch, role.requires_membership, and that one IS
    -- enforced by the permission resolver (D-039).
    --
    -- The two are deliberately not the same column: an adult volunteer commonly holds a
    -- position for years while their membership lapses and is renewed, and the
    -- organization wants to see that on a report without losing the volunteer's access.

    min_age         INTEGER,
    -- Position eligibility, a real constraint: a scoutmaster must be an adult. This is
    -- about the position, not about membership — membership is ageless (D-038).

    sort_order      INTEGER NOT NULL DEFAULT 0,
    valid_from      DATE,
    valid_to        DATE,

    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT ck_position_period CHECK (valid_to IS NULL OR valid_from IS NULL
                                         OR valid_to > valid_from),
    CONSTRAINT ck_position_max_holders CHECK (max_holders IS NULL OR max_holders >= 1)
);

CREATE UNIQUE INDEX uq_position_code_per_type
    ON position (unit_type_id, lower(code)) WHERE valid_to IS NULL;


CREATE TABLE position_assignment (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    position_id     BIGINT NOT NULL REFERENCES position(id),
    org_unit_id     BIGINT NOT NULL REFERENCES org_unit(id),
    -- The concrete unit. position.unit_type_id must match org_unit.unit_type_id —
    -- enforced by trigger, since a FK cannot express it.

    person_id       BIGINT NOT NULL REFERENCES person(id),

    valid_from      DATE NOT NULL,
    valid_to        DATE,          -- NULL = still in post

    is_primary      BOOLEAN NOT NULL DEFAULT true,
    -- Some people hold several positions; one is primary for display and contact.

    appointment_reference TEXT,
    ended_reason_code TEXT,
    ended_note      TEXT,

    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by      BIGINT REFERENCES person(id),
    updated_at      TIMESTAMPTZ,
    updated_by      BIGINT REFERENCES person(id),
    import_batch_id BIGINT,

    CONSTRAINT ck_position_assignment_period CHECK (
        valid_to IS NULL OR valid_to > valid_from)
);

CREATE INDEX ix_position_assignment_person ON position_assignment
    (person_id, valid_from DESC, valid_to);
CREATE INDEX ix_position_assignment_unit ON position_assignment (org_unit_id)
    WHERE valid_to IS NULL;
CREATE INDEX ix_position_assignment_pos ON position_assignment (position_id)
    WHERE valid_to IS NULL;

-- Where a position declares a holder limit, enforce it:
CREATE OR REPLACE FUNCTION check_position_holder_limit() RETURNS TRIGGER
LANGUAGE plpgsql AS $$
DECLARE
    v_max   INTEGER;
    v_count INTEGER;
BEGIN
    SELECT max_holders INTO v_max FROM position WHERE id = NEW.position_id;

    IF v_max IS NULL OR NEW.valid_to IS NOT NULL THEN
        RETURN NEW;                     -- unlimited, or a closed assignment
    END IF;

    SELECT count(*) INTO v_count
      FROM position_assignment pa
     WHERE pa.position_id = NEW.position_id
       AND pa.org_unit_id  = NEW.org_unit_id
       AND pa.valid_to IS NULL
       AND pa.id IS DISTINCT FROM NEW.id;

    IF v_count >= v_max THEN
        RAISE EXCEPTION
            'position % in unit % already has % current holder(s); limit is %',
            NEW.position_id, NEW.org_unit_id, v_count, v_max;
    END IF;

    RETURN NEW;
END $$;

CREATE TRIGGER trg_position_holder_limit
    BEFORE INSERT OR UPDATE OF position_id, org_unit_id, valid_to
    ON position_assignment
    FOR EACH ROW EXECUTE FUNCTION check_position_holder_limit();
```

**Why a trigger rather than a unique index.** The limit is `position.max_holders`, which
lives in another table, so an index predicate cannot express it — and a partial index
predicate may not contain a subquery in any case. The trigger is also the only form that
handles `max_holders > 1`.

**Note the absence of a uniqueness rule on the assignment triple.** There is deliberately
no `UNIQUE (person_id, position_id, org_unit_id)`: a person may hold the same position in
the same unit across *separate periods* (left in 2020, returned in 2024), which is
historical fact and must remain representable. Overlap is still prevented, directly on the
row:

```sql
ALTER TABLE position_assignment ADD CONSTRAINT ex_position_assignment_no_overlap
    EXCLUDE USING gist (
        person_id   WITH =,
        position_id WITH =,
        org_unit_id WITH =,
        daterange(valid_from, valid_to, '[)') WITH &&
    );
```

Without this, the same person could be double-counted as holder of the same position in the
same unit over overlapping dates — which would defeat the holder-limit trigger by consuming
two of the slots.

**What the schema cannot enforce, and must be handled elsewhere:**

**7.1 `requires_membership` and `min_age`.** Both depend on temporal state in other tables, so
no FK or check constraint can express them. They are application-level validations plus a
periodic report:

```sql
-- Position holders who are not currently paid-up members (needs attention, but is NOT
-- an access problem — see the note below):
SELECT pa.id, p.family_name, p.given_name, ou.name AS unit, pos.title
  FROM position_assignment pa
  JOIN position pos ON pos.id = pa.position_id
  JOIN person   p   ON p.id  = pa.person_id
  JOIN org_unit ou  ON ou.id = pa.org_unit_id
 WHERE pos.requires_membership
   AND pa.valid_to IS NULL
   AND NOT is_current_member(pa.person_id);

-- Position holders below the position's minimum age:
SELECT pa.id, p.family_name, p.given_name, pos.title, pos.min_age,
       p.birth_date, date_part('year', age(p.birth_date)) AS age_now
  FROM position_assignment pa
  JOIN position pos ON pos.id = pa.position_id
  JOIN person   p   ON p.id  = pa.person_id
 WHERE pos.min_age IS NOT NULL
   AND pa.valid_to IS NULL
   AND (p.birth_date IS NULL
        OR p.birth_date + make_interval(years => pos.min_age) > CURRENT_DATE);
```

> **An unpaid volunteer holding a position is a bookkeeping problem, not a
> safeguarding one.** The important consequences:
>
> - Note that `requires_membership` here is a *report*, while `role.requires_membership` is
>   *enforced* by the resolver ([D-039](../decisions/decision-log.md#d-039--member-permissions-require-a-current-paid-membership)).
>   The holder may lose their **system access** the moment the fee lapses, while still
>   legitimately holding the **position**. That asymmetry is intentional — see
>   [03-membership.md §6](03-membership.md#6-membership-and-the-authorization-system) — but
>   any role that exists to make a position work should almost certainly be defined with
>   `requires_membership = false`, or the volunteer loses access to the tools their position
>   needs.
> - **No background checks are recorded in this system at all**
>   ([D-043](../decisions/decision-log.md#d-043--no-background-checks-are-recorded-in-this-system)).
>   If the organization ever introduces them, the natural home is a dated record with an
>   `expires_at`, plus a `person_identifier` scheme — and it would warrant a daily alerting
>   report, because a lapsed clearance is a safeguarding matter rather than a data-quality
>   one.

**7.2 Holder limits are a per-position declaration, not a structural rule.** See the trigger
and `max_holders` above. The important consequences:

- **Multiple occupancy is the default.** `max_holders IS NULL` means unlimited, so a new
  position kind accepts several holders without anyone having to state it.
- **Single occupancy never arises from the hierarchy.** A parent unit cannot declare that a
  nested unit has one scoutmaster. The limit is a property the position carries, and the
  positions in a unit are that unit's own business.
- **An over-limit condition is a business error, not a crash.** Two people legitimately
  sharing a position during a handover is a normal transient state; resolution is either
  closing one assignment or raising the limit.


**Positions are not permissions.** Holding `scoutmaster` grants no system capability. The
association between a position and authority is made explicitly through `role_assignment`,
and `position.is_leadership` exists only so a workflow can offer to create both at once.
See [../domain/04-organization-structure.md](../domain/04-organization-structure.md#4-positions).

---

## 8. `unit_participation` lives in 03-membership.md

Taking part in a sub-unit is a separate table from membership of the organization, because
they have different lifetimes — a person may hold a membership while taking part in no
sub-unit at all, or take part in several at once.

The name matters: this is **participation**, not a second kind of membership
([D-041](../decisions/decision-log.md#d-041--belonging-to-a-sub-unit-is-a-participation-record-not-a-membership)).
Everyone registers and pays at the root; the sub-units hold rosters, not memberships.

See [03-membership.md](03-membership.md#5-unit_participation).

---

## 9. Integrity checks

```sql
-- 1. Stored path disagrees with actual tree (§6.2)
-- 2. A unit whose parent is closed but which is itself open
SELECT c.id, c.name, p.name AS parent FROM org_unit c
  JOIN org_unit p ON p.id = c.parent_unit_id
 WHERE c.valid_to IS NULL AND p.valid_to IS NOT NULL;

-- 3. Live units with no current name row (violates the denormalisation invariant)
SELECT u.id FROM org_unit u
 WHERE u.valid_to IS NULL
   AND NOT EXISTS (SELECT 1 FROM org_unit_name n
                    WHERE n.org_unit_id = u.id AND n.valid_to IS NULL);

-- 4. org_unit.name disagrees with org_unit_name
SELECT u.id, u.name, n.name FROM org_unit u
  JOIN org_unit_name n ON n.org_unit_id = u.id AND n.valid_to IS NULL
 WHERE u.name <> n.name;

-- 5. A unit type with no nesting rules defined at all (usually fine — nesting is
--    permissive by default and a new type starts unconstrained — but a type that has
--    been in use for years with no rules is probably an oversight worth reviewing)
SELECT t.* FROM org_unit_type t
 WHERE t.valid_to IS NULL
   AND NOT EXISTS (SELECT 1 FROM org_unit_type_rule r
                    WHERE r.child_type_id = t.id
                       OR r.parent_type_id = t.id);

-- 6. Position assignments whose position type does not match the unit's type
SELECT pa.id FROM position_assignment pa
  JOIN position pos ON pos.id = pa.position_id
  JOIN org_unit ou  ON ou.id = pa.org_unit_id
 WHERE pos.unit_type_id <> ou.unit_type_id;

-- 7. Units with a single child (often a data-entry error, sometimes real)
SELECT parent_unit_id, count(*) FROM org_unit
 WHERE valid_to IS NULL AND parent_unit_id IS NOT NULL
 GROUP BY parent_unit_id HAVING count(*) = 1;

-- 8. A placeholder for the CI assertion on the single-root invariant. The unique index
--    makes a second root impossible, so this queries the catalog and fails the build if
--    the index is ever dropped — the same pattern as the unit_ancestors assertion in
--    05-authorization.md §11.
SELECT NOT EXISTS (
    SELECT 1 FROM pg_indexes
     WHERE schemaname = current_schema()
       AND indexname  = 'uq_org_unit_single_root');
-- must return false.
```

Checks 3 and 4 are the important ones — they detect the denormalisation drifting, which
otherwise produces a system that displays one name and reports under another.

Check 8 is the structural guarantee rather than a data-quality report: with reparenting
prohibited ([§3](#a-unit-never-changes-parent)), the single-root index and the recursive
ancestor walk are the two things everything else in the authorization model assumes, and both
are worth asserting in CI rather than trusting.

---

## 10. Seed data

The vocabulary is data, so it belongs in a migration. Two parts: the single root, and
whatever sub-unit types the organization actually uses.

```sql
-- The root. Exactly one row may have parent_unit_id IS NULL (§3).
INSERT INTO org_unit_type (code, name, allows_minors, is_leaf, sort_order) VALUES
    ('organization', 'The Organization', false, false, 10);

INSERT INTO org_unit (unit_type_id, parent_unit_id, code, name, valid_from, path, depth)
SELECT t.id, NULL, 'ORG', 'The Organization', DATE '1970-01-01', '/', 0
  FROM org_unit_type t WHERE t.code = 'organization';

-- Sub-unit types. PLACEHOLDER — see the note below.
INSERT INTO org_unit_type (code, name, allows_minors, is_leaf, sort_order) VALUES
    ('pack',   'Pack',   true,  false, 20),
    ('group',  'Group',  true,  false, 30),
    ('team',   'Team',   true,  true,  40);
```

> **The sub-unit vocabulary is a placeholder and nothing else is.** `pack`/`group`/`team` is a
> guess at the three words your organization uses; the *shape* — one root, a handful of
> freely-nestable types beneath it — is settled
> ([D-035](../decisions/decision-log.md#d-035--one-root-unit-all-sub-units-nest-arbitrarily-beneath-it)).
> Note that **no nesting rules are seeded**, deliberately: nesting is permissive by default,
> so the organization can start using a new kind of group immediately and constrain it later
> if it turns out to want that. Tracked in
> [../open-questions.md](../open-questions.md#a-1-remainder--the-real-unit-type-vocabulary).

**Position definitions, by contrast, are a real starting set** and worth filling in — they
are what `position_assignment` hangs off, and `min_age` / `requires_membership` on them are
the eligibility rules the reports in §7.1 enforce.

---

## 11. Open issues

- The real sub-unit type vocabulary (§10). One root and arbitrary nesting are settled; the
  words are not.
- May the root **read** what happens in its sub-units, or must each sub-unit expose its
  scope first? The root owns the registry and the fees, so this is narrower than it was —
  it is about the sub-units' own events and rosters. See
  [../open-questions.md](../open-questions.md#c-1--may-the-root-see-what-happens-in-its-sub-units).
- Whether a person may hold positions in units of different types simultaneously.
- Whether `is_leadership` should automatically create a `role_assignment`, or only suggest it.
- Whether `allows_minors` should also constrain `position_assignment`, or only
  `unit_participation` — currently it is specified for participation and the position side
  relies on `position.min_age` instead (a minor could in principle hold a position defined
  with `min_age IS NULL` in a unit that excludes minors).

**Resolved and no longer open**, kept visible so the reasoning survives: the organizational
structure itself (one root, arbitrary nesting — D-035); retroactive reparenting (prohibited
outright, and enforced by trigger — D-036); organization-wide operational roles (largely
dissolved by D-035, since the root owns the registry and the fees); and background checks
(none are recorded — D-043).

All tracked in [../open-questions.md](../open-questions.md).
