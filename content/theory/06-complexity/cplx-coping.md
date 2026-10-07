---
id: cplx-coping
title: Coping with NP-hardness
level: intermediate
minutes: 15
summary: What to do when your problem is NP-hard, with special cases, smarter exponential algorithms, approximation algorithms and their limits (PCP, Unique Games), parameterised algorithms and kernels, and the heuristics and solvers used in industry.
---

Proving a problem NP-hard doesn't make it go away. Airlines still need crew rosters, chip designers still need verified circuits, and delivery firms still need routes. NP-hardness tells you that you can't have all three of these at once (assuming P ≠ NP):

1. **Exact** answers,
2. on **every** input,
3. in **polynomial** time.

Every coping strategy gives up one of them. This lesson works through the options, with the guarantees each one does and doesn't give.

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

Exponential is not one speed. For TSP on n cities, brute force tries (n − 1)!/2 tours. The **Held–Karp** dynamic program (1962) runs in O(n² · 2ⁿ):

| n | (n−1)!/2 | n² · 2ⁿ |
|---|---|---|
| 10 | 181,440 | about 10⁵ |
| 20 | about 6 × 10¹⁶ | about 4 × 10⁸ |
| 30 | about 4 × 10³⁰ | about 10¹² |

Industrial exact solvers go much further using **branch and bound** and cutting planes: prove a lower bound for a whole region of the search space and skip it if it can't beat the best answer so far. The Concorde TSP solver found and proved the optimal tour for an 85,900-city instance in 2006. Integer programming solvers (Gurobi, CPLEX, HiGHS) and CDCL SAT solvers are this idea, industrialised.

## Option 3: approximation algorithms

An algorithm is an **α-approximation** for a minimisation problem if it runs in polynomial time and always returns a solution of cost at most α × OPT. (For maximisation, at least OPT/α, or α × OPT with α < 1, depending on convention.) The guarantee holds on every input, without knowing OPT.

### Vertex cover: a 2-approximation in five lines

Repeatedly take an edge with neither end covered, and add **both** endpoints.

```python
def vc_2approx(edges):
    cover = set()
    for u, v in edges:
        if not ({u, v} & cover):
            cover |= {u, v}
    return cover

path = [(1, 2), (2, 3), (3, 4)]
print(vc_2approx(path))   # {1, 2, 3, 4}
# optimum is {2, 3}: ratio exactly 2
```

Why it's within factor 2: the edges we picked form a **matching** M (no two share a vertex). Any cover, including the optimal one, must contain at least one endpoint of each matched edge, and those endpoints are all different. So OPT ≥ |M|, and our cover has exactly 2|M| ≤ 2 × OPT.

The path example shows the bound is tight: the algorithm picks (1, 2) and (3, 4), four vertices, while {2, 3} covers all three edges. On 300 random small graphs I compared it with brute force; the ratio never exceeded 2.

### A spectrum of approximability

| Problem | Representative guarantee | Known limit (if P ≠ NP) |
|---|---|---|
| Knapsack | 1 + ε, any ε | none (FPTAS) |
| Metric TSP | about 1.5 | about 1.0081 |
| Vertex cover | 2 | √2 (2 if UGC) |
| Set cover | ln n + 1 | (1 − ε) ln n |
| General TSP | none | no constant ratio |
| Clique | n / polylog | n^(1−ε) |

- **Knapsack** has an FPTAS: for any ε > 0, a (1 − ε)-approximate solution in time polynomial in n and 1/ε, by rounding the values and running the pseudo-polynomial DP.
- **Metric TSP** (distances obey the triangle inequality): Christofides' algorithm (1976) gives 1.5. Karlin, Klein and Oveis Gharan's 2020 work gave a randomised expected-cost bound of 1.5 − ε for some ε > 10⁻³⁶; their 2022 work derandomised it. The gain is tiny but significant theoretically.
- **General TSP** has no constant-factor approximation unless P = NP: give graph edges weight 1 and non-edges weight α·n + 1; an α-approximation would then detect Hamiltonian cycles.
- **Greedy set cover** (repeatedly take the set covering most uncovered elements) achieves H(n) ≤ ln n + 1, and doing better than (1 − ε) ln n is NP-hard (Dinur and Steurer, 2014).

### Where the limits come from: PCP

The **PCP theorem** (Arora, Safra, Lund, Motwani, Sudan and Szegedy, 1992) says every NP statement has a proof format that a verifier can check by reading only a **constant number of randomly chosen bits**, catching any false claim with probability at least 1/2. An equivalent form: there is a constant ρ < 1 such that distinguishing satisfiable 3-SAT formulas from those where at most a ρ fraction of clauses can be satisfied is NP-hard.

The sharpest result, Håstad's (2001): for MAX-3SAT with three distinct variables per clause, a uniformly random assignment satisfies 7/8 of clauses in expectation, and achieving 7/8 + ε for any ε > 0 is NP-hard. The trivial algorithm is optimal.

