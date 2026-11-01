# Decision Log — Refinement round 23 (D-171 … D-192)

> Nine sittings, twenty-two decisions, and the shape of three of the answers changed while they were being given. `person.gender` turned out to be a column about grammar rather than a column about reporting, which falsified the assumption the register had carried since round 1 and gave the value set a reason to exist; "an invoice can be requested by the payee" turned out to mean the payer, which is the difference between a document the organization issues to itself and one a family asks for; and a question about sibling discounts came back as a requirement to select payment requests and change their amounts, which is a different decision and a larger one. **This round also deletes the legacy import pipeline**, which is the largest thing removed since the unit hierarchy and which arrived as a subordinate clause: *"one script and one key, you can remove all the machinery around."*
>
> **One of the questions asked again what round 20 had already answered.** [F-27](../open-questions.md#f-27), whether this system ever calls outward, was settled by [D-146](round-20.md#d-146--an-outbound-call-is-a-persons-act-or-a-job-and-nothing-about-it-is-designed-yet) — an outbound call is a person's act or this system's job, and nothing about it is designed yet. The answer it got this time ("there MAY be external services added in future versions, but no specifics for now") is the same answer. It is recorded here rather than quietly dropped because the question was asked *sharper* than round 20 left it, and the sharper form is worth having on the record; the register's row is closed against D-146 and no new decision is minted for it.

[Refinement round 22 (D-155 … D-170 ←)](round-22.md) | [All decisions](index.md)

**Where the questions came from.** **All nine** of the questions
[round 22](round-22.md) filed as [§ K of the register](../open-questions.md#k-filed-by-a-module-page) — the repair
for a module page that had kept its open issues where no register could see them. **Three** of the survivors at the
top of that register: [`E-3`](../open-questions.md#e-3--guardian-acting-for-an-adult-child),
[`F-9`](../open-questions.md#f-9--should-membership_type-stay-a-table-with-one-row) and
[`F-34`](../open-questions.md#f-34); [`F-11`](../open-questions.md#f-11--does-the-identity-reviewer-need-to-read-the-person-record-to-settle-a-claim)
was deliberately **not** asked, on its own recommendation, and stays open.
**Four** items out of [`07-finance` §5](../data-model/07-finance.md#5-open-issues--the-whole-of-this-document-essentially):
its discount item, its invoice item, its variable-symbol item, and its accounting-direction item, which is also
[`F-27`](../open-questions.md#f-27). **And four holes that opened while the answers were being written:** what
happens to a required column at an erasure ([D-175](#d-175--an-erased-persons-grammatical-form-goes-with-their-names)),
who is the actor when a variable symbol resolves itself ([D-182](#d-182--matching-money-is-a-code-of-its-own-and-the-automatic-half-is-systembank-pulls)),
what a ceiling reads when a right can be widened without writing one ([D-188](#d-188--the-ceiling-reads-a-grant-and-nothing-else-and-what-it-leaves-open-is-written-down)),
and what "change the amount" means in a module that prints QR codes
([D-183](#d-183--a-changed-ask-is-a-voided-request-and-a-new-symbol-and-amount_discount-goes)).

**What was checked before asking, and once was not.** Every question here was grepped for a prior answer first,
and the one above still got through: `F-27`'s row is on a page of this register titled *answered*, in a column
that says the caller is designed and the wire is not, and the register's own API row cites D-146 in the sentence
about calls going out. **A question surviving on a register is not proof that it is open** — it is proof that
nobody deleted the row.

---

## D-171 — A member row has to meet its group, and the resolver trims it to the group's life

**Status:** decided (from your answer) — rules the question [`02` §8](../data-model/02-organization.md#8-open-issues)
called "assumed in §2, reported in §6 check 2, and nowhere ruled", and replaces the
[register's row](../data-model/00a-invariant-register.md#3-the-answer-reads-another-table-a-resolver-or-a-graph)
whose save-time check read *none — containment is assumed*.

**The rule.** A row in `person_group_member` need **not** lie inside its group's period. It must **meet** it: the
two periods must have a non-empty intersection, and a member row that cannot overlap its group at all is refused at
the save. During a permission check the membership contributes only the part of itself that falls inside the
group's lifetime — the resolver reads the intersection, not the member row's own span.

**Read as given, and the one word that needed deciding.** The answer came as *"if it at least intersects with
max(start, now) : min(end, now)"*. The `min`/`max` pair is the intersection of two intervals, and this writes it as
the intersection of the **two periods**; `now` is read as *the date a check runs on*, which is the date
[`OLDER(n)` and `YOUNGER(n)` already read on](round-10b.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree)'s
sibling rule, and not a fourth bound in the constraint. So the save-time test is between `person_group.valid_from` /
`valid_to` and the member row's own two columns, with an absent `valid_to` on either side read as open, and a future
membership of a group that still exists passes it. **If `now` was meant inside the constraint rather than inside the
resolver, say so and this entry moves** — the difference is whether a membership can be written today for a group
that ended last spring, which under this reading it cannot, because the periods do not meet.

**Why trimming rather than refusing containment, which is the interesting half.** Containment would have been the
obvious rule and it is the wrong one. A group's period is a fact about a body; a member row's period is a fact about
a person's belonging to it, and the two are dated by different people at different moments — a roster corrected in
2026, a group whose `valid_to` is set by whoever closes it. Refusing to hold a row whose ends disagree would make
ordinary bookkeeping impossible and would force whoever hit it to *invent an earlier date* to get the write through,
which is data corruption as a side effect of a validation rule. What matters is not that the two intervals agree but
that **nobody gains a right from a period the group does not have**, and trimming the interval at resolution
guarantees exactly that without touching the stored facts. It is the same shape the corpus already uses for a
membership whose group has ended: [setting `valid_to` is refused while a live grant names the group](../data-model/02-organization.md#1-person_group),
so the group cannot stop covering a right it is holding; this is the other direction, where the person's row runs on
and the group's does not.

**What it costs the page that reports it.** [`02` §6 check 2](../data-model/02-organization.md#6-integrity-checks)
was written to catch rows outside their group's period — a report standing under an assumption. Its subject is now
the narrower and real one: a member row meeting no part of its group's period at all, which is not untidy bookkeeping
but a row that says nothing and cannot be repaired by reading either end. The register's row stops reading as an
omission, and the report becomes the net under a rule instead of the whole of one.

**Cost, stated.** The resolver now reads a second table's period on the path where it decides anything about a
group's members, which is one more join per check and one more thing that must be inside any
[compilation](round-21.md#d-151--creating-an-event-writes-the-events-authority-and-its-organizers-may-grant-on-it)'s
reach rather than smuggled in beside it. It also means a group's dates can *silently shorten* a membership's effect:
a person with a row running to June in a group closed in March stops being reachable through that group in March,
and no report says so, because nothing sends anything to anybody ([D-164](round-22.md#d-164--nobody-is-told-and-no-page-may-say-otherwise)).

---

## D-172 — An ended group is in no picker and comes back never

**Status:** decided (from your answer) — closes the second
[§ K question](../open-questions.md#k-filed-by-a-module-page) and the
[`02` §8](../data-model/02-organization.md#8-open-issues) bullet that called the two halves one question.

**The rule.** A group whose `valid_to` is set is not offered by a picker. It is not offered by a picker *because*
it may never be reopened: `valid_to` is set by a person and is not cleared. A name that comes back is a new group,
which is [§1's rule](../data-model/02-organization.md#1-person_group) and stays the only rule about a returning
name. An ended group stays reachable as history — its member rows still answer the question
[D-098](round-10a.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority)
built them for — and reachable by search, which is not a picker.

**Why the two halves really were one.** The page noticed the collision by itself: reopening a group by clearing
`valid_to` would put two rules over the same name, "a returning name is a new group" and "sometimes it is the old
one", and the difference between them would be a judgement nobody recorded. Refusing to reopen is the only answer
that keeps the naming rule singular, and it is the answer the picker question wanted anyway — a list of live groups
is a list of groups that can be written to.

**What this silently decides, since it is worth saying out loud.** A troop that sleeps for a year and restarts is a
new row, and its old roster does not come with it: the new group's first roster is empty and someone writes it
again. Continuity between the two rows is not recorded either, which is [D-173](#d-173--that-two-groups-are-the-same-group-is-said-not-stored)
and was asked in the same sitting. So "the same troop, 1998" is now true of nothing in the database, deliberately,
in two directions.

---

## D-173 — That two groups are the same group is said, not stored

**Status:** decided (from your answer) — closes the third
[§ K question](../open-questions.md#k-filed-by-a-module-page), and ends the last trace of
[D-096](round-09.md#d-096--a-reused-unit-number-is-a-new-unit-unless-someone-records-the-continuity)'s
continuity rule, whose subject [D-097](round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)
removed.

**The rule.** Nothing records that a group continues another. There is no self-reference on `person_group`, no
carried number, and no edge: [D-098's refusal of group-to-group edges](round-10a.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority)
stands, and the words "the same troop, 1998" live outside the database. This is written as a choice, in the page
that held the question, rather than left as the silence of a table that has no column for it.

**Why the question existed at all, and why it is cheap to close.** The corpus used to have exactly one continuity
rule and it belonged to units: a reused number is a new unit *unless someone records the continuity*. When units
became a scope rather than a row, the rule lost the thing it was about and its shape stayed behind, so `02` §8
asked where an assertion would be held and the honest answer was *nowhere, and no decision ever said that was the
intention*. Saying it is the whole of this entry.

**What is refused, and the cost of each.** A self-reference on `person_group` reopens a refusal that was made for
good reasons — a graph of groups is a hierarchy arriving by the back door, and the corpus deleted a hierarchy once
already. A carried number revives the identifier D-096 needed units to have, and a group's `name` is already unique
across [`person_group`, `role` and `audience` together](../data-model/02-organization.md#1-person_group), which is
one namespace more than a number would fit into. The cost of refusing both is real but bounded: a search for a group
that no longer exists does not find its successor, and the person who wants the whole story of a troop reads two
rosters. That is a job for the words on the page, which is where the corpus puts everything it has refused to
build.

---

## D-174 — `person.gender` is how the system declines a verb, and it is required

**Status:** decided (from your answer) — closes the fourth
[§ K question](../open-questions.md#k-filed-by-a-module-page), deletes one value from the set, and
**falsifies assumption 15** of
[the register's assumption index](../open-questions.md#i-assumption-index), which had this column's
justification as "needed for reporting" since the first round.

**The rule.** The column exists so that the system can address a person in a language that asks for it: Czech
inflects a past tense and an adjective for the sex of the person it talks about, so *"your registration was
accepted"* has more than one form and the system has to pick one. Its value set is `male`, `female`, `other`.
**`unknown` is deleted** — it is not a grammatical form, and a value that cannot be declined toward is not an answer
to the question this column asks. The column is **required**, and it holds nothing else: it is not a category for
reporting, no report groups on it, and no page may justify it by a report again.

**Why the falsification matters more than the value set.** Assumption 15 was not wrong about the column existing;
it was wrong about *why*, and the wrong reason was load-bearing in a way the right one is not. "Needed for
reporting" is a justification that has to survive a legal review, a data-minimisation argument, and every year in
which nobody publishes the number — and [`00-conventions §8`'s own non-collection rule](../data-model/00-conventions.md#8-personal-data-and-erasure)
is written to defeat exactly that kind of justification, saying *do not collect what you cannot justify*. "The
sentence will otherwise be wrong in the mouth of the system" is a different claim: it is about every sentence the
system says, and it is falsifiable the next morning by anyone who reads one. This is the second time in two rounds
that a column's recorded reason turned out not to be its reason — [`07-finance` §5](../data-model/07-finance.md#5-open-issues--the-whole-of-this-document-essentially)
asserted a currency question it had already answered in koruna, and closed as
[D-155](round-22.md#d-155--the-currency-is-koruna-and-the-modules-own-money-path-said-so).

**Why it stays one of the three exceptions, and does not move into the vocabulary.** [D-083](round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)'s
formula — everything about a person other than a name, a gender and an age is one class of data — is quoted in
about ten pages, and the wording survives this ruling unchanged. That is not inertia: the column has to be readable
by anything that renders a sentence about a person, which is the least privileged path in the design and cannot
issue a [`person.view`](../appendix/permission-catalog-a-codes.md) check to decline a verb with, and an attribute
value in a vocabulary the organization edits at runtime cannot be required to exist. A required value that any
screen might need in order to be grammatical is a column. The round-22 option of pushing it into the attribute
vocabulary was the right instinct for a reporting category and the wrong one for this.

**Required, and what that costs the two paths that write a person.** An import and a merge are the two writers that
do not have the person in front of them. The script ([D-190](#d-190--the-legacy-import-is-a-script-and-a-key-and-the-pipeline-is-gone))
that cannot derive the value from its source has to supply one, which for the historical corpus means the value is
the organization's inference rather than its record — the same posture
[D-093](round-09.md#d-093--the-one-off-import-may-create-memberships-both-ends-dated)
already takes toward an inferred period: write it, mark the row's confidence low, do not pretend the source said it.
A merge has it easier: both candidate rows carry a required value, and two required values that disagree are
already what [`field_conflict`](../appendix/erd-b-inventory.md) exists to hold.

**Reading, not ruling:** *"other" is doing two jobs and one page should say which.* It is the third grammatical
option and, for anybody who did not choose it, the absence of a choice the system is allowed to make for them; the
row that explains the value set should say in one sentence that it is a form of address, not a category of person,
because the same ten pages that quote D-083's formula will otherwise read it as the reporting category assumption
15 said it was.

---

## D-175 — An erased person's grammatical form goes with their names

**Status:** decided (from your answer) — puts `person.gender` on
[the redactor's list in `00-conventions §8` item 1](../data-model/00-conventions.md#8-personal-data-and-erasure),
which named names and contact points and did not name it, and answers the question the previous entry's own answer
opened.

**The rule.** A redaction overwrites `person.gender` with the other personal fields. Since the column is required
and its set is closed, the set gains a fourth value that no screen offers and nothing but an erasure writes, and it
is the one the redaction marker already means. After an erasure no sentence in this system is ever addressed to that
person again, so the value is not a form of address; it is the shape a required column makes when its contents are
gone.

**The tension, kept in the open rather than argued away.** [D-059](round-05.md#d-059--unanswered-is-the-absence-of-a-row-a-registration-stores-two-values)
is the corpus's standing refusal to let an absence have a value, and this ruling writes one. The alternative was to
name `gender` in neither place — which is where it stood, and which meant an erased person kept a datum selected
for how the system would talk to them, forever, for a person the system no longer talks about. Between an absent
answer and an invented one, this round invents one and says so; the difference between that and the thing D-059
refuses is that D-059's rule is about *a person's answer to a question*, and nobody is being asked anything here.

**Why it is not simply deleted the way an attribute row is.** [Item 2 of §8](../data-model/00-conventions.md#8-personal-data-and-erasure)
deletes `person_attribute` rows because the row *is* the value and there is nothing left for a foreign key to point
at once it is gone. `person.gender` is a column of a row that must survive — the person id is what every 2003
reference resolves through — and a column of a surviving row cannot be removed without removing the row's shape.

---

## D-176 — Google or a password, one identity one account, and the invariant finally has a check

**Status:** decided (from your answers) — closes the fifth
[§ K question](../open-questions.md#k-filed-by-a-module-page), gives
[`00a`'s row for one current credential per external identity](../data-model/00a-invariant-register.md#3-the-answer-reads-another-table-a-resolver-or-a-graph)
the save-time check it recorded as **none**, and replaces the hypothetical that [`01a` §5](../data-model/01a-accounts-and-contacts.md#5-account_credential)
drew the `oauth` half of the table around.

**The rule.** A person signs in with **Google or an e-mail address and a password**. Every person may have their own
login. One external identity is one account: an `(external_issuer, external_ref)` pair held by a current credential
is refused at the save for a second account, and that refusal is the enforcement the register has been recording as
absent. A child who has no Google account, or will not sign in with one, is not given a worse login — they are
reached through the guardianship row ([D-178](#d-178--a-child-without-a-login-is-reached-through-the-guardianship-row)).

**What the hypothesis was, and what it cost.** `01a` §5 says `oauth` "supports a national Scout identity provider",
and the credential table's shape was drawn with that issuer in mind: one provider, whose subject id means *this
member*, because a national body's provider vouches for membership. **Google vouches for an e-mail address.** It
does not know the organization exists, it does not know the person is a member, and — the case the register's row
was written to name — a parent has one and three children. The register's row said the save-time check is *none*
and the failure is that "an issuer's login lands on whichever credential the index happened to keep". Under the old
hypothesis that was a tidy-up problem behind an issuer nobody had ever seen. Under Google it is the ordinary
sign-up path, and the row was one paragraph away from describing a shared family login as an index artifact.

**Why the answer keeps the constraint rather than loosening it.** The option on the table was the other one: let one
external identity back several accounts and have the person choose which to enter. It is not silly — it is how
family banking works — but it was refused, and the refusal has a consequence worth writing here rather than in a
cost column: **a child with no e-mail of their own has no account, and the model must not be read as needing one.**
That is why this entry and the guardianship entry are one ruling told twice, and why the register's row stops being
advisory: with self-service sign-up on a public provider, "one live account per person"
([D-089](round-07-08.md#d-089--one-live-account-a-colliding-sign-up-files-a-claim-and-creates-nothing))
and "one account per external identity" are the same wall seen from either side, and a wall with no check in it is a
comment.

**Cost, stated.** A family of four needs three Google accounts and a guardian's, and the organization will spend real
effort on that at the start of each year. Some of that effort lands on the person who signs a child up. The
mitigation already exists and is not new: a staff member may open an account, and it waits to be claimed
([D-179](#d-179--staff-may-open-an-account-only-its-person-can-start-it)).

---

## D-177 — The list of login methods is written in the program

**Status:** decided (from your answer) — settles how a method added later gets into
[`01a` §5's `credential_type`](../data-model/01a-accounts-and-contacts.md#5-account_credential), which is where a
magic link and an SMS code will arrive whenever they are built.

**The rule.** The allowed values are stated in the program and in this document. A new method is a release: the code
that authenticates against an SMS code and the value naming it ship together. No table lists the methods, and no
screen can offer one that has not been written.

**Why not a vocabulary row, when the corpus says vocabularies are rows.** Because the principle exists for data the
organization decides — a fee, a category, an office — and a login method is not data, it is behaviour. The
[one-row-table precedent, `membership_type`](../data-model/03-membership.md#1-membership_type--one-row-kept-as-a-table),
holds a thing a person could genuinely change their mind about; nobody has ever changed their mind about whether the
software speaks SMS. A table of methods would make a row exist that the software cannot honour, and the first
implementation of that table puts a row in it, offers it on a login screen, and breaks on the first click. **The
principle is not "anything enumerable is a row"; it is "anything the organization may decide is a row"**, and the
page that states the shape of `credential_type` should say which side of that line it is on, because the corpus has
now ruled both ways in the same neighbourhood.

**What stays on the list.** `password`, `passkey`, `totp`, `oauth`, `staff_link`. The answer named a magic link and
an SMS code as possible future methods and this round adds neither — a future version is not a value — and it
leaves `staff_link` alone, which the round-22 option proposed merging into a general link type. Merging was not
chosen; `staff_link` is what it says it is, a link a staff member issues, and the day a member may issue themselves
one is the day the list grows and this entry gets corrected.

---

## D-178 — A child without a login is reached through the guardianship row

**Status:** decided (from your answer) — the other half of [D-176](#d-176--google-or-a-password-one-identity-one-account-and-the-invariant-finally-has-a-check),
and the reason the account model does not need a child's e-mail address.

**The rule.** The guardianship channel is how an adult acts for a child who cannot sign in, and it already is:
a guardianship row carries a `right_level` of `none`, `view` or `write`
([`04` §2](../data-model/04-relationships.md#2-the-guardians-right-none-view-or-write)), and the party direction
already lets a party end the row, add a guardian and change the level. Nothing is added by this ruling. What is
settled is the negative half: **a child without their own external identity does not get a second-class credential,
a shared mailbox, or a login held by staff.** The absence of a login is not a gap in the child's record; it is a
record of an adult acting for them, which is what the table for that already says.

**Why this is a decision rather than an observation, since the mechanism was already built.** Because the model has
two ways to do the same job and until now nothing said which one is meant. A guardian acting for a child could ride
the guardianship row or an ordinary grant aimed at the child
([`04` §4](../data-model/04-relationships.md#4-how-the-resolver-uses-these-tables) reads both channels). After this,
for the case of a person who cannot sign in, the guardianship row is the answer, and the grant route is for an adult
who can. That fixes which of two working mechanisms an implementer builds first, which is the thing a document is
for.

**Where the same logic lands for an adult child, which was asked separately and is answered here.** [E-3](../open-questions.md#e-3--guardian-acting-for-an-adult-child)
asked whether a parent may register an adult child for an event with the child's consent, and the answer given was
that the delegation and the guardianship arrive at the same place, so keep the guardianship until someone ends it.
See [D-185](#d-185--a-guardianship-ends-when-a-party-ends-it-and-majority-is-not-a-party), which records that this
was already the rule and names the one sentence that was missing.

---

## D-179 — Staff may open an account; only its person can start it

**Status:** decided (from your answer) — closes the ninth
[§ K question](../open-questions.md#k-filed-by-a-module-page), the one round 22 touched without closing, and it
uses a status that already exists rather than a mechanism.

**The rule.** Staff may create an `account` row for a person who has not signed up — the useful case being a camp
office with a paper list. The row sits at
[`pending_verification`](../data-model/01a-accounts-and-contacts.md#4-account), which is already its default, and it
cannot authenticate until the person it belongs to, or that person's guardian, sets a credential. **Nobody ever
holds a child's password** is the whole of this rule said the other way round.

**Why a status rather than a rule against the write, which the corpus has said before.** [`01a` §4](../data-model/01a-accounts-and-contacts.md#4-account)
already writes its gate as a condition on a status "rather than as a rule against creating the row", and this lands
on the same choice for the same reason: the row is worth having before it can be used, because it is the thing a
registration attaches to and the thing an import attaches to. Refusing the insert would push staff into recording a
child somewhere worse than the database. A status that cannot sign in keeps the row and refuses the only thing that
mattered, which is a stranger or a well-meaning volunteer authenticating *as* a child.

**What is not refused, and should be watched.** Nothing here stops staff setting a password at the moment they
create the row and reading it out across a table. The write is audited like every other, the gate that allows it
exists and names who holds it, and the control is the trail — which is what this design has always relied on where
it refused a mechanism
([D-137](round-20.md#d-137--a-guardian-may-appoint-a-guardian-and-nobody-at-the-organization-is-told)).
If an organization wants that pattern to be impossible rather than visible, the way to want it is a denial, not a
column: an explicit `deny` on the write that sets a credential for somebody who is not you.

---

## D-180 — There is no queue for money that does not fit

**Status:** decided (from your answer) — closes the eighth
[§ K question](../open-questions.md#k-filed-by-a-module-page) by refusing its premise, deletes the queue as a named
thing from [`07` §2a and §2b](../data-model/07-finance.md#2b-money-that-cannot-be-matched), and narrows what
[D-076](round-06.md#d-076--money-that-cannot-be-matched-waits-for-a-person)
is a decision *about*.

**The rule.** Bank transactions arrive on a schedule and every one of them is in the system; there is no queue. A
`bank_transaction` whose `matched_payment_request_id` is empty is not waiting for a person and is not an exception —
**most money that arrives has nothing to do with a member at all**: donations, grants, a shop's sponsorship.
Accounting may tie any incoming transaction to any live request when they choose to. No page may describe an
unmatched row as a piece of outstanding work, because nobody is assigned to it, nothing counts it, and the design has
no way to tell "not yet" from "never".

**What survives D-076, because the decision was right and only its framing was wrong.** *Waiting is better than
guessing*: an unmatched transaction gets no subject assigned by a match on an amount and a date, and that stands
untouched. What dies is the picture underneath it — that an unmatched row is money with a person waiting somewhere
behind it, which is true of a camp fee and false of a sponsorship, and was drawn from a corpus of exports where
everything was a member. `matched_payment_request_id IS NULL` was written as "that absence *is* the queue"; it is
now the absence of a match, which is a value like any other absence
([D-059](round-05.md#d-059--unanswered-is-the-absence-of-a-row-a-registration-stores-two-values)) and stops being
the name of a worklist.

**What must not be swept by mistake, because two reports share the word.** [`07` §5's reconciliation list](../data-model/07-finance.md#5-open-issues--the-whole-of-this-document-essentially)
warns in its own words *"do not read this list as the queue"*, and that warning was written to keep an unrelated hole
— **a liability with no ask attached** — from being confused with the money queue. The money queue is deleted; the
hole is not, and it is still silent in both directions: nobody is chased and nobody pays. The sentence loses its
left-hand term and has to be rewritten rather than cut.

**The cost, which is the honest half of a no-queue design.** A transfer aimed at a camp whose request nobody ties
anything to can sit forever, and nothing anywhere will show that it is not merely non-member money. That is a
consequence of two answers taken together — nothing sends anything to anyone
([D-164](round-22.md#d-164--nobody-is-told-and-no-page-may-say-otherwise)), and now no list of rows that need
looking at — and it is bought on purpose: the alternative is a worklist whose first entry is always a grant payment
nobody wants to classify, and a worklist nobody clears is a lie about supervision. What makes this survivable is
that the money is not lost, only unattributed, and it is all on one screen in date order.

---

## D-181 — Every payable has a variable symbol

**Status:** decided (from your answer) — closes the scope half of
[`07` §5 item 5](../data-model/07-finance.md#5-open-issues--the-whole-of-this-document-essentially), which is the
question [D-075](round-06.md#d-075--money-arrives-from-a-bank-api-a-payment-is-requested-by-variable-symbol-and-qr-code)
raised and this round of questions finally got.

**The rule.** Every `fee_obligation` gets a `payment_request` and therefore a variable symbol — the yearly fee and a
camp fee alike — and it gets it because [every payable needs one](#d-180--there-is-no-queue-for-money-that-does-not-fit),
not because a person asked. The granularity the same item proposed stands as proposed: **one live request per
liability**, never per person and never per person-year, because a parent paying for two children in one transfer is
the ordinary case and a camp must not share a symbol with a membership fee.

**Why the answer had to be "every", and what the alternative really was.** With no queue, a liability with no symbol
has money arriving against nothing and nobody looking at a list where it would show. A second, hand-recorded money
path is what "membership only" buys, at the exact moment of the year with the most money and the fewest volunteers in
it — and hand-recorded is what the renewal window has been designed to avoid since
[D-040](round-02-03.md#d-040--the-fee-expires-yearly-a-date-tracked-renewal-window-replaces-a-grace-status).
The recommendation the page made in round 22 and the answer agree, so the entry records the answer rather than the
argument.

**Cost, stated.** Symbols are consumed for liabilities that are never paid — a child registered for a camp that
does not happen — and the sequence is
[unique across all rows forever](../data-model/07-finance.md#2-minimal-provisional-shape), so they are spent and
never reused. Eleven digits is a large number and this is not a real cost; it is named because a future reader will
wonder whether burning symbols on dead liabilities was noticed.

---

## D-182 — Matching money is a code of its own, and the automatic half is `system:bank-pull`'s

**Status:** decided (from your answers) — adds a `payment.match` code, gives the automatic half of matching an
actor that already exists
([`00-conventions §7a`](../data-model/00-conventions.md#7a-what-an-empty-actor-column-means) names six labels and
now still six).

**The rule.** Tying a `bank_transaction` to a `payment_request` by hand is a human act with a code: `payment.match`.
It is not an act of a unit — money arrives at one bank account and the ledger is one ledger, and the person who can
read a statement is not the person who owns the camp — so the code is held at the organization's scope, by whoever
runs the accounting. Tying the same two rows by variable symbol is not a human act at all: it is what the scheduled
bank fetch does, and its rows already belong to `system:bank-pull`.

**Why a code of its own when `payment.record` was free and the corpus prefers a code to cover a family of acts.**
Because the two acts point in opposite directions. `payment.record` writes money that a person typed, which is the
shape a correction and a refund take ([D-158](round-22.md#d-158--a-refund-happens-at-the-bank):
money leaves as a negative payment and the bank is where the fact lives). Matching asserts that a row the bank
already reported belongs to a liability somebody else created, which changes *somebody's membership status*
([D-039](round-02-03.md#d-039--member-permissions-require-a-current-paid-membership)) without writing any money.
One role doing both is fine and will usually happen; one code doing both means the permission that can free a
member is the permission that can type in a number, and this round has spent twenty entries on not conflating the
two.

**Why the automatic half needs no new label, which is the part of the answer that was not a free choice.** The
fetch that lands a transaction and the resolver that reads its symbol are one run, so one actor writes both rows;
this is also what the [existing label's own entry says it is for](../data-model/00-conventions.md#7a-what-an-empty-actor-column-means)
— "the `bank_transaction` and `payment` rows that answer a variable symbol" — which means the answer was already in
the label's wording and the question asked for a confirmation of it. Nothing in the fixed list is added, and the
count of six stands.

**The shape of the code, decided here because the entry adds it.** `payment.match`, namespace `payment`,
`applies_to = unit`. Not `unit_and_item`: money is not an item in the sense that an event or a group is one, and an
item-scope grant on a fee would be a right over one obligation, which is nobody's job. It is a `write`.

**Cost, stated, and one thing this entry found out by trying to cite it.** A second money code is a second thing a
curator has to grant, and an accounting role given `payment.match` without `payment.record` can settle transfers but
cannot correct them — which is the point of the split and will read as an oversight to whoever grants the first one.
**And where the code is written down turned out to be a different question than the one this entry first answered.**
The sentence drafted here said the money codes were *"registered by no page"*, and the grep drafted to prove it found
[the catalog's deferred namespaces](../appendix/permission-catalog-b-roles-and-open-issues.md#10-deferred-namespaces),
which lists `fee.view`, `fee.create`, `payment.view`, `payment.record`, `payment.reverse` and `report.finance.view` and
has listed them for six rounds. **So the codes are registered — in the section reserved for namespaces whose module
does not exist yet, while this module already moves money.** [Catalog A](../appendix/permission-catalog-a-codes.md)
has sections for people, accounts, membership, organization, groups, guardianship, permission administration, audit,
events and keys, and no money section, so the two codes this round adds go to §10 beside their family: that is where a
code that exists is filed when its namespace has never been promoted, and this entry records the correction rather
than the claim, because the file it cites says something the entry did not read. **Whether the promotion is owed is
[K-10](../open-questions.md#k-10--are-the-money-permission-codes-still-deferred).**
Because there is no `permission.create` and no `permission.delete`
([D-152](round-21.md#d-152--zero-is_system-columns-what-protects-a-vocabulary-is-its-table-not-a-flag-on-its-rows)),
both codes arrive as seeded rows in a migration, which is the only way a code has ever arrived.

---

## D-183 — A changed ask is a voided request and a new symbol, and `amount_discount` goes

**Status:** decided (from your answer, against the recommendation this page first offered) — answers the discount
question [`07` §5 item 1](../data-model/07-finance.md#5-open-issues--the-whole-of-this-document-essentially)
asked as a yes or no, deletes `fee_obligation.amount_discount`, and settles what "change the amount" means in a
module whose asks are printed on QR codes.

**What was actually asked.** The question put to you was whether a family or sibling discount exists. What came
back was a requirement, not a policy: *be able to select payment requests and change their amount*. A discount is a
policy about who owes less; editing an ask is a capability somebody will use for a discount, a mistake, a
negotiated camp fee, or a transcription error, and the design has to answer the capability. Three shapes were
weighed — edit the rows in place, add an adjustment table, void and reissue — and the third was chosen.

**The rule.** `fee_obligation.amount_due` is edited in place, exactly as
[D-160](round-22.md#d-160--no-proration-rule-and-the-row-is-the-amount)
already ruled that a reduced fee is "an obligation written with a smaller `amount_due`, the same act that writes any
other amount" — this round only makes explicit that *written* includes *written again*. **What a person has been
asked to pay is never edited.** Changing an ask means the live `payment_request` is voided, with
`voided_reason`, and a new request is issued with the new amount and **a new variable symbol**; the old symbol keeps
resolving to the row it was printed on, which is voided, and money against it is matched by hand
([D-182](#d-182--matching-money-is-a-code-of-its-own-and-the-automatic-half-is-systembank-pulls)).
`amount_discount` is deleted, and the balance in
[§3](../data-model/07-finance.md#3-keeping-membershipoutstanding_balance-honest)
loses a term: **balance = `amount_due` − allocations**.

**Why in-place editing of the request was refused, in one sentence a payer could check.** The symbol, the amount
and the QR code were shown to a person standing at their own bank. Editing a live request's amount rewrites the
promise while it is in their hand: they pay the figure they were given, it does not fit the ask, and after
[D-180](#d-180--there-is-no-queue-for-money-that-does-not-fit) there is no list where that mismatch would ever
appear. The request's `amount` is a copy rather than a reference for precisely this reason —
["what a person was asked to pay is a historical fact about the ask"](../data-model/07-finance.md#2-minimal-provisional-shape).

**Why no adjustment table, which was the option with the best argument.** A named reduction is countable, and after
[D-157](round-22.md#d-157--there-are-no-hardship-waivers)
nothing in this design can answer "how much did we reduce this year" — that report is genuinely gone, and an
adjustment row would have restored it. It was refused because the shape it needs is the shape this module has
refused twice: a second set of rows that the balance has to sum and the reconciliation checks have to agree with,
which is what [`07` §2b](../data-model/07-finance.md#2b-money-that-cannot-be-matched) says about a separate
worklist, and what the matcher would inherit — an ask settles against `amount` minus a sum of adjustments, which
turns a comparison into a solver. It also needs a code, a scope and a granter's ceiling
([D-163](round-22.md#d-163--a-grant-may-not-confer-more-than-the-granter-holds)), which is the corpus's costliest
unit of new machinery. **And it buys nothing void-and-reissue does not:** a voided request is a permanent row holding
the amount originally asked for, with a reason and a person's name on it, kept with no end date
([D-088](round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)). The history was
already being kept; it just was not being read as history.

**What is lost, and it should be read rather than skipped.** A discount that is granted by lowering `amount_due`
leaves **no mark that a reduction happened** — after the edit the row reads as a fee that was always that size, and
the audit payload saying what it used to be
[empties after 24 months (D-088)](round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short).
Void-and-reissue keeps the old *ask*, not the old *liability*: an obligation written at 500, edited to 350 before
any request went out, is a 350 obligation with no trace of the 500 anywhere in the data. That is the exact hole
D-157 refused to build a mechanism for and this entry now states as ordinary operation: **the discretion exists, it
is audited while the payload lives, and no report will ever count what it was used for.** If a grant report ever
needs that number, this is the entry to reverse, and the reversal is the adjustment table refused above.

**Cost, stated twice because the plural was in the requirement.** "Select payment requests, plural, and change
their amount" is a loop of one void and one new symbol per row, not an edit: twelve children on one camp means
twelve voids and twelve new symbols, and each family's QR code changes. The old symbols stay live in the banks. And
`amount_discount` was not decorative — it is a term in the balance and in
[§5's checks](../data-model/07-finance.md#5-open-issues--the-whole-of-this-document-essentially), so deleting it
moves three pages and one check that compares a screen against a recomputation.

---

## D-184 — Every table is audited, and the delete carve-out names the moments that survive

**Status:** decided (from your answer) — turns
[assumption 17](../open-questions.md#i-assumption-index)
into a rule, closes [`06b` §6](../data-model/06b-redaction-and-checks.md#6-open-issues)'s ask for confirmation
rather than derivation, and re-cuts the `DELETE` carve-out in
[`06` §2.1](../data-model/06-audit-and-import.md#21-the-trigger)
now that [D-190](#d-190--the-legacy-import-is-a-script-and-a-key-and-the-pipeline-is-gone) has removed one of its
moments.

**The rule.** The audit obligation is no longer scoped by a list of tables. Every table the application writes owes
one `audit_log` row per insert and update, on every path, from the day the table exists. The only tables outside it
are the trails themselves: `audit_log` and `access_log` are the record, and a record of a record is a row that has
to be recorded in its turn.

**Why the confirmation was worth asking for at all, when §2.1 already claimed it.** Because §2.1 named some tables
and then pointed at an open question for the rest, and
[the page holding that question](../data-model/06b-redaction-and-checks.md#6-open-issues)
asked for somebody to read the list and say yes — the cheapest closure on the register and the one nobody
volunteers for, because a confirmation changes no table and closes no hole visibly. A rule whose scope is "everything
except the list we never finished" is a rule that a new table can fall outside of by nobody noticing; check 5's
assertion that the list and the write paths agree had nothing correct to agree with.

**The delete carve-out, re-cut.** §2.1's `DELETE` exclusion rested on "nothing in this data model is hard-deleted"
and admitted **two** moments where a delete reaches a business row: the import revert and erasure's attribute
deletion. The revert is gone ([D-190](#d-190--the-legacy-import-is-a-script-and-a-key-and-the-pipeline-is-gone)),
so one path reaches a business row with a delete — erasure, which audits nothing per row and is recorded once in
`redaction_log` — and one path deletes a trail row: [`access_log`'s age-out at 24 months
(D-145)](round-20.md#d-145--access_log-rows-are-deleted-at-24-months-and-the-job-that-does-it-has-a-name).
That leaves the enumerated list in check 5 shorter by one, and it leaves the deletion policy in
[`00-conventions §4`](../data-model/00-conventions.md#4-deletion-policy)
carrying **two** exceptions where it currently says three, because the staging truncate goes with the pipeline.

**Reading, not ruling — but the reading this answer forces.** [D-145](round-20.md#d-145--access_log-rows-are-deleted-at-24-months-and-the-job-that-does-it-has-a-name)
gave the age-out a name in the fixed actor list for one reason: "a job that removes rows has to be nameable". While
`DELETE` wrote no audit row anywhere, that name had nowhere to be written — the label existed in a list and on no
row. Now that every table is audited and the age-out is the one scheduled delete left standing, the reading is that
**it writes one summary audit row per run** — `system:log-reduction`, how many rows went, and the window that
removed them — and not one row per deleted row. Per-row entries would either quote contents the deletion exists to
destroy, which is the argument
[`06` §2.1 makes for erasure](../data-model/06-audit-and-import.md#21-the-trigger), or accumulate thousands of rows
whose entire content is "something was deleted", which is the same argument. So the age-out finally becomes
attributable in the place D-145 implied it already was.

**Cost, stated.** A trail that records every table is bigger than one that records the interesting ones, and this
design already says the cost of the obligation is storage rather than correctness. The offsetting fact is the one
[D-088](round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)
set up: rows are kept indefinitely and **payloads empty at 24 months**, so the growth is in the skeleton of the row,
and widening the obligation multiplies a small fixed-size row rather than a payload holding two images of a person.

---

## D-185 — A guardianship ends when a party ends it, and majority is not a party

**Status:** confirmed (from your answer), with the sentence that was missing — closes
[E-3](../open-questions.md#e-3--guardian-acting-for-an-adult-child), and re-points
[assumption row 9](../open-questions.md#i-assumption-index), which round 22 struck through as superseded.

**What your answer added to what was already written.** You answered that a delegation and a guardianship arrive at
the same result, so leave the guardianship until the child or another guardian ends it. [`04` §1](../data-model/04-relationships.md#1-guardianship)
already says a `valid_to` is set by a person and **never by a job**
([D-069](round-05.md#d-069--guardianship-ends-when-a-person-ends-it-the-system-takes-no-position-on-majority)),
and its table of three acts already gives the ending of a row to the guardian, to staff on request, and to
**"the subject (adult)"** ([D-073](round-06.md#d-073--guardianship-is-administered-by-its-own-parties-not-by-staff)).
The answer is the rule on the page. **What was missing is the sentence that says a dependent may be an adult** —
nothing restricts the column to a minor, and nothing said so either, which is how
[E-3](../open-questions.md#e-3--guardian-acting-for-an-adult-child) could stay open while its answer sat three sections away.

**So, plainly.** A guardianship row's dependent is a person, not a minor; nothing happens to the row when the
dependent's birth date passes 18; a parent acting under a `write` level may register an adult child for an event
because that is what `write` says; and the row ends when the guardian ends it, when the adult named in it ends it,
or when staff record either of those. A delegated grant remains available to an adult who prefers it
([D-143](round-20.md#d-143--a-delegation-is-validated-once-when-it-is-written-and-stands-to-its-own-end-date)),
and this ruling does not prefer one over the other — it refuses the premise that a second mechanism was needed.

**Why "both arrive at the same result" is worth recording as an answer rather than an evasion.** Because the two
mechanisms are checked through different channels — the guardianship channel is entered by shape and cannot be
denied ([D-079](round-06.md#d-079--the-guardianship-channel-is-entered-by-shape-not-by-permission-name)), while a
delegation is an ordinary grant with everything that implies — and the register's recommendation for E-3 argued for
the delegation on the ground that *the legal basis differs*. Your answer drops that argument for the reason the
corpus would give: the legal basis is not something this system records a position on
([D-069](round-05.md#d-069--guardianship-ends-when-a-person-ends-it-the-system-takes-no-position-on-majority)),
so it cannot be a reason to prefer a mechanism.

**Cost, stated.** An adult with a guardianship row still pointing at a parent, because nobody ended it, has a person
with `write` over their records. Every defence here is the one this design always uses: the subject may end it
without a grant and without anybody's agreement, the row names both parties, and the trail shows every act taken
under it. What is *not* there is a prompt — no report lists adult dependents whose guardianship outlived its
reason, because the design takes no position on majority and a list like that is the position, wearing a report.

---

## D-186 — `membership_type` is settings wearing a vocabulary's clothes

**Status:** decided (from your answer) — closes [F-9](../open-questions.md#f-9--should-membership_type-stay-a-table-with-one-row), changes no table, and moves the
defence of [`03` §1](../data-model/03-membership.md#1-membership_type--one-row-kept-as-a-table)
off the ground it was standing on.

**The ruling.** The one-row table stays, with its `member` row and its foreign key that can only ever hold one
value, and it stops being described as a vocabulary. **It is a settings row**: three of its columns are the
organization's calendar — `expiry_month`, `expiry_day`, `renewal_grace_days`, the knobs
[A-4's remainder](../open-questions.md#a-4-remainder--the-organizational-calendar)
exists to keep out of code — and a settings row that one other table points at is a settings row with a foreign key,
not a taxonomy with one member.

**Why the distinction is worth an entry rather than a sentence.** Because the defence on the page was the
corpus's own best principle — *vocabularies are rows, not enums* ([D-037](round-02-03.md#d-037--exactly-one-membership-type-the-fee-is-flat-and-per-person))
— applied to a table that does not earn it. A vocabulary is a set the organization may change its mind about, and
for twenty-two rounds this one has been refused a second member at every turn: the fee is flat and per person, one
live price is edited in place
([D-161](round-22.md#d-161--one-live-price-and-the-amount-is-filed-as-a-question-at-last)),
and the fee buys membership and nothing else
([D-156](round-22.md#d-156--the-fee-buys-nothing-but-membership)). **A principle cited on behalf of a shape it does
not describe is a principle that will be cited wrongly again**, which is the same failure as
[the login-method list in D-177](#d-177--the-list-of-login-methods-is-written-in-the-program)
— two tables in the same round, both defended by "vocabularies are rows", neither of them a vocabulary.

**What stays exactly as it was.** The row, the key, the columns, the seed of one `member`, and the discipline A-4
asked for: a job or a screen that contains the literal `60` or the literal `1` is the only way to lose the property
those columns were bought for. Renaming the table was not chosen, and would have been a rename of a table for the
sake of a comment.

---

## D-187 — An invoice is a document a payer asks for

**Status:** decided (from your answer) — closes [`07` §5 item 2](../data-model/07-finance.md#5-open-issues--the-whole-of-this-document-essentially),
adds an `invoice` to [the inventory](../appendix/erd-b-inventory.md) and an `invoice.issue` code, and answers a
question whose wording had to be corrected before it could be answered — the first answer said *by the payee*, and a
payee is the organization, which would have had it invoicing itself.

**The rule.** A payer may ask for an invoice against a `payment_request` they have been sent. Issuing one writes an
`invoice` row over the same obligation, carrying its own number from its own sequence, and it is written by whoever
holds `invoice.issue`. **A `payment_request` is not an invoice and does not become one** — that was the page's own
sharpening and it survives untouched: no tax identity, no legally-required sequence, no delivery record. If this
country turns out to require invoices of somebody, the answer is this table, not a renaming.

**Why there is no "requested" state, which is the half of this a reader will trip on.** A payer's ask that sat on a
row waiting for accounting to notice it is **the queue this round deleted two entries ago**
([D-180](#d-180--there-is-no-queue-for-money-that-does-not-fit)) wearing a different coat: a column meaning
*somebody owes this person a document*, with nobody assigned to it and nothing counting it. So an invoice is a row
that exists or does not. Someone asks; someone issues; the trail of the ask is the conversation the organization had
with the payer, which is outside the database, exactly as [D-173](#d-173--that-two-groups-are-the-same-group-is-said-not-stored)
does for a troop that continues another troop. **Reading, not ruling:** if this turns out to be wrong in practice —
if invoices are asked for often enough that forgetting one is a real failure — the fix is a report over the requests
that have no invoice, not a status on the request.

**What this does not touch, and the review that still owns it.** [Item 4 of §5](../data-model/07-finance.md#5-open-issues--the-whole-of-this-document-essentially)
asks what this country's law demands of a fee, and
[the four data policies already in front of a legal review](../data-model/00-conventions.md#8-personal-data-and-erasure)
sit in the same sitting. This round decides that the organization *issues* invoices when asked. Whether it is
*obliged* to, what one must contain, and how long it must be kept are a lawyer's questions and stay filed. The
document this design has now added a table for may turn out to need columns this design has not invented; that is
the correct order, because a table whose number is real is cheaper to extend than a document that was printed
without one.

**The shape of the code.** `invoice.issue`, namespace `invoice`, `applies_to = unit`, a `write` — same reasoning as
[`payment.match`](#d-182--matching-money-is-a-code-of-its-own-and-the-automatic-half-is-systembank-pulls), and the
same complaint: it joins a money family the catalog files as **deferred** — a namespace whose module does not
exist — while the module that spends these codes has been designed for two rounds and moves real money in
[`07`](../data-model/07-finance.md).

**Cost, stated.** A third money entity, a second numbering sequence beside the variable symbol's, and a code whose
holder can produce a document with a legal shape. `invoice.issue` is deliberately separate from `payment.match`
([D-182](#d-182--matching-money-is-a-code-of-its-own-and-the-automatic-half-is-systembank-pulls))
so that the person who can settle a transfer is not automatically the person who can sign a tax document, and — this
is the sentence that matters — **nothing in this design sends the invoice to anybody**
([D-164](round-22.md#d-164--nobody-is-told-and-no-page-may-say-otherwise)). It exists on a screen and is handed over
by a person or printed by one, and no page may say otherwise.

---

## D-188 — The ceiling reads a grant and nothing else, and what it leaves open is written down

**Status:** decided (from your answer) — answers the half of
[D-163](round-22.md#d-163--a-grant-may-not-confer-more-than-the-granter-holds)
that its own entry refused to pretend was settled, and settles it in the direction of *no*.

**The rule.** The granter's ceiling reads a write to `access_grant` whose subject somebody chose, and nothing else.
It does not read an edit to an `audience`'s expression tree, and it does not read adding a person to an office. A
grant pointing at an audience can therefore be widened without any write to `access_grant` at all, and this says so
in the pages that describe the ceiling rather than leaving it to be discovered by whoever audits something.

**What that costs, stated without softening, because the shape of it is not obvious.** An audience's whole content
is an expression over named sets ([D-101](round-10b.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree)),
and a person holding `audience.manage` can rewrite one. Rewriting `ROLE(camp organizer)` to `MEMBERS` takes every
live grant that names that audience and gives it to everybody in the unit — including the person who made the edit,
who needed no grant to make it and no grant to be covered by it. **That is escalation, and the ceiling does not see
it**, because no grant was written and no grant was touched. It is bounded by what the vocabulary can be made to
read: to admit a specific person an editor still has to be able to name a set they fall into, and adding them to an
office is a separate act behind `role.assign`. But the broad case does not need any of that.

**Why "no" anyway, which is the answer given and the reason it is defensible.** Because the alternative is not
safe, it is only wider: a ceiling that reads an expression edit has to decide, at the save, what the expression
resolves to for every live grant that points at it — which is a permission check *inside* the definition of a
permission's reach, running while the check is being changed. The corpus has refused that recursion before, and it
refused the mechanism rather than the worry: **`audience.manage` is not a lesser code than `access_grant.create`
and must not be granted like one**, which is a sentence the catalog should carry beside both codes. The control for
the widening is the same control that protects the codes themselves — there is no `permission.create`, no
`permission.delete`, and `permission.edit` reaches labels only
([D-152](round-21.md#d-152--zero-is_system-columns-what-protects-a-vocabulary-is-its-table-not-a-flag-on-its-rows)),
so what is rare is rare because somebody granted it, once, in the open.

**Cost, stated.** Two things now widen a right without a ceiling reading them, and [D-170](round-22.md#d-170--the-ceiling-does-not-read-the-twelve-a-create-writes)
already refused to let "by construction" cover a pair: the twelve rows an event create writes, and the audience an
editor can rewrite. The difference between them is worth keeping straight rather than merging into a worry —
the twelve name nobody the writer chose, and this one names exactly whoever the editor decides to name.

---

## D-189 — One author writes the vocabulary before the batch

**Status:** decided (from your answer) — closes the schedule half of [F-34](../open-questions.md#f-34), which is the
question [D-141](round-20.md#d-141--a-definition-is-live-at-the-save-the-proposal-stage-its-queue-and-its-check-are-deleted)
left open by deleting the stage that used to carry it.

**The rule.** One named person holds `attribute.define` and writes the definitions the legacy corpus needs,
sitting with the source's column headers, **before** the batch that would otherwise refuse at apply time on a mapped
column naming no live code. Afterwards the code stays with that role. There is no queue of proposals, no ageing, no
curation stage — the mechanism was deleted in round 20 and stays deleted — and what replaces the schedule the
deleted stage secretly carried is a person and a period, written down.

**Why the answer is a name and not a mechanism, which is the pattern of this whole round.** D-141 removed
`proposed` and with it the only thing that made the vocabulary arrive *in time for* an import, and the round noticed
afterwards that a mechanism had been quietly answering a question nobody had written. The corpus has now answered
that shape of gap four rounds running the same way: **a report and a written procedure, not a mechanism**
([D-126](round-17.md#d-126--break-glass-is-a-report-and-a-written-procedure-not-a-mechanism)),
and [D-164](round-22.md#d-164--nobody-is-told-and-no-page-may-say-otherwise)
means the schedule cannot be a reminder — nobody is told anything, including the author, and the page that states the
rule must be where the deadline lives.

**Reading, not ruling:** the refusal that D-141 put at apply time was a refusal *of the pipeline*, and the pipeline
is gone ([D-190](#d-190--the-legacy-import-is-a-script-and-a-key-and-the-pipeline-is-gone)). What survives is the
invariant underneath it — **a value may not invent a code**, and an unmapped column is an error rather than a
proposal — which now binds the script, and every later write, exactly as hard.

---

## D-190 — The legacy import is a script and a key, and the pipeline is gone

**Status:** decided (from your answer) — the largest deletion since
[D-097](round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)
removed the unit hierarchy, and the reason several pages of this corpus now describe a thing that does not exist
until they are swept.

**The rule.** The membership and attendance exports are loaded **once**, by a script, through an `api_key`. The
script reads the two exports, transforms them, and writes rows through the application with a key that the
[keys-and-callers page](../data-model/05e-keys-and-callers.md)
already knows how to authenticate and already names as a third kind of grantee
([D-116](round-16.md#d-116--a-caller-that-is-not-a-person-is-a-registered-key-and-a-key-is-a-third-grantee-kind)).
Everything built around the idea that an import is a feature of this system is deleted.

**What dies.** `import_batch` and `import_batch_id`; the staging tables `staging_import` and `staging_import_row`,
and with them [the deletion policy's first exception](../data-model/00-conventions.md#4-deletion-policy) — the
staging truncate, which was one of the three named holes in "nothing is hard-deleted" and is now one of two; the six
stages and the field→code mapping, which is
[`06a` §3](../data-model/06-audit-and-import.md#3-import-pipeline--deleted) entire; the per-batch revert, and with it the *first* of
the two moments where [`06` §2.1](../data-model/06-audit-and-import.md#21-the-trigger)
let a delete reach a business row; the four codes `import.view`, `import.apply`, `import.stage` and `import.revert`;
the `import_batch:<id>` entry in the fixed actor list, which goes from six labels to five;
[`06a` §4's three checks](../data-model/06-audit-and-import.md#3-import-pipeline--deleted), all of which are assertions about
staged rows and batch accounting; and the page
[`06a-import.md`](../data-model/06-audit-and-import.md#3-import-pipeline--deleted) itself, whose whole contents are those two sections.

**What does not die, and should not be swept by mistake.** The **bank** import is a different thing and stays:
transactions arrive on a schedule under `system:bank-pull`
([D-075](round-06.md#d-075--money-arrives-from-a-bank-api-a-payment-is-requested-by-variable-symbol-and-qr-code)),
with `bank_reference` as the idempotency key. D-169's end-date inference stays the rule for what an imported
membership's `valid_to` holds, but it is now a rule about rows rather than about a pipeline's parse step, and its
check goes with the page it was written on. D-093's ruling that the one-off load may create dated memberships
stands, D-092's description of the corpus as people and events stands, `data_confidence` stays on the rows the
script writes because the periods are still inferences, and D-141's invariant — a value may not invent a code — is
what the script must obey instead of a stage that used to enforce it.
[D-090](round-07-08.md#d-090--the-legacy-corpus-is-thousands-of-roster-rows-with-numbers-and-no-money)'s
"no unit is named by any row" consequence is untouched and remains the reason there is no sub-unit history.

**What is genuinely lost, named one by one rather than waved at.**

- **Revert.** A batch that goes wrong can no longer be undone as a batch. A bad load is corrected forward — row by
  row, in the open, each correction audited — or the database is restored from before it ran. This is the real
  price, and the honest framing is that it was never a safety feature so much as a *tidiness* feature: the rows it
  let you un-write are rows a person with the script could have written wrongly one at a time, and nothing in this
  design lets a bad `membership` go unnoticed for long, because [D-039](round-02-03.md#d-039--member-permissions-require-a-current-paid-membership)
  puts an open membership at the front of a permission check.
- **The person who ran it.** `import_batch.created_by` named whoever uploaded the file. A key names itself and
  never carries a person's authority ([D-121](round-16.md#d-121--a-key-never-carries-a-persons-authority)), so the
  trail will say *this script's key wrote these rows* and not *Ana ran it at eleven at night*. Accountability
  survives one step removed: the key was granted, the grant names its holder, and the grant is audited. That is a
  weaker sentence than the one it replaces and it should be recorded as weaker.
- **Provenance as a column.** `import_batch_id` on created rows let any report ask "what made this row" without
  touching the trail. After this, provenance lives in the trail: an `audit_log` row whose `api_key_id` names the
  load. The trail's rows survive — [their payloads empty at 24 months and the skeleton stays
  (D-088)](round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short) — so *which key
  wrote this* is answerable forever while *what it wrote* is answerable for two years, which is the same bargain this
  design already makes everywhere else and is exactly why
  [D-152](round-21.md#d-152--zero-is_system-columns-what-protects-a-vocabulary-is-its-table-not-a-flag-on-its-rows)
  refused to put provenance flags on rows.
- **Three checks.** All of [`06a` §4](../data-model/06-audit-and-import.md#3-import-pipeline--deleted) is assertions about staged
  rows. The one that mattered was the first — an imported membership with no end date, which is authority rather
  than untidiness, and was **the only check on that page that reached the permission gate**. Its subject outlives
  it: an open imported membership is still a person who can be handed rights by
  [D-039](round-02-03.md#d-039--member-permissions-require-a-current-paid-membership), and D-169 still supplies the
  date that closes it. What is gone is the report that would have noticed one, which is a hole, and the shape of the
  hole is a `membership` row with `valid_to` empty whose audit row names the load's key.

**Why the deletion is right anyway, which is not the same as it being free.** The machinery was built for a job
that happens **once**, and every one of its features — six stages, staging tables, a mapping the organization
edits, a revert, four permission codes, a fixed actor label, three checks — is a feature of a thing that will be
run and never run again. This corpus's own test for a mechanism has been the same in every round: *who uses this on
a Tuesday?* Nothing here used the pipeline on a Tuesday. The script has the same requirements written in a language
where they are cheap — idempotence in a script is a key and a skip — and the parts that were decisions rather than
machinery are the parts this entry has just carried forward.

**One consequence nobody asked for and it is fair to name.** The transformation stops being configuration and
becomes code, so the definitions of what a source row means — that a people row evidences *a person and a bounded
membership*, that an attendance row evidences *an event nobody owns and a registration*
([D-102](round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it))
— now live in a script that is not in this repository and will not be reviewed by whoever reads this page next.
The rules survive; the place they are readable does not.

---

## D-191 — `person.notes` is deleted, and the vocabulary takes the job

**Status:** decided (from your answer) — closes the sixth
[§ K question](../open-questions.md#k-filed-by-a-module-page), deletes a column of `person`, and removes the one
corner of the person record that [D-083](round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)
was written to forbid.

**The rule.** The column is gone. Free text about a person becomes what every other free text about a person
already is: an `attribute_definition` row somebody holds `attribute.define` for, live at the save of that person
([D-141](round-20.md#d-141--a-definition-is-live-at-the-save-the-proposal-stage-its-queue-and-its-check-are-deleted)),
readable by anyone with `person.view`, erased by having its rows deleted like every other attribute row. There is no
longer a place to write something about a child that is not in the vocabulary.

**Why this was worth a ruling rather than a shrug, which is the argument the holding page had already made.**
[`01-identity`'s own field row](../data-model/01-identity.md#2-person)
said the column "may contain anything, including a diagnosis sitting under a column nobody would call medical", and
its own boundary section said it "is a worse exposure than most of what" the vocabulary guards. The protection it
did have was the one every guarded field has: the trail, and `audit.view` deciding who may read a value at all
([D-138](round-20.md#d-138--one-permission-guards-the-whole-audit-trail-and-the-widening-is-on-the-record)).
**So the column bought nothing except the property of not being in the vocabulary** — and not being in the
vocabulary is the thing that made it worth asking about, because a value the organization has to define in order to
store is a value somebody had to think about once.

**The erasure argument runs the opposite way to the obvious one, and it is the strongest reason for the deletion.**
`person.notes` was deliberately kept off [the redactor's list](../data-model/00-conventions.md#8-personal-data-and-erasure),
and the reason given was that naming a column as an exception is the field-name rule D-083 removed. The consequence
nobody drew was that a redaction therefore **left the notes intact**: erasure overwrites names and contacts, deletes
every `person_attribute` row, empties an event answer — and does not touch the free text that the same page admits
may hold a diagnosis. Moving the text into the vocabulary does not weaken its erasure, it fixes one: attribute rows
are the one thing this design *deletes* on erasure, because the row is the value
([§4's second exception](../data-model/00-conventions.md#4-deletion-policy)). A diagnosis that lived in `person.notes`
survived being asked to leave; the same diagnosis as an attribute value does not survive it.

**What the sweep has to re-point rather than delete.** [§8 item 2](../data-model/00-conventions.md#8-personal-data-and-erasure)
names "free-text notes that may contain personal data" in its cascade, and
[`09-attributes`](../data-model/09-attributes.md#7-the-legacy-import-which-is-where-the-vocabulary-comes-from)
lists notes as an example of what the vocabulary is for; both are now about attribute rows rather than about a
column. And the corpus is not now free of free text about a person, which the pages that keep the remaining ones
should say rather than imply: a roster row's `note`
([`02` §2](../data-model/02-organization.md#2-person_group_member)) is free text about why a child joined a group
and is written in the organization's words on purpose; an account's `status_reason` and `status_note` are free text
about a person in the words of whoever suspended them; a `field_conflict` holds the two values a merge could not
choose between. Every one of those is a row of a relationship or an act rather than a column of the person record,
which is the distinction this deletion draws and no page has ever stated — **the person row holds no free text, and
plenty of rows about a person still do.**

**Cost, stated.** One column is easy to delete and the cost is not in the schema.

- **The legacy load meets D-141 face to face.** A source export with a notes or remarks column can no longer land it
  anywhere without a definition existing first, and the refusal is now the script's
  ([D-190](#d-190--the-legacy-import-is-a-script-and-a-key-and-the-pipeline-is-gone)). That is the correct order —
  [one author writes the vocabulary first](#d-189--one-author-writes-the-vocabulary-before-the-batch) — and it is
  also the first place an operator will hit it, because "notes" is the column every export has.
- **A merged note is now N values, not one.** Free text arriving as one blob against a person becomes one or more
  attribute values, each of which has to be mapped to a code by somebody reading it, which is exactly the work
  `attribute.define` was made to carry and is not work the column ever asked anyone to do.
- **The trail still holds what the column held, for as long as payloads live.** Deleting a column does not delete
  its past: `audit_log` rows carry before and after images of a field that no longer exists on the table, and they
  empty [at 24 months (D-088)](round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short).
  Someone auditing 2027 in 2030 will find an old value under a column name they cannot find in the schema, which is
  true of every deletion this corpus has ever made and is worth saying once where the deleted thing was the worst
  field on the table.

**What is refused, so that nobody re-litigates it from this entry.** Keeping the column and putting it on the
redactor's list was the third option, and it is the one that contradicts a decision: naming a column as an exception
to a field-name rule is what D-083 removed, and a design with one named exception invites the second. Keeping it
exactly as it stood was the second, defensible on the grounds that the trail already guards every field; it was
refused because the corpus's own page called the column a worse exposure than the things the vocabulary protects,
and a page that says that about its own column has made the argument.

## D-192 — `proposed_by` loses `import_job`, because a vocabulary value is a claim about who can write

**Raised by this round's own sweep, and by nothing else.** After [D-190](#d-190--the-legacy-import-is-a-script-and-a-key-and-the-pipeline-is-gone) deleted the pipeline, two pages went on
describing `match_proposal.proposed_by` as one of `import_job`, `match_job`, `person`, `staff`
([01b §8](../data-model/01b-merges-views-and-checks.md#8-identity_hypothesis-and-person_merge),
[domain/03 §3](../domain/03-identity-and-legacy.md#3-identity-hypotheses-not-merges)). **No gate would have caught
it.** `scripts/check-registries.py` reads permission codes, selectors, scope types and actor labels; an enumerated
column's value set is not a registry it knows, so a value that names a mechanism this corpus has just deleted is
invisible to it, and the sweep that deleted the page was looking for pages.

**Answer.** The value is deleted. `proposed_by` is one of `match_job`, `person`, `staff`.

**Why not rename it `legacy_load`, which is what it meant.** Because the rename keeps the false claim and adds a
migration to it. The column answers *who put this hypothesis in front of a reviewer*, and after [D-190](#d-190--the-legacy-import-is-a-script-and-a-key-and-the-pipeline-is-gone) the
writers are the nightly matcher, a person asserting that a sign-up colliding with their record is themselves
([01a §4](../data-model/01a-accounts-and-contacts.md#4-account)), and a staff member at the review screen.
**The load does not propose matches.** If it lands two near-duplicate people, it is the matcher's code that scores
the pair and the matcher's name the value carries; the load's own writes carry the key that ran it, which is
provenance and answered where provenance lives ([`06` §3](../data-model/06-audit-and-import.md#3-import-pipeline--deleted)).

**This is not the corpus forgetting which rows are legacy.** Stated here so the deletion is not read as a second
sweep of the same idea: `person.record_origin`, `data_confidence`, `person_attribute.source`, and the `source`
columns on names, contact points, identifiers and registrations all still say *an import wrote this*, and
[D-190](#d-190--the-legacy-import-is-a-script-and-a-key-and-the-pipeline-is-gone) kept them on purpose. **A row's provenance marker and a proposal's origin value answer different
questions**, and only the second one lost the thing it named.

**What it costs.** A hypothesis that exists only because the load created a duplicate can no longer be told apart,
*in this column*, from one the nightly matcher found by itself. It can be reconstructed by reading the trail behind
the two person rows, which is work no page promises and a report no check lists. The review screen is the only
reader of this column and it shows the signals, not the origin, so the loss lands on nobody's workflow — which is
the reason it is worth recording rather than the reason to ignore it.

**The rule this generalizes, and it is not new.** A value in an enumerated column is a claim that something in this
system can be that thing. When a mechanism dies, every value that named it dies in the same round — the test
[D-113](round-13.md#d-113--the-guardianship-channel-has-no-expression-guardians-is-not-a-selector) applied to an operand that named a channel instead of a set, and [D-152](round-21.md#d-152--zero-is_system-columns-what-protects-a-vocabulary-is-its-table-not-a-flag-on-its-rows) applied to the
rows of a vocabulary. `scripts/check-registries.py` will not apply it, so it is written in the page that owns each
column. **Schema impact: one value leaving one column.** The dead name is registered in
[removed concepts](../appendix/removed-concepts.md).

---

## What this round cost, and what it did not close

**One question out of the whole batch was already answered.** `F-27` is recorded above against
[D-146](round-20.md#d-146--an-outbound-call-is-a-persons-act-or-a-job-and-nothing-about-it-is-designed-yet)
and mints nothing. It is not the fourth question this corpus has found already-settled in the way
[D-169](round-22.md#d-169--an-imported-membership-ends-with-the-calendar-year-it-was-seen-in)
described, and the reason it slipped through is narrower than that finding and worth its own sentence: **the
question was drafted from the register's live section and the answer was in the register's answered table, on the
same page, two hundred lines apart.**

**Three answers changed shape while being given, and each is recorded where it landed rather than tidied.** A
reporting column became a grammar column ([D-174](#d-174--persongender-is-how-the-system-declines-a-verb-and-it-is-required)),
which forced a second entry about an erasure it had not occurred to anyone to ask about
([D-175](#d-175--an-erased-persons-grammatical-form-goes-with-their-names)); a document issued by the payee became a
document requested by the payer ([D-187](#d-187--an-invoice-is-a-document-a-payer-asks-for)); a yes-or-no about
discounts became a capability, and the capability became the death of a column
([D-183](#d-183--a-changed-ask-is-a-voided-request-and-a-new-symbol-and-amount_discount-goes)). None of the three
was foreseeable from the question, which is the argument for asking questions in a register rather than answering
them in a summary.

**And one entry nobody was asked for.** [D-192](#d-192--proposed_by-loses-import_job-because-a-vocabulary-value-is-a-claim-about-who-can-write) is a value in one enum, and it arrived because
the page that listed it was opened to be swept rather than to be asked about. **Every round of this size leaves
residues of exactly this shape**, and the honest note about it is that a round which only asks registered questions
never finds them: the register held twenty-one questions and closed twenty-one, and the thing that was actually
broken was found by reading a field table.

**The count this page will not claim.** [Round 22's repair](round-22.md) ended by refusing to print a per-file
sentence count it could not point a program at, and that refusal is the habit this entry inherits: the numbers in
this round that are verifiable are the ones a script can produce, and they are these: **twenty-two decisions** on this
page (counted from its own headings); **one page deleted**; **three tables deleted** (`import_batch`,
`staging_import`, `staging_import_row`) **and one added** (`invoice`); **four permission codes removed**
(`import.view`, `import.stage`, `import.apply`, `import.revert`) **and two added** (`payment.match`, `invoice.issue`);
**one actor label removed** (`import_batch:<id>`, six to five); **three column names deleted** — `person.notes`,
`fee_obligation.amount_discount`, and `import_batch_id`, which was written into 12 rows of eight field tables before
it went; and **two vocabulary values deleted** (`unknown` from `person.gender`, `import_job` from
`match_proposal.proposed_by`). **The sentence printed here for an hour said twenty entries, one column and two
tables, and every one of those three figures was wrong** — twenty-one decisions when it was written and twenty-two
now, three columns, three tables — which is the same failure this paragraph exists to describe, reproduced inside
the paragraph describing it. The figures above name what counted them so the next reader can re-produce them.
the number of sentences swept across the corpus is deliberately not stated anywhere in these documents, because the
last round's was wrong every time it was measured.

**What is still open when this closes.** [`F-11`](../open-questions.md#f-11--does-the-identity-reviewer-need-to-read-the-person-record-to-settle-a-claim) — whether the identity reviewer needs
to *read* a person record to settle a claim — stays open on its own recommendation, and nothing in this round
touches it; its recommendation is to watch a queue rather than redesign around a guess, and the queue it means is
produced by the sign-up collision path, not by the import that has just been deleted. The legal review is still four
policies and now also owns the invoice's contents
([D-187](#d-187--an-invoice-is-a-document-a-payer-asks-for)). The wire in and the wire out are still undesigned.
And [D-188](#d-188--the-ceiling-reads-a-grant-and-nothing-else-and-what-it-leaves-open-is-written-down) has left a
widening path open on purpose, with the sentence about it in the pages that describe the ceiling so that the next
reader finds the statement rather than the hole.

**A gate this round wrote, and which is deliberately not a decision.** This page's own figures are above, and they
were measured; the sentence that broke was in a different page and the sweep missed it. The decision index says in its own
introduction how many decisions it indexes; that number was one short of its own rows from the moment
`D-192`'s row was added, and it survived every gate this round ran — `scripts/check-registries.py` reads names, and
`mkdocs --strict` reports a document with a stale figure in it as a successful build. So round 23 wrote
`scripts/count-decisions.py`, which counts the entry headings, counts the index's rows, reads every sentence outside
the history pages that states a total, and exits non-zero when the three disagree. Closing a round now means running
it beside `check-registries.py` and the documentation build. It is not a decision because it changes nothing about the system being designed: it is a
script, it can be deleted by anybody who finds it cheaper to count by hand, and no ruling depends on it. What it
cannot do is check a figure it was not written for — the count of rows on
[the invariant register](../data-model/00a-invariant-register.md) that drifted for three rounds is still checked by
nobody but the next reader who counts, which the page itself now says.

**One hazard found in the existing tooling while doing this.** `scripts/check-registries.py` has an
`--update-baseline` flag that rewrites `scripts/registry-baseline.txt` from scratch, which deletes the file's header
and the reason after every `#` — and that header says a reason is the record, not a comment. It also drops lines
whose finding has stopped firing, silently, which is the one useful thing it does. Round 23 ran the flag, lost the
file, and got it back by saving the diff and reversing it:
`git diff -- scripts/registry-baseline.txt > /tmp/bs.diff`, then `git apply -R /tmp/bs.diff`. **The flag should not be run
inside a round:** add or delete the baseline's lines by hand, keeping each reason, and if a bulk edit is wanted, run
the script against a scratch copy of `docs/` and copy in what was measured.
