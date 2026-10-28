# Domain Overview

What the organization is, who interacts with the system, and how the core lifecycles
flow. Read [../glossary.md](../glossary.md) first — this document uses its terms
strictly.

---

## 1. The organization

A youth organization (Scout-like: uniformed groups, trained adult leadership, camps
and weekly meetings) with:

- **Child members** — youth participants, typically organized into units.
- **Adult members** — counselors/leaders who run units and hold positions.

*(These two are how the organization talks about people. They are **not** two kinds of membership: there
is one membership type and it is ageless, so the sentence "is this person a child?" is a question about
`person.birth_date` and today's date — see [§2](#2-actors) and
[D-038](../decisions/decision-log.md#d-038--membership-is-ageless). Nothing downstream keys off the
difference except guardianship, position eligibility, and the mirroring rule for messages.)*
- **Caretakers** — parents and legal guardians of child members. They may or may not
  be members themselves.
- **Non-member supporters** — people who interact with the organization (donors,
  volunteers, alumni) without holding a membership.

The organization has **sub-units that nest** and that have been **reorganized repeatedly
over four decades**. Both facts are load-bearing and are handled in
[04-organization-structure.md](04-organization-structure.md).

---

## 2. Actors

The system distinguishes actors by *what they can do*, not by *what they are*. The full
treatment is in [02-actors.md](02-actors.md); the summary:

| Actor | Has account? | Has membership? | Can do |
|-------|-------------|-----------------|--------|
| Anonymous visitor | no | no | see public info, submit a registration or a membership request |
| Registered person | yes | no | maintain own profile, submit/renew a request, view own history |
| Member | yes | yes | own profile, unit participation, event signups, own history — **the same actor whether or not `birth_date` makes them a minor today** |
| Caretaker | yes | maybe | view/act on their dependents — **only** as explicitly granted |
| Staff / registrar | yes | maybe | organization-wide administrative permissions |
| Historical record | no | **a bounded period, if the export states one** | nothing. Data only, never a login. |

**The two member rows this table used to carry — "Member (child)" and "Member (adult)" — were one row
wearing two hats.** There is one membership type ([D-037](../decisions/decision-log.md#d-037--exactly-one-membership-type-the-fee-is-flat-and-per-person))
and it is ageless ([D-038](../decisions/decision-log.md#d-038--membership-is-ageless)), so the difference
between them was always `person.birth_date` against today's date, which changes on its own and is a fact
about a person rather than a kind of account. What a minor genuinely cannot do on their own is a
guardianship question, not an actor type
([02-actors.md](02-actors.md)).

The last row matters twice, and its answer changed in round 9. Imported rows create `person` rows with
**no account**, and must never be blocked from import by a "users must have email addresses" rule. They
also create **`membership` rows now** — bounded ones, both ends dated, only for the periods the people
export states, `data_confidence = 'low'` and marked with the batch that wrote them
([D-092](../decisions/decision-log.md#d-092--the-corpus-is-people-and-events-and-it-names-no-units),
[D-093](../decisions/decision-log.md#d-093--the-one-off-import-may-create-memberships-both-ends-dated)).
**What the earlier answer got right and still binds**: it refused to make a membership out of an
attendance row, and that refusal survives as the rule that an imported period is never open-ended and
never inferred from presence
([D-090](../decisions/decision-log.md#d-090--the-legacy-corpus-is-thousands-of-roster-rows-with-numbers-and-no-money));
and no sub-unit row is ever imported, because neither export names a sub-unit, so "who was in Pack 12 in
1998?" has no system answer at go-live
([03-identity-and-legacy.md §7](03-identity-and-legacy.md#7-legacy-import-pipeline)).

---

## 3. The three lifecycles

Almost everything in the system is one of three multi-step processes. They are separate
because they succeed and fail independently: you can register without applying, apply
without being accepted, be accepted without paying, and pay without ever joining a unit.

### 3.1 Account lifecycle

```
                  ┌─────────────────────────────────────────────┐
                  │                                             │
 (none) ──register──> pending_verification ──verify──> active ──┴──> suspended
                                                            │              │
                                                            └──> closed <──┘
```

An account is about **authentication only**. It says "this person can log in". It says
nothing about membership. A person can hold a verified, active account for years and
never become a member — a parent who only ever manages their child is exactly this case.

**One gate the arrows do not draw:** an account may not reach `active` while an unresolved
`identity_hypothesis` names its person, which is what a sign-up that strong-matches someone who
already exists runs into ([D-089](../decisions/decision-log.md#d-089--one-live-account-a-colliding-sign-up-files-a-claim-and-creates-nothing)).
Verification is necessary and not sufficient; a human decision is the second condition, and because
that makes a stalled queue a person who cannot log in, the blocking hypothesis is age-checked and
alerts. One live account per person is the rule doing the underlying work
([02-actors.md §3](02-actors.md#3-account-state-machine)).

### 3.2 Membership lifecycle

```
 (none)
   │
   ├─ request submitted ──> under_review ──accept──> approved ──payment confirmed──> active member
   │                             │                                                    │
   │                             └──reject──> rejected                                 │
   │                                                                                   │
   │                                     ┌─────────────────────────────────────────────┤
   │                                     │                                             │
   │                                     ├──> lapsed (fee expired at the yearly date)  │
   │                                     ├──> terminated (cause, with reason)          │
   │                                     └──> suspended (temporary hold)               │
   │                                                                                   │
   │      ┌──────────────── renewal (no new application) ────────────────────────────┘
   │      │        inside the renewal window → the new period opens at the expiry date
   │      │        after it                  → the new period opens at the payment date
   │      ▼
   │   active member again
   │
   └──────────────────────── re-apply ─────────────────────────────────────────────────┘
```

Every transition creates or closes a row; nothing is overwritten. A person who was a
member 1990–2010 and again from 2024 has two `membership` rows and the gap is visible
as data, not inferred from a date.

**Note the shape of the lapse.** There is no `completed` state: it existed only for ageing
out, and membership is ageless ([D-038](../decisions/decision-log.md#d-038--membership-is-ageless)).
And **the lapse happens on a date, to everyone at once** — the yearly expiry — which is why
the renewal path matters more here than the word "grace" suggests
([D-040](../decisions/decision-log.md#d-040--the-fee-expires-yearly-a-date-tracked-renewal-window-replaces-a-grace-status)).

Detailed in [05-membership-lifecycle.md](05-membership-lifecycle.md).

### 3.3 Authorization lifecycle

```
 (none) ──grant──> active ──expire/revoke──> inactive
                     │
                     └──delegate──> delegated grant (with end date, provenance recorded)
```

Every grant has a start, an end, a granter, and a reason. Nothing is permanent by
default and nothing is revoked by deletion. Detailed in
[06-authorization-model.md](06-authorization-model.md).

---

## 4. The relationships between people

Three distinct relationships, deliberately not merged:

| Relationship | Direction | Example | Grants access? |
|--------------|-----------|---------|----------------|
| **Guardianship** | guardian → dependent | parent → child | **No** by itself — only the `right_level` (`none` / `view` / `write`) carried on the live `guardianship` row. Since D-074 that value is the whole authority; `guardianship_permission` keeps only its history. |
| **Membership** | member → the organization | anyone → the root unit | No. |
| **Participation** | participant → sub-unit | child → Pack 12 | No. |
| **Position held** | person → position in a sub-unit | adult → scoutmaster of Pack 12 | No. Only via `role_assignment`. |

**Membership and participation are two rows, not one** ([D-041](../decisions/decision-log.md#d-041--belonging-to-a-sub-unit-is-a-participation-record-not-a-membership)).
A person is a **member of the organization** and a **participant in a pack** — different
facts with different lifetimes, which is why someone who stops attending on Thursdays is
still a paid-up member, and someone who is paid up may take part in nothing.

The recurring theme: **participation is not authority.** A person can be deeply involved
— a parent of three members, a 20-year veteran, a pack's founder — and still have no
administrative access. Access comes only from an explicit grant. This separation is what
makes the permission system auditable and what prevents the classic failure where a
relationship ends (custody changes, a leader steps down) but access silently persists.

### The counselor-who-is-also-a-parent case

You named this case explicitly. It is not special:

- One `person` row.
- One open `membership` — `member`, like everyone else's.
- A `position_assignment` making them a leader of their pack.
- One `unit_participation` row for the pack they lead.
- Two `guardianship` rows (to their own children).
- Separate `guardianship_permission` rows for their parental capabilities.
- `role_assignment` rows for their leadership authority.

Note there is no `counselor` membership type. Being a counselor is the **position**, not a
kind of membership ([D-037](../decisions/decision-log.md#d-037--exactly-one-membership-type-the-fee-is-flat-and-per-person)) —
and this person's membership is identical to that of the child they lead, which is exactly
the point.

Their leadership role grants authority over **the unit's members**. Their guardianship
grants authority over **their own children**. These are different scopes and the system
keeps them separate — critically, being a leader does *not* give them access to other
people's children's records beyond what their leadership role explicitly permits.

> This last point is a safety property, not a convenience. Child-protection rules
> generally require that a leader's access to minors' personal data be bounded by their
> function. Keeping `role_assignment` and `guardianship_permission` as separate tables
> makes that boundary enforceable and reportable.

---

## 5. Multiplicity, in both directions

You specified: *one parent can manage multiple children; multiple children can be managed
by the same parent.* The model generalizes both:

- One guardian → many dependents (many `guardianship` rows).
- Many guardians → one dependent (both parents, stepparents, legal guardians — the
  schema makes no assumption that a child has exactly two, or exactly one).
- A guardian's authority over each dependent is **per-dependent**, so a parent can hold
  full permissions for one child and only read access for another (a realistic custody
  arrangement).

The same person can also be a guardian *of* someone and a dependent of someone else — the
relation is a general graph, not a two-level hierarchy. This costs nothing to allow and
avoids a rewrite when a member turns 18 and becomes guardian to a sibling.

---

## 6. The four decades of history

This is the constraint that most shapes the schema, so it is worth stating plainly.

The system must answer, correctly and indefinitely:

- "Who was in Pack 12 on 1 June 1998?"
- "Was this person a member when they attended that camp in 2003?"
- "This person registered in 2026 claiming they were a member in the 90s — is that true?"
- "What was this unit called in 2001, and what is its successor unit today?"

Consequences, all of which the data model implements:

1. **Everything temporal is a period**, never a boolean or a single date.
2. **Nothing is hard-deleted**, except by three named acts, each of which is somebody's decision
   rather than a cleanup job. Merges leave tombstones and units that closed keep their rows. Against
   that: **erasing a person** redacts their values wherever they were copied, including in the audit
   payload, immediately and at any age; **payload reduction** empties an audit row's values 24 months
   after they were written and leaves the row standing, so the trail keeps answering *who changed this,
   when, and were they allowed to* indefinitely and stops answering *and to what*
   ([D-088](../decisions/decision-log.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short));
   and **reverting an import batch** removes the rows that batch created. Reduction is not redaction —
   one answers to a person and is absolute, the other answers to a calendar and is bounded — and the
   accounting skeleton (`membership`, fees, payments) is deliberately outside all three: it is kept
   indefinitely as the organization's own history. *Assumption:* that "forever" has a legal basis is
   exactly the thing this document cannot establish for itself; the claim is recorded as an assumption
   awaiting review, not as settled law.
3. **Names change.** Units get renamed and renumbered; people change names. Names live in
   child tables with validity periods, not as columns that get overwritten.
4. **Imported data is low-confidence.** A 1994 roster has names, dates, and on most rows a legacy
   member number — which keys the organization's paper, not a session, and is exactly what is missing
   from the records that most need matching. This bullet used to say "no reliable unique key", written
   before the corpus had been described. Import still therefore *proposes* identities and a human
   confirms them, and where a number is present the proposal is a lookup rather than a guess.
   See [03-identity-and-legacy.md](03-identity-and-legacy.md).

---

## 7. What this design deliberately does not decide yet

These are referenced by the schema but not designed, pending your specification:

*(Events came off this list: they were specified, in [07-events.md](07-events.md) and
[data-model/08-events.md](../data-model/08-events.md), along with the thirteen codes in the catalog.)*

- **Fees and payments** — a provisional shape exists in
  [../data-model/07-finance.md](../data-model/07-finance.md) because membership
  activation depends on it. Expect to rewrite it.
- **Notifications, documents, reporting, API/UI.** *(Health records went off this list in round 7 —
  there is no health module, because [D-083](../decisions/decision-log.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)
  found no category to build one around; the facts live in the personal-attribute layer,
  [domain/08](08-person-data.md).)*

---

## 8. Next

- Terminology → [../glossary.md](../glossary.md)
- Accounts and registration → [02-actors.md](02-actors.md)
- Historical data → [03-identity-and-legacy.md](03-identity-and-legacy.md)
- Units → [04-organization-structure.md](04-organization-structure.md)
- Membership → [05-membership-lifecycle.md](05-membership-lifecycle.md)
- Permissions → [06-authorization-model.md](06-authorization-model.md)
