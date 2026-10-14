---
id: sort-comparator-ordering
title: Comparator contracts and failure cases
level: advanced
minutes: 4
sourceLesson: sort-real-world
summary: Strict weak ordering includes transitivity of both ordering and incomparability.
---

This unit builds on the preceding sorting units. Here n is the number of input elements; Big O bounds growth up to a constant factor, and logarithms are base two unless stated otherwise.

## Comparators: the contract

A comparator must define a **strict weak ordering**. Written as rules about its "less than" answer:

```formula
¬(a < a)
a < b  ⇒  ¬(b < a)
(a < b) ∧ (b < c)  ⇒  a < c
E(a, b) = ¬(a < b) ∧ ¬(b < a)
E(a, b) ∧ E(b, c)  ⇒  E(a, c)
where
a: any element being sorted
b: any other element
c: any third element
E: Boolean equivalence test: true when neither argument precedes the other according to this comparator; it need not mean the objects are identical
<: "comes before", as the comparator reports it
¬: "not": the statement in brackets is false
∧: "and": both statements hold
⇒: "implies": if the left side holds, the right side must too
In words: nothing comes before itself, two elements cannot each come before the other, and both ordering and comparator-equivalence chain transitively. If a ties b and b ties c, a must also tie c.
```

In practice:

1. Consistent: `cmp(a, b)` always gives the same answer for the same pair.
2. Irreflexive and asymmetric: the first two rules above.
3. Transitive: the third rule, and the same for "equal" (neither comes before the other).

Break the contract and the consequences depend on the language:

- **Java** TimSort may throw `IllegalArgumentException: Comparison method violates its general contract!`, often only on large or unlucky inputs, so it passes tests and fails in production.
- **C++** `std::sort` has **undefined behaviour**. Real implementations can run past the end of the array (the unguarded insertion sort assumes a sentinel), causing crashes or memory corruption.
- **Rust** may panic since 1.81, but never causes memory unsafety.
- **Python** may produce an order that does not satisfy the intended relation; user comparison code can also raise exceptions.

Common ways to break it (the Java block shows alternative comparator expressions to place inside a sorting call):

```java
// overflow: 2e9 - (-2e9) wraps negative
(a, b) -> a - b
// fix
(a, b) -> Integer.compare(a, b)
```

Why it overflows: Java's `int` holds values only up to about 2.1 billion, so a true difference larger than that wraps round to a negative number.

```formula
d = a − b
d = 2 × 10^9 − (−2 × 10^9) = 4 × 10^9
d_max = 2^31 − 1 ≈ 2.147 × 10^9
where
d: the difference the comparator returns; its sign is meant to say which is larger
a: the first value compared; here 2,000,000,000
b: the second value compared; here −2,000,000,000
d_max: the largest value a 32-bit signed Java int can hold, 2,147,483,647
2^31: 31 copies of 2 multiplied together
10^9: ten to the power 9, a billion
≈: approximately equal to
In words: the real difference, 4 billion, is bigger than an int can hold, so it wraps to a negative number and the comparator claims a < b.
```

- Random comparators (`() => Math.random() - 0.5` to "shuffle") are inconsistent and produce biased shuffles. Use Fisher–Yates.
- **NaN.** Ordered comparisons (<, <=, >, >=) with NaN are false, while != is true. Treating NaN as equivalent to every value via neither-less-than breaks transitivity of incomparability. In Python, `sorted([3, nan, 1, 2])` returns `[3, nan, 1, 2]`: not sorted at all. Filter NaNs out first or use a key that places them explicitly.
- Comparators that read mutable state (a "current time" or a cache that changes mid-sort).

## Key takeaways
- Strict weak ordering includes transitivity of both ordering and incomparability.
- Overflow, NaNs and changing state can break the contract and invalidate sorting results.

## Further reading
- [Comparator contract — Java documentation](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/Comparator.html)
- [Ordering requirements — C++ working draft](https://eel.is/c++draft/alg.sorting)
