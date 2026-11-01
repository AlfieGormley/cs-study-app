---
id: tech-recursion-costs
title: Repeated calls and hidden slice costs
level: basic
minutes: 3
sourceLesson: tech-recursion
summary: A recursion tree counts repeated work, not just distinct arguments.
---

## The cost of recursion: recursion trees

When a function makes more than one recursive call, draw the **recursion tree** to estimate its cost. Each non-base invocation of naive Fibonacci makes two recursive calls:

```python
def fib(n):
    # Reject inputs outside the stated
    # domain.
    if type(n) is not int or n < 0:
        raise ValueError("nonnegative n")
    if n < 2:
        return n
    # The two branches repeat smaller
    # arguments.
    return fib(n - 1) + fib(n - 2)
```

```
            fib(4)
          /        \
      fib(3)       fib(2)
      /    \       /    \
  fib(2) fib(1) fib(1) fib(0)
  /    \
fib(1) fib(0)
```

Count the boxes: `fib(4)` makes 9 calls, `fib(5)` makes 15 and `fib(30)` makes about 2.7 million, yet there are only n + 1 different arguments (0 to n). The same subproblems are solved again and again: `fib(2)` appears twice in the small tree above, and far more often in bigger ones.

The call count itself follows a Fibonacci-like pattern, because each call is one call plus all the calls its two children make. So each step up in the argument multiplies the number of calls by roughly 1.6 (the golden ratio): exponential growth.

```formula reference
C(n) = 1 + C(n − 1) + C(n − 2)
C(n) = 2F(n + 1) − 1
where
C(n): the total number of calls that fib(n) makes, including itself, for n of at least 2; C(0) = C(1) = 1
n: the non-negative whole number passed to fib
F(n): the nth Fibonacci number (F(0) = 0, F(1) = 1, each later one the sum of the previous two)
In words: a call is itself plus the calls of its two children, which makes the call count about twice a Fibonacci number, growing by a factor of about 1.6 per step.
```

Caching results (memoisation) removes the repetition: each argument is computed once, so the number of additions drops to O(n). The integers still get longer as n grows, so this is not an O(n) bit-cost claim. That idea is the heart of the dynamic programming module.

> [!analogy] Real-world analogy: a family tree of questions
> Imagine a family-history volunteer who, asked about a person, must separately research both parents, and for each parent research both of theirs, without keeping notes. When distant cousins have married, the same people appear on several branches and get researched again every time they turn up.
>
> **How it maps:** each research job is a call; the two parents are the two recursive calls; a person who appears on several branches is a repeated subproblem such as `fib(2)`. Keeping a notebook of finished answers is memoisation.
>
> **Where it stops:** in a real family tree, people shared between branches turn up irregularly and the records eventually run out. Naive Fibonacci repeats in a perfectly regular way and always ends at the base cases 0 and 1, which is what makes its call count follow its own Fibonacci pattern.

## Hidden O(n) work per call

Here n is the original list length. `return xs[0] + total(xs[1:])` looks linear, but each slice copies the rest of the list:

- The first call copies n − 1 references, the next n − 2, and so on down to 0. Those copies add up to about half of n squared, so the running time is **O(n²)**, assuming constant-cost element addition.
- Every frame keeps its slice alive until it returns, and at the deepest point all of the frames are still waiting. So peak memory is **O(n²)** as well, not just O(n) for the frames.

A thousand-item list makes about half a million reference copies instead of a thousand additions. The fix is to pass an index (`total(xs, i + 1)`) so each call does constant work, or, in Python, to use a loop.

## Key takeaways
- A recursion tree counts repeated work, not just distinct arguments.
- A copied slice retained by each frame can turn linear-looking recursion into quadratic work and storage.

## Further reading
- [Recursive cost analysis — Erickson](https://jeffe.cs.illinois.edu/teaching/algorithms/book/01-recursion.pdf)
- [Python lists and slices](https://docs.python.org/3/tutorial/introduction.html#lists)
