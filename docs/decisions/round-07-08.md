# Decision Log — Refinement rounds 7 and 8 (D-082 … D-090)

> Personal data as one class, organization-defined attributes, the audit trail that holds values, merge chains, two retention clocks, and what the legacy corpus actually is.

[Refinement round 6 — the no-SQL round (D-072 … D-081) ←](round-06.md) | [All decisions](index.md) | [Refinement round 9 — organization (D-091 … D-096) →](round-09.md)

**Why four whole questions about identity changed no table.** They were questions about the organization rather than about the model, and three of the four were answerable simply by looking at what the organization already has: a roster with no money in it settled a rule that had been written as a default, and a wanted feature settled a trade that had been written as an assumption. The fourth — the two retention clocks — was settled by deciding that the two halves of a person's record are allowed to age differently. That is why they were worth holding to the end rather than asking first.

---

## D-082 — A direct message to a minor is mirrored to the minor's guardians

**Status:** decided (from your answer) — **closes MSG-1**
**Date:** refinement round 7
**Follows:** [D-077](round-06.md#d-077--messaging-is-direct-by-default-broadcast-is-an-ordinary-scoped-permission-and-the-recipient-chooses-the-channel)

**Your answer.** Asked which of the two available safeguards you wanted, having been shown that
[D-077](round-06.md#d-077--messaging-is-direct-by-default-broadcast-is-an-ordinary-scoped-permission-and-the-recipient-chooses-the-channel)
had declined the sender restriction and left nothing in its place, you chose **mirror to guardians**.

**The rule.** A direct message whose recipient is a minor is delivered **also** to that minor's
guardians, and the sender is told, before sending, that it will be. Nothing is blocked. No permission
is involved, and no check in the resolver looks at an age.

**Why this direction and not the other one.** The corpus already refused an age branch at check time,
for events, in [D-070](round-05.md#d-070--an-event-has-no-age-ceiling-the-grant-is-the-rule), on the ground that a
condition the capability model does not know about is the first rule in a rule engine nobody asked
for. Messaging was going to reintroduce exactly that condition by a different door. Mirroring gets
the safeguarding property without it: **the property nobody was ever arguing for was "an adult cannot
reach a child", and the property actually needed was "no private exchange about a child is secretly
unread."** Those are not the same rule, and only the second one survives contact with a volunteer
organization, where a restriction that inconveniences a leader on a Friday evening gets bypassed by
Monday — and a routinely-bypassed restriction is worse than none, because it teaches everyone that the
rule is decorative.

**Three things "mirror it to the guardians" does not say, settled here rather than in code:**

1. **Which guardians — those at `view` or `write`.** A guardian whose right level is `none` receives
   nothing. `none` is not an oversight; it is the organization having already decided that this party
   sees nothing about the child, and a safeguarding convenience is not a reason to reverse a recorded
   decision as a side effect of a message.
   **The consequence is named rather than left to be found:** a minor whose guardians are *all* `none`
   is exactly as unwatched as a minor with no guardian row at all, so both are reported together by
   the existing completeness check in
   [04-relationships §6](../data-model/04-relationships.md#6-invariants-to-verify). Mirroring must not
   become a channel through which `none` quietly stops meaning anything.
2. **Which set, as of when — frozen at send time.** The guardianships open at the moment the message
   is sent are the recipients, recorded into the delivery. A guardianship closed later does not lose
   its copy; a guardian added later does not acquire old threads. This is the same discipline that
   makes the audit log answer "what did this role say on that date" rather than "what does it say
   now" ([06-audit §2](../data-model/06-audit-and-import.md#2-audit_log)) — a safeguarding question
   about a past message has to be answerable against the arrangement that existed then, because the
   question "did anyone tell the father?" is asked months later, about a family that has since
   separated.
3. **Broadcast is not mirrored.** A scoped broadcast is addressed to a set, recorded, attributable,
   and not private; mirroring exists precisely for the private case, where "nobody saw this" is a
   claim nobody can check. Extending it to broadcast would deliver the same content twice to the same
   guardians and would blur the one distinction the rule depends on.

**What mirroring is explicitly not.** Not approval — nobody consents before a message is sent, so the
channel stays open and the organization stays out of the middle of ordinary communication. Not
delivery confirmation; the mirror inherits the recipient's own channel choice
([D-077](round-06.md#d-077--messaging-is-direct-by-default-broadcast-is-an-ordinary-scoped-permission-and-the-recipient-chooses-the-channel))
and can therefore fail to be read exactly like any other message. And not a record of concern: it is
a copy, not a report, and the organization learns of a message only through the ordinary routes.

**The variant rejected, and why it will come back.** *"Only guardians and unit leaders may message a
child."* It is the sender rule wearing the visibility rule's clothes: it needs the age branch, it is
bypassed the first time it is in the way, and worst of all it **tells a child that the adult messaging
them has been vetted** — a claim the system cannot support, since no background checks are recorded at
all ([D-043](round-02-03.md#d-043--no-background-checks-are-recorded-in-this-system)). Recorded here because the
proposal is intuitive and will return.

**Impact.** One mirroring rule, one notice to the sender, one extended completeness report. No new
permission, no resolver branch, no new table. **The undesigned module now has a constraint on it
before it is designed**, which is the point of taking this decision early: a messaging design that
ships private delivery to minors with neither restriction nor mirroring would have to be reopened
after the fact, when the storage of message bodies and the retention policy are already fixed.

**See:** [MSG-1, closed](../open-questions.md#msg-1),
[permission-catalog](../appendix/permission-catalog-b-roles-and-open-issues.md#10-deferred-namespaces),
[glossary — Mirroring](../glossary.md#communication).

---

## D-083 — There is no medical record: personal data is one class of data

**Status:** decided (from your answer) — **closes E-7, resolves H-0, retires the health module**
**Date:** refinement round 7

**Your answer.** *"I consider everything apart from name, gender and age a 'medical record'. It is
fields in the database, not files. In general, ignore 'court order', guardian has all rights on a
child if it's permissions say so. Medical data is not different in any way."*

**This was asked as a scoping question and it answered itself a size larger.** The question on the
table was how to protect a health module. The answer removes the category: there is no privileged
subset of the person record, because the whole thing is equally the sensitive thing. Name, gender and
age are identity — they are what a person is *called and counted as*; everything else the system
knows is descriptive data of one kind, held in fields, and none of it is a different kind of object
from any other.

**Four things this dissolves, and none of them quietly:**

| What the documents said | What it means now |
|---|---|
| **E-7**: one right level cannot separate the medical record from the profile | **Closed, because the sentence describes something nobody wants.** "Read everything except the diagnoses" was the case the eighteen `dependent.*` codes were built for; the answer is that the case is not real and the exception is not wanted. The guardian's right level applies to the record, whole, and that is the end of it |
| **H-0**: the medical record is cited by five files and defined by none | **Resolved by removing the referent, not by building it.** Nothing was hiding behind the phrase; the phrase was inherited from deleted permission codes |
| *"a `view` guardian already sees them"* — the reason the module was deferred | It was false (there was nothing to see) and it is now moot: a `view` guardian sees the person's data, which is the same sentence with a table behind it |
| *"the medical file, which no event permission reaches"* — 08-events' reassurance | **Corrected, not restated.** No file, no reach. See [D-085](#d-085--the-identity-machinery-stays-structured-the-boundary-is-rules-not-sensitivity) for who reads what instead |

**The court-order case, refused on the merits rather than waved away.** The granular model existed for
one story: a parent with access to everything about their child except the medical file, by order of a
court. That story was the entire justification for a sensitive sub-resource, and it is declined —
**a guardian's rights are what the guardian's permission says, and no data inside the record changes
that.** It is worth recording what was traded, because the story is not absurd: the model now cannot
express an arrangement a court might order. The trade made is that a system which cannot express it
**fails visibly** — a guardian either has the access or does not, in one place, auditable — whereas a
system that can express it has a per-field exception nobody outside a courtroom can configure
correctly, and a list of eighteen codes is a list somebody ticks without reading.

**Where protection actually lives now — three places, two of them machinery and the third a sentence
somebody has to keep true:**

1. **Grants.** Whoever holds `person.view` over that person's scope reads the record. This is why
   [the permission catalog](../appendix/permission-catalog.md) raises `person.view` rather than
   inventing a code: a permission that reads everything about a child is not a ⚠, it is in the top
   tier.
2. **The guardian right level** ([D-074](round-06.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular)),
   applied to the whole record.
3. **The guard on the audit trail** ([00-conventions §8 item
   7](../data-model/00-conventions.md#8-personal-data-and-erasure)) — the trail quotes the whole
   record, so the permission that opens it is graded accordingly. Erasure reaching it is unchanged and
   absolute.

**The one thing that must not survive the round: protection keyed by field name.** The redactor used
to scrub a *list of sensitive keys* out of logged row images. That list was coherent when there was a
sensitive subset; with one class of data it is a list of exceptions to a rule that has no exceptions,
and it fails on the first value stored under a column named `note` — or under a code named `allergy`,
which is worse, because the attribute layer generates such names faster than anybody can list them.

**What replaces it, after one reversal inside this same round.** The first answer written down here was
that the audit payload therefore carries no descriptive values at all: who changed which code, for
whom, when, and that a value existed. **That rule is withdrawn, and it was withdrawn by this decision's
own logic.** Stripping attribute values from the trail while a change of address is logged with its old
and new values is a sensitive *subset* of the person record re-enacted in the logging rules — the
privileged corner arriving as a list of table names after it was refused as a list of permission names —
and it empties the history that [D-085](#d-085--the-identity-machinery-stays-structured-the-boundary-is-rules-not-sensitivity)
chose overwrite-in-place in order to have. **So the trail holds the values, and what rises instead is
the guard: an audit entry about a person is as sensitive as the person data it quotes, which puts
`audit.view` in the catalog's top tier next to `person.view`.** That is a line in a document rather than
a mechanism, and it is the weakest link in this design on purpose, so that a reader can see where the
protection actually sits
([09-attributes.md §6](../data-model/09-attributes.md#6-erasure-retirement-and-the-audit-payload)
argues it through, [06-audit-and-import.md §2.2](../data-model/06-audit-and-import.md#22-redaction-before-logging)
keeps the withdrawn rule visible). Erasure reaching the payload is unaffected and remains absolute.

**What is genuinely lost.** The ability to say *"everything except the diagnoses"* — to a court, to a
doctor, to a future board that wants a narrower access tier. It is lost deliberately. If the case ever
arrives in reality the way E-7 hoped it would not, the fix is a **second grant scope over a defined set
of data**, taken as a decision with these documents in front of the reader, and **not** the return of
a code list: one scope, argued once, rather than eighteen flags that encode the same distinction in
the names of permissions nobody reads.

**See:** [D-084](#d-084--descriptive-data-is-organization-defined-at-runtime),
[D-085](#d-085--the-identity-machinery-stays-structured-the-boundary-is-rules-not-sensitivity),
[data-model/09-attributes.md](../data-model/09-attributes.md),
[domain/08-person-data.md](../domain/08-person-data.md).

---

## D-084 — Descriptive data is organization-defined at runtime

**Status:** decided (from your answer)
**Date:** refinement round 7
**Follows:** [D-083](#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)

**Your answer.** Asked whether the field vocabulary is a fixed typed set, a hybrid, or entirely
organization-defined, you chose **entirely organization-defined**; on typing, **typed for rendering,
not for law**; on curation, **values anywhere, codes by permission**; on retirement, **a retired code
keeps its values, redaction erases**.

**Decision.** Two tables. **`attribute_definition`** is the vocabulary the organization maintains:
a code, a label, a value type, whether several values may be open at once, and a status of live or
retired. **`person_attribute`** is a value one person has: the definition it belongs to, the value,
who recorded it and when. Nothing in the schema names a fact about a scout.

**Why this is the shape and not the safer-looking one.** The alternative — a column per fact — makes
every collection habit a release. This organization's list of things it wants to know changes with the
program: shoe sizes for a camp season, an insurance number for one country's requirement, a
preferred contact language for one intake. A schema where that needs a migration produces the real
failure instead of the apparent one: the field does not get added, and the information is collected on
paper, photographed, and lost. **[D-083](#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)
removed the argument for a fixed set** — a closed typed set is justified by needing to *constrain* the
important fields, and the answer was that no field is more important than another.

**Typing for rendering, not for law.** A definition declares text, number, date, yes/no, one-of-a-list,
or free text with a unit. The system uses it to draw the right input, to sort a list, and to warn —
*"that is not a date"* — and it does not use it to refuse a save a human insists on. The reason the
warning must not be a wall is that the value is not the system's to overrule: `2019` as a year for
`last_checkup` is a truer record than an empty field behind a validation error, and the person typing
it knows and the form does not. **What this costs is stated plainly in
[09-attributes §5](../data-model/09-attributes.md#5-what-this-design-cannot-do)**: no database type
checking, no constraint can reference a value, and no report may assume it understands a code.

**Curation, because a vocabulary is the design.** Anyone who may edit a person may record a value
against an existing code. Creating a code needs **`attribute.define`**, which is a small permission
held by few people. An improvised need at 23:00 is recorded as a **proposal**: the value is written
into an uncatalogued code that is visible, unusable-by-default, and waiting for whoever curates the
vocabulary to accept, rename, or merge it. The reason is the one failure this design is exposed to
more than any other: an open vocabulary left open becomes `allergy`, `Allergy`, `alergie` and
`allergies (2)`, after which the layer still stores everything and answers nothing — which is the
entirety of what the attribute table was built to do.

**Two rules that keep a runtime vocabulary from decaying immediately:**

- **Codes are normalized before comparison** — trimmed, case-folded, whitespace-collapsed — and
  uniqueness is checked against the normalized form. This is not a nicety; it is the difference
  between four spellings surviving a week and four spellings surviving a decade, and it is a rule the
  database *can* still enforce.
- **Retiring a code never deletes values.** A retired code disappears from data entry and remains
  readable, reportable, and revivable. Deleting the label must not delete the fact underneath it —
  a code discovered to have been badly named is an administrative event, and if it destroys nine years
  of records it will never be retired, and the vocabulary accretes instead of being curated.
  **Redaction is the opposite case and the only eraser:** when a person is anonymised
  ([00-conventions §8](../data-model/00-conventions.md#8-personal-data-and-erasure)), their values go.

**See:** [data-model/09-attributes.md](../data-model/09-attributes.md),
[D-085](#d-085--the-identity-machinery-stays-structured-the-boundary-is-rules-not-sensitivity),
[open question F-10](../open-questions.md#f-10)
for which of its rules the attribute layer can and cannot express.

---

## D-085 — The identity machinery stays structured; the boundary is rules, not sensitivity

**Status:** decided (from your answer)
**Date:** refinement round 7
**Follows:** [D-083](#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data), [D-084](#d-084--descriptive-data-is-organization-defined-at-runtime)

**Your answer.** Asked where the attribute layer starts, you chose **keep the identity machinery
structured** — attributes take everything that has no table today, not the tables that exist.

**The boundary, and it is a different boundary than "sensitive versus ordinary".**

| Stays structured | Becomes attributes |
|---|---|
| `person_name` history, `gender`, `birth_date` + `birth_date_precision` | health and medical facts, education, occupations, languages, insurance, measurements, dietary habits, preferences, notes — everything with no table today |
| `person_contact` — purpose, primary flag, validity period | |
| `person_identifier` — per-scheme uniqueness, decided by the scheme ([D-080](round-06.md#d-080--five-contradictions-the-translation-surfaced-and-how-each-was-resolved) item 1) | |
| `account`, `account_credential` | |

**The test is whether a rule exists that the attribute layer physically cannot hold.** *"Exactly one
primary postal contact among the open rows"*, *"a school id may repeat but a birth number may not"*,
*"this person has one current name"* — each is a constraint over a **known set of columns**, and a
key/value table has no known set. Folding those tables in would not have simplified the model; it
would have moved four working constraints into application code and called it uniformity, which is
[F-10 shape 3](../open-questions.md#f-10)
manufactured on purpose. **Descriptive data is open-ended because nobody can enumerate it; identity is
closed because it was enumerated years ago and has not changed.** That is the whole boundary.

**Values are overwritten; `audit_log` is the history.** Chosen over a history table, and worth
noticing as a **departure from the shape guardianship uses**, where
`guardianship_permission` keeps current value plus history. The difference is real and not
inertia: a guardianship row is **authority**, and authority is asked "what was it on that date" as a
routine part of answering whether an action was permitted — while a descriptive value is a description,
and nobody queries the allergy list of 2019 except in an incident, which is exactly the case the audit
trail exists for. **The dependency is stated rather than glossed, and it has two halves.**
[D-081](round-06.md#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now)
records that audit completeness is now a discipline rather than a guarantee, so choosing the trail as
the only history buys simplicity with the one control the corpus admits is weakest — and the trail here
is not a pointer into the record, it is **the only copy of the values that ever existed**, since the row
itself holds one belief at a time. So the history exists if, and only if: **(a)** every write path
writes its audit row, including the import, the sweep and the hand-fix, and **(b)** the trail is guarded
as the copy of a child's whole record that this makes it
([D-083](#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data) records why the values
are logged rather than stripped, and what that demands of `audit.view`). If a safeguarding question is
ever unanswerable because the trail was not written, or answerable by somebody who should not have been
able to answer it, this is the decision that made that possible, and it should be reversed with those
two sentences in front of the reader.

**Who reads it: whoever the grants already say.** A unit leader holding `person.view` over their own
unit's members reads their descriptive data — no age branch, no special channel, no per-event grant,
consistent with [D-083](#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)'s
"not different in any way". **This changes D-061's status without reversing it:** the per-event answer
form was designed as *the only* route by which an organizer learns a child has a nut allergy, because
nothing else was readable. It is now the fallback for a fact the organization has not recorded, rather
than the ceiling on what an organizer may know — and the discipline in
[08-events §7](../data-model/08-events.md#health-facts-and-the-discipline-this-requires) about what
belongs on a form survives unchanged, because it was always about not re-collecting what the
organization already holds.

**Amends [D-061](round-05.md#d-061--event-answers-are-read-by-that-events-organizers).** Its decision stands —
answers are read by that event's organizers — but its premise that this is the only route to a health
fact is superseded by this entry.

**See:** [data-model/09-attributes.md](../data-model/09-attributes.md),
[domain/08-person-data.md](../domain/08-person-data.md),
[data-model/01-identity.md](../data-model/01-identity.md).

---

## D-086 — A sensitivity mark grades what a grant exposes, not the table it reads

**Status:** decided — **by the assistant, during round-7 propagation, not from an answer of yours.**
It follows mechanically from [D-083](#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data),
which is why it was taken rather than asked, but it changes two rows of a table you will read, so it is
numbered and flagged rather than folded into prose. Reverse it if you read the marks differently.

**Date:** refinement round 7
**Follows:** [D-083](#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data),
[D-085](#d-085--the-identity-machinery-stays-structured-the-boundary-is-rules-not-sensitivity)

**The problem the round produced.** Two codes were found to be graded against their table's reputation
rather than their payload's contents. `audit.view` sat at ⚠ while
[D-085](#d-085--the-identity-machinery-stays-structured-the-boundary-is-rules-not-sensitivity)
had just made its `old_values`/`new_values` the only surviving copy of a child's descriptive values — a
log read by people who need not hold `person.view`, holding more than `person.view` shows.
`event.answer.view` sat at ⚠ beside a note conceding that the answers under it "can be clinical".

**Decision.** The mark follows the content. **`audit.view`, `event.answer.view` and `person.view` are
all ⚠⚡**, and the legend's top tier was reworded so it names *whose* data a grant exposes instead of
naming a category of fields — "children's personal data, or the same about an adult where the code reads
a whole person record". Wording matters here more than usual: the previous legend read "children's
personal data **or health data**", which is a category D-083 deleted, and a legend that names a category
invites somebody to write the code that separates it.

**What a raise does and does not do.** It changes **no grant, no scope and no channel.** An event's
organizers still read that event's answers with no additional gate
([D-061](round-05.md#d-061--event-answers-are-read-by-that-events-organizers) stands); an auditor still reads the
trail. A mark is the sentence a reviewer reads before ticking a box, and the reason it was worth two
rows is the seed roles: `auditor` is now honestly described as a ⚠⚡ read over everything the system has
ever believed about a child, which "just the logs" concealed, and `event.answer.view` arriving in a role
handed to thirty volunteers is now visible at a glance.

**Where this is enforced: nowhere.** A sensitivity mark is a line in
[the catalog](../appendix/permission-catalog.md#1-conventions), reviewed by a human, and
the check that a payload's contents match its code's mark does not exist and cannot be written against a
runtime vocabulary — see [AT-4](../open-questions.md#at-4),
which asks whether one permission is the right shape for a trail that holds person data at all.

**See:** [appendix/permission-catalog.md §8](../appendix/permission-catalog-a-codes.md#8-audit-and-system),
[data-model/09-attributes.md §6](../data-model/09-attributes.md#6-erasure-retirement-and-the-audit-payload).
---

## D-087 — Merge chains stay, because reversing a merge is a supported operation

**Status:** decided (from your answer)
**Date:** refinement round 8
**Follows:** [D-004](round-01a.md#d-004--no-automatic-merging-ever),
[D-056](round-04.md#d-056--the-legacy-import-expects-a-large-corpus-with-legacy-member-numbers)

**Your answer.** Asked whether the system must be able to reverse a merge that a human approved —
framed as the question that decides B-2, since chains make a reversal a replay and flattening makes it
a rebuild — you chose **chains, and an explicit unmerge**.

**Decision.** `person.merged_into_person_id` stays a pointer that is *not* rewritten forward when the
survivor is itself later absorbed. A→B→C remains a chain and `resolve_person()` keeps walking it
([01b-merges-views-and-checks.md §9](../data-model/01b-merges-views-and-checks.md#9-views)). Flattening is now **closed off**, not
merely slower.

**What this decision actually changes is the direction of the argument.** These documents have argued
for chains *because* unmerge would otherwise be impossible — an assumption resting on a capability that
nothing had asked for. You have asked for the capability, so the reasoning runs the other way now:
unmerge is a requirement, and chains are its consequence. That matters for how the rule is defended
later, because "flattening is faster" is no longer a trade being weighed against an abstract
tidiness — it is a trade against a feature someone named.

**Two rules a permanent chain needs, and neither existed until this entry.**

1. **A cycle cannot be created, and the place it cannot be created is the merge, not the read.**
   A merge is refused when the person chosen as survivor resolves — by walking the chain — to the
   person being absorbed. That includes the one-hop case already ruled out (nobody merges into
   themselves) and the case that actually happens: absorbing B into A when A has already been absorbed
   into B. Checking at write time is the whole guard; a read-side step limit would merely decide which
   of two wrong answers to return.
2. **Chain length is a signal, not an error.** Resolution has no hop limit — a bound would silently
   return a tombstoned id, which is the failure the function exists to prevent. Instead, a chain longer
   than **three hops** is reported. Four merges in a row on one line of people does not mean the data
   is odd, it means the matcher is producing duplicates faster than a human can settle them, which is a
   statement about the queue and not about the row.
   [08a-event-guards-and-checks.md §10](../data-model/08a-event-guards-and-checks.md#10-integrity-checks) stated this as a breach and
   is corrected: with chains decided, *a survivor that has itself been absorbed is normal*, and only the
   length means anything.

**What was already built, and is confirmed rather than changed.** `person_merge` exists and is
append-only with `reversed_at`/`reversed_by`/`reversal_note`, so an unmerge records that a merge was
undone instead of erasing the record of the mistake
([01b-merges-views-and-checks.md §8](../data-model/01b-merges-views-and-checks.md#8-identity_hypothesis-and-person_merge)); and the
reversal procedure is written in four steps
([domain/03-identity-and-legacy.md §6](../domain/03-identity-and-legacy.md#6-reversing-a-merge))
— tombstone off, rows created *before* the merge go back, rows created *inside* the merged window are
flagged for a human, and every `access_grant` from that window is flagged rather than guessed.
**That asymmetry is the honest core of this entry: a merge can be undone and the merged period cannot
be.** Whatever those two humans did while they were one row stays one row's history, because the grants
exercised in that window were really exercised by somebody who can no longer be identified from the
record. Two further things follow and are stated where they belong:

- **Reversal needs no new permission.** Unmerging is the same act as merging — an identity correction
  made by a named human — so it is `person.merge`, already held by the identity reviewer. A
  `person.unmerge` code would grade undoing a mistake as safer than making one.
- **The resolve-on-entry rule now has a check under it.** "Every place that accepts a person id from
  outside must call `resolve_person()`" is a rule application code can forget, and D-072 removed the
  database-level ways of catching it; the net is a report for live rows that reference a tombstoned
  person, which is the only form of this failure that is visible afterwards.

**Closes:** [B-2](../open-questions.md#b-2).

**See:** [data-model/01b-merges-views-and-checks.md §9–§10](../data-model/01b-merges-views-and-checks.md#9-views),
[domain/03-identity-and-legacy.md §6](../domain/03-identity-and-legacy.md#6-reversing-a-merge).

---

## D-088 — The accounting skeleton is permanent; the audit trail is short

**Status:** decided (from your answer). The retention *periods* are a policy you have chosen; whether
they survive a legal review is a different question and stays open, recorded as an assumption with a
name attached rather than as settled law.

**Date:** refinement round 8
**Follows:** [D-083](#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data),
[D-085](#d-085--the-identity-machinery-stays-structured-the-boundary-is-rules-not-sensitivity),
[D-086](#d-086--a-sensitivity-mark-grades-what-a-grant-exposes-not-the-table-it-reads)

**Your answer.** Of the four retention shapes, **the skeleton stays and the trail ages out**:
membership and fee history is the organization's own record and is kept indefinitely; the audit trail
keeps its values for a bounded window and is then reduced to who did what to which row, when.

**Decision — two clocks, and they are deliberately opposite.**

- **`membership`, `fee_obligation`, `payment` and the anonymised `person` row: no clock.** An erasure
  redacts the person and leaves this skeleton standing, which is the shape
  [00-conventions §8](../data-model/00-conventions.md#8-personal-data-and-erasure) already required;
  what is new is that it is now *because it is the organization's history* rather than because nobody
  decided when it ends. `redaction_log.retained_reason` has a real value to hold.
- **`audit_log`: payloads live 24 months, rows live forever.** After the window a row is **reduced** —
  its `old_values`/`new_values` are emptied and everything else survives: actor, on-behalf-of,
  operation, table, record id, changed fields, transaction, session, channel. The trail keeps
  answering *"who changed this, and when, and were they allowed to"* for as long as the system exists,
  and stops answering *"and to what"* after two years. Twelve months is the floor the window may be set
  to; anything shorter stops covering a full year of a child's activities, which is the unit an
  incident is asked in.

**A third operation on the trail, and it is not redaction.** These documents say
[D-072](round-06.md#d-072--the-documentation-carries-no-sql-the-schema-is-the-orms-job)-era
([06-audit-and-import.md §2.2](../data-model/06-audit-and-import.md#22-redaction-before-logging)) that
redaction runs on the way in and *"never in a cleanup job that might not run"*, and that sentence is
about a secret that must never have existed in the table. **Reduction is the opposite case and must not
be argued from that sentence**: its entire purpose is to happen later than the write, and its failure
mode is that it does not run at all. So it is a scheduled job with a check on it — a row older than the
window still carrying a payload is a finding that alerts — and the two rules coexist without
contradiction because one forbids late *unwriting of a credential* and the other requires late
*unwriting of history*.

**What this buys, at a price, and both halves are recorded.**

- **It answers [D-086](#d-086--a-sensitivity-mark-grades-what-a-grant-exposes-not-the-table-it-reads)
  more cheaply than any guard could.** The exposure that decision accepts is a wrongly-graded
  `audit.view` reading a child's descriptive values. The window does not fix that — it **bounds how
  long it can**, which for a small organization is the realistic control. This is the strongest argument
  AT-4 will receive and it is not an argument for keeping one permission forever; it is an argument for
  keeping the payload short.
- **It puts a horizon under [D-085](#d-085--the-identity-machinery-stays-structured-the-boundary-is-rules-not-sensitivity),
  and that has to be said plainly rather than discovered in an incident.** Overwrite-in-place was chosen
  because the trail is the history. Now the trail's values expire. So *"what did we believe about this
  child's allergy list in 2019"* is unanswerable **twice over**: the values were never kept in the
  business rows, and after 24 months they are nowhere at all. The real cost of D-085 is therefore not
  "no temporal columns", it is *no long history* — three accepted things stacked: values live in one
  overwritten row, the copy of them depends on a write path remembering to log, and the copy ages out.
  **If a case ever needs the long version, the fix is temporal columns on the value — D-085 reversed —
  and not a longer trail**, because stretching the trail stretches the thing D-086 graded and D-083
  refuses to keep separately.

**Erasure is unaffected and still immediate.** A redaction scrubs that person's values from payloads
whatever their age; the window is a ceiling on how long anything can be there, not a waiting period.

**Legal status of the "forever" half.** Indefinite retention of `membership` and fee rows about a named
person is a claim that needs a basis, and this log is not the place that grants it. What the corpus
states now, as an **assumption pending review**: organizational history plus accounting obligations,
against a redacted person row that keeps the skeleton non-identifying — and the review is the same one
B-3 already names, now with a concrete policy to review rather than a blank.

**Also decided from here:** `access_log` takes the same window as `audit_log`'s payloads as a proposed
default (**F-8**, which needs your confirmation, and which is a weaker question because
[05-authorization §9](../data-model/05c-access-log-and-resolver.md#9-access_log) keeps the payloads of *reads*
out of that table to begin with).

**Closes:** [B-3](../open-questions.md#b-3).

**See:** [data-model/06-audit-and-import.md §2.2](../data-model/06-audit-and-import.md#22-redaction-before-logging), [§4](../data-model/06b-redaction-and-checks.md#4-redaction-log) and [§6](../data-model/06b-redaction-and-checks.md#6-open-issues),
[data-model/00-conventions.md §8](../data-model/00-conventions.md#8-personal-data-and-erasure),
[data-model/09-attributes.md §6](../data-model/09-attributes.md#6-erasure-retirement-and-the-audit-payload).

---

## D-089 — One live account; a colliding sign-up files a claim and creates nothing

**Status:** decided (from your answer)
**Date:** refinement round 8
**Follows:** [D-004](round-01a.md#d-004--no-automatic-merging-ever),
[D-056](round-04.md#d-056--the-legacy-import-expects-a-large-corpus-with-legacy-member-numbers)

**Your answer.** Asked what happens when a person who already has an account signs up again with a
different e-mail: **refuse, and queue a claim** — not an automatic link, and not a second account.

**Decision, stated as the gate that enforces it.** One live account per person stands
([01a-accounts-and-contacts.md §4](../data-model/01a-accounts-and-contacts.md#4-account)) and is joined by a second rule: **an
account may not reach `active` while an unresolved `identity_hypothesis` names its person.** That is the
whole mechanism — there is no new table and no new queue, because the identity review queue already
exists, already records its signals, and already has the reviewer role for it. A sign-up that
strong-matches an existing person runs into that gate on its way to being usable, the person who typed
it sees a holding message, and a human decides.

**The trigger is a strong match only, and the threshold is the load-bearing part.** A hypothesis is
raised at sign-up on an exact legacy member number, or an exact birth date together with a normalized
name match — the same signal set [domain/03 §4](../domain/03-identity-and-legacy.md#4-match-signals)
already weights, at the top of its band. **The soft band must not raise one.** Blocking a stranger's
registration on a fuzzy score is the failure this rule would most deserve, and the cost of letting a
true duplicate through is bounded, reviewable and nightly-matched anyway; the cost of stopping a new
member is a child who cannot sign up to a camp on the day the form closes.

**Two costs, both accepted in the open.**

- **A brand-new person who happens to match waits for a human.** So the blocking condition gets an age
  check shaped like `field_conflict`'s thirty days, and it alerts rather than logs, because a stalled
  identity queue is no longer a data-quality problem — it is a specific person who cannot log in and
  has no way to say so except to telephone someone.
- **The refusal must not confirm that an account exists.** The holding message says the request was
  received and will be checked. It says nothing about whether the name, the birth date or the number
  matched anything, because a sign-up form that answers "yes, that person exists" is an existence
  oracle over the roster, and this system's roster is children
  ([05-authorization.md](../data-model/05-authorization.md)).

**What the answer refuses, and why those were the alternatives.** *Link automatically once the e-mail
is verified and the signals are strong* would have been the convenient one and is
[D-004](round-01a.md#d-004--no-automatic-merging-ever) under another name: a false-positive merge is a privacy
incident in which one human's medical data becomes another human's record, and the merge is the hard
part to undo even with [D-087](#d-087--merge-chains-stay-because-reversing-a-merge-is-a-supported-operation)'s
reversal. *Allow two live accounts* drops the uniqueness rule and splits a person's consents, payments
and attributes across two ids until somebody notices — and the records that must be complete are
exactly the ones where nobody notices.

**The everyday case is not the collision case, and it is worth naming so this rule is not oversold.**
"I have a new e-mail address" is not a second account and was never one: `account_credential` holds
many credentials for one account, so a new address is an *addition* to the login a person already has.
The collision case is narrower than "signing up twice" — it is a person arriving through a door the
system did not know they had.

**No new permission.** Resolving a claim is confirming or rejecting a hypothesis, which is `person.merge`
and already sits with `identity_reviewer`. Note the seed role still has no read over the *person record*
(`person.view` is not in it), so a reviewer decides identity questions from signals and names. That is
defensible — the signals *are* the decision — but [D-089](#d-089--one-live-account-a-colliding-sign-up-files-a-claim-and-creates-nothing)'s
gate means a reviewer's answer now decides whether a child can log in, which is more than tidying a
queue, and it is registered as
[F-11](../open-questions.md#f-11--does-the-identity-reviewer-need-to-read-the-person-record-to-settle-a-claim)
rather than settled here.

**Closes:** [B-4](../open-questions.md#b-4).

**See:** [data-model/01a-accounts-and-contacts.md §4–§5](../data-model/01a-accounts-and-contacts.md#4-account) and [§8](../data-model/01b-merges-views-and-checks.md#8-identity_hypothesis-and-person_merge),
[domain/03-identity-and-legacy.md §4](../domain/03-identity-and-legacy.md#4-match-signals).

---

## D-090 — The legacy corpus is thousands of roster rows with numbers and no money

**Status:** decided (from your answer)
**Date:** refinement round 8
**Follows:** [D-056](round-04.md#d-056--the-legacy-import-expects-a-large-corpus-with-legacy-member-numbers),
[D-041](round-02-03.md#d-041--belonging-to-a-sub-unit-is-a-participation-record-not-a-membership),
[D-084](#d-084--descriptive-data-is-organization-defined-at-runtime)

**Your answer.** Thousands of roster rows, **one export**, 1990s to now, carrying a legacy member
number, **no payment data**, and free-text columns alongside.

**The consequence that does most of the work: the corpus decides the question the import was going to
default.** [06-audit-and-import.md §6](../data-model/06b-redaction-and-checks.md#6-open-issues) had kept
open whether a historical roster should create a `membership` or only a `unit_participation`, with
"participation unless there is payment evidence" as the safe default. **There is no payment evidence in
the corpus at all**, so the default's exception has an empty set: every imported historical row is a
participation, and `membership` rows come only from the current register. A conditional rule with one
arm is not a safe default, it is the rule, and saying so retires the question rather than answering it.
The stakes were already named in D-041 and
[D-039](round-02-03.md#d-039--member-permissions-require-a-current-paid-membership): an inferred open-ended membership
would make every 2003 roster a *current member* with authority today.

**The vocabulary arrives all at once, which changes how the mapping has to be reviewed.** Under
[D-084](#d-084--descriptive-data-is-organization-defined-at-runtime) every legacy column that is not
identity machinery becomes an attribute code, so the first import is the single largest event in the
life of that vocabulary — hundreds of codes from one file. Two things follow:

- **The map is reviewed before the batch applies, not after.** That is precisely why the mapping is
  recorded on the batch as one object
  ([06-audit-and-import.md §3](../data-model/06a-import.md#3-import-pipeline)) rather than per
  staged row: it is one artefact a person reads once, top to bottom. The codes it names arrive **`live`**,
  because a curator has just read them.
- **`proposed` keeps its meaning.** It stays the status for what a *human at a desk* improvises later —
  a fact with no code yet — and not for "whatever the import did not understand". If several hundred
  codes arrive `proposed` on day one, the curation queue
  ([09-attributes.md §8](../data-model/09-attributes.md#8-integrity-checks) check 1) opens full, its age
  signal is meaningless, and the first lesson the organization learns about the attribute layer is that
  its warning queue is noise. **This is a partial answer to AT-2, which stays open** for the runtime
  case: who holds `attribute.define` day to day, and how long a proposal may sit.

**What is confirmed rather than decided.** The legacy number goes to `person_identifier` with
`scheme = 'legacy'`, imported verbatim and never reissued; where it is present the match is exact and
the heuristics are for backfilling it, not for deciding identity (D-056). At thousands of rows the
review is a work queue with a trustworthy set at the top of it, which
[B-1](../open-questions.md#b-1) already
called a strengthening of D-004 rather than a relaxation.

**What this makes sharper rather than smaller.** With attendance and no money,
[06-audit §3.1](../data-model/06a-import.md#31-what-a-source-row-actually-evidences) is the
load-bearing section of the whole import — a roster row evidences *presence in a unit*, and everything
beyond that is inference. Which leaves **A-4**, the organizational year boundary, as the sharpest
remaining import question, because it is what an end date gets inferred from.

**Still not known, and it is operational.** The exact record count and the year range. Both are inputs a
batch carries; neither changes a table. B-1 is closed on the design and these two numbers are recorded
as the import's own inputs.

**Closes:** [B-1](../open-questions.md#b-1).

**See:** [domain/03-identity-and-legacy.md §7](../domain/03-identity-and-legacy.md#7-legacy-import-pipeline),
[data-model/06-audit-and-import.md §3](../data-model/06a-import.md#3-import-pipeline),
[data-model/09-attributes.md §7](../data-model/09-attributes.md#7-the-legacy-import-which-is-where-the-vocabulary-comes-from).

**Amended one round later, in part.** The corpus this entry describes was the wrong shape in its
second half: the rows are people with their membership periods, and events with attendance, and they
name no units at all. Read [D-092](round-09.md#d-092--the-corpus-is-people-and-events-and-it-names-no-units) and
[D-093](round-09.md#d-093--the-one-off-import-may-create-memberships-both-ends-dated), which retire this entry's
absolute ban on an imported `membership`. **What survives intact is the other half** — the legacy
member number, the absence of money, and the reviewed-before-apply field map that decides where the
whole attribute vocabulary comes from. Three entries describe one import and none is complete alone.

---
