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

The `exactly_one` encoding gives each cell one "at least one" clause plus one "not both" clause per pair of symbols:

```formula
N_clauses = 1 + C(C − 1) / 2
N_clauses = 1 + 4 × 3 / 2 = 7   for C = 4
where
N_clauses: the number of clauses φ_cell uses for one cell
C: the number of possible cell symbols (tape symbols and state markers); a constant fixed by the machine N, not by the input
In words: one clause says "at least one symbol", and each of the C × (C − 1) / 2 pairs of symbols gets a "not both" clause, so the count grows like C squared but never depends on the input.
```

Add it up over the whole grid:

```formula
N_cells = n^k n^k = n^{2k}
N_cells = 100^3 × 100^3 = 10^12
|φ| = O(C^2 n^{2k}) = O(n^{2k})
where
N_cells: the number of cells in an unpadded reference grid; actual start-row and boundary padding preserve the same asymptotic growth
n: the length of the input w, in symbols; 100 in the second line
k: the fixed exponent of N's running time n^k; 3 in the second line
C: the number of possible cell symbols, a constant fixed by N
φ: phi, the Boolean formula the reduction builds
|φ|: the size of the formula φ: how many symbols it takes to write down
O(...): Big O: grows at most as fast as a constant times the expression inside, for large n
In words: every cell contributes a constant amount of formula (its exactly-one clauses plus a constant number of window constraints), so the formula's size is a constant times n^{2k}: a polynomial in n.
```

The second line is the example of a machine running in cubic time (exponent three) on an input of 100 symbols (100 input symbols): a trillion cells. That is enormous, but it is a polynomial, and the formula can be written out mechanically.

A satisfying assignment *is* an accepting computation, read off cell by cell; and an accepting computation gives a satisfying assignment:

```formula
w ∈ L  iff  φ ∈ SAT
where
w: the input to the original problem
L: the NP problem (language) being reduced: the set of inputs whose answer is yes
φ: the Boolean formula built from w
SAT: the set of Boolean formulas that have at least one satisfying assignment
∈: "is a member of"
In words: w is a yes-instance of L exactly when the formula built from it can be satisfied, which is what makes the construction a reduction from L to SAT.
```

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
