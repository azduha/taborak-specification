# Data Model Conventions

Read this before reviewing any DDL in this folder. Every table follows the patterns
here, and the patterns are load-bearing — deviating from them in one table creates bugs
that only appear across decades of history.

---

## 1. Target platform

*Assumption:* **PostgreSQL 14+**. The design relies on:

- `daterange` / `tstzrange` types and `&&` overlap operators — for the "no overlapping
  periods" invariants that the whole temporal model depends on.
- `EXCLUDE USING gist` constraints — the only clean way to enforce those invariants.
- `btree_gist` extension — required for the exclusion constraints.
- `jsonb` — for match signals, audit diffs, and other semi-structured payloads.
- Recursive CTEs — for the unit hierarchy.
- Native `ENUM` types *avoided* (see §5).

If the target is MySQL/MariaDB, the exclusion constraints become triggers plus periodic
consistency reports; that is a materially weaker guarantee and should be recorded as an
accepted risk in [../decisions/decision-log.md](../decisions/decision-log.md).

---

## 2. Naming

| Object | Convention | Example |
|--------|-----------|---------|
| Table | `snake_case`, **singular** | `person`, `membership_request` |
| Column | `snake_case` | `valid_from`, `person_id` |
| Primary key | `id` | always the same name, so joins read uniformly |
| Foreign key | `<referenced_table_singular>_id` | `person_id` → `person.id` |
| Boolean | `is_` / `has_` / `requires_` prefix | `is_primary`, `has_account` |
| Timestamp | `<verb>_at` | `created_at`, `verified_at` |
| Date/period | `valid_from` / `valid_to` | never `start_date`/`end_date` |
| Junction table | `<a>_<b>` in alphabetical order | `role_permission`, not `permission_role` |
| View | `v_<name>` | `v_active_member` |
| Index | `ix_<table>_<cols>` | `ix_membership_person_period` |
| Constraint | `ck_` / `fk_` / `uq_` / `ex_` prefix | `ex_membership_no_overlap` |

There is no `deleted_at` column. Deletion is handled by temporal closure and tombstones,
never by a soft-delete flag — see §4.

---

## 3. Primary keys

**Every table has a surrogate `id`.** No natural keys as primary keys, ever.

Rationale specific to this project: natural keys here are things like names, old member
numbers, and email addresses — all of which **change**, **repeat**, and **get corrected**.
A name is not unique (and was less so in 1994). An email address is reused by providers
and reassigned between people. A legacy member number may be absent, or duplicated across
two source systems.

```
id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY
```

`BIGINT` rather than `INT` because this system accumulates rows for decades and the
polymorphic `access_grant.scope_id` must never have its ids reused.

**Exception:** `person.public_id` — a separate `UUID` column for external exposure.

Rationale: `access_grant.scope_id` is a bare bigint with no foreign key, and ids appear in
URLs and exports. Sequential ids leak record counts and — more seriously — let someone
enumerate `/person/1001`, `/person/1002` and discover members. Expose `public_id` in all
external interfaces; keep `id` internal.

---

## 4. Deletion policy

**Nothing is hard-deleted.** There is no `deleted_at` and no `DELETE` for business data.

| Situation | Mechanism |
|-----------|-----------|
| A period ended | Set `valid_to` |
| A person left the organization | Close their membership; the person row remains |
| A grant revoked | Set `access_grant.valid_to`; keep the row |
| Two people merged | Tombstone: set `merged_into_person_id`; row remains |
| A unit closed | Set `org_unit.valid_to` and `status = 'closed'` |
| GPDR-style erasure requested | **Redact** field values; do not delete rows — see §8 |

This is not nostalgia. Historical foreign keys — "who attended this camp in 2003" — must
resolve forever. A hard delete breaks the audit trail and, in a youth organization, the
safeguarding record.

**The one exception:** staging tables (`staging_import*`) may be truncated after a batch is
applied, subject to the project's retention policy.

---

## 5. Enumerations

**Use `TEXT` with a `CHECK` constraint, not the native `ENUM` type.**

```sql
status TEXT NOT NULL CHECK (status IN ('draft', 'submitted', 'approved'))
```

Why, given that native enums are more compact:

- Adding a value to a native enum is easy; **removing or reordering** one is painful, and
  over a 40-year lifespan a status vocabulary *will* be revised.
