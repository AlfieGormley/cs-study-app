---
id: sort-bubble-passes
title: Bubble sort and early exit
level: basic
minutes: 3
sourceLesson: sort-simple
summary: A pass fixes the largest remaining element at the right.
---

This unit builds on the preceding sorting units. Here n is the number of input elements; Big O bounds growth up to a constant factor, and logarithms are base two unless stated otherwise.

## Bubble sort

Repeatedly walk the array, swapping neighbours that are out of order. After the first pass the largest element has "bubbled" to the end; after the second pass the last two positions are final, and so on.

```python
def bubble_sort(a):
    n = len(a)
    # The sorted suffix grows each pass.
    for end in range(n - 1, 0, -1):
        # A swap-free pass proves
        # sortedness.
        swapped = False
        for i in range(end):
            # Strict comparison preserves
            # equal keys.
            if a[i] > a[i + 1]:
                a[i], a[i+1] = a[i+1], a[i]
                swapped = True
        if not swapped:
            break   # no swaps: sorted
```

Each pass compares neighbours across the unsorted part, which is one element shorter each time. Without an early exit, the comparisons add up to:

```formula
C = (n − 1) + (n − 2) + … + 1
C = (n(n − 1)) / 2
C = 10 × 9 / 2 = 45
where
C: the number of comparisons bubble sort makes when every pass runs
n: the number of elements in the array; here 10
…: "and so on": each term is one less than the one before, down to 1
In words: the first pass makes n − 1 comparisons, the next one fewer, and the total of that shrinking series is n × (n − 1) / 2.
```

- Comparisons: up to that total, 45 for 10 elements. With the `swapped` flag, a sorted input finishes after one pass of one comparison per adjacent input pair (9 for 10 elements), so it is adaptive in the best case.
- Swaps: exactly the number of inversions.
- Stable, because it only swaps when strictly greater (`>`). Change that to `>=` and equal elements leapfrog each other: no longer stable.

Bubble sort has an asymmetry. A large element near the start (a "rabbit") races to the end in one pass. A small element near the end (a "turtle") moves only one position left per pass.

```
[2, 3, 4, 5, 1]   1 is a turtle
pass 1: [2, 3, 4, 1, 5]
pass 2: [2, 3, 1, 4, 5]
pass 3: [2, 1, 3, 4, 5]
pass 4: [1, 2, 3, 4, 5]
```

Four passes to move one element. Cocktail shaker sort (alternating direction) helps with turtles, but it is still O(n²).

## Key takeaways
- A pass fixes the largest remaining element at the right.
- A swap-free pass proves the array is sorted; small trailing values still move slowly left.

## Further reading
- [Elementary sorts — Princeton Algorithms](https://algs4.cs.princeton.edu/21elementary/)
