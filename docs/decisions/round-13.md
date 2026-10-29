# Decision Log — Refinement round 13 (D-109 … D-113)

> Nothing a rule names is deleted; the expression is the record; the scale is stated; and guardianship is a channel, not a selector.

[Refinement rounds 11 and 12 (D-105 … D-108) ←](round-11-12.md) | [All decisions](index.md) | [Refinement round 14 (D-114) →](round-14.md)

---

## D-109 — Nothing a rule names is deleted: deprecated, hidden, disabled — and a tab instead of a report

**Status:** decided (from your answer)
**Date:** refinement round 13
**Supersedes:** the report D-106 added, the merge-repoint duty D-105 recorded, and part of F-21

**Decision.** Anything a stored expression can name — a `selector_type` row, a `role`, a `person_group`, an
`audience` — **is never deleted while a rule may name it. It is given a state instead.** Three states, and they
must stay three different things or one of them will silently become the other:

| State | Does it still resolve? | Is it offered when writing a rule? | Is it flagged? |
|---|---|---|---|
| **`deprecated`** | **yes, unchanged** | no — it cannot be added to a new rule, and editing a rule cannot introduce it | **yes**, highlighted in the editor wherever it appears |
| **`hidden`** | **yes, unchanged** | no | no — it is not obsolete, it is not everybody's business |
| **`disabled`** | **no — the empty set** | no | yes, and this is the only state that changes an answer |

**No standing report.** There is **a tab on the permissions page** listing every live rule whose expression names
a deprecated, hidden or disabled thing, or fails to resolve at all.

**Why.** Your answer, in full: *"There should be no deleted selectors, only deprecated/hidden/disabled. In that
case, the original resource is still referenced and applied, BUT it cannot be added to new or edited rules AND it
is highlighted in the rule editor. No real report is needed, there can be a tab on the permissions page listing
all the 'broken' permissions."*

**This deletes the reason the report existed, which is the elegant part of it.** D-106 added a report to catch an
unresolvable operand; F-21 asked who would read the report of the widest expansions and could not name anybody.
Both are answers about a failure whose **cause is now removed**: a leaf broke because the thing it named was
deleted, and here nothing is deleted. F-21's reader question resolves to *nobody, because there is nothing to
read* — and what replaces it is better than a report for the ordinary reason that **a report has to be
remembered and a tab is where the person already is**. The tab is not a control either, in D-081's sense; it is a
control that has a decent chance of being seen, which is all the difference between a convention and a decoration.

**Two duties this withdraws, and one it leaves standing.** Round 11 recorded that **a person merge or a redaction
must repoint every `audience_operand` leaf**, because a leaf naming nobody is the empty set and on a `-` side
that widens. **For the resources in the table above that duty is gone** — retiring a group is now one write to the
group, not N writes to N expressions, and the expressions keep meaning what they meant until somebody edits them.
**It survives for exactly one argument kind, and that is the collision this entry has to name:** `PERSON(x)` names
a *person*, and [D-088](round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short) lets a redaction
require the row to actually go. **Erasure wins.** A person is not a selector, and no convenience owed to an
expression author survives a former member's right to be deleted. So the corpus now has **exactly one remaining
way to produce a broken leaf — a redacted person** — and D-106's semantics cover it unchanged: the empty set,
narrowing an allow and widening a deny, now visible in the tab rather than in a report nobody opens. **That is a
much smaller domain than D-106 assumed, and stating it that way is the point.**

