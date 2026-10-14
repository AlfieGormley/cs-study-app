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

In the worst case (no duplicates), how many comparisons? Here n is the number of items in the list, and `i` and `j` are the two positions being compared. When `i = 0`, the inner loop runs n − 1 times; when `i = 1`, n − 2 times; and so on down to 0. Adding these up:

```formula
C(n) = (n − 1) + (n − 2) + … + 1 + 0
C(n) = n × (n − 1) / 2
C(5) = 5 × 4 / 2 = 10
C(1000) = 1000 × 999 / 2 = 499500
where
C(n): the number of comparisons has_dup makes in the worst case (no duplicates), on a list of n items
n: the number of items in the list; a whole number with no unit
…: "and so on": the terms keep falling by 1 until they reach 0
In words: every pair of different positions is compared exactly once, and a list of n items has n × (n − 1) / 2 pairs.
```

Where does the second line come from? Write the sum forwards and then backwards underneath it. Each column adds up to n − 1, and there are n columns, so twice the sum is n × (n − 1). Halve it to get the sum itself. Another way to see it: each of the n items is paired with the n − 1 others, and that counts every pair twice.

So for 5 items that is 10 comparisons, for 1,000 items 499,500, and for 1,000,000 items about 500 billion (1,000,000 × 999,999 / 2 ≈ 5 × 10^11). Doubling n roughly **quadruples** the work, because n appears twice in the product: twice as many items, each compared with twice as many others.

A different approach is to sort the list first and then compare neighbours, since duplicates end up next to each other. Good sorting algorithms take about n × log_2(n) operations ("n log n", where log_2 is the base-2 logarithm, explained in the following growth-rate lesson; later modules show how). Another is to put each item in a hash set and stop if it is already there, which is about n operations on average. Same problem, three very different growth rates.

## Key takeaways
- Compare each pair of distinct positions once.
- An early return helps some inputs; the no-duplicate input performs the full scan.
- Doubling the list approximately quadruples the pair count.

## Further reading
- [Analysis of algorithms — Wikipedia](https://en.wikipedia.org/wiki/Analysis_of_algorithms)
- [Time complexity — Wikipedia](https://en.wikipedia.org/wiki/Time_complexity)
