---
id: cx-master-root
sourceLesson: cx-recurrences
title: Master Theorem: root work dominates
level: advanced
minutes: 4
summary: Check regularity and apply the complete three-case shortcut.
---

Here n is the input size. After the leaf-dominated and balanced cases, the final case considers a root whose own work outweighs its children.

## Case 3

**Case 3: f is polynomially larger than n^c**, *and* a **regularity condition** holds. Then the root dominates:

```formula
f(n) = Ω(n^{c + ε})  for some ε > 0
a × f(n / b) ≤ q × f(n),  q < 1
T(n) = Θ(f(n))
where
f(n): the work outside the recursive calls
f(n / b): the work outside the calls in one child call
a: the number of subproblems
b: the shrink factor
n: the input size (the regularity inequality must hold for all large n)
c: the critical exponent, log_b(a)
ε: epsilon, some fixed positive number
q: some fixed constant below 1 (written k in some textbooks)
Ω: Big-Omega, at least a constant times
Θ: Big-Theta, exactly this rate up to constants
T(n): the running time on input size n
≤: less than or equal to
In words: if the root's work beats the leaf count by a fixed power of n, and the children together always do a fixed fraction less work than their parent, the root's own work dominates.
```

The regularity condition says that the work really does shrink from one level to the next. It holds automatically for ordinary polynomial f, such as f(n) = n^2 with a = 2, b = 2 (two children do 2 × (n/2)^2 = n^2 / 2, half the parent's work); it exists to rule out pathological, wildly oscillating functions.

### The simple version

Most recurrences you'll meet have f(n) = Θ(n^d), a plain power of n. Then just compare d with log_b(a):

```formula
T(n) = a × T(n / b) + Θ(n^d)
where
T(n): the running time on input size n
a: the number of subproblems
b: the shrink factor; each subproblem has size n / b
d: the power of n in the outside work, a constant of at least 0 (d = 1 for a linear merge)
n: the input size
Θ: Big-Theta, exactly this rate up to constants
In words: the special case where the work outside the calls is a simple power of n, which covers almost every textbook recurrence.
```

| Compare | Result |
|---|---|
| d < log_b a | Θ(n^(log_b a)) |
| d = log_b a | Θ(n^d log n) |
| d > log_b a | Θ(n^d) |

Equivalently, compare a with b^d: the ratio a / b^d is exactly how fast the work per level grows. Above 1, the leaves win; equal to 1, every level ties; below 1, the root wins.

### Worked examples

In the table, the first column is the right-hand side of T(n) = …, and log_b a is the critical exponent:

| Recurrence | a, b | log_b a | f | Case | T(n) |
|---|---|---|---|---|---|
| T(n/2) + 1 | 1, 2 | 0 | 1 | 2 | log n |
| 2T(n/2) + n | 2, 2 | 1 | n | 2 | n log n |
| 3T(n/2) + n | 3, 2 | 1.585 | n | 1 | n^1.585 |
| 7T(n/2) + n^2 | 7, 2 | 2.807 | n^2 | 1 | n^2.807 |
| 4T(n/2) + n^2 | 4, 2 | 2 | n^2 | 2 | n^2 log n |
| 2T(n/2) + n^2 | 2, 2 | 1 | n^2 | 3 | n^2 |
| T(n/2) + n | 1, 2 | 0 | n | 3 | n |
| 2T(n/2) + n log n | 2, 2 | 1 | n log n | 2, k=1 | n log^2 n |

## Key takeaways
- Polynomially larger outside work dominates only when the regularity condition also holds.
- For ordinary polynomial outside work, comparing exponents gives the familiar three-case shortcut.
- The worked table applies the same conditions to several common recurrences.

## Further reading
- [Master theorem — Wikipedia](https://en.wikipedia.org/wiki/Master_theorem_(analysis_of_algorithms))
- [Erickson: Solving Recurrences](https://jeffe.cs.illinois.edu/teaching/algorithms/notes/99-recurrences.pdf)
