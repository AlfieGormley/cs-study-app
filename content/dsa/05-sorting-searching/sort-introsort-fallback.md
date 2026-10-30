---
id: sort-introsort-fallback
title: Introsort and adversarial inputs
level: intermediate
minutes: 2
sourceLesson: sort-quicksort
summary: A depth budget detects excessive quicksort work and switches to heapsort.
---

This unit builds on the preceding sorting units. Here n is the number of input elements; Big O bounds growth up to a constant factor, and logarithms are base two unless stated otherwise.

## Introsort: a worst-case guarantee

David Musser's **introsort** (1997) combines three algorithms:

1. Run quicksort (median-of-three pivots).
2. Track recursion depth. If it exceeds a budget of about twice the depth that perfect halving would need (38 levels for a million elements in libstdc++), the pivots are going badly, so switch that sub-array to **heapsort**, which is O(n log n) worst case (covered later in this module).
3. Leave small sub-arrays (16 elements or fewer in libstdc++) unsorted, then finish with one insertion sort pass over the whole array.

```formula reference
d_max = 2⌊log_2(n)⌋
where
d_max: the recursion depth at which libstdc++'s introsort gives up on quicksort for that sub-array
n: the number of elements being sorted
log_2(n): the base-2 logarithm of n
⌊ ⌋: the floor: round down to a whole number
In words: introsort allows about twice the depth that perfect halving would need before deciding the pivots are bad.
```

> [!analogy] Real-world analogy: a shortcut with a turn-back rule
> You usually drive home through back streets because they are fastest. But you set yourself a rule: if you have taken more than twice the usual number of turns, something has gone wrong (roadworks, a diversion), so for the rest of the way you take the main road, which is never quick but never terrible.
>
> **How it maps:** the back streets are quicksort, the turn count is the recursion depth, the "twice the usual" rule is the depth budget, and the main road is heapsort's guaranteed O(n log n).
>
> **Where it stops:** you abandon the whole route at once. Introsort switches only the sub-array whose budget ran out; other parts of the array carry on with quicksort, and the work already done is kept.

Since heapsort costs O(n log n) on any sub-array it takes over, the total stays O(n log n). You get quicksort's speed in the common case and an O(n log n) guarantee. C++ requires `std::sort` to be O(n log n) in the worst case since C++11, and the major standard libraries typically use introsort-style hybrids (libstdc++ and MSVC; libc++ only added the worst-case fallback in LLVM 14). .NET's `Array.Sort` is introsort too. pdqsort (covered later in this module) is a modern descendant.

## Key takeaways
- A depth budget detects excessive quicksort work and switches to heapsort.
- Deterministic pivot heuristics alone cannot guarantee safety against adversarial inputs.

## Further reading
- [Quicksort and partitioning — Princeton Algorithms](https://algs4.cs.princeton.edu/23quicksort/)
