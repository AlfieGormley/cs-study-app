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

A comparator must define a **strict weak ordering**. In plain terms, its "comes before" answers must obey these rules:

1. **Consistent:** `cmp(a, b)` always gives the same answer for the same pair.
2. **Irreflexive and asymmetric:** nothing comes before itself, and two elements cannot each come before the other.
3. **Transitive:** if a comes before b and b before c, then a comes before c.
4. **Transitive ties:** if a ties with b (neither comes before the other) and b ties with c, then a must tie with c.

```formula reference
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

> [!analogy] Real-world analogy: ranking rock, paper and scissors
> Try to line up rock, paper and scissors from weakest to strongest. Rock beats scissors, scissors beats paper, but paper beats rock, so whichever order you pick, some pair is in the "wrong" place. Asking different people to do the ranking gives different answers, depending on which pair each looks at first.
>
> **How it maps:** "beats" is a comparator that breaks transitivity. A sorting algorithm assumes the answers fit together into one consistent line; when they do not, its result depends on which pairs it happened to compare, or it detects the contradiction and fails.
>
> **Where it stops:** the game's cycle is obvious. Real comparator bugs are usually hidden: `a - b` is correct for most values and wrong only for extreme ones, and NaN breaks the rules only when one is present, so the failure appears rarely and often only in production.

Break the contract and the consequences depend on the language:

- **Java** TimSort may throw `IllegalArgumentException: Comparison method violates its general contract!`, often only on large or unlucky inputs, so it passes tests and fails in production.
- **C++** `std::sort` has **undefined behaviour**. Real implementations can run past the end of the array (the unguarded insertion loop assumes some earlier element will stop its scan), causing crashes or memory corruption.
- **Rust** may panic since 1.81, but never causes memory unsafety.
- **Python** may produce an order that does not satisfy the intended relation; user comparison code can also raise exceptions.

Common ways to break it (the Java block shows alternative comparator expressions to place inside a sorting call):

```java
// overflow: 2e9 - (-2e9) wraps negative
(a, b) -> a - b
// fix
(a, b) -> Integer.compare(a, b)
```

Why it overflows: Java's `int` holds values only up to 2,147,483,647 (about 2.1 billion). Comparing 2 billion with −2 billion gives a true difference of 4 billion, which does not fit, so it wraps round to −294,967,296. The negative result tells the sort that 2 billion comes *before* −2 billion.

- Random comparators (`() => Math.random() - 0.5` to "shuffle") are inconsistent and produce biased shuffles. Use Fisher–Yates.
- **NaN.** Ordered comparisons (<, <=, >, >=) with NaN are false, while != is true. Treating NaN as equivalent to every value via neither-less-than breaks transitivity of incomparability. In Python, `sorted([3, nan, 1, 2])` returns `[3, nan, 1, 2]`: not sorted at all. Filter NaNs out first or use a key that places them explicitly.
- Comparators that read mutable state (a "current time" or a cache that changes mid-sort).

## Key takeaways
- Strict weak ordering includes transitivity of both ordering and incomparability.
- Overflow, NaNs and changing state can break the contract and invalidate sorting results.

## Further reading
- [Comparator contract — Java documentation](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/Comparator.html)
- [Ordering requirements — C++ working draft](https://eel.is/c++draft/alg.sorting)
