---
id: tech-greedy-fails-canonical
title: Testing whether a coin system is canonical
level: advanced
minutes: 2
sourceLesson: tech-greedy-fails
summary: A theorem bounds the smallest counterexample for sorted distinct denominations beginning with one.
---

A failed amount disproves canonicity immediately. A successful finite sample alone does not prove it. For sorted distinct denominations beginning with a one-coin, a theorem identifies a finite range that is sufficient to test.

### Testing a coin system

You don't have to test every amount. Kozen and Zaks (1994) showed that the smallest counterexample, if there is one, lies in a narrow window:

```formula
1 = c_1 < c_2 < … < c_m
c_3 + 1 < x < c_m + c_{m−1}
13 < x < 17
where
c_1: the smallest denomination, which must be 1
c_2: the second-smallest denomination
c_m: the largest denomination
c_{m−1}: the second-largest denomination
c_3: the third-smallest denomination
m: the number of distinct denominations, at least 3
x: the smallest amount where greedy uses more coins than necessary, if the system is non-canonical
…: and so on, in increasing order
In words: if greedy ever goes wrong, it first goes wrong somewhere between c_3 + 1 and the sum of the two largest coins, so only those amounts need checking; for {1, 5, 12} that is 14 to 16.
```

So for {1, 5, 12}, checking amounts below 17 suffices, and 15 is found. Pearson later gave a polynomial-time test.

## Key takeaways
- A theorem bounds the smallest counterexample for sorted distinct denominations beginning with one.
- Finite testing proves canonicity only when its tested range follows a valid theorem.

## Further reading
- [Kozen and Zaks: Optimal Bounds for the Change-Making Problem](https://www.cs.cornell.edu/~kozen/papers/change)
