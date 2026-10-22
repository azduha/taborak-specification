# Open Questions

Everything still unresolved, each with its **schema impact** — what changes once you answer.
Ordered roughly by how much they block.

Marked: 🔴 **blocking** something else · 🟡 **important** · 🟢 can be deferred.

**Resolved items are not deleted.** They are moved to the bottom of this file with a link to
the decision that settled them, so the reasoning survives — see
[§ R. Resolved](#r-resolved--moved-to-the-decision-log).

---

## A. Blocking the core design

### A-1 ✅ **Closed** — the unit type vocabulary is not seeded at all

**Answered: the sub-unit vocabulary is not a question the specification can answer, so it is
not seeded** ([D-054](decisions/decision-log.md#d-054--the-sub-unit-vocabulary-is-not-seeded-the-organization-defines-its-own-types)).

`org_unit_type` is **runtime data**, like `role` ([D-052](decisions/decision-log.md#d-052--roles-are-runtime-data-the-seed-set-is-not-a-specification)).
The seed contains the root type and nothing else; the organization creates the types it uses.
The previous placeholder — `pack`/`group`/`team`, and before it a
`national`/`region`/`district` ladder — is gone.

**Why this is a better answer than a correct list would have been.** The organization's own
vocabulary is not knowable at specification time, and a wrong word in seed data is harder to
dislodge than an absent one, because it reads as a specification to whoever implements the
system. The *shape* was always the settled part: one root, arbitrary nesting beneath it
([D-035](decisions/decision-log.md#d-035--one-root-unit-all-sub-units-nest-arbitrarily-beneath-it)).

**What remains true and worth knowing.** Nesting is **permissive by default** —
`org_unit_type_rule` is seeded with nothing, so any type may sit under any other until the
organization states a rule, and a new type is usable the moment it is created. Every rule
added later is a constraint deliberately chosen. The words `pack`, `troop` and `section` still
appear across these docs **as illustration only** — read them as "some sub-unit type the
organization has defined".

**See:** [data-model/02 §10](data-model/02-organization.md#10-seed-data),
[domain/04 §1–2](domain/04-organization-structure.md#1-one-root-arbitrary-sub-units)

---

### A-4 (remainder) 🟢 The organizational calendar

**Answered.** The fee expires on **1 January**
([D-047](decisions/decision-log.md#d-047--the-fee-expires-on-1-january)) and the renewal
window is **60 days** ([D-048](decisions/decision-log.md#d-048--the-renewal-window-is-60-days-and-is-a-configuration-parameter)).

**What is left is not a question but a discipline.** Both values live in
`membership_type` as columns — `expiry_month`, `expiry_day`, `renewal_grace_days` — so either
can be moved by an `UPDATE`. The one way to lose that property is a scheduled job or a front
end that contains the literal `60` or `1`. Worth one line in code review: *do these values
come from the row?*

**See:** [data-model/03 §1](data-model/03-membership.md#1-membership_type--one-row-kept-as-a-table),
[domain/05 §6](domain/05-membership-lifecycle.md#6-renewal-and-the-yearly-fee)

---

## B. Identity and history

### B-1 (remainder) 🟢 The legacy corpus is large and number-bearing

**Answered: large, and the old records carry a legacy member number**
([D-056](decisions/decision-log.md#d-056--the-legacy-import-expects-a-large-corpus-with-legacy-member-numbers)).

That changes what the import has to be. The number goes into
[person_identifier](data-model/01-identity.md#7-person_identifier) with `scheme = 'legacy'`,
and where it is present the match is **exact rather than probabilistic** — same number, same
person. The heuristics in [domain/03 §4](domain/03-identity-and-legacy.md#4-match-signals)
are then for **backfilling** the number on rows that lack it, not for deciding identity from
scratch.

**The consequence for [D-004](decisions/decision-log.md#d-004--no-automatic-merging-ever).**
The "no automatic merging, ever" rule was costed on a small corpus where review was the
bottleneck. At thousands of rows that changes shape: the **number-bearing rows are the
trustworthy set** and the rest is a work queue. The rule is unchanged — the human still
decides every match — but the number does the work the human would have done, so the rule
becomes far cheaper to obey. This is a strengthening, not a relaxation.

**What must hold.** The legacy number is imported **verbatim and never reissued**. The
`(scheme, value)` index is what enforces it. A second numbering era can coexist, because
`person_identifier` carries a scheme and a period.

**What gets harder, not easier: membership vs. participation.** Volume and numbers fix
*identity*; they say nothing about *what a historical row means*. At this scale a 1998 roster
almost certainly records which unit someone attended, not whether their fee was paid — so the
import must decide per row which of the two it becomes
([D-041](decisions/decision-log.md#d-041--belonging-to-a-sub-unit-is-a-participation-record-not-a-membership)).
The safe default matters more at thousands of rows than at hundreds, because the failure
compounds: **participation unless there is payment evidence**, since an inferred open-ended
`membership` would make every 2003 roster member a *current* member today through the gate
([D-039](decisions/decision-log.md#d-039--member-permissions-require-a-current-paid-membership)).

**Still needed (operational, not design).** The record count, the format, and the year range.
Those are inputs the import batch carries; they do not change the schema.

---

### B-2 🟡 Merge chains: allowed or flattened?

**Question.** If A is merged into B, and later B into C, does A point at B (a chain) or is
A repointed at C (flattened)?

**Current design.** Chains. `resolve_person()` follows them recursively.

**Impact.** Flattening is faster to query but rewrites pointers and makes unmerge nearly
impossible. Chains need `resolve_person()` called everywhere an external id enters the
system — a rule application code can forget.

---

### B-3 🟡 Erasure: the policy, not the mechanism

**Question.** What must be redacted, what must be retained, for how long? Does the
organization have a legal obligation to keep membership records after an erasure request?

**Resolved already.** The *shape* is settled: **redact the person, keep the financial and
membership skeleton** — the `person` row is anonymised in place and the `membership`,
`fee_obligation` and `payment` rows survive intact, because the organization's own accounting
and "was this person a member on that date" questions outlive the person's participation.

**Still open.** The retention periods and the legal basis. `redaction_log.retained_reason` is
a placeholder for that judgement.

**Needed.** Legal review. Not a technical question.

**See:** [data-model/06 §4](data-model/06-audit-and-import.md#4-redaction-log)

---

### B-4 🟢 Can a person hold two live accounts?

**Recommendation.** No. Enforced by the partial unique index already in the schema.

**Impact.** If yes, the index is dropped and identity attribution weakens.

---

## C. Organization

### C-1 🟢 May the root *see* what happens in its sub-units?

**Answered: no — `scope_exposure` is the only crossing, and no reporting channel is built**
([D-049](decisions/decision-log.md#d-049--the-root-may-not-read-into-its-sub-units-scope_exposure-is-the-only-crossing)).

**What was not obvious until it was answered.** The question existed on the assumption that
the root needed a way *around* the no-inheritance rule in order to report nationally. It
does not, because the root **owns the membership registry and the fees** — so "how many
members in 2019?", "who is currently a member?" and "what fees are outstanding?" are all
answered from the root's own tables, with no exposure at all. Only the sub-units' own
material — their events, their rosters, their local leadership — requires one.

The consequence that will be misread as a bug: `registrar` holds `unit_participation.view` at
organization scope and **cannot** read a pack roster. Scope is an exact match; it reads the
root participation rows, which mirror membership
([D-041](decisions/decision-log.md#d-041--belonging-to-a-sub-unit-is-a-participation-record-not-a-membership)).
See [domain/06 §2.4](domain/06-authorization-model.md#24-the-organization-wide-role-problem-and-why-it-mostly-dissolved).

---

### C-3 🟢 Units with the same number across decades

**Question.** When a troop closes and a new troop with the same number starts ten years
later, is it the same unit or a new one?

**Impact.** An organizational judgement, not a technical one — but it must be *recorded*,
or it will be re-litigated every time someone asks about the 80s troop with that number.

**See:** [domain/04 §3](domain/04-organization-structure.md#3-unit-names-and-renumbering--the-history-problem)

---

### C-4 🟢 Does appointing someone to a position auto-create a role assignment?

**Current design.** Separate. `position.is_leadership` lets a workflow offer both.

**Impact.** Purely a workflow question; the schema is unaffected.

---

## D. Membership

### D-6 — closed, by making the question the organization's to answer

**Answered: the mechanism** ([D-051](decisions/decision-log.md#d-051--the-membership-gate-is-waived-by-a-permission-not-only-by-a-role-flag)).
The membership gate is waived by a person-level permission, `system.gate_exempt`, in addition
to the role-level flag. `system_admin` holds it — without it the 1 January sweep locks the
administrator out of the system on the day it needs repair.

**And "which other roles carry it" is no longer a question for this document.** Roles are
runtime data: the organization creates them, edits what they grant, assigns them, and deletes
the unused ones ([data-model/05 §3](data-model/05-authorization.md#3-role-and-role_permission)). Marking
a role as carrying `system.gate_exempt` is therefore a configuration act the organization
performs, not a fact the specification can state. The seed set in
[appendix/permission-catalog.md §11](appendix/permission-catalog.md#11-roles--proposed-seed-set)
shows the shape; it is a starting point to edit, and it explicitly declines to answer this.

**What is *not* delegatable, and is therefore all this document has to get right:** that
`system.gate_exempt` is a `system`-namespace permission, so it can only ever arrive through a
role and never through an item grant. That structural guarantee — an `access_grant` cannot
lift the membership gate — is the part a configuration screen must not be able to weaken.

**Tracked here only for visibility:** check 7b in
[data-model/05 §11](data-model/05-authorization.md#11-invariants-to-verify) reports who currently
holds the exemption, so the organization can see the list it has configured.

---

### D-7 🟢 What does the root-unit participation row do at renewal?

**Answered: it is extended, not closed and reopened**
([D-050](decisions/decision-log.md#d-050--a-renewal-inside-the-window-extends-the-existing-root-participation-row)).

The yearly sweep moves the root row's `valid_to` forward to the expiry date rather than
closing it, and a renewal inside the window stretches that one row over the new period. The
join between the two is **person and date** (`new_m.valid_from = up.valid_to`), not a
membership FK — the participation table has none, deliberately.

**The accepted cost, recorded rather than hidden.** This erases the visual evidence of the
lapse: a person who lapsed and renewed looks, in `unit_participation`, exactly like a person
who never lapsed. Accepted because `membership` remains the authority on payment and the
lapse is fully visible there, while the participation table answers a *roster* question — and
for "who was in this pack when" a child who was present across the period has one answer, not
two.

**See:** [data-model/03 §5.1](data-model/03-membership.md#51-a-participation-row-on-the-root-unit)

---

### D-8 🟢 Should `unit_participation` reference the membership?

**Question.** A nullable `membership_id` on `unit_participation` would give referential
integrity between "paid up" and "takes part", at the cost of being unenforceable for imported
historical rows, where no membership exists to point at.

**Impact.** Integrity vs. import coverage. The current design chose person-based linkage for
exactly that reason.

**See:** [data-model/03 §5](data-model/03-membership.md#5-unit_participation)

---

### D-9 ✅ **Closed** — `household` is removed entirely

**Answered: drop it** ([D-057](decisions/decision-log.md#d-057--household-is-removed)).
`household`, `household_member`, `fee_obligation.household_id`, its CHECK arm,
`ix_obligation_household` and integrity check 7 are all gone.

**Why removal rather than a derived view.** D-037 had already taken the load-bearing half —
the fee is flat and per person, so there is no family price. The two survivors were both
served by tables that must exist anyway: a billing address is a `person_contact` row where
`contact_type = 'postal' AND purpose = 'billing'`, and "who lived at this address in 2003?"
is a query over that table's own `valid_from`/`valid_to` history. The household table was
duplicating the address under a second key, and the copy had already gone stale — its
`postal_address` was documented as denormalised *from* the contact row, with nothing keeping
it true.

**The safeguarding property is untouched, and this is the point to check first.** Shared
address never granted access: **a child's records are reachable only through a guardianship
row**, whatever the household arrangement beside it. Removing a table that granted nothing
cannot grant anything.
[D-019](decisions/decision-log.md#d-019--household-membership-grants-no-access) stays in the
log, marked superseded, because "why does living together not imply access?" will be asked
again.

**The one thing genuinely lost.** A household was a group with a name and its own lifetime;
two people at one address are now related by a query, not a row. There is nowhere to hang
"the Novák family" as a first-class thing. Accepted because nothing used it. If family-level
communication or a family discount is ever wanted, the grouping comes back as a group with a
period — not a fake person.

**One knock-on worth knowing.** Finance question 2 (family/sibling discounts) is now *more*
open, not less: a per-family discount needs the grouping designed again before it can be
priced. A per-person discount is unaffected.

**See:** [data-model/04 §3](data-model/04-relationships.md#3-there-is-no-household-table)

---

## E. Guardianship

### E-2 ✅ **Closed** — the system takes no position on majority

**Answered: nothing at all.** No job, no review queue, no computed candidate date
([D-069](decisions/decision-log.md#d-069--guardianship-ends-when-a-person-ends-it-the-system-takes-no-position-on-majority),
reversing D-024). A guardianship is ended by a person ending it.

**What was wrong with the review queue** the docs had recommended: it was still automatic, and
it computed a date the system has no authority to assert. Deferring a decision is not the same
as declining to make one.

**This closes E-2 and immediately opens E-5 below.** With no automatic end and no queue, the
only exit is `guardianship.end` — and the adult who is the *subject* of the row holds no
permission over it.

### E-5 ✅ **Closed** — the parties administer their own row

**Answered: the guardian and the subject both act on the row themselves; there is no
management-team route** ([D-073](decisions/decision-log.md#d-073--guardianship-is-administered-by-its-own-parties-not-by-staff)).

**All three of the shapes above were wrong in the same direction.** Support request, ownership
channel, and request object each assumed the answer had to come from somewhere *other than the
people in the relationship*. It does not. A guardianship is a relationship between two people, both
of them are principals on the row, and either may end it. A guardian may add another guardian. No
staff approval, and no workflow invented for the purpose.

**It is not the ownership channel, which is why option (2) was the right answer for the wrong
reason.** Ownership is *your own record*; a guardianship row belongs to neither party alone. The
guardianship channel simply gained a direction — from "may guardian G act on D's records?" to also
"may a party act on this row?" — and the resolver still has four channels.

**The gap this closes was real, and it is now closed at the only place it could be.** D-069 removed
both the automatic end and the queue, leaving `guardianship.end` as the sole exit and the subject
unable to reach it. That was a door with no handle on the inside.

**Two things this opens, both below.**

### E-6 🟡 A guardian may appoint a guardian

**Raised by closing E-5.** D-073 lets a guardian add another guardian, so anyone with authority
over a child can hand that same authority to a second person **with no approval from the
organization**. The ordinary case is a mother adding the father. The design does not prevent the
non-ordinary case; it attributes it — who added whom, when, from which account, audited, with the
other party notified.

**The open question is whether attribution is enough**, and specifically whether adding a guardian
over a **minor** should also notify somebody at the organization beyond the audit log. A child
gaining a second legal stranger with `write` over their records is not the same kind of event as an
adult adding a co-parent.

**Recommendation.** Notify a safeguarding contact on `guardianship.assign` where the subject is a
minor, and nothing else. Notification is visibility, not approval, so the parties still do not need
the organization's permission — which is the whole point of D-073.

**Impact.** One notification rule. No schema change.

### E-7 🟡 One level cannot separate the medical record from the profile

**Raised by [D-074](decisions/decision-log.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular),
which deleted the eighteen `dependent.*` codes that existed for this case.**

**What cannot be said now.** *"This guardian may register the child for events but may not read the
medical record."* *"Read-only, except not the health data."* *"The grandmother may see the roster
and nothing else."* A guardian either sees everything about the child or nothing. The case the old
namespace was built around — a court order restricting one parent's medical access while their other
access continues — is inexpressible.

**Why it was accepted anyway.** Three values a volunteer treasurer can hold in their head, versus
eighteen whose differences nobody outside a court uses. And the alternative had a failure mode of
its own: a granular list that administrators ticked without reading is not more protective than a
coarse one, it only looks more precise.

**Recommendation.** Leave it closed until the case arrives in reality rather than in review. If it
does, the fix is **not** the return of the code list — it is one additional, explicitly-argued
exception on the medical sub-resource, taken as a decision with the current documents in front of
you.

**Impact.** Would re-open the shape of guardian authority. Currently: one value, three choices.

**Impact.** One branch in the ownership channel plus a check on the subject's age at
`p_at`. No schema change.

### E-3 🟢 Guardian acting for an adult child

**Question.** Can a parent register their adult child for an event, with the child's consent?

**Recommendation.** An explicit consent-based delegation, not a guardianship — the legal
basis differs and `access_grant.is_delegated` already supports it.

**Note.** Now that grants can target **audiences**
([D-042](decisions/decision-log.md#d-042--grants-may-target-audiences-not-only-individuals)),
the *event-wide* version of this question — "register everyone in this group" — is answered
without touching guardianship at all. What remains is the individual case.

---

### E-4 🟢 Guardianship lifetime vs. the membership gate

**Question.** Guardianship is exempt from the membership gate
([D-039](decisions/decision-log.md#d-039--member-permissions-require-a-current-paid-membership)),
so a lapsed parent keeps their guardian's right over their child's records. Confirm that is
intended rather than a side effect: it means an unpaid parent and a paid one are indistinguishable
inside the guardianship channel.

**Impact.** None structurally. It is worth stating explicitly because it is the one place the
gate is deliberately absent, and "why can this person still see that?" should have a written
answer.

---

## F. Authorization

### F-1 ✅ **Closed** — the catalog stays comprehensive and granular

**Answered: keep the catalog large and granular; more permissions arrive with the unbuilt
modules** ([D-055](decisions/decision-log.md#d-055--the-permission-catalog-is-deliberately-comprehensive-and-granular)).

It is a **menu**, not a checklist. Administrators assign people only the permissions they
actually need, and that is only possible if the capabilities exist as separate rows to assign.
The parts of the question that remain — the exact contents — are tracked in
[appendix/permission-catalog.md §12](appendix/permission-catalog.md#12-open-issues) and will
move as events, documents, communication and reporting land.

**Note the asymmetry with roles, because it looks like an inconsistency and is not.** Roles
are *runtime data* the organization invents ([D-052](decisions/decision-log.md#d-052--roles-are-runtime-data-the-seed-set-is-not-a-specification));
permissions are *capabilities the code implements*. You cannot assign a power that is not
expressible in the schema, so a comprehensive catalog costs only rows. A comprehensive *role*
list, by contrast, would be a specification pretending to be data.

**The sharp edge.** Granularity only buys least-privilege if the grants are narrow, and
[D-007](decisions/decision-log.md#d-007--every-resource-has-an-admin-level-that-subsumes-narrower-ones--reversed)
means any new permission in a namespace is **retroactively held by everyone with that
namespace's `.admin`**, with no assignment written. That is intended — and it is the reason
`role.edit` is marked 🔒🔒.

---

### F-3 ✅ **Closed** — nothing forces an assignment to end

**Answered: nothing — rely on the gate.** No `NOT NULL`, no application-layer requirement,
no per-role policy ([D-071](decisions/decision-log.md#d-071--nothing-forces-a-role-assignment-to-end-the-gate-and-the-report-are-the-control)).
The docs had recommended *yes, at the application layer*; that recommendation is withdrawn.

**Why the recommendation was wrong.** It claimed the membership gate makes an open-ended
assignment *more* dangerous. It makes it less: the gate already expires authority for exactly
the population an expiry date would target, and ties expiry to a fact the organization
maintains on purpose rather than to a date somebody typed.

**The residue, which is the whole control now.** `unit_leader` and `assistant_leader` have
`requires_membership = false` by decision, so a lapsed leader keeps leading; the same for any
role held by a non-member or carrying `system.gate_exempt`. For those, **a periodic human
review over open-ended assignments is not a nice-to-have, it is the entire defence** — D-053
put all the weight on `role_assignment.valid_to` and this decision declined to add a guard
rail there. Read the two decisions as one pair.

**See:** [data-model/05 §4](data-model/05-authorization.md#4-role_assignment--system-wide-authority)

### F-4 ✅ **Closed** — the question was answered by deleting the premise

**Answered obliquely and decisively.** Asked whether `person.admin` should subsume
`person.merge`/`person.redact`, the answer was *"Only the system should have admin permissions,
not the individual items"* — which removed the subsumer rather than choosing between the two
options offered
([D-068](decisions/decision-log.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle),
reversing D-007).

**The question moved rather than dissolved.** A role bundling all `person.*` codes still
reaches `person.merge` and `person.redact`. What changed is where that is decided: it used to
be a resolver rule, invisible in every role editor and true for every resource whether or not
anyone wanted it. Now it is **the contents of a role somebody wrote** — visible in
`role_permission`, dated, alarmable, and audited on change.

**What carries the guidance now** is the seed table, not the schema: no seeded role mixes
`person.merge`/`person.redact` with routine `person.edit`, and `identity_reviewer` is the one
that deliberately holds `person.merge`. A role that *does* bundle a resource including its
irreversible codes should be named for it.

**See:** [appendix/permission-catalog.md §11](appendix/permission-catalog.md#11-roles--proposed-seed-set)

### F-4a ✅ **Closed** — the catalog is the only list now

**Surfaced by D-068, not created by it.** When the two were reconciled during that work,
**22 documented permissions had no `INSERT` row** — including `unit_participation.view`, which
five of the catalog's *own* seed roles assign, and `person.redact`, one of the two codes
D-068 exists to protect. A further 12 were the `event.*` set, catalogued when events were
designed and never seeded. **All 34 are now fixed**; both sides list 91 codes and the diff is
empty.

**Why nobody noticed, which is the part worth keeping.** [D-068](decisions/decision-log.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle)
made a harmless inconsistency into a live one. Under the prefix-match wildcard, a role holding
`unit_participation.admin` reached `unit_participation.view` whether or not a `permission` row
existed — the catalog could advertise a capability the database could not name, and nothing
noticed, because the wildcard papered over the gap and only the permission editor showed it.
**The cushion was itself the bug's hiding place.**

**What is open is the discipline, not the data.** There is **no SQL check for this** — one side
is a Markdown file. Integrity check 18 reads the table, so it can find a permission no role
grants; it cannot find a permission the catalog promises and the seed never contained. The
reconciliation is scripted in [data-model/05 §12](data-model/05-authorization.md#12-what-the-organization-starts-with),
and it is a review rule, not a test.

**The actual question:** should the catalog be **generated from** `permission` rather than
maintained beside it? That is the only change that makes the two incapable of disagreeing.
Against it: the catalog's value is its prose — the sensitivity marks, the rationale notes, the
§5a and §8a argumentation — none of which belongs in a table. A middle path is to keep the
prose in Markdown and generate the code tables from the database, so only the commentary can
drift.

**Impact.** If left manual, this recurs on every module added, and D-055's decision to keep
growing the catalog guarantees modules get added.

**✅ Closed — answered by deleting one of the two lists.** Asked whether to generate the catalog
from the seed, the answer was **"delete the schema, I will use ORM anyway"**
([D-072](decisions/decision-log.md#d-072--the-documentation-carries-no-sql-the-schema-is-the-orms-job)),
which removed the seed blocks, the DDL and the 19 integrity checks from the documentation
altogether.

**The generation question dissolved rather than being settled, and the difference matters for what
is still true.** Nothing is generated, because there is no longer a table to generate *from*.
**The catalog is now the only list that exists** — which answers the drift problem completely and
removes, at the same time, the executable form of every rule the DDL had been carrying. That trade
is D-072's to make and its entry records what it costs: integrity check 18, the orphaned-permission
check that was the safety net for the deleted wildcard, is now a prose instruction rather than a
query. **A check nobody runs is a convention.**

**What remains genuinely open is the thing the check was guarding.** With no seed and no wildcard,
a capability in the catalog that no role bundles is unusable and silent. It is now caught by review
of the catalog, and there is no automated backstop at all.

---

### F-5 🟢 Which built-in audiences are needed?

**Question.** `everyone` and `all_members` are seeded, plus parameterised
`unit:<id>:participants` and `unit:<id>:leaders`
([D-042](decisions/decision-log.md#d-042--grants-may-target-audiences-not-only-individuals)).
Which others are real — "the guardians of this child", "the leaders of the parent unit",
"adults only", "everyone in this section *and everything under it*"?

**Impact.** Each is one `audience` row plus one branch in `person_in_audience()`. Cheap to
add, cheap to remove. But the parameterised ones raise a second question: are
`unit:42:participants` rows **seeded per instance** on demand, or created when first granted?
The first is a migration that must be re-run as units are created; the second needs a
create-on-demand path that bypasses the usual admin permission.

---

### F-6 🟢 The permission cache lifetime under the membership gate

**Question.** [D-039](decisions/decision-log.md#d-039--member-permissions-require-a-current-paid-membership)
means the resolver's answer changes when a membership lapses — including at the yearly sweep,
which touches everyone at once. What TTL is acceptable?

**Impact.** The shorter the TTL, the smaller the window in which a lapsed member still has
access, and the more load on the resolver. The sweep must invalidate by person, not by scope
([data-model/05 §10](data-model/05-authorization.md#10-the-resolver)), and that is
settled — this is only about the steady-state TTL.

---

### F-7 🟢 Cache vs materialized `effective_permission` table

**Recommendation.** Start with cache-only. Materializing is a denormalization requiring
transactional maintenance, and a silent refresh failure is an access bug nothing detects.

**Impact.** Performance only; revisit if measurement demands it. The membership gate makes
materializing harder, not easier — every membership transition would have to rewrite rows.

---

### F-8 🟢 Retention policy for `access_log`

Legal input required. Recommend monthly partitioning from the start, with archival to cold
storage and **never deletion**.

---

### F-9 🟢 Should `membership_type` stay a table with one row?

**Question.** [D-037](decisions/decision-log.md#d-037--exactly-one-membership-type-the-fee-is-flat-and-per-person)
kept `membership_type` as a table with a single seeded `member` row, on the principle that
vocabularies are rows and not enums — at the cost of an FK that always holds one value.

**Impact.** A deliberate trade, not an oversight. Worth confirming it is the trade you want,
since it is the one place the design pays a structural cost for a hypothetical future.

**See:** [data-model/03 §1](data-model/03-membership.md#1-membership_type--one-row-kept-as-a-table)

---

### F-10 🔴 Which invariants the ORM cannot express, and who writes those

**Question.** [D-072](decisions/decision-log.md#d-072--the-documentation-carries-no-sql-the-schema-is-the-orms-job)
moved the schema to an ORM. Most of what the deleted DDL asserted an ORM will generate from a
model definition. **Three shapes it generally cannot**, and each appears dozens of times in these
documents:

The list below is four shapes, and they are not equally bad. Shapes 1–3 have a known answer even
if nobody has chosen it yet; shape 4 does not have one, and is why this question is red.

1. **No two open rows overlap** — the temporal invariant under memberships, participations,
   assignments, guardianships, grants and exposures. On PostgreSQL this needs an exclusion
   constraint over a range built from two columns.
2. **Unique, but only among rows satisfying a condition** — "one open request per person and
   type", "one primary contact among open rows", "one live exposure per unit and assignment".
   These need a partial unique index; a plain unique constraint over the same columns is a
   *different and wrong rule*, forbidding the second closed row that history requires.
3. **Anything whose answer comes from another table or from the resolver** — the holder limit, the
   nesting rules, the exposure direction, per-scheme identifier uniqueness
   ([D-080](decisions/decision-log.md#d-080--five-contradictions-the-translation-surfaced-and-how-each-was-resolved)
   item 1 is this class). No declarative constraint can state these; they need a check inside the
   writing transaction plus a report.
4. **A column that may not change once it is set** — `org_unit.parent_unit_id`
   ([D-036](decisions/decision-log.md#d-036--units-cannot-be-reparented-a-unit-that-moves-is-a-new-unit)).
   This is not a PostgreSQL limitation that an ORM happens to inherit; **no declarative constraint
   in any database states it**, which is why it survived into the hand-written migrations even when
   the DDL was still in these documents. It is a rule about a transition between two states of a
   row, and a constraint sees states.

   **What makes it different from 1–3 is that there is no report.** The nightly checks catch shape 1
   and 2 by finding a pair of rows that should not coexist, and shape 3 by recomputing an answer and
   comparing. A reparent leaves no offending row: every row in the database stays individually valid
   and satisfies every constraint, while the meaning of the subtree's entire history moves under
   them. Nothing can be compared afterwards, because there is no second statement of the intended
   hierarchy to compare against — and the `path` the damage would show up in is itself derived and
   would simply be recomputed to match. So the guard is the whole enforcement, and it must sit in
   the write path ([data-model/02 §4](data-model/02-organization.md#a-unit-never-changes-parent)),
   with an automated test that attempts the update and expects a refusal. **A test is not a
   substitute for the guard; it is the only remaining evidence that the guard was intended to stay.**

**Why this is a question and not a task.** The fallback an ORM offers for all three is validation
in the model layer, and
[data-model/00 §6a](data-model/00-conventions.md#6a-who-enforces-an-invariant-now) explains why
that is not the same guarantee: an import, a data fix, and a second client all bypass it. **The
legacy import is the specific case that makes this urgent rather than theoretical** — the corpus
arrives through exactly the path that model-layer validation does not cover, and an overlapping
membership written by the importer is nearly impossible to diagnose afterwards, because the two
rows look like two memberships and only one of them was ever real.

**Needed.** A decision per shape — hand-written migration, database check, or application check
plus report — before the first migration is generated, not discovered during one. **The
recommendation in [data-model/00 §6a](data-model/00-conventions.md#6a-who-enforces-an-invariant-now)
is that shapes 1 and 2 are hand-written migrations, and that this is the condition on which using
an ORM is safe rather than an argument against using one.**

**Impact if unanswered.** Not a crash. A system whose constraints are quietly absent, whose
integrity checks (every "Invariants to verify" section) then start reporting rows, and whose first
report is read as a data-quality problem rather than as the missing guarantee arriving on schedule.

**See:** [data-model/00 §6a](data-model/00-conventions.md#6a-who-enforces-an-invariant-now),
[appendix/erd.md's inventory](appendix/erd.md), which marks every temporal entity.

---

## G. Events — designed, with three things left open

The module is written: [domain/07-events.md](domain/07-events.md) and
[data-model/08-events.md](data-model/08-events.md). Fifteen questions have been answered
(D-058 … D-067, plus EV-1 and EV-5 in a later round); what remains below is what those answers
did **not** settle. None of it blocks implementation.

### EV-1 ✅ **Closed** — there is no age ceiling; the grant is the rule

**Answered: leave it.** No `min_age`/`max_age` on `event`, and no age test anywhere in the path
that places a registration ([D-070](decisions/decision-log.md#d-070--an-event-has-no-age-ceiling-the-grant-is-the-rule)).

**The residual risk is accepted, not eliminated**, and it is worth restating so nobody
"closes" it later without knowing: an event opened to `all_members` can be registered for by a
nine-year-old and **nothing objects**. What makes it survivable is attribution
(`source = 'staff'`), a roster query one join away from birth dates, and the fact that the
age-bounded case is already handled by opening an event to the right unit.

**If it ever needs closing, the shape is a built-in audience, not a column on the row** —
`all_members` is a rule the resolver evaluates, so `members_aged_13_plus` can be one too. That
keeps every answer to "who may register" inside `access_grant`, which is the property D-060
bought and D-070 defended.

### EV-2 🟡 Retention of `event_answer`

**The question.** A dietary answer citing a medical condition is health data. Event answers
end with the event — but "end" is not a defined policy, and health data has a retention
obligation.

**Why it is not trivial.** [D-061](decisions/decision-log.md#d-061--event-answers-are-read-by-that-events-organizers)
made an event form the route by which a camp leader learns a child has a nut allergy. That is
a deliberate widening, and it puts health-adjacent data in a table whose protections are weaker
than the health record's — **and in round 6 that gap widened twice over**: there is no longer a
`dependent.medical.*` code marking which data is the sensitive kind (**E-7**), and the audience
entitled to read an answer is whoever runs that event, a set sized by whoever creates it.
The retention policy is the remaining half of that trade.

**Needed.** Legal input, like B-3. The technical question — where does it live, who may read
it — is answered; whether it must be deleted, kept, or archived is not.

### EV-3 ✅ **Closed** — cancelling voids the request, and paid money queues

**Answered by [D-076](decisions/decision-log.md#d-076--money-that-cannot-be-matched-waits-for-a-person),
in the finance module rather than here.** The recommendation was right and the mechanism arrived
before the policy did:

- **Cancelling an event voids its outstanding payment requests**, recording why
  ([finance model §2b](data-model/07-finance.md#2b-money-that-cannot-be-matched)).
- **Money already received becomes a queue item** for a person to refund or carry forward. Not
  auto-refunded — that needs an outbound bank integration and would return a grandparent's
  mistaken camp fee.

**Why the recommendation held.** It said neither, automatically, because an automatic release would
be a second automatic transition in a module with exactly one
([D-066](decisions/decision-log.md#d-066--payment-confirms-the-place-and-the-release-deadline-is-the-one-automatic-transition)).
That argument was strong enough to survive contact with the payment design unchanged. **Voiding an
outstanding request is not that second transition** — a request nobody has paid against has no state
to preserve and nobody is disadvantaged by its withdrawal, which is exactly the property the waitlist
release had and this does not.

**What actually moved.** The question assumed cancellation was the interesting case and payment an
afterthought parked in finance. It is the reverse: cancellation is where **most of the unmatched
queue's volume comes from**, because a cancelled event keeps its registrations
([D-064](decisions/decision-log.md#d-064--there-is-no-event-status-visibility-is-the-permission-model))
and therefore its money obligations, unless something explicitly voids them.

**Impact.** Answered; the queue itself lives in the finance module.

### EV-4 🟢 `was_present` as a safeguarding record

**The question.** Presence is the record of who was actually in the organization's care
([D-067](decisions/decision-log.md#d-067--presence-is-a-three-valued-fact-on-the-registration)).
Does it need its own retention, or its own permission?

**Why it might.** It is the record that answers "was this child at camp on the day of the
incident" — the question insurance and any safeguarding review will ask. That is a heavier
thing than "who said they were coming", and it currently shares both a table and a permission
with the registration.

**Why it might not.** It is meaningless without the registration it belongs to, and splitting
it would put two rows in two places describing one fact.

**Impact.** Splitting it is a table; keeping it is nothing. The argument for splitting is
permissions — a volunteer who takes the register at camp is not the same trust as one who may
alter the roster. See EV-5, which is the same tension.

### EV-5 ✅ **Closed** — it split, and the new permission sits a level lower

**Resolved in favour of the split: `event.presence.mark`, at `contribute`.**

The reasoning recommended the split and the recommendation stood. Marking the register at a
camp door is not the same trust as deleting a child from the roster, and one permission forced
organizations to hand the clipboard-holder both. Note where the new permission landed:
`contribute`, not `manage` — **so the volunteer taking the register is somebody who could
already register themselves**, which is the right bar for the job and plainly the wrong bar
for altering who is coming. Same shape as `membership.lapse` versus `membership.terminate`
(D-022): one routine, one consequential.

Thirteen `event.*` codes now exist; `event.admin` is not one of them
([D-068](decisions/decision-log.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle)).

**See:** [appendix/permission-catalog.md §8a](appendix/permission-catalog.md#8a-events)

---

## H. Not yet designed

Each of these is referenced by the schema and has hooks left for it — **except health records, which
has no hooks because it has no design at all, and whose missing design is load-bearing in two other
documents. Read H-0 below before the table.**

| Area | Hooks already in place | Notes |
|------|------------------------|-------|
| **Events** ✅ | **Designed** — [domain/07](domain/07-events.md), [data-model/08](data-model/08-events.md) | Fifteen questions answered; three left in § G above. |
| **Fees and payments** | [data-model/07-finance.md](data-model/07-finance.md) — **architecture settled, policy open** | **Nine open questions**, of which one is new. Round 6 closed the architectural ones: money arrives by **bank API**, is requested by **variable symbol + QR code**, there is **no card gateway**, and unmatched money **queues** ([D-075](decisions/decision-log.md#d-075--money-arrives-from-a-bank-api-a-payment-is-requested-by-variable-symbol-and-qr-code), [D-076](decisions/decision-log.md#d-076--money-that-cannot-be-matched-waits-for-a-person)). What remains needs somebody in the organization asked: proration, discounts, insurance, waivers, invoices. |
| **Documents** | `access_grant.scope_type = 'document'`; the evidence-reference hook belonged to the removed requirement tables | Needs: storage, versions, retention, consent-driven access. |
| **Consents** | No `dependent.consent.*` any more — a guardian at `write` may give and manage consents ([D-074](decisions/decision-log.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular)) | Needs: template, per-activity consent, expiry, revocation, who may consent. No longer connected to a membership requirement ([D-044](decisions/decision-log.md#d-044--nothing-gates-a-membership-request-except-identity-and-payment)). **`is_legal_decision_maker` on the guardianship row is the existing hook for "who may sign" — and it is now the only place that distinction lives**, since the right level cannot express it. |
| **Health records** | **Nothing. There is no health entity in the data model** — see **H-0** below | **Highest-sensitivity data in the system, and the exposure grew in round 6.** [D-074](decisions/decision-log.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular) deleted the codes that used to gate medical visibility, so "read everything except the health file" is no longer sayable — see **E-7**. This raises the case for designing the module **before** the coarse default is relied on, rather than after: separate retention, separate access, likely separate storage, and its own legal review. |
| **Communication** | `message.send_direct`, `message.broadcast` (scoped) — shape decided, detail undesigned | **Shape decided by [D-077](decisions/decision-log.md#d-077--messaging-is-direct-by-default-broadcast-is-an-ordinary-scoped-permission-and-the-recipient-chooses-the-channel):** internal first, external channels are delivery; everyone may send direct; `broadcast` is one scoped permission; **the recipient picks the channel.** Needs: templates, opt-out granularity, retention, moderation. The rule against contacting minors directly was **declined as a sender restriction** — see **MSG-1** below. |
| **Reporting** | `report.*` permissions sketched | The historical queries in [domain/05](domain/05-membership-lifecycle.md#8-since-1985--the-ten-queries-this-design-must-answer) are the starting set. Query 10 (members per year since 1985) is the acceptance test. |
| **API and UI** | — | Not started. The resolver's `p_at` parameter exists partly for this. |
| **Notifications** | — | Expiring roles, members inside the renewal window, unpaid fees. Note the renewal window makes this *dated* rather than status-driven — a nightly job over `in_renewal_window()`. |
| **Payment gateway** | — | **Answered, so this row is now narrower than it was.** The organization collects via **bank API**, not a card gateway ([D-075](decisions/decision-log.md#d-075--money-arrives-from-a-bank-api-a-payment-is-requested-by-variable-symbol-and-qr-code)): no webhooks, no disputes, no processor reconciliation. What remains undesigned is the **statement import** itself — file formats, the idempotency key, and what happens to an account the bank revises. |
| **Multi-language** | — | Unit names and permission display names are all in the database. Whether they need translation columns is unanswered. |

---

### H-0 🔴 The medical record is referred to throughout these documents and does not exist

**Found while starting the health-records module, and it changes what that module is.** Sentences
across five files discuss who may read *the medical record* as though it were a table:

| Where | What it says |
|---|---|
| §H, this file, Health records row | "a `view` guardian already sees them" |
| [E-7](#e-7--one-level-cannot-separate-the-medical-record-from-the-profile) | "a guardian either sees everything about the child or nothing" |
| [permission-catalog §9](appendix/permission-catalog.md#9-there-is-no-dependent-namespace) | a `view` guardian "reaches the fee history and the health record" |
| [data-model/08 §7](data-model/08-events.md#health-data-and-the-discipline-this-requires) | "the medical file, which **no event permission reaches**" |
| [data-model/04 §2](data-model/04-relationships.md#2-the-guardians-right-none-view-or-write) | the case the old codes existed for is "access to medical information" |

**No document defines one.** There is no health or medical entity in any
[data-model](data-model/00-conventions.md) file and no box in [the ERD](appendix/erd.md). The only
thing that ever had a medical shape in this model was a `medical_form` **requirement code**, and
[D-044](decisions/decision-log.md#d-044--nothing-gates-a-membership-request-except-identity-and-payment)
deleted that table. So the referent is a habit of speech inherited from the old
`dependent.medical.*` permission codes, which named a sub-resource of a table that was itself
removed with [D-074](decisions/decision-log.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular).

**What this does to the arguments built on it — most of them survive, one does not.**

- **E-7 stands, and is sharper than it looked.** "One right level cannot separate the medical record
  from the profile" is *still true* about a record that does not exist: it says the guardian model has
  no granularity to offer whenever something sensitive is later attached to a person. That is a real
  finding about the model, not about a table.
- **"No event permission reaches the medical record" is true but empty.** Nothing reaches it, because
  nothing is there. The paragraph in 08-events that leans on this to reassure is right about
  permissions and wrong about the risk: **the only health data the system actually holds today is in
  `event_answer.value`** — free text typed into a form, read by whoever runs the event, with no
  retention policy ([EV-2](#ev-2--retention-of-event_answer)). The sensitive data is in the weakest
  place, not the strongest.
- **"A `view` guardian already sees them" is simply false**, and was written as a reason not to design
  the module early. It is replaced by the question below.

**The question, before any field is designed.** *What is a health record in this system?* Not "which
fields" — the shape. Three coherent answers, and they imply different systems:

1. **Structured entries** (allergy, medication, condition, instruction) — queryable, so "who in this
   unit has a nut allergy" is answerable, and the price is that the organization is now a custodian of
   diagnosable data with everything that implies.
2. **Documents only** — a scanned form filed against the person, using the `document` scope that
   already exists in the catalog. Cheap, legally simple, and useless in an emergency, because nobody
   reads a PDF at 23:00 in a tent.
3. **Hybrid** — a small set of structured, actionable entries plus documents behind them for anything
   a form can hold. This is what organizations actually do on paper, and the option the rest of the
   corpus seems to assume.

**Why this is H-0 and not a row in the table.** Every other open question about health — who may read
it, whether the guardian default changes, what event organizers get, how long answers survive,
whether E-7 needs its exception — takes a different answer depending on this one. It is also the only
module whose *absence* is already load-bearing: two documents cite the medical record's protections in
order to argue that something else is safe.

**Needed.** One answer above, then a round of design questions that follow from it.

---

### MSG-1 ✅ **Closed** — a direct message to a minor is mirrored to their guardians

**Raised by [D-077](decisions/decision-log.md#d-077--messaging-is-direct-by-default-broadcast-is-an-ordinary-scoped-permission-and-the-recipient-chooses-the-channel),
which declined the restriction rather than forgetting it.**

**The situation.** Messaging has two sender tiers — direct, which everyone may do, and `broadcast`,
which is a permission. **Neither tier mentions age.** So any person with an account may send a
private message to any child with an account, and nothing in the model prevents it, records it as
unusual, or tells anyone. This is not a gap created by oversight: the question asked whether staff
may address a child or only their guardians, and the answer replaced it with a model in which
age is not a sender concept at all. **The rule the communication section had promised — "a rule
against contacting minors directly" — is therefore not implemented, and it is worth being blunt
that this is the most consequential unanswered question in the file.**

**Why restricting senders is the wrong fix here.** An age branch in the resolver is what
[D-070](decisions/decision-log.md#d-070--an-event-has-no-age-ceiling-the-grant-is-the-rule)
refused for events, on the grounds that a condition evaluated at check time which the capability
model does not know about becomes the first rule in a rule engine nobody wants. It would also be
the kind of restriction that gets loosened the first time it inconveniences a leader, and a
permission that is routinely bypassed on a messaging system is worse than none, because it makes
the bypass normal.

**Recommendation — restrict visibility, not permission.** Mirror direct messages reaching a minor
to that minor's guardians, and make the mirroring visible to the sender. Then:

- nothing is blocked, so the resolver still has no age branch;
- nothing is secretly unread, which is the actual safeguarding property;
- it is built on the guardianship rows the organization already maintains, so it needs no new
  authority concept;
- and it degrades honestly — a child with no guardian on record gets no mirroring, which is the
  same safeguarding gap **check 4** in [data-model/04 §6](data-model/04-relationships.md#6-invariants-to-verify)
  already alerts on, arriving through a second channel.

**The variant to reject.** "Only guardians and unit leaders may message a child." That is the
restriction wearing the visibility recommendation's clothes: it is a sender rule, it needs the age
branch, and it silently tells a child that the adult messaging them has been vetted — which the
model does not establish, and the organization records no background checks
([D-043](decisions/decision-log.md#d-043--no-background-checks-are-recorded-in-this-system)).

**Answered (round 6): the recommendation is adopted**, as
[D-082](decisions/decision-log.md#d-082--a-direct-message-to-a-minor-is-mirrored-to-the-minors-guardians)
— mirror to guardians, tell the sender, block nothing. Three details were settled with it, because
"mirror it to the guardians" does not by itself say who the guardians are *to this message*:

- **Which guardians.** Those whose right level is `view` or `write`. A guardian at `none` receives
  nothing: `none` is the organization having already decided that this party sees nothing about the
  child, and a safeguarding rule is not a licence to undo a recorded decision by side effect. **A
  minor whose guardians are all `none` is therefore reported with the minors who have no guardian at
  all** — otherwise the exclusion would be a way to make a child silently unwatched.
- **Which set, as of when.** The guardianships open *at the moment the message is sent*, frozen into
  the delivery. A guardianship closed afterwards does not lose its mirror, and a guardian added later
  does not acquire old threads — same discipline as
  [06-audit §2](data-model/06-audit-and-import.md#2-audit_log), which keeps the
  trail answering "what was true then".
- **Broadcast is not mirrored.** A scoped broadcast is already addressed to a set, recorded, and
  attributable; mirroring exists for the *private* case, which is the one that can be invisible.

**What mirroring is not.** Not approval, not a gate, and not evidence anyone read it. It buys the one
property the safeguarding argument actually needs — **no private conversation about a child is
secretly unread** — without putting an age into the resolver.

**See:** [D-082](decisions/decision-log.md#d-082--a-direct-message-to-a-minor-is-mirrored-to-the-minors-guardians),
[permission-catalog's `message` row](appendix/permission-catalog.md#10-deferred-namespaces),
[glossary — Mirroring](glossary.md#communication).

---

## R. Resolved — moved to the decision log

Kept here so a reader of this file knows the question was asked and where the answer lives,
rather than finding it silently deleted.

| Was | Question | Settled by | In one line |
|-----|----------|-----------|-------------|
| A-1 | The organizational structure | [D-035](decisions/decision-log.md#d-035--one-root-unit-all-sub-units-nest-arbitrarily-beneath-it) | One root; all sub-units nest arbitrarily beneath it. |
| A-1 | The unit type vocabulary | [D-054](decisions/decision-log.md#d-054--the-sub-unit-vocabulary-is-not-seeded-the-organization-defines-its-own-types) | Not seeded — `org_unit_type` is runtime data; only the root type ships. |
| B-1 | How much legacy data, in what shape? | [D-056](decisions/decision-log.md#d-056--the-legacy-import-expects-a-large-corpus-with-legacy-member-numbers) | Large, with legacy member numbers — exact matches, so review is a work queue. |
| D-9 | Is `household` load-bearing at all? | [D-057](decisions/decision-log.md#d-057--household-is-removed) | No — removed entirely. Addresses are temporal `person_contact` rows. |
| F-1 | Which permissions and roles does the organization need? | [D-055](decisions/decision-log.md#d-055--the-permission-catalog-is-deliberately-comprehensive-and-granular) | The catalog stays large and granular; it is a menu, not a checklist. |
| — | Eligibility for an event — a separate rule engine? | [D-060](decisions/decision-log.md#d-060--eligibility-is-capability-there-is-no-separate-rule-engine) | No — eligibility **is** capability. `event.register_self` at `contribute`, via audiences. |
| — | Is `unanswered` a stored attendance value? | [D-059](decisions/decision-log.md#d-059--unanswered-is-the-absence-of-a-row-a-registration-stores-two-values) | No — absence of a row. Two stored values: `attending`, `not_attending`. |
| — | Is a weekly meeting an event? | [D-058](decisions/decision-log.md#d-058--an-event-is-a-dated-occasion-owned-by-exactly-one-unit) | No — it is `unit_participation`. No recurrence, no series table. |
| — | One owning unit per event, or several? | [D-058](decisions/decision-log.md#d-058--an-event-is-a-dated-occasion-owned-by-exactly-one-unit) | Exactly one. A joint camp is one unit's event another unit participates in. |
| — | Are organizers a grant or a roster? | [D-062](decisions/decision-log.md#d-062--organizers-are-appointed-on-the-event-not-granted) | A roster on the event — labelled and ordered. Grants stay separate. |
| — | Do unit roles reach the unit's own events? | [D-063](decisions/decision-log.md#d-063--an-event-is-an-artifact-of-its-unit-not-a-child-of-it) | Yes — an event is an **artifact** of its unit, not a child. Not inheritance (D-031 stands). |
| — | Does an event have a status (`draft`, `published`)? | [D-064](decisions/decision-log.md#d-064--there-is-no-event-status-visibility-is-the-permission-model) | No status column. Visibility **is** the permission model; cancellation is a fact. |
| — | What happens when a full event gets another registration? | [D-065](decisions/decision-log.md#d-065--capacity-is-a-waitlist-threshold-and-organizers-may-exceed-it) | Waitlisted for self-service; admitted for organizers; the overrun reported. |
| — | Does paying confirm a place? | [D-066](decisions/decision-log.md#d-066--payment-confirms-the-place-and-the-release-deadline-is-the-one-automatic-transition) | Yes when the event has a fee; most events are free and confirm immediately. |
| — | Do organizers record who actually came? | [D-067](decisions/decision-log.md#d-067--presence-is-a-three-valued-fact-on-the-registration) | Yes — `was_present`, three-valued. It is the "who was in our care" record. |
| — | May an event form collect medical detail? | [D-061](decisions/decision-log.md#d-061--event-answers-are-read-by-that-events-organizers) | Effectively yes: answers are read by that event's organizers, and **no event permission reaches the health record**, so the form is the only route for a camp leader to learn an allergy at all. A recorded widening, restated after D-074 removed the namespace the original wording relied on. |
| A-2 | Permissions conditioned on membership status | [D-039](decisions/decision-log.md#d-039--member-permissions-require-a-current-paid-membership) | Yes, enforced by the resolver, with guardianship and ownership carved out. |
| A-3 | Activate on payment or on approval? | [D-040](decisions/decision-log.md#d-040--the-fee-expires-yearly-a-date-tracked-renewal-window-replaces-a-grace-status) | On payment; the fee expires yearly and a dated renewal window replaces a grace status. |
| A-4 | Background checks | [D-043](decisions/decision-log.md#d-043--no-background-checks-are-recorded-in-this-system) | None are recorded in this system. |
| A-4 | The expiry date | [D-047](decisions/decision-log.md#d-047--the-fee-expires-on-1-january) | 1 January; the organizational year runs with the calendar. |
| A-4 | The renewal window length | [D-048](decisions/decision-log.md#d-048--the-renewal-window-is-60-days-and-is-a-configuration-parameter) | 60 days, stored as a parameter rather than compiled in. |
| C-1 | May the root read into its sub-units? | [D-049](decisions/decision-log.md#d-049--the-root-may-not-read-into-its-sub-units-scope_exposure-is-the-only-crossing) | No. `scope_exposure` is the only crossing; no reporting channel is built. |
| D-6 | How may the membership gate be waived? | [D-051](decisions/decision-log.md#d-051--the-membership-gate-is-waived-by-a-permission-not-only-by-a-role-flag) | A person-level `system.gate_exempt` permission, in addition to the role flag. |
| D-7 | The root participation row at renewal | [D-050](decisions/decision-log.md#d-050--a-renewal-inside-the-window-extends-the-existing-root-participation-row) | Extended across the renewed period; one row, no gap. |
| B-3 (part) | Erasure: what shape? | your answer, round 5 | Redact the person, keep the financial and membership skeleton. *(The retention policy is still open — see B-3.)* |
| C-1 (largely) | Organization-wide operational roles without downward inheritance | [D-035](decisions/decision-log.md#d-035--one-root-unit-all-sub-units-nest-arbitrarily-beneath-it) | The problem dissolves: the root owns the registry and the fees. What remains is a reporting question — see C-1. |
| C-2 | May units be reparented retroactively? | [D-036](decisions/decision-log.md#d-036--units-cannot-be-reparented-a-unit-that-moves-is-a-new-unit) | Not at all — a unit that moves is a new unit. |
| D-1 | Fee per person or per household? | [D-037](decisions/decision-log.md#d-037--exactly-one-membership-type-the-fee-is-flat-and-per-person) | Per person, flat, yearly. |
| D-2 | One open membership, or several of different types? | [D-037](decisions/decision-log.md#d-037--exactly-one-membership-type-the-fee-is-flat-and-per-person), [D-041](decisions/decision-log.md#d-041--belonging-to-a-sub-unit-is-a-participation-record-not-a-membership) | One type, so one open membership, enforced person-wide. |
| D-3 | Age-out timing | [D-038](decisions/decision-log.md#d-038--membership-is-ageless) | Retired — there is no age-out. |
| D-4 | Child → adult transition | [D-038](decisions/decision-log.md#d-038--membership-is-ageless) | Retired — there are no membership categories to transition between. |
| D-5 | Membership type vocabulary | [D-037](decisions/decision-log.md#d-037--exactly-one-membership-type-the-fee-is-flat-and-per-person) | One type, `member`; counselor is a position, not a type. |
| E-1 | Default rights when a guardianship is created | [D-046](decisions/decision-log.md#d-046--guardianship-defaults-depend-on-how-the-guardianship-was-created) | `write` for a self-registered child's guardian; `view` for staff-created and imported rows; chosen at creation when recorded manually. **D-074 turned the answer from a code bundle into one level**, which is why the decision still stands on its original wording. |
| F-2 | Polymorphic `scope_id` vs a `grantable_item` supertable | your answer, round 6 | Polymorphic — `scope_type` plus `scope_id`, as currently designed. |
| — | The bulk scope-exposure tool | [D-045](decisions/decision-log.md#d-045--the-bulk-scope-exposure-tool-is-removed) | Removed once audiences existed to cover the case it was for. |
| — | What a membership request must contain | [D-044](decisions/decision-log.md#d-044--nothing-gates-a-membership-request-except-identity-and-payment) | Identity and the fee. The whole requirement mechanism is gone. |
| — | Whether grants may target groups | [D-042](decisions/decision-log.md#d-042--grants-may-target-audiences-not-only-individuals) | Yes — built-in rule-evaluated audiences plus admin-managed named groups. |
| E-2 | What happens to guardianship at majority? | [D-069](decisions/decision-log.md#d-069--guardianship-ends-when-a-person-ends-it-the-system-takes-no-position-on-majority) | Nothing — no job, no queue, no computed date. A person ends the row. *(Reverses D-024.)* |
| F-3 | Must a high-authority role assignment have an end date? | [D-071](decisions/decision-log.md#d-071--nothing-forces-a-role-assignment-to-end-the-gate-and-the-report-are-the-control) | No. The membership gate plus a human review report; the earlier "yes" recommendation is withdrawn. |
| F-4 | Should `person.admin` subsume merge and redact? | [D-068](decisions/decision-log.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle) | Moot — there are no per-resource `admin` permissions. The choice moved into reviewable role contents. *(Reverses D-007.)* |
| — | Should every resource expose an `admin` permission? | [D-068](decisions/decision-log.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle) | No. Sixteen codes and the resolver's prefix match are gone; roles are the bundle. |
| EV-1 | Does an event need an age ceiling? | [D-070](decisions/decision-log.md#d-070--an-event-has-no-age-ceiling-the-grant-is-the-rule) | No. The grant is the rule; a future ceiling would be a built-in audience, not a column. |
| EV-5 | Should `event.manage_participants` split? | this round | Yes — `event.presence.mark` at `contribute`, one level below the roster. |

---

## I. Assumption index

Every *Assumption:* in the documentation, so they can be reviewed as a group. Once you confirm
one, it should be promoted to a numbered decision and struck from [§ R](#r-resolved--moved-to-the-decision-log).

Rows marked **†** are now backed by a decision rather than a bare assumption — kept here
because the docs still cite them and because the decision is worth seeing in this list.

| # | Assumption | Where |
|---|-----------|-------|
| 1 | PostgreSQL 14+ with `btree_gist` | [data-model/00](data-model/00-conventions.md#1-target-platform) |
| 2 | No automatic merging (D-004) † | [domain/03](domain/03-identity-and-legacy.md#4-match-signals) |
| 3 | Minors need guardian consent for an account | [domain/02](domain/02-actors.md#2-who-registers-and-why) |
| 4 | A self-registered child's parent gets a `write` right over the child (D-046, as amended by D-074) † | [data-model/04](data-model/04-relationships.md#2-the-guardians-right-none-view-or-write) |
| 5 | Locality orders allows only; deny is absolute (D-032) † | [domain/06](domain/06-authorization-model.md#6-the-resolver) |
| 6 | Membership activates on payment (D-040) † | [domain/05](domain/05-membership-lifecycle.md#1-the-flow-you-described) |
| 7 | The fee is per person and yearly (D-037) † | [domain/05](domain/05-membership-lifecycle.md#6-renewal-and-the-yearly-fee) |
| 8 | Renewal opens a new row, not an extended `valid_to` (D-016) † | [domain/05](domain/05-membership-lifecycle.md#6-renewal-and-the-yearly-fee) |
| ~~9~~ | ~~Guardianship reviewed at majority, not auto-expired~~ — **superseded**: neither, the system takes no position (D-069) | [data-model/04](data-model/04-relationships.md#1-guardianship) |
| 10 | Display name uses `preferred_name` if set | [data-model/01](data-model/01-identity.md#3-person_name--name-history) |
| 11 | Merge chains allowed (B-2) | [data-model/01](data-model/01-identity.md#9-views) |
| 12 | Only confirmed payments count toward a balance | [data-model/07](data-model/07-finance.md#3-keeping-membershipoutstanding_balance-honest) |
| 13 | No sub-unit types are seeded; nesting is permissive by default (D-054) † | [data-model/02](data-model/02-organization.md#10-seed-data) |
| 14 | `membership_type` is seeded with exactly one row (D-037) † | [data-model/03](data-model/03-membership.md#8-seed-data) |
| 15 | `person.gender` is needed for reporting | [data-model/01](data-model/01-identity.md#2-person) |
| 16 | Imported rosters end at the organizational year end (D-028) † | [data-model/06](data-model/06-audit-and-import.md#3-import-pipeline) |
| 17 | All business tables are audited | [data-model/06](data-model/06-audit-and-import.md#6-open-issues) |
| 18 | Currency is EUR | [data-model/07](data-model/07-finance.md#2-minimal-provisional-shape) |
| 19 | `access_log` is not human-annotatable | [data-model/05](data-model/05-authorization.md#9-access_log) |
| ~~20~~ | ~~Each permission has an `admin` sibling~~ — **superseded**: no per-resource wildcard codes (D-068) | throughout |
| 21 | No downward inheritance; exposures are written by the unit (D-031) † | [domain/06](domain/06-authorization-model.md#2-scope-authority--no-downward-inheritance) |
| 22 | The person record holds no deceased flag (D-034) † | [data-model/01](data-model/01-identity.md#2-person) |
| 23 | Positions are multi-holder unless `max_holders` says otherwise (D-033) † | [domain/04](domain/04-organization-structure.md#4-positions) |
| 24 | Membership is ageless — no category, no `min_age`, no `max_age` (D-038) † | [data-model/03](data-model/03-membership.md#1-membership_type--one-row-kept-as-a-table) |
| 25 | A grant targets a person **or** an audience, never both (D-042) † | [data-model/05](data-model/05-authorization.md#6-access_grant--the-per-item-layer) |
| 26 | Built-in audiences are rules evaluated by the resolver, not stored lists (D-042) † | [data-model/05](data-model/05-authorization.md#8-audience--grants-that-target-a-set-of-people) |
| 27 | Belonging to a sub-unit is participation, not membership (D-041) † | [data-model/03](data-model/03-membership.md#5-unit_participation) |
| 28 | Roles require a current membership unless `requires_membership = false` (D-039) † | [data-model/05](data-model/05-authorization.md#3-role-and-role_permission) |
| 29 | There is no bulk exposure tool and no `bulk:` reason marker (D-045) † | [data-model/05](data-model/05-authorization.md#5-scope_exposure--how-a-unit-delegates-upward) |
| 30 | No background checks are recorded anywhere (D-043) † | throughout |
| 31 | `access_grant.scope_id` is polymorphic, with no foreign key (F-2) † | [data-model/05](data-model/05-authorization.md#6-access_grant--the-per-item-layer) |
| 32 | The organizational calendar is 1 January plus a 60-day window (D-047, D-048) † | [data-model/03](data-model/03-membership.md#1-membership_type--one-row-kept-as-a-table) |
| 33 | The root reads into a sub-unit only through `scope_exposure` (D-049) † | [domain/06](domain/06-authorization-model.md#24-the-organization-wide-role-problem-and-why-it-mostly-dissolved) |
| 34 | A renewal extends the root participation row rather than closing it (D-050) † | [data-model/03](data-model/03-membership.md#51-a-participation-row-on-the-root-unit) |
| 35 | The membership gate is waived by a person-level permission, not only a role flag (D-051) † | [data-model/05](data-model/05-authorization.md#3-role-and-role_permission) |
| 36 | The permission catalog is deliberately comprehensive and granular (D-055) † | [appendix/permission-catalog.md](appendix/permission-catalog.md) |
| 37 | The legacy corpus is large and carries legacy member numbers (D-056) † | [domain/03](domain/03-identity-and-legacy.md#4-match-signals) |
| 38 | There is no `household` table; addresses are temporal `person_contact` rows (D-057) † | [data-model/04](data-model/04-relationships.md#3-there-is-no-household-table) |
| 39 | An event belongs to exactly one unit; meetings are participation (D-058) † | [data-model/08](data-model/08-events.md#2-event) |
| 40 | "Unanswered" is the absence of a registration row (D-059) † | [data-model/08](data-model/08-events.md#4-event_registration) |
| 41 | Eligibility is capability — there is no rule engine (D-060) † | [domain/07](domain/07-events.md#4-who-may-register-capability-not-a-separate-rule-engine) |
| 42 | Event answers are read by that event's organizers (D-061) † | [data-model/08](data-model/08-events.md#7-event_question-and-event_answer) |
| 43 | Organizers are a roster on the event, not grants (D-062) † | [data-model/08](data-model/08-events.md#3-event_organizer) |
| 44 | An event is an artifact of its unit, so unit roles reach it (D-063) † | [domain/07](domain/07-events.md#6-the-hinge-organizers-and-the-scope-mismatch) |
| 45 | There is no event status; visibility is the permission model (D-064) † | [data-model/08](data-model/08-events.md#2-event) |
| 46 | Capacity is a waitlist threshold organizers may exceed (D-065) † | [data-model/08](data-model/08-events.md#5-capacity-and-the-waitlist) |
| 47 | Payment confirms a place; free events confirm immediately (D-066) † | [data-model/08](data-model/08-events.md#6-payments-and-confirmation) |
| 48 | Presence is a three-valued fact, not a boolean (D-067) † | [data-model/08](data-model/08-events.md#4-event_registration) |

---

## How to answer

**The blocking set is now empty.** Four rounds have cleared every question that was holding
the schema still, so nothing here has to be answered before implementation could start.

What remains is genuinely deferrable, and the most useful next ones are:

1. **F-5** — which built-in audiences are needed, and whether parameterised ones are seeded
   per instance or created on demand
2. **F-3** — should high-authority role assignments require a `valid_to`?
3. **E-2 / E-4** — guardianship at majority, and confirming the gate's guardianship carve-out
   is intended
4. **B-2 / B-3** — merge chains, and the retention policy (the latter needs legal input,
   not design)

Everything else can be answered as we go. The schema is built so that most answers change
data rather than structure — which is why the four above are worth a moment and the rest are
not.

**Answered in round 4:** the unit type vocabulary (A-1 — not seeded, D-054); the permission
catalog (F-1 — comprehensive and granular on purpose, D-055); the legacy corpus
(B-1 — large, with member numbers, D-056); and `household` (D-9 — removed entirely, D-057).
All four are in [§ R](#r-resolved--moved-to-the-decision-log) with links to the decisions that
settled them.

**Answered in round 3, for reference:** the organizational calendar (A-4 — 1 January, 60
days); the root's read access into sub-units (C-1 — `scope_exposure` only); the membership
gate's waiver (D-6 — a person-level permission, in addition to the role flag); and the root
participation row at renewal (D-7 — extended).
