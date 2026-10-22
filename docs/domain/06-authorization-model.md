# Authorization Model

The permission system end to end. This is the document to read if you read only one.

---

## 1. The four channels of authority

Every question of the form "may person P do X?" is answered by exactly one of four
mechanisms. They are separate tables because they have different lifetimes, different
granters, and different revocation semantics.

| # | Channel | Question it answers | Table | Grants authority over |
|---|---------|--------------------|-------|----------------------|
| 1 | **Role assignment** | What may this person do *in the organization*? | `role_assignment` | Everything within its scope |
| 2 | **Guardianship** | What may this person do *regarding this child*? | `guardianship.right_level` | One dependent |
| 3 | **Access grant** | What may this person, **or this set of people**, do *to this specific item*? | `access_grant` | One record (event, document, unit) |
| 4 | **Resource ownership** | Is this *their own* data? | (derived) | The row's owner |

Channel 4 is not a table. It is the rule that a person may always act on their own
profile, their own requests, their own memberships. It is resolved by comparing
`person_id` before any other channel is consulted.

> **What a channel reaches once one of them says yes.** Each of the four answers *whether*, never
> *how much of a person*: there is one read rule and one write rule over a person's record, and no
> narrower tier standing beside them, so a grant that reaches the record reaches all of it. What
> that consists of, and why there is no sensitive corner left inside it to withhold, is
> [08-person-data.md](08-person-data.md) — worth reading before proposing a fifth channel that
> reaches "only" one kind of fact.

**Why keep channels 1–3 apart rather than one unified grants table.** They differ in ways
that matter:

