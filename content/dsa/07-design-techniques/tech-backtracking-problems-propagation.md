---
id: tech-backtracking-problems-propagation
title: Propagation, exact cover and SAT
level: advanced
minutes: 3
sourceLesson: tech-backtracking-problems
summary: Naked and hidden singles eliminate candidates before guessing.
---

The previous Sudoku unit chose the cell with the smallest candidate set. Propagation removes impossible values and makes forced assignments before branching. The examples below distinguish these deductions from variable ordering and explain how wider solver frameworks encode constraints.

### Constraint propagation

MRV picks good cells; **propagation** goes further by deducing values before guessing. Peter Norvig's well-known solver keeps a set of possible digits for every cell and applies two rules repeatedly:

1. **Naked single**: if a cell has only one possible digit, assign it and remove that digit from all its 20 peers.
2. **Hidden single**: if a digit has only one possible cell in a row, column or box, it must go there.

Each assignment can trigger more eliminations, which trigger more assignments. Many easy puzzles are solved by propagation alone, with no search at all. When propagation stalls, the solver picks the MRV cell, guesses, propagates again, and backtracks if any cell's set becomes empty.

> [!analogy] Real-world analogy: filling in a crossword
> Writing in one answer fixes letters in every answer that crosses it. Those letters often leave only one possible word for a crossing clue, which fixes more letters, and so on. You only start guessing when no clue is forced any more.
>
> **How it maps:** each crossword entry is a variable, the dictionary words that still fit are its domain, and crossing squares are constraints. Writing in an answer and updating the crossing entries is propagation; an entry with exactly one fitting word is a naked single.
>
> **Where it stops:** a person solving a crossword can rub out answers in any order. A propagating solver must record every elimination it made after a guess so it can restore exactly those candidates when the guess fails.

## Constraint propagation in general

All of this generalises to CSPs: variables, domains and constraints. Solvers combine backtracking with:

| Technique | Idea |
|---|---|
| MRV | Branch on the smallest domain |
| Degree heuristic | Tie-break by most constraints |
| Least constraining value | Try values that leave neighbours most options |
| Forward checking | After assigning, prune neighbours' domains; fail if one empties |
| Arc consistency (AC-3) | For binary constraints, retain a value only if it has support in each constrained neighbour |

**Forward checking** looks one step ahead. **Arc consistency** propagates further: removing a value from one domain can remove values from others, and so on, until nothing changes. Propagation has a per-node cost and can reduce the search tree; whether it improves running time depends on the instance and implementation.

**Exact cover** is the problem of choosing rows of a 0/1 table so that every column has exactly one 1 among the chosen rows. Sudoku fits it directly: each row of the table is one possible (cell, digit) placement, 81 cells times 9 digits = 729 rows, and each column is one rule that must be satisfied exactly once. There are four kinds of rule with 81 of each: every cell is filled, and every digit appears once in every row, once in every column and once in every box, giving 324 columns before the givens remove candidates.

Knuth’s **Algorithm X** can be implemented with **dancing links** (DLX): restoring an individual removed link/node takes O(1), while undoing a whole choice may restore many nodes. N-Queens uses exactly-one row/column constraints and **at-most-one diagonal** constraints, so the direct formulation needs optional secondary columns (generalised exact cover) or another encoding.

**SAT solvers.** The DPLL algorithm is backtracking plus **unit propagation** (an unsatisfied clause with one unassigned literal and all others false forces it). Modern CDCL solvers add clause learning and non-chronological backjumping, and can solve substantial structured instances; size alone does not determine difficulty. They power hardware verification, scheduling and package managers: libsolv (used by DNF and by conda's libmamba solver) resolves dependencies with SAT techniques, while pip's resolver backtracks over candidate versions.

## Key takeaways
- Naked and hidden singles eliminate candidates before guessing.
- Forward checking, arc consistency, exact cover and SAT organise constraints differently.

## Further reading
- [Peter Norvig: Solving Every Sudoku Puzzle](https://norvig.com/sudoku.html)
- [Knuth: Dancing Links](https://arxiv.org/pdf/cs/0011047)
- [CSP ordering and propagation — Berkeley notes](https://berkeleyai.github.io/cs188-website/assets/notes/n2.pdf)
