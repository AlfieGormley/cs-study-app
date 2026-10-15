---
id: cplx-cook-levin-tableau
title: "Encoding a computation as SAT"
level: intermediate
minutes: 4
summary: "Cook–Levin proves SAT NP-complete by encoding accepting computations."
sourceLesson: cplx-np-completeness
---

## The Cook–Levin theorem

**Theorem (Cook 1971; Levin independently, published 1973).** SAT, deciding whether a Boolean formula has a satisfying assignment, is NP-complete.

SAT is in NP: the assignment is the certificate. The hard part is showing every NP problem reduces to SAT. We can't know each problem in advance, so the proof works from the only thing they share: a nondeterministic Turing machine N that decides L within a polynomial number of steps.

### The tableau

An accepting run of N on an input w is a sequence of configurations (snapshots of the state, head position and tape), one per step. Write them as the rows of a square grid, the **tableau**. Each cell holds one symbol: a tape symbol, or a state marker showing where the head is.

```formula
N_rows = O(n^k)
N_cols = O(n^k)
where
N_rows: the number of rows of the tableau: one per step (configuration) of the run
N_cols: the number of columns: tape cells the run can touch, since in n^k steps the head can visit at most n^k cells
n: the length of the input w, in symbols
k: the fixed exponent of N's polynomial running time n^k; a constant set by the machine, not by the input
O(...): Big O, an upper bound up to a fixed factor for sufficiently large n
In words: allowing the initial configuration, boundary markers and input cells changes only constant factors: a run of at most n^k steps fits in a grid with both dimensions O(n^k), assuming the time bound is at least the input length. For a machine running in n^3 steps on a 100-symbol input, the unpadded reference dimensions are 1,000,000 rows by 1,000,000 columns, with the actual tableau allowing the extra rows and boundary cells.
```

```
       cell 1  2  3  4  5 ...
row 1   # q0 w1 w2 w3  _ ... #  start
row 2   #  a q3 w2 w3  _ ... #
row 3   #  a  b q7 w3  _ ... #
 ...
row t   #  .  . qacc   ...   #  accept
```

The formula has one Boolean variable per (cell, symbol) pair, and is the AND of four parts:

```formula
x_{i,j,s} = 1  iff  T_{i,j} = s
φ = φ_cell ∧ φ_start ∧ φ_accept ∧ φ_move
where
x_{i,j,s}: a Boolean variable, one for each cell and each possible symbol; 1 means true, 0 means false
T_{i,j}: the symbol written in the tableau cell at row i, column j
i: the row number (the time step), from 1 up to n^k
j: the column number (the tape cell), from 1 up to n^k
s: one symbol from the fixed set of possible cell symbols (tape symbols and state markers)
φ: phi, the whole Boolean formula the reduction outputs
φ_cell, φ_start, φ_accept, φ_move: the four parts of φ, described in the list below
∧: AND: φ is true only when all four parts are true
In words: x_{i,j,s} says "cell (i, j) holds symbol s", and φ is true exactly when the variables describe a legal accepting run.
```

- **φ_cell**: every cell holds exactly one symbol.
- **φ_start**: row 1 is the start configuration on w.
- **φ_accept**: the accept state appears somewhere.
- **φ_move**: every 2 × 3 **window** of adjacent cells is consistent with N's transition function. Because a Turing machine changes only the cells around its head in one step, checking all these small local windows is enough to guarantee that each row legally follows from the one before.

Here is how φ_cell is built for one cell, as CNF clauses over integer-named variables (positive means the variable, negative its negation):

```python
from itertools import combinations

def exactly_one(vs):
    # at least one symbol in the cell
    clauses = [list(vs)]
    # no two symbols at once
    for a, b in combinations(vs, 2):
        clauses.append([-a, -b])
    return clauses

print(exactly_one([1, 2, 3]))
# [[1, 2, 3], [-1, -2], [-1, -3], [-2, -3]]
```

## Key takeaways

- Cook–Levin proves SAT NP-complete by encoding accepting computations.
- Tableau cells encode symbols and machine state through Boolean variables.
- Exactly-one constraints and local transition windows describe legal runs.

## Further reading

- [Computational Complexity — Arora and Barak](https://theory.cs.princeton.edu/complexity/book.pdf)
- [Theory of Computation — MIT OpenCourseWare](https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/)
