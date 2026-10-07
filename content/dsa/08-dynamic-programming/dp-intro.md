---
id: dp-intro
title: What dynamic programming is
level: basic
minutes: 11
summary: Overlapping subproblems and optimal substructure, how Fibonacci goes from exponential to linear, and the difference between memoisation and tabulation.
---

Dynamic programming (DP) is a way of solving a problem by breaking it into smaller subproblems, solving each subproblem **once**, storing the answer, and reusing it whenever the same subproblem comes up again.

That's it. The rest is learning to spot when it applies and how to define the subproblems well.

The name is famously unhelpful. Richard Bellman coined it in the 1950s while working at RAND. "Programming" meant planning, as in a schedule or a table of decisions, not writing code. By his own account he picked "dynamic" partly because it sounded impressive and was hard to object to.

## The two ingredients

For the finite, acyclic recurrences in this module, look for reusable subproblems and a valid rule for combining their answers. Overlap explains why caching saves repeated work; some algorithms called tree DP have disjoint subtrees.

### Overlapping subproblems

A naive recursive solution solves the **same** subproblem many times. If every subproblem were new (as in merge sort, where each half is different data), caching would buy nothing. That is plain divide and conquer.

### Optimal substructure

An optimal solution to the whole problem can be **built from optimal solutions to subproblems**. In a nonnegative-weight graph, every segment of a shortest path is itself shortest between its endpoints. If it didn't, you could swap in the shorter piece and improve the whole route.

The property depends on the chosen state. The **longest simple path** between two nodes in a general graph does not have it with endpoints alone: the longest path from A to C via B need not contain the longest path from A to B, because that piece might reuse nodes the rest of the path needs. Recording the visited set restores a valid recurrence but introduces exponentially many possible states. Longest simple path is NP-hard in general; nonnegative-weight shortest paths have polynomial-time algorithms.

> [!note] Counting problems too
> "Optimal substructure" is phrased in terms of optimisation, but DP also counts things ("how many ways...?") and decides things ("is it possible...?"). The general requirement is that the answer for a state can be **combined** from answers for smaller states.

## Fibonacci: the classic example

The Fibonacci numbers are defined by `F(0) = 0`, `F(1) = 1`, and `F(n) = F(n-1) + F(n-2)`. The definition translates directly into code:

```python
def fib(n):
    if type(n) is not int or n < 0:
        raise ValueError("nonnegative n")
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)
```

For nonnegative integer n it is correct, but becomes expensive as n grows. Look at the call tree for `fib(5)`:

```
              fib(5)
           /         \
       fib(4)        fib(3)
       /    \        /    \
   fib(3) fib(2)  fib(2) fib(1)
   /   \   / \     / \
 f(2) f(1) ...    ...
```

`fib(3)` is computed twice, `fib(2)` three times, `fib(1)` five times. These are the overlapping subproblems.

The total number of calls is `2·F(n+1) − 1`. For `fib(5)` that is 15 calls; for `fib(30)` it is 2,692,537; for `fib(40)` it is about 331 million. The running time grows like φⁿ, where φ ≈ 1.618 is the golden ratio. It's exponential, even though there are only `n + 1` distinct subproblems.

### Fix 1: memoisation (top-down)

Keep the recursion, but remember every answer. Before computing `fib(k)`, check the cache.

```python
def fib(n, memo=None):
    if type(n) is not int or n < 0:
        raise ValueError("nonnegative n")
    if memo is None:
        memo = {}
    if n < 2:
        return n
    if n not in memo:
        memo[n] = fib(n - 1, memo) + \
                  fib(n - 2, memo)
    return memo[n]
```

Python has this built in:

```python
from functools import cache

@cache
def fib(n):
    if type(n) is not int or n < 0:
        raise ValueError("nonnegative n")
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)
```

In a cold, single-threaded `@cache` call with n ≥ 2, each body executes once for k = 0..n; later requests hit the cache. The manual version does not cache its constant-time base cases. Counting integer additions and dictionary operations as unit cost gives **O(n) work and O(n) stored numbers**, plus recursive stack space.

The call tree collapses into a chain:

```
fib(5) -> fib(4) -> fib(3) -> fib(2) -> ...
   \         \         \
  fib(3)    fib(2)    fib(1)
  (hit)     (hit)     (hit)
```

### Fix 2: tabulation (bottom-up)

Turn the recursion inside out. Fill a table from the smallest subproblem upwards, so that every value you need has already been computed.

```python
def fib(n):
    if type(n) is not int or n < 0:
        raise ValueError("nonnegative n")
    if n < 2:
        return n
    table = [0] * (n + 1)
    table[1] = 1
    for i in range(2, n + 1):
        table[i] = table[i-1] + table[i-2]
    return table[n]
```

Same O(n) time, same O(n) space, but no recursion.

### Fix 3: keep only what you need

`table[i]` only looks back two entries, so the rest of the table is dead weight. Keep two variables:

```python
def fib(n):
    if type(n) is not int or n < 0:
        raise ValueError("nonnegative n")
    a, b = 0, 1  # F(0), F(1)
    for _ in range(n):
        a, b = b, a + b
    return a
```

