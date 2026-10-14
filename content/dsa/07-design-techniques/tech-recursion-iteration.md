---
id: tech-recursion-iteration
title: Turning recursion into iteration
level: basic
minutes: 2
sourceLesson: tech-recursion
summary: Self tail calls become parameter updates in a loop.
---

## Converting recursion to iteration

### Tail recursion becomes a loop

A tail-recursive function maps directly onto a `while` loop: the parameters become variables, and the tail call becomes reassignment.

```python
def fact_iter(n):
    # Reject inputs outside the stated
    # domain.
    if type(n) is not int or n < 0:
        raise ValueError("nonnegative n")
    acc = 1
    while n > 1:     # not yet base case
        # Both new values use the old
        # parameters.
        n, acc = n - 1, acc * n
    return acc
```

### General recursion needs an explicit stack

When there are several recursive calls or work after the call, replace the call stack with your own list. This pre-order traversal avoids the interpreter recursion limit; its maximum usable input is still constrained by memory and execution time:

```python
def preorder(root):
    out, stack = [], [root]
    while stack:
        # Resume the most recently queued
        # subtree.
        node = stack.pop()
        # An empty subtree contributes no
        # nodes.
        if node is None:
            continue
        # Record the parent before its
        # children.
        out.append(node.val)
        # push right first so left
        # is popped (visited) first
        stack.append(node.right)
        stack.append(node.left)
    return out
```

A Python list stores pending work in dynamically allocated memory. General simulations can retain a resume point or a visited flag; specialised traversals sometimes need fewer entries. This routine also stores O(n) output. Here depth is the maximum nesting of pending work. The following table counts control-stack entries, assuming constant-sized entries; it excludes retained data and output.

| Approach | Stack space | Clarity |
|---|---|---|
| Plain recursion | O(depth), capped | High |
| Tail rec. + TCO | O(1) | High |
| Loop replacing self tail calls | O(1) | Medium |
| Explicit stack | O(depth), heap | Lower |

## Key takeaways
- Self tail calls become parameter updates in a loop.
- General recursion needs explicit pending work; push right before left to reproduce pre-order.

## Further reading
- [Recursive algorithms — Erickson](https://jeffe.cs.illinois.edu/teaching/algorithms/book/01-recursion.pdf)
- [Python recursion allowance](https://docs.python.org/3/library/sys.html)
