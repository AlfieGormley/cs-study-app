---
id: pat-next-greater-stack
title: Answer waiting indices with the next greater value
level: advanced
minutes: 3
sourceLesson: pat-monotonic
summary: Keep indices of unanswered positions with non-increasing values.
---

A **monotonic stack** is an ordinary stack with one rule: its contents stay sorted (all increasing or all decreasing from bottom to top). Before pushing a new element, you pop everything that would break the order.

The magic is in the pops. In the left-to-right next-element scan, a pop can identify the first later value satisfying the chosen strict or non-strict comparison. Other scan directions and previous-element variants use different invariants. Questions of the form "for each element, find the nearest element to the left/right that is greater/smaller" all fall to this.

Each element is pushed once and popped no more than once, so the whole scan of n elements is **O(n)**, even though there's a `while` inside the `for`.

## Next greater element

**Problem.** For each element, find the first element to its right that is strictly greater, or −1 if none.

Brute force scans right from every element: O(n²). Instead, keep a stack of indices that are still **waiting** for their next greater element. Their values are non-increasing from bottom to top (if a smaller one sat under a bigger one, the bigger one would already have answered it).

```python
def next_greater(a):
    res = [-1] * len(a)
    stack = []   # non-increasing values
    for i, x in enumerate(a):
        while stack and a[stack[-1]] < x:
            # Answer the waiting position,
            # not its value.
            res[stack.pop()] = x
        stack.append(i)
    return res
```

Trace for `a = [2, 1, 2, 4, 3]`:

```
i x  pops (answer)     stack after
0 2  -                 [2]
1 1  -                 [2,1]
2 2  1 -> 2            [2,2]
3 4  2 -> 4, 2 -> 4    [4]
4 3  -                 [4,3]
end: 4 and 3 stay -1
result: [4, 2, 4, -1, -1]
```

(The stack holds indices; values are shown for readability.)

Note `a[2] = 2` doesn't pop `a[0] = 2`: the problem says *strictly* greater, so the comparison is `<`. Using `<=` would answer "next greater or equal". Getting this right matters a lot with duplicates.

## Key takeaways
- Keep indices of unanswered positions with non-increasing values.
- A strictly larger arrival answers all smaller waiting values on top.
- Use a deliberate strict or non-strict comparison for duplicates.

## Further reading
- [All nearest smaller values — Wikipedia](https://en.wikipedia.org/wiki/All_nearest_smaller_values)
- [Minimum stack / minimum queue — cp-algorithms](https://cp-algorithms.com/data_structures/stack_queue_modification.html)
- [Sliding window — USACO Guide](https://usaco.guide/gold/sliding-window)
- [Amortized analysis — Wikipedia](https://en.wikipedia.org/wiki/Amortized_analysis)
