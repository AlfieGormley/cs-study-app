---
id: cx-recursion-memory
sourceLesson: cx-space-complexity
title: Pending calls and recursion depth
level: intermediate
minutes: 4
summary: Count live stack frames and understand why caching does not remove the first recursive descent.
---

Here n is the input length or recursive argument. Memoisation remembers returned answers, but the first uncached chain still has to reach its base case. A bottom-up loop avoids that chain.

## The recursion stack

This is where most space mistakes happen. Every call that hasn't returned yet holds a **stack frame** with its local variables, arguments and return address. Recursive code uses space proportional to the **maximum depth of the recursion**, even if it never creates a list.

```python
def fact(n):
    if n <= 1:
        return 1
    # Wait for the smaller call to return.
    return n * fact(n - 1)
```

When `fact(5)` reaches its base case, five frames are alive at once:

```
fact(1)   <- top: about to return 1
fact(2)   waiting to multiply by 2
fact(3)   waiting to multiply by 3
fact(4)   waiting to multiply by 4
fact(5)   waiting to multiply by 5
```

Counting frames and treating values as atomic, `fact` has Θ(n) auxiliary space, where n is its argument; an iterative version keeps a constant number of values. Python integers are not fixed-size: a factorial alone needs Θ(n log n) bits. Its bit length follows the logarithm of its value, and the logarithm of a factorial has that growth rate.

Note that it's **depth**, not the total number of calls, that matters. Naive `fib(n)` makes an exponential number of calls, but at any moment only one path from the root to a leaf is active:

```formula
time(n) = Θ(φ^n)
φ ≈ 1.618
space(n) = Θ(n)
C_fib(n) = Θ(φ^n)
C_merge(n) ≈ 2n
where
time(n): the number of calls naive fib(n) makes, which sets its running time
space(n): the maximum number of stack frames alive at once, which sets its memory use
n: the positive Fibonacci argument, or merge-sort item count for C_merge; fib’s deepest path has n frames
φ: phi, the golden ratio, about 1.618
φ^n: n copies of φ multiplied together
Θ: Big-Theta: grows at exactly this rate, up to a constant factor
≈: approximately equal to
C_fib(n): the naive Fibonacci call count
C_merge(n): the merge-sort call count with one-item leaves
In words: naive Fibonacci takes exponential time but only linear space, because each finished branch hands its stack frames back before the next branch starts.
```

In the table below, n is the input (the argument, or the list length) and logarithmic means base-two logarithmic growth:

| Function | Calls | Maximum live depth |
|---|---|---|
| Factorial | linear | linear |
| Naive Fibonacci | exponential | linear |
| Binary search | logarithmic | logarithmic |
| Merge sort | about twice the item count | logarithmic |

Merge sort’s stack has Θ(log n) depth, where n is the list length, because each call halves its range. The merge buffer needs O(n) space, so total auxiliary space is O(n).

> [!warning] Python stops at 1,000
> CPython's default recursion limit is 1,000 frames (`sys.getrecursionlimit()`). `fact(5000)` raises `RecursionError`. You can raise the limit with `sys.setrecursionlimit`, but very deep recursion stays fragile: every frame costs memory, and recursion that passes through C code can still overflow the real thread stack and crash the interpreter. Python doesn't do **tail-call optimisation**, so even tail-recursive functions use one frame per call. For deep linear recursion, rewrite it as a loop.

Other languages vary. Scheme guarantees proper tail calls. Some C and C++ compilers eliminate tail calls when optimising, but the language standards don't require it. Stack limits depend on the operating system, thread configuration and build, so measure the actual limits and frame costs before relying on a recursion depth.

## Memoisation and stack depth

- **Memoisation.** Caching `fib` results turns Θ(φ^n) time into Θ(n) time, at the cost of Θ(n) space for the cache. A loop keeping just the last two values gets Θ(n) time *and* O(1) space.

## Key takeaways
- Stack space follows the deepest chain of pending calls.
- Many calls over time do not imply that all their frames coexist.
- Caching completed answers avoids repeated work; a cold recursive descent can still reach the recursion limit.

## Further reading
- [Call stack — Wikipedia](https://en.wikipedia.org/wiki/Call_stack)
- [sys.setrecursionlimit — Python docs](https://docs.python.org/3/library/sys.html)
- [Tail call — Wikipedia](https://en.wikipedia.org/wiki/Tail_call)
