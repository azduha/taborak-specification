# Data Model — Identity: the central claim, `person`, and name history

`person` — what the organization knows about a human, on which there is no status, no role and no
type — the columns deliberately left off it, and the name history in `person_name`. How that human
signs in and is reached is [01a](01a-accounts-and-contacts.md); how two rows become one person is
[01b](01b-merges-views-and-checks.md).

Every pattern referenced here is defined in [00-conventions.md](00-conventions.md).

**Section numbers are shared across the three parts** and never renumbered, because other pages cite
them by number and their anchors are built from them:
[01-identity.md](01-identity.md) holds §1–§3 (the central claim, `person`, `person_name`),
[01a](01a-accounts-and-contacts.md) §4–§7 (`account`, `account_credential`, `person_contact`,
`person_identifier`), and [01b](01b-merges-views-and-checks.md) §8–§11 (`identity_hypothesis`,
`person_merge`, the views, the integrity checks, open issues).

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
| `notes` | text, optional | Free text about a person, and the only such text that lives outside the attribute vocabulary — see *What is deliberately not on this table* below. May contain anything, including a diagnosis sitting under a column nobody would call medical. **It is logged with its contents, like every other field on this row, and it is deliberately *not* on the redactor's list** — a column named as an exception is the field-name rule [D-083](../decisions/round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data) removed, and the protection is the guard on the trail ([00-conventions §8 item 7](00-conventions.md#8-personal-data-and-erasure)). Whether the column should exist at all is argued below |
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
[D-083](../decisions/round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)).
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
([D-085](../decisions/round-07-08.md#d-085--the-identity-machinery-stays-structured-the-boundary-is-rules-not-sensitivity)).

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
([06-audit-and-import.md §6](06b-redaction-and-checks.md#6-open-issues)); what is settled is that it
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
