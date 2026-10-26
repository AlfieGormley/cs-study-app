---
id: cplx-cook-levin-size
title: "Why the tableau stays polynomial"
level: intermediate
minutes: 4
summary: "A polynomial-time run occupies a tableau of polynomial area."
sourceLesson: cplx-np-completeness
---

Continue the Cook–Levin encoding: each cell in a time-by-tape tableau has a fixed finite choice of symbols, represented by Boolean variables. The machine is fixed while its input grows. Exactly-one clauses and local transition checks enforce a legal accepting run.

### Why it's a polynomial reduction

The `exactly_one` encoding adds an at-least-one clause and forbids every pair of symbols from coexisting. The alphabet and machine rules are fixed, so this is a constant amount of work per cell as the input grows.

Add it up over the whole grid:

```formula essential
N_cells = O(n^{2k})
|φ| = O(C^2 n^{2k}) = O(n^{2k})
where
N_cells: the number of tableau cells, including start-row and boundary padding
n: the input length, in symbols
k: the fixed exponent of the machine's polynomial time bound
C: the number of possible cell symbols, a constant fixed by the machine
φ: phi, the Boolean formula the reduction builds
|φ|: the size of the formula φ: how many symbols it takes to write down
O(...): Big O: grows at most as fast as a constant times the expression inside, for large n
In words: each grid dimension is bounded by the polynomial runtime, so their product is still polynomial. A fixed amount of local formula per cell preserves that polynomial size bound.
```

Squaring a polynomial bound keeps it polynomial. This is a validity argument for the reduction, not a claim that materialising the tableau is an efficient practical SAT encoding.

A satisfying assignment *is* an accepting computation, read off cell by cell; and an accepting computation gives a satisfying assignment. Thus the input is accepted exactly when the constructed SAT instance is satisfiable.

> [!note] What the nondeterminism becomes
> N's guesses turn into the freedom the SAT solver has in choosing variable values. The formula is fixed; the "guessing" is the existential "is there an assignment?".

The formula-size counts use atomic Boolean variables and clauses. If every variable identifier is written explicitly in binary, identifier lengths can add a logarithmic factor to the bit length. The construction remains polynomial under either reasonable encoding.

## Key takeaways

- A polynomial-time run occupies a tableau of polynomial area.
- The machine’s alphabet and local rules are fixed constants.
- Satisfying assignments correspond to accepting runs in both directions.

## Further reading

- [Computational Complexity — Arora and Barak](https://theory.cs.princeton.edu/complexity/book.pdf)
- [Theory of Computation — MIT OpenCourseWare](https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/)
