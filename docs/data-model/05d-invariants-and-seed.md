# Data Model — Authorization: invariants, seed data, open issues

The invariants a correct implementation must hold, the rows the platform ships
with, and what is still open on this part of the model.

**Section numbers are shared across the five parts** and never renumbered, because other
pages cite them by number and their anchors are built from them: [05-authorization.md](05-authorization.md) holds §1–§7, [05a](05a-audience-and-grammar.md) §8 (the `audience` table, the grammar, the selector registry), [05b](05b-expression-tree.md) §8 continued (the tree and what each operand costs), [05c](05c-access-log-and-resolver.md) §9–§10 (`access_log` and the resolver), and [05d](05d-invariants-and-seed.md) §11–§13 (invariants, seed data, open issues).

---

## 11. Invariants to verify

These were queries. They are now invariants to be verified by something, in whichever way the
implementation chooses, and what follows states what each one counts and what a non-zero result
would mean. **They are renumbered for round 10**, because several lost their subjects
(`requires_scope`, the membership gate, `system.gate_exempt`, `permission_level`, the three
`scope_exposure` checks) and the survivors were closed up rather than left with holes.

**Three of the old checks were CI assertions that read the text of the stored resolver to prove a rule
was still inside it (14, 15 and 19 in the previous numbering). Nothing can read that text any more.**
Their successors below are written as assertions about behaviour rather than about program text,
because that is the strongest form still available, and
[D-081](../decisions/round-06.md#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now)
requires saying so: **a prohibition nobody runs is a convention, not a guard.**

**Invariants to verify**

- **1. Live grants for a person who has been merged away.** An open `access_grant` whose person
  has been merged into somebody else. A row means authority is still attached to a tombstone;
  it should have been closed or moved at merge time.
- **2. Orphaned item grants, and orphaned selector arguments.** Per scope type, generated from
  `grant_scope_type`: a grant whose `scope_id` names no row in the item table it points at — and the
  same scan over `audience_operand.selector_arg_id`, which is polymorphic for the same reason and
  takes the same mitigation. A row is exactly the risk the polymorphic columns accept (§6,
  [D-011](../decisions/round-01a.md#d-011--scope_id-on-access_grant-is-polymorphic-with-no-foreign-key),
  extended to operands by
  [D-101](../decisions/round-10b.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree)),
  and this is that trade's compensating control. **An orphaned operand is the quiet half**: it
  resolves to the empty set, so the grant is inert rather than dangerous, and inert authority is the
  failure nobody notices.

  **Since [D-103](../decisions/round-10b.md#d-103--an-audience-may-name-another-audience) the scan
  covers one more target kind, and this is the one place its asymmetry has to be stated rather than
  assumed away.** `selector_arg_id` now also points at `audience`, and an orphaned `AUDIENCE` leaf is
  **not necessarily quiet**: quietness is a property of the leaf's *position*, not of the leaf. Reached
  through `+` or `*` it removes people; reached through `-` it adds everyone the missing audience was
  excluding. **So run the scan, and route its output to check 7's second report rather than to this
  one's** — an orphaned `ROLE` leaf belongs with inert authority and an orphaned `AUDIENCE` leaf
  belongs with the grants that got wider, which is the same fact about the operator being the thing
  that decides the direction of a failure, said once in §8's evaluation rules and again here because a
  reviewer reading only this list would otherwise file all of it under "inert". **In practice: one scan,
  two outputs**, splitting on whether the orphan sits under an odd number of `-` right-hand positions.

  **And since [D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)
  this scan is a backstop and not the mechanism, which is a downgrade in status and has to be said out
  loud.** Every hand-named person in the system is now a leaf in this column with no key behind it, so a
  person merge and a redaction are required to **repoint** those leaves in all five argument kinds that name an entity (§8,
  *A hand-named person is now a keyless reference*). **The scan cannot stand in for that requirement, for
  two reasons.** It runs the following morning, and an expression resolves wrong from the moment of the
  merge. And **it only fires when the absorbed person's row is actually removed** — if the merge leaves the
  row in place, as any design that keeps its history will, the leaf still names an existing id, this check
  reports nothing, and the grant quietly keeps a person who no longer signs in. On the allow side that is
  inert — **the failure narrows the set and stops there**; **under `-` the same failure widens it, and
  `EVERYONE - PERSON(x)` with an un-repointed `x` denies everybody.** [D-106](../decisions/round-11-12.md#d-106--a-failed-operand-stays-the-empty-set-the-missing-half-was-a-report-not-a-refusal)
  retired this bullet's earlier word for the second half — *loud* — and the replacement is worth the
  typographical trouble, because the two halves do not differ in volume, **they differ in which direction a
  wrong answer moves access**, and only one of those directions can grant.
- **3. A grant at a scope its code forbids.** An open grant whose `scope_id` is present while the
  permission's `applies_to` is `unit` — or any grant of a `system.` permission whose `applies_to` is
  not `unit`, which is the seeding rule §2 depends on. **Zero expected, and a row means the save-time
  check was skipped, not that a constraint was disabled** — no constraint spans those two tables.
  This is the report that stands in for a database rule, which makes it worth alerting on.
- **4. A bound operand where it cannot bind.** An `audience_operand` whose selector has
  `binds_to_item = true` and which sits in an audience aimed at a `unit`-scope grant, or whose
  `selector_type.argument_type` differs from the item type of every grant aimed at that audience. Zero
  expected for the same reason as 3: refused on save, unenforced by any constraint, and a row means
  the write path was bypassed. `PLACED` aimed at a group, or `ORGANIZERS` aimed at nothing, should be
  unsaveable, and this check catches the build in which they are not.
- **5. A deny that denies nothing.** A live `deny` whose grantee, scope and code match no live allow
  anywhere. **Probably intended as a removal rather than as a restriction; verify the intent.** D-099
  requires this one by name: a deny that denies nothing is how a stale restriction survives its
  reason, and the resolver will never tell anyone it is dead, because a deny never needs to.
- **6. A grant naming an office with no `MEMBERS`.** A live grant whose audience expression contains a
  `ROLE(...)` operand and no `MEMBERS` operand anywhere in the tree
  ([D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)'s
  standing report). **A row is not an error** — writing an office without the gate is a legitimate act
  and is exactly how an appointed officer keeps serving while their own fee is unpaid — but it is the
  case worth a human eye, because it authorizes a lapsed member silently and forever. This is the
  successor to the old "leavers with access" and "holders of the gate exemption" checks, and it is
  deliberately narrower than either: **the report has to be short enough to actually be read**, which
  the two it replaces were not.
- **7. A grant aimed at an audience that reaches nobody — or everybody.** A live `access_grant` naming
  an audience whose expression contains no operand that can hold a person — a sum of `PERSON(x)` leaves
  naming people who have been merged away,
  a `GROUP(x)` whose group has ended, an operand whose `selector_arg_id` is orphaned, **an
  `AUDIENCE(x)` leaf whose target has ended or gone (§8, and D-103)**, a tree that cannot be assembled.
  **The grant join is what makes this check worth running**: an empty audience on its own is a work in
  progress, but an empty audience a live grant points at is a permission configured, visible in an
  editor as granted, and reaching nobody — the same inert-authority shape the previous version of this
  document recorded for a rule that matched no person, and the one an administrator cannot see from the
  grant screen.

  **Run the same scan for the mirror-image case and report it separately, because it is the more
  dangerous of the two:** an empty operand reached through `-` makes the expression **wider**, so
  `EVERYONE - AUDIENCE(x)` with `x` gone reaches *everybody* — an allow that meant to exclude now
  includes, and a deny that meant to exclude now falls on everyone. D-103 kept fail-closed evaluation
  because of exactly this case, and this check used to call the case *"loud"* — the word
  [D-106](../decisions/round-11-12.md#d-106--a-failed-operand-stays-the-empty-set-the-missing-half-was-a-report-not-a-refusal)
  retired, because a widening is not a noise, it is a direction: **a wide failure is only better than a
  narrow one when somebody is reading**, which is what this check is for and nothing more. **What D-106
  added is a second column on the tab F-21 placed on the permissions page** — naming *which* leaf failed, not merely that one
  did — **aimed at the audience's owner**, which is the same shape as this check: a listing with somebody's
  name beside the row. So the control here is *report, twice over*, and **not** a refusal: nothing in this
  round stops an audience whose leaf is broken from being saved, and the round's premise is why
  ([D-107](../decisions/round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)).
  `MEMBERS - AUDIENCE(x)` is the **narrow** version — ~~the quiet version~~, again in the retired word — and
  it is the easier one to miss: **the exclusion is the grant's whole point and its
  target is gone, which reads on screen as a grant that still names the audience it excludes.** The
  save-time refusal (an audience named by anything live cannot be ended or deleted) is the primary
  control; this check is the one that fires when the refusal was bypassed by a restore or a manual
  delete, and unlike the empty side it should alert rather than be read weekly.
- **8. A grant whose expression contains `EVERYONE`.** Live, and naming `EVERYONE` anywhere in the
  tree. Not a violation: it is what a public page is for, and holding it directly was always legal.
  It is on the list because a language with union in it lets one edit widen a grant to every person
  with no account and no membership, and the person who made the edit is the only control
  (§8, *What audiences do not do*).
- **9. Holders of `system.admin`.** Everyone with a live allow of it, however they came by it —
  through a personal grant or through an expression naming an office. This should be a very short
  list, and it should alert on change.
- **10. Expression trees that are not trees.** Any of: a node with a selector, or a leaf with an
  operator; a node with one child; a row whose `audience_id` differs from its parent's; a row whose
  `parent_id` names no row; an audience with zero or several root rows. **Zero expected, and every
  shape here means the write path let a tree be assembled one row at a time.** §8's first rule is the
  one check a migration *can* state; the rest of the list cannot be, which is exactly why it is here.
  **Nesting did not relax any of it**: `AUDIENCE(x)` is a leaf pointing at another audience's *root*,
  never at one of its interior rows, so a tree still has one parent per node and one audience per
  tree — and a row whose `parent_id` crosses an audience boundary is this check firing, not a feature.
- **11. A delegation that cannot expire.** A live `access_grant` with `is_delegated` true and no
  `valid_to`. The row rule forbids it and no constraint enforces it. **Half of the old delegation
  check is gone**: "or whose source assignment has ended" had an assignment to point at, and
  `delegation_of` is deleted (§4), so expiry is now the *only* guard against a delegation outliving its
  reason.
- **12. Two names that are one name, and a reference that points at an unnamed thing.** Three shapes,
  one namespace:
  1. A `role.code` equal to a `person_group.code` after case, whitespace and separator folding;
  2. either of those equal to a `selector_type.code`, **or any of the three equal to an
     `audience.code`** — the third table is in the namespace now, because `AUDIENCE(<code>)` resolves
     through it ([D-103](../decisions/round-10b.md#d-103--an-audience-may-name-another-audience));
  3. an `AUDIENCE` leaf whose `selector_arg_id` names an audience **whose `code` is absent** — legal on
     every column of both rows and unsayable as a constraint, because the check reads a third table
     ([F-10 shape 3](../open-questions.md#f-10--which-invariants-the-orm-cannot-express-and-who-writes-those)).

  **Zero expected; no single constraint spans three tables, and no constraint at all covers the
  reserved-word half or the null-code half**, so the write path carries all of it and this check asserts
  the write path exists. A row here is not untidy: a group called `MEMBERS` would silently rewrite the
  meaning of every expression in the system, **and an audience sharing an office's code is the same
  accident one arm over — the kind of the name decides which set a bare expression meant, and after
  D-103 there are three kinds that can collide instead of two.**
- **13. Orphaned permissions.** An assignable permission that **no live grant names**, at any scope.
  This check exists **because of** D-068 and survives D-100's deletion of `role_permission` by
  retargeting: the net was "no role grants it", and now nothing grants anything, so the question has
  to be asked of the grants themselves. **Expected: empty after a seeding pass.** A row means either a
  permission nobody has bundled into an office yet — fine on a roadmap, wrong in production — or a
  module was added and its grants were not. **Note what it cannot see:** a permission granted to *an*
  office but not to the office that arguably should have it. That residual is the accepted cost of
  D-068 and nothing closes it; it is a human reading the starter list in §12 against the catalog.
- **14. Offices nobody holds, and holder rows pointing at an office that is gone.** The first is
  **expected and is not an error**: a role nobody holds is either one about to be used or one stopped
  using and not deleted, and there is no third possibility, because a role has no period
  ([D-053](../decisions/round-04.md#d-053--a-role-is-valid-always-only-its-assignment-is-temporal))
  and cannot be switched off, only held or not held. Delete the mistakes, keep the ones on the
  roadmap. The second should be zero — the delete guard on `role` enforces it, and the check exists
  because a restored dump or a manually disabled guard bypasses it, and the loss is unrecoverable.
- **15. TIME-BOMB: an expression must be refused at the write, never survived at the read.** The
  successor to the old inclusion-cycle assertion, same shape, and it asserts a **guarantee rather than
  a set of rows**. Four halves are listed, and the last is the one that fails silently — **one of the four
  is now retired rather than active, which is what half 2 is doing there.**
  1. **A cycle must be unsayable, and there are now two walks to try.** Assert that saving is refused
     for **both** shapes — a node whose parent chain revisits a row inside one tree, **and** an
     `AUDIENCE` leaf whose target audience reaches back to the audience being saved, at any distance
     ([D-103](../decisions/round-10b.md#d-103--an-audience-may-name-another-audience)).
     **The second half is the one this document got wrong**, in D-101's words and therefore in its own:
     it claimed the write-time cycle walk had been deleted because *a tree cannot cycle*, and a forest
     of audiences naming each other is not a tree. Both are tested as a test that *tries*, not one that
     counts, because after the fact there are none to count. **Zero is the expected result every time
     this runs, and a non-zero result is not bad data but a missing guard.**
  2. **RETIRED, not answered: depth must be refused at the same moment, over the expanded tree.**
     [D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)
     deleted `selector_depth_limit`, and with it the check this half asserted — so **there is no save-time
     size rule left to test, and an assertion here would test nothing.** The number is kept in the list so
     that the halves keep the numbers other pages cite, and because what this half said *about* the bound
     outlived it: a bound measured per-audience was a bound on nothing, since five nested audiences three
     deep are fifteen deep and each passed a local check; and **the bound bounded height while an
     expression's cost is proportional to the number of *audiences* it reaches, which is breadth** — fifty
     `+ AUDIENCE(...)` leaves at depth one were legal under any depth bound and cost fifty fetches per
     check. **Both observations stand, and now nothing bounds either shape at all.** What survives
     operationally is not an invariant but the **standing report of the widest and deepest audiences and
     their cost per check** (§8, *The cost of composition*): no CI job, no refused save, nothing that fails
     if the report is not read. **That is D-081's case stated in its purest form — the rule's name
     outlived its mechanism, and this line exists to say which of the two happened here.** **A retired
     invariant is not a passing test, so nothing here asserts anything about size: a build that gets an
     enormous expression is a green build**, and [F-21](../open-questions.md#f-21--closed--no-report-a-tab-on-the-permissions-page-and-unbounded-cost-is-accepted-at-the-stated-size)
     is the open question about who reads what is left. Half 3 is
     therefore the whole structural story now: acyclicity at save, and nothing else.
  3. **No sharing table may exist, and the read path must grow neither a depth cap nor a cycle
     check.** The tree's one-parent rule is worth nothing if a later round adds a side table letting
     two expressions share a node — editing the shared node would silently widen every grant using it,
     which is D-091's inclusion hazard re-imported. `AUDIENCE` is not that table and must not become
     it: it points at an audience's whole expression, never at an interior node. And a forest met at
     read time by a hop counter is survivable-looking, so whoever meets one adds a cap, and **the cap
     becomes the thing that decides who a grant reaches** — which is the reason the read path must
     depend on the write guard rather than back it up. **This refusal used to be the back-up for half 2 and
     is now the entire design** ([D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)),
     which is why the temptation it guards against has got stronger rather than weaker: with no bound
     anywhere, a hop counter looks like the obvious way to make a check cheap, and the moment one exists it
     is deciding who a grant reaches. **A build that passes half 1 and fails this one is a build where the
     write guard has been removed and papered over, and it is the specific shape D-103 makes easy to reach**
     because nesting gives the read path somewhere to want a counter.
  4. **A referenced audience may not be emptied from the other end.** Saving must refuse to end or
     delete an audience while a live grant, or a live audience reachable from a live grant, names it
     (§8, *Rules*). It is a save-path refusal like the others and it belongs to this assertion for the
     same reason: **the data after the fact is perfectly well-formed** — an ended audience and a leaf
     naming it are both legal rows — and the damage is that every expression doing `X - <that one>`
     silently got wider. **Of the four halves this is the one most likely to be implemented as a
     warning**, because a delete that pops a confirmation dialog feels like sufficient care and a
     refuse feels like an obstacle. It is the one where a warning is not enough.

  **Why this is a CI assertion and not a report:** three of the four guards are walks over rows rather
  than comparisons within one row, which means they live in application code and no migration can emit
  them
  ([F-10 shape 3](../open-questions.md#f-10--which-invariants-the-orm-cannot-express-and-who-writes-those)).
  **A guard that lives in code is deleted by a refactor and the data looks fine afterwards** — which is
  why D-072's removal of the build-time greps is recorded as a weakening rather than a cleanup.
- **16. TIME-BOMB: no permission path may materialize a set.** The requirement is that
  **`operand_holds` decides membership for one person and never loads a set of ids to test containment
  in.** An operand is a **named** set — a row of `selector_type`, which is the only test the language
  has — for the purposes of the editor's preview ~~and the cache key~~ **("and the cache key" was the second
  reason this page ever wanted a set of ids, and
  [D-114](../decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation)
  removed it along with the key; only the preview wants one now, and only shows it to a human)**; in the
  resolver it is a predicate, and
  D-101 writes the distinction down precisely because an implementation is one lazy join away from getting
  it the other way and paying three thousand rows per check.
  ~~An operand is a named, materializable set~~ **for the purposes of this check: that was the wording
  here while §8 still claimed materializability was the test for what an operand may be, and
  [D-107](../decisions/round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)
  deleted the test, so this bullet carries its third and last surviving instance.** **The assertion itself
  does not move an inch:** `OLDER(18)` is precisely as materializable, and precisely as unmaterialized, as
  `MEMBERS` — a birth date read at the checked date and a membership row read at the checked date are both
  answers computed per person, and neither is allowed to become a list of ids. **This replaces the old "no permission path may inherit" assertion, whose
  subject — the unit hierarchy — no longer exists**, and it is the same *kind* of rule: a requirement
  about how the code computes, which no migration can state and no reviewer will notice missing until
  the first slow day.

  **Nesting is where this assertion earns its keep, so assert on a nested expression specifically.** A
  flat `ROLE(x)` is awkward to write as a set load and natural to write as a predicate; an inner
  `AUDIENCE(veterans)` inside an outer expression reads like a job for *"fetch the inner set once and
  reuse it"*, which is the tempting optimization, is correct as an answer, and is the thing that makes a
  check slow at exactly the depth the expression happens to have — **and since
  [D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)
  deleted the depth bound, that is now "at whatever depth somebody typed", with nothing above it.**
  **A test exercising only single-level
  expressions passes on an implementation that materializes at every nesting level.** Assert that the
  recursion takes a person and returns a boolean, and that no path between two audiences hands over a
  collection.
- **17. TIME-BOMB: `.admin` prefix matching, and any ordering comparison, must stay deleted.** Two
  parts, both prose since D-072 removed the SQL that could be grepped, which that entry records as a
  real weakening. **First, no step of the resolver may build a permission code by concatenating a
  resource with `.admin`,** and no permission may have `admin` as its *action* except **exactly one**:
  `system.admin`. [D-074](../decisions/round-06.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular)
  withdrew the four exemptions D-068 had allowed, so the allow-list is a single code and the check is
  an equality, not a set membership. Zero rows expected; the point of the entry is that the first
  version of the second half accepted five exceptions and the second accepts one, **because an
  allow-list is where a wildcard comes back to life.** **Second, and new: no comparison of
  `access_level` ranks, no `required_level` lookup, and no "at least `contribute`" anywhere.** D-099
  notes that the bug
  [D-012](../decisions/round-01a.md#d-012--status-strings-compare-by-rank-never-lexicographically)
  existed to catch — `'admin' < 'contribute'` read alphabetically — cannot occur in a system with no
  levels, which is a better fix than the guard. **The one ordering this model still performs is
  `right_kind` containment in the guardianship channel**, so a build where a second ordering has
  appeared has not reintroduced a bug; it has started reintroducing the ladder.

**Checks 3, 4, 5, 6 and 9 are the ones to wire to alerts, plus one half of 7.**

- **3 and 4 are the reports that stand in for the database rules that do not exist.** A row in either
  is not data drift — it is a save-path check that stopped running, which is the failure mode §5 of
  this document used to need a whole table for.
- **5 and 6 are the two reports round 10 created**, one for each mechanism it simplified: a deny that
  denies nothing, and an office granted without the membership operand. Both are lists a human reads,
  and both are the entire remaining control on their failure.
- **9 should email someone every time its result changes** — a new holder of `system.admin` is either
  a planned change or an incident, and either way someone should know within the hour.
- **Check 7 is the exception to the rule that this list is read rather than alerting on.** Its empty
  half — a grant reaching nobody — is inert and belongs on a weekly list. **Its wide half, a grant that
  got wider because something under a `-` stopped resolving, is the only entry in §11 that describes
  authority increasing**, and it should go to the same place check 9 does. **Splitting 7 is not
  tidiness**: a single report containing both halves has the wide row sitting between nineteen inert
  ones, which is how a widening gets read.
- **Checks 15 and 16 are CI assertions, not reports.** They are the automated guards on the two rules
  most likely to be "simplified" away when someone optimizes the resolver: the refusal of a malformed
  expression at the write, and the refusal to compute a set where a predicate will do. Both fail the
  build rather than silently changing who can do what, and both live in code rather than in the schema,
  which is why neither can be a migration. **D-103 moved weight onto 15 in particular** — with nesting
  available, the write path is guarding a graph rather than a row, and **since
  [D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)
  retired the depth bound it guards two things and not three: cycles, and not emptying something that is
  named.** **The acyclicity walk is therefore the only structural guard left on this module**, and check
  15's half 3 is the assertion that nobody quietly adds a second one inside the read path.
- **18. TIME-BOMB: `deprecated` and `hidden` must never change an answer, and `disabled` must change one and
  say whose.** [D-109](../decisions/round-13.md#d-109--nothing-a-rule-names-is-deleted-deprecated-hidden-disabled--and-a-tab-instead-of-a-report)
  replaced deletion with three states, and the states are only safe if two of them are inert. **Assert both
  halves, because each fails alone.** *Inertness:* resolve every live expression, then flip a
`selector_type`, `role`, `person_group` or `audience` row to `deprecated` and then to `hidden`, and **the
  resolved sets must be identical** — a rule that quietly stops granting because somebody tidied a list is the
  precise failure this design exists to make impossible, and it is exactly the kind of thing an implementation
  gets wrong by having the editor filter non-active rows out of a list it also uses to evaluate. *Effect:*
  flipping the same row to `disabled` must empty exactly the leaves that name it, in every expression, and the
  write must record the rules it touched, resolved before and after. **Third assertion, revised by
  [D-114](../decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation):
  the flag must be read live by the resolver, not compiled into a predicate.** It used to read *"the flag write
  must bump the ruleset version (§10)"*, which was the mechanism the deleted cache needed and a strange thing to
  require of a state; what is actually asserted is that flipping a row to `disabled` changes the next check, not
  the next rebuild. **The inertness half is unaffected by the deletion and the effect half is now easier to pass
  and harder to fake**: there is no `true` that survives a flip, because nothing persisted it, and a
  `deprecated` row that stops granting is now a bug in one function rather than a disagreement between two of
  them. **Nothing else in §11 can see this one**, because the flag is a legitimate value in a legitimate column
  and every row is well-formed on its own.
- **19. TIME-BOMB: no row, table or field anywhere may map a person — or a person and a code, or a person and
  an item — to a permission answer.** [D-114](../decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation)
  deleted the one table that did (`permission_cache`), and the wording here is deliberately the schema-shaped one
  it left behind, because **this invariant is the reason that table cannot come back later as an optimization.**
  Assert it the way a schema review asserts things: **no column pairing a person with a boolean that could only
  have come from a check, no table whose key contains `person_id` together with `permission_code` or a
  `selector_kind` / `selector_arg_id` or an item, and no `computed_at` sitting beside an answer.** Three shapes
  survive the sweep and each is legal for a reason worth repeating: **`ruleset_version`**, an integer about a
  *ruleset* that names no person and keys a compilation; **D-110's record of whom a grant reached**, a snapshot
  taken because it is a historical record — a rule naming a person who has since left must still read as it read
  then, which is the opposite of an answer kept for speed: it is *deliberately* stale, and nothing reads it to
  decide whether to allow something now; and **the audit payloads**, which record that a check happened and
  expire on their own schedule
  ([D-088](../decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)).
  **The first is a value in a column; the second and third are records of an event. There is no fourth, and what
  the check looks for is a row that is a *current* answer.**
  **This is enforced structurally, which is the strongest thing this page says about it and also its limit:** the
  schema has nowhere to put an answer, so an implementation cannot persist one by forgetting not to — it would
  have to add a table, which is an act. In
  [D-081](../decisions/round-06.md#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now)'s
  vocabulary the residue is a named convention, not a guard: **nothing stops a team from adding a
  `permission_cache` table again in a year, under load, at 2 a.m., because it is the obvious move and this
  invariant is a paragraph.** What the corpus holds against that is not a mechanism but a record — D-111's three
  rounds of invalidation policy, the `membership` write that appeared on no invalidation list while
  `membership.terminate` is exactly the ⛔ action a concerned guardian waits on, and the sentence in
  [`03-membership.md` §6](03-membership.md#6-membership-and-the-authorization-system) that demanded cache
  invalidation on every membership transition three rounds before the policy that failed to provide it was
  written. **Read that pairing before writing the migration.**
- **Where these go.** §11's reports now have a home rather than a schedule: **the permissions page has a tab**
  ([D-109](../decisions/round-13.md#d-109--nothing-a-rule-names-is-deleted-deprecated-hidden-disabled--and-a-tab-instead-of-a-report)),
  with **`Broken`** holding the rules that name something deprecated, hidden or disabled or that resolve to
  nobody — checks **1, 2, 3, 7's empty half, 12, 13, 14 and 18's second half** all land there — and
  **`Unusual`** holding rules that resolve correctly and look odd, which is where **6** lives. **Checks 7's wide
  half and 9 still go to a person rather than to a screen**, because both describe authority getting bigger
  while nobody edited a grant, and a tab nobody opened is not an alert. **Check 19 goes to neither tab**: it is not a fact about a rule, it is a fact about the
  schema, and the place it can be enforced is a migration review — which is the point of D-114 deleting the
  table rather than forbidding its contents in prose. **What the tab replaced is four rounds
  of "a standing report nobody is obliged to read"**, and the difference is not that the tab is a guard in
  [D-081](../decisions/round-06.md#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now)'s
  sense — nothing is blocked — but that **it is where the person writing the rule already is.**

---

## 12. What the organization starts with

Starting catalog. Expect to edit this heavily; it is a proposal, not a specification.

> **This section and [../appendix/permission-catalog.md](../appendix/permission-catalog.md) are
> the same list written twice, and they drift.** When this was reconciled, **22 documented
> permissions had no seed row** — among them a code five of the catalog's own seed roles assigned, and
> one of the two codes D-068 exists to protect. A further 12 were the `event.*` set, added to the
> catalog when events were designed and never carried here. **Under the old wildcard much of this was
> harmless**: a role holding a resource's `.admin` reached a code whether or not the row existed, so
> the catalog could advertise a capability the database could not name and nothing noticed. The
> permission editor was the only place the gap showed.
> **[D-068](../decisions/round-05.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle)
> removed that cushion,** and round 10 removed a second one: with `role_permission` gone there is no
> per-role list left to compare a catalog row against, so a documented code that nothing grants is
> now invisible in a way it never was. **Integrity check 13** reads the grants for exactly that reason.
>
> **There is no SQL check for this** — one side is a Markdown file. The discipline is the
> check: when adding a permission, add it in **both** places in the same edit, and treat a catalog
> row that no grant names as a bug of the same class as a missing migration. The reconciliation is
> mechanical enough to script: a diff of the codes the catalog lists against the codes that exist.
> Anything in the catalog and not in the database is a permission that cannot be granted; anything in
> the database and not in the catalog is an undocumented capability. Both were present at the same
> time.

**Off the catalog now, and named rather than quietly dropped:** the eighteen `dependent.*` codes (a
guardian's authority is a `right_level` on the relationship, not a bundle of permissions — D-074);
`scope.expose` and `scope.exposure.review` (the table they guarded is deleted — D-097);
`system.gate_exempt` (the gate it waived is deleted — D-100); every `position.*` code and the
appointment workflows behind them (D-100); and the codes that were about *bodies* rather than people —
a unit's renaming, restructuring and closing, and participation in a sub-unit — all deleted with the
hierarchy (D-097). `role.assign` and `role.unassign` survive but are **retargeted at `role_holder`**,
as do `role.create`, `role.view`, `role.edit` and `role.delete` — and `role.edit` no longer reaches
anyone's authority (§3).

**Roles are data, and the organization administers them at runtime.** This section seeds the
*permissions* — the vocabulary of things anyone might do — and one role. The role names used
throughout the docs are worked examples of composing those permissions into grants, not a fixed list.
Creating a role, naming it, filling it and deleting an unused one are all supported operations.

**What is seeded as a role, and it is one row: `counselors`, marked `is_system`**
([D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)).
A permanent, organization-wide population is the opposite of D-098's definition of a group (*"a
temporary set of members that do events together"*), and which table it lives in decides the
sensitivity that every safeguarding convention in this area hangs from. **It ships `is_system` so an
editor refuses to delete it**, and it confers nothing: this is a **set**, and being in it is worth
only what a grant naming `ROLE(counselors)` says
([D-005](../decisions/round-01a.md#d-005--permissions-are-grants-never-derived-from-identity)).
**Consistency requirement, and it is the import's problem too:** `MEMBERS * ROLE(counselors)` is only
as correct as that roster, so the import reconciliation of D-090 counts people marked as counselors in
the corpus against `role_holder` rows written.

**Everything else is starter material the organization edits** — including the `system_admin` office
the catalog sketches, whose reason for existing is that someone has to hold `system.admin` before
anything can be granted. **What §12 must fix, and does, is the *shape* rather than the list**: a
`system.` permission is seeded `applies_to = unit`, so it can never arrive through an item grant. That
is not a configuration choice — it is the structural guarantee that a shared item cannot hand someone
authority over the permission system, and it is now carried by a column value instead of by a resolver
branch (§2).

**What the organization starts with, in one list.** The platform ships:

- **The permission vocabulary** — each code marked `is_system` so it cannot be deleted or renamed —
  spanning people, accounts, membership, groups, audiences, roles, guardianship, item grants, audit,
  legacy import, reporting, the thirteen `event.*` codes, and messaging. **The one complete list is
  [../appendix/permission-catalog.md](../appendix/permission-catalog.md)**; this document deliberately
  no longer keeps a second copy of it, because the two copies disagreed for exactly the reason the
  note above describes.
- **`grant_scope_type`**: `unit` (the only row that is not item-scoped), `event`, `person_group`,
  `role`, and `document` (deferred).
- **`selector_type`**: the thirteen operands of §8's language, **every one of them seeded, `is_system`
  and implemented in the shipped evaluator, because there is no fourth combination and no third kind**
  (§8, *The selector registry*). **This registry is what both the grant editor's dropdown and the
  parser's reserved words read**, which is what D-101 means by *the language becomes data* — a new
  operand is a decision entry, a seed row **and a resolver arm in one release**, never a row typed into
  a screen and never a row shipped ahead of the code that evaluates it. `AUDIENCE` is the newest operand
  anyone *designed* ([D-103](../decisions/round-10b.md#d-103--an-audience-may-name-another-audience));
  `PERSON` was the last row to arrive **for two rounds** — it went in *thirteenth*, because two decision
  entries had used it
  for a whole round while this table did not carry it (§8, [D-104](../decisions/round-10b.md#d-104--a-permission-codes-last-segment-is-an-action-and-a-registry-that-prose-contradicts-is-a-fiction)) —
  which is the difference between a registry and a list of what somebody remembered. **The round after,
  [D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)
  deleted `LIST` and the table came back to twelve: the row that was added last and the row that was
  deleted last are not the same row, and the count is stated here rather than inferred from either.**
  **And twelve is now history in the past tense, not the present: round 12 seeded `OLDER` and `YOUNGER`
  together, so the count moved by two in one decision and nothing was deleted, which makes it the first
  round since `PERSON` in which this table only grew**
  ([D-107](../decisions/round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)).
  **Their arms ship in the same release as their rows, on the rule two sentences above, and their argument
  is an integer — the first argument kind here that is not an entity reference**, which is why the merge
  and orphan scans of §11 walk five kinds and not six (§8, *A hand-named person is now a keyless
  reference*). `GRANTS` is refused and therefore absent (§8).
- **Two audiences, both `is_system`, and both must have a `code`**: `everyone`, whose expression is
  `EVERYONE`, and `all_members`, whose expression is `MEMBERS`. **The code is not cosmetic any more** —
  since D-103 it is the only way another audience can name them, so a seeded row without one is a
  piece of the resolver's vocabulary that nothing can compose with, and §11's check 12 is the net for
  the leaf side of that. **Whether `code` should simply be *required* on an `is_system` audience rather
  than merely seeded is a question this document does not settle** (§13). **The parameterized seeded
  audiences are gone**, and their three
  names are worth tracing because each became something smaller: `unit_participants` is `MEMBERS`
  (there is one unit), `unit_leaders` is `ROLE(x)` — **and it is the case this document had to correct
  in round 6, because the stored rule matched nobody while every grant aimed at it looked granted,
  which is the cautionary tale §8's evaluation rules are written against** — and `guardians_of` became
  **nothing at all**, which is the interesting one: it was first read as the operand `GUARDIANS(person)`, and
  that operand's row has now been deleted
  ([D-113](../decisions/round-13.md#d-113--the-guardianship-channel-has-no-expression-guardians-is-not-a-selector)),
  because a guardian's authority comes from the guardianship channel's `right_level` over the child rather than
  from anything an audience could name. **So the honest trace for the third name is "became a channel, not a
  smaller expression"** — the only one of the three that did not shrink into the language. **The bound spelling
  the old text offered (`GUARDIANS` on a grant about that person) was never writable anyway**: the registry says
  `person` is not a `grant_scope_type`, so the binding check refused it on every scope that exists. Nothing needs a
  row per unit any more, because there is one unit and no per-unit audience to parameterize. **What used
  to be said here — that a member row on either `is_system` row is refused — is retired rather than
  answered**, because the row it refused no longer exists to be written: `audience_member` was deleted with
  the `LIST` operand, and its `is_system` refusal is a rule whose mechanism is gone and whose name does not
  need to survive it (§8,
  *`audience_member`, re-roled as the `LIST` leaf — deleted by D-105*). **What of that sentence still
  stands is the category it was protecting:** seeded rows are the resolver's own vocabulary rather than a
  set somebody curates, and editing `everyone`'s *expression* is exactly as much a category error as adding
  a name to it ever was — the refusal just moved from a row nobody can write to the screen that should not
  offer the edit.
- **The `counselors` role**, above.
- **One seeded grant, and it replaces a hard-coded sentence: `event.answer.view` on an event, aimed at
  an audience whose expression is `ORGANIZERS`** — the code in the catalog's singular spelling, which is
  the registered one
  ([D-102](../decisions/round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it),
  amending [D-061](../decisions/round-05.md#d-061--event-answers-are-read-by-that-events-organizers)).
  "Answers are read by that event's organizers" used to be prose the resolver implemented; now it is a
  row a reader can find, narrow, or delete, and it is the worked example of a **bound operand**:
  item-scoped, argument-less, meaning *the organizers of whichever event this grant is on* — which is
  why it is one grant in the seed rather than one per event. **[D-062](../decisions/round-05.md#d-062--organizers-are-appointed-on-the-event-not-granted)
  is not contradicted**: the appointment still grants nothing by itself, because an operand is a set
  and not a grant. **It is written without `MEMBERS`** and must not be "corrected" to include it: an
  organizer appointed for one weekend is not required to be a paying member, and D-062's appointment
  model assumes exactly that.
- **The effects and the enums.** `allow` and `deny` arrive with the schema, as do the two values of
  `applies_to` and the two of `right_kind`. **This is the same argument the five levels used to be
  given** — a comparison the organization can edit at runtime is a security control with no owner —
  only now there is no comparison to edit, which is the point of
  [D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality).
  The old sentence about `revoked` at rank 0 and `admin` at rank 40 is deleted with the ranks.

A few of the surviving codes carry a decision in their shape, and those are worth naming:

- **`person.merge` and `person.redact` are separate codes**, not flavours of `person.edit`. **They are
  separate for reach, not for irreversibility, and the two words were used as one here until round 9.**
  `person.redact` is irreversible — that is what an erasure is. `person.merge` is **not**:
  [D-087](../decisions/round-07-08.md#d-087--merge-chains-stay-because-reversing-a-merge-is-a-supported-operation)
  made reversing a merge a supported operation, with the undo written as its own audit entry. What both
  codes share is that they act on **every row of a person's life** rather than on one field, which is
  the reason they were pulled out of `person.edit` — and with no `person.admin` to imply them (D-068),
  a role that reaches them does so by listing them, visibly.
- **`person.view` reaches the whole record, and round 10 made it reach further still.** Since
  [D-083](../decisions/round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)
  there is no privileged corner of the record for it to stop outside: whoever holds it over a person
  reads their descriptive values — the allergy list, the insurance number, the note about who the child
  actually lives with — on the same grant that reads their name
  ([09-attributes.md §4](09-attributes.md#4-who-may-read-and-who-may-write)). **And since D-097, a
  grant of it at the unit reaches every member in the organization**, because that is what "at the
  unit" now means; the safeguarding property that used to narrow it — access to a body's children
  granted *by that body* — is recorded as lost in §5 and in D-097. It is therefore the widest read
  permission in the system, and **the catalog's sensitivity mark is where that has to be visible**
  ([D-086](../decisions/round-07-08.md#d-086--a-sensitivity-mark-grades-what-a-grant-exposes-not-the-table-it-reads)):
  the honest mark is the top tier, worded around *whose* data a grant exposes rather than around a
  category of fields, because a category is what D-083 deleted.
- **`audit.view` is graded against what the trail quotes, not against what a log is usually for.**
  `audit_log` carries before and after images, and since
  [D-085](../decisions/round-07-08.md#d-085--the-identity-machinery-stays-structured-the-boundary-is-rules-not-sensitivity)
  those images are the only place a child's past descriptive values exist; reading history has to sit
  in the same tier as reading a person. **D-088 bounds the exposure to 24 months and fixes nothing**,
  and the bound is the realistic control for an organization of this size rather than an argument that
  the mark is right — see §9 and
  [AT-4](../open-questions.md#at-4--is-one-permission-enough-to-guard-a-trail-that-holds-person-data)
  for why two years is not a short interval when the question is about a child.
- **`attribute.define` is the narrow half of a deliberate pair**: values are open to anyone who may
  already edit the person, so that the fact gets recorded, and codes are held by few people, because
  the codes are what make the data queryable
  ([09-attributes.md §2](09-attributes.md#2-attribute_definition--the-vocabulary)). An ordinary
  permission — no namespace, no resolver branch, no structural consequence.
- **`person_group.member.manage` is how "joining a group is somebody else's act" is said now**
  ([D-098](../decisions/round-10a.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority),
  carrying
  [D-095](../decisions/round-09.md#d-095--units-carry-no-restrictions-joining-one-is-somebody-elses-act)
  across the rename): held at the unit, where it reaches every group, or granted on one group as an
  item. **There is no self-scoped variant and none will be added** — nobody writes themselves onto a
  roster. Its counterpart for offices is `role.assign` 🔒🔒, and the gap between the two marks is the
  whole content of D-100's "why two tables".
- **`role.unassign` is one of the only two things that end authority** (the other is a holder row's
  `valid_to`), because a role has no period (D-053) and nothing forces a holder row to end (D-071).
- **`membership.terminate` expels**, and is restricted as such; `membership.lapse` is an
  administrative end for non-payment. **Neither now changes what a role grants** — that used to be the
  interesting part of both, and it was the membership gate's business, which is gone. A lapse changes
  what `MEMBERS` means, which is a different thing, in a different place.
- **`event.presence.mark` stays a separate code from `event.manage_participants` on purpose**, and
  **`event.register_self` *is* the eligibility rule**
  ([D-060](../decisions/round-05.md#d-060--eligibility-is-capability-there-is-no-separate-rule-engine))
  rather than an expression of one. Under the ladder the first sentence meant "one rank below"; with
  ranks gone it means what it should have meant all along — **a volunteer leader is handed the register
  without being handed the roster** — and that difference is now two grant rows rather than a rung.
- **There is no wildcard at all, and that is worth noticing.** `dependent.admin` was the last
  deliberate one, and D-074 replaced it with `right_level = write`, which does the same job **without
  being a permission**. The residue is the opposite problem: with no wildcard, nothing implies
  anything, so a role that should have a new permission must be told (check 13 is the net).
- **Reporting is seeded coarse, and left open on purpose.** Only `report.view` and `report.export` are
  starters. Whether reporting is per-report or one permission with row-level filtering is still open
  (catalog §12). Do not ship both shapes; pick one when reporting is designed.

> **`system.admin` is deliberately a single top-level permission**, not a
> per-resource one. Holding it satisfies everything, and check 9 in §11 alerts on its
> holders. Keeping the most dangerous capability concentrated and alarmed is safer than
> spreading equivalents of it across every resource. **Under the deleted ladder it was also the level
> called `admin**, which is how this corpus came to have two unrelated things named "admin" and to
> need a paragraph telling readers they were different. That paragraph is now about one thing.

---

## 13. Open issues

- The complete permission catalog and real role definitions (§12) — needs your input. **The question
  changed shape with
  [D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape):**
  it used to ask which roles are marked `requires_membership = false`, a per-row switch. There is no
  switch now, so the question is **which starter grants are written with `MEMBERS` in the expression
  and which are not** — and it has to be answered per grant rather than per role, with check 6 (§11)
  as the net and the seeded grants as the default.
- **Whether the API should refuse a check that names an item for a unit-only code (§2).**
  `applies_to` is deliberately a save-time rule, and D-099 says so in as many words, so the mismatched
  *grant* cannot exist — but a *caller* that asks `can(person, 'event.create', 'event', 1204, …)`
  gets the unit's answer rather than an error. **Assumption, not a ruling:** the honest answer is a
  refusal at the API layer naming the code and the scope, because a caller that asks that question has
  a bug worth surfacing. Nothing in D-097..D-103 settles it.
- ~~**What the default `selector_depth_limit` should be (§8).**~~ **Moot, not answered, and deleted rather
  than closed** ([D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)).
  The bullet asked what number a parameter should hold; the parameter is gone, so there is nothing left to
  tune, and answering "is 3 right?" is not a possible act. **What the bullet had discovered on the way is
  still open and is now the only half of it that is:** it noted that a bound on *height* never bounded the
  thing an expression actually costs, which is how many *audiences* it reaches — a depth-3 limit allowed a
  wide flat sum of twenty `AUDIENCE()` leaves and priced each one at a fetch. **With no bound at all now,
  neither shape is bounded — **and round 13 answered that, too, in the negative.**
  [F-21](../open-questions.md#f-21--closed--no-report-a-tab-on-the-permissions-page-and-unbounded-cost-is-accepted-at-the-stated-size)
  closed with *nothing bounds what an expression costs, and at the stated size that is accepted rather than
  merely unaddressed*, so the question is no longer "does it need a limit, and who decides" but *what would
  make somebody wish it had one* — and that has a number now:
  [D-112](../decisions/round-13.md#d-112--the-systems-scale-is-stated-hundreds-of-people-tens-of-registrants-per-event)
  states the size, and states the trigger (a few thousand people, or a thousand registrants on one event) at
  which the unbounded cost stops being affordable. **A fake question was retired and a real one was
  answered with a trigger instead of a parameter**, which is the same move this page has always preferred:
  inventing a number nobody asked for is not this page's call, but naming the size at which you would
  reconsider it is, and is cheaper. **The placeholder value of 3 is gone with the column, and the
  standing report of §8 and §11 half 2 is what a real number would eventually be argued from.**
- ~~**Whether an expression's *fingerprint* should be computed on save (§8).**~~ **Refused, not
  implemented and not deferred** ([F-14](../open-questions.md#f-14--closed--nothing-computes-semantic-equality-of-two-expressions-and-nothing-will),
  [D-110](../decisions/round-13.md#d-110--the-expression-is-the-record-of-whom-a-grant-reached)).
  Two expressions with the same meaning are two different row sets, and *"you already granted exactly
  this set on that item"* no longer falls out of storage — **that is accepted, not mitigated.** The
  watered-down version this bullet proposed (a derived fingerprint, a warning, never a refusal) was put
  to the same question and refused with it, because computing it means deciding that two expressions mean
  the same thing, and this module computes *who is in a set*, never *what a string means*. A fingerprint
  is a semantic-equality function wearing a warning badge: either it is exact, which is undecidable
  without evaluating both sides, or it is a hash of a normalized string, which two spellings of one set
  will fail to match and will therefore produce a warning that is wrong in both directions.
- **The per-item reach preview (§8) is a screen nobody has designed.** `PLACED` means different people
  on different events, so the editor's expanded set must be computed *for an item* and say so on
  screen
  ([D-102](../decisions/round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)).
  D-091 made the expanded set a requirement; D-102 made it depend on an input the grant does not
  contain. Which item the editor picks by default — the grant's item, an event the writer chooses, the
  next event with registrants — is not decided anywhere.
- ~~**`WHITELISTED` (§8): no stored state to name, so no selector.**~~ **Closed by refusal**
  ([F-20](../open-questions.md#f-20--closed--whitelisted-stays-unseeded-because-there-is-no-state-to-evaluate-and-the-feature-arrives-anyway)).
  The three readings this bullet listed — `source = staff`, promotion off the waitlist, a new column on
  `event_registration` — were never narrowed, and that is the answer rather than an evasion: **there is no
  state to evaluate, so there is nothing for an operand to resolve to**, and picking a meaning in order to
  seed a row would invent an events feature from the authorization module. **The feature it was wanted for
  arrives anyway**, which is the part that made this a closure and not a parking lot: whoever needs "these
  few people" writes grants, or a `GROUP(x)`, or `PERSON(a) + PERSON(b)`. What is kept from this bullet is
  its discipline — the row stays unseeded so a question cannot become a word in a grammar by being typed
  often enough.
- **`PERSON(x)` — closed by this round, and the way it closed is the open item.** Two decision entries wrote
  `PERSON()` and the seeded registry in §8 did not contain it, so this page concluded the operand did not
  exist and read both examples as `LIST`. **That was the wrong reading** (it cannot express D-103's example),
  the registry was the side that was wrong, and the row is seeded now: `argument_type = person`, and the
  table that carries it holds **thirteen** rows today — thirteen while `LIST` existed, **twelve for
  exactly one round** after
  ([D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other))
  deleted it, fourteen after round 12 seeded `OLDER` and `YOUNGER`, and **thirteen again** once round 13 deleted
  `GUARDIANS` ([D-113](../decisions/round-13.md#d-113--the-guardianship-channel-has-no-expression-guardians-is-not-a-selector)).
  **The two thirteens are not the same thirteen** — one had `LIST` and no age operands, the other has both and
  no guardian operand — which is the whole reason a count in this corpus travels with its history. **The twelve
  is quoted here only
  because this bullet is where the count was recorded when it was true**; a reader who takes it forward
  repeats, one round late, exactly the mistake this bullet exists to record.
  [D-107](../decisions/round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)
  is the entry that moved it, and it moved the count by growing the table rather than by trading a row.
  **The point of recording the number twice stands: it is cheap to check and it has been wrong before.**
  The operand that was added to fix this drift turned out to be the one the other half of the drift was
  arguing for ([D-101's amendment](../decisions/round-10b.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree),
  [D-104](../decisions/round-10b.md#d-104--a-permission-codes-last-segment-is-an-action-and-a-registry-that-prose-contradicts-is-a-fiction)).
  **What is still open is the class, not this operand:** nothing in this module, or in this repository,
  compares the dotted tokens these documents write against the seeded registries they describe, so the same
  drift will happen again in whichever table is written next. D-104 adopts a hand-run report over the
  documents as the answer, and states plainly that **a report nobody runs is a convention** — there is no CI
  here to make it a guard, and no layer of this spec can tell a writer that `PERSON(` had no row behind it.
- ~~**Whether the `LIST` gloss is enough, or the operand should be renamed `ADDED` (§8).**~~ **Moot, not
  answered, and deleted rather than closed**
  ([D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)).
  D-103 recorded the name as the weak part of the design and refused the rename on cost grounds, and this
  bullet added that the cost rose every round it was deferred. **There is no operand left to rename**, so
  the question cannot be answered in either direction; the argument simply lost its subject. **It is
  deleted rather than marked closed because "closed" would imply somebody weighed it.**
- **Whether two people editing one audience is handled by a lock, a queue, or nothing (§8).** Adding a
  name used to be an insert into `audience_member`, where two clerks adding two people could not collide.
  It is now an edit of one expression, so they can, **and a silent lost update removes somebody's access
  without any row recording that it happened.** [D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)
  states the obligation — an optimistic-concurrency check or a queue — and puts it on the editor rather
  than on the schema, because the table whose absence caused it no longer exists to carry the note.
  **Nothing in this document decides which of the two it is, and nothing detects the failure after the
  fact**: the audit trail records the write that happened, not the one that was overwritten.
- **Whether a person merge repoints every leaf that named the absorbed person, and who tests it (§8,
  §11 check 2).** The requirement is D-105's and is not open; **what is open is that no layer can express
  it.** `selector_arg_id` has no foreign key
  ([D-011](../decisions/round-01a.md#d-011--scope_id-on-access_grant-is-polymorphic-with-no-foreign-key)),
  so the merge reassignment table has to be told about `audience_operand` the way it was told about every
  other person-referencing table, **in all five argument kinds that name an entity**, and the orphan scan that would otherwise
  catch it is both late and blind — late because it runs nightly, blind because a merge that leaves the
  absorbed row in place produces no orphan at all. It belongs to
  [F-10](../open-questions.md#f-10--which-invariants-the-orm-cannot-express-and-who-writes-those)'s register
  for exactly that reason, and it is the first item on that register where **the failure direction is a
  grant that denies everybody**: `EVERYONE - PERSON(x)` with an un-repointed `x`.
- **Whether the reference listing is actually cheap (§8, §10).** D-103 registers the assumption: "which
  live grants name this audience, and at what depth" is one indexed query over the leaf rows, cheap at
  this organization's size, **unverified at any size**. It is on the save path of a screen a person is
  standing at — and since [D-114](../decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation)
  **it is load-bearing for a policy and not only for a screen**: the blunt version bump it used to stand in for is
  deleted, and what replaces it — dropping exactly the compilations that embed a changed expression — needs this
  listing's **direction**, the reverse one, run transitively rather than one hop at a time (§10). **So the
  assumption got more load-bearing rather than less, and this bullet is where that is registered rather than §10
  pretending it is settled.** If the import corpus's row-count estimates are wrong there is no blunt instrument
  left to fall back on, because there is nothing left to invalidate for everyone at once; what there is instead is
  D-112's trigger and this bullet.
- **Whether `audience.code` should be required rather than optional on `is_system` rows (§8, §12).**
  The seeded audiences are the resolver's vocabulary and cannot be composed with by anything that lacks
  a code, which makes the code mandatory in every practical sense while leaving it nullable in the
  schema. **A check is being asked to assert what a column could have guaranteed**; making the column
  required-where-`is_system` would be the honest fix and is not this document's call to make.
- ~~Whether a nested audience's past reach should be reconstructable (§8, *Three named sets*).~~ **Answered in
  round 13, in the direction of not reconstructing it:** the record of whom a grant reached **is the
  expression** ([D-110](../decisions/round-13.md#d-110--the-expression-is-the-record-of-whom-a-grant-reached),
  closing [F-17](../open-questions.md#f-17--closed--the-expression-is-the-record-so-a-nested-audiences-past-is-recomputed-and-never-promised)).
  `GROUP(x)` still answers *"was she in it on 1 June 2024?"* from its dated rows and `AUDIENCE(x)` still does
  not, and **this no longer counts as a gap, because the system never promised the answer** — what it keeps is
  the words, and D-109's refusal to delete the nouns is what keeps them evaluable. **What is logged as history is
  a rendering on a date, not a roster**, and the roster alternative was refused because it stores, against
  [D-088](../decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)'s
  window, a per-person record of people who were never granted anything.
- **Whether `membership` belongs in `grant_scope_type` (§6).** It is not seeded, and that is an
  inference from what D-097 and D-099 list rather than a ruling; the old seed had the row.
- Whether `valid_to` should be mandatory for high-authority holder rows and long-lived item grants
  (§4, §6).
- Polymorphic `scope_id` vs a `grantable_item` supertable (§6) — a real fork, now covering
  `selector_arg_id` too.
- ~~How long a `permission_cache` entry may live (§10).~~ ~~**Closed in round 13, and the answer is: it does
  not live, it is rebuilt.**~~ **Closed twice, and the second closing deleted the subject rather than answering
  it.** Round 13 spent F-6's four rounds on that number and then removed the need for it
  ([F-6](../open-questions.md#f-6--closed--the-permission-cache-is-rebuilt-nightly-on-any-ruleset-write-and-on-request),
  [D-111](../decisions/round-13.md#d-111--the-permission-cache-is-rebuilt-nightly-on-any-ruleset-change-and-on-request)):
  a nightly full rebuild, immediate invalidation on any ruleset write, an operator's request, and **no TTL and no
  asymmetric TTL** — which is why `expires_at` left §10's table that round and `ruleset_version` stayed. **Round
  14 then deleted the table whose lifetime this bullet asked about**
  ([D-114](../decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation)).
  **Neither closing was wasted, and the pairing is the useful part:** the first closed the TTL question by making
  a TTL unnecessary, and the second found that the rebuild had quietly inherited the thing the TTL was for — the
  staleness window moved from the row to the schedule, which is a harder place to notice it. **What is left open
  here is nothing.** `ruleset_version` survives as a compilation key with its bump set cut to `audience_operand`
  and `selector_type`, and the affordability question this bullet ended on is answered the same way D-112
  answers it — by a stated size, now with no job to afford at all.
- ~~Cache vs materialized effective-permission table (§8, §10).~~ **Dissolved, not decided** —
  [F-7](../open-questions.md#f-7--dissolved--a-nightly-rebuild-of-cached-answers-and-a-materialized-effective-permission-table-are-one-job).
  A nightly full rebuild of cached answers and a nightly materialized `effective_permission` table turned out to
  be **the same job with two names**, and the design was chosen for a reason outside the question. Recorded as
  dissolved on purpose: **a dissolved question is the kind that comes back if nobody writes down that it
  dissolved**, and D-091's history-not-performance framing is exactly where it would come back from.
  **Round 14 dissolved the other half of the identity**: with the answer cache deleted
  ([D-114](../decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation))
  there is no rebuild left to be confused with a history table, so what remains of the question is only the
  history side — and D-114 records that deleting the cache **did not** answer it, since a table of today's
  answers was never a record of 2011. **If it comes back, it comes back as that question, and D-114's invariant
  19 is the thing it has to argue with.**
- Retention policy for `access_log` — legal input required
  ([F-8](../open-questions.md#f-8--retention-policy-for-access_log)).
- Whether `access_log` needs human annotation (recommend a separate table if so).

**Resolved and no longer open**, kept visible so the reasoning survives: **whether a role may be held
by a rule — [F-12](../open-questions.md#f-12--closed--may-a-role-be-held-by-a-rule-as-an-audience-is), closed
by D-100, and the answer is no**; whether an audience may compose other sets (**yes, three times over,
and the third answer is the settled one**: D-091 through an inclusion graph, D-101 through an
expression naming only rosters, and D-103 through `AUDIENCE()` — the edge table stays deleted and the
edges are leaves); whether a saved rule may be reused by name (**yes, and only if it has a `code`,**
which D-103 settled after D-101 answered it in effect by accident); whether permissions depend on
membership status (**the gate is deleted and membership is an operand**, with the posture opt-in per
grant); the bulk exposure tool (removed — D-045), the exposure model itself (deleted — D-097), the
level ladder (deleted — D-099), positions and their appointment workflows (deleted — D-100), and
background-check permissions (removed — D-043).

All tracked in [../open-questions.md](../open-questions.md).
