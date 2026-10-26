---
id: cx-recursion-memory
sourceLesson: cx-space-complexity
title: Pending calls and recursion depth
level: intermediate
minutes: 3
summary: Count live stack frames and understand why caching does not remove the first recursive descent.
---

Every call that is waiting for a child needs a frame containing its local state. Space follows the deepest chain of pending calls, together with data those calls retain.

```python
def fact(n):
    if n <= 1:
        return 1
    return n * fact(n - 1)
```

For a positive argument n, this creates a chain down to one. Under a model treating each number as atomic and each frame as fixed-size, stack space is Θ(n). An iterative version holds a constant number of values. Actual Python integers grow: the factorial result alone needs Θ(n log n) bits for sufficiently large n.

## Calls over time are not simultaneous frames

Naive Fibonacci makes exponentially many calls but follows one child at a time. Completed branches release their frames before later siblings finish. Its maximum depth is linear in the argument, so its stack is linear in the atomic-value model.

Recursive binary search with index bounds has logarithmic depth because it halves the range. Merge sort also has logarithmic depth, but its merge buffer requires linear extra space. Count retained buffers as well as frames.

> [!analogy] Real-world analogy: A stack of unfinished tasks
> When a task depends on a smaller task, put a reminder aside until that task finishes.
>
> **How it maps:** Each reminder is a pending frame. The tallest pile matters for space, even if many reminders are used throughout the day.
>
> **Where it stops:** Frames can retain differently sized objects; counting reminders alone assumes fixed-size state.

## Caching does not shorten the first descent

Memoisation avoids repeating completed calculations. With an empty cache, a Fibonacci-style function still descends through consecutive smaller arguments before any result is available. It can hit the configured recursion limit despite doing only linearly many distinct computations.

Use `sys.getrecursionlimit()` to inspect that limit. Raising it is not a substitute for a space analysis and can be unsafe for some interpreter and C-extension call paths. Python does not eliminate recursive Python tail calls. A bottom-up loop avoids the recursive chain; retaining only the previous two values also avoids a full answer cache. Their growing bit lengths remain a separate cost.

## Key takeaways
- Count simultaneously live frames and retained data.
- Exponential call counts can coexist with linear stack depth.
- A bottom-up loop can remove a cold recursive descent that caching preserves.

## Further reading
- [Python recursion limits](https://docs.python.org/3.14/library/sys.html)
- [Python caching tools](https://docs.python.org/3.14/library/functools.html)
