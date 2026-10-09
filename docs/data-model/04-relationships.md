# Data Model — Relationships

`guardianship`, `guardianship_permission`.

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
    valid_to        DATE,          -- NULL = current. Set by a person: when an arrangement
                                   -- changes, or by the subject once adult (E-5). NOT by a
                                   -- job — the system takes no position on majority (D-069).

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

- a person ends it — staff, or (once it exists, E-5) the subject themselves;
- a court order changes the arrangement;
- the guardian dies.

**The system does not notice birthdays in this connection.** No job, no review queue, no
computed candidate date ([D-069](../decisions/decision-log.md#d-069--guardianship-ends-when-a-person-ends-it-the-system-takes-no-position-on-majority),
reversing D-024 and closing E-2).

**Why not, including why the gentler version was also refused.** The legal reasoning is
unchanged and still correct: in many jurisdictions a parent's authority over health and school
records does not end at 18, and in some it ends at a different age, so *any* computed date is
a claim the system cannot support. What D-069 adds is that a **review queue makes the same
claim more quietly**. A queue is a worklist asserting *this arrangement is now suspect*, raised
in every case, for every family, including the ones where the adult child actively wants their
parent to keep handling the paperwork. Deferring a decision is not the same as declining to
make one, and the queue was a decision.

**What is lost, precisely:** a *prompt*, not a *record*. `valid_from`/`valid_to` mean "who is
listed as my guardian, and since when?" is a query with a complete answer including the date
each ended. What replaces the prompt is the report in §6 check 1, which is run by a person on
purpose rather than generated by a job on a schedule.

**What this makes load-bearing:** `guardianship.end` is now the only exit, and the subject of
the row holds no permission over it. See
[E-5](../open-questions.md#e-5--how-does-an-adult-end-a-guardianship-over-themselves).

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
**[D-068](../decisions/decision-log.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle)
withdraws this as a *resolver rule*** — the prefix-match wildcard codes are gone, but
`dependent.admin` itself stays, because it is a shorthand a person deliberately stores on one
guardianship row, not a wildcard inferred by code (see §9 of the permission catalog for the
distinction).

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

[Decided (D-046)](../decisions/decision-log.md#d-046--guardianship-defaults-depend-on-how-the-guardianship-was-created):
the default set depends on **how the guardianship arose**, not on a single global rule.

| `guardianship.source` | Default permission set |
|---|---|
| `self` — a parent registering their own child | **`dependent.admin`** — they created the record and are asserting the relationship; there is nobody better placed to hold full authority over it |
| `staff`, `court_order`, `import` — recorded by someone else | **Chosen at creation**, from the conservative set below |

The conservative set, for the second row — read-and-consent, deliberately not admin:
`dependent.profile.view`, `dependent.contact.view`, `dependent.membership.view`,
`dependent.event.view`, `dependent.fee.view`, `dependent.medical.view`,
`dependent.consent.give`. Everything beyond it requires a deliberate grant.

```sql
-- Applied by the application at guardianship insert, not by a trigger — the "chosen at
-- creation" case needs a human in the loop, and a trigger cannot express that.
CREATE OR REPLACE FUNCTION default_guardianship_grants(
    p_guardianship_id BIGINT
) RETURNS INTEGER LANGUAGE plpgsql AS $$
DECLARE
    v_source TEXT;
    v_count  INTEGER := 0;
BEGIN
    SELECT source INTO v_source FROM guardianship WHERE id = p_guardianship_id;

    IF v_source = 'self' THEN
        INSERT INTO guardianship_permission
            (guardianship_id, permission_id, is_granted, granted_by, grant_reason)
        SELECT p_guardianship_id, perm.id, true, NULL,
               'self-registration: parent created the child record'
          FROM permission perm
         WHERE perm.code = 'dependent.admin'
            OR perm.code LIKE 'dependent.admin.%';
        GET DIAGNOSTICS v_count = ROW_COUNT;
    END IF;

    RETURN v_count;   -- 0 for the manual paths: the caller chooses the set explicitly.
END $$;
```

**Why `source` and `grant_reason` are both recorded.** The same word — "guardian" — now means
two different default scopes depending on paperwork, and the record has to say which was
chosen and why. A guardian with read-only access and a guardian with full access are
indistinguishable in the domain language and must not be in the data.

---

## 3. There is no `household` table

**Removed** ([D-057](../decisions/decision-log.md#d-057--household-is-removed)). An address
is a `person_contact` row of type `postal`
([01-identity.md §6](01-identity.md#6-person_contact)), which already exists, already keeps
history (`valid_from` / `valid_to`), and already carries a `purpose` — `'billing'` for the
address an invoice goes to. A separate household table was duplicating it under a different
key, and the duplication had gone stale: its `postal_address` column was documented as
denormalised *from* the billing contact's postal contact, with nothing keeping the copy true.

### Shared address still grants no access

> **Living at the same address does not grant any permission over another person at that
> address.** A stepparent with no `guardianship` row has no access to the children's records.
> A grandparent at the address has no access. This is deliberate and it is a safeguarding
> property, not an oversight.

This was true when `household` existed ([D-019](../decisions/decision-log.md#d-019--household-membership-grants-no-access))
and it is true now, for a simple reason worth stating so nobody re-derives it: **the access
never came from the household tables.** All `dependent.*` authority comes from
`guardianship` + `guardianship_permission` (§1–2). Removing a table that granted nothing
cannot grant anything.

### What replaced it

| Household feature | Now |
|---|---|
| Billing address | `person_contact` where `contact_type = 'postal' AND purpose = 'billing'` |
| "Which children lived at this address in 2003?" | A query over the temporal `person_contact` history ([domain/03 §4](../domain/03-identity-and-legacy.md#4-match-signals)) |
| One invoice for three siblings | The fee is flat and per person ([D-037](../decisions/decision-log.md#d-037--exactly-one-membership-type-the-fee-is-flat-and-per-person)); there is no family price to invoice |
| `fee_obligation.household_id` | Column, CHECK arm and index all removed ([07-finance.md §2](07-finance.md#2-minimal-provisional-shape)) |

**What was genuinely lost, recorded rather than glossed:** a household was a *group* with a
name and its own lifetime. Two people at one address are now related by a query, not by a row,
so there is nowhere to hang "the Novák family" as a first-class thing and no `valid_from` for
the grouping itself. Accepted, because nothing was using it — no code set
`fee_obligation.household_id`, and `household.name` had no consumer. If family-level
communication or a family discount is ever wanted, this is the decision to revisit, and the
shape to bring back is a group with a period, not a fake person.

### Why not a `family` person row

Some systems model a household as a fake person so that memberships and payments can
attach to it. Do not. It creates rows in `person` that are not people, which breaks
identity matching, produces nonsense in name searches, and — because it is a person — can
receive a membership, an account, and eventually permissions.

---

## 4. How the resolver uses these tables

The guardianship channel is step 4 of the resolver
([../domain/06-authorization-model.md](../domain/06-authorization-model.md#6-the-resolver)).
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
-- 1. Guardianships where the dependent is an adult and the row is still open.
--    NOT an error, and under D-069 it is *expected* in the ordinary case — a parent keeping
--    authority over an adult child's records is legal and common. This is not a violation
--    report; it is the periodic human review D-069 names as the entire control, and it
--    exists precisely BECAUSE no job acts on this date. Run it deliberately, not nightly.
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

-- 4. A MINOR participant or member with NO guardian recorded at all (a safeguarding gap).
--    Age comes from person.birth_date — there is no membership category to read it from,
--    because membership is ageless (D-038).
SELECT m.id, m.person_id, p.family_name, p.given_name
  FROM membership m
  JOIN person p ON p.id = m.person_id
 WHERE m.status = 'active'
   AND is_minor(m.person_id)
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

-- 7. REMOVED — "households with no address and no billing contact".
--    There is no household table (D-057), so there is nothing to check.
--    The nearest surviving signal is a live billing purpose with no postal
--    address behind it, which is a finance problem, not a relationship one:
--
--    SELECT pc.person_id FROM person_contact pc
--     WHERE pc.purpose = 'billing' AND pc.valid_to IS NULL
--       AND NOT EXISTS (SELECT 1 FROM person_contact a
--                        WHERE a.person_id = pc.person_id
--                          AND a.contact_type = 'postal'
--                          AND a.valid_to IS NULL);
```

**Check 4 is the important one.** A minor with no guardian recorded is a
safeguarding gap, not a data-quality nit — the organization has a member it cannot contact
in an emergency and cannot obtain consent from. It should alert, not log. This check is one
of the reasons `guardianship` is a required part of the model rather than an optional
convenience.

Note what changed when membership became ageless. The check used to read
`membership_type.category = 'child'`; with one membership type
([D-037](../decisions/decision-log.md#d-037--exactly-one-membership-type-the-fee-is-flat-and-per-person))
that column does not exist, and the question is now answered from `person.birth_date` via
`is_minor()`. The signal is arguably better than it was: "this person is under 18 today"
rather than "this person's membership row was categorised as a child when it was opened",
which could be years out of date.

Check 2 detects the specific failure that scoping permissions to `guardianship_id` was
meant to prevent — worth keeping as a backstop, since an application bug or a manual SQL
fix could still create it.

---

## 7. Open issues

- ~~Whether guardianship should auto-expire at majority, or always require review.~~
  **Neither** — the system takes no position on majority, and the review queue this file
  recommended was withdrawn with it (§1, [D-069](../decisions/decision-log.md#d-069--guardianship-ends-when-a-person-ends-it-the-system-takes-no-position-on-majority)).
- **New, and sharper because of that:** how does an adult end a guardianship over themselves?
  They are the subject and hold no permission over the row. See
  [E-5](../open-questions.md#e-5--how-does-an-adult-end-a-guardianship-over-themselves).
- **Resolved: `household` is removed entirely** — answered "drop household entirely", now
  [D-057](../decisions/decision-log.md#d-057--household-is-removed) (§3). Addresses live on
  `person_contact`.
- Whether a guardian may act for a dependent who is also a member in their own right — e.g.
  can a parent register their adult child for an event, if the child consents? Recommend an
  explicit consent-based delegation rather than a guardianship, since the legal basis
  differs. The *group* version of this is now answered by audiences
  ([D-042](../decisions/decision-log.md#d-042--grants-may-target-audiences-not-only-individuals)).
- Whether `custody_arrangement` free text should be structured. Recommend not — custody
  orders vary too much to model, and a wrong model is worse than honest prose.
- **Confirm that the membership gate's guardianship carve-out is intended** (§6). A lapsed
  parent keeps full `dependent.*` access ([D-039](../decisions/decision-log.md#d-039--member-permissions-require-a-current-paid-membership)),
  which means an unpaid parent and a paid one are indistinguishable inside that namespace.
  It is almost certainly right — guardianship comes from a legal relationship, not a
  membership — but it should be a stated choice, not a side effect of where the gate was
  placed.

**Resolved and no longer open**, kept visible so the reasoning survives: the default grant
set at guardianship creation (now depends on `source` — D-046); whether fees are per person
or per household (per person, flat — D-037, which retired the load-bearing half of `household`
and led to its removal — D-057); and background checks (none are recorded — D-043).

All tracked in [../open-questions.md](../open-questions.md).
