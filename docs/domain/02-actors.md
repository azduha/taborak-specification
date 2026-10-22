# Actors, Accounts, and Self-Registration

How a human being gets into the system, what an account is (and is not), and why
registration is deliberately separate from membership.

---

## 1. The core separation

```
   person ─────────── the human being. Exists even with no account and no membership.
     │
     ├── account ──── the ability to log in. Optional. Zero or more per person over time.
     │
     └── membership ─ the state of being a member. Optional. Zero or more periods.
```

These are three independent things. Any combination is legal:

| State | Example |
|-------|---------|
| person, no account, no membership | 1994 roster entry imported from paper. |
| person, account, no membership | A parent who registered to manage their child. |
| person, account, membership | An active member. |
| person, no account, membership | An adult member who never uses the system; staff manage them. |
| person, account, *lapsed* membership | Someone who let their membership lapse but still logs in. |

The schema must not reject any of these. In particular there must be **no requirement
that a person has an email address**, or that a member has an account — otherwise the
historical import is impossible.

---

## 2. Who registers, and why

You said: *"The people can register on their own to get access to the system, however
they become member only if they request a membership, they get accepted and pay a yearly
fee."*

So registration produces an **account**, not a membership. The person is then a
*registered non-member* — able to log in, maintain their profile, view their own history,
and submit a membership request. This is the correct split, and it gives the system a
clean place to hang capabilities that must work before membership exists:

- A caretaker registering to manage a child before deciding whether to join themselves.
- An adult applying to become a counselor, who needs to fill in an application first.
- A returning member from the 90s reconnecting to their history.

### Registration paths

| Path | Actor | Result |
|------|-------|--------|
| Self-registration | adult, or a minor with guardian involvement | `person` + `account` |
| Registration on behalf | caretaker registers a minor who has no account | `person` (child) + `guardianship` |
| Staff-created account | registrar creates one for an adult who is not self-sufficient with computers | `person` + `account`, flagged `created_by_staff` |
| Legacy import | no account created | `person` only, `record_origin = 'legacy_import'` |
| Self-registration claiming history | adult registers and asserts a past membership | `person` + `account` + `identity_hypothesis` |

### Minor registration — the consent problem

*Assumption:* a minor may not create an account unattended. The schema supports
requiring a guardian's confirmation before a minor's account becomes usable, via
`account.guardian_consent_at`. See [../open-questions.md](../open-questions.md) for the
age threshold and whether consent is required at all in your jurisdiction.

---

## 3. Account state machine

| Status | Meaning |
|--------|---------|
| `pending_verification` | Registered; email/phone not yet confirmed. Minimal capabilities. |
| `active` | Normal. |
| `suspended` | Temporarily blocked (security, disciplinary). Membership unaffected. |
| `closed` | Voluntarily or administratively closed. Retained for audit; login refused. |

Two deliberate choices:

