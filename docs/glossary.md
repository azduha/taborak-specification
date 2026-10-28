# Glossary — Ubiquitous Language

Terms used consistently across every document in this folder. Where everyday
language is ambiguous, the definition here wins and the schema follows it.

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
else. In particular: no member status, no child/adult flag, no troop, no role, and
**no deceased flag** — the organization does not record death. What the organization
records *about* the human is not on this table at all: it is
[descriptive data](#personal-data), reached by the same permission as the rest of the
person record, because none of it is a different kind of object.

**Account** — Credentials and login state for a person. A person may have zero or
more accounts over their lifetime (e.g. a childhood account abandoned in 2010, a new
one created in 2024), **but at most one live one** — closed rows aside. Accounts are
never shared between people, not even between a parent and child.

**Account activation gate** — The rule that an account may not reach `active` while an
unresolved identity hypothesis names its person. This is what a colliding sign-up runs into:
a sign-up that *strong*-matches an existing person — exact legacy member number, or exact birth
date together with a normalized name, **never the fuzzy band** — raises a hypothesis. Its own rows are
created and stay `pending_verification`: **nothing is merged, nothing is linked, nothing is
activated.** The contact point the person typed survives as the credential it was offered as, and
`identity_reviewer` decides it with `person.merge`. The holding message confirms nothing, since
a sign-up form that can answer "yes, that person exists" is an existence oracle over a roster of
children; and a hypothesis that is blocking an account gets an age check that alerts, because a
stalled queue is no longer a data-quality problem but a specific person who cannot log in
([D-089](decisions/decision-log.md#d-089--one-live-account-a-colliding-sign-up-files-a-claim-and-creates-nothing)).
"I have a new e-mail address" is not this case and is not routed through it: `account_credential`
holds many credentials for one account.

**Contact point** — A single email address, phone number, or postal address belonging
to a person. Stored as many rows per person, not as columns, so that a person can have
five email addresses, or a new kind invented later, without a migration. Each has a
`type`, a `purpose`, and a verification timestamp.

**Identity hypothesis** — A *proposed* but unconfirmed link between two `person` rows
that may actually be the same human. Created during legacy import, by the nightly matcher,
when someone registers claiming a historical identity, or by a sign-up that strong-matches
a person who already exists. Confirming one triggers a merge; while one is unresolved it
also holds the account of any person it names out of `active` — see **account activation
gate**.

**Merge** — The act of declaring two person rows to be one human, and collapsing them.
Never a delete: the absorbed row survives as a tombstone pointing at the survivor, so
that historical foreign keys keep resolving. Always a human's decision (`person.merge`),
including at the highest score — and refused outright when the chosen survivor turns out,
on resolution, to be the person being absorbed.

**Merge chain** — What forms when a survivor is itself later absorbed. The pointer is **not
rewritten forward**: A→B→C stays a chain and `resolve_person()` walks it to the live row.
This is **decided, not provisional** — chains persist because reversing a merge would otherwise
be a reconstruction of facts nobody recorded, and flattening is closed off rather than merely
faster ([D-087](decisions/decision-log.md#d-087--merge-chains-stay-because-reversing-a-merge-is-a-supported-operation)).
Two rules come with them, neither on the read: a cycle is impossible because the *merge* is
refused, never because a hop limit gave up; and a chain longer than **three hops is reported**,
which is a statement about the matcher's queue, not about the row.

**Unmerge** — Reversing a merge a human approved. The tombstone comes off, rows created *before*
the merge go back to the revived person, and rows created *inside* the window are flagged for a
human rather than split by a rule — every `access_grant` from that window flagged, not guessed.
**The merge is reversible; the merged window is not**: what two people did while they were one row
stays one row's history, because the record cannot separate who did it
([D-087](decisions/decision-log.md#d-087--merge-chains-stay-because-reversing-a-merge-is-a-supported-operation)).
No permission of its own — undoing an identity correction is the same act as making one, so it is
`person.merge`.

**Membership export** — **One of the two files the legacy corpus actually is**, and neither of them is a
roster. A row says: a person, a birth date, and **the period they were a member of the organization**
([D-092](decisions/decision-log.md#d-092--the-corpus-is-people-and-events-and-it-names-no-units)). A people
batch turns it into `person` rows and **bounded** `membership` rows — both ends dated,
`data_confidence = 'low'`, batch id set — each bringing its root-unit participation row with it, and
**no fee obligation of any kind**
([D-093](decisions/decision-log.md#d-093--the-one-off-import-may-create-memberships-both-ends-dated)).
**It names no sub-unit**, so it answers neither *"who was in Pack 12 in 2011"* nor *"were they a cub or a
rover"*, and no `org_unit` is created from it.

**Attendance export** — The other file: events, and which people came. It becomes `event` rows **owned by
the root unit** — the corpus names no unit to own them, and inventing one to hold forty years of
tent-weeks would put thousands of people inside a unit nobody chose
([D-094](decisions/decision-log.md#d-094--the-root-unit-owns-every-imported-event)) — with one
`event_registration` per attendee at `attending` and `was_present = true`, and **no `not_attending` rows**,
because an absence row would say the system asked someone who was never asked. **Attendance never becomes
a membership.**

---

## Personal data

Everything the system knows about a person once you subtract what they are *called* and
*counted as*. The module is [domain/08-person-data.md](domain/08-person-data.md), the tables are
[data-model/09-attributes.md](data-model/09-attributes.md), and the reasoning is
[D-083](decisions/decision-log.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data),
[D-084](decisions/decision-log.md#d-084--descriptive-data-is-organization-defined-at-runtime) and
[D-085](decisions/decision-log.md#d-085--the-identity-machinery-stays-structured-the-boundary-is-rules-not-sensitivity).

**Descriptive data** — **Everything the system holds about a person other than their name, their
gender and their age: one class of data, with no privileged corner inside it.** Allergies,
medication, insurance numbers, languages, measurements, clothing sizes, dietary habits, a
grandparent's phone manner — the same kind of fact, held in fields rather than files, none of it a
different kind of object from any other, and all of it reached by the permission that already reads
the person. The term exists to rule a category *out*: there is no sensitive sub-record with its own
codes, which is what
[D-083](decisions/decision-log.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)
declined on the merits rather than failed to build. Its cost is stated there and in
[domain/08 §4](domain/08-person-data.md#4-what-was-refused-and-what-it-cost), and it is the reason
`person.view` is graded in the catalog's top tier.

**Attribute definition** — One thing the organization has decided to collect: a `code`, a label, a
description of what belongs in the field, a value type, and whether several values may be current at
once. The **type draws the form and raises the warning; it never refuses a save** a human insists on
— `2019` recorded as the year of a checkup is a truer record than an empty field behind a validation
error. Creating, renaming, merging or retiring a definition is `attribute.define`; recording a value
against one needs nothing beyond `person.edit`.

**Person attribute** — The value one person currently has for one code. **Overwritten in place:**
the row is the organization's present belief, and the sequence of earlier beliefs lives in the audit
trail, **values included, for 24 months** — logged on the same terms as a contact point or a note, because a list of
person fields whose values must not be logged would be exactly the privileged corner
[D-083](decisions/decision-log.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)
deleted, and would leave nothing behind for an overwritten value. What guards the trail is who may
read it, not what it omits — **and it now omits, on a clock**: those logged values are emptied 24
months after they were written (see **payload reduction**), so the trail is the record of *what
changed, who did it and when* for the life of the system and the record of the *values* for two
years. The honest name for the whole stack is therefore **no long history**, not merely *no temporal
columns*: the value lives in one overwritten row, the copy of it depends on a write path remembering
to log, and the copy ages out. If a case ever needs the long version, the fix is temporal columns on
the value — [D-085](decisions/decision-log.md#d-085--the-identity-machinery-stays-structured-the-boundary-is-rules-not-sensitivity)
reversed — and not a longer trail. No `valid_from` / `valid_to`, deliberately
([data-model/09 §3](data-model/09-attributes.md#3-person_attribute--a-value-one-person-has)).

**Proposed code** — A definition that came into existence because somebody recorded a value against
a code that did not exist. It waits in the curation queue: kept out of data entry forms and reports,
yet **readable by anyone already entitled to read the person**, because the organization's data
quality problem is not the family's confidentiality problem. It is where an improvised need at 23:00
goes instead of into a notes box that nobody will read again — **improvised by a person at a desk**,
which is the whole meaning. It is emphatically *not* "whatever the legacy import did not understand":
the codes a batch's column→code map names arrive `live`, because a curator read that map as one object
before the batch applied, and several hundred proposals landing on day one would make this queue's age
signal meaningless before it had ever meant anything
([D-090](decisions/decision-log.md#d-090--the-legacy-corpus-is-thousands-of-roster-rows-with-numbers-and-no-money)).

**Retired code** — A definition taken out of data entry and left alone everywhere else: readable,
reportable, revivable, its values untouched. **Deleting a label must never delete the facts filed
under it**, or the badly-named label is never retired and the vocabulary accretes instead of being
curated. Redaction is the opposite operation: retiring keeps the values, erasing a person deletes
them, immediately and whatever their age. It used to be called *the only eraser*; there is now a
second one — **payload reduction**, below — and the distinction is that redaction answers to a
person and is absolute, while reduction answers to a calendar and is bounded.

**Payload reduction** — Emptying the `old_values` / `new_values` out of an audit row **24 months
after it was written**, leaving everything else standing: actor, on-behalf-of, operation, table,
record id, changed fields, transaction, session, channel. The trail goes on answering *who changed
this row, when, and were they allowed to* for the life of the system, and stops answering *and to
what* after two years; twelve months is the floor the window may be set to. **Not redaction**, which
is a named person's erasure, immediate and absolute, and reaches payloads of any age; **not an
import revert**, which deletes the rows a batch created. Reduction is the one case in this design
that deliberately unwrites *later* than the write, so its failure mode is not running at all — hence
a scheduled job with a check that alerts on any row past its window still carrying a payload
([D-088](decisions/decision-log.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)).

**The two clocks** — The accounting skeleton (`membership`, `fee_obligation`, `payment`, and the
anonymised `person` row an erasure leaves behind) has **no clock at all**, now justified as the
organization's own history rather than merely unchallenged. *Assumption:* that this indefinite
retention of rows about a named person has a legal basis — organizational history plus accounting
obligations, against a redacted person row that keeps the skeleton non-identifying — is unverified,
and a decision log is not the document that grants it. The audit trail runs the opposite direction: rows
forever, payloads for 24 months. Erasure sits outside both, immediate and absolute. The same window
is *proposed* for `access_log` and is not yet confirmed
([D-088](decisions/decision-log.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)).

**Curation** — Keeping the vocabulary meaning one thing: merging near-duplicates, promoting or
discarding proposals, retiring codes nobody uses, and writing the description that stops one code
meaning four things to four people. It is `attribute.define` plus somebody who reads what they are
given, and the documents treat it as a job rather than an outcome — an open vocabulary left
unwatched decays into `allergy`, `Allergy`, `alergie` and `allergies (2)`, after which the layer
still stores everything and answers nothing.

*Not to be confused with* **identity**, which stays structured in its own tables: a fact keeps a
table of its own when there is a rule about it that an open layer physically cannot hold — one
primary postal contact, one current name, a birth number that may not repeat. The boundary is that
test, not sensitivity
([domain/08 §1](domain/08-person-data.md#the-three-exceptions-and-why-they-are-exceptions)).

---

## Organization

**Org unit** — Any node in the organization's structural hierarchy. Two kinds, and the
difference is load-bearing:

- **The organization itself** — the single root unit. There is exactly one, and it is where
  people are members.
- **Sub-units** — weekly meeting groups, packs, sections, teams. Created by the organization
  or by other sub-units, nested to **arbitrary depth**. They run themselves: their own
  events, their own local leadership, their own roster.

There is no fixed ladder of levels. Types are configurable rows, not a hardcoded enum,
because the vocabulary will change over decades while the data must not.

**Unit type** — A category of org unit (`organization`, `pack`, `group`, `section`, …).
Defines whether units of that type may nest, and inside which other types. Most types carry
**no nesting rules at all**, which leaves them unconstrained — the organization can invent a
kind of group and nest it wherever it likes without asking the schema's permission.

**Position** — A defined role within a unit that people can occupy:
`scoutmaster`, `assistant_leader`, `unit_treasurer`, `quartermaster`. A position is a
*slot*; it exists whether or not anyone fills it.

**Multiple people may occupy the same position at the same time.** The schema makes no
assumption of single occupancy. Some positions are organizationally limited to one holder
at a time (`position.max_holders`), but that is a per-position *limit*, not a structural
rule — and it is a limit the position declares about itself, never one imposed from
outside the unit.

**Position assignment** — The period during which a specific person occupies a specific
position in a specific unit. Carries a start, an optional end, and a primary flag. Several
assignments may be open against the same position simultaneously.

---

## Membership

**Membership** — The period during which a person is a member **of the organization**.
Holds `valid_from`, `valid_to` (null = open/current), and a status in an approval workflow.
A person accumulates multiple memberships over time; they never overwrite one another.

**There is exactly one membership, and it is ageless.** Membership does not distinguish
children from adults, has no age ceiling, and does not end because a person got older. Being
a counselor or a leader is a **position**, never a membership type.

**Membership type** — A table kept for the future, currently holding **one row**: `member`.
It survives as a table rather than collapsing into a constant so that a second kind of
membership (a supporting or honorary one) would be a data change rather than a migration.
The fee is flat and per person, so the type does not affect pricing either.

**Participation** — The period during which a person takes part in **one sub-unit**. This is
what a pack's roster is. Distinct from membership in every way: a person holds exactly one
membership and any number of participations, participation is free, and it ends when the
person stops attending rather than when a fee is unpaid. A participation row for the root
unit is created alongside each membership, so "everyone in unit X" is one uniform query.
**Nobody writes themselves into a sub-unit**: a counselor does it, under
`unit_participation.manage` at that unit, which **has no self-scoped variant and none will be added** —
the same holds for appointment, and no unit type carries a restriction about who may belong to it
([D-095](decisions/decision-log.md#d-095--units-carry-no-restrictions-joining-one-is-somebody-elses-act)).
**What the legacy corpus writes here changed in round 9.** This entry used to say that an imported
historical row is *always* a participation and *never* a membership, because the corpus carries no payment
evidence ([D-090](decisions/decision-log.md#d-090--the-legacy-corpus-is-thousands-of-roster-rows-with-numbers-and-no-money))
— and it turned out the people export states membership periods directly, so no payment evidence was ever
needed to read one
([D-092](decisions/decision-log.md#d-092--the-corpus-is-people-and-events-and-it-names-no-units),
[D-093](decisions/decision-log.md#d-093--the-one-off-import-may-create-memberships-both-ends-dated)).
**What still never happens**: a participation row for a sub-unit created by the import — the corpus names
no units — and a membership inferred from attendance. The rule that replaced the withdrawn one is one
sentence: **an imported membership is bounded at both ends, always.**

**Membership request** — A person's application to become a member. Separate from the
membership itself, because a request has its own lifecycle (submitted, under review,
rejected, withdrawn) and can be rejected without ever producing a membership. **Nothing
gates a request except identity and payment** — there is no checklist to satisfy.

**Lapse** — A membership ending because the yearly fee was not paid or the person withdrew.
Distinct from termination for cause, which requires a reason code. **A lapsed person is not
a member and holds no member permissions**, though a renewal window lets them rejoin without
re-applying.

**Renewal window** — The fixed period after a membership expires during which payment
restores it **without re-applying**, and — importantly — opens the new period *at the expiry
date*, so the record shows continuous coverage and the person is not misclassified as a
returning member. Tracked as **dates, not a status**: during the window the person is simply
expired.

**Returning member** — A person whose new membership follows a gap. The system detects
this rather than treating them as new. This is the case you described: 1990–2010, gap,
2024–present.

---

## Relationships

**Guardianship** — A period during which one person is responsible for another. Directional:
guardian → dependent. Carries relationship kind (`parent`, `legal_guardian`, `foster_parent`,
`step_parent`, `grandparent`, `sibling`, `other`) and an end date that **a person sets**.
**Not a birthday**: the system takes no position on majority, and no job ends one
([D-069](decisions/decision-log.md#d-069--guardianship-ends-when-a-person-ends-it-the-system-takes-no-position-on-majority)).

**Party to a guardianship** — The guardian and the subject, both. **They, and not staff, run the
arrangement:** either may end it, a guardian may add another guardian, and no request has to go
through the organization
([D-073](decisions/decision-log.md#d-073--guardianship-is-administered-by-its-own-parties-not-by-staff)).
Staff hold the same powers and are *a* route, never *the* route. This is scope authority applied to
a household: authority over a nested thing originates at that thing.

**Guardian's right** — **One of exactly three values on the guardianship row: `none`, `view`, or
`write`.** Nothing more granular exists
([D-074](decisions/decision-log.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular)).
They rank onto the same ladder as every other grant — 0, 10, 20 — so a guardian is not a second
authorization model.

**Being a guardian still grants nothing by itself**; `none` is a real value and the common starting
point for anything the guardian did not assert themselves. What D-074 gives up in exchange for the
short vocabulary is recorded in the catalog: **it is not possible to say "read everything except the
medical record."**

**That sentence is not waiting on a mechanism, and the right level has not become softer for it.**
[D-083](decisions/decision-log.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)
was put the case the sentence was invented for — a parent keeping access to everything about their
child except the medical file, by court order — and **declined it on the merits**: there is no
medical record inside the person record to be excepted from, because everything other than name,
gender and age is [descriptive data](#personal-data) of one class. So the right level is what it
always was, `none`, `view` or `write`, applied to the record **whole** — and the thing that was
given up is not a half-built feature but an arrangement the organization decided not to want.

*Not to be confused with* **guardianship permission**, which was the deleted eighteen-code list
(`dependent.profile.view`, `dependent.medical.admin`, …). Those codes are gone; do not write them
into a role, a query, or a screen.

**Household** — **No longer a thing in this system** ([D-057](decisions/decision-log.md#d-057--household-is-removed)).
A person's address is a `person_contact` row of type `postal`, which is temporal like any
other contact. Two people at one address are related by a query, not by a table. The word is
kept here only to answer "where did the household go?": shared address never granted access,
and still does not.

**Acting on behalf** — Performing an operation as another person, under that guardianship row's
right level (`view` to read it, `write` to change it). Every such operation records both the acting
person and the subject person.

---

## Authorization

**Permission** — The atomic unit of authority: a coded capability such as
`membership.request.approve` or `unit.manage`. Permissions are the only things the
authorization layer actually checks.

**Role** — A named bundle of permissions (`unit_leader`, `registrar`, `treasurer`,
`system_admin`). Roles exist so that operationally meaningful sets can be assigned and
reviewed as a unit.

**Role assignment** — The period during which a person holds a role. Carries a **scope**:
organization-wide, or limited to a specific org unit. Same mechanism for both, because
"treasurer of Pack 12" and "treasurer of the organization" differ only in scope.

**Scope authority** — The principle that **authority over a unit originates at that unit
and cannot be claimed from outside it.** A parent unit — including the organization itself
— can never decide permissions over a nested unit. Coverage of subordinate units exists
only where the unit itself has granted it, as an explicit `scope_exposure` row. The single
exception is `system_admin`. See
[domain/06-authorization-model.md](domain/06-authorization-model.md#2-scope-authority--no-downward-inheritance).

**Access grant** — The item-scoped layer you asked for: a period during which a person
may act on one specific record — this event, this chat thread, this document, this unit's
data — with a level (`revoked` < `view` < `contribute` < `manage` < `admin`). This is what
"per-item permission" means in this design.

**It may also target an audience** ([D-042](decisions/decision-log.md#d-042--grants-may-target-audiences-not-only-individuals)),
which is how "open this event to everyone" or "to the whole pack" is expressed. A grant
names either a person or an audience, never both.

**Audience** — **The organization's word is *permission group*; the table is `audience`, and both names
mean one thing.** A grant target that stands for a set of people rather than one, filled by **any
combination of three optional arms**: a **filling rule**, a hand-kept list of people, and the groups it
**includes**. Membership on a date is the **union** of whichever arms the group has
([D-091](decisions/decision-log.md#d-091--a-permission-group-is-a-rule-and-a-list-at-once-and-a-rule-may-name-another-group)).
The old split into **built-in audiences** (rules the resolver evaluates) and **named groups** (stored
lists), with a group required to be one or the other, is **deleted** — `audience.kind` went, and with it
the rule that a member row on a rule-filled group "would look authoritative". The shipped rules are still
the part that carries the design — `everyone`, `all_members`, the guardians of a given person, the
participants of a given unit, the leaders of a given unit — because a new pack member automatically
receives what the pack was granted, with no rows to maintain and no stale-group problem; what D-091 adds
is that a hand-built group may *borrow* a rule instead of copying what it produced. **The cost is that a
grant's reach stops being visible in the row**: whoever edits a grant has to be shown the expanded set of
people it actually reaches, not the group's name
([domain/06-authorization-model.md §6.2](domain/06-authorization-model.md#62-audiences--a-rule-a-list-and-other-groups)).

**Filling rule** — The rule arm of a group: a resolver plus a scope parameter, evaluated at check time —
*"everyone with membership"*, *"the leaders of this unit"*, the derived `unit_leaders` that
`position.is_leadership` feeds ([D-091](decisions/decision-log.md#d-091--a-permission-group-is-a-rule-and-a-list-at-once-and-a-rule-may-name-another-group)).
A rule does not rot the way a list does, and it stops covering a person the day the fact underneath ends
— which is precisely why **an appointment creates no role assignment**: the derivation belongs on a rule,
not on a copy that has to be found and revoked later
([domain/04-organization-structure.md §4](domain/04-organization-structure.md#4-positions)). **A rule
fills groups, not roles**: whether a *role* may be held by a rule the way a group is is open as
[F-12](open-questions.md#f-12--may-a-role-be-held-by-a-rule-as-an-audience-is), because `role_assignment`
is the record of who held which office and a derived holder list cannot answer that.

**Inclusion (of a group)** — A stored edge putting one group inside another. This was refused outright
(*"they do not nest"*) and the refusal is withdrawn: **a cycle is refused when the edge is saved**, because
inclusion edges are rows and a write can walk them, so nothing in the read path gets a hop limit or a
guess ([D-091](decisions/decision-log.md#d-091--a-permission-group-is-a-rule-and-a-list-at-once-and-a-rule-may-name-another-group)).
Chain length has a bound stored as a configuration parameter, and a group that cannot be evaluated
**denies** — it reaches nobody. Inclusion is also the arm that makes reach non-obvious: a group may include
one that includes `everyone`, which was already grantable directly and is now grantable by three edits and
a save.

**Membership gate** — The rule that authority held through a role is honoured **only while
the holder has a current membership**. Two carve-outs: **guardianship** (a legal
relationship, not a membership) and roles marked `requires_membership = false`
(appointed counselors and local leaders, who must be able to serve regardless of their own
fee). Ownership is exempt too, so a lapse cannot lock someone out of the screen they renew
on. See [domain/06-authorization-model.md](domain/06-authorization-model.md#6-the-resolver).

**Locality** — The rule that **a grant on the specific item always beats a grant from a
broader scope.** A per-event grant outranks a unit-scoped one, which outranks an
organization-wide one. Locality decides between competing *allows* only — a **deny wins
over everything, at any scope.** See
[domain/06-authorization-model.md](domain/06-authorization-model.md#7-precedence).

**Scope** — What a grant applies to. Either an org unit, a concrete item (via
`scope_type` + `scope_id`), or the whole organization.

**`admin`** — **Was ambiguous three ways; two deletions later, two remain.** Say which you mean:

| Meaning | What it does | Status |
|---|---|---|
| **Grant level** — `access_level.admin`, rank 40 | *How much* authority a grant carries. `revoked` < `view` < `contribute` < `manage` < `admin`, compared by **integer rank, never by string**. A check asks "at least level X?" | **Real, untouched** |
| **Resource wildcard** — `person.admin`, `event.admin` | A permission code implying every sibling capability on that resource, matched by prefix in the resolver | **Deleted** — all sixteen codes and the prefix match ([D-068](decisions/decision-log.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle)) |
| **Edit action** — `dependent.medical.admin` | Means "edit", paired against `.view` inside a sub-resource. Implies nothing | **Deleted** — with the whole `dependent.*` namespace ([D-074](decisions/decision-log.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular)) |

What survives of "can do everything": **`system.admin`** (the only wildcard permission, held
through a role, never an item grant) and **roles** — a bundle the organization composes, which
is where "someone who can do everything about events" now lives, written out as thirteen rows
rather than implied by a resolver rule.

**Scope exposure** — An explicit row by which a unit accepts one named **role assignment** as
authority over itself. This is the *only* way authority crosses a unit boundary downward, and it
is created at the subordinate unit's own level, never assumed from the hierarchy. It names an
assignment — a particular person in a particular role for a particular period — which is why a
unit is approving a person rather than opening a door any future holder may walk through.
**An exposure extends that assignment and nothing else: not the role, and never a direct access
grant** ([D-078](decisions/decision-log.md#d-078--an-exposure-extends-an-assignment-never-a-direct-grant)).
See [data-model/05-authorization.md](data-model/05-authorization.md#5-scope_exposure--how-a-unit-delegates-upward).

**Channel** — Which of the resolver's four questions answers a check: ownership, guardianship,
item grants, roles, with an absolute deny in front of all of them. **How a check reaches a channel
changed in round 6 and it is easy to state backwards.** It used to be the permission's namespace —
a code beginning `dependent.` went to guardianship. That silently skipped every guardian act whose
code was an ordinary one, like a parent editing their child's address under `person.address.edit`.
Now guardianship is reached **when the person the act is about is not the person performing it**,
which nobody has to remember, because the shape of the call decides
([D-079](decisions/decision-log.md#d-079--the-guardianship-channel-is-entered-by-shape-not-by-permission-name)).
**Corollary, and the part people get wrong:** the guardianship channel can only say *yes*. When
there is no guardianship, or the right is too low, it says nothing and the person's own roles are
still tried — otherwise a parent who is also the event registrar would be blocked from the roster
by their own `view` over their child. Prohibitions are not made here; they are explicit denies.

**Effective permission** — The union of everything a person may do right now, computed
from role assignments and access grants that are currently valid. Never stored, always
derived, so it cannot drift out of sync with the grants that produce it.

**Delegation** — Temporarily granting someone your authority (e.g. a leader going on
leave). Modeled as an access grant with an explicit end date and a
`delegated_from` reference, so the provenance of authority is visible.

---

## Events

**Event** — A dated occasion that people **register** for: a camp, a trip, a hike, a
jamboree. It belongs to **exactly one unit**, has a start and an end, an optional capacity,
an optional fee, and a set of **organizers**. It has **no status column** — visibility *is*
the permission model, and cancellation is a recorded fact rather than a state
([D-064](decisions/decision-log.md#d-064--there-is-no-event-status-visibility-is-the-permission-model)).

**A weekly meeting is not an event.** It is **participation**. A Thursday group meeting
forty times a year is one `unit_participation` row, not forty events — so there is no
recurrence, no series, and no occurrence table
([D-058](decisions/decision-log.md#d-058--an-event-is-a-dated-occasion-owned-by-exactly-one-unit)).
This boundary is deliberate and easy to miss: "was Jan at the meeting on 14 March?" is not
answerable from the events module.

**Organizer** — Someone **running** an event. A roster entry on the event, with an optional
label (`'lead'`, `'cook'`, `'driver'`) and an order — **not** an `access_grant`
([D-062](decisions/decision-log.md#d-062--organizers-are-appointed-on-the-event-not-granted)).
It is the event-scoped analogue of a **position assignment**: an appointment on the thing
being run, not a permission bundle. Authority to *act* on the event comes from the owning
unit's roles, which reach the unit's own events because an event is an **artifact** of its
unit rather than a child of it
([D-063](decisions/decision-log.md#d-063--an-event-is-an-artifact-of-its-unit-not-a-child-of-it)).

**Registration** — One person's answer about one event: `attending`, or `not_attending`.
**"Unanswered" is not a value** — it is the absence of a registration row, so "who has not
replied yet?" is the eligible set minus the registered set
([D-059](decisions/decision-log.md#d-059--unanswered-is-the-absence-of-a-row-a-registration-stores-two-values)).

**Eligibility** — Who may register. This is **capability**, not a rule engine:
`event.register_self` requires `contribute` on the event, and opening a camp to members is
**one** `access_grant` naming an audience. An age-restricted camp is a camp opened to a
unit's participants
([D-060](decisions/decision-log.md#d-060--eligibility-is-capability-there-is-no-separate-rule-engine)).

**Waitlist** — What happens when a full event gets a self-service registration: the person is
written down and ordered, never refused. **Organizers may exceed capacity** outright, and the
overrun is reported rather than prevented — the leader who knows there are two spare tents is
trusted ([D-065](decisions/decision-log.md#d-065--capacity-is-a-waitlist-threshold-and-organizers-may-exceed-it)).

**Presence** — Whether someone actually turned up, marked by an organizer after the fact.
Three-valued: `NULL` (no register taken), `true`, `false`. For a camp this is **the record of
who was in the organization's care**, and it cannot be reconstructed from registrations
([D-067](decisions/decision-log.md#d-067--presence-is-a-three-valued-fact-on-the-registration)).
Not the same as registration — a no-show is a registration with `was_present = false`.

---

## Money

**Payment request** — A liability rendered payable: an amount, a recipient account, a start, and
an optional expiry. **The request, not the payment, is the entity the finance module is built
around**, because it is the only thing that connects "we expect money" to "money arrived"
([D-075](decisions/decision-log.md#d-075--money-arrives-from-a-bank-api-a-payment-is-requested-by-variable-symbol-and-qr-code)).
It is not an invoice; the organization may also owe people invoices, which is still open.

**Variable symbol** — The number a payer types into their bank, and the number the bank reports
back against the money. **Unique across every symbol ever issued, not merely across live ones**,
and taken from a sequence — never derived from a birth date, a member number, or anything else a
stranger could guess. Anyone can type eleven digits into a payment form; guessing a symbol puts a
stranger's money into a child's financial record.

**A QR code is a rendering, not data.** It encodes the symbol, the amount and the recipient that
already exist. Nothing stores it and nothing invalidates it.

**There is no card gateway.** The organization **collects**, but by bank API rather than checkout:
no card tokens, no disputes, no chargebacks, no processor reconciliation, and **no `pending` or
`failed` payment status** — a bank transfer the bank has reported does not later fail. A refund is
a second payment going the other way, never a reversal of the first.

**Unmatched money** — A transfer whose symbol resolves to nothing live: mistyped, belonging to a
cancelled event, already settled, or the wrong amount. It **waits for a person**
([D-076](decisions/decision-log.md#d-076--money-that-cannot-be-matched-waits-for-a-person)). It is
never auto-applied by payer identity — *a parent with two children pays one amount* is the normal
case, not the edge case, and the fallback would be wrong on the common path.

## Communication

**Direct message** — One person to one person. **Everyone can send one**; there is no permission for
it ([D-077](decisions/decision-log.md#d-077--messaging-is-direct-by-default-broadcast-is-an-ordinary-scoped-permission-and-the-recipient-chooses-the-channel)).

**Broadcast** — The only messaging permission, and **an ordinary scoped one**: granted on a unit it
reaches that unit, granted organization-wide it reaches everyone. There is deliberately no global
broadcast flag, because the alternative leaves a pack leader choosing between an organization-wide
power and typing the same sentence twelve times.

**Delivery channel** — Email, push, or in-app, **chosen by the recipient**, not the sender. The
sender chooses *who*; the recipient chooses *how it arrives*. This is why the system is the medium
rather than a mail relay: a bounced email is a failed delivery on one channel, not a lost message.

**Age is not a sender concept** — and it is not a *recipient* concept either, which is the part worth
saying out loud. Nothing restricts who may address a child
([D-077](decisions/decision-log.md#d-077--messaging-is-direct-by-default-broadcast-is-an-ordinary-scoped-permission-and-the-recipient-chooses-the-channel));
what stops a private message to a child from being unnoticed is
**mirroring** ([D-082](decisions/decision-log.md#d-082--a-direct-message-to-a-minor-is-mirrored-to-the-minors-guardians)):
the guardians get a copy, the sender is told before sending that they will, and no check in the
resolver ever looks at an age.

**Mirroring** — A copy of a direct message addressed to a minor, delivered to that minor's guardians
whose right level is `view` or `write`, fixed to that set **at the moment of sending**. Visibility,
not approval: nobody has to agree before the message is sent. A guardian at `none` receives nothing,
because `none` is the organization having already decided that this party sees nothing about the
child — and a minor whose guardians are *all* `none` is the same alertable shape as a minor with no
guardian at all, so it is reported together with it.

## Time

**Temporal row** — Any row with `valid_from` / `valid_to`. `valid_to IS NULL` means
"still true". All permission checks and history queries filter on these. The full
pattern is specified in [data-model/00-conventions.md](data-model/00-conventions.md).

**Point-in-time query** — A question of the form "who/what was true on date D?" —
*"Who was in Pack 12 on 1 June 1998?"*, *"Was this person a member when they attended
camp?"* These are first-class requirements, not an afterthought, because you have four
decades of history to preserve.

**As-of vs audit time** — Two different times, both needed. **As-of** is the date the
fact was true about the world (a membership that ran 1990–2010). **Audit time** is when
the row was written in the system. A membership backdated during a 2026 data-entry
session has as-of 1990–2010 and audit time 2026. Do not conflate them.

---

## Roles in conversation (informal terms — not names in the model)

The words you and the organization will naturally use, and what they map to:

| Informal term | What it is in the model |
|---------------|------------------------|
| "child member" | a person with an open `membership` whose `birth_date` makes them a minor — **age is a fact about the person, not a kind of membership** |
| "counselor" / "leader" | a `position_assignment` held by a member — **never a membership type** |
| "parent" / "caretaker" | party to an active `guardianship` row |
| "leader of the Thursday group" | `role_assignment` of a leadership role, scoped to that `org_unit` |
| "in the Thursday group" | an open `unit_participation` row for that sub-unit |
| "ex-member" | person with a `membership` whose `valid_to` has passed |
| "lapsed but can still renew" | `valid_to` passed, within the renewal window |
| "registered but not a member" | person with an `account` and no open `membership` — they may sign in and see their own data, but hold no member permissions |
| "they're allowed to attend" | `access_grant` on that event at level `view` or above, naming them **or an audience they belong to** |
| "open to everyone" | an `access_grant` whose audience is the built-in `everyone` |
| "the treasurer" | `role_assignment` of `treasurer`, scope = org or unit |
| "put me in Pack 12" | a `unit_participation` row **somebody else writes** — below the root there is no self-service path and no self-scoped permission to build one with (D-095) |
| "the permission group for the kitchen crew" | an `audience` row — **one thing**, filled by a rule, a hand-kept list, other groups, or all three at once |
| "the old Pack 12 came back" | a **new** `org_unit` whose `code` happens to equal a dead one; the continuity is an `org_unit_relationship` saying `successor_of`, written by a person — or there is no continuity, only a reused label (D-096) |