- Native enum ordering is baked in, and the order of states here is meaningful (see below).
- `CHECK` constraints are visible in `information_schema` and in every migration tool,
  which makes review and diffing straightforward.

### Critical rule: status strings are ordered

Several status columns have a **meaningful progression**, and code must compare by rank,
never by string. A `CHECK` on the value list does not capture rank, so **also add a lookup
table** wherever rank matters:

```sql
CREATE TABLE access_level (
    level       TEXT PRIMARY KEY,      -- 'revoked','view','contribute','manage','admin'
    rank        INTEGER NOT NULL UNIQUE,
    description TEXT NOT NULL
);
INSERT INTO access_level VALUES
    ('revoked',    0, 'Explicitly denied; overrides all grants'),
    ('view',      10, 'Read only'),
    ('contribute',20, 'Read and add'),
    ('manage',    30, 'Full control of the item'),
    ('admin',     40, 'Full control including granting access');
```

Then `WHERE l.rank >= (SELECT rank FROM access_level WHERE level = 'manage')`. **Never**
compare level strings lexicographically — doing so silently inverts the ordering of
`admin` and `contribute` (`'admin' < 'contribute'` alphabetically), which is a security bug
that produces no error.

---

## 6. The temporal pattern

The pattern behind every period in this system.

```sql
CREATE TABLE example (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    person_id   BIGINT NOT NULL REFERENCES person(id),

    valid_from  DATE        NOT NULL,
    valid_to    DATE,                          -- NULL = still true
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT ck_example_period CHECK (valid_to IS NULL OR valid_to > valid_from),
    CONSTRAINT ex_example_no_overlap EXCLUDE USING gist (
        person_id WITH =,
        daterange(valid_from, valid_to, '[)') WITH &&
    )
);
```

### The four rules

1. **`valid_to IS NULL` means "still true".** Not a far-future sentinel date. A sentinel
   like `'9999-12-31'` looks convenient and breaks every `IS NULL` check, every range
   query, and every "currently active" index. Do not use one.
2. **Ranges are half-open `[valid_from, valid_to)`.** A membership ending 2010-06-30 and
   another starting 2010-06-30 do not overlap. Closed intervals make adjacent periods
   collide, and you will spend a day debugging it.
3. **Overlap is prevented by an exclusion constraint**, not by application code. An
   import script, a manual SQL fix, or a future API will bypass application validation.
   The database is the only place the invariant can be trusted.
4. **`created_at` is audit time, not world time.** It is distinct from `valid_from` — a
   membership backdated to 1990 during a 2026 import has `valid_from = 1990-09-01` and
   `created_at = 2026-…`. Never conflate them, and never derive one from the other.

### Why `daterange` and not a pair of timestamps

A `DATE` granularity is correct here: memberships, guardianships, and unit assignments
start and end on days, not seconds. Using `TIMESTAMPTZ` invites timezone-dependent
boundary bugs on things like "was this person a member on 1 June?".

Where sub-day precision genuinely matters (session validity, delegation during a specific
meeting), the column pair becomes `TIMESTAMPTZ` and the exclusion uses `tstzrange`. Both
patterns exist; each table documents which it uses.

### Indexing the pattern

```sql
CREATE INDEX ix_example_person_period
    ON example (person_id, valid_from DESC, valid_to);

CREATE INDEX ix_example_open
    ON example (person_id)
    WHERE valid_to IS NULL;
```

The partial index on open rows is the one that carries the load — "currently active" is
the overwhelmingly common query, and it stays small because open rows are a small fraction
of history.

---

## 7. Standard columns

Every business table carries:

| Column | Type | Purpose |
|--------|------|---------|
| `id` | `BIGINT IDENTITY` | Surrogate key |
| `created_at` | `TIMESTAMPTZ NOT NULL DEFAULT now()` | Audit time of insert |
| `created_by` | `BIGINT REFERENCES person(id)` | Who inserted. NULL for system/import jobs. |
| `updated_at` | `TIMESTAMPTZ` | Audit time of last change (via trigger) |
| `updated_by` | `BIGINT REFERENCES person(id)` | Who last changed it |
| `import_batch_id` | `BIGINT REFERENCES import_batch(id)` | Nullable; set on imported rows |

Temporal tables additionally carry `valid_from` / `valid_to`.