- Channel 2 has a **legal** character — guardianship is a fact about the world, often
  court-ordered, and the organization records what it was told rather than deciding it.
  **It does not expire by itself.** An earlier version of this bullet said it "expires when a
  child reaches majority", which is exactly the claim
  [D-069](../decisions/decision-log.md#d-069--guardianship-ends-when-a-person-ends-it-the-system-takes-no-position-on-majority)
  withdrew, together with the review queue that asserted it more quietly: a parent's authority
  over health and school records does not end at 18 in many jurisdictions, and in some it ends at
  a different age, so any date the system computed would be a claim it cannot support. A
  guardianship ends when a **party to it** says so (D-073), and nobody else — not a job, not a
  birthday. Channel 1 does not expire by itself either, for the same kind of reason: it is a fact
  about the world.
- Channel 3 is **per-record** and therefore high-volume and short-lived. Channel 1 is
  low-volume and long-lived. Mixing them makes both hard to reason about.
- Channel 3 may target **a person or an audience** ([D-042](../decisions/decision-log.md#d-042--grants-may-target-audiences-not-only-individuals)) —
  "everyone", "all members", "the leaders of this unit". Channels 1 and 2 never do:
  a role is held by a named person, and a guardianship is between two named people.

That said, `role_assignment` and `access_grant` **share a resolver and a scope model**, so
the check logic is written once. See §6.

**A fifth thing that looks like a channel but is not: the membership gate.** Whether a channel
applies at all can depend on whether the person is currently a paid-up member
([D-039](../decisions/decision-log.md#d-039--member-permissions-require-a-current-paid-membership)).
That is not a *source* of authority — it is a condition on channels 1 and 3, resolved inside
the same function. Channels 2 and 4 are exempt. See §6.1.

---

## 2. Scope authority — no downward inheritance

**This section states the rule that most shapes the permission system.**

> **Authority over a unit originates at that unit. It cannot be claimed from outside it.**
>
> A parent unit — **including the organization itself** — cannot decide permissions inside a
> sub-unit. The root does not reach down into a pack; a pack does not reach down into the
> groups under it. If a sub-unit wants a higher-level role to have authority over it, **the
> sub-unit must state so explicitly.** Nothing is inherited, nothing is assumed, and there is
> no configuration flag that enables inheritance.
>
> **The only exception is `system_admin`**, which is organization-wide by definition and by
> design not scoped to any unit.

**What the rule does *not* say, and this is the part that changed.** It does not say the root
cannot act on the root's own data. Memberships, the person registry and the fees belong to
the **root unit**, because that is where they live
([D-035](../decisions/decision-log.md#d-035--one-root-unit-all-sub-units-nest-arbitrarily-beneath-it)).
An organization-scoped `registrar` processing a membership is working at their own scope,
not reaching downward, and no exposure is involved. What a sub-unit owns is its **own**
records — its events, its rosters, its local leadership — and there the rule is absolute.

This is the inverse of the usual hierarchical RBAC model, and it is a deliberate
organizational stance rather than a technical preference. The reasoning below is worth
preserving, because the "simplification" of adding inheritance back will always look
attractive and would silently reverse the policy.

### 2.1 Why this rule exists

**It is a safeguarding property.** In a youth organization, the authority that matters most
is authority over *children's records*. The rule ensures that a person's access to a
sub-unit's participants is granted by that sub-unit — the people who know them, who recruited
the leader, and who can be held responsible for the grant. Someone at the root cannot grant
themselves access to a pack's children unilaterally. That is precisely the property a
safeguarding review wants to be able to confirm.

**It makes every grant attributable to a locus of accountability.** With inheritance, "who
gave this person access to this pack?" has the answer "someone at the root, three years ago,
and possibly by accident." Without it, the answer is always a specific unit and a specific
person, because the grant had to be written at that unit.

**It prevents silent blast-radius growth.** With downward inheritance, adding a subordinate
unit to the hierarchy silently expands the permissions of every role above it. A
restructure — which in this organization happens every few years — would quietly grant
people access to sub-units they have never heard of. Under this rule, restructuring changes
nothing about who can do what.

**It matches how the organization actually delegates.** Real delegation in volunteer
organizations runs *up*: a pack decides to let a more senior treasurer handle its finances,
and says so. It does not run down from a policy nobody at the pack ever agreed to.

**It survives restructuring completely, thanks to D-036.** Because a unit never changes
parent, no grant's meaning can shift under it. A reparent would move a unit in or out of
every ancestor's reach, silently re-scoping rows nobody edited — and that is now impossible
by construction, not merely discouraged.

### 2.2 What this means concretely

| Question | With inheritance (rejected) | Under this rule |
|---|---|---|
| The root's treasurer acts on a pack's finances | Automatic | Only if that pack exposed its scope — **but the pack's finances are not the pack's: fees live at the root** (D-035) |
| A new pack added under the root | Root roles automatically gain access | Nothing changes. Access is unchanged until the pack says otherwise. |
| The root's `registrar` edits a **person's** record | Automatic | **Yes, and legitimately** — the person registry is the root's own data |
| The root's `registrar` edits a **pack's event** | Automatic | Only if that pack exposed its scope to the `registrar` role |
| `system_admin` | — | **Full authority everywhere. The sole exception.** |

The rows that were uncomfortable are now two different rows, and that is the whole effect of
[D-035](../decisions/decision-log.md#d-035--one-root-unit-all-sub-units-nest-arbitrarily-beneath-it).
**Memberships, people, and fees belong to the root**, so an organization-scoped `registrar`
or `treasurer` acting on them is not reaching into anything — that is their own data at their
own scope. **Events, rosters and local leadership belong to the sub-unit**, and there the rule
bites exactly as before: the sub-unit must expose its scope, or the work goes through
`system_admin`. §2.4 discusses what remains.

### 2.3 `scope_exposure` — how up-delegation is recorded

Authority crosses a unit boundary downward through exactly one mechanism: an explicit row
created **at the subordinate unit's level**, granting a specific role assignment coverage
over that unit.

A row names the unit — `org_unit_id`, the unit granting coverage over **itself** — the
`role_assignment_id` whose authority is to be honoured there, the person who wrote it
(`exposed_by`, who must be authorized *at* that unit) and when (`exposed_at`), an
`exposure_reason`, and the period it holds for.

The full field list is in [../data-model/05-authorization.md](../data-model/05-authorization.md#5-scope_exposure--how-a-unit-delegates-upward).
The three properties that matter:

1. **The row is keyed on the unit being covered, and it is written at that unit.** The
   unit is the grantor. A parent cannot create it — see §2.5.
2. **It points at a specific role assignment**, not at a role. Exposing a unit's scope to
   "the treasurer role" would let any future treasurer inherit access without the unit
   knowing. Pointing at the assignment means the unit approves *a person in a role*, which
   is what a unit can actually reason about.
3. **It is temporal and revocable**, like every other grant. A unit can withdraw coverage
   without touching the parent's role assignment.

**There is no bulk tool** ([D-045](../decisions/decision-log.md#d-045--the-bulk-scope-exposure-tool-is-removed)).
An earlier version of this design included one — a person authorized at a parent unit would
select sub-units and the tool would write an exposure row for each, marked `bulk:`. It was
removed, for two reasons. It wrote rows a sub-unit had not authored, which is a real
weakening of the rule the section is about. And on inspection, the case it was actually built
for turned out to be a different problem: not "let the treasurer serve forty sub-units" but
**"tell everyone about this event"** — which is what **audiences**
([D-042](../decisions/decision-log.md#d-042--grants-may-target-audiences-not-only-individuals))
now express directly, without touching the exposure mechanism at all (§6.2).

What remains is the honest case. A sub-unit that wants the root's treasurer to keep its books
writes one exposure row naming that assignment: a deliberate, dated, revocable act, which is
exactly what the rule exists to produce. Forty of them is forty deliberate acts, and that is
not drudgery — it is the auditability.

### 2.4 The organization-wide role problem, and why it mostly dissolved

The rule used to create a real tension. D-035 largely removes it, and it is worth seeing why
rather than assuming the tension is still there:

> If the organization cannot reach down into units, how does a national registrar process
> memberships for a unit that has not exposed its scope?

**Because the registrar is not reaching into a unit.** Memberships are held **at the root
unit**, which *is* the organization ([D-035](../decisions/decision-log.md#d-035--one-root-unit-all-sub-units-nest-arbitrarily-beneath-it)).
The registrar processing a membership is working on the organization's own records, at the
scope they hold. No exposure is needed and none should be.

The same is true of the treasurer and the fee data, and of anyone maintaining the person
registry. The problem existed only while "the organization" and "the units holding the data"
were assumed to be different entities.

**What genuinely remains** is narrower: the root does **not** own a pack's events, rosters or
local leadership. So the question becomes:

> May the root *read* what happens in its sub-units, or must each sub-unit expose its scope?

**Answered: the sub-unit exposes its scope, and there is no other route**
([D-049](../decisions/decision-log.md#d-049--the-root-may-not-read-into-its-sub-units-scope_exposure-is-the-only-crossing)).
Every crossing is a written, attributed act by the unit that owns the data.

> **No reporting channel outside the permission model is built, and this was a deliberate
> refusal.** A push-upward aggregate channel was the answer most likely to preserve the rule
> while still answering "how many members in 2019?" — but it turns out not to be needed,
> because **the root already owns the memberships**. The question that motivated it is
> answered from the root's own table.

The split is worth stating plainly, because it is what makes the strict answer affordable:

| The root's own records — **no exposure needed** | A unit's own records — **exposure required** |
|---|---|
| How many members in 2019 | Who was in the 4th Pack in 1998 |
| Who is currently a member | Which events a pack ran |
| What fees are outstanding | Who leads a pack |
| Was this person a member on this date | A pack's roster and attendance |

Memberships and fees are held **at the root unit**, which *is* the organization
([D-035](../decisions/decision-log.md#d-035--one-root-unit-all-sub-units-nest-arbitrarily-beneath-it)).
A unit's internal life is the unit's.

**What must not happen** is a background process that quietly treats root-scoped roles as
universal because "otherwise the office can't do its job." That converts a deliberate policy
into an inconsistency, and the inconsistency is where access bugs live. The specific shape
this takes in this system is worth naming: **`registrar` holds `unit_participation.view` at
organization scope, and that does not let it read a single pack roster.** Scope is exact — the
role reads the root participation rows, which are the membership rows
([D-041](../decisions/decision-log.md#d-041--belonging-to-a-sub-unit-is-a-participation-record-not-a-membership)).
It looks like an oversight and is not
([appendix/permission-catalog.md §11](../appendix/permission-catalog.md#11-roles--proposed-seed-set)).

> **Note for the real organization:** if it turns out that the majority of sub-units are
> writing exposures to the same organization-wide roles, that is a signal the rule does not
> match how the organization works — and it should be revisited as a policy decision, recorded
> in [../decisions/decision-log.md](../decisions/decision-log.md), rather than worked around
> in code. The signal is legible precisely *because* there is no side channel that would hide
> it: every crossing is a row someone wrote.

### 2.5 Enforcing the direction of authority

The rule is only as good as its enforcement. Three layers:

**Layer 1 — the permission that gates exposure.** Creating a `scope_exposure` requires
`scope.expose`, held at **the unit being exposed**.

Note the scope: the unit being *covered*, not the actor's own unit. Someone holding
`scope.expose` at a parent unit cannot satisfy this for a sub-unit, because they hold nothing
at the sub-unit. That one detail of the wording is what makes the rule structural rather than
advisory.

**Layer 2 — a check that rejects exposures created from above**, defense in depth against
a bug or a write that bypasses the ordinary path. It runs before a row is written, once per row,
on both a new row and a change to an existing one, and it does this in this order:

1. Apply **the rule, with no exceptions**: the person writing the row must hold `scope.expose`
   **at the unit being covered**. Holding it at an ancestor, or at an unrelated unit, does not
   qualify.
2. Ask the *same question layer 1 asks*, rather than a weaker copy of it — that is the only
   reason this layer exists. See the two notes below.
3. There is **no bulk branch**. The tool that wrote rows on a unit's behalf was removed
   ([D-045](../decisions/decision-log.md#d-045--the-bulk-scope-exposure-tool-is-removed)) once
   audiences ([D-042](../decisions/decision-log.md#d-042--grants-may-target-audiences-not-only-individuals))
   covered the case it existed for.
4. If the answer is no, refuse the row and name both the person and the unit in the refusal —
   a rejection that does not say who and where is not diagnosable. Otherwise the row stands.

Two things about this check are deliberate:

- **It is now a single unconditional predicate.** It used to have a second branch
  permitting a `bulk:` prefixed row written by an ancestor — the design's one sanctioned
  exception. That branch is gone
  ([D-045](../decisions/decision-log.md#d-045--the-bulk-scope-exposure-tool-is-removed)),
  and its removal is what makes this function something a reviewer can hold in their head.
  **Every exposure row is written by the unit it covers**, with no marker to explain away.
- **It was layer 2, and layer 2 is now missing.** Until D-072 this check ran a second time
  inside the database, so that a migration, a data fix, or a future code path that bypassed the
  write path still could not invert the direction of authority. **The write-path permission check
  is now the only thing standing between a caller and an upside-down exposure** — it cannot be a
  constraint (the answer comes from the resolver), and there is no longer a second copy of it
  below the application. Two consequences, both load-bearing: it must run **inside the same
  transaction as the row**, so that "checked, then written" is not two moments in time; and
  layer 3 below stops being a backstop and becomes the only detector.

**Layer 3 — the nightly integrity check** in
[../data-model/05-authorization.md](../data-model/05-authorization.md#11-invariants-to-verify),
which reports (a) any exposure whose granting assignment sits at an **ancestor** of the
covered unit, and (b) any exposure whose actor does not hold `scope.expose` at the covered
unit. **Layer 3 is now the only detection**, not the second line of it — it catches what the
write-path check missed, inverted, or was bypassed by, and nothing else will. That makes it the
one invariant in the authorization model worth alerting on rather than reporting: an inverted
exposure is authority flowing in the direction the founding principle forbids, and it is invisible
in the UI, which will show the exposure as a legitimate row either way.

### 2.6 `system_admin` is the only exception

`system_admin` is deliberately outside this rule, and deliberately so in a way that is
visible rather than implicit:

- It is **organization-scoped and unscoped simultaneously** — it satisfies every check at
  every scope without needing an exposure row.
- **It contains every permission**, so concerns about individual unit permissions are
  largely moot for a system administrator.
- **Sub-permissions** (`system.permission.edit`, `report.*`, and similar) also resolve
  under `system_admin` wherever the check is made.

Two properties keep this exception from being the hole in the design:

1. **Its holders are alarmed on.** The integrity check that lists current `system_admin`
   holders should notify on every change — a new holder is either a planned act or an
   incident, and either way someone should know within the hour.
2. **It is not delegatable.** `role.is_delegatable = false` for `system_admin`, so it
   cannot be lent, which prevents it becoming the routine workaround.

> The exception is safe only because it is narrow, alarmed, and undelegatable. If
> `system_admin` becomes the mechanism by which routine organization-wide work is done, the
> rule in §2.1 has been defeated in practice even though it holds in the schema. Watch the
> access log for its use — see §9.

### 2.7 What this replaces

Two things previously stated in this document are **reversed by this section**:

| Previously | Now |
|---|---|
| "Authority inherits downward through the unit hierarchy" | It does not. `scope_exposure` only, and only upward-delegated. |
| The resolver expanded unit scope via `unit_ancestors()` | The resolver matches scope **exactly**, plus explicit exposures. No ancestor walk. |

`unit_ancestors()` remains in the schema and is still used for reporting and for the
exposure-direction check (§2.5) — but **never** for permission resolution. Anywhere it
appears in a permission path is a bug.

Both reversals are recorded in
[../decisions/decision-log.md](../decisions/decision-log.md), with the reasoning, so they
are not re-litigated.

---

## 3. Permissions — the atomic unit

A permission is a coded capability. It is the only thing the check function ever looks at.

A permission row carries its `code`, the `resource` and `action` it decomposes into, a
`description`, and `is_system` — set for the permissions the platform ships with, which therefore
cannot be deleted.

Codes are `resource.action` and are **stable identifiers**, never display strings. The UI
shows a human label; the code never changes. Renaming a permission code is a breaking
change and must be avoided.

### Naming convention

| Pattern | Meaning | Example |
|---------|---------|---------|
| `<resource>.view` | Read | `person.view` |
| `<resource>.create` | Create | `event.create` |
| `<resource>.<field>.edit` | Edit a field subset | `person.contact.edit` |
| `<resource>.delete` | Delete (soft, and audited) | `document.delete` |

There is no row here for acting on a supervised person, because there is no `dependent.*`
namespace to name ([D-074](../decisions/decision-log.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular)).
A guardian's act is checked under the ordinary code for the thing being touched — `person.view`,
`person.address.edit` — and reaches the guardianship channel by the shape of the request, not by
its name (§6, and [D-079](../decisions/decision-log.md#d-079--the-guardianship-channel-is-entered-by-shape-not-by-permission-name)).

**Every capability is narrow and explicit.** A check for `X.y` needs an exact grant of `X.y`,
or `system.admin`. There is no `<resource>.admin` wildcard and no prefix match in the resolver
([D-068](../decisions/decision-log.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle),
reversing the earlier convention) — which is what makes the next section load-bearing rather
than decorative: **if somebody can do everything about events, a role says so, in thirteen
rows, and you can read them.**

Do not confuse this with the `admin` **grant level** in §5, which is real and untouched: the
level says *how much* authority a grant carries, the deleted code said *which capabilities it
implied*.

---

## 4. Roles — bundles of permissions

A role is a named set of permissions, assigned to a person for a period, within a scope.

A role row is a `code`, a name, a description, `is_system`, and `scope_required` — whether an
assignment of this role has to name a scope. `role_permission` is a join entity and nothing
more: this role carries this permission.

An assignment joins a `person` to a `role` for a period — `valid_from`, `valid_to` — and records
who created it (`granted_by`, `granted_at`) and why (`grant_reason`). `delegation_of` is absent
on an ordinary assignment and set on one that was lent, naming what it came from (§9).

### Scope

`scope_type`/`scope_id` is what makes "treasurer of Pack 12" and "treasurer of the
organization" the same row shape. It also means adding a new scope kind later (an event
series, a committee) is a data change, not a schema change.

**Authority does not inherit downward. See §2.** A role at a parent unit does *not* cover
the sub-units beneath it unless each of those has explicitly exposed its scope to it — with
the single important nuance that the **membership registry and the fees belong to the root
unit**, so an organization-scoped role over them is not reaching downward at all.

### Seed roles (a starting shape, not a specification)

**Roles are data.** The organization creates them, composes them from permissions, assigns
them, edits what they grant and deletes the unused ones
([D-052](../decisions/decision-log.md#d-052--roles-are-runtime-data-the-seed-set-is-not-a-specification),
[D-053](../decisions/decision-log.md#d-053--a-role-is-valid-always-only-its-assignment-is-temporal)).
This means two things about the table below, and both are corrections to how this section
read before:

1. It is a **worked example** of composing permissions into permission groups, included so the
   model can be reviewed against something concrete. It is not a requirement list.
2. **The `Req.` and `Waives gate` columns are configuration, not specification.** They are
   attributes of roles, and an organization sets them in the admin UI. The values shown are
   reasoned defaults; only `system_admin` carrying `system.gate_exempt` is not a preference,
   because the 1 January lockout it prevents is a property of the system.

A person may hold **several roles at once** — a leader can hold a leadership role *and* a role
carrying administrative permissions; a counselor may hold a role carrying event creation and
`person.view`. A role is a bundle, and bundles compose.

The `Req.` column is `role.requires_membership` — whether the role stops working when the
holder's fee lapses ([D-039](../decisions/decision-log.md#d-039--member-permissions-require-a-current-paid-membership)).
It remains the blunt form of the gate's waiver; `system.gate_exempt` is the precise form.

| Role | Scope | Req. | Waives gate | Key permissions |
|------|-------|------|-------------|-----------------|
| `system_admin` | organization | — | **yes** | all, plus `system.*`. Holds `system.gate_exempt`: the 1 January sweep lapses every membership including this one, and the recovery path must work on the day it is needed. |
| `registrar` | organization | yes | no | `membership.request.*`, `person.*`, `unit_participation.view` (root rows — see the note below the table) |
| `treasurer` | organization or unit | yes | no | `fee.*`, `payment.*`, `report.finance.view` |
| `unit_leader` | org_unit | **no** | no | `event.*` for own unit, `unit_participation.view`, `unit_report.view` |
| `assistant_leader` | org_unit | **no** | no | subset of `unit_leader` |
| `unit_admin` | org_unit | yes | no | administrative management of a sub-unit and its children |
| `audience_admin` | organization or unit | yes | no | `audience.view`, `audience.manage` — who maintains the named groups |

**`Req.` and `Waives gate` are not alternatives.** `Req.` is `role.requires_membership` — "is
this role membership-dependent?". `Waives gate` is whether the role carries the person-level
`system.gate_exempt` permission — "does holding this role make *me* exempt everywhere?"
([D-051](../decisions/decision-log.md#d-051--the-membership-gate-is-waived-by-a-permission-not-only-by-a-role-flag)).
Which roles carry it beyond `system_admin` is open for your review — the mechanism is
settled, the list is data.

**Why the two leader roles are marked `no`.** They are held by adult volunteers, and the
organization's answer was *"everything except guardianship and adult volunteers"* — a
volunteer whose own fee is unpaid still runs the Thursday meeting, and losing the roster the
night the fee lapses is the failure mode this flag exists to prevent. Note the asymmetry with
`position.requires_membership`, which stays `true` for those same positions and puts the
volunteer on a chase-up report. **The report is how the organization notices; the resolver is
not how it punishes.** See
[data-model/02 §7.1](../data-model/02-organization.md#7-position-and-position_assignment).

**Why `registrar` and `treasurer` are marked `yes`.** Both are staff-like roles working on
the organization's own records at the root. A lapsed member should not be processing other
people's memberships or fees, and there is no operational reason for the exemption.

> **`registrar` reading `unit_participation.view` at organization scope does not let it read a
> pack roster** ([D-049](../decisions/decision-log.md#d-049--the-root-may-not-read-into-its-sub-units-scope_exposure-is-the-only-crossing)).
> Scope is an exact match, so the role reads the **root** participation rows — the ones that
> mirror membership. A sub-unit roster is a different scope and requires that sub-unit to
> expose it. This looks like a mistake and is not; widening the role to "fix" it would quietly
> reverse D-049.

> **Organization-scoped roles do not reach into sub-units.** A `registrar` assigned at
> organization scope has authority over organization-level records — which now includes the
> **membership registry and the fees**, because those live at the root
> ([D-035](../decisions/decision-log.md#d-035--one-root-unit-all-sub-units-nest-arbitrarily-beneath-it)).
> Authority over a *sub-unit's* own records — its events, its local rosters — requires **that
> sub-unit exposing its scope to the assignment** (§2.3). There is no other route, and
> `system_admin` is not one: it remains the stated emergency exception, alarmed and logged
> (§2.6), not a way to read a roster on a Tuesday. See §2.4.

### The role assignment period matters

`valid_from`/`valid_to` on `role_assignment` means authority ends on a date even if nobody
remembers to revoke it. **Every assignment of a role with real authority should have an
end date.** Leavers are the classic audit failure: the volunteer who stepped down in 2019
still has an active account with treasurer access in 2026. A default term (e.g. one
organizational year, renewed explicitly) turns that from an invisible risk into a visible
expiry report.

*Recommendation:* require `valid_to` on all roles flagged `scope_required = true`, and
produce a periodic report of assignments expiring in the next 60 days. Tracked in
[../open-questions.md](../open-questions.md).

---

## 5. Access grants — the per-item layer

This is the "per-item permission" you asked for, and you specified it means a **capability
on that item**: "person X may act on item Y". Not a statement of attendance, and not a
separate eligibility check — those are other tables.

A grant names its grantee, the item it is about, and how much. The grantee is a `person_id` or
an `audience_id`. The item is a `scope_type` — `event`, `document`, `org_unit`, `membership`, and
whatever is invented next — and a `scope_id` naming the concrete row. The `level` is one of the
five below, the period is `valid_from`/`valid_to`, and the provenance is `is_delegated` with
`delegated_from` naming the person whose authority a delegation came from, plus `granted_by`,
`granted_at` and `grant_reason`.

**`person_id` or `audience_id`, never both and never neither.** The audience form is what
makes "expose this event to everyone" expressible without writing a row per person
([D-042](../decisions/decision-log.md#d-042--grants-may-target-audiences-not-only-individuals)) —
see §6.2 for how it resolves.

### Levels

Ordered, cumulative — a higher level always subsumes the lower ones:

| Level | Numeric | Means |
|-------|---------|-------|
| `revoked` | 0 | Explicitly denied. **Overrides any other grant** — see §7. |
| `view` | 10 | Read the item |
| `contribute` | 20 | Read and add to it (sign up, comment, submit) |
| `manage` | 30 | Full control short of permissions administration |
| `admin` | 40 | Everything, including granting others access to this item |

`revoked` at 0 is important: without an explicit deny level there is no way to say "this
person must not see this event" when a broader grant would otherwise allow it.

### Why `scope_type`/`scope_id` and not one column per item type

`scope_id` has no foreign key — it is a polymorphic reference. This is a deliberate,
accepted trade-off:

- **Cost:** no referential integrity. A grant can point at a deleted event.
- **Benefit:** the permission system does not need a schema change every time a new
  grantable thing is invented, which — since you have deferred events, documents, and
  everything else — will happen repeatedly.

Mitigations, all of which are required:

1. A `scope_type` registry table validates `scope_type` values.
2. Deleting an item of a granted type must close its grants (an application-level
   obligation, tested).
3. A nightly consistency job reports orphaned grants.
4. `scope_id` is `BIGINT` and ids are never reused.

> If you would rather have strict referential integrity, the alternative is a
> `grantable_item` supertable that every grantable entity references. That is a heavier
> design; I have chosen polymorphism for flexibility, and flagged it here so you can
> overrule it. See [../open-questions.md](../open-questions.md).

---

## 6. The resolver

One function answers every authorization question. Written once, used everywhere — an
authorization rule that exists in two places will diverge.

The call is `can(person, permission_code, scope_type, scope_id, at)`. The scope pair is optional
and `at` defaults to now. Where the thing being touched has an owner, the caller passes
`owner_person_id` too, because two of the steps below need to know whose record this is. The
answer is allowed or denied; the function has no other output, and no part of it is stored.

These steps run **in this order, and the order is a rule**
([D-032](../decisions/decision-log.md#d-032--deny-is-absolute-locality-orders-allows-only)).
Each one either returns an answer or falls through, so no later step can contradict an earlier
one — and renumbering them silently changes who can do what.

0. **Deny — absolute, at any scope.** If **any** applicable grant for this person carries level
   `revoked` and covers this permission — at item scope, unit scope or organization scope, to this
   person or to an audience they are in — the answer is no. No scope outranks a deny: a per-event
   grant can never restore access that an organization-wide suspension removed (§7).

1. **Ownership.** If the target resource's owner is this person → true for `*.view`, `*.edit` and
   the self-service actions. **Exempt from the membership gate** (§6.1): a lapsed person must
   still be able to reach the screen they renew on.

2. **Guardianship — entered by the shape of the request, and it answers with allows only.**
   Compare the actor with the owner of the thing being touched. The same person, and this channel
   is not in play at all. Different people, and the question is whether the actor holds a **live
   guardianship over that subject as of `at`** whose right level is at least what the checked
   permission needs — `view` for a read, `write` for a change, and `none` for nothing
   ([D-074](../decisions/decision-log.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular)).
   A row at a sufficient level → **true**. Every other outcome — no row, `none`, a level too low —
   is **not a refusal**: the channel says nothing, and the resolver continues to step 3, where the
   actor's own grants and roles are tried exactly as they always were
   ([D-079](../decisions/decision-log.md#d-079--the-guardianship-channel-is-entered-by-shape-not-by-permission-name)).
   A parent who is also the event registrar holds `view` over their own child and must not be
   refused the roster by their own guardianship.

   - **Nothing escapes by naming.** The act that routes here is chosen by whose record it touches,
     so a permission written next year for a field a guardian must edit is covered the day the
     field exists. Under the rule this replaces, dispatch read the code's prefix — and an ordinary
     `person.address.edit` slipped past it.
   - **An ended guardianship never opens this channel again.** What a former guardian may still do
     is what any other member may do, through their own assignment.
   - **The row is the whole test.** The guard must not be rewritten as "the subject is a minor":
     the resolver contains no age branch, and [D-070](../decisions/decision-log.md#d-070--an-event-has-no-age-ceiling-the-grant-is-the-rule)
     and [D-077](../decisions/decision-log.md#d-077--messaging-is-direct-by-default-broadcast-is-an-ordinary-scoped-permission-and-the-recipient-chooses-the-channel)
     keep it that way.

   A genuine prohibition is still available and still absolute — it is step 0, which runs before
   anything and does not care about scope. This step is **exempt from the membership gate** (§6.1):
   guardianship is a legal relationship, not a membership. See
   [../data-model/04-relationships.md](../data-model/04-relationships.md#4-how-the-resolver-uses-these-tables).

3. **Allow — the most specific scope determines the level.** Evaluate from the most local scope
   outward. The **first** tier that yields a determination decides this permission's effective
   level for this check:

   - **a. Item grant** — an `access_grant` on this exact `(scope_type, scope_id)`.
   - **b. Unit grant** — an `access_grant` on this `org_unit`, matched **exactly**. An exposure
     never widens a direct grant: it names one person's role assignment, and a grant carries no
     assignment for it to attach to
     ([D-078](../decisions/decision-log.md#d-078--an-exposure-extends-an-assignment-never-a-direct-grant)).
   - **c. Org grant** — an `access_grant` with `scope_type = 'organization'`.
   - **d. Role** — a `role_assignment` at the most specific applicable scope: the exact unit, a
     unit that has written an exposure row naming **that assignment**, or the organization. This
     tier is the only consumer of `scope_exposure`, and the membership gate (§6.1) applies to
     tier **d** alone.

   If the deciding tier's level satisfies the permission's required level (per `permission_level`)
   → true. Otherwise fall through to the next tier.

4. **Otherwise → false.**

Points worth stressing:

- **Default deny.** Step 4. Any new resource starts with nobody able to touch it.
- **Deny is absolute and is the only thing that outranks locality.** A safeguarding
  suspension is not overridable by a more local grant — that is the entire reason
  `revoked` sits outside the tier ordering. See §7.
- **Locality decides between allows.** The most specific scope sets the level. This is
  what "local permissions override global" means: a per-event `manage` grant gives you
  `manage` **on that event** even if your only unit-level grant is `view`, and the
  unit-level `view` still applies to the unit's other events.
- **No ancestor walk, and no widening of grants.** Step 3b matches the checked unit and nothing
  else; an exposure enters at step 3d only, and only for the single assignment it names
  ([D-078](../decisions/decision-log.md#d-078--an-exposure-extends-an-assignment-never-a-direct-grant)).
  `unit_ancestors()` must not appear anywhere in this path. See §2.
- **A grant may name an audience instead of a person.** "Everyone", "all members", "the
  leaders of this unit" — the grantee is resolved by a rule, the level and scope are resolved
  exactly as for a personal grant. See §6.2.
- **Effective permissions are never stored.** They are computed per request. A stored
  permission snapshot *will* drift from the grants that produced it — the only question is
  how long before anyone notices.
- **Time is a parameter.** `at` defaults to now, but the resolver accepts a historical
  time. This enables "could this person have done this on that date?" — needed for auditing
  past actions, and free if built in from the start.

### 6.1 The membership gate

**A role grants nothing while its holder's membership has lapsed**
([D-039](../decisions/decision-log.md#d-039--member-permissions-require-a-current-paid-membership)).
This is a condition on tier d, not a source of authority — it is what makes the resolver's
answer *time-sensitive* rather than merely *scope-sensitive*.

Concretely — inside tier d, each candidate role assignment counts only if one of three things
holds: the role does not require membership, which is the carve-out for this **role**; the person
is a current member as of the date being checked, which is the gate; or the person holds
`system.gate_exempt`, which is the carve-out for this **person**. One of the three is enough, and
none of them is a source of authority — they say only whether the role's authority still applies.

| Channel | Gated? | Why |
|---|---|---|
| Ownership (step 1) | **No** | Otherwise a lapse locks a person out of the screen they renew on |
| Guardianship (step 2) | **No** | A legal relationship, not a membership |
| Item / unit / org grants (tiers a–c) | **No** | An explicit act by someone who chose to give this person access. Not inherited, not implied. |
| Roles (tier d) | **Yes**, unless the role or the person opts out | The role was granted *because* the person was a member; the justification has gone |

**Two ways to opt out, and they answer different questions**
([D-051](../decisions/decision-log.md#d-051--the-membership-gate-is-waived-by-a-permission-not-only-by-a-role-flag)):

| | `role.requires_membership = false` | `system.gate_exempt` (a permission) |
|---|---|---|
| Question | Is this **role** membership-dependent? | Is this **person** exempt? |
| Granularity | the role | the person |
| Effect | the role grants regardless of membership | **every** gated role that person holds is honoured |
| Example | a volunteer-facing role that would break the evening if it stopped working | the system administrator, who must not be locked out by the sweep they are expected to run |

**`system.gate_exempt` must not be evaluated through `can()`.** Doing so is circular — the
resolver would have to apply the gate in order to find out whether the gate applies — and a
lapsed holder would be denied the permission whose only purpose is to say that a lapse does
not matter. It is a plain read of `role_assignment`, and it is the one place the resolver
touches the role tables without consulting itself. Because it is a `system`-namespace
permission, it can never arrive through an `access_grant`: an item-level grant cannot lift the
gate, structurally.

**Why the gate reaches tier d and stops there.** The distinction is *how the authority
arose*. A role is granted to a member qua member — a leader's authority is a consequence of
belonging. An `access_grant` is a deliberate, per-item act: someone decided that this person
should see this event, and a lapsed fee does not undo that decision. Gating grants too would
make the per-item layer unusable for exactly the people it exists for — a contractor, a
photographer, a parent helper who was never a member at all.

**The cost, stated plainly.** This is a real coupling:

- **A lapse silently removes access.** The intent, but "why can't I see this?" now has a date
  for an answer rather than a person's decision.
- **Every membership transition must invalidate the cache**, and the yearly sweep does it for
  everyone at once. Build the cache for this from the start (§8).
- **`role.requires_membership` is now enforced**, not merely reported. Its meaning changed;
  see [data-model/05 §3](../data-model/05-authorization.md#3-role-and-role_permission).

### 6.2 Audience grants

A grant names a **person or an audience, never both**
([D-042](../decisions/decision-log.md#d-042--grants-may-target-audiences-not-only-individuals)):

| Kind | How it resolves | Example |
|---|---|---|
| Built-in | A rule the resolver evaluates against current state | `everyone`, `all_members`, `unit:<id>:participants`, `unit:<id>:leaders` |
| Named group | A stored membership list someone administers | "the summer camp kitchen crew" |

**Built-in audiences are rules, not lists**, and that is the whole point: a new pack member
automatically receives what the pack was granted, with no rows to maintain and no
stale-group problem. Named groups are the escape hatch, and they carry that problem
knowingly — nobody ever removes anyone from a group.

Audiences are evaluated **inside tiers a–c**, through the same `grant_satisfies()` predicate
personal grants use. They do not add a channel and they do not change the level or the scope
resolution; they change only how "is this grant addressed to me?" is answered.

### Permission → required level mapping

The mapping lives in `permission_level`, which pairs a permission with the level it needs, held
per `scope_type`.

Example: `event.view` requires level `view`; `event.edit` requires `contribute`;
`event.manage` requires `manage`; `event.grant_access` requires `admin`. This table is what
lets one `access_grant` level serve many different permission codes without a hardcoded
mapping in code.

---

## 7. Precedence

Two separate questions, answered by two separate rules. Conflating them is the mistake this
section exists to prevent.

### 7.1 Who decides — deny is absolute

```
1. Explicit deny  (level = 'revoked', at ANY scope)   ← WINS OVER EVERYTHING
2. Ownership     (it's your own row — gate-exempt)
3. Guardianship  (the act is about someone else — allows only, gate-exempt)
4. Allows        (see §7.2; the membership gate applies to the role tier only, §6.1)
5. Deny          (nothing matched)
```

**A deny is checked before locality and is never subject to it.** A `revoked` grant at
organization scope blocks access to a unit's event even if a per-event grant explicitly
allows it. There is no scope local enough to override a suspension.

**A deny is also never subject to the membership gate** — in either direction. A `revoked`
grant blocks someone who is not a member, which is obvious. What is worth stating: a
`revoked` grant *to an audience* blocks the members of that audience whether or not they are
current members, because the deny is evaluated against who the audience rule matches, not
against the gate. Suspensions are absolute; the gate is a condition on a *grant of authority*,
and there is no authority here to condition.

This answers the question directly: *when does a local allow lose?* Only when any deny
applies at any level. A safeguarding suspension, a court-ordered restriction, or an
emergency removal must not be defeatable by a grant someone created earlier and forgot
about — which is exactly what a "most specific always wins" rule would permit.

### 7.2 How the level is decided — locality

Among competing **allows**, the most specific scope determines the effective level:

```
1. Item grant    (access_grant on this exact item)              ← most specific
2. Unit grant    (access_grant on this exact unit — matched exactly.
                  An exposure never widens a grant)
3. Org grant     (access_grant, scope_type = 'organization')
4. Role          (role_assignment at the most specific applicable
                  scope, or at a unit that has exposed its scope to
                  that assignment)                              ← least specific
```

The first tier that yields a determination decides the level; if that level is insufficient
for the permission being checked, the next tier still applies. So a per-event `view` grant
does not *downgrade* you below a unit-level `manage` for other purposes — it decides the
level **for that event**, and the broader grants continue to govern everything else.

**Consequences worth being explicit about:**

- A unit leader whose role grants `event.manage` on their unit still gets `manage` on a new
  event — the item tier is empty, so the unit tier decides.
- A specific `view` grant on one document works even for someone with no organizational role
  at all — the case for an external contractor or a parent photographer.
- A per-event `manage` grant gives full control of that event even to someone whose unit
  role is only `view`. **This is the user's requirement — local overrides global — and it
  applies to allows.** It does not apply to a deny: a `revoked` row anywhere beats this
  `manage` grant (§7.1, D-032).
- Locality orders grants; it does **not** create authority. An item grant on a unit you have
  no relationship to is still a valid grant — but creating it required `access_grant.create`
  at that item with `admin` level (§5), which is where the authority to make it came from.
  Contrast §2: the right to *hand out* authority at a unit lives at that unit, but the
  right to *delegate a specific grant* comes from the level held on the item.

---

## 8. Caching and invalidation

Permission checks happen on every request. Compute cheaply, cache carefully.

**Cache key must include everything the answer depends on:**

```
(person_id, permission_code, scope_type, scope_id, at_bucket)
```

where `at_bucket` truncates the timestamp to a granularity shorter than the shortest grant
duration you allow. If grants can start/end at an arbitrary second, a time-bucketed cache
is unsafe — use now() and a short TTL instead.

**Invalidate on:**

- any write to `role_assignment`, `access_grant`, `guardianship_permission`,
  `role_permission`, `audience`, `audience_member`
- **every membership transition, including the yearly expiry sweep** — the gate in §6.1 means
  a lapse changes the resolver's answer for a whole person, so invalidate **by `person_id`,
  not by scope**. The sweep touches everyone at once, so this must be a bulk operation the
  cache is designed for, not one delete per person in a loop.
- **a merge** — this is the one that gets missed. Merging two people unions their
  permissions, so the survivor's cache must be cleared. See
  [03-identity-and-legacy.md](03-identity-and-legacy.md#5-the-merge-operation).
- a unit's parent changing — **retired**, because this can no longer happen
  ([D-036](../decisions/decision-log.md#d-036--units-cannot-be-reparented-a-unit-that-moves-is-a-new-unit)).
  It previously affected reporting and the exposure-direction check but **not** permission
  resolution (§2), so its removal costs nothing.
- a write to `scope_exposure` (a sub-unit exposing or withdrawing coverage over itself)

**A note on the gate and TTL.** Because access now changes on a *date* rather than on
someone's action, the cache TTL is a policy choice about how long a lapsed member keeps
access. The sweep invalidates immediately; the TTL governs the window for transitions that
are not the sweep. Keep the TTL short and measure.

**Alternative worth considering:** materialize `effective_permission` as a table refreshed
on write rather than cached per-request. Faster reads, but it is a denormalization and it
must be maintained transactionally — if a refresh fails silently you have an access bug
that nothing detects. If you take this path, add a verification job that recomputes and
compares. Recommendation: start with cache-only, add materialization only if measurement
demands it.

---

## 9. Delegation

A leader going on leave, a treasurer handing over during an audit — the common need to
lend authority temporarily.

A delegation is an ordinary `access_grant` with its provenance set: `is_delegated`, and
`delegated_from` naming the person whose authority is being lent, a `grant_reason` saying what
for, and a `valid_to`.

Rules:

- A delegation **always** has an end date. Enforce with a constraint.
- Delegation cannot exceed the delegator's own authority — validate at grant time that
  every permission being delegated is one the delegator currently holds, and re-check at
  use time, because the delegator may lose it mid-delegation.
- The provenance is recorded, so an audit can answer "who really had this authority on
  that date?" — it lists both the holder and the delegator.
- Delegation of `system_admin` should be prohibited outright.

---

## 10. Anti-patterns this design rejects

Stated explicitly, because each is a common and expensive mistake:

| Rejected | Why | Instead |
|----------|-----|---------|
| `person.is_admin` boolean | Cannot scope, cannot date, cannot audit, cannot delegate | `role_assignment` |
| Role on `person` (`person.role = 'leader'`) | One role per person, no scope, no history | `role_assignment`, many per person |
| Checking membership type in code (`if type == 'adult'`) | Rules change; the check is invisible and untestable | A permission, granted to a role. There is one membership type now, so this is doubly wrong |
| Deriving access from "is a member" without a role | Being a member is not a capability; it is a fact | The membership **gate** (§6.1) conditions roles — it never grants anything |
| A parent-unit actor writing a `scope_exposure` covering a sub-unit | A sub-unit's records are not the root's records. A sanctioned bulk shortcut did exist for this and was removed (D-045) | The sub-unit exposes its own scope, or an **audience** grant covers the "tell everyone" case (§6.2) |
| Role → permission mapping hardcoded in the app | Cannot be reviewed by the organization, cannot change without deployment | `role_permission` table |
| Deriving access from guardianship without a right | Authorization by identity is unauditable and unsafe | The explicit `right_level` on the `guardianship` row |
| Deleting a grant to revoke it | Loses the audit trail of what was revoked when | `valid_to` + `revoked_at` |
| Two authorization implementations | They diverge; the weaker one becomes the exploit | One resolver, §6 |
| Unit leader sees all member data by default | Fails safeguarding review | Scoped role permissions, resolved per operation |
| Downward inheritance of authority through the unit tree | A parent unit decides permissions over nested units; restructuring silently changes who can do what | `scope_exposure` rows written at the covered unit — §2 |
| "Most specific scope always wins", including against a deny | Makes a safeguarding suspension defeatable by a stale local grant | Deny is absolute; locality orders allows only — §7 |
| Treating an organization-scoped role as universal "so the registrar can work" | Converts a deliberate policy into an inconsistency; the inconsistency is where access bugs live | Exposure rows, or `system_admin` — §2.4 |

---

## 11. Open issues

- The complete permission catalog and the real role definitions — the starting set in §4 is
  a proposal awaiting your input. **In particular the `Req.` column**: which roles are marked
  `requires_membership = false` decides who keeps working when their fee lapses, and it needs
  a deliberate answer per role rather than a default (§4, §6.1).
- Whether role assignments must have end dates (§4). This matters more now — an open-ended
  role held by a lapsed member is a "dormant authority" case (§6.1).
- May the root **read** what happens in its sub-units, or must each sub-unit expose its scope?
  The organization-wide-role problem largely dissolved
  ([D-035](../decisions/decision-log.md#d-035--one-root-unit-all-sub-units-nest-arbitrarily-beneath-it)),
  because the root owns the registry and the fees; what remains is this narrower question
  (§2.4).
- Which built-in audiences are needed, and whether the parameterised ones are seeded or
  created on demand (§6.2).
- The cache TTL under the membership gate (§8) — a policy choice about how long a lapsed
  member keeps access.
- Whether the membership gate should also apply to **item grants**, or only to roles (§6.1).
  The design says roles only, on the grounds that a grant is an explicit act — but a unit
  that hands an event to an unpaid helper may not see it that way.

**Resolved and no longer open**, kept visible so the reasoning survives: whether any
permission is conditioned on membership being current (yes, with three carve-outs — D-039,
§6.1); polymorphic `scope_id` (confirmed — §5, F-2); and the bulk exposure tool (removed —
D-045, §2.5).

All tracked in [../open-questions.md](../open-questions.md).