> [!warning] Proven versus conjectured hardness
> The vertex-cover limit of √2 − ε is a theorem conditional only on P ≠ NP (Khot, Minzer and Safra, 2017–18; it improved Dinur and Safra's 1.36). The limit of 2 − ε relies on the **Unique Games Conjecture** (Khot, 2002), which is open. Always check which assumption a hardness-of-approximation result uses.

## Option 4: parameterised algorithms

Sometimes the hardness lives in one small number. A problem is **fixed-parameter tractable (FPT)** in parameter k if it can be solved in f(k) · poly(n) time, where f can be exponential but doesn't depend on n.

### Vertex cover in O(2^k · m)

Any cover must contain u or v for an edge (u, v). Branch on both choices, with budget k − 1 each:

```python
def vc_fpt(edges, k):
    # returns a cover of size <= k, or None
    if not edges:
        return set()
    if k == 0:
        return None
    u, v = edges[0]
    for w in (u, v):
        rest = [e for e in edges
                if w not in e]
        sub = vc_fpt(rest, k - 1)
        if sub is not None:
            return sub | {w}
    return None

print(vc_fpt([(1, 2), (2, 3), (3, 4)], 2))
# {1, 3}: also a minimum cover
print(vc_fpt([(1, 2), (2, 3), (3, 4)], 1))
# None
```

The recursion tree has depth at most k and branching factor 2, so at most 2^k leaves, each doing O(m) work. A 10,000-vertex network with a cover of size 20 has a search-tree bound involving about 2²⁰ ≈ 10⁶ leaves, each with edge-processing costs; practical runtime still requires measurement, while brute force over all C(10,000, 20) subsets is not. Refined branching gets this to about O(1.2738^k + kn) (Chen, Kanj and Xia, 2010).

### Kernelisation

A **kernel** is a polynomial-time shrinking step that leaves an equivalent instance whose size depends only on k. Buss's rule for vertex cover:

1. A vertex with degree greater than k **must** be in any cover of size ≤ k (otherwise all its more-than-k neighbours would be needed). Take it, decrease k.
2. Afterwards, every vertex has degree ≤ k, so k vertices cover at most k² edges. If more than k² edges remain, answer no.

Remove isolated vertices as well. What remains then has at most k² edges and 2k² vertices, regardless of the original n. Kernels are a standard preprocessing step in practical solvers.

### Not everything is FPT

Clique parameterised by solution size is **W[1]-hard**: no f(k) · poly(n) algorithm is believed to exist, and the best known is essentially brute force over n^k subsets (sped up a little with fast matrix multiplication). The **Exponential Time Hypothesis** (Impagliazzo and Paturi, 2001) conjectures that 3-SAT needs 2^Ω(n) time; it implies clique has no f(k) · n^o(k) algorithm. ETH is a conjecture, stronger than P ≠ NP.

## Option 5: heuristics and solvers

Heuristics give up guarantees entirely and often work very well:

- **Local search**: start somewhere, make small improving changes. 2-opt for TSP swaps two edges when that improves the tour. Its quality depends on the initial route and instance; it has no universal few-percent guarantee. **Content gap:** numerical tour-quality and runtime claims are omitted because no reproducible benchmark for the stated inputs was available.
- **Metaheuristics**: simulated annealing, tabu search, genetic algorithms. Tunable, but no worst-case promises.
- **CDCL SAT solvers** (MiniSat, CaDiCaL, Kissat) and **MIP solvers** routinely solve industrial instances with millions of variables, for hardware verification, scheduling and planning.

## Choosing a strategy

1. Look for structure: is it bipartite, a tree, small treewidth, 2-SAT?
2. Is there a small parameter (budget, solution size)? Try FPT and kernels.
3. Need a guarantee on quality? Use an approximation algorithm, and check what the hardness results say is possible.
4. Need optimal answers on real data? Encode for a SAT/MIP solver and measure.
5. Need something good, fast? Heuristics, ideally seeded from an approximation.

## Key takeaways
- NP-hardness rules out exact, all-input, polynomial-time solutions together (if P ≠ NP); each coping strategy relaxes one.
- Exponential algorithms differ hugely: Held–Karp's O(n² · 2ⁿ) versus n! for TSP.
- Vertex cover's matching algorithm is a tight 2-approximation; metric TSP is about 1.5; general TSP has no constant ratio unless P = NP.
- The PCP theorem underlies hardness of approximation; Håstad shows 7/8 is optimal for MAX-3SAT. Some limits (vertex cover 2 − ε) rely on the unproven Unique Games Conjecture.
- FPT algorithms confine the exponential to a parameter: vertex cover in O(2^k · m), with a k²-edge kernel. Clique is W[1]-hard.

## Further reading
- [Approximation algorithm — Wikipedia](https://en.wikipedia.org/wiki/Approximation_algorithm)
- [Hardness of approximation — Wikipedia](https://en.wikipedia.org/wiki/Hardness_of_approximation)
- [PCP theorem — Wikipedia](https://en.wikipedia.org/wiki/PCP_theorem)
- [Parameterized complexity — Wikipedia](https://en.wikipedia.org/wiki/Parameterized_complexity)
- [Kernelization — Wikipedia](https://en.wikipedia.org/wiki/Kernelization)
- [Christofides algorithm — Wikipedia](https://en.wikipedia.org/wiki/Christofides_algorithm)
- [Unique games conjecture — Wikipedia](https://en.wikipedia.org/wiki/Unique_games_conjecture)
- [Held–Karp algorithm — Wikipedia](https://en.wikipedia.org/wiki/Held%E2%80%93Karp_algorithm)
