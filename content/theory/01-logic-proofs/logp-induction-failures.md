---
id: logp-induction-failures
title: Finding broken links in induction
level: intermediate
minutes: 3
sourceLesson: logp-induction
summary: Every induction link must apply, including the first one.
---

## How induction proofs go wrong

The famous bad proof: "all horses are the same colour".

- **Claim**: any n horses share a colour.
- **Base**, n equals 1: trivially true.
- **Step**: take n plus 1 horses. Remove horse A: the remaining n horses are the same colour by the IH. Remove horse B instead: the same colour again. The two groups overlap, so all n plus 1 match.

The step silently assumes the two groups of n overlap. For n plus 1 equals 2, removing A leaves {B} and removing B leaves {A}: no overlap. The step from P(1) to P(2) fails, so the chain breaks at the first link.

Other common errors:

- **No base case**, or one that doesn't match where the step starts.
- **Assuming P(n plus 1)** in the step and working backwards to something true.
- **Step that doesn't apply to every n**, as with the horses.
- **Calling a strong-induction step on a value below the base**, such as using n minus 4 when n minus 4 is less than 12.


The two-horse failure is decisive even if all later overlap arguments have the expected shape. A chain of implications only carries a true statement as far as its justified links reach. Starting from the one-horse base gives no permission to cross the failed link to two horses. Starting from a larger group would need a new, independently established base; assuming that larger group already has one colour would simply assume the disputed claim.

When reviewing an induction proof, separate the roles of its statements. A checked example establishes a base. The hypothesis is a temporary assumption about the smaller case. The step must transform that assumption into the next case for every permitted index. A true algebraic rearrangement at the end cannot repair a missing range condition at the start. In recursive code, the same review asks whether every recursive path reaches an allowed base and whether each invocation is on a smaller argument covered by the hypothesis.

## Key takeaways
- Every induction link must apply, including the first one.
- Check range restrictions and all required starting cases before trusting a claimed chain.

## Further reading
- [MIT Mathematics for Computer Science](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-spring-2015/mit6_042js15_textbook.pdf)
