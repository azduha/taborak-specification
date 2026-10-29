# Data Model — Authorization: invariants, seed data, open issues

The invariants a correct implementation must hold, the rows the platform ships
with, and what is still open on this part of the model.

**Section numbers are shared across the six parts** and never renumbered, because other
pages cite them by number and their anchors are built from them: [05-authorization.md](05-authorization.md) holds §1–§7, [05a](05a-audience-and-grammar.md) §8 (the `audience` table, the grammar, the selector registry), [05b](05b-expression-tree.md) §8 continued (the tree and what each operand costs), [05c](05c-access-log-and-resolver.md) §9–§10 (`access_log` and the resolver), and [05d](05d-invariants-and-seed.md) §11–§13 (invariants, seed data, open issues), and [05e](05e-keys-and-callers.md) §14–§17 (a key, and what it may hold).

---

## 11. Invariants to verify

Each entry states what it counts and what a non-zero result would mean. They are verified by
something, in whichever way the implementation chooses. **The numbering has no holes and does not
move**: other pages cite these checks by number, so a check whose subject is gone keeps its number
and says in one line what stands in its place.

**No check reads a column this schema does not have.** `requires_scope`, `permission_level`,
`scope_exposure` and `system.gate_exempt` are not columns of anything described here, and no entry
below counts them.

