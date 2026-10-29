# Decision Log — Refinement round 9 — organization (D-091 … D-096)

> Audiences that name other audiences, what the corpus names and what it does not, and what joining a body means.

[Refinement rounds 7 and 8 (D-082 … D-090) ←](round-07-08.md) | [All decisions](index.md) | [Refinement round 10 — the deletions, part 1 (D-097 … D-100) →](round-10a.md)

**Two things this round produced that are worth more than the questions it asked.** A rule that lives only as prose in one section is still a rule: "audiences do not nest" sat in the authorization data-model for three rounds and quietly cost two grants for one intention, until an answer asked for the forbidden thing. And **a decision recorded from a description of the data is only as durable as the description** — [D-090](round-07-08.md#d-090--the-legacy-corpus-is-thousands-of-roster-rows-with-numbers-and-no-money)'s absolute import rule lasted one round because nobody had read the file, which is why [D-092](#d-092--the-corpus-is-people-and-events-and-it-names-no-units) exists and why the corpus questions are now asked in the present tense about a real export.

---

## D-091 — A permission group is a rule and a list at once, and a rule may name another group

**Status:** decided (from your answer)
**Date:** refinement round 9

**Amended three times — by [D-101](round-10b.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree),
[D-103](round-10b.md#d-103--an-audience-may-name-another-audience) and
[D-105](round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other) — and the arm this entry
is named for is the one that changed, twice.** A rule may still name another set — as `GROUP(x)` or
`AUDIENCE(x)` inside an expression — but `audience_include` is deleted, 'other groups' became an operand kind
rather than a table, and the list arm this entry is *named for* outlived its table by one round: D-101 turned
it into the `LIST` leaf, and D-105 deleted that, so **"a rule and a list at once" is now only half true and the
half that survives is the rule.** A hand-written set is `PERSON(a) + PERSON(b)` in the expression. The
write-time acyclicity requirement survives, widened into reachability across audiences — and since D-105 it is
the only structural guard left, because the depth bound that used to stand beside it is gone.

**Follows:** [D-042](round-02-03.md#d-042--grants-may-target-audiences-not-only-individuals),
[D-033](round-02-03.md#d-033--multiple-people-may-occupy-the-same-position),
[D-087](round-07-08.md#d-087--merge-chains-stay-because-reversing-a-merge-is-a-supported-operation)

**Your answer.** Asked whether appointing someone to a position should also create a role assignment,
the answer described something one level further out: *within the permission groups there should be
"filling rules" for each, which specify who will be placed in that group on top of manually added
people — "everyone with membership", "a leader role", "anyone", "members of permission group ABC"*.
The examples given were from another system, where a group's population is derived from enrolment in
a course: `studpredmet 1433 kod PV160` puts the students and teachers of one course in a group.

**What was already here, because the answer describes most of an existing mechanism.** The
organization already has rule-filled groups: an `audience` is a named set that a permission is granted
to, whose membership a rule decides at check time (D-042). Three of the four rules named exist
verbatim — `everyone` is "anyone", `all_members` is "everyone with membership", and `unit_leaders` is
"a leader role", derived live from position assignments marked `is_leadership`. Named groups are the
manually-added arm. **What the answer added, and what this decision is about, are the two things the
model refused.**

**Decision, in three parts.**

1. **`audience.kind` is gone.** A group has an **optional rule arm** (`resolver_key` plus
   `scope_parameter`), an **optional manual arm** (`audience_member` rows) and an **optional inclusion
   arm** (`audience_include` rows naming other groups). Its membership on a date is the **union of all
   three**. The old rule — a group is a rule *xor* a list, and a member row on a rule "would look
   authoritative" — is withdrawn. It forced two grants for the common case of *"the kitchen crew, plus
   whoever leads this pack"*, and two rows in two places is how one of them gets forgotten.
2. **A group may include another group.** This was refused outright — *"They do not nest. An audience
   cannot contain another audience — that is how you get evaluation cycles and answers nobody can
   predict."* The refusal is withdrawn and its reason answered where D-087 answered the same reason for
   merge chains: **the cycle is refused when the edge is saved, not in the read path.** Inclusion edges
   are stored rows, so the cycle is decidable at write time by walking them, and nothing about
   evaluation gets a hop limit or a guess. Inclusion chains get a length bound, stored as a parameter in
   the way the renewal window is ([D-048](round-04.md#d-048--the-renewal-window-is-60-days-and-is-a-configuration-parameter)
   is the precedent for that shape of parameter), and an unresolvable chain **denies**: a group that
   cannot be evaluated reaches nobody, which is the direction this model fails in everywhere else.
3. **An appointment still creates no role assignment.** `position.is_leadership` keeps the one job it
   has always had — driving the derived `unit_leaders` rule, and marking which roles exist to make a
   position work. Copying a role assignment at appointment time would duplicate a derivation, and a
   copy is the thing that outlives its reason: it has to be found and revoked when the position ends,
   whereas the rule stops covering the person on the day the assignment closes. **That is the answer to
   the question that was asked, and it is the cheapest part of it** — no schema, no workflow.

**What was *not* taken from the answer, and it needs saying rather than burying.** In the system you
described, permissions sit on the group. Here, permissions sit on a group at one scope through
`access_grant` — which is how "all leaders of pack X may take part in its roster" is one row today — but
a **role** is still held by one named person, because `role_assignment` is the record of who holds which
office and it is read to answer "who was treasurer in 2023". A derived holder list cannot answer that,
and an office record that cannot answer it is not an office record. So a rule-filled role is **not**
decided here: it is registered as
[F-12](../open-questions.md#f-12) — the change is one
grantee pair on `role_assignment`, exactly the shape D-042 already put on `access_grant`, and it wants
an answer about the historical question before it wants an implementation.

**The cost, stated where it will be felt.** Membership of a rule group has never been stored — D-042
accepted that, and the docs even recommended it, because a rule does not rot the way a list does. This
decision **widens how much of the permission answer is recomputed rather than recorded**: a grant that
once named three people now names a chain of sets whose membership depends on positions, participations
and memberships as they are today. Two consequences follow, and the second is the one to keep in view:

- **A grant's reach stops being visible in the row.** The editor must show the resolved set — who this
  grant actually reaches, expanded — and not the group's name. Composition makes a three-deep inclusion
  a silent widening, and `everyone` is a legal member of the graph: nothing in part 2 stops a group from
  including one that includes the whole world, which is already grantable directly and is now grantable
  by three edits and a save.
- **"Who could read this in 2023?" now has one fewer answer.** The audit trail used to hold the change
  that made it true, and [D-088](round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)
  empties those payloads after 24 months; the derived membership was never stored at all. So after two
  years the question is answered by re-running rules against state that has itself moved on. **The route
  back is [F-7](../open-questions.md#f-7)** — a
  materialized effective-permission snapshot, kept as history rather than as a cache — which until now
  looked like a performance question and is now also the only thing that could make this answerable.

**Naming, since your word and this file's word differ.** What you called a *permission group* is the
`audience` table, and the table keeps the name — not to avoid work, but because `group` is already taken
inside it for one of the two kinds this decision deletes, and a document that renames a table and keeps
the word for a fragment of it is worse than one that renames neither. The glossary carries both words.
What does change is that **`group` no longer names a kind of anything**: there is one thing, and it has
arms.

**Closes:** [C-4](../open-questions.md#c-4).

**See:** [data-model/05a-audience-and-grammar.md §8](../data-model/05a-audience-and-grammar.md#8-audience--grants-that-target-a-set-of-people),
[domain/06-authorization-model.md](../domain/06-authorization-model.md#2-scopes--the-unit-and-the-item),
[domain/04-organization-structure.md §4](../domain/04-organization-structure.md#6-appointments).

---

## D-092 — The corpus is people and events, and it names no units

**Status:** decided (from your answer)
**Date:** refinement round 9
**Follows:** [D-090](round-07-08.md#d-090--the-legacy-corpus-is-thousands-of-roster-rows-with-numbers-and-no-money),
[D-041](round-02-03.md#d-041--belonging-to-a-sub-unit-is-a-participation-record-not-a-membership),
[D-058](round-05.md#d-058--an-event-is-a-dated-occasion-owned-by-exactly-one-unit)

**Your answer.** Asked what creates the units the roster rows point at: *the rows are mainly "person
with names, birthdate and when they were members of the root unit", "events with attendance". Not much
more — do not solve assignment to org units.*

**So the corpus has two halves and neither is a roster.** D-090 recorded it as *roster rows*: people
attending units. That word was wrong in its second half, and the whole import design hung off it,
because a roster is evidence of *presence in a unit* and that is what
[06-audit-and-import.md §3.1](../data-model/06-audit-and-import.md#31-what-a-source-row-actually-evidences)
was written to police. What is actually arriving is a **membership export** and an **attendance
export**. Each is evidence of a different thing, and neither is evidence of a sub-unit:

| Half | What a row says | What the import writes |
|---|---|---|
| **People** | name, birth date, **member of the organization for a period** | a `person`, and a bounded `membership` ([D-093](#d-093--the-one-off-import-may-create-memberships-both-ends-dated)), which brings its root participation row with it |
| **Events** | an event, and who attended it | an `event` owned by the root ([D-094](#d-094--the-root-unit-owns-every-imported-event)) and an `event_registration` per attendee |

**Unit assignment is out of scope, by instruction, and that is a decision with a consequence rather
than an omission.** `parsed_unit_code` and `parsed_unit_name` stay in the parser — an export that
surprises whoever runs it with a unit column is exactly what those fields and the `unit_not_found`
warning are for, and they cost nothing to keep. But nothing resolves them, no `org_unit` is created by
any batch, and no sub-unit `unit_participation` row is ever imported. **The consequence, plainly: the
system's historical record has no sub-units in it.** "Who was in pack X in 2011?" has no answer on day
one and will have one only from live data forward, and the first answer anyone reads is a roster
somebody typed in. That is not a gap in the model — the model has always been able to hold it — it is
what the source can say, and it is written here so that the first person to ask the question finds the
sentence rather than the absence.

**What this retires, and what it leaves alone.** Retired: the roster frame, and with it D-090's rule
that an imported row is a participation and never a membership
([D-093](#d-093--the-one-off-import-may-create-memberships-both-ends-dated) replaces it), and the
import exclusion that rule forced into integrity check 1 in
[03-membership.md §7](../data-model/03-membership.md#7-integrity-checks) — with no imported
participations, that exclusion goes and the check starts finding what it was written to find. Left
alone, because none of it depended on units: the legacy member number going to `person_identifier` and
the exact-match identity story (D-056), the absence of money, the attribute vocabulary arriving wholesale
from the free-text columns through a map read before the batch applies, the end-date inference, and the
revert mechanics.

**The one thing the answer makes harder rather than clearer.** Two halves means two shapes of batch, and
the pipeline has one `import_batch` with one `field_mapping` on it. An events export has nothing to map
to an attribute code and a people export has nothing to map to a registration, so **either the batch
types itself** (a people batch, an events batch, each with the mapping and the checks that fit) **or one
batch carries two mappers that can never both apply.** The first is the smaller change and it is what
these documents now assume; it is recorded as a design consequence here rather than as a new question,
because the answer that decided the shape also decided this about it.

**Closes:** [C-5](../open-questions.md#c-5).

**See:** [domain/03-identity-and-legacy.md §7](../domain/03-identity-and-legacy.md#7-legacy-import-pipeline),
[data-model/06-audit-and-import.md §3](../data-model/06-audit-and-import.md#3-import-pipeline).

---

## D-093 — The one-off import may create memberships, both ends dated

**Status:** decided (from your answer)
**Date:** refinement round 9
**Follows:** [D-090](round-07-08.md#d-090--the-legacy-corpus-is-thousands-of-roster-rows-with-numbers-and-no-money),
[D-092](#d-092--the-corpus-is-people-and-events-and-it-names-no-units),
[D-050](round-04.md#d-050--a-renewal-inside-the-window-extends-the-existing-root-participation-row),
[D-039](round-02-03.md#d-039--member-permissions-require-a-current-paid-membership)

**Your answer.** *The import will be a one-off — allow creation of memberships.*

**Decision.** A batch may create `membership` rows, with `valid_from` **and** `valid_to` set, from a
source that states a period of membership. One row per period the source states — not one row per
calendar year — with `data_confidence = 'low'` and the batch id on it, and the
`renewed_from_membership_id` chain left to whoever reconstructs it, because an export of consecutive
years is a period, not a renewal history. **D-090's ban is narrowed to the thing it was actually
protecting, in one sentence that survives unchanged: never an open-ended membership, and never one
inferred from an attendance row.** The reason is D-039 and it has not moved — a membership with no
`valid_to` satisfies `is_current_member()`, so an inferred 1998 membership hands whoever signs up under
that name authority in the present. That is why the ban was absolute and it is why *this* half of it can
go: a closed period cannot gate anything.

**"One-off" is doing real work in the answer, and it is worth naming what it buys.** The argument for
the original ban was about a standing hazard — an import that infers, run by whoever is holding the
file, repeatedly, for years. What is being decided here is one reviewed batch whose mapping is read
before it applies, on a corpus that will never arrive twice. A rule written for a recurring process is
too strict for a one-time one, and the safety that mattered is not the ban but the review.

**Four consequences, in the order they arrive.**

- **The root participation obligation now points at the import again.**
  [03-membership.md §5.1](../data-model/03-membership.md#5-unit_participation--deleted-by-d-097) had
  just been corrected to say that an ordinary import "touches neither arm of this pair". With
  memberships arriving by the thousand it does: every imported membership owes its root-unit
  participation row in the same transaction, which is what keeps *who is in unit X* one query
  (D-041). Consecutive imported years for one person therefore stretch one root row rather than opening
  a second, and a gap in the source is a lapse that produces two — the same rule as a renewal, and the
  same accepted cost: the lapse stops being visible in the participation table.
- **No obligation, no payment, no balance.** An imported membership creates **no `fee_obligation`**.
  The corpus has no money in it (D-090), so an obligation per historical year would arrive as `unpaid`
  and turn a decade of members into a wall of debt on a ledger that has never heard of them, with a
  `due_date` in 1999 for the lapse sweep to choke on. The sweep is already safe — it acts on active
  memberships with a positive-balance obligation, and an imported row is neither — but the *absence*
  becomes a rule, because the alternative failure is silent and enormous.
- **`outstanding_balance` is NULL on these rows, and that is now load-bearing rather than incidental**
  ([07-finance.md](../data-model/07-finance.md#2-minimal-provisional-shape)). A zero would be a claim —
  *settled* — that the export does not support.
- **These rows are the oldest layer of the skeleton D-088 keeps forever.** That decision held named
  membership periods indefinitely on legitimate interest, on an unverified legal basis
  ([assumption 49](../open-questions.md#i-assumption-index)). From this round the indefinite-retention
  half of D-088 covers thousands of named people with birth dates who were never asked and never used
  the system. It is the same judgement, applied to a much larger population, and the review commissioning
  it is unchanged in kind and much changed in scale.

**What this makes true about reports.** Every cross-decade member count is now a mix of an export and a
register, distinguished only by `data_confidence` and `import_batch_id`. A membership-rate chart that
spans the import boundary is comparing a source that states membership with a system that records it,
and nothing in the query knows the difference.

**Closes:** [C-5](../open-questions.md#c-5)
(together with [D-092](#d-092--the-corpus-is-people-and-events-and-it-names-no-units)).

**See:** [data-model/06-audit-and-import.md §3.1](../data-model/06-audit-and-import.md#31-what-a-source-row-actually-evidences),
[data-model/03-membership.md §5.1](../data-model/03-membership.md#5-unit_participation--deleted-by-d-097),
[domain/03-identity-and-legacy.md §7](../domain/03-identity-and-legacy.md#7-legacy-import-pipeline).

---

## D-094 — The root unit owns every imported event

**Status:** decided (from your answer)
**Date:** refinement round 9

**Deleted rather than reversed by [D-102](round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it): there is no owner column for an imported event to
have.** The import still owes one `event` row per event in the corpus, and now owes the per-event grant
instantiation D-102 added with it.

**Follows:** [D-058](round-05.md#d-058--an-event-is-a-dated-occasion-owned-by-exactly-one-unit),
[D-092](#d-092--the-corpus-is-people-and-events-and-it-names-no-units),
[D-067](round-05.md#d-067--presence-is-a-three-valued-fact-on-the-registration)

**Your answer.** Asked what owns an imported event, given that every event belongs to exactly one unit
(D-058) and that unit assignment is out of scope: **the root unit owns them all.**

**Decision.** `event.org_unit_id` on an imported event is the single root unit, as a rule rather than a
judgement. D-058's "exactly one owning unit" is satisfied without inventing a unit, without a per-event
decision, and without the import touching the unit vocabulary at all — which is what makes this
compatible with the instruction that decided D-092. The root is the only unit the corpus speaks of, so
it is also the honest answer, not merely the convenient one.

**Attendance becomes registrations, and the three-valued rule decides what is *not* written.** An
attendance export lists the people who came. Each one becomes an `event_registration` with `attending`
and `was_present = true` (D-067). **Nobody else gets a row**: a person who might have come and did not is
not in the export, and inventing `not_attending` rows from silence would put words in a source that said
nothing ([D-059](round-05.md#d-059--unanswered-is-the-absence-of-a-row-a-registration-stores-two-values)). So
imported events have a population exactly as large as the evidence for them, and the historical
attendance figures these documents will be asked for are *arrived*, not *registered*.

**Three costs, one of which is the reason this decision was worth recording separately.**

- **The root's event list becomes mostly history.** "What's on" stops being a unit filter and has to be a
  date filter — and the unit-scoped report that asks "our events this term" shows an imported camp
  because the root is its owner, which is the same class of misreading D-049 recorded for
  `unit_participation.view` at organization scope.
- **Imported events have no organizers**, so nobody holds them at unit scope: `event_organizer` is empty
  on them by construction, and editing one takes organization-scope authority
  ([D-062](round-05.md#d-062--organizers-are-appointed-on-the-event-not-granted)). An imported event is therefore
  read-only for the people who would ordinarily run an event, which is correct and will still surprise
  somebody.
- **Correcting an owner is one column, and it moves the audience.** Unlike participation history, which
  is never rewritten, `event.org_unit_id` is editable — and because an event is an artifact of its unit
  ([D-063](round-05.md#d-063--an-event-is-an-artifact-of-its-unit-not-a-child-of-it)), moving an event from the root
  to a pack silently changes who can read it. So corrections are allowed and expected, and each is an
  audited write with a reason; and the audit record of *who moved it* is readable for 24 months
  ([D-088](round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)) while the event itself
  is kept indefinitely.

**Closes:** [C-5](../open-questions.md#c-5)
(together with [D-092](#d-092--the-corpus-is-people-and-events-and-it-names-no-units)).

**See:** [data-model/08-events.md §2–§4](../data-model/08-events.md#2-event),
[data-model/06-audit-and-import.md §3](../data-model/06-audit-and-import.md#3-import-pipeline).

---

## D-095 — Units carry no restrictions; joining one is somebody else's act

**Status:** decided (from your answer)
**Date:** refinement round 9
**Follows:** [D-038](round-02-03.md#d-038--membership-is-ageless),
[D-043](round-02-03.md#d-043--no-background-checks-are-recorded-in-this-system),
[D-081](round-06.md#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now)

**Your answer.** Asked whether a unit that declares it does not supervise minors should refuse a minor's
*position* as it refuses their participation: *a unit does not have any restrictions — however, persons
can't assign themselves. They will be assigned to the unit by the counselors.* And on the shape of
entry: *into the root unit, there is a fee for entry; into the sub-units, there is no fee, it is entirely
managed by the organization, including adding more members.*

**Decision.** Two entry paths, each with exactly one gate, and no third control:

| | **The root unit** | **A sub-unit** |
|---|---|---|
| **How you get in** | You pay. The membership flow is the only self-service entry in the system, and it opens the membership and its root participation row (D-041, D-050) | Somebody else writes the row |
| **What stops you** | The fee | `unit_participation.manage` at that unit — held by the people who run it, **with no self-scoped variant, and none will be added** |
| **Money** | The yearly fee | Nothing. There is no fee for taking part in a pack, and no model wants one |

The same holds for `position_assignment`: nobody appoints themselves. There is no code in the catalog
that could express either, and D-095's instruction is not to add one.

**`org_unit_type.allows_minors` is removed.** It was introduced as a **safeguarding** flag — the thing
that let the system refuse to place a minor in a unit that does not supervise them without hardcoding
which type codes those are. After this answer it enforces nothing about positions, and a flag that is
documented as a safeguard and enforced on one of two write paths is precisely the thing these documents
elsewhere refuse to keep: *a list of eighteen ticks nobody read is not a safeguard, it is a receipt*
([domain/08 §4](../domain/08-person-data.md#4-what-was-refused-and-what-it-cost)). What goes with the
column: its check in [03-membership.md §7](../data-model/03-membership.md#7-integrity-checks) (check 2,
*participants in units that do not allow minors*), the root type's `allows_minors = false` in the seed,
and the sentence in [02-organization.md §1](../data-model/02-organization.md#5-what-this-page-held-before-round-10) that
explains why there is no `allows_adults` sibling.

**D-081 requires naming who enforces the rule now, and the honest form of that answer is a shift in
kind.** The rule the flag existed to express — *do not place a child where nobody is responsible for
them* — is now enforced by **who is allowed to write the row**: a person able to add a child to a unit is
a person the unit's leadership trusts with its roster, the write is audited, and the assignment names who
made it. That is a stronger control than a boolean on a type, because a boolean only ever refused a
placement nobody had thought about and the permission refuses every placement by the wrong person
regardless of the child's age.

**What is genuinely lost, and it is the safeguarding story in one paragraph.** **The system no longer
knows which units are for children.** `allows_minors` was the only machine-readable answer to that
question; nothing replaces it, because "entirely managed by the organization" is a statement about people
rather than data. Combined with D-043 — no background checks recorded anywhere — the organization
module's safeguarding story after D-095 is: a permission held by named adults, an audit trail whose
values expire after two years, and a report list of who holds the write. If that turns out to be too
little — after a real incident, or an insurer's question — the route back is **a rule about who may be
placed where, argued once as a decision, with its enforcement layer named** in D-081's terms, and not a
resurrected column whose name implies it enforces something.

**Not changed by this, because it was never about units:** membership stays ageless (D-038), `position.min_age`
stays a real eligibility constraint about the *position* (a scoutmaster must be an adult), and the
guardianship channel is untouched.

**Closes:** [C-6](../open-questions.md#c-6).

**See:** [domain/04-organization-structure.md §1, §4](../domain/04-organization-structure.md#1-the-organization-is-one-unit-and-the-unit-is-a-scope),
[data-model/02-organization.md §1](../data-model/02-organization.md#5-what-this-page-held-before-round-10),
[domain/05-membership-lifecycle.md](../domain/05-membership-lifecycle.md#1-the-flow-you-described).

---

## D-096 — A reused unit number is a new unit unless someone records the continuity

**Status:** decided (from your answer, and one question back)
**Date:** refinement round 9
**Follows:** [D-036](round-02-03.md#d-036--units-cannot-be-reparented-a-unit-that-moves-is-a-new-unit),
[D-054](round-04.md#d-054--the-sub-unit-vocabulary-is-not-seeded-the-organization-defines-its-own-types),
[D-092](#d-092--the-corpus-is-people-and-events-and-it-names-no-units)

**Question, put back to you, and the answer's shape.** Asked whether a unit number appearing twice —
one unit closed in the 1990s, another carrying the number now — is the same unit or a new one, the
answer was *"what is a unit number?"*. That question is the useful part of this entry, so it is answered
before the decision is. A `code` is **a short human label typed by somebody**: `T12`, `4. oddíl`. It is
not the unit's identity, which is the row; it is not its name, which is a temporal row of its own
(`org_unit_name`); and it is not unique, deliberately — uniqueness is per parent and among live rows
only, which is exactly why a closed unit's number is free again
([02-organization.md §3](../data-model/02-organization.md#5-what-this-page-held-before-round-10)). Once it is described as a label,
the question answers itself in the direction the docs already argued.

**Decision.** **A reused number is a new unit.** One `org_unit` row per unit that existed, each with its
own period; the continuity between two of them is not a property of the label but an assertion somebody
makes and records as an `org_unit_relationship` with `successor_of`
([§5](../data-model/02-organization.md#5-what-this-page-held-before-round-10)). The opposite
default — reuse the row and let a thirty-year gap show inside one unit's life — is what a system drifts
into if nobody says, because it is what "match on code" does. And the two cases the docs separate are
unchanged and are *not* this case: **a renumber is one unit with two name rows** (same participants,
continuity asserted by the rename itself), while **a unit that moves parent is a new unit** (D-036).

**The cost is a decision the organization has to make in words, occasionally, and it is cheap.** When a
number really does come back — a troop refounded after a decade dormant — someone writes down that this
unit is the successor of that one, and "who was in Pack 12 in 1984?" follows the relationship instead of
guessing from an overlapping name. Refusing to default either way was considered, and it is what
`domain/04 §6` used to say (*"record which was chosen and why on the unit"*); what D-096 adds is the
direction the record goes in when nobody records anything, because a default that is unstated is a
default that gets implemented by whoever writes the matching screen.

**Closes:** [C-3](../open-questions.md#c-3).

**See:** [domain/04-organization-structure.md §3, §6](../domain/04-organization-structure.md#4-a-name-carries-no-identity),
[data-model/02-organization.md §4–§5](../data-model/02-organization.md#5-what-this-page-held-before-round-10).

**Superseded by [D-097](round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row).** There are no
sub-units left to number, close, or declare a successor of, and no `org_unit` row for a `code` to sit on.
The reasoning survives as a method — *a label carries no identity, so continuity is asserted and never
matched* — and it transfers intact to `person_group`, where a group name that comes back after a decade
is a new group unless somebody says otherwise.

---
