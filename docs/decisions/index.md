# Decision Log

Decisions taken, with the reasoning that produced them. Recorded so they are not
re-litigated from scratch — and so that when a decision is reversed, the reason for the
original choice is visible.

**How this log is filed.** The entries live in the round that took them; this page indexes all
149 of them and lists the reversals. Read the round you are curious about — each one says what was
asked and what the answers did to the design — or follow a `D-` number from any page straight to its
entry. Nothing is summarised here that is not stated in full there.

**Status values:** `decided` — settled, the data model reflects it *(since D-072: the documents, not a schema file)*. `proposed` — recommended,
awaiting your confirmation. `assumption` — taken by default, stated in italics in the
docs, easily reversed. `reversed` — no longer in force; the entry is kept, marked, and the
replacement is linked. Reversals are also listed together in
[Reversed decisions](#reversed-decisions) below, where they were first collected; the collection has
not been reordered, because a section with a stable anchor is worth more than a section in a tidier
place.

**Five SQL fences survive in this archive, and only in these entries.** [D-072](round-06.md#d-072--the-documentation-carries-no-sql-the-schema-is-the-orms-job) moved the schema out of the
documentation, but it did not rewrite the entries that had been written *in* the schema — at
[D-035](round-02-03.md#d-035--one-root-unit-all-sub-units-nest-arbitrarily-beneath-it),
[D-041](round-02-03.md#d-041--belonging-to-a-sub-unit-is-a-participation-record-not-a-membership),
[D-060](round-05.md#d-060--eligibility-is-capability-there-is-no-separate-rule-engine),
[D-066](round-05.md#d-066--payment-confirms-the-place-and-the-release-deadline-is-the-one-automatic-transition)
and [D-068](round-05.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle). Each is a
**quotation of the shape a decision was made in**, and each says below it where the requirement
actually lives now. No later entry adds a fence: the rule for writing this log from here is
[D-081](round-06.md#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now)
— state the requirement, name the layer that owes it, and let an identifier be a name rather than
an actor.

---


## Index

One line per decision, in the order the decisions were taken. The link goes to the entry,
which carries the reasoning; the round is the page that entry sits on.

| # | Decides | Status | Round |
|---|---|---|---|
| [D-001](round-01a.md#d-001--person-account-and-membership-are-three-separate-things) | Person, account, and membership are three separate things | decided (from your requirements) | founding |
| [D-002](round-01a.md#d-002--everything-temporal-is-a-period-never-a-boolean) | Everything temporal is a period, never a boolean | decided | founding |
| [D-003](round-01a.md#d-003--never-hard-delete-merges-leave-tombstones) | Never hard-delete; merges leave tombstones | decided | founding |
| [D-004](round-01a.md#d-004--no-automatic-merging-ever) | No automatic merging, ever | assumption ⚠ *confirm or overrule* | founding |
| [D-005](round-01a.md#d-005--permissions-are-grants-never-derived-from-identity) | Permissions are grants, never derived from identity | decided (from your answer) | founding |
| [D-006](round-01a.md#d-006--per-item-permissions-are-capabilities-on-the-item) | Per-item permissions are capabilities on the item | decided (from your answer) | founding |
| [D-007](round-01a.md#d-007--every-resource-has-an-admin-level-that-subsumes-narrower-ones--reversed) | Every resource has an admin level that subsumes narrower ones | ~~decided~~ **reversed by [D-068](round-05.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle)** ⚠ | founding |
| [D-008](round-01a.md#d-008--organizations-units-are-one-self-referencing-table-with-configurable-types) | Organizations units are one self-referencing table with configurable types | decided (from your answer) | founding |
| [D-009](round-01a.md#d-009--unit-membership-links-to-person-not-to-membership) | Unit membership links to person, not to membership | decided | founding |
| [D-010](round-01a.md#d-010--role-assignments-and-access-grants-share-a-scope-model-and-a-resolver) | Role assignments and access grants share a scope model and a resolver | decided | founding |
| [D-011](round-01a.md#d-011--scope_id-on-access_grant-is-polymorphic-with-no-foreign-key) | scope_id on access_grant is polymorphic, with no foreign key | assumption ⚠ *a real fork — worth a deliberate decision* | founding |
| [D-012](round-01a.md#d-012--status-strings-compare-by-rank-never-lexicographically) | Status strings compare by rank, never lexicographically | decided | founding |
| [D-013](round-01a.md#d-013--explicit-deny-revoked-is-checked-before-everything) | Explicit deny (revoked) is checked before everything | decided | founding |
| [D-014](round-01a.md#d-014--roles-do-not-inherit-from-other-roles) | Roles do not inherit from other roles | decided | founding |
| [D-015](round-01a.md#d-015--authority-inherits-downward-through-the-unit-hierarchy--reversed) | Authority inherits downward through the unit hierarchy | **reversed by [D-031](round-02-03.md#d-031--no-downward-inheritance-of-authority-scope_exposure-is-the-only-crossing)** ⚠ | founding |
| [D-016](round-01b.md#d-016--renewal-opens-a-new-membership-row-not-an-extended-valid_to) | Renewal opens a new membership row, not an extended valid_to | decided | founding |
| [D-017](round-01b.md#d-017--requests-are-separate-from-memberships) | Requests are separate from memberships | decided | founding |
| [D-018](round-01b.md#d-018--membership_request-records-the-subject-and-the-submitter-separately) | membership_request records the subject and the submitter separately | decided (from your answer) | founding |
| [D-019](round-01b.md#d-019--household-membership-grants-no-access) | Household membership grants no access | ⚠ **PARTLY SUPERSEDED** — the `household` tables are gone | founding |
| [D-020](round-01b.md#d-020--guardian-permissions-are-scoped-to-the-guardianship-row) | Guardian permissions are scoped to the guardianship row | decided (from your answer) | founding |
| [D-021](round-01b.md#d-021--healthmedical-access-is-separate-from-consent-authority) | Health/medical access is separate from consent authority | decided | founding |
| [D-022](round-01b.md#d-022--lapsing-and-termination-are-different-permissions) | Lapsing and termination are different permissions | decided | founding |
| [D-023](round-01b.md#d-023--nothing-is-auto-lapsed-or-auto-terminated) | Nothing is auto-lapsed or auto-terminated | ⚠ **partly superseded** by [D-040](round-02-03.md#d-040--the-fee-expires-yearly-a-date-tracked-renewal-window-replaces-a-grace-status) | founding |
| [D-024](round-01b.md#d-024--guardianship-does-not-auto-expire-at-majority--reversed) | Guardianship does not auto-expire at majority | ~~assumption~~ **reversed by [D-069](round-05.md#d-069--guardianship-ends-when-a-person-ends-it-the-system-takes-no-position-on-majority)** ⚠ | founding |
| [D-025](round-01b.md#d-025--audit-log-redacts-sensitive-values-before-insert) | Audit log redacts sensitive values before insert | decided | founding |
| [D-026](round-01b.md#d-026--two-audit-trails) | Two audit trails | decided | founding |
| [D-027](round-01b.md#d-027--legacy-import-is-staged-reviewed-idempotent-and-per-batch-reversible) | Legacy import is staged, reviewed, idempotent, and per-batch reversible | decided (from your answer) | founding |
| [D-028](round-01b.md#d-028--imported-memberships-never-get-a-null-valid_to) | Imported memberships never get a NULL valid_to | decided | founding |
| [D-029](round-01b.md#d-029--finance-design-is-provisional-and-will-be-rewritten) | Finance design is provisional and will be rewritten | assumption / open | founding |
| [D-030](round-01b.md#d-030--finer-permissions-will-be-added-incrementally) | Finer permissions will be added incrementally | decided | founding |
| [D-031](round-02-03.md#d-031--no-downward-inheritance-of-authority-scope_exposure-is-the-only-crossing) | No downward inheritance of authority; scope_exposure is the only crossing | decided | rounds 2-3 |
| [D-032](round-02-03.md#d-032--deny-is-absolute-locality-orders-allows-only) | Deny is absolute; locality orders allows only | decided | rounds 2-3 |
| [D-033](round-02-03.md#d-033--multiple-people-may-occupy-the-same-position) | Multiple people may occupy the same position | decided | rounds 2-3 |
| [D-034](round-02-03.md#d-034--the-person-record-holds-no-deceased-flag) | The person record holds no deceased flag | decided | rounds 2-3 |
| [D-035](round-02-03.md#d-035--one-root-unit-all-sub-units-nest-arbitrarily-beneath-it) | One root unit; all sub-units nest arbitrarily beneath it | decided (from your answer) | rounds 2-3 |
| [D-036](round-02-03.md#d-036--units-cannot-be-reparented-a-unit-that-moves-is-a-new-unit) | Units cannot be reparented; a unit that moves is a new unit | decided (from your answer) | rounds 2-3 |
| [D-037](round-02-03.md#d-037--exactly-one-membership-type-the-fee-is-flat-and-per-person) | Exactly one membership type; the fee is flat and per person | decided (from your answer) | rounds 2-3 |
| [D-038](round-02-03.md#d-038--membership-is-ageless) | Membership is ageless | decided (from your answer) | rounds 2-3 |
| [D-039](round-02-03.md#d-039--member-permissions-require-a-current-paid-membership) | Member permissions require a current paid membership | decided (from your answer) | rounds 2-3 |
| [D-040](round-02-03.md#d-040--the-fee-expires-yearly-a-date-tracked-renewal-window-replaces-a-grace-status) | The fee expires yearly; a date-tracked renewal window replaces a grace status | decided (from your answer) | rounds 2-3 |
| [D-041](round-02-03.md#d-041--belonging-to-a-sub-unit-is-a-participation-record-not-a-membership) | Belonging to a sub-unit is a participation record, not a membership | decided (from your answer) | rounds 2-3 |
| [D-042](round-02-03.md#d-042--grants-may-target-audiences-not-only-individuals) | Grants may target audiences, not only individuals | decided (from your answer) | rounds 2-3 |
| [D-043](round-02-03.md#d-043--no-background-checks-are-recorded-in-this-system) | No background checks are recorded in this system | decided (from your answer) | rounds 2-3 |
| [D-044](round-02-03.md#d-044--nothing-gates-a-membership-request-except-identity-and-payment) | Nothing gates a membership request except identity and payment | decided (from your answer) | rounds 2-3 |
| [D-045](round-02-03.md#d-045--the-bulk-scope-exposure-tool-is-removed) | The bulk scope-exposure tool is removed | decided (from your answer) | rounds 2-3 |
| [D-046](round-02-03.md#d-046--guardianship-defaults-depend-on-how-the-guardianship-was-created) | Guardianship defaults depend on how the guardianship was created | decided (from your answer) | rounds 2-3 |
| [D-047](round-04.md#d-047--the-fee-expires-on-1-january) | The fee expires on 1 January | decided (from your answer) | round 4 |
| [D-048](round-04.md#d-048--the-renewal-window-is-60-days-and-is-a-configuration-parameter) | The renewal window is 60 days, and is a configuration parameter | decided (from your answer) | round 4 |
| [D-049](round-04.md#d-049--the-root-may-not-read-into-its-sub-units-scope_exposure-is-the-only-crossing) | The root may not read into its sub-units; scope_exposure is the only crossing | decided (from your answer) | round 4 |
| [D-050](round-04.md#d-050--a-renewal-inside-the-window-extends-the-existing-root-participation-row) | A renewal inside the window extends the existing root participation row | decided (from your answer) | round 4 |
| [D-051](round-04.md#d-051--the-membership-gate-is-waived-by-a-permission-not-only-by-a-role-flag) | The membership gate is waived by a permission, not only by a role flag | decided (from your answer) | round 4 |
| [D-052](round-04.md#d-052--roles-are-runtime-data-the-seed-set-is-not-a-specification) | Roles are runtime data; the seed set is not a specification | decided (from your answer) | round 4 |
| [D-053](round-04.md#d-053--a-role-is-valid-always-only-its-assignment-is-temporal) | A role is valid always; only its assignment is temporal | decided (from your answer) | round 4 |
| [D-054](round-04.md#d-054--the-sub-unit-vocabulary-is-not-seeded-the-organization-defines-its-own-types) | The sub-unit vocabulary is not seeded; the organization defines its own types | decided (from your answer) | round 4 |
| [D-055](round-04.md#d-055--the-permission-catalog-is-deliberately-comprehensive-and-granular) | The permission catalog is deliberately comprehensive and granular | decided (from your answer) | round 4 |
| [D-056](round-04.md#d-056--the-legacy-import-expects-a-large-corpus-with-legacy-member-numbers) | The legacy import expects a large corpus with legacy member numbers | decided (from your answer) | round 4 |
| [D-057](round-04.md#d-057--household-is-removed) | household is removed | decided (from your answer) | round 4 |
| [D-058](round-05.md#d-058--an-event-is-a-dated-occasion-owned-by-exactly-one-unit) | An event is a dated occasion owned by exactly one unit | decided (from your answer) | round 5 |
| [D-059](round-05.md#d-059--unanswered-is-the-absence-of-a-row-a-registration-stores-two-values) | "Unanswered" is the absence of a row; a registration stores two values | decided (from your answer) | round 5 |
| [D-060](round-05.md#d-060--eligibility-is-capability-there-is-no-separate-rule-engine) | Eligibility is capability; there is no separate rule engine | decided (from your answer) | round 5 |
| [D-061](round-05.md#d-061--event-answers-are-read-by-that-events-organizers) | Event answers are read by that event's organizers | decided (from your answer) | round 5 |
| [D-062](round-05.md#d-062--organizers-are-appointed-on-the-event-not-granted) | Organizers are appointed on the event, not granted | decided (from your answer) | round 5 |
| [D-063](round-05.md#d-063--an-event-is-an-artifact-of-its-unit-not-a-child-of-it) | An event is an ARTIFACT of its unit, not a child of it | decided (from your answer, as a consequence you did not have to state) | round 5 |
| [D-064](round-05.md#d-064--there-is-no-event-status-visibility-is-the-permission-model) | There is no event status; visibility is the permission model | decided (from your answer) | round 5 |
| [D-065](round-05.md#d-065--capacity-is-a-waitlist-threshold-and-organizers-may-exceed-it) | Capacity is a waitlist threshold, and organizers may exceed it | decided (from your answer) | round 5 |
| [D-066](round-05.md#d-066--payment-confirms-the-place-and-the-release-deadline-is-the-one-automatic-transition) | Payment confirms the place, and the release deadline is the one automatic transition | decided (from your answer) | round 5 |
| [D-067](round-05.md#d-067--presence-is-a-three-valued-fact-on-the-registration) | Presence is a three-valued fact on the registration | decided (from your answer) | round 5 |
| [D-068](round-05.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle) | There are no per-resource admin permissions; roles are the bundle | decided (from your answer) — **reverses [D-007](round-01a.md#d-007--every-resource-has-an-admin-level-that-subsumes-narrower-ones--reversed)** | round 5 |
| [D-069](round-05.md#d-069--guardianship-ends-when-a-person-ends-it-the-system-takes-no-position-on-majority) | Guardianship ends when a person ends it; the system takes no position on majority | decided (from your answer) — **reverses [D-024](round-01b.md#d-024--guardianship-does-not-auto-expire-at-majority--reversed)** | round 5 |
| [D-070](round-05.md#d-070--an-event-has-no-age-ceiling-the-grant-is-the-rule) | An event has no age ceiling; the grant is the rule | decided (from your answer) | round 5 |
| [D-071](round-05.md#d-071--nothing-forces-a-role-assignment-to-end-the-gate-and-the-report-are-the-control) | Nothing forces a role assignment to end; the gate and the report are the control | decided (from your answer) — **overrides the recommendation in F-3** | round 5 |
| [D-072](round-06.md#d-072--the-documentation-carries-no-sql-the-schema-is-the-orms-job) | The documentation carries no SQL; the schema is the ORM's job | decided (from your answer) — **closes F-4a** | round 6 |
| [D-073](round-06.md#d-073--guardianship-is-administered-by-its-own-parties-not-by-staff) | Guardianship is administered by its own parties, not by staff | decided (from your answer) — **closes E-5** | round 6 |
| [D-074](round-06.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular) | A guardian's rights are none, view, or write. Nothing more granular | decided (from your answer) — **supersedes the mechanism of D-020; deletes `dependent.*`** | round 6 |
| [D-075](round-06.md#d-075--money-arrives-from-a-bank-api-a-payment-is-requested-by-variable-symbol-and-qr-code) | Money arrives from a bank API; a payment is requested by variable symbol and QR code | decided (from your answer) — **closes finance questions 3, 5 and 6** | round 6 |
| [D-076](round-06.md#d-076--money-that-cannot-be-matched-waits-for-a-person) | Money that cannot be matched waits for a person | decided (from your answer) — **closes EV-3 and finance question 1's sibling** | round 6 |
| [D-077](round-06.md#d-077--messaging-is-direct-by-default-broadcast-is-an-ordinary-scoped-permission-and-the-recipient-chooses-the-channel) | Messaging is direct by default, broadcast is an ordinary scoped permission, and the recipient chooses the channel | decided (from your answer) — **first decision of the communication module** *(amended by | round 6 |
| [D-078](round-06.md#d-078--an-exposure-extends-an-assignment-never-a-direct-grant) | An exposure extends an assignment, never a direct grant | decided — **found by deleting the SQL, not by running it** | round 6 |
| [D-079](round-06.md#d-079--the-guardianship-channel-is-entered-by-shape-not-by-permission-name) | The guardianship channel is entered by shape, not by permission name | decided — consequence of [D-074](round-06.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular) | round 6 |
| [D-080](round-06.md#d-080--five-contradictions-the-translation-surfaced-and-how-each-was-resolved) | Five contradictions the translation surfaced, and how each was resolved | decided — **each resolution is a correction, not a choice between options** | round 6 |
| [D-081](round-06.md#d-081--rule-names-survive-the-deletion-of-their-mechanisms-a-renamed-rule-must-say-who-enforces-it-now) | Rule names survive the deletion of their mechanisms; a renamed rule must say who enforces it now | decided (editorial ruling, ratified this round) | round 6 |
| [D-082](round-07-08.md#d-082--a-direct-message-to-a-minor-is-mirrored-to-the-minors-guardians) | A direct message to a minor is mirrored to the minor's guardians | decided (from your answer) — **closes MSG-1** | rounds 7-8 |
| [D-083](round-07-08.md#d-083--there-is-no-medical-record-personal-data-is-one-class-of-data) | There is no medical record: personal data is one class of data | decided (from your answer) — **closes E-7, resolves H-0, retires the health module** | rounds 7-8 |
| [D-084](round-07-08.md#d-084--descriptive-data-is-organization-defined-at-runtime) | Descriptive data is organization-defined at runtime | decided (from your answer) | rounds 7-8 |
| [D-085](round-07-08.md#d-085--the-identity-machinery-stays-structured-the-boundary-is-rules-not-sensitivity) | The identity machinery stays structured; the boundary is rules, not sensitivity | decided (from your answer) | rounds 7-8 |
| [D-086](round-07-08.md#d-086--a-sensitivity-mark-grades-what-a-grant-exposes-not-the-table-it-reads) | A sensitivity mark grades what a grant exposes, not the table it reads | decided — **by the assistant, during round-7 propagation, not from an answer of yours.** | rounds 7-8 |
| [D-087](round-07-08.md#d-087--merge-chains-stay-because-reversing-a-merge-is-a-supported-operation) | Merge chains stay, because reversing a merge is a supported operation | decided (from your answer) | rounds 7-8 |
| [D-088](round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short) | The accounting skeleton is permanent; the audit trail is short | decided (from your answer). The retention *periods* are a policy you have chosen; whether | rounds 7-8 |
| [D-089](round-07-08.md#d-089--one-live-account-a-colliding-sign-up-files-a-claim-and-creates-nothing) | One live account; a colliding sign-up files a claim and creates nothing | decided (from your answer) | rounds 7-8 |
| [D-090](round-07-08.md#d-090--the-legacy-corpus-is-thousands-of-roster-rows-with-numbers-and-no-money) | The legacy corpus is thousands of roster rows with numbers and no money | decided (from your answer) | rounds 7-8 |
| [D-091](round-09.md#d-091--a-permission-group-is-a-rule-and-a-list-at-once-and-a-rule-may-name-another-group) | A permission group is a rule and a list at once, and a rule may name another group | decided (from your answer) | round 9 |
| [D-092](round-09.md#d-092--the-corpus-is-people-and-events-and-it-names-no-units) | The corpus is people and events, and it names no units | decided (from your answer) | round 9 |
| [D-093](round-09.md#d-093--the-one-off-import-may-create-memberships-both-ends-dated) | The one-off import may create memberships, both ends dated | decided (from your answer) | round 9 |
| [D-094](round-09.md#d-094--the-root-unit-owns-every-imported-event) | The root unit owns every imported event | decided (from your answer) | round 9 |
| [D-095](round-09.md#d-095--units-carry-no-restrictions-joining-one-is-somebody-elses-act) | Units carry no restrictions; joining one is somebody else's act | decided (from your answer) | round 9 |
| [D-096](round-09.md#d-096--a-reused-unit-number-is-a-new-unit-unless-someone-records-the-continuity) | A reused unit number is a new unit unless someone records the continuity | decided (from your answer, and one question back) | round 9 |
| [D-097](round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row) | There are no sub-units. The unit is a scope, not a row | decided (from your answer) | round 10 |
| [D-098](round-10a.md#d-098--a-group-is-a-person_group-explicit-members-a-lifetime-and-no-authority) | A group is a person_group: explicit members, a lifetime, and no authority | decided (from your answer) | round 10 |
| [D-099](round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality) | A grant allows or denies one permission. There is no level, and no locality | decided (from your answer) | round 10 |
| [D-100](round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape) | A role is an office and a group is company: two tables of the same shape | decided (from your answer) | round 10 |
| [D-101](round-10b.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree) | An audience is an expression over named sets, stored as a tree | decided (from your answers) | round 10 |
| [D-102](round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it) | Nothing owns an event. The people connected to it are named by selectors that bind to it | decided (from your answer) | round 10 |
| [D-103](round-10b.md#d-103--an-audience-may-name-another-audience) | An audience may name another audience | decided (from your answer) | round 10 |
| [D-104](round-10b.md#d-104--a-permission-codes-last-segment-is-an-action-and-a-registry-that-prose-contradicts-is-a-fiction) | A permission code's last segment is an action, and a registry that prose contradicts is a fiction | decided — **by the assistant at the close of round 10, not from an answer of yours.** | round 10 |
| [D-105](round-11-12.md#d-105--there-are-no-lists-a-hand-written-set-is-an-expression-like-any-other) | There are no LISTs: a hand-written set is an expression like any other | decided — from your request, with both open points ruled on the same day. | rounds 11-12 |
| [D-106](round-11-12.md#d-106--a-failed-operand-stays-the-empty-set-the-missing-half-was-a-report-not-a-refusal) | A failed operand stays the empty set; the missing half was a report, not a refusal | decided (from your answer) | rounds 11-12 |
| [D-107](round-11-12.md#d-107--the-grammar-opens-an-attribute-may-be-an-operand-and-the-vocabulary-stays-seeded) | The grammar opens: an attribute may be an operand, and the vocabulary stays seeded | decided (from your answer) | rounds 11-12 |
| [D-108](round-11-12.md#d-108--there-is-no-school-operand-a-selector-may-only-name-a-fact-the-model-stores) | There is no SCHOOL operand: a selector may only name a fact the model stores | decided (from your answer) | rounds 11-12 |
| [D-109](round-13.md#d-109--nothing-a-rule-names-is-deleted-deprecated-hidden-disabled--and-a-tab-instead-of-a-report) | Nothing a rule names is deleted: deprecated, hidden, disabled — and a tab instead of a report | decided (from your answer) | round 13 |
| [D-110](round-13.md#d-110--the-expression-is-the-record-of-whom-a-grant-reached) | The expression is the record of whom a grant reached | decided (from your answer) | round 13 |
| [D-111](round-13.md#d-111--the-permission-cache-is-rebuilt-nightly-on-any-ruleset-change-and-on-request) | The permission cache is rebuilt nightly, on any ruleset change, and on request | decided (from your answer) | round 13 |
| [D-112](round-13.md#d-112--the-systems-scale-is-stated-hundreds-of-people-tens-of-registrants-per-event) | The system's scale is stated: hundreds of people, tens of registrants per event | decided (from your answer) | round 13 |
| [D-113](round-13.md#d-113--the-guardianship-channel-has-no-expression-guardians-is-not-a-selector) | The guardianship channel has no expression: GUARDIANS is not a selector | decided (found while closing F-5) | round 13 |
| [D-114](round-14.md#d-114--there-is-no-permission-cache-a-check-resolves-a-request-memoizes-and-the-only-cached-thing-is-a-compilation) | There is no permission cache: a check resolves, a request memoizes, and the only cached thing is a compilation | decided (from your answer) | round 14 |
| [D-115](round-15.md#d-115--a-guardianship-does-not-know-about-membership-right_level-outlives-a-lapse-and-survives-a-renewal) | A guardianship does not know about membership: `right_level` outlives a lapse and survives a renewal | decided (from your answer) | round 15 |
| [D-116](round-16.md#d-116--a-caller-that-is-not-a-person-is-a-registered-key-and-a-key-is-a-third-grantee-kind) | A caller that is not a person is a registered key, and a key is a third grantee kind | decided (from your answer) | round 16 |
| [D-117](round-16.md#d-117--a-key-is-never-inside-an-expression-thirteen-selectors-and-none-of-them-can-name-one) | A key is never inside an expression: thirteen selectors, and none of them can name one | decided (from your answer) | round 16 |
| [D-118](round-16.md#d-118--the-two-channels-that-compare-people-cannot-fire-for-a-key-and-a-deny-on-a-person-does-not-slow-a-key-down) | The two channels that compare people cannot fire for a key, and a deny on a person does not slow a key down | decided (as a consequence of D-116) | round 16 |
| [D-119](round-16.md#d-119--a-key-is-one-row-holding-one-live-secret-and-it-rotates-in-place) | A key is one row holding one live secret, and it rotates in place | decided (from your answer) | round 16 |
| [D-120](round-16.md#d-120--a-key-outlives-whoever-created-it-and-the-report-is-the-control) | A key outlives whoever created it, and the report is the control | decided (from your answer) | round 16 |
| [D-121](round-16.md#d-121--a-key-never-carries-a-persons-authority) | A key never carries a person's authority | decided (from your answer) | round 16 |
| [D-122](round-16.md#d-122--what-a-key-owes-the-catalog-four-codes-at-the-unit-and-the-fourth-owed-thing-declined) | What a key owes the catalog: four codes at the unit, and the fourth owed thing declined | decided (from your answer) | round 16 |
| [D-123](round-16.md#d-123--invariant-19-reads-a-caller-not-a-person) | Invariant 19 reads "a caller", not "a person" | decided (found by writing this round) | round 16 |
| [D-124](round-16.md#d-124--two-defects-systemadmin-satisfies-every-code-and-one-prose-code-named-no-row) | Two defects: `system.admin` satisfies every code, and one prose code named no row | decided (defect fix, not a design change) | round 16 |
| [D-125](round-17.md#d-125--an-empty-actor-column-is-this-system-acting-on-its-own-and-its-name-comes-from-a-fixed-list) | An empty actor column is this system acting on its own, and its name comes from a fixed list | decided (from your answer) | round 17 |
| [D-126](round-17.md#d-126--break-glass-is-a-report-and-a-written-procedure-not-a-mechanism) | Break-glass is a report and a written procedure, not a mechanism | decided (from your answer) | round 17 |
| [D-127](round-18.md#d-127--the-registry-diff-is-a-committed-script-and-it-gates-a-round) | The registry diff is a committed script, and it gates a round | decided (from your answer) | round 18 |
| [D-128](round-18.md#d-128--a-reason-is-text-the-reason_code-table-is-deleted) | A reason is text; the `reason_code` table is deleted | decided (from your answer) | round 18 |
| [D-129](round-18.md#d-129--where-the-register-and-the-page-disagree-the-page-is-wrong) | Where the register and the page disagree, the page is wrong | decided (found while writing the register) | round 18 |
| [D-130](round-18.md#d-130--one-register-answers-who-enforces-an-invariant-and-f-10-closes) | One register answers who enforces each invariant, and F-10 closes | decided | round 18 |
| [D-131](round-18.md#d-131--shape-4-is-not-empty-and-a-code-that-is-referenced-may-not-be-renamed) | Shape 4 is not empty, and a code that is referenced may not be renamed | decided (found by writing the register) | round 18 |
| [D-132](round-18.md#d-132--day-one-is-one-account-holding-systemadmin-and-every-role-after-it-is-written-by-the-organization) | Day one is one account holding `system.admin`; every role after it is written by the organization | decided (from your answer) — **decided in round 18, still unapplied; deferred twice and now round 21's** | round 18 |
| [D-133](round-19.md#d-133--two-trail-rules-stay-unchecked-and-say-so-out-loud) | Two trail rules stay unchecked, and say so out loud | decided (from your answer) | round 19 |
| [D-134](round-19.md#d-134--four-more-polymorphic-columns-get-an-orphan-scan-and-the-audit-row-never) | Four more polymorphic columns get an orphan scan; the audit row never gets one | decided (from your answer) | round 19 |
| [D-135](round-19.md#d-135--the-two-modules-with-no-check-list-get-one-each) | The two modules with no check list get one each | decided (from your answer) | round 19 |
| [D-136](round-19.md#d-136--an-election-is-not-recorded-a-role-holds-only-the-people) | An election is not recorded; a role holds only the people | decided (from your answer) | round 19 |
| [D-137](round-20.md#d-137--a-guardian-may-appoint-a-guardian-and-nobody-at-the-organization-is-told) | A guardian may appoint a guardian, and nobody at the organization is told | decided (from your answer) | round 20 |
| [D-138](round-20.md#d-138--one-permission-guards-the-whole-audit-trail-and-the-widening-is-on-the-record) | One permission guards the whole audit trail, and the widening is on the record | decided (from your answer) | round 20 |
| [D-139](round-20.md#d-139--an-event-question-may-bind-to-a-stored-value-it-prefills-as-a-suggestion-and-writes-back-as-an-answer) | An event question may bind to a stored value: it prefills as a suggestion and writes back as an answer | decided (from your answer) | round 20 |
| [D-140](round-20.md#d-140--nothing-about-an-event-is-deleted-on-a-schedule-and-erasure-empties-an-answer-without-deleting-it) | Nothing about an event is deleted on a schedule, and erasure empties an answer without deleting it | decided (from your answer) | round 20 |
| [D-141](round-20.md#d-141--a-definition-is-live-at-the-save-the-proposal-stage-its-queue-and-its-check-are-deleted) | A definition is live at the save; the proposal stage, its queue and its check are deleted | decided (from your answer) — **and it raises [F-34](../open-questions.md#f-34)** | round 20 |
| [D-142](round-20.md#d-142--the-displayed-name-stays-a-copy-and-the-check-that-counts-its-drift-is-named-at-last) | The displayed name stays a copy, and the check that counts its drift is named at last | decided (from your answer) — **the check it asked for already existed** | round 20 |
| [D-143](round-20.md#d-143--a-delegation-is-validated-once-when-it-is-written-and-stands-to-its-own-end-date) | A delegation is validated once, when it is written, and stands to its own end date | decided (from your answer) — **and it settled a contradiction two pages were living inside** | round 20 |
| [D-144](round-20.md#d-144--right_kind-is-a-note-required-by-the-schema-checked-against-nothing-and-no-longer-claiming-to-be-checked) | `right_kind` is a note: required by the schema, checked against nothing, and no longer claiming to be checked | decided (from your answer) | round 20 |
| [D-145](round-20.md#d-145--access_log-rows-are-deleted-at-24-months-and-the-job-that-does-it-has-a-name) | `access_log` rows are deleted at 24 months, and the job that does it has a name | decided (from your answer) — **the third named exception to "nothing is hard-deleted"** | round 20 |
| [D-146](round-20.md#d-146--an-outbound-call-is-a-persons-act-or-a-job-and-nothing-about-it-is-designed-yet) | An outbound call is a person's act or a job, and nothing about it is designed yet | decided (from your answer) | round 20 |
| [D-147](round-20.md#d-147--presence-stays-on-the-registration-no-clock-of-its-own-no-permission-of-its-own) | Presence stays on the registration: no clock of its own, no permission of its own | decided (from your answer) | round 20 |
| [D-148](round-20.md#d-148--there-is-no-whitelisted-and-the-refusal-is-written-where-the-tiers-are) | There is no `WHITELISTED`, and the refusal is written where the tiers are | decided (from your answer) | round 20 |
| [D-149](round-20.md#d-149--words-are-stored-in-one-language-and-a-label-is-not-translated) | Words are stored in one language, and a label is not translated | decided (from your answer) | round 20 |

## Reversed decisions

- **D-015 — Authority inherits downward through the unit hierarchy.** Reversed by
  [D-031](round-02-03.md#d-031--no-downward-inheritance-of-authority-scope_exposure-is-the-only-crossing)
  (refinement round 2). The organization must not be able to decide permissions over a
  nested unit; authority originates at the unit. The original entry is kept in its round, marked
  reversed, rather than edited away.
- **"Local permissions override global ones"** (a phrasing used in the domain docs, never a
  numbered decision). Amended by
  [D-032](round-02-03.md#d-032--deny-is-absolute-locality-orders-allows-only): still true for **allows**,
  and deliberately **not** true for denies. The statement in isolation was the source of
  the ambiguity, so it no longer appears unqualified anywhere in the docs.
- **Person `deceased` field** (never assigned a decision number; it appeared in the person
  table and the permission catalog). Removed by
  [D-034](round-02-03.md#d-034--the-person-record-holds-no-deceased-flag).
- **`position.is_unique_per_unit`** (a boolean). Replaced by `position.max_holders`
  ([D-033](round-02-03.md#d-033--multiple-people-may-occupy-the-same-position)).
- **The single-rooted hierarchy as an *assumption*** (§2 of the organization docs described a
  national → region → district → group → troop ladder, with groups permitted directly under
  national). Replaced by
  [D-035](round-02-03.md#d-035--one-root-unit-all-sub-units-nest-arbitrarily-beneath-it): one root, arbitrary
  nesting beneath it.
- **Retroactive reparenting as an open question** (C-2). Resolved by
  [D-036](round-02-03.md#d-036--units-cannot-be-reparented-a-unit-that-moves-is-a-new-unit): not permitted
  at all.
- **`membership_type.category`, `min_age`, `max_age`, and the age-out workflow.** Removed by
  [D-038](round-02-03.md#d-038--membership-is-ageless).
- **`unit_membership`** (the name, and the claim that sub-unit belonging is a species of
  membership). Renamed and reframed by
  [D-041](round-02-03.md#d-041--belonging-to-a-sub-unit-is-a-participation-record-not-a-membership).
- **The bulk scope-exposure tool**, its `bulk:` reason marker, and integrity check 12.
  Removed by [D-045](round-02-03.md#d-045--the-bulk-scope-exposure-tool-is-removed); their replacements are
  audiences ([D-042](round-02-03.md#d-042--grants-may-target-audiences-not-only-individuals)).
- **Background checks in every form** (`requires_background_check`, the permission pair, the
  requirement code, the `background_check_officer` role, the expiry report). Removed by
  [D-043](round-02-03.md#d-043--no-background-checks-are-recorded-in-this-system).
- **`requirement_code` and `membership_request_requirement`.** Removed by
  [D-044](round-02-03.md#d-044--nothing-gates-a-membership-request-except-identity-and-payment).
- **The "condition only a narrow set of permissions on membership" recommendation** (a
  recommendation, never a numbered decision). Reversed by
  [D-039](round-02-03.md#d-039--member-permissions-require-a-current-paid-membership): the resolver *does*
  evaluate membership state, with guardianship, ownership and exempt role classes carved out.
- **`role.valid_from` / `valid_to`, the `role.retire` permission, and the resolver's check on
  a role's own period** — all introduced by
  [D-052](round-04.md#d-052--roles-are-runtime-data-the-seed-set-is-not-a-specification) and removed the
  same round by [D-053](round-04.md#d-053--a-role-is-valid-always-only-its-assignment-is-temporal). A
  role is a definition and is valid always; the period lives on `role_assignment`. The
  superseded reasoning is kept in D-052's entry, because *why* it looked right is worth
  knowing.
- **`role.requires_membership` as the *only* way to waive the gate.** Widened by
  [D-051](round-04.md#d-051--the-membership-gate-is-waived-by-a-permission-not-only-by-a-role-flag): the
  flag survives and still answers "is this role membership-dependent?", but a person-level
  `system.gate_exempt` permission now waives the gate for a named individual regardless of
  which roles they hold. The original framing — in which D-6 was a question about which *roles*
  to exempt — is what this supersedes.
- **The seeded sub-unit vocabulary** (`pack`, `group`, `team`, and before them the
  `national`/`region`/`district`/`group`/`troop` ladder). Removed by
  [D-054](round-04.md#d-054--the-sub-unit-vocabulary-is-not-seeded-the-organization-defines-its-own-types):
  the unit-type seed is the root and nothing else, and the organization defines its own types
  as runtime data. The words still appear across these docs as illustration — they are not
  types the system ships with.
- **`household` and `household_member`**, plus `fee_obligation.household_id`, its CHECK arm,
  `ix_obligation_household`, and integrity check 7. Removed by
  [D-057](round-04.md#d-057--household-is-removed). The address is a temporal `person_contact` row of type
  `postal`. **Note this is not in the list as a reversal of [D-019](round-01b.md#d-019--household-membership-grants-no-access):**
  D-019's *principle* — shared address grants no access — is untouched and still binding, since
  the access never came from these tables. Only its subject was deleted.
- **The trimmed-permission-catalog direction implied by F-1** (a review that would cut the
  catalog down to what the organization needs now). Resolved the other way by
  [D-055](round-04.md#d-055--the-permission-catalog-is-deliberately-comprehensive-and-granular): the
  catalog is a deliberately large, granular *menu*, and further permissions arrive with the
  modules not yet specified.

- **`<resource>.admin`, and the resolver's prefix match.** All sixteen per-resource wildcard
  permission codes (`person.admin`, `event.admin`, …) and the `X.admin` branch of `can()` were
  removed by [D-068](round-05.md#d-068--there-are-no-per-resource-admin-permissions-roles-are-the-bundle),
  reversing [D-007](round-01a.md#d-007--every-resource-has-an-admin-level-that-subsumes-narrower-ones--reversed).
  **Two things sharing the name survive and are not reversals:** the `admin` **grant level**
  (rank 40), which is a different mechanism, and `dependent.admin`, which is a shorthand a
  person deliberately stores on one guardianship row rather than an implied capability. The
  failure mode D-007 was written to prevent — a new permission nobody bundled into a role — is
  **accepted**, and integrity check 18 is the net that replaces the wildcard.
- **The guardianship review queue at majority**, together with the computed candidate date it
  relied on. Removed by
  [D-069](round-05.md#d-069--guardianship-ends-when-a-person-ends-it-the-system-takes-no-position-on-majority),
  reversing [D-024](round-01b.md#d-024--guardianship-does-not-auto-expire-at-majority--reversed). Note the
  direction: the replacement is **not** auto-expiry. Both automatic behaviours went. D-024's
  *conclusion* — never silently strip a legally valid arrangement — is kept; its mechanism was
  a deferral that still asserted a date the system cannot justify.
- **The "require `valid_to` on high-authority role assignments" recommendation** (F-3, a
  recommendation, never a numbered decision). Withdrawn by
  [D-071](round-05.md#d-071--nothing-forces-a-role-assignment-to-end-the-gate-and-the-report-are-the-control):
  the membership gate already expires what an expiry date would have expired, for the same
  population, without inventing a date. Read together with D-053, which placed all the weight
  on `role_assignment.valid_to` — the human review report is now the entire control.
- **The proposal to give `event` a `min_age`/`max_age` pair** (raised as EV-1 within this
  round, never built). Declined by
  [D-070](round-05.md#d-070--an-event-has-no-age-ceiling-the-grant-is-the-rule): a registration-time
  condition the capability model does not know about is the first rule-engine rule. No
  reversal, since nothing was shipped — recorded here because the idea will return.
- **Merge chains as an assumption.** Decided by
  [D-087](round-07-08.md#d-087--merge-chains-stay-because-reversing-a-merge-is-a-supported-operation), in
  the same direction the assumption pointed — chains persist and `resolve_person()` walks them.
  It is in this list because of *how* it was argued: the docs justified chains by saying
  flattening would make unmerge impossible, which is a reason resting on a capability nobody
  had asked for. Reversing a human-approved merge is now a requirement, so the conclusion is
  unchanged and the argument behind it is not — and flattening, previously "faster", is now a
  trade against a named feature. The integrity check that read a tombstoned survivor as a
  breach was corrected the same round: under decided chains it is normal.
- **The audit trail as the permanent keeper of values.** Narrowed by
  [D-088](round-07-08.md#d-088--the-accounting-skeleton-is-permanent-the-audit-trail-is-short) to a payload
  window of 24 months (rows survive; `old_values`/`new_values` are emptied). [D-085](round-07-08.md#d-085--the-identity-machinery-stays-structured-the-boundary-is-rules-not-sensitivity)
  is **not** reversed and its overwrite-in-place stands, but its stated justification —
  "the trail is the history" — is true for two years and untrue afterwards, which changes what
  that decision costs. Read the two entries together; neither is complete alone.
- **"A historical roster may create a `membership` if there is payment evidence"** (the safe
  default kept open in `06-audit-and-import.md` §6). Retired rather than answered by
  [D-090](round-07-08.md#d-090--the-legacy-corpus-is-thousands-of-roster-rows-with-numbers-and-no-money):
  the corpus carries no payment data at all, so the exception arm has nothing to fire on and the
  default is simply the rule. Historical rows are `unit_participation`; `membership` comes only
  from the current register. Recorded because the *reason* for the rule — an inferred open-ended
  membership would make a 2003 roster a current member with authority today
  ([D-039](round-02-03.md#d-039--member-permissions-require-a-current-paid-membership)) — is the part worth
  keeping if a corpus with money in it ever arrives. **Retired outright one round later, which is the
  more instructive half:** the corpus turned out to state membership periods directly, so the rule was
  replaced by [D-093](round-09.md#d-093--the-one-off-import-may-create-memberships-both-ends-dated) and the frame
  it rested on by [D-092](round-09.md#d-092--the-corpus-is-people-and-events-and-it-names-no-units). The reason
  survives; the rule does not. A decision recorded from a description of the data is only as durable as
  the description.

- **"An audience does not nest", and `audience.kind`'s rule-*xor*-list split.** Both withdrawn by
  [D-091](round-09.md#d-091--a-permission-group-is-a-rule-and-a-list-at-once-and-a-rule-may-name-another-group):
  a group is now a rule arm, a manual arm and an inclusion arm whose membership is their union, and a
  group may include another. Neither was ever a numbered decision — both were prose in
  `data-model/05 §8`, which is how they survived three rounds of review unexamined while doing real work
  (they are the reason "the crew, plus everyone who leads this pack" needed two grants and why a
  composition the organization asked for in round 9 had been silently impossible). The cycle the nesting
  ban existed to prevent is refused at the write instead, which is the same answer D-087 gave for merge
  chains one round earlier — **worth reading as the pattern rather than the reversal**: when a rule was
  written to prevent a hard case, the first question is whether the hard case can be refused at the write
  rather than defended against at the read.
- **`org_unit_type.allows_minors`, and the write-path check it drove** (integrity check 2 in
  `03-membership.md §7`). Removed by
  [D-095](round-09.md#d-095--units-carry-no-restrictions-joining-one-is-somebody-elses-act): units carry no
  restrictions, and the control is that nobody joins a unit or takes a position in one themself. This is
  in this list because of what replaced it, not because a column went — a *flag on a type* became *a
  permission held by named adults*, which is D-081's "say who enforces it now" answered with a change of
  kind rather than a rename. The consequence is symmetrical: the system can no longer tell anyone which
  units are for children.
- **The correction made to `03-membership.md §5.1` in round 8** — that "an ordinary import touches
  neither arm of this pair", because a roster writes participations and no memberships. Reversed by
  [D-093](round-09.md#d-093--the-one-off-import-may-create-memberships-both-ends-dated) within one round: the
  membership export writes memberships by the thousand, so the root-participation obligation points at
  the import again, which is what that section said before round 8 for entirely different reasons.
  Recorded because a *correction* that gets reversed is the kind a reader will not trust, and the reason
  to trust it here is that both rounds were wrong about the same unknown thing — the shape of a file
  nobody had read.

**Round 10 removed a dimension of the model, and the reversals below are the largest single set in this
log.** They are grouped rather than listed one per line, because they are not twelve independent
reversals: they are one diagnosis (*"I have over-specified the system and this complicates things"*)
drawn through the unit hierarchy, the authority ladder, the membership gate and event ownership at once.

- **The unit hierarchy itself** — `org_unit`, its types, names, relationships, participations and the
  upward `scope_exposure` crossing. Deleted by
  [D-097](round-10a.md#d-097--there-are-no-sub-units-the-unit-is-a-scope-not-a-row): there is one unit, it is the
  organization, and it is a **scope** rather than a row. Reverses D-008, D-035, D-036, D-041, D-049, D-050,
  D-054, D-078, D-096 and deprives [D-031](round-02-03.md#d-031--no-downward-inheritance-of-authority-scope_exposure-is-the-only-crossing)
  of its subject. The property this bought — access to a body's children had to be granted *by that body* —
  is recorded in D-097 as lost, not as replaced.
- **The level ladder** (`access_level`, `permission_level`, the rank integer, and everything that compared
  levels). Deleted by
  [D-099](round-10a.md#d-099--a-grant-allows-or-denies-one-permission-there-is-no-level-and-no-locality): a grant is one
  permission code with an effect of `allow` or `deny`. This reverses
  [D-012](round-01a.md#d-012--status-strings-compare-by-rank-never-lexicographically) including the reason it was
  written (a level string compared alphabetically inverts the model — now there is no level to compare),
  makes [D-013](round-01a.md#d-013--explicit-deny-revoked-is-checked-before-everything)'s deny an effect rather than a
  level, and **deletes half of [D-032](round-02-03.md#d-032--deny-is-absolute-locality-orders-allows-only)**: locality
  only ever ordered allows against each other, and a boolean answer has nothing to order.
  [D-074](round-06.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular) survives on a new
  `permission.right_kind` column, which D-099 names as a column with exactly one customer.
- **The membership gate as a resolver clause** (`role.requires_membership`, `system.gate_exempt`,
  `person_holds_gate_exempt`). Deleted by
  [D-100](round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape), which moves the
  test into the selector: `MEMBERS * ROLE(x)` gates on current membership because `MEMBERS` is evaluated
  live, and leaving `MEMBERS` out is how a role is exempt. Reverses the enforcement half of
  [D-039](round-02-03.md#d-039--member-permissions-require-a-current-paid-membership) and all of
  [D-051](round-04.md#d-051--the-membership-gate-is-waived-by-a-permission-not-only-by-a-role-flag), including the
  lockout hazard D-051 had to document. **The posture reverses from default-on to opt-in**, and the new
  failure mode — a grant written without `MEMBERS` authorizing a lapsed member, silently — is answered with
  a report and an import count, not by the resolver.
- **Positions** (`position`, `position_assignment`, `is_leadership`, `max_holders`) and **`role_assignment`**
  (becoming `role_holder`, with no scope), by
  [D-100](round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape), which also
  deletes `role_permission`: a role confers nothing by itself, and the codes an office carries are the
  grants whose audience names `ROLE(x)`. The elected-versus-appointed distinction survives only as a role
  the organization invents. [F-12](../open-questions.md#f-12)
  is closed, and the answer is no.
- **The audience's three arms, and the inclusion edge.** `audience.resolver_key`, `scope_parameter`,
  `audience_include` and `include_depth_limit` are deleted by
  [D-101](round-10b.md#d-101--an-audience-is-an-expression-over-named-sets-stored-as-a-tree), which replaces them with an
  expression over named sets stored as a tree of binary rows. This **amends
  [D-091](round-09.md#d-091--a-permission-group-is-a-rule-and-a-list-at-once-and-a-rule-may-name-another-group) rather
  than reversing it**: the outcome D-091 wanted — composing *"the kitchen crew, plus whoever leads this
  pack"* in one grant — survives, and the intersection and difference it could not express now can be
  written. What dies with the edge table is the transitive walk, the graph-shaped cycle check and its CI
  assertion, because a tree cannot cycle. The one thing genuinely lost is one-edit widening
  (*"add the crew to everywhere this group is used"*), answered by naming the composite.
- **Event ownership** (`event.org_unit_id`, `can_event()`, the unit-authority rule). Deleted by
  [D-102](round-10b.md#d-102--nothing-owns-an-event-the-people-connected-to-it-are-named-by-selectors-that-bind-to-it),
  which reverses [D-058](round-05.md#d-058--an-event-is-a-dated-occasion-owned-by-exactly-one-unit)'s ownership,
  [D-063](round-05.md#d-063--an-event-is-an-artifact-of-its-unit-not-a-child-of-it) and
  [D-094](round-09.md#d-094--the-root-unit-owns-every-imported-event), and answers "who is connected to this event?"
  with selectors that bind to the item being checked (`ORGANIZERS`, `PLACED`, `CONFIRMED`, …) instead.
  [D-062](round-05.md#d-062--organizers-are-appointed-on-the-event-not-granted) stands untouched: an operand is a set,
  not a grant.

---
