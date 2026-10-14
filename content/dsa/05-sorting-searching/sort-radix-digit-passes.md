---
id: sort-radix-digit-passes
title: Stable LSD radix passes
level: intermediate
minutes: 2
sourceLesson: sort-linear-time
summary: Start with the least significant digit and preserve previous lower-digit order.
---

This unit builds on the preceding sorting units. Here n is the number of input elements; Big O bounds growth up to a constant factor, and logarithms are base two unless stated otherwise.

## Radix sort

**Idea:** break each key into digits and sort one digit at a time with a stable counting sort.

**LSD (least significant digit) radix sort** starts with the last digit and works left. Sort `[170, 45, 75, 90, 802, 24, 2, 66]` in base 10:

```
ones:  [170, 90, 802, 2, 24, 45, 75, 66]
tens:  [802, 2, 24, 45, 66, 170, 75, 90]
100s:  [2, 24, 45, 66, 75, 90, 170, 802]
```

Look at the tens pass: 802 and 2 both have tens digit 0. The ones pass had already put 802 before 2, and because the sort is stable, they keep that order. Once a pass is done, ties on the current digit are broken by the lower digits, which were sorted earlier. **Without stability, LSD radix sort gives wrong answers.**

```python
def radix_sort(a, base=256):
    if type(base) is not int or base < 2:
        raise ValueError("base >= 2")
    if any(type(x) is not int or x < 0
           for x in a):
        raise ValueError("nonnegative ints")
    if not a:
        return a
    # Start at the least significant digit.
    exp = 1
    while max(a) // exp > 0:
        digit = lambda x: (x // exp) % base
        # Keep the order established by
        # prior digits.
        a = counting_sort(a, digit, base)
        # Move to the next more significant
        # digit.
        exp *= base
    return a
```

## Key takeaways
- Start with the least significant digit and preserve previous lower-digit order.
- Every digit pass must be stable for the final ordering to be correct.

## Further reading
- [LSD and MSD radix sorting — Princeton Algorithms](https://algs4.cs.princeton.edu/51radix/)
