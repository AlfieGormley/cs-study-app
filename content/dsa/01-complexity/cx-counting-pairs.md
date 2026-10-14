---
id: cx-counting-pairs
sourceLesson: cx-growth-rates
title: Comparing every pair
level: basic
minutes: 3
summary: Count the comparisons in a duplicate check that visits each distinct pair once.
---

The pairwise duplicate check shows why a small change in input length can create a large change in work. Here n is the number of list items.

## Counting pairs

Now a function that checks whether a list contains a duplicate by comparing every pair:

```python
# has_dup([2, 3, 2]) returns True.
def has_dup(xs):
    n = len(xs)
    for i in range(n):
        # Later positions: each pair once.
        for j in range(i + 1, n):
            if xs[i] == xs[j]:
                return True
    return False
```

In the worst case (no duplicates), how many comparisons? Here n is the item count; `i` and `j` are positions in the code. The first outer pass compares with every later position, the second skips one more position, and the final pass has no later positions. The series below records those shrinking counts.

```formula
C(n) = (n − 1) + (n − 2) + … + 1 + 0
C(n) = n(n − 1) / 2
C(5) = 5 × 4 / 2 = 10
C(1000) = 1000 × 999 / 2 = 499500
C(1000000) = 1000000 × 999999 / 2
C(1000000) = 499999500000
where
C(n): the number of comparisons has_dup makes in the worst case (no duplicates), on a list of n items
n: the number of items in the list; a whole number with no unit
…: "and so on": the terms keep falling by 1 until they reach 0
In words: every pair of different positions is compared exactly once, and a list of n items has n × (n − 1) / 2 pairs.
```

Where does the second line come from? Write the series forwards and backwards underneath itself. Each column totals one less than the item count, and there is one column per item. That counts every pair twice, so halve the product. Equivalently, pair every item with every other item and remove that same double count.

So for 5 items that is 10 comparisons, for 1,000 items 499,500, and for a million items about 500 billion, as the card shows. Doubling the list roughly **quadruples** the work: twice as many items, each compared with twice as many others.

A different approach sorts first and compares neighbours, since duplicates become adjacent. Good sorting algorithms take O(n log n) time, where n is the item count and log is the base-2 logarithm introduced next. A hash set gives O(n) expected time under the usual hashing assumptions. Same problem, three different growth rates.

## Key takeaways
- Compare each pair of distinct positions once.
- An early return helps some inputs; the no-duplicate input performs the full scan.
- Doubling the list approximately quadruples the pair count.

## Further reading
- [Analysis of algorithms — Wikipedia](https://en.wikipedia.org/wiki/Analysis_of_algorithms)
- [Time complexity — Wikipedia](https://en.wikipedia.org/wiki/Time_complexity)
