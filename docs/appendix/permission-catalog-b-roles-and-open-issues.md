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

**What cannot be expressed, and was declined rather than left unbuilt.** A court order giving one parent
access to everything about their child except the medical file **cannot be expressed**: `view` is one level
over the whole of a child's record, so a grandmother granted roster visibility gets the fee history with
it. [D-083](../decisions/round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)
put that story to the organization directly and it was refused on the merits — *"medical data is not
different in any way"* — and the same answer removed the referent: there is no medical record inside the
person record to be shut out of, because everything other than name, gender and age is one class of data
reached by `person.view` and governed by the guardian's level whole
([../domain/08-person-data.md](../domain/08-person-data.md)). *"Read everything except the diagnoses"* is
therefore not a sentence waiting on a mechanism; it is one the organization declined to want, which is why
[E-7 closed](../open-questions.md#e-7)
as a dissolved question rather than an answered one. **Read the inexpressibility as settled, not as pending
work.** Reopening it means producing the case that was declined, not finding the code that was deleted.

**What still holds:**

- **A guardian's authority is per guardianship row.** The channel is entered by whose record the act
  touches and answers only about that row
  ([D-079](../decisions/round-06.md#d-079--the-guardianship-channel-is-entered-by-shape-not-by-permission-name)),
  so a guardian cannot do organization-wide things and cannot reach a different dependent's records. What
  `write` means is *this row's dependent, both kinds*: it covers the `write` codes and the `read` ones,
  where `view` covers only `read` and `none` covers nothing — compared against `permission.right_kind`, not
  against a level (§6).
- **A deny still reaches the channel.** A live deny beats every allow that applies, at any scope and in
  any channel (D-032's first half, now its entire content, restated by
  [D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)),
  so *"this guardian, nothing"* remains expressible: a `deny` at the unit aimed at the person, `PERSON(x)`.
  There is no *narrow* deny — no operand names one child's guardians to aim one at, because the channel
  resolves no sets and the name an expression can carry here is the person's
  ([D-113](../decisions/round-13.md#d-113--the-guardianship-channel-has-no-expression-guardians-is-not-a-selector)).
  What was lost is the narrowness, not the refusal.
- **A guardianship at `none` grants literally nothing**, so **being a guardian still grants nothing by
  itself** — the safeguarding property that motivated the eighteen codes survives without them.
- **An event's answers are not guardian data.** They are read through `event.answer.view`, a permission on
  the grant side, carried by the seeded grant to `ORGANIZERS` (§8a), and never were a guardian's
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
| `message` | `message.send_direct`, `message.broadcast` | **Decided in shape, undesigned in detail** ([D-077](../decisions/round-06.md#d-077--messaging-is-direct-by-default-broadcast-is-an-ordinary-scoped-permission-and-the-recipient-chooses-the-channel)). Everyone may send direct; `broadcast` is an ordinary **scoped** permission. **D-077 wrote "one code at two scopes" when there were two scopes to have** — a unit and the organization; after [D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row) they are the same scope, so the code reaches everyone when it is held at the unit, and the narrower reading the pair used to buy would have to be a **grant on a `person_group`**, reaching that roster — which is the shape D-099 makes available and D-077 could not have. *Which of those messaging means, and whether `message.broadcast` should be `applies_to = unit_and_item`, is messaging's decision, not this catalog's* (§12). Recipient chooses the channel, which is not a permission at all. **A direct message to a minor is mirrored to that minor's guardians and the sender is told it will be** — no permission, no age branch in the resolver ([D-082](../decisions/round-07-08.md#d-082--a-direct-message-to-a-minor-is-mirrored-to-the-minors-guardians)) |
| `partner` | *(namespace)* | For external organizations, if the model expands. |

**What each new resource owes the authorization module changed in round 10, and the old sentence about
it is deleted rather than adapted.** ~~Generate each resource's `permission_level` rows at the same
time.~~ That table is deleted by
[D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality),
so what a new resource owes is now four things, all of them cheap and all of them required: **codes**
(two or more lowercase segments, first segment = `resource`), each with a **`right_kind`** — `read` or
`write`, required, because that column is a guardian's answer and not a hint (§6) — each with an
**`applies_to`**, checked on save (§1); and a row in **`grant_scope_type`** if its records are things a
grant can be written on, which is what makes a document or a group an item at all.

---

## 11. Roles — proposed seed set

**A starting point, not a specification.** *The heading is kept because its slug is cited from the
decision log and from four other pages, not because the words still fit:* this section used to list
roles with their permissions attached to them, and a role has no contents now. ~~Scope required ·
`Req.` · Waives gate · Key permissions~~ — `role_permission` is deleted, with `role.scope_required`
and `role.requires_membership` beside it
([D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)),
so **the codes an office carries are the live grants whose expression names it**: one row per code,
each with its own scope and its own period. `MEMBERS * ROLE(treasurers)` on `fee.create` is one such
row, and it — not the office, and not a bundle table nobody read — is what lets a treasurer issue a
fee. What a role *is* now is two things: a name a grant can be aimed at, and the register that answers
*who held this in 2023* (`role_holder` — which is exactly why
[F-12](../open-questions.md#f-12) is closed, with the
answer *no*: a holder row names one person). Roles stay runtime data — the organization creates them,
names them, writes and closes their holders, and deletes the unused ones
([§7](../data-model/05-authorization.md#3-role--an-office)). **What is no longer runtime data
is reach**, which is administered through `access_grant.create` and `access_grant.revoke` and is
therefore reviewed in `access_grant`, not in a role editor (§7).

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
| `event.answer.view`, item-scoped on an event, aimed at `ORGANIZERS` | `access_grant` | — | — | The one rule that used to be prose in the resolver: answers are read by that event's organizers ([D-061](../decisions/round-05.md#d-061--event-answers-are-read-by-that-events-organizers), amended by [D-102](../decisions/round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)) |

**Why a role and not a group**, when D-098's own definition of a group is *"a temporary set of members
that do events together"* and counselors are neither temporary nor event-shaped: the table decides
**which code protects the set**, and every safeguarding convention in this area hangs from that answer
being unchangeable by an ordinary grant — `role.*` is 🔒🔒, `person_group.member.manage` is ⚠
(§5a). **It ships `is_system` so that an editor refuses to delete it**, and so that the §7 rule
*deletable only if never held, and never if it is a system role* has something to refuse.

**Nothing in the seed names `ROLE(counselors)`, and that is the design rather than an omission.**
Being a counselor confers nothing until someone writes the grant
([D-005](../decisions/round-01a.md#d-005--permissions-are-grants-never-derived-from-identity));
D-100 repeats the sentence D-042 has always said. **What that leaves open is not a permission but a
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
| `leaders` | the thirteen `event.*` codes (§8a), `membership.view` ⚠, `person_group.view` ⚠, `report.membership.view` ⚠ — **sixteen rows** | `ROLE(leaders)` | **this is what `unit_leader` was**, including its `Req. = no`: volunteers, so no `MEMBERS` (property 4) — and nothing bounds it to one unit any more |
| `audience_admin` | `audience.view`, `audience.manage` ⚠ | `MEMBERS * ROLE(audience_admin)` | §5a, including the naming rule this office is subject to |
| `identity_reviewer` | `person.merge` 🔒, `import.view` ⚠, `import.apply` 🔒 | `MEMBERS * ROLE(identity_reviewer)` | and **no `person.view`** — property 5 |
| `auditor` | `audit.view` ⚠⚠, `audit.export` ⚠⚠, `report.view` ⚠ — **read-only, no writes** | `ROLE(auditor)` | **no `MEMBERS`**: an auditor who forgets to pay must not lose the read (property 4) |

**`Term` left the table and went to two places, and that is worth knowing before you set either.**
The old table had one twelve-month column per role. An office is now held for a period
(`role_holder.valid_from`/`valid_to`) **and** every one of its grants has a period of its own, so an
office's reach is an intersection of up to twenty dates, and the question *when does this person stop
being able to do that?* has more than one right answer. Nothing forces either kind of row to end —
[D-071](../decisions/round-05.md#d-071--nothing-forces-a-role-assignment-to-end-the-gate-and-the-report-are-the-control)
transfers to `role_holder` intact, and the control is still the report.

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

1. **`registrar` omits `person.merge` and `person.redact` by not having those rows, and the exclusion
   was always this literal.** It used to be phrased as a caveat about a wildcard's prefix match, and as
   a caveat it was worth a paragraph; now it is simply the two rows nobody inserted, visible in
   `access_grant` with a date and an author and alarmable like any other row. `identity_reviewer` is
   the office that *does* hold `person.merge` — and since round 8 `person.merge` is the whole of
   identity correction: merging, reversing a merge, and deciding a sign-up collision (§2) — listed
   beside `registrar` so the difference between the two is legible. **An office that bundles a resource
   *including* its 🔒 codes should be named for that**, since nothing else records the choice any more;
   the wording here used to say *irreversible* codes, and
   [D-087](../decisions/round-07-08.md#d-087--merge-chains-stay-because-reversing-a-merge-is-a-supported-operation)
   removed one of the two that wording pointed at, so the marker is the honest referent —
   `person.redact` is irreversible, `person.merge` is undoable but unions permissions the moment it
   runs.
2. **`leaders` holding `event.*` means thirteen explicit rows** (§8a), and a fourteenth added later is
   *not* in the office until someone writes it. Integrity check 18 surfaces an orphaned permission — one
   **no live grant names** — and it does not surface *"this office arguably should have had it."* That is
   the cost D-068 accepts, and since round 10 it lands here rather than being absorbed silently by a
   resolver: with `role_permission` gone there is no per-office list left for a reader to compare a
   catalog row against, so a documented code that nothing grants is now invisible in a way it never was.
3. **`auditor` is an office that reads the whole person record, and does it without `person.view`.**
   `audit.view` is graded ⚠⚠ in §8 precisely because the payload is a second copy of the record, so
   this row grants a ⚠⚠ read over what the system believed about a child and when it believed it.
   Since [D-088](../decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)
   that read has a floor it did not have before: payloads older than 24 months are emptied, so what is
   exposed reaches back two years and no further, while the who-did-what-to-which-row part reaches back
   for the life of the system. That bounds this row's exposure and does not soften its grading. Nothing
   here forbids it — it is a plausible office — but the row must not be described to anyone as "just the
   logs", and it is scoped and dated for the same reason the ⚠⚠ rows above it are.

### The gate moved into the expression

~~`Req.`~~ was `role.requires_membership`: whether the office stopped conferring anything the moment
its holder's fee lapsed
([D-039](../decisions/round-02-03.md#d-039--member-permissions-require-a-current-paid-membership)).
~~Waives gate~~ was the separate, person-level *permission* `system.gate_exempt`
([D-051](../decisions/round-04.md#d-051--the-membership-gate-is-waived-by-a-permission-not-only-by-a-role-flag)),
and the two columns answered different questions and were never alternatives: the flag exempted
everyone holding an office, everywhere, while the permission exempted one named person across every
office they held. **Both columns, both mechanisms and the resolver clause that implemented them are
deleted by D-100.** `MEMBERS` is an operand now, evaluated live on the checked date, and whether an
office survives its holder's lapse is a property of the expression written on the grant:

| Old mechanism | New expression | What the writer is saying |
|---------------|----------------|---------------------------|
| The gate applied to an office with `requires_membership = true` | `MEMBERS * ROLE(x)` | this office is for people who are members right now |
| The gate waived for a whole office | `ROLE(x)` | written **without** `MEMBERS`; a lapse in the fee ledger does not stop this office |
| The gate waived for one named person (`system.gate_exempt`) | `(MEMBERS * ROLE(x)) + PERSON(y)` | one person is the exception, and the exception is visible to everyone who reads the grant |

**A second grant aimed at `PERSON(y)` is the other way to write the third row**, leaving the gated
expression alone; D-100 keeps both legal and calls the second arguably clearer for a permanent
exception, because it keeps the exception off the expression everyone else reads. What is gone is the
*permission* — not the ability.

**The posture reversed, so name the new failure instead of burying it.** The gate used to be
**default-on**, which made forgetting it impossible and waiving it a deliberate act. It is now
**opt-in per grant**: an expression written `ROLE(treasurers)` with no `MEMBERS` authorizes a lapsed
member, silently, for as long as the grant lives. Three controls, none of which is the resolver:

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
- **Import completeness.** The counselor office is only as correct as the roster behind it, and the
  gate used to fall out of membership alone; the duty is stated above, and it fails closed.

**One value in the old table was never a preference, and it is the one to copy carefully.**
`system_admin` was marked *Waives gate = yes* because on 1 January the expiry sweep of
[D-040](../decisions/round-02-03.md#d-040--the-fee-expires-yearly-a-date-tracked-renewal-window-replaces-a-grace-status)
lapses every membership in the organization including the administrator's, and without the exemption
the person who would repair the system loses the ability to use it on the day it breaks. That is a
property of the system, not a policy choice, and it is carried now by **writing that one row
`ROLE(system_admin)`, with no `MEMBERS`** — which turns a flag nobody read into an expression with
an outage attached to getting it wrong. The loud mistake is the opposite one: writing
`MEMBERS * ROLE(system_admin)` "for consistency" reproduces the lockout, silently, with no error
message — D-051's documented hazard outlives the mechanism that produced it. **Whether any office
in the shipped seed is written this way is a different question, and the answer is no: the seed
contains no office grants at all** ([What the seed ships](#what-the-seed-ships), §12).

> **~~`registrar` holding `unit_participation.view` at organization scope is not a bug, and it will be
> read as one.~~** Both halves of that note died with the hierarchy. The code is deleted (§4), and the
> oddity it defended — a scope that matched only the root's own rows and refused to read into a pack's
> roster, because crossing into a sub-unit took a `scope_exposure`
> ([D-049](../decisions/round-04.md#d-049--the-root-may-not-read-into-its-sub-units-scope_exposure-is-the-only-crossing),
> [D-041](../decisions/round-02-03.md#d-041--belonging-to-a-sub-unit-is-a-participation-record-not-a-membership)) —
> has no subject after [D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row):
> there is one scope, so there is nothing for it to fail to reach, and `membership.view` answers *who is
> in the organization?* on its own. **What is genuinely lost is the mistake nobody can make any more.**
> The old hazard was a well-meaning administrator widening a parent's role to see a child unit's roster,
> silently reversing D-049; there is no child unit to widen toward, and the equivalent act today — a
> grant at the unit — is not a hazard but the ordinary case.

**Eight properties worth noting: six carried over from the old table and retargeted, two new because
round 10 created them:**

1. **`membership_approver` is separate from `registrar`.** Deciding who becomes a member is
   a different act from processing records. If your organization wants one person to do
   both, hold both offices — which now literally means two holder rows and two sets of grant rows —
   but keep them separately attributable, because that separation is the only thing the office names
   buy.
2. **`safeguarding_officer` holds `membership.terminate`.** The permission to end someone's
   membership sits with the person responsible for safeguarding, not with whoever chases
   fees. This is deliberate. Note that the office **lost** `person.background_check.*` and
   gained nothing in its place, because the organization records no background checks
   ([D-043](../decisions/round-02-03.md#d-043--no-background-checks-are-recorded-in-this-system)).
   What it also does not have here is `person.view`: three rows, and the ⚠⚠ one is the report rather
   than the record. **If working a case needs the record, that is a fourth grant row** — scoped, dated,
   attributable, and visible to anyone who asks what this office can read, which is the review §2 moved
   to when it graded `person.view` ⚠⚠.
3. **No office is a guardian.** There used to be a rule that no role bundles
   `dependent.*`, and the namespace it named no longer exists
   ([D-074](../decisions/round-06.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular)).
   The safeguarding property it protected is the one that survives, restated against the mechanism
   that now provides it: **the guardianship channel is only consulted when the subject of the act
   is someone else, and it only finds a guardianship row.** Leadership is not guardianship, so no
   office hands anyone a guardian's right over a child — not the right to act for that child, and not
   the row that decides what the family may see.
   **What an office can now do, and does openly, is read the child's record.** That sentence used to
   be false, and [D-083](../decisions/round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)
   is why it is not: with no privileged subset inside the person record, a leader granted `person.view`
   reads the whole of a member's descriptive data, allergy list included
   ([../domain/08-person-data.md](../domain/08-person-data.md)) — **and round 10 widened what one such
   grant means**, because after D-097 there is no narrower scope than the unit for a code about people,
   so that single row reaches every member in the organization (§1). Nothing about leading anything
   grants it: no channel opens on its own, and the row that would is explicit, scoped, dated and
   readable in `access_grant`. That is also why §2 now grades that code ⚠⚠: the safeguarding review
   moved from *"is there a code we kept out of offices?"* to *"which grants were given this one?"*,
   which is a question the catalog can actually answer.
   **Do not re-derive the old rule as a list of codes to keep out of offices** — the rule is about
   the channel, and there is no code left to quarantine.
4. **`system_admin`, `leaders` and `auditor` are the three example offices written without `MEMBERS`,
   and the last two are the successors to the old `Req. = no`.** The rule the old column followed was
   one sentence — **staff-like offices working on the organization's own records require a membership;
   volunteer-facing offices do not** — and it survives as a writing habit, because a resolver clause
   does not survive otherwise.
   The failure it prevents is specific: the volunteer whose own fee is unpaid still runs the Thursday
   meeting, and must not lose their roster the night it lapses. ~~The corresponding
   `position.requires_membership` stays `true`, so the unpaid volunteer shows up on a chase-up report.~~
   Positions are deleted (D-100), so the noticing moved: that volunteer's office now appears in the
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
   omission** — the sentence used to be about `unit_participation.manage`, and the code is deleted. What
   D-095 decided has not moved: joining a set is somebody else's act, the write is never self-scoped, and
   this code is now the only thing standing between a person and a group's roster (§5a). As written,
   `leaders` may *see* a roster and cannot write one. **The gap is wider than it was, not narrower**,
   because the answer behind D-095 was *"they will be assigned to the unit by the counselors"* — and the
   counselor office is seeded with no grants at all ([What the seed ships](#what-the-seed-ships)), so
   on the shipped seed nobody at all may write a roster. **It is recorded here instead of added to
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
8. **An office name is now load-bearing in a way it never was, because names are one namespace.**
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
  so there is no longer a "prune this down" review to do.
  What remains is *additive*: each unbuilt module brings its own permissions as it is
  specified, and unused rows cost nothing.
- **Which offices' grants carry `MEMBERS` is now a decision with no default recorded anywhere.**
  ~~Both were attributes of roles, and roles are runtime data the organization administers, so the
  values shown were reasoned defaults~~
  ([D-039](../decisions/round-02-03.md#d-039--member-permissions-require-a-current-paid-membership),
  [D-051](../decisions/round-04.md#d-051--the-membership-gate-is-waived-by-a-permission-not-only-by-a-role-flag)
  — both mechanisms deleted by D-100). The answer is now written into a grant's expression, and the control
  D-100 nominated for it exists — as a section of a page, not a report: **the `Unusual` section of the tab
  on the permissions page lists live grants naming a `ROLE(…)` operand whose expression contains no
  `MEMBERS`** (§11). Round 13 retired the questions this bullet said the specification still owed. *Who runs
  it, how often* has no referent, because a tab is not run; *a warning at save time or a listing afterwards*
  was F-13, and it closed on the weaker half on purpose — nothing is refused and nothing is warned at the
  save, because that test fires on the intended case as often as on the mistake, and a prompt that cries
  wolf teaches the writer to route around it
  ([F-13](../open-questions.md#f-13),
  [D-109](../decisions/round-13.md#d-109--nothing-a-rule-names-is-deleted-deprecated-hidden-disabled--and-a-tab-instead-of-a-report)).
  What is still owed is the thing F-13 itself nominates: whether those `MEMBERS`-less office grants turn out
  to be mistakes or choices.
- **Nothing bounds what a holder of `access_grant.create` may write, and the catalog no longer
  pretends otherwise.** ~~A grant could not carry a level above the writer's own~~ — that was
  `permission_level`'s second job, and the table is deleted by
  [D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality).
  So **anyone with `access_grant.create` can grant `system.admin` to anyone, including themselves**, and
  the only remaining guard is `applies_to = unit`, which stops the *shape* of the grant and not the act
  (§1, §7). Every earlier answer to "who can grant what" is gone with it: the ceiling was the one thing
  the deleted ladder was still doing, and nothing replaced it. Whether the answer is a second code for
  granting the `system.` namespace, a two-person rule, or "the audit trail and a small organization's
  judgment" is open, and it is the sharpest hole round 10 left in this file.
- **`event.grant_access` may now be an orphan, and it is one the round created.** Its whole purpose was
  to demand a *level* over an event that the general grant path could not express; with the level gone,
  what distinguishes it from `access_grant.create` is the scope alone (§8a). Either it is a scoped
  front door onto the same table — in which case the catalog should say so and the two codes'
  relationship should be an invariant — or it is a code with no remaining subject, which is the class of
  bug D-068 made visible. **It is left in the catalog, marked, rather than deleted here**: deleting a
  code because one mechanism died is the events module's call, not an appendix's.
- **A `deny` that matches no `allow` is invisible, and D-099 asks for a report nobody has written.** The
  new integrity report is *"a live deny matching no live allow is dead weight"* (§9 restates it). It is
  not the same question as integrity check 18's — that one asks which **permissions** no grant names,
  this one asks which **grants** do nothing — and it is easy to under-build: a deny aimed at a set that
  currently resolves nobody looks identical to a deny that is working. Open only as a report with no
  owner; the semantics are settled.
- **A leaf that names nothing is still the empty set, and it is now also a line on a page.** Nothing about
  resolution moved: `EVERYONE - PERSON(x)` with a dead `x` still subtracts nobody and therefore still
  denies everybody, and nothing is refused at save because a leaf is broken
  ([D-106](../decisions/round-11-12.md#d-106--a-failed-operand-stays-the-empty-set-the-missing-half-was-a-report-not-a-refusal)).
  What arrived is the report — **an audience carrying a leaf that does not resolve is listed, for the
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
  unmarked.** ~~D-091's inclusion arm~~ is gone, and composition *is* the expression now
  ([D-101](../decisions/round-10b.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree)):
  the arm that used to need its own code is an ordinary `+` beside a leaf, and the leaf that should
  worry everyone is `EVERYONE`. What the round took away is an option, not a safeguard: the code's
  former second half — editing a `LIST`'s names apart from the rule — lost its operand when
  [D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)
  deleted the list, so *may tick names on this audience* without *may rewrite the rule* is no longer a
  shape any code could cover even if one were written; if the need is ever real it is a new question
  about the editor, not an argument that the deletion was wrong.
  The shape of the concern is unchanged and one edit shorter: **whoever can edit one expression can
  widen every live grant aimed at it**, including by writing `EVERYONE`, which is legal, reachable, and
  resolves to non-members and the public — **and the reach is now transitive**, because
  [D-103](../decisions/round-10b.md#d-103--an-audience-may-name-another-audience) lets one audience be
  named inside another, so editing a widely-named audience widens every grant aimed at every audience
  that names it. Either composition is documented as plainly inside
  `audience.manage` — accepting exactly that consequence — or it gets a code of its own; **no code was
  invented here to fill the gap**. The interim control is the editor showing the expanded set and the
  affected grants *before* the save, which is a user-interface requirement carried in
  [../domain/06-authorization-model.md §6.2](../domain/06a-audiences-and-selectors.md#62-audiences--an-expression-over-named-sets),
  not a permission.
- **Nothing bounds what a permission check costs, and that was a property of this system until this
  round.** The bound lived in `audience.selector_depth_limit` and was refused at the save, which is
  where the sentence *"a check costs a bounded amount"* came from;
  [D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)
  deleted the column, the bound and the save-time depth refusal together, and kept the two cycle walks
  — inside the tree, and across audiences through every `AUDIENCE(x)` leaf — as the only structural
  guard there is. An expansion that never terminates is still refused, because acyclicity is the one
  thing the deletion did not relax; what a *terminating* expansion costs is bounded by nothing, and that
  is now **accepted rather than merely unaddressed, because the size is finally stated**: a few hundred
  people in the organization, a few dozen registrants on a typical event, a big camp on the order of two
  hundred — a size stated rather than measured, with the trigger written down beside it that a few
  thousand people, or a thousand registrants on one event, reopens the question
  ([D-112](../decisions/round-13.md#d-112--the-systems-scale-is-stated-hundreds-of-people-tens-of-registrants-per-event)).
  **Round 13 also withdrew the report this bullet used to name:** there is no standing report of the
  widest and deepest audiences, because there are no standing reports of that kind any more — what exists
  is **the tab on the permissions page**, and it lists rules that name something deprecated, hidden or
  disabled or that fail to resolve, saying nothing about how wide any of them is
  ([D-109](../decisions/round-13.md#d-109--nothing-a-rule-names-is-deleted-deprecated-hidden-disabled--and-a-tab-instead-of-a-report)).
  Two of the three same-shaped controls D-105 counted here have therefore moved: the widest-and-deepest
  report is gone outright, and §11's no-`MEMBERS` listing is now the tab's **Unusual** section rather than
  a report somebody has to remember to run; D-104's by-hand registry diff is the one still a report
  (D-081's *convention, not a guard* survives all three moves). No number makes an audience too wide and
  nothing in the language caps one. The two rules that must outlive any growth are already written —
  a check compiles its expression to a predicate and never materializes the set, and a listing is
  paginated — so this module gets slow before it gets wrong. The catalog mints
  nothing against it: no code governs expansion, and none could — whoever can write `EVERYONE` into
  an expression already holds `audience.manage` (§5a).
- **A grant's reach now moves with the calendar, and there is no write to mark the moment.** `OLDER(n)` and
  `YOUNGER(n)` are ordinary named operands composed by the same three operators as every other (§1), and
  they are the first whose membership changes **with no write at all**
  ([D-107](../decisions/round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)):
  a person turns eighteen, joins the set, and no row was touched — which is exactly why age *bands*, with
  the per-person expiry dates they would need, are not in this design. **There is no longer an invalidation
  model for this to be an exception to** — because there is no cache left for one to be about.
  ~~The cache is rebuilt nightly in full, immediately on any write to the ruleset, and on explicit request,
  with no per-entry TTL and no table of which write invalidates how wide a fan-out~~
  ([D-111](../decisions/round-13.md#d-111--the-permission-cache-is-rebuilt-nightly-on-any-ruleset-change-and-on-request))
  and ~~a birthday is not a ruleset write, so a cached answer about an age set may be up to one night stale,
  and the nightly rebuild is what fixes it~~ are both retired by
  [D-114](../decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation),
  which deletes the stored answer outright; what survives of D-111 is the version integer, its bump set cut
  to the two tables whose rows change what an expression *means* — `audience_operand` and `selector_type` —
  and what a bump drops is now a compilation, never an answer. **A birthday moves the set at the instant it
  happens.** What [D-107](../decisions/round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)
  waived was the calendar arriving between two rebuilds, and there are no rebuilds any more: its ruling
  stands, *"...how the rules resolve and IT IS FINE"*, with nothing left for it to be fine about, and
  **"up to one night stale" is deleted from this corpus** — under live resolution a birthday, a period reaching its own
  `valid_to` and a registration write each move the answer at the instant they happen, and so does a
  membership termination, which is the one this design used to get wrong. **One thing follows that is open, and one that is closed, and keeping them apart is the whole
  point.** **Open: nothing bounds what such a check costs** — the bound this system had was a depth bound
  and
  [D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)
  deleted it, so an age-bearing expression is one more set to expand and it is bounded by nothing; that is
  [F-21](../open-questions.md#f-21),
  whose shape this round did not change and whose width it did, and the catalog mints nothing against it:
  **no code, no column, no number, no threshold.** **Closed, and deliberately not a finding here: whom a
  derived set reached.** The preview a writer looked at is a workbench, never a record, and **the record is
  the expression**
  ([D-110](../decisions/round-13.md#d-110--the-expression-is-the-record-of-whom-a-grant-reached)):
  the audit row says *this person wrote these words, about this item, on this date*, and what the preview
  printed beside it is logged as **a rendering on a date**, never as a statement of who was in it. The
  alternative was keeping that list indefinitely — a per-person record, past
  [D-088](../decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)'s
  window, of people who were never granted anything. Ask whom a grant reached in May and the model does not
  read a stored list back, because there is none: it evaluates the words against the data of May, which is
  the property D-107 bought rather than a hole it left, and these documents do not promise the answer.
  Words-only is affordable rather than brave only because nothing a rule names is deleted any more, so the
  words keep resolving
  ([D-109](../decisions/round-13.md#d-109--nothing-a-rule-names-is-deleted-deprecated-hidden-disabled--and-a-tab-instead-of-a-report));
  what it costs is named here rather than found sideways — **an edit to a shared audience is a
  retrospective edit to every rule that names it**, and the control is the editor printing the resolved set
  before such an edit saves.
  **The premise this rests on is the organization's
  own** — *the people writing the rules WILL know what they are doing* — and it is written down in
  [D-107](../decisions/round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)
  with its two limits, because a claim about the authors buys nothing about the people a rule reaches and
  nothing about the write that is never recorded.
- **`audience.view` carries no sensitivity mark, and the thing it shows is a list of people.** A grant
  aimed at a name used to point at a set whose contents were mostly typed in; now the same row resolves
  through dated holder rows, group rosters and `MEMBERS`, and an expression containing `EVERYONE`
  resolves to the whole organization and beyond it. Whether reading a resolved expression needs a grade
  of its own — or whether `person.view` already covers it and the *display* is the leak to watch — is
  unsettled (§5a).
- **~~Whether `PERSON(x)` exists~~ — closed: it is a seeded `selector_type` row** (the thirteenth to arrive,
  one of the twelve that remained after round 11 — `LIST` left afterwards, D-105 — one of the fourteen
  D-107 seeded, for one round — and one of the **thirteen** seeded today, D-113 having removed the
  `GUARDIANS` row that should never have been in the registry).** This
  bullet recorded the round's sharpest disagreement, and
  [D-104](../decisions/round-10b.md#d-104--a-permission-codes-last-segment-is-an-action-and-a-registry-that-prose-contradicts-is-a-fiction)
  settles it the way [D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)
  and D-101's registry amendment already had: *"`PERSON(y)` is a selector, and this entry is the reason
  it had to become one."* So `(MEMBERS * ROLE(x)) + PERSON(y)` parses (§1, §11), and the waiver D-100
  wrote for itself is legal against the registry at last. **`LIST` was never a stand-in, and the reason
  was arithmetic**: `+ LIST` added everyone on that list and `- LIST` removed everyone on it, so an
  audience could not use it to except one person from itself. **That argument is what
  [D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)
  overturned — not by finding the arithmetic wrong but by deleting the operand it was about**, which is
  worth saying because the arithmetic was the reason both survived one round and the arithmetic was never
  the thing a reader needed. **What is left is a repair, not a question**
  — the two module pages that call `PERSON(…)` *"not in the language at all"*, one of them refusing the
  leaf while its own gate table writes it, and the domain grammar that omits it for the same reason,
  need this round's correction; the registry row and the printed grammar belong to
  [../data-model/05a-audience-and-grammar.md §8](../data-model/05a-audience-and-grammar.md#8-audience--grants-that-target-a-set-of-people)
  and [../domain/06-authorization-model.md §6.2](../domain/06a-audiences-and-selectors.md#62-audiences--an-expression-over-named-sets),
  not to this appendix. **The fallback survives the answer**: a second grant aimed at the person is the
  other way to write the exception, and the better one when the exception should not appear in the
  expression everybody else reads (§11).
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
  This bullet used to say *"named groups"* as a kind, opposed to *"built-in audiences"*;
  [D-091](../decisions/round-09.md#d-091--a-permission-group-is-a-rule-and-a-list-at-once-and-a-rule-may-name-another-group)
  deleted the kinds and D-101 deleted the filling rules, so what is left is genuinely two questions:
  which `selector_type` operands ship — **the count is thirteen today (§1): thirteen for exactly one
  round until [D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)
  deleted `LIST`, twelve from there until
  [D-107](../decisions/round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)
  seeded `OLDER(n)` and `YOUNGER(n)` — fourteen, for one round — until
  [D-113](../decisions/round-13.md#d-113--the-guardianship-channel-has-no-expression-guardians-is-not-a-selector)
  removed the `GUARDIANS` row that should never have been seeded. Closing that row closed the last bullet
  F-5 was still carrying, and by refusal rather than by arrival: the question was *which operand names a
  person's guardians*, and the answer is that none does, because the channel carries a level over a child
  and not a set. Its age bullet had closed in round 12, when `OLDER(n)` and `YOUNGER(n)` arrived as
  registry rows exactly as that entry said they would have to and not as a rule engine; `WHITELISTED`, the
  one name still without stored state, is F-20's question now and not a gap in this registry**
  (§1) — and who may create a group, which is `person_group.create` (§5a).
- **Which office may put a person on a group's roster is unanswered, and on the shipped seed nobody
  may.** ~~Which role holds the right to place a person in a unit~~ — the code and the unit are both
  gone, and what replaced them is `person_group.member.manage`: one code, `applies_to = unit_and_item`,
  never self-scoped, and the only thing between a person and a roster (§5a, §11 property 6). The
  catalog's side is settled; what is missing is a decision the organization records as `role` rows and
  grant rows, not a code.
- **`message.broadcast` lost a scope it was specified against, and messaging has not ruled on the
  consequence.** [D-077](../decisions/round-06.md#d-077--messaging-is-direct-by-default-broadcast-is-an-ordinary-scoped-permission-and-the-recipient-chooses-the-channel)
  wrote *"one code at two scopes"* — the organization, or one unit — and D-097 collapsed the pair into
  the single unit scope. So a broadcaster reaches everyone, and the narrower reading now has to be a
  grant aimed at a `person_group`, which is a different shape of decision (who may create the group, and
  whether it is the *broadcast* grant or the group roster that carries the ⚠). §10 records it as
  messaging's call; **the catalog has not silently re-specified it either way**, including whether the
  code should become `applies_to = unit_and_item`.
- **`membership.manage` does not exist, and five places in this round's documents refuse it.** D-099
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
- **The registered spelling of the answer-read code is the catalog's, singular, and the round said so
  out loud.** [../data-model/08a-event-guards-and-checks.md §8](../data-model/08a-event-guards-and-checks.md#selectors-that-bind-to-an-event)
  records that D-102 wrote the plural while its own entry was new, that the two spellings were one code
  and not two, and that **the catalog is the arbiter** — so the seeded grant in §11 and the code in §8a
  are `event.answer.view`, and no other spelling is registered anywhere. That case was easy, because
  the catalog was self-consistent and naming it arbiter settled something. **The hard case ended
  differently, and how it ended is the finding:**
  [D-104](../decisions/round-10b.md#d-104--a-permission-codes-last-segment-is-an-action-and-a-registry-that-prose-contradicts-is-a-fiction)
  greps the closed round for the door-code capability the round spent a dispute on and finds it
  **nowhere** — not in this catalog, not in the events module, not in the ERD, not in the decision log.
  **There is no QR capability, seeded or deferred, anywhere in this system.** A thing was possible in
  prose, was half-designed in the course of arguing about its name, and left as prose: the registry —
  the one place a permission legally exists, since
  [D-072](../decisions/round-06.md#d-072--the-documentation-carries-no-sql-the-schema-is-the-orms-job)
  made these documents the specification rather than a description of a schema — never had a row, so
  nothing refused anything, and no reviewer asked the one question that ends the argument, *which seeded
  row carries this?* What survives of the dispute is §1's three rules, the report D-104 adopts, and a
  presence story that is `event.presence.mark` and nothing more (§8a,
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
- **Which role holds the right to place a person in a unit is unanswered in the seed set**, and it is
  now the only question standing between a child and a unit's roster (§11 property 6). The catalog's
  side of it is settled — one code, unit-scoped, never self-scoped — so what is missing is not a code
  but a decision the organization has to record in `role` rows.

**Resolved and no longer open**, kept visible so the reasoning survives: whether
`person.admin` should subsume `person.merge` and `person.redact` (moot — there are no
per-resource `admin` permissions at all, and the question moved into reviewable office contents,
D-068); whether `event.manage_participants` should split off presence (it did, into
`event.presence.mark` — EV-5 asked whether the new code sat a level lower, and
[round 10 deleted the ladder](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality),
so what survives is the split and the two codes' different `right_kind` (§8a)); the `event` resource's
real permission set (§8a, thirteen codes); ~~whether any permission should require current membership
status (yes, via the role — D-039)~~ — **reversed: no permission requires it**, and the expression on
each grant says who does (D-100, §11); `person.background_check.*` (removed — D-043);
~~`membership.transfer` (obsolete once participation replaced unit membership — D-041)~~ — the
replacement was itself deleted with the hierarchy, so the code is gone outright and moving a person
between groups is `person_group.member.manage` (§5a); whether `org_unit.restructure` includes
reparenting (~~it cannot — D-036~~ — moot twice over: reparenting needed a hierarchy, and
[D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)
deleted it, so the code is off this catalog and the act is the organization renaming a scope it no
longer stores (§5)); whether reversing a merge deserves a code of its own (it does not —
undoing an identity correction is the same act as making one, so `person.unmerge` is gone from §2 and
unmerge is `person.merge`, D-087); and whether a colliding sign-up needs a claim object and a way to
link it (it needs neither — the hypothesis queue already exists and deciding it is `person.merge`,
D-089). From round 9: whether a person may hold ~~`unit_participation.manage`~~ or ~~`position.assign`~~
over themselves — ~~no, because there is no self-scoped form of either~~ **the same answer, on the two
codes that replaced them**: neither `person_group.member.manage` nor `role.assign` has a self-scoped
form and none will be added, D-095's reasoning transferring intact (§4, §7); whether anything below the
root needed a gate of its own (it did not — and there is no root-or-below any more, and no gate; the
unit type carried no restriction, and D-100 deleted the resolver's membership clause, D-095, D-097);
whether an appointment should also write a role assignment (~~it should not — the derivation belongs on
a group's filling rule, D-091~~ — positions are deleted, filling rules are deleted, and
[F-12](../open-questions.md#f-12) is **closed with the
answer no**: a holder row names one person, which is the only way an office can answer *who held this
in 2023*, D-100); and whether group membership needs a rule against nesting now that groups nest
(~~it does not — a cycle is refused when the edge is saved~~ — the edge table is deleted and nesting
moved into the expression tree, where a tree could not cycle on its own; when
[D-103](../decisions/round-10b.md#d-103--an-audience-may-name-another-audience) reopened *an audience
naming another audience*, cycles became possible **between** audiences and the guard came back as a
reachability walk over the reference closure, refused when the row is saved — a depth bound came with
it and [D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)
deleted that bound while the walks, inside the tree and across audiences, stayed as the only
structural guard there is —
**still a write path with no permission of its own**,
which is the part this catalog cares about, D-101, D-103, D-105). From round 10, additionally: whether a grant
should carry a strength, a locality, or more than one code (no, no, and no — D-099); whether the unit is
a row or a scope (a scope — D-097); whether
anything may be exposed across a unit boundary (there is no boundary to cross — D-031, D-049 and
D-045's `scope.exposure` review are all deleted together); whether leadership is a position (it is an
office, and the elected/appointed distinction survives only as a name the organization invents, D-100);
whether an event has an owner (no — D-102, and `can_event()` with it); whether presence is a set anyone
may be granted over (it is not — `PRESENT` is not seeded, **on the argument it has always stood on and
with the answer unchanged**: a forgotten tick box revoking a leader's access to their own camp. The
refusal is written down in three documents so that nobody re-adds it as a convenience, and nothing in the
language would have caught it structurally in any case — a selector may read a column against a date,
because `OLDER(n)` does, and may be a hard-coded computation in the resolver, because `MEMBERS` is
(D-107, §1)); whether a code's last segment had to be an
action, or merely usually was (**it is a rule now — D-104 promotes §1's two shapes from description to
requirement, names `system.admin` as the single noun allowed, and finds sixty-five of the sixty-six
live codes already obeying it**); and whether `PERSON(x)` is in the selector language at all (it is —
it arrived as the thirteenth seeded `selector_type` row, D-101's amendment, D-104, with `LIST`
deleted it was one of the twelve that remained, D-105, one of the fourteen D-107 seeded, for exactly one
round, and one of the **thirteen** seeded today — D-113 removed a row that should never have been counted,
which is the fourth time this page has had to re-type this number). From round
12, whether `OLDER(n)` may be an operand (**it may: an operand must be a named row of the registry, and
this is a row** — `AGE >= 18` is not expressible because the language has no comparison operator to build
it out of, and D-060's refusal of a rule engine survives the sentence that used to argue for it, D-107),
and whether an unresolvable leaf should stop a save (**no** — it stays the empty set, and it is listed in
the `Broken` section of the tab on the permissions page rather than on a report nobody runs, D-106 as
corrected by D-109, §12 — and round 13 narrowed what can produce one to a single cause, a redacted person). **What closed those two is worth
keeping beside them:** the report D-104 adopts diffs every dotted token in prose against every seeded
registry in both directions, would have caught all four of the round's instances, and **can only ever
be run by hand here, because this repository has no build step** — a convention, not a guard, and the
one that decides whether this catalog's tables and the corpus's prose are still one thing next round.

All tracked in [../open-questions.md](../open-questions.md).
