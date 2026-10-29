# Decision Log — Refinement round 15 (D-115)

> A guardianship does not know about membership: a guardian's `right_level` outlives a lapse, and survives a renewal.

[Refinement round 14 (D-114) ←](round-14.md) | [All decisions](index.md)

---

## D-115 — A guardianship does not know about membership: `right_level` outlives a lapse and survives a renewal

**Status:** decided (from your answer)
**Date:** refinement round 15
**Closes:** [E-4](../open-questions.md#e-4),
which had been asking whether the behaviour was intended or merely inherited. It is intended.
**Amends rather than reverses:** [D-039](round-02-03.md#d-039--member-permissions-require-a-current-paid-membership)'s
gate was deleted by [D-100](round-10a.md#d-100--a-role-is-an-office-and-a-group-is-company-two-tables-of-the-same-shape),
and this entry does not bring it back — it gives the one behaviour that gate used to carry an owner of its own.
[D-074](round-06.md#d-074--a-guardians-rights-are-none-view-or-write-nothing-more-granular) and
[D-113](round-13.md#d-113--the-guardianship-channel-has-no-expression-guardians-is-not-a-selector) stand untouched;
this is a consequence of them being written down, not a change to them.

**Decision. The guardianship channel has no knowledge of membership.** A guardian's authority is
`guardianship.right_level ∈ none | view | write`, read off a live `guardianship` row
([D-113](round-13.md#d-113--the-guardianship-channel-has-no-expression-guardians-is-not-a-selector)) — and
nothing else. Not whether the guardian is a current member, not whether their fee is settled, not whether
their own membership has lapsed. Three consequences, all of them wanted:

1. **A lapse does not touch a guardianship.** A membership expiring changes that `membership` row's status
   and nothing else. A parent whose membership lapsed keeps whatever `right_level` their row carries over
   their child.
2. **A renewal finds the right still there.** When that person's membership comes back, their guardian's
   access has not been revoked and does not need to be restored. That is the point of the ruling: the
   relationship to the child did not lapse, so nothing about it should have to be re-granted. Somebody
   re-approving a parent after a renewal would be a second, unstated rule about who counts as that child's
   guardian.
3. **Ending it is an act, not a state.** `right_level` changes to `none` because a named adult wrote it —
   the same shape as the safety property everywhere else in this design, where what protects a record is
   who is allowed to write it
   ([D-095](round-09.md#d-095--units-carry-no-restrictions-joining-one-is-somebody-elses-act)), not a rule
   watching a status.

**Why this needed deciding rather than leaving it as a consequence.** For as long as the membership gate
existed, "a lapsed parent keeps their guardian's right" was an *exemption* — written down, pointable at, and
therefore visibly a choice. Deleting the gate removed the place the exemption lived, so the behaviour
survived without an owner and read like an oversight. The question then sharpened itself: once the
membership test moved into grant expressions, a guardianship had nowhere to be conditioned, because it is
not a grant. It is a channel, and
[D-113](round-13.md#d-113--the-guardianship-channel-has-no-expression-guardians-is-not-a-selector) closed the
last route by which an expression could have reached it — `GUARDIANS` is not a selector in either arity, so
no grant can say *guardians who are members* either. What had been "confirm this is intended" became
"structurally, there is nothing else this could be" — and the answer recorded here is that the
indistinguishability is what the organization wants.

**What is given up, stated plainly.** There is no lever anywhere that conditions a guardian's access on
their membership. An organization that ever wants the posture *members-only guardianship* gets it by
ending the guardianship, not by suspending it, and there is no suspended state to come back from. That is a
coarser instrument than the gate was, and it is the price of a channel with no expression in it; the other
side of the trade is that nobody has to keep two facts about one adult in agreement.

**Where this is written in the docs.** [domain/06](../domain/06-authorization-model.md) for the channels and
what a check reads, [data-model/03](../data-model/03-membership.md) for what a lapse does change, and
[data-model/05b](../data-model/05b-expression-tree.md) for why there is no expression in the channel to write
`MEMBERS` into.

---

*This round is the readability round: the pages were rewritten to state what is, with the reasoning where it
is counter-intuitive and the rest here. Most of what the round produced are rulings already recorded in
earlier entries; this is the one new question it settled.*
