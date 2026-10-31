# Appendix — ERD: authorization

The authorization model as one diagram, the tables behind it, and the expression tree an audience is stored as.

**Section numbers are shared across the three parts** and never renumbered, because other pages cite them by number and their anchors are built from them: [erd.md](erd.md) holds §1–§4, the diagrams of the people — identity and attributes, the unit's groups and offices, membership, guardianship; [erd-a-authorization.md](erd-a-authorization.md) holds §5–§5b, the whole authorization answer, its tables and the audience expression tree; [erd-b-inventory.md](erd-b-inventory.md) holds §6–§8, the temporal pattern, the table inventory and the foreign key summary.

---

## 5. Authorization — the whole answer in one diagram

```
                     ┌──────────────────────────────┐
                     │          permission          │   'membership.request.approve'
                     │   code · resource · action   │   'event.answer.view'
                     │   applies_to ∈ unit |        │   where a code may be granted at all,
                     │              unit_and_item   │   checked when the GRANT IS SAVED (D-099)
                     │   right_kind ∈ read | write  │   ONE customer: the guardianship channel
                     └──────────────┬───────────────┘   (D-074, given the column by D-099)
                                    │
     one check asks for ONE code. There is no wildcard except 'system.admin' (D-068):
     "can do everything about events" is an OFFICE some grants name, one code per grant.
                                    │
                                    ▼
 ╔═══════════════════════════════════════════════════════════════╗
 ║                         access_grant                          ║  THE ONLY TABLE THAT
 ║  person_id   ─┐  exactly ONE of the three names the grantee:  ║  GRANTS (D-005). A grant at
 ║  audience_id ─┤  two is ambiguous, none is meaningless; a key ║  the unit reaches EVERY item
 ║  api_key_id  ─┘  is in no set, so it is read, never evaluated ║
 ║  scope_type ────►  grant_scope_type                           ║  of every type; a grant on
 ║               unit | event | person_group | role | document   ║  one item reaches that item
 ║  scope_id  ⇒ (polymorphic, NO foreign key; ABSENT exactly at  ║  and nothing else (D-099).
 ║               'unit' — that absence IS "the unit is a scope,  ║  There is no middle tier
 ║               not a row")                                     ║  left for anything to
 ║  permission_id ───► permission   (one code, never a bundle)   ║  inherit down.
 ║  effect ∈ allow | deny      DENY IS ABSOLUTE: checked first,  ║
 ║                             scope-independent, beats every    ║  A grant is one code and one
 ║                             allow, no tie-break of any kind   ║  effect: no level, no locality,
 ║  valid_from / valid_to [T] · granted_by · revoked_by/_at      ║  and no wildcard — a check for
 ║  is_delegated · delegated_from  (a delegation must expire)    ║  'X.y' needs a grant of 'X.y'.
 ╚═══════════════════════════════════════════════════════════════╝
        ▲ aimed at by id                        ▲ named by code from a leaf (D-103)
        │
   ┌──────────────────────┐                 ┌───────────────────────┐
   │         role         │  an office, and │       audience        │  an EXPRESSION over
   │ code · name ·        │  it confers     │ name · code? ·        │  named sets, stored as a
   │ description ·        │  NOTHING        │ valid_from/[to] [T]   │  tree (D-101). Nothing here
   │ sort_order ·         │  by itself:     │ one shape: an         │  is a roster: an operand
   │ valid always         │  the codes an   │  expression over named│  names a set, and the set
   │ (D-053): NO period   │  office carries │  sets, with no depth  │  is computed at the check
   │ NO scope (D-100): an │  are the live   │  limit (D-101, D-105).│  it is asked about.
   │ office is held at the│  grants whose   └───────────┬───────────┘
   │ unit, never per item │  audience names ├───────────┴──────────────────────────┐
   └──────────┬───────────┘  ROLE(x)        ▼                                      │
              │ dated holders     ┌─────────────────────┐                          │
              ▼                   │  audience_operand   │  hand-written people     │  the audience's
   ┌────────────────────────────┐ │ one row = ONE NODE: │  are PERSON(a) +         │  expression is
   │ person · role ·            │ │ operator + left_id  │  PERSON(b) leaves in     │  evaluated live
   │ valid_from · valid_to ·    │ │  ...or... ONE LEAF: │  this same tree (D-105); │  at the resolver
   │ granted_by · note          │ │ selector_kind +     │  a person is in the set  │  (D-101)
   │ NO scope columns at all:   │ │ selector_arg_id ⇒   │  or not, with no dates   │
   │ a role is held at the unit │ │ (NO FK — see below) │  of their own.           │
   └────────────────────────────┘ └──────────┬──────────┘                          │
                                             │ every leaf is typed by              │
                                             ▼                                     │
                                  ┌─────────────────────────────┐                  │
                                  │        selector_type        │  SEEDED and      │
                                  │ code (a RESERVED word) ·    │  organization-   │
                                  │ takes_argument ·            │  read-only: the  │
                                  │ binds_to_item ·             │  language is data│
                                  │ argument_type               │  (D-101), not    │
                                  └─────────────────────────────┘  extensible at   │
                                                                   runtime         │
                                                                                   │
   A BOUND operand — the argument-less `PLACED`, `ORGANIZERS`, `CONFIRMED`,        │
   `ATTENDED`, `ON_WAITLIST` — means "relative to the item being                   │
   checked". Legal only on an item-scope grant whose type matches `argument_type`  │
   (`PLACED` on a group grant is refused, `ORGANIZERS` on a unit grant is          │
   refused). EVERY EVENT'S AUTHORITY is written by the act that CREATES THE        │
   EVENT, in the same transaction as the event row (D-102, D-151):                 │
   Twelve item-scope allows per event, each aimed at an audience whose             │
   expression is the bare operand ORGANIZERS — so `event.answer.view` is           │
   one of twelve, and never one row shared by every event.                         │
   `OLDER(n)` and `YOUNGER(n)` bind to no item and point at no row:                │
   their argument is an integer — the registry's first non-reference — so          │
   `selector_arg_id` holds a number with nothing behind it: no edge to draw,       │
   nothing for a merge to repoint, nothing for a cascade to find, and the keyless  │
   polymorphic keys drawn here stay two of seven. Thirteen seeded rows:            │
   five argument tables, one integer, and the operators are still `+ - *`.         │
   `PRESENT(<event>)` is not seeded, and the reason is a consequence: a tick box   │
   on a check-in screen would revoke a leader's access to their own camp when      │
   somebody forgets to tick it. `WHITELISTED` is not seeded either, for want of    │
   any state to evaluate (F-20). Neither is kept out by the language — nothing     │
   in it would refuse either name — both are kept out by what they would do.       │
   `GUARDIANS` is not seeded: a guardian holds a level over a child, not a set of  │
   codes, so an audience aimed at guardians offers one code at a time what the     │
   guardianship channel grants outright (D-113).                                   │
                                                                                   │
   can(person, permission, scope_type, scope_id, at, about_whom) ── ONE resolver ─ ┘
   can_key(api_key, permission_code, scope_type, scope_id, at) ── same resolver, no person
   ──────────────────────────────────────────────────────────────────────────────
    0  explicit DENY ── absolute and scope-independent. A deny at the unit reaches every
       item of every type; a personal deny beats an audience allow, because this step has
       already returned (D-013). Revoking is ending that row's period, never a rank of its own.
    1  a live ALLOW at the unit ── reaches every item of every type: there is no tier
       between the unit and an item (D-097), and no owner of an item to ask (D-102).
    2  a live ALLOW on this exact item ── exact scope type and id. Nothing precedes it:
       one resolver, and no special case for events inside it (D-102).
    3  OWNERSHIP ── the checked person is the actor. Their own row, their own data.
    4  GUARDIANSHIP ── entered by SHAPE (the subject is not the actor), never by a code's
       name; answers with an ALLOW only, when `right_level` covers `permission.right_kind`
       — none covers nothing, view covers `read`, write covers both (D-074, D-079, D-099).
    5  default DENY.
   A KEY reaches steps 0, 1, 2 and 5 and no others: steps 3 and 4 each compare a person
   against a row, and a key is not a person — so neither channel is refused by a rule of its
   own, neither is reachable (D-118). can_key therefore takes no owner and no person of any
   kind: that parameter would be the impersonation hole, because a claimed person is exactly
   that — claimed (D-121).
   The allow steps are ALTERNATIVES producing one boolean: their order decides which channel
   the audit names, never what the answer is. There is **no locality rule**: locality could
   only ever order allows against each other, and a boolean has nothing to order (D-099).
   Step 0 is not an ordering either — it is a check that runs before every other.
```

