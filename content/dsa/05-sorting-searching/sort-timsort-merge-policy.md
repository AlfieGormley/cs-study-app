---
id: sort-timsort-merge-policy
title: Timsort merge policies and galloping
level: advanced
minutes: 4
sourceLesson: sort-real-world
summary: Merge only adjacent runs and use a policy that bounds pending work.
---

This unit builds on the preceding sorting units. Here n is the number of input elements; Big O bounds growth up to a constant factor, and logarithms are base two unless stated otherwise.

### 3. Merge runs with a balanced policy

Runs are pushed onto a stack. Timsort merges only **adjacent** runs (merging non-adjacent ones would break stability) and chooses when to merge so that merges stay balanced and the stack stays small.

Classic Timsort uses run-length inequalities to keep pending runs growing geometrically toward the bottom of the stack:

```formula
|A| > |B| + |C|
|B| > |C|
where
A: the third run from the top of the run stack
B: the second run from the top
C: the run on top of the stack, the most recently found
|A|: the length of run A, in elements (likewise |B| and |C|)
>: greater than
In words: each pending run must be longer than the two above it combined, so lengths grow at least as fast as Fibonacci numbers and the stack stays short.
```

When an inequality fails, Timsort merges runs until both hold again. With runs of 15, 20 and 30 elements (C, B, A), the first rule fails because 30 is not greater than 20 + 15 = 35, so a merge happens. Correct collapse logic must maintain the intended invariant beyond just the top three runs. Stack capacity and policies differ by implementation; CPython uses powersort.

> [!warning] A proof found a bug
> In 2015, researchers formally verifying Java's `TimSort` with the KeY tool found that the merge-collapse rules did not always restore the invariant. On specially crafted arrays of around 67 million elements, the run stack overflowed with an `ArrayIndexOutOfBoundsException`. Python fixed the rule; Java enlarged the stack. Since Python 3.11, CPython uses the **powersort** merge policy (Munro and Wild), which is provably near-optimal and simpler to reason about.

### 4. Gallop when one run is winning

During a normal merge, Timsort counts how many times in a row the output came from the same run. If that reaches `MIN_GALLOP` (initially 7), it switches to **galloping**: an exponential search checking positions 1, 3, 7, 15, ... then a binary search, to find how many elements it can copy in one block.

```formula
p_j = 2^j − 1
g ≈ 2 log_2(m)
g ≈ 2 log_2(500) ≈ 18
where
p_j: the position (offset from the start of the run) checked on probe number j: 1, 3, 7, 15, …
j: the probe number, 1, 2, 3, …
2^j: j copies of 2 multiplied together
g: the comparisons galloping needs to find where the other run's next element belongs
m: how many elements the winning run can copy in one block; 500 in the example below
log_2(m): the base-2 logarithm of m: how many doublings it takes to reach m (log_2(500) ≈ 9)
≈: approximately equal to
In words: about log_2(m) doubling probes overshoot the target, then about log_2(m) binary-search steps pin it down, instead of m one-by-one comparisons.
```

```
A: [1 2 3 4 5 ... 1000]
B: [500.5, 2000]
normal merge: ~500 comparisons for A's head
galloping: about 18 boundary comparisons
```

If galloping stops paying off, the threshold rises; if it keeps paying off, it falls. This adaptivity is why concatenating two sorted lists and sorting costs close to O(n), not O(n log n).

### Timsort's profile

In the table, n is the number of elements and k the number of natural runs in the input.

| Input | Cost |
|---|---|
| Already sorted / reversed | O(n): one run |
| k runs | O(n(1 + log k)) adaptive bound |
| Random | O(n log n), close to merge sort |
| Merge buffer | up to half the input elements; key caching and other metadata add storage |

Timsort minimises **comparisons**, which is exactly right for Python and JavaScript, where each comparison is a dynamic call that may run user code and costs far more than moving a pointer.

## Key takeaways
- Merge only adjacent runs and use a policy that bounds pending work.
- Galloping finds copy boundaries by exponential then binary search when one run keeps winning.

## Further reading
- [Sorting techniques — Python documentation](https://docs.python.org/3/howto/sorting.html)
- [CPython 3.14.0 list-sort design notes](https://raw.githubusercontent.com/python/cpython/v3.14.0/Objects/listsort.txt)
- [Formal verification of Java’s TimSort — de Gouw and colleagues](https://ir.cwi.nl/pub/23709/23709A.pdf)
