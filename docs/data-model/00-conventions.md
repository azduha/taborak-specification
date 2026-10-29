# Data Model Conventions

Read this before reading any other document in this folder. Every entity in this system is
described using the patterns here, and the patterns are load-bearing — deviating from them in
one table creates bugs that only appear across decades of history.

**What this file is, since [D-072](../decisions/round-06.md#d-072--the-documentation-carries-no-sql-the-schema-is-the-orms-job).**
It used to be the preamble to a set of `CREATE TABLE` statements. Those statements are gone —
the schema is the ORM's job — and what remains is the part that was never about SQL: the rules
about time, identity, deletion and rank that a generated schema will happily violate without
noticing. **Nothing here is a suggestion.** A convention in this folder is a bug that has
already happened somewhere, written down.

---

## 1. Target platform

*Assumption:* **PostgreSQL 14+**, reached through an ORM.

The design relies on four things from the platform, and it is worth being exact about which
four, because an ORM hides the list:

- **Range types with an overlap operator** (`daterange`, `tstzrange`, `&&`) — for the
  "no overlapping periods" invariants that the whole temporal model depends on.
- **Exclusion constraints** (`EXCLUDE USING gist`, with `btree_gist`) — the only way to state
  "no two open rows may overlap" that survives every possible writer.
- **A structured column type** (`jsonb`) — for match signals, audit diffs, event answers and
  other semi-structured payloads whose shape is per-row by design.
- **Recursive queries** — for the unit hierarchy. Note that this one is *only* for structure:
  no authorization path may walk the hierarchy
  ([../domain/06-authorization-model.md](../domain/06-authorization-model.md#2-scopes--the-unit-and-the-item)).

Native enum types are avoided — see §5.

**What the ORM changes, and what it must not be allowed to change: see §6a. Read it before
generating the first migration.** The short version is that most ORMs cannot emit an exclusion
constraint, and the fallback they offer — validation in the model layer — is precisely the
mechanism this document has always warned against. Hand-written migrations for those tables are
not a deviation from "use the ORM", they are the condition on which it is safe.

If the target turns out not to be PostgreSQL, exclusion constraints become triggers plus
periodic consistency reports. **That is a materially weaker guarantee and it must be recorded as
an accepted decision, not discovered as an outage.** Tracked in
[../open-questions.md](../open-questions.md).

---

## 2. Naming

| Object | Convention | Example |
|--------|-----------|---------|
| Table | `snake_case`, **singular** | `person`, `membership_request` |
| Column | `snake_case` | `valid_from`, `person_id` |
| Primary key | `id` | always the same name, so joins read uniformly |
| Foreign key | `<referenced_table_singular>_id` | `person_id` → `person.id` |
| Boolean | `is_` / `has_` / `requires_` prefix | `is_system`, `binds_to_item` |
| Timestamp | `<verb>_at` | `created_at`, `verified_at` |
| Date/period | `valid_from` / `valid_to` | never `start_date`/`end_date` |
| Junction table | `<a>_<b>` in alphabetical order | `guardianship_permission`, not `permission_guardianship`. *(The example here was `audience_member` for ten rounds, which was a better illustration because its two halves are further apart alphabetically; the table is deleted by [D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other), and a naming convention should not be taught with a table that does not exist.)* |
| Lookup table | singular of the vocabulary it *is* | `selector_type`, `reason_code` |
| Index | names the table and what it answers | "the open rows for one person", not `idx_3` |

Singular table names are not aesthetic. `membership` reads correctly in a sentence about one
row, which is how most of this system's rules are written; plural table names produce code that
says `memberships[0].membership_id` and reviewers stop reading it.

There is no `deleted_at` column. Deletion is handled by temporal closure and tombstones, never
by a soft-delete flag — see §4.

Naming survives the move to an ORM; it is the one section of this file that the ORM will follow
without being told, provided someone wrote these rules into the ORM's own conventions.

---

## 3. Primary keys

**Every table has a surrogate `id`.** No natural keys as primary keys, ever.

Rationale specific to this project: natural keys here are things like names, old member numbers,
and email addresses — all of which **change**, **repeat**, and **get corrected**. A name is not
unique (and was less so in 1994). An email address is reused by providers and reassigned between
people. A legacy member number may be absent, or duplicated across two source systems. A natural
key that turns out to be wrong is a key that must be rewritten, and a rewritten primary key
rewrites every historical reference beside it.

The surrogate key is a **64-bit** integer, not 32-bit, because this system accumulates rows for
decades and because `access_grant.scope_id` must never run out of room or recycle.

**Exception, and it is a security requirement:** `person.public_id` — a separate `UUID` column,
used for every external exposure.

Rationale: `access_grant.scope_id` is a bare bigint with no foreign key, and ids appear in URLs
and exports. Sequential ids leak record counts and — more seriously — let someone enumerate
`/person/1001`, `/person/1002` and discover members. **Expose `public_id` in all external
interfaces; keep `id` internal.** An ORM that marshals entities by primary key has, by default,
published the internal counter.

---

## 4. Deletion policy

**Nothing is hard-deleted.** There is no `deleted_at` and no delete for business data. **Two
exceptions are named below** — a staging truncate, and one delete that erasure has to make — and both
are narrow enough to prove the rule rather than erode it.

| Situation | Mechanism |
|-----------|-----------|
| A period ended | Set `valid_to` |
| A person left the organization | Close their membership; the person row remains |
| A grant revoked | Set `access_grant.valid_to`; keep the row |
| Two people merged | Tombstone: set `merged_into_person_id`; row remains |
| A group ended | Set `person_group.valid_to`; its member rows remain |
| GDPR-style erasure requested | **Redact** field values; do not delete rows — see §8. **One table is deleted rather than redacted; the exception below names it and why** |

This is not nostalgia. Historical foreign keys — "who attended this camp in 2003" — must resolve
forever. A hard delete breaks the audit trail and, in a youth organization, the safeguarding
record.

**The first exception:** staging tables (`staging_import*`) may be truncated after a batch is
applied, subject to the project's retention policy.

**The second exception is not convenience and it should be read as a decision, not an oversight.**
Redacting a person **deletes** their `person_attribute` rows ([§8 item
2](#8-personal-data-and-erasure)). Everywhere else in this file, erasure means overwriting a value
and keeping the row, because the row is what old references point at. A descriptive value is the one
thing that has no row worth keeping: **the row *is* the value** — there is no period that closed, no
assignment that ended, no id another table cites. Blanking the value instead would leave the shape of
a person's erased life behind as a permanent record of it: which codes they had, how many of each,
and the dates they were first recorded. Retiring the *code* is not the answer either, and
[D-084](../decisions/round-07-08.md#d-084--descriptive-data-is-organization-defined-at-runtime) is
explicit that retirement must never destroy values — retirement is an act about the vocabulary,
erasure is an act about the person, and the two point in opposite directions on purpose
([09-attributes.md §6](09-attributes.md#6-erasure-retirement-and-the-audit-payload)).
**This exception is safe only while nothing references an attribute row, and nothing does today.**
Should a future table ever point at one — an event question bound to a stored value is the obvious
candidate, and it is open as AT-1 — that table must be designed around this rule rather than
discovering it, because at that point the delete stops being invisible and becomes the referential
integrity problem §9 exists to prevent.

**This rule is now carried entirely by discipline, and that is worth saying out loud.** A
`ON DELETE RESTRICT` default, a revoke of `DELETE` from the application role, an ORM whose delete
method nobody has ever called — those were enforcement. What remains is an instruction to whoever
configures the ORM: **deleting business rows is not a feature this system has.** Do not wire a
"remove" button to an ORM delete call. The audit log will not save you, because it records
changes to rows that still exist.

---

## 5. Enumerations

**Status vocabularies are text with an allowed-value list, not the database's native enum type.**

Why, given that native enums are more compact:

- Adding a value to a native enum is easy; **removing or reordering** one is painful, and over a
  40-year lifespan a status vocabulary *will* be revised.
- Native enum ordering is baked in, and the order of states here is meaningful — and it is *not*
  the order the type would infer (see below).
- An allowed-value list is visible in schema introspection and in every migration tool, which
  makes review and diffing straightforward.

**The rule, in the words D-072 left behind when it took the `CREATE TABLE` and `CHECK` syntax out**: the
vocabulary lives with the entity, the values are closed, and the vocabulary is reviewable without reading
application code.

### Critical rule: status strings are ordered, and the order is not alphabetical

Several status columns have a **meaningful progression**, and code must compare by **rank**, never by
string. Read this as a rule about the next ordered column you add: the vocabulary it was written for —
`revoked`, `view`, `contribute`, `manage`, `admin`, ranked inside the strings — is gone, because
[D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)
made a grant name one permission code whose effect is `allow` or `deny`. **The mistake generalizes and the
vocabulary did not.** Comparing strings ranked `admin` **below** `contribute` — full control including
granting access, under read and add — with no error, no failed test and no log line
([D-012](../decisions/round-01a.md#d-012--status-strings-compare-by-rank-never-lexicographically)).

**And the survivor is the dangerous shape, not the safe one.** One ordered vocabulary is left: a
guardian's right over a child is `none`, `view`, or `write`
([D-074](../decisions/round-06.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular)).
Those three words happen to sort alphabetically in exactly the intended order — `none` < `view` < `write` —
so a string comparison here **passes every test you can write today**, and breaks silently the first time
somebody adds a fourth value in the middle of the scale. The old bug at least announced itself on the
first comparison; this one is a trap set for whoever extends the list. So:

- **Never compare the right to itself as a string.** Ask whether the permission being checked is a `read`
  or a `write` (`permission.right_kind`, D-099) and whether the guardian's right covers that kind.
  The comparison is against a column on the permission, not between two words.
- **One comparison, one column.** There is no master scale that a guardian's right is a slice of, and
  adding a second way to rank rights is how a guardian ends up able to do *more* than the adult who holds
  the grant.

When adding any new ordered vocabulary, ask the same two questions this section has always asked: is it
data with a stored rank, or is it this rule wearing a name — and if it is data, does a string comparison
of it happen to look correct?

---

## 6. The temporal pattern

The pattern behind every period in this system.

```
entity
  id
  the thing the period is about        e.g. person_id
  valid_from    DATE        NOT NULL
  valid_to      DATE        NULL       -- NULL = still true
  created_at    TIMESTAMPTZ NOT NULL
```

### The four rules

1. **`valid_to IS NULL` means "still true".** Not a far-future sentinel date. A sentinel like
   `'9999-12-31'` looks convenient and breaks every "is open" check, every range query, and every
   index on open rows. Do not use one.
2. **Periods are half-open `[valid_from, valid_to)`.** A membership ending 2010-06-30 and another
   starting 2010-06-30 **do not overlap**. Closed intervals make adjacent periods collide, and
   you will spend a day debugging it. This rule is invisible in a schema and cannot be inferred
   from column names; it must be written in whatever the ORM uses to express such a thing, and
   tested.
3. **Overlap is prevented below the application, not inside it.** An import script, a manual data
   fix, a future API, and a bulk edit all bypass model-layer validation. The invariant must hold
   for writers that were never written. → §6a.
4. **`created_at` is audit time, not world time.** It is distinct from `valid_from` — a membership
   backdated to 1990 during a 2026 import has `valid_from = 1990-09-01` and `created_at = 2026-…`.
   Never conflate them, and never derive one from the other. A system that sets `valid_from` from
   the clock cannot import its own history.

### Why days, not timestamps

`DATE` granularity is correct for most periods here: memberships, guardianships, unit assignments,
fees and exposures start and end on days. Timestamps invite timezone-dependent boundary bugs on
questions like "was this person a member on 1 June?".

Where sub-day precision genuinely matters — session validity, a delegation in force during one
meeting — the same pattern uses timestamps. Both patterns exist in this system; **each entity
states which one it uses**, because a comparison between the two is where the boundary bugs live.

### Indexing the pattern

Two access paths carry the load and both must exist when the schema is generated:

- **One entity's periods, newest first** — the history view.
- **The open periods for one entity** — restricted to rows with no `valid_to`. **This is the
  index that matters.** "Currently active" is the overwhelmingly common question, it stays small
  because open rows are a small fraction of history, and it is the one an ORM will not create on
  its own, because it is not an index on a column combination the model declares — it is an index
  with a condition. If your migrations do not contain a filtered index, nobody thought about this.

---

## 6a. Who enforces an invariant now

**This section exists because the constraints live in migrations now, which moved a responsibility — and a
moved responsibility that nobody names is a responsibility nobody holds.**

Every data-model document in this folder states its rules as prose: "no two open rows may
overlap", "at most one primary contact", "a revoked grant must name who revoked it". Prose does
not reject a row. Three layers could do it, and they are not equivalent:

| Layer | Survives an import? | Survives a manual fix? | Survives a second client? |
|---|---|---|---|
| Model-layer validation in the ORM | **No** | **No** | **No** |
| Migration-level database constraint | Yes | Yes | Yes |
| Nightly consistency report | Yes, eventually | Yes, eventually | Yes, eventually |

**The rule for this system, stated once and applied everywhere: an invariant that is a
correctness property of the data belongs in the database, emitted by a migration, even when the
ORM cannot generate it and the migration must be written by hand.** Model-layer validation is a
*usability* feature — it produces a good error message before a round trip — and it is not an
invariant. The nightly report is a safety net for the invariants that were never expressible as a
constraint at all, and each document's "Invariants to verify" section is exactly that list.

Three consequences that are easy to get wrong:

1. **The overlap invariants need hand-written migrations on PostgreSQL.** Most ORMs cannot emit
   an exclusion constraint over a range built from two columns. Writing those twenty-odd lines
   once, per temporal table, is cheaper than the alternative — which is duplicate open rows
   discovered in 2031 by someone who cannot tell which one was ever real.
2. **Uniqueness that depends on a condition needs a partial unique index.** "One open request per
   person and type", "one primary contact per child among open rows", "one live exposure per unit
   and assignment" are all this shape. A unique constraint over the *un*conditioned columns is
   not the same rule and is usually wrong in the direction of too strict — it forbids the second
   closed row, which history requires.
3. **Uniqueness decided by data cannot live in an index at all.** `identifier_scheme.is_unique`
   says per scheme whether a value may repeat
   ([01a-accounts-and-contacts.md §7](01a-accounts-and-contacts.md#7-person_identifier)); no index can consult a row of a
   different table. This one is genuinely application-level plus a report, and it is documented as
   such rather than being pretended away. **The earlier version of that document had the opposite
   bug — an index that applied to every scheme, ignoring the flag and making `school_id`
   unrepeatable in fact.**

**And the honest cost, stated in D-072's own terms: some rules now have no enforcement anywhere
automatic can reach.** They are written as invariants to verify and they will catch drift only if
someone runs them. A prohibition nobody runs is a convention, not a guard.

---

## 7. Standard columns

Every business table carries:

| Column | Kind | Purpose |
|--------|------|---------|
| `id` | 64-bit surrogate key | Set by the database, never by the caller |
| `created_at` | timestamp, required | Audit time of insert |
| `created_by` | person, optional | Who inserted. Absent for the writers that have no row of their own — the sweeps, payload reduction, migrations ([F-25](../open-questions.md#f-25)). An import batch is not one of them: `import_batch.created_by` is **required** there ([06a §3](06a-import.md#3-import-pipeline)), so the page that carries imports already names a person. A row an integration wrote is not one of them either: the audit trail names the **key** there, and no person is inferred from it ([D-121](../decisions/round-16.md#d-121--a-key-never-carries-a-persons-authority)). |
| `updated_at` | timestamp, optional | Audit time of last change |
| `updated_by` | person, optional | Who last changed it |
| `import_batch_id` | import batch, optional | Set on imported rows — the only way to undo a bad import |

Temporal entities additionally carry `valid_from` / `valid_to`.

Entities that record a *decision about a person* (terminations, rejections, rejections of identity
hypotheses) additionally carry a reason:

| Column | Kind |
|--------|------|
| `<verb>_reason_code` | reference to `reason_code` |
| `<verb>_reason_note` | free text, for the human explanation |

**Reason codes are a lookup table, not free text.** "Why was this membership terminated?" must be
reportable and comparable across years. Free text is not. The note exists so the code does not
have to carry the nuance, and a decision with a code and no note is fine while the reverse is not.

`updated_at` and `updated_by` were maintained by a database trigger. **With the schema generated,
nothing maintains them unless someone says so** — and an ORM that sets them only on the paths the
application happens to take gives you an audit trail that is silently incomplete. Either
maintain them at the database level or accept that `updated_at` means "last changed through the
app". Do not leave it undecided; an audit column nobody thinks about is worse than no audit
column, because people rely on it.

**`api_key.created_by` is required, and it is the one column of this shape in the authorization module
that is never blank.** Installing a permanent outside authority is the most sensitive write that module
offers, and a key nobody is answerable for is exactly what this file's posture refuses. The line above
about jobs does not reach it, because no job installs a key: a person installs a key, and a key never
installs one — `api_key.create` is among the codes a key may never be granted
([05e-keys-and-callers.md §15](05e-keys-and-callers.md),
[D-122](../decisions/round-16.md#d-122--what-a-key-owes-the-catalog-four-codes-at-the-unit-and-the-fourth-owed-thing-declined)).
Required is not inherited: the column says who performed the install and nothing else, and a key outlives
that person with its authority untouched ([D-120](../decisions/round-16.md#d-120--a-key-outlives-whoever-created-it-and-the-report-is-the-control)).

---

## 8. Personal data and erasure

This system holds data about **children**, which raises the stakes on every decision here.

Requirements the design must satisfy:

1. **A deletion request must not destroy the audit trail.** Implement as **redaction**: set
   `person.redacted_at`, overwrite names and contact points with a redaction marker, and keep the
   row and its ids so historical references still resolve. The person is no longer identifiable;
   the record that *someone* was in Troop 12 in 2003 survives.
2. **Redaction must cascade.** It reaches contact points, identifiers, and free-text notes that may
   contain personal data — and it **deletes every `person_attribute` row belonging to the person**
   ([09-attributes.md §6](09-attributes.md#6-erasure-retirement-and-the-audit-payload)). That is the
   one place in this system where erasure deletes rather than overwrites, and
   [§4](#4-deletion-policy) says why it is the only row that can be handled that way. A redacted
   person with attribute values attached is a redaction that did not happen. A `redaction_log`
   records what was redacted and when.
3. **Some data must not be redacted, and the reason is now stated rather than left unopposed** —
   membership periods, unit participations, fee obligations, payments and position assignments are
   organizational history rather than personal data, and removing them would falsify records that the
   organization is often obliged to keep. Until
   [D-088](../decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)
   this item was a carve-out nobody had had to defend; it is now the permanent half of a pair of clocks,
   and those rows carry **no retention period at all**. That is what gives
   `redaction_log.retained_reason` a judgement worth recording instead of a formality
   ([06-audit-and-import.md §4](06b-redaction-and-checks.md#4-redaction-log)). **What the decision did not do
   is supply a legal basis, and the difference should not be blurred:** what stands here is an assumption
   pending review — organizational history plus accounting obligations, leaning on a person row that the
   erasure in item 1 has made non-identifying — recorded as an assumption and not as settled law. **The
   uncertainty about that half reaches nothing on this side:** the erasure in items 1 and 2 is immediate
   and absolute, and would be if the retained half were cut to a single year tomorrow.
4. **Whatever keeps its own retention policy must be able to see `person.redacted_at`, and erasure
   reaching it is a rule that store has to implement.** There is no separate health or safeguarding store
   for such a rule to live in: a diagnosis is an attribute value now, with the same access, protection and
   retention as a shoe size
   ([D-083](../decisions/round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data),
   [09-attributes.md](09-attributes.md)). The store this system does have is `audit_log`, and this item is
   worth keeping precisely because it is easy to wave through: its retention has half an answer — **the
   rows are kept for the life of the system and their payloads are emptied 24 months after they are
   written**
([D-088](../decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short);
   [06-audit-and-import.md §6](06b-redaction-and-checks.md#6-open-issues) keeps the legal half that remains) —
   and a redaction that stops at the business tables while the trail keeps the erased values is a
   redaction that failed in the one place a regulator looks. **The window is a ceiling on how long a value
   may sit there, never a waiting period: erasure reaches the same two columns on request, at any age of
   the row, and does so immediately.** That is the distinction the two separate checks in that document's
   §5 are for — one fires when a person's erasure did not happen, the other when the clock's work did not
   happen — and it is the reason **this section describing erasure does not make a store honour it; the
   checks are what notices.**
5. **Sensitive attributes should not be over-collected.** `person.gender` is included because
   Scouting-type organizations typically must report it; if yours does not, remove the field
   rather than keeping it "just in case". **The same test now applies per code**, since most of what
   is collected is decided at runtime: a code nobody can justify is retired
   ([09-attributes.md §2](09-attributes.md#2-attribute_definition--the-vocabulary)), and retirement —
   which stops the collecting without destroying what was already recorded — is the mechanism.
   Erasing what was recorded is item 2, and only item 2.
6. **Redaction is invisible in listings and visible in the database.** A redacted person must not
   appear where people are listed, and must still resolve wherever an old record points at them
   ([01b-merges-views-and-checks.md §9](01b-merges-views-and-checks.md#9-views)). These two requirements are one rule with two
   halves and the first version of that document had only one of them.
7. **The trail is a second copy of the person record and has to be guarded like one.** For a
   person's descriptive data the trail holds the **value** — the before and after image, exactly as
   it does for a contact point or a note — because
   [D-085](../decisions/round-07-08.md#d-085--the-identity-machinery-stays-structured-the-boundary-is-rules-not-sensitivity)
   chose overwrite-in-place on the strength of the trail being the history there is, and a trail that
   records *a value existed* without recording which one answers neither of the two questions an
   audit entry is built for (*who said this* and *what did they say*). The consequence is therefore
   about the log rather than about the shape of a row: **an audit entry about a person is as
   sensitive as the person data it carries**, which is a requirement on a permission's sensitivity
   mark and not on anything the schema can express — see
   [05c-access-log-and-resolver.md §9](05c-access-log-and-resolver.md#9-access_log), which argues against copying data into
   a less-guarded place and describes this table better than it knows: the trail *is* such a copy,
   holding the whole person record in its payloads while historically being graded below it. Nothing
   here makes that guard true; the catalog does, or does not
   ([appendix/permission-catalog-a-codes.md §8](../appendix/permission-catalog-a-codes.md#8-audit-and-system)).
   The mechanism that implements erasure against this table is in
   [06-audit-and-import.md §2.2](06-audit-and-import.md#22-redaction-before-logging) and its §4, and
   [09-attributes.md §6](09-attributes.md#6-erasure-retirement-and-the-audit-payload) is where the
   trade is stated next to the values. **The same section carries the fact that this copy expires**: the
   values this item names are emptied out of payloads 24 months after they were written
   ([D-088](../decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)),
   which shortens the exposure this item is complaining about and settles nothing about the guard it
   demands — so the sentence opening this item, *the trail is a second copy of the person record*, is true
   for two years and untrue afterwards, and the mark on the permission has to be right for the years in
   which it is true. **The clock makes erasure neither cheaper nor slower.** Items 1 and 2 act on those
   same columns on request, at any age of a row, and the row's scheduled emptying satisfies nobody's
   erasure request.

> Legal review is required before implementing §8. This section describes the technical mechanism,
> not the compliance policy. Tracked in
> [../open-questions.md](../open-questions.md).
>
> **What the review is handed has changed shape, which is worth saying so nobody reads this note as
> unchanged.** It used to be asked "how long may this trail keep personal data, and which fields count as
> personal data". The corpus now puts a concrete policy in front of it instead of a blank: rows forever
> and payloads for a bounded window on one side (item 4), an accounting skeleton with no clock at all on
> the other (item 3), and no graded category of field anywhere for it to deliberate over, because D-083
> deleted that idea. **What is asked is narrower and harder: on what basis does the retained half survive
> indefinitely.** That is the assumption item 3 names, and nothing in this section makes it lawful.

**The key-name list is a credential filter, and reading it as the personal-data filter is the mistake to
avoid.** It once carried a list of sensitive *key names* — `notes`, `custody_arrangement`, and the rest —
and stripped any image holding one, which presupposed a sensitive **subset** of the person record: a list of
names is a way of pointing at some fields and not others. [D-083](../decisions/round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)
removed the subset, and what is left of the list is a set of arbitrary fields — one that **fails on the first
value stored under a name nobody predicted**, in an attribute layer whose whole purpose is that nobody can
enumerate its names. So the list keeps exactly one class of value out of the trail: **the values that must
never be logged at all** — credentials, tokens, the secret half of an integration — the only values where
*being in a log* is itself the harm. Everything else, `notes`, the reason fields and an attribute value
included, is logged in the clear and protected by **who may read the log** (item 7), because the answer to
*who may read a child's address* was never a list of field names. Read the list as a credential filter and it
is a working mechanism; read it as the personal-data filter, notice that `allergy` is not in it, and conclude
the payload is covered. [09-attributes.md §6](09-attributes.md#6-erasure-retirement-and-the-audit-payload)
carries the same warning next to the values themselves.

**Two things that used to do this work are gone, and they failed in different directions.** Redaction of the
audit *payload* was a trigger stripping listed keys out of the before/after images; there is no trigger, so
both halves of that job — credential stripping, and the scrub items 2 and 7 require when a person is erased —
are application behaviour. Forgetting the first writes a secret into a table designed to be read later by
auditors; forgetting the second leaves an erased person's values in the trail with a `redaction_log` row next
to them saying they are gone. *(Inside that trigger was a list of keys to scrub **unconditionally**, and
nothing ever read it: a dead list of forbidden fields is not a protection.)* The other is the listing view
that excludes redacted rows, which is §6a's problem in general. **Neither failure is loud**, and both are
written down because a compliance property resting on a code review is the kind of thing an organization
discovers from a regulator.

---

## 9. Referential integrity rules

| Rule | Rationale |
|------|-----------|
| References **restrict**, with **one** deliberate exception | A person cannot be removed while memberships reference them, and nothing but the exception below cascades. **The exception is `event_organizer.event_id`** — deleting an event removes its organizer rows, the single `ON DELETE CASCADE` in this design ([08-events.md §3](08-events.md#3-event_organizer) explains why it is safe there and nowhere else). |
| Cascade delete is refused everywhere else | It is the enemy of a 40-year audit trail, and ORM relation configs default to it. **Check every one**, and read the exception above before you "fix" the one row that is allowed to cascade. |
| Optional references document *why* they are optional | An optional reference is usually a design decision worth recording, and it is invisible in the schema. |
| There are exactly **two** reference-less keys, and both are polymorphic on purpose | `access_grant.scope_id` and `audience_operand.selector_arg_id`, the second documented in [05a-audience-and-grammar.md §8](05a-audience-and-grammar.md#8-audience--grants-that-target-a-set-of-people). Neither may gain a third companion without a decision: a polymorphic key is a rule the schema cannot check, so each one has to buy the orphan scan that covers it — §11 of that page, [Invariants to verify](05d-invariants-and-seed.md#11-invariants-to-verify), carries both scans and the nightly report that replaces the missing foreign key. *(This row used to read "`access_grant.scope_id` is the **one** reference-less key … nothing else may be", which had been false for several rounds by the time the round that widened `selector_arg_id` from three tables to five got written down. It is the same defect [D-104](../decisions/round-10b.md#d-104--a-permission-codes-last-segment-is-an-action-and-a-registry-that-prose-contradicts-is-a-fiction) was entered for, in a conventions page rather than a registry.)* |
| Circular references are broken with an optional column, not a deferred constraint | `membership_request` ↔ `membership` is the one instance; the two-step insert is documented where it lives. |

The polymorphic `access_grant.scope_id` deserves its warning again now that the schema is
generated: **an ORM will want to make this a real relation, and making it one is a design
change.** It points at **the unit**, or at exactly one item — an `event`, a `person_group`, a `role`, or
the deferred `document` — depending on the sibling `scope_type` column
([D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row) deleted the
unit family from that list, so "a unit" and "an organization" are now the same answer rather than two of
them). No foreign key can express that, and every query that joins it must filter on
`scope_type` first. If the ORM maps it as a relation to one table, the others become silent
wrong answers rather than errors.

---

## 10. Migration discipline

- **Every migration is reversible**, or explicitly marked irreversible with a rationale. A
  migration that drops a column holding historical data is irreversible by definition.
- **Never rewrite a historical row's meaning.** Adding a column is fine; changing what an existing
  value *means* is a data migration that needs its own review, and it is the kind of change that
  makes old audit entries lie.
- **Backfills are separate from schema changes**, in their own migration, so a failed backfill
  does not roll back a schema change and vice versa.
- **Seed data for vocabularies** (`permission`, `reason_code`, `grant_scope_type`, and
  `selector_type` — the last of these being the language an audience expression is written in,
  [D-101](../decisions/round-10b.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree))
  lives in migrations, not in application startup code, so the vocabulary is versioned with the
  data it describes. Application-startup seeding produces environments that disagree about what
  `event.answer.view` reaches. It is also the reason `selector_type` is read-only to an
  organization: an operand added at runtime is a word no resolver knows, and the empty set is a
  quiet way to say so.
- **Two documents are the source of truth for what a migration must achieve:** each data-model
  file's **Rules** block for the constraints, and its **Invariants to verify** block for the
  reports. A migration that implements neither set completely has generated a schema, not a
  design.

---

## 11. Where each subject is described

Not "where the DDL lives" — that question stopped meaning anything at D-072. Each document below
states the fields, rules, invariants and open issues for its part of the model.

| Document | Entities |
|----------|----------|
| [01-identity.md](01-identity.md) | `person`, `person_name`, `account`, `account_credential`, `person_contact`, `person_identifier`, `identity_hypothesis`, `person_merge` |
| [02-organization.md](02-organization.md) | `person_group`, `person_group_member` — and nothing else, because there is no unit table: the unit is a scope ([D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)) |
| [03-membership.md](03-membership.md) | `membership`, `membership_type`, `membership_request` |
| [04-relationships.md](04-relationships.md) | `guardianship` (carrying the guardian's current `right_level`), `guardianship_permission` (the **history** of that value) |
| [05-authorization.md](05-authorization.md) | `permission`, `role`, `role_holder`, `access_grant`, `audience`, `audience_operand`, `selector_type`, `grant_scope_type`, `access_log`, `api_key` (a caller that is not a person: [05e-keys-and-callers.md](05e-keys-and-callers.md) §14–§17) — and **no member table for an audience**, because a hand-named person is a `PERSON(x)` leaf in the expression ([D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)) |
| [06-audit-and-import.md](06-audit-and-import.md) | `audit_log`, `field_conflict`, `redaction_log`, `import_batch`, `staging_import*` |
| [07-finance.md](07-finance.md) | `fee_schedule`, `fee_obligation`, `payment_request`, `payment`, `bank_transaction` — **provisional on policy** |
| [08-events.md](08-events.md) | `event`, `event_organizer`, `event_registration`, `event_question`, `event_answer` |
| [09-attributes.md](09-attributes.md) | `attribute_definition`, `attribute_option`, `person_attribute` — **everything the system knows about a person other than their name, their gender and their age** ([D-083](../decisions/round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data), [D-084](../decisions/round-07-08.md#d-084--descriptive-data-is-organization-defined-at-runtime)). It is last in this table because it is last in every other document's account of a person: it references `person` and nothing references it |

Each document presents its entities in **dependency order**: one appears only after everything it
references. That ordering was needed to make a schema file execute; it is kept because it is also
the order in which the model is understandable.

**Messaging is not in this table.** `message` and `message_recipient` are decided at
[D-077](../decisions/round-06.md#d-077--messaging-is-direct-by-default-broadcast-is-an-ordinary-scoped-permission-and-the-recipient-chooses-the-channel)
and not yet designed; they will need their own document. The absence is tracked in
[../open-questions.md](../open-questions.md#h-not-yet-designed).
