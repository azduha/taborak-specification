# Decision Log — Refinement round 19 (D-133 … D-136)

> Two trail rules are unchecked and now say so; four of seven polymorphic columns get an orphan scan and the audit row deliberately does not; the two modules with no check list get one; and an election is not recorded, because a role holds only the people.

[Refinement round 18 (D-127 … D-132) ←](round-18.md) | [All decisions](index.md)

**What was asked.** Round 18 had just emptied the top of the "answer next" list and filled it again with six
questions of its own making, all of them found the same way: write down who enforces each invariant and
count the blanks. This round was asked to put questions, not to change the model, and it did: four were put,
four were answered, and **none of the four changed a table**. That is the shape this corpus is in — the
remaining questions are about what a report is able to see and what a piece of prose is worth when nothing
runs it.

**What the round found while answering, which is the part worth reading.** Three of the four questions
arrived with a premise that did not survive being checked against the page that owns the rule.

- **F-29 blamed the payload window for a gap the window does not cause.** The check it was debating would
  compare a key's `valid_to`, its `revoked_at` and an audit row's `occurred_at` — three columns of the
  accounting skeleton, all permanent. The report could be written and would work in thirty years. So the
  answer "no report" is not a limit the design is under, it is a guarantee the design declines, and the
  documents now say that instead of implying the opposite.
