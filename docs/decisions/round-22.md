# Decision Log — Refinement round 22 (D-155 … D-169)

> Sixteen questions asked and answered in four sittings, and they came out as fifteen decisions, because one of the answers was taken back by a later one and two of the fifteen are rulings to decide nothing. The money module gave up its currency, its insurance, its waivers, its refunds, four of its seven status values and the question it had been asserting it had asked; the authority model got the one ceiling it had been circling and had, one round ago, written down as untouched; the import's end-date inference got its date from a boundary the register had already answered; and the promise that someone would be told within the hour was taken out of every page that had been making it. **Most of this changes no table.** Nine of the fifteen are a sentence removed, a blank confirmed, or a report named — which is what a module left open for sixteen rounds actually costs you: not structure, but a corpus that keeps saying *unanswered* in a voice nobody reads.

[Refinement round 21 (D-150 … D-154) ←](round-21.md) | [All decisions](index.md)

**What was asked, and where the questions came from.** [Round 21](round-21.md) closed with nothing owed but
five 🟢 questions and a legal review, which was true of the register and false of the corpus. The register
tracks questions about the core design. The module pages had been keeping their own open issues for sixteen
rounds, in sections with no numbers attached and no path in from the page that says how open everything is:
`07-finance.md` §5 is an eleven-item list that opens by calling itself "the whole of this document,
essentially", it registers **no** question in `open-questions.md`, and the register's finance row reports
"nine open questions" without naming one of them. A reader of the register alone would have found **zero**
finance questions in a design whose money module had nine. That gap is the source of D-155 to D-162 and of
three of the four authority answers.

**The finding worth keeping, before any of the answers.** The finance page's counts did not match the thing
counted, twice over. §5 numbered eleven items and said **nine remain open**, which is right — and the sentence
underneath it, the one that names what still needs somebody in the organization to be asked, prints eight. It
lists proration, discounts, insurance, waivers, invoices, accounting and "the two choices question 11 names", so
it counts one item twice while **dropping two**: who may authorize a refund, and currency. Those are precisely
the two this round closed. **A summary that is right above a list that is wrong is worse than a wrong summary**,
because the summary is what a reader quotes and the list is what a reader answers from — nobody ever sat down and
closed item 3, because the page that owned item 3 did not print item 3.

And the question the module asserted about itself twice — in the framing sentence at the top of the page and
again in its *Unspecified* line, both naming the fee **amount** as unanswered — **was not in §5 at all**. The
page had been saying the amount was unanswered while filing no item for it, so nothing could ever have closed it.
D-161 files it as item 12 and answers it in the same act. **A count beside a sentence is a claim, and this is the
second round running in which the claim was the part nobody had checked.**

---

## D-155 — The currency is koruna, and the module's own money path said so