Some entries assert **behaviour rather than program text**, because there is no stored resolver text
left to read and behaviour is the strongest form still available —
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
  and this is that trade's compensating control. **An orphaned operand is normally the quiet half**: it
  resolves to the empty set, so the grant is inert rather than dangerous, and inert authority is the
  failure nobody notices.

  **`selector_arg_id` also points at `audience`**
  ([D-103](../decisions/round-10b.md#d-103--an-audience-may-name-another-audience)),
  **and an orphaned `AUDIENCE` leaf is not necessarily quiet**: quietness is a property of the leaf's
  *position*, not of the leaf. Reached through `+` or `*` it removes people; reached through `-` it
  adds everyone the missing audience was excluding. **Run one scan with two outputs**, splitting on
  whether the orphan sits under an odd number of `-` right-hand positions, and **route the wide half to
  check 7's second report rather than to this one's** — an orphaned `ROLE` leaf belongs with inert
  authority and an orphaned `AUDIENCE` leaf belongs with the grants that got wider. The operator is
  what decides the direction of a failure (§8's evaluation rules).

  **This scan is a backstop, not the mechanism.** Every hand-named person in the system is a leaf in
  this column with no key behind it, so a person merge and a redaction are required to **repoint**
  those leaves in all five argument kinds that name an entity (§8, *A hand-named person is now a
  keyless reference*). **The scan cannot stand in for that requirement, for two reasons.** It runs the
  following morning, and an expression resolves wrong from the moment of the merge. And **it only
  fires when the absorbed person's row is actually removed** — if the merge leaves the row in place, as
  any design that keeps its history will, the leaf still names an existing id, this check reports
  nothing, and the grant quietly keeps a person who no longer signs in. On the allow side that is inert
  — **the failure narrows the set and stops there**; **under `-` the same failure widens it, and
  `EVERYONE - PERSON(x)` with an un-repointed `x` denies everybody.** **Why the halves are reported
  apart:** they do not differ in volume, **they differ in which direction a wrong answer moves
  access**, and only one of those directions can grant
  ([D-106](../decisions/round-11-12.md#d-106--a-failed-operand-stays-the-empty-set-the-missing-half-was-a-report-not-a-refusal)).
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
  case worth a human eye, because it authorizes a lapsed member silently and forever. The report is
  deliberately narrow: **it has to be short enough to actually be read**.
- **7. A grant aimed at an audience that reaches nobody — or everybody.** A live `access_grant` naming
  an audience whose expression contains no operand that can hold a person — a sum of `PERSON(x)` leaves
  naming people who have been merged away,
  a `GROUP(x)` whose group has ended, an operand whose `selector_arg_id` is orphaned, **an
  `AUDIENCE(x)` leaf whose target has ended or gone (§8, and D-103)**, a tree that cannot be assembled.
  **The grant join is what makes this check worth running**: an empty audience on its own is a work in
  progress, but an empty audience a live grant points at is a permission configured, visible in an
  editor as granted, and reaching nobody — and it is the inert authority an administrator cannot see
  from the grant screen.

  **Run the same scan for the mirror-image case and report it separately, because it is the more
  dangerous of the two:** an empty operand reached through `-` makes the expression **wider**, so
  `EVERYONE - AUDIENCE(x)` with `x` gone reaches *everybody* — an allow that meant to exclude now
  includes, and a deny that meant to exclude now falls on everyone. **Why these are two reports and not
  one:** a widening is not a noise, it is a direction, and **a wide failure is only better than a narrow
  one when somebody is reading**
  ([D-106](../decisions/round-11-12.md#d-106--a-failed-operand-stays-the-empty-set-the-missing-half-was-a-report-not-a-refusal)).
  **The permissions page's tab ([F-21](../open-questions.md#f-21))
  therefore carries a second column naming *which* leaf failed, not merely that one did, aimed at the
  audience's owner** — a listing with somebody's name beside the row. **So the control here is *report,
  twice over*, and not a refusal:** nothing stops an audience whose leaf is broken from being saved
  ([D-107](../decisions/round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)).
  `MEMBERS - AUDIENCE(x)` is the **narrow** version and it is the easier one to miss: **the exclusion is the grant's whole point and its
  target is gone, which reads on screen as a grant that still names the audience it excludes.** The
  save-time refusal (an audience named by anything live cannot be ended or deleted) is the primary
  control; this check is the one that fires when the refusal was bypassed by a restore or a manual
  delete, and unlike the empty side it should alert rather than be read weekly.
- **8. A grant whose expression contains `EVERYONE`.** Live, and naming `EVERYONE` anywhere in the
  tree. Not a violation: it is what a public page is for, and holding `EVERYONE` directly is legal.
  It is on the list because a language with union in it lets one edit widen a grant to every person
  with no account and no membership, and the person who made the edit is the only control
  (§8, *What audiences do not do*).
- **9. Holders of `system.admin`.** Everyone with a live allow of it, however they came by it —
  through a personal grant or through an expression naming an office. This should be a very short
  list, and it should alert on change. **A key never appears on it and cannot**: that grant is refused when
  it is saved and counted by check 20, so a list containing only people is also the evidence that the
  refusal held.
- **10. Expression trees that are not trees.** Any of: a node with a selector, or a leaf with an
  operator; a node with one child; a row whose `audience_id` differs from its parent's; a row whose
  `parent_id` names no row; an audience with zero or several root rows. **Zero expected, and every
  shape here means the write path let a tree be assembled one row at a time.** §8's first rule is the
  one check a migration *can* state; the rest of the list cannot be, which is exactly why it is here.
  **Nesting relaxes none of it**: `AUDIENCE(x)` is a leaf pointing at another audience's *root*,
  never at one of its interior rows, so a tree still has one parent per node and one audience per
  tree — and a row whose `parent_id` crosses an audience boundary is this check firing, not a feature.
- **11. A delegation that cannot expire.** A live `access_grant` with `is_delegated` true and no
  `valid_to`. The row rule forbids it and no constraint enforces it. **There is no source grant for the
  check to point at** — `delegation_of` is not a column of this schema (§4) — **so the delegation's own
  expiry is the only guard against it outliving its reason.**
- **12. Two names that are one name, and a reference that points at an unnamed thing.** Three shapes,
  one namespace:
  1. A `role.code` equal to a `person_group.code` after case, whitespace and separator folding;
  2. either of those equal to a `selector_type.code`, **or any of the three equal to an
     `audience.code`** — `audience` shares the namespace, because `AUDIENCE(<code>)` resolves
     through that table ([D-103](../decisions/round-10b.md#d-103--an-audience-may-name-another-audience));
  3. an `AUDIENCE` leaf whose `selector_arg_id` names an audience **whose `code` is absent** — legal on
     every column of both rows and unsayable as a constraint, because the check reads a third table
     ([F-10 shape 3](../open-questions.md#f-10--which-invariants-the-orm-cannot-express-and-who-writes-those)).

  **Zero expected; no single constraint spans three tables, and no constraint at all covers the
  reserved-word half or the null-code half**, so the write path carries all of it and this check asserts
  the write path exists. A row here is not untidy: a group called `MEMBERS` would silently rewrite the
  meaning of every expression in the system, and an audience sharing an office's code is the same
  accident one arm over — **the kind of a name decides which set a bare expression meant.**
- **13. Orphaned permissions.** An assignable permission that **no live grant names**, at any scope.
  With no wildcard, a permission nothing bundles grants nobody, so the question is asked of the grant
  rows themselves and of nothing else (D-068). **Expected: empty after a seeding pass.** A row means either a
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
- **15. TIME-BOMB: an expression must be refused at the write, never survived at the read.** It asserts
  a **guarantee rather than a set of rows**. Four halves keep their numbers; the last is the one that
  fails silently, and half 2 is retired rather than active.
  1. **A cycle must be unsayable, over both walks.** Saving is refused for **both** shapes — a node whose
     parent chain revisits a row inside one tree, **and** an `AUDIENCE` leaf whose target audience
     reaches back to the audience being saved, at any distance
     ([D-103](../decisions/round-10b.md#d-103--an-audience-may-name-another-audience)).
     **A forest of audiences naming each other is not a tree**, so *"a tree cannot cycle"* is not a proof
     of safety and the cross-audience walk is not optional. Both are tested as a test that *tries*, not
     one that counts, because after the fact there are none to count. **Zero is the expected result every
     time this runs, and a non-zero result is not bad data but a missing guard.**
  2. **Retired, and it asserts nothing: there is no save-time size rule to test.**
     `selector_depth_limit` is not a parameter of this system
     ([D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)),
     so an assertion here would test nothing — **a build that gets an enormous expression is a green
     build**. The number stays in the list because other pages cite these halves by number. What is true
     of size is that **neither shape is bounded: height is unlimited, and an expression's cost is
     proportional to the number of *audiences* it reaches, so a wide flat sum of `+ AUDIENCE(...)` leaves
     costs a fetch per leaf per check.** What stands there is the **standing report of the widest and
     deepest audiences and their cost per check** (§8, *The cost of composition*) — no CI job, no refused
     save, nothing that fails if the report is not read, which is
     [D-081](../decisions/round-06.md#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now)'s
     case: a rule's name outliving its mechanism.
     [F-21](../open-questions.md#f-21)
     is the open question about who reads it. Half 3 is therefore the whole structural story: acyclicity
     at save, and nothing else.
  3. **No sharing table may exist, and the read path must grow neither a depth cap nor a cycle
     check.** The tree's one-parent rule is worth nothing if a side table lets two expressions share a
     node — editing the shared node would silently widen every grant using it, which is D-091's inclusion
     hazard re-imported. `AUDIENCE` is not that table and must not become it: it points at an audience's
     whole expression, never at an interior node. A forest met at read time is survivable-looking, so
     whoever meets one reaches for a hop counter, and **the cap becomes the thing that decides who a
     grant reaches** — which is why the read path depends on the write guard rather than backing it up.
     **With no bound anywhere, a hop counter looks like the obvious way to make a check cheap**
     ([D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)),
     and this refusal is the only structural one left, so the temptation is the design's real exposure.
     **A build that passes half 1 and fails this one is a build where the write guard has been removed
     and papered over** — the shape nesting makes easy to reach, because a read path that can follow an
     audience is a read path that wants a counter.
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
  **A guard that lives in code is deleted by a refactor and the data looks fine afterwards**, and nothing
  greps for it at build time (D-072).
- **16. TIME-BOMB: no permission path may materialize a set.** The requirement is that
  **`operand_holds` decides membership for one person and never loads a set of ids to test containment
  in.** An operand is a **named** set — a row of `selector_type`, which is the only test the language
  has. One thing wants it as an expanded set: **the editor's preview**, which shows the set to a human
  and is not a permission path
  ([D-114](../decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation)).
  In the resolver an operand is a **predicate**, and D-101 writes the distinction down precisely because
  an implementation is one lazy join away from getting it the other way and paying three thousand rows
  per check. **Materializability is not the test for what an operand may be**
  ([D-107](../decisions/round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)):
  `OLDER(18)` is precisely as materializable, and precisely as unmaterialized, as `MEMBERS` — a birth
  date read at the checked date and a membership row read at the checked date are both answers computed
  per person, and neither is allowed to become a list of ids. This is a requirement about **how the code
  computes**, which no migration can state and no reviewer will notice missing until the first slow day.

  **Nesting is where this assertion earns its keep, so assert on a nested expression specifically.** A
  flat `ROLE(x)` is awkward to write as a set load and natural to write as a predicate; an inner
  `AUDIENCE(veterans)` inside an outer expression reads like a job for *"fetch the inner set once and
  reuse it"*, which is the tempting optimization, is correct as an answer, and is the thing that makes a
  check slow at exactly the depth the expression happens to have — **and there is no depth above it: an
  expression is as deep as somebody typed**
  ([D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)).
  **A test exercising only single-level
  expressions passes on an implementation that materializes at every nesting level.** Assert that the
  recursion takes a person and returns a boolean, and that no path between two audiences hands over a
  collection.
- **17. TIME-BOMB: `.admin` prefix matching, and any ordering comparison, must stay deleted.** Two
  parts, both prose: there is no SQL left in which a build could grep for either (D-072).
  **First, no step of the resolver may build a permission code by concatenating a
  resource with `.admin`,** and no permission may have `admin` as its *action* except **exactly one**:
  `system.admin`. The allow-list is that single code and the check is an equality, not a set membership
  ([D-074](../decisions/round-06.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular)),
  **because an allow-list is where a wildcard comes back to life.** Zero rows expected.
  **Second: no comparison of
  `access_level` ranks, no `required_level` lookup, and no "at least `contribute`" anywhere.** There are
  no levels to compare (D-099), so the bug
  [D-012](../decisions/round-01a.md#d-012--status-strings-compare-by-rank-never-lexicographically)
  existed to catch — `'admin' < 'contribute'` read alphabetically — cannot occur, which is a better fix
  than the guard. **The one ordering this model still performs is
  `right_kind` containment in the guardianship channel**, so a build where a second ordering has
  appeared has not reintroduced a bug; it has started reintroducing the ladder.
- **18. TIME-BOMB: `deprecated` and `hidden` must never change an answer, and `disabled` must change one and
  say whose.** Three states stand where deletion stood
  ([D-109](../decisions/round-13.md#d-109--nothing-a-rule-names-is-deleted-deprecated-hidden-disabled--and-a-tab-instead-of-a-report)),
  and they are only safe if two of them are inert. **Assert both halves, because each fails alone.**
  *Inertness:* resolve every live expression, then flip a `selector_type`, `role`, `person_group` or
  `audience` row to `deprecated` and then to `hidden`, and **the resolved sets must be identical** — a rule
  that quietly stops granting because somebody tidied a list is the precise failure this design exists to
  make impossible, and an implementation gets it wrong by having the editor filter non-active rows out of
  a list it also uses to evaluate. *Effect:* flipping the same row to `disabled` must empty exactly the
  leaves that name it, in every expression, and the write must record the rules it touched, resolved
  before and after. *Third assertion:* **the flag is read live by the resolver, never compiled into a
  predicate** — flipping a row to `disabled` changes the next check, not the next rebuild
  ([D-114](../decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation)).
  A `deprecated` row that stops granting is therefore a bug in one function, and a `disabled` row that
  does not is visible in the same place. **Nothing else in §11 can see this one**, because the flag is a
  legitimate value in a legitimate column and every row is well-formed on its own.
- **19. TIME-BOMB: no row, table or field anywhere may map a caller — or a caller and a code, or a caller
  and an item — to a permission answer.** **A caller is a person or a registered key, and the widening is
  deliberate rather than a tidy-up**: as written over persons only, a table keyed by `api_key_id` and
  `permission_code` holding a boolean would not have been forbidden by this invariant
  ([D-123](../decisions/round-16.md#d-123--invariant-19-reads-a-caller-not-a-person)), and *"the
  integration's permissions"* is the most natural table in this system to write — it reads like
  configuration, not like a cache. This is the reason a permission cache cannot come back later as
  an optimization ([D-114](../decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation)).
  Assert it the way a schema review asserts things: **no column pairing a caller with a boolean that could
  only have come from a check, no table whose key contains `person_id` or `api_key_id` together with
  `permission_code` or a `selector_kind` / `selector_arg_id` or an item, and no `computed_at` sitting beside
  an answer.** **`api_key.last_used_at` is named here and cleared, but it is not a fourth shape:** a
  timestamp of when something happened answers no permission question and nothing reads it to decide one,
  while `api_key.last_checked_permission` would be exactly the row this check exists to catch, and is the
  name a review should search for. Three
  shapes survive the sweep and each is legal for a reason worth repeating: **`ruleset_version`**, an integer
  about a *ruleset* that names no person and keys a compilation; **D-110's record of whom a grant reached**,
  deliberately stale because it is a historical record — a rule naming a person who has since left must
  still read as it read then, and nothing reads it to decide whether to allow something now; and **the audit
  payloads**, which record that a check happened and expire on their own schedule
  ([D-088](../decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)).
  **The first is a value in a column; the second and third are records of an event. There is no fourth, and
  what the check looks for is a row that is a *current* answer.** **This is enforced structurally, which is
  both its strength and its limit:** the schema has nowhere to put an answer, so an implementation cannot
  persist one by forgetting not to — it would have to add a table, which is an act. In
  [D-081](../decisions/round-06.md#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now)'s
  vocabulary the residue is a named convention, not a guard: **nothing stops a team from adding a
  `permission_cache` table again in a year, under load, at 2 a.m., because it is the obvious move and this
  invariant is a paragraph.** **Read D-114 before writing that migration.**

- **20. A refused code granted to a key.** A live grant naming `api_key_id` whose permission is
  `system.admin` or one of the four `api_key.*` codes
  ([D-122](../decisions/round-16.md#d-122--what-a-key-owes-the-catalog-four-codes-at-the-unit-and-the-fourth-owed-thing-declined)).
  **This check is the entire net**, and saying so is the point: the refused set is an equality against five
  named codes, `permission` and `access_grant` share no column, and so no database rule can span them —
  unlike check 3, which reads one column of the permission row and can therefore always see the shape it
  counts. A row here means the save path was skipped, not that a constraint was disabled. **The refused set
  is written out code by code and never derived**, for the reason check 17 states for `.admin`: an
  allow-list is where a wildcard comes back to life.
- **21. A grant naming a key that cannot be used.** A live, unrevoked grant naming an `api_key` row that is
  revoked or past its `valid_to`. The grant is inert — an expired secret cannot authenticate, so nothing is
  being reached — and that is precisely why the check exists: **dead weight of this kind reads as an active
  integration to the next person reviewing who can do what**, which is the same failure check 5 reports for
  a deny that denies nothing and check 13 for a code nothing grants. Closing the grant is a person's act
  with a reason, and §14's revocation triple is where the reason is written.
- **22. TIME-BOMB: nothing may read a key's own columns to decide an answer.** An assertion, not a report:
  no code path reaches for `last_used_at`, `owner_person_id` or `created_by` when it resolves a permission,
  and no check consults the person who installed an integration at all
  ([D-120](../decisions/round-16.md#d-120--a-key-outlives-whoever-created-it-and-the-report-is-the-control),
  [D-123](../decisions/round-16.md#d-123--invariant-19-reads-a-caller-not-a-person)). **The reason this needs
  its own numbered assertion is that every one of those columns is right there on the row the check has
  already loaded**, which makes creator-derived authority the cheapest wrong turn available: a suspended
  account, a lapsed membership or a `deny` written against whoever installed a key would otherwise change
  what the key may do, and D-005's *"a permission is never derived from an identity"* forbids exactly that —
  including when the identity belongs to somebody else. 15 and 16 are CI assertions too, and this belongs
  beside them for the same reason: **a prohibition nobody runs is a convention, not a guard.**

**Checks 3, 4, 5, 6 and 9 are the ones to wire to alerts, plus one half of 7.**

- **3 and 4 are the reports that stand in for the database rules that do not exist.** A row in either
  is not data drift — it is a save-path check that stopped running.
- **5 and 6 are the reports for the two restrictions that have no mechanism enforcing them**: a deny
  that denies nothing, and an office granted without the membership operand. Both are lists a human
  reads, and both are the entire remaining control on their failure.
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
  which is why neither can be a migration. With nesting, 15 guards a graph rather than a row, and it
  guards **two** things: **cycles, and not emptying something that is named.** **The acyclicity walk is
  therefore the only structural guard on this module**, and check
  15's half 3 is the assertion that nobody quietly adds a second one inside the read path.
- **Where these go.** **The permissions page has a tab**
  ([D-109](../decisions/round-13.md#d-109--nothing-a-rule-names-is-deleted-deprecated-hidden-disabled--and-a-tab-instead-of-a-report)).
  **`Broken`** holds the rules that name something deprecated, hidden or disabled or that resolve to nobody
  — checks **1, 2, 3, 7's empty half, 12, 13, 14 and 18's second half** all land there — and **`Unusual`**
  holds rules that resolve correctly and look odd, which is where **6** lives. **`Unusual` also gains a line
  of keys** — each live `api_key` with what it is granted, when it was last used, and whether the person in
  its `owner_person_id` still has an account — because a permanent outside authority is exactly the kind of
  correctly-configured oddity a tab is for
  ([D-120](../decisions/round-16.md#d-120--a-key-outlives-whoever-created-it-and-the-report-is-the-control)).
  **There is no age threshold on that line**: a bound somebody might want to change belongs in a column, and
  inventing one is not this page's call. **Check 7's wide
  half and check 9 go to a person rather than to a screen**, because both describe authority getting bigger
  while nobody edited a grant, and a tab nobody opened is not an alert. **Checks 20 and 21 land in `Broken`
  beside 3, 4 and 13** — one is a save-path refusal that got through, the other is authority that reads as
  live and is not. **Checks 19 and 22 go to neither tab**: they are facts about the schema and about the
  resolver, not about a rule, and the place either can be enforced is a migration review or a CI assertion. The
  tab is not a guard in
  [D-081](../decisions/round-06.md#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now)'s
  sense — nothing is blocked — but **it is where the person writing the rule already is**, which a report on
  a schedule never was.

---

## 12. What the organization starts with

Starting catalog. Expect to edit this heavily; it is a proposal, not a specification.

> **This section and [../appendix/permission-catalog.md](../appendix/permission-catalog.md) are
> the same list written twice, and they drift.** A reconciliation found documented permissions with no
> seed row, among them a code several of the catalog's own seed roles assign and one of the two codes
> D-068 exists to protect; the `event.*` codes are the standing example of the two lists disagreeing.
> **With no wildcard, a code the catalog advertises and the database does not name is a capability nobody
> can be granted**, and the permission editor is the only place the gap shows. Nothing in the schema pairs
> codes with roles, so there is no per-role list to compare a catalog row against either: a documented code
> that nothing grants is invisible to anything but a report. **Integrity check 13** reads the grants for exactly that
> reason (D-068).
>
> **There is no SQL check for this** — one side is a Markdown file. The discipline is the
> check: when adding a permission, add it in **both** places in the same edit, and treat a catalog
> row that no grant names as a bug of the same class as a missing migration. The reconciliation is
> mechanical enough to script: a diff of the codes the catalog lists against the codes that exist.
> Anything in the catalog and not in the database is a permission that cannot be granted; anything in
> the database and not in the catalog is an undocumented capability. **Both directions of the gap can be
> present at the same time.**

**Not in the catalog, named rather than quietly dropped, each with what to use instead:** the
`dependent.*` codes — a guardian's authority is a `right_level` on the relationship, not a bundle of
permissions (D-074); `scope.expose` and `scope.exposure.review` — the table they guarded is not in this
schema (D-097); `system.gate_exempt` — there is no gate to waive, membership is an operand (D-100); every
`position.*` code and the appointment workflows behind them (D-100); and the codes about *bodies* rather
than people — a unit's renaming, restructuring and closing, and participation in a sub-unit — since there
is one unit and it is a scope (D-097). `role.assign`, `role.unassign`, `role.create`, `role.view`,
`role.edit` and `role.delete` are in the catalog and are **aimed at `role_holder`**; `role.edit` reaches
nobody's authority, only its name and description (§3).

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

**No seeded office holds any of the four `api_key.*` codes, and none should.** Whoever holds
`system.admin` already satisfies those checks because `system.admin` satisfies every code
([D-124](../decisions/round-16.md#d-124--two-defects-systemadmin-satisfies-every-code-and-one-prose-code-named-no-row)),
so seeding one would move the capability to install a permanent outside authority into a row nobody chose,
on an office whose purpose is something else
([D-122](../decisions/round-16.md#d-122--what-a-key-owes-the-catalog-four-codes-at-the-unit-and-the-fourth-owed-thing-declined)).
**It arrives by an ordinary grant or it does not arrive.**

**Everything else is starter material the organization edits** — including the `system_admin` office
the catalog sketches, whose reason for existing is that someone has to hold `system.admin` before
anything can be granted. **What §12 must fix, and does, is the *shape* rather than the list**: a
`system.` permission is seeded `applies_to = unit`, so it can never arrive through an item grant. That
is not a configuration choice — it is the structural guarantee that a shared item cannot hand someone
authority over the permission system, and it is carried by a column value rather than by a resolver
branch (§2).

**What the organization starts with, in one list.** The platform ships:

- **The permission vocabulary** — each code marked `is_system` so it cannot be deleted or renamed —
  spanning people, accounts, membership, groups, audiences, roles, guardianship, item grants, audit,
  legacy import, reporting, the thirteen `event.*` codes, messaging, and the four `api_key.*` codes of [05e §15](05e-keys-and-callers.md) —
  `api_key.view`, `api_key.create`, `api_key.rotate`, `api_key.end`, every one `applies_to = unit`. **The one complete list is
  [../appendix/permission-catalog.md](../appendix/permission-catalog.md)**; this document keeps no second
  copy of it, because two copies drift for exactly the reason above.
- **`grant_scope_type`**: `unit` (the only row that is not item-scoped), `event`, `person_group`,
  `role`, and `document` (deferred).
- **`selector_type`**: **thirteen rows — the thirteen operands of §8's language — every one of them
  seeded, `is_system` and implemented in the shipped evaluator**, because there is no fourth combination
  and no third kind (§8, *The selector registry*, whose table **is** the language: the count is only the
  cheap form of the check that no operand exists anywhere else). **This registry is what both the grant
  editor's dropdown and the parser's reserved words read**, which is what D-101 means by *the language
  becomes data* — a new operand is a decision entry, a seed row **and a resolver arm in one release**,
  never a row typed into a screen and never a row shipped ahead of the code that evaluates it. `AUDIENCE`
  is the newest operand anyone designed
  ([D-103](../decisions/round-10b.md#d-103--an-audience-may-name-another-audience)). `OLDER` and `YOUNGER`
  are the only rows whose argument is not an entity reference: it is an integer, and their arms ship in the
  same release as their rows on the rule above, which is why the merge and orphan scans of §11 walk five
  argument kinds and not six (§8, *A hand-named person is now a keyless reference*,
  [D-107](../decisions/round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded)).
  **Refused, and therefore absent** (§8): `GRANTS`, and `LIST` — a hand-written set of people is a sum of
  `PERSON(x)` leaves, not an operand
  ([D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)).
- **Two audiences, both `is_system`, and both must have a `code`**: `everyone`, whose expression is
  `EVERYONE`, and `all_members`, whose expression is `MEMBERS`. **The code is not cosmetic**: it is the
  only way another audience can name them
  ([D-103](../decisions/round-10b.md#d-103--an-audience-may-name-another-audience)), so a seeded row
  without one is a piece of the resolver's vocabulary that nothing can compose with, and §11's check 12 is
  the net for the leaf side of that. **Whether `code` should simply be *required* on an `is_system`
  audience rather than merely seeded is a question this document does not settle** (§13). **No seeded
  audience is parameterized**: there is one unit, so nothing needs a row per unit. **Three names keep being
  asked for, and each of them is something smaller or nothing at all** —
  `unit_participants` is `MEMBERS`; `unit_leaders` is `ROLE(x)`, the shape §8's evaluation rules are written
  against — **an expression that resolves to nobody is silent, while every grant aimed at it looks
  granted**; and
  `guardians_of` is **nothing** — a guardian's authority is the guardianship channel's `right_level` over
  the child, not a set an audience can name, which is why `GUARDIANS` is not a selector
  ([D-113](../decisions/round-13.md#d-113--the-guardianship-channel-has-no-expression-guardians-is-not-a-selector)).
  **A bound `GUARDIANS` on a grant about that person is unsavable on every scope that exists**: `person` is
  not a `grant_scope_type`, so the binding check refuses it. **`audience_member` is not a table** (§8), so there is no member row on an `is_system`
  audience for anything to refuse; what stands is the category that refusal protected — **seeded audiences
  are the resolver's own vocabulary, not a set somebody curates, and the editor should not offer to edit
  `everyone`'s expression.**
- **The `counselors` role**, above.
- **One seeded grant: `event.answer.view` on an event, aimed at
  an audience whose expression is `ORGANIZERS`** — the code in the catalog's singular spelling, which is
  the registered one
  ([D-102](../decisions/round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it),
  amending [D-061](../decisions/round-05.md#d-061--event-answers-are-read-by-that-events-organizers)).
  "Answers are read by that event's organizers" is a row a reader can find, narrow or delete rather than a
  sentence the resolver implements, and it is the worked example of a **bound operand**:
  item-scoped, argument-less, meaning *the organizers of whichever event this grant is on* — which is
  why it is one grant in the seed rather than one per event. **[D-062](../decisions/round-05.md#d-062--organizers-are-appointed-on-the-event-not-granted)
  is not contradicted**: the appointment still grants nothing by itself, because an operand is a set
  and not a grant. **It is written without `MEMBERS`** and must not be "corrected" to include it: an
  organizer appointed for one weekend is not required to be a paying member, and D-062's appointment
  model assumes exactly that.
- **The effects and the enums.** `allow` and `deny` arrive with the schema, as do the two values of
  `applies_to` and the two of `right_kind`. None of them is editable at runtime: **a comparison the
  organization can edit is a security control with no owner**, and there is no level comparison to seed at
  all
  ([D-099](../decisions/round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality)).

A few of the surviving codes carry a decision in their shape, and those are worth naming:

- **`person.merge` and `person.redact` are separate codes**, not flavours of `person.edit`. **They are
  separate for reach, not for irreversibility.**
  `person.redact` is irreversible — that is what an erasure is. `person.merge` is **not**: reversing a
  merge is a supported operation
  ([D-087](../decisions/round-07-08.md#d-087--merge-chains-stay-because-reversing-a-merge-is-a-supported-operation)),
  with the undo written as its own audit entry. What both codes share is that they act on **every row of a
  person's life** rather than on one field, which is why they are their own codes — and with no
  `person.admin` to imply them (D-068), a role that reaches them does so by listing them, visibly.
- **`person.view` reaches the whole record.** There is
  no privileged corner of the record for it to stop outside: whoever holds it over a person
  reads their descriptive values — the allergy list, the insurance number, the note about who the child
  actually lives with — on the same grant that reads their name
  ([09-attributes.md §4](09-attributes.md#4-who-may-read-and-who-may-write),
  [D-083](../decisions/round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data)).
  **A grant of it at the unit reaches every member in the organization**, because that is what "at the
  unit" means: **nothing in the model reproduces "access was granted by the body that knows these
  children"** — the loss is recorded in §5 and in D-097. It is therefore the widest read
  permission in the system, and **the catalog's sensitivity mark is where that has to be visible**
  ([D-086](../decisions/round-07-08.md#d-086--a-sensitivity-mark-grades-what-a-grant-exposes-not-the-table-it-reads)):
  the honest mark is the top tier, worded around *whose* data a grant exposes rather than around a
  category of fields, because there are no field categories (D-083).
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
- **`person_group.member.manage` is how "joining a group is somebody else's act" is said**
  ([D-098](../decisions/round-10a.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority),
  carrying
  [D-095](../decisions/round-09.md#d-095--units-carry-no-restrictions-joining-one-is-somebody-elses-act)):
  held at the unit, where it reaches every group, or granted on one group as an
  item. **There is no self-scoped variant and none will be added** — nobody writes themselves onto a
  roster. Its counterpart for offices is `role.assign` 🔒🔒, and the gap between the two marks is the
  whole content of D-100's "why two tables".
- **`role.unassign` is one of the only two things that end authority** (the other is a holder row's
  `valid_to`), because a role has no period (D-053) and nothing forces a holder row to end (D-071).
- **`membership.terminate` expels**, and is restricted as such; `membership.lapse` is an
  administrative end for non-payment. **Neither changes what a role grants** — there is no membership gate
  for them to act through. A lapse changes what `MEMBERS` means, which is a different thing, in a
  different place.
- **`event.presence.mark` stays a separate code from `event.manage_participants` on purpose**, and
  **`event.register_self` *is* the eligibility rule**
  ([D-060](../decisions/round-05.md#d-060--eligibility-is-capability-there-is-no-separate-rule-engine))
  rather than an expression of one. The difference the two codes mark is **a volunteer leader is handed the
  register without being handed the roster**, and that difference is two grant rows.
- **There is no wildcard at all, and nothing implies anything.** A guardian's authority is
  `right_level = write` on the relationship, not a permission (D-074); the code families `dependent.*` and
  `*.admin` are not in this catalog. So an office that should hold a new permission must be **told** —
  check 13 is the net.
- **Reporting is seeded coarse, and left open on purpose.** Only `report.view` and `report.export` are
  starters. Whether reporting is per-report or one permission with row-level filtering is still open
  (catalog §12). Do not ship both shapes; pick one when reporting is designed.

> **`system.admin` is deliberately a single top-level permission**, not a
> per-resource one. Holding it satisfies everything, and check 9 in §11 alerts on its
> holders. Keeping the most dangerous capability concentrated and alarmed is safer than
> spreading equivalents of it across every resource. **`system.admin` is a permission code, not a level** —
> there are no levels (D-099) — and it is the only permission whose *action* is `admin` (§11's check 17 is
> the assertion that it stays the only one).

---

## 13. Open issues

- **Three questions about callers that are not people, registered rather than guessed at.** Round 16
  designed the arriving integration and deliberately stopped there: this system's **own** writers are still
  a NULL plus an `actor_label` ([F-25](../open-questions.md#f-25)), the case where nobody who could hold
  `system.admin` can reach a screen has no mechanism ([F-26](../open-questions.md#f-26)), and calls going
  *out* have no design at all ([F-27](../open-questions.md#f-27)).
  [05e §17](05e-keys-and-callers.md) states each from this module's side; none of the three is answered by
  adding a column to `api_key`, and a key is a poor fit for the first of them — **a sweep is not a caller
  and should not have to authenticate.**
- The complete permission catalog and real role definitions (§12) — needs your input. The question is
  **which starter grants are written with `MEMBERS` in the expression and which are not**: `role` has no
  `requires_membership` switch to carry the answer
  ([D-100](../decisions/round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape)),
  so it is answered per grant rather than per role, with check 6 (§11) as the net and the seeded grants as
  the default.
- **Whether the API should refuse a check that names an item for a unit-only code (§2).**
  `applies_to` is deliberately a save-time rule, and D-099 says so in as many words, so the mismatched
  *grant* cannot exist — but a *caller* that asks `can(person, 'event.create', 'event', 1204, …)`
  gets the unit's answer rather than an error. **Assumption, not a ruling:** the honest answer is a
  refusal at the API layer naming the code and the scope, because a caller that asks that question has
  a bug worth surfacing. Nothing in D-097..D-103 settles it. **Round 16 gave that word a second sense
  and changed this answer not at all:** a call made with a key asks `can_key(api_key, 'event.create',
  'event', 1204, …)` and is refused the same way, by the same layer, for the same reason
  ([05e §16](05e-keys-and-callers.md#16-how-a-call-made-with-a-key-is-checked),
  [D-116](../decisions/round-16.md#d-116--a-caller-that-is-not-a-person-is-a-registered-key-and-a-key-is-a-third-grantee-kind)).
- **`selector_depth_limit` (§8): moot — there is no such parameter to give a default**
  ([D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)).
  What the question was reaching for is live: **a bound on *height* does not bound what an expression
  actually costs**, which is how many *audiences* it reaches — a depth limit of 3 still permits a wide flat
  sum of twenty `AUDIENCE()` leaves and prices each one at a fetch. **Neither shape is bounded.**
  [F-21](../open-questions.md#f-21)
  is closed on exactly that point — *nothing bounds what an expression costs, and at the stated size that
  is accepted rather than merely unaddressed* — so what remains open is *what would make somebody wish
  there were a limit*.
  [D-112](../decisions/round-13.md#d-112--the-systems-scale-is-stated-hundreds-of-people-tens-of-registrants-per-event)
  answers it with a stated size and a trigger (a few thousand people, or a thousand registrants on one
  event) at which the unbounded cost stops being affordable, rather than with a parameter. Inventing a
  default number nobody asked for is not this page's call; naming the size at which the answer would change
  is. The standing report of §8 and §11's half 2 is what a real number would eventually be argued from.
- **Nothing computes an expression's *fingerprint* (§8): refused, not deferred**
  ([F-14](../open-questions.md#f-14),
  [D-110](../decisions/round-13.md#d-110--the-expression-is-the-record-of-whom-a-grant-reached)).
  Two expressions with the same meaning are two different row sets, and *"you already granted exactly this
  set on that item"* does not fall out of storage — **that is accepted, not mitigated.** A watered-down
  version (a derived fingerprint, a warning, never a refusal) is refused with it, because computing one
  means deciding that two expressions mean the same thing, and this module computes *who is in a set*,
  never *what a string means*. **A fingerprint is a semantic-equality function wearing a warning badge:**
  either it is exact, which is undecidable without evaluating both sides, or it is a hash of a normalized
  string, which two spellings of one set will fail to match — a warning wrong in both directions.
- **The per-item reach preview (§8) is a screen nobody has designed.** `PLACED` means different people
  on different events, so the editor's expanded set must be computed *for an item* and say so on
  screen
  ([D-102](../decisions/round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it)).
  The expanded set is a requirement (D-091), and for a bound operand it depends on an input the grant does
  not contain. Which item the editor picks by default — the grant's item, an event the writer chooses, the
  next event with registrants — is not decided anywhere.
- **`WHITELISTED` (§8) is not seeded, and no selector will be: there is no stored state to evaluate**
  ([F-20](../open-questions.md#f-20)).
  The candidate readings — `source = staff`, promotion off the waitlist, a new column on
  `event_registration` — are not narrowed, and that is the answer rather than an evasion: **an operand with
  no state to read resolves to nothing**, and picking a meaning in order to seed a row would invent an
  events feature from the authorization module. **The need for "these few people" arrives anyway** and is
  served today: write grants, or a `GROUP(x)`, or `PERSON(a) + PERSON(b)`. The discipline stays — a row is
  not seeded so that a question cannot become a word in a grammar by being typed often enough.
- **`PERSON(x)` is a seeded row (`argument_type = person`); the class of bug behind it is the open item.**
  §12 states the one count that matters — how many rows `selector_type` holds — cheap to check, and checked
  here because a registry that prose contradicts is a fiction
  ([D-104](../decisions/round-10b.md#d-104--a-permission-codes-last-segment-is-an-action-and-a-registry-that-prose-contradicts-is-a-fiction)).
  **What is open is the class, not this operand:** nothing in this module, or in this repository,
  compares the dotted tokens these documents write against the seeded registries they describe, so the same
  drift will happen again in whichever table is written next. D-104 adopts a hand-run report over the
  documents as the answer, and states plainly that **a report nobody runs is a convention** — there is no CI
  here to make it a guard, and no layer of this spec can tell a writer that `PERSON(` had no row behind it.
- **The `LIST` gloss, and the proposed rename of that operand to `ADDED` (§8): moot — there is no such
  operand** ([D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)).
  Neither the gloss nor the rename has a subject: `LIST` is not an operand of this grammar, so there is
  nothing to rename and nothing to explain.
- **Whether two people editing one audience is handled by a lock, a queue, or nothing (§8).** Editing an
  audience is one expression edit, so two clerks editing one audience **can** collide, **and a silent lost
  update removes somebody's access without any row recording that it happened.**
  [D-105](../decisions/round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other)
  states the obligation — an optimistic-concurrency check or a queue — and puts it on the editor rather
  than on the schema; there is no membership table left to hold such a rule.
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
  standing at, and it is **load-bearing for a policy and not only for a screen**: dropping exactly the
  compilations that embed a changed expression
  ([D-114](../decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation))
  needs this listing run in its **reverse** direction, transitively rather than one hop at a time (§10).
  If the import corpus's row-count estimates are wrong there is no blunt instrument to fall back on — there
  is nothing to invalidate for everyone at once — so what stands here is D-112's trigger and this bullet.
- **Whether `audience.code` should be required rather than optional on `is_system` rows (§8, §12).**
  The seeded audiences are the resolver's vocabulary and cannot be composed with by anything that lacks
  a code, which makes the code mandatory in every practical sense while leaving it nullable in the
  schema. **A check is being asked to assert what a column could have guaranteed**; making the column
  required-where-`is_system` would be the honest fix and is not this document's call to make.
- **A nested audience's past reach is not reconstructable, and that is the answer (§8, *Three named
  sets*):** the record of whom a grant reached **is the expression**
  ([D-110](../decisions/round-13.md#d-110--the-expression-is-the-record-of-whom-a-grant-reached),
  closing [F-17](../open-questions.md#f-17)).
  `GROUP(x)` answers *"was she in it on 1 June 2024?"* from its dated rows and `AUDIENCE(x)` does not, and
  **that is not a gap, because the system never promised the answer** — what it keeps is the words, and
  D-109's rule that nothing a rule names is deleted is what keeps them evaluable. **What is logged as
  history is a rendering on a date, not a roster**; a roster would store, against
  [D-088](../decisions/round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short)'s
  window, a per-person record of people who were never granted anything.
- **Whether `membership` belongs in `grant_scope_type` (§6).** It is not seeded, and that is an
  inference from what D-097 and D-099 list rather than a ruling.
- Whether `valid_to` should be mandatory for high-authority holder rows and long-lived item grants
  (§4, §6).
- Polymorphic `scope_id` vs a `grantable_item` supertable (§6) — a real fork, covering
  `selector_arg_id` too.
- **How long a `permission_cache` entry may live (§10): there is no such table, so there is no lifetime**
  ([D-114](../decisions/round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation)).
  **No TTL is being asked about, because there is no row to put one on:** `expires_at` is not a column of
  §10 and `ruleset_version` is, as a compilation key bumped by writes to `audience_operand` and
  `selector_type`
  ([F-6](../open-questions.md#f-6),
  [D-111](../decisions/round-13.md#d-111--the-permission-cache-is-rebuilt-nightly-on-any-ruleset-change-and-on-request)).
  **Nothing is open here.** The affordability question F-6 ended on is answered by
  [D-112](../decisions/round-13.md#d-112--the-systems-scale-is-stated-hundreds-of-people-tens-of-registrants-per-event)'s
  stated size and trigger, and there is no rebuild job to afford.
- **Cache vs a materialized effective-permission table (§8, §10): dissolved, not decided** —
  [F-7](../open-questions.md#f-7).
  A rebuild of cached answers and a materialized `effective_permission` table are **the same job with two
  names**, which is why the pair is recorded as dissolved rather than answered — and **a dissolved question
  is the kind that comes back if nobody writes down that it dissolved**, with "history, not performance"
  exactly where it would come back from. What is left of the pair is the history side alone: there is no
  rebuild to confuse with a history table, a table of today's answers is not a record of 2011, and
  **invariant 19 is the thing a return has to argue with.**
- Retention policy for `access_log` — legal input required
  ([F-8](../open-questions.md#f-8--retention-policy-for-access_log)).
- Whether `access_log` needs human annotation (recommend a separate table if so).

**Settled, stated as answers.** A role may **not** be held by a rule
([F-12](../open-questions.md#f-12), D-100). An
audience composes other sets through an expression whose leaves name other sets, and `AUDIENCE()` is the
form that settled it (D-101, D-103); there is no inclusion edge table in this model — the edges are leaves
(D-091). A saved rule is reusable by name **only if it has a `code`** (D-103). Permissions do not depend on
membership status through any switch: **membership is an operand**, and the posture is opt-in per grant
(D-100).

All tracked in [../open-questions.md](../open-questions.md).

*Decisions behind this page: D-005, D-011, D-012, D-053, D-060, D-061, D-062, D-068, D-071, D-072,
D-074, D-081, D-083, D-085, D-086, D-087, D-088, D-090, D-091, D-095, D-097, D-098, D-099, D-100, D-101,
D-102, D-103, D-104, D-105, D-106, D-107, D-109, D-110, D-111, D-112, D-113, D-114.*
