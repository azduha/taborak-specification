# Decision Log — Refinement round 16 (D-116 … D-124)

> A caller that is not a person is a registered key, a key is a grantee, and the two audit trails stop calling it NULL.

[Refinement round 15 (D-115) ←](round-15.md) | [All decisions](index.md)

**What was asked, and what the answers did.** The question put to this round was "system-level API
access", which turned out to be four questions wearing one name: what an outside system that calls in
*is*, what our own clients are, what the writes this system already performs to itself are, and what
somebody does when nobody can log in. Two were chosen and two were declined. **An outside system
calling in, and our own clients talking to our API, are in scope**; naming the corpus's own authorless
writes and a break-glass way in are not, and are registered as
[F-25](../open-questions.md#f-25) and [F-26](../open-questions.md#f-26) rather than guessed at.

**The finding the whole round hangs on is that this design already has a machine actor, and its name is
NULL.** Three pages write as though one acts: `created_by` is "Absent for system and import jobs"
([00-conventions.md §7](../data-model/00-conventions.md)), `person_group.created_by` "is NULL for system
jobs" ([02-organization.md §2](../data-model/02-organization.md)), and `access_log.actor_person_id` is
"Absent for system actions" ([05c.md §9](../data-model/05c-access-log-and-resolver.md)). The audit
trigger reads the actor out of the request context and states that an unset or empty value means no
actor, not an error ([06-audit-and-import.md §2.1](../data-model/06-audit-and-import.md)). And one rule
already gives orders to this unnamed agent: a guardianship's `valid_to` is "**Never by a job**"
([04-relationships.md §1](../data-model/04-relationships.md)). A corpus whose own rule against a silent
NULL is that "a nullable one whose null-ness silently means something is how the guardianship channel
would have acquired an answer that depends on a value nobody typed"
([05-authorization.md §2](../data-model/05-authorization.md)) had a NULL of exactly that shape in its
standard columns all along. What this round mostly does is **give that NULL a row**.

**One thing this round found out by being wrong, recorded so it is not repeated.** A survey during this
round reported that no credential mechanism exists anywhere in the corpus. It does, and has since round
1: [`account_credential`](../data-model/01a-accounts-and-contacts.md) carries `credential_type`, a
`secret_hash`, `valid_from`, `valid_to` where `NULL` = current, `last_used_at` and `revoked_reason`,
under the rule that "a credential with nothing to check against cannot exist". That table is the nearest
cousin of everything decided here, and [D-119](#d-119--a-key-is-one-row-holding-one-live-secret-and-it-rotates-in-place)
is deliberately shaped against it — including in the one place where it departs from it.

---

## D-116 — A caller that is not a person is a registered key, and a key is a third grantee kind

**Status:** decided (from your answer)
**Date:** refinement round 16
**Narrows:** the **API and UI** row of
[open-questions.md §H](../open-questions.md#h-not-yet-designed), which read "Not started". The
authorization half of that layer is now specified; its transport is not.
**Amends:** the grantee shape of a grant, stated in
[D-006](round-01a.md#d-006--per-item-permissions-are-capabilities-on-the-item)'s surviving form and in
§6 of `05-authorization.md`. **Reverses nothing.**
**Stands beside:** [D-100](round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape),
which settled that an office is held by "one person, never a rule". This is that ruling read from the
other end: a caller is one row, never a set.

**Decision. A machine that calls this system is recorded, and it is a grantee.** A new table `api_key`
([05e](../data-model/05e-keys-and-callers.md)) holds one registered caller. `access_grant` gains
`api_key_id` beside `person_id` and `audience_id`, and the grantee rule becomes **exactly one of the
three is set**. A key is therefore a thing a permission is held *by*, in the same sense a person is, and
through the same single channel as everyone else — [D-005](round-01a.md#d-005--permissions-are-grants-never-derived-from-identity)
is unchanged and unexceptioned: a key's authority is grants, and nothing about a key derives one.

Four parts of that sentence are load-bearing:

1. **It is registered, in the system, by a named person.** `created_by` on `api_key` is a required
   reference to `person`. The catalog's whole safety posture is that a sensitive write is held by a named
   adult, and installing a permanent outside authority is the most sensitive write this module offers.
2. **It is a grantee, not a scope.** A key is not something a permission is granted *on*; see
   [D-122](#d-122--what-a-key-owes-the-catalog-four-codes-at-the-unit-and-the-fourth-owed-thing-declined)
   for the one owed thing this round declines to add.
3. **It is not a person, and does not become one.** A `person` row holds identity — a body, a name, a
   birth date — and every operand in the audience language is a set of people, so a synthetic person row
   would land inside `EVERYONE`, which is "any person, including those with no account and no
   membership". See the refusals at the end of this round.
4. **The grantee columns are three; the channels are still three.** A key is reached through grants
   only — [D-118](#d-118--the-two-channels-that-compare-people-cannot-fire-for-a-key-and-a-deny-on-a-person-does-not-slow-a-key-down).

**Why a new grantee kind rather than a person standing in for the machine.** Because the alternative
was measured and it is worse in three specific places. If every machine call carries a person's
credential, then the audit trail names a human who did nothing, which is a trail that will be read
during a safeguarding investigation and will be wrong. A `deny` on that human stops the integration
outright, because deny is absolute
([D-032](round-02-03.md#d-032--deny-is-absolute-locality-orders-allows-only)) — a restriction written to
protect one child would silently stop money being matched. And the human leaves: this corpus already
knows the shape of that failure from [D-093](round-09.md#d-093--the-one-off-import-may-create-memberships-both-ends-dated)'s
account of an open-ended membership inherited from 1998, and a credential inherited from a person who
left in 2019 is the same hazard with a live secret on it.

**What is given up, stated plainly.**

- **The grantee shape has to be re-read everywhere it is stated.** Until this round a grant was written
  to a person or to an expression over people, and that sentence — in those words or close to them —
  appears on every authorization page, in both ERD renderings of `access_grant`, in both glossaries and
  in the catalog's own description of what a grantee is. Every one of them now has a third case, and a
  reader of any one of them can get the model wrong by missing it. This is the cost of the chosen shape
  and it was paid knowingly; the pages were swept and now say three.
- **A bearer secret is now an authority-holder.** A grant to a person can be withdrawn by suspending an
  account; a grant to a key is reachable only by ending the key or the grant, and a copied key is
  reachable by nobody until it is noticed. The mitigations are
  [D-122](#d-122--what-a-key-owes-the-catalog-four-codes-at-the-unit-and-the-fourth-owed-thing-declined)'s
  refusals and [D-120](#d-120--a-key-outlives-whoever-created-it-and-the-report-is-the-control)'s report,
  and neither is a guard.
- **Two things named a key and a person can no longer be conflated.** Nothing in this design can now
  say "the accounting system, acting as the treasurer". That is [D-121](#d-121--a-key-never-carries-a-persons-authority)
  and it is wanted, but it costs a use case, which is written there rather than here.

**Where this is written in the docs.** [05e](../data-model/05e-keys-and-callers.md) is the new page and
holds the table, the rules and the refusals. [05-authorization.md §6](../data-model/05-authorization.md)
carries the amended grantee rule and the two rules that follow from it.
[domain/06 §10a](../domain/06-authorization-model.md) is the domain statement.
[05c.md §10](../data-model/05c-access-log-and-resolver.md) says how a call is checked without a second
resolver.

---

## D-117 — A key is never inside an expression: thirteen selectors, and none of them can name one

**Status:** decided (from your answer)
**Date:** refinement round 16
**Closes nothing.** **Preserves:** [D-101](round-10b.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree),
[D-103](round-10b.md#d-103--an-audience-may-name-another-audience),
[D-105](round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other) and
[D-114](round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation)
all stand untouched, and this entry is the reason none of them had to change.

**Decision. The expression language does not learn the word.** No selector is added, so the seeded
`selector_type` registry keeps its thirteen rows. No `audience_operand` may name a key in either of its
reference arms. An audience is a set of people and a key is not in any of those sets, including
`EVERYONE`, which is defined over people and reads "any person, including those with no account and no
membership".

**Why this is a decision rather than an omission, and what it buys.** The cheap way to make a machine
fit an existing model is to make it a member of something, and the model would have accepted it: a
fourteenth selector, an office for integrations, and `MEMBERS * ROLE(integrations)` grants every key the
same authority in one edit. That was refused on the same ground
[D-100](round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)
refused a rule-held office, only inverted: **an office is one named person and never a rule, and a caller
is one row and never a set.** The reason is the same reason it was given there — a set is the wrong
grain for a thing that must be individually revocable, and a stolen key must be stoppable without
deciding what else was in the set.

What it buys is that the largest machinery in this module was not touched. A key has no expression, so
there is nothing to compile and nothing to memoize about one; the compilation of
[D-114](round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation)
is still keyed by an expression root and a `ruleset_version` and still holds no caller; and
`ruleset_version`'s bump trigger stays exactly what round 14 left it — `audience_operand` and
`selector_type`, no third table. **Anyone adding `api_key_id` to that trigger has misread this entry.**

**What is given up, stated plainly.** **A grant to integrations cannot be written in one sentence.**
Twelve integrations that all read events need twelve grants, and adding a thirteenth is a write, not an
edit to one rule. That is genuinely more work than the selector would have been, at this system's scale
it is a dozen rows
([D-112](round-13.md#d-112--the-systems-scale-is-stated-hundreds-of-people-tens-of-registrants-per-event)),
and the asymmetry is the point: adding a key is meant to be an act somebody performs. The second loss is
quieter — **a key cannot be *removed* from a set either**, so there is no "take integrations out of
everything `MEMBERS` touches" lever, and an organization that wants that posture edits twelve grants.

---

## D-118 — The two channels that compare people cannot fire for a key, and a deny on a person does not slow a key down

**Status:** decided (as a consequence of D-116, recorded because the consequence is frightening)
**Date:** refinement round 16

**Decision. A key's authority is its grants, in full and only.** Of the three channels of authority in
[domain/06 §1](../domain/06-authorization-model.md), a key can be reached by one. Ownership compares a
person's id against a row, and a key has no id that any row holds. Guardianship requires an actor who is
a party to a `guardianship` row, and no such row names a key. Both channels are therefore not refused by
a new rule; they are **unreachable**, because each of them is a comparison against a person.

**`authorization_channel` gains no seventh value.** The enum is six values and its own note says that
`system` "was never a channel rather than a namespace"
([05c.md §9](../data-model/05c-access-log-and-resolver.md)); the same holds here. A check answered for a
key records `unit_grant` or `item_grant` exactly as a check for a person does, because the channel names
*how authority was obtained*, not who asked. This matters: the audit question "by what authority did this
happen?" keeps one answer-shape for every caller.

**The consequence, written out where it cannot be missed.** **A deny written against a person has no
effect whatsoever on a key.** Deny is absolute and defeats every allow — but it defeats the allows of
the grantee it names, and a key is a different grantee. So the instrument this design reaches for first
when somebody must stop reading children's records reaches one grantee and not the others. Symmetrically,
**a guardianship can never authorize a key**, which is the direction nobody was worried about.

Two controls cover this, and neither is a guard in
[D-081](round-06.md#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now)'s
sense:

- **the permissions page's tabs list keys beside people** — the *Unusual* tab gains live keys and what
  they hold ([D-109](round-13.md#d-109--nothing-a-rule-names-is-deleted-deprecated-hidden-disabled--and-a-tab-instead-of-a-report)'s
  decision that the answer to a standing report is a tab where the person writing the rule already is),
  so a safeguarding review that reads the grant list reads one list, not two;
- **[D-122](#d-122--what-a-key-owes-the-catalog-four-codes-at-the-unit-and-the-fourth-owed-thing-declined)'s
  refused codes** keep a key from holding everything, or from holding the power to hand out keys.

**What is given up, stated plainly.** Safeguarding now has a second list to review, and the property
"one row anywhere can stop this person" is gone: it was always per-grantee, and there is now a second
kind of grantee. An organization that wants a single stop-everywhere lever across people and keys would
need a deny that names a subject rather than a grantee, which is a different instrument than the one this
corpus has, and adding it is not in this round.

---

## D-119 — A key is one row holding one live secret, and it rotates in place

**Status:** decided (from your answer: one table, the key is the grantee, rotation in place)
**Date:** refinement round 16
**Models itself on:** [`account_credential`](../data-model/01a-accounts-and-contacts.md), and **departs
from it in exactly one way**, named below as the loss it is.

**Decision. The granted thing and the secret are the same row.** `api_key` carries a `code` (stable, so
that a grant and an audit row can name the same integration across years), a `secret_hash` — required,
checked against and never stored readable, "a credential with nothing to check against cannot exist" is
borrowed from `account_credential` verbatim because it is the right rule — `valid_from`, `valid_to` where
absent means current, `last_used_at`, the revocation triple copied from `access_grant`, `created_by`
required, and an optional `owner_person_id` that is a contact and nothing else. **Rotating replaces the
hash on the row.** One live secret per key, because one row is one caller.

**Why one row and not a caller with dated secrets beside it.** The alternative — an `api_client` as
grantee with dated `api_key` rows under it, exactly as an `account` has `account_credential`s — was
offered and refused. Its case is honest: it is the corpus's own idiom, and it buys a rotation window in
which two secrets work, plus `account_credential`'s property that a revoked credential "stays as a row,
so 'was this account ever accessed with a credential that has since been revoked?' is answerable". What
it costs is that **every grant would then sit one join away from the thing that was actually
compromised**, and the audit trail would have to name two rows to say who acted — the caller and the
secret it used. With one row, `audit_log.api_key_id` is simultaneously "which integration" and "which
secret", and rotating does not move a single grant or a single historical row. At twelve integrations the
window it buys is a coordination problem, not a safety property.

**The losses, all three of them.**

1. **There is no rotation window.** The instant the hash is replaced, the old secret stops working.
   Rotating is therefore a coordinated act with whoever holds the secret, and a partner that has not
   updated is locked out between the two moments. Nothing in this design can make that window smaller
   than the humans involved.
2. **There is no history of past secrets, and one question is now unanswerable**: *"was this record read
   with the secret that has since been rotated?"* The answer is always the same row, because the row
   survives rotation. `account_credential`'s dated rows would have answered it. This is the precise
   thing given up by the chosen shape and it is given up knowingly; what is kept in its place is
   `last_used_at` (which answers "has this key been used since the rotation", which is the question that
   is actually asked during an incident) and the fact that ending a key is still a dated row.
3. **One integration with two channels needs two sets of grants.** A partner that reads one API and
   writes another cannot share one identity across both without sharing one secret, which is worse.
   Two keys, two grant lists.

**The secret is already handled by a rule that predates this round.** Credential material is stripped
from audit images **on the way in, never by a cleanup job that might not run**, and the list it is
stripped by already names `secret_hash` "and the integration secrets beside it"
([06-audit-and-import.md §2.2](../data-model/06-audit-and-import.md)). So an `api_key` insert or rotate
audits itself like any other business write — `api_key` is a business table and is inside "every
remaining business table" with no amendment — with the hash already replaced by the marker. **No new
redaction rule is needed, and none is added.** That the list was written before any integration secret
existed is the one place this corpus legislated for this round in advance.

**How the secret identifies its key** is the same trick `account_credential` uses for `oauth`: `secret_hash`
is unique among live rows, because the lookup a request performs is "given this secret, which key is
this", and the index that makes that fast is the same index that enforces it. How the secret is
*presented* — header, format, hashing choice, anything on the wire — is API layer and not this
repository's, which is [D-072](round-06.md#d-072--the-documentation-carries-no-sql-the-schema-is-the-orms-job)'s
standing division.

---

## D-120 — A key outlives whoever created it, and the report is the control

**Status:** decided (from your answer: created in the system, does not expire with its creator, may carry
an expiry of its own)
**Date:** refinement round 16
**Depends on:** [D-005](round-01a.md#d-005--permissions-are-grants-never-derived-from-identity), which
this entry does not extend so much as apply somewhere it had never been pointed.

**Decision. Nothing about a key is derived from its creator.** `created_by` is required and names the
person who installed the integration, and it is **attribution for an act, not a dependency of the
authority** — the same words `event.created_by` already uses: "`created_by` is attribution, and a
permission is never derived from an identity". So the creator's account being suspended changes nothing,
their membership lapsing changes nothing, their leaving the organization changes nothing, and a `deny`
written against them changes nothing. A key ends when a person ends it, or when the `valid_to` somebody
chose to write arrives.

`valid_to` is **optional and absent by default**, which is this corpus's existing posture for an
authority that nothing forces to end: an open-ended row with a report underneath it
([D-071](round-05.md#d-071--nothing-forces-a-role-assignment-to-end-the-gate-and-the-report-are-the-control)).
**A mandatory expiry was offered and refused.** A delegation is the case where an end date is enforced
("a delegation must expire", §6 of `05-authorization.md`), and a key is not a delegation — a delegation
lends authority a person already has, and there is no person here to lend it. Making a key expire on a
date would have bought a stopped integration on a date, with the failure surfacing wherever the
integration writes: for a bank feed, in the unmatched-money queue days later.

`owner_person_id` is optional and is **a contact, not a channel**: "who do we telephone when this stops"
— and nothing whatsoever reads it to decide an answer, so it cannot become a back door to
creator-derived authority. A live key whose owner has no live account is a row on the report.

**The report.** The permissions page's *Unusual* tab gains a line of keys, each with what it can do, when
it was last used, and whether its owner still has an account. **There is deliberately no age threshold**
— not "keys older than 13 months" — because a bound somebody may want to change belongs in a column and
a job containing the literal `60` has quietly reverted a parameter to a constant
([03-membership.md §9](../data-model/03-membership.md)); this one has no column, so the report prints an
age and a person decides whether it is old. Adding a threshold column later is a decision, not a
configuration.

**What is given up, stated plainly.** **A forgotten key is live forever unless somebody reads a list, and
a copied secret cannot be recalled.** For an ordinary grant, open-ended-with-a-report is a mild risk: a
forgotten grant row helps nobody until somebody authenticates. A key is different, because the bearer
already has the thing. The report is therefore load-bearing in a way D-071's report is not, and that
asymmetry is the price of choosing an integration that does not quietly stop working. The other loss is
administrative: **there is no "keys belonging to X" query that means anything**, because the creator is
deliberately not an owner, and the only grouping that means something is `owner_person_id`, which is a
contact a person may have left blank.

---

## D-121 — A key never carries a person's authority

**Status:** decided (from your answer, chosen over allowing it and marking it)
**Date:** refinement round 16
**Protects:** [`access_log.on_behalf`](../data-model/05c-access-log-and-resolver.md) and
`audit_log.on_behalf_of`, whose existing rule is that the flag is "true, explicitly — not inferred from
the two ids differing" ([04-relationships.md §5](../data-model/04-relationships.md)).

**Decision. A request is authenticated as a person or as a key, never as both.** In both trails,
`actor_person_id` and `api_key_id` are mutually exclusive; a row carrying both is illegal, and `on_behalf`
/ `on_behalf_of` is never set on a row whose actor is a key. Correspondingly the resolver entry point for
a key **takes no owner parameter at all** ([D-116](#d-116--a-caller-that-is-not-a-person-is-a-registered-key-and-a-key-is-a-third-grantee-kind)'s
`can_key` in [05c.md §10](../data-model/05c-access-log-and-resolver.md)) — there is nothing to pass a
claimed person in.

**Why this needed a rule of its own rather than falling out of the model.** Mechanically, a caller-named
person is nearly free: add an optional parameter and the resolver has plenty to do with it. What it would
actually have done is **turn the trail's word for who acted into an input**. `on_behalf` is defined
against inference precisely because guardianship and delegation are channels, so the system can derive
the relationship rather than accept it; a key has no channel to derive from, so a claimed person would
be exactly that — claimed. And the harm is the obvious one: **a copied bearer secret would read any
child's record by typing that child's id into a field**, while the trail said a person did it. The
strongest property this design has over a log-less system is that its trail cannot be told a story, and
that property dies in one optional parameter.

**What is given up, stated plainly.** **An outside system that acts *for* a person must carry that
person's own credential** — a partner app whose members log in into it calls us with the member's
credential, one more round trip and, for a member of that partner who has no account here, an account.
The alternative is the write happening as the key with no person actor, which the trail records honestly
and which a safeguarding reader will read as "the accounting system changed this child's row" — and
sometimes that is the truth, and sometimes it is not good enough, which is the case this refusal costs.
It is also the case that
[F-27](../open-questions.md#f-27)'s outbound direction will meet again from the other side.

---

## D-122 — What a key owes the catalog: four codes at the unit, and the fourth owed thing declined

**Status:** decided (from your answer: unit-only, no new grantable item type)
**Date:** refinement round 16
**Pays off:** the catalog's rule that **each new resource owes the authorization module four things** —
codes, a `right_kind` each, an `applies_to` each, and a row in `grant_scope_type`
([permission-catalog-b §10](../appendix/permission-catalog-b-roles-and-open-issues.md)). **Three are
paid; the fourth is declined on purpose**, below, so the debt is visible rather than forgotten.

**Decision. Four codes, resource `api_key`, no `system.` prefix, all `applies_to = unit`.**

**Why no prefix, since the codes administer a table the system keeps.** `permission.namespace` is `system`
or absent, and `permission.resource` is required to equal the code's first segment with `system.` as the one
exemption ever granted ([05-authorization.md §2](../data-model/05-authorization.md#2-permission)). `api_key`
is a stored table, so the first segment already *is* the resource and a prefix would be a second, drifting
copy of a name the code already carries. **And a prefix would buy nothing, because after D-124 a namespace
routes nothing at all** — the resolver stopped branching on the prefix, so the only work left for these four
codes' unit-only reach is done by `applies_to`, which the save path checks. The precedent is in the catalog
already and is stronger than any argument here: `access_grant.create`, the act that turns a code into
somebody's authority, carries no namespace either.

| Code | `right_kind` | Grants |
|---|---|---|
| `api_key.view` | `read` | See which keys exist, their `code`, what they are granted, and when each was last used |
| `api_key.create` 🔒 | `write` | Register a key, which mints its secret and shows it once |
| `api_key.rotate` 🔒 | `write` | Replace a live key's secret, which shows the new one once |
| `api_key.end` 🔒 | `write` | Set `valid_to`, or revoke it now with a reason |

The naming grammar of
[D-104](round-10b.md#d-104--a-permission-codes-last-segment-is-an-action-and-a-registry-that-prose-contradicts-is-a-fiction)
is satisfied without an exception: every last segment is an act, and the first segment names stored
state — a table that now exists. **`rotate` appears once in this corpus already, in
[removed-concepts.md](../appendix/removed-concepts.md), as the last segment of `event.qr.rotate`** — a
code that never existed in any registry, deleted by D-104 for being prose-only. This row is not its
revival; the lesson of that deletion is *a name must have a row behind it*, and it has one here before it
has any prose.

**Codes a key may never hold, refused on the write path and counted by integrity check 20:
`system.admin`, and all four `api_key.*` codes.** The first refusal is the obvious one — a bearer secret
carrying *everything* is the whole organization in a request header, and `system.admin` is already not
delegatable and already alarmed on its holders. The second is the one worth stating as a rule rather than
a hunch: **a key may never hold a code whose act is about keys**, because a key granted `api_key.create`
can mint its own replacements, and rotating a stolen key then means finding rows that were created by the
thief rather than by a person. Together they are one sentence — *a key may not change what a key can do,
and may not become everything* — and, like check 17's list for `.admin`, **it is an equality against
named codes rather than a set built by rule**, because an allow-list is where a wildcard comes back to
life.

**No seeded office.** The seeded starter offices get none of these four. Whoever holds
`system.admin` already satisfies every one of these checks, because `system.admin` satisfies everything
([D-124](#d-124--two-defects-systemadmin-satisfies-every-code-and-one-prose-code-named-no-row)), which is
precisely why all four are marked 🔒: **the capability to install a permanent outside authority is the
capability to escalate, and it arrives by an ordinary grant like every other code** — there is no second
route, and no new seeded office that quietly has it.

**The declined fourth thing, and what it costs.** `api_key` is **not** added to `grant_scope_type`, so a
key is not a grantable item and these four codes cannot be granted on one key. The control that would
have bought — "rotate the accounting key and no other" — is therefore not writable, and anyone who may
issue a key may issue any key. That is the accepted shape at this scale: the four codes are four, the
population who may hold them is the population who hold `system.admin` today, and adding the item type
would widen
[05d §13's open question](../data-model/05d-invariants-and-seed.md) about a code and a scope shape
disagreeing by letting *any* item-scoped code be scoped to a key, which is meaningless for almost all of
them. **If this is ever reversed, the fourth owed thing is the thing to add** — that sentence exists so a
later reader finds the debt recorded rather than inferring it from an absence.

**The contrast with the one precedent this round had, stated because it cuts the other way.** Payload
reduction gets **no** permission code, on the grounds that "a permission for it would imply a person
choosing not to run it" ([permission-catalog-a §8](../appendix/permission-catalog-a-codes.md)). A key is
the mirror image: **it is chosen, installed, rotated and revoked by people, interactively, one at a
time**, so a code for each act says exactly what happened, and the alerting-check-instead-of-a-code
posture would be the wrong import. The two cases differ in whether a person decides, and the catalog now
shows both.

---

## D-123 — Invariant 19 reads "a caller", not "a person"

**Status:** decided (as a defect in the newest TIME-BOMB, found by writing this round)
**Date:** refinement round 16
**Amends:** [D-114](round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation)'s
invariant 19, whose **intent** is unchanged and whose **wording** had a hole the width of this round.

**The hole.** Invariant 19 forbids any row, table or field mapping **a person** — or a person and a code,
or a person and an item — to a permission answer. It is written entirely about a person, because when it
was written there was no other kind of caller. **A table keyed by `api_key_id` and `permission_code`
holding a boolean would not have been forbidden by it.** That is not a hypothetical: "the integration's
permissions" is the single most natural cache in this system to write, it would be written by someone
optimizing an integration under load, and it is precisely a *current answer*, which is the thing the
invariant says it looks for.

**Decision. The invariant's subject is a caller — a person or a key — and its three permitted shapes are
named in the same breath as a fourth refusal: no row maps a key, or a key and a code, or a key and an
item, to an answer.**

`api_key.last_used_at` is **not** such a row and says so in the page that carries it: it is a timestamp
about an event that happened, in the same class as the audit payloads the invariant already permits
("the second and third are records of an event"), and nothing reads it to decide whether to allow
something now. A column named `api_key.last_checked_permission` would be, and is the shape to look for.

**What is given up, stated plainly.** Nothing is gained and one thing is lost: **the invariant is a
paragraph, and now it is a longer paragraph.** It was already enforced structurally, with the residue
named as a convention rather than a guard — "nothing stops a team from adding a `permission_cache` table
again in a year, under load, at 2 a.m., because it is the obvious move". Renaming its subject from person
to caller widens the convention's reach without adding any enforcement, and every future cache proposal
now has to disprove one more sentence instead of noticing one less row.

---

## D-124 — Two defects: `system.admin` satisfies every code, and one prose code named no row

**Status:** decided (defect fix, not a design change)
**Date:** refinement round 16
**Closes:** nothing; the second defect is a fifth instance of the class
[F-19](../open-questions.md#f-19) exists to catch.

Two things in [05-authorization.md §2](../data-model/05-authorization.md) were wrong, found because this
round needed to know what `system.admin` means before deciding whether a key could hold it.

**1. `system.admin` satisfies a check for every code, whatever its namespace — and can only ever arrive
as a grant at the unit.** The resolver's rule was written with a trailing parenthetical, present **once in
the entire corpus**:

```
A check for permission 'X.y' is satisfied by:
    - an exact allow of 'X.y', OR
    - an allow of 'system.admin'   (NULL-namespace permissions only)
```

Read as written it qualifies *which checks `system.admin` satisfies*: only codes whose `namespace` is
absent. Since `role.assign`, `permission.edit` and `access_grant.create` all sit in the `system`
namespace, that reading means **the sole holder of `system.admin` cannot grant themselves an office,
cannot edit the catalog and cannot write a grant** — contradicting the catalog's own description of the
code ("Everything"), contradicting `05-authorization.md §6`'s "a unit grant of `system.admin` therefore
reaches everywhere on its own", and contradicting
[§2's own statement](../data-model/05-authorization.md) that the namespace selects no channel for any
namespace. Nine catalog codes were quietly unreachable for the most powerful holder in the system.
The parenthetical is **deleted** and the block now states the two facts that were meant: it satisfies any
code, and `applies_to = unit` is what keeps it out of an item grant — a column value checked when a grant
is saved, not a resolver branch, which is how the corpus already guarantees this.

**2. A prose example cited a code that does not exist.** The namespace table's Example cell read
`system.permission.edit`. The catalog's row is `permission.edit`
([permission-catalog-a §7](../appendix/permission-catalog-a-codes.md)). The invented code has one
occurrence corpus-wide, is granted by nothing, and names no row — F-19's exact defect class, and its
fifth instance in the registries this corpus has checked. Corrected to the real code; no other page
quoted it.

**What is given up, stated plainly.** Nothing, and it matters that the log says so: **this entry is not a
reversal and no property was traded.** Its value is the record that a single parenthetical, in the one
rule the whole authorization module leans on, survived fifteen rounds while contradicting two sentences on
its own page — which is what the hand-run diff report of F-19 was adopted for and did not catch, because
F-19's machinery compares **prose against the registry** and this contradiction was between two pieces of
prose.

---

## What this round changes elsewhere in the corpus

- **The refusal of automatic refunds now stands on one reason instead of two.** Auto-refund was refused
  partly because it "needs the bank integration to work outbound as well as inbound, which is a second
  integration with its own authorization" ([07-finance.md §2b](../data-model/07-finance.md)). **That half
  of the reason is now a mechanism rather than an absence.** The refusal stands on its other reason — it
  returns the grandparent's attempt at a camp contribution, which is a judgement — but the money half of
  `07-finance.md §7`'s accounting-integration question and the refund question now have somewhere to
  point. Registered as [F-27](../open-questions.md#f-27).
- **[05d §13's](../data-model/05d-invariants-and-seed.md) open question about the API refusing a check
  that names an item for a unit-only code** now has a second kind of caller to refuse, and its answer —
  "a refusal at the API layer naming the code and the scope" — is unchanged and is adopted for keys too.
- **The catalog's totals move by four**, in every place that counts codes rather than listing them.
- **The § map** at the head of `05d` gains the new page; `00-conventions.md §11`'s index of where each
  subject is described gains it too.
- **`grant_scope_type` keeps its rows unchanged** — see D-122 — and `ruleset_version` keeps its trigger
  unchanged — see D-117.

## What this round refused, and what it declined to answer

Refused, with the reason stated where it belongs:

- **A synthetic `person` row for an integration** — the cheapest thing that compiles, and the reason it
  will be reached for is exactly why it must be refused: it lands inside `EVERYONE` (every allow's
  widest operand), it appears in every safeguarding report as a person who may read children's records,
  and it becomes mergeable and redactable like a person.
- **A `client` row plus dated `credential` rows** — offered, priced, refused in D-119.
- **An IP allowlist or a rate limit as a form of access control** — either would be a second, weaker
  authorization implementation, which [domain/06 §10](../domain/06-authorization-model.md) already lists
  as an anti-pattern with the reason "they diverge; the weaker one becomes the exploit". A rate limit is
  an availability measure and belongs to no permission code.
- **A seventh `authorization_channel` value** — D-118.
- **A per-key answer row** — D-123.

Declined by your answer, and registered rather than guessed:

- **[F-25](../open-questions.md#f-25) — naming this system's own authorless writes.** The yearly
  membership sweep, payload reduction, migrations and the bank statement pull still name themselves in
  `audit_log.actor_label` as free text (`system`, `migration:0042`, `import_batch:17`), while a key now
  names itself as a reference. The asymmetry is real and the forensic-gap check now counts three ways
  instead of two, so it is covered rather than broken; it is not *named*.
- **[F-26](../open-questions.md#f-26) — a way in when nobody can log in.** Break-glass. Distinct from a
  permanent machine credential, and this round's key is a poor fit for it precisely because a key is not
  a person.
- **[F-27](../open-questions.md#f-27) — the outbound direction.** The accounting export question, the
  refund question, and anything that pushes rather than being pulled. The corpus has always had exactly
  one inbound flow and no outbound one, and it deleted the only push mechanism it ever discussed
  ([D-075](round-06.md#d-075--money-arrives-from-a-bank-api-a-payment-is-requested-by-variable-symbol-and-qr-code)'s
  webhook).

---

*This round is the first in which the system was given something to be besides a place people act. Its
largest risk is not the new table; it is that a grant now names a grantee who cannot be asked to stop,
and the pages that describe a grant as written to a person or an expression were corrected accordingly.*
