---
id: prob-quicksort-runtime-checks
title: Check quicksort runtime and production safeguards
level: advanced
minutes: 3
sourceLesson: prob-algorithms
summary: A sampled comparison count is one draw, rather than proof of the mean.
---

For a fixed input of distinct totally ordered keys, the preceding indicator proof gives about 10,986 comparisons on average at 1,000 elements. An unlucky pivot sequence can still compare every pair. This function counts comparisons rather than returning the sorted array; its random choices determine the count.

```python
import random

def qs(a):
    # Distinct keys with a total order.
    # Count actual pivot comparisons.
    if len(a) <= 1:
        return 0
    # Every element can be the next pivot.
    i = random.randrange(len(a))
    p = a[i]
    lo, hi = [], []
    for j, x in enumerate(a):
        # Skip the pivot itself.
        if j == i:
            continue
        if x < p:
            lo.append(x)
        else:
            hi.append(x)
    # Count this partition and both sides.
    return (len(a) - 1) + qs(lo) + qs(hi)

print(qs(list(range(1000))))
# One run; the mean is about 10,986.
```

A quadratic execution remains possible. The expectation guarantee assumes the input is fixed independently of the random choices and comparisons obey a total order; an adaptive adversary or predictable pivots needs separate analysis. A naive two-way implementation can also be quadratic on equal keys. A related analysis shows **quickselect** (finding an element at a specified rank among n values) runs in expected O(n).

> [!note] What libraries do
> Production sorts hedge further. GCC’s libstdc++ implements `std::sort` with an introsort loop that uses a heap-based fallback at its depth limit. Go's `sort` package switched to pattern-defeating quicksort (pdqsort) in Go 1.19, and Rust's documented current unstable sort uses ipnsort. Python's list sort and Java's object-array sort are stable; implementation details can change by version. These library algorithms have additional safeguards and are not identical to the teaching function above.

## Key takeaways
- A sampled comparison count is one draw, rather than proof of the mean.
- Quadratic pivot sequences remain possible, and duplicate keys need suitable partitioning.
- Production sorts add implementation-specific safeguards.

## Further reading
- [Mathematics for Computer Science — MIT](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-fall-2010/)
