---
id: disc-binomial-lattice-paths
title: "The binomial theorem and lattice paths"
level: intermediate
minutes: 3
summary: "Expanding a two-term power counts which brackets provide each term."
sourceLesson: disc-counting
---

### The binomial theorem

Binomial coefficients get their name from expanding a power of a two-term sum such as x + y. Expanding (x + y)ⁿ means picking either x or y from each of the n brackets and multiplying; the number of ways to pick x exactly k times is C(n, k).

```formula
(x + y)^n = Σ C(n, k) × x^k × y^{n−k}
(x + y)^3 = x^3 + 3 × x^2 × y
          + 3 × x × y^2 + y^3
where
x, y: any two numbers (or algebraic quantities that commute)
n: the power, a whole number 0 or more
k: the number of brackets from which x is picked, running from 0 to n
C(n, k): the number of ways to choose those k brackets ("n choose k")
Σ: sigma, "sum of": add up the term after it for every whole number k from 0 to n
x^k, y^{n−k}: k copies of x multiplied together, y multiplied by itself n − k times
In words: the coefficient of the term with k copies of x is the number of ways to choose which k brackets supply them. For n = 3 the coefficients are 1, 3, 3, 1, the fourth row of Pascal's triangle.
```

Substituting 1 for both x and y makes the left side 2ⁿ and the right side the sum of the row, which recovers the row-sum fact above.

### Lattice paths

How many shortest paths are there on a grid from (0, 0) to (4, 3), moving only right (R) or up (U)? Every path is a string of 4 Rs and 3 Us, and choosing which 3 of the 7 positions are Us fixes it:

```formula
N_path = C(7, 3) = (7 × 6 × 5) / 3!
N_path = 210 / 6 = 35
where
N_path: the number of shortest grid paths from (0, 0) to (4, 3)
C(7, 3): the number of ways to choose 3 of the 7 moves to be up-moves ("7 choose 3")
!: factorial: 3! = 3 × 2 × 1 = 6
In words: a path is fixed by deciding which 3 of its 7 moves go up, so there are 35 paths.
```

Many dynamic-programming problems ("unique paths") are this binomial coefficient in disguise.

## Key takeaways

- Expanding a two-term power counts which brackets provide each term.
- A shortest grid route is determined by the positions of its up moves.

## Further reading

- [Mathematics for Computer Science — MIT](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
