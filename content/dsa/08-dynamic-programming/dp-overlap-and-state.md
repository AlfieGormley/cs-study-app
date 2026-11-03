---
id: dp-overlap-and-state
title: Reusable subproblems and sufficient states
level: basic
minutes: 3
summary: Caching saves work only when the same subproblem is requested repeatedly.
sourceLesson: dp-intro
---

Dynamic programming (DP) is a way of solving a problem by breaking it into smaller subproblems, solving each subproblem **once**, storing the answer, and reusing it whenever the same subproblem comes up again.

That's it. The rest is learning to spot when it applies and how to describe each subproblem well.

The name is famously unhelpful. Richard Bellman developed the method in the 1950s, partly while working at RAND. "Programming" meant planning, as in a schedule or a table of decisions, not writing code. In his 1984 autobiography Bellman said he chose "dynamic" because it conveyed multistage, time-varying decisions and could not be used in a pejorative sense, which helped him shield mathematical research from a Secretary of Defense, Charles Wilson, who disliked the word "research". Treat that as a later recollection: Russell and Norvig point out that his first paper using the term (1952) appeared before Wilson took office (1953).

## The two ingredients

Before reaching for DP, look for two things: subproblems that come up repeatedly, and a valid rule for building an answer from the answers to smaller subproblems.

### Overlapping subproblems

A naive recursive solution solves the **same** subproblem many times. Caching helps only when a lookup can hit. If every subproblem were new (as in merge sort, where each half is different data), caching would buy nothing: that is plain divide and conquer.

> [!analogy] Real-world analogy: a shared stock pot
> A restaurant has three soups on the menu, and all three start from the same chicken stock. A sensible kitchen makes the stock once in the morning and ladles it into each soup. A kitchen that made a fresh pot of stock for every bowl would do the same work again and again.
>
> **How it maps:** each soup is a larger problem, the stock is a subproblem that several of them need, and the pot of finished stock is the cache. Making it once and reusing it is exactly what DP does with a repeated subproblem.
>
> **Where it stops:** stock goes off and every bowl uses some of it up. A stored DP answer is just a value: it never changes and can be read any number of times. And reuse only works when the subproblem is *exactly* the same; a merge sort that sorts different slices is like a kitchen whose soups share no ingredient at all.

### Optimal substructure

An optimal solution to the whole problem can be **built from optimal solutions to subproblems**. In a graph with nonnegative edge weights, every segment of a shortest path is itself a shortest path between its endpoints. If it weren't, you could replace that segment with a shorter one and improve the whole route.

Whether this holds depends on what the **DP state** (the information that identifies one subproblem) records. The **longest simple path** between two nodes in a general graph does not have it if the state is just the two endpoints: the longest path from A to C via B need not contain the longest path from A to B, because that piece might use nodes the rest of the path needs. Recording the set of visited nodes as well restores a valid recurrence, but there are exponentially many such sets. Longest simple path is NP-hard in general, while shortest paths with nonnegative weights have fast polynomial-time algorithms.

So a good state is **sufficient**: it holds every fact the rest of the problem depends on, and nothing about how you got there matters beyond what it records.

> [!note] Counting problems too
> "Optimal substructure" is phrased in terms of optimisation, but DP also counts things ("how many ways...?") and decides things ("is it possible...?"). The general requirement is that the answer for a state can be **combined** from answers for smaller states.

## Key takeaways
- Caching saves work only when the same subproblem is requested repeatedly.
- A valid state must retain every fact needed to combine subanswers safely.

## Further reading
- [CMU notes quoting Bellman’s retrospective account](https://www.cs.cmu.edu/afs/cs/academic/class/15210-f14/www/lectures/dp.pdf)
- [Erickson: dynamic programming](https://jeffe.cs.illinois.edu/teaching/algorithms/book/03-dynprog.pdf)
- [MIT algorithms course](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/)
