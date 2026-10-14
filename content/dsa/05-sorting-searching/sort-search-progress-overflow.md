---
id: sort-search-progress-overflow
title: Binary-search progress and overflow
level: intermediate
minutes: 4
sourceLesson: sort-binary-search
summary: Avoid overflowing fixed-width midpoint arithmetic.
---

This unit builds on the preceding search units. Here n is the number of input elements; Big O bounds growth up to a constant factor, and logarithms are base two unless stated otherwise.

## The classic pitfalls

### 1. Midpoint overflow

The following Java lines are alternative midpoint expressions, not three declarations to place in one scope.

```java
int mid = (lo + hi) / 2;        // bug
int mid = lo + (hi - lo) / 2;   // fix
int mid = (lo + hi) >>> 1;      // Java
```

A 32-bit signed `int` can hold values only up to about 2.1 billion. Two large indices can add up to more than that:

```formula
s_max = 2^31 − 1 = 2147483647
lo + hi = 1.1 × 10^9 + 1.2 × 10^9
lo + hi = 2.3 × 10^9 > s_max
lo + (hi − lo) / 2 ≤ hi
where
s_max: the largest value a 32-bit signed integer can hold
lo: the low index of the search range; here 1.1 billion
hi: the high index of the search range; here 1.2 billion
2^31: 31 copies of 2 multiplied together
10^9: ten to the power 9, a billion
≤: less than or equal to
>: greater than
In words: once both indices are above about a billion, their sum exceeds the largest int and wraps to a negative number; the safe form only ever adds half the gap to lo, so it never exceeds hi.
```

For nonnegative Java int indices, the addition `lo + hi` can wrap once the array has more than about a billion elements, producing a negative midpoint. Signed overflow in C and C++ is undefined behavior; other languages have their own checked, wrapping or unsigned rules. In 2006 Joshua Bloch revealed that this bug had sat in Java's `Arrays.binarySearch` for about nine years, and in the version in Programming Pearls for two decades. Python's integers do not overflow, but C, C++, Java, Go and Rust code must use the safe form.

### 2. Infinite loops

If you ever write `lo = mid`, check what happens when `hi = lo + 1`. Then the rounded-down midpoint is `lo` itself, so `lo = mid` changes nothing and the loop spins forever:

```formula
m = ⌊(lo + hi) / 2⌋
m = ⌊(4 + 5) / 2⌋ = ⌊4.5⌋ = 4
where
m: the midpoint index, mid in the code
lo: the low end of the range; here 4
hi: the high end of the range; here 5, one more than lo
⌊ ⌋: the floor: round down to a whole number (Python's // does this)
In words: with two elements left, the rounded-down midpoint is lo itself, so setting lo to it makes no progress.
```

```
lo 4, hi 5 -> mid 4 -> lo = mid = 4
lo 4, hi 5 -> mid 4 -> ... forever
```

The fixes: make every branch move strictly past mid (`lo = mid + 1`), or round the midpoint up (`mid = (lo + hi + 1) // 2`) when the branch is `lo = mid`, or loop while `hi - lo > 1` (see the later integer-root unit).

### 3. Mixing interval conventions

Most bugs come from mixing closed `[lo, hi]` and half-open `[lo, hi)` conventions: `hi = len(a)` with `while lo <= hi` reads past the end; `hi = len(a) - 1` with `hi = mid` can never return n. Pick one convention per function and derive every line from it.

### 4. Unsorted or wrongly sorted input

Binary search on data that is not sorted by the same ordering silently returns nonsense, not an error. Sorting by `key=str.lower` and then searching with raw strings is a classic mismatch.

> [!tip] Test the edges
> Every binary search should be tested on: an empty array, one element, x smaller than everything, x larger than everything, x absent but in the middle, and many duplicates. Off-by-one bugs hide in exactly those cases.

## Key takeaways
- Avoid overflowing fixed-width midpoint arithmetic.
- Derive termination and updates from one interval convention and test empty, absent and duplicate cases.

## Further reading
- [Insertion-bound searches — Python bisect](https://docs.python.org/3/library/bisect.html)
