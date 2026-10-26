---
id: disc-binomial-lattice-paths
title: "The binomial theorem and lattice paths"
level: intermediate
minutes: 2
summary: "Expanding a two-term power counts which brackets provide each term."
sourceLesson: disc-counting
---

### The binomial theorem

Expanding a product of identical two-term brackets means choosing one term from each bracket. Several choices can produce the same final term; its coefficient counts those choices. The following example uses numbers or commuting algebraic quantities:

```formula essential
(x + y)^3 = x^3 + 3 × x^2 × y
          + 3 × x × y^2 + y^3
where
x, y: any two numbers (or algebraic quantities that commute)
In words: The middle coefficients count which of three brackets supply the different term: three choices give each mixed term.
```

For the cubic example, each mixed term has coefficient three because there are three choices for which bracket supplies the lone different term. Setting both terms to one counts all choices and adds the row of Pascal’s triangle.

### Lattice paths

Consider an unobstructed grid route from the origin to a point four units right and three units up.

Every route has four right moves and three up moves. Choosing the three up-move positions among the seven steps fixes the entire route. This assumes there are no blocked cells and only right/up moves are allowed.

Many dynamic-programming problems ("unique paths") are this binomial coefficient in disguise.

## Key takeaways

- Expanding a two-term power counts which brackets provide each term.
- A shortest grid route is determined by the positions of its up moves.

## Further reading

- [Mathematics for Computer Science — MIT](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
