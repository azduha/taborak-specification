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
| 2 | **Guardianship permission** | What may this person do *regarding this child*? | `guardianship_permission` | One dependent |
| 3 | **Access grant** | What may this person, **or this set of people**, do *to this specific item*? | `access_grant` | One record (event, document, unit) |
| 4 | **Resource ownership** | Is this *their own* data? | (derived) | The row's owner |

Channel 4 is not a table. It is the rule that a person may always act on their own
profile, their own requests, their own memberships. It is resolved by comparing
`person_id` before any other channel is consulted.

**Why keep channels 1–3 apart rather than one unified grants table.** They differ in ways
that matter:

- Channel 2 has a **legal** character — guardianship is a fact about the world, often
  court-ordered, that expires when a child reaches majority. Channel 1 does not.
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

```
scope_exposure(
    id,
    org_unit_id,          -- the unit granting coverage over ITSELF
    role_assignment_id,   -- the parent- or organization-scoped assignment being honoured
    exposed_by,           -- a person authorized AT org_unit_id
    exposed_at,
    exposure_reason,
    valid_from, valid_to
)
```

The full DDL is in [../data-model/05-authorization.md](../data-model/05-authorization.md#5-scope_exposure--how-a-unit-delegates-upward).
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

Three honest answers, in order of preference:

1. **The sub-unit exposes its scope.** The normal path, and the rule holds absolutely. For an
   ongoing working relationship, the exposure row makes it visible and revocable — which is
   the point.
2. **A read-only reporting channel, deliberately outside the permission model.** Aggregate
   counts and rosters pushed upward by each unit, carrying no item-level authority. This lets
   the organization report nationally without letting it act locally — and it is the answer
   most likely to preserve the rule while still answering "how many members in 2019?".
3. **`system_admin`.** The stated exception; alarmed and logged. The escape hatch, not the
   routine path.

**What must not happen** is a background process that quietly treats root-scoped roles as
universal because "otherwise the office can't do its job." That converts a deliberate policy
into an inconsistency, and the inconsistency is where access bugs live.

> **Note for the real organization:** if it turns out that the majority of sub-units expose
> their scope to the same organization-wide roles, that is a signal the rule does not match
> how the organization works — and it should be revisited as a policy decision, recorded in
> [../decisions/decision-log.md](../decisions/decision-log.md), rather than worked around in
> code. Tracked as C-1 in [../open-questions.md](../open-questions.md#c-1--may-the-root-see-what-happens-in-its-sub-units).

### 2.5 Enforcing the direction of authority

The rule is only as good as its enforcement. Three layers:

**Layer 1 — the permission that gates exposure.** Creating a `scope_exposure` requires
`scope.expose`, held at **the unit being exposed**:

```
can(actor, 'scope.expose', 'org_unit', <the unit being covered>)
```

Note the scope: the unit being *covered*, not the actor's own unit. Someone holding
`scope.expose` at a parent unit cannot satisfy this for a sub-unit, because they hold nothing
at the sub-unit. This one line is what makes the rule structural rather than advisory.

**Layer 2 — a trigger that rejects exposures created from above.** Defense in depth against
a bug or a direct SQL fix:

```sql
CREATE OR REPLACE FUNCTION check_exposure_direction() RETURNS TRIGGER
LANGUAGE plpgsql STABLE AS $$
BEGIN
    -- THE RULE, with no exceptions: the actor must hold scope.expose AT THE UNIT
    -- BEING COVERED. Holding it at an ancestor, or at an unrelated unit, does not
    -- qualify. This is the same predicate layer 1 applies, re-checked here so that
    -- a direct INSERT cannot skip it.
    --
    -- There is no bulk branch. The tool that wrote rows on a unit's behalf was
    -- removed (D-045) once audiences (D-042) covered the case it existed for.
    IF NOT can(NEW.exposed_by, 'scope.expose', 'org_unit', NEW.org_unit_id,
               NEW.valid_from, NULL) THEN
        RAISE EXCEPTION
          'person % may not expose the scope of unit % — they hold no scope.expose there',
          NEW.exposed_by, NEW.org_unit_id;
    END IF;

    RETURN NEW;
END $$;

CREATE TRIGGER trg_exposure_direction
    BEFORE INSERT OR UPDATE ON scope_exposure
    FOR EACH ROW EXECUTE FUNCTION check_exposure_direction();
```

Two things about this trigger are deliberate:

- **It is now a single unconditional predicate.** It used to have a second branch
  permitting a `bulk:` prefixed row written by an ancestor — the design's one sanctioned
  exception. That branch is gone
  ([D-045](../decisions/decision-log.md#d-045--the-bulk-scope-exposure-tool-is-removed)),
  and its removal is what makes this function something a reviewer can hold in their head.
  **Every exposure row is written by the unit it covers**, with no marker to explain away.
- **It re-checks layer 1 rather than being layer 1.** The permission check in the write
  path is the primary control; the trigger exists so that a migration, a data fix, or a
  future code path that bypasses the write path still cannot invert the direction of
  authority.

**Layer 3 — the nightly integrity check** in
[../data-model/05-authorization.md](../data-model/05-authorization.md#11-integrity-checks),
which reports (a) any exposure whose granting assignment sits at an **ancestor** of the
covered unit, and (b) any exposure whose actor does not hold `scope.expose` at the covered
unit. Layer 3 catches rows written before the trigger existed, or by a path the trigger
misses; the trigger catches what layer 1 lets through at runtime.

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

```
permission(
    id,
    code,                     -- 'membership.request.approve'
    resource,                 -- 'membership_request'
    action,                   -- 'approve'
    description,
    is_system                 -- true = cannot be deleted; seeded by the platform
)
```

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
| `<resource>.admin` | **Everything** on that resource | `event.admin` |
| `dependent.<x>` | Acting on a supervised person | `dependent.fee.pay` |

Per your instruction: **every resource exposes an `admin` permission** that subsumes all
narrower ones for that resource. The resolver treats `X.admin` as satisfying any check for
`X.<anything>`. This is checked structurally (`code` prefix match), so adding a new narrow
permission to a resource does not require updating every role that grants `X.admin`.

---

## 4. Roles — bundles of permissions

A role is a named set of permissions, assigned to a person for a period, within a scope.

```
role(id, code, name, description, is_system, scope_required)
role_permission(role_id, permission_id)

role_assignment(
    id,
    person_id, role_id,
    scope_type,               -- 'organization' | 'org_unit'
    scope_id,                 -- null for organization
    valid_from, valid_to,
    granted_by, granted_at,
    grant_reason,
    delegation_of             -- nullable; set if this came from a delegation
)
```

### Scope

`scope_type`/`scope_id` is what makes "treasurer of Pack 12" and "treasurer of the
organization" the same row shape. It also means adding a new scope kind later (an event
series, a committee) is a data change, not a schema change.

**Authority does not inherit downward. See §2.** A role at a parent unit does *not* cover
the sub-units beneath it unless each of those has explicitly exposed its scope to it — with
the single important nuance that the **membership registry and the fees belong to the root
unit**, so an organization-scoped role over them is not reaching downward at all.

### Seed roles (starting set — expects your refinement)

The `Req.` column is `role.requires_membership` — whether the role stops working when the
holder's fee lapses ([D-039](../decisions/decision-log.md#d-039--member-permissions-require-a-current-paid-membership)).
It is the column to argue about, and the values below are proposals.

| Role | Scope | Req. | Key permissions |
|------|-------|------|-----------------|
| `system_admin` | organization | — | all, plus `system.*`. Exempt: it is the recovery path, and it must work when nothing else does. |
| `registrar` | organization | yes | `membership.request.*`, `person.*`, `unit_participation.*` |
| `treasurer` | organization or unit | yes | `fee.*`, `payment.*`, `report.finance.view` |
| `unit_leader` | org_unit | **no** | `event.*` for own unit, `unit_participation.view`, `unit_report.view` |
| `assistant_leader` | org_unit | **no** | subset of `unit_leader` |
| `unit_admin` | org_unit | yes | administrative management of a sub-unit and its children |
| `audience_admin` | organization or unit | yes | `audience.view`, `audience.manage` — who maintains the named groups |

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

> **Organization-scoped roles do not reach into sub-units.** A `registrar` assigned at
> organization scope has authority over organization-level records — which now includes the
> **membership registry and the fees**, because those live at the root
> ([D-035](../decisions/decision-log.md#d-035--one-root-unit-all-sub-units-nest-arbitrarily-beneath-it)).
> Authority over a *sub-unit's* own records — its events, its local rosters — still requires
> either that sub-unit exposing its scope to the assignment (§2.3) or the work being done as
> `system_admin` (§2.6). See §2.4.

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

```
access_grant(
    id,
    person_id,                -- the grantee ... OR (exactly one of these two)
    audience_id,              -- ... a set of people, resolved by rule or by list
    scope_type,               -- 'event' | 'document' | 'org_unit' | 'membership' | ...
    scope_id,                 -- the concrete item
    level,                    -- revoked | view | contribute | manage | admin
    valid_from, valid_to,
    is_delegated,
    delegated_from,           -- person_id whose authority this came from
    granted_by, granted_at,
    grant_reason
)
```

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

```
can(person_id, permission_code, scope_type = null, scope_id = null, at = now()) → bool
```

Algorithm:

```
0. DENY — ABSOLUTE, AT ANY SCOPE
   If ANY applicable grant for this person carries level 'revoked' and covers
   this permission — at item scope, unit scope, or organization scope, to this
   person or to an audience they are in — return false.
   No scope outranks a deny. A per-event grant can never restore access that an
   organization-wide suspension removed. See §7.

1. OWNERSHIP
   If the target resource's owner is this person → true for `*.view`, `*.edit`,
   and self-service actions. EXEMPT from the membership gate (§6.1): a lapsed
   person must still be able to reach the screen they renew on.

2. GUARDIANSHIP
   If permission_code is in the 'dependent.' namespace →
     resolve against `guardianship_permission` for the (guardian, dependent) pair
     (requires an active guardianship row). EXEMPT from the membership gate:
     guardianship is a legal relationship, not a membership. See
     [../data-model/04-relationships.md](../data-model/04-relationships.md#2-guardianship_permission).

3. ALLOW — MOST SPECIFIC SCOPE DETERMINES THE LEVEL
   Evaluate from the most local scope outward. The FIRST tier that yields a
   determination decides that permission's effective level for this check:

     a. ITEM GRANT    — access_grant on this exact (scope_type, scope_id)
     b. UNIT GRANT    — access_grant on this org_unit, OR on an org_unit that has
                        an explicit scope_exposure row covering this unit
     c. ORG GRANT     — access_grant with scope_type = 'organization'
     d. ROLE          — role_assignment at the most specific applicable scope:
                        the exact unit, a unit with an exposure row, or organization
                        ...and for tier d ONLY, the membership gate (§6.1) applies.

   If the deciding tier's level satisfies the permission's required level
   (per `permission_level`) → true. Otherwise fall through to the next tier.

4. Otherwise → false
```

Points worth stressing:

- **Default deny.** Step 4. Any new resource starts with nobody able to touch it.
- **Deny is absolute and is the only thing that outranks locality.** A safeguarding
  suspension is not overridable by a more local grant — that is the entire reason
  `revoked` sits outside the tier ordering. See §7.
- **Locality decides between allows.** The most specific scope sets the level. This is
  what "local permissions override global" means: a per-event `manage` grant gives you
  `manage` **on that event** even if your only unit-level grant is `view`, and the
  unit-level `view` still applies to the unit's other events.
- **No ancestor walk.** Step 3b matches the exact unit plus any unit that has explicitly
  exposed its scope. `unit_ancestors()` must not appear anywhere in this path. See §2.
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

```sql
-- Inside tier d, for every candidate role assignment r:
AND (NOT r.requires_membership              -- the carve-out for this role
     OR is_current_member(p_person_id, p_at))   -- the gate
```

| Channel | Gated? | Why |
|---|---|---|
| Ownership (step 1) | **No** | Otherwise a lapse locks a person out of the screen they renew on |
| Guardianship (step 2) | **No** | A legal relationship, not a membership |
| Item / unit / org grants (tiers a–c) | **No** | An explicit act by someone who chose to give this person access. Not inherited, not implied. |
| Roles (tier d) | **Yes**, unless the role opts out | The role was granted *because* the person was a member; the justification has gone |

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

```
permission_level(permission_id, level)   -- per scope_type
```

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
3. Guardianship  (dependent.* permissions — gate-exempt)
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
2. Unit grant    (access_grant on this unit, or on a unit that
                  has explicitly exposed its scope to cover it)
3. Org grant     (access_grant, scope_type = 'organization')
4. Role          (role_assignment, at the most specific
                  applicable scope)                             ← least specific
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

```
access_grant(
    ...,
    is_delegated = true,
    delegated_from = <person_id>,
    valid_to = <required — delegations always expire>,
    grant_reason = 'annual leave 2026-07-01 to 2026-08-15'
)
```

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
| Deriving access from guardianship without a grant | Authorization by identity is unauditable and unsafe | Explicit `guardianship_permission` |
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