**Key points:**

- **One table grants.** `access_grant` is the only place authority is written, plus the one
  table over a single person, `guardianship_permission` (§4, step 4 above). `role_holder`,
  `person_group_member` and every operand of an audience decide only **whom a grant reaches** —
  being in a set is worth exactly what the grant aimed at that set says
  ([D-005](../decisions/round-01a.md#d-005--permissions-are-grants-never-derived-from-identity),
  restated for roles by
  [D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)).
  `role_holder` carries no scope columns, no level and no resolver channel; what it shares with
  `access_grant` is only the temporal shape every dated row has.
- **There is no wildcard permission.** A check for `X.y` needs an exact grant of `X.y`, or
  `system.admin` ([D-068](../decisions/round-05.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle)).
  "Can do everything about events" is a **role** some grants name, each grant naming one of the
  thirteen `event.*` codes. *Why `admin` is never ambiguous here: a grant carries no level, so the
  word appears in exactly one place — the code `system.admin` — [D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality).*
- **Deny is absolute.** **A live deny beats every live allow, with no tie-break, and the only thing
  that removes one is a person ending its period**
  ([D-013](../decisions/round-01a.md#d-013--explicit-deny-revoked-is-checked-before-everything),
  [D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)).
  That is why `valid_to` earns its keep on a deny row, and why *a live deny matching no live allow*
  is a reported shape rather than a harmless row — a deny that denies nothing is how a stale
  restriction outlives its reason.
  *Why the ranking went: D-013 let a newer act outrank a denial, so a stale deny was one late
  revocation away from winning anyway. Deleting the ordering deleted the hatch.*
- **The membership gate is opt-in, written in the expression.** `MEMBERS` is an operand evaluated
  live on the checked date, so `MEMBERS * ROLE(x)` gates an office and `ROLE(x)` alone does not, and
  the *"except this one person"* case is written inside the same expression
  ([D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)).
  The failure mode is a grant written `ROLE(x)` with no `MEMBERS`, authorizing a lapsed member
  silently and forever, failing closed-looking so nobody notices — the control is the **Unusual
  section of the tab on the permissions page**, which lists exactly that shape and refuses nothing,
  plus the writer's own habit that a grant template carries `MEMBERS` — **no grant arrives already
  carrying it**, and the only grants this system writes by itself, the twelve beside an event, must not
  ([D-109](../decisions/round-13.md#d-109--nothing-a-rule-names-is-deleted-deprecated-hidden-disabled--and-a-tab-instead-of-a-report),
  [F-13](../open-questions.md#f-13)). Ownership and guardianship are not gated and never were.
- **The guardianship channel is entered by shape, not by permission name** ([D-079](../decisions/round-06.md#d-079--the-guardianship-channel-is-entered-by-shape-not-by-permission-name)):
  the check is about someone other than the actor, and the channel answers with **allows only**. A
  sufficient `right_level` returns true; no row, `none`, or too low a level returns nothing at all
  and the actor's own grants are tried. A prohibition is therefore a `deny` grant, never a low level.
  What the channel compares a permission against is now `permission.right_kind` — a column D-099
  added and names as having exactly one customer, this channel.
- **There is no downward crossing, because there is no down.** With one unit there is no *outside it*
  for authority to leak toward, so [D-031](../decisions/round-02-03.md#d-031--no-downward-inheritance-of-authority-scope_exposure-is-the-only-crossing)
  was not weakened, it was **deprived of its subject**
  ([D-097](../decisions/round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row)).
  A grant at the unit therefore reaches every item of every type, and `system.admin` with it.
  *What is lost and reproduced nowhere is the safeguarding property: access to a body's children had
  to be granted **by that body** — by the people who recruited its leader and can be asked. What
  remains is a permission held by a named adult, an audit trail whose payloads expire after two years,
  and a report of who holds the write, minus the part where the adult was somebody the body chose.*
- **A grantee may be an audience, or a key.** `access_grant.person_id`, `audience_id` and `api_key_id`
  carry exactly one value between them — never two, never none
  ([D-116](../decisions/round-16.md#d-116--a-caller-that-is-not-a-person-is-a-registered-key-and-a-key-is-a-third-grantee-kind)).
  An audience is **an expression over named sets**
  ([D-101](../decisions/round-10b.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree)):
  every operand is evaluated live and nothing is stored as a roster, a hand-written set is written
  `PERSON(a) + PERSON(b)` like any other set
  ([D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)),
  and two sets are composed with an operand rather than an edge between them.
  **Author in sets, evaluate per person:** a check compiles the expression to a predicate and never
  materializes a set, and an operand that does not resolve is the **empty set**
  ([D-106](../decisions/round-11-12.md#d-106--a-failed-operand-stays-the-empty-set-the-missing-half-was-a-report-not-a-refusal)).
  That is one of the two rules the stated scale names as surviving any growth — the other is that a
  listing is paginated — and it is why the system gets slow before it gets wrong
  ([D-112](../decisions/round-13.md#d-112--the-systems-scale-is-stated-hundreds-of-people-tens-of-registrants-per-event)).
  *Why "fail closed" is the wrong shorthand here: a failed operand on `+` or `*` narrows the set and a
  failed operand on `-` widens it, so `EVERYONE - PERSON(x)` with a dead `x` is fail-closed and
  lockout-everybody in one step.* The failure stays fail-closed and stops being silent: an audience
  carrying a leaf that resolves to nothing is **listed** on the tab on the permissions page
  ([D-109](../decisions/round-13.md#d-109--nothing-a-rule-names-is-deleted-deprecated-hidden-disabled--and-a-tab-instead-of-a-report)),
  and no save is refused for it. **One thing can still produce such a leaf: a redacted person.**
  Nothing else a rule names is deleted any more, and the empty set a `disabled` operand yields is
  somebody's deliberate act, not a failure. A person with no birth date is not such a failure either:
  that operand resolves perfectly well, and they are simply not in the set.
- **A key is the third grantee, and it holds no expression.** The seeded `selector_type` registry keeps
  its **thirteen** rows and none of them names a key, so there is nothing to compile for one and no set it
  could join — `EVERYONE` is every *person*, so a key is not even in the widest operand
  ([D-117](../decisions/round-16.md#d-117--a-key-is-never-inside-an-expression-thirteen-selectors-and-none-of-them-can-name-one)).
  What that keeps is this diagram's largest machinery unchanged: a grant naming a key is read as written,
  `ruleset_version` keeps the two tables that bump it, and `api_key_id` is a **real foreign key**, so the
  reference-less polymorphic keys stay the two they were. What it costs is that **"grant this to the
  integrations" is not one sentence**: twelve integrations need twelve grants, and the thirteenth is a
  write somebody performs.
- **Nothing owns an event** ([D-102](../decisions/round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)).
  The people connected to an event are named by operands that bind to it — `ORGANIZERS`, `PLACED`,
  `CONFIRMED`, `ATTENDED`, `ON_WAITLIST` — each a set the item itself defines. An operand is a set, not
  a grant, which is why
  [D-062](../decisions/round-05.md#d-062--organizers-are-appointed-on-the-event-not-granted)'s "an
  `event_organizer` row grants nothing" is the whole story: the row appoints, the operand resolves.
  The consequence worth remembering: a bound operand is illegal at the unit, so
  "every event's answers go to its organizers" is **twelve item-scope allows** written beside the event
  row by the act that creates the event, one set per event, in one transaction — and an event whose
  creation died partway through has nobody who can read its answers, which is what the *events with an
  incomplete organizer bundle* report is for — it counts every event, not only staffed ones, and names which
  of the twelve are absent. **That failure has an author**: one create, named in the trail,
  rather than a configuration step nobody took
  ([D-151](../decisions/round-21.md#d-151--creating-an-event-writes-the-events-authority-and-its-organizers-may-grant-on-it)).
- `scope_id` is polymorphic (no FK) so a new grantable item type is a config row, not a
  migration. Accepted cost, with four mandatory mitigations — the same trade-off and the same four
  mitigations hold for the second reference-less key, `audience_operand.selector_arg_id`
  ([D-011](../decisions/round-01a.md#d-011--scope_id-on-access_grant-is-polymorphic-with-no-foreign-key),
  [D-101](../decisions/round-10b.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree)).

See [../data-model/05-authorization.md](../data-model/05-authorization.md) and
[../domain/06-authorization-model.md](../domain/06-authorization-model.md).

---

## 5a. Authorization — the tables

```mermaid
erDiagram
    PERMISSION {
        integer id PK
        string code
        string applies_to
        string right_kind
        string namespace
        boolean is_assignable
    }
    ROLE {
        integer id PK
        string code
        string name
        integer sort_order
    }
    ROLE_HOLDER {
        integer role_id FK
        uuid person_id FK
        date valid_from
        date valid_to
        uuid granted_by FK
        timestamp granted_at
        string note
    }
    GRANT_SCOPE_TYPE {
        string code PK
        string name
        string item_table
        boolean is_item_scoped
    }
    ACCESS_GRANT {
        uuid person_id FK
        integer audience_id FK
        integer api_key_id FK
        string scope_type FK
        integer scope_id
        integer permission_id FK
        string effect
        date valid_from
        date valid_to
        boolean is_delegated
        uuid delegated_from FK
        uuid granted_by FK
    }
    AUDIENCE {
        integer id PK
        string code
        string name
        date valid_from
        date valid_to
    }
    API_KEY {
        integer id PK
        string code
        string name
        string secret_hash
        date valid_from
        date valid_to
        timestamp last_used_at
        uuid owner_person_id FK
        uuid created_by FK
        timestamp revoked_at
        uuid revoked_by FK
        string revoke_reason
    }
    PERSON_GROUP {
        uuid id PK
        string name
    }
    PERSON {
        uuid id PK
        string public_id
    }
    EVENT {
        uuid id PK
        string title
    }
    PERSON ||--o{ ROLE_HOLDER : "holds an office"
    PERSON ||--o{ ROLE_HOLDER : "appointed the holder"
    ROLE ||--o{ ROLE_HOLDER : "is held"
    PERSON ||--o{ ACCESS_GRANT : "is granted to"
    PERSON ||--o{ ACCESS_GRANT : "delegated by"
    AUDIENCE ||--o{ ACCESS_GRANT : "is granted to"
    API_KEY ||--o{ ACCESS_GRANT : "is granted to"
    PERMISSION ||--o{ ACCESS_GRANT : "is its one code"
    GRANT_SCOPE_TYPE ||--o{ ACCESS_GRANT : "types the scope"
```

**Key point:** `access_grant` is a pentagon of references and grants exactly one thing — a grantee
(person **or** audience **or** key), a scope, **one** permission, an **effect**, a period
([D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)).
Uniqueness follows the shape: at most one live **allow** per grantee, scope **and permission** — and
because a unique index does not constrain a row whose grantee column is `NULL`, that one rule is
**three** unique indexes, one counted over the rows naming a person, one over the rows naming an
audience, one over the rows naming a key
([D-116](../decisions/round-16.md#d-116--a-caller-that-is-not-a-person-is-a-registered-key-and-a-key-is-a-third-grantee-kind)).
Denies sit deliberately outside all three so a deny can sit beside an allow on the same item — that pair is
the only way to say *"this person has the unit's events, except this one"*. A person, a set and a key are
three grantees, so the same code on the same item may live once for each of them, and no row there is
another one's duplicate.

**No line leaves `scope_id`, and that is the diagram telling the truth.** The edge that exists runs to
`grant_scope_type`, the seeded registry (`unit` — the only row with `is_item_scoped = false`, `event`,
`person_group`, `role`, `document` deferred) which is what states which table the unresolved id belongs
to. The id itself is `⇒` polymorphic: no foreign key, validated by the registry plus a nightly orphan
scan per type ([D-011](../decisions/round-01a.md#d-011--scope_id-on-access_grant-is-polymorphic-with-no-foreign-key),
§8). A unit grant carries **no** `scope_id` at all, which is the entire schema-level content of "the unit
is a scope, not a row".

**A role is not a permission bundle.** An office carries no codes of its own: what a treasurer has is the
live grant rows whose audience names that office as `ROLE(x)`, so *"what may a treasurer do?"* is a query
over rows a screen can show
([D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)).
`role_holder` is a dated holder row — person, role, period, who granted it, note — and **names one person,
never a rule**: an office that cannot answer "who was treasurer in 2023" is not an office record
([F-12](../open-questions.md#f-12)). `role` itself has no period: it is a definition, valid always, and the
period lives on the holder row
([D-053](../decisions/round-04.md#d-053--a-role-is-valid-always-only-its-assignment-is-temporal)).
The second arrow into `person` is `granted_by`, and it is drawn to a person because the column records
**who appointed** — a fact carried on the appointment, readable five years later by whoever has to ask.
The **act** of appointing is what `audit_log` holds, with its actor taken from the request context rather
than from the row ([../data-model/06-audit-and-import.md §2](../data-model/06-audit-and-import.md#2-audit_log));
the two are not one column's job, and every other actor column here (`access_grant.granted_by`,
`person_group_member.added_by`) points the same way for the same reason. **The first actor column in this
appendix that does not point at a person is on a trail, not in this diagram:** `access_log.api_key_id` and
`audit_log.api_key_id` name the registered caller a request authenticated as, mutually exclusive with each
trail's `actor_person_id` — a request is made by a person or by a key, never by both at once, so there is
no actor column to disagree about and `on_behalf` is never set on a row whose actor is a key
([D-121](../decisions/round-16.md#d-121--a-key-never-carries-a-persons-authority)). **A trail row naming
neither is not a missing arrow:** the empty column is this system acting on its own and a complete answer to
*who did this*, and where the trail has a label column the writer's name comes from a fixed list rather than
from free text ([../data-model/00-conventions.md §7a](../data-model/00-conventions.md#7a-what-an-empty-actor-column-means),
[D-125](../decisions/round-17.md#d-125--an-empty-actor-column-is-this-system-acting-on-its-own-and-its-name-comes-from-a-fixed-list)).

**Names are one namespace.** `role.code`, `person_group.name` and a set `audience.code` are unique
**together**, case- and separator-folded, and every `selector_type.code` is reserved — so a group called
`MEMBERS` is refused at the save rather than discovered later as an expression whose meaning moved. No
constraint spans three tables, so the write path carries the rule and an integrity check asserts the
write path still does
([D-101](../decisions/round-10b.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree),
[D-103](../decisions/round-10b.md#d-103--an-audience-may-name-another-audience),
[D-081](../decisions/round-06.md#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now)).
What is stored is always kind + id, so a rename never rewrites a grant.

---

## 5b. The audience expression

The rows of one audience's expression tree. The audience **is** the tree; `audience_operand` holds its
nodes and leaves, one row each.

```mermaid
erDiagram
    AUDIENCE {
        integer id PK
        string code
        string name
        date valid_from
        date valid_to
    }
    AUDIENCE_OPERAND {
        integer id PK
        integer audience_id FK
        integer parent_id FK
        string operator
        integer left_id FK
        integer right_id FK
        string selector_kind FK
        integer selector_arg_id
    }
    SELECTOR_TYPE {
        string code PK
        string name
        boolean takes_argument
        boolean binds_to_item
        string argument_type
    }
    ROLE {
        integer id PK
        string code
    }
    PERSON_GROUP {
        uuid id PK
        string name
    }
    PERSON {
        uuid id PK
    }
    EVENT {
        uuid id PK
        string title
    }
    AUDIENCE ||--o{ AUDIENCE_OPERAND : "has its tree"
    AUDIENCE_OPERAND ||--o{ AUDIENCE_OPERAND : "has a child"
    SELECTOR_TYPE ||--o{ AUDIENCE_OPERAND : "types the leaf"
    AUDIENCE_OPERAND }o--o| ROLE : "ROLE(x) - no FK"
    AUDIENCE_OPERAND }o--o| PERSON_GROUP : "GROUP(x) - no FK"
    AUDIENCE_OPERAND }o--o| AUDIENCE : "AUDIENCE(code) - no FK"
    AUDIENCE_OPERAND }o--o| PERSON : "PERSON(x) - no FK"
    AUDIENCE_OPERAND }o--o| EVENT : "ORGANIZERS(x) - no FK"
```

**Five of these lines are `⇒` in the notation above, and not one of them is a foreign key.** A leaf's
`selector_arg_id` is one
integer column pointing at `role`, `person_group`, `audience`, `person` or `event` depending on
`selector_kind` — the same polymorphism, the same four mandatory mitigations and the same nightly orphan
scan as `access_grant.scope_id`, the same trade-off accepted for both keys
([D-011](../decisions/round-01a.md#d-011--scope_id-on-access_grant-is-polymorphic-with-no-foreign-key),
[D-101](../decisions/round-10b.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree)).
Drawing it as five real edges would be the lie; drawing it as no edges at all would hide the fan. The
registry is what resolves the ambiguity, and it is a real edge: `selector_type` says whether the code
takes an argument, whether the **argument-less** form binds to the item being checked, and what type the
argument is — the parser reads its reserved words from that table, the editor builds its dropdown from
it, and the save path checks arity against it
([D-101](../decisions/round-10b.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree)).
It is seeded and **organization-read-only** — the whole table is written only by migrations and no screen
edits it: "the language becomes data" has never meant the language is extensible at runtime, and a seeded
code with no shipped evaluator arm is a deployment bug that surfaces as an empty set — which is why the
registry holds no row waiting to be implemented.

**`argument_type` has six values and five of them are tables.** `OLDER` and `YOUNGER`
([D-107](../decisions/round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded))
take **an integer — a whole number of years** — so `selector_arg_id` holds `18` for `OLDER(18)`, and this
is the first operand argument in the registry that names no row. **The five drawn edges are still exactly
five, and the count this appendix keeps is unchanged for the right reason rather than by luck**: a scalar
sitting in `selector_arg_id` is not a reference, so there is nothing to repoint when a person is merged,
nothing for a cascade to find, nothing for the orphan scan to walk, and the binding check that compares
`argument_type` against a grant's item type simply does not apply to an operand that binds to no item.
**There are still exactly two reference-less polymorphic keys in what this part draws** —
`access_grant.scope_id` and `audience_operand.selector_arg_id` — and `18` is not one of them, because the
check is about references. **The shared inventory in §8 keeps the design's whole count, which is seven: the
other five sit on the two trails and on a merge conflict, none of which is drawn here.** The two operands read `person.birth_date` **as of the date being checked**, which is why they are a
registry row and nothing more: they are ordinary named operands, composed by `+ - *` like every other, and
the set they name changes with no write at all.

**No leaf resolves to anything but people, and that is why there is no `GRANTS(…)`.** An operand resolves
to a **set of people**, because a set of people is what a grantee that is a set is — the two grantees that
are not sets, one named person and one registered key, name a single bearer and are reached without this
tree at all ([D-117](../decisions/round-16.md#d-117--a-key-is-never-inside-an-expression-thirteen-selectors-and-none-of-them-can-name-one));
a set of *grants* is a filter over
the grant list, and "these twenty rows, now also for that office" is something an editor does while
finding the rows to act on, not something a stored grantee could ever be evaluated against. The bulk
operation stays an affordance over the list, and the registry refuses the kind rather than leaving it
unimplemented
([D-101](../decisions/round-10b.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree)).

**One row is one node or one leaf, never both.** A node carries `operator` (`+` union, `*` intersection,
`-` difference) with `left_id` and `right_id`, which are **not** interchangeable because `-` is not
commutative; a leaf carries `selector_kind` and, where the registry says so, `selector_arg_id`.
`parent_id` lives **on the child**, so a node belongs to exactly one expression and a sharing table is
refused — editing a shared node would silently widen every grant using it. `audience_id` is
denormalized onto every row so the read path fetches one audience's rows in one indexed read and
assembles the tree in memory; it never walks a parent chain
([D-101](../decisions/round-10b.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree)).
`OLDER` and `YOUNGER` are two seeded rows of that registry and nothing more: the operator enum is `+ - *`,
an attribute adds no node kind and no column, so `(MEMBERS * OLDER(18)) - YOUNGER(6)` is stored with the
shapes that already existed — a `*` node with a `MEMBERS` leaf and an `OLDER` leaf, under a `-` node whose
right operand is a `YOUNGER` leaf
([D-107](../decisions/round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)).

**`AUDIENCE(code)` is the leaf that points back into this diagram**
([D-103](../decisions/round-10b.md#d-103--an-audience-may-name-another-audience)): it names another
saved audience **by its `code`**, which is why `code` exists and is optional, and why an unnamed audience
is simply not composable. The `AUDIENCE` leaves *are* the reference edges, so "does this cycle", "how deep",
"which grants name this audience" and "may I end it" are all one indexed query over
`selector_kind = 'AUDIENCE'` rows.
*Why a saved expression can still cycle when every one of them is a tree: one tree cannot, but a forest of
trees pointing at each other can. The save-time reachability walk therefore goes inside this tree and
across every `AUDIENCE(x)` leaf, and it is the only structural guard there is — no cap on expression depth
survives
([D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)).*
The walk looks for cycles and nothing else: the tree is stored exactly as the writer wrote it, with no depth
bound and no rebalancing, and **nothing bounds what an expression may cost** — affordable at the stated size
of a few hundred people and a few dozen registrants per event, with a named trigger to reopen the question
([D-112](../decisions/round-13.md#d-112--the-systems-scale-is-stated-hundreds-of-people-tens-of-registrants-per-event)).
Depth and width stay a convention, not a guard
([D-081](../decisions/round-06.md#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now)):
there is no report of the widest and deepest audiences, and what the permissions page shows is **the tab**
listing rules that name something deprecated, hidden or disabled or fail to resolve — silent about how wide
any of them is
([D-109](../decisions/round-13.md#d-109--nothing-a-rule-names-is-deleted-deprecated-hidden-disabled--and-a-tab-instead-of-a-report)).
The protection that keeps the dangerous case out is that an audience named by a live grant may not be ended
or deleted while that grant lives: under `-`, an emptied operand makes the answer **wider**.

**A hand-written set is an expression like any other**
([D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)),
written as `PERSON(a) + PERSON(b)` in the same tree as every `GROUP(x)` and `MEMBERS` leaf. What that gives
up is written as lost, not as managed: **no per-person dates** — a person
is in the audience or not, and a June-to-August exception is a second grant with its own period, which is
what
[D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)'s
shape is for — and no record of who added a person beyond who last saved the tree.
**Why a name in an expression was never merged into `GROUP(x)`:** a group's members are the organization's
record and are true with no grant pointing at them, while a name written into an expression is meaningless
outside the expression it completes
([D-098](../decisions/round-10a.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority)).
Naming people inside a grant must not make them group members, and
`(GROUP(kitchen) + PERSON(honza)) - PERSON(a)` says the whole thing: the same set as any list spelling, one
fewer kind of thing in the model, and no chance of the permission table becoming the system's roster.

**`PERSON(x)` is drawn as the `person` argument edge, and the edge has exactly one occupant.** `PERSON` is
one of the **thirteen** seeded `selector_type` rows — the seeded registry, not an evaluator's arm list, is
the record of what the language accepts
([D-107](../decisions/round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded),
[D-104](../decisions/round-10b.md#d-104--a-permission-codes-last-segment-is-an-action-and-a-registry-that-prose-contradicts-is-a-fiction),
[D-113](../decisions/round-13.md#d-113--the-guardianship-channel-has-no-expression-guardians-is-not-a-selector)).
A guardian is not a second occupant. Guardianship is a **level over a child** — `none`, `view` or `write`
read off the `guardianship` row
([D-074](../decisions/round-06.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular)) —
and not a set the expression language resolves, so an operand aimed at guardians would offer, one code at a
time, a subset of what those people already hold
([D-113](../decisions/round-13.md#d-113--the-guardianship-channel-has-no-expression-guardians-is-not-a-selector)).
What the registry row adds over the storage fact — `selector_arg_id` may hold a person id
([D-011](../decisions/round-01a.md#d-011--scope_id-on-access_grant-is-polymorphic-with-no-foreign-key)) — is
one fact of meaning: **an expression may name a single human who is on nobody's roster**. Since a
hand-written set is a sum of these
([D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)),
the edge is load-bearing: every hand-named person in the system is a `selector_arg_id` with deliberately no
foreign key. **`PERSON` is the one argument kind the repoint duty still reaches**
([D-109](../decisions/round-13.md#d-109--nothing-a-rule-names-is-deleted-deprecated-hidden-disabled--and-a-tab-instead-of-a-report)):
retiring an office, a group or an audience is one write to that row and no expression is edited, because
nothing a rule names is deleted — it goes `deprecated`, `hidden` or `disabled`, and only `disabled` changes
the answer. A person is not in that protected set, because
[D-088](../decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)
lets a redaction require the row to actually go and **erasure wins**. So a merge repoints the `PERSON`
leaves naming the absorbed person, a redaction leaves the rest resolving to the empty set, and **a redacted
person is the only remaining way to produce a broken leaf** — shown on the permissions tab rather than in a
report nobody opens, with the nightly orphan scan as backstop rather than mechanism.
`PERSON`, `ROLE`, `GROUP` and `AUDIENCE` are the four codes whose argument names a person, an office, a group
or another audience. The fifth drawn edge, to `event`, belongs to the
item-bound codes — `ORGANIZERS`, `PLACED`, `CONFIRMED`, `ATTENDED`, `ON_WAITLIST` — whose argument is
optional exactly because the item being checked usually supplies it
([D-102](../decisions/round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)).

See [../data-model/05a-audience-and-grammar.md §8](../data-model/05a-audience-and-grammar.md#8-audience--grants-that-target-a-set-of-people)
and [../domain/06-authorization-model.md §6](../domain/06-authorization-model.md#6-the-resolver).

---
