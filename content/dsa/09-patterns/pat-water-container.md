---
id: pat-water-container
title: Prove the shorter-line container move
level: basic
minutes: 4
sourceLesson: pat-two-pointers
summary: A container is limited by its shorter endpoint and the distance between endpoints.
---

Here n is the number of nonnegative heights. The input need not be sorted: the move rule follows from a bound on all pairs involving one endpoint.

## Opposite ends: container with most water

**Problem.** `h[i]` is a nonnegative height of a vertical line at position `i`. Choose two lines that, with the x-axis, hold the most water. The water a pair of lines can hold is limited by the shorter line:

```formula
A = (j − i) min(h[i], h[j])
where
A: the area of water held between lines i and j, in square units (width × height)
i: the position (index) of the left line, counting from 0
j: the position of the right line, with j > i
h[i]: the height of the line at position i
min: the smaller of its two inputs, so min(8, 7) = 7
In words: the container is as wide as the distance between the lines and as tall as the shorter line; water above the shorter line would spill over it.
```

The formula assumes the lines are thin and the water's surface is flat, so only the shorter line matters; it holds for any nonnegative heights.

The array isn't sorted, so why do two pointers work? Start with the widest container (`lo = 0`, `hi = n - 1`). Suppose `h[lo] < h[hi]`. Any other container using `lo` with a partner inside the range:

- is **narrower** (the partner is closer), and
- has height at most `h[lo]` (the shorter line caps it).

So it can never beat the current one. Every pair involving `lo` is discarded in one move: advance `lo`. Move the **shorter** line; if heights tie, either endpoint can be discarded. For fewer than two lines, the code returns 0.

```python
def max_area(h):
    lo, hi = 0, len(h) - 1
    best = 0
    while lo < hi:
        width = hi - lo
        area = width * min(h[lo], h[hi])
        # Keep the largest candidate area
        # seen.
        best = max(best, area)
        if h[lo] < h[hi]:
            lo += 1
        else:
            hi -= 1
    return best
```

For `[1, 8, 6, 2, 5, 4, 8, 3, 7]` the answer is 49, from the lines at positions 1 and 8:

```formula
A = (j − i) min(h[i], h[j])
A = (8 − 1) × min(8, 7)
A = 7 × 7 = 49
where
A: the area of water held, in square units
i: the left line's position; here 1
j: the right line's position; here 8
h[i]: the height at position i; here h[1] = 8 and h[8] = 7
min: the smaller of its two inputs
In words: the best pair is 7 positions apart and 7 tall (the shorter of 8 and 7), giving 49.
```

> [!note] The proof is the pattern
> Two pointers are only correct when you can argue that the move discards nothing useful. If you can't say *why* a move is safe, you don't yet have a two-pointer solution; you have a guess.

## Key takeaways
- A container is limited by its shorter endpoint and the distance between endpoints.
- Discarding the shorter endpoint cannot remove an improvement inside the current range.
- Equal heights allow either endpoint to move; fewer than two lines give zero area.

## Further reading
- [Two pointers — USACO Guide](https://usaco.guide/silver/two-pointers)
- [Dutch national flag problem — Wikipedia](https://en.wikipedia.org/wiki/Dutch_national_flag_problem)
- [Array cheatsheet — Tech Interview Handbook](https://www.techinterviewhandbook.org/algorithms/array/)
