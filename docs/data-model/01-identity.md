# Data Model — Identity

`person`, `account`, contact points, identifiers, identity hypotheses, and merges.

Every pattern referenced here is defined in [00-conventions.md](00-conventions.md).

---

## 1. The central claim

```
person   ── what the organization knows about a human. No status. No role. No type.
account  ── how that human logs in. Optional. Zero or more over a lifetime.
```

**There is no `is_member`, `member_type`, `is_child`, `is_adult`, `unit_id`, or `role` on
`person`.** Each of those is either a period in another table or a derived fact. This is
the single most important property of the schema and the one most likely to be undone by
a well-meaning future change.

---

## 2. `person`

```sql
CREATE TABLE person (
    id                  BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    public_id           UUID        NOT NULL DEFAULT gen_random_uuid() UNIQUE,

    given_name          TEXT        NOT NULL,
    family_name         TEXT        NOT NULL,
    -- Names are ALSO stored as temporal rows in person_name (see §3). These two columns
    -- are the current/canonical form, denormalised for display and search. History and
    -- legal-name variants live in person_name.

    birth_date          DATE,
    -- Nullable: legacy records frequently lack it. Never NOT NULL — a 1994 roster
    -- with no birth date must still import.

    birth_date_precision TEXT CHECK (birth_date_precision IN
                            ('exact','month','year','unknown')),
    -- Because an imported birth date of '1990-01-01' often means "year 1990, month
    -- and day unknown". Storing the precision prevents false matches on a guessed
    -- day and prevents "happy 1 January birthday" emails.

    gender              TEXT CHECK (gender IN ('male','female','other','unknown')),
    -- Included because youth organizations typically must report it. Remove if yours
    -- does not need it — do not collect what you cannot justify.

    preferred_name      TEXT,
    -- What the person is actually called. Distinct from given_name so that the
    -- organization's records stay legally correct while the person is addressed
    -- correctly ("Alexandra" recorded, "Lex" displayed).

    -- NOTE: there is deliberately NO deceased flag. The organization does not record
    -- whether a person has died. A membership simply ends; the reason for the ending
    -- lives in the generic reason-code tables (membership.termination_reason_code,
    -- membership.ended_note) like any other ending, and the organization's own
    -- vocabulary for such reasons is theirs to define. Do not add is_deceased or
    -- deceased_at back: it is not data the organization keeps.

    record_origin       TEXT        NOT NULL DEFAULT 'self_registered'
                        CHECK (record_origin IN
                            ('self_registered','staff_created','legacy_import')),

    data_confidence     TEXT        NOT NULL DEFAULT 'high'
                        CHECK (data_confidence IN ('high','medium','low')),
    -- 'low' for imported rows. Drives whether a merge may absorb this row, and whether
    -- the UI warns before displaying it as fact.

    merged_into_person_id BIGINT    REFERENCES person(id),
    merged_at           TIMESTAMPTZ,
    -- Tombstone. When set, this row is absorbed; queries must follow the pointer.
    -- Never deleted. See §7.

    redacted_at         TIMESTAMPTZ,
    -- Set when a GDPR-style erasure was performed. Names and contacts are overwritten;
    -- the row and its id survive so historical references still resolve.

    notes               TEXT,
    -- Free text. Flagged in redaction (§8 of conventions): may contain personal data.

    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by          BIGINT      REFERENCES person(id),
    updated_at          TIMESTAMPTZ,
    updated_by          BIGINT      REFERENCES person(id),
    import_batch_id     BIGINT,     -- FK added after import_batch exists

    CONSTRAINT ck_person_not_own_merge CHECK (merged_into_person_id IS DISTINCT FROM id),
    CONSTRAINT ck_person_merge_consistent CHECK (
        (merged_into_person_id IS NULL) = (merged_at IS NULL)),
    CONSTRAINT ck_person_birth_precision CHECK (
        birth_date IS NOT NULL OR birth_date_precision IS NULL
        OR birth_date_precision = 'unknown')
);

CREATE INDEX ix_person_family_given  ON person (lower(family_name), lower(given_name));
CREATE INDEX ix_person_birth_date    ON person (birth_date) WHERE birth_date IS NOT NULL;
CREATE INDEX ix_person_not_merged    ON person (id) WHERE merged_into_person_id IS NULL;
CREATE INDEX ix_person_not_redacted  ON person (id) WHERE redacted_at IS NULL;
CREATE INDEX ix_person_public_id     ON person (public_id);
```

