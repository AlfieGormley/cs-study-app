---
id: fp-recursive-progress
title: Recursive progress and pending work
level: intermediate
minutes: 4
sourceLesson: fp-recursion-tail-calls
summary: Termination needs a well-founded decreasing measure.
---

Pure code can use local mutation if it stays unobservable. In a purely functional style, repetition is commonly expressed without mutable loop counters. Instead, repetition comes from **recursion**: a function that calls itself on a smaller problem until it reaches a case it can answer directly.

Recursion is not just a substitute for loops. For recursive data (trees, nested lists, JSON, abstract syntax trees) it's the most natural way to write code, because the shape of the function mirrors the shape of the data.

## Anatomy of a recursive function

A terminating recursion over finite input commonly has two parts:

1. **Base case**: an input simple enough to answer without recursing.
2. **Recursive case**: break the input into a smaller piece, call yourself on it, and combine the result.

```python
# Each call leaves a pending addition.
def length(xs):
    if not xs:                 # base
        return 0
    return 1 + length(xs[1:])  # recursive
```

In Haskell, pattern matching makes the two cases explicit:

```haskell
-- Pattern matching exposes the list tail.
length' :: [a] -> Int
length' []     = 0
length' (_:xs) = 1 + length' xs
```

To prove termination, identify a well-founded measure that decreases towards a base case. The raw input need not shrink on every call; a countdown measure or another ordering may suffice.

> [!note] Structural recursion
> When you recurse on the *parts* of a value (the tail of a list, the children of a tree node), termination follows when the input is finite and acyclic, every recursive call uses a proper subpart, and each case performs only terminating work outside those calls. This is called **structural recursion**, and it's the safest kind.

## What it costs: the call stack

In a conventional non-tail-recursive execution, each active call retains a frame or continuation for its pending work. Compilers and runtimes may optimize that representation.

Look at `1 + length(xs[1:])`. After the recursive call returns, there's still work to do: add 1. So every frame must stay alive until the bottom is reached. You can watch this by rewriting each call into its body, step by step:

```formula
length([a, b, c])
  = 1 + length([b, c])
  = 1 + (1 + length([c]))
  = 1 + (1 + (1 + length([])))
  = 1 + (1 + (1 + 0))
  = 3
where
length: the recursive function above, which counts a list's elements
a, b, c: any three list elements (their values don't matter, only how many there are)
[]: the empty list: the base case, whose length is 0
In words: each call leaves a pending "1 +" waiting for the call below it, so three pending additions pile up before the expression collapses to 3.
```

The expression grows wider as it goes down, then collapses on the way back. In general:

```formula
D(n) = n + 1
D(n) = O(n)
where
D(n): the recursion depth: the most stack frames alive at once while measuring a list of n items
n: the number of items in the list
O(n): Big-O notation: grows in proportion to n (under a fixed-size frame model; this does not count the copied list slices)
In words: there is one call per item plus the empty-list base call; pending-call space grows linearly in this straightforward execution.
```

So a 500-item list needs about 500 frames at its deepest point, and a 5,000-item list needs about 5,000.

CPython commonly defaults to a recursion limit of **1,000**; inspect sys.getrecursionlimit() in the actual process. Node.js also has a finite recursion limit, but no universal frame count is provided here because it depends on engine, flags and frame shape. Deep list recursion is therefore not portable.

> [!warning] Don't just raise the limit
> `sys.setrecursionlimit(10**6)` lets Python try deeper recursion, but memory remains finite and platform-specific calls may still consume C stack. Since CPython 3.11 many Python-to-Python calls avoid recursive C calls, so Python recursion depth and native-stack depth are not identical. Raising the limit can still risk exhaustion or crashes.

## Key takeaways
- Termination needs a well-founded decreasing measure.
- Pending additions retain work in a straightforward recursive execution.

## Further reading
- [Recursion](https://softwarefoundations.cis.upenn.edu/lf-current/Induction.html)
- [Python Sys](https://docs.python.org/3/library/sys.html)
- [Python 311](https://docs.python.org/3/whatsnew/3.11.html)
