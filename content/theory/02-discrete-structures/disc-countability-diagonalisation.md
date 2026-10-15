---
id: disc-countability-diagonalisation
title: "Countability and Cantor’s diagonal argument"
level: basic
minutes: 4
summary: "A bijection establishes equal cardinality even for infinite sets."
sourceLesson: disc-sets-functions
---

## Infinite sets have different sizes

For infinite sets, no finite count gives their size, so "same size" is defined by pairing them up: two sets have the same cardinality exactly when there is a bijection between them, so their elements pair off one-to-one with nothing left over on either side. This leads to surprises.

A set is **countable** if it is finite or in bijection with ℕ, the natural numbers 0, 1, 2, …: you can list its elements in a sequence that eventually reaches each one. ℤ (the integers) is countable, even though it seems twice as big, because this bijection lists it as 0, 1, −1, 2, −2, …:

```formula
f(n) = (n + 1) / 2   for n = 1, 3, 5, …
f(n) = −n / 2   for n = 0, 2, 4, …
|ℕ| = |ℤ|
where
ℕ: the natural numbers 0, 1, 2, 3, …
ℤ: the integers …, −2, −1, 0, 1, 2, …
f: a bijection from ℕ to ℤ
n: a natural number, the position in the list
f(n): the integer at position n
…: and so on without end
| |: the cardinality: the size of a set
In words: odd positions get the positive integers (1 → 1, 3 → 2, 5 → 3) and even positions get zero and the negatives (0 → 0, 2 → −1, 4 → −2). Every integer appears once and only once, so ℕ and ℤ have the same size.
```

So is ℚ (the fractions), and so is the set of all finite strings over a finite alphabet, which means **the set of all programs is countable**.

**Cantor's diagonal argument** shows that the set of infinite binary sequences (equivalently, the power set of ℕ, or the real numbers) is **not** countable. Suppose you had a complete list of sequences. Build a new sequence d by flipping the i-th bit of the i-th sequence:

```formula
d(i) = 1 − s_i(i)
d(i) ≠ s_i(i)   for every i
where
s_i: the i-th infinite 0/1 sequence in the supposedly complete list (s_1 first, s_2 second, …)
s_i(i): bit number i of sequence s_i: the bits on the diagonal
d: the new sequence being built
d(i): bit number i of d
i: a position, 1, 2, 3, …
≠: is not equal to
In words: d takes the diagonal bit of each listed sequence and flips it (1 − 0 = 1, 1 − 1 = 0), so d disagrees with every listed sequence somewhere and cannot be on the list.
```

```
s1 = 0 1 1 0 1 ...
s2 = 1 1 0 0 0 ...
s3 = 0 0 0 1 1 ...
s4 = 1 0 1 1 0 ...
d  = 1 0 1 0 ...   (flip diagonal)
```

The diagonal bits are 0, 1, 0, 1, so d starts 1, 0, 1, 0. It differs from s1 in position 1, from s2 in position 2, and so on, so it is not on the list, contradicting completeness. More generally, **Cantor's theorem** says every set is strictly smaller than its power set:

```formula
|P(A)| > |A|   for every A
where
A: any set, finite or infinite
P(A): the power set of A, the set of all its subsets
| |: the cardinality: the size of a set
>: is strictly larger than: there is an injection from A into P(A) but no bijection between them
In words: a set always has more subsets than elements. For finite sets this is 2^n > n; for infinite ones it means there is no largest infinity.
```

> [!note] Why CS cares
> Programs are countable but the set of functions from ℕ to {0, 1} (all possible yes/no problems) is not. So almost all problems have no program that solves them. The halting problem, covered in the computability module, is a concrete example built with the same diagonal trick.

## Key takeaways

- A bijection establishes equal cardinality even for infinite sets.
- Diagonalisation constructs an infinite binary sequence missing from any proposed list.

## Further reading

- [Mathematics for Computer Science — MIT](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
- [Cantor's diagonal argument — Wikipedia](https://en.wikipedia.org/wiki/Cantor%27s_diagonal_argument)
- [Mathematics for Computer Science — MIT OpenCourseWare](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-spring-2015/)
