# Data Model — Identity

`person`, `account`, contact points, identifiers, identity hypotheses, and merges.

Every pattern referenced here is defined in [00-conventions.md](00-conventions.md).

---

## 1. The central claim

```
person   ── what the organization knows about a human. No status. No role. No type.
account  ── how that human logs in. Optional. Zero or more over a lifetime.
```

**There is no `is_member`, `member_type`, `is_child`, `is_adult`, `unit_id`, or `role` on
`person`.** Each of those is either a period in another table or a derived fact. This is
the single most important property of the schema and the one most likely to be undone by
a well-meaning future change.

---

## 2. `person`

**Fields**

| Field | Kind | Notes |
|---|---|---|
| `id` | surrogate id | Internal only |
| `public_id` | external identifier, required | Unique. Generated when the row is created. This is what URLs and exports carry |
| `given_name` | text, required | Names are **also** stored as temporal rows in `person_name` (§3). These two columns are the current, canonical form, denormalised for display and search; history and legal-name variants live in `person_name` |
| `family_name` | text, required | As above |
| `birth_date` | date, optional | Nullable because legacy records frequently lack it. **Never required** — a 1994 roster with no birth date must still import |
| `birth_date_precision` | text, optional | One of: `exact`, `month`, `year`, `unknown`. Because an imported birth date of `1990-01-01` often means "year 1990, month and day unknown". Storing the precision prevents false matches on a guessed day and prevents "happy 1 January birthday" emails |
| `gender` | text, optional | One of: `male`, `female`, `other`, `unknown`. Included because youth organizations typically must report it. Remove if yours does not need it — do not collect what you cannot justify |
| `preferred_name` | text, optional | What the person is actually called. Distinct from `given_name` so that the organization's records stay legally correct while the person is addressed correctly — "Alexandra" recorded, "Lex" displayed |
| `record_origin` | text, required | One of: `self_registered`, `staff_created`, `legacy_import`. Default `self_registered` |
| `data_confidence` | text, required | One of: `high`, `medium`, `low`. Default `high`. `low` for imported rows: it drives whether a merge may absorb this row, and whether the UI warns before displaying it as fact |
| `merged_into_person_id` | reference to person, optional | Tombstone. When set, this row is absorbed and queries must follow the pointer. Never deleted (§8) |
| `merged_at` | timestamp, audit time, optional | |
| `redacted_at` | timestamp, audit time, optional | Set when a GDPR-style erasure was performed. Names and contacts are overwritten and the person's `person_attribute` rows are deleted; the row and its id survive so historical references still resolve ([00-conventions §8](00-conventions.md#8-personal-data-and-erasure)) |
| `notes` | text, optional | Free text about a person, and the only such text that lives outside the attribute vocabulary — see *What is deliberately not on this table* below. May contain anything, including a diagnosis sitting under a column nobody would call medical. **It is logged with its contents, like every other field on this row, and it is deliberately *not* on the redactor's list** — a column named as an exception is the field-name rule [D-083](../decisions/decision-log.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data) removed, and the protection is the guard on the trail ([00-conventions §8 item 7](00-conventions.md#8-personal-data-and-erasure)). Whether the column should exist at all is argued below |
| `created_at` | timestamp, audit time | |
| `created_by` | reference to person, optional | |
| `updated_at` | timestamp, audit time | |
| `updated_by` | reference to person, optional | |
| `import_batch_id` | reference to import batch, optional | Set on imported rows. Its link to `import_batch` can only be made once that table exists |

**Rules**

- There is deliberately **no deceased flag**. The organization does not record whether a
  person has died. A membership simply ends; the reason for the ending lives in the generic
  reason-code fields (`membership.termination_reason_code`, `membership.ended_note`) like any
  other ending, and the organization's own vocabulary for such reasons is theirs to define.
  Do not add `is_deceased` or `deceased_at` back: it is not data the organization keeps.
- `public_id` is unique.
- A person may not be merged into themselves — `merged_into_person_id` may never name this
  same row, **nor any row that resolves to it**. The one-hop case is the degenerate form of
  the cycle banned in §8, not a separate rule beside it.
- `merged_into_person_id` and `merged_at` are set together or both left null. A pointer with
  no date, or a date with no pointer, cannot be explained to anyone.
- A `birth_date_precision` may be recorded without a `birth_date` only when it says
  `unknown`. Every other precision claims something about a date that is not there.

**Indexes**

