# Decision Log — Refinement round 25 (D-206 … D-216)

> **[Round 24](round-24.md) emptied [the register](../open-questions.md). This round fills it again, on purpose,
> and that is the honest shape of it.** It opened as four questions about loose ends — three free-text columns,
> one spelling clash, and two standing questions about what reporting even is — and one of those answers came
> back as **a designed messaging module**, which is the feature [README](../README.md) had kept in its deferred
> list since round 1 and which this corpus has referred to in the conditional mood for twenty-four rounds.
> A design that gains a feature gains questions, so the register leaves zero and goes to seven
> ([K-11](../open-questions.md#k-11) … [K-17](../open-questions.md#k-17)); an empty register was never a claim
> that the design was finished, and round 24 said so in its own words.
>
> **Two of these answers reverse recent decisions, and both reversals are named rather than absorbed.**
> [D-210](#d-210--a-report-is-a-delivered-message-so-all-five-report-codes-are-deleted-and-reporting-stops-being-a-name)
> deletes four permission codes, two of them shipped, on the ground that a report is a delivery and not a screen —
> which undoes the reporting posture [round 21](round-21.md) fixed and the deferral
> [D-195](round-24.md#d-195--the-money-codes-are-shipped-codes-catalog-a-grows-a-money-section-and-catalog-b-10-loses-three-rows)
> chose one round ago.
> [D-214](#d-214--the-system-sends-and-d-164-is-narrowed-to-the-one-thing-it-was-protecting) narrows
> [D-164](round-22.md#d-164--nobody-is-told-and-no-page-may-say-otherwise), the eight-round-old rule that no page
> may say the system sends anything — the rule **twenty-nine lines across nineteen pages** were written to obey, two
> of them added by [round 24](round-24.md) itself **on 2026-11-01, the same day as this round**. Nothing here
> pretends those sentences were always going to be wrong; they were correct under the ruling that stood, and the
> ruling moved.
>
> **One answer arrived twice and differently.** Asked who a notice reaches, the first answer was *"the admin
> selects an audience for each event type"* and the follow-up was *"each message type"*. The audience hangs on
> the message type ([D-209](#d-209--a-message-type-is-a-row-and-the-audience-it-reaches-is-configuration-an-admin-edits));
> what an event type wants as a default is filed as a question instead of being inferred from the first wording.
>
> **Nothing in this round was asked that a previous round had answered** — the discipline round 23 and round 24
> both promised. Where this round touches an old decision it narrows it in the open: D-164 by D-214, D-199's
> actor list by [D-212](#d-212--systemmessages-is-the-sixth-actor-label-and-the-renewal-sweep-stops-being-a-sender),
> and [D-082](round-07-08.md#d-082--a-direct-message-to-a-minor-is-mirrored-to-the-minors-guardians) by
> [D-213](#d-213--the-account-chooses-its-own-doors-a-childs-message-mirrors-as-its-own-rows-and-only-e-mail-lands-today),
> which turns a sentence about mirroring into a rule about rows.

[← Refinement round 24 (D-193 … D-205)](round-24.md) | [All decisions](index.md)

**Where the questions came from.** None of them was in the register, because the register had just been emptied.
They were asked directly, in four batches, and each answer is quoted in the entry it produced. The two standing
questions that turned out to be load-bearing were both mine and both about reporting: what a report is, and who
receives one. The loose ends were [the three `notes` columns](#d-215--the-three-notes-columns-stay-and-erasure-empties-them),
[the `ROLE(treasurers)` spelling](#d-216--every-worked-example-names-the-office-treasurer-and-what-the-operand-reads-is-still-unstated),
and [the half of messaging catalog B §12 still calls open](#d-208--messagesend-is-the-only-messaging-code-and-the-audience-a-send-names-is-not-checked).

---

## D-206 — A message is one table, this system is one of its authors, and a notification is a type of message

**Status:** decided (from your answer) — opens the module README has listed as deferred since round 1, and starts
[`data-model/10` Messaging](../data-model/10-messaging.md).

**The answer, as given.** *"Let's call it messages, not notifications (notification is a type of message), but yes,
they are the same machinery and a message can be sent to a single person or an audience."*

**The rule.** There is one thing, and its word is **message**. A `message` row has exactly one author, and the
author is either a person (`author_person_id`) or this system acting on its own (`actor_label`, from the fixed
list — [D-125](round-17.md#d-125--an-empty-actor-column-is-this-system-acting-on-its-own-and-its-name-comes-from-a-fixed-list)).
**A notification is a message whose `message_type_id` is set**, and nothing more: the word names a kind of row,
not a table, not a module, and not a second mechanism beside the one a person uses to write to another person.

**Why one table, when an automated notice has nobody to ask.** The temptation is a `notification` table next to
`message`, on the argument that a safeguarding record should tell a system notice and a person's letter apart
without reading a column. It is refused twice over. Once by shape: this corpus has refused two tables of the
same shape before, in [D-100](round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape),
and the difference between these two tables would be exactly which table a row sits in. And once by substance:
what makes a notice attributable is already there — the actor label, and one audit row per write
([D-184](round-23.md#d-184--every-table-is-audited-and-the-delete-carve-out-names-the-moments-that-survive)) —
while a second table would need its own expiry rule, its own audit shape, and its own reader, and those three
would drift apart within two rounds the way four pages used to drift apart over one sentence about NULL
([`00-conventions §7a`](../data-model/00-conventions.md#7a-what-an-empty-actor-column-means)).

**What this changes.** Three tables, in a new
[`data-model/10-messaging.md`](../data-model/10-messaging.md): `message_type`, `message`, `message_recipient`.
[`README`](../README.md) loses "notifications" from its deferred list and gains the module's shape in the
paragraph that already draws communication's line. The [ERD inventory](../appendix/erd-b-inventory.md) gains
three entities. And the sentence in that same README paragraph — *"nothing in this design sends anything to
anybody today"* — is false from this round on and is rewritten by [D-214](#d-214--the-system-sends-and-d-164-is-narrowed-to-the-one-thing-it-was-protecting).

## D-207 — A message is addressed to one person or to a saved audience, and the recipient rows record an act and not a set

**Status:** decided (from the same answer) — gives the send its shape, and answers the half of
[D-110](round-13.md#d-110--the-expression-is-the-record-of-whom-a-grant-reached) that a reader could have carried
into messaging by mistake.

**The rule.** A `message` names exactly one of two targets: `target_person_id` **or** `audience_id`. Exactly one,
never both, never neither — the same discipline a `fee_obligation` keeps over its three possible targets.
At the save, an audience is resolved once by the resolver that already answers grants, and one
`message_recipient` row is written per person reached.

**What the rows are, and what they are not.** They are **the record of the act**: whom this message reached, on
which door, and whether it was opened. **Nothing resolves against them.** No audience expression may name a
message's recipients as a set, which is the whole reason this paragraph exists: an operand must be a named
registry row and never a stored set, and a table that starts as a log ends as a vocabulary the moment somebody
writes `PERSON(...)` over it. A grant's record of whom it reached stays the expression it holds (D-110); a
message's record is the rows, **because an audience can be edited tomorrow and the fact that thirty people were
addressed in March must not change with it.**

**A message is never edited.** A body written is a body kept; a wrong send is followed by a second message that
says what the first got wrong. This is [D-183](round-23.md#d-183--a-changed-ask-is-a-voided-request-and-a-new-symbol-and-amount_discount-goes)'s
rule about an ask, reused without ceremony, and it is what makes "nothing ages out"
([D-211](#d-211--nothing-about-a-message-ages-out-and-erasure-does-not-reach-messages)) survivable at all.

**The absence worth naming.** An audience that resolves to nobody writes no recipient rows, and the message row
still exists. That is not an error and there is no queue: it is the same shape as money that arrived under no
symbol ([D-180](round-23.md#d-180--there-is-no-queue-for-money-that-does-not-fit)) — the design records the act
and does not invent a waiting room for a result nobody claimed.

## D-208 — `message.send` is the only messaging code, and the audience a send names is not checked

**Status:** decided (from your answer) — registers messaging in
[catalog A](../appendix/permission-catalog-a-codes.md), and closes
[catalog B §12](../appendix/permission-catalog-b-roles-and-open-issues.md#12-open-issues)'s open half.

**The answer, as given.** *"One permission to write messages to anyone, call it message.send (it will be held by
the leadership or anyone the granter decides)."*

**The rule.** **`message.send`** is registered: one code, `applies_to = unit`, marked twice
for sensitivity, and it authorizes writing a message to one person or to an audience. **What the send names is
not checked.** There is no per-person test over an audience, no requirement that the writer could read the rows
of everyone addressed, and no rule that an event's organizers may address only their event. D-163's ceiling still
governs **who may hand the code out**, and one audit row records every send; that is the whole control, chosen
over the alternatives rather than left as an oversight.

**`message.send_direct` and `message.broadcast` were never codes.** They appear in
[catalog B §1](../appendix/permission-catalog-b-roles-and-open-issues.md) as names and in its §12 as an open
question about which scope `broadcast` should carry — and they appear **nowhere in catalog A's register**, which
is what a register is for. They retire as names. They are deliberately **not** entered in
[`removed-concepts.md`](../appendix/removed-concepts.md): the first column of that page is this corpus's dead-name
register, and a row there is a death certificate for something that lived. These two never did.

**Catalog B §12's open half closes with them.** Its question was whether `message.broadcast` should hold one
scope or two; there is no `broadcast` code to scope, and an audience narrows a send instead of a grant scope
doing it. [D-099](round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)
is untouched: one grant, one permission, one scope.

**This narrows [D-077](round-06.md#d-077--messaging-is-direct-by-default-broadcast-is-an-ordinary-scoped-permission-and-the-recipient-chooses-the-channel)
in the place its title is not about.** D-077's other half was that **messaging is direct by default and no
permission exists for it** — everyone could write one message to one person, and only reaching a crowd needed a
grant. From this round **one code gates every write**, a sentence to one person included, so *"direct by default"*
now describes the **shape** of a send — one target instead of an audience — and no longer a right. The corpus's own
rule runs in the new direction: [D-197](round-24.md#d-197--an-invoice-is-compulsory-so-nobody-issues-one-invoiceissue-is-deleted-and-the-asks-write-writes-it)
ruled that a permission nobody can decline is not a permission, and this code can be declined, which is what makes
it the control the answer asked for ("held by the leadership or anyone the granter decides").

**The cost, named in full, because the answer did not buy the route as well.** A person who holds no code has **no
way to write to the organization through this module** — not to a leader, not to a group, not about their own
child's membership. **This entry does not design a route for that person and does not claim one exists**, and it
does not soften the ruling by inventing an ungated exception beside the code the answer asked to be the only one.
What the account keeps is everything else in this design: a person's own rows are readable to their guardians
through the guardianship channel, and an erasure request is a person's act that never needed a messaging code,
because there is no messaging code in front of it.

**A job does not hold this code.** An automated message is written under an actor label
([D-212](#d-212--systemmessages-is-the-sixth-actor-label-and-the-renewal-sweep-stops-being-a-sender)), because a
permission gates a person's act and a job has none to gate.

## D-209 — A message type is a row, and the audience it reaches is configuration an admin edits

**Status:** decided (from two answers, the second correcting the first) — puts the reach of an automated message
where an installation can change it.

**The answers, as given.** *"Ok, not permissions, but in the system configuration, the admin selects an audience
for each event type"* — and, asked which word "type" belonged to: *"Each message type."*

**The rule.** `message_type` is a table: `code`, `name`, `description`, `audience_id`, `is_automated`,
`valid_from`, `valid_to`, `created_at`, `created_by`. **A type reaches the audience on its own row**, chosen from
the saved audiences [05a §8](../data-model/05a-audience-and-grammar.md) already documents. `is_automated` is true
exactly when a job may write the type, and `audience_id` is required exactly then — a human send carries its own
target on the message instead ([D-207](#d-207--a-message-is-addressed-to-one-person-or-to-a-saved-audience-and-the-recipient-rows-record-an-act-and-not-a-set)).
**A type is retired with `valid_to`, never deleted**, which is [D-109](round-13.md#d-109--nothing-a-rule-names-is-deleted-deprecated-hidden-disabled--and-a-tab-instead-of-a-report)
saying what it says about anything a row may point at.

**This is `membership_type` again, and saying so is the point.** [D-186](round-23.md#d-186--membership_type-is-settings-wearing-a-vocabularys-clothes)
found a table that looked like a vocabulary and was really a settings panel with a vocabulary's clothes. A
message type is the same animal: the *code* is the vocabulary (`renewal-window-opened`, `fee-overdue`,
`registration-confirmed`), the *audience* is a setting, and what an organization changes on a Tuesday afternoon
is the second and not the first.

**What the two wordings disagreed about, and what was not inferred from them.** An event type is not what holds
an audience here. The first answer named one; the follow-up named the message; the message wins because it is
the row that fires. Whether an event type should propose a default audience that a per-event send may narrow is
a real question and is filed as [K-13](../open-questions.md#k-13) rather than drawn in from the first wording —
[D-204](round-24.md#d-204--custody_arrangement-is-deleted-a-court-order-is-stored-here-neither-as-prose-nor-as-structure)
is the reason this round refuses to do that: an entry that widens an answer while writing it down becomes a false
claim about a table.

**Who may edit a type is not settled here.** Every write in this design is gated by a code, and no code for this
table is proposed, because a vocabulary table's editing has been refused a code before
([D-152](round-21.md#d-152--zero-is_system-columns-what-protects-a-vocabulary-is-its-table-not-a-flag-on-its-rows)).
The working default is whoever holds `system.admin` at the unit, and the question of whether that is right is
[K-12](../open-questions.md#k-12).

## D-210 — A report is a delivered message, so all five report codes are deleted and reporting stops being a name

**Status:** decided (from your answers) — deletes two shipped codes and three deferred ones, and rewrites every
sentence in this corpus that ends with somebody opening a list.

**The answers, as given.** *"Report is a system message delivered through a notification."* Asked whether a report
still has a screen a person opens: *"Only a delivery message, depending on a type delivered to people with
specific permission."* Asked what happens to `report.view`: *"Both die."*

**The rule.** **There is no report screen in this design.** What an organization calls a report is a message of a
type, addressed to an audience, delivered by the machinery in [D-206](#d-206--a-message-is-one-table-this-system-is-one-of-its-authors-and-a-notification-is-a-type-of-message).
**Five codes go, not four.** **`report.view` and `report.export` lose their rows in catalog A**, and
**`report.finance.view`, `report.membership.view` and `report.safeguarding.view` lose their rows among the deferred
namespaces** — the deferral of a finance report was
[D-195](round-24.md#d-195--the-money-codes-are-shipped-codes-catalog-a-grows-a-money-section-and-catalog-b-10-loses-three-rows)'s
deliberate choice one round ago, and a code that would gate a screen is not worth deferring once there is no such
screen. **This entry's first draft named four and missed `report.membership.view`,** which catalog B §10 had carried
beside the other two and which the `leaders` office named as its one report row; a namespace dies by its whole list,
so the miss changed nothing about the ruling and everything about this page's accuracy, and the code now has its own
row in [the dead-name register](../appendix/removed-concepts.md). **The `report.*` namespace stops existing.**
Reporting is not a permission, not a module, and not a deferred item: it is an audience and a type.

**What the deleted codes' absence is filled with.** **Twenty-five lines across seven pages** named one of these
codes at the commit this round starts from, forty occurrences because several lines name two of them:
seven in [catalog A](../appendix/permission-catalog-a-codes.md), nine in
[catalog B](../appendix/permission-catalog-b-roles-and-open-issues.md), three in
[`07-finance`](../data-model/07-finance.md), two in [`domain/06`](../domain/06-authorization-model.md), and one each
in [`05d`](../data-model/05d-invariants-and-seed.md), [`05e`](../data-model/05e-keys-and-callers.md) and
[the open register](../open-questions.md). **Counted by program, and the count is this entry's own correction:**
the first draft said seventeen lines across ten pages and listed
[`03-membership`](../data-model/03-membership.md), [`09-attributes`](../data-model/09-attributes.md) and
[`domain/05`](../domain/05-membership-lifecycle.md) among them, and none of those three pages ever named one of the
five codes — their `report` sentences are sense 3 below, which survives. Most of the twenty-five sentences were
written to be
honest about a hole — they are the corpus admitting that a rule needs a human to notice something. **None of them
becomes "nobody notices".** Each becomes one of two things, and which one is decided sentence by sentence in the
sweep, not by a rule here:

- **a type and an audience.** The over/under payment notice ([`07-finance §2b`](../data-model/07-finance.md#2b-money-that-cannot-be-matched))
  and the overdue notice ([`07-finance §3`](../data-model/07-finance.md#3-keeping-membershipoutstanding_balance-honest))
  are exactly the two cases this round was asked about, and both now reach people instead of waiting for them.
- **an honest absence.** Where a sentence said *a person with `report.view` opens the list* and no type is
  configured, the sentence now says the thing plainly: nobody computes it, and the design is not waiting for
  somebody who might.

**Three things this corpus calls a report, and only one of them changes meaning.**

1. **A report as a permission — deleted.** `report.view` and `report.export` authorized a screen, and there is no
   screen. This is what the answer was about.
2. **A report as something delivered — the new sense.** "Report is a system message delivered through a
   notification" is the answer's own sentence, and in that sense a report is a `message` of a type addressed to an
   audience. [D-126](round-17.md#d-126--break-glass-is-a-report-and-a-written-procedure-not-a-mechanism)'s
   break-glass *report* fits this sense better than it ever fitted the old one: the decision always wanted whoever
   can act to be reached, and had no machinery to reach them.
3. **A report as a listing nobody receives — this keeps its wording, and the reason is that three decision titles
   are built on it.** *"The gate and the report are the control"* is [D-071](round-05.md#d-071--nothing-forces-a-role-assignment-to-end-the-gate-and-the-report-are-the-control)'s
   title, *"a key outlives whoever installed it and the report is the control"* is
   [D-120](round-16.md#d-120--a-key-outlives-whoever-created-it-and-the-report-is-the-control)'s, and D-126's title is
   built the same way. **Twenty-nine live lines echo them**, and the two halves do not overlap: seventeen carry one
   of "no report will ever show it", "the report of long-lived open grants", "a report over a date", and twelve say
   *the report is the control* — and each means *a check exists, somebody runs it, nothing delivers it*. **Rewriting that idiom would misquote a title that has an anchor, and an anchor moved is a
   citation lost**, so the idiom stands where it is. **What is forbidden from this round is the other two senses
   being confused:** no sentence may promise that a listing reaches anybody, and no page may name a `report.*`
   code, because there is no code and no screen.

**Where a page had to be precise, the register was the place, so the register changed its word.**
[The invariant register](../data-model/00a-invariant-register.md) headed its right-hand column **Report** and its
prose said "a report over the state they would breach"; that column lists numbered checks, so it is now headed
**Backstop** — the word the page already used for it in its own reading instructions — and the page states that
nothing in the column changed but its name. **A canonical page a resolver of citations reads is worth one rename;
twenty-nine echoes of a quoted title are not.**

**What this costs, said where it bites.** There is now no screen anywhere in this design that shows an
organization-wide list. [`05d §12`](../data-model/05d-invariants-and-seed.md#12-what-day-one-looks-like) used to
state that exactly two reporting codes exist, and that sentence is gone. And `report.export` was the one moment
this design had data leaving it by intention; with it gone,
[D-199](round-24.md#d-199--nothing-leaves-this-system-to-an-accounting-system-and-an-external-one-is-a-later-versions-design)'s
"nothing leaves" gets stronger, not weaker — a person who wants data out now has to read it.

## D-211 — Nothing about a message ages out, and erasure does not reach messages

**Status:** decided (from two answers) — the third kept-forever posture in this design, and stated with the
argument against it rather than without it.

**The answers, as given.** Asked which of the body, the address, and the read moment expires: *"Nothing ages
out."* Asked what erasure reaches: *"Erasure does not reach messages."*

**The rule.** A `message` row, its body, its `message_recipient` rows, and their `read_at` are never scheduled
away and never emptied by an erasure. This sits beside the accounting skeleton, which
[D-088](round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short) keeps indefinitely,
and against two clocks that do run: audit payloads empty at 24 months (D-088) and `access_log` rows are **deleted**
at 24 months ([D-145](round-20.md#d-145--access_log-rows-are-deleted-at-24-months-and-the-job-that-does-it-has-a-name)).
**A message is the first body of text in this design that is written to be kept and is then kept.**

**The argument against it, recorded because it was available and was declined.** [D-191](round-23.md#d-191--personnotes-is-deleted-and-the-vocabulary-takes-the-job)
deleted `person.notes` on the ground that free text about a person, sitting outside the vocabulary and outside
erasure, made erasure a lie. The same argument is standing in this room: a message body is free text about a
person, it is written by the organization rather than curated, and it now survives the one act a person can
demand. **That argument was put and refused.** The answer's own weight is that a message is correspondence — an
act that happened on a date — and an act this organization performed is not something it deletes on request.
[`06b §4`](../data-model/06b-redaction-and-checks.md#4-redaction-log) names what erasure empties and says that
messages are outside that list **by decision, with this paragraph as the reason**, and
[`00-conventions §8`](../data-model/00-conventions.md#8-personal-data-and-erasure) carries the same sentence in
the section that lists the erasure's reach.

**The consequence, not softened.** An erasure removes the person and leaves every message addressed to them: the
recipient row points at a tombstone, and its body keeps saying what the organization told that person, and when,
and on which door. [`01b`](../data-model/01b-merges-views-and-checks.md) is where a person's row survives as a
tombstone, and that is what makes this survivable rather than broken — nothing dangles; it points somewhere
quiet.

## D-212 — `system:messages` is the sixth actor label, and the renewal sweep stops being a sender

**Status:** decided (from your answer) —
[`00-conventions §7a`](../data-model/00-conventions.md#7a-what-an-empty-actor-column-means) goes from five rows
to six, for the first time since round 17 fixed the list.

**The answer, as given.** *"One new label: `system:messages`."*

**The rule.** **`system:messages`** joins the fixed list, and it is the author of every automated message.
**`system:renewal-sweep` stops being a sender**: it expires memberships, which is what it has always done, and the
renewal notice is a message whose author is the messaging label. One label per kind of act, so that adding a type
to configuration never adds a label to a vocabulary. The run writes **one audit row** for itself
([D-184](round-23.md#d-184--every-table-is-audited-and-the-delete-carve-out-names-the-moments-that-survive)),
as every table the application writes owes.

**The count moves, and a count that moves has to be swept.** Five labels were the settled number:
[D-199](round-24.md#d-199--nothing-leaves-this-system-to-an-accounting-system-and-an-external-one-is-a-later-versions-design)
wrote it in as a refusal of a sixth for accounting, and
[`05e`](../data-model/05e-keys-and-callers.md) says it twice in prose. **D-199's refusal stands untouched** — the
rejected label was an accounting one, and there is still no accounting label and no export — but its sentence
about the size of the list is narrowed here, and its row in [the index](index.md) says so. History pages keep
their wording; that is what makes them history, and it is why [D-145](round-20.md#d-145--access_log-rows-are-deleted-at-24-months-and-the-job-that-does-it-has-a-name)'s
label count in [round 20](round-20.md) does not get edited either.

**What still has no answer.** Which clock fires which automated type — nightly, hourly, or at the moment a row
crosses a date — is not ruled here, and the renewal window's own arithmetic
([D-048](round-04.md#d-048--the-renewal-window-is-60-days-and-is-a-configuration-parameter)) was deliberately date-driven rather than
job-driven. It is [K-14](../open-questions.md#k-14).

## D-213 — The account chooses its own doors, a child's message mirrors as its own rows, and only e-mail lands today

**Status:** decided (from your answers) — completes [D-077](round-06.md#d-077--messaging-is-direct-by-default-broadcast-is-an-ordinary-scoped-permission-and-the-recipient-chooses-the-channel)'s
"the recipient chooses the channel", and turns
[D-082](round-07-08.md#d-082--a-direct-message-to-a-minor-is-mirrored-to-the-minors-guardians) into a rule about rows.

**The answers, as given.** *"They can decide to read it only within the system or enable external delivery via
email, push notifications or (possibly) SMS."* And, on who decides for a child: *"The account opts in; guardians
get their own."*

**The rule.** The choice belongs to the account: **`account.opt_in_email`**, boolean, required, default **false**.
**The inbox is not a door and cannot be turned off** — a `message_recipient` row with `channel = inbox` is the
record that a message exists for you, and a design where that can be declined is a design where "you were
addressed" has no evidence. **A door arrives with its column on the day its transport exists.** E-mail has one,
because [`person_contact`](../data-model/01a-accounts-and-contacts.md#6-person_contact) already carries a verified
`email` value. Push has nowhere to live: a device token is not a contact point — a person holds many, they expire
silently, and `contact_type`'s values (`email`, `phone`, `postal`, `website`, `messaging`) all describe something
that survives its device. SMS would land on the `phone` row and has no transport. **No column is written for a
thing this design cannot do**, which is the same lesson
[D-192](round-23.md#d-192--proposed_by-loses-import_job-because-a-vocabulary-value-is-a-claim-about-who-can-write)
drew from an enum value that claimed a kind of actor existed. Where push lives is [K-15](../open-questions.md#k-15).

**Mirroring, as rows.** A message addressed to a minor is mirrored to that minor's guardians as **their own
recipient rows, on their own chosen doors**. Guardianship is already the channel that says who that is — it
carries a `right_level` and needs no selector ([D-113](round-13.md#d-113--the-guardianship-channel-has-no-expression-guardians-is-not-a-selector))
— so D-082 gains no table and no age branch in the resolver. It gains a physical form: **the mirror is rows, and
a row is why "the sender is told it will be" is now an ordinary in-app statement at the write rather than a
message about a message.**

**The question mirroring opens, filed rather than answered.** A message addressed to an **audience** may contain
minors by the hundred, and every one of them mirrors to their guardians on this rule. Whether an
audience-addressed message mirrors at all — or only a message addressed to one named child does — decides whether
a class-wide announcement generates a thousand rows and whether a guardian can see that their child was on a list
they were not told about. It is [K-11](../open-questions.md#k-11).

## D-214 — The system sends, and D-164 is narrowed to the one thing it was protecting

**Status:** decided (from your answer) — narrows
[D-164](round-22.md#d-164--nobody-is-told-and-no-page-may-say-otherwise), which is rewritten nowhere and re-read
everywhere.

**The answer, as given.** Asked how much of D-164 survives: *"Narrow it, keep the deadline rule."*

**The rule.** **The system sends, and a send is a named act.** A person's send is gated by `message.send`; a
job's send is authored by `system:messages`; the rows themselves record who was addressed, on which door, and
whether it was opened; and one audit row answers for the write. **What stays forbidden is a page inventing a
period nobody chose.** *"Told within 14 days"* may be written only if a row holds the 14 and a named decision
chose it — that was D-164's real work, disguised as a rule about verbs, and it is untouched.

**What moves.** **Twenty-nine lines across nineteen pages**, outside this folder, assert that nothing is sent or
that nobody is told — counted with the vocabulary of [D-164](round-22.md#d-164--nobody-is-told-and-no-page-may-say-otherwise)
itself, and listed in the sweep's brief rather than here, because a count I cannot re-run is a count that goes stale
silently. Each is now either true in a narrower sense or false. The false ones are rewritten where they are, in the
tense they are in:
[`README`](../README.md)'s *"nothing in this design sends anything to anybody today"*,
[`04-relationships`](../data-model/04-relationships.md)'s *"Nothing notifies anybody"*,
[`05d`](../data-model/05d-invariants-and-seed.md)'s *"sends nothing"*,
[`07-finance`](../data-model/07-finance.md)'s two,
[`domain/02`](../domain/02-actors.md)'s *"no message is sent"*,
and the register's own. **Two of them were written today by [round 24](round-24.md) itself, in
[`07-finance`](../data-model/07-finance.md)**, in the commit that obeyed this rule across the whole corpus — and
the follow-up sweep committed hours later read that page again and left both sentences standing, correctly, because
under the rule that still stood they were correct. That is recorded here rather than quieted: it is what ruling in
the present tense costs when the ruling moves, and it is why every page this round touches cites the decision
rather than its own memory of the rule.

**What survives intact.** [D-137](round-20.md#d-137--a-guardian-may-appoint-a-guardian-and-nobody-at-the-organization-is-told)
stands: a guardian appointing a guardian tells nobody, because no type reaches anybody for that event and nobody
has configured one — which is now the *reason* rather than the *rule*. **D-126's named break-glass person
stands**, for the reason round 22 already gave: a procedure needs a name, and a notification does not. And
[D-146](round-20.md#d-146--an-outbound-call-is-a-persons-act-or-a-job-and-nothing-about-it-is-designed-yet) is
still unanswered about everything except messages — an outbound call to another system is not a message and is
still undesigned.

## D-215 — The three `notes` columns stay, and erasure empties them

**Status:** decided (from your answer) — closes the loose end that
[D-191](round-23.md#d-191--personnotes-is-deleted-and-the-vocabulary-takes-the-job) left one table away from
itself.

**The answer, as given.** *"Keep, add to erasure."*

**The rule.** `membership.notes`, `membership_request.notes` and `payment.notes` stay exactly where they are —
free text beside the row, where the work happens. **Erasure empties all three**, the way
[D-140](round-20.md#d-140--nothing-about-an-event-is-deleted-on-a-schedule-and-erasure-empties-an-answer-without-deleting-it)
empties an event answer rather than the way a redaction overwrites a name: the row survives, the text goes.
They join the list in [`06b §4`](../data-model/06b-redaction-and-checks.md#4-redaction-log) and the reach sentence in
[`00-conventions §8`](../data-model/00-conventions.md#8-personal-data-and-erasure).

**What this does not widen, and why that is stated.** Free text about a person exists in more places than these
three columns, and [`06b`](../data-model/06b-redaction-and-checks.md) says so about the others by name: a roster
row's `note`, an account's `status_reason` and `status_note`, and the two values a `field_conflict` holds when a
merge could not choose between them. **The answer given was about three columns and this entry rules on three
columns.** Whether the others join them is [K-16](../open-questions.md#k-16) — a question, not a footnote, because
round 24 learned the hard way that an entry which quietly generalizes an answer becomes a false claim about a
table two sections away.

## D-216 — Every worked example names the office `treasurer`, and what the operand reads is still unstated

**Status:** decided (from your answer) — repairs fourteen sites, and files the thing the answer did not settle.

**The answer, as given.** *"Rename every example to `treasurer`."*

**The rule.** Fourteen places write `ROLE(treasurers)` — including the worked audience that opens
[`05a`](../data-model/05a-audience-and-grammar.md), which is the sentence a newcomer reads first. Every one of
them now names **`treasurer`**, the office [catalog B §11](../appendix/permission-catalog-b-roles-and-open-issues.md)
writes out and [the glossary](../glossary.md) defines as held for the unit. An example that names a different
office from the worked one is not a second example; it reads as a typo in a language that has fourteen
occurrences and no compiler.

**What the answer did not rule, kept as a question rather than a guess.** Renaming the examples says nothing about
what `ROLE(x)` resolves against — `role.code` or `role.name`. Nothing in this corpus states it, and both readings
are consistent with everything written down: the operand's argument type names the `role` table, not a column of
it. It is [K-17](../open-questions.md#k-17), and it is not cosmetic — under one reading a rename silently changes
whom an old expression picks out, which is the cost [D-201](round-24.md#d-201--a-group-keeps-no-previous-name-this-is-now-a-ruling-and-not-an-absence)
already made payable for a group's name.

---

## What this round adds to the register, and why an empty register was not a finished design

Seven rows, all filed by this round and none of them a question round 24 answered:
[K-11](../open-questions.md#k-11) does an audience-addressed message mirror to guardians ·
[K-12](../open-questions.md#k-12) what gates editing a message type ·
[K-13](../open-questions.md#k-13) whether an event type proposes a default audience ·
[K-14](../open-questions.md#k-14) which clock fires each automated type ·
[K-15](../open-questions.md#k-15) where a push token lives ·
[K-16](../open-questions.md#k-16) whether the other free-text columns join erasure ·
[K-17](../open-questions.md#k-17) what `ROLE(x)` resolves against.

**Seven, of which one is not about messaging.** [K-17](../open-questions.md#k-17) rode in on the spelling fix and
[**K-16**](../open-questions.md#k-16) on the `notes` columns; a round that clears the register would have caught
both instead of carrying them, and it did not, so they are rows now.
**K-12 and K-16** both concern who may write something and were filed apart on purpose: one is about a vocabulary
table and one is about a person's text, and folding them together would let either answer be borrowed by the wrong
one.

**The number stated, because a number beside a sentence is what goes stale silently.** The register leaves round
24 at zero live questions and leaves this round at **seven**: [A-4's remainder](../open-questions.md#a-4-remainder--the-organizational-calendar)
and [F-11](../open-questions.md#f-11--does-the-identity-reviewer-need-to-read-the-person-record-to-settle-a-claim)
stay resolved rows in § R, K-10 stays closed, and `message.send`'s registration
([D-208](#d-208--messagesend-is-the-only-messaging-code-and-the-audience-a-send-names-is-not-checked)) closes
the question round 24 had answered with a section of its own.

## What the sweep found that this round did not plan

**Four things, none of them a ruling, all of them cheaper said here than left in the pages.**

1. **A namespace dies by its whole list, and this entry's list was one short.**
   [`report.membership.view` is now a row in the dead-name
   register](../appendix/removed-concepts.md), where it had no death certificate at all:
   [D-210](#d-210--a-report-is-a-delivered-message-so-all-five-report-codes-are-deleted-and-reporting-stops-being-a-name)
   enumerated four codes, catalog B §10 had carried three deferred ones, and the fifth name therefore appeared
   nowhere in the corpus — a code deleted by a ruling and remembered by no page, which is the one state a dead
   name should never be in. **The rule this teaches is not about reports:** when an entry says a namespace or an
   enum or a list goes, the entry has to carry every member, because the sweep works from the entry and not from
   the registry.
2. **Two of this round's own counts were wrong, and the program that settled them is the same one that settles
   every other count here.**
   [D-210](#d-210--a-report-is-a-delivered-message-so-all-five-report-codes-are-deleted-and-reporting-stops-being-a-name)
   now states twenty-five lines across seven pages rather than seventeen across ten, and twenty-nine echo lines
   rather than "around fifteen"; three pages it had listed among the sites never named one of the five codes,
   because their `report` sentences are the third sense, which survives. **A count written beside a sentence is
   the number that goes stale silently, and the only repair is to measure before typing.**
3. **Two links crossed a directory without `../`,** one from [the ERD inventory](../appendix/erd-b-inventory.md)
   into [`06b §4`](../data-model/06b-redaction-and-checks.md#4-redaction-log) and one from
   [`05d §12`](../data-model/05d-invariants-and-seed.md#12-what-day-one-looks-like) into
   [catalog B §12](../appendix/permission-catalog-b-roles-and-open-issues.md#12-open-issues). Both pointed at a
   section that exists and a file that does not, which is the failure a build without `--strict` reports as a
   line nobody reads; the dead-anchor script named both. **A link that resolves inside its own directory is not
   a link that resolves.**
4. **Two pages still called the `access_log` delete "the third" hard-delete exception** —
   [`00a`'s shape-3 table](../data-model/00a-invariant-register.md) and the
   [ERD inventory](../appendix/erd-b-inventory.md) — although
   [the page that owns that list](../data-model/00-conventions.md#4-deletion-policy) has named **two** since round 23 deleted
   the deletion policy's first exception along with the import pipeline
   ([D-190](round-23.md#d-190--the-legacy-import-is-a-script-and-a-key-and-the-pipeline-is-gone)). **A round-23
   tail, caught a full round late:** the ordinal lives in sentences two directories away from the list, and
   nothing that gates a round reads a sentence.

**One false alarm worth recording, because it was believed for a minute.** A sweep handback reported that
[`domain/03 §7`](../domain/03-identity-and-legacy.md#7-legacy-import-pipeline) still described the deleted import
pipeline as a mechanism across five passages. It does not: the section opens "**There is no pipeline**", names
everything that was deleted, and states that **the heading and the section number stay** because pages cite §7 by
number. **A grep that finds the words of a deleted thing is not a finding until somebody reads the sentence that
puts them in the past tense.**

[← Refinement round 24 (D-193 … D-205)](round-24.md) | [All decisions](index.md)