Tables that record a *decision about a person* (terminations, rejections, rejections of
identity hypotheses) additionally carry a reason:

| Column | Type |
|--------|------|
| `<verb>_reason_code` | `TEXT REFERENCES reason_code(code)` |
| `<verb>_reason_note` | `TEXT` — free text, for the human explanation |

**Reason codes are a lookup table, not free text.** "Why was this membership terminated?"
must be reportable and comparable across years. Free text is not.

---

## 8. Personal data and erasure

This schema holds data about **children**, which raises the stakes on every decision here.

Requirements the design must satisfy:

1. **A deletion request must not destroy the audit trail.** Implement as **redaction**:
   set `person.redacted_at`, overwrite names and contact points with a redaction marker,
   and keep the row and its ids so historical references still resolve. The person is no
   longer identifiable; the record that *someone* was in Troop 12 in 2003 survives.
2. **Redaction must cascade** to contact points, identifiers, and free-text notes that may
   contain personal data. A `redaction_log` records what was redacted and when.
3. **Some data must not be redacted** — membership periods, unit memberships, and position
   assignments are organizational history rather than personal data, and removing them
   would falsify records that the organization is often obliged to keep.
4. **Health and safeguarding records have separate retention rules** and are out of scope
   for this document, but the `person.redacted_at` flag must be visible to them.
5. **Sensitive attributes should not be over-collected.** `person.gender` is included
   because Scouting-type organizations typically must report it; if yours does not, remove
   the column rather than keeping it "just in case".

> Legal review is required before implementing §8. This section describes the technical
> mechanism, not the compliance policy. Tracked in
> [../open-questions.md](../open-questions.md).

---

## 9. Referential integrity rules

| Rule | Rationale |
|------|-----------|
| All FKs are `ON DELETE RESTRICT` | Nothing cascades. A person cannot be deleted while memberships reference them. |
| No `ON DELETE CASCADE` anywhere | Cascade delete is the enemy of a 40-year audit trail. |
| Nullable FKs document *why* they are nullable | In a comment. A nullable FK is usually a design decision worth recording. |
| `access_grant.scope_id` is the **one** FK-less column | It is polymorphic by design; see [../domain/06-authorization-model.md](../domain/06-authorization-model.md#5-access-grants--the-per-item-layer). |
| Circular FKs are resolved with a deferred constraint or a nullable column | `membership_request.membership_id` ↔ `membership.joined_via_request_id` is the one instance. |

---

## 10. Migration discipline

- **Every migration is reversible** or explicitly marked irreversible with a rationale.
  A migration that drops a column holding historical data is irreversible by definition.
- **Never rewrite a historical row's meaning.** Adding a column is fine; changing what an
  existing value means is a data migration that needs its own review.
- **Backfills are separate from schema changes**, in their own migration, so a failed
  backfill does not roll back a schema change and vice versa.
- **Seed data for lookups** (`access_level`, `permission`, `org_unit_type`,
  `reason_code`) lives in migrations, not in application startup code, so that the
  vocabulary is versioned with the schema.

---

## 11. Where the DDL lives

| Document | Tables |
|----------|--------|
| [01-identity.md](01-identity.md) | `person`, `person_name`, `account`, `account_credential`, `person_contact`, `person_identifier`, `identity_hypothesis`, `person_merge` |
| [02-organization.md](02-organization.md) | `org_unit`, `org_unit_type`, `org_unit_name`, `org_unit_relationship`, `position`, `position_assignment` |
| [03-membership.md](03-membership.md) | `membership`, `membership_type`, `membership_request`, `unit_participation` |
| [04-relationships.md](04-relationships.md) | `guardianship`, `guardianship_permission` |
| [05-authorization.md](05-authorization.md) | `permission`, `role`, `role_permission`, `role_assignment`, `access_grant`, `permission_level`, `access_log` |
| [06-audit-and-import.md](06-audit-and-import.md) | `audit_log`, `field_conflict`, `import_batch`, `staging_import*` |
| [07-finance.md](07-finance.md) | `fee_schedule`, `fee_obligation`, `payment` — **provisional** |
| [08-events.md](08-events.md) | `event`, `event_organizer`, `event_registration`, `event_question`, `event_answer` |

DDL is presented in **dependency order**: a table appears only after everything it
references.
