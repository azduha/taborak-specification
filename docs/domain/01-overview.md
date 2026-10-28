# Domain Overview

What the organization is, who interacts with the system, and how the core lifecycles
flow. Read [../glossary.md](../glossary.md) first — this document uses its terms
strictly.

---

## 1. The organization

A youth organization (Scout-like: uniformed groups, trained adult leadership, camps
and weekly meetings) with:

- **Child members** — youth participants, who join one another in **groups**.
- **Adult members** — counselors/leaders who run the programs, hold **offices**, and put people into
  groups.

*(These two are how the organization talks about people. They are **not** two kinds of membership: there
is one membership type and it is ageless, so the sentence "is this person a child?" is a question about
`person.birth_date` and today's date — see [§2](#2-actors) and
[D-038](../decisions/decision-log.md#d-038--membership-is-ageless). Nothing downstream keys off the
difference except guardianship, position eligibility, and the mirroring rule for messages.)*
- **Caretakers** — parents and legal guardians of child members. They may or may not
  be members themselves.
- **Non-member supporters** — people who interact with the organization (donors,
  volunteers, alumni) without holding a membership.

The organization has **been reorganized repeatedly over four decades**, and **this system models none of
it**: there is one unit, it is a scope rather than a row, and the internal structure that got reorganized
was deleted in round 10 ([D-097](../decisions/decision-log.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)).
What remains of "the inside of the organization" is **groups** — named sets of people with a lifetime —
in [04-organization-structure.md](04-organization-structure.md). The reorganizations are a fact the system
knows nothing about, and saying that here, on the first page, is the point: a reader who arrives expecting
a hierarchy should learn at once that the absence is a decision, not an omission, and what it cost is
written down in the entry that made it.

---

## 2. Actors

The system distinguishes actors by *what they can do*, not by *what they are*. The full
treatment is in [02-actors.md](02-actors.md); the summary:

| Actor | Has account? | Has membership? | Can do |
|-------|-------------|-----------------|--------|
| Anonymous visitor | no | no | see public info, submit a registration or a membership request |
| Registered person | yes | no | maintain own profile, submit/renew a request, view own history |
| Member | yes | yes | own profile, unit participation, event signups, own history — **the same actor whether or not `birth_date` makes them a minor today** |
| Caretaker | yes | maybe | view/act on their dependents — **only** as explicitly granted |
| Staff / registrar | yes | maybe | organization-wide administrative permissions |
| Historical record | no | **a bounded period, if the export states one** | nothing. Data only, never a login. |

**The two member rows this table used to carry — "Member (child)" and "Member (adult)" — were one row
wearing two hats.** There is one membership type ([D-037](../decisions/decision-log.md#d-037--exactly-one-membership-type-the-fee-is-flat-and-per-person))
and it is ageless ([D-038](../decisions/decision-log.md#d-038--membership-is-ageless)), so the difference
between them was always `person.birth_date` against today's date, which changes on its own and is a fact
about a person rather than a kind of account. What a minor genuinely cannot do on their own is a
guardianship question, not an actor type
([02-actors.md](02-actors.md)).

The last row matters twice, and its answer changed in round 9. Imported rows create `person` rows with
**no account**, and must never be blocked from import by a "users must have email addresses" rule. They
also create **`membership` rows now** — bounded ones, both ends dated, only for the periods the people
export states, `data_confidence = 'low'` and marked with the batch that wrote them
([D-092](../decisions/decision-log.md#d-092--the-corpus-is-people-and-events-and-it-names-no-units),
[D-093](../decisions/decision-log.md#d-093--the-one-off-import-may-create-memberships-both-ends-dated)).
**What the earlier answer got right and still binds**: it refused to make a membership out of an
attendance row, and that refusal survives as the rule that an imported period is never open-ended and
never inferred from presence
([D-090](../decisions/decision-log.md#d-090--the-legacy-corpus-is-thousands-of-roster-rows-with-numbers-and-no-money));
and no sub-unit row is ever imported, because neither export names a sub-unit, so "who was in Pack 12 in
1998?" has no system answer at go-live
([03-identity-and-legacy.md §7](03-identity-and-legacy.md#7-legacy-import-pipeline)).

---

## 3. The three lifecycles

Almost everything in the system is one of three multi-step processes. They are separate
because they succeed and fail independently: you can register without applying, apply
without being accepted, be accepted without paying, and pay without ever joining a unit.

### 3.1 Account lifecycle

```
                  ┌─────────────────────────────────────────────┐
                  │                                             │
 (none) ──register──> pending_verification ──verify──> active ──┴──> suspended
                                                            │              │
                                                            └──> closed <──┘
```

An account is about **authentication only**. It says "this person can log in". It says
nothing about membership. A person can hold a verified, active account for years and
never become a member — a parent who only ever manages their child is exactly this case.

**One gate the arrows do not draw:** an account may not reach `active` while an unresolved
`identity_hypothesis` names its person, which is what a sign-up that strong-matches someone who
already exists runs into ([D-089](../decisions/decision-log.md#d-089--one-live-account-a-colliding-sign-up-files-a-claim-and-creates-nothing)).
Verification is necessary and not sufficient; a human decision is the second condition, and because
that makes a stalled queue a person who cannot log in, the blocking hypothesis is age-checked and
alerts. One live account per person is the rule doing the underlying work
([02-actors.md §3](02-actors.md#3-account-state-machine)).

### 3.2 Membership lifecycle

```
 (none)
   │
   ├─ request submitted ──> under_review ──accept──> approved ──payment confirmed──> active member
   │                             │                                                    │
   │                             └──reject──> rejected                                 │
   │                                                                                   │
   │                                     ┌─────────────────────────────────────────────┤
   │                                     │                                             │
   │                                     ├──> lapsed (fee expired at the yearly date)  │
   │                                     ├──> terminated (cause, with reason)          │
   │                                     └──> suspended (temporary hold)               │
   │                                                                                   │
   │      ┌──────────────── renewal (no new application) ────────────────────────────┘
   │      │        inside the renewal window → the new period opens at the expiry date
   │      │        after it                  → the new period opens at the payment date
   │      ▼
   │   active member again
   │
   └──────────────────────── re-apply ─────────────────────────────────────────────────┘
```

Every transition creates or closes a row; nothing is overwritten. A person who was a
member 1990–2010 and again from 2024 has two `membership` rows and the gap is visible
as data, not inferred from a date.

**Note the shape of the lapse.** There is no `completed` state: it existed only for ageing
out, and membership is ageless ([D-038](../decisions/decision-log.md#d-038--membership-is-ageless)).
And **the lapse happens on a date, to everyone at once** — the yearly expiry — which is why
the renewal path matters more here than the word "grace" suggests
([D-040](../decisions/decision-log.md#d-040--the-fee-expires-yearly-a-date-tracked-renewal-window-replaces-a-grace-status)).

Detailed in [05-membership-lifecycle.md](05-membership-lifecycle.md).

### 3.3 Authorization lifecycle

```
 (none) ──grant──> active ──expire/revoke──> inactive
                     │
                     └──delegate──> delegated grant (with end date, provenance recorded)
```

Every grant has a start, an end, a granter, and a reason. Nothing is permanent by
default and nothing is revoked by deletion. Detailed in
[06-authorization-model.md](06-authorization-model.md).

---

## 4. The relationships between people

Four relationships, deliberately not merged — and **the two that used to be here are gone**, because
between them they described the hierarchy this system no longer has: *participation in a sub-unit* and
*position held in a sub-unit* ([D-041](../decisions/decision-log.md#d-041--belonging-to-a-sub-unit-is-a-participation-record-not-a-membership),
[D-097](../decisions/decision-log.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)).
Their replacements are the two same-shaped tables of round 10:

| Relationship | Direction | Example | Grants access? |
|--------------|-----------|---------|----------------|
| **Guardianship** | guardian → dependent | parent → child | **No** by itself — only the `right_level` (`none` / `view` / `write`) carried on the live `guardianship` row. Since D-074 that value is the whole authority; `guardianship_permission` keeps only its history. |
| **Membership** | member → the organization | anyone → the unit | No. |
| **Being in a group** | person → group | child → the Thursday group | **No** — a `person_group_member` row is a dated roster entry ([D-098](../decisions/decision-log.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority)). |
| **Holding an office** | person → role | adult → a leader | **No** — a `role_holder` row says who holds it, and an office confers nothing by being held ([D-100](../decisions/decision-log.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)). |

**Being a member and being in a group are two rows, not one** — the distinction D-041 drew between
membership and participation, which survives its subject ([D-098](../decisions/decision-log.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority)).
A person is a **member of the organization** and **on a group's roster**: different facts, different
lifetimes, different guards on who may change them, which is why someone who stops attending on Thursdays
is still a paid-up member, and someone who is paid up may turn up to nothing. The old sentence named a
pack on the right-hand side; the new one names a group, and the reason the distinction was worth two
tables all along is that the two rows are edited by different people for different reasons.

The recurring theme: **participation is not authority.** A person can be deeply involved
— a parent of three members, a 20-year veteran, a pack's founder — and still have no
administrative access. Access comes only from an explicit grant. This separation is what
makes the permission system auditable and what prevents the classic failure where a
relationship ends (custody changes, a leader steps down) but access silently persists.

### The counselor-who-is-also-a-parent case

You named this case explicitly. It is not special:

- One `person` row.
- One open `membership`, of the one membership type, `member` — the same shape as the child they lead
  ([D-037](../decisions/decision-log.md#d-037--exactly-one-membership-type-the-fee-is-flat-and-per-person)).
- One `role_holder` row: they hold the office `counselors`, over a dated period. The office itself is a
  `role` row ([D-100](../decisions/decision-log.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)).
- A `person_group_member` row or two, dated, for the companies they actually turn up to
  ([D-098](../decisions/decision-log.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority)).
- Two `guardianship` rows (to their own children), each carrying its own right.
- Whatever `access_grant` rows somebody wrote whose grantee names them — as `ROLE(counselors)`, or
  `MEMBERS * ROLE(counselors)` where the membership gate applies
  ([D-099](../decisions/decision-log.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality),
  [D-101](../decisions/decision-log.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree)).
- No row of its own for "is a counselor". That is the `role_holder` row above, and nothing more.

Note there is no `counselor` membership type. Being a counselor is an **office held for a period**, not a
kind of membership ([D-037](../decisions/decision-log.md#d-037--exactly-one-membership-type-the-fee-is-flat-and-per-person)),
and since [D-100](../decisions/decision-log.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)
not even a *position* — the word went, along with the table that stored it, because a position implied
authority and an office confers nothing until a grant names it. This person's membership is identical to
that of the child they lead, which is exactly the point.

Their grants reach **the unit's members**, which after
[D-097](../decisions/decision-log.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row) is the whole
organization rather than one pack: there is no smaller body to scope inside, so a unit-scope grant is the
broadest thing a person can hold, and the round says that plainly instead of pretending the pack is still
a fence. Their guardianship reaches **their own children**, through a different channel entirely — entered
by the shape of the request rather than by any permission they were given
([D-079](../decisions/decision-log.md#d-079--the-guardianship-channel-is-entered-by-shape-not-by-permission-name)),
and capped by the right that row records. Being a leader does *not* give them access to other people's
children's records, and now the reason is mechanical: there is no rule that could have implied it, so the
access exists only as rows, or not at all.

> This last point is a safety property, not a convenience. Child-protection rules generally require that a
> leader's access to minors' personal data be bounded by their function. Two things carry that boundary
> now, and it is worth naming which: **[D-100](../decisions/decision-log.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)
> deletes the implication** — an office, a roster, a membership and a guardianship each confer nothing by
> being what they are — **and [D-099](../decisions/decision-log.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)
> makes what remains readable** — one code, one scope, one effect per row, so *"what exactly does this
> person have over minors?"* is answered by reading rows rather than by evaluating a rank. What the round
> lost is stated in [the overview's own rule 5](../README.md#the-one-idea-this-whole-design-rests-on): it is
> no longer true that a leader's reach had to be written by the body that chose the leader. The boundary is
> enforceable and reportable; who is obliged to look at the report is a convention, not a guard.

---

## 5. Multiplicity, in both directions

You specified: *one parent can manage multiple children; multiple children can be managed
by the same parent.* The model generalizes both:

- One guardian → many dependents (many `guardianship` rows).
- Many guardians → one dependent (both parents, stepparents, legal guardians — the
  schema makes no assumption that a child has exactly two, or exactly one).
- A guardian's authority over each dependent is **per-dependent**, so a parent can hold
  full permissions for one child and only read access for another (a realistic custody
  arrangement).

The same person can also be a guardian *of* someone and a dependent of someone else — the
relation is a general graph, not a two-level hierarchy. This costs nothing to allow and
avoids a rewrite when a member turns 18 and becomes guardian to a sibling.

---

## 6. The four decades of history

This is the constraint that most shapes the schema, so it is worth stating plainly.

The system must answer, correctly and indefinitely:

- "Who was in Pack 12 on 1 June 1998?"
- "Was this person a member when they attended that camp in 2003?"
- "This person registered in 2026 claiming they were a member in the 90s — is that true?"
- "What was this unit called in 2001, and what is its successor unit today?"

Consequences, all of which the data model implements:

1. **Everything temporal is a period**, never a boolean or a single date.
2. **Nothing is hard-deleted**, except by three named acts, each of which is somebody's decision
   rather than a cleanup job. Merges leave tombstones and units that closed keep their rows. Against
   that: **erasing a person** redacts their values wherever they were copied, including in the audit
   payload, immediately and at any age; **payload reduction** empties an audit row's values 24 months
   after they were written and leaves the row standing, so the trail keeps answering *who changed this,
   when, and were they allowed to* indefinitely and stops answering *and to what*
   ([D-088](../decisions/decision-log.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short));
   and **reverting an import batch** removes the rows that batch created. Reduction is not redaction —
   one answers to a person and is absolute, the other answers to a calendar and is bounded — and the
   accounting skeleton (`membership`, fees, payments) is deliberately outside all three: it is kept
   indefinitely as the organization's own history. *Assumption:* that "forever" has a legal basis is
   exactly the thing this document cannot establish for itself; the claim is recorded as an assumption
   awaiting review, not as settled law.
3. **Names change.** Units get renamed and renumbered; people change names. Names live in
   child tables with validity periods, not as columns that get overwritten.
4. **Imported data is low-confidence.** A 1994 roster has names, dates, and on most rows a legacy
   member number — which keys the organization's paper, not a session, and is exactly what is missing
   from the records that most need matching. This bullet used to say "no reliable unique key", written
   before the corpus had been described. Import still therefore *proposes* identities and a human
   confirms them, and where a number is present the proposal is a lookup rather than a guess.
   See [03-identity-and-legacy.md](03-identity-and-legacy.md).

---

## 7. What this design deliberately does not decide yet

These are referenced by the schema but not designed, pending your specification:

*(Events came off this list: they were specified, in [07-events.md](07-events.md) and
[data-model/08-events.md](../data-model/08-events.md), along with the thirteen codes in the catalog.)*

- **Fees and payments** — a provisional shape exists in
  [../data-model/07-finance.md](../data-model/07-finance.md) because membership
  activation depends on it. Expect to rewrite it.
- **Notifications, documents, reporting, API/UI.** *(Health records went off this list in round 7 —
  there is no health module, because [D-083](../decisions/decision-log.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)
  found no category to build one around; the facts live in the personal-attribute layer,
  [domain/08](08-person-data.md).)*

---

## 8. Next

- Terminology → [../glossary.md](../glossary.md)
- Accounts and registration → [02-actors.md](02-actors.md)
- Historical data → [03-identity-and-legacy.md](03-identity-and-legacy.md)
- Units → [04-organization-structure.md](04-organization-structure.md)
- Membership → [05-membership-lifecycle.md](05-membership-lifecycle.md)
- Permissions → [06-authorization-model.md](06-authorization-model.md)
