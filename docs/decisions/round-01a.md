# Decision Log — The founding decisions (D-001 … D-015)

> What the first design conversation settled: person, account and membership as three things, everything temporal, no hard deletes, and permissions as grants.

[All decisions](index.md) | [The founding decisions (D-016 … D-030) →](round-01b.md)

---

## D-001 — Person, account, and membership are three separate things

**Status:** decided (from your requirements)
**Date:** initial design

**Decision.** `person` holds identity only. `account` holds login credentials and is
optional. `membership` holds participation and is temporal. No member flags, no
child/adult flag, no `is_member` on `person`.

**Why.** You described a person who was a member 1990–2010 and again from 2024. That is one
person and two membership periods. Any design with `person.is_member` cannot express it,
cannot answer "who was in Troop 12 in 1998?", and silently destroys 36 years of history
the first time someone corrects a record.

**Consequence.** Membership questions are always date-qualified:
[../data-model/03-membership.md](../data-model/03-membership.md) provides `is_current_member()`,
`was_member_on()`, `current_member_category()`, and `membership_years()`.

---

## D-002 — Everything temporal is a period, never a boolean

**Status:** decided
**Date:** initial design

**Decision.** `valid_from` / `valid_to` with `valid_to IS NULL` meaning "still true", and
half-open `[from, to)` ranges. Overlap prevented by `EXCLUDE USING gist` constraints.

**Why.** Required by D-001, guardianship expiry, unit membership history, role terms, and
grant expiry. Enforcing overlap in the database rather than in application code is
essential: an import script, a manual SQL fix, or a future API will bypass application
validation.

**Consequence.** Requires PostgreSQL with `btree_gist`. On MySQL, the guarantee weakens to
triggers plus nightly checks — a materially weaker invariant to be recorded as an accepted
risk if that platform is chosen.

---

## D-003 — Never hard-delete; merges leave tombstones

**Status:** decided
**Date:** initial design

**Decision.** No `deleted_at`, no business-data `DELETE`, no `ON DELETE CASCADE` anywhere.
Ended periods get `valid_to`. Merged people keep their row with `merged_into_person_id`.
Erasure is redaction, not deletion.

**Why.** "Who attended this camp in 2003?" must resolve forever. A hard delete breaks the
safeguarding record. Merges must be reversible because bad matches are inevitable.

**Consequence.** Every query must exclude merged and redacted rows — hence the `v_person`
view and `resolve_person()` function, which exist so application code cannot forget.

---

## D-004 — No automatic merging, ever

**Status:** assumption ⚠ *confirm or overrule*

**Decision.** Every identity match, however strong, requires human confirmation. There is
no confidence threshold above which the system merges on its own.

**Why.** A false-positive merge is a privacy incident: the survivor gains the absorbed
person's permissions, and two people's records become one. A false negative is an
inconvenience someone can fix. The asymmetry justifies the cost.

**Reverse if:** the volume of historical data makes manual review infeasible. If so, the
high-confidence tier should be narrow (exact external identifier match only) and its
application must be logged and alerted.

