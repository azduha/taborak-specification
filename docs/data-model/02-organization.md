# Data Model — Organization Structure

`org_unit`, unit types, name history, restructuring, positions, and assignments.

Domain rationale: [../domain/04-organization-structure.md](../domain/04-organization-structure.md).

---

## 1. `org_unit_type`

```sql
CREATE TABLE org_unit_type (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    code            TEXT NOT NULL UNIQUE,      -- 'national','region','district','group','troop','pack'
    name            TEXT NOT NULL,
    description     TEXT,

    allows_children BOOLEAN NOT NULL DEFAULT false,
    allows_adults   BOOLEAN NOT NULL DEFAULT true,
    -- Validates that a child member is not placed in an administrative unit.
    -- Both may be true: many units contain children and the adults who lead them.

    is_leaf         BOOLEAN NOT NULL DEFAULT false,
    -- A troop/pack is a leaf: it may contain members but not sub-units.

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
deployment. See [../domain/04-organization-structure.md](../domain/04-organization-structure.md#1-units-are-a-configurable-tree).

**`allows_children`/`allows_adults` is the replacement for hardcoded type checks.** The
validation "a child member may not be a member of a region" reads this flag rather than
listing type codes in code.

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
    -- Nullable = top-level unit. Self-reference forms the tree.

    code            TEXT,
    -- Short human code, e.g. 'T12'. Not unique globally — two regions may both have a
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
```

**`ck_org_unit_closed` states the invariant explicitly:** a unit cannot be closed without
an end date. Without it you get closed units with `valid_to IS NULL`, which then appear in
"currently active units" queries forever.

**Why `code` is not globally unique.** Unit numbering restarts per region and has been
reused across decades. A global unique constraint would reject real historical data during
import. Uniqueness is scoped to the parent and to live rows.

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

**Renumbering is a rename, not a new unit.** "4th Troop" becoming "Troop 12" with the same
members is one `org_unit` row and two `org_unit_name` rows. Creating a new unit would
orphan all historical `unit_membership` rows and make "who was in Troop 12 in 1998?"
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

