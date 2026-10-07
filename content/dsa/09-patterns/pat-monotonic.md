---
id: pat-monotonic
title: Monotonic stacks and queues
level: advanced
minutes: 14
summary: Keeping a stack or deque in sorted order so each element is pushed and popped once, giving O(n) solutions to next greater element, largest rectangle in a histogram and sliding window maximum.
---

A **monotonic stack** is an ordinary stack with one rule: its contents stay sorted (all increasing or all decreasing from bottom to top). Before pushing a new element, you pop everything that would break the order.

The magic is in the pops. In the left-to-right next-element scan, a pop can identify the first later value satisfying the chosen strict or non-strict comparison. Other scan directions and previous-element variants use different invariants. Questions of the form "for each element, find the nearest element to the left/right that is greater/smaller" all fall to this.

Each element is pushed once and popped at most once, so the whole scan is **O(n)**, even though there's a `while` inside the `for`.

## Next greater element

**Problem.** For each element, find the first element to its right that is strictly greater, or −1 if none.

Brute force scans right from every element: O(n²). Instead, keep a stack of indices that are still **waiting** for their next greater element. Their values are non-increasing from bottom to top (if a smaller one sat under a bigger one, the bigger one would already have answered it).

```python
def next_greater(a):
    res = [-1] * len(a)
    stack = []   # non-increasing values
    for i, x in enumerate(a):
        while stack and a[stack[-1]] < x:
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

### The four variants

| Want | Scan | Pop while top is |
|---|---|---|
| Next greater (right) | L→R | `< x` |
| Next smaller (right) | L→R | `> x` |
| Previous greater | L→R | `<= x`, then top |
| Previous smaller | L→R | `>= x`, then top |

For "previous" variants, the answer for `x` is whatever is left on top of the stack *after* popping (or none if empty).

**Circular arrays** (the element after the last is the first): loop `i` over `range(2 * n)` and use `a[i % n]`, only pushing during the first pass.

**Daily temperatures** ("how many days until a warmer day?") is the same algorithm storing `i - j` instead of the value. **Stock span** is the previous-greater variant.

## Largest rectangle in a histogram

**Problem.** Bars of width 1 have heights `h`. Find the area of the largest rectangle that fits under the histogram.

For `h = [2, 1, 5, 6, 2, 3]` the answer is 10: height 5 across the bars of height 5 and 6.

```
        #
      # #
      # #
      # #   #
  #   # # # #
  # # # # # #
  2 1 5 6 2 3
      [===]  5 x 2 = 10
```

**Insight.** The best rectangle uses some bar `i` as its *shortest* bar, and then extends as far as possible on both sides: until the previous smaller bar on the left and the next smaller bar on the right. So for each bar:

```
width = next_smaller(i)
        - prev_smaller(i) - 1
area  = h[i] * width
```

The code below uses strictly increasing stack heights and pops on `>=`. Its left boundary is the previous strictly smaller bar; its right boundary is the first smaller-or-equal bar (or the end sentinel). An equal bar therefore takes ownership of a span from an earlier equal bar. This asymmetric tie rule still measures a maximum-area representative for every possible height.

```python
def largest_rect(h):
    if any(type(x) is not int or x < 0
           for x in h):
        raise ValueError("bad heights")
    stack = []   # indices, heights rise
    best = 0
    for i in range(len(h) + 1):
        cur = h[i] if i < len(h) else 0
        while stack and h[stack[-1]] >= cur:
            top = stack.pop()
            left = stack[-1] if stack \
                else -1
            width = i - left - 1
            best = max(best, h[top] * width)
        stack.append(i)
    return best
