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

**Case 3: outside work is polynomially larger than leaf growth**, *and* a **regularity condition** holds. Then the root dominates:

```formula
f(n) = Ω(n^{c + ε})  for some ε > 0
af(n / b) ≤ qf(n),  q < 1
T(n) = Θ(f(n))
a = 2, b = 2, f(n) = n^2
a f(n/b) = 2(n/2)^2 = n^2/2
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

Regularity means outside work really shrinks down the tree. It holds for ordinary polynomial outside work, such as the example below, where two children together do half the parent’s work. The condition rules out pathological, wildly oscillating functions.

### The simple version

Most textbook recurrences have polynomial outside work. Compare its exponent with the critical exponent, as the three conditions below show:

```formula
T(n) = aT(n / b) + Θ(n^d)
d < log_b(a): T(n) = Θ(n^{log_b(a)})
d = log_b(a): T(n) = Θ(n^d log(n))
d > log_b(a): T(n) = Θ(n^d)
where
T(n): the running time on input size n
a: the number of subproblems
b: the shrink factor; each subproblem has size n / b
d: the power of n in the outside work, a constant of at least 0 (d = 1 for a linear merge)
n: the input size
Θ: Big-Theta, exactly this rate up to constants
log_b: logarithm to base b
log_b(a): the critical exponent
log: the base-2 logarithm
<, >: less than, greater than
In words: the special case where the work outside the calls is a simple power of n, which covers almost every textbook recurrence.
```

| Outside-work exponent | Result |
|---|---|
| Below critical exponent | leaves dominate |
| Equal to critical exponent | add a logarithm |
| Above critical exponent | root dominates |

Equivalently, compare branching with the shrink factor raised to the outside-work exponent. Their ratio determines whether level costs grow, stay equal or shrink:

```formula
R = a / b^d
where
R: the ratio between consecutive level costs
a: the number of recursive subproblems
b: the factor shrinking each input, greater than one
d: the outside-work exponent
In words: Above one, leaves win; at one, levels tie; below one, the root wins.
```

### Worked examples

The following independent recurrence/solution pairs use the parameter values in the table beneath them. Exponents printed as decimals are rounded:

```formula
T(n) = T(n/2) + 1
T(n) = Θ(log(n))
T(n) = 2T(n/2) + n
T(n) = Θ(n log(n))
T(n) = 3T(n/2) + n
T(n) = Θ(n^{log_2(3)})
T(n) = 7T(n/2) + n^2
T(n) = Θ(n^{log_2(7)})
T(n) = 4T(n/2) + n^2
T(n) = Θ(n^2 log(n))
T(n) = 2T(n/2) + n^2
T(n) = Θ(n^2)
T(n) = T(n/2) + n
T(n) = Θ(n)
T(n) = 2T(n/2) + n log(n)
T(n) = Θ(n(log(n))^2)
log_2(3) ≈ 1.585, log_2(7) ≈ 2.807
where
T(n): running time in each independent example
n: the current input size
log, log_2: the base-2 logarithm
Θ: a tight growth bound
≈: approximately equal
In words: Apply the three cases to each pair: matching work adds one log factor, smaller work leaves the leaf exponent, and larger regular work leaves the root cost.
```

| Pair | Children; shrink factor | Critical exponent | Outside work; case |
|---|---|---|---|
| 1 | 1; 2 | 0 | constant; 2 |
| 2 | 2; 2 | 1 | linear; 2 |
| 3 | 3; 2 | about 1.585 | linear; 1 |
| 4 | 7; 2 | about 2.807 | quadratic; 1 |
| 5 | 4; 2 | 2 | quadratic; 2 |
| 6 | 2; 2 | 1 | quadratic; 3 |
| 7 | 1; 2 | 0 | linear; 3 |
| 8 | 2; 2 | 1 | linear times log; 2, log exponent one |

## Key takeaways
- Polynomially larger outside work dominates only when the regularity condition also holds.
- For ordinary polynomial outside work, comparing exponents gives the familiar three-case shortcut.
- The worked table applies the same conditions to several common recurrences.

## Further reading
- [Master theorem — Wikipedia](https://en.wikipedia.org/wiki/Master_theorem_(analysis_of_algorithms))
- [Erickson: Solving Recurrences](https://jeffe.cs.illinois.edu/teaching/algorithms/notes/99-recurrences.pdf)
