---
id: pat-xor-cancellation
title: Cancel pairs and separate two single values
level: advanced
minutes: 4
sourceLesson: pat-bits
summary: XOR cancels equal pairs regardless of order or grouping.
---

Here n is the sequence length. Multiplicity contracts are part of correctness: do not apply cancellation when counts differ from those promised.

## XOR: the cancelling operator

XOR has four properties that make it look like magic:

```formula essential
x ⊕ x = 0
x ⊕ 0 = x
x ⊕ y = y ⊕ x
(x ⊕ y) ⊕ z = x ⊕ (y ⊕ z)
where
x: any integer (y and z likewise)
y: a second integer
z: a third integer
⊕: XOR (written `^` in Python), bit by bit: 1 where the two bits differ, 0 where they match
In words: a value XOR-ed with itself vanishes, XOR with 0 changes nothing, and neither the order nor the grouping matters, so in a long chain each pair of equal values cancels wherever they sit.
```

The four lines are self-inverse, identity, commutative and associative.

So XOR-ing a list together **cancels every value that appears an even number of times**.

> [!analogy] Real-world analogy: pairing socks from the wash
> Tip a basket of clean socks on the bed and pair them up in whatever order they come out. Every matched pair goes away, and if exactly one sock has no partner, it is the one left on the bed, no matter where in the pile it was.
>
> **How it maps:** each sock is a value, a matched pair is `x ^ x = 0`, and the fact that the order of pairing does not matter is XOR's commutativity and associativity. The lone sock is what `reduce(xor, nums, 0)` returns.
>
> **Where it stops:** you need room on the bed for unmatched socks, while XOR keeps a single running integer however many values are waiting for partners. XOR also works bit by bit: it does not "find" the odd value, it is what remains when all pairs cancel, so if the input breaks the promise (say, three copies of one value), the result is the XOR of everything that fails to cancel, which need not be any value in the input.

**Single number.** Every element appears twice except one. Find it in O(n) time, O(1) space:

```python
from functools import reduce
from operator import xor

def single(nums):
    return reduce(xor, nums, 0)

# [4, 1, 2, 1, 2] -> 4
```

**Missing number.** `nums` contains n distinct values from `0..n` with one missing. XOR all of `0..n` together with all the values: every value that is present appears twice and cancels, leaving the missing one. For `nums = [3, 0, 1]`, XOR-ing 0, 1, 2 and 3 with 3, 0 and 1 leaves 2. Unlike summing, the running XOR never grows beyond the bit width of the values, so there is no overflow risk.

## Two single numbers

Assume a reusable sequence of integers in which every value appears twice except **two distinct singles**, `x` and `y`. XOR-ing everything gives `x ^ y`, which is non-zero because `x != y`. Any set bit in it is a position where `x` and `y` differ, so split the numbers into two groups by that bit; each group contains exactly one of them, and duplicates stay together.

```python
def two_singles(nums):
    xy = 0
    for n in nums:
        xy ^= n
    # Separate the singles with a differing
    # bit.
    low = xy & -xy     # a differing bit
    x = 0
    for n in nums:
        if n & low:
            # Equal pairs within this group
            # cancel.
            x ^= n
    return x, xy ^ x
```

For `[1, 2, 1, 3, 2, 5]`, the total XOR is 3 XOR 5, which is 6 (binary 110). Its lowest set bit has value 2, so 3 and 5 differ there. The group with that bit contains 2, 3 and 2, cancelling to 3; XOR-ing the total 6 with 3 gives the other single, 5.

## Key takeaways
- XOR cancels equal pairs regardless of order or grouping.
- Missing-number XOR needs the exact distinct-value domain.
- A differing bit partitions two unique singles while duplicates stay together.

## Further reading
- [Bit manipulation — cp-algorithms](https://cp-algorithms.com/algebra/bit-manipulation.html)
- [Enumerating submasks — cp-algorithms](https://cp-algorithms.com/algebra/all-submasks.html)
- [Bit Twiddling Hacks — Sean Eron Anderson, Stanford (archived copy)](https://web.archive.org/web/20250605031917/https://graphics.stanford.edu/~seander/bithacks.html)
- [Hamming weight — Wikipedia](https://en.wikipedia.org/wiki/Hamming_weight)
- [Binary cheatsheet — Tech Interview Handbook](https://www.techinterviewhandbook.org/algorithms/binary/)
