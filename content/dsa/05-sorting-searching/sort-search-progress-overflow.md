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

A 32-bit signed `int` can hold values only up to 2,147,483,647 (about 2.1 billion). Two large indices can add up to more than that: with `lo` at 1.1 billion and `hi` at 1.2 billion, the sum is 2.3 billion, which wraps round to a negative number. The safe form only ever adds half the gap to `lo`, so its result never exceeds `hi` and cannot overflow.

For nonnegative Java int indices, the addition `lo + hi` can wrap once the array has more than about a billion elements, producing a negative midpoint. Signed overflow in C and C++ is undefined behavior; other languages have their own checked, wrapping or unsigned rules. In 2006 Joshua Bloch revealed that this bug had sat in Java's `Arrays.binarySearch` for about nine years, and in the version in Programming Pearls for two decades. Python's integers do not overflow, but C, C++, Java, Go and Rust code must use the safe form.

### 2. Infinite loops

If you ever write `lo = mid`, check what happens when `hi = lo + 1`. Then the rounded-down midpoint is `lo` itself (for `lo` 4 and `hi` 5, `(4 + 5) // 2` is 4), so `lo = mid` changes nothing and the loop spins forever:

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
