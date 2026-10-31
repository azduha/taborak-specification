# Domain Overview

What the organization is, who interacts with the system, and how the core lifecycles flow.
Read [../glossary.md](../glossary.md) first — this document uses its terms strictly.

---

## 1. The organization

A youth organization (Scout-like: uniformed groups, trained adult leadership, camps and weekly
meetings) with:

- **Child members** — youth participants, who join one another in **groups**.
- **Adult members** — counselors and leaders who run the programs, hold **offices**, and put people
  into groups.
- **Caretakers** — parents and legal guardians of child members. They may or may not be members
  themselves.
- **Non-member supporters** — people who interact with the organization (donors, volunteers, alumni)
  without holding a membership.

"Child" and "adult" are how the organization talks about people. They are **not** two kinds of
membership: there is one membership type and it is ageless, so *"is this person a child?"* is a
question about `person.birth_date` and the date being asked about (§2). Only three things downstream
key off the difference: guardianship, eligibility an organizer writes for one event, and the
mirroring rule for messages.

**The system models no internal structure of the organization.** There is one unit, it is a **scope**
rather than a row, and the nested bodies the organization has been reorganized into over four
decades are not stored, not versioned and not imported — an absence decided on purpose, whose cost is
written down in [D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row).
What remains of "the inside of the organization" is **groups**: named sets of people with a lifetime,
in [04-organization-structure.md](04-organization-structure.md). A reader arriving expecting a
hierarchy should learn that here, on the first page, because the absence changes every later answer
about scope.

---

## 2. Actors

The system distinguishes actors by *what they can do*, not by *what they are*. The full treatment is
in [02-actors.md](02-actors.md); the summary:

| Actor | Has account? | Has membership? | Can do |
|-------|-------------|-----------------|--------|
| Anonymous visitor | no | no | see public info, submit a registration or a membership request |
| Registered person | yes | no | maintain own profile, submit/renew a request, view own history |
| Member | yes | yes | own profile, event signups, own history |
| Caretaker | yes | maybe | view and act on their dependents — **only** as the guardianship row allows |
| Staff / registrar | yes | maybe | organization-wide administrative permissions |
| Historical record | no | **a bounded period, if the export states one** | nothing. Data only, never a login. |

**A minor is not an actor row.** One row above is a member, and whether that member is a minor today
is `person.birth_date` against the date of the check — a fact about a person that changes on its own,
never a kind of account. What a minor genuinely cannot do alone is a guardianship question
([02-actors.md](02-actors.md)).

