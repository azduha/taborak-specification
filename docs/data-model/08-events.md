# Data Model — Events

`event`, `event_organizer`, `event_registration`, `event_question`, `event_answer`.

Domain rationale: [../domain/07-events.md](../domain/07-events.md).

**Nothing here is provisional.** This module was designed against the authorization model
rather than beside it, and every hook it uses — `access_grant.scope_type = 'event'`,
`grant_scope_type`, audiences, `permission_level` — was already in place and seeded. The
tables below fill those hooks; they do not extend the model.

---

## 1. Why these five tables, and no `event_series`

| Table | What it is |
|---|---|
| `event` | The occasion. One owning unit, a date, a registration window, an optional capacity |
| `event_organizer` | Who is running it — an appointment on the event, not a grant (§5) |
| `event_registration` | One person's answer: attending, or not attending. *Unanswered is the absence of a row* |
| `event_question` | What this event asks registrants |
| `event_answer` | What one person said to one question |

**No recurrence.** A weekly meeting is `unit_participation`, not an event
([../domain/07-events.md §1](../domain/07-events.md#1-what-an-event-is-and-what-it-is-not)).
Adding `event_series` would mean every downstream table — registrations, capacity, presence,
organizers, questions — needs a second possible home, and the feature that needed recurrence
is already modelled.

**No `event_status` column.** Visibility is the permission model; cancellation is a fact
([../domain/07-events.md §10](../domain/07-events.md#10-cancellation-and-why-there-is-no-status-column)).

---

## 2. `event`

```sql
CREATE TABLE event (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    public_id       UUID NOT NULL DEFAULT gen_random_uuid() UNIQUE,

    org_unit_id     BIGINT NOT NULL REFERENCES org_unit(id),
    -- EXACTLY ONE owning unit, and it is NOT NULL. A joint camp is one unit's event
    -- that another unit's children register for, via an audience grant. See
    -- ../domain/07-events.md §2 — this is forced by D-049, not merely preferred:
    -- two owners would create an exception to "the root may not read a sub-unit's
    -- events" shaped exactly like a joint camp, with no principled place to stop.

    title           TEXT NOT NULL,
    description     TEXT,
    public_note     TEXT,
    -- Shown to registrants. Separate from description, which is internal:
    -- "bring a sleeping bag and a torch" vs. the committee's own notes.

    location        TEXT,          -- free text: a camp site, an address, "the usual place"
    location_detail JSONB,         -- {lat, lon, meeting_point, …} when known

    starts_at       TIMESTAMPTZ NOT NULL,
    ends_at         TIMESTAMPTZ NOT NULL,
    -- Instants, not dates. A Thursday group meets at 5pm; a camp starts on Saturday
    -- morning. TIMESTAMPTZ because an event has a moment, and the timezone is the
    -- organization's, recorded rather than assumed.

    all_day         BOOLEAN NOT NULL DEFAULT false,
    -- Display only. An all-day camp still has instants underneath.

    registration_opens_at  TIMESTAMPTZ,
    -- NULL = open as soon as the event is visible. The event is visible to whoever
    -- holds event.view, which for a fresh event is its organizers and nobody else
    -- (../domain/07-events.md §10), so NULL is a reasonable default and wrong for a
    -- jamboree whose sign-up should not open before the dates are fixed.

    registration_closes_at TIMESTAMPTZ,
    -- NULL = when the event starts. This is the "unlimited" case: registration stays
    -- open until the thing happens.

    capacity        INTEGER,
    -- NULL = unlimited. Bed count, bus seats, fire-safety limit. Enforced as a
    -- WAITLIST threshold, not a block, and organizers may exceed it
    -- (../domain/07-events.md §8).

    waitlist_deadline TIMESTAMPTZ,
    -- When an unpaid registration at a full event releases its place to the waitlist
    -- (§6). NULL = never releases. Only meaningful when the event has a fee AND a
    -- capacity; ignored otherwise. This is the ONE automatic transition in this
    -- module — see §6 for why it is accepted and what it costs.

    fee_schedule_id BIGINT REFERENCES fee_schedule(id),
    -- NULL = this event is free, which most are. Set = a fee applies; registering
    -- creates a fee_obligation (§6). The amount and currency live in fee_schedule,
    -- not here — events do not price themselves.

    cancelled_at    TIMESTAMPTZ,
    cancelled_by    BIGINT REFERENCES person(id),
    cancel_reason   TEXT,
    -- Cancellation is a FACT, not a status, and this is the point where the "no
    -- status column" reasoning deliberately diverges: revoking grants would hide the
    -- cancellation from the registrants, who are exactly the people who must be told.
    -- A cancelled event stops accepting registrations and KEEPS every registration
    -- row — those rows are the record that the camp was planned and who was coming.

    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by      BIGINT REFERENCES person(id),
    updated_at      TIMESTAMPTZ,
    updated_by      BIGINT REFERENCES person(id),
    import_batch_id BIGINT,

    CONSTRAINT ck_event_period CHECK (ends_at > starts_at),
    CONSTRAINT ck_event_capacity CHECK (capacity IS NULL OR capacity > 0),
    CONSTRAINT ck_event_registration_window CHECK (
        registration_opens_at IS NULL OR registration_closes_at IS NULL
        OR registration_closes_at > registration_opens_at),
    CONSTRAINT ck_event_cancel CHECK (
        (cancelled_at IS NULL) = (cancelled_by IS NULL)),
    -- A cancellation has a who and a when, or neither. The reason is free text and
    -- may be absent ("cancelled — see email").
    CONSTRAINT ck_event_waitlist_deadline CHECK (
        waitlist_deadline IS NULL
        OR (capacity IS NOT NULL AND fee_schedule_id IS NOT NULL))
    -- A waitlist deadline is meaningless without a capacity to fill or a fee to pay.
    -- Stating it prevents a column that silently does nothing.
);

CREATE INDEX ix_event_unit      ON event (org_unit_id, starts_at DESC);
CREATE INDEX ix_event_upcoming  ON event (starts_at)
    WHERE cancelled_at IS NULL;
CREATE INDEX ix_event_reg_open  ON event (registration_closes_at)
    WHERE cancelled_at IS NULL;
```

### No `status` column, and why that is not an omission

```sql
-- "Is this event over?"
ends_at < now()

-- "Is it cancelled?"
cancelled_at IS NOT NULL

-- "Needs attention now" — the query an admin screen runs
SELECT * FROM event
 WHERE cancelled_at IS NULL AND ends_at >= now()
 ORDER BY starts_at;
```

`completed` is derived, never stored, so there is no state to keep consistent and no job to
move rows between states. **Draft** is not a state either: a new event has no grants beyond
its organizers, so nobody else can see it, and publishing is an `access_grant`, not an
`UPDATE`. A status column and a permission system that both claim to answer "who may see
this?" will eventually disagree, and the one that gets enforced is whoever wrote the last
`IF`.

### Why `fee_schedule_id` and not an `event_fee` table

The fee amount, currency and validity already live in `fee_schedule`
([07-finance.md §2](07-finance.md#2-minimal-provisional-shape)), which is temporal — so a
1998 camp's fee recomputes correctly from the 1998 schedule. An `event_fee` table would
duplicate that and immediately drift. An event points at the schedule that prices it.

---

## 3. `event_organizer`

**The absence of a `valid_to` is deliberate.** This is a *roster*, not a period: you are on
the list, or you are not. An organizer who drops out is removed (recorded in `audit_log`),
because "was Jan an organizer of that camp?" must have one answer, not a set of intervals.

```sql
CREATE TABLE event_organizer (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    event_id        BIGINT NOT NULL REFERENCES event(id) ON DELETE CASCADE,
    person_id       BIGINT NOT NULL REFERENCES person(id),

    organizer_role  TEXT,
    -- 'lead', 'assistant', 'cook', 'driver', 'medic', 'quartermaster' — free text.
    -- NOT a controlled vocabulary: every organization labels these differently, and
    -- a CHECK here would be a guess of the kind D-054 removed for unit types.

    is_primary      BOOLEAN NOT NULL DEFAULT false,
    -- The person the parents are told to call. At most one per event (§10 check 3).

    sort_order      INTEGER NOT NULL DEFAULT 0,
    -- Display order for the list. Cooks before drivers is a real preference and not
    -- something to derive.

    note            TEXT,

    added_by        BIGINT REFERENCES person(id),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT uq_event_organizer UNIQUE (event_id, person_id)
);
```

> **`ON DELETE CASCADE` here, and nowhere else in this schema.** It is justified because
> `event_organizer` is a roster of *assignments on the event*, not a business record: a
> deleted event has no organizers in the domain sense either. **In practice nothing deletes
> an event** — the deletion policy is temporal closure, and cancellation sets `cancelled_at`.
> The cascade exists so that a mistaken `INSERT` into a draft event can be cleaned up
> without leaving orphan rows, and it is the only cascade in the design. Deleting an event
> that has registrations is refused by trigger (§8).

CREATE INDEX ix_event_organizer_person ON event_organizer (person_id);
CREATE INDEX ix_event_organizer_event  ON event_organizer (event_id, sort_order);
CREATE UNIQUE INDEX uq_event_organizer_primary ON event_organizer (event_id)
    WHERE is_primary;

### Organizers are appointments, not grants

`event_organizer` is the **domain** answer to "who is running this camp?" — the labelled,
ordered list that parents see. It is deliberately **not** an `access_grant`
([../domain/07-events.md §5](../domain/07-events.md#5-organizers-are-appointed-not-granted)):

- A grant has no room for `organizer_role = 'cook'`.
- "Who is running this camp?" should not be answered by reading the permission table.
- Revoking a grant to remove a cook would also revoke their ability to see the event at
  all, which is not what "they are no longer cooking" means.

**Authority to act on the event does not come from this table.** It comes from the owning
unit's roles (via §7's rule), from an explicit `access_grant`, or from `system.admin`.

---

## 4. `event_registration`

One row per person per event. **Two stored values; "unanswered" is the absence of a row.**

```sql
CREATE TABLE event_registration (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    event_id        BIGINT NOT NULL REFERENCES event(id),
    person_id       BIGINT NOT NULL REFERENCES person(id),
    -- person_id, NOT membership_id — same reasoning as unit_participation
    -- (D-041, ../data-model/03-membership.md §5). An event's roster must survive
    -- independently of how membership is recorded, and imported historical
    -- attendance has no membership row to point at. A 1998 camp roster is
    -- participation, and an inferred open-ended membership would make every one of
    -- those children a "current member" today through the gate (D-039, D-056).

    response        TEXT NOT NULL CHECK (response IN ('attending','not_attending')),
    -- TWO values. 'unanswered' is written NOWHERE. It is the absence of a row, so
    -- "who has not replied yet?" is a subtraction, not a stored state
    -- (../domain/07-events.md §3). Returning someone to unanswered deletes the row,
    -- which audit_log records — the honest act, and the one that leaves least behind.

    responded_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    -- When the ANSWER was given, which may differ from when it was recorded. A phone
    -- call on Tuesday entered on Thursday has two dates and both matter.

    source          TEXT NOT NULL DEFAULT 'self' CHECK (source IN
                        ('self','staff','guardian','import')),
    -- How this person got here, and the audit answer to "how did they get in?".
    -- 'staff' bypasses the contribute requirement deliberately
    -- (../domain/07-events.md §6): organizers may register anyone.
    -- 'guardian' is acting-under-guardianship; the acting person is in access_log.

    registered_by   BIGINT REFERENCES person(id),
    -- NULL when source = 'self'. Set otherwise: which organizer, or which guardian.

    is_waitlisted   BOOLEAN NOT NULL DEFAULT false,
    waitlist_position INTEGER,
    -- Order within the waitlist. Assigned on insert when the event is at capacity,
    -- and rewritten on promotion. See §5.

    is_confirmed    BOOLEAN NOT NULL DEFAULT false,
    confirmed_at    TIMESTAMPTZ,
    -- Registration is not the same as a held place. An event with NO fee confirms
    -- immediately on registration; an event WITH a fee confirms on payment (§6).
    -- This is the "payment confirms the place" rule, and it is the only place in
    -- this module where money changes a registration's meaning.

    was_present     BOOLEAN,
    -- NULL = not yet marked. true = turned up. false = marked absent.
    -- THREE-VALUED ON PURPOSE: "we did not take a register" and "we took one and
    -- they were not there" are different facts, and only one is a safeguarding
    -- signal. For a camp this is the record of who was actually in the
    -- organization's care, and it cannot be reconstructed afterwards (§9).

    presence_marked_by BIGINT REFERENCES person(id),
    -- The person who took the register. Held by whoever has event.presence.mark, which is
    -- deliberately ONE LEVEL BELOW event.manage_participants (contribute, not manage) so the
    -- volunteer at the door is not also the person who can delete a child from the roster.
    presence_marked_at TIMESTAMPTZ,

    fee_obligation_id BIGINT REFERENCES fee_obligation(id),
    -- Set when the event has a fee_schedule and this registration created an
    -- obligation. The reverse pointer from fee_obligation.event_registration_id
    -- also exists (§6) — both directions, because each is asked a different
    -- question: "what does this person owe for this camp?" and "what is this
    -- obligation for?".

    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ,
    updated_by      BIGINT REFERENCES person(id),
    import_batch_id BIGINT,

    CONSTRAINT ck_event_registration_response CHECK (
        response <> 'not_attending' OR (is_waitlisted = false AND is_confirmed = false)),
    -- A decline is not waitlisted and not confirmed. Otherwise a "no" could hold a
    -- place on the waitlist, which is nonsense.

    CONSTRAINT ck_event_registration_presence CHECK (
        (was_present IS NULL) = (presence_marked_at IS NULL)
        AND (was_present IS NULL) = (presence_marked_by IS NULL)),
    -- Presence is marked all together: the fact, who marked it, and when. A
    -- partially-set trio is a bug, not a state.

    CONSTRAINT ck_event_registration_confirmed CHECK (
        (is_confirmed) = (confirmed_at IS NOT NULL)),

    CONSTRAINT ck_event_registration_waitlist CHECK (
        (is_waitlisted) = (waitlist_position IS NOT NULL)),

    CONSTRAINT uq_event_registration UNIQUE (event_id, person_id)
    -- One row per person per event, full stop. This is what makes "unanswered =
    -- absence" work: there is exactly one place an answer could live.
);

CREATE INDEX ix_event_registration_person ON event_registration (person_id);
CREATE INDEX ix_event_registration_event  ON event_registration (event_id, response);
CREATE INDEX ix_event_registration_attending ON event_registration (event_id)
    WHERE response = 'attending' AND is_waitlisted = false;
CREATE INDEX ix_event_registration_waitlist ON event_registration (event_id, waitlist_position)
    WHERE is_waitlisted;
CREATE INDEX ix_event_registration_presence ON event_registration (event_id, was_present)
    WHERE was_present IS NOT NULL;
```

### Why `person_id`, not `membership_id`

Same argument as `unit_participation` ([03-membership.md §5](03-membership.md#5-unit_participation)),
and it is stronger here. An imported 1998 camp roster names children who have no membership
row to point at. With the corpus being large and number-bearing
([D-056](../decisions/decision-log.md#d-056--the-legacy-import-expects-a-large-corpus-with-legacy-member-numbers)),
linking to `membership` would make those rows unrepresentable — and, worse, an inferred
open-ended membership created to satisfy the FK would make every one of those children a
*current* member today through the gate.

**The trade-off, stated:** the schema cannot enforce "only members may register". It does not
need to — eligibility is capability ([../domain/07-events.md §4](../domain/07-events.md#4-who-may-register-capability-not-a-separate-rule-engine)),
and capability is a grant, not a membership row.

---

## 5. Capacity and the waitlist

**Capacity is a threshold, not a block.** Registering for a full event succeeds and produces
a waitlisted row.

```sql
-- Is this event at capacity? Attending, non-waitlisted registrations only.
CREATE OR REPLACE FUNCTION event_is_full(p_event_id BIGINT)
RETURNS BOOLEAN LANGUAGE sql STABLE AS $$
    SELECT COALESCE(
        (SELECT count(*) >= e.capacity
           FROM event e
          WHERE e.id = p_event_id AND e.capacity IS NOT NULL),
        false);
$$;

-- The placing rule, as a trigger so that EVERY insert path obeys it — self-service,
-- staff, guardian and import alike. Application-level placement would let one of the
-- four paths forget, and the forgotten one would be the one that matters.
CREATE OR REPLACE FUNCTION place_event_registration()
RETURNS TRIGGER LANGUAGE plpgsql STABLE AS $$
DECLARE
    v_event event%ROWTYPE;
BEGIN
    SELECT * INTO v_event FROM event WHERE id = NEW.event_id;

    -- A decline never occupies a place.
    IF NEW.response <> 'attending' THEN
        NEW.is_waitlisted     := false;
        NEW.waitlist_position := NULL;
        NEW.is_confirmed      := false;
        NEW.confirmed_at      := NULL;
        RETURN NEW;
    END IF;

    -- Waitlisting is a SELF-SERVICE outcome. A staff registration is admitted even
    -- past capacity: the organizer who knows there are two spare tents is not to be
    -- blocked by a number they cannot edit mid-camp (../domain/07-events.md §8).
    -- The overrun is permitted, attributed, and REPORTED (§10, check 5).
    IF NEW.source = 'self'
       AND v_event.capacity IS NOT NULL
       AND (SELECT count(*) FROM event_registration r
             WHERE r.event_id = NEW.event_id
               AND r.response = 'attending'
               AND NOT r.is_waitlisted) >= v_event.capacity
    THEN
        NEW.is_waitlisted := true;
        NEW.waitlist_position := COALESCE(
            (SELECT max(r.waitlist_position) + 1
               FROM event_registration r
              WHERE r.event_id = NEW.event_id AND r.is_waitlisted), 1);
    ELSE
        NEW.is_waitlisted     := false;
        NEW.waitlist_position := NULL;
    END IF;

    -- Confirmation: immediate when there is no fee to wait for.
    IF v_event.fee_schedule_id IS NULL THEN
        NEW.is_confirmed := true;
        NEW.confirmed_at := now();
    ELSE
        NEW.is_confirmed := false;
        NEW.confirmed_at := NULL;   -- §6 — payment confirms the place
    END IF;

    RETURN NEW;
END $$;

CREATE TRIGGER trg_place_event_registration
    BEFORE INSERT ON event_registration
    FOR EACH ROW EXECUTE FUNCTION place_event_registration();
```

> **The `source = 'self'` disjunct is the whole of "organizers may register anyone", made
> mechanical.** Removing it silently reverses the answer: every staff registration would be
> waitlisted behind self-service ones, and the leader adding a child on the day would be
> told the camp is full when they can see two spare beds.

### Promotion, which is a deliberate act

Promotion is **not automatic** — no trigger, no job. An organizer picks someone from the
waitlist:

```sql
-- Promote one person. Bypasses the capacity test, by design: the whole point of
-- promoting is that a place has freed up, and re-testing would just fail again.
UPDATE event_registration SET
    is_waitlisted     = false,
    waitlist_position = NULL,
    is_confirmed      = (SELECT fee_schedule_id IS NULL FROM event WHERE id = event_id),
    confirmed_at      = CASE WHEN (SELECT fee_schedule_id FROM event WHERE id = event_id)
                                  IS NULL THEN now() END
 WHERE event_id = :event AND person_id = :person;
```

Promotion writes the same two flags the trigger would have, so a promoted registration and
an admitted one are indistinguishable afterwards — which is correct, because the difference
between them is *when*, not *what*.

### When an unpaid registration releases its place

If `waitlist_deadline` is set, an unpaid registration at a full event releases its place to
the waitlist at that moment. This is **the one automatic transition in this module**, and it
is recorded as such:

```sql
-- The release. Scoped as narrowly as the rule can be: only at a full event, only
-- with a fee configured, only past the deadline, only unpaid, and never a staff
-- registration (which is admitted by hand and by a human who can see the roster).
UPDATE event_registration r SET
    is_waitlisted     = true,
    waitlist_position = COALESCE(
        (SELECT max(x.waitlist_position) + 1 FROM event_registration x
          WHERE x.event_id = r.event_id AND x.is_waitlisted), 1),
    is_confirmed      = false,
    confirmed_at      = NULL
 WHERE r.response = 'attending'
   AND NOT r.is_waitlisted
   AND r.source = 'self'
   AND r.is_confirmed = false
   AND EXISTS (SELECT 1 FROM event e
                WHERE e.id = r.event_id
                  AND e.fee_schedule_id IS NOT NULL
                  AND e.waitlist_deadline IS NOT NULL
                  AND e.waitlist_deadline < now()
                  AND e.cancelled_at IS NULL);
```

> **Why this is accepted despite the design's habit of avoiding automatic transitions.** The
> design has spent real effort keeping state changes deliberate
> ([D-023](../decisions/decision-log.md#d-023--nothing-is-auto-lapsed-or-auto-terminated),
> [D-040](../decisions/decision-log.md#d-040--the-fee-expires-yearly-a-date-tracked-renewal-window-replaces-a-grace-status)),
> and "payment confirms the place" reintroduces one. It is a *deadline*, not a sweep: it
> applies to a narrow conjunction, it is opt-in per event (`waitlist_deadline` is `NULL` by
> default, so most events never run it), and the state it produces is visible — the person
> is on the waitlist, not silently deleted. The alternative, no deadline at all, means a
> place is held forever by someone who never paid, which is worse.

---

## 6. Payments and confirmation

**Registering creates a fee obligation; payment confirms the place.**

```sql
-- Create the obligation alongside the registration, when the event has a fee.
-- Runs AFTER INSERT so the registration id exists.
CREATE OR REPLACE FUNCTION create_event_fee_obligation()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
DECLARE
    v_event     event%ROWTYPE;
    v_schedule  fee_schedule%ROWTYPE;
    v_obligation_id BIGINT;
BEGIN
    SELECT * INTO v_event FROM event WHERE id = NEW.event_id;
    IF v_event.fee_schedule_id IS NULL OR NEW.response <> 'attending' THEN
        RETURN NEW;
    END IF;

    SELECT * INTO v_schedule FROM fee_schedule WHERE id = v_event.fee_schedule_id;

    INSERT INTO fee_obligation (
        person_id, event_registration_id, fee_schedule_id,
        description, period_from, period_to, amount_due, currency, due_date
    ) VALUES (
        NEW.person_id, NEW.id, v_event.fee_schedule_id,
        v_event.title, v_event.starts_at::date, v_event.ends_at::date,
        v_schedule.amount, v_schedule.currency,
        COALESCE(v_event.waitlist_deadline, v_event.starts_at)::date
    ) RETURNING id INTO v_obligation_id;

    UPDATE event_registration SET fee_obligation_id = v_obligation_id
     WHERE id = NEW.id;

    RETURN NEW;
END $$;

CREATE TRIGGER trg_event_fee_obligation
    AFTER INSERT ON event_registration
    FOR EACH ROW EXECUTE FUNCTION create_event_fee_obligation();
```

**The pointer that had to be restored.** [D-057](../decisions/decision-log.md#d-057--household-is-removed)
removed the household arm from `fee_obligation.ck_obligation_target`, leaving `= 1`
(membership XOR request). An event fee needs an arm back — and this time it is a *real* arm
with data behind it, not the dormant hedge the household column was:

```sql
-- In fee_obligation (§2 of 07-finance.md):
    event_registration_id BIGINT REFERENCES event_registration(id),

    CONSTRAINT ck_obligation_target CHECK (
        (membership_id IS NOT NULL)::int
      + (membership_request_id IS NOT NULL)::int
      + (event_registration_id IS NOT NULL)::int = 1),
    -- Still "= 1", not "<= 3". Every obligation is for exactly one thing: a
    -- membership period, a membership request, or one person's place at one event.
    -- The per-person choice is deliberate — the fee is flat and per person (D-037),
    -- and a family price would need the household grouping designed again first.

CREATE INDEX ix_obligation_event_registration ON fee_obligation (event_registration_id)
    WHERE event_registration_id IS NOT NULL;
```

### Confirming on payment

```sql
-- Called by the payment flow. NOT a trigger on fee_obligation.status — the payment
-- module owns that transition, and a trigger here would make every fee, membership
-- or event alike, confirm an event place.
CREATE OR REPLACE FUNCTION confirm_event_place(p_obligation_id BIGINT)
RETURNS VOID LANGUAGE plpgsql AS $$
BEGIN
    UPDATE event_registration r SET
        is_confirmed = true,
        confirmed_at = now()
      FROM fee_obligation o
     WHERE o.id = p_obligation_id
       AND o.event_registration_id = r.id
       AND r.response = 'attending'
       AND r.is_waitlisted = false;   -- a waitlisted person stays waiting until promoted
END $$;
```

> **`confirm_event_place` is deliberately a function the finance module calls, not a trigger
> on `fee_obligation`.** A trigger would fire for membership fees and event fees alike, and
> "the fee is paid" means something different in each case: a membership activates
> ([D-040](../decisions/decision-log.md#d-040--the-fee-expires-yearly-a-date-tracked-renewal-window-replaces-a-grace-status)),
> an event place confirms. Two transitions, two owners.

**Free events confirm immediately** — see the trigger in §5. An event with no
`fee_schedule_id` has nothing to wait for, and requiring "confirmation" for a free hike
would be a state with no meaning.

---

## 7. `event_question` and `event_answer`

```sql
CREATE TABLE event_question (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    event_id        BIGINT NOT NULL REFERENCES event(id),

    label           TEXT NOT NULL,      -- 'Tent preference', 'Dietary requirements'
    help_text       TEXT,
    position        INTEGER NOT NULL DEFAULT 0,

    data_type       TEXT NOT NULL CHECK (data_type IN
                        ('text','long_text','integer','decimal','bool','date',
                         'choice','multichoice')),
    choices         TEXT[],
    -- For 'choice' / 'multichoice' only. An array on the question rather than a
    -- child table: the options are a property of the question, they are ordered,
    -- and they are never referenced by anything else.

    is_required     BOOLEAN NOT NULL DEFAULT false,
    -- The person REGISTERING must answer. Not a gate on registration itself: a form
    -- that blocks sign-up is a form nobody completes, and the organizer would rather
    -- have the registration and chase the answer.

    applies_to      TEXT NOT NULL DEFAULT 'attendee' CHECK (applies_to IN
                        ('attendee','organizer','all')),
    -- Who is asked. Organizers may be asked things attendees are not (T-shirt size
    -- for the leaders' shirts) and vice versa.

    valid_from      DATE NOT NULL DEFAULT CURRENT_DATE,
    valid_to        DATE,
    -- A question can be retired after people have answered it. Answers survive
    -- (event_answer has no cascade from here), because "what did they say?" must
    -- outlive "do we still ask this?".

    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by      BIGINT REFERENCES person(id),

    CONSTRAINT ck_event_question_choices CHECK (
        (data_type IN ('choice','multichoice')) = (choices IS NOT NULL)),
    -- Choice types have options; nothing else does. Stated as an equivalence so a
    -- 'text' question cannot carry a stray choices array that the UI might honour.

    CONSTRAINT ck_event_question_period CHECK (
        valid_to IS NULL OR valid_to > valid_from)
);

CREATE INDEX ix_event_question_event ON event_question (event_id, position);

CREATE TABLE event_answer (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    question_id     BIGINT NOT NULL REFERENCES event_question(id),
    person_id       BIGINT NOT NULL REFERENCES person(id),
    -- Who ANSWERED — for a child, the child. The person who submitted on their
    -- behalf is in access_log and in registered_by, not here. Answers are about
    -- the person the question concerns.

    value           JSONB NOT NULL,
    -- Typed by question.data_type. JSONB rather than a column per type: the
    -- alternative is eight nullable columns that only one of which is ever set,
    -- which is the shape 01-identity.md §6 rejected for person_contact.

    answered_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    answered_by     BIGINT REFERENCES person(id),

    CONSTRAINT uq_event_answer UNIQUE (question_id, person_id)
);

CREATE INDEX ix_event_answer_person   ON event_answer (person_id);
CREATE INDEX ix_event_answer_question ON event_answer (question_id);
```

### Answers as rows, not JSONB on the registration

This is the choice that makes the feature worth having. The whole reason to collect
"dietary requirements" is to be able to answer **"who needs a gluten-free meal, and how
many?"** — and that is a query:

```sql
SELECT a.value, count(*)
  FROM event_answer a
  JOIN event_question q ON q.id = a.question_id
 WHERE q.event_id = :camp AND q.label = 'Dietary requirements'
 GROUP BY a.value
 ORDER BY count(*) DESC;
```

With answers stored as a JSONB blob on the registration, that becomes JSON traversal, an
index that does not help, and a report nobody writes. The cost is one row per answer — which
is exactly the number of things the organization must act on.

### Reusable question libraries were considered and rejected

A shared pool of question definitions — `question_code`, assigned to events — is
structurally the requirement machinery removed in
[D-044](../decisions/decision-log.md#d-044--nothing-gates-a-membership-request-except-identity-and-payment).
It earns its keep only when the same question must mean the same thing across events, and
tent preference does not: what one camp asks and what another needs are allowed to differ.
Per-event definitions keep them from having to agree, and avoid reviving a removed pattern
for a benefit nobody asked for.

### Health data, and the discipline this requires

> **An event form is the route by which the people running the event learn what they need to
> know — and, given the `dependent.*` namespace is unreachable by unit leaders, it is the
> only one for a child's allergy** ([D-061](../decisions/decision-log.md#d-061--event-answers-are-read-by-that-events-organizers),
> [../domain/07-events.md §12](../domain/07-events.md#12-the-forms-questions-and-answers)).

**Nothing in the schema distinguishes a preference from a condition.** "Vegetarian" and
"coeliac" are both `data_type = 'text'` and both live in `event_answer.value`. The
distinction is what an organizer types into `label`, so it is **form design guidance, not an
enforced constraint**:

| Belongs on an event form | Does not |
|---|---|
| Dietary preference, T-shirt size, tent preference, bus or own transport | Diagnoses, medication, allergies, conditions |
| What the organizers need **on the day** | The medical file, which `dependent.medical.view` protects |

The reason this is guidance rather than a constraint is honest: a `CHECK` cannot tell
"coeliac" from "vegetarian", and an attempt to would be a keyword list that fails on the
first unusual phrasing. What the schema *can* do — and does — is keep answers scoped to one
event, readable by that event's organizers, and finite in lifetime.

**Open:** the retention policy for answers. A dietary answer citing a medical condition is
health data with a retention obligation, and there is no policy yet
([../open-questions.md](../open-questions.md), G. Events).

---

## 8. Projections and guards

### The unit-authority rule, in SQL

The resolver matches scope **exactly**, so a `unit_leader` at `('org_unit', 7)` does not
satisfy a check at `('event', 42)` — even when unit 7 owns event 42. This is the hinge of
the module ([../domain/07-events.md §6](../domain/07-events.md#6-the-hinge-organizers-and-the-scope-mismatch)).

```sql
-- One permission check for events, used by the API in place of a bare can().
--
-- An event is an ARTIFACT of its owning unit, not a child of it. So a permission is
-- satisfied at ('event', E) if it is satisfied at ('org_unit', E.org_unit_id) AND
-- the event's owner is that same unit.
--
-- This is NOT inheritance downward. It does not reach the unit's SUB-units, and it
-- does not grow when the hierarchy is restructured — the event's owner is one unit,
-- fixed by D-049. Authority for a sub-unit's events still requires that sub-unit's
-- own roles or an exposure, exactly as before.
CREATE OR REPLACE FUNCTION can_event(
    p_person_id       BIGINT,
    p_permission_code TEXT,
    p_event_id        BIGINT,
    p_at              DATE DEFAULT CURRENT_DATE
) RETURNS BOOLEAN LANGUAGE sql STABLE AS $$
    SELECT COALESCE((
        SELECT can(p_person_id, p_permission_code, 'event', e.id, p_at)
            OR can(p_person_id, p_permission_code, 'org_unit', e.org_unit_id, p_at)
          FROM event e
         WHERE e.id = p_event_id
    ), false);
$$;
```

> **`can_event` is a convenience wrapper, not a new channel.** It calls `can()` twice on
> scopes that already resolve, and adds no authority of its own. If the organization later
> decides leaders should not automatically run every event their unit creates, **deleting
> the second `can()` call is the whole change** — and making organizers
> `access_grant`-based then needs no data migration, because nothing was written to
> `access_grant` to make this work.

### Guards

```sql
-- 1. A registration may not be added to a cancelled or closed event, except by an
--    organizer. Enforced as a trigger so every insert path obeys it.
CREATE OR REPLACE FUNCTION check_event_registration_open()
RETURNS TRIGGER LANGUAGE plpgsql STABLE AS $$
DECLARE
    v_event event%ROWTYPE;
BEGIN
    SELECT * INTO v_event FROM event WHERE id = NEW.event_id;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'event % does not exist', NEW.event_id;
    END IF;

    -- Staff may always register, including at a cancelled event (to record who had
    -- been coming) — they are acting deliberately and are attributed.
    IF NEW.source = 'staff' THEN
        RETURN NEW;
    END IF;

    IF v_event.cancelled_at IS NOT NULL THEN
        RAISE EXCEPTION 'event % is cancelled', v_event.id
            USING ERRCODE = 'check_violation';
    END IF;

    IF v_event.registration_opens_at IS NOT NULL
       AND now() < v_event.registration_opens_at THEN
        RAISE EXCEPTION 'registration for event % has not opened', v_event.id
            USING ERRCODE = 'check_violation';
    END IF;

    IF COALESCE(v_event.registration_closes_at, v_event.starts_at) < now() THEN
        RAISE EXCEPTION 'registration for event % is closed', v_event.id
            USING ERRCODE = 'check_violation';
    END IF;

    RETURN NEW;
END $$;

CREATE TRIGGER trg_event_registration_open
    BEFORE INSERT ON event_registration
    FOR EACH ROW EXECUTE FUNCTION check_event_registration_open();

-- 2. An event with registrations cannot be deleted. Cancellation is the mechanism.
CREATE OR REPLACE FUNCTION forbid_delete_event_with_registrations()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM event_registration WHERE event_id = OLD.id) THEN
        RAISE EXCEPTION
            'event % has registrations and cannot be deleted; cancel it instead '
            '(set cancelled_at) so the record of who was coming survives', OLD.id
            USING ERRCODE = 'restrict_violation';
    END IF;
    RETURN OLD;
END $$;

CREATE TRIGGER trg_forbid_delete_event
    BEFORE DELETE ON event FOR EACH ROW
    EXECUTE FUNCTION forbid_delete_event_with_registrations();
```

> **Guard 2 is what makes the `ON DELETE CASCADE` in §3 safe.** Organizers cascade when an
> event is deleted — but an event that anyone registered for cannot be deleted at all. So
> the cascade can only ever fire on a draft with no registrations, which is the only case
> where losing the roster is harmless.

---

## 9. The three queries that matter

### Who has not replied yet?

"Unanswered" is a subtraction ([../domain/07-events.md §3](../domain/07-events.md#3-registration-one-record-two-stored-answers-and-no-unanswered)).
The subtrahend is *who could contribute* — which, for an open event, is an audience:

```sql
-- Everyone who may register for this camp and has not answered.
-- The audience is the eligible set; the registration table is the answered set.
SELECT p.id, p.preferred_name
  FROM access_grant g
  JOIN audience a        ON a.id = g.audience_id
  JOIN person p          ON person_in_audience(p.id, a.id, CURRENT_DATE)
  LEFT JOIN event_registration r
    ON r.event_id = :camp AND r.person_id = p.id
 WHERE g.scope_type = 'event' AND g.scope_id = :camp
   AND g.level <> 'revoked'
   AND g.revoked_at IS NULL
   AND r.id IS NULL
   AND p.id NOT IN (SELECT id FROM person WHERE merged_into_person_id IS NOT NULL)
 ORDER BY p.preferred_name;
```

**This is the query that would be impossible if `unanswered` were a stored value**, because
the eligible set — an audience, evaluated as a rule — is what defines the question. Storing
"unanswered" rows would mean enumerating an audience into rows, and re-enumerating whenever
a child joins the pack.

### Who is actually coming?

```sql
SELECT count(*) FILTER (WHERE NOT r.is_waitlisted) AS attending,
       count(*) FILTER (WHERE r.is_waitlisted)     AS waitlisted,
       count(*) FILTER (WHERE NOT r.is_confirmed AND NOT r.is_waitlisted) AS unconfirmed,
       e.capacity
  FROM event e
  LEFT JOIN event_registration r
    ON r.event_id = e.id AND r.response = 'attending'
 WHERE e.id = :camp
 GROUP BY e.id, e.capacity;
```

The four numbers an organizer needs, in one row: coming, waiting, holding a place without
having paid, and the limit. `attending > capacity` is the overrun, and it is visible here
rather than prevented (§10 check 5).

### Who was actually there?

```sql
-- The camp roster as a safeguarding record, not a plan.
SELECT p.preferred_name, p.birth_date, r.was_present
  FROM event_registration r
  JOIN person p ON p.id = r.person_id
 WHERE r.event_id = :camp
   AND r.response = 'attending'
 ORDER BY r.was_present NULLS FIRST, p.preferred_name;
```

`NULLS FIRST` puts the unmarked at the top, which is the work remaining. Once every row is
`true` or `false`, this is the answer to "who was in the organization's care at that camp" —
and it is the reason `was_present` is three-valued rather than a boolean defaulting to false.

---

## 10. Integrity checks

```sql
-- 1. Events whose owning unit has closed. Either the event was miscategorised or the
--    unit's closure was recorded without ending its future events.
SELECT e.id, e.title, u.code FROM event e
  JOIN org_unit u ON u.id = e.org_unit_id
 WHERE u.status = 'closed' AND u.valid_to IS NULL;

-- 2. Overlapping events for the same unit. Not an error — a pack may run two things at
--    once — but worth a glance, since it is often a duplicate entry.
SELECT a.id, b.id, a.org_unit_id, a.starts_at, a.ends_at
  FROM event a JOIN event b
    ON a.org_unit_id = b.org_unit_id AND a.id < b.id
   AND tstzrange(a.starts_at, a.ends_at, '[)') && tstzrange(b.starts_at, b.ends_at, '[)')
 WHERE a.cancelled_at IS NULL AND b.cancelled_at IS NULL;

-- 3. Events with no organizer. An event nobody is running: either abandoned mid-setup,
--    or a data-entry error. Not a constraint, because an event is legitimately created
--    before its organizers are named.
SELECT e.id, e.title FROM event e
 WHERE NOT EXISTS (SELECT 1 FROM event_organizer o WHERE o.event_id = e.id)
   AND e.cancelled_at IS NULL
   AND e.starts_at > now();

-- 4. Registrations held by people who have been merged away. The merge should have
--    repointed them; this catches the ones it missed.
SELECT r.id, r.person_id, p.merged_into_person_id
  FROM event_registration r
  JOIN person p ON p.id = r.person_id
 WHERE p.merged_into_person_id IS NOT NULL;

-- 5. Events running over their stated capacity. PERMITTED — organizers may exceed
--    deliberately (../domain/07-events.md §8) — so this is a report, not an error.
--    A pattern of overruns means the capacity numbers are wrong, not that the rule is.
SELECT e.id, e.title, e.capacity,
       count(*) AS attending
  FROM event e
  JOIN event_registration r
    ON r.event_id = e.id AND r.response = 'attending' AND NOT r.is_waitlisted
 WHERE e.cancelled_at IS NULL
 GROUP BY e.id, e.title, e.capacity
HAVING e.capacity IS NOT NULL AND count(*) > e.capacity;

-- 6. Unpaid registrations holding a place past the waitlist deadline. Should be empty
--    once the release in §5 has run — a non-empty result means the job is not running.
SELECT r.id, r.person_id, e.title, o.status, e.waitlist_deadline
  FROM event_registration r
  JOIN event e          ON e.id = r.event_id
  JOIN fee_obligation o ON o.id = r.fee_obligation_id
 WHERE r.response = 'attending'
   AND NOT r.is_waitlisted
   AND e.waitlist_deadline < now()
   AND e.cancelled_at IS NULL
   AND o.status IN ('unpaid','partially_paid','overdue');

-- 7. Answers to questions the person was never registered for. Either the registration
--    was deleted, or the answer was written against the wrong person.
SELECT a.id, a.question_id, a.person_id
  FROM event_answer a
  JOIN event_question q ON q.id = a.question_id
 WHERE NOT EXISTS (
     SELECT 1 FROM event_registration r
      WHERE r.event_id = q.event_id AND r.person_id = a.person_id);

-- 8. Presence marked on a registration that declined. Contradictory: you cannot have
--    been present at a thing you said you were not attending.
SELECT r.id, r.event_id, r.person_id
  FROM event_registration r
 WHERE r.response = 'not_attending' AND r.was_present IS NOT NULL;
```

**Check 5 is the important one to read correctly.** It will produce rows, and that is not a
failure — exceeding capacity is a permitted, attributed act
([../domain/07-events.md §8](../domain/07-events.md#8-capacity-and-the-waitlist)). What the
report is *for* is the pattern: an event that overruns every year has a capacity number that
is wrong, and the fix is to change the number rather than to start refusing people.

---

## 11. Open issues

Tracked in [../open-questions.md](../open-questions.md) under **G. Events**.

- ~~**The age ceiling on an open event.**~~ **Settled: there is none**
  ([D-070](../decisions/decision-log.md#d-070--an-event-has-no-age-ceiling-the-grant-is-the-rule)).
  No `min_age`/`max_age` on `event`, no age branch in the registration trigger. If it is ever
  revisited the shape is a new **built-in audience**, not a column on the row.
- ~~**Whether `event.manage_participants` should split.**~~ **It did**, into
  `event.presence.mark` at `contribute` (§4).
- **Retention of `event_answer`.** Answers end with the event, but a dietary answer citing a
  medical condition is health data with a retention obligation, and there is no policy (§7).
- **Cancelled events and fees.** Cancelling keeps the registrations. Whether it releases the
  obligations, refunds them, or neither is the finance module's decision (§6).
- **`was_present` as a safeguarding record.** Whether presence needs its own retention or its
  own permission, given what it is (§9 of the domain doc).
- **Whether organizers should be `access_grant`s after all.** §8's `can_event` makes the
  unit's roles reach its events. If the organization would rather organizers be opt-in per
  event, that is one clause — and no data migration (§8).
- **Waitlist notification.** Promotion is deliberate; telling the promoted person is not
  designed. It belongs to the communication module.

