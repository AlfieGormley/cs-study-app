---
id: logp-invariants-binary-search
title: Proving binary search and checking machine arithmetic
level: intermediate
minutes: 4
sourceLesson: logp-invariants
summary: Track known lower and upper regions and keep midpoint updates inside the unknown region.
---

## Binary search, done properly

Binary search is famous for being easy to describe and hard to get right. An invariant makes it mechanical. This version returns the first index whose element is at least x (the bisect_left insertion position), assuming a stable ascending list and a total order shared with x. NaNs and inconsistent custom comparisons are excluded. The invariant also includes 0 is at most lo is at most hi is at most len(a):

```python
def bsearch(a, x):
    # a is sorted ascending
    lo, hi = 0, len(a)
    # I: all of a[:lo]  <  x
    #    all of a[hi:] >= x
    while lo < hi:
        # Floor division stays in the
        # interval.
        mid = (lo + hi) // 2
        if a[mid] < x:
            # Discard values below the
            # target.
            lo = mid + 1
        else:
            # Keep mid as a possible answer.
            hi = mid
    return lo
```

The invariant splits the list into three regions (with n equals len(a)):

```
 index: 0    lo         hi     n
        [ <x ][  unknown  ][ >=x ]
```

The three regions have precise meanings:

Everything before the lower boundary is known to be smaller than the target. Everything from the upper boundary onward is known to be at least the target. During an iteration the midpoint lies inside the remaining unknown region.

- **Init**: a[:0] and a[n:] are both empty, so I holds vacuously. ✓
- **Maintain**: since lo is at most mid is less than hi, mid is in the unknown zone.
  - If a[mid] is less than x, then because a is sorted, everything up to mid is less than x. Setting lo equals mid plus 1 keeps "every value in `a[:lo]` is less than `x`". ✓
  - Otherwise a[mid] is at least x, so everything from mid on is at least x. Setting hi equals mid keeps "every value in `a[hi:]` is at least `x`". ✓
- **Terminate**: exit means lo equals hi. The unknown zone is empty: everything before lo is less than x and everything from lo on is at least x. So lo is exactly the first index with a[lo] is at least x (or n if there is none). ✓
- **Variant**: hi minus lo. Because lo is at most mid is less than hi, either lo grows or hi shrinks, by at least 1. ✓

Each choice is now forced by the invariant. Write `hi = mid - 1` and you could skip the answer; write `lo = mid` and when hi equals lo plus 1 the loop spins forever, because mid equals lo. The invariant tells you which is right instead of guessing.

> [!warning] Proofs over ideal numbers
> In 2006 Joshua Bloch reported that the JDK's `binarySearch` had been broken for about nine years. The line `mid = (low + high) / 2` overflows a 32-bit `int` once low plus high exceeds the largest signed 32-bit integer, giving a negative index. The invariant proof was right *for mathematical integers*. Python integers have arbitrary precision, subject to available memory. For nonnegative in-range indices with low at most high in Java or C, use `low + (high - low) / 2`. C signed overflow is undefined behaviour, whereas Java int arithmetic wraps.

A signed 32-bit integer holds values only up to 2,147,483,647. Two valid large indices can have a sum above that limit. Adding half the nonnegative gap to the lower index stays between the two indices, so it remains in range.


## Key takeaways
- Track known lower and upper regions and keep midpoint updates inside the unknown region.
- An integer proof needs additional checks when the implementation uses fixed-width machine arithmetic.

## Further reading
- [MIT Mathematics for Computer Science](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-spring-2015/mit6_042js15_textbook.pdf)
- [Binary-search overflow — Joshua Bloch](https://research.google/blog/extra-extra-read-all-about-it-nearly-all-binary-searches-and-mergesorts-are-broken/)
