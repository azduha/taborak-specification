# Decision Log — Refinement round 14 (D-114)

> The permission cache is deleted. A check resolves, a request memoizes, and the only cached thing is a compilation.

[Refinement round 13 (D-109 … D-113) ←](round-13.md) | [All decisions](index.md) | [Refinement round 15 (D-115) →](round-15.md)

---

## D-114 — There is no permission cache: a check resolves, a request memoizes, and the only cached thing is a compilation

**Status:** decided (from your answer)
**Date:** refinement round 14
**Supersedes:** [D-111](round-13.md#d-111--the-permission-cache-is-rebuilt-nightly-on-any-ruleset-change-and-on-request)'s
storage half — the cache, the nightly rebuild, and both invalidation lists. **Its `ruleset_version` integer
survives, with its bump set cut from the eight kinds of write D-111 named — six tables, the D-109 flag and a
merge — **to two tables** (below), which is the part of it worth keeping.
**Amends rather than reopens:** F-6's key dies with the cache it keyed; F-7's dissolution needs a new reason
now that one of the two things it dissolved between has been deleted; [D-112](round-13.md#d-112--the-systems-scale-is-stated-hundreds-of-people-tens-of-registrants-per-event)'s
"the rebuild is affordable here specifically" was a reason for choosing D-111 and is retired, while its
population figure and its trigger both stand.

**Decision. No permission answer is ever stored.** `permission_cache` is deleted from the schema, and with it
the key `(person_id, permission_code, scope_type, scope_id, at_bucket)`, the `at_bucket` truncation, the
nightly full rebuild, and the two lists that decided what bumps a version. Three things do the work the cache
was supposed to do:

1. **A compiled expression is cached.** Parse once, resolve operand kinds once, emit the parameterized
   predicate once — keyed by the expression's root plus `ruleset_version`, **holding no person and no item**,
   because both arrive as parameters. **This is exactly why a compilation survives across people and an answer
   cannot**: nothing in it depends on whom or where it is asked about.
2. **A request memoizes.** One indexed read fetches the checked person's live grant rows; every code, item and
   date in that request is evaluated against them in memory. Within the same request, a named operand that
   recurs (`ROLE(leader)`, `GROUP(cubs)`) is resolved once. **Lifetime is the request, so there is no
   invalidation policy for it and no staleness window at all.**
3. **The bulk screens batch.** `can_many(person, codes[], item?)` answers a screen's worth of affordances from
   one resolution, and `which_of(people[], code, item)` answers a list's worth from one pass. The per-item
   preview (F-15) and the permissions tab (D-109) are written against these, not against a loop of single
   checks.

**Named rosters may still be cached across requests**, keyed by the name — `ROLE(x)` over `role_holder`,
`GROUP(x)` over `person_group_member`. **Two conditions, and they are the whole difference from what is
deleted:** the key is the thing the write touches, so **invalidation is local to the row that changed** and
never global; and the cache holds **the dated rows, or the set with its validity ranges**, never the set as of
today, so the checked date is still applied at check time and a period ending at midnight needs no job to be
seen. A roster is also *named and addressable* — it is a row someone maintains and can point at — which an
answer never was. **And a roster is only what those two are.** `MEMBERS` is not one: it is not a row anybody
writes but the read predicate over `membership`, whose dated rows the 1 January sweep rewrites for every member at
once, so caching it would put that bulk event straight back on the invalidation list this entry deletes
([`03-membership.md` §6](../data-model/03-membership.md#6-membership-and-the-authorization-system)).
`ORGANIZERS` is not one either, and not for want of holder rows — it has them — but because it is **bound to an
item** ([D-102](round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)),
so its key would name an event and the cache would be a stored answer to "who was at this one", which is what
D-102 refused to make a permanent set. **Of the five operands that bind to an item none is a roster; of the
seeded selectors only `ROLE` and `GROUP` name a holder table that a person maintains by name.** That is the whole
extension of the exception, and it is closed rather than open-ended.

**Why the design as written was ineffective, in the order the numbers say it.** The key's space at
[D-112](round-13.md#d-112--the-systems-scale-is-stated-hundreds-of-people-tens-of-registrants-per-event)'s stated size is a
few hundred people × 66 codes, order **tens of thousands of entries**, and a full rebuild of that is one short
job — so the cache was saving a thing whose replacement costs about as much as it does. Worse, **the bump set
included `person_group_member` and `role_holder`, which are the two most ordinary writes in this
organization** — a child joins the Thursday group, an office hands over at camp — so every one of them dropped
the entire cache, and the effective hit rate was *time since the last group edit* in a place where group edits
never stop. A cache whose invalidation is free and total is one step from no cache, and D-111 had already made
it free.

**The decisive finding is not the hit rate; it is that the boundary was wrong in the sensitive direction.**
§8 said *"the line between those two lists is the entire safety property"*, and the lists were: `access_grant`,
`audience_operand`, `guardianship_permission`, `permission`, `role_holder`, `person_group_member`, the D-109
flag, and a merge or unmerge. **`membership` is on neither list as a table whose writes matter.** But `membership.terminate` ⛔ is a real code in
the catalog, held by `safeguarding_officer`, whose stated reason is *"whoever finds the problem and whoever ends a
membership over it are the same person, and nobody else"*. So an officer terminates a member, `MEMBERS` shrinks,
nothing rebuilds, and **every cached `true` behind `MEMBERS * …` stands until midnight.** One tier lower and the
same shape: `event_registration` was declared
*not* a ruleset write, so a family cancelling a place left the child inside `PLACED` and `CONFIRMED` until the
nightly job. D-111's defence was *"what waits for the night is what nobody does: an expiry arriving on its
own"* — and a termination and a cancellation are precisely things people **do**, one of them the most
safeguarding-shaped act in the catalog.

**The corpus had warned about exactly this, in the other file.** `data-model/03-membership.md` §6, "What still
costs, unchanged by the move", carried as its first bullet: *"**The permission cache must be invalidated on every
membership transition** — including the yearly expiry sweep, which is a bulk event touching every member at
once. … The cache design has to be built for this from the start; **retrofitting it is where the bugs will be**."*
That sentence was written three rounds before D-111 drew the two lists, in the module that *has* the coupling, and
the lists were drawn in the module that *owns* the cache — **which is the whole failure in one sentence: a
requirement stated where the dependency is felt is not read by the page that has to satisfy it.** The prophecy was
right about the mechanism and about the size of the hole. This entry deletes both the cache and the bullet's
obligation, which is the only way the two files can now be made to agree.

**How this entry's own finding got here, because the route matters more than the finding.** The first version
asserted that `membership` appeared in the caching discussion with *"zero occurrences in the corpus"* — **and that
was true**, checked two ways: no file names `membership` beside the ruleset boundary, and no file describes a
membership transition as rebuilding anything. What is *not* true is how nearly it was overwritten: a report
reached me during this round asserting the claim false and supplying a quotation to a page, a sentence beginning
*"the change lands in the cache's one-night staleness window … that is the designed behaviour of the cache … not
an oversight"*. **That quotation does not exist anywhere in this repository.** It was written into two files
before the grep that should have preceded it was run; the grep found nothing, and both insertions came out.
**The lesson has two halves, and the second is the one that stung.** (i) Grep the *claim*, not the phrasing — the
requirement here is real and it hides behind the words "must be invalidated", not behind "ruleset", so a narrow
grep nearly talked me out of a correct finding. (ii) **A correction arriving from anywhere — an agent, a diff, a
quotation with a line number — is a claim, and the check is the same two seconds it always was.** A report that
flatters its reader by catching the reader's error is the version of this that gets through, because the
temptation is to accept it without looking.

**The general form, which is why editing the list was never the fix.** A correct invalidation set is **every
table any operand can read transitively**: `membership`, `role_holder`, `person_group_member`,
`event_registration`, `event_organizer`, the `person` row's birth date and status, the guardianship rows, plus
the rule tables. That is not a policy boundary, it is the read path, and a hand-maintained copy of the read
path is a second source of truth about what an expression means — [D-081](round-06.md#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now)'s
class and [D-104](round-10b.md#d-104--a-permission-codes-last-segment-is-an-action-and-a-registry-that-prose-contradicts-is-a-fiction)'s
in one object: **a list whose membership contradicts the operands' read set is a fiction, and it had already
contradicted it in the one place where being wrong is worst.** Completing the list would make the version bump
on nearly every write, which is this entry's answer with extra machinery bolted on first.

**What D-111 actually got wrong, said precisely enough to be useful.** It did not make an error inside its own
frame; **it never questioned the object that created the problem.** Given a stored answer, "whom does this
change reach?" is unanswerable without evaluating, so a global version was the right answer — and the sentence
that turned the boundary into the safety property was written by this round, one round ago, into four files, and
no check can read a list like that. `ruleset_version` was sound and is kept. **What is retracted is the claim
that the two lists were a safety property at all: a safety property that has to be re-derived from the grammar
every time an operand is added is a chore with a reassuring name.**

**The version integer, narrowed rather than deleted, and the shrink is the point.** A compilation depends on an
expression's shape and on the seeded vocabulary and nothing else, so the bump set is **`audience_operand` and
`selector_type`** — two tables, down from the eight kinds of write D-111 named: six tables, the D-109 flag and a
merge. `access_grant` drops out because **grants are not
compiled**: a check reads the person's live grant rows, so adding, editing or revoking one changes what that read
returns and leaves nothing stale to drop, and a grant created together with a new audience is an
`audience_operand` write, which stays in the set; the
`deprecated | hidden | disabled` flag drops out because a state is **not compiled in** — resolution consults it
live, once per request, memoized — which is also what makes `disabled` still mean *now*, by reading the flag
rather than by dropping the world; `guardianship_permission` drops out because the channel is read live;
`role_holder`, `person_group_member` and a person merge drop out because they move rosters and grant rows, which
are read live or invalidated locally. **Concretely: adding a child to a group, which used to drop the whole
cache, now drops nothing.** And because a compilation is finite and enumerable over the audience tree, **"an
edit to a shared audience invalidates everything" becomes "it invalidates the compilations that embed it",
which is a bounded walk over rows that already exist**,
and the direction is worth stating rather than glossing: **the save path walks the other way.** Cycle refusal
walks forward from the tree being saved, while invalidation needs the **reverse** direction — the one the
delete-refusal check already runs when it asks whether a live grant, or a live audience reachable from one through
any number of `AUDIENCE` leaves, names the audience being edited
([D-103](round-10b.md#d-103--an-audience-may-name-another-audience), and `data-model/05` §*The expression tree* with §11's
check 15). **So it is a new use of a direction the design already needs, not a free ride on a query that already
runs**, and the listing's cost is registered as unverified at any size in `data-model/05` §13 — **this entry
inherits that registration instead of resolving it, which is the honest form of "bounded".** The claim that
survives all of this is the narrow one, and it is the one that mattered: **the fan-out that defeated F-6 was only
hard because it fanned out to people.** **The name `ruleset_version` stays and its meaning is redefined here, in place,
because a term whose scope just narrowed by an order of magnitude will be re-inflated by the next reader
otherwise: "ruleset" now means the text of the rules, not anything an expression can read.**

**What is gained, and it is more than the deletion.** *"The safeguarding case is immediate"* stops being a
property of a list and becomes a property of the read path: a termination, a revoke, a cancellation or a closed
period is visible on the **next check**, with no job in between and nothing to remember to mark as a ruleset
write. **And [D-107](round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)'s
accepted drift ceases to exist.** What D-107 waived was the calendar moving an answer between rebuilds — a
birthday crossing `OLDER(n)`, a period reaching its own `valid_to` — and D-111's own residual list widened that
to **the 1 January sweep and the attendance writes behind the event tiers**, which is how a schedule ends up
covering things that are not the calendar at all. Under live resolution **every one of them** moves the answer
**at the instant it happens**, so the ruling stands and its mechanism is no
longer needed: **"up to one night stale" is deleted from this corpus, and the sentence that survives is
*"IT IS FINE"* with nothing left for it to be fine about.** A ruling that turns out to be unnecessary is a
better outcome than a ruling that had to be defended.

**What may never be stored again** — invariant 19, TIME-BOMB: **no row, table or field may map a person (or a
person-and-code, or a person-and-item) to a permission answer.** Enforcement is first structural, which is the
best kind this corpus has: **the schema has nowhere to put one**, since the only table that could hold it was
just deleted. The residue is honest and named — a future implementer adding a cache is stopped by this entry and
by review, not by a constraint, so for them it is **a convention, not a guard**
([D-081](round-06.md#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now)).
**If a cache is ever added back it must arrive as a decision entry, and it must carry three things this one
lacked: a per-person invalidation handle alongside the global one, an explicit statement of which tables it
watches, and that statement derived from the operand registry rather than from a list of ideas — on pain of
this entry repeating one round later with a different table in the hole.**

**Cost, stated as arithmetic and not as a measurement.** A check is one indexed read of the person's live grant
rows — a few dozen rows at the stated size — plus, per expression, a handful of indexed point lookups against
the operand tables. **The cost that made a cache look necessary was never this arithmetic; it was the N+1
across a screen**, and the memo and `can_many` remove that directly, so the deleted cache and the replacement
differ mostly in *when* the work happens. **What is genuinely lost:** a nightly job used to pre-pay the
expensive screens, so the per-item preview, the tab and the "who holds this" listing now do their work on open.
At the stated size that is affordable, and D-109 already ruled the tab is computed when opened — **that ruling
now has no fallback, which is worth recording as a dependency rather than as a risk.** D-112's trigger stands,
and its reopen answer is now named instead of vague: at a few thousand people, materialize `effective_permission`
per person **and call it that** — a real materialization with a per-person invalidation handle and a stated
staleness window, which is the honest shape of the object being deleted here.

**The second loss is the one nobody was counting, and it lands on a control that was already the weakest kind.**
Cached answers were the accidental mitigation for unbounded expression size: a wide expansion got paid once per
person per night, so the cost of a thousand-person `EVERYONE` stopped being anybody's problem between rebuilds.
[D-105](round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other) deleted the depth bound and
refused to mint a size bound in its place, and `data-model/05` §*The cost of composition* registered what replaced
the retired invariant — a standing report of the widest and deepest audiences and their cost per check, which is a
**convention, not a guard** in [D-081](round-06.md#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now)'s
vocabulary. **Deleting the answer cache moves load onto that convention:** after this entry an expansion is paid per
check, memoized inside a request and cached nowhere wider. **This does not reopen D-105's ruling; it changes what
the ruling costs**, and the honest record is that round 14 made the report this module is worst at reading carry
slightly more. It is written into that bullet rather than softened here.

**See:** [D-111](round-13.md#d-111--the-permission-cache-is-rebuilt-nightly-on-any-ruleset-change-and-on-request) (what
this keeps and what it retires), [D-107](round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)
(the ruling whose mechanism this removes), [D-110](round-13.md#d-110--the-expression-is-the-record-of-whom-a-grant-reached)
(why nothing here needed a stored answer for the record's sake),
[F-6](../open-questions.md#f-6)
and [F-7](../open-questions.md#f-7)
(both amended, neither reopened),
[D-102](round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it) and
[D-103](round-10b.md#d-103--an-audience-may-name-another-audience) (the binding the roster exception respects, and the walk
whose direction the narrowed bump set needs), [D-105](round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)
(the ruling whose cost this changes without reopening it), and
[D-081](round-06.md#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now)
— a rule that outlives its mechanism must say who enforces it now, and this entry deleted the mechanism on
purpose and wrote the answer down. **The invariant lives in
[`data-model/05` §11](../data-model/05d-invariants-and-seed.md#11-invariants-to-verify) as check 19, and the read path it
protects is [§10 of the same page](../data-model/05c-access-log-and-resolver.md#the-cache-is-deleted-nothing-in-this-schema-holds-a-permission-answer).**
**And the finding that decided it came from another module's file**
([`data-model/03-membership.md` §6](../data-model/03-membership.md#6-membership-and-the-authorization-system)),
which is where a reader should look for the shape of this failure again.
