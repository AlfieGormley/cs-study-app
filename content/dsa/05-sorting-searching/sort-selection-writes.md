---
id: sort-selection-writes
title: Selection sort and costly writes
level: basic
minutes: 3
sourceLesson: sort-simple
summary: Minimum scans always make the same comparison count.
---

This unit builds on the preceding sorting units. Here n is the number of input elements; Big O bounds growth up to a constant factor, and logarithms are base two unless stated otherwise.

## Selection sort

Find the minimum of the unsorted part and swap it into the next position.

```python
def selection_sort(a):
    n = len(a)
    for i in range(n - 1):
        # Track the smallest remaining key.
        m = i
        # Scan all remaining candidates.
        for j in range(i + 1, n):
            if a[j] < a[m]:
                m = j
        # One long swap fixes this position.
        a[i], a[m] = a[m], a[i]
```

The scan for the minimum always covers the whole unsorted part, so the counts never depend on the input:

```formula
C = (n − 1) + (n − 2) + … + 1
C = (n(n − 1)) / 2
S ≤ n − 1
C = 500 × 499 / 2 = 124750
where
C: the number of comparisons selection sort makes, on every input
S: the number of swaps it makes (one per position, at most)
n: the number of elements in the array; here 500
…: "and so on", down to 1
≤: less than or equal to
In words: selection sort always makes about n²/2 comparisons, but never more than n − 1 swaps.
```

- Comparisons: always exactly that total, whatever the input. It is **not adaptive**: a sorted array costs the same as a reversed one.
- Swaps: at most one fewer than the input size (499 for 500 elements). This is its one virtue. If writes are far more expensive than reads, selection sort has a linear worst-case swap bound, while bubble and insertion can require quadratic data movement. It need not use the fewest writes on every particular input.
- **Not stable** in its usual array form. The long-distance swap can jump an element past its equal twin:

```
[2a, 2b, 1]
i 0: min is 1, swap with 2a
     [1, 2b, 2a]   2a and 2b reversed
```

You can make it stable by shifting instead of swapping (insert the minimum and slide the rest right), but that costs O(n) writes per step and throws away its only advantage.

## Key takeaways
- Minimum scans always make the same comparison count.
- Long-distance swaps save data movement but can reverse equal-key records.

## Further reading
- [Elementary sorts — Princeton Algorithms](https://algs4.cs.princeton.edu/21elementary/)
