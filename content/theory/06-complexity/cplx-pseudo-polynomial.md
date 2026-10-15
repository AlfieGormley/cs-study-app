---
id: cplx-pseudo-polynomial
title: "Values versus bit lengths"
level: basic
minutes: 3
summary: "Subset sum’s table depends on the target value, not just its bit length."
sourceLesson: cplx-p-np
---

### The unary trap: pseudo-polynomial time

**Subset sum** asks: given a list of nonnegative integers and a nonnegative target total, does some subset of S add up to exactly T? A textbook dynamic program fills a table with one row per number and one column per possible total, so its running time grows with the *value* of the target. That looks polynomial, but a positive target’s bit length grows only logarithmically:

```formula
t = O(nT)
T < 2^b
T < 2^64 ≈ 1.8 × 10^19   for b = 64
where
t: the running time of the dynamic program, in steps
n: how many numbers are in the list S
T: the target total (a value, not a length)
b: the number of bits used to write T in the input
2^b: 2 to the power b; a b-bit number is always smaller than this
O(...): Big O: "at most a constant times this, for large inputs"
≈: approximately equal to
In words: the running time is proportional to n times the target's value, and the value can be exponential in its length b. Adding a bit to the target can double its value and the table width, so the dynamic-programming table method is not polynomial in the general binary-encoded input length. The displayed bound counts table operations; bit operations also account for the lengths of counters and values.
```

With a 64-bit target the table can need about 1.8 × 10¹⁹ columns, even though the target takes only 8 bytes to write down.

Such algorithms are **pseudo-polynomial**: polynomial in the *value* of the numbers, not their length. Subset sum is not known to be in P.

## Key takeaways

- Subset sum’s table depends on the target value, not just its bit length.
- Pseudo-polynomial time can be exponential for binary inputs.
- A fixed numeric bound and a growing bit-width describe different input families.

## Further reading

- [Computational Complexity — Arora and Barak](https://theory.cs.princeton.edu/complexity/book.pdf)