```

The **sentinel** height 0 at `i = n` flushes every remaining bar off the stack so they all get measured.

Trace the key moment, at `i = 4` (height 2), with stack holding indices `[1, 2, 3]` (heights 1, 5, 6):

```
pop 3 (h=6): left=2  width=4-2-1=1  area 6
pop 2 (h=5): left=1  width=4-1-1=2  area 10
h[1]=1 < 2: stop, push 4
```

O(n) time, O(n) space. It's also the core of **maximal rectangle in a binary matrix**: treat each row as the base of a histogram of consecutive 1s above, and run this per row for O(R·C).

> [!note] `>=` versus `>` here
> With equal heights, popping on `>=` means an earlier equal bar is measured with a too-short right boundary. That's fine: the last equal bar in the run gets the full width, so the maximum is still correct.

## Monotonic deque: sliding window maximum

**Problem.** Return the maximum of every window of size `k`.

A heap with only lazy deletion of expired roots can retain O(n) entries and take O(n log n). A bounded indexed heap or periodic rebuilding can instead give O(n log(k + 1)). A **monotonic deque** gives O(n).

Keep indices in a deque whose values are **decreasing** from front to back. The front is always the current window's maximum.

- **Push at the back:** before adding `i`, pop smaller-or-equal values from the back. They need not represent any future maximum: `a[i]` is at least as large and expires later. Equal maxima are interchangeable when returning only values.
- **Expire at the front:** if the front index has slid out of the window, pop it.

```python
from collections import deque

def window_max(a, k):
    if (type(k) is not int
            or not 1 <= k <= len(a)):
        raise ValueError("1 <= k <= len(a)")
    dq = deque()  # values decrease
    out = []
    for i, x in enumerate(a):
        while dq and a[dq[-1]] <= x:
            dq.pop()
        dq.append(i)
        if dq[0] <= i - k:
            dq.popleft()
        if i >= k - 1:
            out.append(a[dq[0]])
    return out
```

```
a = [1, 3, -1, -3, 5, 3, 6, 7], k = 3

i  x   deque (values)   out
0  1   [1]
1  3   [3]
2  -1  [3,-1]           3
3  -3  [3,-1,-3]        3
4  5   [5]              5
5  3   [5,3]            5
6  6   [6]              6
7  7   [7]              7
```

Result `[3, 3, 5, 5, 6, 7]`. Each index enters and leaves the deque once: O(n) time, O(k) auxiliary space, plus O(n − k + 1) output space.

The same structure powers DP optimisations where `dp[i]` depends on the max or min of `dp` over a sliding range (for example "jump game VI"). A related dominance argument solves "shortest subarray with sum at least k" with negative values, using a deque of increasing prefix sums; that is not simply the same fixed-range DP recurrence.

## Why it's O(n): the amortised argument

Count operations per element rather than per loop iteration:

- each index is pushed exactly once: n pushes;
- each index is popped at most once: at most n pops.

So there are at most 2n pushes and pops; loop tests, comparisons and output writes add O(n) more work. A single step may pop many elements, but then those elements are gone and can't be popped again.

## Recognising the pattern

| Cue | Structure |
|---|---|
| "next/previous greater/smaller" | Monotonic stack |
| "days until warmer", "span" | Monotonic stack |
| Area bounded by shortest bar | Increasing stack |
| Max/min of each window | Monotonic deque |
| DP over a sliding max/min | Monotonic deque |
| Remove k digits for smallest | Increasing stack (greedy) |

## Pitfalls

- **Storing values instead of indices.** You usually need the index for widths, distances or window expiry. Store indices; look values up.
- **Strict vs non-strict comparisons.** Decide what duplicates should do and pick `<` or `<=` deliberately.
- **Forgetting leftovers.** Elements still on the stack at the end have no next greater; use a sentinel or a final pass.
- **Expiry check in the deque.** Compare the front index with `i - k`, not the value with anything.

## Key takeaways
- A monotonic stack keeps elements sorted; each pop reveals a "next greater/smaller" relationship.
- Every element is pushed and popped at most once, so the scan is O(n) amortised.
- Largest rectangle uses smaller-height boundaries; the code assigns equal heights asymmetrically (previous strictly smaller, next smaller-or-equal) to cover their full span.
- A monotonic deque gives the max or min of every sliding window in O(n), beating a heap's O(n log n).
- Store indices, choose strict or non-strict comparisons deliberately, and flush leftovers.

## Further reading
- [All nearest smaller values — Wikipedia](https://en.wikipedia.org/wiki/All_nearest_smaller_values)
- [Minimum stack / minimum queue — cp-algorithms](https://cp-algorithms.com/data_structures/stack_queue_modification.html)
- [Sliding window — USACO Guide](https://usaco.guide/gold/sliding-window)
- [Amortized analysis — Wikipedia](https://en.wikipedia.org/wiki/Amortized_analysis)