**Do not rewrite history on a split.** Members who moved to the new unit get a *new*
`unit_membership` row starting at the split date; their old row closes at the same date.
Rewriting the old row destroys "where was this child in 2003?" — see
[§8](#8-unit_membership-lives-in-03-membershipmd).

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

Reparenting a subtree must cascade to descendants' paths — a separate `AFTER UPDATE`
trigger, or (simpler and safer) a function that reparents and rewrites the subtree in one
transaction. **Reparenting is rare and dangerous; make it a single named procedure, not an
ad-hoc UPDATE.**

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

`unit_ancestors` is what the permission resolver calls for downward-inheriting roles. It
must be indexed and cached — see
[../domain/06-authorization-model.md](../domain/06-authorization-model.md#7-caching-and-invalidation).

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

    is_unique_per_unit BOOLEAN NOT NULL DEFAULT false,
    -- True for scoutmaster (one per troop), false for assistant_leader.

    is_leadership   BOOLEAN NOT NULL DEFAULT false,
    -- Flags positions that carry organizational authority. Used to drive the
    -- convenience workflow that also creates a role_assignment.

    requires_adult_membership BOOLEAN NOT NULL DEFAULT true,
    requires_background_check BOOLEAN NOT NULL DEFAULT false,
    min_age         INTEGER,

    sort_order      INTEGER NOT NULL DEFAULT 0,
    valid_from      DATE,
    valid_to        DATE,

    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT ck_position_period CHECK (valid_to IS NULL OR valid_from IS NULL
                                         OR valid_to > valid_from)
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

-- A unique position may be held by only one person at a time within a unit:
CREATE UNIQUE INDEX uq_position_unique_holder ON position_assignment
    (position_id, org_unit_id)
    WHERE valid_to IS NULL
      AND position_id IN (SELECT id FROM position WHERE is_unique_per_unit);
```

**Two things the schema cannot enforce, and must be handled elsewhere:**

**7.1 `requires_adult_membership` and `requires_background_check`.** These depend on
temporal state in other tables, so no FK or check constraint can express them. They are
application-level validations plus a periodic report:

```sql
-- Leaders who are not currently adult members (needs attention):
SELECT pa.id, p.family_name, p.given_name, ou.name AS unit, pos.title
  FROM position_assignment pa
  JOIN position pos ON pos.id = pa.position_id
  JOIN person   p   ON p.id  = pa.person_id
  JOIN org_unit ou  ON ou.id = pa.org_unit_id
 WHERE pos.requires_adult_membership
   AND pa.valid_to IS NULL
   AND NOT EXISTS (
       SELECT 1 FROM membership m
        JOIN membership_type mt ON mt.id = m.membership_type_id
        WHERE m.person_id = pa.person_id
          AND m.status = 'active' AND m.valid_to IS NULL
          AND mt.category = 'adult');

-- Leaders whose background check is missing or expiring:
SELECT pa.id, p.family_name, p.given_name, pa.valid_to AS check_expires
  FROM position_assignment pa
  JOIN position pos ON pos.id = pa.position_id
  JOIN person   p   ON p.id  = pa.person_id
  LEFT JOIN person_identifier bc
         ON bc.person_id = p.id AND bc.scheme = 'background_check'
 WHERE pos.requires_background_check
   AND pa.valid_to IS NULL
   AND (bc.id IS NULL OR bc.valid_to IS NULL OR bc.valid_to < CURRENT_DATE + 90);
```

> **A leader with an expired background check is a safeguarding risk, not a data-quality
> issue.** This report is one of the few that should run daily and alert, not weekly and
> report. See [../open-questions.md](../open-questions.md).

**7.2 The unique-holder index above is a partial index with a subquery — which PostgreSQL
does not allow in an index predicate.** Replace the subquery with either:

- a `is_unique_per_unit` column denormalised onto `position_assignment`, set by trigger; or
- a plain unique index on `(position_id, org_unit_id)` for a **separate** table of
  singleton positions; or
- a trigger that rejects a second concurrent holder, which is simplest:

```sql
CREATE OR REPLACE FUNCTION check_unique_position_holder() RETURNS TRIGGER
LANGUAGE plpgsql AS $$
DECLARE v_unique BOOLEAN;
BEGIN
    SELECT is_unique_per_unit INTO v_unique FROM position WHERE id = NEW.position_id;
    IF v_unique AND NEW.valid_to IS NULL AND EXISTS (
        SELECT 1 FROM position_assignment pa
         WHERE pa.position_id = NEW.position_id
           AND pa.org_unit_id  = NEW.org_unit_id
           AND pa.valid_to IS NULL
           AND pa.id <> COALESCE(NEW.id, 0))
    THEN
        RAISE EXCEPTION 'position % in unit % already has a current holder',
            NEW.position_id, NEW.org_unit_id;
    END IF;
    RETURN NEW;
END $$;
```

**Positions are not permissions.** Holding `scoutmaster` grants no system capability. The
association between a position and authority is made explicitly through `role_assignment`,
and `position.is_leadership` exists only so a workflow can offer to create both at once.
See [../domain/04-organization-structure.md](../domain/04-organization-structure.md#4-positions).

---

## 8. `unit_membership` lives in 03-membership.md

Membership of a unit is a separate table from membership of the organization, because they
have different lifetimes — a person may hold an organization membership while between
units, or belong to two units at once (an adult in both a troop and a district team).

See [03-membership.md](03-membership.md#5-unit_membership).

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

-- 5. A unit type with no nesting rules defined at all (probably an oversight,
--    since the trigger is permissive in that case)
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
```

Checks 3 and 4 are the important ones — they detect the denormalisation drifting, which
otherwise produces a system that displays one name and reports under another.

---

## 10. Seed data

The vocabulary is data, so it belongs in a migration:

```sql
INSERT INTO org_unit_type (code, name, allows_children, allows_adults, is_leaf, max_depth, sort_order) VALUES
    ('national', 'National Organization', false, true,  false, 0, 10),
    ('region',   'Region',                false, true,  false, 1, 20),
    ('district', 'District',              false, true,  false, 2, 30),
    ('group',    'Group',                 true,  true,  false, 3, 40),
    ('troop',    'Troop',                 true,  true,  true,  4, 50),
    ('pack',     'Pack',                  true,  true,  true,  4, 60);

INSERT INTO org_unit_type_rule (parent_type_id, child_type_id, is_required) VALUES
    ((SELECT id FROM org_unit_type WHERE code='national'),
     (SELECT id FROM org_unit_type WHERE code='region'),   true),
    ((SELECT id FROM org_unit_type WHERE code='region'),
     (SELECT id FROM org_unit_type WHERE code='district'), true),
    ((SELECT id FROM org_unit_type WHERE code='district'),
     (SELECT id FROM org_unit_type WHERE code='group'),    true),
    ((SELECT id FROM org_unit_type WHERE code='group'),
     (SELECT id FROM org_unit_type WHERE code='troop'),    true),
    ((SELECT id FROM org_unit_type WHERE code='group'),
     (SELECT id FROM org_unit_type WHERE code='pack'),     true),
    ((SELECT id FROM org_unit_type WHERE code='national'),
     (SELECT id FROM org_unit_type WHERE code='group'),    true);
    -- The last rule permits groups directly under national, which some
    -- organizations have for historical or special-purpose units.
```

> **This is a placeholder for your real structure.** Replace it once you tell me the actual
> unit types and nesting rules. The schema does not change; only these two `INSERT`s do.
> Tracked in [../open-questions.md](../open-questions.md).

---

## 11. Open issues

- The real unit type vocabulary and nesting rules (§10).
- Whether authority inherits downward through the hierarchy — affects
  `unit_ancestors` usage in the resolver.
- Whether units may be reparented retroactively (a troop reassigned to another district as
  of a past date). This is much harder than a forward reparent and needs a decision.
- Whether a person may hold positions in units of different types simultaneously.
- Whether `is_leadership` should automatically create a `role_assignment`, or only suggest it.
- Background-check validity period and whether it must alert daily.

All tracked in [../open-questions.md](../open-questions.md).
