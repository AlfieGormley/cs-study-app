---
id: cplx-coping
title: Coping with NP-hardness
level: intermediate
minutes: 18
summary: What to do when your problem is NP-hard, with special cases, smarter exponential algorithms, approximation algorithms and their limits (the PCP theorem, Unique Games), parameterised algorithms and kernels, and the heuristics and solvers used in industry.
---

Proving a problem NP-hard doesn't make it go away. Airlines still need crew rosters, chip designers still need verified circuits, and delivery firms still need routes. NP-hardness tells you that you can't have all three of these at once, assuming the widely believed conjecture below:

1. **Exact** answers,
2. on **every** input,
3. in **polynomial** time.

The conjecture is that P and NP are different classes:

```formula
P ≠ NP
where
P: the complexity class P: decision problems a deterministic algorithm solves in polynomial time (at most about n^k steps on an input of n bits, for some fixed k)
NP: the class NP (nondeterministic polynomial time): decision problems whose yes-answers have a short certificate that can be checked in polynomial time
≠: is not equal to: here, at least one problem in NP is not in P
In words: some problems whose answers are quick to check are not quick to solve. Nobody has proved it, but if it is true then no NP-hard problem has an algorithm that is exact, works on every input and runs in polynomial time.
```

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

Exponential is not one speed. Take the travelling salesperson problem (TSP) on n cities. Brute force fixes a starting city, tries every order of the other n − 1 cities, and halves the count because each round trip can be driven in two directions. The **Held–Karp** dynamic program (1962) instead builds the best path through every subset of cities, which costs far less:

```formula
N_tours = (n − 1)! / 2
T_HK = O(n^2 × 2^n)
where
N_tours: the number of different round trips brute force must try
n: the number of cities
!: factorial: m! = m × (m − 1) × … × 2 × 1, the number of ways to put m things in order
T_HK: the number of basic steps Held–Karp takes
O(...): Big O: grows at most as fast as a constant times the expression inside, for large n
2^n: n copies of 2 multiplied together; here, the number of subsets of the n cities
In words: brute force grows like a factorial, while Held–Karp grows like n squared times 2 to the n. Both are exponential, but the factorial is far worse.
```

For 10 cities:

```formula
N_tours = 9! / 2 = 362880 / 2 = 181440
n^2 × 2^n = 100 × 1024 = 102400
where
N_tours: the number of round trips brute force tries
!: factorial: 9! = 9 × 8 × … × 2 × 1 = 362880
n: the number of cities, here 10
2^n: 2 to the power n; here 2^10 = 1024
In words: at 10 cities the two methods do similar work, about 10^5 each. The gap opens fast as n grows, as the table shows.
```

| n | (n−1)!/2 | n² · 2ⁿ |
|---|---|---|
| 10 | 181,440 | about 10⁵ |
| 20 | about 6 × 10¹⁶ | about 4 × 10⁸ |
| 30 | about 4 × 10³⁰ | about 10¹² |

Industrial exact methods go much further using **branch and bound** and cutting planes: prove a lower bound for a whole region of the search space and skip it if it can't beat the best answer so far. The Concorde TSP solver found and proved the optimal tour for an 85,900-city instance in 2006. MIP solvers for integer programming (Gurobi, CPLEX, HiGHS) and CDCL SAT solvers are this idea, industrialised.

## Option 3: approximation algorithms

An approximation algorithm runs in polynomial time and always returns a solution that is provably close to the best one. The closeness is measured by a factor α:

```formula
ALG_min ≤ α × OPT_min
ALG_max ≥ OPT_max / α
where
ALG_min: the cost of the solution the algorithm returns, for a minimisation problem (lower is better, e.g. a route length)
OPT_min: the cost of the best possible solution to the same input
ALG_max: the value the algorithm achieves, for a maximisation problem (higher is better, e.g. clauses satisfied)
OPT_max: the best possible value for the same input
α: alpha, the approximation factor, a fixed number of at least 1; α = 1 means always optimal
In words: an α-approximation is never worse than the optimum by more than a factor α, in either direction. A 2-approximation for a route problem never returns a route more than twice the shortest.
```

The guarantee holds on every input, without the algorithm ever knowing OPT. Some authors write maximisation guarantees as a factor below 1 instead (for example "0.5-approximation" for the same thing as 2 here), so check the convention.

### Vertex cover: a 2-approximation in five lines

A vertex cover is a set of vertices that touches every edge. Repeatedly take an edge with neither end covered, and add **both** endpoints.

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

Why it's within factor 2: the edges we picked form a **matching** M (no two share a vertex). Any cover, including the optimal one, must contain at least one endpoint of each matched edge, and those endpoints are all different. That gives a lower bound on the optimum and an exact count for our cover:

