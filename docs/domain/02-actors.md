# Actors, Accounts, and Self-Registration

How a human being gets into the system, what an account is (and is not), and why
registration is deliberately separate from membership.

---

## 1. The core separation

```
   person ─────────── the human being. Exists even with no account and no membership.
     │
     ├── account ──── the ability to log in. Optional. Zero or more per person over time, one live.
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

People register on their own to get access to the system; a person becomes a member only by
requesting a membership, being accepted, and paying the yearly fee. So registration produces an
**account**, not a membership. The person is then a *registered non-member* — able to log in,
maintain their profile, view their own history, and submit a membership request.

The split gives the system a clean place to hang capabilities that must work before membership
exists:

- A caretaker registering to manage a child before deciding whether to join themselves.
- An adult applying to become a counselor, who needs to fill in an application first.
- A returning member from the 90s reconnecting to their history.

### Registration paths

| Path | Actor | Result |
|------|-------|--------|
| Self-registration | an adult, or a minor — the path does not branch on age | `person` + `account` |
| Registration on behalf | caretaker registers a minor who has no account | `person` (child) + `guardianship` |
| Staff-created account | registrar creates one for an adult who is not self-sufficient with computers | `person` + `account`, flagged `created_by_staff` |
| Legacy import | no account created | `person` only, `record_origin = 'legacy_import'` |
| Self-registration claiming history | adult registers and asserts a past membership | `person` + `account` + `identity_hypothesis` |
| Sign-up colliding with an existing person | adult signs up again through an address the system did not know, and **strong**-matches someone who already exists | `person` + `account`, both held at `pending_verification`, + `identity_hypothesis` — and **no merge, no link, no activation**. The address typed survives as the credential it was offered as, and the hypothesis is what holds the account out of `active` (§3) |

### Minor registration

A minor may create an account unattended and nothing in the model objects, because an account is a login
and authority reaches nothing except through grants
([D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape),
[D-166](../decisions/round-22.md#d-166--an-account-is-not-where-authority-over-a-child-lives)). **No
minimum age, no consent step, no branch in the sign-up path.** A new account holds no grants, and a new
account is a person-shaped hole in the database until somebody writes a row about its person — a grant, a
guardianship, a membership — which is what every new account is, not a safeguard designed for this case.
**If the organization wants a guardian's answer on record**, it goes on the guardianship relationship,
which already carries `right_level` and its own dates
([../data-model/04-relationships.md §2](../data-model/04-relationships.md#2-the-guardians-right-none-view-or-write));
no column returns for it. **What this page does not decide** is whether the law of this country demands a
consent step regardless — a policy in front of the legal review beside the four data policies, and stated
there ([06b §6](../data-model/06b-redaction-and-checks.md#6-open-issues)).

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

**And a gate this table cannot express.** `active` has a second condition beyond verification: an
account may not reach it while an unresolved `identity_hypothesis` names its person. One live account
per person is the rule doing the underlying work — uniqueness says a person may not *hold* two live
accounts, and the gate says the second arrival waits for a human rather than being merged into the
first or quietly linked to it.

**Why a human, and not an automatic link:** a merge made by machine turns one person's false positive
into one person's record becoming another's. Making a queue state block a login buys two obligations,
and both are checks rather than intentions:

- **A hypothesis that is blocking an account is age-checked.** A queue that stalls is
  not a data-quality problem with no victim you can name: it is a specific person who cannot log in,
  whose only remaining channel is to telephone someone. Nothing here will tell anyone the queue has
  stalled — no message is sent, and the age on a row is the whole of the warning
  ([D-164](../decisions/round-22.md#d-164--nobody-is-told-and-no-page-may-say-otherwise)),
  which is why the block carries a number rather than sitting in a list.
- **The message the person sees confirms nothing.** Not that the name matched, not that the birth date
  did, not that anyone by that name exists — because a sign-up form that can answer "yes, that person
  exists" is an existence oracle, and this system's roster is children.

The trigger is a *strong* match only — exact legacy member number, or exact birth date together with a
normalised name. The scored band below that raises nothing at sign-up: blocking a stranger's
registration on a fuzzy score is the failure this rule would most deserve
([03-identity-and-legacy.md §4](03-identity-and-legacy.md#4-match-signals)).

Why: [D-089](../decisions/round-07-08.md#d-089--one-live-account-a-colliding-sign-up-files-a-claim-and-creates-nothing).

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

### When nobody who can hold `system.admin` can sign in

`system.admin` is the capability this system has no substitute for: it is what rotates or ends an
integration that is writing right now, what releases a data subject's erasure, and the only code that
satisfies every other check ([D-068](../decisions/round-05.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle)).
**A key cannot be the way back in** — it is not a person, carries nobody's authority, and may never be
granted that code ([D-122](../decisions/round-16.md#d-122--what-a-key-owes-the-catalog-four-codes-at-the-unit-and-the-fourth-owed-thing-declined))
— and no self-service path exists anywhere here: nobody joins, appoints or un-suspends themselves, so an
emergency door would be the second, weaker authorization this design rejects by name.
**What exists instead is a report and this procedure**
([D-126](../decisions/round-17.md#d-126--break-glass-is-a-report-and-a-written-procedure-not-a-mechanism)).

1. **Read the report before acting from memory.** Integrity check 9 lists everyone with a live allow of
   `system.admin`, however they came by it, and says for each of them whether they can sign in:
   `account.status` is `active` **and** their credential is live
   (`account_credential.valid_to` unset or in the future, not revoked). An **empty second column is the
   alert**, and the alert is a report somebody opens rather than a message somebody receives: nobody is
   told when that column empties, which is precisely why step 1 says to read the report instead of acting
   from memory and step 2 names a person long before one is needed
   ([D-164](../decisions/round-22.md#d-164--nobody-is-told-and-no-page-may-say-otherwise),
   [05d §11](../data-model/05d-invariants-and-seed.md#11-invariants-to-verify)).
2. **One named person is written down before it is needed**, and someone knows their telephone number.
   **`api_key.owner_person_id` is not that person** — it answers *whose integration is this*, not *who
   fixes it* ([D-120](../decisions/round-16.md#d-120--a-key-outlives-whoever-created-it-and-the-report-is-the-control)).
3. **The recovery is performed on an account, never on a grant.** Un-suspend the account, or re-issue the
   credential, whichever is the actual obstacle. **This is the one write in this design made outside the
   application, and it stays that way**: it produces no audit row, and nothing in the schema distinguishes
   it from somebody editing a row they had no business editing.
4. **Everything after it is ordinary.** The recovered person acts through the screens, so every authority
   change that follows carries `granted_by`, an `authorization_channel` and an audit row like anybody else's.
   **The recovery restores a person's access; it does not hand out authority**, which is the difference
   between this and the sealed emergency credential that was refused.

**What catches the edit afterwards** is one line of the integrity-check list: an audited row whose newest
audit row predates its `updated_at` is a change the trail never saw
([06b §5](../data-model/06b-redaction-and-checks.md#5-integrity-checks)). It is a report rather than a guard,
and it is honest about its own limit — whoever can make the edit can also write an audit row by hand, because
the trail is append-only to the application and not to whoever holds the database. **That is the residual
risk this procedure accepts, stated here so that nobody discovers it during the incident.**

---

## 4. Contact points and identifiers

A person's email, phone and address are **rows, not columns**. Each row carries its type, its
purpose, its value, whether it is the primary one for that type and purpose, when it was
verified, and the period it applied for.

Why not just `person.email`:

- People have several emails (personal, school, work) and which one is primary changes.
- A caretaker's contact details are often the *effective* contact for a child; the system
  needs both the child's own contact and the adult's.
- Addresses change, and history is kept: an address row with a validity period answers
  "where did this member live in 2003?", which a column cannot.
- Changing an email must not lose the old one, because historical records may reference it.

**Purpose** is the field that makes this useful operationally:
`login`, `membership`, `emergency`, `billing`, `guardian_contact`. A person can have one
address for billing and another for emergency contact, and the permission system can treat
them differently — emergency contacts are visible to whoever holds the roster read on that
camp; billing details are not.

### External identifiers

One row per identifier held against a person: a `scheme`, a `value`, and when it was verified
if it ever was. `(scheme, value)` is unique among the identifiers that are still current — a
superseded number may be reused, a current one may not be shared.

Identifiers issued *outside* the system belong here: a national Scout registration number, a
government ID, an old membership card number from a previous system, a school ID. Keeping
these separate from contact points is what gives the legacy import somewhere to put the old
system's member numbers — which is precisely what makes reconnecting 1990–2010 members
possible. See [03-identity-and-legacy.md](03-identity-and-legacy.md).

---

## 5. Acting on behalf

Both read and write access for a caretaker are **explicit**:

- A `guardianship` row establishes the *relationship*.
- That row carries one right — `none`, `view`, or `write`. Being the parent implies nothing;
  a row at `none` grants literally nothing.

The right is **one value, not a capability list**, compared against
`permission.right_kind ∈ read | write`: `none` covers nothing, `view` covers the codes marked
`read`, `write` covers both. A court order that lets one parent register the child for events
but not read the rest of the record cannot be written, and neither can "roster visibility and
nothing else": a guardian at `view` reads the child's record whole, because the record has no
compartment inside it to be excepted from
([D-074](../decisions/round-06.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular),
[D-083](../decisions/round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)).
What the right is, and keeps: explicit, dated, revocable, audited — one deliberate value per row
rather than an inference from who someone is.

**`write` is not a license over the organization.** The ceiling is the channel, not a rank: the
guardianship channel is entered only when the check is about somebody other than the actor, so the
widest right in the system reaches this child's record and cannot reach a roster, a fee schedule or
another family — those checks are not about the child and the channel is never asked
([D-079](../decisions/round-06.md#d-079--the-guardianship-channel-is-entered-by-shape-not-by-permission-name)).
Authority is per row, so a guardian of one child sees nothing of another's. A deny still refuses a
guardian holding `write`, absolutely and regardless of scope — what is unavailable is a *narrow*
deny, not the ability to say no. There is no per-resource `admin` wildcard either; a role that needs
broad reach lists what it grants
([D-068](../decisions/round-05.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle)).

History is kept: every change of the value is a new `guardianship_permission` row, and the
value on the `guardianship` row is always the open one's.

**How a check resolves.** A check about a dependent is evaluated against the `guardianship`
row for the `(guardian, dependent)` pair and the right level it holds, not against roles. This
keeps the two authority channels distinct:

- **Grants** answer "what may this person do in the organization?"
- **Guardianship** answers "what may this person do regarding this child?"

An office confers nothing by being held
([D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)),
so holding one gives nobody a guardian's right over a child and leadership has no channel of its own:
a leader reaches data the way every other non-guardian does, through grants. If the organization needs
its leaders to see a camper's emergency contacts, that is *said*, as a grant of `person.view`, and the
scope chosen is the entire decision — **every member of the organization** or **the people on one
event**, with nothing between them
([D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)), and
`person.view` has no narrower cousin to reach for if the first one turns out to feel like what it is
([08-person-data.md](08-person-data.md)). Audited either way; never through a fictional guardianship.

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

- Whether staff-created accounts are allowed for children, or only adults. **Still open, and untouched by
  the fact that the sign-up path has no age gate:** [D-166](../decisions/round-22.md#d-166--an-account-is-not-where-authority-over-a-child-lives)
  removes a gate on a path, not a policy about who may open an account on somebody else's behalf, so a
  reader who takes "no gate" to mean "staff may create a child's account" has read further than the answer
  goes. The `created_by_staff` flag on `account` ([01a §4](../data-model/01a-accounts-and-contacts.md#4-account))
  stays whichever way this is settled.

**Not registered in [../open-questions.md](../open-questions.md),** and a reader of the register alone
would not find it: this page is the only place the question is written down.

---

*Decisions behind this page: D-068, D-074, D-079, D-083, D-089, D-097, D-099, D-100, D-164, D-166.*