**Status:** decided (from your answer) — [assumption 18](../open-questions.md#i-assumption-index) promoted,
the first row of that index to be *corrected* rather than confirmed.

**Corrects:** `07-finance.md` §2's `Default EUR`, and §5 item 8.

[D-075](round-06.md#d-075--money-arrives-from-a-bank-api-a-payment-is-requested-by-variable-symbol-and-qr-code)
settled that money arrives from a bank API, requested by **variable symbol and QR code**. That is a Czech
bank-account mechanism. The same file's `fee_schedule.currency` said `Default EUR`, and the corpus carried no
other currency anywhere and no second mention of euro at all — so the design had been storing, on four
tables, a currency its own money path could not have delivered. One currency, koruna, and the column stays:
it is required on `fee_schedule`, `fee_obligation`, `payment_request` and `payment`, and D-072 is right that
whether it stays a column is the ORM's business, not this corpus's.

**What this does not buy.** One live currency is not multi-currency deferred; it is multi-currency *refused
for now*, and the column is the only reason that refusal is cheap to reverse. §5 item 8 was
"currency **and jurisdiction**", and only the currency half is answered here. The jurisdiction half goes to
the legal review, which D-166 hands a fourth policy.

---

## D-156 — The fee buys nothing but membership

**Status:** decided (from your answer) — closes §5 item 9.

**Deletes:** the three places the corpus hedged toward cover existing, and with them the last reason a
membership date was ever load-bearing for something other than money.

The fee buys membership. No insurance is bought with it, sold with it, or implied by it, so **no date in this
system is evidence of cover**, and `membership.valid_to` is left being exactly what
[D-040](round-02-03.md#d-040--the-fee-expires-yearly-a-date-tracked-renewal-window-replaces-a-grace-status)
made it: the date the obligation stops being current.

Three sentences were written leaning on the opposite possibility, and all three lose their reason to exist:
§2a's warning that a guessable symbol means money lands in a child's record and "reads as a paid fee, an
active membership, and possibly insurance cover that does not exist"; §2c's wrong-child sentence, "**a fee
recorded against the wrong child is a finance error, a membership that appears paid when it is not, and — if
the fee buys insurance — a coverage record that is untrue, all at once**"; and §5 item 9 itself, which warned
that the softer "still covered during grace" reading D-040 explicitly rejected might be what the
organization actually wanted. That alternative is now not merely rejected but **about a thing that does not
exist**, which is the strongest form a refusal can take.

**What is given up, because it is the interesting part.** This system will never be able to say who was
insured. If the organization buys cover — and most youth organizations of this shape do, separately — the
record of it lives outside, and the in-system answer to *who was there* stays what
[D-147](round-20.md#d-147--presence-stays-on-the-registration-no-clock-of-its-own-no-permission-of-its-own)
said it was: `was_present` on a registration, which is a record of attendance and was never a record of
cover. The second consequence is quieter and better. [D-088](round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)'s
permanently-kept skeleton was already standing on the claim that membership and fee rows are the
organization's own history; this answer stops that skeleton from also being somebody's evidence of
insurability, which is a narrower thing to have to defend in front of the legal review.

---

## D-157 — There are no hardship waivers

**Status:** decided (from your answer) — closes §5 item 10, and with it the finance module's share of
[D-097](round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)'s first loss.

**Deletes:** the `waived` status value, `waived_by`, `waived_reason`, the `fee.waive` code, and the write-path
invariant at §2 that no waived obligation is ever unattributed or unexplained.

No waiver mechanism, at any level of granularity. Where a fee is reduced for a family that cannot pay — if
it ever is — the reduction is a `fee_schedule` row with a smaller amount, or an obligation written with a
smaller `amount_due`, exactly as any other price is written. A reduction therefore stops being a fact about a
person and becomes a fact about a year's pricing.

§5 item 10 was the one place the corpus said a question had got **harder** rather than easier: with no units
there was no smaller scope a waiver could live inside, so a `fee.view` held at the unit reached every
person's money, and all that separated a hardship waiver from general visibility was which codes existed,
who held them, and a deny that "can exclude a named person from a unit grant but cannot carve a private
subset out of one". The catalog's ⛔ note on `fee.waive` said the mark and the grant list were *the whole
control*. **This answer does not build a better control; it removes the thing that needed one.** The need-to-know
process the item described — "must not be visible to every adult who runs a group" — is guaranteed by the
plainest available means, which is that there is nothing to see.

**What is given up, said flatly.** Nothing in this design will ever record that a fee was reduced because a
family could not afford it. Some organizations want that in their books and some refuse to hold it, and this
is the second group, by choice. If the fact is ever wanted, [D-083](round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)
already says where it goes and gives no option about it: a definition in the vocabulary of
[data-model/09](../data-model/09-attributes.md), readable through `person.view` like everything else anyone
knows about a person, with every visibility consequence that implies. It does not go back into a status
column, and that is not a preference — a status column is read by balance arithmetic, which is D-159's whole
subject.

---

## D-158 — A refund happens at the bank

**Status:** decided (from your answer) — closes the half of §5 item 3 that was still open.

**Deletes:** the `refunded` status value and the `fee.refund` code.

Nobody initiates a refund inside this system. The transfer goes out at the bank, and what arrives here is a
record of it: **money out is a `payment` like money in**, written by `payment.record` or found by the bank
import, and the person who recorded it is in the row.

What is notable is that the corpus had already written the rule and then kept a permission for authorizing
its exception. §5 item 3: "a refund is a second payment in the opposite direction, **not a status**, so it
cannot corrupt the original record and there is no reversal state to authorize" — and then the same item
asked who may authorize it, and the file marked `fee.refund` with a lock glyph. **The rule was the whole
design; the code was a leftover from the shape the rule had replaced.** Deleting the code rather than the
rule is what closes the question, and it closes it on ground this corpus uses constantly: the trail is the
control (D-137), a report and a written procedure beat a mechanism (D-126), and a permission for a job implies
a person choosing not to do it (D-125).

**Consequence for cancellation, which was the volume case.** [D-076](round-06.md#d-076--money-that-cannot-be-matched-waits-for-a-person)'s
answer to EV-3 is that cancelling an event voids its outstanding payment requests and that money already
received "becomes a queue item, for a person to refund or to carry forward to a later event". That sentence
is now literally what it always gestured at: **the queue is where the system stops and a person begins**, and
the person's next act is at their bank, not on a screen here. Nothing about the queue's shape changes.

---

## D-159 — The status enum keeps three of its seven values

**Status:** decided (from your answer, together with D-157 and D-158).

**Deletes:** the `written_off` and `overdue` values of `fee_obligation.status`.

`fee_obligation.status` is `unpaid`, `partially_paid`, `paid`. Nothing else. Of the four values that went, two
were deleted by name in the two decisions above, and this round found the remaining two by grepping for the
rule that sets them and finding none: `written_off` has no code anywhere — there is no `fee.write_off` in
either half of the catalog, only `fee.view`, `fee.create` and the two codes D-157 and D-158 delete — and
`overdue` **is already computed in two places**, in §2's index of open obligations and again in integrity
check 5, which counts an obligation that is "`unpaid`, `partially_paid` or `overdue` with **no live
`payment_request`** pointing at it". So a state derived from `due_date` was also being stored, which is one
fact in two places with exactly one of them written by anybody.

The move is the corpus's own, twice over. [D-059](round-05.md#d-059--unanswered-is-the-absence-of-a-row-a-registration-stores-two-values)
deleted `unanswered` because an absence is not a value; [D-144](round-20.md#d-144--right_kind-is-a-note-required-by-the-schema-checked-against-nothing-and-no-longer-claiming-to-be-checked)
kept `right_kind` and demoted it to a note rather than pretend a check read it. Here the derived half wins
and the stored half goes: **overdue is a report over `due_date`, and uncollectable is a row nobody paid.**

**The tell, and it is worth keeping.** §4 worked out the balance that gates membership with an explicit
exclusion — "obligations carrying `waived`, `written_off` or `refunded` are excluded from the question
entirely, because a waived fee that nobody is going to pay is not an unpaid one". With all four values gone
that exclusion has an empty set. **An exclusion clause that ends up excluding nothing was not a rule; it was
a repair**, and the fact that §4 needed it at all is the evidence that the enum had three states doing the
job a smaller amount or a report should have done. The sentence goes, the arithmetic gets shorter, and check 5
and §2's index are rewritten to read `due_date`.

---

## D-160 — No proration rule, and the row is the amount

**Status:** decided (from your answer) — closes §5 item 1.

The design states no proration rule. Someone joining in October gets an obligation whose `amount_due` is
whatever the person opening it writes, and the renewal twelve months later is written by the same kind of act.

This is not an evasion, and the difference matters. §5 item 1 framed it as fairness plus a schema fork —
"whether that is fair is a policy question; whether the data model supports it is `amount_due` vs
`amount_expected`". The fork is refused: `amount_due` already exists, already defaults nothing, and already
holds the number a person chose. So the answer moves the decision from a rule nobody had written to **a row
somebody wrote**, which is the shape this corpus keeps landing on when a mechanism would have to encode a
policy it has no authority to set — D-109's listing instead of a lint, D-144's note that admits it is a note,
D-136's election that arrives as one `role_holder` row and a `note`.

**What is given up:** the last claim that the fee model encodes a policy rather than recording one. Nobody
will be able to point at a rule and say this organization prorates, or refuses to. And the report that would
notice a year priced unfairly does not exist and is not being added, because a price a person wrote down is
not a defect — the review is somebody reading it, which is the same answer D-071 gave for role assignments
sixteen rounds ago and which D-109 later turned into a tab.

`amount_discount` survives this untouched. §5 item 2 stays open, unchanged: a **per-person** discount is
still just `amount_discount`, and a **per-family** one still needs the grouping
[D-057](round-04.md#d-057--household-is-removed) deleted, which the page says is "not a constraint change but
a shape".

---

## D-161 — One live price, and the amount is filed as a question at last

**Status:** decided (from your answer) — closes the question §5 asserted twice and never listed.

**Deletes:** `fee_schedule.valid_from` and `valid_to`.

There is one price at a time. It is edited in place when the year is reopened; there is no price history.
Before it can be answered the question has to exist, so it is filed as **§5 item 12** here — the fee amount,
which the page's own framing sentences named unanswered at line 12 and again at line 40 while §5 listed
eleven items, none of them the amount.

Deleting the validity pair is the part that deserves a reason rather than a shrug, because `valid_from` was
justified on the page: "fee amounts change yearly, so a price is stored against a validity period rather than
overwritten", and `valid_to` that `NULL` means still current, and the note that storing it this way means a
historical obligation can be recomputed correctly. **The reason that deletion is safe is one line above, in
`fee_obligation`: `fee_schedule_id` is "snapshotted so the amount is reproducible even if the schedule
changes", and the obligation copies `amount_due` beside it.** The record of what a person owed was never in
the schedule. Only the price list was, and a price list is not a record — which is the same discovery
[D-142](round-20.md#d-142--the-displayed-name-stays-a-copy-and-the-check-that-counts-its-drift-is-named-at-last)
made about the displayed name, arrived at from the money side, except that there the copy was kept and here
the original is dropped.

**What is given up:** nobody can ask this system what a membership cost in 2027. The available answer is an
aggregate over the obligations of 2027, which is arguably the truer one, since it reports what people were
actually asked rather than what a list said.

**One blank kept open on purpose, and labelled as one.** No code is named for editing the price row, and this
round declines to mint `fee.schedule.edit` in passing — a code invented in prose is exactly the failure
[D-104](round-10b.md#d-104--a-permission-codes-last-segment-is-an-action-and-a-registry-that-prose-contradicts-is-a-fiction)
was written about, and the checker now refuses one. So the register says what is true: opening a billing year
is reached by the same grant that lets a person write a fee at that scope. **That clause is this round's
reading, not a ruling that came out of the answer**, and it is marked as such on the page that carries it, so
the next reader can tell which of the two it is. If it turns out to be wrong, the correction is a decision
entry and not a schema change.

---

## D-162 — An imported membership is `completed`, and the warning stays on the page

**Status:** decided (from your answer) — closes the naming bullet of `domain/05` §9.

An imported, closed `membership` carries `status = 'completed'`.

The objection on the page is recorded and not overruled. It lists the enum — `pending_payment`, `active`,
`suspended`, `lapsed`, `terminated`, `completed` — and says none of them means *a source stated this period and
nobody in the system decided anything*: `terminated` claims an end reason the export never gave, `completed`
claims a lifecycle this model does not have. And it names the risk in the form that matters: **"a `status`
that reads as a decision will be reported as one."** The answer takes the second-worst of the two lies, and
takes it knowingly.

What makes it survivable is that the row does not stand alone. Every imported membership is
`data_confidence = 'low'` and both of its dates came from a source row
([D-093](round-09.md#d-093--the-one-off-import-may-create-memberships-both-ends-dated)), so the honest answer to
*did anybody decide this* is two fields away from the field that reads as a decision.

**A seventh value named `imported` was the alternative, and it is refused — for a reason worth stating,
since it is the reason the page's instinct was wrong rather than merely expensive.** That value would answer
the question by teaching the column to mean two things: its other six values say *what happened to the
membership*, and `imported` would say *how the row arrived*. Every future historical query would then have to
decide, in that one column, between an event and a provenance — and the corpus's whole answer to "what did
this import assert" is already `data_confidence`, which lives beside `status` for exactly this reason.
Refusing a value is cheap here in a way refusing a table never is.

**Cost, accepted:** historical query 10 — members per year, as far back as the records reach — counts imported
rows as completed memberships, which is the whole point of the acceptance test and now its most literal
reading. And `terminated` stays what it is for the live path, untouched by the import.

---

## D-163 — A grant may not confer more than the granter holds

**Status:** decided (from your answer) — closes the hole `permission-catalog-b` §12 called the sharpest in the
file, and the one [round 21](round-21.md) recorded as untouched.

**The rule.** A write to `access_grant` may name only a permission that the person writing it holds, at a
scope that reaches what they are writing. `access_grant.create` says *you may write grant rows*; it has never
said *what they may say*, and until now nothing else did either. The answer is none of the three options the
page offered — no second code for the `system.` namespace, no two-person rule, no verdict of trail-and-judgment —
and instead a ceiling that reads the granter.

The mechanism is free, which is what makes it better than all three proposals: **it is the check the resolver
already performs, pointed at the granter at save time.** No new code, no new table, no second person in the
loop, and a person can predict the answer to "may I grant this?" from the same question they already ask —
*can I do this myself?*

**What it closes.** That anyone holding `access_grant.create` could grant `system.admin` to anyone, including
themselves, is over at the source: `system.admin` may now be granted only by somebody who already holds it.
Stated as the invariant the file was circling — **the set of privileges held by anybody in this system can
only grow from a person who already holds what they are handing out.** Day one is unaffected, because
[D-150](round-21.md#d-150--day-one-is-one-account-holding-systemadmin-and-nothing-else-is-shipped)'s single
account holds `system.admin` at the unit, which satisfies every code; the origin of all authority is exempt
by construction rather than by a special case.

**Three consequences, written down while they are cheap.**

- **A borrowed right is not a raised ceiling.** The check reads the granter's own grants, not rights they hold
  through a delegation. Lending is not holding, and refusing to let a lent permission be re-lent is the same
  instinct that stopped [D-146](round-20.md#d-146--an-outbound-call-is-a-persons-act-or-a-job-and-nothing-about-it-is-designed-yet)
  from letting an `api_key` carry the accountability of an act. Delegation is not obstructed by this: a
  delegation's grant row is written by the delegator, who holds the right directly, so the write path passes
  the ceiling on exactly the occasion [D-143](round-20.md#d-143--a-delegation-is-validated-once-when-it-is-written-and-stands-to-its-own-end-date)
  already validates at.
- **It says nothing about spread, and this round says so rather than pretending otherwise.** A person who
  holds `person.view` at the unit may hand it to twenty people, since they hold it. The ceiling stops
  **escalation**, not **distribution**, and **no report covers distribution** — not because it was decided that
  a report is enough, but because nothing was decided. *The entry a grep finds beside this row is
  [05d §11 check 7](../data-model/05d-invariants-and-seed.md#11-invariants-to-verify)'s wide half, and it is
  about something else:* a grant that got wider on its own because a `-` beneath it stopped resolving, which is
  authority growing with nobody writing a grant. Different widening, different report. This row's whole control
  is the save refusal, which is the posture this design takes deliberately elsewhere (D-126, and D-071 long
  before it) — the difference is that those name the report standing in for the mechanism, and this one has
  none. Naming it is cheaper than letting the near-miss report be read as coverage.
- **`granted_by` becomes load-bearing in a new way.** [`access_grant`](../data-model/05-authorization.md#6-access_grant--the-per-item-layer)
  holds it as *reference to person, required*, and [D-125](round-17.md#d-125--an-empty-actor-column-is-this-system-acting-on-its-own-and-its-name-comes-from-a-fixed-list)
  records that a grant's `granted_by` names a person, so those rows have no empty to read. That was
  bookkeeping. It is now the precondition of a security rule: the ceiling is evaluated against a named person,
  so an authorless grant could not be checked at all.
  [The register](../data-model/00a-invariant-register.md) gains the row that says so.

**Scope, so the ceiling is not over-read:** this is a rule about writes to `access_grant`. Editing an audience's
expression or a `role_holder` row is a different code and is unchanged; whether those should carry an analogous
ceiling is a question this round neither answers nor pretends is settled.

---

## D-164 — Nobody is told, and no page may say otherwise

**Status:** decided (from your answer) — [D-137](round-20.md#d-137--a-guardian-may-appoint-a-guardian-and-nobody-at-the-organization-is-told)
generalized from a ruling about guardianship to a property of the design, with its exceptions removed.

**Deletes:** the *promise*, wherever it is, and no mechanism — because none of it was ever built. The test
applied to every page is narrow on purpose: a report may be described as urgent, or as the only control on a
failure, or as the thing a person must read; what goes is any sentence saying the system **sends** something, or
that a person **will be told** within some period, or that a check *alerts* rather than being read.

**And the count this entry first carried was wrong, so it is recorded wrong here on purpose.** It said "four
sentences across three pages", which is what you get for reading a design instead of grepping it — the failure
this round has now written up twice in its own opening. The grep this entry can stand behind, run over every page
outside `decisions/` for `alert`, `notif`, `email`, `warn` or `ping` against `1a65aca` — the commit this round
started from, so the number is reproducible rather than remembered: **218 lines on 37 pages.** The same grep
today: **214 lines on 38 pages.** Most matches survive the test, and by construction: a report described as urgent is not a message, the
communication module's own rows are a module that does not exist yet, and wording about the audit trail is about
the trail. What the four did not include is the sentence that mattered most, because it names no report at all:
`05d` §11 opens by wiring **five checks and half of a sixth** to alerts. A framing sentence is invisible to a
count of sentences about `system.admin`, which is the same blind spot as a summary count that does not match the
list underneath it, two pages of this round earlier.

[D-137](round-20.md#d-137--a-guardian-may-appoint-a-guardian-and-nobody-at-the-organization-is-told) decided
that nothing in this design sends a notification: attribution is enough, the write is audited, the trail is the
control. Then four places promised that someone would be told within the hour about the holders of
`system.admin` — twice in `05d` §11, once in `domain/06` §2, once in `domain/02` §3, the last of those
pointing at "the same person the list already goes to" while no page named that person — and §11's opening
promise covered checks that no one had asked about. Asked which was
right — send the design's first message, address the report to the holder set, or leave it at the tab — the
answer was none of those: **no message at all, and no record beyond the audit row the write already made.**

**What survives, and must not be swept away by whoever applies this:** the **named recovery person** of
[D-126](round-17.md#d-126--break-glass-is-a-report-and-a-written-procedure-not-a-mechanism) stays exactly where
they are. That is not an alert. It is one human being written down in advance as the person allowed to perform
a break-glass edit, and a *procedure* needs a name where a *notification* does not. Conflating the two would
delete the only person named in the whole authority model, on the strength of a decision about email.

Check 9 keeps reporting who holds `system.admin` and whether each of them can sign in — that report is the
alert D-126 chose over a mechanism. What it loses is the claim that anyone is told when its result changes,
which was always a promise about a mailbox nobody had.

**The cost, in the plainest form available.** A grant of `system.admin` to a stranger is now detected by a
person opening a tab. Nothing stands in front of it, and the audit trail behind it can be read but not
prevented. That is survivable for one reason only: **D-163 means the stranger had to be handed it by somebody
who already held it**, so the question the trail answers — *who did this* — is now the question that matters.
The two answers belong side by side in the reader's head: this round is the admission that nothing is watching,
and the previous one is the reason that is bearable.

**What the sweep removed, counted three ways, because one number would have made this a fourth unverified
claim.** The word grep, above, moved from 218 lines on 37 pages to 214 on 38 — which is the entire truth about a
word list, and the sharpest of the three: the premise was corpus-wide while the count is noise, because nearly
everything matching those five words was already describing a report. The citation grep — added lines outside
`decisions/` carrying this decision's anchor — is **23 lines across 16 pages**, and it is the only figure here
computed from the diff rather than from somebody's report of their own work, which is why it is the smallest.
Between them the five sweeps listed **sixty-five sentences across twenty-five pages**, and each listed the same
round total of **fifty-eight**, which five measurements of a growing corpus could not all produce; one page, `01a`,
is counted in two of the five lists, so sixty-five is itself a ceiling. **I record both numbers and vouch for
neither.** "Sentence" is not a unit two people count alike — what one sweep rewrote as one, another counted as
two — and this round has now twice found that the count sitting beside a sentence is precisely the part nobody
checked. What is verified, and is the thing that matters, is not a number at all: **every page in the corpus was
put against the test**, the test is written where a reader will meet it rather than in this entry: `05d` §11, the
page that had the worst sentence on the subject, now carries the rule as its own framing — *"None of them sends
anything, and no page may say otherwise: what a check owes is a row on a screen, and urgency is a property of the
report rather than a message."* A count filed here would have been read instead of that.

---

## D-165 — There is no default for `MEMBERS`, and that is the decision

**Status:** decided (from your answer) — `permission-catalog-b` §11's "a decision with no default recorded
anywhere" stops being a hole and becomes the ruling.

Which offices are written without a `MEMBERS` term in their grant expression is decided **per office, by
whoever writes the grant**, and the design states no default in either direction. [D-100](round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)
moved the membership gate out of the resolver and into the grant text, and then nobody ruled what to write;
three pages carried that as an assumption, and the sharpest of them was honest about it — "this is left to
whoever writes the grant, which is the honest reading of D-100 rather than a ruling in it". It is a ruling
now, and its content is that there isn't one.

That buys and costs the same thing, which is why it is one decision rather than a trade-off: no office can
inherit an entitlement by being written from a template, and no office can inherit a lockout that way either.

**The risk this answer was really about is already closed, elsewhere, and says so.** The reason
`system.gate_exempt` existed was that a sweep must not lock out the one person who can repair the system
([D-051](round-04.md#d-051--the-membership-gate-is-waived-by-a-permission-not-only-by-a-role-flag)), and D-100
deleted both the gate and the exemption and left the reason standing. It does not need an exemption any more:
**day one's grant names a person and carries no `MEMBERS` term at all** ([D-150](round-21.md#d-150--day-one-is-one-account-holding-systemadmin-and-nothing-else-is-shipped)),
so no lapse can reach the repair path. The reason survives as a property of day one rather than as a rule about
offices, which is a better place for it.

**Two rules derived from the answer, marked as this round's reading rather than as the answer itself.**

- The **Unusual** tab lists *every* `ROLE(…)` operand with no `MEMBERS` term, not only the offices marked
  sensitive — which is the threshold `domain/06` §11 left open. The reason is structural: a list filtered by
  which offices "should" carry the term would encode exactly the default this round declines to set.
- A grant written without the term needs no reason field. [D-136](round-19.md#d-136--an-election-is-not-recorded-a-role-holds-only-the-people)
  already gives `note` to anybody who wants a reason beside a fact, and requiring one would turn the absence of
  a default into a small approval process wearing a field as a costume.

---

## D-166 — An account is not where authority over a child lives

**Status:** decided (from your answer) — falsifies
[assumption 3](../open-questions.md#i-assumption-index), the first row of that index to be falsified rather
than confirmed.

**Deletes:** `account.guardian_consent_at`, `domain/02` §2's assumption that a minor may not create an account
unattended, and the same page's open-issues bullet asking for an age threshold.

No minimum age. No consent step. No branch in the sign-up path. The reasoning is the design's own, applied one
page further along than it had been applied before: a guardianship is a relationship carrying its own
`right_level` ([D-074](round-06.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular),
[D-113](round-13.md#d-113--the-guardianship-channel-has-no-expression-guardians-is-not-a-selector)), a
membership is written by a person, and [D-100](round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)
made authority arrive only through grants. An account is a login. A timestamp on the *login* recording a
*guardian's* answer was therefore recording consent to a thing this model does not think an account grants.
`guardian_consent_at` goes, and `account` keeps the columns that describe authentication.

**What is given up, and it is not small.** A child may create an account unattended and nothing in the schema
will object. What stands between that account and anything about a child is that the account holds no grants
and grants are the only thing that reaches anything — which is true here in the ordinary way, not as a defence:
a new account is a person-shaped hole in the database until somebody writes a row about them.

**Two things this does not decide, kept open rather than swept up.**

- **The jurisdictional half.** Whether the law of this country requires a guardian's consent for a child's
  account in an information system is not answered by deciding that the *model* does not need one, and this
  round does not pretend otherwise. It goes to the legal review as a **fourth** policy in front of it, beside
  [assumption 49](../data-model/00-conventions.md#8-personal-data-and-erasure)'s indefinitely-kept rows, the
  audit payloads emptied at 24 months and the `access_log` rows deleted at 24 months
  ([D-145](round-20.md#d-145--access_log-rows-are-deleted-at-24-months-and-the-job-that-does-it-has-a-name)).
- **`domain/02`'s other bullet** — whether staff may create accounts for children at all, or only for adults —
  is untouched by this, stays open, and keeps its `created_by_staff` flag beside it. A reader who takes "no gate"
  to mean "staff may create a child's account" has read further than the answer goes.

---

## D-167 — The office that may place a child in a group stays unnamed

**Status:** decided (from your answer) — an omission becomes a ruling, which is the only way an omission can be
made safe.

`person_group.member.manage` is the whole of the right to place a person in a set. On day one the only grantee
that may write one is the single account holding `system.admin` at the unit. Which volunteer office holds it is
**not named here**, and the page's reason is kept as the reason: an appendix "that quietly hands it to `leaders`
would be making a safeguarding choice on someone else's behalf". Ruled now so that a later round does not
repair the blank: **the blank is the answer.**

**Cost, which is in day one rather than in the schema:** the first roster anybody builds is built by the one
account that must not be used day to day. That pressure is precisely what
[D-154](round-21.md#d-154--counselors-is-an-example-now-not-a-shipped-office)'s worked examples and
[D-100](round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)'s office model
exist to relieve, and the relief is cheap — writing the office is one `role` row and one grant, not a migration.
What would have been expensive is the alternative: an appendix choosing it.

---

## D-168 — Age is reported and never enforced

**Status:** decided (from your answer) — closes `domain/05` §9's age-rule bullet and
`data-model/03` §9's "may a group ever state an age rule of its own".

Nothing in this model carries an age rule, and nothing will. A `role` is a name, two dates and a holder list
([D-100](round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)),
a `person_group` was refused an age band
([D-098](round-10a.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority)), and
"a scoutmaster must be an adult" stays what it is today: a report over `role_holder` read against `is_minor()`.
Historical query 8 — which minors are in groups that do not accept them — **stays unanswerable and stays
numbered**, which is how it was left deliberately so that the gap sits on the list instead of being renumbered
away.

Ruling this instead of inheriting it is the point. The alternative was one column and one refusal at save, and
this corpus has now refused that shape repeatedly on identical ground: **a field that looks like a control
where no control is wanted is worse than the absence, because someone comes to rely on it**
([D-136](round-19.md#d-136--an-election-is-not-recorded-a-role-holds-only-the-people) on elected-versus-appointed,
[D-144](round-20.md#d-144--right_kind-is-a-note-required-by-the-schema-checked-against-nothing-and-no-longer-claiming-to-be-checked)
on `right_kind`, [D-138](round-20.md#d-138--one-permission-guards-the-whole-audit-trail-and-the-widening-is-on-the-record)
on a per-entry audit filter). An eligibility column would be consulted by nobody and trusted by everybody.

**Cost, stated:** the enforcement of every age rule this organization has is a person reading a report. If the
bylaws ever demand a real eligibility test, the honest route is a new column, a new refusal, and a stated
reason to break D-098 — a decision entry, not a schema change.

---

## D-169 — An imported membership ends with the calendar year it was seen in

**Status:** decided (from your answer) — fills the blank inside the recommended default of
[`06a` §3.1's end-date inference](../data-model/06a-import.md#end-date-inference), and closes the
[`06b` §6](../data-model/06b-redaction-and-checks.md#6-open-issues) bullet that asked for it.

**The rule.** Where a people batch states when a period began and not when it ended, the imported
`membership` ends with the calendar year of the last period in which the person appears. **The person's last day
as a member is 31 December, and the value written into `valid_to` is 1 January of the following year** — every
period in this model is half-open, and
[`is_current_member`](../data-model/03-membership.md#current-membership-queries) requires `valid_to` to be *after*
today, so a literal 31 December in that column ends the membership on the thirtieth. Written as the answer was
given, the column would be one day short in every single row and would look correct in every report that does not
name the day. This is a translation into the column's own convention, not a change to the date you chose, and it
is the kind of sentence this round exists to force somebody to write down.

**Where the answer already was, which is the finding.** [D-047](round-04.md#d-047--the-fee-expires-on-1-january)
settled that the fee expires on 1 January, the two columns that hold it live in `membership_type`, and
[the register's own assumption index](../open-questions.md#a-4-remainder--the-organizational-calendar) says in
four words that *the organizational year runs with the calendar* — which is precisely the phrase the import page
needed and then went and asked for. `06a` wrote "the end of the organizational year" and never resolved it to a
date; `06b` filed the missing date as a question and pointed at A-4; A-4 had answered it. **This is the third
question this round found already answered somewhere else** — after the fee amount, which was asserted
unanswered but never filed (D-161), and the ceiling on a grant, which three proposals had worked around while the
free mechanism sat in the resolver (D-163). The corpus does not mainly lack answers. It lacks edges between pages
that already hold them.

**Why this boundary rather than an arbitrary one, since it is defensible on its own merits.** It is the same
boundary a live membership's period runs to, so an imported row ends where the real one would have ended, and the
yearly sweep and the member-count-per-year reports read one calendar rather than two. Of the three options the
table offered, it is the middle one, and the answer is a choice between the two live rows rather than a
restatement of the recommendation: the first is already banned (NULL makes an open row satisfy
`is_current_member()`, so the row passes the permission gate — [D-039](round-02-03.md#d-039--member-permissions-require-a-current-paid-membership),
and it stays banned), and the third — end at the last date the person appears in *any* export — is refused,
because it needs the complete dataset and the corpus is two exports with gaps, not an archive.

**The consequence worth more than the rule.** [`06b` §5's check](../data-model/06b-redaction-and-checks.md#5-integrity-checks)
on imported memberships with no end date says "zero is the only acceptable answer" and is a security check, not a
data-quality one. Until now that zero was unreachable in the ordinary case: a row arriving without an end date had
no correct value to be moved to, so the report could only announce a failure with no remedy attached. Now the
remedy is this rule, and a non-zero result means **the inference did not run** rather than *nobody knew*.
The same reasoning is why `data_confidence = 'low'` stays on every one of these rows
([D-093](round-09.md#d-093--the-one-off-import-may-create-memberships-both-ends-dated)): the date is the
organization's, the *period* is a guess.

**Cost, stated.** A membership that actually continued into the next year is truncated, which is the risk the
option's own row named ("May truncate a period that continued"). That is the direction of error this design takes
on purpose: truncation is wrong toward *fewer current members*, which shows up as a person who cannot sign in and
is corrected by a person who knows them, while an open row is wrong toward *more authority* and nothing surfaces
it. D-162 chose `completed` as the status of exactly these rows; the two answers together are what an imported
closed membership is — dated to a boundary it did not choose, marked low confidence, and wearing a status that
belonged to a lifecycle nobody consulted.

**Reading, not ruling:** the day should be read from the same two columns D-047 put in `membership_type` rather
than compiled in as a literal, for the only reason those columns exist — [A-4's remainder](../open-questions.md#a-4-remainder--the-organizational-calendar)
is precisely the discipline that a job containing `1` and `1` would break. This round states that as its reading
of the answer rather than as a second ruling, and the check on it is the one that question already asked: *does
this date come from the row?*

---

## What this round leaves open, with its shape named

The point of a round that starts from "the register said five and the corpus said twenty" is to end with a
register that tells the truth again, so this section is the count and the shapes, not a summary.

**`07-finance.md` §5, counted rather than recited.** It opened with eleven items, two closed and one half
closed. This round closes item 1 (D-160), item 3 (D-158), item 9 (D-156) and item 10 (D-157), narrows item 8 to
its jurisdiction half (D-155), and adds and answers item 12 (D-161). **Five remain**: discounts, invoices, the
accounting export, jurisdiction, and the variable-symbol question — the last of which is still three questions
in a trenchcoat, because it decides whether the module has one money path or two. The page renumbers those five
from one and keeps each closed item as a single line, so **an item number anywhere in this round means the old
numbering**; the heading still reads "the whole of this document, essentially" because that title is quoted here
and every inbound anchor resolves through it.

**All five survivors are now the only place they are written**, and none of them is registered in
`open-questions.md` — which is now stated on the money page itself, at the foot of §5, rather than left for the
register's finance row to imply otherwise. That is the shape of the bug this round was summoned by, and answering
sixteen questions did not fix it: a register that counts a page cannot see a module page's open issues. What this
round did instead is make the invisibility sayable — the page names what is registered there (the closed items,
with their decisions) and what is not (the five), so the next round that touches money inherits a sentence to
correct rather than a silence to rediscover.

**Not one of the register's five survivors was answered, and nine new questions were filed there.** A-4's
remainder, E-3, F-9, F-11 and F-34 are questions about the core design, and sixteen answers touched the core
design exactly twice — at the ceiling on a grant (D-163) and at the account of a child (D-166) — neither of which
was on the list. D-169 looks like it closes A-4 and does not: the calendar question was answered in round 4, and
what D-169 closed was a module page's bullet that had not noticed. **What did move is the page's total, from five
to fourteen:** the nine questions this round found and verified but did not ask are now
[§ K](../open-questions.md#k-filed-by-a-module-page), each naming the page that holds it, because the alternative
was to leave them in a decision entry where only a reader of decision logs would find them. **That is the whole
repair this round could make for its own finding: an answer on a page is not a registered question, and neither is
a question written up in the log that found it.**

**Questions found, verified and deliberately not asked this time**, so that they are not rediscovered as
findings: whether a `person_group_member` row must lie inside its group's own period (`data-model/02` §8,
"nowhere ruled", and the register records the containment as enforced by nothing); whether an ended group is
hidden from pickers and whether it may be reopened, which collides with §1's rule that a returning name is a
new group; where a claimed group continuity is recorded, since D-098 refuses group-to-group edges and nothing
replaced what D-096 gave units; whether `person.gender` is needed and with what value set; whether there is or
will be a national SSO identity provider, which decides how much of `account_credential` is ever built;
whether `person.notes` should exist given the redaction burden it creates; which tables the audit obligation
covers, where the page asks for confirmation rather than derivation; who reads the unpaid-money queue monthly,
since four pages say *someone*; and whether staff may create accounts for children, which D-166 keeps open.
None of these is closed. All of them are one sentence long.

**And the legal review now has four policies in front of it, not three**: named membership and fee rows kept
indefinitely, audit payloads emptied at 24 months, `access_log` rows deleted at 24 months, and — added by
D-166 — whether a child may hold an account with no guardian's consent recorded anywhere. The second and third
are this system's own clocks; the first and fourth are the two a data subject asks about.