### Notes on specific choices

**`birth_date_precision`.** Without it, a legacy import that only knows the year produces
`1990-01-01`, which then matches every other year-only record born in 1990 on the same
invented day, and sends birthday greetings on 1 January. Cheap column, prevents a whole
class of matching noise.

**`public_id` alongside `id`.** External references use `public_id`. Sequential internal
ids appear in `access_grant.scope_id` and in URLs; exposing them would let anyone enumerate
member records. See [00-conventions.md](00-conventions.md#3-primary-keys).

**`merged_into_person_id` and `redacted_at` are both on `person` rather than in side
tables.** They are read on *every* query (every listing must exclude merged and redacted
rows from ordinary views), so they need to be cheap. They are also the reason the two
partial indexes above exist.

### The answer to "who is a member?" is never on this table

To be unambiguous, the queries:

```sql
-- Currently a member
SELECT p.* FROM person p
 JOIN membership m ON m.person_id = p.id
 WHERE m.valid_to IS NULL AND m.status = 'active';

-- Was a member on 1998-06-01
SELECT p.* FROM person p
 JOIN membership m ON m.person_id = p.id
 WHERE m.valid_from <= DATE '1998-06-01'
   AND (m.valid_to IS NULL OR m.valid_to > DATE '1998-06-01')
   AND m.status IN ('active','completed','lapsed','terminated');
```

Note the second query includes closed statuses — "was a member in 1998" is true regardless
of how the membership later ended. Getting this wrong is why "years of membership" reports
are usually wrong.

---

## 3. `person_name` — name history

```sql
CREATE TABLE person_name (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    person_id   BIGINT NOT NULL REFERENCES person(id),

    name_type   TEXT   NOT NULL CHECK (name_type IN
                    ('legal','preferred','maiden','former','alias','imported')),
    given_name  TEXT   NOT NULL,
    family_name TEXT   NOT NULL,
    middle_name TEXT,

    valid_from  DATE,
    valid_to    DATE,          -- NULL = current for this name_type
    source      TEXT,          -- 'self' | 'staff' | 'legacy_import'
    import_batch_id BIGINT,

    CONSTRAINT ck_person_name_period CHECK (valid_to IS NULL OR valid_from IS NULL
                                            OR valid_to > valid_from)
);

CREATE INDEX ix_person_name_person ON person_name (person_id);
-- Fuzzy search across all historical names, which is what legacy matching reads:
CREATE INDEX ix_person_name_search ON person_name
    (lower(family_name) text_pattern_ops, lower(given_name) text_pattern_ops);
```

**Why name history is a table.** Three concrete cases:

1. A member married and changed their family name. The 1998 roster has the maiden name;
   the 2026 registration has the married name. Legacy matching must find the link, and
   the historical record must keep the name it actually had.
2. An imported name has a typo (`Novak` for `Novák`). Correcting it must not destroy the
   imported form, because that is what the paper says and someone will ask.
3. A person goes by a different name than their legal one. Both must be storable, and
   which is used where must be deterministic.

**`person.given_name`/`family_name` are the denormalised current values** and are what the
UI displays. `person_name` is the source of truth for matching and for historical queries.
This is a deliberate denormalization — the alternative is joining on every list view — and
it must be updated in the same transaction whenever the canonical name changes.

*Assumption:* display should use `person.preferred_name ?? person.given_name`. If the
organization requires legal names on official documents, that rule lives in the document
layer, not here.

---

## 4. `account`

```sql
CREATE TABLE account (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    person_id       BIGINT      NOT NULL REFERENCES person(id),
    -- NOT unique: a person may have several accounts over a lifetime (one abandoned in
    -- 2010, a new one in 2024). Uniqueness applies only to *active* accounts, below.

    username        TEXT,
    status          TEXT        NOT NULL DEFAULT 'pending_verification'
                    CHECK (status IN
                        ('pending_verification','active','suspended','closed')),

    verified_at     TIMESTAMPTZ,
    guardian_consent_at TIMESTAMPTZ,
    -- Set when a guardian confirmed a minor's account. NULL for adults.
    -- See domain/02-actors.md §2.

    created_by_staff BOOLEAN    NOT NULL DEFAULT false,
    last_login_at   TIMESTAMPTZ,
    failed_login_count INTEGER  NOT NULL DEFAULT 0,
    locked_until    TIMESTAMPTZ,

    status_reason_code TEXT,    -- why suspended/closed
    status_note     TEXT,

    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by      BIGINT      REFERENCES person(id),
    updated_at      TIMESTAMPTZ,
    updated_by      BIGINT      REFERENCES person(id),

    CONSTRAINT ck_account_verified CHECK (
        status <> 'active' OR verified_at IS NOT NULL)
);

-- At most one non-closed account per person:
CREATE UNIQUE INDEX uq_account_one_active_per_person
    ON account (person_id)
    WHERE status IN ('pending_verification','active','suspended');

CREATE UNIQUE INDEX uq_account_username ON account (lower(username))
    WHERE username IS NOT NULL AND status <> 'closed';

CREATE INDEX ix_account_person ON account (person_id);
```

**Why `person_id` is not unique.** The partial unique index expresses the real rule:
*one live account per person*, while permitting closed historical accounts. A plain
`UNIQUE (person_id)` would make it impossible to close an old account and open a new one —
which is exactly the returning-member case at the account level.

**Why `guardian_consent_at` is on `account`, not `person`.** Consent is about the *act of
creating login credentials*, not about the human. A person who was registered as a child
and later reaches majority keeps the same `person` row; the consent record stays attached
to the account it was given for.

**A suspended account does not suspend a membership.** They are independent lifecycles.
The schema enforces this by simply not linking them.

---

## 5. `account_credential`

```sql
CREATE TABLE account_credential (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    account_id      BIGINT      NOT NULL REFERENCES account(id),

    credential_type TEXT        NOT NULL CHECK (credential_type IN
                        ('password','passkey','totp','oauth','staff_link')),
    -- Multiple methods per account. 'oauth' supports a national Scout identity provider;
    -- 'staff_link' supports a one-time link issued to a member who cannot self-serve.

    secret_hash     TEXT,       -- password/OTP hash. NULL for passkey/oauth.
    external_ref    TEXT,       -- OAuth subject id, or WebAuthn credential id
    external_issuer TEXT,       -- OAuth issuer

    valid_from      TIMESTAMPTZ NOT NULL DEFAULT now(),
    valid_to        TIMESTAMPTZ,-- NULL = current
    last_used_at    TIMESTAMPTZ,
    revoked_reason  TEXT,

    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT ck_credential_has_secret CHECK (
        (credential_type IN ('password','totp','staff_link') AND secret_hash IS NOT NULL)
     OR (credential_type IN ('passkey','oauth')
         AND external_ref IS NOT NULL AND external_issuer IS NOT NULL)),
    CONSTRAINT ck_credential_period CHECK (
        valid_to IS NULL OR valid_to > valid_from)
);

CREATE INDEX ix_credential_account ON account_credential (account_id)
    WHERE valid_to IS NULL;
CREATE UNIQUE INDEX uq_credential_oauth ON account_credential
    (external_issuer, external_ref)
    WHERE credential_type = 'oauth' AND valid_to IS NULL;
```

**Why credentials are not columns on `account`.** Adding passkeys, an organizational SSO,
or a one-time-link flow later must not require restructuring `account` and migrating every
existing password. Keeping `secret_hash` off the `account` table also means the common
"show me the user" query never touches credential material.

**`valid_to` on a credential is how password history and revocation are expressed.** A
revoked credential stays as a row, so "was this account ever accessed with a credential
that has since been revoked?" is answerable.

---

## 6. `person_contact`

```sql
CREATE TABLE person_contact (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    person_id   BIGINT NOT NULL REFERENCES person(id),

    contact_type TEXT NOT NULL CHECK (contact_type IN
                    ('email','phone','postal','website','messaging')),
    purpose      TEXT NOT NULL CHECK (purpose IN
                    ('login','membership','emergency','billing','guardian','general')),

    value        TEXT NOT NULL,
    -- Normalised per type: emails lowercased, phones E.164, postal as structured JSON.

    value_detail JSONB,
    -- For postal addresses: {street, city, postal_code, country}. Avoids six nullable
    -- columns that only apply to one contact_type.

    label        TEXT,          -- 'home', 'work', 'school' — display only
    is_primary   BOOLEAN NOT NULL DEFAULT false,
    verified_at  TIMESTAMPTZ,
    verified_by  TEXT CHECK (verified_by IN ('self','staff','bounce_check','import')),

    valid_from   DATE NOT NULL DEFAULT CURRENT_DATE,
    valid_to     DATE,          -- NULL = current. Addresses change; history is required.
    source       TEXT,          -- 'self' | 'staff' | 'legacy_import'
    import_batch_id BIGINT,

    created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by   BIGINT REFERENCES person(id),

    CONSTRAINT ck_contact_period CHECK (valid_to IS NULL OR valid_to > valid_from)
);

CREATE INDEX ix_contact_person    ON person_contact (person_id);
CREATE INDEX ix_contact_type      ON person_contact (person_id, contact_type, purpose)
    WHERE valid_to IS NULL;
CREATE INDEX ix_contact_email     ON person_contact (lower(value))
    WHERE contact_type = 'email' AND valid_to IS NULL;
CREATE INDEX ix_contact_phone     ON person_contact (value)
    WHERE contact_type = 'phone' AND valid_to IS NULL;

-- At most one current primary per (person, type, purpose):
CREATE UNIQUE INDEX uq_contact_primary ON person_contact
    (person_id, contact_type, purpose)
    WHERE is_primary AND valid_to IS NULL;
```

**`purpose` is the column that makes this operationally useful.** It lets the permission
system distinguish "a unit leader may see emergency contacts for camp" from "only billing
staff may see payment email addresses". Without `purpose`, every contact is equally
sensitive and the only safe choice is to hide all of them.

**The `uq_contact_primary` partial unique index** enforces "one primary email per person
per purpose" without preventing a person from having four non-primary addresses. Note this
index is what makes the merge conflict in
[§8](#8-identity_hypothesis-and-person_merge) possible — resolving two `is_primary` rows is a review
step, not a rule.

**`ix_contact_email` is a functional index on `lower(value)`** because email matching in
the legacy importer must be case-insensitive, and a plain index cannot serve that.

---

## 7. `person_identifier`

```sql
CREATE TABLE person_identifier (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    person_id   BIGINT NOT NULL REFERENCES person(id),

    scheme      TEXT NOT NULL,
    -- 'national_scout_id' | 'legacy_member_no' | 'legacy_member_no_oldsystem'
    -- | 'government_id' | 'school_id' | 'insurance_no'
    -- Validated against identifier_scheme (below).

    value       TEXT NOT NULL,

    issued_at   DATE,
    valid_to    DATE,           -- IDs expire or are superseded
    verified_at TIMESTAMPTZ,
    source      TEXT,
    import_batch_id BIGINT,

    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE identifier_scheme (
    code            TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    is_unique       BOOLEAN NOT NULL DEFAULT true,
    -- True: a value may appear on only one person (national id, member number).
    -- False: values legitimately repeat (school id across schools).
    description     TEXT
);

-- Enforce uniqueness only for schemes flagged unique:
CREATE UNIQUE INDEX uq_identifier_unique_scheme
    ON person_identifier (scheme, value)
    WHERE valid_to IS NULL;

CREATE INDEX ix_identifier_person ON person_identifier (person_id);
```

**This table is the highest-value asset in the legacy import.** If the old system issued
member numbers, an exact `(scheme='legacy_member_no', value=…)` match is the strongest
identity signal available — strong enough to short-circuit a fuzzy name comparison. See
[../domain/03-identity-and-legacy.md](../domain/03-identity-and-legacy.md#4-match-signals).

**Why not put these on `person` as columns.** A person may have zero identifiers (most
self-registered children), one, or several; schemes appear and disappear over decades; and
`national_scout_id` must be unique while `school_id` must not. Columns would mean a schema
change per scheme and a nullable-unique mess.

---

## 8. `identity_hypothesis` and `person_merge`

```sql
CREATE TABLE identity_hypothesis (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    -- Canonical ordering enforced so that (a,b) and (b,a) cannot both exist:
    person_a_id     BIGINT NOT NULL REFERENCES person(id),
    person_b_id     BIGINT NOT NULL REFERENCES person(id),

    confidence      NUMERIC(4,3) NOT NULL CHECK (confidence BETWEEN 0 AND 1),
    match_signals   JSONB NOT NULL,
    -- [{signal:'birth_date_exact', weight:0.4, matched:true},
    --  {signal:'name_normalised',  weight:0.3, matched:true}, ...]
    -- Stored so a human reviewer can see WHY the matcher proposed this.

    status          TEXT NOT NULL DEFAULT 'proposed'
                    CHECK (status IN ('proposed','needs_review','confirmed',
                                      'rejected','superseded')),

    proposed_by     TEXT NOT NULL CHECK (proposed_by IN
                        ('import_job','match_job','person','staff')),
    -- 'match_job' = the nightly batch matcher, as opposed to a person suggesting a match
    -- by hand. (Named 'background_match' before background checks were removed from the
    -- design; renamed so the two never get confused.)
    proposed_by_person_id BIGINT REFERENCES person(id),
    proposed_at     TIMESTAMPTZ NOT NULL DEFAULT now(),

    reviewed_by     BIGINT REFERENCES person(id),
    reviewed_at     TIMESTAMPTZ,
    review_note     TEXT,

    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT ck_hypothesis_ordering CHECK (person_a_id < person_b_id),
    CONSTRAINT ck_hypothesis_distinct   CHECK (person_a_id <> person_b_id),
    CONSTRAINT ck_hypothesis_reviewed CHECK (
        status NOT IN ('confirmed','rejected') OR reviewed_at IS NOT NULL)
);

-- One live hypothesis per pair:
CREATE UNIQUE INDEX uq_hypothesis_pair_live
    ON identity_hypothesis (person_a_id, person_b_id)
    WHERE status IN ('proposed','needs_review','confirmed');

CREATE INDEX ix_hypothesis_queue ON identity_hypothesis (status, confidence DESC)
    WHERE status IN ('proposed','needs_review');


CREATE TABLE person_merge (
    id                  BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    surviving_person_id BIGINT NOT NULL REFERENCES person(id),
    merged_person_id    BIGINT NOT NULL REFERENCES person(id),
    -- The absorbed row. It keeps its id; person.merged_into_person_id points here.

    hypothesis_id       BIGINT REFERENCES identity_hypothesis(id),
    merged_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
    merged_by           BIGINT NOT NULL REFERENCES person(id),
    reason              TEXT,

    reversed_at         TIMESTAMPTZ,
    reversed_by         BIGINT REFERENCES person(id),
    reversal_note       TEXT,

    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT ck_merge_distinct CHECK (surviving_person_id <> merged_person_id)
);

CREATE INDEX ix_merge_surviving ON person_merge (surviving_person_id);
CREATE INDEX ix_merge_merged    ON person_merge (merged_person_id);
CREATE INDEX ix_merge_active    ON person_merge (merged_person_id)
    WHERE reversed_at IS NULL;
```

**`ck_hypothesis_ordering` (`a < b`) is not cosmetic.** Without it the matcher can create
both `(100, 847)` and `(847, 100)`, and a reviewer will confirm one while the other sits in
the queue forever — or worse, confirm both. The check plus the partial unique index makes
the pair identity unambiguous.

**`match_signals` as JSONB** rather than columns, because the signal set will evolve as the
matcher improves, and because these are write-once-read-for-review, never queried
analytically.

**`person_merge` is append-only** — `reversed_at` is set, rows are never deleted. An
unmerge does not remove the merge record; it records that it was undone, so the history of
the mistake is visible. See
[../domain/03-identity-and-legacy.md](../domain/03-identity-and-legacy.md#6-reversing-a-merge).

### Merge conflicts

```sql
CREATE TABLE field_conflict (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    merge_id        BIGINT NOT NULL REFERENCES person_merge(id),

    entity_table    TEXT NOT NULL,     -- 'person' | 'person_contact' | 'membership' | ...
    entity_id       BIGINT NOT NULL,
    field_name      TEXT NOT NULL,

    surviving_value TEXT,
    merged_value    TEXT,
    resolution      TEXT CHECK (resolution IN
                        ('kept_surviving','took_merged','manual','unresolved')),
    resolved_value  TEXT,
    resolved_by     BIGINT REFERENCES person(id),
    resolved_at     TIMESTAMPTZ,

    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX ix_conflict_merge ON field_conflict (merge_id, resolution);
CREATE INDEX ix_conflict_open  ON field_conflict (merge_id) WHERE resolution = 'unresolved';
```

Every field the merge could not resolve automatically lands here as `unresolved`. **A
merge with unresolved conflicts must be visible in an operational report** — otherwise
these rows accumulate silently and the data is quietly wrong.

Conflict cases worth naming, because each needs a human decision and none has a safe rule:

| Case | Why it cannot be automatic |
|------|---------------------------|
| Two `is_primary` emails of the same purpose | Which one does the person actually use? |
| Two different `birth_date` values | One is a typo; guessing produces a wrong legal record. |
| Two overlapping memberships | May be legitimate, or may mean the merge is *wrong*. |
| Two different current names | One may be a maiden name, or they may be different people. |
| Two accounts, both active | Which one is in use? |

---

## 9. Views

Convenience views that encode the "always exclude merged and redacted" and "point in
time" rules, so that application code cannot forget them.

```sql
-- The person most queries actually want:
CREATE VIEW v_person AS
SELECT * FROM person
 WHERE merged_into_person_id IS NULL;

-- Resolve a possibly-merged id to its survivor (follows chains):
CREATE OR REPLACE FUNCTION resolve_person(p_id BIGINT)
RETURNS BIGINT LANGUAGE sql STABLE AS $$
    WITH RECURSIVE chain AS (
        SELECT id, merged_into_person_id FROM person WHERE id = p_id
        UNION ALL
        SELECT p.id, p.merged_into_person_id
          FROM person p JOIN chain c ON p.id = c.merged_into_person_id
    )
    SELECT id FROM chain WHERE merged_into_person_id IS NULL LIMIT 1;
$$;

-- Display name, honouring preferred_name:
CREATE VIEW v_person_display AS
SELECT p.id, p.public_id,
       COALESCE(p.preferred_name, p.given_name) AS display_given_name,
       p.family_name,
       COALESCE(p.preferred_name, p.given_name) || ' ' || p.family_name AS display_name,
       p.birth_date, p.birth_date_precision, p.redacted_at
  FROM person p
 WHERE p.merged_into_person_id IS NULL;
```

`resolve_person` uses `RECURSIVE` because merges chain: A absorbed into B, later B absorbed
into C. A single-level pointer lookup would return B, whose row is itself tombstoned.
**Every place that accepts a person id from outside must call this.** Getting it wrong
means a historical record links to a tombstone and the UI shows a blank name — or the
wrong one.

*Assumption:* merge chains are allowed rather than flattened at merge time. Flattening
(silently repointing every existing pointer to the new survivor) is faster to query but
rewrites history and makes unmerge nearly impossible. Tracked in
[../open-questions.md](../open-questions.md).

---

## 10. Integrity checks

Queries that should run nightly and alert. These encode invariants the schema cannot
express on its own.

```sql
-- 1. A person with more than one live account (should be zero; index permits
--    pending+active simultaneously? no — verify the index covers all cases)
SELECT person_id, count(*) FROM account
 WHERE status IN ('pending_verification','active','suspended')
 GROUP BY person_id HAVING count(*) > 1;

-- 2. Merge chains longer than expected (signals repeated bad merges)
SELECT * FROM person WHERE merged_into_person_id IS NOT NULL
 EXCEPT SELECT merged_person_id FROM person_merge WHERE reversed_at IS NULL;

-- 3. Tombstoned rows that are still referenced as survivors
SELECT m.* FROM person_merge m
 JOIN person p ON p.id = m.surviving_person_id
 WHERE p.merged_into_person_id IS NOT NULL;

-- 4. Unresolved merge conflicts older than 30 days
SELECT * FROM field_conflict
 WHERE resolution = 'unresolved' AND created_at < now() - INTERVAL '30 days';

-- 5. Redacted people still referenced by a live account
SELECT p.id FROM person p JOIN account a ON a.person_id = p.id
 WHERE p.redacted_at IS NOT NULL AND a.status <> 'closed';

-- 6. Imported people with no membership (probably a partially applied batch)
SELECT p.* FROM person p
 WHERE p.record_origin = 'legacy_import'
   AND NOT EXISTS (SELECT 1 FROM membership m WHERE m.person_id = p.id);
```

---

## 11. Open issues

- Whether merge chains are allowed or flattened at merge time (§9).
- Whether a person may hold two live accounts simultaneously — recommend no, enforced by
  the partial index in §4.
- Erasure policy specifics: what must be redacted vs. retained, and the retention period.
  Requires legal input. See [00-conventions.md](00-conventions.md#8-personal-data-and-erasure).
- Whether `person.gender` is needed at all; if so, what value set.
- Whether the organization has (or will have) a national SSO identity provider — this
  determines how much of `account_credential` is actually used.

All tracked in [../open-questions.md](../open-questions.md).