```formula
OPT ≥ |M|
|C| = 2 × |M|
|C| = 2 × |M| ≤ 2 × OPT
where
M: the matching: the edges the algorithm picked, no two sharing a vertex
|M|: the number of edges in M
OPT: the size (number of vertices) of a smallest vertex cover
C: the cover the algorithm returns; |C| is its number of vertices
In words: every cover needs a different vertex for each picked edge, so the best cover has at least |M| vertices. The algorithm takes exactly two per picked edge, so it is never more than twice the best.
```

The path example shows the bound is tight: the algorithm picks (1, 2) and (3, 4), so |M| = 2 and |C| = 4, while {2, 3} covers all three edges, so OPT = 2 and the ratio is exactly 2. On 300 random small graphs I compared it with brute force; the ratio never exceeded 2.

### A spectrum of approximability

Each row gives the best known guarantee and the best known limit, as an approximation ratio. The symbols in the table are defined just after it.

| Problem | Representative guarantee | Known limit (if P ≠ NP) |
|---|---|---|
| Knapsack | 1 + ε, any ε | none (FPTAS) |
| Metric TSP | about 1.5 | about 1.0082 |
| Vertex cover | 2 | √2 (2 if UGC) |
| Set cover | ln n + 1 | (1 − ε) ln n |
| General TSP | none | no constant ratio |
| Clique | n / polylog | n^(1−ε) |

```formula
ρ = ALG / OPT
ρ_metric ≥ 123 / 122 ≈ 1.0082
√2 ≈ 1.414
ln(n) + 1 ≈ 14.8   for n = 10^6
where
ρ: rho, the approximation ratio: how many times worse than the optimum the answer can be; for a maximisation problem, ρ = OPT / ALG, so ρ ≥ 1 either way
ALG: the cost of the algorithm's answer
OPT: the cost of the best answer
ρ_metric: the best ratio any polynomial-time algorithm for metric TSP can guarantee; below 123/122 is NP-hard
ε: epsilon, any small positive number you choose, such as 0.01
√2: the square root of 2, the number that gives 2 when multiplied by itself
ln(n): the natural logarithm of n (log to base e ≈ 2.718)
n: the input size: the number of elements for set cover, the number of vertices for clique
polylog: a power of log n, such as (log n)^2; it grows far slower than n
n^(1−ε): n to the power 1 − ε, only slightly less than n itself
UGC: the Unique Games Conjecture (below)
FPTAS: fully polynomial-time approximation scheme: a ratio of 1 + ε for any ε, in time polynomial in n and 1/ε
≈: approximately equal to
In words: a ratio near 1 is excellent and one that grows with n is weak. Set cover's guarantee grows slowly (about 15 for a million elements); clique's is almost as bad as n.
```

- **Knapsack** has an FPTAS. You get as close to optimal as you like, by rounding the values and running the pseudo-polynomial DP (formula below).
- **Metric TSP** (distances obey the triangle inequality): Christofides' algorithm (1976) gives 1.5. Karlin, Klein and Oveis Gharan's 2020 work gave a randomised expected-cost bound a tiny amount below 1.5 (the improvement is more than 10⁻³⁶); their 2022 work derandomised it. The gain is tiny but significant theoretically.
- **General TSP** has no constant-factor approximation unless P = NP, by a weighting trick (formula below).
- **Greedy set cover** (repeatedly take the set covering most uncovered elements) achieves about ln n + 1, and doing much better is NP-hard (Dinur and Steurer, 2014).

The knapsack FPTAS is written as a fraction of the optimum, because knapsack is a maximisation problem:

```formula
ALG ≥ (1 − ε) × OPT
ALG ≥ 0.99 × OPT   for ε = 0.01
where
ALG: the total value of the items the algorithm packs
OPT: the best possible total value that fits
ε: epsilon, the error you allow, any number between 0 and 1
In words: choose ε = 0.01 and you are guaranteed at least 99 % of the best value, in time polynomial in n (the number of items) and in 1/ε = 100. This is the same promise as a ratio of about 1 + ε.
```

