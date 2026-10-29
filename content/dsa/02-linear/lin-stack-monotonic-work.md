---
id: lin-stack-monotonic-work
title: Monotonic stacks and total-work counting
level: intermediate
minutes: 3
sourceLesson: lin-stacks
summary: Unresolved indices wait until a later value supplies their answer.
---

The preceding stack units used last-in, first-out storage. Here the stack additionally keeps unresolved candidates in nonincreasing value order. In every bound n is the number of input values; equal values may remain together because only a strictly larger value answers the query.

## The monotonic stack

A **monotonic stack** keeps its contents in sorted order (all increasing or all decreasing) by popping anything that would break the order before each push. It solves "for each element, find the nearest element to the left or right that is bigger (or smaller)" in O(n).

**Next greater element:** for each value, find the first larger value to its right.

```python
def next_greater(nums):
    res = [-1] * len(nums)
    stack = []  # indices; values decrease
    for i, x in enumerate(nums):
        while stack and nums[stack[-1]] < x:
            # This waiting index has found
            # its answer.
            res[stack.pop()] = x
        # The new index now waits for a
        # larger one.
        stack.append(i)
    return res

next_greater([2, 1, 2, 4, 3])
# [4, 2, 4, -1, -1]
```

The stack holds indices still **waiting** for a bigger value. When `x` arrives, every waiting element smaller than `x` has found its answer and is popped.

There's a `while` inside a `for`, but for n input values it's still **O(n)**. Instead of asking how long one `while` loop can run, count the work over the whole run: every index is pushed exactly once, can be popped at most once, and each pass of the `for` loop ends its `while` loop with one failed check.

```formula reference
events = pushes + pops + exits
events ≤ n + n + n = 3n
where
events: counted push events, pop events and final failed while checks; a successful while check is charged together with its ensuing pop, not counted separately
n: the number of input values
pushes: exactly n, one per index
pops: at most n, because each index can be popped only once after being pushed once
exits: exactly n: each pass of the for loop ends its while loop once, when the check fails
≤: is less than or equal to
In words: however the pops are spread out, the whole run does at most three counted events per input value, each taking fixed work, so the total is linear. This is a counting bound, not an exact count of Python instructions.
```

One step can pop many items, but then other steps pop none: for `[2, 1, 2, 4, 3]` the 4 pops two waiting indices at once, while three of the five steps pop nothing. This is an **amortised** argument, like dynamic array growth.

The same pattern answers "how many days until a warmer temperature", stock span problems and the largest rectangle in a histogram.

## Other uses

- **Undo** in editors: push each action; undo pops it. Redo is a second stack.
- **Browser back button:** a stack of visited pages.
- **Backtracking** (maze solving, Sudoku): push choices, pop to retreat.
- **Parsers:** compilers use a stack to track nested constructs.

## Key takeaways
- Unresolved indices wait until a later value supplies their answer.
- Count pushes and pops over the complete run rather than multiplying the inner and outer loop bounds.

## Further reading
- [Stack (abstract data type) — Wikipedia](https://en.wikipedia.org/wiki/Stack_(abstract_data_type))
