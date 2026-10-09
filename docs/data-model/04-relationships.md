# Data Model — Relationships

`guardianship`, `guardianship_permission`, `household`, `household_member`.

Domain rationale: [../domain/02-actors.md](../domain/02-actors.md#5-acting-on-behalf).

---

## 1. `guardianship`

```sql
CREATE EXTENSION IF NOT EXISTS btree_gist;   -- idempotent; also declared in 03-membership.md

CREATE TABLE guardianship (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    guardian_person_id  BIGINT NOT NULL REFERENCES person(id),
    dependent_person_id BIGINT NOT NULL REFERENCES person(id),

    relationship    TEXT NOT NULL CHECK (relationship IN
                        ('parent','legal_guardian','foster_parent','step_parent',
                         'grandparent','sibling','other')),
    -- 'sibling' and 'other' are included because the organization will encounter
    -- cases that do not fit, and forcing them into 'parent' corrupts the data.
    -- A 19-year-old legal guardian of a 12-year-old sibling is real.

    valid_from      DATE NOT NULL,
    valid_to        DATE,          -- NULL = current. Set when the child turns 18,
                                   -- or when a court order changes.

    is_primary_contact BOOLEAN NOT NULL DEFAULT false,
    -- Who the organization calls in an emergency. INDEPENDENT of permissions:
    -- a grandparent with no system access can still be the emergency contact.
    -- See domain/02-actors.md §6.

    is_legal_decision_maker BOOLEAN NOT NULL DEFAULT false,
    -- Distinguishes who may make legal decisions (consent for medical treatment,
    -- travel) from who provides day-to-day care. Often different people.

    lives_with      BOOLEAN,
    -- Nullable: false = guardianship without cohabitation (shared custody,
    -- guardian in another city). Relevant to contact routing, not to authority.

    custody_arrangement TEXT,      -- free text: a description, not a computable fact
    source          TEXT,          -- 'self' | 'staff' | 'import' | 'court_order'
    verified_at     TIMESTAMPTZ,
    verified_by     BIGINT REFERENCES person(id),
    evidence_reference TEXT,
    -- Where the proof of guardianship is filed. For legal guardianship this matters:
    -- the organization must be able to show it checked.

    ended_reason_code TEXT,
    ended_note      TEXT,

    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by      BIGINT REFERENCES person(id),
    updated_at      TIMESTAMPTZ,
    updated_by      BIGINT REFERENCES person(id),
    import_batch_id BIGINT,

    CONSTRAINT ck_guardianship_period CHECK (
        valid_to IS NULL OR valid_to > valid_from),
    CONSTRAINT ck_guardianship_distinct CHECK (
        guardian_person_id <> dependent_person_id)
);

-- One current guardianship per (guardian, dependent) pair:
ALTER TABLE guardianship ADD CONSTRAINT ex_guardianship_no_overlap
    EXCLUDE USING gist (
        guardian_person_id  WITH =,
        dependent_person_id WITH =,
        daterange(valid_from, valid_to, '[)') WITH &&
    );

CREATE INDEX ix_guardianship_guardian  ON guardianship (guardian_person_id, valid_to);
CREATE INDEX ix_guardianship_dependent ON guardianship (dependent_person_id, valid_to);
CREATE INDEX ix_guardianship_current   ON guardianship (dependent_person_id)
    WHERE valid_to IS NULL;
CREATE INDEX ix_guardianship_primary   ON guardianship (dependent_person_id)
    WHERE valid_to IS NULL AND is_primary_contact;
```

### The relation is a general graph, not a two-level hierarchy

The schema permits:

- **One guardian → many dependents.** Multiple `guardianship` rows with the same guardian.
  This is your "one parent can manage multiple children".
- **Many guardians → one dependent.** Brothers' grandparents, both parents, a legal
  guardian plus a step-parent. Nothing assumes a child has exactly two guardians.
- **A person being both.** Person A is guardian of B, and dependent of C. Costs nothing to
  allow, and avoids a rewrite when a member reaches majority and becomes guardian to a
  younger sibling.

You specified the first two explicitly. The third is free.

### Per-dependent authority

Authority is **per `guardianship` row**, not per person. A parent can hold full
`dependent.admin` for one child and only `dependent.event.view` for another — a realistic
shared-custody arrangement, and one the schema must be able to represent without inventing
a second parent identity.

### Guardianship ends

`valid_to` is set when:

- the dependent reaches majority (a date the system can compute from `person.birth_date`,
  but **should not set automatically** — see below);
- a court order changes the arrangement;
- the guardian dies.

**Do not auto-expire guardianship at majority without review.** *Assumption:* in many
jurisdictions a parent's authority over health and school records does not end at 18, and
in some it ends at a different age. Compute the candidate date, put it on a review queue,
and let staff close the row. An automatic cutoff will silently strip a parent's access in
a case where it was still legally valid. Tracked in
[../open-questions.md](../open-questions.md).

### `is_primary_contact` vs `is_legal_decision_maker`

Two distinct questions that a single "is primary parent" flag conflates:

| Question | Column |
|----------|--------|
| Who do we phone at 2am when the child is injured at camp? | `is_primary_contact` |
| Who may sign the consent form for that treatment? | `is_legal_decision_maker` |

They are often different people, and conflating them means either the wrong person is
called or an invalid consent is accepted. Both are `BOOLEAN` on the row rather than a
single `is_primary`, because a child can have two primary contacts and one decision maker.

---

## 2. `guardianship_permission`

```sql
CREATE TABLE guardianship_permission (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    guardianship_id BIGINT NOT NULL REFERENCES guardianship(id),
    -- Scoped to the guardianship row, NOT to the (guardian, dependent) pair.
    -- Consequence: when a guardianship ends and a new one begins (a renewed court
    -- order), permissions do not silently carry over. They must be re-granted.
    -- This is deliberate — see the note below.

    permission_code TEXT NOT NULL REFERENCES permission(code),
    -- Codes in the 'dependent.*' namespace. See the catalog below.

    is_granted      BOOLEAN NOT NULL DEFAULT true,
    -- False = explicitly DENIED. This is how "this parent may not see medical
    -- records" is expressed without revoking every other permission. Explicit
    -- denial is checked before any other guardianship permission.

    valid_from      DATE NOT NULL DEFAULT CURRENT_DATE,
    valid_to        DATE,          -- NULL = until the guardianship ends

    granted_by      BIGINT REFERENCES person(id),
    granted_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    grant_reason    TEXT,
    -- e.g. 'default for new guardianship', 'court order 2026-03-14', 'parent request'

    revoked_by      BIGINT REFERENCES person(id),
    revoked_at      TIMESTAMPTZ,
    revoke_reason   TEXT,

    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT ck_guard_permission_period CHECK (
        valid_to IS NULL OR valid_to > valid_from),
    CONSTRAINT ck_guard_permission_revoked CHECK (
        revoked_at IS NULL OR revoked_by IS NOT NULL)
);

-- One live row per (guardianship, permission_code):
CREATE UNIQUE INDEX uq_guard_permission_code
    ON guardianship_permission (guardianship_id, permission_code)
    WHERE valid_to IS NULL;

CREATE INDEX ix_guard_permission_guardianship ON guardianship_permission (guardianship_id)
    WHERE valid_to IS NULL;
CREATE INDEX ix_guard_permission_code ON guardianship_permission (permission_code);
```

### Why scoped to `guardianship_id` and not to the person pair

If it were scoped to `(guardian, dependent)`, then a guardianship ending and a new one
starting — a renewed court order, a lapse and re-establishment — would silently retain all
previously granted permissions. Per your instruction that both read and write access must
be **explicit**, that inheritance is undesirable. Scoping to the guardianship row forces a
deliberate re-grant.

**The trade-off:** more rows and a re-granting step in a rare case. Accepted, because the
failure mode it prevents is access surviving a change in legal relationship.

### `is_granted = false` — explicit denial

Needed for cases like a parent whose access to medical records is restricted by a court
order while their other permissions continue. Without a deny flag the only options are
"grant everything" or "revoke the guardianship", neither of which is correct.

Resolution order inside the guardianship channel:

```
1. any guardianship_permission with is_granted = false for this code → DENY
2. any guardianship_permission with is_granted = true  for this code → ALLOW
3. the 'dependent.admin' permission, if granted                 → ALLOW
4. otherwise                                                     → DENY
```

Step 1 before step 3 matters: `dependent.medical.view = false` must override a granted
`dependent.admin`. A court restriction is not overridable by a broader grant.

### Permission catalog — `dependent.*`

Per your instruction, every resource has an `admin` level that subsumes narrower ones.

| Code | Grants | Notes |
|------|--------|-------|
| `dependent.profile.view` | See name, birth date, membership state | Baseline for any guardian |
| `dependent.profile.admin` | View and edit the profile | |
| `dependent.contact.view` | See the dependent's contact points | |
| `dependent.contact.manage` | Edit the dependent's contact points | Usually granted |
| `dependent.membership.view` | See membership history | |
| `dependent.membership.request` | Submit/renew a membership | |
| `dependent.event.view` | See event registrations | |
| `dependent.event.register` | Register for events | |
| `dependent.fee.view` | See fee and payment records | |
| `dependent.fee.pay` | Pay fees | |
| `dependent.medical.view` | See medical/allergy records | **Sensitive.** Frequently denied for one guardian. |
| `dependent.medical.admin` | Edit medical records | |
| `dependent.consent.give` | Give consents (photo, transport, activity) | Distinct from `medical` |
| `dependent.consent.admin` | Manage consent records | |
| `dependent.achievement.view` | See badges/awards/progress | |
| `dependent.document.view` | See the dependent's documents | |
| `dependent.admin` | **All of the above** | Subsumes everything except an explicit deny |

**`dependent.medical.*` and `dependent.consent.give` are deliberately separate.** A parent
who may consent to their child attending a camp is not necessarily a parent who may read
the child's medical file — and vice versa, a guardian with medical access may not have
decision-making authority. Keeping them apart means the common court-ordered restriction is
expressible.

### Default grants for a new guardianship

An application-level decision, not a schema one, but worth fixing now: when a guardianship
is created, grant a **conservative default set** — `dependent.profile.view`,
`dependent.contact.view`, `dependent.membership.view`, `dependent.event.view`,
`dependent.fee.view`, `dependent.medical.view`, `dependent.consent.give`. That is
read-and-consent, not admin. Everything else requires a deliberate grant.

*Assumption:* a parent registering their own child should have `dependent.admin` by default
— they created the record. The two cases (parent self-registering vs. staff recording a
court-ordered guardianship) should produce different defaults, which is why `source` and
`grant_reason` are recorded. Tracked in [../open-questions.md](../open-questions.md).

---

## 3. `household` and `household_member`

```sql
CREATE TABLE household (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name            TEXT,          -- 'Novák family'; display only
    public_id       UUID NOT NULL DEFAULT gen_random_uuid() UNIQUE,

    billing_contact_person_id BIGINT REFERENCES person(id),
    -- Who receives and pays the household's fees. Nullable — a household may exist
    -- only as an address grouping with no billing meaning.

    postal_address  JSONB,
    -- {street, city, postal_code, country}. Denormalised from the billing contact's
    -- primary postal contact for convenience of the "one invoice per household" view.

    valid_from      DATE NOT NULL DEFAULT CURRENT_DATE,
    valid_to        DATE,

    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by      BIGINT REFERENCES person(id),
    updated_at      TIMESTAMPTZ,
    updated_by      BIGINT REFERENCES person(id),

    CONSTRAINT ck_household_period CHECK (valid_to IS NULL OR valid_to > valid_from)
);

CREATE TABLE household_member (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    household_id    BIGINT NOT NULL REFERENCES household(id),
    person_id       BIGINT NOT NULL REFERENCES person(id),

    role_in_household TEXT CHECK (role_in_household IN
                        ('adult','child','other')),

    valid_from      DATE NOT NULL DEFAULT CURRENT_DATE,
    valid_to        DATE,

    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT ck_household_member_period CHECK (
        valid_to IS NULL OR valid_to > valid_from)
);

ALTER TABLE household_member ADD CONSTRAINT ex_household_member_no_overlap
    EXCLUDE USING gist (
        household_id WITH =,
        person_id    WITH =,
        daterange(valid_from, valid_to, '[)') WITH &&
    );

CREATE INDEX ix_household_member_household ON household_member (household_id);
CREATE INDEX ix_household_member_person    ON household_member (person_id, valid_to);
```

### Household membership grants no access — say it explicitly

> **Being in the same household does not grant any permission over another member of it.**
> A stepparent in the household with no guardianship row has no access to the children's
> records. A grandparent living at the address has no access. This is deliberate and it is
> a safeguarding property, not an oversight.

All access comes from `guardianship` + `guardianship_permission`. The household exists for
exactly two purposes:

1. **Billing.** One invoice for three siblings, rather than three. This is the reason the
   table exists — see [../domain/05-membership-lifecycle.md](../domain/05-membership-lifecycle.md#6-renewal-and-the-yearly-fee),
   where the open question of per-person vs. per-household fees is tracked.
2. **Address grouping.** For the historical question "which children lived at this address
   in 2003?", which is a useful corroborating signal in legacy matching
   ([../domain/03-identity-and-legacy.md](../domain/03-identity-and-legacy.md#4-match-signals)).

If the organization charges per person and never needs address history, this table can be
dropped entirely. It is included because retrofitting household billing later is expensive
and the table costs little.

### Why not a `family` person row

Some systems model a household as a fake person so that memberships and payments can
attach to it. Do not. It creates rows in `person` that are not people, which breaks
identity matching, produces nonsense in name searches, and — because it is a person — can
receive a membership, an account, and eventually permissions.

---

## 4. How the resolver uses these tables

The guardianship channel is step 4 of the resolver
([../domain/06-authorization-model.md](../domain/06-authorization-model.md#5-the-resolver)).
Concretely:

```sql
CREATE OR REPLACE FUNCTION can_act_for_dependent(
    p_actor_person_id   BIGINT,
    p_subject_person_id BIGINT,
    p_permission_code   TEXT,
    p_at                DATE DEFAULT CURRENT_DATE
) RETURNS BOOLEAN
LANGUAGE sql STABLE AS $$
    WITH guard AS (
        SELECT g.id
          FROM guardianship g
         WHERE g.guardian_person_id  = p_actor_person_id
           AND g.dependent_person_id = p_subject_person_id
           AND g.valid_from <= p_at
           AND (g.valid_to IS NULL OR g.valid_to > p_at)
         LIMIT 1
    ),
    perms AS (
        SELECT gp.permission_code, gp.is_granted
          FROM guardianship_permission gp
          JOIN guard ON guard.id = gp.guardianship_id
         WHERE gp.valid_from <= p_at
           AND (gp.valid_to IS NULL OR gp.valid_to > p_at)
           AND gp.revoked_at IS NULL
    )
    SELECT CASE
        -- 1. explicit deny wins
        WHEN EXISTS (SELECT 1 FROM perms WHERE permission_code = p_permission_code
                                            AND NOT is_granted) THEN false
        -- 2. explicit grant
        WHEN EXISTS (SELECT 1 FROM perms WHERE permission_code = p_permission_code
                                            AND is_granted) THEN true
        -- 3. dependent.admin subsumes (but not over a deny, handled above)
        WHEN EXISTS (SELECT 1 FROM perms WHERE permission_code = 'dependent.admin'
                                            AND is_granted) THEN true
        -- 4. default deny
        ELSE false
    END;
$$;
```

Two properties to note:

- **An expired or ended guardianship yields `false` at every step**, because `guard`
  is empty. There is no path by which a former guardian retains access.
- **`p_at` is a parameter**, so the question "could this parent have seen this record on
  the date they did?" is answerable retroactively. Needed for auditing past actions.

**The `dependent.` prefix is what routes a check to this function.** The resolver
dispatches on the permission code's namespace, so no caller decides which channel applies.
That is what prevents an authorization rule from being implemented twice.

---

## 5. Acting on behalf — recording it

Every operation performed for a dependent must record both parties. This is not optional:
without it, the audit trail attributes the parent's actions to the child.

```sql
-- Every access_log row for an act-on-behalf carries all three:
INSERT INTO access_log (
    actor_person_id,      -- the guardian who acted
    subject_person_id,    -- the child whose record was affected
    on_behalf,            -- true
    authorization_channel,-- 'guardianship'
    guardianship_id,      -- which grant authorized it
    result
) VALUES (...);
```

Concretely, when a parent registers their child for an event, the record must answer:

- **Who did it?** The parent (`actor_person_id`).
- **For whom?** The child (`subject_person_id`).
- **By what authority?** A specific `guardianship_permission` row.
- **Is that authority still valid?** Re-checkable from the row's dates.

A row that records only "the child registered" is not merely incomplete — it is **wrong**,
and it is the kind of wrong that matters when someone later asks whether a parent consented
to something.

---

## 6. Integrity checks

```sql
-- 1. Guardianships where the dependent is an adult and the row is still open
--    (should have been reviewed; not necessarily an error)
SELECT g.id, g.dependent_person_id, p.birth_date,
       EXTRACT(YEAR FROM age(CURRENT_DATE, p.birth_date)) AS age
  FROM guardianship g JOIN person p ON p.id = g.dependent_person_id
 WHERE g.valid_to IS NULL AND p.birth_date IS NOT NULL
   AND CURRENT_DATE > p.birth_date + INTERVAL '18 years';

-- 2. Guardian permissions on an ended guardianship that are still open
SELECT gp.id FROM guardianship_permission gp
  JOIN guardianship g ON g.id = gp.guardianship_id
 WHERE gp.valid_to IS NULL AND g.valid_to IS NOT NULL;

-- 3. A dependent with no primary contact at all
SELECT g.dependent_person_id, count(*) FROM guardianship g
 WHERE g.valid_to IS NULL
 GROUP BY g.dependent_person_id
HAVING count(*) FILTER (WHERE g.is_primary_contact) = 0;

-- 4. A child member with NO guardian recorded at all (a safeguarding gap)
SELECT m.id, m.person_id, p.family_name, p.given_name
  FROM membership m
  JOIN membership_type mt ON mt.id = m.membership_type_id
  JOIN person p ON p.id = m.person_id
 WHERE mt.category = 'child' AND m.status = 'active'
   AND NOT EXISTS (SELECT 1 FROM guardianship g
                    WHERE g.dependent_person_id = m.person_id
                      AND g.valid_to IS NULL);

-- 5. Guardianship permissions granting a code outside the dependent.* namespace
SELECT gp.id, gp.permission_code FROM guardianship_permission gp
  JOIN permission p ON p.code = gp.permission_code
 WHERE gp.permission_code NOT LIKE 'dependent.%';

-- 6. A guardianship where the guardian is also the dependent's child
--    (data-entry error; requires the birth dates to detect)
SELECT g.id FROM guardianship g
  JOIN person a ON a.id = g.guardian_person_id
  JOIN person b ON b.id = g.dependent_person_id
 WHERE a.birth_date IS NOT NULL AND b.birth_date IS NOT NULL
   AND a.birth_date >= b.birth_date;

-- 7. Household members with no address and no billing contact (empty households)
SELECT h.id FROM household h
 WHERE h.valid_to IS NULL
   AND h.postal_address IS NULL
   AND h.billing_contact_person_id IS NULL;
```

**Check 4 is the important one.** A child member with no guardian recorded is a
safeguarding gap, not a data-quality nit — the organization has a member it cannot contact
in an emergency and cannot obtain consent from. It should alert, not log. This check is one
of the reasons `guardianship` is a required part of the model rather than an optional
convenience.

Check 2 detects the specific failure that scoping permissions to `guardianship_id` was
meant to prevent — worth keeping as a backstop, since an application bug or a manual SQL
fix could still create it.

---

## 7. Open issues

- The default permission set granted when a guardianship is created, and whether it differs
  by `source` (§2).
- Whether guardianship should auto-expire at majority, or always require review (§1).
  Recommend review.
- Per-person vs. per-household fees — determines whether `household` is load-bearing (§3).
- Whether a guardian may act for a dependent who is also a member in their own right — e.g.
  can a parent register their adult child for an event, if the child consents? Recommend an
  explicit consent-based delegation rather than a guardianship, since the legal basis
  differs.
- Whether the organization needs to record guardianship for deceased members' records.
- Whether `custody_arrangement` free text should be structured. Recommend not — custody
  orders vary too much to model, and a wrong model is worse than honest prose.

All tracked in [../open-questions.md](../open-questions.md).
