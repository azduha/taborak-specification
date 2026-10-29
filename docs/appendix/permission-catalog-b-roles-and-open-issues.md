# Appendix — Permission Catalog: absent namespaces, the role seed, open issues

What the catalog deliberately does not have, what arrives with the unbuilt modules, the offices the organization starts with, and what is not settled.

**Section numbers are shared across the three parts** and never renumbered, because other pages cite them by number and their anchors are built from them: [permission-catalog.md](permission-catalog.md) holds §1, the conventions; [permission-catalog-a-codes.md](permission-catalog-a-codes.md) holds §2–§8a, the codes; [permission-catalog-b-roles-and-open-issues.md](permission-catalog-b-roles-and-open-issues.md) holds §9–§12, the namespaces that are not here, the deferred ones, the role seed and what is open.

---

## 9. There is no `dependent.*` namespace

**A guardian has no permission codes.** Their rights are one value on the guardianship row — `none`,
`view` or `write` ([D-074](../decisions/round-06.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular),
§6) — and the eighteen codes that used to sit in this namespace, `dependent.profile.view`,
`dependent.medical.admin` and their siblings, are indexed with the other dead names in
[removed-concepts](removed-concepts.md). **Nothing here may be reinstated by pattern-matching one of those
names**: there is no set left for a name to stand for. If the finer split turns out to matter in operation,
it is a new decision argued from the current documents — one grant scope over a defined set of data — and
not a restoration.