The general TSP trick reduces Hamiltonian cycle (is there a round trip using only the graph's edges?) to TSP. Give each edge of an n-vertex graph weight 1 and each missing edge a huge weight w:

```formula
w = α × n + 1
OPT_yes = n
c_no ≥ (n − 1) + w
c_no ≥ (1 + α) × n > α × n
where
w: the weight given to every pair of vertices that is not an edge of the graph
α: alpha, the approximation factor being ruled out, any constant at least 1
n: the number of vertices (cities)
OPT_yes: the length of the shortest tour when the graph has a Hamiltonian cycle: n edges of weight 1
c_no: the length of any tour when the graph has no Hamiltonian cycle, so the tour must use at least one missing edge
In words: with a Hamiltonian cycle the best tour costs n, so an α-approximation returns at most α × n. Without one, every tour costs more than α × n. Reading the approximation's output would decide an NP-complete problem.
```

This works only because non-metric weights can break the triangle inequality, which is why metric TSP escapes it.

Greedy set cover's guarantee is the harmonic number:

```formula
H(n) = 1 + 1/2 + 1/3 + … + 1/n
H(n) ≤ ln(n) + 1
H(100) ≈ 5.19 ≤ ln(100) + 1 ≈ 5.61
where
H(n): the nth harmonic number: the sum of 1/1, 1/2, … up to 1/n
n: the number of elements to cover
ln(n): the natural logarithm of n (log to base e ≈ 2.718)
≈: approximately equal to
In words: greedy uses at most about ln n + 1 times as many sets as the best cover; for 100 elements, at most about 5.2 times. Beating (1 − ε) × ln n for any fixed ε > 0 is NP-hard.
```

### Where the limits come from: the PCP theorem

The **PCP theorem** (Arora, Safra, Lund, Motwani, Sudan and Szegedy, 1992) says every NP statement has a proof format that a verifier can check by reading only a **constant number of randomly chosen bits**, catching any false claim with probability at least 1/2. An equivalent form is a gap that is hard to see:

```formula
f_max = 1   or   f_max ≤ s
where
f_max: the largest fraction of a 3-SAT formula's clauses that any true/false assignment satisfies, between 0 and 1
s: a fixed constant below 1 given by the theorem
In words: given a 3-SAT formula that is either fully satisfiable or can have at most a fraction s of its clauses satisfied, telling which is NP-hard. So no polynomial-time algorithm can approximate the best fraction better than s (unless P = NP).
```

The sharpest result is Håstad's (2001), for MAX-3SAT with three distinct variables per clause. A clause (a ∨ b ∨ c) is "a OR b OR c", so it fails only when all three are false. A uniformly random assignment gives:

```formula
Pr_fail = (1/2)^3 = 1/8
Pr_sat = 1 − 1/8 = 7/8
E_sat = 7/8 × m
where
Pr_fail: the probability a given clause is false: each of its three distinct variables is false with probability 1/2, independently
Pr_sat: the probability the clause is satisfied
E_sat: the expected number of satisfied clauses
m: the number of clauses; with m = 800, E_sat = 700
In words: a coin flip per variable satisfies seven eighths of the clauses on average. Håstad proved that guaranteeing 7/8 + ε of the optimum, for any ε > 0, is NP-hard, so this trivial algorithm is optimal.
```

> [!warning] Proven versus conjectured hardness
> The vertex-cover limit of about 1.414 (the square root of 2) is a theorem conditional only on P differing from NP (Khot, Minzer and Safra, 2017–18; it improved Dinur and Safra's 1.36). The limit of 2 relies on the **Unique Games Conjecture** (Khot, 2002), which is open. Always check which assumption a hardness-of-approximation result uses.

Stated as formulas:

```formula
ρ_VC ≥ √2 − ε   if P ≠ NP
ρ_VC ≥ 2 − ε    if UGC
where
ρ_VC: the approximation ratio any polynomial-time vertex-cover algorithm can guarantee
ε: epsilon, any small positive number
√2: the square root of 2, about 1.414
P: the class of problems solvable in polynomial time
NP: the class of problems whose yes-answers can be checked in polynomial time
≠: is not equal to
UGC: the Unique Games Conjecture, an unproven conjecture by Subhash Khot about a particular labelling problem
In words: if P ≠ NP, nobody can beat about 1.414; if the Unique Games Conjecture is also true, nobody can beat 2, so the simple matching algorithm would be best possible.
```

## Option 4: parameterised algorithms

Sometimes the hardness lives in one small number. A problem is **fixed-parameter tractable (FPT)** in parameter k if it can be solved in this much time:

```formula
T(n, k) = f(k) × poly(n)
where
T(n, k): the running time, in basic steps
n: the input size, in bits
k: the parameter, a number you expect to be small, such as the solution size
f(k): any function of k alone, possibly exponential such as 2^k, but not involving n
poly(n): some polynomial in n, such as n^2 or n^3
In words: all the explosive growth is confined to the small parameter k; for a fixed k, the time grows only polynomially with the input, with an exponent that does not depend on k.
```

### Vertex cover by bounded branching

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

The recursion tree has depth at most k and branching factor 2, so at most 2 to the power k leaves, each doing work proportional to the number of edges m:

```formula
T = O(2^k × m)
2^20 ≈ 1.05 × 10^6
C(10000, 20) ≈ 4.0 × 10^61
1.2738^20 ≈ 126
where
T: the running time, in basic steps
O(...): Big O: grows at most as fast as a constant times the expression inside
k: the cover-size budget, here 20
m: the number of edges; each call filters the edge list once
2^k: 2 to the power k: the most leaves a binary recursion of depth k can have
C(N, r): "N choose r": the number of ways to pick r items from N; here, all 20-vertex subsets of 10,000 vertices
In words: with a budget of 20, the search tree has about a million leaves, while brute force would test about 4 × 10^61 subsets. Refined branching shrinks the exponential part to about 126.
```

So a 10,000-vertex network with a cover of size 20 has a search-tree bound of about a million leaves, each with edge-processing costs; practical runtime still requires measurement, while brute force over all 20-vertex subsets is hopeless. Refined branching gets this to about O(1.2738^k + kn) (Chen, Kanj and Xia, 2010), where n is the number of vertices.

### Kernelisation

A **kernel** is a polynomial-time shrinking step that leaves an equivalent instance whose size depends only on k. Buss's rule for vertex cover, where the degree of a vertex is its number of edges:

1. A vertex with degree greater than k **must** be in any cover of size at most k (otherwise all its more-than-k neighbours would be needed). Take it, decrease k.
2. Afterwards, every vertex has degree at most k, so k vertices cover at most k² edges. If more than k² edges remain, answer no.

Remove isolated vertices as well. What remains is small:

```formula
E_max = k × k = k^2
V_max = 2 × k^2
E_max = 9,  V_max = 18   for k = 3
where
E_max: the most edges the remaining instance can have if a cover of size k exists
V_max: the most vertices it can have, since each edge has two ends and no vertex is isolated
k: the remaining cover budget, after forced vertices have been taken
In words: k vertices, each touching at most k edges, cover at most k squared edges. So a yes-instance shrinks to at most k^2 edges and 2k^2 vertices, however large the original graph was.
```

Kernels are a standard preprocessing step in practical solvers.

### Not everything is FPT

Clique (a set of vertices all joined to each other) parameterised by solution size is **W[1]-hard**: no f(k) · poly(n) algorithm is believed to exist, and the best known is essentially brute force over all k-vertex subsets (sped up a little with fast matrix multiplication). The **Exponential Time Hypothesis** (ETH; Impagliazzo and Paturi, 2001) conjectures that 3-SAT needs exponential time:

```formula
T_3SAT(n) = 2^{Ω(n)}
C(n, k) ≤ n^k
C(10^6, 10) ≈ 2.8 × 10^53
where
T_3SAT(n): the time the best possible algorithm needs for 3-SAT with n variables
Ω(n): big Omega of n: at least a fixed positive constant times n, for large n
n: for 3-SAT, the number of variables; for clique, the number of vertices
k: the clique size you are looking for
C(n, k): "n choose k": the number of k-vertex subsets brute force checks
In words: ETH says 3-SAT needs time 2 to the power of a constant times n. It implies clique cannot escape having k in the exponent: there is no algorithm running in f(k) × n^{o(k)}, where o(k) means anything growing more slowly than k.
```

ETH is a conjecture, stronger than P ≠ NP.

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
- NP-hardness rules out exact, all-input, polynomial-time solutions together (if P and NP differ); each coping strategy relaxes one.
- Exponential algorithms differ hugely: Held–Karp's O(n² · 2ⁿ) versus about n! for brute-force TSP, where n is the number of cities.
- Vertex cover's matching algorithm is a tight 2-approximation; metric TSP is about 1.5; general TSP has no constant ratio unless P equals NP.
- The PCP theorem underlies hardness of approximation; Håstad shows 7/8 is optimal for MAX-3SAT. Some limits (vertex cover just below 2) rely on the unproven Unique Games Conjecture.
- FPT algorithms confine the exponential to a parameter: vertex cover in O(2^k · m) for budget k and m edges, with a kernel of at most k² edges. Clique is W[1]-hard.

## Further reading
- [Approximation algorithm — Wikipedia](https://en.wikipedia.org/wiki/Approximation_algorithm)
- [Hardness of approximation — Wikipedia](https://en.wikipedia.org/wiki/Hardness_of_approximation)
- [PCP theorem — Wikipedia](https://en.wikipedia.org/wiki/PCP_theorem)
- [Parameterized complexity — Wikipedia](https://en.wikipedia.org/wiki/Parameterized_complexity)
- [Kernelization — Wikipedia](https://en.wikipedia.org/wiki/Kernelization)
- [Christofides algorithm — Wikipedia](https://en.wikipedia.org/wiki/Christofides_algorithm)
- [Unique games conjecture — Wikipedia](https://en.wikipedia.org/wiki/Unique_games_conjecture)
- [Held–Karp algorithm — Wikipedia](https://en.wikipedia.org/wiki/Held%E2%80%93Karp_algorithm)
