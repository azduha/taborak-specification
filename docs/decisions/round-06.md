# Decision Log — Refinement round 6 — the no-SQL round (D-072 … D-081)

> 4,689 lines of DDL deleted and every rule it carried restated as a requirement. The round that made the prose the specification.

[Refinement round 5 — the events module (D-058 … D-071) ←](round-05.md) | [All decisions](index.md) | [Refinement rounds 7 and 8 (D-082 … D-090) →](round-07-08.md)

---

## D-072 — The documentation carries no SQL; the schema is the ORM's job

**Status:** decided (from your answer) — **closes F-4a**
**Date:** refinement round 6

**Your answer.** Asked whether the permission catalog should be *generated from* the seed data
rather than maintained beside it, you answered **"Delete the schema, I will use ORM anyway."**

**The question was a symptom.** F-4a was about two lists disagreeing. The real cause is that the
documentation was asserting a deployment. It carried **4,689 lines of PostgreSQL across 19
files — 31% of the repository**: every `CREATE TABLE`, a `can()` function, trigger bodies,
91 `INSERT INTO permission` rows whose only purpose was to make a list executable, and one
integrity check whose entire job was to read `pg_proc` and grep a function definition for a
string. Under an ORM, not one of those lines would ever be run as written. Hand-written
migrations and ORM-generated migrations disagree about who owns the schema, and the docs
asserting DDL was the losing side of that argument before it started.

**Decision.** No SQL in the documentation. Field lists, types at the level of *what kind of
thing this is* (a period, an amount, an identifier), nullability, uniqueness, no-overlap rules,
temporality, indexes that exist for a reason, and derived facts are all stated as
**requirements**, in the document that owns the entity.

**The deletion is a translation, and this is the part that matters.** The DDL was not
illustration; in most places it was the only *precise* statement of a rule, and prose beside it
was the argument. Deleting the block and keeping the argument would silently drop the rule.
What must survive as written requirements, at minimum:

- the **no-overlap** rules — one open participation per person per unit, one open
  guardianship per pair, one open role assignment per person-role-scope, no two overlapping
  current contact points of one purpose. The *rule* is the design; the GiST index that
  PostgreSQL happens to use for it is not
