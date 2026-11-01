# Appendix — Permission Catalog: absent namespaces, worked-example offices, open issues

What the catalog deliberately does not have, what arrives with the unbuilt modules, what an installation actually has on its first day, how an office is written when somebody writes one, and what is not settled.

**Section numbers are shared across the three parts** and never renumbered, because other pages cite them by number and their anchors are built from them: [permission-catalog.md](permission-catalog.md) holds §1, the conventions; [permission-catalog-a-codes.md](permission-catalog-a-codes.md) holds §2–§8b, the codes; [permission-catalog-b-roles-and-open-issues.md](permission-catalog-b-roles-and-open-issues.md) holds §9–§12, the namespaces that are not here, the deferred ones, the worked examples of writing an office, and what is open.

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
  the grant side, carried by one of the twelve grants the act that creates the event writes beside it and
  aimed at `ORGANIZERS` (§8a), and leadership is not guardianship
  ([D-061](../decisions/round-05.md#d-061--event-answers-are-read-by-that-events-organizers)).

See [../data-model/04-relationships.md §2](../data-model/04-relationships.md#2-the-guardians-right-none-view-or-write)
for the value, its defaults by `source`, and the three-value ordering it is a range of — `none` < `view`
< `write`, which is D-074's own ordering over one column and **not** the access-level ladder
[D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)
deleted. Nothing in this catalog is a range of anything.

## 10. Deferred namespaces

Placeholders for features you have not specified. Listed so the naming convention is
established before anyone invents an inconsistent one.

**Money left this page, and the sentence above is the reason it had to.** [D-195](../decisions/round-24.md#d-195--the-money-codes-are-shipped-codes-catalog-a-grows-a-money-section-and-catalog-b-10-loses-three-rows)
moved six codes into [catalog A §4a](permission-catalog-a-codes.md#4a-money) — `fee.view`, `fee.create`,
`payment.view`, `payment.record`, `payment.reverse`, `payment.match` — because this table is the register for
*a namespace whose module does not exist*, and the finance module's money already moved: its worked-example
treasurer below was written out of codes this page called placeholders, which made §10 dishonest rather than
merely optimistic. The `invoice` row left with them and for a different reason —
[D-197](../decisions/round-24.md#d-197--an-invoice-is-compulsory-so-nobody-issues-one-invoiceissue-is-deleted-and-the-asks-write-writes-it)
deleted `invoice.issue` outright one answer after it was registered, because invoices are compulsory and a
permission nobody can decline is not a permission. **The `invoice` table itself is untouched: it is the code
that died, not the table.** What remains below is genuinely unbuilt.

**What those three rows used to say, because a deletion ought to be readable from the page it happened on.**
The `fee` row carried two codes and no sensitivity mark, and one long reason for the missing mark: `fee.waive`
had gone because there are no hardship waivers
([D-157](../decisions/round-22.md#d-157--there-are-no-hardship-waivers)) and `fee.refund` because a refund is a
transfer the bank makes and a `payment` row records, not an act authorized on a screen
([D-158](../decisions/round-22.md#d-158--a-refund-happens-at-the-bank))
— **that argument was not deleted with the row, it moved to [catalog A §4a](permission-catalog-a-codes.md#4a-money),
which is where the marks now live.** The `payment` row listed four codes and then admitted, in its own cell, that
whether it was still honest as a *deferred* namespace was an open question, since the finance module is designed
and those codes appear in this page's own worked examples below — **the question is answered now, and the answer is
that it was not honest, so the row and its admission go together.** The `invoice` row held one code and one
deliberate separation: that the person who may type in a number is not automatically the person who may produce a
document with a legal shape. **[D-197](../decisions/round-24.md#d-197--an-invoice-is-compulsory-so-nobody-issues-one-invoiceissue-is-deleted-and-the-asks-write-writes-it)
gave that separation up**, and the giving-up is written as a cost in catalog A §4a and as a death in
[the dead-name register](removed-concepts.md) rather than kept here as a distinction nothing enforces any more.

**Two rows left this page in round 25, for the reason the money rows left it in round 24.** The `report` row went
first, and it did not go to [catalog A](permission-catalog-a-codes.md): [D-210](../decisions/round-25.md#d-210--a-report-is-a-delivered-message-so-all-five-report-codes-are-deleted-and-reporting-stops-being-a-name)
ruled that what an organization calls a report is a message of a type delivered to an audience and that **there is
no report screen in this design**, so the namespace has no shape left to defer — a code that would gate a screen is
not worth deferring once there is no such screen. **The posture [D-195](../decisions/round-24.md#d-195--the-money-codes-are-shipped-codes-catalog-a-grows-a-money-section-and-catalog-b-10-loses-three-rows)
chose for money is untouched and is repeated in [catalog A §4a](permission-catalog-a-codes.md#4a-money): money is
readable through `fee.view` and `payment.view`, no money report code exists here or there, and none is deferred.**
The `message` row went because its module arrived: [../data-model/10-messaging.md](../data-model/10-messaging.md)
draws the three tables, and its one code, `message.send`, is a shipped row in
[catalog A §8c](permission-catalog-a-codes.md#8c-messaging) — and this table is the register for *a namespace whose
module does not exist*, which is exactly the sentence that moved the money rows. What that row used to describe in
the conditional is now settled rather than deferred, and settled differently than it read: **one code gates every
write, a message to one person included**, so *"direct by default"* names a send's shape and not a right
([D-208](../decisions/round-25.md#d-208--messagesend-is-the-only-messaging-code-and-the-audience-a-send-names-is-not-checked)
narrowing [D-077](../decisions/round-06.md#d-077--messaging-is-direct-by-default-broadcast-is-an-ordinary-scoped-permission-and-the-recipient-chooses-the-channel));
an audience narrows a *send* rather than the scope of a grant, so [D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)
is untouched; **the recipient's choice of door is a column on the account** and not a permission
([D-213](../decisions/round-25.md#d-213--the-account-chooses-its-own-doors-a-childs-message-mirrors-as-its-own-rows-and-only-e-mail-lands-today));
and a minor's mirroring is **recipient rows on the guardian's own doors**, which is the physical form
[D-082](../decisions/round-07-08.md#d-082--a-direct-message-to-a-minor-is-mirrored-to-the-minors-guardians)
had always meant ([10-messaging §6](../data-model/10-messaging.md#6-a-childs-message-mirrors-as-rows)).
**Two of this page's §12 items close with those two rows**, and both are written their verdicts in place rather
than removed.

| Resource | Permission | Notes |
|----------|-----------|-------|
| `document` | `document.view`, `document.create`, `document.edit`, `document.delete`, `document.grant_access` | `document` is already a row of `grant_scope_type`, marked deferred — the item exists in the registry before the module does, which is what the polymorphic `scope_id` is for (D-011). The code is the one this catalog's own §1 rule pays for: `document.grant_access` sits beside `access_grant.create` exactly as `event.grant_access` does, and §12 asks the question once for both. |
| `consent` | `consent.template.edit`, `consent.record.view` | |
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

## 11. Roles — worked examples of writing one

**Examples of an act, not a list of rows.** The heading says "roles" and most of what follows is grants,
because an office has no contents: **the codes an office carries are the live grants whose expression
names it**, one row per code, each with its own scope and its own period
([D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)).
`MEMBERS * ROLE(treasurer)` on `fee.create` is one such row, and it — not the office — is what lets a
treasurer issue a fee. A role is two things: **a name a grant can be aimed at**, and **the register that
answers *who held this in 2023*** (`role_holder`, which is why
[F-12](../open-questions.md#f-12) closes with *no* — a holder row names one person). Offices are runtime
data: the organization creates them, names them, writes and closes their holders, and deletes the
never-held ones ([§7](../data-model/05-authorization.md#3-role--an-office)). **Reach is not runtime
data** — it is administered through `access_grant.create` and `access_grant.revoke`, so it is reviewed in
`access_grant`, not in a role editor (§7).

### What an installation has

**Counting only the tables this section is about: no office and no grant.** Nothing about an organization's
authority arrives built. **Day one is one account and one ordinary `access_grant` row giving it
`system.admin` at the unit** — one row, one audit row beside it, and nothing in the model that can tell it
apart from a grant written a year later
([D-150](../decisions/round-21.md#d-150--day-one-is-one-account-holding-systemadmin-and-nothing-else-is-shipped)).
Everything else that ships is vocabulary: the permission rows of this catalog, the `selector_type` operands
(§1), the `grant_scope_type` rows that make an event or a group or a role an item, the two effects and the
two enums ([§12](../data-model/05d-invariants-and-seed.md#12-what-day-one-looks-like)). **None of that is
authority**, and the sentence is repeated here because this section is where a reader looks for it.

| What an installation has | Table | Written by | What it grants |
|--------------------------|-------|------------|----------------|
| one grant of `system.admin` at the unit, naming one account | `access_grant` | the installation, as an ordinary grant row with an ordinary audit row beside it | **Everything** — the one wildcard, `applies_to = unit`, so never reachable on an item (§1, §7). This is the entire configuration of a new installation |
| twelve item-scope allows beside every event, aimed at an audience whose expression is the bare operand `ORGANIZERS` | `access_grant` | the act that creates the event, in the same transaction as the event row ([D-151](../decisions/round-21.md#d-151--creating-an-event-writes-the-events-authority-and-its-organizers-may-grant-on-it)) | That event's organizers run that event. The twelve are §8a's `event.*` codes except `event.create`, whose `applies_to` is `unit` — so **`event.answer.view` is one of twelve grants written beside every event**, not a lone answer-read grant, and one of the other eleven is `event.grant_access` (§8a) |

**Why a role and not a group**, when D-098's own definition of a group is *"a temporary set of members
that do events together"* and counselors are neither temporary nor event-shaped: the table decides
**which code protects the set**, and every safeguarding convention in this area hangs from that answer
being unchangeable by an ordinary grant — `role.*` is 🔒🔒, `person_group.member.manage` is ⚠
(§5a). **That argument is about which of two tables a permanent population lives in, and it stands
untouched**; what it never needed was for the platform to write the row. `counselors` is the name the corpus
uses when it needs an office, and it is now openly one
([D-154](../decisions/round-21.md#d-154--counselors-is-an-example-now-not-a-shipped-office)).
**What refuses a deletion of any office that has been held is the foreign key from `role_holder`**, a
migration-level constraint, and it protects every office the organization ever writes at least as well as it
would have protected a shipped one (§7,
[D-152](../decisions/round-21.md#d-152--zero-is_system-columns-what-protects-a-vocabulary-is-its-table-not-a-flag-on-its-rows)).

**Nothing names `ROLE(counselors)` until somebody writes the grant, and that is the design rather than an
omission.**
Being a counselor confers nothing until someone writes the grant
([D-005](../decisions/round-01a.md#d-005--permissions-are-grants-never-derived-from-identity)).
**What that leaves open is not a permission but a
number**, and it is the price D-100 names for moving the gate into the expression: the reach of the
counselor office is only as correct as the roster, so the import reconciliation of
[D-090](../decisions/round-07-08.md#d-090--the-legacy-corpus-is-thousands-of-roster-rows-with-numbers-and-no-money)
counts people marked as counselors in the legacy corpus against `role_holder` rows written. An import
that misses three hundred counselors **fails closed** — nobody's access breaks — which is exactly why
nobody notices. **And on a first run there is no such office**, so that reconciliation has nothing to
reconcile and reports nothing — a report whose subject arrives later, not a report that is broken.

**Who may make someone a counselor, over just that one office.** `role.assign` writes a `role_holder`
row and is `applies_to = unit_and_item` (§7), so holding it **at the unit** lets you fill every office
in the organization, which is what 🔒🔒 is for, while a grant of it **on the item `counselors`** says
*these two may manage the counselor roster* and nothing else. That is D-098's move read symmetrically,
and it is why `role` is a row of `grant_scope_type`.

**The twelve grants beside an event are written without `MEMBERS`, and must not be "corrected."** An
organizer appointed for one weekend is not required to hold a current membership — D-062's appointment model
assumes exactly that — so a `MEMBERS` on those rows would take an organizer's read of their own event's
answers away the night their fee lapsed. **They are also the only grants this system writes by itself**, and
that is worth stating beside one of D-100's three controls, which counted on a shortcut that does not exist
here: it was that *any grant template carries `MEMBERS`, so the path of least repetition is the safe path*,
and **there is no repetition to take** — every grant an office holds will have been written by hand, and the
one automated write path in the system produces twelve rows that must not carry it ([05 §6](../data-model/05-authorization.md#6-access_grant--the-per-item-layer)). *Nor can
those twelve be one row covering every event — a bound operand cannot sit on a unit-scope grant — which is
why the act that creates an event writes them beside it (§8a).*

### The worked-example offices

**None of the following ships, and nothing below is a row the platform writes.** These are the names the
rest of the corpus uses whenever it needs an office to talk about, written out the way an office has to be
written by the person writing it: one `role.create` for the name — which confers nothing on its own — and
then **one grant per code**, all aimed at one expression, all at the unit, because there is nowhere else for
a code about people to be aimed (§1), each with its own period, and then a `role.assign` for whoever holds
it. Do not read a row as a
requirement, and do not expect the list to survive contact with the organization.

| Office | The grant rows that are its reach | Grantee expression | Why that expression |
|--------|------------------------------------------|--------------------|---------------------|
| `system_admin` | `system.admin` — **one row, and it is enough** | `ROLE(system_admin)` | **no `MEMBERS`**, deliberately: the 1 January case below |
| `registrar` | `person.view` ⚠⚠, `person.create`, `person.edit` ⚠, `person.contact.view` ⚠, `person.contact.edit` ⚠, `account.view` ⚠, `account.create`, `account.suspend` ⚠, `account.close` ⚠, `account.credential.reset` 🔒, `membership.view` ⚠, `membership.request.create`, `membership.request.review` ⚠, `membership.activate`, `membership.backdate` ⚠ — **fifteen rows** | `MEMBERS * ROLE(registrar)` | staff working the organization's own records; the office stops when the fee lapses |
| `membership_approver` | `membership.request.review` ⚠, `membership.request.approve` ⛔, `membership.view` ⚠ — **three rows** | `MEMBERS * ROLE(membership_approver)` | as above, plus the read the approve offers: an approver who cannot open the membership says yes to something they have not seen. **The row is there because the author wrote it and no rule put it there** ([D-194](../decisions/round-24.md#d-194--nothing-is-implied-by-a-permission-the-editor-offers-the-companion-read-and-the-database-stores-two-rows)) |
| `treasurer` | `fee.view`, `fee.create`, `payment.view`, `payment.record`, `payment.reverse`, `payment.match` — **six rows, all six registered** | `MEMBERS * ROLE(treasurer)` | as above, and one list shorter than it was: the treasurer waives nothing and refunds nothing here (D-157, D-158). The six money rows are [catalog A §4a](permission-catalog-a-codes.md#4a-money)'s since [round 24](../decisions/round-24.md), which is what makes this office writable today — and it is writable in full now, because the seventh row this office used to name is gone with the whole reporting namespace ([D-210](../decisions/round-25.md#d-210--a-report-is-a-delivered-message-so-all-five-report-codes-are-deleted-and-reporting-stops-being-a-name)) |
| `safeguarding_officer` | `membership.view` ⚠, `membership.terminate` ⛔ — **two rows** | `MEMBERS * ROLE(safeguarding_officer)` | whoever finds the problem and whoever ends a membership over it are the same person, and nobody else |
| `leaders` | the thirteen `event.*` codes (§8a), `membership.view` ⚠, `person_group.view` ⚠ — **fifteen rows** | `ROLE(leaders)` | **volunteers, so no `MEMBERS`** (property 4): the office must survive a lapsed fee, and it reaches every event, not one body's events |
| `audience_admin` | `audience.view`, `audience.manage` ⚠ | `MEMBERS * ROLE(audience_admin)` | §5a, including the naming rule this office is subject to |
| `identity_reviewer` | `person.merge` 🔒, `person.view` ⚠⚠ — **two rows** | `MEMBERS * ROLE(identity_reviewer)` | **the read is here because the author wrote it, and not because `person.merge` carried it** — nothing is implied by a permission ([D-194](../decisions/round-24.md#d-194--nothing-is-implied-by-a-permission-the-editor-offers-the-companion-read-and-the-database-stores-two-rows)) — and **no `person.edit`**, because settling an identity is not editing one. Property 5 |
| `auditor` | `audit.view` ⚠⚠, `audit.export` ⚠⚠ — **read-only, no writes, and two rows** | `ROLE(auditor)` | **no `MEMBERS`**: an auditor who forgets to pay must not lose the read (property 4). What this office used to hold besides the trail was a report code, and there is none left to hold — the trail is the read, and it is ⚠⚠ for what it quotes ([D-138](../decisions/round-20.md#d-138--one-permission-guards-the-whole-audit-trail-and-the-widening-is-on-the-record)) |

**An office's reach carries two kinds of period, and both are worth knowing before you set either.**
The office is held for a period (`role_holder.valid_from`/`valid_to`) **and** each of its grants has a
period of its own, so an office's reach is an intersection of up to twenty dates, and the question *when
does this person stop being able to do that?* has more than one right answer. **Nothing forces either
kind of row to end** — the posture of
[D-071](../decisions/round-05.md#d-071--nothing-forces-a-role-assignment-to-end-the-gate-and-the-report-are-the-control)
applies to both, and the control is the report.

**Every code every office above names is registered, and that is new.** Two rounds took the exceptions
away. [D-195](../decisions/round-24.md#d-195--the-money-codes-are-shipped-codes-catalog-a-grows-a-money-section-and-catalog-b-10-loses-three-rows)
registered six codes for money in [catalog A §4a](permission-catalog-a-codes.md#4a-money), so the sentence this
page used to carry — that the treasurer's office *"cannot be written today"* and its count is *"a wish rather
than a migration"* — was true of it only while its codes were placeholders, and it is false now; the same
ruling is why `payment.match` appears in that row, because the office that runs the accounting is the office
the finance module names as holding it, and a hand-move of an allocation is the only correction the automatic
match leaves for a person ([D-196](../decisions/round-24.md#d-196--the-variable-symbol-is-the-whole-match-what-arrives-under-its-own-symbol-is-attached-in-full-and-the-difference-is-shown)).
[round 25](../decisions/round-25.md) took the last three with it: `treasurer`, `safeguarding_officer` and
`leaders` each held exactly one reporting code, unregistered and parked in [§10](#10-deferred-namespaces)
because **reporting's shape was undecided rather than because their modules were unbuilt**, and
[D-210](../decisions/round-25.md#d-210--a-report-is-a-delivered-message-so-all-five-report-codes-are-deleted-and-reporting-stops-being-a-name)
deleted the namespace outright — what an organization calls a report is a message of a type delivered to an
audience now ([../data-model/10-messaging.md §8](../data-model/10-messaging.md#8-reports-arrive-here-and-stop-being-a-name)),
so an office's reach stops at the codes that act on rows and the listings an organization wants are configured
as types, not granted as screens. **Four of the nine rows above got shorter by one, and none got unwritable.**
**The paragraph stays because the hazard it was written about does not:** nothing in the schema stops a grant
row naming a code that has no row, so a future office could walk into the same gap and
[F-19](../open-questions.md#f-19) is still the answer — today this page simply has no example of it.

**Read `event.*` above as a count, not as a wildcard.** Since
[D-068](../decisions/round-05.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle)
there is no resolver rule that makes `person.*` mean anything; the notation means *"every `person.`
code listed in §2"*, and a real office has an explicit **grant row** for each — which since D-100 is
the only place such a list exists at all. Three consequences for whoever writes these:

1. **`registrar` omits `person.merge` and `person.redact` by not having those rows, and the exclusion is
   exactly that literal**: two rows nobody inserted, visible in `access_grant` with a date and an author,
   reviewable like any other row. `identity_reviewer` is the office that *does* hold `person.merge` — the
   whole of identity correction: merging, reversing a merge, and deciding a sign-up collision (§2) — listed
   beside `registrar` so the difference between the two is legible. **A companion read is not a licence to
   bundle**: the reviewer gained `person.view` ([D-194](../decisions/round-24.md#d-194--nothing-is-implied-by-a-permission-the-editor-offers-the-companion-read-and-the-database-stores-two-rows),
   property 5) and holds no `person.edit`, so the rule in the sentence after this one is untouched.
   **An office that bundles a resource
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

**There is no default, in either direction, and that is the ruling.** Which offices are written without
the term is decided per office, by whoever writes the grant ([D-165](../decisions/round-22.md#d-165--there-is-no-default-for-members-and-that-is-the-decision));
the `Unusual` section below lists *every* `ROLE(…)` operand with no `MEMBERS`, not a marked subset, and
a grant written without the term needs no reason field: `grant_reason` is already an optional column on the
row ([05 §6](../data-model/05-authorization.md#6-access_grant--the-per-item-layer)), and it stays optional.
§12 carries the ruling and its edges.

**The posture is opt-in, so name the new failure rather than bury it.** An expression written
`ROLE(treasurer)` with no `MEMBERS` authorizes a lapsed member, silently, for as long as the grant
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
- **Any grant template carries `MEMBERS`**, so the path of least repetition is the safe path. *This control
  has nothing to work on and must not be trusted with anything: no grant arrives carrying `MEMBERS`, because
  the only grants this system writes by itself are the twelve beside an event, and those must not carry it
  (§11, §8a). Every office grant in existence has been written by hand, so the safe path is not the short
  one. Recorded in §12.*
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
the lockout, silently, with no error message. **Whether any office exists to be written this way on day one
is a different question, and the answer is no: day one is one account and one grant naming that account, not
an office**, so there is nothing to gate, nothing to forget `MEMBERS` on, and the January risk arrives with
the first office somebody writes ([What an installation has](#what-an-installation-has), §12).

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
   What it also does not have here is `person.view`: **two rows**, and neither reads a person record. Until
   round 25 this office held a second read as well, a report code marked ⚠⚠, and [D-210](../decisions/round-25.md#d-210--a-report-is-a-delivered-message-so-all-five-report-codes-are-deleted-and-reporting-stops-being-a-name)
   took it away with the rest of that namespace, so **the widest thing this office reads is now a membership**.
   **If working a case needs the record, that is a third grant row** — scoped, dated,
   attributable, and visible to anyone who asks what this office can read, which is the review §2 moved
   to when it graded `person.view` ⚠⚠. What reached the officer before was a listing somebody opened, and
   what reaches them now is a message of a type with an audience
   ([../data-model/10-messaging.md §8](../data-model/10-messaging.md#8-reports-arrive-here-and-stop-being-a-name)):
   **this corpus configures no type for a safeguarding case**, which is a fact about the configuration and not
   a promise that one is coming.
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
   The instinct behind them is one sentence — **staff-like offices working on the organization's own
   records hold a membership; volunteer-facing offices need not** — and it is a writing habit, the
   judgment of whoever writes each grant, not a default the design carries in either direction and not
   a resolver clause ([D-165](../decisions/round-22.md#d-165--there-is-no-default-for-members-and-that-is-the-decision)).
   The failure it prevents is specific: the volunteer whose own fee is unpaid still runs the Thursday
   meeting, and must not lose their roster the night it lapses. That volunteer's office appears in the
   `Unusual` section of the tab on the permissions page — grants naming a `ROLE(…)` operand with no
   `MEMBERS` — **which is how the organization notices, and the resolver is still not how it punishes**. See
   [../domain/06-authorization-model.md §4](../domain/06-authorization-model.md#4-roles-are-offices-groups-are-company).
5. **`identity_reviewer` holds `person.view`, and the author wrote that row rather than inheriting it.**
   **This property argued the opposite for four rounds and [F-11](../open-questions.md#f-11--does-the-identity-reviewer-need-to-read-the-person-record-to-settle-a-claim)
   closed it the other way: the office carries two rows now, `person.merge` 🔒 and `person.view` ⚠⚠**
   ([D-194](../decisions/round-24.md#d-194--nothing-is-implied-by-a-permission-the-editor-offers-the-companion-read-and-the-database-stores-two-rows)).
   The reason is practical and it is the half of F-11 that a model cannot answer: **an installation copies
   this table**, and a reviewer who cannot open either of the two records in front of them spends the first
   week asking somebody else to look — the work the office exists to do simply does not get done.
   **Nothing put `person.view` there.** `person.merge` implies nothing, the resolver reads no dependency, and
   the editor that *offers* the companion read writes a second row when the offer is taken and nothing when it
   is declined: this row is what taking it looks like — written by a person, dated, with its own grantee and
   its own audit row. And the read is not `person.edit`, because **settling an identity is not editing one**,
   which is also why §2's rule against mixing `person.merge` with routine `person.edit` is untouched.
   **What the old argument said, kept because the trade it named is still live.** The descriptive values
   underneath a candidate pair are not evidence about whether two rows are one human; the reviewer works from
   the pair, the `match_signals` recorded against it, and the names and dates those signals compare — and this
   is also the office a **blocked sign-up** lands on
   ([D-089](../decisions/round-07-08.md#d-089--one-live-account-a-colliding-sign-up-files-a-claim-and-creates-nothing)),
   where the stalled item is a person who cannot log in and the queue's listing is read by whoever works it.
   **Nobody is fetched for that queue, and the reason is configuration rather than a rule about verbs:** no
   message type is configured for a blocked sign-up, so there is nothing that would fetch anybody
   ([D-164](../decisions/round-22.md#d-164--nobody-is-told-and-no-page-may-say-otherwise) as narrowed by
   [D-214](../decisions/round-25.md#d-214--the-system-sends-and-d-164-is-narrowed-to-the-one-thing-it-was-protecting)).
   `person.view` at the unit is the catalog's largest ⚠⚠ read sitting in the office with the most write
   authority over identity — **the road this property called the wrong one is now the office as written**, and
   what controls it is the one §2 nominated when it graded the code ⚠⚠: the question *which grants were given
   this one?*, which a catalog can answer. A narrower form is still available to whoever writes the real
   grant — a scoped, dated row, or a review screen that shows more of the *signals* — but the example shows
   the wide form, because an example is the thing that gets copied.
   **The failure this does not fix, on the page rather than in a footnote.** The offer reaches only the
   grant screen: it does not reach an `api_key` writing a grant, a migration, or the twelve rows an event
   create writes, so a reviewer office built by one of those **can hold `person.merge` and no read — nothing
   refuses it, nothing lists it, and no report will ever show it**
   ([D-194](../decisions/round-24.md#d-194--nothing-is-implied-by-a-permission-the-editor-offers-the-companion-read-and-the-database-stores-two-rows)).
   That is the price of "editor convenience" over a save-time refusal. `auditor` was left exactly as it was
   for the mirror-image reason: it holds **no write at all**, so there was never a companion for an editor to
   have offered, and reading the trail without `person.view` stays the plausible office property 3 describes.
6. **No office in this set holds `person_group.member.manage`, and the omission is now ruled rather than
   open — the blank is the answer, named as one by
   [D-167](../decisions/round-22.md#d-167--the-office-that-may-place-a-child-in-a-group-stays-unnamed) so
   no later round repairs it.** What
   D-095 decided has not moved: joining a set is somebody else's act, the write is never self-scoped, and
   this code is the only thing standing between a person and a group's roster (§5a). As written,
   `leaders` may *see* a roster and cannot write one — and because the answer behind D-095 was
   *"they will be assigned to the unit by the counselors"* while `counselors` is an office somebody writes
   rather than one that arrives ([What an installation has](#what-an-installation-has)), **until an
   organization writes that office and gives it this code, the only person who may write a roster is the one
   account holding `system.admin` at the unit** — one ordinary `access_grant` row, satisfying this code the
   way it satisfies every code (§7). **It is recorded here instead of added to
   the table on purpose**: which volunteer office may put a child on a group's roster is the
   organization's decision, and an appendix that quietly hands it to `leaders` would be making a
   safeguarding choice on someone else's behalf (§12).
7. **`attribute.define` is held by nothing here, and an office is the wrong shape for the answer.**
   [open-questions AT-2](../open-questions.md#at-2) points at this section as the place the question gets
   answered, and the honest answer for a volunteer
   organization is one or two people rather than an office: **a grant aimed at `PERSON(x)`** (§1) is the
   form that fits, with a date on it, and an office would only be a way of making one person's job
   look like a policy — a role confers nothing a grant does not already confer
   ([D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)).
   **What changed under this property is the shape of the risk, and it got sharper rather than softer.**
   There is no proposal stage left, so nothing arrives in a queue to be noticed later
   ([D-141](../decisions/round-20.md#d-141--a-definition-is-live-at-the-save-the-proposal-stage-its-queue-and-its-check-are-deleted)):
   **an office that holds no `attribute.define` is an office that cannot name a new thing at all**, because a
   value recorded against a code nobody has defined is refused rather than filed. §12 states what that costs.
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
- **Which offices' grants carry `MEMBERS`: per office, by whoever writes the grant, no default either way
  — not into the expression and not out of it — and that is the ruling.**
  Which offices are written without the term is decided **per office, by whoever writes the grant**
  ([D-165](../decisions/round-22.md#d-165--there-is-no-default-for-members-and-that-is-the-decision)):
  no office can inherit an entitlement by being written from a template, and no office can inherit a
  lockout that way either. No screen adds the term and no screen strips it. The answer is written into a
  grant's expression, and the control D-100 nominated for it exists — as a section of a page, not a report:
  **the `Unusual` section of the tab on the permissions page lists live grants naming a `ROLE(…)` operand
  whose expression contains no `MEMBERS`** (§11) — every one of them, not the offices somebody marks
  sensitive, because a list filtered by which grants *should* carry the term would encode exactly the default
  this ruling declines to set. And **a grant written without the term needs no reason field**:
  `grant_reason` is already an optional column on the row
  ([05 §6](../data-model/05-authorization.md#6-access_grant--the-per-item-layer)) and it stays optional,
  because requiring one would turn the absence of a default into a small approval process. *The list's width
  — every such grant rather than a marked subset — and the day-one clause below are this round's reading of
  the ruling, not the ruling's own words.* Nothing is refused and nothing is warned when such a grant
  is saved. *Why: that test fires on the intended case as often as on the mistake, and a prompt that
  cries wolf teaches the writer to route around it, so
  [F-13](../open-questions.md#f-13) closed on the weaker half on purpose
  ([D-109](../decisions/round-13.md#d-109--nothing-a-rule-names-is-deleted-deprecated-hidden-disabled--and-a-tab-instead-of-a-report)).*
  **Day one's grant carries no `MEMBERS` term at all** — it names a person, and a grant aimed at one
  person has no expression to carry one, **and a grant that has no expression to carry one cannot be read
  as having declined one** — so the lockout
  [D-051](../decisions/round-04.md#d-051--the-membership-gate-is-waived-by-a-permission-not-only-by-a-role-flag)
  was written against is answered by
  [D-150](../decisions/round-21.md#d-150--day-one-is-one-account-holding-systemadmin-and-nothing-else-is-shipped),
  not by an exemption. What is still owed is the thing F-13 itself nominates: whether those
  `MEMBERS`-less office grants turn out to be mistakes or choices.
- **What a holder of `access_grant.create` may write now has a bound, and the bound is the writer.**
  **A write to `access_grant` may name only a permission that the person writing it holds, at a scope
  that reaches what they are writing** — the granter's ceiling
  ([D-163](../decisions/round-22.md#d-163--a-grant-may-not-confer-more-than-the-granter-holds)), stated
  where the model states write-path refusals, as check 7 of the seven in
  [05 §6](../data-model/05-authorization.md#6-access_grant--the-per-item-layer).
  **And the bound reads a grant and nothing else, which [D-188](../decisions/round-23.md#d-188--the-ceiling-reads-a-grant-and-nothing-else-and-what-it-leaves-open-is-written-down)
  ruled and this page has to carry beside the rule:** the ceiling reads a write whose subject somebody chose, so
  it does not read an edit to an audience's expression tree, does not read adding a person to an office behind
  `role.assign`, and does not read the twelve rows an event creation writes
  ([D-170](../decisions/round-22.md#d-170--the-ceiling-does-not-read-the-twelve-a-create-writes)), and that
  exemption covers exactly one transaction: a write that rebuilds a missing bundle by hand is a person choosing
  rows, so the ceiling reads it like any other grant. The widening that leaves is on the record and not a
  discovery — `audience.manage` is not a lesser code than
  `access_grant.create` and must not be granted like one, which is the sentence this file owes for both codes and
  carries beside the `audience.manage` bullet below.
  `access_grant.create` has always said *you may write grant rows*; that it never said *what they may
  say* was this file's sharpest hole, and the answer is none of the three options this page offered —
  no second code for the `system.` namespace, no two-person rule, no verdict of trail-and-judgment.
  *Why: the level ladder was still doing this one job — a grant could not carry a rank above
  its writer's own — and
  [D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)
  deleted it without replacing that ceiling; the bound that came back is the check the resolver already
  performs, pointed at the granter at save time, so a writer predicts *may I grant this?* from the
  question they already ask.* Three consequences, each stated with the rule on 05 §6: a right held only
  through a delegation **does not raise** the ceiling — lending is not holding — and delegation still
  works, because the delegator writes the row and holds the right directly; the ceiling stops
  **escalation** and not **spread**: a person who holds `person.view` at the unit may hand it to twenty
  people, since they hold it, and **no report covers that distribution and none was called for.** The entry a
  reader will find nearest to the claim, the wide half of check 7 in
  [05d §11](../data-model/05d-invariants-and-seed.md#11-invariants-to-verify), is about something else — a
  grant that widened because a set under a `-` stopped resolving, which is an expression changing shape under
  a row nobody edited; and
  `granted_by` is now the precondition of a security rule rather than bookkeeping, because the ceiling
  reads a named person and
  [D-125](../decisions/round-17.md#d-125--an-empty-actor-column-is-this-system-acting-on-its-own-and-its-name-comes-from-a-fixed-list)
  guarantees every grant row names one. Day one is untouched: the account of
  [D-150](../decisions/round-21.md#d-150--day-one-is-one-account-holding-systemadmin-and-nothing-else-is-shipped)
  holds `system.admin` at the unit, which satisfies every code, so the origin of authority is exempt by
  construction rather than by a special case.
- **`event.grant_access` has a subject, and the subject is every event.** What distinguishes it from
  `access_grant.create` is the scope alone (§8a), and the reading this file left open is the one that stands:
  it is a scoped front door onto the same table, and it arrives **in the bundle of twelve that the act
  creating an event writes beside it**, so whoever runs an event hands access to that event out without
  holding `access_grant.create` at the unit and without asking anybody
  ([D-151](../decisions/round-21.md#d-151--creating-an-event-writes-the-events-authority-and-its-organizers-may-grant-on-it)).
  **The two codes authorize the same write to the same table, and what differs is which code the person was
  given** — the resolver matches one code exactly, the item-facing screens check `event.grant_access` and the
  general permission screens check `access_grant.create`. *That is two codes for one write, said here rather
  than dressed up as an invariant.* What makes it survivable is that they come through different doors: one
  is in every event's bundle and leaves when the event's grants end, the other is a unit-scope decision about
  who may operate the permission system. **And the ceiling is structural either way** — the scope an
  organizer may write is the event they run, and `applies_to = unit` refuses `system.admin` on an item at the
  save, so the wildcard cannot be handed out from an event (§1, §7).
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
- **`audience.manage` is one code over an expression, and the largest act it covers is now marked: composition is
  inside it, and the ceiling does not read it.** Composition *is* the expression now
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
  that names it. **Settled: composition is documented as plainly inside `audience.manage`, the consequence is
  accepted rather than coded around, and no code was invented to fill the gap**
  ([D-188](../decisions/round-23.md#d-188--the-ceiling-reads-a-grant-and-nothing-else-and-what-it-leaves-open-is-written-down)).
  The alternative was not safer, only wider: a ceiling that read an expression edit would have to resolve what that
  expression means for every live grant aimed at it, at the moment of the save, inside the definition of a
  permission's reach — a permission check running while the check is being changed, which is a recursion this corpus
  has refused before. **So the rewriting is escalation and the ceiling does not see it**, bounded only by what the
  vocabulary can be made to read: to admit one named person an editor still has to be able to name a set that person
  falls into, and putting them in an office is a separate act behind `role.assign` — while the broad case,
  `ROLE(camp organizer)` rewritten to `MEMBERS`, needs neither of them. What is left as the control is the editor
  showing the expanded set and the affected grants *before* the save, which is a user-interface requirement carried in
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
- **D-100 wrote its 1 January rule about an office, and on day one there is no office for it to fail in.**
  The entry assumed an administrative office exists and is written without `MEMBERS`, so the expiry sweep of
  [D-040](../decisions/round-02-03.md#d-040--the-fee-expires-yearly-a-date-tracked-renewal-window-replaces-a-grace-status)
  cannot lock the administrator out. **Day one cannot be locked out, because it has no office**: the one
  grant names one account rather than an expression, so there is no `MEMBERS` in it to add and none to
  forget, and the person who set the system up is still holding everything on 1 January
  ([D-150](../decisions/round-21.md#d-150--day-one-is-one-account-holding-systemadmin-and-nothing-else-is-shipped)).
  **What moved is where the mistake can be made**: it is now whoever first writes
  `MEMBERS * ROLE(system_admin)` "for consistency" (§11), and every office grant that will ever exist has
  been written by hand, since no grant arrives from anywhere carrying anything (§11). The January reason
  survives as a property of day one rather than as a rule about offices, and that is now the ruling and
  not a reading: the design states no default for `MEMBERS` in either direction
  ([D-165](../decisions/round-22.md#d-165--there-is-no-default-for-members-and-that-is-the-decision)).
- Whether reporting should be gated per report by one permission with row-level
  filtering. **Answered, and answered by deleting the question:** [D-210](../decisions/round-25.md#d-210--a-report-is-a-delivered-message-so-all-five-report-codes-are-deleted-and-reporting-stops-being-a-name)
  ruled that what an organization calls a report is a message of a type addressed to an audience and delivered
  by the messaging module, and that **there is no report screen in this design** — so there is no permission to
  shape, no row-level filter to attach to one, and no namespace to defer. Reporting is not a permission, not a
  module, and not a deferred item: it is an audience and a type
  ([../data-model/10-messaging.md §8](../data-model/10-messaging.md#8-reports-arrive-here-and-stop-being-a-name)).
  **Everything [D-195](../decisions/round-24.md#d-195--the-money-codes-are-shipped-codes-catalog-a-grows-a-money-section-and-catalog-b-10-loses-three-rows)
  refused to decide by accident now decides itself:** the finance module spends its six codes and no seventh,
  money is gated by `fee.view` and `payment.view`, and no money report code exists anywhere to be promoted or
  deferred — the module's money and the listing somebody might want over it are simply no longer the same kind
  of thing. The §10 row is gone with them, and the codes that ever had a row in
  [catalog A](permission-catalog-a-codes.md) are named in [the dead-name register](removed-concepts.md).
- Whether the organization has offices this catalog does not anticipate (a chaplain, a
  quartermaster, a camp chief). **This is answerable by the organization itself** rather than by a
  change to the data model and a migration — one `role` row and some grants — which is the point of
  roles being runtime data. Since D-098 the same is true of a set of people who simply do things
  together, and the two are told apart by which table they are in and therefore by which code protects
  them (§5a).
- Which audiences the organization needs, and who may create a `person_group` — `audience_admin` is
  proposed, and it is an office rather than a unit leader's extra code now that there are no units
  ([D-042](../decisions/round-02-03.md#d-042--grants-may-target-audiences-not-only-individuals),
  [F-5](../open-questions.md#f-5)).
  **There are no kinds of audience** — one expression language over named sets, no built-in versus
  named split and no filling rules
  ([D-091](../decisions/round-09.md#d-091--a-permission-group-is-a-rule-and-a-list-at-once-and-a-rule-may-name-another-group),
  [D-101](../decisions/round-10b.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree)) —
  so this is genuinely two questions: which `selector_type` operands the language has, which is thirteen
  and §1 prints the names, and who may create a group, which is `person_group.create` (§5a).
  **Neither question is "which audiences ship", because none do.** The two named audiences went and
  **nothing replaces them**: everything either one carried is written as an operand where the grant is
  written — `EVERYONE` for "every person", `MEMBERS` for "everyone holding a membership live on the
  checked date" — and an
  audience earns its row when somebody intends to name it (`AUDIENCE(x)`)
  ([D-153](../decisions/round-21.md#d-153--two-named-audiences-go-and-nothing-replaces-them)).
  **No operand names a person's guardians:** the channel carries a level over a child, not a set
  ([D-113](../decisions/round-13.md#d-113--the-guardianship-channel-has-no-expression-guardians-is-not-a-selector)),
  which closes the last part of F-5; and `WHITELISTED`, the one name with no stored state behind it, is
  **refused rather than pending**
  ([D-148](../decisions/round-20.md#d-148--there-is-no-whitelisted-and-the-refusal-is-written-where-the-tiers-are))
  and so is not a gap in the registry — **no operand may be added for it, and nothing reserves its name**.
- **Which office may put a person on a group's roster is not named, and the blank is the answer.**
  [D-167](../decisions/round-22.md#d-167--the-office-that-may-place-a-child-in-a-group-stays-unnamed)
  rules that this stays unnamed **on purpose**, so that no later round repairs it as a hole:
  `person_group.member.manage` is the whole of the right
  to place a person in a set — one code,
  `applies_to = unit_and_item`, never self-scoped, and the only thing between a person and a roster
  (§5a, §11 property 6) — and on day one the only grantee that may write a roster is the one account
  holding `system.admin` at the unit. The catalog's side is settled; which volunteer office holds the
  code is the organization's decision to record as `role` rows and grant rows, for the reason §11
  property 6 carries: an appendix that quietly hands it to `leaders` would be making a safeguarding
  choice on someone else's behalf. The cost sits in day one rather than in the schema — the first
  roster anybody builds is built by the account that must not be used day to day — and the relief is
  one `role` row and a grant, not a migration
  ([D-154](../decisions/round-21.md#d-154--counselors-is-an-example-now-not-a-shipped-office),
  [D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)).
- **Which scope a send should carry — closed: one code, at the unit, and nothing about its target checked.**
  This item asked whether the wide messaging code should be `applies_to = unit` only or
  `unit_and_item`, so that a body could be given the power to address its own roster and nothing
  wider. [D-208](../decisions/round-25.md#d-208--messagesend-is-the-only-messaging-code-and-the-audience-a-send-names-is-not-checked)
  answered it by registering one code, `message.send`, at the unit, and by ruling that **what a send names is
  not checked**: a send carries either one person or a saved audience on the message itself, so **an audience
  narrows the send, and no grant scope narrows it** — the code reaches everybody, and a holder may address a
  member they have never seen. **The other half of the answer is that a job holds no code at all**: a
  permission gates an act, a scheduled job has none, and an automated send is therefore not gated by this code
  and reaches the audience its type names — one message carries one target, and an automated type must name its
  audience, so there is no second set the run could add to it
  ([10-messaging §7](../data-model/10-messaging.md#7-who-may-send-and-what-is-not-checked)), which is also why
  no narrower code exists to be scoped for a job either. That is why the two names this item was written around
  retire rather than get a scope — they never had a row in [catalog A](permission-catalog-a-codes.md), which is
  what a register is for, and they get no entry in [the dead-name register](removed-concepts.md) either, because
  a death certificate is for something that lived. [D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)
  is untouched: one grant, one permission, one scope, and `message.send` carries `applies_to = unit` and stops
  there ([10-messaging §7](../data-model/10-messaging.md#7-who-may-send-and-what-is-not-checked)). **Who holds
  it is the granter's decision**, and the ceiling over handing it out is
  [D-163](../decisions/round-22.md#d-163--a-grant-may-not-confer-more-than-the-granter-holds); **what it costs is
  on the record** — a person holding no code has no way to write to the organization through this module, and no
  route for that person is designed anywhere.
- **`membership.manage` does not exist, and five places in these documents used it as their example.** D-099
  quotes the organization's own observation — *"on an event, `membership.manage`, or `event.create`, make
  no sense"* — the domain model and the authorization module each restate that sentence as the reason
  `applies_to` exists, and the events page carries a refusal row naming the code. **This catalog has
  never registered it** — membership acts are `membership.activate`, `.lapse`, `.suspend`,
  `.terminate`, `.backdate` and the request pair (§4) — and **no code is minted here to make an example
  true**: a refusal that names nothing refuses nothing, which is the class of bug D-097's `unit_leaders`
  correction exists to warn about. **The five places now name `membership.terminate`, which is the exact
  fit and a registered code** — a fact about a person at the unit that no event owns — found by the
  registry diff rather than by a reader ([D-127](../decisions/round-18.md#d-127--the-registry-diff-is-a-committed-script-and-it-gates-a-round));
  the organization's quoted words are left as they were spoken. Had the other branch been taken, the
  code would owe what every registered code owes: a `right_kind`, an `applies_to`, a ⛔ mark, and a row
  in §4. **This was one instance of the gap D-104 closes as
  [F-19](../open-questions.md#f-19):
  a code is a row that ships, this catalog is prose about rows, and the check adopted is a two-way report
  over the shipped registries, run by hand.** D-104 supplied the grammar and the report; **it did not
  re-point these five sentences**, and that repair still belongs to whoever owns each of those pages.
- **The registered spelling of a code is this catalog's, and prose is prose.** `event.answer.view` is
  singular — the code in §8a, one of the twelve grants §11 says are written beside every event, and no
  other spelling
  ([../data-model/08a-event-guards-and-checks.md §8](../data-model/08a-event-guards-and-checks.md#selectors-that-bind-to-an-event)
  records how that was settled, and **the catalog is the arbiter**). The case that did not settle quietly
  is the finding worth carrying: a door-scanning capability was argued over at length and exists
  **nowhere** — not in this catalog, not in the events module, not in the ERD, not in the decision log —
  so nothing ever refused it, because since
  [D-072](../decisions/round-06.md#d-072--the-documentation-carries-no-sql-the-schema-is-the-orms-job)
  these documents *are* the specification and a permission legally exists only as a row in the shipped
  `permission` registry; the question that ends any such argument is *which shipped row carries this?*
  ([D-104](../decisions/round-10b.md#d-104--a-permission-codes-last-segment-is-an-action-and-a-registry-that-prose-contradicts-is-a-fiction)).
  What survives of it is §1's three rules, the two-way registry report D-104 adopts, and a presence story
  that is `event.presence.mark` and nothing more (§8a,
  [D-067](../decisions/round-05.md#d-067--presence-is-a-three-valued-fact-on-the-registration)).
  **If door scanning is ever wanted it arrives as an open question and then a decision entry naming the
  permission, the artifact that rotates and who may reprint it — not as a code beside a paragraph about
  a door.**
- **`attribute.define` is in the catalog and in no office §11 works through — and who holds it is now answered,
  by a person and a period rather than by an office.** The permission and its rules are settled (§2), and so is
  the second half of what AT-2 asked: **there
  is no proposal, so there is no age for a proposal to reach**
  ([D-141](../decisions/round-20.md#d-141--a-definition-is-live-at-the-save-the-proposal-stage-its-queue-and-its-check-are-deleted)).
  **Who holds the code was what remained, and [D-189](../decisions/round-23.md#d-189--one-author-writes-the-vocabulary-before-the-batch)
  answers it: one named person, holding the code, writing the definitions the legacy corpus needs before the load
  that would refuse them, and keeping the code afterwards** — the handover is an ordinary dated grant aimed at one
  person rather than an office, which is the shape §11 property 7 recorded for it. Both of the register's rows for
  this question are in § R now: [AT-2](../open-questions.md#at-2) closed on the mechanism and
  [F-34](../open-questions.md#f-34) on the schedule the deleted proposal stage had secretly been carrying. The
  schedule cannot live in a reminder either — nobody is told anything, the author included, and the reason is
  that no message type is configured for a definition going stale rather than a rule about verbs — so the page
  that states the rule is where the deadline lives
  ([D-164](../decisions/round-22.md#d-164--nobody-is-told-and-no-page-may-say-otherwise) as narrowed by
  [D-214](../decisions/round-25.md#d-214--the-system-sends-and-d-164-is-narrowed-to-the-one-thing-it-was-protecting)).
  **The risk of leaving it unheld changed kind and got
  worse.** While a proposal stage existed, an office without the permission was a slow leak: values arrived
  against invented codes, sat in a queue, and the vocabulary rotted while still storing everything. Now a value
  recorded against a code nobody has defined is **refused at the write**: an office that cannot name a new
  thing writes it into the free text that is left on the rows *about* a person — a roster row's `note`, an
  account's `status_reason` — or does not write it at all, which is the exact failure the whole
  attribute layer exists to prevent, arriving as a wall rather than as a leak. **The person row itself no longer
  has anywhere for it:** `person.notes` is deleted and the vocabulary took its job, so there is no longer a place
  to write something about a child that is not in the vocabulary
  ([D-191](../decisions/round-23.md#d-191--personnotes-is-deleted-and-the-vocabulary-takes-the-job)). The checks that notice a
  vocabulary rotting are in [../data-model/09-attributes.md §8](../data-model/09-attributes.md#8-integrity-checks),
  and none of them can fire on codes nobody was able to create.
  **The import half is answered, and only that half:** every code the legacy load's column→code map names must
  already be defined and `live` when the script writes the rows, and a source column that maps to nothing is an
  error and not a proposal — so the
  vocabulary is authored *before* the import that looks like it produces it, and day one does not arrive with
  several hundred codes nobody has read
  ([D-141](../decisions/round-20.md#d-141--a-definition-is-live-at-the-save-the-proposal-stage-its-queue-and-its-check-are-deleted),
  [D-090](../decisions/round-07-08.md#d-090--the-legacy-corpus-is-thousands-of-roster-rows-with-numbers-and-no-money),
  [../domain/03-identity-and-legacy.md §7](../domain/03-identity-and-legacy.md#7-legacy-import-pipeline)).
  **That refusal was a rule about a pipeline, and the pipeline is gone:** what survives is the invariant
  underneath it — a value may not invent a code — which now binds the script, and every write after it, exactly as
  hard ([D-190](../decisions/round-23.md#d-190--the-legacy-import-is-a-script-and-a-key-and-the-pipeline-is-gone)).
**Settled, so that nobody reopens them from the shape of this page.** A grant carries one code, and there
is neither a level nor a "nearest scope wins" ordering to pair with it
([D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality));
nothing is implied by a code — the grant editor may *offer* a companion read and taking it writes a second row,
so the database holds rows and no dependency is stored anywhere, in no table and read by no gate
([D-194](../decisions/round-24.md#d-194--nothing-is-implied-by-a-permission-the-editor-offers-the-companion-read-and-the-database-stores-two-rows));
the money codes are shipped codes and only six of them
([D-195](../decisions/round-24.md#d-195--the-money-codes-are-shipped-codes-catalog-a-grows-a-money-section-and-catalog-b-10-loses-three-rows));
the unit is a scope and never a row
([D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row));
nothing owns an event
([D-102](../decisions/round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it));
leadership is an office, not a position
([D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape));
`PERSON(x)` is in the selector language and `LIST` is not, and
[data-model/05a §8](../data-model/05a-audience-and-grammar.md#8-audience--grants-that-target-a-set-of-people)
is where the operand registry is written out in full, thirteen rows, each one either a rule about people or
a row that takes an argument; presence is not a set anyone may be granted
over (§1 carries the argument); a code's last segment is an action (§1,
[D-104](../decisions/round-10b.md#d-104--a-permission-codes-last-segment-is-an-action-and-a-registry-that-prose-contradicts-is-a-fiction)).
**Every one of those is one entry in
[decisions/index.md](../decisions/index.md), findable by number, and each entry names what enforces the
rule now** — which is the discipline [D-081](../decisions/round-06.md#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now) states.
**What is open is the list above this paragraph, and nothing else in this file.**

Nothing above is on its way to [../open-questions.md](../open-questions.md): round 24 emptied that register and left the asking on this page, so an item here closes by having its answer written **into the bullet above**, and one that is genuinely still open stays open here rather than being handed back to the register.
