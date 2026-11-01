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
| `created_by_staff` | boolean, required | Default false |
| `last_login_at` | timestamp, audit time, optional | |
| `failed_login_count` | integer, required | Default 0 |
| `locked_until` | timestamp, audit time, optional | |
| `status_reason` | text, optional | Why suspended or closed, in the words of whoever did it (D-128) |
| `status_note` | text, optional | The human explanation |
| `opt_in_email` | boolean, required | Default `false`. **The account's own answer about its one door outside the inbox**, on this row rather than on anything a sender can touch ([D-213](../decisions/round-25.md#d-213--the-account-chooses-its-own-doors-a-childs-message-mirrors-as-its-own-rows-and-only-e-mail-lands-today)); [the messaging module](10-messaging.md) is what reads it |
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
- **Staff may create an account for a person who has not signed up** — the useful case being a camp
  office with a paper list. The row sits at `pending_verification`, which is already its default, and it
  **cannot authenticate until the person it belongs to, or that person's guardian, sets a credential** —
  the same shape as the gate above: the row is worth having before it can be used, because it is what a
  registration attaches to, and refusing the insert would push staff into recording a child somewhere
  worse than the database ([D-179](../decisions/round-23.md#d-179--staff-may-open-an-account-only-its-person-can-start-it)).
  Said the other way round: **nobody ever holds a child's password**. What this does *not* refuse is a
  staff member setting a password at the moment of creating the row; the write is audited, the gate that
  allows it names who holds it, and the control is the trail
  ([D-137](../decisions/round-20.md#d-137--a-guardian-may-appoint-a-guardian-and-nobody-at-the-organization-is-told)).
  An organization that wants that pattern impossible rather than visible wants an explicit `deny` on the
  write that sets a credential for somebody who is not you.
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

**An account is a login, and nothing about a child is decided here.** `account` keeps the columns that
describe authentication — and one that does not, `opt_in_email` below, which is the account's own answer about
its own mail and decides nothing about anybody either, least of all a child. Nothing else is kept here: there
is no minimum age for an account, no consent step, and no branch
in the sign-up path that a minor's sign-up takes and an adult's does
([D-166](../decisions/round-22.md#d-166--an-account-is-not-where-authority-over-a-child-lives),
[D-213](../decisions/round-25.md#d-213--the-account-chooses-its-own-doors-a-childs-message-mirrors-as-its-own-rows-and-only-e-mail-lands-today)). What a
new account can reach is nothing until somebody writes a row about its person — a grant, a guardianship,
a membership — which is what every new account is anyway, not a defence built for this case. **If the
organization wants a guardian's answer on record**, it goes on the guardianship relationship, where an
adult's authority over a child is already written, dated, revocable and carrying its own `right_level`
([04 §2](04-relationships.md#2-the-guardians-right-none-view-or-write)); no column returns here for it.
**Every person may have their own login** — a person signs in with Google or an e-mail address and a
password ([D-176](../decisions/round-23.md#d-176--google-or-a-password-one-identity-one-account-and-the-invariant-finally-has-a-check))
— **and a child with no Google account and no e-mail of their own has no account, which the model must not
be read as needing.** Such a child is not given a second-class credential, a shared mailbox or a login
held by staff; the way an adult acts for them is the guardianship row, and an account staff open for them
waits to be claimed (Rules above; [D-178](../decisions/round-23.md#d-178--a-child-without-a-login-is-reached-through-the-guardianship-row)).

**The one column here that is not about logging in, and why it is here.** `opt_in_email` is the account's own
yes or no about having its messages delivered to it outside the system, and it is [D-077](../decisions/round-06.md#d-077--messaging-is-direct-by-default-broadcast-is-an-ordinary-scoped-permission-and-the-recipient-chooses-the-channel)'s
*"the recipient chooses the channel"* finally given somewhere to live
([D-213](../decisions/round-25.md#d-213--the-account-chooses-its-own-doors-a-childs-message-mirrors-as-its-own-rows-and-only-e-mail-lands-today)).
**It sits on `account` and not on anything a sender can touch, because the choice is the login owner's and not
a property of the message** — while everything the choice means, what a door is, what a message writes against
one, and what a notification is, belongs to [the messaging module](10-messaging.md), whose
[§5](10-messaging.md#5-doors-the-account-chooses-the-inbox-is-not-one-and-only-e-mail-lands) is the page that
decides it. **Three things follow, and none of them is a column on this table.** The inbox is **not a door and
cannot be turned off**: it is the record that a message exists for you, so there is no `opt_in` for it and no
refusing it. The **address is not here either** — the door opens onto a `person_contact` row of type `email`
carrying a verified address (§6), and an account with the flag on and no such row holds a choice with nothing
behind it, which writes no row for that door and is a fact about the person's contacts rather than a failed
send. And **only one door exists today**: no column is written for a transport this design cannot perform, which
is the same lesson [D-192](../decisions/round-23.md#d-192--proposed_by-loses-import_job-because-a-vocabulary-value-is-a-claim-about-who-can-write)
drew from a vocabulary value that claimed a kind of actor existed — where the next transport's address will live
is [K-15](../open-questions.md#k-15).

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
person's own, carrying a verification and a credential history that belong to an act the survivor never
performed. **The rule is instead, in this order:**

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
Two costs come with it and both are stated rather than absorbed. **A genuinely new person who happens to
match now waits for a human**, so the blocking condition carries an age check shaped like
`field_conflict`'s thirty days below — a number on a listing somebody opens, because **no message type is
configured for a queue that has stalled**: the design has the sending machinery
([10-messaging](10-messaging.md)) and an installation's vocabulary of types is empty until somebody writes it
([10-messaging §2](10-messaging.md#2-message_type--a-vocabulary-that-is-also-a-settings-panel)), so nothing is
written about a waiting claim unless a person configures a type that says so — the reason is configuration now,
and not a rule about verbs
([D-164](../decisions/round-22.md#d-164--nobody-is-told-and-no-page-may-say-otherwise) as narrowed by
[D-214](../decisions/round-25.md#d-214--the-system-sends-and-d-164-is-narrowed-to-the-one-thing-it-was-protecting)). A
stalled identity queue stopped being a data-quality problem the moment it could hold a login, and the
person it is holding has no way to say so except by telephoning someone.
**And the reviewer deciding it is deliberately half-blind** — the office that holds the merge holds no read
over the person record, so it decides from signals and names, which is the correct conservative shape and
also the thing to revisit if reviewers start asking for context they cannot see. **No platform ships that
office**: some organization writes it, aims `person.merge` at `ROLE(x)` and leaves `person.view` out of the
grant, and the conservatism is in the grant it chose rather than in a row the design brought with it
([05d §12](05d-invariants-and-seed.md#12-what-day-one-looks-like)).

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
| `credential_type` | text, required | One of: `password`, `passkey`, `totp`, `oauth`, `staff_link`. Multiple methods per account. `oauth` is **Google**, which vouches for an e-mail address and not for membership — it does not know the organization exists; `staff_link` supports a one-time link issued to a member who cannot self-serve. The list is written in the program and in this row — see below for what adding a method costs |
| `secret_hash` | text, optional | Password/OTP hash. Absent for passkey and oauth |
| `external_ref` | text, optional | OAuth subject id — with Google, the subject behind one e-mail address — or WebAuthn credential id |
| `external_issuer` | text, optional | OAuth issuer. The `(external_issuer, external_ref)` pair is an **external identity**: exactly one account may hold a live one (Rules) |
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
  are still current — **one external identity, one account**. A second account offering a pair a live
  credential already holds is **refused at the save**: with self-service sign-up on a public provider,
  this and §4's one-live-account rule are the same wall seen from either side, and the refusal is the
  enforcement the invariant register had recorded as absent
  ([D-176](../decisions/round-23.md#d-176--google-or-a-password-one-identity-one-account-and-the-invariant-finally-has-a-check),
  [D-089](../decisions/round-07-08.md#d-089--one-live-account-a-colliding-sign-up-files-a-claim-and-creates-nothing)).
  It covers open rows only — an expired credential does not hold its
  external identity back.

**Indexes**

- An account's current credentials — the open half of the period only.
- The `oauth` uniqueness above, which is itself a lookup: given an issuer and a subject id,
  which account is this.

**The issuer is Google, and what that costs is the ordinary sign-up path, not a corner.** Google vouches
for an e-mail address; it does not know the organization exists and cannot vouch for membership, and the
case the constraint above exists for is the commonest one in the building: a parent has one Google account
and three children do not. Before the refusal, an issuer login landing on "whichever credential the index
happened to keep" was a tidy-up problem behind an issuer nobody had ever seen — a national Scout identity
provider whose subject id would have meant *this member*; after it, a second account wearing the parent's
identity is simply refused, and the family's answer is the child's own credential or the guardianship row
([D-176](../decisions/round-23.md#d-176--google-or-a-password-one-identity-one-account-and-the-invariant-finally-has-a-check),
[D-178](../decisions/round-23.md#d-178--a-child-without-a-login-is-reached-through-the-guardianship-row)).

**The list of methods is written in the program and in this document.** The five values of
`credential_type` are behaviour, not a vocabulary: a new method — a magic link, an SMS code — is a
**release** in which the code that authenticates against it and the value naming it ship together, no
table lists the methods, and no screen can offer one that has not been written
([D-177](../decisions/round-23.md#d-177--the-list-of-login-methods-is-written-in-the-program)). This is
the corpus's line for vocabularies read from the other side: the principle is not *anything enumerable is
a row* but *anything the organization may decide is a row*, and nobody has ever changed their mind about
whether the software speaks SMS — where the one-row [`membership_type`](03-membership.md#1-membership_type--one-row-kept-as-a-table)
holds a thing a person could genuinely change their mind about. A row the software cannot honour is a
login screen that breaks on the first click. `staff_link` stays what it says it is: a link a staff member
issues; the day a member may issue themselves one is the day the list grows.

**Why credentials are not columns on `account`.** When a new method ships, nothing must restructure
`account` or migrate every existing password — one row per method, each with its own period and
revocation history, makes the arrival of a magic link a write and not a schema change. Keeping
`secret_hash` off the `account` table also means the common
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
