---
id: cplx-structure-exact-search
title: "Special structure and smarter exact search"
level: intermediate
minutes: 5
summary: "Restricted instances can have polynomial-time exact algorithms."
sourceLesson: cplx-coping
---

Proving a problem NP-hard doesn't make it go away. Airlines still need crew rosters, chip designers still need verified circuits, and delivery firms still need routes. NP-hardness tells you that you can't have all three of these at once, assuming the widely believed conjecture below:

1. **Exact** answers,
2. on **every** input,
3. in **polynomial** time.

The assumption is that P and NP are different: short checkable certificates do not always imply a polynomial-time solving algorithm. This remains unproven.

Every coping strategy gives up one of the three properties. This lesson works through the options, with the guarantees each one does and doesn't give.

## Option 1: your inputs may be a special case

Hard problems often become easy on restricted inputs. Check before anything else.

| Problem | Hard in general | Easy when |
|---|---|---|
| Vertex cover | Any graph | Bipartite (matching) |
| Independent set | Any graph | Trees (DP) |
| SAT | 3-CNF | 2-CNF, Horn |
| Colouring | 3 colours | 2 colours |

More generally, many NP-hard graph problems are solvable in linear time on graphs of bounded **treewidth** (Courcelle's theorem), with constants that grow very fast in the width.

## Option 2: exact, but exponential and smarter

Exponential is not one speed. Take the travelling salesperson problem (TSP) on n cities. For symmetric TSP on at least three cities, brute force fixes a starting city, tries every order of the other n − 1 cities, and halves the count because each closed tour can be driven in two directions. The **Held–Karp** dynamic program (1962) instead builds the best path through every subset of cities, which costs far less:

```formula reference
N_tours = (n − 1)! / 2
T_HK = O(n^2 2^n)
where
N_tours: the number of different closed tours brute force must try
n: the number of cities
!: factorial: m! = m × (m − 1) × … × 2 × 1, the number of ways to put m things in order
T_HK: the number of basic steps Held–Karp takes
O(...): Big O: grows at most as fast as a constant times the expression inside, for large n
2^n: n copies of 2 multiplied together; here, the number of subsets of the n cities
In words: enumerating tours has factorial growth. Held–Karp instead has an exponential subset factor multiplied by a polynomial in the city count. Reusing subproblems improves growth dramatically, but the subset factor remains exponential.
```

The important gain is reuse: many candidate tours share the same “visited cities and last city” subproblem. Held–Karp solves that subproblem once. The number of subsets is still exponential, so the method remains unsuitable for large unrestricted instances. Its asymptotic bound is not a measured operation count.

Industrial exact methods go much further using **branch and bound** and cutting planes: prove a lower bound for a whole region of the search space and skip it if it can't beat the best answer so far. The Concorde TSP solver found and proved the optimal tour for an 85,900-city instance in 2006. MIP solvers for integer programming (Gurobi, CPLEX, HiGHS) combine branching, bounds and cuts. CDCL SAT solvers also search and prune, but use learned logical conflict clauses rather than the same numeric optimisation bounds.

## Key takeaways

- Restricted instances can have polynomial-time exact algorithms.
- Held–Karp replaces factorial enumeration with subset dynamic programming.
- Exact solvers prune search using valid bounds while retaining correctness.

## Further reading

- [Computational Complexity — Arora and Barak](https://theory.cs.princeton.edu/complexity/book.pdf)