**What cannot be expressed was declined, not left unbuilt.** A court order giving one parent access to
everything about their child except the medical file **cannot be expressed**: `view` is one value over the
whole of a child's record, so a grandmother granted roster visibility gets the fee history with it. There
is also no medical record to be shut out of — everything other than name, gender and age is one class of
data reached by `person.view` and governed by the guardian's level whole
([../domain/08-person-data.md](../domain/08-person-data.md)). *Why: the story was put to the organization
and refused on the merits — "medical data is not different in any way" — which is
[D-083](../decisions/round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data),
and it is why [E-7 closed](../open-questions.md#e-7) as a dissolved question rather than an answered one.*
**Read the inexpressibility as settled, not as pending work:** reopening it means producing the case that
was declined, not finding a code to restore.

**What still holds:**

- **A guardian's authority is per guardianship row.** The channel is entered by whose record the act
  touches and answers only about that row
  ([D-079](../decisions/round-06.md#d-079--the-guardianship-channel-is-entered-by-shape-not-by-permission-name)),
  so a guardian cannot do organization-wide things and cannot reach a different dependent's records. What
  `write` means is *this row's dependent, both kinds*: it covers the `write` codes and the `read` ones,
  where `view` covers only `read` and `none` covers nothing — compared against `permission.right_kind`, not
  against a level (§6).
- **A deny still reaches the channel.** A live deny beats every allow that applies, at any scope and in
  any channel
  ([D-032](../decisions/round-02-03.md#d-032--deny-is-absolute-locality-orders-allows-only),
  [D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)),
  so *"this guardian, nothing"* remains expressible: a `deny` at the unit aimed at the person, `PERSON(x)`.
  There is no *narrow* deny — no operand names one child's guardians to aim one at, because the channel
  resolves no sets and the name an expression can carry here is the person's
  ([D-113](../decisions/round-13.md#d-113--the-guardianship-channel-has-no-expression-guardians-is-not-a-selector)).
  What was lost is the narrowness, not the refusal.
- **A guardianship at `none` grants literally nothing**, so **being a guardian grants nothing by itself** —
  the safeguarding property the eighteen codes were written for, held without any of them.
- **An event's answers are not guardian data.** They are read through `event.answer.view`, a permission on
  the grant side, carried by the seeded grant to `ORGANIZERS` (§8a), and leadership is not guardianship
  ([D-061](../decisions/round-05.md#d-061--event-answers-are-read-by-that-events-organizers)).

See [../data-model/04-relationships.md §2](../data-model/04-relationships.md#2-the-guardians-right-none-view-or-write)
for the value, its defaults by `source`, and the three-value ordering it is a range of — `none` < `view`
< `write`, which is D-074's own ordering over one column and **not** the access-level ladder
[D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)
deleted. Nothing in this catalog is a range of anything.

## 10. Deferred namespaces

Placeholders for features you have not specified. Listed so the naming convention is
established before anyone invents an inconsistent one.

| Resource | Permission | Notes |
|----------|-----------|-------|
| `document` | `document.view`, `document.create`, `document.edit`, `document.delete`, `document.grant_access` | `document` is already a row of `grant_scope_type`, marked deferred — the item exists in the registry before the module does, which is what the polymorphic `scope_id` is for (D-011). The code is the one this catalog's own §1 rule pays for: `document.grant_access` sits beside `access_grant.create` exactly as `event.grant_access` does, and §12 asks the question once for both. |
| `fee` | `fee.view`, `fee.create`, `fee.waive`, `fee.refund` | ⛔ `fee.waive` and `fee.refund` are sensitive — a hardship waiver must not be visible to whoever happens to run a group. There is no unit level to be below any more, so the mark and the grant list are the whole control. |
| `payment` | `payment.view`, `payment.record`, `payment.reverse` | |
| `report` | `report.finance.view`, `report.membership.view`, `report.safeguarding.view` | ⚠⚠ `report.safeguarding.view` |
| `consent` | `consent.template.edit`, `consent.record.view` | |
| `message` | `message.send_direct`, `message.broadcast` | **Decided in shape, undesigned in detail** ([D-077](../decisions/round-06.md#d-077--messaging-is-direct-by-default-broadcast-is-an-ordinary-scoped-permission-and-the-recipient-chooses-the-channel)). Everyone may send direct; `broadcast` is an ordinary **scoped** permission. **The unit is one scope** ([D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)), so held at the unit `broadcast` reaches everyone; the narrower audience — this body, not the unit — is a **grant on a `person_group`**, reaching that roster, which [D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality) makes available. *Which of the two messaging means, and whether `message.broadcast` should be `applies_to = unit_and_item`, is messaging's decision, not this catalog's* (§12). Recipient chooses the channel, which is not a permission at all. **A direct message to a minor is mirrored to that minor's guardians and the sender is told it will be** — no permission, no age branch in the resolver ([D-082](../decisions/round-07-08.md#d-082--a-direct-message-to-a-minor-is-mirrored-to-the-minors-guardians)) |
| `partner` | *(namespace)* | For external organizations, if the model expands. |

**What each new resource owes the authorization module is four things** — all cheap, all required, and no
level table among them
([D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)):
**codes**
(two or more lowercase segments, first segment = `resource`), each with a **`right_kind`** — `read` or
`write`, required, because that column is a guardian's answer and not a hint (§6) — each with an
**`applies_to`**, checked on save (§1); and a row in **`grant_scope_type`** if its records are things a
grant can be written on, which is what makes a document or a group an item at all.

---

## 11. Roles — proposed seed set

**A starting point, not a specification.** The heading says "roles" and most of what follows is grants,
because an office has no contents: **the codes an office carries are the live grants whose expression
names it**, one row per code, each with its own scope and its own period
([D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)).
`MEMBERS * ROLE(treasurers)` on `fee.create` is one such row, and it — not the office — is what lets a
treasurer issue a fee. A role is two things: **a name a grant can be aimed at**, and **the register that
answers *who held this in 2023*** (`role_holder`, which is why
[F-12](../open-questions.md#f-12) closes with *no* — a holder row names one person). Offices are runtime
data: the organization creates them, names them, writes and closes their holders, and deletes the
never-held ones ([§7](../data-model/05-authorization.md#3-role--an-office)). **Reach is not runtime
data** — it is administered through `access_grant.create` and `access_grant.revoke`, so it is reviewed in
`access_grant`, not in a role editor (§7).

### What the seed ships

**Counting only the tables this section is about: one role and one grant, and the role is empty.**
Everything else the seed carries is vocabulary — the permission rows of this catalog, the
`selector_type` operands (§1), the `grant_scope_type` rows that make an event or a group or a role an
item, and two `is_system` audiences whose expressions are `EVERYONE` and `MEMBERS`
([§7](../data-model/05d-invariants-and-seed.md#12-what-the-organization-starts-with)). **None of those is
authority**, and the sentence is repeated here because this section is where a reader looks for it.

| Seeded row | Table | `is_system` | Holders at seed | What it grants |
|------------|-------|-------------|-----------------|----------------|
| `counselors` | `role` | **yes** | **nobody** — `role_holder` is empty | **Nothing.** A set is not a grant (§1, §5a) |
| `event.answer.view`, item-scoped on an event, aimed at `ORGANIZERS` | `access_grant` | — | — | Answers are read by that event's organizers, written as a grant rather than as prose somewhere else ([D-061](../decisions/round-05.md#d-061--event-answers-are-read-by-that-events-organizers), [D-102](../decisions/round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)) |

**Why a role and not a group**, when D-098's own definition of a group is *"a temporary set of members
that do events together"* and counselors are neither temporary nor event-shaped: the table decides
**which code protects the set**, and every safeguarding convention in this area hangs from that answer
being unchangeable by an ordinary grant — `role.*` is 🔒🔒, `person_group.member.manage` is ⚠
(§5a). **It ships `is_system` so that an editor refuses to delete it**, and so that the §7 rule
*deletable only if never held, and never if it is a system role* has something to refuse.

**Nothing in the seed names `ROLE(counselors)`, and that is the design rather than an omission.**
Being a counselor confers nothing until someone writes the grant
([D-005](../decisions/round-01a.md#d-005--permissions-are-grants-never-derived-from-identity)).
**What that leaves open is not a permission but a
number**, and it is the price D-100 names for moving the gate into the expression: the reach of the
counselor office is only as correct as the roster, so the import reconciliation of
[D-090](../decisions/round-07-08.md#d-090--the-legacy-corpus-is-thousands-of-roster-rows-with-numbers-and-no-money)
counts people marked as counselors in the legacy corpus against `role_holder` rows written. An import
that misses three hundred counselors **fails closed** — nobody's access breaks — which is exactly why
nobody notices.

**Who may make someone a counselor, over just that one office.** `role.assign` writes a `role_holder`
row and is `applies_to = unit_and_item` (§7), so holding it **at the unit** lets you fill every office
in the organization, which is what 🔒🔒 is for, while a grant of it **on the item `counselors`** says
*these two may manage the counselor roster* and nothing else. That is D-098's move read symmetrically,
and it is why `role` is a row of `grant_scope_type`.

**The one seeded grant is written without `MEMBERS`, and must not be "corrected."** An organizer
appointed for one weekend is not required to hold a current membership — D-062's appointment model
assumes exactly that — so a `MEMBERS` on that row would take an organizer's read of their own event's
answers away the night their fee lapsed. **It is also the seed's only grant, which means no seeded
grant carries `MEMBERS` at all**, and that is worth stating because one of D-100's three controls
reads *"seeded grants and any grant template carry `MEMBERS`, so the path of least repetition is the
safe path"*: in this seed the path of least repetition carries nothing (§12). *And the seeded row is a
**template** rather than one grant covering every event — a bound operand cannot sit on a unit-scope
grant — so the row a reader finds is written beside each event by the event-creation path (§8a).*

### The worked-example offices

**None of the following ships.** These are the names the rest of the corpus uses whenever it needs an
office to talk about, written out the way an office now has to be written: as grant rows. Each row
below is **one grant per code**, all aimed at one expression, all at the unit — there is nowhere else
for a code about people to be aimed (§1) — each with its own period. Do not read a row as a
requirement, and do not expect the list to survive contact with the organization.

| Office | The grant rows that are its reach | Grantee expression | Why that expression |
|--------|------------------------------------------|--------------------|---------------------|
| `system_admin` | `system.admin` — **one row, and it is enough** | `ROLE(system_admin)` | **no `MEMBERS`**, deliberately: the 1 January case below |
| `registrar` | `person.view` ⚠⚠, `person.create`, `person.edit` ⚠, `person.contact.view` ⚠, `person.contact.edit` ⚠, `account.view` ⚠, `account.create`, `account.suspend` ⚠, `account.close` ⚠, `account.credential.reset` 🔒, `membership.view` ⚠, `membership.request.create`, `membership.request.review` ⚠, `membership.activate`, `membership.backdate` ⚠, `import.view` ⚠, `import.stage`, `import.apply` 🔒, `import.revert` 🔒 — **nineteen rows** | `MEMBERS * ROLE(registrar)` | staff working the organization's own records; the office stops when the fee lapses |
| `membership_approver` | `membership.request.review` ⚠, `membership.request.approve` ⛔ | `MEMBERS * ROLE(membership_approver)` | as above |
| `treasurer` | `fee.view`, `fee.create`, `fee.waive`, `fee.refund`, `payment.view`, `payment.record`, `payment.reverse`, `report.finance.view` | `MEMBERS * ROLE(treasurer)` | as above |
| `safeguarding_officer` | `membership.view` ⚠, `report.safeguarding.view` ⚠⚠, `membership.terminate` ⛔ | `MEMBERS * ROLE(safeguarding_officer)` | whoever finds the problem and whoever ends a membership over it are the same person, and nobody else |
| `leaders` | the thirteen `event.*` codes (§8a), `membership.view` ⚠, `person_group.view` ⚠, `report.membership.view` ⚠ — **sixteen rows** | `ROLE(leaders)` | **volunteers, so no `MEMBERS`** (property 4): the office must survive a lapsed fee, and it reaches every event, not one body's events |
| `audience_admin` | `audience.view`, `audience.manage` ⚠ | `MEMBERS * ROLE(audience_admin)` | §5a, including the naming rule this office is subject to |
| `identity_reviewer` | `person.merge` 🔒, `import.view` ⚠, `import.apply` 🔒 | `MEMBERS * ROLE(identity_reviewer)` | and **no `person.view`** — property 5 |
| `auditor` | `audit.view` ⚠⚠, `audit.export` ⚠⚠, `report.view` ⚠ — **read-only, no writes** | `ROLE(auditor)` | **no `MEMBERS`**: an auditor who forgets to pay must not lose the read (property 4) |

**An office's reach carries two kinds of period, and both are worth knowing before you set either.**
The office is held for a period (`role_holder.valid_from`/`valid_to`) **and** each of its grants has a
period of its own, so an office's reach is an intersection of up to twenty dates, and the question *when
does this person stop being able to do that?* has more than one right answer. **Nothing forces either
kind of row to end** — the posture of
[D-071](../decisions/round-05.md#d-071--nothing-forces-a-role-assignment-to-end-the-gate-and-the-report-are-the-control)
applies to both, and the control is the report.

**Three of these offices name codes this catalog has not registered, and one office is made entirely
of them.** The treasurer's eight rows are `fee.*`, `payment.*` and `report.finance.view`, and all
three of those namespaces are [§10](#10-deferred-namespaces) placeholders — so **that office cannot
be written today**, and its row count is a wish rather than a migration. `safeguarding_officer` and
`leaders` each name one deferred report code among otherwise live rows, which is the milder form of
the same thing. The counts above therefore say what an office would hold once finance ships; the live
half of each list is what a seed migration could insert now. Nothing in the schema stops a grant row
naming a code that does not exist, so this paragraph is
[F-19](../open-questions.md#f-19)
one section further along: the catalog names the office, the office names the code, and no row agrees.

**Read `event.*` above as a count, not as a wildcard.** Since
[D-068](../decisions/round-05.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle)
there is no resolver rule that makes `person.*` mean anything; the notation means *"every `person.`
code listed in §2"*, and a real office has an explicit **grant row** for each — which since D-100 is
the only place such a list exists at all. Three consequences for whoever writes these:

1. **`registrar` omits `person.merge` and `person.redact` by not having those rows, and the exclusion is
   exactly that literal**: two rows nobody inserted, visible in `access_grant` with a date and an author,
   alarmable like any other row. `identity_reviewer` is the office that *does* hold `person.merge` — the
   whole of identity correction: merging, reversing a merge, and deciding a sign-up collision (§2) — listed
   beside `registrar` so the difference between the two is legible. **An office that bundles a resource
   *including* its 🔒 codes should be named for that**, since nothing else records the choice:
   `person.redact` is irreversible, and `person.merge` is undoable but unions permissions the moment it
   runs
   ([D-087](../decisions/round-07-08.md#d-087--merge-chains-stay-because-reversing-a-merge-is-a-supported-operation)),
   which is why 🔒 and not a word like *irreversible* is what a reviewer should read.
2. **`leaders` holding `event.*` means thirteen explicit rows** (§8a), and a fourteenth added later is
   *not* in the office until someone writes it. Integrity check 18 surfaces an orphaned permission — one
   **no live grant names** — and it does not surface *"this office arguably should have had it."* That is
   the cost D-068 accepts. **`access_grant` is the only place an office's list exists**, so the question
   *should this office have that code?* has no page that answers it: check 18 answers only *does any live
   grant name this code?*
3. **`auditor` is an office that reads the whole person record, and does it without `person.view`.**
   `audit.view` is graded ⚠⚠ in §8 precisely because the payload is a second copy of the record, so
   this row grants a ⚠⚠ read over what the system believed about a child and when it believed it.
   That read has a floor: payloads older than 24 months are emptied
   ([D-088](../decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)),
   so what is exposed reaches back two years and no further, while the who-did-what-to-which-row part
   reaches back for the life of the system. That bounds this row's exposure and does not soften its
   grading. Nothing
   here forbids it — it is a plausible office — but the row must not be described to anyone as "just the
   logs", and it is scoped and dated for the same reason the ⚠⚠ rows above it are.

### How the gate is written

**`MEMBERS` is an operand**, evaluated live on the checked date, so whether an office survives its
holder's lapse is a property of the expression written on the grant (§7,
[../domain/06-authorization-model.md §6.1](../domain/06-authorization-model.md#61-members--the-membership-test-moved-into-the-expression)).
Three things a writer says with it:

| Expression | What the writer is saying |
|------------|---------------------------|
| `MEMBERS * ROLE(x)` | this office is for people who are members right now |
| `ROLE(x)` | written **without** `MEMBERS`; a lapse in the fee ledger does not stop this office |
| `(MEMBERS * ROLE(x)) + PERSON(y)` | one named person is the exception, and the exception is visible to everyone who reads the grant |

**A second grant aimed at `PERSON(y)` is the other way to write the third row**, leaving the gated
expression alone; D-100 keeps both legal and calls the second arguably clearer for a permanent
exception, because it keeps the exception off the expression everyone else reads. *Why: there is nothing
to waive and no column to set — the test is not a resolver clause any more, so the fee either appears in
the expression or it does not. What used to carry it — a role flag exempting a whole office, a
person-level permission exempting one named person, and the resolver clause that asked the question of
every grant
([D-039](../decisions/round-02-03.md#d-039--member-permissions-require-a-current-paid-membership),
[D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)) —
is in [removed-concepts.md](removed-concepts.md).*

**The posture is opt-in, so name the new failure rather than bury it.** An expression written
`ROLE(treasurers)` with no `MEMBERS` authorizes a lapsed member, silently, for as long as the grant
lives: forgetting `MEMBERS` is now possible, and waiving it is a deliberate act in the text. Three
controls, none of which is the resolver:

- **The tab on the permissions page, in its `Unusual` section: live grants that name a `ROLE(…)`
  operand and contain no `MEMBERS`.** An office held by a non-member is the case worth a human eye, and
  this population is narrow enough to actually be read — `system_admin`, `leaders` and `auditor` are on it
  here, and all three are on it *because someone chose them*, which is the whole point. It is a section of
  a tab rather than a report, because a report has to be remembered and the writer is already standing on
  that page; and it says *unusual*, never *broken*, because such a grant resolves exactly as written
  ([F-13](../open-questions.md#f-13),
  [D-109](../decisions/round-13.md#d-109--nothing-a-rule-names-is-deleted-deprecated-hidden-disabled--and-a-tab-instead-of-a-report)).
- **Seeded grants and any grant template carry `MEMBERS`**, so the path of least repetition is the
  safe path. *In this seed that control has nothing to work on: the seed's one grant must not carry
  `MEMBERS`, and it is the only one, so every office grant anyone ever writes will have been written by
  hand — the safe path is not the short one. Recorded in §12.*
- **Import completeness.** The counselor office is only as correct as the roster behind it: a grant
  aimed at `ROLE(counselors)` says nothing about anyone the import left out. The duty is stated above,
  and a short import fails closed.

**One of these offices is not a preference, and it is the one to copy carefully.** `system_admin` is
written `ROLE(system_admin)`, with **no `MEMBERS`**, because on 1 January the expiry sweep of
[D-040](../decisions/round-02-03.md#d-040--the-fee-expires-yearly-a-date-tracked-renewal-window-replaces-a-grace-status)
lapses every membership in the organization including the administrator's, and a gated administrator
loses the ability to repair the system on the day it breaks. That is a property of the system, not a
policy choice — and it is now an expression rather than a flag, which means it can be got wrong. The
loud mistake is the opposite one: writing `MEMBERS * ROLE(system_admin)` "for consistency" reproduces
the lockout, silently, with no error message. **Whether any office
in the shipped seed is written this way is a different question, and the answer is no: the seed
contains no office grants at all** ([What the seed ships](#what-the-seed-ships), §12).

**Eight properties worth noting:**

1. **`membership_approver` is separate from `registrar`.** Deciding who becomes a member is
   a different act from processing records. If your organization wants one person to do
   both, hold both offices — which now literally means two holder rows and two sets of grant rows —
   but keep them separately attributable, because that separation is the only thing the office names
   buy.
2. **`safeguarding_officer` holds `membership.terminate`.** The permission to end someone's
   membership sits with the person responsible for safeguarding, not with whoever chases
   fees. This is deliberate. There is no `person.background_check.*` for it to hold: the organization
   records no background checks
   ([D-043](../decisions/round-02-03.md#d-043--no-background-checks-are-recorded-in-this-system)).
   What it also does not have here is `person.view`: three rows, and the ⚠⚠ one is the report rather
   than the record. **If working a case needs the record, that is a fourth grant row** — scoped, dated,
   attributable, and visible to anyone who asks what this office can read, which is the review §2 moved
   to when it graded `person.view` ⚠⚠.
3. **No office is a guardian.** **The guardianship channel is only consulted when the subject of the act
   is someone else, and it only finds a guardianship row**
   ([D-074](../decisions/round-06.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular)).
   Leadership is not guardianship, so no office hands anyone a guardian's right over a child — not the
   right to act for that child, and not the row that decides what the family may see.
   **What an office can do, and does openly, is read the child's record.** With no privileged subset
   inside the person record, a leader granted `person.view` reads the whole of a member's descriptive
   data, allergy list included
   ([D-083](../decisions/round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data),
   [../domain/08-person-data.md](../domain/08-person-data.md)) — and **one such grant reaches every
   member in the organization**, because there is no narrower scope than the unit for a code about
   people (§1,
   [D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)).
   Nothing about leading anything grants it: no channel opens on its own, and the row that would is
   explicit, scoped, dated and readable in `access_grant`. That is also why §2 grades that code ⚠⚠: the
   safeguarding review is the question *which grants were given this one?*, which is a question the
   catalog can answer. **Do not re-derive it as a list of codes to keep out of offices** — the rule is
   about the channel, and there is no code left to quarantine.
4. **`system_admin`, `leaders` and `auditor` are the three example offices written without `MEMBERS`.**
   The rule behind them is one sentence — **staff-like offices working on the organization's own records
   require a membership; volunteer-facing offices do not** — and it is a writing habit now, not a
   resolver clause.
   The failure it prevents is specific: the volunteer whose own fee is unpaid still runs the Thursday
   meeting, and must not lose their roster the night it lapses. That volunteer's office appears in the
   `Unusual` section of the tab on the permissions page — grants naming a `ROLE(…)` operand with no
   `MEMBERS` — **which is how the organization notices, and the resolver is still not how it punishes**. See
   [../domain/06-authorization-model.md §4](../domain/06-authorization-model.md#4-roles-are-offices-groups-are-company).
5. **`identity_reviewer` decides identity questions about children without a read over the person
   record.** The office carries three rows — `person.merge`, `import.view`, `import.apply` — and
   **`person.view` is not among them**: the reviewer works from the candidate pair, the
   `match_signals` recorded against it, and the names and dates those signals compare. That is
   deliberate as it stands — the question being decided is whether two rows are one human, and the
   descriptive values underneath are not evidence about that — and it is the same shape as `auditor`
   reading the trail without holding `person.view`.
   What round 8 changed is the pressure on it. This is now also the office a **blocked sign-up** lands
   on: an account held out of `active` by an unresolved hypothesis, with an age check alerting because
   the stalled item is a person who cannot log in
   ([D-089](../decisions/round-07-08.md#d-089--one-live-account-a-colliding-sign-up-files-a-claim-and-creates-nothing)).
   **If reviewers begin asking for context they cannot see, that is the finding to act on**, and the two
   honest answers are a scoped, dated `person.view` on this office, or a review screen that shows more
   of the *signals*. Reaching instead for an organization-wide `person.view` would put the catalog's
   largest ⚠⚠ read in the office with the most write authority over identity. Tracked as
   [F-11](../open-questions.md#f-11--does-the-identity-reviewer-need-to-read-the-person-record-to-settle-a-claim),
   where none of the three positions is yet recorded as taken.
6. **No office in this set holds `person_group.member.manage`, and that is a hole rather than a neutral
   omission.** What
   D-095 decided has not moved: joining a set is somebody else's act, the write is never self-scoped, and
   this code is the only thing standing between a person and a group's roster (§5a). As written,
   `leaders` may *see* a roster and cannot write one — and because the answer behind D-095 was
   *"they will be assigned to the unit by the counselors"* while the counselor office is seeded with no
   grants at all ([What the seed ships](#what-the-seed-ships)), **on the shipped seed nobody at all may
   write a roster**. **It is recorded here instead of added to
   the table on purpose**: which volunteer office may put a child on a group's roster is the
   organization's decision, and an appendix that quietly hands it to `leaders` would be making a
   safeguarding choice on someone else's behalf (§12).
7. **`attribute.define` is held by nothing here, and an office is the wrong shape for the answer.**
   [open-questions AT-2](../open-questions.md#at-2--who-curates-the-vocabulary-and-how-long-may-a-proposal-sit)
   points at this section as the place the question gets answered, and the honest answer for a volunteer
   organization is one or two people rather than an office: **a grant aimed at `PERSON(x)`** (§1) is the
   form that fits, with a date on it, and an office would only be a way of making one person's job
   look like a policy. What is *not* the answer is leaving it unheld while proposals keep arriving
   through ordinary data entry (§12).
8. **An office name is load-bearing, because names are one namespace.**
   A bare name in an expression resolves against `role` and `person_group` together, so an office
   called `leaders` and a group called `leaders` cannot both exist, and the collision is caught on the
   write path rather than by a constraint (there is no constraint spanning two tables)
   ([D-101](../decisions/round-10b.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree),
   [D-081](../decisions/round-06.md#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now)).
   Every `selector_type.code` is reserved on top of that, so an office called `MEMBERS` is refused when
   it is saved rather than silently rewriting every expression in the system. **`audience_admin` is
   therefore a name with a second duty**: as well as saying who may edit audiences (§5a), it occupies a
   name no group may take — and note that it grants nothing over `person_group` at all, so whoever
   manages audiences and whoever manages groups may be, and here are, different people.

---

## 12. Open issues

- **The catalog's disposition is settled; its contents are not.** It stays comprehensive and
  granular ([D-055](../decisions/round-04.md#d-055--the-permission-catalog-is-deliberately-comprehensive-and-granular)),
  so there is no "prune this down" review to do.
  What remains is *additive*: each unbuilt module brings its own permissions as it is
  specified, and unused rows cost nothing.
- **Which offices' grants carry `MEMBERS` is a decision with no default recorded anywhere.**
  The answer is written into a grant's expression, and the control D-100 nominated for it exists — as a
  section of a page, not a report: **the `Unusual` section of the tab
  on the permissions page lists live grants naming a `ROLE(…)` operand whose expression contains no
  `MEMBERS`** (§11). Nothing is refused and nothing is warned when such a grant is saved.
  *Why: that test fires on the intended case as often as on the mistake, and a prompt that cries
  wolf teaches the writer to route around it, so
  [F-13](../open-questions.md#f-13) closed on the weaker half on purpose
  ([D-109](../decisions/round-13.md#d-109--nothing-a-rule-names-is-deleted-deprecated-hidden-disabled--and-a-tab-instead-of-a-report)).*
  What is still owed is the thing F-13 itself nominates: whether those `MEMBERS`-less office grants turn out
  to be mistakes or choices.
- **Nothing bounds what a holder of `access_grant.create` may write.**
  So **anyone with `access_grant.create` can grant `system.admin` to anyone, including themselves**, and
  the only remaining guard is `applies_to = unit`, which stops the *shape* of the grant and not the act
  (§1, §7). *Why: the level ladder was still doing this one job — a grant could not carry a rank above
  its writer's own — and
  [D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)
  deleted it without replacing that ceiling.* Whether the answer is a second code for
  granting the `system.` namespace, a two-person rule, or "the audit trail and a small organization's
  judgment" is open, and it is the sharpest hole in this file.
- **`event.grant_access` may be a code with no subject, and this appendix will not delete it.**
  What distinguishes it from `access_grant.create` is the scope alone (§8a). Either it is a scoped
  front door onto the same table — in which case the catalog should say so and the two codes'
  relationship should be an invariant — or it is a code with no remaining subject, which is the class of
  bug D-068 made visible. **It is left in the catalog, marked**: deleting a
  code because one mechanism died is the events module's call, not an appendix's.
- **A `deny` that matches no `allow` is invisible, and D-099 asks for a report nobody has written.** The
  new integrity report is *"a live deny matching no live allow is dead weight"* (§9 restates it). It is
  not the same question as integrity check 18's — that one asks which **permissions** no grant names,
  this one asks which **grants** do nothing — and it is easy to under-build: a deny aimed at a set that
  currently resolves nobody looks identical to a deny that is working. Open only as a report with no
  owner; the semantics are settled.
- **A leaf that names nothing is still the empty set, and it is also a line on a page.**
  `EVERYONE - PERSON(x)` with a dead `x` subtracts nobody and therefore still denies everybody, and
  nothing is refused at save because a leaf is broken
  ([D-106](../decisions/round-11-12.md#d-106--a-failed-operand-stays-the-empty-set-the-missing-half-was-a-report-not-a-refusal)).
  What makes the two cases tellable apart is the listing: **an audience carrying a leaf that does not
  resolve is listed, for the
  audience's owner, in a second column of the page
  [F-21](../open-questions.md#f-21)
  already asks for** — and it is the thing that separates the two rows this bullet is about: a deny over a
  set that is genuinely empty, and a deny whose operand has quietly stopped resolving. **The direction is
  the fact worth carrying, not a volume**: a failed operand on the `+` or `*` side *narrows* the set, and a
  failed operand on the `-` side *widens* it, so `-` is not the noisy operator, it is the only one whose
  failed operand can grant — and a check that "fails closed" on that side is fail-closed and
  lockout-everybody in the same step. **And one thing is not a failure at all**: a person with no birth
  date is not a broken `OLDER(18)`. The operand resolves perfectly well, to the set of people who are that
  age on the date being checked, and that person is simply not in it, exactly as a person with no
  membership row is not in `MEMBERS`. A missing value on the person being asked about never reaches the
  report, which is the distinction the page has to preserve or it pages about every incomplete import in
  the legacy corpus. **The page is a query with an owner, not a guard** (D-081's phrase, applied to it by
  D-106): no save depends on it, and the catalog mints no code for reading it.
- **`audience.manage` is one code over an expression, and the largest act it covers is still
  unmarked.** Composition *is* the expression now
  ([D-101](../decisions/round-10b.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree)):
  an inclusion is an ordinary `+` beside a leaf, and the leaf that should worry everyone is `EVERYONE`.
  **There is no smaller act to grant either** — *may tick names on this audience* without *may rewrite
  the rule* is not a shape any code could cover, because
  [D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)
  deleted the list those names sat on; if the need is ever real it is a new question
  about the editor.
  The shape of the concern is one edit long: **whoever can edit one expression can
  widen every live grant aimed at it**, including by writing `EVERYONE`, which is legal, reachable, and
  resolves to non-members and the public — **and the reach is now transitive**, because
  [D-103](../decisions/round-10b.md#d-103--an-audience-may-name-another-audience) lets one audience be
  named inside another, so editing a widely-named audience widens every grant aimed at every audience
  that names it. Either composition is documented as plainly inside
  `audience.manage` — accepting exactly that consequence — or it gets a code of its own; **no code was
  invented here to fill the gap**. The interim control is the editor showing the expanded set and the
  affected grants *before* the save, which is a user-interface requirement carried in
  [../domain/06a-audiences-and-selectors.md §6.2](../domain/06a-audiences-and-selectors.md#62-audiences--an-expression-over-named-sets),
  not a permission.
- **Nothing bounds what a permission check costs.** There is no depth bound:
  `audience.selector_depth_limit` is gone, and with it the save-time refusal that made *"a check costs a
  bounded amount"* true; the two cycle walks
  — inside the tree, and across audiences through every `AUDIENCE(x)` leaf — are the only structural
  guard there is
  ([D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)).
  An expansion that never terminates is still refused, because acyclicity is what the deletion left
  intact; what a *terminating* expansion costs is bounded by nothing, and that is
  **accepted, because the size is stated**: a few hundred
  people in the organization, a few dozen registrants on a typical event, a big camp on the order of two
  hundred — a size stated rather than measured, with the trigger written down beside it that a few
  thousand people, or a thousand registrants on one event, reopens the question
  ([D-112](../decisions/round-13.md#d-112--the-systems-scale-is-stated-hundreds-of-people-tens-of-registrants-per-event)).
  **What exists for looking at any of this is the tab on the permissions page**, which lists rules that
  name something deprecated, hidden or disabled, or that fail to resolve, and says nothing about how wide
  any of them is
  ([D-109](../decisions/round-13.md#d-109--nothing-a-rule-names-is-deleted-deprecated-hidden-disabled--and-a-tab-instead-of-a-report));
  there is no standing report of the widest and deepest audiences, and the registry diff that would catch
  a prose code naming no row is run by hand — D-081's *convention, not a guard*.
  No number makes an audience too wide and
  nothing in the language caps one. The two rules that must outlive any growth are already written —
  a check compiles its expression to a predicate and never materializes the set, and a listing is
  paginated — so this module gets slow before it gets wrong. The catalog mints
  nothing against it: no code governs expansion, and none could — whoever can write `EVERYONE` into
  an expression already holds `audience.manage` (§5a).
- **A grant's reach moves with the calendar, and there is no write to mark the moment.** `OLDER(n)` and
  `YOUNGER(n)` are ordinary named operands composed by the same three operators as every other (§1), and
  they are the first whose membership changes **with no write at all**
  ([D-107](../decisions/round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)):
  a person turns eighteen, joins the set, and no row was touched — which is exactly why age *bands*, with
  the per-person expiry dates they would need, are not in this design. **Nothing is invalidated, because
  nothing that depends on a person is stored:** a check resolves, a request memoizes, and the only cached
  thing is a compilation of an expression root plus `ruleset_version` — bumped by writes to
  `audience_operand` and `selector_type`, the two tables whose rows change what an expression *means*, and
  holding no person and no item
  ([D-114](../decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation)).
  A birthday, a period reaching its own `valid_to`, a registration write and a membership termination each
  move the answer at the instant they happen.
  **What follows is open, and it is only the cost:** nothing bounds such a check, because the bound this
  system had was a depth bound and
  [D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)
  deleted it, so an age-bearing expression is one more set to expand and it is bounded by nothing; that is
  [F-21](../open-questions.md#f-21),
  and the catalog mints nothing against it:
  **no code, no column, no number, no threshold.** **Whom a derived set reached is not a finding here.**
  The preview a writer looked at is a workbench, never a record, and **the record is the expression**
  ([D-110](../decisions/round-13.md#d-110--the-expression-is-the-record-of-whom-a-grant-reached)):
  the audit row says *this person wrote these words, about this item, on this date*, and what the preview
  printed beside it is logged as **a rendering on a date**, never as a statement of who was in it. Ask whom
  a grant reached in May and the model evaluates those words against the data of May: there is no list to
  read back, and these documents do not promise the answer. **What that costs is named here rather than
  found sideways — an edit to a shared audience is a retrospective edit to every rule that names it** — and
  the control is the editor printing the resolved set before such an edit saves. *Why: this rests on a
  premise the organization supplied — that the people writing the rules know what they are doing — written
  down in
  [D-107](../decisions/round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)
  with its two limits, and it is affordable only because nothing a rule names is deleted, so the words keep
  resolving
  ([D-109](../decisions/round-13.md#d-109--nothing-a-rule-names-is-deleted-deprecated-hidden-disabled--and-a-tab-instead-of-a-report)).*
- **`audience.view` carries no sensitivity mark, and the thing it shows is a list of people.**
  A grant aimed at a name resolves through dated holder rows, group rosters and `MEMBERS`, and an
  expression containing `EVERYONE` resolves to the whole organization and beyond it. Whether reading a
  resolved expression needs a grade of its own — or whether `person.view` already covers it and the
  *display* is the leak to watch — is unsettled (§5a).
- **The shipped seed contains no office grants at all, so D-100's 1 January assumption is unmet.** The
  entry assumes *"the seeded `is_system` role set contains at least one such office"* written without
  `MEMBERS`; the seed is one empty role and one grant about event answers (§11). Either the seed grows
  an administrative office, or **the first January after go-live is a support call** — and the seed
  control *"seeded grants carry `MEMBERS`, so the path of least repetition is the safe path"* has
  nothing to apply to, which means every office grant in existence will have been written by hand.
- Whether `report.*` should be per-report permissions or one `report.view` with
  row-level filtering.
- Whether the organization has offices this catalog does not anticipate (a chaplain, a
  quartermaster, a camp chief). **This is answerable by the organization itself** rather than by a
  change to the data model and a migration — one `role` row and some grants — which is the point of
  roles being runtime data. Since D-098 the same is true of a set of people who simply do things
  together, and the two are told apart by which table they are in and therefore by which code protects
  them (§5a).
- Which seeded audiences the organization needs beyond `everyone` and `all_members`, and who may create
  a `person_group` — `audience_admin` is proposed, and it is an office rather than a unit leader's extra
  code now that there are no units
  ([D-042](../decisions/round-02-03.md#d-042--grants-may-target-audiences-not-only-individuals),
  [F-5](../open-questions.md#f-5)).
  **There are no kinds of audience** — one expression language over named sets, no built-in versus
  named split and no filling rules
  ([D-091](../decisions/round-09.md#d-091--a-permission-group-is-a-rule-and-a-list-at-once-and-a-rule-may-name-another-group),
  [D-101](../decisions/round-10b.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree)) —
  so this is genuinely two questions: which `selector_type` operands ship, which is thirteen and is
  written once in §1, and who may create a group, which is `person_group.create` (§5a).
  **No operand names a person's guardians:** the channel carries a level over a child, not a set
  ([D-113](../decisions/round-13.md#d-113--the-guardianship-channel-has-no-expression-guardians-is-not-a-selector)),
  which closes the last part of F-5; and `WHITELISTED`, the one name still without stored state, is
  [F-20](../open-questions.md#f-20)'s question and not a gap in the registry.
- **Which office may put a person on a group's roster is unanswered, and on the shipped seed nobody
  may.** `person_group.member.manage` is the whole of the right to place a person in a set: one code,
  `applies_to = unit_and_item`, never self-scoped, and the only thing between a person and a roster
  (§5a, §11 property 6). The
  catalog's side is settled; what is missing is a decision the organization records as `role` rows and
  grant rows, not a code.
- **`message.broadcast` has one scope, and messaging has not ruled on what that means.**
  There is one unit scope
  ([D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)),
  so a broadcaster held there reaches everyone
  ([D-077](../decisions/round-06.md#d-077--messaging-is-direct-by-default-broadcast-is-an-ordinary-scoped-permission-and-the-recipient-chooses-the-channel)),
  and the narrower audience has to be a
  grant aimed at a `person_group`, which is a different shape of decision (who may create the group, and
  whether it is the *broadcast* grant or the group roster that carries the ⚠). §10 records it as
  messaging's call; **the catalog has not silently re-specified it either way**, including whether the
  code should become `applies_to = unit_and_item`.
- **`membership.manage` does not exist, and five places in these documents refuse it.** D-099
  quotes the organization's own observation — *"on an event, `membership.manage`, or `event.create`, make
  no sense"* — the domain model and the authorization module each restate that sentence as the reason
  `applies_to` exists, and the events page carries a refusal row naming the code. **This catalog has
  never registered it** — membership acts are `membership.activate`, `.lapse`, `.suspend`,
  `.terminate`, `.backdate` and the request pair (§4) — and **no code is minted here to make an example
  true**: a refusal that names nothing refuses nothing, which is the class of bug D-097's `unit_leaders`
  correction exists to warn about. Either those five places re-point the example at a registered code —
  `membership.terminate` is the exact fit, a fact about a person at the unit that no event owns — or the
  code is registered here first, and then it owes what every registered code owes: a `right_kind`, an
  `applies_to`, a ⛔ mark, and a row in §4. **This was one instance of the gap D-104 closes as
  [F-19](../open-questions.md#f-19):
  a code is a seeded row, this catalog is prose about rows, and the check adopted is a two-way report
  over the seeded registries, run by hand.** D-104 supplied the grammar and the report; **it did not
  re-point these five sentences**, and that repair still belongs to whoever owns each of those pages.
- **The registered spelling of a code is this catalog's, and prose is prose.** `event.answer.view` is
  singular — the seeded grant in §11, the code in §8a, and no other spelling
  ([../data-model/08a-event-guards-and-checks.md §8](../data-model/08a-event-guards-and-checks.md#selectors-that-bind-to-an-event)
  records how that was settled, and **the catalog is the arbiter**). The case that did not settle quietly
  is the finding worth carrying: a door-scanning capability was argued over at length and exists
  **nowhere** — not in this catalog, not in the events module, not in the ERD, not in the decision log —
  so nothing ever refused it, because since
  [D-072](../decisions/round-06.md#d-072--the-documentation-carries-no-sql-the-schema-is-the-orms-job)
  these documents *are* the specification and a permission legally exists only as a seeded row; the
  question that ends any such argument is *which seeded row carries this?*
  ([D-104](../decisions/round-10b.md#d-104--a-permission-codes-last-segment-is-an-action-and-a-registry-that-prose-contradicts-is-a-fiction)).
  What survives of it is §1's three rules, the two-way registry report D-104 adopts, and a presence story
  that is `event.presence.mark` and nothing more (§8a,
  [D-067](../decisions/round-05.md#d-067--presence-is-a-three-valued-fact-on-the-registration)).
  **If door scanning is ever wanted it arrives as an open question and then a decision entry naming the
  permission, the artifact that rotates and who may reprint it — not as a code beside a paragraph about
  a door.**
- **`attribute.define` is in the catalog and in no seed office, and that gap is the open half of the
  design.** The permission and its rules are settled (§2); who holds it, and how long a `proposed`
  code may sit before it is an embarrassment rather than a queue, are not — tracked as **AT-2** in
  [../open-questions.md](../open-questions.md#at-2--who-curates-the-vocabulary-and-how-long-may-a-proposal-sit),
  and §11 property 7 records the shape the answer should take (a dated grant aimed at one person, not an
  office). The risk of leaving it unheld is specific and slow:
  proposals keep arriving through ordinary data entry, and a vocabulary nobody curates stops
  answering questions while still storing everything
  ([../data-model/09-attributes.md §8](../data-model/09-attributes.md#8-integrity-checks)).
  **The import half of this is now answered**, and only that half: the codes the legacy batch's
  column→code map names arrive `live`, because a curator reads the map as one object before the batch
  applies, so the queue does not open several-hundred-deep on day one
  ([D-090](../decisions/round-07-08.md#d-090--the-legacy-corpus-is-thousands-of-roster-rows-with-numbers-and-no-money),
  [../domain/03-identity-and-legacy.md §7](../domain/03-identity-and-legacy.md#7-legacy-import-pipeline)).
  Who holds the permission afterwards, day to day, is still what is open.
**Everything this file used to leave open is answered in the decision log, not here.** Whether a grant
carries a strength, a locality, or more than one code
([D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality));
whether the unit is a row or a scope
([D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)); whether
an event has an owner
([D-102](../decisions/round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it));
whether leadership is a position or an office
([D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape));
whether `PERSON(x)` is in the selector language and whether `LIST` still is (it is, and it is not — the
registry table is
[data-model/05a §8](../data-model/05a-audience-and-grammar.md#8-audience--grants-that-target-a-set-of-people),
and it is the only place the number of seeded operands is written); whether presence is a set anyone may
be granted over (it is not, on the argument that always carried it, and §1 says why); whether a code's
last segment must be an action (it must — §1,
[D-104](../decisions/round-10b.md#d-104--a-permission-codes-last-segment-is-an-action-and-a-registry-that-prose-contradicts-is-a-fiction));
and the smaller reversals this section used to list one struck line at a time. **Each of those is one
entry in [decisions/index.md](../decisions/index.md), findable by number, and each names what enforces the
rule now** — the discipline
([D-081](../decisions/round-06.md#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now))
this appendix was written under. **What is open is the list above this paragraph, and nothing else in
this file.**

All tracked in [../open-questions.md](../open-questions.md).
