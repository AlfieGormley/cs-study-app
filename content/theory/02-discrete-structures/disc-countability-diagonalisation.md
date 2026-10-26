---
id: disc-countability-diagonalisation
title: "Countability and Cantor’s diagonal argument"
level: basic
minutes: 3
summary: "A bijection establishes equal cardinality even for infinite sets."
sourceLesson: disc-sets-functions
---

## Infinite sets have different sizes

For infinite sets, no finite count gives their size, so "same size" is defined by pairing them up: two sets have the same cardinality exactly when there is a bijection between them, so their elements pair off one-to-one with nothing left over on either side. This leads to surprises.

A set is **countable** if it is finite or in bijection with the natural numbers 0, 1, 2, …: its elements can be listed so every particular element is eventually reached. The integers are countable: list them as 0, 1, −1, 2, −2, ….

The list alternates positive and negative integers while moving away from zero. Every particular integer appears after finitely many steps, although the list never finishes.

The rational numbers are countable too, as are all finite strings over a finite alphabet. Therefore **the set of all programs is countable**.

**Cantor's diagonal argument** shows that the set of infinite binary sequences (equivalently, the power set of ℕ, or the real numbers) is **not** countable. Suppose you had a complete list of sequences. Build a new sequence d by flipping the i-th bit of the i-th sequence:

```formula essential
d(i) = 1 − s_i(i)
where
s_i: the i-th infinite 0/1 sequence in the supposedly complete list (s_1 first, s_2 second, …)
s_i(i): bit number i of sequence s_i: the bits on the diagonal
d: the new sequence being built
d(i): bit number i of d
i: a position, 1, 2, 3, …
In words: d takes the diagonal bit of each listed sequence and flips it (1 − 0 = 1, 1 − 1 = 0), so d disagrees with every listed sequence somewhere and cannot be on the list.
```

```
s1 = 0 1 1 0 1 ...
s2 = 1 1 0 0 0 ...
s3 = 0 0 0 1 1 ...
s4 = 1 0 1 1 0 ...
d  = 1 0 1 0 ...   (flip diagonal)
```

The diagonal bits are 0, 1, 0, 1, so the new sequence starts 1, 0, 1, 0. It differs from the first sequence in position one, from the second in position two, and so on. It cannot occur anywhere on the supposed complete list. **Cantor’s theorem** generalises this:

Every set has strictly more subsets than elements: there is no bijection between a set and its power set. This holds for infinite sets too, so there is no largest infinity.

> [!note] Why CS cares
> Programs are countable but the set of functions from ℕ to {0, 1} (all possible yes/no problems) is not. So almost all problems have no program that solves them. The halting problem, covered in the computability module, is a concrete example built with the same diagonal trick.

## Key takeaways

- A bijection establishes equal cardinality even for infinite sets.
- Diagonalisation constructs an infinite binary sequence missing from any proposed list.

## Further reading

- [Mathematics for Computer Science — MIT](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
- [Cantor's diagonal argument — Wikipedia](https://en.wikipedia.org/wiki/Cantor%27s_diagonal_argument)
- [Mathematics for Computer Science — MIT OpenCourseWare](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-spring-2015/)
