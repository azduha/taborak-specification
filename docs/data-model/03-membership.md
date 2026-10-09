# Data Model — Membership

`membership_type`, `membership`, `membership_request`, request requirements, and
`unit_membership`.

Domain rationale: [../domain/05-membership-lifecycle.md](../domain/05-membership-lifecycle.md).

---

## 1. `membership_type`

```sql
CREATE TABLE membership_type (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    code            TEXT NOT NULL UNIQUE,   -- 'child','adult','counselor','honorary','lifetime'
    name            TEXT NOT NULL,
    description     TEXT,

    category        TEXT NOT NULL CHECK (category IN ('child','adult','special')),
    -- 'child'  — youth participant. Drives guardian-consent and age validation.
    -- 'adult'  — adult participant. Drives background-check validation.
    -- 'special'— honorary, lifetime, staff. No age rules, no background check.
    --
    -- This is the column that replaces `person.is_child`. A person's category comes
    -- from their CURRENT membership's type, never from the person row.

    requires_background_check BOOLEAN NOT NULL DEFAULT false,
    requires_guardian_consent BOOLEAN NOT NULL DEFAULT false,
    requires_references       BOOLEAN NOT NULL DEFAULT false,

    min_age         INTEGER,     -- in years, at valid_from. NULL = no minimum.
    max_age         INTEGER,     -- drives automatic age-out. NULL = no maximum.

    duration_months INTEGER,     -- 12 typically; NULL = indefinite (lifetime)
    grace_period_days INTEGER NOT NULL DEFAULT 0,
    -- Days after valid_to during which the person still counts as a member.
    -- Matters legally: "was this person a member on the day of the camp?"

    fee_schedule_id BIGINT,      -- FK added in 07-finance.md
    allows_concurrent BOOLEAN NOT NULL DEFAULT false,
    -- May a person hold this type concurrently with another open membership?
    -- See §3 for how this interacts with the overlap constraint.

    is_self_registerable BOOLEAN NOT NULL DEFAULT true,
    -- False for types only staff may grant (honorary, lifetime).

    requires_approval BOOLEAN NOT NULL DEFAULT true,
    sort_order      INTEGER NOT NULL DEFAULT 0,

    valid_from      DATE,
    valid_to        DATE,

    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT ck_membership_type_period CHECK (
        valid_to IS NULL OR valid_from IS NULL OR valid_to > valid_from),
    CONSTRAINT ck_membership_type_ages CHECK (
        min_age IS NULL OR max_age IS NULL OR max_age > min_age)
);

CREATE INDEX ix_membership_type_current ON membership_type (code) WHERE valid_to IS NULL;
```

**`category` rather than treating type codes as interchangeable.** The validation and
permission rules genuinely differ between a child and an adult in a youth organization, and
expressing that once on the type is far better than scattering
`if membership_type == 'child'` through the codebase. It is a three-valued classification,
not a type-code check, so adding a `cub` or `venture` type does not require touching code.

**`grace_period_days` here, not as a date on the membership.** During grace the person is
*still a member*. Modeling it as an extended `valid_to` on the row would lose the
distinction between "paid up" and "in grace", and that distinction is exactly what an
insurance or safeguarding question turns on.

---

## 2. `membership_request`

