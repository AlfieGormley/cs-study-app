---
id: sort-quickselect-one-side
title: Quickselect keeps one partition
level: advanced
minutes: 5
sourceLesson: sort-selection
summary: Only the side containing the requested rank survives.
---

This unit builds on the preceding sorting units. Here n is the number of input elements; Big O bounds growth up to a constant factor, and logarithms are base two unless stated otherwise.

## Quickselect

Hoare's **quickselect** (1961) is quicksort that only recurses into **one side**. Partition around a pivot. The pivot lands at its final index p. If p equals k, done. If k is smaller than p, the answer is on the left; otherwise it is on the right. Throw the other side away.

```python
import random

def quickselect(a, k):
    if not 0 <= k < len(a):
        raise IndexError(
            "rank out of range"
        )
    lo, hi = 0, len(a) - 1
    while True:
        if lo == hi:
            return a[lo]
        # Uniform pivot choice gives
        # expectation.
        r = random.randint(lo, hi)
        a[r], a[hi] = a[hi], a[r]
        # Partition before choosing the next
        # range.
        p = lomuto(a, lo, hi)
        # The desired global index is now
        # fixed.
        if k == p:
            return a[p]
        # Only retain the side with the
        # wanted rank.
        if k < p:
            # Discard the pivot and its
            # right side.
            hi = p - 1
        else:
            # Discard the pivot and its left
            # side.
            lo = p + 1
```

(`lomuto` is the partition from the quicksort lesson.) This compact version has the expected linear guarantee for distinct keys. With duplicates, random pivots alone do not prevent quadratic time on all-equal input; use a three-way partition and discard the entire equal block for a duplicate-robust version. Because only one side survives, recursion becomes a loop.

Trace with the last element as pivot (no randomisation, to keep it readable), finding k = 5 in `[7, 2, 1, 6, 8, 5, 3, 4]`:

```
pivot 4: [2,1,3,4,8,5,7,6]  p 3
k=5 > 3: keep a[4..7] = [8,5,7,6]
pivot 6: [5,6,7,8]          p 5
k == p: answer 6
```

Check: sorted, the array is `[1, 2, 3, 4, 5, 6, 7, 8]` and index 5 is 6.

> [!analogy] Real-world analogy: finding the 10th-cheapest flat
> You want the 10th-cheapest flat from 200 listings. Pick one listing as a reference and split the rest into a cheaper pile and a pricier pile. If the cheaper pile holds 25 listings, the 10th-cheapest must be in it, so you never look at the pricier pile again. Repeat with a new reference inside the pile you kept.
>
> **How it maps:** the reference listing is the pivot, splitting into piles is the partition, and keeping only the pile that contains the wanted position is quickselect discarding one side. Nobody ever puts the piles in full price order, which is the saving over sorting.
>
> **Where it stops:** a person would pick a reference that looks typically priced. Quickselect picks blindly (at random), so an unlucky pick can be the cheapest or dearest listing and remove only itself; a long run of such picks is what makes the worst case quadratic.

### Why it is expected O(n)

With a good pivot, each round discards a constant fraction. If every pivot split the array in half, the work would be a **geometric series** (each term a fixed fraction of the one before):

```formula essential
W = n + n / 2 + n / 4 + … ≤ 2n
where
W: the total number of elements partitioned over all rounds
n: the number of elements
…: "and so on", each term half the one before
≤: less than or equal to
In words: halving the work every round adds up to less than twice the first round's work, so the total is linear.
```

So the total is linear. For distinct keys, with random pivots the splits are not exactly half, but the pivot lands in the middle 50% of the range with probability 1/2, and then at least a quarter is discarded. The expected cost is still a geometric series: **O(n)**. A more careful analysis puts the expected cost of finding the median at about 3.4 comparisons per element, and less for ranks near either end:

```formula reference
C ≈ 2(1 + ln(2))n
C ≈ 3.39n
where
C: the expected comparisons randomised quickselect makes to find the median of n distinct keys
n: the number of elements
ln(2): the natural logarithm of 2 (base e, about 2.718), about 0.693
≈: approximately equal to (leading term)
In words: finding the median with random pivots takes about 3.4 comparisons per element on average.
```

### The worst case

Bad pivots every round shrink the range by only one element, exactly like quicksort. The rounds then partition all n elements, then one fewer, then one fewer again, down to 1: a shrinking triangle of work that adds up to about half of n squared element visits, which is **O(n²)**.

With a first- or last-element pivot, a sorted input does this. Random pivots make it vanishingly unlikely, but not impossible, and an adversary who can predict your random number generator can still force it.

## Key takeaways
- Only the side containing the requested rank survives.
- Independent random pivots give expected linear work for distinct keys; poor splits still give a quadratic worst case.

## Further reading
- [Heap operations and top-k — Python heapq](https://docs.python.org/3/library/heapq.html)
- [Time bounds for selection — Blum, Floyd, Pratt, Rivest and Tarjan](https://people.csail.mit.edu/rivest/pubs/BFPRT73.pdf)
- [Quickselect comparison analysis — Martínez and Roura](https://www.cs.upc.edu/~conrado/research/papers/sicomp-mr01.pdf)
