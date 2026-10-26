---
id: cx-master-leaves
sourceLesson: cx-recurrences
title: Master Theorem: leaves dominate
level: advanced
minutes: 2
summary: Find the critical exponent and recognise leaf-dominated recurrences.
---

The Master Theorem summarises the recursion-tree argument for equal-size fractional children. Use a fixed positive base-case cost and nonnegative outside work. Here n is input size.

## Compare outside work with leaf growth

```formula essential
T(n) = aT(n/b) + f(n)
c = log_b(a)
where
T(n): total counted work on input size n
a: a fixed number of children, at least one
b: a fixed shrink divisor greater than one
f(n): work done outside the recursive calls
c: the critical exponent describing leaf-count growth
log_b: logarithm to base b
n: positive input size
In words: fixed branching and fixed fractional shrinking determine how quickly the leaf count grows; compare the parent's outside work with that leaf growth.
```

For exact full trees, take input sizes that are powers of the divisor; ordinary rounding leaves the standard asymptotic results unchanged. Leaves grow as the input raised to the critical exponent.

## When the leaves dominate

The first case requires outside work to be smaller than leaf growth by a fixed positive power of input size. A mere logarithmic difference is insufficient.

```formula essential
f(n) = O(n^{c−ε})
T(n) = Θ(n^c)
where
f(n): nonnegative outside work
n: input size
c: the critical exponent from branching and shrinking
ε: epsilon, some fixed positive exponent gap
O: an eventual upper growth bound
Θ: a tight growth bound
T(n): total work under the equal-size recurrence and fixed positive base case
In words: when outside work is polynomially smaller, the growing number of small calls determines the total growth.
```

Four half-size children produce a quadratic leaf count. Linear outside work is smaller by a full power, so the total is quadratic rather than quadratic times log.

Reducing child count can improve an algorithm's exponent. Karatsuba integer multiplication uses three half-size products instead of four, with linear outside work in digit count. Strassen matrix multiplication uses seven half-size products instead of eight, with quadratic outside work in matrix side length. Toom-3 uses five roughly third-size integer products instead of nine. These examples reduce the leaf growth; constants and representation still affect practical performance.

## Key takeaways
- Check equal fractional children and fixed parameters first.
- The critical exponent comes from branching and shrinking.
- A fixed positive power gap lets leaf growth determine the total.

## Further reading
- [MIT: Master theorem, including power gaps and regularity](https://people.csail.mit.edu/thies/6.046-web/master.pdf)
- [Erickson: Solving Recurrences](https://jeffe.cs.illinois.edu/teaching/algorithms/notes/99-recurrences.pdf)
- [GMP: Toom three-way multiplication](https://gmplib.org/manual/Toom-3_002dWay-Multiplication)
