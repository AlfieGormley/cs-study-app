---
id: pat-submask-walk
title: Walk nonzero submasks in descending order
level: advanced
minutes: 3
sourceLesson: pat-bits
summary: Subtract one then intersect with the original mask to get the next submask.
---

The preceding subset representation is the prerequisite. Here n is the number of mask bits, and the illustrative loop visits nonzero submasks under a unit-cost mask model.

## Iterate nonzero submasks

For nonnegative `mask`, iterate over every **nonzero submask**:

```python
s = mask
while s:
    ...           # use submask s
    # Restrict the next candidate to this
    # mask.
    s = (s - 1) & mask
```

Over all n-bit masks, there are 3ⁿ (mask, submask) pairs including zero submasks, since each element is in the submask, in the mask only, or in neither. This loop omits one zero submask per mask:

```formula
V = 3^n − 2^n
n = 3
V = 27 − 8 = 19
where
V: the total number of loop visits, summed over all 2^n masks
n: the number of bits (items)
3^n: n copies of 3 multiplied together, the number of (mask, submask) pairs including empty submasks
2^n: the number of masks, each of which has one empty submask that the loop skips
In words: three choices per bit give 3^n pairs, and dropping the empty submask of each of the 2^n masks leaves 3^n − 2^n visits; for 3 bits, 19.
```

That is O(3ⁿ) in the unit-cost mask model.

## Recognising the pattern

| Cue | Trick |
|---|---|
| "appears twice except one" | XOR everything |
| "power of two" | `x > 0 and (x & (x - 1)) == 0` |
| "count 1 bits" | Kernighan / DP |
| Lowest set bit | `x & -x` |
| At most 20 items, choose a subset | Enumerate position masks |
| Visit all of at most 20 nodes | Bitmask DP |
| Many boolean flags | Pack into an int |

## Key takeaways
- Subtract one then intersect with the original mask to get the next submask.
- The shown loop excludes zero and requires a nonnegative original mask.
- Across all masks, excluding empty submasks removes one visit per mask.

## Further reading
- [Bit manipulation — cp-algorithms](https://cp-algorithms.com/algebra/bit-manipulation.html)
- [Enumerating submasks — cp-algorithms](https://cp-algorithms.com/algebra/all-submasks.html)
- [Bit Twiddling Hacks — Sean Eron Anderson, Stanford](https://graphics.stanford.edu/~seander/bithacks.html)
- [Hamming weight — Wikipedia](https://en.wikipedia.org/wiki/Hamming_weight)
- [Binary cheatsheet — Tech Interview Handbook](https://www.techinterviewhandbook.org/algorithms/binary/)
