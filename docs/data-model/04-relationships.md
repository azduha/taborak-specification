# Data Model — Relationships

`guardianship`, and the single right level that travels with it.

Domain rationale: [../domain/02-actors.md](../domain/02-actors.md#5-acting-on-behalf).

This document describes **requirements**. It contains no DDL
([D-072](../decisions/round-06.md#d-072--the-documentation-carries-no-sql-the-schema-is-the-orms-job));
the ORM decides how each rule is enforced.

---

## 1. `guardianship`

**Fields**

| Field | Kind | Notes |
|---|---|---|
| `id` | internal identifier | Never appears in a URL or an external reference |
| `guardian_person_id` | reference to person, required | One side of the relationship |
| `dependent_person_id` | reference to person, required | The other side. **Must not equal the guardian** |
| `relationship` | enum: `parent` / `legal_guardian` / `foster_parent` / `step_parent` / `grandparent` / `sibling` / `other`, required | `sibling` and `other` exist because the organization will meet cases that do not fit, and forcing them into `parent` corrupts the data. A 19-year-old legal guardian of a 12-year-old sibling is real |
| `right_level` | enum: `none` / `view` / `write` | **The whole of the guardian's authority** ([D-074](../decisions/round-06.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular)). Current value, denormalised for the read that happens on every authorization check; history in `guardianship_permission` (§2) |
| `valid_from` | date, required | |
| `valid_to` | date, optional | NULL = current. **Set by a person** — a party to the row (§1 "Guardianship ends"), or a staff member asked to record it. **Never by a job**: the system takes no position on majority ([D-069](../decisions/round-05.md#d-069--guardianship-ends-when-a-person-ends-it-the-system-takes-no-position-on-majority)) |
| `is_primary_contact` | boolean, required, default false | Who the organization calls in an emergency. **Independent of `right_level`** — a grandparent with no system access at all can still be the emergency contact. See [../domain/02-actors.md §6](../domain/02-actors.md#6-effective-contact-for-a-minor) |
| `is_legal_decision_maker` | boolean, required, default false | Distinguishes who may make legal decisions — consent for medical treatment, travel — from who provides day-to-day care. Often different people |
| `lives_with` | boolean, optional | Deliberately optional: *false* means guardianship without cohabitation (shared custody, a guardian in another city), which is a different fact from *unknown*. Relevant to contact routing, never to authority |
| `custody_arrangement` | free text | A description, not a computable fact, and kept that way on purpose (§7) |
| `source` | enum: `self` / `staff` / `import` / `court_order` | **Decides the starting `right_level`** (§2 defaults, [D-046](../decisions/round-02-03.md#d-046--guardianship-defaults-depend-on-how-the-guardianship-was-created)) |
| `verified_at` | timestamp, optional | |
| `verified_by` | reference to person, optional | |
| `evidence_reference` | free text | Where the proof of guardianship is filed. For legal guardianship this matters: the organization must be able to show that it checked |
| `ended_reason_code` | free text / reason code | |
| `ended_note` | free text | |
| `created_at`, `updated_at` | timestamps | |
| `created_by`, `updated_by` | reference to person | |
| `import_batch_id` | reference to import batch | Legacy rows only |

**Rules**

- A person may not be a guardian of themselves: the two person references must differ.
- `valid_to`, when present, must be after `valid_from`.
- **At most one *current* guardianship per (guardian, dependent) pair.** Their periods may not
  overlap. Past ones are unlimited and expected: a court order lapses and is renewed.
- A dependent may have **any number** of simultaneous guardians, each with its own row and its
  own `right_level`.
- `is_primary_contact` is not unique per dependent. A child can have two primary contacts.

**Indexes**

- Lookups in both directions by person and `valid_to` — "who is this person's guardian" and
  "who does this person guard" are equally common.
- A partial index on current rows only, and a second on current rows that are primary contacts:
  the emergency-contact lookup must not scan history.

### The relation is a general graph, not a two-level hierarchy

The requirements permit:

- **One guardian → many dependents.** Multiple rows with the same guardian. This is "one parent
  can manage multiple children".
- **Many guardians → one dependent.** Both parents, brothers' grandparents, a legal guardian
  plus a step-parent. Nothing assumes a child has exactly two guardians.
- **A person being both.** Person A is guardian of B and dependent of C. Costs nothing to allow,
  and avoids a rewrite when a member reaches majority and becomes guardian to a younger sibling.

You specified the first two explicitly. The third is free.

### Per-dependent authority

Authority is **per `guardianship` row**, never per person. A parent can hold `write` for one
child and `view` for another — a realistic shared-custody arrangement, and one the model must
represent without inventing a second parent identity.

What changed with [D-074](../decisions/round-06.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular)
is the *grain*, not the *location*. Per row it used to be a set of capability codes; per row it
is now one of three values. See §2 for what that costs.

### Guardianship ends — and who is allowed to end it

`valid_to` is set when:

- **a party to the row ends it.** The guardian, or the adult who is the subject of it
  ([D-073](../decisions/round-06.md#d-073--guardianship-is-administered-by-its-own-parties-not-by-staff));
- a court order changes the arrangement, which staff record;
- the guardian dies — and note the organization does not record death
  ([D-034](../decisions/round-02-03.md#d-034--the-person-record-holds-no-deceased-flag)), so this
  too arrives as a person ending a row, with whatever reason the organization uses.

Staff may always do it when asked. **Staff may never be the only way it happens.**

**The parties are principals, not third parties with a grant.** A guardianship row is not the
guardian's record, and it is not the subject's record. It is a record *of a relationship between
them*, and both hold it.

**This claim used to borrow its justification from a rule that no longer exists.** It was written as
*scope authority* — ~~the rule that authority over a nested thing originates at that thing~~
([D-031](../decisions/round-02-03.md#d-031--no-downward-inheritance-of-authority-scope_exposure-is-the-only-crossing)),
"applied to a household instead of a unit" — which was a good analogy right up until
[D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row) deleted
the nesting it was borrowed from, along with the crossing mechanism that made it a rule rather than a
sentiment. The claim does not need the borrowing. **A relationship row belongs to the people in it** is a
statement about this channel and stands on its own, and it is the reason neither party needs a grant to act
on the row. What the deleted rule was really doing on this page was answering *who may end it*, and that
answer is already given locally, a paragraph above: a party to the row, or staff acting on a request — with
staff never the only way it can happen.

**It is not the ownership channel, and the distinction is worth keeping.** Ownership is *your own
record*. Ending a guardianship over yourself is not editing your own record; it is dissolving a
relationship you are one half of. Mechanically this is the **guardianship channel gaining a
direction**: it already asks "may guardian G act on D's records?", and it now also answers "may a
party act on the guardianship row itself?", for exactly three acts — ending it, adding another
guardian, and changing the right level. The resolver still has four channels
([D-010](../decisions/round-01a.md#d-010--role-assignments-and-access-grants-share-a-scope-model-and-a-resolver), and the channels' dispatch changed in D-079).

**The three acts a party may take, and no others:**

| Act | Guardian | Subject (adult) | Staff |
|---|---|---|---|
| End the row | ✅ | ✅ | ✅ |
| Add another guardian over the same dependent | ✅ | ❌ | ✅ |
| Change `right_level` **downward** | ✅ | ✅ | ✅ |
| Change `right_level` **upward** | ✅ | ❌ | ✅ |
| Edit the dependent's records | per `right_level` | own record | per role |

**Read the last row against the first four, because an implementation will get this backwards.**
The four acts above are **not** gated by `right_level`: a guardian whose right is `view`, or even
`none`, may still end the guardianship, and a person who has never been a guardian at all may not.
The level ranks *what you may do to the child's records*, which is the fifth row and nothing else —
it is not a general competence over the relationship, and reading it as one would mean that
lowering someone's access to a medical file also locked them out of leaving the arrangement.
**The party direction follows the same rule as the record direction: it can only say yes**
([D-079](../decisions/round-06.md#d-079--the-guardianship-channel-is-entered-by-shape-not-by-permission-name)).
Being a party grants the act; not being one leaves the actor's own `guardianship.*` role
permissions to be tried, which is how staff in the table above get their ✅s. An explicit deny still
runs first and beats both.

**The asymmetry, stated plainly.** A guardian may appoint a guardian: anyone with authority over
a child can give a second person that same authority with no approval from the organization. The
ordinary case is a mother adding the father. The design does not prevent the non-ordinary case;
it **attributes** it instead — who added whom, when, from which account, is audited, and the other
party is notified. That is a deterrent and an evidence trail, not a wall. See
[E-6](../open-questions.md#e-6--a-guardian-may-appoint-a-guardian).

**The system does not notice birthdays in this connection.** No job, no review queue, no computed
candidate date ([D-069](../decisions/round-05.md#d-069--guardianship-ends-when-a-person-ends-it-the-system-takes-no-position-on-majority),
reversing D-024 and closing E-2).

**Why not, including why the gentler version was also refused.** The legal reasoning is unchanged
and still correct: in many jurisdictions a parent's authority over health and school records does
not end at 18, and in some it ends at a different age, so *any* computed date is a claim the
system cannot support. What D-069 adds is that a **review queue makes the same claim more
quietly**. A queue asserts *this arrangement is now suspect*, in every case, for every family,
including the ones where the adult child actively wants their parent to keep handling the
paperwork. Deferring a decision is not declining to make one, and the queue was a decision.

**D-069 refused, D-073 supplies.** Read as one decision in two halves: a legal relationship
between two people ends when one of those people says so, and the organization's job is to be
told rather than to permit it. Without D-073, D-069 was a refusal with no alternative; the exit
it assumed had no door.

**What is lost, precisely:** a *prompt*, not a *record*. `valid_from`/`valid_to` mean "who is
listed as my guardian, and since when?" is a query with a complete answer including the date each
ended. What replaces the prompt is the report in §6, run by a person on purpose.

### `is_primary_contact` vs `is_legal_decision_maker`

Two distinct questions that a single "is primary parent" flag conflates:

| Question | Column |
|----------|--------|
| Who do we phone at 2am when the child is injured at camp? | `is_primary_contact` |
| Who may sign the consent form for that treatment? | `is_legal_decision_maker` |

They are often different people, and conflating them means either the wrong person is called or
an invalid consent is accepted. Both are separate flags rather than one `is_primary`, because a
child can have two primary contacts and one decision maker.

---

## 2. The guardian's right: `none`, `view`, or `write`

**A guardian either cannot see the child's records, can see them, or can change them.** That is
the entire vocabulary
([D-074](../decisions/round-06.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular)).

**`guardianship_permission`** survives as the **history of that value**, not as a capability
list. One row per change, exactly one row open at a time, so "what was this guardian allowed to
see in March 2024?" stays answerable — the same current-value-plus-temporal-history shape that
`person` uses for names.

| Field | Kind | Notes |
|---|---|---|
| `guardianship_id` | reference to guardianship, required | **Scoped to the row, never to the (guardian, dependent) pair** |
| `right_level` | enum: `none` / `view` / `write`, required | The value being recorded |
| `valid_from` | date, required | |
| `valid_to` | date, optional | NULL = current. Ending this row without ending the guardianship *changes* the right; a new row starts it again |
| `changed_reason` | free text | e.g. `default for self-registered guardianship`, `court order 2026-03-14`, `guardian request` |
| `changed_by` | reference to person, optional | NULL when the default was applied by the application at creation |

**Rules**

- Exactly one row per `guardianship` may be open at a time.
- Every change is a row; the value on `guardianship.right_level` is always the open row's value.
  If the two disagree, the row is authoritative and the copy is wrong.
- **Scoping to the guardianship row and not to the person pair is deliberate** ([D-020](../decisions/round-01b.md#d-020--guardian-permissions-are-scoped-to-the-guardianship-row)):
  when a guardianship ends and a new one begins — a renewed court order, a lapse and
  re-establishment — the rights must not silently carry over. A new relationship is a new row and
  a new, deliberate level.

### Three values, two kinds, and no scale

**This section used to argue that the guardian rights were not a second authorization model by mapping
them onto the shared level ladder** — `none` → 0, `view` → 10, `write` → 20, so the resolver would never
need to know which ladder it was standing on. **The ladder is deleted**
([D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)),
so that argument is gone and the requirement underneath it is still met, by a different mechanism: the
level is compared against a column on the permission, **`permission.right_kind ∈ read | write`** —
**`none` covers nothing, `view` covers the codes marked `read`, `write` covers both.** There is nothing to
order and no rank to keep in step, because three values against two kinds is a lookup, not a scale. The
column exists for exactly this comparison and for no other customer in the system
([05-authorization.md §1](05-authorization.md#right_kind-a-column-with-exactly-one-customer)).

**What the ladder was really buying survives, and it never was the numbers.** A guardian was never a staff
member, and that was expressed by `write` landing on `contribute` rather than `manage`. It is now expressed
by the shape of the request: **the guardianship channel is entered only when the check is about somebody
other than the actor** ([D-079](../decisions/round-06.md#d-079--the-guardianship-channel-is-entered-by-shape-not-by-permission-name)),
so the widest guardian right in the system reaches the child's record and cannot reach a roster, a fee
schedule or another family — not because its rank was too low, but **because those checks are not about the
child and the channel is never asked**. Losing the ladder costs the comparison; the boundary moved into the
one place that was always enforcing it.

### What the collapse gives up, written down rather than discovered later

Before D-074, a guardianship carried a set of capability codes — `dependent.profile.view`,
`dependent.medical.view`, `dependent.consent.give`, `dependent.fee.pay`, and thirteen others,
with `dependent.admin` as a shorthand for all of them. **Every `dependent.*` code is deleted.**

The consequence is specific and should not be softened: **it is no longer expressible that this
guardian may register the child for events but may not read the medical record.** The case the old
model existed for — a court order restricting one parent's access to medical information while
their other access continues — cannot be represented. A grandmother who was granted roster
visibility and nothing else is now a `view` guardian, which means she can see the fee history and
the medical file too.

What still holds:

- `write` is not `manage`, and since [D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality) there is no `manage` to be short of: the ceiling on a guardian is the **channel**, which answers only for checks about this child. A guardian cannot do organization-wide things because those checks are not about the child, not because a rank was too low.
- Authority is per row, so a guardian of one child sees nothing of another's.
- The **organization-wide deny channel is untouched**: a `guardianship` row granting `write` can
  still be refused by a deny, because deny is absolute and scope-independent
  ([D-032](../decisions/round-02-03.md#d-032--deny-is-absolute-locality-orders-allows-only)). What
  was lost is a *narrow* deny — "not medical" — not the ability to say *no*.

**If the split turns out to matter in operation it is a new decision, not a permission to be
re-added quietly** ([E-7](../open-questions.md#e-7)).

### Defaults still depend on how the guardianship arose

[D-046](../decisions/round-02-03.md#d-046--guardianship-defaults-depend-on-how-the-guardianship-was-created)
survives, with one value where it used to have a set:

| `source` | Starting `right_level` | Why |
|---|---|---|
| `self` — a parent registering their own child | `write` | They created the record and are asserting the relationship. There is nobody better placed to hold authority over it |
| `staff`, `import` — recorded by someone else | `view`, chosen at creation and raisable | A person who did not assert the relationship is not handed authority by a default |
| `court_order` | `view`, and **raised only by the person who filed the order** | The document says what the authority is; the system should not guess above it |

**Applied by the code that creates the row, at creation — and this is the correct layer, not a
compromise.** A default depends on *why* the row is being created, which is a fact about the user's
intent that no database rule can inspect. What must not happen is the default being applied only by
a form: an import that omits it produces a `view` guardian where the person meant full rights, and
nothing objects. **And nothing in §6 catches this either**, which is worth being plain about: a
default that was never applied leaves no inconsistent row behind — only a quiet `view` where a
`write` was intended, indistinguishable from a deliberate restriction. **That gap is a consequence
of §2's collapse.** Before D-074 an omitted bundle of grants was visible as an empty set, and an
empty set is reportable where `view` is not. What closes it is not a report but the shape of the
write path: one place creates guardianships, it reads `source`, and it does not accept a
`right_level` from a caller who is not entitled to choose one. The `staff` and `court_order` paths
need a human choosing a value, and a default that fires before anybody is asked is not a default,
it is a decision made on someone's behalf — the same refusal D-069 and D-076 make elsewhere.

**Why `source` and `changed_reason` are both kept.** The same word — "guardian" — now means two
different starting scopes depending on paperwork, and the record has to say which was chosen and
why. A guardian with read-only access and a guardian with full access are indistinguishable in
the domain language and must not be in the data.

---

## 3. There is no `household` table

**Removed** ([D-057](../decisions/round-04.md#d-057--household-is-removed)). An address
is a `person_contact` row of type `postal`
([01-identity.md §6](01-identity.md#6-person_contact)), which already exists, already keeps
history (`valid_from` / `valid_to`), and already carries a `purpose` — `'billing'` for the
address an invoice goes to. A separate household table was duplicating it under a different
key, and the duplication had gone stale: its `postal_address` column was documented as
denormalised *from* the billing contact's postal contact, with nothing keeping the copy true.

### Shared address still grants no access

> **Living at the same address does not grant any permission over another person at that
> address.** A stepparent with no `guardianship` row has no access to the children's records.
> A grandparent at the address has no access. This is deliberate and it is a safeguarding
> property, not an oversight.

This was true when `household` existed ([D-019](../decisions/round-01b.md#d-019--household-membership-grants-no-access))
and it is true now, for a simple reason worth stating so nobody re-derives it: **the access
never came from the household tables.** All authority over a child's records comes from
`guardianship` (§1–2). Removing a table that granted nothing cannot grant anything.

### What replaced it

| Household feature | Now |
|---|---|
| Billing address | `person_contact` of type `postal` with purpose `billing` |
| "Which children lived at this address in 2003?" | A query over the temporal `person_contact` history ([domain/03 §4](../domain/03-identity-and-legacy.md#4-match-signals)) |
| One invoice for three siblings | The fee is flat and per person ([D-037](../decisions/round-02-03.md#d-037--exactly-one-membership-type-the-fee-is-flat-and-per-person)); there is no family price to invoice |
| `fee_obligation.household_id` | Column and its index removed ([07-finance.md §2](07-finance.md#2-minimal-provisional-shape)) |

**What was genuinely lost, recorded rather than glossed:** a household was a *group* with a
name and its own lifetime. Two people at one address are now related by a query, not by a row,
so there is nowhere to hang "the Novák family" as a first-class thing and no `valid_from` for
the grouping itself. Accepted, because nothing was using it — no code set
`fee_obligation.household_id`, and `household.name` had no consumer. If family-level
communication or a family discount is ever wanted, this is the decision to revisit, and the
shape to bring back is a group with a period, not a fake person.

### Why not a `family` person row

Some systems model a household as a fake person so that memberships and payments can
attach to it. Do not. It creates rows in `person` that are not people, which breaks
identity matching, produces nonsense in name searches, and — because it is a person — can
receive a membership, an account, and eventually permissions.

---

## 4. How the resolver uses these tables

The guardianship channel is step 4 of the resolver
([../domain/06-authorization-model.md](../domain/06-authorization-model.md#6-the-resolver)).

**How the channel is selected — a change D-074 forces, and it is an improvement.** It used to be
selected by the permission code's namespace: a code beginning `dependent.` routed here, and the
point of routing by prefix was that *no caller gets to choose which channel applies*, which is what
stops one authorization rule being implemented twice, once wrong. With no `dependent.*` codes there
is no prefix, so the channel is now selected by **a fact about the request: the person the action is
about is not the person performing it.** Nobody picks a channel; the shape of the call picks it. And
it catches what the prefix missed — a parent editing their child's address under a `person.*` code
previously did not route through guardianship at all, because the code's name said otherwise.

Asked about another person, it resolves in this **fixed order**, and it produces one of **two**
outcomes: **an allow, or no answer at all.** It never answers "no".

1. **Is there a current guardianship row** between this actor and this subject, at the date being
   asked about? **If not, this step is not the channel's business and says nothing** — the
   resolver continues to the actor's own roles and grants. Silence, not refusal
   ([D-079](../decisions/round-06.md#d-079--the-guardianship-channel-is-entered-by-shape-not-by-permission-name)).
2. **Is there an explicit deny** covering this check? Deny wins here as everywhere else, and
   independently of how broad the underlying grant is
   ([D-032](../decisions/round-02-03.md#d-032--deny-is-absolute-locality-orders-allows-only)) —
   but note that this deny is found by **channel 0 of the resolver, before this step runs**, so
   nothing in this list can override it. It is listed second only because it is the other reason a
   guardian with a sufficient `right_level` still gets nothing.
3. **Read the row's `right_level`** and rank it: `none` 0, `view` 10, `write` 20.
4. **Compare against what the action needs.** Reading a profile needs 10; editing a contact needs
   20. At or above the requirement → **allow**. Below it, or `none` → **no answer**, and the
   actor's own roles are tried.

**Why step 1 and step 4 fall through instead of refusing, when refusing is what this channel used
to do.** It used to be entered only by codes no role could hold, so its refusal was the whole
answer. Now it is entered by ordinary codes that a role may also carry, and finality produces an
absurd result the moment one person wears two hats: **the parent who is also the event registrar,
holding `view` over their own child, refused the right to mark attendance.** The relationship
should not be able to revoke a job. What is *not* given up: `none` still grants nothing (that is
what D-074 promised, not a power to block other bases), and an organization that genuinely must
stop a specific person touching a specific child's records uses **an explicit deny**, which runs
first, everywhere, at any scope. The prohibition survives; it simply lives in the channel D-032
built for it rather than in a capability level.

Two further properties:

- **An ended guardianship never opens this channel again.** For every question, forever, the row
  is not current, so step 1 does not fire and no guardian authority flows. What a *former* guardian
  may still do is what any other member may do — through their own assignment, on its own scope,
  with the guardianship row doing nothing at all. That distinction did not exist while the channel
  was the only road to a child's records, and it is the honest version now.
- **The date is a parameter of the question, not read from the clock.** So "could this parent have
  seen this record on the day they did it?" stays answerable, which is what auditing a past action
  requires. As-of must be threaded into every step above, including the deny lookup — a check that
  reads today's denies against a 2024 action invents history.

Asked about the **guardianship row itself** rather than through it, the same channel answers for a
party to it, and only for the three acts in §1's table. That branch is not a fifth channel; it is
this one, pointed the other way.

---

## 5. Acting on behalf — recording it

Every operation performed for a dependent must record both parties. This is not optional:
without it, the audit trail attributes the parent's actions to the child.

Every access-log row for an act-on-behalf carries, together:

| Field | Records |
|---|---|
| `actor_person_id` | the guardian who acted |
| `subject_person_id` | the child whose record was affected |
| `on_behalf` | true, explicitly — not inferred from the two ids differing |
| `authorization_channel` | `guardianship` |
| `guardianship_id` | **which row** authorized it |
| `result` | allowed or refused |

Concretely, when a parent registers their child for an event, the record must answer:

- **Who did it?** The parent.
- **For whom?** The child.
- **By what authority?** A specific `guardianship` row, and the `right_level` it held at the time.
- **Is that authority still valid?** Re-checkable from the row's dates.

A row that records only "the child registered" is not merely incomplete — it is **wrong**,
and it is the kind of wrong that matters when someone later asks whether a parent consented
to something.

---

## 6. Invariants to verify

These were executable queries. They are now requirements stated in prose, and nothing runs them
([D-072](../decisions/round-06.md#d-072--the-documentation-carries-no-sql-the-schema-is-the-orms-job)).

1. **Adults still listed under a guardian.** Every open guardianship whose subject is past
   majority by `person.birth_date`. **Expected in the ordinary case and not an error** — this is
   the periodic human review D-069 names as the entire control, and it exists precisely *because*
   no job acts on that date. **Run it deliberately, never nightly**: a report nobody reads is a
   queue, and the queue was withdrawn.
2. **Rights outliving the relationship.** A `guardianship_permission` history row still open while
   its guardianship has ended. This is the exact failure that scoping to the row was meant to
   prevent; worth verifying because an application bug or a hand-edit can still create it.
3. **A dependent with no primary contact.** A current guardianship set in which nobody is flagged
   as the emergency contact.
4. **A minor member or participant whom no guardian can see.** Two shapes, one report, because
   they are the same gap arriving by different routes: **no guardianship row at all**, and **a full
   set of guardians with every one of them at `right_level = none`**. Age comes from
   `person.birth_date` — there is no membership category to read it from, because membership is
   ageless ([D-038](../decisions/round-02-03.md#d-038--membership-is-ageless)). **This is a
   safeguarding gap, not a data-quality nit**: the organization holds a member it cannot contact in
   an emergency and cannot obtain consent from. It should alert, not log. This check is one of the
   reasons `guardianship` is a required part of the model rather than an optional convenience.

   **The second half was added by [D-082](../decisions/round-07-08.md#d-082--a-direct-message-to-a-minor-is-mirrored-to-the-minors-guardians),
   and it is not a hypothetical refinement.** A direct message to a minor is mirrored to the
   guardians at `view` or `write` — deliberately *not* to a guardian at `none`, because `none` means
   the organization already decided that party sees nothing about the child. Without this half of the
   check, a child whose guardians are all `none` would look, in every report, like a child with
   guardians, while in fact nobody outside the child receives a copy of anything sent to them. **A
   right level that silently removes the only safeguarding net is a right level nobody understands
   anymore**, and this report is what keeps `none` meaning what it says.
5. **A guardian younger than the dependent**, where both birth dates are known. Almost always a
   data-entry error, and detectable only when both dates survived the import.
6. **`guardianship.right_level` disagrees with its own open history row.** A new invariant created
   by D-074's current-value-plus-history shape. If it is ever non-empty, the copy is wrong and the
   row is right.

*Deleted with the model that needed it:* "a guardian permission outside the `dependent.*`
namespace" — there is no `dependent.*` namespace any more. "Households with no address" went with
[D-057](../decisions/round-04.md#d-057--household-is-removed); the nearest surviving signal is
a live billing purpose with no postal address behind it, which is a finance problem.

Note what changed when membership became ageless. Check 4 used to read
`membership_type.category = 'child'`; with one membership type
([D-037](../decisions/round-02-03.md#d-037--exactly-one-membership-type-the-fee-is-flat-and-per-person))
that column does not exist, and the question is now answered from `person.birth_date`. The signal
is arguably better than it was: "this person is under 18 today" rather than "this person's
membership row was categorised as a child when it was opened", which could be years out of date.

---

## 7. Open issues

- ~~Whether guardianship should auto-expire at majority, or always require review.~~
  **Neither** — the system takes no position on majority, and the review queue this file
  recommended was withdrawn with it (§1, [D-069](../decisions/round-05.md#d-069--guardianship-ends-when-a-person-ends-it-the-system-takes-no-position-on-majority)).
- ~~How does an adult end a guardianship over themselves?~~ **They end it, themselves, as a party
  to the row** — [D-073](../decisions/round-06.md#d-073--guardianship-is-administered-by-its-own-parties-not-by-staff).
- **New:** a guardian may appoint a guardian, with no approval from the organization. Attributed
  and notified, not prevented. [E-6](../open-questions.md#e-6--a-guardian-may-appoint-a-guardian).
- **New:** one right level cannot separate the medical record from the profile, which is the case
  the deleted capability codes existed for.
  [E-7](../open-questions.md#e-7).
- **Resolved: `household` is removed entirely** — answered "drop household entirely", now
  [D-057](../decisions/round-04.md#d-057--household-is-removed) (§3). Addresses live on
  `person_contact`.
- Whether a guardian may act for a dependent who is also a member in their own right — e.g.
  can a parent register their adult child for an event, if the child consents? Recommend an
  explicit consent-based delegation rather than a guardianship, since the legal basis
  differs. The *group* version of this is now answered by audiences
  ([D-042](../decisions/round-02-03.md#d-042--grants-may-target-audiences-not-only-individuals)).
- Whether `custody_arrangement` free text should be structured. Recommend not — custody
  orders vary too much to model, and a wrong model is worse than honest prose.
- **Confirm that the membership gate's guardianship carve-out is intended.** A lapsed parent keeps
  their `right_level` ([D-039](../decisions/round-02-03.md#d-039--member-permissions-require-a-current-paid-membership)),
  which means an unpaid parent and a paid one are indistinguishable inside that namespace. It is
  almost certainly right — guardianship comes from a legal relationship, not a membership — but it
  should be a stated choice, not a side effect of where the gate was placed.

**Resolved and no longer open**, kept visible so the reasoning survives: the default grant at
guardianship creation (now one level, chosen by `source` — D-046); whether fees are per person or
per household (per person, flat — D-037, which retired the load-bearing half of `household` and led
to its removal — D-057); and background checks (none are recorded — D-043).

All tracked in [../open-questions.md](../open-questions.md).
