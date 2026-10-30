---
id: sort-selection-extreme-ranks
title: Selection ranks and tournament minima
level: advanced
minutes: 3
sourceLesson: sort-selection
summary: Selection asks for ranks rather than an entirely sorted array.
---

Many questions that sound like sorting are really selection problems, answered by a **selection algorithm**: find the median latency, the 99th percentile, the 10 highest-scoring posts, the k nearest points. You need one element (or k elements) in the right place, not the whole array ordered.

Sorting answers all of these in O(n log n). But selection can be done in **O(n)**, and top-k in **O(n log(k + 1))**. At a billion items, the base-two logarithm of the input size is about thirty; this compares asymptotic growth, not literal pass counts or measured runtime.

Throughout, n is the number of elements, costs use Big O notation (how a cost grows with n, ignoring constant factors), and "k-th smallest" is 0-based: rank zero is the minimum, the last rank is the maximum, and the integer-divided halfway index is the upper middle value for even-length inputs. The numeric median of an even sample conventionally averages its two central values.

## The easy cases

- **Minimum or maximum**: one pass, one fewer comparison than the number of items. That is optimal: every element except the winner must lose at least one comparison.
- **Min and max together**: compare elements in pairs, then the smaller with the current min and the larger with the current max. That is about one and a half comparisons per element instead of two.
- **Second smallest**: a knockout tournament finds it with only a few extra comparisons. The runner-up must have lost directly to the winner, and the winner played only about a logarithmic number of matches, so a second small contest among the players the winner beat finds it.

```formula reference
C_min = n − 1
C_mm ≈ 3n / 2
C_2 ≤ n + ⌈log_2(n)⌉ − 2
where
C_min: the comparisons needed to find the minimum (or the maximum) alone
C_mm: the comparisons needed to find the minimum and maximum together, using pairs
C_2: the comparisons a balanced knockout tournament uses to find the second smallest, for at least two distinct items; the displayed upper bound is exact when n is a power of two
n: the number of elements
log_2(n): the base-2 logarithm of n: the number of rounds in a knockout tournament of n players (10 for 1,024)
⌈ ⌉: the ceiling: round up to the next whole number
≈: approximately equal to
≤: less than or equal to
In words: the minimum needs one comparison per loser; doing min and max together saves about a quarter; the runner-up costs only about as many extra comparisons as the winner played matches.
```

For 1,024 elements: 1,023 comparisons for the minimum, about 1,536 for min and max together instead of 2,046 separately, and 1,032 for the second smallest.

The general k is where it gets interesting.

## Key takeaways
- Selection asks for ranks rather than an entirely sorted array.
- Tournament losers prove minimum and second-minimum comparison costs.

## Further reading
- [Heap operations and top-k — Python heapq](https://docs.python.org/3/library/heapq.html)
