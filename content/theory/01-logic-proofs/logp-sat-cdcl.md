---
id: logp-sat-cdcl
title: Learning clauses from conflicts
level: advanced
minutes: 3
sourceLesson: logp-sat
summary: A learned clause excludes an inconsistent combination while preserving all original solutions.
---

## CDCL: learning from mistakes

Modern solvers (MiniSat, Glucose, CaDiCaL, Kissat) use **conflict-driven clause learning**. The key ideas:

1. **Clause learning.** When propagation hits a conflict, analyse *which decisions* caused it, and add a new clause forbidding that combination. If deciding x1 true and x7 false always leads to a conflict, learn the clause shown in the block after this list. While retained, the learned clause prevents propagation from accepting that same conflicting combination. Practical solvers can later delete learned clauses.
2. **Non-chronological backjumping.** Instead of undoing only the last decision, standard first-UIP analysis backjumps to the second-highest decision level among literals in its learned clause, or level zero for a unit clause, making that clause assert a literal. This need not be the earliest involved decision.
3. **Decision heuristics** such as VSIDS: prefer variables that have appeared in recent conflicts, so the search concentrates on the hardest part of the problem.
4. **Solver restarts.** Periodically discard decisions while retaining root consequences and useful learned clauses (subject to clause deletion), to escape unlucky early decisions.
5. **Watched literals.** During ordinary propagation, nonunit clauses can watch two literals and avoid scans unless a watched literal becomes false. Unit clauses and other solver phases need separate handling.

The learned clause from point 1 is the negation of the failing combination:

```formula essential
¬(x_1 ∧ ¬x_7) ≡ (¬x_1 ∨ x_7)
where
x_1, x_7: variables 1 and 7 of the formula (written x1, x7 above)
¬: NOT; ¬¬x_7 simplifies to x_7
∧: AND
∨: OR
≡: is logically equivalent to (by De Morgan and double negation)
In words: "not (x1 true and x7 false)" is "x1 false or x7 true": at least one of the two decisions must go the other way.
```

These techniques do not provide a polynomial-time guarantee for general SAT. Standard complete search can still require exponential work; restarting and clause-deletion policies also affect progress. What helps in practice is that real-world formulas often have structure (modules, locality, near-independent parts), and CDCL exploits it. Runtime depends on encoding, solver, hardware and instance structure.

> [!note] Evidence gap
> Universal claims about million-clause solve times or millisecond verification are omitted: no reproducible benchmark set and hardware configuration were supplied.

> [!note] What "unsatisfiable" means here
> Basic CDCL learns resolution consequences. Production solvers may also use preprocessing or stronger transformations, and can emit checkable proof logs such as DRAT. DRAT permits steps beyond ordinary resolution; an independently checked log reduces reliance on the solver, while still depending on the checker and input encoding. Exponential resolution lower bounds for standard pigeonhole encodings do not automatically establish the same limit for every extended solver or encoding.


## Key takeaways
- A learned clause excludes an inconsistent combination while preserving all original solutions.
- Backjumping, heuristics, restarts and watched literals improve practical search without a general polynomial guarantee.

## Further reading
- [CMU lecture: SAT solvers and DPLL](https://www.cs.cmu.edu/~15414/f18/2018/lectures/13-dpll.pdf)
- [2-satisfiability — Wikipedia](https://en.wikipedia.org/wiki/2-satisfiability)
