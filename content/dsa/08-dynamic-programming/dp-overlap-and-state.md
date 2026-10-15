---
id: dp-overlap-and-state
title: Reusable subproblems and sufficient states
level: basic
minutes: 3
summary: Caching saves work only when the same subproblem is requested repeatedly.
sourceLesson: dp-intro
---

Dynamic programming (DP) is a way of solving a problem by breaking it into smaller subproblems, solving each subproblem **once**, storing the answer, and reusing it whenever the same subproblem comes up again.

That's it. The rest is learning to spot when it applies and how to define the subproblems well.

The name is famously unhelpful. Richard Bellman coined it in the 1950s while working at RAND. "Programming" meant planning, as in a schedule or a table of decisions, not writing code. Bellman later recalled choosing "dynamic" partly because it sounded impressive and was hard to object to; this is his retrospective naming account, rather than a chronology established by the recurrence theory.

## The two ingredients

For the finite, acyclic recurrences in this module, look for reusable subproblems and a valid rule for combining their answers. Overlap explains why caching saves repeated work; some algorithms called tree DP have disjoint subtrees.

### Overlapping subproblems

A naive recursive solution solves the **same** subproblem many times. If every subproblem were new (as in merge sort, where each half is different data), caching would buy nothing. That is plain divide and conquer.

### Optimal substructure

An optimal solution to the whole problem can be **built from optimal solutions to subproblems**. In a nonnegative-weight graph, every segment of a shortest path is itself shortest between its endpoints. If it didn't, you could swap in the shorter piece and improve the whole route.

The property depends on the chosen state. The **longest simple path** between two nodes in a general graph does not have it with endpoints alone: the longest path from A to C via B need not contain the longest path from A to B, because that piece might reuse nodes the rest of the path needs. Recording the visited set restores a valid recurrence but introduces exponentially many possible states. Longest simple path is NP-hard in general; nonnegative-weight shortest paths have polynomial-time algorithms.

> [!note] Counting problems too
> "Optimal substructure" is phrased in terms of optimisation, but DP also counts things ("how many ways...?") and decides things ("is it possible...?"). The general requirement is that the answer for a state can be **combined** from answers for smaller states.

## Key takeaways
- Caching saves work only when the same subproblem is requested repeatedly.
- A valid state must retain every fact needed to combine subanswers safely.

## Further reading
- [CMU notes quoting Bellman’s retrospective account](https://www.cs.cmu.edu/afs/cs/academic/class/15210-f14/www/lectures/dp.pdf)
- [Erickson: dynamic programming](https://jeffe.cs.illinois.edu/teaching/algorithms/book/03-dynprog.pdf)
- [MIT algorithms course](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/)
