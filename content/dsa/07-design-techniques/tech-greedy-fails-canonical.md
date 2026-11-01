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

You don't have to test every amount. Kozen and Zaks (1994) showed that, for a system of at least three distinct coins including a 1-coin, the smallest counterexample, if there is one, lies strictly between the third-smallest coin plus one and the sum of the two largest coins. So a finite, short range of amounts settles the question: if greedy matches the true optimum on all of them, it matches everywhere.

```formula reference
1 = c_1 < c_2 < … < c_m
c_3 + 1 < x < c_m + c_{m−1}
where
c_1: the smallest denomination, which must be 1
c_2: the second-smallest denomination
c_m: the largest denomination
c_{m−1}: the second-largest denomination
c_3: the third-smallest denomination
m: the number of distinct denominations, at least 3
x: the smallest amount where greedy uses more coins than necessary, if the system is non-canonical
…: and so on, in increasing order
In words: if greedy ever goes wrong, it first goes wrong above the third-smallest coin plus one and below the sum of the two largest coins, so only those amounts need checking.
```

For {1, 5, 12} the window is 14 to 16, and checking it finds 15: greedy pays 12 + 1 + 1 + 1, four coins, where 5 + 5 + 5 needs three. Each check compares greedy with an exact method such as the amount DP. Pearson (2005) later gave a test that runs in time polynomial in the number of denominations.

## Key takeaways
- A theorem bounds the smallest counterexample for sorted distinct denominations beginning with one.
- Finite testing proves canonicity only when its tested range follows a valid theorem.

## Further reading
- [Kozen and Zaks: Optimal Bounds for the Change-Making Problem](https://www.cs.cornell.edu/~kozen/papers/change)