```sql
CREATE TABLE membership_request (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    public_id       UUID NOT NULL DEFAULT gen_random_uuid() UNIQUE,

    person_id       BIGINT NOT NULL REFERENCES person(id),
    -- The SUBJECT: the person who would become a member. For a minor's application this
    -- is the CHILD, not the parent.

    submitted_by_person_id BIGINT REFERENCES person(id),
    -- Who actually submitted it. Equals person_id for self-application; differs when a
    -- guardian (or staff) applies on behalf. This is the act-on-behalf record.

    requested_membership_type_id BIGINT NOT NULL REFERENCES membership_type(id),
    requested_unit_id   BIGINT REFERENCES org_unit(id),
    -- Nullable: the applicant may express a preference, or the organization may assign
    -- the unit at approval.

    status          TEXT NOT NULL DEFAULT 'draft'
                    CHECK (status IN ('draft','submitted','under_review','approved',
                                      'rejected','withdrawn','expired')),

    submitted_at    TIMESTAMPTZ,
    decided_at      TIMESTAMPTZ,
    decided_by      BIGINT REFERENCES person(id),

    rejection_reason_code TEXT,
    rejection_note  TEXT,

    membership_id   BIGINT,     -- set on approval; FK added after membership (§3).
                                -- Circular reference resolved with a deferred FK.

    previous_membership_id BIGINT REFERENCES membership(id),
    -- Links a renewal or re-application to the prior membership. This is how a
    -- returning member's chain is expressed.

    expires_at      TIMESTAMPTZ,
    -- An unreviewed request eventually goes stale. Needed so the review queue does
    -- not accumulate abandoned drafts forever.

    notes           TEXT,
    source          TEXT,       -- 'self' | 'guardian' | 'staff' | 'import'

    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by      BIGINT REFERENCES person(id),
    updated_at      TIMESTAMPTZ,
    updated_by      BIGINT REFERENCES person(id),

    CONSTRAINT ck_request_decided CHECK (
        status NOT IN ('approved','rejected') OR (decided_at IS NOT NULL
                                                  AND decided_by IS NOT NULL)),
    CONSTRAINT ck_request_rejection_reason CHECK (
        status <> 'rejected' OR rejection_reason_code IS NOT NULL),
    CONSTRAINT ck_request_submitted CHECK (
        status = 'draft' OR submitted_at IS NOT NULL),
    CONSTRAINT ck_request_membership_link CHECK (
        status <> 'approved' OR membership_id IS NOT NULL OR decided_at > now()
        -- on approval the membership link is set; the now() escape allows the
        -- two-step insert within one transaction
    )
);

CREATE INDEX ix_request_person  ON membership_request (person_id, submitted_at DESC);
CREATE INDEX ix_request_queue   ON membership_request (status, submitted_at)
    WHERE status IN ('submitted','under_review');
CREATE INDEX ix_request_submitter ON membership_request (submitted_by_person_id)
    WHERE submitted_by_person_id IS NOT NULL;
CREATE INDEX ix_request_unit    ON membership_request (requested_unit_id)
    WHERE requested_unit_id IS NOT NULL;

-- At most one open request per person per type:
CREATE UNIQUE INDEX uq_request_open_per_person_type
    ON membership_request (person_id, requested_membership_type_id)
    WHERE status IN ('draft','submitted','under_review');
```

