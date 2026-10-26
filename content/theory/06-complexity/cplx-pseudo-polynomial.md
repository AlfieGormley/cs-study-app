---
id: cplx-pseudo-polynomial
title: "Values versus bit lengths"
level: basic
minutes: 3
summary: "Subset sum’s table depends on the target value, not just its bit length."
sourceLesson: cplx-p-np
---

### The unary trap: pseudo-polynomial time

**Subset sum** asks: given a list of nonnegative integers and a nonnegative target total, does some selection add up to exactly the target? A textbook dynamic program fills a table with one row per number and one column per possible total, so its running time grows with the *value* of the target. That looks polynomial, but a positive target’s bit length grows only logarithmically:

```formula reference
t = O(nT)
T < 2^b
where
t: the running time of the dynamic program, in steps
n: how many numbers are in the input list
T: the target total (a value, not a length)
b: the number of bits used to write T in the input
2^b: 2 to the power b; a b-bit number is always smaller than this
O(...): Big O: "at most a constant times this, for large inputs"
In words: table work grows with the item count times the target value. The target value can be exponential in its encoded bit length, so this is not a polynomial-time bound for general binary inputs. Bit-operation analysis also accounts for counter and integer lengths.
```

Adding one bit to the target can roughly double the table width. A target fixed below a small bound is a useful special case, but does not establish polynomial time when its bit length grows.

Such algorithms are **pseudo-polynomial**: polynomial in the *value* of the numbers, not their length. Subset sum is not known to be in P.

## Key takeaways

- Subset sum’s table depends on the target value, not just its bit length.
- Pseudo-polynomial time can be exponential for binary inputs.
- A fixed numeric bound and a growing bit-width describe different input families.

## Further reading

- [Computational Complexity — Arora and Barak](https://theory.cs.princeton.edu/complexity/book.pdf)
