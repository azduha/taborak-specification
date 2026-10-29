# Glossary — Ubiquitous Language

Terms used consistently across every document in this folder. Where everyday
language is ambiguous, the definition here wins and the schema follows it.
Each entry says what a term means in the system as designed today; how a term came
to mean that is in the [decision log](decisions/index.md).

---

## The three-way split that everything else depends on

These three words are frequently conflated in real organizations. This design keeps
them strictly apart, because conflating them is the single most common source of
unfixable data models in this domain.

| Term | Definition | Table |
|------|-----------|-------|
| **Person** | A human being the organization knows about, now or ever. Exists independent of whether they have ever logged in, paid, or applied. | `person` |
| **Account** | A set of login credentials attached to a person. Optional — a person imported from a 1994 paper roster has no account. | `account` |
| **Member** | *Not a noun in this system.* A person is "a member" at a moment in time if they hold a qualifying membership. It is always a question with a date attached. | `membership` |

A fourth, related distinction:

| Term | Definition | Table |
|------|-----------|-------|
| **User** | Avoid entirely. When you mean the account, say account; when you mean the human, say person. Most systems use "user" for the wrong one and it never gets fixed. | — |

---

## Identity

**Person** — A human. Stores given name, family name, birth date, and gender. Nothing
else: no member status, no child/adult flag, no group, no office, and
**no deceased flag** — the organization does not record death. What the organization
records *about* the human is not on this table at all: it is
[descriptive data](#personal-data), reached by the same permission as the rest of the
person record, because none of it is a different kind of object.
Specified in [data-model/01 §2](data-model/01-identity.md#2-person).

**Account** — Credentials and login state for a person. A person may have zero or
more accounts over their lifetime (a childhood account abandoned in 2010, a new one
created in 2024), **but at most one live one** — closed rows aside. Accounts are never
shared between people, not even between a parent and child.

**Account activation gate** — The rule that an account may not reach `active` while an
unresolved identity hypothesis names its person. A sign-up that *strong*-matches an
existing person — exact legacy member number, or exact birth date together with a
normalized name, **never the fuzzy band** — raises a hypothesis. Its own rows are
created and stay `pending_verification`: **nothing is merged, nothing is linked,
nothing is activated.** The contact point the person typed survives as the credential it
was offered as, and `identity_reviewer` decides it with `person.merge`. The holding
message confirms nothing, since a sign-up form that can answer "yes, that person exists"
is an existence oracle over a roster of children; and a hypothesis that is blocking an
account gets an age check that alerts, because a stalled queue is not a
data-quality problem but a specific person who cannot log in
([D-089](decisions/round-07-08.md#d-089--one-live-account-a-colliding-sign-up-files-a-claim-and-creates-nothing)).
"I have a new e-mail
address" is not this case and is not routed through it: `account_credential` holds many
credentials for one account.

**Contact point** — A single email address, phone number, or postal address belonging
to a person, one row per point in `person_contact` rather than a column, so that a
person can have five email addresses, or a new kind invented later, without a
migration. Each has a `type`, a `purpose`, and a verification timestamp. A postal
address is a contact point of type `postal`: two people at one address are related by a
query, not by a table, and a shared address grants nothing to anybody.

**Identity hypothesis** — A *proposed* but unconfirmed link between two `person` rows
that may actually be the same human. Created during legacy import, by the nightly
matcher, when someone registers claiming a historical identity, or by a sign-up that
strong-matches a person who already exists. Confirming one triggers a merge; while one
is unresolved it also holds the account of any person it names out of `active` — see
**account activation gate**.

**Merge** — The act of declaring two person rows to be one human, and collapsing them.
Never a delete: the absorbed row survives as a tombstone pointing at the survivor, so
that historical foreign keys keep resolving. Always a human's decision
(`person.merge`), including at the highest score — and refused outright when the chosen
survivor turns out, on resolution, to be the person being absorbed.

**Merge chain** — What forms when a survivor is itself later absorbed. The pointer is
**not rewritten forward**: A→B→C stays a chain and `resolve_person()` walks it to the
live row. Chains persist because reversing a merge would otherwise be a reconstruction
of facts nobody recorded. Two rules come with the chain, neither on the read: a cycle is
impossible because the *merge* is refused, never because a hop limit gave up; and a
chain longer than **three hops is reported**, which is a statement about the matcher's
queue, not about the row.

**Unmerge** — Reversing a merge a human approved. The tombstone comes off, rows created
*before* the merge go back to the revived person, and rows created *inside* the window
are flagged for a human rather than split by a rule — every `access_grant` from that
window flagged, not guessed. **The merge is reversible; the merged window is not**: what
two people did while they were one row stays one row's history, because the record
cannot separate who did it. No permission of its own — undoing an identity correction is
the same act as making one, so it is `person.merge`.

**Membership export** — **One of the two files the legacy corpus actually is**, and
neither of them is a roster. A row says: a person, a birth date, and **the period they
were a member of the unit**. A people batch turns it into `person` rows and **bounded**
`membership` rows — both ends dated, `data_confidence = 'low'`, batch id set — and **no
fee obligation of any kind**. **It names no group either**, so it answers neither
*"who was in the Thursday group in 2011"* nor *"were they a child or a rover"*, and
nothing is created in `person_group` from it: a corpus that names no groups means every
roster row is typed by a person, which is also the only way one can be true.

**Attendance export** — The other file: events, and which people came. It becomes
`event` rows **with no owner** — there is no column for an imported event to have
([D-102](decisions/round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)) — with
one `event_registration` per attendee at `attending` and `was_present = true`, and **no
`not_attending` rows**, because an absence row would say the system asked someone who
was never asked. **Attendance never becomes a membership**, and it never becomes a group
roster either: attendance is read through the `ATTENDED` and `PLACED` selectors, and no
rows are written into `person_group_member` from it.

---

## Personal data

Everything the system knows about a person once you subtract what they are *called* and
*counted as*. The module is [domain/08-person-data.md](domain/08-person-data.md), the
tables are [data-model/09-attributes.md](data-model/09-attributes.md).

**Descriptive data** — **Everything the system holds about a person other than their
name, their gender and their age: one class of data, with no privileged corner inside
it.** Allergies, medication, insurance numbers, languages, measurements, clothing sizes,
dietary habits, a grandparent's phone manner — the same kind of fact, held in fields
rather than files, none of it a different kind of object from any other, and all of it
reached by the permission that already reads the person. The term exists to rule a
category *out*: there is no sensitive sub-record with its own codes.
*Why:* a sub-record of its own was declined on the merits, and its cost — one read rule
over the whole record — is stated in
[D-083](decisions/round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data).
It is the reason `person.view` is graded in the catalog's top tier.

**Attribute definition** — One thing the organization has decided to collect: a `code`, a
label, a description of what belongs in the field, a value type, and whether several
values may be current at once. The **type draws the form and raises the warning; it never
refuses a save** a human insists on — `2019` recorded as the year of a checkup is a truer
record than an empty field behind a validation error. Creating, renaming, merging or
retiring a definition is `attribute.define`; recording a value against one needs nothing
beyond `person.edit`.

**Person attribute** — The value one person currently has for one code. **Overwritten in
place:** the row is the organization's present belief, and the sequence of earlier
beliefs lives in the audit trail, **values included, for 24 months** — logged on the same
terms as a contact point or a note, because a list of person fields whose values must not
be logged would be a privileged corner, and would leave nothing behind for an overwritten
value. What guards the trail is who may read it, not what it omits — **and it omits, on a
clock**: those logged values are emptied 24 months after they were written (see **payload
reduction**), so the trail is the record of *what changed, who did it and when* for the
life of the system and the record of the *values* for two years. The honest name for the
whole stack is therefore **no long history**, not merely *no temporal columns*: the value
lives in one overwritten row, the copy of it depends on a write path remembering to log,
and the copy ages out. If a case ever needs the long version, the fix is temporal columns
on the value — [D-085](decisions/round-07-08.md#d-085--the-identity-machinery-stays-structured-the-boundary-is-rules-not-sensitivity)
reversed — and not a longer trail. No `valid_from` / `valid_to`, deliberately
([data-model/09 §3](data-model/09-attributes.md#3-person_attribute--a-value-one-person-has)).

**Proposed code** — A definition that came into existence because somebody recorded a
value against a code that did not exist. It waits in the curation queue: kept out of data
entry forms and reports, yet **readable by anyone already entitled to read the person**,
because the organization's data quality problem is not the family's confidentiality
problem. It is where an improvised need at 23:00 goes instead of into a notes box that
nobody will read again — **improvised by a person at a desk**, which is the whole meaning.
It is emphatically *not* "whatever the legacy import did not understand": the codes a
batch's column→code map names arrive `live`, because a curator read that map as one
object before the batch applied, and several hundred proposals landing on day one would
make this queue's age signal meaningless before it had ever meant anything.

**Retired code** — A definition taken out of data entry and left alone everywhere else:
readable, reportable, revivable, its values untouched. **Deleting a label must never
delete the facts filed under it**, or the badly-named label is never retired and the
vocabulary accretes instead of being curated. Redaction is the opposite operation:
retiring keeps the values, erasing a person deletes them, immediately and whatever their
age. The other thing that removes stored values is **payload reduction**, below, and the
distinction is that redaction answers to a person and is absolute, while reduction
answers to a calendar and is bounded.

**Payload reduction** — Emptying the `old_values` / `new_values` out of an audit row
**24 months after it was written**, leaving everything else standing: actor,
on-behalf-of, operation, table, record id, changed fields, transaction, session,
channel. The trail goes on answering *who changed this row, when, and were they allowed
to* for the life of the system, and stops answering *and to what* after two years; twelve
months is the floor the window may be set to. **Not redaction**, which is a named
person's erasure, immediate and absolute, and reaches payloads of any age; **not an
import revert**, which deletes the rows a batch created. Reduction is the one case in
this design that deliberately unwrites *later* than the write, so its failure mode is not
running at all — hence a scheduled job with a check that alerts on any row past its
window still carrying a payload
([D-088](decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)).

**The two clocks** — The accounting skeleton (`membership`, `fee_obligation`, `payment`,
and the anonymised `person` row an erasure leaves behind) has **no clock at all**,
justified as the organization's own history. *Assumption:* that this indefinite retention
of rows about a named person has a legal basis — organizational history plus accounting
obligations, against a redacted person row that keeps the skeleton non-identifying — is
unverified, and a decision log is not the document that grants it. The audit trail runs
the opposite direction: rows forever, payloads for 24 months. Erasure sits outside both,
immediate and absolute. The same window is *proposed* for `access_log` and is not yet
confirmed ([F-8](open-questions.md#f-8--retention-policy-for-access_log)).

**Curation** — Keeping the vocabulary meaning one thing: merging near-duplicates,
promoting or discarding proposals, retiring codes nobody uses, and writing the
description that stops one code meaning four things to four people. It is
`attribute.define` plus somebody who reads what they are given, and the documents treat
it as a job rather than an outcome — an open vocabulary left unwatched decays into
`allergy`, `Allergy`, `alergie` and `allergies (2)`, after which the layer still stores
everything and answers nothing.

*Not to be confused with* **identity**, which stays structured in its own tables: a fact
keeps a table of its own when there is a rule about it that an open layer physically
cannot hold — one primary postal contact, one current name, a birth number that may not
repeat. The boundary is that test, not sensitivity
([domain/08 §1](domain/08-person-data.md#the-three-exceptions-and-why-they-are-exceptions)).

---

## Organization

**The unit** — There is exactly one, and it is the organization. It is **a scope, not a
row**: no table, no id, no parent, no type, no name history, no path. In
`grant_scope_type` its code is `unit` — the one row there with `is_item_scoped = false` —
and a grant written at the unit carries no `scope_id`. Say **the unit**: not "the root
unit", not "the organization unit", not "org"; there is no second unit for the word *root*
to distinguish this one from, and a name that implies a second one is how a hierarchy
creeps back into a sentence. Membership, a role, and a grant at non-item scope are all
held *at the unit*, and a grant at it reaches **every item of every type**. There are no
unit kinds either: `pack`, `troop` and `section` name nothing in the model, and where
these documents need a set of people they say **group**
([D-097](decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)).
What one unit costs — there is no body between a person and a unit-scope read, and no
per-unit report — is stated in
[domain/04 §1](domain/04-organization-structure.md#1-the-organization-is-one-unit-and-the-unit-is-a-scope).

**Group** — **A `person_group`: a named set of people with explicitly stated, dated
members and a lifetime of its own.** A `name`, a `description`, `valid_from` / `valid_to`
and the audit columns; its roster is `person_group_member`(person, **`valid_from`**,
**`valid_to`**, who wrote it, note), dated rows that may not overlap **counted over all
rows**, half-open. **Company, not a body**: the Thursday group, the kitchen crew, this
year's camp staff — in the organization's own words *"a temporary set of members that do
e.g. events together"*. What a group is **not**: no parent and no children, no type and
no vocabulary of types, no `code`, no path, no nesting rules, no rename history, no split
or merger edge, no leadership of its own, **no roles**, and no fee. **Being in a group
authorizes nothing** — `person_group.member.manage` writes a roster and nothing else;
participation is not authority, and tidier storage does not promote it
([D-098](decisions/round-10a.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority)).
A group **is an
item** (registered in `grant_scope_type`), so *"these two may work this group's roster"*
is a grant on one group. Its two dated facts are **different facts**: the group's own
period says it existed, the member rows say who was in it, and *"who was in
`schuzka2026-1` on 14 March 2026"* is a point-in-time read over the roster — which is why
the rows are dated, and why that answer survives the audit trail's payload expiry.
**A group is not an audience**: a group *states* its members and an audience *picks* them
([Audience](glossary.md#authorization)). **Nobody writes themselves onto a roster** —
`person_group.member.manage` has no self-scoped variant and none will be added, and **no
group is seeded**. **Moving a person between groups closes one dated row and opens
another.** Specified in
[domain/04 §2](domain/04-organization-structure.md#2-what-a-group-is-and-everything-a-group-is-not)
and [§3](domain/04-organization-structure.md#3-joining-a-group-is-somebody-elses-act).

**Office (a `role`) and `role_holder`** — **An office is a small, visible set of
holders** — the leaders, the finance people, IT — where a group is company. The
difference decides **who may edit the membership**: `role.assign` / `role.unassign` are
🔒🔒, the most sensitive family in the catalog, while writing a group's roster is
`person_group.member.manage` at ⚠. `role` keeps `code`, `name`, `description`,
`is_system`, `sort_order`; **`role_holder`**(role, person, `valid_from`, `valid_to`,
`granted_by`, `note`) is the holder row and names **exactly one person** — one grantee
per row, always, because [F-12](open-questions.md#f-12)
is closed and the answer is no. **A role confers nothing**: the codes an office carries
are **the live grants whose expression names `ROLE(x)`**, which is what makes *"what may a
treasurer do?"* a query over rows a person wrote
([D-100](decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)).
An office is held **at the unit,
always**; a role is an item, so a grant can be written on one. Nothing forces a holder row
to end — the report is the control
([D-071](decisions/round-05.md#d-071--nothing-forces-a-role-assignment-to-end-the-gate-and-the-report-are-the-control)),
and an empty office is not a reportable vacancy: absence of rows has no start date
([F-18](open-questions.md#f-18--does-a-role-record-elected-versus-appointed-and-what-does-an-election-write)).

---

## Membership

**Membership** — The period during which a person is a member **of the unit**. Holds
`valid_from`, `valid_to` (null = open/current), and a status in an approval workflow. A
person accumulates multiple memberships over time; they never overwrite one another.
**"Everyone in the organization" is one query against `membership`.** There is exactly
one kind of it and **it is ageless**: membership does not distinguish children from
adults, has no age ceiling, and does not end because a person got older. Being a
counselor or a leader is an **office** held through `role_holder`, never a membership
type.

**Membership type** — A table kept for the future, currently holding **one row**:
`member`. It survives as a table rather than collapsing into a constant so that a second
kind of membership (a supporting or honorary one) would be a data change rather than a
migration. The fee is flat and per person, so the type does not affect pricing either.

**Membership request** — A person's application to become a member **of the unit**.
Separate from the membership itself, because a request has its own lifecycle (submitted,
under review, rejected, withdrawn) and can be rejected without ever producing a
membership. **Nothing gates a request except identity and payment** — there is no
checklist to satisfy. **Which group a new member lands in is a write on the group, never
a preference on the request.**

**Lapse** — A membership ending because the yearly fee was not paid or the person
withdrew. Distinct from termination for cause, which requires a reason code. **A lapsed
person is not a member and holds no member permissions**, though a renewal window lets
them rejoin without re-applying.

**Renewal window** — The fixed period after a membership expires during which payment
restores it **without re-applying**, and — importantly — opens the new period *at the
expiry date*, so the record shows continuous coverage and the person is not misclassified
as a returning member. Tracked as **dates, not a status**: during the window the person is
simply expired.

**Returning member** — A person whose new membership follows a gap. The system detects
this rather than treating them as new: 1990–2010, gap, 2024–present.

**Imported membership** — **An imported membership is bounded at both ends, always.**
A membership is never inferred from attendance
([D-093](decisions/round-09.md#d-093--the-one-off-import-may-create-memberships-both-ends-dated)).

---

## Relationships

**Guardianship** — A period during which one person is responsible for another.
Directional: guardian → dependent. Carries relationship kind (`parent`,
`legal_guardian`, `foster_parent`, `step_parent`, `grandparent`, `sibling`, `other`) and
an end date that **a person sets**. **Not a birthday**: the system takes no position on
majority, and no job ends one
([D-069](decisions/round-05.md#d-069--guardianship-ends-when-a-person-ends-it-the-system-takes-no-position-on-majority)).

**Party to a guardianship** — The guardian and the subject, both. **They, and not staff,
run the arrangement:** either may end it, a guardian may add another guardian, and no
request has to go through the organization
([D-073](decisions/round-06.md#d-073--guardianship-is-administered-by-its-own-parties-not-by-staff)).
Staff hold the same powers and are *a* route, never *the* route. A guardianship is a
relationship between two people who are both principals on the row, and that is why they
run it.

**Guardian's right** — **One of exactly three values on the guardianship row: `none`,
`view`, or `write`.** Nothing more granular exists
([D-074](decisions/round-06.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular)).
A right is measured against `permission.right_kind` (`read` | `write`): `none` covers
nothing, `view` covers `read` codes, `write` covers both. A guardian is a **channel**, not
a set and not a grant: a guardian's act is checked under the ordinary code for the thing
being touched, so this is one vocabulary and not a second authorization model.
**Being a guardian still grants nothing by itself**; `none` is a real value and the common
starting point for anything the guardian did not assert themselves.

How the channel answers: a check looks for a live `guardianship` row linking the person
asking to the person the action is about, and reads `right_level` off it — **a lookup over
a relationship, not a set anything resolves**; the channel returns an allow or says nothing
at all. The history of that value is `guardianship_permission` (`right_level`,
`valid_from`, `valid_to`, `changed_reason`, `changed_by`) — no grantee, no permission code,
no audience. **A guardian is neither a grantee nor an operand**, and `write` means *any
action about this child*, which is wider than any expression could assemble and narrower in
the direction that matters: **it reaches no item that is not about the child.** There is no
guardian-shaped permission code anywhere in the catalog and none scoped to "my ward", so
**nothing has to be granted for a guardian to act as a guardian**
([D-113](decisions/round-13.md#d-113--the-guardianship-channel-has-no-expression-guardians-is-not-a-selector)).
The system computes no guardian list from these rows; *"send these six children's parents
the newsletter"* is a `person_group` somebody maintains, aimed at through `GROUP(x)`.

What the short vocabulary gives up is recorded in the catalog: **it is not possible to say
"read everything except the medical record."** *Why:* the case that sentence was invented
for — a parent keeping access to everything about their child except the medical file, by
court order — was declined on the merits, because there is no medical record inside the
person record to be excepted from: everything other than name, gender and age is
[descriptive data](#personal-data) of one class
([D-083](decisions/round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)).
So the right level is `none`, `view` or `write`, applied to the record **whole**, and what
was given up is not a half-built feature but an arrangement the organization decided not
to want.

**A key is a grantee, and never an operand.** Where a guardian holds a channel and no grant,
an integration holds grants and belongs to no set, `EVERYONE` included — and it is not an
**account**, which is a way for a person to log in
([API key](glossary-authorization.md#authorization),
[D-116](decisions/round-16.md#d-116--a-caller-that-is-not-a-person-is-a-registered-key-and-a-key-is-a-third-grantee-kind),
[D-117](decisions/round-16.md#d-117--a-key-is-never-inside-an-expression-thirteen-selectors-and-none-of-them-can-name-one)).

**Acting on behalf** — Performing an operation as another person, under that guardianship
row's right level (`view` to read it, `write` to change it). Every such operation records
both the acting person and the subject person
([data-model/04 §5](data-model/04-relationships.md#5-acting-on-behalf--recording-it)).

---

## Authorization

The authorization vocabulary — **permission, scope, grant, allow and deny, channel, audience,
selector, the expression grammar, the compilation, a key and the caller a check is answered
about, and the states a named thing gets instead of deletion** — is defined on its own page:
[glossary-authorization.md](glossary-authorization.md).

---

## Events

**Event** — A dated occasion that people **register** for: a camp, a trip, a hike, a
jamboree. It has a start and an end, an optional capacity, an optional fee, and a set of
**organizers**. It has **no status column** — visibility *is* the permission model, and
cancellation is a recorded fact rather than a state. **Nothing owns an event**: there is no
`event.org_unit_id` and no `can_event()`; the people connected to an event are named by
**selectors that bind to it**
([Bound operand](glossary.md#authorization)), and an event is addressed by being
**the item** of an item-scope grant, which is the only way anything reaches it
([D-064](decisions/round-05.md#d-064--there-is-no-event-status-visibility-is-the-permission-model),
[D-102](decisions/round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)).

**A weekly meeting is not an event.** Forty meetings a year are not forty events, so there
is no recurrence, no series and no occurrence table. What the meeting has is a **group** to
be in — a dated roster, not a calendar of evenings. **"Was Jan at the meeting on 14 March?"
is answerable by nobody**: a group says who **is in** it between two dates, not who walked
in on a given evening.

**Organizer** — Someone **running** an event. A roster entry on the event (`event_organizer`)
with an optional label (`'lead'`, `'cook'`, `'driver'`) and an order — **not** an
`access_grant`, and analogous only to **being a member of a group**. Authority to *act* on
the event arrives from **one seeded grant template** — `event.answer.view`, scoped to an
event, aimed at the bound operand `ORGANIZERS` — instantiated per event by whoever creates
it. An event created without that grant has organizers who can do nothing, which is why the
*events with no answer-view grant* report exists
([D-062](decisions/round-05.md#d-062--organizers-are-appointed-on-the-event-not-granted)).

**Registration** — One person's answer about one event: `attending`, or `not_attending`.
**"Unanswered" is not a value** — it is the absence of a registration row, so "who has not
replied yet?" is the eligible set minus the registered set.

**Eligibility** — Who may register. This is **capability**, not a rule engine:
`event.register_self` is an ordinary permission, allowed by a live **allow** grant and
blocked by any live **deny**, granted either on the unit or on the event itself; opening a
camp to members is **one** `access_grant` naming an audience whose expression contains
`MEMBERS`; an age-restricted camp is a camp opened to **a group**
([D-060](decisions/round-05.md#d-060--eligibility-is-capability-there-is-no-separate-rule-engine)).

**Waitlist** — What happens when a full event gets a self-service registration: the person
is written down and ordered, never refused. **Organizers may exceed capacity** outright,
and the overrun is reported rather than prevented — the leader who knows there are two
spare tents is trusted
([D-065](decisions/round-05.md#d-065--capacity-is-a-waitlist-threshold-and-organizers-may-exceed-it)).

**Presence** — Whether someone actually turned up, marked by an organizer after the fact.
Three-valued: `NULL` (no register taken), `true`, `false`. For a camp this is **the record
of who was in the organization's care**, and it cannot be reconstructed from registrations.
Not the same as registration — a no-show is a registration with `was_present = false`.
Because it is `NULL` until somebody marks it, **there is no `PRESENT` selector**: a
selector that meant "came" would silently mean "was not marked absent" on every event
nobody took a register for.

**The four attendance tiers** — Four argument-less selectors that **bind to the event** a
grant is scoped to, so a sentence written once reads correctly on every event it is copied
to. From widest to narrowest:

| Selector | Who it reaches, on the bound event |
|----------|-----------------------------------|
| `ATTENDED` | anyone whose `response` is `attending` — asked, said yes, whether or not there was room |
| `PLACED` | those attending **who were not waitlisted** — the set the capacity actually let through |
| `CONFIRMED` | `PLACED` **and** `is_confirmed` — somebody has since looked at each of them |
| `ON_WAITLIST` | written down, ordered, **not yet placed** — waiting, not attending |
| `ORGANIZERS` | the event's organizer roster — the reason a per-event answer-view grant is seeded |

They are **not** one set with flags: `ATTENDED` is wider than `PLACED` precisely because a
full event says yes to more people than it can seat, and `CONFIRMED` is narrower than
`PLACED` because a seat is not a headcount. **`WHITELISTED` is not one of these**, and is
not a selector at all — see
[EV-6](open-questions.md#ev-6--whitelisted--the-word-people-reach-for-with-no-stored-state-to-name).

---

## Money

**Payment request** — A liability rendered payable: an amount, a recipient account, a
start, and an optional expiry. **The request, not the payment, is the entity the finance
module is built around**, because it is the only thing that connects "we expect money" to
"money arrived". It is not an invoice; the organization may also owe people invoices, which
is still open
([D-075](decisions/round-06.md#d-075--money-arrives-from-a-bank-api-a-payment-is-requested-by-variable-symbol-and-qr-code)).

**Variable symbol** — The number a payer types into their bank, and the number the bank
reports back against the money. **Unique across every symbol ever issued, not merely across
live ones**, and taken from a sequence — never derived from a birth date, a member number,
or anything else a stranger could guess. Anyone can type eleven digits into a payment form;
guessing a symbol puts a stranger's money into a child's financial record.

**A QR code is a rendering, not data.** It encodes the symbol, the amount and the recipient
that already exist. Nothing stores it and nothing invalidates it.

**There is no card gateway.** The organization **collects**, but by bank API rather than
checkout: no card tokens, no disputes, no chargebacks, no processor reconciliation, and
**no `pending` or `failed` payment status** — a bank transfer the bank has reported does not
later fail. A refund is a second payment going the other way, never a reversal of the first.

**Unmatched money** — A transfer whose symbol resolves to nothing live: mistyped, belonging
to a cancelled event, already settled, or the wrong amount. It **waits for a person**. It is
never auto-applied by payer identity — *a parent with two children pays one amount* is the
normal case, not the edge case, and the fallback would be wrong on the common path
([D-076](decisions/round-06.md#d-076--money-that-cannot-be-matched-waits-for-a-person)).

---

## Communication

**Direct message** — One person to one person. **Everyone can send one**; there is no
permission for it.

**Broadcast** — The only messaging permission, and **an ordinary scoped one**: a grant like
any other. Held at the unit, `message.broadcast` reaches everyone; **the narrower reading is
a grant naming a group**, reaching that roster. There is **no global broadcast flag**: a
permission that has to be granted is one that can be given to some people and refused to
others, whereas the flag would be all-or-nothing and would leave a section leader choosing
between an organization-wide power and typing the same sentence twelve times. Whether
broadcast should ever be grantable on an item is messaging's open question, not the model's
([D-077](decisions/round-06.md#d-077--messaging-is-direct-by-default-broadcast-is-an-ordinary-scoped-permission-and-the-recipient-chooses-the-channel)).

**Delivery channel** — Email, push, or in-app, **chosen by the recipient**, not the sender.
The sender chooses *who*; the recipient chooses *how it arrives*. This is why the system is
the medium rather than a mail relay: a bounced email is a failed delivery on one channel,
not a lost message.

**Age is not a sender concept** — and it is not a *recipient* concept either. Nothing
restricts who may address a child; what stops a private message to a child from being
unnoticed is **mirroring**, and no check in the resolver ever looks at an age.

**Mirroring** — A copy of a direct message addressed to a minor, delivered to that minor's
guardians whose **right** is `view` or `write` — the three-value right of the guardianship
channel, not a level — fixed to that set **at the moment of sending**. Visibility, not
approval: nobody has to agree before the message is sent. A guardian at `none` receives
nothing, because `none` is the organization having already decided that this party sees
nothing about the child — and a minor whose guardians are *all* `none` is the same
alertable shape as a minor with no guardian at all, so it is reported together with it
([D-082](decisions/round-07-08.md#d-082--a-direct-message-to-a-minor-is-mirrored-to-the-minors-guardians)).

---

## Time

**Temporal row** — Any row with `valid_from` / `valid_to`. `valid_to IS NULL` means
"still true". All permission checks and history queries filter on these. The full pattern
is specified in [data-model/00-conventions.md](data-model/00-conventions.md).

**Point-in-time query** — A question of the form "who/what was true on date D?" — *"Who was
in the group `schuzka2026-1` on 1 June 1998?"*, *"Was this person a member when they
attended camp?"* These are first-class requirements, not an afterthought, because there are
four decades of history to preserve. The answer depends on **which named set** the question
is about, and there are only two kinds to be about: a **group** answers it from its dated
roster, and an **audience** cannot answer it at all — its expression is evaluated live, and
its one past is the audit trail. That includes a name typed straight into the expression: a
`PERSON(x)` leaf carries no dates of its own, so *"was she in this audience on 1 June 2024?"*
is a recomputation over audit payloads that expire after 24 months
([D-088](decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)).

**As-of vs audit time** — Two different times, both needed. **As-of** is the date the fact
was true about the world (a membership that ran 1990–2010). **Audit time** is when the row
was written in the system. A membership backdated during a 2026 data-entry session has
as-of 1990–2010 and audit time 2026. Do not conflate them.

---

## Roles in conversation (informal terms — not names in the model)

The words you and the organization will naturally use, and what they map to:

| Informal term | What it is in the model |
|---------------|------------------------|
| "child member" | a person with an open `membership` whose `birth_date` makes them a minor — **age is a fact about the person, not a kind of membership** |
| "counselor" / "leader" | an **office** held through `role_holder` — never a membership type, and **conferring nothing by itself**: authority comes from the grants that name `ROLE(counselors)` |
| "parent" / "caretaker" | party to an active `guardianship` row |
| "leader of the Thursday group" | there is no such thing: an office is held for the unit and has no scope column, so this is **a member of that group**, plus whatever a grant aimed at them or at it allows |
| "in the Thursday group" | an open `person_group_member` row in that `person_group` — **company, not authority** |
| "ex-member" | person with a `membership` whose `valid_to` has passed |
| "lapsed but can still renew" | `valid_to` passed, within the renewal window |
| "registered but not a member" | person with an `account` and no open `membership` — they may sign in and see their own data, but hold no member permissions |
| "they're allowed to attend" | a live **allow** grant naming `event.register_self`, aimed at them or at a set they belong to (a grant aimed at an **integration** is the third kind of grantee and answers for that integration alone, never for a person attending), **and no live deny anywhere** naming them — not a level, and nothing inherited from a unit that owns the event |
| "open to everyone" | a grant naming the seeded audience `everyone`, whose expression is the operand `EVERYONE` — or `all_members`, whose expression is `MEMBERS`. A bare name in an expression is **not** a reference to either: audiences are named only as `AUDIENCE(code)` |
| "the treasurer" | `role_holder` of `treasurer`, held **for the unit** — there is no narrower place to hold it, and holding it answers no permission question on its own |
| "put me in the Thursday group" | a `person_group_member` row **somebody else writes** under `person_group.member.manage`, which has **no self-scoped variant** — there is no self-service path and no permission with which to build one |
| "the kitchen crew" | a **`person_group`** if the answer is a list of people somebody keeps up by hand, dated and quotable years later; an **`audience`** if the answer is a sentence recomputed each time it is asked. *"Whom did this grant reach on 1 June 2024?"* is answerable for the first and not the second |
| "the permission group for the kitchen crew" | one or the other of the row above; an expression names a group through `GROUP(code)` and another audience through `AUDIENCE(code)` |
| "the old Pack 12 came back" | **there are no units to bring back.** The closest thing left is a **group** whose `name` repeats a dead one, and that is only a reused label: groups have no `code`, no succession and no rename history |
| "the organizers" | the event's own `event_organizer` roster, reached as `ORGANIZERS` on a grant scoped to that event — an appointment on the thing being run |

---

*Decisions behind this page: D-060, D-062, D-064, D-065, D-069, D-071, D-073, D-074, D-075, D-076, D-077, D-082, D-083, D-085, D-088, D-089, D-093, D-097, D-098, D-100, D-102, D-113, D-116, D-117.*
