---
id: logp-sat-applications
title: SAT encodings, workloads and real uses
level: advanced
minutes: 3
sourceLesson: logp-sat
summary: Encoding and instance structure matter more than raw variable count for predicting runtime.
---

## Hard and easy instances

Random-instance experiments must specify the clause distribution, number of variables and solver. Clause density can correlate with satisfiability and observed difficulty in such experiments; it does not determine whether an individual formula is easy. Industrial formulas have different structure.

> [!note] Evidence gap
> The previous universal density cutoff and easy/hard classifications are omitted because they conflated a model-dependent approximate threshold with a theorem and a runtime guarantee.


## Where SAT is used

- **Hardware verification**: equivalence checking and bounded model checking of chip designs, a major driver of solver research.
- **Package managers**: dependency resolution with version constraints is NP-complete in general. libsolv (used by openSUSE's zypper and Fedora's DNF) and SAT4J (in Eclipse's p2 installer) treat it as a SAT problem.
- **SMT solvers** (Satisfiability Modulo Theories) such as Z3 and cvc5 extend SAT with integers, arrays and bit-vectors. They are the engines inside Dafny, symbolic execution tools, and AWS's Zelkova, which reasons about IAM policy rules.
- **Planning, scheduling and test generation**: encode "find a schedule" or "find an input reaching this branch" as constraints.

> [!tip] Using a solver in practice
> You rarely write DPLL yourself. Encode the problem, hand it to a solver (Python bindings exist for most), and spend your effort on the encoding. Sound symmetry-breaking constraints may reduce search. For unconstrained graph colouring with interchangeable colours, fixing one vertex to red preserves satisfiability; precolouring or other colour-specific constraints can invalidate that symmetry. Measure the effect on the actual workload.


A small package example shows the importance of decoding a solution. Suppose installing an application requires packages A and D. Package A needs either version B2 or package C, while B2 conflicts with D. Installing D rules out B2, so satisfying A’s dependency forces C. The solver can find that combination by propagation; it is still the package manager’s responsibility to encode version ranges, conflicts and user requests correctly. A solver proves properties of its clauses, so missing a real dependency from the encoding can produce a mathematically valid answer that is unusable as an installation plan.

## Key takeaways
- Encoding and instance structure matter more than raw variable count for predicting runtime.
- An unsatisfiable answer proves the encoded constraints have no solution; trust also depends on encoding and proof checking.

## Further reading
- [CMU lecture: SAT solvers and DPLL](https://www.cs.cmu.edu/~15414/f18/2018/lectures/13-dpll.pdf)
- [Cook–Levin theorem — Wikipedia](https://en.wikipedia.org/wiki/Cook%E2%80%93Levin_theorem)
