---
id: dp-evaluation-strategies
title: Choose top-down or bottom-up
level: basic
minutes: 3
summary: Memoisation can skip unreachable states; dense tabulation may fill them.
sourceLesson: dp-intro
---

You have now seen the same Fibonacci recurrence evaluated recursively and iteratively. Choose the evaluation strategy by the reachable states, dependency order and storage requirements.

## Memoisation vs tabulation

Both can evaluate the same recurrence. They may visit different sets of states; they differ in **who decides the order**.

- **Memoisation** lets the recursion discover which subproblems are needed, on demand.
- **Tabulation** has you choose an order up front so that dependencies are always ready.

| | Memoisation | Tabulation |
|---|---|---|
| Direction | Top-down | Bottom-up |
| Order | Automatic | You choose it |
| Unneeded states | Skipped | Usually computed |
| Recursion limit | A risk | No issue |
| Space tricks | Hard | Easy |

> [!analogy] Real-world analogy: two ways to cook a dinner
> One cook starts from the main recipe. Whenever a step says "add the sauce", they pause, make the sauce, label the jar and carry on; if the sauce is needed again, they use the jar. Another cook first works through a prep list in a planned order, so every sauce and stock is ready before the main recipe starts.
>
> **How it maps:** the first cook is memoisation: sub-recipes are made on demand and the labelled jars are the cache. The pile of half-finished recipes they must come back to is the recursion stack. The second cook is tabulation: the prep list is the evaluation order, and it must put every ingredient before the dishes that use it.
>
> **Where it stops:** a kitchen can often reorder prep steps freely, but a DP table order must respect every dependency exactly. And a prep list may make a garnish that nobody ends up using, which is the tabulation cost of filling unreachable states. Both cooks produce the same dinner: the evaluation strategy changes the order and the overheads, never the answer.

### When memoisation wins

- It's **easier to write**: take the recursive definition and add a cache.
- It computes **only reachable states**. If most of a huge state space is never visited, top-down can be far faster.
- The evaluation order can be awkward to work out by hand (trees, DAGs, odd dependency shapes). Recursion handles it for you.

### When tabulation wins

- **No recursive call-depth limit.** CPython usually starts with a recursion limit of 1,000 (`sys.getrecursionlimit()`), but configuration, existing call depth and previously cached answers affect when an error occurs. A cold deep recursive Fibonacci call can fail; the loop avoids that limit, though large exact answers still cost arithmetic time and memory.
- **Potentially lower overhead**: a dense array implementation can avoid recursive calls and dictionary lookups. Actual performance depends on representation and reachable states.
- It enables the **rolling-array** space optimisations, because you control exactly when old rows can be thrown away.

> [!warning] Mutable default arguments
> Writing `def fib(n, memo={})` "works" because Python evaluates the default once and shares it across calls. That is a well-known trap: the cache silently leaks between unrelated calls, which bites you as soon as the inputs change (for example, a memo keyed only on `i` for a function that also depends on a list argument). Use `None` as the default, or `@cache` on an inner function.

## Key takeaways
- Memoisation can skip unreachable states; dense tabulation may fill them.
- Iterative evaluation avoids recursive call-depth limits.
- A cache must have the right key and the right lifetime.

## Further reading
- [Python caching](https://docs.python.org/3/library/functools.html)
- [Erickson: dynamic programming](https://jeffe.cs.illinois.edu/teaching/algorithms/book/03-dynprog.pdf)
