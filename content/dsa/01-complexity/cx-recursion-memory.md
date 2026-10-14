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

Counting frames and treating arithmetic values as atomic, `fact` uses Θ(n) auxiliary space (n frames for `fact(n)`); an iterative version keeps a constant number of values. Actual Python integers are not fixed-size: n! (n factorial) alone needs Θ(n log n) bits, because the number of bits is the logarithm of the value and log(n!) grows like n log n.

Note that it's **depth**, not the total number of calls, that matters. Naive `fib(n)` makes an exponential number of calls, but at any moment only one path from the root to a leaf is active:

```formula
time(n) = Θ(φ^n) ≈ Θ(1.618^n)
space(n) = Θ(n)
where
time(n): the number of calls naive fib(n) makes, which sets its running time
space(n): the maximum number of stack frames alive at once, which sets its memory use
n: the argument passed to fib, which is also the depth of the deepest path in the recursion tree
φ: phi, the golden ratio, about 1.618
φ^n: n copies of φ multiplied together
Θ: Big-Theta: grows at exactly this rate, up to a constant factor
≈: approximately equal to
In words: naive Fibonacci takes exponential time but only linear space, because each finished branch hands its stack frames back before the next branch starts.
```

In the table below, n is the input (the argument, or the list length) and log n is the base-2 logarithm of n:

| Function | Calls | Max depth (space) |
|---|---|---|
| fact(n) | n | n |
| naive fib(n) | ~1.618^n | n |
| binary search | log n | log n |
| merge sort | ~2n | log n |

(Merge sort's stack is only log n deep, because each call halves the list, but its merge step needs an O(n) buffer, so its total auxiliary space is O(n).)

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
