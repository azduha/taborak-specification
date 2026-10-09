# Data Model — Membership

`membership_type`, `membership`, `membership_request`, and `unit_participation`.

Domain rationale: [../domain/05-membership-lifecycle.md](../domain/05-membership-lifecycle.md).

---

## 1. `membership_type` — one row, kept as a table

```sql
CREATE TABLE membership_type (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    code            TEXT NOT NULL UNIQUE,   -- 'member' — and nothing else, for now
    name            TEXT NOT NULL,
    description     TEXT,

    duration_months INTEGER NOT NULL DEFAULT 12,
    -- 12: the fee is yearly. Kept as a column rather than a constant so a type with a
    -- different term could be added without a schema change.

    expiry_month    SMALLINT NOT NULL DEFAULT 1 CHECK (expiry_month BETWEEN 1 AND 12),
    expiry_day      SMALLINT NOT NULL DEFAULT 1 CHECK (expiry_day BETWEEN 1 AND 31),
    -- WHEN THE FEE EXPIRES (D-047): 1 January. The organizational year runs with the
    -- calendar, so "a member this year" means what a reader expects, and the sweep, the
    -- campaign and the reports all land on a boundary nobody has to look up.
    --
    -- These are columns, not a constant in a scheduled job, for the reason the user gave
    -- for the window below: the date is a parameter the organization may move, and moving
    -- it must not require a code change. Every lapse date, the yearly sweep and the
    -- renewal worklist derive from these two values.

    renewal_grace_days INTEGER NOT NULL DEFAULT 60,
    -- The renewal window after valid_to, during which a payment restores the
    -- membership WITHOUT re-applying and backdates the new period to the expiry date.
    -- Dates, not a status: the person is expired throughout (D-040). 60 days (D-048).
    --
    -- Read it from here; never hardcode 60 in a job or a front end (D-048). The
    -- requirement attached to that answer was precisely that the value stays tunable.

    is_self_registerable BOOLEAN NOT NULL DEFAULT true,
    requires_approval BOOLEAN NOT NULL DEFAULT true,
    sort_order      INTEGER NOT NULL DEFAULT 0,

    valid_from      DATE,
    valid_to        DATE,

    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT ck_membership_type_period CHECK (
        valid_to IS NULL OR valid_from IS NULL OR valid_to > valid_from)
);

CREATE INDEX ix_membership_type_current ON membership_type (code) WHERE valid_to IS NULL;
```

### Why this table still exists with one row

**There is exactly one membership** (D-037). Everyone who is a member holds
`membership_type = 'member'`, the fee is flat and per person, and being a counselor or a
leader is a **position**, never a type.

The table survives rather than collapsing into a constant for two reasons:

1. **Consistency with the design's own principle.** Vocabularies are rows, not enums —
   the same argument that keeps `org_unit_type` and `position` as tables. A second kind of
   membership (a supporting or honorary one) would then be a data change.
