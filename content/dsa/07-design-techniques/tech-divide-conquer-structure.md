---
id: tech-divide-conquer-structure
title: Divide, conquer and combine
level: intermediate
minutes: 4
sourceLesson: tech-divide-conquer
summary: Independent smaller pieces can be solved separately and combined.
---

**Divide and conquer** is recursion with a plan. You divide the input into smaller subproblems, solve them recursively, and combine their answers. Balanced pieces often give efficient recurrences, but unequal splits also count as divide and conquer.

The payoff comes from the cutting. Halving an input of a million items takes only about 20 levels to reach size 1. So even if every level does work proportional to the whole input, the total is about 20 million basic steps, against about half a trillion comparisons for an algorithm that compares every item with every other item. These are scale estimates, not exact instruction counts or timings.

## The three steps

1. **Divide** the input into some number of smaller subproblems, each a fixed fraction of the original size.
2. **Conquer** each subproblem recursively (with a base case for tiny inputs).
3. **Combine** the sub-answers into the answer for the whole.

The cleanest examples have **independent** subproblems that can be solved separately. Repeated equivalent subproblems can waste work; caching them leads toward dynamic programming. Independence alone neither guarantees balanced splits nor eliminates all coordination costs in parallel implementations.

> [!analogy] Real-world analogy: counting votes in an election
> Each polling district counts its own ballots, the districts report to their region, and the regions report to a national total. Nobody needs to see another district's ballots to do their part.
>
> **How it maps:** splitting the country into districts is the divide step; each district's count is an independent subproblem; adding the reported totals is the combine step. Because districts don't overlap, no ballot is counted twice, which is what "independent subproblems" means.
>
> **Where it stops:** an election splits the country once into fixed districts. A divide-and-conquer algorithm keeps splitting the same way until pieces are tiny, and its combine step can be much more expensive than adding two numbers, as merging sorted lists or checking a boundary strip shows.

## Analysing it: recurrences

The cost of a divide-and-conquer algorithm is a **recurrence**: an equation that gives the running time on an input in terms of the running time on smaller inputs. Its shape is the relationship the rest of this module reasons about:

```formula essential
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

Merge sort, for example, makes two half-size calls and does linear work to merge their answers.

Draw the recursion tree to see where the time goes. Going down one level multiplies the number of calls by a and divides each call's input size by b. Whether the total is dominated by the root, by the leaves or spread evenly depends on which of those two effects wins: how fast the number of calls grows compared with how fast the per-call work shrinks. The next unit turns that race into a rule.

## Key takeaways
- Independent smaller pieces can be solved separately and combined.
- Repeated equivalent subproblems call for caching rather than repeated plain recursion.

## Further reading
- [Recursive algorithms — Erickson](https://jeffe.cs.illinois.edu/teaching/algorithms/book/01-recursion.pdf)
- [Divide and conquer](https://en.wikipedia.org/wiki/Divide-and-conquer_algorithm)
