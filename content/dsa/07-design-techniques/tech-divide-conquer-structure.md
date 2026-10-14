---
id: tech-divide-conquer-structure
title: Divide, conquer and combine
level: intermediate
minutes: 4
sourceLesson: tech-divide-conquer
summary: Independent smaller pieces can be solved separately and combined.
---

**Divide and conquer** is recursion with a plan. You divide the input into smaller subproblems, solve them recursively, and combine their answers. Balanced pieces often give efficient recurrences, but unequal splits also count as divide and conquer.

The payoff comes from the cutting. Halving an input of a million items takes only about 20 levels to reach size 1, so even if every level does work proportional to the input size, the total stays small. Compare that with an algorithm that pairs every item with every other item:

```formula
L = log_2(n) = log_2(1,000,000) ≈ 20
W_dc = nL ≈ 1,000,000 × 20
W_dc ≈ 20,000,000
W_sq = n^2 = 1,000,000^2
W_sq = 1,000,000,000,000
where
n: the number of input items, here one million
L: the real-valued logarithmic scale for halving from n items to one; actual recursion levels are whole numbers
log_2(n): the base-2 logarithm of n, the number of times you can halve n before reaching 1; log_2(1,000,000) ≈ 19.93
W_dc: the rough work, in basic steps, of a divide-and-conquer algorithm that does about n steps on each level
W_sq: the rough work, in basic steps, of a quadratic algorithm that compares every item with every other item
n^2: n squared, n × n
≈: approximately equal to
In words: about 20 levels of a million steps each is about 20 million steps, against a trillion for the all-pairs approach: 50,000 times less work.
```

These growth expressions are scale estimates, not exact instruction counts or timings.

## The three steps

1. **Divide** the input into some number of smaller subproblems, each a fixed fraction of the original size.
2. **Conquer** each subproblem recursively (with a base case for tiny inputs).
3. **Combine** the sub-answers into the answer for the whole.

The cleanest examples have **independent** subproblems that can be solved separately. Repeated equivalent subproblems can waste work; caching them leads toward dynamic programming. Independence alone neither guarantees balanced splits nor eliminates all coordination costs in parallel implementations.

## Analysing it: recurrences

The cost of a divide-and-conquer algorithm is a **recurrence**: an equation that gives the running time on an input in terms of the running time on smaller inputs.

```formula
T(n) = aT(n / b) + f(n)
where
T(n): the running time on an input of size n, in basic steps
n: the input size (number of items, digits or points)
a: the number of subproblems each call creates; a fixed number of at least 1
b: the factor by which the input shrinks; each subproblem has size n / b; a fixed number greater than 1
T(n / b): the running time of one subproblem
f(n): the work one call does itself, outside its recursive calls: dividing the input and combining the answers
In words: one call costs the cost of its a smaller calls, plus the work it does itself to split and to combine.
```

```formula
a = 2, b = 2
f(n) = Θ(n)
where
a: the number of recursive subproblems
b: the factor by which each subproblem shrinks
n: the number of input items
f(n): the local splitting and merging work, in unit-cost steps
Θ: Big-Theta, growth bounded above and below by constant multiples
In words: Merge sort makes two half-size calls and combines their answers with linear work.
```

Draw the recursion tree to see where the time goes:

```formula
N_k = a^k
s_k = n / b^k
where
N_k: the number of calls (nodes) on level k of the recursion tree
s_k: the input size of each call on level k
k: the level number, 0 at the root (the first call)
a: the number of subproblems per call
b: the shrink factor per level
n: the original input size
a^k: k copies of a multiplied together
b^k: k copies of b multiplied together
In words: going down one level multiplies the number of calls by a and divides each call's input size by b.
```

Whether the total is dominated by the root, the leaves or spread evenly depends on how fast the number of calls grows compared with how fast the per-call work shrinks.

## Key takeaways
- Independent smaller pieces can be solved separately and combined.
- Repeated equivalent subproblems call for caching rather than repeated plain recursion.

## Further reading
- [Recursive algorithms — Erickson](https://jeffe.cs.illinois.edu/teaching/algorithms/book/01-recursion.pdf)
- [Divide and conquer](https://en.wikipedia.org/wiki/Divide-and-conquer_algorithm)
