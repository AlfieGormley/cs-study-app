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

The scan for the minimum always covers the whole unsorted part, so the counts never depend on the input: about half of n squared comparisons (124,750 for 500 elements), but at most one swap per position (499 for 500 elements).

```formula reference
C = (n(n − 1)) / 2
S ≤ n − 1
where
C: the number of comparisons selection sort makes, on every input of n elements
S: the number of swaps it makes, at most one per position
n: the number of elements in the array
≤: less than or equal to
In words: selection sort always makes about half of n squared comparisons, but never more than one swap per position.
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

> [!analogy] Real-world analogy: lining up heavy boxes by their labels
> You must line up crates in weight order, and each crate's weight is printed on its label. Reading a label is easy; carrying a crate is hard work. So you read every remaining label to find the lightest, then make one carry to put it in the next spot.
>
> **How it maps:** reading labels is comparing keys, carrying a crate is writing to the array, and "find the lightest, then one carry" is selection sort's full scan followed by one swap per position.
>
> **Where it stops:** you might notice two crates already in the right place and skip work, but selection sort still scans the whole remaining row every time, so its comparison count never drops. The single swap is also what breaks stability: a carried crate can jump over an equal-weight crate.

## Key takeaways
- Minimum scans always make the same comparison count.
- Long-distance swaps save data movement but can reverse equal-key records.

## Further reading
- [Elementary sorts — Princeton Algorithms](https://algs4.cs.princeton.edu/21elementary/)
