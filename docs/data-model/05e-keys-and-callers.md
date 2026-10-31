# Data Model — Authorization: keys, and a caller that is not a person

`api_key` — the one table for a caller that is nobody. What it can hold, what it can never hold, and how
a call made with one is checked by the same resolver everything else uses. Decisions:
[round 16, D-116 … D-124](../decisions/round-16.md).

**Section numbers are shared across the six parts** and never renumbered, because other
pages cite them by number and their anchors are built from them: [05-authorization.md](05-authorization.md) holds §1–§7, [05a](05a-audience-and-grammar.md) §8 (the `audience` table, the grammar, the selector registry), [05b](05b-expression-tree.md) §8 continued (the tree and what each operand costs), [05c](05c-access-log-and-resolver.md) §9–§10 (`access_log` and the resolver), [05d](05d-invariants-and-seed.md) §11–§13 (invariants, seed data, open issues), and [05e](05e-keys-and-callers.md) §14–§17 (keys).

---

## 14. `api_key` — a caller that is nobody

An integration that calls this system is **registered here, by a named person, and is a grantee** — a
thing a permission is held *by*, in the same sense a person is
([D-116](../decisions/round-16.md#d-116--a-caller-that-is-not-a-person-is-a-registered-key-and-a-key-is-a-third-grantee-kind)).
It is not an account, which is a way for a person to log in; it is not an office, which is held by a
person and confers nothing; it is not a selector, and no expression can name one (§15).

Until this table existed the design had machine writers and no word for one: `created_by` was "absent for
system and import jobs", `access_log.actor_person_id` was "absent for system actions", and the audit
trigger treated an empty request context as *no actor, not an error*. **That NULL is what this table
replaces** — for the calls an outside system makes. **What this system does to itself keeps the empty
column**, which is read as a complete answer to *who did this* and named, where the trail has a label
column, from a fixed list (§17,
[D-125](../decisions/round-17.md#d-125--an-empty-actor-column-is-this-system-acting-on-its-own-and-its-name-comes-from-a-fixed-list)).

**Fields**

| Field | Kind | Notes |
|---|---|---|
| `id` | integer identity | Surrogate key. |
| `code` | text, required | A stable name — `accounting`, `bank_feed`, `camp_site`. **Unique among live rows.** Grants, audit rows and the report all name an integration by this, and it is the only part of the row a human is meant to remember. |
| `name`, `description` | text, optional | What it is for, in words a person will still understand in three years. |
| `secret_hash` | text, required | The only secret held, and only ever as a hash. Presented once, at `api_key.create` or `api_key.rotate`, and unreadable afterwards. **Unique among live rows**, because a request's lookup is "given this secret, which key is this". A key with nothing to check against cannot exist — the rule is borrowed from [`account_credential`](01a-accounts-and-contacts.md) verbatim, because it is right. |
| `valid_from` | date, required | Default today. |
| `valid_to` | date, optional | Absent = current, which is the normal case — see [D-120](../decisions/round-16.md#d-120--a-key-outlives-whoever-created-it-and-the-report-is-the-control). An expiry is allowed and is not required. |
| `last_used_at` | timestamp, audit time, optional | The only field that answers "has this been used since we rotated it", which is the question an incident asks. **Not a permission answer** — see §16. |
| `owner_person_id` | reference to `person`, optional | Who to telephone when this stops. **A contact, not a channel:** nothing reads it to decide an answer, and it is not the creator. |
| `created_by` | reference to person, required | Who installed this integration. Required, because installing a permanent outside authority is the most sensitive write this module offers. **Attribution for an act, not a dependency of the authority** (§15). |
| `created_at`, `updated_at`, `updated_by` | audit | Standard columns ([00-conventions §7](00-conventions.md)). |
| `revoked_at`, `revoked_by`, `revoke_reason` | timestamp; reference to `person`; text | Copied in shape from `access_grant`'s revocation triple, including its rule: a revocation names who made it. |

**Rules**

- `code` and `secret_hash` are each unique among live rows. The `secret_hash` one is a lookup before it
  is a constraint: two live keys answering the same secret would make "which integration was this"
  unanswerable at the moment it matters.
- `valid_to` is either absent or strictly after `valid_from`.
- A revocation names who made it: if `revoked_at` is set, `revoked_by` is set.
- **Nothing is derived from `created_by`.** Not liveness, not a check, not a report's judgement. The
  creator's account being suspended, their membership lapsing, a `deny` written against them and their
  leaving all change nothing about this row
  ([D-005](../decisions/round-01a.md#d-005--permissions-are-grants-never-derived-from-identity)'s
  "a permission is never derived from an identity", applied where it had never been pointed).
- **A key is a business table and is audited like one** — it is inside
  ["every remaining business table"](06-audit-and-import.md) with no amendment. Its insert and rotate rows
  carry `secret_hash` in their images, and that key is **already** on the credential list stripped before
  the audit row is written, which names `secret_hash` "and the integration secrets beside it". **No
  redaction rule is added here, because the one that was needed already existed.**
- `secret_hash` never leaves the row: not in a report, not in an export, not in a log line. The report of
  §15 prints `code`.

**Indexes**

- Live rows by `secret_hash` — the request path, and the uniqueness rule, in one index.
- Live rows by `code`.
- Keys by `owner_person_id`, for the report only.

**Why one row is both the caller and the secret.** The alternative was a caller row with dated secret rows
under it, exactly as an `account` has `account_credential`s, and it was refused
([D-119](../decisions/round-16.md#d-119--a-key-is-one-row-holding-one-live-secret-and-it-rotates-in-place)).
What it costs, said once so it is not rediscovered: **there is no rotation window** — the instant the hash
is replaced the old secret stops working, so rotating is a coordinated act; and **there is no history of
past secrets**, so "was this read with the secret we have since rotated?" always answers *this row*, which
is the one question `account_credential`'s dated rows would have answered. What is kept instead is that a
rotation moves no grant and no audit reference, and that `last_used_at` answers the question that actually
gets asked during an incident.

---

## 15. What a key may hold

**A key is a third grantee kind.** `access_grant` gains `api_key_id`, and the rule
[§6 states](05-authorization.md) is **exactly one of `person_id`, `audience_id` and `api_key_id` is set**.
Everything else about a grant is unchanged: one code, an effect of `allow` or `deny`, a scope, a period, a
`granted_by` who is a person.

Four consequences, and one of them is the reason this page exists:

1. **A key is never inside an expression.** No selector names one, no `audience_operand` may hold one,
   and the selector registry keeps its thirteen rows. `EVERYONE` is "any person, including those with no
   account and no membership" and a key is not a person, so it is in nobody's set — including its own.
   The machinery this preserves is not small: a key has no expression, so there is nothing to compile,
   and `ruleset_version`'s bump trigger stays `audience_operand` plus `selector_type` with no third table
   ([D-117](../decisions/round-16.md#d-117--a-key-is-never-inside-an-expression-thirteen-selectors-and-none-of-them-can-name-one)).
2. **Two of the three channels of authority cannot fire for a key.** Ownership compares a person's id
   against a row; guardianship needs an actor who is a party to a `guardianship` row. Neither is refused
   by a new rule — neither is reachable, because each is a comparison against a person. A key's authority
   is its grants, in full and only.
3. **A deny on a person does not slow a key down.** Deny is absolute, but it defeats the allows of the
   grantee it names, and a key is a different grantee
   ([D-118](../decisions/round-16.md#d-118--the-two-channels-that-compare-people-cannot-fire-for-a-key-and-a-deny-on-a-person-does-not-slow-a-key-down)).
   Safeguarding review therefore reads one grant list that contains two kinds of grantee, which is why
   the permissions page's tabs list keys beside people (§15's last paragraph).
4. **A grant to a key is never a delegation.** The existing audience rule is the model: `is_delegated`
   requires `delegated_from`, which is a person, and lending authority to a set is not a coherent act —
   *if `api_key_id` is set, `is_delegated` is false.*

**Codes a key may never be granted, refused when the grant is saved and counted by integrity check 20:
`system.admin` and all four `api_key.*` codes.** A bearer secret holding *everything* is the whole
organization in a request header; a key holding `api_key.create` can mint its own replacements, and
rotating a stolen key then means finding rows a thief created rather than rows a person created. One
sentence covers both: **a key may not change what a key can do, and may not become everything.** Like the
`.admin` assertion in check 17, the refused set is **an equality against named codes, not a set derived
by rule** — an allow-list is where a wildcard comes back to life.

**The four codes the resource owes** — [D-104](../decisions/round-10b.md#d-104--a-permission-codes-last-segment-is-an-action-and-a-registry-that-prose-contradicts-is-a-fiction)'s
grammar satisfied with no exception, and the full rows in
[the catalog](../appendix/permission-catalog-a-codes.md):

| Code | `right_kind` | `applies_to` | Grants |
|---|---|---|---|
| `api_key.view` | `read` | `unit` | Which keys exist, what each is granted, when each was last used |
| `api_key.create` 🔒 | `write` | `unit` | Register a key; mints the secret and shows it once |
| `api_key.rotate` 🔒 | `write` | `unit` | Replace a live key's secret; shows the new one once |
| `api_key.end` 🔒 | `write` | `unit` | Set `valid_to`, or revoke now |

**`api_key` is not in `grant_scope_type`, so a key is not a grantable item.** The catalog owes a new
resource four things and this one is paid three: codes, a `right_kind` each, an `applies_to` each — and
**no scope row, deliberately**
([D-122](../decisions/round-16.md#d-122--what-a-key-owes-the-catalog-four-codes-at-the-unit-and-the-fourth-owed-thing-declined)).
The control that would have bought, *"rotate the accounting key and no other"*, is therefore not
writable: **anyone who may issue a key may issue any key.** That is accepted at this scale, and it is
recorded as an unpaid debt rather than as a design feature — if it is ever reversed, the fourth owed thing
is the thing to add.

**Who may hold these four.** No seeded office carries them, and none should: whoever holds
`system.admin` already satisfies these checks, because `system.admin` satisfies every code
([D-124](../decisions/round-16.md#d-124--two-defects-systemadmin-satisfies-every-code-and-one-prose-code-named-no-row))
— which is exactly why the three writes among them carry 🔒. `api_key.view` carries no mark, on the
precedent of `role.view` and `permission.view`
([the catalog's §8b](../appendix/permission-catalog-a-codes.md#8b-keys--a-caller-that-is-nobody)). The
capability to install a permanent outside authority is a capability to escalate, and it arrives through
the one grant channel like every other code. **There is no second route to it, and no seeded office that
quietly has it.**

---

## 16. How a call made with a key is checked

**One resolver, and the key's entry point takes fewer arguments than the person's.** §10 of
[05c](05c-access-log-and-resolver.md) is the implementation and it is not duplicated here; what belongs
here is the signature and the refusal inside it:

```
can_key(api_key, permission_code, scope_type, scope_id, at)   → allowed | denied
```

No `owner_person_id`, and no person of any kind
([D-121](../decisions/round-16.md#d-121--a-key-never-carries-a-persons-authority)). That is not an
omission to be filled in later: the parameter *is* the impersonation vulnerability, because a claimed
person would make the trail's word for who acted an input, and this design's `on_behalf` exists precisely
to be "true, explicitly — **not inferred from the two ids differing**". A key has no channel to infer
from, so a claimed person would be exactly that — claimed. **A request authenticates as a person or as a
key, never as both**, and in both audit trails `actor_person_id` and `api_key_id` are mutually exclusive.

**Channels are unchanged, and there is no seventh one.** A check answered for a key records `unit_grant`
or `item_grant` exactly as one for a person does, and `authorization_ref_id` still names an
`access_grant.id` — so **no new reference-less polymorphic key is introduced here**, and the two this
model already has stay the two. The channel enum's own note already says that `system` "was never a
channel rather than a namespace"; a key is not a channel either. **What the trail adds is who, not how.**

**Invariant 19 now reads "a caller".** It forbade any row mapping **a person** — or a person and a code,
or a person and an item — to a permission answer, and as written a table keyed by `api_key_id` and
`permission_code` holding a boolean would not have been forbidden by it. "The integration's permissions"
is the most natural cache in this system to write and it is precisely a current answer, so the invariant's
subject is now **a caller, a person or a key**
([D-123](../decisions/round-16.md#d-123--invariant-19-reads-a-caller-not-a-person)). `last_used_at` is
not such a row and is named as permitted beside the three shapes §11 already permits: it is a timestamp
about an event that happened, and nothing reads it to decide whether to allow something now. A column
named `api_key.last_checked_permission` would be, and is the shape the review looks for.

**Who enforces what** — [00-conventions §6a](00-conventions.md), because a machine is exactly the writer
that was never written:

| Rule | Layer |
|---|---|
| `secret_hash` present, `code` and `secret_hash` **each** unique among live rows, `valid_to` after `valid_from` | migration-level constraint — the invariant, and now naming both columns rather than the one D-130 found missing |
| `api_key_id` set on a grant means `is_delegated` false; a grant never sets two grantees | model validation at the save, and check 1's shape report is the net |
| A grant of a refused code to a key | **the save path only** — no constraint spans `permission` and `access_grant`, so check 20 is the entire net |
| `api_key_id` and `actor_person_id` never both set on a trail row | migration-level constraint on each trail |
| A live key nobody has used, or whose owner has no live account | nightly report — a convention, and §15's tabs are where it is read |

---

## 17. What is not designed here

Stated because a reader will otherwise assume the nearest mechanism applies.

- **What this system does to itself is not a caller and has no row.** The 1 January membership sweep, payload
  reduction, migrations and the bank statement pull write rows with an empty actor column, which is read as
  the system acting on its own and is a complete answer to *who did this*; where the audit trail keeps a
  label, it is one of six from a list rather than free text
  ([00-conventions §7a](00-conventions.md#7a-what-an-empty-actor-column-means),
  [D-125](../decisions/round-17.md#d-125--an-empty-actor-column-is-this-system-acting-on-its-own-and-its-name-comes-from-a-fixed-list)).
  **`api_key` was deliberately not stretched to cover them**: a sweep is not a caller, and a table whose rows
  may or may not carry a secret is a table whose invariants become conditional.
- **Break-glass is a report and a procedure, not a mechanism**
  ([D-126](../decisions/round-17.md#d-126--break-glass-is-a-report-and-a-written-procedure-not-a-mechanism)).
  A key is not a person, carries nobody's authority and may never hold `system.admin`, so it cannot stand in
  for somebody who cannot log in; what it can do is nothing, which is why the answer is check 9's second
  column and a written procedure
  ([domain/02 §3](../domain/02-actors.md#when-nobody-who-can-hold-systemadmin-can-sign-in)).
- **The outbound direction is [F-27](../open-questions.md#f-27).** Everything here is a caller arriving.
  Anything this system initiates — an accounting export, a refund, a webhook (a mechanism this corpus
  deleted rather than deferred) — has no design, and the one refusal that cited "a second integration with
  its own authorization" as a reason now has a mechanism to point at
  ([07-finance.md §2b](07-finance.md)).
- **Nothing about the wire.** How a secret is presented, what it looks like, how it is hashed, how a
  session is carried after a person logs in — API layer, and [D-072](../decisions/round-06.md#d-072--the-documentation-carries-no-sql-the-schema-is-the-orms-job)
  is the standing division. What is decided here is only what may be stored: a hash, and nothing else.
- **No rate limiting, no IP allowlist.** Either would be a second, weaker authorization implementation,
  which [domain/06 §10](../domain/06-authorization-model.md) rejects because "they diverge; the weaker one
  becomes the exploit". A rate limit is an availability measure and earns no permission code.
- **No anonymous caller.** A public read of published facts is an integration with a key granted
  specifically those codes — there is no fourth kind of caller, and nothing in this design grants
  anything to a request that authenticated as nobody.