**What `disabled` costs, said plainly, because it is the loudest switch in this system.** Disabling a group, an
office or an audience **stops every rule that names it, in every scope, at once**, and **re-enabling it restores
all of them** — a widening in which nobody edited a grant, so the audit trail would show one flag write and a
hundred permissions appear if it were logged as anything less. Therefore: **disabling and re-enabling are audited
writes that print the rules they touch**, resolved before and after, which is the same report
[D-104](round-10b.md#d-104--a-permission-codes-last-segment-is-an-action-and-a-registry-that-prose-contradicts-is-a-fiction)
and [D-105](round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other) adopted for their own
migrations; and the tab lists the rules currently dead for this reason, so the state is reversible *knowingly*.
`disabled` is also the answer to a question this corpus kept meeting — *"how do I turn off that whole naming
without editing forty grants?"* — which until now had no answer except a deny per grant.

**The invariant that keeps `deprecated` from drifting into `disabled`:** *deprecating or hiding what an expression
names must not change the set the expression resolves to.* That is check-worthy, it is cheap, and it is the
precise failure this whole design is meant to make impossible — a rule that quietly stops granting because
somebody tidied a list. The editor's reserved-name rule (D-101) keeps a deprecated or disabled name reserved, so
nothing new can quietly claim the word and split its meaning in two.

**See:** [D-106](round-11-12.md#d-106--a-failed-operand-stays-the-empty-set-the-missing-half-was-a-report-not-a-refusal) (whose
semantics now apply to redacted people only), [D-105](round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)
(the repoint duty, halved), [D-088](round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short) (why
erasure wins), and [F-21](../open-questions.md#f-21),
closed as "no report; a tab; nothing bounds a check, deliberately".

---

## D-110 — The expression is the record of whom a grant reached

**Status:** decided (from your answer)
**Date:** refinement round 13
**Closes:** F-23, and the reconstructable-past half of F-17

**Decision.** The audit record of a grant's reach **is the expression**. The preview still prints a resolved set
before a save ([D-091](round-09.md#d-091--a-permission-group-is-a-rule-and-a-list-at-once-and-a-rule-may-name-another-group))
and that printing is logged as *a rendering on a date*, not as a statement of who was in it. **"Whom did this
grant reach in May?" is answered, if at all, by evaluating the words against the data of May** — and these
documents do not promise the answer.

**Why.** Your answer, four words: *"Words only — the expression is the record."* The alternative was to keep the
preview's list beside the audit row, and that list **is the roster table this corpus has deleted twice**
([D-105](round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other), and assumption 58's
history of it). It would also store, indefinitely and against
[D-088](round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)'s window, a per-person record of
people who were **never granted anything** — a list of everyone a rule happened to cover, kept after the rule
was withdrawn. Storing that to make a historical question comfortable is the trade this corpus has refused every
time it has been offered.

**Why words-only is cheap now rather than brave.** It was nearly untenable an hour ago and it is sound now,
because of [D-109](#d-109--nothing-a-rule-names-is-deleted-deprecated-hidden-disabled--and-a-tab-instead-of-a-report):
**if nothing a rule names is deleted, the words stay evaluable long after their reason is gone.** A role that was
retired still resolves; a group that was deprecated still resolves; a name stays reserved. **The two rulings are
one design** — refuse to delete the nouns, and then keeping only the words is not an amputation. Without D-109,
this answer would mean "the past is usually unanswerable"; with it, the past is usually *computable*, and what is
left is honestly bounded.

**What is conceded, named so nobody finds it later.** Editing a shared audience changes what **every grant that
names it** has meant all along, because those grants hold a word, not a copy — and a re-evaluation for a past
date uses *today's* inner expression. **An edit to a shared audience is therefore a retrospective edit to every
rule that names it.** That is not new (D-103 accepted it as the price of reuse) but until now it was only implied;
here it is the reason a past-date answer can be wrong rather than missing, and the control is D-103's existing
one: **the editor prints the resolved set before an edit to a shared expression saves**, so the person editing
sees, at least once, the thing they are changing backwards in time. What is *not* kept is a history of inner
expressions; the audit trail records the edit, not the meaning that existed before it.

**A consequence worth holding onto:** the audit trail gets *smaller and more honest*. A row says *this person
wrote these words on this date about this item*, which is a fact that cannot go stale, rather than *this grant
reached these 214 people*, which starts decaying the night somebody's birthday falls.

**See:** [D-107](round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded) for why
a set now moves on its own, [D-109](#d-109--nothing-a-rule-names-is-deleted-deprecated-hidden-disabled--and-a-tab-instead-of-a-report)
for why the words keep resolving, and [F-17](../open-questions.md#f-17),
whose premise about materializing this removes.

---

## D-111 — The permission cache is rebuilt nightly, on any ruleset change, and on request

**Status:** decided (from your answer)
**Date:** refinement round 13
**Closes:** F-6, and F-7 by absorption
**Superseded in part by [D-114](round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation): the cache is deleted, so there is nothing to rebuild.** What
survives of this entry is the *integer* — `ruleset_version`, now keying a compiled expression instead of a cached
answer, with its bump set cut from the eight kinds of write listed below — six tables, this entry's own D-109
flag and a merge — to `audience_operand` and
`selector_type`. **What went is the object, the schedule and both invalidation lists.** Reading this entry as
wrong would be the mistake it does not deserve: it removed a TTL question by removing the need for a TTL, which
was the right move against the problem it could see, and **what D-114 found is that the rebuild had quietly
inherited the staleness window the TTL was for** — the answer moved on a schedule instead of on a clock, and a
schedule is a harder place to notice that than a column. Its *"the safeguarding case is immediate"* argument is
true now by construction rather than by trigger, which is the best outcome a superseded ruling can have.

**Decision.** There is one cache policy and three triggers. **Every cached authorization answer is rebuilt (a)
nightly, in full; (b) immediately on any write to the ruleset; (c) on explicit request** — an administrative
action, which belongs on the same permissions page as the tab. **No TTL per entry, no asymmetric TTL, no partial
invalidation list to get right.**

**Why.** Your answer, verbatim: *"All cache is represhed at night every day OR on manual request and ruleset
change."* F-6 had spent four rounds on which write invalidates how wide a fan-out, and on an asymmetric TTL that
would make a deny visible sooner than an allow. **This replaces the whole invalidation table with a rebuild and a
rule about what counts as a ruleset change**, which is a smaller thing to be right about — and the fan-out
question was only hard because per-entry invalidation was assumed.

**What counts as the ruleset**, because the boundary is now the whole design: a write to `access_grant`,
`audience_operand`, `guardianship_permission`, or `permission`; to `role_holder` and `person_group_member`; to
the `deprecated | hidden | disabled` flag of anything in D-109's table (**that flag must be a ruleset write — if
it is not, "turn off this naming" waits until midnight, which is exactly the failure the flag exists to
prevent**); and a person merge or unmerge. **An answer that moves without one of these is allowed to be up to one
night stale**: a birthday crossing `OLDER(n)`/`YOUNGER(n)`, the 1 January membership sweep, a role or group period
that ends by its own date, attendance writes behind the event tiers.

**That residual window is the ruling, and it is the same ruling as D-107's.** A withdrawn permission keeps
working until the nightly rebuild **only if the withdrawal was not a write** — and every withdrawal a person
performs *is* a write: revoke, add a deny, close a grant's period, end a guardianship, end a role assignment.
What waits for the night is what nobody does: an expiry arriving on its own, an age arriving on its own.
**The safeguarding case is immediate; the calendar case waits at most one refresh, and the refresh is what fixes
it.** This is D-107's *"I know, that the time will change, how the rules resolve and IT IS FINE"* with the
mechanism attached — until now the sentence described a behaviour, and now it describes a policy.

**What "immediately" means when you cannot enumerate the affected people — the mechanism, added the same
round because the ruling was incomplete without it.** Found while propagating this entry: the cache key is
`(person_id, permission_code, scope_type, scope_id, at_bucket)`, and **an audience appears in it nowhere**. So
the writes that need *global* invalidation are exactly the ones that name nobody. **Ending one
`role_holder` row names its person; ending one `person_group_member` row names its person; an edit to a shared
`audience_operand` tree names nobody at all** — the people it stops reaching are whatever the expression
happens to resolve to, and finding them means evaluating it for everyone, which is the job, not a way around
it. Per-entry invalidation had no answer to that, which is why F-6's table spent four rounds pretending the
fan-out was tractable. **The answer is a ruleset version: one integer, bumped by any write in the ruleset set
above, carried in every cache entry, and an entry is valid only while its version matches.** "Rebuild
immediately on a ruleset change" then means *bump the version*, which is one write to one row and never needs
to know whom a rule reaches; the nightly rebuild stays as the correctness backstop for everything the version
does not cover (the calendar cases); and the manual request becomes "bump it and warm it". **This is also what
makes the `deprecated | hidden | disabled` flag safe in D-109's sense**: flipping `disabled` on a group is a
ruleset write, so it bumps the version, so no cached `true` survives it — and if the flag ever stops bumping,
D-109's *"deprecating or hiding must not change the answer"* invariant still holds while *"disabling takes
effect now"* silently does not, which is a failure worth having a check for. **What the version does not buy:**
it is not a per-audience version and not a version per grant. A system large enough to want that is the system
D-112 says this one is not, and the trigger there is what reopens this.

**What F-7 was, and why it is answered rather than decided.** F-7 asked whether to keep a cache or materialize an
`effective_permission` table. **A nightly full rebuild of cached answers and a nightly materialized
`effective_permission` table are the same job with two names.** There is now one job; the question was not
resolved between two designs, it was **dissolved by the design being chosen for a different reason** — which is
worth recording as such, because a dissolved question is the kind that comes back if nobody writes down that it
dissolved.

**The constraint this does not lift.** The rebuild may evaluate expressions per person — that is what a cache
warm is, and at the size in [D-112](#d-112--the-systems-scale-is-stated-hundreds-of-people-tens-of-registrants-per-event)
it is cheap. What stays forbidden is the failure domain/06 names as the one way to get this wrong: **inside a
check, an expression is compiled to a predicate on the person being asked, never materialized as a set** —
otherwise the nightly job is correct and every request still materializes the whole set instead of testing the
one person in front of it. **That clause used to end "…and every request still costs three thousand rows," and
the number is gone on purpose:** it was an estimate of the whole grant table, written three rounds before
[D-112](#d-112--the-systems-scale-is-stated-hundreds-of-people-tens-of-registrants-per-event) stated a size and
said plainly that nothing in these documents had measured anything. It is in the same order of magnitude as that
size, so nothing computed here changes — but a load-bearing number in a decision entry has to be one somebody
counted, and this one was not.

**See:** [F-6](../open-questions.md#f-6) and its
invalidation table, which this replaces, and [data-model/05 §10's cache section](../data-model/05c-access-log-and-resolver.md#the-cache-is-deleted-nothing-in-this-schema-holds-a-permission-answer).

---

## D-112 — The system's scale is stated: hundreds of people, tens of registrants per event

**Status:** decided (from your answer)
**Date:** refinement round 13
**Closes:** F-15, F-16, and the cost half of F-21

**Decision.** The system is specified against a stated size, and the size is now written down instead of being
assumed differently by every page that reasons about cost: **a few hundred people in the organization, a few
dozen registrants on a typical event, a big camp on the order of two hundred.** Every "is this cheap enough?"
question this project has carried — the per-item preview, listing the grants that name an audience, an unbounded
audience expansion, a nightly full rebuild — resolves at that size, and resolves **only** at that size.

**Why.** The pair chosen was *"Hundreds of people, tens per event"* — asked because two questions had stayed
open for three rounds for the reason that nobody had stated a number, and a cost argument without a number is
not an argument, it is a mood. **Nothing in these documents measured this.** No page carried a headcount before
this entry, including the import pages that describe the legacy export row by row — so the number is *stated*,
not observed, and it is the answer to a question rather than a finding. That is the whole reason the trigger
below exists: a stated size is a load-bearing assumption with no evidence under it, which is exactly the shape
this corpus has repeatedly had to come back and pin down.

**What it closes.** **F-15:** a preview that resolves an audience for one item is, at this size, evaluating a
couple of hundred predicates — nobody will feel it, so the preview stays per-item and lazy (assumption 60) with
no cap and no background job. **F-16:** listing the grants that name an audience is a scan over a small table
with a handful of referencing rows each; pagination is a UI nicety, not a requirement, and D-103's assumption
that listing is cheap is **true, now on stated grounds**. **F-21's cost half:** nothing bounds what an expression
can cost, and at this size that is accepted rather than merely unaddressed. ~~**D-111's nightly rebuild:** people ×
66 permission codes × a small number of items is a bounded, short job — **"rebuild everything nightly" is
affordable here specifically**, and would be a different decision at ten thousand people, which is the honest
reason it was chosen.~~ **This half of the entry's affordability arithmetic was overtaken by
[D-114](round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation), which deleted the job whose cost was being estimated — so the answer to "is the rebuild
affordable at this size?" is that there is no rebuild, and this entry's *other* four answers (preview, listing,
expression cost, F-16) are the parts that stand.** The method here is what matters and it is unchanged: a stated
size is what makes a cost claim checkable, and a claim that stops applying says so.

**The trigger, since a stated assumption without a trigger is just a guess with more confidence.** If the
population reaches **a few thousand people, or a thousand registrants on one event**, reopen F-15, F-16, F-7 and
F-21 — in that order, because the preview is the first thing a user will feel and ~~the nightly rebuild the
last~~ **the nightly rebuild was last in that list and is now deleted; what sits in its place is nothing, so the
order below it is unchanged and one shorter**.
**Nothing in the design depends on the number, on purpose**: the two rules that must survive any growth are the
ones already written — *a check compiles its expression to a predicate and never materializes the set*, and *a
listing is paginated* — so the system gets slow before it gets wrong, which is the only graceful failure this
module can promise.

**See:** F-15 and F-16, both closed against this entry, and
[D-111](#d-111--the-permission-cache-is-rebuilt-nightly-on-any-ruleset-change-and-on-request).

---

## D-113 — The guardianship channel has no expression: `GUARDIANS` is not a selector

**Status:** decided (found while closing F-5)
**Date:** refinement round 13
**Closes:** F-5's last live bullet, and with it the contradiction F-6 recorded about where a bound
`GUARDIANS` could be written.

**How it was found, since both the method and the mistake in it are useful.** F-5 had one live bullet left —
*does `GUARDIANS` bind to the item?* — and answering it needed every claim the corpus makes about that operand,
so a read-only sweep went out to collect them. **What came back was a confident report that the registry has no
`GUARDIANS` row at all**, fourteen rows and none of them guardianship. **That was false:** the row is the sixth
in `data-model/05` §8's table, `takes_argument` optional, `argument_type` `person`, and round 12's count of
fourteen was a correct count of a table that includes it. The report also named a file that does not exist and a
membership kind that does not, so its claims became leads and nothing more. **What survived checking was
better than what was claimed.**

**The real defect, which no count could have shown.** The row's third column reads `binds_to_item` =
**"yes, `person`"** — the one row in a table where that column means *the item this grant sits on* using it to
mean *a person*, and its gloss promises a **bound** form: *"Bound: the guardians of the person this item is
about."* **That form cannot be written.** F-6 found it independently while being closed: the save path refuses
any bound operand on a unit-scope grant, and the only item scope that could host one is an event, which is the
and the registry's own `argument_type` entry says the deciding sentence in passing — **"`person` never was" a
`grant_scope_type`** — so a bound operand whose argument is a person can never satisfy the type match, at any
scope, ever. **The bound half of the row was illegal by the registry's own fields**, while §12 was saying it may
be "bound as `GUARDIANS` on a grant about that person". **So the fourteenth row was a row
whose advertised half no grant could hold, and the count agreed with itself the whole time.**

**Which is the opposite lesson to the one this entry was going to record.** It was drafted as *"a count is a
good alarm"* — an uncounted name pointing at a defect. **Here the count was not the alarm, it was the
camouflage:** fourteen was arithmetically true of a table containing a row that could not be used as described,
and every page that repeated "fourteen" was reinforcing a fiction with arithmetic. **A registry checked against
itself is not a registry checked against the rules that write it**; that is
[D-104](round-10b.md#d-104--a-permission-codes-last-segment-is-an-action-and-a-registry-that-prose-contradicts-is-a-fiction)'s
finding again, one layer up, and it is why the checks that matter here are on the **save path** rather than on
the row count.

**Two things about this round's own conduct belong in the same section, because the entry is about method.**
The unsavability of the bound form was found **twice, independently** — once while closing F-6, once by an
agent sweeping for this operand — which is the only reason I trusted it after this round's reports had already
been wrong four times over. And **this round wrote two false claims of its own while deleting the fiction**: a
quotation attributed to a page that does not contain it, and an invented `role_holder` *"kind"* whose enum I
wrote out of nothing in a page I was editing to be tidy about D-100. **The second was repaired by the agent
that found it, in `domain/04`, and the correction says so on the page.** The pattern across all six cases is
one line: *a confident claim with a line number is the most dangerous object in this repository, and the check
is two seconds of grep.* Which is worth more here than in most projects, because in a repo that is only
documents, **the grep is the test suite.**

**Decision.**

1. **The registry drops to thirteen: the `GUARDIANS` row is deleted, and nothing replaces it.** Neither the
   bound form it advertised nor the `GUARDIANS(p)` form it actually supported is a selector. **Fourteen was a
   true count of a table with a row that should not have been in it** — clause 4 is the argument for deleting
   the usable half along with the unusable one, and it is also the part of this entry that changed after the
   entry was written.
2. **The guardianship channel contains no expression, and never did since D-074.** A check asks whether a
   live `guardianship` row links the person asking to the person the action is about, and reads
   `right_level ∈ none | view | write` off it — **a lookup over a relationship, not a set that something
   resolves.** `guardianship_permission` is that value's **history**: `guardianship_id`, `right_level`,
   `valid_from`, `valid_to`, `changed_reason`, `changed_by`. **It has no grantee, no permission code, no
   audience and no expression column**, so there was never anywhere in it for a selector to be seeded.
3. **What the corpus did was describe a channel with a selector's syntax.** The word `GUARDIANS` appeared in
   tables and prose across `domain/06`, `glossary`, `data-model/05`, `data-model/08-events`, `domain/07-events`,
   `appendix/erd`, `appendix/permission-catalog` and `open-questions` — **31 occurrences outside this log**,
   counted with grep rather than remembered, and deliberately *not* all of them live claims: several are struck
   quotations of the round that introduced the word, which stay struck and stay wrong in place because that is
   what keeping history means. **The live ones all state a set where the model has a relationship.** In a table
   listing seeded *values* the word meant
   *"the guardians of this ward, via the guardianship channel"*, which is a true and useful thing to mean and
   the wrong notation to write, because
   [D-107](round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)'s test for
   an operand is **a named registry row** and no such row exists. **Worse than a typo: a notation that parses
   reads as a decision someone made.** The fix at each site is to name the channel and the value — a
   `guardianship.right_level` of `view` or `write` — which the same tables already do in their prose one line
   away, and which several of them do in the very next sentence.
4. **`GUARDIANS(p)` goes too, and this clause is the one that changed after the entry was first written.** My
   first version removed the empty form and **kept the parenthesised one** as a narrowing operand — *"the set of
   guardians of the named child"*, useful, I argued, for granting a ward's guardians something the three
   `right_level`s do not contain. **That was wrong, and the reason is a fact about the channel I had described
   twice without drawing its consequence:**

   > *"True, GUARDIANS should not be selectable in the audience, guardians can perform ANY action (their
   > read/write perms grant) on behalf of the child."*

   **A guardian's authority is not a list of codes; it is a level over a child.** `write` does not mean *these
   six permissions* — it means *any action about this child*. So an operand aiming a grant at a child's
   guardians offers, one code at a time, **a subset of what those people already hold**, and it can only ever be
   used about an item the channel would have reached anyway. **It is not redundant by accident; it is the long
   way round to something the model grants outright.** The reason it took a round to see is that
   `GUARDIANS(p)` looks like a perfectly ordinary narrowing operand — the `ROLE(x)` of family relationships — and
   the reason it is not one is that **what it narrows is not a permission set but a relationship that carries its
   own authority**, which nothing else in the registry is. That is the whole content of *"a channel is not a
   selector"*; clause 3 was only the half I had got.

   **What a real need looks like instead.** *"Send the parents of these six children the newsletter"* is not a
   permission question — it is **a set of people with a lifetime**, which is what `person_group` is for
   ([D-098](round-10a.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority)): name the group,
   put the six guardians in it, aim the grant at `GROUP(x)`. If the list must be *derived* rather than kept, the
   honest sentence is that this system stores a `guardianship` row and no query over it as an audience.
   **A derived guardian list is a feature this system does not have** — checked, not assumed: nothing anywhere
   in the model derives a set of people from the guardianship rows except the channel itself, not as a group's
   membership kind, not as an office's holder, in no table — and a missing feature is a question or a decision
   entry, not an operand nobody checked for.
5. **`binds_to_item` keeps its meaning and loses its exhibit.** D-102 introduced the column to settle a question
   about guardianship — it *"records whose guardianship is being asked about, which is the only thing `GUARDIANS`
   ever needed and could not say"* — and the thing it was introduced to classify turns out not to exist.
   **The column is undamaged:** `ATTENDED`, `PLACED`, `CONFIRMED`, `ON_WAITLIST` and `ORGANIZERS` are `true`
   because they cannot be evaluated without the event the grant sits on, and everything else is `false` because it
   can — **five `true` rows, and this clause first printed four**, having written the four attendance tiers and
   forgotten the roster, which is the same slip in the same entry that exists to record slips of exactly this
   kind: a count written from the shape of a sentence instead of from the table. `ORGANIZERS` is `true` on the
   registry's own row (`yes, event`) and is named in the same save-path rule in `data-model/08-events.md`. What changes
   is that the column is now justified by **the event operands, which is a large and ordinary reason**, instead of
   by one strange case that was never real. **Where the confusion actually lived, because the two sentences are
   the evidence:** `data-model/05`'s registry row read `Binds to item` = **"yes, `person`"** — the one row in a
   table whose third column means *the item this grant sits on*, using the column to say something the column
   cannot say, and adding *"Bound: the guardians of the person this item is about"* — **asserting a bound form the
   registry could not produce.** `data-model/08-events.md` then counted it as **the sixth attendance tier**: *"The
   sixth is `GUARDIANS`, which binds to the person an item is about rather than to an event."* **An operand with
   no seed row, listed among five that have rows, declared bound by a page while its own row used a column whose
   definition excludes it.** Corrected at both sites: **nothing guardian-shaped is bound to anything, because
   nothing guardian-shaped is an operand.** **What is left is four attendance tiers plus the organizer roster —
   five operands that bind, and no sixth**, which is the naming `data-model/08-events.md` uses and the one this
   entry should have used the first time: "five tiers" and "five binding operands" are different claims wearing
   the same number, and only one of them is about the tiers.

   **The lesson is not about guardianship, it is about registries that are copied.** A row can be wrong in a
   way no check catches, because the check compares the row's fields to each other and a field used to mean two
   things agrees with itself. `binds_to_item` needed a third value, or the sentence needed a different column,
   and neither happened for eleven rounds because the sentence was doing a good job in prose.

**Why this is not merely a naming cleanup, and what class of error it is.** `SCHOOL` was refused (D-108) for
naming a fact no table stores. **This is the same refusal one level up: a selector naming a *mechanism* the
model implements somewhere else entirely.** The grammar is closed and its vocabulary is checkable, so a word
that parses without a row behind it is the only way to say something false in it — and this corpus has now
been caught doing exactly that with a word nobody hand-typed, which means **the vocabulary's open half was not
the only place the check was needed.** The general rule, for
[F-10](../open-questions.md#f-10--which-invariants-the-orm-cannot-express-and-who-writes-those)'s list:
***every selector name that appears in a document must be a `selector_type` row, and a check should be able to
say so.*** That is a lint over documentation against a seed list, which is a strange thing to want until the
fourteenth selector turns out to be a prose idiom.

**What this costs, and why the answer is "less than it looked like from the clause above".** Deleting the
operand removes **no capability**, which is worth being precise about because the first draft of this entry
thought otherwise and minted an open question for the loss. The worry was: *nothing can now denote "whatever
guardians the person this item is about has", so a guardian could never be given a permission wider than
`view`/`write` over their ward.* **That worry presumes `view`/`write` is a ceiling on codes, and it is not — it
is a ceiling on acts about that child.** A guardian at `write` may already perform any action whose subject is
their ward, which is a larger grant than any audience operand could have assembled from single codes, and
smaller in exactly the direction that matters: **it reaches no item that is not about the child.** The channel
is both wider and narrower than the operand it replaces, which is what makes it a channel. The residual case —
*guardians of this child should get at something that is not about the child* — is not a permissions question
and never was: **it is a list of people, and lists are groups.** So there is no F-24 and there is no new row —
**this sentence printed "the fifteenth row" while `GUARDIANS` still held slot fourteen, and at thirteen the next
operand would be the fourteenth, so the number has been replaced by the words rather than corrected:** an
ordinal in this entry turned out to be a count in disguise, which is the collision this entry exists to
stop — and **no third binding kind is needed**: `binds_to_item` keeps its two operands' worth of justification on
the event side and never has to mean *the subject*.

**Recorded because the pattern is the point:** the open question I minted for this entry's supposed loss was
emptied by the same ruling that caused it, ten minutes later, and **an entry that had shipped in between would
have put a real-sounding question in front of somebody who could not answer it.** A question written against a
capability should be checked against the channel that grants it before it is written down.

**The seam this entry leaves open, and whose it is.** [D-109](#d-109--nothing-a-rule-names-is-deleted-deprecated-hidden-disabled--and-a-tab-instead-of-a-report)
says a selector that a rule may name is **never deleted** — it is deprecated, hidden, or disabled — and this
entry deletes a row. **The two are reconciled by a fact about dates, not by an exception: the row is unseeded in
the same round it is criticized, in a spec that has shipped no release, so the set of stored expressions naming
it is empty by construction.** It would not have stayed empty. The argument-less form was unsavable on every
scope (`person` never was a `grant_scope_type`), but the explicit `GUARDIANS(p)` form — legal arity, an argument
type that column can hold, and no item-type check because an explicit argument binds to nothing — **was savable,
and one writer finding it in a dropdown would have made this deletion illegal.** **That is the whole of the reconciliation, so
it is also a standing instruction:** a deployment that does hold such a leaf must **hide the row, rewrite the
leaves, and only then unseed it**, because deleting a row under a live leaf produces precisely the failing leaf
D-109 retired deletion to prevent, and D-109 said the only remaining way to make one was a redacted person.
**If this entry is ever re-read as licence to delete a seeded operand, the reading is wrong: what licenses the
deletion here is the emptiness of the set of grants that could name it, and that set has to be checked, not
assumed.**

**See:** [D-074](round-06.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular) (why there is no
capability list to select from), [D-085](round-07-08.md#d-085--the-identity-machinery-stays-structured-the-boundary-is-rules-not-sensitivity)
(the `view`/`write` level on the live `guardianship` row, which is what actually serves the need — this line
 first named that thing **`OWN_WARD`**, a token invented in this line and found nowhere else in the corpus — the
 second name this entry manufactured after the F-24 question it disowns above, and the one that reached a
 reference, where it looks like a row someone seeded. **It is named here in prose and linked from nowhere, which
 is the smallest honest repair: deleting the words would hide the invention, and leaving the link would keep it.**
 [D-102](round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)
(`binds_to_item`, whose definition this entry keeps and whose prose it corrects),
[D-107](round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded) (the test that
caught it), [D-108](round-11-12.md#d-108--there-is-no-school-operand-a-selector-may-only-name-a-fact-the-model-stores) (its
neighbour: a selector naming a fact that is not stored, this one naming a mechanism that is stored elsewhere),
[D-098](round-10a.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority) (where a kept list of
contact adults actually belongs), and **F-5**, whose last live bullet was exactly this question.

---
