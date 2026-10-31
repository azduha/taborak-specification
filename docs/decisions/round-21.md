# Decision Log — Refinement round 21 (D-150 … D-154)

> D-132 was decided in round 18 and never applied: the seed was still described on the page that owns the seed, deferred to a round that went off to do something else twice. This round applies it. The roles, the two named audiences, the shipped answer-view grant and **every `is_system` column in the design** go, and applying a decision that had been settled for three rounds turned out to need three rulings the decision did not contain: where the first `system.admin` comes from when nobody yet may write a grant, who writes the per-event answer-view grant once nobody ships one, and what protects a vocabulary once the flag on its rows is gone.

[Refinement round 20 (D-137 … D-149) ←](round-20.md) | [All decisions](index.md)

**What was asked.** Round 20 was split on purpose: thirteen answers in one file, the twenty-five-page sweep
in the next ([D-132](round-18.md#d-132--day-one-is-one-account-holding-systemadmin-and-every-role-after-it-is-written-by-the-organization)'s
sweep, deferred since the round that decided it). This file is the second half of that split, and it was
under way before it stopped being mechanical. A deletion is only a deletion if nothing was relying on the
thing deleted, and three things were: the first account's authority, every event's answer privacy, and the
four vocabulary columns that told a screen not to edit a row. Each became a question, the questions were
asked, and the answers are D-150 to D-152. D-153 and D-154 are the two named things the sweep swept up.

**What the round found while applying it, which is again the part worth reading.** A deferred decision is
not a decision that stopped costing anything: while it sat unapplied, pages kept being written against the
seed as if it were shipped, and two of them disagreed about what the seed *was*.

- **D-132 said day one has "no role, no audience, no grant", and day one needs one grant.** Every authority
  in this design arrives through `access_grant`
  ([the catalog](../appendix/permission-catalog.md) says so in as many words: every code, `system.admin`
  included), so an account that *holds* `system.admin` holds a grant row. And on day one nobody holds
  `access_grant.create`, because the seed that would have carried an office holding it is the seed being
  deleted here. The round asked where that first row comes from and the answer was flat, and right:
  **from the same place every other authority comes from — it is a permission, and it is the one that means
  everything.** Nothing bootstraps anything; there is no fourth kind of actor, no `bootstrap_person_id`
  column, no CLI-only back door into the resolver. The account holds one code and that code satisfies every
  check, so `access_grant.create`, `role.create` and `audience.manage` are all available in the same instant
  the account is. D-132's "no grant" was a sentence about **bundles** — no starter set, no office, no
  audience — and this round says so instead of leaving a decision to be re-litigated by a reader who takes
  it literally.
- **The seed and the guard page disagreed about how many rows the seed was, and the check was written
  against the reading that was wrong.**
  [05d §12](../data-model/05d-invariants-and-seed.md#12-what-day-one-looks-like) explained the shipped
  answer-view grant as "**one grant in the seed rather than one per event**".
  [08a §8](../data-model/08a-event-guards-and-checks.md#selectors-that-bind-to-an-event) explained the same
  grant as the opposite: a bound operand is legal only on an item-scope grant, so it "**cannot be one row
  for every event**", and the page read the seed as a *template* the creation path instantiates. Those are
  two descriptions of one row-count, both in the corpus, and
  [check 2](../data-model/08a-event-guards-and-checks.md#10-integrity-checks) counts events one by one —
  which is only a sensible check against the second reading, since against the first a single shipped row
  would satisfy it forever and the check could never fire for an imported event. The contradiction was
  invisible because the disagreement was about a row count and both pages were busy making a different
  point about bound operands. **Resolved: one grant per event, written by the act that creates the event**
  (D-151), which is the reading the check was already assuming and the reading 08a's own
  *Assumption* paragraph had already reached.
- **`event.grant_access` turns out to have a subject, and the appendix that suspected it did not is closed
  by the module that owns the code.**
  [catalog-b §12](../appendix/permission-catalog-b-roles-and-open-issues.md#12-open-issues) wrote: "*`event.grant_access`
  may be a code with no subject, and this appendix will not delete it* … either it is a scoped front door
  onto the same table — in which case **the catalog should say so and the two codes' relationship should be
  an invariant** — or it is a code with no remaining subject", and declined to decide, because "deleting a
  code because one mechanism died is the events module's call, not an appendix's". The events module's call
  is in D-151, and it went the other way from deletion: with no seed, the answer to "who turns on an
  organizer's authority?" is *the creation of the event*, and what that act writes includes this code — so
  **an organizer may grant access to the event they run without holding anything at the unit**, which is a
  capability the design did not have a way to express until it had a reason to. The relationship the
  appendix asked to have stated is stated there.
- **`is_system` meant "the migration wrote this row", and after this round that is true of every row of
  every table that still has the column.** D-132 deleted the flag from `role` and `audience` because those
  tables stopped shipping rows. The same argument applied to the two tables that *kept* their rows —
  nothing about a flag is rescued by the rows beside it being kept, if the flag is now true on all of them
  and no row can ever arrive any other way. [05a's own column note](../data-model/05a-audience-and-grammar.md#the-selector-registry)
  had already conceded it: "**every seeded row is true with no row planned false. This column exists to
  make the table refuse an edit, not to mark a category.**" A column that cannot be false is not a flag; it
  is a sentence about the table, and the sentence was already written two lines above it in
  [05a](../data-model/05a-audience-and-grammar.md#the-selector-registry) ("no screen edits this table") and
  in [erd-a](../appendix/erd-a-authorization.md) ("organization-read-only"). Zero `is_system` columns
  remain in the design, and
  [00 §2's](../data-model/00-conventions.md#2-naming) example of the `is_` boolean prefix had to
  change, because a convention illustrated by a column that no longer exists teaches the wrong thing.
- **Integrity check 13's expectation inverts, and inverting it is the clearest sign the sweep was real.**
  [05d §11 check 13](../data-model/05d-invariants-and-seed.md#11-invariants-to-verify) reports "an
  assignable permission that no live grant names" and its stated expectation was "**empty after a seeding
  pass**", with the residual explained as "a human reading the starter list in §12 against the catalog".
  There is no seeding pass and no starter list. On the first run of this system the report is **the entire
  catalog except `system.admin`**, and every one of those rows is correct — a code nobody has granted yet is
  D-132's point 3, "the list the organization reads in order to decide what to grant". A check whose
  empty-state is now the system's most common state needed its expectation re-worded, not deleted, and the
  re-worded version is the one that says what a row means *after* somebody has been using the system for a
  year: an unmapped module, not an untouched vocabulary.
- **Two of the round's numbers were wrong before anyone checked them, and one of them is D-132's.** The
  estimate this round inherits is "a sweep of twenty-five pages rather than a deletion". That was a guess
  written in the round that made the decision, and a deferred guess is worse than a small one: it gets
  quoted. The real figure is counted below, off `git diff --stat`, in the same section that counts the gate.

---

## D-150 — Day one is one account holding `system.admin`, and nothing else is shipped

**Status:** applied. **Applies:** [D-132](round-18.md#d-132--day-one-is-one-account-holding-systemadmin-and-every-role-after-it-is-written-by-the-organization),
whose status line carried this round's number as "round 19" for three rounds; that pointer is corrected on
the entry itself rather than silently rewritten, because *which round owes what* is exactly the kind of
fact a reader cannot recover from a tidied-up log.
**Deletes:** the seeded roles (the one `counselors` row and the `system_admin` office the catalog sketches),
the two named audiences `everyone` and `all_members` ([D-153](#d-153--two-named-audiences-go-and-nothing-replaces-them)
is what replaces them, which is nothing), the shipped `event.answer.view` → `ORGANIZERS` grant
([D-151](#d-151--creating-an-event-writes-the-events-authority-and-its-organizers-may-grant-on-it) is where
that authority comes from now), the worked-example offices that
[05d §12](../data-model/05d-invariants-and-seed.md#12-what-day-one-looks-like) presented as seed, and
`role.is_system` / `audience.is_system`
([D-152](#d-152--zero-is_system-columns-what-protects-a-vocabulary-is-its-table-not-a-flag-on-its-rows)
takes the other two).
**Confirms:** `permission`, `grant_scope_type`, `selector_type`, the two effects and both enums ship. They
are the language, not configuration, and D-132's reasoning for that survives untouched: a grant naming a
code that does not exist is a save-time refusal rather than a narrow permission, and a selector added at
runtime is a word no resolver arm evaluates.

**Decision. Five parts, four of them D-132's and one of them this round's.**

1. **Day one is one account, one grant row, one code.** The account holds `system.admin` at the unit — an
   ordinary `access_grant` row with an ordinary audit row beside it — and that is the entire configuration
   of a new installation. It satisfies every check in the system, so whoever set the system up can write the
   first role, the first audience and the first grant without a second step and without a mechanism. **The
   row is not special and nothing in the model can tell it apart from a grant written a year later**, which
   is the whole point: D-068 deleted the starter bundle because bundling is the organization's job, and a
   bootstrap mechanism would have put one back through a door with `migration` on it.
2. **Three vocabularies and the enums ship** (`permission`, `grant_scope_type`, `selector_type`, `allow` /
   `deny`, `applies_to`, `right_kind`), for the reason in
   [00 §10](../data-model/00-conventions.md#10-migration-discipline): they are data the code has to agree
   with, so they arrive with the code.
3. **The catalog is the checklist, and the ten codes nobody holds are the first thing to read.** D-132
   listed them — `event.cancel`, `event.delete`, `event.organizer.manage`, `event.question.manage`, the four
   `guardianship.*`, `person_group.edit`, `person_group.end`. They stay registered with their `applies_to`
   and their sensitivity marks. What changed is what a reader should conclude from "nobody holds this": not
   *dead weight* but **not yet granted**. D-132 named them in a decision entry and no page carried them, so
   this round moved them onto [the day-one page](../data-model/05d-invariants-and-seed.md#12-what-day-one-looks-like),
   where a person setting a system up will actually meet them. **Four of the ten are `event.*` codes and
   D-151 puts them back in play**; the honest statement of what is left is in that entry, and it is a
   correction to how D-132's list reads now.
4. **Both flags go, and then all four go** — [D-152](#d-152--zero-is_system-columns-what-protects-a-vocabulary-is-its-table-not-a-flag-on-its-rows).
5. **What the page that used to list the seed is now for.** §12 was titled *What the organization starts
   with* and answered with a list of rows. It is titled **What day one looks like** and answers with a
   shape: the one account, the catalog read as a checklist, the first writes in the order they have to
   happen (a role, then an audience, then a grant aimed at it — each one visible, dated and revocable), and
   the reports that start paying for themselves on day two. **The list is gone rather than rewritten**,
   because a list of offices a new organization should create is a seed with less structure and the same
   drift problem the section's own opening block has been complaining about for four rounds.

**What the round had to give up to do this.** **A first run has no useful permissions until somebody writes
them** — D-132's cost, unchanged and now real rather than hypothetical. **`05d §12`'s drift block loses its
second half and keeps its argument**: the block's complaint was that §12 and the catalog are "the same list
written twice, and they drift", evidenced by catalog codes that no seed row granted. With no seeded roles
there is no second list to drift, so the evidence is gone; what stands is the sentence underneath it —
**with no wildcard, a code the catalog advertises and no grant names is a capability nobody can be
granted**, and check 13 reads the grants for exactly that reason. **And `05d §11`'s check 9 alerts on the
day-one row**, since its whole job is "holders of `system.admin`, and whether they can sign in" and it
alerts on change; the first change is the installation, and the first entry in that report is the
installation's own. That is correct, and it is worth saying because it is the kind of thing an operator
reads as a bug on the first morning.

**See:** [D-068](round-05.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle) (the
reason a bundle is not the design's job), [D-100](round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)
(roles are runtime data — this round only removed the exception),
[D-124](round-16.md#d-124--two-defects-systemadmin-satisfies-every-code-and-one-prose-code-named-no-row)
(what `system.admin` satisfying every code does to a report), and
[D-126](round-17.md#d-126--break-glass-is-a-report-and-a-written-procedure-not-a-mechanism) (the procedure a
world with exactly one possible holder exists for).

---

## D-151 — Creating an event writes the event's authority, and its organizers may grant on it

**Status:** decided (from your answer) and applied.
**Replaces:** the shipped `event.answer.view` grant, and 08a §8's *seed template* reading of it.
**Closes:** [08a §11's "who writes the per-event seeded grant" and "what else should be seeded to
`ORGANIZERS`"](../data-model/08a-event-guards-and-checks.md#11-open-issues), and
[catalog-b §12](../appendix/permission-catalog-b-roles-and-open-issues.md#12-open-issues)'s
`event.grant_access` question.
**Corrects:** D-132's consequence paragraph ("the organization writes that grant itself, **once**") and
D-132's part 3 ("ten catalog codes are granted by nobody at first"), both below.

**Decision.** **The act that creates an event writes the event's authority, in the same transaction as the
event row.** One item-scope `allow` per event code, aimed at an audience whose expression is the bare
operand `ORGANIZERS`, and the set of codes is **not hand-picked**: it is every code in the catalog whose
`applies_to` admits an event, which for the `event.*` family is all of them but `event.create` —
`applies_to = unit`, because "nothing owns an event, so there is no one to create one *for*". **Twelve
grants beside every event**, then, and a rule that derives them rather than a list someone has to keep in
step with the catalog. The rule is *stated once and used once today*: it is a rule about items whose people
are named by bound operands, and `ORGANIZERS` is the only set that a creation act writes for. The five
bound sets this design has (`ATTENDED`, `PLACED`, `CONFIRMED`, `ON_WAITLIST`, `ORGANIZERS`) all bind to an
event, so `person_group` and `document` have nothing to write yet, and when a module grows a set of people
connected to an item, this is what it does instead of shipping a grant.

**Three things that are not contradicted, said because each one looks like it is.**

- **[D-062](round-05.md#d-062--organizers-are-appointed-on-the-event-not-granted): organizers are appointed
  on the event, not granted.** Still true. The grant aims at a **set**; the appointment writes a roster row.
  Adding a cook changes the set and touches no grant, and the twelve rows still point at `ORGANIZERS`.
  Being an organizer confers nothing, exactly as being a treasurer confers nothing — what confers is the
  rows, and this round moved *who writes the rows* from a migration to a creation.
- **[D-100](round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape):
  an office confers nothing.** Unchanged, and this is why the round is affordable: the organizer's authority
  is twelve visible, dated, individually revocable rows, not a status.
- **[D-061](round-05.md#d-061--event-answers-are-read-by-that-events-organizers), which started all this.**
  "Answers are read by that event's organizers" is still a row in `access_grant`, still narrow, still
  deletable, still written without `MEMBERS` — an organizer appointed for one weekend is not required to be
  a paying member.

**The second half of the answer, which is the part that was not a question: organizers may grant on their
own event.** The bundle includes `event.grant_access`, and that is what it is for. A person running a camp
can give the nurse, the cook and the two assistant leaders the access they need **without holding
`access_grant.create` at the unit, and without asking anyone**. What bounds them is the shape of the grant
and nothing else — which is the same sentence the catalog already writes about
`access_grant.create`, applied to someone whose reach cannot leave the event:

- **the scope they can write is the event they run**, so nothing they grant reaches another event, a group,
  or the unit;
- **`applies_to` is the ceiling that matters here.** They cannot hand out `system.admin`, because
  `system.admin` is `applies_to = unit` and the save refuses it on an item. The structural guarantee D-099
  left behind when it deleted the level ladder turns out to be the thing that makes organizer grant-power
  safe to grant.

**And the relationship the appendix asked to have stated.** `event.grant_access` and `access_grant.create`
written on one event authorize **the same write to the same table**; the resolver matches one code exactly
([05c's rule 6](../data-model/05c-access-log-and-resolver.md)), so the difference is not what gets checked
but **which code a person was given**. The item-facing screens check `event.grant_access`; the general
permission screens check `access_grant.create`; a person holding the latter at the unit can do everything
the former does, plus everything else. *That is two codes for one write, and the round says so rather than
calling it an invariant.* What makes it survivable is that the two arrive through different doors — one is
in every event's bundle and leaves the event with it, the other is a unit-scope decision about who may
operate the permission system — and a reader who wants to know who can hand out access to a camp reads
`ORGANIZERS`, while a reader who wants to know who can hand out access *in general* reads
`access_grant.create`. **Two questions, two codes, one table.**

**The correction to D-132's consequence, which this round owed it.** D-132 wrote that with the seed gone
"the organization writes that grant itself, **once**, as an ordinary grant". Counted, that is once **per
event**, and the sentence is wrong in a way that matters: a reader who took it literally would write one
grant and expect every organizer in the system to be covered, which the bound-operand rule makes impossible
(08a §8). And D-132's part 3 said ten catalog codes "are granted by nobody at first" and named four
`event.*` codes among them. **Nineteen grants deep into a first week nobody is holding those four at the
unit**, which is what that sentence means and is still true; what it did not say, because D-132 had not
looked at events yet, is that the organizers of each event hold `event.cancel`, `event.delete`,
`event.organizer.manage` and `event.question.manage` **on that event** from the moment it exists. The
correction is recorded here and annotated on D-132 rather than pasted into its body.

**What it costs, stated as costs.**

- **`event.create` now confers a bundle, and the bundle contains ⚠⚠ data.** Whoever can create an event is
  handing read access to registrant answers — tent size, dietary notes, what a parent wrote about why their
  child is crying on the first night — to **everyone who ends up on that event's roster**, not only the
  people who were on it at the save. The widening is reachable with one code and no second person, and the
  sharpest edge is in the bundle itself: `event.organizer.manage` is one of the twelve, so an organizer can
  add an organizer and widen all eleven others at once. The catalog already marks that code ⚠ with exactly
  that note; what is new is that nobody has to hold it at the unit any more.
- **What keeps it honest is the trail and the row-ness, not a gate.** `access_log` records the reads, every
  grant is a row a screen can list and a person can end, and the answer to "who could read those answers?"
  is a query over rows rather than a story about a role. That is the design's standing answer to widening,
  the one E-6's answer leaned on last round, and this round did not weaken it.
- **`event.delete` is in the bundle and stays there** because the catalog already confines it: an event with
  registrations cannot be deleted, so an organizer's 🔒 is a thing they can only do to an empty event they
  just made.
- **`event.register_self` is in the bundle** because the bundle is derived, not curated, and it means
  almost nothing: an organizer may register themselves for their own event, which is the eligibility rule,
  not a privilege. A round that hand-picked the list would have left it out and would have had to maintain
  the omission forever.
- **An event whose twelve rows did not arrive is the same failure as ever**, and check 2 still counts it.
  Two things about that check moved, because a bundle is not a row: it is **renamed the *events with an
  incomplete organizer bundle* report**, **counts every non-cancelled event rather than only events that
  already have an organizer row** — the twelve are written at the create, while `ORGANIZERS` is still empty,
  so an event nobody has staffed is owed all twelve already — and it **names which of the twelve are
  missing**, because eleven of a bundle is the same defect wearing different clothes: a missing
  `event.answer.view` is a camp whose organizers cannot read its answers (⚠⚠, and the row the report was
  written for), a missing `event.manage_participants` is a roster nobody can fix at the gate. The older name
  survives where it was coined, in [round 10b](round-10b.md), which is right — it is what the report was
  called when it counted one row.

---

## D-152 — Zero `is_system` columns: what protects a vocabulary is its table, not a flag on its rows

**Status:** decided (from your answer) and applied. **Completes:** D-132's part 4, which deleted two of the
four. **Deletes:** `permission.is_system`, `selector_type.is_system`, `role.is_system`,
`audience.is_system`, and the second refusal in `role.delete`'s guard.

**Decision.** The design has no `is_system` column anywhere. D-132 removed the flag from the two tables that
stopped shipping rows; the same reasoning reaches the two that kept them, and once it does there is nothing
left to keep it consistent with.

**The test the round actually applied, since "it is always true" is not on its own an argument.** A
per-row flag is worth a column if some row could be false. After the sweep:

- **`permission`** — there is no `permission.create` code anywhere in the catalog, and
  [05 §9](../data-model/05-authorization.md) puts adding a grantable type at "new table + FK from
  supertable + migration". No screen writes this table and no organization can extend the vocabulary at
  runtime.
- **`selector_type`** — same, and louder: a new operand is "a decision entry, a seed row **and a resolver
  arm in one release**", so a row typed into a screen is not merely disallowed, it is a word that fails to
  parse.
- **`grant_scope_type`** — never had the column, which is the tell. Three vocabulary tables, two of which
  carried a flag that said *do not edit this*, and the third of which needed no flag because **the table is
  not editable**. That is the flag admitting it was describing the table.

**What replaces it** is the sentence those pages already carried next to the column —
[05a's](../data-model/05a-audience-and-grammar.md#the-selector-registry) "this table is written only by
migrations, and no screen edits it", [erd-a's](../appendix/erd-a-authorization.md)
*organization-read-only*. A property of a table now lives in the paragraph about the table. **The
protection is the same strength as it was, because it was never the column:** a refusal an editor performs
by reading a boolean is a friendly message, which is precisely what catalog-a wrote about `role.delete`'s
`is_system` half — "a property of the row being deleted and no index can see it… a model-layer guard there
is a friendlier message, not the refusal". The half that refused an import, a manual fix and a second client
was the foreign key, and it is untouched.

**What `role.delete` loses, and what it keeps.** The guard said: refuse if any `role_holder` row references
the role; otherwise refuse if `is_system`. **Step two protected one row** — `counselors`, the shipped office
— and there is no shipped office. Step one stays, absolute, migration-level, and it is the half that also
protects every office the organization ever writes and then stops using, which is the larger set by every
measure. **A role that clears the remaining step was created by mistake and never held**, which is exactly
what the catalog already said deleting it is.

**What this forecloses.** If a future release ever does let an organization mint its own permission code, it
must re-add the column **and** mint the code that writes the row, and the re-addition will arrive with a
decision entry explaining why this one was deleted — which is the correct amount of friction for a change
that would move a capability from the migration to a screen. **The flag was cheap to keep and cheap to
delete; what it cost to keep was a glossary definition** ("the platform shipped this, so a screen must not
destroy it") **that would have gone on implying some rows were not shipped.**

---

## D-153 — Two named audiences go, and nothing replaces them

**Status:** applied. **Deletes:** the audiences `everyone` (expression `EVERYONE`) and `all_members`
(expression `MEMBERS`), and with them
[05d §13's](../data-model/05d-invariants-and-seed.md#13-open-issues) open question about whether `code`
should be *required* rather than merely seeded on an `is_system` audience.

**Decision.** They are deleted and **nothing ships in their place**, because there was never anything in
them to replace. Each was a name over a one-operand expression, and the operand is writable anywhere: an
audience whose whole content is `EVERYONE` is worth having only if somebody is going to *name* it, and
naming is one row a person writes when they have a reason
([D-103](round-10b.md#d-103--an-audience-may-name-another-audience) is the rule that made a code useful,
and it is a rule about composition, not a request for a starter set).

**The three names people keep asking for are already answered, and the answers move to the day-one page as
guidance rather than as rows.** `unit_participants` is `MEMBERS`. `unit_leaders` is `ROLE(x)` — and the
reason that one matters is the sentence the old section carried beside it: **an expression that resolves to
nobody is silent, while every grant aimed at it looks granted**, so a role nobody has written yet is a grant
that appears to protect something and protects nothing. `guardians_of` is **nothing**: guardianship is a
channel with a `right_level` over a child, not a set an expression can name, which is why `GUARDIANS` is not
one of the thirteen operands
([D-113](round-13.md#d-113--the-guardianship-channel-has-no-expression-guardians-is-not-a-selector)).

**Two refusals die with the rows they refused, and one category survives them.**
[05b §…'s](../data-model/05b-expression-tree.md) list of things the editor refuses included *adding a person
to a seeded `is_system` audience*, and 05d §12's paragraph on the same subject closed with *the editor
should not offer to edit `everyone`'s expression*. There is no seeded audience to offer to edit. **What
stands is the category the refusals were guarding, which does not need a flag to be true**: an expression is
not a member list — `audience_member` is not a table, so "add somebody to this audience" has no row to
write, and a hand-written set of people is a sum of `PERSON(x)` leaves in an expression, not a membership
([D-105](round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)).
Stated that way it covers every audience, including ones a curator writes tomorrow, which is more than the
two refusals covered.

**And the open question goes the way most of this file's questions go: not answered, unaskable.** "Should
`code` be required on an `is_system` audience?" had no answer for three rounds because the two rows that
made it concrete were the ones being deleted; with the flag gone in both directions there is no row the rule
could apply to that is not an ordinary audience somebody named because they meant it. **§13 loses its row
and the file loses nothing a reader needed.**

---

## D-154 — `counselors` is an example now, not a shipped office

**Status:** applied. **Deletes:** the claim that `counselors` ships — ten sentences across eight pages and
one row of a seed table, counted at this round's baseline — and changes nothing about `role`, `ROLE()`, or
the argument that decided which table a permanent population lives in.

**Decision.** The name stays everywhere, and what changes is its tense. Outside the decision log,
**forty-seven lines name `counselors`**, and almost all of them are expressions —
`MEMBERS * ROLE(counselors)`, `(MEMBERS * ROLE(counselors)) + PERSON(y)` — which read exactly as well when
the office is one the organization wrote. **Ten of those lines said it ships; the rest were always examples
of composing a grant, and they were never the thing at risk.** Both counts are `git grep -n counselors` at
this round's baseline, one of them with `| wc -l` behind it, because a count written from memory in a round
whose whole subject is what a number of sentences claimed is the kind of count nobody re-checks.

**What survives untouched is the reason the name was chosen at all.** D-100's argument was about **which
table a permanent, organization-wide population lives in**, because which table decides which safeguards
follow: a *group* is "a temporary set of members that do events together"
([D-098](round-10a.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority)) and a *role* is
a named office, and putting the counselors in the group table would have let a safeguarding set dissolve
with its expiry date. That argument is about the two tables and stands exactly as written. What it never
needed was for the platform to write the row.

**One integrity consequence, and it is a new kind of empty for this design.** The import reconciliation of
D-090 counts people marked as counselors in the incoming corpus against `role_holder` rows written, which is
how a silently-empty `MEMBERS * ROLE(counselors)` gets caught. On a first run there is no such role, so the
check has nothing to reconcile and reports nothing. **That is not the check being broken; it is the check
whose subject arrives later**, and it joins the small family of reports whose day-one output is "nothing
yet" — check 13 (the whole catalog, correctly) and check 9 (exactly one holder, correctly). What the family
owes, and does not get this round, is one sentence in
[05d §11](../data-model/05d-invariants-and-seed.md#11-invariants-to-verify) saying that **a report whose
first-run output is empty or is everything is not a finding**, which is a paragraph a reader needs before
they read any of the three.

**What this round refused to do about it.** Put a list of *offices a new organization usually needs* back
onto the day-one page. It would be friendlier, it would be quoted within a round as the seed under another
name, and it would restart the drift the §12 header block has been complaining about since the round that
wrote it. **The catalog of codes is the list. Naming sets of people is the organization's own act**, which is
the entire content of D-132 and the reason the sweep was worth doing rather than reversing.

---

**What the round did not do.**

- **The four questions that survived round 20 are where they were.**
  [A-4's remainder](../open-questions.md#a-4-remainder--the-organizational-calendar),
  [E-3](../open-questions.md#e-3--guardian-acting-for-an-adult-child),
  [F-9](../open-questions.md#f-9--should-membership_type-stay-a-table-with-one-row) and
  [F-11](../open-questions.md#f-11--does-the-identity-reviewer-need-to-read-the-person-record-to-settle-a-claim).
- **[F-34](../open-questions.md#f-34) got closer to being answerable and was not answered.** It asks who
  writes the vocabulary the first import needs, and who holds `attribute.define` afterwards. Its "day one is
  not blocked, because the setup account holds `system.admin`, which satisfies every code" line is now true
  in the plainest possible way — day one *is* that account — so the question has narrowed to the part it was
  always really about: **who holds the code after the person who set the system up stops being the person
  using it.**
- **Nothing bounds what a holder of `access_grant.create` may write, and that hole is untouched.**
  [catalog-b §12](../appendix/permission-catalog-b-roles-and-open-issues.md#12-open-issues) still calls it
  the sharpest one in that file. D-151 gives an organization one **bounded** grant-writing power, which
  means a person who is nervous about handing out `access_grant.create` at the unit can hand out
  `event.grant_access` per event instead; that is a narrower option, not a ceiling, and the round says so
  rather than filing it as an answer.
- **No module grew a bundle.** The rule in D-151 is written once and used by `event`. When `person_group` or
  `document` grows a set of people connected to an item, this is what it does — and until then nobody should
  write grants for a set that does not exist.
- **No check was written without a page, and no page was given a check it cannot name.** That is the rule
  [round 19](round-19.md) closed on, and it bites here in one place: the sentence D-154 asks for — *a report
  whose first-run output is empty, or is everything, is not a finding* — is prose in §11, not check 24,
  because "was this report read with the system's age in mind" is not a query.
- **`00a` gained nothing and lost one row's citation.** No invariant of the seed's survived the seed, so no
  new shape-2 uniqueness or shape-4 immutability rule arrived; the rows that *mentioned* seeded roles and
  seeded audiences as the thing carrying a rule now cite the write that carries it. Shape 4's members are
  unchanged at seven, and a vocabulary code is still the newest of them.
- **No legal review, and nothing about this round is one.** The setup account holding everything is the
  shape with the least ceremony and the largest blast radius;
  [check 9](../data-model/05d-invariants-and-seed.md#11-invariants-to-verify) and
  [D-126](round-17.md#d-126--break-glass-is-a-report-and-a-written-procedure-not-a-mechanism)'s procedure are
  what the design offers instead of a second keyholder, and choosing between *one account* and *two people*
  is the organization's call, which is now a call it makes with a role it wrote itself.

---

**The sweep, counted off `git diff --stat` against the commit this round started from.** **Thirty-six pages
changed, 767 lines in and 432 out** — fourteen under `data-model/`, eight under `domain/`, six in the appendix,
four in this log, and one each in both glossaries, in [open-questions](../open-questions.md) and in
[the README](../README.md) — plus this page, which is new, and two files outside `docs/` (`mkdocs.yml` for the
nav, the baseline below). **D-132's estimate was twenty-five, and it was low by eleven.** Where the eleven came
from: the appendix, whose §11 was not a paragraph to delete but a table to rewrite as an example of writing a
role, and the two glossaries, which did not *mention* the seed so much as carry **entries** for it. The
estimate was wrong in the direction that made the round later than promised, and the reason it was wrong is
that it counted pages while the work counts paragraphs — a page with one sentence to change and a page whose
subject is gone are one page in `git diff --stat` and nothing like one page of reading. **What the estimate got
right is the part that mattered:** `ORGANIZERS` did appear most of those times, it is a selector, and it stayed.

**The gate ran, and it caught this round's own sentences.** `scripts/check-registries.py` finishes at **no
unbaselined finding** and `mkdocs build --clean --strict` is clean, with nothing in its INFO lines but the
banner the theme prints. The registers are **unchanged** — 70 codes, 19 deferred namespaces, 13 selectors, 5
scope types, 6 actor labels — which is the sweep's proof in the only register that checker reads: **nothing
that ships was renamed, because nothing that ships went away.** Three findings had to be met, and the first was
a defect this round wrote: twice, in [05d §12](../data-model/05d-invariants-and-seed.md#12-what-day-one-looks-like)
and in this page, a sentence named `audience.edit` as a code the setup account reaches for, **and there is no
such code** — the write is `audience.manage`. Both are fixed on the page, because a name that does not exist
has no baseline that can save it. The other three findings are refusals, and they are this round's own
argument: `permission.create` and `permission.delete` and `selector_type.edit` are spelled only to say no such
code exists, which is what D-152 substituted for the flags, so three lines went to
`scripts/registry-baseline.txt` with the reason after the `#`.

**One more count, from the checker rather than from a sentence.** Registered codes named nowhere outside the
catalog went from **ten to four** between the commit before this round and this one — and the ten that started
it are *exactly* the ten [D-132](round-18.md#d-132--day-one-is-one-account-holding-systemadmin-and-every-role-after-it-is-written-by-the-organization)
called "granted by nobody at first". Six of them are now named on the day-one page, because this round had to
write that list out to say it was no longer a seed; four remain uncited, all four `guardianship.*`. **That is
D-132's point 3 measured:** "the list the organization reads in order to decide what to grant" was, until
today, a list no page read, and a sweep whose whole claim is that the catalog is the checklist left six codes
newly legible and four still not. **The habit this page should have learned from round 20 and did not:**
three of this page's own links were dead when the build checked them — `00 §5` for a naming convention that
lives in §2, `08a §12` for open issues that live in §11, and [D-098](round-10a.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority)'s
heading slug written from memory instead of recomputed. Two are a section number read rather than looked up and
the third is the exact failure round 20 named one page earlier.
