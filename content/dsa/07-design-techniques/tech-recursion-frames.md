---
id: tech-recursion-frames
title: Reading the call stack
level: basic
minutes: 3
sourceLesson: tech-recursion
summary: Pending work resumes after a recursive call returns.
---

## What the call stack actually does

The leap of faith is how you *design* recursion. To *debug* it, and to understand its cost, you need the machine's view.

Conceptually, a pending call has a **stack frame** holding parameters, local state and where execution resumes. Implementations can inline calls or eliminate tail calls; the examples here use ordinary CPython frames. A returned frame may remain referenced by debugging or traceback objects. Here is `fact(3)` at its deepest point:

```python
def fact(n):
    # Reject inputs outside the stated
    # domain.
    if type(n) is not int or n < 0:
        raise ValueError("nonnegative n")
    if n <= 1:
        return 1
    # Keep this multiplication pending on
    # return.
    return n * fact(n - 1)
```

```
 top   fact(1)  returns 1
       fact(2)  waiting: 2 * ?
       fact(3)  waiting: 3 * ?
 base  <module>
```

Then the stack unwinds: `fact(1)` returns 1, `fact(2)` computes 2 × 1 = 2, `fact(3)` computes 3 × 2 = 6.

Two consequences follow:

- **Space is proportional to depth.** With constant-sized frame state, a recursion that is d calls deep at its deepest point costs O(d) control-stack space: d frames, each of fixed size. Retained lists, arbitrary-size integers and other objects must be counted separately. A recursive function over a linked list of length n uses O(n) space; over a balanced tree of n nodes, O(log n).
- **Work after the call happens on the way back up.** Along a single call chain, code before the call runs on descent and code after it runs on return; multiple recursive branches are completed in the order the code calls them.

```python
def show(n):
    # Reject inputs outside the stated
    # domain.
    if type(n) is not int or n < 0:
        raise ValueError("nonnegative n")
    if n == 0:
        return
    print(n, end=" ")    # on the way down
    # Pause this frame until the smaller
    # call ends.
    show(n - 1)
    print(n, end=" ")    # on the way up

show(3)   # 3 2 1 1 2 3
```

### Python's recursion limit

CPython limits active recursion and raises `RecursionError` when the configured allowance is exhausted. The usual default is **1000**; inspect `sys.getrecursionlimit()` rather than assuming how many calls remain. Since CPython 3.11, most Python-to-Python calls no longer consume C stack per call. Raising the limit still increases memory/resource exposure, and calls involving C code can have separate stack limits; the documentation warns that an excessively high setting can crash the process.

In practice: a million-node binary tree with near-minimum height has about 20 levels, well below the usual recursion allowance when entered from a shallow call stack. Recursion over a list, a string, or a tree that might degenerate into a chain is a bug waiting for large input.

## Key takeaways
- Pending work resumes after a recursive call returns.
- Control-stack space depends on maximum nesting, not on the number of nodes visited.

## Further reading
- [Python recursion allowance](https://docs.python.org/3/library/sys.html)
- [CPython 3.11 call changes](https://docs.python.org/3/whatsnew/3.11.html)