**O(n) additions, O(1) integer slots.** With Python’s exact integers, F(n) has Θ(n) bits: this loop uses O(n) bits and O(n²) bit work, while retaining the whole Fibonacci table uses Θ(n²) bits. This "keep only the last few rows" trick is a standard DP space optimisation you'll see again for grids and knapsack.

The table counts unit-cost arithmetic and integer slots rather than bits.

| Version | Unit-cost work | Extra slots |
|---|---|---|
| Naive recursion | O(φⁿ) | O(n) stack |
| Memoised | O(n) | O(n) |
| Tabulated | O(n) | O(n) |
| Two variables | O(n) | O(1) |

> [!tip] The cost formula
> Sum the work over evaluated states. **(Number of states) × (maximum work per state)** is a useful upper bound; include preprocessing, reconstruction and operand-bit costs when relevant.

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

### When memoisation wins

- It's **easier to write**: take the recursive definition and add a cache.
- It computes **only reachable states**. If most of a huge state space is never visited, top-down can be far faster.
- The evaluation order can be awkward to work out by hand (trees, DAGs, odd dependency shapes). Recursion handles it for you.

### When tabulation wins

- **No recursive call-depth limit.** CPython usually starts with a recursion limit of 1,000 (`sys.getrecursionlimit()`), but configuration, existing call depth and warm cache entries affect when an error occurs. A cold deep recursive Fibonacci call can fail; the loop avoids that limit, though large exact answers still cost arithmetic time and memory.
- **Potentially lower overhead**: a dense array implementation can avoid recursive calls and dictionary lookups. Actual performance depends on representation and reachable states.
- It enables the **rolling-array** space optimisations, because you control exactly when old rows can be thrown away.

> [!warning] Mutable default arguments
> Writing `def fib(n, memo={})` "works" because Python evaluates the default once and shares it across calls. That is a well-known trap: the cache silently leaks between unrelated calls, which bites you as soon as the inputs change (for example, a memo keyed only on `i` for a function that also depends on a list argument). Use `None` as the default, or `@cache` on an inner function.

## DP vs its neighbours

| Technique | Subproblems | Choice |
|---|---|---|
| Typical divide and conquer | Separate smaller inputs | Combine recursive results |
| Greedy | One per step | Commit locally |
| Typical DP | Reusable states | Combine feasible alternatives |

**Greedy** makes one locally best choice and never revisits it. It can avoid examining alternatives, but needs a proof that the local choice is safe. DP tries every option for each decision and keeps the best, which is why it handles problems where greedy fails (you'll see coin change with coins `{1, 3, 4}` in lesson 3).

## Where DP shows up in the real world

DP is not just an interview topic. A few systems that are DP at their core:

- **`diff` and `git diff`** are built on longest common subsequence and related edit-script algorithms.
- **Spell checkers and fuzzy search** use edit (Levenshtein) distance.
- **Bioinformatics** aligns DNA and protein sequences with Needleman–Wunsch and Smith–Waterman, both grid DPs.
- **Hidden Markov models** use Viterbi decoding to find the most likely hidden-state sequence; speech recognition is a classical application.
- **Network routing**: Bellman–Ford, used in distance-vector protocols like RIP, is DP over path lengths.
- **Query optimisers** in databases have long used DP to choose join orders (the System R approach).

## Common pitfalls

1. **Caching without overlap.** Memoising standard merge sort by input interval adds overhead and does not reuse an interval; a content-based cache has different key costs and may reuse equal-valued segments. Check that subproblems actually repeat.
2. **A state that's missing information.** If the answer depends on something you didn't put in the cache key, the cache returns wrong answers. More in the next lesson.
3. **Forgetting base cases**, which leads to infinite recursion or off-by-one tables.
4. **Exponential numbers.** `F(1000)` has 209 digits. Python integers grow as needed. Fixed-width Java integer arithmetic wraps; signed integer overflow in C++ is undefined behavior, while arbitrary-precision libraries are available. Reduce modulo a value only when that is the requested output.

## Key takeaways
- DP = solve each subproblem once, store it, reuse it.
- Choose sufficient states and a valid combination rule; overlap is what makes caching save repeated work.
- Naive Fibonacci makes `2·F(n+1) − 1` calls; memoising or tabulating needs O(n) additions; two variables use O(1) integer slots, whose bit sizes grow with n.
- Memoisation is top-down and on demand; tabulation is bottom-up in an order you choose. The same recurrence may be evaluated on different subsets of states.
- Running time ≈ number of states × work per state.

## Further reading
- [Dynamic programming — Wikipedia](https://en.wikipedia.org/wiki/Dynamic_programming)
- [Overlapping subproblems — Wikipedia](https://en.wikipedia.org/wiki/Overlapping_subproblems)
- [Optimal substructure — Wikipedia](https://en.wikipedia.org/wiki/Optimal_substructure)
- [functools.cache — Python docs](https://docs.python.org/3/library/functools.html)
- [Jeff Erickson, Algorithms, ch. 3: Dynamic Programming (PDF)](https://jeffe.cs.illinois.edu/teaching/algorithms/book/03-dynprog.pdf)