**See:** [../domain/03-identity-and-legacy.md](../domain/03-identity-and-legacy.md#4-match-signals)

---

## D-005 — Permissions are grants, never derived from identity

**Status:** decided (from your answer)
**Date:** initial design

**Decision.** Being a parent, a member, a leader, or a long-serving volunteer grants
nothing. Every capability comes from an explicit, dated, revocable row.

You answered that **both read and write access should be explicit** for caretakers.

**Why.** The classic failure: a relationship ends (custody changes, a leader steps down) but
access persists, because it was implied rather than granted. Explicit grants make access
auditable and revocable.

**Consequence.** A `guardianship` row alone grants nothing; `guardianship_permission` rows
do. A `position_assignment` alone grants nothing; `role_assignment` does.

---

## D-006 — Per-item permissions are capabilities on the item

**Status:** decided (from your answer)
**Date:** initial design

**Decision.** You clarified that "per-item permission" means *capability on that item* —
"person X may act on item Y" — not a participation record and not an eligibility gate.
Implemented as `access_grant` with an ordered `level`
(`revoked` < `view` < `contribute` < `manage` < `admin`).

**Why.** Isolates authorization from participation (D-005) and from eligibility, which will
be a separate concept when events are specified.

**Consequence.** `permission_level` connects permission codes to the level they require,
so one grant level serves many permissions without a hardcoded mapping.

---

## D-007 — Every resource has an `admin` level that subsumes narrower ones ⚠ **REVERSED**

**Status:** ~~decided~~ **reversed by [D-068](round-05.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle)**
**Date:** initial design · reversed refinement round 5

> **Reversed.** The per-resource `<resource>.admin` *permissions* and the resolver's prefix
> match are gone. **The `admin` grant LEVEL (rank 40) is untouched** — this decision conflated
> the two, and the collision is what made it hard to reverse cleanly. See D-068.

**Decision.** Per your instruction, every grantable resource exposes `<resource>.admin`,
checked by prefix match, plus a single top-level `system.admin`.

**Why.** Without it, every new narrow permission requires updating every role that should
already have implied it — and someone will miss one, producing a permission that silently
is not granted. The prefix match makes new permissions automatically covered.

**Consequence.** The check is computed, not mapped. `person.admin` etc. are real
permission rows so they appear in the role editor.

---

## D-008 — Organizations units are one self-referencing table with configurable types

**Status:** decided (from your answer)
**Date:** initial design

**Superseded by [D-097](round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row), outright: the table is gone.** Its reasoning that a type is a label and
not a permission survives into `person_group`; the self-referencing hierarchy it was proud of is the
exact thing the round deleted.

**Decision.** One `org_unit` table with `parent_unit_id` self-reference and a configurable
`org_unit_type`. Hierarchy via materialized `path` plus recursive CTE functions.

**Why.** You confirmed sub-units are core. Depth is a data question, not a schema question —
a 40-year-old organization has changed its levels. One table means "everyone in this
district" is one recursive query rather than a hand-written union.

**Consequence.** Nesting rules live in `org_unit_type_rule` plus a trigger. Units that
closed remain queryable forever.

---

## D-009 — Unit membership links to `person`, not to `membership`

**Status:** decided
**Date:** initial design

**Decision.** `unit_membership.person_id → person.id`, deliberately not `membership_id`.

**Why.** 1990s rosters have a unit and a year but no membership workflow. Linking to
`membership` would make that data unrepresentable and lose the whole historical dataset.

**Cost.** Nothing enforces that a person with a unit membership holds an organization
membership. Mitigated by application validation plus a nightly check
([../data-model/03-membership.md](../data-model/03-membership.md#7-integrity-checks), check 1).

---

## D-010 — Role assignments and access grants share a scope model and a resolver

**Status:** decided
**Date:** initial design

**Decision.** `role_assignment` and `access_grant` are separate tables but share
`scope_type`, the level model, and one `can()` function. Four authority channels
(ownership, guardianship, item grants, roles), each dispatching from the permission's
namespace, with an absolute deny check in front of them.

**Amended** (see D-031, D-032): the resolver's allow channels are now ordered by
**locality** rather than by channel, and the deny channel is scope-independent.

**Amended again by [D-079](round-06.md#d-079--the-guardianship-channel-is-entered-by-shape-not-by-permission-name),
and this reaches the sentence above the amendment.** "Each dispatching from the permission's
namespace" was how the channels were *found*, and it is gone: dispatch is now `subject ≠ actor`
for guardianship, and `system.` remains the only namespace with resolver-visible meaning. **The
four channels themselves are untouched** — that part of this decision was durable for six rounds
and is the part worth keeping. What the namespace rule turned out to be was a way of skipping the
guardianship channel whenever the permission's *name* happened not to mark it as a guardian act,
which is a thing a name cannot do. **Note the shape of the failure for future amendments: the
channel list was right and the routing over it was wrong, and every document that cited the
routing copied the error.**

**Why.** They are the same idea at two granularities — authority for a period, in a scope,
granted by someone. A single resolver prevents the divergence that makes the weaker of two
implementations an exploit. Separate tables because their lifetimes, granters, and
revocation semantics genuinely differ.

---

## D-011 — `scope_id` on `access_grant` is polymorphic, with no foreign key

**Status:** assumption ⚠ *a real fork — worth a deliberate decision*

**Decision.** `access_grant.scope_type` + `scope_id` with no FK. Validated by
`grant_scope_type` plus nightly orphan checks.

**Why.** Most of this system is unspecified (events, documents, and more). Polymorphism
makes each new grantable type a config row rather than a schema migration.

**Cost.** No referential integrity. Mitigated by: `grant_scope_type` FK, application-level
grant closure on item delete, nightly orphan detection, non-reused `BIGINT` ids.

**Alternative.** A `grantable_item(id, item_type)` supertable referenced by every grantable
entity — full integrity, heavier design, migration per new type. **Overrule this if you
prefer integrity to flexibility.**

---

## D-012 — Status strings compare by rank, never lexicographically

**Status:** decided
**Date:** initial design

**Superseded by [D-099](round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality): the levels are gone, so the bug this guarded is unconstructible.** The hazard
is not forgotten — the one surviving ordered triple, a guardian's `none` / `view` / `write`, still sorts
wrong alphabetically, and [data-model/00-conventions.md](../data-model/00-conventions.md) says so where
this entry used to.

**Decision.** `access_level` is a lookup table with an integer `rank`. All level comparisons
use `rank`.

**Why.** `'admin' < 'contribute'` alphabetically. A string comparison silently inverts the
levels and makes the most powerful level the least. It throws no error and passes most
tests. This is the single most dangerous easy mistake in the design.

---

## D-013 — Explicit deny (`revoked`) is checked before everything

**Status:** decided
**Date:** initial design

**Decision.** Resolver channel 0. A `revoked` grant overrides roles, item grants, and
ownership. In the guardianship channel, `is_granted = false` overrides a granted
`dependent.admin`.

**Why.** Without an explicit deny level there is no way to express "this person must not
see this event" or "this guardian may not see medical records" when a broader grant would
otherwise allow it. Court-ordered restrictions must not be overridable by a broader grant.

---

## D-014 — Roles do not inherit from other roles

**Status:** decided
**Date:** initial design

**Decision.** No role-to-role inheritance. If `unit_leader` should have `assistant_leader`
permissions, they are granted explicitly.

**Why.** Inheritance chains produce authorization answers nobody can predict by reading the
configuration. Predictability matters more than configuration economy in an authorization
system — the people who must reason about it are volunteers, not engineers.

**Note:** unit *scope* inheritance was a separate axis. It was **reversed** — see D-031.
That reversal does not disturb this decision: role-to-role inheritance remains prohibited
for the same reason it always was.

---

## D-015 — Authority inherits downward through the unit hierarchy ⚠ **REVERSED**

**Status:** **reversed by [D-031](round-02-03.md#d-031--no-downward-inheritance-of-authority-scope_exposure-is-the-only-crossing)**
**Date:** initial design

**Decision (original).** A role assigned at a unit covers that unit and all descendants. A
district treasurer can act on troops within the district.

**Why (original).** Matches how organizations actually work — a district officer has
district-wide responsibility.

**Why it is reversed.** Your rule: *"The organization itself should not be able to itself
decide permissions over the nested unit, it must come from the unit itself up. The only
exception is the system admin."* Downward inheritance makes every unit's authority
decidable from above — a role written at the district level silently reaches into troops
that never agreed to it. That is exactly the direction you excluded. The replacement is
`scope_exposure`, where the **unit** grants coverage over itself.

**Consequence, accepted.** Organization-wide operational roles (national registrar,
national treasurer) no longer work by assigning a role high in the tree. Tracked as the
reworked [C-1](../open-questions.md).

---