**`person_id` vs `submitted_by_person_id` is the most important pair in this table.** The
subject is the child; the submitter is the parent. Collapsing them into one column — which
is what most systems do — makes it impossible to answer "who applied for this child?" and
falsely attributes the parent's action to the child. See
[../domain/02-actors.md](../domain/02-actors.md#5-acting-on-behalf).

**Why requests are a separate table from memberships.** A rejected request produces no
membership and must not pollute member listings; a person may submit several over time; and
review data (who decided, why) has no meaning on a membership. See
[../domain/05-membership-lifecycle.md](../domain/05-membership-lifecycle.md#2-membership-request).

**`ck_request_rejection_reason` requires a reason code on rejection.** "Why was this
application turned down?" is asked months later, sometimes by the family. A rejection with
no recorded reason is an answerable question made unanswerable.

**`previous_membership_id`** is what makes the returning-member chain explicit rather than
inferred from date arithmetic.

---

## 3. `membership`

```sql
CREATE TABLE membership (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    public_id       UUID NOT NULL DEFAULT gen_random_uuid() UNIQUE,

    person_id       BIGINT NOT NULL REFERENCES person(id),
    membership_type_id BIGINT NOT NULL REFERENCES membership_type(id),

    status          TEXT NOT NULL CHECK (status IN
                        ('pending_payment','active','suspended','lapsed',
                         'terminated','completed')),

    valid_from      DATE NOT NULL,
    valid_to        DATE,          -- NULL = open / current

    joined_via_request_id BIGINT REFERENCES membership_request(id),
    renewed_from_membership_id BIGINT REFERENCES membership(id),
    -- Self-reference forming the renewal chain. See domain/05 §6.

    outstanding_balance NUMERIC(12,2),
    -- DENORMALISED from fee_obligation/payment. Convenience for the "approved but
    -- unpaid" worklist. Must be maintained transactionally or recomputed — see
    -- 07-finance.md. NULL for imported historical memberships with no payment data.

    termination_reason_code TEXT,
    termination_note TEXT,
    ended_by        BIGINT REFERENCES person(id),
    ended_at        TIMESTAMPTZ,

    data_confidence TEXT NOT NULL DEFAULT 'high'
                    CHECK (data_confidence IN ('high','medium','low')),
    import_batch_id BIGINT,
    notes           TEXT,

    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by      BIGINT REFERENCES person(id),
    updated_at      TIMESTAMPTZ,
    updated_by      BIGINT REFERENCES person(id),

    CONSTRAINT ck_membership_period CHECK (valid_to IS NULL OR valid_to > valid_from),
    CONSTRAINT ck_membership_terminated CHECK (
        status <> 'terminated' OR (termination_reason_code IS NOT NULL
                                   AND ended_at IS NOT NULL)),
    CONSTRAINT ck_membership_not_own_renewal CHECK (
        renewed_from_membership_id IS DISTINCT FROM id)
);

-- THE critical constraint: no two overlapping open memberships of the same type.
CREATE EXTENSION IF NOT EXISTS btree_gist;

ALTER TABLE membership ADD CONSTRAINT ex_membership_no_overlap
    EXCLUDE USING gist (
        person_id          WITH =,
        membership_type_id WITH =,
        daterange(valid_from, valid_to, '[)') WITH &&
    )
    WHERE (status IN ('pending_payment','active','suspended'));

CREATE INDEX ix_membership_person   ON membership (person_id, valid_from DESC);
CREATE INDEX ix_membership_current  ON membership (person_id)
    WHERE valid_to IS NULL AND status = 'active';
CREATE INDEX ix_membership_status   ON membership (status, valid_to)
    WHERE status IN ('active','pending_payment');
CREATE INDEX ix_membership_period   ON membership USING gist
    (person_id, daterange(valid_from, valid_to, '[)'));
CREATE INDEX ix_membership_type     ON membership (membership_type_id, status);
```

### Why the exclusion constraint is scoped to `membership_type_id`

Not to `person_id` alone, because some combinations are legitimate: an honorary member who
is also an active adult member, or a lifetime member who still volunteers. Constraining on
the type permits that while blocking the case that matters — one person, one open child
membership.

**If you decide a person may hold only ONE open membership of any type**, change the
constraint to drop the `membership_type_id` line and handle `allows_concurrent` in
application logic. That is a stricter and simpler rule; it is your call. Tracked in
[../open-questions.md](../open-questions.md).

### The exclusion constraint and status transitions

Note the `WHERE` clause covers only `pending_payment`, `active`, `suspended`. A
`terminated`/`lapsed`/`completed` row is excluded, so a new membership can be created with
a `valid_from` inside an old one's period without violating the constraint. **This is
deliberate** — a returning member's new membership may legitimately overlap the tail of a
lapsed one if the dates were entered imprecisely. Historical imports rely on this.

**Consequence:** the constraint does not prevent two *active* memberships with overlapping
periods if one was inserted while in another status and then transitioned. A status update
re-evaluates the constraint (PostgreSQL does check exclusion constraints on UPDATE), so
this is safe — but the transition from `lapsed` back to `active` can therefore **fail with
a constraint violation**. That is correct behaviour: it means the person has two
overlapping claims to membership and someone must resolve it. Handle it as a business
error, not a crash.

### Why `valid_to IS NULL` and not a sentinel

Repeated from the conventions because it is the mistake most likely to be made here.
A `'9999-12-31'` sentinel breaks `IS NULL` checks, makes `daterange` spans enormous, and
defeats the `ix_membership_current` partial index. Use NULL.

### `renewed_from_membership_id`

Renewal opens a **new** row (Shape A in
[../domain/05-membership-lifecycle.md](../domain/05-membership-lifecycle.md#6-renewal-and-the-yearly-fee)).
The self-reference makes the chain explicit:

```
membership 501  child  1990-09-01 → 1991-06-30   completed
     ↑ renewed_from
membership 502  child  1991-09-01 → 1992-06-30   completed
     ↑ renewed_from
membership 503  child  1992-09-01 → 1993-06-30   completed
```

"Why does this person have 15 membership rows?" is then answerable by following the chain
rather than by reasoning about dates. And a gap — a missing link — is visible as data.

### Current-membership queries

```sql
-- Is person X a member right now?
CREATE OR REPLACE FUNCTION is_current_member(p_person_id BIGINT)
RETURNS BOOLEAN LANGUAGE sql STABLE AS $$
    SELECT EXISTS (
        SELECT 1 FROM membership m
          JOIN membership_type mt ON mt.id = m.membership_type_id
         WHERE m.person_id = p_person_id
           AND m.status = 'active'
           AND m.valid_from <= CURRENT_DATE
           AND (m.valid_to IS NULL
                OR m.valid_to + mt.grace_period_days > CURRENT_DATE)
    );
$$;

-- Was person X a member on a given past date?
CREATE OR REPLACE FUNCTION was_member_on(p_person_id BIGINT, p_date DATE)
RETURNS BOOLEAN LANGUAGE sql STABLE AS $$
    SELECT EXISTS (
        SELECT 1 FROM membership m
         WHERE m.person_id = p_person_id
           AND m.valid_from <= p_date
           AND (m.valid_to IS NULL OR m.valid_to > p_date)
           -- include all terminal statuses: how it ended does not change that it existed
           AND m.status <> 'pending_payment'
    );
$$;

-- Person's current membership category (replaces any person.is_child check):
CREATE OR REPLACE FUNCTION current_member_category(p_person_id BIGINT)
RETURNS TEXT LANGUAGE sql STABLE AS $$
    SELECT mt.category
      FROM membership m JOIN membership_type mt ON mt.id = m.membership_type_id
     WHERE m.person_id = p_person_id AND m.status = 'active'
       AND m.valid_from <= CURRENT_DATE
       AND (m.valid_to IS NULL OR m.valid_to > CURRENT_DATE)
     ORDER BY m.valid_from DESC LIMIT 1;
$$;

-- Total years of membership, excluding gaps:
CREATE OR REPLACE FUNCTION membership_years(p_person_id BIGINT)
RETURNS NUMERIC LANGUAGE sql STABLE AS $$
    SELECT COALESCE(SUM(
        (COALESCE(m.valid_to, CURRENT_DATE) - m.valid_from)
    ), 0) / 365.25
      FROM membership m
     WHERE m.person_id = p_person_id AND m.status <> 'pending_payment';
$$;
```

`membership_years` sums the periods rather than subtracting the first join date from today.
The difference is the 14-year gap in the returning-member case, and getting it wrong
mislabels a returning member as having 36 years of service.

---

## 4. `membership_request_requirement`

```sql
CREATE TABLE requirement_code (
    code            TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    description     TEXT,
    is_blocking     BOOLEAN NOT NULL DEFAULT true,
    -- Blocking requirements must be satisfied before approval.
    has_expiry      BOOLEAN NOT NULL DEFAULT false,
    -- True for background checks, medical forms — things that lapse.
    default_validity_months INTEGER
);

CREATE TABLE membership_request_requirement (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    request_id      BIGINT NOT NULL REFERENCES membership_request(id),
    requirement_code TEXT NOT NULL REFERENCES requirement_code(code),

    status          TEXT NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending','satisfied','waived','failed')),

    satisfied_at    TIMESTAMPTZ,
    satisfied_by    BIGINT REFERENCES person(id),
    evidence_reference TEXT,
    -- Document id, external reference number, or a note explaining the evidence.
    -- Free text pointing at the durable record; the document layer is out of scope.

    expires_at      DATE,
    waived_by       BIGINT REFERENCES person(id),
    waived_reason   TEXT,

    notes           TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT ck_requirement_waived CHECK (
        status <> 'waived' OR (waived_by IS NOT NULL AND waived_reason IS NOT NULL)),
    CONSTRAINT ck_requirement_satisfied CHECK (
        status <> 'satisfied' OR satisfied_at IS NOT NULL)
);

CREATE INDEX ix_requirement_request ON membership_request_requirement (request_id);
CREATE INDEX ix_requirement_expiry  ON membership_request_requirement (expires_at)
    WHERE expires_at IS NOT NULL AND status = 'satisfied';
```

**Requirements are rows, not columns**, because the requirement set changes per membership
type and per year. Adding "police clearance" in 2027 must not be a schema migration.

**`is_blocking` matters.** Not every requirement blocks approval — some are collected for
record-keeping. The distinction must be explicit, or the review UI cannot tell a reviewer
what actually prevents approval.

**Why `evidence_reference` is free text rather than a FK.** The document layer is out of
scope (see [../open-questions.md](../open-questions.md)). When it exists, this becomes a
proper reference. Until then, a free-text pointer plus the audit log is honest about the
gap — better than a fake FK to a table that does not exist.

### Expiry is the point of this table

A background check is not a one-time fact. Modeled with `expires_at`, it becomes a
standing obligation that can be reported on:

```sql
-- Adult members whose background check expires within 90 days:
SELECT p.id, p.family_name, p.given_name, r.expires_at
  FROM membership_request_requirement r
  JOIN membership_request mr ON mr.id = r.request_id
  JOIN person p ON p.id = mr.person_id
 WHERE r.requirement_code = 'background_check'
   AND r.status = 'satisfied'
   AND r.expires_at BETWEEN CURRENT_DATE AND CURRENT_DATE + 90
   AND is_current_member(p.id);
```

---

## 5. `unit_membership`

```sql
CREATE TABLE unit_membership (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    person_id       BIGINT NOT NULL REFERENCES person(id),
    -- Deliberately person_id, NOT membership_id.
    --
    -- Why: a person's unit history must survive independently of how their
    -- organization membership is recorded. Imported 1998 rosters often have a unit
    -- but no formal membership row. Linking to membership would make those
    -- unrepresentable, and would break the whole historical dataset.
    --
    -- The trade-off: the schema cannot enforce "unit membership implies organization
    -- membership". Enforced by application + the integrity check in §8.

    org_unit_id     BIGINT NOT NULL REFERENCES org_unit(id),

    role_in_unit    TEXT CHECK (role_in_unit IN ('member','leader','assistant','guest')),
    -- A denormalised convenience for display and historical import. NOT an
    -- authorization fact — authority is in role_assignment.

    valid_from      DATE NOT NULL,
    valid_to        DATE,          -- NULL = current

    join_reason_code    TEXT,      -- 'initial' | 'transfer' | 'promotion' | 'reorganisation'
    leave_reason_code   TEXT,      -- 'age_out' | 'transfer_out' | 'unit_closed' | 'personal'

    is_primary      BOOLEAN NOT NULL DEFAULT true,
    -- Some people (adults especially) belong to several units.

    data_confidence TEXT NOT NULL DEFAULT 'high'
                    CHECK (data_confidence IN ('high','medium','low')),
    import_batch_id BIGINT,
    source          TEXT,          -- 'self' | 'staff' | 'legacy_import'

    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by      BIGINT REFERENCES person(id),
    updated_at      TIMESTAMPTZ,
    updated_by      BIGINT REFERENCES person(id),

    CONSTRAINT ck_unit_membership_period CHECK (
        valid_to IS NULL OR valid_to > valid_from)
);

-- The core invariant: a person is in a given unit only once at a time.
ALTER TABLE unit_membership ADD CONSTRAINT ex_unit_membership_no_overlap
    EXCLUDE USING gist (
        person_id   WITH =,
        org_unit_id WITH =,
        daterange(valid_from, valid_to, '[)') WITH &&
    );

CREATE INDEX ix_unit_membership_person ON unit_membership
    (person_id, valid_from DESC, valid_to);
CREATE INDEX ix_unit_membership_unit   ON unit_membership
    (org_unit_id, valid_from DESC, valid_to);
CREATE INDEX ix_unit_membership_current ON unit_membership (org_unit_id, person_id)
    WHERE valid_to IS NULL;
CREATE INDEX ix_unit_membership_period ON unit_membership USING gist
    (org_unit_id, daterange(valid_from, valid_to, '[)'));
```

**Why `person_id` and not `membership_id`.** This is a deliberate trade-off worth stating
plainly:

- **Chosen:** unit history is independent. Imported rosters without formal memberships are
  representable; a unit change does not require membership rows; queries about units are
  simpler and faster.
- **Cost:** nothing enforces that a person with a `unit_membership` has an organization
  `membership`. A data-entry error can put a non-member in a unit.
- **Mitigation:** an application-level validation, plus the nightly integrity check in §8.

The alternative — linking to `membership_id` — would make the entire 1990s dataset
unrepresentable, since those rosters have units and years but no membership workflow. That
is a decisive argument.

**"Who was in Troop 12 on 1 June 1998?"** is now a single indexed range query:

```sql
SELECT p.id, p.family_name, p.given_name
  FROM unit_membership um
  JOIN person p ON p.id = um.person_id
 WHERE um.org_unit_id = 12
   AND um.valid_from <= DATE '1998-06-01'
   AND (um.valid_to IS NULL OR um.valid_to > DATE '1998-06-01')
 ORDER BY p.family_name, p.given_name;
```

### Transfers and reorganizations

When a member moves units, **close the old row and open a new one.** Never update
`org_unit_id` on an existing row:

```sql
-- Transfer person 100 from unit 12 to unit 31 effective 1998-09-01
UPDATE unit_membership
   SET valid_to = DATE '1998-09-01',
       leave_reason_code = 'transfer_out',
       updated_at = now(),
       updated_by = :actor
 WHERE person_id = 100 AND org_unit_id = 12 AND valid_to IS NULL;

INSERT INTO unit_membership
    (person_id, org_unit_id, valid_from, join_reason_code, source, created_by)
VALUES (100, 31, DATE '1998-09-01', 'transfer', 'staff', :actor);
```

Rewriting the old row would destroy the answer to "where was this child in 2003?" — the
question the whole temporal design exists to answer.

### Unit reorganizations

When a unit is split or merged, members are transferred by the same close-and-open
pattern, with `join_reason_code = 'reorganisation'` and the
`org_unit_relationship` row recording the lineage. A bulk operation should be a single
named procedure with a dry-run mode — it will be run on hundreds of rows during an import
and must be testable before it commits.

---

## 6. Membership and the authorization system

Two permissions depend on membership state, and both need care:

**Can a lapsed member see their unit's events?** The resolver would need to evaluate
`is_current_member()`, which means the permission cache must be invalidated when a
membership lapses. This is a real coupling and a real cost.

Two options:

| Option | Cost | Benefit |
|--------|------|---------|
| Condition permissions on membership status | Cache invalidation on every membership transition; a lapse silently removes access, which is correct but surprising | Matches the common intent — lapsed members lose member access |
| Do not condition permissions on membership; revoke roles explicitly when a membership ends | A lapse leaves roles in place until someone acts | Simpler, decoupled; but requires a process to close out leaving members |

**Recommendation:** condition only the narrow set of permissions that genuinely require
current membership (member-only event signup, member pricing) and drive role revocation
from the membership lifecycle for the rest. Do not make the resolver's general answer
depend on membership state — it makes the permission system much harder to reason about.
Tracked in [../open-questions.md](../open-questions.md).

**A role assignment should not outlive the membership that justified it.** A nightly check:

```sql
-- People with an authority-bearing role but no current membership:
SELECT ra.id, p.family_name, p.given_name, r.code AS role, ra.valid_to
  FROM role_assignment ra
  JOIN role r ON r.id = ra.role_id
  JOIN person p ON p.id = ra.person_id
 WHERE ra.valid_to IS NULL
   AND r.scope_required
   AND NOT is_current_member(ra.person_id);
```

This is the "leaver with access" report. It is one of the highest-value operational
reports in the whole system — see
[../domain/06-authorization-model.md](../domain/06-authorization-model.md#3-roles--bundles-of-permissions).

---

## 7. Integrity checks

```sql
-- 1. Unit memberships without a corresponding organization membership at that time
SELECT um.id, um.person_id, um.org_unit_id, um.valid_from, um.valid_to
  FROM unit_membership um
 WHERE NOT EXISTS (
     SELECT 1 FROM membership m
      WHERE m.person_id = um.person_id
        AND m.status <> 'pending_payment'
        AND m.valid_from <= COALESCE(um.valid_to, um.valid_from)
        AND (m.valid_to IS NULL OR m.valid_to > um.valid_from));

-- 2. Child-category members in units that do not allow children
SELECT m.id, p.family_name, p.given_name, ou.name
  FROM membership m
  JOIN membership_type mt ON mt.id = m.membership_type_id
  JOIN org_unit ou ON ou.id = (
        SELECT org_unit_id FROM unit_membership
         WHERE person_id = m.person_id AND valid_to IS NULL LIMIT 1)
  JOIN person p ON p.id = m.person_id
  JOIN org_unit_type out_ ON out_.id = ou.unit_type_id
 WHERE mt.category = 'child' AND m.status = 'active'
   AND NOT out_.allows_children;

-- 3. Members whose type's max_age has been exceeded but are still active
--    (age-out not processed)
SELECT m.id, p.family_name, p.given_name, mt.code,
       EXTRACT(YEAR FROM age(CURRENT_DATE, p.birth_date)) AS age, mt.max_age
  FROM membership m
  JOIN membership_type mt ON mt.id = m.membership_type_id
  JOIN person p ON p.id = m.person_id
 WHERE m.status = 'active' AND m.valid_to IS NULL
   AND mt.max_age IS NOT NULL AND p.birth_date IS NOT NULL
   AND EXTRACT(YEAR FROM age(CURRENT_DATE, p.birth_date)) > mt.max_age;

-- 4. Approved requests that never produced a membership
SELECT mr.* FROM membership_request mr
 WHERE mr.status = 'approved' AND mr.membership_id IS NULL
   AND mr.decided_at < now() - INTERVAL '7 days';

-- 5. Blocking requirements unsatisfied on approved requests
SELECT mr.id, r.requirement_code
  FROM membership_request mr
  JOIN membership_request_requirement r ON r.request_id = mr.id
  JOIN requirement_code rc ON rc.code = r.requirement_code
 WHERE mr.status = 'approved' AND rc.is_blocking
   AND r.status NOT IN ('satisfied','waived');

-- 6. Renewal chains with a gap or a broken link
SELECT m.id FROM membership m
 WHERE m.renewed_from_membership_id IS NOT NULL
   AND NOT EXISTS (SELECT 1 FROM membership pm
                    WHERE pm.id = m.renewed_from_membership_id);

-- 7. Overlapping memberships of DIFFERENT types (permitted but worth reviewing)
SELECT a.person_id, a.id AS m1, b.id AS m2, a.membership_type_id, b.membership_type_id
  FROM membership a JOIN membership b
    ON a.person_id = b.person_id AND a.id < b.id
   AND daterange(a.valid_from, a.valid_to, '[)') &&
       daterange(b.valid_from, b.valid_to, '[)')
 WHERE a.status = 'active' AND b.status = 'active';
```

Checks 3 and 4 are operational (work not yet done); 1, 5, 6 and 7 are data-quality
(cases the schema could not prevent). Both categories belong in a nightly job, and the
operational ones should produce worklists, not just logs.

---

## 8. Seed data

```sql
INSERT INTO membership_type
    (code, name, description, category, requires_background_check,
     requires_guardian_consent, min_age, max_age, duration_months,
     grace_period_days, is_self_registerable, sort_order)
VALUES
    ('child',    'Child Member',     'Youth participant',            'child',   false, true,   6,  18, 12, 30, true,  10),
    ('adult',    'Adult Member',     'Adult participant and leader', 'adult',   true,  false, 18, NULL, 12, 30, true,  20),
    ('counselor','Counselor',        'Trained adult leader',         'adult',   true,  false, 18, NULL, 12, 30, true,  30),
    ('honorary', 'Honorary Member',  'Granted by the organization',  'special', false, false,NULL, NULL, NULL,  0, false, 40),
    ('lifetime', 'Lifetime Member',  'Indefinite membership',        'special', false, false,NULL, NULL, NULL,  0, false, 50);

INSERT INTO requirement_code (code, name, is_blocking, has_expiry, default_validity_months) VALUES
    ('guardian_consent',   'Guardian consent',              true,  false, NULL),
    ('background_check',   'Background check',              true,  true,  36),
    ('medical_form',       'Medical form',                  true,  true,  12),
    ('references',         'References',                    true,  false, NULL),
    ('previous_unit_transfer', 'Transfer confirmation',     false, false, NULL),
    ('photo_consent',      'Photo consent',                 false, false, NULL);
```

> Placeholder values; the ages, durations, and grace period are assumptions. See
> [../open-questions.md](../open-questions.md).

---

## 9. Open issues

- Whether a person may hold **one** open membership of any type, or several of different
  types (§3).
- The real age limits, membership durations, and grace period (§8).
- Does membership activate on approval or on payment? Affects whether
  `pending_payment` is a membership status at all, or only a fee state (§3).
- Whether `outstanding_balance` should exist as a denormalised column or be computed
  (§3) — depends on the finance design in [07-finance.md](07-finance.md).
- Whether permissions should be conditioned on membership status (§6) — recommend a narrow
  set only.
- Whether `unit_membership` should reference `membership_id` in addition to `person_id`,
  to get referential integrity without losing the import case. Possible as a nullable
  column, but it would be unenforced for imports.

All tracked in [../open-questions.md](../open-questions.md).