- Person search by name, with both names compared case-insensitively.
- Persons by `birth_date`, restricted to rows that have one.
- **Persons that have not been merged** — a partial index, because every ordinary listing
  must exclude merged rows and it has to stay cheap.
- **Persons that have not been redacted** — same reason.
- Lookup by `public_id`.

### Notes on specific choices

**`birth_date_precision`.** Without it, a legacy import that only knows the year produces
`1990-01-01`, which then matches every other year-only record born in 1990 on the same
invented day, and sends birthday greetings on 1 January. Cheap column, prevents a whole
class of matching noise.

**`public_id` alongside `id`.** External references use `public_id`. Sequential internal
ids appear in `access_grant.scope_id` and in URLs; exposing them would let anyone enumerate
member records. See [00-conventions.md](00-conventions.md#3-primary-keys).

**`merged_into_person_id` and `redacted_at` are both on `person` rather than in side
tables.** They are read on *every* query (every listing must exclude merged and redacted
rows from ordinary views), so they need to be cheap. They are also the reason the two
partial indexes above exist.

### What is deliberately not on this table

Everything the system knows about a person other than their **name, their gender and their age** is
a descriptive value in `person_attribute`, and this table carries no column for any of it — no
allergy, no medication, no insurance number, no shoe size, no preferred contact language, no
diagnosis ([09-attributes.md](09-attributes.md),
[D-083](../decisions/decision-log.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)).
That is not a gap waiting for the next module. An earlier design did put the medical facts on a shelf
of their own, behind codes of their own, and the answer that produced D-083 refused the shelf: a drug
dosage and a clothing size are the same kind of object — recorded by the organization, wrong in three
years, unenumerable in advance — and a permission that reads a person reads the whole record
whatever the shelf is called ([domain/08-person-data.md](../domain/08-person-data.md)).

**`given_name`/`family_name`/`preferred_name`, `gender` and `birth_date` are the only descriptive
facts that are columns here, and they are the last the model will accept.** The test for keeping one
is not sensitivity — `notes` sits in the field table above and is a worse exposure than most of what
moved out. **The test is whether a rule exists that an open layer physically cannot hold.** *"One
current name per person"*, *"exactly one primary postal contact among the open rows"*, *"a school id
may repeat, a birth number may not"* — each is a constraint over a **known set of columns**, and a
key/value layer has no known set of columns, which is the whole of what it is for. Folding
`person_name`, `person_contact` or `person_identifier` into the attribute layer would have relocated
four working constraints into application code and been called uniformity
([F-10 shape 3](../open-questions.md#f-10--which-invariants-the-orm-cannot-express-and-who-writes-those)).
Identity is closed because it was enumerated years ago and has not changed; description is open
because nobody can enumerate it
([D-085](../decisions/decision-log.md#d-085--the-identity-machinery-stays-structured-the-boundary-is-rules-not-sensitivity)).

**The rule cuts both ways, and review is where it is applied.** A fact with no such rule behind it
does not earn a column here, however reasonable it looks — that is the sentence that keeps
`is_deceased`'s cousins out. And a table already in this document does not lose its columns because
the new layer looks tidier — that is the sentence that keeps a well-meaning unification of "everything
about a person" from quietly turning four enforced rules into four hopes.

**One consequence names itself.** `person.notes` is the last free text about a person kept outside the
vocabulary, and it is the column a reviewer should ask about: a sentence typed there is invisible to
the curation queue, to any report on a code, and to the screen a first aider reads at 23:00, while the
same sentence recorded as a value against a `proposed` code is visible to all three
([09-attributes.md §2](09-attributes.md#2-attribute_definition--the-vocabulary)). Whether the column
should exist at all is open and already argued
([06-audit-and-import.md §6](06-audit-and-import.md#6-open-issues)); what is settled is that it
carries no protection the attribute layer does not carry, and less readability.

### The answer to "who is a member?" is never on this table

To be unambiguous, the two facts:

- **Currently a member** — the person has a `membership` whose `valid_to` is absent and whose
  status is `active`.
- **Was a member on 1998-06-01** — the person has a `membership` whose period contains that
  date: `valid_from` on or before it, and `valid_to` either absent or after it. Its status is
  one of `active`, `completed`, `lapsed`, `terminated`.

Note the second fact includes closed statuses — "was a member in 1998" is true regardless
of how the membership later ended. Getting this wrong is why "years of membership" reports
are usually wrong.

---

## 3. `person_name` — name history

**Fields**

| Field | Kind | Notes |
|---|---|---|
| `id` | surrogate id | |
| `person_id` | reference to person, required | |
| `name_type` | text, required | One of: `legal`, `preferred`, `maiden`, `former`, `alias`, `imported` |
| `given_name` | text, required | |
| `family_name` | text, required | |
| `middle_name` | text, optional | |
| `valid_from` | date, optional | Optional because an imported name often arrives with no start date at all |
| `valid_to` | date, optional | `NULL` = current for this `name_type` |
| `source` | text, optional | `self`, `staff`, `legacy_import` |
| `import_batch_id` | reference to import batch, optional | |

**Rules**

- `valid_to` is either absent, or `valid_from` is absent, or `valid_to` is later than
  `valid_from`.

**Indexes**

- A person's names.
- Fuzzy search across all historical names — both names lowercased, family name first, and
  usable for prefix matching. This is what legacy matching reads.

**Why name history is a table.** Three concrete cases:

1. A member married and changed their family name. The 1998 roster has the maiden name;
   the 2026 registration has the married name. Legacy matching must find the link, and
   the historical record must keep the name it actually had.
2. An imported name has a typo (`Novak` for `Novák`). Correcting it must not destroy the
   imported form, because that is what the paper says and someone will ask.
3. A person goes by a different name than their legal one. Both must be storable, and
   which is used where must be deterministic.

**`person.given_name`/`family_name` are the denormalised current values** and are what the
UI displays. `person_name` is the source of truth for matching and for historical queries.
This is a deliberate denormalization — the alternative is joining on every list view — and
it must be updated in the same transaction whenever the canonical name changes.

*Assumption:* display should use `person.preferred_name ?? person.given_name`. If the
organization requires legal names on official documents, that rule lives in the document
layer, not here.

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
  gate on the same transition and [D-089](../decisions/decision-log.md#d-089--one-live-account-a-colliding-sign-up-files-a-claim-and-creates-nothing)
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
([D-089](../decisions/decision-log.md#d-089--one-live-account-a-colliding-sign-up-files-a-claim-and-creates-nothing)):
someone arrives at the sign-up form through a door the system did not know they had, and their details
strong-match a person who already exists. **The tempting answer was the convenient one** — verify the
e-mail, see that the signals are strong, link the two accounts — and it is
[D-004](../decisions/decision-log.md#d-004--no-automatic-merging-ever) wearing a different coat: a
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
[§8](#8-identity_hypothesis-and-person_merge) possible — resolving two `is_primary` rows is a review
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

---

## 8. `identity_hypothesis` and `person_merge`

**Fields**

| Field | Kind | Notes |
|---|---|---|
| `id` | surrogate id | |
| `person_a_id` | reference to person, required | The lower of the two ids — canonical ordering, so that `(a,b)` and `(b,a)` cannot both exist |
| `person_b_id` | reference to person, required | |
| `confidence` | number between 0 and 1, required | Inclusive of both ends |
| `match_signals` | jsonb, required | A list of signals, each with a name, a weight and whether it matched — `[{signal: 'birth_date_exact', weight: 0.4, matched: true}, {signal: 'name_normalised', weight: 0.3, matched: true}, …]`. Stored so a human reviewer can see **WHY** the matcher proposed this |
| `status` | text, required | One of: `proposed`, `needs_review`, `confirmed`, `rejected`, `superseded`. Default `proposed` |
| `proposed_by` | text, required | One of: `import_job`, `match_job`, `person`, `staff`. `match_job` is the nightly batch matcher, as opposed to a person suggesting a match by hand. (Named `background_match` before background checks were removed from the design; renamed so the two never get confused.) |
| `proposed_by_person_id` | reference to person, optional | Set when a person proposed it |
| `proposed_at` | timestamp, audit time | Default: now |
| `reviewed_by` | reference to person, optional | |
| `reviewed_at` | timestamp, audit time, optional | |
| `review_note` | text, optional | |
| `created_at` | timestamp, audit time | |

**Rules**

- `person_a_id` names a lower person id than `person_b_id`, and the two are never the same
  person.
- A hypothesis cannot be `confirmed` or `rejected` without a `reviewed_at`.
- One live hypothesis per pair: unique over `(person_a_id, person_b_id)` while the status is
  `proposed`, `needs_review` or `confirmed`. A `rejected` or `superseded` hypothesis does not
  block a new one, so the pair can be re-proposed later.

**Indexes**

- The review queue: status, then `confidence` highest first, restricted to the rows still
  waiting — `proposed` and `needs_review`.

**`person_merge`** — the record that one person row was absorbed into another.

**Fields**

| Field | Kind | Notes |
|---|---|---|
| `id` | surrogate id | |
| `surviving_person_id` | reference to person, required | |
| `merged_person_id` | reference to person, required | The absorbed row. It keeps its id; `person.merged_into_person_id` points here |
| `hypothesis_id` | reference to identity hypothesis, optional | The hypothesis this merge came from, when one did |
| `merged_at` | timestamp, audit time | Default: now |
| `merged_by` | reference to person, required | |
| `reason` | text, optional | |
| `reversed_at` | timestamp, audit time, optional | |
| `reversed_by` | reference to person, optional | |
| `reversal_note` | text, optional | |
| `created_at` | timestamp, audit time | |

**Rules**

- A person may not be merged into themselves: `surviving_person_id` and `merged_person_id`
  are never the same person.
- **A merge is refused when the chosen survivor resolves — by walking the chain — to the person being
  absorbed.** That includes the one-hop case just stated and the case that actually happens: absorbing B
  into A when A has already been absorbed into B.
  [D-087](../decisions/decision-log.md#d-087--merge-chains-stay-because-reversing-a-merge-is-a-supported-operation)
  puts this check on the **merge** and not on the read, and the placement is the substance of the rule: a
  cycle refused on the way in cannot be reached, whereas a step limit on `resolve_person()` achieves
  nothing except deciding *which of two wrong answers to return* — the tombstone, or wherever the walk
  happened to stop. There is no schema object that spans two rows of a walk, so this is a rule about an
  operation; the cycle check in §10 is a canary for it having leaked, not the guard.

**Indexes**

- Merges by surviving person, and merges by merged person — both directions get asked.
- Merges by merged person that have not been reversed — the "who is this person now" query.

**The canonical ordering (`person_a_id` before `person_b_id`) is not cosmetic.** Without it
the matcher can create both `(100, 847)` and `(847, 100)`, and a reviewer will confirm one
while the other sits in the queue forever — or worse, confirm both. The ordering rule plus
the partial unique index makes the pair identity unambiguous.

**`match_signals` as JSONB** rather than columns, because the signal set will evolve as the
matcher improves, and because these are write-once-read-for-review, never queried
analytically.

**`person_merge` is append-only** — `reversed_at` is set, rows are never deleted. An
unmerge does not remove the merge record; it records that it was undone, so the history of
the mistake is visible. See
[../domain/03-identity-and-legacy.md](../domain/03-identity-and-legacy.md#6-reversing-a-merge).

**Reversing a merge is a required operation, not an accommodation.** Those three columns exist because
someone asked for the capability, and
[D-087](../decisions/decision-log.md#d-087--merge-chains-stay-because-reversing-a-merge-is-a-supported-operation)
is where it was asked for; §9 explains that this is the reason chains were kept rather than the other way
round. Two consequences sit under it, and both are easy to lose later.

- **Reversal needs no permission of its own.** Unmerging is the same act as merging — an identity
  correction made by a named human — so it is `person.merge`, which `identity_reviewer` already holds.
  A separate code would grade undoing a mistake as safer than making one, which is precisely backwards:
  the mistake is the thing that needed the guard.
- **A merge can be undone; the merged period cannot.** The reversal procedure lifts the tombstone and
  returns the rows created *before* the merge, but the rows created *inside* the window are flagged for a
  human rather than guessed at — and every `access_grant` from that window is flagged, not redistributed,
  because the authority exercised in there really was exercised by somebody the record can no longer
  separate. **That asymmetry is the honest core of the feature: the row is restorable, the interval is
  not.** Anyone who reads `reversed_at` as "as if it never happened" is reading the wrong column for
  that claim, which is why the reversal record is kept rather than deleted.

### Merge conflicts

**`field_conflict`** — one field the merge could not decide.

**Fields**

| Field | Kind | Notes |
|---|---|---|
| `id` | surrogate id | |
| `merge_id` | reference to person merge, required | |
| `entity_table` | text, required | `person`, `person_contact`, `membership`, … |
| `entity_id` | surrogate id, required | The row in `entity_table`. No reference — with the table named per row it would point at any table in the schema |
| `field_name` | text, required | |
| `surviving_value` | text, optional | |
| `merged_value` | text, optional | |
| `resolution` | text, optional | One of: `kept_surviving`, `took_merged`, `manual`, `unresolved` |
| `resolved_value` | text, optional | |
| `resolved_by` | reference to person, optional | |
| `resolved_at` | timestamp, audit time, optional | |
| `created_at` | timestamp, audit time | |

**Indexes**

- A merge's conflicts by resolution.
- A merge's conflicts that are still `unresolved` — the reportable set.

Every field the merge could not resolve automatically lands here as `unresolved`. **A
merge with unresolved conflicts must be visible in an operational report** — otherwise
these rows accumulate silently and the data is quietly wrong.

Conflict cases worth naming, because each needs a human decision and none has a safe rule:

| Case | Why it cannot be automatic |
|------|---------------------------|
| Two `is_primary` emails of the same purpose | Which one does the person actually use? |
| Two different `birth_date` values | One is a typo; guessing produces a wrong legal record. |
| Two overlapping memberships | May be legitimate, or may mean the merge is *wrong*. |
| Two different current names | One may be a maiden name, or they may be different people. |
| Two accounts, both active | Which one is in use? |

---

## 9. Views

Convenience views that encode the "always exclude merged and redacted" and "point in
time" rules, so that application code cannot forget them.

**`v_person`** — the person rows most queries actually want: a person who is neither merged
away nor redacted. **Both exclusions, not one.** They are different reasons and they must not be
collapsed: a merged row is a *duplicate* that points at the real answer, while a redacted row is a
*person who was erased*, whose names and contacts no longer exist. Neither belongs in a list of
people, and a listing that shows one and hides the other is worse than either, because it teaches
the reader that the redacted child is a data-entry error.

> **This is a correction, not a restatement.** The view as this document first carried it
> excluded merged rows only, while §1 and §2 both said every listing must exclude redacted ones
> too, and §9's own opening sentence claimed the views encoded both. Three statements, one of them
> the code. The code lost. It is fixed here rather than noted as a discrepancy, because with the
> SQL gone (§1 of D-072) there is nothing left to disagree with the prose — **the prose is now the
> only place the rule lives, so it has to be right.**

**What is deliberately *not* excluded anywhere: the row itself.** A redacted person is still a
row with a still-working id, so historical references keep resolving
([§2](#2-person)'s `redacted_at`). Anything that must reach a merged or redacted
row — audit, as-of reconstruction, `resolve_person` — queries `person` directly and says so.
`v_person` is the view for "people", and people is not what an audit trail is asking for.

**`resolve_person(id)`** — turns a possibly-merged id into the survivor. These steps run in
this order, and the order is the rule:

1. Begin at the person row carrying the given id.
2. If that row has no `merged_into_person_id`, stop; this id is the answer.
3. Otherwise move to the row its `merged_into_person_id` names and repeat from step 2.

**`v_person_display`** — one row per person `v_person` admits, carrying `id`, `public_id`, a
display given name (`preferred_name` where present, `given_name` otherwise), `family_name`,
a display name formed by putting the two together with a space, `birth_date`,
`birth_date_precision` and `redacted_at`.

**What `v_person_display` does not carry, and why that is a rule rather than an omission.** It is a
*display* row — the columns needed to name a person in a list — and it carries **no descriptive
values**. It cannot: a view is a fixed list of columns and the attribute layer is the part of a
person with no fixed list, which is §2's test arriving from the other side. Naming the boundary
matters because the failure mode is silent. **Anything asked about a *person*, rather than about what
they are called, reads `person` and `person_attribute` together under the one `person.view` that
reaches both** ([09-attributes.md §4](09-attributes.md#4-who-may-read-and-who-may-write)) — the
allergy list a first aider asks for, the record a guardian opens, the form a leader fills in. A screen
built on `v_person_display` alone answers those questions with a name and a birth date, shows no
empty field where an allergy should be, and looks entirely healthy while doing it
([domain/08-person-data.md §3](../domain/08-person-data.md#3-who-needs-to-know-what)). The view stays
narrow for the reason it exists — every picker and roster in the system reads it and none of them
needs the record — and the obligation sits on the caller: **do not answer a question about a person
out of a view that only knows how to print one.**

`resolve_person` follows every hop because merges chain: A absorbed into B, later B absorbed
into C. A single-level pointer lookup would return B, whose row is itself tombstoned.
**Every place that accepts a person id from outside must call this.** Getting it wrong
means a historical record links to a tombstone and the UI shows a blank name — or the
wrong one.

**Chains are a decision, not an assumption, and this used to be an assumption.** The sentence this
replaces read *"Assumption: merge chains are allowed rather than flattened at merge time"*, and it argued
for chains on the ground that flattening makes unmerge nearly impossible — a defence resting on a
capability nobody had asked for. Someone has since asked for it, as a requirement (§8), and
[D-087](../decisions/decision-log.md#d-087--merge-chains-stay-because-reversing-a-merge-is-a-supported-operation)
is that request: with chains kept a reversal is a replay, with flattening it is a rebuild. So the
direction of the argument is reversed and the trade is now asymmetric in a way it was not before —
**flattening is closed off, not merely slower**, and "flattening is faster" no longer buys anything except
the death of a feature somebody named.

**Two rules keep a permanent chain safe, and neither existed while this was an assumption.**

- **A cycle cannot be created, and the place it cannot be created is the merge, not the read** (§8's
  rule). A read-side hop limit is not a weaker version of this guard; it is a different and worse thing,
  because it always returns an answer.
- **Chain length is a signal, not an error.** Resolution has **no hop limit** — a bound would silently
  hand back a tombstoned id, which is the single failure this function exists to prevent, and the
  argument for following every hop above is the argument for having no bound. Instead a chain longer
  than **three hops is reported**, because four merges in a row on one line of people does not mean the
  data is odd: it means the matcher is producing duplicates faster than a human can settle them, which is
  a statement about the queue and not about the row. Check 3 in §10, which used to treat an absorbed
  survivor as a breach, is corrected for exactly this: **a survivor that has itself been absorbed is what
  a chain looks like when it works.** Only the length means anything.

**And the rule immediately above now has a check under it.** "Every place that accepts a person id from
outside must call this" is a rule about application code, which application code can forget, and
[D-072](../decisions/decision-log.md#d-072--the-documentation-carries-no-sql-the-schema-is-the-orms-job)
removed the database-level ways of catching the forgetting. The net is check 4 in §10 — live rows that
reference a tombstoned person — which is the only form of this failure that is still visible after the
fact, and the reason §9's prose is no longer the only thing standing between a foreign key and a
tombstone.

---

## 10. Integrity checks

Checks that should run nightly and alert. These encode invariants that no per-column rule
above can express.

**Invariants to verify**

- **A person with more than one live account.** Count `account` rows per person whose status
  is `pending_verification`, `active` or `suspended`; anything above one is a breach of the
  rule in §4, and the point of the check is to confirm that rule really does exclude the
  pending-plus-active combination.
- **A tombstoned person with no merge record.** Count persons whose merge pointer is set but
  who do not appear as the merged person of any un-reversed `person_merge` row; non-zero
  means a pointer was written without the record that explains it, which is the case the
  append-only table in §8 exists to make impossible.
- **A merge chain longer than three hops.** Walk each tombstone's pointer and count the hops to the
  survivor; report the chains over three. **This is a report about a queue, not a finding about a row.**
  It replaces a check that counted `person_merge` rows whose `surviving_person_id` has its own merge
  pointer set and called a non-zero result a breach — with [D-087](../decisions/decision-log.md#d-087--merge-chains-stay-because-reversing-a-merge-is-a-supported-operation)
  deciding that chains stay, **that count is the normal shape of the data and its expected value is not
  zero**; a person absorbed twice has a survivor who was absorbed, by construction. What carries
  information is the *depth*: four merges in a row on one line of people means the matcher is producing
  duplicates faster than a human can settle them. It is read alongside the review queue's age, never on
  its own, and it is not alertable — there is nothing wrong to fix on the row, and an alert that can only
  be answered by "work faster" trains people to ignore alerts.
- **A live row that references a tombstoned person.** Count rows in any table that names a person which
  point at a person whose merge pointer is set, where the referring row is itself live. **This is the
  only net under §9's rule that every entry point calls `resolve_person()`, and it exists because D-072
  took the database-level ones away.** Getting that call wrong is invisible at the moment it happens — a
  blank name in a list, at worst the wrong name — and permanent afterwards, because the row is written and
  referenced by whatever came after it. **This one alerts rather than logs**: the gap is not reconstructable
  later, and unlike a missing audit entry it misattributes a person rather than merely forgetting them.
- **A cycle in the merge graph.** Walk the pointers and look for a row reachable from itself. There should
  never be a single row here: §8 refuses a merge whose chosen survivor resolves to the person being
  absorbed, so **a non-zero count is not untidy data, it is that rule having failed**, and it is the one
  merge finding that should stop work rather than fill a report — `resolve_person()` does not terminate on
  a cycle, and every screen and every resolver hop that touches the affected people goes with it.
- **An account held below `active` by an unresolved hypothesis for more than 30 days.** Count accounts
  whose status is not `active` or `closed`, whose person is named by a hypothesis still in `proposed` or
  `needs_review`, where that hypothesis is older than 30 days — the same shape as the conflict-age check
  below, for the same reason. **It alerts rather than logs, and the reason is worth keeping in the check's
  own text: a stalled identity queue stopped being a data-quality problem the day it acquired the power to
  hold a login.** Behind each row is a specific person who cannot sign up — often to a camp whose form
  closes this week — and no channel by which to tell anyone except a telephone call.
- **Unresolved merge conflicts older than 30 days.** Count `field_conflict` rows resolved to
  `unresolved` and created more than 30 days ago; non-zero means the review queue is being
  ignored and the data is quietly wrong.
- **Redacted people still referenced by a live account.** Count `account` rows that are not
  closed and belong to a person with `redacted_at` set; non-zero means an erasure left a
  working login behind.
- **Imported people with no participation.** Count people whose `record_origin` is
  `legacy_import` and who have no `unit_participation` row at all; non-zero probably means a
  partially applied batch. **This check is the reverse of the one it replaced, and the reversal is
  [D-090](../decisions/decision-log.md#d-090--the-legacy-corpus-is-thousands-of-roster-rows-with-numbers-and-no-money)
  and not a change of mind about imports.** It counted imported people with no `membership`, which after
  "a roster makes a participation and nothing else" is the ordinary condition of every imported row — so
  the old version would have reported the entire legacy corpus as a failed batch, which is precisely how a
  check stops being read. A roster that *did* create memberships is a different finding and lives in
  [06-audit-and-import.md §5](06-audit-and-import.md#5-integrity-checks).
- **A redacted person with descriptive values still attached.** Stated where the rows are, as check 6
  of [09-attributes.md §8](09-attributes.md#8-integrity-checks) — attribute rows belonging to a
  redacted person, and attribute values still present in `audit_log`. It is named here because the
  redaction checks above are the same erasure guarantee read from the identity side, and a half-finished
  erasure does not announce which table it stopped in. Of everything on either list, that is the one
  that should alert rather than log.

---

## 11. Open issues

- Erasure policy specifics: what must be redacted vs. retained. **Smaller than it used to be, and not
  gone.** The retention *shape* is decided — the trail's payloads expire on a window, the accounting
  skeleton has no clock at all
  ([D-088](../decisions/decision-log.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short))
  — so what is left is the question a decision log cannot settle, namely whether indefinite retention of
  *named* `membership` and fee rows has a basis. See
  [00-conventions.md](00-conventions.md#8-personal-data-and-erasure) and
  [06-audit-and-import.md §6](06-audit-and-import.md#6-open-issues).
- Whether `person.gender` is needed at all; if so, what value set.
- Whether the organization has (or will have) a national SSO identity provider — this
  determines how much of `account_credential` is actually used.

**Resolved, kept visible so that nobody reopens them by reading the tables alone.** Whether merge chains
are allowed or flattened at merge time (§9): **chains stay**, because reversing a merge is a required
operation rather than a convenience, and the two rules a permanent chain needs are now written where they
are obeyed — the cycle refusal in §8, the length report in §10
([D-087](../decisions/decision-log.md#d-087--merge-chains-stay-because-reversing-a-merge-is-a-supported-operation),
[B-2](../open-questions.md#b-2--closed--merge-chains-stay-because-unmerge-is-required)). And whether a
person may hold two live accounts simultaneously: **no**, enforced by the partial unique index in §4 —
with the case that made the question hard answered by a gate rather than by an exception, so that a
colliding sign-up files a claim and activates nothing instead of becoming a second account or being
silently linked
([D-089](../decisions/decision-log.md#d-089--one-live-account-a-colliding-sign-up-files-a-claim-and-creates-nothing),
[B-4](../open-questions.md#b-4--closed--one-live-account-a-colliding-sign-up-files-a-claim)).

All tracked in [../open-questions.md](../open-questions.md).
