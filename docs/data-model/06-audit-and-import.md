# Data Model — Audit and Import

`audit_log`, `import_batch`, staging tables, and the redaction log.

`access_log` (the authorization audit trail) is in
[05-authorization.md](05-authorization.md#7-access_log). This document covers the
data-change audit trail, the legacy import pipeline, and erasure.

---

## 1. Two audit trails, and why both

| | `access_log` | `audit_log` |
|---|---|---|
| Records | Who did what, and by what authority | What a row's field values were before and after |
| Answers | "Who accessed this child's medical record, and were they allowed to?" | "When did this person's address change, and who changed it?" |
| Volume | Very high | High |
| Trigger | Application-level, on every permission check and action | Database trigger, on every write to audited tables |

Keeping them separate is deliberate. They have different retention needs, different query
patterns, and different access permissions. Merging them produces a table that is too
large to query and too sensitive to expose to anyone who needs one half of it.

---

## 2. `audit_log`

```sql
CREATE TABLE audit_log (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    occurred_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    transaction_id  BIGINT NOT NULL DEFAULT txid_current(),
    -- Groups all changes made in one transaction, so a multi-table operation
    -- (approve a request → create a membership → open a unit membership) reads
    -- as one event rather than three unrelated ones.

    actor_person_id BIGINT REFERENCES person(id),
    -- From the session variable app.current_person_id. NULL for migrations,
    -- imports, and batch jobs.

    actor_label     TEXT,
    -- 'system', 'migration:0042', 'import_batch:17' — for changes with no person
    -- actor. Otherwise a forensic gap.

    operation       TEXT NOT NULL CHECK (operation IN ('insert','update','delete')),
    table_name      TEXT NOT NULL,
    record_id       BIGINT NOT NULL,

    changed_fields  TEXT[],
    -- Which columns changed. Enables targeted history queries without parsing JSON.

    old_values      JSONB,
    new_values      JSONB,
    -- REDACTED before insert. See §2.2.

    on_behalf_of    BIGINT REFERENCES person(id),
    -- Set when the actor was acting for another person. Mirrors
    -- access_log.on_behalf. See 04-relationships.md §5.

    session_id      TEXT,
    ip_address      INET,
    request_id      TEXT
);

CREATE INDEX ix_audit_record  ON audit_log (table_name, record_id, occurred_at DESC);
CREATE INDEX ix_audit_actor   ON audit_log (actor_person_id, occurred_at DESC);
CREATE INDEX ix_audit_tx      ON audit_log (transaction_id);
CREATE INDEX ix_audit_time    ON audit_log (occurred_at DESC);
CREATE INDEX ix_audit_changed ON audit_log USING gin (changed_fields);
```

### 2.1 The trigger

```sql
CREATE OR REPLACE FUNCTION audit_trigger() RETURNS TRIGGER
LANGUAGE plpgsql AS $$
DECLARE
    v_old       JSONB;
    v_new       JSONB;
    v_changed   TEXT[];
    v_actor     BIGINT;
    v_behalf    BIGINT;
BEGIN
    v_actor  := NULLIF(current_setting('app.current_person_id', true), '')::BIGINT;
    v_behalf := NULLIF(current_setting('app.on_behalf_of', true), '')::BIGINT;

    IF TG_OP = 'INSERT' THEN
        v_new := to_jsonb(NEW);
    ELSIF TG_OP = 'UPDATE' THEN
        v_old := to_jsonb(OLD);
        v_new := to_jsonb(NEW);
        SELECT array_agg(key ORDER BY key) INTO v_changed
          FROM jsonb_each(v_new) n
          JOIN jsonb_each(v_old) o USING (key)
         WHERE n.value IS DISTINCT FROM o.value;
        IF v_changed IS NULL THEN
            RETURN NEW;      -- nothing actually changed; do not log noise
        END IF;
    ELSE
        v_old := to_jsonb(OLD);
    END IF;

    -- Redact before writing. Never store sensitive values in the audit trail.
    v_old := redact_audit_values(TG_TABLE_NAME, v_old);
    v_new := redact_audit_values(TG_TABLE_NAME, v_new);

    INSERT INTO audit_log (
        actor_person_id, on_behalf_of, operation, table_name, record_id,
        changed_fields, old_values, new_values, session_id, ip_address, request_id
    ) VALUES (
        v_actor, v_behalf, lower(TG_OP), TG_TABLE_NAME,
        COALESCE(NEW.id, OLD.id),
        v_changed, v_old, v_new,
        current_setting('app.session_id', true),
        NULLIF(current_setting('app.ip_address', true), '')::INET,
        current_setting('app.request_id', true)
    );

    RETURN COALESCE(NEW, OLD);
END $$;
```

Apply to the audited tables:

```sql
CREATE TRIGGER trg_audit_person           AFTER INSERT OR UPDATE ON person
    FOR EACH ROW EXECUTE FUNCTION audit_trigger();
CREATE TRIGGER trg_audit_membership       AFTER INSERT OR UPDATE ON membership
    FOR EACH ROW EXECUTE FUNCTION audit_trigger();
CREATE TRIGGER trg_audit_guardianship     AFTER INSERT OR UPDATE ON guardianship
    FOR EACH ROW EXECUTE FUNCTION audit_trigger();
CREATE TRIGGER trg_audit_role_assignment  AFTER INSERT OR UPDATE ON role_assignment
    FOR EACH ROW EXECUTE FUNCTION audit_trigger();
CREATE TRIGGER trg_audit_access_grant     AFTER INSERT OR UPDATE ON access_grant
    FOR EACH ROW EXECUTE FUNCTION audit_trigger();
-- ... and the remaining business tables
```

**`DELETE` is intentionally absent from the trigger definitions for business tables**,
because nothing in this schema is hard-deleted (see
[00-conventions.md](00-conventions.md#4-deletion-policy)). Staging tables do get deleted;
they are not audited.

### 2.2 Redaction before logging

```sql
CREATE OR REPLACE FUNCTION redact_audit_values(p_table TEXT, p_data JSONB)
RETURNS JSONB LANGUAGE plpgsql IMMUTABLE AS $$
DECLARE
    v_redact_keys TEXT[] := ARRAY['secret_hash','notes','custody_arrangement',
                                  'termination_note','rejection_note','status_note'];
    v_always_redact TEXT[] := ARRAY['notes','custody_arrangement'];
    k TEXT;
BEGIN
    IF p_data IS NULL THEN RETURN NULL; END IF;
    FOREACH k IN ARRAY v_redact_keys LOOP
        IF p_data ? k THEN
            p_data := jsonb_set(p_data, ARRAY[k], '"«redacted»"');
        END IF;
    END LOOP;
    RETURN p_data;
END $$;
```

> **An audit log that stores the data it audits is a second copy of the sensitive data,
> with weaker access controls and a longer retention period.** Redaction happens before the
> insert, in the trigger — never in a cleanup job that might not run.

`v_always_redact` covers free-text fields that could plausibly contain medical or custody
information. `notes` is the usual offender: someone types a diagnosis into a general notes
field, and it is now in the audit trail forever. Consider whether `person.notes` should
exist at all.

### 2.3 History query

```sql
-- Full change history of a membership, newest first:
SELECT a.occurred_at, a.operation, a.changed_fields,
       a.old_values, a.new_values,
       COALESCE(p.family_name || ' ' || p.given_name, a.actor_label) AS actor
  FROM audit_log a
  LEFT JOIN person p ON p.id = a.actor_person_id
 WHERE a.table_name = 'membership' AND a.record_id = 501
 ORDER BY a.occurred_at DESC;
```

---

## 3. Import pipeline

Six stages, from
[../domain/03-identity-and-legacy.md](../domain/03-identity-and-legacy.md#7-legacy-import-pipeline).
The guiding requirements: **idempotent**, **reversible per batch**, **never overwrites
self-registered data**, **preserves provenance**.

```sql
CREATE TABLE import_batch (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name            TEXT NOT NULL,
    description     TEXT,

    source_type     TEXT NOT NULL CHECK (source_type IN
                        ('csv','xlsx','json','sql_dump','manual_entry','other')),
    source_reference TEXT,
    -- Where the file lives, or what it is. Enough to find the original again.

    source_hash     TEXT,
    -- SHA-256 of the source file. Detects re-importing the same file under a new name.

    row_count       INTEGER,
    status          TEXT NOT NULL DEFAULT 'staging' CHECK (status IN
                        ('staging','parsed','matching','review','applying',
                         'applied','reverted','failed')),
    dry_run         BOOLEAN NOT NULL DEFAULT false,
    -- A dry run parses and matches but writes nothing to business tables.

    created_by      BIGINT NOT NULL REFERENCES person(id),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    applied_at      TIMESTAMPTZ,
    applied_by      BIGINT REFERENCES person(id),

    reverted_at     TIMESTAMPTZ,
    reverted_by     BIGINT REFERENCES person(id),
    revert_note     TEXT,

    error_summary   TEXT,
    notes           TEXT
);

CREATE INDEX ix_import_batch_status ON import_batch (status);
```

```sql
CREATE TABLE staging_import (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    batch_id        BIGINT NOT NULL REFERENCES import_batch(id),

    source_row_number INTEGER,
    raw_data        JSONB NOT NULL,
    -- The row VERBATIM. Never modified. This is the evidence.

    source_row_hash TEXT NOT NULL,
    -- Deterministic hash of the meaningful fields. Idempotency key: re-importing
    -- a file matches on this and skips already-applied rows.

    CONSTRAINT uq_staging_row UNIQUE (batch_id, source_row_hash)
);

CREATE INDEX ix_staging_batch ON staging_import (batch_id);
```

```sql
CREATE TABLE staging_import_row (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    staging_id      BIGINT NOT NULL REFERENCES staging_import(id),

    parsed_given_name    TEXT,
    parsed_family_name   TEXT,
    parsed_name_normalised TEXT,      -- diacritics stripped, casefolded
    parsed_birth_date    DATE,
    parsed_birth_precision TEXT,      -- reuses person.birth_date_precision values
    parsed_unit_code     TEXT,
    parsed_unit_name     TEXT,
    parsed_period_from   DATE,
    parsed_period_to     DATE,        -- often NULL; see the inference rules below

    parse_status    TEXT NOT NULL DEFAULT 'ok'
                    CHECK (parse_status IN ('ok','warning','error')),
    parse_warnings  TEXT[],
    -- e.g. {'birth_date_year_only', 'unit_not_found', 'ambiguous_name'}
    -- Warnings do not block; errors do.

    resolution      TEXT CHECK (resolution IN
                        ('link_existing','create_new','discard','deferred')),
    resolved_person_id BIGINT REFERENCES person(id),
    resolved_by     BIGINT REFERENCES person(id),
    resolved_at     TIMESTAMPTZ,
    resolution_note TEXT,

    applied         BOOLEAN NOT NULL DEFAULT false,
    applied_person_id BIGINT REFERENCES person(id),
    applied_membership_id BIGINT REFERENCES membership(id),
    applied_unit_membership_id BIGINT REFERENCES unit_membership(id),

    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX ix_staging_row_staging ON staging_import_row (staging_id);
CREATE INDEX ix_staging_row_review  ON staging_import_row (parse_status, resolution)
    WHERE resolution IS NULL OR resolution = 'deferred';
CREATE INDEX ix_staging_row_applied ON staging_import_row (applied)
    WHERE applied;
```

### Reversibility

`staging_import_row` holding the three created ids is what makes per-batch revert possible:

```sql
-- Revert a batch: remove only what this batch created.
-- Order matters: dependents first.
UPDATE unit_membership SET valid_to = NULL   -- (or delete if it was purely created here)
 WHERE id IN (SELECT applied_unit_membership_id FROM staging_import_row
               WHERE staging_id IN (SELECT id FROM staging_import WHERE batch_id = :batch)
                 AND applied_unit_membership_id IS NOT NULL);
-- ... similarly for membership, then person, then mark rows unapplied
UPDATE staging_import_row SET applied = false
 WHERE staging_id IN (SELECT id FROM staging_import WHERE batch_id = :batch);
```

**Revert is only safe before live data references the imported rows.** Once a real person
has been linked, or an event attendance recorded against an imported membership, deleting
the row breaks it. Therefore:

- Revert is allowed only while `import_batch.status = 'applied'` **and** no row created by
  the batch has been referenced by a later live record.
- Detecting that requires checking for references — implement as a pre-flight check that
  reports which rows cannot be reverted, and refuse rather than partially applying.
- After that window, corrections are made by editing the data, not by reverting. This is
  the honest behaviour; a "revert" that silently orphans references is worse than refusing.

> **Bias toward import in small batches and review before applying.** Reversibility is a
> safety net, not a workflow.

### Idempotency

`uq_staging_row (batch_id, source_row_hash)` makes re-staging cheap. Idempotency across
*batches* needs the hash to be computed from the row's semantic content, not its position:

```
source_row_hash = sha256(
    normalise(given_name) || '|' ||
    normalise(family_name) || '|' ||
    coalesce(birth_date::text,'') || '|' ||
    coalesce(unit_code,'') || '|' ||
    coalesce(period_from::text,'')
)
```

Then a re-import of an overlapping roster produces rows that match already-applied ones,
and the pipeline can skip them. **The hash function must be stable** — changing it
invalidates every previously staged row. Version it if it must change.

### End-date inference

Imported rosters rarely state when a membership ended. Three defensible options:

| Rule | Effect | Risk |
|------|--------|------|
| Leave `valid_to` NULL | Person appears to be a current member | **Wrong and dangerous** — inflates the member count and grants member privileges |
| End at the end of the roster's organizational year | Defensible, documented | May truncate a membership that continued |
| End at the last date the person appears in *any* roster | Best fidelity, needs all rosters | Requires the complete dataset |

**Recommended default:** end at the end of the organizational year of the last roster in
which the person appears, marked `data_confidence = 'low'` and with a parse warning. Never
NULL — an open membership from 1998 would make that person a current member in 2026.

---

## 4. Redaction log

```sql
CREATE TABLE redaction_log (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    person_id       BIGINT NOT NULL REFERENCES person(id),
    -- The row is NOT deleted. The id survives so historical references resolve.

    requested_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    requested_by    BIGINT REFERENCES person(id),
    legal_basis     TEXT,
    -- 'gdpr_art17' | 'court_order' | 'internal_policy' — required for accountability.

    performed_at    TIMESTAMPTZ,
    performed_by    BIGINT REFERENCES person(id),

    redacted_tables TEXT[],
    -- Which tables had values overwritten.

    retained_reason TEXT,
    -- Why some data was kept. Membership periods and unit memberships are
    -- organizational history, not personal data, and removing them would falsify
    -- records the organization may be obliged to keep. This field records that
    -- judgement per case.

    note            TEXT,
    CONSTRAINT ck_redaction_performed CHECK (
        performed_at IS NULL OR performed_by IS NOT NULL)
);

CREATE INDEX ix_redaction_person ON redaction_log (person_id);
```

**This log is the answer to "prove you honoured the erasure request".** It records what
was removed, when, on what legal basis, and — importantly — what was deliberately retained
and why. A redaction performed without a record is indistinguishable from a data loss
incident.

---

## 5. Integrity checks

```sql
-- 1. Imported memberships with a NULL valid_to (should be zero; see §3)
SELECT m.id, m.person_id, m.valid_from FROM membership m
 WHERE m.import_batch_id IS NOT NULL AND m.valid_to IS NULL;

-- 2. Imported people who were later merged away (probably fine, worth an eye)
SELECT p.id, p.merged_into_person_id FROM person p
 WHERE p.record_origin = 'legacy_import' AND p.merged_into_person_id IS NOT NULL;

-- 3. Staged rows left in a non-terminal state for a long time
SELECT b.id, b.name, b.status, b.created_at FROM import_batch b
 WHERE b.status NOT IN ('applied','reverted','failed')
   AND b.created_at < now() - INTERVAL '30 days';

-- 4. Audit rows with no actor at all (a forensic gap)
SELECT * FROM audit_log
 WHERE actor_person_id IS NULL AND actor_label IS NULL;

-- 5. Tables missing an audit trigger (compare against a maintained list)
SELECT c.relname
  FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
 WHERE n.nspname = 'public' AND c.relkind = 'r'
   AND c.relname NOT LIKE 'staging_%' AND c.relname NOT LIKE 'pg_%'
   AND NOT EXISTS (SELECT 1 FROM pg_trigger t
                    WHERE t.tgrelid = c.oid AND t.tgname LIKE 'trg_audit_%');

-- 6. Redacted people with surviving personal data
SELECT p.id FROM person p
 WHERE p.redacted_at IS NOT NULL
   AND (p.given_name <> '«redacted»' OR p.family_name <> '«redacted»')
   AND EXISTS (SELECT 1 FROM person_contact c
                WHERE c.person_id = p.id AND c.valid_to IS NULL
                  AND c.value NOT LIKE '%redacted%');
```

**Check 5 is worth automating as a test**, not just a nightly query. A new table added
without an audit trigger is a silent, permanent hole in the audit trail — and it will be
discovered only when someone needs the history that was never recorded.

---

## 6. Open issues

- Which tables must be audited. Recommend: all business tables. The cost is storage; the
  cost of a gap is unbounded.
- Retention period for `audit_log` before archival to cold storage. Legal input required.
- Whether `audit_log` should be partitioned by month from the start (recommend yes, given
  the write volume and the multi-decade horizon).
- The definitive end-date inference rule for imported rosters (§3) — needs your input on
  the organizational year boundary.
- Exact redaction scope: which fields are personal data vs. organizational history (§4).
  Requires legal review.
- Whether `person.notes` should exist at all, given the redaction burden it creates.

All tracked in [../open-questions.md](../open-questions.md).
