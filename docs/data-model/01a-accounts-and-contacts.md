# Data Model — Identity: accounts, credentials, contact points, identifiers

`account` and `account_credential` — how a human logs in, and by what — then `person_contact` and
`person_identifier`: where they can be reached, and what other systems call them by. The human these
rows all belong to is [§2](01-identity.md#2-person).

Every pattern referenced here is defined in [00-conventions.md](00-conventions.md).

**Section numbers are shared across the three parts** and never renumbered, because other pages cite
them by number and their anchors are built from them:
[01-identity.md](01-identity.md) holds §1–§3 (the central claim, `person`, `person_name`),
[01a](01a-accounts-and-contacts.md) §4–§7 (`account`, `account_credential`, `person_contact`,
`person_identifier`), and [01b](01b-merges-views-and-checks.md) §8–§11 (`identity_hypothesis`,
`person_merge`, the views, the integrity checks, open issues).

---

## 4. `account`

**Fields**

| Field | Kind | Notes |
|---|---|---|
| `id` | surrogate id | |
| `person_id` | reference to person, required | Not unique. Uniqueness applies only to live accounts, under **Rules** |
| `username` | text, optional | |
| `status` | text, required | One of: `pending_verification`, `active`, `suspended`, `closed`. Default `pending_verification` |
| `verified_at` | timestamp, audit time, optional | |
| `guardian_consent_at` | timestamp, audit time, optional | Set when a guardian confirmed a minor's account. `NULL` for adults (domain/02-actors.md §2) |
| `created_by_staff` | boolean, required | Default false |
| `last_login_at` | timestamp, audit time, optional | |
| `failed_login_count` | integer, required | Default 0 |
| `locked_until` | timestamp, audit time, optional | |
| `status_reason_code` | text, optional | Why suspended or closed |
| `status_note` | text, optional | The human explanation |
| `created_at` | timestamp, audit time | |
| `created_by` | reference to person, optional | |
| `updated_at` | timestamp, audit time | |
| `updated_by` | reference to person, optional | |

**Rules**

- At most one live account per person: unique over `person_id` across the rows whose status
  is `pending_verification`, `active` or `suspended`. Closed rows are not covered, so a
  person may accumulate as many closed accounts as their history contains.
- `username` is unique compared case-insensitively, over the rows that have one and are not
  closed. A closed account releases its username for someone else to take. It covers live
  rows only, not all rows.
- An account may not reach `active` while `verified_at` is absent.
- **An account may not reach `active` while an unresolved `identity_hypothesis` names its person** —
  a hypothesis sitting in `proposed` or `needs_review`, on either side of the pair. This is the second
  gate on the same transition and [D-089](../decisions/round-07-08.md#d-089--one-live-account-a-colliding-sign-up-files-a-claim-and-creates-nothing)
  is why it is here. It is written as a gate on a *status* rather than as a rule against creating the row,
  because the row has to exist for the claim to be attached to anything, and because the queue a claim
  lands in already exists (§8) with its signals, its ordering and its reviewer. See the collision flow
  below for what that buys and what it costs.

**Indexes**

- A person's accounts.

**Why `person_id` is not unique.** The partial unique index expresses the real rule:
*one live account per person*, while permitting closed historical accounts. A plain
`UNIQUE (person_id)` would make it impossible to close an old account and open a new one —
which is exactly the returning-member case at the account level.

**Why `guardian_consent_at` is on `account`, not `person`.** Consent is about the *act of
creating login credentials*, not about the human. A person who was registered as a child
and later reaches majority keeps the same `person` row; the consent record stays attached
to the account it was given for.

**A colliding sign-up files a claim and brings nothing into the world that a human has not approved.**
This is the case the second gate above exists for
([D-089](../decisions/round-07-08.md#d-089--one-live-account-a-colliding-sign-up-files-a-claim-and-creates-nothing)):
someone arrives at the sign-up form through a door the system did not know they had, and their details
strong-match a person who already exists. **The tempting answer was the convenient one** — verify the
e-mail, see that the signals are strong, link the two accounts — and it is
[D-004](../decisions/round-01a.md#d-004--no-automatic-merging-ever) wearing a different coat: a
false-positive link is one human's descriptive data becoming another human's record, and a merge is the
hard part to undo even with §9's reversal. **The other tempting answer was the permissive one** — let the
second live account stand — which drops the uniqueness rule above and splits one person's consents,
payments and attributes across two ids until somebody happens to notice, in exactly the records where
nobody notices. So the system refuses, files the claim, and waits.

**What actually happens, in the order it happens.** The sign-up's rows are created as any sign-up creates
them and stay `pending_verification`; an `identity_hypothesis` is raised naming the two person rows, with
`proposed_by` of `person` because that is what happened — a person asserted this is them — and its
`match_signals` carrying which of them matched; the gate holds the account where it is; the person at the
form sees a holding message. **Nothing is merged, nothing is linked, nothing is activated.** The address
they typed is not thrown away: it stays on the pending account as the credential it was offered as, the
identifier awaiting verification, rather than being echoed back to a browser and lost — which matters
because the reviewer's *second* possible answer is "this is a different person", and that answer should
leave the applicant finishing the sign-up they started rather than starting it again.

**The trigger is a strong match, and the threshold is the whole rule.** A hypothesis is raised at sign-up
on an **exact legacy member number**, or an **exact birth date together with a normalized name match** —
the top of the band [../domain/03-identity-and-legacy.md §4](../domain/03-identity-and-legacy.md#4-match-signals)
already weights, and nothing below it. **The soft band must not raise one.** Blocking a stranger's
registration on a fuzzy score is the failure this rule would most deserve to have caused, and the two
sides of that trade are not symmetric: the cost of letting a true duplicate through is bounded,
reviewable, and caught by the nightly matcher anyway, while the cost of stopping a new member is a child
who cannot sign up to a camp on the day the form closes.

**The holding message confirms nothing, and this is a security requirement rather than a tone choice.**
It says the request was received and will be checked. It says nothing about whether the name, the birth
date or the member number matched anything at all, **because a sign-up form that answers "yes, that
person exists" is an existence oracle over a roster, and this system's roster is children**
([05-authorization.md](05-authorization.md) is the document that spends its length on why that
distinction is worth a resolver). The same form that legitimately helps a returning member find their
account is the form that lets anyone with a birth date enumerate who is enrolled. So the message is
identical whether the match was exact, partial, or absent, and it stays identical whether or not an
account exists to be found.

**Resolving the claim is not a new permission and not a new queue.** A reviewer confirms or rejects the
hypothesis, which is `person.merge` and already sits with `identity_reviewer`; confirming it merges the
two person rows under §9's rules, rejecting it lifts the gate and the account activates. **No new code is
involved on either side**, for the same reason §9 gives for reversal needing none: undoing and correcting
an identity are one act by one named human.

**Confirming the claim closes the placeholder account; it does not move it.** This is the part of the flow
that looks obvious and is wrong, so the wrong version is written out first: the sign-up's person row is
absorbed, the sign-up's account still points at it, so repoint `account.person_id` at the survivor and the
applicant keeps the login they were building. **That write is refused by §4's own rule** — one live account
per person, unique over the pending, active and suspended rows — for the common case where the survivor
already has an account; and in the case where it is *not* refused it quietly makes a login older than the
person's own, carrying a consent timestamp, a verification and a credential history that belong to an act
the survivor never performed. **The rule is instead, in this order:**

1. **Close the placeholder account** — `status` becomes `closed`, with the reason naming the hypothesis
   that closed it. Closed rows are outside the uniqueness rule (§4), which is exactly why closing works
   where repointing does not, and the row survives as the record that someone applied.
2. **Move the credential, not the account.** The typed address was verified as far as it ever was, and
   throwing it away punishes the one person in this flow who did the right thing. It is added to the
   survivor's live account as an `account_credential` row (§5) — credentials are many-per-account already,
   which is why this is an addition rather than an exception. **Where that account has no live account to
   receive it**, the survivor is given one, carrying the moved credential and the placeholder's
   `verified_at`: the address was verified, and making somebody click a second link to prove a claim a
   reviewer has already confirmed is bureaucracy with a security costume.
3. **A credential of the same type already live on the survivor's account is not overwritten.** Two
   password rows do not both become current; the arriving one is left unverified and a `field_conflict`
   (§10's queue) is raised for the person to sort out, because this is the one branch where the system
   cannot tell whether it is looking at the same address typed twice or at two different claims to one
   mailbox.
4. **One audit entry names both accounts, both persons and the hypothesis**, and it is written by the same
   transaction that closes the row. Not two entries, and not the merge's own entry doing double duty: the
   merge says two people became one, and this says a login changed hands, which is the question whoever
   reverses the merge (§9) will actually be asking.

**What this costs is the applicant's session, and it is worth naming.** Someone mid-sign-up whose claim is
confirmed does not continue in the account they were filling in; they log in to the one they already had.
That is one extra login against the alternative of an account that belongs to two people's history at
once, and the holding message (§4 above) is where they are told it.
Two costs come with it and both are stated rather than absorbed. **A genuinely new person who happens to match now
waits for a human**, so the blocking condition carries an age check shaped like `field_conflict`'s thirty
days below, and it alerts: a stalled identity queue stopped being a data-quality problem the moment it
could hold a login, and a person who cannot sign up has no way to say so except by telephoning someone.
**And the reviewer deciding it is deliberately half-blind** — the seeded role holds the merge and no read
over the person record, so it decides from signals and names, which is the correct conservative shape and
also the thing to revisit if reviewers start asking for context they cannot see.

**The everyday case is not this case, and naming it stops the rule being oversold.** "I have a new
e-mail address" has never been a second account and is not one now: `account_credential` (§5) holds many
credentials for one account, so a new address is an *addition* to the login a person already has and runs
past nothing here. The collision case is narrower than signing up twice — it is a person arriving through
a door the system did not know they had.

**A suspended account does not suspend a membership.** They are independent lifecycles.
The schema enforces this by simply not linking them.

---

## 5. `account_credential`

**Fields**

| Field | Kind | Notes |
|---|---|---|
| `id` | surrogate id | |
| `account_id` | reference to account, required | |
| `credential_type` | text, required | One of: `password`, `passkey`, `totp`, `oauth`, `staff_link`. Multiple methods per account. `oauth` supports a national Scout identity provider; `staff_link` supports a one-time link issued to a member who cannot self-serve |
| `secret_hash` | text, optional | Password/OTP hash. Absent for passkey and oauth |
| `external_ref` | text, optional | OAuth subject id, or WebAuthn credential id |
| `external_issuer` | text, optional | OAuth issuer |
| `valid_from` | timestamp, audit time, required | Default: now |
| `valid_to` | timestamp, audit time, optional | `NULL` = current |
| `last_used_at` | timestamp, audit time, optional | |
| `revoked_reason` | text, optional | |
| `created_at` | timestamp, audit time | |

**Rules**

- A `password`, `totp` or `staff_link` credential must carry a `secret_hash`. A `passkey` or
  `oauth` credential must carry both `external_ref` and `external_issuer`. A credential with
  nothing to check against cannot exist.
- `valid_to` is either absent or later than `valid_from`.
- One current credential per `(external_issuer, external_ref)` pair among `oauth` rows that
  are still current. It covers open rows only — an expired credential does not hold its
  external identity back.

**Indexes**

- An account's current credentials — the open half of the period only.
- The `oauth` uniqueness above, which is itself a lookup: given an issuer and a subject id,
  which account is this.

**Why credentials are not columns on `account`.** Adding passkeys, an organizational SSO,
or a one-time-link flow later must not require restructuring `account` and migrating every
existing password. Keeping `secret_hash` off the `account` table also means the common
"show me the user" query never touches credential material.

**`valid_to` on a credential is how password history and revocation are expressed.** A
revoked credential stays as a row, so "was this account ever accessed with a credential
that has since been revoked?" is answerable.

---

## 6. `person_contact`

**Fields**

| Field | Kind | Notes |
|---|---|---|
| `id` | surrogate id | |
| `person_id` | reference to person, required | |
| `contact_type` | text, required | One of: `email`, `phone`, `postal`, `website`, `messaging` |
| `purpose` | text, required | One of: `login`, `membership`, `emergency`, `billing`, `guardian`, `general` |
| `value` | text, required | Normalised per type: emails lowercased, phones E.164, postal as structured JSON |
| `value_detail` | free-form jsonb, optional | For postal addresses: `{street, city, postal_code, country}`. Avoids six optional fields that only apply to one `contact_type` |
| `label` | text, optional | `home`, `work`, `school` — display only |
| `is_primary` | boolean, required | Default false |
| `verified_at` | timestamp, audit time, optional | |
| `verified_by` | text, optional | One of: `self`, `staff`, `bounce_check`, `import` |
| `valid_from` | date, required | Default: today |
| `valid_to` | date, optional | `NULL` = current. Addresses change; history is required |
| `source` | text, optional | `self`, `staff`, `legacy_import` |
| `import_batch_id` | reference to import batch, optional | |
| `created_at` | timestamp, audit time | |
| `created_by` | reference to person, optional | |

**Rules**

- `valid_to` is either absent or later than `valid_from`.
- At most one current primary per `(person, contact_type, purpose)`. It covers open rows
  only: a superseded primary does not block the new one.

**Indexes**

- A person's contact points.
- A person's current contact points by type and purpose — open rows only.
- Email lookup on `value` lowercased, over current email rows only.
- Phone lookup on `value` as stored, over current phone rows only.

**`purpose` is the column that makes this operationally useful.** It lets the permission
system distinguish "a unit leader may see emergency contacts for camp" from "only billing
staff may see payment email addresses". Without `purpose`, every contact is equally
sensitive and the only safe choice is to hide all of them.

**The partial unique index on the primary contact** enforces "one primary email per person
per purpose" without preventing a person from having four non-primary addresses. Note this
index is what makes the merge conflict in
[§8](01b-merges-views-and-checks.md#8-identity_hypothesis-and-person_merge) possible — resolving two `is_primary` rows is a review
step, not a rule.

**The email index is functional — it indexes `value` lowercased** because email matching in
the legacy importer must be case-insensitive, and a plain index cannot serve that.

---

## 7. `person_identifier`

**Fields**

| Field | Kind | Notes |
|---|---|---|
| `id` | surrogate id | |
| `person_id` | reference to person, required | |
| `scheme` | text, required | `national_scout_id`, `legacy_member_no`, `legacy_member_no_oldsystem`, `government_id`, `school_id`, `insurance_no`. Validated against `identifier_scheme` below |
| `value` | text, required | |
| `issued_at` | date, optional | |
| `valid_to` | date, optional | IDs expire or are superseded |
| `verified_at` | timestamp, audit time, optional | |
| `source` | text, optional | |
| `import_batch_id` | reference to import batch, optional | |
| `created_at` | timestamp, audit time | |

**`identifier_scheme`** — the vocabulary of schemes.

**Fields**

| Field | Kind | Notes |
|---|---|---|
| `code` | text, required | The value `person_identifier.scheme` holds |
| `name` | text, required | |
| `is_unique` | boolean, required | Default true. True: a value may appear on only one person (national id, member number). False: values legitimately repeat (school id across schools) |
| `description` | text, optional | |

**Rules**

- **Uniqueness is per scheme, and `identifier_scheme.is_unique` decides it.** For a scheme
  flagged unique, `(scheme, value)` is unique over the identifiers that are still current — those
  with no `valid_to`. A superseded number may be reused; a current one may not be shared. The rule
  covers open rows only.
- **For a scheme flagged not-unique there is no such rule, and that is the point of the flag.**
  `school_id` repeats by design: the same school issues the same number to many children, and each
  of them is a different person who genuinely carries it. `is_unique = false` means one value may
  appear on any number of people, and means it *at enforcement time*, not as a note in a
  description column.
- **Corrected here, and worth reading as a lesson.** The rule as first written applied to every
  scheme and never read the flag; the flag and the rule were the same idea stated twice, once
  enforced and once decorative. The effect was that `school_id` could not in fact repeat — the
  second child at that school with the same number would have been rejected as a duplicate
  identifier, at import time, by a constraint whose own table said it should not exist. **A column
  that no rule reads is not documentation, it is a promise.** This is the same failure D-072 warns
  about from the other side: a rule nobody runs is a convention, and a flag nothing consults is
  decoration. Both read correctly on the page.

**Indexes**

- A person's identifiers.
- The uniqueness lookup above.

**This table is the highest-value asset in the legacy import.** If the old system issued
member numbers, an exact `(scheme='legacy_member_no', value=…)` match is the strongest
identity signal available — strong enough to short-circuit a fuzzy name comparison. See
[../domain/03-identity-and-legacy.md](../domain/03-identity-and-legacy.md#4-match-signals).

**Why not put these on `person` as columns.** A person may have zero identifiers (most
self-registered children), one, or several; schemes appear and disappear over decades; and
`national_scout_id` must be unique while `school_id` must not. Columns would mean a schema
change per scheme and a nullable-unique mess.
