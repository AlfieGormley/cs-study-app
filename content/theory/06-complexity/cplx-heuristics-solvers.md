---
id: cplx-heuristics-solvers
title: "Choosing heuristics and measuring solvers"
level: intermediate
minutes: 3
summary: "Local search and metaheuristics trade universal quality promises for measured performance."
sourceLesson: cplx-coping
---

## Option 5: heuristics and solvers

Heuristics generally give up a universal quality guarantee and must be measured on the intended workload:

- **Local search**: start somewhere, make small improving changes. 2-opt for TSP swaps two edges when that improves the tour. Its quality depends on the initial route and instance; it has no universal few-percent guarantee.
- **Metaheuristics**: simulated annealing, tabu search, genetic algorithms. Tunable, but the label alone gives no polynomial-time worst-case quality guarantee.
- **CDCL SAT solvers** (MiniSat, CaDiCaL, Kissat) and **MIP solvers** solve many large industrial instances for hardware verification, scheduling and planning; measure them on the intended workload.

## Choosing a strategy

1. Look for structure: is it bipartite, a tree, small treewidth, 2-SAT?
2. Is there a small parameter (budget, solution size)? Try FPT and problem kernels.
3. Need a guarantee on quality? Use an approximation algorithm, and check what the hardness results say is possible.
4. Need optimal answers on real data? Encode for a SAT/MIP solver and measure.
5. Need something good, fast? Heuristics, ideally seeded from an approximation.

For a delivery deadline, benchmark a construction such as nearest neighbour or a savings method, then improve it using 2-opt, Or-opt or guided local search. OR-Tools supplies routing machinery for such experiments. A valid relaxation can provide a lower bound: a route costing 1,050 kilometres against a positive lower bound of 1,000 kilometres is at most five percent above the optimum. The actual optimum may lie between the bound and the route cost. A solver’s reported gap depends on its convention, so state the denominator. No universal tour-quality or runtime percentage follows without a reproducible benchmark.

## Key takeaways

- Local search and metaheuristics trade universal quality promises for measured performance.
- Exact SAT and MIP solvers remain useful on structured inputs.
- Choose a strategy from structure, parameters, quality requirements and deadlines.

## Further reading

- [Computational Complexity — Arora and Barak](https://theory.cs.princeton.edu/complexity/book.pdf)
