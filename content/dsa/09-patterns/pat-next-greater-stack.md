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

Each element is pushed once and popped no more than once, so the whole scan of n elements is **O(n)**, even though there's a `while` inside the `for`. The Arrays, Lists, Stacks & Queues module's "Monotonic stacks and total-work counting" unit introduces the structure; these units treat it as a pattern to recognise and vary.

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

> [!analogy] Real-world analogy: waiting for someone taller to arrive
> People arrive at a viewing spot one at a time, and each wants to know the height of the first person to arrive after them who is taller. Those still waiting stand one behind another, the most recent arrival last. A newcomer checks the most recent waiter first: if that person is shorter, they have their answer and leave, and the newcomer checks the next most recent. When the newcomer meets someone at least as tall, or nobody is left, the newcomer starts waiting too.
>
> **How it maps:** the people still waiting are the stack of unanswered indices, the most recent waiter is the stack top, the newcomer is `x`, and each person who leaves is a pop that writes `res[...] = x`. No one still waiting is shorter than a later arrival who is also waiting, because that later person would have answered them; that is why the waiting heights never increase from first to last.
>
> **Where it stops:** real people could look around at everyone; the algorithm only ever compares the newcomer with the most recent waiter. Whether an equal height counts as an answer is a choice the code must make explicitly with `<` or `<=`, and people never answered get −1.

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
