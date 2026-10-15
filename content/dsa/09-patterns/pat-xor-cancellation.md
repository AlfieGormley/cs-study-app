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

XOR has three properties that make it look like magic:

```formula
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

**Single number.** Every element appears twice except one. Find it in O(n) time, O(1) space:

```python
from functools import reduce
from operator import xor

def single(nums):
    return reduce(xor, nums, 0)

# [4, 1, 2, 1, 2] -> 4
```

**Missing number.** `nums` contains n distinct values from `0..n` with one missing. XOR all indices `0..n` with all values; everything present cancels, leaving the missing one:

```formula
m = (0 ⊕ 1 ⊕ … ⊕ n) ⊕ (v_1 ⊕ … ⊕ v_n)
m = (0 ⊕ 1 ⊕ 2 ⊕ 3) ⊕ (3 ⊕ 0 ⊕ 1)
m = 2
where
m: the missing number
n: the length of nums; the values come from 0 to n
v_1: the first value in nums (v_n the last)
v_n: the last value in nums
⊕: XOR (`^` in Python); equal values cancel to 0
…: "and so on", continuing the pattern
In words: every value that is present appears once in each bracket and cancels, so only the missing one survives; for nums = [3, 0, 1], the missing number is 2.
```

No integer overflow risk, unlike summing.

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

For `[1, 2, 1, 3, 2, 5]`, the total XOR is 6, whose lowest set bit has value 2. The group with that bit contains 2, 3 and 2, cancelling to 3; the other single is 5.

```formula
X = 3 ⊕ 5 = 6
L = X ∧ (−X) = 2
Y = X ⊕ 3 = 5
where
X: the total XOR after duplicate pairs cancel
L: the isolated differing bit used to partition the input
Y: the other single value
⊕: bitwise XOR, one where operand bits differ
∧: bitwise AND, one only where both operand bits are one
In words: the singles differ at the bit of value two, so the two groups separately recover three and five.
```



## Key takeaways
- XOR cancels equal pairs regardless of order or grouping.
- Missing-number XOR needs the exact distinct-value domain.
- A differing bit partitions two unique singles while duplicates stay together.

## Further reading
- [Bit manipulation — cp-algorithms](https://cp-algorithms.com/algebra/bit-manipulation.html)
- [Enumerating submasks — cp-algorithms](https://cp-algorithms.com/algebra/all-submasks.html)
- [Bit Twiddling Hacks — Sean Eron Anderson, Stanford](https://graphics.stanford.edu/~seander/bithacks.html)
- [Hamming weight — Wikipedia](https://en.wikipedia.org/wiki/Hamming_weight)
- [Binary cheatsheet — Tech Interview Handbook](https://www.techinterviewhandbook.org/algorithms/binary/)
