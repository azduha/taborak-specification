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
roster. A row says: a person, a birth date, and **the period they were a member of the unit**
([D-092](decisions/decision-log.md#d-092--the-corpus-is-people-and-events-and-it-names-no-units)). A people
batch turns it into `person` rows and **bounded** `membership` rows — both ends dated,
`data_confidence = 'low'`, batch id set — and **no fee obligation of any kind**
([D-093](decisions/decision-log.md#d-093--the-one-off-import-may-create-memberships-both-ends-dated)).
~~Each bringing its root-unit participation row with it~~ — **withdrawn by
[D-097](decisions/decision-log.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)**, which
deleted the table those rows lived in; the import owes participation rows to nothing. **It names no group
either**, so it answers neither *"who was in the Thursday group in 2011"* nor *"were they a child or a
rover"*, and nothing is created in `person_group` from it: a corpus that names no groups means every roster
row is typed by a person, which is also the only way one can be true
([D-098](decisions/decision-log.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority)).

**Attendance export** — The other file: events, and which people came. It becomes `event` rows **with no
owner** — ~~owned by the root unit~~, **withdrawn by
[D-102](decisions/decision-log.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)**,
which deleted the owner column outright and
[D-094](decisions/decision-log.md#d-094--the-root-unit-owns-every-imported-event)'s rule with it: there is
no column left for an imported event to have — with one `event_registration` per attendee at `attending` and
`was_present = true`, and **no `not_attending` rows**, because an absence row would say the system asked
someone who was never asked. **Attendance never becomes a membership**, and it never becomes a group roster
either: attendance is read through the `ATTENDED` and `PLACED` selectors, and no rows are written into
`person_group_member` from it.

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

**The unit** — There is exactly one, and it is the organization. It is **a scope, not a row**: no table,
no id, no parent, no type, no name history, no path
([D-097](decisions/decision-log.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)). In
`grant_scope_type` its code is `unit` — the one row there with `is_item_scoped = false` — and a grant
written at the unit carries no `scope_id`. Say **the unit**: not "the root unit", not "the organization
unit", not "org". There is no second unit for the word *root* to distinguish this one from, and a name that
implies a second one is how the hierarchy creeps back into a sentence. Membership, a role, and a grant at
non-item scope are all held *at the unit*, and a grant at it reaches **every item of every type**
([D-099](decisions/decision-log.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)).

~~**Org unit** — Any node in the organization's structural hierarchy, of two kinds, and the difference
was load-bearing: the single **root unit**, where people were members, and **sub-units** beneath it —
weekly meeting groups, packs, sections, teams — created by the organization or by other sub-units, nested to
arbitrary depth, each running its own events, its own local leadership and its own roster.~~ **Deleted by
[D-097](decisions/decision-log.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)**, which
also deleted `org_unit_type`, `org_unit_type_rule`, `org_unit_name`, `org_unit_relationship`,
`unit_participation`, `scope_exposure`, `unit_ancestors()` and `unit_descendants()`. **Why it existed:** a
hierarchy is how a system says *which body a piece of authority belongs to*, and the type vocabulary existed
because that vocabulary changes over decades while the data must not
([D-054](decisions/decision-log.md#d-054--the-sub-unit-vocabulary-is-not-seeded-the-organization-defines-its-own-types)).
**Why the reason stopped applying:** [D-092](decisions/decision-log.md#d-092--the-corpus-is-people-and-events-and-it-names-no-units)
established that the legacy corpus names no units, and
[D-095](decisions/decision-log.md#d-095--units-carry-no-restrictions-joining-one-is-somebody-elses-act)
that a unit restricted nothing — a structure that describes nothing imported and restricts nothing carries
no information. **What is genuinely lost, said once and not argued away:** the unit as a *locus of
accountability* for a child's records (access to a body's children used to have to be granted **by that
body**, which is [D-031](decisions/decision-log.md#d-031--no-downward-inheritance-of-authority-scope_exposure-is-the-only-crossing)'s
property and nothing in the remaining model reproduces it); restructuring as a recorded event — splits,
mergers and successions are gone; and every per-unit report, because there is one unit to report on.
**Two-way door: no.** This is a deleted dimension, not a flag.

**Unit type** — ~~A category of org unit (`organization`, `pack`, `group`, `section`, …), defining whether
units of that type may nest and inside which others, and kept as runtime rows rather than an enum because
the words change while the data must not.~~ **Deleted by D-097**, with the seven-step nesting check,
`is_leaf`, `max_depth`, and D-054's whole argument about not guessing words. **The words `pack`, `troop` and
`section` are now illustration of nothing in particular** — where these documents need a set of people they
say **group**.

**Group** — **A `person_group`: a named set of people with explicitly stated, dated members and a lifetime
of its own.** A `name`, a `description`, `valid_from` / `valid_to` and the audit columns; its roster is
`person_group_member`(person, **`valid_from`, `valid_to`**, who wrote it, note), dated rows that may not
overlap **counted over all rows**, half-open
([D-098](decisions/decision-log.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority)).
**Company, not a body**: the Thursday group, the kitchen crew, this year's camp staff — in the
organization's own words *"a temporary set of members that do e.g. events together"*. What a group is
**not**, in one list, because this is the part the previous design got wrong: no parent and no children, no
type and no vocabulary of types, no `code`, no path, no nesting rules, no rename history, no split or
merger edge, no leadership of its own, **no roles**, and no fee. **Being in a group authorizes nothing** —
`person_group.member.manage` writes a roster and nothing else, which is
[D-005](decisions/decision-log.md#d-005--permissions-are-grants-never-derived-from-identity) and
[D-019](decisions/decision-log.md#d-019--household-membership-grants-no-access) restated one level down:
participation is not authority, and tidier storage does not promote it. A group **is an item** (registered
in `grant_scope_type`), so *"these two may work this group's roster"* is a grant on one group. Its two dated
facts are **different facts**: the group's own period says it existed, the member rows say who was in it,
and *"who was in `schuzka2026-1` on 14 March 2026"* is a point-in-time read over the roster — which is why
the rows are dated, and why that answer survives the audit trail's payload expiry
([D-088](decisions/decision-log.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)).
**A group is not an audience**: a group *states* its members and an audience *picks* them
([Audience](#authorization)). **Nobody writes themselves onto a roster** —
`person_group.member.manage` has no self-scoped variant and none will be added, which is D-095's rule moved
intact, and **no group is seeded**.

**Office (a `role`) and `role_holder`** — **An office is a small, visible set of holders** — the leaders,
the finance people, IT — where a group is company. *"Role and group are technically the same, but not
semantically"* is the sentence that kept them apart, and the difference decides **who may edit the
membership**: `role.assign` / `role.unassign` are 🔒🔒, the most sensitive family in the catalog, while
writing a group's roster is `person_group.member.manage` at ⚠
([D-100](decisions/decision-log.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)).
`role` keeps `code`, `name`, `description`, `is_system`, `sort_order`; **`role_holder`**(role, person,
`valid_from`, `valid_to`, `granted_by`, `note`) is the holder row and names **exactly one person** — one
grantee per row, always, because
[F-12](open-questions.md#f-12--closed--may-a-role-be-held-by-a-rule-as-an-audience-is) is closed and the
answer is no. **A role confers nothing**: `role_permission` is deleted, and the codes an office carries are
**the live grants whose expression names `ROLE(x)`**, which is what makes *"what may a treasurer do?"* a
query over rows a person wrote. An office is held **at the unit, always** (D-097 left one scope), a role is
an item so a grant can be written on one, and nothing forces a holder row to end — the report is the control
([D-071](decisions/decision-log.md#d-071--nothing-forces-a-role-assignment-to-end-the-gate-and-the-report-are-the-control),
whose posture transferred from assignments unchanged).

~~**Position** — A defined role within a unit that people could occupy: `scoutmaster`,
`assistant_leader`, `unit_treasurer`, `quartermaster`. A position was a *slot*: it existed whether or not
anyone filled it, **several people could occupy the same one at the same time**, and `max_holders` was a
per-position limit rather than a structural rule. **A position assignment** was the period during which a
specific person occupied a specific position in a specific unit, with a start, an optional end and a primary
flag.~~ **Deleted by D-100**, with `position`, `position_assignment`, `is_leadership`, `max_holders`, every
`position.*` code, the appointment workflows, and
[D-033](decisions/decision-log.md#d-033--multiple-people-may-occupy-the-same-position)'s occupancy rules. The
reason is structural: **with no units there is no body to be a leader *of***, which was the only fact a
position recorded and a role does not. An elected leader is now a holder of a role, and the rule that used to
read `unit_leaders` — which round 6 had to correct because it silently matched nobody — is `ROLE(leaders)`,
and means what its name says. **What is lost:** the *elected-versus-appointed* distinction as stored data,
which survives only as roles the organization invents (`elected_council` beside `appointed_it`), and **a
vacancy as a reportable state** — an empty office is the absence of rows, and absence has no start date
([F-18](open-questions.md#f-18--does-a-role-record-elected-versus-appointed-and-what-does-an-election-write)).

---

## Membership

**Membership** — The period during which a person is a member **of the unit** — the one unit, the
organization, which is a scope and not a row. Holds `valid_from`, `valid_to` (null = open/current), and a
status in an approval workflow. A person accumulates multiple memberships over time; they never overwrite
one another. **"Everyone in the organization" is now one query against `membership`**, with no participation
row beside it
([D-097](decisions/decision-log.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)).

**There is exactly one membership, and it is ageless.** Membership does not distinguish
children from adults, has no age ceiling, and does not end because a person got older. Being
a counselor or a leader is an **office** held through `role_holder`, never a membership type
([D-100](decisions/decision-log.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)).

**Membership type** — A table kept for the future, currently holding **one row**: `member`.
It survives as a table rather than collapsing into a constant so that a second kind of
membership (a supporting or honorary one) would be a data change rather than a migration.
The fee is flat and per person, so the type does not affect pricing either.

~~**Participation** — The period during which a person takes part in **one sub-unit**: what a pack's roster
was. Distinct from membership in every way — a person held exactly one membership and any number of
participations, participation was free, and it ended when the person stopped attending rather than when a fee
was unpaid. A participation row for the root unit was created alongside each membership, so "everyone in
unit X" was one uniform query. **Nobody wrote themselves into a sub-unit:** a counselor did it, under
`unit_participation.manage` at that unit, which had **no self-scoped variant and none would be added**
([D-095](decisions/decision-log.md#d-095--units-carry-no-restrictions-joining-one-is-somebody-elses-act)).~~
**Deleted by
[D-097](decisions/decision-log.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)** — the
table, its codes (`unit_participation.view`, `unit_participation.manage`), the root row every membership
owed, and the transfers between units. **What replaced it is a group, and two of its rules survive the move
verbatim**: joining one is still somebody else's act under `person_group.member.manage` with no self-scoped
variant, and moving between them still closes one dated row and opens another
([D-098](decisions/decision-log.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority)).
**What the legacy corpus wrote here changed in round 9 and then stopped being a question.** This entry used
to say an imported historical row is *always* a participation and *never* a membership, because the corpus
carries no payment evidence
([D-090](decisions/decision-log.md#d-090--the-legacy-corpus-is-thousands-of-roster-rows-with-numbers-and-no-money))
— then the people export turned out to state membership periods directly
([D-092](decisions/decision-log.md#d-092--the-corpus-is-people-and-events-and-it-names-no-units),
[D-093](decisions/decision-log.md#d-093--the-one-off-import-may-create-memberships-both-ends-dated)) — and
now there is no table to write at all. **What still never happens**: a membership inferred from attendance,
and an imported membership left open-ended. The surviving rule is one sentence: **an imported membership is
bounded at both ends, always.**

**Membership request** — A person's application to become a member **of the unit**. Separate from the
membership itself, because a request has its own lifecycle (submitted, under review,
rejected, withdrawn) and can be rejected without ever producing a membership. **Nothing
gates a request except identity and payment** — there is no checklist to satisfy. ~~It could also name
the unit the applicant wanted to join (`requested_unit_id`)~~ — **deleted with the hierarchy by
[D-097](decisions/decision-log.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)**, and
[D-098](decisions/decision-log.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority)
left it deleted rather than retargeting it at a group: **which group a new member lands in is a write on
the group, never a preference on the request.**

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
Staff hold the same powers and are *a* route, never *the* route. ~~This is scope authority applied to
a household: authority over a nested thing originates at that thing.~~ — **withdrawn by
[D-097](decisions/decision-log.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)**, which
deprived
[D-031](decisions/decision-log.md#d-031--no-downward-inheritance-of-authority-scope_exposure-is-the-only-crossing)
of the nesting that rule was about. The arrangement needs no borrowed principle: a guardianship is a
relationship between two people who are both principals on the row, and that is why they run it.

**Guardian's right** — **One of exactly three values on the guardianship row: `none`, `view`, or
`write`.** Nothing more granular exists
([D-074](decisions/decision-log.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular)).
~~They rank onto the same ladder as every other grant — 0, 10, 20 — so a guardian is not a second
authorization model.~~ **The ladder is deleted by
[D-099](decisions/decision-log.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)**,
and with it the sentence that made this channel *the same model*: a guardian is now a channel of its own,
and the three values are compared against a column rather than against a rank. `permission.right_kind`
(`read` | `write`) is what a right is measured against — `none` covers nothing, `view` covers `read` codes,
`write` covers both — and D-099 says out loud that **this column exists for exactly this one customer**, the
guardianship channel being the only mechanism left that grades rather than flips. What is unchanged is the
point the ladder was making: a guardian's act is checked under the ordinary code for the thing being touched,
so this is one vocabulary, not a second authorization model.

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
`membership.request.approve` or `person.view`. Permissions are the only things the
authorization layer actually checks. Each row carries `applies_to` (`unit`, or `unit_and_item` — where the
code may be granted at all, checked when a grant is saved, so a grant of `event.create` *written on* an
event is refused rather than evaluated) and `right_kind` (`read` | `write`, which exists for exactly one
customer: the guardianship channel, which has had nothing else to compare a permission against since the
ladder went)
([D-099](decisions/decision-log.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)).
Codes are stable identifiers, never display strings, and there is no `<resource>.admin` wildcard and no
prefix match
([D-068](decisions/decision-log.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle)).

**Role** — **An office**, not a bundle: see [Organization](#organization). What survives here is the one
sentence people get wrong — **a role confers nothing**, and the codes it carries are the live grants naming
`ROLE(x)` ([D-100](decisions/decision-log.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)).
Roles are runtime data: the organization invents them, composes them out of grants and deletes the unused
ones ([D-052](decisions/decision-log.md#d-052--roles-are-runtime-data-the-seed-set-is-not-a-specification)).

~~**Role assignment** — The period during which a person holds a role, carrying a **scope**:
organization-wide, or limited to a specific org unit — the same mechanism for both, because "treasurer of
Pack 12" and "treasurer of the organization" differed only in scope.~~ **Renamed `role_holder` and stripped
of its scope columns by D-100**, because D-097 left exactly one scope and there is nowhere else to hold an
office; **`role_permission` is deleted in the same entry**, which is the half that mattered: an assignment
used to be the far end of a permission bundle, and now it is a row in a set that grants point at.

**Scope** — What a grant applies to: **the unit, or exactly one item** (`scope_type` + `scope_id`), never a
nested body and never a choice between several items
([D-097](decisions/decision-log.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)). Items are
registered in `grant_scope_type` — `event`, `person_group`, `role`, and `document` deferred — and `unit` is
the one row that is not item-scoped. **Inheritance, stated once:** a grant at the unit reaches every item of
every type, because nothing is left between them and there is no owner to test; a grant on one item reaches
that item and nothing else ([D-099](decisions/decision-log.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality),
[D-102](decisions/decision-log.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)).

**Grant** — The whole of the grants channel, and its shape is the whole definition: **grantee + scope + one
`permission_id` + effect + period**. The grantee is a person **or** an audience, never both and never neither
([D-042](decisions/decision-log.md#d-042--grants-may-target-audiences-not-only-individuals)); the scope is
the unit or one item; the effect is `allow` or `deny`; the period is `valid_from` / `valid_to`, live on the
checked date. Plus provenance — `granted_by`, `granted_at`, `grant_reason`, and for lent authority
`is_delegated` with `delegated_from`. **One code per grant, not a set and not a level**, which is what makes
*"what exactly does this person have?"* a list of rows and *"who else can do this?"* the same list read the
other way ([D-099](decisions/decision-log.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)).
See [domain/06 §5](domain/06-authorization-model.md#5-the-grant--one-permission-one-effect).

~~**Access grant (the levelled layer)** — A period during which a person may act on one specific record with
a level: `revoked` < `view` < `contribute` < `manage` < `admin`.~~ **Withdrawn by D-099**, which kept the
row and deleted the ladder out of it. Nothing inherits a "level" now; a grant says yes-or-no about one code.

**Allow / deny, and the decision rule** — **Allowed when some live allow applies and no live deny applies.**
That is the whole of precedence, and everything else in the model is elaboration
([domain/06 §7](domain/06-authorization-model.md#7-precedence)). **A deny is absolute**: it is checked before
anything else, at any scope, so no item is local enough to override a suspension
([D-013](decisions/decision-log.md#d-013--explicit-deny-revoked-is-checked-before-everything), whose
surviving content is now exactly this —
[D-032](decisions/decision-log.md#d-032--deny-is-absolute-locality-orders-allows-only)'s second half went
with **locality**). A deny is legal at the unit as well as on an item, and is never conditioned on membership
in either direction. **`-` inside an expression is not a deny and the two are not interchangeable**:
subtracting a set narrows *one grant's reach*, while a deny defeats *every grant* that applies to the person,
written anywhere by anyone — "she must not have this, whatever else she is given" is only ever a deny. The
hygiene rule that comes with it is a report, not a constraint: **a live deny whose grantee, scope and code
match no live allow is dead weight**, and a deny that denies nothing is how a stale restriction survives its
reason.

**Channel** — **There are three, and one absolute deny in front of them**: grants, guardianship, and
resource ownership. ~~The fourth was **role assignment**,~~ and ~~a fifth, the **membership gate**, used to
be described as "a condition on channels 1 and 3"~~ — **both withdrawn by D-100**: a role is now a set that
grants point at rather than a source of authority, and the membership test is a term inside an expression
rather than a clause in the resolver. **How a check reaches a channel changed in round 6 and it is easy to
state backwards.** It used to be the permission's namespace — a code beginning `dependent.` went to
guardianship. That silently skipped every guardian act whose code was an ordinary one, like a parent editing
their child's address under `person.contact.edit`. Now guardianship is reached **when the person the act is
about is not the person performing it**, which nobody has to remember, because the shape of the call decides
([D-079](decisions/decision-log.md#d-079--the-guardianship-channel-is-entered-by-shape-not-by-permission-name)).
**Corollary, and the part people get wrong:** the guardianship channel can only say *yes*. When there is no
guardianship, or the right is too low, it says nothing and the person's grants are still tried — otherwise a
parent who is also the event registrar would be blocked from the roster by their own `view` over their child.
Prohibitions are not made here; they are explicit denies.

**Audience** — **The organization's word is *permission group*; the table is `audience`; both mean one
thing.** An audience is **an expression over named sets of people, stored as a tree of binary rows and aimed
at by a grant** ([D-101](decisions/decision-log.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree)).
**Author in sets, evaluate per person**: a check asks about one person, so the resolver compiles the
expression down to a predicate and never materializes a set. The named sets are the whole vocabulary —
`GROUP(x)` (a dated roster), `ROLE(x)` (an office), `AUDIENCE(code)` (another saved expression),
`PERSON(x)` (**one person**, and since
[D-105](decisions/decision-log.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)
**the only way to write a set somebody typed by hand**: `PERSON(a) + PERSON(b)`) — plus `EVERYONE`,
`MEMBERS`, `GUARDIANS`, the two age operands `OLDER(n)` and `YOUNGER(n)`, and the five event operands.
**The operators are `+ - *` and round 12 added none of its own**: the age operands are ordinary named
operands composed by those three, so `MEMBERS * OLDER(13) * YOUNGER(19)` — thirteen to eighteen, a band that needs both — is an ordinary
term and the
language's *vocabulary* grew by decision while its *grammar* did not grow at all.
**The count is left unsaid here on purpose:** the
registry grew a row while round 10 was closing, when `PERSON` turned out to have been written by two
decisions and seeded by neither
([D-104](decisions/decision-log.md#d-104--a-permission-codes-last-segment-is-an-action-and-a-registry-that-prose-contradicts-is-a-fiction)),
**lost one while round 11 was closing**
([D-105](decisions/decision-log.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)),
and **grew two while round 12 was closing**, when `OLDER` and `YOUNGER` were seeded
([D-107](decisions/decision-log.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded))
— **which is why this page counts nothing: the number has moved three times in three rounds, and the one
place a count belongs is the registry table itself**
([data-model/05 §8](data-model/05-authorization.md#the-selector-registry)). ~~A group was filled by any combination of **three optional arms**: a filling rule, a
hand-kept list, and the groups it **included**, unioned on the checked date~~
([D-091](decisions/decision-log.md#d-091--a-permission-group-is-a-rule-and-a-list-at-once-and-a-rule-may-name-another-group))
— **superseded by D-101**, which turned the rule arm into the selectors and the manual arm into the `LIST`
leaf, and deleted the inclusion arm; **amended by D-103**, which gave a rule a name to point at by
letting an operand name another audience; and **amended again by D-105**, which deleted the `LIST` leaf and
the table behind it with it, so the manual arm's last surviving spelling is a sum of `PERSON(x)` leaves
inside the expression. What survived untouched is the cost D-091 named: **a grant's reach
is not visible in the row that grants it**, so whoever edits a grant or an audience is shown the expanded set
of people — **for a specific item**, since round 10 — rather than a name
([domain/06 §6.2](domain/06-authorization-model.md#62-audiences--an-expression-over-named-sets)).
**Fail closed in every direction:** an operand that does not resolve is the empty set, and an expression that
cannot be evaluated reaches nobody. **The direction is the half people get backwards, and the corpus's old
word for it is retired:** it used to say the `-` side was *"loud"*, which names a volume where there is only
a direction. What is true is that **a failed operand on the `+` or `*` side narrows the set and a failed
operand on the `-` side widens it**, so `EVERYONE - PERSON(x)` with a dead `x` is fail-closed **and**
locks out everybody, in one step, which is not a safe state
([D-106](decisions/decision-log.md#d-106--a-failed-operand-stays-the-empty-set-the-missing-half-was-a-report-not-a-refusal)).
**What round 12 added to this rule is a page, not a refusal:** an audience carrying a leaf that does not
resolve is listed for its owner, and **no save is refused because a leaf is broken**. **And a missing value
on the person being asked about is not a failure at all** — a person with no birth date is simply not in
`OLDER(18)`, exactly as a person with no membership row is not in `MEMBERS`; the operand resolved perfectly
well, and a report that conflated the two would page about every incomplete import in the country.

**Selector** — One **operand** of an audience expression: **a named operand, which means a row.** The
corpus defined this for rounds as ~~a named, materializable set of people~~ and used it to refuse
age — *"an attribute is not a set of people; guardianship is, age is not"* — and
**that test is deleted, not relaxed**
([D-107](decisions/decision-log.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)):
`OLDER(18)` is a test over one column and it denotes the set of people who are eighteen or older on the
checked date, which is the same shape of answer `MEMBERS` gives from a membership table and `GUARDIANS(x)`
gives from a guardianship table. **Every operand is a test with a set on the other side of it**, so the
test as written proved too much — it would have excluded `MEMBERS`, since nothing anywhere stores the
member list. **What is required of an operand is that it be named.** The legal set is a seeded registry,
`selector_type` — `code`, `takes_argument`, `binds_to_item`, `argument_type` — which the parser reads as
its reserved words, the editor builds its dropdown from, and the save path checks arity against. **The
language became data, and it is a closed language anyway:** every row ships with the platform, the registry
is organization-read-only, and a new operand is a decision entry plus a seed row, never a row somebody
types into a screen. **That closure, not the set-ness, is the line that keeps
[D-060](decisions/decision-log.md#d-060--eligibility-is-capability-there-is-no-separate-rule-engine)'s
refusal of a rule engine true:** `OLDER(13)` is a row, and `AGE >= 13` is not one and cannot be, because
**the language has no `>=` anywhere to put it** — no comparison operator, and the operators it does have
(`+ - *`) did not change this round either. So *"13 and over"* is a term a writer types from the registry
now, and anything not in the registry is still a group somebody maintains or a thing this system cannot
say. **Eligibility stays capability: the system applies no gate on its own; a person may write one with
the vocabulary that ships**
([data-model/05 §8](data-model/05-authorization.md#the-selector-registry)).

| Operand | The set, on the checked date | Argument |
|---|---|---|
| `EVERYONE` | Any person, including those with no account and no membership | none |
| `MEMBERS` | Holds a membership live on the checked date | none |
| `OLDER(n)` / `YOUNGER(n)` | **`n` or older** / **strictly under `n`**, both read from the birth date **on the checked date** — so this set gains and loses people at midnight with no write, and `can(..., on date)` for a past date answers for that past date. **A person with no birth date is in neither of them, which is an ordinary answer and not a resolution failure** — as a person with no membership row is not in `MEMBERS` (D-107) | a whole number of years — **the registry's first argument that is not an entity**, and therefore nothing for a merge to repoint |
| `GUARDIANS` | Guardians of the person this item is about, or of the named person | optional person |
| `ROLE(x)` / bare `x` | Holders of that office (`role_holder`) | a role name |
| `GROUP(x)` / bare `x` | Members of that group (`person_group_member`) | a group name |
| `AUDIENCE(code)` | The value of another saved audience's expression | an audience `code` |
| `PERSON(x)` | **One named person** — a set of one, which is a set, so it is an ordinary row of the registry like every other operand. Summed, it is also **the hand-typed set**: `PERSON(a) + PERSON(b)` is the whole of what `audience_member` used to hold (D-105) | a person |
| `ATTENDED` / `PLACED` / `CONFIRMED` / `ON_WAITLIST` / `ORGANIZERS` | The four attendance tiers and the organizer roster | optional event |
| `PRESENT(e)` | — | **refused, and now as a decision rather than as a type error.** A predicate over a column became an ordinary kind of operand the moment `OLDER(n)` was seeded, so nothing excludes `PRESENT` by *what it is*; it stays out because of what it would do — a tick box on a check-in screen would revoke a leader's access to their own camp photos whenever somebody forgot to tick it (D-107 withdrew the older claim that the language could not express it; the refusal stands) |

**`PERSON(x)` was an argument and `LIST` was a set, which is the argument that kept them both for one round —
and it was right about the semantics and wrong about the conclusion.** The difference was real while both were
spellings: `PERSON(x)` named whoever the expression named, composed freely, and could be subtracted on its own,
while `LIST` was one **un-splittable** set belonging to one audience, so **subtracting it removed everybody on
it** and never the one person meant. Pages that noticed `PERSON` missing from the registry "fixed"
`MEMBERS * ROLE(x) + PERSON(y)` by writing `LIST`, and that substitution silently removed everyone on the list
rather than the one person exempted — the defect class
[F-19](open-questions.md#f-19--closed--a-permission-code-is-a-row-prose-names-codes-and-nothing-checks-the-two)
describes, caught in
[D-104](decisions/decision-log.md#d-104--a-permission-codes-last-segment-is-an-action-and-a-registry-that-prose-contradicts-is-a-fiction)
and now **unwritable, because there is only one spelling left**
([D-105](decisions/decision-log.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)).
**What the deleted half was for, and where each property went:** a set of several people belonging to this one
expression, invisible in the group browser, dying with the audience — `PERSON(a) + PERSON(b)` does all of that,
and does it one name at a time, which is the property the kitchen example actually needed and which the old
design got by having two operands rather than by needing them. What went **unreplaced** is the dates:
`audience_member` rows carried `valid_from` / `valid_to`, a sum of leaves carries none, and **a time-windowed
exception is therefore a second grant with its own period** — which is also why a reviewer asking *what does
this person have?* must now find two grants rather than one audience.

The registry seeded `PERSON` as `takes_argument` true, `argument_type` `person`, `binds_to_item` false — the
last of those is why a grant about one person never needed it (the grantee pair already names them) while a
**saved audience** does: an expression aimed at several things cannot carry a grantee. That is what makes
`MEMBERS * ROLE(x) + PERSON(y)` — the control that replaced the membership gate's exemption — a sentence the
parser accepts; for most of round 10 it was not. Since D-105 **every hand-named person in the system is a
`selector_arg_id`, and that column deliberately has no foreign key**, so a merge must repoint the leaves that
name the absorbed person
([D-011](decisions/decision-log.md#d-011--scope_id-on-access_grant-is-polymorphic-with-no-foreign-key)'s
trade-off, and [F-10](open-questions.md#f-10--which-invariants-the-orm-cannot-express-and-who-writes-those)'s
register).

**Names are one namespace** across `role`, `person_group` and `audience.code`, and every `selector_type.code`
is a **reserved name** — a group called `MEMBERS` is refused at the save rather than silently rewriting every
expression in the system. No single constraint spans three tables, so the write path carries the rule and an
integrity check asserts the write path exists
([D-081](decisions/decision-log.md#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now)).
What is stored is always kind + id, so **a rename never rewrites a grant**. Bare names do **not** resolve to
audiences: `AUDIENCE(veterans)` is written out
([D-103](decisions/decision-log.md#d-103--an-audience-may-name-another-audience)).

**Operand, operator, and the canonical form** — An expression is built from **`+` union, `-` difference,
`*` intersection**, with brackets. **`*` and `-` bind tighter than `+`; `*` and `-` bind equally, left to
right; brackets override** — arithmetic-shaped on purpose, with one deliberate departure: `-` does not sit
beneath `*`, because the first expression anybody writes in this language,
`MEMBERS - GROUP(schuzka2026-1) * COUNSELORS`, is meant the left-to-right way
([D-101](decisions/decision-log.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree)).
**The canonical stored rendering prints every bracket, always** — `(MEMBERS - GROUP(schuzka2026-1)) * COUNSELORS`
— the editor rewriting what is typed into that form before it saves. Not for legibility: so that a grant read
two years from now by someone who never learned the table above means what its author meant, and so that a
later change of precedence changes nothing already stored. Storage is a **binary tree**, one row per node
(`operator` + `left_id` + `right_id`) or leaf (`selector_kind` + `selector_arg_id`), with `audience_id`
denormalized onto every row; one parent per node, never a DAG, because a shared node would let one edit
silently widen every grant using it, and the tree is stored **exactly as its author wrote it** — one row per
node, left to right, no rebalancing, because a rebalanced tree is a different expression than the one a person
wrote and storing what was written is the reason the tree exists. Cycles are refused at the save — and since
D-103 the guard is a **reachability walk over the reference closure**, not just the cheap parent-chain one,
because a forest of trees pointing at each other does cycle. **That walk is now the only structural guard
there is:** `selector_depth_limit` and the save-time depth bound it enforced are deleted, and
**an expansion is bounded by acyclicity alone** — no bound on height, no bound ever asserted on breadth, and
deliberately no cap on the read path, because a cap there would become the thing that decides who a grant
reaches ([D-105](decisions/decision-log.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)).
**"A check costs a bounded amount" is therefore no longer a property of this system**; what replaced it is a
standing report of the widest and deepest audiences, which is **a convention and not a guard**
([D-081](decisions/decision-log.md#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now))
— who reads it, and what number makes an audience too wide, is [F-21](open-questions.md#f-21--nothing-bounds-an-audience-expansion-now-who-reads-the-report-of-the-widest-ones).

**`LIST`** — ~~The audience's own hand-typed list of people: the dated rows of `audience_member`, the one
operand that was not a rule *about* people, and the proof that `LIST` and `PERSON()` were not one operand
wearing two names.~~ **Deleted by [D-105](decisions/decision-log.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)**,
with the table, its per-person dates and its seed row: a hand-written set is now written where every other set
is written, as `PERSON(a) + PERSON(b)`. **The term stays because a reader of the round-10 pages will look it
up, and that reader is owed the finding:** the argument was correct about the semantics — an un-splittable set
and a single name really do behave differently — and wrong about the conclusion, because a sum of names has
every property the set was kept for. The kitchen expression it was cited as proof for reads
`(GROUP(kitchen) + PERSON(honza)) - PERSON(a) - PERSON(b)`: **same meaning, one fewer kind of thing, and the
reason not to use a `person_group` for it is unchanged**. The `ADDED` rename that §13 held open for this word
is **moot, not answered** — deleted with the row rather than closed, so nothing in these documents promises it.

**`AUDIENCE(code)`** — The operand that names **another saved audience's expression**, evaluated live
([D-103](decisions/decision-log.md#d-103--an-audience-may-name-another-audience)). It is what makes a **rule
namable**: `GROUP()` and `ROLE()` name rosters, so before it the advice *"name the composite once and aim
grants at it"* had nothing to name, and it is the only arm whose argument is a **decision about access**
rather than a roster — *"the same people that grant may see the fee ledger, plus the accountant"*. Rules come
with it: a reference names a `code` (optional, unique-where-set) and may not point at an audience with none;
**an audience may not be ended or deleted while a live grant, or a live audience reachable from a live
grant, names it**, because "ended" would otherwise be a way to silently empty an operand and an empty operand
behind a `-` makes the result **wider**; naming an audience requires reading it and grants no read of it to
the people inside it. **What it costs:** editing a referenced audience changes grants its owner never wrote,
so saving such an edit shows **which grants name it, and at what depth** before it commits — and
*"who could see this child's data in 2024?"* is answerable when the grant pointed at a group and **is not**
answerable when it pointed at a nested audience, because a live expression's past shape survives only in
audit payloads that expire after 24 months
([D-088](decisions/decision-log.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)).

This comparison was four columns wide — `GROUP(x)`, `AUDIENCE(x)`, `LIST`, `PERSON(x)` — until
[D-105](decisions/decision-log.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)
deleted one of them, and what is left is the three shapes a set can arrive in: a roster somebody maintains, a
saved expression evaluated live, and one person written into the expression itself:

| | `GROUP(x)` | `AUDIENCE(x)` | `PERSON(x)` |
|---|---|---|---|
| What it is | A dated roster somebody maintains | A saved expression, evaluated live | One person, typed into this expression |
| Who changes who is in it | `person_group.member.manage` | `audience.update` on that audience | whoever may edit this audience |
| Exists outside a grant? | **Yes** | No | No |
| *"Was she in it on 1 June 2024?"* | **Answerable** | **Not past the audit window** | **Not past the audit window** — the leaf is a row of the tree, and the tree's past is an audit payload |
| Sensitive as | ⚠ company | 🔒🔒 authority | 🔒 |

**Bound operand** — The **argument-less** form of an operand that means *relative to the item being checked*:
`PLACED` on the event under check, not `PLACED(1204)`. The form exists to kill a specific flaw — one grant
per event with the event's own id typed into it is a thing you do 400 times and forget on the 401st — and two
rules keep it safe, **both enforced when the grant is saved**, with the operand named in the refusal: a bound
operand is legal **only on an item-scope grant** (at the unit there is nothing to bind it to) and **only on a
matching item type** (`PLACED` on a group grant is refused, because that item is not an event —
`selector_type.argument_type` checked against `grant_scope_type`). The consequence nobody should be surprised
by: **the set a grant reaches is now per-item**, so the editor's preview is computed for an item and says so
on screen, and a cache key must carry the item
([D-102](decisions/decision-log.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)).

~~**Filling rule** — The rule arm of a group: a resolver key plus a scope parameter, evaluated at check time
— *"everyone with membership"*, *"the leaders of this unit"*, the derived `unit_leaders` that
`position.is_leadership` fed. A rule does not rot the way a list does, and it stops covering a person the day
the fact underneath ends, which is why an appointment created no role assignment.*__ **Deleted by D-101**,
which decomposed it into selectors and an operator: there is no `resolver_key` and no `scope_parameter` left,
`unit_leaders` is `ROLE(leaders)`, and the reasoning that made a rule better than a copy — do not derive
authority into a second table that has to be found and revoked later — is now carried by the expression
itself. **Filling rule and office were two different questions, and only one is still open:** a *rule* fills
sets that grants aim at, while `role_holder` names one person and
[F-12](open-questions.md#f-12--closed--may-a-role-be-held-by-a-rule-as-an-audience-is) is closed with the
answer **no**, because a derived holder list cannot answer "who was treasurer in 2023".

~~**Inclusion (of a group)** — A stored edge putting one group inside another, refused outright ("they do not
nest") and then allowed, with **the cycle refused when the edge was saved** rather than defended against in
the read path, and a bound on chain length stored as configuration.~~ **`audience_include` and
`include_depth_limit` are deleted by D-101**: `GROUP(kitchen) + ROLE(troop_staff)` composes as much as an edge
did, in one grant, and a tree cannot cycle. What was genuinely lost was **one-edit widening** — *"add the
kitchen crew to everything this group is used for"* — answered at the time by "name the composite once", which
[D-103](decisions/decision-log.md#d-103--an-audience-may-name-another-audience) admits was not deliverable
while the only names available were two rosters. `AUDIENCE(code)` is that answer arriving properly: the edge
table stays deleted, and the edges *are* the `AUDIENCE` leaves.

~~**Membership gate** — Authority held through a role was honoured **only while the holder had a current
membership**, with two carve-outs: guardianship (a legal relationship, not a membership) and roles marked
`requires_membership = false` (appointed counselors and local leaders, who had to be able to serve regardless
of their own fee). Ownership was exempt too, so a lapse could not lock someone out of the screen they renew
on, and one person-level permission — `system.gate_exempt`, held by `system_admin` — waived it for a named
individual, with the documented hazard that a permission check performed *through* `can()` there means a
lockout with no error message
([D-051](decisions/decision-log.md#d-051--the-membership-gate-is-waived-by-a-permission-not-only-by-a-role-flag)).~~
**Deleted by D-100**, resolver clause and all: **the test moved into the expression.** `MEMBERS` is an
operand evaluated live on the checked date, so the gate is written `MEMBERS * ROLE(x)`, waived for a whole
office by writing `ROLE(x)` alone, and waived for one named person by `MEMBERS * ROLE(x) + PERSON(y)` —
ownership and guardianship are channels and have no expression to gate. **The posture reverses from
default-on to opt-in per grant**, and the new failure mode is named rather than buried: a grant written as
`ROLE(treasurers)` with no `MEMBERS` **authorizes a lapsed member, silently, forever**. Three controls, none
of which is the resolver — a standing report of live grants naming `ROLE(…)` without `MEMBERS`, seeded
grants and templates that carry it, and an import reconciliation that counts counselors against
`role_holder` rows. Nothing enforces `MEMBERS` being present: **a convention, not a guard**
([D-081](decisions/decision-log.md#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now)).

~~**Locality** — A grant on the specific item always beat a grant from a broader scope: a per-event grant
outranking a unit-scoped one, outranking an organization-wide one, deciding between competing **allows**
only.~~ **Deleted by D-099**, which is exact about the half that died: **locality only ever ranked allows
against each other**, and once a grant says yes-or-no about one code, two allows that both apply produce one
answer and there is nothing to order. **Deny is absolute survives intact** and is now the entire content of
[D-032](decisions/decision-log.md#d-032--deny-is-absolute-locality-orders-allows-only) — see
[domain/06 §7.1](domain/06-authorization-model.md#71-who-decides--deny-is-absolute).

~~**Scope authority** — Authority over a unit originated at that unit and could not be claimed from outside
it; a parent unit, including the organization itself, could never decide permissions over a nested unit, and
coverage of subordinate units existed only where the subordinate had granted it.~~ **Deprived of its subject
by D-097**: with one unit there is no "outside it" left to be stopped from, so the rule is not weakened, it
has nothing to apply to. What its reasoning still supports is carried by deny-is-absolute and by the
ownership and guardianship channels, neither of which was ever about units. **The safeguarding property it
bought — access to a body's children granted *by that body* — is recorded as lost, not as replaced**
([D-097](decisions/decision-log.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)).

~~**Scope exposure** — An explicit row by which a unit accepted one named **role assignment** as authority
over itself: the only way authority crossed a unit boundary downward, written at the subordinate unit's own
level, naming a person in a role for a period rather than opening a door any future holder could walk
through. **An exposure extended that assignment and nothing else: not the role, and never a direct access
grant** ([D-078](decisions/decision-log.md#d-078--an-exposure-extends-an-assignment-never-a-direct-grant)).~~
**Deleted by D-097**, with `scope.expose`, `scope.exposure.review`, the direction-of-authority check and the
nightly alert that was its only detector
([data-model/05 §5](data-model/05-authorization.md#5-scope_exposure--deleted-by-d-097)).

**`admin`** — **Was ambiguous three ways; after round 10, one remains.** Say which you mean:

| Meaning | What it does | Status |
|---|---|---|
| **Grant level** — `access_level.admin`, rank 40 | *How much* authority a grant carried: `revoked` < `view` < `contribute` < `manage` < `admin`, compared by **integer rank, never by string**; a check asked "at least level X?" | **Deleted by [D-099](decisions/decision-log.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)** — with `access_level`, `permission_level`, the rank integer of [D-012](decisions/decision-log.md#d-012--status-strings-compare-by-rank-never-lexicographically), and the bug it guarded, which cannot occur in a system with no levels |
| **Resource wildcard** — `person.admin`, `event.admin` | A permission code implying every sibling capability on that resource, matched by prefix in the resolver | **Deleted** — all sixteen codes and the prefix match ([D-068](decisions/decision-log.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle)) |
| **Edit action** — `dependent.medical.admin` | Meant "edit", paired against `.view` inside a sub-resource. Implied nothing | **Deleted** — with the whole `dependent.*` namespace ([D-074](decisions/decision-log.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular)) |

What survives of "can do everything": **`system.admin`** (the only wildcard permission; seeded
`applies_to = unit`, so it can never arrive through an item grant) and **roles and audiences** — the bundles
the organization composes, which is where "someone who can do everything about events" now lives, written
out as a couple of dozen grant rows rather than implied by a resolver rule.

**`is_system`** — The flag meaning *the platform shipped this, so a screen must not destroy it*. It sits on
`permission` (a shipped code can neither be deleted nor renamed), on `role` (**`counselors` ships with it so
an editor refuses to delete the set every safeguarding convention hangs from**), on the two seeded audiences
`everyone` and `all_members`, and on every `selector_type` row — where its job is specifically **to make the
registry refuse an edit**, which is what makes "a closed language" true of a table rather than merely
asserted. It is not a sensitivity mark and not a category: `applies_to` and `right_kind` grade what a code
does, and the catalog's 🔒 marks grade what it exposes
([D-086](decisions/decision-log.md#d-086--a-sensitivity-mark-grades-what-a-grant-exposes-not-the-table-it-reads)).

**What is seeded — three answers, three different ones** — Membership ships **one row** (`member` in
`membership_type`, kept as a table so a second kind is a data change rather than a migration); **no group
ships at all**, because a seeded group would be an invented one and the corpus names none, which is the same
argument D-054 made about the unit vocabulary and which D-097 retired along with the vocabulary; and **one
role ships**, `counselors`, marked `is_system`, because a permanent organization-wide population is the
opposite of D-098's definition of a group. Plus the platform's own vocabulary: the permission codes, the
`grant_scope_type` rows, the **fourteen** `selector_type` rows (`PERSON` was the last to arrive *for two
rounds* — two decision entries had been writing it while the registry, copied from the evaluator's arm list,
lacked it — and `LIST` the last to leave, deleted with its table and its seed row one round later by D-105,
which left **twelve for exactly one round**; `OLDER` and `YOUNGER` arrived together after that, so the count
went from twelve straight to fourteen, the only round this seed has had in which nothing was deleted
([D-107](decisions/decision-log.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)),
and their argument is an integer, **the first seeded operand argument that is not a row in some table**), the
two audiences
`everyone` and `all_members`, and
**a grant template rather than a row** for "every event's answers go to its organizers" — a bound operand is
only legal on an item-scope grant, so the event-creation path instantiates that grant beside each event
([D-102](decisions/decision-log.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)).
Roles, groups and their rosters are **runtime data** in every other case
([D-052](decisions/decision-log.md#d-052--roles-are-runtime-data-the-seed-set-is-not-a-specification)).

**Effective permission** — The union of everything a person may do right now, computed from live grants whose
expressions contain them on the checked date, plus ownership and guardianship. **Never stored, always
derived**, so it cannot drift out of sync with the grants that produce it — and since round 10 it is also
*not stored anywhere else*, which is why the historical questions point at
[F-7](open-questions.md#f-7--cache-vs-materialized-effective_permission-table) instead of at a table.

**Delegation** — Temporarily granting someone your authority (a leader going on leave). Modeled as an
ordinary grant with its provenance set: `is_delegated`, `delegated_from` naming who it came from,
`grant_reason`, and a mandatory `valid_to`. Round 10 made it *easier* rather than changing it: because a
grant is **one permission code**, "do not lend more than you hold" is a set-membership test instead of a
comparison of levels. A deny cannot be lent and cannot be lent around, and `system.admin` is never delegated.
~~`role.is_delegatable`~~ went with the rest of the role configuration in D-100, which lists the surviving
columns as `code`, `name`, `description`, `is_system`, `sort_order` — so **lending is said on the grant, not
on the role** (*an assumption; see the index in [open-questions.md](open-questions.md#i-assumption-index)*).

---

## Events

**Event** — A dated occasion that people **register** for: a camp, a trip, a hike, a jamboree. It has
a start and an end, an optional capacity, an optional fee, and a set of **organizers**. It has **no
status column** — visibility *is* the permission model, and cancellation is a recorded fact rather
than a state
([D-064](decisions/decision-log.md#d-064--there-is-no-event-status-visibility-is-the-permission-model)).
~~It belongs to **exactly one unit**~~, and ~~an event is an **artifact** of its unit rather than a
child of it, so the unit's roles reach the unit's own events~~ — **both withdrawn by
[D-102](decisions/decision-log.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)**.
**Nothing owns an event.** There is no `event.org_unit_id` and no `can_event()`; the people connected
to an event are named by **selectors that bind to it** (see *Bound operand*). An event is addressed by
being **the item** of an item-scope grant, which is the only way anything reaches it now.

**A weekly meeting is not an event.** It never was: forty meetings a year are not forty events, so
there is no recurrence, no series and no occurrence table
([D-058](decisions/decision-log.md#d-058--an-event-is-a-dated-occasion-owned-by-exactly-one-unit),
whose *owned by exactly one unit* half D-102 reversed and whose *not an event* half stands). What the
meeting has now is a **group** to be in — a dated roster, not a calendar of evenings. **"Was Jan at the
meeting on 14 March?" is answerable by nobody**: it used to be answerable by nobody in the events module
and by `unit_participation` outside it, and the row that answered it was deleted by
[D-097](decisions/decision-log.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row). A group
says who **is in** it between two dates, not who walked in on a given evening.

**Organizer** — Someone **running** an event. A roster entry on the event, with an optional label
(`'lead'`, `'cook'`, `'driver'`) and an order — **not** an `access_grant`
([D-062](decisions/decision-log.md#d-062--organizers-are-appointed-on-the-event-not-granted)). ~~It is
the event-scoped analogue of a **position assignment**~~ — withdrawn by
[D-100](decisions/decision-log.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape),
which deleted positions; being an organizer is now analogous only to **being a member of a group**.
Authority to *act* on the event no longer arrives from an owning unit: it arrives from **one seeded
grant template** — `event.answer.view`, scoped to an event, aimed at the bound operand `ORGANIZERS` —
instantiated per event by whoever creates it
([D-102](decisions/decision-log.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)).
An event created without that grant has organizers who can do nothing, which is why the *events with no
answer-view grant* report exists.

**Registration** — One person's answer about one event: `attending`, or `not_attending`.
**"Unanswered" is not a value** — it is the absence of a registration row, so "who has not
replied yet?" is the eligible set minus the registered set
([D-059](decisions/decision-log.md#d-059--unanswered-is-the-absence-of-a-row-a-registration-stores-two-values)).

**Eligibility** — Who may register. This is **capability**, not a rule engine: `event.register_self` is
an ordinary permission, allowed by a live **allow** grant and blocked by any live **deny**, granted
either on the unit or on the event itself; opening a camp to members is **one** `access_grant` naming an
audience whose expression contains `MEMBERS`
([D-060](decisions/decision-log.md#d-060--eligibility-is-capability-there-is-no-separate-rule-engine),
[D-099](decisions/decision-log.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)).
~~`event.register_self` requires `contribute` on the event~~ — withdrawn by D-099 with the level ladder;
an age-restricted camp is a camp opened to **a group**.

**Waitlist** — What happens when a full event gets a self-service registration: the person is
written down and ordered, never refused. **Organizers may exceed capacity** outright, and the
overrun is reported rather than prevented — the leader who knows there are two spare tents is
trusted ([D-065](decisions/decision-log.md#d-065--capacity-is-a-waitlist-threshold-and-organizers-may-exceed-it)).

**Presence** — Whether someone actually turned up, marked by an organizer after the fact. Three-valued:
`NULL` (no register taken), `true`, `false`. For a camp this is **the record of who was in the
organization's care**, and it cannot be reconstructed from registrations
([D-067](decisions/decision-log.md#d-067--presence-is-a-three-valued-fact-on-the-registration)).
Not the same as registration — a no-show is a registration with `was_present = false`. Because it is
`NULL` until somebody marks it, **there is no `PRESENT` selector**: a selector that meant "came" would
silently mean "was not marked absent" on every event nobody took a register for, so D-102 refuses it and
the four tiers below are what you may name instead.

**The four attendance tiers** — Four argument-less selectors that **bind to the event** a grant is scoped
to, so a sentence written once reads correctly on every event it is copied to. From widest to narrowest:

| Selector | Who it reaches, on the bound event |
|----------|-----------------------------------|
| `ATTENDED` | anyone whose `response` is `attending` — asked, said yes, whether or not there was room |
| `PLACED` | those attending **who were not waitlisted** — the set the capacity actually let through |
| `CONFIRMED` | `PLACED` **and** `is_confirmed` — somebody has since looked at each of them |
| `ON_WAITLIST` | written down, ordered, **not yet placed** — waiting, not attending |
| `ORGANIZERS` | the event's organizer roster — the reason a per-event answer-view grant is seeded |

They are **not** one set with flags: `ATTENDED` is wider than `PLACED` precisely because a full event says
yes to more people than it can seat, and `CONFIRMED` is narrower than `PLACED` because a seat is not a
headcount
([D-102](decisions/decision-log.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)).
**`WHITELISTED` is not one of these**, and is not a selector at all — see
[EV-6](open-questions.md#ev-6--whitelisted--the-word-people-reach-for-with-no-stored-state-to-name).

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

**Broadcast** — The only messaging permission, and **an ordinary scoped one**: a grant like any other.
~~Granted on a unit it reaches that unit, granted organization-wide it reaches everyone~~ — that pair was
**one code at two scopes**, and after the sub-units went there is only one scope to have
([D-097](decisions/decision-log.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)): held at
the unit, `message.broadcast` reaches everyone. The narrower reading the pair used to buy now has to be a
**grant naming a group**, reaching that roster — a shape D-099 makes available and D-077 could not have.
What survives untouched is why there is **no global broadcast flag**: a permission that has to be granted
is one that can be given to some people and refused to others, whereas the flag would be all-or-nothing
and would leave a section leader choosing between an organization-wide power and typing the same sentence
twelve times. Whether broadcast should ever be grantable on an item is messaging's open question, not the
model's.

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

**Mirroring** — A copy of a direct message addressed to a minor, delivered to that minor's guardians whose
**right** is `view` or `write` — the three-value right of the guardianship channel, not a grant level,
which no longer exists ([D-099](decisions/decision-log.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality))
— fixed to that set **at the moment of sending**. Visibility,
not approval: nobody has to agree before the message is sent. A guardian at `none` receives nothing,
because `none` is the organization having already decided that this party sees nothing about the
child — and a minor whose guardians are *all* `none` is the same alertable shape as a minor with no
guardian at all, so it is reported together with it.

## Time

**Temporal row** — Any row with `valid_from` / `valid_to`. `valid_to IS NULL` means
"still true". All permission checks and history queries filter on these. The full
pattern is specified in [data-model/00-conventions.md](data-model/00-conventions.md).

**Point-in-time query** — A question of the form "who/what was true on date D?" — *"Who was in the group
`schuzka2026-1` on 1 June 1998?"*, *"Was this person a member when they attended camp?"* These are
first-class requirements, not an afterthought, because you have four decades of history to preserve. Note
that the answer now depends on **which named set** the question is about, and there are only two kinds left to
be about: a **group** answers it from its dated roster, and an **audience** cannot answer it at all — its
expression is evaluated live, and its one past is the audit trail. That includes a name typed straight into
the expression: since [D-105](decisions/decision-log.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)
a `PERSON(x)` leaf carries no dates of its own (the dated rows it replaced are deleted), so *"was she in this
audience on 1 June 2024?"* is a recomputation over audit payloads that expire after 24 months
([D-088](decisions/decision-log.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)),
and the same is true of [D-103](decisions/decision-log.md#d-103--an-audience-may-name-another-audience)'s
nested audiences.

**As-of vs audit time** — Two different times, both needed. **As-of** is the date the
fact was true about the world (a membership that ran 1990–2010). **Audit time** is when
the row was written in the system. A membership backdated during a 2026 data-entry
session has as-of 1990–2010 and audit time 2026. Do not conflate them.

---

## Roles in conversation (informal terms — not names in the model)

The words you and the organization will naturally use, and what they map to:

| Informal term | What it is in the model |
|---------------|------------------------|
The table is the same shape it always was; what changed in round 10 is that most of its right-hand column
no longer has a table to point at.

| Informal term | What it is in the model |
|---------------|------------------------|
| "child member" | a person with an open `membership` whose `birth_date` makes them a minor — **age is a fact about the person, not a kind of membership** |
| "counselor" / "leader" | an **office** held through `role_holder` — never a membership type, never a participation row, and since D-100 **conferring nothing by itself**: authority comes from the grants that name `ROLE(counselors)` |
| "parent" / "caretaker" | party to an active `guardianship` row |
| "leader of the Thursday group" | ~~a leadership role scoped to that `org_unit`~~ — there is no such thing: an office is held for the unit and has no scope column, so this is **a member of that group**, plus whatever a grant aimed at them or at it allows (D-097, D-100) |
| "in the Thursday group" | an open `person_group_member` row in that `person_group` — **company, not authority** (D-098) |
| "ex-member" | person with a `membership` whose `valid_to` has passed |
| "lapsed but can still renew" | `valid_to` passed, within the renewal window |
| "registered but not a member" | person with an `account` and no open `membership` — they may sign in and see their own data, but hold no member permissions |
| "they're allowed to attend" | a live **allow** grant naming `event.register_self`, aimed at them or at a set they belong to, **and no live deny anywhere** naming them — not a level, and nothing inherited from a unit that owns the event (D-099, D-102) |
| "open to everyone" | a grant naming the seeded audience `everyone`, whose expression is the operand `EVERYONE` — or `all_members`, whose expression is `MEMBERS`. A bare name in an expression is **not** a reference to either: audiences are named only as `AUDIENCE(code)` (D-101, D-103) |
| "the treasurer" | `role_holder` of `treasurer`, held **for the unit** — there is no narrower place to hold it, and holding it answers no permission question on its own |
| "put me in the Thursday group" | a `person_group_member` row **somebody else writes** under `person_group.member.manage`, which has **no self-scoped variant** — there is no self-service path and no permission with which to build one (D-095, D-098) |
| "the kitchen crew" | a **`person_group`** if the answer is a list of people somebody keeps up by hand, dated and quotable years later; an **`audience`** if the answer is a sentence recomputed each time it is asked. *"Whom did this grant reach on 1 June 2024?"* is answerable for the first and not the second (D-098, D-103) |
| "the permission group for the kitchen crew" | one or the other of the row above. ~~an `audience` filled by a rule, a hand-kept list, **other permission groups**, or all three~~ — the third arm is gone; an expression names a group through `GROUP(code)` and another audience through `AUDIENCE(code)` (D-091 as amended by D-098 and D-101) |
| "the old Pack 12 came back" | ~~a **new** `org_unit` whose `code` happens to equal a dead one, with `successor_of` written by a person~~ — **there are no units to bring back** (D-097). The closest thing left is a **group** whose `name` repeats a dead one, and that is only a reused label: groups have no `code`, no succession and no rename history (D-098) |
| "the organizers" | the event's own `event_organizer` roster, reached as `ORGANIZERS` on a grant scoped to that event — an appointment on the thing being run, and since D-100 **not** the event-scoped cousin of a position |
