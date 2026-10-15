---
id: cplx-reduction-pitfalls
title: "Checking direction, size and reduction type"
level: intermediate
minutes: 3
summary: "A valid reduction must be polynomial and preserve answers in both directions."
sourceLesson: cplx-reductions
---

## Pitfalls that invalidate a reduction

1. **Wrong direction.** To show X is hard, map *from* the known hard problem *to* X.
2. **Only one direction proved.** You need both directions: every yes-instance must map to a yes-instance, *and* every instance that maps to a yes-instance must itself be a yes-instance (equivalently, no-instances map to no-instances). Many broken proofs show only that satisfying assignments give solutions.
3. **Using the answer.** The reduction can't "first find a satisfying assignment". It must run in polynomial time without solving the problem.
4. **Exponential blow-up.** Encoding every possible assignment, or writing numbers in unary, breaks polynomial time.
5. **Forgetting membership.** Hardness plus a reduction gives NP-hard; you still need to show X is in NP to claim NP-complete.

> [!note] Karp versus Cook reductions
> Everything here is a **many-one (Karp)** reduction: one call to B, answer passed through unchanged. A **Turing (Cook)** reduction may call B many times and post-process. Turing reductions are more powerful; for example, they make SAT and UNSAT reduce to each other trivially, which blurs NP versus coNP. NP-completeness is standardly defined with Karp reductions.

## Key takeaways

- A valid reduction must be polynomial and preserve answers in both directions.
- The construction cannot assume a solution to the source problem.
- Karp reductions pass through one answer; Cook reductions may adapt and negate answers.

## Further reading

- [Computational Complexity — Arora and Barak](https://theory.cs.princeton.edu/complexity/book.pdf)
