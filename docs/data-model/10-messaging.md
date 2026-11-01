# Data Model — Messaging

The module [README](../README.md) kept in its deferred list from round 1 to round 24, opened by
[D-206](../decisions/round-25.md#d-206--a-message-is-one-table-this-system-is-one-of-its-authors-and-a-notification-is-a-type-of-message).
It was deferred because a corpus that had decided, since round 22, that nothing is sent
([D-164](../decisions/round-22.md#d-164--nobody-is-told-and-no-page-may-say-otherwise)) has no business drawing a
sending machine, and the deferral held through every one of the twenty-four rounds before this one for a good reason. What opened it was not a change
of heart about talking to people; it was the answer to a different question — *what is a report, and who receives
one* — which turned out to need a delivery, and a delivery turned out to be the same object as a letter.

**Read [05a](05a-audience-and-grammar.md) first.** Half of this module is the audience machinery that page
already documents, seen from the side of a write instead of a check.

---

## 1. One word, one table, and what a notification is

**There is one thing and its word is `message`.** A row in `message` has exactly one author, and the author is
either a person or this system acting on its own. **A notification is a message whose `message_type_id` is set** —
a kind of row, not a table, not a module, and not a second mechanism beside the one a person uses to write to
another person ([D-206](../decisions/round-25.md#d-206--a-message-is-one-table-this-system-is-one-of-its-authors-and-a-notification-is-a-type-of-message)).

The alternative was designed and refused: a `notification` table beside `message`, so that an automated notice and
a person's letter could be told apart without reading a column. It is two tables of the same shape, which
[D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)
refuses on sight, and the difference it buys is already bought twice over by the author columns and by the audit
row every write in this design owes ([D-184](../decisions/round-23.md#d-184--every-table-is-audited-and-the-delete-carve-out-names-the-moments-that-survive)).
What it would cost is three more things to keep honest — its own expiry rule, its own audit shape, and its own
reader — and this corpus has watched four pages drift apart over one sentence about a NULL.

**Three tables, then.** `message_type` is what may be sent automatically and whom it reaches; `message` is a body
with one author; `message_recipient` is whom it reached, on which door, and whether it was opened.

## 2. `message_type` — a vocabulary that is also a settings panel

| Field | Kind | Notes |
|---|---|---|
| `id` | surrogate id | |
| `code` | text, required, unique among live rows | The vocabulary: `renewal-window-opened`, `fee-overdue`, `registration-confirmed`. **Renamable, and this is the register's own test rather than a convenience** ([D-131](../decisions/round-18.md#d-131--shape-4-is-not-empty-and-a-code-that-is-referenced-may-not-be-renamed)): a `message` points at its type by id, so a rename rewrites nothing inside the database — exactly the audience code's case, which [the register](00a-invariant-register.md#4-a-value-that-may-never-change-once-set) names as the correction rather than a member. What sits outside the database is an installation's own job configuration, and a rename there is that installation's edit to make |
| `name` | text, required | What a screen shows; editable, unlike `code` |
| `description` | text | |
| `audience_id` | reference to `audience`, **required when `is_automated`** | Whom this type reaches. An admin edits it; it is the setting this table exists to hold ([D-209](../decisions/round-25.md#d-209--a-message-type-is-a-row-and-the-audience-it-reaches-is-configuration-an-admin-edits)) |
| `is_automated` | boolean, required, default false | True exactly when a job may write this type. False means the type is a label a person may choose when they write — it does not make the type fire |
| `valid_from`, `valid_to` | dates | `valid_to` **retires** a type. A type is never deleted: a message written against it would point at nothing ([D-109](../decisions/round-13.md#d-109--nothing-a-rule-names-is-deleted-deprecated-hidden-disabled--and-a-tab-instead-of-a-report)) |
| `created_at`, `created_by` | when, who | |

**This is [`membership_type`](03-membership.md) a second time, and the diagnosis is the same one
[D-186](../decisions/round-23.md#d-186--membership_type-is-settings-wearing-a-vocabularys-clothes) made.** The
code is the vocabulary and the audience is a setting; what an organization changes on a Tuesday afternoon is the
second and not the first. Say it plainly because the shape invites the wrong edit: a table with a `code` column
reads like something only a migration may touch, and a table whose whole purpose is a column named `audience_id`
reads like something a person edits from a screen. It is the latter, wearing the former's clothes.

**What gates an edit here is not settled.** No code is proposed for this table, and
[D-152](../decisions/round-21.md#d-152--zero-is_system-columns-what-protects-a-vocabulary-is-its-table-not-a-flag-on-its-rows)
is the precedent for refusing one; the working default is whoever holds `system.admin` at the unit. It is
[K-12](../open-questions.md#k-12).

## 3. `message` — one author, one target, and no second version

| Field | Kind | Notes |
|---|---|---|
| `id` | surrogate id | |
| `message_type_id` | reference to `message_type`, nullable | **Null means a person's own letter**, of no type. Set means a notification, and that is the whole of what a notification is |
| `author_person_id` | reference to `person`, nullable | **Exactly one of this and `actor_label`.** A person who wrote it |
| `actor_label` | text, nullable | For a message this system wrote, from the fixed list in [`00-conventions §7a`](00-conventions.md#7a-what-an-empty-actor-column-means). Automated traffic is authored by `system:messages` and by nothing else ([D-212](../decisions/round-25.md#d-212--systemmessages-is-the-sixth-actor-label-and-the-renewal-sweep-stops-being-a-sender)) |
| `subject` | text, required | |
| `body` | text, required | Free text, and it stays free. **Never edited** — see below |
| `target_person_id` | reference to `person`, nullable | **Exactly one of this and `audience_id`**: one person, or an audience |
| `audience_id` | reference to `audience`, nullable | Set means the audience was resolved once, at this write, and the rows below were written from it |
| `written_at` | timestamp, required | When it was written, which is the moment the act happened |

**A message is never edited.** A body written is a body kept; a wrong send is followed by a second message saying
what the first got wrong. This is [D-183](../decisions/round-23.md#d-183--a-changed-ask-is-a-voided-request-and-a-new-symbol-and-amount_discount-goes)'s
rule about an ask, reused without ceremony, and it is what makes §9's refusal to expire anything survivable: a
design that keeps text forever may not also be a design that rewrites it.

**Exactly one target, never both and never neither.** The same discipline a `fee_obligation` keeps over its three
possible targets ([`07-finance`](07-finance.md)). A message with no target is a draft, and **there is no draft
state in this design** — nothing here has one, and a `message` row is an act that happened.

**The absence, named because it looks like a bug.** An audience that resolves to nobody writes no recipient rows,
and the message row still exists. That is not an error and there is no queue holding it: it is money that arrived
under no symbol, shaped as words ([D-180](../decisions/round-23.md#d-180--there-is-no-queue-for-money-that-does-not-fit)).

## 4. `message_recipient` — the act recorded, and nothing more

| Field | Kind | Notes |
|---|---|---|
| `id` | surrogate id | |
| `message_id` | reference to `message`, required | |
| `person_id` | reference to `person`, required | Whom this row says was addressed |
| `channel` | enum, required | **Two values today: `inbox` and `email`** — §5. One row per door a person actually has open, so a person with e-mail off has one row and a person with it on has two |
| `mirrored_from_recipient_id` | reference to `message_recipient`, nullable | Set when this row exists because of §6, not because the sender named this person. It is what makes "the sender was shown this would happen" a plain read at the write |
| `opened_at` | timestamp, nullable | Null means not opened. **The column is not proof of reading** — it is a screen being drawn, and no page may make it mean more, which is the same limit [`05c`](05c-access-log-and-resolver.md) puts on an access row |

**These rows are the record of an act, and nothing resolves against them.** No audience expression may name a
message's recipients as a set, and no report — in the old sense of a screen — may be built on `SELECT` over them
as though the set were the point. This is the half of
[D-110](../decisions/round-13.md#d-110--the-expression-is-the-record-of-whom-a-grant-reached) a reader could have
carried in backwards: **a grant's** record of whom it reached is the expression it holds, because the expression
is the authority; **a message's** record is these rows, because an audience can be edited tomorrow and the fact
that thirty people were addressed in March must not change with it.

**Why a table of "whom it reached" is not a vocabulary.** Because nothing reads it as a set of people who are
something. `ATTENDED` exists as a selector because a rule needed to ask "who came"; nothing asks "who was
addressed in March" as a condition for anything, and the moment something does, that something needs its own named
operand and not this table ([D-113](../decisions/round-13.md#d-113--the-guardianship-channel-has-no-expression-guardians-is-not-a-selector)
is the precedent for refusing the shortcut).

## 5. Doors: the account chooses, the inbox is not one, and only e-mail lands

**The choice belongs to the account.** One column, `account.opt_in_email` — boolean, required, default **false**,
which is [D-077](../decisions/round-06.md#d-077--messaging-is-direct-by-default-broadcast-is-an-ordinary-scoped-permission-and-the-recipient-chooses-the-channel)'s
"the recipient chooses the channel" finally getting a place to live
([D-213](../decisions/round-25.md#d-213--the-account-chooses-its-own-doors-a-childs-message-mirrors-as-its-own-rows-and-only-e-mail-lands-today)).

**The inbox is not a door and cannot be turned off.** `channel = inbox` is the record that a message exists for
you; a design in which that can be declined is a design in which "you were addressed" has no evidence behind it.
Everything a person sees of this module arrives through the inbox first, and the doors beside it are copies.

**A door arrives with its column on the day its transport exists.** E-mail has one because
[`person_contact`](01a-accounts-and-contacts.md#6-person_contact) already carries a verified `email` value, and a
message with no address to go to writes no row for that door — which is a fact about the person's contacts, not a
failure of the send.

**No column is written for a thing this design cannot do.** That is the whole of what this page declines: a
device token is not a contact point — a person holds several, they expire without telling anyone, and every value
of `contact_type` (`email`, `phone`, `postal`, `website`, `messaging`) describes something that survives its
device — while a text message would land on the `phone` row and has nothing carrying it. **Both refusals are
named with their reasoning in [D-213](../decisions/round-25.md#d-213--the-account-chooses-its-own-doors-a-childs-message-mirrors-as-its-own-rows-and-only-e-mail-lands-today),
and nowhere on this page do they have values**, for the reason [D-192](../decisions/round-23.md#d-192--proposed_by-loses-import_job-because-a-vocabulary-value-is-a-claim-about-who-can-write)
drew from an enum value that claimed a kind of actor existed: a vocabulary column that holds a thing the system
cannot do is a bug that has already been committed. Where a device token will live is
[K-15](../open-questions.md#k-15).

## 6. A child's message mirrors as rows

**A message addressed to a minor is mirrored to that minor's guardians as their own recipient rows, on their own
chosen doors** ([D-082](../decisions/round-07-08.md#d-082--a-direct-message-to-a-minor-is-mirrored-to-the-minors-guardians),
now given its physical form by
[D-213](../decisions/round-25.md#d-213--the-account-chooses-its-own-doors-a-childs-message-mirrors-as-its-own-rows-and-only-e-mail-lands-today)).
Each mirror row carries `mirrored_from_recipient_id`, and each is written on the guardian's own door choice, not
the child's.

**No table and no age branch in the resolver.** Guardianship is the channel that says who a child's guardians are,
and it carries a `right_level` and needs no selector
([D-113](../decisions/round-13.md#d-113--the-guardianship-channel-has-no-expression-guardians-is-not-a-selector));
[`04-relationships`](04-relationships.md) already answers "who are this child's guardians" for every other feature
in this design. What the ruling adds is rows, and a row is why the sender can be shown the mirroring at the write:
the rows are computable before they are written, so the notice about them is an ordinary in-app statement rather
than a message about a message.

**Whether an audience-addressed message mirrors at all is not ruled.** A message to one named child mirrors; a
message to an audience may contain a hundred children, each of which mirrors on this reading, which is a thousand
rows and a guardian learning their child was on a list nobody told them about. It is
[K-11](../open-questions.md#k-11), and the answer changes the row count of every announcement in this module.

## 7. Who may send, and what is not checked

**`message.send` is the only messaging code** ([catalog A](../appendix/permission-catalog-a-codes.md)), `applies_to
= unit`, marked twice for sensitivity. It authorizes writing a message to one person **or** to an audience
([D-208](../decisions/round-25.md#d-208--messagesend-is-the-only-messaging-code-and-the-audience-a-send-names-is-not-checked)).

**Writing one message to one person needs this code too.** [D-077](../decisions/round-06.md#d-077--messaging-is-direct-by-default-broadcast-is-an-ordinary-scoped-permission-and-the-recipient-chooses-the-channel)
used to make a direct message everyone's, with a permission only for reaching a crowd; from this round one code
gates every write and *"direct"* names a send's shape rather than a right
([D-208](../decisions/round-25.md#d-208--messagesend-is-the-only-messaging-code-and-the-audience-a-send-names-is-not-checked)).
**The cost is stated here because nothing else in this module pays it:** a person holding no code has no way to
write to the organization through this module, and **no route for that person is designed on this page** — the
answer named one code and this design does not soften it with an ungated exception beside it.

**The target is not checked.** There is no per-person test over an audience, no requirement that the writer could
read the rows of everyone addressed, and no rule that an event's organizers may address only their event. This is
a choice, not an oversight, and the two controls that remain are the ceiling — which governs **who may hand the
code out** and not what a send may name ([D-163](../decisions/round-22.md#d-163--a-grant-may-not-confer-more-than-the-granter-holds))
— and one audit row for every send ([D-184](../decisions/round-23.md#d-184--every-table-is-audited-and-the-delete-carve-out-names-the-moments-that-survive)).
**The widening is on the record**, in the same sense [`05d §12`](05d-invariants-and-seed.md#12-what-day-one-looks-like)
puts it for every other coarse code: one code, wide, because the alternative was a test this design has no rule to
write.

**A job does not hold the code.** A permission gates a person's act; an automated message is authored under
`system:messages` ([D-125](../decisions/round-17.md#d-125--an-empty-actor-column-is-this-system-acting-on-its-own-and-its-name-comes-from-a-fixed-list)),
and the run writes one audit row for itself ([D-212](../decisions/round-25.md#d-212--systemmessages-is-the-sixth-actor-label-and-the-renewal-sweep-stops-being-a-sender)).
Which clock fires which type is [K-14](../open-questions.md#k-14).

## 8. Reports arrive here, and stop being a name

**What an organization calls a report is a message of a type, addressed to an audience, delivered by §1's
machinery.** There is no report screen in this design, and the five codes reporting used to have are gone with it
— two shipped and three deferred, all named with their reasoning in
[D-210](../decisions/round-25.md#d-210--a-report-is-a-delivered-message-so-all-five-report-codes-are-deleted-and-reporting-stops-being-a-name)
and listed in [the appendix of dead names](../appendix/removed-concepts.md). **Reporting is not a permission, not a
module, and not a deferred item: it is an audience and a type.**

**Two cases already in this corpus, which is why the module was not drawn in the air.** Money that arrives under
no symbol, and money that is late, both of which [`07-finance`](07-finance.md) used to hand to a person who might
someday open a list. Both are now a type with an audience.

**An integrity check is a run, not a report.** [`05d §11`](05d-invariants-and-seed.md#11-invariants-to-verify) is read
by whoever runs it, and its three checks whose correct first run looks like a failure stay exactly as they are.
Where a check is meant to reach a person it does so as a type like anything else, and the word "report" is retired
with the codes, so no check borrows it to describe itself.

## 9. Nothing ages out, and erasure does not reach this

**A `message`, its body, its recipient rows and their `opened_at` are never scheduled away and never emptied by an
erasure** ([D-211](../decisions/round-25.md#d-211--nothing-about-a-message-ages-out-and-erasure-does-not-reach-messages)).
This sits beside the accounting skeleton, which [D-088](../decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)
keeps indefinitely, and against the two clocks that do run: audit payloads, which empty at 24 months, and
`access_log` rows, which are **deleted** at 24 months
([D-145](../decisions/round-20.md#d-145--access_log-rows-are-deleted-at-24-months-and-the-job-that-does-it-has-a-name))
— one of the two exceptions to "nothing is hard-deleted" in [`00-conventions §4`](00-conventions.md#4-deletion-policy).

**The argument against this was put and refused, and the refusal is the ruling.** [D-191](../decisions/round-23.md#d-191--personnotes-is-deleted-and-the-vocabulary-takes-the-job)
deleted `person.notes` because free text about a person, outside the vocabulary and outside erasure, makes erasure
a lie. The same argument applies to a message body word for word and was declined anyway, on the ground that a
message is correspondence: an act this organization performed on a date, which is not something it deletes on
request. [`06b §4`](06b-redaction-and-checks.md#4-redaction-log) lists what erasure empties and says that this module
is outside that list **by decision, with that paragraph as its reason**.

**The consequence, not softened.** An erasure removes the person and leaves every message addressed to them. The
recipient row points at a tombstone — [`01b`](01b-merges-views-and-checks.md) is where a person's row survives as
one — and the body keeps saying what the organization told that person, when, and on which door. Nothing dangles;
it points somewhere quiet.

## 10. Open issues

- **Does an audience-addressed message mirror to guardians, or only a message addressed to one named child?** The
  row count of every announcement depends on it, and so does whether a guardian can see their child was on a list.
  [K-11](../open-questions.md#k-11).
- **What gates editing a `message_type` row?** Every write here is gated by a code and no code is proposed; the
  default of `system.admin` at the unit is a working answer, not a ruling. [K-12](../open-questions.md#k-12).
- **Does an event type propose a default audience that a per-event send may narrow?** The answer that put the
  audience on the message type named an event type first, and the difference is a per-installation default nobody
  has chosen. [K-13](../open-questions.md#k-13).
- **Which clock fires each automated type** — nightly, hourly, or at the moment a row crosses a date? The renewal
  window was deliberately date-driven rather than job-driven, so this is a real choice and not an implementation
  detail. [K-14](../open-questions.md#k-14).
- **Where a device token lives**, given that `contact_type`'s values all describe something that survives its
  device and this page refuses a column for a transport that does not exist. [K-15](../open-questions.md#k-15).
