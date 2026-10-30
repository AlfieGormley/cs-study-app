---
id: sort-insertion-shifts
title: Insertion sort and existing order
level: basic
minutes: 4
sourceLesson: sort-simple
summary: Each shift removes an inversion; nearly ordered inputs can be much cheaper.
---

This unit builds on the preceding sorting units. Here n is the number of input elements; Big O bounds growth up to a constant factor, and logarithms are base two unless stated otherwise.

## Insertion sort

Keep a sorted prefix. Take the next element and slide it left until it sits in the right place, like sorting a hand of cards.

```python
def insertion_sort(a):
    for i in range(1, len(a)):
        # Save this item before shifting
        # others.
        key = a[i]
        j = i - 1
        # Shift only keys strictly larger.
        while j >= 0 and a[j] > key:
            a[j + 1] = a[j]   # shift right
            j -= 1
        # Insert in the gap left by the
        # shifts.
        a[j + 1] = key
```

Trace on `[5, 2, 4, 6, 1, 3]` (the bar marks the end of the sorted prefix):

```
start     [5 | 2, 4, 6, 1, 3]
key 2     [2, 5 | 4, 6, 1, 3]   1 shift
key 4     [2, 4, 5 | 6, 1, 3]   1 shift
key 6     [2, 4, 5, 6 | 1, 3]   0 shifts
key 1     [1, 2, 4, 5, 6 | 3]   4 shifts
key 3     [1, 2, 3, 4, 5, 6]    3 shifts
```

Total shifts: 9, which is exactly the number of inversions in the input. That is the key insight:

> [!note] Insertion sort is O(n + inversions)
> Each shift removes one inversion, and each element costs at most one extra comparison to stop. So the running time grows with the number of elements plus the number of inversions.

```formula essential
T = Θ(n + I)
where
T: the running time of insertion sort, counted in comparisons plus shifts
n: the number of elements in the array
I: the number of inversions (out-of-order pairs) in the input
Θ: Big Theta: grows exactly this fast, up to a constant factor
In words: insertion sort pays about one step per element plus one per inversion, so its cost tracks how disordered the input is.
```

Three consequences follow:

- **Sorted input** has no inversions, so insertion sort is linear: one comparison per element.
- **Reversed input** has every pair inverted, so it is quadratic.
- **Nearly sorted input**, where no element starts more than k places from its final position, has at most k inversions per element. The cost is then O(nk), which is linear when k is a small constant.

The bound assumes shifting one place costs constant time, which is true for arrays. It is a growth model, not an exact count of executed instructions.

> [!analogy] Real-world analogy: sorting a hand of cards
> Many card players pick up cards one at a time and slide each new card left past any higher cards until it sits in order. If the cards arrive almost in order, each one barely moves; if they arrive in reverse, every new card travels past all the others.
>
> **How it maps:** the cards already held are the sorted prefix, sliding a card past a higher one is one shift (one inversion removed), and stopping at the first card that is not higher keeps equal cards in arrival order, which is stability.
>
> **Where it stops:** in your hand, the other cards make room for free. In an array, every element the key passes must be copied one slot right, so a long slide costs one write per position; that is why reversed input is quadratic.

Insertion sort is:

- **Stable**, because it stops at the first element that is not strictly greater (`a[j] > key`).
- **Adaptive**, in the strong sense above.
- **Online algorithm**: you can feed it elements one at a time and the prefix is always sorted.
- **Fast for small n**. Its inner loop is a tight compare-and-shift with sequential memory access and no recursion. At small ranges (often thresholds of tens of elements) it can beat merge sort and quicksort, whose overheads (function calls, extra buffers, pivot selection) dominate at that size.

A variant, **binary insertion sort**, finds the insertion point with binary search. That cuts comparisons to O(n log n), but shifting is still O(n²). It pays off when comparisons are expensive, which is why CPython uses it to build short runs in its list sort.

## Key takeaways
- Each shift removes an inversion; nearly ordered inputs can be much cheaper.
- Strictly greater comparisons preserve stability and the sorted prefix supports online insertion.

## Further reading
- [Elementary sorts — Princeton Algorithms](https://algs4.cs.princeton.edu/21elementary/)
