---
id: fp-tail-accumulators
title: Tail position and accumulator recursion
level: intermediate
minutes: 3
sourceLesson: fp-recursion-tail-calls
summary: A tail call returns directly without pending work.
---

A tail call returns directly without pending work. This unit develops that mechanism using the earlier units as prerequisites.

## Tail calls

A call is a **tail call** if it's the very last thing a function does: its result is returned directly, with nothing left to compute.

```python
# Pending work determines tail position.
def f(n):
    return g(n) + 1   # NOT a tail call

def f(n):
    return g(n + 1)   # tail call
```

When a call is in tail position, the current frame has nothing left to do. A language can reuse the frame for the callee instead of pushing a new one. This is **tail call optimisation** (TCO), or more precisely **proper tail calls** when the language guarantees it. For a tail-call chain whose other work uses bounded call space, this removes stack growth from the chain. Here O(1) stack means a bound independent of the number of recursive steps; retained data, slices and lazy thunks can still grow.

## The accumulator pattern

To make a function tail-recursive, carry the partial result in an extra parameter, the **accumulator**, instead of leaving work for after the call returns:

```python
# Carry the running count in acc.
def length(xs, acc=0):
    if not xs:
        return acc
    return length(xs[1:], acc + 1)
```

```formula
length([a, b, c], 0)
  = length([b, c], 1)
  = length([c], 2)
  = length([], 3)
  = 3
where
length: the accumulator version above; its second argument is the count so far
a, b, c: any three list elements
[]: the empty list, where the accumulated count is returned
In words: nothing is left pending between steps; the count travels forward in the second argument, so each line is the whole remaining computation.
```

The pending expression stays the same width; a runtime with TCO can discard the caller. CPython retains the calls, and Python list slicing still copies data.

```haskell
-- The accumulator carries deferred work.
sumTo :: Int -> Int -> Int
sumTo acc 0 = acc
sumTo acc n = sumTo (acc + n) (n - 1)
```

For the shown `sumTo`, assume a nonnegative countdown argument and an `Int` result within its supported range. The same accumulator technique applies to factorial, sum, reverse and many folds; argument domains and arithmetic overflow still need checking.

## Key takeaways
- A tail call returns directly without pending work.
- Accumulator syntax alone does not remove Python calls or slicing costs.

## Further reading
- [Scheme](https://standards.scheme.org/corrected-r7rs/r7rs-Z-H-5.html)
- [Python Sys](https://docs.python.org/3/library/sys.html)
- [Haskell List](https://hackage.haskell.org/package/base/docs/Data-List.html)