Imported rows create `person` rows with **no account**, and import must never be blocked by a "users
must have email addresses" rule. They also create **`membership` rows**: bounded ones, both ends
dated, only for the periods the people export states, `data_confidence = 'low'`, marked with the
batch that wrote them
([D-093](../decisions/round-09.md#d-093--the-one-off-import-may-create-memberships-both-ends-dated)).
An imported period is never open-ended and never inferred from presence — an open membership
satisfies `is_current_member()`, so inferring one would make every 1998 attendee a current member
today. No sub-unit row is ever imported, because neither export names a sub-unit
([03-identity-and-legacy.md §7](03-identity-and-legacy.md#7-legacy-import-pipeline)).

---

## 3. The three lifecycles

Almost everything in the system is one of three multi-step processes. They are separate because they
succeed and fail independently: you can register without applying, apply without being accepted, be
accepted without paying, and pay without ever joining a group.

### 3.1 Account lifecycle

```
                  ┌─────────────────────────────────────────────┐
                  │                                             │
 (none) ──register──> pending_verification ──verify──> active ──┴──> suspended
                                                            │              │
                                                            └──> closed <──┘
```

An account is about **authentication only**. It says "this person can log in". It says nothing about
membership. A person can hold a verified, active account for years and never become a member — a
parent who only ever manages their child is exactly this case.

**One gate the arrows do not draw:** an account may not reach `active` while an unresolved
`identity_hypothesis` names its person, which is what a sign-up that strong-matches someone who
already exists runs into
([D-089](../decisions/round-07-08.md#d-089--one-live-account-a-colliding-sign-up-files-a-claim-and-creates-nothing)).
Verification is necessary and not sufficient; a human decision is the second condition. Because that
makes a stalled queue a person who cannot log in, a hypothesis that blocks activation is age-checked
and alerts. One live account per person is the rule doing the underlying work
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
   │                                     ├──> lapsed (fee expired at the yearly date)   │
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

Every transition creates or closes a row; nothing is overwritten. A person who was a member
1990–2010 and again from 2024 has two `membership` rows, and the gap is visible as data rather than
inferred from a date.

Two properties of the lapse are worth naming before the detail. **There is no `completed` status:**
nothing ages out of a membership, so there is no state for having finished one. And **the lapse
happens to everyone at once, on a fixed date** — the yearly expiry — which is why the renewal path
matters more than the word "grace" suggests
([D-040](../decisions/round-02-03.md#d-040--the-fee-expires-yearly-a-date-tracked-renewal-window-replaces-a-grace-status)).

Detailed in [05-membership-lifecycle.md](05-membership-lifecycle.md).

### 3.3 Authorization lifecycle

```
 (none) ──grant──> active ──end date reached / period closed──> inactive
                     │
                     └──delegate──> delegated grant (with end date, provenance recorded)
```

Every grant has a start, an end, a granter, and a reason. Nothing is permanent by default and
nothing is revoked by deletion — closing a period is the act, and the row stays. Detailed in
[06-authorization-model.md](06-authorization-model.md).

---

## 4. The relationships between people

Four relationships, deliberately not merged:

| Relationship | Direction | Example | Grants access? |
|--------------|-----------|---------|----------------|
| **Guardianship** | guardian → dependent | parent → child | **No** by itself — only the `right_level` (`none` / `view` / `write`) carried on the live `guardianship` row is authority, and that row is the whole of it ([D-074](../decisions/round-06.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular)). |
| **Membership** | member → the organization | anyone → the unit | No. |
| **Being in a group** | person → group | child → the Thursday group | **No** — a `person_group_member` row is a dated roster entry. |
| **Holding an office** | person → role | adult → *counselors* | **No** — a `role_holder` row says who holds it, and an office confers nothing by being held. |

**Being a member and being in a group are two rows, not one.** A person is a *member of the
organization* and *on a group's roster*: different facts, different lifetimes, and different guards on
who may change them — which is why someone who stops attending on Thursdays is still a paid-up member,
and someone who is paid up may turn up to nothing. The two rows are edited by different people for
different reasons, which is the whole case for keeping them apart.

The recurring theme: **participation is not authority.** A person can be deeply involved — a parent of
three members, a twenty-year veteran, the founder of a group — and still have no administrative
access. Access comes only from an explicit grant. This separation is what makes the permission system
auditable, and what prevents the classic failure where a relationship ends (custody changes, a leader
steps down) and access silently persists.

### The counselor who is also a parent

This case is not special:

- One `person` row.
- One open `membership`, of the one membership type, `member` — the same shape as the child they lead.
- One `role_holder` row: they hold the office `counselors` over a dated period.
- A `person_group_member` row or two, dated, for the groups they actually turn up to.
- Two `guardianship` rows (to their own children), each carrying its own right level.
- Whatever `access_grant` rows somebody wrote whose grantee names them — as `ROLE(counselors)`, or
  `MEMBERS * ROLE(counselors)` where membership is required of the holder.
- No row of its own for "is a counselor". The `role_holder` row is all of it.

There is no `counselor` membership type, and being a counselor is an **office held for a period** —
not a kind of membership, and not a grade of person. Nor is it a shipped office: **no role ships**, so the
`counselors` role of this example is one the organization wrote, and day one is one account holding
`system.admin`
([D-150](../decisions/round-21.md#d-150--day-one-is-one-account-holding-systemadmin-and-nothing-else-is-shipped),
[D-154](../decisions/round-21.md#d-154--counselors-is-an-example-now-not-a-shipped-office)). This person's membership is identical to that of
the child they lead, which is exactly the point.

Their grants reach **the unit's members**, which is the whole organization: there is no smaller body
to scope inside, so a unit-scope grant is the broadest thing a person can hold. Their guardianship
reaches **their own children** through a different channel entirely — entered by the *shape* of the
request (subject ≠ actor) rather than by any permission they were given
([D-079](../decisions/round-06.md#d-079--the-guardianship-channel-is-entered-by-shape-not-by-permission-name)),
and capped by the right level that row records. Being a leader does not give them access to other
people's children's records, and the reason is mechanical: **no rule could imply it**, so the access
exists as rows or not at all.

> That is a safety property, not a convenience. Child-protection practice requires that a leader's
> access to minors' personal data be bounded by their function, and two properties carry it here: an
> office, a roster, a membership and a guardianship each **confer nothing by being what they are**
> ([D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)),
> and a grant is **one code, one scope, one effect per row**
> ([D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)),
> so *"what exactly does this person have over minors?"* is answered by reading rows rather than by
> evaluating a rank. What the design does not do is guarantee that the reach was written by the body
> it governs — see [rule 5 in the overview](../README.md#the-one-idea-this-whole-design-rests-on).
> The boundary is enforceable and reportable; who is obliged to read the report is a convention, not
> a guard.

---

## 5. Multiplicity, in both directions

Specified directly: *one parent can manage multiple children; multiple children can be managed by the
same parent.* The model generalizes both:

- One guardian → many dependents (many `guardianship` rows).
- Many guardians → one dependent (both parents, stepparents, legal guardians — no assumption that a
  child has exactly two, or exactly one).
- A guardian's authority is **per-dependent**, so a parent can hold write for one child and view only
  for another — a realistic custody arrangement.

The same person can be a guardian *of* someone and a dependent *of* someone else: the relation is a
general graph, not a two-level hierarchy. This costs nothing to allow and avoids a rewrite when a
member's sibling needs a guardian and the member is the one who has them.

---

## 6. The four decades of history

This is the constraint that most shapes the schema.

The system must answer, correctly and indefinitely:

- "Was this person a member when they attended that camp in 2003?"
- "This person registered in 2026 claiming they were a member in the 90s — is that true?"
- "Who was on this group's roster on 1 June 1998?" — if somebody recorded the roster; the import
  supplies no group history.

It must not answer, and does not try to:

- "Who was in Pack 12 on 1 June 1998?" and "what was that unit called in 2001, and what is its
  successor today?" There are no units, no nesting and no successor relations to traverse.

Consequences, which the data model implements:

1. **Everything temporal is a period**, never a boolean or a single date.
2. **Nothing is hard-deleted**, except by three named acts, each somebody's decision rather than a
   cleanup job. **Erasing a person** redacts their values wherever they were copied, including in the
   audit payload, immediately and at any age. **Payload reduction** empties an audit row's values 24
   months after they were written and leaves the row standing, so the trail keeps answering *who
   changed this, when, and were they allowed to* and stops answering *and to what*
   ([D-088](../decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)).
   **Reverting an import batch** removes the rows that batch created. Reduction is not redaction: one
   answers to a person and is absolute, the other answers to a calendar and is bounded. The accounting
   skeleton — `membership`, fees, payments — is deliberately outside all three and kept indefinitely
   as the organization's own history. *Assumption:* that this "forever" has a legal basis is exactly
   what this document cannot establish for itself; the claim is recorded as an assumption awaiting
   review, not as settled law.
3. **People's names change**, so a name is a child-table row with a validity period and never a
   column that gets overwritten. A **group's** name is a column, and nothing replaces the deleted
   name-history table: a rename edits it and the old name is gone. What survives a rename is the
   identity beneath it, because grants and expressions store a kind and an id, never a name.
4. **Imported data is low-confidence.** The people export carries a name, a birth date, and the
   period each person was a member of the organization. Where an export also carries the
   organization's **legacy member number** — the number its paper records are keyed on — that number
   is imported verbatim into `person_identifier` under the legacy scheme, is never reissued, and makes
   a match **exact rather than probable**: same number, same person. Every other identity claim the
   import makes is a *proposal* a human confirms. See
   [03-identity-and-legacy.md](03-identity-and-legacy.md).

---

## 7. What this design does not decide yet

Referenced by the schema but not designed, pending your specification:

- **Fees and payments** — a provisional shape exists in
  [../data-model/07-finance.md](../data-model/07-finance.md) because membership activation depends on
  it. Expect to rewrite it.
- **Communication** — its shape is decided (direct by default, `broadcast` an ordinary scoped
  permission, the recipient chooses the channel, a minor's guardians get a mirror of a direct
  message), and its codes are in the catalog. There is no `message` or `message_recipient` table yet,
  and no design for templates, opt-out granularity, retention or moderation.
- **Notifications** — the renewal window made them dated rather than status-driven, which is a design
  note, not a design.
- **Documents, reporting, API and UI.**

---

## 8. Next

- Terminology → [../glossary.md](../glossary.md)
- Accounts and registration → [02-actors.md](02-actors.md)
- Historical data → [03-identity-and-legacy.md](03-identity-and-legacy.md)
- What the system knows about a person → [08-person-data.md](08-person-data.md)
- Groups, offices and the unit → [04-organization-structure.md](04-organization-structure.md)
- Membership → [05-membership-lifecycle.md](05-membership-lifecycle.md)
- Permissions → [06-authorization-model.md](06-authorization-model.md)
- Events → [07-events.md](07-events.md)

---

*Decisions behind this page: D-037, D-038, D-040, D-041, D-074, D-079, D-088, D-089, D-093, D-097,
D-098, D-099, D-100, D-114.*
