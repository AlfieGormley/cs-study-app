---
id: pat-histogram-span
title: Measure histogram rectangles at pop time
level: advanced
minutes: 5
sourceLesson: pat-monotonic
summary: Rectangle widths come from limiting bars on both sides.
---

Here n is the number of nonnegative integer bar heights, each bar has width one, and empty input returns zero. Numeric operations are treated as constant-cost.

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

```formula
w_i = R_i − L_i − 1
A_i = h[i]w_i
w_2 = 4 − 1 − 1 = 2
A_2 = 5 × 2 = 10
where
w_i: the width of the widest rectangle in which bar i is the shortest bar, in bars
R_i: the index of the next smaller bar to the right of i (or n, one past the end, if none)
L_i: the index of the previous smaller bar to the left of i (or −1 if none)
A_i: the area of that rectangle, in square units
h[i]: the height of bar i
i: the index of the bar being measured, counting from 0
n: the number of bars
w_2: the width for the bar at index 2 (height 5)
A_2: the area for the bar at index 2
In words: the rectangle stretches over every bar strictly between the two smaller neighbours, so its width is the gap between them minus one; for the bar of height 5 at index 2, the neighbours are at 1 and 4, giving width 2 and area 10.
```

The answer is the largest A_i over all bars. Every rectangle under the histogram has some shortest bar, so checking each bar as "the shortest" covers every candidate.

The code below uses strictly increasing stack heights and pops on `>=`. Its left boundary is the previous strictly smaller bar; its right boundary is the first smaller-or-equal bar (or the end histogram flush sentinel). An equal bar therefore takes ownership of a span from an earlier equal bar. This asymmetric tie rule still measures a maximum-area representative for every possible height.

```python
def largest_rect(h):
    if any(type(x) is not int or x < 0
           for x in h):
        raise ValueError("bad heights")
    stack = []   # indices, heights rise
    best = 0
    for i in range(len(h) + 1):
        # The final zero flushes remaining
        # bars.
        cur = h[i] if i < len(h) else 0
        while stack and h[stack[-1]] >= cur:
            top = stack.pop()
            left = stack[-1] if stack \
                else -1
            # Exclude the two limiting
            # boundaries.
            width = i - left - 1
            best = max(best, h[top] * width)
        stack.append(i)
    return best
```

The **histogram flush sentinel** height 0 at `i = n` flushes every remaining bar off the stack so they all get measured.

Trace the key moment, at `i = 4` (height 2), with stack holding indices `[1, 2, 3]` (heights 1, 5, 6):

```
pop 3 (h=6): left=2  width=4-2-1=1  area 6
pop 2 (h=5): left=1  width=4-1-1=2  area 10
h[1]=1 < 2: stop, push 4
```

O(n) time, O(n) space. It's also the core of **maximal rectangle in a binary matrix**: treat each row as the base of a histogram of consecutive 1s above, and run this per row for O(R × C), where R is the number of rows and C the number of columns.

> [!note] `>=` versus `>` here
> With equal heights, popping on `>=` means an earlier equal bar is measured with a too-short right boundary. That's fine: the last equal bar in the run gets the full width, so the maximum is still correct.

## Key takeaways
- Rectangle widths come from limiting bars on both sides.
- The implementation uses previous strictly smaller and next smaller-or-equal tie ownership.
- A zero histogram flush sentinel flushes remaining bars, and row histograms extend the method to a binary matrix.

## Further reading
- [All nearest smaller values — Wikipedia](https://en.wikipedia.org/wiki/All_nearest_smaller_values)
- [Minimum stack / minimum queue — cp-algorithms](https://cp-algorithms.com/data_structures/stack_queue_modification.html)
- [Sliding window — USACO Guide](https://usaco.guide/gold/sliding-window)
- [Amortized analysis — Wikipedia](https://en.wikipedia.org/wiki/Amortized_analysis)
