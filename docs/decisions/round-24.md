# Decision Log — Refinement round 24 (D-193 … D-205)

> **This is the last round the register asks for.** [Open Questions](../open-questions.md) opened it with three
> questions on the page — [A-4's remainder](../open-questions.md#a-4-remainder--the-organizational-calendar),
> [F-11](../open-questions.md#f-11--does-the-identity-reviewer-need-to-read-the-person-record-to-settle-a-claim)
> and [K-10](../open-questions.md#k-10--are-the-money-permission-codes-still-deferred) — and it closes with none.
> The rest came from the module pages' own `## Open issues` lists, which is where the last answerable questions
> actually lived — a register that is down to three rows is not a design with three questions left, it is a design
> whose remaining questions have stopped being filed in one place;
> **and [D-205](#d-205--there-is-no-legal-review-and-assumption-49-is-retired)
> deletes the thing the register said this repository still owed**, on the ground that the review it pointed at is
> not going to happen and a design should stop writing cheques it has decided not to cash.
>
> **Three answers changed shape while they were being given.** A question about whether one role may read one
> record came back as a requirement that permissions depend on each other, which is a rule about the whole
> vocabulary and is answered as one ([D-194](#d-194--nothing-is-implied-by-a-permission-the-editor-offers-the-companion-read-and-the-database-stores-two-rows)).
> A question about whether the calendar is real came back as **two calendars** rather than one — the membership
> year January to December, everything else September to August — which is a finding and not an answer
> ([D-193](#d-193--the-membership-year-is-january-to-december-the-program-year-is-september-to-august-and-only-one-of-them-is-stored)).
> And a question about a short payment came back as **"attach any payment with matching VS"**, which does not
> settle a shortfall so much as delete the condition that made a shortfall a non-match
> ([D-196](#d-196--the-variable-symbol-is-the-whole-match-what-arrives-under-its-own-symbol-is-attached-in-full-and-the-difference-is-shown)).
> **One of those three turned around inside its own round:** invoices are compulsory, which is a fact about the
> country this organization is in rather than about this design, and it arrives one answer after the money codes
> were promoted — so [D-197](#d-197--an-invoice-is-compulsory-so-nobody-issues-one-invoiceissue-is-deleted-and-the-asks-write-writes-it)
> deletes one of the codes [D-195](#d-195--the-money-codes-are-shipped-codes-catalog-a-grows-a-money-section-and-catalog-b-10-loses-three-rows)
> had just registered.
>
> **Nothing in this round was asked that a previous round had answered** — which is the discipline
> [round 23](round-23.md) promised after it spent a question on something
> [D-146](round-20.md#d-146--an-outbound-call-is-a-persons-act-or-a-job-and-nothing-about-it-is-designed-yet)
> had already settled. The item that came closest is
> [D-199](#d-199--nothing-leaves-this-system-to-an-accounting-system-and-an-external-one-is-a-later-versions-design),
> the accounting export, which is the outbound direction D-146 and
> [D-164](round-22.md#d-164--nobody-is-told-and-no-page-may-say-otherwise) already refused in general and which
> [the finance page](../data-model/07-finance.md#5-open-issues--the-whole-of-this-document-essentially) had kept
> asking as its own ever since it was written. It is closed as a consequence of those decisions rather than as a
> new one, and it mints no rule about actors.

[Refinement round 23 (D-171 … D-192 ←)](round-23.md) | [All decisions](index.md)

**Where the questions came from, page by page, so a reader can check that nothing was invented.** The register's
whole live list: [A-4's remainder](../open-questions.md#a-4-remainder--the-organizational-calendar),
[F-11](../open-questions.md#f-11--does-the-identity-reviewer-need-to-read-the-person-record-to-settle-a-claim),
[K-10](../open-questions.md#k-10--are-the-money-permission-codes-still-deferred). Then, from the module pages:
[`07-finance` §5](../data-model/07-finance.md#5-open-issues--the-whole-of-this-document-essentially) — its
accounting direction, its jurisdiction half, and its "a payment that does not fit";
[`03` §9](../data-model/03-membership.md#9-open-issues) — the organizational-calendar bullet and the
`outstanding_balance` bullet;
[`domain/03` §9](../domain/03-identity-and-legacy.md#9-open-issues) — the twins;
[`domain/04` §8](../domain/04-organization-structure.md#8-open-issues) — a group's previous name;
[`04` §7](../data-model/04-relationships.md#7-open-issues) — `custody_arrangement`;
[`07a` §13](../domain/07a-capacity-presence-and-forms.md#13-open-issues) — its one unsettled item, whether the
audience editor should warn about a bound operand, which came back as a question about the rule itself and is
answered *keep the rule, change nothing*
([D-203](#d-203--a-bound-operand-stays-illegal-at-the-unit-and-the-reason-is-the-granters-ceiling)); and
[`06b` §6](../data-model/06b-redaction-and-checks.md#6-open-issues) with
[assumption 49](../open-questions.md#i-assumption-index) — the legal basis, which turns out to be the sharpest
question in the round and is closed by
[D-205](#d-205--there-is-no-legal-review-and-assumption-49-is-retired) refusing the review it assumes.
**One decision comes from no page at all:** that invoices are compulsory
([D-197](#d-197--an-invoice-is-compulsory-so-nobody-issues-one-invoiceissue-is-deleted-and-the-asks-write-writes-it))
arrived as a fact about the country, volunteered while a different question was being answered, and it is the only
entry here that reversed a decision rather than closing a question.

**What this round does not do.** It designs nothing that was undesigned. Two of its answers are refusals to
design ([D-202](#d-202--there-is-no-twin-and-sibling-procedure-and-the-collision-pair-stays-a-persons-judgement),
[D-203](#d-203--a-bound-operand-stays-illegal-at-the-unit-and-the-reason-is-the-granters-ceiling)) and one is a
deferral with a date on it rather than a decision
([D-199](#d-199--nothing-leaves-this-system-to-an-accounting-system-and-an-external-one-is-a-later-versions-design)).
Its schema effect is **two columns and one permission code deleted, and no column added**.

**And an empty register is not an empty corpus, which this round says out loud rather than implying.** What it
closed was what [the register](../open-questions.md) carried, plus the module questions that pointed at a register
row; the module pages keep their own `## Open issues` lists — **sixteen pages carry one, a hundred bullets between
them** — and anything in such a list that this round did not answer stays open and keeps asking.
[`05d` §13](../data-model/05d-invariants-and-seed.md) and
[catalog B §12](../appendix/permission-catalog-b-roles-and-open-issues.md) hold the longest of those lists, and
neither was this round's to answer. **The register being at zero therefore
means one thing precisely: nobody is waiting on an answer from outside the design.** It does not mean the design
has no open questions, and a reader who concludes that from a zero has misread what the number was ever for. Where
a module list still asks something, the asking page is the register for it — that is the arrangement
[the register's own header](../open-questions.md#how-to-answer) now states.

---

## D-193 — The membership year is January to December, the program year is September to August, and only one of them is stored

**Status:** decided (from your answer) — closes
[A-4's remainder](../open-questions.md#a-4-remainder--the-organizational-calendar), the last row of § A and the
oldest open question in the register, and answers the first bullet of
[`03` §9](../data-model/03-membership.md#9-open-issues) and of
[`domain/05` §9](../domain/05-membership-lifecycle.md#9-open-issues).

**The answer, as given.** *"The membership is always jan–dec, while rest of the activities (such as
person_group) will be from sep–aug, however, those are not hardcoded anywhere anyway."*

**The rule.** There are **two years** in this organization and they do not agree. The membership year runs
1 January to 31 December, and it is stored — `expiry_month`, `expiry_day` and `renewal_grace_days` on the single
[`membership_type` row](../data-model/03-membership.md#1-membership_type--one-row-kept-as-a-table), which is the
way [D-047](round-04.md#d-047--the-fee-expires-on-1-january) and
[D-048](round-04.md#d-048--the-renewal-window-is-60-days-and-is-a-configuration-parameter) left them and the reason
both numbers can move with an `UPDATE`. The **program** year — a group's term, a camp season, the collections —
runs September to August, and it is stored **nowhere at all**: not a column, not a constant, not a rule, not a
check. A `person_group` gets the `valid_from` and `valid_to` a person types
([D-098](round-10a.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority)), and those
two dates happen to fall in September and August the way they happen to fall anywhere else.

**Why the "not hardcoded anyway" half is the answer, and not a caveat.** It is the whole answer. The question on
the register was whether 1 January is *this organization's* date or a date a database liked, and the answer is
that it is a real date for a real thing — the fee, the membership, the renewal — and that the things which run on
the other calendar were never dated by the design in the first place. So there is nothing to change and nothing
to add, and what the register was missing was not a number but the fact that its own question assumed one year
where the organization has two. **[D-169](round-22.md#d-169--an-imported-membership-ends-with-the-calendar-year-it-was-seen-in)
stands untouched for the same reason:** it rules the *membership* half, and the membership half is the calendar
year. Had the answer been "the year turns in September", that decision's stored `valid_to` of 1 January would have
had to be restated as an organizational year, and every inferred historical end date with it.

**What this changes.** Nothing in a table. Three pages gain the two-calendar fact where a reader would otherwise
assume one: [A-4's row](../open-questions.md#a-4-remainder--the-organizational-calendar) closes as confirmed
rather than as answered, [`03` §9](../data-model/03-membership.md#9-open-issues) keeps the discipline half of the
question — *do these values come from the row?* — because that half was never about the date at all, and
[`domain/05` §6](../domain/05-membership-lifecycle.md#6-renewal-and-the-yearly-fee) says plainly that a renewal
date in November and a term sheet in September are the same organization keeping two books.

**What it costs, said plainly.** A report that asks "how many members did the 2026 year have" and a report that
asks "who was in a group in the 2026 year" answer about overlapping-but-different periods, and no column anywhere
says which of the two a reader meant. That is the price of a program year with no representation, and it is the
price this design has been paying since
[D-097](round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row) stopped dating bodies at all.
The alternative was a calendar table or a second set of columns on a group, which would have made September a
fact the model asserts about groups that hold no dates in common — the same invention
[D-095](round-09.md#d-095--units-carry-no-restrictions-joining-one-is-somebody-elses-act) refused for money and
restrictions.

**The discipline that outlives the question.** Both numbers are read from the row or they are wrong: no job, no
front end and no report may hold the literal `60` or the literal `1`. That sentence was already the surviving half
of A-4, and this entry keeps it, because
[D-186](round-23.md#d-186--membership_type-is-settings-wearing-a-vocabularys-clothes) moved this table's defence
onto the calendar the row carries and a compiled-in number is the one way to lose it.

---

## D-194 — Nothing is implied by a permission: the editor offers the companion read, and the database stores two rows

**Status:** decided (from your answer) — closes
[F-11](../open-questions.md#f-11--does-the-identity-reviewer-need-to-read-the-person-record-to-settle-a-claim),
and rules the thing F-11's answer opened.

**The answer, as given.** *"The permissions should have dependency, so let's implement that. Some grants (write)
do not make sense without others (read). I want to add a permission dependency where necessary (either by
auto-inheritance, or by forcing the other ones to be present for the new one to be added)."* Asked which of the
two, the answer was **neither**: *editor convenience only*, and *not at save*.

**The rule.** **A permission implies nothing.** `person.merge` does not carry `person.view`, the resolver never
reads a dependency, and a grant answers the one code it names — which is
[D-099](round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality) unchanged,
[D-068](round-05.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle) unchanged, and the
deleted prefix match still deleted. **What is added is one screen behaviour:** where a code is a `write` and the
same resource has a `read`, the editor that saves the grant offers to save the read grant beside it. Taking the
offer writes **two rows**, each naming one code, each with its own grantee, scope and period, each with its own
`granted_by` and its own audit row. Declining it writes one.

**Where the pairing lives, and why not in a table.** Next to the code, in program text, on
[D-177's](round-23.md#d-177--the-list-of-login-methods-is-written-in-the-program) side of the line: the rule the
corpus adopted is that a list becomes a row when the organization may decide it, and no organization gets to
decide whether reading is a different act from writing. The pairing is also **almost derivable** from what is
already registered — `permission.right_kind` says `read` or `write` and the code's first segment names the row —
so the offer is `<resource>.view` whenever that code exists, and nothing at all when it does not. Four cases are
named rather than derived, because their read is not the same resource's `.view`: `person.merge` and
`person.unmerge` offer `person.view`; `payment.match` offers `payment.view` and `fee.view`; `event.presence.mark`
offers `event.answer.view` beside the roster it marks; `membership.request.approve` offers `membership.view`.
**No table, no column, no migration, and no gate reads any of it.**

**Why not auto-inheritance, which was the other half of the offer.** Because an implied permission confers what
no row names, and three rulings say that cannot happen.
[D-163's](round-22.md#d-163--a-grant-may-not-confer-more-than-the-granter-holds) granter's ceiling reads a grant and,
since [D-188](round-23.md#d-188--the-ceiling-reads-a-grant-and-nothing-else-and-what-it-leaves-open-is-written-down),
**nothing else** — a grant that also carried its read implicitly would give away a code the granter may not hold,
and the check would not see it happen. [D-110's](round-13.md#d-110--the-expression-is-the-record-of-whom-a-grant-reached)
record is the expression, and an implied code is not in it. And the question these documents get asked — *what may
this person do?* — is answered today by listing rows, which is the property
[D-151](round-21.md#d-151--creating-an-event-writes-the-events-authority-and-its-organizers-may-grant-on-it) spent
twelve rows per event to keep. The catalog already suspected this before it had a rule: `membership.terminate`
carries the sentence *"it must not be implied by `membership.lapse`"*, and until this entry that prohibition rested
on nobody having proposed implication. **Now it rests on a ruling.**

**Why not a save-time refusal either, which is the option that would have worked.** It was offered, with a
strictness question attached, and the answer was *not at save*. It is worth recording what was declined, because
it was the version that would have closed F-11 outright: a rule refusing an allow for a `write` code whose grantee
holds no live allow for its read. It would have had a real hole in it — the grantee of the two rows is rarely the
same row twice, and deciding whether two expressions reach the same people is the containment question
[D-105](round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other) refused to make
computable — but the reason it is not here is that it was not chosen, not that it could not be built.

**What this changes, and what it does not reach.** [Catalog B §11](../appendix/permission-catalog-b-roles-and-open-issues.md#11-roles--worked-examples-of-writing-one)
writes its worked-example identity reviewer with **`person.view` beside `person.merge`**, and says in one sentence
that the author chose it and no rule put it there — because an installation copies the example, and a reviewer who
cannot open either record spends the first week asking somebody else to look. That is the practical half of F-11
and it is answered there, not in the model. **What the offer does not reach**: an `api_key` holder writing a grant,
a migration, and the twelve rows an event create writes. Those write what they write, and a reviewer office built
by one of them can hold `person.merge` and no read. **Nothing refuses it, nothing lists it, and no report will
ever show it** — which is the cost of "editor convenience", and it is on the page rather than in a footnote.

---

## D-195 — The money codes are shipped codes: catalog A grows a money section, and catalog B §10 loses three rows

**Status:** decided (from your answer) — closes
[K-10](../open-questions.md#k-10--are-the-money-permission-codes-still-deferred), and the decision that makes the
finance module's money path point at something registered.

**The rule.** Money codes are **codes**. They are documented in
[catalog A](../appendix/permission-catalog-a-codes.md) the way every shipped code is documented — a row in the
`Code | Namespace | Sens. | Grants` table, and behind it a `permission` row carrying the `applies_to` the grant save
checks and the `right_kind` that is `read` or `write` because that column is a guardian's answer and not a hint —
and they are deleted from
[catalog B §10](../appendix/permission-catalog-b-roles-and-open-issues.md#10-deferred-namespaces), which is the
page that calls them "placeholders for features you have not specified". §10 keeps what is genuinely unbuilt:
`document`, `consent`, `message`, `partner`, and the whole `report` row. The sentence in its `payment` row asking
whether the row is still honest as a deferred namespace is deleted with the row, because it was not.

**Which codes.** Six: `fee.view`, `fee.create`, `payment.view`, `payment.record`, `payment.reverse`,
`payment.match`. **`invoice.issue` was promoted by this answer and deleted by the next one**
([D-197](#d-197--an-invoice-is-compulsory-so-nobody-issues-one-invoiceissue-is-deleted-and-the-asks-write-writes-it)),
so the section documents six and not the eight this question was asked with. That ordering is recorded rather than
tidied, because it is the clearest evidence in this round that the module was designed ahead of the answers.

**And where the promotion stops: not one report code ships, including the money one.** `report.finance.view` was in
the list K-10 named, and it stays in §10, because promoting it would have answered a **different** question by
accident. [`05d`'s rules list, §12](../data-model/05d-invariants-and-seed.md#12-what-day-one-looks-like) states that
reporting ships coarse on purpose — only `report.view` and `report.export` exist — that whether reporting is
per-report or one permission with row-level filtering is **still open**, and that **an installation must not ship
both shapes; pick one when reporting is designed**. Catalog B §12 carries the same question as its own open item.
K-10 asked whether *the finance module's* codes are still deferred; it did not ask whether reporting's shape is
decided, and it is not. **So the money rows are gated by `fee.view` and `payment.view`, which is the shape this
vocabulary already has — a code per row-set — and the report that reads them across subjects waits for the shape
question like every other report does.** [`07-finance` §5](../data-model/07-finance.md#5-open-issues--the-whole-of-this-document-essentially)
loses `report.finance.view` from the list of codes it calls its own, and gains the reason: **the module can spend
six codes and not the seventh, and the seventh is not this module's to decide.** The catalogue question is
unanswered by this entry and stays where it is filed — which is what makes
[D-138](round-20.md#d-138--one-permission-guards-the-whole-audit-trail-and-the-widening-is-on-the-record)'s
one-code-for-the-whole-trail ruling the only report-shaped decision in the corpus, rather than one of two
contradictory ones.

**What changes.** A grant over money has something to be checked against besides a worked example: `applies_to`
says which scope shape each code may sit on, and
[the grant save](../data-model/05-authorization.md#what-is-refused-when-a-grant-is-saved) refuses one that does
not match. Catalog B §11's `treasurer` office — the one worked example that spends money, and the only one —
stops holding six codes that named no register row, which is what made §10 dishonest rather than merely
optimistic. **It gained `payment.match` and is now seven rows, six of them registered**, and the page's own
sentence saying the office "cannot be written today" retires with them.
[`07-finance` §5](../data-model/07-finance.md#5-open-issues--the-whole-of-this-document-essentially) loses the
paragraph that said its codes are registered nowhere. And `scripts/check-registries.py`, which reads the
registries out of the pages, now finds money codes in the same register as everything else — a code-shaped money
token in prose is news from here on, and an unregistered one is a finding.

**What it costs.** Six rows nobody wrote before this round, each with an `applies_to` somebody has to get
right, and a section in an appendix that an installation may never grant any of — the disposition D-055 chose
says an unused row costs nothing, and this entry spends it on the record rather than on a placeholder.

---

## D-196 — The variable symbol is the whole match: what arrives under its own symbol is attached in full, and the difference is shown

**Status:** decided (from your answer) — answers item 3 of
[`07-finance` §5](../data-model/07-finance.md#5-open-issues--the-whole-of-this-document-essentially),
and narrows what "money that cannot be matched" means since
[D-180](round-23.md#d-180--there-is-no-queue-for-money-that-does-not-fit).

**The answer, as given.** *"Attach any payment with matching VS, show the difference in the UI
(under/overpayment)."* Asked what that means for the case the module calls the normal one — one transfer of
1 100 Kč against one child's symbol, on a camp ask of 550, with a second child who also has an ask — the answer
was **attach it all, show the over**.

**The rule.** A bank row is attached automatically when **its variable symbol resolves to a live request**, and
it is attached **in full**. The amount is not a condition of the match and never becomes one; it is information,
and the information is shown. `system:bank-pull` writes the `payment`, the link, and the allocation that carries
the whole amount — the rows are the fetch's own, exactly as [D-182](round-23.md#d-182--matching-money-is-a-code-of-its-own-and-the-automatic-half-is-systembank-pulls)
ruled, because resolving a symbol is not a human act. What stops a match is **the symbol and nothing else**: no
symbol, a symbol no request carries, or a symbol whose request has been voided. Those rows are still §2b's, and
[D-180's](round-23.md#d-180--there-is-no-queue-for-money-that-does-not-fit) no-queue answer is unchanged about them.

**The three consequences, in the order they hurt.**

1. **`partially_paid` becomes reachable by itself.** It used to be a value a row could only reach through a hand
   allocation. Now 500 Kč against a 550 ask attaches, the obligation's `amount_paid` reads 500, the status
   arithmetic reads `partially_paid`, and the balance is 50 Kč
   ([D-159](round-22.md#d-159--the-status-enum-keeps-three-of-its-seven-values) keeps its three values and
   `due_date` stays the only place lateness lives). **No tolerance is introduced anywhere**: 4,90 against 5,00 is
   a shortfall like any other, and a threshold would be a number nobody can defend and everyone would have to
   remember.
2. **An obligation can be paid too much.** The 1 100 transfer lands entirely on one child's obligation, which
   then reads **550 over**. `status` still reads `paid` — it is arithmetic about how much arrived, and there is no
   fourth value and no credit concept. The surplus is not a new kind of money: it is an allocation a person moves
   with `payment.match`, whose *split* outcome already exists for exactly this shape.
3. **The membership gate does not move.** A fee is settled when no obligation attached to it has a positive
   balance, so a short payment settles nothing and a long one settles everything. That is the same test
   [D-157](round-22.md#d-157--there-are-no-hardship-waivers) and
   [D-159](round-22.md#d-159--the-status-enum-keeps-three-of-its-seven-values) left, read through the one definition
   in §3 — and, from [D-200](#d-200--membershipoutstanding_balance-is-deleted-and-the-balance-is-the-one-definition-it-was-copied-from),
   read through no column at all.

**What this costs, and it is the interesting part.** The family case is now mis-attributed **by the automatic
half**, silently and on the module's own normal path: the child whose symbol was used looks paid to the sum of
1 100, the sibling looks unpaid, and nobody is told because
[D-164](round-22.md#d-164--nobody-is-told-and-no-page-may-say-otherwise) forbids telling. This is the shape
[D-076](round-06.md#d-076--money-that-cannot-be-matched-waits-for-a-person) refused an identity fallback over —
"*a parent with two children pays one amount against one symbol* is the normal case, not the edge case, and a fee
recorded against the wrong child is a finance error and a membership that appears paid when it is not" — and the
refusal **stands**, because it was about resolving a *failed* symbol by guessing a payer, and here nothing is
guessed: the payer's own bank carried the symbol the organization printed. What changed is which mistake the
system makes on its own. It no longer leaves the family's money with no subject, which was the old failure and a
slower one; it now puts all of it somewhere visible and wrong, and the thing that catches it is **a person
reading an obligation that says +550**, or the family being asked. [`07-finance` §2b](../data-model/07-finance.md#2b-money-that-cannot-be-matched)
states this as the trade and does not soften it.

**"Shown" is the word this entry has to be exact about, because the answer said *show the difference in the UI* and
this design cannot promise what that sounds like.** Nothing is sent and nobody is told:
[D-164](round-22.md#d-164--nobody-is-told-and-no-page-may-say-otherwise) forbids the sentence, and
[the overview](../README.md) is plain that notifications stay **genuinely undesigned** rather than deferred — so
there is nothing in this design that could tell a treasurer about an overpayment, even if a page wanted to. **There is also no screen that lists these rows, and none was promised:** reporting ships coarse, with
`report.view` and `report.export` and no per-module report code, and the code that would have gated a money
exception report is the one [D-195](#d-195--the-money-codes-are-shipped-codes-catalog-a-grows-a-money-section-and-catalog-b-10-loses-three-rows)
left deferred on purpose. What "shown" therefore buys, in full: the `payment` row holds the whole amount, the
allocation holds the whole amount, the obligation's computed balance reads **+550 through the one definition
[D-200](#d-200--membershipoutstanding_balance-is-deleted-and-the-balance-is-the-one-definition-it-was-copied-from)
leaves**, so any screen that reads a balance reads the difference; and the two allocations sit side by side in the
list somebody opens when they hold `payment.match` and are moving money by hand. **What closes the gap between
*visible* and *seen* is a person who opens that list, and nothing else** — no flag, no exception queue, no job.
This round chose the silent mis-attribution over the queued one; it should be read as knowing what it bought.

**What this changes elsewhere.** §2a step 6 becomes the whole rule instead of a conditional with an amount in it;
§2b's list of reasons a transaction has no match loses "the amount is less than asked, or more", which was a
fifth of that list and the largest of its entries; the unmatched population narrows to money with a missing,
unknown or dead symbol, which makes
[D-180](round-23.md#d-180--there-is-no-queue-for-money-that-does-not-fit)'s cost paragraph — a camp transfer that
sits unattributed forever with no list anywhere — true of fewer rows and no longer true of a family's part-payment;
and §4a's check that counts a payment whose allocations do not account for its amount has to say for the first
time that an **unmatched payment has no allocations on purpose**, or it reports the designed absence as a breach.

---

## D-197 — An invoice is compulsory, so nobody issues one: `invoice.issue` is deleted, and the ask's write writes it

**Status:** decided (from your answer) — amends
[D-187](round-23.md#d-187--an-invoice-is-a-document-a-payer-asks-for),
and deletes one of the codes
[D-195](#d-195--the-money-codes-are-shipped-codes-catalog-a-grows-a-money-section-and-catalog-b-10-loses-three-rows)
registered one answer earlier.

**The answer, as given.** *"Invoices are compulsory."*

**The rule.** Every `payment_request` has an `invoice` over it. Always, in every installation, without anybody
being asked, because the country this organization is in requires the document. The invoice row is written by **the
same write that creates its request** — one transaction, one actor, `issued_at` and `issued_by` read off that
write, one audit payload covering both rows. **`invoice.issue` is deleted.** There is no act left for it to
authorize: no screen offers a choice about producing an invoice, no row exists in a state of *awaiting one*, and a
permission nobody can decline is not a permission.

**This reverses the round that added the table, and says so.** [D-187](round-23.md#d-187--an-invoice-is-a-document-a-payer-asks-for)
is titled *"An invoice is a document a payer asks for"*, and its rule was that the row exists **only because a
payer asked** — the module's own line is *"A request is not an invoice… An invoice is a separate row over the same
ask, written only because a payer asked for it."* That clause is deleted, with the sentence two lines below it that
depended on it: *"Most obligations have no invoice at all, and no report is planned over the requests that have
none."* The set of requests without an invoice is now empty **by construction**, which retires the alternative
that entry left on the page — *"if invoices are asked for often enough that forgetting one is a real failure, the
fix is a report over the requests that have no invoice, not a status on the request"* — because there is nothing
left to report. **What survives untouched is the part that was not about the asking**: the request still does not
*become* an invoice, the two rows keep their own numbers, and the sharpest line in D-187 still reads exactly as it
was written — *a symbol resolves a payment to an ask, a number identifies a document to a tax authority, and
nothing promises the two agree.* D-187 even named this answer in advance: *"If this country turns out to require
invoices of somebody, the answer is this table, not a renaming."* It turns out to. The table is the answer. The
renaming did not happen.

**One sentence in D-187 changes meaning rather than disappearing.** Its list of what a `payment_request` lacks —
*"no tax identity, no legally-required sequence, no delivery record"* — keeps two of its three clauses and loses
the middle one. **The invoice's sequence is now legally required**: `number` is unique and never reused, which was
hygiene when an invoice was a courtesy and is a legal fact now that one is a document. The request itself still has
no tax identity and no delivery record, and that is still true for the same reason
[D-164](round-22.md#d-164--nobody-is-told-and-no-page-may-say-otherwise) gives — nothing here delivers anything.

**The queue argument gets stronger, and keeps its shape.** D-187 refused a `requested` status because a column
meaning *somebody owes this person a document*, with nobody assigned to it and nothing counting it, is
[D-180's](round-23.md#d-180--there-is-no-queue-for-money-that-does-not-fit) queue wearing a coat. Compulsory
invoicing does not add the column and does not need one: **it deletes the debt.** The invoice's rule of *"no state"*
stands word for word, now for the stronger reason that there is no moment at which a document could be missing.

**What happens to a wrong invoice.** [D-183's](round-23.md#d-183--a-changed-ask-is-a-voided-request-and-a-new-symbol-and-amount_discount-goes)
rule unchanged, extended by one row: the ask is voided and reissued, and the voided request keeps its invoice —
*"a voided request keeps its invoice. Both rows are permanent"* is still true and now fires on every reissue
instead of almost never. The reissued ask gets a new invoice with a fresh number from the same sequence, and the
old number stays retired, because a number a tax authority has seen cannot be handed to a second document.

**Which write, exactly, since the code is gone.** `fee.create`. The money family this round registers has one code
that writes the asking side of the model — an obligation and the request over it — and the invoice joins that same
write rather than getting a code of its own, so the module has no money row whose write is ungated.

**What this costs, and it is a real loss rather than a rounding.** [D-187](round-23.md#d-187--an-invoice-is-a-document-a-payer-asks-for)
bought a separation on purpose and named it: `invoice.issue` was *"deliberately separate from `payment.match` so
that the person who can settle a transfer is not automatically the person who can sign a tax document"*, and catalog
B repeated it — *"the person who may type in a number is not automatically the person who may produce a document
with a legal shape."* **That separation is gone.** Whoever holds `fee.create` now produces tax documents as a side
effect of recording what somebody owes, and no code, no check and no report distinguishes the two acts any more. The
control left is the one
[D-188](round-23.md#d-188--the-ceiling-reads-a-grant-and-nothing-else-and-what-it-leaves-open-is-written-down)
left standing everywhere else in this vocabulary: `fee.create` is rare because somebody granted it, once, in the
open — and if that turns out not to be enough, the repair is a sentence about who may hold `fee.create`, not the
code back. There is also the ordinary cost of automation: the sequence advances for documents nobody handed to
anybody, and a request voided five minutes after it was written leaves a voided invoice behind forever in a table
that, unlike the audit trail, has
[no end date at all](round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short).

---

## D-198 — An invoice's issuer is configuration; its payer's identification is already in the database

**Status:** decided (from your answer) — closes the jurisdiction-and-paperwork half of item 2 of
[`07-finance` §5](../data-model/07-finance.md#5-open-issues--the-whole-of-this-document-essentially).

**The answer, as given.** *"There MAY be an external system added in later versions, however it will not be
designed in this documentation (as already stated), please close this now."* — asked directly, in the same batch,
who the invoice says it is from and what happens after it is issued: **configuration**, like the login methods, and
anything beyond issuing the document is discharged outside the system.

**The rule, in three parts.**

1. **The issuer is deployment configuration.** The organization's name, address, IČO, DIČ and bank account are
   not in a table. There is no `unit` row to hold them
   ([D-097](round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row) deleted the unit as a row),
   there is no `organization` table, and adding one to print a header would be the same invention
   [D-177](round-23.md#d-177--the-list-of-login-methods-is-written-in-the-program) refused for login methods —
   a value with one legal value, one installation, and no screen that writes it. It arrives the way the SMTP relay
   and the bank's API credentials arrive: as configuration the deployment supplies, named nowhere in the schema.
2. **The payer's identification is already modelled, and it is rows.** An invoice needs the payer's name and
   address, and for a business payer their IČO and DIČ. [`domain/02`](../domain/02-actors.md#external-identifiers)
   already has the shape: `person_identifier` is a `(scheme, value)` pair, unique among current identifiers, and
   IČO and DIČ are **schemes**, not columns. Nothing is added for the invoice; the invoice reads rows that exist
   for a completely different reason and were designed before this question was asked.
3. **Everything after issuing happens outside.** The invoice exists as a row here. Getting it to the payer, filing
   it, reporting it, and reconciling it with an accountant are acts this system does not perform, does not record
   having performed, and does not have a column claiming it performed.
   [D-164](round-22.md#d-164--nobody-is-told-and-no-page-may-say-otherwise) already forbids the first of those
   sentences being written as if the system did it; this entry forbids the schema implying it.

**What this changes.** [`07-finance`](../data-model/07-finance.md#5-open-issues--the-whole-of-this-document-essentially)
closes its jurisdiction item as *answered by refusing the question's premise*: the module had been asking which
jurisdiction's rules it should encode, and the answer is that it encodes none — it produces a row whose number is
never reused, and the thing that turns that row into a filing is outside the corpus. The one addition is a sentence
wherever an invoice is described, naming configuration as the source of the header, so an implementer does not put
the organization's IČO in a settings table that does not exist.

**What it costs.** An installation with two legal entities cannot have them both, because the issuer is one set of
configuration values and there is no row to choose between. That is a consequence of D-097 that this answer makes
concrete for the first time: **the design supports one organization**, has supported one organization since round
10, and now says so at the one place where being two organizations would have shown up in the data.

---

## D-199 — Nothing leaves this system to an accounting system, and an external one is a later version's design

**Status:** decided (from your answer) — closes the accounting-direction item of
[`07-finance` §5](../data-model/07-finance.md#5-open-issues--the-whole-of-this-document-essentially), the finance
module's own version of
[F-27](../open-questions.md#f-27),
and mints no new rule.

**The answer, as given.** *"There MAY be an external system added in later versions, however it will not be
designed in this documentation (as already stated), please close this now."*

**The rule.** **No export, no feed, no integration, no ledger.** This system does not send anything to an
accounting package: not the invoices, not the payments, not a periodic journal, not a CSV of the day's bank rows.
Everything the money model asserts lives in its seven tables and is read out of them by
the reports a person reaches with `report.view` or by a person with `report.export`. An external accounting
system **may** appear in a later version of this product; when it does, it will be designed then, in a document
that is not this one. **This corpus contains no placeholder for it** — no `export` status, no
`external_reference` column, no `system:accounting` actor label, no deferred namespace, no open question.

**Why this closes rather than defers, when "MAY be added later" is not a no.** Because the question on the page
was not "will there ever be one" — it was "what does this design owe it now", and the answer is nothing. Leaving
the item open would keep the finance module describing a hole that has been answered, which is the failure
mode this round exists to close. The corpus has an exact precedent for this shape of closure:
[D-146](round-20.md#d-146--an-outbound-call-is-a-persons-act-or-a-job-and-nothing-about-it-is-designed-yet)
answered an outbound direction by refusing to design either side of it, and
[D-164](round-22.md#d-164--nobody-is-told-and-no-page-may-say-otherwise) then swept every sentence that implied the
system sends things. **The actor-label list stays exactly where
[`00-conventions §7a`](../data-model/00-conventions.md#7a-what-an-empty-actor-column-means) left it** — the five it
lists, `system:renewal-sweep`, `system:payload-reduction`, `system:log-reduction`, `system:bank-pull` and
`migration:<id>`, of which the third is already the one that deletes — and no accounting label joins them, which is
the concrete thing this deferral costs: **nothing**. An integration added later is an integration that will need its
own label, and needing one is not a reason to reserve it now.

**One cost is worth naming, because it is a cost of the tooling and not of the design.**
`scripts/check-registries.py` reads three registers out of these pages — permission codes, deferred namespaces, and
the dead names in [`removed-concepts.md`](../appendix/removed-concepts.md) — and it has **no register of things the
design has refused to add**. A label that was considered and declined is therefore invisible to the gate: the only
thing standing between this deferral and a future `system:accounting` appearing in a page is this paragraph and the
two module sentences beside it. It is not baselined, because a baseline is for findings the corpus has read and
kept, and there is no finding to keep — the name appears in the corpus solely to say it does not exist, and the
pages that name it were reworded to say *"no sixth actor label"* instead, so the checker stays at zero and cannot
be the thing that remembers.

---

## D-200 — `membership.outstanding_balance` is deleted, and the balance is the one definition it was copied from

**Status:** decided (from your answer) — the recommendation
[`07-finance` §3](../data-model/07-finance.md#3-keeping-membershipoutstanding_balance-honest) has been making
since round 6 is taken, and it closes that section, [`03` §9](../data-model/03-membership.md#9-open-issues)'s
balance bullet, and the second half of [`03` §9](../data-model/03-membership.md#9-open-issues)'s imported-row note.

**The answer, as given.** *"Delete the column."*

**The rule.** The column is gone. There is **one** definition of what is owed, in
[`07-finance` §3](../data-model/07-finance.md#3-keeping-membershipoutstanding_balance-honest), and it reads
`fee_obligation` and `payment_allocation`; every screen, every report, every gate and every API response that shows
a balance reads that definition. The view it was going to be copied into is not created either — the definition is
the view, and a second name for it is a second thing to get wrong.

**Why the recommendation was already the right one and why it needed an answer anyway.** §3's own sentence — *a
wrong balance suspends the wrong child* — was written in round 6 and has survived nine rounds with the column in
place, because deleting a column is a decision somebody has to take and a document can only recommend it. The
column's defence was never accuracy; it was that a membership screen wants a number without joining four tables.
That defence is now answered the way it should have been answered in round 6: a request memoizes
([D-114](round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation)), so the join is
not the expensive thing it was assumed to be when the column was drawn.

**The NULL that was load-bearing, and where it goes now.**
[Assumption 53](../open-questions.md#i-assumption-index) recorded that an imported membership's balance is
**NULL and not zero**, because zero asserts the organization settled a debt it never saw, and
[D-093](round-09.md#d-093--the-one-off-import-may-create-memberships-both-ends-dated) made imported rows
believe things. With no column, that distinction does not disappear — **it moves into the absence of rows**. An
imported membership has no `fee_obligation` underneath it, and the balance definition reading "no obligations"
must keep reading it as *nothing is known*, not as *nothing is owed*, in exactly the places assumption 53 listed:
the gate, the arrears report, and any screen that would otherwise print `0 Kč`.
**The activation gate's behaviour for such a row is unchanged and is now written down rather than inferred:** it
asks whether any attached obligation has a positive balance, an imported membership has none, so the test passes
vacuously — which is correct for the gate (nobody is being suspended for a debt nobody computed) and is *also* what
makes the import check flag an obligation-less imported membership as something to look at. Deleting the column
removes a number that could lie; it does not remove the underlying absence, and it must not be allowed to remove
the sentence about it.

**What this changes.** The field table in [`03-membership` §3](../data-model/03-membership.md#3-membership)
loses the row, including its honest warning that the column was kept "only until that decision is taken" — this is
that decision. §3 loses its three-option table and keeps its definition. Every mention of the column across the
corpus, in the ERD appendices, in the glossary and in the membership lifecycle prose, becomes a pointer to the one
definition. And the column enters
[the dead-name register](../appendix/removed-concepts.md), so a future page that writes `outstanding_balance` is
named by the checker rather than caught by a reader.

---

## D-201 — A group keeps no previous name: this is now a ruling, and not an absence

**Status:** decided (from your answer) — closes
[`domain/04` §8](../domain/04-organization-structure.md#8-open-issues), which was that page's last open question.

**The answer, as given.** *"No, prose is enough."*

**The rule.** A `person_group` has one `name`, it is editable in place, and **no previous name is stored anywhere**
— no `previous_name`, no name-history table, no `name_changed_at`. A group renamed because it took a new patron, or
inherited an older troop's name, carries the fact **in prose the organization writes where it wants it**: on the
group's own description, in its roster's header, in the annual report. Nothing in the schema knows the group ever
had another name.

**Why this is written as a decision when it changes nothing in a table.** Because the page filed it as an open
question, and an open question is a promise that the answer is not yet known. It is known. And this is the second
time this round closes a question by saying *the words are enough* rather than by adding a column:
[D-173](round-23.md#d-173--that-two-groups-are-the-same-group-is-said-not-stored)
ruled that *two groups being the same group* is said and not stored, and wrote the reason this entry inherits —
the choice is recorded "in the page that held the question, rather than left as the silence of a table that has no
column for it". A previous name and a continuity claim are the same kind of fact about the same table, and it would
be incoherent to store one and decline the other. [`domain/04` §8](../domain/04-organization-structure.md#8-open-issues)
keeps its own sentence that if renaming turns out to be common the answer is **a decision, not a column somebody
adds quietly** — that sentence is now the answer rather than the contingency.

**What it costs, including a sharp edge the question had not mentioned.** The audit trail was the fallback and it is
shorter than the organization's memory of its own troops: an edit writes the old string into an `audit_log` payload,
and payloads are
[emptied at 24 months](round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short), so
**a group renamed more than two years ago has no name trail anywhere in this system**. Worse, and this is the part
nobody had said out loud: a group's `name` is unique across
[`person_group`, `role` and `audience` together](../data-model/02-organization.md#1-person_group), so renaming a
group **frees its old name to be taken by a new group, a role, or an audience** — after which a retired name is not
even a stale pointer to the group that wore it, it is a name that may mean something else entirely. The prose that
carries the memory has to name the group in words a reader resolves for themselves, and the design accepts that.

---

## D-202 — There is no twin-and-sibling procedure, and the collision pair stays a person's judgement

**Status:** decided (from your answer) — closes
[`domain/03` §9](../domain/03-identity-and-legacy.md#9-open-issues), the last open item on that page.

**The answer, as given.** *"No procedure."*

**The rule.** Nothing in this design documents how to tell two children apart, and nothing automates it. There is
no disambiguation checklist, no screen that pairs candidates, no check that flags a suspicious merge, no report of
"persons sharing a normalised name and a birth date", and no rule about siblings anywhere. What exists is what
already existed: [D-089](round-07-08.md#d-089--one-live-account-a-colliding-sign-up-files-a-claim-and-creates-nothing)'s
collision path, where a sign-up that matches an existing person **files a claim and creates nothing**, and
[D-176](round-23.md#d-176--google-or-a-password-one-identity-one-account-and-the-invariant-finally-has-a-check)'s
gate, where an account may not reach `active` while an unresolved `identity_hypothesis` names its person on either
side of the pair. A person then reads two records and decides, holding `person.merge`.

**The recommendation this retires, and why it was already true.** The page recommended "yes, and never merge them
automatically". **The second half of that recommendation describes a design nobody proposed**: there is no job, no
match pass and no import that merges anybody — `match_job` writes a *hypothesis*, `proposed_by` says which of
`match_job`, `person` or `staff` raised it
([D-192](round-23.md#d-192--proposed_by-loses-import_job-because-a-vocabulary-value-is-a-claim-about-who-can-write)),
and every merge is a person's write behind a code. So the only live part of the question was the procedure, and the
answer is that the procedure is the reviewer.

**The anti-signal that was put to you, and declined.** The question came with a fact attached: a guardianship row
already records which adults reach which children, so *"these two are reached through the same guardian"* is a fact
this model stores, and a reviewer could be shown it. **Declined.** Nothing reads the shared-guardian fact as a hint,
no screen surfaces it beside a merge, and the design keeps its position that a guardianship row is about authority
over a child and not about kinship — which is the same reason there is no sibling edge. Recording the refusal
matters because it is the cheapest possible improvement to the risk this entry accepts, and a future reader should
find it already considered rather than not thought of.

**What it costs, stated as the failure rather than as an abstraction.** Two children, same surname, same birth
date, one form filled in by the same parent on the same evening: the sign-up collides, the gate holds the account,
and the thing that stops the wrong merge is **the attention of whoever reviews the claim**. If they merge anyway, one
row carries two children — one fee obligation covering a child who is not the one who came to camp, one attendance
mark belonging to the other, one set of attribute answers where a diagnosis for one child is now held about both,
and [D-140](round-20.md#d-140--nothing-about-an-event-is-deleted-on-a-schedule-and-erasure-empties-an-answer-without-deleting-it)'s
erasure emptying answers about a person who is two people. **The undo exists** — `person.unmerge` is why
`person.merge` was ever safe to hand out — but it is safe only while the field conflicts are still legible, and a
merge that resolves cleanly leaves nothing that reads as a mistake. Nothing was added to guard against that, by
this answer.

---

## D-203 — A bound operand stays illegal at the unit, and the reason is the granter's ceiling

**Status:** decided (from your answer) — closes the last unsettled bullet of
[`07a` §13](../domain/07a-capacity-presence-and-forms.md#13-open-issues) as **declined**: no editor warning, no new
label, no change to the rule.

**The question as asked, and the question that came back.** The page asked whether the *audience* editor should warn
that an audience naming `PLACED` cannot be aimed at a unit-scope grant, since the refusal currently lands later, when
somebody saves the **grant**. Your answer was a question about the rule underneath it: *"If I put those on the
system, doesn't it still work when it resolves against a specific item? If I set up an audience `organizers` defined
as `ORGANIZERS`, then when granted the permission `event.edit`, all events' organizers can edit them."*

**The answer to that question is yes — and it already happens, without anyone writing the grant you are imagining.**
An audience named `organizers` whose whole expression is the bare operand `ORGANIZERS` is a legal row, `event.edit`
aimed at it is a legal grant, and it works on every event in the system — because
[D-151](round-21.md#d-151--creating-an-event-writes-the-events-authority-and-its-organizers-may-grant-on-it)
writes it **once per event**, twelve codes beside every event, each an item-scope grant pointing at that audience. At
check time the resolver is handed an item, so a bound operand has something to bind against
([`05c`](../data-model/05c-access-log-and-resolver.md)); the expression never needed the grant to know the item, the
**grant** is what has to be per-item. What stays illegal is the single unit-scope row naming that audience — which is
check 3 of the seven the grant save runs, reading `selector_type.binds_to_item` against `grant_scope_type`
([`05` §6](../data-model/05-authorization.md#what-is-refused-when-a-grant-is-saved),
[`domain/06a`](../domain/06a-audiences-and-selectors.md)).

**Why the rule is kept now that it has been examined, which is the part worth keeping.** A grant's **scope column is
the thing the granter's ceiling reads**. [D-163](round-22.md#d-163--a-grant-may-not-confer-more-than-the-granter-holds),
narrowed by [D-188](round-23.md#d-188--the-ceiling-reads-a-grant-and-nothing-else-and-what-it-leaves-open-is-written-down)
to "reads a grant and nothing else", compares the code and the scope a grant names against what the granter holds.
Let a bound operand sit at unit scope and that row would say *the unit* while meaning *whatever item is being asked
about* — a grant whose reach is decided by a question its own row cannot answer, checked by a ceiling that reads the
row. It is the same reason there is no permission cache
([D-114](round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation)):
this design has already decided that a permission answer is not a fact about a person, it is a fact about a person,
an item and a date, resolved when asked. **The scope column is the part of a grant that does not depend on the
question being asked, and a bound operand in it would make it depend on the question.** Per-item rows are not a
workaround for a missing feature; they are how a scope stays a scope.

**What was declined, and what it will cost somebody.** The editor warning. Somebody will build an audience called
`organizers`, be pleased with it, try to grant `event.edit` with it at the unit, and be refused at the save by a
message about a bound operand — with the explanation two clicks away in
[`domain/06a`](../domain/06a-audiences-and-selectors.md) and nothing at the audience editor saying *this row will
only ever be usable on an item*. That is a real, recurring, small cost, and the answer accepted it rather than
adding a warning that would have to be right about an audience whose expression may name `ORGANIZERS` in one branch
and `MEMBERS` in another, where the honest verdict is "depends on the grant". **The refusal lands on the grant,
which is faithful to the rule** — the page's own sentence, now its verdict too.

**What this costs the corpus rather than a user.** `07a` §13's list keeps the bullet, with this answer written into
it, because a bullet deleted from an open-issues list reads as "still open, we forgot". The twelve-rows-per-event
consequence of the rule is unaffected by this entry either way, which is worth saying plainly, since the question
looked like it might dissolve it.

---

## D-204 — `custody_arrangement` is deleted: a court order is stored here neither as prose nor as structure

**Status:** decided (from your answer) — closes [`04` §7](../data-model/04-relationships.md#7-open-issues), and it
is the second half of a deletion the corpus started in
[D-191](round-23.md#d-191--personnotes-is-deleted-and-the-vocabulary-takes-the-job).

**The answer, as given.** The question was whether to structure the free-text field, with the page recommending *not*
— custody orders vary too much to model, and a wrong model is worse than honest prose. The answer was neither option:
***"Delete it."***

**The rule.** The column is gone. The arrangement a court ordered is not structured, is not prose, and is not stored
anywhere: it is not a flag, not an enum, not a note, and not a second table. What the row keeps is the two people,
the `relationship`, the `right_level`, `lives_with`, `source`, the dates, and the two contact flags
([D-185](round-23.md#d-185--a-guardianship-ends-when-a-party-ends-it-and-majority-is-not-a-party) is the last
ruling on its life).

**The row is not prose-free, and pretending otherwise would be a false claim about the table on the page beside
this one.** Three free-text columns survive on the same row, and the line between them and the deleted one is the
whole of this entry: **`evidence_reference`, `ended_reason` and `ended_note` say something the organization did or
holds — where the proof is filed, why a party ended the row** — while `custody_arrangement` said something about a
child's life that no rule reads. A column recording an act is a record; a column describing a private arrangement
is a copy of it, and copies are what
[D-083](round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data) and
[D-191](round-23.md#d-191--personnotes-is-deleted-and-the-vocabulary-takes-the-job) both refused. If that line ever
blurs — if `ended_note` becomes the place a person types an order because the box is there — this entry is the
sentence that was broken, and it is written here so the breaking is visible.

**Why deleting beats the recommendation the page made.** The page's argument for prose was that a wrong model is
worse than honest prose, and that is true — but the field was already not doing the job its name claims. It is read
by nobody, gates nothing, and cannot be, because
[D-083](round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data) deleted the idea of a
graded category of field, and authority here is an expression over named sets rather than a flag beside a value. A
column that no rule reads and no screen computes from is
[D-191](round-23.md#d-191--personnotes-is-deleted-and-the-vocabulary-takes-the-job)'s argument for deleting
`person.notes` in a smaller size, and it is worse than `notes` in one respect: **a text field named
`custody_arrangement` invites a person to type a court order into a database that cannot act on it**, which is the
worst place for that sentence — sensitive enough to be a problem if leaked, useless enough to be a problem when
needed, and invisible enough that whoever typed it will assume somebody downstream read it.

**What this does to the case the corpus kept naming.** Both
[`04`](../data-model/04-relationships.md) and
[`domain/01`](../domain/01-overview.md) use the same worked example as the design's honest limit: a court order
restricting one parent's access to the health facts about a child while their other access continues — *"a realistic
custody arrangement, and one the model must"* refuse. The refusal stands, and this entry widens it: **until now the
arrangement could not be expressed but could at least be written down somewhere in the row.** Now it can do neither.
Where it lives: the organization's paper file, and the memory of the person it was told to. That is stated here
rather than left to be discovered, because it is the sharpest cost in this round and it belongs next to the deletion
that causes it.

**The audit trail does not soften this.** An edit that deletes the column moves its values into payloads once, and
payloads are emptied
[24 months after they were written](round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short),
so the trail is a two-year trace of a fact the design has decided to stop holding rather than a second copy of it.
The two places the corpus names this column in **past** tense — the sensitive key-name list that
[`00-conventions §8`](../data-model/00-conventions.md#8-personal-data-and-erasure) says it *once* carried, and the
same list's history in the audit page — stay true and are not rewritten; the column joins
[the dead-name register](../appendix/removed-concepts.md) so the checker treats every later appearance of the
identifier as news.

---

## D-205 — There is no legal review, and assumption 49 is retired

**Status:** decided (from your answer) — closes
[`06b` §6](../data-model/06b-redaction-and-checks.md#6-open-issues)'s retention-as-law bullet,
[`domain/03` §9](../domain/03-identity-and-legacy.md#9-open-issues)'s last bullet,
[`07-finance` §5](../data-model/07-finance.md#5-open-issues--the-whole-of-this-document-essentially)'s
legal-direction half, and
[`open-questions` "How to answer"](../open-questions.md#how-to-answer)'s second debt. **It retires
[assumption 49](../open-questions.md#i-assumption-index)** — the only numbered assumption in this corpus that named
a person outside the design as the one who would settle it.

**The answer, as given.** *"Everything is our decision, there will be no review by the law so do not plan for one.
We design the system, everything is my call."*

**The rule.** **There is no legal review of this design, and there will not be one.** No page may say one is
required, pending, deferred, handed, or owed; no section may describe its own content as "the technical mechanism,
not the compliance policy" on the understanding that somebody else supplies the other half; no policy may be filed
as awaiting a basis. Every retention rule, every erasure rule, and every decision about what this system holds about
a child **is a decision of the person designing the system**, taken on the day written beside it, with the risk named
in the same paragraph instead of a lawful basis claimed.

**The five policies this now owns, and what "owns" means for each.** They are the four
[`06b` §6](../data-model/06b-redaction-and-checks.md#6-open-issues) was already counting, plus the one
[D-187](round-23.md#d-187--an-invoice-is-a-document-a-payer-asks-for) left with a lawyer and
[D-197](#d-197--an-invoice-is-compulsory-so-nobody-issues-one-invoiceissue-is-deleted-and-the-asks-write-writes-it)
made unavoidable:

| The policy | The decision, and the risk carried |
|---|---|
| Named `membership` and `fee_obligation` rows are kept **indefinitely**, through and after an erasure request ([D-088](round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)) | Chosen because the alternative falsifies the organization's own history. The risk: it is the one class of row here that outlives every safeguard in [§8](../data-model/00-conventions.md#8-personal-data-and-erasure), and nothing outside the design vouches for it. |
| `audit_log` **rows forever, payloads 24 months**, 12 months the floor a window may be set to | Chosen because a row without its payload answers *who said this* without saying *what*. The risk: two years of a person's record exist in a log that most readers never see. |
| `access_log` **rows deleted** at 24 months ([D-145](round-20.md#d-145--access_log-rows-are-deleted-at-24-months-and-the-job-that-does-it-has-a-name)) | Chosen because a log of every check is the most sensitive table in the system and has no historical duty. The risk: a question asked in year three about a check in year one has no answer — the third hard delete, and the only one a clock runs. |
| A child may hold an account with **no guardian's answer recorded anywhere** ([D-166](round-22.md#d-166--an-account-is-not-where-authority-over-a-child-lives)) | Chosen because a consent checkbox nobody can verify records a decision that was never made. The risk: this is the answer a data subject asks about first, and the design answers it by holding nothing. |
| What an **invoice** must contain, and how long it is kept | Chosen by [D-198](#d-198--an-invoices-issuer-is-configuration-its-payers-identification-is-already-in-the-database): the row is the record that a document exists, the issuer's half of the document comes from deployment configuration, and the requirement to print more than this design holds is met outside it. |

**What "the risk is named instead of a basis" means in practice, since it is the whole of the ruling.** Where a page
used to write *this stands as an assumption pending review*, it now writes *this is what the design does, this is
what could be asked about it, and the person designing it has decided*. That is not a weakening — **it is the
removal of the only thing in this corpus that could have overruled a design choice from outside**, and it should be
read that way. The checks in
[`05d §11`](../data-model/05d-invariants-and-seed.md#11-invariants-to-verify) and
[`06b` §5](../data-model/06b-redaction-and-checks.md#5-integrity-checks) still verify the mechanisms against their
own rules; what no longer exists is a rule those mechanisms could be measured against that anyone outside this
document wrote. A design that has decided its own lawfulness is self-validating, and the sentence saying so belongs
in the section it describes rather than here.

**What this changes, page by page — because this ruling is mostly a wording change, and a wording change that is
left half-done is worse than the sentence it replaced.** Nine live pages carried the review as a fact about the
future of this project, and each is rewritten to carry the decision and the risk instead:
[`00-conventions` §8](../data-model/00-conventions.md#8-personal-data-and-erasure) — item 3's "an assumption pending
review" and the closing blockquote that begins *"Legal review is required before implementing §8"*, which becomes a
statement of who decided and when; [`06b` §6](../data-model/06b-redaction-and-checks.md#6-open-issues) — the
"decided as policy, still open as law" bullet and its count of policies in front of a review;
[`06-audit-and-import`](../data-model/06-audit-and-import.md) where it says the claim "needs a legal basis and a
decision log"; [`07-finance` §5](../data-model/07-finance.md#5-open-issues--the-whole-of-this-document-essentially)
and its invoice rule; [`domain/01` §6](../domain/01-overview.md#6-the-four-decades-of-history) and
[`domain/03` §9](../domain/03-identity-and-legacy.md#9-open-issues) on the same retention claim; [`domain/02` §2](../domain/02-actors.md#minor-registration) on the child's account;
[`05c` §9](../data-model/05c-access-log-and-resolver.md#9-access_log); [`glossary.md`](../glossary.md) where it
glosses the retention pair as having a legal basis; and the register's
[§ I row 49](../open-questions.md#i-assumption-index) plus
[§ I row 3](../open-questions.md#i-assumption-index), whose "falsified" note cites the review as the place the
answer went. **Past rounds are not rewritten** — [round 20](round-20.md) calling the review "the largest unowned
risk in this corpus" and [round 22](round-22.md) counting its four policies stay as they were written, because they
are the record of a belief this round removes, and the register's § R row for assumption 49 is where the removal is
stated. **What no page may say afterwards:** that anything in this design is awaiting verification, that a basis is
outstanding, or that a mechanism is described "while the policy waits".