- **Suspending an account does not suspend a membership.** They are separate lifecycles;
  a person can be an active member with a suspended account (they'd interact by phone).
- **Closing an account does not delete the person or their history.** The `account` row
  is closed and retained. `person` and all `membership` rows are untouched.

### Credentials

`account` holds authentication material. Two rules worth fixing now:

1. **The password hash lives in `account_credential`, not in `account`.** This leaves
   room for multiple authentication methods (password, passkey, OAuth via a national
   Scout identity provider, staff-issued one-time links) without restructuring.
2. **Never share an account between a parent and a child.** The temptation is real —
   "the parent will just log in as the kid" — but it destroys attributability. The
   correct mechanism is [acting on behalf](#5-acting-on-behalf), which records *who*
   acted and *as whom*. An account shared between people makes every audit entry
   worthless, and in a youth organization the audit trail is the point.

---

## 4. Contact points and identifiers

A person's email, phone and address are **rows, not columns**. Each row carries its type, its
purpose, its value, whether it is the primary one for that type and purpose, when it was
verified, and the period it applied for.

Why not just `person.email`:

- People have several emails (personal, school, work) and which one is primary changes.
- A caretaker's contact details are often the *effective* contact for a child; the system
  needs both the child's own contact and the adult's.
- Addresses change; you asked to preserve history. An address row with a validity period
  answers "where did this member live in 2003?" — a column cannot.
- Changing an email must not lose the old one, because historical records may reference it.

**Purpose** is the field that makes this useful operationally:
`login`, `membership`, `emergency`, `billing`, `guardian_contact`. A person can have one
address for billing and another for emergency contact, and the permission system can treat
them differently — emergency contacts are visible to a unit leader on a camp roster;
billing details are not.

### External identifiers

One row per identifier held against a person: a `scheme`, a `value`, and when it was verified
if it ever was. `(scheme, value)` is unique among the identifiers that are still current — a
superseded number may be reused, a current one may not be shared.

For identifiers issued *outside* the system: a national Scout registration number, a
government ID, an old membership card number from a previous system, a school ID. Keeping
these separate from contact points means the legacy import has somewhere to put the old
system's member numbers — which is precisely what makes reconnecting 1990–2010 members
possible. See [03-identity-and-legacy.md](03-identity-and-legacy.md).

---

## 5. Acting on behalf

Per your answer, both read and write access for a caretaker must be **explicit**. So:

- A `guardianship` row establishes the *relationship*.
- That row carries one right — `none`, `view`, or `write`. Being the parent implies nothing;
  a row at `none` grants literally nothing.

The right is **one value, not a capability list**
([D-074](../decisions/decision-log.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular)).
The `dependent.*` codes this document used to enumerate are deleted — eighteen of them across
the catalog — and with them go the cases they existed for: a guardian who may register the child for events but may not
read the medical record cannot be expressed, and neither can "read-only, but not the medical
file". What survives is what made the list worth having — the right is explicit, dated,
revocable and audited, one deliberate value per row rather than an inference from who someone
is. `write` ranks at `contribute` and not at `manage`, so a guardian still cannot do
organization-wide things and cannot reach a different dependent's records. A role that needs
broad reach over its own side of the model still lists what it grants explicitly — there is no
per-resource `admin` wildcard
([D-068](../decisions/decision-log.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle)).
History is kept: every change of the value is a new `guardianship_permission` row, and the
value on the `guardianship` row is always the open one's.

**How a check resolves.** A check about a dependent is evaluated against the `guardianship`
row for the `(guardian, dependent)` pair and the right level it holds, not against roles. This
keeps the two authority channels distinct:

- **Roles** answer "what may this person do in the organization?"
- **Guardianship** answers "what may this person do regarding this child?"

A unit leader does not hold a guardian's right over unit members by virtue of leading
the unit. If the organization genuinely needs leaders to see a camper's emergency contacts,
that is granted through a *role* permission with a unit scope, resolved at the event, and
audited — not through a fictional guardianship.

### Recording acts on behalf

Every operation performed on behalf of another person writes to `access_log` with both
parties: `actor_person_id` is the parent, `subject_person_id` is the child, and `on_behalf`
records that the actor acted *for* the subject rather than as themselves.

This is not optional bookkeeping. When a parent changes a child's address or registers them
for a camp, the record must show that the *parent* did it, not the child. Without this,
the audit trail falsely attributes the parent's actions to the child.

---

## 6. Effective contact for a minor

A recurring operational need: "who do we call about this child?" The answer is usually a
guardian, but not always the same one, and not always the one with the most permissions.

Resolve it as three conditions on `guardianship`, applied in this order: the row's dependent is
this child; the row is still open today, meaning `valid_to` is absent or later than today — a
guardianship that has ended is not an answer, so the date is checked on the row rather than
assumed; and `is_primary_contact` is set. The answer is the contact points of *those* guardians
whose purpose is `emergency`.

`is_primary_contact` on `guardianship` is separate from the guardian's right level on purpose: a guardian
with no system access at all can still be the emergency contact. Do not require login
capability to be reachable in an emergency.

---

## 7. Open issues

- Minimum age to hold an account; whether guardian consent is legally required.
- ~~Whether guardian permissions lapse automatically at majority, or by review.~~
  **Neither** — no automatic transition and no review queue
  ([D-069](../decisions/decision-log.md#d-069--guardianship-ends-when-a-person-ends-it-the-system-takes-no-position-on-majority)).
  **What that left: whether the subject may end the guardianship themselves** once adult.
  **They may** — the parties to a guardianship are principals on the row, and none of it
  routes through staff ([D-073](../decisions/decision-log.md#d-073--guardianship-is-administered-by-its-own-parties-not-by-staff)).
  Closed — see [E-5](../open-questions.md#e-5--closed--the-parties-administer-their-own-row).
- Whether staff-created accounts are allowed for children, or only adults.
- Whether a person may hold more than one active account at a time (recommend: no).

All tracked in [../open-questions.md](../open-questions.md).