2. **A place for the organizational calendar to live.** The term, the expiry date and the
   renewal window are genuinely type-dependent parameters even when there is one type — and
   they are the parameters most likely to be tuned. Putting them in a row rather than in code
   is what makes *"it should not be hard to modify"* ([D-048](../decisions/decision-log.md#d-048--the-renewal-window-is-60-days-and-is-a-configuration-parameter))
   true by construction rather than by discipline.

The cost is honest and small: an FK that currently always holds one value. Recorded here
rather than hidden.

### What was removed, and why

| Removed | Reason |
|---|---|
| `category` (`child`/`adult`/`special`) | Membership is ageless (D-038). Age is a fact about the person. |
| `min_age`, `max_age` | No age floor, ceiling, or automatic age-out. |
| `requires_background_check` | The system records no background checks (D-043). |
| `requires_references`, `requires_guardian_consent` | Nothing gates a request but identity and payment (D-044). |
| `allows_concurrent` | With one type and a person-scoped overlap constraint, this cannot arise. |
| `grace_period_days` (as a status) | Replaced by `renewal_grace_days` — a window, not a state (D-040). |
| `fee_schedule_id` | The fee is flat and per person (D-037), so there is nothing type-specific to schedule. The schedule attaches to the **obligation** instead — [07-finance.md §2](07-finance.md#2-minimal-provisional-shape). |

**`ck_membership_type_ages`** goes with them; there are no ages to check.

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
    -- DENORMALISED from fee_obligation/payment. 07-finance.md §3 recommends DROPPING
    -- this column in favour of v_fee_obligation_balance — a wrong balance suspends the
    -- wrong child. Kept here only until that decision is taken. NULL for imported
    -- historical memberships with no payment data.

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

-- THE critical constraint: one person, one open membership, full stop.
CREATE EXTENSION IF NOT EXISTS btree_gist;

ALTER TABLE membership ADD CONSTRAINT ex_membership_no_overlap
    EXCLUDE USING gist (
        person_id WITH =,
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
CREATE INDEX ix_membership_expiry   ON membership (valid_to)
    WHERE valid_to IS NOT NULL AND status = 'active';
-- Drives the renewal worklist: who expires soon, who is in their renewal window.
```

### The constraint dropped `membership_type_id` — that is the point

The old constraint was scoped to the type, to permit an honorary member who is also an
active member. **With one membership type (D-037) that case cannot arise**, so the type is
gone from the constraint and "one person, one open membership" becomes an enforceable
invariant rather than a convention.

This is what makes the membership gate (D-039) implementable: `is_current_member()` is a
question about **one row, one status, one date**, not a question that has to reconcile three
concurrent memberships.

### `renewed_from_membership_id` and the renewal window

When a person pays inside the renewal window
([D-040](../decisions/decision-log.md#d-040--the-fee-expires-yearly-a-date-tracked-renewal-window-replaces-a-grace-status)),
the new membership's `valid_from` is set to the **previous row's `valid_to`**, not to the
payment date. Two consequences worth stating:

- **The history shows continuous coverage** — no gap, no spurious "returning member".
- **The person is nevertheless expired during the window** (D-040). The two facts are
  compatible because the window is a *date range*, not a status: they were not a member
  while it was open, and the record of that period is filled in retrospectively once they
  pay. Nothing needs backdating in the audit sense, because the new row's as-of start is the
  expiry date and its audit time is the payment date — the two-times distinction in
  [00-conventions.md](00-conventions.md).

A payment *after* the window opens the new membership at the payment date, and the gap is
real.

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
membership 501  member  1990-09-01 → 1991-06-30   completed
     ↑ renewed_from
membership 502  member  1991-09-01 → 1992-06-30   completed
     ↑ renewed_from
membership 503  member  1992-09-01 → 1993-06-30   completed
```
*(The type is `member` on every row — there is only one type, and the person's age is not
part of it: [§1](#1-membership_type--one-row-kept-as-a-table), D-037, D-038.)*

"Why does this person have 15 membership rows?" is then answerable by following the chain
rather than by reasoning about dates. And a gap — a missing link — is visible as data.

### Current-membership queries

```sql
-- Is person X a member right now?
-- NOTE: no grace coalescing. A lapsed membership is lapsed; the renewal window
-- (§6) is a date range for rejoining, not a state in which the person is a member.
CREATE OR REPLACE FUNCTION is_current_member(p_person_id BIGINT)
RETURNS BOOLEAN LANGUAGE sql STABLE AS $$
    SELECT EXISTS (
        SELECT 1 FROM membership m
         WHERE m.person_id = p_person_id
           AND m.status = 'active'
           AND m.valid_from <= CURRENT_DATE
           AND (m.valid_to IS NULL OR m.valid_to > CURRENT_DATE)
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

-- The organizational calendar for a given year, read from the parameters and never from
-- a constant (D-047). Returns the expiry date of the year containing p_at.
CREATE OR REPLACE FUNCTION membership_expiry_date(p_at DATE DEFAULT CURRENT_DATE)
RETURNS DATE LANGUAGE sql STABLE AS $$
    SELECT make_date(
             EXTRACT(YEAR FROM p_at)::INT,
             mt.expiry_month,
             mt.expiry_day)
      FROM membership_type mt
     WHERE mt.code = 'member';
$$;

-- May this person renew without re-applying? (D-040: expired, but inside the window.)
-- This is the distinction a 'grace_period_days' membership status would have blurred:
-- they are NOT a member, and they MAY rejoin cheaply.
--
-- 60 days, read from the row (D-048). Not a member during the window: this answers
-- "may they rejoin cheaply?", never "do they have access?".
CREATE OR REPLACE FUNCTION in_renewal_window(p_person_id BIGINT,
                                             p_at DATE DEFAULT CURRENT_DATE)
RETURNS BOOLEAN LANGUAGE sql STABLE AS $$
    SELECT EXISTS (
        SELECT 1
          FROM membership m
          JOIN membership_type mt ON mt.id = m.membership_type_id
         WHERE m.person_id = p_person_id
           AND m.valid_to IS NOT NULL
           AND m.valid_to <= p_at
           AND m.valid_to + mt.renewal_grace_days > p_at
    );
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

**`current_member_category()` is gone.** It existed to answer "is this person currently a
child or an adult?", which is no longer a question the membership table can answer, because
membership is ageless (D-038). Age is a fact about the person:

```sql
-- Is this person a minor? A fact about the person, not about their membership.
CREATE OR REPLACE FUNCTION is_minor(p_person_id BIGINT, p_at DATE DEFAULT CURRENT_DATE)
RETURNS BOOLEAN LANGUAGE sql STABLE AS $$
    SELECT p.birth_date IS NOT NULL
       AND p_at < p.birth_date + INTERVAL '18 years'
      FROM person p WHERE p.id = p_person_id;
$$;
```

This matters for **guardianship and safeguarding**, which are where age legitimately bears —
not for whether someone may be a member.

---

## 4. No request requirements — removed entirely

`requirement_code` and `membership_request_requirement` **do not exist** (D-044).

**Why.** Your answer, asked what a membership request must contain in order to be accepted:
*"Just identity and the fee — nothing to verify."* The option of keeping the mechanism as
empty infrastructure was offered and not taken, so it is gone rather than left dangling.

**What a request therefore is:** a person, a submitted timestamp, a reviewer, a decision, and
a payment. The `membership_request` table in [§2](#2-membership_request) is complete as it
stands — it never referenced requirements except through this table.

**Guardian consent is unaffected.** It was never a *membership* requirement; it belongs to
the guardianship layer, where it is a relationship fact rather than a checklist item. See
[04-relationships.md](04-relationships.md#2-guardianship_permission).

**If a requirement ever appears** — a form, an interview, a document — the honest starting
point is to add the table back deliberately, with the requirement that made it necessary
recorded as a decision. The removed design was general enough to carry one; it is recorded
in the decision log rather than deleted from history.

---

## 5. `unit_participation`

**Renamed from `unit_membership`.** Belonging to a sub-unit is **participation**, not a
species of membership (D-041). The old name asserted something untrue, and the rename is the
fix.

```sql
CREATE TABLE unit_participation (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    person_id       BIGINT NOT NULL REFERENCES person(id),
    -- Deliberately person_id, NOT membership_id.
    --
    -- Why: participation history must survive independently of how organization
    -- membership is recorded. Imported 1998 rosters often have a unit and a year but
    -- no formal membership row. Linking to membership would make those
    -- unrepresentable, and would break the whole historical dataset.
    --
    -- The trade-off: the schema cannot enforce "participation implies membership".
    -- Enforced by application + the integrity check in §7.

    org_unit_id     BIGINT NOT NULL REFERENCES org_unit(id),
    -- May be the ROOT unit. A participation row on the root is created alongside
    -- each membership, so that "everyone in unit X" is one uniform query whether X
    -- is the organization or a Thursday-evening pack. See §5.1.

    role_in_unit    TEXT CHECK (role_in_unit IN ('member','leader','assistant','guest')),
    -- A denormalised convenience for display and historical import. NOT an
    -- authorization fact — authority is in role_assignment.

    valid_from      DATE NOT NULL,
    valid_to        DATE,          -- NULL = current

    join_reason_code    TEXT,      -- 'initial' | 'transfer' | 'promotion' | 'reorganisation'
    leave_reason_code   TEXT,      -- 'transfer_out' | 'unit_closed' | 'stopped_attending'

    is_primary      BOOLEAN NOT NULL DEFAULT true,
    -- Which group to show first, for a person in several.

    data_confidence TEXT NOT NULL DEFAULT 'high'
                    CHECK (data_confidence IN ('high','medium','low')),
    import_batch_id BIGINT,
    source          TEXT,          -- 'self' | 'staff' | 'legacy_import'

    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by      BIGINT REFERENCES person(id),
    updated_at      TIMESTAMPTZ,
    updated_by      BIGINT REFERENCES person(id),

    CONSTRAINT ck_unit_participation_period CHECK (
        valid_to IS NULL OR valid_to > valid_from)
);

-- A person takes part in a given unit only once at a time.
ALTER TABLE unit_participation ADD CONSTRAINT ex_unit_participation_no_overlap
    EXCLUDE USING gist (
        person_id   WITH =,
        org_unit_id WITH =,
        daterange(valid_from, valid_to, '[)') WITH &&
    );

CREATE INDEX ix_unit_participation_person ON unit_participation
    (person_id, valid_from DESC, valid_to);
CREATE INDEX ix_unit_participation_unit   ON unit_participation
    (org_unit_id, valid_from DESC, valid_to);
CREATE INDEX ix_unit_participation_current ON unit_participation (org_unit_id, person_id)
    WHERE valid_to IS NULL;
CREATE INDEX ix_unit_participation_period ON unit_participation USING gist
    (org_unit_id, daterange(valid_from, valid_to, '[)'));
```

### 5.1 A participation row on the root unit

When a membership is created, a matching **`unit_participation` row for the root unit** is
created over the same period, and similarly closed when the membership ends.

This buys one thing: **"everyone in unit X" is one query, with one shape, at every level.**

```sql
-- Works whether :unit is the organization (depth 0) or a Thursday group (depth 4).
SELECT p.id, p.family_name, p.given_name
  FROM unit_participation up
  JOIN person p ON p.id = up.person_id
 WHERE up.org_unit_id = :unit
   AND up.valid_from <= :d
   AND (up.valid_to IS NULL OR up.valid_to > :d)
 ORDER BY p.family_name, p.given_name;
```

Without it, "who is in the organization?" would be a query against `membership` and "who is
in a pack?" a query against `unit_participation` — two shapes for one question, and every
report would have to know which case it was in.

**The redundancy is deliberate and bounded.** The root row and the membership always have
the same period, so the root row is derivable — it is maintained by trigger, and integrity
check 1 in [§7](#7-integrity-checks) verifies the two agree. The alternative, a `UNION` in
every roster query, is worse.

**The root row is the only participation row that is *extended* rather than closed and
reopened** ([D-050](../decisions/decision-log.md#d-050--a-renewal-inside-the-window-extends-the-existing-root-participation-row)).
A transfer between sub-units is still close-and-open ([§5.2](#52-transfers-between-sub-units-are-cheap));
the root row is different because it mirrors a period that is itself backdated:

```sql
-- The yearly expiry sweep. The MEMBERSHIP gets a valid_to of the expiry date and its
-- status moves to 'lapsed'. The root participation row is NOT closed with it — it is
-- moved forward to the same date, so it is neither open-ended nor a second row (D-050).
UPDATE unit_participation up
   SET valid_to = m.valid_to
  FROM membership m, org_unit root
 WHERE up.person_id = m.person_id
   AND up.org_unit_id = root.id
   AND root.parent_unit_id IS NULL
   AND up.valid_to IS NULL;

-- A renewal inside the window opens a NEW membership row starting at the expiry date
-- ([D-016], D-040). The root row is then stretched to the new period's end, which is
-- exactly "extend the existing row": one row spanning both periods, no gap, no overlap.
UPDATE unit_participation up
   SET valid_to = new_m.valid_to,
       updated_at = now()
  FROM membership new_m, org_unit root
 WHERE up.person_id = new_m.person_id
   AND up.org_unit_id = root.id
   AND root.parent_unit_id IS NULL
   AND new_m.valid_from = up.valid_to;   -- contiguity, not a membership FK
```

> **The join in the second statement is the whole of D-050, and it is easy to get wrong.**
> The root row is matched to the *new* membership by **person and date**, not through
> `renewed_from_membership_id` — the participation row carries no membership FK, deliberately
> ([D-008](../open-questions.md#d-8--should-unit_participation-reference-the-membership), §5).
> So the condition is `new_m.valid_from = up.valid_to`: the renewal begins exactly where the
> root row was swept to. Anything looser would stretch a single row across a genuine
> post-window rejoin, where the gap is real and must stay.

> **This erases the visual evidence of the lapse, and that is the accepted trade (D-050).**
> A person who lapsed and renewed looks, in `unit_participation`, exactly like a person who
> never lapsed. The lapse is still fully visible in `membership`, which is the authority on
> payment. The participation table answers "who was in this unit when" — a roster question —
> and for that question a child who was in the pack across the period has exactly one answer.

**"Who was in the 4th Pack on 1 June 1998?"** is then exactly the query above.

### 5.2 Transfers between sub-units are cheap

Because participation is not membership (D-041), moving a person between groups is **one row
edit** — close one, open another. Nothing about their membership, their fee, or their status
as a member changes.

```sql
-- Move person 100 from pack 12 to pack 31 effective 1998-09-01
UPDATE unit_participation
   SET valid_to = DATE '1998-09-01',
       leave_reason_code = 'transfer_out',
       updated_at = now(),
       updated_by = :actor
 WHERE person_id = 100 AND org_unit_id = 12 AND valid_to IS NULL;

INSERT INTO unit_participation
    (person_id, org_unit_id, valid_from, join_reason_code, source, created_by)
VALUES (100, 31, DATE '1998-09-01', 'transfer', 'staff', :actor);
```

Rewriting the old row would destroy the answer to "where was this child in 2003?" — the
question the whole temporal design exists to answer. Close and open; never update
`org_unit_id` in place.

**Under the old model this was much more expensive**: a "unit membership" was a membership,
so moving a child between groups raised questions about which membership was which and
whether a fee was owed twice. Participation removes the question.

### Unit reorganizations

When a unit is split or merged, members are transferred by the same close-and-open
pattern, with `join_reason_code = 'reorganisation'` and the
`org_unit_relationship` row recording the lineage. A bulk operation should be a single
named procedure with a dry-run mode — it will be run on hundreds of rows during an import
and must be testable before it commits.

---

## 6. Membership and the authorization system

**The resolver evaluates membership state.** This is settled (D-039) and it is the single
largest coupling in the design, so it is worth stating in full rather than in a footnote.

```
A role grants access ONLY IF the holder has a current membership,
    unless  role.requires_membership = false    (appointed counselors, local leaders)
    or      the channel is guardianship         (a legal relationship, not a membership)
    or      the channel is ownership            (your own record — see below)
```

**The carve-outs, and why each exists:**

| Carve-out | Why |
|---|---|
| **Guardianship** | A parent's authority over their child comes from a legal relationship. An unpaid fee must not make a parent unable to act for their child. |
| **Appointed counselors and local leaders** | The organization needs them present regardless of their own fee status. Marked per-role with `requires_membership = false`. |
| **Ownership** | Otherwise a lapse locks a person out of the very screen they renew on. |

**The cost, named plainly:**

- **The permission cache must be invalidated on every membership transition** — including
  the yearly expiry sweep, which is a bulk event touching every member at once. The cache
  design has to be built for this from the start; retrofitting it is where the bugs will be.
- **A lapse silently removes access.** That is the intent, but "why can't I see this?" now
  has an answer that is a date rather than a decision.
- **`role.requires_membership` changed meaning** — from a flag that drove a report to a value
  the resolver enforces.

**The "leaver with access" report remains valuable**, but its purpose changes. It no longer
*prevents* access — the resolver already does that — so what it now detects is a role that
should have been **closed** and was not. That is still worth a worklist, because a stale
assignment silently springs back to life the moment the person renews:

```sql
-- Role assignments held by non-members. The resolver blocks these today, but the
-- assignment should be closed, not merely dormant.
SELECT ra.id, p.family_name, p.given_name, r.code AS role, ra.valid_to,
       r.requires_membership AS enforced
  FROM role_assignment ra
  JOIN role r ON r.id = ra.role_id
  JOIN person p ON p.id = ra.person_id
 WHERE ra.valid_to IS NULL
   AND NOT is_current_member(ra.person_id)
 ORDER BY r.requires_membership DESC;
```

**Dormant authority is a real hazard.** A membership that lapses and is renewed a year later
would otherwise resurrect every role the person held in the interim, including ones a human
had quietly decided not to reinstate. Closing the assignment at the same time as the
membership is the honest fix; this report finds the ones that were missed.

**A role assignment should not outlive the membership that justified it.**

---

## 7. Integrity checks

```sql
-- 1. Participation rows without a corresponding organization membership at that time
SELECT up.id, up.person_id, up.org_unit_id, up.valid_from, up.valid_to
  FROM unit_participation up
 WHERE NOT EXISTS (
     SELECT 1 FROM membership m
      WHERE m.person_id = up.person_id
        AND m.status <> 'pending_payment'
        AND m.valid_from <= COALESCE(up.valid_to, up.valid_from)
        AND (m.valid_to IS NULL OR m.valid_to > up.valid_from));

-- 1b. The ROOT participation row disagreeing with the membership it mirrors (§5.1).
--     The root row is maintained by trigger; this detects the trigger drifting.
SELECT m.id, m.valid_from, m.valid_to, up.valid_from, up.valid_to
  FROM membership m
  JOIN org_unit root ON root.parent_unit_id IS NULL
  JOIN unit_participation up
    ON up.person_id = m.person_id AND up.org_unit_id = root.id
 WHERE up.valid_from IS DISTINCT FROM m.valid_from
    OR up.valid_to   IS DISTINCT FROM m.valid_to;

-- 2. Participants in units that do not allow minors — a unit that does not
--    supervise minors may not have any placed in it. (Safeguarding, not membership:
--    membership itself is ageless, D-038.)
SELECT up.id, p.family_name, p.given_name, ou.name
  FROM unit_participation up
  JOIN person p ON p.id = up.person_id
  JOIN org_unit ou ON ou.id = up.org_unit_id
  JOIN org_unit_type out_ ON out_.id = ou.unit_type_id
 WHERE up.valid_to IS NULL
   AND NOT out_.allows_minors
   AND p.birth_date IS NOT NULL
   AND CURRENT_DATE < p.birth_date + INTERVAL '18 years';

-- 3. Non-members holding a role that requires membership.
--    The resolver blocks these (D-039), so this is not an access breach — it is a
--    stale assignment that will spring back to life when the person renews (§6).
SELECT ra.id, p.family_name, p.given_name, r.code, ra.valid_to
  FROM role_assignment ra
  JOIN role r ON r.id = ra.role_id
  JOIN person p ON p.id = ra.person_id
 WHERE ra.valid_to IS NULL AND r.requires_membership
   AND NOT is_current_member(ra.person_id);

-- 4. Approved requests that never produced a membership
SELECT mr.* FROM membership_request mr
 WHERE mr.status = 'approved' AND mr.membership_id IS NULL
   AND mr.decided_at < now() - INTERVAL '7 days';

-- 5. Memberships expiring soon — the renewal campaign worklist (§6 of domain/05)
SELECT m.id, p.family_name, p.given_name, m.valid_to
  FROM membership m
  JOIN person p ON p.id = m.person_id
 WHERE m.status = 'active'
   AND m.valid_to BETWEEN CURRENT_DATE AND CURRENT_DATE + 90;

-- 6. Renewal chains with a gap or a broken link
SELECT m.id FROM membership m
 WHERE m.renewed_from_membership_id IS NOT NULL
   AND NOT EXISTS (SELECT 1 FROM membership pm
                    WHERE pm.id = m.renewed_from_membership_id);

-- 7. Renewals inside the window whose new period does NOT start at the previous
--    expiry date. The renewal rule (D-040) backdates the new period, so a mismatch
--    means either a genuine post-window rejoin or a bug.
SELECT m.id, m.valid_from, pm.valid_to AS previous_expiry,
       m.valid_from - pm.valid_to AS gap_days
  FROM membership m
  JOIN membership pm ON pm.id = m.renewed_from_membership_id
 WHERE m.valid_from <> pm.valid_to
   AND m.valid_from < pm.valid_to + INTERVAL '91 days';
```

**Check 3 is the one that matters most now.** Under D-039 the resolver already blocks a
non-member's roles, so this is no longer an access breach — but it detects *dormant*
authority, which is the failure mode the membership gate introduces: a role nobody closed
that silently reactivates on renewal.

**Check 5 is operational** (a worklist for the renewal campaign), and **check 1b** guards the
one deliberate redundancy in the model (§5.1). The rest are data-quality checks for cases the
schema cannot prevent.

---

## 8. Seed data

```sql
INSERT INTO membership_type
    (code, name, description, duration_months, expiry_month, expiry_day,
     renewal_grace_days, is_self_registerable, sort_order)
VALUES
    ('member', 'Member', 'A member of the organization',
     12, 1, 1, 60, true, 10);
```

**One row, and that is the whole vocabulary** (D-037). The fee is flat and per person, so
there is nothing to vary by type; being a counselor or leader is a position, not a type; and
membership is ageless, so there are no age limits to seed (D-038).

**The calendar is now settled** — 1 January, 60 days
([D-047](../decisions/decision-log.md#d-047--the-fee-expires-on-1-january),
[D-048](../decisions/decision-log.md#d-048--the-renewal-window-is-60-days-and-is-a-configuration-parameter)).
The term (12 months) remains a placeholder that nothing currently depends on. All four are
columns rather than constants, so tuning any of them is an `UPDATE`, not a release.

> **The one rule about these four values: read them from the row.** A scheduled job, a front
> end or a report that contains the literal `60` or `1` has quietly reverted a parameter to a
> constant, and the organization will discover it the first time it changes its mind.

**No `requirement_code` seed.** That table does not exist (D-044). The formerly seeded rows
— `guardian_consent`, `background_check`, `medical_form`, `references`,
`previous_unit_transfer`, `photo_consent` — are all gone:
consent moved to the guardianship layer where it belongs, background checks are not recorded
at all (D-043), and the rest were never required.

---

## 9. Open issues

- The real membership term and renewal-window length (§1, §8) — the two remaining
  type-level parameters.
- Whether `outstanding_balance` should exist as a denormalised column or be computed
  (§3) — depends on the finance design in [07-finance.md](07-finance.md).
- Whether `unit_participation` should reference `membership_id` in addition to `person_id`,
  to get referential integrity without losing the import case. Possible as a nullable
  column, but it would be unenforced for imports.
- What the root-unit participation row does when a membership is renewed inside the
  window — it must extend across the (retrospectively filled) period without creating an
  overlapping row (§5.1).

**Resolved and no longer open**, kept visible so the reasoning survives: whether a person
may hold several open memberships (no — one type, person-scoped constraint, §3); whether
membership activates on payment (yes, §3); whether permissions depend on membership state
(yes, with carve-outs — D-039, §6); the age limits and age-out (§8); the grace period as a
status (§6); and the whole requirement mechanism (§4).

All tracked in [../open-questions.md](../open-questions.md).