- **the resolver's channels and their order** ([D-010](round-01a.md#d-010--role-assignments-and-access-grants-share-a-scope-model-and-a-resolver))
- **three-valued `was_present`**, where `NULL` means "no register was taken" and not "absent"
  ([D-067](round-05.md#d-067--presence-is-a-three-valued-fact-on-the-registration))
- **`birth_date_precision`**, because an imported `1990-01-01` often means *year 1990*
- **tombstone and redaction both survive on `person`**, with the two partial indexes that
  exist because every ordinary listing excludes both
- a person may not be merged into themselves, and `merged_into` / `merged_at` are set together
  or not at all

**A rule for writing the docs from here.** Where a rule can only be stated precisely enough to
be checked, state it that precisely. *"A guardianship may not overlap another guardianship for
the same pair"* is a requirement. `EXCLUDE USING gist (guardian_id WITH =, dependent_id WITH =,
period WITH &&)` was that same requirement wearing an implementation's clothes.

**What got genuinely weaker, which should not be written as though it were free.** The 19
integrity checks were executable. They are now **invariants to be verified by something** —
listed in the document that owns them, with no query attached. The one that suffers most is the
time-bomb added in the last round, which failed the build if `.admin` prefix-matching ever
reappeared in the resolver
([D-068](round-05.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle)). It is now
a sentence in a Markdown file. **A prohibition nobody runs is a convention, not a guard.** It
stays, because the alternative is silently forgetting it existed; it should not be described as
equivalent.

**Seed data goes with it.** There is no seed `INSERT` set, so there is no seeded role list and
no seeded permission list in the docs. This is what
[D-052](round-04.md#d-052--roles-are-runtime-data-the-seed-set-is-not-a-specification) already argued —
roles are runtime data and the seed set is not a specification — and D-072 removes the one
place the docs kept pretending otherwise. Starter roles and starter permissions are described
as *what the organization begins with*, not as rows.

**F-4a closes by dissolution.** With no seed block there is exactly one list of permissions,
which is the catalog. Two artifacts cannot drift when only one of them exists.

**Two-way door?** No. Re-deriving 4,689 lines of DDL from prose is a redesign, not a
restoration — the constraints encode decisions the prose does not always restate. Git has them.

**See:** [../data-model/00-conventions.md](../data-model/00-conventions.md),
[../open-questions.md F-4a](../open-questions.md#f-4--closed--the-question-was-answered-by-deleting-the-premise).

---

## D-073 — Guardianship is administered by its own parties, not by staff

**Status:** decided (from your answer) — **closes E-5**
**Date:** refinement round 6

**Your answer.** *"The guardian has the same rights as the user, so they can modify their own
guardians as well as the guardians with the write permissions. There is no need to take this
through the management team."* and, when asked how far that reaches, *"Guardian can be assigned
by other guardian."*

**Decision.** **The parties to a guardianship are principals on that row, not third parties
holding a grant on it.** A guardian may end the arrangement, may add another guardian to the
same child, and may change the permission level of the row they are a party to. The adult who is
the *subject* of a guardianship may end it over themselves. **None of these routes through
staff.** A staff member remains *a* way for it to happen and is never *the* way.

**This is the founding principle, applied one level down.** The rule this system was built on is
that authority over a nested thing originates at that thing and cannot be claimed from outside
it; the organization itself may not decide permissions over a sub-unit, and only the system
administrator is exempt. [D-031](round-02-03.md#d-031--no-downward-inheritance-of-authority-scope_exposure-is-the-only-crossing)
applied that to units. **A guardianship is a nested thing, and its "unit" is the people in it.**
A staff role reaching in to decide who is responsible for a child is exactly the move the
authorization model refuses everywhere else.

**E-5 closes, and it closes differently from every option on offer.** E-5 asked how an adult
ends a guardianship over themselves and offered three shapes — support request, ownership
channel, request object — all of which assumed the answer must come from *somewhere other than
the people involved*. It does not. Note also that the answer is not the **ownership** channel:
ownership is *your own record*, and a guardianship row is not the subject's record any more than
it is the guardian's. It is a record **of a relationship between them**, and both parties hold it.

**Mechanically this is a direction, not a fifth channel.** The resolver has four channels and
[D-010](round-01a.md#d-010--role-assignments-and-access-grants-share-a-scope-model-and-a-resolver) keeps them
at four. The guardianship channel already asks *"may guardian G act on D's records?"*; D-073 gives
it a second question, *"may a party act on the guardianship row itself?"*, answered for exactly
three acts — end the row, add another guardian, change the permission level. Adding a channel
would have been the same capability at the price of touching every document that enumerates them,
and enumeration is how the order stays a rule.

**Read D-069 and D-073 as one decision in two halves.** D-069 refused to let a birthday end a
guardianship and deleted the review queue, on the grounds that a person decides. It left the
question of *which person, using what* open — the exit it assumed had no door. D-073 is the
door. Without it D-069 was a refusal with no alternative; with it the pair says something quite
coherent: **a legal relationship between two people ends when one of those people says so, and
the organization's job is to be told, not to permit it.**

**The asymmetry, stated plainly, because it is real.** A guardian may appoint a guardian. So
anyone with authority over a child can give a second person that same authority with no
approval from the organization — the ordinary case being a mother adding the father, and the
case that is not being everything else. The design accepts this and holds one line instead:
**the act is attributed.** Who added whom, when, from which account, is audited, and the other
party is notified. That is a deterrent and an evidence trail, not a prevention.

**Not decided:** whether adding a guardian over a **minor** should notify anyone at the
organization beyond the audit log, and whether a subject may refuse a guardian appointed over
them. See **E-6**.

**See:** [../data-model/04-relationships.md](../data-model/04-relationships.md),
[../open-questions.md E-5](../open-questions.md#e-5--closed--the-parties-administer-their-own-row).

---

## D-074 — A guardian's rights are `none`, `view`, or `write`. Nothing more granular

**Status:** decided (from your answer) — **supersedes the mechanism of D-020; deletes `dependent.*`**
**Date:** refinement round 6

**Your answer.** *"Guardian rights should be only 'none', 'view', or 'write', nothing more
granular."*

**The docs had it the other way round, deliberately.** `guardianship_permission` was a table of
per-capability grants — `dependent.profile.view`, `dependent.medical.admin`,
`dependent.consent.admin`, `dependent.event.register`, `dependent.fee.pay` — and the glossary
asserted *"Being a guardian grants nothing by itself. Every capability is a separate, revocable,
audited row."* That was drawn as a consequence of the standing instruction that both read and
write permissions be explicit. **It went further than that instruction said: explicit and
granular are not the same property.** Explicit means *nothing is implied by identity*. That is
fully preserved here — a `guardianship` row with level `none` grants nothing at all.

**Decision.** **One value per guardianship row, from exactly three: `none`, `view`, `write`.**
Not a capability list. A guardian either cannot see the child's records, can see them, or can
change them.

**It is the same ladder, not a new one — which is the part that keeps the model honest.** The
design already ranks authority as `revoked`(0) < `view`(10) < `contribute`(20) < `manage`(30) <
`admin`(40) and compares by integer, never by string
([D-012](round-01a.md#d-012--status-strings-compare-by-rank-never-lexicographically)).
The three guardian rights map onto it: `none` → 0, `view` → 10, `write` → 20. **Guardian
authority is therefore a range of an existing ladder, not a parallel enum**, and the resolver
compares it with the machinery it already uses for grants. A fourth guardian value would have
been the beginning of a second authorization model.

> **Amended by [D-099](round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality),
> which deleted the ladder this paragraph leans on.** The three values and everything they mean stand — the
> decision was never the numbers — but there is no rank left to map onto. The comparison now runs against a
> column on the permission: **`permission.right_kind ∈ read | write`**, where `none` covers nothing, `view`
> covers the codes marked `read`, and `write` covers both
> ([data-model/05-authorization.md §1](../data-model/05-authorization.md#right_kind-a-column-with-exactly-one-customer)).
> That column has exactly one customer, and this entry is who it was added for. **The paragraph's real work
> was never the shared arithmetic:** a guardian not being staff is carried by the channel's shape test
> ([D-079](#d-079--the-guardianship-channel-is-entered-by-shape-not-by-permission-name)) — a check that is
> not about this child never reaches the guardianship channel, whatever its right level. And the closing
> warning survives intact, only cheaper to honour: a fourth value would still be the start of a second
> authorization model, and three values against two kinds is a lookup rather than a scale to keep in step.

**What this deletes.** Every `dependent.*` permission code, including `dependent.admin` and the
three sub-resource `.admin` codes that D-068 deliberately exempted. The consequence is worth
noticing: **after D-068 deleted `admin` as a wildcard and D-074 deletes it as an action, the
only things in the entire system still spelled `admin` are `access_level.admin` (a rank) and
`system.admin` (the one wildcard permission).** The word is no longer ambiguous three ways; it
is ambiguous two ways, and the third is recorded as deleted.

> **And since [D-099](round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)
> deleted the ladder, it is ambiguous one way.** `access_level.admin` was a rank in a table that no longer
> exists; **`system.admin` is now the only live permission code in the system whose last segment is not an
> action**, and it is allowed to be one for the two reasons D-104 records: its meaning is defined by the
> resolver rather than read off the name, and D-068 exempted it explicitly rather than by silence.

**What it gives up, written down rather than discovered later.** It is no longer expressible
that *this* guardian may register the child for events but may not read the medical record, or
that a grandmother may see the roster but nothing else. Under D-074 she either can see
everything about her grandchild or nothing. The rescue is that `write` is not `manage`: a
guardian at `write` still cannot do organization-wide things, cannot see a *different*
dependent's records, and cannot reach beyond the records the dependent's own record contains.
**If the split turns out to be needed in real operation it is a new decision (E-7), and it
should not be reintroduced as a permission nobody argued for.**

**D-046 survives, simplified.** Defaults still differ by how the guardianship came into being —
a parent recorded at creation starts at `write`; a court-appointed guardian and a
grandmother-added emergency contact start elsewhere. What differs is now one value instead of a
set.

**See:** [../data-model/04-relationships.md](../data-model/04-relationships.md),
[../appendix/permission-catalog.md](../appendix/permission-catalog.md),
[../open-questions.md E-7](../open-questions.md#e-7--closed--one-level-cannot-separate-the-medical-record-from-the-profile-and-nobody-wanted-to).

---

## D-075 — Money arrives from a bank API; a payment is requested by variable symbol and QR code

**Status:** decided (from your answer) — **closes finance questions 3, 5 and 6**
**Date:** refinement round 6

**Your answer.** *"Collection via gateway is the closest. It will be collected from the bank API
and payments will be requested through variable symbol + a QR code."*

**This is not the gateway the finance document was braced for.** Its question 6 anticipated a
*card* gateway and listed what that drags in: checkout, webhooks, disputes, chargebacks,
reconciliation, PCI. What you describe is the **bank-account** model, and it is a different
animal: nobody pays by card through this system. The system issues a **payment request**
carrying a **variable symbol**; the payer is shown that symbol and a **QR code** containing it;
their own bank moves the money; the **bank API reports the incoming transfer with the symbol
still attached**. The system never touches the payment — it reads a statement.

**Four consequences, in descending order of how much they change the schema.**

1. **The variable symbol is the design, so it must be unique forever.** It is the only
   correlation key between *"we expect money for this membership"* and *"money arrived at this
   account"*, which makes the payment request — not the payment — the entity the finance module
   is built around. Uniqueness is not per year, not per membership, not per unit: **a symbol
   issued in 2019 must never resolve to a 2026 obligation**, because bank statements are
   replayed and late payments are the entire reason the renewal window exists.
2. **A symbol is a sequence, never a derivation.** Anyone can type eleven digits into a payment
   form. A symbol derived from a birth date, a membership id or a member number is guessable,
   and guessing one redirects a stranger's money into a child's financial record — a wrong fee
   balance, a membership that appears paid, a child recorded as covered who is not. Unguessable
   is not a privacy preference here; it is the integrity of the ledger.
3. **There are no reversals, so there is almost no status column.** Bank transfers do not
   bounce, are not disputed by the payer's bank and do not expire. `payment.status` needs
   nothing resembling `pending`, `failed`, `declined` or `disputed`. **A refund is a second
   payment in the opposite direction, not a transition of the first.** The status enum that
   question 3 asked about collapses, and refunds — a policy question with no answer for six
   rounds — mostly answer themselves.
4. **A QR code is a rendering, not data.** It encodes the symbol, amount and recipient that
   already exist. No stored image, no re-generation job, nothing to invalidate.

**The consequence for D-040 is the one that matters operationally.** The renewal window opens a
new membership period *at* the expiry date when payment lands inside the window, and D-040's
own note said the reliability of that rule depended on payment dates arriving reliably. Until
now they arrived when somebody noticed a transfer. **They now arrive from the bank.** The
backdating rule stops being a promise about someone's February and becomes a property of the
import.

**What is not decided, and is now the interesting part of the module.** Whether event fees get
a symbol as well as membership fees; whether a symbol is issued per person, per membership
period, or per individual liability (a camp is a separate payable from a fee); and what the
amount mismatch means when a payer enters 500 for a 550 request. See **F-10**.

**See:** [../data-model/07-finance.md](../data-model/07-finance.md),
[D-040](round-02-03.md#d-040--the-fee-expires-yearly-a-date-tracked-renewal-window-replaces-a-grace-status).

---

## D-076 — Money that cannot be matched waits for a person

**Status:** decided (from your answer) — **closes EV-3 and finance question 1's sibling**
**Date:** refinement round 6

**Decision.** A bank transfer that resolves to no live payment request — unknown symbol, the
symbol of a cancelled event, an already-satisfied request, an amount that does not match, more
than the request asked for — is recorded as an incoming transaction and **enters a queue**. The
system neither applies it nor returns it.

**The queue's outcomes, all chosen by a human:** attach it to a different request; split it
across several; record it as a donation with no obligation behind it; or refund it by hand.

**Why not auto-apply by payer identity, which is the tempting answer.** Because the case it gets
wrong is not the edge case. *A parent with two children pays one amount against one symbol* is
the ordinary shape of family payment in a youth organization, and an identity-based fallback
resolves it to whichever child the query reaches first. A fee recorded against the wrong child
is simultaneously a finance error, a membership that appears paid when it is not, and — where the
fee buys insurance — a coverage record that is untrue. **The fallback would be wrong on the
common path, which is the one place a fallback is never allowed to be wrong.**

**Why not auto-refund.** It requires the bank integration to work outbound as well as inbound —
a second integration, with its own authorization. And it returns the grandparent's attempt at a
camp contribution.

**Where most of the queue's volume will actually come from: cancellation.** [D-064](round-05.md#d-064--there-is-no-event-status-visibility-is-the-permission-model)
made cancellation a recorded fact rather than a state, which means the event survives, the
registrations survive, and **so does an outstanding payment request against an occasion that is
not going to happen.** So: cancelling voids the outstanding requests, and money that had already
arrived becomes a queue item for a person to refund or carry forward. **This is EV-3's answer**,
which is why EV-3 is closed rather than deferred to finance.

**The pattern, third occurrence.** Across six rounds the design has permitted exactly two
automatic state changes — the fee sweep ([D-040](round-02-03.md#d-040--the-fee-expires-yearly-a-date-tracked-renewal-window-replaces-a-grace-status))
and the waitlist release
([D-066](round-05.md#d-066--payment-confirms-the-place-and-the-release-deadline-is-the-one-automatic-transition))
— and refused every other offer to act on a person's behalf. D-076 is the third refusal, and
the first in the opposite direction: **the earlier two released a person from something they
owed; this one declines to release money from the person it belongs to.** Unmatched money is a
fact with no subject, and per
[D-059](round-05.md#d-059--unanswered-is-the-absence-of-a-row-a-registration-stores-two-values)'s discipline
the absence gets stored rather than inferred.

**See:** [../data-model/07-finance.md](../data-model/07-finance.md),
[../open-questions.md EV-3](../open-questions.md#ev-3--closed--cancelling-voids-the-request-and-paid-money-queues).

---

## D-077 — Messaging is direct by default, `broadcast` is an ordinary scoped permission, and the recipient chooses the channel

**Status:** decided (from your answer) — **first decision of the communication module** *(amended by
[D-082](round-07-08.md#d-082--a-direct-message-to-a-minor-is-mirrored-to-the-minors-guardians), which supplied the
thing this entry declined and left unprovided: a rule for the private message to a child)*

**Date:** refinement round 6

**Your answer.** *"There will be internal messaging through the system. Personnel with
'broadcast' permissions are able to send messages to everyone, other users only to direct
persons. The messages get then directed to email, push notifications or IM depending on the
user's choices."* — and, asked about the unit leader left out by that split, you chose a
**scoped** permission.

**Three decisions in one sentence, and the first is structural.**

1. **The system is the medium; email, push and IM are delivery.** A message is written once,
   internally, and then *distributed*. This is the load-bearing choice, because the alternative
   — the system as a mail relay — has no record of what anyone was told.
2. **Two sender tiers.** Everyone may write **direct** messages. **Broadcast** is a permission.
3. **The recipient chooses the channel.** The sender chooses who; the recipient chooses how it
   reaches them.

**Therefore: one message, one recipient row each, and the medium resolved at delivery.**
A `message` plus a `message_recipient` per addressee carrying read state; the channel is
selected per recipient against their own contact points. A bounced email is a failed delivery on
one channel, not a lost message. `person_contact.purpose` gains a messaging purpose and each
contact point carries its own opt-in, which is the existing contact-point model doing work rather
than a new subsystem beside it.

**`broadcast` is granted at a scope, which is the whole authorization model speaking again.**
Granted organization-wide it reaches everyone; granted on a unit it reaches that unit's people.
No new mechanism — role assignments already carry a scope. **A single global `broadcast` flag
would have made a pack leader announcing a 9 a.m. start either the holder of an
organization-wide power or the author of twelve identical messages, and the first of those is
precisely the arrangement every other part of this design exists to prevent.** Note that this
lands on scope authority rather than on audiences: *who may address* a set is authority over that
set, and authority over a set originates inside it.

**Age is not a sender concept, and that is a decision, not an omission.** The question asked
whether staff may address a child directly or only their guardians; the answer replaced it with a
sender-tier model that has no age in it. Consistent with
[D-070](round-05.md#d-070--an-event-has-no-age-ceiling-the-grant-is-the-rule), there is no age branch in the
resolver. **The residue is stated rather than hidden: any account in the system may send a direct
message to any other account, including a child's.** The rule the communication section had
promised — *"a rule against contacting minors directly"* — is **not** implemented as a
restriction on senders. See **MSG-1** for the recommendation, which is to restrict *visibility*
rather than permission: direct messages reaching a minor mirrored to their guardians, so nothing
is blocked, nothing is secretly unread, and the resolver still has no age branch.

**Two-way door?** The delivery half yes — adding a channel is a new contact purpose. The sender
tiers no: once people can message each other, retracting that is a feature removal, and any
later safeguarding rule has to be written as surveillance over a channel that already exists.

**See:** [../domain/02-actors.md](../domain/02-actors.md),
[../appendix/permission-catalog.md](../appendix/permission-catalog.md),
[../open-questions.md § Communication](../open-questions.md#h-not-yet-designed).

---

## D-078 — An exposure extends an assignment, never a direct grant

**Status:** decided — **found by deleting the SQL, not by running it**
**Date:** refinement round 6

**Superseded by [D-097](round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row) with the exposure table itself.** Its distinction, that widening an
inherited reach is a different act from writing a grant, has no subject after [D-099](round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality): a grant has exactly
one shape, and there is nothing to extend it.

**What happened.** Translating the resolver out of SQL for
[D-072](#d-072--the-documentation-carries-no-sql-the-schema-is-the-orms-job) meant reading each
branch for what it *decides* rather than what it says. The unit-grant tier had two branches, and
the second one consulted `scope_exposure`. It joined the direct grant to `se.org_unit_id` while
also requiring `se.org_unit_id =` the unit being checked. Both conditions pin the grant to the
checked unit — which the first branch had already tested. **The branch could never succeed where
the first one failed.**

**It was not a vulnerability.** A branch that can only ever return true where another branch
already returned true grants nothing. The damage is to the reader: a tier that appears to widen
direct grants through exposures is a tier that will be trusted, reviewed and extended on that
basis. It survived every review of the SQL precisely because it reads correctly.

**The rule, now stated.** `scope_exposure.role_assignment_id` points at a **specific person's
assignment**. The unit is agreeing that *this person, in this role, for this period* may act here
— which is what makes the exposure legible as an act of the unit rather than a grant to a
whoever-holds. A direct `access_grant` contains no assignment for an exposure to attach to, and
a grant already at the checked unit needs no extension to work there. **So the role channel is
the table's only consumer, and the unit-grant tier matches exactly.**

**Why the tempting repair must be refused.** "Exposures don't extend my direct grant — that looks
like an oversight, let's add it back" produces a system where a unit that exposed *a treasurer
role assignment* has also, silently, exposed itself to every direct grant held by every person
who happens to hold some other assignment there. The repair would widen an exposure to cover
people the exposing unit never approved, in the one direction the founding principle forbids.
Anyone reaching for it should read this entry first, which is why it is a decision and not a
comment.

**What this says about D-072's trade.** The deleted SQL contained a bug and the prose cannot
contain it, because the prose does not have a dead branch. This is the one case where removing
the schema was an unambiguous improvement, and it is worth recording beside the cases where the
removal cost something real.

**Two-way door?** No, in the sense that matters: adding a second route back is a widening. In
every other sense yes — nothing here constrains a future mechanism that names a grant in an
exposure row deliberately, which would need a new column and a new argument.

**See:** [../data-model/05-authorization.md §5](../data-model/05-authorization.md#5-scope_exposure--deleted-by-d-097).

---

## D-079 — The guardianship channel is entered by shape, not by permission name

**Status:** decided — consequence of [D-074](#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular)
**Date:** refinement round 6

**Before.** The resolver picked a channel by string: a permission code beginning `dependent.` went
down the guardianship channel, everything else went down the ordinary path. This was elegant, and
it had a hole nobody noticed while it was true.

**The hole.** A parent correcting their child's address is performing `person.address.edit`. That
code has no `dependent.` prefix — it is the same code a person uses to correct their own address.
**So the act did not route through guardianship at all.** It resolved against the parent's own
roles and item grants, which say nothing about this child, and the answer was deny — correct by
accident, for a reason that had nothing to do with the relationship that made the act legitimate.
Any future `person.*` act a guardian needed would have inherited the same dead end, and the fix
each time would have been a new `dependent.*` code, which is how the namespace grew to eighteen.

**Now: the channel is entered when the subject of the act is not the actor.** The resolver is
already handed both — the actor, and the owner of the thing being touched. Compare them; if they
are different people, ask the guardianship question. **That question may answer only "yes".** If
the answer is yes the check is finished and the act is allowed; in every other case the channel
falls silent and the resolver carries on to the actor's own roles and grants. **It is not the last
word, and the paragraph below explains why that had to change as well** — the first draft of this
decision kept the old finality, and the two halves are inconsistent within one page, which is
itself instructive about how a rule outlives the reason it had.

**Three things this buys.** *(a)* Nothing escapes by naming: a permission added next year for a
field a guardian must edit is covered the day the field exists, because dispatch reads the shape
of the request rather than a list maintained beside it. *(b)* It is one comparison instead of a
prefix match against a namespace that has to be kept in step with the catalog by hand. *(c)* The
rule is stated in the resolver, where a reader looking for "how does a guardian get authority"
will find it, rather than in a column's comment.

**What it costs.** Dispatch is now invisible in the data. Under the prefix rule you could look at
a permission code and know which channel would answer for it; now you have to know whether the
check is being made about somebody else, which is a property of the call site, not of the
permission. **This is the price of every shape-based rule and it is worth paying here**: the
alternative was a rule that was legible and wrong. The audit side of it is unchanged — an act
performed on behalf of a minor is recorded as such regardless of which code was checked
([04-relationships §5](../data-model/04-relationships.md#5-acting-on-behalf--recording-it)).

**Where the boundary sits, because `subject ≠ actor` is far broader than guardianship.** A
treasurer entering a payment for a child, a leader marking a roster, a registrar correcting a name
they imported: all of these are subject≠actor checks, and none of them is a guardian acting on a
ward. If the channel answered for all of them, the treasurer would be asked whether they are the
child's guardian, told no, and **denied an act their role plainly authorises.** So the channel
speaks only when there is something to ask: **a live guardianship row joining this actor to this
subject, at this date.** No row, no answer, and the resolver falls through to the allow tiers
exactly as it always did. There is no age test in that guard, which is deliberate — the
guardianship row *is* the relationship, and adults who file one for themselves
([D-073](#d-073--guardianship-is-administered-by-its-own-parties-not-by-staff)) are covered by the
same two words as minors are. An age branch would also contradict
[D-070](round-05.md#d-070--an-event-has-no-age-ceiling-the-grant-is-the-rule) and
[D-077](#d-077--messaging-is-direct-by-default-broadcast-is-an-ordinary-scoped-permission-and-the-recipient-chooses-the-channel),
both of which insist the resolver has no age in it.

**The consequence is a real weakening of the channel, and it should be read as such.** Under the
prefix rule the guardianship channel gave the **final** answer: `dependent.medical.view` was a
guardian-only code, no role held it, so "the guardian's right is `view`, this is a write" could
safely end the check. Now that the channel carries ordinary codes a role might also grant,
finality turns into a trap — **the parent who is also the event registrar, holding `view` over
their own child, denied the right to do their job.** So the guardianship channel now returns
**allows only**: sufficient right → true; insufficient, or `none`, or no row → silence, and the
actor's own roles and grants are still tried. What is *not* lost:

- **`none` still grants nothing**, which is what D-074 actually promised. It was never a promise
  to block unrelated authority.
- **A genuine prohibition is still available and still absolute** — an explicit deny in channel 0,
  which runs before everything and does not care about scope. That is where "this person must not
  touch this child's record" belongs, and it is stronger than what a guardianship level could do.
- Nothing an actor reaches by falling through is authority the guardianship row was hiding: their
  role already gave it to them, guardianship row or not.

**What is lost is the ability to say "not even your role".** No guardian's `view` can ever be
that sentence again. In a safeguarding system that sentence has to exist, and D-032 already put it
in the deny channel rather than distributed across capability levels — so the loss is of a
convenient place to write it, not of the mechanism.

**Two-way door?** Yes in principle, no in practice — the old dispatch can only be restored by
re-inventing the namespace D-074 deleted.

**See:** [../data-model/05c-access-log-and-resolver.md §10](../data-model/05c-access-log-and-resolver.md#10-the-resolver),
[../data-model/04-relationships.md §4](../data-model/04-relationships.md#4-how-the-resolver-uses-these-tables),
[../appendix/permission-catalog.md §9](../appendix/permission-catalog-b-roles-and-open-issues.md#9-there-is-no-dependent-namespace).

---

## D-080 — Five contradictions the translation surfaced, and how each was resolved

**Status:** decided — **each resolution is a correction, not a choice between options**
**Date:** refinement round 6

**Why this entry exists.** [D-072](#d-072--the-documentation-carries-no-sql-the-schema-is-the-orms-job)
required every SQL block to be read for what it *decides* before it was deleted. That reading is
the first time these documents were checked against themselves line by line, and it found five
places where a document said two contradictory things — in three cases three things, one of them
executable. **They had been invisible precisely because one of them worked.** A query that returns
the wrong rows is not visibly wrong. Each is resolved here rather than left as a note, because
with the SQL gone there is nothing left to disagree with the prose: **the prose is now the only
place the rule lives, so it has to be right.**

| # | The contradiction | Resolution |
|---|---|---|
| 1 | `identifier_scheme.is_unique` said a school id may repeat; the uniqueness rule applied to every scheme and never read the flag | **The flag decides.** A second child at the same school with the same number is not a duplicate identifier, and would have been rejected at import by a constraint its own table called wrong. [01-identity §7](../data-model/01-identity.md#7-person_identifier) |
| 2 | §9 of the identity document opened by saying its views encode "always exclude merged **and redacted**"; `v_person` excluded merged only, while §1 and §2 both required both | **Both exclusions.** A redacted child in a list of children is not a formatting issue. Rows still resolve; people do not appear. [01-identity §9](../data-model/01-identity.md#9-views) |
| 3 | The audit redactor kept an *always-redacted* list of free-text fields — and nothing read it | **Kept, and labelled as intent.** It is the clearest illustration in the whole repository of what a declarative list nobody consults is worth. [06-audit §2.2](../data-model/06-audit-and-import.md#22-redaction-before-logging) |
| 4 | The unit-grant tier appeared to widen direct grants through `scope_exposure`, and did not | Dead branch. **The rule is now stated once, in the direction that is true:** an exposure extends an assignment and never a grant. [D-078](#d-078--an-exposure-extends-an-assignment-never-a-direct-grant) |
| 5 | `is_leadership` lives on `position`, and the audience rule for `unit_leaders` read it as though it lived on `role` | **Fixed where it is read.** The audience is "holds a live assignment to a leadership *position* at that unit", which is what everyone had been assuming it meant. [05-authorization §8](../data-model/05a-audience-and-grammar.md#8-audience--grants-that-target-a-set-of-people) |

**One pattern, four instances.** Every one of these is a **second statement of a rule that the
first statement did not consult**: a flag beside a constraint, a view beside a section heading, a
list beside a loop, a column on the wrong table. Two copies of a rule diverge — the reason this log
exists at all — and the divergence is only found by someone reading both. That is also why the
permission catalog is now the catalog's alone, why §11 of the conventions points at Rules blocks
instead of restating them, and why the count in that sentence is not a coincidence.

**What was *not* resolved, in the same spirit.** Item 3's fix is a label, not an enforcement;
item 5's check still cannot run automatically; and a correction nobody re-tests is exactly how
item 2 got into the documents. **The five resolutions are therefore themselves invariants** — if
someone regenerates a schema from these documents and produces a per-table identifier constraint
or a redacted-inclusive listing, this entry is the thing that was violated.

**Two-way door?** No, and deliberately: each of these was a bug whose "fix" is indistinguishable
from a regression. If one returns, it returns as a bug report, not as a reversal.

---

## D-081 — Rule names survive the deletion of their mechanisms; a renamed rule must say who enforces it now

**Status:** decided (editorial ruling, ratified this round)
**Date:** refinement round 6
**Follows:** [D-072](#d-072--the-documentation-carries-no-sql-the-schema-is-the-orms-job), [D-080](#d-080--five-contradictions-the-translation-surfaced-and-how-each-was-resolved)

**What was found.** With the DDL gone, roughly sixty sentences still credited a database object
with acting: "the trigger in §3 enforces it", "the schema cannot express", "`ck_request_rejection_reason`
requires a reason code", "refused by trigger (§8)". None was false when it was written. Each became
a **false claim about the present** the moment D-072 removed the thing it named, and a reader who
trusts the sentence does the one thing this corpus cannot afford — assuming a guarantee exists and
not writing it.

**Ruling 1 — the identifiers stay; the agency goes.** `ck_org_unit_closed`,
`uq_org_unit_single_root`, `uq_access_grant_live` and the rest are kept **as names of rules**, not
as claims about objects:

| Before | After |
|---|---|
| "`ck_org_unit_closed` states the invariant explicitly" | "**A unit cannot be closed without an end date** (`ck_org_unit_closed` is this rule's name)" + which layer carries it |
| "the trigger refuses deletion" | "Guard 2 is the rule, the no-cascade reference is what refuses it, and `event.delete` only decides who may ask" |

Deleting the names would be a repository-wide rename touching every cross-reference, and a rule with
a stable handle is worth more than a purer vocabulary. **The line is agency, not vocabulary:** an
identifier may survive its table as long as no sentence asks it to do anything.

**Ruling 2 — renaming the mechanism is never the fix.** Where a rule loses its enforcement, the
sentence must state what is now required **and which layer owes it**, in the register of
[data-model/00 §6a](../data-model/00-conventions.md#6a-who-enforces-an-invariant-now). "The trigger
guarantees X" and "X is validated in the model" are not adjacent statements; the first is a
guarantee on every path and the second is a friendly message on the intended one. Softening one
into the other without saying so is how a deleted schema turns into a silently weaker system. Where
the honest answer is "no layer enforces this and none can", the text now says that — *a convention,
not a guard* — rather than letting the reader infer it.

**Ruling 3 — a rule that lost both its guard and its report gets a report.** Three had neither,
which is worse than losing the guard alone, because a missing guard is at least visible to whoever
writes the migration:

| Rule | Where the guard went | Net added |
|---|---|---|
| `position.max_holders` | no constraint can state a count over other rows (F-10 shape 3) | [02-organization §9 check 9](../data-model/02-organization.md#6-integrity-checks) — over-limit means *bypassed*, unlike event capacity, which may be exceeded deliberately |
| Registration outside its window | Guard 1, inside the writing transaction | [08-events §10 check 9](../data-model/01-identity.md#10-integrity-checks) — a row here is evidence about the code, not the data |
| `fee_obligation`, created by the code that places a registration | nothing ever enforced it | [08-events §10 check 10](../data-model/01-identity.md#10-integrity-checks) — a confirmed place with no bill leaves every row individually correct |

One rule keeps **no** net, deliberately, with the absence named instead of smoothed over:
`org_unit.parent_unit_id` immutability ([D-036](round-02-03.md#d-036--units-cannot-be-reparented-a-unit-that-moves-is-a-new-unit)).
A reparent leaves nothing malformed to count, so it became F-10's fourth shape rather than a check.

**One contradiction of D-080's class, found and settled.** §2.1 of
[data-model/06](../data-model/06-audit-and-import.md#21-the-trigger) said `DELETE` is outside the
audited operations "because nothing in this data model is hard-deleted", while §3's import revert
removes the `person`, `membership` and `unit_participation` rows a batch created. Written together
they meant **a rollback could erase live rows without a trace** — the one event someone is most
certain to ask about later. Settled in favour of the audit log: **a revert writes one audited entry
per deleted row, naming the batch**, and `DELETE` stays outside the audited operations only because
no other path reaches a business row with a delete.

**The residual that could not be closed.** Audit *completeness* used to be answerable from the
database's own catalog — ask which tables carry triggers, compare against the business tables. There
is no catalog to ask now: a table is audited because the code writing it remembers to, so the
nightly comparison runs between two hand-maintained lists, and **both can go stale together and
still report zero.** The replacement is an assertion over the paths that may write or delete a
business row; until that exists this is recorded as a known hole rather than as a solved problem.

**Ruling 4 — the decision log may quote SQL; nothing else may, and a quotation must say where the
rule lives now.** Five fences survived in this log, and deleting them would be the wrong
correction: an entry that says "the exclusion constraint drops `membership_type_id`" is *about* that
constraint, and rewriting it into prose would quietly revise a record of what was decided in order
to keep the vocabulary clean — the same mistake D-080 catalogued, arriving from the opposite
direction. So the fences stay, each followed by one italic line naming **the requirement as it is now
stated, the document that owns it, and the layer that owes it**. The header of this log says the same
thing once, so that no fence is read as a specification by someone who arrived at it directly.
That is the whole distinction: **the documentation describes a system; this log records how the
description got here, and a record is allowed to quote things it no longer endorses.**

**See:** [data-model/00 §6a](../data-model/00-conventions.md#6a-who-enforces-an-invariant-now),
[open question F-10](../open-questions.md#f-10--which-invariants-the-orm-cannot-express-and-who-writes-those)
(now four shapes), [D-072](#d-072--the-documentation-carries-no-sql-the-schema-is-the-orms-job).

---
