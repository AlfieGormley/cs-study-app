---
id: dp-balloons-last
title: Burst balloons by choosing the last move
level: advanced
minutes: 3
summary: An early burst changes the adjacency of the remaining pieces.
sourceLesson: dp-interval-tree
---

## Burst balloons: think about the last move

> Balloons in a row have numbers. Bursting balloon k earns the product of its value and both neighbours’ values, where left and right are its *current* neighbours (or 1 past the ends). Maximise total coins.

The obvious state, "which balloon do I burst **first** in `[i, j]`?", fails: after bursting it, its neighbours become adjacent, so the two halves aren't independent.

The trick is to ask which balloon is burst **last** in an open interval `(i, j)`. The subproblem keeps boundary balloons i and j present. If k is last, then when it is burst its neighbours are exactly i and j (everything between has gone). And the balloons in `(i, k)` and `(k, j)` never interact with each other, because k stands between them the whole time.

Pad the array with 1s at both ends: `a = [1] + nums + [1]`.

```formula
B[i][j] = max(B[i][k] + B[k][j]
  + a_i a_k a_j)   for i < k < j
B[i][i + 1] = 0
where
B[i][j]: the most coins obtainable by bursting every balloon strictly between positions i and j, with i and j still present
a_k: the number on balloon k in the padded array a (a[k] in code), whose two ends are 1
a_i, a_j: the numbers on the two boundary balloons i and j
i, j: the boundary positions, kept unburst
k: the balloon burst last between i and j
max: the largest value over every choice of k
In words: choose which balloon goes last; at that moment its neighbours are the two boundaries, and the balloons on each side were burst independently before it.
```

The base case says there is nothing to burst when no balloons lie strictly between i and j.

For `[3, 1, 5, 8]` the answer is **167**: burst 1 (3·1·5 = 15), then 5 (3·5·8 = 120), then 3 (1·3·8 = 24), then 8 (1·8·1 = 8).

> [!tip] First vs last
> When a choice changes the neighbours of what's left, try defining the recurrence by the **last** action in the interval instead of the first. The last action sees a fixed boundary; the first one doesn't.

## Key takeaways
- An early burst changes the adjacency of the remaining pieces.
- Choosing the last burst fixes both boundary neighbours.
- Two open subintervals can then be solved independently.

## Further reading
- [Erickson: dynamic programming](https://jeffe.cs.illinois.edu/teaching/algorithms/book/03-dynprog.pdf)
- [MIT algorithms course](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/)