- **The register row minted beside that question described a rule no page states.**
  [00a](../data-model/00a-invariant-register.md) carried "which audit views a holder may open follows the
  payload window, not the table" against a citation to
  [06 §2](../data-model/06-audit-and-import.md#2-audit_log). No page in the corpus says any such thing;
  [06 §2.3](../data-model/06-audit-and-import.md#23-history-query) says close to the opposite — a
  per-entry check inside the history view was considered and left unimplemented — and that question is
  [AT-4](../open-questions.md#at-4),
  already open. Under [D-129](round-18.md#d-129--where-the-register-and-the-page-disagree-the-page-is-wrong)
  a register row is a claim about a page and is verified against it, never asserted, so the row is withdrawn.
  **It got into the register in round 18 by the route D-129 warns about**: the inventory was written from the
  pages, and this row was written beside the inventory.
- **F-30's own positions could not count.** They offered to "scan the two a person can cause" and then named
  four columns. The seven columns were re-counted from the field tables before anything was decided, which is
  also what turned up a second, quieter defect: [erd-b](../appendix/erd-b-inventory.md) still said "there are
  exactly two reference-less keys" after round 18 had corrected that exact sentence in
  [00 §9](../data-model/00-conventions.md#9-referential-integrity-rules). The register and the appendix had
  drifted apart by one round.
- **Round 18 had fixed one page of that count and left four.** Checking the drift meant grepping the
  sentence, and the grep found the same claim in [05b](../data-model/05b-expression-tree.md) twice,
  [05a](../data-model/05a-audience-and-grammar.md) and [erd-a](../appendix/erd-a-authorization.md) twice —
  "**exactly two** polymorphic keys in **this design** go without a foreign key", where the design has
  **seven**, every one of them with a sibling column naming what it points at (`grant_scope_type`,
  `argument_type`, `scope_type`, `authorization_channel`, `entity_type`, `entity_table`, `table_name`).
  Three of the five cite §11 for the assertion, and **§11 never makes it** — which is D-129's defect again,
  a claim about a page that the page does not make, stated five times and verified zero times. All five now
  say two *of seven* and point at the page that keeps the count. **A count that was taken by looking is a
  count of what somebody looked at**, and one round is long enough for the corpus to believe it.

**One decision from round 18 is still not in the model.**
[D-132](round-18.md#d-132--day-one-is-one-account-holding-systemadmin-and-every-role-after-it-is-written-by-the-organization)
was ruled last round and is applied by a sweep this round owes and has not yet run: the seeded roles, the
seeded audiences, the seeded `event.answer.view` grant, the worked-example offices presented as seed,
`role.is_system`, `audience.is_system`. [F-18](#d-136--an-election-is-not-recorded-a-role-holds-only-the-people)
below is the second decision this round closed that had been arguing, in the present tense, from `is_system`.

---

## D-133 — Two trail rules stay unchecked, and say so out loud

**Status:** applied.

**Question.** [F-29](../open-questions.md#f-29) asked what a report may be asked to see about an audit row
whose payload has been emptied on schedule. Two rules had no report beneath them: that no write is ever
audited against an `api_key` that had already ended, and — as the register had recorded it — that which audit
views a holder may open follows the payload window. Both were listed as blocked by
[D-088](round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)'s 24-month
window, which empties the payload and is the part a check would have to read.

**Answer.** **No check is written for either rule, and the page that states the first one now says the
guarantee is not offered.** Of the three positions on the page — check the envelope rather than the payload,
accept the blindness and say so, or widen the window for the columns these checks need — the second was
chosen, and chosen with its reason corrected first.

**Why not the cheap-sounding one.** "Check the envelope" is genuinely cheap: the columns involved are a key's
`valid_to`, its `revoked_at`, and the audit row's `occurred_at`, none of which is a payload. **Writing it was
declined, not impeded**, and the decision records what that costs rather than dressing it up: nobody will ever
be able to demonstrate that no write was audited against a key that had already ended. A report nobody reads
is not a control either, and this corpus has already decided — nine times over, in checks that exist only to
re-ask whether a guard is still there — that the number of reports is not what makes a rule true.
**Widening the window was refused for the reason the question itself named: a privacy answer dressed as an
integrity one.**

**What was actually wrong in the question, and what was wrong in the register.** The window was never the
obstacle — see the lede. And the register's second row for this question described a rule that exists
nowhere. Both halves are repaired: [06b §5](../data-model/06b-redaction-and-checks.md#5-integrity-checks)
now carries the ruling beside the sentence that admits the gap, and the phantom row is deleted from
[00a](../data-model/00a-invariant-register.md) rather than re-worded, because there is nothing to re-word it
into. The nearest real rule — a history screen over the trail is a person-data surface, and a per-entry
"could this reader see this field" check was considered and left unimplemented — is stated where it lives,
in [06 §2.3](../data-model/06-audit-and-import.md#23-history-query), and its open question is AT-4.
**This decision does not answer AT-4 and does not close it.**

**Deletes:** one row of `00a`, and with it the eleventh `none`.
**Changes no table, no column, no code.**

**See:** [06b §5](../data-model/06b-redaction-and-checks.md#5-integrity-checks),
[00a](../data-model/00a-invariant-register.md),
[D-088](round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short),
[D-129](round-18.md#d-129--where-the-register-and-the-page-disagree-the-page-is-wrong), and
[F-29](../open-questions.md#f-29) in § R.

---

## D-134 — Four more polymorphic columns get an orphan scan, and the audit row never

**Status:** applied.

**Question.** [F-30](../open-questions.md#f-30). Seven columns hold an id with no foreign key behind it and a
sibling column saying what kind of thing it points at. Two were followed by an orphan scan
([05d §11 check 2](../data-model/05d-invariants-and-seed.md#11-invariants-to-verify)); five were not scanned
anywhere: `access_log.scope_id`, `access_log.authorization_ref_id`, `access_log.entity_id`,
`field_conflict.entity_id` and `audit_log.record_id`. The question said explicitly that these are not one
decision, and it was right, because the answer for the trail is the opposite of the answer for a conflict row.

**Answer.** **Four get a scan; `audit_log.record_id` never does, and the pages say why in those words.**

- **`field_conflict.entity_id`, scanned outright.** A conflict recorded against a row that is not there is a
  broken import. There was no sentence anywhere saying so, which is the reason this one was the cheapest of
  the four.
- **`access_log`'s three, scanned with the legal-absence rule written beside them.** A reference that no
  longer resolves because a person was erased at their own request is not an integrity failure, and a scan
  that cannot tell that apart reports the erasure path's own correct output as a breach.
- **`audit_log.record_id`, deliberately not scanned.** An audit row that outlives the row it described *is*
  what a redaction looks like afterwards. Counting those as orphans would train the reader to ignore the
  report — the first false alarm is the expensive one — and the alternative, a legality rule over the whole
  trail, is a rule about absences so broad it would be read once and never again. **The column is not an
  oversight any more; it is the one place this design states that the trail is allowed to point at nothing.**

**What this corrected as it went.** [00 §9](../data-model/00-conventions.md#9-referential-integrity-rules)
and [erd-b](../appendix/erd-b-inventory.md) both counted reference-less keys, and after round 18 fixed the
sentence in one of them the two disagreed by a round; both are now correct and say which columns are scanned,
which are scanned-with-an-exception, and which is exempt. `00a`'s row for this rule cited only the appendix,
which is the inventory rather than the rule's home, and under D-129 it now cites
[00 §9](../data-model/00-conventions.md#9-referential-integrity-rules).

**Adds:** one numbered check in [05d §11](../data-model/05d-invariants-and-seed.md#11-invariants-to-verify),
beside check 2 and cross-referenced with it, and no TIME-BOMB label — this one is a report over data, which
is what the label is for keeping apart.
**Changes no table and no column.** Whether an orphan in `access_log` after an erasure is legal is a rule
about which rows survive erasure, and the check inherits whatever 00 §4 and 06b already say.

**See:** [00 §9](../data-model/00-conventions.md#9-referential-integrity-rules),
[05d §11](../data-model/05d-invariants-and-seed.md#11-invariants-to-verify),
[erd-b](../appendix/erd-b-inventory.md), and
[F-30](../open-questions.md#f-30) in § R.

---

## D-135 — The two modules with no check list get one each

**Status:** applied.

**Question.** [F-31](../open-questions.md#f-31). Every data-model page states its rules and then lists what
would notice a breach — except [07-finance](../data-model/07-finance.md) and
[06a-import](../data-model/06a-import.md), which state rules and stop. That is why most of the
register's blanks sit in those two modules: **their rules were unassigned by construction, not by oversight**,
because there was no section for an assignment to live in. It was the only yes-or-no on the page.

**Answer.** **Yes: three checks on each page**, in a new
[07 §4a](../data-model/07-finance.md#4a-integrity-checks) and a new
[06a §4](../data-model/06a-import.md#4-integrity-checks).

| The check | What a row means |
|---|---|
| Finance 1 — the balance, recomputed from §3's definition | A member wrongly suspended, or a family wrongly chased. Survives §3's own recommendation to drop the column, because then it checks the view against the definition instead of the copy against the sum |
| Finance 2 — a payment whose allocations do not account for its amount | Money that moved and was never attributed, or an overpayment nobody refunded. No constraint can span the two tables, so this report *is* the backstop |
| Finance 3 — money nobody ever asked for | An open obligation with no live request, or a paid-for event with no obligation behind the registration. Silent in both directions: nobody is chased, nobody pays |
| Import 1 — an imported membership that should not exist | An unbounded period, or a membership written from an attendance list. **The one row in the register that reaches the permission gate**: an open membership satisfies `is_current_member()` (D-039) |
| Import 2 — one event per (title, date), one registration per attendee row | The application-layer rule `uq_staging_event_match` has been lost, and ten thousand attendees have become ten thousand events |
| Import 3 — a batch whose own accounting does not close | Rows neither applied nor discarded, a row that created nothing, ids from the wrong half of the corpus, or a reverted batch that left rows behind — read against the audit entries the revert wrote |

**What the round noticed while writing them.** The import page had been citing, for two rounds, "check 1 in
§5" — a section that page does not have. The citation was correct in intent and wrong in fact, and §3.1 now
points at §4, where check 1 is the one it meant. **The strongest of the six import checks was therefore
already in the corpus as a promise about a section that did not exist**, which is the same failure as a
register row with no report beneath it, one level up.

**Adds:** two sections, six checks, and **three rows in `00a`** for rules both pages had stated and never
registered — the bounded imported membership, a batch's own accounting, and a payment's allocations. The
register is 71 rows where it was 69, and its `none` column is seven where it was eleven. It also **costs the
register its excuse**: *What the register cannot say* had been explaining the concentration of blanks by
pointing at these two pages, and can no longer.

**See:** [07 §4a](../data-model/07-finance.md#4a-integrity-checks),
[06a §4](../data-model/06a-import.md#4-integrity-checks),
[00a](../data-model/00a-invariant-register.md), and
[F-31](../open-questions.md#f-31) in § R.

---

## D-136 — An election is not recorded; a role holds only the people

**Status:** applied.

**Question.** [F-18](../open-questions.md#f-18), open since
[D-100](round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape) deleted
`position` with its `is_leadership`, `min_age` and `max_holders`: does a `role` say elected or appointed, and
if so what does an election *write*? The page's own framing was fair to both sides — `role_holder` has
`valid_from`, `valid_to`, `granted_by` and `note`, which is nearly enough to describe an election, and
`granted_by` names the secretary rather than a mandate.

**Answer.** **Neither. The organization manages elections outside this system, and a role holds only the
people who hold it.** No column for term kind, no table of elections, no record of how a person came to fill
an office. What arrives is the outcome: one `role_holder` row, a period, and `note` for whoever wants the
reason written beside the fact rather than buried in the trail. Stated where a reader will meet it, in
[domain/04 §6](../domain/04-organization-structure.md#6-appointments), with a pointer from
[05 §4](../data-model/05-authorization.md#4-role_holder--who-holds-an-office).

**The refusals, each with the reason it was refused.**

- **A boolean on `role`** — elected or appointed — would make the distinction queryable and would guard
  nothing. **A field that looks like a control in a place where no control is wanted is worse than the
  absence of one**, because someone starts relying on it, and the first exception teaches them not to. The
  question itself noticed this: it observed that a flag "invites a check which D-100's posture would refuse
  to enforce".
- **A table of elections** would describe a process this system does not run. There is no ballot, no
  candidate list, no quorum rule anywhere in these documents, and
  [D-043](round-02-03.md#d-043--no-background-checks-are-recorded-in-this-system) already settled that this is
  not the registry of everything true about a volunteer.
- **The distinction has nowhere to bite.** An office confers nothing by being held
  ([D-100](round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)), so
  there is no dangerous thing an election could confer and no answer anywhere in the resolver that would move
  if a row knew how its holder arrived. **This is the fact that makes the answer cheap, and it is worth
  naming before anyone offers to make the answer expensive again.**

**The cost, stated because the page says it out loud rather than leaving it to be discovered:** nothing in
this system will ever refuse to appoint someone to an office the bylaws reserve for a vote. That rule lives
in the bylaws and in the people reading them.

**Two of the question's load-bearing facts had already gone while it sat open:** `role.max_term_months` is
deleted ([05 §3](../data-model/05-authorization.md#3-role--an-office) lists it among the columns deleted with
their mechanisms), and `role.is_system` — which the question cited as what keeps seeded offices distinct — is
deleted by [D-132](round-18.md#d-132--day-one-is-one-account-holding-systemadmin-and-every-role-after-it-is-written-by-the-organization),
whose sweep is still owed. **A question that has been open long enough to lose its premises should be re-read
before it is answered**, and this one was.

**Changes no table and no column.** Three pages that had been calling this an open question now say it is
closed: [glossary](../glossary.md), [catalog-a §5](../appendix/permission-catalog-a-codes.md#5-organization-and-positions), and
[domain/06 §5](../domain/06-authorization-model.md).

**See:** [domain/04 §6](../domain/04-organization-structure.md#6-appointments),
[05 §4](../data-model/05-authorization.md#4-role_holder--who-holds-an-office),
[D-100](round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape),
[D-043](round-02-03.md#d-043--no-background-checks-are-recorded-in-this-system), and
[F-18](../open-questions.md#f-18) in § R.

---

## What the round did not do

- **It did not run D-132's sweep.** The seed still ships in the pages: 05d §12, catalog-b §11, and
  `role.is_system` in `05-authorization.md`. That is a cleanup with a decision already written, and it is the
  next thing this repository owes itself.
- **It did not answer AT-4,** which D-133's repair brushed against and explicitly left where it was.
- **It added no check that it could not point at a page.** That rule held even where it was inconvenient:
  the register still says `none` seven times, and three of those seven are open questions rather than chores.

**The gate ran.** `scripts/check-registries.py` reports **no unbaselined
finding** at the end of this round, and `mkdocs build --strict` is clean. [D-127](round-18.md#d-127--the-registry-diff-is-a-committed-script-and-it-gates-a-round)
says a round does not close on an unbaselined finding; nothing here needed a new baseline line, which is the
quiet way for a round to go.

**What the link pass swept up on the way.** Five links still pointed at F-8 by its heading slug, which
stopped resolving the round an explicit `<a id="f-8">` was put inside that heading; the target was fine and
the address was not, which is the one kind of breakage a reader never sees coming because the question is
still there, one click away from nowhere. **A slug is derived, and a derived thing has to be recomputed, not
remembered** — which is why every anchor touched this round was recomputed rather than typed.
